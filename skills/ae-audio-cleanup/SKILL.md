---
name: ae-audio-cleanup
description: Cleans spoken audio with safe, tested ffmpeg filter chains (rumble, hiss, plosives, harshness, uneven level) and proves the result with measurements instead of guessing. Use when the user says "the audio sounds bad", "there is background noise", "hiss", "hum", "boomy", "harsh s sounds", "uneven volume", "fix my mic", or before the final loudness step.
---

# ae-audio-cleanup

Clean audio means the voice is clear, steady and natural. It does not mean silent. The most common mistake is
removing too much: the voice turns watery and robotic. This skill gives a conservative chain, a way to diagnose
first, and checks that prove nothing was damaged. Claude cannot hear. You measure, and you tell the user which file to
play.

## 0. Read the profile first

Read `brand/profile.md`. If it is missing or a section it needs is empty, stop and run `ae-setup-interview` for that
section (ask the user, with options), do not guess. This skill needs `## Sound` (voice processing preferences, how
much cleanup is welcome), `## Rules` (anything like "never denoise my voice") and `## Platforms and formats`
(a phone speaker versus headphones changes how much low end to cut).

If `## Sound` has no cleanup answer, ask:

1. How was the voice recorded?
   a) Phone, close to the mouth. b) Phone on a stand, arm's length. c) USB or lavalier microphone.
   d) Studio microphone in a treated room. e) Not sure.
2. How much processing is welcome?
   a) Minimal: only fix real faults. b) Moderate: fix faults and level the voice. c) Full: broadcast style clarity.
3. What bothers you in the raw audio (pick any)?
   a) Hiss or constant noise. b) Low rumble or hum. c) Room echo. d) Harsh s sounds. e) Volume jumps. f) Nothing,
   I just want it checked.
4. Do you want the original audio kept untouched next to the cleaned copy?
   a) Yes, always. b) Only for the final file.

Never edit the user's media in place. Work on a copy in the project folder and keep the original.

## 1. Diagnose before you filter

Run these read only checks first (they are light; run one at a time, see `ae-laptop-load-safety`). Use a mono 48 kHz
copy of the audio so the numbers are comparable.

```
ffmpeg -v error -y -i INPUT -vn -ac 1 -ar 48000 work/voice_raw.wav
ffmpeg -hide_banner -nostats -i work/voice_raw.wav -af "ebur128=peak=true" -f null - 2>&1 | grep -E "I:|LRA:|Peak:"
ffmpeg -hide_banner -nostats -i work/voice_raw.wav -af "astats=metadata=1:reset=0" -f null - 2>&1 | grep -E "RMS level dB|Peak level dB|Noise floor|Flat factor"
ffmpeg -hide_banner -nostats -i work/voice_raw.wav -af "silencedetect=noise=-50dB:d=0.4" -f null - 2>&1 | grep -c silence_start
```

How to read them (all approximate):

- **Noise floor**: take a stretch with no speech (a gap between phrases from `project/ingest.json` silences) and
  measure its RMS with `astats` on that excerpt (`-ss` and `-t` on input). Under -60 dB is clean. -50 to -60 dB is
  fine for a short. Above -45 dB is noisy and needs the denoise step.
- **Rumble**: a low frequency tone under 80 Hz. If the waveform sways in the silent stretch, or `astats` shows a high
  RMS in silence that is not hiss, apply the high pass.
- **Clipping**: `Flat factor` above 0 or `Peak level` at 0 dB means clipped samples. Clipping cannot be repaired
  reliably. `adeclick` helps with clicks, not with hard clipping. Tell the user to re record the line if it is bad.
- **Level range**: `LRA` above 10 LU in a talking head usually means the voice level drifts or the speaker moves.
  A compressor will help.

Write the numbers in a short note in the project folder so the after numbers can be compared.

## 2. The conservative chain

Order matters: remove what is not voice first, then shape, then control level, then limit. Build the chain one step
at a time and keep only the steps the diagnosis called for.

```
ffmpeg -v error -y -threads 2 -i work/voice_raw.wav -af "
highpass=f=80:poles=2,
afftdn=nr=10:nf=-45:tn=1,
equalizer=f=250:t=q:w=1.2:g=-2,
equalizer=f=3000:t=q:w=1.0:g=1.5,
acompressor=threshold=-20dB:ratio=3:attack=15:release=150:makeup=3,
deesser=i=0.4:m=0.5:f=0.5,
alimiter=limit=0.89:level=disabled
" work/voice_clean.wav
```

This exact chain parsed and ran on ffmpeg 8 on a synthetic test tone. Filters and option names vary a little between
ffmpeg builds, so run `ffmpeg -h filter=NAME` if one is refused, and tell the user which step you dropped.

What each step does and when to skip it:

| Step | Purpose | Starting value | Skip when |
| --- | --- | --- | --- |
| `highpass=f=80:poles=2` | removes rumble, wind, handling noise | 70 to 100 Hz; 120 Hz for a bright thin voice only if rumble is strong | never harmful at 80 Hz for speech |
| `afftdn` | steady noise (hiss, fan) | `nr` 6 to 12 dB, `nf` set near the measured floor, `tn=1` tracks noise | noise floor is already under -60 dB |
| `equalizer` at 250 Hz, g -2 | reduces boxy or boomy proximity | -1 to -3 dB, wide Q | voice already sounds thin |
| `equalizer` at 3 kHz, g +1.5 | helps words read on a phone speaker | +1 to +2 dB | voice is already harsh |
| `acompressor` | evens level so quiet words are not lost | ratio 2 to 4, threshold -18 to -24 dB, attack 10 to 25 ms, release 120 to 250 ms | LRA is already under 6 LU |
| `deesser` | softens harsh s sounds | `i` 0.2 to 0.5 | no harshness |
| `alimiter` | catches stray peaks before loudness step | `limit=0.89` is about -1 dBFS | never skip as a last guard |

Rules that keep the voice natural:

- Denoise at most 12 dB. More than that gives a watery, phasey sound. If it needs more, the recording needs a better
  fix at the source (a closer microphone, a quieter room).
- Two light passes of 4 dB each are not better than one pass of 8 dB. Use one.
- Never boost more than 3 dB in any EQ band without a measured reason.
- Compression makeup gain should bring the average level up by about as much as the compressor takes off the peaks,
  so the loudness step later has less to do. Do not push the voice into the limiter.
- Do not use a gate on speech to hide noise. A gate chops word endings and breath, and the room tone pumping on and
  off is easy to hear. If you must, use `agate=threshold=0.02:ratio=2:attack=10:release=250` very gently.

Hum at 50 or 60 Hz and its harmonics: instead of a deep notch you can apply a narrow `bandreject` at the mains
frequency, for example `bandreject=f=50:width_type=q:w=30`, then check with `astats` that speech did not lose body.

Room echo: ffmpeg cannot remove it well. A mild high pass at 100 Hz and less compression helps a little. Tell the
user the honest limit and offer to re record or use a dedicated dereverb tool of their own.

Neural denoise (`arnndn`) needs a separate model file that is not bundled with ffmpeg and the user must supply a model
they have a licence for. Do not assume it exists. Offer it as an option only.

## 3. Proving it worked

Do not call the audio clean because the command exited 0. Run the same measurements on the cleaned file and compare:

| Check | Pass condition |
| --- | --- |
| Noise floor | lower than before by 3 dB or more, and under -55 dB if it started above -50 dB |
| Speech level | integrated loudness within 6 LU of the raw, no new clipping, true peak at or under -1 dBTP |
| LRA | at or under about 8 LU for a short form talking head (a compressor ran) |
| Clicks | `adeclick` was not needed, or the click count dropped |
| Word survival | transcribe a 20 s excerpt of the clean file with the same whisper command and compare words with the raw transcript; no new missing or garbled words |
| Spectrum sanity | `aspectralstats` or a spectrogram image (`showspectrumpic`) shows no hard cutoff below 8 kHz that was not there before |

To make a spectrogram still the user can look at: `ffmpeg -i work/voice_clean.wav -lavfi showspectrumpic=s=1200x400 work/spec_clean.png`.
Look at the image, and compare with the raw one.

Then make a short A/B pair: 8 to 10 s of raw and the same 8 to 10 s cleaned, with clear names, and tell the user
which two files to play. Say plainly that you could not listen.

## 4. Applying the clean voice in the Agent Editor

The Agent Editor render takes the audio from the original source file. It does not read a separate cleaned file by
itself. Choose one of these, and say which you chose:

1. **Clean before ingest**: make a cleaned copy of the source (video copied, audio replaced with the cleaned one),
   then ingest that copy. Cuts and captions are then made on the same audio.
   `ffmpeg -i SOURCE -i work/voice_clean.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest work/source_clean.mp4`
   Keep the cleaned audio the same length as the video. If the clean step changed length, stop and find out why.
2. **Clean after render**: run the chain on the exported file's audio during the loudness step
   (`ae-loudness-mastering`). Cuts are already final, so word timing is unaffected.

Do not change the audio timing in either route. A chain with only the filters above does not change length.

## 5. Worked example

A local bakery owner recorded with a phone on a stand, arm's length, kitchen fan running.

- Diagnosis: noise floor -41 dB (fan), integrated -27 LUFS, LRA 12 LU, no clipping, a rumble sway in the gaps.
- Plan: high pass 80 Hz, `afftdn=nr=12:nf=-42`, mild 250 Hz cut, compressor ratio 3, de esser 0.3, limiter.
- After: noise floor -52 dB (11 dB better), integrated -21 LUFS, LRA 7 LU, true peak -2.1 dBTP.
- Word survival: 20 s excerpt, 58 of 58 words match. Spectrogram shows no new hard cutoff.
- Report: "Noise went from -41 to -52 dB, level is steadier. I checked numbers and the spectrogram, I could not
  listen. Please play `ab_raw.wav` then `ab_clean.wav`. If the voice sounds watery, I will lower the denoise to 8 dB."

## 6. Failure modes

- Denoising too hard: watery voice, the ends of words vanish. Lower `nr`, keep `tn=1`.
- Compressing twice (here and again in a platform or another tool): breathing and pumping. Compress once.
- Editing the original: never. Work on copies.
- Judging by headphones only: check on a phone speaker too, because the target audience likely uses one.
- Fixing clipped audio with filters: it cannot be done well. Re record the line.
- Cleaning after music is mixed in: always clean the voice alone first.

## 7. Checklist

- [ ] Profile read, recording method and tolerance recorded.
- [ ] Original kept, work done on a copy.
- [ ] Before measurements saved (noise floor, loudness, LRA, peak).
- [ ] Only the steps the diagnosis called for were used; denoise at most 12 dB.
- [ ] After measurements saved and compared.
- [ ] Word survival check on an excerpt.
- [ ] Spectrogram image looked at.
- [ ] A/B files named for the user, honest "I could not listen" line in the report.
- [ ] Cleaned audio has the same length as the picture before it is used.

Hand off to: `ae-ingest-and-transcribe`, `ae-music-bed-and-mixing`, `ae-loudness-mastering`, `ae-edit-qa-gates`, `ae-laptop-load-safety`.
