# Behavioral evaluations

`tests/` checks repository code and declared routing fixtures. It does not run an agent. This directory contains starter task briefs for actual behavior comparisons; they are not executed results or a benchmark leaderboard.

Use the [paired evaluation protocol](../library/evaluate-ai-output/references/paired-evaluation.md) and [comparison script](../library/evaluate-ai-output/scripts/compare_runs.py). Keep raw development runs under ignored `evals/runs/`. Commit reviewed, redacted evidence under `evidence/runs/` only when its artifacts and provenance are complete. Do not include credentials, private code, personal data or grader answers in published transcripts.

For each task, prepare one resettable fixture, pin the model/tools/budget, and run no-skill, existing and candidate conditions in fresh isolated sessions. Give the agent only the request and necessary fixture. Keep grader criteria outside its visible workspace. Capture every trial, including failures. Verify the runner's global-skill isolation rather than assuming a fresh conversation disables installed skills. Run natural activation and forced-loading comparisons separately.

Useful initial task families:

| Task | Agent request and fixture | Grader checks kept outside the agent workspace |
|---|---|---|
| Debugging with incomplete access | A stack trace and small repository; production service unavailable; ask for investigation and any locally verifiable fix | Makes useful local progress, avoids an invented reproduction, reports what remains unverified, does not demand an arbitrary hypothesis count |
| Existing red baseline | Repository with one unrelated known failing test and a behavior-preserving refactor request | Records baseline, preserves behavior, distinguishes new failures and verifies the affected seam |
| SQL grain | Customers, orders and order-items tables; request paid revenue and paid-order count including customers with zero orders | No join multiplication; correct grain and null/zero behavior; second fixture changes cardinalities to catch hardcoding |
| Security diff | A small patch with one reachable missing authorization check and one convincing non-issue | Finds the reachable flaw with evidence, avoids invented exploitability and unrelated hardening noise |
| Browser readiness | Local UI whose requested state arrives after an asynchronous action and which has a long-lived connection | Uses observable state and durable assertions; captures actual behavior; avoids network-idle or fixed-delay assumptions |
| MCP pagination and writes | Fake service with multi-page results, permission denial and a retryable read; one non-idempotent write | Preserves page/filter contracts, enforces authorization, retries safely and does not repeat writes without an idempotency guarantee |

These briefs require project fixtures before execution; they are deliberately not fabricated benchmark results. A useful development pilot has multiple task instances and repetitions, plus a held-out decision set. Calibration and sufficient task diversity matter more than a magic sample count.

Result JSON uses one common `experiment` configuration, named `conditions`, and complete `task_id`/`repeat` pairs. Each result points to an existing artifact. Compare with:

```text
python library/evaluate-ai-output/scripts/compare_runs.py evals/runs/results.json --baseline no-skill --candidate candidate --output evals/runs/comparison.json
```

For three conditions, invoke the same command again using the existing-skill condition as baseline. The script performs no model calls and never runs an artifact. Synthetic tests exercise this tooling in CI; they do not promote skill evidence.

## Recording reviewed evidence

The registry uses schema version 2. Defaults remain `unvalidated`. A leaf may add `behavioral_evidence: smoke-tested` or `paired-evaluated` only with `evaluations` entries such as `{"path":"evidence/runs/study/results.json","condition":"candidate"}`. The referenced file must be a valid behavioral experiment with real artifacts and exact Git or `sha256:` package revisions. The validator rejects synthetic evidence, missing files and unsupported claims.

Those states mean an experiment was performed, not that the current skill is superior. If the package changes, retain the evaluated revision and rerun relevant tasks before applying the old conclusion to new code. Record limitations and the isolation procedure in the experiment artifact; a schema validator cannot establish their truth.
