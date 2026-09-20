# Paid customer revenue

Write `query.sql`, one read-only SQLite SELECT. The schema is:

```sql
CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL, status TEXT NOT NULL);
CREATE TABLE order_items (id INTEGER PRIMARY KEY, order_id INTEGER NOT NULL,
                         quantity INTEGER NOT NULL, unit_price_cents INTEGER NOT NULL);
```

Return exactly `customer_id`, `paid_order_count`, `revenue_cents`, one row for
every customer in ascending customer ID order. Count each order with status
`paid` once, even when it has several items or no items. Revenue is the sum of
quantity times unit price for items on paid orders only. Customers without paid
orders must have zero count and zero revenue. Customer names are not unique.
The query must work on other data with this schema, including an empty orders
table; do not hardcode fixture values. No extensions or external files.

`fixture.json` contains a visible example; its expected rows are
`[[1, 2, 850], [2, 0, 0], [3, 0, 0]]`.
