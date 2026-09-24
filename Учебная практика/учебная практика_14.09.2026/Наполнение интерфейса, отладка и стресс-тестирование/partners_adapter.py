from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable

DEFAULT_PARTNER_TYPE = "Партнер"
DEFAULT_DIRECTOR = "Директор"
DEFAULT_RATING = 10

_REPO_ROOT = Path(__file__).resolve().parent.parent
_INTEGRATION_DIR = _REPO_ROOT / "Интеграция с БД и агрегация данных (SQL + Backend)"
if str(_INTEGRATION_DIR) not in sys.path:
    sys.path.insert(0, str(_INTEGRATION_DIR))

PartnerCard = dict[str, Any]
BackendRow = dict[str, Any]
Fetcher = Callable[[], list[BackendRow]]


def to_partner_card(row: BackendRow) -> PartnerCard:
    raw_qty = row.get("total_quantity")
    total_quantity = 0 if raw_qty is None else int(raw_qty)
    discount = row.get("discount_percent")
    if discount is None:
        discount = 0
    director = row.get("director") or DEFAULT_DIRECTOR
    rating = row.get("rating")
    if rating is None:
        rating = DEFAULT_RATING
    return {
        "partner_id": row.get("partner_id"),
        "partner_type": row.get("partner_type") or DEFAULT_PARTNER_TYPE,
        "name": row["name"],
        "director": director,
        "phone": row["phone"],
        "rating": int(rating),
        "total_quantity": total_quantity,
        "discount_percent": int(discount),
    }


def load_partner_cards(fetcher: Fetcher | None = None) -> list[PartnerCard]:
    if fetcher is None:
        from partner_sales import list_partners_with_discount

        fetcher = list_partners_with_discount
    return [to_partner_card(row) for row in fetcher()]
