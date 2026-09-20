"""Grader regressions; keep these reference answers out of trial inputs."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


worker = load_module("smoke_worker", ROOT / "private" / "grade.py")
runner = load_module("smoke_runner", ROOT / "run.py")

SQL = """
WITH paid AS (
 SELECT o.customer_id, o.id AS order_id,
        COALESCE(SUM(i.quantity * i.unit_price_cents), 0) AS cents
 FROM orders o LEFT JOIN order_items i ON i.order_id = o.id
 WHERE o.status = 'paid' GROUP BY o.customer_id, o.id
)
SELECT c.id AS customer_id, COUNT(p.order_id) AS paid_order_count,
       COALESCE(SUM(p.cents), 0) AS revenue_cents
FROM customers c LEFT JOIN paid p ON p.customer_id = c.id
GROUP BY c.id ORDER BY c.id;
"""
PIPELINE = """
def sync(events, sink, checkpoints):
    cursor = checkpoints.load()
    for event in events:
        if event['sequence'] > cursor:
            sink.put(event['id'], event['value'])
            checkpoints.save(event['sequence'])
"""
TOOL = """
def submit(remote, payload, key):
    for attempt in range(2):
        try:
            result = remote.submit(payload, key)
        except TimeoutError:
            try:
                result = remote.status(key)
            except TimeoutError:
                return {'state': 'unknown', 'key': key}
        if result['state'] == 'succeeded':
            return result
        if result['state'] == 'pending':
            return {'state': 'pending', 'key': key}
    return {'state': 'unknown', 'key': key}
"""


class SmokeGraderTests(unittest.TestCase):
    def assert_grade(self, task, source, expected):
        result = worker.grade_source(task, source)
        self.assertEqual(result["success"], expected, result)
        return result

    def test_correct_solutions_pass_all_outcome_cases(self):
        for task, source in [("sql-grain", SQL), ("pipeline-replay", PIPELINE),
                             ("tool-write-recovery", TOOL)]:
            with self.subTest(task=task):
                self.assert_grade(task, source, True)

    def test_sql_join_fanout_fails(self):
        self.assert_grade("sql-grain", """
SELECT c.id AS customer_id, COUNT(o.id) AS paid_order_count,
       COALESCE(SUM(i.quantity * i.unit_price_cents), 0) AS revenue_cents
FROM customers c LEFT JOIN orders o ON o.customer_id = c.id AND o.status = 'paid'
LEFT JOIN order_items i ON i.order_id = o.id
GROUP BY c.id ORDER BY c.id
""", False)

    def test_sql_inner_join_loses_zero_customers(self):
        self.assert_grade("sql-grain", SQL.replace("customers c LEFT JOIN", "customers c JOIN"), False)

    def test_sql_visible_hardcoding_does_not_pass(self):
        self.assert_grade("sql-grain", """
SELECT 1 AS customer_id, 2 AS paid_order_count, 850 AS revenue_cents
UNION ALL SELECT 2, 0, 0 UNION ALL SELECT 3, 0, 0
""", False)

    def test_sql_write_is_denied(self):
        result = self.assert_grade("sql-grain", "DELETE FROM customers RETURNING id", False)
        self.assertTrue(all("authorized" in check["error"] for check in result["checks"]))

    def test_checkpoint_before_sink_is_rejected(self):
        bad = PIPELINE.replace("sink.put(event['id'], event['value'])\n            checkpoints.save(event['sequence'])",
                               "checkpoints.save(event['sequence'])\n            sink.put(event['id'], event['value'])")
        self.assert_grade("pipeline-replay", bad, False)

    def test_batched_checkpoint_is_valid(self):
        result = self.assert_grade("pipeline-replay", """
def sync(events, sink, checkpoints):
    cursor = checkpoints.load()
    remaining = [event for event in events if event['sequence'] > cursor]
    for event in remaining:
        sink.put(event['id'], event['value'])
    if remaining:
        checkpoints.save(remaining[-1]['sequence'])
""", True)
        self.assertTrue(any(check.get("unreached_faults", 0) > 0
                            for check in result["checks"]))

    def test_missing_final_checkpoint_is_rejected(self):
        bad = PIPELINE.replace("            checkpoints.save(event['sequence'])", "")
        self.assert_grade("pipeline-replay", bad, False)

    def test_swallowed_crash_is_rejected(self):
        self.assert_grade("pipeline-replay", """
def sync(events, sink, checkpoints):
    cursor = checkpoints.load()
    try:
        for event in events:
            if event['sequence'] > cursor:
                sink.put(event['id'], event['value'])
                checkpoints.save(event['sequence'])
    except TimeoutError:
        return None
""", False)

    def test_ignoring_loaded_checkpoint_is_rejected(self):
        self.assert_grade("pipeline-replay", PIPELINE.replace("cursor = checkpoints.load()", "cursor = 0"), False)

    def test_retrying_write_without_reconciliation_is_rejected(self):
        self.assert_grade("tool-write-recovery", """
def submit(remote, payload, key):
    try:
        return remote.submit(payload, key)
    except TimeoutError:
        return remote.submit(payload, key)
""", False)

    def test_changing_retry_key_is_rejected(self):
        bad = TOOL.replace("remote.submit(payload, key)", "remote.submit(payload, key + str(attempt))")
        self.assert_grade("tool-write-recovery", bad, False)

    def test_claiming_success_on_pending_is_rejected(self):
        bad = TOOL.replace("return {'state': 'pending', 'key': key}", "return {'state': 'succeeded', 'result': None}")
        self.assert_grade("tool-write-recovery", bad, False)

    def test_external_capabilities_are_not_available(self):
        for source in ("import os", "def sync(a, b, c):\n    open('unexpected', 'w')",
                       "def sync(a, b, c):\n    return b.__class__"):
            with self.subTest(source=source):
                self.assert_grade("pipeline-replay", source, False)

    def test_preparation_is_fresh_and_excludes_private_graders(self):
        for task in runner.TASKS:
            with self.subTest(task=task), tempfile.TemporaryDirectory() as parent:
                destination = Path(parent) / "trial"
                runner.prepare(task, destination)
                artifact = "query.sql" if task == "sql-grain" else "solution.py"
                self.assertEqual({path.name for path in destination.iterdir()},
                                 {"TASK.md", "fixture.json", artifact})
                with self.assertRaises(ValueError):
                    runner.prepare(task, destination)

    def test_subprocess_runner_grades_saved_artifacts(self):
        for task, filename, source in [("sql-grain", "query.sql", SQL),
                                       ("pipeline-replay", "solution.py", PIPELINE),
                                       ("tool-write-recovery", "solution.py", TOOL)]:
            with self.subTest(task=task), tempfile.TemporaryDirectory() as trial:
                (Path(trial) / filename).write_text(source, encoding="utf-8")
                self.assertTrue(runner.grade(task, Path(trial))["success"])

    def test_missing_and_oversized_artifacts_fail(self):
        with tempfile.TemporaryDirectory() as trial:
            directory = Path(trial)
            self.assertFalse(runner.grade("sql-grain", directory)["success"])
            (directory / "query.sql").write_text(" " * 65537, encoding="utf-8")
            self.assertFalse(runner.grade("sql-grain", directory)["success"])

    def test_nonzero_worker_exit_cannot_claim_success(self):
        with tempfile.TemporaryDirectory() as trial:
            directory = Path(trial)
            (directory / "query.sql").write_text(SQL, encoding="utf-8")
            process = subprocess.CompletedProcess([], 1, json.dumps({"success": True}), "")
            with patch.object(runner.subprocess, "run", return_value=process):
                result = runner.grade("sql-grain", directory)
            self.assertFalse(result["success"])
            self.assertEqual(result["error"], "grader failed (exit 1)")

    def test_nonterminating_solution_times_out(self):
        with tempfile.TemporaryDirectory() as trial:
            directory = Path(trial)
            (directory / "solution.py").write_text(
                "def sync(events, sink, checkpoints):\n    while True:\n        pass\n", encoding="utf-8")
            result = runner.grade("pipeline-replay", directory, timeout=0.5)
            self.assertFalse(result["success"])
            self.assertEqual(result["error"], "grader time limit exceeded")


if __name__ == "__main__":
    unittest.main()
