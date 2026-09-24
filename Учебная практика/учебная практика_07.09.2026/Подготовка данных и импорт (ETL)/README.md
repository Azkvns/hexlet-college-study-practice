# Импорт данных

Исходники: `import_partners.csv` и `import_sales.txt`. Дублей не было, но данные кривые.

Что поправил:

- пробелы в названиях (` ООО "Логистик-Экспресс" ` и т.п.)
- пустой телефон у Петрова → `Не указан`
- дату `15.03.2026` → `2026-03-15`
- продажа на `partner_id=4`, которого не было — добавил заглушку (ИНН `0000000000`)
- `rating` выкинул, в схеме его нет
- адреса в исходнике нет, в таблицу пишу `Адрес не указан`

Дальше разложил продажи по нашим таблицам. Файлы для загрузки лежат в `data/`.

Цены взял как `total_amount / quantity` по первой продаже товара:

- порошок «Альфа» — 500
- мыло «Стандарт» — 90
- кондиционер — 350

Каждая продажа = заказ + накладная + строка. Номер договора: `IMP-` + `sale_id`.

После импорта должно быть: partners 4, products 3, orders 5, shipments 5, shipment_items 5.

## Как залить

Сначала схема, потом импорт (запускать из этой папки, `\copy` смотрит относительные пути):

```bash
psql -d your_db -f "../Написание DDL-скрипта (База данных в коде)/schema.sql"
psql -d your_db -f import.sql
```

Либо в DBeaver: Import Data по csv из `data/`, порядок partners → products → orders → shipments → shipment_items.

Проверка — `verify.sql` (те же COUNT в конце `import.sql`):

```sql
SELECT COUNT(*) FROM partners;
SELECT COUNT(*) FROM products;
SELECT COUNT(*) FROM orders;
SELECT COUNT(*) FROM shipments;
SELECT COUNT(*) FROM shipment_items;
```
