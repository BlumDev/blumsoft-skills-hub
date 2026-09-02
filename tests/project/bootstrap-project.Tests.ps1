# Pester 5 executes the file top level during Discovery only; variables assigned there are
# gone once the It/BeforeEach bodies run (pwsh 7.6.5 + Pester 5.9 make that visible, the paths
# arrive as $null and Copy-Item dies on -LiteralPath). Setup therefore lives in BeforeAll.
BeforeAll {
  $script:RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
  $script:BootstrapSourcePath = Join-Path $script:RepoRoot 'scripts/project/bootstrap-project.ps1'
}

Describe 'bootstrap-project.ps1 argument binding' {
  BeforeEach {
    $fixtureRoot = Join-Path $TestDrive 'repo'
    $projectScriptDir = Join-Path $fixtureRoot 'scripts/project'
    $skillsScriptDir = Join-Path $fixtureRoot 'scripts/skills'
    $templateRoot = Join-Path $fixtureRoot 'templates/project'
    $projectRoot = Join-Path $TestDrive 'project'

    New-Item -ItemType Directory -Path $projectScriptDir -Force | Out-Null
    New-Item -ItemType Directory -Path $skillsScriptDir -Force | Out-Null
    New-Item -ItemType Directory -Path $templateRoot -Force | Out-Null
    New-Item -ItemType Directory -Path $projectRoot -Force | Out-Null

    Copy-Item -LiteralPath $script:BootstrapSourcePath -Destination $projectScriptDir
    # -Path, not -LiteralPath: the trailing * has to expand. With -LiteralPath the fixture
    # stayed empty and bootstrap-project.ps1 died on "Template not found".
    Copy-Item -Path (Join-Path $script:RepoRoot 'templates/project/*') -Destination $templateRoot -Recurse
    Set-Content -LiteralPath (Join-Path $skillsScriptDir 'sync.ps1') -Encoding utf8NoBOM -Value @'
[CmdletBinding(SupportsShouldProcess)]
param(
  [string]$Profile = 'freelancer-fullstack',
  [string[]]$BundleId,
  [switch]$IncludeExtended,
  [string[]]$Targets,
  [string]$WorkspaceRoot = '',
  [switch]$SyncAntigravityWorkflows,
  [switch]$DryRun
)

$global:BootstrapSyncInvocation = [pscustomobject]@{
  Profile = $Profile
  BundleId = @($BundleId)
  IncludeExtended = [bool]$IncludeExtended
  Targets = @($Targets)
  WorkspaceRoot = $WorkspaceRoot
  SyncAntigravityWorkflows = [bool]$SyncAntigravityWorkflows
  DryRun = [bool]$DryRun
  BoundParameterKeys = @($PSBoundParameters.Keys)
}
'@

    $bootstrapPath = Join-Path $projectScriptDir 'bootstrap-project.ps1'
    Remove-Variable -Name BootstrapSyncInvocation -Scope Global -ErrorAction SilentlyContinue
  }

  AfterEach {
    Remove-Variable -Name BootstrapSyncInvocation -Scope Global -ErrorAction SilentlyContinue
  }

  It 'binds multiple bundle IDs and named sync parameters correctly' {
    $bootstrapArgs = @{
      ProjectRoot = $projectRoot
      BundleId = @('engineering-core', 'web-product')
      IncludeExtended = $true
      SyncAntigravityWorkflows = $true
    }
    & $bootstrapPath @bootstrapArgs

    $invocation = $global:BootstrapSyncInvocation
    $invocation | Should -Not -BeNullOrEmpty
    $invocation.BundleId | Should -HaveCount 2
    $invocation.BundleId[0] | Should -Be 'engineering-core'
    $invocation.BundleId[1] | Should -Be 'web-product'
    $invocation.Targets | Should -HaveCount 1
    $invocation.Targets[0] | Should -Be 'vscode-copilot'
    $invocation.WorkspaceRoot | Should -Be (Resolve-Path $projectRoot).Path
    $invocation.IncludeExtended | Should -BeTrue
    $invocation.SyncAntigravityWorkflows | Should -BeTrue
    $invocation.BoundParameterKeys | Should -Contain 'BundleId'
    $invocation.BoundParameterKeys | Should -Not -Contain 'Profile'
  }
}
