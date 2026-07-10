---
name: plan-implementation
description: Plan a codebase change with affected components, ordered edits, tests, risks, and decisions.
---

# Plan Implementation

1. Clarify the desired behavior, acceptance criteria, constraints, and exclusions.
2. Read repository guidance and trace the current execution path through concrete files and symbols.
3. Identify existing patterns to extend, affected contracts, data changes, compatibility needs, and operational consequences.
4. Resolve discoverable questions from code and documentation; ask only for decisions that materially alter the solution.
5. Sequence changes into coherent, verifiable steps. Name likely files or components without pretending uncertain paths are facts.
6. Include tests, migration, observability, rollout, rollback, and documentation where they are actually required.

Lead with the recommended approach and its tradeoffs. End with open questions and risks. Do not implement changes during a planning-only request.
