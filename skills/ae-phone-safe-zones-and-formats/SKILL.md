---
name: ae-phone-safe-zones-and-formats
description: Sets the video formats (vertical 9:16, 4:5, square, landscape 16:9), the approximate platform interface safe zones, and the layouts for each, with tools to measure the user's own phone, draw zone overlays on stills, scan the top band, and reframe footage. Use when the user says "make it vertical", "is this safe for Reels or Shorts", "text is hidden behind the app buttons", "square or landscape version", "what resolution should I export", or when captions or graphics need positions.
---

# ae-phone-safe-zones-and-formats

Read `brand/profile.md`. If it is missing or a section it needs (`## Platforms and formats`, `## Captions`, `## Rules`) is empty, stop and run `ae-setup-interview` for that section (ask the user, with options), do not guess. Also read `brand/safe_zones.json` if the user has measured their phone.

Gates that apply: look at overlay stills before calling a layout safe (a command that exits cleanly proves nothing); the numbers on this page are approximate starting values measured on one phone model and the user must verify them on their own phone before relying on them; never export or publish without the user's explicit go (`ae-export-once-workflow`).

## Step 1: Ask the format questions (only what the profile does not answer)

1. Platforms: Instagram Reels, YouTube Shorts, TikTok, LinkedIn, YouTube long form, other. Pick all that apply.
2. Main format per platform: vertical 9:16 (default for short form), 4:5 (feed), square 1:1, landscape 16:9 (default for long form).
3. Layout for vertical: (a) full frame talking head with captions, (b) split: a graphic panel on top and the speaker below, (c) a mix with full screen graphics for some scenes.
4. One layout for all platforms (recommended) or one per platform. A single layout that is safe on every app is cheaper to make and to check.
5. The user's phone model(s) for the safe zone test: iPhone with a notch or Dynamic Island, an Android, both. The strictest zone wins.
6. Source footage: filmed vertical, filmed landscape and reframed, or screen recordings.

Write the answers into `## Platforms and formats` as plain lines. If the user will make several formats from one shoot, record which is the master.

## Step 2: Formats and sizes

| Format | Pixels | Typical use | Notes |
| --- | --- | --- | --- |
| Vertical 9:16 | 1080 by 1920 | Reels, Shorts, TikTok | Default for short form. 30 fps is fine; 60 fps only if the source is 60 and the user wants it |
| Feed 4:5 | 1080 by 1350 | Feed posts | Keep text inside the middle 80 percent; the grid may show a centre crop |
| Square 1:1 | 1080 by 1080 | Feed, LinkedIn | Same rule |
| Landscape 16:9 | 1920 by 1080 (3840 by 2160 for 4K masters) | YouTube long form, LinkedIn, web | Title safe margins below |

Rule: each format is its own composition. A 9:16 version is not a crop of a composed 16:9 frame, because the graphics, captions and the speaker's position were designed for a different shape. Either film for the master format, or rebuild the layout for the second format (reposition graphics, move captions, rebuild the first frame). Reuse the script, the cut and the sound; do not reuse the layout.

The shipped Agent Editor ingest and render do not reframe: they keep the shape of the source. So reframe before ingest, on a copy, and ingest the copy. Never edit the original.

## Step 3: Approximate safe zones for 1080 by 1920 (verify on your own phone)

These are starting values from one phone model, in pixels on the 1080 by 1920 canvas. Apps differ, update, and change their interface; treat them as a prudent default and measure your own (Step 4). The tools read them from `brand/safe_zones.json`.

| Zone | Where | Rule |
| --- | --- | --- |
| Top band | y 0 to 270 (status bar and camera cutout about y 30 to 120, app header icons about y 185 to 255) | Plain background only: no text, logo, face, card edge, window header. First line of text starts at y 290 or lower |
| Text window | y 290 to 1500, x 60 to 1020 | All text, captions, numbers and logos stay inside |
| Bottom | y 1500 and below (video platform interface starts roughly y 1540 to 1625: account line, caption, progress bar) | No text, eyes, mouth, chin, captions or logos. Body, shirt and plain background may continue to the bottom edge. Chin hard limit about y 1530 |
| Right rail | x 900 to 1080, y 980 to 1790 | No text (like, comment, share and save buttons). Above y 980 text may run to x 1020 |
| Sides | x 0 to 32 and x 1048 to 1080 | Cropped on some phones; cards stay inside x 80 to 1000 |

One layout for every app: pick the strictest of the zones so the same file works everywhere. Do not make a different version per app unless the user asks.

Landscape 16:9 (1920 by 1080), as approximate rules: keep important action inside the middle 90 percent; keep titles and captions inside the middle 80 percent horizontally and above the bottom 8 percent (player controls and subtitles); keep the bottom right corner free (the platform's watermark and next video tiles); if the user plans end screens, keep the last 5 to 20 s free of important content on the right and bottom.

Square and 4:5: middle 80 percent for text; the bottom 12 percent can be covered by a caption or buttons in a feed.

## Step 4: Measure the user's own phone (do this once; it makes every later check real)

1. Run `safe_zone_chart.py` (code in `references/zone-tools.md`) and turn the PNG into a 3 s mp4 with the command printed there.
2. Upload it as a private, unlisted or "only me" test in each app the user uses. Never public. Delete it afterwards.
3. Open it on the user's phone inside the app (the interface only appears there, not in the gallery). Take a screenshot with the interface visible. If the user cannot, ask them to describe what covers the grid: "the right buttons start at x about 900, the caption starts at y about 1625".
4. Read the numbered lines: where the top icons end, where the bottom interface begins, where the right rail starts, how many pixels are cropped from the sides. Phones show the video scaled; convert screen positions to the 1080 by 1920 canvas by the grid lines, not by guessing.
5. Write the measured values into `brand/safe_zones.json` and note the phone models in `## Platforms and formats`.

Without a measurement, say plainly in the report: "safe zones are approximate starting values, not verified on the user's phone".

## Step 5: Layouts for vertical video (starting positions, verify with stills)

Layout A, full frame talking head:

| Element | Position |
| --- | --- |
| Head top | y 300 or lower (never in the top band) |
| Eyes | roughly one third down the frame, about y 600 to 850 |
| Chin | at or above y 1400 if possible; never below y 1530 |
| Caption lane | pill bottom at y 1500 or higher up; centre about y 1330 to 1400, below the chin and clear of the mouth |
| Lower third | top at about 0.60 to 0.64 of the height, above the caption lane |
| Graphic or stat card | top at 0.17 to 0.20 of the height (y 330 to 380) |

Layout B, split (graphic panel plus speaker):

| Element | Position |
| --- | --- |
| Graphic panel window | y 290 to about 800 (about 500 px tall); all panel content lives inside it |
| Caption lane | on the seam, centre about y 850 (check it against the speaker's cap or hair: it may touch the top of the head, never the eyes or mouth) |
| Speaker | head top about y 900, chin at or above y 1500, body and shirt continue to the bottom edge |
| Speaker scale | about 1.0 to 1.06 of a full frame; larger heads crowd the zones |

Layout C, full graphic scenes: content window y 290 to 1500, first text line centred at y 340 or lower, nothing in the right rail, same caption lane as the neighbouring face scenes or a lane inside the window.

Hook frames, titles and endings follow the same zones. The first frame of a short is a thumbnail in the feed: put a real, readable subject in the text window, not in the top band.

## Step 6: Shipped render defaults and what to change

The shipped render was written for a landscape frame. For vertical video check these in your copy of `render.py` and the checker output:

| Default | Problem on 1080 by 1920 | Change |
| --- | --- | --- |
| Caption pill top at 0.78 of the height (y 1498) | Pill mostly below y 1500 | Top at about 0.70 (y 1344), computed as 1500 minus the pill height minus 20 |
| Size scale from the height | Text and graphics about 1.78 times too large | Scale from `min(width, height)` |
| `stat_card` top at 0.10 (y 192) | Inside the plain top band | Top at 0.17 to 0.20 |
| `chapter_title` up to 24 characters | Wider than the screen above about 14 characters | Limit the text to 14 characters in vertical |

Then run the plan checks: `graphic_plan_check.py` (`ae-lower-thirds-and-chapter-cards`) and `check_caption_groups.py` (`ae-caption-style-and-grouping`).

## Step 7: Reframing footage (before ingest, on a copy)

Choose by what the user has:

| Source | Method | Command |
| --- | --- | --- |
| Film again in 9:16 | Best: no loss, all zones planned | Film with the head inside y 300 to 1400 |
| 4K landscape, speaker centred | Crop a 9:16 window and scale down: sharp because 2160 px of height become 1920 | `ffmpeg -i in.mp4 -vf "crop='ih*9/16':ih:'(iw-ih*9/16)*0.5':0,scale=1080:1920:flags=lanczos,setsar=1" -c:v libx264 -crf 16 -pix_fmt yuv420p -c:a copy out.mp4` |
| 1080p landscape | The same crop leaves a 608 px wide window that must be enlarged 1.78 times: soft | Prefer the blurred fill below, or accept softness knowingly |
| Landscape footage kept whole | Blurred copy behind a scaled centre | `ffmpeg -i in.mp4 -filter_complex "[0:v]split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=40:6[bg];[b]scale=1080:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1[o]" -map "[o]" -map 0:a -c:v libx264 -crf 16 -pix_fmt yuv420p out.mp4` |
| Speaker off centre | Change the crop x offset (the `0.5` factor is the horizontal position, 0 is left, 1 is right) | |
| Square or 4:5 | `crop=ih:ih:(iw-ih)/2:0,scale=1080:1080` or `crop='ih*4/5':ih:(iw-ih*4/5)/2:0,scale=1080:1350` | |

Run one heavy ffmpeg job at a time, with `nice -n 15` and `-threads 4` (`ae-laptop-load-safety`). If the speaker moves around, a fixed crop will cut them off: check stills at the start, middle and end of the clip before ingesting.

## Step 8: Delivery file settings (approximate, check the platform's current help page)

Typical safe settings for a short: H.264 (High profile), `yuv420p`, 1080 by 1920, 30 fps (or the source frame rate), 8 to 16 Mb/s video, AAC stereo 48 kHz at 128 to 192 kb/s, `-movflags +faststart`, colour tags `bt709` and limited (tv) range, loudness per `ae-loudness-mastering`. Length and file size limits change often: check the platform page for the current limit before the user relies on a length.

Verify an exported file (read only):

```
ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,width,height,pix_fmt,r_frame_rate,color_range,color_space -of compact out/edit.mp4
ffprobe -v error -select_streams a:0 -show_entries stream=codec_name,sample_rate,channels -of compact out/edit.mp4
```

The shipped render already writes H.264, yuv420p, AAC 192 kb/s, faststart and loudness normalisation; check colour tags and add them if the platform shows washed out colours.

## Step 9: Verify with pictures and a scan

1. Extract stills at: the first frame, each graphic's hold, a long caption, a highlight caption, each layout change, the last frame (`ffmpeg -ss T -i out.mp4 -frames:v 1 stillT.png`).
2. Draw the zones: `overlay_zones.py still.png --out still-zones.png --zones brand/safe_zones.json`. Look at each one yourself: nothing important may sit in a coloured zone.
3. Run `scan_top_band.py out.mp4`: it flags busy detail in the top band and right rail. Calibrate once on a plain video (OK) and a busy test video (flags). Look at every flagged time.
4. Repeat on every format and every platform version. Do it before asking for the go and again on the final export.
5. Record each result as seen (stills looked at) or measured (tool output) in the QA report (`ae-edit-qa-gates`).

## Worked example (placeholder: a bakery explainer, vertical, split layout)

Brief: 40 s short, split layout, Reels and Shorts, one layout for both. Phone measured: top icons end at y 255, bottom interface begins at y 1540, right rail starts at x 900.

| Item | Placed at | Check |
| --- | --- | --- |
| Hook headline (chapter style card) | top y 330, 14 characters | Below the band (290), inside x 60 to 1020 |
| Graphic panel | y 290 to 800 | Window respected |
| Stat card "48 hours" | top y 326 (0.17), right side | Shipped 0.10 would have been y 192: moved |
| Caption lane | seam, centre y 850 | 60 px clear below the panel bottom at 800 |
| Speaker | cap top y 905, chin y 1495 | Chin below 1530 would have failed |
| Lower third "Bubbles" | y 1190 (0.62) | Bottom y 1290, above y 1500, left side, outside the rail |
| Last frame | settled card, text inside the window | No element at the bottom |

Results: overlay stills of 7 frames show nothing in a coloured zone; the scan flagged one frame at 0.5 s in the top band (a gradient in the plate, looked at, plain enough); the user's phone test showed the interface 25 px lower than the defaults, so the defaults stayed as the prudent choice.

## Failure modes

1. Zones taken as facts: say "approximate, verify".
2. A 16:9 composition cropped to 9:16: the graphics sit in the wrong place and the speaker is cut off.
3. Text in the top band: covered by the status bar or app header.
4. Caption pill below y 1500: sits behind the platform caption and buttons.
5. Right rail ignored: a stat card behind the like and share buttons.
6. A soft 1080p crop enlarged 1.78 times: tell the user or film in 4K.
7. Different layouts per app when one would do: double the checking, double the mistakes.
8. Colour tags missing: washed out colours after upload; check with ffprobe.
9. Chart uploaded publicly: always private or unlisted, and delete it afterwards.
10. A new phone or app update moved the interface: remeasure when the user reports covered content.

## Checklist

- [ ] Profile read; platforms, formats, layout and phone model recorded.
- [ ] Each format is its own composition; the source reframed before ingest, on a copy.
- [ ] Zones are the user's measurement, or the report says they are approximate.
- [ ] Top band plain; text inside y 290 to 1500 and x 60 to 1020; no text in the right rail.
- [ ] Shipped render defaults checked (lane, scale, stat card position, chapter length).
- [ ] Overlay stills of every layout looked at; `scan_top_band.py` calibrated and run.
- [ ] Export settings verified with ffprobe; colour tags present.
- [ ] Results recorded in the QA report as seen or measured.

More: `references/zone-tools.md` (zones file, calibration chart, overlay and scan tools).

Hand off to: `ae-caption-style-and-grouping` (lanes), `ae-lower-thirds-and-chapter-cards` (positions and sizes), `ae-theme-builder` (plain top band background), `ae-run-multi-agent-edit` (format in the agent briefs), `ae-export-once-workflow` (delivery gate), `ae-loudness-mastering` (audio targets), `ae-edit-qa-gates` (evidence), `ae-publish-packaging` (per platform copy).
