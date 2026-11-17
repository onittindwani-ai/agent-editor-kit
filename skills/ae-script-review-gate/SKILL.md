---
name: ae-script-review-gate
description: A scored 10 point quality gate for any spoken script, plus a feedback extraction sheet that turns a reviewer's or the user's notes into reusable principles. Use before handing any script to the user for approval, after every rewrite, when the user says "rate this script", "is this ready", "review this", or pastes feedback from a friend, partner or voice note.
---

# Script review gate: score it, then extract the lessons

Read `brand/profile.md`. If it is missing or a section it needs is empty, stop and run `ae-setup-interview` for that section (ask the user, with options), do not guess. This skill needs `## Audience`, `## Offer and call to action`, `## Script preferences`, `## Platforms and formats` and `## Claims policy`.

## What this skill does

1. Runs a **line function test** so every line has a job.
2. Scores the script on **10 dimensions** from 1 to 10 with fixed anchors, and blocks the handoff when a critical dimension is weak.
3. Turns outside **feedback** (reviewer notes, voice notes, the user's own edits) into a table of principles, decisions and script changes, so the reasoning survives.
4. Records a **version comparison** so no one ever says only "this version is better".

The gate advises. It never replaces the user's decision, and it never edits text the user has hand edited (see `ae-voice-capture`). Suggestions go in the handoff as: old line, suggested line, reason, words saved.

## Step 0: preconditions

- The script exists as a file (not only in chat). Read it from disk in full this turn.
- A one sentence summary exists: "This video is about [event or problem], which matters to [audience] because [personal consequence], and the viewer will leave with [takeaway]." If you cannot write it, the script is not ready to score. Sharpen first with `ae-script-structure`.
- A claim ledger exists for every number, date, name and comparison (`ae-claims-and-truth-ledger`). Missing ledger caps Accuracy at 5.

## Step 1: the line function test

Label every line with exactly one job. Use this label set (add none without a reason):

| Label | The line's job |
|---|---|
| HOOK | Opens on the most compelling true event, result or contradiction |
| RELEVANCE | Ties the topic to the viewer's own situation |
| EVIDENCE | A fact, number, source or demonstration |
| MECHANISM | Explains how or why, in order |
| DEFINITION | Explains a term the moment it is first used |
| PRACTICAL NEED | What the viewer must do or know because of it |
| SOLUTION or REVEAL | Introduces the tool, method or answer |
| PROOF | Shows the answer works |
| CTA | The single action |
| TRANSITION | Joins two beats causally |

Rules:
- A line with no job is deleted or merged into a neighbour.
- A line that two labels both claim is probably two lines; split or keep the stronger job.
- A line kept "because it sounds dramatic" is deleted.
- TRANSITION lines must be causal ("because of that", "which means"), not filler ("here's the thing", "now it gets interesting"). Filler transitions are cut unless they earn their place by carrying a fact.
- Read the last sentence of each paragraph together with the first sentence of the next. The link must be a reason, not a gesture.

Write the map as a two column table in the review sheet (line number, label).

## Step 2: score the 10 dimensions

Score each 1 to 10. Use the anchors; do not round up to be kind.

| # | Dimension | 3 means | 6 means | 9 means |
|---|---|---|---|---|
| 1 | Hook clarity and impact | Opens with a greeting or setup | Clear but generic | The first 7 to 8 words carry the sharpest true part; the next sentence completes it |
| 2 | Audience relevance | Could be for anyone | Relevance stated late | The viewer sees themselves by the second beat, using a defensible link, not an invented statistic |
| 3 | Narrative continuity | Beats feel stacked | Mostly causal | Every beat follows from the previous one; no detour between promise and payoff |
| 4 | Factual accuracy | Unsourced numbers | Sourced, some wording stronger than the evidence | Every claim at or below its evidence class; hedges where needed |
| 5 | First listen comprehension | Needs a re read | Terms explained late | A stranger understands every sentence once, at speaking speed |
| 6 | Curiosity management | Many loops open at once | One loop, payoff late | One open loop at a time, each paid off exactly where promised |
| 7 | Differentiation | Sounds like every other script | One fresh angle | A specific angle or example only this user could give |
| 8 | CTA clarity | Several asks or vague ask | One ask, unclear reward | One sentence, one action, one promised outcome, deliverable as stated |
| 9 | Spoken naturalness | Reads like an article | Mostly speakable | Reads aloud with no stumble; joined sentences; the user's own voice rules applied |
| 10 | Runtime fit | Over the limit by more than 15 percent | Within 10 percent | Inside the range in the profile, computed from word count |

### Blocking rules

- **Dimension 4 (accuracy) or 5 (first listen comprehension) below 8 blocks the handoff.** A strong hook never compensates for a confused or doubtful story.
- Any dimension 1 to 3 blocks the handoff.
- An overall average is shown but never used to override a block.
- If the user has set stricter thresholds in `## Script preferences`, use those.

### Runtime math

Spoken pace is a profile setting. Typical ranges: about 2.3 to 2.6 words per second for calm teaching delivery, 2.6 to 3.0 for energetic delivery (150 to 180 words per minute). Compute: `seconds = words / pace`. Give runtime as a range (low pace to high pace). Count only spoken words; headings, bracketed pronunciation cues and stage notes do not count. If the profile has separate lengths per platform, compute each ending separately.

## Step 3: mechanical pre checks (run before you score)

1. Search for dash characters (em and en); replace with commas, periods or colons unless the user's own marks.
2. Numbers written the way the profile says (numerals or words) consistently.
3. Banned words and hype list from `ae-value-first-teaching-tone` and the profile `## Rules`.
4. Invented prevalence phrases ("most people", "everyone", "90 percent of") without a ledger row.
5. Terms used before they are explained.
6. More than one CTA, or a CTA that promises something not built.
7. The hook states the payoff the body reveals (hook paying itself off). The hook may raise the question only.
8. Dates: an event older than about 30 days is spoken with when it happened ("last December").

## Step 4: report format

```
SCRIPT REVIEW <script name>  <date>
Summary sentence: ...
Runtime: <low> to <high> seconds from <n> spoken words
Scores: 1 hook 8, 2 relevance 7, ... 10 runtime 9    Average 7.9
Blocks: none | <dimension and why>
Line map: (table)
Top 3 fixes: old line / suggested line / reason / words saved
What I did not change: lines the user has edited
```

Keep it under one screen. Do not paste the whole script back unless asked.

## Step 5: the feedback extraction sheet

When the user or a reviewer sends notes (typed, pasted, or a transcribed voice note):

1. List each actionable recommendation separately.
2. Separate the **principle** from the **example wording**. The reviewer's sample line is evidence of a concern, not a replacement.
3. Resolve contradictions against the actual script and the evidence.
4. Discard transcription noise. Numbers and product names from a noisy transcript are never facts; verify them with the ledger.
5. Fill the sheet:

| Where | Concern | Underlying principle | Decision | Script change |
|---|---|---|---|---|
| Hook | Too much setup | Lead with the consequence | Accept | Merge hook lines 1 and 2 |
| Middle | A second hook interrupts the explanation | Do not delay a promised answer | Accept | Remove the detour |
| Proof | Claim sounds too big | Match wording to evidence class | Accept | Soften the verb and cite the source |
| CTA | Too long | One sentence, last | Accept | One keyword sentence |
| Tone | Reads like docs | Write for the ear | Partly | Join sentences; keep the technical term |

6. Classify each concern so the real cause is fixed, not the symptom: hook strength, relevance, retention, narrative order, accuracy, proof, naturalness, differentiation, CTA friction, delivery.
7. Never paste a reviewer's wording over the user's words. Keep the principle, craft a line that is supportable, natural for this speaker and easy to hear once.
8. Hand every accepted principle to `ae-owner-notes-to-rules`.

## Step 6: the version comparison table

For every revision record:

| Previous line | Problem | Principle | New line | Trade off | Validation |
|---|---|---|---|---|---|
| "Row access control bypass" | Jargon used as suspense before it is explained | State the concrete failure first | "Anyone could read every user's messages" | Less technical, clearer | Read aloud test with a non expert |

Validation means a source check, a read aloud test or audience data, never "it feels better".

## Worked example (synthetic)

A local bakery explains why sourdough needs an overnight rest. Draft hook: "Hey everyone, today I want to talk about bread." Score 1 hook: 3 (greeting). Line map: line 1 has no job. Suggested hook: "Your sourdough is dense because you baked it four hours too early." Check: is "four hours" sourced from the baker's own test? If not, the hook becomes "Your sourdough is probably dense because the dough is not ready" and the claim stays hedged. Accuracy 6 until the ledger has the baker's real timing; the gate blocks, the agent asks the user for the timing rather than inventing it. After the fix: accuracy 9, comprehension 9 (the term "bulk fermentation" is explained in six words right after it), CTA one sentence ("Comment RECIPE and I send the schedule"), runtime 31 to 36 seconds from 88 words. The handoff lists three suggestions and says nothing was changed in the lines the user wrote.

## Failure modes

- Scoring generously to avoid conflict. Use the anchors.
- Scoring before the ledger exists.
- Treating reviewer wording as final. Extract the principle.
- Treating the average as the decision. Blocks win.
- Rewriting the user's lines in the review. Suggest, do not apply.
- Fixing symptoms: patching a line when the real issue is order.

## Checklist

- [ ] Script read from disk this turn; summary sentence written
- [ ] Ledger exists for every claim
- [ ] Line function map done; dead lines flagged
- [ ] Mechanical pre checks run
- [ ] 10 scores with anchors; blocks stated
- [ ] Runtime computed as a range
- [ ] Feedback sheet filled for any notes; principles handed on
- [ ] Version table updated; nothing the user wrote was changed

## Hand off to

`ae-hook-writing`, `ae-script-structure`, `ae-spoken-flow-and-plain-language`, `ae-value-first-teaching-tone`, `ae-claims-and-truth-ledger`, `ae-call-to-action-writing`, `ae-voice-capture`, `ae-owner-notes-to-rules`, `ae-script-first-workflow` (approval gate).
