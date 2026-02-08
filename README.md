# BlumSoft Skills Hub

Bundle-first skill system for Codex, Cursor, Antigravity, and VS Code.

## Quick Start

1. Import vendor skills:

```powershell
./scripts/skills/vendor-import.ps1
```

2. Validate bundles and registry:

```powershell
./scripts/skills/validate.ps1
```

3. Resolve bundle composition:

```powershell
./scripts/skills/resolve-bundle.ps1 -BundleId essentials
./scripts/skills/resolve-bundle.ps1 -BundleId web-wizard -IncludeExtended
```

4. Sync to tool targets:

```powershell
./scripts/skills/sync.ps1 -Profile fullstack-founder
```

5. Optional: also sync Antigravity `global_workflows` bundle starters:

```powershell
./scripts/skills/sync.ps1 -Profile fullstack-founder -SyncAntigravityWorkflows
```
