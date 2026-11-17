# Licensing and media

## This kit

MIT licence (see `LICENSE`). You may use, change and share it.

## What is not included, and why

The kit contains no footage, photos, fonts, music, sound effects, logos or backgrounds. You bring your own. Check the
licence of every file you use. In particular:

- **Footage and photos of people**: only your own, or with written permission.
- **Music and sound effects**: use files you own or that are licensed for your use (commercial use if you earn from
  the video). Keep a small list of each file you use with its source and licence. The skill `ae-sound-effects-placement`
  shows a simple register.
- **Fonts**: check the licence before embedding. Google Fonts families are open licensed; others may not be.
- **Logos and screenshots**: using another company's logo or a screenshot of a page can need permission. The skill
  `ae-proof-cards-and-real-screens` explains what to record about each one.

## Tools the kit uses (their licences are theirs)

- **ffmpeg**: free software, licence depends on how it was built (LGPL or GPL). Check your build.
- **Pillow**: draws the caption images in the render. Open source licence.
- **A whisper command line tool**: transcribes speech with word timestamps. Models have their own licences.
- **Remotion** (optional, for custom motion graphics): free for individuals and small companies, but companies above a
  size threshold need a paid licence. Read Remotion's current licence terms before using it for work.
- **Claude Code**: used to run your agents; its own terms and usage limits apply.

## Your data

Your answers to the setup interview are saved in `brand/profile.md` and `brand/theme.json` on your computer. Both are
listed in `.gitignore` so they are not committed by accident. The editor runs locally on `127.0.0.1` and does not send
your video anywhere. Your agents (Claude Code) read the transcript text you give them.
