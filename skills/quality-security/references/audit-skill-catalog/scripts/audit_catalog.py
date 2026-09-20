#!/usr/bin/env python3
"""Audit an Agent Skills catalog using only the Python standard library."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from itertools import combinations
from pathlib import Path
from urllib.parse import unquote, urlsplit

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
CODE_SPAN_RE = re.compile(r"(?<!`)(`+)(?!`)(.*?)(?<!`)\1(?!`)", re.S)
RESOURCE_PATH_RE = re.compile(r"(?:\.\.?/)*(?:references|scripts|assets)/[^\s`<>]+")
TOP_KEY_RE = re.compile(r"^([A-Za-z0-9_-]+):\s*(.*)$")
ALLOWED_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
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


def is_link(path: Path) -> bool:
    return path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction())


def walk_paths(root: Path):
    """Never descend through symlinks/junctions, including ignored directories."""
    if is_link(root):
        yield root
        return
    for directory, dirs, files in os.walk(root, followlinks=False):
        parent = Path(directory)
        for name in dirs + files:
            path = parent / name
            if name not in IGNORED_DIRS or is_link(path):
                yield path
        dirs[:] = [name for name in dirs if name not in IGNORED_DIRS and not is_link(parent / name)]


def discover_skill_files(root: Path) -> list[Path]:
    return sorted(path for path in walk_paths(root) if path.name == "SKILL.md" and not is_link(path) and path.is_file())


def parse_scalar(value: str) -> str:
    """Read the documented YAML scalar subset without guessing at unsupported YAML."""
    value = value.strip()
    if value.startswith('"'):
        # YAML accepts JSON string syntax; reject extra data and non-strings.
        decoder = json.JSONDecoder()
        parsed, end = decoder.raw_decode(value)
        if value[end:].strip() and not value[end:].lstrip().startswith("#"):
            raise ValueError("unexpected text after quoted scalar")
        return parsed
    if value.startswith("'"):
        match = re.fullmatch(r"'((?:[^']|'')*)'\s*(?:#.*)?", value)
        if not match:
            raise ValueError("invalid single-quoted scalar")
        return match.group(1).replace("''", "'")
    value = re.split(r"\s+#", value, maxsplit=1)[0].rstrip()
    if value and (value[0] in "[{&*!?%@`|>" or ": " in value):
        raise ValueError("unsupported YAML syntax; use a quoted string or an indented block")
    if value.lower() in {"null", "~", "true", "false"} or re.fullmatch(r"[-+]?\d+(?:\.\d+)?", value):
        raise ValueError("frontmatter values must be strings; quote numeric/boolean values")
    return value


def parse_frontmatter(path: Path) -> tuple[dict[str, object], list[str]]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return {}, ["frontmatter must start on line 1"]
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}, ["frontmatter is missing its closing delimiter"]

    metadata: dict[str, object] = {}
    errors: list[str] = []
    if any("\t" in line[:len(line) - len(line.lstrip())] for line in lines[1:end]):
        errors.append("YAML indentation must use spaces, not tabs")
    i = 1
    while i < end:
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
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
        if key in ALLOWED_KEYS - {"metadata"} and value in {">", "|", ">-", "|-", ">+", "|+"}:
            block: list[str] = []
            i += 1
            while i < end and (not lines[i].strip() or lines[i][:1].isspace()):
                block.append(lines[i].strip())
                i += 1
            value = ("\n" if value.startswith("|") else " ").join(block).strip()
            metadata[key] = value
            continue
        if key == "metadata" and not value:
            mapping: dict[str, str] = {}
            i += 1
            while i < end and (not lines[i].strip() or lines[i][:1].isspace()):
                nested = lines[i]
                i += 1
                if not nested.strip() or nested.lstrip().startswith("#"):
                    continue
                match_nested = re.fullmatch(r"  ([A-Za-z0-9_.-]+):\s*(.*)", nested)
                if not match_nested:
                    errors.append("metadata must be a flat mapping indented with two spaces")
                    continue
                nested_key, nested_value = match_nested.groups()
                if nested_key in mapping:
                    errors.append(f"duplicate metadata key: {nested_key}")
                try:
                    mapping[nested_key] = parse_scalar(nested_value)
                except ValueError as error:
                    errors.append(f"metadata.{nested_key}: {error}")
            metadata[key] = mapping
            continue
        try:
            metadata[key] = parse_scalar(value)
        except ValueError as error:
            errors.append(f"{key}: {error}")
        i += 1
    unknown = set(metadata) - ALLOWED_KEYS
    if unknown:
        errors.append(f"unsupported frontmatter keys: {', '.join(sorted(unknown))}")
    if "metadata" in metadata and not isinstance(metadata["metadata"], dict):
        errors.append("metadata must be a mapping of string keys to string values")
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


def document_links(text: str) -> list[str]:
    # Standalone inline resource paths are instructions in this catalog. Commands
    # and sample Markdown inside code spans/fences are not document references.
    text = re.sub(r"(?ms)^\s*(`{3,}|~{3,}).*?^\s*\1\s*$", "", text)
    inline_paths: list[str] = []

    def read_span(match: re.Match) -> str:
        value = match.group(2).strip()
        if RESOURCE_PATH_RE.fullmatch(value):
            inline_paths.append(value)
        return ""

    text = CODE_SPAN_RE.sub(read_span, text)
    return (LINK_RE.findall(text)
            + re.findall(r"(?m)^\s{0,3}\[[^\]]+\]:\s*(\S+)", text)
            + inline_paths)


def local_target(document: Path, raw_link: str) -> Path | None:
    raw_link = raw_link.strip()
    if raw_link.startswith("<"):
        raw_link = raw_link[1:].split(">", 1)[0]
    else:
        raw_link = re.split(r'\s+["\']', raw_link, maxsplit=1)[0]
    if re.match(r"^[A-Za-z]:[\\/]", raw_link):
        return Path(raw_link)
    parsed = urlsplit(raw_link)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None
    return (document.parent / unquote(parsed.path)).resolve()


def reachable_documents(skill_file: Path) -> dict[Path, str]:
    """Return Markdown documents reachable from a skill's entrypoint."""
    package = skill_file.parent.resolve()
    pending = [skill_file]
    documents: dict[Path, str] = {}
    while pending:
        document = pending.pop()
        if document in documents or is_link(document) or not document.resolve().is_relative_to(package) or not document.is_file():
            continue
        text = document.read_text(encoding="utf-8")
        documents[document] = text
        for raw_link in document_links(text):
            target = local_target(document, raw_link)
            if target is not None and target.is_relative_to(package) and not is_link(target) and target.suffix.lower() == ".md" and target.is_file():
                pending.append(target)
    return documents


def resource_is_referenced(resource: Path, documents: dict[Path, str]) -> bool:
    resolved = resource.resolve()
    for document, text in documents.items():
        for raw_link in document_links(text):
            if local_target(document, raw_link) == resolved:
                return True
    return False


def audit(root: Path, overlap_threshold: float) -> list[Finding]:
    findings: list[Finding] = []
    for path in walk_paths(root):
        if is_link(path):
            findings.append(Finding("error", "unsafe-link", relative(root, path), "symlinks and junctions are not portable package resources"))
    skill_files = discover_skill_files(root)
    if not skill_files:
        return findings + [Finding("error", "no-skills", ".", "no SKILL.md files found")]

    by_name: dict[str, list[Path]] = defaultdict(list)
    descriptions: dict[str, tuple[Path, str]] = {}

    for skill_file in skill_files:
        skill_dir = skill_file.parent
        skill_path = relative(root, skill_file)
        try:
            text = skill_file.read_text(encoding="utf-8")
            documents = reachable_documents(skill_file)
            metadata, errors = parse_frontmatter(skill_file)
        except (OSError, UnicodeError, ValueError) as error:
            findings.append(Finding("error", "unreadable-skill", skill_path, str(error)))
            continue
        for error in errors:
            findings.append(Finding("error", "frontmatter", skill_path, error))

        name = metadata.get("name", "")
        description = metadata.get("description", "")
        if not name:
            findings.append(Finding("error", "missing-name", skill_path, "missing name"))
        else:
            by_name[name].append(skill_file)
            if len(name) > 64 or not NAME_RE.fullmatch(name):
                findings.append(Finding("error", "invalid-name", skill_path, "name must be 1-64 lowercase kebab-case characters"))
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
        compatibility = metadata.get("compatibility")
        if compatibility is not None and not 1 <= len(compatibility) <= 500:
            findings.append(Finding("error", "compatibility-length", skill_path, "compatibility must be 1-500 characters"))
        if len(text.splitlines()) > 500:
            findings.append(Finding("warning", "large-skill", skill_path, "SKILL.md exceeds 500 lines; consider progressive disclosure"))
        if len(text.encode("utf-8")) > 50_000:
            findings.append(Finding("warning", "large-skill-bytes", skill_path, "SKILL.md exceeds 50 KB"))

        for markdown in sorted(path for path in walk_paths(skill_dir) if path.suffix.lower() == ".md" and path.is_file() and not is_link(path)):
            try:
                markdown_text = markdown.read_text(encoding="utf-8")
            except (OSError, UnicodeError) as error:
                findings.append(Finding("error", "unreadable-resource", relative(root, markdown), str(error)))
                continue
            for raw_link in document_links(markdown_text):
                try:
                    target = local_target(markdown, raw_link)
                except ValueError as error:
                    findings.append(Finding("error", "invalid-link", relative(root, markdown), str(error)))
                    continue
                if target is None:
                    continue
                if not target.resolve().is_relative_to(skill_dir.resolve()):
                    findings.append(Finding("error", "escaping-link", relative(root, markdown), f"target leaves the portable skill package: {raw_link}"))
                elif not target.exists():
                    findings.append(Finding("error", "broken-link", relative(root, markdown), f"missing relative target: {raw_link}"))

        for resource_name in ("scripts", "references"):
            resource_dir = skill_dir / resource_name
            if not resource_dir.exists():
                continue
            files = [
                path
                for path in walk_paths(resource_dir)
                if path.is_file()
                and not is_link(path)
                and not any(part in IGNORED_DIRS for part in path.parts)
            ]
            if not files:
                findings.append(Finding("warning", "empty-resource-dir", relative(root, resource_dir), "resource directory is empty"))
            for resource in files:
                if not resource_is_referenced(resource, documents):
                    findings.append(Finding("warning", "unreferenced-resource", relative(root, resource), "resource is not referenced from SKILL.md"))

        for candidate in walk_paths(skill_dir):
            if is_link(candidate) or not candidate.is_file() or candidate.suffix.lower() not in TEXT_EXTENSIONS:
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
    try:
        findings = audit(root, args.overlap_threshold)
    except (OSError, UnicodeError, ValueError) as error:
        findings = [Finding("error", "audit-input", str(root), str(error))]
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
