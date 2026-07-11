<!-- Generated from library/design-data-pipeline/SKILL.md; do not edit. -->

# Design Data Pipeline

1. Define producers, consumers, business purpose, data sensitivity, volume, velocity, freshness, retention, and service objectives.
2. Specify source and sink contracts: schema, grain, keys, ordering, event time, nullability, compatibility, ownership, and quality expectations.
3. Choose batch, micro-batch, or streaming from latency and correctness needs rather than fashion.
4. Design stages with explicit inputs, outputs, checkpoints, retry boundaries, and deterministic transformations.
5. Make ingestion and writes idempotent. Define deduplication, late and out-of-order data, replay, watermark, and exactly-once assumptions precisely.
6. Plan schema evolution, partitioning, compaction, reprocessing, backfills, and dual-running during migrations.
7. Add quality gates for completeness, uniqueness, validity, referential integrity, distribution shifts, and reconciliation.
8. Preserve lineage and access controls; minimize sensitive data and define deletion and retention propagation.
9. Define metrics, logs, alerts, dashboards, runbooks, ownership, cost controls, and recovery objectives.

Deliver the architecture, contracts, failure model, operational plan, backfill and rollback strategy, and verification criteria. State where data loss, duplication, or staleness can still occur.
