---
name: migrate-dependency
description: Upgrade, replace, or remove a dependency while controlling compatibility and rollout risk.
---

# Migrate Dependency

1. Pin the current and target versions and read official migration guides, changelogs, release notes, and compatibility policies.
2. Inventory direct usage, transitive exposure, generated files, plugins, configuration, deployment images, and operational assumptions.
3. Record the baseline and add focused coverage for behavior most likely to change. Distinguish pre-existing failures from migration regressions and continue unaffected work when the comparison remains meaningful.
4. Separate mechanical API changes from semantic behavior changes. Migrate in small compilable or runnable steps.
5. Preserve lockfile integrity and avoid unrelated dependency churn. Use the repository's package-manager version and normal resolver; a forced install or ignored compatibility constraint is not evidence that the migration works.
6. Verify build, tests, runtime behavior, data compatibility, performance, and packaging in supported environments.

Document breaking changes, local adaptations, rollout, rollback, and cleanup. Do not rely on compilation alone when the dependency controls runtime semantics.

For upgrades involving a framework/plugin family, distributed package, or persisted data, read [migration compatibility checks](references/compatibility-checks.md). Use the relevant checks without expanding a small dependency bump into a platform rewrite.
