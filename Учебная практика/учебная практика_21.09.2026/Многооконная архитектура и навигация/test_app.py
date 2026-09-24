from unittest.mock import MagicMock, patch

from app import (
    ADD_PARTNER_BUTTON_TEXT,
    BG_COLOR,
    FONT_DETAILS,
    FONT_TITLE,
    MAIN_TITLE,
    MainWindow,
    to_partner_card,
)


def test_main_window_title_and_style_constants():
    assert MAIN_TITLE == "CRM: Реестр партнёров"
    assert ADD_PARTNER_BUTTON_TEXT == "Добавить партнёра"
    assert BG_COLOR == "#FFFFFF"
    assert FONT_TITLE == ("Arial", 11)
    assert FONT_DETAILS == ("Arial", 9)


def test_to_partner_card_empty_sum_gives_zero_discount():
    card = to_partner_card(
        {
            "partner_id": 1,
            "name": "ООО Без продаж",
            "phone": "+7 000 000-00-00",
            "partner_type": "ООО",
            "director": "Иванов И.И.",
            "rating": 3,
            "total_quantity": None,
            "discount_percent": None,
        }
    )
    assert card["discount_percent"] == 0
    assert card["total_quantity"] == 0
    assert card["partner_id"] == 1


def test_to_partner_card_keeps_nonzero_discount():
    card = to_partner_card(
        {
            "partner_id": 2,
            "name": "ООО С продажами",
            "phone": "+7 000 000-00-00",
            "partner_type": "ЗАО",
            "director": "Петров П.П.",
            "rating": 8,
            "total_quantity": 15000,
            "discount_percent": 5,
        }
    )
    assert card["discount_percent"] == 5
    assert card["total_quantity"] == 15000


def _fake_main_window() -> MainWindow:
    window = object.__new__(MainWindow)
    window._connection_factory = object()
    window.refresh_list = MagicMock()
    return window


def test_add_partner_opens_empty_card():
    from app import _ensure_form_import

    window = _fake_main_window()
    _ensure_form_import()
    with patch("partner_form.PartnerEditWindow") as edit_window:
        MainWindow._open_add_partner(window)
        edit_window.assert_called_once()
        _args, kwargs = edit_window.call_args
        assert kwargs["partner_id"] is None
        assert kwargs["connection_factory"] is window._connection_factory
        assert kwargs["on_saved"] is window.refresh_list


def test_double_click_opens_card_with_partner_id():
    from app import _ensure_form_import

    window = _fake_main_window()
    _ensure_form_import()
    with patch("partner_form.PartnerEditWindow") as edit_window:
        MainWindow._open_edit_partner(window, 17)
        edit_window.assert_called_once()
        _args, kwargs = edit_window.call_args
        assert kwargs["partner_id"] == 17
        assert kwargs["connection_factory"] is window._connection_factory
        assert kwargs["on_saved"] is window.refresh_list
