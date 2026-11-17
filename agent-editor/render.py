#!/usr/bin/env python3
"""Turn the shared timeline into a real video with ffmpeg.

Cuts come from the ORIGINAL file when it still exists (so the render is full resolution, the proxy is only for
the screen). Kept cuts are joined with 12 ms audio fades, punch zooms are split segments cropped in 12 percent,
blur_in is a 0.16 s blur, graphics and captions are PNG overlays drawn with Pillow (graphics slide in and fade),
music is mixed under the voice and the result is normalised to -16 LUFS.
"""
import json, os, re, subprocess, sys, tempfile

ZOOM = 1.12
AMBER = (255, 176, 32, 255)
INK = (16, 20, 36, 255)
FONTS = ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/Library/Fonts/Arial Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
SAMPLES = {"stat_card": "204", "lower_third": "Claude Code", "chapter_title": "The CRM test", "highlight": "no repeats"}
# where each template sits: (x as fraction of width or 'c', y fraction of height, from right?)
POS = {"stat_card": ("r", 0.10), "lower_third": ("l", 0.62), "chapter_title": ("c", 0.38), "highlight": ("l", 0.16)}

def font(size):
    from PIL import ImageFont
    for p in FONTS:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def tsize(d, text, f):
    l, t, r, b = d.textbbox((0, 0), text, font=f)
    return l, t, r - l, b - t

def caption_png(text, H, path):
    from PIL import Image, ImageDraw
    size = max(24, round(H * 0.058))
    f = font(size)
    d = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    l, t, tw, th = tsize(d, text, f)
    px, py = round(size * 0.55), round(size * 0.32)
    w, h = tw + px * 2, th + py * 2
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    dr.rounded_rectangle((0, 0, w - 1, h - 1), radius=h // 2, fill=(18, 20, 30, 220))
    dr.text((px - l, py - t), text, font=f, fill=(255, 255, 255, 255))
    img.save(path)

def graphic_png(tpl, text, H, path):
    from PIL import Image, ImageDraw
    s = H / 1080.0
    d0 = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    if tpl == "stat_card":
        f = font(round(112 * s))
        l, t, tw, th = tsize(d0, text, f)
        w, h = tw + round(90 * s), th + round(80 * s)
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((0, 0, w - 1, h - 1), radius=round(30 * s), fill=(255, 255, 255, 244))
        d.rounded_rectangle((round(26 * s), round(16 * s), w - round(26 * s), round(26 * s)), radius=round(5 * s), fill=AMBER)
        d.text(((w - tw) // 2 - l, (h - th) // 2 - t + round(10 * s)), text, font=f, fill=INK)
    elif tpl == "lower_third":
        f = font(round(52 * s))
        l, t, tw, th = tsize(d0, text, f)
        w, h = tw + round(120 * s), th + round(56 * s)
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((0, 0, w - 1, h - 1), radius=round(14 * s), fill=(16, 20, 36, 236))
        d.rounded_rectangle((0, 0, round(16 * s), h - 1), radius=round(8 * s), fill=AMBER)
        d.text((round(60 * s) - l, (h - th) // 2 - t), text, font=f, fill=(255, 255, 255, 255))
    elif tpl == "chapter_title":
        f = font(round(96 * s))
        l, t, tw, th = tsize(d0, text, f)
        w, h = tw + round(140 * s), th + round(110 * s)
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((0, 0, w - 1, h - 1), radius=round(26 * s), fill=(10, 12, 22, 214))
        d.text(((w - tw) // 2 - l, round(26 * s) - t), text, font=f, fill=(255, 255, 255, 255))
        d.rounded_rectangle((round(70 * s), h - round(36 * s), w - round(70 * s), h - round(26 * s)), radius=round(5 * s), fill=AMBER)
    else:  # highlight
        f = font(round(58 * s))
        l, t, tw, th = tsize(d0, text, f)
        w, h = tw + round(80 * s), th + round(44 * s)
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((0, 0, w - 1, h - 1), radius=h // 2, fill=AMBER)
        d.text(((w - tw) // 2 - l, (h - th) // 2 - t), text, font=f, fill=INK)
    img.save(path)
    return img.size

def make_templates(proj):
    """Preview tiles for the media pool, drawn once."""
    d = os.path.join(proj, "graphics")
    os.makedirs(d, exist_ok=True)
    for k, v in SAMPLES.items():
        p = os.path.join(d, f"tpl_{k}.png")
        if not os.path.exists(p):
            graphic_png(k, v, 540, p)

def run_cmd(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)

def render(state, ing, here, out, progress, music_root):
    m = ing["media"]
    origin = m.get("origin_path")
    use_origin = bool(origin and os.path.exists(origin))
    src = origin if use_origin else os.path.join(here, m["file"])
    pre = ["-ss", str(m.get("origin_start", 0)), "-t", str(m["duration"])] if use_origin else []
    pr = json.loads(run_cmd(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "json", src]).stdout)["streams"][0]
    W, H = int(pr["width"]), int(pr["height"])
    cuts = sorted([c for c in state["cuts"] if c["status"] == "ok"], key=lambda c: c["start"])
    if not cuts:
        raise RuntimeError("no accepted cuts yet")
    fx = [f for f in state["fx"] if f["status"] == "ok"]
    segs = []
    for c in cuts:
        zs = sorted((f["at"], min(c["end"], f["at"] + f["dur"])) for f in fx if f["type"] == "punch_zoom" and c["start"] <= f["at"] < c["end"])
        cur = c["start"]
        for a, b in zs:
            if a - cur > 0.05:
                segs.append((cur, a, 1.0))
            segs.append((a, b, ZOOM))
            cur = b
        if c["end"] - cur > 0.05:
            segs.append((cur, c["end"], 1.0))
    starts, acc = [], 0.0
    for a, b, z in segs:
        starts.append(acc)
        acc += b - a
    total = acc

    def to_out(t):
        for (a, b, z), o in zip(segs, starts):
            if a - 1e-3 <= t <= b + 1e-3:
                return o + (t - a)
        return None

    tmp = tempfile.mkdtemp(prefix="ae-")
    inputs = [*pre, "-i", src]
    n_in = 1
    caps = []
    for k in [k for k in state["captions"] if k["status"] == "ok"]:
        s, e = to_out(k["start"]), to_out(k["end"])
        if s is None:
            continue
        e = e if e is not None else s + (k["end"] - k["start"])
        p = os.path.join(tmp, f"{k['id']}.png")
        caption_png(k["text"], min(W, H), p)
        inputs += ["-i", p]
        caps.append((n_in, s, e))
        n_in += 1
    gfx = []
    for g in [g for g in state.get("graphics", []) if g["status"] == "ok"]:
        s = to_out(g["at"])
        if s is None:
            continue
        e = min(total, s + g["dur"])
        p = os.path.join(tmp, f"{g['id']}.png")
        w, h = graphic_png(g["template"], g["text"], min(W, H), p)
        inputs += ["-framerate", "30", "-loop", "1", "-t", f"{total:.3f}", "-i", p]
        gfx.append((n_in, s, e, g["template"], w, h))
        n_in += 1
    music = state.get("music")
    mi = None
    if music and music.get("status") == "ok":
        mi = n_in
        inputs += ["-stream_loop", "-1", "-i", os.path.join(music_root, music["file"])]
        n_in += 1
    f, labels = [], []
    for i, (a, b, z) in enumerate(segs):
        d = b - a
        vz = f",crop=iw/{z}:ih/{z}:(iw-iw/{z})/2:(ih-ih/{z})/2,scale={W}:{H}:flags=lanczos" if z != 1.0 else ""
        f.append(f"[0:v]trim=start={a}:end={b},setpts=PTS-STARTPTS{vz},setsar=1,fps=30[v{i}]")
        f.append(f"[0:a]atrim=start={a}:end={b},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,afade=t=out:st={max(0, d - 0.012):.3f}:d=0.012[a{i}]")
        labels.append(f"[v{i}][a{i}]")
    f.append("".join(labels) + f"concat=n={len(segs)}:v=1:a=1[vc][ac]")
    last = "vc"
    for b in [x for x in fx if x["type"] == "blur_in"]:
        t = to_out(b["at"])
        if t is not None:
            f.append(f"[{last}]boxblur=14:enable='between(t,{t:.3f},{t + 0.16:.3f})'[bb{b['id']}]")
            last = f"bb{b['id']}"
    for i, (ix, s, e, tpl, w, h) in enumerate(gfx):
        side, fy = POS[tpl]
        x = {"r": f"W-w-{int(W * 0.06)}", "l": f"{int(W * 0.06)}", "c": "(W-w)/2"}[side]
        y0 = int(H * fy)
        f.append(f"[{ix}:v]format=rgba,fade=t=in:st={s:.3f}:d=0.22:alpha=1,fade=t=out:st={max(s, e - 0.22):.3f}:d=0.22:alpha=1[g{i}]")
        f.append(f"[{last}][g{i}]overlay=x={x}:y='{y0}+{int(H * 0.035)}*pow(max(0,1-(t-{s:.3f})/0.28),2)':enable='between(t,{s:.3f},{e:.3f})':eof_action=pass[og{i}]")
        last = f"og{i}"
    for i, (ix, s, e) in enumerate(caps):
        f.append(f"[{last}][{ix}:v]overlay=x=(W-w)/2:y=H*0.78:enable='between(t,{s:.3f},{e:.3f})'[o{i}]")
        last = f"o{i}"
    if mi is not None:
        f.append(f"[{mi}:a]volume={music['volume_db']}dB,atrim=0:{total:.3f},afade=t=out:st={max(0, total - 1.5):.3f}:d=1.5[m]")
        f.append("[ac][m]amix=inputs=2:duration=first:normalize=0[am]")
        f.append("[am]loudnorm=I=-16:TP=-1:LRA=11[aout]")
    else:
        f.append("[ac]loudnorm=I=-16:TP=-1:LRA=11[aout]")
    cmd = ["nice", "-n", "15", "ffmpeg", "-v", "error", "-y", "-threads", "4", *inputs, "-filter_complex", ";".join(f),
           "-map", f"[{last}]", "-map", "[aout]", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-t", f"{total:.3f}", "-movflags", "+faststart", "-progress", "pipe:1", "-nostats", out]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    for line in proc.stdout:
        mm = re.match(r"out_time_ms=(\d+)", line)
        if mm and total:
            progress(min(0.99, int(mm.group(1)) / 1e6 / total))
    err = proc.stderr.read()
    if proc.wait():
        raise RuntimeError(err[-600:] or "ffmpeg failed")
    return {"duration": total, "segments": len(segs), "captions": len(caps), "graphics": len(gfx), "size": f"{W}x{H}", "from_original": use_origin}

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    st = json.load(open(os.path.join(here, "project", "state.json")))
    ing = json.load(open(os.path.join(here, "project", "ingest.json")))
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "out", "edit.mp4")
    print(render(st, ing, here, out, lambda f: None, os.environ.get("MUSIC_ROOT", os.path.join(here, "music"))))
