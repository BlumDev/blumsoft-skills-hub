param(
  [string]$Profile = 'freelancer-fullstack',
  [switch]$OnlyArchiveCandidates,
  [switch]$AsJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "lib.ps1")

$root = Get-SkillsRepoRoot
$archiveEntries = Get-ArchivePlanEntries -Root $root
$bundles = Get-AllBundles -Root $root

$profileSkills = @()
$profilePath = Join-Path $root "profiles/$Profile.json"
if (Test-Path $profilePath) {
  $profileConfig = Get-Content -Path $profilePath -Raw | ConvertFrom-Json
  $profileSkills = Resolve-BundleSkills -BundleIds @($profileConfig.bundle_ids) -Bundles $bundles -IncludeExtended:$false
}

$rows = foreach ($entry in $archiveEntries) {
  [PSCustomObject]@{
    name = $entry.name
    status = $entry.status
    target = $entry.target
    in_profile = ($profileSkills -contains $entry.name)
  }
}

if ($OnlyArchiveCandidates) {
  $rows = @($rows | Where-Object { $_.status -eq 'archive-reference' })
}

if ($AsJson) {
  [PSCustomObject]@{
    profile = $Profile
    total = $rows.Count
    by_status = @($rows | Group-Object status | Sort-Object Name | ForEach-Object {
      [PSCustomObject]@{ status = $_.Name; count = $_.Count }
    })
    skills = $rows
  } | ConvertTo-Json -Depth 5
  exit 0
}

Write-Host "Archive report for profile: $Profile"
Write-Host "Total tracked skills: $($rows.Count)"
foreach ($group in ($rows | Group-Object status | Sort-Object Name)) {
  Write-Host ("- {0}: {1}" -f $group.Name, $group.Count)
}
if ($profileSkills.Count -gt 0) {
  Write-Host "Core-only profile skills: $($profileSkills.Count)"
}

$archiveCandidates = @($rows | Where-Object { $_.status -eq 'archive-reference' } | Sort-Object name)
if ($archiveCandidates.Count -gt 0) {
  Write-Host "`nArchive candidates:"
  $archiveCandidates | Format-Table name, target, in_profile -AutoSize
}
