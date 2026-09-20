# MCP contracts that agents can use

Use after choosing the actual client, SDK version, transport, and negotiated protocol. The field names below refer to MCP specification 2025-11-25; verify differences for another version rather than inventing SDK calls.

## Validate the boundary

- Validate arguments against the declared schema and business constraints. Tool annotations describe expected behavior; they do not enforce permissions or make an implementation read-only.
- When declaring `outputSchema`, return matching `structuredContent`. Check the client's compatibility needs for a serialized JSON text block as well. Do not return prose where the schema promises a typed object.
- Separate malformed protocol envelopes or unknown tools from tool-level validation, API, or business failures. Under this specification, invalid tool values such as an out-of-range date are tool execution errors even when no side effect ran. Use `isError: true` with corrective feedback without disclosing secrets or backend internals.
- A stdio server must keep protocol output on stdout and diagnostics elsewhere. Verify process startup/shutdown as well as a successful call.
- For HTTP transport, validate authorization for the operation and resource. Do not accept arbitrary tokens for a downstream service or pass them through as a shortcut; validate intended audience and use the specified authorization flow.
- Bound page size, result size, runtime, retries, and concurrency. Keep pagination cursors scoped to the query/principal and define what happens if the collection changes.

## Exercise lifecycle and interrupted work

Test initialization, version negotiation, the initialized notification, and a client missing optional capabilities. Use only negotiated capabilities; a successful direct handler call does not establish a working MCP connection. Keep a total request deadline even if progress notifications arrive.

For ordinary request cancellation, propagate cancellation to cancellable downstream work and release resources. Exercise a completion/cancellation race: a cancellation notification is not proof that an external write was rolled back. Preserve operation IDs for reconciliation. Task-augmented requests use `tasks/cancel` under this protocol version; do not substitute ordinary request cancellation or invent support when tasks were not negotiated.

For HTTP reconnects or stdio process restarts, verify which application operations can resume or be reconciled. Protocol request IDs identify messages, not durable business idempotency keys.

## Make failures actionable

For a conflict, return a stable object identifier and a safe next read or retry direction. For an ambiguous name, provide bounded candidates with distinguishing fields. For a permission failure, state the missing capability without exposing the protected resource's contents. A timeout after a write needs reconciliation, not an automatic duplicate write.

Example application-level contract, independent of SDK syntax:

```json
{
  "status": "conflict",
  "record_id": "fixture-17",
  "reason": "version_changed",
  "next_action": "read_current_version"
}
```

Whether this is an execution error or a modeled successful result depends on the published tool contract; keep the schema and `isError` behavior consistent across tools.

## Evaluate outcomes, not tool-name recall

Create a resettable fixture with several similarly named records and at least one inaccessible record. Ask an agent to find the right record, perform an authorized change, and verify the final state. Score:

1. Correct final object and values against an independent fixture oracle.
2. No unauthorized reads/writes or duplicate effects.
3. Recovery from empty pages, ambiguous names, stale versions, and transient failures.
4. Bounded calls, latency, and output volume alongside task success.

Keep the prompt, fixture, model, tool revision, and run settings fixed when comparing tool names or schemas. Inspect trajectories to distinguish poor discovery, wrong arguments, server defects, and misleading outputs. A protocol validator passing is necessary interoperability evidence, not proof of task success.

## Primary references

- [MCP 2025-11-25: tool schemas, results, and errors](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)
- [MCP 2025-11-25: transport rules](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports)
- [MCP 2025-11-25: security practices](https://modelcontextprotocol.io/specification/2025-11-25/basic/security_best_practices)
- [MCP 2025-11-25: authorization](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization)
- [MCP 2025-11-25: initialization, capabilities, and timeouts](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle)
- [MCP 2025-11-25: cancellation and races](https://modelcontextprotocol.io/specification/2025-11-25/basic/utilities/cancellation)
