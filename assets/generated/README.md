# Generierte Assets

Alle Dateien in diesem Ordner sind am 2026-08-20 mit Codex (Modell `gpt-5.6-sol`) über das ai-router-Gate erzeugt worden, die SVGs im Textmodus, das PNG im Bildmodus. Palette: Akzent `#2563eb`, dunkler Akzent `#1d4ed8`, Text `#1f2933`, Grau `#6b7280`, Rahmen `#e5e7eb`, Hintergrund `#f7f8fa`, Grün `#16a34a`, passend zu den anderen BlumSoft-Repos.

## Icons (`icons/`)

Zehn Strich-Icons für die Bausteine und Kommandos des Hub, alle mit `viewBox="0 0 24 24"`, `fill="none"`, `stroke="currentColor"`, `stroke-width="1.5"`, ohne `id`, ohne `defs`, ohne externe Referenzen. Sichtgeprüft bei 48px und 20px.

`skill.svg` steht für einen kanonischen Skill-Ordner, `registry.svg` für die Registry, `bundle.svg` für eine kuratierte Gruppe, `profile.svg` für eine Profil-Vorauswahl (Standard `freelancer-fullstack`). Die Tooling-Schritte decken `validate.svg`, `resolve.svg`, `sync.svg`, `import.svg` und `archive.svg` ab, `target.svg` steht für ein Sync-Ziel. Gedacht für Doku-Seiten, das Onboarding und eine spätere Statusübersicht.

## Diagramm

`flow.svg` zeichnet den Bundle-first-Ablauf nach: `skills/` als Quelle der Wahrheit (kanonische Ordner, Registry, Archive-Plan), daraus `bundles/` und `profiles/`, in der Mitte die PowerShell-Kette `validate.ps1`, `resolve.ps1`, `sync.ps1`, `import.ps1` plus `archive-report.ps1`, rechts die fünf Ziele claude, codex, cursor, antigravity und vscode-copilot mit dem Vermerk, dass nur vscode-copilot projektlokal ist, dazu die optionalen antigravity workflows. Der Rückweg über `import.ps1` ist eingezeichnet. Kleiner Schönheitsfehler im Rohergebnis: die gedrehte Beschriftung "Rückweg" liegt sehr dicht an der `profiles/`-Box, inhaltlich stimmt das Bild aber.

## Favicon und Empty-State

`favicon.svg` ist ein quadratisches Signet (32x32): ein zentraler Block, der an drei Ziele verteilt, also genau das Prinzip des Repos. Bei 16px lesbar.

`empty-state.svg` passt zum Zustand "noch kein Bundle ausgewählt": leere Kacheln neben einer gestrichelten Ablagefläche, dazu eine blaue Kachel, die auf ihren Platz wartet. Ohne Text, die Bedeutung steckt im `aria-label`.

## Bild

`skills-hub-og.png` (16:9) zeigt abstrakt einen zentralen Kachelspeicher, aus dem vier Bänder unterschiedliche Teilmengen an vier verschiedene Ziele tragen. Gedacht als Open-Graph-Bild oder Titelbild der Doku. Kein Text im Bild.
