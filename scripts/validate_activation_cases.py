#!/usr/bin/env python3
"""Validate the catalog's skill-activation regression fixtures."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = ROOT / "tests" / "activation-cases.json"
CASE_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REQUIRED_FIELDS = {
    "id",
    "title",
    "prompt",
    "expected_router",
    "expected_skills",
    "unexpected_skills",
    "rationale",
}


def known_skills(root: Path) -> set[str]:
    return {
        path.parent.name
        for path in (root / "library").glob("*/SKILL.md")
    }


def known_routers(root: Path) -> set[str]:
    return {
        path.parent.name
        for path in (root / "skills").glob("*/SKILL.md")
    }


def validate_case(
    case: object,
    index: int,
    skills: set[str],
    routers: set[str],
) -> list[str]:
    prefix = f"case {index + 1}"
    if not isinstance(case, dict):
        return [f"{prefix}: must be an object"]

    errors: list[str] = []
    missing = REQUIRED_FIELDS - set(case)
    extra = set(case) - REQUIRED_FIELDS
    if missing:
        errors.append(f"{prefix}: missing fields: {', '.join(sorted(missing))}")
    if extra:
        errors.append(f"{prefix}: unexpected fields: {', '.join(sorted(extra))}")

    case_id = case.get("id")
    if not isinstance(case_id, str) or not CASE_ID_RE.fullmatch(case_id):
        errors.append(f"{prefix}: id must be lowercase kebab-case")

    for field in ("title", "prompt", "rationale"):
        if not isinstance(case.get(field), str) or not case[field].strip():
            errors.append(f"{prefix}: {field} must be a non-empty string")

    expected_router = case.get("expected_router")
    if not isinstance(expected_router, str) or expected_router not in routers:
        errors.append(f"{prefix}: expected_router must name a known router")

    expected = case.get("expected_skills")
    unexpected = case.get("unexpected_skills")
    if not isinstance(expected, list) or not expected or not all(isinstance(item, str) for item in expected):
        errors.append(f"{prefix}: expected_skills must be a non-empty list of skill names")
        expected = []
    if not isinstance(unexpected, list) or not all(isinstance(item, str) for item in unexpected):
        errors.append(f"{prefix}: unexpected_skills must be a list of skill names")
        unexpected = []

    if len(expected) != len(set(expected)):
        errors.append(f"{prefix}: expected_skills contains duplicates")
    if len(unexpected) != len(set(unexpected)):
        errors.append(f"{prefix}: unexpected_skills contains duplicates")
    overlap = set(expected) & set(unexpected)
    if overlap:
        errors.append(f"{prefix}: skills cannot be both expected and unexpected: {', '.join(sorted(overlap))}")

    for skill in sorted((set(expected) | set(unexpected)) - skills):
        errors.append(f"{prefix}: unknown skill: {skill}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cases", nargs="?", type=Path, default=DEFAULT_CASES)
    args = parser.parse_args()

    try:
        document = json.loads(args.cases.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"Missing activation cases file: {args.cases}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as error:
        print(f"Invalid JSON in {args.cases}: {error}", file=sys.stderr)
        return 1

    if not isinstance(document, dict):
        print("Activation cases document must be an object", file=sys.stderr)
        return 1
    if document.get("schema_version") != 1:
        print("schema_version must be 1", file=sys.stderr)
        return 1
    cases = document.get("cases")
    if not isinstance(cases, list) or not cases:
        print("cases must be a non-empty list", file=sys.stderr)
        return 1

    skills = known_skills(ROOT)
    routers = known_routers(ROOT)
    errors = [
        error
        for index, case in enumerate(cases)
        for error in validate_case(case, index, skills, routers)
    ]
    ids = [case.get("id") for case in cases if isinstance(case, dict) and isinstance(case.get("id"), str)]
    duplicates = sorted(case_id for case_id in set(ids) if ids.count(case_id) > 1)
    if duplicates:
        errors.append(f"duplicate case ids: {', '.join(duplicates)}")

    if errors:
        print("Activation fixture validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    covered = {
        skill
        for case in cases
        for skill in case["expected_skills"]
    }
    covered_routers = {case["expected_router"] for case in cases}
    missing_routers = routers - covered_routers
    missing_skills = skills - covered
    if missing_routers:
        print(
            f"Activation fixtures do not cover routers: {', '.join(sorted(missing_routers))}",
            file=sys.stderr,
        )
        return 1
    if missing_skills:
        print(
            f"Activation fixtures do not cover workflows: {', '.join(sorted(missing_skills))}",
            file=sys.stderr,
        )
        return 1
    print(
        f"OK   {len(cases)} activation cases cover "
        f"{len(covered_routers)} routers and {len(covered)} workflows"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
