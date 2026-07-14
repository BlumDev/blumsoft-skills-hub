# Code-Audit blumsoft-skills-hub (2026-06-24)

REPORT-ONLY. Keine Code-Aenderungen vorgenommen. Branch: `audit-2026-06-24`.

## Kontext und Scope

Das Repo ist ein "Skills Hub": eine Bibliothek von Agent-Skills (je Skill ein
Ordner mit `SKILL.md`), die kuratiert in verschiedene Targets (Claude, Codex,
Cursor, Antigravity, VS Code/Copilot) synchronisiert wird. Trotz `package.json`
ist es kein Node-Projekt: die einzige eigene Programmlogik liegt in
`scripts/skills/*.ps1` und `scripts/project/bootstrap-project.ps1` (781 Zeilen
PowerShell). Der Rest sind 366 Markdown-Skills, Konfigs (YAML/JSON) und in
einzelne Skills eingebettete Hilfsskripte (Python/Shell/JS).

Drei klar zu trennende Code-Populationen, mit unterschiedlicher Verantwortung:

| Population | Pfad | Verantwortung | Audit-Gewicht |
|---|---|---|---|
| Eigenes Tooling | `scripts/skills/*`, `scripts/project/*` | Maintainer | hoch |
| Eigene Skills | `skills/custom/*` | Maintainer | hoch |
| Vendor-Skills | `skills/vendor/{guanyang,sickn33}/*` | importiert, MIT, via `vendor-lock.json` gepinnt | niedrig (geerbt) |
| Archiv / Tests | `skills/archive/*`, `tests/skill-eval/fixture/*` | Maintainer | Tests bewusst "vulnerable" |

Wichtig fuer die Bewertung: `tests/skill-eval/fixture/src/*.py` enthaelt
absichtlich verwundbaren Code (eval, os.system, Hardcoded-Secrets, SQL-Injection)
als Test-Fixture fuer die `code-audit`- und `ai-hardening`-Skills. Das sind
**keine** Findings (siehe `docs/skills-qa-log.md`, `tests/skill-eval/answer-key.md`).

`validate.ps1` laeuft sauber durch (15 Bundles, 77 Registry-Skills, Archive-Plan
konsistent). Die Datenkonsistenz des Hubs (Registry, Bundles, Profiles,
Archive-Plan) ist also intakt.

---

## Findings nach Schwere

### HIGH

#### H1 - Eigener Code dupliziert Vendor-Skript byte-identisch (DRY)
`skills/custom/web/scripts/with_server.py` ist eine **byte-fuer-byte identische
Kopie** von `skills/vendor/guanyang/webapp-testing/scripts/with_server.py`
(per `diff` verifiziert). Damit existiert maintainer-eigener Code, der eine
1:1-Kopie von gepinntem Vendor-Code ist. Folgen: Bugfixes/Sicherheitsfixes im
Vendor-Upstream propagieren nicht; die Custom-Kopie driftet beim naechsten
`vendor-import` lautlos auseinander, ohne dass `vendor-lock.json` das erfasst
(die Kopie liegt ausserhalb des Vendor-Trackings).

Beispiel: `skills/custom/web/scripts/with_server.py` vs.
`skills/vendor/guanyang/webapp-testing/scripts/with_server.py`.

Bewertung: HIGH, weil es ein eigentlich vermeidbares Wartungs-/Sicherheitsrisiko
im eigenen Verantwortungsbereich ist (nicht "geerbt").

#### H2 - `shell=True` mit CLI-steuerbarem Kommando im eigenen Skill
`skills/custom/web/scripts/with_server.py` startet den Server via
`subprocess.Popen(server['cmd'], shell=True)`, wobei `server['cmd']` direkt aus
dem `--server`-CLI-Argument stammt (ohne `shlex.split`, ohne Allowlist). Bei
einem lokalen Dev-Helper, der nur vom Maintainer mit eigenen Kommandos
aufgerufen wird, ist der reale Angriffsvektor begrenzt (kein fremder Input),
aber das Muster ist riskant, sobald das Kommando aus einer Konfig/Agent-Eingabe
gespeist wird. Gleiches Muster im Vendor-Pendant (geerbt, niedriger).

Beispiel: `skills/custom/web/scripts/with_server.py` (Popen mit `shell=True`).

Hinweis: Da H1 und H2 dieselbe Datei betreffen, loest "Custom-Kopie entfernen
und auf den Vendor-Pfad verweisen" beide auf einmal (siehe Quick Win 1).

### MEDIUM

#### M1 - `Set-Content -Encoding UTF8` schreibt BOM und verletzt die eigene Policy
Das Repo erzwingt UTF-8 **ohne** BOM fuer `SKILL.md` (geprueft in `validate.ps1`,
repariert in `fix-encoding.ps1` / `Convert-FileToUtf8NoBom`). Drei Schreibstellen
nutzen aber `Set-Content -Encoding UTF8`, das unter Windows PowerShell 5.1 ein
BOM voranstellt:
- `scripts/skills/vendor-import.ps1:54` (UPSTREAM.md)
- `scripts/skills/vendor-import.ps1:67` (vendor-lock.json)
- `scripts/skills/update-vendor.ps1:26` (vendor-lock.json)

Inkonsistent zur eigenen No-BOM-Regel und zu `CLAUDE.md` (UTF-8 ohne BOM via
`UTF8Encoding($false)`). Betrifft generierte Dateien, nicht die geprueften
SKILL.md, daher MEDIUM.

#### M2 - Heterogene SKILL.md-Frontmatter ueber die Skill-Populationen
Kein durchgesetztes Frontmatter-Schema. `skills/custom/*` ist konsistent
(`name`, `description`), die Vendor-Skills streuen stark ueber Zusatzfelder
(`metadata`, `allowed-tools`, `license`, `source`, `version`, `category`,
`hooks` u.a.). `validate.ps1` prueft nur Existenz/BOM von `SKILL.md`, nicht die
Frontmatter-Struktur. Beispiele:
- `skills/archive/guanyang/planning-with-files/SKILL.md` (viele Zusatzfelder,
  inkl. Hook-Definitionen)
- diverse `skills/vendor/sickn33/*/SKILL.md` mit teils abgeschnittenen/leeren
  `description`-Werten

Da Vendor-Frontmatter geerbt ist (Upstream-Verantwortung), MEDIUM. Eigene
Empfehlung: Schema dokumentieren und im Validator zumindest fuer `skills/custom`
einen nicht-leeren `description` erzwingen.

#### M3 - Handgerollter YAML-Parser fuer Bundles/Registry/Archive-Plan
`scripts/skills/lib.ps1` parst YAML zeilenweise per Regex
(`Get-BundleFromFile`, `Get-RegistryEntries`, `Get-ArchivePlanEntries`). Das
funktioniert nur fuer die heutige, flache Struktur und bricht still bei
legitimem YAML (verschachtelte Maps, Inline-Listen `[a, b]`, Block-Skalare `>`/
`|`, Kommentare am Zeilenende, Quoting mit Sonderzeichen). Bewusste
Vereinfachung, aber fragil: ein Skill-Autor, der gueltiges YAML schreibt, kann
die Validierung lautlos umgehen. MEDIUM (Robustheit), kein akuter Bug, da die
aktuellen Dateien dem Subset folgen.

#### M4 - `Invoke-RestMethod` gegen GitHub-API ohne Timeout, Auth und Fehlerbehandlung
`Get-RepoHeadCommit` in `scripts/skills/lib.ps1:190-196` ruft die GitHub-API
unauthenticated (60 req/h Rate-Limit, schnell erschoepft), ohne `-TimeoutSec`
und ohne Abfangen von Fehlern. Genutzt von `vendor-import.ps1` und
`update-vendor.ps1`. Bei Rate-Limit/Netzwerkfehler bricht der Import mit roher
Exception ab (durch `$ErrorActionPreference = "Stop"`), statt verstaendlich zu
melden. MEDIUM (Robustheit der Vendor-Pipeline).

#### M5 - Keine CI: `validate.ps1` laeuft nur manuell
`.github/` enthaelt keinen Workflow (nur `skills/`, der gitignored ist). Die
einzige Konsistenz-/Encoding-Pruefung haengt davon ab, dass jemand lokal
`validate.ps1` ausfuehrt. Fuer ein Repo, dessen Kernwert die Konsistenz von
Registry/Bundles/Profiles ist, faellt damit das Sicherheitsnetz gegen Drift weg.
MEDIUM.

### LOW

#### L1 - Hartkodierter maschinenspezifischer Pfad
`scripts/skills/vendor-import.ps1:12` haelt den Installer-Pfad fest auf
`C:\Users\Marcus\.codex\skills\.system\...`. Bricht auf jeder anderen Maschine /
unter anderem User. Sollte ueber `$HOME`/Parameter aufgeloest werden. LOW, da
reines Maintainer-Tooling.

#### L2 - Legacy-Wrapper-Bundles erhoehen die Konfig-Flaeche
`bundles/index.yaml` listet 15 Bundles, README nennt aber nur 7 als "aktiv". Die
8 Legacy-Wrapper (`essentials`, `web-wizard`, `security-engineer`,
`startup-growth`, `data-ai`, `devops-cloud`, `workflow-ops`, `project-kickoff`)
haben leere `core_skills` und delegieren nur via `compose_with`. Bewusst fuer
Rueckwaertskompatibilitaet gehalten, aber jeder muss weiter alle Pflicht-Felder
(name/goal/recommended_start_skill/starter_prompt) tragen, sonst schlaegt
`validate.ps1` fehl: dauerhafter Pflegeaufwand fuer totes Gewicht. LOW. Aufraeumen,
sobald keine externen Referenzen mehr auf die alten IDs zeigen.

#### L3 - Geerbte Vendor-Robustheitsmaengel (notebooklm-Skripte)
In `skills/vendor/guanyang/notebooklm/scripts/*` mehrere `except:` ohne Typ
(fangen auch KeyboardInterrupt/SystemExit) und unvollstaendiges Playwright-
Cleanup (`close()` schliesst nur die Page, nicht Context/Browser; Fehler werden
geschluckt). Beispiele:
`skills/vendor/guanyang/notebooklm/scripts/ask_question.py` (bare `except`),
`.../browser_session.py` (Cleanup). Geerbt (MIT), daher LOW: nicht selbst fixen,
ggf. Upstream-Issue/PR.

---

## Quick Wins (priorisiert)

1. **Custom-`with_server.py` entfernen (loest H1 + H2 auf einmal).** Die Datei
   ist eine exakte Kopie des Vendor-Skripts. Wenn der `web`-Skill das Skript
   braucht, sollte er auf den gepinnten Vendor-Pfad verweisen statt eine eigene
   Kopie zu halten. Damit verschwindet sowohl die Duplikation als auch der
   eigenverantwortliche `shell=True`-Pfad. Aufwand: niedrig. Wirkung: hoch.

2. **No-BOM beim Schreiben erzwingen (M1).** Die drei `Set-Content -Encoding
   UTF8`-Stellen auf den vorhandenen Helfer umstellen, der UTF-8 ohne BOM
   schreibt (Muster wie `Convert-FileToUtf8NoBom` / `UTF8Encoding($false)` in
   `lib.ps1`). Beseitigt den Widerspruch zur eigenen Policy an der Wurzel.
   Aufwand: sehr niedrig.

3. **Minimaler CI-Gate (M5).** Einen GitHub-Actions-Workflow ergaenzen, der bei
   PR `pwsh ./scripts/skills/validate.ps1` ausfuehrt. Re-nutzt vorhandenes
   Tooling (set-and-forget), kein neues Tool, und macht Registry-/Encoding-Drift
   sofort sichtbar. Aufwand: niedrig.

## Moegliche Vereinheitlichungs-/DRY-Massnahmen (mittelfristig)

- **Frontmatter-Schema (M2):** Ein dokumentiertes Pflicht-Set (`name`,
  `description`) plus optionale Felder definieren und im Validator zumindest fuer
  `skills/custom` einen nicht-leeren `description` pruefen. Stoppt Drift bei
  neuen eigenen Skills, ohne Vendor-Importe zu blockieren.
- **YAML-Parsing (M3):** Mittelfristig auf einen echten YAML-Parser umstellen
  (z.B. via `pwsh`-Modul oder Konvertierung), damit gueltiges YAML nicht still
  durchfaellt. Alternativ: das erlaubte Subset explizit dokumentieren und im
  Validator harte Fehler werfen, wenn nicht unterstuetzte Konstrukte auftauchen.
- **Vendor-API-Haertung (M4):** `Get-RepoHeadCommit` mit `-TimeoutSec`, optional
  Token (`GITHUB_TOKEN` per Name, nie geloggt) und verstaendlicher
  Rate-Limit-Fehlermeldung versehen.
- **Legacy-Bundles (L2):** Sunset-Plan fuer die 8 Wrapper-Bundles, sobald keine
  externen Referenzen mehr bestehen, um die Konfig-Flaeche zu verkleinern.
