from __future__ import annotations

import sys
import tkinter as tk
from pathlib import Path

_PRACTICE_ROOT = Path(__file__).resolve().parent.parent
_CORE_DIR = (
    _PRACTICE_ROOT / "Разработка ядра алгоритма расчета материалов"
)
_HISTORY_DIR = (
    _PRACTICE_ROOT
    / " Разработка интерфейса истории реализации продукции"
)
if str(_CORE_DIR) not in sys.path:
    sys.path.insert(0, str(_CORE_DIR))
if str(_HISTORY_DIR) not in sys.path:
    sys.path.insert(0, str(_HISTORY_DIR))

from dialogs import show_error_dialog
from material_calculator import calculate_material_amount
from material_catalog import DbMaterialCatalog, MemoryMaterialCatalog

BG_COLOR = "#FFFFFF"
FG_COLOR = "#000000"
FONT_TITLE = ("Arial", 11)
FONT_DETAILS = ("Arial", 9)

CALCULATOR_TITLE = "CRM: Расчёт материалов"
CALCULATE_BUTTON_TEXT = "Рассчитать"
BACK_BUTTON_TEXT = "Назад"
RESULT_PREFIX = "Требуется материала, шт.: "

MATERIAL_ERROR_MESSAGE = (
    "Не удалось рассчитать расход. Проверьте, что типы существуют, "
    "параметры больше нуля, а количество — целое число больше нуля."
)

_FIELD_KEYS = (
    "product_type_id",
    "material_type_id",
    "quantity",
    "param_1",
    "param_2",
)

_FIELD_LABELS = {
    "product_type_id": "Тип продукции",
    "material_type_id": "Тип материала",
    "quantity": "Количество",
    "param_1": "Параметр 1",
    "param_2": "Параметр 2",
}


def parse_calculator_input(raw: dict) -> dict | None:
    try:
        product_type_id = int(str(raw.get("product_type_id", "")).strip())
        material_type_id = int(str(raw.get("material_type_id", "")).strip())
        quantity_raw = str(raw.get("quantity", "")).strip()
        if quantity_raw == "":
            return None
        quantity = int(quantity_raw)
        if str(quantity) != quantity_raw:
            return None
        param_1 = float(str(raw.get("param_1", "")).strip())
        param_2 = float(str(raw.get("param_2", "")).strip())
    except (TypeError, ValueError):
        return None
    return {
        "product_type_id": product_type_id,
        "material_type_id": material_type_id,
        "quantity": quantity,
        "param_1": param_1,
        "param_2": param_2,
    }


def apply_calculation(result, set_text, show_error) -> None:
    if result == -1:
        show_error(MATERIAL_ERROR_MESSAGE)
        return
    set_text(str(result))


class MaterialCalculatorWindow(tk.Toplevel):
    def __init__(self, master, connection_factory=None):
        super().__init__(master)
        self._connection_factory = connection_factory
        self.title(CALCULATOR_TITLE)
        self.configure(bg=BG_COLOR)
        self._entries: dict[str, tk.StringVar] = {}
        self._result_var = tk.StringVar(value="")
        self._build_form()

    def _build_form(self) -> None:
        body = tk.Frame(self, bg=BG_COLOR)
        body.pack(fill="both", expand=True, padx=16, pady=16)

        tk.Label(
            body,
            text=CALCULATOR_TITLE,
            font=FONT_TITLE,
            fg=FG_COLOR,
            bg=BG_COLOR,
            anchor="w",
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        for index, key in enumerate(_FIELD_KEYS):
            row = index + 1
            tk.Label(
                body,
                text=_FIELD_LABELS[key],
                font=FONT_DETAILS,
                fg=FG_COLOR,
                bg=BG_COLOR,
                anchor="w",
            ).grid(row=row, column=0, sticky="w", pady=4, padx=(0, 8))
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

        body.columnconfigure(1, weight=1)

        result_row = len(_FIELD_KEYS) + 1
        tk.Label(
            body,
            textvariable=self._result_var,
            font=FONT_TITLE,
            fg=FG_COLOR,
            bg=BG_COLOR,
            anchor="w",
        ).grid(row=result_row, column=0, columnspan=2, sticky="w", pady=(12, 0))

        buttons = tk.Frame(body, bg=BG_COLOR)
        buttons.grid(
            row=result_row + 1,
            column=0,
            columnspan=2,
            pady=(16, 0),
            sticky="w",
        )
        tk.Button(
            buttons,
            text=BACK_BUTTON_TEXT,
            font=FONT_TITLE,
            command=self.destroy,
        ).pack(side="left", padx=(0, 8))
        tk.Button(
            buttons,
            text=CALCULATE_BUTTON_TEXT,
            font=FONT_TITLE,
            command=self._on_calculate,
        ).pack(side="left")

    def _current_raw(self) -> dict:
        return {key: self._entries[key].get() for key in _FIELD_KEYS}

    def _set_result_text(self, value: str) -> None:
        self._result_var.set(f"{RESULT_PREFIX}{value}")

    def _show_error(self, message: str) -> None:
        show_error_dialog(message, parent=self)

    def _on_calculate(self) -> None:
        parsed = parse_calculator_input(self._current_raw())
        if parsed is None:
            self._show_error(MATERIAL_ERROR_MESSAGE)
            return
        connection = None
        try:
            if self._connection_factory is not None:
                connection = self._connection_factory()
                catalog = DbMaterialCatalog(connection)
            else:
                catalog = MemoryMaterialCatalog()
            result = calculate_material_amount(
                parsed["product_type_id"],
                parsed["material_type_id"],
                parsed["quantity"],
                parsed["param_1"],
                parsed["param_2"],
                catalog,
            )
        except Exception as exc:
            self._show_error(
                f"Не удалось рассчитать расход материалов:\n{exc}"
            )
            return
        finally:
            if connection is not None:
                connection.close()
        apply_calculation(result, self._set_result_text, self._show_error)
