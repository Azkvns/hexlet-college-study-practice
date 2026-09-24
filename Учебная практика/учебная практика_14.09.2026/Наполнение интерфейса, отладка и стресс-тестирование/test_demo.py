import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_UI_DIR = _REPO_ROOT / "Разработка интерфейса (UI) по руководству по стилю"
if str(_UI_DIR) not in sys.path:
    sys.path.insert(0, str(_UI_DIR))

from partners_data import format_discount

from partners_adapter import to_partner_card


def test_demo_pipeline_zero_and_positive_discount():
    rows = [
        {
            "partner_id": 1,
            "name": "Нет продаж",
            "phone": "1",
            "total_quantity": None,
            "discount_percent": 0,
        },
        {
            "partner_id": 2,
            "name": "Есть объём",
            "phone": "2",
            "total_quantity": 12000,
            "discount_percent": 5,
        },
    ]
    cards = [to_partner_card(r) for r in rows]
    assert cards[0]["discount_percent"] == 0
    assert format_discount(cards[0]) == "0%"
    assert cards[1]["discount_percent"] == 5
    assert format_discount(cards[1]) == "5%"
