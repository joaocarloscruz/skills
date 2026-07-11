#!/usr/bin/env python3
"""Validate the repository's SKILL.md files using only the standard library."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
LIBRARY = ROOT / "library"
CATALOG = ROOT / "catalog"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CATALOG_LINK_RE = re.compile(r"\]\(\.\./\.\./library/([a-z0-9-]+)/\)")
DISCOVERY_BUDGET = 8_000
DISCOVERY_PATH_CHARS = 60


def parse_frontmatter(path: Path) -> tuple[dict[str, str], list[str]]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return {}, ["frontmatter must start on the first line"]
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}, ["frontmatter is missing its closing delimiter"]

    values: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            errors.append(f"invalid frontmatter line: {line!r}")
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip("\"'")
    return values, errors


def validate(path: Path) -> list[str]:
    metadata, errors = parse_frontmatter(path)
    allowed = {"name", "description"}
    extra = set(metadata) - allowed
    missing = allowed - set(metadata)
    if extra:
        errors.append(f"unexpected frontmatter keys: {', '.join(sorted(extra))}")
    if missing:
        errors.append(f"missing frontmatter keys: {', '.join(sorted(missing))}")

    name = metadata.get("name", "")
    if name and not NAME_RE.fullmatch(name):
        errors.append("name must use lowercase letters, digits, and hyphens")
    if name and name != path.parent.name:
        errors.append(f"name {name!r} must match folder {path.parent.name!r}")
    if not metadata.get("description", "").strip():
        errors.append("description must not be empty")
    return errors


def main() -> int:
    router_paths = sorted(SKILLS.glob("*/SKILL.md"))
    library_paths = sorted(LIBRARY.glob("*/SKILL.md"))
    paths = router_paths + library_paths
    if not router_paths or not library_paths:
        print("Router skills and the individual-skill library are both required.", file=sys.stderr)
        return 1

    failures = 0
    for path in paths:
        errors = validate(path)
        if errors:
            failures += 1
            print(f"FAIL {path.relative_to(ROOT)}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"OK   {path.relative_to(ROOT)}")

    skill_names = {path.parent.name for path in library_paths}
    categorized: dict[str, list[Path]] = {}
    category_files = sorted(CATALOG.glob("*/README.md"))
    if not category_files:
        print("FAIL no category indexes found")
        failures += 1
    for category_file in category_files:
        category = category_file.parent.name
        if not NAME_RE.fullmatch(category):
            print(f"FAIL invalid category folder: {category}")
            failures += 1
        for name in CATALOG_LINK_RE.findall(category_file.read_text(encoding="utf-8")):
            categorized.setdefault(name, []).append(category_file)

    missing_categories = skill_names - set(categorized)
    unknown_skills = set(categorized) - skill_names
    duplicate_categories = {
        name: files for name, files in categorized.items() if len(files) > 1
    }
    if missing_categories:
        print(f"FAIL uncategorized skills: {', '.join(sorted(missing_categories))}")
        failures += 1
    if unknown_skills:
        print(f"FAIL category links to unknown skills: {', '.join(sorted(unknown_skills))}")
        failures += 1
    for name, files in sorted(duplicate_categories.items()):
        locations = ", ".join(str(path.relative_to(ROOT)) for path in files)
        print(f"FAIL skill {name!r} appears in multiple categories: {locations}")
        failures += 1
    if not (missing_categories or unknown_skills or duplicate_categories):
        print(f"OK   catalog covers {len(skill_names)} skills exactly once")

    metadata = [parse_frontmatter(path)[0] for path in router_paths]
    discovery_chars = sum(
        len(f"- {item['name']}: {item['description']} (file: {'x' * DISCOVERY_PATH_CHARS})")
        for item in metadata
    ) + max(0, len(metadata) - 1)
    if discovery_chars > DISCOVERY_BUDGET:
        print(
            "FAIL default router discovery list uses "
            f"{discovery_chars}/{DISCOVERY_BUDGET} characters"
        )
        failures += 1
    else:
        print(
            "OK   default router discovery list uses "
            f"{discovery_chars}/{DISCOVERY_BUDGET} characters"
        )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
