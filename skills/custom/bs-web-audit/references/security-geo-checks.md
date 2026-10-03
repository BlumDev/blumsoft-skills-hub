# Security-Header, TLS und GEO/AEO

Referenz für [SKILL.md](../SKILL.md), Checklistenpunkte 10-12. Befehle in
**PowerShell** (pwsh 7+, `-SkipHttpErrorCheck` verfügbar). `<URL>` ersetzen.

Stolperfallen bei Ad-hoc-Loops über mehrere URLs/Hosts:
- Ein `foreach ($x in ...) { ... }`-**Statement** kann nicht direkt gepipet
  werden (`| Format-Table` -> ParserError "empty pipe element"). Entweder in
  `$(foreach ...)` wrappen oder gleich `... | ForEach-Object { ... }` nutzen.
- `$home` ist eine reservierte (read-only) Automatic Variable, nicht als
  Schleifen-/Ergebnisvariable verwenden.
- pwsh 7 dekomprimiert Responses automatisch und **entfernt dabei
  `Content-Encoding`** aus `$resp.Headers`. Kompression (gzip/brotli) daher mit
  `curl.exe -sI -H "Accept-Encoding: gzip, br" <URL>` prüfen, nie über
  Invoke-WebRequest beurteilen.

## Security-Header prüfen

```powershell
$resp = Invoke-WebRequest '<URL>' -UseBasicParsing
$h = $resp.Headers
'Strict-Transport-Security','Content-Security-Policy','X-Content-Type-Options',
'X-Frame-Options','Referrer-Policy','Permissions-Policy' |
  ForEach-Object { [pscustomobject]@{ Header = $_; Wert = (($h[$_]) -join '; ') } }
# Banner-Leaks (sollten fehlen oder nichtssagend sein):
$h['Server']; $h['X-Powered-By']
```

Bewertung:
- **HSTS** (`Strict-Transport-Security`): vorhanden, `max-age` >= 15552000 (180 Tage).
- **CSP**: vorhanden. Ersetzt `X-Frame-Options` via `frame-ancestors`. Fehlt sie
  ganz, ist das ein Befund (Medium), aber selten ein Quick Win (CSP einführen ist
  M/L).
- **X-Content-Type-Options**: `nosniff`. Quick Win, wenn es fehlt.
- **Referrer-Policy** / **Permissions-Policy**: vorhanden und restriktiv.
- **Server / X-Powered-By**: keine Versionsnummern preisgeben.

## HTTP -> HTTPS-Redirect und TLS

```powershell
$httpUrl = '<URL>' -replace '^https://','http://'
# -ErrorAction SilentlyContinue unterdrückt die rote "maximum redirection exceeded"-
# Meldung; der 30x-Response landet trotzdem in $r (Fehler ist nicht-terminierend).
$r = Invoke-WebRequest $httpUrl -MaximumRedirection 0 -SkipHttpErrorCheck -UseBasicParsing -ErrorAction SilentlyContinue
[pscustomobject]@{ Status = $r.StatusCode; Location = $r.Headers['Location'] }
# Erwartung: 301/308 auf die https-Variante (302 ist ok, aber 301 wäre korrekter).
```

Mixed Content wird von Lighthouse als Audit `is-on-https` gemeldet
(`$j.audits.'is-on-https'`). Zertifikatsgültigkeit zeigt der Browser; bei
Verdacht im Report vermerken, nicht raten.

## GEO/AEO: AI-Sichtbarkeit

### llms.txt und AI-Crawler-Policy

```powershell
$root = ([uri]'<URL>').Scheme + '://' + ([uri]'<URL>').Authority
# llms.txt vorhanden?
(Invoke-WebRequest "$root/llms.txt" -SkipHttpErrorCheck -UseBasicParsing).StatusCode
# robots.txt: werden AI-Crawler bewusst behandelt?
$robots = (Invoke-WebRequest "$root/robots.txt" -SkipHttpErrorCheck -UseBasicParsing).Content
'GPTBot','OAI-SearchBot','ChatGPT-User','ClaudeBot','anthropic-ai',
'PerplexityBot','Google-Extended','CCBot' | ForEach-Object {
  $hit = $robots -match "(?im)User-agent:\s*$_"
  [pscustomobject]@{ Crawler = $_; ImRobots = if ($hit) {'referenziert'} else {'nicht (Default = erlaubt)'} }
}
```

Einordnung:
- **`llms.txt`** (Markdown-Index der wichtigsten Inhalte für LLMs) ist optional,
  aber ein günstiges Signal. Fehlt = Quick Win (S), wenn AI-Traffic ein Ziel ist.
- **AI-Crawler in robots.txt**: bewusste Entscheidung ist gut. Wer in AI-Antworten
  zitiert werden will, sollte GPTBot/OAI-SearchBot/ClaudeBot/PerplexityBot **nicht**
  blocken. Wer Inhalte schützen will, blockt bewusst. Im Report die Absicht
  hinterfragen, nicht pauschal "erlauben" empfehlen.

### Zitierfähigkeit (Antwortmaschinen-Tauglichkeit)

Heuristisch am Seiteninhalt bewerten (HTML lesen):
- **Entitäten klar**: `Organization`-Schema mit `name`, `url`, `sameAs`
  (Verlinkung zu Profilen), `LocalBusiness`/`ProfessionalService` bei lokalem
  Bezug. Bei Artikeln `Article` mit `author` und `datePublished`.
- **Antwortbare Struktur**: konkrete Fragen als Überschriften, knappe
  Antwort-zuerst-Absätze, Listen/Tabellen, definierte Begriffe. LLMs zitieren
  extrahierbare, eigenständige Aussagen leichter als Marketing-Prosa.
- **Belegte Fakten**: Zahlen, Daten, Quellenangaben statt vager Claims.
- **E-E-A-T-Signale**: benannte Autoren, Über-uns, Kontakt/Impressum (Punkt 7),
  sichtbare Aktualität (Datum). Stärkt Vertrauen bei AI- und klassischem Ranking.
- **FAQPage/HowTo-Schema** wo inhaltlich passend, deckt sowohl Rich Results als
  auch AI-Antworten ab.

## Broken Links (Checklistenpunkt 12)

Schneller Crawl der Startseiten-Links, HEAD auf jeden, Fehler auflisten:

```powershell
$base = '<URL>'
$root = ([uri]$base).Scheme + '://' + ([uri]$base).Authority
$links = (Invoke-WebRequest $base -UseBasicParsing).Links.href |
  Where-Object { $_ } |
  ForEach-Object { if ($_ -match '^https?://') { $_ } elseif ($_ -match '^/') { $root + $_ } } |
  Sort-Object -Unique
$links | ForEach-Object {
  $u = $_
  try { $s = (Invoke-WebRequest $u -Method Head -SkipHttpErrorCheck -TimeoutSec 8 -UseBasicParsing).StatusCode }
  catch { $s = $null }
  [pscustomobject]@{ Status = $s; Url = $u }
} | Where-Object { -not $_.Status -or $_.Status -ge 400 }
```

Liefert nur die kaputten/fehlerhaften Links. Redirect-Ketten (mehrfach 30x)
separat vermerken, sie kosten Performance. Dritt-Skripte (Tracking/Fonts/Widgets)
aus dem Lighthouse-Audit `network-requests` (Fremd-Domains) ableiten und als
Performance- plus Consent-Risiko bewerten.
