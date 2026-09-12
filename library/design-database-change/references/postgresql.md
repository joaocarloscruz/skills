# PostgreSQL migration decisions

Use for PostgreSQL changes after checking the installed major version, table size, partitioning, replicas, and whether the runner wraps every migration in one transaction. Inspect representative data and active traffic; an empty test database is not a lock or backfill rehearsal.

## Choose a deployable sequence

1. Identify which old and new application versions may run simultaneously, including workers. Add compatible schema before deploying code that uses it.
2. State the invariant that makes cutover safe: for example, no unmapped legacy rows and no newer writes overwritten by the backfill. Counts alone may miss value mismatches.
3. Backfill in bounded transactions using a stable key or explicit work queue. Record progress, retry the same batch safely, and limit load based on latency and replication lag.
4. Verify ongoing writes, nulls, duplicates, and values before switching reads. A backfill must not overwrite a user's newer value with stale source data.
5. Remove compatibility structures only after old code and in-flight jobs can no longer use them. Data deletion may make rollback a restore/replay operation, not a reverse migration.

## Account for locks and transactions

| Operation | Decision to make |
| --- | --- |
| `ALTER TABLE` | Determine the exact subcommand's lock, scan, and rewrite behavior for the installed version. A fast metadata change can still wait behind a long transaction and block later work. |
| `CREATE INDEX CONCURRENTLY` | Schedule outside a transaction block. It permits writes but takes additional work and can wait; inspect failure state before retrying. |
| Concurrent index build fails | Check index validity and definition. An invalid index may remain; a same-name `IF NOT EXISTS` retry does not repair it or verify equivalence. |
| New check or foreign-key constraint | Where supported, consider adding it `NOT VALID`, then validating existing rows separately. New/changed rows are still checked after addition; validation is not optional completion work. |
| Column default or type conversion | Check whether the exact expression or cast rewrites stored rows; avoid assuming all defaults or casts are metadata-only. |

Use session/transaction-scoped timeouts appropriate to the operation. A short lock timeout can limit a blocked DDL attempt; a statement timeout bounds execution too. Rehearse retries and recovery rather than globally changing production settings.

For a unique constraint, define how nulls and existing duplicates should behave before creating the index. Options such as `NULLS NOT DISTINCT` require a supporting version; partitioned tables add constraints of their own. Verify the index covers the intended rows and is valid before depending on it.

## Evidence to deliver

- Migration order and runner settings, including statements that cannot be transaction-wrapped.
- Representative before/after invariants, expected lock exposure, and a bounded backfill/checkpoint design.
- Measured rehearsal results when available; otherwise name the untested size, traffic, or replication assumption.
- Stop signals, failed-step recovery, and the last point where application rollback remains compatible.

Designing a migration does not itself authorize executing it against a database. Use the environment and execution scope already authorized by the user.

## Primary references

- [PostgreSQL: CREATE INDEX, especially concurrent builds](https://www.postgresql.org/docs/current/sql-createindex.html)
- [PostgreSQL: ALTER TABLE](https://www.postgresql.org/docs/current/sql-altertable.html)
- [PostgreSQL: lock and statement timeouts](https://www.postgresql.org/docs/current/runtime-config-client.html)

The `current` links move with PostgreSQL releases; select the installed version in the documentation before deriving an execution plan.
