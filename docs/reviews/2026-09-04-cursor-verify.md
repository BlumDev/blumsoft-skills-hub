# Verify der Fix-Staffel 2026-09-02 (cursor-grok-4.6-high)

Werkzeug: cursor-agent, Modell cursor-grok-4.6-high, read-only über das ai-router-Gate. Run-ID `20260904T072157-6da303`. Gegenstand: der Diff der Wartungs-Session vom 2026-09-02 (`.claude/verify/staffel-20260902.patch`, Stand `ee3120a`). Auftrag an das Werkzeug: prüfen, ob die sechs Fixes halten, was ihre Commit-Messages zusagen. Ergebnis: 4 Findings, alle medium, dazu eine Liste geprüfter Stellen ohne Befund.

Triage am Code: Claude Opus 5, 2026-09-06, Basis `ee3120a`. Alle vier Findings sind am heutigen Code nachvollzogen worden, keines widerlegt. Drei sind behoben, jeder Fix mit einer Mutationsprobe belegt; eines bleibt offen, weil es eine Architekturentscheidung braucht.

| Finding | Urteil |
| --- | --- |
| 1. `ledger.py:107` fängt nur `ValueError`, ein Abbruch mitten im Multibyte stirbt schon beim Zeilenlesen | bestätigt, behoben in `9f0cb6f` |
| 2. `upscale.py:172` und `comfy_generate.py:200`: `except OSError` deckt den Antwort-Body nicht ab | bestätigt, behoben in `f938366` (die zweite Hälfte bewusst anders gelöst, siehe Triage) |
| 3. `upscale.py:25,121`: der Guard erkennt den Tunnel auf 127.0.0.1 nicht | bestätigt als Restlücke, offen als `20260904-upscale-tunnel-input-dir` |
| 4. `upscale.py:197`: `keep_staged` wird nur im Timeout-Pfad gesetzt | bestätigt, behoben in `ddb3ad4` |

Gates nach dem letzten Fix: `validate.ps1` PASS, `validate-skills.ps1` PASS (82 Skills, 0 Fehler), Pester 51 grün / 0 rot, `python -m unittest tests.test_gen_asset tests.test_with_server` 25 grün. Keine vorbestehenden Rottöne.

## Externe Ausgabe (wörtlich)

Die Staffel sollte sechs Produktionsfehler schließen: Pester-Discovery, Poll-Wanduhr plus Wiederholen nach fehlgeschlagenem Poll, Staging-Datei nach Timeout behalten, `COMFY_INPUT` nicht still an eine fremde Instanz kopieren, kaputte JSONL-Zeilen überspringen, ComfyUI-Logs nicht auf gesperrte TEMP-Namen legen. Dagegen gehalten:

**medium** `skills/custom/gen-asset/scripts/ledger.py:107`  
`cmd_find` fängt nur `ValueError` von `json.loads`. Ein Abbruch mitten in einem UTF-8-Multibyte (Prompt, Notiz, Windows-Pfad mit Umlaut; `cmd_add` schreibt mit `ensure_ascii=False`) wirft `UnicodeDecodeError` schon beim Zeilenlesen, bevor der `try` greift. Der Index stirbt weiter mitsamt aller intakten Zeilen darüber.

```97:114:skills/custom/gen-asset/scripts/ledger.py
    with open(LEDGER, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    ...
    with open(LEDGER, "r", encoding="utf-8") as fh:
        for number, line in enumerate(fh, 1):
            ...
            try:
                rows.append(json.loads(line))
            except ValueError:
```

Die neuen Tests schreiben nur ASCII-Leichen (`tests/test_gen_asset.py:296`), die Probe kann diesen Pfad nicht rot machen.  
**Prüfschritt:** Datei mit `{"image":"ok.png","rating":5}\n{"note": "` plus dem einzelnen Byte `0xC3` (Anfang von `ü`) schreiben, `cmd_find` aufrufen. Erwartung nach dem Fix: `ok.png` erscheint. Ist: `UnicodeDecodeError`, kein Treffer.

**medium** `skills/custom/gen-asset/scripts/upscale.py:172` und `skills/custom/gen-asset/scripts/comfy_generate.py:200`  
Dieselbe `except OSError`-Klammer ist zu breit und zu schmal. `urllib.error.HTTPError` erbt von `OSError`: ein dauerhaftes 500 von `/history` wird bis `--timeout` wiederholt (Default 1200s bzw. 900s), danach kommt „Timeout … kein Bild“ statt des HTTP-Fehlers. Bei upscale bleibt die Staging-Datei liegen. Umgekehrt bleiben `JSONDecodeError` und `UnicodeDecodeError` in `api()` (`json.loads(r.read().decode("utf-8"))`) ungefangen; ein leerer oder HTML-Body beim Neustart beendet den Lauf sofort. Der Commit versprach beides: Wanduhr und „ein gescheiterter Poll wird wiederholt“.

```39:40:skills/custom/gen-asset/scripts/upscale.py
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))
```

```170:176:skills/custom/gen-asset/scripts/upscale.py
            try:
                hist = api(a.url, f"/history/{pid}", timeout=min(30.0, remaining))
            except OSError as exc:  # timeout, reset connection, ComfyUI restarting
                print(f"Poll fehlgeschlagen, weiter: {exc}", file=sys.stderr)
                continue
```

`PollBudgetTests` mockt `api()` so, dass sie nie wirft (`tests/test_gen_asset.py:190-204`). Ein Entfernen des `except` bleibt grün.  
**Prüfschritt:** `api()` im Poll einmal `urllib.error.HTTPError(500, …)` werfen lassen: Lauf muss sofort mit 500 enden, nicht erst nach `--timeout 6`. Zweiten Lauf mit HTTP 200 und Body `""` machen: muss weiterpollen, nicht mit `JSONDecodeError` sterben.

**medium** `skills/custom/gen-asset/scripts/upscale.py:25` und `:121`  
Der neue Guard lehnt nur Hostnamen außerhalb von `localhost` / `127.0.0.1` / `::1` ab. Genau der im Kommentar genannte Tunnel (`--url` zeigt auf 127.0.0.1, ComfyUI liegt woanders) bleibt der alte Fehler: Kopie landet in `COMFY_INPUT`, der Server sieht die Datei nicht, der Lauf läuft in den Timeout. Der Test `test_a_local_url_still_uses_the_installation_default` zementiert das.

```24:26:skills/custom/gen-asset/scripts/upscale.py
# Hosts whose input folder the local filesystem can be: everything else needs --input-dir.
LOCAL_HOSTS = frozenset(("localhost", "127.0.0.1", "::1", ""))
```

```119:126:skills/custom/gen-asset/scripts/upscale.py
    host = (urllib.parse.urlparse(a.url).hostname or "").lower()
    if not a.input_dir and host not in LOCAL_HOSTS:
        sys.exit(
            f"--url zeigt auf '{host}', der Eingabeordner ist aber der lokale ({COMFY_INPUT}). "
            ...
        )
```

**Prüfschritt:** `upscale.py --url http://127.0.0.1:8188` gegen eine Instanz, deren Input-Ordner nicht `D:\Apps\Stability Matrix\Data\Packages\ComfyUI\input` ist, ohne `--input-dir`. Erwartung nach dem Fix: Abbruch mit Hinweis auf `--input-dir`. Ist: Kopie lokal, kein Prompt-Abbruch, später Timeout.

**medium** `skills/custom/gen-asset/scripts/upscale.py:197`  
`keep_staged` wird nur gesetzt, wenn die Poll-Schleife budgetbedingt endet. Jeder andere Abbruch, während der Job noch in der Queue steht, läuft durch `finally` und löscht die Datei. Der benannte Fehler (LoadImage scheitert, GPU-Arbeit weg) bleibt über Strg+C und über jede unbehandelte Ausnahme nach `api(/prompt)` erreichbar. ComfyUI bekommt kein Cancel.

```192:214:skills/custom/gen-asset/scripts/upscale.py
        if not img:
            keep_staged = True
            sys.exit(
                f"Timeout nach {a.timeout}s: kein Bild. Job {pid} kann noch in der Queue stehen, "
                f"die Eingabekopie bleibt deshalb liegen: {staged_input}"
            )
        ...
    finally:
        if not keep_staged:
            try:
                os.remove(staged_input)
```

`test_keeps_the_copy_when_the_run_times_out` stellt nur `SystemExit` nach FakeClock-Timeout; ein `KeyboardInterrupt` in derselben Schleife würde grün bleiben, obwohl die Datei weg ist.  
**Prüfschritt:** Staging-Ordner mocken, nach `/prompt` in der Poll-Schleife `KeyboardInterrupt` werfen, danach `os.listdir(COMFY_INPUT)`. Erwartung analog zum Timeout-Fix: Datei noch da. Ist: Datei weg.

Geprüft und hier nicht als Befund: Pester-`BeforeAll`/`BeforeDiscovery` in den beiden angefassten Suiten plus die übrigen `*.Tests.ps1` (die lagen schon auf `$script:`); `Copy-Item -Path` mit `*` statt `-LiteralPath`; Wanduhr und `timeout=min(30, remaining)` am `/history`-Aufruf; Remote-Host ohne `--input-dir` wird abgelehnt; ASCII-JSONL-Leiche wird übersprungen; Timeout-Pfad behält die Staging-Datei; `ensure_comfyui.ps1` eindeutige Logs, `try/catch`, `-PassThru`/`HasExited`. Doku (`testing.md`, website-audit) lag nicht im Patch.

## Triage am Code (Claude, 2026-09-06)

Die Belege stammen aus einem Repro-Skript gegen `ee3120a`, also gegen den Stand, den das Werkzeug gesehen hat.

### 1. ledger.py stirbt an einer Zeile, die unterhalb der Textebene kaputt ist (bestätigt, behoben)

Beleg: eine Ledger-Datei aus einer intakten Zeile plus `{"note": "` und dem Einzelbyte `0xC3` beendet `cmd_find` mit `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xc3 in position 0: unexpected end of data`, `ok.png` erscheint nicht im Output. Die Ursache steht genau so im Finding: `ledger.py:108` dekodiert beim Iterieren der Datei, der `try` ab `:112` umschließt nur `json.loads`, also greift der Skip-Pfad nie.

Fix (`9f0cb6f`): die Datei wird mit `errors="replace"` gelesen. Die kaputte Zeile trägt danach das Ersatzzeichen, `json.loads` lehnt sie ab und sie läuft durch den vorhandenen Skip-Pfad samt Meldung auf stderr. Eine Zeile mit einem einzelnen kaputten Byte mitten im gültigen JSON bleibt damit sogar erhalten statt verworfen zu werden.

Test: `LedgerFindTests.test_a_line_broken_mid_utf8_does_not_hide_the_intact_entries`. Mutationsprobe: `errors="replace"` entfernt, Test rot (`UnicodeDecodeError`), zurückgestellt grün.

### 2. Der Poll fängt die Verbindung, nicht die Antwort (bestätigt, behoben, zweite Hälfte anders gelöst)

Beleg für die Hälfte "zu schmal": ein `/history`, das eine `JSONDecodeError` wirft (leerer Body oder HTML-Seite eines neustartenden ComfyUI, `api()` endet in `json.loads(...)`), beendet beide Skripte sofort nach dem Queueing. Gemessen an `ee3120a` für `upscale.py` und `comfy_generate.py`. Damit lief die Wiederholung, die der Commit `820968f` ausdrücklich für den Neustart eingebaut hat, im wichtigsten Fall nicht.

Beleg für die Hälfte "zu breit": ein Server, der jeden Poll mit HTTP 500 beantwortet, wird bei `--timeout 60` 39-mal gepollt und der Lauf endet mit `Timeout nach 60s: kein Bild ...`. Der Statuscode taucht nirgends auf.

Fix (`f938366`): beide Schleifen fangen `(OSError, ValueError)`. Den Abbruch beim ersten dauerhaften HTTP-Fehler habe ich bewusst nicht übernommen: ein 5xx während eines Neustarts ist vorübergehend und ein Abbruch darauf würde gesunde Läufe töten. Stattdessen merkt sich die Schleife den letzten Poll-Fehler und die Timeout-Meldung nennt ihn. Begründung in `docs/decisions.md`.

Tests: `PollErrorTests.test_a_poll_answering_with_garbage_is_retried` und `PollErrorTests.test_the_timeout_names_the_poll_error_that_caused_it`, beide über beide Skripte. Mutationsproben: `except` zurück auf `OSError` macht den ersten Test rot (2 Fehler), das Streichen der Ursache aus der Meldung den zweiten (2 Fehlschläge).

### 3. Der Guard sieht den Tunnel nicht (bestätigt, offen)

Beleg: `--url` auf `127.0.0.1` durchläuft `LOCAL_HOSTS` (`upscale.py:25,121`), die Kopie landet im lokalen `COMFY_INPUT` und der Lauf endet im Timeout. Im Repro liegt der Default-Ordner nicht einmal vor: `os.makedirs(input_dir, exist_ok=True)` legt ihn an, die Kopie landet darin, der gestubbte Server sieht sie nicht. Der Hostname trägt die Information schlicht nicht, ob hinter dem Port ein Tunnel steht.

Nicht behoben, weil die einzige belastbare Prüfung eine über HTTP ist: den Staging-Namen nach dem Kopieren gegen die Dateiliste des Servers halten (`/object_info/LoadImage`) oder das Bild gleich hochladen statt es zu kopieren. Beides ist eine Architekturentscheidung mit neuer Abhängigkeit von einer ComfyUI-Antwortform, und ohne laufende Instanz nicht prüfbar. Gebucht als `20260904-upscale-tunnel-input-dir`, Optionen in `docs/decisions.md`.

### 4. Die Staging-Kopie überlebt nur den Timeout (bestätigt, behoben)

Beleg: wirft der erste `/history`-Poll ein `KeyboardInterrupt`, ist der Input-Ordner nach dem Lauf leer. Der Job kann zu diesem Zeitpunkt noch in der Queue stehen, ComfyUI öffnet die Datei erst beim Start, also ist das derselbe Datenverlust, den `820968f` für den Timeout-Pfad geschlossen hat.

Fix (`ddb3ad4`): `keep_staged` wird gesetzt, sobald der Job eine `prompt_id` hat, und nur dort zurückgenommen, wo der Job nachweislich vorbei ist: nach einem gemeldeten ComfyUI-Fehler und sobald das Ergebnis vorliegt (vor dem Download, denn dann hat ComfyUI die Eingabe gelesen). Ein Lauf ohne `prompt_id` räumt weiter auf.

Test: `UpscaleInputCleanupTests.test_keeps_the_copy_when_the_run_is_interrupted_while_the_job_is_queued`. Mutationsproben: alte Platzierung von `keep_staged` macht den neuen Test rot, das Streichen der Freigabe vor dem Download bzw. im Fehlerpfad macht je einen der beiden vorhandenen Aufräum-Tests rot.

### Geprüfte Stellen ohne Befund

Die Liste am Ende der externen Ausgabe (Pester-Setup, `Copy-Item -Path`, Wanduhr, `timeout=min(30, remaining)`, Remote-Host-Ablehnung, ASCII-Leiche im Ledger, Timeout behält die Kopie, `ensure_comfyui.ps1`) habe ich stichprobenartig gegengelesen und teile sie: die zugehörigen Tests laufen grün und die Mutationsproben der Staffel vom 2026-09-02 stehen in den Commit-Texten. Der Hinweis, dass die Doku-Änderungen (`testing.md`, website-audit) nicht im Patch lagen, stimmt: der Patch enthält nur die Skript-Commits.
