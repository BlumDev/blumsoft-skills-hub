param(
  [Parameter(Mandatory = $true)][string]$ProjectRoot,
  [string]$Profile = 'project-starter',
  [string[]]$BundleId,
  [switch]$IncludeExtended,
  [switch]$SyncAntigravityWorkflows,
  [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$skillsScripts = Join-Path $repoRoot 'scripts/skills'

$targetRoot = (Resolve-Path $ProjectRoot).Path
$templateRoot = Join-Path $repoRoot 'templates/project'

function Copy-IfMissing {
  param([Parameter(Mandatory = $true)][string]$SrcRel, [Parameter(Mandatory = $true)][string]$DstRel)
  $src = Join-Path $templateRoot $SrcRel
  $dst = Join-Path $targetRoot $DstRel
  if (-not (Test-Path $src)) { throw "Template not found: $src" }
  if (Test-Path $dst) { return }
  New-Item -ItemType Directory -Path (Split-Path -Parent $dst) -Force | Out-Null
  Copy-Item -Path $src -Destination $dst -Force
}

# Minimal bootstrap artifacts (do not overwrite existing project files).
Copy-IfMissing -SrcRel 'PROJECT_CONTEXT.md' -DstRel 'PROJECT_CONTEXT.md'
Copy-IfMissing -SrcRel 'DECISIONS.md' -DstRel 'DECISIONS.md'
Copy-IfMissing -SrcRel 'HOW_TO_USE_BUNDLES.md' -DstRel 'HOW_TO_USE_BUNDLES.md'
Copy-IfMissing -SrcRel 'FEATURES/README.md' -DstRel 'FEATURES/README.md'
Copy-IfMissing -SrcRel 'FEATURES/feature-template.md' -DstRel 'FEATURES/feature-template.md'
Copy-IfMissing -SrcRel '.github/copilot-instructions.md' -DstRel '.github/copilot-instructions.md'

# Project-local skills for Copilot/VS Code live under the target repo in `./.github/skills`.
$syncArgs = @(
  '-WorkspaceRoot', $targetRoot,
  '-Targets', 'vscode-copilot',
  '-IncludeExtended:' + [string]([bool]$IncludeExtended),
  '-DryRun:' + [string]([bool]$DryRun)
)

if ($BundleId -and $BundleId.Count -gt 0) {
  $syncArgs += @('-BundleId', ($BundleId -join ','))
} else {
  $syncArgs += @('-Profile', $Profile)
}

if ($SyncAntigravityWorkflows) {
  $syncArgs += @('-SyncAntigravityWorkflows')
}

& (Join-Path $skillsScripts 'sync.ps1') @syncArgs

Write-Host "`nBootstrap completed for: $targetRoot"

