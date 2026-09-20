# Recovery contracts at each boundary

Use for retryable ingestion, checkpointed processing, streaming aggregates, and backfills. Describe guarantees over the complete source-to-sink path, including external effects.

## Find the crash window

For each stage, record the input identity, durable output, progress checkpoint, and transaction boundary. Rehearse the failure between output persistence and acknowledgement:

| Failure point | Required behavior |
| --- | --- |
| Before the output commits | The input remains replayable. |
| After output commits, before progress commits | A replay preserves the intended result without duplicating effects. |
| After progress commits, before output commits | Prevent this ordering or supply a recovery mechanism; otherwise the record can be lost. |
| Acknowledgement is lost | Inspect or retry using the same operation identity; a new identity can duplicate the effect. |

For example, a consumer writing invoice events into a database can atomically claim a unique source-event ID and write its result in one database transaction, then acknowledge the input. On replay, verify the existing event has the same intended content. A deduplication marker written separately from the effect has its own crash window. Expiring deduplication state earlier than the replay horizon reintroduces duplicates.

Kafka transactions can cover supported Kafka read-process-write paths; an external database or API requires its own coordination or idempotency contract. Do not extend a broker guarantee to an email, payment, or arbitrary sink. See [Kafka delivery semantics](https://kafka.apache.org/41/design/design/#message-delivery-semantics); check deployed broker, client, and connector versions.

## Late data and replay

Specify event time, ingestion time, watermark policy, allowed lateness, and correction behavior separately. A watermark describes processing progress under source assumptions; define what happens to later arrivals. When a window emits again, specify whether its output is a replacement, accumulated total, or delta so consumers do not double count it. See [Beam windows and triggers](https://beam.apache.org/documentation/programming-guide/#windowing).

For a live backfill, freeze a source boundary or versioned snapshot, record the transformation version, and isolate progress from live ingestion. Define how newer writes and deletion records win when histories overlap. Reconcile keys and values in bounded partitions before cutover; equal row counts alone are insufficient. Quarantined records need an owner, reason, retention, and replay procedure, and remain visible in completeness metrics.
