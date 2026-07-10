# Skills

A model-neutral collection of small, composable skills for AI coding agents.

Each skill lives in `skills/<name>/` and contains a portable `SKILL.md` with `name` and `description` frontmatter. Reusable scripts, references, and assets should be added only when they earn their keep.

## Catalog

Skills remain flat under `skills/` for broad client and installer compatibility. Human-facing topic folders organize the catalog without changing each portable skill package.

| Category | Scope |
| --- | --- |
| [Planning and discovery](catalog/planning/) | Research, codebase understanding, specifications, and implementation planning |
| [Software engineering](catalog/engineering/) | APIs, database changes, implementation, migrations, and refactoring |
| [Frontend](catalog/frontend/) | Interface design, frontend implementation, design systems, accessibility, and browser testing |
| [Quality and security](catalog/quality-security/) | Debugging, test strategy, reviews, security, CI diagnosis, and interface testing |
| [Operations and maintenance](catalog/operations/) | Dependencies, performance, releases, and incident response |
| [Collaboration](catalog/collaboration/) | Handoffs, issue triage, and documentation |
| [AI engineering](catalog/ai-engineering/) | MCP servers, agent tools, and retrieval evaluation |
| [Data](catalog/data/) | Dataset analysis, SQL, and data pipelines |
| [Platform engineering](catalog/platform/) | Containers, observability, and continuous integration |

## Portability

`SKILL.md` is the complete cross-product skill contract. This catalog intentionally omits vendor-specific metadata so every skill has the same portable structure. Individual consumers may generate local integration metadata outside this repository when their product requires it.

## Use

Copy or symlink an individual folder into the skills directory supported by your agent, or point the agent directly at its `SKILL.md`. Discovery and installation paths vary by product.

Validate the collection with:

```bash
python scripts/validate_skills.py
```

## Install on Windows

From a local checkout, install all skills into Codex with:

```powershell
.\scripts\install.ps1
```

The installer uses `$CODEX_HOME\skills` when `CODEX_HOME` is set, otherwise
`$HOME\.codex\skills`. Its default `Symlink` mode keeps the installed skills
connected to this checkout, so a later `git pull` does not require
reinstallation. Windows may require Developer Mode or an elevated shell to
create symbolic links.

Install only selected skills, inspect the available names, or install into a
different compatible client's skill directory:

```powershell
.\scripts\install.ps1 -List
.\scripts\install.ps1 -Skills analyze-codebase,plan-implementation
.\scripts\install.ps1 -Destination "C:\path\to\skills" -Skills review-changes
```

Use `-Mode Copy` when symbolic links are unavailable. Existing destinations are
left untouched unless `-Force` is supplied; use `-WhatIf` to preview changes.
Copy-mode installations must be refreshed after each update:

```powershell
.\scripts\install.ps1 -Mode Copy -Force
```

## Design rules

- Keep each skill focused on one repeatable job.
- Put triggering language in the frontmatter description.
- Prefer short instructions and progressive disclosure.
- Make observations before conclusions; verify before declaring success.
- Avoid product-specific tool names unless the skill truly requires them.
- Record upstream inspiration and licenses in `SOURCES.md`.

See `CONTRIBUTING.md` before adding or adapting a skill.
