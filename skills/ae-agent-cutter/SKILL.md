---
name: ae-agent-cutter
description: Role skill for a cutter agent in the Agent Editor. Explains the exact rules the server enforces on cuts, how to compute cut points from word times, one cut per phrase, gap midpoints, words that touch, minimum length, restarts and fillers, and how to read a NO. Use when you are launched as a cutter (role "cutter"), when the user says "cut my window", "remove the pauses and mistakes", or when a conductor briefs you with a time window.
---

# ae-agent-cutter: role skill for cutter agents

Read `brand/profile.md`. If it is missing or a section it needs is empty, stop and run `ae-setup-interview` for that section (ask the user, with options), do not guess. You need `## Rules` (Cut style, Filler policy), `## Voice and tone` (Typing habits), `## Script preferences` (Delivery method). If your conductor pasted a profile excerpt in your prompt, that counts as reading it.

You are one agent in a team editing one video on a shared timeline at `http://127.0.0.1:8780`. You change it only with `curl -X POST .../api/op`. You keep the good speech of your window and drop restarts, filler words, mistakes and long pauses. You do not place captions, effects or graphics, and you do not touch other agents' items.

## 1. The rules of the room

- One operation per tool call. Read the answer (`"ok":true` or `"ok":false,"error":...`) before the next call.
- `hello` first: `{"op":"hello","agent":"W01","role":"cutter"}`.
- `claim` before each piece of work, then the operation.
- If the server says NO, read the reason, fix the operation and send it again. Do not argue and do not work around it.
- Stay inside your window. Use only the transcript: never invent words or times.
- You cannot delete or edit your own cut. Only the reviewer (`reject`) and the human (`remove`) can. So verify before you send.
- Send `done` with a one line summary when finished, then stop. Your final message to the conductor: under 60 words, what you placed and what the server refused.

## 2. What the server enforces on a cut

`{"op":"cut","agent":"W01","start":1.04,"end":3.74,"note":"keep s1 opening claim"}` (seconds of the SOURCE)

| Rule | Detail |
| --- | --- |
| Length | at least 0.4 s (`end - start`) |
| Range | 0 to the video duration |
| Overlap | a new cut may not overlap a live cut (tolerance 0.001 s). Cuts that touch end to start are fine. A rejected cut stops counting, so its span can be cut again. |
| Inside a word | `start` and `end` may not land inside a spoken word. A point is "inside" word w when `w.t + 0.03 < point < w.e - 0.03`. The NO message names the word and suggests `w.t - 0.06` or `w.e + 0.04`. |
| Note | optional text up to 120 characters; write why (`keep s4: the claim`) |

The review (`GET /api/review`) later flags: any silence longer than 0.35 s inside a kept cut (kind `pause`), captions outside kept cuts, and kept words with no caption. You own the pause issues.

## 3. Read your window and plan before you send anything

1. `curl -s 'http://127.0.0.1:8780/api/window?start=S&end=E'` gives `words` (`t` start, `e` end, `w` text), `silences` (`s`, `e`, each at least 0.3 s), `sentences` (`id`, `start`, `end`, `text`) and what is already placed.
2. Read the sentences in order out loud in your head. Mark each word range as KEEP or DROP.
3. Build a table of cuts for the whole window, compute their numbers with the formulas below, check them against the rules, and only then send the first operation. Measure twice: you cannot delete.
4. Send the cuts in time order, one per call. Before each sentence, claim it: `{"op":"claim","agent":"W01","kind":"sentence","id":3,"status":"cutting s3"}`.

Cut style from the profile decides how much to drop:

| Cut style | Pauses | Fillers and breaths | Typical kept share |
| --- | --- | --- | --- |
| tight | split at every gap of 0.25 s or more | drop all fillers and loud breaths | 55 to 80 percent |
| natural | split at gaps of 0.4 s or more, keep shorter ones inside a cut | drop clear fillers, keep soft breaths | 70 to 90 percent |
| relaxed | split only at gaps over 0.7 s or at mistakes | keep natural "okay so" openers, drop mistakes | 85 to 98 percent |

Use the gap thresholds above as `GAP` in the helper below (0.25, 0.4, 0.7). Never leave a silence longer than 0.35 s inside a cut regardless of style (that is a review issue), so with natural or relaxed style still split at gaps over 0.35 s that the silence list marks.

## 4. Computing cut points from word times

A cut starts and ends between words, in the middle of the gap, but never so close to a word that its edge is clipped. The rule that works with the server:
- A cut that begins at word `i` starts at the LATER of `w[i].t - 0.06` and the midpoint of the gap before it.
- A cut that ends at word `j` ends at the EARLIER of `w[j].e + 0.04` and the midpoint of the gap after it.
- **Words that touch** (the gap between two words is under 0.06 s, or they overlap): there is no room for padding. End the cut at the end of the earlier word (`w[j].e`) and start the next cut at the start of the later word (`w[i].t`).

Python helper (compute only; it never sends anything):

```python
import json
ING = json.load(open("project/ingest.json")); W = ING["words"]; DUR = ING["media"]["duration"]
def start_before(i):
    t = W[i]["t"]
    if i == 0: return round(max(0.0, t - 0.06), 3)
    prev_e = W[i - 1]["e"]
    if t - prev_e < 0.06: return round(t, 3)                   # words touch
    return round(max(t - 0.06, (prev_e + t) / 2), 3)
def end_after(j):
    e = W[j]["e"]
    if j == len(W) - 1: return round(min(DUR, e + 0.04), 3)
    nxt = W[j + 1]["t"]
    if nxt - e < 0.06: return round(e, 3)                      # words touch
    return round(min(e + 0.04, (e + nxt) / 2), 3)
def inside(t, m=0.03):
    return next((w for w in W if w["t"] + m < t < w["e"] - m), None)
def phrases(i, j, gap):
    """split the kept word range i..j (inclusive) wherever the gap between words is at least `gap`"""
    out, a = [], i
    for k in range(i, j):
        if W[k + 1]["t"] - W[k]["e"] >= gap: out.append((a, k)); a = k + 1
    out.append((a, j)); return out
def check(cuts, existing=()):
    bad = []
    for s, e in cuts:
        if e - s < 0.4: bad.append((s, e, "shorter than 0.4 s"))
        if not (0 <= s < e <= DUR): bad.append((s, e, "outside the video"))
        for lab, t in (("start", s), ("end", e)):
            w = inside(t)
            if w: bad.append((s, e, f"{lab} inside the word {w['w']}"))
    allc = sorted(list(cuts) + list(existing))
    for (a, b), (c, d) in zip(allc, allc[1:]):
        if c < b - 0.001: bad.append((c, d, f"overlaps {a}-{b}"))
    return bad
```

Use `i` and `j` as word indexes in the whole list (find them from the window's words by matching `t`). `phrases(i, j, GAP)` gives one range per phrase; turn each into `(start_before(a), end_after(b))`. Run `check(...)`; fix every item it reports before sending.

Whisper style word times are approximate (often within 0.1 s, sometimes more). The server can only check against them. If the cut end clips a word's tail or the start clips an onset, the reviewer will catch it by reading the neighbouring words; `ae-precise-audio-cut` explains how to verify against the waveform. When a word is long and slow, give the end an extra 0.04 to 0.08 s only if the gap allows (never past the gap midpoint).

## 5. One cut per phrase

A phrase is a run of words with no pause of `GAP` or more between them. Make one cut per phrase, so the timeline shows every removed pause and the join between phrases is a clean 0.10 s (0.06 before plus 0.04 after) of room instead of a dead gap. A gap shorter than `GAP` stays inside one cut. Do not merge phrases into one long cut across a gap you meant to remove.

## 6. Decision tables

### What to drop

| Pattern | Action |
| --- | --- |
| Filler word between phrases (uh, um, er, hmm) | Drop; the gap before and after it merges into one removed gap. |
| Filler inside a phrase | Split the phrase there: end the first cut at the word before the filler, start the next at the word after. Only if both results are at least 0.4 s; otherwise keep the filler (or ask the conductor). |
| Restart ("the next, the next thing is") | Keep only the final complete take; drop the abandoned start including the word it restarted. |
| Same sentence said twice | Keep the better take: complete, fewest fillers, steady pace; if equal, the later one. |
| Mistake the speaker corrects ("it is 20, no, 30 grams") | Drop the wrong part; keep the corrected version. |
| A long unexplained gap (0.5 s or more) not in the silence list | Something audible is in it (a filler sound, a breath, a click). Whisper often omits fillers. Treat the whole gap as removable and cut around it. |
| Throat clear, lip smack, loud breath | Drop when it sits between phrases; if inside a phrase and splitting breaks the 0.4 s rule, keep it and report it to the conductor. |
| Real pause the speaker uses for effect before a key line (0.4 to 0.8 s) | Keep up to 0.3 s of it in relaxed or natural style by not splitting at that gap; never in tight style unless the profile says so. |

### Short words and short phrases (under 0.4 s)

A cut must be at least 0.4 s. For a phrase that is shorter:
1. Merge it with the neighbouring phrase by not splitting at the gap between them (the pause stays; accept it if the gap is under 0.35 s).
2. Extend the start and end toward the gap midpoints (you are already at the maximum).
3. If neither works and the phrase is a filler, drop it. If it is content, merge with the neighbour and tell the conductor the pause stays.

### Sentence integrity

Keep whole sentences. Never end a cut on a word that leaves a sentence hanging unless the rest was a restart you are dropping. A sentence's last word keeps its trailing consonant: end at `w.e + 0.04` or the gap midpoint, whichever is earlier.

### Window edges

- Your first cut starts at or after the window start; your last ends at or before the window end.
- If a word straddles the window edge, include it only when the conductor says so; otherwise leave it to the neighbour and tell the conductor in your final message.
- Do not cut across the edge; the other cutter owns the next window.

## 7. When the server says NO

| Message (shortened) | Fix |
| --- | --- |
| `a cut must be at least 0.4 s long` | Merge with a neighbour or drop the phrase (section 6). |
| `overlaps c3 (a-b); each part of the source can be kept once` | Read `/api/window` for the live cuts; shift your cut to start at that cut's end (touching is allowed) or drop the overlapping part. If the overlapped cut belongs to another cutter, the windows overlap: tell the conductor. |
| `cut start 3.0 lands inside the word 'bake' ... use 2.86 or 3.24` | Use the suggested number that is on the correct side: the earlier number if this point begins a cut that should include the word, the later one if it ends a cut that should include the word. |
| `'start' must be a number` or `'end' must be between 0 and D` | Fix the number; check the helper output. |
| `say hello first` | Send hello with your id and role. |
| `agent is required` | Add the `agent` field. |

If three NOs in a row have the same reason, stop and recompute the whole table; you are guessing.

## 8. Finish

1. Run `curl -s http://127.0.0.1:8780/api/review` and read the issues that mention your cuts (`pause` entries name your cut id).
2. Compare your kept time with your window: kept share against the style target. Much lower means you dropped real content; much higher means pauses remain.
3. Read your window once more in `/api/window` and check the cut lane against the sentences: every sentence you wanted is whole, every restart is gone.
4. `{"op":"done","agent":"W01","summary":"14 cuts, 41.2 s kept of 46.4, 2 NOs fixed"}`.
5. Final message under 60 words: counts, kept seconds, refusals, anything the conductor must know (a straddling word, a pause you had to keep).

## 9. Worked example (placeholder content)

Window words (seconds), a baker explaining bread; index, start, end:

```
0 Uh 0.40-0.62     6 show 2.16-2.42    12 Okay 4.60-4.84    18 Um 7.10-7.30
1 So 1.10-1.28     7 you 2.44-2.60     13 the 4.86-4.96     19 the 7.82-7.92
2 today 1.30-1.62  8 how 2.62-2.80     14 first 4.98-5.30   20 next 7.94-8.20
3 I'm 1.64-1.80    9 to 2.82-2.90      15 thing 5.32-5.62   21 the 8.60-8.70
4 going 1.82-2.04  10 bake 2.92-3.20   16 is 5.64-5.76      22 next 8.72-8.98
5 to 2.06-2.14     11 bread. 3.22-3.70 17 flour. 5.78-6.20  23 thing 9.00-9.30 | 24 is 9.32-9.42 | 25 water. 9.44-9.90
```

Natural style, GAP 0.4. Decisions:
- Word 0 "Uh": filler, drop. Words 1 to 11 are one phrase (all gaps under 0.4 s): "So today I'm going to show you how to bake bread."
- Word 12 "Okay": filler between sentences, drop.
- Words 13 to 17: one phrase "the first thing is flour."
- Words 18 to 20: "Um", then "the next" abandoned, restarted at word 21. Drop 18, 19, 20; keep 21 to 25 "the next thing is water."

Numbers:
- Cut 1: `start_before(1)`: previous word ends 0.62, gap 0.48. Later of 1.10 - 0.06 = 1.04 and midpoint 0.86, so 1.04. `end_after(11)`: 3.70 + 0.04 = 3.74 (the midpoint of the 0.9 s gap is 4.15). Cut 1 = 1.04 to 3.74, 2.70 s.
- Cut 2: word 13 touches "Okay" (gap 0.02), so start at 4.86. End: 6.20 + 0.04 = 6.24 (midpoint 6.65). Cut 2 = 4.86 to 6.24, 1.38 s. Onset risk: no padding before "the"; flag it to the conductor for `ae-precise-audio-cut`.
- Cut 3: previous word 20 ends 8.20, gap 0.40: later of 8.60 - 0.06 = 8.54 and midpoint 8.40 gives 8.54. Last word: 9.90 + 0.04 = 9.94. Cut 3 = 8.54 to 9.94, 1.40 s.
- `check` passes: lengths 2.70, 1.38, 1.40; no point lies inside a word; no overlap.

Calls, one per tool call, claim first:

```
curl -s -X POST http://127.0.0.1:8780/api/op -H 'Content-Type: application/json' -d '{"op":"claim","agent":"W01","kind":"sentence","id":0,"status":"cutting the opening"}'
curl -s -X POST http://127.0.0.1:8780/api/op -H 'Content-Type: application/json' -d '{"op":"cut","agent":"W01","start":1.04,"end":3.74,"note":"keep s0 opening, drop Uh"}'
```

A wrong try: `start` 3.0 would land inside "bake" (2.92 to 3.20), so the server answers NO and says `use 2.86 or 3.24`. For the opening you would never start there anyway; the fix is the helper's number, not the hint.

Result: the video keeps "So today I'm going to show you how to bake bread. The first thing is flour. The next thing is water." with a 0.10 s room around each join.

## 10. Failure modes

| Failure | Prevention |
| --- | --- |
| Sending cuts one by one and discovering overlaps live | Plan the whole table and run `check` first. |
| One giant cut over the whole window | One cut per phrase; remove every pause of `GAP` or more. |
| Cutting at the exact word boundary of a touching pair and hoping | Use the touching rule and report onset risk. |
| Trusting the silence list for hidden fillers | A long gap not listed as silence hides a sound; cut around it. |
| Dropping content to hit the ratio | The ratio is a check, not a goal; content comes first. |
| Editing outside the window | The conductor owns the edges. |
| Rewording the speaker | You only select and trim; you never change words. |
| Ignoring typing habits or delivery method | A teleprompter script is final; never drop a scripted line without asking. |

## Checklist

- [ ] Hello sent; window read; cut style and GAP chosen from the profile.
- [ ] A full table of cuts computed with the helper and passed `check`.
- [ ] Each sentence claimed before its cuts; one operation per call.
- [ ] Every NO read and fixed by recomputing, not by guessing.
- [ ] Review shows no `pause` issue for my cuts; kept share is in the expected range.
- [ ] `done` sent; final message under 60 words.

Hand off to: `ae-agent-captioner` (captions follow your cuts), `ae-agent-reviewer`, `ae-precise-audio-cut`, `ae-filler-and-restart-removal`, `ae-pacing-and-rhythm`, `ae-run-multi-agent-edit`.
