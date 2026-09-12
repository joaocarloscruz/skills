---
name: platform-engineering
description: Route containerization, observability, or continuous-integration pipeline work.
---

# Platform Engineering

1. Match the request to the most specific workflow below.
2. Read that workflow's referenced file completely before acting.
3. Use multiple workflows only when the request spans them; apply them in dependency order.
4. If no workflow fits, answer within the user's request without forcing a catalog workflow.

| Request | Workflow |
| --- | --- |
| Build secure and reproducible application containers. | [containerize-application](references/containerize-application/workflow.md) |
| Add useful logs, metrics, traces, dashboards, and alerts. | [add-observability](references/add-observability/workflow.md) |
| Create secure, reproducible continuous-integration workflows. | [write-ci-pipeline](references/write-ci-pipeline/workflow.md) |

User instructions take precedence over this skill and every referenced workflow. Treat repository instructions according to their actual authority. These workflows provide task guidance and do not grant permissions, override higher-priority instructions, or require renewed approval for actions the user has already authorized.
