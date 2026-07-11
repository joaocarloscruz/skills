[CmdletBinding(SupportsShouldProcess)]
param(
    [string]$Destination,
    [ValidateSet("Symlink", "Copy")]
    [string]$Mode = "Symlink",
    [ValidateSet("Routers", "Library", "All")]
    [string]$Profile = "Routers",
    [string[]]$Skills = @(),
    [switch]$Force,
    [switch]$Prune,
    [switch]$List
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repositoryRoot = Split-Path -Parent $PSScriptRoot
$skillsRoot = Join-Path $repositoryRoot "skills"
$libraryRoot = Join-Path $repositoryRoot "library"
$availableRouters = @(
    Get-ChildItem -LiteralPath $skillsRoot -Directory |
        Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName "SKILL.md") -PathType Leaf } |
        Sort-Object Name
)
$availableLibrary = @(
    Get-ChildItem -LiteralPath $libraryRoot -Directory |
        Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName "SKILL.md") -PathType Leaf } |
        Sort-Object Name
)
$availableSkills = @($availableRouters + $availableLibrary)

if ($List) {
    $availableRouters | ForEach-Object { [pscustomobject]@{ Type = "Router"; Name = $_.Name } }
    $availableLibrary | ForEach-Object { [pscustomobject]@{ Type = "Workflow"; Name = $_.Name } }
    return
}

if (-not $Destination) {
    $codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
    $Destination = Join-Path $codexHome "skills"
}

$byName = @{}
foreach ($skill in $availableSkills) {
    $byName[$skill.Name] = $skill
}

if ($Skills.Count -eq 0 -or $Skills -contains "*") {
    $selectedSkills = switch ($Profile) {
        "Routers" { $availableRouters }
        "Library" { $availableLibrary }
        "All" { $availableSkills }
    }
}
else {
    $unknownSkills = @($Skills | Where-Object { -not $byName.ContainsKey($_) })
    if ($unknownSkills) {
        throw "Unknown skill(s): $($unknownSkills -join ', '). Run .\scripts\install.ps1 -List to see available skills."
    }

    $selectedSkills = @()
    $seen = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
    foreach ($skillName in $Skills) {
        if ($seen.Add($skillName)) {
            $selectedSkills += $byName[$skillName]
        }
    }
}

$selectedNames = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
foreach ($skill in $selectedSkills) {
    [void]$selectedNames.Add($skill.Name)
}

if (-not (Test-Path -LiteralPath $Destination -PathType Container)) {
    if ($PSCmdlet.ShouldProcess($Destination, "Create skills destination")) {
        New-Item -ItemType Directory -Path $Destination -Force | Out-Null
    }
}

$destinationRoot = [System.IO.Path]::GetFullPath($Destination)
$conflicts = @()

if ($Prune -and (Test-Path -LiteralPath $destinationRoot -PathType Container)) {
    foreach ($skill in $availableSkills) {
        if ($selectedNames.Contains($skill.Name)) {
            continue
        }
        $target = Join-Path $destinationRoot $skill.Name
        if (Test-Path -LiteralPath $target) {
            if ($PSCmdlet.ShouldProcess($target, "Remove unselected catalog skill")) {
                Remove-Item -LiteralPath $target -Recurse -Force
                Write-Output "Pruned: $($skill.Name)"
            }
        }
    }
}

foreach ($skill in $selectedSkills) {
    $source = (Resolve-Path -LiteralPath $skill.FullName).Path
    $target = Join-Path $destinationRoot $skill.Name
    if (-not (Test-Path -LiteralPath $target)) {
        continue
    }

    $existing = Get-Item -LiteralPath $target -Force
    $isCurrentLink = $Mode -eq "Symlink" -and $existing.LinkType -eq "SymbolicLink" -and $existing.Target -ieq $source
    if (-not $isCurrentLink) {
        $conflicts += $target
    }
}

if ($conflicts -and -not $Force) {
    throw "Existing skill destination(s): $($conflicts -join ', '). Re-run with -Force to replace only these paths."
}

foreach ($skill in $selectedSkills) {
    $source = (Resolve-Path -LiteralPath $skill.FullName).Path
    $target = Join-Path $destinationRoot $skill.Name

    if (Test-Path -LiteralPath $target) {
        $existing = Get-Item -LiteralPath $target -Force
        $isCurrentLink = $Mode -eq "Symlink" -and $existing.LinkType -eq "SymbolicLink" -and $existing.Target -ieq $source
        if ($isCurrentLink) {
            Write-Output "Already linked: $($skill.Name)"
            continue
        }

        if ($PSCmdlet.ShouldProcess($target, "Replace existing skill")) {
            Remove-Item -LiteralPath $target -Recurse -Force
        }
    }

    if ($Mode -eq "Symlink") {
        if ($PSCmdlet.ShouldProcess($target, "Create symbolic link to $source")) {
            try {
                New-Item -ItemType SymbolicLink -Path $target -Target $source | Out-Null
            }
            catch [System.UnauthorizedAccessException] {
                throw "Cannot create a symbolic link at $target. Enable Windows Developer Mode or run PowerShell as Administrator, or use -Mode Copy."
            }
            Write-Output "Linked: $($skill.Name)"
        }
    }
    else {
        if ($PSCmdlet.ShouldProcess($target, "Copy skill from $source")) {
            Copy-Item -LiteralPath $source -Destination $destinationRoot -Recurse
            Write-Output "Copied: $($skill.Name)"
        }
    }
}
