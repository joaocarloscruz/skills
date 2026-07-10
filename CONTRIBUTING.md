# Contributing

Create skills at `skills/<lowercase-hyphen-name>/SKILL.md`.

The YAML frontmatter must contain only:

```yaml
---
name: lowercase-hyphen-name
description: State what the skill does and the requests that should trigger it.
---
```

Write the body as concise, imperative instructions. Add `scripts/`, `references/`, or `assets/` only for material the agent will actually reuse. Keep detailed variants outside `SKILL.md` and link them directly from it.

If a skill is copied or adapted, confirm that the source license permits redistribution. Preserve required notices, identify modified files, and add the source to `SOURCES.md`. Prefer synthesis over copying.

Run `python scripts/validate_skills.py` before committing.
