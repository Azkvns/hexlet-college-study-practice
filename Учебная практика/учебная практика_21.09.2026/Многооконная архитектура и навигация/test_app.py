from app import (
    ADD_PARTNER_BUTTON_TEXT,
    BG_COLOR,
    FONT_DETAILS,
    FONT_TITLE,
    MAIN_TITLE,
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
