---
name: ae-caption-style-and-grouping
description: Defines how captions look and how they are cut into groups for an Agent Editor edit: 1 to 3 word groups, split points, never ending on a function word, highlight words, lanes, quiet windows when a graphic shows the same words, spelling checks, and building captions from the final transcript. Use when the user says "add captions", "my captions are late or too long", "captions cover the face", "highlight keywords", "caption style", or when a captioner agent needs a grouping plan and checker.
---

# ae-caption-style-and-grouping

Read `brand/profile.md`. If it is missing or a section it needs (`## Captions`, `## Visual theme`, `## Platforms and formats`, `## Rules`) is empty, stop and run `ae-setup-interview` for that section (ask the user, with options), do not guess. Also read `brand/tokens.json` (run `ae-theme-builder` if it is missing).

Gates that apply: the script is approved first; captions are built from the transcript of the audio that will be heard, never from the script text and never from another video; nothing is invented; look at stills before calling captions done. The captioner agent role is described in `ae-agent-captioner`; this skill holds the rules and the tools it uses.

## Step 1: Ask the style questions (only what `## Captions` does not answer)

Show the options. The user may answer freely.

1. Pill style: (a) light card with dark text (the theme `surface` pill, the default), (b) dark pill with light text (`inverse`), (c) bare text with an outline and soft shadow, (d) text on an accent coloured box.
2. Highlight: (a) one keyword per group in the accent colour, (b) italic accent font for the keyword, (c) bold only, (d) none.
3. Case: sentence case (default), lower case, upper case. Upper case costs width: 22 characters of capitals is wider than 22 of lower case.
4. Position: (a) lower middle on the face lane, (b) just under the face, (c) centre, (d) top under the plain top band. Default (a) for vertical talking head video.
5. Rhythm: (a) phrase groups of 2 to 3 words (default), (b) mostly one or two words for a fast feel, (c) one word at a time for emphasis only.
6. Numbers: numerals as spoken ("48") or words ("forty eight"). The caption words must match the transcript, so the transcript is fixed to match this choice (Step 3).

Write the answers under `## Captions` of the profile.

### The pill styles compared (show this to the user if they hesitate)

| Style | Looks like | Strength | Weakness | Check before choosing |
| --- | --- | --- | --- | --- |
| Surface pill (light card, dark text) | Soft card, rounded ends | Readable on any footage, matches cards and lower thirds | Large on screen, can feel heavy over a face | Text on pill 7 or more; pill under 960 px wide |
| Inverse pill (dark pill, light text) | Dark capsule | Strong on bright footage and on light themes | Can look severe on a warm theme | The dark colour is the theme `ink`, text is `bg` |
| Bare text with outline | Text only, 3 to 4 px outline and soft shadow | Lightest touch, face stays visible | Fails on busy or bright frames | Test on the brightest and busiest frame of the video |
| Accent box | Text on a solid accent block | Loud, brand coloured | Competes with highlights and graphics, accent overused | Accent share of the frame stays under about 12 percent |

Two combinations to avoid: a pill and an outline together (double treatment), and a highlight colour equal to the pill colour (the keyword disappears).

## Step 2: What the Agent Editor enforces and how it draws

The `caption` operation fields are `agent`, `start`, `end`, `text`. The server refuses a caption when it has more than 3 words or 22 characters, lasts more than 3 s (or under 0.2 s), overlaps another caption, or contains words not spoken near those times. Words are compared after removing punctuation and case.

The render draws each accepted caption as a PNG pill with Pillow and overlays it at a fixed lane between its start and end (a hard replace: no fade between groups). Mapping: caption times are source times; the render maps them to output times through the accepted cuts. A caption whose start is not inside a kept cut is skipped. A caption that crosses a removed gap keeps its length from the start, so it can run into the next phrase: the review flags orphan captions (`/api/review`, kinds `orphan_caption` and `uncaptioned`).

Defaults in the shipped render (check your copy): pill text size about 5.8 percent of the size basis, pill top at 78 percent of frame height, centred, dark translucent pill with white text, one colour for the whole text. Two consequences:

1. Size basis. The shipped code uses the frame height. On a vertical 1080 by 1920 video that gives text about 111 px, and 22 characters no longer fit the width. Use the short side instead: pass `min(width, height)` to `caption_png`. Result at 1080 short side: about 63 px text. For heavier presence use a size factor up to 0.07 (about 75 px) and check the longest group fits (the checker does).
2. Lane. The 78 percent lane on a vertical frame puts the pill top at y 1498, so most of it sits below y 1500, the limit for text on phone apps. Move the lane up (see Step 6).

No highlight word is possible with the shipped single colour drawing. If the user chose a highlight, add the optional extension in `references/caption-scripts.md` (an `hl` field and a per word drawing function) before promising it.

## Step 3: Build from the final transcript

1. The transcript in `project/ingest.json` is the only source of caption words. If the audio changes (a new take, a cut that removes words, a retake), re ingest or edit the transcript, then regenerate captions. Captions made for an older cut are stale: list which ones.
2. Fix spellings in the transcript before captioning (`ae-ingest-and-transcribe`): proper nouns, product names, acronyms, numbers, hyphenated words, homophones. The server only accepts caption words that match the transcript, so a caption cannot be corrected by typing it differently; the fix goes into the transcript. Keep a glossary file `brand/glossary.txt` (one correct spelling per line) and tell the captioner to read it.
3. Numbers: make the transcript carry numerals if the user chose numerals. Whisper type tools output "forty eight" or "48" inconsistently; unify them once, before grouping.
4. After the final render, transcribe the render itself and compare it with the caption words (a word check in `ae-edit-qa-gates`): it proves the captions match the audio that people hear, including after fades and cuts.

## Step 4: Grouping rules

1. Size: 1 to 3 words and at most 22 characters (space included). One word groups only for emphasis or when the next word follows a pause.
2. Split where a person would breathe: at punctuation (`. , ; : ! ?`), at pauses of 0.12 s or more, and before clause starters (and, but, so, because, which, when, if, then, or) when the group already has two words.
3. Never end a group on a function word: the, a, an, to, and, or, but, of, your, my, our, for, in, on, at, by, with, from, that, this, these, those, as, if, than, so, is, are, was, were, be, I, we, you, it, because, which, when, while, where, into, about. Move the word to the start of the next group. When a split is forced (rare), try another break two words earlier, and only then accept it with a note.
4. Keep together: a number and its unit ("48 hours"), a name ("Claude Code"), a verb and its short object when the pause is under 0.12 s. Pass names with `--keep "Name One,Name Two"` to the tool.
5. Never split a word. Hyphenated words and contractions stay whole.
6. Timing: start 0.02 to 0.05 s before the first word (default 0.03); end at the last word's end, or just before the next group starts (never overlapping it). Minimum display: 0.35 s for two or more words, 0.25 s for one word (the server hard minimum is 0.2 s). Maximum 3 s; a longer pause means the caption goes off and the screen is clean.
7. Reading speed: more than about 4 words per second is hard to read. If the speaker is that fast, groups of 2 words and no highlight.
8. Replace, do not fade: the next group takes the lane at once. No two captions on screen together.
9. Orphans: avoid single word groups next to a 1 or 2 word group when they would still fit together under 3 words and 22 characters and there is no pause between them.

The tool `group_captions.py` (in `references/caption-scripts.md`, save it to `brand/tools/`) applies these rules with a small dynamic program that picks the lowest penalty set of splits. Its output is a first draft: read it aloud against the words, and fix awkward breaks by hand. Command:

```
python3 brand/tools/group_captions.py project/ingest.json --start 0 --end 33 --state project/state.json --keep "Brand Name" --ops W03
```

With `--ops W03` it prints one JSON operation per line. Send each with the editor API (one operation per call, read the answer):

```
curl -s -X POST http://127.0.0.1:8780/api/op -H 'Content-Type: application/json' -d '{"op":"caption","agent":"W03","start":0.37,"end":1.1,"text":"Feed it twice"}'
```

If the server says NO, read the reason: it is almost always a spelling that does not match the transcript, an overlap, or a group that is too long. Fix the cause and resend. Do not rephrase around it.

## Step 5: Highlight words

Only if the user chose a highlight and the render supports it.

1. At most one highlight word per group, and at most one group in three carries one, so it stays special.
2. Pick the word that carries the meaning: a number, a name, the verb of the claim, the contrast word ("only", "never"). Never a function word.
3. Colour: the theme accent, but only if the accent has contrast 4.5 or more against the pill (`caption.highlight_is_accent` in tokens). Otherwise use the italic accent font in the text colour.
4. The accent colour means "look here" across the whole video, so a highlight word does not also appear as a graphic accent in the same instant.
5. Store the choice as `hl` on the caption operation (extension) or as a separate list in `brand/captions-plan.md` read by the render. Never use markup characters inside the caption text, because the server compares the words.

## Step 6: Lanes, contrast and the face

A lane is a vertical position reserved for captions. Rules:

1. Never over the mouth or eyes. Look at stills of the first, middle and last group of each scene.
2. Vertical 1080 by 1920 starting values (approximate, verify on a real phone): pill bottom at y 1500 or higher up; for a full frame talking head the lane centre at about y 1330 to 1400 is usually below the chin and above the app UI; a split layout puts the lane on the seam between the graphic panel and the face. Top band (y 0 to 270) stays plain. Right rail (x 900 to 1080, y 980 to 1790) has no text: keep pills centred and under 960 px wide.
3. Landscape 1920 by 1080: lane centre at about 80 to 84 percent of the height, pills under 80 percent of the width, nothing in the bottom 6 percent.
4. Graphic gap: at least 60 px between the bottom of any graphic and the top of the caption pill, on every stretch (the plan check in `ae-lower-thirds-and-chapter-cards` tests this).
5. Contrast: text on pill at least 7 (the theme tool measures `ink` on `surface`). Bare text with no pill is only safe on calm, even backgrounds: use an outline of 3 to 4 px in the opposite tone plus a soft shadow, and test on the brightest and busiest frame (contact sheet of the whole video).
6. Do not rely on a thin font: weight 700 or heavier.
7. One style for the whole video. A second style needs a reason the user gave.

To move the lane edit the vertical fraction in the render (the `y=H*0.78` in the caption overlay). Compute it: `top = 1500 - pill_height - 20` for vertical at 1920 high, then divide by the frame height. A pill with 63 px text is about 100 px tall, so the top fraction is about 0.70.

## Step 7: Quiet windows (no double text)

When a graphic shows the same words on screen, the caption for those words is hidden for that time. Rule: if every word of a caption group is inside the text of a graphic and the times overlap, drop the caption (`group_captions.py --state` does this; the checker reports a WARN when one is left). Where a graphic repeats only part of a group, keep the group but check on a still that nothing reads twice in a distracting way. The server does not know about quiet windows, so the captioner removes them before sending operations or asks the reviewer to reject the item (`ae-agent-reviewer`).

## Step 8: Check before the render

```
python3 brand/tools/check_caption_groups.py project/state.json --ingest project/ingest.json --width 1080 --height 1920 --font brand/fonts/Inter-Bold.ttf
```

ERROR means a hard problem. WARN means a style problem: fix it or write down why it stays. It checks word and character counts, duration, overlap, function word endings, stray punctuation, reading speed, start lead against the first word, end against the last word, quiet window repeats, and pill width at the real font. Then look at stills: first group of each scene, a long group, a highlight group, the group next to each graphic, the last group. After the render, extract frames at 5 caption times and compare caption text with what is spoken.

Spell check: list every caption word that is not in `brand/glossary.txt` and not in a dictionary (`aspell list < words.txt` or `hunspell -l` if one is installed; otherwise ask the user for a word list). A typo on screen is a failed gate.

## Worked example (placeholder: a bakery explainer, vertical, 1080 by 1920)

Transcript (excerpt, times in seconds): Feed(0.40) it(0.58) twice(0.70) a(1.02) day(1.10) | After(1.90) 48(2.20) hours(2.42) it(2.65) doubles(2.80) | and(3.49) that(3.70) is(3.85) when(3.98) you(4.21) bake(4.36).

Groups produced and checked:

| Group | Start | End | Reason |
| --- | --- | --- | --- |
| Feed it twice | 0.37 | 1.10 | 3 words, breath before "a day" |
| a day | 1.11 | 1.58 | Ends the sentence; "a" opens the group, which is fine |
| After 48 hours | 1.90 | 2.64 | Number kept with its unit |
| it doubles | 2.65 | 3.17 | Pause follows |
| and that is | 3.49 | 4.20 | WARN: ends on "is". Hand fix: "and that" and "is when you" are also forced endings, so the sentence is the hard case; keep the least bad split and mention it |
| when you bake | 4.21 | 4.96 | Clause start kept at the head |

Highlight (if chosen): the number in "After 48 hours" and the verb in "when you bake". If a stat card "48 hours" is on screen at 1.95 s, the caption "After 48 hours" still stays (the graphic does not show "After"), but a caption that was only "48 hours" would be hidden. Result from the checker: 0 errors, 1 warning (the forced function word ending), accepted with a note.

## Failure modes

1. Caption sized from height on a vertical frame: huge text, groups wider than the screen.
2. Lane left at 78 percent on vertical: the pill sits in the app UI zone.
3. Transcript says "forty eight", caption wants "48": the server refuses; fix the transcript.
4. A caption ends on "the": reads as unfinished; carry the word forward.
5. Captions made from the script, not from what was said: they drift whenever the speaker ad libs.
6. Stale captions after a re cut: orphan captions and uncaptioned words in `/api/review`.
7. Highlight colour fails contrast on the pill: use italic in the text colour instead.
8. Same words as a graphic at the same time: hide the caption.
9. A caption crossing a cut: the render keeps its length and it overruns the phrase; split it at the cut.
10. Captions for a sped up or slowed clip use unmapped times: always map through the cuts.

## Checklist

- [ ] Profile `## Captions` answered; tokens built.
- [ ] Transcript spelling and numbers fixed; glossary written.
- [ ] Groups 1 to 3 words, 22 characters, 0.2 to 3 s, no overlap, no function word endings (or noted).
- [ ] Start lead 0.02 to 0.05 s; end at last word; minimum display met.
- [ ] Lane inside the safe zone; 60 px under any graphic; not over the mouth.
- [ ] Quiet windows applied; highlights limited to one in three groups.
- [ ] `check_caption_groups.py` has no ERROR; WARN lines resolved or explained.
- [ ] Stills looked at; after render, a word check compares captions with the audio.

More: `references/caption-scripts.md` (the grouping tool, the checker and the optional highlight drawing function).

Hand off to: `ae-agent-captioner` (places them), `ae-theme-builder` (pill colours and fonts), `ae-phone-safe-zones-and-formats` (lanes), `ae-lower-thirds-and-chapter-cards` (graphic gap and quiet windows), `ae-ingest-and-transcribe` (spelling fixes), `ae-edit-qa-gates` (word check on the render), `ae-owner-notes-to-rules` (every caption note becomes a rule).
