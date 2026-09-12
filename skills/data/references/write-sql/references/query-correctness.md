# Query correctness before speed

Use for read-only SQL with joins, aggregates, missing records, time boundaries, or plan analysis. Confirm the dialect and substitute actual schema names; the examples below are illustrative PostgreSQL syntax.

## Make grain visible

Suppose the output is one row per customer and orders contain one row per order. Aggregate orders to customer grain before joining other one-to-many relations:

```sql
WITH totals AS (
  SELECT customer_id, SUM(amount) AS amount
  FROM orders
  WHERE created_at >= $1 AND created_at < $2
  GROUP BY customer_id
)
SELECT c.id, COALESCE(t.amount, 0) AS amount
FROM customers AS c
LEFT JOIN totals AS t ON t.customer_id = c.id;
```

This example assumes amount is additive in a common currency and that missing orders should mean zero; confirm both. Joining order lines and payments directly before summing can multiply each amount. `DISTINCT` is not a general repair for that error.

Record input counts and key uniqueness, then check the output grain and a reconciliation total. A filter on the nullable side in `WHERE` can turn a left join into inner-join behavior; place it in the join or prefiltered relation when unmatched rows must survive.

## Check the adversarial rows

| Case | Question or check |
| --- | --- |
| Right-hand subquery contains NULL | `NOT IN` can become unknown. For absence, use a correlated `NOT EXISTS` when that expresses the contract, and define how NULL keys should match. |
| No qualifying rows | PostgreSQL `SUM` returns NULL while `COUNT` returns zero; coalesce only if zero is the intended meaning. |
| Outer-joined row has no match | `COUNT(*)` counts the preserved row; `COUNT(child.id)` counts non-NULL child identifiers. |
| Equal sort values | Add a stable tie-breaker for pagination, latest-record selection, and deterministic window results. |
| Ratio with integer inputs | Choose numeric division and define a zero-denominator result; do not silently discard the rows. |
| A local calendar day spans a DST change | Compute the interval's local boundaries in the named zone and convert each boundary to instants; do not assume every day lasts 24 hours. |

Prefer half-open time ranges (`>= start`, `< next_start`) for adjacent windows. Bind parameters with the intended timestamp type and zone semantics instead of relying on session defaults or formatted strings.

## Inspect cost without changing the task

Plain `EXPLAIN` estimates a plan; `EXPLAIN ANALYZE` executes the statement. Inspect writable CTEs and called functions before running either through a supposedly read-only workflow; even `SELECT` can invoke side-effecting functions. A read-only database role/transaction is useful defense, not a substitute for inspecting the query or controlling external function effects.

For authorized execution, bound runtime and output. `LIMIT` may reduce returned rows without avoiding an upstream sort, aggregation, or full scan. Compare estimated versus actual rows and loops only when execution is appropriate; measure with representative parameters and current statistics before claiming an improvement.

## Primary references

- [PostgreSQL: subquery expressions and NULL behavior](https://www.postgresql.org/docs/current/functions-subquery.html)
- [PostgreSQL: aggregate behavior](https://www.postgresql.org/docs/current/functions-aggregate.html)
- [PostgreSQL: EXPLAIN and execution effects](https://www.postgresql.org/docs/current/using-explain.html)
- [PostgreSQL: date/time functions](https://www.postgresql.org/docs/current/functions-datetime.html)
