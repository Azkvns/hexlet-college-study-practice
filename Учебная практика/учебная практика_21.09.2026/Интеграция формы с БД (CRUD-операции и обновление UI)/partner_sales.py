import psycopg2.extras

from db import get_connection
from discount import calculate_partner_discount

_PARTNER_SALES_SQL = """
SELECT
    p.partner_id,
    p.name,
    p.inn,
    p.email,
    p.address,
    p.phone,
    p.partner_type,
    p.director,
    p.rating,
    COALESCE(SUM(sh.quantity), 0) AS total_quantity
FROM partners AS p
LEFT JOIN sales_history AS sh ON sh.partner_id = p.partner_id
WHERE p.partner_id = %s
GROUP BY
    p.partner_id, p.name, p.inn, p.email, p.address, p.phone,
    p.partner_type, p.director, p.rating
"""

_LIST_PARTNERS_SQL = """
SELECT
    p.partner_id,
    p.name,
    p.inn,
    p.email,
    p.address,
    p.phone,
    p.partner_type,
    p.director,
    p.rating,
    COALESCE(SUM(sh.quantity), 0) AS total_quantity
FROM partners AS p
LEFT JOIN sales_history AS sh ON sh.partner_id = p.partner_id
GROUP BY
    p.partner_id, p.name, p.inn, p.email, p.address, p.phone,
    p.partner_type, p.director, p.rating
ORDER BY p.name
"""


def _normalize_total_quantity(raw) -> int:
    if raw is None:
        return 0
    return int(raw)


def _row_to_partner(row) -> dict:
    total_quantity = _normalize_total_quantity(row["total_quantity"])
    return {
        "partner_id": row["partner_id"],
        "name": row["name"],
        "inn": row["inn"],
        "email": row["email"],
        "address": row["address"],
        "phone": row["phone"],
        "partner_type": row["partner_type"],
        "director": row["director"],
        "rating": row["rating"],
        "total_quantity": total_quantity,
        "discount_percent": calculate_partner_discount(total_quantity),
    }


def get_partner_with_discount(partner_id: int, connection=None):
    own_connection = connection is None
    if own_connection:
        connection = get_connection()
    try:
        with connection.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        ) as cursor:
            cursor.execute(_PARTNER_SALES_SQL, (partner_id,))
            row = cursor.fetchone()
        if row is None:
            return None
        return _row_to_partner(row)
    finally:
        if own_connection:
            connection.close()


def list_partners_with_discount(connection=None):
    own_connection = connection is None
    if own_connection:
        connection = get_connection()
    try:
        with connection.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        ) as cursor:
            cursor.execute(_LIST_PARTNERS_SQL)
            rows = cursor.fetchall()
        return [_row_to_partner(row) for row in rows]
    finally:
        if own_connection:
            connection.close()
