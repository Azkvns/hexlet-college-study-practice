TRUNCATE TABLE
    shipment_items,
    shipments,
    orders,
    products,
    partners
    RESTART IDENTITY;

\copy partners (partner_id, name, inn, email, address, phone) FROM 'data/partners.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
\copy products (product_id, product_code, name, price) FROM 'data/products.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
\copy orders (order_id, partner_id, product_id, contract_number, contract_date, planned_quantity) FROM 'data/orders.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
\copy shipments (shipment_id, shipment_date) FROM 'data/shipments.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
\copy shipment_items (shipment_item_id, shipment_id, order_id, quantity_shipped) FROM 'data/shipment_items.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')

SELECT setval(pg_get_serial_sequence('partners', 'partner_id'),
              (SELECT MAX(partner_id) FROM partners));
SELECT setval(pg_get_serial_sequence('products', 'product_id'),
              (SELECT MAX(product_id) FROM products));
SELECT setval(pg_get_serial_sequence('orders', 'order_id'),
              (SELECT MAX(order_id) FROM orders));
SELECT setval(pg_get_serial_sequence('shipments', 'shipment_id'),
              (SELECT MAX(shipment_id) FROM shipments));
SELECT setval(pg_get_serial_sequence('shipment_items', 'shipment_item_id'),
              (SELECT MAX(shipment_item_id) FROM shipment_items));

SELECT COUNT(*) AS partners_count FROM partners;
SELECT COUNT(*) AS products_count FROM products;
SELECT COUNT(*) AS orders_count FROM orders;
SELECT COUNT(*) AS shipments_count FROM shipments;
SELECT COUNT(*) AS shipment_items_count FROM shipment_items;
