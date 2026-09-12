from __future__ import annotations

import copy
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("compare_runs", ROOT / "library/evaluate-ai-output/scripts/compare_runs.py")
assert spec and spec.loader
comparison = importlib.util.module_from_spec(spec)
spec.loader.exec_module(comparison)


def experiment():
    return {
        "schema_version": 1, "kind": "synthetic",
        "experiment": {"model": "fixture-model", "harness": "fixture@1", "environment": "isolated fixtures",
                       "tools": [], "parameters": {}, "dataset_revision": "fixture@1", "grader_revision": "fixture@1"},
        "conditions": {name: {"skill_revision": "fixture@1", "description": name} for name in ("no-skill", "candidate")},
        "results": [{"task_id": "task", "repeat": 1, "condition": name, "success": name == "candidate",
                     "seconds": None, "tokens": None, "artifact": f"{name}.json", "critical_failures": []}
                    for name in ("no-skill", "candidate")],
    }


class EvaluationTests(unittest.TestCase):
    def test_single_task_does_not_claim_confidence(self):
        result = comparison.compare(experiment(), "no-skill", "candidate", 100)
        self.assertEqual(result["success_delta_percentage_points"], 100)
        self.assertIsNone(result["task_cluster_bootstrap_95_percent_interval_pp"])
        self.assertIsNone(result["costs"]["tokens"]["candidate_mean"])
        self.assertTrue(result["warnings"])

    def test_missing_and_duplicate_trials_are_rejected(self):
        for mutate in (lambda rows: rows.pop(), lambda rows: rows.append(copy.deepcopy(rows[0]))):
            data = experiment()
            mutate(data["results"])
            with self.assertRaises(comparison.InvalidExperiment):
                comparison.validate(data)

    def test_malformed_inputs_are_controlled(self):
        for value in (None, [], {}, "experiment"):
            with self.assertRaises(comparison.InvalidExperiment):
                comparison.validate(value)
        for field, value in (("tokens", True), ("seconds", float("nan")), ("seconds", -1),
                             ("seconds", 10 ** 400), ("tokens", 10 ** 400),
                             ("condition", []), ("success", 1), ("repeat", True)):
            data = experiment()
            data["results"][0][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(comparison.InvalidExperiment):
                comparison.validate(data)

    def test_nonfinite_nested_parameters_and_unknown_fields_are_rejected(self):
        data = experiment()
        data["experiment"]["parameters"] = {"nested": [{"limit": float("inf")} ]}
        with self.assertRaises(comparison.InvalidExperiment):
            comparison.validate(data)
        data = experiment()
        data["results"][0]["custom_score"] = 1.0
        with self.assertRaises(comparison.InvalidExperiment):
            comparison.validate(data)
        for baseline, candidate in (([], "candidate"), ("no-skill", {}), ("missing", "candidate")):
            with self.assertRaises(comparison.InvalidExperiment):
                comparison.compare(experiment(), baseline, candidate, 100)

    def test_critical_failure_cannot_pass(self):
        data = experiment()
        data["results"][1]["critical_failures"] = ["unauthorized write"]
        with self.assertRaises(comparison.InvalidExperiment):
            comparison.validate(data)
        data["results"][1]["success"] = False
        result = comparison.compare(data, "no-skill", "candidate", 100)
        self.assertEqual(len(result["candidate_critical_failures"]), 1)

    def test_repeats_are_clustered_not_counted_as_independent_tasks(self):
        data = experiment()
        for row in data["results"]:
            row["seconds"] = 10 if row["condition"] == "no-skill" else 20
        for repeat in range(2, 5):
            for row in data["results"][:2]:
                data["results"].append({**row, "repeat": repeat})
        for row in data["results"][:2]:
            data["results"].append({**row, "task_id": "regression", "seconds": row["seconds"] * 10,
                                    "success": row["condition"] == "no-skill"})
        result = comparison.compare(data, "no-skill", "candidate", 100)
        self.assertEqual(result["success_delta_percentage_points"], 0)
        self.assertEqual(result["distinct_tasks"], 2)
        self.assertEqual(result["paired_trials"], 5)
        self.assertEqual(len(result["regressions"]), 1)
        self.assertEqual(result["baseline_success_rate"], 0.5)
        self.assertEqual(result["candidate_success_rate"], 0.5)
        self.assertEqual(result["task_cluster_bootstrap_95_percent_interval_pp"], [-100, 100])
        self.assertEqual(result["costs"]["seconds"]["baseline_mean"], 28)
        self.assertEqual(result["costs"]["seconds"]["candidate_mean"], 56)

    def test_costs_require_both_observations_and_preserve_real_zero(self):
        data = experiment()
        data["results"][0].update(seconds=0, tokens=10)
        data["results"][1].update(seconds=0, tokens=None)
        result = comparison.compare(data, "no-skill", "candidate", 100)
        self.assertEqual(result["costs"]["seconds"], {"observed_pairs": 1, "baseline_mean": 0, "candidate_mean": 0})
        self.assertEqual(result["costs"]["tokens"], {"observed_pairs": 0, "baseline_mean": None, "candidate_mean": None})

    def test_every_condition_requires_the_same_task_repeat_cells(self):
        data = experiment()
        data["conditions"]["existing"] = {"skill_revision": "fixture@0", "description": "existing"}
        data["results"].append({**data["results"][0], "condition": "existing"})
        self.assertEqual(comparison.validate(data), data)
        data["results"][-1]["repeat"] = 2
        with self.assertRaises(comparison.InvalidExperiment):
            comparison.validate(data)

    def test_artifact_traversal_and_missing_files_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "existing.json").write_text("fixture")
            for value in ("../outside.json", "a/../../outside", "C:/outside", "a\\b", "/tmp/absolute", "missing.json",
                          "existing.json/", "a//b", "nul\x00.json"):
                with self.subTest(value=value), self.assertRaises(comparison.InvalidExperiment):
                    comparison.artifact_path(root, value)

    def test_loader_requires_artifacts_and_rejects_duplicate_json_fields(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "results.json"
            data = experiment()
            source.write_text(json.dumps(data))
            with self.assertRaises(comparison.InvalidExperiment):
                comparison.load_experiment(source)
            for row in data["results"]:
                (root / row["artifact"]).write_text("synthetic fixture")
            self.assertEqual(comparison.load_experiment(source), data)
            source.write_text('{"schema_version":1,"schema_version":1}')
            with self.assertRaises(comparison.InvalidExperiment):
                comparison.load_experiment(source)

    def test_loader_and_cli_reject_overflowing_json_numbers(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data = experiment()
            data["experiment"]["parameters"] = {"limit": "OVERFLOW"}
            source = root / "results.json"
            source.write_text(json.dumps(data).replace('"OVERFLOW"', '1e999'))
            with self.assertRaises(comparison.InvalidExperiment):
                comparison.load_experiment(source)
            result = subprocess.run([sys.executable, str(Path(comparison.__file__)), str(source)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn("finite JSON", result.stderr)
            self.assertNotIn("Traceback", result.stderr)

    def test_cli_writes_comparison_but_protects_evidence_and_hardlinks(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data = experiment()
            source = root / "results.json"
            source.write_text(json.dumps(data))
            for row in data["results"]:
                (root / row["artifact"]).write_text("raw trial evidence")
            command = [sys.executable, str(Path(comparison.__file__)), str(source), "--resamples", "100", "--output"]
            output = root / "comparison.json"
            result = subprocess.run([*command, str(output)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(output.read_text())["paired_trials"], 1)
            for protected in (source, root / "candidate.json"):
                before = protected.read_bytes()
                failed = subprocess.run([*command, str(protected)], capture_output=True, text=True)
                self.assertEqual(failed.returncode, 1)
                self.assertEqual(protected.read_bytes(), before)
            alias = root / "source-alias.json"
            try:
                os.link(source, alias)
            except OSError:
                self.skipTest("hardlinks unavailable")
            failed = subprocess.run([*command, str(alias)], capture_output=True, text=True)
            self.assertEqual(failed.returncode, 1)
            self.assertEqual(json.loads(source.read_text()), data)

    def test_symlink_artifacts_and_input_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / "real.json"
            target.write_text("fixture")
            alias = root / "alias.json"
            try:
                alias.symlink_to(target)
            except OSError:
                self.skipTest("symlinks unavailable")
            with self.assertRaises(comparison.InvalidExperiment):
                comparison.artifact_path(root, "alias.json")
            with self.assertRaises(comparison.InvalidExperiment):
                comparison.load_experiment(alias)


if __name__ == "__main__":
    unittest.main()
