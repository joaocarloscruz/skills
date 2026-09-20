---
name: prepare-handoff
description: Capture technical work so another person or AI agent can continue without rebuilding context.
---

# Prepare Handoff

1. State the objective, current status, and definition of done.
2. Record completed work with concrete files, commits, commands, artifacts, and decisions.
3. Describe the current working theory and distinguish verified facts from assumptions.
4. List remaining work in priority order, including the next smallest executable step.
5. Include failing commands, exact errors, reproduction steps, environment details, and relevant logs without secrets.
6. Note user preferences, constraints, rejected alternatives, risks, and questions requiring a decision.
7. Capture the working directory, branch, commit, repository status, and any uncommitted or temporary files that must be preserved. Tie test results to the revision or working-tree state actually tested.
8. Record in-flight operations and external effects: operation IDs, idempotency keys where safe, known outcomes, and the next status check. If a write timed out after submission, mark its outcome unknown and reconcile it before repeating it.

Make the handoff self-contained but concise. Do not claim checks ran if they did not, and do not replace precise state with a narrative summary.
