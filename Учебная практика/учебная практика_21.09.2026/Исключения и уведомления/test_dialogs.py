from unittest.mock import patch

from dialogs import (
    show_error_dialog,
    show_success_dialog,
    show_unsaved_warning,
)


def test_show_error_dialog_uses_error_icon_and_title():
    with patch("dialogs.messagebox.showerror") as showerror:
        show_error_dialog("Рейтинг должен быть целым числом от 0")
        showerror.assert_called_once()
        args, kwargs = showerror.call_args
        assert args[0] == "Ошибка"
        assert "Рейтинг" in args[1]


def test_show_unsaved_warning_uses_warning_and_returns_bool():
    with patch("dialogs.messagebox.askyesno", return_value=True) as askyesno:
        result = show_unsaved_warning()
        assert result is True
        askyesno.assert_called_once()
        args, _kwargs = askyesno.call_args
        assert args[0] == "Предупреждение"
        assert "несохранённ" in args[1].lower() or "несохраненн" in args[1].lower()


def test_show_success_dialog_uses_info_icon_and_title():
    with patch("dialogs.messagebox.showinfo") as showinfo:
        show_success_dialog()
        showinfo.assert_called_once()
        args, _kwargs = showinfo.call_args
        assert args[0] == "Информация"
        assert args[1]
