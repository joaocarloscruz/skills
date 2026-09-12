#!/usr/bin/env python3
"""Validate and compare paired skill trials; never invokes a model or runs artifacts."""

from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import sys
from pathlib import Path, PurePosixPath


class InvalidExperiment(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise InvalidExperiment(message)


def nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def number(value: object) -> bool:
    try:
        return type(value) in (int, float) and math.isfinite(value) and value >= 0
    except OverflowError:
        return False


def is_link(path: Path) -> bool:
    return path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction())


def artifact_relative_path(value: object) -> PurePosixPath:
    require(nonempty(value), "artifact must be a non-empty relative path")
    path = PurePosixPath(value)
    require(not path.is_absolute() and all(p not in ("", ".", "..") for p in value.split("/"))
            and "\\" not in value and ":" not in value and not any(ord(c) < 32 for c in value),
            f"unsafe artifact path: {value!r}")
    return path


def artifact_path(root: Path, value: object) -> Path:
    path = artifact_relative_path(value)
    target = root.joinpath(*path.parts)
    current = root
    require(not is_link(current), f"experiment directory uses a link: {root}")
    for part in path.parts:
        current = current / part
        require(not is_link(current), f"artifact uses a link: {value}")
    try:
        require(target.resolve().is_relative_to(root.resolve()), f"artifact escapes experiment: {value}")
    except (OSError, RuntimeError) as error:
        raise InvalidExperiment(f"cannot resolve artifact {value!r}: {error}") from error
    require(target.is_file(), f"missing artifact: {value}")
    return target


def validate(document: object, root: Path | None = None) -> dict:
    require(isinstance(document, dict), "experiment must be an object")
    try:
        json.dumps(document, allow_nan=False)
    except (ValueError, TypeError, OverflowError, RecursionError) as error:
        raise InvalidExperiment("experiment must contain finite JSON values") from error
    require(set(document) == {"schema_version", "kind", "experiment", "conditions", "results"},
            "experiment fields must be schema_version, kind, experiment, conditions, results")
    require(type(document["schema_version"]) is int and document["schema_version"] == 1,
            "schema_version must be 1")
    require(document["kind"] in ("behavioral", "synthetic"), "kind must be behavioral or synthetic")
    settings = document["experiment"]
    require(isinstance(settings, dict), "experiment settings must be an object")
    fields = {"model", "harness", "environment", "tools", "parameters", "dataset_revision", "grader_revision"}
    require(set(settings) == fields, f"experiment settings must have: {', '.join(sorted(fields))}")
    for key in fields - {"tools", "parameters"}:
        require(nonempty(settings[key]), f"experiment.{key} must be a non-empty string")
    require(isinstance(settings["tools"], list) and all(nonempty(t) for t in settings["tools"]),
            "experiment.tools must be a list of versioned tool names")
    require(len(settings["tools"]) == len(set(settings["tools"])), "duplicate experiment tools")
    require(isinstance(settings["parameters"], dict), "experiment.parameters must be an object")
    conditions = document["conditions"]
    require(isinstance(conditions, dict) and len(conditions) >= 2, "at least two conditions are required")
    for name, metadata in conditions.items():
        require(nonempty(name) and isinstance(metadata, dict), "invalid condition")
        require(set(metadata) == {"skill_revision", "description"}, f"invalid condition fields: {name}")
        require(all(nonempty(v) for v in metadata.values()), f"empty condition metadata: {name}")
    results = document["results"]
    require(isinstance(results, list) and bool(results), "results must be a non-empty list")
    fields = {"task_id", "repeat", "condition", "success", "seconds", "tokens", "artifact", "critical_failures"}
    seen = set()
    coverage = {name: set() for name in conditions}
    for index, result in enumerate(results):
        prefix = f"result {index + 1}"
        require(isinstance(result, dict) and set(result) == fields, f"{prefix}: invalid result fields")
        require(nonempty(result["task_id"]), f"{prefix}: task_id must be non-empty")
        require(type(result["repeat"]) is int and result["repeat"] >= 1, f"{prefix}: repeat must be positive integer")
        require(isinstance(result["condition"], str) and result["condition"] in conditions,
                f"{prefix}: unknown condition")
        require(type(result["success"]) is bool, f"{prefix}: success must be boolean")
        for key in ("seconds", "tokens"):
            require(result[key] is None or number(result[key]), f"{prefix}: {key} must be finite, nonnegative or null")
        require(result["tokens"] is None or type(result["tokens"]) is int,
                f"{prefix}: tokens must be an integer or null")
        failures = result["critical_failures"]
        require(isinstance(failures, list) and all(nonempty(f) for f in failures),
                f"{prefix}: critical_failures must be a list of descriptions")
        require(not (result["success"] and failures), f"{prefix}: critical failures cannot be scored as success")
        artifact_relative_path(result["artifact"])
        if root is not None:
            artifact_path(root, result["artifact"])
        identity = (result["task_id"], result["repeat"], result["condition"])
        require(identity not in seen, f"duplicate trial: {identity}")
        seen.add(identity)
        coverage[result["condition"]].add(identity[:2])
    reference = next(iter(coverage.values()))
    require(all(pairs == reference for pairs in coverage.values()),
            "conditions must contain exactly the same task/repeat pairs; retain failed trials")
    return document


def compare(document: dict, baseline: str, candidate: str, resamples: int = 5000) -> dict:
    validate(document)
    require(isinstance(baseline, str) and isinstance(candidate, str) and baseline != candidate
            and baseline in document["conditions"] and candidate in document["conditions"],
            "choose two distinct known conditions")
    require(type(resamples) is int and 100 <= resamples <= 100000, "resamples must be 100..100000")
    trials = {(r["task_id"], r["repeat"], r["condition"]): r for r in document["results"]}
    pairs = sorted((task, repeat) for task, repeat, condition in trials if condition == baseline)
    tasks = sorted({task for task, _ in pairs})
    task_deltas = []
    baseline_rates, candidate_rates = [], []
    for task in tasks:
        repeats = [repeat for paired_task, repeat in pairs if paired_task == task]
        b = statistics.mean(trials[task, repeat, baseline]["success"] for repeat in repeats)
        c = statistics.mean(trials[task, repeat, candidate]["success"] for repeat in repeats)
        baseline_rates.append(b)
        candidate_rates.append(c)
        task_deltas.append(c - b)
    interval = None
    if len(tasks) >= 2:
        rng = random.Random(0)
        samples = sorted(statistics.mean(rng.choices(task_deltas, k=len(tasks))) for _ in range(resamples))
        interval = [100 * samples[int((resamples - 1) * quantile)] for quantile in (.025, .975)]
    warnings = []
    if document["kind"] == "synthetic":
        warnings.append("Synthetic data exercises tooling only; it is not behavioral evidence.")
    if len(tasks) < 10:
        warnings.append("Fewer than 10 distinct tasks: treat this as a smoke result, not general superiority.")
    if len({sum(t == task for t, _ in pairs) for task in tasks}) > 1:
        warnings.append("Repeat counts differ by task; task success rates receive equal weight.")
    costs = {}
    for metric in ("seconds", "tokens"):
        observed = [(trials[t, r, baseline][metric], trials[t, r, candidate][metric]) for t, r in pairs
                    if trials[t, r, baseline][metric] is not None and trials[t, r, candidate][metric] is not None]
        costs[metric] = {"observed_pairs": len(observed),
                         "baseline_mean": statistics.mean(b for b, _ in observed) if observed else None,
                         "candidate_mean": statistics.mean(c for _, c in observed) if observed else None}
        if len(observed) != len(pairs):
            warnings.append(f"{metric}: missing measurements are excluded, never treated as zero.")
    regressions = [{"task_id": t, "repeat": r} for t, r in pairs
                   if trials[t, r, baseline]["success"] and not trials[t, r, candidate]["success"]]
    critical = [{"task_id": t, "repeat": r, "failures": trials[t, r, candidate]["critical_failures"]}
                for t, r in pairs if trials[t, r, candidate]["critical_failures"]]
    return {"kind": document["kind"], "baseline": baseline, "candidate": candidate,
            "distinct_tasks": len(tasks), "paired_trials": len(pairs),
            "baseline_success_rate": statistics.mean(baseline_rates),
            "candidate_success_rate": statistics.mean(candidate_rates),
            "success_delta_percentage_points": 100 * statistics.mean(task_deltas),
            "task_cluster_bootstrap_95_percent_interval_pp": interval,
            "costs": costs, "regressions": regressions, "candidate_critical_failures": critical,
            "warnings": warnings,
            "interpretation": "Descriptive paired comparison; does not automatically establish causality or authorize deployment."}


def load_experiment(path: Path) -> dict:
    def reject_constant(value: str) -> None:
        raise InvalidExperiment(f"non-finite JSON number: {value}")

    def unique_keys(items: list) -> dict:
        result = {}
        for key, value in items:
            require(key not in result, f"duplicate JSON field: {key}")
            result[key] = value
        return result

    require(not is_link(path), "experiment file must not be a symlink or junction")
    try:
        document = json.loads(path.read_text(encoding="utf-8"), parse_constant=reject_constant, object_pairs_hook=unique_keys)
    except RecursionError as error:
        raise InvalidExperiment("experiment JSON is nested too deeply") from error
    return validate(document, path.absolute().parent)


def check_output_path(output: Path, source: Path, document: dict) -> None:
    require(not is_link(output), "output must not be a symlink or junction")
    protected = [source, *(artifact_path(source.absolute().parent, r["artifact"]) for r in document["results"])]
    for path in protected:
        require(output.resolve() != path.resolve() and not (output.exists() and output.samefile(path)),
                "output must not overwrite the experiment or a trial artifact")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path)
    parser.add_argument("--baseline", default="no-skill")
    parser.add_argument("--candidate", default="candidate")
    parser.add_argument("--resamples", type=int, default=5000)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        document = load_experiment(args.results)
        if args.output:
            check_output_path(args.output, args.results, document)
        result = compare(document, args.baseline, args.candidate, args.resamples)
        rendered = json.dumps(result, indent=2, allow_nan=False) + "\n"
        if args.output:
            args.output.write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
        return 0
    except (OSError, ValueError, TypeError, RuntimeError) as error:
        print(f"Invalid evaluation: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
