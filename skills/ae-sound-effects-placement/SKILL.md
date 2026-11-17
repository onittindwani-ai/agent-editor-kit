---
name: ae-sound-effects-placement
description: Chooses, times and checks sound effects for an edit: one real, licensed sound per visible action, placed just before the picture, never repeated close together, with a banned list the user controls. Use when the user says "add sound effects", "add whooshes", "pops and clicks", "make it feel more alive", "this sound is annoying", "is this sound allowed", or when graphics and zooms exist and need sound.
---

# ae-sound-effects-placement

Sound effects make motion feel physical, but a wrong or repeated sound is the fastest way to make an edit feel cheap.
This skill covers how to choose a sound, where in time to put it, how loud, how to avoid repeats, how to check the
licence, and how to keep a banned list that never leaks back in.

## 0. Read the profile first

Read `brand/profile.md`. If it is missing or a section it needs is empty, stop and run `ae-setup-interview` for that
section (ask the user, with options), do not guess. This skill needs `## Sound` (how many effects, which kinds, any
banned sounds, where the user's library is), `## Visual theme` (a soft, premium look wants soft sounds), and
`## Rules` (licence rules, banned list).

If `## Sound` lacks effect answers, ask:

1. How should sound effects feel?
   a) None, voice and music only. b) Very quiet and soft, barely noticed. c) Clear and light: pops, ticks, soft whooshes.
   d) Punchy: impacts and risers on key moments.
2. Where may effects land (pick any)?
   a) New graphics. b) Punch zooms. c) Numbers and counters. d) Section changes. e) Typing or UI actions. f) Nowhere
   except where I say.
3. Do you have your own sound library or licensed pack?
   a) Yes, here is the folder. b) No, suggest where to get free commercial use sounds. c) No sounds at all, please.
4. Any sound you already dislike (kind of sound or exact file)? I will add it to the banned list.
5. May effects sit under the voice when they overlap speech?
   a) Never over words. b) Only very quiet ones. c) Yes, mixed under the voice.

## 1. Licence and source rules (hard)

- No licensed media is bundled with this kit. The user brings or licenses their own. If they have none, offer to list
  where to look (libraries that state "free for commercial use" in their licence text), and let them pick.
- Use only real recorded sounds with a written licence the user can show. Never invent a sound by synthesising a beep
  and calling it an effect, unless the user asks for synthesised sound design and understands it is generated.
- Each file used gets a row in `brand/sound-log.csv`: file name, where it came from, licence text or link, whether
  credit is required, date added. Create the file if it does not exist.
- Check the licence for: commercial use allowed, no attribution needed (or attribution done in the description),
  redistribution of the final video allowed, not "non commercial" and not "editorial only". If unsure, do not use it
  and tell the user why.
- Never put a sound from a video, a game, a film or a song into an edit unless the user owns it.
- Work on copies. Trim, fade and level copies in the project folder, never the library original.

## 2. The banned list mechanism

Keep `brand/banned-sounds.md`. One row per banned sound:

| Sound (what it is) | Identified by | Reason from the user | Date |
| --- | --- | --- | --- |
| example: long swipe whoosh | file name AND the SHA 256 hash of the file | "breaks the flow at word ends" | date |

Rules:

1. Before placing any sound, check it against the list by file name AND by hash
   (`shasum -a 256 FILE`). A renamed copy has the same hash, so the hash catches it.
2. After placing sounds, list every sound clip in the edit and check each again. Put the check result in the report.
3. Do not swap a banned sound for a near duplicate (another similar swish) as a workaround. Choose a different kind
   of sound (a soft pop, a tick) or no sound.
4. A new dislike from the user is added to the list immediately (see `ae-owner-notes-to-rules`).
5. The user may unban a sound by saying so in the current message; log the date and the quote.

## 3. Choosing the sound for the action

One sound per visible action. Match the character of the sound to the character of the motion.

| Visible action | Sound character | Length | Notes |
| --- | --- | --- | --- |
| Graphic card slides in | soft whoosh or airy pop | 0.2 to 0.5 s | not a long swipe; keep tail short |
| Graphic text appears | tiny tick or soft click | 0.05 to 0.15 s | quiet |
| Number counter finishes | light chime or soft pop | 0.2 to 0.6 s | on the last step, not during the count |
| Punch zoom | very short low thump or soft pop | 0.1 to 0.3 s | never both a thump and a whoosh |
| Highlight or underline draws | gentle swipe tone | 0.2 to 0.4 s | follow the drawing speed |
| Section or chapter change | slightly longer soft riser or whoosh | 0.5 to 1.2 s | at most a few per video |
| Typing or UI action shown on screen | real keyboard or click | length of the action | only when something really types |
| Success, done, check mark | soft confirm tone | 0.3 to 0.8 s | one per video is plenty |

Do not put a sound on a caption change. Caption swaps happen constantly; sound there turns into noise.

Keep the family consistent: choose 4 to 8 files that sound like they belong together (same softness, same
brightness), then reuse across the video with variety. Mixing a harsh sound into a soft family is noticed instantly.

## 4. Timing: the lead rule

The ear expects the sound slightly before the picture, because light is perceived as arriving with the sound it
causes. Starting values (approximate; check on stills and by frame math):

- Place the sound 0.05 to 0.2 s BEFORE the visible entrance begins. A good starting lead is 0.1 s.
- For a sound with a soft attack (a whoosh), its peak should land on the moment the object settles or on the word.
  Offset the file start by the time from file start to its peak.
- For a click or tick (sharp attack), its start is its peak. Land it on the entrance frame minus 0.05 s.
- Never place a sound after the picture. Late sound reads as a mistake.
- A sound that lands on a spoken word must not cover the first consonant of the next word; if in doubt, move it into
  the gap before the word.

Minimum spacing:

- The same file is not reused within 2.5 s. Use a different file from the family.
- Two sounds closer than 0.25 s fuse into one noise; drop the weaker one.
- No more than about 1 sound per 1.5 s on average in a short vertical video; fewer in long form. The user's choice
  "very quiet" means roughly half of that.
- Leave the first 0.3 s clean so the hook word is unmasked.

## 5. Level

- Effects sit under the voice. Starting level: peak of each effect at -18 to -12 dBFS before the final loudness step,
  and the voice average at about -20 to -18 dBFS. Effects therefore peak a few dB below the loudest voice moments.
- Soft sounds: high pass at 90 Hz and low pass at about 8.5 kHz make them gentler. Example copy command:
  `ffmpeg -i in.wav -af "highpass=f=90,lowpass=f=8500,afade=t=in:d=0.005,afade=t=out:st=0.2:d=0.1,volume=-6dB" out.wav`
  (adjust `st` to the real length).
- Add a 5 ms fade in and a short fade out to every effect so it does not click at its edges.
- Do not normalise every effect to the same peak; a tick and a riser should not be equally loud. Tune by ear and by
  numbers, and record the dB value used.
- After mixing, check that effects never push the true peak over -1 dBTP (see `ae-loudness-mastering`).

## 6. How this works with the Agent Editor

The editor server accepts one background music file through the `music` operation, and it mixes that single file under
the voice. As shipped, the server has no operation for individual sound effects. Therefore:

- Plan effects as a cue list (`brand/sound-cues.csv`: time in OUTPUT seconds, file, level in dB, action it belongs
  to, lead used). Take the times from the final accepted state of cuts, graphics and zooms, converted to output time
  (kept cuts shift everything earlier; the render converts source times with the same offset rule).
- Mix the cue list into the rendered file in a separate step (for example an `ffmpeg` filter graph with `adelay` per
  cue and `amix` with `normalize=0`), before the loudness step. Check the server's current README; a newer version
  may add an effects operation, in which case use that instead.
- Delay values for `adelay` are in milliseconds per channel: `adelay=1230|1230`.
- Re derive the cue list after any change to cuts, because every time after a changed cut moves.

Cue list example (synthetic):

```
time_s,file,level_db,action,lead_s
2.90,pop_soft_03.wav,-14,stat card enters,0.10
9.15,tick_02.wav,-18,highlight draws,0.05
13.40,pop_soft_01.wav,-14,counter lands on 48,0.08
21.00,whoosh_soft_02.wav,-16,chapter title,0.10
```

## 7. Checks before you report

1. Banned list check by name and hash for every placed file. Show the result.
2. Licence rows exist for every file; none unclear.
3. Spacing check: print the cue list sorted by time and compute the gaps; flag gaps under 0.25 s and any file reused
   within 2.5 s.
4. Lead check: for each cue, confirm on a still sequence that the picture event begins after the cue time.
5. Level check: measure the mixed file's true peak; effects must not cause an overload.
6. Count: fewer sounds than the maximum the user chose.
7. State honestly: "I cannot hear. These files were used: ... Please listen to the first 15 seconds and tell me which
   ones you dislike."

## 8. Worked example

A short about sourdough timing from a local bakery. The profile says soft sounds, effects on graphics and counters only.

- Visual events: stat card "48 hours" at 4.2 s, lower third "Starter" at 11.0 s, counter "12" lands at 17.5 s,
  highlight "no yeast" at 24.0 s.
- Cues: soft pop at 4.1 s (-14 dB), tick at 10.95 s (-18 dB), chime at 17.42 s (-14 dB), gentle swipe tone at 23.9 s
  (-16 dB).
- Gap check: smallest gap 6.5 s, no file reused. Banned list: no hit by name or hash.
- The mixed file's true peak is -2.3 dBTP. Report lists four files and asks the user to listen and veto.

## 9. Failure modes

- A sound on every caption: noise. Remove.
- The same pop five times: irritating. Rotate through the family.
- Late sound: feels wrong. Move earlier by 0.1 s.
- A loud effect hiding a word: lower it or move into the gap.
- A licence not recorded: the file cannot ship.
- Renamed banned file slipping in: hash check catches it.

## 10. Checklist

- [ ] Profile read, effect style recorded, library location known.
- [ ] Licence row for every file in `brand/sound-log.csv`.
- [ ] Banned list checked by name and hash, result shown.
- [ ] One sound per visible action, none on caption changes.
- [ ] Lead 0.05 to 0.2 s before the picture, same file never within 2.5 s.
- [ ] Levels recorded, peaks under the voice, final true peak at or under -1 dBTP.
- [ ] Cue list regenerated from the final timeline.
- [ ] Report states the files used and that Claude could not listen.

Hand off to: `ae-music-bed-and-mixing`, `ae-loudness-mastering`, `ae-agent-graphics`, `ae-agent-fx`, `ae-owner-notes-to-rules`, `ae-edit-qa-gates`.
