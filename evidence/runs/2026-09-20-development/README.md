# Recorded development smoke — 2026-09-20

These are actual agent submissions and executable grades, not fabricated
success rows. They are a small development exercise with substantial isolation
and model-provenance limits. The evidence registry remains `unvalidated` for
behavioral improvement and `fixture-only` for native activation.

## Behavior outcomes

| Task | Target package | Target not loaded | Target loaded |
| --- | --- | --- | --- |
| SQL paid revenue and order counts | write-sql | Pass, 2 dataset checks | Pass, 2 dataset checks |
| Restartable event delivery | design-data-pipeline | Pass, 16 scenarios | Pass, 16 scenarios |
| Ambiguous tool-write recovery | design-agent-tools | Pass, 8 scenarios | Pass, 8 scenarios |

All six submissions passed their outcome checks, with no observed regression or
success-rate improvement. The tiny, homogeneous result is not evidence of
equivalence or general superiority. The comparison's degenerate zero-width
bootstrap interval reflects this sample, not certainty about future tasks.
No cost comparison is available; duration and token measurements are `null`.

- [Plan](plan.json): three tasks, one repetition in each condition, frozen before
  execution; per-package file digests and harness digest.
- [Results](results.json) and [comparison](comparison.json): complete paired
  cells, directly linked submission records, and raw grader checks.
- [Candidate packages](candidate-packages.json): exact evaluated UTF-8 contents,
  including original line endings, and file hashes. A package revision hashes
  the compact sorted JSON map of relative paths to SHA-256 file hashes. The
  combined condition revision hashes the sorted task-to-package-revision map.
- Each `artifacts/*.json` preserves the submitted source text and its byte hash,
  public contract, visible fixture, and grade. It is possible to reconstruct a
  submission by UTF-8 encoding `source_utf8` without newline conversion, then
  run `python evals/smoke/run.py grade TASK DIRECTORY` from this repository.

The grader was checked with correct and deliberately defective solutions before
trials. Review caught and fixed an overly strict per-event checkpoint assumption;
the frozen grader accepts a valid final batched checkpoint and reports fault
boundaries not reached by that strategy. These corrections preceded all six
behavior trials. No submission received private grader feedback or a retry.

## Execution conditions and limits

Each task/condition used a fresh `fork_turns=none` Codex agent context and a
separate prepared directory. The baseline phase preceded the loaded-skill phase;
tasks within a phase could overlap. The inherited model and reasoning settings
were left unchanged, but their exact backend versions and sampling parameters
were not exposed. This prevents a strict version-pinned causal comparison.

Every runner received the public `TASK.md`, `fixture.json`, and stub, was asked
to implement and check the visible example, and was prohibited from reading
other trials, private graders, expected answers, or outside repository files.
The loaded condition also received a copied target package and was asked to
read its applicable resources. No web access, extra subagents, or writes outside
the assigned directory were permitted by the runner instructions.

Separation was procedural: the host filesystem and installed tool/skill metadata
were shared, and no OS boundary enforced grader exclusion or disabled global
skills. The baseline therefore means **target package not supplied**, not a
fully skill-free agent. Full tool transcripts and exact cost measurements were
not captured. Submitted source and final grades are preserved; isolation cannot
be established from these artifacts alone. There was one repetition, no held-out
population, and no run of a previous package revision.

## Metadata-selection exercise

A separate fresh context received only [catalog metadata and 74 opaque request
IDs](routing/input.json), and produced [one recorded answer](routing/answer.json).
It was instructed to choose the minimal sufficient workflow set without carrying
out requests or inspecting expected labels. A turn interruption was resumed in
the same context without answer feedback.

[Exact scoring](routing/score.json) matched all 74 routers and 72 complete workflow
sets. The two differences were:

- `plan-change-in-existing-codebase`: chose `plan-implementation`; the fixture
  also expects `analyze-codebase`.
- `implement-feature-test-first`: chose `tdd`; the fixture also expects
  `implement-feature`.

These are composition disagreements, not demonstrated task failures. The chosen
workflows already include code inspection or implementation. Expected labels
were preserved; they should be checked against native execution before adding
instructions that force redundant workflow loading. This exercise exposes all
catalog metadata in a batch and does not test discovery, progressive loading,
router-body instructions, or runtime activation.

After recording the response, the routing helper's dataset digest was made
independent of Windows/Linux newline conversion. The original input, answer and
score retain their original byte-based revision. [The replay answer](routing/replay-answer.json)
changes only the revision metadata to the canonical JSON digest; selections and
all 74 scored outcomes are identical. Reproduce that portable score with:

```text
python evals/routing.py score evidence/runs/2026-09-20-development/routing/replay-answer.json
python library/evaluate-ai-output/scripts/compare_runs.py evidence/runs/2026-09-20-development/results.json --baseline target-not-loaded --candidate target-loaded
```

Use a broader held-out task set, repeated randomized trials, exact model/tool
versions, enforced isolation, and native activation traces before claiming
general improvement or comparing this catalog with popular external skills.
