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

foreach ($bundleId in ($bundles.Keys | Sort-Object)) {
  $bundle = $bundles[$bundleId]
  foreach ($dep in $bundle.compose_with) { if (-not $bundles.ContainsKey($dep)) { $errors.Add("Bundle '$bundleId' references missing compose_with bundle '$dep'") | Out-Null } }
  foreach ($skill in ($bundle.core_skills + $bundle.extended_skills)) {
    if (-not $registryMap.ContainsKey($skill)) { $errors.Add("Bundle '$bundleId' references skill not in registry: $skill") | Out-Null; continue }
    $entry = $registryMap[$skill]
    $skillPath = Join-Path $root $entry.path
    if (-not (Test-Path $skillPath)) { $errors.Add("Skill path missing for '$skill': $($entry.path)") | Out-Null; continue }
    if (-not (Test-Path (Join-Path $skillPath 'SKILL.md'))) { $errors.Add("SKILL.md missing for '$skill' at $($entry.path)") | Out-Null }
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
