# Backlog-Archiv

Ausgelagerte Einträge aus `../backlog.md` nach der Archiv-Regel der `AGENTS.md`
(`## Erledigt` + `## Verworfen` zusammen über 20, älteste hierher, ~10 behalten).
Nur Historie: der Status steht weiterhin ausschließlich in `../backlog.md`.

## Erledigt (ausgelagert 2026-09-07)

Wartungs-Session 5b 2026-09-02 (Modul-Findings der Lesewelle 2026-09-02 plus der bekannte Pester-Punkt; Basis c13a0b3, jeder Fix mit Mutationsprobe oder Vorher-Nachher-Repro, Belege im jeweiligen Commit-Text):

- [x] 20260825-pester-alt-suiten-pwsh76 Alt-Testsuiten verloren unter pwsh 7.6.5 ihre Top-Level-Variablen in den It-Blöcken, 7 Tests rot unabhängig vom Code; Setup liegt jetzt in BeforeAll (Run-Phase, `$script:`-Scope wie in den bereits grünen Suiten) und BeforeDiscovery (TestCases, `-Skip`). Dabei kam heraus, dass die Bootstrap-Fixture ihre Templates mit `-LiteralPath ...\*` kopierte, was das Wildcard nie auflöst: der reparierte Test lief in "Template not found", jetzt `-Path`. Vorher 38 grün / 7 rot, nachher 45 / 0 (452d9f5, 2026-09-02)
- [x] 20260902-comfy-poll-not-wallclock `--timeout` war in comfy_generate.py und upscale.py keine Wanduhr: die Schleife zählte 1,5s-Schlafphasen und gab dem `/history`-Aufruf gar keinen Timeout mit, also griff der api()-Default von 600s bzw. 900s. Ein einzelner hängender Poll dehnte den Lauf weit über die angegebene Grenze. Jetzt Deadline über `time.monotonic()` und je Poll das Restbudget (max 30s) als Socket-Timeout, ein gescheiterter Poll wird wiederholt statt den Lauf zu killen (820968f, 2026-09-02)
- [x] 20260902-upscale-cleanup-removes-queued-input upscale.py löschte die Staging-Kopie im `finally` auch nach einem Timeout, obwohl der Job noch in ComfyUIs Queue stehen konnte und die Datei noch gar nicht geöffnet hatte; LoadImage scheiterte später und die GPU-Arbeit war verloren. Der Timeout-Pfad behält die Kopie jetzt und benennt sie, Erfolg und gemeldeter Fehler räumen weiter auf (820968f, 2026-09-02)
- [x] 20260902-upscale-comfy-input-hardcoded `COMFY_INPUT` war fest auf die lokale Installation codiert, während `--url`/`COMFYUI_URL` frei konfigurierbar blieb; auf eine andere Instanz gerichtet kopierte das Skript lokal und lief 1200s in den Timeout. `--input-dir` (env `COMFYUI_INPUT`) benennt den Ordner jetzt, ohne ihn wird ein nicht-lokaler Host vorab abgelehnt (a0fa1f8, 2026-09-02)
- [x] 20260902-ledger-jsonl-corrupt-line ledger.py `cmd_find` parste jede JSONL-Zeile ungeschützt; eine durch Abbruch oder parallelen `add` halb geschriebene Zeile ließ jeden späteren `find` mit JSONDecodeError sterben, samt aller intakten Einträge. Kaputte Zeilen werden jetzt übersprungen und auf stderr benannt (90aa567, 2026-09-02)
- [x] 20260902-ensure-comfyui-log-no-force ensure_comfyui.ps1 leitete auf zwei feste %TEMP%-Namen um, die ein noch laufender Vorlauf offen hält; Start-Process brach daran ab, ohne den Lauf zu stoppen, und die 240s-Schleife meldete am Ende einen Timeout für einen nie gestarteten Server. Jetzt eigene Log-Dateien je Lauf, Start-Process in try/catch und `-PassThru`, damit ein gestorbener Prozess sofort mit Exitcode gemeldet wird (592bba4, 2026-09-02)
- [x] 20260902-testing-md-tmp-path-windows `web/references/testing.md` schickte den Recon-Screenshot nach `/tmp/inspect.png`; unter Windows existiert der Pfad nicht, Playwright bricht mit FileNotFoundError ab, bevor ein einziger Selektor gelesen ist. Snippet nutzt jetzt `tempfile.gettempdir()` (ccf7c70, 2026-09-02)
- [x] 20260902-website-audit-debug-port-collision Port 9222, Profil und Report-Pfad sind fest codiert und die Warteschleife akzeptierte jeden Prozess auf dem Port, ein abgestürzter Vorlauf wurde also gemessen. Die Namen müssen fest bleiben (Shell-State überlebt keinen Tool-Call), deshalb erzwingt Schritt a jetzt die Voraussetzung: bricht ab, wenn 9222 schon antwortet, räumt Profil-Reste und alten Report weg, Schritt b wirft statt weiterzulaufen (ba957c4, 2026-09-02)

Verify der Runde-2-Commits (`docs/reviews/2026-09-01-cursor-verify.md`, cursor-grok-4.6-high, Basis daef7d0..main): 5 Commits sauber, 3 Findings, alle drei am Code bestätigt und mit Mutationsprobe belegt:

- [x] 20260901-sync-backup-deleted-in-finally Das `finally` des Skill-Austauschs löschte das Backup, sobald `$backupPath` gesetzt war; ein Abbruch zwischen den beiden Umbenennungen (Strg+C läuft durch finally ohne catch) nahm Staging und Backup mit und ließ das Ziel leer zurück. Restore jetzt im finally, Löschen erst bei nachgewiesenem Ziel, Testzugang über den Fault-Hook `SKILLSHUB_SYNC_FAULT` (fb163c6, 2026-09-01)
- [x] 20260901-upscale-input-not-cleaned-up upscale.py entfernte seine Kopie im geteilten ComfyUI-Input auf keinem Pfad, mit den eindeutigen Namen aus b223786 sammelt sich eine Datei je Lauf an; main() räumt jetzt im finally auf, OSError gefangen (8071b34, 2026-09-01)
- [x] 20260901-decisions-duplicate-adrs Die drei ADRs der Wartungs-Session standen doppelt in decisions.md, beide Kopien aus 5335314; zweite Kopie entfernt, erste unverändert, bewusste Ausnahme von append-only im Commit begründet (4010295, 2026-09-01)
- [x] 20260901-cursor-verify Verify-Lauf 20260901T120648-8b95f3 selbst: Report angelegt, Triage am Code, kein Rework an den fünf sauberen Commits (21a12a0, 2026-09-01)

## Erledigt (ausgelagert 2026-09-02)

Security-Session Careful-Fixes (Branch `security/careful-fixes`, gemergt 2026-08-25). Der Reconcile vom 2026-08-18 führte diese beiden Punkte noch als offen, richtig für seine Basis 4dcd9fd: der Fix lag zu dem Zeitpunkt erst auf dem Branch, main erreichte er über a2390a3:

- [x] 20260714-sync-remove-path-traversal sync übergibt ungeprüfte Namen an rekursives Remove-Item, `..`/Wildcards ermöglichen Traversal/Massenlöschung (5e3d7f2, 2026-07-16; verifiziert 2026-09-02: `Test-SkillId`/`Assert-SkillId`/`Resolve-SkillTargetPath` in `lib.ps1:15-55`, `sync.ps1` arbeitet durchgehend mit `-LiteralPath`)
- [x] 20260714-idea-id-allowlist-literalpath Skill-/Bundle-IDs per Allowlist validieren, `-LiteralPath` in den ID-getriebenen Pfadoperationen (5e3d7f2, 2026-07-16; verifiziert 2026-09-02: Allowlist `^[a-z0-9][a-z0-9-]*\z` mit `-cmatch` in `lib.ps1:15-19`, beim YAML-Einlesen erzwungen)
- [x] 20260825-merge-careful-fixes Branch security/careful-fixes nach main gemergt, Guard in mains Staging/ShouldProcess-Sync eingepasst, Guard-Suite 32/32 grün (a2390a3, 2026-08-25)

Wartungs-Session 2026-09-01 (Findings aus den Reviews 2026-08-24, 2026-08-25 und 2026-08-31; jeder Fix mit Regressionstest, jeder Test gegen daef7d0 gegengeprüft):

- [x] 20260901-sync-target-collision sync.ps1 synchronisierte jeden Skill zweimal in denselben Ordner, weil `codex` und `vscode-chatgpt` beide auf `~/.codex/skills` zeigen und die Profile beide in default_targets führen; Ziele werden jetzt nach aufgelöstem Ordner dedupliziert (633c2dd, 2026-09-01)
- [x] 20260901-sync-non-atomic-replace sync.ps1 löschte das Ziel vor dem finalen Move, ein Abbruch dazwischen hinterließ den Skill komplett entfernt; Austausch jetzt über zwei Renames mit Restore, `Move-Item` durch `[System.IO.Directory]::Move` ersetzt, weil Move-Item Verzeichnisse rekursiv verschiebt und bei Fehlern beide Seiten halb gefüllt zurücklässt (633c2dd, 2026-09-01)
- [x] 20260901-setup-from-profile-apply-misleading setup-from-profile.ps1 rief vendor-import.ps1 auch ohne `-Apply` und schrieb dabei vendor-lock.json und UPSTREAM.md; der Vorschau-Lauf lässt den Import jetzt aus und benennt ihn, validate.ps1 läuft weiter in beiden Pfaden (0d13561, 2026-09-01)
- [x] 20260901-comfy-generate-seed-hires-mismatch `--seed` erreichte den zweiten Sampler der Hires-Workflows nicht, der Hires-Pass blieb auf dem eingebackenen Seed 12345; SAMPLER_HIRES bekommt jetzt denselben Seed, `--steps` bleibt bewusst auf dem Basis-Pass (71a10e1 plus Skill-Doku 7763258, 2026-09-01)
- [x] 20260901-comfy-generate-poll-ignores-error Poll-Schleifen in comfy_generate.py und upscale.py lasen nur `outputs.images` und warteten bei `status=error` den vollen Timeout ab statt den Fehler zu melden; beide prüfen jetzt `status.status_str`, unklare History-Formen warten weiter (69b2d61, 2026-09-01)
- [x] 20260901-upscale-input-filename-collision upscale.py kopierte die Eingabe unter festem Namen in ComfyUIs geteilten Input-Ordner, gleicher Basename oder paralleler Lauf überschrieb die fremde Eingabe (b223786, 2026-09-01)
- [x] 20260831-cursor-audit Zweitmeinungs-Audit 2026-08-31 (cursor-grok-4.6-high): alle 3 Findings behoben, siehe die drei 20260901-Einträge zum gen-asset-Tooling (b223786, 2026-09-01)

## Erledigt (ausgelagert 2026-09-01)

Codex-Work-Orders Welle B, Chunks 1-4 (`ai-router/logs/tmp/wo-codex-skillshub-1..4.out.md`), 2026-07-16:

- [x] 20260714-bootstrap-splat-positional Bootstrap splattet Parameter positionell statt benannt, `-WorkspaceRoot`/Bundle-ID falsch gebunden, Kopie dann Abbruch (4b65c98, 2026-07-16)
- [x] 20260714-vendor-import-false-provenance vendor-import aktualisiert vorhandene Skills nicht, markiert sie aber mit HEAD, Provenienz falsch (73b2813, 2026-07-16)
- [x] 20260714-vendor-import-unlocked-commit vendor-import ignoriert Lock-Commit und prüft py-Exitcode nicht, unreviewter HEAD/Teilimport möglich (751d900, 2026-07-16)
- [x] 20260714-sync-default-targets-ignored sync liest `default_targets` nicht, Standardlauf synct zusätzlich nach Claude und ins aktuelle Repo (380f90a, 2026-07-16)
- [x] 20260714-bootstrap-dryrun-writes Bootstrap `-DryRun` schützt Template-Kopien nicht, Probelauf verändert das Zielprojekt (cfb2bd2, 2026-07-16)
- [x] 20260714-sync-delete-before-copy sync löscht Ziel vor erfolgreicher Kopie, Abbruch hinterlässt fehlenden/teilweisen Skill (2692b22, 2026-07-16)
- [x] 20260714-withserver-pipe-deadlock with_server konsumiert umgeleitete stdout/stderr nie, ausgabestarke Server blockieren bei vollem Pipe-Puffer (a487e5f, 2026-07-16)
- [x] 20260714-withserver-readiness-foreign with_server-Readiness akzeptiert jeden Port-Listener und prüft Prozessleben nicht, Tests gegen Fremd-Altprozess (a487e5f, 2026-07-16)
- [x] 20260714-withserver-orphan-children with_server beendet bei `shell=True` nur die Shell, Kindprozesse verwaisen und blockieren Ports (a487e5f, 2026-07-16)
- [x] 20260714-refreshlock-stale-content `-RefreshLock` aktualisiert nur den Repo-Commit ohne Inhalte/Skill-Commits, Lock fälschlich aktuell (17cfea6, 2026-07-16)
- [x] 20260714-vendor-import-hardcoded-user vendor-import hat hartkodierten Benutzerpfad `Marcus`, bricht auf anderen Maschinen ab (e6d1c00, 2026-07-16)
- [x] 20260714-github-calls-no-timeout GitHub-Aufrufe ohne Timeout/kontrollierte Fehlerbehandlung, Pipeline hängt oder bricht roh ab (56cb79f, 2026-07-16)
- [x] 20260714-duplicate-bundle-id-silent Doppelte Bundle-IDs überschreiben sich still im Hashtable, Validator erkennt Kollision nicht (728b00d, 2026-07-16)
- [x] 20260714-archive-report-unknown-profile archive-report behandelt unbekanntes Profil still als leer, plausibel falscher Archivbericht (ddfab67, 2026-07-16)
- [x] 20260714-idea-validate-profile-fields Profilfelder inkl. `default_targets` und unbekannte Properties im Validator prüfen (09928ff, 2026-07-16)
- [x] 20260714-idea-server-helper-processgroups Server-Helper mit Prozessgruppen, geerbten Log-Streams und Prozesszustandsprüfung ausstatten (a487e5f, 2026-07-16)
- [x] 20260624-withserver-custom-dup-vendor with_server.py in skills/custom/web ist byte-identische Kopie des Vendor-Skripts (DRY/Drift, Kopie liegt außerhalb vendor-lock.json), zusammen mit den withserver-*-Einträgen betrachtet; validate.ps1 erzwingt jetzt per SHA-256-Hash-Check Byte-Gleichheit zwischen beiden Kopien (b6a2e97, 2026-07-16)
- [x] 20260624-withserver-custom-shell-true with_server.py (custom) startete den Server via subprocess Popen shell=True mit ungeprüftem --server-Kommando (Command-Injection-Muster) (a487e5f, 2026-07-16)
- [x] 20260624-setcontent-utf8-bom Set-Content -Encoding UTF8 schreibt ein BOM und verletzt die No-BOM-Policy; vendor-import.ps1 (UPSTREAM.md, vendor-lock.json) auf UTF8Encoding(false)-Helfer umgestellt, der Schreibpfad in update-vendor.ps1 entfiel bereits durch die unlocked-commit-Korrektur (09b0643, 2026-07-16)
- [x] 20260624-skillmd-frontmatter-schema Kein durchgesetztes SKILL.md-Frontmatter-Schema, validate.ps1 prüft nur Existenz/BOM statt Frontmatter-Struktur, mindestens für skills/custom nicht-leere description erzwungen (61012ec, 2026-07-16)

Codex-Work-Orders Welle B, Chunk 5 (`ai-router/logs/tmp/wo-codex-skillshub-5.out.md`), 2026-07-16:

- [x] 20260624-no-ci-validate-gate Kein CI-Gate, validate.ps1 lief nur manuell, GitHub-Actions-Workflow validiert jetzt bei jedem Pull Request auf windows-latest (2793ea5, 2026-07-16)
- [x] 20260714-idea-shouldprocess-dryrun `SupportsShouldProcess`/`-WhatIf` ersetzt die Ad-hoc-DryRun-Zweige in bootstrap-project.ps1 und sync.ps1, Staging-Kopieransatz aus 2692b22 bleibt erhalten (ab07328, 2026-07-16)
- [x] 20260714-idea-bootstrap-splatting-test Pester-Regressionstest für Bootstrap-Parameter-Splatting (mehrere `-BundleId`, benannte Sync-Parameter) ergänzt (88cca11, 2026-07-16)
- [x] 20260714-idea-pester-edge-tests Pester-Edge-Case-Suite für vendor-import-Exitcode, doppelte Bundle-IDs, unsichere Skill-Namen und with_server-Portkonflikt ergänzt (68a5fe0, 2026-07-16)
