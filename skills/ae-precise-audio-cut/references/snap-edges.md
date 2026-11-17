# Edge snapping helper (read only)

Save as `snap_edges.py`. It reads the 16 kHz mono wav that the ingest made (`project/a.wav`) and `project/ingest.json`, builds a 10 ms level envelope in dBFS, and suggests where a cut should end and the next one start so no word is clipped and little silence is left. Standard library only. It changes nothing.

Use it for one join at a time: `--a` is the index of the last word you KEEP before the removed part, `--b` is the index of the first word you KEEP after it (indexes in `ingest.json` `words`). Use `--at T` to look at the levels around any time.

```
python3 snap_edges.py --a 41 --b 44
python3 snap_edges.py --at 12.48
```

Defaults are starting values: an onset counts when three frames in a row are 9 dB above the noise floor (`--onset-db`), a tail counts as over when three frames in a row are under 6 dB above the floor (`--tail-db`), the start edge sits 0.03 s before the onset (`--start-pad`), the end edge 0.02 s after the tail (`--end-pad`). Soft starts (f, s, th, h) and soft endings (s, t, k released) may need a lower `--onset-db` (6) or a longer pad; hard starts (p, t, k, b, d, g) may need a pad of 0.05.

```python
import argparse, array, json, math, sys, wave

FRAME = 0.01  # 10 ms frames

def load_env(path):
    w = wave.open(path, "rb")
    if w.getsampwidth() != 2 or w.getnchannels() != 1:
        sys.exit("expected a 16 bit mono wav (project/a.wav is)")
    sr = w.getframerate()
    data = array.array("h")
    data.frombytes(w.readframes(w.getnframes()))
    if sys.byteorder == "big":
        data.byteswap()
    n = int(sr * FRAME)
    env = []
    for i in range(0, len(data) - n + 1, n):
        seg = data[i:i + n]
        rms = math.sqrt(sum(s * s for s in seg) / n)
        env.append(20 * math.log10(max(rms, 1.0) / 32768.0))
    return env

def pct(vals, p):
    s = sorted(vals)
    return s[min(len(s) - 1, int(len(s) * p))]

def lvl(env, t):
    i = int(round(t / FRAME))
    return env[max(0, min(len(env) - 1, i))]

def start_edge(env, floor, onset_db, word_t, prev_end, pad):
    """Last quiet moment before the word's real onset, with a small pad."""
    lo = int(max(prev_end, word_t - 0.20) / FRAME)
    hi = int((word_t + 0.05) / FRAME)
    onset = word_t
    for i in range(lo, min(hi, len(env) - 3)):
        if all(env[i + k] >= floor + onset_db - (3 if k else 0) for k in range(3)):
            onset = i * FRAME
            break
    return max(prev_end + 0.01, onset - pad)

def end_edge(env, floor, tail_db, word_e, next_t, pad):
    """First quiet moment after the word's tail, with a small pad, never closer than 0.03 s to the next word."""
    i = int(max(0.0, word_e - 0.05) / FRAME)
    limit = int(next_t / FRAME)
    tail = word_e
    while i < min(limit, len(env) - 3):
        if all(env[i + k] < floor + tail_db for k in range(3)):
            tail = i * FRAME
            break
        i += 1
    else:
        tail = (word_e + next_t) / 2
    return min(next_t - 0.03, max(word_e, tail) + pad)

def main():
    ap = argparse.ArgumentParser(description="Suggest cut edges from the waveform (read only)")
    ap.add_argument("--wav", default="project/a.wav")
    ap.add_argument("--ingest", default="project/ingest.json")
    ap.add_argument("--a", type=int, help="index of the last word to KEEP before the removed part")
    ap.add_argument("--b", type=int, help="index of the first word to KEEP after the removed part")
    ap.add_argument("--at", type=float, help="check one time: print the level around it")
    ap.add_argument("--onset-db", type=float, default=9.0)
    ap.add_argument("--tail-db", type=float, default=6.0)
    ap.add_argument("--start-pad", type=float, default=0.03)
    ap.add_argument("--end-pad", type=float, default=0.02)
    a = ap.parse_args()
    env = load_env(a.wav)
    words = json.load(open(a.ingest))["words"]
    floor = pct(env, 0.10)
    voiced = [v for v in env if v > floor + 15]
    speech = pct(voiced, 0.5) if voiced else floor + 25
    print(f"noise floor {floor:.1f} dBFS, median speech level {speech:.1f} dBFS, {len(env)} frames of 10 ms")
    if a.at is not None:
        for k in range(-6, 7):
            t = a.at + k * FRAME
            bar = "#" * max(0, int((lvl(env, t) - floor) / 2))
            print(f"{t:8.2f}  {lvl(env, t):6.1f} dB  {bar}")
        q = lvl(env, a.at) < floor + 8
        print("QUIET: an edge here will not clip a word" if q else "LOUD: an edge here lands inside voiced sound")
    if a.a is not None and a.b is not None:
        wa, wb = words[a.a], words[a.b]
        e = end_edge(env, floor, a.tail_db, wa["e"], wb["t"], a.end_pad)
        prev_end = words[a.b - 1]["e"] if a.b - 1 >= 0 and a.b - 1 != a.a else wa["e"]
        s = start_edge(env, floor, a.onset_db, wb["t"], max(e, prev_end), a.start_pad)
        print(f"keep word {a.a} {wa['w']!r} (ends {wa['e']})  ->  cut END   {e:.3f}  (tail room {e - wa['e']:+.3f} s, level there {lvl(env, e):.1f} dB)")
        print(f"keep word {a.b} {wb['w']!r} (starts {wb['t']}) ->  cut START {s:.3f}  (head room {wb['t'] - s:+.3f} s, level there {lvl(env, s):.1f} dB)")
        print(f"silence left at this join in the finished video: {(e - wa['e']) + (wb['t'] - s):.3f} s")
        for name, t in (("end", e), ("start", s)):
            if lvl(env, t) >= floor + 8:
                print(f"WARNING: the {name} edge {t:.3f} is not quiet; the words touch or the timing is off, check by eye with --at")

main()
```

Reading the output:

- `tail room` and `head room` are the silences kept on each side of the join. Their sum is the silence left at the join in the finished video. Aim for 0.08 to 0.18 s for a tight edit (see the main skill for other choices).
- A WARNING line means the edge level is not quiet: the words touch, or the word time is off. Look at it with `--at` before sending the cut.
- The suggested numbers are not sent anywhere. You send them with the normal `cut` operation, and the server's own rule (no more than 0.03 s inside a word) still applies.
- The 16 kHz file cannot show clicks above 8 kHz. For a suspect join, extract a 48 kHz copy of that second from the original and look again.
