from __future__ import annotations

import base64
import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import check as runner


class CheckRunnerTests(unittest.TestCase):
    def run_main(self, args=(), powershell=None, command_status=0):
        with tempfile.TemporaryDirectory() as directory, contextlib.ExitStack() as stack:
            stdout, stderr = io.StringIO(), io.StringIO()
            stack.enter_context(mock.patch.object(runner, "ROOT", Path(directory)))
            stack.enter_context(mock.patch.object(runner, "find_powershell", return_value=powershell))
            stack.enter_context(mock.patch.object(sys, "argv", ["check", *args]))
            process = stack.enter_context(mock.patch.object(runner.subprocess, "run", return_value=subprocess.CompletedProcess([], command_status)))
            stack.enter_context(contextlib.redirect_stdout(stdout))
            stack.enter_context(contextlib.redirect_stderr(stderr))
            result = runner.main()
            return result, stdout.getvalue(), stderr.getvalue(), process.call_args_list

    def test_required_powershell_fails_before_running_checks(self):
        result, _, stderr, calls = self.run_main(("--require-powershell",))
        self.assertEqual(result, 1)
        self.assertIn("PowerShell is unavailable", stderr)
        self.assertEqual(calls, [])

    def test_optional_powershell_skip_is_visible_in_final_coverage(self):
        result, stdout, _, calls = self.run_main()
        self.assertEqual(result, 0)
        self.assertIn("PowerShell checks were skipped", stdout)
        self.assertNotIn("All repository checks passed", stdout)
        self.assertTrue(calls)

    def test_failed_check_stops_the_runner(self):
        result, _, _, calls = self.run_main(powershell="pwsh", command_status=1)
        self.assertEqual(result, 1)
        self.assertEqual(len(calls), 1)

    @unittest.skipUnless(runner.find_powershell(), "PowerShell required for real parser regression")
    def test_powershell_parser_accepts_valid_and_rejects_invalid_installer(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "scripts").mkdir()
            installer = root / "scripts" / "install.ps1"
            encoded = base64.b64encode(runner.INSTALLER_PARSE_SCRIPT.encode("utf-16-le")).decode("ascii")
            for source, expected in [("Write-Output 'valid'\n", 0), ("function Broken {\n", 1)]:
                with self.subTest(source=source):
                    installer.write_text(source, encoding="utf-8")
                    result = subprocess.run(
                        [runner.find_powershell(), "-NoLogo", "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded],
                        cwd=root, capture_output=True, timeout=30,
                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
                    )
                    self.assertEqual(result.returncode, expected, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
