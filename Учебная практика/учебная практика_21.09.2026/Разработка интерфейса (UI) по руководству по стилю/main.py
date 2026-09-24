from __future__ import annotations

import tkinter as tk
from pathlib import Path

from partners_data import (
    Partner,
    format_discount,
    format_partner_title,
    format_rating,
    get_demo_partners,
)

APP_DIR = Path(__file__).resolve().parent
RESOURCES_DIR = APP_DIR / "resources"

BG_COLOR = "#FFFFFF"
FG_COLOR = "#000000"
BORDER_COLOR = "#000000"
CARD_PAD_X = 24
CARD_PAD_RIGHT_DISCOUNT = 80
CARD_PAD_Y = 12
CARD_GAP = 20
FONT_TITLE = ("Arial", 11)
FONT_DETAILS = ("Arial", 9)
LINE_PADY = 0


def _load_photo(path: Path) -> tk.PhotoImage:
    return tk.PhotoImage(file=str(path))


def create_partner_card(parent: tk.Widget, partner: Partner) -> tk.Frame:
    card = tk.Frame(
        parent,
        bg=BG_COLOR,
        highlightbackground=BORDER_COLOR,
        highlightcolor=BORDER_COLOR,
        highlightthickness=1,
    )

    header = tk.Frame(card, bg=BG_COLOR)
    header.pack(
        fill="x",
        padx=(CARD_PAD_X, CARD_PAD_RIGHT_DISCOUNT),
        pady=(CARD_PAD_Y, 0),
    )

    tk.Label(
        header,
        text=format_partner_title(partner),
        font=FONT_TITLE,
        fg=FG_COLOR,
        bg=BG_COLOR,
        anchor="w",
    ).pack(side="left", fill="x", expand=True)

    tk.Label(
        header,
        text=format_discount(partner),
        font=FONT_TITLE,
        fg=FG_COLOR,
        bg=BG_COLOR,
        anchor="e",
    ).pack(side="right")

    details_text = "\n".join(
        (partner["director"], partner["phone"], format_rating(partner)),
    )
    tk.Label(
        card,
        text=details_text,
        font=FONT_DETAILS,
        fg=FG_COLOR,
        bg=BG_COLOR,
        anchor="w",
        justify="left",
        pady=LINE_PADY,
    ).pack(anchor="w", padx=CARD_PAD_X, pady=(0, CARD_PAD_Y))

    return card


def build_app() -> tk.Tk:
    root = tk.Tk()
    root.title("CRM: Список партнеров и скидок")
    root.configure(bg=BG_COLOR)

    icon_path = RESOURCES_DIR / "app_icon.png"
    logo_path = RESOURCES_DIR / "logo.png"

    app_icon = _load_photo(icon_path)
    root.iconphoto(True, app_icon)
    root._app_icon = app_icon  # keep reference

    header = tk.Frame(root, bg=BG_COLOR)
    header.pack(fill="x", padx=16, pady=(16, 8))

    logo = _load_photo(logo_path)
    root._logo = logo
    tk.Label(header, image=logo, bg=BG_COLOR).pack(side="left")

    tk.Label(
        header,
        text="Список партнеров и скидок",
        font=FONT_TITLE,
        fg=FG_COLOR,
        bg=BG_COLOR,
    ).pack(side="left", padx=(12, 0))

    list_outer = tk.Frame(root, bg=BG_COLOR, highlightbackground=BORDER_COLOR, highlightthickness=1)
    list_outer.pack(fill="both", expand=True, padx=16, pady=(0, 16))

    list_inner = tk.Frame(list_outer, bg=BG_COLOR)
    list_inner.pack(fill="both", expand=True, anchor="n", padx=CARD_GAP, pady=CARD_GAP)

    partners = get_demo_partners()
    for index, partner in enumerate(partners):
        card = create_partner_card(list_inner, partner)
        bottom_gap = CARD_GAP if index < len(partners) - 1 else 0
        card.pack(fill="x", expand=False, pady=(0, bottom_gap))

    # Свободная высота окна — в распорке, а не в последней карточке.
    tk.Frame(list_inner, bg=BG_COLOR, height=1).pack(fill="both", expand=True)

    root.update_idletasks()
    root.minsize(480, root.winfo_reqheight())

    return root


def main() -> None:
    build_app().mainloop()


if __name__ == "__main__":
    main()
