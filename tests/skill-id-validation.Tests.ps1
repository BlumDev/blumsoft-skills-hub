# Regression tests for 20260714-sync-remove-path-traversal.
#
# The bug: sync.ps1 built its delete target with Join-Path from an unvalidated skill name
# taken straight from YAML, then handed it to Remove-Item -Recurse -Force. A name like
# '../../../victim' therefore deleted an arbitrary directory outside the skills target.
#
# Requires Pester 5+ (the 'Should -Be' operator syntax does not exist in Pester 3).
#   Invoke-Pester -Path tests/

BeforeAll {
    $script:RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
    . (Join-Path $script:RepoRoot 'scripts/skills/lib.ps1')

    # Builds a throwaway repo whose registry/bundle declare $SkillName, plus a victim
    # directory outside the sync target that holds a canary file. Returns the paths so a
    # test can run the real sync.ps1 against it and check what survived.
    function New-TraversalFixture {
        param([Parameter(Mandatory = $true)][AllowEmptyString()][string]$SkillName)

        $tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("skillshub-test-" + [guid]::NewGuid().ToString('N').Substring(0, 8))
        $repo = Join-Path $tmp 'repo'
        New-Item -ItemType Directory -Path (Join-Path $repo 'scripts/skills') -Force | Out-Null
        New-Item -ItemType Directory -Path (Join-Path $repo 'skills/custom/harmless') -Force | Out-Null
        New-Item -ItemType Directory -Path (Join-Path $repo 'bundles') -Force | Out-Null

        Copy-Item (Join-Path $script:RepoRoot 'scripts/skills/sync.ps1') (Join-Path $repo 'scripts/skills/sync.ps1')
        Copy-Item (Join-Path $script:RepoRoot 'scripts/skills/lib.ps1') (Join-Path $repo 'scripts/skills/lib.ps1')
        Set-Content -Path (Join-Path $repo 'skills/custom/harmless/SKILL.md') -Value '# harmless'

        # The victim sits outside the sync target; from <tmp>/workspace/.github/skills
        # exactly three '..' segments reach it.
        $victim = Join-Path $tmp 'victim'
        New-Item -ItemType Directory -Path $victim -Force | Out-Null
        $canary = Join-Path $victim 'canary.txt'
        Set-Content -Path $canary -Value 'must survive the sync run'

        $workspace = Join-Path $tmp 'workspace'
        New-Item -ItemType Directory -Path (Join-Path $workspace '.github/skills') -Force | Out-Null

        Set-Content -Path (Join-Path $repo 'skills/registry.yaml') -Value @"
skills:
  - name: $SkillName
    source: custom
    path: skills/custom/harmless
"@
        Set-Content -Path (Join-Path $repo 'bundles/evil.yaml') -Value @"
id: evil
name: Evil Bundle
core_skills:
  - $SkillName
"@

        [pscustomobject]@{
            Root      = $tmp
            Sync      = Join-Path $repo 'scripts/skills/sync.ps1'
            Workspace = $workspace
            Canary    = $canary
        }
    }

    # Runs sync.ps1 against the fixture. Returns whether it aborted and whether the canary
    # outside the target directory survived.
    function Invoke-FixtureSync {
        param([Parameter(Mandatory = $true)][psobject]$Fixture)

        $aborted = $false
        try {
            & $Fixture.Sync -BundleId 'evil' -Targets 'vscode-copilot' -WorkspaceRoot $Fixture.Workspace *>&1 | Out-Null
        } catch {
            $aborted = $true
        }
        [pscustomobject]@{
            Aborted        = $aborted
            CanarySurvived = (Test-Path -LiteralPath $Fixture.Canary)
        }
    }
}

Describe 'Test-SkillId' {
    It 'accepts the real skill name <_>' -ForEach @(
        'docu', 'code-review', 'ui-ux-pro-max', 'ab-test-setup', 'notebooklm', 'top-web-vulnerabilities'
    ) {
        Test-SkillId -Id $_ | Should -BeTrue
    }

    It 'rejects <_>' -ForEach @(
        '../../evil'        # posix traversal
        '..\..\evil'        # windows traversal
        'evil/../..'        # traversal in the tail
        '..'
        '.'
        'C:\Windows'        # absolute, drive-qualified
        '\victim'           # rooted
        '\\server\share'    # unc
        'sub/skill'         # nested, must stay a direct child
        'skill*'            # wildcard, would make -Path match siblings
        'sk ill'
        'skill:stream'      # ntfs alternate data stream
        '-leading-hyphen'
        'UPPER'             # -match would accept this, -cmatch must not
        ''
    ) {
        Test-SkillId -Id $_ | Should -BeFalse
    }

    It 'rejects a name with a trailing newline (regex anchor \z, not $)' {
        Test-SkillId -Id ("evil" + [char]10) | Should -BeFalse
    }
}

Describe 'Assert-SkillId' {
    It 'returns the id unchanged for a valid name' {
        Assert-SkillId -Id 'code-review' | Should -Be 'code-review'
    }

    It 'throws on a traversal name' {
        { Assert-SkillId -Id '../../evil' } | Should -Throw '*only lowercase letters, digits and hyphens*'
    }
}

Describe 'Resolve-SkillTargetPath' {
    It 'resolves a valid skill to a direct child of the base directory' {
        $base = Join-Path ([System.IO.Path]::GetTempPath()) 'skills-base'
        $resolved = Resolve-SkillTargetPath -BaseDir $base -SkillId 'code-review'
        $resolved | Should -Be (Join-Path ([System.IO.Path]::GetFullPath($base)) 'code-review')
    }

    It 'throws before returning a path for <_>' -ForEach @('../../evil', 'C:\Windows', '..', 'sub/skill') {
        $base = Join-Path ([System.IO.Path]::GetTempPath()) 'skills-base'
        # Match the message: a bare -Throw would also pass if the function did not exist.
        { Resolve-SkillTargetPath -BaseDir $base -SkillId $_ } | Should -Throw '*only lowercase letters, digits and hyphens*'
    }
}

Describe 'sync.ps1 refuses to delete outside the skills target directory' {
    AfterEach {
        if ($script:fixture) {
            Remove-Item -LiteralPath $script:fixture.Root -Recurse -Force -ErrorAction SilentlyContinue
            $script:fixture = $null
        }
    }

    It 'aborts on a traversal skill name and deletes nothing' {
        $script:fixture = New-TraversalFixture -SkillName '../../../victim'
        $result = Invoke-FixtureSync -Fixture $script:fixture

        $result.Aborted | Should -BeTrue -Because 'the id allowlist must reject the name'
        $result.CanarySurvived | Should -BeTrue -Because 'nothing outside the target directory may be deleted'
    }

    It 'aborts on an absolute skill name and deletes nothing' {
        $script:fixture = New-TraversalFixture -SkillName 'C:\Windows\Temp\victim'
        $result = Invoke-FixtureSync -Fixture $script:fixture

        $result.Aborted | Should -BeTrue
        $result.CanarySurvived | Should -BeTrue
    }

    It 'still syncs a legitimate skill name' {
        # Guards the fixture itself: without this, the two tests above would also pass if
        # sync.ps1 aborted for some unrelated reason.
        $script:fixture = New-TraversalFixture -SkillName 'harmless'
        $result = Invoke-FixtureSync -Fixture $script:fixture

        $result.Aborted | Should -BeFalse
        Test-Path -LiteralPath (Join-Path $script:fixture.Workspace '.github/skills/harmless/SKILL.md') | Should -BeTrue
    }
}
