---
name: resolve-merge-conflicts
description: Resolve Git conflicts by reconstructing both sides' intent and verifying the integration.
---

# Resolve Merge Conflicts

1. Inspect repository status and identify the operation, base, ours, theirs, and all conflicted files.
2. Read the commits and surrounding code from both sides before editing. Conflict markers show text overlap, not intended behavior.
3. Classify each conflict as independent additions, competing edits, move-versus-edit, delete-versus-edit, generated output, or semantic incompatibility.
4. Construct the smallest result that preserves compatible intentions and follows the current architecture.
5. Search for duplicated definitions, stale references, conflict markers, and generated files that must be regenerated.
6. Run focused tests for both sides' behaviors, then broader relevant checks.
7. Confirm Git status and summarize any intent that could not be reconciled confidently.

Do not choose "ours" or "theirs" wholesale unless evidence shows the other side is intentionally obsolete.
