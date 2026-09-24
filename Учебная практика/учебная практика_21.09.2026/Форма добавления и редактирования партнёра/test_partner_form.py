from unittest.mock import MagicMock, patch

import pytest

from partner_form import (
    EMAIL_PLACEHOLDER,
    PARTNER_TYPES,
    PHONE_PLACEHOLDER,
    PartnerEditWindow,
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
            "phone": "+7 495 111-22-33",
            "partner_type": "ООО",
            "director": "Иванов И.И.",
            "rating": "5",
        }
    )
    assert data["name"] == "ООО Тест"
    assert data["email"] == "test@example.ru"
    assert data["phone"] == "+7 495 111-22-33"
    assert data["rating"] == 5
    assert type(data["rating"]) is int


def test_parse_form_data_treats_placeholders_as_empty():
    data = parse_form_data(
        {
            "name": "ООО Тест",
            "inn": "7700000000",
            "email": EMAIL_PLACEHOLDER,
            "address": "Москва",
            "phone": PHONE_PLACEHOLDER,
            "partner_type": "ООО",
            "director": "Иванов И.И.",
            "rating": "0",
        }
    )
    assert data["phone"] == ""
    assert data["email"] == ""


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


def test_on_back_dirty_warns_and_closes_only_after_confirm():
    window = object.__new__(PartnerEditWindow)
    window._initial_values = {"name": "A"}
    window._current_values = MagicMock(return_value={"name": "B"})
    window.destroy = MagicMock()

    with patch("partner_form.show_unsaved_warning", return_value=False) as warn:
        PartnerEditWindow._on_back(window)
        warn.assert_called_once()
        window.destroy.assert_not_called()

    with patch("partner_form.show_unsaved_warning", return_value=True) as warn:
        PartnerEditWindow._on_back(window)
        warn.assert_called_once()
        window.destroy.assert_called_once()


def test_on_back_clean_closes_without_warning():
    window = object.__new__(PartnerEditWindow)
    window._initial_values = {"name": "A"}
    window._current_values = MagicMock(return_value={"name": "A"})
    window.destroy = MagicMock()

    with patch("partner_form.show_unsaved_warning") as warn:
        PartnerEditWindow._on_back(window)
        warn.assert_not_called()
        window.destroy.assert_called_once()


def test_on_save_validation_error_shows_dialog_and_keeps_form():
    window = object.__new__(PartnerEditWindow)
    window.partner_id = None
    window.connection_factory = MagicMock()
    window.on_saved = MagicMock()
    window.destroy = MagicMock()
    window._current_values = MagicMock(
        return_value={
            "name": "",
            "inn": "1",
            "email": "",
            "address": "",
            "phone": "",
            "partner_type": "ООО",
            "director": "",
            "rating": "0",
        }
    )

    with (
        patch(
            "partner_form.parse_form_data",
            side_effect=ValueError("Наименование обязательно"),
        ),
        patch("partner_form.show_error_dialog") as show_error,
        patch("partner_form.show_success_dialog") as show_success,
    ):
        PartnerEditWindow._on_save(window)
        show_error.assert_called_once()
        show_success.assert_not_called()
        window.destroy.assert_not_called()
        window.on_saved.assert_not_called()


def test_on_save_db_error_shows_dialog_and_keeps_form():
    window = object.__new__(PartnerEditWindow)
    window.partner_id = None
    window.connection_factory = MagicMock()
    window.on_saved = MagicMock()
    window.destroy = MagicMock()
    window._current_values = MagicMock(
        return_value={
            "name": "ООО",
            "inn": "7700000000",
            "email": "a@b.ru",
            "address": "",
            "phone": "",
            "partner_type": "ООО",
            "director": "",
            "rating": "0",
        }
    )
    connection = MagicMock()
    window.connection_factory.return_value = connection

    with (
        patch(
            "partner_form.parse_form_data",
            return_value={
                "name": "ООО",
                "inn": "7700000000",
                "email": "a@b.ru",
                "address": "",
                "phone": "",
                "partner_type": "ООО",
                "director": "",
                "rating": 0,
            },
        ),
        patch(
            "partner_form.persist_partner",
            side_effect=RuntimeError("db down"),
        ),
        patch("partner_form.show_error_dialog") as show_error,
        patch("partner_form.show_success_dialog") as show_success,
    ):
        PartnerEditWindow._on_save(window)
        show_error.assert_called_once()
        assert "db down" in show_error.call_args.args[0]
        show_success.assert_not_called()
        window.destroy.assert_not_called()
        window.on_saved.assert_not_called()
        connection.close.assert_called_once()