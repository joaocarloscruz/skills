---
name: add-observability
description: Add logs, metrics, traces, dashboards, alerts, or SLOs to expose system health and failures.
---

# Add Observability

1. Start from critical user journeys, system boundaries, failure modes, and operational decisions; do not instrument everything indiscriminately.
2. Define service-level indicators and objectives where reliability decisions require them.
3. Create structured logs for meaningful state transitions and failures with stable event names and correlation identifiers.
4. Define metrics with clear units, ownership, aggregation, and bounded dimensions. Reject high-cardinality labels such as raw user IDs or URLs.
5. Trace requests and asynchronous work across boundaries, preserving parentage and recording useful events without capturing sensitive payloads.
6. Propagate context through queues, retries, scheduled jobs, and external calls.
7. Redact secrets and personal data, define retention and access, and treat telemetry as production data.
8. Build dashboards around questions and alerts around actionable symptoms. Include runbook links, severity, and ownership.
9. Test instrumentation under success, partial failure, retry, timeout, and overload. Verify telemetry loss does not break the application.

Report the signals added, their semantics, sampling and cardinality choices, dashboards and alerts, privacy controls, and known blind spots.
