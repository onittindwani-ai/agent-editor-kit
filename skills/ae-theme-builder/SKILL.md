---
name: ae-theme-builder
description: Turns the user's visual answers in brand/profile.md and brand/theme.json into a complete working theme (palette roles, 60/30/10 shares, measured contrast, type pairing, background handling, shape and shadow, a derived tokens file and a preview sheet) and explains how the Agent Editor render and Remotion graphics read it. Use when the user says "set up my look", "pick my colours", "make a theme", "change the fonts", "my captions look off brand", "make it darker", or when any skill finds theme.json missing, invalid or failing a contrast check.
---

# ae-theme-builder

Read `brand/profile.md`. If it is missing or a section you need (`## Visual theme`, `## Captions`, `## Platforms and formats`, `## Rules`) is empty, stop and run `ae-setup-interview` for that section (ask the user, with options), do not guess. Also read `brand/theme.json` if it exists.

Your job is to make one theme that every other skill can read without asking again: captions, graphic cards, proof cards, counters, chapter titles, thumbnails briefs. The user chooses the look. You make the choice measurable, check it, and wire it in.

## What you produce

| File | Role | Rules |
| --- | --- | --- |
| `brand/theme.json` | The user's choices. Source of truth. Fixed schema (below). | Change only on the user's word. Copy to `brand/theme.v<N>.json` before any change. |
| `brand/tokens.json` | Derived values: RGBA colours, contrast table, text on accent, caption pill, rim and shadow numbers, resolved font files. | Rebuilt by script every time. Never hand edited. |
| `brand/fonts/` | Font files the user has the right to use (static Bold, Medium or Regular, and an Italic). | The kit bundles no fonts. Ask the user to bring or download their own and confirm the licence allows video use. |
| `brand/backgrounds/` | Background image or video the user supplies. | Never edited in place. Copy first. |
| `brand/theme-sheet.png` | Preview of palette, caption pill, stat card, lower third, chapter title, highlight, state chips and a glyph test. | The user approves this picture before anything is built on it. |

`brand/theme.json` schema (exactly):

```
{"palette":{"bg":"#RRGGBB","surface":"#RRGGBB","ink":"#RRGGBB","muted":"#RRGGBB","accent":"#RRGGBB","ok":"#RRGGBB","warn":"#RRGGBB"},
 "fonts":{"heading":"Family","body":"Family","accent":"Family"},
 "background":{"type":"solid|gradient|image|video|none","path":null},
 "radius":28,"shadow":"soft|none"}
```

Font values are family names. The tools look for matching files in `brand/fonts/`. `background.path` is a path inside the project or null.

## Step 1: Interview rounds (only for what the profile does not answer)

Show the options with a short picture in words. The user may answer freely; map the answer to the closest option and say which one you chose.

Round A, mood:
1. Calm editorial: warm off white, deep ink, one earthy accent. Feels like a printed magazine.
2. Bold high contrast: near black, white text, one hot accent. Feels like a trailer.
3. Fresh and friendly: cream or light tint, dark ink, one bright accent. Feels like a good tutorial.
4. Cool and professional: pale blue grey, navy ink, one blue accent. Feels like a briefing.
5. Soft natural: sage or sand, dark green ink, one deep green accent. Feels like a wellness brand.

Round B, existing brand: "Do you already have brand colours, a logo or fonts?" Options: (1) yes, I will give hex codes, (2) yes, sample them from my logo file, (3) no, pick for me from the mood, (4) I have fonts but no colours. Existing colours are used as given. If a colour fails a check, show the failing number and a nearest passing suggestion, and let the user decide. Never change a brand colour silently.

Round C, surfaces and shape: flat cards, frosted glass (translucent card over the background), or outlined cards? Corner style: crisp (radius 8 to 14), soft (radius 24 to 32, the default 28), or pill (very round). Shadow: soft or none.

Round D, type: (1) one clean heavy sans for everything plus a light italic serif for one highlight word per phrase, (2) one sans only, (3) a serif headline with a sans body, (4) the user's own fonts. Check the language and symbols the videos need (accents, currency signs, non Latin scripts) because many display fonts lack them.

Round E, background behind graphics: solid colour, soft gradient, the user's own image, the user's own looping video, or none (graphics sit over footage only). Round F: caption pill style, `surface` (light or dark card from the theme, default) or `inverse` (pill in the ink colour with background coloured text). If `## Captions` in the profile already says this, use it.

Write the answers into `## Visual theme` of `brand/profile.md` as plain lines (mood, brand colours, shape, type, background, caption pill). Do not rewrite other sections.

## Step 2: Palette roles

Seven roles, each with one job. A role keeps its meaning across the whole video.

| Role | Paints | Rules |
| --- | --- | --- |
| `bg` | The scene background and the plate behind graphics | Largest area. No pattern, or a quiet one. |
| `surface` | Cards, caption pills, lower thirds, stat cards | Must separate from `bg` (Step 4). |
| `ink` | All primary text on `bg` and `surface` | Highest contrast colour in the set. |
| `muted` | Secondary text, source lines, labels | Still readable: 4.5 or more. |
| `accent` | The one colour that says "look here": highlight word, underline bar, stat bar, key mark | Exactly one accent colour per video. |
| `ok` | Done, chosen, correct | Never used decoratively. |
| `warn` | Problem, risk, wrong | Never used decoratively. |

Colour is a code: inside one video a colour keeps one meaning and never swaps. Third party brand colours (a company logo) appear only inside their own tile or crop, never as a second accent for the video.

## Step 3: Make a palette when the user wants one picked

Start from the mood and the user's brand colour if any. Procedure:
1. Choose `ink` first: a very dark colour with a slight tint (never pure black on a light theme, never pure white on a dark theme). Tint toward the accent hue by 3 to 6 percent.
2. Choose `bg` as the lightest or darkest neutral for the mood, with the same tint family.
3. Choose `surface` one step away from `bg` (lighter on a dark theme, white or a tint on a light theme).
4. Choose `muted` midway between `ink` and `bg`, then move it until it passes 4.5 on both `bg` and `surface`.
5. Choose `accent` with enough contrast to be text on `bg` (Step 4 targets). If the user loves a light accent (yellow, light green) on a light theme, keep the colour for fills and marks and use `ink` for any text on it.
6. Choose `ok` and `warn` as plain green and amber or orange tuned to pass 3.0 on `bg`. They are rare, so they can be quieter than the accent.

Run the script (Step 4), look at the sheet (Step 8), then adjust one role at a time.

## Step 4: Measure contrast and separation (the luminance check method)

The tool `theme_tokens.py` (code in `references/theme-scripts.md`; save it to `brand/tools/`) does the numbers. The method, so you can also do it by hand:

1. Convert each hex channel c (0 to 255) to a linear value: c/255, then if that is 0.04045 or less divide by 12.92, otherwise ((c/255 + 0.055) / 1.055) raised to 2.4.
2. Relative luminance L = 0.2126 R + 0.7152 G + 0.0722 B (linear values).
3. Contrast ratio between two colours = (L_lighter + 0.05) / (L_darker + 0.05).

Minimums and targets for text and marks drawn at video sizes (captions are large, so 3.0 is allowed for large display text only):

| Pair | Minimum | Target | Why |
| --- | --- | --- | --- |
| ink on bg, ink on surface | 4.5 | 7 or more | All body and caption text |
| muted on bg, muted on surface | 4.5 | 4.5 or more | Small labels must stay readable on a phone |
| accent on bg, accent on surface | 3.0 | 4.5 or more | Highlight word (large text), bars, marks. Under 36 px text needs 4.5 |
| ok or warn on bg | 3.0 | 4.5 or more | Chips and marks |
| text on accent (`on_accent`) | 4.5 | 7 | The tool picks ink, bg, white or black, whichever is best |

Surface separation: the ratio of `surface` to `bg` must be 1.25 or more. Below that, a card needs a rim of 2 px (in the `rim` token, a mix of surface and ink) plus a soft contact shadow. Light themes almost always take the rim and shadow route because white on cream measures about 1.1 to 1.2. A card with neither a 1.25 ratio nor a rim and shadow is a fail: it looks like a smudge, not a card.

Fix recipe when a pair fails: run with `--fix`. It moves the colour toward black or white in 2 percent steps and prints the first value that passes. Show the user the before and after hex and let them accept it. Typical result: a pale yellow accent on cream becomes a darker mustard, or the user keeps the yellow for fills and uses `ink` for text on it.

Worked example (a placeholder theme called calm paper, bakery explainer): bg `#F4EFE6`, surface `#FFFFFF`, ink `#1E2430`, muted `#5B6270`, accent `#B93A0B`. Results: ink on bg 13.6, ink on surface 15.6, muted on bg 5.4, accent on bg 5.0, surface vs bg 1.15 so a rim and shadow are required, text on accent is white at 5.7. A first attempt with accent `#D9480F` gave 4.0 on bg and the highlight word looked weak at 40 px, so it was darkened.

## Step 5: The 60/30/10 shares, applied correctly

In video terms the shares are of the visible area of a graphic scene (a card, a title scene, a proof scene), not of live footage:

| Share | Colour roles | Where |
| --- | --- | --- |
| About 60 percent | `bg` | Plate, empty space, breathing room |
| About 30 percent | `surface` and `ink` | Cards, pills, text |
| About 10 percent or less | `accent` | One underline, one bar, one highlight, one mark |

On talking head footage the accent is under 5 percent of the frame: the highlight word in a caption, one underline, one punch mark. A frame where the accent is a second background is a fail. Check by looking at a downscaled still: if your eye goes to two places before the face or the key word, the accent is overused. A simple measurement: count pixels near the accent colour in a still; more than 12 percent in a graphic scene is too much.

## Step 6: Type pairing

Two voices at most: one heavy sans for headings, numerals, UI text and captions, and one light italic serif used for one accent word per heading or caption phrase. Body text uses the same sans in Medium or Regular. A third family is a fail.

Options with common free fonts (verify each licence on its own page before use; open licences on large font sites usually allow video use, but check):

| Pair | Heading and body | Accent | Mood |
| --- | --- | --- | --- |
| A | Inter (Bold, Medium) | Instrument Serif Italic | Clean, modern |
| B | Montserrat (Bold, Medium) | Playfair Display Italic | Confident, editorial |
| C | DM Sans (Bold, Medium) | Fraunces Italic | Warm, friendly |
| D | Manrope (ExtraBold, Medium) | Lora Italic | Calm, professional |
| E | Space Grotesk (Bold, Medium) | Instrument Serif Italic | Technical |

Sizes on a canvas whose short side is 1080 px (scale every size by short side divided by 1080):

| Use | Size |
| --- | --- |
| Captions | 54 to 72 px, weight 700 or heavier |
| Headings, chapter titles | 64 to 110 px |
| Big numerals (stat cards) | 96 to 220 px |
| Lower third text | 44 to 56 px |
| Labels, source lines | 36 px minimum |

Pillow needs real font files. Prefer static files (`Inter-Bold.ttf`). Variable fonts may need extra steps and can fail silently; test the sheet. The sheet prints a glyph test line: any empty boxes mean the font lacks that character, so choose another font before building captions.

## Step 7: Background handling

| Type | Rules |
| --- | --- |
| solid | Use `bg`. Safest and cheapest. |
| gradient | Two tones from the palette only: `bg` and a version of `bg` 6 to 10 percent lighter or darker, at 150 to 160 degrees. No rainbow. Check banding on a still. |
| image | The user's own image, covering the canvas, with a veil in `bg` colour. |
| video | The user's own seamless loop. Start each scene at a different offset so scenes are not identical. Keep it slow and low contrast. |
| none | Graphics sit on footage; surfaces carry all contrast. |

Rules for every type: the top band is plain (see `ae-phone-safe-zones-and-formats`); the background never replaces or tints the speaker's own room (no cutout, no colour wash on the person) unless the user asks; no licensed media is bundled, the user brings or licenses their own; keep a copy, never edit the original.

Veil method for image and video backgrounds: take a still (`ffmpeg -ss 1 -i brand/backgrounds/loop.mp4 -frames:v 1 brand/bg_probe.png`; repeat at 3 different times), run `theme_sheet.py --probe`. It samples a 6 by 10 grid, finds the worst case contrast of `ink` over the background, and prints the smallest veil opacity (blend toward `bg`) that gets 4.5. Use that opacity or the next 0.05 step up. If it says more than 0.80, the background is too busy: pick another.

## Step 8: Shape, depth, preview, approval

Shape tokens: `radius` (cards, default 28 at 1080), pill radius is half the pill height, `rim_px` 2, shadow `soft` means a blurred layer of `ink` at about 18 percent opacity, blur about 24 px, offset down 10 px (at 1080). `none` means no shadow. Scale by short side over 1080.

Build the files and the sheet:

```
python3 brand/tools/theme_tokens.py brand/theme.json --out brand/tokens.json --caption-style surface --fix
python3 brand/tools/theme_sheet.py brand/tokens.json --out brand/theme-sheet.png
```

Open the PNG and look at it yourself first: text readable, accent not dominating, rim visible where required, glyph line complete. Then show it to the user with two or three alternatives if they hesitate (change one role at a time). The user approves in words ("use this"). Record the approval date and the contrast table summary in `## Visual theme` of the profile. Nothing downstream (captions, graphics) is built before that.

## Step 9: How the Agent Editor render and Remotion read the theme

Be accurate: the editor's screen has its own look and the theme does not change it. The render is where the theme appears.

The shipped `render.py` draws captions and the four graphic templates with Pillow and keeps its colours and fonts as constants near the top (an amber accent, a dark ink, an Arial Bold font path list, and fixed fill tuples inside the caption and graphic drawing functions). It reads no theme file. Check your copy by searching for `theme_loader` or `tokens.json`. If absent, wire it in with a small change:

1. Save `theme_loader.py` (in `references/theme-scripts.md`) next to `render.py`. Keep `brand/tokens.json` reachable (the loader looks in a `brand` folder next to the file, or at the path in the environment variable `AE_TOKENS`).
2. In `render.py` add `from theme_loader import load_tokens, rgba, derived_rgba, font_path` and `TOK = load_tokens()`.
3. Replace the constants and literals using this map. Keep the old value as the fallback when `TOK` is None.

| In render.py | Becomes |
| --- | --- |
| The amber accent constant | `rgba(TOK, "accent")` |
| The dark ink constant and text drawn in it | `rgba(TOK, "ink")` |
| Stat card, lower third and chapter title fill colours | `rgba(TOK, "surface", 240)` (the template's own alpha stays) |
| White text on lower third and chapter title | `rgba(TOK, "ink")` |
| Text on the highlight template and any text over an accent fill | `derived_rgba(TOK, "on_accent")` |
| Caption pill fill | `tuple(TOK["caption"]["pill_fill"])` |
| Caption text | `TOK["caption"]["text"]` |
| Font path lists | `font_path(TOK, "heading")` for graphics and captions, `font_path(TOK, "accent")` for an italic accent word |
| Rounded rectangle radii of cards | `round(TOK["radius"] * s)` where `s` is the scale already in the function |
| Rim | When `TOK["surface_separation"]["needs_rim"]`, draw the outline in `derived_rgba(TOK, "rim")`, width 2 times scale |

After the change run the render on a short window and look at stills before trusting it. A highlight word inside a caption needs per word drawing, which the shipped single pill drawing does not do; see `ae-caption-style-and-grouping` before promising highlights.

Remotion graphics (optional, for richer scenes): load `brand/tokens.json` once and pass it to compositions as `inputProps`, or import it as JSON if the project enables JSON imports. Every colour in a component comes from tokens, never a literal hex. Frames must be a pure function of time. Composite the result over the render with ffmpeg overlay (a ProRes 4444 or PNG sequence with alpha) and re check every seam. Remotion is free for individuals and small teams, but larger companies need a paid licence: check the current licence terms before the user uses it commercially.

## Step 10: Who reads which token

| Skill | Reads |
| --- | --- |
| `ae-caption-style-and-grouping` | `caption.*`, fonts, accent, on_accent, rim, safe zone lanes |
| `ae-lower-thirds-and-chapter-cards` | surface, ink, accent, on_accent, radius, rim, shadow |
| `ae-proof-cards-and-real-screens` | surface, muted (source line), accent (underline), radius |
| `ae-counters-and-numbers` | heading font, accent, ink |
| `ae-edit-qa-gates` | contrast table, surface separation, one accent rule |
| `ae-publish-packaging` | palette and accent for the thumbnail brief |

## Failure modes

1. A pale accent on a light theme fails contrast: darken it, or use it only as fill with `on_accent` text.
2. White card on cream looks flat: rim and soft shadow, or a surface tint.
3. Dark theme surfaces too close to bg (ratio under 1.25): lighten the surface a step, or rim.
4. Two accents creep in (a link blue, a chart green): one accent, other colours only inside third party tiles.
5. The font lacks a needed glyph: empty boxes in the glyph test; switch fonts.
6. Busy background: the veil number comes back above 0.80; choose a calmer background.
7. Theme changed mid project without a backup: copy to `brand/theme.v<N>.json` first, rebuild tokens, re render only what depends on it.
8. Text over footage with no pill: contrast changes every frame; captions keep a pill or an inverse pill.
9. Brand colours changed silently to pass a check: never; show the numbers and ask.

## Checklist

- [ ] Profile read; missing sections sent to `ae-setup-interview`.
- [ ] All seven roles exist, one accent only.
- [ ] `theme_tokens.py` exits 0; every FAIL fixed or accepted by the user in words.
- [ ] Surface separation is 1.25 or more, or the rim and shadow are on.
- [ ] Two type voices at most; glyph test line complete.
- [ ] Background type chosen; veil opacity measured for image or video; top band plain.
- [ ] `brand/theme-sheet.png` looked at and approved by the user.
- [ ] `brand/tokens.json` rebuilt after the last change; render reads it (or the user was told it does not yet).
- [ ] Backup of the previous theme kept; `## Visual theme` in the profile updated.

More material: `references/example-themes.md` (seven placeholder themes of different moods with measured numbers) and `references/theme-scripts.md` (the three tools).

Hand off to: `ae-caption-style-and-grouping` (caption look), `ae-lower-thirds-and-chapter-cards` (templates), `ae-proof-cards-and-real-screens`, `ae-counters-and-numbers`, `ae-phone-safe-zones-and-formats` (top band and lanes), `ae-edit-qa-gates` (contrast and look gates), `ae-owner-notes-to-rules` (every later look note becomes a rule).
