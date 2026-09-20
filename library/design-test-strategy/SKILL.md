---
name: design-test-strategy
description: Design a risk-based mix of unit, integration, contract, end-to-end, performance, and manual tests.
---

# Design Test Strategy

1. Identify critical user journeys, invariants, trust boundaries, dependencies, failure modes, and expensive mistakes.
2. Rank risks by likelihood, impact, and detectability.
3. Choose the lowest-cost test seam that faithfully exercises each risk. Avoid testing implementation details or duplicating the same assurance at every layer.
4. Define fixtures, environment needs, determinism controls, oracles, and cleanup.
5. Cover normal behavior, boundaries, invalid input, partial failure, concurrency, recovery, compatibility, and observability where relevant.
6. Assign non-functional checks only when tied to measurable requirements.

For each critical assertion, name a plausible wrong implementation it would reject. A test that only checks a mocked return value, successful HTTP status, or executed line can miss the promised behavior. Keep one real boundary check where replacing a dependency would otherwise hide serialization, persistence, authorization, or retry defects. Use targeted fault injection or mutation testing when it resolves a specific assurance gap; do not add a universal coverage or mutation-score gate.

For parsers, transformations, serialization, financial arithmetic, or state machines with many input combinations, read `references/property-tests.md`. Use generated tests where a meaningful invariant exists, rather than turning every example test into fuzzing.

Produce a traceable matrix of risk, scenario, test level, assertion, and owner. Call out what remains manual or untested and why. Prefer a small high-signal suite over a large shallow checklist.
