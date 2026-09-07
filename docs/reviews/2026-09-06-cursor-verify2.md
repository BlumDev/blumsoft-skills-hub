# Verify der Triage-Fixes 2026-09-04/06 (cursor-grok-4.6-high)

Werkzeug: cursor-agent, Modell cursor-grok-4.6-high, read-only über das ai-router-Gate. Run-ID `20260907T074020-639054`. Gegenstand: der Diff der Triage vom 2026-09-04/06 (`.claude/verify/triage-20260906.patch`, Stand `dca4579`), also die drei Code-Fixes `9f0cb6f`, `f938366`, `ddb3ad4` samt ihren Tests. Auftrag an das Werkzeug: prüfen, ob die Fixes halten, was ihre Commit-Messages zusagen. Ergebnis: 4 Findings (2 medium, 2 low), dazu eine Liste geprüfter Stellen ohne Befund.

Triage am Code: Claude Opus 5, 2026-09-07, Basis `dca4579`. Alle vier Findings sind am heutigen Code nachvollzogen worden, keines widerlegt; alle vier sind behoben, jeder Fix mit einer Mutationsprobe, deren Rot vor dem Fix gemessen ist (Belege im jeweiligen Commit-Text).

| Finding | Urteil |
| --- | --- |
| 1. medium `comfy_generate.py:201` / `upscale.py:180`: die Poll-Klammer `(OSError, ValueError)` lässt `http.client`-Protokollfehler durch | bestätigt (Probe: beide Skripte sterben an einer `IncompleteRead` beim ersten Poll), behoben in `7c13030` |
| 2. medium `comfy_generate.py:208` / `upscale.py:187`: `last_poll_error` wird nie gelöscht, die Timeout-Meldung nennt einen überholten Fehler | bestätigt (Probe: ein 500 im ersten Poll steht nach zwei erfolgreichen Polls weiter in der Meldung), behoben in `6278db3` |
| 3. low `tests/test_gen_asset.py:647`: der Test misst nur `KeyboardInterrupt`, obwohl sein Kommentar jede Ausnahme zusagt | bestätigt (Mutationsprobe: eine auf `KeyboardInterrupt`/`SystemExit` verengte Implementierung lässt den alten Test grün), Test erweitert in `15b9e12`, kein Produktionscode geändert |
| 4. low `upscale.py:151` bis `162`: zwischen POST `/prompt` und `prompt_id` ist `keep_staged` noch False | bestätigt (Probe: Strg+C im POST-Fenster löscht die Staging-Kopie), behoben in `1be5ecc` |

Die Findings 1, 2 und 4 sind derselbe Fehler wie in der Vorrunde, jeweils einen Schritt weiter gedacht: die Ausnahmeklammer deckt die dritte Fehlerklasse nicht, die Fehlermeldung überlebt ihren Anlass, und das Eigentum an der Staging-Kopie beginnt eine Zeile zu spät. Zu 4 ist der Fix bewusst enger gefasst als das Finding: die Kopie gehört ab dem Absenden dem Job, freigegeben wird sie nur dort, wo die Antwort beweist, dass nichts in der Queue steht (HTTP-Fehler oder Body ohne `prompt_id`). Eine mitten im POST sterbende Verbindung behält sie, weil eine Dateileiche billiger ist als ein Job ohne Eingabe; ein eigener Test hält die beiden Freigabewege fest.

Der Abschnitt "Geprüft, kein weiterer Befund" ist stichprobenartig gegengeprüft statt übernommen: die Ledger-Aussage hält (ohne `errors="replace"` in `ledger.py:107` läuft `test_a_line_broken_mid_utf8_does_not_hide_the_intact_entries` in einen `UnicodeDecodeError`, die beiden anderen Ledger-Tests bleiben grün), und die Timeout-Texte parst tatsächlich niemand im Repo (`grep "kein Bild"` trifft nur die beiden Skripte selbst und fremde Worktrees unter `.claude/`). Der `LOCAL_HOSTS`-Punkt bleibt als `20260904-upscale-tunnel-input-dir` offen, seine Fundstelle ist durch die Fixes dieser Runde von `upscale.py:25,121` auf `27,123` gewandert.

Gates nach dem letzten Fix: `validate.ps1` PASS (15 Bundles, 82 Registry-Skills), `validate-skills.ps1` PASS (82 Skills, 0 Fehler, 0 Warnungen), Pester 51 grün / 0 rot, `python -m unittest tests.test_gen_asset tests.test_with_server` 29 grün. Keine vorbestehenden Rottöne.

## Externe Ausgabe (wörtlich)

Der Diff soll drei Restfehler der Staffel vom 02.09. schließen: UTF-8-Bruch im Ledger tötet `find` nicht mehr, ein unlesbarer `/history`-Body wird wiederholt statt den Lauf zu beenden, und die Staging-Kopie überlebt jeden Abbruch nach dem Queueing. Der Tunnel-Fall war bewusst ausgenommen.

## Findings

### medium `skills/custom/gen-asset/scripts/comfy_generate.py:201` und `skills/custom/gen-asset/scripts/upscale.py:180`

Der Poll-Fix schließt nur `json.loads` und UTF-8-Dekodierung. Derselbe Neustart- oder Proxy-Pfad bleibt über HTTP-Protokollfehler erreichbar, die weder `OSError` noch `ValueError` sind.

`api()` liest den Body erst nach `urlopen`:

```36:37:skills/custom/gen-asset/scripts/comfy_generate.py
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))
```

Die Schleife fängt nur zwei Klassen:

```199:210:skills/custom/gen-asset/scripts/comfy_generate.py
        try:
            history = api(args.url, f"/history/{prompt_id}", timeout=min(30.0, remaining))
        except (OSError, ValueError) as exc:  # connection, or a body that is not JSON
            last_poll_error = exc
            print(f"Poll fehlgeschlagen, weiter: {exc}", file=sys.stderr)
            continue
```

Identisch in `upscale.py:178-189`. `http.client.IncompleteRead` (Content-Length größer als der gelieferte Body, typisch wenn ComfyUI oder ein Proxy die Antwort mitten im Neustart abschneidet) und `http.client.BadStatusLine` (Müll in der Statuszeile) erben von `Exception`, nicht von `OSError`/`ValueError`. `resp.read()` liegt außerhalb des `except OSError` in `urllib.request`, die Ausnahme kommt also unverändert in `main`. Der Lauf stirbt beim ersten Poll nach `/prompt`, genau das Verhalten, das `f938366` für leeren oder HTML-Body geschlossen hat.

`PollErrorTests.test_a_poll_answering_with_garbage_is_retried` wirft nur `JSONDecodeError`. Ein Entfernen des `ValueError`-Zweigs macht diesen Test rot; ein `IncompleteRead` bleibt grün und tötet den Lauf weiter.

**Prüfschritt:** In beiden Skripten `api()` so stubben, dass der erste `/history`-Aufruf `http.client.IncompleteRead(b"partial")` wirft und der zweite `SUCCESS_HISTORY_ENTRY` liefert. Erwartung nach dem Fix: Lauf erzeugt die Ausgabedatei. Ist: unbehandelte `IncompleteRead`, kein Bild.

### medium `skills/custom/gen-asset/scripts/comfy_generate.py:208` und `skills/custom/gen-asset/scripts/upscale.py:187`

`last_poll_error` wird nur gesetzt, nie bei einem erfolgreichen Poll gelöscht. Die neue Timeout-Meldung kann damit einen Fehler nennen, der nicht mehr der Grund des Timeouts ist.

```190:213:skills/custom/gen-asset/scripts/comfy_generate.py
    last_poll_error = None
    while True:
        ...
        try:
            history = api(args.url, f"/history/{prompt_id}", timeout=min(30.0, remaining))
        except (OSError, ValueError) as exc:
            last_poll_error = exc
            print(f"Poll fehlgeschlagen, weiter: {exc}", file=sys.stderr)
            continue
        entry = history.get(prompt_id)
        if not entry:
            continue
```

Konkreter Ablauf, genau der Neustart, für den die Wiederholung gebaut wurde: erster Poll `HTTPError 502`, danach antwortet `/history` wieder mit `{}` oder einem Queue-Eintrag ohne Bilder, der Job läuft, `--timeout` greift. Die Meldung lautet dann `Timeout nach …s: kein Bild im History-Output. Letzter Poll-Fehler: HTTP Error 502…`, obwohl die letzten Polls erfolgreich waren. In `upscale.py:211-214` steht derselbe Satz vor dem Hinweis, der Job könne noch in der Queue stehen. Wer den 502 glaubt und ComfyUI neu startet, wirft die GPU-Arbeit weg. `test_the_timeout_names_the_poll_error_that_caused_it` lässt jeden Poll scheitern (`fails=None`) und kann diese Mutation nicht rot machen.

**Prüfschritt:** `poll_error_api` mit `fails=1` und `history_entry=QUEUED_HISTORY_ENTRY` plus `FakeClock` und `--timeout 6`. Erwartung: Timeout-Text ohne `502`. Ist: `Letzter Poll-Fehler` trägt den 502 des ersten Polls.

### low `tests/test_gen_asset.py:647`

Der neue Test heißt die Mutation „Strg+C und jede unerwartete Ausnahme“, prüft aber nur `KeyboardInterrupt`.

```647:668:tests/test_gen_asset.py
    def test_keeps_the_copy_when_the_run_is_interrupted_while_the_job_is_queued(self):
        # ... Strg+C runs through finally as well, and so does any unexpected exception.
        def api(base, path, payload=None, timeout=600):
            ...
            raise KeyboardInterrupt()
        ...
            with self.assertRaises(KeyboardInterrupt):
                upscale.main()
        self.assertEqual(len(os.listdir(self.comfy_input)), 1,
                         'the queued job still needs its input image')
```

Eine Implementierung, die nur `except KeyboardInterrupt` um das Flag legt und jede andere Ausnahme weiter ins `finally` mit `keep_staged is False` laufen lässt, bleibt grün. Der Produktionscode setzt das Flag nach der `prompt_id` und deckt das ab; der Test beweist es nicht.

**Prüfschritt:** Dieselbe Fixture, aber `raise RuntimeError("poll")` statt `KeyboardInterrupt`. Erwartung laut Kommentar: Datei bleibt. Ein nur auf `KeyboardInterrupt` spezialisierter Fix würde sie löschen, der Test würde das nicht sehen.

### low `skills/custom/gen-asset/scripts/upscale.py:151` bis `162`

Nach `/prompt` ist `keep_staged` noch False, solange `api(/prompt)` blockiert. ComfyUI legt den Job an und sendet erst dann die `prompt_id`. Unterbricht man den Client in diesem Fenster (Strg+C während des POST), läuft `finally` mit `keep_staged is False` und löscht die Kopie, obwohl der Job schon in der Queue stehen kann. Das ist derselbe LoadImage-Verlust, nur vor der Zeile, ab der der Fix das Eigentum zuweist. Der neue Test trifft `/history`, nicht `/prompt`.

```151:162:skills/custom/gen-asset/scripts/upscale.py
        resp = api(a.url, "/prompt", {"prompt": wf, "client_id": cid})
        pid = resp.get("prompt_id")
        if not pid:
            sys.exit(f"Keine prompt_id erhalten: {resp}")
        print(f"queued {pid} seed={a.seed} upscale_by={a.upscale_by} denoise={a.denoise}", file=sys.stderr)
        keep_staged = True
```

**Prüfschritt:** Stub, der bei `/prompt` blockiert bzw. `KeyboardInterrupt` wirft, danach `os.listdir(COMFY_INPUT)`. Erwartung analog zum Poll-Abbruch: Datei noch da. Ist: Ordner leer.

## Geprüft, kein weiterer Befund

- **Ledger UTF-8:** `errors="replace"` in `ledger.py:113` verhindert `UnicodeDecodeError` beim Iterieren. Danach greift der vorhandene `ValueError`-Skip. Kein zweiter Leser der JSONL im Repo. `test_a_line_broken_mid_utf8_does_not_hide_the_intact_entries` fällt aus, wenn man `errors="replace"` streicht. Ein intakter Eintrag hinter einem Abbruch ohne Newline klebt an der Leiche; das ist die alte JSONL-Rennbedingung ohne Lock, nicht neu durch diesen Fix.
- **JSONDecodeError / UnicodeDecodeError im Poll:** beide sind `ValueError`, die Klammer in beiden Skripten deckt die benannte HTML- oder Leer-Body-Route.
- **keep_staged nach `prompt_id`:** Timeout, ComfyUI-Fehler und Erfolg setzen das Flag wie behauptet; der KeyboardInterrupt-Test trifft den Poll-Pfad.
- **Aufrufer der Timeout-Texte:** im Repo parst niemand `kein Bild`. Die Zusatzphrase ändert nur die Meldung.
- **Windows-Pfade im Ledger:** `json.dumps(..., ensure_ascii=False)` bleibt; der Fix ändert nur das Lesen.
- **Tunnel `LOCAL_HOSTS`:** unverändert in `upscale.py:25,121`, weiter offen als `20260904-upscale-tunnel-input-dir`. Nicht Teil der drei Code-Fixes dieses Diffs.
