---
name: ae-transitions-and-blur
description: Choose and build transitions between the talking head and graphics: hard cuts, blur into a graphic, punch zooms, with exact frame lengths, easing, seam rules, and checks for flashes, ghosts, face slivers and double heads. Use when the user says "the transition looks cheap", "flash at the cut", "I see my face through the graphic", "too many effects", "make it smooth", or whenever a graphic starts or ends, a jump cut is zoomed, or a seam needs checking.
---

# Transitions and blur

Read `brand/profile.md`. If it is missing or a section it needs is empty, stop and run `ae-setup-interview` for that section (ask the user, with options), do not guess. This skill needs `## Visual theme`, `## Sound`, `## Platforms and formats` and `## Rules`.

All frame counts assume **30 fps** (multiply by 0.8 at 24 fps, by 2 at 60 fps).

## The default policy in one table

| Seam | Treatment | Why |
|---|---|---|
| Talking head to a full frame graphic | Blur the face layer over 8 frames, then cut to the graphic at full opacity and sharpen it over 6 to 8 frames | Reads as a deliberate focus change |
| Graphic to talking head | Straight cut | A fading graphic shows the face layer through it |
| Graphic to graphic | Straight cut (the incoming graphic is opaque from its first frame) | No face frames in between |
| Talking head to talking head (jump cut) | Straight cut, optionally alternate a small scale change (see punch zoom) | A jump cut is normal speech editing |
| Partial overlays (lower third, chip, caption pill) | Short blur to sharp or slide, fade allowed | They do not replace the face |
| Anything else | Do not invent a new transition | Restraint is the premium look |

Blur is not applied at every transition. Even talking head to graphic gets it only where it helps (the graphic is the point of the next beat). A video where every seam has an effect looks cheap.

## Hard rules

1. **No opacity fades on a full frame graphic, ever.** If a graphic fades in or out, the face (or the previous graphic) shows through it for several frames. Use blur keyframes only, then cut.
2. **No face frames between two graphics.** If the gap between two graphics holds a face for less than 36 frames (1.2 s), extend the earlier graphic to hold through it and cut straight to the next. Do not leave a sliver of face.
3. **No ghost.** At a jump cut the face layer must not show a double head (an old matte or an unmatched cutout). If a person cutout is used, matte per segment and check the frames on both sides of every cut.
4. **No flash.** The incoming scene is opaque from its first frame. When two graphics overlap, the incoming one is fully opaque while the outgoing one is still present underneath for about 9 frames (0.3 s) only if you need a safety margin; the viewer must never see the face or an empty plate between them.
5. **No graphic starts or ends next to a face jump cut by a few frames.** A graphic that starts 1 to 8 frames after a face cut snaps back to that cut. A graphic that ends 1 to 8 frames before a face cut extends to it. The blur must never straddle a cut.
6. **No opening on empty paper.** The main element (not only the small heading) is fully in on the first frame of the graphic; its entrance runs before the cut, and its arrival sound moves to the cut.
7. **No sweep or flare overuse.** Light sweeps are limited to 2 in a video (see `ae-motion-design-principles`).
8. **No whoosh at the end of a spoken word.** If the profile bans a sound, never use it. Choose a softer sound or none (`ae-sound-effects-placement`).
9. **One transition style per video** for a given kind of seam. Do not mix three blurs.

## Blur into a graphic: exact recipe

Timeline for a cut at frame `C` (the first frame of the graphic):

| Frames | What happens |
|---|---|
| `C - 8` to `C - 1` | The face layer blurs from 0 to about 12 px with an ease in (`0.6, 0, 0.9, 0.35`) |
| `C` | Cut: the graphic is fully opaque, blurred at the starting amount (8 to 12 px) |
| `C` to `C + 7` | The graphic sharpens from 8 to 12 px to 0 with an ease out (`0.16, 1, 0.3, 1`) |
| `C + 8` on | Normal graphic entrances for inner elements (staggered per `ae-word-synced-graphics`) |

Check: the total length of the blur window is 8 + 8 = 16 frames (about 0.53 s). Shorter (about 5 frames) is acceptable for fast styles: the Agent Editor's built in `blur_in` effect is a short blur of about 0.16 s (roughly 5 frames). Use that for simple edits and the longer recipe for custom graphics.

As a pure function:

```ts
const into = prog(frame, C - 8, C, easeIn);          // face blur 0..1
const out  = prog(frame, C, C + 8, easeOut);          // graphic blur 1..0 mapped below
const faceBlurPx    = frame < C ? 12 * into : 0;
const graphicBlurPx = frame >= C ? 12 * (1 - out) : 12;   // the graphic is hidden before C
```

(`prog`, `easeIn`, `easeOut` are in `ae-motion-design-principles/references/pure-function-helpers.md`.)

With ffmpeg, a blur on a time window can be done with a `gblur` or `boxblur` filter and `enable='between(t,a,b)'`; for a ramp, render the blur amount per frame from a function (an expression with `t` works in some filters, but support varies by filter and version, so test on a short clip and look at the result).

## Exits and straight cuts

- Graphic to face: cut on the frame after the last held frame of the graphic. Cut on a spoken beat (the start of a word or just after a stop), never mid word.
- The cut lands within 3 frames of the spoken pause or word start it belongs to (`ae-pacing-and-rhythm`).
- If the face needs a small scale difference to avoid a jump look at a face to face cut, use a punch zoom (below) instead of a dissolve.
- Never use a dissolve between two shots of the same person; it reads as a mistake.

## Punch zooms (the small move on the face)

A punch zoom crops into the face a little and holds. Two styles:

| Style | Scale | In | Hold | Out | Use |
|---|---|---|---|---|---|
| Quick punch (short form) | 1.08 to 1.12 | 4 to 6 frames | at least 45 frames | hard cut or 6 frames | emphasis on a key phrase; the Agent Editor's `punch_zoom` crops in about 12 percent |
| Slow push (long form or calm style) | 1.18 to 1.22 | 24 frames ease in out `(0.65, 0, 0.35, 1)` | at least 45 frames | 24 frames ease in out | a reveal or a serious line |

Rules:
- Anchor the zoom on the eyes so the face does not drift.
- No new zoom without a reason: use them only on key lines marked in the script (the user's emphasis words) and at most one every 3 to 4 seconds.
- Sample the curve on every frame (never linear, never an instant jump unless it is the quick punch).
- Return to exactly scale 1.0 and the original position at the end so the next shot starts clean.
- The face is never cropped so that the eyes, mouth or chin leave the safe area (`ae-phone-safe-zones-and-formats`).

## Seam checks (do these every time)

1. List every seam: face to graphic, graphic to face, graphic to graphic, jump cut with a zoom change, music or sound transitions.
2. For each seam at frame `S`, take stills at `S-3`, `S-1`, `S`, `S+1`, `S+3`, `S+8` and look at them. On a contact strip, tiles are labelled with frame numbers.
3. Classify each still: face, graphic or mixed. A mixed frame that is not a designed blur is a defect. A rough classifier (the graphic plate is flat and low saturation; the face has skin tone and higher saturation) can flag candidates, but **the eye decides**. Do not move clips on a classifier guess alone; tune the classifier from what you saw.
4. Check the last 15 frames of every clip (nothing mid travel, no half typed text) and the first 15 frames of the next (is the main element in?).
5. Check the speech: no clipped word, no sliver of a removed word, no air blast at the join (`ae-precise-audio-cut`).
6. Check every graphic start and end against the nearest face cut (rule 5).
7. Count gaps: any face sliver between two graphics shorter than 36 frames is fixed (rule 2).

Write the result as a seam table in the edit log: seam, frame, kind, stills looked at (yes), classification, status. Never report a seam as clean without having looked at the stills.

## Audio at seams

- Sound sits 2 to 6 frames **before** the visual cut it belongs to (a soft pop or riser end). One sound per seam at most.
- Do not stack a riser, a whoosh and a pop on one seam.
- Dialogue audio is never faded at a visual seam unless a pause is designed; use the 12 ms join fade from `ae-precise-audio-cut` only.
- Music ducking and swells belong to `ae-music-bed-and-mixing`, not to transitions.

## Questions to ask the user

1. Transition personality: (a) hard cuts only, (b) blur into graphics only (recommended), (c) blur plus occasional punch zooms, (d) as many effects as fit the style.
2. Punch zooms: (a) none, (b) only on key lines I mark, (c) on key lines plus about every 4 seconds of long talking.
3. Sweeps or light flares: (a) none, (b) up to 2 per video, (c) my choice per video.
4. Transition sounds: (a) none, (b) soft pops only, (c) soft pops and risers at section starts.
5. When a graphic is on screen, should the face be completely hidden or can part of it remain? (full frame graphics follow this skill; ask only if the layout uses split panels).

Store answers through `ae-profile-schema`.

## Worked example (synthetic)

A bakery video: face from 0 to 6.8 s, then a three item list graphic from 6.8 s to 12.0 s, then the face again. At 30 fps the graphic cut `C = 204`. The face blur runs frames 196 to 203 (0 to 12 px, ease in). At frame 204 the graphic is opaque with 12 px blur and sharpens by frame 211. A soft pop plays at frame 200. Item 1 lands on its word at frame 232. The graphic holds through frame 359 (11.97 s) and the next face frame is 360: straight cut, no fade. A face jump cut exists at frame 207 (3 frames after `C`), so rule 5 says the graphic starts at the jump cut: set `C = 207`, the blur window becomes 199 to 206, the sound moves to frame 203. Seam still sheet at frames 203, 205, 206, 207, 208, 210, 215 is checked: no face under the graphic, no mixed frame after 207.

## Failure modes

- Fade out of a graphic showing the face through it.
- A blur at every seam.
- A graphic that starts 2 frames after a jump cut, so the blur straddles the cut.
- A face sliver of 12 frames between two graphics.
- Ghost double head from a matte reused across a cut.
- A graphic opening on an empty plate with its main element arriving 4 frames later.
- Zoom drifting off the eyes; zoom not returning to 1.0.
- A whoosh landing on the last syllable of a word.
- Believing a classifier instead of the stills.

## Checklist

- [ ] Policy table applied; blur only face to graphic
- [ ] No opacity fades on full frame graphics
- [ ] Blur recipe: 8 frames face blur, cut, 6 to 8 frames sharpen (or the short built in blur_in)
- [ ] Graphic starts and ends snapped to nearby face cuts
- [ ] No face sliver under 36 frames between graphics
- [ ] Punch zooms on key lines only, eased, returning to 1.0
- [ ] Seam table written with stills actually looked at
- [ ] Last 15 and first 15 frames of every clip checked
- [ ] Seam sounds 2 to 6 frames early, one per seam, banned sounds avoided

## Hand off to

`ae-motion-design-principles`, `ae-word-synced-graphics`, `ae-agent-fx`, `ae-agent-graphics`, `ae-precise-audio-cut`, `ae-pacing-and-rhythm`, `ae-sound-effects-placement`, `ae-phone-safe-zones-and-formats`, `ae-edit-qa-gates`.
