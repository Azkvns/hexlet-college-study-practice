from unittest.mock import MagicMock

from partner_repository import get_partner, insert_partner, update_partner


def _mock_connection(fetchone_value=None):
    connection = MagicMock()
    cursor = MagicMock()
    cursor.__enter__ = MagicMock(return_value=cursor)
    cursor.__exit__ = MagicMock(return_value=False)
    cursor.fetchone.return_value = fetchone_value
    connection.cursor.return_value = cursor
    return connection, cursor


def _partner_data(**overrides):
    data = {
        "name": "ООО Тест",
        "inn": "7700000000",
        "email": "test@example.ru",
        "address": "Москва",
        "phone": "+7 495 000-00-00",
        "partner_type": "ООО",
        "director": "Иванов И.И.",
        "rating": 5,
    }
    data.update(overrides)
    return data


def test_insert_partner_uses_percent_s_and_tuple_params():
    connection, cursor = _mock_connection({"partner_id": 42})

    partner_id = insert_partner(_partner_data(), connection)

    assert partner_id == 42
    sql = cursor.execute.call_args[0][0]
    params = cursor.execute.call_args[0][1]
    assert "%s" in sql
    assert "f\"" not in sql and "f'" not in sql
    assert "{" not in sql or "%s" in sql
    assert isinstance(params, tuple)
    assert "INSERT" in sql.upper()
    assert sql.count("%s") == len(params)


def test_update_partner_uses_percent_s_no_delete_orders_or_shipments():
    connection, cursor = _mock_connection()

    update_partner(7, _partner_data(), connection)

    assert cursor.execute.call_count >= 1
    for call in cursor.execute.call_args_list:
        sql = call[0][0]
        params = call[0][1]
        assert "%s" in sql
        assert isinstance(params, tuple)
        upper = sql.upper()
        assert "DELETE" not in upper
        assert "ORDERS" not in upper or "UPDATE" in upper
        assert "SHIPMENT" not in upper
        assert "f\"" not in sql and "f'" not in sql


def test_update_partner_sql_has_no_orders_or_shipment_items_delete():
    connection, cursor = _mock_connection()

    update_partner(3, _partner_data(name="X"), connection)

    all_sql = " ".join(call[0][0] for call in cursor.execute.call_args_list).upper()
    assert "DELETE" not in all_sql
    assert "FROM ORDERS" not in all_sql
    assert "SHIPMENT_ITEMS" not in all_sql


def test_get_partner_uses_percent_s_and_returns_dict_or_none():
    row = {
        "partner_id": 1,
        "name": "ООО Тест",
        "inn": "7700000000",
        "email": "test@example.ru",
        "address": "Москва",
        "phone": "+7 495 000-00-00",
        "partner_type": "ООО",
        "director": "Иванов И.И.",
        "rating": 5,
    }
    connection, cursor = _mock_connection(row)

    result = get_partner(1, connection)

    assert result == row
    sql = cursor.execute.call_args[0][0]
    params = cursor.execute.call_args[0][1]
    assert "%s" in sql
    assert params == (1,)
    assert "SELECT" in sql.upper()
    assert "f\"" not in sql and "f'" not in sql

    connection_missing, _ = _mock_connection(None)
    assert get_partner(999, connection_missing) is None
