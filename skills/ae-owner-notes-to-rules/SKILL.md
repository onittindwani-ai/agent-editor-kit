---
name: ae-owner-notes-to-rules
description: Turns every note the user gives about an edit, script, caption, look, sound or publish copy into a fix plus a permanent rule or automated check, logs it, and makes sure the same note is never needed twice. Use whenever the user says "at 0:14 the ...", "I don't like ...", "from now on", "always", "never", "next time", "make this a rule", returns an edited file, or repeats a correction, and after every review round.
---

# ae-owner-notes-to-rules

Read `brand/profile.md`. If it is missing or a section it needs (`## Rules`, and the section the note is about) is empty, stop and run `ae-setup-interview` for that section (ask the user, with options), do not guess. Also read `brand/rules.md` and `brand/notes-log.md` if they exist, so you know what is already decided.

A note is the user's most valuable signal. Fixing the one file in front of you is only half the job: the lesson must change how every later edit is made. This skill is the loop that does both. It never changes the user's own words in their files (a script, a caption text they edited by hand): suggestions about their text go into the report, not into the file.

## When it triggers

1. Any note about an edit, script, graphic, caption, sound, look, format or publish copy, in any words: "I don't like this", "this looks off", "too fast", "move it up", "that is not what I said".
2. Time references: "at 0:14", "around the middle", "the end".
3. Standing words: "from now on", "always", "never", "next time", "every video", "make this a rule".
4. An edited file the user returns (a script, a caption list, a description): the changes are notes.
5. A correction the user has given before (a repeated note means an earlier loop failed: find why).
6. After a review round, when the user approves or rejects a version.

First do the fix the user asked for (Step 4), then run the rest of the loop in the same session.

## The loop in short

1. Capture the note word for word. 2. Batch the round. 3. Find the exact item. 4. Classify. 5. Fix only what was named. 6. Write the rule. 7. Place it everywhere it applies. 8. Automate what is mechanical. 9. Verify and log. 10. Report in plain words. Consolidate now and then.

## Step 1: Capture literally

Append to `brand/notes-log.md` (template in `references/rules-tools.md`) before touching anything: the date, the file and version the user was looking at, the time in the render, and the user's words in quotes. Do not paraphrase first: paraphrase loses small details (a word, a comma, a unit). If the note was spoken or long, keep it whole and add your short reading under it, clearly marked as your reading.

If the user returned an edited file: compute a word by word difference (for text, `diff -u old new` or Python `difflib`), list every change including punctuation, capitals and word order, and log them as one note per pattern. Note which differences look like a typing habit (curly quotes, capitals) and which look like a decision.

## Step 2: Batch the round

Collect all notes of the round before changing anything. Number them N-0007, N-0008 and so on. Group them by area (captions, graphics, cuts, sound, look, script, publish). Look for conflicts between notes (one wants faster cuts, another wants more breathing room): do not guess, ask one question with options and a recommendation. Do not render between notes (`ae-export-once-workflow`): fix in the editor, show stills, render once when the user gives the go.

## Step 3: Find the exact item

Users watch the render, so their times are output times. The editor stores source times. Run `time_map.py` (in `references/rules-tools.md`):

```
python3 brand/tools/time_map.py project/state.json 14.2
```

It prints the source time, the cut, and every accepted caption, graphic and effect on screen near that moment, with ids and the agent that placed each. Write the ids into the log. If the note is about something no item explains (a pause, a breath, a click), check the cut list and the waveform instead (`ae-precise-audio-cut`).

## Step 4: Classify each note

| Type | Meaning | What follows |
| --- | --- | --- |
| T1 fact | A wrong word, number, name, date | Fix; check the claims ledger (`ae-claims-and-truth-ledger`); a rule only if the cause is systematic (for example the transcript misspells a brand name: add it to the glossary) |
| T2 one off | Taste about this video only ("make this one funnier") | Fix; log; no rule unless the user repeats it |
| T3 preference | A durable like or dislike ("captions a bit lower") | Rule with strength default; update the profile section if the interview covers it |
| T4 hard rule | "Never X", "always Y" | Rule with strength hard |
| T5 process | How the agents should work ("show me stills before rendering") | Rule plus a line in the agent brief |

The test: would the next video break this too? If yes, it is a rule. One observation is a default; a second occurrence or any explicit "always" or "never" makes it hard. Never invent a preference the user did not show: a rule is only what they said or demonstrated, labelled as such.

## Step 5: Fix only what was named

Edit, never remake. Change the named item and its direct dependents, nothing else.

1. In the Agent Editor, only the person at the screen can remove an item, and only a reviewer agent can reject one (with a concrete reason of at least 8 characters). So: the reviewer rejects the item, or the user removes it, then the owning role places a corrected one with the normal operation. Do not work around the server's NO.
2. A change in what is said (a cut) changes output times for everything after it: re run `time_map.py` and the caption and graphic checks (`ae-edit-qa-gates` re run list).
3. A look note (colour, font, radius) changes `brand/theme.json` through `ae-theme-builder`, rebuilds tokens, and re renders only what depends on it.
4. Show stills of the fixed spots, not a full render. Render only after the user's go.
5. Read the changed spot back and compare it with what you intended. Report only what changed.

## Step 6: Write the rule

A rule is a standalone statement that a new agent, who has never seen the note, can follow and check.

| Good | Bad |
| --- | --- |
| "A caption group never ends on a function word (the, a, to, and, of, your)." | "Captions should be nicer." |
| "The first graphic appears no earlier than 1.5 s." | "Not too busy at the start." |
| "Music begins after the hook sentence ends." | "Be careful with music." |
| "Name tags use only names written in the profile or the brief." | "Do not get names wrong." |

Format (full template in `references/rules-tools.md`): id, Statement, Why (the note, shortened, with its date), Area, Strength (hard or default), Check (a read only command, or none), Applies to (skill names), Added, Status. Keep the statement to one sentence with a number or a clear test. No personal names. No reference to one video.

## Step 7: Place it everywhere it applies

| Where | When |
| --- | --- |
| `brand/rules.md` | Always, for every rule |
| The profile section (`## Captions`, `## Sound`, `## Script preferences`, ...) | A durable preference the setup interview covers; update only that section, via `ae-profile-schema` |
| `brand/theme.json` | A look value; through `ae-theme-builder`, never by hand edits that skip the contrast check |
| Agent briefs | Add a line "Read brand/rules.md first and follow every active rule in your area" to each brief that `ae-run-multi-agent-edit` hands out |
| Tools and checks | Step 8 |

Area to skills map (use it to find who must hear about the rule):

| Area | Skills |
| --- | --- |
| captions | `ae-agent-captioner`, `ae-caption-style-and-grouping` |
| graphics | `ae-agent-graphics`, `ae-lower-thirds-and-chapter-cards`, `ae-word-synced-graphics`, `ae-proof-cards-and-real-screens`, `ae-counters-and-numbers` |
| cuts | `ae-agent-cutter`, `ae-precise-audio-cut`, `ae-filler-and-restart-removal`, `ae-pacing-and-rhythm` |
| effects and transitions | `ae-agent-fx`, `ae-transitions-and-blur`, `ae-motion-design-principles` |
| sound | `ae-sound-effects-placement`, `ae-music-bed-and-mixing`, `ae-audio-cleanup`, `ae-loudness-mastering` |
| look | `ae-theme-builder`, `ae-phone-safe-zones-and-formats` |
| script | `ae-hook-writing`, `ae-script-structure`, `ae-spoken-flow-and-plain-language`, `ae-value-first-teaching-tone`, `ae-call-to-action-writing`, `ae-script-review-gate` |
| publish | `ae-publish-packaging`, `ae-call-to-action-writing` |
| process | `ae-run-multi-agent-edit`, `ae-export-once-workflow`, `ae-laptop-load-safety` |

Do not edit the kit's installed skill files to hold a project rule: they are replaced when the kit updates. Project rules live in `brand/` and override kit defaults for this project. If the user wants a rule to travel to every project, say so and keep a copy of the rules file they can import.

## Step 8: Automate what is mechanical

| Rule is about | Make it a check |
| --- | --- |
| Caption length or endings | `check_caption_groups.py` (already) |
| Graphic position, length, spacing | `graphic_plan_check.py` |
| Top band or right rail content | `scan_top_band.py` |
| Colour contrast or fonts | `theme_tokens.py` |
| Words missing after render | `word_check.py` |
| A banned sound or phrase | `grep -q` on the sound plan or the copy file; a short script that lists matches |
| Loudness, size, frame rate | `ffprobe` and `ebur128` in a one line check |
| Taste, mood, humour | No check; list it in the QA table as seen |

Put the command into the rule's `Check:` line so `run_rules.py --run` runs it. Calibrate the new check once with a known bad input (it must fail) and a known good input (it must pass). A check that cannot fail does not count. Warnings for style, errors only for hard rules.

## Step 9: Verify and log

1. `python3 brand/tools/run_rules.py brand/rules.md --run`: structure valid, every active check passes (or the failure is the known edit still in progress).
2. Re run the QA gates the change could touch (`ae-edit-qa-gates`).
3. Complete the log entry: type, fix done (item ids), rule id or "none, because ...", check and result, places updated.
4. Look at the stills of the fixed spot yourself before saying it is fixed; say "passed these checks", never "perfect".

## Step 10: Report in plain words

A short reply (under 120 words): what you changed, the rules you added (with their ids), what the agents will now do automatically, and what you could not check. One decision question at most, with options. Technical detail goes into the log and the QA report.

## Consolidation (monthly, or when `rules.md` passes about 60 rules)

1. Merge duplicates and near duplicates into one clearer rule; mark the old ones superseded by the new id. Never delete a rule or a log entry.
2. A newer note that contradicts an older rule wins: mark the old one superseded, and say so in the log. Never contradict silently.
3. Review default rules that were never used or that the user overrode more than twice: ask the user whether to retire them.
4. Check that every active rule has an area and a strength, and that checks still run.

## Worked example (placeholder: a bakery sourdough short)

The user watched version 1 and sent five notes:

| ID | Note (verbatim) | Type | Action | Rule |
| --- | --- | --- | --- | --- |
| N-0001 | "At 0:14 the caption says 'dough' but I said 'dow', it is a name" | T1 | `time_map.py` shows caption k21 at output 14.1; fix the transcript spelling, add "Dow" to the glossary, re place the caption | RULE-110: names listed in `brand/glossary.txt` are spelled exactly as listed; check: grep the captions for glossary names (new check) |
| N-0002 | "Captions ending on 'the' look unfinished, always" | T4 | Regroup the 3 captions; `check_caption_groups.py` WARN to zero | RULE-111 hard, check already exists |
| N-0003 | "The stat card is too high, my app covers it" | T3 | Move stat card to 0.18; ask the user to run the phone test once | RULE-112 default: graphics tops start at y 330 or lower (vertical); check: `graphic_plan_check.py` |
| N-0004 | "Make the ending a bit warmer" | T2 | Reworded closing line proposed in the report (the user's script is not edited by the agent); user decides | none, because it is about this ending only |
| N-0005 | "Show me stills first, do not render until I say" | T5 | Added to the brief line and to the export gate | RULE-113 hard: no render before an explicit go; check: the export ledger |

Result: 3 new rules with checks, 1 process rule, 1 one off fix. `run_rules.py --run` printed pass for RULE-111, RULE-112, RULE-110; RULE-113 is checked by reading the export ledger. Report to the user: "Fixed 4 of 5 spots (the fifth is a wording suggestion for you). Added rules 110 to 113, so names, caption endings, card height and no early renders are checked automatically from now on. Not checked yet: the new card height on your phone."

## Failure modes

1. Fixing the file, skipping the rule: the same note comes back next week.
2. A vague rule ("make captions nicer"): nothing can check it; rewrite it with a number or a test.
3. Paraphrasing the note before logging it: the small detail is lost.
4. Treating a one off taste note as a hard rule: the user's next video gets over constrained. One observation is a default.
5. A rule with a check that always passes: calibrate.
6. Editing the user's own words to match a rule: forbidden; suggest, do not rewrite.
7. Conflicting notes resolved by guessing: ask one question.
8. Output times used as source times: the wrong item is fixed.
9. A new rule that contradicts an old one silently: supersede explicitly.
10. Skipping the brief update: new agents never see the rule.

## Checklist

- [ ] Note logged verbatim with date, version and time.
- [ ] Round batched; conflicts asked; output time mapped to item ids.
- [ ] Each note typed T1 to T5; only the named item fixed.
- [ ] Rules written as one standalone sentence with a number or a test; strength set.
- [ ] Rule placed in `brand/rules.md`, the profile section if needed, and the agent briefs.
- [ ] Mechanical rules have a `Check:` that was calibrated.
- [ ] `run_rules.py --run` and the relevant QA gates re run; stills looked at.
- [ ] Short plain report sent; consolidation due date noted if the file is large.

More: `references/rules-tools.md` (the two tools and the rule and log templates).

Hand off to: `ae-edit-qa-gates` (re run), `ae-run-multi-agent-edit` (briefs carry the rules), `ae-profile-schema` (update one profile section), `ae-theme-builder` (look changes), `ae-script-review-gate` (script notes), `ae-voice-capture` (the user's edited wording), and the role skill of the area the note concerned.
