# Regression tests for 20260901-sync-target-collision and 20260901-sync-non-atomic-replace.
#
# Both findings sit in the target handling of sync.ps1, so they share one fixture: a throwaway
# repo with a single skill plus a redirected home directory. The redirect goes through
# $env:USERPROFILE of a child pwsh, because pwsh derives $HOME from it at startup. The real
# ~/.codex/skills of the user is therefore never touched by these tests.
#
# Requires Pester 5+.
#   Invoke-Pester -Path tests/

BeforeAll {
    $script:RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
    $script:PwshExe = (Get-Process -Id $PID).Path

    # Throwaway repo carrying one skill 'harmless'. The skill holds a second file that sorts
    # after SKILL.md, so a recursive delete that dies halfway through is visible in what survives.
    function New-SyncFixture {
        $tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("skillshub-sync-" + [guid]::NewGuid().ToString('N').Substring(0, 8))
        $repo = Join-Path $tmp 'repo'
        New-Item -ItemType Directory -Path (Join-Path $repo 'scripts/skills') -Force | Out-Null
        New-Item -ItemType Directory -Path (Join-Path $repo 'skills/custom/harmless') -Force | Out-Null
        New-Item -ItemType Directory -Path (Join-Path $repo 'bundles') -Force | Out-Null

        Copy-Item (Join-Path $script:RepoRoot 'scripts/skills/sync.ps1') (Join-Path $repo 'scripts/skills/sync.ps1')
        Copy-Item (Join-Path $script:RepoRoot 'scripts/skills/lib.ps1') (Join-Path $repo 'scripts/skills/lib.ps1')
        Set-Content -Path (Join-Path $repo 'skills/custom/harmless/SKILL.md') -Value '# harmless'
        Set-Content -Path (Join-Path $repo 'skills/custom/harmless/zz-payload.txt') -Value 'must survive a failed replace'

        Set-Content -Path (Join-Path $repo 'skills/registry.yaml') -Value @"
skills:
  - name: harmless
    source: custom
    path: skills/custom/harmless
"@
        Set-Content -Path (Join-Path $repo 'bundles/only.yaml') -Value @"
id: only
name: Only Bundle
core_skills:
  - harmless
"@

        $fakeHome = Join-Path $tmp 'home'
        New-Item -ItemType Directory -Path $fakeHome -Force | Out-Null

        [pscustomobject]@{
            Root        = $tmp
            Sync        = Join-Path $repo 'scripts/skills/sync.ps1'
            FakeHome    = $fakeHome
            SkillSource = Join-Path $repo 'skills/custom/harmless'
            InstalledAt = Join-Path $fakeHome '.codex/skills/harmless'
        }
    }

    # Runs the real sync.ps1 in its own pwsh whose home directory is the fixture. -Fault reaches
    # the script through SKILLSHUB_SYNC_FAULT, its documented fault injection hook.
    function Invoke-FixtureSync {
        param(
            [Parameter(Mandatory = $true)][psobject]$Fixture,
            [Parameter(Mandatory = $true)][string[]]$Targets,
            [string]$Fault
        )

        $originalProfile = $env:USERPROFILE
        $originalFault = $env:SKILLSHUB_SYNC_FAULT
        try {
            $env:USERPROFILE = $Fixture.FakeHome
            $env:SKILLSHUB_SYNC_FAULT = $Fault
            $command = "& '$($Fixture.Sync)' -BundleId 'only' -Targets $($Targets -join ',')"
            $output = & $script:PwshExe -NoProfile -NonInteractive -Command $command 2>&1
            $exitCode = $LASTEXITCODE
        } finally {
            $env:USERPROFILE = $originalProfile
            $env:SKILLSHUB_SYNC_FAULT = $originalFault
        }

        [pscustomobject]@{
            ExitCode = $exitCode
            Output   = (($output | ForEach-Object { $_.ToString() }) -join "`n")
        }
    }
}

Describe 'sync.ps1 target de-duplication' {
    AfterEach {
        if ($script:fixture) {
            Remove-Item -LiteralPath $script:fixture.Root -Recurse -Force -ErrorAction SilentlyContinue
            $script:fixture = $null
        }
    }

    It 'syncs a skill once when two target names resolve to the same directory' {
        # 'codex' and 'vscode-chatgpt' are aliases for ~/.codex/skills and the shipped profiles
        # list both in default_targets. Without de-duplication every skill was copied and swapped
        # twice, which buys nothing and opens a second replace window.
        $script:fixture = New-SyncFixture
        $result = Invoke-FixtureSync -Fixture $script:fixture -Targets @('codex', 'vscode-chatgpt')

        $result.ExitCode | Should -Be 0
        ([regex]::Matches($result.Output, '\[OK\] harmless')).Count | Should -Be 1
        $result.Output | Should -Match 'gleicher Ordner wie Target'
        Test-Path -LiteralPath (Join-Path $script:fixture.InstalledAt 'SKILL.md') | Should -BeTrue
    }

    It 'still syncs both targets when they resolve to different directories' {
        # Guards the fixture: without this, the test above would also pass if the skip branch
        # swallowed every target after the first one.
        $script:fixture = New-SyncFixture
        $result = Invoke-FixtureSync -Fixture $script:fixture -Targets @('codex', 'cursor')

        $result.ExitCode | Should -Be 0
        ([regex]::Matches($result.Output, '\[OK\] harmless')).Count | Should -Be 2
        Test-Path -LiteralPath (Join-Path $script:fixture.FakeHome '.cursor/skills/harmless/SKILL.md') | Should -BeTrue
    }
}

Describe 'sync.ps1 replace failure' {
    AfterEach {
        if ($script:fixture) {
            Remove-Item -LiteralPath $script:fixture.Root -Recurse -Force -ErrorAction SilentlyContinue
            $script:fixture = $null
        }
    }

    It 'leaves the installed skill complete when the target cannot be replaced' {
        # A locked file inside the installed skill makes the replace impossible. The old code
        # deleted the target first, so Remove-Item -Recurse tore the installation apart before
        # dying on the locked file. The rename based swap fails without touching anything.
        $script:fixture = New-SyncFixture
        (Invoke-FixtureSync -Fixture $script:fixture -Targets @('codex')).ExitCode | Should -Be 0

        $lockedFile = Join-Path $script:fixture.InstalledAt 'zz-payload.txt'
        $handle = [System.IO.File]::Open($lockedFile, 'Open', 'Read', 'None')
        try {
            $result = Invoke-FixtureSync -Fixture $script:fixture -Targets @('codex')

            $result.ExitCode | Should -Not -Be 0 -Because 'the locked file makes the replace impossible'
            Test-Path -LiteralPath (Join-Path $script:fixture.InstalledAt 'SKILL.md') | Should -BeTrue -Because 'a failed replace must not consume the installed skill'
            Test-Path -LiteralPath $lockedFile | Should -BeTrue
        } finally {
            $handle.Dispose()
        }
    }
}

Describe 'sync.ps1 interrupted between the two renames' {
    AfterEach {
        if ($script:fixture) {
            Remove-Item -LiteralPath $script:fixture.Root -Recurse -Force -ErrorAction SilentlyContinue
            $script:fixture = $null
        }
    }

    It 'restores the old version when the run dies after the target was moved to the backup' {
        # The window the rename based swap left open: the target is already gone, the skill lives
        # only in .<skill>.old-<guid>. Ctrl+C runs finally without running catch, and a finally that
        # deletes the backup unconditionally takes the last copy with it. The fault hook produces
        # exactly that state; the assertion is that the installation survives it.
        $script:fixture = New-SyncFixture
        (Invoke-FixtureSync -Fixture $script:fixture -Targets @('codex')).ExitCode | Should -Be 0

        # A changed source makes the restore provable: whatever ends up at the target must be the
        # old text, not the staged new one that never made it out of staging.
        Set-Content -Path (Join-Path $script:fixture.SkillSource 'SKILL.md') -Value '# harmless v2'

        $result = Invoke-FixtureSync -Fixture $script:fixture -Targets @('codex') -Fault 'between-moves'

        $result.ExitCode | Should -Not -Be 0 -Because 'the injected fault must not be swallowed'
        Test-Path -LiteralPath (Join-Path $script:fixture.InstalledAt 'SKILL.md') | Should -BeTrue -Because 'an abort between the renames must not consume the installed skill'
        (Get-Content -LiteralPath (Join-Path $script:fixture.InstalledAt 'SKILL.md') -Raw).Trim() | Should -Be '# harmless'
        (Get-Content -LiteralPath (Join-Path $script:fixture.InstalledAt 'zz-payload.txt') -Raw).Trim() | Should -Be 'must survive a failed replace'

        # Restore consumes the backup and the staging copy is dropped, so nothing is left behind.
        $leftovers = @(Get-ChildItem -LiteralPath (Split-Path -Parent $script:fixture.InstalledAt) -Force | Where-Object { $_.Name -ne 'harmless' })
        $leftovers.Count | Should -Be 0 -Because "no staging or backup directory may stay: $($leftovers.Name -join ', ')"
    }
}
