# BlumSoft Skills Hub

Bundle-first Skill-System fuer Codex, Cursor, Antigravity und VS Code.

## Was ist was?

- `Skill`: ein einzelner Skill-Ordner mit `SKILL.md`.
- `Bundle`: kuratierter Starter-Stack aus `core_skills` und optional `extended_skills`.
- `Profile`: vordefinierte Bundle-Auswahl (z. B. `fullstack-founder`).
- `global_workflows` (Antigravity): Session-Starter-Dateien mit Bundle-Startanweisungen.

Wichtig: Bundles sind Guided Composition, keine automatische "magische" Skill-Fusion.

## Was sind `global_workflows` konkret?

`global_workflows` sind Markdown-Startvorlagen unter:

- `~/.gemini/antigravity/global_workflows`

Sie definieren:

- welches Bundle du starten willst,
- welche Core-Skills zuerst genutzt werden sollen,
- welchen Ablauf du in der Session befolgst.

Sie sind keine Skills und ersetzen keine `SKILL.md`-Ordner.

## Struktur im Repo

- `skills/custom/*`: deine eigenen Kernskills (`webdev`, `backend`, `docu`, ...)
- `skills/vendor/guanyang/*`: primaere Vendor-Quelle
- `skills/vendor/sickn33/*`: Gap-Fill
- `skills/registry.yaml`: kanonische Skill-Quelle pro Name
- `bundles/*.yaml`: Bundle-Definitionen
- `bundles/prompts/*.md`: Starter-Prompts je Bundle
- `adapters/antigravity/global_workflows/*.md`: Bundle-Starter fuer Antigravity

## Einmaliges Setup

Im Repo `blumsoft-skills-hub` ausfuehren:

```powershell
./scripts/skills/vendor-import.ps1
./scripts/skills/validate.ps1
./scripts/skills/sync.ps1 -Profile fullstack-founder -SyncAntigravityWorkflows
```

## Taegliche Nutzung

1. Bundle ansehen (Core oder Core+Extended):

```powershell
./scripts/skills/resolve-bundle.ps1 -BundleId web-wizard
./scripts/skills/resolve-bundle.ps1 -BundleId web-wizard -IncludeExtended
```

2. Skills in deine Tools synchronisieren:

```powershell
./scripts/skills/sync.ps1 -Profile fullstack-founder
```

3. Optional nur bestimmte Bundles/Ziele:

```powershell
./scripts/skills/sync.ps1 -BundleId web-wizard,security-engineer -Targets codex,cursor,antigravity
./scripts/skills/sync.ps1 -BundleId data-ai -IncludeExtended -Targets codex
```

4. Antigravity-Workflow-Dateien mitziehen:

```powershell
./scripts/skills/sync.ps1 -Profile fullstack-founder -SyncAntigravityWorkflows
```

Hinweis: Der Target `vscode-copilot` erzeugt lokal `./.github/skills/` als Sync-Output.

## Aufraeumen alter lokaler Skills (optional)

Falls noch alte, nicht-registry-basierte Skills vorhanden sind, einmal bereinigen (Codex-Beispiel):

```powershell
$dir = Join-Path $HOME '.codex/skills'
Get-ChildItem $dir -Directory | Where-Object { $_.Name -ne '.system' } | ForEach-Object { cmd /c rmdir /s /q "$($_.FullName)" }
```

Danach erneut `sync.ps1` ausfuehren.

## Vendor-Updates

Pruefen, ob Upstream neuer ist:

```powershell
./scripts/skills/update-vendor.ps1
```

Wenn du Upstream-Staende aktualisieren willst:

```powershell
./scripts/skills/vendor-import.ps1
./scripts/skills/validate.ps1
```

## Standard-Flow (Empfehlung)

1. Session mit Bundle starten (in Antigravity optional ueber passendes `global_workflow`).
2. Zuerst nur Core-Skills nutzen.
3. Extended-Skills nur bei Bedarf aktivieren.
4. Nach Bundle/Registry-Aenderungen immer `validate.ps1` laufen lassen.
