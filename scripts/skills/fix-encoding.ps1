Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "lib.ps1")

$root = Get-SkillsRepoRoot
$changed = New-Object System.Collections.Generic.List[string]

$skillRoots = @(
  (Join-Path $root 'skills'),
  (Join-Path $root '.github/skills')
)

foreach ($dir in $skillRoots) {
  if (-not (Test-Path $dir)) { continue }
  foreach ($md in Get-ChildItem -Path $dir -Recurse -Filter 'SKILL.md' -File) {
    if (Convert-FileToUtf8NoBom -Path $md.FullName) {
      $changed.Add($md.FullName) | Out-Null
    }
  }
}

if ($changed.Count -eq 0) {
  Write-Host 'No SKILL.md files required BOM cleanup.'
  exit 0
}

Write-Host "Normalized UTF-8 (no BOM): $($changed.Count) file(s)."
foreach ($f in $changed) { Write-Host " - $f" }
