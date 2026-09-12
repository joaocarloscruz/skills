"""Shared catalog structure; category indexes remain the membership source of truth."""

from __future__ import annotations

import re
import json
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ENTRY_RE = re.compile(r"^- \[([a-z0-9-]+)\]\(\.\./\.\./library/([a-z0-9-]+)/\) - (\S.*)$")
ROUTER_CONFIG = {
    "planning-discovery": ("planning", "Route research, codebase analysis, specifications, implementation planning, or work breakdown."),
    "software-engineering": ("engineering", "Route domain modeling, APIs, database changes, implementation, TDD, migrations, refactoring, or Git conflicts."),
    "frontend": ("frontend", "Route web interface design, implementation, design systems, accessibility review, or browser testing."),
    "quality-security": ("quality-security", "Route debugging, test strategy, AI evaluation, CI diagnosis, code review, security review, interface testing, or skill-catalog audits."),
    "operations": ("operations", "Route dependency audits, performance work, software releases, or incident response."),
    "collaboration": ("collaboration", "Route technical handoffs, issue triage, or documentation work."),
    "ai-engineering": ("ai-engineering", "Route MCP server work, agent-tool design, or retrieval-augmented generation evaluation."),
    "data": ("data", "Route structured dataset analysis, analytical SQL, or batch and streaming pipeline design."),
    "platform-engineering": ("platform", "Route containerization, observability, or continuous-integration pipeline work."),
}


def strict_json_loads(text: str) -> object:
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(text, object_pairs_hook=pairs)


def is_link(path: Path) -> bool:
    """Include Windows junctions, which is_symlink alone does not detect."""
    return path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction())


def category_entries(root: Path, category: str) -> list[tuple[str, str]]:
    path = root / "catalog" / category / "README.md"
    if is_link(path) or is_link(path.parent):
        raise ValueError(f"catalog paths must not be symlinks or junctions: {path}")
    entries = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        match = ENTRY_RE.fullmatch(line)
        if match:
            label, target, summary = match.groups()
            if label != target:
                raise ValueError(f"{path}:{number}: link label and library target differ")
            entries.append((label, summary))
        elif "library/" in line or line.startswith("- ["):
            raise ValueError(f"{path}:{number}: malformed catalog entry")
    if not entries:
        raise ValueError(f"no library entries found in {path}")
    return entries


def catalog_membership(root: Path) -> dict[str, set[str]]:
    """Validate a complete one-category-per-workflow catalog and return router membership."""
    for directory in (root / "library", root / "catalog"):
        if is_link(directory) or not directory.is_dir():
            raise ValueError(f"required real directory: {directory}")
    skills = set()
    for directory in (root / "library").iterdir():
        if is_link(directory):
            raise ValueError(f"library package must not be a symlink or junction: {directory}")
        if not directory.is_dir() or directory.name == "__pycache__":
            continue
        if not NAME_RE.fullmatch(directory.name) or len(directory.name) > 64:
            raise ValueError(f"invalid library package name: {directory.name}")
        if not (directory / "SKILL.md").is_file():
            raise ValueError(f"library package has no SKILL.md: {directory.name}")
        skills.add(directory.name)
    expected_categories = {category for category, _ in ROUTER_CONFIG.values()}
    actual_categories = {path.name for path in (root / "catalog").iterdir() if path.is_dir()}
    if actual_categories != expected_categories:
        raise ValueError(f"catalog category mismatch: missing={sorted(expected_categories - actual_categories)}, extra={sorted(actual_categories - expected_categories)}")
    membership = {}
    seen = set()
    for router, (category, _) in ROUTER_CONFIG.items():
        names = [name for name, _ in category_entries(root, category)]
        duplicates = seen.intersection(names) | {name for name in names if names.count(name) > 1}
        if duplicates:
            raise ValueError(f"workflows appear more than once in catalog: {', '.join(sorted(duplicates))}")
        seen.update(names)
        membership[router] = set(names)
    if seen != skills:
        raise ValueError(f"catalog workflow mismatch: uncategorized={sorted(skills - seen)}, unknown={sorted(seen - skills)}")
    return membership
