<!-- Generated from library/review-changes/SKILL.md; do not edit. -->

# Review Changes

## Fix the review boundary

1. Identify the base and head. Resolve both before reviewing.
2. Prefer a merge-base diff for branch review and include uncommitted changes when they are in scope.
3. Read repository instructions and the originating issue, specification, or acceptance criteria when available.
4. List changed files and commits, then inspect the full diff plus enough surrounding code to understand behavior.

## Review behavior before style

Trace changed inputs through outputs and side effects. Look for:

- incorrect logic, state transitions, boundary conditions, and error handling;
- compatibility or data-migration failures;
- authorization, validation, injection, secret, and privacy risks;
- race conditions, resource leaks, excessive work, and unbounded operations;
- missing or misleading tests, especially tests that cannot fail on the regression;
- requirements that are missing, partial, or exceeded by unrequested scope;
- violations of documented repository conventions that tools do not already enforce.

Treat maintainability smells as judgment calls, not defects by themselves. Avoid speculative findings; follow the actual execution path and cite concrete evidence.

## Report findings

Order findings by severity. For each actionable finding, provide:

1. a concise title with severity;
2. the narrowest relevant file and line;
3. the failure scenario or violated requirement;
4. why the current tests or guards do not prevent it;
5. a brief fix direction when it clarifies the issue.

Keep summaries short. If there are no actionable findings, say so and name any important verification gaps or residual risks. Do not modify code unless the user separately asks for fixes.
