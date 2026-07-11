---
name: audit-dependencies
description: Audit dependencies for advisories, abandonment, licensing, version drift, and supply-chain risk.
---

# Audit Dependencies

1. Identify every package manager, lockfile, runtime, workspace, image, and vendored dependency in scope.
2. Use lockfile-resolved versions rather than manifest ranges when assessing the installed graph.
3. Run ecosystem-native audit and outdated checks without automatically changing versions.
4. Verify important advisories against authoritative databases and confirm whether the vulnerable code path is reachable.
5. Check maintenance activity, release cadence, license compatibility, unnecessary direct dependencies, duplicate capabilities, and install-time scripts.
6. Separate direct, transitive, development-only, and production exposure.

Prioritize findings by exploitability and operational impact, not raw advisory count. For each action, state the affected dependency, evidence, recommended target, compatibility concerns, and verification plan. Do not upgrade packages unless requested.
