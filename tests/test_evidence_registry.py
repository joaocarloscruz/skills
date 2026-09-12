from __future__ import annotations

import copy
import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('evidence_registry', ROOT / 'scripts/validate_evidence_registry.py')
assert spec and spec.loader
registry = importlib.util.module_from_spec(spec)
spec.loader.exec_module(registry)


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.document = json.loads((ROOT / 'evidence/skills.json').read_text())

    def test_current_registry_is_valid(self):
        self.assertEqual(registry.validate(self.document), [])

    def test_non_objects_and_malformed_nested_values_fail_cleanly(self):
        for bad in (None, [], 12, 'text'):
            self.assertTrue(registry.validate(bad))
        for key in ('skills', 'external_sources'):
            data = copy.deepcopy(self.document)
            data[key] = []
            self.assertTrue(registry.validate(data))
        data = copy.deepcopy(self.document)
        candidate = data['skills']['build-mcp-server']['external_candidates'][0]
        for key in ('source', 'path', 'relationship', 'evidence', 'citations'):
            changed = copy.deepcopy(data)
            changed['skills']['build-mcp-server']['external_candidates'][0][key] = {'malformed': []}
            self.assertTrue(registry.validate(changed))

    def test_calendar_date_and_repository_url_are_checked(self):
        for value in ('2026-02-30', '2026-9-1', None, True):
            data = copy.deepcopy(self.document)
            data['reviewed_on'] = value
            self.assertTrue(registry.validate(data))
        data = copy.deepcopy(self.document)
        data['external_sources']['anthropic-skills']['repository'] = 'https://github.com.evil.test/a/b'
        self.assertTrue(registry.validate(data))

    def test_traversal_and_duplicate_candidates_fail(self):
        for path in ('skills/../../outside', 'C:/outside', r'skills\thing', 'skills//thing', '../thing'):
            data = copy.deepcopy(self.document)
            data['skills']['build-mcp-server']['external_candidates'][0]['path'] = path
            self.assertTrue(registry.validate(data))
        data = copy.deepcopy(self.document)
        rows = data['skills']['build-mcp-server']['external_candidates']
        rows.append(copy.deepcopy(rows[0]))
        self.assertTrue(registry.validate(data))

    def test_measured_claim_requires_real_artifacts(self):
        data = copy.deepcopy(self.document)
        skill = data['skills']['tdd']
        skill['behavioral_evidence'] = 'paired-evaluated'
        self.assertTrue(registry.validate(data))
        skill['evaluations'] = [{'path': 'evidence/runs/missing.json', 'condition': 'candidate'}]
        self.assertTrue(registry.validate(data))

    def create_recorded_evaluation(self, root):
        """A declared behavioral fixture tests schema gates, not effectiveness."""
        (root / 'library/tdd').mkdir(parents=True)
        (root / 'library/tdd/SKILL.md').write_text('fixture')
        study = root / 'evidence/runs/study'
        study.mkdir(parents=True)
        run = {
            'schema_version': 1, 'kind': 'behavioral',
            'experiment': {'model': 'fixture', 'harness': 'fixture@1', 'environment': 'disposable',
                          'tools': [], 'parameters': {}, 'dataset_revision': 'fixture@1', 'grader_revision': 'fixture@1'},
            'conditions': {'no-skill': {'skill_revision': 'none', 'description': 'baseline'},
                           'candidate': {'skill_revision': 'sha256:' + 'a' * 64, 'description': 'fixture candidate'}},
            'results': [{'task_id': 'task', 'repeat': 1, 'condition': name, 'success': False,
                         'seconds': None, 'tokens': None, 'artifact': name + '.txt', 'critical_failures': []}
                        for name in ('no-skill', 'candidate')],
        }
        for result in run['results']:
            (study / result['artifact']).write_text('Unverified fixture content')
        source = study / 'results.json'
        source.write_text(json.dumps(run))
        document = copy.deepcopy(self.document)
        document['skills'] = {'tdd': {'behavioral_evidence': 'paired-evaluated',
                                    'evaluations': [{'path': 'evidence/runs/study/results.json', 'condition': 'candidate'}]}}
        return document, run, source

    def test_evidence_schema_does_not_establish_truth_or_a_winner(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data, _, _ = self.create_recorded_evaluation(root)
            # Both conditions fail; the status means evaluated, not successful.
            self.assertEqual(registry.validate(data, root), [])
            # A data root must not supply executable validator code.
            code = root / 'library/evaluate-ai-output/scripts/compare_runs.py'
            code.parent.mkdir(parents=True)
            code.write_text('raise RuntimeError("untrusted data-root code executed")')
            self.assertEqual(registry.validate(data, root), [])

    def test_evidence_promotion_rejects_synthetic_missing_or_unpinned_runs(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data, original, source = self.create_recorded_evaluation(root)
            for revision in ('main', 'shortsha', 'none'):
                run = copy.deepcopy(original)
                run['conditions']['candidate']['skill_revision'] = revision
                source.write_text(json.dumps(run))
                self.assertTrue(registry.validate(data, root))
            run = copy.deepcopy(original)
            run['kind'] = 'synthetic'
            source.write_text(json.dumps(run))
            self.assertTrue(registry.validate(data, root))
            source.write_text(json.dumps(original))
            data['skills']['tdd']['evaluations'][0]['condition'] = 'missing'
            self.assertTrue(registry.validate(data, root))
            data['skills']['tdd']['evaluations'][0]['condition'] = 'candidate'
            (source.parent / 'candidate.txt').unlink()
            self.assertTrue(registry.validate(data, root))

    def test_invalid_paths_and_citation_urls_return_errors(self):
        data = copy.deepcopy(self.document)
        for value in ('evidence/runs/nul\x00.json', 'evidence/runs/../outside.json'):
            data['skills']['tdd'] = {'behavioral_evidence': 'paired-evaluated',
                                    'evaluations': [{'path': value, 'condition': 'candidate'}]}
            self.assertTrue(registry.validate(data))
        candidate = data['skills']['build-mcp-server']['external_candidates'][0]
        for value in ('https://bad host/path', 'https://example.test:99999/path', 'https://example.test\n/path'):
            candidate['citations'] = [value]
            self.assertFalse(registry.https_url(value))
        data['skills'][4] = {}
        data['skills']['unknown'] = {}
        self.assertTrue(registry.validate(data))

    def test_evaluation_file_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data, _, source = self.create_recorded_evaluation(root)
            real = source.with_name('real.json')
            source.rename(real)
            try:
                source.symlink_to(real)
            except OSError:
                self.skipTest('symlinks unavailable')
            self.assertTrue(registry.validate(data, root))

    def test_linked_runs_directory_cannot_redefine_containment_root(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'repo'
            data, _, source = self.create_recorded_evaluation(root)
            runs = root / 'evidence/runs'
            external = Path(temp) / 'external-runs'
            runs.rename(external)
            if os.name == 'nt':
                quote = lambda path: "'" + str(path).replace("'", "''") + "'"
                command = f'New-Item -ErrorAction Stop -ItemType Junction -Path {quote(runs)} -Target {quote(external)} | Out-Null'
                result = subprocess.run(['powershell', '-NoProfile', '-Command', command],
                                        capture_output=True, text=True)
                if result.returncode:
                    self.skipTest('junction creation unavailable: ' + result.stderr)
            else:
                runs.symlink_to(external, target_is_directory=True)
            try:
                self.assertTrue(any('symlink or junction' in error for error in registry.validate(data, root)))
            finally:
                if os.name == 'nt':
                    runs.rmdir()  # Remove the junction itself, never recurse into its target.
                else:
                    runs.unlink()

    def test_duplicate_json_keys_fail(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'data.json'
            path.write_text('{"schema_version":2,"schema_version":2}')
            with self.assertRaises(ValueError):
                registry.load_json(path)


if __name__ == '__main__':
    unittest.main()
