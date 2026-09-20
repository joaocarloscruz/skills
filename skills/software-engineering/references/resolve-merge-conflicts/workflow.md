<!-- Generated from library/resolve-merge-conflicts/SKILL.md; do not edit. -->

# Resolve Merge Conflicts

1. Inspect repository status, staged and unstaged changes, and the active merge, rebase, or cherry-pick. Record unrelated work to preserve. Use `git ls-files -u` to identify unmerged entries, including conflicts without text markers.
2. Read [Git conflict mechanics](references/git-conflicts.md) when identifying index stages, handling rebase side names, or completing the operation. Determine which commits each side represents before selecting any content.
3. Read the commits and surrounding code from both sides before editing. Conflict markers show text overlap, not intended behavior.
4. Classify each conflict as independent additions, competing edits, move-versus-edit, delete-versus-edit, generated output, or semantic incompatibility.
5. Construct the smallest result that preserves compatible intentions and follows the current architecture. Regenerate lockfiles and other generated output with the repository's tools after reconciling their source inputs.
6. Search for duplicated definitions, stale references, and remaining conflict markers. Run focused tests for both sides' behaviors, then broader relevant checks; distinguish baseline failures from integration regressions.
7. Stage only resolved paths, inspect the staged diff, and confirm the unmerged index is empty. Complete the active operation when the user's scope includes it; if explicitly asked to leave resolutions uncommitted, stop at that boundary. Recheck each subsequent conflict during a rebase or cherry-pick sequence.
8. Confirm final status, whether the operation finished, checks run, preserved unrelated work, and any intent that could not be reconciled confidently.

Do not choose "ours" or "theirs" wholesale unless evidence shows the other side is intentionally obsolete.
