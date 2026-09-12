[CmdletBinding(SupportsShouldProcess)]
param(
    [string]$Destination,
    [ValidateSet("Symlink", "Copy")][string]$Mode = "Symlink",
    [ValidateSet("Routers", "Library", "All")][string]$Profile = "Routers",
    [string[]]$Skills = @(),
    [switch]$Force,
    [switch]$Prune,
    [switch]$List
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$pathComparison = if ([IO.Path]::DirectorySeparatorChar -eq '\') { [StringComparison]::OrdinalIgnoreCase } else { [StringComparison]::Ordinal }
$catalogId = "github.com/joaocarloscruz/skills"

function Get-FullPath([string]$Path) {
    $full = [IO.Path]::GetFullPath($Path)
    if ($full -ne [IO.Path]::GetPathRoot($full)) { $full = $full.TrimEnd([char[]]@('/', '\')) }
    return $full
}

function Test-Within([string]$Path, [string]$Root) {
    $prefix = $Root.TrimEnd([char[]]@('/', '\')) + [IO.Path]::DirectorySeparatorChar
    return $Path.Equals($Root, $pathComparison) -or $Path.StartsWith($prefix, $pathComparison)
}

# Enumerating the parent identifies dangling links even on older PowerShell.
function Get-Entry([string]$Path) {
    $parent = [IO.Path]::GetDirectoryName($Path)
    if (-not $parent) { return Get-Item -LiteralPath $Path -Force -ErrorAction Stop }
    if (-not [IO.Directory]::Exists($parent)) { return $null }
    $name = [IO.Path]::GetFileName($Path)
    return Get-ChildItem -LiteralPath $parent -Force -ErrorAction Stop |
        Where-Object { $_.Name.Equals($name, $pathComparison) } | Select-Object -First 1
}

function Test-Reparse($Entry) {
    return ($null -ne $Entry -and ($Entry.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)
}

function Assert-PlainAncestors([string]$Path) {
    $cursor = $Path
    while ($cursor) {
        $entry = Get-Entry $cursor
        if (Test-Reparse $entry) { throw "Refusing reparse-point destination or ancestor: $cursor. Use its real directory path instead." }
        if ($entry -and -not $entry.PSIsContainer) { throw "Expected a directory: $cursor" }
        $cursor = [IO.Path]::GetDirectoryName($cursor)
    }
}

function Get-LinkSource($Entry) {
    if (-not (Test-Reparse $Entry) -or $Entry.LinkType -ne "SymbolicLink") { return $null }
    $targets = @($Entry.Target)
    if ($targets.Count -ne 1 -or -not $targets[0]) { return $null }
    $linkTarget = [string]$targets[0]
    if (-not [IO.Path]::IsPathRooted($linkTarget)) { $linkTarget = Join-Path ([IO.Path]::GetDirectoryName($Entry.FullName)) $linkTarget }
    return Get-FullPath $linkTarget
}

function Get-FileDigest([string]$Path) {
    $sha = [Security.Cryptography.SHA256]::Create()
    $stream = [IO.File]::OpenRead($Path)
    try { return ([BitConverter]::ToString($sha.ComputeHash($stream))).Replace('-', '').ToLowerInvariant() }
    finally { $stream.Dispose(); $sha.Dispose() }
}

function Get-TreeHash([string]$Path, [switch]$RejectLinks) {
    $records = [Collections.Generic.List[string]]::new()
    $pending = [Collections.Generic.Stack[string]]::new()
    $pending.Push($Path)
    while ($pending.Count) {
        $current = $pending.Pop()
        $entry = Get-Entry $current
        if (-not $entry) { throw "Path disappeared during inspection: $current" }
        $relative = $current.Substring($Path.Length).Replace('\', '/')
        if (Test-Reparse $entry) {
            if ($RejectLinks) { throw "Skill source contains a reparse point: $current" }
            $records.Add((@('link', $relative, [string]$entry.LinkType, @($entry.Target)) | ConvertTo-Json -Compress -Depth 4))
        }
        elseif ($entry.PSIsContainer) {
            $records.Add((@('directory', $relative) | ConvertTo-Json -Compress))
            foreach ($child in @(Get-ChildItem -LiteralPath $current -Force)) { $pending.Push($child.FullName) }
        }
        else { $records.Add((@('file', $relative, (Get-FileDigest $current)) | ConvertTo-Json -Compress)) }
    }
    $ordered = $records.ToArray()
    [Array]::Sort($ordered, [StringComparer]::Ordinal)
    $sha = [Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($sha.ComputeHash([Text.Encoding]::UTF8.GetBytes(($ordered -join "`n"))))).Replace('-', '').ToLowerInvariant() }
    finally { $sha.Dispose() }
}

function Assert-ScopedPath([string]$Path) {
    $absolute = Get-FullPath $Path
    if ($absolute.Equals($destinationRoot, $pathComparison) -or -not (Test-Within $absolute $destinationRoot)) { throw "Refusing operation outside the skills destination: $absolute" }
    Assert-PlainAncestors ([IO.Path]::GetDirectoryName($absolute))
}

# Never recurse through junctions or links, including nested links in a -Force
# replacement. Every deletion is verified against the destination root.
function Remove-ScopedTree([string]$Path) {
    Assert-ScopedPath $Path
    $entry = Get-Entry $Path
    if (-not $entry) { return }
    if (Test-Reparse $entry) {
        if (($entry.Attributes -band [IO.FileAttributes]::Directory) -ne 0) { [IO.Directory]::Delete($Path) }
        else { [IO.File]::Delete($Path) }
    }
    elseif ($entry.PSIsContainer) {
        foreach ($child in @(Get-ChildItem -LiteralPath $Path -Force)) { Remove-ScopedTree $child.FullName }
        Remove-Item -LiteralPath $Path -Force
    }
    else { Remove-Item -LiteralPath $Path -Force }
}

function Move-ScopedEntry([string]$Source, [string]$Target) {
    Assert-ScopedPath $Source
    Assert-ScopedPath $Target
    Move-Item -LiteralPath $Source -Destination $Target -Force
}

$repositoryRoot = Get-FullPath (Split-Path -Parent $PSScriptRoot)
$availableRouters = @(Get-ChildItem -LiteralPath (Join-Path $repositoryRoot 'skills') -Directory |
    Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'SKILL.md') -PathType Leaf } | Sort-Object Name)
$availableLibrary = @(Get-ChildItem -LiteralPath (Join-Path $repositoryRoot 'library') -Directory |
    Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'SKILL.md') -PathType Leaf } | Sort-Object Name)
$availableSkills = @($availableRouters + $availableLibrary)
if ($List) {
    $availableRouters | ForEach-Object { [pscustomobject]@{ Type = 'Router'; Name = $_.Name } }
    $availableLibrary | ForEach-Object { [pscustomobject]@{ Type = 'Workflow'; Name = $_.Name } }
    return
}

if (-not $Destination) {
    $codexDirectory = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
    $Destination = Join-Path $codexDirectory 'skills'
}
$destinationRoot = Get-FullPath $Destination
if ((Test-Within $destinationRoot $repositoryRoot) -or (Test-Within $repositoryRoot $destinationRoot)) { throw "Destination must be outside the repository and must not contain it: $destinationRoot" }
Assert-PlainAncestors $destinationRoot

$byName = @{}
foreach ($skill in $availableSkills) {
    if ($skill.Name -cnotmatch '^[a-z0-9]+(-[a-z0-9]+)*$' -or $byName.ContainsKey($skill.Name)) { throw "Invalid or duplicate skill name: $($skill.Name)" }
    $byName[$skill.Name] = $skill
}
if ($Skills.Count -eq 0 -or $Skills -contains '*') {
    $selectedSkills = @(switch ($Profile) { 'Routers' { $availableRouters }; 'Library' { $availableLibrary }; 'All' { $availableSkills } })
}
else {
    $unknown = @($Skills | Where-Object { -not $byName.ContainsKey($_) })
    if ($unknown.Count) { throw "Unknown skill(s): $($unknown -join ', '). Run install.ps1 -List to see available skills." }
    $seen = @{}
    $selectedSkills = @($Skills | ForEach-Object { if (-not $seen.ContainsKey($_)) { $seen[$_] = $true; $byName[$_] } })
}

$manifestPath = Join-Path $destinationRoot '.skills-install-manifest.json'
$manifestEntry = Get-Entry $manifestPath
$manifestText = $null
$manifestHash = $null
$entries = @{}
if ($manifestEntry) {
    if ($manifestEntry.PSIsContainer -or (Test-Reparse $manifestEntry)) { throw "Ownership manifest must be a regular file: $manifestPath" }
    $manifestText = Get-Content -LiteralPath $manifestPath -Raw
    $manifestHash = Get-FileDigest $manifestPath
    if (-not $manifestText.TrimStart().StartsWith('{')) { throw "Ownership manifest must be a JSON object: $manifestPath" }
    $manifest = $manifestText | ConvertFrom-Json
    if ($manifest -isnot [Management.Automation.PSCustomObject] -or
        -not ($manifest.schema_version -is [int] -or $manifest.schema_version -is [long]) -or
        $manifest.schema_version -ne 1 -or $manifest.catalog_id -isnot [string] -or
        $manifest.catalog_id -cne $catalogId -or $manifest.entries -isnot [array] -or
        @($manifest.PSObject.Properties.Name | Where-Object { $_ -cnotin @('schema_version', 'catalog_id', 'entries') }).Count) {
        throw "Unsupported, invalid or foreign ownership manifest: $manifestPath"
    }
    foreach ($record in @($manifest.entries)) {
        if ($record -isnot [Management.Automation.PSCustomObject] -or
            $record.name -isnot [string] -or $record.name.Length -gt 64 -or
            $record.name -cnotmatch '^[a-z0-9]+(-[a-z0-9]+)*$' -or $entries.ContainsKey($record.name) -or
            $record.mode -isnot [string] -or $record.mode -cnotin @('Copy', 'Symlink') -or
            $record.source -isnot [string] -or -not [IO.Path]::IsPathRooted($record.source) -or
            ($record.mode -eq 'Copy' -and ($record.fingerprint -isnot [string] -or $record.fingerprint -cnotmatch '^[a-f0-9]{64}$')) -or
            ($record.mode -eq 'Symlink' -and $null -ne $record.fingerprint) -or
            @($record.PSObject.Properties.Name | Where-Object { $_ -cnotin @('name', 'mode', 'source', 'fingerprint') }).Count) {
            throw "Invalid ownership record in $manifestPath"
        }
        $entries[$record.name] = $record
    }
}

# A legacy link to this exact checkout has independently verifiable ownership.
# Legacy copies and same-name third-party skills are never claimed by name.
foreach ($skill in $availableSkills) {
    if (-not $entries.ContainsKey($skill.Name)) {
        $link = Get-LinkSource (Get-Entry (Join-Path $destinationRoot $skill.Name))
        if ($link -and $link.Equals($skill.FullName, $pathComparison)) { $entries[$skill.Name] = [pscustomobject]@{ name = $skill.Name; source = $link; mode = 'Symlink'; fingerprint = $null } }
    }
}

$plan = [Collections.Generic.List[object]]::new()
$selectedNames = @{}
foreach ($skill in $selectedSkills) {
    $selectedNames[$skill.Name] = $true
    $source = Get-FullPath $skill.FullName
    Assert-PlainAncestors $source
    $fingerprint = Get-TreeHash $source -RejectLinks
    $target = Join-Path $destinationRoot $skill.Name
    Assert-ScopedPath $target
    $existing = Get-Entry $target
    $snapshot = if ($existing) { Get-TreeHash $target } else { $null }
    $link = Get-LinkSource $existing
    $sameLink = $Mode -eq 'Symlink' -and $link -and $link.Equals($source, $pathComparison)
    $sameCopy = $Mode -eq 'Copy' -and $existing -and -not (Test-Reparse $existing) -and
        $entries.ContainsKey($skill.Name) -and $entries[$skill.Name].mode -eq 'Copy' -and
        $snapshot -eq $entries[$skill.Name].fingerprint -and $snapshot -eq $fingerprint
    if ($existing -and -not $sameLink -and -not $sameCopy -and -not $Force) { throw "Existing skill destination: $target. -Force explicitly replaces this selected path, including unrelated contents." }
    $action = if ($sameLink -or $sameCopy) { 'Keep' } else { 'Install' }
    $plan.Add([pscustomobject]@{ name = $skill.Name; action = $action; source = $source; target = $target; snapshot = $snapshot; fingerprint = $fingerprint })
}

if ($Prune) {
    foreach ($name in @($entries.Keys | Sort-Object)) {
        if ($selectedNames.ContainsKey($name)) { continue }
        $target = Join-Path $destinationRoot $name
        Assert-ScopedPath $target
        $existing = Get-Entry $target
        if (-not $existing) { $entries.Remove($name); continue }
        $record = $entries[$name]
        $snapshot = Get-TreeHash $target
        $link = Get-LinkSource $existing
        $owned = if ($record.mode -eq 'Symlink') { $link -and $link.Equals((Get-FullPath $record.source), $pathComparison) }
            else { -not (Test-Reparse $existing) -and $snapshot -eq $record.fingerprint }
        if ($owned) { $plan.Add([pscustomobject]@{ name = $name; action = 'Prune'; target = $target; snapshot = $snapshot }) }
        else { Write-Warning "Preserving modified or replaced skill: $target" }
    }
}

# Build the final metadata before any mutation, including legacy-link adoption.
foreach ($item in $plan) {
    if ($item.action -eq 'Prune') { $entries.Remove($item.name) }
    else { $entries[$item.name] = [pscustomobject]@{ name = $item.name; source = $item.source; mode = $Mode; fingerprint = $(if ($Mode -eq 'Copy') { $item.fingerprint } else { $null }) } }
}
$newManifest = [ordered]@{ schema_version = 1; catalog_id = $catalogId; entries = @($entries.Keys | Sort-Object | ForEach-Object { $entries[$_] }) }
$newManifestJson = $newManifest | ConvertTo-Json -Depth 6
if ($manifestText -and $newManifestJson.Trim() -ceq $manifestText.Trim() -and @($plan | Where-Object { $_.action -ne 'Keep' }).Count -eq 0) {
    foreach ($item in $plan) { Write-Output "Already current: $($item.name)" }
    return
}

# One decision covers the preflighted operation. WhatIf creates no directories,
# copies, links, or manifest and never removes anything.
$summary = (@($plan | ForEach-Object { "$($_.action) $($_.name)" }) -join ', ') + '; update ownership manifest'
if (-not $PSCmdlet.ShouldProcess($destinationRoot, $summary)) { return }

if (-not [IO.Directory]::Exists($destinationRoot)) { New-Item -ItemType Directory -Path $destinationRoot -Force | Out-Null }
Assert-PlainAncestors $destinationRoot
$stage = Join-Path $destinationRoot ('.skills-install-stage-' + [Guid]::NewGuid().ToString('N'))
Assert-ScopedPath $stage
New-Item -ItemType Directory -Path $stage | Out-Null
$changed = [Collections.Generic.List[object]]::new()
$committed = $false
try {
    # Stage all new entries first: missing link privileges cannot destroy an
    # existing copy. Keep replaced entries as backups until the manifest commits.
    foreach ($item in @($plan | Where-Object { $_.action -eq 'Install' })) {
        $staged = Join-Path $stage ('new-' + $item.name)
        if ($Mode -eq 'Copy') {
            Copy-Item -LiteralPath $item.source -Destination $staged -Recurse -Force
            if ((Get-TreeHash $staged -RejectLinks) -ne $item.fingerprint) { throw "Source changed while copying: $($item.source)" }
        }
        else {
            try { New-Item -ItemType SymbolicLink -Path $staged -Target $item.source | Out-Null }
            catch { throw "Cannot create symbolic link: $($_.Exception.Message) Use -Mode Copy, or enable Windows Developer Mode / symlink privileges." }
        }
    }
    foreach ($item in $plan) {
        $current = Get-Entry $item.target
        $currentHash = if ($current) { Get-TreeHash $item.target } else { $null }
        if ($currentHash -ne $item.snapshot) { throw "Destination changed after preflight: $($item.target). Rerun the installer." }
    }
    foreach ($item in $plan) {
        if ($item.action -eq 'Keep') { Write-Output "Already current: $($item.name)" }
        else {
            $backup = Join-Path $stage ('old-' + $item.name)
            $change = [pscustomobject]@{ target = $item.target; backup = $backup; backedUp = $false; installed = $false }
            $changed.Add($change)
            if (Get-Entry $item.target) { Move-ScopedEntry $item.target $backup; $change.backedUp = $true }
            if ($item.action -eq 'Install') { Move-ScopedEntry (Join-Path $stage ('new-' + $item.name)) $item.target; $change.installed = $true }
        }
    }
    $stagedManifest = Join-Path $stage 'manifest.json'
    $newManifestJson | Set-Content -LiteralPath $stagedManifest -Encoding UTF8
    $currentManifest = Get-Entry $manifestPath
    if ($currentManifest -and ($currentManifest.PSIsContainer -or (Test-Reparse $currentManifest))) { throw "Ownership manifest changed during installation." }
    $currentManifestHash = if ($currentManifest) { Get-FileDigest $manifestPath } else { $null }
    if ($currentManifestHash -ne $manifestHash) { throw "Ownership manifest changed during installation. Rerun the installer." }
    $manifestChange = [pscustomobject]@{ target = $manifestPath; backup = (Join-Path $stage 'old-manifest.json'); backedUp = $false; installed = $false }
    $changed.Add($manifestChange)
    if ($currentManifest) { Move-ScopedEntry $manifestPath $manifestChange.backup; $manifestChange.backedUp = $true }
    Move-ScopedEntry $stagedManifest $manifestPath
    $manifestChange.installed = $true
    $committed = $true
    foreach ($item in @($plan | Where-Object { $_.action -ne 'Keep' })) { Write-Output "$($item.action): $($item.name)" }
}
catch {
    $failure = $_
    for ($index = $changed.Count - 1; $index -ge 0; $index--) {
        $change = $changed[$index]
        if ($change.installed) { Remove-ScopedTree $change.target }
        if ($change.backedUp) { Move-ScopedEntry $change.backup $change.target }
    }
    throw $failure
}
finally {
    # A failed rollback preserves its backups instead of deleting the only copy.
    $remainingBackups = @(Get-ChildItem -LiteralPath $stage -Force | Where-Object { $_.Name.StartsWith('old-') })
    if ($committed -or $remainingBackups.Count -eq 0) { Remove-ScopedTree $stage }
    else { Write-Warning "Installation backups preserved for recovery: $stage" }
}
