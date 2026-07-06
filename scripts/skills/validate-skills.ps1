# Validates the content of every skill's SKILL.md (per-skill, not repo consistency).
# Repo-level consistency (bundles / registry / profiles / BOM) stays in validate.ps1.
#
# Per skill it checks:
#   - YAML frontmatter present and parseable                        (error)
#   - required fields 'name' and 'description' present, non-empty   (error)
#   - locally referenced files (references/..., markdown links) exist (error)
#   - name matches the skill folder name                            (warning)
#   - encoding health: broken UTF-8 / mojibake / ae-oe-ue instead
#     of umlauts (reported only, never auto-changed)                (warning)
#
# Exit code is 1 when any error is found. With -Strict, warnings fail too.
[CmdletBinding()]
param(
  [switch]$Strict
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "lib.ps1")

function Read-Utf8Text {
  # Decode as UTF-8 without throwing: invalid bytes become U+FFFD so we can flag them.
  param([Parameter(Mandatory = $true)][string]$Path)
  $bytes = [System.IO.File]::ReadAllBytes($Path)
  $enc = New-Object System.Text.UTF8Encoding($false, $false)
  $text = $enc.GetString($bytes)
  if ($text.Length -gt 0 -and [int][char]$text[0] -eq 0xFEFF) { $text = $text.Substring(1) }
  $text
}

function Parse-Frontmatter {
  # Minimal top-level YAML frontmatter parser (name/description only are needed).
  # Handles plain, quoted, and block scalars (>, >-, |, |-).
  param([Parameter(Mandatory = $true)][string]$Text)

  $lines = $Text -split "`r?`n"
  if ($lines.Count -eq 0 -or $lines[0].Trim() -ne '---') {
    return @{ ok = $false; error = "no YAML frontmatter (file does not start with '---')"; fields = @{}; body = $Text }
  }

  $end = -1
  for ($i = 1; $i -lt $lines.Count; $i++) {
    if ($lines[$i].Trim() -eq '---') { $end = $i; break }
  }
  if ($end -lt 0) {
    return @{ ok = $false; error = "unterminated YAML frontmatter (no closing '---')"; fields = @{}; body = $Text }
  }

  $fields = @{}
  $i = 1
  while ($i -lt $end) {
    $line = $lines[$i]
    $trim = $line.Trim()
    if ($trim -eq '' -or $trim.StartsWith('#')) { $i++; continue }

    $m = [regex]::Match($line, '^([A-Za-z0-9_-]+):\s*(.*)$')
    if (-not $m.Success) { $i++; continue }

    $key = $m.Groups[1].Value
    $val = $m.Groups[2].Value.Trim()

    if ($val -match '^[>|][+-]?$') {
      # Block scalar: fold indented follow-up lines into one string.
      $blockLines = @()
      $i++
      while ($i -lt $end) {
        $bl = $lines[$i]
        if ($bl.Trim() -eq '') { $blockLines += ''; $i++; continue }
        if ($bl -match '^\s+\S') { $blockLines += $bl.Trim(); $i++; continue }
        break
      }
      $fields[$key] = ($blockLines -join ' ').Trim()
      continue
    }

    $fields[$key] = Normalize-YamlValue -Value $val
    $i++
  }

  $bodyLines = if (($end + 1) -le ($lines.Count - 1)) { $lines[($end + 1)..($lines.Count - 1)] } else { @() }
  return @{ ok = $true; error = $null; fields = $fields; body = ($bodyLines -join "`n") }
}

function Convert-ToLocalRef {
  # Returns a normalized in-skill file reference, or $null if the candidate is
  # not a local file (external URL, cross-repo path, anchor, command snippet).
  param(
    [Parameter(Mandatory = $true)][AllowEmptyString()][string]$Raw,
    [string[]]$Subdirs = @(),
    [bool]$AllowBare = $false
  )
  $t = $Raw.Trim()
  if ($t -eq '') { return $null }
  $t = ($t -split '\s+')[0]          # drop a markdown-link title after the path
  $t = $t.Trim('<', '>')
  $t = ($t -split '#')[0]            # drop an #anchor
  if ($t -eq '') { return $null }
  if ($t -match '^[A-Za-z][A-Za-z0-9+.\-]*://') { return $null }   # http(s)://, etc.
  if ($t -match '^(mailto:|tel:)') { return $null }
  if ($t.StartsWith('/') -or $t.StartsWith('~')) { return $null }  # absolute / home
  if ($t -match '^[A-Za-z]:[\\/]') { return $null }                # drive letter
  if ($t.StartsWith('..')) { return $null }                        # escapes the skill dir
  if ($t -match '\s') { return $null }
  $t = $t -replace '^\./', ''

  if ($t.Contains('/')) {
    $first = $t.Split('/')[0]
    if ($Subdirs -notcontains $first) { return $null }             # only refs into real subdirs
    return $t
  }
  if (-not $AllowBare) { return $null }
  if ($t -notmatch '\.[A-Za-z0-9]{1,8}$') { return $null }         # bare token needs an extension
  return $t
}

function Get-LocalFileRefs {
  param(
    [Parameter(Mandatory = $true)][AllowEmptyString()][string]$Body,
    [Parameter(Mandatory = $true)][string]$SkillDir
  )
  $subdirs = @()
  foreach ($d in (Get-ChildItem -LiteralPath $SkillDir -Directory -ErrorAction SilentlyContinue)) { $subdirs += $d.Name }

  $refs = New-Object System.Collections.Generic.List[string]
  foreach ($m in [regex]::Matches($Body, '\]\(([^)]+)\)')) {          # markdown links
    $c = Convert-ToLocalRef -Raw $m.Groups[1].Value -Subdirs $subdirs -AllowBare $true
    if ($c) { [void]$refs.Add($c) }
  }
  foreach ($m in [regex]::Matches($Body, '`([^`]+)`')) {             # inline-code paths
    $c = Convert-ToLocalRef -Raw $m.Groups[1].Value -Subdirs $subdirs -AllowBare $false
    if ($c) { [void]$refs.Add($c) }
  }
  $refs.ToArray() | Select-Object -Unique
}

function Get-EncodingWarnings {
  param([Parameter(Mandatory = $true)][string]$Text)
  $w = @()

  if ($Text.Contains([char]0xFFFD)) {
    $w += "broken UTF-8 (U+FFFD replacement char present; file may be saved in a non-UTF-8 encoding)"
  }

  # Mojibake = correct UTF-8 bytes re-read as Latin-1. Built from char codes so
  # this script stays pure ASCII (PS 5.1 reads it correctly without a BOM).
  $c3 = [char]0xC3
  $mojibake = [ordered]@{
    'lower-a' = ($c3 + [char]0xA4); 'lower-o' = ($c3 + [char]0xB6); 'lower-u' = ($c3 + [char]0xBC)
    'upper-a' = ($c3 + [char]0x84); 'upper-o' = ($c3 + [char]0x96); 'upper-u' = ($c3 + [char]0x9C)
    'sz' = ($c3 + [char]0x9F)
  }
  $hits = @()
  foreach ($label in $mojibake.Keys) { if ($Text.Contains($mojibake[$label])) { $hits += $label } }
  if ($hits.Count -gt 0) { $w += "mojibake sequences present (garbled umlauts: $($hits -join ', '))" }

  # ae/oe/ue transliteration: conservative denylist of unambiguous German words.
  # Whole-word match keeps English (value, queue, argue, ...) from matching.
  $deny = @(
    'fuer', 'fuers', 'ueber', 'ueberblick', 'koennen', 'koennte', 'muessen',
    'loesung', 'loesungen', 'moeglich', 'moeglichkeit', 'waehrend', 'naechste',
    'naechsten', 'zunaechst', 'fuehrt', 'fuehren', 'gefuehrt', 'ausfuehren',
    'ausfuehrung', 'aehnlich', 'hoehe', 'hoeher', 'schoen', 'groesse', 'groesser',
    'praezise', 'qualitaet', 'funktionalitaet', 'aenderung', 'aenderungen',
    'pruefen', 'prueft', 'pruefung', 'geprueft', 'unterstuetzung', 'unterstuetzen',
    'verfuegbar', 'benoetigt', 'benoetigen', 'standardmaessig', 'gemaess',
    'erklaeren', 'erklaerung', 'waehlen', 'gewaehlt', 'ueblich', 'hinzufuegen',
    'loeschen', 'ausgefuehrt'
  )
  $found = @()
  foreach ($word in $deny) { if ([regex]::IsMatch($Text, "(?i)\b$word\b")) { $found += $word } }
  if ($found.Count -gt 0) {
    $w += "possible ae/oe/ue instead of umlauts in German words: $(($found | Select-Object -Unique) -join ', ')"
  }

  $w
}

# --- main ---------------------------------------------------------------------

$root = Get-SkillsRepoRoot
$skillsDir = Join-Path $root 'skills'
if (-not (Test-Path $skillsDir)) { Write-Host "No skills directory found at $skillsDir" -ForegroundColor Red; exit 1 }

$files = @(Get-ChildItem -Path $skillsDir -Recurse -Filter 'SKILL.md' -File | Sort-Object FullName)

$errorCount = 0
$warnCount = 0
$filesWithErrors = 0

foreach ($f in $files) {
  $rel = ($f.FullName.Substring($root.Length).TrimStart('\', '/')) -replace '\\', '/'
  $skillDir = Split-Path $f.FullName -Parent
  $folderName = Split-Path $skillDir -Leaf
  $errs = @()
  $warns = @()

  $text = Read-Utf8Text -Path $f.FullName
  $fm = Parse-Frontmatter -Text $text

  if (-not $fm.ok) {
    $errs += $fm.error
  }
  else {
    $fields = $fm.fields
    if (-not $fields.ContainsKey('name') -or [string]::IsNullOrWhiteSpace($fields['name'])) {
      $errs += "frontmatter missing required field 'name' (or empty)"
    }
    elseif ($fields['name'] -ne $folderName) {
      $warns += "frontmatter name '$($fields['name'])' does not match folder name '$folderName'"
    }
    if (-not $fields.ContainsKey('description') -or [string]::IsNullOrWhiteSpace($fields['description'])) {
      $errs += "frontmatter missing required field 'description' (or empty)"
    }

    foreach ($ref in (Get-LocalFileRefs -Body $fm.body -SkillDir $skillDir)) {
      $target = Join-Path $skillDir ($ref -replace '/', '\')
      if (-not (Test-Path -LiteralPath $target)) { $errs += "referenced file not found: $ref" }
    }
  }

  $warns += Get-EncodingWarnings -Text $text

  if ($errs.Count -gt 0 -or $warns.Count -gt 0) {
    Write-Host ""
    Write-Host $rel -ForegroundColor Cyan
    foreach ($e in $errs) { Write-Host "  ERROR  $e" -ForegroundColor Red; $errorCount++ }
    foreach ($wn in $warns) { Write-Host "  WARN   $wn" -ForegroundColor Yellow; $warnCount++ }
    if ($errs.Count -gt 0) { $filesWithErrors++ }
  }
}

Write-Host ""
Write-Host ("Skills checked : {0}" -f $files.Count)
Write-Host ("Errors         : {0} (in {1} skill(s))" -f $errorCount, $filesWithErrors)
Write-Host ("Warnings       : {0}" -f $warnCount)

if ($errorCount -gt 0 -or ($Strict -and $warnCount -gt 0)) {
  Write-Host "Skill validation FAILED." -ForegroundColor Red
  exit 1
}
Write-Host "Skill validation passed." -ForegroundColor Green
exit 0
