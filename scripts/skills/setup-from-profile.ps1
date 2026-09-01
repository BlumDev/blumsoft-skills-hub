param(
  [string]$Profile = 'freelancer-fullstack',
  [switch]$Apply,
  [switch]$SyncAntigravityWorkflows
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# vendor-import lädt fehlende Vendor-Skills nach und schreibt vendor-lock.json sowie
# UPSTREAM.md. Das verändert das Repo und gehört damit nicht in den Lauf ohne -Apply, den
# dieses Skript ansonsten als reine Vorschau behandelt.
if ($Apply) {
  & (Join-Path $scriptDir 'vendor-import.ps1')
} else {
  Write-Host "[DRY RUN] vendor-import.ps1 übersprungen: schreibt vendor-lock.json und lädt fehlende Vendor-Skills. Mit -Apply ausführen."
}

& (Join-Path $scriptDir 'validate.ps1')

if ($Apply) {
  & (Join-Path $scriptDir 'sync.ps1') -Profile $Profile -SyncAntigravityWorkflows:$SyncAntigravityWorkflows
} else {
  & (Join-Path $scriptDir 'sync.ps1') -Profile $Profile -DryRun -SyncAntigravityWorkflows:$SyncAntigravityWorkflows
}
