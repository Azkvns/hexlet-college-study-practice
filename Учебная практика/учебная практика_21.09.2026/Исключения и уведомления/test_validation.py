import pytest

from validation import validate_partner


def _valid_partner(**overrides):
    data = {
        "name": "ООО Тест",
        "email": "test@example.ru",
        "rating": 0,
    }
    data.update(overrides)
    return data


def test_validate_partner_rejects_empty_name():
    with pytest.raises(ValueError):
        validate_partner(_valid_partner(name=""))

    with pytest.raises(ValueError):
        validate_partner(_valid_partner(name="   "))


def test_validate_partner_rejects_empty_email():
    with pytest.raises(ValueError):
        validate_partner(_valid_partner(email=""))

    with pytest.raises(ValueError):
        validate_partner(_valid_partner(email="   "))


def test_validate_partner_rejects_invalid_rating():
    with pytest.raises(ValueError):
        validate_partner(_valid_partner(rating=-1))

    with pytest.raises(ValueError):
        validate_partner(_valid_partner(rating=1.5))

    with pytest.raises(ValueError):
        validate_partner(_valid_partner(rating="abc"))


def test_validate_partner_accepts_zero_rating_and_nonempty_fields():
    validate_partner(_valid_partner(name=" Партнёр ", email=" a@b.ru ", rating=0))
    validate_partner(_valid_partner(rating=11))
