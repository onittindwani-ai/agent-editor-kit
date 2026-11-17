# Join rehearsal: an audio only preview of every join (prints a command, runs nothing)

The editor's render builds the video by cutting the original and joining the kept parts with 12 ms audio fades. You can rehearse exactly that for the audio alone, without any video render and without any export, then transcribe the result once and compare it with the words you expect. Every difference near a join is a clipped, doubled or missing word.

Steps:

1. Make the scratch folder: `mkdir -p work`.
2. Run the script below. It prints one ffmpeg command, the list of joins with the silence left at each, and writes the expected words to `work/join-expected.txt`.
3. Run the printed command (one heavy job at a time, it is light: audio only, a few seconds).
4. Transcribe `work/join-check.wav` with the same whisper command and settings as the ingest, in JSON with word timestamps.
5. Run the script again with `--compare` and the whisper JSON.

```
python3 join_rehearsal.py
python3 join_rehearsal.py --compare work/join-check.json
```

```python
import argparse, difflib, json, re, shlex, sys, urllib.request

norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())

def load(src):
    return json.load(urllib.request.urlopen(src)) if src.startswith("http") else json.load(open(src))

ap = argparse.ArgumentParser(description="Audio only rehearsal of the joins (prints a command, runs nothing)")
ap.add_argument("--state", default="http://127.0.0.1:8780/api/state")
ap.add_argument("--ingest", default="project/ingest.json")
ap.add_argument("--wav", default="project/a.wav")
ap.add_argument("--out", default="work/join-check.wav")
ap.add_argument("--expected", default="work/join-expected.txt")
ap.add_argument("--compare", help="a whisper json of the rehearsal wav: compare it with the expected words")
a = ap.parse_args()

state = load(a.state)
ing = json.load(open(a.ingest))
cuts = sorted((c for c in state["cuts"] if c["status"] == "ok"), key=lambda c: c["start"])
words = ing["words"]

def inside(c):
    return [w for w in words if c["start"] <= (w["t"] + w["e"]) / 2 <= c["end"]]

expected = [norm(w["w"]) for c in cuts for w in inside(c) if norm(w["w"])]

if a.compare:
    wj = json.load(open(a.compare))
    heard = [norm(x["word"]) for s in wj["segments"] for x in s.get("words", []) if norm(x["word"])]
    sm = difflib.SequenceMatcher(a=expected, b=heard, autojunk=False)
    bad = 0
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op != "equal":
            bad += 1
            print(f"{op:8} expected {expected[max(0,i1-3):i2+3]}  heard {heard[max(0,j1-3):j2+3]}")
    print(f"similarity {sm.ratio():.3f}; {bad} differences. Each difference near a join is a clipped, doubled or missing word: look at it with snap_edges --at.")
    sys.exit(0)

parts, labels, out_t, joins = [], [], 0.0, []
for i, c in enumerate(cuts):
    d = c["end"] - c["start"]
    parts.append(f"[0:a]atrim=start={c['start']}:end={c['end']},asetpts=PTS-STARTPTS,"
                 f"afade=t=in:d=0.012,afade=t=out:st={max(0, d - 0.012):.3f}:d=0.012[a{i}]")
    labels.append(f"[a{i}]")
    out_t += d
    if i < len(cuts) - 1:
        wa, wb = inside(c), inside(cuts[i + 1])
        gap = (c["end"] - wa[-1]["e"]) + (wb[0]["t"] - cuts[i + 1]["start"]) if wa and wb else None
        joins.append((round(out_t, 2), c["id"], cuts[i + 1]["id"], None if gap is None else round(gap, 3)))
graph = ";".join(parts) + ";" + "".join(labels) + f"concat=n={len(cuts)}:v=0:a=1[out]"
cmd = ["nice", "-n", "15", "ffmpeg", "-v", "error", "-y", "-threads", "2", "-i", a.wav, "-filter_complex", graph, "-map", "[out]", a.out]
print("# 1. run this once (audio only, light, a scratch file, not a deliverable):")
print(" ".join(shlex.quote(x) for x in cmd))
print("# 2. transcribe", a.out, "with the same whisper command and settings as the ingest (one heavy job at a time)")
print("# 3. compare:  python3 join_rehearsal.py --compare <whisper json>")
print("# joins in finished time (seconds, from cut, to cut, silence left at the join):")
for j in joins:
    flag = "  LONG" if j[3] is not None and j[3] > 0.35 else ""
    print("#  ", j, flag)
import os
os.makedirs(os.path.dirname(a.expected) or ".", exist_ok=True)
open(a.expected, "w").write(" ".join(expected))
```

Notes:

- The rehearsal uses `project/a.wav`, which came from the 720p proxy's audio, so it is a close copy of what the render does, not a bit exact one. The render cuts the original file. A problem that shows here will show there.
- The words compared are the ingest words whose midpoint falls inside each kept cut. If the ingest is wrong at a place, the comparison is wrong there too.
- This is a scratch file, not a deliverable. It is not an export, and it needs no green light. Keep it out of the user's delivery folder.
