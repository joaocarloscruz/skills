#!/usr/bin/env python3
"""Validate the repository's SKILL.md files using only the standard library."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


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
    paths = sorted(SKILLS.glob("*/SKILL.md"))
    if not paths:
        print("No skills found.", file=sys.stderr)
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
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
