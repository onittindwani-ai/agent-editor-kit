---
name: ae-counters-and-numbers
description: Animate numbers so they tick in even steps and land exactly on the spoken number, with display formats, planning backwards from the word time, sourced values only, honest labelling of examples, and bars, rings and charts that never show invented figures. Use when a script says a number, price, percentage, count or time, when the user asks for a counter, "count up", a stat card, a chart or a gauge, or says "the number lands late".
---

# Counters and numbers

Read `brand/profile.md`. If it is missing or a section it needs is empty, stop and run `ae-setup-interview` for that section (ask the user, with options), do not guess. This skill needs `## Visual theme`, `## Claims policy`, `## Script preferences` (how numbers are written) and `## Sound`; read `brand/theme.json` for fonts and colours.

## Hard rules

1. **Every number on screen is real or labelled.** A figure shown as fact must have a ledger row with a source and the date checked (`ae-claims-and-truth-ledger`). Never invent a number to fill a gauge, a chart or a dashboard. An illustrative figure carries the word "Example" at 28 px or more.
2. **The counter lands on the spoken number.** The final step is on the frame the speaker finishes saying the number (or within 3 frames after). Plan backwards from the word time (below).
3. **Never show more precision than the source has.** If the source says "about 4 million", do not display "4,012,336". If the speaker rounds, the screen matches the speaker's rounding and the exact figure stays in the ledger.
4. **Screen and speech agree.** If the speaker says "four point two million", show "4.2M" or "4,200,000", not "4.25M".
5. **No decorative numbers.** No gauge, ring, dial, meter, graph or "dashboard" with figures that did not come from a source. A counter exists because the script states a number.
6. **Units and sign stay with the number** during the whole animation (the dollar sign does not pop in at the end).
7. **Nothing else moves under a counter while it counts**; it is the focal point.

## Plan backwards from the word

You know the time the speaker finishes the number word (`ae-word-synced-graphics`, the `e` field of the last word of the phrase, in seconds). Convert:

```
land_frame  = round(word_end_seconds * fps)            # the frame the FINAL value first appears
step_frames = 10                                        # 0.333 s per step at 30 fps (8 frames at 24 fps)
start_frame = land_frame - (n_steps - 1) * step_frames  # the frame the FIRST value after the start value appears
settled     = card entrance frame + entrance length     # the card must be settled before the first tick
require       start_frame >= settled + 3
```

At 30 fps each step is 10 frames (one third of a second); at 24 fps it is 8 frames; at 60 fps 20 frames. Choose `n_steps` between 4 and 12:
- Small numbers (under 100): 4 to 6 steps.
- Hundreds or thousands: 6 to 9 steps.
- Millions and above: 8 to 12 steps.
- If the word comes too early for the chosen steps (the `require` line fails), reduce `n_steps` rather than starting before the card is settled. If even 4 steps do not fit, show the final number sharp on the word with a short blur clear (6 frames) and no counting.

The counter ticks in **even steps** (a step function), not a smooth ramp, so each value is readable and the motion feels deliberate:

```
value(frame) = start_value + (final_value - start_value) * k / n_steps
where k = 0 for frame < start_frame,
      k = min(n_steps, floor((frame - start_frame) / step_frames) + 1) for frame >= start_frame
```

Before `start_frame` show the start value (usually 0, or the prior figure in a "from X to Y" story). The final value appears at `start_frame + (n_steps - 1) * step_frames = land_frame` and stays. Round intermediate values to "nice" numbers: for 4,200,000 with 6 steps show 700K, 1.4M, 2.1M, 2.8M, 3.5M, 4.2M (equal increments, rounded to the display precision). Never display an intermediate value that looks like a real figure of its own (for example a believable price on the way to a price).

## Display formats

Pick the format from the spoken form and the profile. Always keep one format per number through its whole animation.

| Spoken | Show | Notes |
|---|---|---|
| "four thousand two hundred" | 4,200 | thousands separator per locale in the profile |
| "four point two million" | 4.2M or 4,200,000 | choose one style per video |
| "forty two percent" | 42% | no space before the percent unless the profile says so |
| "ninety nine dollars" | $99 | currency sign fixed from frame 0 |
| "three and a half hours" | 3.5 h or 3h 30m | match the speaker's phrasing |
| "from twelve to forty eight" | 12 then 48 | start value is the first number, not 0 |
| "a hundred and fifty times" | 150x | |
| "up by two thirds" | 67% only if the source says so | never convert a fraction to a precise percent unless the ledger does |

Typography:
- Use **tabular (fixed width) numerals** so digits do not jitter: in CSS `font-variant-numeric: tabular-nums`; in a Pillow renderer choose a font with tabular figures or draw each digit in a fixed width cell.
- Reserve the **final width** of the number from frame 0 (centre or right align inside a box sized for the last value) so the layout does not shift as digits are added.
- Number size: hero numbers at least 96 px on a 1080 px wide canvas, at least 64 px in a list, label at least 36 px.
- The number uses the theme's heading or accent font; do not add a third family (`ae-theme-builder`).
- Rolling digit columns (an odometer) are allowed when the theme is playful; keep the same step timing and land on the same frame.

## Counter anatomy and timing (30 fps)

| Part | Frames | Notes |
|---|---|---|
| Card (container) enters with the number present | 12 to 20 | the container and the start value enter on the same frame, never an empty card |
| Wait before the first tick | 0 to 6 | the card must be settled |
| Ticks | `(n_steps - 1) * 10` between first and last value | the last value appears on `land_frame` |
| Landing accent | 8 to 12 | a small pop (scale 1.0 to 1.04 to 1.0) or a brief accent colour on the final value; optional |
| Hold after landing | at least 36 (1.2 s) | longer if the label has more than 3 words (add 8 per extra word) |
| Exit | 4 to 10 or a hard cut | per `ae-transitions-and-blur` |

Sound lead: a soft recorded tick or pop on each step is too busy for more than 6 steps; prefer **one** sound on the landing, placed 2 to 6 frames before `land_frame`, plus optionally a quiet tick on the first step. Never reuse the same file within 75 frames. See `ae-sound-effects-placement`.

## Bars, rings, lines and charts

- A bar or ring grows from 0 to the sourced value on the same frames as the counter and stops on the same frame; use the overshoot easing at most 12 percent and settle within 8 frames, or no overshoot.
- Axes and labels are real (the source's own labels, spell checked). Axis scales start at zero for bars unless the source explicitly says otherwise and the break is shown.
- A mini chart rises to its final value in 24 to 45 frames and holds; all points are real data points from the source. If the source only gives two numbers, draw two bars, not an invented curve.
- A comparison ("A is 3 times B"): both numbers appear in spoken order, each on its word, and the ratio is shown only if it is in the source or is simple arithmetic you show your working for in the ledger.
- Percent of a whole: show the whole as 100 percent; segments sum to 100 percent after rounding (adjust the largest segment's rounding and note it in the ledger).

## Spoken versus written numbers

- Follow the profile's rule (numerals versus words) for captions and text. Spell digits the way the speaker says them in the transcript so captions and counters match.
- Years are not counters. Dates and phone numbers are never animated.
- If the speaker corrects a number ("three, no, four"), show only the corrected number and land on the second.
- If the speaker says a range ("three to five days"), show the range as text ("3 to 5 days") with the first number landing on its word and the second on its word, or as a bar with two markers; do not count to a single value.

## Sourcing and labelling

For each number record in the ledger: value, unit, source, date, evidence class, safe wording, and whether the screen shows exact or rounded. On the card show a source line when the number is a factual claim (same rules as `ae-proof-cards-and-real-screens`). For numbers the user measured themselves, show "Our test" or the wording the user chooses, never an implied independent study.

If the user cannot give a source: either remove the number from the graphic, hedge the wording ("about", "roughly") if the speaker already does, or label the card "Example". Do not make up a figure to make the visual look good.

## Questions to ask the user

1. Counting style: (a) even ticks (recommended), (b) smooth count up, (c) odometer rolling digits, (d) no counting, the number just appears sharp.
2. Number format: (a) 4.2M, (b) 4,200,000, (c) four point two million written in full words.
3. Source line on number cards: (a) always, (b) only for factual claims, (c) never (the profile `## Claims policy` must allow it).
4. Should the final number get an accent (a pop or the accent colour)? yes, subtle only, no.
5. Currency and thousands separators (locale) if the profile does not say.

Store answers via `ae-profile-schema`.

## Worked example (synthetic)

A bakery says: "Last year we baked 4,200 loaves." The number phrase "4,200" ends at 8.70 s, the card enters at frame 230 and is settled by frame 246.

Case A, the word comes too soon: `land_frame = round(8.70 * 30) = 261`. Even 4 steps need `start_frame = 261 - 30 = 231`, which is before the card is settled (246 + 3). So do not count: show "4,200" sharp on the word with a 6 frame blur clear starting at frame 255, plus the landing pop from frame 261 to 270.

Case B, more time: the number ends at 11.0 s, `land_frame = 330`. With `n_steps = 6`, `start_frame = 330 - 5 * 10 = 280`. Values appear at frames 280, 290, 300, 310, 320 and 330 as 700, 1,400, 2,100, 2,800, 3,500 and 4,200. The `require` check passes (280 is at least 249). The landing sound goes at frame 325 (5 frames early). Hold until frame 366 at minimum (36 frames after landing), longer if the label is more than 3 words.

Rule in one line: the **last value appears on `land_frame`**.

## Failure modes

- Counter lands after the speaker has moved on.
- Counter finishes seconds before the word (the viewer reads it, then hears it, which kills the moment).
- A chart with a made up trend line.
- Digits that jitter because the font is not tabular.
- The layout shifting as the number grows.
- The currency sign popping in at the end.
- A gauge showing a score the user never measured.
- Two numbers landing on one word.
- A screen number that differs from the spoken number.

## Checklist

- [ ] Every number has a ledger row or an "Example" label
- [ ] Format chosen; screen matches speech and rounding
- [ ] Land frame = word end; last value on that frame; start planned backwards
- [ ] 4 to 12 even steps of 10 frames at 30 fps (8 at 24)
- [ ] Container present from the first frame; width reserved; tabular numerals
- [ ] Hold 36 frames or more after landing
- [ ] One landing sound 2 to 6 frames early; no repeat within 75 frames
- [ ] Bars and rings stop on the same frame; real axes and labels
- [ ] Still checked at the land frame and at 360 px wide

## Hand off to

`ae-word-synced-graphics`, `ae-motion-design-principles`, `ae-proof-cards-and-real-screens`, `ae-claims-and-truth-ledger`, `ae-lower-thirds-and-chapter-cards`, `ae-sound-effects-placement`, `ae-caption-style-and-grouping`, `ae-edit-qa-gates`.
