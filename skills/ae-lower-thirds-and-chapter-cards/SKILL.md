---
name: ae-lower-thirds-and-chapter-cards
description: Designs, words, places and times the reusable graphic templates of an edit (name tags and lower thirds, chapter title cards, stat cards, key phrase highlights), including how to add a new template, sizes per format, reading holds and spacing. Use when the user says "add name tags", "add chapter titles", "make a stat card", "highlight this phrase", "design my lower third", "graphics look cramped or off screen", or when a graphics agent needs a template plan for a script.
---

# ae-lower-thirds-and-chapter-cards

Read `brand/profile.md`. If it is missing or a section it needs (`## Visual theme`, `## Platforms and formats`, `## Rules`) is empty, stop and run `ae-setup-interview` for that section (ask the user, with options), do not guess. Also read `brand/tokens.json` if it exists; if it does not, run `ae-theme-builder` first, because every colour, font and radius in a template comes from the theme and never from a literal.

Gates that apply here: the script is approved before any graphic is planned (`ae-script-first-workflow`). Graphic text is spoken text only, never invented. A graphic never states a fact, number or name the user did not provide or say. Look at stills before calling a template done.

## What the Agent Editor gives you

Four built in templates, placed with the `graphic` operation. The server answers ok or NO with a reason.

| Template | Purpose | Text | Default position in the shipped render |
| --- | --- | --- | --- |
| `stat_card` | A number or short figure the speaker says | 1 to 24 characters ("204", "7 stages") | Right side, 10 percent down |
| `lower_third` | Name a tool, thing or person when first said | 1 to 24 characters ("Claude Code") | Left side, 62 percent down |
| `chapter_title` | Start of a new part | 1 to 24 characters ("The CRM test") | Centre, 38 percent down |
| `highlight` | A key phrase worth stressing | 1 to 24 characters ("no repeats") | Left side, 16 percent down |

Server rules for every graphic: `at` is a source time in seconds (not output time); `dur` is 1.5 to 4 s (default 2.5); every word of the text must be spoken within 2 s of the graphic; at least 0.5 s between two graphics; at most 10 graphics in one video. The render slides a graphic up about 3.5 percent of the frame height over 0.28 s while it fades in over 0.22 s, and fades out over the last 0.22 s.

Check your copy of `render.py` before you plan: positions and sizes are in its `POS` table and in `graphic_png`. If the numbers differ from this page, trust the file.

## Scale by short side (important for vertical video)

The shipped drawing code scales sizes from the frame height (`H / 1080`). On a landscape 1920 by 1080 frame that is exactly right. On a vertical 1080 by 1920 frame it makes every graphic about 1.78 times too big: a 24 character lower third can be wider than the screen. The fix is one line at each call: pass `min(width, height)` where the render passes the height to `graphic_png` and `caption_png`. Do this once, then verify with the checker in `references/plan-check.md`.

Widths at the corrected scale (frame 1080 wide, Arial Bold style font, about 0.6 em per character):

| Template | Font px | Padding | Longest text that fits inside a 960 px window |
| --- | --- | --- | --- |
| `stat_card` | 112 | 90 | about 12 characters |
| `lower_third` | 52 | 120 | 24 characters |
| `chapter_title` | 96 | 140 | about 14 characters |
| `highlight` | 58 | 80 | 24 characters |

So in vertical video a chapter title is 14 characters at most, and a stat card is a number plus a short unit. Measure with the real font; the checker does it.

## Placement rules by format

Zones come from `ae-phone-safe-zones-and-formats` (approximate; the user verifies on their own phone). Starting values for 1080 by 1920:

| Template | Top (fraction of height) | Why |
| --- | --- | --- |
| `highlight` | 0.16 to 0.17 (about y 310 to 330) | Under the plain top band (text starts at y 290 or lower) |
| `stat_card` | 0.17 to 0.20 | The shipped 0.10 lands at y 192, inside the top band: move it |
| `chapter_title` | 0.30 to 0.38 | Mid upper frame, above the face in a split layout |
| `lower_third` | 0.60 to 0.64 | Above the caption lane, clear of the chin and the right rail |

Every graphic: bottom edge at y 1500 or higher up, nothing in the right rail (x 900 to 1080, y 980 to 1790), at least 60 px clear above the caption pill. Edit the `POS` fractions in `render.py` rather than overriding per graphic.

Landscape 1920 by 1080: keep graphics inside the middle 90 percent of the frame, titles inside 80 percent horizontally, nothing in the bottom right corner (watermark, next video tile) or the bottom 8 percent (player controls).

## Wording rules (the part that is easy to get wrong)

1. Use the speaker's words exactly. The server checks that every word was spoken; a paraphrase is refused.
2. Shortest honest form: "48 hours" beats "Forty eight hours of rest".
3. No trailing punctuation, no all capitals unless the user's style says so, no emoji.
4. A graphic never repeats a caption for the same words at the same time. If the words are on screen as a graphic, hide the caption (`ae-caption-style-and-grouping`, quiet windows).
5. Names of people: only a name the user supplied in the profile or in the brief. Never guess a name or a job title from the audio. If the name is unknown, no name tag: that is a blocker, ask.
6. Names of tools or products: spell them as the owner of the product spells them, checked against a real page, not memory.
7. A number in a stat card is the number spoken, in the same units. A rounded or converted number is a new claim and needs a ledger row (`ae-claims-and-truth-ledger`). Invented or example numbers are labelled "Example" in the card text only when the user asked for a mock up.

## Choosing which template, when

| Situation | Template | Notes |
| --- | --- | --- |
| A figure is said ("204 leads", "7 stages") | `stat_card` | At the figure word, hold 2.5 s |
| A tool, product or person is named for the first time | `lower_third` | First mention only, never repeats |
| A new part of the video begins (long form, or a short with two or three parts) | `chapter_title` | One per part, same pattern each time |
| A phrase carries the argument ("no repeats", "one idea per scene") | `highlight` | At most one per 10 s |
| The same word is said ten times | None | Nothing is better than repetition |

Quotas and spacing: a 30 to 45 s short gets 3 to 5 graphics; a 60 to 90 s short 5 to 7; long form one graphic every 10 to 20 s at most plus a chapter title per part (the server cap of 10 means long form needs the cap raised or graphics built in another tool, see `ae-motion-design-principles`). Keep at least 3 s between the end of one graphic and the start of the next so each is read; the server only enforces 0.5 s. Variety: never the same template twice in a row, and put the biggest or most unusual graphic on the moment that matters most (one hero per scene).

## Timing numbers

| Item | Value |
| --- | --- |
| `at` | The word's start time minus 0.12 s (never earlier than 0.3 s before the word; the text must not be readable before the word) |
| Reading hold | 1.5 s minimum; for more than three words add 0.25 s per extra word; never above 4 s |
| Entrance | 0.28 s ease out slide, 0.22 s fade (as the shipped render) |
| Exit | Fade over the last 0.22 s, a hard stop when a cut follows |
| Sound lead | A soft sound 0.05 to 0.2 s before the entrance, see `ae-sound-effects-placement` |
| Spacing | 3 s clear between graphics, 0.5 s is the server minimum |

Check: the text is fully formed and readable for the whole hold, nothing is still moving or fading in the middle of the hold, and the last frame of a graphic is a settled hold or a clean fade (never a half drawn element).

## Template design spec (use it for the four built ins and for new templates)

Write one spec per template into `brand/templates.md` so the look is reusable and the render and the checker stay in step. Fields:

1. Name, purpose, one sentence.
2. Text rule: character limit, case, what it may contain.
3. Size: font role (heading or body from the theme), px at the 1080 short side, padding, minimum text px (36).
4. Box: fill (`surface`, an `accent` pill, or none), text colour (`ink`, `on_accent`), radius from the theme, rim when `needs_rim`, shadow.
5. Marker: one accent element only (a left bar, a top bar, an underline). The accent colour is the only accent.
6. Position: side, vertical fraction, safe zone check.
7. Motion: entrance, hold, exit, in numbers.
8. Do not use when: the situations that make it wrong.

Example spec (placeholder, bakery explainer): `name_tag`: "Person on screen for the first time". Text: the person's name as the user supplied it, up to 24 characters. Size: body font 50 px, padding 120 by 56. Box: `surface` fill, `ink` text, left bar 16 px in `accent`, radius 14 at 1080. Position: left, 0.62 of height. Motion: 0.28 s slide, hold 3 s, 0.22 s fade. Do not use: when a lower third for a tool is already visible.

## Adding a new template (two edits, then tests)

The server and the render each know the template names, so a new one needs both:
1. In `server.py` add the name to the `TEMPLATES` tuple. The `graphic` operation then accepts it with the same checks (words spoken, spacing, 1 to 24 characters).
2. In `render.py` add the template to `POS` and add a branch in `graphic_png` that draws it with Pillow from the tokens (see `ae-theme-builder` step 9). Also add its name and a sample text to `SAMPLES` so the preview tile exists.
3. In `agent-editor/tests/test_ops.py` add a test that the new template is accepted and that bad text is refused (follow the existing graphic tests).
4. Render a 10 s window with the template and look at stills. A new template that has not been seen on stills is not finished.
5. Tell the graphics agents (`ae-agent-graphics`) the new name, its text rule and when to use it in the next brief.

If the user wants richer graphics than Pillow can draw (animated counters, icons, logos), build them as a Remotion overlay as in `ae-word-synced-graphics`, composite over the render, and re check seams (`ae-transitions-and-blur`).

## Chapter cards for long form

1. Chapters follow the story, not the clock: a new chapter when the viewer's question changes. Typical spacing in long form: one every 2 to 5 minutes, at least 10 s long each.
2. The card text is a plain label of the step or question, in the spoken words ("The test", "What went wrong"), never a conclusion that spoils the next minute.
3. Same template, same position, same duration for every chapter so they read as a set. Number them only if the speaker says the numbers.
4. The chapter times you place become the YouTube chapter list (`ae-publish-packaging`): record each card's output time while you place it (use the cut mapping, not the source time).
5. Keep the card out of the first 5 s and the last 10 s of the video.

## Worked example (placeholder: a local bakery explaining sourdough, 45 s vertical short)

Spoken text (excerpt): "Feed it twice a day. After 48 hours it doubles. I call mine Bubbles. Keep it warm, around 24 degrees."

| Graphic | Template | Text | at (source s) | dur | Reason |
| --- | --- | --- | --- | --- | --- |
| g1 | `highlight` | twice a day | 4.1 | 2.0 | The one rule of the first beat |
| g2 | `stat_card` | 48 hours | 9.2 | 2.0 | Figure spoken at 9.3 |
| g3 | `lower_third` | Bubbles | 14.2 | 2.0 | Names the starter, first mention |
| g4 | `stat_card` | 24 degrees | 22.4 | 2.5 | Figure spoken at 22.5 |

Checks done: text fits (all under 14 characters), `at` is 0.1 s before each word, gaps between graphics are 3.1, 3.0 and 6.2 s (the first plan held g2 for 2.5 s, which left only 2.1 s before g3, so g2 was shortened to 2.0 s, still above the 1.5 s minimum), none repeats a caption, g2 and g4 are both stat cards but a different template sits between them. Positions: stat card at 0.18, highlight at 0.17, lower third 0.62, all inside the safe zones. Result of the plan check script: one warning (the short gap), fixed, then OK.

## Failure modes

1. Stat card at the shipped 0.10 on a vertical frame: inside the top band, covered by the app's status bar.
2. Graphic scaled from the height on a vertical frame: too big, wider than the screen.
3. Chapter title text over 14 characters in vertical: clipped at the edges.
4. Graphic shown before the word is spoken: the viewer reads it first and the word lands flat.
5. Two graphics 0.5 s apart: legal for the server, unreadable for people.
6. A name tag with a guessed name: never; a blocker, not a fix.
7. Highlight repeating the caption: the same words twice on screen at once.
8. A long form video that needs more than 10 graphics: the server cap refuses the eleventh; raise the cap on purpose or move those graphics to another tool.
9. Theme colour literals pasted into the template: the next theme change misses them.

## Checklist

- [ ] Script approved; profile and tokens read.
- [ ] Each graphic's words are in the transcript and in the speaker's spelling.
- [ ] Number, name and tool facts come from the user or a checked page.
- [ ] Sizes scaled by short side; longest text measured with the real font.
- [ ] Positions inside the safe zones; 60 px above the caption lane; nothing in the right rail.
- [ ] Hold at least 1.5 s (plus 0.25 s per word over three); 3 s between graphics.
- [ ] Template variety; one hero moment; no repeats of the same word.
- [ ] `graphic_plan_check.py` prints OK; stills of entrance, hold and exit looked at.
- [ ] Chapter output times recorded for the publish package.

More: `references/plan-check.md` (the plan check script and how to run it).

Hand off to: `ae-agent-graphics` (places them), `ae-word-synced-graphics` (timing to words), `ae-counters-and-numbers` (animated numbers), `ae-phone-safe-zones-and-formats` (zones), `ae-theme-builder` (colours and fonts), `ae-sound-effects-placement` (sound lead), `ae-edit-qa-gates` (final checks), `ae-publish-packaging` (chapters).
