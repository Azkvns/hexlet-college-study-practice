from partner_history import HISTORY_SQL, history_title, list_partner_sales


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


def test_list_partner_sales_passes_partner_id():
    connection = _Connection()
    rows = list_partner_sales(7, connection)
    assert connection.cursor_obj.params == (7,)
    assert rows[0]["product_name"] == "Ламинат"
    assert rows[0]["quantity"] == 12
    assert rows[0]["sale_date"] == "15.03.2026"
