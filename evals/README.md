# Behavioral evaluations

`tests/` checks repository code and declared routing fixtures. It does not run an agent. This directory contains starter task briefs and [three executable smoke fixtures](smoke/README.md) for actual behavior comparisons. The fixture code is not itself an executed agent result or a benchmark leaderboard.

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

The broader briefs require project-specific fixtures before execution. The bundled smoke suite supplies three small resettable tasks, not this whole task population. A useful development pilot has multiple task instances and repetitions, plus a held-out decision set. Calibration and sufficient task diversity matter more than a magic sample count.

Result JSON schema version 2 uses one common `experiment` configuration, named `conditions`, a `planned_tasks` list frozen before execution, and complete `task_id`/`repeat` pairs. Each result points to an existing artifact. The recorded plan catches cases omitted from every condition; legacy version 1 inputs remain supported with a coverage warning. Compare with:

```text
python library/evaluate-ai-output/scripts/compare_runs.py evals/runs/results.json --baseline no-skill --candidate candidate --output evals/runs/comparison.json
```

For three conditions, invoke the same command again using the existing-skill condition as baseline. The script performs no model calls and never runs an artifact. Synthetic tests exercise this tooling in CI; they do not promote skill evidence.

## Recording reviewed evidence

The registry uses schema version 2. Defaults remain `unvalidated`. A leaf may add `behavioral_evidence: smoke-tested` or `paired-evaluated` only with `evaluations` entries such as `{"path":"evidence/runs/study/results.json","condition":"candidate"}`. The referenced file must be a valid behavioral experiment with real artifacts and exact Git or `sha256:` package revisions. The validator rejects synthetic evidence, missing files and unsupported claims.

Those states mean an experiment was performed, not that the current skill is superior. If the package changes, retain the evaluated revision and rerun relevant tasks before applying the old conclusion to new code. Record limitations and the isolation procedure in the experiment artifact; a schema validator cannot establish their truth.

## Metadata-selection smoke

Export catalog metadata and opaque request IDs without the expected answers:

```text
python evals/routing.py prepare > routing-input.json
python evals/routing.py score routing-answer.json > routing-score.json
```

Give only the exported input to a fresh model context. It must return the two
revision fields and one selection for every case, including no-match requests.
The scorer rejects missing cells, duplicates, unknown labels and snapshot drift;
it then reports exact router/workflow-set agreement with the declared fixtures.
Save the input, raw response and scores. Run against the same repository snapshot
when reproducing a score. Do not overwrite the first response after feedback.

This batch exercise cannot measure whether a client discovers, loads or follows
a router. Review disagreements before changing descriptions: composed requests
can have overlapping sufficient workflows. A model selection score alone does
not prove that the resulting task would fail. Use actual runtime traces and
held-out prompts for stronger activation claims.

See [the recorded development smoke](../evidence/runs/2026-09-20-development/README.md)
for raw selection and behavior results, including disagreements and limitations.
