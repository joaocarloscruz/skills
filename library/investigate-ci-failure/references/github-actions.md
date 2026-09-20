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

Inspect the checkout step and its resolved revision as well as run metadata. A `pull_request` workflow normally checks out the synthetic merge result; a checkout override may use the contributor's head, and `pull_request_target` runs in the base context. Reproducing only the branch head can miss a failure caused by its combination with the base. Do not change to a more privileged event merely to make secrets available to forked code.

## Separate diagnosis from rerun behavior

- Find the first causal error with surrounding context; a final nonzero exit is often only a wrapper result. Compare environment and resolved dependency versions with the last relevant passing run.
- `--log-failed` can be empty or incomplete while a job is running or when a failure occurs before ordinary steps. Inspect job status, annotations, and available provider logs; do not interpret missing output as a pass.
- Reproduce the nearest command locally with the same inputs where practical. A runner-only failure may require targeted instrumentation; continue source and configuration analysis while that evidence is unavailable.
- Rerunning uses the original run's revision and has side effects and costs. Confirm that the user's requested fix/retest scope includes the selected run, especially if the workflow contains publishing or deployment jobs; prefer a specific validation job when appropriate.
- A passing retry is evidence of intermittency, not evidence that the underlying cause has been fixed. Retain failing seeds, artifacts, and frequency estimates.
- Distinguish a failing check from one that is skipped, cancelled, pending, or absent. Check event/path filters, job conditions, matrix exclusions, concurrency cancellation, and required-check names before changing application code. Preserve the original result when comparing a cache-disabled run; a clean-cache pass is a diagnostic observation, not proof that deleting caches repairs the cause.

## Primary references

- [GitHub CLI: gh run view](https://cli.github.com/manual/gh_run_view)
- [GitHub CLI: gh run list](https://cli.github.com/manual/gh_run_list)
- [GitHub: rerunning workflows and jobs](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs)
- [GitHub: event contexts and pull-request merge checkouts](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#pull_request)
