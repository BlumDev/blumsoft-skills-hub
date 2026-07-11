---
name: website-audit
description: >-
  Prüft eine Website auf die wichtigsten Qualitätsprobleme und liefert einen
  priorisierten Markdown-Report mit Quick Wins. Eingabe: Live-URL oder lokaler
  Repo-Pfad (oder beides), die Skill erkennt selbst, was vorliegt. Misst
  Lighthouse mobil (Performance/SEO/Accessibility) real via Edge-Debug-Port,
  prüft Core Web Vitals (LCP/TBT/CLS/FCP/SI/TTI), Optik/Positionierung,
  Motion, Responsive (320-1440px), SEO/Schema.org, Security-Header/TLS, GEO/AEO
  (AI-Sichtbarkeit, llms.txt, AI-Crawler), Recht (Impressum/Datenschutz DACH),
  Conversion und bei Repo-Quellen die größten Assets und JS-Bundles. Analysiert
  und berichtet nur, ändert nichts ohne Freigabe. Use when the user wants to
  audit, check or review a website or landing page, run Lighthouse, check
  Performance/SEO/Accessibility/Core Web Vitals, security headers, GEO/AEO (AI
  search visibility), find Quick Wins, or get a website quality report. Trigger:
  "Website auditieren/prüfen/checken", "Lighthouse", "Website-Report", "Quick
  Wins", "Performance/SEO Check", "Security-Header", "GEO/AEO", "AI-Sichtbarkeit".
---

# Website Audit

Prüft eine Website auf Qualität und gibt einen priorisierten Report aus. **Nur
Analyse, keine Änderungen** am Code oder an der Seite ohne explizite Freigabe.
Am Ende fragen, ob die Quick Wins umgesetzt werden sollen.

Lead mit dem Verdikt. Deutsche Inhalte mit echten Umlauten, ae/oe/ue nur in
Code/Pfaden, keine Em-/En-Dashes in Prosa. Senior-Tonfall, knapp. Befunde aus
Repo-Quellen mit Belegstelle (`Datei:Zeile`).

**Abgrenzung zu `/seo-audit`:** Das ist ein Marketing-Skill (Keyword-Recherche,
Content-Gaps, Wettbewerb, Content-Kalender) und misst Lighthouse nicht real.
Dieser Skill ist der Engineering-/Qualitätscheck (gemessene Werte, Recht,
Repo-Tiefencheck, GEO/AEO). Sie ergänzen sich. Bei reinem Keyword-/Content-
Strategie-Wunsch auf `/seo-audit` verweisen, nicht doppeln.

## Schritt 0, Eingabe erkennen

Aufruf: `website-audit [url-oder-pfad]`. Argument auswerten:

- **URL** (beginnt mit `http(s)://` oder sieht aus wie eine Domain): Live-Audit.
- **Existierender Pfad**: Repo-Audit (Stack erkennen, Quellen lesen).
- **Beide**: Repo für Quellcode-Tiefencheck, URL für Lighthouse. Beste Variante.
- **Nichts**: prüfen, ob das aktuelle Verzeichnis ein Web-Repo ist; sonst kurz
  nach URL oder Pfad fragen. Nicht raten.

Nur nachfragen, wenn unklar. Bei Repo: Stack bestimmen (Next.js, Astro, Vite,
plain HTML, ...), Static Export vs. SSR erkennen (relevant für Bild-Optimierung).

## Schritt 1, Prüfkriterien (Checkliste)

Diese Punkte abarbeiten. Was nicht prüfbar ist (z.B. Repo fehlt, Seite offline),
explizit als "nicht prüfbar" markieren statt zu raten.

1. **Optik/Positionierung**: hochwertiger bespoke Eindruck statt Template-Look,
   Value Proposition in 5 Sekunden verständlich, konsistente Typo/Farbwelt,
   Trust-Elemente (Referenzen/Showcases), klare Conversion-CTA.
2. **Lighthouse mobil**: Performance, SEO, Accessibility. Zielmarke jeweils
   >= 95. **Real messen** (Schritt 2), nicht schätzen.
3. **Core Web Vitals** konkret nennen: LCP, TBT, CLS, FCP, Speed Index, TTI.
4. **Motion/Interaktion** (falls vorhanden): transform/opacity-only, 60 fps,
   `prefers-reduced-motion`-Fallback. Falls keine Motion: bewerten, ob welche
   sinnvoll wäre, ohne Übertreibung.
5. **Responsive**: kein Layoutbruch 320 bis 1440 px. An 320 px prüfen.
6. **SEO/Technik**: Title/Description/OG, Schema.org (Organization /
   LocalBusiness / ProfessionalService), Sitemap, robots, Canonical, saubere
   Heading-Hierarchie.
7. **Recht (DACH)**: Impressum (DDG Paragraph 5) und Datenschutz (DSGVO)
   vorhanden, vollständig, ohne offene Platzhalter. Cookie-/Tracking-Konformität
   (Consent nur nötig, falls Tracking/Ads geladen werden).
8. **Conversion**: Kontaktweg, Formular, Reaktionszeit-Versprechen, klare
   nächste Aktion, `tel:`/`mailto:` klickbar.
9. **Performance-Tiefencheck bei Repo-Quellen** (Schritt 3): größte Assets
   finden (rohe PNG statt WebP/AVIF, fehlendes `loading="lazy"`, fehlende
   `width`/`height`, unoptimierte Bilder, bei Static Export fehlt der
   Image-Optimizer), große JS-Bundles / unused JS.
10. **Security-Header & TLS**: HSTS, Content-Security-Policy,
    X-Content-Type-Options, X-Frame-Options bzw. CSP `frame-ancestors`,
    Referrer-Policy, Permissions-Policy. HTTP leitet auf HTTPS um, gültiges
    Zertifikat, kein Mixed Content (Lighthouse `is-on-https`), keine
    Server-/Framework-Banner-Leaks. Befehle: siehe
    [references/security-geo-checks.md](references/security-geo-checks.md).
11. **GEO/AEO (AI-Sichtbarkeit)**: Zitierfähigkeit in AI-Antwortmaschinen.
    `llms.txt` vorhanden, AI-Crawler-Policy in robots.txt bewusst gesetzt
    (GPTBot, OAI-SearchBot, ClaudeBot, PerplexityBot, Google-Extended, CCBot),
    Entitäten klar (Organization + `sameAs`, Autor, `datePublished`),
    antwortbare Struktur (klare Frage/Antwort-Blöcke, Listen/Tabellen,
    belegte Fakten), E-E-A-T-Signale (Autor, Über-uns, Aktualität). Befehle:
    siehe [references/security-geo-checks.md](references/security-geo-checks.md).
12. **Broken Links & Third-Party-Last**: interne/externe 404s, Redirect-Ketten,
    Anzahl/Gewicht eingebundener Dritt-Skripte (Tracking, Fonts, Widgets) als
    Performance- und Datenschutz-Risiko (koppelt an Punkt 7 Consent).

## Schritt 2, Lighthouse zuverlässig messen

Harness-Preview und ein normaler Chrome/Edge-Launch sind unzuverlässig (docken
an eine laufende Instanz an). Stattdessen Edge mit eigenem Profil und Debug-Port
starten und Lighthouse per `--port` andocken. Alle Befehle in **PowerShell**.

**a) Edge headless im Hintergrund starten:**

```powershell
$edge = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if (-not (Test-Path $edge)) { $edge = "C:\Program Files\Microsoft\Edge\Application\msedge.exe" }
Start-Process $edge -ArgumentList '--headless=new','--remote-debugging-port=9222',"--user-data-dir=$env:TEMP\edge-lh",'--no-first-run','--disable-extensions','about:blank'
```

**b) Auf den Debug-Port warten** (bis `/json/version` antwortet):

```powershell
$ok = $false
1..30 | ForEach-Object {
  if (-not $ok) {
    try { Invoke-RestMethod 'http://127.0.0.1:9222/json/version' -TimeoutSec 1 | Out-Null; $ok = $true }
    catch { Start-Sleep -Milliseconds 500 }
  }
}
if (-not $ok) { Write-Error 'Edge-Debug-Port nicht erreichbar' }
```

**b2) Node/npx sicherstellen** (diese Maschine nutzt **fnm**; in der
non-interaktiven PowerShell des Tools ist `node`/`npx` oft NICHT im PATH, weil das
fnm-Multishell-PATH nur in interaktiven Shells aktiviert wird). Erst testen, dann
via fnm den aktiven Node-Pfad **im selben Call** wie Lighthouse prependen
(Shell-State persistiert nicht zwischen Tool-Calls):

```powershell
if (-not (Get-Command npx -ErrorAction SilentlyContinue)) {
  $nodeExe = Get-ChildItem "$env:APPDATA\fnm\node-versions\*\installation\node.exe","$env:LOCALAPPDATA\fnm\node-versions\*\installation\node.exe" -ErrorAction SilentlyContinue |
             Sort-Object FullName -Descending | Select-Object -First 1
  if ($nodeExe) { $env:PATH = (Split-Path $nodeExe.FullName) + ";$env:PATH" }
}
node --version   # muss jetzt eine Version zeigen
```

**c) Lighthouse andocken** (Node 24/npm vorhanden, Lighthouse via `npx -y`):

```powershell
npx -y lighthouse <URL> --port=9222 --only-categories=performance,accessibility,seo --form-factor=mobile --screenEmulation.mobile --throttling-method=simulate --output=json --output=html --output-path=$env:TEMP\lh-report --quiet
```

Erzeugt `$env:TEMP\lh-report.report.json` und `...report.html`.

**d) Scores und Metriken aus dem JSON lesen:**

```powershell
$j = Get-Content "$env:TEMP\lh-report.report.json" -Raw | ConvertFrom-Json
[pscustomobject]@{
  Performance   = [math]::Round($j.categories.performance.score   * 100)
  Accessibility = [math]::Round($j.categories.accessibility.score * 100)
  SEO           = [math]::Round($j.categories.seo.score           * 100)
}
'LCP','TBT','CLS','FCP','SI','TTI' | Out-Null
$j.audits.'largest-contentful-paint'.displayValue
$j.audits.'total-blocking-time'.displayValue
$j.audits.'cumulative-layout-shift'.displayValue
$j.audits.'first-contentful-paint'.displayValue
$j.audits.'speed-index'.displayValue
$j.audits.'interactive'.displayValue
```

Für die Tiefenanalyse (größte Requests, unused JS, Mainthread, failing audits
je Kategorie): siehe [references/lighthouse-audits.md](references/lighthouse-audits.md).

**e) Edge mit dem Temp-Profil wieder killen** (nur diese Instanz, nicht den
normalen Browser des Users):

```powershell
Get-CimInstance Win32_Process -Filter "Name='msedge.exe'" |
  Where-Object { $_.CommandLine -like '*edge-lh*' } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
```

Wenn die Seite nicht öffentlich erreichbar ist: lokalen Dev-/Preview-Server
starten und dessen `localhost`-URL messen.

## Schritt 3, Repo-Tiefencheck (nur bei Repo-Quelle)

- **Bilder**: größte Dateien finden, Format prüfen. Rohe PNG/JPG ohne
  WebP/AVIF, fehlendes `loading="lazy"` (außer LCP-Bild), fehlende
  `width`/`height` (CLS-Risiko). Bei Next.js Static Export (`output: 'export'`)
  greift der `next/image`-Optimizer nicht, das ist oft der größte Hebel.
- **JS**: große Bundles, doppelte/unused Dependencies, Client-Components, die
  Server-Components sein könnten.
- **Belege**: jede Aussage mit `Datei:Zeile`.

```powershell
# Größte Assets (Bilder/Medien) im Repo
Get-ChildItem -Recurse -File -Include *.png,*.jpg,*.jpeg,*.gif,*.webp,*.avif,*.mp4,*.svg `
  -Path . -ErrorAction SilentlyContinue |
  Where-Object { $_.FullName -notmatch '\\node_modules\\|\\.next\\|\\dist\\|\\build\\' } |
  Sort-Object Length -Descending | Select-Object -First 15 Name, @{n='KB';e={[math]::Round($_.Length/1KB)}}, FullName
```

## Report-Format (Template)

```markdown
# Website-Audit: <Quelle>

**Quelle:** <URL und/oder Repo-Pfad> · **Datum:** <YYYY-MM-DD> · **Stack:** <Stack>
**Verdikt:** <ein Satz, der das Gesamtbild trifft>

## Lighthouse mobil (gemessen)
| Kategorie | Score | Ziel | Status |
|---|---|---|---|
| Performance | XX | >= 95 | ✅/⚠️/❌ |
| Accessibility | XX | >= 95 | ... |
| SEO | XX | >= 95 | ... |

## Core Web Vitals
| Metrik | Wert | Bewertung |
|---|---|---|
| LCP | x.x s | gut/grenzwertig/schlecht |
| TBT | xxx ms | ... |
| CLS | 0.xx | ... |
| FCP | x.x s | ... |
| Speed Index | x.x s | ... |
| TTI | x.x s | ... |

## Security & GEO/AEO
| Check | Status | Detail |
|---|---|---|
| HTTPS-Redirect / TLS | ✅/⚠️/❌ | ... |
| HSTS / CSP / X-Content-Type-Options | ... | fehlende Header nennen |
| llms.txt / AI-Crawler-Policy | ... | vorhanden? robots-Direktiven? |
| AI-Zitierfähigkeit (Entitäten/Antwortstruktur) | ... | ... |

## Schon stark
- <Punkt mit Beleg>

## Unter dem Massstab
- <Punkt mit Beleg/Datei:Zeile>

## Quick Wins
| Massnahme | Aufwand | Wirkung |
|---|---|---|
| <konkret> | S/M/L | hoch/mittel/niedrig |
(priorisiert nach Hebel, höchster Hebel zuerst)

## Groessere Massnahmen
- <strategisch, optional>

## Ads: Sinnvoll?   <!-- nur falls relevant, siehe unten -->
**Empfehlung:** ja / nein / erst wenn ...
- Vorbedingungen: <z.B. Conversion-Tracking, Landingpage, Rechtstexte>
- Budget-Rahmen: <grobe Monatsspanne>
- Erste 1-2 Schritte: <konkret>
```

### Abschnitt "Ads: Sinnvoll?", wann und wie

Nur einbauen, wenn der User danach fragt **oder** es eine Business-/Agentur-Seite
ist (Lead-Generierung relevant). Klare Empfehlung ja/nein/erst-wenn,
Vorbedingungen, grober Monatsbudget-Rahmen, 1-2 erste Schritte.

Guardrail: **keine Kaltakquise**. Search Ads sind Inbound (Nutzer sucht aktiv),
kein Konflikt. Meta/Display haben bei B2B meist schwachen Intent, eher
zurückhaltend empfehlen. Voraussetzung für jede Empfehlung "ja": die Seite
konvertiert überhaupt (klare CTA, Tracking, saubere Rechtstexte), sonst "erst
wenn".

## Abschluss

Nach dem Report fragen: **"Sollen die Quick Wins umgesetzt werden?"** Erst nach
expliziter Freigabe Änderungen vornehmen, dann nur die freigegebenen Punkte,
chirurgisch.

## Schritt 4, Selbst-Optimierung (Feedback-Loop)

Diese Skill verbessert sich nach jedem Lauf selbst. Ziel: konkrete Reibung, die
in diesem Lauf auftrat, beim nächsten Mal vermeiden.

**Während des Laufs ein Reibungs-Log mitführen** (im Kopf, kurz). Notiere nur
Konkretes, das schieflief:
- Befehl, der einen Fehler warf, plus die Korrektur, die funktioniert hat (z.B.
  anderer Edge-Pfad, Port 9222 belegt, anderer Lighthouse-Output-Dateiname).
- Schritt, der mehrere Anläufe oder manuelles Eingreifen brauchte.
- Vom User gewünschter Check, der noch nicht in der Checkliste stand.
- Falsche/leere Messwerte, fehlende Fallbacks, Umgebungs-Eigenheiten.

**Nach dem Report (und nach der Quick-Wins-Entscheidung) bewerten und handeln:**

- Gab es Reibung mit klarer, belegter Ursache und sicherer Korrektur, dann diese
  **eigenständig in die eigenen Skill-Dateien einarbeiten** (SKILL.md oder
  `references/*`). Beispiele: Edge-Pfad-Fallback ergänzen, belegten Port-Konflikt
  abfangen, fehlerhaften Befehl fixen, einen neuen wertvollen Check aufnehmen.
- Jede Änderung als datierten Eintrag in
  [CHANGELOG.md](CHANGELOG.md) anhängen (Datum, Auslöser, Änderung).
- Lief alles glatt, **nichts ändern**. Keine kosmetischen Edits.

**Guardrails (nicht verhandelbar):**

- Nur Dateien **im Skill-Ordner** ändern, niemals das auditierte Projekt.
- Edits chirurgisch und konservativ. Niemals die Sicherheitsregel "nur Analyse,
  keine Änderungen ohne Freigabe" aufweichen.
- Methodische oder mehrdeutige Verbesserungen (anderer Bewertungsmaßstab,
  zusätzliche Tools) **nicht** automatisch anwenden, sondern im Report unter
  "Vorschlag zur Skill-Verbesserung" listen und den User entscheiden lassen.
- Im Report einen Einzeiler ergänzen, falls die Skill sich selbst angepasst hat
  ("Skill aktualisiert: <was>, siehe CHANGELOG"), damit die Änderung sichtbar
  und reversibel bleibt.
