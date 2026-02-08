Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-SkillsRepoRoot {
  param([string]$StartPath = $PSScriptRoot)
  (Resolve-Path (Join-Path $StartPath "..\..")).Path
}

function Normalize-YamlValue {
  param([string]$Value)
  $v = $Value.Trim()
  if (($v.StartsWith('"') -and $v.EndsWith('"')) -or ($v.StartsWith("'") -and $v.EndsWith("'"))) {
    return $v.Substring(1, $v.Length - 2)
  }
  $v
}

function Get-BundleFromFile {
  param([Parameter(Mandatory=$true)][string]$Path)

  $bundle = [ordered]@{
    id=""; name=""; goal="";
    core_skills=@(); extended_skills=@(); compose_with=@();
    starter_prompt=""; file=$Path
  }

  $listKeys = @("core_skills","extended_skills","compose_with")
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
      $bundle[$activeList] += (Normalize-YamlValue -Value $matches[1])
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
      $current = [ordered]@{name=(Normalize-YamlValue -Value $matches[1]); source=""; path=""; upstream_repo=""}
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

function Get-RepoHeadCommit {
  param([Parameter(Mandatory=$true)][string]$Repo)
  $repoInfo = Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo"
  $branch = $repoInfo.default_branch
  $commit = Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/commits/$branch"
  $commit.sha
}
