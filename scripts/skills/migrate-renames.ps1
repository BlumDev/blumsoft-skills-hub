[CmdletBinding(SupportsShouldProcess)]
param(
  [string[]]$Targets = @('claude','codex','cursor','antigravity','vscode-copilot','vscode-chatgpt'),
  [string]$WorkspaceRoot = '',
  [switch]$DryRun
)

# Einmalige Migration installierter Skills auf das bs-Präfix (Entscheidung 2026-10-03 in
# docs/decisions.md). sync.ps1 legt nur an und ersetzt, es räumt nie ab: ohne diesen Lauf
# liegen alter und neuer Name nebeneinander im Zielordner und triggern doppelt.
#
# Je Target und alter Name:
#   1. Der alte Ordner wandert vollständig in ein Backup unter ~/.skills-hub-backup.
#   2. Umbenannte Skills werden unter dem neuen Namen aus dem Repo installiert, auch die
#      inaktiven (bs-media-image, bs-text-audio, ...), die kein Profil mitsynct.
#   3. Dateien, die nur im alten Ordner lagen (Laufzeitdaten wie out/ von bs-media-image),
#      werden in den neuen Ordner übernommen. Lokal geänderte Dateien, die es auch im Repo
#      gibt (etwa reference/ledger.jsonl), bleiben in der Repo-Fassung, die alte liegt im Backup.
# Ein Ordner wird nur angefasst, wenn sein SKILL.md den alten Namen trägt; ein fremder
# Skill, der zufällig 'web' oder 'security' heißt, bleibt liegen.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "lib.ps1")
if ($DryRun) { $WhatIfPreference = $true }

$renames = [ordered]@{
  'engineering'               = 'bs-dev-workflow'
  'bootstrap'                 = 'bs-dev-kickoff'
  'smart-commits'             = 'bs-dev-commits'
  'code-audit'                = 'bs-dev-audit'
  'repo-modernization-review' = 'bs-dev-repo-review'
  'security'                  = 'bs-dev-security'
  'web'                       = 'bs-web-build'
  'website-audit'             = 'bs-web-audit'
  'ai-systems'                = 'bs-ai-build'
  'ai-hardening'              = 'bs-ai-harden'
  'platform'                  = 'bs-ops-infra'
  'blumsoft-deploy'           = 'bs-ops-deploy-blumsoft'
  'human-voice'               = 'bs-text-natural'
  'voice'                     = 'bs-text-audio'
  'gen-asset'                 = 'bs-media-image'
  'business'                  = 'bs-business-growth'
}
# Legacy-Skills, deren Inhalt längst in den Kern-Skills steckt: nur sichern und entfernen.
$removed = @('docu', 'code-review', 'webdev', 'ai-seo-auditor', 'backend', 'project-bootstrap')

function Get-SkillMdName {
  param([Parameter(Mandatory=$true)][string]$SkillDir)
  $md = Join-Path $SkillDir 'SKILL.md'
  if (-not (Test-Path -LiteralPath $md)) { return $null }
  $lines = [System.IO.File]::ReadAllLines($md)
  if ($lines.Count -eq 0 -or $lines[0].Trim().TrimStart([char]0xFEFF) -ne '---') { return $null }
  for ($i = 1; $i -lt $lines.Count; $i++) {
    if ($lines[$i].Trim() -eq '---') { break }
    if ($lines[$i] -match '^name:\s*(.+)$') { return (Normalize-YamlValue -Value $matches[1]) }
  }
  $null
}

$root = Get-SkillsRepoRoot
$registry = Get-RegistryMap -Root $root
foreach ($new in $renames.Values) {
  if (-not $registry.ContainsKey($new)) { throw "Neuer Name fehlt in der Registry: $new" }
}

$resolvedWorkspaceRoot = if ([string]::IsNullOrWhiteSpace($WorkspaceRoot)) { $root } else { $WorkspaceRoot }
$targetMap = Get-SyncTargetMap -WorkspaceRoot $resolvedWorkspaceRoot
$backupRoot = Join-Path $HOME (".skills-hub-backup/rename-{0}" -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
$oldNames = @($renames.Keys) + $removed
$seenDirs = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
$moved = 0

foreach ($target in $Targets) {
  if (-not $targetMap.Contains($target)) { throw "Unknown target: $target" }
  $targetDir = $targetMap[$target]
  # codex und vscode-chatgpt zeigen auf denselben Ordner, der zweite Durchlauf fände nichts mehr.
  if (-not $seenDirs.Add([System.IO.Path]::GetFullPath($targetDir).TrimEnd([System.IO.Path]::DirectorySeparatorChar))) { continue }
  if (-not (Test-Path -LiteralPath $targetDir)) { continue }
  Write-Host "`nTarget: $target -> $targetDir"

  foreach ($old in $oldNames) {
    $oldPath = Resolve-SkillTargetPath -BaseDir $targetDir -SkillId $old
    if (-not (Test-Path -LiteralPath $oldPath -PathType Container)) { continue }
    $foundName = Get-SkillMdName -SkillDir $oldPath
    if ($foundName -ne $old) {
      Write-Host "  [SKIP] $old (SKILL.md heißt '$foundName', kein Skill aus diesem Hub)" -ForegroundColor DarkYellow
      continue
    }

    $new = if ($renames.Contains($old)) { $renames[$old] } else { $null }
    $action = if ($new) { "nach $new migrieren" } else { 'entfernen (Legacy)' }
    if (-not $PSCmdlet.ShouldProcess($oldPath, $action)) { continue }

    # Kopieren und dann löschen statt verschieben: das Backup liegt unter $HOME, das Ziel von
    # vscode-copilot kann auf einem anderen Laufwerk liegen, und Move-Item kann Ordner nicht
    # über Laufwerksgrenzen bewegen.
    $backupPath = [System.IO.Path]::GetFullPath((Join-Path (Join-Path $backupRoot $target) $old))
    New-Item -ItemType Directory -Path (Split-Path -Parent $backupPath) -Force | Out-Null
    Copy-Item -LiteralPath $oldPath -Destination $backupPath -Recurse -Force
    Remove-Item -LiteralPath $oldPath -Recurse -Force
    $moved++

    if (-not $new) {
      Write-Host "  [OK] $old entfernt"
      continue
    }

    $newPath = Resolve-SkillTargetPath -BaseDir $targetDir -SkillId $new
    if (-not (Test-Path -LiteralPath $newPath)) {
      Copy-Item -LiteralPath (Join-Path $root $registry[$new].path) -Destination $newPath -Recurse -Force
      Convert-FileToUtf8NoBom -Path (Join-Path $newPath 'SKILL.md') | Out-Null
    }

    $carried = 0
    foreach ($file in Get-ChildItem -LiteralPath $backupPath -Recurse -File -Force) {
      $relative = $file.FullName.Substring($backupPath.Length).TrimStart('\', '/')
      $destination = Join-Path $newPath $relative
      if (Test-Path -LiteralPath $destination) { continue }
      New-Item -ItemType Directory -Path (Split-Path -Parent $destination) -Force | Out-Null
      Copy-Item -LiteralPath $file.FullName -Destination $destination
      $carried++
    }
    $suffix = if ($carried -gt 0) { ", $carried Datei(en) nur im alten Ordner übernommen" } else { '' }
    Write-Host "  [OK] $old -> $new$suffix"
  }
}

if ($moved -gt 0) {
  Write-Host "`nAlte Ordner gesichert unter: $backupRoot"
  Write-Host "Danach wie gewohnt synchronisieren: ./scripts/skills/sync.ps1 -Profile freelancer-fullstack"
} elseif (-not $WhatIfPreference) {
  Write-Host "`nNichts zu migrieren."
}
