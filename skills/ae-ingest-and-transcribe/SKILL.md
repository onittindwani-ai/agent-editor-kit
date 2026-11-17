---
name: ae-ingest-and-transcribe
description: Prepares a video for the Agent Editor: probes the file, makes the 720p proxy, runs the word level transcript, silence detection, sentences and thumbnails with ingest.py, then checks the transcript quality and fixes spellings before any agent starts. Use when the user says "ingest this video", "transcribe my footage", "prepare the video for editing", "the transcript is wrong", "fix the spelling of names", or before any multi agent edit.
---

# Ingest and transcribe

Read `brand/profile.md`. If it is missing or a section this skill needs is empty, stop and run `ae-setup-interview` for that section (ask the user, with options), do not guess.

Sections used here: `## Business` (names, products and jargon that must be spelled right), `## Platforms and formats` (frame shape and target length), `## Rules` (what may be cut or changed).

Everything the agents see comes from one file, `project/ingest.json`. If it is wrong, every cut, caption and graphic built on it is wrong. This skill gets that file right once.

## Questions to ask the user

Ask them as one short list, before running anything.

1. Which part of the recording do you want to edit?
   a) The whole file. b) One excerpt (give me the start second and the length). c) Several excerpts, one at a time.
2. What language is spoken?
   a) English only. b) One other language (name it). c) Mixed languages (then see "Language limits").
3. Which names, brands, products and unusual words appear? Please give them spelled the way you want them on screen.
   a) I will list them now. b) They are in my profile. c) There are none.
4. Can I download a speech model if one is missing? It can be over a gigabyte and needs a network connection.
   a) Yes. b) Ask me again with the size. c) No, I will install it myself.

Never download anything without the answer to question 4.

## Step 0: probe the file (nothing is written)

Run these in the folder that holds the video. Replace `VIDEO` with the file name.

```
ffprobe -v error -show_format -show_streams -of json VIDEO
ffmpeg -hide_banner -i VIDEO -vn -af volumedetect -f null - 2>&1 | grep -E "mean_volume|max_volume"
```

Read the first output for: duration, number of video and audio streams, width, height, frame rate (`r_frame_rate` against `avg_frame_rate`: if they differ the video is variable frame rate, typical for phone footage), pixel format and colour tags (a 10 bit or HDR tag means the 720p proxy may look washed out), audio codec, channels, sample rate, and any rotation tag.

| Finding | What to do |
| --- | --- |
| No audio stream | Stop. There is nothing to transcribe. Ask the user for the right file |
| Two or more audio streams | Ask which one is the voice. The ingest lets ffmpeg choose the audio stream automatically (normally the first, or the one with the most channels). If the voice is on another track, make a copy of the file with that track first (`ffmpeg -i VIDEO -map 0:v -map 0:a:1 -c copy copy.mp4`, a new file) |
| `mean_volume` under -40 dB | The track is probably silent or the wrong one. Ask before continuing |
| `max_volume` of 0.0 dB | The recording clips. Note it for `ae-audio-cleanup` |
| Variable frame rate | Fine for the editor (the proxy and the render use 30 fps), but check lip sync on the first render |
| Rotation tag or a vertical file | Fine, the proxy is upright. Look at the first thumbnail to confirm |
| Longer than about 15 minutes | Ingest an excerpt first (question 1b). The screen draws a thumbnail every 2 s and every sentence, which gets heavy on long sources (starting value, verify on your machine) |

## Step 1: before you run ingest

1. One heavy job at a time. Transcription and the proxy encode are heavy. Do not run a render, a second ingest or a 4K encode at the same time (`ae-laptop-load-safety`). The script already runs with low priority.
2. Check free disk space. The proxy is roughly 10 to 25 MB per minute for a talking head; the 16 kHz mono wav is about 2 MB per minute (16000 samples per second, 2 bytes each); thumbnails are small.
3. The ingest always writes into the `project` folder next to `ingest.py`. It also empties `project/thumbs` and overwrites `ingest.json`, `source.mp4`, `a.wav` and `a.json`. If a `project` folder from an earlier video exists, move it to a new name first (a rename, never a delete): for example `project` to `project-bakery-take1`. That folder also holds the old timeline in `state.json`. One kit folder holds one project at a time.
4. The ingest reads `project/a.json` after whisper runs and does not check whisper's exit code. If whisper fails silently and an old `a.json` exists, you get the old transcript for the new video. Rename any existing `a.json` aside before running (moving the whole `project` folder, item 3 above, does this).
5. The default `--whisper` value points at a command that exists only on the machine it was written for. Always pass `--whisper` with the full path or name of the speech to text command that works on this machine (`which mlx_whisper` or the equivalent), and `--model` if the user wants another model.
6. The ingest passes flags in the style of `mlx_whisper`: `--model`, `--word-timestamps True`, `--output-format json`, `--output-dir`. Other whisper tools use other spellings (some use underscores). Test the command on a 10 second file first. If the flags differ, write a small wrapper script that accepts these flags and writes `a.json` in the same layout (`segments`, each with `words` holding `word`, `start`, `end`), and pass the wrapper as `--whisper`.

## Step 2: run it

```
python3 ingest.py VIDEO --start 0 --dur 100 --whisper WHISPER_COMMAND
```

`--start` and `--dur` take seconds and select the excerpt (omit `--dur` for the whole file). The render later cuts from the original file using the same start, so the excerpt is what you edit.

What the script does, in order, so you can tell where it failed:

| Stage | Output | Typical failure |
| --- | --- | --- |
| Proxy: 720 lines high, 30 fps, H.264 (CRF 21), AAC 160 kbit/s, keyframe every second, `project/source.mp4` | The proxy that the screen plays | ffmpeg not found, bad path, unreadable file. The script prints ffmpeg's message and stops |
| Audio for the transcript: mono, 16 kHz, `project/a.wav` | The audio all later analysis uses | none usually |
| Whisper with word timestamps, `project/a.json` | Words with start and end, rounded to 0.01 s | command not found (Python traceback), model missing or downloading, flags rejected (silent, see step 1.4) |
| Silences: ffmpeg `silencedetect` at -34 dB, minimum 0.3 s | `silences` list of `s` and `e` | none usually. A silence still open at the very end of the file is dropped |
| Sentences: break at `.` `?` `!`, or a gap over 0.6 s, or 22 words | `sentences` list | n/a |
| Thumbnails: one every 2 s, 240 px wide | `project/thumbs/t001.jpg` onward, first at time 0 | n/a |

It ends with a line like `ok: 33.4s, 98 words, 4 silences, 6 sentences, 17 thumbs`. Compare those numbers with what you expect. A 100 s talking head with 12 words is not a success.

## Step 3: check the transcript quality

You cannot hear audio, so check with numbers and then with thumbnails. Run the checker in `references/check-ingest.md` (standard library only):

```
python3 check_ingest.py project/ingest.json vocab.txt
```

It reports these flags. Read each one. Never fix by guessing.

| Flag | Meaning | What to do |
| --- | --- | --- |
| `rate` | Fewer than 1.2 or more than 4.5 words per second over the spoken span | Missed speech (low) or a loop (high). Re run with a larger model or an excerpt |
| `head`, `tail` | First word later than 2 s, or over 3 s of audio after the last word | Look at the first and last thumbnails and check the audio level in that region with the volume check below |
| `zero`, `long`, `overlap`, `order` | Words with no length, longer than 1.2 s, overlapping, out of order | Alignment trouble. A few are normal. Many in one area mean that area is unreliable. List the times for the cutters |
| `in_silence` | A word sits mostly inside a detected silence | A hallucinated word or poor alignment. Treat the area as unreliable |
| `silences` | Most gaps of 0.5 s or more have no silence entry | The room is noisy so the -34 dB threshold never triggers. Recompute (below) |
| `loop` | One word four times in a row, or one phrase four or more times | A classic whisper loop. Re run that excerpt |
| `tail_phrase` | The last words are "thank you" style closers | Common false tail text in silence. Ask the user if it was said |
| `vocab` | A word from the user's list is missing but a near spelling exists | Fix the spelling (below) |

Extra checks the script cannot do:

1. Look at three thumbnails, one near the start, one in the middle, one near the end (`curl -o` from `/project/thumbs/t001.jpg`, then view). Confirm the right video, orientation and framing.
2. Read the first and last 10 seconds of the transcript aloud against the script, if the user has an approved script (`ae-script-first-workflow`). The first words and the last words are where models fail most.
3. Compare the speech with the script: the transcript should contain every script sentence the user delivered. Missing sentences usually mean missed speech, not a missing delivery.
4. Numbers: transcripts may write "7" or "seven", "40 percent" or "40%". Graphics and captions can only use the transcript's own form, so decide the form once with the user and fix it in the transcript.

To list loud and quiet regions at a glance (a missing word shows as a loud region with no word on it), use the envelope helper in `ae-precise-audio-cut`.

## Step 4: fix spellings (safe, reversible)

Only spelling. Never insert, delete or reorder words, never "improve" grammar, never change a time.

1. Build the list of wrong spelling to the user's spelling from `## Business`, the user's answer to question 3, and the `vocab` flags. If a name has two plausible spellings, ask the user with the candidates as options.
2. Run `references/fix-spellings.md` in dry run mode. It prints every change with its time. Read the list.
3. Run it with `--apply`. It copies `ingest.json` to `ingest.json.before-spelling` first and then rewrites the word list and the sentence text.
4. Restart the server so it reads the fixed file. The timeline survives a restart because the server reloads `project/state.json`. Do not do this while agents are mid operation: finish the round, restart between rounds, tell the conductor.
5. Save the change list next to the project for the user (a plain text file).

Why this matters: captions and graphics are refused by the server unless every word appears in the transcript. A misspelled brand name in the transcript becomes a misspelled caption. A transcript that has "sour dough" blocks a graphic reading "sourdough".

Merging two transcript words into one (for example "sour dough" into "sourdough") is allowed when the user confirms the compound; the merged word keeps the first word's start and the last word's end.

## Recompute silences in a noisy room

The shipped threshold is -34 dB for 0.3 s, which suits a quiet room. For a noisy room, measure the noise floor first, then rerun detection a few dB above it:

```
ffmpeg -hide_banner -i project/a.wav -af silencedetect=noise=-28dB:d=0.25 -f null - 2>&1 | grep silence_
```

Convert the `silence_start` and `silence_end` pairs into the `silences` list (`s` and `e`, rounded to 0.01). Back up `ingest.json` before editing it, and restart the server. Note that the review pass of the editor treats silences over 0.35 s inside a kept cut as a problem, so over sensitive settings create false alarms.

## Language limits

The ingest has no language flag, so whisper chooses the language automatically from the start of the audio. Mixed language recordings can come out in the wrong language or as translations of parts. Tell the user. For a single non English language the model usually works but spelling checks (step 4) matter more. For mixed recordings, ingest each language stretch as its own excerpt with a wrapper that fixes the language.

Whisper family models often leave out filler sounds ("um", "uh") and stutters. That is not an error in the transcript, but it means fillers are invisible to the cutters. `ae-filler-and-restart-removal` shows how to find them from the audio.

## Worked example (neutral placeholder content)

A local bakery owner records a 95 second explainer on reviving a sourdough starter.

1. Probe: one video stream 1080 by 1920 at 30 fps, one audio stream, mean volume -21 dB, max -1.2 dB. Fine.
2. User answers: the whole file, English, names "Levain" and "sourdough", model download allowed.
3. Move the old `project` folder to `project-old-demo` (rename). Run:
   `python3 ingest.py bakery.mp4 --whisper mlx_whisper`
   Output: `ok: 95.2s, 238 words, 7 silences, 16 sentences, 48 thumbs`.
4. Checker: speaking rate 2.7 words per second (good); `vocab`: "Levain" missing, transcript has "levin" and "sour dough". `tail_phrase`: none. `in_silence`: none.
5. Fix list: `{"sour dough": "sourdough", "levin": "Levain"}`. Dry run shows 3 changes, apply, restart the server, tell the conductor the spelling log is saved.
6. Report to the conductor: 238 words, 2 spellings fixed, no flagged regions, speech starts at 0.4 s, noise is low so the default silences are fine.

## Checklist

- [ ] Profile read; the four questions answered; no download without a yes.
- [ ] Probe done; stream, audio level and frame rate recorded.
- [ ] Old `project` folder moved aside (not deleted); one heavy job at a time.
- [ ] `--whisper` passed explicitly and tested on a short file.
- [ ] The ingest summary line looks plausible for the duration.
- [ ] Quality checker run; every flag read and answered.
- [ ] Three thumbnails looked at.
- [ ] Spellings fixed with a backup, dry run first, server restarted between rounds.
- [ ] Numbers form agreed with the user.
- [ ] Report sent: counts, unreliable regions, spelling log.

## Do not

- Do not edit the user's original file. All derived files go under `project`.
- Do not edit word times. If the timing is poor, re run with a different model or tell the user.
- Do not run the ingest while the server is handling an edit round.
- Do not start the editor and agents before the checks are done.

Hand off to: `ae-take-selection` (when there are several takes), `ae-filler-and-restart-removal` (what the transcript leaves out), `ae-precise-audio-cut` (waveform checks on the same audio), `ae-install-and-run` (tools and server), `ae-laptop-load-safety` (heavy jobs), `ae-run-multi-agent-edit` (next step: the edit), `ae-audio-cleanup` (noise and clipping).
