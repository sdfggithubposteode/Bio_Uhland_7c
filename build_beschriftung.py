"""Überträgt die Positionen aus Bilder/beschriftungen.json in die HTML-Datei.

Ersetzt den Block zwischen GENERATED-START/END in Bio_Lerntrainer_KA.html.
Nach Änderungen im beschriftung_editor.py einfach erneut ausführen:
    python build_beschriftung.py
"""

import json
import os
import re
from urllib.parse import quote

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "Bilder", "beschriftungen.json")
HTML_FILE = os.path.join(BASE, "index.html")

META = {
    "Schematische Tierzelle mit Organellen.png": {
        "key": "tierzelle",
        "name": "Tierzelle",
        "decoys": ["Zellwand", "Chloroplast", "Vakuole"],
    },
    "Dreidimensionale Pflanzenzelle mit Organellen.png": {
        "key": "pflanze3d",
        "name": "Pflanzenzelle (3D)",
        "decoys": ["Spaltöffnung", "Kutikula", "Blattader"],
    },
    "Pflanzenzelle im Querschnitt.png": {
        "key": "pflanzelm",
        "name": "Pflanzenzelle (LM)",
        "decoys": ["Kernmembran", "Vakuolenmembran", "Mitochondrium"],
    },
    "Detaillierter Querschnitt eines Blattes.png": {
        "key": "blatt",
        "name": "Blattquerschnitt",
        "decoys": ["Zellkern", "Mitochondrium", "Vakuole"],
    },
    "Realistisches Mikroskop auf weißem Hintergrund.png": {
        "key": "mikroskop",
        "name": "Mikroskop",
        "decoys": ["Objektträger", "Deckgläschen", "Kondensor"],
    },
    "zeilung_tiere_zelle.png": {
        "key": "zellteilung_tiere",
        "name": "Zellteilung (Tier)",
        "decoys": ["Erbsubstanz", "Stammzelle"],
    },
    "Verschiedene Zelltypen im Überblick.png": {
        "key": "zelltypen",
        "name": "Zelltypen (Tier)",
        "decoys": ["Chloroplast", "Hautzelle", "Zellkern"],
    },
    "Pflanzenzelltypen und Gewebestrukturen.png": {
        "key": "pflanzenzelltypen",
        "name": "Zelltypen (Pflanze)",
        "decoys": ["Nervenzelle", "Muskelzelle"],
    },
    "Histologisches Vierfachbild unter dem Mikroskop(1).png": {
        "key": "gewebe",
        "name": "Gewebe",
        "decoys": ["Nervengewebe", "Bindegewebe", "Festigungsgewebe"],
    },
    "Biomoleküle_ Bausteine und Beispiele.png": {
        "key": "biomolekuele",
        "name": "Biomoleküle",
        "decoys": ["Vitamine", "Mineralstoffe", "Laktose"],
    },
    "Botanische Infografik zur Photosynthese.png": {
        "key": "fotosynthese",
        "name": "Fotosynthese",
        "decoys": ["Stickstoff", "Chlorophyll", "Humus"],
    },
    "Fünf botanische Lehrillustrationen.png": {
        "key": "orgstufen_pflanze",
        "name": "Org.-Stufen (Pflanze)",
        "decoys": ["Wurzel", "Zellmembran", "Samen"],
    },
    "Pflanzenzellteilung und Wachstum in sechs Stadien.png": {
        "key": "zellteilung_pflanze",
        "name": "Zellteilung (Pflanze)",
        "decoys": ["Zellatmung", "Keimung", "Chloroplast"],
    },
}

# Spalten-Übung ohne Linien: je Spalte [Stufe, Beispiel, Erklärung]
ORGA = {
    "file": "Biologische Organisationsebenen von Zelle bis Mensch_zugeschnitten.png",
    "key": "orga",
    "name": "Organisationsebenen",
    "columns": [
        ["Zelle", "Darmzelle",
         "Kleinste lebende Baueinheit des Körpers. Eine Darmzelle hilft dabei, Nährstoffe aufzunehmen."],
        ["Gewebe", "Darmschleimhaut / Darmepithel",
         "Viele ähnliche Zellen arbeiten zusammen und erfüllen eine gemeinsame Aufgabe. Die Darmschleimhaut ist an der Aufnahme von Nährstoffen beteiligt."],
        ["Organ", "Dünndarm",
         "Ein Organ besteht aus verschiedenen Geweben. Im Dünndarm wird Nahrung weiter verdaut und ein großer Teil der Nährstoffe aufgenommen."],
        ["Organsystem", "Verdauungssystem",
         "Mehrere Organe arbeiten zusammen, z. B. Magen und Darm. Ihre gemeinsame Aufgabe ist die Verdauung der Nahrung und die Aufnahme von Nährstoffen."],
        ["Organismus", "Mensch",
         "Ein vollständiges Lebewesen, dessen Organsysteme zusammenarbeiten."],
    ],
    "decoys": ["Zellkern", "Magen", "Nervensystem"],
}


def img_src(fname):
    """Relativer Bildpfad – der Ordner Bilder/ muss neben der HTML liegen."""
    return "Bilder/" + quote(fname)


def normalize_boxes(labels):
    """Gibt allen Kästchen eines Bildes dieselbe Größe (zentriert auf der
    bisherigen Mitte), damit die Wortlänge nicht erraten werden kann."""
    w = max(lb["box"]["w"] for lb in labels)
    h = max(lb["box"]["h"] for lb in labels)
    for lb in labels:
        b = lb["box"]
        b["x"] = round(b["x"] + b["w"] / 2 - w / 2)
        b["y"] = round(b["y"] + b["h"] / 2 - h / 2)
        b["w"], b["h"] = w, h


def crop_rect(labels, rect, canvas):
    ix, iy, iw, ih = rect["x"], rect["y"], rect["w"], rect["h"]
    x0, y0, x1, y1 = ix, iy, ix + iw, iy + ih
    for lb in labels:
        b = lb["box"]
        x0 = min(x0, b["x"]); y0 = min(y0, b["y"])
        x1 = max(x1, b["x"] + b["w"]); y1 = max(y1, b["y"] + b["h"])
    x0 = max(0, x0 - 30); y0 = max(0, y0 - 30)
    x1 = min(canvas["width"], x1 + 30); y1 = min(canvas["height"], y1 + 30)
    return {"x": round(x0), "y": round(y0), "w": round(x1 - x0), "h": round(y1 - y0)}


def main():
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)

    imgs = []
    for fname, meta in META.items():
        if fname not in data:
            print(f"Überspringe (noch keine Positionen): {meta['name']}")
            continue
        e = data[fname]
        labels = [{"text": lb["text"], "box": dict(lb["box"]),
                   "point": dict(lb["point"])} for lb in e["labels"]]
        normalize_boxes(labels)
        imgs.append({
            "key": meta["key"],
            "name": meta["name"],
            "src": img_src(fname),
            "crop": crop_rect(labels, e["imageRect"], e["canvas"]),
            "imageRect": e["imageRect"],
            "labels": labels,
            "targets": [lb["text"] for lb in labels],
            "decoys": meta["decoys"],
        })

    imgs.append({
        "key": ORGA["key"],
        "name": ORGA["name"],
        "src": img_src(ORGA["file"]),
        "columns": [{"slots": col} for col in ORGA["columns"]],
        "targets": [t for col in ORGA["columns"] for t in col],
        "decoys": ORGA["decoys"],
    })

    block = json.dumps(imgs, ensure_ascii=False, separators=(",", ":"))

    with open(HTML_FILE, encoding="utf-8") as f:
        html = f.read()

    html, n = re.subn(
        r"(const IMGS=/\*GENERATED-START\*/).*?(/\*GENERATED-END\*/;)",
        lambda m: m.group(1) + block + m.group(2),
        html, flags=re.S,
    )
    if n != 1:
        raise SystemExit("GENERATED-Marker nicht gefunden oder mehrfach vorhanden.")

    with open(HTML_FILE, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)

    print(f"{len(imgs)} Bilder eingetragen -> {os.path.basename(HTML_FILE)}")


if __name__ == "__main__":
    main()
