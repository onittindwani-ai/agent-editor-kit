---
name: ae-take-selection
description: Chooses the best take, or the best take for each part, from several raw takes of the same script using a scored, evidence based method (script match, clean delivery, audio, pace, handles, picture), then builds one source file for the editor. Use when the user has several takes, says "pick the best take", "which take is better", "combine my takes", "I filmed it three times", or before ingesting footage that exists in more than one version.
---

# Take selection

Read `brand/profile.md`. If it is missing or a section this skill needs is empty, stop and run `ae-setup-interview` for that section (ask the user, with options), do not guess.

Sections used here: `## Script preferences` (the approved script and its target length), `## Voice and tone` (pace and energy the user wants), `## Platforms and formats` (frame, length limit), `## Rules` (anything about mixing takes or on camera conduct).

The editor works on one source video. When the user filmed several takes, someone has to decide which one (or which parts of which) becomes that source. You are that someone, but you recommend and the user chooses. You can measure a lot from transcripts, audio and stills. You cannot hear tone or judge a face, so the numbers narrow the list and the user decides the last step.

## Questions to ask the user

Ask them as one short list.

1. What decides it for you?
   a) The cleanest delivery (fewest stumbles).
   b) The best energy and personality, even if less clean.
   c) The best picture and lighting.
   d) A balance (use the default weights).
2. May I combine parts of different takes?
   a) No, one take only. b) Yes, at the start of a new idea only (recommended). c) Yes, anywhere the script allows, I accept visible jumps. d) Only if the framing matches closely.
3. Which pace do you want? (words per second of speech)
   a) Relaxed, about 2.0 to 2.6. b) Conversational, about 2.4 to 3.2 (default). c) Brisk, about 3.0 to 3.8. d) Use my profile.
4. Is the approved script final? Takes can only be scored against a final script (`ae-script-first-workflow`). If it is not approved, stop and ask the user to approve it first.

## What you may change

You never edit, rename, move or delete the user's original takes. Everything you make goes in a work folder next to the project: `takes/analysis` (transcripts, wavs, scores), `takes/stills` (frames to look at), `takes/selection.md` (your decision), and the assembled source if you build one. Rejected takes stay on disk exactly where they were.

## Step 1: inventory

1. List every take with name, duration, resolution, frame rate, audio streams, file size. Use `ffprobe -v error -show_format -show_streams -of json FILE` (see `ae-ingest-and-transcribe` for how to read it).
2. Check they are the same kind of recording: same resolution and frame rate, same audio sample rate, same orientation. If they are not, note it. Combining mismatched takes needs a conversion step (below).
3. Write the table into `takes/selection.md`. Mark takes that stop mid sentence, clap or slate at the start, or obviously start over.

## Step 2: transcribe each take once

One heavy job at a time, with low priority (`ae-laptop-load-safety`). For each take, one by one:

1. Extract audio: `ffmpeg -v error -y -threads 2 -i TAKE -vn -ac 1 -ar 16000 takes/analysis/<take>.wav`.
2. Transcribe the wav with the same whisper command, model and flags as the ingest, JSON with word timestamps, into `takes/analysis/<take>.json`.
3. Never run two transcriptions at once. If a take is under 20 seconds you may batch the extraction, not the transcription.

## Step 3: measure and score

Run the helper in `references/score-takes.md`:

```
python3 score_takes.py --script approved-script.txt --pace 2.4-3.2 --picture take1=8,take2=6
```

The components:

| Part | Points | Measured from | Good | Poor |
| --- | --- | --- | --- | --- |
| Script match | 30 | the share of script words found in order in the transcript, minus extra words | 0.97 or more matched, under 5 percent extra | under 0.85 matched |
| Clean delivery | 25 | fillers, doubles and broken words per 100 words, plus pauses over 0.6 s | under 2 per 100 words, no long pauses | over 6 per 100 words |
| Audio | 20 | gap between median speech level and noise floor, clipping, level | 45 dB gap or more, no clipping, speech louder than -30 dBFS | under 25 dB gap, clipping |
| Pace | 10 | words per second over the spoken span | inside the user's range | 0.6 w/s outside it or more |
| Handles | 5 | silence before the first word and after the last | 0.4 s or more before, 0.5 s or more after | the take starts or ends on speech |
| Picture | 10 | your look at stills (below), a manual 0 to 10 | steady, well lit, face clear, eye line consistent | blur, flicker, face cut off |

Weights are starting values. If the user chose "best energy" or "best picture", shift 10 points toward that part in the script and say so in the report.

## Step 4: look at the picture (manual, with evidence)

For each take that scored above 60 on the measurable parts, extract stills with ffmpeg: the first frame, the frame at 25, 50 and 75 percent, and the last frame.

```
ffmpeg -v error -y -ss 12.0 -i TAKE -frames:v 1 -vf scale=640:-2 takes/stills/take1-12s.jpg
```

Look at them (if you cannot view images, ask the user to look and score). Score from the checklist: face fully in frame and not cut by the edge, eyes toward the lens, exposure steady (no flicker between stills), background tidy and the same in all stills, nothing entering the frame, no motion blur in the face, hands and gestures in frame. Each failed item costs 1 to 2 points out of 10. Write the evidence in `takes/selection.md`: which still, what you saw.

Optional light measurement for exposure steadiness: `ffmpeg -hide_banner -i TAKE -vf "fps=1,signalstats,metadata=print:file=-" -f null -` prints per second statistics including average brightness (`YAVG`). Large jumps between neighbouring seconds mean flicker or an auto exposure change (the filter is standard in ffmpeg, check the output on your build).

## Step 5: choose

1. Rank by total score. If the top two are within 5 points, they are tied: the user decides, with the table.
2. Show the user a short report: the table, the two best takes with their strongest and weakest part, a recommendation, and what cannot be measured ("tone and expression need your ear").
3. Wait for the user's choice. Do not assemble or ingest before they choose.

If the user chose to combine takes (question 2 b to d), work part by part:

1. Split the approved script into beats (one idea each, see `ae-script-structure`).
2. Score each beat in each take on script match and clean delivery only (a part of a take with no stumble in that beat wins), then compare picture and audio at the whole take level.
3. Use a different take for a beat only when its gain is clear (a stumble free beat against one with a restart). Changing takes costs continuity.
4. Take switches only at a beat boundary, at most 2 switches in 30 seconds of output (starting value). Prefer a switch where a graphic or a punch zoom will cover the jump (`ae-agent-fx`, `ae-agent-graphics`).
5. Check each switch: same framing (compare the stills), same brightness, same background, same eye line. If two takes differ in distance from the camera, do not switch.

## Step 6: build one source for the editor

The editor takes a single file. For one chosen take, ingest that file directly. For a combination:

1. Decide exact ranges with the word times: each range starts a little before its first word and ends a little after its last word, in real silence (`ae-precise-audio-cut`).
2. Cut each range from its take into a new file, all with identical settings so they can be joined:

```
ffmpeg -v error -y -threads 4 -ss START -to END -i TAKE -vf "fps=30,scale=1080:1920" -c:v libx264 -crf 16 -preset medium -pix_fmt yuv420p -c:a aac -b:a 192k -ar 48000 work/part01.mp4
```

(Use the real frame size of the takes; the scale shown is only an example.) Run with `nice -n 15`, one part at a time.

3. Join them: write `work/list.txt` with lines `file 'part01.mp4'`, then

```
ffmpeg -v error -y -f concat -safe 0 -i work/list.txt -c copy work/source-assembled.mp4
```

Stream copy only works when every part has the same codec settings, which is why step 2 re encodes them identically.
4. Record the mapping in `takes/assembly-map.json`: each part, its take, source start and end, and the position in the assembled file. This lets anyone trace a word back to its take.
5. Check the seams: extract a still just before and just after each join and look at them; you cannot listen, so transcribe a 3 second window across each join and compare it with the script.
6. Ingest `work/source-assembled.mp4` (`ae-ingest-and-transcribe`). The assembled file is the one the render will cut from, so keep it until the edit is delivered.

## Decisions that belong to the user (never guess)

- Which take wins when the top two are tied.
- Whether a take with a better look but a worse delivery should win.
- Whether to use a take that stops mid sentence.
- Whether to keep the rejected takes (they stay until the user says otherwise).

## Worked example (neutral placeholder content)

A local bakery owner filmed the same 30 second sourdough explainer three times. The approved script has 74 words.

| Take | Score (picture scored) | Script match | Clean | Audio | Pace | Handles | Picture |
| --- | --- | --- | --- | --- | --- | --- | --- |
| take2 | 92 | 29 | 22 | 18 | 10 | 5 | 8 |
| take3 | 87.5 | 30 | 25 | 12 | 10 | 2.5 | 8 |
| take1 | 73 | 22 | 10 | 20 | 7 | 5 | 9 |

Notes behind the numbers: take3 reads the script cleanly but its noise floor is only 28 dB under speech (a fridge hum from 14 s). Take1 is the best looking and has the best audio but contains two restarts and a 1.1 s pause. Take2 has one filler and a small pace dip.

Report to the user: "Take2 and take3 are within 5 points. Take2 has better audio, take3 is cleaner but has background hum. I recommend take2. If you want the cleanest delivery, take3 plus an audio cleanup pass (`ae-audio-cleanup`). The picture score is my reading of five stills each, please look at them: takes/stills/." The user picks take2. Ingest that file. No combination was needed.

If the user had asked to combine: beat 3 ("feed it twice a day") is clean in take3 and has a restart in take2. Use take3 for beat 3 only (one switch). The stills at the join show the same framing and light, so the switch is acceptable. Record it in the mapping file.

## Failure modes

| Problem | What to do |
| --- | --- |
| A take has a perfect transcript but the person looks away | Picture points cannot be measured from numbers, so the manual score decides. Say so |
| All takes match the script, scores are tied | Present the table and ask. Do not break the tie yourself |
| Names misspelled in some transcripts, so script match is low | Fix spellings or normalise before comparing (`ae-ingest-and-transcribe`) |
| Takes recorded at different distances or lights | Do not combine them. Offer one take only |
| Whisper loses the tail of a take | Compare the last 5 seconds with the stills and audio level before scoring |
| Audio and video out of sync in one take | Note it in the report, and exclude the take until the user decides |
| Disk nearly full while building parts | Stop, tell the user. Do not delete anything to make room |

## Checklist

- [ ] Profile read; the four questions answered; the script is approved.
- [ ] Inventory table written; originals untouched.
- [ ] Each take transcribed once, one at a time.
- [ ] Scores computed; weights stated; picture scored from stills with notes.
- [ ] Report shows the table, the top two, a recommendation and what is not measurable.
- [ ] The user chose before anything was built or ingested.
- [ ] If combined: switches at beat boundaries only, seams checked, mapping file saved.
- [ ] Rejected takes left in place.

Hand off to: `ae-ingest-and-transcribe` (ingest the chosen source), `ae-filler-and-restart-removal` (clean the chosen take), `ae-precise-audio-cut` (exact ranges and joins), `ae-audio-cleanup` (hum, noise), `ae-script-first-workflow` (the approved script gate), `ae-laptop-load-safety` (heavy jobs), `ae-run-multi-agent-edit` (the edit itself).
