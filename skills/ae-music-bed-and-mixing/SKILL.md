---
name: ae-music-bed-and-mixing
description: Chooses a quiet music bed, sets its level under speech, ducks it with a sidechain compressor, fades it, loops it and checks the licence, including how to use the Agent Editor music operation. Use when the user says "add music", "background music", "the music is too loud", "I can't hear the voice", "make it feel premium", "duck the music", or "is this track safe to use".
---

# ae-music-bed-and-mixing

A music bed should be felt, not noticed. Its job is to carry mood and cover edit seams, never to compete with the
voice. This skill covers choosing a track, the right level, ducking, fades, looping, licence checks and how the
Agent Editor mixes music.

## 0. Read the profile first

Read `brand/profile.md`. If it is missing or a section it needs is empty, stop and run `ae-setup-interview` for that
section (ask the user, with options), do not guess. This skill needs `## Sound` (music yes or no, mood, library),
`## Voice and tone` (mood of the video), `## Platforms and formats` (some platforms offer their own licensed music;
that is the user's choice and outside this edit), and `## Rules` (licence rules).

If the music answers are missing, ask:

1. Do you want music under the voice?
   a) No music. b) A very quiet bed, barely there. c) A clear but low bed. d) Music only at the start and end.
2. What mood fits the video?
   a) Calm and warm. b) Focused and modern. c) Upbeat and light. d) Serious and steady. e) No preference, suggest.
3. Do you have a licensed track or library?
   a) Yes, here is the file or folder. b) No, tell me where to find free commercial use music. c) I will license one.
4. Lyrics are distracting under speech. May I restrict to instrumental only?
   a) Yes, always. b) Yes, except where I say.
5. Should the music be the same in every video of this series?
   a) Yes, one signature bed. b) No, choose per video.

## 1. Licence rules (hard)

- No music is bundled with this kit. The user supplies the track or licenses one.
- Record every track in `brand/sound-log.csv` (file, source, licence text or link, credit needed, dates). The licence
  must allow commercial use and use in a video the user posts. Many "free" tracks require credit in the description
  or forbid use on monetised videos. Read the licence text; if it is unclear, do not use the track.
- Never use a commercial song. Never use a track found in someone else's video.
- Platform content matching can flag music even when the licence is valid. Tell the user to keep the licence text
  and track page link in case of a claim.
- Work on a copy; never edit the original track.

## 2. Choosing a bed

Criteria in priority order:

1. **Instrumental, with no vocals** and no spoken samples. Vocals fight with speech.
2. **Low density in the mid range** (1 to 4 kHz is where words live). Pads, soft piano, warm guitar, light
   synth beds, and gentle percussion work. Busy lead melodies and bright snares do not.
3. **Steady energy**: no big drops, no long silent breaks, no sudden crescendo in the middle. A short video should
   not have a sudden change unless it is planned for the payoff.
4. **Tempo that matches the pace** (see `ae-pacing-and-rhythm`): roughly 80 to 100 BPM for calm explainers, 100 to
   125 for brisk ones. This is a taste starting point, not a rule.
5. **Length**: at least the video length. A shorter track will be looped by the editor; check that the loop point
   does not click or feel like a restart (listen to the loop seam yourself via the user).
6. **Clean ending**: if the track has a natural ending, align the end of the video to it; otherwise fade out.

Offer the user 2 or 3 candidates with a one line description each and let them choose. Claude cannot hear, so describe
what you can know from metadata, tags and measured numbers (duration, estimated loudness, spectral balance from
`aspectralstats` or `astats`), not what the music "feels like". Say that clearly.

## 3. Levels

Starting values (approximate, the user's ear decides):

- Music average about 18 to 22 dB below the voice average while the voice is speaking. A simple rule used in short
  form: the music bed is mixed at roughly -20 dB relative to speech.
- Under a quiet or intimate voice, go lower (about -24 dB). Under a loud voice with a dense track, also lower.
- During a gap with no voice (the intro and outro) the music may rise by 6 to 10 dB. That is what ducking is for.
- Never let the music alone make the final mix louder than the loudness target; the loudness step (see
  `ae-loudness-mastering`) is measured on the full mix.

If the track is loud (mastered hot), measure it first and lower the track before mixing:

```
ffmpeg -hide_banner -nostats -i music.mp3 -af "ebur128=peak=true" -f null - 2>&1 | grep -E "I:|Peak:"
```

If the track reads about -9 LUFS and the voice about -20 LUFS, then set the track gain to bring it to about -38 LUFS
before the mix.

## 4. How the Agent Editor handles music

The editor accepts one music operation:

```
curl -s -X POST http://127.0.0.1:8780/api/op -H 'Content-Type: application/json' \
  -d '{"op":"music","agent":"W08","file":"folder/track.mp3","volume_db":-24}'
```

Facts from the shipped server and renderer (re read `server.py` and `render.py` on the user's copy, because a newer
version may differ):

- `file` is a path relative to the music library folder (set by the `MUSIC_ROOT` environment variable when the
  server starts). A path outside that folder, or a file that does not exist, is refused with a reason.
- `volume_db` must be between -30 and -14. Outside that range is refused.
- Only one music file is kept at a time; a second `music` operation replaces the first.
- At render time the track is looped as needed, set to `volume_db`, cut to the video length, given a fade out of
  1.5 s at the end, mixed with the voice using `amix` without automatic normalising, then the whole mix goes through
  loudness normalisation.
- The shipped renderer does not duck the music under the voice. The level is a fixed offset. So choose a low
  `volume_db` (about -26 to -22 as a start) and let the loudness stage do the rest, or add ducking in a separate
  mixing step as below.

## 5. Ducking with a sidechain compressor

When the music must rise in gaps and dip under speech, use the voice as the sidechain key. This chain parsed and ran
on ffmpeg 8 with synthetic inputs:

```
ffmpeg -v error -y -threads 2 -i music.wav -i voice.wav -filter_complex "
[0:a]volume=-18dB[m];
[m][1:a]sidechaincompress=threshold=0.05:ratio=8:attack=20:release=400[d];
[d][1:a]amix=inputs=2:normalize=0:duration=first[o]" -map "[o]" mix.wav
```

Notes:

- `threshold=0.05` (linear, about -26 dBFS) makes the compressor react when the voice is clearly present. Lower it if
  the music does not dip on quiet phrases; raise it if breaths trigger it.
- `ratio=8` gives a firm dip; `4` gives a gentler one.
- `attack=20` ms lets the first consonant through before the dip; `release=400` ms lets the music recover smoothly
  between phrases, not between every word. For fast speech use 500 to 700 ms so the music does not pump.
- Verify with measurement: compute the music level inside speech versus in gaps. The difference should be about
  6 to 12 dB. If the music pumps audibly (the user says "it breathes"), lengthen release.
- The voice file used as the key must be the final edited voice (cuts applied), or timing will not match.
- When the mix is made outside the editor, the editor's own music operation should be left unset, otherwise the music
  is added twice.

## 6. Fades and the edges

- Fade in over 0.3 to 1.0 s if the music begins with the video; a hard start at full level is jarring.
- Fade out over 1 to 2 s at the end. The editor does 1.5 s by default. Keep the voice's last word clear of the fade.
- If the music starts later (after the hook), cross fade it in over 1 to 2 s on a quiet spot.
- Never cut the music mid beat at the video's end; end on a fade.
- Command to fade a copy: `ffmpeg -i music.wav -af "afade=t=in:st=0:d=0.8,afade=t=out:st=28.5:d=1.5" music_faded.wav` with
  `st` set to the video length minus the fade length.

## 7. Where music is a bad idea

- Under a spoken list of numbers or a dense technical explanation: it competes with attention. Drop it or go lower.
- With a nervous or breathy voice and a tight room: music exposes noise. Clean the voice first (`ae-audio-cleanup`).
- Over a graphic that carries a real quote: let it breathe in near silence.
- When the user chose "no music": do none, and do not ask again.

## 8. Checks before you report

1. Licence row recorded and the track is instrumental.
2. Level measured: voice loudness, music loudness, and the difference under speech (target about 18 to 22 dB, or
   what the user chose).
3. Ducking verified by numbers if used (music level in speech windows versus gap windows).
4. Fades present at both ends; the loop seam checked if the track is shorter than the video.
5. The final mix measured for loudness and true peak after the music is added (`ae-loudness-mastering`).
6. Word check: transcribe 20 s of the finished mix to confirm the music did not hide words.
7. The report says: "I cannot hear. Please play the first 15 s and the end and tell me if the music is too loud."

## 9. Worked example

A bakery's 32 s vertical short. The user chose "a very quiet bed, warm, instrumental" and supplied a licensed track
of 90 s.

- Track measured: -12.4 LUFS, so the editor `volume_db` is set to -28 (voice is about -16 LUFS after mastering).
- `{"op":"music","agent":"W08","file":"warm/soft_piano_bed.mp3","volume_db":-28}` is accepted.
- Render: voice -16 LUFS, music about -36 LUFS under speech, so about 20 dB below. True peak -1.3 dBTP.
- Word survival on 20 s of the output: all words match.
- Licence logged with link and "no credit needed". Report asks the user to play the opening and the last 5 s.

## 10. Failure modes

- Too loud music: the most common complaint. Lower first, argue later.
- Loud vocals or a melody in the voice range: choose another track.
- Two music sources (editor operation and an outside mix): double music.
- Pumping from too short a release: lengthen release.
- Loop seam click: crossfade the loop with `acrossfade` before use.
- Unrecorded licence: do not ship.

## 11. Checklist

- [ ] Profile read; music wanted or not recorded.
- [ ] Track is instrumental and has a licence row.
- [ ] `volume_db` inside -30 to -14 and chosen from measurements.
- [ ] Ducking only if needed, verified by numbers.
- [ ] Fades in place, ending clean.
- [ ] Final loudness and true peak measured on the full mix.
- [ ] Word survival checked; user asked to listen.

Hand off to: `ae-sound-effects-placement`, `ae-loudness-mastering`, `ae-audio-cleanup`, `ae-edit-qa-gates`, `ae-export-once-workflow`.
