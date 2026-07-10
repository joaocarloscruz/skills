---
name: migrate-dependency
description: Upgrade, replace, or remove a library, framework, runtime, SDK, or service dependency while controlling compatibility and rollout risk. Use for dependency migrations, major-version upgrades, deprecated APIs, or vendor replacement.
---

# Migrate Dependency

1. Pin the current and target versions and read official migration guides, changelogs, release notes, and compatibility policies.
2. Inventory direct usage, transitive exposure, generated files, plugins, configuration, deployment images, and operational assumptions.
3. Establish a green baseline and add focused coverage for behavior most likely to change.
4. Separate mechanical API changes from semantic behavior changes. Migrate in small compilable or runnable steps.
5. Preserve lockfile integrity and avoid unrelated dependency churn.
6. Verify build, tests, runtime behavior, data compatibility, performance, and packaging in supported environments.

Document breaking changes, local adaptations, rollout, rollback, and cleanup. Do not rely on compilation alone when the dependency controls runtime semantics.
