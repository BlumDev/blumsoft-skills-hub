# Agent Instructions

## Skill Installation

This repository is a curated skills hub. Do not install every skill from the repo by default.

When the task is to install skills from this repo, use **PowerShell in the repo root** and install only the curated default profile:

```powershell
./scripts/skills/validate.ps1
./scripts/skills/sync.ps1 -Profile freelancer-fullstack
```

## Default behavior

- Prefer profile `freelancer-fullstack`.
- Do not sync the full registry.
- Do not add legacy wrapper bundles unless explicitly requested.
- Do not add archived skills unless explicitly requested.
- Add `business-growth` only when the task explicitly includes pricing, launch, SEO, analytics, CRO, or experimentation.

## If unsure

- Read `README.md`
- Read `docs/ide-agent-onboarding.md`
- Inspect `profiles/freelancer-fullstack.json`

---

## Wissens-Ablage

- `docs/backlog.md` = EINZIGE Workflow-Wahrheit (Aufgaben, Ideen, umgesetzt, verworfen).
- `docs/decisions.md` = nicht-triviale Entscheidungen (append-only, "Warum").
- `docs/reviews/YYYY-MM-DD-<agent>.md` = rohe Audit-Läufe (Findings-Puffer).
- `docs/archive/` = ausgelagerte alte Einträge (nicht default lesen; bei Triage durchsuchen).

## `backlog.md` Format

Sektionen: `## Offen` | `## Erledigt` | `## Verworfen`.
- Offen:     `- [ ] <id> Titel #bug|#idea|#task (Quelle)`
- Erledigt:  `- [x] <id> Titel (<short-sha>, YYYY-MM-DD)`
- Verworfen: `- <id> Titel — Grund (YYYY-MM-DD)`  (normale Bullets, kein Checkbox)
- ID = `YYYYMMDD-slug`. NIE renumbern/wiederverwenden. Gleiche Sache -> bestehenden Eintrag updaten.
- Kein "In Arbeit"-Status (aus Branch/Commit ableitbar). Ideen = offene Einträge mit `#idea`.

## Regeln

- Vor jedem Schreiben die Datei NEU lesen. Bestehende IDs/Inhalte bewahren. Konflikte nicht auto-überschreiben.
- Nur `docs/backlog.md` besitzt Status. Andere Dateien referenzieren nur einseitig.
- Archiv: `## Erledigt` + `## Verworfen` zusammen > 20 -> älteste nach `docs/archive/backlog-archive.md`, ~10 behalten.
- Codex läuft read-only, sofern nicht ausdrücklich zum Schreiben beauftragt.
- Secrets/Tokens/`.env` nie im Klartext (auch nicht in Findings/Reviews); nur per Name referenzieren.

Ablage-Standard: `ai-router/docs/repo-ablage-standard.md`.
</content>
