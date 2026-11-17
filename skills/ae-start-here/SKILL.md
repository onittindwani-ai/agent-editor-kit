---
name: ae-start-here
description: The front door of the Agent Editor Kit. Use it first on every new session or when the user says "get started", "set up the editor", "what can this kit do", "help me edit a video", "where do I begin" or names any kit task without saying which skill. It checks that a brand profile exists, refuses to continue any other kit task until `brand/profile.md` exists, runs the setup interview when it does not, and routes the user to the right skill.
---

# ae-start-here: router and first run gate

You are the first skill the user meets. Your job has two parts: (1) enforce the profile gate, (2) route the request to the right skill. Do the gate before anything else, every session, even if the user is in a hurry.

## 1. The gate (run this first, always)

The whole kit is built so that nothing is hard coded: brand, voice, offer, audience, colours, fonts, caption style and rules all live in `brand/profile.md` and `brand/theme.json` in the user's project. Without them every other skill would have to guess, and guessing is banned.

Run these checks from the project root (use the shell, do not assume):

```
test -f brand/profile.md && echo "profile: present" || echo "profile: MISSING"
test -f brand/theme.json && echo "theme: present" || echo "theme: MISSING"
for h in "## Business" "## Audience" "## Offer and call to action" "## Voice and tone" "## Script preferences" "## Visual theme" "## Captions" "## Sound" "## Platforms and formats" "## Rules" "## Claims policy"; do grep -qxF "$h" brand/profile.md 2>/dev/null && echo "ok   $h" || echo "MISSING $h"; done
python3 -c "import json;json.load(open('brand/theme.json'));print('theme.json: valid JSON')"
```

Decide with this table:

| Result | What you do |
| --- | --- |
| `brand/profile.md` missing | REFUSE every task except the two allowed ones below. Say the refusal text, then start `ae-setup-interview`. |
| Profile present, one or more of the 11 headings missing | Treat as a broken profile. Run the checklist in `ae-profile-schema`, then run `ae-setup-interview` for the missing sections only. Refuse other tasks until the headings exist. |
| Profile has all 11 headings, theme.json missing or invalid | Run `ae-setup-interview` in theme mode (round 6 only), then `ae-theme-builder`. Tasks that do not touch visuals (script, claims, cut) may continue; anything with captions, graphics or render waits. |
| Profile complete, some sections show `Status: NOT SET` | Allow the task. List the unset sections, and tell the user the skill that needs one will stop and ask. |
| Profile complete and confirmed | Show the menu (section 4) and route. |

### Refusal text (adapt the wording, keep the meaning)

"Before I can help with that, I need your brand profile. It is a file that tells every part of this kit who you are, who watches, how you talk, and how your videos should look. It does not exist yet, so I will ask you 12 rounds of questions (about 90 in total) with options and examples. The full interview takes about 40 minutes; a quick start takes about 8 minutes and I will ask the rest later when a task needs it. Which do you want? You can say 'you choose' or 'skip' on any question."

### What you must not do at the gate

- Do not create an empty or placeholder `brand/profile.md` to get past the check. The check is about the user's real answers.
- Do not accept "just use defaults" as a way to skip the whole interview. Defaults exist only per question, after the user has seen the options and said "you choose".
- Do not copy a profile from a previous project, an example, or another user. If the user has their own brand document, ask for it and use it only to pre fill answers; the user still confirms every round.
- Do not start an install, ingest, edit, script, caption, graphic, sound or export task "while we wait". Nothing else runs until the file exists.
- Do not hide the refusal inside a long answer. Say it in the first two sentences.

### The two allowed exceptions

1. `ae-setup-interview`, because it creates the file.
2. `ae-profile-schema`, read only, because the interview and the user may need to see the file format.

Plain questions about what the kit is, what it costs (it is local software plus skills), or how long a task takes may be answered without a profile. If the user says "install first", explain once that the interview needs no tools and takes minutes, then offer to do it right now. If they still refuse, the answer stays no for every other task.

## 2. First run orientation (say this in your own words, short)

The Agent Editor Kit has two halves:

1. **The editor**: a small local server (`server.py`) that holds one shared timeline. Several Claude Code agents edit it at once by sending checked operations with `curl` (cut, caption, effect, graphic, music), and a browser tab shows every agent's cursor. One click renders a real mp4 with ffmpeg.
2. **42 skills**: the know how that tells agents how to script, cut, caption, theme, add graphics and sound, check quality and prepare the post. Every skill reads your profile instead of assuming a brand.

Recommended project layout (the user may choose differently; record the choice in the profile Rules section):

```
brand/            profile.md, theme.json, logo and font files the user owns
footage/          raw takes, never edited in place (copy first)
scripts/          approved scripts, one file per video
edit/             working notes, run logs, stills, owner notes log
exports/          the single export per video, plus post copy
agent-editor/     the editor (server.py, ingest.py, render.py, ui, project/)
```

## 3. Routing: what the user says, where it goes

| The user says (examples) | Skill chain, in order |
| --- | --- |
| "set up", "get started", "my brand", "change my colours" | `ae-setup-interview`, then `ae-theme-builder` |
| "install", "it does not start", "port in use" | `ae-install-and-run` |
| "edit this video", "cut and caption", "use all agents" | `ae-ingest-and-transcribe`, `ae-run-multi-agent-edit` |
| "which take is best" | `ae-take-selection` |
| "remove the ums", "tighten it" | `ae-filler-and-restart-removal`, `ae-precise-audio-cut` |
| "write a script", "give me a hook", "idea for a video" | `ae-script-first-workflow`, `ae-hook-writing`, `ae-script-structure` |
| "make it sound natural", "plain language" | `ae-spoken-flow-and-plain-language`, `ae-value-first-teaching-tone` |
| "is this claim true", "add a source" | `ae-claims-and-truth-ledger` |
| "call to action", "giveaway" | `ae-call-to-action-writing` |
| "review my script", "score it" | `ae-script-review-gate` |
| "learn my voice from my edits" | `ae-voice-capture` |
| "captions", "subtitles" | `ae-caption-style-and-grouping` |
| "graphics", "lower third", "stat card", "chapter card" | `ae-motion-design-principles`, `ae-lower-thirds-and-chapter-cards`, `ae-word-synced-graphics` |
| "show a real page or post on screen" | `ae-proof-cards-and-real-screens` |
| "animate a number" | `ae-counters-and-numbers` |
| "transitions", "blur" | `ae-transitions-and-blur` |
| "sound effects", "music", "mix", "loudness" | `ae-sound-effects-placement`, `ae-music-bed-and-mixing`, `ae-audio-cleanup`, `ae-loudness-mastering` |
| "pacing feels slow" | `ae-pacing-and-rhythm` |
| "vertical", "safe zones", "square", "landscape" | `ae-phone-safe-zones-and-formats` |
| "is it ready", "check everything" | `ae-edit-qa-gates` |
| "export", "render the final" | `ae-export-once-workflow` (needs the user's explicit go) |
| "my laptop is slow", "it froze" | `ae-laptop-load-safety` |
| "I do not like X", any note on an edit | `ae-owner-notes-to-rules` |
| "title", "description", "thumbnail", "chapters" | `ae-publish-packaging` |

## 4. The menu (show it when the profile is complete)

Show it as five groups, one line each, and ask what the user wants to make today.

- **Setup and operation**: `ae-start-here`, `ae-setup-interview`, `ae-profile-schema`, `ae-install-and-run`, `ae-run-multi-agent-edit`, `ae-agent-cutter`, `ae-agent-captioner`.
- **Agent roles and footage**: `ae-agent-fx`, `ae-agent-graphics`, `ae-agent-reviewer`, `ae-ingest-and-transcribe`, `ae-take-selection`, `ae-precise-audio-cut`, `ae-filler-and-restart-removal`.
- **Audio, pacing, delivery mechanics**: `ae-pacing-and-rhythm`, `ae-audio-cleanup`, `ae-sound-effects-placement`, `ae-music-bed-and-mixing`, `ae-loudness-mastering`, `ae-export-once-workflow`, `ae-laptop-load-safety`.
- **Scripting**: `ae-script-first-workflow`, `ae-hook-writing`, `ae-script-structure`, `ae-spoken-flow-and-plain-language`, `ae-value-first-teaching-tone`, `ae-claims-and-truth-ledger`, `ae-call-to-action-writing`, `ae-voice-capture`, `ae-script-review-gate`.
- **Motion graphics, captions, formats, QA, publishing**: `ae-motion-design-principles`, `ae-word-synced-graphics`, `ae-proof-cards-and-real-screens`, `ae-counters-and-numbers`, `ae-transitions-and-blur`, `ae-theme-builder`, `ae-lower-thirds-and-chapter-cards`, `ae-caption-style-and-grouping`, `ae-phone-safe-zones-and-formats`, `ae-edit-qa-gates`, `ae-owner-notes-to-rules`, `ae-publish-packaging`.

## 5. Typical journeys (offer the one that fits)

**A. Raw footage to a finished edit** (the main one)
1. `ae-script-first-workflow` (if the user has no script yet; if the footage already contains the spoken words, the script is the transcript and the user approves it by saying so).
2. `ae-install-and-run`, `ae-ingest-and-transcribe`, then `ae-take-selection` if there are several takes.
3. `ae-run-multi-agent-edit` (cutters, captioners, fx, graphics, reviewer).
4. `ae-edit-qa-gates` on stills and seams, notes through `ae-owner-notes-to-rules`.
5. Explicit go from the user, then `ae-export-once-workflow`, `ae-loudness-mastering`, `ae-publish-packaging`.

**B. Script only**: `ae-script-first-workflow`, `ae-hook-writing`, `ae-script-structure`, `ae-spoken-flow-and-plain-language`, `ae-claims-and-truth-ledger`, `ae-call-to-action-writing`, `ae-script-review-gate`. Stop at the approved script.

**C. Captions only on finished footage**: `ae-ingest-and-transcribe`, `ae-caption-style-and-grouping`, then one captioner through `ae-run-multi-agent-edit` with only the captioner role.

**D. Brand and theme only**: `ae-setup-interview` (rounds 6 and 7), `ae-theme-builder`.

**E. Packaging only**: `ae-publish-packaging` with the approved script and the final file names.

## 6. Gates that apply to every task (say them once on first run)

1. Script first. No graphics, caption plan or edit before the user approves the script (unless the footage already holds the words).
2. Never invent facts, numbers, quotes, screens or results. A missing asset is a blocker; mock ups are labelled.
3. Never export a final video or publish anything without the user's explicit go. Rendering in the editor counts as an export.
4. One heavy job at a time (transcription, 4K encodes, renders). Low priority, capped threads, small resumable steps.
5. Look at frames and stills before calling anything done. A command that exits 0 proves nothing.
6. Real recorded sounds with a licence. The user's media is never edited in place; copy first.
7. Safe delete: literal absolute paths only, prefer the system Trash, never wildcards.
8. Every user note on an edit becomes a rule or a check.

## 7. Returning users

When the profile is complete:
1. Read `Last updated` at the top of `brand/profile.md`. If it is older than 90 days, or the user mentions a rebrand, a new offer, a new platform or a new audience, offer a section refresh through `ae-setup-interview` before editing.
2. Read the Rules and Claims policy sections out loud in one line each so the user is reminded of the defaults in force.
3. Ask what to make today, then route with section 3.

## 8. Worked example (placeholder content)

User: "Help me edit a video for my bakery."
You run the checks. Output shows `profile: MISSING`.
You: "Before I can edit, I need your brand profile, a file about you and your viewers. I will ask in 12 rounds with options, about 40 minutes for the full interview or about 8 for a quick start. Which do you want?" The user says "ok". You start `ae-setup-interview` round 1 (business). You do not open the editor, ingest the footage or look at the clips yet.

Next day the same user returns. Checks pass. You say: "Your profile was last updated 12 days ago: a local bakery, viewers who want to bake at home, friendly teacher voice, 9:16 for two platforms. Same setup today? What do you want to make: a script, an edit of the footage, or captions?" Then you route.

## 9. Failure modes

| Mistake | Fix |
| --- | --- |
| Answering a how to question with a long tutorial before the gate | Gate first, then answer. |
| Treating a stale profile as current | Ask about changes when it is older than 90 days. |
| Routing to a skill without naming the section it needs | Each skill checks its own sections; tell the user which sections the chain will read. |
| Leaving the user in menu loops | After the menu, always ask one concrete question. |
| Letting a partial draft in `brand/.interview-draft.md` count as a profile | Only `brand/profile.md` with all 11 headings passes the gate. |

## Checklist

- [ ] Ran the three checks (profile, headings, theme.json) in this session.
- [ ] If anything failed, said the refusal in the first two sentences and started the interview.
- [ ] Did not start any other kit task before the profile existed.
- [ ] Showed the menu or routed with the table, naming the skills in order.
- [ ] Stated the gates once.

Hand off to: `ae-setup-interview` (no profile), `ae-profile-schema` (broken profile), `ae-install-and-run`, `ae-script-first-workflow`, `ae-run-multi-agent-edit`, `ae-theme-builder`.
