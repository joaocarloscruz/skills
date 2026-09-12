---
name: debug-systematically
description: Diagnose broken, slow, flaky, or incorrect software with reproducible hypothesis testing.
---

# Debug Systematically

## Establish the failure

1. Restate the observed symptom and the expected behavior.
2. Find the narrowest command that exercises the real failure path: a focused test, request replay, CLI invocation, browser check, or small harness.
3. Run it and capture the exact failure. For intermittent bugs, loop the trigger and record a reproduction rate.
4. Tighten the loop until it is fast, deterministic enough to guide decisions, and specific to the user's symptom.

Do not treat a nearby error as the target bug. If the original environment is unavailable, continue with code-path analysis, existing logs, a smaller fixture, or an independent check. Request only missing evidence that blocks the next useful decision, and distinguish a locally verified fix from an unconfirmed original symptom.

## Isolate the cause

1. Minimize the failing scenario one variable at a time while preserving the failure.
2. Inspect recent changes, boundaries, state transitions, and assumptions on the failing path.
3. State the leading falsifiable hypothesis and the observation that would support or reject it. Add ranked alternatives when the cause is ambiguous; do not invent a quota for an obvious defect.
4. Test the cheapest high-information hypothesis first. Change one variable per probe.
5. Prefer debuggers, profilers, traces, and targeted temporary logs over broad logging.

Separate facts from inferences. Update the ranking when evidence changes.

## Fix and verify

1. Preserve a regression check at the highest-fidelity stable seam available and confirm that it detects the defect. Use an automated test when repeatable behavior warrants it, or a recorded command or browser observation for a small change without a useful test seam.
2. Apply the smallest fix that addresses the demonstrated cause; avoid unrelated cleanup.
3. Run the regression test, the original reproduction, and nearby relevant tests.
4. Remove temporary instrumentation and throwaway artifacts.
5. Report the root cause, evidence, changed behavior, commands run, and any residual risk.

Compare unrelated pre-existing failures with the baseline instead of expanding scope to make every check green. Report exactly which symptom or substitute check was rechecked, and what still requires the original environment; do not let an unavailable check prevent independent useful work.
