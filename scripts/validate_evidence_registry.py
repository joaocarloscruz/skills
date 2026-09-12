#!/usr/bin/env python3
"""Validate provenance and recorded evaluations without inferring skill effectiveness."""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from datetime import date
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
REVISION_RE = re.compile(r"^[0-9a-f]{40}$")
PACKAGE_REVISION_RE = re.compile(r"^(?:[0-9a-f]{40}|sha256:[0-9a-f]{64}|none)$")
DEFAULTS = {"provenance": "original-synthesis", "structural_validation": "passed",
            "activation_evidence": "fixture-only", "behavioral_evidence": "unvalidated"}
EVIDENCE = {"vendor-maintained-no-public-per-skill-benchmark",
            "benchmark-dataset-member-revision-result-unverified",
            "maintainer-with-evaluation-assets-no-verified-uplift",
            "limited-comparative-evaluation-revision-unverified"}


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def relative_path(value):
    return (nonempty(value) and not PurePosixPath(value).is_absolute() and "\\" not in value and ":" not in value
            and not any(ord(c) < 32 for c in value)
            and all(part not in ("", ".", "..") for part in value.split("/")))


def https_url(value):
    if not isinstance(value, str) or any(c.isspace() or ord(c) < 32 for c in value):
        return False
    try:
        parsed = urlsplit(value)
        parsed.port  # Validate malformed and out-of-range ports too.
        return parsed.scheme == "https" and bool(parsed.hostname) and parsed.username is None and parsed.password is None
    except ValueError:
        return False


def load_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f"duplicate JSON field: {key}")
            result[key] = value
        return result

    def invalid_constant(value):
        raise ValueError(f"invalid JSON number: {value}")

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs, parse_constant=invalid_constant)


def validate(document, root=ROOT):
    if not isinstance(document, dict):
        return ["registry must be an object"]
    errors = []
    required = {"schema_version", "reviewed_on", "catalog_inspiration", "classification_defaults", "external_sources", "skills"}
    if set(document) != required:
        errors.append("registry must contain exactly the documented top-level fields")
    if type(document.get("schema_version")) is not int or document.get("schema_version") != 2:
        errors.append("schema_version must be 2")
    try:
        reviewed = document.get("reviewed_on")
        if not isinstance(reviewed, str) or date.fromisoformat(reviewed).isoformat() != reviewed:
            raise ValueError()
    except ValueError:
        errors.append("reviewed_on must be a real date in YYYY-MM-DD format")
    if document.get("catalog_inspiration") != "SOURCES.md":
        errors.append("catalog_inspiration must reference SOURCES.md")
    if document.get("classification_defaults") != DEFAULTS:
        errors.append("defaults must retain conservative states; record measured results per skill")
    sources = document.get("external_sources")
    if not isinstance(sources, dict):
        errors.append("external_sources must be an object")
        sources = {}
    for source, metadata in sources.items():
        if not nonempty(source):
            errors.append("source names must be non-empty strings")
        if not isinstance(metadata, dict):
            errors.append(f"source {source}: metadata must be an object")
            continue
        required_source = {"repository", "reviewed_revision"}
        if not required_source <= set(metadata) or set(metadata) - required_source - {"license", "notes"}:
            errors.append(f"source {source}: invalid metadata fields")
        repository = metadata.get("repository")
        if not isinstance(repository, str) or not re.fullmatch(r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
            errors.append(f"source {source}: use an exact GitHub HTTPS repository URL")
        revision = metadata.get("reviewed_revision")
        if not isinstance(revision, str) or not REVISION_RE.fullmatch(revision):
            errors.append(f"source {source}: reviewed_revision must be a full Git SHA")
        for key in ("license", "notes"):
            if key in metadata and not nonempty(metadata[key]):
                errors.append(f"source {source}: {key} must be non-empty")
    skills = document.get("skills")
    if not isinstance(skills, dict):
        errors.append("skills must be an object")
        skills = {}
    expected = {p.parent.name for p in (root / "library").glob("*/SKILL.md")}
    if set(skills) != expected:
        errors.append(f"skill coverage mismatch: missing={sorted(expected - set(skills))}, unknown={sorted(set(skills) - expected, key=str)}")
    for skill, metadata in skills.items():
        if not isinstance(metadata, dict):
            errors.append(f"skill {skill}: metadata must be an object")
            continue
        if set(metadata) - {"external_candidates", "behavioral_evidence", "evaluations"}:
            errors.append(f"skill {skill}: unexpected metadata fields")
        candidates = metadata.get("external_candidates", [])
        if not isinstance(candidates, list):
            errors.append(f"skill {skill}: external_candidates must be a list")
            candidates = []
        identities = set()
        for candidate in candidates:
            prefix = f"skill {skill} candidate"
            fields = {"source", "path", "relationship", "evidence"}
            if not isinstance(candidate, dict) or not fields <= set(candidate) or set(candidate) - fields - {"assessment", "citations"}:
                errors.append(f"{prefix}: invalid fields")
                continue
            source, path = candidate["source"], candidate["path"]
            if not isinstance(source, str) or source not in sources:
                errors.append(f"{prefix}: unknown source")
            if not relative_path(path):
                errors.append(f"{prefix}: path must be canonical and repository-relative")
            if candidate["relationship"] not in ("scope-overlap", "tool-specific-specialization"):
                errors.append(f"{prefix}: unsupported relationship")
            if not isinstance(candidate["evidence"], str) or candidate["evidence"] not in EVIDENCE:
                errors.append(f"{prefix}: unsupported evidence status")
            if "assessment" in candidate and not nonempty(candidate["assessment"]):
                errors.append(f"{prefix}: assessment must be non-empty")
            citations = candidate.get("citations", [])
            if not isinstance(citations, list) or not all(https_url(c) for c in citations):
                errors.append(f"{prefix}: citations must be HTTPS URLs")
            if isinstance(source, str) and isinstance(path, str):
                identity = (source, path)
                if identity in identities:
                    errors.append(f"{prefix}: duplicate source/path")
                identities.add(identity)
        state = metadata.get("behavioral_evidence", "unvalidated")
        if state not in ("unvalidated", "smoke-tested", "paired-evaluated"):
            errors.append(f"skill {skill}: unsupported behavioral evidence state")
        evaluations = metadata.get("evaluations", [])
        if not isinstance(evaluations, list):
            errors.append(f"skill {skill}: evaluations must be a list")
            evaluations = []
        if state != "unvalidated" and not evaluations:
            errors.append(f"skill {skill}: measured state requires evaluation artifacts")
        seen = set()
        for evaluation in evaluations:
            if not isinstance(evaluation, dict) or set(evaluation) != {"path", "condition"}:
                errors.append(f"skill {skill}: evaluation needs path and condition")
                continue
            path, condition = evaluation["path"], evaluation["condition"]
            if not relative_path(path) or not path.startswith("evidence/runs/") or not nonempty(condition):
                errors.append(f"skill {skill}: invalid evaluation reference")
                continue
            if (path, condition) in seen:
                errors.append(f"skill {skill}: duplicate evaluation reference")
            seen.add((path, condition))
            target = root / path
            try:
                current = root
                for part in ("", *PurePosixPath(path).parts):
                    current = current / part
                    if current.is_symlink() or (hasattr(current, "is_junction") and current.is_junction()):
                        raise ValueError("evaluation path must not use a symlink or junction")
                if not target.resolve().is_relative_to((root / "evidence/runs").resolve()):
                    raise ValueError("evaluation path escapes runs directory")
                # Load trusted repository code, never code supplied by an alternate evidence root.
                spec = importlib.util.spec_from_file_location("evidence_compare_runs", ROOT / "library/evaluate-ai-output/scripts/compare_runs.py")
                if spec is None or spec.loader is None:
                    raise ValueError("comparison helper unavailable")
                helper = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(helper)
                run = helper.load_experiment(target)
                if run["kind"] != "behavioral" or condition not in run["conditions"]:
                    raise ValueError("evidence requires a behavioral run and an existing condition")
                if run["conditions"][condition]["skill_revision"] == "none":
                    raise ValueError("evidence must identify the evaluated skill revision")
                if any(not PACKAGE_REVISION_RE.fullmatch(c["skill_revision"]) for c in run["conditions"].values()):
                    raise ValueError("record exact Git SHA or sha256 package revision")
            except (OSError, ValueError, TypeError, RuntimeError) as error:
                errors.append(f"skill {skill}: invalid evaluation {path}: {error}")
    return errors


def main():
    try:
        document = load_json(ROOT / "evidence/skills.json")
        errors = validate(document)
    except (OSError, ValueError) as error:
        errors = [str(error)]
    if errors:
        print("Evidence registry validation failed:\n" + "\n".join(f"- {e}" for e in errors), file=sys.stderr)
        return 1
    count = sum(len(m.get("external_candidates", [])) for m in document["skills"].values())
    print(f"OK   evidence registry classifies {len(document['skills'])} skills and records {count} external candidates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
