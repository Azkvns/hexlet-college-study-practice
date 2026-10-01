import inspect

from partner_history import (
    COLUMN_DATE,
    COLUMN_PRODUCT,
    COLUMN_QUANTITY,
    HISTORY_SQL,
    PartnerHistoryWindow,
    history_title,
    list_partner_sales,
)


def test_history_column_titles():
    assert COLUMN_PRODUCT == "Наименование продукции"
    assert COLUMN_QUANTITY == "Количество (шт.)"
    assert COLUMN_DATE == "Дата продажи"


def test_history_title_contains_partner_name():
    title = history_title("ООО Ромашка")
    assert title == "CRM: История реализации продукции — ООО Ромашка"


def test_history_sql_joins_and_uses_parameter():
    assert "JOIN" in HISTORY_SQL
    assert "%s" in HISTORY_SQL
    assert "TO_CHAR" in HISTORY_SQL
    assert "{" not in HISTORY_SQL


class _Cursor:
    def __init__(self):
        self.query = None
        self.params = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, query, params):
        self.query = query
        self.params = params

    def fetchall(self):
        return [
            {
                "product_name": "Ламинат",
                "quantity": 12,
                "sale_date": "15.03.2026",
            }
        ]


class _Connection:
    def __init__(self):
        self.cursor_obj = _Cursor()

    def cursor(self, cursor_factory=None):
        return self.cursor_obj


def test_history_window_has_icon_and_logo():
    """PartnerHistoryWindow must guard resource paths like MainWindow."""
    init_src = inspect.getsource(PartnerHistoryWindow.__init__)
    build_src = inspect.getsource(PartnerHistoryWindow._build)
    assert "icon_path.exists()" in init_src
    assert "iconphoto" in init_src
    assert "logo.png" in build_src
    assert "logo_path.exists()" in build_src


def test_list_partner_sales_passes_partner_id():
    connection = _Connection()
    rows = list_partner_sales(7, connection)
    assert connection.cursor_obj.params == (7,)
    assert rows[0]["product_name"] == "Ламинат"
    assert rows[0]["quantity"] == 12
    assert rows[0]["sale_date"] == "15.03.2026"
