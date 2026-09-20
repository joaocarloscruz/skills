# Complete catalog review — 2026-09-20

This follow-up reviewed all 43 canonical workflows after the
[public-skills comparison](research-2026-09-20.md). 35 workflows changed;
8 were retained because the review found no concrete gap requiring more
instructions. Twelve new conditional references add depth without loading all
details into every request. All material is original synthesis; supporting
primary documentation is linked in each relevant package and [SOURCES.md](../SOURCES.md).

The review used separate engineering/frontend, platform/data, and quality/AI
passes, plus integration review. An independent platform review caught and
corrected an off-by-one retry/attempt example before publication. Editorial
review and popularity comparisons do not establish measured skill uplift.

## Disposition of every workflow

| Workflow | Disposition | Reason or correction |
| --- | --- | --- |
| [add-observability](../library/add-observability/SKILL.md) | Changed | The checklist did not resolve distributed percentile aggregation, sampling bias, attempt/outcome denominators, missing signals, low-volume alerts, or multi-input span parentage. Added a conditional signal-design reference and corrected the parentage instruction to allow links. |
| [analyze-codebase](../library/analyze-codebase/SKILL.md) | Retained | Already traces actual execution paths, checks claims against code, and distinguishes inactive code from current behavior. No supported gap justified expansion. |
| [analyze-dataset](../library/analyze-dataset/SKILL.md) | Changed | Added conditional checks for join expansion/null-key semantics, weighted versus average-group rates, partial-period comparisons, and preprocessing leakage. Avoided making descriptive analysis require predictive modeling. |
| [audit-dependencies](../library/audit-dependencies/SKILL.md) | Changed | Replaced absolute reachability confirmation with explicit unknowns; development/build exposure is assessed rather than discounted. Added scanner/lockfile provenance, advisory alias grouping, transitive-owner remediation, and concrete reporting-versus-install distinctions. |
| [audit-skill-catalog](../library/audit-skill-catalog/SKILL.md) | Retained | The preceding pass repaired executable resource reachability and Windows path aliases. Its claims already distinguish structural checks from behavioral effectiveness. |
| [break-down-work](../library/break-down-work/SKILL.md) | Changed | Resolve dependency cycles before parallel work and keep behavior, its verification, and necessary documentation in the same completion unit. |
| [build-design-system](../library/build-design-system/SKILL.md) | Changed | Existing React composition reference now covers repeated instance IDs, explicit consumer IDs, hydration, and the distinction between accessibility IDs and data-derived list keys. |
| [build-frontend-interface](../library/build-frontend-interface/SKILL.md) | Changed | React reference adds the concrete A-then-B/B-resolves-first race, lifecycle cleanup, and the distinction between canceled reads and server mutation outcomes. |
| [build-mcp-server](../library/build-mcp-server/SKILL.md) | Changed | Corrected error classification: tool input validation can be `isError` before an operation has side effects. Added initialization/capability tests, absolute deadlines, cancellation/completion races, task cancellation distinction, and protocol-ID versus business-idempotency separation. |
| [containerize-application](../library/containerize-application/SKILL.md) | Changed | Added concrete build-secret leakage, Linux signal forwarding, native runtime compatibility, writable-path verification, and readiness/liveness/startup distinctions. Kept this conditional and platform-labeled rather than imposing Kubernetes on every container. |
| [debug-systematically](../library/debug-systematically/SKILL.md) | Changed | Added conditional nondeterminism/bisection reference: order-dependent isolation, low-interference instrumentation, comparable failure counts, stable predicates, skip semantics, and preserving user work. |
| [design-agent-tools](../library/design-agent-tools/SKILL.md) | Changed | Added stable object/version preconditions, preview staleness, authenticated identity versus model-supplied scope, and reuse of existing user authorization. |
| [design-api](../library/design-api/SKILL.md) | Changed | Added conditional contract examples for ambiguous mutation outcomes, duplicate request identity, conditional edits, null/omitted semantics, and pagination/evolution. Existing checklist named these concerns without making their decisions testable. Corrected the implication that additive changes are inherently compatible. |
| [design-data-pipeline](../library/design-data-pipeline/SKILL.md) | Changed | Added a crash-boundary table and atomic deduplication example, scoped broker guarantees to supported sinks, and defined late-window output semantics, backfill overlap, and quarantine accounting. |
| [design-database-change](../library/design-database-change/SKILL.md) | Retained | Existing PostgreSQL reference already covers mixed application versions, stale backfills, invalid concurrent indexes, transaction restrictions, lock exposure, constraint validation, and rollback compatibility. Additional engine-specific material without a concrete need would dilute the skill. |
| [design-frontend-interface](../library/design-frontend-interface/SKILL.md) | Changed | Removed mandatory signature novelty and arbitrary three-default rejection. Established product screens can preserve existing patterns while new brands/campaigns still receive appropriate distinctiveness critique. |
| [design-test-strategy](../library/design-test-strategy/SKILL.md) | Changed | Added a wrong-implementation test for assertions and real-boundary checks where mocks hide the risk. Mutation/fault injection stays conditional. |
| [domain-modeling](../library/domain-modeling/SKILL.md) | Changed | Scoped terminology consistency to bounded contexts instead of imposing one global model; made immediate invariants versus eventual policy convergence and decision ownership explicit. |
| [evaluate-ai-output](../library/evaluate-ai-output/SKILL.md) | Changed | Version 2 trial plans reject tasks missing from every condition, not only mismatched pairs. Legacy results retain an explicit unverified-coverage warning. |
| [evaluate-rag](../library/evaluate-rag/SKILL.md) | Changed | Added principal/time-aware relevance, separate unauthorized retrieval failures, stable labels across chunking changes, incomplete-label qualifications, grouped held-out cases, and skipped/timeout denominators. |
| [implement-feature](../library/implement-feature/SKILL.md) | Retained | Already gives proportional verification, stable seams, scope control, baseline-failure separation, and incomplete acceptance reporting. More universal gates or another checklist would duplicate the workflow without changing decisions. |
| [improve-performance](../library/improve-performance/SKILL.md) | Changed | Corrected unconditional warm-up, which could invalidate cold-start work. Added open/closed load models, dropped/failed work accounting, comparable cache/data conditions, interleaving, variance, and end-to-end equivalence. |
| [investigate-ci-failure](../library/investigate-ci-failure/SKILL.md) | Changed | Distinguished run metadata from the actual checkout, including synthetic PR merge results, plus absent/skipped/cancelled checks and cache diagnostic limits. |
| [migrate-dependency](../library/migrate-dependency/SKILL.md) | Changed | Added conditional host/plugin/runtime compatibility, normal resolution, isolated clean installs, packed-consumer checks, and persisted-data rollback boundaries. Resolving or compiling alone does not establish those outcomes. |
| [plan-implementation](../library/plan-implementation/SKILL.md) | Retained | Already resolves discoverable questions, sequences verifiable changes, and scales operational checks to the task. More universal gates would duplicate existing guidance. |
| [prepare-handoff](../library/prepare-handoff/SKILL.md) | Changed | Preserve exact checkout/tested state and in-flight external effects so the next worker reconciles uncertain writes before repeating them. |
| [refactor-safely](../library/refactor-safely/SKILL.md) | Retained | Already protects serialization/public behavior/runtime references and distinguishes baseline failures. No supported gap justified expanding a concise behavior-preservation workflow. |
| [release-software](../library/release-software/SKILL.md) | Changed | Added artifact identity, idempotent resumption after uncertain publication, conflict handling, immutable-release staging, and schema-compatible rollback. Existing user authorization is reused. |
| [research-with-sources](../library/research-with-sources/SKILL.md) | Changed | Separate publication, event and effective dates; trace repeated reporting to the underlying source; open support before citing a snippet. |
| [resolve-merge-conflicts](../library/resolve-merge-conflicts/SKILL.md) | Retained | Recent reference already handles missing index stages, rebase side reversal, unrelated staged work, generated inputs, sequencer continuation, and redundant-patch skip evidence. Rewriting would duplicate verified mechanics. |
| [respond-to-incident](../library/respond-to-incident/SKILL.md) | Changed | Added bounded action records, uncertain-outcome inspection, mitigation tradeoffs, backlog-aware recovery and handoff. Communication drafts do not imply authority to send messages. |
| [review-accessibility](../library/review-accessibility/SKILL.md) | Changed | Adds WCAG 2.2 AA authentication/OTP paste checks with the actual alternative/assistance exceptions, avoiding false automatic conformance findings. |
| [review-changes](../library/review-changes/SKILL.md) | Changed | Added conditional Git comparison table, untracked/local/merge/root-commit handling, revision drift, and base-versus-patch defect attribution. |
| [review-security](../library/review-security/SKILL.md) | Changed | Added worker/service-credential, status/artifact, revocation, and authorization-bypassing cache-hit paths. |
| [tdd](../library/tdd/SKILL.md) | Changed | Distinguished a relevant missing-behavior/public-interface red result from unrelated runner/setup failure, without prohibiting legitimate initial failure for an unimplemented API. |
| [test-api](../library/test-api/SKILL.md) | Changed | Added response-loss-after-commit injection, duplicate downstream-effect assertions, and bounded eventual-consistency observations. |
| [test-cli](../library/test-cli/SKILL.md) | Changed | Added conditional process-contract reference covering installed entrypoint, outside-checkout launch, machine streams, EOF versus TTY, option-looking filenames, process-tree cleanup, and trustworthy pipe/time-limit harnesses. |
| [test-local-webapp](../library/test-local-webapp/SKILL.md) | Changed | Keeps initial failure evidence after successful retries and requires bounded classification rather than retry-until-green; Playwright reference explains worker/setup changes. |
| [triage-issues](../library/triage-issues/SKILL.md) | Changed | Do not deduplicate by error text alone; distinguish recurrence after a fix and separate impact severity from scheduling priority. |
| [write-ci-pipeline](../library/write-ci-pipeline/SKILL.md) | Changed | Extended the existing GitHub reference with the operational differences between a filtered workflow, skipped job, failed dependency, and merge queue. Required final gates must evaluate dependency results; always() alone does not establish success. |
| [write-documentation](../library/write-documentation/SKILL.md) | Changed | Test state-changing examples in disposable fixtures; make shell, working directory, placeholders and success observations explicit. |
| [write-sql](../library/write-sql/SKILL.md) | Retained | Existing query-correctness reference already covers join grain, anti-join NULLs, outer-join counts, stable ties, integer ratios, DST windows, and EXPLAIN execution effects. No demonstrated missing decision justified additional prose. |
| [write-technical-spec](../library/write-technical-spec/SKILL.md) | Changed | Require concrete accepted/rejected examples and observable retry/concurrency behavior where relevant. |

## Executable improvements

- The paired-result validator accepts a frozen version 2 task/repetition plan,
  rejects omitted and unplanned cells, and keeps legacy input support with a
  warning. Regression tests demonstrate the old blind spot and the new behavior.
- The routing corpus grew from 50 to 74 declared cases. A metadata-only selection
  harness exports opaque case IDs without answer labels and requires complete,
  revision-matched responses before scoring.
- Three resettable behavior tasks cover SQL aggregation grain, crash/replay
  boundaries, and uncertain tool writes. Private outcome graders and deliberately
  defective solutions check whether the harness can distinguish real failures.

These harnesses provide development checks, not a leaderboard or a substitute
for fresh, isolated, version-pinned evaluations on held-out tasks.

## Validation and remaining evidence limits

The official validator passes all 52 installable packages. Canonical and generated
catalog audits report zero errors or warnings. Repository tests and the 19
smoke-grader regressions pass; nine Windows symlink-capability checks are skipped
on the local host and remain visible in the test output. Shared CI runs the same
checks on Linux and Windows.

[Recorded development results](../evidence/runs/2026-09-20-development/README.md)
preserve all six behavioral submissions: three tasks pass both without and with
their target package. There is no observed uplift on this small set. Metadata
selection matches all 74 routers and 72 full workflow sets, with two composition
disagreements retained for native-runtime investigation. Exact model versions,
enforced isolation, cost measurements, and held-out evaluation are unavailable;
these limits are explicit in the run records.

The registry retains conservative evidence states. An editorial improvement or
a passing small development task does not demonstrate general superiority.
