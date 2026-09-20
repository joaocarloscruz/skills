---
name: audit-dependencies
description: Audit dependencies for advisories, abandonment, licensing, version drift, and supply-chain risk.
---

# Audit Dependencies

1. Identify every package manager, lockfile, runtime, workspace, image, and vendored dependency in scope.
2. Use lockfile-resolved versions rather than manifest ranges when assessing the installed graph.
3. Run ecosystem-native audit and outdated checks without automatically changing versions.
4. Verify important advisories against authoritative databases, match the resolved package/version, and investigate reachability. Record unknown reachability as unknown; no observed call path is not proof that runtime loading, plugins, or a build step cannot reach it.
5. Check maintenance activity, release cadence, license compatibility, unnecessary direct dependencies, duplicate capabilities, and install-time scripts.
6. Separate direct, transitive, development-only, and production exposure. Development tools can execute in privileged builds; assess their actual inputs and credentials before reducing priority.

Record scanner/database dates, lockfile revision, excluded ecosystems, and unsupported analysis so a clean report has a defined scope. Group advisory aliases and repeated dependency paths without hiding separately affected versions.

Prioritize findings by exploitability and operational impact, not raw advisory count. For each action, state the affected dependency, path from a direct dependency, evidence, recommended target, compatibility concerns, and verification plan. For a transitive dependency, evaluate updating its owning direct dependency before forcing a potentially incompatible override.

Keep the audit read-only unless remediation is requested. For example, `npm audit fix` performs an install, and `--package-lock-only` still changes the lockfile; neither is a reporting command. Consult the installed ecosystem's documentation, such as [npm audit](https://docs.npmjs.com/cli/v11/commands/npm-audit/) and [OSV call-analysis output](https://google.github.io/osv-scanner/output/), before interpreting scope or executing suggested fixes.
