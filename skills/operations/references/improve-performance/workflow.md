<!-- Generated from library/improve-performance/SKILL.md; do not edit. -->

# Improve Performance

1. Define the workload, environment, metric, percentile, budget, and acceptable tradeoffs.
2. Build a repeatable benchmark that captures the user's real bottleneck; distinguish cold-start and steady-state measurements, warming up only where that matches the target.
3. Measure a baseline and profile before changing code. Attribute time or allocation to concrete call paths, queries, payloads, or waits.
4. Rank bottlenecks by expected impact and test one intervention at a time.
5. Guard correctness while optimizing; watch tail latency, memory, cache behavior, cold starts, and downstream load.
6. Repeat enough samples to distinguish signal from variance and compare against the same baseline conditions.

For service load tests or noisy benchmark comparisons, read [measurement validity](references/measurement-validity.md).

Report before and after measurements, methodology, profile evidence, tradeoffs, and regression protection. Reject optimizations that move cost elsewhere without improving the stated target.
