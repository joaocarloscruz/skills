#!/usr/bin/env python3
"""Prepare a blinded metadata-selection exercise or score its recorded answers.

This does not invoke a model or test a client's native skill activation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from catalog_utils import ROUTER_CONFIG, category_entries, strict_json_loads


def prepare(root=ROOT):
    document = strict_json_loads((root / "tests/activation-cases.json").read_text(encoding="utf-8"))
    source = json.dumps(document, sort_keys=True, separators=(",", ":")).encode()
    cases = document["cases"]
    catalog = [{"router": router, "description": description,
                "workflows": [{"name": name, "description": summary}
                              for name, summary in category_entries(root, category)]}
               for router, (category, description) in ROUTER_CONFIG.items()]
    return {
        "kind": "metadata-selection-smoke",
        "dataset_revision": "sha256:" + hashlib.sha256(source).hexdigest(),
        "catalog_revision": "sha256:" + hashlib.sha256(
            json.dumps(catalog, sort_keys=True).encode()).hexdigest(),
        "instructions": (
            "For each independent request, select the single best router and minimal workflow set "
            "from this catalog. Use null and [] if none applies. Do not perform the request. "
            "Return an object with dataset_revision, catalog_revision, and selections; each selection "
            "has exactly id, router, workflows. Copy both revisions. Include each opaque case ID once. "
            "Use only this input; do not inspect expected answers or other repository files."
        ),
        "catalog": catalog,
        "cases": [{"id": f"case-{i:03d}", "prompt": c["prompt"]} for i, c in enumerate(cases, 1)],
    }


def score(document, root=ROOT):
    prepared = prepare(root)
    if not isinstance(document, dict) or set(document) != {"dataset_revision", "catalog_revision", "selections"}:
        raise ValueError("answers must contain dataset_revision, catalog_revision, selections")
    for field in ("dataset_revision", "catalog_revision"):
        if document[field] != prepared[field]:
            raise ValueError(f"{field} changed; score against the original snapshot")
    rows = document["selections"]
    if not isinstance(rows, list):
        raise ValueError("selections must be a list")
    choices = {}
    membership = {c["router"]: {w["name"] for w in c["workflows"]} for c in prepared["catalog"]}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"id", "router", "workflows"}:
            raise ValueError("each selection must contain id, router, workflows")
        ident, router, workflows = row["id"], row["router"], row["workflows"]
        if not isinstance(ident, str) or ident in choices:
            raise ValueError("invalid or duplicate case ID")
        if router is not None and (not isinstance(router, str) or router not in membership):
            raise ValueError("unknown router")
        if not isinstance(workflows, list) or not all(isinstance(w, str) for w in workflows):
            raise ValueError("workflows must be a list of names")
        if len(workflows) != len(set(workflows)) or not set(workflows) <= membership.get(router, set()):
            raise ValueError("unknown, duplicate, or wrong-router workflow")
        if (router is None) != (not workflows):
            raise ValueError("a router requires workflows; no match requires null and []")
        choices[ident] = row
    if set(choices) != {c["id"] for c in prepared["cases"]}:
        raise ValueError("retain every case exactly once, including no-match and failed selections")
    expected = strict_json_loads((root / "tests/activation-cases.json").read_text(encoding="utf-8"))["cases"]
    outcomes = []
    for index, case in enumerate(expected, 1):
        selected = choices[f"case-{index:03d}"]
        passed = selected["router"] == case["expected_router"] and set(selected["workflows"]) == set(case["expected_skills"])
        outcomes.append({"case": case["id"], "success": passed, "selected": selected,
                         "expected_router": case["expected_router"], "expected_workflows": case["expected_skills"]})
    return {"kind": prepared["kind"], "dataset_revision": prepared["dataset_revision"],
            "catalog_revision": prepared["catalog_revision"], "cases": len(outcomes),
            "passed": sum(r["success"] for r in outcomes), "outcomes": outcomes,
            "limitation": "Exact metadata-selection agreement on declared development cases; not native activation, held-out generalization, or task-outcome evidence."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("prepare", help="Print prompts and catalog metadata without expected answers")
    grading = commands.add_parser("score", help="Score a recorded selection file")
    grading.add_argument("answers", type=Path)
    args = parser.parse_args()
    try:
        result = prepare() if args.command == "prepare" else score(strict_json_loads(args.answers.read_text(encoding="utf-8")))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Invalid routing exercise: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
