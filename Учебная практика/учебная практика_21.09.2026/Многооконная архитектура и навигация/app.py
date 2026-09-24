from __future__ import annotations

import importlib.util
import sys
import tkinter as tk
from pathlib import Path
from typing import Any, Callable

_PRACTICE_ROOT = Path(__file__).resolve().parent.parent
_UI_DIR = (
    _PRACTICE_ROOT / "Разработка интерфейса (UI) по руководству по стилю"
)
_FORM_DIR = _PRACTICE_ROOT / "Форма добавления и редактирования партнёра"
_INTEGRATION_DIR = (
    _PRACTICE_ROOT / "Интеграция с БД и агрегация данных (SQL + Backend)"
)
_EXCEPTIONS_DIR = _PRACTICE_ROOT / "Исключения и уведомления"
RESOURCES_DIR = _UI_DIR / "resources"

MAIN_TITLE = "CRM: Реестр партнёров"
ADD_PARTNER_BUTTON_TEXT = "Добавить партнёра"
BG_COLOR = "#FFFFFF"
FG_COLOR = "#000000"
BORDER_COLOR = "#000000"
FONT_TITLE = ("Arial", 11)
FONT_DETAILS = ("Arial", 9)
CARD_GAP = 20

PartnerCard = dict[str, Any]
Fetcher = Callable[[], list[dict[str, Any]]]


def to_partner_card(row: dict[str, Any]) -> PartnerCard:
    raw_qty = row.get("total_quantity")
    total_quantity = 0 if raw_qty is None else int(raw_qty)
    discount = row.get("discount_percent")
    if discount is None:
        discount = 0
    director = row.get("director") or "Директор"
    rating = row.get("rating")
    if rating is None:
        rating = 0
    return {
        "partner_id": row.get("partner_id"),
        "partner_type": row.get("partner_type") or "Партнер",
        "name": row["name"],
        "director": director,
        "phone": row.get("phone") or "",
        "rating": int(rating),
        "total_quantity": total_quantity,
        "discount_percent": int(discount),
    }


def _load_ui_module():
    if str(_UI_DIR) not in sys.path:
        sys.path.insert(0, str(_UI_DIR))
    spec = importlib.util.spec_from_file_location("crm_ui_main_21", _UI_DIR / "main.py")
    if spec is None or spec.loader is None:
        raise ImportError("Cannot load UI main module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _ensure_form_import() -> None:
    if str(_FORM_DIR) not in sys.path:
        sys.path.insert(0, str(_FORM_DIR))


def _ensure_integration_import() -> None:
    if str(_INTEGRATION_DIR) not in sys.path:
        sys.path.insert(0, str(_INTEGRATION_DIR))


def _ensure_exceptions_import() -> None:
    if str(_EXCEPTIONS_DIR) not in sys.path:
        sys.path.insert(0, str(_EXCEPTIONS_DIR))


def load_partner_cards(fetcher: Fetcher | None = None) -> list[PartnerCard]:
    if fetcher is None:
        _ensure_integration_import()
        from partner_sales import list_partners_with_discount

        fetcher = list_partners_with_discount
    return [to_partner_card(row) for row in fetcher()]


class MainWindow(tk.Tk):
    def __init__(
        self,
        fetcher: Fetcher | None = None,
        connection_factory=None,
    ):
        super().__init__()
        self._fetcher = fetcher
        self._connection_factory = connection_factory
        self.title(MAIN_TITLE)
        self.configure(bg=BG_COLOR)

        self._ui = _load_ui_module()
        icon_path = RESOURCES_DIR / "app_icon.png"
        logo_path = RESOURCES_DIR / "logo.png"
        self._app_icon = self._ui._load_photo(icon_path)
        self.iconphoto(True, self._app_icon)
        self._logo = self._ui._load_photo(logo_path)

        header = tk.Frame(self, bg=BG_COLOR)
        header.pack(fill="x", padx=16, pady=(16, 8))

        tk.Label(header, image=self._logo, bg=BG_COLOR).pack(side="left")
        tk.Label(
            header,
            text=MAIN_TITLE,
            font=FONT_TITLE,
            fg=FG_COLOR,
            bg=BG_COLOR,
        ).pack(side="left", padx=(12, 0))

        tk.Button(
            header,
            text=ADD_PARTNER_BUTTON_TEXT,
            font=FONT_TITLE,
            command=self._open_add_partner,
        ).pack(side="right")

        self._list_outer = tk.Frame(
            self,
            bg=BG_COLOR,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1,
        )
        self._list_outer.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        self._list_inner = tk.Frame(self._list_outer, bg=BG_COLOR)
        self._list_inner.pack(
            fill="both",
            expand=True,
            anchor="n",
            padx=CARD_GAP,
            pady=CARD_GAP,
        )

        self.refresh_list()
        self.update_idletasks()
        self.minsize(480, max(self.winfo_reqheight(), 320))

    def refresh_list(self) -> None:
        for child in self._list_inner.winfo_children():
            child.destroy()

        _ensure_exceptions_import()
        from dialogs import show_error_dialog

        try:
            partners = load_partner_cards(self._fetcher)
        except Exception as exc:
            show_error_dialog(
                f"Не удалось загрузить список партнёров:\n{exc}",
                parent=self,
            )
            partners = []

        if not partners:
            tk.Label(
                self._list_inner,
                text="Нет данных для отображения.",
                font=FONT_TITLE,
                fg=FG_COLOR,
                bg=BG_COLOR,
            ).pack(anchor="w")
        else:
            for index, partner in enumerate(partners):
                card = self._ui.create_partner_card(self._list_inner, partner)
                bottom_gap = CARD_GAP if index < len(partners) - 1 else 0
                card.pack(fill="x", expand=False, pady=(0, bottom_gap))
                partner_id = partner.get("partner_id")
                # partner_id передаётся в замыкание для двойного клика по карточке
                self._bind_card_open(card, partner_id)

        tk.Frame(self._list_inner, bg=BG_COLOR, height=1).pack(
            fill="both",
            expand=True,
        )

    def _bind_card_open(self, widget: tk.Widget, partner_id) -> None:
        def handler(_event=None, pid=partner_id):
            if pid is not None:
                self._open_edit_partner(pid)

        widget.bind("<Double-Button-1>", handler)
        for child in widget.winfo_children():
            self._bind_card_open(child, partner_id)

    def _open_add_partner(self) -> None:
        self._open_edit_partner(None)

    def _open_edit_partner(self, partner_id: int | None) -> None:
        _ensure_form_import()
        from partner_form import PartnerEditWindow

        PartnerEditWindow(
            self,
            partner_id=partner_id,
            connection_factory=self._connection_factory,
            on_saved=self.refresh_list,
        )


def main() -> None:
    MainWindow().mainloop()


if __name__ == "__main__":
    main()
