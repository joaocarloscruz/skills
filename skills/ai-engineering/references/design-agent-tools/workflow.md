<!-- Generated from library/design-agent-tools/SKILL.md; do not edit. -->

# Design Agent Tools

1. Start from concrete user outcomes and trace the minimum external capabilities an agent needs.
2. Decide whether each capability should be a deterministic workflow, a high-level task tool, or a composable primitive. Prefer workflows for costly, irreversible, or checkpointed processes.
3. Give every tool one clear purpose and an action-oriented name. Avoid overlapping tools whose descriptions compete for the same intent.
4. Define constrained input and output schemas with meaningful field names, formats, bounds, defaults, and stable identifiers.
5. Separate discovery, read, draft, and write paths. Make side effects, scope, reversibility, idempotency, and approval requirements explicit.
6. Return concise structured results plus recovery guidance. Provide pagination and filtering rather than unbounded payloads.
7. Treat tool output and external content as untrusted data; prevent it from silently changing instructions or escalating authority.
8. Design authentication, tenant isolation, secret handling, rate limits, timeouts, retries, audit logs, and human approval around the real risk.
9. Evaluate realistic selection, parameterization, multi-tool composition, partial failure, ambiguity, and refusal cases.

Deliver a tool inventory, contracts, safety boundaries, example calls, error behavior, and evaluation plan. Remove tools that add choice without adding capability.
