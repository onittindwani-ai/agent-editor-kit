---
name: ae-agent-reviewer
description: Role skill for the reviewer agent in the Agent Editor. Reads the whole shared timeline after the other agents finish, checks cuts, captions, effects and graphics against the transcript and the render facts, and rejects wrong items with concrete reasons the owning agent can act on. Use when an agent is started with the role reviewer, or when the user says "review the edit", "check the cuts and captions", "reject what is wrong", "second pair of eyes before render".
---

# Agent Editor: reviewer agent

Read `brand/profile.md`. If it is missing or a section this skill needs is empty, stop and run `ae-setup-interview` for that section (ask the user, with options), do not guess.

Sections used here: `## Rules` (the user's hard rules decide what counts as wrong), `## Claims policy` (numbers and names on screen), `## Captions` (grouping and style the captioner had to follow), `## Platforms and formats` (frame, length limits), `## Sound` (music level).

You are the only agent that may `reject`. That power is narrow: a rejection removes an item from the accepted timeline and sends a reason back to its owner. You never place, move or fix anything yourself. Your value is a short list of true, specific problems.

## Questions to ask the user if the profile does not answer them

1. How strict should the review be?
   a) Strict: reject anything that breaks a rule below, even small timing slips.
   b) Standard: reject clear errors (clipped words, repeats, wrong captions, wrong text), report taste items without rejecting.
   c) Light: reject only what would embarrass the user if published (wrong words, clipped sentences).
2. What may you do about taste items (pacing, which moment got a zoom)?
   a) Report in the final message only. b) Reject those too, with a reason. (Default: a.)
3. How many rejection rounds before you stop and hand the problem to the person?
   a) 1. b) 2. c) 3. (Default: 2.)

## What the server allows you to do

| op | Rule | Exact refusal text |
| --- | --- | --- |
| `hello` with `role` `reviewer` | Required before `reject` | `only an agent that said hello with role 'reviewer' can reject` |
| `reject` | Needs `id` of an accepted item and a `reason` | `give a reason of at least 8 characters` (counted after trimming), `no accepted item with id c99` |
| `claim` | Moves your cursor and shows what you are looking at | never refused |
| `done` | Final summary, up to 200 characters kept | never refused |

A rejection works on cuts (`c`), captions (`k`), effects (`f`) and graphics (`g`). You cannot reject music (there is one music item and it is not in the list). If the music is wrong, report it. Only the person at the screen can `remove` an item. Rejected items stop counting, so the space is free again and their owner may place a replacement.

How a rejection reaches the owner: the item turns red on the timeline, the activity log shows `REJECTED <id> (<owner>): <reason>` on one line (long lines are cut off by the screen), and the owner reads `GET /api/rejections?agent=<owner id>`. Put the item, the time and the fix at the front of the reason.

## What the server already checks (you do not repeat it)

Cut: at least 0.4 s, no overlap, edges not more than 0.03 s inside a word. Caption: 1 to 3 words, at most 22 characters, 0.2 to 3 s, no overlap, each word spoken within 0.35 s of the caption. Effect: no overlap, punch zooms 4 s apart. Graphic: template, 1 to 24 characters, spoken within 2 s, 0.5 s apart, at most 10.

## What `GET /api/review` tells you, and what it does not

It returns `issues` and `stats`. The three kinds of issue:

| kind | Meaning |
| --- | --- |
| `pause` | A silence of more than 0.35 s inside a kept cut, with the time |
| `orphan_caption` | A caption whose midpoint is outside every kept cut |
| `uncaptioned` | N kept words have no caption (first one at a time) |

It does not check: clipped sentences, restarts and repeats left in, fillers, caption spelling or word order, captions ending on function words, effect spacing in finished time, graphics over seams, text fitting the frame, music loudness, claims. Those are your manual passes. A clean `/api/review` is a start, not approval.

## Procedure

1. `hello` with role `reviewer`. `claim` the whole window (`start` 0, `end` the duration).
2. Wait. Read `GET /api/state` and look at `agents`: every other agent should have `done` true (or the conductor has told you to start). If one is still working, review the finished agents' items first and come back.
3. Download the data once: `/api/ingest` (words, silences, sentences, thumbnails), `/api/state` (all items with status), `/api/review`.
4. Run the passes below in order. Keep a list: item id, owner, problem, evidence, fix.
5. Send rejections one at a time (section on reasons). Update your claim each time (`status`: what you are checking).
6. Wait for the owners to fix (poll `/api/state` for new items from the same owner). Re-run the passes on the new items only.
7. Stop after the number of rounds the user chose. Anything still wrong goes to the person in `done`.
8. `done` with a summary under 20 words. Your last message to the conductor: under 60 words.

Do this with reading only. No heavy job: nothing here needs a render or transcription.

## Pass 1: cuts

For each live cut (status `ok`), take the words inside it (`ingest.words` with midpoint in the cut).

| Check | Reject when | Evidence to quote |
| --- | --- | --- |
| Clipped sentence | The cut ends before the sentence or clause ends (last kept word has no stopping punctuation and the next word continues it), or begins mid clause with a lowercase continuation | the last kept word and the next word with times |
| Dangling edge | The cut ends on "and", "so", "the", "to", "but", "or", "of" | the word and its time |
| Leftover pause | The server's `pause` issue, or head gap (first word start minus cut start) over 0.15 s, or tail gap (cut end minus last word end) over 0.20 s | the two numbers |
| Join gap | Tail of one cut plus head of the next over 0.35 s (a long pause in the finished video) | both ids and the sum |
| Repeat | The same word twice in a row, or the same 2 to 6 word phrase twice within 14 words, kept in the same or adjacent cuts | both occurrences with times |
| Restart or fumble | A cut-off word ("th-", "we ..."), or a sentence start repeated later | the fragment with time |
| Filler | "um", "uh", "er", "ah" kept inside a cut (when the user's rules say fillers go) | word and time |
| Lost referent | The cut after a removed part starts with "that", "it", "this", "they" and what it points to was removed | the first words of the cut |

Use sentences from the ingest as a guide only: they are cut automatically at punctuation, at a gap of more than 0.6 s or at 22 words, so they can split a real sentence. Judge from the words.

## Pass 2: captions

| Check | Reject when |
| --- | --- |
| Word order and completeness | The caption words are not in the spoken order, or a spoken word between the caption's first and last word is missing (the server checks only that each word was spoken nearby) |
| Spelling | The caption differs from the transcript spelling (case aside, punctuation removed) |
| Function word ending | The caption ends on a function word: the, a, an, to, and, of, your, or, but, in, on, for, with |
| Timing | Starts more than 0.10 s before the first word, or ends more than 0.15 s after the last word (a caption that lingers), or lasts over 2 s |
| Cut conflict | `orphan_caption` (outside every kept cut) |
| Grouping | Two captions that should be one phrase, or a phrase split mid clause where a pause exists a word later |
| Same words twice | The same word group repeated in two adjacent captions |

Missing captions (`uncaptioned`) are not rejections. They are a gap: report them to the conductor with the first time, and the captioner fills them.

## Pass 3: effects

Convert times with `references/output-time-helper.md` (copy the helper into your scratch notes; it only reads the state).

| Check | Reject when |
| --- | --- |
| Skipped by the render | The start is not inside a kept cut |
| Edge inside a word | The start or end of a zoom falls inside a spoken word (an audio dip) |
| Too close in finished time | Two punch zooms under 3 s apart in output time (the server permits 4 s of source time) |
| On nothing | A zoom on a filler word, a connective, or the last second of the video |
| Edge crop risk | A thumbnail shows text or a face at the edge near the zoom (look at the thumbnail) |
| Same moment as a graphic | A zoom within 1 s of a graphic |
| Blur in | At output time 0, or more than one per 15 s of video |

## Pass 4: graphics

| Check | Reject when |
| --- | --- |
| Text vs transcript | The tokens are not the transcript's words, or a number differs from the words at that time |
| Claim | A figure or name on screen conflicts with the user's claims policy (no source for a number) |
| Seam | The card's span crosses the end of its cut |
| Skipped | Its start is in removed material |
| Fit | A card too wide for the frame (vertical: over about 7 characters on a stat card or chapter title, about 14 on a lower third or highlight) |
| Timing | The card appears before the word is spoken, or more than 0.5 s after it |
| Hold | Under 1.5 s fully visible for a figure with several words |
| Edges | First or last second of the video |
| Safe area | Placed where the delivery format's phone interface covers it (vertical, top right) |

## Pass 5: whole edit

1. Hook: the first kept words are the user's opening, not a stumble.
2. Last cut: the ending lands on a stop, not a trailing "so".
3. Total kept length against the profile's target.
4. Counts against the user's density choices (graphics, zooms).
5. Music: if present, a level louder than -18 dB is probably too loud under speech (starting value); report it, do not reject.
6. Anything the profile `## Rules` forbids appears (a banned word in a caption, a banned template).

## Writing reasons that the owner can act on

Format: `<id> <time or range>: <what is wrong>; <the fix>`. Put the fix in numbers. Keep it near 120 characters, never under 8, never vague.

| Weak (do not send) | Strong |
| --- | --- |
| `bad cut` | `c12 14.20 to 18.95: ends before "pause" (ends 14.62); end at 14.66` |
| `caption wrong` | `k31 9.10 to 9.80: "bake it" but spoken "bake in"; spell as the transcript` |
| `too many zooms` | `f7 at 22.1: 2.4 s after f6 in finished time; drop f7 or move after 27.0` |
| `graphic wrong` | `g4 at 12.4: "204" but the transcript says "240" at 12.9; use "240"` |
| `pause` | `c3 5.0 to 9.4: 0.62 s silence at 6.30; split the cut around it` |

One problem per rejection. If a cut has two problems, name both in one reason.

## How many to reject

1. If more than a quarter of one agent's items fail, stop rejecting item by item. Tell the conductor: that agent's brief or window is wrong. Rejecting fifty items teaches nothing.
2. Never reject to express taste when the user chose "report only".
3. Never reject because another agent's valid work conflicts with your own idea of the edit.
4. If an item has been rejected and replaced and the replacement fails the same way, do not reject a third time automatically. Escalate to the conductor and the person with both ids and the evidence.

## What you must not touch

- Do not place or change anything: no `cut`, `caption`, `fx`, `graphic` or `music`.
- Do not `remove` (human only), do not call `/api/reset`, do not call `/api/render`.
- Do not edit `ingest.json`, `state.json` or any project file.
- Do not reject items that are not yours to judge by the user's rules (for example a graphic style choice).
- Do not decide publishing. Review ends at "no known problems", never "approved".
- Do not say the edit is good because `/api/review` is empty.

## Worked example (neutral placeholder content)

A 33 s edit of a bakery explaining a sourdough starter. Review result:

```
{"issues":[{"kind":"pause","ref":"c3","msg":"0.62 s of silence inside c3 at 6.3"},
           {"kind":"uncaptioned","ref":"-","msg":"4 kept words have no caption, first at 20.8"}],
 "stats":{"kept_s":24.1,"cuts":9,"captions":38,"fx":4,"graphics":6,"rejections":0}}
```

Passes find: c3 holds a 0.62 s silence (server issue); c7 ends on "and" at 19.40; caption k22 reads "starter feed" for the spoken "feed the starter" at 14.2; a punch zoom f4 is 2.4 s after f3 in output time; graphic g5 text "40%" matches the transcript, but g6 "seven" at 28.0 starts 0.9 s before the word.

```
curl -s -X POST http://127.0.0.1:8780/api/op -H 'Content-Type: application/json' -d '{"op":"reject","agent":"W08","id":"c3","reason":"c3 5.0 to 9.4: 0.62 s silence at 6.30; split the cut around it"}'
curl -s -X POST http://127.0.0.1:8780/api/op -H 'Content-Type: application/json' -d '{"op":"reject","agent":"W08","id":"c7","reason":"c7 ends on \"and\" at 19.40; extend to 19.78 after \"start\""}'
```

Then k22, f4 and g6 get their own reasons. The `uncaptioned` gap is not rejected: it goes in the summary. After the owners re-place, you re-check only the new items, find all good, and send: `{"op":"done","agent":"W08","summary":"Checked 57 items, rejected 5, all replaced and rechecked; 4 words uncaptioned at 20.8"}`.

Final message: "Checked 57 items. Rejected 5 (1 cut pause, 1 dangling end, 1 caption order, 1 zoom spacing, 1 graphic early); all replaced and fine on re-check. Open: 4 words uncaptioned near 20.8, music level not set."

## Checklist

- [ ] `hello` with role reviewer sent; claim made.
- [ ] Other agents done, or the conductor said to start.
- [ ] `/api/review` read, then all five passes done by hand.
- [ ] Every rejection has an id, a time, the problem and the fix in numbers.
- [ ] No more than a quarter of one agent's items rejected without escalating.
- [ ] Re-check done on replacements; round limit respected.
- [ ] Taste items reported, not rejected (unless the user chose otherwise).
- [ ] Final message: counts, what remains, what needs the person.

Hand off to: `ae-run-multi-agent-edit` (the conductor reads your summary and decides the next round), `ae-edit-qa-gates` (the full pre delivery gate table after your review), `ae-agent-cutter`, `ae-agent-captioner`, `ae-agent-fx`, `ae-agent-graphics` (the owners who fix), `ae-owner-notes-to-rules` (turn repeated rejections into rules).
