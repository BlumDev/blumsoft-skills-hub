# Regression test for 20260901-setup-from-profile-apply-misleading.
#
# setup-from-profile.ps1 only orchestrates its three sibling scripts, so the fixture replaces
# them with stubs that append their name and arguments to a log file. That keeps the test
# deterministic and offline: the real vendor-import.ps1 downloads skills from GitHub and
# rewrites vendor-lock.json, which is exactly what must not happen without -Apply.
#
# Requires Pester 5+.
#   Invoke-Pester -Path tests/

BeforeAll {
    $script:RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path

    function New-SetupFixture {
        $tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("skillshub-setup-" + [guid]::NewGuid().ToString('N').Substring(0, 8))
        $scriptDir = Join-Path $tmp 'scripts/skills'
        New-Item -ItemType Directory -Path $scriptDir -Force | Out-Null

        Copy-Item (Join-Path $script:RepoRoot 'scripts/skills/setup-from-profile.ps1') (Join-Path $scriptDir 'setup-from-profile.ps1')

        Set-Content -Path (Join-Path $scriptDir 'vendor-import.ps1') -Value @'
Add-Content -LiteralPath $env:SKILLSHUB_SETUP_LOG -Value 'vendor-import'
'@
        Set-Content -Path (Join-Path $scriptDir 'validate.ps1') -Value @'
Add-Content -LiteralPath $env:SKILLSHUB_SETUP_LOG -Value 'validate'
'@
        Set-Content -Path (Join-Path $scriptDir 'sync.ps1') -Value @'
param([string]$Profile, [switch]$DryRun, [switch]$SyncAntigravityWorkflows)
Add-Content -LiteralPath $env:SKILLSHUB_SETUP_LOG -Value "sync Profile=$Profile DryRun=$DryRun"
'@

        [pscustomobject]@{
            Root  = $tmp
            Setup = Join-Path $scriptDir 'setup-from-profile.ps1'
            Log   = Join-Path $tmp 'calls.log'
        }
    }

    # Returns the recorded child script calls, one line each.
    function Invoke-FixtureSetup {
        param(
            [Parameter(Mandatory = $true)][psobject]$Fixture,
            [switch]$Apply
        )

        $originalLog = $env:SKILLSHUB_SETUP_LOG
        try {
            $env:SKILLSHUB_SETUP_LOG = $Fixture.Log
            & $Fixture.Setup -Profile 'freelancer-fullstack' -Apply:$Apply *>&1 | Out-Null
        } finally {
            $env:SKILLSHUB_SETUP_LOG = $originalLog
        }

        @(Get-Content -LiteralPath $Fixture.Log -ErrorAction SilentlyContinue)
    }
}

Describe 'setup-from-profile.ps1 preview run' {
    AfterEach {
        if ($script:fixture) {
            Remove-Item -LiteralPath $script:fixture.Root -Recurse -Force -ErrorAction SilentlyContinue
            $script:fixture = $null
        }
    }

    It 'does not run vendor-import without -Apply' {
        # vendor-import writes vendor-lock.json and downloads missing vendor skills. A run that
        # only previews the sync must not change the repo on the way there.
        $script:fixture = New-SetupFixture
        $calls = Invoke-FixtureSetup -Fixture $script:fixture

        $calls | Should -Not -Contain 'vendor-import'
        $calls | Should -Contain 'validate'
        $calls | Should -Contain 'sync Profile=freelancer-fullstack DryRun=True'
    }

    It 'runs vendor-import with -Apply' {
        # Guards the test above: without this, dropping the vendor-import call entirely would
        # also pass.
        $script:fixture = New-SetupFixture
        $calls = Invoke-FixtureSetup -Fixture $script:fixture -Apply

        $calls | Should -Contain 'vendor-import'
        $calls | Should -Contain 'validate'
        $calls | Should -Contain 'sync Profile=freelancer-fullstack DryRun=False'
    }
}
