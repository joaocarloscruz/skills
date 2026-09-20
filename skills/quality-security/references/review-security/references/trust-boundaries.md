# Validate a security finding

Use when a review crosses identity, tenant, execution, file, or network boundaries. Match the actual framework/version and deployment configuration. A dangerous-looking function without a reachable untrusted input is a lead, not a demonstrated vulnerability.

## Trace the complete path

For each candidate, record: attacker-controlled source, transformations, security decision, sensitive operation, and resulting impact. Inspect all paths that call a shared helper; one guarded caller does not protect another unguarded caller. Distinguish a code-confirmed path from an exploit reproduced in a sandbox.

For object authorization, build a small matrix with two disposable principals and objects:

| Principal and operation | Contract to check |
| --- | --- |
| Owner reads own object | Allowed result and only permitted fields |
| Same-role user reads another user's object | Denied unless sharing policy allows it |
| User in a different tenant supplies an object ID | Tenant scope enforced server-side |
| Former member uses an old session or link | Current policy and revocation apply |
| User updates an allowed object with privileged fields | Field-level permissions cannot be bypassed |

Random identifiers and hidden UI controls do not establish authorization. Check downloads, search results, counts, exports, caches, and asynchronous jobs as well as direct object endpoints. Denied requests must not have already changed state. These checks develop the application's actual policy rather than assuming every cross-user read is forbidden.

For a queued operation, trace the initiating principal and tenant into the worker, status endpoint, and final artifact. A worker's service credentials must not turn a user-supplied object ID into unrestricted access. Apply the product's revocation policy at execution and retrieval, including old download links. For cached protected data, compare the cache key and hit path with the authorization decision; a correctly guarded database query does not protect a cache hit that bypasses it.

## Match the defense to the sink

- SQL parameters bind values; dynamic identifiers need an allowlist or dialect-aware identifier handling. Escaping for one context is not protection in another.
- Shell commands should separate executable and arguments where possible; inspect argument-option injection and the chosen shell, not only metacharacters.
- File paths need a resolved containment check that accounts for traversal and symlinks where relevant. A string prefix alone does not prove containment.
- For server-side URL fetches, inspect schemes, parsed host/port, DNS results, redirects, and private/link-local destinations. Validation before a redirect is insufficient if the client follows it to an unauthorized target. Prefer an explicit destination policy and network egress controls appropriate to the integration.
- Race-sensitive invariants require an atomic server/database enforcement point; a separate read-then-write permission or balance check may become stale.

Use the smallest harmless fixture that tests the claim within the user's authorized scope. Do not probe unrelated live systems, consume real resources, or expose secrets merely to make a report more convincing.

## Avoid misleading certainty

Report the preconditions and exact missing enforcement point. Separate absence of a desirable hardening layer from bypass of a promised boundary. When runtime configuration is unavailable, state which setting would confirm or defeat the attack path and continue reviewing independent paths.

## Primary references

- [OWASP: authorization checks and policy testing](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
- [OWASP: server-side request forgery prevention](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)
- [OWASP: query parameterization](https://cheatsheetseries.owasp.org/cheatsheets/Query_Parameterization_Cheat_Sheet.html)

This is original review guidance informed by the cited technical references; it is not a conformance checklist or a copied vendor skill.
