---
name: ae-agent-graphics
description: Role skill for a graphics agent in the Agent Editor. Chooses and places the four graphic templates (stat_card, lower_third, chapter_title, highlight) using only words that are spoken, with the spacing, length, count and size limits the server and the render impose. Use when an agent is started with the role graphics, or when the user says "add motion graphics", "add a stat card", "name the tool on screen", "add chapter titles", "highlight the key phrase".
---

# Agent Editor: graphics agent

Read `brand/profile.md`. If it is missing or a section this skill needs is empty, stop and run `ae-setup-interview` for that section (ask the user, with options), do not guess.

Sections used here: `## Visual theme` (how loud or quiet graphics should be), `## Platforms and formats` (frame shape: text width and safe zones depend on it), `## Rules` (banned templates, banned words), `## Claims policy` (a number on screen is a claim).

The editor server runs at `http://127.0.0.1:8780` (or the port the conductor gave you). You act only with `curl -s -X POST http://127.0.0.1:8780/api/op`. Your role is `graphics`. A person watches your cursor move, so work one clear step at a time.

## Questions to ask the user if the profile does not answer them

1. How many graphics do you want?
   a) A few: 2 to 4, only the most important moments.
   b) Standard: 5 to 8 across the whole video (the shipped brief).
   c) Busy: 8 to 10 (the server limit is 10 for the whole video).
   d) One per chapter only.
2. Which templates are allowed? (tick any)
   a) Stat card (a number or short figure). b) Lower third (names a tool or thing). c) Chapter title (a new part starts). d) Highlight (a key phrase).
3. How should numbers appear?
   a) Exactly as spoken (the transcript's own form, "7" or "seven"). b) Always digits when the transcript has digits. c) Never show numbers without a source line (then no stat cards until the user supplies sources).
4. What frame will the video be delivered in?
   a) Vertical 9:16. b) Square 1:1. c) Landscape 16:9. d) Several (tell me which is the main one).

Defaults if the user does not answer: Standard, all four templates, numbers as spoken, and the frame from the profile.

## What you may send

| op | Use |
| --- | --- |
| `hello` | `{"op":"hello","agent":"W07","role":"graphics"}` first |
| `claim` | Before placing: `{"op":"claim","agent":"W07","kind":"template","id":"stat_card","status":"picking a stat card"}`. `kind` can also be `window` with `start` and `end`. A claim only moves your cursor and highlights the template tile. It does not lock anything |
| `graphic` | The only edit you make |
| `done` | Last call, one line summary |

Do not send `cut`, `caption`, `fx` or `music`. Never `reject` or `remove`.

## Exact rules the server enforces for `graphic`

Fields: `template`, `text`, `at` (source seconds), optional `dur`.

| Check | Limit | The server's answer |
| --- | --- | --- |
| `template` | one of `stat_card`, `lower_third`, `chapter_title`, `highlight` | `template must be one of ['stat_card', 'lower_third', 'chapter_title', 'highlight']` |
| `at` | number, 0 to the source duration | `'at' must be a number` or `'at' must be between 0 and <duration>` |
| `dur` | 1.5 to 4.0 s, default 2.5 | `'dur' must be between 1.5 and 4.0` |
| `text` | 1 to 24 characters after trimming | `text is 1 to 24 characters` |
| Spoken words | each space separated token of `text`, with punctuation and case removed, must appear among the transcript words that overlap the span from 2 s before `at` to 2 s after `at + dur` | `words not spoken near 12.4: ['204']; graphic text comes only from the transcript` |
| Count | at most 10 live graphics in the whole video (all agents together) | `at most 10 graphics in one video` |
| Spacing | at least 0.5 s between the end of one graphic and the start of the next | `too close to g12 ('204' at 12.4); keep 0.5 s between graphics` |

Details of the spoken check, because they cause most refusals:

- The comparison removes everything that is not a letter or digit. "Claude Code" matches "Claude" and "code". "follow-up" becomes "followup", so the text "follow up" (two tokens) fails when the transcript has "follow-up". Use the transcript's own form.
- A token with no letters or digits ("$", "%") always passes. "$204" and "204" are the same token.
- If the transcript wrote the number as words ("two hundred and four"), the text "204" is refused. Use the words the transcript has, or ask the conductor to have the spelling fixed in the transcript first (`ae-ingest-and-transcribe`).
- The check does not verify order, and it does not verify that the number is true. Those are your job (claims section below).
- The count and spacing checks are first come, first served. If two graphics agents run, the conductor must give each a budget (for example 5 and 5).

## What the render does (this decides where you place things)

| Fact | Consequence |
| --- | --- |
| `at` and `dur` are source seconds for the start; the card then shows for `dur` seconds of finished video | If a seam between kept cuts falls inside `[at, at + dur]`, the card sits over words from a different part of the source. Keep the whole span inside one kept cut |
| A graphic whose `at` is in removed material is skipped silently | Check `at` against the kept cuts (`references/size-and-timing.md`) |
| Fade in 0.22 s, fade out 0.22 s, a small slide up over 0.28 s | The card is fully readable about 0.3 s after `at` and starts fading 0.22 s before its end. Readable time is about `dur - 0.5` |
| Fixed positions as fractions of the frame: stat card top right (10 percent down), lower third left (62 percent down), chapter title centred (38 percent down), highlight left (16 percent down). Margins 6 percent | You cannot move a card with the API. Choose the template whose place is free |
| Captions are drawn centred at 78 percent down | Lower third and captions are separated; do not expect a stat card to collide with captions |
| Text is drawn with a bold system font; colours and the accent are constants in the render file | Check with the conductor whether the theme was applied there (`ae-theme-builder`). Otherwise the defaults are an amber accent on a dark navy ink. If no suitable font is found, Pillow may fall back to a tiny default font, so check the first render |
| Card size scales with the shorter side of the frame (the render uses `min(width, height)`) | A card has the same pixel size in a 1080 by 1920 vertical frame as in a 1920 by 1080 landscape frame, so in a narrow frame it covers a bigger share of the width (next section) |

## Templates: when to use each

| Template | Use for | Text | Where | Reading time |
| --- | --- | --- | --- | --- |
| `stat_card` | A number or short figure someone says ("204", "7 stages", "40%") | the figure plus at most one short word | top right | 2.0 to 3.0 s |
| `lower_third` | Naming a tool or thing at the moment it is first said ("Claude Code") | the name, 1 to 3 words | left, lower | 2.0 to 2.5 s |
| `chapter_title` | A new part starts ("The CRM test") | 1 to 4 words, the part's name as spoken | centre | 2.0 to 2.5 s |
| `highlight` | A key phrase worth keeping on screen ("no repeats") | 2 to 4 words | left, upper | 1.5 to 2.0 s |

Use `highlight` rarely (at most one per 30 s): captions already show the same words, so a highlight mostly repeats them. Stat cards, lower thirds and chapter titles add information and are better value.

## Will the text fit? (check before you send)

Cards scale with the shorter side `S = min(W, H)` of the frame. A 1080 wide vertical or square frame therefore gets the same card pixels as a 1920 by 1080 landscape frame, which leaves less room across a narrow frame. The render uses the original file's size when it still exists, otherwise the 720 line proxy; the ratio is what matters. Approximate maximum characters that fit inside 88 percent of the frame width (mixed case text, default font; capitals and letters like m and w are 15 to 25 percent wider, so subtract 2):

| Frame | stat_card | lower_third | chapter_title | highlight |
| --- | --- | --- | --- | --- |
| Landscape 16:9 | 24 | 24 | 24 | 24 |
| Square 1:1 | 15 | 24 | 15 | 24 |
| Vertical 9:16 | 15 | 24 | 15 | 24 |

In a narrow frame the limits matter for `stat_card` and `chapter_title`. Example at 1080 wide: the chapter title "The CRM test" (12 characters) is about 750 px wide and fits; a 24 character title would not. The server accepts up to 24 characters, so a card that runs off the frame is not refused: you must prevent it.

Measure instead of guessing when you can run Python in the editor folder: `references/size-and-timing.md` has a snippet that calls the render's own drawing function and prints the card size. Rule: width must be 88 percent of the frame width or less. If a text is too wide, shorten it to the key words (still spoken words), or choose another template, or tell the conductor. Do not abbreviate with invented words.

Phone safe zones (approximate, tell the user to verify on their own phone): in a vertical frame the stat card sits about 190 px from the top of a 1920 line frame, which is inside the area that phone apps cover with their own interface; the highlight sits near 300 px. Prefer `lower_third`, `chapter_title` and `highlight` for vertical delivery, or ask the user whether stat cards at the top are acceptable. See `ae-phone-safe-zones-and-formats`. Changing positions means editing the render file, which is the user's decision, not yours.

## Procedure

1. `hello`, then `claim` the window you were given (or the whole video).
2. Read the transcript: `curl -s 'http://127.0.0.1:8780/api/window?start=0&end=<duration>'` (or `/api/ingest` for everything). Read `/api/state` for the kept cuts and for graphics other agents placed.
3. Wait until the cutters are done (their `done` flag in `/api/state`), then work from the final cuts. If the conductor told you to start earlier, re-check every graphic against the cuts at the end.
4. Make a candidate list (below), choose the final set within your budget, then place them one at a time.
5. After each `graphic`, read the answer. On NO, fix the cause (table at the end).
6. When all are placed, re-run the check in `references/size-and-timing.md` for starts in removed material and for spans crossing a seam.
7. `done` with a summary under 20 words.

## Choosing the moments

Candidates come from the transcript words only. Number of graphics: the user's answer to question 1. As a scale: about one graphic per 8 to 15 seconds of finished video, never more than 10 in total.

| Moment in the transcript | Template |
| --- | --- |
| A number, count, price, duration, percentage that the sentence depends on | `stat_card` |
| The start of a new part: a sentence that introduces a topic, usually after a longer pause or after "now", "next", "first" | `chapter_title` |
| The first time a named tool, product, person or place is said | `lower_third` |
| The one phrase you would underline in the script | `highlight` |

Spread them: no two within 1.5 s of each other (the server minimum is 0.5 s, this keeps the screen calm), none in the first 1.0 s of the video, none over the last 1.0 s. If a punch zoom from the fx agent starts within 1 s of the moment, shift your card after the zoom or pick another moment (`/api/window` shows fx within 3 s).

## Timing a card

1. Find the first matching word `w` in the transcript (searching forward only, never from the top for each card).
2. `at` = `w.t - 0.15` so the slide in finishes as the word lands, but never before the previous word has ended. For a chapter title use the start of its sentence minus 0.1 s.
3. `dur` = 1.5 + 0.25 per word beyond 3, plus the time the spoken phrase takes if it is longer than that. Typical: 2.0 (short), 2.5 (default), 3.0 (a figure with a spoken explanation), 4.0 maximum.
4. Check `at + dur` is inside the same kept cut as `at`. If not, shorten `dur` (down to 1.5) or shift earlier. If still impossible, skip this graphic.
5. Leave at least 1.5 s before the next graphic.

## Truth rules (claims)

1. The text must be the speaker's own words for the thing shown. Never round, translate, convert units, add a currency sign the speaker did not say, or "improve" a number.
2. A number is a claim. Apply the user's `## Claims policy`: if it requires a source for numbers and none exists, do not place the stat card, and list the number in `done` for the user. The conductor decides.
3. Verify against the text: the figure in `text` equals the figure in the transcript words at that time. If the transcript is probably wrong (a figure that contradicts the script), say so in `done` instead of placing it. You cannot hear the audio.
4. Do not place a graphic that names a brand or person in a way the speaker did not.
5. Mock ups are labelled. This editor draws plain text cards only. For real screens or real documents, use the proof card route in `ae-proof-cards-and-real-screens`, which is outside this role.

## NO answers and fixes

| The server says | Do this |
| --- | --- |
| `words not spoken near 12.4: [...]` | Use the words as the transcript has them; check you used source seconds; check the time is within 2 s of the words |
| `too close to g12 (...)` | Move after it (`at >= its at + dur + 0.5`), or drop the weaker graphic |
| `at most 10 graphics in one video` | Stop. Report the budget in `done` |
| `text is 1 to 24 characters` | Shorten to the key spoken words |
| `'dur' must be between 1.5 and 4.0` | Fix `dur` |
| `template must be one of [...]` | Use the exact lowercase names |

## Worked example (neutral placeholder content)

A local bakery explains reviving a sourdough starter, delivered vertical 9:16, standard density, cutters done. Kept cuts: c1 0.34 to 2.54, c2 2.99 to 4.26, c3 4.94 to 7.60, c4 8.00 to 9.40. Transcript words: "Feed" 5.00 to 5.20, "twice" 5.32 to 5.60, "seven" 6.18 to 6.50, "days" 6.50 to 6.85, "Sourdough" 0.62 to 1.20.

1. Moment: "seven days" (a number). Template `stat_card`. The transcript has the word "seven", not the digit, so the text "7 days" would be refused (`words not spoken near 6.03: ['7']`). Either ask the conductor to correct the transcript spelling to "7" (see `ae-ingest-and-transcribe`) or use the spoken form. "seven days" is 10 characters and the vertical stat card limit is 7, so it would overflow. Decision: the conductor approves the spelling "7", so the text is "7 days" (6 characters, fits).
2. Timing: first matching word "seven" at 6.18. `at` = 6.18 - 0.15 = 6.03, after the previous word ended. `dur` 2.0 gives an end at 8.03. The cut c3 ends at 7.60, so the card would cross the seam into c4. Use `dur` 1.5, ending at 7.53, inside c3. Readable time is about 1.0 s, enough for a three character figure.
3. Moment: the first mention of the product name ("Sourdough" at 0.62). Template `lower_third`, text "Sourdough starter" is 17 characters, over the vertical limit of 14, so use "Sourdough" (9 characters). The right `at` would be 0.47, inside the first second, which stays clean. Moving it to 1.00 would land in the middle of the word and lose the sync. Skip it and report it.

Calls for step 2:

```
curl -s -X POST http://127.0.0.1:8780/api/op -H 'Content-Type: application/json' -d '{"op":"hello","agent":"W07","role":"graphics"}'
curl -s -X POST http://127.0.0.1:8780/api/op -H 'Content-Type: application/json' -d '{"op":"claim","agent":"W07","kind":"template","id":"stat_card","status":"picking a stat card"}'
curl -s -X POST http://127.0.0.1:8780/api/op -H 'Content-Type: application/json' -d '{"op":"graphic","agent":"W07","template":"stat_card","text":"7 days","at":6.03,"dur":1.5}'
```

The answer is `{"ok":true,"id":"g14","item":{...}}`. Final message: "Placed 1 graphic (g14, stat card '7 days' at 6.03). Skipped the lower third for Sourdough: it falls in the first second. Server refused nothing; one text needed a transcript spelling fix first."

## Checklist

- [ ] Profile read; the four questions answered or defaulted.
- [ ] Every text token is in the transcript, in the transcript's own form.
- [ ] Every card fits the frame width (measured, or within the table limits).
- [ ] Every `at` is inside a kept cut and `at + dur` inside the same cut.
- [ ] 1.5 s or more between graphics; none in the first or last second.
- [ ] Count within budget (10 maximum for the whole video, shared).
- [ ] Every number matches the transcript and the claims policy.
- [ ] No graphic within 1 s of a punch zoom.
- [ ] `done` lists skipped moments with reasons.

## Do not

- Do not invent words, numbers or names. Do not abbreviate to something unspoken.
- Do not use all four templates for the sake of variety.
- Do not place a graphic over a seam, over the first or last second, or on top of another.
- Do not edit the render file or the templates. Report problems to the conductor.
- Do not render or export.

Hand off to: `ae-agent-reviewer` (checks your cards against the transcript and the cuts), `ae-lower-thirds-and-chapter-cards` (design of the templates), `ae-counters-and-numbers` (landing numbers on the spoken word), `ae-word-synced-graphics` (timing to word times), `ae-theme-builder` (colours and fonts), `ae-phone-safe-zones-and-formats` (safe areas), `ae-proof-cards-and-real-screens` (real screens), `ae-run-multi-agent-edit` (the conductor).
