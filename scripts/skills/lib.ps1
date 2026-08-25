Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-SkillsRepoRoot {
  param([string]$StartPath = $PSScriptRoot)
  (Resolve-Path (Join-Path $StartPath "..\..")).Path
}

# Skill and bundle ids become path segments during sync, so they are restricted to
# lowercase letters, digits and hyphens. That excludes path separators, '..', drive
# letters, alternate data streams and wildcards structurally, instead of blacklisting
# them one by one.
# -cmatch, not -match: PowerShell matches case-insensitively by default, so [a-z] alone
# would accept 'EVIL'. \z, not $: in .NET '$' also matches before a trailing newline.
function Test-SkillId {
  param([Parameter(Mandatory=$true)][AllowEmptyString()][AllowNull()][string]$Id)
  if ([string]::IsNullOrEmpty($Id)) { return $false }
  $Id -cmatch '^[a-z0-9][a-z0-9-]*\z'
}

function Assert-SkillId {
  param(
    [Parameter(Mandatory=$true)][AllowEmptyString()][AllowNull()][string]$Id,
    [string]$Context = "id"
  )
  if (-not (Test-SkillId -Id $Id)) {
    throw "Invalid $Context '$Id': only lowercase letters, digits and hyphens are allowed (no path separators, no '..', no drive letters, no wildcards)."
  }
  $Id
}

# Resolves <BaseDir>/<SkillId> and proves the result really is below BaseDir before a
# caller deletes or overwrites it. Uses GetFullPath rather than Resolve-Path because on a
# first sync the target legitimately does not exist yet.
function Resolve-SkillTargetPath {
  param(
    [Parameter(Mandatory=$true)][string]$BaseDir,
    [Parameter(Mandatory=$true)][AllowEmptyString()][AllowNull()][string]$SkillId
  )

  Assert-SkillId -Id $SkillId -Context "skill id" | Out-Null

  $sep = [System.IO.Path]::DirectorySeparatorChar
  $baseFull = [System.IO.Path]::GetFullPath($BaseDir)
  $basePrefix = $baseFull.TrimEnd($sep) + $sep
  $candidate = [System.IO.Path]::GetFullPath((Join-Path $baseFull $SkillId))

  # Compare against the separator-terminated base: a plain prefix check would also accept
  # a sibling directory like '<base>-evil'.
  if (-not $candidate.StartsWith($basePrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Refusing to touch a path outside the skills target directory: '$candidate' is not below '$baseFull'."
  }

  $candidate
}

function Normalize-YamlValue {
  param([string]$Value)
  $v = $Value.Trim()
  if (($v.StartsWith('"') -and $v.EndsWith('"')) -or ($v.StartsWith("'") -and $v.EndsWith("'"))) {
    return $v.Substring(1, $v.Length - 2)
  }
  $v
}

function Test-HasUtf8Bom {
  param([byte[]]$Bytes)
  if ($null -eq $Bytes -or $Bytes.Length -lt 3) { return $false }
  ($Bytes[0] -eq 0xEF -and $Bytes[1] -eq 0xBB -and $Bytes[2] -eq 0xBF)
}

function Test-FileHasUtf8Bom {
  param([Parameter(Mandatory=$true)][string]$Path)
  $bytes = [System.IO.File]::ReadAllBytes($Path)
  Test-HasUtf8Bom -Bytes $bytes
}

function Convert-FileToUtf8NoBom {
  param([Parameter(Mandatory=$true)][string]$Path)
  $bytes = [System.IO.File]::ReadAllBytes($Path)
  if (-not (Test-HasUtf8Bom -Bytes $bytes)) { return $false }

  # Keep file content unchanged while removing only the UTF-8 BOM.
  $text = [System.Text.Encoding]::UTF8.GetString($bytes, 3, $bytes.Length - 3)
  $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllText($Path, $text, $utf8NoBom)
  $true
}

function Write-FileUtf8NoBom {
  param([Parameter(Mandatory=$true)][string]$Path,[Parameter(Mandatory=$true)][string]$Content)
  $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllText($Path, $Content, $utf8NoBom)
}

function Get-BundleFromFile {
  param([Parameter(Mandatory=$true)][string]$Path)

  $bundle = [ordered]@{
    id=""; name=""; goal="";
    recommended_start_skill=""; fallback_skills=@();
    core_skills=@(); extended_skills=@(); compose_with=@();
    starter_prompt=""; file=$Path
  }

  $listKeys = @("core_skills","extended_skills","compose_with","fallback_skills")
  $activeList = ""
  foreach ($line in Get-Content -Path $Path) {
    $trim = $line.Trim()
    if ([string]::IsNullOrWhiteSpace($trim) -or $trim.StartsWith("#")) { continue }

    if ($trim -match '^([a-z_]+):\s*(.*)$') {
      $key = $matches[1]
      $rawValue = $matches[2]
      if ($listKeys -contains $key) {
        $activeList = $key
      } else {
        $activeList = ""
        $bundle[$key] = Normalize-YamlValue -Value $rawValue
      }
      continue
    }

    if ($trim -match '^- (.+)$' -and $activeList) {
      $item = Normalize-YamlValue -Value $matches[1]
      Assert-SkillId -Id $item -Context "$activeList entry in $Path" | Out-Null
      $bundle[$activeList] += $item
      continue
    }
  }

  $bundle
}

function Get-AllBundles {
  param([string]$Root = (Get-SkillsRepoRoot))
  $bundleDir = Join-Path $Root "bundles"
  $map = @{}
  foreach ($file in Get-ChildItem -Path $bundleDir -Filter "*.yaml" -File) {
    if ($file.Name -eq "index.yaml" -or $file.Name -eq "schema.yaml") { continue }
    $bundle = Get-BundleFromFile -Path $file.FullName
    if ([string]::IsNullOrWhiteSpace($bundle.id)) { throw "Bundle file has no id: $($file.FullName)" }
    Assert-SkillId -Id $bundle.id -Context "bundle id in $($file.FullName)" | Out-Null
    if ($map.ContainsKey($bundle.id)) { throw "Duplicate bundle id: $($bundle.id)" }
    $map[$bundle.id] = $bundle
  }
  $map
}

function Resolve-BundleSkills {
  param(
    [Parameter(Mandatory=$true)][string[]]$BundleIds,
    [Parameter(Mandatory=$true)][hashtable]$Bundles,
    [switch]$IncludeExtended
  )

  $seenBundles = @{}
  $seenSkills = @{}
  $orderedSkills = New-Object System.Collections.Generic.List[string]

  function Add-BundleInternal {
    param([string]$BundleId)
    if ($seenBundles.ContainsKey($BundleId)) { return }
    if (-not $Bundles.ContainsKey($BundleId)) { throw "Unknown bundle id: $BundleId" }
    $seenBundles[$BundleId] = $true
    $bundle = $Bundles[$BundleId]

    foreach ($dep in $bundle.compose_with) { Add-BundleInternal -BundleId $dep }

    foreach ($skill in $bundle.core_skills) {
      if (-not $seenSkills.ContainsKey($skill)) { $seenSkills[$skill] = $true; $orderedSkills.Add($skill) | Out-Null }
    }

    if ($IncludeExtended) {
      foreach ($skill in $bundle.extended_skills) {
        if (-not $seenSkills.ContainsKey($skill)) { $seenSkills[$skill] = $true; $orderedSkills.Add($skill) | Out-Null }
      }
    }
  }

  foreach ($id in $BundleIds) { Add-BundleInternal -BundleId $id }
  ,$orderedSkills.ToArray()
}

function Get-RegistryEntries {
  param([string]$Root = (Get-SkillsRepoRoot))
  $path = Join-Path $Root "skills/registry.yaml"
  $entries = New-Object System.Collections.Generic.List[hashtable]
  $current = $null

  foreach ($line in Get-Content -Path $path) {
    $trim = $line.Trim()
    if ([string]::IsNullOrWhiteSpace($trim) -or $trim.StartsWith("#") -or $trim -eq "skills:") { continue }

    if ($trim -match '^- name:\s*(.+)$') {
      if ($current) { $entries.Add($current) | Out-Null }
      $name = Normalize-YamlValue -Value $matches[1]
      Assert-SkillId -Id $name -Context "skill name in $path" | Out-Null
      $current = [ordered]@{name=$name; source=""; path=""; upstream_repo=""}
      continue
    }

    if (-not $current) { continue }
    if ($trim -match '^source:\s*(.+)$') { $current.source = Normalize-YamlValue -Value $matches[1]; continue }
    if ($trim -match '^path:\s*(.+)$') { $current.path = Normalize-YamlValue -Value $matches[1]; continue }
    if ($trim -match '^upstream_repo:\s*(.+)$') { $current.upstream_repo = Normalize-YamlValue -Value $matches[1]; continue }
  }
  if ($current) { $entries.Add($current) | Out-Null }
  ,$entries.ToArray()
}

function Get-RegistryMap {
  param([string]$Root = (Get-SkillsRepoRoot))
  $map = @{}
  foreach ($entry in (Get-RegistryEntries -Root $Root)) {
    if ($map.ContainsKey($entry.name)) { throw "Duplicate skill in registry: $($entry.name)" }
    $map[$entry.name] = $entry
  }
  $map
}

function Get-ArchivePlanEntries {
  param([string]$Root = (Get-SkillsRepoRoot))
  $path = Join-Path $Root "skills/archive-plan.yaml"
  if (-not (Test-Path $path)) { throw "Archive plan not found: $path" }

  $entries = New-Object System.Collections.Generic.List[hashtable]
  $current = $null

  foreach ($line in Get-Content -Path $path) {
    $trim = $line.Trim()
    if ([string]::IsNullOrWhiteSpace($trim) -or $trim.StartsWith("#") -or $trim -eq "skills:") { continue }
    if ($trim -match '^version:\s*(.+)$') { continue }

    if ($trim -match '^- name:\s*(.+)$') {
      if ($current) { $entries.Add($current) | Out-Null }
      $current = [ordered]@{name=(Normalize-YamlValue -Value $matches[1]); status=""; target=""}
      continue
    }

    if (-not $current) { continue }
    if ($trim -match '^status:\s*(.+)$') { $current.status = Normalize-YamlValue -Value $matches[1]; continue }
    if ($trim -match '^target:\s*(.+)$') { $current.target = Normalize-YamlValue -Value $matches[1]; continue }
  }

  if ($current) { $entries.Add($current) | Out-Null }
  ,$entries.ToArray()
}

function Get-RepoHeadCommit {
  param([Parameter(Mandatory=$true)][string]$Repo)
  $headers = @{ Accept = "application/vnd.github+json" }
  if (-not [string]::IsNullOrWhiteSpace($env:GITHUB_TOKEN)) {
    $headers.Authorization = "Bearer $($env:GITHUB_TOKEN)"
  }
  try {
    $repoInfo = Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo" -Headers $headers -TimeoutSec 30
    $branch = $repoInfo.default_branch
    $commit = Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/commits/$branch" -Headers $headers -TimeoutSec 30
    $commit.sha
  } catch {
    throw "GitHub-API-Abfrage für Repository '$Repo' fehlgeschlagen. Netzwerkzugriff, Rate-Limit und GITHUB_TOKEN prüfen."
  }
}
