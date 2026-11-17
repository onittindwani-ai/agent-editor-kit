# Disfluency detector (read only)

Save as `detect_disfluencies.py`. It reads `project/ingest.json` and, when present, `project/a.wav`, and prints candidates: filler sounds, words that may be fillers, doubles, restarts, broken words, self corrections, and sounds in gaps that the transcript does not contain (likely "um" and "uh", or breaths). Standard library only. It changes nothing.

```
python3 detect_disfluencies.py
```

```python
import argparse, array, json, math, re, sys, wave

FRAME = 0.01
FILLER_SOUNDS = {"um", "umm", "uh", "uhm", "uhh", "er", "erm", "ah", "hmm", "mm", "mhm", "huh"}
FILLER_WORDS = {"like", "so", "basically", "actually", "literally", "right", "okay", "well", "anyway"}
SELF_FIX = [("i", "mean"), ("sorry",), ("or", "rather"), ("no", "wait"), ("let", "me", "start"), ("let", "me", "try", "again"), ("scratch", "that")]
SHORT_REAL = set("a i is it to we of in on at an as be by do go he if me my no or so up us oh ok".split())
norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())

def load_env(path):
    w = wave.open(path, "rb")
    data = array.array("h"); data.frombytes(w.readframes(w.getnframes()))
    if sys.byteorder == "big": data.byteswap()
    n = int(w.getframerate() * FRAME)
    return [20 * math.log10(max(math.sqrt(sum(s * s for s in data[i:i + n]) / n), 1.0) / 32768.0)
            for i in range(0, len(data) - n + 1, n)]

def pct(v, p):
    s = sorted(v); return s[min(len(s) - 1, int(len(s) * p))]

def main():
    ap = argparse.ArgumentParser(description="List disfluency candidates (read only)")
    ap.add_argument("--ingest", default="project/ingest.json")
    ap.add_argument("--wav", default="project/a.wav")
    a = ap.parse_args()
    words = json.load(open(a.ingest))["words"]
    toks = [norm(w["w"]) for w in words]
    out = []

    def add(kind, i, j, why):          # words i..j inclusive
        out.append((words[i]["t"], kind, " ".join(w["w"] for w in words[i:j + 1]), words[i]["t"], words[j]["e"], why))

    for i, t in enumerate(toks):
        w = words[i]
        if t in FILLER_SOUNDS:
            add("filler", i, i, "filler sound listed in the transcript")
        elif t in FILLER_WORDS:
            add("check", i, i, "may be a filler or a real word: read the neighbours before removing")
        if w["w"].rstrip().endswith(("-", "\u2014", "...", "\u2026")):
            add("cutoff", i, i, "word ends with a dash or ellipsis: a broken word or false start")
        elif (w["e"] - w["t"]) < 0.12 and len(t) <= 2 and t not in SHORT_REAL and t:
            add("cutoff", i, i, "very short fragment: a stumble")
        if i + 1 < len(toks) and t and t == toks[i + 1]:
            add("double", i, i + 1, "same word twice in a row (keep the last unless the script repeats it)")
    for k in range(2, 7):
        for i in range(len(toks) - 2 * k + 1):
            if toks[i:i + k] == toks[i + k:i + 2 * k] and all(toks[i:i + k]):
                add("double", i, i + k - 1, f"{k} word phrase said twice in a row")
    for i, t in enumerate(toks):
        for pat in SELF_FIX:
            n = len(pat)
            if tuple(toks[i:i + n]) == pat:
                add("selffix", i, i + n - 1, "a self correction: keep the corrected version, check the facts after it")
    starts = [0] + [i + 1 for i in range(len(words) - 1) if re.search(r"[.?!,]$", words[i]["w"]) or words[i + 1]["t"] - words[i]["e"] >= 0.3]
    for i in starts:
        for k in (4, 3, 2):
            head = toks[i:i + k]
            if len(head) == k and all(head):
                for j in range(i + k, min(len(toks) - k + 1, i + 14)):
                    if toks[j:j + k] == head:
                        add("restart", i, j - 1, f"the opening '{' '.join(head)}' is said again at {words[j]['t']:.2f}: the earlier part is a false start")
                        break
                else:
                    continue
                break
    # sounds the transcript does not contain: voiced stretches inside gaps between words
    try:
        env = load_env(a.wav)
        floor = pct(env, 0.10)
        voiced = [v for v in env if v > floor + 15]
        speech = pct(voiced, 0.5) if voiced else floor + 25
        for i in range(len(words) - 1):
            g0, g1 = words[i]["e"], words[i + 1]["t"]
            if g1 - g0 < 0.20:
                continue
            f0, f1 = int((g0 + 0.03) / FRAME), int((g1 - 0.03) / FRAME)
            run = best = 0
            for f in range(f0, min(f1, len(env))):
                run = run + 1 if env[f] >= speech - 15 else 0
                best = max(best, run)
            breath = sum(1 for f in range(f0, min(f1, len(env))) if floor + 4 <= env[f] < speech - 20)
            if best >= 12:
                out.append((g0, "untranscribed", "(sound)", g0 + 0.03, g1 - 0.03, f"{best * FRAME:.2f} s of voiced sound somewhere in this gap with no word: likely um or uh"))
            elif breath >= 20:
                out.append((g0, "breath", "(breath)", g0 + 0.03, g1 - 0.03, f"{breath * FRAME:.2f} s of low level noise in the gap: likely a breath"))
        print(f"noise floor {floor:.1f} dBFS, median speech {speech:.1f} dBFS")
    except (OSError, EOFError, wave.Error):
        print("no wav read: voiced gap scan skipped")
    for t, kind, text, s, e, why in sorted(out):
        print(f"{t:7.2f} {kind:13} {text!r:34} span {s:.2f} to {e:.2f}  {why}")
    print(len(out), "candidates. These are candidates, not decisions: check each against the script and the user's rules.")

main()
```

How to read it:

- `filler`: a filler sound the transcript did contain.
- `check`: a word that is sometimes a filler ("so", "like", "right", "well"). Never remove it from this list alone; read the words around it.
- `double`: the same word, or the same 2 to 6 word phrase, twice in a row.
- `restart`: a sentence opening (2 to 4 words) that is said again within 14 words. The earlier part is the false start.
- `cutoff`: a word ending with a dash or ellipsis, or a very short fragment.
- `selffix`: "I mean", "sorry", "or rather", "no wait" and similar. The corrected version stays.
- `untranscribed`: a stretch of voiced sound inside a gap that has no word. The `span` printed is the whole gap searched, not the sound itself; use `snap_edges.py --at` (from `ae-precise-audio-cut`) to find the exact edges.
- `breath`: low level noise in a gap, likely a breath.

All thresholds are starting values (a gap of 0.20 s or more, a voiced run of 0.12 s at 15 dB under the median speech level, a breath of 0.20 s between 4 dB over the floor and 20 dB under speech). Quiet speakers and noisy rooms shift them. Treat every line as a candidate, never as a decision.
