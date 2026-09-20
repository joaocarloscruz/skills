# Intermittent failures and regression searches

Use when a single reproduction does not reliably distinguish a fix from a lucky run.

## Preserve the conditions that make the failure possible

- Record failures and attempts, elapsed time, concurrency, execution order, seed, and relevant environment. Reset persistent state between trials when isolation is the intended contract; retain the failing sequence when investigating a state leak.
- A test that passes alone but fails in a suite suggests an order or shared-state dependency. Minimize the preceding tests or operations while preserving their order before changing production logic.
- Replace guessed sleeps with an observable readiness condition. For a suspected race, use a controlled barrier or injected scheduling seam to reproduce the conflicting interleaving; serializing the whole suite can hide the defect.
- Compare pre-fix and post-fix behavior under the same trigger and budget. Report the counts. Zero failures in a short run does not establish that a rare bug is gone.
- If the instrumented build stops failing, consider whether logging, breakpoints, or timing changes suppress the failure. Prefer a lower-interference trace or state capture.

## Bisect only with a useful classifier

Use a separate worktree when the user's checkout has work to preserve. Confirm both known-good and known-bad endpoints using the same predicate. Keep the harness outside the revisions being checked out and recreate version-appropriate dependencies instead of reusing stale build output.

For `git bisect run`, return `0` for good and a chosen failure code such as `1` for the target defect. Return `125` for an untestable revision, such as an unrelated build failure. Do not let a missing command classify a revision as bad. A flaky predicate can select the wrong commit; stabilize it or preserve uncertainty rather than automating a misleading search. Save `git bisect log`, then end the bisect with `git bisect reset` in the worktree used for the search.

The first failing commit narrows the cause; inspect its behavior and confirm the hypothesis before treating a revert as the complete fix.

## Primary references

- [Git: bisection, exit codes, replay, and reset](https://git-scm.com/docs/git-bisect)
- [Hypothesis: flaky failures and uncontrolled state](https://hypothesis.readthedocs.io/en/latest/tutorial/flaky.html)
