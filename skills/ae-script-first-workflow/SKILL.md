---
name: ae-script-first-workflow
description: The gated order from idea to approved script to plan to build, and what may not happen before the user approves the words. Use whenever the user asks for a video, Reel, Short or long form piece, says "make a video about X", "write me a script", "here is my transcript", "I am filming this today", or hands you a changed script, and before any graphics, captions plan, edit or render is started.
---

# Script first workflow

Read `brand/profile.md`. If it is missing or a section this skill needs (`## Audience`, `## Offer and call to action`, `## Script preferences`, `## Platforms and formats`, `## Rules`, `## Claims policy`) is empty, stop and run `ae-setup-interview` for that section (ask the user, with options), do not guess.

## Why this skill exists

Every picture, caption, sound and cut in a video is built on the spoken words. If the words change after the build, the build is wrong and the user pays twice: once in time and once in trust. So the words are written first, alone, and approved by the user before anything else exists. This skill is the traffic light for the whole kit: it decides what may happen now and what must wait.

The user hand edits scripts, reads them aloud from a teleprompter and cares about single words, commas and capital letters. Treat every script file as theirs, not yours.

## The gates (never skip one, never build ahead of an open gate)

| Gate | What happens | Output | Who decides |
| --- | --- | --- | --- |
| G0 Intake | Read the profile, take the topic, confirm audience, length, platform, resource | Brief (section 3) | the user answers, you record |
| G1 One sentence summary | Write the single sentence the video is about | Summary line | you propose, the user can correct |
| G2 Facts | Claim ledger for every number, name, date, screen and comparison (`ae-claims-and-truth-ledger`) | Ledger file | you build, evidence decides |
| G3 Script | Draft with the method skills (`ae-hook-writing`, `ae-script-structure`, `ae-spoken-flow-and-plain-language`, `ae-value-first-teaching-tone`, `ae-call-to-action-writing`) | Script sent ALONE | the user approves, edits or rejects |
| G4 Review gate | Score it (`ae-script-review-gate`), fix, show scores | Score table | you, then the user |
| G5 Plan | Beat map, visuals list, graphics list, sound ideas, caption plan | Plan file | the user agrees |
| G6 Build | Cut, graphics, captions, sound in the editor | Timeline | you |
| G7 QC | `ae-edit-qa-gates`, stills, seams | Evidence | you report honestly |
| G8 Export and publish | Only on the user's explicit go (`ae-export-once-workflow`, `ae-publish-packaging`) | Files | the user |

One gate per reply. After G3 you stop and wait. A reply that contains a script AND a graphics plan AND captions has broken the order.

## What may NOT happen before G3 is approved

- No graphics, motion templates, proof cards, counters or lower thirds.
- No caption plan, no caption style choice for this video, no highlight words list.
- No sound plan, no music pick, no sound effect list.
- No filming guide that depends on the words, no shot list, no B roll list.
- No cut of footage that is meant to follow the script (a raw take cut for dead air is fine only when the user already spoke the words, see section 7).
- No thumbnail, title or description copy (these come after the script is final because the script can change the promise).
- No resource or giveaway built or promised in public text. You may ASK what the resource is.
- No claim copied into a hook that is not in the ledger.

What MAY happen before G3: reading the profile, researching sources for the ledger, asking intake questions, proposing a topic list, checking the user's raw footage exists and plays.

## 1. Intake (G0): ask, do not assume

Do not ask what the conversation already answered. If a detail is missing and a sensible default exists in the profile, use the default and say so in one line. Ask only what changes the script. Show options; the user may answer freely.

Questions, with options:

1. Format and length: (a) a 30 to 35 second short, (b) a 45 to 60 second short, (c) a 60 to 90 second short, (d) a long form video of about [N] minutes, (e) other.
2. Which platform wins if they conflict: (a) Instagram Reels, (b) YouTube Shorts, (c) TikTok, (d) LinkedIn video, (e) all, same words.
3. What should the viewer be able to do or understand at the end: (a) do one concrete thing, (b) understand one idea they misjudged, (c) know about one news item and what it changes for them, (d) decide between two options.
4. What is the resource or action at the end: (a) a free resource sent after a comment, (b) a link in the description, (c) follow for the next part of a series, (d) no action, only value. Detail in `ae-call-to-action-writing`.
5. Where do the facts come from: (a) the user's own real experience (ask for specifics), (b) a public page or document the user names, (c) news you must verify, (d) a tool or product you must test or read first.
6. Is there a reference video to model (topic, order of beats, title pattern, never the words)? If yes, the gate still applies: you write new words in the user's voice.

Record the answers in the brief file (section 3).

## 2. The one sentence summary (G1)

Write exactly one sentence in this shape and put it at the top of the brief:

> This video is about [specific event, problem or idea], which matters to [specific audience from the profile] because [a personal consequence for them], and the viewer will leave with [one takeaway].

If you cannot fill every bracket with something specific, the idea is not ready. Sharpen it or ask. Vague example (fails): "A video about AI tools for small businesses." Sharp example (passes): "This video is about a free recipe scaler that doubles a bread formula without ruining the ratios, which matters to home bakers who keep guessing the water amount, and the viewer will leave with a one step way to scale any formula."

## 3. The brief file

Create `project/script/BRIEF.md` (create the folder if needed):

```
# Brief
Summary: <one sentence>
Format: <length, platform>
Audience (from profile): <one line>
Takeaway: <one line>
Resource or action: <one line or none>
Facts needed: <list, each becomes a ledger row>
Source of words: <written by agent | supplied by user | reference to model>
Status: G0 done, G1 done, G2 open
```

Update the Status line after every gate. A stranger opening the folder must know where the project stands.

## 4. How to send the script for approval (G3)

Send the script alone in chat. Use labels so the user can review structure:

```
HOOK
<spoken words>

SETUP (why it matters to you)
<spoken words>

POINT 1, POINT 2 ...
<spoken words>

PAYOFF
<spoken words>

ACTION
<spoken words>
```

Under it, three short lines only: the template or beat sheet used, the estimated runtime range with the word count (see `ae-script-structure`), and the open facts that still need the user (marked `[NEEDS USER FACT: ...]`). Nothing else. No graphics ideas, no "and for the visuals".

The saved file is different: `project/script/SCRIPT.txt` holds the spoken words only, one beat per paragraph, with no labels, so the user can load it into a teleprompter. Keep labelled and clean copies in step.

If the project has a long form ending or a platform specific ending (for example a link line for a platform with no direct messages), that is a spoken section too and goes in the script, see `ae-call-to-action-writing`.

## 5. Edit rounds: the user's words are never rebuilt from memory

When the user returns an edited script, or asks you to change a line:

1. Read the current file from disk in that turn. Never work from your last draft, a summary or a generator.
2. Save the current file to `project/script/superseded/SCRIPT-<date>-<n>.txt` before any whole rewrite. One safety copy per rewrite.
3. Change only the lines the user named. Keep every other character, including their typing marks (odd capitals, repeated words, curly quotes, ellipses). Do not normalise their punctuation.
4. List every change you made as old line, new line, reason. If you disagree with one of their words, say so in a suggestion, never silently change it.
5. If they edited words, run `ae-voice-capture` to learn from the difference (word by word), then continue.
6. After the change, re run the claim check for any changed number or name, and list the assets that are now stale (section 6).

Keep only one current version in every place the user looks (the project folder top level, any cloud copy, any tracker). Older versions live in `superseded/` only. Never leave `script-v2`, `script-final`, `script-old` at the top level.

## 6. Stale asset map: what a script change invalidates

| Changed in the script | Now stale and must be redone |
| --- | --- |
| Any spoken word | transcript of the take, caption groups, word synced graphics timing |
| A number or name | counters, proof cards, lower thirds, the ledger row, any on screen string |
| A line removed or added | beat map, runtime, sound cue times, graphic start times |
| The hook | first frame, hook text on screen, thumbnail concept, title options |
| The action line | end card, pinned comment, description link line, resource list |
| The promised resource | the resource itself, the ledger, every place that names it |

After any change, write the stale list into `project/STATUS.md` and tell the user which items will be redone and which stay valid.

## 7. When the user supplies the words

If the user pastes a transcript, a finished script or raw footage where the words are already spoken, those words are the approved script. G3 is skipped, but:

- Keep every character. Offer suggestions only as old line, new line, reason.
- Still build the ledger (G2) and tell the user, plainly, which claims are weak and what safer wording you propose. Do not silently soften their words.
- Still run `ae-script-review-gate` and report scores honestly. Do not block them from filming.
- If they hand you a reference video to model, that is NOT supplied words. Run the full gate.

## 8. Failure modes to avoid

| Failure | Why it hurts | Fix |
| --- | --- | --- |
| Script and graphics plan in one reply | The user approves two things at once and a script change wastes the plan | Send the script alone, plan after approval |
| Rebuilding a script from memory after the user edited it | You erase their changes | Read the file from disk every time |
| Drafting from taste, not method | Inconsistent, hard to review | Name the method skills used in the brief |
| Writing the CTA last without a resource | The promise is invented | Settle the resource at G0 |
| Treating "looks good" as approval for the plan | They approved the words only | Ask again at G5 |
| Skipping the ledger because "everyone knows this" | One wrong number kills trust | Ledger every number, name and date |
| Letting a reference video leak its words | Copying | Take mechanisms only, write new words |

## 9. Worked example (placeholder content)

User: "Make me a short about why my sourdough starter smells like nail polish."

1. G0: you ask length (user picks 45 to 60 s), platform (Reels and Shorts, same words), resource (a one page feeding schedule, sent after a comment), facts source (the user's own baking plus one public baking-science page they name).
2. G1: "This video is about the sharp nail polish smell of a hungry starter, which matters to home bakers who think the starter is ruined because the smell is sudden, and the viewer will leave with the one feeding change that clears it."
3. G2: ledger rows for "the smell comes from acetone like compounds when the starter is underfed" (needs the named page), "feed twice a day for 2 to 3 days" (the user's own experience, marked B), and the count of what the resource contains.
4. G3: you send HOOK, SETUP, two POINTs, PAYOFF, ACTION as one message. Estimate: 124 words at 2.7 words per second is about 46 seconds. Open fact: the resource has 1 page, so the action line says "one page", not "a full guide".
5. The user edits two words. You read the file, save the superseded copy, change only those lines, list the changes, update the stale list (transcript and counters not yet built, so nothing is stale), and only now offer the plan (G5).

## 10. Checklist

- [ ] Profile read, empty sections handled by `ae-setup-interview`.
- [ ] Brief file exists with the one sentence summary filled in with specifics.
- [ ] Ledger rows exist before the draft claims anything.
- [ ] Script sent alone, with labels, runtime range and open facts.
- [ ] No graphics, captions, sound, thumbnail or title work started.
- [ ] After approval, the stale list is written and the clean spoken file saved.
- [ ] Every edit round read the file from disk and saved a superseded copy first.
- [ ] STATUS.md shows the current gate.
- [ ] Only one current version of each script exists outside `superseded/`.

## Hand off to

`ae-claims-and-truth-ledger` (G2), `ae-hook-writing`, `ae-script-structure`, `ae-spoken-flow-and-plain-language`, `ae-value-first-teaching-tone`, `ae-call-to-action-writing` (G3), `ae-script-review-gate` (G4), `ae-voice-capture` (after user edits), then `ae-run-multi-agent-edit` once the plan is agreed.

See also `references/status-and-stale-templates.md` for the STATUS file and a stale list template.
