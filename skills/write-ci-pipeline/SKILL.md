---
name: write-ci-pipeline
description: Create or improve a continuous-integration pipeline that builds, tests, analyzes, and packages changes reproducibly and securely. Use when authoring CI workflows, matrices, caches, artifacts, quality gates, or pull-request checks; deployment belongs in a separately authorized release workflow.
---

# Write CI Pipeline

1. Identify repository commands, supported environments, required services, generated artifacts, and the checks that must block integration.
2. Reproduce important steps locally before encoding them in CI.
3. Use least-privilege tokens and permissions. Keep untrusted pull-request code away from secrets and privileged events.
4. Pin third-party actions, images, tools, and dependency installs to reviewed versions or immutable references according to project policy.
5. Separate setup, fast checks, tests, packaging, and optional analysis into understandable jobs with explicit dependencies.
6. Use matrices only for supported combinations that provide distinct assurance. Fail clearly when required coverage is skipped.
7. Cache immutable or safely keyed inputs; never cache credentials, mutable build outputs, or state that can poison another trust boundary.
8. Bound time, concurrency, retries, logs, and artifact retention. Cancel obsolete runs where safe.
9. Preserve useful failure evidence while redacting secrets. Make job and step names explain what failed.
10. Test the workflow on a representative branch or draft change and verify required-check behavior.

Report triggers, permissions, jobs, matrices, caches, artifacts, expected duration, and validation. Do not add deployment or publishing authority unless the user explicitly requests it.
