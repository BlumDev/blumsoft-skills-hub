# Tests for Resolve-BundleSkills in scripts/skills/lib.ps1 (Lücke aus 20260902-cursor-testgaps).
#
# Requires Pester 5+.
#   Invoke-Pester -Path tests/

BeforeAll {
    $script:RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
    . (Join-Path $script:RepoRoot 'scripts/skills/lib.ps1')
}

Describe 'Resolve-BundleSkills compose_with and extended' {
    It 'resolves composed bundles depth first and survives a cycle' {
        # Fällt aus, wenn in Add-BundleInternal die Schleife über $bundle.compose_with entfernt wird
        # (dann fehlen x und y) und ebenso, wenn der Zyklus-Wächter $seenBundles.ContainsKey
        # entfernt wird (dann läuft der zweite Teil in einen call depth overflow).

        $bundles = @{}
        $bundles['a'] = [ordered]@{
            id              = 'a'
            compose_with    = @('b')
            core_skills     = @('z')
            extended_skills = @('e')
        }
        $bundles['b'] = [ordered]@{
            id              = 'b'
            compose_with    = @()
            core_skills     = @('x', 'y')
            extended_skills = @()
        }

        $coreOnly = Resolve-BundleSkills -BundleIds @('a') -Bundles $bundles
        $coreOnly | Should -Be @('x', 'y', 'z')

        $withExtended = Resolve-BundleSkills -BundleIds @('a') -Bundles $bundles -IncludeExtended
        $withExtended | Should -Be @('x', 'y', 'z', 'e')

        $cyclic = @{}
        $cyclic['a'] = [ordered]@{
            id              = 'a'
            compose_with    = @('b')
            core_skills     = @('z')
            extended_skills = @('e')
        }
        $cyclic['b'] = [ordered]@{
            id              = 'b'
            compose_with    = @('a')
            core_skills     = @('x', 'y')
            extended_skills = @()
        }

        { Resolve-BundleSkills -BundleIds @('a') -Bundles $cyclic } | Should -Not -Throw
        $cycled = Resolve-BundleSkills -BundleIds @('a') -Bundles $cyclic
        $cycled | Should -Be @('x', 'y', 'z')
    }
}
