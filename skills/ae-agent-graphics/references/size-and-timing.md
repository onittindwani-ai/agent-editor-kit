# Size and timing checks for graphics (read only)

## 1. Measure a card with the render's own drawing function

Run from the editor folder (the one that holds `render.py`). Needs Pillow. It draws into a temporary folder that cleans itself up and prints the card size in pixels.

```python
import os, sys, tempfile
sys.path.insert(0, ".")
import render

FRAME_W, FRAME_H = 1080, 1920          # the delivered frame (the render uses the original file's size)
CHECKS = [("chapter_title", "Shaping"), ("lower_third", "Claude Code"), ("stat_card", "7 days"), ("highlight", "no repeats")]

with tempfile.TemporaryDirectory() as d:
    for tpl, text in CHECKS:
        w, h = render.graphic_png(tpl, text, min(FRAME_W, FRAME_H), os.path.join(d, "probe.png"))
        verdict = "ok" if w <= 0.88 * FRAME_W else ("tight" if w <= 0.94 * FRAME_W else "OVERFLOW")
        print(f"{tpl:14} {text!r:22} {w:5d} x {h:4d}  {verdict}")
```

Rules of thumb: `ok` means 88 percent of the frame width or less. `tight` is on screen but crowds the 6 percent margin. `OVERFLOW` runs off the frame. Do the check for every text you plan to send in a vertical or square frame. For a landscape frame only unusually long capital letter texts are a risk.

## 2. Check starts and seams against the kept cuts

Same helper as the effects skill, with graphics in mind. Standard library only.

```python
import json, urllib.request
BASE = "http://127.0.0.1:8780"
state = json.load(urllib.request.urlopen(BASE + "/api/state"))
cuts = sorted((c for c in state["cuts"] if c["status"] == "ok"), key=lambda c: c["start"])

def cut_of(t):
    return next((c for c in cuts if c["start"] - 1e-3 <= t <= c["end"] + 1e-3), None)

def out_time(t):
    acc = 0.0
    for c in cuts:
        if c["start"] - 1e-3 <= t <= c["end"] + 1e-3:
            return round(acc + t - c["start"], 2)
        acc += c["end"] - c["start"]
    return None

for g in sorted((g for g in state["graphics"] if g["status"] == "ok"), key=lambda g: g["at"]):
    c = cut_of(g["at"])
    if c is None:
        print(g["id"], g["text"], "START IN REMOVED MATERIAL, the render will skip it")
    elif g["at"] + g["dur"] > c["end"] + 1e-3:
        print(g["id"], g["text"], "CROSSES A SEAM at", c["end"], "(the card will sit over words from another part)")
    else:
        print(g["id"], g["text"], "ok, output time", out_time(g["at"]), "to", round(out_time(g["at"]) + g["dur"], 2))
```

## 3. Spacing in output time

Graphics are checked by the server in source time. In the finished video they can be closer. Print the output times of all graphics and zooms, sort them, and make sure no two graphics start less than 1.5 s apart in output time.
