---
name: ae-motion-design-principles
description: The taste and numbers behind motion graphics for short and long video: timing in frames at 30 fps, easing curves, springs, entrance and exit lengths, reading holds, hierarchy, one hero moment per scene, motion budget, sound lead, and the pure function of time rule for Remotion or any frame renderer. Use before building or reviewing any graphic, scene, overlay or animated text, and when the user says "make it look premium", "it looks cheap", "too busy", "too fast to read" or "not smooth".
---

# Motion design principles: taste with numbers

Read `brand/profile.md`. If it is missing or a section it needs is empty, stop and run `ae-setup-interview` for that section (ask the user, with options), do not guess. This skill needs `## Visual theme`, `## Platforms and formats` and `## Sound`; also read `brand/theme.json` for palette, fonts and radius. Never hard code a colour, font or accent: take them from the theme.

All frame numbers below assume **30 fps**. For 24 fps multiply frame counts by 0.8, for 60 fps by 2. Store beats in seconds and convert with `frame = round(seconds * fps)`.

## The one rule that makes everything else work: time is a pure function

Every graphic is `f(frame)`. Given a frame number it returns exactly the same pixels, every time, on every machine.

Required:
- One timeline file per graphic (seconds, named beats). Components read it; nothing hard codes a start time.
- Animation values computed from the frame number only.
- Random looking variation from a seeded hash of an integer (see `references/pure-function-helpers.md`).

Forbidden:
- CSS transitions, CSS keyframe animations, `requestAnimationFrame` loops, `setTimeout` driven state.
- `Math.random()` and any unseeded random.
- `Date.now()`, `performance.now()` or any wall clock.
- Reading a value written by a previous frame (state that depends on render order). Render order is not guaranteed when frames render in parallel.
- Network or file reads inside a frame function (preload and pass as props).

Why: renders run in parallel chunks and are re run to fix one note. If time is not a pure function, frames flicker, drift or differ between a preview and the final render. Retiming then means editing the beat file and re rendering only what changed.

This works the same in Remotion (use the frame from its hook and its `random(seed)` helper) and in a plain Python or Node frame renderer (loop over frame numbers, call `draw(frame)`). If the user is a company, check Remotion's current licence terms before relying on it (it is free for individuals and small teams under its published conditions; larger companies need a paid licence); say so once and let the user decide. Offer the plain renderer path when licence is a blocker.

## Easing: pick by job

Curves are CSS style cubic beziers `(x1, y1, x2, y2)`. Implementation in `references/pure-function-helpers.md`.

| Job | Curve | Notes |
|---|---|---|
| Entrance, reveal, anything arriving | `(0.16, 1, 0.3, 1)` ease out | Fast start, long soft landing |
| Exit | `(0.6, 0, 0.9, 0.35)` ease in | Leaves fast, does not linger |
| Move between two states (dock, flip, zoom) | `(0.65, 0, 0.35, 1)` ease in out | Symmetric, camera like |
| A value that lands (bar climbing to a number) | `(0.55, 0, 0.2, 1.12)` slight overshoot | Overshoot at most 12 percent, settle inside 8 frames |
| Continuous motion (slow drift, rotation of a clock hand) | linear | Only for things that never start or stop abruptly |

Never use linear easing on anything that starts or stops. Never use bounce curves for text.

## Springs (for things that feel physical)

Use springs for UI objects and badges, bezier tweens for type and camera like moves. Starting values for `damping / stiffness / mass`:

| Feel | Values | Used for |
|---|---|---|
| Default settle | 14 / 140 / 0.8 | cards and chips entering |
| Heavy and calm | 15 to 20 / 140 to 240 / 0.6 to 1 | large panels, full frame swaps |
| Snap to a step | 12 / 190 / 0.75 | a control or tab clicking into place |
| Pop | 9 to 11 / 200 to 230 / 0.7 | badges, check marks, success dots |
| Elastic accent | 8 / 200 / 0.7 | one hero moment per video, never more |

A spring must settle (velocity under 0.001 and position within 0.5 px) before its element is read. Settling takes roughly 12 to 24 frames at these values; check by sampling.

## Lengths in frames (30 fps)

| Motion | Frames | Seconds | Notes |
|---|---|---|---|
| Text blur to sharp entrance | 4 to 10 | 0.13 to 0.33 | start blur 8 to 12 px, end 0 |
| Chip, tag or label entrance | 6 to 10 | 0.2 to 0.33 | scale 0.94 to 1.0 with the blur clear |
| Card or panel entrance | 12 to 20 | 0.4 to 0.67 | ease out, no overshoot |
| Full frame graphic entrance (ready content) | 6 to 8 blur clear after a hard cut | 0.2 to 0.27 | see `ae-transitions-and-blur` |
| Exit | half of the entrance, usually 4 to 10 | 0.13 to 0.33 | ease in; for most elements a hard cut is fine |
| Stagger between words | 3 | 0.1 | one word per beat when synced to speech |
| Stagger between list items | 6 to 8 | 0.2 to 0.27 | only if not synced to speech; synced items land on their word |
| Stagger between small dots | 2 | 0.06 | |
| Typing | 2 to 2.5 per character | 12 to 16 characters per second | only for things that are really typed |
| Underline or marker draw | 9 to 14 | 0.3 to 0.45 | line grows along the text, arrowhead last |
| Counter step | 10 per step | 0.333 | see `ae-counters-and-numbers` |
| Ease in out camera style push in | 90 to 150 total | 3 to 5 | scale 1.0 to 1.035 over a whole graphic so no frame is frozen |

An entrance may start up to about 9 frames (0.3 s) before the spoken word, starting value 4 frames (0.12 s); the text itself is never readable before the word is said. Details in `ae-word-synced-graphics`.

## Reading holds

A viewer must be able to read a state after it settles.

- Short phrase (up to 3 words): hold at least 30 frames (1 s).
- Each extra word beyond 3: add 8 frames (0.25 s).
- Final line or call to action: hold at least 60 frames (2 s).
- A number with a label: hold at least 36 frames (1.2 s) after the counter lands.
- Never move text while it is meant to be read. Motion stops, then the hold starts.
- When in doubt, hold longer and animate less.

Example: a 7 word line settles at frame 40, so it needs 30 + 4 * 8 = 62 frames of hold, and may exit from frame 102.

## Hierarchy and restraint

1. **One focal point per frame.** If two things compete, one waits (enters later or dims to about 70 percent).
2. **One hero moment per video.** The largest, longest or most elastic move is spent once, late enough to be earned.
3. **Two type voices.** One heavy sans for headlines, numbers, UI text and captions plus one light italic accent per headline. At most two families in view. Labels and anything that matters are at least 36 px on a 1080 px wide canvas; hero words and numbers at least 64 px.
4. **One accent colour, one meaning.** Inside one video an accent keeps its meaning (for example "the answer" or "done") and never swaps. Third party brand colours appear only inside their own tile.
5. **Contrast step.** A card must read as separate from its background: at least a 20 percent relative luminance step, or a 2 px rim plus a contact shadow. Check with `ae-theme-builder` tokens.
6. **Safe area.** Keep content inside the safe zones in `ae-phone-safe-zones-and-formats` (and at least 60 px from any frame edge).
7. **Padding.** At least 40 px between any element and its container edge, equal on all sides.
8. **No empty containers.** A card and its content enter on the same frame. The only permitted ghost is a row of real text blurred 6 to 8 px that sharpens on its spoken word.
9. **Frame 0 is a real image.** A sharp anchor element is on screen at frame 0 because it can become the thumbnail.

## Motion budget (restraint)

- No decorative rotation, spinners, orbits or looping shines.
- At most 2 light sweeps or travelling lines in a whole video; at most 2 hand drawn marks.
- No neon glow, no rainbow gradient, no bounce.
- Something always moves while the speaker talks, but slowly: a push in, a drift of a few px per second, a new element every 15 to 45 frames (0.5 to 1.5 s). No stage unchanged for more than 75 frames (2.5 s) except a final hold.
- Every moving element carries meaning: it arrives, connects, counts or reveals.
- Every move lands and settles before the clip ends. No line, dot, counter or cursor is mid travel on the last frame, and nothing points off frame. End on a settled hold of at least 9 frames (0.3 s).

## Continuity

- Prefer one persistent object that changes state (a list card that gains a row, a bar that grows) over a new card per idea, when the script has 3 or more parts. Its labels are the spoken nouns taken from the transcript.
- A connector that leaves one clip must land on the same position, size and colour on the first frame of the next clip, and the two clips sit back to back.
- Neighbouring stretches use different grammars (a claim, a contrast, a list, a proof, a number); do not reuse the same card with new words.

## Sound lead (details in `ae-sound-effects-placement`)

- A sound sits 2 to 6 frames (0.05 to 0.2 s) before the entrance it belongs to.
- Sounds belong on entrances, persistent object state changes and counter landings, never on caption swaps.
- One soft family of sounds with several files; the same file is never reused within 75 frames (2.5 s).
- Recorded, licensed sound files only; never invent a sound. Tell the user which files were used because the agent cannot hear.
- Never place a whoosh so it lands at the end of a spoken word; check the user's banned list in the profile.

## Questions to ask the user (if `## Visual theme` is thin)

1. Motion personality: (a) calm and editorial, (b) crisp and quick, (c) playful with small springs, (d) cinematic with slow pushes.
2. Graphic density: (a) minimal, a few moments, (b) steady, something every 1 to 2 seconds, (c) dense, a new element every second.
3. Sweeps and highlights: allowed up to 2, none at all, or the user's choice per video.
4. Hero moment: ask what the one biggest moment of the video should be.
5. Reading level: slower holds for a general audience, or tighter for a fast audience.

Store answers through `ae-profile-schema`.

## Review loop (never call it done unblind)

1. Render a draft at half resolution.
2. Build a contact sheet with one frame at each beat plus 9 frames (0.3 s) so motion has settled; 4 by 2 tiles with timestamps.
3. Look at every sheet. Zoom into: the first 45 frames at every 3 frames (does it look like a loading screen?), every seam, the last 15 frames of each clip.
4. Shrink a tile to 360 px wide: can the key message still be read?
5. Fix with exact numbers ("move the entrance 4 frames later"), re render only what changed, look again.
6. Report what was checked and which sheet shows it. Never claim a fix you did not re render and look at. See `ae-edit-qa-gates`.

## Worked example (synthetic)

A bakery explains "3 reasons your sourdough is dense". Beats file (seconds): `title 0.2, r1 3.4, r2 6.1, r3 9.0, hero 12.3, hold_end 14.8`. At 30 fps: title frame 6, reason 1 frame 102, reason 2 frame 183, reason 3 frame 270, hero frame 369, end hold from frame 444.

- One persistent list card enters at frame 6 (16 frame ease out) with three blurred real text rows.
- At each reason frame minus 4, that row sharpens over 8 frames and its marker draws over 12 frames; a soft pop plays 5 frames before the entrance.
- The hero moment (frame 369) is the one spring with elastic accent values: the finished loaf photo scales 0.94 to 1.0.
- A 3.5 s slow push in (scale 1.0 to 1.035) runs under everything, so no frame is frozen.
- Last frame has the list complete, the marker landed, nothing travelling; hold from 444.

## Failure modes

- Everything fades in at once with the same duration.
- Linear easing on entrances.
- Text moving while it should be read.
- Two focal points.
- Looping decoration that looks like a loader.
- CSS animation or random used, so a re render differs.
- Hero move spent early.
- Content too near an edge or in a platform UI zone.

## Checklist

- [ ] Profile and theme read; no hard coded colour or font
- [ ] Beats in one file in seconds; frames computed
- [ ] Every value a pure function of frame; no random, no CSS animation, no clock
- [ ] Entrance 4 to 20 frames, exit about half, hard cut allowed
- [ ] Reading holds met (30 frames plus 8 per extra word)
- [ ] One focal point, one hero moment, two type voices, one accent meaning
- [ ] Motion budget respected (sweeps at most 2, no decorative rotation)
- [ ] Everything lands before the clip ends; settled hold of 9 frames or more
- [ ] Sound lead 2 to 6 frames; no repeat within 75 frames
- [ ] Contact sheets looked at, phone size test done

## Hand off to

`ae-word-synced-graphics`, `ae-proof-cards-and-real-screens`, `ae-counters-and-numbers`, `ae-transitions-and-blur`, `ae-lower-thirds-and-chapter-cards`, `ae-theme-builder`, `ae-sound-effects-placement`, `ae-phone-safe-zones-and-formats`, `ae-edit-qa-gates`.
