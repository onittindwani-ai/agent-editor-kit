---
name: ae-loudness-mastering
description: Sets, measures and verifies final loudness and true peak, with two pass ffmpeg loudnorm, platform target ranges, and a re mux that leaves the picture untouched. Use when the user says "the volume is too low", "too loud", "normalise the audio", "what LUFS", "true peak", "will Instagram or YouTube change my volume", or after any export and before delivery.
---

# ae-loudness-mastering

Loudness is how loud the whole video feels, measured over its length in LUFS. True peak is the highest level the
reconstructed audio signal can reach, in dBTP. Mastering means landing both inside a target and proving it by
measuring the actual file the viewer will get. A single command that exits cleanly proves nothing.

## 0. Read the profile first

Read `brand/profile.md`. If it is missing or a section it needs is empty, stop and run `ae-setup-interview` for that
section (ask the user, with options), do not guess. This skill needs `## Sound` (target loudness if the user has one),
`## Platforms and formats` (where the video will be posted) and `## Rules` (delivery gates).

If the platform answer is missing, ask:

1. Where will this video be posted (pick any)?
   a) Instagram Reels. b) YouTube Shorts. c) TikTok. d) YouTube long form. e) LinkedIn. f) Website or ads.
2. Which loudness target do you want?
   a) The kit default (about -16 LUFS, -1 dBTP; fits mobile viewing well). b) Slightly louder (about -14 LUFS).
   c) Quieter, more dynamic (about -18 LUFS, for long form with music). d) Whatever each platform recommends.
3. Do you want one master for every platform or a separate file per platform?
   a) One master. b) One per platform.

## 1. Vocabulary in plain words

- **Integrated loudness (LUFS or LKFS)**: average perceived loudness of the whole file. Higher (closer to 0) is louder.
- **LRA (loudness range)**: how much loudness varies, in LU. A talking head with music is usually 3 to 9 LU.
- **True peak (dBTP)**: the peak after oversampling, which can exceed the sample peak. Keep it at or under -1 dBTP so
  lossy encoders (AAC and similar) do not clip.
- **Sample peak (dBFS)**: highest stored sample. Always lower than or equal to the true peak.

## 2. Targets (approximate; platforms change them, verify)

The default for short vertical video in this kit is **-16 LUFS integrated, true peak at or under -1 dBTP**. That is a
common, safe choice for phone viewing. The numbers below are commonly cited ranges, not guarantees. Platforms change
their processing without notice. Tell the user to check the platform's current guidance, and to compare the posted
video's volume with other videos on their own phone.

| Destination | Typical range people use | Notes |
| --- | --- | --- |
| Instagram Reels, TikTok, Shorts | -16 to -13 LUFS, true peak -1 dBTP | Loudness is often reported as lightly normalised or not at all. A quiet file can sound weak next to loud neighbours. |
| YouTube long form | -16 to -12 LUFS | YouTube is commonly reported to turn loud files down to a reference level, and not to raise quiet files. Hedge when saying so. |
| LinkedIn, website embeds | -16 to -14 LUFS | No known normalisation; the file plays as it is. |
| Podcast style long form | -19 to -16 LUFS | Optional. |
| Broadcast style delivery | follow the specification the user supplies | Not the kit default. |

Rules of thumb:

- Never exceed -14 LUFS by pushing a limiter hard just to be louder; the voice flattens and distorts.
- For long form with background music, -16 to -18 LUFS leaves room for quiet parts to breathe.
- Always leave true peak at or under -1 dBTP, even for platforms that do not require it.

## 3. The measuring tools

Measure the file the viewer receives, after the final export. Light jobs, one at a time:

```
ffmpeg -hide_banner -nostats -i FILE.mp4 -vn -af "ebur128=peak=true" -f null - 2>&1 | grep -E "^\s+(I|LRA|Peak):"
```

That prints `I:` (integrated LUFS), `LRA:` and `Peak:` (true peak in dBFS from the summary). Also useful:

```
ffmpeg -hide_banner -nostats -i FILE.mp4 -vn -af "loudnorm=I=-16:TP=-1:LRA=11:print_format=json" -f null - 2>&1
```

This prints the measured block (`input_i`, `input_tp`, `input_lra`, `input_thresh`, `target_offset`). It does not
change the file when output goes to `-f null -`.

Check `ffprobe` too: `ffprobe -v error -show_entries stream=codec_name,sample_rate,channels,duration -of default=nw=1 FILE.mp4`
so you know sample rate, channels and the audio length.

## 4. Two pass loudnorm (the accurate way)

A single pass `loudnorm` guesses while it runs ("dynamic" mode) and can leave the result a little off target, or
squash the dynamics. Two passes measure first, then apply a correction using the measured numbers, which lets it use a
single linear gain when possible.

**Pass 1, measure only:**

```
ffmpeg -hide_banner -nostats -i INPUT.wav -af "loudnorm=I=-16:TP=-1:LRA=11:print_format=json" -f null - 2>&1
```

Copy the five numbers from the JSON block: `input_i`, `input_tp`, `input_lra`, `input_thresh`, `target_offset`.

**Pass 2, apply using those numbers (replace the example values):**

```
ffmpeg -v error -y -threads 2 -i INPUT.wav -af "loudnorm=I=-16:TP=-1:LRA=11:measured_I=-24.81:measured_TP=-19.17:measured_LRA=0.00:measured_thresh=-34.81:offset=-0.04:linear=true:print_format=summary,aresample=48000" OUTPUT.wav
```

Tested on ffmpeg 8 with a synthetic file: pass 1 reported -24.81 LUFS input, pass 2 produced -16.0 LUFS integrated
when re measured. Notes:

- `linear=true` asks for a plain gain change. If the measured values make a linear change impossible without
  breaking the true peak limit (for example the input has a high peak relative to its loudness), ffmpeg falls back to
  dynamic processing. Check the pass 2 result by measuring the output, not by trusting the option.
- `loudnorm` works internally at a high sample rate. Add `aresample=48000` (or the file's original rate) at the end,
  otherwise the output may be at 192 kHz.
- `LRA=11` is a ceiling; if the input range is already under it, nothing is squashed.
- If the voice is very dynamic and the true peak limit forces the gain down, the integrated loudness may land lower
  than the target. Add the compressor and limiter from `ae-audio-cleanup` first, then re measure.
- Do two pass on the whole mix (voice, music, effects), because the music and effects change the loudness.

A small helper pattern for agents: run pass 1, parse the JSON with `python3 -c`, build the pass 2 command from the
numbers, run it, then re measure and write all values to `qa/loudness.txt`.

## 5. Putting the mastered audio back without touching the picture

Never re encode the video just to fix audio. Copy the video stream and replace the audio:

```
ffmpeg -v error -y -threads 2 -i EXPORT.mp4 -i mastered.wav -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart FINAL.mp4
```

Checks after the mux:

- Video stream is bit for bit the same codec and dimensions (`-c:v copy` guarantees no re encode).
- Audio length equals video length within one frame (compare `ffprobe` durations). If the audio is longer, `-shortest`
  trims it; if it is shorter, the end is silent, so investigate.
- Audio and video start together: the first word still starts at the same time as in the export (look at a still and
  a waveform of the first 2 seconds).
- `+faststart` moves the index to the front so phones start playing sooner.

If colour tags matter (`color_range`, `color_primaries`), copy the video stream so they are unchanged.

## 6. What the Agent Editor already does

The shipped render normalises with a single pass `loudnorm=I=-16:TP=-1:LRA=11` at the end of its audio chain, after
mixing the voice and any music. That usually lands close to the target, but a single pass is an estimate. Therefore:

1. After the one export, measure it with section 3.
2. If integrated loudness is within 1 LU of the target and true peak is at or under -1 dBTP, accept it and record the numbers.
3. If not, run the two pass mastering above on the exported audio and mux it back with a copied video stream. This
   does not need a new picture render, so it does not break the export once rule (see `ae-export-once-workflow`).
4. Do not run loudnorm twice in a row on already normalised audio unless you measured a miss; it can compress needlessly.

## 7. Tolerances for pass or fail

| Measure | Pass | Needs fixing |
| --- | --- | --- |
| Integrated loudness | within 1 LU of the target (for example -17 to -15 for a -16 target) | farther away |
| True peak | at or under -1.0 dBTP | above -1.0 dBTP |
| LRA | under about 11 LU for short form | over, check for uneven music or speech |
| Clipping | no samples at full scale | any |
| Audio length vs video | within one frame | longer or shorter |

Also note if the video has no audio stream (a broken mux) or a stereo to mono difference the user did not expect.

## 8. Worked example

A 34 s vertical short for a bakery, destination Instagram Reels and YouTube Shorts, one master.

- Export measured: I -17.9 LUFS, LRA 5.1 LU, true peak -0.4 dBTP. Fails (peak too high, a bit quiet).
- Pass 1 on the exported audio: input_i -17.88, input_tp -0.41, input_lra 5.10, input_thresh -28.0, offset 0.5.
- Pass 2 with those values and `linear=true`. Re measure: I -16.0, TP -1.6, LRA 5.0. Passes.
- Mux with `-c:v copy`. Durations: video 34.033 s, audio 34.027 s. Within one frame. The first word starts at the same
  frame as in the export (checked on a still and a waveform).
- Record in `qa/loudness.txt`: before and after numbers, the exact commands, the date.
- Tell the user: "Measured -16.0 LUFS and -1.6 dBTP. Platforms may change volume, so compare it with other videos on
  your phone after posting."

## 9. Failure modes

- Trusting the target without measuring the final file.
- Measuring only the voice track and forgetting the music and effects change the result.
- Letting `loudnorm` output at 192 kHz: always add `aresample`.
- Pushing louder than -14 LUFS with a limiter: distortion and fatigue.
- A true peak above -1 dBTP: the encoder can clip.
- Re encoding the video to fix audio: lowers picture quality and breaks the export once rule.
- Mastering before the cut is final: any later cut change shifts the measurements.
- Believing a platform rule from memory: platforms change; hedge and tell the user to check.

## 10. Checklist

- [ ] Profile read, targets chosen and written in `## Sound`.
- [ ] Final export measured (I, LRA, true peak) and values saved.
- [ ] If outside tolerance, two pass applied to the whole mix and re measured.
- [ ] Video copied, audio replaced, durations compared, start alignment looked at.
- [ ] Sample rate is 48 kHz (or the source rate), not 192 kHz.
- [ ] No clipping; true peak at or under -1 dBTP.
- [ ] Platform statements hedged; user told to verify on their own phone.
- [ ] Commands and numbers recorded in the QA report.

Hand off to: `ae-export-once-workflow`, `ae-edit-qa-gates`, `ae-music-bed-and-mixing`, `ae-audio-cleanup`, `ae-publish-packaging`.
