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

## How-to: Was wann nutzen?

### Schnellentscheidung (Bundle + Workflow)

| Wenn du... | Bundle | Antigravity Workflow |
|---|---|---|
| allgemeine Feature-/Bug-Arbeit machst | `essentials` | `essentials.md` |
| UI/Web bauen oder verbessern willst | `web-wizard` | `web-wizard.md` |
| Security/Hardening/Audit brauchst | `security-engineer` | `security-engineer.md` |
| Growth/SEO/Pricing/Go-to-market willst | `startup-growth` | `startup-growth.md` |
| RAG/LLM/Data-Features baust | `data-ai` | `data-ai.md` |
| Deployment/Infra/Scaling machst | `devops-cloud` | `devops-cloud.md` |
| Team-/Agent-Workflows standardisieren willst | `workflow-ops` | `workflow-ops.md` |

### Wichtigste Skills (in der Praxis)

#### Universell (fast immer)

- `brainstorming`: Scope und Zielbild vor Umsetzung klaeren.
- `writing-plans`: einen umsetzbaren Plan vor Code erstellen.
- `systematic-debugging`: Fehler strukturiert und reproduzierbar isolieren.
- `verification-before-completion`: keine "done"-Aussage ohne echte Verifikation.
- `requesting-code-review`: gezielter finaler Review vor Abschluss.

#### Deine Kernskills (custom)

- `webdev`: Fullstack-Web-Umsetzung, content-first + UX-orientiert.
- `backend`: APIs, DB, Performance, Reliability.
- `code-review`: Security/Hardening/Redundanz/Qualitaetschecks.
- `docu`: technische Dokumentation und strukturierte Wissensuebergabe.
- `ai-seo-auditor`: AI-gestuetzter SEO- und Content-Qualitaetscheck.

### Bundle-Playbooks (Best Practice)

#### 1) Essentials

Wann:
- unklarer Start, gemischte Aufgaben, Bugfix + Refactor, normaler Delivery-Flow.

Ablauf:
1. Ziel/Scope klaeren (`brainstorming`).
2. Plan schreiben (`writing-plans`).
3. Umsetzen + Fehler isolieren (`systematic-debugging`).
4. Verifikation + Code-Review (`verification-before-completion`, `requesting-code-review`).

#### 2) Web Wizard

Wann:
- neue Seite, Landingpage, UX-Verbesserung, Conversion + SEO.

Ablauf:
1. Core nutzen: `webdev`, `frontend-design`, `ui-ux-pro-max`, `webapp-testing`, `seo-audit`.
2. Erst bei Bedarf erweitern: `ai-seo-auditor`, `copywriting`, `form-cro`.

#### 3) Security Engineer

Wann:
- vor Release, nach Security-Bug, bei Auth/API-Hardening.

Ablauf:
1. Core fuer Audit/Hardening fahren.
2. Findings priorisieren: exploitable zuerst.
3. Extended nur wenn noetig (`incident-responder`, `top-web-vulnerabilities`).

#### 4) Startup Growth

Wann:
- Pricing, Messaging, GTM, SEO-basierte Nachfrage.

Ablauf:
1. Value + Zielgruppe fixieren (`product-manager-toolkit`).
2. Pricing + Messaging ausarbeiten (`pricing-strategy`, `copywriting`).
3. Launch + SEO Plan (`launch-strategy`, `seo-audit`).

#### 5) Data AI

Wann:
- Prompting, RAG, Agent-Orchestrierung, MCP-Tooling.

Ablauf:
1. Architektur festlegen (`prompt-engineer`, `rag-engineer`, `langgraph`, `mcp-builder`).
2. Extended fuer Qualitaet nutzen (`evaluation`, `advanced-evaluation`).

#### 6) DevOps Cloud

Wann:
- Deployment, Infra-Aenderungen, Performance/Observability.

Ablauf:
1. Core fuer Deploy + Operability.
2. Extended bei Komplexitaet (`kubernetes-architect`, `distributed-tracing`).

#### 7) Workflow Ops

Wann:
- wiederkehrende Arbeitsablaeufe, Team-Standardisierung, Agent-Execution.

Ablauf:
1. Prozessdesign (`workflow-patterns`).
2. Orchestrierung + Automation (`workflow-orchestration-patterns`, `workflow-automation`).
3. Execution diszipliniert fahren (`project-development`, `executing-plans`).

### Prompt-Beispiele (copy/paste)

- Essentials:
  - "Use `essentials` core only. Ziel: behebe Bug X reproduzierbar, inklusive Verifikationsschritte."
- Web Wizard:
  - "Use `web-wizard` core. Ziel: baue die Landingpage fuer Feature X, mobil-first, dann SEO-Check."
- Security Engineer:
  - "Use `security-engineer` core. Fuehre Audit fuer Auth + API durch und priorisiere Findings nach Risiko."
- Startup Growth:
  - "Use `startup-growth` core. Erstelle Pricing + Messaging fuer Zielgruppe Y, inklusive Launch-Plan."
- Data AI:
  - "Use `data-ai` core. Entwerfe RAG-Flow fuer Support-QA, danach Evaluationskriterien."
- DevOps Cloud:
  - "Use `devops-cloud` core. Plane und implementiere sicheres Deployment fuer Service Z mit Rollback."
- Workflow Ops:
  - "Use `workflow-ops` core. Standardisiere unseren Delivery-Workflow mit klaren Gates."

## Best Practices (wichtig)

1. Starte immer mit `core_skills`.
2. Nimm `extended_skills` nur bei realer Mehrkomplexitaet dazu.
3. Nutze pro Aufgabe ein primaeres Bundle.
4. Fuer Security- oder Release-kritische Aufgaben immer Verifikation erzwingen.
5. Bundle/Registry-Aenderungen nie ohne `validate.ps1` abschliessen.

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
