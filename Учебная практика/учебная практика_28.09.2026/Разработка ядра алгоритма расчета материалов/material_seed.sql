INSERT INTO product_types (product_type_id, name, coefficient)
VALUES
    (1, 'Тип продукции 1', 1.5),
    (2, 'Тип продукции 2', 2.5)
ON CONFLICT (product_type_id) DO NOTHING;

INSERT INTO material_types (material_type_id, name, defect_percent)
VALUES
    (1, 'Тип материала 1', 0),
    (2, 'Тип материала 2', 2)
ON CONFLICT (material_type_id) DO NOTHING;
