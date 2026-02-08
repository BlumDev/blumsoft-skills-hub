param(
  [Parameter(Mandatory=$true)][string]$BundleId,
  [switch]$IncludeExtended,
  [switch]$Summary,
  [switch]$AsJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "lib.ps1")

$root = Get-SkillsRepoRoot
$bundles = Get-AllBundles -Root $root
if (-not $bundles.ContainsKey($BundleId)) { throw "Unknown bundle id: $BundleId" }
$bundle = $bundles[$BundleId]

$skills = Resolve-BundleSkills -BundleIds @($BundleId) -Bundles $bundles -IncludeExtended:$IncludeExtended

if ($AsJson) {
  if ($Summary) {
    [ordered]@{
      bundle_id=$BundleId
      name=$bundle.name
      goal=$bundle.goal
      compose_with=@($bundle.compose_with)
      recommended_start_skill=$bundle.recommended_start_skill
      fallback_skills=@($bundle.fallback_skills)
    } | ConvertTo-Json -Depth 4
  } else {
    [ordered]@{bundle_id=$BundleId; include_extended=[bool]$IncludeExtended; skill_count=$skills.Length; skills=$skills} | ConvertTo-Json -Depth 4
  }
} else {
  if ($Summary) {
    Write-Host "Bundle: $BundleId ($($bundle.name))"
    if (-not [string]::IsNullOrWhiteSpace($bundle.goal)) { Write-Host "Goal: $($bundle.goal)" }
    if ($bundle.compose_with -and $bundle.compose_with.Count -gt 0) { Write-Host "Compose with: $($bundle.compose_with -join ', ')" }
    Write-Host "Start: $($bundle.recommended_start_skill)"
    if ($bundle.fallback_skills -and $bundle.fallback_skills.Count -gt 0) {
      Write-Host "Fallbacks:"
      foreach ($s in $bundle.fallback_skills) { Write-Host "  - $s" }
    }
  } else {
    Write-Host "Bundle: $BundleId"
    Write-Host "Include extended: $([bool]$IncludeExtended)"
    $i=1
    foreach ($s in $skills) { Write-Host ("{0}. {1}" -f $i,$s); $i++ }
  }
}
