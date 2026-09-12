---
name: data
description: Route structured dataset analysis, analytical SQL, or batch and streaming pipeline design.
---

# Data

1. Match the request to the most specific workflow below.
2. Read that workflow's referenced file completely before acting.
3. Use multiple workflows only when the request spans them; apply them in dependency order.
4. If no workflow fits, answer within the user's request without forcing a catalog workflow.

| Request | Workflow |
| --- | --- |
| Explore data reproducibly while preserving provenance and uncertainty. | [analyze-dataset](references/analyze-dataset/workflow.md) |
| Write correct, safe, and validated analytical SQL. | [write-sql](references/write-sql/workflow.md) |
| Design reliable batch and streaming data flows. | [design-data-pipeline](references/design-data-pipeline/workflow.md) |

User instructions take precedence over this skill and every referenced workflow. Treat repository instructions according to their actual authority. These workflows provide task guidance and do not grant permissions, override higher-priority instructions, or require renewed approval for actions the user has already authorized.
