param(
  [string]$Profile = 'fullstack-founder',
  [switch]$Apply,
  [switch]$SyncAntigravityWorkflows
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
& (Join-Path $scriptDir 'vendor-import.ps1')
& (Join-Path $scriptDir 'validate.ps1')

if ($Apply) {
  & (Join-Path $scriptDir 'sync.ps1') -Profile $Profile -SyncAntigravityWorkflows:$SyncAntigravityWorkflows
} else {
  & (Join-Path $scriptDir 'sync.ps1') -Profile $Profile -DryRun -SyncAntigravityWorkflows:$SyncAntigravityWorkflows
}
