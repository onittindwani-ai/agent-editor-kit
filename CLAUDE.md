# Agent Editor Kit: instructions for Claude Code

You are working inside the Agent Editor Kit: an AI native video editor (`agent-editor/`) plus 42 skills (`skills/`)
for scripting, editing, captions, motion graphics, sound, quality checks and publishing short and long form video.

## First rule: the kit must be set up for this user before anything else

1. Look for `brand/profile.md` and `brand/theme.json`.
2. If either is missing, or the user says "set up", "start", "install", "run it", "edit my video" or anything similar,
   read `skills/ae-start-here/SKILL.md` and follow it. It runs `skills/ae-setup-interview/SKILL.md`: a long interview where you
   ask the user about their business, audience, offer, voice, script style, visual theme, captions, sound, platforms,
   formats, rules and claims policy. Ask in rounds, show options with examples, wait for answers, then write the profile.
3. Do not write a script, plan graphics, edit, render or export for the user until the profile exists. Never guess
   their brand, colours, niche, offer, voice or call to action. Ask.

## How the skills are found

`sh install.sh` copies `skills/` into `.claude/skills/` (or `sh install.sh --global` for every project). If they are not
installed, read the needed `skills/<name>/SKILL.md` directly. Every skill reads `brand/profile.md` first.

## Working rules (the user may change them in the profile)

- Script first: the user approves the spoken script before graphics, captions plan or edit.
- Never invent a fact, number, quote, screen or result. A missing asset is a blocker, not something to fake.
- Never export a final video or publish anything without the user's explicit go.
- One heavy job at a time (transcription, 4K encodes, renders). Use low priority and small resumable steps.
- Look at frames and stills before calling an edit done. A command that exits cleanly proves nothing.
- Copy media before editing. Never edit the user's originals in place. Delete only with literal absolute paths.
- Every note the user gives about an edit becomes a rule or a check (`skills/ae-owner-notes-to-rules`).

## The editor

`agent-editor/README.md` explains the editor. Start it with `python3 server.py` inside `agent-editor/` after
`python3 ingest.py YOUR_VIDEO.mp4`. The skill `ae-run-multi-agent-edit` runs a whole multi agent edit.

## Kit health

`python3 scripts/check_kit.py` checks every skill (front matter, size, links between skills, stray paths).
`cd agent-editor && python3 -m unittest tests/test_ops.py` checks the editor rules.
