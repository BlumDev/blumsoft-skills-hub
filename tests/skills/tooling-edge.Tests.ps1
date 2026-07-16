$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$vendorImportPath = Join-Path $repoRoot 'scripts/skills/vendor-import.ps1'
$libPath = Join-Path $repoRoot 'scripts/skills/lib.ps1'
$syncSourcePath = Join-Path $repoRoot 'scripts/skills/sync.ps1'
$pythonCommand = Get-Command python -ErrorAction SilentlyContinue

$unsafeSkillCases = @(
  @{ SkillName = '../outside' }
  @{ SkillName = '*' }
)
$serverHelperCases = @(
  @{ Name = 'custom'; Path = Join-Path $repoRoot 'skills/custom/web/scripts/with_server.py' }
  @{ Name = 'vendor'; Path = Join-Path $repoRoot 'skills/vendor/guanyang/webapp-testing/scripts/with_server.py' }
)

Describe 'vendor-import.ps1 native command handling' {
  It 'throws when the skill installer returns a nonzero exit code' {
    $tokens = $null
    $parseErrors = $null
    $ast = [System.Management.Automation.Language.Parser]::ParseFile(
      $vendorImportPath,
      [ref]$tokens,
      [ref]$parseErrors
    )
    @($parseErrors).Count | Should -Be 0
    $functionAst = @(
      $ast.FindAll(
        { param($node) $node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq 'Install-RepoSkills' },
        $true
      )
    )[0]
    $functionAst | Should -Not -BeNullOrEmpty
    . ([scriptblock]::Create($functionAst.Extent.Text))

    $fixtureRoot = Join-Path $TestDrive 'native-command'
    $destPath = Join-Path $fixtureRoot 'skills/vendor/test'
    New-Item -ItemType Directory -Path $fixtureRoot -Force | Out-Null
    $root = $fixtureRoot
    $installer = 'unused-installer.py'
    $registry = @(
      [ordered]@{ name = 'example'; source = 'vendor-test'; path = 'skills/vendor/test/example' }
    )

    $installArgs = @{
      Repo = 'example/repository'
      SourceType = 'vendor-test'
      DestPath = $destPath
    }
    $parameterNames = @(
      $functionAst.Body.ParamBlock.Parameters | ForEach-Object { $_.Name.VariablePath.UserPath }
    )
    if ($parameterNames -contains 'Commit') { $installArgs.Commit = 'locked-commit' }

    $previousLastExitCode = $global:LASTEXITCODE
    $global:FakePyCalled = $false
    $caught = $null
    function py { $global:FakePyCalled = $true; $global:LASTEXITCODE = 17 }
    try {
      try { Install-RepoSkills @installArgs } catch { $caught = $_ }
      $fakePyCalled = $global:FakePyCalled
    } finally {
      $global:LASTEXITCODE = $previousLastExitCode
      Remove-Variable -Name FakePyCalled -Scope Global -ErrorAction SilentlyContinue
    }

    $fakePyCalled | Should -BeTrue
    $caught | Should -Not -BeNullOrEmpty
  }
}

Describe 'Get-AllBundles duplicate handling' {
  It 'rejects duplicate bundle IDs' {
    . $libPath
    $fixtureRoot = Join-Path $TestDrive 'duplicate-bundles'
    $bundleDir = Join-Path $fixtureRoot 'bundles'
    New-Item -ItemType Directory -Path $bundleDir -Force | Out-Null
    Set-Content -LiteralPath (Join-Path $bundleDir 'first.yaml') -Encoding utf8NoBOM -Value @(
      'id: duplicate'
      'name: First'
      'core_skills:'
      '  - first-skill'
    )
    Set-Content -LiteralPath (Join-Path $bundleDir 'second.yaml') -Encoding utf8NoBOM -Value @(
      'id: duplicate'
      'name: Second'
      'core_skills:'
      '  - second-skill'
    )

    { Get-AllBundles -Root $fixtureRoot } | Should -Throw
  }
}

Describe 'sync.ps1 unsafe skill names' {
  It 'rejects <SkillName> without changing existing targets' -TestCases $unsafeSkillCases {
    param($SkillName)
    $fixtureRoot = Join-Path $TestDrive "sync-$([guid]::NewGuid())"
    $fixtureScripts = Join-Path $fixtureRoot 'scripts/skills'
    $sourceSkill = Join-Path $fixtureRoot 'skills/custom/source'
    $workspaceRoot = Join-Path $fixtureRoot 'workspace'
    $targetSkillDir = Join-Path $workspaceRoot '.github/skills/existing'
    $sentinelPath = Join-Path $targetSkillDir 'sentinel.txt'

    New-Item -ItemType Directory -Path $fixtureScripts -Force | Out-Null
    Copy-Item -LiteralPath $libPath -Destination $fixtureScripts
    Copy-Item -LiteralPath $syncSourcePath -Destination $fixtureScripts
    New-Item -ItemType Directory -Path (Join-Path $fixtureRoot 'bundles') -Force | Out-Null
    Set-Content -LiteralPath (Join-Path $fixtureRoot 'bundles/test-bundle.yaml') -Encoding utf8NoBOM -Value @(
      'id: test-bundle'
      'name: Test bundle'
      'compose_with:'
      'core_skills:'
      "  - $SkillName"
    )
    New-Item -ItemType Directory -Path (Join-Path $fixtureRoot 'skills') -Force | Out-Null
    Set-Content -LiteralPath (Join-Path $fixtureRoot 'skills/registry.yaml') -Encoding utf8NoBOM -Value @(
      'skills:'
      "  - name: $SkillName"
      '    source: custom'
      '    path: skills/custom/source'
    )
    New-Item -ItemType Directory -Path $sourceSkill -Force | Out-Null
    Set-Content -LiteralPath (Join-Path $sourceSkill 'SKILL.md') -Encoding utf8NoBOM -Value '---'
    New-Item -ItemType Directory -Path $targetSkillDir -Force | Out-Null
    Set-Content -LiteralPath $sentinelPath -Encoding utf8NoBOM -Value 'sentinel'

    $fixtureSync = Join-Path $fixtureScripts 'sync.ps1'
    $thrown = $null
    try {
      & $fixtureSync -BundleId 'test-bundle' -Targets 'vscode-copilot' -WorkspaceRoot $workspaceRoot
    } catch {
      $thrown = $_
    }

    $thrown | Should -Not -BeNullOrEmpty
    Test-Path -LiteralPath $sentinelPath | Should -BeTrue
    Test-Path -LiteralPath (Join-Path $workspaceRoot '.github/outside') | Should -BeFalse
  }
}

Describe 'with_server.py occupied port handling' {
  It 'rejects an occupied port in the <Name> copy' -TestCases $serverHelperCases -Skip:($null -eq $pythonCommand) {
    param($Name, $Path)
    $markerPath = Join-Path $TestDrive "$Name-command-ran.txt"
    $commandScript = Join-Path $TestDrive "$Name-command.py"
    $markerLiteral = ConvertTo-Json -InputObject $markerPath -Compress
    Set-Content -LiteralPath $commandScript -Encoding utf8NoBOM -Value "from pathlib import Path`nPath($markerLiteral).write_text('ran', encoding='utf-8')"
    $serverCommand = '"{0}" -c "pass"' -f $pythonCommand.Source.Replace('"', '\"')
    $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, 0)
    $listener.Start()
    $exitCode = $null
    $previousNativePreference = $PSNativeCommandUseErrorActionPreference
    try {
      $port = ([System.Net.IPEndPoint]$listener.LocalEndpoint).Port
      $PSNativeCommandUseErrorActionPreference = $false
      $null = & $pythonCommand.Source $Path --server $serverCommand --port $port --timeout 1 -- $pythonCommand.Source $commandScript 2>&1
      $exitCode = $LASTEXITCODE
    } finally {
      $PSNativeCommandUseErrorActionPreference = $previousNativePreference
      $listener.Stop()
    }

    $exitCode | Should -Not -Be 0
    Test-Path -LiteralPath $markerPath | Should -BeFalse
  }
}
