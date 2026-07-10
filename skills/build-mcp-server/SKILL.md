---
name: build-mcp-server
description: Design, implement, secure, or evaluate an MCP server exposing a service to AI agents.
---

# Build MCP Server

1. Read the current MCP specification and official SDK documentation for the selected language; confirm versions instead of relying on remembered APIs.
2. Study the target service's authentication, rate limits, pagination, errors, data model, and high-value user workflows.
3. Choose the transport and deployment model from actual client and operational requirements.
4. Design a coherent tool surface:
   - use action-oriented, consistently prefixed names;
   - make input schemas constrained and self-explanatory;
   - return focused structured content with stable identifiers;
   - support filtering and pagination instead of dumping large responses;
   - distinguish read-only, idempotent, destructive, and open-world behavior;
   - provide actionable errors that tell an agent how to recover.
5. Keep credentials server-side, validate every input, enforce authorization per operation, bound resource use, and redact sensitive output and logs.
6. Implement shared API, retry, pagination, error, and response-formatting infrastructure before repeating it across tools.
7. Test protocol behavior, schemas, authentication, failures, timeouts, pagination, concurrency, and representative client connections.
8. Create realistic evaluations that require agents to select and compose tools. Include ambiguous names, empty results, permission failures, and large collections.

Report the supported workflows, tool contracts, security boundaries, commands run, client evidence, and known limitations. Do not claim quality from protocol compliance alone; verify that agents can complete real tasks reliably.
