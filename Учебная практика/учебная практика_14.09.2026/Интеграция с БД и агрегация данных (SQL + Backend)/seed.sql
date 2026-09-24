-- Демо-данные практики 14.09 поверх ETL 07.09.
-- Не удаляет партнёров/отгрузки ETL целиком и не делает TRUNCATE представления.

-- Карточка партнёра для строк из CSV (по совпадению имени; иначе остаются DEFAULT).
UPDATE partners
SET
    partner_type = 'ООО',
    director = 'Кузнецова М.А.',
    rating = 9
WHERE name IN (
    'ООО «Логистик-Экспресс»',
    E'ООО "Логистик-Экспресс"'
);

UPDATE partners
SET
    partner_type = 'ИП',
    director = 'Петров А.В.',
    rating = 8
WHERE name = 'ИП Петров А.В.';

UPDATE partners
SET
    partner_type = 'ТК',
    director = 'Сидоров И.Н.',
    rating = 7
WHERE name IN (
    'ТК «Быстрый Путь»',
    E'ТК "Быстрый Путь"'
);

-- Партнёры сида 14.09, которых нет в ETL CSV.
INSERT INTO partners (name, inn, email, address, phone, partner_type, director, rating)
SELECT
    'ООО «СеверТранс»',
    '100000000001',
    'office@severtrans.example.com',
    'г. Мурманск, ул. Портовая, 1',
    '+7 815 220 10 01',
    'ООО',
    'Иванов С.П.',
    6
WHERE NOT EXISTS (
    SELECT 1 FROM partners WHERE name = 'ООО «СеверТранс»'
);

INSERT INTO partners (name, inn, email, address, phone, partner_type, director, rating)
SELECT
    'ООО «Магистраль»',
    '100000000005',
    'office@magistral.example.com',
    'г. Казань, ул. Вокзальная, 8',
    '+7 843 111 22 33',
    'ООО',
    'Волков Д.Е.',
    10
WHERE NOT EXISTS (
    SELECT 1 FROM partners WHERE name = 'ООО «Магистраль»'
);

-- Демо-продукт для порогов скидки.
INSERT INTO products (product_code, name, price)
SELECT 'DEMO-THRESHOLD', 'Демо-товар для порогов скидки', 1.00
WHERE NOT EXISTS (
    SELECT 1 FROM products WHERE product_code = 'DEMO-THRESHOLD'
);

-- Пороги скидки поверх ETL: демо-qty + уже существующий SUM(quantity_shipped)
-- по партнёру должны остаться в целевой полосе (<10k→0, 10k–49999→5,
-- 50k–299999→10, ≥300k→15). ETL: Логистик 80, Петров 200, Быстрый Путь 150.
-- ООО «СеверТранс»: ETL 0 + 9999 → 0%
WITH new_order AS (
    INSERT INTO orders (partner_id, product_id, contract_number, contract_date, planned_quantity)
    SELECT p.partner_id, pr.product_id, 'DEMO-9999', CURRENT_DATE, 9999
    FROM partners AS p
    CROSS JOIN products AS pr
    WHERE p.name = 'ООО «СеверТранс»'
      AND pr.product_code = 'DEMO-THRESHOLD'
      AND NOT EXISTS (SELECT 1 FROM orders WHERE contract_number = 'DEMO-9999')
    RETURNING order_id
),
new_shipment AS (
    INSERT INTO shipments (shipment_date)
    SELECT CURRENT_DATE
    FROM new_order
    RETURNING shipment_id
)
INSERT INTO shipment_items (shipment_id, order_id, quantity_shipped)
SELECT ns.shipment_id, no.order_id, 9999
FROM new_order AS no
CROSS JOIN new_shipment AS ns;

-- ИП Петров А.В.: ETL 200 + 10000 = 10200 → 5%
WITH new_order AS (
    INSERT INTO orders (partner_id, product_id, contract_number, contract_date, planned_quantity)
    SELECT p.partner_id, pr.product_id, 'DEMO-10000', CURRENT_DATE, 10000
    FROM partners AS p
    CROSS JOIN products AS pr
    WHERE p.name = 'ИП Петров А.В.'
      AND pr.product_code = 'DEMO-THRESHOLD'
      AND NOT EXISTS (SELECT 1 FROM orders WHERE contract_number = 'DEMO-10000')
    RETURNING order_id
),
new_shipment AS (
    INSERT INTO shipments (shipment_date)
    SELECT CURRENT_DATE
    FROM new_order
    RETURNING shipment_id
)
INSERT INTO shipment_items (shipment_id, order_id, quantity_shipped)
SELECT ns.shipment_id, no.order_id, 10000
FROM new_order AS no
CROSS JOIN new_shipment AS ns;

-- ООО «Логистик-Экспресс»: ETL 80 + 50000 = 50080 → 10%
WITH new_order AS (
    INSERT INTO orders (partner_id, product_id, contract_number, contract_date, planned_quantity)
    SELECT p.partner_id, pr.product_id, 'DEMO-50000', CURRENT_DATE, 50000
    FROM partners AS p
    CROSS JOIN products AS pr
    WHERE p.name IN ('ООО «Логистик-Экспресс»', E'ООО "Логистик-Экспресс"')
      AND pr.product_code = 'DEMO-THRESHOLD'
      AND NOT EXISTS (SELECT 1 FROM orders WHERE contract_number = 'DEMO-50000')
    RETURNING order_id
),
new_shipment AS (
    INSERT INTO shipments (shipment_date)
    SELECT CURRENT_DATE
    FROM new_order
    RETURNING shipment_id
)
INSERT INTO shipment_items (shipment_id, order_id, quantity_shipped)
SELECT ns.shipment_id, no.order_id, 50000
FROM new_order AS no
CROSS JOIN new_shipment AS ns;

-- ООО «Магистраль»: ETL 0 + 300000 → 15%
WITH new_order AS (
    INSERT INTO orders (partner_id, product_id, contract_number, contract_date, planned_quantity)
    SELECT p.partner_id, pr.product_id, 'DEMO-300000', CURRENT_DATE, 300000
    FROM partners AS p
    CROSS JOIN products AS pr
    WHERE p.name = 'ООО «Магистраль»'
      AND pr.product_code = 'DEMO-THRESHOLD'
      AND NOT EXISTS (SELECT 1 FROM orders WHERE contract_number = 'DEMO-300000')
    RETURNING order_id
),
new_shipment AS (
    INSERT INTO shipments (shipment_date)
    SELECT CURRENT_DATE
    FROM new_order
    RETURNING shipment_id
)
INSERT INTO shipment_items (shipment_id, order_id, quantity_shipped)
SELECT ns.shipment_id, no.order_id, 300000
FROM new_order AS no
CROSS JOIN new_shipment AS ns;
