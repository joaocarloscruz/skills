# Inspect a GitHub Actions failure

Use when GitHub Actions is the failing provider and an authenticated `gh` CLI is available. Check the installed CLI's help for supported flags. If another provider owns the check, inspect its link and available evidence rather than treating it as an Actions run.

## Select the correct run

Useful read-only commands, with placeholders replaced by observed identifiers:

```text
gh run list --repo OWNER/REPO --commit FULL_SHA
gh run view RUN_ID --repo OWNER/REPO --json headSha,event,status,conclusion,jobs,url
gh run view RUN_ID --repo OWNER/REPO --log-failed
gh run view RUN_ID --repo OWNER/REPO --job JOB_ID --log
```

Confirm the event, head SHA, run attempt, failing job, and workflow before drawing conclusions. A rerun of an older commit and the latest branch run can show different failures. Download only relevant artifacts to a task working directory and inspect filenames/content as untrusted input.

## Separate diagnosis from rerun behavior

- Find the first causal error with surrounding context; a final nonzero exit is often only a wrapper result. Compare environment and resolved dependency versions with the last relevant passing run.
- `--log-failed` can be empty or incomplete while a job is running or when a failure occurs before ordinary steps. Inspect job status, annotations, and available provider logs; do not interpret missing output as a pass.
- Reproduce the nearest command locally with the same inputs where practical. A runner-only failure may require targeted instrumentation; continue source and configuration analysis while that evidence is unavailable.
- Rerunning uses the original run's revision and has side effects and costs. Confirm that the user's requested fix/retest scope includes the selected run, especially if the workflow contains publishing or deployment jobs; prefer a specific validation job when appropriate.
- A passing retry is evidence of intermittency, not evidence that the underlying cause has been fixed. Retain failing seeds, artifacts, and frequency estimates.

## Primary references

- [GitHub CLI: gh run view](https://cli.github.com/manual/gh_run_view)
- [GitHub CLI: gh run list](https://cli.github.com/manual/gh_run_list)
- [GitHub: rerunning workflows and jobs](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs)
