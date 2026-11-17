# QA commands (read only)

Every command reads files and writes only pictures or text under `project/qa/` (make that folder first). Use absolute or project relative paths; the shell may reset its folder between calls. Run one heavy job at a time (`ae-laptop-load-safety`), with `nice -n 15` in front of ffmpeg and `-threads 4` for decoding heavy sources.

Replace `out/edit.mp4` with the render and `T` with a time in seconds.

## Stills and strips

```
mkdir -p project/qa
ffmpeg -v error -y -ss T -i out/edit.mp4 -frames:v 1 project/qa/still-T.png
ffmpeg -v error -y -i out/edit.mp4 -t 1.5 -vf "fps=10,scale=216:-1,tile=5x3" project/qa/first-1.5s.png
ffmpeg -v error -y -sseof -0.5 -i out/edit.mp4 -vf "fps=10,scale=216:-1,tile=5x1" project/qa/last-0.5s.png
ffmpeg -v error -y -ss 2.8 -t 0.6 -i out/edit.mp4 -vf "fps=30,scale=216:-1,tile=9x2" project/qa/window-2.8.png
ffmpeg -v error -y -i out/edit.mp4 -vf "fps=3,scale=270:-1,tile=8x6" project/qa/contact-sheet.png
```

For a window start use T minus 0.2 (not below 0). `tile=9x2` holds 18 frames, enough for 0.6 s at 30 fps. For a long video split the contact sheet into several pictures with `-ss` and `-t` so each tile stays readable.

Seam pair (the end of one clip and the start of the next):

```
ffmpeg -v error -y -sseof -0.04 -i clipA.mp4 -frames:v 1 project/qa/seam-a.png
ffmpeg -v error -y -i clipB.mp4 -frames:v 1 project/qa/seam-b.png
```

## Audio

```
ffmpeg -nostats -i out/edit.mp4 -af ebur128=peak=true -f null - 2>&1 | sed -n '/Summary:/,$p'
```

Read `I:` (integrated loudness, LUFS), `LRA:` and `Peak:` under True peak (dBFS, treated as dBTP). Targets come from `## Sound` and `ae-loudness-mastering`.

```
ffmpeg -nostats -i out/edit.mp4 -af silencedetect=noise=-40dB:d=0.25 -f null - 2>&1 | grep silence_
```

Lists silences of 0.25 s or more; compare with the cut list.

## Video

```
ffmpeg -nostats -i out/edit.mp4 -vf blackdetect=d=0.05:pix_th=0.10 -an -f null - 2>&1 | grep black_
ffmpeg -nostats -i out/edit.mp4 -vf freezedetect=n=-60dB:d=1 -an -f null - 2>&1 | grep freeze_
```

Black frames inside a talking video are almost always a bug at a transition. A freeze over 1 s may be a held card on purpose: look at it.

## Specs and sync

```
ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,width,height,pix_fmt,r_frame_rate,color_range,color_space,duration -of compact out/edit.mp4
ffprobe -v error -select_streams a:0 -show_entries stream=codec_name,sample_rate,channels,duration -of compact out/edit.mp4
ffprobe -v error -show_entries format=duration,size -of compact out/edit.mp4
```

Audio and video durations within 0.1 s. `faststart` means the `moov` atom is near the start of the file: `ffprobe -v trace out/edit.mp4 2>&1 | grep -m2 -E "type:'(moov|mdat)'"` should list `moov` before `mdat`.

## Stale export and editor counts

```
test out/edit.mp4 -nt project/state.json && echo "render is newer than the last edit" || echo "STALE: edit after render"
curl -s http://127.0.0.1:8780/api/review
```

Compare the counts the review reports (captions, graphics, fx) with those in the render's printed summary.

## Originals unchanged

At ingest record the hashes: `shasum -a 256 /absolute/path/to/original.mp4 > project/original.sha256`. At QA: `shasum -a 256 -c project/original.sha256` must print OK.

## Word check on the render

Transcribe the render with the same whisper command line tool the project uses for ingest (word timestamps, JSON output into `project/qa/`), build the expected words file (the approved script lines that remain in the cut, or the accepted caption texts in time order), then:

```
python3 brand/tools/word_check.py project/qa/expected.txt project/qa/render.json
```

```python
# file: word_check.py
#!/usr/bin/env python3
"""Compare the words that should be heard with a transcript of the rendered video.

    python3 word_check.py expected.txt render-transcript.json [--max-report 40]

expected.txt: the words the final cut should contain (for example the accepted caption texts in time order, one per line, or the
approved script lines that were kept). render-transcript.json: the word level transcript of the RENDER made with the same whisper tool
the project uses (a JSON with segments, each with words that have word, start, end). Words are compared lowercase without punctuation.
Output: missing words (expected, not heard), extra words (heard, not expected) with times, and a match percentage. Exit code 0 when
the match is 97 percent or more and no run of 3 or more consecutive words is missing, 1 otherwise, 2 for unreadable input.
Standard library only. A mismatch is a pointer: listen to the time listed, then fix the cut or the spelling.
"""
import argparse, difflib, json, re, sys


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("expected")
    ap.add_argument("transcript")
    ap.add_argument("--max-report", type=int, default=40)
    a = ap.parse_args(argv)
    try:
        exp = [norm(w) for w in open(a.expected, encoding="utf-8").read().split()]
        exp = [w for w in exp if w]
        tj = json.load(open(a.transcript, encoding="utf-8"))
        heard = []
        for seg in tj.get("segments", []):
            for x in seg.get("words", []):
                n = norm(x.get("word", ""))
                if n:
                    heard.append((n, float(x.get("start", 0.0))))
    except (OSError, ValueError) as e:
        print("cannot read input:", e)
        return 2
    hw = [h[0] for h in heard]
    sm = difflib.SequenceMatcher(None, exp, hw, autojunk=False)
    missing, extra, worst_run = [], [], 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag in ("delete", "replace"):
            missing.append((i1, exp[i1:i2], heard[j1][1] if j1 < len(heard) else None))
            worst_run = max(worst_run, i2 - i1)
        if tag in ("insert", "replace"):
            extra.append((heard[j1][1], hw[j1:j2]))
    matched = sum(b.size for b in sm.get_matching_blocks())
    pct = 100.0 * matched / max(1, len(exp))
    print("expected %d words, heard %d, matched %.1f percent" % (len(exp), len(hw), pct))
    for i, words, t in missing[:a.max_report]:
        print("MISSING near word %d (heard around %s s): %s" % (i, "%.2f" % t if t is not None else "end", " ".join(words)))
    for t, words in extra[:a.max_report]:
        print("EXTRA at %.2f s: %s" % (t, " ".join(words)))
    ok = pct >= 97.0 and worst_run < 3
    print("OK" if ok else "CHECK: listen to the times above")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
```

## Negative controls (do once per project)

| Tool | Feed it | It must |
| --- | --- | --- |
| `word_check.py` | An expected file with one extra word | Report one MISSING |
| `check_caption_groups.py` | A state file with a 4 word caption | Print an ERROR |
| `graphic_plan_check.py` | A stat card at 0.10 on a 1080 by 1920 frame | Print a PROBLEM |
| `scan_top_band.py` | A busy test pattern | Flag the top band |
| `theme_tokens.py` | A pale yellow accent on cream | Print a FAIL |
| `blackdetect` | A clip with one black second | List it |
