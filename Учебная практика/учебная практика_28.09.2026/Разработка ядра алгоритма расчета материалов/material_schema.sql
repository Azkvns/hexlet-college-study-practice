CREATE TABLE IF NOT EXISTS product_types (
    product_type_id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    coefficient DECIMAL NOT NULL
);

CREATE TABLE IF NOT EXISTS material_types (
    material_type_id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    defect_percent DECIMAL NOT NULL
);
