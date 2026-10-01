from unittest.mock import MagicMock, patch

from app import (
    ADD_PARTNER_BUTTON_TEXT,
    BG_COLOR,
    FONT_DETAILS,
    FONT_TITLE,
    MAIN_TITLE,
    MainWindow,
    RESOURCES_DIR,
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
    window = _fake_main_window()
    with patch("app.PartnerEditWindow") as edit_window:
        MainWindow._open_add_partner(window)
        edit_window.assert_called_once()
        _args, kwargs = edit_window.call_args
        assert kwargs["partner_id"] is None
        assert kwargs["connection_factory"] is window._connection_factory
        assert kwargs["on_saved"] is window.refresh_list


def test_double_click_opens_card_with_partner_id():
    window = _fake_main_window()
    with patch("app.PartnerEditWindow") as edit_window:
        MainWindow._open_edit_partner(window, 17)
        edit_window.assert_called_once()
        _args, kwargs = edit_window.call_args
        assert kwargs["partner_id"] == 17
        assert kwargs["connection_factory"] is window._connection_factory
        assert kwargs["on_saved"] is window.refresh_list


def test_open_history_without_selection_shows_error():
    window = _fake_main_window()
    window._selected_partner_id = None
    window._selected_partner_name = None
    with (
        patch("app.show_error_dialog") as error_dialog,
        patch("app.PartnerHistoryWindow") as history_window,
    ):
        MainWindow._open_history(window)
        error_dialog.assert_called_once()
        history_window.assert_not_called()


def test_open_history_with_selection_opens_history_window():
    window = _fake_main_window()
    window._selected_partner_id = 42
    window._selected_partner_name = "ООО Тест"
    with (
        patch("app.show_error_dialog") as error_dialog,
        patch("app.PartnerHistoryWindow") as history_window,
    ):
        MainWindow._open_history(window)
        error_dialog.assert_not_called()
        history_window.assert_called_once()
        args, kwargs = history_window.call_args
        assert args[0] is window
        assert kwargs["partner_id"] == 42
        assert kwargs["partner_name"] == "ООО Тест"
        assert kwargs["connection_factory"] is window._connection_factory


def test_main_window_guards_missing_resource_paths():
    """MainWindow must check path.exists() before PhotoImage / iconphoto / logo."""
    import inspect

    src = inspect.getsource(MainWindow.__init__)
    assert "icon_path.exists()" in src
    assert "logo_path.exists()" in src
    assert "iconphoto" in src


def test_load_photo_raises_clearly_when_missing(tmp_path):
    from partner_cards import _load_photo

    missing = tmp_path / "missing.png"
    try:
        _load_photo(missing)
        assert False, "expected FileNotFoundError"
    except FileNotFoundError as exc:
        assert "missing.png" in str(exc)


def test_nav_resources_png_restored():
    assert (RESOURCES_DIR / "app_icon.png").is_file()
    assert (RESOURCES_DIR / "logo.png").is_file()


def test_refresh_list_logs_errors_before_dialog():
    """MainWindow.refresh_list must call log_error before show_error_dialog."""
    import inspect

    src = inspect.getsource(MainWindow.refresh_list)
    assert "log_error" in src
    assert "Не удалось загрузить список партнёров:" in src


def test_partner_edit_save_logs_errors_before_dialog():
    """PartnerEditWindow._on_save must call log_error before show_error_dialog."""
    import inspect

    from partner_form import PartnerEditWindow

    src = inspect.getsource(PartnerEditWindow._on_save)
    assert "log_error" in src
