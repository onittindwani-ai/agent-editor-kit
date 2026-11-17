---
name: ae-install-and-run
description: Installs and verifies everything the Agent Editor needs (Python 3, ffmpeg and ffprobe, a whisper command line tool that writes word timestamps, Pillow, optional Remotion), ingests a video, starts the editor server on 127.0.0.1:8780, runs health checks and fixes common errors. Use when the user says "install", "set it up", "run the editor", "start the server", "ingest my video", "port in use", "it does not start", "no transcript", or before any multi agent edit.
---

# ae-install-and-run: install, verify, ingest, start

Read `brand/profile.md`. If it is missing or a section it needs is empty, stop and run `ae-setup-interview` for that section (ask the user, with options), do not guess. This skill needs `## Rules` (laptop limits, working setup, cleanup policy) and `## Platforms and formats`.

Installing software changes the user's machine. Say what you will install before you install it, prefer a project local virtual environment, and never use `sudo` or system wide package managers without the user's yes for that command. Everything the editor does is local: the server binds to `127.0.0.1` only, so nothing is exposed to the network. Never change that.

## 1. What the editor consists of

| File | Role |
| --- | --- |
| `ingest.py` | prepares a video: 720p proxy, word level transcript, silences, sentences, a thumbnail every 2 s, writes `project/ingest.json` |
| `server.py` | the shared timeline and the HTTP API on port 8780, also serves the screen (`ui/index.html`) |
| `render.py` | builds the mp4 with ffmpeg and Pillow |
| `AGENT-BRIEF.md` | what every agent reads |
| `tests/test_ops.py` | unit tests of the operation rules |

## 2. Requirements and checks

Run each check and report the result in a small table before installing anything.

| Need | Check | Notes |
| --- | --- | --- |
| Python 3 | `python3 --version` | 3.9 or newer recommended. The server uses only the standard library. |
| ffmpeg and ffprobe | `ffmpeg -version`, `ffprobe -version` | Must include the `libx264` encoder: `ffmpeg -hide_banner -encoders \| grep libx264`, and the `aac` encoder. |
| Pillow (Python imaging) | `python3 -c "import PIL; print(PIL.__version__)"` | Draws captions and graphics at render. Needed for render, not for the server. |
| A whisper command line tool | `command -v mlx_whisper` or `command -v whisper` | Must write word level timestamps as JSON. See section 4. |
| A bold TrueType font | see section 6 | The renderer looks for a bold sans font file in three common places. |
| A modern browser | Chrome, Safari, Firefox or Edge | The page plays the proxy (h264 and aac). |
| Free disk | `df -h .` | Keep at least the amount in the profile (default 5 GB) free after the proxy, thumbnails and renders. |

### Install steps (confirm each command with the user first)

1. **ffmpeg.** macOS with Homebrew: `brew install ffmpeg`. Debian or Ubuntu: `sudo apt install ffmpeg` (the user runs this). Windows: a build from the official ffmpeg site, unpacked and added to the PATH (the user does this). After installing, run the two version checks again.
2. **Virtual environment and Pillow** (inside the `agent-editor/` folder):
   ```
   python3 -m venv .venv
   .venv/bin/pip install pillow
   ```
   On Windows the interpreter is `.venv\Scripts\python`. Use the venv interpreter for `server.py` so the render can import Pillow.
3. **A whisper tool** (section 4).
4. **Optional, richer graphics**: Remotion (section 7). Not needed for the editor.

## 3. Resource safety before heavy steps

Ingest (transcription and encoding) and render are heavy. Follow `ae-laptop-load-safety`:
- One heavy job at a time. Never ingest while a render runs.
- The scripts already start ffmpeg and the transcription with `nice -n 15` (low priority) and `-threads 4` or `-threads 2`. If the profile's laptop limit is 2 threads and the machine is light, tell the user it will be slower but safe.
- Check load and disk first: `uptime`, `df -h .`. If free disk is under the profile's limit, stop and tell the user.
- The agents themselves are light (they only send `curl`).

## 4. The whisper command

`ingest.py` calls: `<whisper> a.wav --model <model> --word-timestamps True --output-format json --output-dir project`, then reads `project/a.json` and expects `segments[].words[]` with `word`, `start` and `end`.

- **Apple silicon Mac**: `mlx_whisper` (from the `mlx-whisper` Python package) matches these flags and the default model name `mlx-community/whisper-large-v3-turbo`. Install into a venv: `.venv/bin/pip install mlx-whisper`.
- **The default whisper path inside `ingest.py` points into a cache folder that will most likely not exist on your machine.** Always pass your own: `--whisper "$(command -v mlx_whisper)"` or the venv path `.venv/bin/mlx_whisper`.
- **Other whisper tools** (for example the `openai-whisper` package with a `whisper` command): flag spellings and model names differ (it uses `--word_timestamps True` and model names like `small`). Check `whisper --help`. If the flags do not match, write a small wrapper script that accepts `<wav> --model X --word-timestamps True --output-format json --output-dir D`, calls the real tool with its own flags, and writes `D/a.json` in the shape above, then pass the wrapper to `--whisper`. Say plainly that you could not test the user's tool and verify with the ingest output counts (section 5).
- Model choice: a large model is more accurate and slower; a small model is fast but misspells names. Ask the user which they prefer when the machine is light; record it in `edit/run-log.md`.
- First run of a model downloads it (hundreds of MB to a few GB). Tell the user before it starts. Never download anything without their yes.

## 5. Ingest a video

Never edit the user's original: ingest reads it and writes only inside `project/`. If the original is on removable media, copy it to `footage/` first.

```
python3 ingest.py PATH_TO_VIDEO --whisper "$(command -v mlx_whisper)"            # whole file
python3 ingest.py PATH_TO_VIDEO --start 0 --dur 100 --whisper "$(command -v mlx_whisper)"   # an excerpt
```

Options: `--start S` start second, `--dur D` duration in seconds (0 or omitted means to the end), `--whisper PATH`, `--model NAME`.

What it makes (all inside `project/`):
- `source.mp4`: 720p, 30 fps, h264 high quality, a keyframe every second so the page can seek. Used for the screen. The render cuts from the ORIGINAL file when it still exists at the same path, so keep the original where it was.
- `a.wav` and `a.json`: mono 16 kHz audio for the transcript and the raw transcript.
- `thumbs/`: a small frame every 2 s.
- `ingest.json`: `media` (duration, size, origin path, origin start), `words` (`t`, `e`, `w`), `silences` (`s`, `e`, pauses of at least 0.3 s below about -34 dB), `sentences` (break at . ? ! or a gap over 0.6 s or 22 words), `thumbs`.
- It prints one line: `ok: 99.9s, 285 words, 14 silences, 17 sentences, 50 thumbs`.

Sanity checks after ingest:
1. Words per second = words divided by duration. Normal speech is about 2 to 3.5. Under 1.5 means a quiet or silent stretch or a failed transcript. Over 4.5 is suspicious.
2. Open `project/ingest.json` and read the first and last 20 words. Do they match what is said?
3. Silences: a talking video usually has several. Zero silences with hundreds of words means the threshold missed them or the audio has noise; tell `ae-audio-cleanup`.
4. If names or brand words are misspelled, fix them in `ingest.json` BEFORE any caption or graphic work (the editor only accepts caption and graphic words that match the transcript). See `ae-ingest-and-transcribe`.

New video, new project: `ingest.py` overwrites `project/ingest.json`, the proxy and the thumbnails but does not clear `project/state.json` (the old timeline). Before ingesting a different video, rename the old folder (for example `mv project project-<name>`) so old cuts and captions never attach to a new transcript.

## 6. Start the server

```
.venv/bin/python server.py                 # http://127.0.0.1:8780
.venv/bin/python server.py --port 8790     # another port
```

Environment variables (optional): `AGENT_EDITOR_PROJECT` (project folder, default `project/` next to `server.py`), `AGENT_EDITOR_OUT` (render output folder, default `out/`), `MUSIC_ROOT` (the folder music files are chosen from, see below).

At start it prints `Agent Editor on http://127.0.0.1:8780  (source 99.9s, 285 words)`. It also tries to draw four template preview images; if it prints "template previews not made", Pillow is missing or unusable (fix Pillow; harmless for the API).

Run the server in the background so the shell stays free, and keep its output in a log file under `edit/` so you can read errors. Open the page in a browser tab and leave it open: it shows the media pool, the transcript, the roster of agents, the activity log and the timeline lanes (cuts, graphics, captions, effects, music).

**Fonts.** `render.py` looks for a bold TrueType font at three paths: the macOS system Arial Bold, `/Library/Fonts/Arial Bold.ttf` and the DejaVu Sans Bold file on common Linux systems. If none exists (Windows, minimal Linux), Pillow falls back to a tiny bitmap font and captions look too small. Fix: edit the `FONTS` tuple near the top of `render.py` to point to a bold font file the user is licensed to use. `ae-theme-builder` then maps the user's chosen fonts into this tuple.

**Colours.** The shipped renderer draws with an amber and ink palette and a dark pill for captions. The user's colours are applied by `ae-theme-builder`. Say this honestly if the user asks why the first render is not on brand.

**Music folder.** The `music` operation accepts only files that exist inside `MUSIC_ROOT`. Set it to the folder the profile names under Sound (`Music library location`) before starting the server: `MUSIC_ROOT=music-folder .venv/bin/python server.py`. The kit bundles no music.

## 7. Optional: Remotion

The editor's four graphic templates are drawn with Pillow. For custom animated graphics outside the editor, a Remotion project (React code that renders video frames) is an option. Facts, hedged: Remotion needs Node.js and a recent browser engine it downloads itself; rendering is CPU heavy (see `ae-laptop-load-safety`); its licence is free for individuals and small teams but companies above a size threshold need a paid company licence, so read the current licence terms before commercial use and tell the user to do the same. Do not install it unless the user asks. Never import anyone else's templates or media.

## 8. Health checks (run all of these before saying it works)

```
curl -s http://127.0.0.1:8780/api/state | head -c 400          # JSON with agents, cuts, captions, render
curl -s http://127.0.0.1:8780/api/ingest | head -c 300         # media and the first words
curl -s 'http://127.0.0.1:8780/api/window?start=0&end=20' | head -c 400
curl -s http://127.0.0.1:8780/api/review                       # issues and stats (empty edit shows zero)
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8780/ # 200
.venv/bin/python -m unittest tests/test_ops.py                  # all tests pass
```

Smoke test of the API (only on a fresh project with no real edits, and only with the user's go, because `reset` clears the timeline):

```
curl -s -X POST http://127.0.0.1:8780/api/op -H 'Content-Type: application/json' -d '{"op":"hello","agent":"TEST","role":"cutter"}'
curl -s -X POST http://127.0.0.1:8780/api/op -H 'Content-Type: application/json' -d '{"op":"cut","agent":"TEST","start":1,"end":1.2}'   # expect ok:false, "at least 0.4 s"
curl -s -X POST http://127.0.0.1:8780/api/reset -H 'Content-Type: application/json' -d '{}'
```

If the NO message arrives with its reason, the rule engine works. Then look at the browser: the roster should show TEST before the reset. A command that exits cleanly proves nothing; look at the screen and the numbers.

## 9. Common errors

| Symptom | Cause | Fix |
| --- | --- | --- |
| `No video prepared yet. Run: python3 ingest.py ...` | `project/ingest.json` missing | Run ingest, or set `AGENT_EDITOR_PROJECT` to the right folder. |
| `Address already in use` | A server is already on 8780 | Use the running one, stop the old one, or pass `--port`. |
| `FileNotFoundError` for the whisper path | The default whisper path does not exist on this machine | Pass `--whisper` with your tool's path. |
| `FileNotFoundError` for `a.json` or `KeyError: 'words'` | The tool wrote another file name, or did not write word timestamps | Check the tool's flags; use a wrapper (section 4); upgrade the tool. |
| 0 words or very few words | Silent audio, wrong stream, or the tool failed quietly | Play the proxy; run `ffmpeg -i project/source.mp4 -af volumedetect -f null -`; try another model. |
| `ffmpeg` encoder error | ffmpeg built without `libx264` or `aac` | Install a full build. |
| `ModuleNotFoundError: No module named 'PIL'` at render | Server run with the wrong Python | Start the server with `.venv/bin/python`. |
| Render state `error`, text `no accepted cuts yet` | Nothing has been cut | Run cutters first. |
| Render fails with a font or drawing error | No usable font file | Section 6, fonts. |
| Browser shows a blank player | The proxy did not finish, or the browser blocks the codec | Re run ingest; try Chrome. |
| `music` op says `file must be a path inside the music library that exists` | `MUSIC_ROOT` points elsewhere | Restart the server with `MUSIC_ROOT` set; give a path relative to it. |
| Old edits appear on a new video | `state.json` from the old project | Move the old `project` folder aside before ingesting a new video. |
| The machine is slow or fans scream | Heavy job plus other apps | `ae-laptop-load-safety`; wait for the job; do not start another. |

## 10. Worked example (placeholder content)

User: "Install it and load my bakery video."
1. Checks: Python 3.11 yes; ffmpeg yes with libx264; Pillow missing; `mlx_whisper` missing; free disk 42 GB.
2. You say: "I will create a local virtual environment and install Pillow and mlx-whisper into it. The first transcription downloads a speech model (hundreds of MB). OK?" The user says yes.
3. Install, then ingest the file with `--whisper .venv/bin/mlx_whisper`. It prints `ok: 92.4s, 262 words, 11 silences, 15 sentences, 47 thumbs`. 262 / 92.4 = 2.8 words per second: normal.
4. First 20 words match the speech; "sourdough" appears as "sour dough" in two places: logged for `ae-ingest-and-transcribe`.
5. Start the server in the background, run the health checks and the tests, open the page, and report the numbers.

## Checklist

- [ ] Reported every requirement check before installing.
- [ ] Confirmed install commands with the user; nothing used `sudo` without a yes.
- [ ] Ingest used the user's whisper path and the original stayed untouched.
- [ ] Sanity checks on words per second, first and last words, silences done.
- [ ] Server listens only on 127.0.0.1; health checks and unit tests passed.
- [ ] Fonts and `MUSIC_ROOT` addressed, or told to the user as limits.
- [ ] Old project folder moved aside before a new video.

Hand off to: `ae-ingest-and-transcribe` (fix the transcript), `ae-run-multi-agent-edit` (start the agents), `ae-theme-builder` (apply the theme to the renderer), `ae-laptop-load-safety`, `ae-take-selection`.
