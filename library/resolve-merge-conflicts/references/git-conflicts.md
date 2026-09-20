# Git conflict mechanics

Inspect the operation before interpreting either side. These commands assume the
repository root; replace `path/to/file` with an observed repository-relative path.

```text
git status
git diff --name-only --diff-filter=U
git ls-files -u
git show ":1:path/to/file"
git show ":2:path/to/file"
git show ":3:path/to/file"
```

Stage 1 is the merge base, stage 2 is ours, and stage 3 is theirs. Some entries
are absent: add/add can have no stage 1; modify/delete can lack one side. Inspect
the recorded paths for rename conflicts instead of assuming all stages use the
same name. Binary and deletion conflicts may have no markers to search for.

During a normal merge, ours is the checked-out branch and theirs is the branch
being merged. During a rebase, ours is the destination plus commits already
replayed; theirs is the commit currently being replayed from the topic branch.
Use `git rebase --show-current-patch` to inspect that commit. In a cherry-pick,
inspect `CHERRY_PICK_HEAD` alongside the current `HEAD`.

For example, when rebasing `feature` onto `main`, choosing ours for a conflicted
file can discard the feature edit. Stage labels describe the operation, not which
change the user prefers. Reconcile behavior from the actual contents and history.

## Finish the requested operation

After resolving a path, use `git add -- "path/to/file"`; for an intended deletion,
use `git rm -- "path/to/file"`. Avoid staging the whole checkout: unrelated edits
or notes can otherwise enter the integration commit. Inspect changes already in
the index too; targeted staging alone does not exclude previously staged work.
If unrelated staged work would be committed, preserve it before proceeding and
ask only when its ownership or intended handling cannot be determined.

Check `git diff --cached`, `git diff --cached --check`, and `git ls-files -u`.
The last command must have no entries before continuation; its successful exit
code alone does not mean all conflicts were resolved. Whitespace and marker
checks do not prove semantic correctness; run the relevant behavior checks.

Use the continuation command for the observed operation: `git merge --continue`,
`git rebase --continue`, or `git cherry-pick --continue`. A sequence can stop again;
inspect the new state and resolve each remaining conflict. Do not use `--skip`
as a generic recovery command: it drops the current patch. Use it only when the
patch is proven redundant or its omission is part of the user's intended result.
Respect an explicit request to abort or leave the operation unfinished. Finishing
a local integration does not itself authorize a remote push or history rewrite.

## Primary references

- [Git checkout: index stages and rebase side names](https://git-scm.com/docs/git-checkout#Documentation/git-checkout.txt---ours)
- [Git ls-files: unmerged entries](https://git-scm.com/docs/git-ls-files#Documentation/git-ls-files.txt---unmerged)
- [Git rebase: conflict recovery and continuation](https://git-scm.com/docs/git-rebase)
- [Git cherry-pick: sequencer subcommands](https://git-scm.com/docs/git-cherry-pick#_sequencer_subcommands)
