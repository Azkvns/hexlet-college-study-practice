from pathlib import Path
import re

_PRACTICE_ROOT = Path(__file__).resolve().parent.parent
_HISTORY_DIR = (
    _PRACTICE_ROOT
    / " Разработка интерфейса истории реализации продукции"
)
_CORE_DIR = (
    _PRACTICE_ROOT / "Разработка ядра алгоритма расчета материалов"
)

_MODULES = {
    "partner_repository.py": _HISTORY_DIR / "partner_repository.py",
    "partner_history.py": _HISTORY_DIR / "partner_history.py",
    "material_catalog.py": _CORE_DIR / "material_catalog.py",
    "partner_sales.py": _HISTORY_DIR / "partner_sales.py",
}

_REPOSITORY_CONSTANTS = (
    "_GET_PARTNER_SQL",
    "_INSERT_PARTNER_SQL",
    "_UPDATE_PARTNER_SQL",
)

_FSTRING_IN_EXECUTE = re.compile(
    r"execute\s*\(\s*f['\"]",
    re.MULTILINE,
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_no_fstring_inside_execute():
    for name, path in _MODULES.items():
        source = _read(path)
        assert _FSTRING_IN_EXECUTE.search(source) is None, name


def test_where_filters_use_percent_s():
    where_line = re.compile(
        r"^.*WHERE.*(?:partner_id|product_type_id|material_type_id|_id).*=.*$",
        re.IGNORECASE | re.MULTILINE,
    )
    for name, path in _MODULES.items():
        source = _read(path)
        for match in where_line.finditer(source):
            fragment = match.group(0)
            if "JOIN" in fragment.upper() and "WHERE" not in fragment.upper():
                continue
            assert "%s" in fragment, f"{name}: {fragment}"


def test_partner_repository_sql_constants_are_parameterized():
    source = _read(_MODULES["partner_repository.py"])
    for constant in _REPOSITORY_CONSTANTS:
        pattern = re.compile(
            rf"{constant}\s*=\s*\"\"\"(.*?)\"\"\"",
            re.DOTALL,
        )
        match = pattern.search(source)
        assert match is not None, constant
        body = match.group(1)
        assert "%s" in body, constant
        assert "{" not in body, constant
