---
name: improve-performance
description: Diagnose and improve latency, throughput, memory, CPU, I/O, query, bundle, or startup performance using reproducible measurements and profiling. Use when software is slow, resource-heavy, regressed, or must meet a performance target.
---

# Improve Performance

1. Define the workload, environment, metric, percentile, budget, and acceptable tradeoffs.
2. Build a repeatable benchmark that captures the user's real bottleneck; warm up runtimes and control noise.
3. Measure a baseline and profile before changing code. Attribute time or allocation to concrete call paths, queries, payloads, or waits.
4. Rank bottlenecks by expected impact and test one intervention at a time.
5. Guard correctness while optimizing; watch tail latency, memory, cache behavior, cold starts, and downstream load.
6. Repeat enough samples to distinguish signal from variance and compare against the same baseline conditions.

Report before and after measurements, methodology, profile evidence, tradeoffs, and regression protection. Reject optimizations that move cost elsewhere without improving the stated target.
