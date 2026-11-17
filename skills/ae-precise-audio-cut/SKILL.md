---
name: ae-precise-audio-cut
description: Places cut edges from the waveform and the word times so no word is clipped, no gap is left, no word repeats, and no join clicks, then rehearses every join before rendering. Use when cuts sound clipped, pauses are left in, words are doubled, the user says "the cut sounds choppy", "a word is cut off", "tighten the gaps", or when a cutter agent needs exact edges.
---

# Precise audio cut

Read `brand/profile.md`. If it is missing or a section this skill needs is empty, stop and run `ae-setup-interview` for that section (ask the user, with options), do not guess.

Sections used here: `## Rules` (anything that must never be cut), `## Voice and tone` (how natural or punchy the delivery should feel), `## Script preferences` (pace).

The editor's only edit is a cut: a kept range of the source. Everything the viewer hears is decided by where each kept range starts and ends. This skill is the method for choosing those edges. It is used by cutter agents (`ae-agent-cutter`) and by anyone fixing a cut that sounds wrong.

## Questions to ask the user

1. How tight should the cuts be?
   a) Tight: every pause of 0.25 s or more removed, about 0.08 to 0.14 s of silence left at each join.
   b) Natural: pauses up to 0.30 s kept at sentence ends, joins up to 0.25 s.
   c) Breathing: only pauses over 0.50 s removed, designed pauses kept.
   d) Mixed: tight inside sentences, natural between sentences (default).
2. Should small breaths between phrases stay?
   a) Remove all that fall in a removed gap. b) Keep a short natural breath (up to 0.15 s) before a new sentence. c) No preference.
3. Are there places where a pause is deliberate (a pause before a reveal, a dramatic beat)?
   a) No. b) Yes, I will mark them (give times or words). c) Look for them in the script and ask me.

Default: tight inside sentences, natural between sentences, breaths removed.

## What the server decides, and what it does not

| The server | Consequence |
| --- | --- |
| A cut is at least 0.4 s, inside the source, and cannot overlap another kept cut | Short fragments cannot be cut on their own |
| A cut edge may not land inside a word, with a margin of 0.03 s: an edge up to 0.03 s after a word starts, or up to 0.03 s before it ends, is accepted | The server allows up to 30 ms of a word's start or ending to be clipped. Do not use that margin |
| The refusal text suggests two alternatives: `max(0, word start - 0.06)` or `word end + 0.04` | Those are computed from the offending word only. In a tight gap they can land inside the neighbouring word. Check them before using them |
| Word times are rounded to 0.01 s and come from a model | They are often off by 0.05 to 0.15 s at the start of a word after a pause and on short words. The waveform is the truth |

What the render does at each join (this decides your pad sizes):

- Audio of each kept cut is trimmed from the original, then faded in and out over 12 ms. Any voiced sound in the first or last 12 ms of a cut is attenuated. Edges must sit in silence, at least 20 ms away from voiced sound.
- The kept cuts are joined end to end, nothing is inserted. The silence the viewer hears at a join is the tail of one cut plus the head of the next.
- Picture is cut on 30 frames per second, so a picture edge can differ from the audio edge by up to 33 ms. Look at a few joins in a frame view before delivery.

## No take backs

A cutter cannot edit or delete its own cut. Only a reviewer can reject a cut, and only the person at the screen can remove one. A wrong edge stays on the timeline until one of them acts, and while it is live it blocks any overlapping replacement. So compute the edge first, check it, then send it. Do not send test cuts.

## Method: edges from the waveform

You need `project/a.wav` (16 kHz mono, made by the ingest) and `project/ingest.json`. The helper in `references/snap-edges.md` builds a 10 ms level envelope and suggests edges. A 16 kHz file shows everything up to 8 kHz, which covers onsets and most sibilants. For a doubtful join, extract that second from the original at 48 kHz and look again.

1. Measure the room: noise floor = the level that 10 percent of the frames are below. Speech level = the median of frames more than 15 dB above the floor. A clean recording has 40 to 50 dB between them. Under 25 dB, edges are hard to place and background noise needs cleaning first (`ae-audio-cleanup`).
2. For each removed stretch, name the last word to keep before it (A) and the first word to keep after it (B).
3. End edge for A: start at A's end time, find where the level falls to under 6 dB above the floor and stays there for 30 ms. That is the end of the tail. Put the cut end 0.02 s after it. Never closer than 0.03 s to B's start (or to whatever word follows A).
4. Start edge for B: look from 0.20 s before B's start time to 0.05 s after it, and find the first moment where the level rises 9 dB above the floor and stays up for 30 ms. That is the real onset. Put the cut start 0.03 s before it (0.05 s for hard starts: p, t, k, b, d, g), never earlier than A's end edge or the end of the previous word.
5. Silence left at the join = (A end edge minus A end time) plus (B start time minus B start edge). Compare with the user's tightness (question 1). Typical result: 0.04 + 0.06 = 0.10 s.
6. If the silence left is over the target, move the edges closer to the words, but never within 20 ms of voiced sound. If it is under the target (the words are almost touching), leave it: do not make a gap.
7. Send the cuts one at a time and read each answer.

Starting values: pad before an onset 0.03 s; pad after a tail 0.02 s; onset threshold 9 dB over the floor; tail threshold 6 dB over the floor; join silence target 0.08 to 0.18 s for tight cuts. They are approximate. Test them on one join and look at the envelope before using them everywhere.

## Cases that need care

| Case | What to do |
| --- | --- |
| Words touch (the gap between them is under 0.06 s) | There is no silence to cut in. Keep both words in the same cut |
| A removed word touches both neighbours ("so [um] we") | End the first cut at the first word's end and start the next at the second word's start, using the lowest level frame in each touching zone. Expect a hard join; check it in the rehearsal. If the level never drops, keep the filler |
| A word starts softly (f, s, th, h, a vowel) | Use a lower onset threshold (6 dB) and a pad of 0.04 s. Look at the envelope, not the transcript |
| A word ends in a release (t, k, p) or a long s | Add 0.04 s of pad to the tail and require a quiet frame after it |
| Breath before a new sentence | Level 4 to 12 dB over the floor for 0.20 to 0.60 s. If the user keeps breaths (question 2 b), start the cut up to 0.15 s before the word, otherwise start at the onset minus the pad |
| Plosive blast at the start of a kept cut | If the first 40 ms of a cut hold a short burst well above the following syllable, start the cut 0.02 s later, after the burst, or flag it for `ae-audio-cleanup` (a high pass filter) |
| Room tone changes between two cuts | A joint between two very different noise levels is audible. Prefer joining where both sides are equally quiet. Report it |
| Coarticulated words ("going to" said as "gonna") | The sound cannot be split. Keep it whole |

## No gaps, no repeats, no clipped words: the tests

Run these on every cut before sending it (the helper does the level tests):

1. Edge level test: the level at the first 10 ms of a cut and at the last 10 ms before its end must be under floor + 8 dB. Over that, the edge is inside voiced sound.
2. Gap test: the silence left at each join stays inside the user's target (0.35 s is the point where the editor's own review calls it a pause).
3. Repeat test: no word is kept twice in a row, and no 2 to 6 word phrase is kept twice within 14 words, unless the script says so. A repeated syllable inside one transcript word shows as two level bursts with a dip of 40 ms or more and a word duration longer than normal (over 0.5 s for a short word). See `ae-filler-and-restart-removal`.
4. Word survival test: every word the script needs survives. Count them in the rehearsal.
5. Onset test: the first kept word of a cut starts at least 0.02 s after the cut start, with level at floor level before it.

## Join rehearsal (audio only, before the render)

Do not wait for the render to learn that a join is wrong. `references/join-rehearsal.md` builds a command that joins the kept cuts exactly like the render does (12 ms fades) from `project/a.wav` into one scratch wav, with no video and no export. Transcribe that wav once (one heavy job at a time) and compare it with the expected words. The comparison prints each difference with its neighbours. A difference near a join is a clipped word, a doubled word or a missing word. Inspect it with `snap_edges.py --at`, then ask the reviewer to reject the faulty cut (the cutter cannot) and place a corrected cut.

This scratch file is not a deliverable and not an export, so it needs no green light (`ae-export-once-workflow`). Keep it out of the delivery folder.

## Worked example (neutral placeholder content)

A local bakery explains sourdough. Transcript: "dead," 2.10 to 2.50, then a pause, then "it" 3.05 to 3.15, "is" 3.15 to 3.28. The user chose tight cuts. Noise floor -69 dBFS, speech median -18 dBFS (a 51 dB gap, clean).

```
python3 snap_edges.py --a 6 --b 7
noise floor -69.6 dBFS, median speech level -17.7 dBFS
keep word 6 'dead,' (ends 2.5) -> cut END   2.580  (tail room +0.080 s, level there -66.9 dB)
keep word 7 'it' (starts 3.05)  -> cut START 3.010  (head room +0.040 s, level there -68.2 dB)
silence left at this join in the finished video: 0.120 s
```

0.12 s is inside the 0.08 to 0.18 s target. Send the edges:

```
curl -s -X POST http://127.0.0.1:8780/api/op -H 'Content-Type: application/json' -d '{"op":"cut","agent":"W01","start":0.34,"end":2.58,"note":"first sentence"}'
curl -s -X POST http://127.0.0.1:8780/api/op -H 'Content-Type: application/json' -d '{"op":"cut","agent":"W01","start":3.01,"end":4.26,"note":"it is just hungry"}'
```

A harder join: "so" 0.80 to 1.00, "um" 1.00 to 1.25, "we" 1.25 to 1.40, user wants the "um" gone. The words touch. Sending `end` 1.04 (the usual "word end plus 0.04") is refused: `cut end 1.04 lands inside the word 'um' (1.0-1.25); use 0.94 or 1.29`. Both suggestions are wrong here: 0.94 clips the end of "so", and 1.29 is inside "we". Use 1.00 (the end of "so") for the first cut end and 1.25 for the next cut start, after checking the envelope shows the lowest level of the touching zone at those times. The joint is hard, so mark it for the rehearsal. If the rehearsal transcript reads "so e" instead of "so we", the edge is clipping: keep the "um" and say so to the user.

## Reading the envelope (what the numbers look like)

`snap_edges.py --at 2.55` prints 13 frames of 10 ms around a time, with a bar per frame. A healthy end of a word looks like this (levels are examples):

```
    2.49   -24.8 dB  ######################
    2.50   -31.0 dB  ##################
    2.52   -42.3 dB  ############
    2.54   -55.6 dB  ######
    2.56   -66.1 dB  #
    2.58   -68.9 dB
    2.60   -69.2 dB
QUIET: an edge here will not clip a word
```

The level falls steadily into the floor. An edge at 2.58 is safe. A level that falls and then rises again (a second bump) is another sound, a breath or the start of the next word, and the edge must stay before it. A level that never falls (the words run together) means there is nothing to cut in.

## Speaker and room adjustments

| Situation | Adjust |
| --- | --- |
| Fast talker (over 3.4 words per second) | Gaps are short, so pads shrink: use 0.02 before onsets and 0.015 after tails, and accept 0.06 to 0.10 s of silence at joins |
| Slow, deliberate talker | Pads of 0.04 and 0.03 are fine; consider "natural" tightness so the pace is not rushed |
| Quiet speaker (median speech under -30 dBFS) | Lower the onset threshold to 6 dB and the tail threshold to 4 dB |
| Noisy room (floor above -50 dBFS) | The 6 and 9 dB thresholds fire on noise. Raise them by 4 dB, or clean the audio first (`ae-audio-cleanup`), and expect to inspect every join by eye |
| Hum or constant tone | The floor is high and flat. Edges are placed by the speech rise, not by silence. Tail pads of 0.04 |
| Music or other voices behind the speaker | Edge placement cannot find silence. Tell the user; cut at word boundaries and accept audible joins, or re record |
| A whispered or breathy ending | The tail is long and low. Use the tail threshold of 4 dB and a pad of 0.04 |

## Auditing a finished cut list (before the reviewer)

Read `/api/state` and print each kept cut with its first and last words and the silence on both sides. Then:

1. Sort by start time. The list must be in source order and must not overlap.
2. For each cut, head gap (first word start minus cut start) between 0.02 and 0.15 s, tail gap (cut end minus last word end) between 0.01 and 0.15 s. Outside that, look at it again.
3. For each join, head plus tail inside the target. Mark any over 0.35 s.
4. For each cut under 1.0 s, check it is a whole phrase (a one word cut is a sign of fragments or a missed restart).
5. Total kept length against the user's target length (`## Platforms and formats`).
6. Count joins: more than about one join per 2 seconds of finished video makes the speech feel choppy. Tell the conductor if the count is higher and the user chose "natural".

## Failure modes

| Symptom | Cause | Fix |
| --- | --- | --- |
| A word sounds cut off at its start | Edge inside the onset; word time was late | Move the start earlier by 0.03 to 0.05 s after checking the envelope |
| A word has a tiny dip or a click | An edge within 12 ms of voiced sound, or inside a word by the server margin | Move the edge into real silence |
| Odd extra syllable ("b" of a removed word) | The edge sits on the start of a removed word | Move the edge so the removed word is entirely outside |
| A pause the user did not want | Tail plus head is over target | Trim the cut edges closer to the words |
| A word repeated | A restart was kept in two cuts | See `ae-filler-and-restart-removal` |
| Picture and sound drift at a join | Picture is cut on a 30 fps grid | Check a few joins as frames, report the worst |
| The server says "inside the word" for an edge that looks fine | The transcript time is off | Trust the waveform, but the server decides acceptance, so choose an edge the server accepts that is also quiet |

## Checklist

- [ ] Profile read; tightness, breath and deliberate pause questions answered.
- [ ] Noise floor and speech level measured; gap between them recorded.
- [ ] Every edge at least 20 ms from voiced sound and at a level under floor + 8 dB.
- [ ] Silence left at every join is inside the target; none over 0.35 s.
- [ ] Touching words handled without clipping, or the filler kept.
- [ ] No word or phrase kept twice; script words all survive.
- [ ] Join rehearsal run, compared, differences resolved.
- [ ] No test cuts sent; every cut sent once.

## Do not

- Do not trust the transcript's word times over the waveform.
- Do not use the server's suggested numbers without checking the neighbours.
- Do not start or end a cut inside a word to save a few milliseconds.
- Do not add padding to make gaps: nothing is inserted at a join.
- Do not export a video to test a join. Use the audio rehearsal.

Hand off to: `ae-agent-cutter` (the role that sends the cuts), `ae-filler-and-restart-removal` (what to remove and keep), `ae-audio-cleanup` (noise, plosives, clicks), `ae-pacing-and-rhythm` (how tight the whole edit should feel), `ae-agent-reviewer` (rejects faulty cuts), `ae-edit-qa-gates` (the pre delivery table), `ae-loudness-mastering` (after the edit is final).
