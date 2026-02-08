param([string]$Profile = 'fullstack-founder')

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
& (Join-Path $scriptDir 'vendor-import.ps1')
& (Join-Path $scriptDir 'validate.ps1')
& (Join-Path $scriptDir 'sync.ps1') -Profile $Profile -DryRun
