---
name: tdd
description: Build behavior test-first in small red-green-refactor cycles at stable seams.
---

# Test-Driven Development

1. Translate the requested behavior into one observable example. Resolve ambiguity from the contract and existing behavior; ask only when a material product decision remains.
2. Choose the narrowest stable seam that proves user-visible behavior without coupling the test to implementation details.
3. Write one test that fails for the intended reason. Confirm it is discovered and its failure is tied to the missing behavior or intended public interface; an unrelated import, fixture, or environment failure is not that evidence. If it starts green, verify whether the behavior already exists or the assertion misses the new requirement; do not break working code to manufacture a red result.
4. Add the smallest production change that makes the test pass. Avoid unrelated cleanup or speculative abstractions.
5. Run the focused test until green, then run nearby tests to catch local regressions.
6. Refactor only while tests remain green. Improve names, duplication, and boundaries without changing behavior.
7. Repeat with the next behavior, boundary, or failure case until the acceptance criteria are covered.

Keep each cycle small enough that a failure has one likely cause. Prefer contract or public-interface assertions over private calls, snapshots, mocks, or tautological expected values. Use mocks only at genuine external boundaries where a real dependency would make the loop slow or nondeterministic.

For bug fixes, first capture the defect with a failing regression test. If the cause is not yet known or reproducible, diagnose it before beginning the red-green loop.

Report the behaviors added, tests that began red, commands run, and any acceptance criteria that remain unproved.
