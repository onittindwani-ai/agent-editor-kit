# Start here

You do not need to read the skills. Your Claude Code reads them. You only need to do these things.

## 1. Open the folder in Claude Code

Clone the repo, open a terminal in the folder and start Claude Code (`claude`).

## 2. Say this

> Set up the Agent Editor Kit for me.

Claude will:

1. **Interview you first.** Expect about 90 questions in 12 rounds (about 40 minutes), each with options and an example: your
   business, who you make videos for, your offer and call to action, how you talk, how you like scripts written, your colours
   and fonts, caption style, sound, platforms and formats, your rules, and what you may and may not claim. In a hurry? Ask for
   the quick start (about 8 minutes) and Claude will ask the rest later, when a task needs it.
2. Write your profile into `brand/profile.md` and `brand/theme.json`. These stay on your computer (they are in `.gitignore`).
3. Then check that Python, ffmpeg and a whisper tool are installed, help you install what is missing, and install the skills
   (`sh install.sh`).

Take your time on the interview. Everything after it is built on your answers.

## 3. Give Claude a raw video

> Edit this video: /path/to/raw-video.mp4

Claude will first write the script for your approval (nothing else happens before you approve it), then ingest the
video, start the editor at `http://127.0.0.1:8780`, start a team of agents (cutters, captioners, effects, graphics and a
reviewer), and show you the edit as it is built. Open the page to watch every cursor.

You review the result with stills and the live timeline. Say what to change. When you say export, one render is made.

## If something breaks

Ask Claude: "run the kit checks and tell me what is wrong". It runs `python3 scripts/check_kit.py` and the editor
tests. The skill `ae-install-and-run` lists the common errors and their fixes.

## What the kit will never do

Post or publish for you, invent facts or numbers, export a final video without your go, or edit your original files.
