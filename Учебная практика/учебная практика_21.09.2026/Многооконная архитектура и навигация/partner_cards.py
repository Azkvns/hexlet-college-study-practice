from __future__ import annotations

import tkinter as tk
from pathlib import Path

from partners_data import (
    Partner,
    format_discount,
    format_partner_title,
    format_rating,
)

BG_COLOR = "#FFFFFF"
FG_COLOR = "#000000"
BORDER_COLOR = "#000000"
CARD_PAD_X = 24
CARD_PAD_RIGHT_DISCOUNT = 80
CARD_PAD_Y = 12
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
