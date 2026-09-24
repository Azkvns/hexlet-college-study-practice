TRUNCATE sales_history, partners RESTART IDENTITY;

INSERT INTO partners (name, inn, email, address, phone, partner_type, director, rating)
VALUES
    ('ООО «СеверТранс»', '100000000001', 'office@severtrans.example.com', 'г. Мурманск, ул. Портовая, 1', '+7 815 220 10 01', 'ООО', 'Иванов С.П.', 6),
    ('ТК «Быстрый Путь»', '100000000002', 'speedway@example.com', 'г. Санкт-Петербург, пр. Невский, 10', '+7 812 555 44 33', 'ТК', 'Сидоров И.Н.', 7),
    ('ИП Петров А.В.', '100000000003', 'petrov@example.com', 'г. Москва, ул. Садовая, 5', '+7 495 322 22 32', 'ИП', 'Петров А.В.', 8),
    ('ООО «Логистик-Экспресс»', '100000000004', 'info@logex.example.com', 'г. Москва, ул. Ленина, 12', '+7 223 322 22 32', 'ООО', 'Кузнецова М.А.', 9),
    ('ООО «Магистраль»', '100000000005', 'office@magistral.example.com', 'г. Казань, ул. Вокзальная, 8', '+7 843 111 22 33', 'ООО', 'Волков Д.Е.', 10);

-- Нет строк в sales_history → 0%
-- ТК «Быстрый Путь»: 9999 → 0%
INSERT INTO sales_history (partner_id, quantity)
SELECT partner_id, 9999
FROM partners
WHERE name = 'ТК «Быстрый Путь»';

-- ИП Петров А.В.: 10000 → 5%
INSERT INTO sales_history (partner_id, quantity)
SELECT partner_id, 10000
FROM partners
WHERE name = 'ИП Петров А.В.';

-- ООО «Логистик-Экспресс»: 20000 + 30000 = 50000 → 10%
INSERT INTO sales_history (partner_id, quantity)
SELECT partner_id, quantity
FROM partners
CROSS JOIN (VALUES (20000), (30000)) AS quantities (quantity)
WHERE name = 'ООО «Логистик-Экспресс»';

-- ООО «Магистраль»: 300000 → 15%
INSERT INTO sales_history (partner_id, quantity)
SELECT partner_id, 300000
FROM partners
WHERE name = 'ООО «Магистраль»';
