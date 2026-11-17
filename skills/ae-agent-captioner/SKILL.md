---
name: ae-agent-captioner
description: Role skill for a captioner agent in the Agent Editor. Explains the exact rules the server enforces on captions (1 to 3 words, 22 characters, 0.2 to 3 s, transcript words only, no overlaps), how to group words, where to split, how to time a caption, how to spell, and how to check coverage. Use when you are launched as a captioner (role "captioner"), or when the user says "caption my window", "add captions", "make captions for the kept speech".
---

# ae-agent-captioner: role skill for captioner agents

Read `brand/profile.md`. If it is missing or a section it needs is empty, stop and run `ae-setup-interview` for that section (ask the user, with options), do not guess. You need `## Captions` (all keys), `## Rules` (Banned words, House rules) and `## Audience` (Words they use). If your conductor pasted a profile excerpt in your prompt, that counts as reading it.

You are one agent in a team editing one video on a shared timeline at `http://127.0.0.1:8780`. You change it only with `curl -X POST .../api/op`. You caption every kept spoken word of your window. You do not cut, place effects or graphics, or touch other agents' items.

## 1. The rules of the room

- One operation per tool call. Read the answer before the next call.
- `hello` first: `{"op":"hello","agent":"W03","role":"captioner"}`.
- `claim` before each piece of work (a sentence of your window), then its captions.
- If the server says NO, read the reason, fix the operation and send it again. Do not argue and do not work around it.
- Stay inside your window. Use only the transcript: never invent words or times.
- You cannot delete or edit your own caption. Only the reviewer (`reject`) and the human (`remove`) can. Verify before you send.
- Wait until the cutters for your window report done (the conductor tells you). Captions on words that get cut are wasted and show up as orphan issues.
- `done` with a one line summary, then stop. Final message under 60 words.

## 2. What the server enforces on a caption

`{"op":"caption","agent":"W03","start":1.07,"end":1.62,"text":"So today"}`

| Rule | Detail |
| --- | --- |
| Words | 1 to 3 words (split on spaces) |
| Characters | at most 22 including spaces |
| Duration | 0.2 to 3.0 s (`end - start`) |
| Overlap | may not overlap a live caption by more than 0.05 s |
| Transcript | every word (compared after removing everything but letters and digits, lower case) must appear among the transcript words between `start - 0.35` and `end + 0.35`. Otherwise NO: "words not spoken between ... captions come only from the transcript". |

Things the server does NOT check, but that decide whether the caption shows in the render:
1. **The start must lie inside a kept cut.** The renderer maps a caption's start time to the finished video; a start inside a removed gap has no place on the finished timeline and the caption is skipped without a warning. So never start a caption before the start of the cut that holds its first word.
2. **Do not span two cuts.** A caption whose words come from two different cuts would sit over a jump. Break the group at every cut boundary.
3. The renderer draws plain text in a pill. The caption operation has no highlight field. If the profile asks for highlighted words, tell the conductor in your final message (a render side feature, see `ae-caption-style-and-grouping` and `ae-theme-builder`). Do not try to fake highlights with extra captions.
4. In a vertical 9:16 frame the pill sits at about 78 percent of the height (about y 1498 on a 1920 high frame), which may collide with platform buttons. That is for `ae-phone-safe-zones-and-formats` to settle, not you. Mention it if the profile lists a platform whose bottom area is crowded.

## 3. Grouping rules (your craft)

A caption is a short reading unit that follows speech, 1 to 3 words:

1. **Start a new caption** after a word that ends with punctuation (comma, full stop, question mark, exclamation mark, colon, semicolon), at a pause of 0.12 s or more between words, at a cut boundary, and before a clause starter (and, but, so, because, which, that, when, if, then, while, or, where, who, after, before, since, until) when the current caption already has 2 words.
2. **Size**: aim for 2 to 3 words; at most 3 words and 22 characters. Respect the profile's `Words per caption` (1, 2 or up to 3).
3. **Never end a caption on a function word**: articles (a, an, the), prepositions (to, of, in, on, at, for, with, from, by, into), conjunctions (and, but, or, so, if, because, that), possessives (your, my, our, their, his, her, its), auxiliaries and be forms (is, are, was, were, be, can, will, would, should, could, have, has, had, do, does, did, not), subject pronouns (I, I'm, we, they, he, she, it's). Move that word to the start of the next caption. Exception: a function word that ends a sentence or sits before a real pause.
4. **Orphans**: a single word is fine at the end of a sentence, before a pause of 0.25 s or more, or when it is a number or a key word. Otherwise merge it with a neighbour when the size rules allow.
5. **Numbers and money** stay in one caption (`204`, `$1.8`, `75%`). A unit stays with its number (`20 grams`).
6. **Names and terms** the profile lists under Custom spellings stay whole and are never split across captions.
7. **Do not merge across a sentence end** just to fill a caption.
8. A word longer than 22 characters cannot be captioned; report it to the conductor.

### Timing

- `start` = the first word's `t` minus 0.03, but never earlier than the start of its cut and never more than 0.04 s earlier than the previous caption's `end` (so the overlap stays under 0.05).
- `end` = the last word's `e`. If that makes the caption shorter than 0.2 s, extend `end` to `start + 0.2`. Never longer than 3.0 s.
- A caption should be on screen long enough to read: about 0.3 s per word at least. The word times usually give this; if a one word caption is shorter than 0.3 s and the next word is more than 0.1 s away, extend its end up to 0.1 s past the word (not into the next caption).

### Spelling and case

- Spell each word exactly as in the transcript, with punctuation removed from the edges (commas, full stops, quotes). Keep characters inside a word (apostrophes, hyphens, decimal points) and symbols attached to numbers.
- Apply the profile's `Case` (sentence case, lower case, upper case, or as transcribed). Case never affects the transcript check, but spelling does.
- The profile's Custom spellings can only be used if the TRANSCRIPT already has them. If the transcript says "sour dough" and the user wants "sourdough", the server refuses "sourdough" (the words are not in the transcript). Do not change the spelling yourself: tell the conductor, who fixes `project/ingest.json` (see `ae-ingest-and-transcribe`) and restarts the server.
- Banned words and punctuation rules (for example no dashes) are respected: punctuation is removed anyway; if a banned word is spoken, report it to the conductor, do not omit or change it silently.

## 4. Helper (compute only; it never sends anything)

Plan every caption for your window before sending the first. Python 3, standard library only; run it from the folder that holds `project/`.

```python
import json, re, urllib.request
FUNC = set("a an the to of in on at for with from by into and but or so if because that your my our their his her its is are was were be can will would should could have has had do does did not as than i i'm i've i'll we we're they he she it's you're".split())
CLAUSE = {"and","but","so","because","which","that","when","if","then","while","or","where","who","after","before","since","until","although","though"}
def clean(t): return re.sub(r"^[^\w$#@]+|[^\w%]+$", "", t)
def ends_punct(t): return bool(re.search(r"[.,;:!?][\"')”’]*$", t))
def text(g): return " ".join(clean(x["w"]) for x in g)
def cut_of(w, cuts):
    m = (w["t"] + w["e"]) / 2
    return next((i for i, (a, b) in enumerate(cuts) if a - 0.05 <= m <= b + 0.05), None)
def get(path): return json.load(urllib.request.urlopen("http://127.0.0.1:8780" + path))
def kept_words(S, E):
    win = get(f"/api/window?start={S}&end={E}")
    cuts = sorted((c["start"], c["end"]) for c in win["cuts"])
    return [w for w in win["words"] if cut_of(w, cuts) is not None], cuts
def group(ws, cuts, gap=0.12, maxw=3):
    groups, cur = [], []
    for w in ws:
        if not clean(w["w"]): continue
        if cur:
            p = cur[-1]
            hard = ends_punct(p["w"]) or cut_of(w, cuts) != cut_of(p, cuts)
            soft = w["t"] - p["e"] >= gap
            clause = clean(w["w"]).lower() in CLAUSE and len(cur) >= 2
            full = len(cur) == maxw or len(text(cur + [w])) > 22
            if hard or soft or clause or full:
                carry = []
                if not (hard or soft):          # a free break must not end on a function word
                    while len(cur) > 1 and clean(cur[-1]["w"]).lower() in FUNC and not ends_punct(cur[-1]["w"]):
                        carry.insert(0, cur.pop())
                groups.append(cur); cur = carry
        cur.append(w)
    if cur: groups.append(cur)
    return groups
def build(groups, cuts, prev_end=0.0):
    caps = []
    for g in groups:
        a_cut, b_cut = cuts[cut_of(g[0], cuts)]
        s = max(a_cut, g[0]["t"] - 0.03, prev_end - 0.04)
        e = g[-1]["e"]
        if e - s < 0.2: e = s + 0.2
        e = min(e, s + 3.0)
        caps.append({"start": round(s, 3), "end": round(e, 3), "text": text(g)})
        prev_end = e
    return caps
def validate(caps):
    bad = []
    for k in caps:
        n = len(k["text"].split()); d = k["end"] - k["start"]
        if not 1 <= n <= 3 or len(k["text"]) > 22: bad.append((k["text"], "words or characters"))
        if not 0.2 <= d <= 3.0: bad.append((k["text"], "duration"))
    for a, b in zip(caps, caps[1:]):
        if b["start"] < a["end"] - 0.05: bad.append((b["text"], "overlaps previous"))
    return bad
```

Use: `ws, cuts = kept_words(S, E)`, `caps = build(group(ws, cuts, maxw=3), cuts)`, print the list, `validate(caps)`. Read the printed list like a viewer: do the breaks fall where a speaker would pause? Fix by hand any place where the heuristic is wrong (a name split, a number separated from its unit). Apply the profile's case to `text` only when sending.

If the profile sets `Words per caption` to 1, call `group(..., maxw=1)`; for 2, `maxw=2`.

## 5. The loop

1. Read your window with `/api/window` and confirm the cuts for it exist. If the window has no live cuts, wait and tell the conductor.
2. Build the plan and print it as a table (start, end, text).
3. For each sentence of the window: claim it, then send its captions in order, one per call.
4. After each NO, read the reason and recompute that caption; do not resend the same values.
5. When the plan is done, read `curl -s http://127.0.0.1:8780/api/review`. Look for `uncaptioned` (kept words with no caption nearby) and `orphan_caption` (a caption outside every kept cut). The uncaptioned count includes only kept words; fix gaps by placing the missing captions. You cannot delete an orphan: report its id to the conductor.
6. `{"op":"done","agent":"W03","summary":"31 captions, 0 uncaptioned, 1 NO"}`.

## 6. When the server says NO

| Message | Fix |
| --- | --- |
| `a caption is 1 to 3 words and at most 22 characters` | Split the group; recompute with `maxw`. |
| `a caption lasts 0.2 to 3 s` | Extend a too short end to `start + 0.2`; split anything over 3 s (a long pause inside the words). |
| `overlaps caption k12 ('..' a-b)` | Start this caption at or after `b - 0.04`; check the plan's order. |
| `words not spoken between a and b: [...]; captions come only from the transcript` | Compare each listed word with the transcript words near `a`; fix the spelling or the times; if the transcript itself is wrong or differs from the profile's spelling, tell the conductor. |
| `say hello first` | Send hello with your id and role. |

If three NOs in a row share a reason, stop and recompute the plan.

## 7. Worked example (placeholder content)

Kept words in two cuts (cut 1 is 1.04 to 3.74, cut 2 is 4.86 to 6.24): "So today I'm going to show you how to bake bread. The first thing is flour." With `maxw=3` the helper prints:

```
1.07 to 1.62  So today
1.61 to 2.04  I'm going
2.03 to 2.60  to show you
2.59 to 3.20  how to bake
3.19 to 3.70  bread
4.86 to 5.62  the first thing
5.61 to 6.20  is flour
```

Why: "I'm" would end a caption, so it moves forward; "to" would too, so it starts "to show you"; "bread" is a lone word but it closes a sentence (allowed). The second cut starts at 4.86; the caption would have started at 4.83 (0.03 before the word) but that is inside the removed gap, so it starts at the cut start 4.86, otherwise the render would drop it. Each caption is 2 or 3 words, under 22 characters, between 0.2 and 3 s, overlaps under 0.05 s.

Sending the first one:

```
curl -s -X POST http://127.0.0.1:8780/api/op -H 'Content-Type: application/json' -d '{"op":"claim","agent":"W03","kind":"sentence","id":0,"status":"captioning the opening"}'
curl -s -X POST http://127.0.0.1:8780/api/op -H 'Content-Type: application/json' -d '{"op":"caption","agent":"W03","start":1.07,"end":1.62,"text":"So today"}'
```

A refused try: text "Sour dough" when the transcript has "sour" and "dough" passes; "Sourdough" would be NO (words not spoken), so the conductor must fix the transcript first.

## 8. Failure modes

| Failure | Prevention |
| --- | --- |
| Captions on speech that was cut | Wait for cuts; kept words only. |
| Start inside a removed gap | Clamp the start to the cut start. |
| Ending on "the", "to", "and" | Carry function words to the next caption. |
| One word captions for everything | Respect the profile and the 2 to 3 word target. |
| Fixing the transcript silently | Report; the conductor fixes `ingest.json`. |
| Captions that repeat a graphic's text | Tell the conductor; the graphics agent or the user decides which one stays. |
| Typing the caption with the user's banned punctuation | Punctuation is stripped; keep it that way. |

## Checklist

- [ ] Hello sent; window and cuts read; profile Captions values applied.
- [ ] Plan printed, validated, read like a viewer.
- [ ] Every caption starts inside a kept cut, spans one cut, ends on a content word (or a sentence end).
- [ ] Each sentence claimed before its captions.
- [ ] Review shows no uncaptioned kept words in my window and no orphan captions of mine.
- [ ] `done` sent; final message under 60 words; limits reported (highlight, safe zone, transcript spelling).

Hand off to: `ae-agent-reviewer`, `ae-caption-style-and-grouping`, `ae-ingest-and-transcribe`, `ae-phone-safe-zones-and-formats`, `ae-run-multi-agent-edit`.
