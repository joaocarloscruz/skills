# Signals that survive aggregation and failure

Use when adding service telemetry or alerts. Reuse the installed instrumentation's conventions and version before inventing another metric for the same operation.

## Define what one observation means

Record the measured boundary, unit, eligible population, and outcome. A user request attempted three times is one user outcome and three downstream attempts; do not mix those denominators. Keep deployment/environment identity consistent across logs, metrics, and traces.

- Use counters for event totals and distributions for durations. For Prometheus-style histograms, aggregate compatible buckets before computing a fleet percentile; averaging instance p99 values does not produce a fleet p99. Choose resolution around the latency decision being made. See [Prometheus histogram guidance](https://prometheus.io/docs/practices/histograms/).
- Prefer bounded route templates over raw paths. Estimate the product of label dimensions, including replicas and histogram buckets, before introducing a new series family. Put request identifiers in traces or logs with appropriate access controls.
- Keep availability measurement independent of biased trace sampling. A retained trace is diagnostic evidence, not automatically an unbiased count of requests.
- For a batch with several causal inputs, choose span links when a single parent misrepresents causality. Check the messaging instrumentation's actual context propagation behavior. See [OpenTelemetry messaging spans](https://opentelemetry.io/docs/specs/semconv/messaging/messaging-spans/).

## Alert on a decision

For an SLO, define eligible events and the bad-event fraction first. Burn rate is that fraction divided by the allowed bad-event fraction. Choose windows and paging thresholds from the time available to respond; do not paste example constants into a different SLO. Distinguish a missing series, a zero denominator, and a healthy interval.

Low traffic can make one failure dominate a ratio. Evaluate the cost of that failure and an appropriate observation window or separate synthetic probe; do not dilute real failures by counting synthetic successes as user successes. See [Google SRE on SLO alerts and low traffic](https://sre.google/workbook/alerting-on-slos/).

Verify an alert fires and resolves for representative data, including no traffic and absent telemetry. Interrupt the exporter to check bounded buffering, visible drop signals, and application behavior; flush on shutdown within the process's shutdown budget. Report what the diagnostic signals still cannot see.
