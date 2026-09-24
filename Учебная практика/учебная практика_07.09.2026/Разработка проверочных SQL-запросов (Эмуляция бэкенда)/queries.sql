-- список партнёров + сколько у них доставок
SELECT
    p.partner_id,
    p.name,
    p.inn,
    p.email,
    p.phone,
    COUNT(DISTINCT s.shipment_id) AS deliveries_count
FROM partners AS p
LEFT JOIN orders AS o
    ON o.partner_id = p.partner_id
LEFT JOIN shipment_items AS si
    ON si.order_id = o.order_id
LEFT JOIN shipments AS s
    ON s.shipment_id = si.shipment_id
GROUP BY
    p.partner_id,
    p.name,
    p.inn,
    p.email,
    p.phone
ORDER BY p.name;


-- новый партнёр и его первая отгрузка в одной транзакции
BEGIN;

WITH new_partner AS (
    INSERT INTO partners (name, inn, email, address, phone)
    VALUES (
        'ООО «Тест-Доставка»',
        '7703999001',
        'test-delivery@example.ru',
        'г. Москва, ул. Тестовая, 1',
        '+7 (495) 000-00-01'
    )
    ON CONFLICT (inn) DO UPDATE
        SET name    = EXCLUDED.name,
            email   = EXCLUDED.email,
            address = EXCLUDED.address,
            phone   = EXCLUDED.phone
    RETURNING partner_id
),
new_order AS (
    INSERT INTO orders (
        partner_id,
        product_id,
        contract_number,
        contract_date,
        planned_quantity
    )
    SELECT
        np.partner_id,
        1,
        'TEST-001',
        DATE '2026-04-01',
        10
    FROM new_partner AS np
    RETURNING order_id
),
new_shipment AS (
    INSERT INTO shipments (shipment_date)
    VALUES (DATE '2026-04-01')
    RETURNING shipment_id
)
INSERT INTO shipment_items (shipment_id, order_id, quantity_shipped)
SELECT
    ns.shipment_id,
    no.order_id,
    10
FROM new_shipment AS ns
CROSS JOIN new_order AS no;

COMMIT;


-- история отгрузок партнёра 1 за март 2026
SELECT
    s.shipment_id,
    s.shipment_date,
    pr.product_code,
    pr.name AS product_name,
    o.contract_number,
    si.quantity_shipped,
    pr.price AS unit_price,
    (si.quantity_shipped * pr.price) AS shipment_amount,
    SUM(si.quantity_shipped * pr.price) OVER () AS period_total
FROM partners AS pt
JOIN orders AS o
    ON o.partner_id = pt.partner_id
JOIN shipment_items AS si
    ON si.order_id = o.order_id
JOIN shipments AS s
    ON s.shipment_id = si.shipment_id
JOIN products AS pr
    ON pr.product_id = o.product_id
WHERE pt.partner_id = 1
  AND s.shipment_date BETWEEN DATE '2026-03-01' AND DATE '2026-03-31'
ORDER BY s.shipment_date, s.shipment_id, pr.name;
