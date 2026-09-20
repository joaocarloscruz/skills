<!-- Generated from library/design-api/SKILL.md; do not edit. -->

# Design API

1. Start from consumers, use cases, trust boundaries, latency needs, and consistency requirements.
2. Define resources or domain operations before selecting transport syntax.
3. Specify inputs, outputs, invariants, validation, authorization, errors, idempotency, pagination, and rate behavior.
4. Model retries, partial failure, timeouts, ordering, concurrency, and duplicate delivery where applicable.
5. Prefer additive evolution, but test compatibility from existing consumers' perspective: new required inputs, response enum values, or changed defaults can still break them. Document deprecation, versioning, and migration.
6. Include observability without exposing secrets or sensitive payloads.
7. Provide representative success, failure, and boundary examples.

Compare meaningful alternatives and explain the chosen tradeoffs. End with a contract precise enough to test independently of its implementation.

For HTTP mutations, retries, pagination, or a published contract change, read [contract edge cases](references/contract-edge-cases.md). Apply only the cases relevant to the interface; do not impose HTTP conventions on RPC, event, or library APIs.
