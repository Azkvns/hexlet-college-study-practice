from __future__ import annotations

import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk

_PRACTICE_ROOT = Path(__file__).resolve().parent.parent
_EXCEPTIONS_DIR = (
    _PRACTICE_ROOT
    / "Обработка исключений и интерактивные уведомления (UX／UI)"
)
_REPO_DIR = (
    _PRACTICE_ROOT / "Интеграция формы с БД (CRUD-операции и обновление UI)"
)
_NAV_DIR = _PRACTICE_ROOT / "Многооконная архитектура и навигация"

for _path in (_EXCEPTIONS_DIR, _REPO_DIR):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from dialogs import (  # noqa: E402
    show_error_dialog,
    show_success_dialog,
    show_unsaved_warning,
)
from partner_repository import (  # noqa: E402
    get_partner,
    insert_partner,
    update_partner,
)
from validation import validate_partner  # noqa: E402

BG_COLOR = "#FFFFFF"
FG_COLOR = "#000000"
FONT_TITLE = ("Arial", 11)
FONT_DETAILS = ("Arial", 9)

PARTNER_TYPES = ("ЗАО", "ООО", "ИП", "ТК")
PHONE_PLACEHOLDER = "+7 (999) 000-00-00"
EMAIL_PLACEHOLDER = "name@example.ru"

_FIELD_KEYS = (
    "name",
    "partner_type",
    "rating",
    "address",
    "director",
    "phone",
    "email",
    "inn",
)


def partner_edit_title(partner_id: int | None) -> str:
    if partner_id is None:
        return "CRM: Карточка партнёра [Добавление]"
    return "CRM: Карточка партнёра [Редактирование]"


def is_form_dirty(initial: dict, current: dict) -> bool:
    return initial != current


def _strip_placeholder(key: str, value: str) -> str:
    text = value.strip()
    if key == "phone" and text == PHONE_PLACEHOLDER:
        return ""
    if key == "email" and text == EMAIL_PLACEHOLDER:
        return ""
    return text


def parse_form_data(raw: dict) -> dict:
    rating_raw = str(raw.get("rating", "")).strip()
    try:
        rating = int(rating_raw)
    except ValueError as exc:
        raise ValueError(
            "Рейтинг должен быть целым числом от 0. "
            "Пожалуйста, удалите знаки препинания и повторите попытку"
        ) from exc
    if str(rating) != rating_raw:
        raise ValueError(
            "Рейтинг должен быть целым числом от 0. "
            "Пожалуйста, удалите знаки препинания и повторите попытку"
        )
    return {
        "name": str(raw.get("name", "")).strip(),
        "inn": str(raw.get("inn", "")).strip(),
        "email": _strip_placeholder("email", str(raw.get("email", ""))),
        "address": str(raw.get("address", "")).strip(),
        "phone": _strip_placeholder("phone", str(raw.get("phone", ""))),
        "partner_type": str(raw.get("partner_type", "")).strip(),
        "director": str(raw.get("director", "")).strip(),
        "rating": rating,
    }


def persist_partner(partner_id: int | None, data: dict, connection) -> None:
    validate_partner(data)
    if partner_id is None:
        insert_partner(data, connection)
    else:
        update_partner(partner_id, data, connection)
    connection.commit()


class PartnerEditWindow(tk.Toplevel):
    def __init__(
        self,
        master,
        partner_id: int | None = None,
        connection_factory=None,
        on_saved=None,
    ):
        super().__init__(master)
        self.partner_id = partner_id
        self.connection_factory = connection_factory
        self.on_saved = on_saved
        self.title(partner_edit_title(partner_id))
        self.configure(bg=BG_COLOR)

        icon_path = _NAV_DIR / "resources" / "app_icon.png"
        if icon_path.exists():
            self._app_icon = tk.PhotoImage(file=str(icon_path))
            self.iconphoto(True, self._app_icon)

        self._entries: dict[str, tk.Variable | ttk.Combobox] = {}
        self._placeholder_widgets: dict[str, tuple[tk.Entry, str]] = {}
        self._initial_values: dict[str, str] = {}
        self._build_form()
        self._load_partner_if_needed()
        self._refresh_placeholders()
        self._initial_values = self._current_values()

        self.protocol("WM_DELETE_WINDOW", self._on_back)

    def _build_form(self) -> None:
        body = tk.Frame(self, bg=BG_COLOR)
        body.pack(fill="both", expand=True, padx=16, pady=16)

        labels = {
            "name": "Наименование",
            "partner_type": "Тип партнёра",
            "rating": "Рейтинг",
            "address": "Адрес",
            "director": "ФИО директора",
            "phone": "Телефон",
            "email": "Email",
            "inn": "ИНН",
        }

        for row, key in enumerate(_FIELD_KEYS):
            tk.Label(
                body,
                text=labels[key],
                font=FONT_DETAILS,
                fg=FG_COLOR,
                bg=BG_COLOR,
                anchor="w",
            ).grid(row=row, column=0, sticky="w", pady=4, padx=(0, 8))

            if key == "partner_type":
                combo = ttk.Combobox(
                    body,
                    values=list(PARTNER_TYPES),
                    state="readonly",
                    font=FONT_DETAILS,
                    width=40,
                )
                combo.set(PARTNER_TYPES[1])
                combo.grid(row=row, column=1, sticky="ew", pady=4)
                self._entries[key] = combo
            else:
                var = tk.StringVar()
                entry = tk.Entry(
                    body,
                    textvariable=var,
                    font=FONT_DETAILS,
                    bg=BG_COLOR,
                    fg=FG_COLOR,
                    width=42,
                )
                entry.grid(row=row, column=1, sticky="ew", pady=4)
                self._entries[key] = var
                if key == "phone":
                    self._attach_placeholder(entry, var, PHONE_PLACEHOLDER)
                elif key == "email":
                    self._attach_placeholder(entry, var, EMAIL_PLACEHOLDER)

        body.columnconfigure(1, weight=1)

        buttons = tk.Frame(body, bg=BG_COLOR)
        buttons.grid(row=len(_FIELD_KEYS), column=0, columnspan=2, pady=(16, 0))

        tk.Button(
            buttons,
            text="Назад",
            font=FONT_TITLE,
            command=self._on_back,
        ).pack(side="left", padx=(0, 8))
        tk.Button(
            buttons,
            text="Сохранить",
            font=FONT_TITLE,
            command=self._on_save,
        ).pack(side="left")

    def _attach_placeholder(
        self,
        entry: tk.Entry,
        var: tk.StringVar,
        placeholder: str,
    ) -> None:
        """Show hint text in the entry; never treat it as a saved value."""
        key = "phone" if placeholder == PHONE_PLACEHOLDER else "email"
        self._placeholder_widgets[key] = (entry, placeholder)

        def show_placeholder() -> None:
            if not _strip_placeholder(key, var.get()):
                var.set(placeholder)
                entry.configure(fg="#808080")

        def on_focus_in(_event=None) -> None:
            if var.get() == placeholder:
                var.set("")
                entry.configure(fg=FG_COLOR)

        def on_focus_out(_event=None) -> None:
            show_placeholder()

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

    def _refresh_placeholders(self) -> None:
        for key, (entry, placeholder) in self._placeholder_widgets.items():
            var = self._entries[key]
            assert isinstance(var, tk.StringVar)
            current = var.get().strip()
            if not current or current == placeholder:
                var.set(placeholder)
                entry.configure(fg="#808080")
            else:
                entry.configure(fg=FG_COLOR)

    def _load_partner_if_needed(self) -> None:
        if self.partner_id is None:
            return
        if self.connection_factory is None:
            from db import get_connection

            connection_factory = get_connection
        else:
            connection_factory = self.connection_factory
        connection = connection_factory()
        try:
            row = get_partner(self.partner_id, connection)
        finally:
            connection.close()
        if row is None:
            show_error_dialog(
                f"Партнёр с id={self.partner_id} не найден",
                parent=self,
            )
            return
        self._set_values(
            {
                "name": row.get("name") or "",
                "partner_type": row.get("partner_type") or PARTNER_TYPES[1],
                "rating": str(row.get("rating") if row.get("rating") is not None else ""),
                "address": row.get("address") or "",
                "director": row.get("director") or "",
                "phone": row.get("phone") or "",
                "email": row.get("email") or "",
                "inn": row.get("inn") or "",
            }
        )

    def _set_values(self, values: dict[str, str]) -> None:
        for key, value in values.items():
            widget = self._entries[key]
            if isinstance(widget, ttk.Combobox):
                if value in PARTNER_TYPES:
                    widget.set(value)
                else:
                    widget.set(PARTNER_TYPES[1])
            else:
                widget.set(value)

    def _current_values(self) -> dict[str, str]:
        result: dict[str, str] = {}
        for key, widget in self._entries.items():
            if isinstance(widget, ttk.Combobox):
                result[key] = widget.get()
            else:
                result[key] = _strip_placeholder(key, widget.get())
        return result

    def _on_back(self) -> None:
        if is_form_dirty(self._initial_values, self._current_values()):
            if not show_unsaved_warning(parent=self):
                return
        self.destroy()

    def _on_save(self) -> None:
        try:
            data = parse_form_data(self._current_values())
            if self.connection_factory is None:
                from db import get_connection

                connection_factory = get_connection
            else:
                connection_factory = self.connection_factory
            connection = connection_factory()
            try:
                persist_partner(self.partner_id, data, connection)
            finally:
                connection.close()
        except Exception as exc:
            show_error_dialog(str(exc), parent=self)
            return
        show_success_dialog(parent=self)
        self._initial_values = self._current_values()
        if self.on_saved is not None:
            self.on_saved()
        self.destroy()
