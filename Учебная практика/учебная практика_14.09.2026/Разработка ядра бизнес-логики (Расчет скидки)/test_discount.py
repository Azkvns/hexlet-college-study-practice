import pytest

from discount import calculate_partner_discount


@pytest.mark.parametrize(
    ("total_quantity", "expected_discount"),
    [
        (-1, 0),
        (0, 0),
        (9999, 0),
        (10000, 5),
        (49999, 5),
        (50000, 10),
        (299999, 10),
        (300000, 15),
        (300001, 15),
    ],
)
def test_calculate_partner_discount(
    total_quantity: int,
    expected_discount: int,
) -> None:
    assert calculate_partner_discount(total_quantity) == expected_discount
