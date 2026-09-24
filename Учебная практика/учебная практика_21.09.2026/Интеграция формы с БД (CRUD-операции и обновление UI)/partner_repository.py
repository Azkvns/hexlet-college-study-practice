import psycopg2.extras

_GET_PARTNER_SQL = """
SELECT
    partner_id,
    name,
    inn,
    email,
    address,
    phone,
    partner_type,
    director,
    rating
FROM partners
WHERE partner_id = %s
"""

_INSERT_PARTNER_SQL = """
INSERT INTO partners (
    name,
    inn,
    email,
    address,
    phone,
    partner_type,
    director,
    rating
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
RETURNING partner_id
"""

_UPDATE_PARTNER_SQL = """
UPDATE partners
SET
    name = %s,
    inn = %s,
    email = %s,
    address = %s,
    phone = %s,
    partner_type = %s,
    director = %s,
    rating = %s
WHERE partner_id = %s
"""


def _partner_params(data: dict) -> tuple:
    return (
        data["name"],
        data["inn"],
        data["email"],
        data["address"],
        data["phone"],
        data["partner_type"],
        data["director"],
        data["rating"],
    )


def get_partner(partner_id: int, connection) -> dict | None:
    with connection.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor
    ) as cursor:
        cursor.execute(_GET_PARTNER_SQL, (partner_id,))
        row = cursor.fetchone()
    if row is None:
        return None
    return dict(row)


def insert_partner(data: dict, connection) -> int:
    with connection.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor
    ) as cursor:
        cursor.execute(_INSERT_PARTNER_SQL, _partner_params(data))
        row = cursor.fetchone()
    return int(row["partner_id"])


def update_partner(partner_id: int, data: dict, connection) -> None:
    params = _partner_params(data) + (partner_id,)
    with connection.cursor() as cursor:
        cursor.execute(_UPDATE_PARTNER_SQL, params)
