#!/usr/bin/env python3
"""Audit an Agent Skills catalog using only the Python standard library."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from itertools import combinations
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
TOP_KEY_RE = re.compile(r"^([A-Za-z0-9_-]+):\s*(.*)$")
IGNORED_DIRS = {".git", ".hg", ".svn", "node_modules", "__pycache__"}
TEXT_EXTENSIONS = {".md", ".py", ".sh", ".ps1", ".js", ".ts", ".rb"}
STOPWORDS = {
    "a", "an", "and", "as", "for", "from", "in", "into", "of", "on",
    "or", "the", "to", "use", "using", "when", "with", "without", "asked",
    "create", "improve", "review", "design", "build", "write", "software",
}
RISK_PATTERNS = {
    "download piped to a shell": re.compile(r"(?:curl|wget)[^\n|]*\|\s*(?:ba)?sh\b", re.I),
    "force push": re.compile(r"\bgit\s+push\b[^\n]*--force\b", re.I),
    "destructive Git reset": re.compile(r"\bgit\s+reset\s+--hard\b", re.I),
    "recursive forced delete": re.compile(r"\brm\s+-[a-z]*r[a-z]*f\b", re.I),
    "world-writable permission": re.compile(r"\bchmod\s+777\b", re.I),
    "instruction override language": re.compile(r"ignore\s+(?:all|any|the)\s+previous\s+instructions", re.I),
    "unbounded allowed tools": re.compile(r"allowed[-_]tools\s*:\s*[\"']?\*[\"']?", re.I),
}


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    path: str
    message: str


def discover_skill_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("SKILL.md")
        if not any(part in IGNORED_DIRS for part in path.parts)
    )


def parse_frontmatter(path: Path) -> tuple[dict[str, str], list[str]]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return {}, ["frontmatter must start on line 1"]
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}, ["frontmatter is missing its closing delimiter"]

    metadata: dict[str, str] = {}
    errors: list[str] = []
    i = 1
    while i < end:
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#") or line[:1].isspace():
            i += 1
            continue
        match = TOP_KEY_RE.match(line)
        if not match:
            errors.append(f"invalid top-level frontmatter line: {line!r}")
            i += 1
            continue
        key, value = match.groups()
        if key in metadata:
            errors.append(f"duplicate frontmatter key: {key}")
        if value in {">", "|"}:
            block: list[str] = []
            i += 1
            while i < end and (not lines[i].strip() or lines[i][:1].isspace()):
                block.append(lines[i].strip())
                i += 1
            value = " ".join(part for part in block if part)
            metadata[key] = value
            continue
        metadata[key] = value.strip().strip("\"'")
        i += 1
    return metadata, errors


def relative(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def tokenize(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if len(token) > 2 and token not in STOPWORDS
    }


def audit(root: Path, overlap_threshold: float) -> list[Finding]:
    findings: list[Finding] = []
    skill_files = discover_skill_files(root)
    if not skill_files:
        return [Finding("error", "no-skills", ".", "no SKILL.md files found")]

    by_name: dict[str, list[Path]] = defaultdict(list)
    descriptions: dict[str, tuple[Path, str]] = {}

    for skill_file in skill_files:
        skill_dir = skill_file.parent
        skill_path = relative(root, skill_file)
        text = skill_file.read_text(encoding="utf-8")
        metadata, errors = parse_frontmatter(skill_file)
        for error in errors:
            findings.append(Finding("error", "frontmatter", skill_path, error))

        name = metadata.get("name", "")
        description = metadata.get("description", "")
        if not name:
            findings.append(Finding("error", "missing-name", skill_path, "missing name"))
        else:
            by_name[name].append(skill_file)
            if not NAME_RE.fullmatch(name):
                findings.append(Finding("error", "invalid-name", skill_path, "name must be lowercase kebab-case"))
            if name != skill_dir.name:
                findings.append(Finding("error", "folder-mismatch", skill_path, f"name {name!r} does not match folder {skill_dir.name!r}"))
        if not description:
            findings.append(Finding("error", "missing-description", skill_path, "missing description"))
        else:
            descriptions[skill_path] = (skill_file, description)
            if len(description) < 50:
                findings.append(Finding("warning", "short-description", skill_path, "description may not explain both capability and trigger"))
            if len(description) > 1024:
                findings.append(Finding("error", "long-description", skill_path, "description exceeds 1024 characters"))
        if len(text.splitlines()) > 500:
            findings.append(Finding("warning", "large-skill", skill_path, "SKILL.md exceeds 500 lines; consider progressive disclosure"))
        if len(text.encode("utf-8")) > 50_000:
            findings.append(Finding("warning", "large-skill-bytes", skill_path, "SKILL.md exceeds 50 KB"))

        for markdown in sorted(skill_dir.rglob("*.md")):
            markdown_text = markdown.read_text(encoding="utf-8")
            for raw_link in LINK_RE.findall(markdown_text):
                target_text = raw_link.strip().split("#", 1)[0].strip().strip("<>")
                if not target_text or re.match(r"^[a-z]+://|^mailto:", target_text, re.I):
                    continue
                target = (markdown.parent / target_text).resolve()
                if not target.exists():
                    findings.append(Finding("error", "broken-link", relative(root, markdown), f"missing relative target: {raw_link}"))

        for resource_name in ("scripts", "references"):
            resource_dir = skill_dir / resource_name
            if not resource_dir.exists():
                continue
            files = [
                path
                for path in resource_dir.rglob("*")
                if path.is_file()
                and not any(part in IGNORED_DIRS for part in path.parts)
            ]
            if not files:
                findings.append(Finding("warning", "empty-resource-dir", relative(root, resource_dir), "resource directory is empty"))
            for resource in files:
                resource_ref = resource.relative_to(skill_dir).as_posix()
                if resource_ref not in text:
                    findings.append(Finding("warning", "unreferenced-resource", relative(root, resource), "resource is not referenced from SKILL.md"))

        for candidate in skill_dir.rglob("*"):
            if not candidate.is_file() or candidate.suffix.lower() not in TEXT_EXTENSIONS:
                continue
            candidate_text = candidate.read_text(encoding="utf-8", errors="replace")
            for label, pattern in RISK_PATTERNS.items():
                if pattern.search(candidate_text):
                    findings.append(Finding("warning", "risky-instruction", relative(root, candidate), f"review heuristic match: {label}"))

    for name, paths in sorted(by_name.items()):
        if len(paths) > 1:
            locations = ", ".join(relative(root, path) for path in paths)
            findings.append(Finding("error", "duplicate-name", locations, f"duplicate skill name: {name}"))

    for (path_a, (_, desc_a)), (path_b, (_, desc_b)) in combinations(descriptions.items(), 2):
        tokens_a, tokens_b = tokenize(desc_a), tokenize(desc_b)
        union = tokens_a | tokens_b
        score = len(tokens_a & tokens_b) / len(union) if union else 0.0
        if score >= overlap_threshold:
            findings.append(Finding("warning", "description-overlap", f"{path_a} <-> {path_b}", f"description token overlap is {score:.0%}"))

    return sorted(findings, key=lambda item: ({"error": 0, "warning": 1}[item.severity], item.code, item.path))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="catalog or repository root")
    parser.add_argument("--overlap-threshold", type=float, default=0.45, help="Jaccard warning threshold from 0 to 1")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--fail-on-warning", action="store_true", help="return nonzero when warnings exist")
    args = parser.parse_args()
    if not 0 <= args.overlap_threshold <= 1:
        parser.error("--overlap-threshold must be between 0 and 1")

    root = Path(args.root).resolve()
    findings = audit(root, args.overlap_threshold)
    if args.json:
        print(json.dumps([asdict(finding) for finding in findings], indent=2))
    else:
        for finding in findings:
            print(f"{finding.severity.upper():7} {finding.code:22} {finding.path}: {finding.message}")
        errors = sum(finding.severity == "error" for finding in findings)
        warnings = sum(finding.severity == "warning" for finding in findings)
        print(f"Audited {len(discover_skill_files(root))} skills: {errors} errors, {warnings} warnings")

    has_error = any(finding.severity == "error" for finding in findings)
    has_warning = any(finding.severity == "warning" for finding in findings)
    return 1 if has_error or (args.fail_on_warning and has_warning) else 0


if __name__ == "__main__":
    raise SystemExit(main())
