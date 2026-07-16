#!/usr/bin/env python3
"""Validate the skill evidence and provenance registry."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "evidence" / "skills.json"
REVISION_RE = re.compile(r"^[0-9a-f]{40}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
EXPECTED_DEFAULTS = {
    "provenance": "original-synthesis",
    "structural_validation": "passed",
    "activation_evidence": "fixture-only",
    "behavioral_evidence": "unvalidated",
}
ALLOWED_RELATIONSHIPS = {"scope-overlap", "tool-specific-specialization"}
ALLOWED_EVIDENCE = {
    "vendor-maintained-no-public-per-skill-benchmark",
    "benchmark-dataset-member-revision-result-unverified",
}
CANDIDATE_FIELDS = {"source", "path", "relationship", "evidence"}


def known_skills() -> set[str]:
    return {path.parent.name for path in (ROOT / "library").glob("*/SKILL.md")}


def main() -> int:
    try:
        document = json.loads(REGISTRY.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"Missing evidence registry: {REGISTRY.relative_to(ROOT)}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as error:
        print(f"Invalid JSON in {REGISTRY.relative_to(ROOT)}: {error}", file=sys.stderr)
        return 1

    errors: list[str] = []
    if document.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if not isinstance(document.get("reviewed_on"), str) or not DATE_RE.fullmatch(document["reviewed_on"]):
        errors.append("reviewed_on must use YYYY-MM-DD")
    if document.get("catalog_inspiration") != "SOURCES.md":
        errors.append("catalog_inspiration must reference SOURCES.md")
    if document.get("classification_defaults") != EXPECTED_DEFAULTS:
        errors.append("classification_defaults must use the catalog's conservative evidence states")

    sources = document.get("external_sources")
    if not isinstance(sources, dict):
        errors.append("external_sources must be an object")
        sources = {}
    for source, metadata in sources.items():
        if not isinstance(metadata, dict):
            errors.append(f"external source {source!r} must be an object")
            continue
        repository = metadata.get("repository")
        revision = metadata.get("reviewed_revision")
        if not isinstance(repository, str) or not repository.startswith("https://github.com/"):
            errors.append(f"external source {source!r} must use a GitHub HTTPS repository URL")
        if not isinstance(revision, str) or not REVISION_RE.fullmatch(revision):
            errors.append(f"external source {source!r} must record a full Git revision")

    skills = document.get("skills")
    if not isinstance(skills, dict):
        errors.append("skills must be an object")
        skills = {}
    expected_skills = known_skills()
    missing = expected_skills - set(skills)
    unknown = set(skills) - expected_skills
    if missing:
        errors.append(f"missing skill classifications: {', '.join(sorted(missing))}")
    if unknown:
        errors.append(f"unknown skill classifications: {', '.join(sorted(unknown))}")

    for skill, metadata in skills.items():
        if not isinstance(metadata, dict):
            errors.append(f"skill {skill!r} must be an object")
            continue
        extra = set(metadata) - {"external_candidates"}
        if extra:
            errors.append(f"skill {skill!r} has unexpected fields: {', '.join(sorted(extra))}")
        candidates = metadata.get("external_candidates", [])
        if not isinstance(candidates, list):
            errors.append(f"skill {skill!r} external_candidates must be a list")
            continue
        identities: list[tuple[object, object]] = []
        for index, candidate in enumerate(candidates, start=1):
            prefix = f"skill {skill!r} candidate {index}"
            if not isinstance(candidate, dict):
                errors.append(f"{prefix} must be an object")
                continue
            missing_fields = CANDIDATE_FIELDS - set(candidate)
            extra_fields = set(candidate) - CANDIDATE_FIELDS
            if missing_fields:
                errors.append(f"{prefix} is missing fields: {', '.join(sorted(missing_fields))}")
            if extra_fields:
                errors.append(f"{prefix} has unexpected fields: {', '.join(sorted(extra_fields))}")
            if candidate.get("source") not in sources:
                errors.append(f"{prefix} references an unknown external source")
            path = candidate.get("path")
            if not isinstance(path, str) or not path or path.startswith(("/", "..")):
                errors.append(f"{prefix} must use a repository-relative path")
            if candidate.get("relationship") not in ALLOWED_RELATIONSHIPS:
                errors.append(f"{prefix} has an unsupported relationship")
            if candidate.get("evidence") not in ALLOWED_EVIDENCE:
                errors.append(f"{prefix} has an unsupported evidence status")
            identities.append((candidate.get("source"), candidate.get("path")))
        if len(identities) != len(set(identities)):
            errors.append(f"skill {skill!r} contains duplicate external candidates")

    if errors:
        print("Evidence registry validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    candidate_count = sum(
        len(metadata.get("external_candidates", []))
        for metadata in skills.values()
    )
    print(
        f"OK   evidence registry classifies {len(skills)} skills and records "
        f"{candidate_count} external candidates"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
