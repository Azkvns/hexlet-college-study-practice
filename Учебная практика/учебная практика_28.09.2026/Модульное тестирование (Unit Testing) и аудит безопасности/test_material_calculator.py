import sys
from pathlib import Path

_CORE_DIR = (
    Path(__file__).resolve().parent.parent
    / "Разработка ядра алгоритма расчета материалов"
)
sys.path.insert(0, str(_CORE_DIR))

from material_calculator import calculate_material_amount
from material_catalog import MemoryMaterialCatalog


def test_standard_calculation_returns_92():
    catalog = MemoryMaterialCatalog()
    result = calculate_material_amount(1, 2, 10, 2, 3, catalog)
    assert result == 92


def test_ceil_rounding_returns_2_not_1():
    catalog = MemoryMaterialCatalog()
    result = calculate_material_amount(1, 1, 1, 1.1, 1.1, catalog)
    assert result == 2
    assert result != 1


def test_unknown_type_returns_minus_one():
    catalog = MemoryMaterialCatalog()
    assert calculate_material_amount(99, 1, 10, 2, 3, catalog) == -1
    assert calculate_material_amount(1, 99, 10, 2, 3, catalog) == -1


def test_negative_params_return_minus_one():
    catalog = MemoryMaterialCatalog()
    assert calculate_material_amount(1, 2, 10, -1, 3, catalog) == -1
    assert calculate_material_amount(1, 2, 10, 2, -0.5, catalog) == -1


def test_non_positive_quantity_returns_minus_one():
    catalog = MemoryMaterialCatalog()
    assert calculate_material_amount(1, 2, 0, 2, 3, catalog) == -1
    assert calculate_material_amount(1, 2, -3, 2, 3, catalog) == -1
