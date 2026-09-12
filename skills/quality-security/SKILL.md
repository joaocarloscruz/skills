---
name: quality-security
description: Route debugging, test strategy, AI evaluation, CI diagnosis, code review, security review, interface testing, or skill-catalog audits.
---

# Quality Security

1. Match the request to the most specific workflow below.
2. Read that workflow's referenced file completely before acting.
3. Use multiple workflows only when the request spans them; apply them in dependency order.
4. If no workflow fits, answer within the user's request without forcing a catalog workflow.

| Request | Workflow |
| --- | --- |
| Audit skill structure, routing, safety, provenance, and maintenance quality. | [audit-skill-catalog](references/audit-skill-catalog/workflow.md) |
| Reproduce, isolate, fix, and verify defects. | [debug-systematically](references/debug-systematically/workflow.md) |
| Select risk-based tests at effective seams. | [design-test-strategy](references/design-test-strategy/workflow.md) |
| Build rigorous evaluations for AI behavior. | [evaluate-ai-output](references/evaluate-ai-output/workflow.md) |
| Trace pipeline failures to root causes. | [investigate-ci-failure](references/investigate-ci-failure/workflow.md) |
| Review diffs for correctness, risk, and scope. | [review-changes](references/review-changes/workflow.md) |
| Threat-model changes and find exploitable risks. | [review-security](references/review-security/workflow.md) |
| Verify contracts, errors, and side effects. | [test-api](references/test-api/workflow.md) |
| Verify command-line behavior and compatibility. | [test-cli](references/test-cli/workflow.md) |

User instructions take precedence over this skill and every referenced workflow. Treat repository instructions according to their actual authority. These workflows provide task guidance and do not grant permissions, override higher-priority instructions, or require renewed approval for actions the user has already authorized.
