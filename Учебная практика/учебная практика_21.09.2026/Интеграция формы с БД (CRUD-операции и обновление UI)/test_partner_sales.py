from unittest.mock import MagicMock, patch

import pytest

from db import get_connection
from partner_sales import get_partner_with_discount, list_partners_with_discount


def test_get_connection_uses_database_url(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/practice")
    monkeypatch.delenv("PGHOST", raising=False)

    with patch("db.psycopg2.connect") as mock_connect:
        mock_connect.return_value = MagicMock()
        get_connection()

    mock_connect.assert_called_once_with(
        "postgresql://user:pass@localhost:5432/practice"
    )


def _mock_connection_with_row(row):
    connection = MagicMock()
    cursor = MagicMock()
    cursor.__enter__ = MagicMock(return_value=cursor)
    cursor.__exit__ = MagicMock(return_value=False)
    cursor.fetchone.return_value = row
    connection.cursor.return_value = cursor
    return connection, cursor


def test_get_partner_with_discount_returns_partner_and_discount():
    row = {
        "partner_id": 1,
        "name": "ООО Тест",
        "inn": "7700000000",
        "email": "test@example.ru",
        "address": "Москва",
        "phone": "+7 495 000-00-00",
        "partner_type": "ООО",
        "director": "Иванов И.И.",
        "rating": 8,
        "total_quantity": 12000,
    }
    connection, _ = _mock_connection_with_row(row)

    result = get_partner_with_discount(1, connection=connection)

    assert result == {
        "partner_id": 1,
        "name": "ООО Тест",
        "inn": "7700000000",
        "email": "test@example.ru",
        "address": "Москва",
        "phone": "+7 495 000-00-00",
        "partner_type": "ООО",
        "director": "Иванов И.И.",
        "rating": 8,
        "total_quantity": 12000,
        "discount_percent": 5,
    }


def test_get_partner_with_discount_zero_quantity():
    row = {
        "partner_id": 2,
        "name": "Без продаж",
        "inn": "7700000001",
        "email": "zero@example.ru",
        "address": "СПб",
        "phone": "+7 812 000-00-00",
        "partner_type": "ООО",
        "director": "Петров П.П.",
        "rating": 6,
        "total_quantity": 0,
    }
    connection, _ = _mock_connection_with_row(row)

    result = get_partner_with_discount(2, connection=connection)

    assert result["total_quantity"] == 0
    assert result["discount_percent"] == 0
    assert result["partner_type"] == "ООО"
    assert result["director"] == "Петров П.П."
    assert result["rating"] == 6


def test_get_partner_with_discount_missing_partner():
    connection, _ = _mock_connection_with_row(None)

    result = get_partner_with_discount(999, connection=connection)

    assert result is None


def test_get_partner_with_discount_sql_uses_sum_left_join_and_param():
    row = {
        "partner_id": 3,
        "name": "X",
        "inn": "1",
        "email": "x@x.ru",
        "address": "A",
        "phone": "1",
        "partner_type": "ТК",
        "director": "Сидоров С.С.",
        "rating": 7,
        "total_quantity": 100,
    }
    connection, cursor = _mock_connection_with_row(row)

    get_partner_with_discount(3, connection=connection)

    sql = cursor.execute.call_args[0][0]
    params = cursor.execute.call_args[0][1]
    assert "SUM" in sql.upper()
    assert "LEFT JOIN" in sql.upper()
    assert "SALES_HISTORY" in sql.upper()
    assert "SUM(SH.QUANTITY)" in sql.upper()
    assert params == (3,)


def test_normalize_null_total_quantity_via_get():
    row = {
        "partner_id": 9,
        "name": "NullQty",
        "inn": "1",
        "email": "n@n.ru",
        "address": "A",
        "phone": "1",
        "partner_type": "ИП",
        "director": "Новиков Н.Н.",
        "rating": 5,
        "total_quantity": None,
    }
    connection, _ = _mock_connection_with_row(row)

    result = get_partner_with_discount(9, connection=connection)

    assert result["total_quantity"] == 0
    assert result["discount_percent"] == 0


def test_list_partners_with_discount_maps_rows():
    rows = [
        {
            "partner_id": 2,
            "name": "B",
            "inn": "2",
            "email": "b@b.ru",
            "address": "A",
            "phone": "2",
            "partner_type": "ТК",
            "director": "Белов Б.Б.",
            "rating": 4,
            "total_quantity": None,
        },
        {
            "partner_id": 1,
            "name": "A",
            "inn": "1",
            "email": "a@a.ru",
            "address": "A",
            "phone": "1",
            "partner_type": "ООО",
            "director": "Алексеев А.А.",
            "rating": 9,
            "total_quantity": 12000,
        },
    ]
    connection = MagicMock()
    cursor = MagicMock()
    cursor.__enter__ = MagicMock(return_value=cursor)
    cursor.__exit__ = MagicMock(return_value=False)
    cursor.fetchall.return_value = rows
    connection.cursor.return_value = cursor

    result = list_partners_with_discount(connection=connection)

    assert [r["name"] for r in result] == ["B", "A"]
    assert result[0]["discount_percent"] == 0
    assert result[0]["director"] == "Белов Б.Б."
    assert result[0]["rating"] == 4
    assert result[1]["discount_percent"] == 5
    assert result[1]["partner_type"] == "ООО"
    sql = cursor.execute.call_args[0][0]
    assert "SUM" in sql.upper()
    assert "LEFT JOIN" in sql.upper()
    assert "SALES_HISTORY" in sql.upper()
    assert "SUM(SH.QUANTITY)" in sql.upper()
    assert "WHERE" not in sql.upper().split("GROUP BY")[0]
