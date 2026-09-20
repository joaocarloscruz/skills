# Contract edge cases

Use for externally consumed HTTP contracts or changes whose retry and evolution
semantics need concrete examples. Match the service's existing conventions.

## Ambiguous mutation outcomes

A timeout does not establish that a mutation failed. Define how a caller discovers
its outcome before retrying a non-idempotent operation. For an idempotency-key
contract, specify caller/tenant scope, request identity, retention, concurrent
duplicates, and whether a repeated key with different input is rejected. These
are application decisions, not behavior supplied by an HTTP header name alone.

Idempotency concerns repeated effects, not identical responses. In HTTP, only
retry a non-idempotent operation automatically when its specific semantics or
evidence about the original attempt make that safe. Specify retryable conditions
and limits; do not make every error retryable.

For concurrent edits, state whether last-write-wins is acceptable. Otherwise use
the service's conditional-write mechanism. HTTP `If-Match` with an entity tag can
reject a stale edit; define the precondition-failure recovery path rather than
silently overwriting newer data.

Example cases worth putting in the contract:

- A create succeeds but its response is lost; retry does not create a second object.
- Two submissions reuse the same key with different payloads; the outcome is defined.
- Two editors update one revision; the losing editor can recover their input.

## Evolution and collections

Specify omitted, `null`, empty, and explicit default values separately when they
have different meanings. For partial updates, show how to leave, clear, or reset
a field. Preserve old request behavior when adding an optional field. Check
generated clients as well as wire compatibility; adding a response enum value
can expose clients that assume their switch is exhaustive.

For collections, define a stable order with a tie-breaker, page limits, cursor
scope/expiry if relevant, and the behavior under insertions or deletions between
pages. State whether traversal is a snapshot or may miss/repeat changed items.
Treat cursors as navigation state, not authorization: each page still needs the
caller's current access checks. Retrofitting a default page limit can silently
truncate results for callers that previously received every item.

Provide old-request/new-server examples and a representative old-client check
when changing a published API. A schema diff alone cannot establish semantic
compatibility. Google AIP conventions are useful comparison points, not universal
requirements for every API.

## Primary references

- [HTTP semantics: idempotent methods](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2.2)
- [HTTP semantics: If-Match](https://www.rfc-editor.org/rfc/rfc9110.html#section-13.1.1)
- [Google AIP-180: backwards compatibility](https://google.aip.dev/180)
