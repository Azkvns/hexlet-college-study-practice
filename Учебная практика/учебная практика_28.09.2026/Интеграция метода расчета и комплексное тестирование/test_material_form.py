from material_form import (
    MATERIAL_ERROR_MESSAGE,
    apply_calculation,
    parse_calculator_input,
)


def test_parse_calculator_input_converts_types():
    parsed = parse_calculator_input(
        {
            "product_type_id": "1",
            "material_type_id": "2",
            "quantity": "10",
            "param_1": "2",
            "param_2": "3",
        }
    )
    assert parsed == {
        "product_type_id": 1,
        "material_type_id": 2,
        "quantity": 10,
        "param_1": 2.0,
        "param_2": 3.0,
    }
    assert type(parsed["product_type_id"]) is int
    assert type(parsed["material_type_id"]) is int
    assert type(parsed["quantity"]) is int
    assert type(parsed["param_1"]) is float
    assert type(parsed["param_2"]) is float


def test_parse_calculator_input_empty_quantity_returns_none():
    result = parse_calculator_input(
        {
            "product_type_id": "1",
            "material_type_id": "2",
            "quantity": "",
            "param_1": "2",
            "param_2": "3",
        }
    )
    assert result is None


def test_parse_calculator_input_text_param_returns_none():
    result = parse_calculator_input(
        {
            "product_type_id": "1",
            "material_type_id": "2",
            "quantity": "10",
            "param_1": "abc",
            "param_2": "3",
        }
    )
    assert result is None


def test_apply_calculation_minus_one_shows_error_not_label():
    texts = []
    errors = []

    def set_text(value):
        texts.append(value)

    def show_error(message):
        errors.append(message)

    apply_calculation(-1, set_text, show_error)
    assert errors == [MATERIAL_ERROR_MESSAGE]
    assert texts == []
    assert "-1" not in texts


def test_apply_calculation_success_sets_text():
    texts = []
    errors = []

    def set_text(value):
        texts.append(value)

    def show_error(message):
        errors.append(message)

    apply_calculation(92, set_text, show_error)
    assert texts == ["92"]
    assert errors == []


def test_material_error_message_exact():
    assert MATERIAL_ERROR_MESSAGE == (
        "Не удалось рассчитать расход. Проверьте, что типы существуют, "
        "параметры больше нуля, а количество — целое число больше нуля."
    )
