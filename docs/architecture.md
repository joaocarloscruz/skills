# Catalog architecture

The repository has one editable workflow library and a generated installation view:

```text
library/<workflow>/        Canonical SKILL.md, conditional references, tested helpers
catalog/<topic>/README.md  Human-facing membership; exactly one category per workflow
scripts/catalog_utils.py  Shared router definitions and membership validation
skills/<router>/          Generated, self-contained portable installation packages
skills/.generated-files.json  Ownership and hashes for generated output cleanup
scripts/                  Repository build, installation and validation tools
tests/                    Deterministic tooling and declared activation fixtures
evals/                    Behavioral evaluation protocol and starter task briefs
evidence/                 Reviewed sources and any recorded behavioral results
docs/                     Maintenance decisions and research
```

Edit `library/`, then regenerate with `python scripts/build_router_bundles.py`. Do not edit generated workflow copies. Each router bundles its leaf references and scripts, so installing a router does not require the repository's other folders. The builder validates source packages before writing output, rejects symlink/junction redirects and tracks generated ownership. It refuses to delete unowned or locally modified stale output. Preserve or reconcile unexpected output before rebuilding.

Modification protection applies to manifest-tracked files; initial migration without a manifest writes canonical expected paths while refusing unowned extra files.

Both installation shapes remain useful. Nine routers keep initial metadata small for a broad catalog. Installing an exact `library/<workflow>` exposes it directly and avoids an extra selection step for frequent work. Neither shape is assumed to outperform the other; compare natural discovery on the target runtime. Installing both can create redundant choices and should be deliberate.

Frontmatter remains the catalog's narrow portable subset (`name` and `description`). This is a repository convention, not a claim that the Agent Skills specification forbids optional metadata. Runtime-specific UI, hooks, policies and tool dependencies belong in a separately justified integration, not every portable skill.

References are conditional and self-contained. They should supply a worked decision, a version-sensitive implementation constraint or a reusable procedure. An ordinary short workflow does not need a references directory. Tooling tests and evaluation graders live outside installable packages to avoid shipping hidden answers as skill context.

The Windows installer records ownership in `.skills-install-manifest.json` in the destination. It preflights the entire selection before modifying anything, stages replacements, and uses rollback backups for ordinary operation failures. Pruning applies only to verified, unchanged owned entries. Unknown or modified entries survive pruning. `-Force` explicitly replaces selected collisions; it is not a blanket authorization to prune unknown entries. `-WhatIf` reports the plan without creating the destination or writing a manifest. A process kill or machine failure is outside ordinary exception rollback; preserve reported staging/backup data when recovering.

The architecture adopts progressive disclosure, independently installable packages, deterministic generation and separated behavioral evaluation from established repositories. It does not import their full plugin frameworks, runtime gates or licenses. See [the source comparison](research-2026-09-12.md) and [evaluation workflow](../evals/README.md).
