-- Расширение схемы 07.09 под карточку партнёра и объём продаж (практика 14.09).
-- Базовые таблицы не заменяются: только ALTER + VIEW.

ALTER TABLE partners
    ALTER COLUMN phone TYPE VARCHAR(30);

ALTER TABLE partners
    ADD COLUMN partner_type VARCHAR(64) NOT NULL DEFAULT 'ООО',
    ADD COLUMN director VARCHAR(255) NOT NULL DEFAULT '',
    ADD COLUMN rating INTEGER NOT NULL DEFAULT 0,
    ADD CONSTRAINT chk_partners_rating CHECK (rating >= 0);

CREATE OR REPLACE VIEW sales_history AS
SELECT
    si.shipment_item_id AS sale_id,
    o.partner_id,
    si.quantity_shipped AS quantity
FROM shipment_items AS si
JOIN orders AS o ON o.order_id = si.order_id;

COMMENT ON COLUMN partners.partner_type IS 'Тип партнёра (ООО, ИП, ТК, …)';
COMMENT ON COLUMN partners.director IS 'ФИО директора';
COMMENT ON COLUMN partners.rating IS 'Рейтинг партнёра (целое >= 0)';
COMMENT ON VIEW sales_history IS 'Объём отгрузок в формате sales_history для агрегации скидки';
