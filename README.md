# Skills

A model-neutral collection of small, composable skills for AI coding agents.

Each skill lives in `skills/<name>/` and contains a portable `SKILL.md` with `name` and `description` frontmatter. Reusable scripts, references, and assets should be added only when they earn their keep.

## Catalog

### Understand and plan

- `analyze-codebase` — Map architecture, boundaries, and execution paths.
- `break-down-work` — Turn goals into small, verifiable work items.
- `plan-implementation` — Create implementation-ready plans grounded in code.
- `research-with-sources` — Produce concise, source-backed research.
- `write-technical-spec` — Define testable behavior and engineering contracts.

### Build and change

- `design-api` — Design coherent, evolvable interfaces.
- `design-database-change` — Plan safe schemas, migrations, and rollbacks.
- `implement-feature` — Implement scoped behavior with verification.
- `migrate-dependency` — Upgrade dependencies with controlled compatibility.
- `refactor-safely` — Improve structure while preserving behavior.
- `resolve-merge-conflicts` — Reconcile competing changes by intent.

### Frontend

- `design-frontend-interface` — Define intentional product and marketing interface direction.
- `build-frontend-interface` — Implement production web interfaces and interaction behavior.
- `build-design-system` — Create reusable tokens, primitives, components, and governance.

### Debug, test, and review

- `debug-systematically` — Reproduce, isolate, fix, and verify defects.
- `design-test-strategy` — Select risk-based tests at effective seams.
- `evaluate-ai-output` — Build rigorous evaluations for AI behavior.
- `investigate-ci-failure` — Trace pipeline failures to root causes.
- `review-accessibility` — Find barriers in essential user journeys.
- `review-changes` — Review diffs for correctness, risk, and scope.
- `review-security` — Threat-model changes and find exploitable risks.
- `test-api` — Verify contracts, errors, and side effects.
- `test-cli` — Verify command-line behavior and compatibility.
- `test-local-webapp` — Inspect and verify local web applications.

### Operate and maintain

- `audit-dependencies` — Assess dependency health and supply-chain risk.
- `improve-performance` — Measure and fix performance bottlenecks.
- `release-software` — Prepare and verify controlled releases.
- `respond-to-incident` — Stabilize, investigate, recover, and learn.

### Collaborate

- `prepare-handoff` — Capture state for seamless continuation.
- `triage-issues` — Turn reports into prioritized, actionable issues.
- `write-documentation` — Create accurate, task-oriented documentation.

## Portability

`SKILL.md` is the complete cross-product skill contract. This catalog intentionally omits vendor-specific metadata so every skill has the same portable structure. Individual consumers may generate local integration metadata outside this repository when their product requires it.

## Use

Copy or symlink an individual folder into the skills directory supported by your agent, or point the agent directly at its `SKILL.md`. Discovery and installation paths vary by product.

Validate the collection with:

```bash
python scripts/validate_skills.py
```

## Design rules

- Keep each skill focused on one repeatable job.
- Put triggering language in the frontmatter description.
- Prefer short instructions and progressive disclosure.
- Make observations before conclusions; verify before declaring success.
- Avoid product-specific tool names unless the skill truly requires them.
- Record upstream inspiration and licenses in `SOURCES.md`.

See `CONTRIBUTING.md` before adding or adapting a skill.
