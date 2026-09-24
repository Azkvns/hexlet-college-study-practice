from partners_data import (
    format_discount,
    format_partner_title,
    format_rating,
    get_demo_partners,
)


def test_format_partner_title():
    p = {"partner_type": "Партнер", "name": "ООО «Ромашка»"}
    assert format_partner_title(p) == "Партнер | ООО «Ромашка»"


def test_format_discount():
    assert format_discount({"discount_percent": 10}) == "10%"


def test_format_discount_none_and_missing():
    assert format_discount({"discount_percent": None}) == "0%"
    assert format_discount({}) == "0%"


def test_format_rating():
    assert format_rating({"rating": 10}) == "Рейтинг: 10"


def test_get_demo_partners_len_3():
    partners = get_demo_partners()
    assert len(partners) == 3
    assert set(partners[0]) >= {
        "partner_type",
        "name",
        "director",
        "phone",
        "rating",
        "discount_percent",
    }
