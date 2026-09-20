---
name: break-down-work
description: Break approved work into ordered tasks with dependencies, acceptance criteria, and verification.
---

# Break Down Work

1. State the outcome, user-visible behavior, constraints, and non-goals.
2. Inspect the relevant system enough to anchor tasks in real components and existing conventions.
3. Split by independently verifiable behavior, not by generic layers such as "backend" and "frontend."
4. Order prerequisites first and identify tasks that can proceed independently. Resolve dependency cycles by defining a contract or combining inseparable work before assigning parallel tasks.
5. Keep each item small enough for one focused change and one clear review.

For every item, include purpose, concrete scope, dependencies, acceptance criteria, and the command or observation that verifies completion. Include the tests and documentation needed to finish that behavior in its task; avoid declaring implementation done while verification is deferred to an unrelated final ticket. Add discovery tasks only where uncertainty cannot be resolved now. Avoid duplicating requirements across tickets; give each requirement one owner.
