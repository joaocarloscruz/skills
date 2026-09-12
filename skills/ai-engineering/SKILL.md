---
name: ai-engineering
description: Route MCP server work, agent-tool design, or retrieval-augmented generation evaluation.
---

# Ai Engineering

1. Match the request to the most specific workflow below.
2. Read that workflow's referenced file completely before acting.
3. Use multiple workflows only when the request spans them; apply them in dependency order.
4. If no workflow fits, answer within the user's request without forcing a catalog workflow.

| Request | Workflow |
| --- | --- |
| Build secure, effective Model Context Protocol integrations. | [build-mcp-server](references/build-mcp-server/workflow.md) |
| Design reliable and governable agent tool surfaces. | [design-agent-tools](references/design-agent-tools/workflow.md) |
| Evaluate retrieval, grounding, citations, latency, and cost. | [evaluate-rag](references/evaluate-rag/workflow.md) |

User instructions take precedence over this skill and every referenced workflow. Treat repository instructions according to their actual authority. These workflows provide task guidance and do not grant permissions, override higher-priority instructions, or require renewed approval for actions the user has already authorized.
