from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


router_builder = load_module("router_builder", ROOT / "scripts" / "build_router_bundles.py")
catalog_auditor = load_module(
    "catalog_auditor",
    ROOT / "library" / "audit-skill-catalog" / "scripts" / "audit_catalog.py",
)


class RouterBundleTests(unittest.TestCase):
    def test_text_comparison_normalizes_crlf(self) -> None:
        path = Path("workflow.md")
        self.assertEqual(
            router_builder.comparable_content(path, b"first\r\nsecond\r\n"),
            b"first\nsecond\n",
        )

    def test_binary_comparison_preserves_bytes(self) -> None:
        content = b"first\r\nsecond\x00"
        self.assertEqual(
            router_builder.comparable_content(Path("asset.bin"), content),
            content,
        )


class CatalogAuditorTests(unittest.TestCase):
    def test_nested_resource_reference_is_reachable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            skill = Path(directory)
            workflow = skill / "references" / "workflow.md"
            script = skill / "references" / "scripts" / "check.py"
            workflow.parent.mkdir(parents=True)
            script.parent.mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "Read [the workflow](references/workflow.md).\n",
                encoding="utf-8",
            )
            workflow.write_text("Run `scripts/check.py`.\n", encoding="utf-8")
            script.write_text("print('ok')\n", encoding="utf-8")

            documents = catalog_auditor.reachable_documents(skill / "SKILL.md")

            self.assertTrue(catalog_auditor.resource_is_referenced(script, documents))

    def test_unmentioned_resource_is_not_referenced(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            skill = Path(directory)
            resource = skill / "references" / "unused.md"
            resource.parent.mkdir(parents=True)
            (skill / "SKILL.md").write_text("No resources.\n", encoding="utf-8")
            resource.write_text("Unused.\n", encoding="utf-8")

            documents = catalog_auditor.reachable_documents(skill / "SKILL.md")

            self.assertFalse(catalog_auditor.resource_is_referenced(resource, documents))


if __name__ == "__main__":
    unittest.main()
