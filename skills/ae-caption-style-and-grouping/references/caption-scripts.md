# Caption tools

Save each block into `brand/tools/` (the first comment line gives the file name). Read them before running. They never change the project except through the operations you send.

## 1. group_captions.py: propose groups from the transcript

Prints a table, or with `--ops AGENT` one JSON operation per line. Treat the result as a first draft and read it against the audio words.

```python
# file: group_captions.py
#!/usr/bin/env python3
"""Propose caption groups from the transcript, ready to send as caption operations.

    python3 group_captions.py project/ingest.json --start 0 --end 33 [--state project/state.json] [--keep "Claude Code,Bubbles"]
        [--ops W03]

Rules: 1 to 3 words, at most 22 characters, 0.2 to 3.0 s, break at punctuation, at pauses of 0.12 s or more and before clause
starters, never end on a function word, keep a number with its unit and named phrases together, start 0.03 s before the first
word and end at the last word's end. With --state, groups whose words are all shown by a graphic at the same time are dropped
(quiet windows). Prints a table, or with --ops AGENT one JSON caption operation per line for the server. Standard library only.
"""
import argparse, json, re, sys

FUNCTION = set("the a an to and or but of your my our for in on at by with from that this these those as if than so is are was were be i we you it because which when while where into about".split())
CLAUSE = set("and but so because which when if then or while though".split())
MAX_WORDS, MAX_CHARS, PAUSE, LEAD = 3, 22, 0.12, 0.03


def clean(w):
    return re.sub(r"^[^\w$]+|[^\w%]+$", "", w)


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def is_number(w):
    return bool(re.search(r"\d", w))


def build(words, keep):
    """Choose break points with a small dynamic program: lowest total penalty wins."""
    n = len(words)
    keep_words = [k.split() for k in keep]
    punct = re.compile(r"[.,;:!?\u2026]$")

    def joined(a, b):
        if is_number(a["w"]) and b["t"] - a["e"] < PAUSE and not punct.search(a["w"]):
            return True
        for k in keep_words:
            for j in range(len(k) - 1):
                if norm(a["w"]) == norm(k[j]) and norm(b["w"]) == norm(k[j + 1]):
                    return True
        return False

    def cost(i, j):
        g = words[i:j + 1]
        if len(g) > MAX_WORDS or len(" ".join(clean(x["w"]) for x in g)) > MAX_CHARS:
            return None
        c = {1: 1.5, 2: 0.2, 3: 0.0}[len(g)]
        for k in range(len(g) - 1):
            if punct.search(g[k]["w"]):
                return None
            if g[k + 1]["t"] - g[k]["e"] >= PAUSE:
                c += 6.0
        last = g[-1]
        ends_hard = bool(punct.search(last["w"]))
        if norm(last["w"]) in FUNCTION and not ends_hard:
            c += 8.0 if len(g) > 1 else 4.0
        if j + 1 < n:
            nxt = words[j + 1]
            if joined(last, nxt):
                c += 10.0
            if ends_hard or nxt["t"] - last["e"] >= PAUSE:
                c -= 0.5
            elif norm(nxt["w"]) in CLAUSE:
                c -= 0.8
            if not ends_hard and nxt["t"] - last["e"] < PAUSE and norm(nxt["w"]) in FUNCTION and norm(nxt["w"]) not in CLAUSE:
                c += 0.0
        return c

    best = [(0.0, -1)] + [(1e18, -1)] * n
    for j in range(n):
        for L in range(1, MAX_WORDS + 1):
            i = j - L + 1
            if i < 0:
                break
            c = cost(i, j)
            if c is None:
                continue
            tot = best[i][0] + c
            if tot < best[j + 1][0]:
                best[j + 1] = (tot, i)
    groups, j = [], n
    while j > 0:
        i = best[j][1]
        groups.append(words[i:j])
        j = i
    return list(reversed(groups))


def timed(groups):
    res = []
    for n, g in enumerate(groups):
        start = round(max(0.0, g[0]["t"] - LEAD), 3)
        end = g[-1]["e"]
        nxt = groups[n + 1][0]["t"] - LEAD if n + 1 < len(groups) else None
        if nxt is not None and end > nxt - 0.01:
            end = nxt - 0.01
        if end - start < 0.2:
            end = start + 0.2
        end = min(end, start + 3.0)
        res.append({"start": start, "end": round(end, 3), "text": " ".join(clean(x["w"]) for x in g)})
    return res


def quiet(res, state_path):
    st = json.load(open(state_path, encoding="utf-8"))
    gs = [g for g in st.get("graphics", []) if g.get("status") == "ok"]
    kept = []
    for c in res:
        cw = {norm(x) for x in c["text"].split() if norm(x)}
        hide = False
        for g in gs:
            gw = {norm(x) for x in g["text"].split() if norm(x)}
            if cw and cw <= gw and c["start"] < g["at"] + g["dur"] and c["end"] > g["at"]:
                hide = True
        if not hide:
            kept.append(c)
    return kept


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("ingest")
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--end", type=float, default=1e9)
    ap.add_argument("--state", default=None)
    ap.add_argument("--keep", default="")
    ap.add_argument("--ops", default=None)
    a = ap.parse_args(argv)
    ing = json.load(open(a.ingest, encoding="utf-8"))
    words = [w for w in ing["words"] if w["t"] >= a.start - 1e-6 and w["e"] <= a.end + 1e-6 and clean(w["w"])]
    res = timed(build(words, [k.strip() for k in a.keep.split(",") if k.strip()]))
    if a.state:
        res = quiet(res, a.state)
    for r in res:
        if a.ops:
            print(json.dumps({"op": "caption", "agent": a.ops, **r}))
        else:
            print("%7.2f %7.2f  %s" % (r["start"], r["end"], r["text"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

## 2. check_caption_groups.py: check the accepted captions

Run it after the captioners finish and again after any re cut. `--size-factor` is the caption font size as a fraction of the short side (0.058 after the fix described in `SKILL.md` step 2).

```python
# file: check_caption_groups.py
#!/usr/bin/env python3
"""Check the accepted captions in project/state.json against the grouping and timing rules.

    python3 check_caption_groups.py project/state.json --ingest project/ingest.json [--width 1080 --height 1920 --font brand/fonts/Inter-Bold.ttf]

ERROR lines are hard problems (the server normally refuses them, a render may break). WARN lines are style problems to fix or defend.
Exit code: 0 no ERROR, 1 at least one ERROR, 2 unreadable input. Standard library only (Pillow is used for the width check when installed).
"""
import argparse, json, os, re, sys

FUNCTION = set("the a an to and or but of your my our for in on at by with from that this these those as if than so is are was were be i we you it because which when while where into about".split())


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def width_of(text, px, font):
    try:
        from PIL import Image, ImageDraw, ImageFont
        if font and os.path.exists(font):
            d = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
            l, t, r, b = d.textbbox((0, 0), text, font=ImageFont.truetype(font, px))
            return r - l
    except Exception:
        pass
    return round(0.6 * px * len(text))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("state")
    ap.add_argument("--ingest", default=None)
    ap.add_argument("--width", type=int, default=None)
    ap.add_argument("--height", type=int, default=None)
    ap.add_argument("--font", default=None)
    ap.add_argument("--size-factor", type=float, default=0.058, help="caption font size as a fraction of the size basis (0.058 in the shipped render)")
    a = ap.parse_args(argv)
    try:
        st = json.load(open(a.state, encoding="utf-8"))
        words = json.load(open(a.ingest, encoding="utf-8"))["words"] if a.ingest else []
    except (OSError, ValueError, KeyError) as e:
        print("cannot read input:", e)
        return 2
    caps = sorted([c for c in st.get("captions", []) if c.get("status") == "ok"], key=lambda c: c["start"])
    gfx = [g for g in st.get("graphics", []) if g.get("status") == "ok"]
    errs, warns = [], []
    prev = None
    for c in caps:
        ws = c["text"].split()
        tag = "%s '%s' %.2f to %.2f" % (c["id"], c["text"], c["start"], c["end"])
        if not 1 <= len(ws) <= 3:
            errs.append("%s: %d words (1 to 3 allowed)" % (tag, len(ws)))
        if len(c["text"]) > 22:
            errs.append("%s: %d characters (22 allowed)" % (tag, len(c["text"])))
        if not 0.2 <= c["end"] - c["start"] <= 3.0:
            errs.append("%s: lasts %.2f s (0.2 to 3.0 allowed)" % (tag, c["end"] - c["start"]))
        if prev and c["start"] < prev["end"] - 0.05:
            errs.append("%s: overlaps %s" % (tag, prev["id"]))
        if ws and norm(ws[-1]) in FUNCTION:
            warns.append("%s: ends on the function word '%s' (try another split)" % (tag, ws[-1]))
        if re.search(r"[.,;:!?]\s*$", c["text"]) or re.search(r"\s[.,;:!?]", c["text"]):
            warns.append("%s: has stray punctuation (captions use the words only)" % tag)
        if c["end"] - c["start"] < 0.35 and len(ws) >= 2:
            warns.append("%s: %.2f s for %d words is too fast to read" % (tag, c["end"] - c["start"], len(ws)))
        if words and ws:
            first = [w for w in words if norm(w["w"]) == norm(ws[0]) and abs(w["t"] - c["start"]) < 0.6]
            last = [w for w in words if norm(w["w"]) == norm(ws[-1]) and abs(w["e"] - c["end"]) < 0.8]
            if first:
                lead = min(first, key=lambda w: abs(w["t"] - c["start"]))["t"] - c["start"]
                if lead < 0:
                    warns.append("%s: starts %.2f s after its first word (late)" % (tag, -lead))
                elif lead > 0.12:
                    warns.append("%s: starts %.2f s before its first word (aim for 0.02 to 0.05)" % (tag, lead))
            if last:
                lag = c["end"] - min(last, key=lambda w: abs(w["e"] - c["end"]))["e"]
                if lag < -0.05:
                    warns.append("%s: ends %.2f s before its last word ends" % (tag, -lag))
                elif lag > 0.5:
                    warns.append("%s: stays %.2f s after its last word" % (tag, lag))
        cw = {norm(x) for x in ws if norm(x)}
        for g in gfx:
            gw = {norm(x) for x in g["text"].split() if norm(x)}
            if cw and cw <= gw and c["start"] < g["at"] + g["dur"] and c["end"] > g["at"]:
                warns.append("%s: repeats the words of graphic %s ('%s') on screen at the same time (quiet window)" % (tag, g["id"], g["text"]))
        if a.width and a.height:
            px = round(a.size_factor * min(a.width, a.height))
            w = width_of(c["text"], px, a.font) + round(px * 1.1)
            if w > a.width - 120:
                errs.append("%s: pill %d px wide does not fit the frame with 60 px margins at %d px text" % (tag, w, px))
        prev = c
    print("%d captions checked" % len(caps))
    for e in errs:
        print("ERROR:", e)
    for w in warns:
        print("WARN:", w)
    if not errs and not warns:
        print("OK")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
```

## 3. caption_highlight.py: optional highlight word drawing (needs Pillow)

Steps to enable highlights, all in your own copy of the editor:

1. In `server.py`, in `op_caption`, accept an optional `hl` field: it must be one word of the text (compare with `norm`) and is stored on the caption item next to `text`.
2. In `render.py`, replace the call that draws the caption PNG by `caption_png_hl(k["text"], k.get("hl"), min(W, H), TOK, p)`. Save this file next to `render.py` and load the tokens as described in `ae-theme-builder`.
3. Add a test to `agent-editor/tests/test_ops.py`: an `hl` word that is not in the text is refused; an `hl` that is in the text is accepted.
4. Render a short window and look at stills of a highlighted group on the lightest and darkest frames.

```python
# file: caption_highlight.py
"""Caption pill with one highlighted word, for render.py (replaces caption_png when you add the optional `hl` field).

Usage inside render.py:
    from caption_highlight import caption_png_hl
    caption_png_hl(k["text"], k.get("hl"), min(W, H), TOK, path)

`hl` is the highlighted word exactly as it appears in the caption text, or None. TOK is the dict from brand/tokens.json
(load_tokens in theme_loader.py). Without TOK a neutral dark pill with white text is drawn.
"""
import os
from PIL import Image, ImageDraw, ImageFont

FALLBACKS = ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/Library/Fonts/Arial Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")


def _font(path, size):
    for p in (path,) + FALLBACKS:
        if p and os.path.exists(p):
            return ImageFont.truetype(p, size)
    try:
        return ImageFont.load_default(size)
    except TypeError:
        return ImageFont.load_default()


def _rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def caption_png_hl(text, hl, basis, tok, path):
    size = max(24, round(basis * 0.058))
    files = tok["fonts"]["files"] if tok else {}
    base = _font(files.get("heading"), size)
    accent = _font(files.get("accent"), round(size * 1.1))
    fill = tuple(tok["caption"]["pill_fill"]) if tok else (18, 20, 30, 220)
    ink = _rgb(tok["caption"]["text"]) if tok else (255, 255, 255, 255)
    hcol = _rgb(tok["caption"]["highlight"]) if tok else ink
    words = text.split()
    probe = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    space = probe.textlength(" ", font=base)
    parts = []
    for w in words:
        f = accent if (hl and w == hl) else base
        parts.append((w, f, hcol if (hl and w == hl) else ink, probe.textlength(w, font=f)))
    asc = max(f.getmetrics()[0] for _, f, _, _ in parts)
    desc = max(f.getmetrics()[1] for _, f, _, _ in parts)
    px, py = round(size * 0.55), round(size * 0.32)
    total = sum(p[3] for p in parts) + space * (len(parts) - 1)
    w_img, h_img = round(total + px * 2), asc + desc + py * 2
    img = Image.new("RGBA", (w_img, h_img), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, w_img - 1, h_img - 1), radius=h_img // 2, fill=fill)
    x = px
    for w, f, col, wd in parts:
        d.text((x, py + asc), w, font=f, fill=col, anchor="ls")
        x += wd + space
    img.save(path)
    return img.size
```
