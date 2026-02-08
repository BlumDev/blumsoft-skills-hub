param(
  [Parameter(Mandatory=$true)][string]$BundleId,
  [switch]$IncludeExtended,
  [switch]$AsJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "lib.ps1")

$root = Get-SkillsRepoRoot
$bundles = Get-AllBundles -Root $root
$skills = Resolve-BundleSkills -BundleIds @($BundleId) -Bundles $bundles -IncludeExtended:$IncludeExtended

if ($AsJson) {
  [ordered]@{bundle_id=$BundleId; include_extended=[bool]$IncludeExtended; skill_count=$skills.Length; skills=$skills} | ConvertTo-Json -Depth 4
} else {
  Write-Host "Bundle: $BundleId"
  Write-Host "Include extended: $([bool]$IncludeExtended)"
  $i=1
  foreach ($s in $skills) { Write-Host ("{0}. {1}" -f $i,$s); $i++ }
}
