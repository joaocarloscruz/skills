---
name: software-engineering
description: Route domain modeling, APIs, database changes, implementation, TDD, migrations, refactoring, or Git conflicts.
---

# Software Engineering

1. Match the request to the most specific workflow below.
2. Read that workflow's referenced file completely before acting.
3. Use multiple workflows only when the request genuinely spans them; apply them in dependency order.
4. If no workflow fits, explain the gap instead of stretching an unrelated workflow.

| Request | Workflow |
| --- | --- |
| Design coherent, evolvable interfaces. | [design-api](references/design-api/workflow.md) |
| Plan safe schemas, migrations, and rollbacks. | [design-database-change](references/design-database-change/workflow.md) |
| Clarify domain language, rules, lifecycles, and boundaries. | [domain-modeling](references/domain-modeling/workflow.md) |
| Implement scoped behavior with verification. | [implement-feature](references/implement-feature/workflow.md) |
| Upgrade dependencies with controlled compatibility. | [migrate-dependency](references/migrate-dependency/workflow.md) |
| Improve structure while preserving behavior. | [refactor-safely](references/refactor-safely/workflow.md) |
| Reconcile competing changes by intent. | [resolve-merge-conflicts](references/resolve-merge-conflicts/workflow.md) |
| Build behavior in small red-green-refactor cycles. | [tdd](references/tdd/workflow.md) |

Follow the selected workflow as binding process guidance. Preserve user authority and repository instructions when they are more specific.
