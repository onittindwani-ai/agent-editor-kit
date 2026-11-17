---
name: ae-export-once-workflow
description: Runs the export gate: finish the whole edit inside the editor, review with stills, ask for the user's explicit go, make exactly one export, then do post steps (loudness check, captions pass if separate, versioning, cleanup of superseded files). Use when the user says "export it", "render the final", "is it ready to render", "make the file", "send me the video", "I changed one thing, render again", or whenever an agent is about to call the render endpoint.
---

# ae-export-once-workflow

Exports are expensive (minutes of heavy CPU), and every extra one leaves a pile of near duplicate files and a user who
cannot tell which one is current. The rule of this kit: **finish the edit first, review with stills, ask once, export
once.** A review render is still an export.

## 0. Read the profile first

Read `brand/profile.md`. If it is missing or a section it needs is empty, stop and run `ae-setup-interview` for that
section (ask the user, with options), do not guess. This skill needs `## Rules` (delivery gates, who must approve),
`## Platforms and formats` (which files to deliver), `## Sound` (loudness target) and `## Captions` (burned in or
separate).

If the delivery gates are missing, ask:

1. Who must say "go" before an export?
   a) Only me. b) Me, after a second person reviews. c) Any message from me that says export. d) Always ask me, even if I
   already approved once.
2. How many files do you want at the end?
   a) One master. b) One per platform (vertical, square, landscape). c) Master plus a short preview clip.
3. Where should finished files go?
   a) A folder named `exports` inside the project. b) A folder I name. c) Ask me each time.
4. After delivery, should superseded exports be moved to the system Trash automatically?
   a) Yes, after I confirm the new one is good. b) Never, I will clean up. c) Ask each time.

Write the answers in `## Rules` under "Delivery gates" using the `ae-profile-schema` format.

## 1. The five states of an edit

An edit is always in exactly one state. Say which one in every report.

1. **Drafting**: agents are placing cuts, captions, effects, graphics.
2. **Reviewing**: the reviewer rejects bad items; the conductor fixes them; stills are inspected.
3. **Ready**: all gates in `ae-edit-qa-gates` are green, no open user notes. The agent says "Ready to export, say the word."
4. **Exported**: one export exists. A green light was used.
5. **Delivered**: loudness verified, post steps done, files named and filed, the user has the paths.

A move from 3 to 4 needs the user's explicit go. A move back from 4 to 2 (a note arrives) needs a new go before the
next export.

## 2. What counts as a green light

Counts:

- The user writes "export", "render it", "go ahead and export", "yes, export" in the current conversation, after you
  said the edit is ready.

Does not count:

- "Looks good" or "nice" about a still.
- "Build it" or "do it all" given at the start of the job.
- An earlier go for an earlier version.
- A quiet user, a passing QA gate, a finished timeline, or an agent saying it is done.
- A go from a third person unless `## Rules` names that person.

Quote the user's words in the export ledger (section 4). One yes covers one export. If a note arrives after export, a
new go is needed before another.

## 3. Finish in the editor, review with stills

Before asking for the go, everything below must be done inside the editor session (no render):

1. All agents have sent `done`. The reviewer has run `/api/review` and the issues list is empty or explained.
2. The user's notes (if any) are applied, each turned into a rule or check by `ae-owner-notes-to-rules`.
3. Stills were made from the SOURCE frames at every event: first frame, every graphic start and end, every punch zoom
   peak, each caption sample, the last frame. Use a tiny extraction, not a render:
   `ffmpeg -v error -ss 12.4 -i project/source.mp4 -frames:v 1 -q:v 3 stills/t12_4.jpg` (one at a time). Because the
   proxy is 720p, say that stills show the proxy, not the final resolution.
4. Cut seams checked from the transcript: words at each join, no gap over the limit, no clipped word.
5. `ae-edit-qa-gates` table is filled with evidence, not ticks.
6. Disk and load checks pass (see `ae-laptop-load-safety`).

Then say once: "Ready to export. This will make one 1080p file and take about N minutes (estimate with a range). Say
the word." Do not export until the user says it.

## 4. The export ledger

Keep `exports/LEDGER.md` (create it). One row per export:

```
| # | Date and time | Green light (quote) | Edit state (cuts, captions, fx, graphics counts) | File | Notes |
```

Write the row BEFORE exporting, with the quoted go. A row without a quote means the export is not allowed. After the
export, fill in the file name and the measured result. If a second export is needed, the ledger shows the second go.

## 5. How to export in the Agent Editor

The render is started with `POST /api/render` and the file lands in the project's `out` folder as `edit-<number>.mp4`
(the number is a Unix timestamp), unless the server was started with another output folder. Rendering runs on the
server in a background thread; check progress with `GET /api/state` (the `render` field shows `rendering`, a fraction
and finally `done` with the file name, or an error).

Rules for the run:

1. Confirm the ledger row first.
2. Confirm no other heavy job is running (see `ae-laptop-load-safety`).
3. Send one render request. Do not send a second while `state` is `rendering`; the server answers "already rendering"
   and a second thread would double the load.
4. Wait by checking the state every 20 to 30 seconds, not in a tight loop.
5. On error, read the message. Typical causes: no accepted cuts, a missing font, the music file moved, a disk that is
   full. Fix the cause, tell the user, and do NOT start repeated blind retries. A failed render that did not finish
   does not use up the green light, but say so explicitly and ask before the next try if the cause is not obvious.
6. The render reads the original source file when it still exists; do not move or rename it during the run.

Do not make draft exports, "quick previews" or half length test renders for review. Stills and the editor screen are
the review tools. (If the user explicitly asks for a short preview clip, that is their request; log it as an export.)

## 6. Post steps after the one export

Do these in order. All of them work on the exported file or its copies; none re render the picture.

1. **Verify the file** with `ffprobe`: dimensions (1080 by 1920 for a vertical master unless the profile says
   otherwise), frame rate, duration equals the sum of kept cuts (within one frame), one video and one audio stream.
2. **Look at frames**: contact strips at 1 second steps, and full size stills at the first frame, every seam,
   every graphic, and the last frame. See `ae-edit-qa-gates`. Do not say done from the exit code.
3. **Measure loudness and true peak** and fix with the mux method from `ae-loudness-mastering` if needed.
4. **Word check**: transcribe the exported file (one heavy job at a time) and compare with the expected words; flag
   missing words, doubles and clipped starts.
5. **Captions**: if the profile says captions are separate from the picture (for example a caption pass in another
   tool), make them from the transcript of this export so times match exactly. In the shipped Agent Editor the
   captions are drawn in the same render, so this step is a visual check only.
6. **Name and file** the master using the pattern `<project-slug>_<format>_v<N>.mp4` (for example
   `sourdough-basics_vertical_v1.mp4`). Versions go up by one per export. Never overwrite an earlier file.
7. **Platform variants** the user asked for (square, landscape) are separate compositions, not crops of the vertical
   file; see `ae-phone-safe-zones-and-formats`. Each needs its own go if it needs a new render.
8. **Write the delivery report** (section 8) and give the user full absolute paths.

## 7. Versioning and cleanup

Versions and cleanup keep the folder understandable.

- Keep: the raw takes (never touched), the editor project folder (state and ingest files), the current clean export,
  the current deliverables, the ledger, the QA report and the notes.
- Superseded: older exports, review stills of old versions, old caption composites, old loudness test files.
- Move superseded files to the system Trash, never delete with wildcards. On macOS: `trash "/absolute/path/file"` (the
  `/usr/bin/trash` command exists on recent macOS) or Finder. On other systems use the desktop Trash tool or a
  `superseded` folder and tell the user. List the exact absolute paths first, show the list, and only act after the
  user agreed (or the profile says to auto trash after confirmation).
- Never empty the Trash. The user does that.
- Never use `rm -rf`, wildcards, relative paths or paths built from variables in a delete.
- Report the space freed (sum of file sizes) once the Trash is emptied by the user.

## 8. The delivery report (plain and short)

```
State: Delivered (export #1)
Files: /absolute/path/sourdough-basics_vertical_v1.mp4 (34.0 s, 1080x1920, 30 fps, 41 MB)
Green light used: "export it" (quoted, date, time)
Measured: -16.0 LUFS, -1.6 dBTP; 12 cuts, 14 captions, 5 graphics, 4 zooms
Looked at: first frame, 12 seams, 5 graphics, 4 zooms, last frame (strips and stills in qa/)
Not done or not heard: I cannot hear audio; please listen to the first 15 s and the ending.
Cleaned up: none yet. 2 superseded files proposed for the Trash (paths listed).
Not posted: nothing was published or uploaded.
```

## 9. Changes after delivery

- A small note (a caption spelling, a graphic text): fix it in the editor state, redo the stills, ask for a new go,
  make a new export, bump the version. If the change is only audio level or a caption drawn outside the editor, use
  the separate step (mux or caption pass) and do not re render the picture.
- Several notes at once: batch them. Apply them all, review stills once, ask for one go. Do not export after each note.
- A late fact check: if a claim is wrong, stop and flag it before any export.

## 10. Never

- Never export without a quoted green light for this revision.
- Never "just test" with a render.
- Never publish, upload, post, schedule or send. Preparing files is within scope; publishing is the user's act.
- Never overwrite an earlier export.
- Never delete originals, never empty the Trash.

## 11. Worked example

A bakery short. State Ready. Agent says: "Ready to export. About 3 to 5 minutes on this machine. Say the word."
User: "export it". Ledger row written with the quote. Load check clean. Render started once, finished in about 4
minutes (the file lands in `out` with a number name). ffprobe: 34.03 s. Strips and seam stills looked at. Loudness
-17.6 LUFS, so the two pass mux runs. Final named `sourdough-basics_vertical_v1.mp4`. The report is sent. The user
then writes "make the card say 48 hours not 48 hrs." The agent fixes the graphic text in the state, remakes two
stills, says "Ready again. One more export, say the word," and waits.

## 12. Checklist

- [ ] Profile read, delivery gates recorded.
- [ ] State is Ready, every gate in `ae-edit-qa-gates` has evidence.
- [ ] Stills of every event looked at (and said to be proxy resolution).
- [ ] User go quoted in `exports/LEDGER.md` before rendering.
- [ ] Load and disk checks passed; only one heavy job.
- [ ] One render request; waited by polling every 20 to 30 s.
- [ ] ffprobe, strips, word check and loudness done on the exported file.
- [ ] Versioned file name, no overwrite.
- [ ] Superseded files listed with absolute paths, moved to the Trash only after agreement.
- [ ] Nothing published; report lists what was not heard.

Hand off to: `ae-loudness-mastering`, `ae-edit-qa-gates`, `ae-publish-packaging`, `ae-laptop-load-safety`, `ae-owner-notes-to-rules`.
