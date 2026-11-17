---
name: ae-script-structure
description: Beat sheets by length (30 to 35 second short, 60 second short, long form), word budgets, runtime math, open loops, one idea per beat and the line function test. Use when the user says "structure this script", "how long will it run", "it is too long", "cut it to 45 seconds", "outline the video", or when drafting any script.
---

# Script structure

Read `brand/profile.md`. If it is missing or a section this skill needs (`## Platforms and formats`, `## Script preferences`, `## Offer and call to action`, `## Audience`) is empty, stop and run `ae-setup-interview` for that section (ask the user, with options), do not guess.

## The goal

A script feels inevitable when each line answers the question the previous line created and opens the next useful one. Structure is how you get there. It is also how you hit a runtime without cutting the lines that make the script flow.

## Runtime math (do this before writing, and again after)

Speaking pace varies by person. Defaults, as starting values the user can correct:

| Context | Words per second | Words per minute |
| --- | --- | --- |
| Reading a teleprompter calmly | 2.5 to 2.8 | 150 to 170 |
| Natural conversational delivery | 2.7 to 3.0 | 160 to 180 |
| A hook delivered slightly faster | about 3.2 | about 190 |
| Slow, explanatory or emphatic | 2.0 to 2.4 | 120 to 145 |

Formula: seconds = words / words per second. Word budget = target seconds x words per second. Always give a range, not a single number: low = words / 3.0, high = words / 2.5.

| Target | Word budget (at 2.5 to 3.0) | Hard ceiling |
| --- | --- | --- |
| 30 s | 75 to 90 | 100 |
| 35 s | 88 to 105 | 115 |
| 45 s | 112 to 135 | 150 |
| 60 s | 150 to 180 | 195 |
| 90 s | 225 to 270 | 290 |
| 5 min | 750 to 900 | 950 |
| 10 min | 1500 to 1800 | 1900 |

Count only spoken words. Do not count labels, stage directions, pronunciation hints or link lines that are not spoken. Numerals count as the words spoken: "2,400" is "two thousand four hundred" (4 words). Ask the user their real pace after their first recording and recompute from then on (`ae-voice-capture`). Say "estimate" until a real recording exists. When the user hands you a take, measure the real words per second from the transcript and replace the default.

Pauses and designed beats add time. Add about 0.4 s for every deliberate pause the script marks and 0.7 s for each beat where the user shows something silently.

## Choosing a length

Ask the user (options): (a) 30 to 35 seconds, a one idea invitation; (b) 45 to 60 seconds, one idea plus proof; (c) 60 to 90 seconds, a short story or a list of 3; (d) long form of [N] minutes. Defaults come from the profile. Guidance: a short video sells the what and the why, not the how. Setup steps, extra features and details belong in the resource or a follow up, not in the short. Every word must earn its place; cut before adding. A short that runs past 60 seconds needs a reason the viewer will feel.

## Spine: pick exactly one

| Spine | Order | Use for |
| --- | --- | --- |
| Result then how | result, why it matters to you, the one key step, payoff, action | tool, method, tip |
| Problem then cause then fix | specific problem, why it happens, the fix, proof, action | troubleshooting |
| Event then meaning | what happened, why you should care, the mechanism, what to do, action | news |
| Contradiction | belief, why it is wrong, evidence, the better way, action | mindset, myth busting |
| List | promise, item 1, item 2, item 3, wrap, action | roundups (3 items best) |
| Story | situation, turn, consequence, lesson, action | the user's own experience |

Do not add a second spine, a secondary incident or an extra statistic unless it deepens the same idea and does not delay the promised answer.

## Beat sheet: 30 to 35 seconds (about 85 to 100 words)

| Beat | Seconds | Words | Job |
| --- | --- | --- | --- |
| Hook | 0 to 3 | 8 to 14 | Anchor, tension, gap (`ae-hook-writing`) |
| Open loop and proof | 3 to 8 | 14 to 20 | Make the gap matter to the viewer; show the real thing |
| Point 1 | 8 to 15 | 17 to 22 | One idea, value then name then ease (`ae-value-first-teaching-tone`) |
| Point 2 (optional) | 15 to 22 | 17 to 22 | Same shape |
| Payoff | 22 to 28 | 14 to 20 | Close the loop with the real answer |
| Action | 28 to 35 | 14 to 20 | One action (`ae-call-to-action-writing`) |

One or two points only. One idea per beat.

## Beat sheet: 60 seconds (about 150 to 175 words)

| Beat | Seconds | Words | Job |
| --- | --- | --- | --- |
| Hook | 0 to 4 | 10 to 14 | As above |
| Why it matters to you | 4 to 12 | 20 to 28 | Connect to the viewer with a defensible statement, no invented prevalence |
| Explain the key term | 12 to 18 | 15 to 22 | Define it in 3 to 4 plain words, then one sentence of use |
| Mechanism or steps | 18 to 40 | 55 to 70 | In chronological order, joined with connectors |
| Honest catch | 40 to 46 | 14 to 20 | What it cannot do or what the viewer still decides |
| Payoff | 46 to 54 | 18 to 25 | Close the loop |
| Action | 54 to 60 | 14 to 18 | One action |

## Beat sheet: 3 item list, 60 to 75 seconds

Promise line (10 to 14 words, names the three outcomes), three points of 22 to 30 words each opened with a spoken signpost (So, Then, And lastly), a one sentence wrap (14 to 20 words) and the action. Signposts belong to list scripts; story scripts use causal transitions instead (because, which means, so that).

## Beat sheet: long form (10 minutes, about 1500 to 1800 words)

| Section | Minutes | Words | Job |
| --- | --- | --- | --- |
| Opening stack | 0:00 to 0:40 | 100 to 125 | Hook plus 2 to 3 true intrigue lines, preview of what the viewer gets |
| Stakes and steer | 0:40 to 1:30 | 130 to 150 | One true stakes line, promise the payoff in THIS video |
| Section A | 1:30 to 4:00 | 380 to 450 | One idea, an example, a proof, a bridge |
| Section B | 4:00 to 6:30 | 380 to 450 | Same, with a new angle |
| Section C | 6:30 to 8:30 | 300 to 360 | Same, plus the honest limits |
| Wrap and takeaway | 8:30 to 9:20 | 130 to 160 | A new angle, not generic advice |
| Action and close | 9:20 to 10:00 | 90 to 120 | One action, a friendly sign off if the voice allows |

For 20 minutes, add sections of the same shape, keep a re hook every 3 to 4 minutes (a new question or a result to come), and keep the first payoff before minute 2.

Value part early: if the video has a news half and a value half, start the value half by about 30 percent of the runtime. Cut montage lines that repeat the opening.

## Open loops

An open loop is a question the viewer wants answered. Keep a loop table in `project/script/LOOPS.md`:

| Loop | Opened at | Closes at | Closed by (line) |
| --- | --- | --- | --- |
| Why does the smell happen? | hook | 22 s | payoff |

Rules: one loop is open at a time inside the body (between a promise and its payoff, do not insert a second hook). A long form opening may stack up to 3. Every loop closes at the same level of specificity it opened. A loop that never closes is a broken promise; remove it or pay it off.

## One idea per beat, one job per line

Label every line with its job: HOOK, RELEVANCE, EVIDENCE, DEFINITION, MECHANISM, STEP, CATCH, PAYOFF, ACTION. Then test: can the viewer follow the video if this line is removed? If yes, cut it. If the line has two jobs, split it or drop the weaker job. Lines that only say what the next line says better are cut. Targets: no more than 2 consecutive lines with the same job; EVIDENCE lines are specific (a number, a named source, a thing shown), not "studies show".

## Transition audit

Read the end of each line and the start of the next. Each pair needs a reason: because, so, which means, but, and then, so now. Filler transitions ("moving on", "now let's talk about", "next up") are cut unless the video is a list. A viewer should never have to hold an unexplained term for more than one line; define it where it first appears.

## Personal relevance early

Within the first third, connect to the viewer in a defensible way: "If you [do specific thing], this is worth checking." Not "everyone makes this mistake" and not "90 percent of people" without a source.

## Cutting to length (in this order)

1. Remove repeated ideas and recaps.
2. Remove the weakest point.
3. Fold two lines saying one idea into a short phrase.
4. Remove setup the viewer already knows from the hook.
5. Remove adjectives and hedges that carry no meaning.
6. Only then tighten wording. Do NOT cut the connectors that make it flow. Propose only changes that remove real words; a same length rewording is not a shortening, list it separately as a quality idea.
Give each proposal as old line, new line and words saved, and keep the user's merges.

## Worked example (placeholder, 45 second video)

Topic: why a loaf comes out dense (spine: problem then cause then fix). Budget: 112 to 135 words.

```
HOOK (13 words)
If your loaf comes out dense, it is probably not your oven.

RELEVANCE (22 words)
So if you bake at home and keep blaming the heat, there is a good chance the real problem happened hours before the loaf went in.

DEFINITION (23 words)
It is called underproofing, which just means the dough did not rest long enough for the yeast to fill it with air.

MECHANISM (35 words)
Yeast makes gas while the dough rests, and that gas is what lifts the loaf. Cut the rest short and the gas is not there, so the oven can only bake a dense crumb.

CATCH (15 words)
A warm kitchen speeds this up, so the time on a recipe is a guide, not a rule.

PAYOFF (17 words)
So poke the dough with a wet finger. If the dent springs back slowly, it is ready.

ACTION (16 words)
If you want my one page proofing guide, comment the word PROOF and I will send it.
```

Total 141 words, over the 135 budget. Estimate: 141 / 3.0 = 47 s to 141 / 2.5 = 56 s, so it is not a 45 second video. Cut: the CATCH line (15 words) if the user wants 45 s; new total 126, 42 to 50 s. Loop table: gap "why dense" opens at 0 s and closes at the MECHANISM line; the PAYOFF gives the action. The ACTION promises "one page", which must exist (`ae-call-to-action-writing`).

## Failure modes

| Failure | Fix |
| --- | --- |
| Hook, then a recap of the hook | Delete the recap, go to relevance |
| Explaining steps in a short | Move steps to the resource |
| A second hook between promise and payoff | Remove it, hold one loop |
| Tail of three CTAs | One action only |
| Runtime given as a single number | Always give a range and say estimate |
| Word budget broken by labels counted | Count spoken words only |
| Choppy 3 word full stop lines | Join with connectors (`ae-spoken-flow-and-plain-language`) |

## Checklist

- [ ] Length and pace stated, word budget computed, range reported.
- [ ] One spine chosen; no second incident added.
- [ ] Every line labelled with one job; no line removable without loss.
- [ ] Loop table complete; every loop closes.
- [ ] Transition audit done; no unexplained term held more than a line.
- [ ] Personal relevance in the first third, without invented prevalence.
- [ ] Action is one sentence and fulfillable.
- [ ] Runtime recomputed after the last edit.

## Hand off to

`ae-hook-writing`, `ae-spoken-flow-and-plain-language`, `ae-value-first-teaching-tone`, `ae-claims-and-truth-ledger`, `ae-call-to-action-writing`, `ae-script-review-gate`, `ae-pacing-and-rhythm` (after approval, for the edit).
