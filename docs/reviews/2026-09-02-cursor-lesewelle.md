# Lesewelle 2026-09-02 (cursor-grok-4.6-high)

Basis: main, Kurz-SHA 08347c5.

## Testgaps (Run-ID 20260902T115800-f96d01)

Vorhandene Tests decken vor allem **bereits gebrochene Pfade** ab, nicht die Default-Pipeline.

**Pester:** `Test-SkillId` / `Assert-SkillId` / `Resolve-SkillTargetPath` (Allowlist, Traversal); `sync.ps1` lehnt unsichere Namen ab und löscht nichts außerhalb; Ziel-Dedup `codex`/`vscode-chatgpt`; Replace-Fehler und Abbruch zwischen den Renames lassen die alte Installation stehen; `setup-from-profile.ps1` ohne `-Apply` überspringt `vendor-import`; `Install-RepoSkills` wirft bei Installer-Exit ≠ 0; `Get-AllBundles` bei doppelter Bundle-ID; `bootstrap-project.ps1` splattet `-BundleId` an einen Sync-Stub.

**Python:** `comfy_generate.inject` nur Seed/Steps; `execution_error` in beiden Comfy-Skripten; Poll-Abbruch bei `status=error`; Upscale-Inputnamen, keine Kollision, Cleanup; `with_server.is_server_ready` nur wenn der eigene Prozess schon tot ist und ein Fremd-Listener den Port hält.

**Nicht in der Suite:** `Resolve-BundleSkills`, Profil-Sync, `-DryRun` am echten `sync.ps1`, Registry-`path`, Antigravity-Workflows, `validate.ps1`-Fehlerklassen, `validate-skills.ps1`, Vendor-Skip nach Teilimport, `Copy-IfMissing`. CI führt nur `validate.ps1` gegen das gesunde Repo aus (Happy-Path), nicht Pester/unittest.

1. `scripts/skills/lib.ps1:Resolve-BundleSkills` | Kernfeature: bestimmt die Skillmenge für Sync, Validate und Profile; Fehler in `compose_with` oder `-IncludeExtended` installiert zu viel oder zu wenig in die globalen Skill-Ordner | `Resolve-BundleSkills_compose_with_and_extended`: Mini-Bundles A `compose_with` B, B.core=`x,y`, A.core=`z`, A.extended=`e`; ohne Flag `@(x,y,z)`, mit Flag `@(x,y,z,e)`; Zyklus A↔B terminiert ohne Throw | klein
2. `scripts/skills/lib.ps1:Get-BundleFromFile` | Korrektheit: der Zeilen-YAML-Parser speist Validate und Sync; eine Flow-Liste (`core_skills: [a, b]`) wird still als leer gelesen, das Bundle verliert seine Skills | `Get-BundleFromFile_flow_list_not_silently_empty`: YAML mit `core_skills: [engineering, web]`; Assertion: beide IDs in `core_skills` oder Throw, nicht Count 0 | klein
3. `scripts/skills/sync.ps1` (Profilzweig, Laden von `profiles/*.json`) | Kernfeature: der dokumentierte Default `sync.ps1 -Profile freelancer-fullstack` setzt `bundle_ids`, `default_targets` und `include_extended`; alle Sync-Tests übergeben `-BundleId` und umgehen das | `sync_profile_drives_bundles_and_targets`: Fixture-Profil `bundle_ids=[only]`, `default_targets=[codex]`, `include_extended=false`; Aufruf nur `-Profile`; Assertion: Skill nur unter FakeHome `\.codex\skills`, nicht unter `\.cursor\skills` | mittel
4. `scripts/skills/sync.ps1` (ShouldProcess/`-DryRun`) | Datenverlust: Preview darf installierte Skills nicht anfassen; getestet ist nur, dass der Setup-Stub das Flag sieht, nicht der echte Copy/Rename | `sync_dryrun_leaves_installed_skill_untouched`: vorhandene Installation plus geänderte Quelle, `sync.ps1 -BundleId only -Targets codex -DryRun`; Exit 0, Ziel-`SKILL.md` unverändert, kein `.*.sync-*` Staging-Ordner | klein
5. `scripts/skills/sync.ps1` (Copy-Item von `registry.path`) | Security: Skill-IDs sind allowlisted, der Registry-`path` nicht; `path: ../outside` kopiert fremde Bäume nach `~/.codex/skills` | `sync_rejects_registry_path_outside_repo`: Eintrag `name=harmless`, `path=../outside` mit Canary außerhalb des Fixture-Repos; Throw vor dem Copy, Canary unangetastet, Ziel ohne fremden Inhalt | mittel
6. `scripts/skills/sync.ps1` (`-SyncAntigravityWorkflows`) | Datenverlust: Quickstart kopiert `*.md` per `Copy-Item -Force` nach `~/.gemini/antigravity/global_workflows` ohne Staging/Backup (anders als der Skill-Swap) | `sync_antigravity_dryrun_does_not_overwrite_workflows`: FakeHome-Datei `workflow-ops.md` mit `user-edit`; `-DryRun -SyncAntigravityWorkflows` lässt den Text stehen; Lauf ohne DryRun schreibt die Repo-Fassung | mittel
7. `scripts/skills/validate.ps1` (Archive-Pfad- und Profil-Checks) | Korrektheit: einziges CI-Gate; nur Happy-Path gegen das echte Repo, die Fehlerklassen (active unter `skills/archive`, Profil zieht `archive-reference`) sind ungetestet | `validate_fails_on_archive_mismatch_and_profile_leak`: Mini-Repo, Skill `status=archive-reference` aber `path=skills/custom/x`, Profil-Core enthält denselben Skill; Exit 1, Ausgabe enthält `must live under skills/archive` und `includes archive-reference skill` | mittel
8. `scripts/skills/validate-skills.ps1:Convert-ToLocalRef` | Korrektheit: Content-Gate; `references/../../scripts/foo` gilt als lokale Ref, `Test-Path` folgt aus dem Skill heraus, kaputte oder ausbrechende Links bleiben grün | `Convert-ToLocalRef_rejects_parent_escape`: Raw=`references/../../scripts/skills/sync.ps1`, Subdirs=`references`; Rückgabe `$null`; fehlende `references/missing.md` in `Get-LocalFileRefs` wird zum ERROR | klein
9. `scripts/skills/vendor-import.ps1:Install-RepoSkills` | Korrektheit/Datenverlust: existiert der Dest-Ordner, wird der Skill übersprungen; nach Teilfehler (Installer legt Ordner an, dann Exit ≠ 0) bleibt ein halber Vendor-Tree ohne `UPSTREAM.md`, Retry holt ihn nicht, `vendor-lock.json` kann trotzdem `generated_at` schreiben | `Install-RepoSkills_retries_incomplete_dest`: `DestPath/example` existiert ohne `SKILL.md`; zweiter Lauf muss den Installer für `example` erneut aufrufen oder Throw `incomplete`; `vendor-lock.json` danach nicht als Erfolg überschrieben | mittel
10. `scripts/project/bootstrap-project.ps1:Copy-IfMissing` | Datenverlust: Bootstrap verspricht, vorhandene Projektdateien nicht zu überschreiben; der einzige Test prüft nur Sync-Parameter-Splatting | `Copy-IfMissing_keeps_existing_decisions`: Ziel-`DECISIONS.md` mit `keep-me`, Template anders, Sync-Stub; nach Bootstrap bleibt `keep-me`, fehlendes `PROJECT_CONTEXT.md` wird angelegt | klein

## Simplify (Run-ID 20260902T120245-9d64fb)

1. Acht Legacy-Wrapper (`bundles/essentials.yaml:11`, `web-wizard.yaml:10`, `security-engineer.yaml:10`, `startup-growth.yaml:10`, `data-ai.yaml:10`, `devops-cloud.yaml:10`, `workflow-ops.yaml:10`, `project-kickoff.yaml:10`) plus `bundles/index.yaml:23-46`, acht `bundles/prompts/*.md` und acht `adapters/antigravity/global_workflows/*.md` sind Aliase auf die sieben aktiven Bundles; die Adapter und das Default-`sync.ps1 -SyncAntigravityWorkflows` (`sync.ps1:130-144`, `README.md:42`) laufen nur unter den alten IDs, die Prompts driftieren (z. B. `bundles/prompts/essentials.md:4-8` listet Vendor-Skills, die `bundles/engineering-core.yaml:8-11` nicht enthält) — Schnitt: Template `templates/project/.github/copilot-instructions.md:7,10` auf `engineering-core`/`project-bootstrap-core` umstellen, Wrapper-YAMLs, Wrapper-Prompts und Legacy-Adapter löschen — Risiko: Aufrufe mit `-BundleId essentials` und bereits installierte Antigravity-Workflows unter den alten Dateinamen.

2. `skills/custom/web/scripts/with_server.py` ist eine erzwungene Byte-Kopie von `skills/vendor/guanyang/webapp-testing/scripts/with_server.py` (`validate.ps1:152-159`), Tests laden beide (`tests/test_with_server.py:10-12`, `tests/skills/tooling-edge.Tests.ps1:11-14`); `webapp-testing` ist `inactive` (`skills/archive-plan.yaml:129-131`) und fehlt im Default-Profil, `web` ruft lokal `python scripts/with_server.py` auf (`skills/custom/web/references/testing.md:4,10`) — Schnitt: Custom-Kopie und Hash-Check streichen, `webapp-testing` in `web-product` core aufnehmen (oder den Aufruf in der `web`-Doku auf diesen Skill umbiegen) — Risiko: nach Sync hat der Ordner `web` kein `scripts/with_server.py` mehr, solange die Doku den relativen Pfad behält.

3. `skills/archive-plan.yaml` ist ein 1:1-Spiegel von `skills/registry.yaml` (Name plus `status`/`target`), `validate.ps1:90-95` erzwingt die Bijektion, Parser `lib.ps1:222-248` ist eine dritte Kopie der Zeilen-YAML-Schleife neben `lib.ps1:96-133` und `lib.ps1:185-210` — Schnitt: `status` und `target` in die Registry-Einträge legen, `archive-plan.yaml` und `Get-ArchivePlanEntries` löschen, `archive-report.ps1:12-19` auf die Registry umstellen — Risiko: Status-Pfad-Regeln in `validate.ps1:96-106` müssen mitwandern, sonst rutscht ein `archive-reference` wieder unter `skills/vendor/` oder umgekehrt.

4. `comfy_generate.py` und `upscale.py` duplizieren denselben Comfy-Client: `api` (`comfy_generate.py:27-37` / `upscale.py:28-38`), `download` (`:40-53` / `:41-51`), `execution_error` (`:77-95` / `:65-83`) und die History-Poll-Schleife (`:185-206` / `:138-159`); `tests/test_gen_asset.py:119-147` prüft beide Kopien extra — Schnitt: eine gemeinsame `comfy_client.py`, beide Skripte importieren — Risiko: Default-Timeouts unterscheiden sich (600 vs 900), ein gemeinsames Poll könnte ein Skript härter oder weicher machen als heute.

5. Zwei Frontmatter-Parser tun dieselbe Arbeit: `Get-FrontmatterDescription` in `validate.ps1:5-35` (nur Custom-`description`, genutzt `:129-139`) und `Parse-Frontmatter` in `validate-skills.ps1:32-83` (Name, Description, Block-Skalare für alle `SKILL.md`); CI führt nur `./scripts/skills/validate.ps1` aus (`.github/workflows/validate.yml:17`) — Schnitt: einen Parser nach `lib.ps1`, `validate.ps1` ruft die Skill-Checks mit auf, `validate-skills.ps1` entfällt — Risiko: Vendor-/Archiv-`SKILL.md` ohne `name`/`description` oder mit toten Referenzpfaden würden das einzige CI-Gate rot färben, das sie bisher nicht sieht.

6. `Get-AllBundles` lädt Bundles nur über das Dateisystem und überspringt `index.yaml`/`schema.yaml` (`lib.ps1:140`); `validate.ps1:43-51` prüft den Index nur in eine Richtung (Index-ID muss als Datei existieren, nicht umgekehrt), `bundles/schema.yaml:1-11` wird nirgends geparst und lässt `recommended_start_skill`/`fallback_skills` weg, die `lib.ps1:99-102` und `validate.ps1:57-58` verlangen — Schnitt: `index.yaml`, die Index-Prüfung und `schema.yaml` löschen, die Bundle-YAMLs bleiben die einzige Quelle — Risiko: Docs/Reviews, die Bundle-Listen über `index.yaml`-Zeilen zitieren, zeigen ins Leere.

## Modul-Audit: skills/ (Run-ID 20260902T120354-6c2ba7)

Bekannte Punkte aus Reviews/Backlog (with_server-Readiness/Prozessbaum/`shell=True`/Duplikat, notebooklm-bare-except/Cleanup, `ensure_comfyui`-Logs ohne `-Force`, YAML-Regex, Seed/Poll/Upscale-Cleanup-Fixes) sind nicht erneut aufgeführt.

`skills/custom/gen-asset/scripts/upscale.py:164` - severity(medium) - Das `finally` löscht die Staging-Kopie in ComfyUIs geteiltem Input auf jedem Pfad, auch nach Timeout. Fehlerszenario: `/prompt` hängt hinter einem langen Job, die Poll-Schleife gibt nach `--timeout` 1200s auf (`sys.exit` in Zeile 161). ComfyUI hat die Datei oft noch nicht geöffnet (Queued). `os.remove` gelingt, der Job startet später, `LoadImage` findet `upscale_src_<hex>_…` nicht. Der Lauf ist tot, die GPU-Arbeit danach ebenfalls; der Comment in Zeile 168 deckt nur den Windows-Lock-Fall (`OSError`), nicht den noch nicht geöffneten Queue-Fall. Das ist die Kehrseite des Cleanup-Fixes 8071b34.

`skills/custom/gen-asset/scripts/upscale.py:23` - severity(medium) - `COMFY_INPUT` ist fest `D:\Apps\Stability Matrix\Data\Packages\ComfyUI\input`, die API läuft über `--url`/`COMFYUI_URL`. Fehlerszenario: ComfyUI ist erreichbar (Laptop-Tunnel, andere Installation, anderer Port), `/system_stats` gelingt, `os.makedirs` legt den Stability-Matrix-Baum lokal an und kopiert dorthin. Der Server sucht denselben Namen in *seinem* Input-Ordner, findet nichts, die Poll-Schleife sitzt die vollen 1200s ab und meldet Timeout.

`skills/custom/gen-asset/scripts/comfy_generate.py:188` - severity(medium) - `--timeout` ist keine Wanduhr: die Schleife zählt nur `timeout/1.5` Iterationen, jedes `api()` auf `/history/{id}` (Zeile 191) hängt bis zu 600s (`api()`-Default Zeile 27). Dieselbe Konstruktion in `upscale.py:139`. Fehlerszenario: ComfyUI nimmt TCP an, die HTTP-Antwort bleibt aus (GPU-Hang, blockierender Custom-Node). Ein einziges Poll verbraucht 600s; danach folgen weitere. Der Lauf dauert weit über die angegebenen 900s, ohne `/interrupt`, der Prompt bleibt in der Queue und blockiert Folgejobs.

`skills/custom/website-audit/SKILL.md:104` - severity(medium) - Das verpflichtende Lighthouse-Rezept pinnt Debug-Port `9222`, Profil `%TEMP%\edge-lh` und Report `%TEMP%\lh-report` (Zeile 138). Fehlerszenario: Ein voriger Audit ist vor dem Kill in Zeile 168 abgestürzt, oder zwei Audits laufen parallel. Die Wait-Schleife in Zeile 111 akzeptiert den Altprozess auf 9222, Lighthouse misst die falsche Session bzw. überschreibt `lh-report.report.json`; Scores und Empfehlungen gehören dann zur anderen URL.

`skills/custom/gen-asset/scripts/ledger.py:110` - severity(low) - `cmd_find` macht `json.loads(line)` ohne Schutz. Fehlerszenario: Ein paralleles `add` (zwei Agenten) oder ein Abbruch mitten in der Append-Zeile hinterlässt eine unvollständige JSONL-Zeile. Jeder spätere `find --vertical …` stirbt mit `JSONDecodeError`, der Index ist unbenutzbar, obwohl die übrigen Zeilen gültig sind.

`skills/custom/web/references/testing.md:47` - severity(low) - Die Recon-Anweisung schreibt `page.screenshot(path='/tmp/inspect.png', …)`. Fehlerszenario: Ein Agent folgt dem Web-Skill auf Windows, `C:\tmp` existiert nicht, Playwright wirft `FileNotFoundError`, die Recon bricht ab, bevor Selektoren gesammelt sind.

## Modul-Audit: scripts/ (Run-ID 20260902T120731-18fbcc)

Keine neuen Findings in `scripts/` gegenüber `docs/reviews/` und `docs/backlog.md`.

Bekannte offene Punkte (YAML-Regex-Parser, Vendor-Import ohne Staging/atomarem Lock, Partial-Skip, `brand-review` ohne Lock, Staging ohne Inhaltsprüfung) sind nicht erneut aufgeführt.

Geprüft:

- `scripts/skills/lib.ps1`
- `scripts/skills/sync.ps1`
- `scripts/skills/vendor-import.ps1`
- `scripts/skills/setup-from-profile.ps1`
- `scripts/skills/validate.ps1`
- `scripts/skills/update-vendor.ps1`
- `scripts/skills/archive-report.ps1`
- `scripts/skills/validate-skills.ps1`
- `scripts/skills/resolve-bundle.ps1`
- `scripts/skills/fix-encoding.ps1`
- `scripts/project/bootstrap-project.ps1`

## Stichproben aus den Modul-Audits (hart am Code nachvollzogen)

1. **upscale.py:164, severity medium — bestätigt.** `try`-Block sys.exit bei Timeout (Zeile 160-161: `if not img: sys.exit(...)`); das `finally` (Zeile 163-172) räumt `staged_input` in jedem Fall auf, `os.remove(staged_input)` in einem eigenen `try/except OSError: pass` (Zeile 170-172). Ein `OSError` (Windows-Filelock) wird abgefangen, ein bereits gequeuter aber noch nicht geöffneter Job lässt `os.remove` aber erfolgreich durchlaufen — die Datei verschwindet, bevor ComfyUI sie liest. Das Fehlerszenario aus dem Finding tritt exakt so ein.

2. **comfy_generate.py:188, severity medium — bestätigt.** `deadline = args.timeout / 1.5` (Zeile 186), Schleife `while polls < deadline` mit `time.sleep(1.5)` (Zeile 188-189), pro Iteration ein Aufruf `api(args.url, f"/history/{prompt_id}")` (Zeile 191) ohne eigenen Timeout-Parameter. `api()` selbst hat den Default `timeout=600` (Zeile 27) und übergibt ihn unverändert an `urllib.request.urlopen(req, timeout=timeout)` (Zeile 36). Ein einzelner Poll kann also bis zu 600 Sekunden blockieren, unabhängig vom übergebenen `--timeout`; dieselbe Struktur (Default-`timeout=600` in `api()`, kein Override beim Poll-Aufruf) liegt in `upscale.py:139` identisch vor.
