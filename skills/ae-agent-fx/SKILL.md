---
name: ae-agent-fx
description: Role skill for an effects agent in the Agent Editor. Places punch zooms and blur-ins on the shared timeline through the operation API, picks emphasis moments from the transcript, and respects both the spacing the server enforces and the extra spacing the render needs. Use when an agent is started with the role fx, or when the user says "add punch zooms", "add emphasis zooms", "add a blur in at the new section", "make the key lines pop".
---

# Agent Editor: effects agent (punch zoom and blur in)

Read `brand/profile.md`. If it is missing or a section this skill needs is empty, stop and run `ae-setup-interview` for that section (ask the user, with options), do not guess.

Sections used here: `## Platforms and formats` (frame shape, so you know what a 12 percent crop cuts off), `## Visual theme` (how restrained the look is), `## Rules` (any "never zoom on X" rule).

You are one agent in a team. The editor server runs at `http://127.0.0.1:8780` (or the port the conductor gave you). You change the timeline only by sending operations with `curl -s -X POST .../api/op`. Your role name is `fx`. Your whole job is emphasis: a few well chosen moments, never decoration.

## Questions to ask the user if the profile does not answer them

Ask once, as a short list with options. The user may answer freely.

1. How much emphasis motion do you want?
   a) Calm: about one punch zoom per 8 to 10 seconds of finished video, no blur ins.
   b) Standard: about one per 6 seconds, one blur in per new section.
   c) Energetic: about one per 4 to 5 seconds (the server minimum is 4 source seconds), blur in at every section.
   d) None on faces, only on screen recordings (tell me which parts are screen).
2. Is the main subject centred in the frame?
   a) Yes, a person centred. b) A person off to one side. c) A screen recording or product shot. d) Mixed (tell me where each part is).
3. Is there text burned into the footage near the edges (logos, labels, old subtitles)?
   a) No. b) Yes at the bottom. c) Yes at the top. d) Yes at the sides. (A zoom crops the edges, see below.)

If the user says nothing, use Standard and a centred subject, and say so in your `done` summary.

## What you may send

| op | You use it for |
| --- | --- |
| `hello` | First call: `{"op":"hello","agent":"W05","role":"fx"}` |
| `claim` | Before each piece of work: `{"op":"claim","agent":"W05","kind":"window","start":0,"end":33,"status":"choosing emphasis"}` |
| `fx` | The only edit you make |
| `done` | Last call, with a one line summary |

Do not send `cut`, `caption`, `graphic` or `music`. The server would accept them, but they belong to other roles and your window may overlap theirs. Never send `reject` (reviewer only) or `remove` (the person at the screen only).

## Exact rules the server enforces for `fx`

Fields: `type` (`punch_zoom` or `blur_in`), `at` (source seconds), optional `dur`.

| Check | Limit | The server's answer |
| --- | --- | --- |
| `type` | must be `punch_zoom` or `blur_in` | `type must be punch_zoom or blur_in` |
| `at` | a number from 0 to the source duration | `'at' must be a number` or `'at' must be between 0 and <duration>` |
| `dur` | 0.3 to 2.5 s; default 1.2 for a punch zoom, 0.3 for a blur in | `'dur' must be between 0.3 and 2.5` |
| Overlap with any other effect (either type) | none allowed | `overlaps f12 (punch_zoom at 1.87)` |
| Two punch zooms | start times at least 4 s apart (source seconds) | `punch zooms must be at least 4 s apart (f12 is at 1.87)` |

The server does not check that `at` is inside a kept cut, that it lands between words, that it fits your window, or that it matches an emphasis. Those are your job. A NO answer looks like `{"ok":false,"error":"..."}` (the HTTP status is still 200). Read the reason, fix the operation, send it again, do not argue.

## What the render does with your effects (this decides where you place them)

Read this table twice. It is taken from how the shipped render works.

| Fact | What it means for you |
| --- | --- |
| `at` and `dur` are in source seconds, but the finished video only contains the kept cuts | Always convert to output time (`references/output-time-helper.md`) before judging spacing |
| A punch zoom is applied only if `at` is inside a kept cut. Its end is clamped to the end of that cut | A zoom whose start sits in removed material is silently skipped. A zoom that runs past a cut end is shortened |
| A punch zoom is a constant crop of about 12 percent (scale 1.12) with a hard switch at both ends, no easing | It behaves like a cut-in. Choose the start on a word boundary and expect a visible jump |
| Each side of a 12 percent crop loses about 5 to 6 percent of the frame | Text, logos or faces near the edges can be cut off. Check a thumbnail |
| Every segment boundary (including a zoom boundary) gets a 12 ms audio fade in and out | A zoom edge inside a spoken word makes a tiny dip in that word. Put both edges in the gaps between words |
| A blur in is a box blur on the first 0.16 s from `at`, then the picture snaps sharp. The `dur` you send does not change that 0.16 s | Send the default `dur` (0.3). A longer `dur` only blocks other effects for no visual gain |
| A blur in is skipped if `at` is not inside a kept cut | Same check as for zooms |
| Punch zooms and blur ins cannot overlap in time | Leave at least 0.3 s between a blur in and the first zoom after it |

## Procedure

1. `hello`, then `claim` your window (`kind` `window` with `start` and `end`, status under 60 characters).
2. Read the window: `curl -s 'http://127.0.0.1:8780/api/window?start=0&end=33'`. You get words with times (`t` start, `e` end), silences, sentences, and what is already placed (cuts, captions, fx within 3 s of the window, graphics within 3 s).
3. Find out whether the cutters are done. Read `/api/state` (the `agents` object shows `done`). If cuts are not final, build your candidate list now, but place nothing until the cuts in your window are stable. Rejected cuts disappear, and a zoom that lost its cut is skipped by the render.
4. Build candidates from the transcript only (next section). Never invent words or times.
5. Choose the final set using output-time spacing (section below).
6. Snap each zoom start and end into gaps between words (section below).
7. Send one `fx` operation per call. Read the answer before the next one. Re-claim when you move to a new part of the window.
8. After the cutters and reviewer finish, re-read `/api/state`. Check every effect of yours is still inside a kept cut. If a cut was rejected and re-placed, move your effect (you cannot edit it, see "No take backs").
9. Send `done` with a summary of under 20 words.

## Choosing the moments (emphasis scoring)

Score each candidate, keep the highest scores that satisfy spacing. A candidate is a word or short phrase.

| Signal | Points |
| --- | --- |
| The turn of a claim: "but", "instead", "actually", "not X, it is Y", a reversal | 3 |
| A number, price, count or time that the sentence depends on ("seven days") | 3 |
| The payoff word or phrase of a sentence (the last stressed phrase before a stop) | 2 |
| The first words after a pause of 0.35 s or more (a fresh thought) | 2 |
| A named thing introduced for the first time | 1 |
| The first sentence of the video (the hook) | 1 |
| Filler, a connective, or a word the speaker rushes (under 0.15 s) | 0, never zoom here |

Numbers are better served by a `stat_card` from the graphics agent. If a graphic starts within 1 s of your zoom (check `graphics` in the window), skip your zoom or move it: one emphasis device per moment. When two moments tie, keep the one nearer the start of the video, because early emphasis sets the rhythm.

Density target (starting values, adjust to the user's answer):

| Output length of your window | Punch zooms |
| --- | --- |
| under 12 s | 1 |
| 12 to 24 s | 2 to 3 |
| 24 to 40 s | 4 to 5 |
| 40 s or more | about one per 6 s, never more than 6 in a 33 s source window |

The shipped agent brief asks for 4 to 6 punch zooms per window. Follow it when the kept (output) length supports it. When the window is shorter, place fewer and say why in `done`.

## Spacing in output time (the part most agents miss)

The server only checks 4 s between zoom starts in source time. If the cutters removed 5 s of pauses between two zooms, they can sit 1 s apart in the finished video and feel like a stutter.

1. Convert each chosen start to output time with the helper in `references/output-time-helper.md`.
2. Require at least 5 s between zoom starts in output time (starting value; 4 s is the least acceptable, 6 to 8 s feels calm).
3. If two candidates are too close in output time, keep the higher score and drop the other.
4. Keep the last zoom at least 1.5 s before the end of the video, so the last line is not cropped.

## Snap the edges into gaps

1. Start: find the gap just before the emphasised word. If the gap is 0.12 s or longer, use `next_word.t - 0.06`. If it is shorter, use the midpoint of the gap. Never start inside a word.
2. End: choose `dur` so that `at + dur` lands in a gap after a word, between 0.9 and 1.6 s (default 1.2 when it fits). The end must also be at or before the end of the cut that contains the start. Cut ends sit in removed gaps, so ending 0.02 s before the cut end is normal.
3. The crop applies for the whole `dur`, so cover a whole phrase or clause, not half of one.
4. Stay 0.3 s or more from other effects.

## Blur in

Use one `blur_in` at the start of a genuinely new section (a new topic after a pause, a chapter title). Rules:

1. Put `at` at the first kept frame of the section: the start of the cut that begins it, or `first_word.t - 0.06`.
2. Never at output time 0. The first 0.16 s of the video should be sharp for the thumbnail and the first frame.
3. At most one per 15 s of finished video (starting value). If the user chose "Calm", use none.
4. Do not put a blur in on the same moment as a chapter title graphic that starts a transition of its own; one change at a time.
5. Send the default duration (omit `dur`).

## Frame check before you zoom

The zoom crops about 5.5 percent from each side and each of top and bottom. Fetch a thumbnail near each zoom: the editor serves a still every 2 seconds at `http://127.0.0.1:8780/project/thumbs/t001.jpg` (the first is time 0, the number is the index plus 1). Save it with `curl -o` and look at it if you can view images.

1. A face centred: safe.
2. A face off to one side or a person holding something at the edge: the crop may cut it. Skip that moment, or ask the conductor.
3. Burned in text, logos or labels near the edges: skip, or tell the user (question 3).
4. A screen recording: only zoom where the important part is central.

## NO answers and what to do

| The server says | Do this |
| --- | --- |
| `overlaps f12 (...)` | Move the new effect after that one ends, or drop it. Your own earlier effect counts too |
| `punch zooms must be at least 4 s apart (f12 is at 1.87)` | Pick the other candidate, or shift by whole phrases. Do not nudge by 0.1 s to sneak under the rule |
| `'at' must be between 0 and 33.4` | You used output time or a window offset. Use source seconds |
| `'dur' must be between 0.3 and 2.5` | Shorten or lengthen to a gap boundary inside that range |
| `agent is required` / `say hello first` | Send `hello` with your agent id |

## No take backs

You cannot edit or withdraw an effect. Only a reviewer can reject it, or the person at the screen can delete it. Compute everything before you send. If you find a mistake after sending, tell the conductor in `done`, with the id and the reason, and wait for a rejection before placing a replacement (an overlapping replacement is refused while the old one is live).

## Worked example (neutral placeholder content)

A local bakery explains how to revive a sourdough starter. Window 0 to 8.2 s of the source. Cutters are done, with these kept cuts: c1 0.34 to 2.54, c2 2.99 to 4.26, c3 4.94 to 6.89, c4 7.34 to 8.14. Output starts: c1 0.00, c2 2.20, c3 3.47, c4 5.42.

Words (source seconds): "is" 1.70 to 1.82, "not" 1.92 to 2.10, "dead," 2.10 to 2.50, "seven" 6.18 to 6.50, "days" 6.50 to 6.85.

Candidates:

| Phrase | Source at | Output | Score | Note |
| --- | --- | --- | --- | --- |
| "not dead," | 1.87 | 1.53 | 3 + 1 (hook) | Claim reversal. Gap before "not" is 0.10 s, so the midpoint 1.87 |
| "seven days" | 6.15 | 4.68 | 3 | A number. A graphics agent will likely put a stat card here |
| "wakes up" | 7.52 | 5.60 | 2 | Too close to the second one in output time |

Output spacing between the first two is 3.15 s, under the 5 s target even though the server would accept it (source gap 4.28 s). Keep "not dead," and leave "seven days" to a stat card. Duration: the cut c1 ends at 2.54, "dead," ends at 2.50, so the end must be at or before 2.54. Choose `dur` 0.65, which ends at 2.52 in the gap after "dead,".

```
curl -s -X POST http://127.0.0.1:8780/api/op -H 'Content-Type: application/json' -d '{"op":"hello","agent":"W05","role":"fx"}'
curl -s -X POST http://127.0.0.1:8780/api/op -H 'Content-Type: application/json' -d '{"op":"claim","agent":"W05","kind":"window","start":0,"end":8.2,"status":"choosing emphasis"}'
curl -s -X POST http://127.0.0.1:8780/api/op -H 'Content-Type: application/json' -d '{"op":"fx","agent":"W05","type":"punch_zoom","at":1.87,"dur":0.65}'
```

The answer is `{"ok":true,"id":"f12","item":{...}}`. A later attempt at 4.20 would return `{"ok":false,"error":"punch zooms must be at least 4 s apart (f12 is at 1.87)"}`, so you do not send it. Final message: "Placed 1 punch zoom (f12 at 1.87, not dead). Skipped seven days for a stat card, spacing 3.2 s in output. Server refused nothing."

## Checklist (tick every line before `done`)

- [ ] Profile read; intensity question answered or defaulted and stated.
- [ ] Every candidate comes from words in the transcript.
- [ ] Every start is inside a kept cut and in a gap between words.
- [ ] Every end is inside the same cut and in a gap between words.
- [ ] Output spacing between zooms is 5 s or more (or the reason is in `done`).
- [ ] No effect within 1 s of a graphic.
- [ ] No blur in at output time 0; at most one per 15 s.
- [ ] Thumbnails checked for edge content near each zoom.
- [ ] Every NO read and fixed, nothing forced.
- [ ] Final message under 60 words: what you placed and what the server refused.

## Do not

- Do not zoom on filler words, connectives or the last second of the video.
- Do not stack a zoom on a graphic or on a chapter blur at the same moment.
- Do not try to "improve" a refused operation by changing `type` or `dur` until it passes if the emphasis no longer makes sense.
- Do not edit outside your window or touch other roles' items.
- Do not render or export. The conductor and the user control that (see `ae-export-once-workflow`).

Hand off to: `ae-agent-reviewer` (checks your effects against the render facts above), `ae-run-multi-agent-edit` (the conductor that reads your `done`), `ae-pacing-and-rhythm` (how many emphasis moments a given length can carry), `ae-transitions-and-blur` (when a blur is the right transition), `ae-motion-design-principles` (restraint and one hero per scene), `ae-edit-qa-gates` (the pre delivery table).
