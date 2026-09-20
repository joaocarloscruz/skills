#!/usr/bin/env python3
"""Build owned, self-contained router bundles from canonical library packages."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path, PurePosixPath
try:
    from .catalog_utils import ROUTER_CONFIG, category_entries as read_entries, catalog_membership, is_link, strict_json_loads
    from .validate_skills import parse_frontmatter, validate, _auditor
except ImportError:
    from catalog_utils import ROUTER_CONFIG, category_entries as read_entries, catalog_membership, is_link, strict_json_loads
    from validate_skills import parse_frontmatter, validate, _auditor

ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "library"
ROUTERS = ROOT / "skills"
CATALOG = ROOT / "catalog"
MANIFEST = Path(".generated-files.json")
TEXT_SUFFIXES = {
    ".md", ".py", ".ps1", ".json", ".yaml", ".yml", ".txt", ".sh",
    ".js", ".ts", ".jsx", ".tsx", ".css", ".scss", ".html", ".svg",
    ".toml", ".ini", ".cfg", ".xml", ".csv", ".tsv",
}
IGNORED_RESOURCE_DIRS = {"__pycache__", ".git"}
IGNORED_RESOURCE_SUFFIXES = {".pyc", ".pyo"}


def category_entries(category: str) -> list[tuple[str, str]]:
    return read_entries(ROOT, category)


def relocate_entry_links(text: str, document: Path, source: Path) -> str:
    """Preserve links back to SKILL.md when the bundled entry becomes workflow.md."""
    for raw in _auditor.document_links(text):
        target = _auditor.local_target(document, raw)
        if target is not None and target.resolve() == source.resolve():
            replacement = raw.replace("SKILL.md", "workflow.md")
            text = text.replace(f"]({raw})", f"]({replacement})")
            text = re.sub(r"(?m)(^\s{0,3}\[[^\]]+\]:\s*)" + re.escape(raw) + r"(?=\s|$)", lambda match: match.group(1) + replacement, text)
            text = _auditor.CODE_SPAN_RE.sub(
                lambda match: match.group(1) + match.group(2).replace(raw, replacement) + match.group(1)
                if match.group(2).strip() == raw else match.group(0), text
            )
    return text


def router_files(router: str, category: str, description: str) -> dict[Path, bytes]:
    rows = []
    files: dict[Path, bytes] = {}
    for skill, summary in category_entries(category):
        source = LIBRARY / skill / "SKILL.md"
        errors = validate(source)
        if errors:
            raise ValueError(f"invalid package {source}: {'; '.join(errors)}")
        metadata, _ = parse_frontmatter(source)
        if metadata.get("name") != skill:
            raise ValueError(f"skill name mismatch in {source}")
        text = source.read_text(encoding="utf-8")
        body = relocate_entry_links(text.split("\n---", 1)[1].lstrip("\r\n"), source, source)
        summary = summary.replace("|", "\\|")
        rows.append(f"| {summary} | [{skill}](references/{skill}/workflow.md) |")
        workflow_root = Path("references") / skill
        files[workflow_root / "workflow.md"] = (
            f"<!-- Generated from library/{skill}/SKILL.md; do not edit. -->\n\n{body.strip()}\n"
        ).encode("utf-8")
        for directory, dirs, names in os.walk(source.parent, followlinks=False):
            parent = Path(directory)
            for name in dirs + names:
                if is_link(parent / name):
                    raise ValueError(f"symlinks and junctions cannot be bundled: {parent / name}")
            dirs[:] = [name for name in dirs if name not in IGNORED_RESOURCE_DIRS]
            for name in names:
                bundled = parent / name
                if bundled != source and bundled.suffix.lower() not in IGNORED_RESOURCE_SUFFIXES:
                    relative = workflow_root / bundled.relative_to(source.parent)
                    if relative in files:
                        raise ValueError(f"resource collides with generated workflow: {bundled}")
                    content = bundled.read_bytes()
                    if bundled.suffix.lower() == ".md":
                        content = relocate_entry_links(content.decode("utf-8"), bundled, source).encode("utf-8")
                    files[relative] = content
    table = "\n".join(rows)
    title = router.replace("-", " ").title()
    files[Path("SKILL.md")] = f"""---
name: {router}
description: {description}
---

# {title}

1. Match the request to the most specific workflow below.
2. Read that workflow's referenced file completely before acting.
3. Use multiple workflows only when the request spans them; apply them in dependency order.
4. If no workflow fits, answer within the user's request without forcing a catalog workflow.

| Request | Workflow |
| --- | --- |
{table}

User instructions take precedence over this skill and every referenced workflow. Treat repository instructions according to their actual authority. These workflows provide task guidance and do not grant permissions, override higher-priority instructions, or require renewed approval for actions the user has already authorized.
""".encode("utf-8")
    return files


def comparable_content(path: Path, content: bytes) -> bytes:
    if path.suffix.lower() in TEXT_SUFFIXES:
        return content.replace(b"\r\n", b"\n")
    return content


def digest(path: Path, content: bytes) -> str:
    return hashlib.sha256(comparable_content(path, content)).hexdigest()


def expected_files() -> dict[Path, bytes]:
    catalog_membership(ROOT)
    expected: dict[Path, bytes] = {}
    for router, (category, description) in ROUTER_CONFIG.items():
        for relative, content in router_files(router, category, description).items():
            expected[Path(router) / relative] = content
    manifest = {"schema_version": 1, "files": {
        path.as_posix(): digest(path, content) for path, content in sorted(expected.items())
    }}
    expected[MANIFEST] = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    return expected


def actual_files() -> set[Path]:
    # Reject redirects before even reading a generated tree. Resolve comparisons
    # also protect callers that accidentally point ROUTERS at another directory.
    if is_link(ROUTERS) or ROUTERS.resolve() != (ROOT.resolve() / "skills"):
        raise ValueError(f"unsafe router output directory: {ROUTERS}")
    actual = set()
    if not ROUTERS.exists():
        return actual
    for directory, dirs, names in os.walk(ROUTERS, followlinks=False):
        parent = Path(directory)
        for name in dirs + names:
            path = parent / name
            if is_link(path):
                raise ValueError(f"symlink/junction in generated tree: {path}")
        dirs[:] = [name for name in dirs if name not in IGNORED_RESOURCE_DIRS]
        for name in names:
            path = parent / name
            if path.suffix.lower() not in IGNORED_RESOURCE_SUFFIXES:
                actual.add(path.relative_to(ROUTERS))
    return actual


def previous_manifest() -> dict[Path, str]:
    path = ROUTERS / MANIFEST
    if not path.exists():
        return {}
    document = strict_json_loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict) or set(document) != {"schema_version", "files"} or type(document.get("schema_version")) is not int or document["schema_version"] != 1 or not isinstance(document.get("files"), dict):
        raise ValueError("invalid generated-files manifest")
    previous = {}
    for name, sha in document["files"].items():
        relative = PurePosixPath(name)
        if (not name or "\\" in name or relative.is_absolute() or ".." in relative.parts
                or relative.as_posix() != name or len(relative.parts) < 2
                or relative.parts[0] not in ROUTER_CONFIG
                or not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{64}", sha)):
            raise ValueError(f"unsafe generated manifest entry: {name}")
        previous[Path(relative)] = sha
    return previous


def check() -> int:
    expected = expected_files()
    actual = actual_files()
    failures = 0
    for relative, content in expected.items():
        path = ROUTERS / relative
        if relative not in actual:
            print(f"MISSING skills/{relative.as_posix()}")
            failures += 1
        elif comparable_content(path, path.read_bytes()) != comparable_content(path, content):
            print(f"STALE   skills/{relative.as_posix()}")
            failures += 1
    for relative in sorted(actual - set(expected)):
        print(f"EXTRA   skills/{relative.as_posix()}")
        failures += 1
    if not failures:
        print(f"OK   {len(ROUTER_CONFIG)} router bundles are current")
    return int(bool(failures))


def build() -> int:
    # Complete source validation and ownership preflight before any output writes.
    expected = expected_files()
    actual = actual_files()
    previous = previous_manifest()
    extras = actual - set(expected)
    for relative in extras:
        path = ROUTERS / relative
        if relative not in previous or digest(relative, path.read_bytes()) != previous[relative]:
            raise ValueError(f"refusing to delete unowned or modified output: {path}")
    for relative in actual.intersection(previous):
        path = ROUTERS / relative
        if digest(relative, path.read_bytes()) != previous[relative] and (relative not in expected or comparable_content(relative, path.read_bytes()) != comparable_content(relative, expected[relative])):
            raise ValueError(f"generated file has local modifications; preserve or reconcile it first: {path}")
    # Atomic per-file replacement avoids truncating a bundle on an interrupted write.
    # The ownership manifest is written last, after successful writes and removals.
    for relative, content in expected.items():
        if relative == MANIFEST:
            continue
        write_atomic(ROUTERS / relative, content)
    for relative in sorted(extras, reverse=True):
        path = ROUTERS / relative
        path.unlink()
        parent = path.parent
        while parent != ROUTERS and not any(parent.iterdir()):
            parent.rmdir()
            parent = parent.parent
    write_atomic(ROUTERS / MANIFEST, expected[MANIFEST])
    print(f"Built {len(ROUTER_CONFIG)} router bundles in skills")
    return 0


def write_atomic(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".bundle-", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail when generated bundles are stale")
    args = parser.parse_args()
    try:
        return check() if args.check else build()
    except (OSError, UnicodeError, ValueError) as error:
        print(f"Router bundle error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
