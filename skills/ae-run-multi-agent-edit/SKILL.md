---
name: ae-run-multi-agent-edit
description: The conductor for a multi agent edit in the Agent Editor. Plans time windows, launches 7 or more Claude Code subagents (cutters, captioners, fx, graphics, a reviewer) with the agent brief and a role skill, watches progress, handles refusals and re runs, runs the review and fix rounds, and renders only after the user's explicit go. Use when the user says "edit this video with all the agents", "run the edit", "start the agents", "cut and caption this", "use 7 agents", or after ingest is done.
---

# ae-run-multi-agent-edit: the conductor

Read `brand/profile.md`. If it is missing or a section it needs is empty, stop and run `ae-setup-interview` for that section (ask the user, with options), do not guess. You need: `## Rules` (cut style, filler policy, gates, laptop limits), `## Captions`, `## Script preferences`, `## Claims policy`, `## Visual theme`.

You do not cut, caption or place anything yourself during a run. You plan, brief, launch, supervise, route problems and report. The agents place everything through the editor's API; the server checks every operation and says OK or NO with a reason.

Prompts, the window planner and the run log template are in `references/agent-prompt-templates.md`.

## 1. What the editor accepts (so you brief correctly)

Operations are POSTed to `/api/op` as JSON. The server answers `{"ok":true,"id":...}` or `{"ok":false,"error":...}`.

| op | Role | The server says NO when |
| --- | --- | --- |
| `hello` (agent, role) | all | never; must be sent first |
| `claim` (kind: sentence with id, template with id, or window with start and end; status) | all | never |
| `cut` (start, end in source seconds, note) | cutter | under 0.4 s, overlaps a kept cut, start or end inside a spoken word |
| `caption` (start, end, text) | captioner | more than 3 words or 22 characters, shorter than 0.2 s or longer than 3 s, overlaps another caption, words not spoken near it |
| `fx` (type `punch_zoom` or `blur_in`, at, dur) | fx | overlaps another effect, two punch zooms closer than 4 s |
| `graphic` (template `stat_card`, `lower_third`, `chapter_title`, `highlight`; text 1 to 24 chars; at; dur 1.5 to 4 s) | graphics | words not spoken within 2 s, closer than 0.5 s to another graphic, more than 10 graphics |
| `music` (file inside MUSIC_ROOT, volume_db -30 to -14) | conductor or an audio agent | file not inside the music folder, volume out of range |
| `reject` (id, reason of 8 or more characters) | reviewer only | not a reviewer, no such accepted item |
| `remove` (id) | the person at the screen (role `human`) only | not human, no such item |
| `done` (agent, summary) | all | never |

Reads: `GET /api/window?start=A&end=B` (words with `t` and `e`, silences, sentences, items already placed), `GET /api/review` (problems in the whole edit and stats), `GET /api/state` (roster, items, render status), `GET /api/rejections?agent=ID`, `GET /api/ingest`. The page listens to `/api/events`.

An agent cannot delete or edit its own item. The only ways to remove one are the reviewer's `reject` (with a reason) and the human's `remove`. This is why agents must verify before they send.

## 2. Preflight (all must be true before launching anything)

1. The profile exists and the sections above are present.
2. The user approved the spoken script, or the footage already holds the words and the user said the transcript is the script (gate: script first). Record how in the run log.
3. `ae-install-and-run` health checks passed: server up, `/api/state` answers, tests pass.
4. The transcript was checked (`ae-ingest-and-transcribe`): names spelled as the user wants, in `project/ingest.json`, before captioners start.
5. The timeline is empty: `/api/state` shows zero cuts, captions, fx and graphics. If it is not empty and this is a new video, stop and move the old project aside; if it is a continuation, read what exists first.
6. No other heavy job is running (`uptime`, no render, no ingest). Free disk is above the profile's limit.
7. Create `edit/run-log.md` from the template.

## 3. Plan the roster

Default roster for a source of 46 to 120 seconds is 7 agents. Scale with the source length:

| Source length | Cutters | Captioners | FX | Graphics | Reviewer | Total |
| --- | --- | --- | --- | --- | --- | --- |
| up to 45 s | 1 | 1 | 1 | 1 | 1 | 5 |
| 46 to 120 s | 2 | 2 | 1 | 1 | 1 | 7 |
| 121 to 240 s | 3 | 3 | 1 | 1 | 1 | 9 |
| over 240 s | ceil(length / 80) up to 6 | same as cutters | 1 | 1 to 2 | 1 | 10 or more |

Ids: `W01`, `W02` cutters, `W03`, `W04` captioners, `W05` fx, `W06` reviewer, `W07` graphics; continue `W08`... for extra agents. Roles must be exactly `cutter`, `captioner`, `fx`, `graphics`, `reviewer` (a reviewer must say hello with the role `reviewer` or its rejects fail).

Windows:
- Cutter windows: 40 to 60 seconds of source each, edges in the middle of a real pause (silence list), no overlap, no gap. Use the planner in the reference file.
- Captioner windows: the same windows as the cutters whose results they caption (one captioner per cutter window), or wider but never splitting a sentence.
- FX and graphics agents get the whole video but use only kept speech.
- The reviewer gets the whole video.

Quotas (scale to the kept length after cutting; compute after phase 2):
- Punch zooms: about one per 8 to 12 s of kept time, 4 to 6 in a 60 s video, at least 4 s apart, 1.2 s long.
- Blur in: one at the start of a new section, at most 2.
- Graphics: about one per 12 to 15 s of kept time, 5 to 8 in a long short, 2 to 4 in a very short one, never more than 10.
- Respect the profile's motion taste: "almost none" means 0 to 2 zooms and 0 to 2 graphics.

## 4. The phases

**P1. Plan.** Write the roster and windows into the run log. Tell the user the plan in 5 lines: agents, windows, expected duration of the run (a cutter takes a few minutes per window; the whole run is usually under 30 minutes), what you will show them before rendering.

**P2. Cutters** (parallel). Launch all cutters in ONE message (one subagent call per agent, all in the same message, so they run concurrently). Each prompt = base prompt + cutter addendum + profile excerpt. Tell each: cut style from the profile, and "plan all your cuts in a table first, verify, then send".
- While they run, watch the roster (section 5). Do not start captioners yet.
- When all are `done`: read `/api/review`. Check the stats: kept seconds, cuts. Compute the kept ratio (kept divided by source). For the cut style: tight about 55 to 80 percent kept, natural 70 to 90 percent, relaxed 85 to 98 percent. A ratio far outside means a window was over or under cut; ask that cutter's window to be re checked (section 7).
- Open the page and look at the cuts lane. Check the seams you cannot see in numbers later with stills.

**P3. Gate before the next phase.** Zero `pause` issues in `/api/review` for cuts, or each one explained. Windows covered. Edges between windows not clipped (look at the words near each edge in `/api/window`).

**P4. Captioners, FX, graphics** (parallel, one message). They need the cuts, so they start after P3. Give each the kept video summary (the list of cuts). Graphics and fx agents must place items only inside kept cuts: the render silently ignores a graphic or punch zoom whose start is not inside a kept cut, and the review does not flag it.

**P5. Reviewer.** After all editors are `done`, launch the reviewer alone. It reads `/api/review`, the window of every cut, caption, fx and graphic, and rejects with concrete reasons. It must not create items.

**P6. Fix rounds.** For each agent with rejections (`GET /api/rejections?agent=ID`), tell that agent (a new subagent with the same id and a prompt that includes the rejection list and its window) to read the reason and place a corrected item. Maximum 2 fix rounds. If an item is still rejected after round 2, stop and decide with the user: accept the compromise, cut around it, or fix by hand.

**P7. Final checks before asking for the go.**
1. `/api/review` shows no issues (or each remaining one explained to the user).
2. Stats vs targets: kept length, captions count, fx and graphics counts, rejections count.
3. Look at stills (not only numbers): extract from the proxy with `ffmpeg -ss <time> -i project/source.mp4 -frames:v 1 edit/stills/<name>.png`, at each cut seam, at every graphic, and at the first and last second. A still of the source does not show captions or graphics; use the page preview for those and describe what you saw honestly.
4. Spell check every caption and graphic text against the transcript and the profile's custom spellings.
5. Run `ae-edit-qa-gates`.
6. Collect the user's notes (batch them), turn each into a rule or check with `ae-owner-notes-to-rules`, fix, and re check.

**P8. The go.** Ask once: "The edit is ready to render. Say 'export' when you want the file." Rendering is an export. Do not call `POST /api/render` before an explicit yes. A yes covers one render. After the go, record the user's exact words and the time in the run log.

**P9. Render and verify.**
```
curl -s -X POST http://127.0.0.1:8780/api/render        # starts a background render
curl -s http://127.0.0.1:8780/api/state | python3 -c "import json,sys;print(json.load(sys.stdin)['render'])"
```
Poll at 20 to 30 second intervals (state `rendering` with `frac`, then `done` with `file`, or `error` with text). One render at a time; never start ingest or another heavy job meanwhile. The file lands in the `out/` folder as `edit-<timestamp>.mp4`.

Verify: `ffprobe` duration (should match kept length within a fraction of a second), width and height, video and audio streams; loudness (see `ae-loudness-mastering`); stills at the seams in the RENDERED file, including a caption still and a graphic still; a word check that the speech still matches the script. Report what you looked at.

**P10. Post.** `ae-export-once-workflow` for versioning and cleanup, `ae-publish-packaging` for the post copy. Nothing is posted by the kit.

## 5. Supervising while agents run

Poll the roster no more than every 20 to 30 seconds:

```
curl -s http://127.0.0.1:8780/api/state | python3 -c "import json,sys;s=json.load(sys.stdin);[print(a,v['role'],'|',v['status'],'| ops',v['ops'],'| NO',v['no'],'| done',v['done']) for a,v in s['agents'].items()]"
```

| Signal | Meaning | Action |
| --- | --- | --- |
| `NO` count over 40 percent of `ops` plus `NO`, or 8 NOs in a row | The agent is guessing instead of calculating | Send a short correction prompt that quotes the three most common reasons and the rule from the role skill. |
| `ops` unchanged for 3 minutes and status not `done` | Stalled or waiting | Check the subagent's output; if it ended without `done`, re launch for the remaining window (section 7). |
| `done` true but ops 0 | The agent gave up or misread the window | Re launch with a prompt that includes a worked example from the role skill. |
| The same item rejected twice | The method is wrong, not the number | Read both reasons and add a rule to the agent's prompt. |
| Two agents claim the same sentence | Windows overlap | Fix the window edges; the server rejects overlapping cuts so no harm, but wasted work. |

## 6. User interventions

The user may delete a chip with the Delete key on the page (that sends `remove` as role `human`). Never undo that. A removed item stays removed. If the user says "put it back", ask a cutter, captioner, fx or graphics agent to place it again.

If the user says "reset", that clears the whole timeline: confirm first, because it is destructive. `POST /api/reset` empties items and agents. Never reset to "fix" one mistake.

## 7. Re runs and restarts

- A subagent ended before `done`: find the last item it placed (`/api/window` with its window, items carry the `agent` id), compute the remaining part of its window (from the end of its last item to the window end), and launch a replacement with the same role and a window of only the remainder. Use a new id such as `W01b` so counters stay readable.
- The server restarted: `project/state.json` is reloaded if the old run logged any events. Check `/api/state` shows your items before acting.
- Wrong cut density in a window: do not fix by stacking more cuts. Ask the reviewer to reject the bad cuts, then send a new cutter to that window.
- The transcript changes (a word was misspelled): stop captioners, correct `project/ingest.json`, restart the server (state is kept), then continue. Items already placed that use the old spelling are rejected by the reviewer and re placed.

## 8. Reporting to the user

At each phase end, give 3 lines: what happened, numbers (kept seconds, items, NOs), what is next. At the end of P7 give a short table:

| Item | Count | Note |
| --- | --- | --- |
| Source length | 92.4 s | |
| Kept length | 71.3 s | 77 percent kept, natural style |
| Cuts | 14 | one per phrase |
| Captions | 63 | 1 to 3 words |
| Punch zooms, blur ins | 5, 1 | 4 s or more apart |
| Graphics | 6 | |
| Rejections | 3 | all re placed |

Never say "done" or "working" about the edit until you looked at stills and read the review. Say what you checked and what you could not check (for example, you cannot hear audio).

## 9. Worked example (placeholder content)

A 92 second bakery video, natural cut style, vertical, two platforms.
- Plan: 2 cutters (W01 0 to 46.4, W02 46.4 to 92.4; the edge sits in a 0.6 s pause at 46.4), 2 captioners on the same windows, W05 fx, W06 reviewer, W07 graphics. Seven agents.
- P2: both cutters done in about 6 minutes; kept 71.3 s (77 percent). Review shows one pause of 0.42 s inside a cut at 58.2. W02's agent reports it; the reviewer rejects that cut with the reason "0.42 s pause inside c9 at 58.2, split at the gap". W02b re places it as two cuts.
- P4: captioners place 63 captions; fx 5 punch zooms (the closest pair is 5.1 s apart) and 1 blur in at the chapter start; graphics 6 items (lower third "starter", stat card "75 percent", chapter title "Shaping").
- P5: the reviewer rejects 3 items; each agent re places once.
- P7: stills at each seam; the numbers pass. The user asks for the stat card to start 0.3 s later: the graphics agent re places it after the old one is rejected. The user says "export". Render, verify, report.

## 10. Failure modes

| Failure | Prevention |
| --- | --- |
| Launching captioners before cuts exist | Gate P3. Captions outside every cut become orphan issues and waste work. |
| Windows that split a word | Edges in the middle of a silence only. |
| Rendering to "check how it looks" | Not allowed; review with the page and stills. The render is the export. |
| Agents inventing words | The server checks captions and graphics against the transcript; spelling is fixed in the transcript first. |
| One agent doing everything | Roles stay separate so the reviewer is independent of the editors. |
| Running ingest or a second render during a render | One heavy job at a time. |
| Telling the user it is done from exit codes | Stills, review, ffprobe, a word check. |
| Forgetting to log user notes | Every note goes to the run log and `ae-owner-notes-to-rules`. |

## Checklist

- [ ] Preflight items 1 to 7 true and logged.
- [ ] Roster and windows planned with edges in real pauses.
- [ ] Cutters launched in one message; P3 gate passed.
- [ ] Captioners, fx and graphics launched after cuts; reviewer launched last.
- [ ] Rejections handled in at most 2 rounds.
- [ ] Stills and review checked; QA gates run; user notes logged.
- [ ] Explicit go received and quoted; one render; output verified.

Hand off to: `ae-agent-cutter`, `ae-agent-captioner`, `ae-agent-fx`, `ae-agent-graphics`, `ae-agent-reviewer`, `ae-edit-qa-gates`, `ae-export-once-workflow`, `ae-loudness-mastering`, `ae-owner-notes-to-rules`, `ae-laptop-load-safety`.
