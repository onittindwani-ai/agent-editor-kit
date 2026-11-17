---
name: ae-edit-qa-gates
description: The full pre delivery gate table for an Agent Editor edit, with the check, the evidence class and the failure condition for each gate, plus how to inspect stills, transition windows and seams, how to measure audio and file specs, and how to write an honest report. Use before asking the user for the export go, after every round of notes, on a finished render, or when the user says "is it ready", "check the edit", "QA this", "what could still be wrong", "review before I look".
---

# ae-edit-qa-gates

Read `brand/profile.md`. If it is missing or a section it needs (`## Rules`, `## Captions`, `## Sound`, `## Platforms and formats`, `## Claims policy`) is empty, stop and run `ae-setup-interview` for that section (ask the user, with options), do not guess. Also read `brand/rules.md` if it exists (rules learned from the user's notes, see `ae-owner-notes-to-rules`) and `brand/tokens.json`.

This skill is the last check before the user is asked for the export go. It is a read only pass: the checker does not fix, render, export, move or delete anything. It finds problems, ranks them, and names which role fixes each. The reviewer agent (`ae-agent-reviewer`) uses the editor's own review; this skill is the wider check of the whole edit and the render.

## Principles

1. A command that exits cleanly proves nothing. A gate passes only with evidence of one of three classes: seen (frames or stills looked at by you, with one line of what you saw), measured (a tool printed a number, and you quote it), or not checkable yet (it needs a render or an export that does not exist; say so, never mark it passed).
2. Never loosen a check to reach green. Never say done, fixed, working or approved: say "passed these checks" and list what was and was not checked.
3. Calibrate every tool once per project with a negative control: feed it a known bad input (a shifted caption, a one frame black gap, a missing word, a busy top band) and confirm it fails. A check that cannot fail is not a check.
4. The checker is not the builder. If you built the edit, ask for a second pass by another agent or by the user's eyes.
5. Ranked findings: blocker (breaks a hard rule or the user's rule), major (a viewer would notice), minor (polish). Blockers stop the request for the go.
6. Gates are cumulative: after every note round re run every gate the change could touch, and write down which you re ran.

## The gate table

Evidence column: S seen, M measured, N not checkable until a render or export exists. "Fix owner" is the role that repairs a fail.

### A. Process and facts

| ID | Gate | How to check | Ev | Fails when |
| --- | --- | --- | --- | --- |
| A1 | Script first | The approved script file exists with a date older than the first graphic or caption operation in the log | S | Graphics or captions were built before approval |
| A2 | Script match | `word_check.py` on the approved script lines against a transcript of the render (N until a render exists); before that, compare the cut's transcript with the script | M | Missing line, restart left in, an ad lib that changes a claim |
| A3 | Claims ledger | Every number, name, date, comparison and quote in speech, captions and graphics has a ledger row with source and safe wording (`ae-claims-and-truth-ledger`) | S | A number or claim with no row; a stale or unverified source |
| A4 | Nothing invented | Every screen, logo, quote and result shown is real or labelled "Example" | S | A fake interface, an invented figure, an unlabelled mock up |
| A5 | Profile rules | Every line of `## Rules` and every `brand/rules.md` rule is ticked with its own check | S/M | Any rule broken (list it by number) |
| A6 | Originals untouched | `shasum -a 256` of the original files equals the hashes recorded at ingest | M | Any hash differs |
| A7 | Sensitive data on screen | Stills of every screen recording scanned for keys, tokens, emails, phone numbers, client names, private tabs | S | Anything private is readable |
| A8 | Isolation | Captions, graphics and sounds come only from this project's transcript and assets | S | Words or media from another video |

### B. Cut and speech

| ID | Gate | How to check | Ev | Fails when |
| --- | --- | --- | --- | --- |
| B1 | Editor review is clean | `curl -s http://127.0.0.1:8780/api/review`: no `pause`, `orphan_caption` or `uncaptioned` issues left | M | Any issue remains without a written reason |
| B2 | Pauses | No silence over 0.35 s inside a kept cut; no gap at a join over about 0.2 s unless designed | M | A dead pause, a gap at a join |
| B3 | Clipped words | Listen or transcribe 2 s windows across 10 joins: first and last syllable of each word survive | M/S | A cut that eats a first consonant or last syllable |
| B4 | Repeats and restarts | Transcript of the render scanned for doubled words and restart phrases | M | "the the", a phrase said twice |
| B5 | Fillers | Filler words removed per the user's choice in the profile | M | Fillers remain where the profile says remove |
| B6 | Joins | 12 ms audio fades present (render default); no click or breath burst at a join in the waveform strip | S | A click, an air burst |
| B7 | Word survival after render | `word_check.py` expected words versus render transcript: 97 percent or more and no run of 3 missing | M (N before render) | Below 97 percent or a run of 3 |

### C. Captions

| ID | Gate | How to check | Ev | Fails when |
| --- | --- | --- | --- | --- |
| C1 | Grouping | `check_caption_groups.py` has no ERROR; WARN lines resolved or explained | M | Any ERROR; unexplained WARN |
| C2 | Timing | Start 0.02 to 0.05 s before the first word, end at the last word; stills at 5 caption times show the right words | M/S | Late or early captions, drift after a cut |
| C3 | Spelling | Every caption word is in the transcript glossary or a dictionary; numbers match the profile choice | M | A typo, a wrong name |
| C4 | No double text | No caption repeats the words of a graphic at the same time | M | Same words twice on screen |
| C5 | Lane and face | Stills of first, longest and last group per scene: pill not over mouth or eyes, inside the safe zone, 60 px under any graphic | S | Over the face, in the app zone |
| C6 | Contrast | `theme_tokens.py` table has no FAIL; caption text on a pill is 7 or more; bare text tested on the busiest frame | M | Unreadable on any frame |

### D. Graphics, effects, motion

| ID | Gate | How to check | Ev | Fails when |
| --- | --- | --- | --- | --- |
| D1 | First 1.5 s | Contact strip at 10 frames per second: starts on the real subject, no loader look, no empty frame | S | A spinner look, an empty or caption only start |
| D2 | Graphic plan | `graphic_plan_check.py` prints OK | M | Any PROBLEM |
| D3 | Word sync | Each graphic appears at its word (0.12 s lead at most 0.3 s); stills at 3 graphics | S | Shown before the word, or late |
| D4 | Complete states | Stills at entrance, hold and exit: text complete, nothing half drawn or half typed | S | Half a word, an empty card, an element still moving on the hold |
| D5 | Spacing and cadence | 3 s clear between graphics; punch zooms 4 s apart; no stage unchanged over 2.5 s with nothing moving | M | Crowded or dead stretches |
| D6 | Overlaps | Stills at the busiest moment: no element touches or covers another | S | Text on a shape, a label over a graphic |
| D7 | Transitions | Frames every 1/30 s across each blur in and zoom edge (window of about 0.6 s), tiled and looked at | S | Black flash, one frame pop, a face flash between graphics, a ghost |
| D8 | Endings and seams | Last 0.5 s of the video and of every overlay clip; the last frame of one next to the first of the next | S | A moving element cut off, a connector that lands nowhere |
| D9 | Motion budget | Count blurs, sweeps and zooms; look for rotation or decoration with no meaning | S | Motion that carries no meaning |
| D10 | Flashing | No more than 3 bright flashes per second | S | Rapid flashing |
| D11 | Type voices | At most two font families; labels 36 px or more at 1080 | S | A third family, tiny text |

### E. Look and assets

| ID | Gate | How to check | Ev | Fails when |
| --- | --- | --- | --- | --- |
| E1 | Theme tokens | Colours and fonts on stills match `brand/tokens.json` | S | A literal colour or a font not in the theme |
| E2 | One accent | One accent colour means one thing; ok and warn only for done and problem | S | A second accent; a colour that changes meaning |
| E3 | Surface separation | `surface_separation` in tokens is 1.25 or more, or a rim and shadow are visible on stills | M/S | A card that melts into the plate |
| E4 | Real assets | Logos are official or licensed with a licence row; screens are readable at phone size (40 px text) and cropped to the point | S | A generic icon for a named product, a page too small to read |
| E5 | Numbers | Counters land on the spoken number; no gauge or dashboard value without a source | S | An invented value |
| E6 | Background | Background and face: the speaker's own room is not replaced or tinted unless the user asked; veil measured for image or video backgrounds | S/M | A wash over the speaker |

### F. Format and zones

| ID | Gate | How to check | Ev | Fails when |
| --- | --- | --- | --- | --- |
| F1 | Format | Frame size, fps and aspect match `## Platforms and formats` | M | Wrong size |
| F2 | Safe zones | `overlay_zones.py` stills for every layout looked at; nothing important in a coloured zone | S | Content in the top band, below y 1500 or in the right rail |
| F3 | Top band scan | `scan_top_band.py` calibrated and run; every flag looked at | M/S | An unexplained flag |
| F4 | Each format its own composition | A second format is not a crop of the first; checks re run per format | S | A cropped composition |
| F5 | Zone source | Safe zones are the user's measurements, or the report says they are approximate | S | Presented as verified when not |

### G. Sound

| ID | Gate | How to check | Ev | Fails when |
| --- | --- | --- | --- | --- |
| G1 | Licence | Every sound and music file has a source and a licence row that allows the use | S | No licence, or non commercial for a commercial video |
| G2 | Banned list | Every file name and hash against the profile's banned list | M | A banned sound |
| G3 | Placement | Sounds sit 0.05 to 0.2 s before the action, one per visible action, none on caption swaps; the same file not repeated within about 2.5 s | S | A late sound, a sound on every cut |
| G4 | Voice first | Music starts about 18 to 22 dB below the voice (starting value); voice clearly intelligible at phone speaker level | S | Buried voice |
| G5 | Loudness | After render: integrated about -16 LUFS, true peak at or below -1 dBTP (`ebur128` summary) | M (N before render) | Outside the profile's target |
| G6 | Audio sync | Duration of audio and video within 0.1 s; claps or hard sounds line up in a strip | M | Drift |

### H. Delivery and publish

| ID | Gate | How to check | Ev | Fails when |
| --- | --- | --- | --- | --- |
| H1 | Specs | `ffprobe`: codec, size, pixel format, frame rate, audio stream, colour tags, `faststart` (moov first) | M (N before export) | A mismatch with the profile |
| H2 | Stale export | The file is newer than `project/state.json` and the render's reported counts equal the editor's counts (captions, graphics) | M | An old file shown as new |
| H3 | Duration | Within the target range from the script structure | M | Over or under without a reason |
| H4 | Frame strips | Strips at every cut and graphic in the final file looked at | S | Anything the stills of the timeline did not show |
| H5 | One export per go | The export ledger shows one render per explicit go; no draft renders sent as finals | S | An export without a go |
| H6 | Cleanup | Superseded files are only removed with literal absolute paths, to the Trash; the report lists them | S | Wildcard deletes, or old exports left around |
| H7 | Publish package | CTA, links, chapters, title and description checked (`ae-publish-packaging`) | S/M | A dead link, a CTA that differs between places |

## How to inspect (commands in `references/qa-commands.md`, all read only)

| Need | Method |
| --- | --- |
| Single frame | `ffmpeg -ss T -i out/edit.mp4 -frames:v 1 stillT.png` then open the PNG with an image viewer tool and write one line of what you see |
| First 1.5 s | 10 frames per second tiled into one picture |
| Last 0.5 s | `-sseof -0.5` tiled |
| Transition window | `-ss (T minus 0.2) -t 0.6` at 30 fps tiled in 2 rows; look for a dark, white or doubled frame |
| Whole video | 3 frames per second contact sheet, tiles of 270 px |
| Seam pair | last frame of clip A and first frame of clip B side by side |
| Loudness | `ebur128=peak=true`, read integrated loudness (I) and true peak |
| Silence, black, freeze | `silencedetect`, `blackdetect`, `freezedetect` |
| Word survival | transcript of the render with the project's whisper tool, then `word_check.py` |

Rules for looking: look at the image yourself, do not just generate it. Scan at full size for the moment that matters (a transition, a graphic) and at phone size for readability (about a third of the size). Write what you saw in the report, one line per still: "t 12.5: stat card complete, 48 hours, clear of caption, in zone".

## The honest report

Write `project/qa/QA-REPORT.md` from `references/qa-report-template.md`. Rules:

1. Open with the verdict word: BLOCKED (a blocker exists), HOLD (majors remain), or READY FOR THE USER'S REVIEW (no blocker or major found by the checks run). Never "done", "perfect" or "approved".
2. Then findings, ranked, each with gate ID, time, evidence and the fix owner.
3. Then the gate table filled: for each gate S, M, N or SKIPPED with a reason.
4. Then what was not checked and why (no render yet, no phone measurement, no dictionary).
5. Then the one question for the user if a decision is needed (with options and a recommendation).
6. The chat reply is short (under 120 words): verdict, top three findings, what is next. The report file holds the detail.
7. After a note round, add a section "Re run" naming the gates re run and the result.

## Worked example (placeholder: a bakery sourdough short, vertical, 41 s)

Run before asking for the export go:

| Gate | Result |
| --- | --- |
| B1 | M: `/api/review` shows 1 `uncaptioned` (6 words at 31.4 s) |
| C1 | M: `check_caption_groups.py` 0 ERROR, 2 WARN (function word endings) |
| D2 | M: graphic plan check 1 PROBLEM: stat card top at y 192, in the top band |
| F3 | M: scan flagged 2 frames at 0.5 s in the top band, looked at: plate gradient, plain enough |
| G5 | N: no render yet |
| H1 | N: no export yet |

Verdict: BLOCKED. Findings: (1) D2 blocker: move the stat card to 0.17 of the height; owner: graphics agent. (2) B1 major: caption the 6 words at 31.4 s; owner: captioner. (3) C1 minor: two forced function word endings, explained in the notes. Not checked: loudness and final specs (no render). Next: fix 1 and 2, re run B1, C1, D2, F2, then ask the user for a go to render. The reply to the user: "BLOCKED: stat card in the top band, 6 words uncaptioned. Fixing both, then re running captions and graphics checks. Loudness and specs need a render, not yet checked."

## Failure modes

1. Saying "all checks pass" when half were N: list the N gates.
2. Marking seen without looking: write the one line.
3. Checking only the cut that changed: a note round can break a gate far away; re run by dependency (caption notes re run C1 to C6 and F2).
4. Treating a scan flag as a fail or a pass without looking.
5. Looking at the timeline instead of the render: effects, fades and overlay positions only exist in the render.
6. A stale export reviewed as the latest: gate H2.
7. Loosening a threshold to turn green: record a user decision instead.
8. A reviewer that fixes things: the checker reports; the owner role fixes.
9. Skipping the negative control: a broken scanner passes everything.

## Checklist

- [ ] Profile, `brand/rules.md` and tokens read.
- [ ] Every gate has S, M, N or SKIPPED with a reason; none left blank.
- [ ] Tools calibrated on a known bad input once.
- [ ] Stills looked at for first 1.5 s, last 0.5 s, every transition, every graphic, captions, ending.
- [ ] Report file written; verdict word used; findings ranked with fix owners.
- [ ] Re run list written after every note round.
- [ ] No export, render or delete happened as part of the check unless the user had given the go.

More: `references/qa-commands.md` (every command and the word check script) and `references/qa-report-template.md`.

Hand off to: `ae-agent-reviewer` (editor side review), `ae-run-multi-agent-edit` (fix routing), `ae-export-once-workflow` (the go and the single export), `ae-loudness-mastering`, `ae-owner-notes-to-rules` (every finding the user disagrees with or adds becomes a rule), `ae-publish-packaging` (publish package checks).
