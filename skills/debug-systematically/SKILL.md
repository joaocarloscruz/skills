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

Do not treat a nearby error as the target bug. If no runnable reproduction is possible, report what evidence is missing and request the smallest useful artifact, such as logs, a trace, fixture data, or environment access.

## Isolate the cause

1. Minimize the failing scenario one variable at a time while preserving the failure.
2. Inspect recent changes, boundaries, state transitions, and assumptions on the failing path.
3. Write three to five ranked, falsifiable hypotheses. For each, state the observation that would support or reject it.
4. Test the cheapest high-information hypothesis first. Change one variable per probe.
5. Prefer debuggers, profilers, traces, and targeted temporary logs over broad logging.

Separate facts from inferences. Update the ranking when evidence changes.

## Fix and verify

1. Add a regression test at the highest-fidelity stable seam available and confirm that it fails for the intended reason.
2. Apply the smallest fix that addresses the demonstrated cause; avoid unrelated cleanup.
3. Run the regression test, the original reproduction, and nearby relevant tests.
4. Remove temporary instrumentation and throwaway artifacts.
5. Report the root cause, evidence, changed behavior, commands run, and any residual risk.

Do not claim success unless the original symptom has been rechecked after the fix.
