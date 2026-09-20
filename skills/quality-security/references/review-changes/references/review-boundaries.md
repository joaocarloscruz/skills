# Choose a review boundary

Resolve placeholders to observed refs or full commit IDs. Record the resolved pair so findings remain attributable if a branch moves during review.

| Requested scope | Comparison |
| --- | --- |
| Contribution on a branch | `git diff BASE...HEAD` compares the merge base with the head |
| Exact before/after snapshots | `git diff OLD NEW` compares those trees directly |
| One ordinary commit | `git diff COMMIT^ COMMIT` compares its parent and result |
| Staged changes | `git diff --cached` compares the index with HEAD |
| Unstaged tracked changes | `git diff` compares the working tree with the index |
| All current tracked changes | `git diff HEAD` compares the working tree with HEAD |

Also inspect `git status --short` for untracked files when local work is in scope; a tracked diff does not include their contents. Do not stage them just to make them visible. For a root commit, use an empty-tree comparison rather than assuming a parent exists. For a merge commit, identify the intended parent or integration comparison explicitly; a combined diff can omit changes visible against only one parent.

## Make findings checkable

Trace a concrete input and its observable consequence through the changed contract. A useful finding establishes the triggering condition, affected caller or user, failed invariant, and missing guard. Verify against the base when the defect's origin is unclear. If a focused reproduction is practical, use disposable fixtures and record the revision and command; do not imply tests ran when the result is based only on inspection.

Choose severity from reachable impact and likely conditions, not from the general danger of a function name. Consolidate repeated manifestations of one root cause unless they need different fixes. Attach the finding to the narrowest changed location that explains the defect, while citing unchanged downstream behavior in the explanation.

Before delivery, check whether head or local files changed during review. Recheck affected findings and line locations when they did; identify any unreviewed revision rather than silently claiming coverage.

## Primary references

- [Git: diff endpoints, merge bases, index, and working tree](https://git-scm.com/docs/git-diff)
- [Git: status and untracked paths](https://git-scm.com/docs/git-status)
