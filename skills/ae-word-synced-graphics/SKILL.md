---
name: ae-word-synced-graphics
description: Build graphics whose every element lands on the spoken word, as a pure function of time keyed to word timestamps from the transcript, with sequential lookup, fuzzy matching, arrival tolerance, pacing, density and sound lead rules. Use when the user says "graphics are out of sync", "it appears before I say it", "too slow", "too empty", "make it pop as I speak", or whenever any graphic, list, chip, underline or counter must follow speech.
---

# Word synced graphics

Read `brand/profile.md`. If it is missing or a section it needs is empty, stop and run `ae-setup-interview` for that section (ask the user, with options), do not guess. This skill needs `## Visual theme`, `## Platforms and formats` and `## Sound`, and an approved script (`ae-script-first-workflow`): never build graphics before the user approves the words.

## The idea

A graphic is not a clip placed near the right time. It is a program that answers: given this frame, what should the screen show? Every element has its own start frame computed from the time the speaker says its word. When the cut or the words change, you re run the lookup and the graphic follows.

Prerequisites: `ae-motion-design-principles` (pure function of time, easing, lengths), word timestamps from the final cut transcript (`ae-ingest-and-transcribe`; the Agent Editor writes them to `project/ingest.json` as a `words` list of objects with `t` start seconds, `e` end seconds and `w` the word).

## Step 1: get word times from the cut that will be rendered

1. Word times must come from the **final cut audio**, not the raw take. If cuts changed, re transcribe or remap times through the cut list before anything else. Stale times are the most common reason for drift.
2. Check transcript quality first: read the words around each anchor. Fix spellings of names and brand words in the transcript (not in the user's script) so anchors match.
3. Save a trimmed copy for the graphic: `graphics/<id>/words.json` with only the words in that graphic's window, times shifted so the graphic starts at 0 s.

## Step 2: write the anchor spec

One entry per element that must arrive on speech. Use the script's words, in spoken order:

```json
{
  "graphic": "three-reasons",
  "window": [14.2, 24.6],
  "anchors": [
    { "id": "title",   "say": "three reasons",   "lead": 0.12 },
    { "id": "r1",      "say": "too cold",        "lead": 0.12 },
    { "id": "r2",      "say": "not enough salt", "lead": 0.12 },
    { "id": "r3",      "say": "rushed the rest", "lead": 0.12 },
    { "id": "fix",     "say": "overnight",       "lead": 0.12, "hold_min": 1.2 }
  ]
}
```

`say` is the first word or short phrase the viewer hears when the element should appear. `lead` is how many seconds before that word the entrance may start (see tolerance).

## Step 3: sequential lookup (never search the whole transcript)

For each anchor in order, search for its words **only after the end of the previous matched anchor**, and only inside the graphic's window. Never "find the first word that starts with X" across the whole file: a common word ("the", "so", "and") appears earlier and the element lands too soon.

Algorithm:

```python
import re
from difflib import SequenceMatcher

def norm(w): return re.sub(r"[^a-z0-9']", "", w.lower())

def similar(a, b, floor=0.8):
    a, b = norm(a), norm(b)
    return a == b or SequenceMatcher(None, a, b).ratio() >= floor

def locate(words, anchors, start_after=0.0):
    """words: [{'t':..,'e':..,'w':..}] in spoken order. Returns {anchor_id: seconds} or raises."""
    out, cursor = {}, start_after
    for a in anchors:
        target = a["say"].split()
        found = None
        for i, w in enumerate(words):
            if w["t"] < cursor - 1e-6:
                continue
            ok = all(i + k < len(words) and similar(words[i + k]["w"], target[k]) for k in range(len(target)))
            if ok:
                found = words[i]["t"]
                cursor = found      # the next anchor may share this word's time, never earlier
                break
        if found is None:
            raise ValueError(f"anchor {a['id']} not found after {cursor:.2f}s: fix the say text or the transcript")
        out[a["id"]] = found
    return out
```

Rules:
- Two anchors may share a frame (same word), but no anchor may land before an anchor that is spoken earlier.
- **Fuzzy matching**: normalise case and punctuation, accept a similarity of about 0.8 for brand names the transcriber spells differently, and write the transcript spelling into the anchor's `say` when it keeps failing.
- **Fallback**: if the exact phrase is missing, match the first word of the phrase; if even that fails, stop and tell the user. Do not guess a time, and never let an element appear seconds after its word because the match fell back to a later place. The earliest valid match after the cursor wins.
- An anchor not found is a blocker, reported with the nearest transcript words.

## Step 4: convert to frames and apply the arrival tolerance

`start_frame = round((word_time - lead) * fps)`. Starting value `lead = 0.12 s` (4 frames at 30 fps), allowed range 0 to 0.3 s (9 frames).

- The entrance may begin before the word so the thing is *there* as the word lands, but the **readable text must not be readable before the word**: while an element is arriving it is blurred (6 to 12 px) or small and unreadable, and it is sharp and legible only from the word onward.
- A graphic never lands after its word by more than 3 frames (0.1 s). Offsets bigger than 0.1 s are listed in the arrival table and fixed.
- Never use a spoken pause as the trigger. Anchor to a word.

## Step 5: density and pacing

1. **Something lands on almost every spoken phrase** (a word, a number, a chip, an underline, a mark, a move). No empty stretch while the speaker talks. A talking head only stretch while a graphic area exists is a fail.
2. **A new element every 15 to 45 frames** (0.5 to 1.5 s) while a graphic is on screen; none unchanged for more than 75 frames (2.5 s) except a final hold.
3. **A spoken list arrives one item at a time**, each on the start of the word that names it, never all at once and never three on one word.
4. **No late burst**: no arrival in the last 0.6 s (18 frames) of a graphic; no still stretch over 2.5 s followed by a pile of arrivals right before the cut. Spread arrivals across the spoken line.
5. **Hear what you see** (the 3 second rule): a graphic shows only what is being said now or was said at most 3 seconds ago. When a passage carries several ideas, split it into 2 to 5 second graphics, one idea each, straight cut to the next. A graphic longer than about 6 seconds must keep changing and drop what is no longer being said.
6. **Fill the frame**: headlines 64 to 140 px on a 1080 px wide canvas, content spread through the stage, centred stack. A third of the stage empty is a fail (respect the safe zones in `ae-phone-safe-zones-and-formats`).
7. **A graphic that only repeats the spoken words is a fail.** Turn words into the fitting element: a sequence of dated events becomes a timeline, the parts of a thing become a stack, a number becomes a counter (`ae-counters-and-numbers`), a source becomes a real page (`ae-proof-cards-and-real-screens`). Text is a short label, not the sentence.
8. **The graphic's text wins over the caption**: when a graphic already shows the words being spoken, the caption for exactly those words is hidden (a quiet window in `ae-caption-style-and-grouping`). Never the same words twice on screen.

## Step 6: typing and text entrances

- Typing is only for things that are really typed (a prompt, a command, a search box, a form), 12 to 16 characters per second (about 2 to 2.5 frames per character), started early enough to **finish 0.1 to 0.3 s before the spoken word**, centred and complete before the cut.
- Headlines, labels and card text do not type letter by letter. They arrive blur to sharp in 4 to 10 frames.
- A lead in phrase the speaker says ("Make sure you...") may type on as it is spoken, then the items arrive on their words.
- Never show a half word or an empty container at any swap.

## Step 7: sound lead

Place one soft recorded sound **2 to 6 frames (0.05 to 0.2 s) before** the visual entrance it belongs to. Put sounds on entrances, state changes of a persistent object and counter landings. Never on caption swaps. The same file is not reused within 75 frames (2.5 s). Generate the cue list from the same anchor file so picture and sound share one source of truth, then hand it to `ae-sound-effects-placement`.

## Step 8: the arrival table (required evidence)

After building, print this table into the edit log and read it:

| Element | Word | Word start (s) | Arrival frame | Offset (s) | Status |
|---|---|---|---|---|---|
| title | three | 14.60 | 438 | -0.07 | ok |
| r1 | too | 16.02 | 481 | -0.05 | ok |
| r3 | rushed | 20.50 | 619 | +0.03 | ok |

`Offset = arrival_time - word_start`. Allowed range: -0.30 to +0.10. Anything outside is fixed or explained. Also list every gap longer than 2.5 s with nothing arriving.

A small checker takes the anchor spec, the located times and the rendered timeline and prints the table plus violations (late arrivals, early readable text, arrivals in the last 0.6 s, still stretches, repeats). Write it in Python in the project's scripts folder; it only reads files.

## Step 9: re timing and re rendering

- A change to the cut or the words: re transcribe, re run `locate`, re render only the graphics whose anchor times changed. Keep a hash of each graphic's anchor times to know.
- A note such as "the second chip is late": check the table, change the anchor or `lead`, re render that graphic only, show a still at that frame.
- Never hand shift a layer on the timeline to fix a sync problem; fix the anchor so it stays fixed after the next re cut.

## Questions to ask the user (if the profile is silent)

1. Graphic density: (a) calm, one idea per graphic with space, (b) steady, a new element every second, (c) dense, an element on nearly every phrase.
2. When a graphic already shows the words, should the caption hide? (a) yes, always, (b) yes except for hook lines, (c) no, show both.
3. Entrance lead: (a) exactly on the word, (b) just before the word (recommended, about 0.12 s), (c) up to 0.3 s before for slow styles.
4. Should lists arrive one item per spoken item (recommended) or all together at the end?

## Worked example (synthetic)

A bakery explains "three mistakes with sourdough". The user says: "The first mistake is cold water, the second is too much flour, the third is rushing the rest."

Anchors: `title: "three mistakes"`, `m1: "cold water"`, `m2: "too much flour"`, `m3: "rushing"`. Word times (from the final cut): three 2.10, cold 3.35, too 5.20, rushing 7.60. At 30 fps with lead 0.12: title frame 59, m1 frame 97, m2 frame 152, m3 frame 224. The chips are blurred 10 px at those frames and sharp 8 frames later, so they are readable from just after their word. Sounds go at frames 54, 92, 147, 219. Table offsets are all -0.12 to -0.10 s, inside tolerance. Nothing arrives after frame 224 until the exit, and the graphic ends at 9.0 s (frame 270), more than 0.6 s after the last arrival, so no late burst. A still taken at frame 99 shows chip 1 sharp and the other two absent.

## Failure modes

- Searching the whole transcript for an anchor word; it lands early.
- Using raw take times after a re cut.
- A graphic that appears seconds after its word because a fuzzy match fell back to a later place.
- Three items arriving on one word.
- An element readable before its word.
- A burst of arrivals in the last 0.5 s.
- A hand shifted layer instead of a fixed anchor.

## Checklist

- [ ] Script approved; word times from the final cut
- [ ] Anchor spec in spoken order; sequential lookup used
- [ ] Every anchor found; fuzzy misses reported, not guessed
- [ ] Arrival table printed and read; offsets within -0.30 to +0.10 s
- [ ] Something lands on almost every phrase; no stretch over 2.5 s still
- [ ] No arrivals in the last 0.6 s; lists arrive one by one
- [ ] Typing finishes 0.1 to 0.3 s before the word
- [ ] Sound cues 2 to 6 frames before entrances; none repeated within 75 frames
- [ ] Stills looked at around each anchor

## Hand off to

`ae-motion-design-principles`, `ae-counters-and-numbers`, `ae-proof-cards-and-real-screens`, `ae-transitions-and-blur`, `ae-sound-effects-placement`, `ae-caption-style-and-grouping`, `ae-edit-qa-gates`, `ae-agent-graphics`.
