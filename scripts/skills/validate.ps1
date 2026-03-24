Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "lib.ps1")

$root = Get-SkillsRepoRoot
$errors = New-Object System.Collections.Generic.List[string]
$bundles = Get-AllBundles -Root $root

if ($bundles.Count -eq 0) { $errors.Add("No bundle files found in bundles/*.yaml") | Out-Null }

$indexPath = Join-Path $root "bundles/index.yaml"
if (Test-Path $indexPath) {
  $indexIds = @()
  foreach ($line in Get-Content -Path $indexPath) {
    $trim = $line.Trim()
    if ($trim -match '^(?:- )?id:\s*(.+)$') { $indexIds += $matches[1].Trim() }
  }
  foreach ($id in $indexIds) { if (-not $bundles.ContainsKey($id)) { $errors.Add("bundles/index.yaml references missing bundle id '$id'") | Out-Null } }
}

foreach ($bundleId in ($bundles.Keys | Sort-Object)) {
  $bundle = $bundles[$bundleId]
  if ([string]::IsNullOrWhiteSpace($bundle.name)) { $errors.Add("Bundle '$bundleId' missing name") | Out-Null }
  if ([string]::IsNullOrWhiteSpace($bundle.goal)) { $errors.Add("Bundle '$bundleId' missing goal") | Out-Null }
  if ([string]::IsNullOrWhiteSpace($bundle.recommended_start_skill)) { $errors.Add("Bundle '$bundleId' missing recommended_start_skill") | Out-Null }
  if (-not $bundle.fallback_skills -or $bundle.fallback_skills.Count -ne 2) { $errors.Add("Bundle '$bundleId' must have exactly 2 fallback_skills") | Out-Null }
  if ($bundle.core_skills.Count -eq 0) { $errors.Add("Bundle '$bundleId' has no core_skills") | Out-Null }
  if ([string]::IsNullOrWhiteSpace($bundle.starter_prompt)) {
    $errors.Add("Bundle '$bundleId' missing starter_prompt") | Out-Null
  } else {
    $p = Join-Path $root $bundle.starter_prompt
    if (-not (Test-Path $p)) { $errors.Add("Bundle '$bundleId' starter_prompt file not found: $($bundle.starter_prompt)") | Out-Null }
  }
}

$registryEntries = Get-RegistryEntries -Root $root
$registryMap = @{}
foreach ($entry in $registryEntries) {
  if ($registryMap.ContainsKey($entry.name)) { $errors.Add("Duplicate skill in registry: $($entry.name)") | Out-Null; continue }
  $registryMap[$entry.name] = $entry
}

$archiveEntries = @()
$archiveMap = @{}
$allowedArchiveStatuses = @('active-core', 'active-extended', 'archive-reference')
try {
  $archiveEntries = Get-ArchivePlanEntries -Root $root
  foreach ($entry in $archiveEntries) {
    if ($archiveMap.ContainsKey($entry.name)) { $errors.Add("Duplicate skill in archive plan: $($entry.name)") | Out-Null; continue }
    $archiveMap[$entry.name] = $entry
    if ($allowedArchiveStatuses -notcontains $entry.status) { $errors.Add("Archive plan has invalid status for '$($entry.name)': $($entry.status)") | Out-Null }
    if ([string]::IsNullOrWhiteSpace($entry.target)) { $errors.Add("Archive plan missing target for '$($entry.name)'") | Out-Null }
  }
} catch {
  $errors.Add($_.Exception.Message) | Out-Null
}

foreach ($entry in $registryEntries) {
  if (-not $archiveMap.ContainsKey($entry.name)) { $errors.Add("Registry skill missing from archive plan: $($entry.name)") | Out-Null }
}
foreach ($entry in $archiveEntries) {
  if (-not $registryMap.ContainsKey($entry.name)) { $errors.Add("Archive plan references skill not in registry: $($entry.name)") | Out-Null }
}
foreach ($entry in $archiveEntries) {
  if (-not $registryMap.ContainsKey($entry.name)) { continue }
  $registryEntry = $registryMap[$entry.name]
  $path = $registryEntry.path.Replace('\','/')
  if ($entry.status -eq 'archive-reference' -and -not $path.StartsWith('skills/archive/')) {
    $errors.Add("Archive-reference skill must live under skills/archive: $($entry.name) -> $($registryEntry.path)") | Out-Null
  }
  if ($entry.status -ne 'archive-reference' -and $path.StartsWith('skills/archive/')) {
    $errors.Add("Active skill must not live under skills/archive: $($entry.name) -> $($registryEntry.path)") | Out-Null
  }
}

# Validate canonical registry skill files (independent of bundle references).
foreach ($entry in $registryEntries) {
  if ([string]::IsNullOrWhiteSpace($entry.path)) {
    $errors.Add("Registry entry '$($entry.name)' is missing path") | Out-Null
    continue
  }
  $skillPath = Join-Path $root $entry.path
  if (-not (Test-Path $skillPath)) {
    $errors.Add("Registry path missing for '$($entry.name)': $($entry.path)") | Out-Null
    continue
  }
  $skillMd = Join-Path $skillPath 'SKILL.md'
  if (-not (Test-Path $skillMd)) {
    $errors.Add("Registry skill '$($entry.name)' has no SKILL.md at $($entry.path)") | Out-Null
    continue
  }
  if (Test-FileHasUtf8Bom -Path $skillMd) {
    $errors.Add("SKILL.md must be UTF-8 without BOM for '$($entry.name)': $($entry.path)/SKILL.md") | Out-Null
  }
}

# Keep checked-in .github skill mirror BOM-free to avoid reintroducing bad files.
$githubSkillsDir = Join-Path $root '.github/skills'
if (Test-Path $githubSkillsDir) {
  foreach ($md in Get-ChildItem -Path $githubSkillsDir -Recurse -Filter 'SKILL.md' -File) {
    if (Test-FileHasUtf8Bom -Path $md.FullName) {
      $errors.Add(".github skill mirror SKILL.md must be UTF-8 without BOM: $($md.FullName)") | Out-Null
    }
  }
}

foreach ($bundleId in ($bundles.Keys | Sort-Object)) {
  $bundle = $bundles[$bundleId]
  foreach ($dep in $bundle.compose_with) { if (-not $bundles.ContainsKey($dep)) { $errors.Add("Bundle '$bundleId' references missing compose_with bundle '$dep'") | Out-Null } }

  # Ensure start/fallback skills exist and are part of the bundle resolution (core-only).
  try {
    $resolvedCore = Resolve-BundleSkills -BundleIds @($bundleId) -Bundles $bundles
    if ($bundle.recommended_start_skill -and ($resolvedCore -notcontains $bundle.recommended_start_skill)) {
      $errors.Add("Bundle '$bundleId' recommended_start_skill is not part of core resolution: $($bundle.recommended_start_skill)") | Out-Null
    }
    foreach ($s in @($bundle.fallback_skills)) {
      if ($s -and ($resolvedCore -notcontains $s)) { $errors.Add("Bundle '$bundleId' fallback_skill is not part of core resolution: $s") | Out-Null }
    }
  } catch {
    $errors.Add("Bundle '$bundleId' failed to resolve for start/fallback validation: $($_.Exception.Message)") | Out-Null
  }

  foreach ($skill in @($bundle.recommended_start_skill) + @($bundle.fallback_skills)) {
    if ([string]::IsNullOrWhiteSpace($skill)) { continue }
    if (-not $registryMap.ContainsKey($skill)) { $errors.Add("Bundle '$bundleId' references skill not in registry (start/fallback): $skill") | Out-Null; continue }
    $entry = $registryMap[$skill]
    $skillPath = Join-Path $root $entry.path
    if (-not (Test-Path (Join-Path $skillPath 'SKILL.md'))) { $errors.Add("SKILL.md missing for '$skill' (start/fallback) at $($entry.path)") | Out-Null }
  }

  foreach ($skill in ($bundle.core_skills + $bundle.extended_skills)) {
    if (-not $registryMap.ContainsKey($skill)) { $errors.Add("Bundle '$bundleId' references skill not in registry: $skill") | Out-Null; continue }
    $entry = $registryMap[$skill]
    $skillPath = Join-Path $root $entry.path
    if (-not (Test-Path $skillPath)) { $errors.Add("Skill path missing for '$skill': $($entry.path)") | Out-Null; continue }
    if (-not (Test-Path (Join-Path $skillPath 'SKILL.md'))) { $errors.Add("SKILL.md missing for '$skill' at $($entry.path)") | Out-Null }
  }
}

$profilePaths = Get-ChildItem -Path (Join-Path $root 'profiles') -Filter '*.json' -File
foreach ($profileFile in $profilePaths) {
  $profile = Get-Content -Path $profileFile.FullName -Raw | ConvertFrom-Json
  $bundleIds = @($profile.bundle_ids)
  if ($bundleIds.Count -eq 0) { continue }
  try {
    $resolved = Resolve-BundleSkills -BundleIds $bundleIds -Bundles $bundles -IncludeExtended:$false
    foreach ($skill in $resolved) {
      if ($archiveMap.ContainsKey($skill) -and $archiveMap[$skill].status -eq 'archive-reference') {
        $errors.Add("Profile '$($profile.profile_name)' includes archive-reference skill in core resolution: $skill") | Out-Null
      }
    }
  } catch {
    $errors.Add("Profile '$($profile.profile_name)' failed to resolve: $($_.Exception.Message)") | Out-Null
  }
}

$guanyangDir = Join-Path $root 'skills/vendor/guanyang'
foreach ($entry in $registryEntries | Where-Object { $_.source -eq 'vendor-sickn33' }) {
  $dupePath = Join-Path $guanyangDir $entry.name
  if (Test-Path $dupePath) { $errors.Add("Collision policy violation for '$($entry.name)': source is vendor-sickn33 but guanyang copy exists") | Out-Null }
}

if ($errors.Count -gt 0) {
  Write-Host 'Validation failed:' -ForegroundColor Red
  $i=1
  foreach ($e in $errors) { Write-Host ("{0}. {1}" -f $i,$e) -ForegroundColor Red; $i++ }
  exit 1
}

Write-Host 'Validation passed.' -ForegroundColor Green
Write-Host "Bundles: $($bundles.Count)"
Write-Host "Registry skills: $($registryEntries.Count)"
Write-Host "Archive plan skills: $($archiveEntries.Count)"
