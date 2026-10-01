class MemoryMaterialCatalog:
    def __init__(self):
        self._product_coefficients = {
            1: 1.5,
            2: 2.5,
        }
        self._material_defect_percents = {
            1: 0.0,
            2: 2.0,
        }

    def get_product_coefficient(self, product_type_id: int):
        return self._product_coefficients.get(product_type_id)

    def get_material_defect_percent(self, material_type_id: int):
        return self._material_defect_percents.get(material_type_id)


class DbMaterialCatalog:
    def __init__(self, connection):
        self._connection = connection

    def get_product_coefficient(self, product_type_id: int):
        with self._connection.cursor() as cursor:
            cursor.execute(
                "SELECT coefficient FROM product_types WHERE product_type_id = %s",
                (product_type_id,),
            )
            row = cursor.fetchone()
        if row is None:
            return None
        return float(row[0])

    def get_material_defect_percent(self, material_type_id: int):
        with self._connection.cursor() as cursor:
            cursor.execute(
                "SELECT defect_percent FROM material_types WHERE material_type_id = %s",
                (material_type_id,),
            )
            row = cursor.fetchone()
        if row is None:
            return None
        return float(row[0])
