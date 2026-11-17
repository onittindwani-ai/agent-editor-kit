---
name: ae-filler-and-restart-removal
description: Finds and removes filler sounds, filler words, false starts, restarts, doubled words, stumbles and breaths from talking footage using the transcript plus the audio, with rules for what to keep. Use when the user says "remove the ums", "cut the fumbles", "clean up the restarts", "I repeated myself", "take out the false starts", or when a cutter agent needs to know what to leave out of a window.
---

# Filler and restart removal

Read `brand/profile.md`. If it is missing or a section this skill needs is empty, stop and run `ae-setup-interview` for that section (ask the user, with options), do not guess.

Sections used here: `## Voice and tone` (casual speakers often want some "you know" kept), `## Rules` (words or phrases that must stay), `## Script preferences` (the approved script: its words are never removed as fillers).

The editor can only keep ranges of the source. Removing something means leaving it out of the kept cuts, so every removal is a pair of cut edges around it. This skill decides what to remove and what to keep. The exact placement of the edges is `ae-precise-audio-cut`. The role that sends the cuts is `ae-agent-cutter`.

## Questions to ask the user

1. How strict should the clean up be?
   a) Strict: remove every filler sound and every filler word that is not carrying meaning.
   b) Standard: remove filler sounds (um, uh, er) and stalling words, keep spoken style words (you know, I mean) when they sound natural.
   c) Light: remove only filler sounds and obvious restarts.
   d) Keep everything except long pauses and mistakes.
2. When a sentence is said twice, which one stays?
   a) The last complete one (default). b) The best delivered one (I will compare). c) Ask me each time.
3. Should breaths between sentences stay?
   a) Remove those in removed gaps. b) Keep a short breath (up to 0.15 s) before a new sentence. c) No preference.
4. Are there repeated words that are on purpose (emphasis, a list, a joke)?
   a) No. b) Yes, I will mark them. c) Treat anything in my approved script as intentional.

Default: standard, last complete one, remove breaths in removed gaps, anything in the approved script is intentional.

## What counts as what

| Kind | Examples | Default action |
| --- | --- | --- |
| Filler sound | um, uh, er, ah, hmm | Remove (all levels except "keep everything") |
| Filler word | like, so, basically, actually, literally, right, okay, well, anyway, you know, I mean, kind of, sort of | Remove only when it carries no meaning. Read the words around it first |
| False start | "So we, so we need to...", a sentence that is abandoned and begun again | Remove the abandoned part, keep the last complete version |
| Restart | The same sentence or phrase said again after a mistake | Keep the last complete one (or the one the user picked) |
| Stumble | A broken word ("wh-", "th-"), a repeated syllable | Remove the broken part. Keep the word if it is completed cleanly right after |
| Double | "the the", "to to", a phrase said twice in a row | Keep one |
| Self correction | "it takes four, I mean five minutes" | Keep the corrected version and check the fact against the script |
| Breath | Quiet broadband noise before a phrase | Remove in a removed gap; keep a short one if the user chose to |
| Mouth noise, throat clear, click | Short sounds between words | Remove when they sit in a gap; if they sit inside a phrase, flag for `ae-audio-cleanup` |
| Laugh, natural reaction | A short laugh the speaker did not intend to cut | Keep unless the user says otherwise |

## What must never be removed

1. Any word or phrase in the approved script (a repeat that is in the script is deliberate).
2. A word that changes meaning: negations ("not", "never", "no"), numbers, names, the verb "like" ("I like it"), the comparison "like" ("looks like a loaf"), "so" as a result ("so we fed it"), "right" as an answer or a direction.
3. A word that the next sentence refers back to ("that", "it", "this" pointing at what you remove). Check the first words after the removal.
4. Anything the user's `## Rules` protect.

## How to find them (the transcript misses things)

Speech to text models of the whisper family often leave out filler sounds and stutters. The transcript can look clean while the audio is full of "um". So use both sources.

1. Run the detector in `references/detect-disfluencies.md` on `project/ingest.json` and `project/a.wav`. It lists candidates by kind with times. It is read only.
2. For each candidate, read 5 words before and 5 after in the transcript before deciding.
3. For `untranscribed` sounds (voiced sound in a gap with no word), locate the real edges with `snap_edges.py --at T` from `ae-precise-audio-cut`. A filler vowel usually shows as a steady level within 15 dB of the speech level for 0.15 to 0.40 s. A breath shows as low level noise (4 to 12 dB above the floor) for 0.20 to 0.60 s, with no steady tone.
4. For doubles, test whether the transcript is wrong: two level bursts with a dip of 40 ms or more between them means the word really was said twice; one burst means the model wrote it twice, or merged two words into one longer word (a word longer than 0.5 s that should be short is a hint).
5. For restarts, the detector marks opening phrases repeated within 14 words. Confirm by reading both versions and comparing delivery: the last one is usually cleaner, but check (question 2).
6. For whole sentence retakes (the speaker stops, says "sorry" or "let me start again", and delivers the line again), find them by repeated sentences with similarity above about 0.7 on normalised words, or by the self correction markers.

## Removal as cuts

The server's minimum kept cut is 0.4 s. That sets how you remove things.

1. Each kept piece between two removals must be at least 0.4 s long. If removing a filler would leave a piece under 0.4 s, you have three options, in this order: (a) keep the filler if it is a short sound and removal is not worth a gap in the cut list; (b) also remove the tiny piece if it is itself a fragment (a leftover "and", a broken word); (c) join it into a longer neighbour by keeping everything between, and accept the filler.
2. Keep the last clean version of a repeated phrase: the kept cut starts at the start of the final version, so the abandoned first part is outside every kept cut.
3. A single cut can contain a short filler and nothing else odd. Prefer removing the filler to keeping a joined cut that rambles.
4. Edge placement and gap sizes come from `ae-precise-audio-cut`. After a removal the silence left at the join should match the user's tightness (typically 0.08 to 0.18 s).
5. Do removals before captions. Captions placed on removed words become `orphan_caption` problems in the editor's review. In a multi agent run the conductor orders cutters first (`ae-run-multi-agent-edit`).
6. Windows of different cutters meet at boundaries. A restart that begins in one window and ends in another belongs to the cutter whose window holds the start. The conductor places boundaries in silences; if yours is not, tell the conductor.

You cannot withdraw a cut. Plan the whole window first, then send the cuts one at a time.

## Procedure for a window

1. Read the window: `curl -s 'http://127.0.0.1:8780/api/window?start=0&end=33'`.
2. Run the detector and list candidates inside your window.
3. Build the keep list: for each sentence, decide the kept words (those in the final clean version). Write it as plain text: kept words, removed words, reason.
4. Check the keep list against the approved script: every script word is present once, in order, with the user's repeats intact.
5. Convert the keep list into ranges with edges from `ae-precise-audio-cut`.
6. Send the cuts one at a time. Claim the sentence before each (`{"op":"claim","agent":"W01","kind":"sentence","id":4,"status":"cleaning restart"}`).
7. Read the kept words as continuous text (concatenate the words of your cuts). Fix anything that reads wrong with a note to the reviewer or the conductor. No repeated adjacent word, no dangling "and" or "so", no fragment.
8. Run the join rehearsal (`ae-precise-audio-cut`) and compare. `done` with a short summary.

## Worked example (neutral placeholder content)

A local bakery owner explains reviving a sourdough starter. The user chose standard strictness, last complete version, remove breaths in gaps. Transcript (source seconds):

```
0.50 So   0.90 we   1.40 the   1.75 the   2.20 starter,   (um at 2.75 to 3.10, not in the transcript)
3.40 So   3.80 we   4.10 feed   4.50 it   4.80 wh-   5.00 twice   5.40 a   5.70 day.
```

The detector prints:

```
0.50 restart       'So we the the starter,'   the opening 'so we' is said again at 3.40
1.40 double        'the the'
2.53 untranscribed '(sound)'                  0.34 s of voiced sound somewhere in this gap with no word
4.80 cutoff        'wh-'
```

Reading: the first sentence "So we the the starter," is abandoned. The second "So we feed it ... twice a day." is the complete version. The "um" at 2.75 to 3.10 sits between them and goes with the abandoned part. "wh-" at 4.80 is a broken word before "twice": remove it. The word "So" at 3.40 is a result connector: keep (it joins to "we feed it").

Keep list: from 3.40 "So we feed it" (3.40 to 4.62), skip "wh-" (4.80 to 4.98), keep "twice a day." (5.00 to 6.00). Removed: 0.50 to 3.30 entirely (the false start, the double, the um), and the stumble. Kept pieces: 3.40 to 4.62 is 1.22 s, and 5.00 to 6.00 is 1.00 s, both over 0.4 s.

Edges (from the envelope, tight): cut 1 starts at 3.37 (onset of "So" minus 0.03) and ends at 4.65 (tail of "it" plus 0.02), cut 2 starts at 4.95 and ends at 6.04. Silence left at the join: (4.65 minus 4.62) plus (5.00 minus 4.95) = 0.08 s, in the target. Report: "Removed 1 false start (0.50 to 3.30, includes a double and an um) and 1 stumble (wh-). Kept: So we feed it twice a day. Script match: all script words present once."

If the script contains "the the" on purpose (a joke), the double would have been kept.

## Keep or remove: examples in context

Neutral lines from a bakery explainer. "Remove" means leave it out of the kept cuts.

| Line as spoken | Decision | Why |
| --- | --- | --- |
| "It is, um, a living thing" | Remove "um" | Filler sound |
| "It is like a pet you feed" | Keep "like" | A comparison, it carries meaning |
| "Like, you just feed it" | Remove "Like," (standard strictness) | A stalling opener, nothing depends on it |
| "I like how it smells" | Keep | The verb |
| "So we feed it, and so it wakes up" | Keep both "so" | Each introduces a result |
| "So, basically, you feed it" | Remove "basically" under strict, keep under light | A softener, not a meaning |
| "Feed it twice, I mean three times a day" | Remove "twice, I mean", keep "three times a day"; check the script says three | A self correction |
| "You need flour, flour and water" | Remove the first "flour" only if the script says "flour and water" | A stumble, check the script |
| "No, no, no, do not skip that" | Keep if the script has it, remove two "no" otherwise | Emphasis versus stutter: the script decides |
| "Right, so the next step" | Keep "Right," only if it answers or confirms something | Often a filler opener |
| "wh- why does it rise" | Remove "wh-" | A broken word |
| "(laugh) sorry, let me say that again" | Remove everything up to "again", keep the clean retake | A retake marker |

When the table does not decide it, ask the user once with a short example from their own footage, with options: keep, remove, always keep this word, always remove this word. Then record the answer as a rule for the rest of the edit (`ae-owner-notes-to-rules`).

## Report format for the conductor

Send this after your window, in under 80 words:

1. Counts: fillers removed, false starts removed, doubles removed, breaths removed, kept on purpose (with the reason).
2. Anything unresolved: pieces under 0.4 s that forced you to keep a filler, a retake you could not choose between, a sound inside a phrase that needs audio cleanup.
3. The cut ids and the windows covered.

## Failure modes

| Problem | What happens | Fix |
| --- | --- | --- |
| A real "like" or "so" is removed | Meaning changes | Read context; "never remove" list above |
| An intentional repeat is removed | The user's emphasis is lost | Compare with the approved script and the user's question 4 |
| The first half of a restart stays | A fragment is audible before the sentence | Start the kept cut at the final version's first onset |
| The transcript has "the the" but the audio has one burst | The model duplicated it | Do nothing (it is not in the audio). Tell the user the transcript has an error |
| A tiny piece (under 0.4 s) between two removals | The server refuses it | See "Removal as cuts" options |
| A filler sound inside a phrase (gap under 0.25 s) | Cutting it leaves a hard join | Leave it, or use `ae-audio-cleanup`. Note it |
| A breath cut leaves a tight join that sounds unnatural | The speaker never breathes | Keep up to 0.15 s of breath before a new sentence if the user wants |
| Facts after a self correction | "four, I mean five": the kept number must match the script | Check the script and `## Claims policy` |

## Checklist

- [ ] Profile read; the four questions answered or defaulted.
- [ ] Detector run on the transcript and the audio; `untranscribed` sounds looked at with the envelope.
- [ ] Every removal read in context; the never remove list respected.
- [ ] Keep list written and compared with the approved script.
- [ ] Every kept piece is 0.4 s or longer.
- [ ] Kept words read as continuous text without doubles, fragments or dangling connectors.
- [ ] Silence left at joins within the user's target.
- [ ] Join rehearsal run and compared.
- [ ] Facts after any self correction match the script.

## Do not

- Do not remove a word because it looks like a filler; read around it.
- Do not remove anything that is in the approved script.
- Do not trust the transcript alone: it hides fillers and may duplicate words.
- Do not send test cuts: a cut cannot be withdrawn by the cutter.
- Do not clean the audio itself here (noise, plosives): that is `ae-audio-cleanup`.

Hand off to: `ae-agent-cutter` (sends the cuts), `ae-precise-audio-cut` (edges and joins), `ae-audio-cleanup` (sounds that cannot be cut), `ae-agent-reviewer` (rejects leftover doubles and fragments), `ae-voice-capture` (how this speaker normally talks, what to keep), `ae-pacing-and-rhythm` (how tight the finished edit should feel), `ae-script-first-workflow` (the approved script is the reference), `ae-edit-qa-gates` (the final read through).
