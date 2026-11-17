---
name: ae-pacing-and-rhythm
description: Sets and checks the pace of an edit, meaning cut density, breath room, graphic and effect cadence, delivery speed and the shape of attention from the first second to the last. Use when the user says "it feels slow", "it feels rushed", "too many cuts", "too much talking head", "tighten the pauses", "how fast should this be", or before the review of any edit.
---

# ae-pacing-and-rhythm

Pace is the number of things that change per second, and how evenly. It is not speed alone. A fast edit with no
variation tires the viewer; a slow edit with no change loses them. This skill gives numbers to measure, ranges to aim
for, and a repair order when the numbers are off.

## 0. Read the profile first

Read `brand/profile.md`. If it is missing or a section it needs is empty, stop and run `ae-setup-interview` for that
section (ask the user, with options), do not guess. This skill needs:

- `## Script preferences` (target length, tone, how dense the delivery is).
- `## Platforms and formats` (vertical short, square, landscape long form; the platform changes the target pace).
- `## Voice and tone` (a calm teacher and a fast hype style need different breath room).
- `## Rules` (anything the user already said about pacing, for example "never speed up my voice").

If `## Script preferences` has no pace answer, ask these questions (show the options, the user may answer freely):

1. How should the finished video feel?
   a) Calm and clear, room to think. b) Brisk and friendly. c) Fast and dense. d) Mixed: fast hook, calmer middle.
2. How much silence between phrases is acceptable?
   a) Almost none (under 0.15 s). b) A natural breath (up to 0.25 s). c) Deliberate beats allowed (up to 0.5 s on
   key lines). d) Keep my natural pauses.
3. May the agents change playback speed of the speech?
   a) Never. b) Up to 3 percent. c) Up to 6 percent. d) Ask me each time.
4. Is the visual rhythm allowed to be busy?
   a) Quiet: few effects, graphics only for numbers. b) Moderate. c) Busy: something moves every few seconds.

Write the answers into `## Script preferences` with `ae-profile-schema` rules, then continue.

## 1. The four layers of pace

Treat these as four separate dials. Fix them in this order, because each one changes the next.

1. **Speech density**: how many words per second of kept speech, and how much silence sits between phrases.
2. **Cut rhythm**: how often the picture jumps (jump cuts between kept phrases, punch zooms).
3. **Graphic cadence**: how often a new graphic, number or highlight arrives.
4. **Sound cadence**: how often a sound lands (see `ae-sound-effects-placement`) and the music bed level.

The thing the viewer feels is the sum of the four, so never raise one dial to hide a problem in another.

## 2. Starting values (approximate, tune on the real video)

These are typical starting points for a single speaker talking to camera. They are not laws. Judge by looking and
listening, and tell the user which ones you used.

| Measure | Short vertical (15 to 60 s) | Mid form (1 to 3 min) | Long form (8 min and up) |
| --- | --- | --- | --- |
| Words per second of kept speech | 2.6 to 3.3 | 2.4 to 3.0 | 2.2 to 2.8 |
| Longest silence left between phrases | 0.15 to 0.25 s | 0.2 to 0.35 s | 0.25 to 0.5 s |
| Designed beat after a key line | up to 0.5 s, at most 2 in the video | up to 0.6 s | up to 0.8 s |
| Jump cuts per 10 s of output | 2 to 5 | 1.5 to 4 | 1 to 3 |
| Longest unchanged picture (no cut, zoom, graphic) | 4 s | 6 s | 10 s |
| New graphic or on screen event per 10 s | 1.5 to 3 | 1 to 2 | 0.5 to 1.5 |
| Punch zooms | one per 6 to 10 s, never closer than 4 s | one per 10 to 15 s | sparing, on turns only |

The Agent Editor server enforces a few of these for you: a cut is at least 0.4 s, two punch zooms are at least 4 s
apart, graphics are 1.5 to 4 s long, closer than 0.5 s to another graphic is refused, and at most 10 graphics are
accepted. The rest is your judgment.

## 3. Measure first

Never judge pace by feel alone. Compute it. After the cutters finish, run this against the project file (it only reads
`project/ingest.json` and the state returned by `/api/state`):

```python
import json, urllib.request
ing = json.load(open("project/ingest.json"))
st = json.load(urllib.request.urlopen("http://127.0.0.1:8780/api/state"))
cuts = sorted([c for c in st["cuts"] if c["status"] == "ok"], key=lambda c: c["start"])
kept = sum(c["end"] - c["start"] for c in cuts)
words = [w for w in ing["words"] if any(c["start"] <= w["t"] < c["end"] for c in cuts)]
print("kept seconds", round(kept, 1), "words", len(words), "words/s", round(len(words) / kept, 2))
gaps = [round(b["start"] - a["end"], 2) for a, b in zip(cuts, cuts[1:])]
print("cuts", len(cuts), "cuts per 10 s", round(len(cuts) / kept * 10, 1))
fx = [f for f in st["fx"] if f["status"] == "ok"]
gr = [g for g in st["graphics"] if g["status"] == "ok"]
print("punch zooms", sum(f["type"] == "punch_zoom" for f in fx), "graphics", len(gr))
```

Confirm the state field names against `GET /api/state` on the user's copy before relying on the script, because a
newer server may rename them. If a name differs, print the JSON once and adapt.

Then build an "events per 10 second window" table: for each 10 s window of the OUTPUT timeline (not the source), count
jump cuts, graphics, zooms and sounds. Windows with zero events are dead stretches. Windows with more than about 8
events are crowded.

## 4. The retention shape

Aim for this shape on a short vertical video. For other lengths scale the seconds proportionally.

1. **Seconds 0 to 3, the hook**: speech starts on the first frame or within 0.3 s. Something visual is already
   present (a sharp anchor: the speaker, a real number, a real page). No logo, no title card, no breath in.
2. **Seconds 3 to 8, the promise made specific**: the highest density of the video. One graphic or zoom is fine here.
3. **Middle, the proof and points**: steady cadence, one change every 2 to 4 s, each change on a spoken word.
   Vary the type of change: do not use five punch zooms in a row, alternate zoom, graphic, plain cut.
4. **Ninety percent mark, the payoff**: a deliberate breath (0.3 to 0.5 s) before the biggest line is allowed, once.
5. **Last 3 to 5 s, the ending**: one clear action in words. No new idea. Let the last word finish; leave 0.3 to 0.6 s
   of room before the end so the file does not cut the final syllable.

Hold density roughly flat across the middle. The common failure is a dense first half and an empty second half.

## 5. Breath room: what to keep, what to remove

The cutter removes silence, but not all silence is waste. Use these rules when judging the cut.

- Remove: a pause longer than the limit in the table, a breath into the first word of a phrase, a "thinking" gap.
- Keep: the short gap after a claim so the claim can land; the beat before a reveal; the natural gap after a
  question the viewer is meant to answer in their head.
- A joined phrase that was spoken in one breath must stay in one piece. Cutting inside it makes the speaker sound
  clipped. If the transcript shows two words touching (gap under 0.05 s), do not cut between them.
- If every gap is trimmed to the same length the speech sounds mechanical. Let gap lengths vary by 0.05 to 0.1 s
  where the original varied, especially at sentence ends versus mid sentence.

## 6. Delivery speed

- Do not change the speed of the voice unless the profile allows it. If allowed, 3 to 6 percent is rarely noticed;
  more than that changes pitch and sounds hurried. Use ffmpeg `atempo=1.04` on audio and `setpts=PTS/1.04` on video
  together, never one without the other. The built in render does not change speed, so this is a manual step on the
  source before ingest, and it needs the user's yes.
- If the speaker is slow, prefer tighter cuts over speeding the voice.
- If the speaker is already fast, add breath room at the key lines rather than removing more words.

## 7. Repair order when pace is wrong

If it feels too slow:
1. Check dead stretches (windows with no event). Add a graphic or a zoom ON an existing spoken word there.
2. Tighten gaps over the limit. Re run the words per second measure.
3. Remove repeated ideas with the script owner's approval (see `ae-script-first-workflow`). Never cut words from the
   user's script without their yes.
4. Only then consider more effects. Effects do not fix a slow idea.

If it feels too rushed or tiring:
1. Count events per 10 s. Remove the weakest third of effects (the ones not tied to a number or a claim).
2. Restore the natural breath after the main claim and before the payoff.
3. Replace two adjacent zooms with one zoom and one plain cut.
4. Lengthen reading holds on graphics to at least 1 s plus 0.25 s per word beyond three.

## 8. Worked example

A local bakery explaining sourdough. 30 s target, vertical, brisk.

- Raw take: 52 s with fillers and restarts.
- After the cut: 31.4 s kept, 93 words, 2.96 words per second. In range for a short.
- Cuts: 14 in 31.4 s, which is 4.5 per 10 s, at the top of the range. Two cuts are between words that touch, so merge
  them. Now 12 cuts, 3.8 per 10 s.
- Event table: window 10 to 20 s has 0 events, window 0 to 10 s has 9. The graphic agent moves a stat card
  ("48 hours") from 4 s to 13 s, onto the word "hours". Window counts become 6 and 4.
- Silence check: three gaps of 0.31 s remain after sentence ends. The user chose "natural breath up to 0.25 s", so
  the cutters tighten them to 0.22 s.
- Result reported honestly: "Words per second 2.96, 12 cuts, graphics at 3.2 s, 13 s and 24 s, zooms at 9 s and 21 s.
  I checked stills at every event. I did not listen to the audio, you should."

## 9. Failure modes

- Fixing pace by speeding up everything: raises words per second but flattens emphasis. Do not.
- Adding effects to a dead stretch without tying them to a word: the effect looks random. Tie each to a spoken word.
- Measuring on the source timeline instead of the output timeline: kept cuts move everything earlier.
- Treating the table as a law: a calm explainer can sit below the ranges and be right. Ask the user.
- Cutting the last syllable by ending the video on the last word's end: leave a short tail.

## 10. Checklist

- [ ] Profile read, pace answers recorded.
- [ ] Words per second, cuts per 10 s, longest silence and longest unchanged picture measured on the OUTPUT timeline.
- [ ] No window of 10 s without an event (for short form), none above about 8 events.
- [ ] Punch zooms at least 4 s apart, varied with graphics and plain cuts.
- [ ] Hook starts within 0.3 s with a real picture on the first frame.
- [ ] Natural breath kept at the main claim and before the payoff, once.
- [ ] Ending has a 0.3 to 0.6 s tail.
- [ ] Any speed change was allowed by the profile and applied to audio and video together.
- [ ] Report lists what was measured, what was looked at, and what was not heard.

Hand off to: `ae-agent-cutter`, `ae-agent-fx`, `ae-agent-graphics`, `ae-edit-qa-gates`, `ae-sound-effects-placement`.
