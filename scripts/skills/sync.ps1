[CmdletBinding(SupportsShouldProcess)]
param(
  [string]$Profile = 'freelancer-fullstack',
  [string[]]$BundleId,
  [switch]$IncludeExtended,
  [string[]]$Targets = @('claude','codex','cursor','antigravity','vscode-copilot','vscode-chatgpt'),
  [string]$WorkspaceRoot = '',
  [switch]$SyncAntigravityWorkflows,
  [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "lib.ps1")
if ($DryRun) { $WhatIfPreference = $true }

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
  if (-not $PSBoundParameters.ContainsKey('Targets')) { $Targets = @($p.default_targets) }
  if (-not $IncludeExtended) { $IncludeExtended = [bool]$p.include_extended }
} else {
  throw "Profile not found and no -BundleId provided: $profilePath"
}

$skills = Resolve-BundleSkills -BundleIds $bundleIds -Bundles $bundles -IncludeExtended:$IncludeExtended

$targetMap = [ordered]@{
  'claude'         = Join-Path $HOME '.claude/skills'
  'codex'          = Join-Path $HOME '.codex/skills'
  'cursor'         = Join-Path $HOME '.cursor/skills'
  'antigravity'    = Join-Path $HOME '.gemini/antigravity/skills'
  'vscode-copilot' = Join-Path $resolvedWorkspaceRoot '.github/skills'
  'vscode-chatgpt' = Join-Path $HOME '.codex/skills'
}

Write-Host "Bundles: $($bundleIds -join ', ')"
Write-Host "Include extended: $([bool]$IncludeExtended)"
Write-Host "Skill count: $($skills.Count)"

# 'codex' und 'vscode-chatgpt' sind Aliase auf denselben Ordner (~/.codex/skills). Die
# Profile listen beide in default_targets. Ohne Dedup läuft jeder Skill zweimal durch
# Kopieren und Ersetzen, also doppelte Arbeit plus ein zweites Austauschfenster ohne Nutzen.
$syncedTargetDirs = [System.Collections.Generic.Dictionary[string,string]]::new([System.StringComparer]::OrdinalIgnoreCase)

foreach ($target in $Targets) {
  if (-not $targetMap.Contains($target)) { throw "Unknown target: $target" }
  $targetDir = $targetMap[$target]
  $targetKey = [System.IO.Path]::GetFullPath($targetDir).TrimEnd([System.IO.Path]::DirectorySeparatorChar)
  if ($syncedTargetDirs.ContainsKey($targetKey)) {
    Write-Host "`nTarget: $target -> $targetDir (übersprungen: gleicher Ordner wie Target '$($syncedTargetDirs[$targetKey])')"
    continue
  }
  $syncedTargetDirs[$targetKey] = $target
  Write-Host "`nTarget: $target -> $targetDir"

  foreach ($skill in $skills) {
    if (-not $registry.ContainsKey($skill)) { throw "Skill not found in registry: $skill" }
    $srcPath = Join-Path $root $registry[$skill].path
    if (-not (Test-Path -LiteralPath $srcPath)) { throw "Source path not found for skill '$skill': $srcPath" }
    $dstPath = Resolve-SkillTargetPath -BaseDir $targetDir -SkillId $skill
    if (-not $PSCmdlet.ShouldProcess($dstPath, "Skill '$skill' aus '$srcPath' synchronisieren")) { continue }

    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
    # Staging und Backup hängen an $dstPath statt an $targetDir: [System.IO.Directory]::Move löst
    # relative Pfade gegen das Prozess-Arbeitsverzeichnis auf, das von Get-Location abweichen
    # kann. $dstPath kommt bereits absolut aus Resolve-SkillTargetPath.
    $dstParent = [System.IO.Path]::GetDirectoryName($dstPath)
    $stagingPath = Join-Path $dstParent (".{0}.sync-{1}" -f $skill, [guid]::NewGuid().ToString('N'))
    $backupPath = $null
    try {
      Copy-Item -LiteralPath $srcPath -Destination $stagingPath -Recurse -Force
      $stagedSkillMd = Join-Path $stagingPath 'SKILL.md'
      if (Test-Path -LiteralPath $stagedSkillMd) {
        $changedEncoding = Convert-FileToUtf8NoBom -Path $stagedSkillMd
        if ($changedEncoding) { Write-Host "  [FIX] normalized SKILL.md encoding (UTF-8 no BOM)" -ForegroundColor DarkYellow }
      }

      # Austausch über zwei Umbenennungen statt Löschen-dann-Verschieben. Zwischen Remove-Item und
      # Move-Item lag ein Fenster, in dem ein Abbruch den Skill komplett entfernt hinterließ.
      # Directory::Move ist auf demselben Volume ein Rename und scheitert folgenlos, während
      # Move-Item Verzeichnisse rekursiv verschiebt (gemessen an einer gesperrten Datei: Quelle und
      # Ziel danach beide halb gefüllt).
      if (Test-Path -LiteralPath $dstPath) {
        $backupPath = Join-Path $dstParent (".{0}.old-{1}" -f $skill, [guid]::NewGuid().ToString('N'))
        [System.IO.Directory]::Move($dstPath, $backupPath)
      }
      # Test-Haken für genau dieses Abbruchfenster (siehe tests/skills/sync-targets.Tests.ps1).
      # Zwischen den beiden Umbenennungen läuft kein Kommando, das sich von außen ersetzen ließe,
      # der Zustand "Ziel weg, Backup da" ist ohne den Haken nicht deterministisch herstellbar.
      if ($env:SKILLSHUB_SYNC_FAULT -eq 'between-moves') { throw "SKILLSHUB_SYNC_FAULT: injizierter Fehler zwischen den Umbenennungen" }
      [System.IO.Directory]::Move($stagingPath, $dstPath)
    } finally {
      # Reihenfolge zählt. Das Backup ist Restore-Quelle, solange der neue Stand nicht am Ziel
      # liegt, und erst danach Müll. Ein Abbruch zwischen den beiden Umbenennungen (Strg+C wirft
      # PipelineStoppedException, dann läuft finally ohne catch) hinterlässt den Skill allein im
      # Backup: wird hier bedingungslos gelöscht, sind Ziel und beide Fassungen weg.
      $targetPresent = Test-Path -LiteralPath $dstPath
      if ($backupPath -and -not $targetPresent -and (Test-Path -LiteralPath $backupPath)) {
        try {
          [System.IO.Directory]::Move($backupPath, $dstPath)
          $backupPath = $null
          $targetPresent = $true
          Write-Host "  [WARN] Austausch abgebrochen, alte Version wiederhergestellt: $skill" -ForegroundColor DarkYellow
        } catch {
          Write-Host "  [ERR] Austausch abgebrochen, Restore fehlgeschlagen, alte Version liegt unter: $backupPath" -ForegroundColor Red
        }
      }
      if (Test-Path -LiteralPath $stagingPath) { Remove-Item -LiteralPath $stagingPath -Recurse -Force }
      if ($backupPath -and $targetPresent -and (Test-Path -LiteralPath $backupPath)) {
        # Der Austausch ist durch, das Entsorgen der alten Version ist nur noch Aufräumarbeit und
        # darf einen bereits erfolgreichen Sync nicht nachträglich scheitern lassen.
        Remove-Item -LiteralPath $backupPath -Recurse -Force -ErrorAction SilentlyContinue
        if (Test-Path -LiteralPath $backupPath) { Write-Host "  [WARN] alte Version bleibt liegen: $backupPath" -ForegroundColor DarkYellow }
      }
    }
    Write-Host "  [OK] $skill"
  }
}

if ($SyncAntigravityWorkflows) {
  $workflowSrcDir = Join-Path $root 'adapters/antigravity/global_workflows'
  $workflowDstDir = Join-Path $HOME '.gemini/antigravity/global_workflows'
  if (-not (Test-Path $workflowSrcDir)) { throw "Workflow source dir not found: $workflowSrcDir" }

  $workflowFiles = Get-ChildItem -Path $workflowSrcDir -Filter '*.md' -File
  Write-Host "`nAntigravity workflows -> $workflowDstDir"

  if ($PSCmdlet.ShouldProcess($workflowDstDir, 'Antigravity-Workflows synchronisieren')) {
    New-Item -ItemType Directory -Path $workflowDstDir -Force | Out-Null
    foreach ($wf in $workflowFiles) {
      Copy-Item -Path $wf.FullName -Destination (Join-Path $workflowDstDir $wf.Name) -Force
      Write-Host "  [OK] $($wf.Name)"
    }
  }
}

Write-Host "`nSync completed."
