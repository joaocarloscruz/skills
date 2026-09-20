#!/usr/bin/env python3
"""Prepare visible smoke tasks or grade an artifact in a bounded subprocess."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
TASKS = ("sql-grain", "pipeline-replay", "tool-write-recovery")


def prepare(task: str, destination: Path) -> None:
    if destination.exists():
        raise ValueError("destination already exists; use a fresh trial directory")
    shutil.copytree(ROOT / "tasks" / task, destination,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


def grade(task: str, directory: Path, timeout: float = 5) -> dict:
    artifact = directory.resolve() / ("query.sql" if task == "sql-grain" else "solution.py")
    if not artifact.is_file() or artifact.is_symlink():
        return {"task": task, "success": False, "error": "artifact is missing or is a symlink"}
    if artifact.stat().st_size > 65536:
        return {"task": task, "success": False, "error": "artifact exceeds 64 KiB"}
    with tempfile.TemporaryDirectory(prefix="skills-smoke-") as scratch:
        # Copy the exact submitted bytes, so imports and cwd never expose a trial.
        submitted = Path(scratch) / artifact.name
        submitted.write_bytes(artifact.read_bytes())
        try:
            process = subprocess.run(
                [sys.executable, "-I", "-S", str(ROOT / "private" / "grade.py"),
                 task, str(submitted)],
                cwd=scratch, capture_output=True, text=True, timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return {"task": task, "success": False, "error": "grader time limit exceeded"}
    if process.returncode != 0:
        return {"task": task, "success": False,
                "error": f"grader failed (exit {process.returncode})"}
    try:
        result = json.loads(process.stdout)
        if not isinstance(result, dict) or type(result.get("success")) is not bool:
            raise ValueError("invalid result")
        return result
    except (ValueError, json.JSONDecodeError):
        return {"task": task, "success": False,
                "error": f"grader failed (exit {process.returncode})"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "grade"))
    parser.add_argument("task", choices=TASKS)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    if args.action == "prepare":
        try:
            prepare(args.task, args.directory)
        except (OSError, ValueError) as error:
            parser.error(str(error))
        print(json.dumps({"task": args.task, "directory": str(args.directory.resolve())}))
        return 0
    result = grade(args.task, args.directory)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
