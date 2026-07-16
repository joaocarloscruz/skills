# Contributing

Create individual workflows at `library/<lowercase-hyphen-name>/SKILL.md`, then
add the workflow to exactly one `catalog/<category>/README.md` index. Run
`python scripts/build_router_bundles.py` to regenerate the installable routers
under `skills/`; do not edit generated references directly.

Add at least one declared routing case for the workflow to
`tests/activation-cases.json`, including nearby skills that should not be
selected. Add the skill to `evidence/skills.json`; inherit the conservative
defaults until stronger evidence exists.

The YAML frontmatter must contain only:

```yaml
---
name: lowercase-hyphen-name
description: State what the skill does and the requests that should trigger it.
---
```

Write the body as concise, imperative instructions. Add `scripts/`, `references/`, or `assets/` only for material the agent will actually reuse. Keep detailed variants outside `SKILL.md` and link them directly from it.

If a skill is copied or adapted, confirm that the source license permits redistribution. Preserve required notices, identify modified files, and add the source to `SOURCES.md`. Prefer synthesis over copying.

Do not label a skill externally evaluated merely because it belongs to a
vendor repository or benchmark dataset. Record the exact evaluated artifact,
revision, task result, model, and harness before strengthening its evidence
status. Otherwise keep `behavioral_evidence` unvalidated.

Run these checks before committing:

```bash
python scripts/build_router_bundles.py --check
python scripts/validate_skills.py
python scripts/validate_activation_cases.py
python scripts/validate_evidence_registry.py
```
