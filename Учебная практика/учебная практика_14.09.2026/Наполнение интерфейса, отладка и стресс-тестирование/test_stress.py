from partners_adapter import load_partner_cards, to_partner_card


def test_to_partner_card_null_quantity_and_discount():
    card = to_partner_card(
        {
            "partner_id": 1,
            "name": "X",
            "phone": "+7",
            "total_quantity": None,
            "discount_percent": None,
        }
    )
    assert card["discount_percent"] == 0
    assert card["total_quantity"] == 0
    assert card["partner_type"] == "Партнер"
    assert card["director"] == "Директор"
    assert card["rating"] == 10


def test_load_partner_cards_uses_fetcher():
    def fake():
        return [
            {
                "partner_id": 1,
                "name": "A",
                "phone": "1",
                "total_quantity": 0,
                "discount_percent": 0,
            }
        ]

    cards = load_partner_cards(fetcher=fake)
    assert len(cards) == 1
    assert cards[0]["discount_percent"] == 0


def test_to_partner_card_reads_row_fields():
    card = to_partner_card(
        {
            "partner_id": 4,
            "partner_type": "ООО",
            "name": "ООО «Магистраль»",
            "director": "Волков Д.Е.",
            "phone": "+7 843 111 22 33",
            "rating": 10,
            "total_quantity": 300000,
            "discount_percent": 15,
        }
    )
    assert card["partner_type"] == "ООО"
    assert card["director"] == "Волков Д.Е."
    assert card["rating"] == 10
    assert card["discount_percent"] == 15
