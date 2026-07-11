---
name: design-database-change
description: Design safe database changes, migrations, backfills, indexes, compatibility windows, and rollback.
---

# Design Database Change

1. Record the current schema, data volume, access patterns, invariants, retention rules, and deployment topology.
2. Separate schema evolution from data backfill and application cutover.
3. Prefer expand-and-contract: add compatible structures, dual-read or dual-write only when justified, backfill in bounded batches, verify, switch reads, then remove old structures later.
4. Assess locks, index build behavior, replication lag, transaction size, hot rows, and failure recovery.
5. Define checkpoints and measurable invariants for row counts, nulls, duplicates, checksums, and application behavior.
6. Make rollback explicit; distinguish reversible schema steps from irreversible data transformations.

Deliver ordered migration and deployment steps, compatibility requirements, monitoring, stop conditions, rollback, and cleanup. Never assume a migration is safe solely because it succeeds on an empty database.
