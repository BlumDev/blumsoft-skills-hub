# Reconcile blumsoft-skills-hub (2026-08-18)

Abgleich der offenen Backlog-Punkte und der Findings aus `docs/reviews/` gegen den Code auf `main` (Stand `4dcd9fd`). Es wurde kein Produktivcode geändert.

Prüfumgebung: Linux-Container ohne PowerShell. `validate.ps1` und die Pester-Suiten konnten deshalb nicht ausgeführt werden, alle Aussagen unten stammen aus dem Lesen des Codes mit Datei und Zeile als Beleg. Wo die Codelektüre allein nicht ausreicht, steht das ausdrücklich dabei.

Ergebnis in Zahlen: 7 offene Punkte geprüft, davon 7 weiterhin offen (2 mit deutlich verkleinertem Rest), 0 nachweislich erledigt, 0 hinfällig. Zusätzlich wurden die 22 Einträge unter `## Erledigt` stichprobenartig gegen den Code gehalten, alle geprüften sind tatsächlich umgesetzt.

## 1. Nachweislich noch offen

### 20260714-sync-remove-path-traversal (#bug, high)

Offen. `scripts/skills/sync.ps1:72` löscht das Ziel weiterhin mit `Remove-Item -Path $dstPath -Recurse -Force`, also mit Wildcard-Auflösung statt `-LiteralPath`. `$dstPath` entsteht in `scripts/skills/sync.ps1:59` aus `Join-Path $targetDir $skill`, der Skillname kommt ungeprüft aus Bundle und Registry (`scripts/skills/lib.ps1:76` und `scripts/skills/lib.ps1:144`). Eine Namensprüfung gibt es an keiner Stelle, eine Suche nach Allowlist-Mustern über `scripts/` bleibt leer.

Teilentschärft ist der Punkt durch die Staging-Kopie aus `2692b22`: `scripts/skills/sync.ps1:63` legt zuerst ein temporäres Verzeichnis an und erst `scripts/skills/sync.ps1:72` löscht das Ziel. Bei den beiden Namen aus dem Regressionstest (`tests/skills/tooling-edge.Tests.ps1:7-10`) scheitert damit voraussichtlich schon das `Copy-Item` in `scripts/skills/sync.ps1:65`, weil der Staging-Name `.*.sync-<guid>` unter Windows ein unzulässiges Zeichen enthält beziehungsweise der Name `.../outside.sync-<guid>` in ein nicht existierendes Elternverzeichnis zeigt. Der Schutz kommt in diesen zwei Fällen also aus den Windows-Pfadregeln, nicht aus einer Prüfung im Skript. Ob der Test `tests/skills/tooling-edge.Tests.ps1:94` heute grün ist, ist hier nicht überprüfbar (kein PowerShell), an der Bewertung des Findings ändert das nichts: die auflösende `Remove-Item`-Stelle steht unverändert im Code.

### 20260714-idea-id-allowlist-literalpath (#idea, quick-win)

Offen. Weder Skill- noch Bundle-IDs werden gegen eine Allowlist geprüft und `-LiteralPath` wird nur punktuell verwendet. Ohne `-LiteralPath` arbeiten weiterhin `scripts/skills/sync.ps1:58`, `scripts/skills/sync.ps1:62`, `scripts/skills/sync.ps1:65`, `scripts/skills/sync.ps1:72`, `scripts/skills/vendor-import.ps1:52`, `scripts/skills/vendor-import.ps1:56` sowie `scripts/project/bootstrap-project.ps1:30-31`. Umgestellt sind bisher nur die Staging-Pfade (`scripts/skills/sync.ps1:73` und `scripts/skills/sync.ps1:75`) und die Prüfungen in `scripts/skills/validate.ps1:154-158`.

### 20260714-idea-atomic-sync (#idea, mittel)

Offen, Rest deutlich kleiner als beim Aufnehmen des Punktes. Das temporäre Verzeichnis samt Austausch existiert seit `2692b22` (`scripts/skills/sync.ps1:63-76`). Zwei Teile der Idee fehlen: der Austausch ist ein Löschen mit anschließendem Verschieben (`scripts/skills/sync.ps1:72-73`), zwischen beiden Schritten ist der Skill kurz gar nicht installiert. Eine Validierung des Stagings findet nicht statt, `scripts/skills/sync.ps1:66-70` normalisiert nur die Kodierung der `SKILL.md`.

### 20260714-idea-real-yaml-parser (#idea, mittel)

Offen. `scripts/skills/lib.ps1` parst weiterhin zeilenweise per Regex, an drei Stellen: Bundles in `scripts/skills/lib.ps1:60-80`, Registry in `scripts/skills/lib.ps1:140-154`, Archivplan in `scripts/skills/lib.ps1:177-191`. Verschachtelte Maps, Inline-Listen, Block-Skalare und Kommentare am Zeilenende fallen unverändert still durch. Eine Schema-Validierung existiert nur für Profile (`scripts/skills/validate.ps1:196-206`), nicht für die YAML-Dateien selbst.

### 20260714-idea-transactional-vendor-import (#idea, gross)

Offen, Rest kleiner. Umgesetzt sind der gesperrte Commit (`scripts/skills/vendor-import.ps1:16-20` und `scripts/skills/vendor-import.ps1:58`), die Exitcode-Prüfung des Installers (`scripts/skills/vendor-import.ps1:59`) und die korrekte Provenienz nur für tatsächlich neu importierte Skills (`scripts/skills/vendor-import.ps1:28-32` und `scripts/skills/vendor-import.ps1:65-66`). Es fehlen weiterhin das Staging-Verzeichnis, die Inhalts-Hashes je Skill und das atomare Lock-Update: `scripts/skills/vendor-import.ps1:56-58` installiert direkt in das Zielverzeichnis, `scripts/skills/vendor-import.ps1:84-86` schreibt `vendor-lock.json` ohne Zwischendatei.

### 20260624-legacy-wrapper-bundles-sunset (#idea)

Offen, Beschreibung war in einem Punkt überholt und ist im Backlog nachgezogen. Die acht Wrapper stehen weiter in `bundles/index.yaml:23-46`, `README.md:131-143` nennt sieben aktive Bundles plus Legacy-IDs. Anders als im Audit von 2026-06-24 beschrieben sind die `core_skills` nicht mehr leer, jeder Wrapper trägt heute genau einen Skill (etwa `bundles/essentials.yaml:8-9` und `bundles/web-wizard.yaml:6-7`), erzwungen durch `scripts/skills/validate.ps1:59`. Die im Punkt genannte Sunset-Bedingung ist nachweislich nicht erfüllt: `templates/project/.github/copilot-instructions.md:7` verweist auf `essentials` und `templates/project/.github/copilot-instructions.md:10` auf `project-kickoff`.

### 20260624-vendor-notebooklm-robustness (#bug)

Offen und bewusst nicht selbst zu beheben (Vendor-Code, MIT, gepinnt). Belege unverändert vorhanden: `except:` ohne Typ in `skills/vendor/guanyang/notebooklm/scripts/ask_question.py:96`, `:132`, `:153`, `:180`, `:186` sowie `skills/vendor/guanyang/notebooklm/scripts/browser_utils.py:75`. Das Cleanup schließt weiterhin nur die Page, nicht Context oder Browser: `skills/vendor/guanyang/notebooklm/scripts/browser_session.py:77-80` und `skills/vendor/guanyang/notebooklm/scripts/browser_session.py:224-231`. Nächster sinnvoller Schritt bleibt ein Upstream-Issue, nicht ein lokaler Fix.

## 2. Nachweislich erledigt

Keine Neubewertung: kein bisher offener Punkt hat sich als bereits erledigt herausgestellt. Die Stichprobe über `## Erledigt` bestätigt dagegen die dort eingetragenen Punkte, unter anderem:

- `20260714-github-calls-no-timeout`: `scripts/skills/lib.ps1:197-211` mit `-TimeoutSec 30`, optionalem `GITHUB_TOKEN` und verständlicher Fehlermeldung.
- `20260714-vendor-import-hardcoded-user`: `scripts/skills/vendor-import.ps1:22-26` löst über `$HOME`, `USERPROFILE` und `CODEX_HOME` auf.
- `20260624-no-ci-validate-gate`: `.github/workflows/validate.yml` führt `validate.ps1` bei jedem Pull Request auf `windows-latest` aus.
- `20260624-withserver-custom-dup-vendor`: beide Kopien sind byte-identisch (`diff` ohne Ausgabe), abgesichert per SHA-256-Vergleich in `scripts/skills/validate.ps1:152-160`.
- `20260624-withserver-custom-shell-true`: Standardpfad ohne Shell über `shlex.split` (`skills/custom/web/scripts/with_server.py:27-31`), `shell=True` nur noch über den ausdrücklichen Operator-Schalter (`skills/custom/web/scripts/with_server.py:34-37` und `:133-137`).
- `20260624-setcontent-utf8-bom`: `Write-FileUtf8NoBom` in `scripts/skills/lib.ps1:42-46`, genutzt in `scripts/skills/vendor-import.ps1:79` und `:86`.
- `20260624-skillmd-frontmatter-schema`: nicht-leere `description` für `skills/custom` erzwungen (`scripts/skills/validate.ps1:5-34` und `:129-140`).
- `20260714-sync-default-targets-ignored`: `scripts/skills/sync.ps1:29` liest `default_targets` aus dem Profil.
- `20260714-duplicate-bundle-id-silent`: `scripts/skills/lib.ps1:93` wirft bei doppelter Bundle-ID.
- `20260714-archive-report-unknown-profile`: `scripts/skills/archive-report.ps1:17` wirft bei unbekanntem Profil.
- `20260714-refreshlock-stale-content`: `scripts/skills/update-vendor.ps1:7-9` deaktiviert `-RefreshLock` ohne echten Re-Import.
- `20260714-idea-shouldprocess-dryrun`: `SupportsShouldProcess` in `scripts/skills/sync.ps1:1` und `scripts/project/bootstrap-project.ps1:1`, Entscheidungspunkte in `scripts/skills/sync.ps1:60` und `scripts/project/bootstrap-project.ps1:28`.
- `20260714-bootstrap-splat-positional`: benanntes Hashtable-Splatting in `scripts/project/bootstrap-project.ps1:43-61`.

## 3. Hinfällig

Keiner. Alle sieben offenen Punkte beschreiben Code, der weiterhin existiert, sowie ein Ziel, das weiterhin gilt.

## 4. Beobachtung am Rand (nicht triagiert, kein Backlog-Eintrag)

Sieben der acht Tooling-Skripte beginnen mit einem UTF-8-BOM: `scripts/skills/lib.ps1`, `resolve-bundle.ps1`, `setup-from-profile.ps1`, `sync.ps1`, `update-vendor.ps1`, `validate.ps1`, `vendor-import.ps1`. Die durchgesetzte No-BOM-Regel gilt heute nur für `SKILL.md` (`scripts/skills/validate.ps1:142-150`), insofern liegt kein Regelverstoß vor. Ob die Regel auf die eigenen Skripte ausgedehnt werden soll, ist eine offene Frage an den Maintainer und hier bewusst nicht entschieden.
