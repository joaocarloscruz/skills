---
name: release-software
description: Prepare, verify, publish, and monitor a software release with versioning, changelog, artifacts, migrations, rollout, and rollback controls. Use when cutting a release, publishing packages, deploying a version, or assembling release readiness.
---

# Release Software

1. Confirm the target version, channel, source revision, supported environments, and approval authority.
2. Review changes since the previous release and classify user impact, breaking changes, migrations, and security fixes.
3. Verify tests, builds, generated artifacts, dependency locks, signatures, provenance, and packaging from a clean checkout.
4. Write release notes for users: behavior changes, upgrade steps, known issues, and rollback considerations.
5. Sequence irreversible steps last. Define preflight checks, rollout stages, health signals, stop conditions, and rollback.
6. Publish only with explicit authorization and verify the resulting artifact or deployment independently.
7. Monitor critical signals and record final version, commit, artifact, and outcome.

Never infer permission to publish from a request to prepare a release.
