from __future__ import annotations

import importlib.util
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

from partners_adapter import load_partner_cards

_REPO_ROOT = Path(__file__).resolve().parent.parent
_UI_DIR = _REPO_ROOT / "Разработка интерфейса (UI) по руководству по стилю"
RESOURCES_DIR = _UI_DIR / "resources"


def _load_ui_module():
    if str(_UI_DIR) not in sys.path:
        sys.path.insert(0, str(_UI_DIR))
    spec = importlib.util.spec_from_file_location("crm_ui_main", _UI_DIR / "main.py")
    if spec is None or spec.loader is None:
        raise ImportError("Cannot load UI main module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _fetch_partners():
    try:
        return load_partner_cards()
    except Exception as exc:
        messagebox.showerror(
            "Ошибка базы данных",
            f"Не удалось загрузить список партнёров:\n{exc}",
        )
        return []


def build_app() -> tk.Tk:
    ui = _load_ui_module()

    root = tk.Tk()
    root.title("CRM: Список партнеров и скидок")
    root.configure(bg=ui.BG_COLOR)

    icon_path = RESOURCES_DIR / "app_icon.png"
    logo_path = RESOURCES_DIR / "logo.png"

    app_icon = ui._load_photo(icon_path)
    root.iconphoto(True, app_icon)
    root._app_icon = app_icon

    header = tk.Frame(root, bg=ui.BG_COLOR)
    header.pack(fill="x", padx=16, pady=(16, 8))

    logo = ui._load_photo(logo_path)
    root._logo = logo
    tk.Label(header, image=logo, bg=ui.BG_COLOR).pack(side="left")

    tk.Label(
        header,
        text="Список партнеров и скидок",
        font=ui.FONT_TITLE,
        fg=ui.FG_COLOR,
        bg=ui.BG_COLOR,
    ).pack(side="left", padx=(12, 0))

    list_outer = tk.Frame(
        root,
        bg=ui.BG_COLOR,
        highlightbackground=ui.BORDER_COLOR,
        highlightthickness=1,
    )
    list_outer.pack(fill="both", expand=True, padx=16, pady=(0, 16))

    list_inner = tk.Frame(list_outer, bg=ui.BG_COLOR)
    list_inner.pack(fill="both", expand=True, anchor="n", padx=ui.CARD_GAP, pady=ui.CARD_GAP)

    partners = _fetch_partners()
    if not partners:
        tk.Label(
            list_inner,
            text="Нет данных для отображения.",
            font=ui.FONT_TITLE,
            fg=ui.FG_COLOR,
            bg=ui.BG_COLOR,
        ).pack(anchor="w")

    for index, partner in enumerate(partners):
        card = ui.create_partner_card(list_inner, partner)
        bottom_gap = ui.CARD_GAP if index < len(partners) - 1 else 0
        card.pack(fill="x", expand=False, pady=(0, bottom_gap))

    tk.Frame(list_inner, bg=ui.BG_COLOR, height=1).pack(fill="both", expand=True)

    root.update_idletasks()
    root.minsize(480, root.winfo_reqheight())

    return root


def main() -> None:
    build_app().mainloop()


if __name__ == "__main__":
    main()
