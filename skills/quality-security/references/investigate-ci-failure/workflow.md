<!-- Generated from library/investigate-ci-failure/SKILL.md; do not edit. -->

# Investigate CI Failure

1. Identify the failing workflow, job, step, revision, runner environment, and whether earlier jobs failed first.
2. Read the complete relevant log around the first causal error; later failures are often consequences.
3. Compare with the last successful run and inspect changes to code, dependencies, caches, secrets, images, and workflow configuration.
4. Classify the failure as deterministic code, test flake, infrastructure, configuration, resource limit, or external dependency.
5. Reproduce with the closest available command and environment. For flakes, estimate frequency and preserve seeds, timing, and artifacts.
6. When fixes are in scope, make the smallest justified fix and rerun the exact failing check plus nearby checks. For diagnosis-only work, provide the evidence and next concrete action.

When using GitHub Actions and `gh`, read `references/github-actions.md` for revision selection, logs, and rerun boundaries. If an external provider or unavailable runner blocks reproduction, continue with available source, configuration, and logs; identify the remaining provider-specific verification.

Report evidence, root cause confidence, reproduction, proposed or applied fix, and residual uncertainty. Never "fix" a flaky test by weakening its assertion without demonstrating why the assertion was wrong.
