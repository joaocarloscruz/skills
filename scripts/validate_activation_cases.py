#!/usr/bin/env python3
"""Validate the catalog's skill-activation regression fixtures."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
try:
    from .catalog_utils import catalog_membership, strict_json_loads
except ImportError:
    from catalog_utils import catalog_membership, strict_json_loads


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
    return set(catalog_membership(root))


def validate_case(
    case: object,
    index: int,
    skills: set[str],
    routers: set[str],
    membership: dict[str, set[str]] | None = None,
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
    if expected_router is not None and (not isinstance(expected_router, str) or expected_router not in routers):
        errors.append(f"{prefix}: expected_router must name a known router or be null for no match")

    expected = case.get("expected_skills")
    unexpected = case.get("unexpected_skills")
    if not isinstance(expected, list) or not all(isinstance(item, str) for item in expected):
        errors.append(f"{prefix}: expected_skills must be a list of skill names")
        expected = []
    if not isinstance(unexpected, list) or not unexpected or not all(isinstance(item, str) for item in unexpected):
        errors.append(f"{prefix}: unexpected_skills must be a non-empty list of skill names")
        unexpected = []

    if expected_router is None and expected:
        errors.append(f"{prefix}: no-match cases must have no expected skills")
    elif expected_router is not None and not expected:
        errors.append(f"{prefix}: a matched router requires expected skills")
    if membership is not None and isinstance(expected_router, str) and expected_router in membership:
        outside = set(expected) - membership[expected_router]
        if outside:
            errors.append(f"{prefix}: expected skills are not members of {expected_router}: {', '.join(sorted(outside))}")

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
        document = strict_json_loads(args.cases.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as error:
        print(f"Cannot read activation cases {args.cases}: {error}", file=sys.stderr)
        return 1

    if not isinstance(document, dict):
        print("Activation cases document must be an object", file=sys.stderr)
        return 1
    if set(document) != {"schema_version", "cases"}:
        print("Activation cases document must contain only schema_version and cases", file=sys.stderr)
        return 1
    if type(document.get("schema_version")) is not int or document["schema_version"] != 1:
        print("schema_version must be 1", file=sys.stderr)
        return 1
    cases = document.get("cases")
    if not isinstance(cases, list) or not cases:
        print("cases must be a non-empty list", file=sys.stderr)
        return 1

    try:
        membership = catalog_membership(ROOT)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"Invalid catalog membership: {error}", file=sys.stderr)
        return 1
    skills = set().union(*membership.values())
    routers = set(membership)
    errors = [
        error
        for index, case in enumerate(cases)
        for error in validate_case(case, index, skills, routers, membership)
    ]
    ids = [case.get("id") for case in cases if isinstance(case, dict) and isinstance(case.get("id"), str)]
    duplicates = sorted(case_id for case_id in set(ids) if ids.count(case_id) > 1)
    if duplicates:
        errors.append(f"duplicate case ids: {', '.join(duplicates)}")
    prompts = [case["prompt"].strip().casefold() for case in cases if isinstance(case, dict) and isinstance(case.get("prompt"), str)]
    if len(prompts) != len(set(prompts)):
        errors.append("duplicate activation prompts")
    if not any(isinstance(case, dict) and case.get("expected_router") is None and case.get("expected_skills") == [] for case in cases):
        errors.append("activation fixtures must include no-match requests to check overactivation")

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
    covered_routers = {case["expected_router"] for case in cases if case["expected_router"] is not None}
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
