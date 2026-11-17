#!/usr/bin/env python3
"""Ingest a video for the Agent Editor.

Usage: python3 ingest.py VIDEO [--start S] [--dur D] [--whisper PATH] [--model NAME]

Makes project/source.mp4 (a 720p proxy of the excerpt), a word level transcript, silences,
thumbnails every 2 s and project/ingest.json. Everything the agents see comes from this file.
Needs: ffmpeg, ffprobe and a whisper CLI that writes word timestamps (default: mlx_whisper).
"""
import argparse, json, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.join(HERE, "project")

def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--dur", type=float, default=0.0)
    ap.add_argument("--whisper", default=shutil.which("mlx_whisper") or "mlx_whisper")
    ap.add_argument("--model", default="mlx-community/whisper-large-v3-turbo")
    a = ap.parse_args()
    os.makedirs(os.path.join(PROJ, "thumbs"), exist_ok=True)
    src = os.path.join(PROJ, "source.mp4")
    cut = ["-ss", str(a.start)] if a.start else []
    if a.dur:
        cut += ["-t", str(a.dur)]
    # proxy: 720p high, h264 + aac, keyframes every 1 s so the browser can seek
    r = run(["nice", "-n", "15", "ffmpeg", "-v", "error", "-y", "-threads", "4", *cut, "-i", a.video,
             "-vf", "scale=-2:720,fps=30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-g", "30",
             "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-movflags", "+faststart", src])
    if r.returncode:
        sys.exit(r.stderr)
    info = json.loads(run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=width,height", "-of", "json", src]).stdout)
    dur = float(info["format"]["duration"])
    w = next(s["width"] for s in info["streams"] if "width" in s)
    h = next(s["height"] for s in info["streams"] if "height" in s)
    # audio for the transcript
    wav = os.path.join(PROJ, "a.wav")
    run(["ffmpeg", "-v", "error", "-y", "-threads", "2", "-i", src, "-vn", "-ac", "1", "-ar", "16000", wav])
    r = run(["nice", "-n", "15", a.whisper, wav, "--model", a.model, "--word-timestamps", "True",
             "--output-format", "json", "--output-dir", PROJ])
    tj = json.load(open(os.path.join(PROJ, "a.json")))
    words = []
    for s in tj["segments"]:
        for x in s.get("words", []):
            t = x["word"].strip()
            if t:
                words.append({"t": round(x["start"], 2), "e": round(x["end"], 2), "w": t})
    # silences
    r = run(["ffmpeg", "-hide_banner", "-threads", "2", "-i", wav, "-af", "silencedetect=noise=-34dB:d=0.3", "-f", "null", "-"])
    starts = [float(m) for m in re.findall(r"silence_start: ([0-9.]+)", r.stderr)]
    ends = [float(m) for m in re.findall(r"silence_end: ([0-9.]+)", r.stderr)]
    silences = [{"s": round(s, 2), "e": round(e, 2)} for s, e in zip(starts, ends)]
    # sentences (break on . ? ! or a gap over 0.6 s)
    sents, cur = [], []
    for i, x in enumerate(words):
        cur.append(x)
        gap = (words[i + 1]["t"] - x["e"]) if i + 1 < len(words) else 9
        if re.search(r"[.?!]$", x["w"]) or gap > 0.6 or len(cur) >= 22:
            sents.append({"id": len(sents), "start": cur[0]["t"], "end": cur[-1]["e"], "text": " ".join(c["w"] for c in cur)})
            cur = []
    if cur:
        sents.append({"id": len(sents), "start": cur[0]["t"], "end": cur[-1]["e"], "text": " ".join(c["w"] for c in cur)})
    # thumbnails
    for f in os.listdir(os.path.join(PROJ, "thumbs")):
        os.remove(os.path.join(PROJ, "thumbs", f))
    run(["nice", "-n", "15", "ffmpeg", "-v", "error", "-y", "-threads", "2", "-i", src, "-vf", "fps=1/2,scale=240:-2", "-q:v", "5",
         os.path.join(PROJ, "thumbs", "t%03d.jpg")])
    n = len(os.listdir(os.path.join(PROJ, "thumbs")))
    thumbs = [{"t": i * 2.0, "file": f"project/thumbs/t{i + 1:03d}.jpg"} for i in range(n)]
    out = {"media": {"file": "project/source.mp4", "duration": round(dur, 3), "w": w, "h": h, "origin": os.path.basename(a.video), "origin_path": os.path.abspath(a.video), "origin_start": a.start},
           "words": words, "silences": silences, "sentences": sents, "thumbs": thumbs}
    json.dump(out, open(os.path.join(PROJ, "ingest.json"), "w"))
    print(f"ok: {dur:.1f}s, {len(words)} words, {len(silences)} silences, {len(sents)} sentences, {n} thumbs")

if __name__ == "__main__":
    main()
