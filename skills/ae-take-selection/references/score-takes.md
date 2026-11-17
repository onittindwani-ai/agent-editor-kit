# Take scoring helper (read only)

Save as `score_takes.py`. It compares the transcript and audio of each take with the approved script and prints a score table and the raw numbers. Standard library only. It changes nothing and never touches the original takes.

Folder layout it expects: `takes/analysis/<take>.json` (a whisper word timestamp JSON of that take) and `takes/analysis/<take>.wav` (the same take as 16 kHz mono wav). Make the wav with ffmpeg from a copy path, one take at a time:

```
ffmpeg -v error -y -threads 2 -i TAKE_FILE -vn -ac 1 -ar 16000 takes/analysis/take1.wav
```

Then transcribe each wav with the same whisper command and flags as the ingest (one heavy job at a time) and save the JSON as `takes/analysis/take1.json`.

```
python3 score_takes.py --script approved-script.txt --pace 2.2-3.2 --picture take1=8,take2=6
```

`--pace` is the user's target in words per second (from the profile; the default is 2.2 to 3.2). `--picture` is a manual score from 0 to 10 for each take, from your look at stills (see the main skill). Without it the total is computed from the measurable parts only and marked "picture not scored yet".

```python
import argparse, array, difflib, json, math, os, re, statistics, sys, wave

norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
FILLERS = {"um", "umm", "uh", "uhm", "er", "erm", "ah", "hmm"}
clamp = lambda x: max(0.0, min(1.0, x))

def read_wav(path):
    w = wave.open(path, "rb")
    data = array.array("h"); data.frombytes(w.readframes(w.getnframes()))
    if sys.byteorder == "big": data.byteswap()
    return data, w.getframerate()

def levels(data, sr, frame=0.01):
    n = int(sr * frame)
    return [20 * math.log10(max(math.sqrt(sum(s * s for s in data[i:i + n]) / n), 1.0) / 32768.0) for i in range(0, len(data) - n + 1, n)]

def pct(v, p):
    s = sorted(v); return s[min(len(s) - 1, int(len(s) * p))]

def words_of(path):
    j = json.load(open(path))
    return [{"t": x["start"], "e": x["end"], "w": x["word"].strip()} for s in j["segments"] for x in s.get("words", []) if x["word"].strip()]

def score(stem, script_toks, folder, pace_lo, pace_hi, picture):
    words = words_of(os.path.join(folder, stem + ".json"))
    toks = [norm(w["w"]) for w in words if norm(w["w"])]
    data, sr = read_wav(os.path.join(folder, stem + ".wav"))
    lv = levels(data, sr)
    floor = pct(lv, 0.10)
    voiced = [v for v in lv if v > floor + 15]
    speech = pct(voiced, 0.5) if voiced else floor
    peak = max(abs(s) for s in data) / 32768.0
    clipped = sum(1 for s in data if abs(s) >= 32440)
    sm = difflib.SequenceMatcher(a=script_toks, b=toks, autojunk=False)
    matched = sum(b.size for b in sm.get_matching_blocks())
    coverage = matched / max(1, len(script_toks))
    extras = (len(toks) - matched) / max(1, len(toks))
    fill = sum(1 for t in toks if t in FILLERS)
    dbl = sum(1 for i in range(1, len(toks)) if toks[i] == toks[i - 1])
    cut = sum(1 for w in words if w["w"].endswith(("-", "\u2014", "...")))
    dis = (fill + dbl + cut) / max(1, len(toks)) * 100
    pauses = sum(1 for a, b in zip(words, words[1:]) if b["t"] - a["e"] >= 0.6)
    span = max(0.1, words[-1]["e"] - words[0]["t"])
    pace = len(toks) / span
    head, tail = words[0]["t"], len(data) / sr - words[-1]["e"]
    snr = speech - floor
    p_fid = 30 * clamp((coverage - 0.80) / 0.19) - 10 * clamp(extras / 0.2)
    p_clean = max(0.0, 25 - 3 * dis - 3 * pauses)
    p_audio = max(0.0, 20 * clamp((snr - 20) / 25) - (6 if clipped > 10 else 0) - (4 if speech < -30 else 0))
    p_pace = max(0.0, 10 - 3 * (max(0, pace_lo - pace, pace - pace_hi) / 0.3))
    p_hand = (2.5 if head >= 0.4 else 0) + (2.5 if tail >= 0.5 else 0)
    p_pic = picture
    parts = [max(0.0, p_fid), p_clean, p_audio, p_pace, p_hand] + ([p_pic] if p_pic is not None else [])
    maxp = 30 + 25 + 20 + 10 + 5 + (10 if p_pic is not None else 0)
    return dict(stem=stem, total=100 * sum(parts) / maxp, fid=parts[0], clean=p_clean, audio=p_audio, pace_pts=p_pace, hand=p_hand,
                pic=p_pic, coverage=coverage, extras=extras, dis=dis, pauses=pauses, pace=pace, snr=snr, speech=speech, floor=floor,
                peak=peak, clipped=clipped, head=head, tail=tail, partial=p_pic is None)

def main():
    ap = argparse.ArgumentParser(description="Score takes against the approved script (read only)")
    ap.add_argument("--script", required=True, help="the approved spoken script, plain text")
    ap.add_argument("--folder", default="takes/analysis", help="holds <take>.json (whisper word json) and <take>.wav (16 kHz mono)")
    ap.add_argument("--pace", default="2.2-3.2", help="target words per second, from the profile")
    ap.add_argument("--picture", default="", help="manual picture scores 0-10, for example take1=8,take2=6")
    a = ap.parse_args()
    script_toks = [t for t in (norm(x) for x in open(a.script).read().split()) if t]
    lo, hi = (float(x) for x in a.pace.split("-"))
    pic = {k: float(v) for k, v in (p.split("=") for p in a.picture.split(",") if p)}
    stems = sorted(f[:-5] for f in os.listdir(a.folder) if f.endswith(".json") and os.path.exists(os.path.join(a.folder, f[:-5] + ".wav")))
    rows = sorted((score(s, script_toks, a.folder, lo, hi, pic.get(s)) for s in stems), key=lambda r: -r["total"])
    print(f"{'take':16}{'score':>6}{'script':>8}{'clean':>7}{'audio':>7}{'pace':>6}{'handles':>8}{'picture':>8}")
    for r in rows:
        print(f"{r['stem']:16}{r['total']:6.1f}{r['fid']:8.1f}{r['clean']:7.1f}{r['audio']:7.1f}{r['pace_pts']:6.1f}{r['hand']:8.1f}{('-' if r['pic'] is None else format(r['pic'], '.1f')):>8}")
    print()
    for r in rows:
        print(f"{r['stem']}: coverage {r['coverage']:.2f}, extra words {r['extras']:.2f}, disfluencies {r['dis']:.1f} per 100 words, pauses over 0.6 s {r['pauses']}, "
              f"pace {r['pace']:.2f} w/s, level {r['speech']:.0f} dBFS over a floor of {r['floor']:.0f} (gap {r['snr']:.0f} dB), peak {r['peak']:.2f}, "
              f"clipped samples {r['clipped']}, head {r['head']:.2f} s, tail {r['tail']:.2f} s" + (", picture not scored yet" if r["partial"] else ""))
    print("\nNumbers only. A person decides: eyes, energy, and anything that cannot be measured.")

main()
```

Weights (points out of 100): script match 30, clean delivery 25, audio 20, pace 10, handles 5, picture 10. They are starting values. If the user says picture matters more than anything, change the weights in the script and say so in the report.

What the numbers mean and where they fail:

- Script match is measured on spoken words in order. Names the model spells differently will cost points. Fix spellings first (`ae-ingest-and-transcribe`) or compare after normalising.
- Disfluencies are counted from the transcript only. Whisper family models often leave out fillers, so a take full of "um" may look clean. Check the audio with `ae-filler-and-restart-removal`.
- Audio points use the gap between median speech level and the noise floor (about 45 dB or more is clean, under 25 dB is poor), clipping and a very low level. They cannot hear hum, echo or room tone.
- The score ranks takes. It does not choose. Show the top two with the numbers and let the user decide.
