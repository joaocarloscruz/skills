---
name: test-api
description: Verify HTTP, RPC, GraphQL, event, or service APIs against their contracts, including authentication, validation, errors, idempotency, pagination, concurrency, and side effects. Use when testing an API implementation or reproducing integration failures.
---

# Test API

1. Obtain the authoritative contract and identify environment, credentials, test data, and destructive operations.
2. Start with one valid request and capture status, headers, body, timing, and side effects.
3. Cover required and optional fields, types, boundaries, invalid values, authorization roles, missing resources, conflicts, and dependency failure.
4. Verify idempotency, retries, pagination, filtering, ordering, rate behavior, and concurrency when promised by the contract.
5. Assert stored state and emitted events, not only response bodies.
6. Keep tests isolated, deterministic, and safe to rerun; clean up created data.

Report contract violations separately from environment or client problems. Preserve minimal request and response evidence with secrets redacted.
