# Regression tests for validate.ps1 archive-path and profile-leak checks
# (Lücke aus 20260902-cursor-testgaps).
#
# CI runs validate.ps1 only against the healthy repo. These fixtures copy the real
# script into a throwaway tree so the failing classes can be asserted without
# touching the checked-in skills.
#
# Requires Pester 5+.
#   Invoke-Pester -Path tests/

BeforeAll {
    $script:RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
    $script:PwshExe = (Get-Process -Id $PID).Path

    function New-ValidateFixture {
        $tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("skillshub-validate-" + [guid]::NewGuid().ToString('N').Substring(0, 8))
        $repo = Join-Path $tmp 'repo'
        New-Item -ItemType Directory -Path (Join-Path $repo 'scripts/skills') -Force | Out-Null
        New-Item -ItemType Directory -Path (Join-Path $repo 'bundles/prompts') -Force | Out-Null
        New-Item -ItemType Directory -Path (Join-Path $repo 'skills/custom/x') -Force | Out-Null
        New-Item -ItemType Directory -Path (Join-Path $repo 'profiles') -Force | Out-Null

        Copy-Item (Join-Path $script:RepoRoot 'scripts/skills/validate.ps1') (Join-Path $repo 'scripts/skills/validate.ps1')
        Copy-Item (Join-Path $script:RepoRoot 'scripts/skills/lib.ps1') (Join-Path $repo 'scripts/skills/lib.ps1')

        Set-Content -Path (Join-Path $repo 'bundles/prompts/only.md') -Value 'starter'
        Set-Content -Path (Join-Path $repo 'skills/custom/x/SKILL.md') -Value @"
---
name: x
description: fixture skill
---
# x
"@
        Set-Content -Path (Join-Path $repo 'skills/registry.yaml') -Value @"
skills:
  - name: x
    source: custom
    path: skills/custom/x
"@
        Set-Content -Path (Join-Path $repo 'skills/archive-plan.yaml') -Value @"
skills:
  - name: x
    status: archive-reference
    target: only
"@
        Set-Content -Path (Join-Path $repo 'bundles/only.yaml') -Value @"
id: only
name: Only Bundle
goal: Fixture bundle for archive and profile checks.
recommended_start_skill: x
core_skills:
  - x
starter_prompt: bundles/prompts/only.md
"@
        Set-Content -Path (Join-Path $repo 'profiles/leaky.json') -Value @"
{
  "profile_name": "leaky",
  "include_extended": false,
  "bundle_ids": ["only"],
  "default_targets": ["codex"]
}
"@

        [pscustomobject]@{
            Root     = $tmp
            Validate = Join-Path $repo 'scripts/skills/validate.ps1'
        }
    }
}

Describe 'validate.ps1 archive mismatch and profile leak' {
    AfterEach {
        if ($script:fixture) {
            Remove-Item -LiteralPath $script:fixture.Root -Recurse -Force -ErrorAction SilentlyContinue
            $script:fixture = $null
        }
    }

    It 'fails on an archive-reference skill outside skills/archive and inside a profile' {
        # Fällt aus, wenn die Prüfung "archive-reference muss unter skills/archive liegen"
        # entfernt wird, und ebenso, wenn die Prüfung auf archive-reference in der
        # Core-Auflösung eines Profils entfernt wird. Beide Meldungen werden einzeln geprüft,
        # der Exit-Code allein trägt hier nichts: die Fixture erzeugt ohnehin einen zweiten
        # Fehler (with_server.py fehlt in der Wegwerf-Kopie).

        $script:fixture = New-ValidateFixture
        $output = & $script:PwshExe -NoProfile -NonInteractive -File $script:fixture.Validate 2>&1
        $exitCode = $LASTEXITCODE
        $text = (($output | ForEach-Object { $_.ToString() }) -join "`n")

        $exitCode | Should -Be 1
        $text | Should -Match 'must live under skills/archive'
        $text | Should -Match 'includes archive-reference skill'
    }
}
