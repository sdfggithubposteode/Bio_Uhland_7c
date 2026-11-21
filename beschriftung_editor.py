"""Editor zum Positionieren der Beschriftungen auf den vier Bio-Bildern.

Bedienung:
  - Kästchen und rote Punkte mit der Maus ziehen
  - Pfeiltasten: markiertes Element fein bewegen (Shift = 10 px)
  - Oben zwischen den Bildern wechseln, mit "Speichern" sichern

Kästchen lassen sich frei platzieren (für das Layout außerhalb des
Bildes vorsehen), die roten Punkte bleiben immer innerhalb des Bildes.
Ergebnis: Bilder/beschriftungen.json (inkl. Zuschnitt-Rechteck "crop").
"""

import json
import os
import tkinter as tk
from tkinter import font as tkfont, messagebox, simpledialog

from PIL import Image, ImageTk

BASE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE, "Bilder")
DATA_FILE = os.path.join(IMG_DIR, "beschriftungen.json")

MARGIN_X = 300      # Platz für Kästchen links/rechts vom Bild
MARGIN_Y = 240      # Platz ober-/unterhalb
MAX_IMG_W = 1000    # Bild wird auf diese Anzeigegröße skaliert
MAX_IMG_H = 540
CROP_PAD = 30       # Zuschlag um Bild+Kästchen beim Zuschnitt
GAP = 40            # Abstand Kästchen <-> Bildkante bei Startposition

ZONES = {"full": (0.05, 0.95), "top": (0.05, 0.5), "bottom": (0.5, 0.95)}

IMAGES = [
    {
        "file": "Schematische Tierzelle mit Organellen.png",
        "name": "1 · Tierzelle",
        "labels": [
            ("mitochondrium", "Mitochondrium", "left", "top"),
            ("zellplasma", "Zellplasma", "left", "bottom"),
            ("zellkern", "Zellkern", "right", "top"),
            ("zellmembran", "Zellmembran", "right", "bottom"),
        ],
    },
    {
        "file": "Dreidimensionale Pflanzenzelle mit Organellen.png",
        "name": "2 · Pflanzenzelle 3D",
        "labels": [
            ("zellkern", "Zellkern", "left", "full"),
            ("kernmembran", "Kernmembran", "left", "full"),
            ("chloroplast", "Chloroplast", "left", "full"),
            ("zellwand", "Zellwand", "left", "full"),
            ("zellmembran", "Zellmembran", "left", "full"),
            ("mitochondrium", "Mitochondrium", "right", "full"),
            ("zellplasma", "Zellplasma", "right", "full"),
            ("vakuole", "Vakuole", "right", "full"),
            ("vakuolenmembran", "Vakuolenmembran", "right", "full"),
        ],
    },
    {
        "file": "Pflanzenzelle im Querschnitt.png",
        "name": "3 · Pflanzenzelle LM",
        "labels": [
            ("zellmembran", "Zellmembran", "right", "full"),
            ("vakuole", "Vakuole", "right", "full"),
            ("zellwand", "Zellwand", "right", "full"),
            ("zellplasma", "Zellplasma", "right", "full"),
            ("zellkern", "Zellkern", "right", "full"),
            ("chloroplast", "Chloroplast", "right", "full"),
        ],
    },
    {
        "file": "Detaillierter Querschnitt eines Blattes.png",
        "name": "4 · Blattquerschnitt",
        "labels": [
            ("spaltoeffnung", "Spaltöffnung", "left", "bottom"),
            ("hohlraum", "Hohlraum / Atemhöhle", "left", "bottom"),
            ("kutikula_oben", "Kutikula", "right", "full"),
            ("obere_epidermis", "Obere Epidermis", "right", "full"),
            ("palisadengewebe", "Palisadengewebe", "right", "full"),
            ("blattader", "Blattader", "right", "full"),
            ("schwammgewebe", "Schwammgewebe", "right", "full"),
            ("untere_epidermis", "Untere Epidermis", "right", "full"),
            ("kutikula_unten", "Kutikula", "right", "full"),
        ],
    },
    {
        "file": "Realistisches Mikroskop auf weißem Hintergrund.png",
        "name": "5 · Mikroskop",
        "labels": [
            ("okular", "Okular", "left", "top"),
            ("tubus", "Tubus", "left", "top"),
            ("objektivrevolver", "Objektivrevolver", "left", "full"),
            ("objektiv", "Objektiv", "left", "bottom"),
            ("objekttisch", "Objekttisch", "left", "bottom"),
            ("blende", "Blende", "right", "top"),
            ("triebrad", "Triebrad", "right", "full"),
            ("leuchte", "Mikroskopleuchte", "right", "bottom"),
            ("stativ_fuss", "Stativ und Fuß", "right", "bottom"),
        ],
    },
    {
        "file": "zeilung_tiere_zelle.png",
        "name": "6 · Zellteilung Tiere",
        "labels": [
            ("teilungsfaehig_1", "teilungsfähige Zelle", "left", "top"),
            ("verdopplung", "Verdopplung des Zellkerns", "left", "bottom"),
            ("teilungsfaehig_2", "teilungsfähige Zelle", "right", "top"),
            ("differenziert", "differenzierte Zelle", "right", "bottom"),
        ],
    },
    {
        "file": "Verschiedene Zelltypen im Überblick.png",
        "name": "7 · Zelltypen",
        "labels": [
            ("druesenzelle", "Drüsenzelle", "left", "top"),
            ("nervenzelle", "Nervenzelle", "left", "top"),
            ("knorpelzelle", "Knorpelzelle", "left", "bottom"),
            ("muskelzelle", "Muskelzelle", "left", "bottom"),
            ("stammzellen", "Stammzellen", "right", "top"),
            ("blutzellen", "Blutzellen", "right", "top"),
            ("spermienzelle", "Spermienzelle", "right", "bottom"),
            ("eizelle", "Eizelle", "right", "bottom"),
        ],
    },
    {
        "file": "Pflanzenzelltypen und Gewebestrukturen.png",
        "name": "8 · Pfl.-Zelltypen",
        "labels": [
            ("grundgewebe", "Junge Zelle aus dem Grundgewebe", "left", "top"),
            ("deckgewebe", "Zelle aus dem Deckgewebe", "left", "bottom"),
            ("speicherzelle", "Speicherzelle", "right", "top"),
            ("wurzelhaarzelle", "Wurzelhaarzelle", "right", "full"),
            ("leitgewebe", "Zelle aus dem Leitgewebe", "right", "bottom"),
        ],
    },
    {
        "file": "Histologisches Vierfachbild unter dem Mikroskop(1).png",
        "name": "9 · Gewebe",
        "labels": [
            ("deckgewebe", "Deckgewebe von Tieren", "left", "top"),
            ("grundgewebe", "Grundgewebe von Pflanzen", "left", "bottom"),
            ("muskelgewebe", "Muskelgewebe von Tieren", "right", "top"),
            ("leitgewebe", "Leitgewebe von Pflanzen", "right", "bottom"),
        ],
    },
    {
        "file": "Biomoleküle_ Bausteine und Beispiele.png",
        "name": "10 · Biomoleküle",
        "labels": [
            ("einfachzucker", "Einfachzucker", "left", "top"),
            ("zweifachzucker", "Zweifachzucker", "left", "top"),
            ("vielfachzucker", "Vielfachzucker", "left", "full"),
            ("kartoffeln", "Kartoffeln", "left", "bottom"),
            ("glycerin", "Glycerin", "left", "full"),
            ("proteinbausteine", "Proteinbausteine", "left", "bottom"),
            ("fettsaeuren", "Fettsäuren", "right", "top"),
            ("fette", "Fette", "right", "full"),
            ("erdnuesse", "Erdnüsse", "right", "full"),
            ("proteine", "Proteine", "right", "bottom"),
            ("sojabohnen", "Sojabohnen", "right", "bottom"),
        ],
    },
    {
        "file": "Botanische Infografik zur Photosynthese.png",
        "name": "11 · Fotosynthese",
        "labels": [
            ("licht", "Licht", "left", "top"),
            ("co2", "CO₂", "left", "full"),
            ("wasser", "Wasser mit Mineralstoffen", "left", "bottom"),
            ("glukose", "Glukose", "right", "top"),
            ("o2", "O₂", "right", "bottom"),
        ],
    },
    {
        "file": "Fünf botanische Lehrillustrationen.png",
        "name": "12 · Org.-Stufen Pfl.",
        "labels": [
            ("organismus", "Organismus (Tulpe)", "left", "top"),
            ("organ_blatt", "Organ (Blatt)", "left", "top"),
            ("zelle", "Zelle", "left", "full"),
            ("gewebe", "Gewebe", "left", "bottom"),
            ("organ_blue", "Organ (Blüte)", "left", "bottom"),
            ("z_zellkern", "Zellkern", "right", "top"),
            ("z_zellwand", "Zellwand", "right", "top"),
            ("z_zellplasma", "Zellplasma", "right", "full"),
            ("z_vakuole", "Vakuole", "right", "full"),
            ("z_chloroplast", "Chloroplast", "right", "bottom"),
            ("b_kronblatt", "Kronblatt", "right", "full"),
            ("b_staubblatt", "Staubblatt", "right", "bottom"),
            ("b_fruchtblatt", "Fruchtblatt", "right", "bottom"),
        ],
    },
    {
        "file": "Pflanzenzellteilung und Wachstum in sechs Stadien.png",
        "name": "13 · Zellteilung Pfl.",
        "labels": [
            ("zellwand", "Zellwand", "left", "top"),
            ("zellmembran", "Zellmembran", "left", "top"),
            ("zellkern_erbsubstanz", "Zellkern mit Erbsubstanz", "left", "full"),
            ("kernhuelle", "Hülle des Zellkerns", "left", "bottom"),
            ("zellplasma", "Zellplasma", "left", "bottom"),
            ("zellteilung", "Zellteilung", "left", "bottom"),
            ("aufloesen_kernhuelle", "Auflösen der Zellkernhülle", "right", "top"),
            ("beginn_verteilung", "Beginn der Verteilung der Erbsubstanz", "right", "top"),
            ("verteilt", "Erbsubstanz gleichmäßig verteilt", "right", "top"),
            ("neue_membranen", "Bildung neuer Zellmembranen und Zellwände", "right", "full"),
            ("kernhuellen_neu", "Zellkernhüllen neu gebildet", "right", "full"),
            ("teilung_fertig", "Teilung der Zelle abgeschlossen", "right", "bottom"),
            ("groessenzunahme", "Zunahme der Größe", "right", "bottom"),
            ("endgroesse", "endgültige Größe der Zellen erreicht", "right", "bottom"),
            ("zellwachstum", "Zellwachstum", "right", "bottom"),
        ],
    },
]


class Editor:
    def __init__(self, root):
        self.root = root
        root.title("Beschriftungs-Editor – Bio Klasse 7")
        root.state("zoomed")
        self.font = tkfont.Font(family="Segoe UI", size=12, weight="bold")
        self.data = self._load_json()
        self.img_index = None
        self.labels = []
        self.items = {}
        self.dirty = False
        self.sel = None
        self.drag = None
        self._build_ui()
        self.load_image(0)

    def _load_json(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _build_ui(self):
        bar = tk.Frame(self.root, bg="#eef3ef", pady=6, padx=10)
        bar.pack(fill="x")
        self.img_buttons = []
        for i, spec in enumerate(IMAGES):
            b = tk.Button(bar, text=spec["name"], command=lambda i=i: self.switch_image(i))
            b.pack(side="left", padx=(0, 6))
            self.img_buttons.append(b)
        tk.Button(bar, text="Speichern", bg="#17634d", fg="white",
                  command=self.save).pack(side="right")
        tk.Button(bar, text="Zurücksetzen", command=self.reset).pack(side="right", padx=(0, 6))
        tk.Button(bar, text="+ Kästchen", command=self.add_box).pack(side="right", padx=(0, 6))
        tk.Label(bar, text="Ziehen = grob · Pfeiltasten = fein (Shift ×10) · Doppelklick = Text · Entf = löschen",
                 bg="#eef3ef", fg="#5d7080").pack(side="right", padx=14)

        frame = tk.Frame(self.root)
        frame.pack(fill="both", expand=True)
        self.cv = tk.Canvas(frame, bg="#dfe7e1", highlightthickness=0)
        vsb = tk.Scrollbar(frame, orient="vertical", command=self.cv.yview)
        hsb = tk.Scrollbar(self.root, orient="horizontal", command=self.cv.xview)
        self.cv.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(fill="x")
        self.cv.pack(fill="both", expand=True)

        self.cv.bind("<ButtonPress-1>", self.on_press)
        self.cv.bind("<B1-Motion>", self.on_drag)
        self.cv.bind("<ButtonRelease-1>", self.on_release)
        self.cv.bind("<Double-Button-1>", self.on_double)
        self.root.bind("<Delete>", lambda e: self.delete_selected())
        self.root.bind("<Left>", lambda e: self.nudge(-1, 0, e))
        self.root.bind("<Right>", lambda e: self.nudge(1, 0, e))
        self.root.bind("<Up>", lambda e: self.nudge(0, -1, e))
        self.root.bind("<Down>", lambda e: self.nudge(0, 1, e))
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---------- Bild laden / wechseln ----------

    def switch_image(self, i):
        if i == self.img_index:
            return
        if not self.confirm_discard():
            return
        self.load_image(i)

    def confirm_discard(self):
        if not self.dirty:
            return True
        r = messagebox.askyesnocancel("Ungespeicherte Änderungen",
                                      "Änderungen an diesem Bild speichern?")
        if r is None:
            return False
        if r:
            self.save()
        return True

    def load_image(self, i):
        self.img_index = i
        spec = IMAGES[i]
        path = os.path.join(IMG_DIR, spec["file"])
        with Image.open(path) as im:
            self.orig_size = im.size
            scale = min(MAX_IMG_W / im.width, MAX_IMG_H / im.height, 1.6)
            self.scale = scale
            disp = im.resize((round(im.width * scale), round(im.height * scale)),
                             Image.LANCZOS)
            self.photo = ImageTk.PhotoImage(disp.convert("RGB"))

        ix, iy = MARGIN_X, MARGIN_Y
        iw, ih = disp.width, disp.height
        self.img_rect = (ix, iy, iw, ih)
        self.canvas_w = ix * 2 + iw
        self.canvas_h = iy * 2 + ih

        saved = self.data.get(spec["file"])
        if saved and saved.get("labels"):
            self.labels = saved["labels"]
        else:
            self.labels = self.default_labels(spec)

        self.normalize_boxes()
        self.dirty = False
        self.sel = None
        self.draw()
        for j, b in enumerate(self.img_buttons):
            b.configure(relief="sunken" if j == i else "raised")
        self.root.title(f"Beschriftungs-Editor – {spec['name']}"
                        + (" (gespeichert)" if saved else ""))

    def default_labels(self, spec):
        ix, iy, iw, ih = self.img_rect
        groups = {}
        for lid, text, side, zone in spec["labels"]:
            groups.setdefault((side, zone), []).append((lid, text))
        labels = []
        for (side, zone), entries in groups.items():
            z0, z1 = ZONES[zone]
            for k, (lid, text) in enumerate(entries):
                w = self.font.measure(text) + 30
                h = 34
                cy = iy + ih * (z0 + (z1 - z0) * (k + 1) / (len(entries) + 1))
                x = ix - GAP - w if side == "left" else ix + iw + GAP
                y = cy - h / 2
                px = min(max(x + w / 2, ix + 50), ix + iw - 50)
                py = min(max(cy, iy + 50), iy + ih - 50)
                labels.append({
                    "id": lid, "text": text,
                    "box": {"x": round(x), "y": round(y), "w": w, "h": h},
                    "point": {"x": round(px), "y": round(py)},
                })
        return labels

    def normalize_boxes(self):
        """Zieht alle Kästchen auf einheitliche Größe (zentriert) – so wie
        es der Build fürs HTML macht, damit die Ansicht hier dem späteren
        Ergebnis entspricht."""
        if not self.labels:
            return
        w = max(lb["box"]["w"] for lb in self.labels)
        h = max(lb["box"]["h"] for lb in self.labels)
        for lb in self.labels:
            b = lb["box"]
            b["x"] += (b["w"] - w) / 2
            b["y"] += (b["h"] - h) / 2
            b["w"], b["h"] = w, h

    # ---------- Zeichnen ----------

    def draw(self):
        self.cv.delete("all")
        self.items = {}
        ix, iy, iw, ih = self.img_rect
        self.cv.create_image(ix, iy, anchor="nw", image=self.photo, tags="img")
        self.cv.create_rectangle(ix - 1, iy - 1, ix + iw + 1, iy + ih + 1,
                                 outline="#17634d", width=1)
        for i, lb in enumerate(self.labels):
            b, p = lb["box"], lb["point"]
            ax, ay = self.attach_point(b, p)
            line = self.cv.create_line(ax, ay, p["x"], p["y"], fill="#c0392b",
                                       width=2, arrow=tk.LAST,
                                       arrowshape=(11, 13, 5))
            rect = self.cv.create_rectangle(
                b["x"], b["y"], b["x"] + b["w"], b["y"] + b["h"],
                fill="white", outline="#17634d", width=2,
                tags=(f"bx{i}", "bx"))
            text = self.cv.create_text(
                b["x"] + b["w"] / 2, b["y"] + b["h"] / 2, text=lb["text"],
                font=self.font, fill="#1b3040", tags=(f"bx{i}", "bx"))
            r = 6
            dot = self.cv.create_oval(
                p["x"] - r, p["y"] - r, p["x"] + r, p["y"] + r,
                fill="#c0392b", outline="white", width=2,
                tags=(f"pt{i}", "pt"))
            self.items[i] = {"line": line, "rect": rect, "text": text, "dot": dot}
        self.cv.configure(scrollregion=(0, 0, self.canvas_w, self.canvas_h))

    def attach_point(self, box, point):
        cx, cy = box["x"] + box["w"] / 2, box["y"] + box["h"] / 2
        dx, dy = point["x"] - cx, point["y"] - cy
        if dx == 0 and dy == 0:
            return cx, cy
        tx = (box["w"] / 2) / abs(dx) if dx else float("inf")
        ty = (box["h"] / 2) / abs(dy) if dy else float("inf")
        t = min(tx, ty)
        return cx + dx * t, cy + dy * t

    def refresh_label(self, i):
        lb = self.labels[i]
        b, p = lb["box"], lb["point"]
        it = self.items[i]
        ax, ay = self.attach_point(b, p)
        self.cv.coords(it["line"], ax, ay, p["x"], p["y"])
        self.cv.coords(it["rect"], b["x"], b["y"], b["x"] + b["w"], b["y"] + b["h"])
        self.cv.coords(it["text"], b["x"] + b["w"] / 2, b["y"] + b["h"] / 2)
        r = 6
        self.cv.coords(it["dot"], p["x"] - r, p["y"] - r, p["x"] + r, p["y"] + r)

    # ---------- Kästchen hinzufügen / umbenennen / löschen ----------

    def add_box(self):
        text = simpledialog.askstring("Neues Kästchen", "Beschriftung:",
                                      parent=self.root)
        if not text:
            return
        ix, iy, iw, ih = self.img_rect
        w = self.font.measure(text) + 30
        n = sum(1 for lb in self.labels if lb["id"].startswith("custom"))
        self.labels.append({
            "id": f"custom_{n}", "text": text,
            "box": {"x": ix - GAP - w, "y": iy + 40 * (n % 5), "w": w, "h": 34},
            "point": {"x": ix + iw // 2, "y": iy + ih // 2},
        })
        self.dirty = True
        self.normalize_boxes()
        self.draw()
        self.select(("bx", len(self.labels) - 1))

    def on_double(self, e):
        x, y = self.cv.canvasx(e.x), self.cv.canvasy(e.y)
        for item in reversed(self.cv.find_overlapping(x - 3, y - 3, x + 3, y + 3)):
            for tag in self.cv.gettags(item):
                if tag.startswith("bx") and len(tag) > 2:
                    self.rename_box(int(tag[2:]))
                    return

    def rename_box(self, i):
        lb = self.labels[i]
        t = simpledialog.askstring("Kästchen umbenennen", "Beschriftung:",
                                   initialvalue=lb["text"], parent=self.root)
        if not t or t == lb["text"]:
            return
        b = lb["box"]
        nw = self.font.measure(t) + 30
        b["x"] += (b["w"] - nw) / 2
        b["w"] = nw
        lb["text"] = t
        self.dirty = True
        self.normalize_boxes()
        self.draw()

    def delete_selected(self):
        if not self.sel or self.sel[0] != "bx":
            return
        del self.labels[self.sel[1]]
        self.dirty = True
        self.select(None)
        self.normalize_boxes()
        self.draw()

    # ---------- Ziehen ----------

    def on_press(self, e):
        x, y = self.cv.canvasx(e.x), self.cv.canvasy(e.y)
        hit = None
        for item in reversed(self.cv.find_overlapping(x - 4, y - 4, x + 4, y + 4)):
            for tag in self.cv.gettags(item):
                if tag.startswith("pt") and len(tag) > 2:
                    hit = ("pt", int(tag[2:]))
                elif tag.startswith("bx") and len(tag) > 2 and not hit:
                    hit = ("bx", int(tag[2:]))
            if hit and hit[0] == "pt":
                break
        if not hit:
            self.drag = None
            self.select(None)
            return
        kind, idx = hit
        self.drag = (kind, idx, x, y)
        self.select(hit)

    def select(self, hit):
        if self.sel:
            kind, idx = self.sel
            if kind == "bx":
                self.cv.itemconfigure(self.items[idx]["rect"],
                                      outline="#17634d", width=2)
            else:
                self.cv.itemconfigure(self.items[idx]["dot"], fill="#c0392b")
        self.sel = hit
        if hit:
            kind, idx = hit
            if kind == "bx":
                self.cv.itemconfigure(self.items[idx]["rect"],
                                      outline="#e67e22", width=3)
            else:
                self.cv.itemconfigure(self.items[idx]["dot"], fill="#e67e22")

    def on_drag(self, e):
        if not self.drag:
            return
        kind, idx, sx, sy = self.drag
        x, y = self.cv.canvasx(e.x), self.cv.canvasy(e.y)
        dx, dy = x - sx, y - sy
        lb = self.labels[idx]
        if kind == "bx":
            b = lb["box"]
            b["x"] += dx
            b["y"] += dy
        else:
            p = lb["point"]
            p["x"], p["y"] = self.clamp_point(p["x"] + dx, p["y"] + dy)
        self.drag = (kind, idx, x, y)
        self.refresh_label(idx)
        self.dirty = True

    def on_release(self, e):
        self.drag = None

    def nudge(self, dx, dy, e):
        if not self.sel:
            return
        step = 10 if e.state & 0x0001 else 1
        kind, idx = self.sel
        lb = self.labels[idx]
        if kind == "bx":
            b = lb["box"]
            b["x"] += dx * step
            b["y"] += dy * step
        else:
            p = lb["point"]
            p["x"], p["y"] = self.clamp_point(p["x"] + dx * step,
                                              p["y"] + dy * step)
        self.refresh_label(idx)
        self.dirty = True

    # ---------- Grenzen ----------

    def clamp_point(self, x, y):
        ix, iy, iw, ih = self.img_rect
        return (min(max(x, ix + 6), ix + iw - 6),
                min(max(y, iy + 6), iy + ih - 6))

    # ---------- Speichern ----------

    def crop_rect(self):
        ix, iy, iw, ih = self.img_rect
        x0, y0, x1, y1 = ix, iy, ix + iw, iy + ih
        for lb in self.labels:
            b = lb["box"]
            x0 = min(x0, b["x"]); y0 = min(y0, b["y"])
            x1 = max(x1, b["x"] + b["w"]); y1 = max(y1, b["y"] + b["h"])
        x0 = max(0, x0 - CROP_PAD); y0 = max(0, y0 - CROP_PAD)
        x1 = min(self.canvas_w, x1 + CROP_PAD)
        y1 = min(self.canvas_h, y1 + CROP_PAD)
        return {"x": round(x0), "y": round(y0),
                "w": round(x1 - x0), "h": round(y1 - y0)}

    def save(self):
        spec = IMAGES[self.img_index]
        ix, iy, iw, ih = self.img_rect
        self.data[spec["file"]] = {
            "image": {"file": f"Bilder/{spec['file']}",
                      "width": self.orig_size[0], "height": self.orig_size[1]},
            "canvas": {"width": self.canvas_w, "height": self.canvas_h,
                       "scale": round(self.scale, 5)},
            "imageRect": {"x": ix, "y": iy, "w": iw, "h": ih},
            "crop": self.crop_rect(),
            "labels": self.labels,
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        self.dirty = False
        self.root.title(f"Beschriftungs-Editor – {spec['name']} (gespeichert)")

    def reset(self):
        if not messagebox.askyesno("Zurücksetzen",
                                   "Positionen dieses Bildes auf Startwerte?"):
            return
        self.labels = self.default_labels(IMAGES[self.img_index])
        self.dirty = True
        self.select(None)
        self.draw()

    def on_close(self):
        if self.confirm_discard():
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    Editor(root)
    root.mainloop()
