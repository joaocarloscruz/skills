---
name: investigate-ci-failure
description: Diagnose failing continuous-integration jobs by locating the first actionable error, reproducing it locally when possible, distinguishing code defects from flaky or environmental failures, and proposing a verified fix. Use when builds, tests, checks, or pipelines fail.
---

# Investigate CI Failure

1. Identify the failing workflow, job, step, revision, runner environment, and whether earlier jobs failed first.
2. Read the complete relevant log around the first causal error; later failures are often consequences.
3. Compare with the last successful run and inspect changes to code, dependencies, caches, secrets, images, and workflow configuration.
4. Classify the failure as deterministic code, test flake, infrastructure, configuration, resource limit, or external dependency.
5. Reproduce with the closest available command and environment. For flakes, estimate frequency and preserve seeds, timing, and artifacts.
6. Make the smallest justified fix and rerun the exact failing check plus nearby checks.

Report evidence, root cause confidence, reproduction, proposed or applied fix, and residual uncertainty. Never "fix" a flaky test by weakening its assertion without demonstrating why the assertion was wrong.
