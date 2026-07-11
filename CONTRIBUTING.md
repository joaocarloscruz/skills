# Contributing

Create individual workflows at `library/<lowercase-hyphen-name>/SKILL.md`, then
add the workflow to exactly one `catalog/<category>/README.md` index. Run
`python scripts/build_router_bundles.py` to regenerate the installable routers
under `skills/`; do not edit generated references directly.

The YAML frontmatter must contain only:

```yaml
---
name: lowercase-hyphen-name
description: State what the skill does and the requests that should trigger it.
---
```

Write the body as concise, imperative instructions. Add `scripts/`, `references/`, or `assets/` only for material the agent will actually reuse. Keep detailed variants outside `SKILL.md` and link them directly from it.

If a skill is copied or adapted, confirm that the source license permits redistribution. Preserve required notices, identify modified files, and add the source to `SOURCES.md`. Prefer synthesis over copying.

Run these checks before committing:

```bash
python scripts/build_router_bundles.py --check
python scripts/validate_skills.py
```
