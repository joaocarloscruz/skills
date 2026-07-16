# Skills

A model-neutral collection of small, composable skills for AI coding agents.

The default installation exposes nine portable router skills. Each router selects
and loads one of 43 generated workflow references, keeping the initial skill list
small without removing capabilities. Canonical individual skills remain under
`library/<name>/` for direct installation and maintenance.

## Catalog

Routers remain flat under `skills/` for broad client and installer compatibility.
Human-facing topic folders define their workflow membership, and the individual
portable packages remain flat under `library/`.

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

`SKILL.md` and referenced Markdown files form the complete cross-product contract.
Routers use ordinary progressive disclosure rather than vendor-specific dynamic
registration, so clients only need to support bundled references. The catalog
intentionally omits vendor-specific metadata.

## Use

Install the nine folders under `skills/` for the complete routed catalog. Install
an exact folder under `library/` when you want a leaf workflow such as `tdd` to
appear as a native top-level skill. Discovery and installation paths vary by
product.

Validate the collection with:

```bash
python scripts/validate_skills.py
python scripts/validate_activation_cases.py
python scripts/validate_evidence_registry.py
```

The validator measures the routers' approximate contribution to Codex's initial
discovery list using a 60-character installed-path allowance. The 8,000-character
fallback affects initial metadata, not the workflow loaded after routing.

Regenerate and verify router bundles with:

```bash
python scripts/build_router_bundles.py
python scripts/build_router_bundles.py --check
```

## Install on Windows

From a local checkout, install the nine routers into Codex with:

```powershell
.\scripts\install.ps1
```

The installer uses `$CODEX_HOME\skills` when `CODEX_HOME` is set, otherwise
`$HOME\.codex\skills`. Its default `Routers` profile provides all workflows
through hierarchical routing. Its default `Symlink` mode keeps the installation
connected to this checkout, so a later `git pull` does not require
reinstallation. Windows may require Developer Mode or an elevated shell to
create symbolic links.

Inspect both routers and individual workflows, install an individual workflow,
or install into a different compatible client's skill directory:

```powershell
.\scripts\install.ps1 -List
.\scripts\install.ps1 -Skills tdd,domain-modeling
.\scripts\install.ps1 -Destination "C:\path\to\skills" -Skills review-changes
```

Use `-Profile Library` to install all 43 individual workflows or `-Profile All`
to install routers and workflows together. `-Prune` removes other entries from
this catalog when switching profiles without touching unrelated skills.

Use `-Mode Copy` when symbolic links are unavailable. Existing destinations are
left untouched unless `-Force` is supplied; use `-WhatIf` to preview changes.
Copy-mode installations must be refreshed after each update:

```powershell
.\scripts\install.ps1 -Mode Copy -Force -Prune
```

## Activation regression fixtures

`tests/activation-cases.json` records representative requests and the skills
that should, and should not, activate. It is a catalog-specific regression
corpus, not an executed test or cross-model benchmark. The validator checks
fixture structure and requires every router and workflow to be represented; it
does not run an agent or establish that routing works in a particular model.
Use the prompts as declared expectations when manually checking a target agent.

Validate the fixture schema and every referenced skill with:

```bash
python scripts/validate_activation_cases.py
```

## Evidence and provenance

`evidence/skills.json` records the catalog's current claim boundary. Its default
classification applies to every individual skill:

- `structural_validation: passed` means deterministic repository and format
  checks pass.
- `activation_evidence: fixture-only` means a routing expectation exists but
  has not been executed across models.
- `behavioral_evidence: unvalidated` means the repository has no evidence that
  the skill improves task outcomes over a no-skill baseline.
- `provenance: original-synthesis` reflects the repository's authorship claim;
  catalog-level inspiration remains documented in `SOURCES.md`.

The registry also pins reviewed revisions of plausible public alternatives.
These entries are comparison candidates, not endorsements. Vendor maintenance,
repository popularity, or inclusion in a benchmark dataset does not by itself
show that a skill improves performance.

Validate the registry with:

```bash
python scripts/validate_evidence_registry.py
```

## Design rules

- Keep each skill focused on one repeatable job.
- Put triggering language in the frontmatter description.
- Prefer short instructions and progressive disclosure.
- Make observations before conclusions; verify before declaring success.
- Avoid product-specific tool names unless the skill truly requires them.
- Record upstream inspiration and licenses in `SOURCES.md`.
- Keep evidence claims and external candidates current in `evidence/skills.json`.

See `CONTRIBUTING.md` before adding or adapting a skill.
