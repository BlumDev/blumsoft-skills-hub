---
name: blumsoft-deploy
description: >-
  Projekt-spezifischer Release-/Deploy-Flow für die BlumSoft-Plattform
  (Repos `blumsoft-platform` + `blumsoft-devops`): von "was ist noch nicht live"
  über Vorbereiten, Push und Coolify-Redeploy bis zur Live-Verifikation und
  Masterplan-Pflege. Nutze diesen Skill, wenn BlumSoft nach Produktion soll, z. B.
  "deploy blumsoft", "release blumsoft", "redeploy web/api/admin", "bring die
  Änderungen live", "blumsoft nach prod". NICHT für generische Deploy-/Infra-Fragen
  (Docker, K8s, Terraform, CI) — dafür der `platform`-Skill. Mechanik-Details
  (Coolify-API, UUIDs, Token) stehen in `blumsoft-devops/runbooks/`; dieser Skill
  orchestriert nur Ablauf + Sicherheits-Leitplanken.
---

# BlumSoft Deploy

Release der BlumSoft-Plattform nach Produktion. Quelle ist `origin/main` von
`BlumDev/blumsoft-platform`; Coolify auf dem VPS baut daraus. Dieser Skill ist
**blumsoft-spezifisch** und setzt voraus, dass die Repos `blumsoft-platform` und
`blumsoft-devops` lokal vorliegen.

> Single Source of Truth für die **Mechanik** ist `blumsoft-devops/runbooks/`
> (`coolify-automation.md` = API-Weg, `deploy-service.md` = Deploy/Rollback) plus
> der Wrapper `blumsoft-devops/scripts/coolify.ps1`. Dieser Skill dupliziert das
> nicht, sondern legt den End-to-End-Ablauf und die Gates fest. Bei Konflikt
> gewinnt das Runbook.

## Leitplanken (vor jedem Deploy lesen)

- **Push ≠ Deploy.** Auto-Deploy ist in Coolify überall AUS (verifiziert mehrfach,
  zuletzt 2026-06-22). Ein Push nach `main` stellt nur bereit; der Prod-Build muss
  aktiv getriggert werden.
- **Coolify baut den kompletten `main`-Stand**, nicht einzelne Commits. Vor dem
  Deploy prüfen, was *sonst noch* ungedeployt auf `main` liegt — sonst geht
  unbeabsichtigt fremde Arbeit mit live.
- **Scope bestätigen lassen.** State-ändernd auf Prod: welche Services (web/api/
  admin) redeployt werden, vorher mit Marcus klären.
- **Token nie exponieren.** Der Coolify-API-Token liegt git-ignored in
  `blumsoft-devops/.coolify.env`; der Wrapper liest ihn selbst. Nie ausgeben/loggen.
- **Uncommittete WIP bleibt lokal.** Nicht ungefragt mitcommitten/mitdeployen.
- **UUIDs nicht blind vertrauen.** Coolify-Resource-UUIDs ändern sich bei
  Neuaufbau. Im Zweifel via `coolify.ps1 apps` oder Docker-Labels
  (`coolify.projectName`/`coolify.resourceName`) auflösen.

## Ablauf

### 1. Pre-Check — was ist noch nicht live?
- `git fetch origin` und drei Ebenen trennen: uncommittet (`git status`),
  committet-nicht-gepusht (`git log origin/main..HEAD`), und auf `main`-aber-
  nicht-deployed.
- **Offene Feature-Branches prüfen** (`git branch -a`, je `git log main..<branch>`).
  Gesuchte Änderung liegt oft auf einem ungemergten Branch, nicht im erwarteten File.
- Mit Marcus klären, *was* rein soll; WIP bewusst draußen lassen.

### 2. Vorbereiten
- Falls nötig mergen/cherry-picken. Doku-Konflikte (z. B. Masterplan) zugunsten
  `main` (`git checkout --ours`), Code-Konflikte bewusst auflösen.
- Gate: `npx turbo run check-types --filter=web --filter=api` (betroffene Workspaces).
- Optional sichtbare Änderungen lokal prüfen: `launch.json`-Config `web-preview`
  (Port 3199, weicht dem Docker-Stack auf 3100 aus), Inhalt per DOM-Eval verifizieren.

### 3. Deploy
- `git push origin main` (Fast-Forward).
- Redeploy je gewähltem Service über den Wrapper (öffnet SSH-Tunnel automatisch):
  `pwsh -File D:\Repos\blumsoft-devops\scripts\coolify.ps1 redeploy -Uuid <uuid>`
  (Prod-UUIDs: web `xcoo80k0k844w0sscckgko0w`, api `cws4kskkc40scccg004kgwsg`,
  admin `t0kosc88c4gs4wgg4g8480wc` — Stand prüfen via `coolify.ps1 apps`).

### 4. Live verifizieren (Pflicht, nicht nur "queued")
- Rollout abwarten: `coolify.ps1 deployments` pollen bis leer.
- `https://blumsoft.de/version.json` + Header `X-Release` haben gewechselt
  (neue `release_id`/`built_at`).
- Inhaltliche Marker auf der Zielseite live, alte weg (z. B. `curl … | grep`).
- `https://api.blumsoft.de/health` → `status: ok`.
- `ssh blumsoft-vps docker ps` → betroffene Container frisch gestartet (junge Uptime).

### 5. Nachpflege
- Masterplan-Status-Log + Version fortschreiben
  (`blumsoft-platform/docs/masterplan/BLUMSOFT_MASTERPLAN.md`), Doku-Commit pushen.

## Bei Problemen
- Build hängt / schlägt fehl: Logs in Coolify (Deployment-URL aus der
  Trigger-Antwort) oder `coolify.ps1 history -Uuid <uuid>`; Details + Rollback in
  `blumsoft-devops/runbooks/deploy-service.md`.
- API 401/403 beim Wrapper, Tunnel-Probleme: `blumsoft-devops/runbooks/coolify-automation.md`.

## Boundaries
- Generische Deploy-/Infra-/Container-/CI-Fragen → **platform**-Skill.
- Commit-Hygiene → **smart-commits**-Skill.
