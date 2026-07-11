# Lighthouse: Audit-Keys und Extraktion

Referenz für [SKILL.md](../SKILL.md), Schritt 2d. Voraussetzung: das JSON ist
geladen:

```powershell
$j = Get-Content "$env:TEMP\lh-report.report.json" -Raw | ConvertFrom-Json
```

## Core Web Vitals / Metriken

| Was | Audit-Key | Feld |
|---|---|---|
| LCP | `largest-contentful-paint` | `.displayValue` / `.numericValue` (ms) |
| Total Blocking Time | `total-blocking-time` | `.displayValue` |
| Cumulative Layout Shift | `cumulative-layout-shift` | `.displayValue` |
| First Contentful Paint | `first-contentful-paint` | `.displayValue` |
| Speed Index | `speed-index` | `.displayValue` |
| Time to Interactive | `interactive` | `.displayValue` |

Zugriff mit Punkt-Notation und Quotes wegen Bindestrich:
`$j.audits.'largest-contentful-paint'.numericValue`.

Richtwerte (mobil, gut/grenzwertig/schlecht): LCP <= 2.5s / <= 4.0s / >4.0s ·
TBT <= 200ms / <= 600ms / >600ms · CLS <= 0.1 / <= 0.25 / >0.25 ·
FCP <= 1.8s / <= 3.0s / >3.0s.

## Performance-Tiefenanalyse

**Größte Netzwerk-Requests** (Transfergröße, deckt schwere Bilder/JS auf):

```powershell
$j.audits.'network-requests'.details.items |
  Sort-Object transferSize -Descending | Select-Object -First 12 url,
  @{n='KB';e={[math]::Round($_.transferSize/1KB)}}, resourceType
```

**Ressourcen-Summe nach Typ** (Bilder vs. Script vs. Font Budget):

```powershell
$j.audits.'resource-summary'.details.items |
  Select-Object resourceType, requestCount,
  @{n='KB';e={[math]::Round($_.transferSize/1KB)}}
```

**Unused JavaScript** (Einsparpotenzial in KB):

```powershell
$j.audits.'unused-javascript'.details.items |
  Sort-Object wastedBytes -Descending | Select-Object -First 10 url,
  @{n='WastedKB';e={[math]::Round($_.wastedBytes/1KB)}}
```

**Mainthread-Arbeit** (was blockiert, Gruppen nach Dauer):

```powershell
$j.audits.'mainthread-work-breakdown'.details.items |
  Sort-Object duration -Descending | Select-Object groupLabel,
  @{n='ms';e={[math]::Round($_.duration)}}
```

Weitere nützliche Performance-Audit-Keys (gleiche `.details.items`-Struktur):
`modern-image-formats` (WebP/AVIF-Potenzial), `uses-responsive-images`,
`offscreen-images` (fehlendes lazy-loading), `uses-optimized-images`,
`unminified-javascript`, `unused-css-rules`, `render-blocking-resources`,
`uses-text-compression`, `efficient-animated-content`, `legacy-javascript`,
`uses-rel-preconnect`, `font-display`, `bootup-time`.

## Failing Audits je Kategorie

Alle nicht bestandenen Audits einer Kategorie auflisten (score < 1, ohne reine
Info-Audits):

```powershell
function Get-FailingAudits($cat) {
  $j.categories.$cat.auditRefs |
    Where-Object { $a = $j.audits.($_.id); $a.score -ne $null -and $a.score -lt 1 } |
    ForEach-Object { $j.audits.($_.id) } |
    Select-Object id, title, @{n='score';e={$_.score}}, displayValue |
    Sort-Object score
}
Get-FailingAudits 'performance'
Get-FailingAudits 'accessibility'
Get-FailingAudits 'seo'
```

Accessibility-Failures sind oft Quick Wins: `color-contrast`, `image-alt`,
`label`, `link-name`, `button-name`, `html-has-lang`, `meta-viewport`.
SEO-Failures: `document-title`, `meta-description`, `http-status-code`,
`crawlable-anchors`, `robots-txt`, `canonical`, `structured-data`.

## Hinweise

- `--throttling-method=simulate` (Lighthouse-Default) liefert reproduzierbare
  Lab-Werte ohne echte Netzwerk-Drosselung. Bei stark schwankenden Scores 2-3
  Läufe machen und den Median nehmen.
- `score` ist 0..1, im Report mit `* 100` runden.
- Manche Audits haben `score = $null` (manual/informative/notApplicable), die
  beim Filtern ausschließen (siehe Funktion oben).
- **Neuere Lighthouse (LH 12+, ab Next 16 via npx) nutzt das Insights-Format**:
  die Hebel heißen `*-insight` (`render-blocking-insight`, `image-delivery-insight`,
  `network-dependency-tree-insight`, `legacy-javascript-insight`,
  `cache-insight`, `forced-reflow-insight`). Die klassischen
  `render-blocking-resources` und das element-genaue
  `largest-contentful-paint-element` sind dann oft leer (`details.items` = 0).
  Verlasse dich auf die `Get-FailingAudits`-Funktion oben (zeigt die echten
  Insight-Keys) und für das LCP-Element auf den HTML-Report `...report.html`.
- **Cache-Hinweise bei lokalem Static-Serve ignorieren**: `npx serve` setzt kein
  `Cache-Control`, daher meldet `cache-insight` große "savings". Auf
  Produktions-nginx mit immutable-Caching für `/_next/static` ist das gegenstandslos.
