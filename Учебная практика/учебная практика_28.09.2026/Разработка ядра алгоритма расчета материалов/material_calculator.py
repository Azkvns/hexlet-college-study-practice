import math


def calculate_material_amount(
    product_type_id: int,
    material_type_id: int,
    quantity: int,
    param_1: float,
    param_2: float,
    catalog,
) -> int:
    if type(product_type_id) is not int or type(material_type_id) is not int:
        return -1
    if type(quantity) is not int or quantity <= 0:
        return -1
    if param_1 <= 0 or param_2 <= 0:
        return -1
    coefficient = catalog.get_product_coefficient(product_type_id)
    defect_percent = catalog.get_material_defect_percent(material_type_id)
    if coefficient is None or defect_percent is None:
        return -1
    per_unit = param_1 * param_2 * coefficient
    net_total = per_unit * quantity
    with_defect = net_total * (1 + defect_percent / 100)
    # ceil: дробный расход округляется вверх до целых единиц сырья
    return math.ceil(with_defect)
