from tkinter import messagebox

ERROR_TITLE = "Ошибка"
WARNING_TITLE = "Предупреждение"
INFO_TITLE = "Информация"
UNSAVED_MESSAGE = (
    "Есть несохранённые данные. Закрыть карточку без сохранения?"
)
SUCCESS_MESSAGE = "Данные партнёра успешно сохранены."


def show_error_dialog(message: str, parent=None) -> None:
    messagebox.showerror(ERROR_TITLE, message, parent=parent)


def show_unsaved_warning(parent=None) -> bool:
    return bool(
        messagebox.askyesno(WARNING_TITLE, UNSAVED_MESSAGE, parent=parent)
    )


def show_success_dialog(message: str = SUCCESS_MESSAGE, parent=None) -> None:
    messagebox.showinfo(INFO_TITLE, message, parent=parent)
