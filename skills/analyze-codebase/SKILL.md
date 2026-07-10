---
name: analyze-codebase
description: Map an unfamiliar repository's architecture, entry points, boundaries, data flow, conventions, and change hotspots. Use when onboarding to a codebase, locating where behavior lives, explaining system structure, or identifying the files relevant to a proposed change.
---

# Analyze Codebase

1. Read repository instructions, manifests, top-level directories, and architecture records before following implementation details.
2. Identify runtime entry points, build and test commands, deployment units, persistent stores, external integrations, and generated code.
3. Trace one representative user or system flow end to end. Follow symbols and call sites instead of inferring architecture from filenames alone.
4. Distinguish current behavior from comments, plans, deprecated paths, and dead code.
5. Map ownership boundaries and the contracts between them: inputs, outputs, state, errors, and side effects.
6. Verify important claims against code, configuration, or runnable commands.

Report the smallest useful map: major components, their relationships, the execution path relevant to the question, key conventions, and unresolved uncertainties. Cite concrete file paths and symbols. Do not propose changes unless asked.
