# Graphic plan check

Run it after the graphics agents are done and before any render. It reads `project/state.json` (written by the server) and the frame size of the video you will render. It never changes anything.

```
python3 brand/tools/graphic_plan_check.py project/state.json --width 1080 --height 1920 --font brand/fonts/Inter-Bold.ttf
python3 brand/tools/graphic_plan_check.py project/state.json --width 1080 --height 1920 --pos stat_card=0.18,highlight=0.17 --caption-top 0.70
```

Reads: fit inside the frame with 60 px margins (measured with the font file when Pillow is installed, else 0.6 em per character), text length 1 to 24, reading hold, vertical safe zones (top band, bottom text limit, right rail), 60 px above the caption lane, and 3 s of breathing room between graphics (output time, using the accepted cuts).

Exit code 0 is OK, 1 means at least one PROBLEM line, 2 means the file could not be read. Fix by moving `POS` fractions, shortening text (the user's words stay the user's words: ask before changing a graphic's text) or retiming a graphic. After a render, the numbers are not enough: look at stills.

`--pos` must mirror the `POS` table of your `render.py`. `--caption-top` is the top of the caption pill as a fraction of height (the shipped render uses 0.78, which is too low for vertical video, see `ae-caption-style-and-grouping`).

```python
# file: graphic_plan_check.py
#!/usr/bin/env python3
"""Check the graphics placed in project/state.json before a render: fit, hold, spacing, cadence, safe zones, caption gap.

    python3 graphic_plan_check.py project/state.json --width 1080 --height 1920 [--font brand/fonts/Inter-Bold.ttf]
        [--pos stat_card=0.17,lower_third=0.62,chapter_title=0.38,highlight=0.16] [--caption-top 0.70]

Positions are the vertical start of each template as a fraction of frame height (the same numbers render.py uses in its POS table).
Sizes follow the shipped render's template sizes, scaled by short side over 1080 (see SKILL.md, "Scale by short side").
Exit code: 0 no problem, 1 at least one problem, 2 unreadable input. Uses Pillow when installed, otherwise estimates 0.6 em per character.
"""
import argparse, json, os, sys

BASE = {  # template: (font px at 1080, pad w, pad h, x side)
    "stat_card": (112, 90, 80, "r"), "lower_third": (52, 120, 56, "l"),
    "chapter_title": (96, 140, 110, "c"), "highlight": (58, 80, 44, "l"),
}
DEFAULT_POS = {"stat_card": 0.10, "lower_third": 0.62, "chapter_title": 0.38, "highlight": 0.16}


def measure(text, px, font):
    try:
        from PIL import ImageFont, ImageDraw, Image
        f = ImageFont.truetype(font, px) if font and os.path.exists(font) else None
        if f is not None:
            d = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
            l, t, r, b = d.textbbox((0, 0), text, font=f)
            return r - l, b - t
    except Exception:
        pass
    return round(0.6 * px * len(text)), round(0.72 * px)


def out_time(t, cuts):
    acc = 0.0
    for c in cuts:
        if c["start"] - 1e-3 <= t <= c["end"] + 1e-3:
            return acc + (t - c["start"])
        acc += c["end"] - c["start"]
    return None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("state")
    ap.add_argument("--width", type=int, required=True)
    ap.add_argument("--height", type=int, required=True)
    ap.add_argument("--font", default=None)
    ap.add_argument("--pos", default="")
    ap.add_argument("--caption-top", type=float, default=0.78)
    a = ap.parse_args(argv)
    try:
        st = json.load(open(a.state, encoding="utf-8"))
    except (OSError, ValueError) as e:
        print("cannot read state:", e)
        return 2
    pos = dict(DEFAULT_POS)
    for part in filter(None, a.pos.split(",")):
        k, v = part.split("=")
        pos[k.strip()] = float(v)
    W, H = a.width, a.height
    s = min(W, H) / 1080.0
    vertical = H / W >= 1.5
    sz = H / 1920.0  # safe zone numbers are for a 1920 tall canvas
    gs = sorted([g for g in st.get("graphics", []) if g.get("status") == "ok"], key=lambda g: g["at"])
    cuts = sorted([c for c in st.get("cuts", []) if c.get("status") == "ok"], key=lambda c: c["start"])
    problems = []
    if len(gs) > 10:
        problems.append("more than 10 graphics (%d)" % len(gs))
    prev_end = None
    for g in gs:
        tpl, text = g["template"], g["text"]
        px, pw, ph, side = BASE[tpl]
        tw, th = measure(text, round(px * s), a.font)
        bw, bh = tw + round(pw * s), th + round(ph * s)
        x = {"r": W - bw - round(0.06 * W), "l": round(0.06 * W), "c": (W - bw) // 2}[side]
        y = round(H * pos[tpl])
        tag = "%s %s '%s' at %.2f" % (g["id"], tpl, text, g["at"])
        if bw > W - round(120 * s):
            problems.append("%s: box %d px wide does not fit inside the frame with 60 px margins (shorten the text or lower the font)" % (tag, bw))
        if not 1 <= len(text) <= 24:
            problems.append("%s: text is %d characters (the server allows 1 to 24)" % (tag, len(text)))
        words = len(text.split())
        need = max(1.5, 1.0 + 0.25 * max(0, words - 3))
        if g["dur"] < need:
            problems.append("%s: hold %.1f s is under the reading hold %.2f s" % (tag, g["dur"], need))
        if vertical:
            if y < 290 * sz:
                problems.append("%s: top at y %d is inside the plain top band (text must start at y %d or lower)" % (tag, y, round(290 * sz)))
            if y + bh > 1500 * sz:
                problems.append("%s: bottom at y %d is below the text limit y %d" % (tag, y + bh, round(1500 * sz)))
            if x + bw > 900 * sz and y + bh > 980 * sz and y < 1790 * sz:
                problems.append("%s: box reaches the right rail zone (x over %d, y %d to %d)" % (tag, round(900 * sz), round(980 * sz), round(1790 * sz)))
        cap_top = round(H * a.caption_top)
        if y < cap_top and y + bh + round(60 * s) > cap_top and y + bh > cap_top - round(60 * s):
            problems.append("%s: less than 60 px clear above the caption lane (caption top y %d, graphic bottom y %d)" % (tag, cap_top, y + bh))
        ot = out_time(g["at"], cuts) if cuts else g["at"]
        if prev_end is not None and ot is not None and ot - prev_end < 3.0:
            problems.append("%s: only %.1f s after the previous graphic ended (aim for 3 s or more of breathing room)" % (tag, ot - prev_end))
        if ot is not None:
            prev_end = ot + g["dur"]
    print("%d graphics checked, frame %dx%d, scale %.2f" % (len(gs), W, H, s))
    for p in problems:
        print("PROBLEM:", p)
    if not problems:
        print("OK")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
```
