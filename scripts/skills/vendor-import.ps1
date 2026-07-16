param(
  [switch]$SkipGuanyang,
  [switch]$SkipSickn33
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "lib.ps1")

$root = Get-SkillsRepoRoot
$registry = Get-RegistryEntries -Root $root
$lockPath = Join-Path $root 'vendor-lock.json'
if (-not (Test-Path $lockPath)) { throw "vendor-lock.json not found at $lockPath" }
$lock = Get-Content -Path $lockPath -Raw | ConvertFrom-Json
$repoCommits = @{}
foreach($repo in @('guanyang/antigravity-skills','sickn33/antigravity-awesome-skills')){
  $repoProp = $lock.repos.PSObject.Properties[$repo]
  if (-not $repoProp -or [string]::IsNullOrWhiteSpace($repoProp.Value.commit)) { throw "Kein gesperrter Commit für Repository: $repo" }
  $repoCommits[$repo] = $repoProp.Value.commit
}

$userHome = if (-not [string]::IsNullOrWhiteSpace($HOME)) { $HOME } else { $env:USERPROFILE }
if ([string]::IsNullOrWhiteSpace($userHome)) { throw 'Home directory not found in $HOME or $env:USERPROFILE.' }
$codexHome = if (-not [string]::IsNullOrWhiteSpace($env:CODEX_HOME)) { $env:CODEX_HOME } else { Join-Path $userHome '.codex' }
$installer = Join-Path $codexHome 'skills/.system/skill-installer/scripts/install-skill-from-github.py'
if (-not (Test-Path $installer)) { throw "Installer script not found: $installer" }

$preExistingSkills = @{}
foreach ($entry in $registry | Where-Object { $_['source'] -like 'vendor-*' }) {
  $skillPath = Join-Path $root $entry['path']
  if (Test-Path $skillPath) { $preExistingSkills[$entry['name']] = $true }
}

function Install-RepoSkills {
  param(
    [Parameter(Mandatory=$true)][string]$Repo,
    [Parameter(Mandatory=$true)][string]$SourceType,
    [Parameter(Mandatory=$true)][string]$DestPath,
    [Parameter(Mandatory=$true)][string]$Commit
  )

  $destRelative = [System.IO.Path]::GetRelativePath($root, $DestPath).Replace('\','/')
  $allSkills = @(
    $registry |
      Where-Object { $_['source'] -eq $SourceType -and $_['path'].Replace('\','/').StartsWith($destRelative + '/') } |
      ForEach-Object { $_['name'] } |
      Sort-Object -Unique
  )
  if ($allSkills.Count -eq 0) { Write-Host "No skills to import for source type '$SourceType'."; return }

  $skills = @()
  foreach ($s in $allSkills) { if (-not (Test-Path (Join-Path $DestPath $s))) { $skills += $s } }
  if ($skills.Count -eq 0) { Write-Host "All skills already present for source type '$SourceType'."; return }

  $paths = @(); foreach($s in $skills){ $paths += "skills/$s" }
  New-Item -ItemType Directory -Path $DestPath -Force | Out-Null
  Write-Host "Installing $($skills.Count) skills from $Repo to $DestPath"
  & py -3 $installer --repo $Repo --ref $Commit --dest $DestPath --path $paths
  if ($LASTEXITCODE -ne 0) { throw "Skill-Installer für Repository '$Repo' mit Exitcode $LASTEXITCODE fehlgeschlagen." }
}

if (-not $SkipGuanyang) { Install-RepoSkills -Repo 'guanyang/antigravity-skills' -SourceType 'vendor-guanyang' -DestPath (Join-Path $root 'skills/vendor/guanyang') -Commit $repoCommits['guanyang/antigravity-skills'] }
if (-not $SkipSickn33) { Install-RepoSkills -Repo 'sickn33/antigravity-awesome-skills' -SourceType 'vendor-sickn33' -DestPath (Join-Path $root 'skills/vendor/sickn33') -Commit $repoCommits['sickn33/antigravity-awesome-skills'] }

foreach ($entry in $registry | Where-Object { $_['source'] -like 'vendor-*' }) {
  if ($preExistingSkills.ContainsKey($entry['name'])) { continue }
  $skillPath = Join-Path $root $entry['path']
  if (-not (Test-Path $skillPath)) { continue }
  $repo = $entry['upstream_repo']
  $commit = $repoCommits[$repo]
  Set-Content -Path (Join-Path $skillPath 'UPSTREAM.md') -Encoding UTF8 -Value @(
    "source_repo: $repo",
    "source_path: skills/$($entry['name'])",
    "source_commit: $commit",
    "imported_at: $((Get-Date).ToUniversalTime().ToString('o'))",
    "local_changes: none",
    "license: MIT"
  )
  $skillProp = $lock.skills.PSObject.Properties[$entry['name']]
  if ($skillProp) { $skillProp.Value.commit = $commit }
}

$lock.generated_at = (Get-Date).ToUniversalTime().ToString('o')
$lock | ConvertTo-Json -Depth 8 | Set-Content -Path $lockPath -Encoding UTF8
Write-Host 'Vendor import complete.'
