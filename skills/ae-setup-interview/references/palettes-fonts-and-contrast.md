# Palettes, fonts and contrast for round 6

These are starting sets to show the user as options. They are neutral and invented for this kit; none belongs to a brand. After the user chooses, adjust one value at a time on request, then re check contrast.

## 1. The seven palette roles

| Role | Meaning | Used for |
| --- | --- | --- |
| `bg` | the ground | scene backgrounds, behind graphics |
| `surface` | a card sitting on the ground | stat cards, lower thirds, chapter cards |
| `ink` | main text | headlines, caption text on light surfaces |
| `muted` | secondary text | labels, source lines |
| `accent` | the one emphasis colour | key word, underline, active element |
| `ok` | good, done, chosen | checks, positive states |
| `warn` | caution, problem | warnings, problems |

Rules to tell the user: one accent per video; an accent keeps one meaning inside a video; ok and warn appear only when the script talks about good or bad; third party brand colours appear only inside their own tile.

## 2. Five looks with hex values (show these)

| Look | bg | surface | ink | muted | accent | ok | warn |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A. Light and clean | #F4F6FA | #FFFFFF | #14181F | #5B6475 | #1F6FEB | #1E8E4E | #C26A00 |
| B. Dark and premium | #0B0D12 | #171A22 | #F2F4F8 | #9AA3B2 | #8B7CFF | #3DDC84 | #FFB020 |
| C. Warm and earthy | #F3EBDD | #FBF6EC | #2B2118 | #6E5E4C | #B5532B | #3F7D3A | #B36B00 |
| D. Bold and bright | #FFE14D | #FFFFFF | #111111 | #444444 | #E8236B | #12805C | #B54708 |
| E. Minimal monochrome | #FAFAFA | #FFFFFF | #151515 | #6A6A6A | #D93F0B | #1E7F4F | #B7791F |

Accent families if the user picks a colour first (use as `accent`, light looks first, dark looks second): blue #1F6FEB / #5AA2FF, green #17803D / #4ADE80, orange #D9560B / #FF9A3D, purple #6D4AFF / #A58BFF, red or pink #D6246E / #FF6BA0.

## 3. Contrast check (do this before writing the file)

Contrast ratio between two colours uses relative luminance. Targets:
- `ink` on `bg` and `ink` on `surface`: at least 7 (aim) and never under 4.5.
- `muted` on `bg` and on `surface`: at least 4.5.
- `accent` on `bg` and on `surface`: at least 3 (it is used for large or bold text and shapes). If the accent is used as text on a surface, aim for 4.5.
- Card step: `surface` must be clearly different from `bg`, either at least a 6 percent difference in lightness or a visible border plus shadow. A white card on an off white ground with no border fails.

Runnable check (Python 3, standard library only):

```python
def lum(h):
    h = h.lstrip("#"); r, g, b = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)
def ratio(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)
import json
t = json.load(open("brand/theme.json"))["palette"]
for name, (a, b, need) in {
    "ink on bg": (t["ink"], t["bg"], 4.5), "ink on surface": (t["ink"], t["surface"], 4.5),
    "muted on bg": (t["muted"], t["bg"], 4.5), "muted on surface": (t["muted"], t["surface"], 4.5),
    "accent on bg": (t["accent"], t["bg"], 3.0), "accent on surface": (t["accent"], t["surface"], 3.0)}.items():
    r = ratio(a, b); print(f"{'OK  ' if r >= need else 'FAIL'} {name}: {r:.2f} (need {need})")
```

If something fails, change the lighter or darker side of that colour in small steps (about 5 percent), show the user the new hex, and re run.

## 4. Fonts

Rules:
- At most two families visible in one frame. Role mapping: `heading` (headlines, numbers), `body` (captions, labels), `accent` (one emphasis word, italic by default).
- The kit bundles no font files. The user supplies each font file or confirms the family is installed and licensed for video use. Many families named below are published under the SIL Open Font License; the user must check the licence of the exact files.
- Pillow (used by the shipped renderer) draws from a TrueType or OpenType file path, so each chosen family needs a bold file for captions. `ae-theme-builder` maps the choice into the renderer.

| Option | heading | body | accent |
| --- | --- | --- | --- |
| A. Modern sans plus italic serif | Inter Bold | Inter Medium | a serif italic such as Fraunces Italic |
| B. Rounded friendly | Poppins Bold | Nunito Semibold | Poppins Italic |
| C. Bold condensed | Bebas Neue | Inter Medium | Inter Italic |
| D. Classic serif | Playfair Display Bold | Source Sans Semibold | Playfair Display Italic |
| E. Technical mono | Space Grotesk Bold | Inter Medium | JetBrains Mono Medium |

## 5. Background handling summary

| Type | `path` | Notes |
| --- | --- | --- |
| `solid` | null | uses `palette.bg` |
| `gradient` | null | convention: a soft vertical blend from `palette.bg` to `palette.surface`; keep contrast checks against both ends |
| `image` | relative path inside `brand/` | the user owns it; keep important content off busy areas |
| `video` | relative path inside `brand/` | a loop the user owns; use a different start point per scene; no sound |
| `none` | null | graphics sit directly on the footage |

## 6. Radius and shadow

Radius is one number in pixels at 1080 wide (scale for other sizes): 8, 16, 28, 44. Shadow `soft` means a gentle blurred shadow under cards; `none` means flat. Do not mix a large radius on cards with a small radius on buttons in one video.
