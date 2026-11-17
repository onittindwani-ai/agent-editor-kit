# Safe zone tools

Save each block into `brand/tools/` (the first comment line gives the file name). They need Pillow (`.venv/bin/pip install pillow`) except `scan_top_band.py`, which needs only ffmpeg, ffprobe and Python. None changes your video.

## 1. safe_zones.json: the numbers (starting values, approximate)

Copy to `brand/safe_zones.json`, replace with your own measurements after the phone test, and keep the file. All tools read it.

```json
# file: safe_zones.json
{
  "note": "Starting values measured on one phone model, approximate. Verify on your own phone with safe_zone_chart.py and edit this file.",
  "canvas": {"w": 1080, "h": 1920},
  "top_reserve_y": 270,
  "text_start_y": 290,
  "status_bar_y": [30, 120],
  "app_header_y": [185, 255],
  "text_limit_y": 1500,
  "chin_limit_y": 1530,
  "youtube_ui_start_y": 1540,
  "instagram_ui_start_y": 1625,
  "right_rail": {"x_start": 900, "y": [980, 1790]},
  "text_x": [60, 1020],
  "card_x": [80, 1000],
  "side_crop_x": 32
}
```

## 2. safe_zone_chart.py: calibration picture for a phone test

```
python3 brand/tools/safe_zone_chart.py --out brand/safe-zone-chart.png
ffmpeg -y -loop 1 -i brand/safe-zone-chart.png -t 3 -r 30 -vf format=yuv420p -c:v libx264 -crf 18 brand/safe-zone-chart.mp4
```

Upload the mp4 as a private, unlisted or "only me" test in each app, never public. Open it on your phone, take screenshots with the app interface visible, and read the numbered lines.

```python
# file: safe_zone_chart.py
#!/usr/bin/env python3
"""Make a calibration picture for measuring your own phone's overlays (needs Pillow).

    python3 safe_zone_chart.py --out brand/safe-zone-chart.png [--w 1080 --h 1920]

How to use it: turn the PNG into a 3 second video (see SKILL.md), upload it as a private or unlisted test on the platform, open it on
your own phone, take screenshots, and read where the app icons, captions and bars cover the numbered grid lines. Write the measured
values into brand/safe_zones.json. Never upload the test publicly.
"""
import argparse
from PIL import Image, ImageDraw, ImageFont


def font(size):
    for p in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size)
    except TypeError:
        return ImageFont.load_default()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="safe-zone-chart.png")
    ap.add_argument("--w", type=int, default=1080)
    ap.add_argument("--h", type=int, default=1920)
    a = ap.parse_args()
    img = Image.new("RGB", (a.w, a.h), (245, 245, 245))
    d = ImageDraw.Draw(img)
    f, fs = font(30), font(22)
    for y in range(0, a.h + 1, 50):
        major = y % 100 == 0
        d.line((0, y, a.w, y), fill=(30, 30, 30) if major else (190, 190, 190), width=3 if major else 1)
        if major:
            d.text((8, y + 3), "y %d" % y, font=f, fill=(200, 0, 0))
            d.text((a.w - 130, y + 3), "y %d" % y, font=f, fill=(200, 0, 0))
    for x in range(0, a.w + 1, 50):
        major = x % 100 == 0
        d.line((x, 0, x, a.h), fill=(30, 30, 30) if major else (190, 190, 190), width=3 if major else 1)
        if major and x:
            d.text((x + 3, 6), "x %d" % x, font=fs, fill=(0, 0, 200))
            d.text((x + 3, a.h // 2), "x %d" % x, font=fs, fill=(0, 0, 200))
    d.rectangle((0, 0, a.w - 1, a.h - 1), outline=(0, 160, 0), width=6)
    img.save(a.out)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
```

## 3. overlay_zones.py: draw the zones over a still

```
ffmpeg -ss 12.5 -i out/edit.mp4 -frames:v 1 stills/t12.5.png
.venv/bin/python brand/tools/overlay_zones.py stills/t12.5.png --out stills/t12.5-zones.png --zones brand/safe_zones.json
```

```python
# file: overlay_zones.py
#!/usr/bin/env python3
"""Draw the safe zones over a still so you can see what the app interface may cover (needs Pillow).

    python3 overlay_zones.py still.png --out still-zones.png [--zones brand/safe_zones.json]

Colours: red top band (plain background only), orange below the text limit (no text, eyes, mouth, chin), violet right rail
(no text), blue cropped sides, green rectangle the text window. Look at the result; nothing important may sit in a coloured zone.
The numbers are for a 1080 by 1920 canvas and are scaled to the still. Edit brand/safe_zones.json with your own measurements.
"""
import argparse, json, os
from PIL import Image, ImageDraw

DEFAULT = {"canvas": {"w": 1080, "h": 1920}, "top_reserve_y": 270, "text_start_y": 290, "text_limit_y": 1500, "chin_limit_y": 1530,
           "right_rail": {"x_start": 900, "y": [980, 1790]}, "text_x": [60, 1020], "side_crop_x": 32}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("still")
    ap.add_argument("--out", default=None)
    ap.add_argument("--zones", default=None)
    a = ap.parse_args()
    z = dict(DEFAULT)
    if a.zones and os.path.exists(a.zones):
        z.update(json.load(open(a.zones, encoding="utf-8")))
    im = Image.open(a.still).convert("RGBA")
    sx, sy = im.width / z["canvas"]["w"], im.height / z["canvas"]["h"]
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    R = lambda x0, y0, x1, y1, c: d.rectangle((x0 * sx, y0 * sy, x1 * sx, y1 * sy), fill=c)
    W, H = z["canvas"]["w"], z["canvas"]["h"]
    R(0, 0, W, z["top_reserve_y"], (255, 0, 0, 90))
    R(0, z["text_limit_y"], W, H, (255, 140, 0, 90))
    rr = z["right_rail"]
    R(rr["x_start"], rr["y"][0], W, rr["y"][1], (150, 0, 255, 90))
    R(0, 0, z["side_crop_x"], H, (0, 90, 255, 110))
    R(W - z["side_crop_x"], 0, W, H, (0, 90, 255, 110))
    d.rectangle((z["text_x"][0] * sx, z["text_start_y"] * sy, z["text_x"][1] * sx, z["text_limit_y"] * sy), outline=(0, 180, 0, 255), width=4)
    out = a.out or os.path.splitext(a.still)[0] + "-zones.png"
    Image.alpha_composite(im, ov).convert("RGB").save(out)
    print("wrote", out)


if __name__ == "__main__":
    main()
```

## 4. scan_top_band.py: flag busy detail in the top band and the right rail

```
python3 brand/tools/scan_top_band.py out/edit.mp4 --fps 2 --zones brand/safe_zones.json
```

It decodes at low priority and a quarter of the size. Calibrate it once on a plain colour video (must print OK) and on a busy test pattern (must flag). A flag is a pointer: open the frame at that time and look.

```python
# file: scan_top_band.py
#!/usr/bin/env python3
"""Scan a vertical video for busy detail in the top band and the right rail. A pointer, not a verdict: look at every flagged time.

    python3 scan_top_band.py video.mp4 [--fps 2] [--top 270] [--threshold 6.0] [--spread 14.0] [--zones brand/safe_zones.json]

Frames are decoded by ffmpeg at low priority, scaled to a quarter size, turned to grey, and the mean absolute difference between
neighbouring pixels (an edge measure) and the standard deviation of the grey values are computed for the top band and for the right rail. A plain
background gives low values; text, faces, card edges and busy video give high ones (the right rail limits are 1.5 times higher). Exit code: 0 nothing flagged, 1 something flagged, 2 cannot read the
video (it must be 9:16). Standard library only; ffmpeg and ffprobe must be installed.
"""
import argparse, json, os, subprocess, sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--fps", type=float, default=2.0)
    ap.add_argument("--top", type=int, default=None)
    ap.add_argument("--threshold", type=float, default=6.0, help="edge limit (mean neighbour difference)")
    ap.add_argument("--spread", type=float, default=14.0, help="limit for the standard deviation of grey values in the zone")
    ap.add_argument("--zones", default=None)
    a = ap.parse_args()
    z = {"top_reserve_y": 270, "right_rail": {"x_start": 900, "y": [980, 1790]}}
    if a.zones and os.path.exists(a.zones):
        z.update(json.load(open(a.zones, encoding="utf-8")))
    top = a.top or z["top_reserve_y"]
    pr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", a.video], capture_output=True, text=True)
    try:
        w, h = [int(x) for x in pr.stdout.strip().split(",")[:2]]
    except ValueError:
        print("cannot probe the video")
        return 2
    if abs(h / w - 16 / 9) > 0.05:
        print("this scan is for 9:16 video; got %dx%d" % (w, h))
        return 2
    qw, qh = 270, 480
    cmd = ["nice", "-n", "15", "ffmpeg", "-v", "error", "-threads", "2", "-i", a.video, "-vf", "fps=%s,scale=%d:%d,format=gray" % (a.fps, qw, qh), "-f", "rawvideo", "-"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    size = qw * qh
    ty = max(1, round(top * qh / 1920))
    rx0, ry0, ry1 = round(z["right_rail"]["x_start"] * qw / 1080), round(z["right_rail"]["y"][0] * qh / 1920), round(z["right_rail"]["y"][1] * qh / 1920)

    def edge(buf, x0, y0, x1, y1):
        """Return (mean absolute neighbour difference, standard deviation of the grey values)."""
        tot, n, vals = 0, 0, []
        for y in range(y0, y1):
            row = buf[y * qw + x0: y * qw + x1]
            vals.extend(row)
            for i in range(1, len(row)):
                tot += abs(row[i] - row[i - 1])
                n += 1
        mean = sum(vals) / max(1, len(vals))
        sd = (sum((v - mean) ** 2 for v in vals) / max(1, len(vals))) ** 0.5
        return tot / max(1, n), sd

    idx, flagged = 0, []
    while True:
        buf = proc.stdout.read(size)
        if len(buf) < size:
            break
        t = idx / a.fps
        (et, st), (er, sr) = edge(buf, 0, 0, qw, ty), edge(buf, rx0, ry0, qw, ry1)
        if et > a.threshold or st > a.spread:
            flagged.append((t, "top band", et, st))
        if er > a.threshold * 1.5 or sr > a.spread * 1.5:
            flagged.append((t, "right rail", er, sr))
        idx += 1
    proc.wait()
    print("%d frames scanned at %s fps, top band y 0 to %d, threshold %.1f" % (idx, a.fps, top, a.threshold))
    for t, name, v, sd in flagged:
        print("FLAG %6.2f s  %-10s edge %.1f spread %.1f  (look at this frame)" % (t, name, v, sd))
    if not flagged:
        print("OK: no busy detail found in the checked zones (still look at overlay stills)")
    return 1 if flagged else 0


if __name__ == "__main__":
    sys.exit(main())
```
