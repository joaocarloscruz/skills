#!/usr/bin/env python3
"""Run repository checks locally and in CI on Windows or Linux."""
from __future__ import annotations

import argparse
import base64
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALLER_PARSE_SCRIPT = """
$tokens = $null
$parseErrors = $null
$installer = Join-Path (Get-Location).Path 'scripts/install.ps1'
[void][System.Management.Automation.Language.Parser]::ParseFile(
    $installer, [ref]$tokens, [ref]$parseErrors
)
if ($parseErrors) {
    $parseErrors | Format-List | Out-String | Write-Error
    exit 1
}
Write-Output 'PowerShell installer syntax is valid.'
"""


def find_powershell() -> str | None:
    configured = os.environ.get('SKILLS_TEST_POWERSHELL')
    if configured:
        executable = shutil.which(configured)
        if not executable:
            raise ValueError(f'SKILLS_TEST_POWERSHELL does not identify an executable: {configured}')
        return executable
    return shutil.which('pwsh') or shutil.which('powershell')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--official', action='store_true', help='Also require the installed agentskills reference validator')
    parser.add_argument('--require-powershell', action='store_true', help='Fail instead of skipping installer checks when PowerShell is unavailable')
    args = parser.parse_args()
    try:
        powershell = find_powershell()
    except ValueError as error:
        print(error, file=sys.stderr)
        return 1
    if not powershell:
        message = 'PowerShell is unavailable; installer syntax and integration checks cannot run.'
        if args.require_powershell:
            print(message, file=sys.stderr)
            return 1
        print('SKIP: ' + message + ' Use --require-powershell for CI-equivalent coverage.', flush=True)

    commands = [
        [sys.executable, 'scripts/validate_skills.py'],
        [sys.executable, 'scripts/build_router_bundles.py', '--check'],
        [sys.executable, 'library/audit-skill-catalog/scripts/audit_catalog.py', 'library', '--fail-on-warning'],
        [sys.executable, 'library/audit-skill-catalog/scripts/audit_catalog.py', 'skills', '--fail-on-warning'],
        [sys.executable, 'scripts/validate_activation_cases.py'],
        [sys.executable, 'scripts/validate_evidence_registry.py'],
    ]
    if powershell:
        encoded = base64.b64encode(INSTALLER_PARSE_SCRIPT.encode('utf-16-le')).decode('ascii')
        commands.append([powershell, '-NoLogo', '-NoProfile', '-NonInteractive', '-EncodedCommand', encoded])
    commands.append([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_*.py'])
    commands.append([sys.executable, '-m', 'unittest', 'discover', '-s', 'evals/smoke', '-p', 'test_*.py'])
    if args.official:
        validator = shutil.which('agentskills')
        if not validator:
            print('Missing agentskills: install skills-ref==0.1.1 in an isolated environment.', file=sys.stderr)
            return 1
        commands += [[validator, 'validate', str(path.parent)] for directory in ('skills', 'library')
                     for path in sorted((ROOT / directory).glob('*/SKILL.md'))]
    try:
        for command in commands:
            # EncodedCommand keeps quoting portable; print the purpose, not base64.
            label = 'PowerShell installer syntax' if powershell and command[0] == powershell else ' '.join(command)
            print('Running: ' + label, flush=True)
            if subprocess.run(command, cwd=ROOT, check=False).returncode:
                return 1
        for directory in ('scripts', 'library', 'skills', 'tests', 'evals'):
            for path in (ROOT / directory).rglob('*.py'):
                compile(path.read_text(encoding='utf-8'), str(path), 'exec')
    except (OSError, UnicodeError, SyntaxError) as error:
        print(f'Repository check failed: {error}', file=sys.stderr)
        return 1
    coverage = 'All repository checks passed.' if powershell else 'Available checks passed; PowerShell checks were skipped.'
    print(coverage + ' Structural checks do not prove agent effectiveness.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
