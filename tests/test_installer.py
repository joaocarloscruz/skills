from __future__ import annotations

import base64
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POWERSHELL = os.environ.get("SKILLS_TEST_POWERSHELL") or shutil.which("pwsh") or shutil.which("powershell")
MANIFEST = ".skills-install-manifest.json"


def ps_quote(value: str | Path) -> str:
    return "'" + str(value).replace("'", "''") + "'"


@unittest.skipUnless(POWERSHELL, "PowerShell is required for installer integration tests")
class InstallerTests(unittest.TestCase):
    def setUp(self) -> None:
        # All actual writes and removals stay in a disposable sibling of the
        # checkout, never in the user's installed skill directory.
        self.temporary = tempfile.TemporaryDirectory(prefix="installer-test-", dir=ROOT.parent)
        self.addCleanup(self.temporary.cleanup)
        self.scratch = Path(self.temporary.name).resolve()
        self.repo = self.scratch / "repo"
        self.destination = self.scratch / "installed"
        (self.repo / "scripts").mkdir(parents=True)
        shutil.copy2(ROOT / "scripts" / "install.ps1", self.repo / "scripts" / "install.ps1")
        for directory, name in (("skills", "operations"), ("library", "tdd"), ("library", "test-cli")):
            package = self.repo / directory / name
            package.mkdir(parents=True)
            (package / "SKILL.md").write_text(f"---\nname: {name}\n---\nOriginal.\n", encoding="utf-8")
            (package / "references").mkdir()
            (package / "references" / "example.txt").write_text("example", encoding="utf-8")

    def run_ps(self, command: str) -> subprocess.CompletedProcess[str]:
        encoded = base64.b64encode(command.encode("utf-16-le")).decode("ascii")
        return subprocess.run(
            # Process-only policy permits these locally generated fixtures;
            # it never changes the user's saved PowerShell execution policy.
            [POWERSHELL, "-NoLogo", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "RemoteSigned", "-EncodedCommand", encoded],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )

    def install(self, *flags: str, skills: tuple[str, ...] | None = ("tdd",),
                mode: str = "Copy", destination: Path | None = None, ok: bool = True):
        arguments = f"-Destination {ps_quote(destination or self.destination)} -Mode {mode}"
        if skills is not None:
            arguments += " -Skills @(" + ",".join(ps_quote(name) for name in skills) + ")"
        result = self.run_ps(f"& {ps_quote(self.repo / 'scripts' / 'install.ps1')} {arguments} {' '.join(flags)}")
        if ok:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def manifest(self):
        return json.loads((self.destination / MANIFEST).read_text(encoding="utf-8-sig"))

    def link(self, target: Path, source: Path) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            target.symlink_to(source, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"Directory symlink privileges unavailable: {error}")

    def test_copy_and_repeat_preserve_installed_files(self):
        self.install()
        installed = self.destination / "tdd" / "SKILL.md"
        stamp = installed.stat().st_mtime_ns
        manifest_stamp = (self.destination / MANIFEST).stat().st_mtime_ns
        self.assertEqual(installed.read_bytes(), (self.repo / "library/tdd/SKILL.md").read_bytes())
        self.assertEqual(self.manifest()["entries"][0]["name"], "tdd")
        result = self.install()
        self.assertIn("Already current", result.stdout)
        self.assertEqual(installed.stat().st_mtime_ns, stamp)
        self.assertEqual((self.destination / MANIFEST).stat().st_mtime_ns, manifest_stamp)
        self.assertFalse(list(self.destination.glob(".skills-install-stage-*")))

    def test_prune_only_removes_unchanged_owned_copies(self):
        self.install()
        unowned = self.destination / "test-cli"
        unowned.mkdir()
        (unowned / "mine.txt").write_text("not from this catalog")
        self.install("-Prune", skills=None)
        self.assertFalse((self.destination / "tdd").exists())
        self.assertEqual((unowned / "mine.txt").read_text(), "not from this catalog")
        self.assertEqual([item["name"] for item in self.manifest()["entries"]], ["operations"])

    def test_modified_owned_copy_is_preserved_on_prune(self):
        self.install()
        changed = self.destination / "tdd" / "SKILL.md"
        changed.write_text("local modifications")
        result = self.install("-Prune", skills=None)
        self.assertIn("Preserving modified", result.stdout + result.stderr)
        self.assertEqual(changed.read_text(), "local modifications")

    def test_collision_is_rejected_before_any_prune_or_manifest_change(self):
        self.install()
        manifest_before = (self.destination / MANIFEST).read_bytes()
        conflict = self.destination / "operations"
        conflict.mkdir()
        (conflict / "mine.txt").write_text("keep")
        self.install("-Prune", skills=None, ok=False)
        self.assertTrue((self.destination / "tdd/SKILL.md").is_file())
        self.assertEqual((conflict / "mine.txt").read_text(), "keep")
        self.assertEqual((self.destination / MANIFEST).read_bytes(), manifest_before)

    def test_force_explicitly_replaces_selected_unowned_directory(self):
        foreign = self.destination / "tdd"
        foreign.mkdir(parents=True)
        (foreign / "mine.txt").write_text("selected replacement")
        self.install(ok=False)
        self.install("-Force")
        self.assertFalse((foreign / "mine.txt").exists())
        self.assertTrue((foreign / "SKILL.md").is_file())

    def test_whatif_creates_nothing_and_does_not_prune(self):
        self.install("-WhatIf")
        self.assertFalse(self.destination.exists())
        self.install()
        before = (self.destination / MANIFEST).read_bytes()
        self.install("-Prune", "-WhatIf", skills=None)
        self.assertTrue((self.destination / "tdd/SKILL.md").is_file())
        self.assertFalse((self.destination / "operations").exists())
        self.assertEqual((self.destination / MANIFEST).read_bytes(), before)

    def test_rejects_repository_destination_and_ancestors(self):
        for destination in (self.repo, self.repo / "library", self.repo / "library/tdd", self.scratch):
            with self.subTest(destination=destination):
                self.install("-Force", "-Prune", destination=destination, ok=False)
        self.assertTrue((self.repo / "library/tdd/SKILL.md").is_file())

    def test_unknown_skill_has_no_side_effects(self):
        self.install(skills=("does-not-exist",), ok=False)
        self.assertFalse(self.destination.exists())

    def test_duplicate_skill_names_are_installed_once(self):
        self.install(skills=("tdd", "TDD", "tdd"))
        self.assertEqual(len(self.manifest()["entries"]), 1)

    def test_invalid_or_foreign_manifest_prevents_changes(self):
        self.destination.mkdir()
        manifest = self.destination / MANIFEST
        for body in ("{", json.dumps({"schema_version": 1, "catalog_id": "another/repo", "entries": []}),
                     json.dumps({"schema_version": 1, "catalog_id": "github.com/joaocarloscruz/skills", "entries": [
                         {"name": "../escape", "source": str(self.repo), "mode": "Copy", "fingerprint": "a" * 64}]})):
            with self.subTest(body=body):
                manifest.write_text(body)
                self.install("-Force", "-Prune", ok=False)
                self.assertEqual(manifest.read_text(), body)
                self.assertFalse((self.destination / "tdd").exists())

    def test_manifest_rejects_coerced_versions_and_nonobject_shapes(self):
        self.destination.mkdir()
        manifest = self.destination / MANIFEST
        base = {"schema_version": 1, "catalog_id": "github.com/joaocarloscruz/skills", "entries": []}
        malformed = [dict(base, schema_version=value) for value in (True, "1", 1.0)]
        malformed += [[base], dict(base, entries={}), dict(base, entries=["tdd"])]
        record = {"name": "tdd", "source": str(self.repo / "library/tdd"), "mode": "Copy", "fingerprint": "a" * 64}
        malformed += [dict(base, entries=[dict(record, **{key: [value]})]) for key, value in record.items()]
        for body in malformed:
            with self.subTest(body=body):
                serialized = json.dumps(body)
                manifest.write_text(serialized)
                self.install("-Force", "-Prune", ok=False)
                self.assertEqual(manifest.read_text(), serialized)
                self.assertFalse((self.destination / "tdd").exists())

    def test_legacy_current_symlink_is_adopted_and_prunable(self):
        self.link(self.destination / "tdd", self.repo / "library/tdd")
        self.install(mode="Symlink")
        self.assertEqual(self.manifest()["entries"][0]["mode"], "Symlink")
        self.install("-Prune", skills=None)
        self.assertFalse(os.path.lexists(self.destination / "tdd"))
        self.assertTrue((self.repo / "library/tdd/SKILL.md").is_file())

    def test_new_symlink_and_repeat(self):
        probe = self.scratch / "probe"
        self.link(probe, self.repo / "library/tdd")
        probe.unlink()
        self.install(mode="Symlink")
        self.assertTrue((self.destination / "tdd").is_symlink())
        self.install(mode="Symlink")
        self.assertEqual((self.destination / "tdd").resolve(), self.repo / "library/tdd")

    def test_broken_unknown_symlink_requires_force_and_removes_only_link(self):
        missing = self.scratch / "missing"
        self.link(self.destination / "tdd", missing)
        self.install(ok=False)
        self.install("-Force")
        self.assertFalse(missing.exists())
        self.assertFalse((self.destination / "tdd").is_symlink())
        self.assertTrue((self.destination / "tdd/SKILL.md").is_file())

    def test_force_does_not_follow_nested_symlink(self):
        foreign = self.scratch / "foreign"
        foreign.mkdir()
        (foreign / "precious.txt").write_text("preserve")
        self.link(self.destination / "tdd" / "nested", foreign)
        self.install("-Force")
        self.assertEqual((foreign / "precious.txt").read_text(), "preserve")

    def test_reparse_destination_and_manifest_are_rejected(self):
        real = self.scratch / "real"
        real.mkdir()
        self.link(self.destination, real)
        self.install(ok=False)
        self.assertFalse(list(real.iterdir()))
        self.destination.unlink()
        self.destination.mkdir()
        outside = self.scratch / "outside.json"
        outside.write_text("preserve")
        try:
            (self.destination / MANIFEST).symlink_to(outside)
        except OSError as error:
            self.skipTest(str(error))
        self.install(ok=False)
        self.assertEqual(outside.read_text(), "preserve")

    def test_default_profile_and_force_refresh(self):
        self.install(skills=None)
        self.assertTrue((self.destination / "operations/SKILL.md").is_file())
        source = self.repo / "skills/operations/SKILL.md"
        source.write_text("new source")
        self.install(skills=None, ok=False)
        self.install("-Force", skills=None)
        self.assertEqual((self.destination / "operations/SKILL.md").read_text(), "new source")

    @unittest.skipUnless(os.name == "nt", "Junctions are Windows-specific")
    def test_junction_replacement_never_deletes_external_target(self):
        foreign = self.scratch / "foreign"
        foreign.mkdir()
        (foreign / "precious.txt").write_text("preserve")
        (self.destination / "tdd").mkdir(parents=True)
        junction = self.destination / "tdd/nested"
        result = self.run_ps(f"New-Item -ItemType Junction -Path {ps_quote(junction)} -Target {ps_quote(foreign)} | Out-Null")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.install("-Force")
        self.assertEqual((foreign / "precious.txt").read_text(), "preserve")

    @unittest.skipUnless(os.name == "nt", "Junctions are Windows-specific")
    def test_junction_destination_ancestor_is_rejected(self):
        foreign = self.scratch / "foreign"
        foreign.mkdir()
        result = self.run_ps(f"New-Item -ItemType Junction -Path {ps_quote(self.destination)} -Target {ps_quote(foreign)} | Out-Null")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.install(destination=self.destination / "nested", ok=False)
        self.assertFalse(list(foreign.iterdir()))

    def test_staging_failure_preserves_existing_installation(self):
        self.install()
        before = (self.destination / MANIFEST).read_bytes()
        command = (
            "function New-Item { [CmdletBinding()] param([string]$ItemType, [string]$Path, [string]$Target, [switch]$Force) "
            "if ($ItemType -eq 'SymbolicLink') { throw 'Injected link-creation failure' }; "
            "Microsoft.PowerShell.Management\\New-Item @PSBoundParameters }; "
            f"& {ps_quote(self.repo / 'scripts/install.ps1')} -Destination {ps_quote(self.destination)} -Skills tdd -Mode Symlink -Force"
        )
        result = self.run_ps(command)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Injected link-creation failure", result.stdout + result.stderr)
        self.assertEqual((self.destination / MANIFEST).read_bytes(), before)
        self.assertTrue((self.destination / "tdd/SKILL.md").is_file())
        self.assertFalse(list(self.destination.glob(".skills-install-stage-*")))

    def test_failed_replacement_rolls_back_original_directory(self):
        old = self.destination / "tdd"
        old.mkdir(parents=True)
        (old / "mine.txt").write_text("preserve")
        command = (
            "function Move-Item { [CmdletBinding()] param([string]$LiteralPath, [string]$Destination, [switch]$Force) "
            "if ($LiteralPath.EndsWith('new-tdd')) { throw 'Injected replacement failure' }; "
            "Microsoft.PowerShell.Management\\Move-Item @PSBoundParameters }; "
            f"& {ps_quote(self.repo / 'scripts/install.ps1')} -Destination {ps_quote(self.destination)} -Skills tdd -Mode Copy -Force"
        )
        result = self.run_ps(command)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Injected replacement failure", result.stdout + result.stderr)
        self.assertEqual((old / "mine.txt").read_text(), "preserve")
        self.assertFalse((self.destination / MANIFEST).exists())
        self.assertFalse(list(self.destination.glob(".skills-install-stage-*")))

    def test_manifest_commit_failure_restores_files_and_ownership(self):
        self.install()
        before = (self.destination / MANIFEST).read_bytes()
        original = (self.destination / "tdd/SKILL.md").read_bytes()
        (self.repo / "library/tdd/SKILL.md").write_text("updated source")
        command = (
            "function Move-Item { [CmdletBinding()] param([string]$LiteralPath, [string]$Destination, [switch]$Force) "
            "if ([IO.Path]::GetFileName($LiteralPath) -eq 'manifest.json') { throw 'Injected manifest failure' }; "
            "Microsoft.PowerShell.Management\\Move-Item @PSBoundParameters }; "
            f"& {ps_quote(self.repo / 'scripts/install.ps1')} -Destination {ps_quote(self.destination)} -Skills tdd -Mode Copy -Force"
        )
        result = self.run_ps(command)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Injected manifest failure", result.stdout + result.stderr)
        self.assertEqual((self.destination / MANIFEST).read_bytes(), before)
        self.assertEqual((self.destination / "tdd/SKILL.md").read_bytes(), original)
        self.assertFalse(list(self.destination.glob(".skills-install-stage-*")))


if __name__ == "__main__":
    unittest.main()
