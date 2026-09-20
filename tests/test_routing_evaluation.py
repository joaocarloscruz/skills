import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("routing", ROOT / "evals/routing.py")
routing = importlib.util.module_from_spec(spec)
spec.loader.exec_module(routing)


class RoutingEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.prepared = routing.prepare()
        cases = json.loads((ROOT / "tests/activation-cases.json").read_text(encoding="utf-8"))["cases"]
        self.answers = {key: self.prepared[key] for key in ("dataset_revision", "catalog_revision")}
        self.answers["selections"] = [{"id": f"case-{i:03d}", "router": c["expected_router"],
                                       "workflows": c["expected_skills"]} for i, c in enumerate(cases, 1)]

    def test_preparation_withholds_labels_and_scores_exact_selections(self):
        self.assertTrue(all(set(case) == {"id", "prompt"} for case in self.prepared["cases"]))
        result = routing.score(self.answers)
        self.assertEqual(result["cases"], result["passed"])
        self.answers["selections"][0].update(router=None, workflows=[])
        self.assertEqual(routing.score(self.answers)["passed"], result["passed"] - 1)

    def test_missing_duplicate_and_unknown_cells_are_not_silent_successes(self):
        for change in (lambda d: d["selections"].pop(),
                       lambda d: d["selections"].append(d["selections"][0]),
                       lambda d: d["selections"][0].update(id="unknown"),
                       lambda d: d["selections"][0].update(router="unknown"),
                       lambda d: d["selections"][0].update(workflows=["unknown"]),
                       lambda d: d["selections"][0].update(workflows=[]),
                       lambda d: d.update(dataset_revision="stale"),
                       lambda d: d.update(catalog_revision="stale")):
            data = copy.deepcopy(self.answers)
            change(data)
            with self.assertRaises(ValueError):
                routing.score(data)

    def test_dataset_revision_is_portable_across_line_endings(self):
        content = (ROOT / "tests/activation-cases.json").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as temp, mock.patch.object(routing, "category_entries", return_value=[]):
            root = Path(temp)
            (root / "tests").mkdir()
            path = root / "tests/activation-cases.json"
            path.write_bytes(content.encode("utf-8"))
            expected = routing.prepare(root)["dataset_revision"]
            path.write_bytes(content.replace("\n", "\r\n").encode("utf-8"))
            self.assertEqual(routing.prepare(root)["dataset_revision"], expected)
            changed = json.loads(content)
            changed["cases"][0]["prompt"] += " Changed intent."
            path.write_text(json.dumps(changed), encoding="utf-8")
            self.assertNotEqual(routing.prepare(root)["dataset_revision"], expected)


if __name__ == "__main__":
    unittest.main()
