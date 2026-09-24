from unittest.mock import MagicMock, patch

import pytest

from partner_form import (
    EMAIL_PLACEHOLDER,
    PARTNER_TYPES,
    PHONE_PLACEHOLDER,
    is_form_dirty,
    parse_form_data,
    partner_edit_title,
    persist_partner,
)


def test_partner_edit_title_add_and_edit():
    assert partner_edit_title(None) == "CRM: Карточка партнёра [Добавление]"
    assert partner_edit_title(5) == "CRM: Карточка партнёра [Редактирование]"


def test_partner_types_and_placeholders():
    assert PARTNER_TYPES == ("ЗАО", "ООО", "ИП", "ТК")
    assert PHONE_PLACEHOLDER == "+7 (999) 000-00-00"
    assert EMAIL_PLACEHOLDER == "name@example.ru"


def test_parse_form_data_converts_rating_and_strips():
    data = parse_form_data(
        {
            "name": " ООО Тест ",
            "inn": "7700000000",
            "email": " test@example.ru ",
            "address": "Москва",
            "phone": "+7 (999) 000-00-00",
            "partner_type": "ООО",
            "director": "Иванов И.И.",
            "rating": "5",
        }
    )
    assert data["name"] == "ООО Тест"
    assert data["email"] == "test@example.ru"
    assert data["rating"] == 5
    assert type(data["rating"]) is int


def test_parse_form_data_rejects_non_integer_rating():
    with pytest.raises(ValueError):
        parse_form_data(
            {
                "name": "ООО",
                "inn": "1",
                "email": "a@b.ru",
                "address": "",
                "phone": "",
                "partner_type": "ООО",
                "director": "",
                "rating": "1.5",
            }
        )


def test_is_form_dirty_detects_changes():
    initial = {"name": "A", "rating": "0"}
    assert is_form_dirty(initial, {"name": "A", "rating": "0"}) is False
    assert is_form_dirty(initial, {"name": "B", "rating": "0"}) is True


def test_persist_partner_insert_commits():
    connection = MagicMock()
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
    with (
        patch("partner_form.insert_partner", return_value=10) as insert,
        patch("partner_form.update_partner") as update,
        patch("partner_form.validate_partner") as validate,
    ):
        persist_partner(None, data, connection)
        validate.assert_called_once_with(data)
        insert.assert_called_once_with(data, connection)
        update.assert_not_called()
        connection.commit.assert_called_once()


def test_persist_partner_update_commits():
    connection = MagicMock()
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
    with (
        patch("partner_form.insert_partner") as insert,
        patch("partner_form.update_partner") as update,
        patch("partner_form.validate_partner"),
    ):
        persist_partner(7, data, connection)
        update.assert_called_once_with(7, data, connection)
        insert.assert_not_called()
        connection.commit.assert_called_once()


def test_persist_partner_validation_error_does_not_commit():
    connection = MagicMock()
    data = {
        "name": "",
        "inn": "7700000000",
        "email": "test@example.ru",
        "address": "Москва",
        "phone": "+7 495 000-00-00",
        "partner_type": "ООО",
        "director": "Иванов И.И.",
        "rating": 5,
    }
    with patch(
        "partner_form.validate_partner",
        side_effect=ValueError("Наименование обязательно"),
    ):
        with pytest.raises(ValueError):
            persist_partner(None, data, connection)
    connection.commit.assert_not_called()
