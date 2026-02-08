param(
  [string]$Profile = 'fullstack-founder',
  [string[]]$BundleId,
  [switch]$IncludeExtended,
  [string[]]$Targets = @('codex','cursor','antigravity','vscode-copilot','vscode-chatgpt'),
  [string]$WorkspaceRoot = '',
  [switch]$SyncAntigravityWorkflows,
  [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "lib.ps1")

$root = Get-SkillsRepoRoot
$resolvedWorkspaceRoot = if ([string]::IsNullOrWhiteSpace($WorkspaceRoot)) { $root } else { $WorkspaceRoot }
$bundles = Get-AllBundles -Root $root
$registry = Get-RegistryMap -Root $root

$bundleIds = @()
$profilePath = Join-Path $root "profiles/$Profile.json"
if ($BundleId -and $BundleId.Count -gt 0) {
  $bundleIds = $BundleId
} elseif (Test-Path $profilePath) {
  $p = Get-Content -Path $profilePath -Raw | ConvertFrom-Json
  $bundleIds = @($p.bundle_ids)
  if (-not $IncludeExtended) { $IncludeExtended = [bool]$p.include_extended }
} else {
  throw "Profile not found and no -BundleId provided: $profilePath"
}

$skills = Resolve-BundleSkills -BundleIds $bundleIds -Bundles $bundles -IncludeExtended:$IncludeExtended

$targetMap = [ordered]@{
  'codex'          = Join-Path $HOME '.codex/skills'
  'cursor'         = Join-Path $HOME '.cursor/skills'
  'antigravity'    = Join-Path $HOME '.gemini/antigravity/skills'
  'vscode-copilot' = Join-Path $resolvedWorkspaceRoot '.github/skills'
  'vscode-chatgpt' = Join-Path $HOME '.codex/skills'
}

Write-Host "Bundles: $($bundleIds -join ', ')"
Write-Host "Include extended: $([bool]$IncludeExtended)"
Write-Host "Skill count: $($skills.Count)"

foreach ($target in $Targets) {
  if (-not $targetMap.Contains($target)) { throw "Unknown target: $target" }
  $targetDir = $targetMap[$target]
  Write-Host "`nTarget: $target -> $targetDir"

  if ($DryRun) {
    foreach ($skill in $skills) {
      if (-not $registry.ContainsKey($skill)) { Write-Host "  [MISS] $skill not in registry" -ForegroundColor Yellow; continue }
      Write-Host "  [DRY] $skill <= $($registry[$skill].path)"
    }
    continue
  }

  New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
  foreach ($skill in $skills) {
    if (-not $registry.ContainsKey($skill)) { throw "Skill not found in registry: $skill" }
    $srcPath = Join-Path $root $registry[$skill].path
    if (-not (Test-Path $srcPath)) { throw "Source path not found for skill '$skill': $srcPath" }
    $dstPath = Join-Path $targetDir $skill
    if (Test-Path $dstPath) { Remove-Item -Path $dstPath -Recurse -Force }
    Copy-Item -Path $srcPath -Destination $dstPath -Recurse -Force
    Write-Host "  [OK] $skill"
  }
}

if ($SyncAntigravityWorkflows) {
  $workflowSrcDir = Join-Path $root 'adapters/antigravity/global_workflows'
  $workflowDstDir = Join-Path $HOME '.gemini/antigravity/global_workflows'
  if (-not (Test-Path $workflowSrcDir)) { throw "Workflow source dir not found: $workflowSrcDir" }

  $workflowFiles = Get-ChildItem -Path $workflowSrcDir -Filter '*.md' -File
  Write-Host "`nAntigravity workflows -> $workflowDstDir"
  if ($DryRun) {
    foreach ($wf in $workflowFiles) { Write-Host "  [DRY] $($wf.Name)" }
  } else {
    New-Item -ItemType Directory -Path $workflowDstDir -Force | Out-Null
    foreach ($wf in $workflowFiles) {
      Copy-Item -Path $wf.FullName -Destination (Join-Path $workflowDstDir $wf.Name) -Force
      Write-Host "  [OK] $($wf.Name)"
    }
  }
}

Write-Host "`nSync completed."
