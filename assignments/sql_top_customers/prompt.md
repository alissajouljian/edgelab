# SQL — Top Customers by Total Spend (SQLite)

You are given two tables:

- `customers(id, name)`
- `orders(id, customer_id, amount)`

Write SQL that creates a VIEW named `result` with these columns:

- `customer_id`
- `name`
- `total_spend`

Rules:
- `total_spend` is the SUM of `orders.amount` per customer
- Include only customers who have at least 1 order
- Sort by `total_spend` DESC, then `customer_id` ASC

Your submission must be a file named `solution.sql` that contains:

```sql
CREATE VIEW result AS
SELECT ...
;
```
