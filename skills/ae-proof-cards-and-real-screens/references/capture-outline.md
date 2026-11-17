# Page capture outline (Python and Playwright, hedged)

This is an outline, not a guaranteed recipe. Browser automation libraries change between versions: test on the real page, read the output and adjust. It captures a public page, finds exact phrase rectangles and writes a JSON of rectangles. Use only on public pages, never while logged in.

Prerequisites (the user installs them, the agent asks first): Python 3, the `playwright` package and a browser it can drive, or any other headless browser tool the user already has. Pillow for stitching.

```python
import json, sys
from playwright.sync_api import sync_playwright
from PIL import Image

URL = sys.argv[1]
PHRASES = json.load(open(sys.argv[2]))   # {"key": "exact text on the page"}
OUT = sys.argv[3]
CLIP_H = 6000   # css px per capture clip; tall pages glitch if captured in one shot
SCALE = 2

FIND = """
(phrase) => {
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const nodes = []; let full = '';
  while (walker.nextNode()) { nodes.push({n: walker.currentNode, s: full.length}); full += walker.currentNode.nodeValue; }
  const flat = full.replace(/\\s+/g, ' ');
  // map normalised index back is approximate: search the raw text with flexible whitespace
  const esc = phrase.trim().replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&').replace(/\\s+/g, '\\\\s+');
  const m = new RegExp(esc).exec(full);
  if (!m) return null;
  const start = m.index, end = m.index + m[0].length;
  const range = document.createRange();
  for (const {n, s} of nodes) {
    const e = s + n.nodeValue.length;
    if (start >= s && start < e) range.setStart(n, start - s);
    if (end > s && end <= e) range.setEnd(n, end - s);
  }
  const rects = Array.from(range.getClientRects()).map(r => ({x: r.x + scrollX, y: r.y + scrollY, w: r.width, h: r.height}));
  return rects;
}
"""

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1280, "height": 900}, device_scale_factor=SCALE)
    page.goto(URL, wait_until="networkidle")
    # hide obvious overlays WITHOUT editing text (adjust selectors for the page)
    page.add_style_tag(content="[id*=cookie],[class*=cookie],[class*=sticky]{display:none !important}")
    height = page.evaluate("document.documentElement.scrollHeight")
    rects = {}
    for key, phrase in PHRASES.items():
        r = page.evaluate(FIND, phrase)
        rects[key] = r if r else "NOT FOUND"
    clips = []
    y = 0
    while y < height:
        h = min(CLIP_H, height - y)
        path = f"{OUT}/clip_{len(clips)}.png"
        page.screenshot(path=path, clip={"x": 0, "y": y, "width": 1280, "height": h}, full_page=True)
        clips.append((path, h)); y += h
    browser.close()

# stitch
total = sum(h for _, h in clips) * SCALE
img = Image.new("RGB", (1280 * SCALE, total), "white")
off = 0
for path, h in clips:
    img.paste(Image.open(path), (0, off)); off += h * SCALE
img.save(f"{OUT}/page_full.png")
json.dump({"scale": SCALE, "rects": rects, "url": URL}, open(f"{OUT}/page_rects.json", "w"), indent=1)
print("NOT FOUND:", [k for k, v in rects.items() if v == "NOT FOUND"])
```

Notes:
- "NOT FOUND" means the page text differs from your phrase (curly quotes, non breaking spaces, a different word). Fix the phrase from the page, never guess.
- The rectangles are in css pixels of the full page; multiply by `scale` for image pixels.
- Check the stitched image around the clip boundaries for seams.
- For a scrolling animation, scale the stitched image to about 1500 px wide and keep it under about 16,000 px tall.
- If the page blocks automated access, do not work around it. Ask the user for a screenshot.
- Always look at the capture before using it.
