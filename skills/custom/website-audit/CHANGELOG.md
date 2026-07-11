# Changelog: website-audit

Self-Optimization-Log (siehe SKILL.md, Schritt 4). Neueste Einträge oben.
Format: `YYYY-MM-DD, Auslöser -> Änderung`.

## 2026-07-06, Lauf blumsoft.de (Live, mobil)
- Reibung: `npx`/`node` in der non-interaktiven Tool-PowerShell nicht im PATH
  (Maschine nutzt fnm; Multishell-PATH nur interaktiv aktiv). Kostete mehrere
  Anläufe, bis Node über den fnm-node-versions-Pfad gefunden war.
- Fix: Schritt 2 um Block "b2) Node/npx sicherstellen" ergänzt (fnm-Pfad-Fallback,
  PATH-Prepend im selben Call wie Lighthouse).

## 2026-07-02, Lauf holz-weisbrodt.de (www + shop)
- Reibung: `foreach`-Statement direkt in `| Format-Table` gepipet -> ParserError
  "empty pipe element" (zweimal). Fix: `$(foreach ...)` bzw. `ForEach-Object`.
- Reibung: `$home` als Variable kollidierte mit der read-only Automatic Variable.
- Reibung: `Content-Encoding` fehlte in Invoke-WebRequest-Headers (pwsh
  dekomprimiert automatisch), Kompressions-Check brauchte `curl.exe`.
- Fix: alle drei als Stolperfallen-Block in references/security-geo-checks.md ergänzt.

## 2026-06-21, Lauf blumsoft.de lokal (out/)
- Reibung: `largest-contentful-paint-element` und `render-blocking-resources`
  lieferten leere `details.items` (LH 12+ Insights-Format). Hebel heißen `*-insight`.
- Reibung: lokaler `npx serve` setzt kein Cache-Control, `cache-insight` meldet
  falsche "savings" (Produktions-nginx irrelevant).
- Fix: beide Hinweise in references/lighthouse-audits.md ergänzt.

## 2026-06-21, Lauf blumsoft.de
- Reibung: Redirect-Check in security-geo-checks.md warf eine rote
  "maximum redirection exceeded"-Meldung (`-MaximumRedirection 0` ohne
  `-ErrorAction SilentlyContinue`). Response (302) kam trotzdem korrekt an.
- Fix: `-ErrorAction SilentlyContinue` ergänzt, Kommentar zur 301-vs-302-Wertung.

## 2026-06-21, Initial
- Skill erstellt. Checkliste 1-9, Lighthouse-Messprozedur (Edge-Debug-Port),
  Report-Template, Ads-Abschnitt.
- Ergänzt: Checks 10 (Security-Header/TLS), 11 (GEO/AEO), 12 (Broken Links /
  Third-Party), references/security-geo-checks.md, Feedback-Loop (Schritt 4).
