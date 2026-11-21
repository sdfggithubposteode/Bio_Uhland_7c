# BioLern – Interaktiver Lerntrainer (Klasse 7)

Mobilfreundliche Lern-Homepage zur Vorbereitung auf die Biologie-Arbeit
(KA 1). Reine HTML/CSS/JS-Datei – kein Server, keine Installation nötig.

## Inhalte

- **69 Quizfragen** zu den Klassenarbeits-Themen:
  Mikroskop, Bau von Zellen, Zellteilung & Gewebe,
  Organisationsstufen, Fotosynthese
- **14 Bildbeschriftungs-Aufgaben** (Drag & Drop, auch per Touch):
  Zellen, Blattquerschnitt, Mikroskop, Zellteilung, Zelltypen,
  Gewebe, Organisationsebenen, Biomoleküle, Fotosynthese
- Bildaufgaben kommen im Training anstelle einer Frage vor und
  lassen sich unten gezielt auswählen
- Fortschritt wird lokal im Browser gespeichert (`localStorage`)

## Nutzung

`index.html` im Browser öffnen – auf dem PC oder aufs Handy.
**Wichtig:** Die Bilder werden relativ aus dem Ordner `Bilder/`
geladen – beim Kopieren also immer `index.html` **und** den Ordner
`Bilder/` zusammen mitnehmen.

## Für Maintainer: Beschriftungen bearbeiten

Die Positionen der Beschriftungs-Kästchen und Linien werden mit dem
Tkinter-Editor gesetzt und gespeichert:

```bash
beschriftung_editor.bat   # oder: python beschriftung_editor.py
```

- Kästchen und rote Punkte per Drag & Drop positionieren
- `+ Kästchen` fügt eigene Begriffe hinzu, Doppelklick benennt um,
  Entf löscht das markierte Kästchen
- Positionen landen in `Bilder/beschriftungen.json`

Danach die HTML neu generieren:

```bash
python build_beschriftung.py
```

Das Skript schreibt die Bildverweise und Positionen in den
markierten `GENERATED-START/END`-Block der `index.html`.

## Struktur

| Pfad | Inhalt |
|---|---|
| `index.html` | komplette Lernseite (~70 KB, verweist auf `Bilder/`) |
| `beschriftung_editor.py` | Tkinter-Editor für Kästchen-/Linien-Positionen |
| `beschriftung_editor.bat` | Windows-Starter für den Editor |
| `build_beschriftung.py` | generiert den Bilddaten-Block in der HTML |
| `Bilder/` | Quellbilder (PNG), `beschriftungen.json`, Beschriftungs-Quellen (MD) |

## Lizenz

[GNU Affero General Public License v3.0 (AGPL-3.0)](LICENSE)
– Copyright (C) 2026 LuxUmbra

Kurz gesagt: Du darfst das Projekt frei nutzen, verändern und
weitergeben – abgeleitete Werke müssen aber ebenfalls unter der
AGPL quelloffen bleiben und den Hinweis auf den Urheber enthalten.
Das gilt auch, wenn eine geänderte Version nur über ein Netzwerk
angeboten wird.

## Unterstützen

Wenn dir der Trainer hilft, freue ich mich über eine freiwillige
Spende: <https://www.paypal.com/qrcodes/managed/6e439f00-2f95-4125-95b5-b2e2208af01f>
*(keine Nutzungsbedingung – das Projekt ist und bleibt frei)*
