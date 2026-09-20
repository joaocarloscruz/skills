# Measure the same workload before and after

Use when load generation, caching, warm-up, or run variance can change the conclusion.

## Match offered load to the question

A fixed number of clients that wait for responses produces a closed load model: when the service slows, those clients send less traffic. That is suitable for some fixed-concurrency questions but can hide overload when arrivals should continue independently. For a fixed arrival-rate question, use an open model and record offered, started, completed, failed, timed-out, and dropped work. Check whether the load generator itself saturated. See [k6 open and closed models](https://grafana.com/docs/k6/latest/using-k6/scenarios/concepts/open-vs-closed/).

Example: lower p99 with half the original offered load is not evidence that an optimization handles the original demand. Likewise, dropping slow requests from the latency sample can improve p99 while making the user experience worse. Report errors, throughput, queueing, and timeout policy alongside latency.

## Keep comparison conditions visible

Record the revision, build mode, dataset shape, concurrency or arrival schedule, hardware limits, runtime version, and cache state. Exercise representative key popularity and data sizes; repeating one hot key can hide cache-miss or eviction costs. Measure cold startup separately when it matters instead of removing it through warm-up.

Repeat baseline and candidate runs under comparable conditions, interleaving or randomizing order where useful to reduce time-dependent bias. Preserve per-run results and show their spread, not only the fastest run. For microbenchmarks, ensure the compiler cannot remove the measured work and use the appropriate wall or CPU timer. See [Google Benchmark's timing, repetition, and optimization guidance](https://google.github.io/benchmark/user_guide.html).

Recheck output equivalence and the end-to-end metric after the local optimization. A faster function may not improve a request dominated by network waits, and a cache can trade latency for unacceptable memory or stale results. If the observed change is within run variance, report the result as inconclusive rather than selecting a favorable sample.
