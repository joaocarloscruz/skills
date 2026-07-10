---
name: review-security
description: Review code, architecture, or a change set for concrete security vulnerabilities using threat modeling, trust boundaries, data flow, and exploitability. Use when assessing authentication, authorization, input handling, secrets, cryptography, dependencies, or sensitive data.
---

# Review Security

1. Define assets, actors, entry points, trust boundaries, data sensitivity, and deployment assumptions.
2. Trace untrusted input through parsing, validation, authorization, storage, execution, rendering, and logging.
3. Check identity lifecycle, object-level authorization, tenant isolation, privilege changes, session handling, and fail-open behavior.
4. Inspect injection surfaces, unsafe deserialization, path and URL handling, request forgery, secret exposure, cryptographic misuse, race conditions, and resource exhaustion.
5. Verify defenses in code and configuration; do not infer protection from function names or framework reputation.
6. Assess exploit prerequisites, reachable impact, existing mitigations, and detection.

Report only evidence-backed findings with severity, affected path, attack scenario, impact, and remediation direction. Distinguish vulnerabilities from hardening suggestions. Do not publish exploit details beyond what the user needs to remediate safely.
