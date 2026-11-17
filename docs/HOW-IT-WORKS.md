# How the Agent Editor works

```
raw video ──ingest.py──▶ proxy, word transcript, silences, thumbnails (project/ingest.json)
                              │
                              ▼
agents (Claude Code) ──curl POST /api/op──▶ server.py  ──checks──▶ shared timeline (project/state.json)
                                                │
                       /api/events (live stream) ▼
                                        browser screen: media pool, transcript, roster, activity log,
                                        timeline lanes, one cursor per agent
                                                │
                                POST /api/render ▼
                                        render.py (ffmpeg + Pillow) ──▶ out/edit-<time>.mp4
```

## One shared timeline

All agents change the same timeline through one tiny HTTP API. The server holds the state, so agents never fight over
a window or a mouse. Each operation is checked before it is accepted:

| Operation | The server says NO when |
| --- | --- |
| `cut` | shorter than 0.4 s, overlaps a kept cut, or starts or ends inside a spoken word |
| `caption` | more than 3 words or 22 characters, longer than 3 s, overlaps another caption, or words not spoken at that time |
| `fx` | overlaps another effect, or two punch zooms are closer than 4 s |
| `graphic` | words not spoken within 2 s of it, closer than 0.5 s to another graphic, or more than 10 graphics |
| `reject` | the agent is not a reviewer, or there is no such accepted item |

A NO always comes with a reason. The agent reads it and sends a corrected operation. This is why a team of agents can
work fast without breaking the edit.

## What you see

The screen draws what the server accepted. When an agent works on a sentence, its cursor moves to that line in the
transcript; when it places a cut or a caption, its cursor moves to that spot on the timeline. The roster shows each
agent's role, its count of accepted edits and its count of refusals. The activity log lists every action.

You can also edit by hand: select a chip on the timeline and press Delete, zoom with the wheel, drag to pan, click to
seek, and press Space to play.

## Review and render

`Review` lists problems found across the whole edit (pauses left in, clipped sentences, overlaps). `Render` builds the
video from your original file at full quality: kept cuts joined with short audio fades, punch zooms, blur ins, graphics,
captions, optional music, loudness normalised to -16 LUFS with a -1 dBTP ceiling.

## Run it yourself

```
cd agent-editor
python3 -m venv .venv && .venv/bin/pip install pillow
python3 ingest.py YOUR_VIDEO.mp4 --start 0 --dur 100
.venv/bin/python server.py
```

Then open `http://127.0.0.1:8780`, and start your agents with `AGENT-BRIEF.md`. Or let Claude do all of it with the
skill `ae-run-multi-agent-edit`.
