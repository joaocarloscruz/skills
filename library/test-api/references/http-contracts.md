# Exercise HTTP contracts

Use for HTTP APIs after identifying a permitted environment, the current contract, and an isolated fixture. Match the installed client/framework APIs; do not add standards-based behavior that the service never promised without identifying it as a contract change.

## Start with one observable operation

Capture the request method, path, relevant headers, sanitized input, response, and resulting state. Use a client that can report status, headers, and body separately; distinguish transport failure from an HTTP error response. Never print authorization headers, session cookies, or sensitive payloads into shared evidence.

| Promised behavior | High-information check |
| --- | --- |
| Role/tenant authorization | Reuse an object identifier with a second isolated principal and verify both denial and absence of side effects |
| Retryable create operation | Repeat the same idempotency key and request; check one committed effect, including concurrent duplicates |
| Idempotency conflict handling | Reuse a key with a different payload and verify the documented conflict or replay policy |
| Optimistic concurrency | Read a version/ETag, perform a competing update, then send the stale precondition; verify it cannot overwrite the winner |
| Cursor pagination | Traverse multiple pages with tied sort values; check no duplicates or omissions under the documented snapshot/consistency model |
| Filtering and ordering | Apply filters before validating page boundaries; assert a deterministic tie-breaker where stable paging is promised |
| Rate limiting | In an isolated bounded test, check the documented signal and retry guidance without flooding a shared service |
| Caching | Check the relevant cache-control and variation behavior across principals and changed representations |

HTTP idempotence concerns the intended effect of repeating a request, not identical status/body on every attempt. Do not assume POST can be retried safely, or that a GET implementation is harmless merely because its method should be safe. After a timeout, the server may have committed; verify through the API's reconciliation or idempotency mechanism before retrying a write.

For asynchronous operations, assert the initial acceptance separately from eventual completion or failure. Poll a documented status resource with a bound and preserve the final state; a successful submission response is not proof of completed work.

## Minimal evidence for a failure

State the precondition, exact request shape, expected contract, actual response/state, and whether retry reproduces it. Record identifiers for disposable fixtures and clean up only data created by the test. Keep external downstream actions stubbed unless those actions are within the authorized integration test.

## Primary references

- [RFC 9110: HTTP semantics, idempotence, and conditional requests](https://www.rfc-editor.org/rfc/rfc9110.html)
- [RFC 9111: HTTP caching](https://www.rfc-editor.org/rfc/rfc9111.html)
- [OpenAPI specification](https://spec.openapis.org/oas/latest.html)

Use the API's own versioned specification to resolve status codes, key lifetimes, pagination consistency, and eventual-consistency guarantees; the protocol standards alone do not define those application contracts.
