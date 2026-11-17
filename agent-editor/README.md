# Agent Editor

A video editor built for AI agents. Many agents (Claude Code subagents, or any program that can run `curl`) edit one
shared timeline at the same time, and a web screen shows every agent's cursor and every edit as it happens. When the
edit is ready, one click renders a real mp4.

## Why it exists

An agent that drives a normal browser is one actor in one tab and acts slowly. Agent Editor takes the opposite
approach: the timeline lives in a small server with a tiny API, so as many agents as you like can edit together
from a single open tab, each with its own cursor.

## How it works

- Agents read the transcript and decide cuts, captions, motion graphics and effects themselves.
- The server checks every operation and answers OK or NO with a reason. A cut cannot start inside a spoken word or
  overlap a kept part. A caption is 1 to 3 words taken only from the transcript. Two punch zooms are at least 4 s
  apart. Only a reviewer can reject. An agent that gets a NO reads the reason and fixes its work.
- The screen draws what the server accepted: media pool, transcript, an agent roster, an activity log and a
  multi-track timeline with zoom.
- Render builds an mp4 with ffmpeg: kept cuts joined with short audio fades, punch zooms, captions, graphics,
  optional music, loudness normalised to -16 LUFS.

## Run it

Needs Python 3, ffmpeg and a whisper command line tool that writes word timestamps (default `mlx_whisper`, change it
with `--whisper`).

```
python3 -m venv .venv && .venv/bin/pip install pillow          # Pillow draws the captions
python3 ingest.py YOUR_VIDEO.mp4 --start 0 --dur 100            # proxy, transcript, silences, thumbnails
.venv/bin/python server.py                                      # http://127.0.0.1:8780
```

Open the page, then start your agents. Give each one `AGENT-BRIEF.md` and a role (cutter, captioner, effects,
graphics, reviewer) with its own time window. Use Review to list problems found in the edit and Render for the mp4.

## API

`POST /api/op` with `op` in `hello`, `claim`, `cut`, `caption`, `fx`, `graphic`, `music`, `reject`, `done`.
`GET /api/window`, `/api/review`, `/api/state`, `/api/rejections`, `/api/events` (live stream).
`POST /api/render`, `POST /api/reset`. The full operation table is in `AGENT-BRIEF.md`.

## Files

`ingest.py` prepares a video. `server.py` is the shared timeline and the API. `render.py` builds the mp4.
`ui/index.html` is the screen. `AGENT-BRIEF.md` is what each agent reads. `tests/` checks the operation rules:

```
.venv/bin/python -m unittest tests/test_ops.py
```

## Honest limits

This is a focused tool for multi agent editing, not a replacement for a full editor such as Palmier Pro or Adobe
After Effects: there is no colour grading, no keyframe curve editor and a small set of graphic templates. Each
agent decision takes seconds because the agent is thinking, so quality and speed depend on the model and on the
transcript. Check every result before you publish it.
