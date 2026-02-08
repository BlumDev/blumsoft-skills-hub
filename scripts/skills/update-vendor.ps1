param([switch]$RefreshLock)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "lib.ps1")

$root = Get-SkillsRepoRoot
$lockPath = Join-Path $root 'vendor-lock.json'
if (-not (Test-Path $lockPath)) { throw "vendor-lock.json not found at $lockPath" }

$lock = Get-Content -Path $lockPath -Raw | ConvertFrom-Json
$repos = @($lock.repos.PSObject.Properties | ForEach-Object { $_.Name })
$changes = New-Object System.Collections.Generic.List[hashtable]

foreach ($repo in $repos) {
  $current = Get-RepoHeadCommit -Repo $repo
  $repoProp = $lock.repos.PSObject.Properties[$repo]
  $locked = $repoProp.Value.commit
  $isOutdated = $locked -ne $current
  $changes.Add([ordered]@{repo=$repo; locked_commit=$locked; latest_commit=$current; outdated=$isOutdated}) | Out-Null
  if ($RefreshLock) { $repoProp.Value.commit = $current }
}

if ($RefreshLock) {
  $lock.generated_at = (Get-Date).ToUniversalTime().ToString('o')
  $lock | ConvertTo-Json -Depth 8 | Set-Content -Path $lockPath -Encoding UTF8
  Write-Host 'vendor-lock.json refreshed.'
}

Write-Host 'Vendor status:'
$i=1
foreach ($row in $changes) {
  $marker = if ($row.outdated) { 'OUTDATED' } else { 'OK' }
  Write-Host ("{0}. [{1}] {2}`n    locked: {3}`n    latest: {4}" -f $i,$marker,$row.repo,$row.locked_commit,$row.latest_commit)
  $i++
}
