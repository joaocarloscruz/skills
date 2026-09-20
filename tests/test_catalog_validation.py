from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_router_bundles as builder
import catalog_utils
import validate_activation_cases as activation
import validate_skills

auditor = validate_skills._auditor
DESCRIPTION = "Validate a representative engineering request with explicit expected behavior."


def write_skill(directory: Path, body: str = "Use the evidence available for the requested task.\n") -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "SKILL.md"
    path.write_text(f"---\nname: {directory.name}\ndescription: {DESCRIPTION}\n---\n\n{body}", encoding="utf-8")
    return path


def make_catalog(root: Path) -> dict[str, str]:
    names = {}
    for router, (category, _) in catalog_utils.ROUTER_CONFIG.items():
        skill = "sample-" + category
        names[router] = skill
        write_skill(root / "library" / skill)
        directory = root / "catalog" / category
        directory.mkdir(parents=True)
        (directory / "README.md").write_text(
            f"# {category}\n\n- [{skill}](../../library/{skill}/) - Representative task.\n", encoding="utf-8"
        )
    return names


class FrontmatterAndPackageTests(unittest.TestCase):
    def test_malformed_frontmatter_produces_errors_without_crashing(self):
        mutations = [
            "name: sample\nname: sample\ndescription: useful text",
            "name: [sample]\ndescription: useful text",
            "name: sample\ndescription: true",
            "name: sample\ndescription: useful text\nunknown: value",
            "name: sample\ndescription: useful text\n  ignored: no",
            "name: sample\ndescription: useful text\nmetadata:\n  author: first\n  author: second",
            "name: sample\ndescription: useful text\nmetadata:\n    nested: bad",
            "name: sample\ndescription: useful text\nmetadata: nope",
            "name: sample\ndescription: >\n\ttab-indented YAML is invalid",
            'name: sample\ndescription: "unterminated',
            "name: " + "a" * 65 + "\ndescription: useful text",
            "name: sample\ndescription: " + "a" * 1025,
            "name: sample\nlicense: MIT",
        ]
        with tempfile.TemporaryDirectory() as directory:
            skill = Path(directory) / "sample"
            path = write_skill(skill)
            for frontmatter in mutations:
                with self.subTest(frontmatter=frontmatter[:90]):
                    path.write_text(f"---\n{frontmatter}\n---\nBody.\n", encoding="utf-8")
                    self.assertTrue(validate_skills.validate(path))

    def test_valid_optional_fields_and_yaml_strings(self):
        with tempfile.TemporaryDirectory() as directory:
            path = write_skill(Path(directory) / "sample")
            path.write_text("---\nname: sample\ndescription: >-\n  Validate a representative engineering request\n  with explicit expected behavior.\nlicense: 'Apache-2.0'\ncompatibility: Python 3.12\nmetadata:\n  author: 'Team''s example'\n  version: \"1.0\"\nallowed-tools: Read Write\n---\nBody.\n", encoding="utf-8")
            self.assertEqual(validate_skills.validate(path), [])
            metadata, errors = auditor.parse_frontmatter(path)
            self.assertEqual(errors, [])
            self.assertEqual(metadata["metadata"]["author"], "Team's example")

    def test_invalid_utf8_is_a_finding(self):
        with tempfile.TemporaryDirectory() as directory:
            path = write_skill(Path(directory) / "sample")
            path.write_bytes(b"\xff")
            self.assertTrue(any(item.code == "unreadable-skill" for item in auditor.audit(path.parent, 1.0)))

    def test_nested_skill_entrypoint_cannot_silently_join_a_package(self):
        with tempfile.TemporaryDirectory() as directory:
            path = write_skill(Path(directory) / "sample")
            write_skill(path.parent / "nested")
            self.assertTrue(any("exactly its top-level" in error for error in validate_skills.validate(path)))

    def test_existing_external_link_is_rejected_without_reading_it(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            # If reachable_documents follows this link, decoding would fail.
            (root / "outside.md").write_bytes(b"\xff")
            path = write_skill(root / "sample", "Read [outside](../outside.md).\n")
            findings = auditor.audit(path.parent, 1.0)
            self.assertTrue(any(item.code == "escaping-link" for item in findings))
            self.assertFalse(any(item.code == "unreadable-skill" for item in findings))
            self.assertEqual(set(auditor.reachable_documents(path)), {path})

    def test_encoded_escape_and_missing_reference_links_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = write_skill(Path(directory) / "sample", "[outside](%2e%2e/outside.md)\nRead [guide][docs].\n[docs]: references/missing.md\n")
            codes = {item.code for item in auditor.audit(path.parent, 1.0)}
            self.assertIn("escaping-link", codes)
            self.assertIn("broken-link", codes)

    def test_inline_resource_paths_are_validated(self):
        with tempfile.TemporaryDirectory() as directory:
            path = write_skill(Path(directory) / "sample",
                               "Read `references/missing.md` and run `scripts/missing.py`.\n"
                               "Use `assets/../../../outside.txt`.\n")
            findings = auditor.audit(path.parent, 1.0)
            self.assertEqual(sum(item.code == "broken-link" for item in findings), 2)
            self.assertTrue(any(item.code == "escaping-link" for item in findings))

    def test_inline_reference_chain_is_reachable_and_cycles_terminate(self):
        with tempfile.TemporaryDirectory() as directory:
            path = write_skill(Path(directory) / "sample", "Read `references/guide.md`.\n")
            guide = path.parent / "references" / "guide.md"
            helper = guide.parent / "scripts" / "check.py"
            helper.parent.mkdir(parents=True)
            guide.write_text("Run `scripts/check.py`. Return to [start](../SKILL.md).\n", encoding="utf-8")
            helper.write_text("print('ok')\n", encoding="utf-8")
            self.assertEqual(set(auditor.reachable_documents(path)), {path, guide})
            self.assertEqual(auditor.audit(path.parent, 1.0), [])

    def test_resource_mentions_are_exact_and_decode_link_targets(self):
        with tempfile.TemporaryDirectory() as directory:
            path = write_skill(Path(directory) / "sample",
                               'Read [the guide](references/query%20guide.md#usage "Details") '
                               "and `references/guide.md.old`.\n")
            resources = path.parent / "references"
            resources.mkdir()
            for name in ("query guide.md", "guide.md", "guide.md.old"):
                (resources / name).write_text("Details.\n", encoding="utf-8")
            findings = auditor.audit(path.parent, 1.0)
            unused = [item.path for item in findings if item.code == "unreferenced-resource"]
            self.assertEqual(unused, ["references/guide.md"])
            self.assertFalse(any(item.severity == "error" for item in findings))

    def test_code_examples_are_not_live_resource_links(self):
        with tempfile.TemporaryDirectory() as directory:
            path = write_skill(Path(directory) / "sample",
                               "Example syntax: `[guide](references/missing.md)`.\n"
                               "``Use `references/missing.md` in an example.``\n"
                               "```markdown\nRead [guide](references/missing.md).\n"
                               "Run `scripts/missing.py`.\n```\n"
                               "Run `python scripts/example.py --help` after substituting a real path.\n")
            self.assertEqual(auditor.audit(path.parent, 1.0), [])

    def test_resource_symlink_is_rejected_without_following(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = write_skill(root / "sample")
            external = root / "outside.md"
            external.write_bytes(b"\xff")
            try:
                (path.parent / "linked.md").symlink_to(external)
            except OSError as error:
                self.skipTest(f"symlink creation unavailable: {error}")
            findings = auditor.audit(path.parent, 1.0)
            self.assertTrue(any(item.code == "unsafe-link" for item in findings))
            self.assertFalse(any(item.code == "unreadable-resource" for item in findings))


class CatalogAndActivationTests(unittest.TestCase):
    def test_category_label_must_match_target(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_catalog(root)
            index = root / "catalog" / "planning" / "README.md"
            index.write_text("- [wrong](../../library/sample-planning/) - A task.\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "label and library target differ"):
                catalog_utils.catalog_membership(root)

    def test_duplicate_membership_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_catalog(root)
            index = root / "catalog" / "planning" / "README.md"
            with index.open("a", encoding="utf-8") as stream:
                stream.write("- [sample-planning](../../library/sample-planning/) - Again.\n")
            with self.assertRaisesRegex(ValueError, "more than once"):
                catalog_utils.catalog_membership(root)

    def test_expected_skills_must_belong_to_router(self):
        case = {"id": "cross-router", "title": "Wrong route", "prompt": "Do a task", "rationale": "Fixture mutation", "expected_router": "data", "expected_skills": ["test-cli"], "unexpected_skills": ["write-sql"]}
        membership = {"data": {"write-sql"}, "quality-security": {"test-cli"}}
        errors = activation.validate_case(case, 0, {"write-sql", "test-cli"}, set(membership), membership)
        self.assertTrue(any("not members" in error for error in errors))
        case.update(expected_router=None, expected_skills=[])
        self.assertEqual(activation.validate_case(case, 0, {"write-sql", "test-cli"}, set(membership), membership), [])
        case["expected_skills"] = ["test-cli"]
        self.assertTrue(any("no-match" in error for error in activation.validate_case(case, 0, {"write-sql", "test-cli"}, set(membership), membership)))

    def test_invalid_json_documents_fail_cleanly(self):
        for document in ["[]", "null", "{", '{"schema_version":true,"cases":[]}', '{"schema_version":1,"schema_version":1,"cases":[]}']:
            with self.subTest(document=document), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "cases.json"
                path.write_text(document, encoding="utf-8")
                with mock.patch.object(sys, "argv", ["validate", str(path)]), contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(activation.main(), 1)

    def test_nested_invalid_case_values_return_errors(self):
        case = {"id": [], "title": 4, "prompt": {}, "rationale": None, "expected_router": [], "expected_skills": [{}], "unexpected_skills": [[]]}
        self.assertTrue(activation.validate_case(case, 0, {"sample"}, {"router"}, {"router": {"sample"}}))


class GenerationOwnershipTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.names = make_catalog(self.root)
        self.patch = mock.patch.multiple(builder, ROOT=self.root, LIBRARY=self.root / "library", ROUTERS=self.root / "skills", CATALOG=self.root / "catalog")
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.output = io.StringIO()
        self.capture = contextlib.redirect_stdout(self.output)
        self.capture.__enter__()
        self.addCleanup(self.capture.__exit__, None, None, None)

    def test_bad_source_leaves_existing_outputs_untouched(self):
        target = self.root / "skills" / "notes.txt"
        target.parent.mkdir()
        target.write_text("preserve", encoding="utf-8")
        path = self.root / "library" / self.names["data"] / "SKILL.md"
        path.write_text("bad frontmatter", encoding="utf-8")
        with self.assertRaises(ValueError):
            builder.build()
        self.assertEqual(target.read_text(encoding="utf-8"), "preserve")
        self.assertEqual(list(target.parent.iterdir()), [target])

    def test_failed_atomic_replace_keeps_previous_output_and_cleans_temporary(self):
        target = self.root / "skills" / "data" / "SKILL.md"
        target.parent.mkdir(parents=True)
        target.write_text("previous", encoding="utf-8")
        with mock.patch.object(builder.os, "replace", side_effect=OSError("simulated filesystem failure")):
            with self.assertRaises(OSError):
                builder.write_atomic(target, b"replacement")
        self.assertEqual(target.read_text(encoding="utf-8"), "previous")
        self.assertEqual(list(target.parent.iterdir()), [target])

    def test_stale_owned_resource_is_removed_and_other_paths_survive(self):
        skill = self.root / "library" / self.names["data"]
        write_skill(skill, "Read [guide](references/guide.md).\n")
        resource = skill / "references" / "guide.md"
        resource.parent.mkdir()
        resource.write_text("Detailed guidance.\n", encoding="utf-8")
        builder.build()
        output_resource = self.root / "skills" / "data" / "references" / skill.name / "references" / "guide.md"
        self.assertTrue(output_resource.exists())
        outside = self.root / "outside.txt"
        outside.write_text("keep", encoding="utf-8")
        resource.unlink()
        resource.parent.rmdir()
        write_skill(skill)
        builder.build()
        self.assertFalse(output_resource.exists())
        self.assertEqual(outside.read_text(encoding="utf-8"), "keep")
        self.assertEqual(builder.check(), 0)

    def test_unowned_and_modified_generated_outputs_are_preserved(self):
        builder.build()
        unowned = self.root / "skills" / "data" / "personal.txt"
        unowned.write_text("keep", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "unowned"):
            builder.build()
        self.assertEqual(unowned.read_text(encoding="utf-8"), "keep")
        unowned.unlink()
        generated = self.root / "skills" / "data" / "SKILL.md"
        generated.write_text("user edit", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "local modifications"):
            builder.build()
        self.assertEqual(generated.read_text(encoding="utf-8"), "user edit")

    def test_corrupt_or_escaping_manifest_cannot_delete_files(self):
        builder.build()
        sentinel = self.root / "outside.txt"
        sentinel.write_text("keep", encoding="utf-8")
        manifest = self.root / "skills" / builder.MANIFEST
        for content in ["[]", '{"schema_version":1,"files":{"../outside.txt":"' + "0" * 64 + '"}}']:
            manifest.write_text(content, encoding="utf-8")
            with self.assertRaises(ValueError):
                builder.build()
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")

    def test_backlinks_survive_entrypoint_renaming(self):
        skill = self.root / "library" / self.names["data"]
        write_skill(skill, "Read [guide](references/guide.md).\n")
        guide = skill / "references" / "guide.md"
        guide.parent.mkdir()
        guide.write_text("Return to [workflow](../SKILL.md#usage).\n", encoding="utf-8")
        builder.build()
        output = self.root / "skills" / "data"
        bundled = output / "references" / skill.name / "references" / "guide.md"
        self.assertIn("../workflow.md#usage", bundled.read_text(encoding="utf-8"))
        self.assertFalse([finding for finding in auditor.audit(output, 1.0) if finding.severity == "error"])

    def test_inline_backlink_survives_entrypoint_renaming(self):
        skill = self.root / "library" / self.names["data"]
        write_skill(skill, "Read `references/guide.md`.\n")
        guide = skill / "references" / "guide.md"
        guide.parent.mkdir()
        guide.write_text("Return to `../references/../SKILL.md#usage`.\n", encoding="utf-8")
        builder.build()
        output = self.root / "skills" / "data"
        self.assertFalse([finding for finding in auditor.audit(output, 1.0) if finding.severity == "error"])

    def test_text_checkout_line_endings_do_not_stale_manifest(self):
        skill = self.root / "library" / self.names["data"]
        write_skill(skill, "Run [the check](scripts/check.py) or [the shell check](scripts/check.sh).\n")
        script = skill / "scripts" / "check.py"
        script.parent.mkdir()
        script.write_bytes(b"print('one')\r\nprint('two')\r\n")
        (script.parent / "check.sh").write_bytes(b"#!/bin/sh\r\nprintf 'ok'\r\n")
        builder.build()
        manifest = (self.root / "skills" / builder.MANIFEST).read_bytes()
        # Simulate Git checking out the same tracked content on another platform.
        for tree in (self.root / "library", self.root / "skills"):
            for path in tree.rglob("*"):
                if path.is_file() and path.suffix in builder.TEXT_SUFFIXES:
                    path.write_bytes(path.read_bytes().replace(b"\r\n", b"\n"))
        self.assertEqual(builder.check(), 0)
        self.assertEqual(builder.expected_files()[builder.MANIFEST], manifest)

    def test_resource_cannot_overwrite_generated_workflow(self):
        skill = self.root / "library" / self.names["data"]
        (skill / "workflow.md").write_text("would overwrite the entrypoint", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "collides"):
            builder.build()
        self.assertFalse((self.root / "skills").exists())

    def test_output_directory_redirect_is_rejected(self):
        external = self.root / "external"
        external.mkdir()
        sentinel = external / "keep.txt"
        sentinel.write_text("keep", encoding="utf-8")
        try:
            (self.root / "skills").symlink_to(external, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"symlink creation unavailable: {error}")
        with self.assertRaisesRegex(ValueError, "unsafe router"):
            builder.build()
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")


if __name__ == "__main__":
    unittest.main()
