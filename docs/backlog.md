---
status: wartung
track: infra
next_step: "Skills bei Bedarf pflegen, optional eine CI-Validierung ergänzen"
updated: 2026-09-06
---

# Backlog

Einzige Workflow-Wahrheit dieses Repos. Format/Regeln: siehe `../AGENTS.md`.
IDs `YYYYMMDD-slug`, nie renumbern. Ideen = offene Einträge mit `#idea`.

## Offen

- [ ] 20260904-upscale-tunnel-input-dir Der `LOCAL_HOSTS`-Guard in `upscale.py:25,121` erkennt einen Tunnel auf 127.0.0.1 nicht: zeigt `--url` dorthin und liegt ComfyUI woanders, landet die Kopie im lokalen Input-Ordner, der Server sieht sie nie und der Lauf endet nach 1200s im Timeout #bug (Quelle: docs/reviews/2026-09-04-cursor-verify.md, bestätigt 2026-09-06 mit Repro. Nicht gefixt, weil der Hostname die Information nicht trägt: die einzige belastbare Prüfung läuft über HTTP (Dateiliste via `/object_info/LoadImage` oder Upload statt Kopie), das ist eine Architekturentscheidung mit neuer Abhängigkeit von einer ComfyUI-Antwortform und ohne laufende Instanz nicht prüfbar. Optionen in docs/decisions.md, Eintrag 2026-09-06)

- [ ] 20260902-cursor-lesewelle Lesewelle 2026-09-02 (cursor-grok-4.6-high): 10 Test-Lücken, 6 Vereinfachungen, 6 Modul-Findings (0 high / 4 medium / 2 low), siehe docs/reviews/2026-09-02-cursor-lesewelle.md #note (Stand 2026-09-02: die Modul-Findings sind in der Wartungs-Session 5b behoben, siehe die 20260902-Einträge unter `## Erledigt`; 6 der 10 Test-Lücken sind mit `20260902-cursor-testgaps` geschlossen; offen bleiben die 6 Vereinfachungen und die 4 restlichen Test-Lücken, die kein ungetestetes Verhalten beschreiben, sondern Bugs: der Bundle-Parser verschluckt eine Flow-Liste `[a, b]` still, `Copy-Item` prüft die Registry-`path` nicht gegen die Repo-Grenze, `Convert-ToLocalRef` verwirft nur führende `..` und `Install-RepoSkills` überspringt ein vorhandenes Zielverzeichnis ohne `SKILL.md` statt es neu zu holen. Ein Test darauf wäre ohne Verhaltensänderung rot)

- [ ] 20260825-zweitmeinung-audit Zweitmeinungs-Audit 2026-08-25 (cursor-grok-4.6-high): 6 neue Findings (0 high / 5 medium / 1 low), siehe docs/reviews/2026-08-25-cursor-audit.md #note

- [ ] 20260824-reconcile Reconcile 2026-08-24 (gpt-5.6-sol): 10 von 25 Review-Findings offen, 15 behoben, siehe docs/reviews/2026-08-24-reconcile.md #note

Aus Codex-Audit 2026-07-14 (`docs/reviews/2026-07-14-codex.md`), am 2026-08-18 gegen den Code validiert (`docs/reviews/2026-08-18-reconcile.md`, Basis 4dcd9fd). Zwei der fünf damals bestätigt offenen Punkte sind inzwischen erledigt (seit 2026-09-02 in `archive/backlog-archive.md`), diese drei bleiben offen, Belege am Merge-Stand 2026-09-02 nachgezogen:

- [ ] 20260714-idea-atomic-sync Sync über temporäre Verzeichnisse, Validierung und atomaren Austausch implementieren #idea (mittel, Rest bestätigt 2026-09-02: Staging und atomarer Austausch sind da (`sync.ps1:78-101`, zwei Umbenennungen statt Löschen plus Verschieben, 633c2dd und fb163c6), offen bleibt allein die Validierung des Stagings, `sync.ps1:82-86` normalisiert nur die Kodierung der `SKILL.md`)
- [ ] 20260714-idea-real-yaml-parser Regex-YAML-Parser durch echten Parser plus Schema-Validierung ersetzen #idea (mittel, bestätigt 2026-09-02: `lib.ps1:96-133` (Bundles), `lib.ps1:185-210` (Registry) und `lib.ps1:222-248` (Archivplan) parsen weiter zeilenweise)
- [ ] 20260714-idea-transactional-vendor-import Vendor-Import als transaktionale, commit-genaue Pipeline mit Staging, Inhalts-Hashes und atomarem Lock-Update #idea (gross, Rest bestätigt 2026-09-02: gesperrter Commit und Exitcode-Prüfung sind da, es fehlen Staging, Inhalts-Hashes und der atomare Lock-Schreibvorgang in `vendor-import.ps1:56-58,84-86`)

Aus Code-Audit 2026-06-24 (`reviews/2026-06-24-code-audit.md`), recovered, am 2026-08-18 gegen den Code validiert (`docs/reviews/2026-08-18-reconcile.md`), beide bestätigt offen:

- [ ] 20260624-legacy-wrapper-bundles-sunset 8 Legacy-Wrapper-Bundles (`bundles/index.yaml:23-46`) delegieren via compose_with und verursachen Pflegeaufwand, Sunset-Plan sobald keine externen Referenzen mehr auf die alten IDs zeigen #idea (Quelle: reviews/2026-06-24-code-audit.md, korrigiert 2026-08-18: die core_skills sind nicht mehr leer, jeder Wrapper trägt genau einen Skill; die Sunset-Bedingung ist nicht erfüllt, `templates/project/.github/copilot-instructions.md:7,10` verweist noch auf `essentials` und `project-kickoff`)
- [ ] 20260624-vendor-notebooklm-robustness Geerbte Vendor-Robustheitsmängel in notebooklm-Skripten (bare except fängt KeyboardInterrupt/SystemExit, unvollständiges Playwright-Cleanup), geerbt (MIT), nicht selbst fixen, ggf. Upstream-Issue/PR #bug (Quelle: reviews/2026-06-24-code-audit.md, bestätigt 2026-08-18: `ask_question.py:96,132,153,180,186`, `browser_utils.py:75`, Cleanup nur der Page in `browser_session.py:77-80,224-231`)

## Erledigt

Ältere Einträge liegen in `archive/backlog-archive.md` (Archiv-Regel der AGENTS.md). Der Reconcile vom 2026-08-18 hat die damals hier stehenden Einträge stichprobenartig gegen den Code gehalten, alle geprüften sind tatsächlich umgesetzt (Belege in `docs/reviews/2026-08-18-reconcile.md`); inzwischen sind sie ins Archiv gewandert, ebenso die Security-Session und die Wartungs-Session 2026-09-01 (ausgelagert 2026-09-02).

Verify der Fix-Staffel 2026-09-02 (`docs/reviews/2026-09-04-cursor-verify.md`, cursor-grok-4.6-high, Lauf `20260904T072157-6da303` über das ai-router-Gate, Basis ee3120a): 4 Findings, alle vier am Code bestätigt, keines widerlegt. Drei behoben, jeder Fix mit Mutationsprobe im Commit-Text, das vierte offen als `20260904-upscale-tunnel-input-dir`:

- [x] 20260904-ledger-broken-utf8-line `cmd_find` übersprang eine halb geschriebene JSONL-Zeile nur dann, wenn `json.loads` sie ablehnte. `cmd_add` schreibt mit `ensure_ascii=False`, also endet ein abgebrochener add mitten in einem Multibyte-Zeichen und das Dekodieren wirft schon beim Iterieren der Datei, vor dem `try`; der Index starb weiter samt aller intakten Einträge darüber. Gelesen wird jetzt mit `errors="replace"`, die kaputte Zeile läuft in den vorhandenen Skip-Pfad (9f0cb6f, 2026-09-06)
- [x] 20260904-poll-error-not-only-oserror Die Poll-Schleife beider Skripte fing nur `OSError`, deckte also die Verbindung ab, nicht die Antwort: `api()` endet in `json.loads`, ein neustartendes ComfyUI oder ein Proxy davor liefert leeren Body oder HTML und die daraus entstehende `JSONDecodeError` beendete den Lauf sofort, genau im Fall, für den die Wiederholung gebaut war. Jetzt `(OSError, ValueError)`; ein dauerhafter HTTP-Fehler wird bewusst weiter wiederholt, steht aber jetzt in der Timeout-Meldung (f938366, 2026-09-06)
- [x] 20260904-upscale-staged-input-lost-on-abort `keep_staged` wurde nur im Timeout-Pfad gesetzt; jeder andere Ausgang aus der Poll-Schleife (Strg+C, unerwartete Ausnahme) löschte die Staging-Kopie, während der Job noch in der Queue stand: derselbe Datenverlust, den 820968f für den Timeout geschlossen hatte. Das Flag steht jetzt ab dem Queueing und fällt nur dort, wo der Job nachweislich vorbei ist (ddb3ad4, 2026-09-06)
- [x] 20260904-cursor-verify Verify-Lauf `20260904T072157-6da303` selbst: Report angelegt, alle 4 Findings am Code nachvollzogen (0 widerlegt), 3 behoben, 1 gebucht, 2 ADRs in decisions.md. Gates danach: `validate.ps1` PASS, `validate-skills.ps1` PASS, Pester 51 grün / 0 rot, `python -m unittest tests.test_gen_asset tests.test_with_server` 25 grün (35f567a, 2026-09-06)

Cursor-Testlücken 2026-09-02 (Lauf `20260902T154440-9e966d` über das ai-router-Gate, Branch cursor/testgaps auf Basis 08347c5; jeder neue Test einzeln gegen die im Kopf benannte Mutation geprüft, Proben im Commit-Text von c8f90c2):

- [x] 20260902-cursor-testgaps 6 der 10 Test-Lücken der Lesewelle geschlossen, kein Produktionscode angefasst. Neu: `tests/skills/lib.Tests.ps1` (compose_with-Rekursion plus Zyklus-Wächter in `Resolve-BundleSkills`) und `tests/skills/validate.Tests.ps1` (archive-reference außerhalb `skills/archive` sowie in der Core-Auflösung eines Profils). Erweitert: je ein Fall für `Copy-IfMissing`, den Profilzweig von sync.ps1, `-DryRun` und die Antigravity-Workflows. 5 Tests unverändert übernommen, 1 nachgearbeitet (der Antigravity-Fall fing seine eigene Mutation nicht, siehe decisions.md), 0 verworfen. Danach 51 grün / 0 rot, `validate.ps1` PASS, pytest 21 grün (4155fa7, 2026-09-02)

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

## Verworfen

(keine)
