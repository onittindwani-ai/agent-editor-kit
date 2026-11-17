# Theme tools (standard library, plus Pillow for the sheet)

Save each block into `brand/tools/` (the first comment line gives the file name). They are small on purpose: read them before running. None of them changes `brand/theme.json`.

Install Pillow in the project's virtual environment if it is not there yet: `.venv/bin/pip install pillow`.

## 1. theme_tokens.py: validate the theme, check contrast, write tokens.json

Run: `python3 brand/tools/theme_tokens.py brand/theme.json --out brand/tokens.json --caption-style surface --fix`

Exit code 0 means no pair is below its minimum. 1 means at least one FAIL (with `--fix` it prints a nearest passing colour). 2 means the file is invalid.

```python
# file: theme_tokens.py
#!/usr/bin/env python3
"""Build brand/tokens.json from brand/theme.json and check every colour pair.

    python3 theme_tokens.py brand/theme.json --out brand/tokens.json [--caption-style surface|inverse] [--fix]

Exit code: 0 all pairs at or above their minimum, 1 at least one pair below its minimum, 2 the theme file is invalid.
Only the Python standard library is used. theme.json is only read, never changed (--fix prints suggestions).
"""
import argparse, json, os, re, sys

ROLES = ("bg", "surface", "ink", "muted", "accent", "ok", "warn")
FONT_ROLES = ("heading", "body", "accent")
# (label, foreground role, background role, minimum ratio, target ratio)
PAIRS = [
    ("ink on bg", "ink", "bg", 4.5, 7.0),
    ("ink on surface", "ink", "surface", 4.5, 7.0),
    ("muted on bg", "muted", "bg", 4.5, 4.5),
    ("muted on surface", "muted", "surface", 4.5, 4.5),
    ("accent on bg", "accent", "bg", 3.0, 4.5),
    ("accent on surface", "accent", "surface", 3.0, 4.5),
    ("ok on bg", "ok", "bg", 3.0, 4.5),
    ("warn on bg", "warn", "bg", 3.0, 4.5),
]
MIN_SURFACE_SEPARATION = 1.25


def parse_hex(value):
    s = str(value).strip().lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    if not re.fullmatch(r"[0-9a-fA-F]{6}", s):
        raise ValueError("not a hex colour: %r" % (value,))
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def to_hex(rgb):
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(c))) for c in rgb)


def _lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(rgb):
    r, g, b = (_lin(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a, b):
    la, lb = luminance(parse_hex(a)), luminance(parse_hex(b))
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def mix(a, b, t):
    ra, rb = parse_hex(a), parse_hex(b)
    return to_hex(tuple(x + (y - x) * t for x, y in zip(ra, rb)))


def nudge(fg, bg, target):
    """Smallest move of fg toward black or white (2 percent steps) that reaches the target ratio against bg."""
    best = None
    for toward in ("#000000", "#FFFFFF"):
        for i in range(0, 51):
            cand = mix(fg, toward, i / 50.0 * 0.6)
            if ratio(cand, bg) >= target:
                if best is None or i < best[0]:
                    best = (i, cand)
                break
    return best[1] if best else None


def validate(theme):
    problems = []
    pal = theme.get("palette", {})
    for r in ROLES:
        if r not in pal:
            problems.append("palette.%s is missing" % r)
        else:
            try:
                parse_hex(pal[r])
            except ValueError as e:
                problems.append("palette.%s: %s" % (r, e))
    fonts = theme.get("fonts", {})
    for r in FONT_ROLES:
        if not fonts.get(r):
            problems.append("fonts.%s is missing" % r)
    bg = theme.get("background", {})
    if bg.get("type") not in ("solid", "gradient", "image", "video", "none"):
        problems.append("background.type must be solid, gradient, image, video or none")
    if bg.get("type") in ("image", "video") and not bg.get("path"):
        problems.append("background.path is required for image and video backgrounds")
    if not isinstance(theme.get("radius", 0), (int, float)) or theme.get("radius", 0) < 0:
        problems.append("radius must be a number of 0 or more")
    if theme.get("shadow") not in ("soft", "none"):
        problems.append("shadow must be soft or none")
    return problems


def find_font(fonts_dir, family, role):
    if not os.path.isdir(fonts_dir):
        return None
    key = re.sub(r"[^a-z0-9]", "", family.lower())
    want = {"heading": ("extrabold", "black", "bold"), "body": ("medium", "regular"), "accent": ("italic",)}[role]
    files = [f for f in os.listdir(fonts_dir) if f.lower().endswith((".ttf", ".otf"))]
    cands = [f for f in files if key in re.sub(r"[^a-z0-9]", "", f.lower())]
    for w in want:
        for f in cands:
            if w in f.lower():
                return os.path.join(fonts_dir, f)
    return os.path.join(fonts_dir, cands[0]) if cands else None


def build(theme, base_dir, caption_style):
    p = theme["palette"]
    p = {k: to_hex(parse_hex(v)) for k, v in p.items()}
    on_accent = max((p["ink"], p["bg"], "#FFFFFF", "#000000"), key=lambda c: ratio(c, p["accent"]))
    sep = ratio(p["surface"], p["bg"])
    rows = []
    for label, fg, bgr, lo, hi in PAIRS:
        r = ratio(p[fg], p[bgr])
        rows.append({"pair": label, "ratio": round(r, 2), "min": lo, "target": hi,
                     "status": "ok" if r >= hi else ("low" if r >= lo else "FAIL")})
    if caption_style == "inverse":
        fill, text, base = p["ink"], p["bg"], p["ink"]
    else:
        fill, text, base = p["surface"], p["ink"], p["surface"]
    hl = p["accent"] if ratio(p["accent"], base) >= 4.5 else text
    rim = mix(p["surface"], p["ink"], 0.28)
    rgb = lambda h, a=255: list(parse_hex(h)) + [a]
    fonts = theme["fonts"]
    fdir = os.path.join(base_dir, "fonts")
    toks = {
        "version": 1, "palette": p, "rgba": {k: rgb(v) for k, v in p.items()},
        "derived": {"on_accent": on_accent, "rim": rim, "veil": p["bg"],
                    "shadow": rgb(p["ink"], 46) if theme["shadow"] == "soft" else None},
        "surface_separation": {"ratio": round(sep, 2), "minimum": MIN_SURFACE_SEPARATION, "needs_rim": sep < MIN_SURFACE_SEPARATION},
        "caption": {"style": caption_style, "pill_fill": rgb(fill, 235 if caption_style == "surface" else 225),
                    "text": text, "highlight": hl, "highlight_is_accent": hl == p["accent"]},
        "contrast": rows,
        "fonts": {**{r: fonts[r] for r in FONT_ROLES}, "files": {r: find_font(fdir, fonts[r], r) for r in FONT_ROLES}},
        "background": theme["background"], "radius": theme["radius"], "shadow": theme["shadow"],
        "rim_px": 2, "shadow_blur": 24, "shadow_dy": 10, "design_short_side": 1080,
    }
    return toks, p


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("theme")
    ap.add_argument("--out", default=None)
    ap.add_argument("--caption-style", choices=("surface", "inverse"), default="surface")
    ap.add_argument("--fix", action="store_true", help="print suggested hex values for failing pairs")
    a = ap.parse_args(argv)
    try:
        with open(a.theme, "r", encoding="utf-8") as fh:
            theme = json.load(fh)
    except (OSError, json.JSONDecodeError) as e:
        print("cannot read theme:", e)
        return 2
    problems = validate(theme)
    if problems:
        print("INVALID THEME")
        for x in problems:
            print(" -", x)
        return 2
    base = os.path.dirname(os.path.abspath(a.theme))
    toks, pal = build(theme, base, a.caption_style)
    bad = 0
    print("%-20s %7s %5s %7s  %s" % ("pair", "ratio", "min", "target", "status"))
    for r in toks["contrast"]:
        print("%-20s %7.2f %5.1f %7.1f  %s" % (r["pair"], r["ratio"], r["min"], r["target"], r["status"]))
        if r["status"] == "FAIL":
            bad += 1
            if a.fix:
                label_fg = r["pair"].split(" on ")[0]
                label_bg = r["pair"].split(" on ")[1]
                s = nudge(pal[label_fg], pal[label_bg], r["min"])
                print("    suggestion: %s %s -> %s" % (label_fg, pal[label_fg], s))
    ss = toks["surface_separation"]
    print("surface vs bg ratio %.2f (needs %.2f or a rim plus a contact shadow): %s" % (
        ss["ratio"], ss["minimum"], "RIM AND SHADOW REQUIRED" if ss["needs_rim"] else "separate enough"))
    print("text on accent: %s (ratio %.2f)" % (toks["derived"]["on_accent"], ratio(toks["derived"]["on_accent"], pal["accent"])))
    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump(toks, fh, indent=2)
        print("wrote", a.out)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
```

## 2. theme_sheet.py: preview picture and background veil check

Run: `.venv/bin/python brand/tools/theme_sheet.py brand/tokens.json --out brand/theme-sheet.png`

With a background still: add `--probe brand/bg_probe.png`. It prints the worst case ink contrast over that picture and the smallest veil opacity that reaches 4.5.

```python
# file: theme_sheet.py
#!/usr/bin/env python3
"""Draw a preview sheet of the theme (swatches, caption pill, stat card, lower third, chapter title, highlight).

    python3 theme_sheet.py brand/tokens.json --out brand/theme-sheet.png [--width 1080] [--probe brand/bg_probe.png]

Needs Pillow. With --probe (a still taken from the background image or video) it also prints the worst case contrast of the ink
colour over that background and the smallest veil opacity (0 to 0.8) that reaches 4.5. The sheet is a preview for the user to
approve; it is not a render of the video.
"""
import argparse, json, os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont


def hx(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def lum(rgb):
    f = lambda c: (c / 255) / 12.92 if c / 255 <= 0.04045 else (((c / 255) + 0.055) / 1.055) ** 2.4
    r, g, b = (f(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def cratio(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def load_font(tok, role, size):
    path = tok["fonts"]["files"].get(role)
    for p in (path, "/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        if p and os.path.exists(p):
            return ImageFont.truetype(p, size)
    try:
        return ImageFont.load_default(size)
    except TypeError:
        return ImageFont.load_default()


def text_box(d, text, f):
    l, t, r, b = d.textbbox((0, 0), text, font=f)
    return l, t, r - l, b - t


def card(img, xy, fill, radius, tok, s):
    x, y, w, h = xy
    if tok["shadow"] == "soft":
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        sd.rounded_rectangle((x, y + round(tok["shadow_dy"] * s), x + w, y + h + round(tok["shadow_dy"] * s)), radius, fill=tuple(tok["derived"]["shadow"]))
        sh = sh.filter(ImageFilter.GaussianBlur(tok["shadow_blur"] * s / 2))
        img.alpha_composite(sh)
    d = ImageDraw.Draw(img)
    rim = hx(tok["derived"]["rim"]) if tok["surface_separation"]["needs_rim"] else None
    d.rounded_rectangle((x, y, x + w, y + h), radius, fill=fill, outline=rim, width=max(2, round(tok["rim_px"] * s)) if rim else 0)


def sheet(tok, W):
    s = W / 1080.0
    H = round(1500 * s)
    p = tok["palette"]
    img = Image.new("RGBA", (W, H), hx(p["bg"]) + (255,))
    d = ImageDraw.Draw(img)
    fl = load_font(tok, "body", round(30 * s))
    x = round(60 * s)
    for i, role in enumerate(("bg", "surface", "ink", "muted", "accent", "ok", "warn")):
        bx = x + i * round(140 * s)
        d.rounded_rectangle((bx, round(50 * s), bx + round(120 * s), round(170 * s)), round(18 * s), fill=hx(p[role]), outline=hx(p["muted"]), width=2)
        d.text((bx, round(180 * s)), role, font=fl, fill=hx(p["ink"]))
        d.text((bx, round(216 * s)), p[role], font=load_font(tok, "body", round(22 * s)), fill=hx(p["muted"]))
    rad = round(tok["radius"] * s)
    # caption pill
    cap = tok["caption"]
    f = load_font(tok, "heading", round(60 * s))
    words = ["Sourdough", "needs time"]
    fa = load_font(tok, "accent", round(66 * s))
    l, t, tw, th = text_box(d, words[0] + " ", f)
    tw += text_box(d, words[1], fa)[2]
    pw, ph = tw + round(70 * s), th + round(40 * s)
    cx, cy = (W - pw) // 2, round(300 * s)
    card(img, (cx, cy, pw, ph), tuple(cap["pill_fill"]), ph // 2, tok, s)
    d = ImageDraw.Draw(img)
    d.text((cx + round(35 * s) - l, cy + round(20 * s) - t), words[0], font=f, fill=hx(cap["text"]))
    w0 = text_box(d, words[0] + " ", f)[2]
    d.text((cx + round(35 * s) - l + w0, cy + round(20 * s) - t), words[1], font=fa, fill=hx(cap["highlight"]))
    # stat card
    fs = load_font(tok, "heading", round(120 * s))
    l, t, tw, th = text_box(d, "48 h", fs)
    sw, sh_ = tw + round(100 * s), th + round(90 * s)
    sx, sy = W - sw - round(80 * s), round(440 * s)
    card(img, (sx, sy, sw, sh_), hx(p["surface"]), rad, tok, s)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((sx + round(28 * s), sy + round(18 * s), sx + sw - round(28 * s), sy + round(28 * s)), round(5 * s), fill=hx(p["accent"]))
    d.text((sx + (sw - tw) // 2 - l, sy + (sh_ - th) // 2 - t + round(10 * s)), "48 h", font=fs, fill=hx(p["ink"]))
    # lower third
    fl3 = load_font(tok, "body", round(54 * s))
    l, t, tw, th = text_box(d, "Maya, head baker", fl3)
    lw, lh = tw + round(120 * s), th + round(60 * s)
    lx, ly = round(80 * s), round(440 * s)
    card(img, (lx, ly, lw, lh), hx(p["surface"]), round(14 * s), tok, s)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((lx, ly, lx + round(16 * s), ly + lh), round(8 * s), fill=hx(p["accent"]))
    d.text((lx + round(60 * s) - l, ly + (lh - th) // 2 - t), "Maya, head baker", font=fl3, fill=hx(p["ink"]))
    # chapter title
    fc = load_font(tok, "heading", round(96 * s))
    l, t, tw, th = text_box(d, "Part 1: The starter", fc)
    ccw, cch = min(tw + round(140 * s), W - round(120 * s)), th + round(130 * s)
    ccx, ccy = (W - ccw) // 2, round(720 * s)
    card(img, (ccx, ccy, ccw, cch), hx(p["surface"]), rad, tok, s)
    d = ImageDraw.Draw(img)
    d.text(((W - tw) // 2 - l, ccy + round(28 * s) - t), "Part 1: The starter", font=fc, fill=hx(p["ink"]))
    d.rounded_rectangle((ccx + round(70 * s), ccy + cch - round(38 * s), ccx + ccw - round(70 * s), ccy + cch - round(28 * s)), round(5 * s), fill=hx(p["accent"]))
    # highlight
    fh = load_font(tok, "heading", round(58 * s))
    l, t, tw, th = text_box(d, "keep it warm", fh)
    hw, hh = tw + round(80 * s), th + round(44 * s)
    hxp, hyp = round(80 * s), round(1000 * s)
    d.rounded_rectangle((hxp, hyp, hxp + hw, hyp + hh), hh // 2, fill=hx(p["accent"]))
    d.text((hxp + (hw - tw) // 2 - l, hyp + (hh - th) // 2 - t), "keep it warm", font=fh, fill=hx(tok["derived"]["on_accent"]))
    # state chips
    for i, (role, label) in enumerate((("ok", "Done"), ("warn", "Watch out"))):
        fc2 = load_font(tok, "body", round(40 * s))
        l, t, tw, th = text_box(d, label, fc2)
        bx = round(80 * s) + i * round(300 * s)
        d.rounded_rectangle((bx, round(1180 * s), bx + tw + round(60 * s), round(1180 * s) + th + round(36 * s)), round(30 * s), fill=hx(p[role]))
        d.text((bx + round(30 * s) - l, round(1180 * s) + round(18 * s) - t), label, font=fc2, fill=hx(p["bg"]) if cratio(hx(p["bg"]), hx(p[role])) >= cratio((255, 255, 255), hx(p[role])) else (255, 255, 255))
    d.text((round(80 * s), round(1300 * s)), "Glyph test: aeiou AEIOU 0123456789 % $ EUR & @ ? !", font=fl, fill=hx(p["muted"]))
    return img


def veil_report(tok, probe, cols=6, rows=10):
    im = Image.open(probe).convert("RGB")
    ink, bgc = hx(tok["palette"]["ink"]), hx(tok["palette"]["bg"])
    samples = []
    for r in range(rows):
        for c in range(cols):
            x = int((c + 0.5) * im.width / cols)
            y = int((r + 0.5) * im.height / rows)
            samples.append(im.getpixel((x, y)))
    worst0 = min(cratio(ink, s) for s in samples)
    need = None
    for a in [i / 20 for i in range(0, 17)]:
        mixed = [tuple(round(sc * (1 - a) + bc * a) for sc, bc in zip(s, bgc)) for s in samples]
        if min(cratio(ink, m) for m in mixed) >= 4.5:
            need = a
            break
    print("worst case ink contrast over the background without a veil: %.2f" % worst0)
    print("smallest veil opacity that reaches 4.5: %s" % ("none needed" if need == 0 else (("%.2f" % need) if need is not None else "more than 0.80, choose another background")))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("tokens")
    ap.add_argument("--out", default="theme-sheet.png")
    ap.add_argument("--width", type=int, default=1080)
    ap.add_argument("--probe", default=None)
    a = ap.parse_args(argv)
    tok = json.load(open(a.tokens, encoding="utf-8"))
    sheet(tok, a.width).convert("RGB").save(a.out)
    print("wrote", a.out)
    if a.probe:
        veil_report(tok, a.probe)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

## 3. theme_loader.py: how render.py reads the tokens

Save next to `render.py`. See step 9 of `SKILL.md` for the replacement map.

```python
# file: theme_loader.py
"""Small helper the render reads colours and fonts through. Save next to render.py.

    from theme_loader import load_tokens, rgba, font_path
    TOK = load_tokens()            # None when no tokens file exists: keep the render's built in defaults
    ACCENT = rgba(TOK, "accent") if TOK else (255, 176, 32, 255)

The tokens file is brand/tokens.json (built by theme_tokens.py). Set AE_TOKENS to use another path.
"""
import json, os


def load_tokens(path=None):
    here = os.path.dirname(os.path.abspath(__file__))
    path = path or os.environ.get("AE_TOKENS") or os.path.join(here, "brand", "tokens.json")
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def rgba(tok, role, alpha=255):
    h = tok["palette"][role].lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def derived_rgba(tok, key, alpha=255):
    h = tok["derived"][key].lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def font_path(tok, role):
    p = tok["fonts"]["files"].get(role)
    return p if p and os.path.exists(p) else None
```
