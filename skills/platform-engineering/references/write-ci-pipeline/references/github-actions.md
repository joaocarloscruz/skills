# GitHub Actions trust and verification

Use for GitHub Actions only. Confirm repository permissions, branch protection/rulesets, runner type, and supported Actions versions before changing the workflow.

## Match authority to code provenance

- Run untrusted contribution code with minimal credentials. `pull_request_target` runs in a privileged base-repository context; checking out and running a contributor's head code there can expose write authority or secrets. Do not use that event simply to make a failing fork workflow work.
- Treat issue titles, branch names, PR bodies, and event fields as untrusted strings. Pass them through an action's structured inputs or a quoted environment variable; do not interpolate them directly into a `run:` script where they become shell source.
- Scope `GITHUB_TOKEN` permissions to needed jobs. When all default permissions are removed, add only the capabilities each job needs.
- Pin third-party actions to reviewed full commit SHAs and record the human-readable version alongside the pin. A pin controls code identity; it does not establish that the code is trustworthy.
- For cloud access, use an appropriately scoped short-lived identity where supported, with audience and repository/ref/environment restrictions. Do not turn a read-only test job into a deployment identity.

These are separate decisions: who may trigger a job, which revision it executes, and which credentials and artifacts it may consume. Verify all three together.

## Make the pipeline's result meaningful

1. Use locked/reproducible installs supported by the project and distinguish dependency caches from executable build artifacts. Include relevant OS, toolchain, and lockfile inputs in keys.
2. Treat restored caches and downloaded artifacts as inputs from their producing trust context. A privileged follow-up job must not execute arbitrary artifacts produced by an untrusted PR.
3. Give required checks stable names. Verify behavior for skipped paths, conditional jobs, failed dependencies, and merge queues where enabled; a workflow file alone does not configure branch protection.
4. Test the actual events the repository uses. A manual dispatch pass does not establish fork-PR permission behavior.
5. Cancel superseded validation jobs when safe, but do not interrupt deployments or migrations without a recovery design. Keep job and process timeouts bounded.

Avoid blanket bans on every build cache: an existing cache can be useful when provenance and invalidation are sound. Never store credentials or allow cache reuse to cross a trust boundary unintentionally.

## Required checks must represent completed work

These cases have different GitHub behavior:

| Situation | Consequence and design choice |
| --- | --- |
| A required workflow is filtered out by paths or branches | Its check can remain pending. Keep the required entry workflow eligible and put selective execution behind an explicit result policy. |
| A job is skipped by its condition | It may satisfy a required check without testing anything. Distinguish an intentional no-op from missing coverage. |
| A prerequisite fails and the final gate depends on it | Run the gate with `always()` and `needs`, then explicitly fail unless required dependencies succeeded or were skipped for an allowed reason. `always()` by itself is not a success policy. |
| A merge queue is enabled | Include `merge_group` for required validation; test the queued merge revision. |

Exercise at least one intended failure through the final gate, plus an irrelevant-path change when filtering is used. A green manually dispatched run does not establish that the required PR check will be reported. See [GitHub required-check troubleshooting](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks).

## Primary references

- [GitHub: secure workflow use](https://docs.github.com/en/actions/reference/security/secure-use)
- [GitHub: events that trigger workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)
- [GitHub: workflow syntax and permissions](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)
- [GitHub: dependency caching](https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows)
