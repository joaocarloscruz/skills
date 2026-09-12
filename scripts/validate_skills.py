#!/usr/bin/env python3
"""Validate repository packages and discovery metadata using the portable auditor."""
from __future__ import annotations
import importlib.util
import sys
from pathlib import Path
try:
    from .catalog_utils import ROUTER_CONFIG, catalog_membership, is_link
except ImportError:
    from catalog_utils import ROUTER_CONFIG, catalog_membership, is_link
ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
LIBRARY = ROOT / "library"
CATALOG = ROOT / "catalog"
DISCOVERY_BUDGET = 8_000
DISCOVERY_PATH_CHARS = 60
# Repository tools reuse the portable auditor; installed skills need no repo imports.
_spec = importlib.util.spec_from_file_location(
    "portable_catalog_auditor", LIBRARY / "audit-skill-catalog" / "scripts" / "audit_catalog.py"
)
if _spec is None or _spec.loader is None:
    raise RuntimeError("cannot load portable catalog auditor")
_auditor = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _auditor
_spec.loader.exec_module(_auditor)
parse_frontmatter = _auditor.parse_frontmatter


def validate(path: Path) -> list[str]:
    if is_link(path) or is_link(path.parent):
        return ["skill package and SKILL.md must not be symlinks or junctions"]
    errors = [finding.message for finding in _auditor.audit(path.parent, 1.0) if finding.severity == "error"]
    if _auditor.discover_skill_files(path.parent) != [path]:
        errors.append("a repository package must contain exactly its top-level SKILL.md")
    return errors


def main() -> int:
    try:
        if is_link(SKILLS) or not SKILLS.is_dir():
            raise ValueError("skills must be a real directory")
        router_paths = sorted(SKILLS.glob("*/SKILL.md"))
        library_paths = sorted(LIBRARY.glob("*/SKILL.md"))
        paths = router_paths + library_paths
        if not router_paths or not library_paths:
            raise ValueError("Router skills and the individual-skill library are both required")
        actual_routers = {path.name for path in SKILLS.iterdir() if path.is_dir()}
        if actual_routers != set(ROUTER_CONFIG):
            raise ValueError(f"router directory mismatch: missing={sorted(set(ROUTER_CONFIG) - actual_routers)}, extra={sorted(actual_routers - set(ROUTER_CONFIG))}")
        failures = 0
        names: set[str] = set()
        router_metadata = []
        for path in paths:
            errors = validate(path)
            metadata, _ = parse_frontmatter(path)
            name = metadata.get("name")
            if isinstance(name, str):
                if name in names:
                    errors.append(f"duplicate skill name: {name}")
                names.add(name)
            if errors:
                failures += 1
                print(f"FAIL {path.relative_to(ROOT)}")
                for error in errors:
                    print(f"  - {error}")
            else:
                print(f"OK   {path.relative_to(ROOT)}")
                if path in router_paths:
                    router_metadata.append(metadata)
        membership = catalog_membership(ROOT)
        print(f"OK   catalog covers {sum(map(len, membership.values()))} skills exactly once")
        discovery_chars = sum(
            len(f"- {item['name']}: {item['description']} (file: {'x' * DISCOVERY_PATH_CHARS})")
            for item in router_metadata
        ) + max(0, len(router_metadata) - 1)
        if discovery_chars > DISCOVERY_BUDGET:
            print(f"FAIL default router discovery list uses {discovery_chars}/{DISCOVERY_BUDGET} characters")
            failures += 1
        else:
            print(f"OK   default router discovery list uses {discovery_chars}/{DISCOVERY_BUDGET} characters")
        return 1 if failures else 0
    except (OSError, UnicodeError, ValueError) as error:
        print(f"Catalog validation error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
