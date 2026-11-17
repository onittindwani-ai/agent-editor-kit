# Agent Editor Kit

A video editor built for AI agents, plus 42 skills that teach your Claude Code how to script, edit, caption,
animate, sound design and ship video the way you want it done.

- **Agent Editor**: many agents edit one shared timeline at the same time, from a single open browser tab. Each agent has
  its own cursor, every edit is checked by the server (OK or NO with a reason), and one click renders a 1080p mp4.
- **42 skills**: scripting rules, hooks, claims, motion graphics, captions, sound, loudness, quality gates, safe zones,
  publishing. They contain no brand, niche or person of mine. They run on YOUR profile.
- **A long setup interview**: the first time you open the kit, your Claude asks you many questions (your business,
  audience, voice, script style, theme, captions, sound, platforms) with options, then writes your own profile.

## Start in 3 steps

1. Clone this repo and open the folder in Claude Code.
2. Say: **set up the Agent Editor Kit for me.** Claude first interviews you (about 90 questions in 12 rounds, about 40 minutes, or a quick start of about 8 minutes) and writes your profile. Then it checks and installs the tools you need.
3. Say: **edit my video** and give it a raw video file. Claude scripts, cuts, captions and renders with a team of agents.

Prefer to install the skills yourself?

```
sh install.sh            # into ./.claude/skills of this folder
sh install.sh --global   # into ~/.claude/skills for every project
```

## What is inside

| Folder | What it is |
| --- | --- |
| `agent-editor/` | The editor: server, live screen, ingest tool, renderer, agent brief, tests |
| `skills/` | 42 skills, each a folder with a `SKILL.md` (and deeper `references/` where needed) |
| `brand/` | Where your own profile and theme are written. Templates only until you run the interview |
| `docs/` | The skill index, how the editor works, media and licence notes |
| `scripts/check_kit.py` | Checks every skill (front matter, detail, links between skills) |

### The 42 skills

Setup and operation: `ae-start-here`, `ae-setup-interview`, `ae-profile-schema`, `ae-install-and-run`,
`ae-run-multi-agent-edit`, `ae-agent-cutter`, `ae-agent-captioner`.

Agent roles and footage: `ae-agent-fx`, `ae-agent-graphics`, `ae-agent-reviewer`, `ae-ingest-and-transcribe`,
`ae-take-selection`, `ae-precise-audio-cut`, `ae-filler-and-restart-removal`.

Audio, pacing and delivery: `ae-pacing-and-rhythm`, `ae-audio-cleanup`, `ae-sound-effects-placement`,
`ae-music-bed-and-mixing`, `ae-loudness-mastering`, `ae-export-once-workflow`, `ae-laptop-load-safety`.

Scripting: `ae-script-first-workflow`, `ae-hook-writing`, `ae-script-structure`, `ae-spoken-flow-and-plain-language`,
`ae-value-first-teaching-tone`, `ae-claims-and-truth-ledger`, `ae-call-to-action-writing`, `ae-voice-capture`,
`ae-script-review-gate`.

Motion graphics: `ae-motion-design-principles`, `ae-word-synced-graphics`, `ae-proof-cards-and-real-screens`,
`ae-counters-and-numbers`, `ae-transitions-and-blur`, `ae-theme-builder`, `ae-lower-thirds-and-chapter-cards`.

Captions, formats, quality and publishing: `ae-caption-style-and-grouping`, `ae-phone-safe-zones-and-formats`,
`ae-edit-qa-gates`, `ae-owner-notes-to-rules`, `ae-publish-packaging`.

Full descriptions: [docs/SKILL-INDEX.md](docs/SKILL-INDEX.md).

## Requirements

Python 3.9 or newer, ffmpeg, and a whisper command line tool that writes word timestamps (the default is
`mlx_whisper` on Apple silicon; use `--whisper` for another). Pillow draws the captions. Remotion is optional, for
custom motion graphics (check its licence for company use). Your agents run in Claude Code.

## How agents edit

Agents never click around a normal browser. They send small operations to the editor's API with `curl`:
`cut`, `caption`, `fx`, `graphic`, `music`, `reject`. The server checks each one against the transcript and the editing
rules, answers OK or NO with a reason, and the screen draws the accepted edit and moves that agent's cursor to it.
See [agent-editor/README.md](agent-editor/README.md) and `skills/ae-run-multi-agent-edit`.

## Honest limits

This is a focused tool for multi agent editing, not a replacement for a full editor such as Palmier Pro or Adobe After
Effects: there is no colour grading and no keyframe curve editor, and the graphic templates are few. Each agent decision
takes seconds because the agent is thinking. Quality depends on the model, the transcript and the profile you wrote.
The kit never publishes anything and never exports a final video without your go. Check every result.

You bring your own footage, fonts, music and sound effects. None are included; check each licence. See
[docs/LICENSING-AND-MEDIA.md](docs/LICENSING-AND-MEDIA.md).

## Licence

MIT. See [LICENSE](LICENSE).
