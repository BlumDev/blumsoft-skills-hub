# Diagramm-Muster

Fünf Muster als Inline-SVG. Kopieren, Beschriftung und Kastenanzahl anpassen, fertig. Keine Bibliothek, keine externe Datei, funktioniert offline und im Druck.

**Warum SVG und nicht Mermaid:** Eine Bibliothek müsste eingebettet werden (über ein Megabyte) oder von außen laden, dann ist das Dokument nicht mehr offline lauffähig. Inline-SVG kostet nichts und lässt sich exakt setzen.

## Regeln für jedes Diagramm

- **Keine festen Maße am `<svg>`**, nur `viewBox` plus `style="width:100%;max-width:…"`. Sonst bricht es auf schmalen Fenstern.
- **Farben ausschließlich über die `d-*`-Klassen** aus dem Gerüst. Nie `fill="#333"`. Sonst verschwindet das Diagramm im Dunkelmodus.
- **Text nie kleiner als 11px** im viewBox-Maßstab. Was im Browser knapp lesbar ist, ist im Druck weg.
- **Jedes Muster bringt seine `defs` mit** (die Pfeilspitzen). Beim Kopieren mitnehmen, sonst fehlen die Spitzen und niemand sieht die Richtung. Mehrere gleiche `defs` in einem Dokument stören nicht, doppelte IDs mit identischem Inhalt sind unkritisch.
- **Ein Diagramm ersetzt Text, es begleitet ihn nicht.** Wenn daneben derselbe Ablauf nochmal in Prosa steht, ist eines von beidem überflüssig.

## Wann welches Muster

| Frage, die der Leser hat | Muster |
|---|---|
| In welcher Reihenfolge passiert was? | 1 Ablaufkette |
| Wovon hängt es ab, wie es weitergeht? | 2 Verzweigung |
| Was passiert wo? Was wird übergeben? | 3 Zwei Systeme |
| Was hängt womit zusammen? | 4 Objektbeziehungen |
| Was ist besser, was schlechter? | 5 Stufenleiter |

---

## Muster 1: Ablaufkette

Vier Schritte nacheinander. Für Prozessketten, Verarbeitungsreihenfolgen, Vorgehensschritte.

```html
<figure class="fig">
<svg viewBox="0 0 780 90" style="width:100%;max-width:780px" role="img" aria-label="Ablauf in vier Schritten">
  <defs>
    <marker id="ar" viewBox="0 0 10 8" refX="9" refY="4" markerWidth="8" markerHeight="7" orient="auto">
      <path d="M0,0 L10,4 L0,8 z" class="d-fill-line"/>
    </marker>
    <marker id="ar-a" viewBox="0 0 10 8" refX="9" refY="4" markerWidth="8" markerHeight="7" orient="auto">
      <path d="M0,0 L10,4 L0,8 z" class="d-fill-accent"/>
    </marker>
  </defs>

  <rect x="2"   y="20" width="170" height="50" rx="6" class="d-box"/>
  <text x="87"  y="42" class="d-t-b" text-anchor="middle">Antrag</text>
  <text x="87"  y="58" class="d-t-s" text-anchor="middle">CRM</text>

  <rect x="204" y="20" width="170" height="50" rx="6" class="d-box"/>
  <text x="289" y="42" class="d-t-b" text-anchor="middle">Bewertung</text>
  <text x="289" y="58" class="d-t-s" text-anchor="middle">CRM</text>

  <rect x="406" y="20" width="170" height="50" rx="6" class="d-box-a"/>
  <text x="491" y="42" class="d-t-b" text-anchor="middle">Vereinbarung</text>
  <text x="491" y="58" class="d-t-s" text-anchor="middle">erzeugt Obligo</text>

  <rect x="608" y="20" width="170" height="50" rx="6" class="d-box"/>
  <text x="693" y="42" class="d-t-b" text-anchor="middle">Auszahlung</text>
  <text x="693" y="58" class="d-t-s" text-anchor="middle">ERP</text>

  <path d="M172,45 L200,45" class="d-line" marker-end="url(#ar)"/>
  <path d="M374,45 L402,45" class="d-line" marker-end="url(#ar)"/>
  <path d="M576,45 L604,45" class="d-line" marker-end="url(#ar)"/>
</svg>
<figcaption>Der hervorgehobene Schritt ist der, an dem der Systemwechsel passiert.</figcaption>
</figure>
```

Rechnung für andere Schrittzahlen: Kastenbreite `b`, Lücke 30, linker Rand 2. Kasten `i` (ab 0) beginnt bei `2 + i*(b+30)`. Bei fünf Kästen auf 780 Breite ist `b = 132`.

---

## Muster 2: Verzweigung

Eine Prüfung, zwei Wege. Für Entscheidungen, Fehlerpfade, Fallunterscheidungen.

```html
<figure class="fig">
<svg viewBox="0 0 620 260" style="width:100%;max-width:620px" role="img" aria-label="Verzweigung nach einer Prüfung">
  <defs>
    <marker id="ar" viewBox="0 0 10 8" refX="9" refY="4" markerWidth="8" markerHeight="7" orient="auto">
      <path d="M0,0 L10,4 L0,8 z" class="d-fill-line"/>
    </marker>
    <marker id="ar-a" viewBox="0 0 10 8" refX="9" refY="4" markerWidth="8" markerHeight="7" orient="auto">
      <path d="M0,0 L10,4 L0,8 z" class="d-fill-accent"/>
    </marker>
  </defs>
  <rect x="215" y="4" width="190" height="42" rx="6" class="d-box"/>
  <text x="310" y="30" class="d-t-b" text-anchor="middle">Fehler gemeldet</text>

  <path d="M310,46 L310,74" class="d-line" marker-end="url(#ar)"/>

  <path d="M310,78 L430,124 L310,170 L190,124 z" class="d-box-a"/>
  <text x="310" y="120" class="d-t-b" text-anchor="middle">Fundstelle</text>
  <text x="310" y="136" class="d-t-b" text-anchor="middle">bekannt?</text>

  <path d="M190,124 L110,124 L110,196" class="d-line" marker-end="url(#ar)"/>
  <text x="150" y="116" class="d-t-a" text-anchor="middle">NEIN</text>
  <path d="M430,124 L510,124 L510,196" class="d-line" marker-end="url(#ar)"/>
  <text x="470" y="116" class="d-t-a" text-anchor="middle">JA</text>

  <rect x="15"  y="200" width="190" height="52" rx="6" class="d-box-warn"/>
  <text x="110" y="222" class="d-t-b" text-anchor="middle">Protokolle lesen</text>
  <text x="110" y="238" class="d-t-s" text-anchor="middle">Dump, Joblog, Trace</text>

  <rect x="415" y="200" width="190" height="52" rx="6" class="d-box-ok"/>
  <text x="510" y="222" class="d-t-b" text-anchor="middle">Quelltext prüfen</text>
  <text x="510" y="238" class="d-t-s" text-anchor="middle">Review</text>
</svg>
<figcaption>Die Raute ist die einzige Stelle, an der entschieden wird.</figcaption>
</figure>
```

Die Raute ist ein Pfad, kein Rechteck: `M cx,oben L rechts,cy L cx,unten L links,cy z`.

---

## Muster 3: Zwei Systeme mit Übergabe

Zwei Bereiche nebeneinander, dazwischen die Übergabestellen. Für Schnittstellen, Systemgrenzen, Verantwortungswechsel.

```html
<figure class="fig">
<svg viewBox="0 0 780 300" style="width:100%;max-width:780px" role="img" aria-label="Zwei Systeme mit zwei Übergaben">
  <defs>
    <marker id="ar" viewBox="0 0 10 8" refX="9" refY="4" markerWidth="8" markerHeight="7" orient="auto">
      <path d="M0,0 L10,4 L0,8 z" class="d-fill-line"/>
    </marker>
    <marker id="ar-a" viewBox="0 0 10 8" refX="9" refY="4" markerWidth="8" markerHeight="7" orient="auto">
      <path d="M0,0 L10,4 L0,8 z" class="d-fill-accent"/>
    </marker>
  </defs>
  <rect x="2"   y="24" width="330" height="228" rx="8" class="d-box" opacity="0.55"/>
  <text x="167" y="16" class="d-t-a" text-anchor="middle">CRM</text>

  <rect x="448" y="24" width="330" height="228" rx="8" class="d-box" opacity="0.55"/>
  <text x="613" y="16" class="d-t-a" text-anchor="middle">ERP</text>

  <rect x="26" y="44"  width="282" height="42" rx="6" class="d-box"/>
  <text x="167" y="70" class="d-t" text-anchor="middle">Programm und Antrag</text>
  <rect x="26" y="100" width="282" height="42" rx="6" class="d-box"/>
  <text x="167" y="126" class="d-t" text-anchor="middle">Bewertung</text>
  <rect x="26" y="156" width="282" height="42" rx="6" class="d-box-a"/>
  <text x="167" y="182" class="d-t-b" text-anchor="middle">Vereinbarung</text>

  <rect x="472" y="100" width="282" height="42" rx="6" class="d-box-a"/>
  <text x="613" y="126" class="d-t-b" text-anchor="middle">Obligo</text>
  <rect x="472" y="156" width="282" height="42" rx="6" class="d-box"/>
  <text x="613" y="182" class="d-t" text-anchor="middle">Mittelabruf</text>
  <rect x="472" y="212" width="282" height="28" rx="6" class="d-box"/>
  <text x="613" y="231" class="d-t" text-anchor="middle">Auszahlung</text>

  <path d="M308,168 L400,168 L400,121 L468,121" class="d-line-a" marker-end="url(#ar-a)"/>
  <text x="408" y="145" class="d-t-a">1</text>

  <path d="M613,240 L613,278 L167,278 L167,202" class="d-dash" marker-end="url(#ar)"/>
  <text x="390" y="270" class="d-t-a" text-anchor="middle">2 Ist-Fortschreibung</text>
</svg>
<figcaption>1 ist die Erzeugung des Obligos, 2 die Ist-Fortschreibung zurück. Das sind die beiden Übergabestellen. Bei einem Fehler dort werden immer beide Enden getrennt geprüft.</figcaption>
</figure>
```

Der gestrichelte Rückweg (`d-dash`) unterscheidet Rückmeldung von Hauptfluss.

---

## Muster 4: Objektbeziehungen

Was hängt womit zusammen, mit Kardinalität. Für Datenmodelle, Belegketten, Abhängigkeiten.

```html
<figure class="fig">
<svg viewBox="0 0 700 230" style="width:100%;max-width:700px" role="img" aria-label="Beziehungen zwischen vier Objekten">
  <defs>
    <marker id="ar" viewBox="0 0 10 8" refX="9" refY="4" markerWidth="8" markerHeight="7" orient="auto">
      <path d="M0,0 L10,4 L0,8 z" class="d-fill-line"/>
    </marker>
    <marker id="ar-a" viewBox="0 0 10 8" refX="9" refY="4" markerWidth="8" markerHeight="7" orient="auto">
      <path d="M0,0 L10,4 L0,8 z" class="d-fill-accent"/>
    </marker>
  </defs>
  <rect x="250" y="4"   width="200" height="46" rx="6" class="d-box-a"/>
  <text x="350" y="24" class="d-t-b" text-anchor="middle">Vereinbarung</text>
  <text x="350" y="40" class="d-t-s" text-anchor="middle">Kopf mit Gesamtbetrag</text>

  <rect x="30"  y="106" width="200" height="46" rx="6" class="d-box"/>
  <text x="130" y="126" class="d-t-b" text-anchor="middle">Position</text>
  <text x="130" y="142" class="d-t-s" text-anchor="middle">je Zahlungsart</text>

  <rect x="470" y="106" width="200" height="46" rx="6" class="d-box"/>
  <text x="570" y="126" class="d-t-b" text-anchor="middle">Änderungsantrag</text>
  <text x="570" y="142" class="d-t-s" text-anchor="middle">nachträglich</text>

  <rect x="250" y="180" width="200" height="46" rx="6" class="d-box"/>
  <text x="350" y="200" class="d-t-b" text-anchor="middle">Obligo</text>
  <text x="350" y="216" class="d-t-s" text-anchor="middle">im ERP</text>

  <path d="M290,50 L160,102" class="d-line" marker-end="url(#ar)"/>
  <text x="205" y="70" class="d-t-s" text-anchor="middle">1 : n</text>

  <path d="M410,50 L540,102" class="d-line" marker-end="url(#ar)"/>
  <text x="495" y="70" class="d-t-s" text-anchor="middle">1 : n</text>

  <path d="M350,50 L350,176" class="d-line-a" marker-end="url(#ar-a)"/>
  <text x="380" y="118" class="d-t-a">erzeugt</text>
</svg>
<figcaption>Kardinalitäten an der Linie, nicht am Kasten.</figcaption>
</figure>
```

Beschriftete Linien immer mittig neben der Linie, nie darauf. Ein `text` mit `text-anchor="middle"` auf dem Linienmittelpunkt reicht.

---

## Muster 5: Stufenleiter

Rangfolge von oben nach unten, mit abnehmender Güte. Für Entscheidungsleitern, Eskalationsstufen, Präferenzreihenfolgen.

```html
<figure class="fig">
<svg viewBox="0 0 700 240" style="width:100%;max-width:700px" role="img" aria-label="Fünf Stufen von oben nach unten">
  <defs>
    <marker id="ar" viewBox="0 0 10 8" refX="9" refY="4" markerWidth="8" markerHeight="7" orient="auto">
      <path d="M0,0 L10,4 L0,8 z" class="d-fill-line"/>
    </marker>
    <marker id="ar-a" viewBox="0 0 10 8" refX="9" refY="4" markerWidth="8" markerHeight="7" orient="auto">
      <path d="M0,0 L10,4 L0,8 z" class="d-fill-accent"/>
    </marker>
  </defs>
  <rect x="2"   y="4"   width="560" height="38" rx="5" class="d-box-ok"/>
  <text x="20"  y="28" class="d-t-b">1 Customizing</text>
  <text x="552" y="28" class="d-t-s" text-anchor="end">keine Entwicklung</text>

  <rect x="22"  y="50"  width="540" height="38" rx="5" class="d-box-ok"/>
  <text x="40"  y="74" class="d-t-b">2 Freigegebene Schnittstelle</text>
  <text x="552" y="74" class="d-t-s" text-anchor="end">upgradefest</text>

  <rect x="42"  y="96"  width="520" height="38" rx="5" class="d-box"/>
  <text x="60"  y="120" class="d-t-b">3 BAdI oder Enhancement Spot</text>
  <text x="552" y="120" class="d-t-s" text-anchor="end">vorgesehen</text>

  <rect x="62"  y="142" width="500" height="38" rx="5" class="d-box-warn"/>
  <text x="80"  y="166" class="d-t-b">4 Implizite Erweiterung</text>
  <text x="552" y="166" class="d-t-s" text-anchor="end">fragil</text>

  <rect x="82"  y="188" width="480" height="38" rx="5" class="d-box-warn"/>
  <text x="100" y="212" class="d-t-b">5 Modifikation</text>
  <text x="552" y="212" class="d-t-s" text-anchor="end">praktisch nie</text>

  <path d="M592,10 L592,220" class="d-line" marker-end="url(#ar)"/>
  <text x="608" y="118" class="d-t-s">schlechter</text>
</svg>
<figcaption>Die Einrückung zeigt die Rangfolge, die Farbe die Empfehlung.</figcaption>
</figure>
```

Einrückung je Stufe 20px, Breite entsprechend 20px kürzer. Grün für empfohlen, neutral für vertretbar, gelb für letzte Wahl.

---

## Prüfung vor dem Ausliefern

1. **Screenshot ziehen** mit `node ~/.claude/scripts/shot.js <datei> -o bild.png` und ansehen. Ein Diagramm, das nur im Kopf stimmt, ist nicht geprüft.
2. **Dunkelmodus prüfen**: Taste T im Dokument, dann erneut ansehen. Hartkodierte Farben fallen hier auf.
3. **Schmales Fenster prüfen**: `--viewport 420x900`. Läuft das SVG über, fehlt `max-width`.
4. **Überlappende Beschriftung** ist der häufigste Fehler. Text, der über eine Linie oder aus dem Kasten läuft, macht das ganze Diagramm wertlos.
