from __future__ import annotations

import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk

import psycopg2.extras

from dialogs import show_error_dialog

_AUDIT_DIR = (
    Path(__file__).resolve().parent.parent
    / "Модульное тестирование (Unit Testing) и аудит безопасности"
)
if str(_AUDIT_DIR) not in sys.path:
    sys.path.insert(0, str(_AUDIT_DIR))

from error_log import DEFAULT_LOG_PATH, log_error

BG_COLOR = "#FFFFFF"
FG_COLOR = "#000000"
FONT_TITLE = ("Arial", 11)
FONT_DETAILS = ("Arial", 9)

COLUMN_PRODUCT = "Наименование продукции"
COLUMN_QUANTITY = "Количество (шт.)"
COLUMN_DATE = "Дата продажи"

HISTORY_SQL = """
SELECT
    pr.name AS product_name,
    si.quantity_shipped AS quantity,
    TO_CHAR(s.shipment_date, 'DD.MM.YYYY') AS sale_date
FROM shipment_items AS si
JOIN orders AS o ON o.order_id = si.order_id
JOIN products AS pr ON pr.product_id = o.product_id
JOIN shipments AS s ON s.shipment_id = si.shipment_id
WHERE o.partner_id = %s
ORDER BY s.shipment_date, pr.name
"""


def history_title(partner_name: str) -> str:
    return f"CRM: История реализации продукции — {partner_name}"


def list_partner_sales(partner_id: int, connection) -> list[dict]:
    with connection.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor
    ) as cursor:
        cursor.execute(HISTORY_SQL, (partner_id,))
        rows = cursor.fetchall()
    return [dict(row) for row in rows]


class PartnerHistoryWindow(tk.Toplevel):
    def __init__(self, master, partner_id, partner_name, connection_factory=None):
        super().__init__(master)
        self.partner_id = partner_id
        self.title(history_title(partner_name))
        self.configure(bg=BG_COLOR)

        icon_path = Path(__file__).resolve().parent / "app_icon.png"
        if icon_path.exists():
            self._app_icon = tk.PhotoImage(file=str(icon_path))
            self.iconphoto(True, self._app_icon)

        self._build(connection_factory)

    def _build(self, connection_factory) -> None:
        header = tk.Frame(self, bg=BG_COLOR)
        header.pack(fill="x", padx=16, pady=16)

        logo_path = Path(__file__).resolve().parent / "logo.png"
        if logo_path.exists():
            self._logo = tk.PhotoImage(file=str(logo_path))
            tk.Label(header, image=self._logo, bg=BG_COLOR).pack(side="left")

        tk.Label(
            header,
            text=self.title(),
            font=FONT_TITLE,
            fg=FG_COLOR,
            bg=BG_COLOR,
        ).pack(side="left")
        tk.Button(
            header,
            text="Назад",
            font=FONT_TITLE,
            command=self.destroy,
        ).pack(side="right")
        columns = ("product_name", "quantity", "sale_date")
        table = ttk.Treeview(self, columns=columns, show="headings", height=12)
        table.heading("product_name", text=COLUMN_PRODUCT)
        table.heading("quantity", text=COLUMN_QUANTITY)
        table.heading("sale_date", text=COLUMN_DATE)
        table.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self._fill(table, connection_factory)

    def _fill(self, table, connection_factory) -> None:
        if connection_factory is None:
            from db import get_connection
            connection_factory = get_connection
        connection = None
        try:
            connection = connection_factory()
            rows = list_partner_sales(self.partner_id, connection)
        except Exception as exc:
            message = f"Не удалось загрузить историю продаж:\n{exc}"
            log_error(message, DEFAULT_LOG_PATH)
            show_error_dialog(message, parent=self)
            return
        finally:
            if connection is not None:
                connection.close()
        for row in rows:
            table.insert(
                "",
                "end",
                values=(row["product_name"], row["quantity"], row["sale_date"]),
            )
