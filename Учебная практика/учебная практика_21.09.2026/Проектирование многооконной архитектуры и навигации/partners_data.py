from __future__ import annotations

from typing import Any

Partner = dict[str, Any]

_DEMO_PARTNERS: list[Partner] = [
    {
        "partner_type": "ООО",
        "name": 'ООО «Логистик-Экспресс»',
        "director": "Кузнецова М.А.",
        "phone": "+7 223 322 22 32",
        "rating": 9,
        "discount_percent": 10,
    },
    {
        "partner_type": "ИП",
        "name": "ИП Петров А.В.",
        "director": "Петров А.В.",
        "phone": "+7 495 322 22 32",
        "rating": 8,
        "discount_percent": 5,
    },
    {
        "partner_type": "ТК",
        "name": "ТК «Быстрый Путь»",
        "director": "Сидоров И.Н.",
        "phone": "+7 812 555 44 33",
        "rating": 7,
        "discount_percent": 0,
    },
]


def get_demo_partners() -> list[Partner]:
    return list(_DEMO_PARTNERS)


def format_partner_title(partner: Partner) -> str:
    return f"{partner['partner_type']} | {partner['name']}"


def format_discount(partner: Partner) -> str:
    value = partner.get("discount_percent")
    if value is None:
        value = 0
    return f"{value}%"


def format_rating(partner: Partner) -> str:
    return f"Рейтинг: {partner['rating']}"
