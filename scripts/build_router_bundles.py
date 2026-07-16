#!/usr/bin/env python3
"""Build self-contained router skills from the canonical individual-skill library."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "library"
ROUTERS = ROOT / "skills"
CATALOG = ROOT / "catalog"
LINK_RE = re.compile(r"^- \[([a-z0-9-]+)\]\(\.\./\.\./library/[a-z0-9-]+/\) - (.+)$")
TEXT_SUFFIXES = {".md", ".py", ".ps1", ".json", ".yaml", ".yml", ".txt"}
IGNORED_RESOURCE_DIRS = {"__pycache__"}
IGNORED_RESOURCE_SUFFIXES = {".pyc", ".pyo"}

ROUTER_CONFIG = {
    "planning-discovery": (
        "planning",
        "Route research, codebase analysis, specifications, implementation planning, or work breakdown.",
    ),
    "software-engineering": (
        "engineering",
        "Route domain modeling, APIs, database changes, implementation, TDD, migrations, refactoring, or Git conflicts.",
    ),
    "frontend": (
        "frontend",
        "Route web interface design, implementation, design systems, accessibility review, or browser testing.",
    ),
    "quality-security": (
        "quality-security",
        "Route debugging, test strategy, AI evaluation, CI diagnosis, code review, security review, or interface testing.",
    ),
    "operations": (
        "operations",
        "Route dependency audits, performance work, software releases, or incident response.",
    ),
    "collaboration": (
        "collaboration",
        "Route technical handoffs, issue triage, or documentation work.",
    ),
    "ai-engineering": (
        "ai-engineering",
        "Route MCP server work, agent-tool design, or retrieval-augmented generation evaluation.",
    ),
    "data": (
        "data",
        "Route structured dataset analysis, analytical SQL, or batch and streaming pipeline design.",
    ),
    "platform-engineering": (
        "platform",
        "Route containerization, observability, or continuous-integration pipeline work.",
    ),
}


def parse_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", text, re.DOTALL)
    if not match:
        raise ValueError(f"invalid frontmatter: {path.relative_to(ROOT)}")
    metadata: dict[str, str] = {}
    for line in match.group(1).splitlines():
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip("\"'")
    return metadata, match.group(2).strip()


def category_entries(category: str) -> list[tuple[str, str]]:
    path = CATALOG / category / "README.md"
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = LINK_RE.match(line)
        if match:
            entries.append((match.group(1), match.group(2)))
    if not entries:
        raise ValueError(f"no library entries found in {path.relative_to(ROOT)}")
    return entries


def router_files(router: str, category: str, description: str) -> dict[Path, bytes]:
    entries = category_entries(category)
    rows = []
    files: dict[Path, bytes] = {}
    for skill, summary in entries:
        source = LIBRARY / skill / "SKILL.md"
        metadata, body = parse_frontmatter(source)
        if metadata.get("name") != skill:
            raise ValueError(f"skill name mismatch in {source.relative_to(ROOT)}")
        rows.append(f"| {summary} | [{skill}](references/{skill}/workflow.md) |")
        workflow_root = Path("references") / skill
        files[workflow_root / "workflow.md"] = (
            f"<!-- Generated from library/{skill}/SKILL.md; do not edit. -->\n\n{body}\n"
        ).encode()
        for bundled in sorted(source.parent.rglob("*")):
            if (
                bundled.is_file()
                and bundled != source
                and not any(part in IGNORED_RESOURCE_DIRS for part in bundled.parts)
                and bundled.suffix.lower() not in IGNORED_RESOURCE_SUFFIXES
            ):
                files[workflow_root / bundled.relative_to(source.parent)] = bundled.read_bytes()

    title = router.replace("-", " ").title()
    table = "\n".join(rows)
    files[Path("SKILL.md")] = f"""---
name: {router}
description: {description}
---

# {title}

1. Match the request to the most specific workflow below.
2. Read that workflow's referenced file completely before acting.
3. Use multiple workflows only when the request genuinely spans them; apply them in dependency order.
4. If no workflow fits, explain the gap instead of stretching an unrelated workflow.

| Request | Workflow |
| --- | --- |
{table}

Follow the selected workflow as binding process guidance. Preserve user authority and repository instructions when they are more specific.
""".encode()
    return files


def expected_files() -> dict[Path, bytes]:
    expected: dict[Path, bytes] = {}
    for router, (category, description) in ROUTER_CONFIG.items():
        for relative, content in router_files(router, category, description).items():
            expected[Path(router) / relative] = content
    return expected


def comparable_content(path: Path, content: bytes) -> bytes:
    """Normalize text line endings while preserving binary resource bytes."""
    if path.suffix.lower() in TEXT_SUFFIXES:
        return content.replace(b"\r\n", b"\n")
    return content


def check() -> int:
    expected = expected_files()
    actual = {
        path.relative_to(ROUTERS)
        for path in ROUTERS.rglob("*")
        if path.is_file()
    } if ROUTERS.exists() else set()
    failures = 0
    for relative, content in expected.items():
        path = ROUTERS / relative
        if not path.exists():
            print(f"MISSING {path.relative_to(ROOT)}")
            failures += 1
        elif comparable_content(path, path.read_bytes()) != comparable_content(path, content):
            print(f"STALE   {path.relative_to(ROOT)}")
            failures += 1
    for relative in sorted(actual - set(expected)):
        print(f"EXTRA   {(ROUTERS / relative).relative_to(ROOT)}")
        failures += 1
    if not failures:
        print(f"OK   {len(ROUTER_CONFIG)} router bundles are current")
    return 1 if failures else 0


def build() -> int:
    if ROUTERS.exists():
        shutil.rmtree(ROUTERS)
    for relative, content in expected_files().items():
        path = ROUTERS / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    print(f"Built {len(ROUTER_CONFIG)} router bundles in {ROUTERS.relative_to(ROOT)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail when generated bundles are stale")
    args = parser.parse_args()
    try:
        return check() if args.check else build()
    except (OSError, ValueError) as error:
        print(f"Router bundle error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
