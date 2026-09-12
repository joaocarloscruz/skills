# Contributing

Create individual workflows at `library/<lowercase-hyphen-name>/SKILL.md`, then
add the workflow to exactly one `catalog/<category>/README.md` index. Run
`python scripts/build_router_bundles.py` to regenerate the installable routers
under `skills/`; do not edit generated references directly.

`scripts/catalog_utils.py` is the shared router configuration. Category indexes
are the canonical source of membership; validators and generation read the same
mapping. Commit the generated bundles and `skills/.generated-files.json` together.
Generation refuses conflicting local edits and unknown stale files rather than
silently deleting them. See [the architecture guide](docs/architecture.md).

Add at least one declared routing case for the workflow to
`tests/activation-cases.json`, including nearby skills that should not be
selected. Include near misses and explicit no-match cases when changing router
boundaries. A named router must actually bundle every expected workflow. Add the
skill to `evidence/skills.json`; inherit the conservative
defaults until stronger evidence exists.

This catalog uses a deliberately small YAML subset. Its frontmatter contains only
the following two scalar fields (a local convention, not a restriction of the
broader Agent Skills specification):

```yaml
---
name: lowercase-hyphen-name
description: State what the skill does and the requests that should trigger it.
---
```

Write the body as concise, imperative instructions. Add `scripts/`, `references/`,
or `assets/` only for material the agent will actually reuse. Keep detailed
variants outside `SKILL.md`, link them directly, and state when to read them.
Prefer domain-specific failure modes, decision rules, and checkable examples to
generic advice. Optional helpers must work from the installed package without
reaching into this repository. Keep resource paths inside the package and avoid
symlink or junction resources. The auditor checks this supported Markdown and
frontmatter subset; it is not a general YAML parser.

Preserve the user's authority and authorization across the workflow. Make
verification proportional to the change, report unavailable checks accurately,
and avoid making unrelated baseline failures or a missing reproduction block
independent useful work. Review the whole workflow when adding a new gate.

If a skill is copied or adapted, confirm that the source license permits redistribution. Preserve required notices, identify modified files, and add the source to `SOURCES.md`. Prefer synthesis over copying.

Do not label a skill externally evaluated merely because it belongs to a
vendor repository or benchmark dataset. Record the exact evaluated artifact,
revision, task result, model, and harness before strengthening its evidence
status. Otherwise keep `behavioral_evidence` unvalidated.

Use the [paired evaluation protocol](evals/README.md) for behavioral evidence.
Schema version 2 registry entries can reference recorded runs under
`evidence/runs/`; measured claims require complete paired results, exact skill
revisions, and existing raw artifacts. Synthetic fixtures test the tooling and
cannot support a behavioral claim. Preserve failed trials and report uncertainty
and cost alongside quality.

For technical references, cite the primary documentation in the relevant resource
and add new upstream inspiration to `SOURCES.md`. Pin reviewed candidate revisions
in the evidence registry. Attribution, popularity, structural validity, and
measured task improvement are different claims.

Run these checks before committing:

```bash
python scripts/build_router_bundles.py
python scripts/check.py
```

For CI parity, install PowerShell and use the official validator as well:

```bash
uv run --with skills-ref==0.1.1 python scripts/check.py --official --require-powershell
```

CI runs the shared checks on Linux and Windows. Add meaningful regression tests
for generator, installer, validator, or evaluation logic changes. Exercise
malformed input and failure recovery when they affect data preservation; avoid
tests that merely duplicate prose or implementation details.
