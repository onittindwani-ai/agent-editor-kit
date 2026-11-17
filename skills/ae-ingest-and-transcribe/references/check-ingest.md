# Transcript quality checker (read only)

Save as `check_ingest.py` in the editor folder (or anywhere) and run it against `project/ingest.json`. The optional second argument is a text file with one preferred spelling per line (names, brands, product words). Standard library only. It changes nothing.

```
python3 check_ingest.py project/ingest.json vocab.txt
```

```python
import json, re, sys
from collections import Counter

path = sys.argv[1] if len(sys.argv) > 1 else "project/ingest.json"
vocab_path = sys.argv[2] if len(sys.argv) > 2 else None   # optional: one preferred spelling per line
d = json.load(open(path))
words, silences, dur = d["words"], d["silences"], d["media"]["duration"]
norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
flags = []

def flag(kind, msg):
    flags.append((kind, msg))

print(f"duration {dur:.1f}s, {len(words)} words, {len(silences)} silences, {len(d['sentences'])} sentences")
if not words:
    sys.exit("NO WORDS: the transcript is empty (wrong audio track, silent file, or whisper failed)")

# 1. speaking rate
speech = max(0.1, words[-1]["e"] - words[0]["t"])
rate = len(words) / speech
print(f"first word {words[0]['t']}s, last word ends {words[-1]['e']:.2f}s, rate {rate:.2f} words/s over the spoken span")
if rate < 1.2 or rate > 4.5:
    flag("rate", f"{rate:.2f} words/s is outside 1.2 to 4.5: missed speech or a loop")
if dur - words[-1]["e"] > 3.0:
    flag("tail", f"{dur - words[-1]['e']:.1f}s of audio after the last word: missed speech, or real silence")
if words[0]["t"] > 2.0:
    flag("head", f"first word at {words[0]['t']}s: check the first seconds for missed speech")

# 2. timing sanity
for i, w in enumerate(words):
    if w["e"] <= w["t"]:
        flag("zero", f"word {i} {w['w']!r} at {w['t']} has no length")
    elif w["e"] - w["t"] > 1.2:
        flag("long", f"word {i} {w['w']!r} lasts {w['e'] - w['t']:.2f}s at {w['t']} (held word, or spans a silence)")
    if i and w["t"] < words[i - 1]["e"] - 0.02:
        flag("overlap", f"word {i} {w['w']!r} starts {words[i - 1]['e'] - w['t']:.2f}s before the previous word ends ({w['t']})")
    if i and w["t"] < words[i - 1]["t"]:
        flag("order", f"word {i} {w['w']!r} starts before the previous word at {w['t']}")

# 3. words inside detected silences
for w in words:
    for s in silences:
        ov = min(w["e"], s["e"]) - max(w["t"], s["s"])
        if ov > 0.6 * max(0.01, w["e"] - w["t"]) and s["e"] - s["s"] >= 0.3:
            flag("in_silence", f"{w['w']!r} at {w['t']} sits mostly inside the silence {s['s']} to {s['e']} (hallucination or bad alignment)")
            break

# 4. gaps with no silence entry (threshold too low for this room)
gaps = [(words[i]["e"], words[i + 1]["t"]) for i in range(len(words) - 1) if words[i + 1]["t"] - words[i]["e"] >= 0.5]
unlisted = [g for g in gaps if not any(s["s"] < g[1] and s["e"] > g[0] for s in silences)]
if len(unlisted) >= 3 and len(unlisted) > 0.5 * len(gaps):
    flag("silences", f"{len(unlisted)} of {len(gaps)} gaps of 0.5s or more have no silence entry: the room is noisy, recompute silences")

# 5. loops
toks = [norm(w["w"]) for w in words]
run = 1
for i in range(1, len(toks)):
    run = run + 1 if toks[i] == toks[i - 1] and toks[i] else 1
    if run == 4:
        flag("loop", f"{words[i]['w']!r} repeated 4 times in a row near {words[i]['t']}")
tri = Counter(tuple(toks[i:i + 3]) for i in range(len(toks) - 2))
for k, n in tri.items():
    if n >= 4 and all(k):
        flag("loop", f"phrase {' '.join(k)!r} appears {n} times: check for a hallucination loop")

# 6. known whisper tail hallucinations
tail_text = " ".join(toks[-6:])
for phrase in ("thankyou", "thanksforwatching", "subscribe", "seeyounexttime"):
    if phrase in tail_text.replace(" ", "") and dur - words[-1]["t"] < 6:
        flag("tail_phrase", f"the last words contain {phrase!r}: confirm it was really said")

# 7. vocabulary (optional)
if vocab_path:
    prefer = [l.strip() for l in open(vocab_path) if l.strip()]
    have = Counter(toks)
    for p in prefer:
        parts = [norm(x) for x in p.split()]
        if len(parts) == 1 and parts[0] not in have:
            near = [t for t in have if t and (t[:4] == parts[0][:4]) and t != parts[0]]
            if near:
                flag("vocab", f"{p!r} not found; transcript has {near[:4]} (a likely misspelling)")

for kind, msg in flags:
    print(f"[{kind}] {msg}")
print("OK: no flags" if not flags else f"{len(flags)} flags: read each one, do not fix by guessing")
```

Thresholds are starting values for ordinary speech: 1.2 to 4.5 words per second over the spoken span, a single word longer than 1.2 s, a word mostly inside a detected silence, a gap of 0.5 s or more with no silence entry. Singing, very slow narration or a fast reader can legitimately trip some of them: tell the user, do not "fix" the data.

A clean run (`OK: no flags`) means the numbers look plausible. It does not prove the words are right. Look at thumbnails and compare with the script.
