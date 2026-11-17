---
name: ae-laptop-load-safety
description: Keeps the user's computer from freezing or restarting during video work: one heavy job at a time, thread caps, low priority, memory and disk checks, small resumable steps, and a recovery routine after a freeze. Use before any transcription, 4K encode, render or batch job, when the user says "my laptop is lagging", "it froze", "fans are loud", "out of disk space", "run it safely", or when several agents are about to run at once.
---

# ae-laptop-load-safety

A video edit can use all of a laptop's processor, memory and disk at once. A pile of parallel heavy jobs can freeze or
restart the machine and lose work. This skill makes heavy work boring and safe: one job at a time, low priority,
checked before starting, resumable if it stops, and recoverable after a crash.

## 0. Read the profile first

Read `brand/profile.md`. If it is missing or a section it needs is empty, stop and run `ae-setup-interview` for that
section (ask the user, with options), do not guess. This skill needs `## Rules` (machine limits, working hours,
anything the user said about the computer) and `## Platforms and formats` (4K sources and long videos are heavier).

If the machine facts are not in the profile, ask:

1. What computer is this?
   a) A laptop with 8 GB memory or less. b) A laptop with 16 GB. c) A laptop with 32 GB or more. d) A desktop.
   e) A cloud or remote machine.
2. Is the machine used for other work during the edit?
   a) Yes, I keep many apps open. b) A few apps. c) Only this.
3. How much free disk space is there on the drive that holds the project?
   a) Under 10 GB. b) 10 to 50 GB. c) More than 50 GB. d) I do not know, please check.
4. How should long jobs run?
   a) Only when I say. b) In the background at low priority. c) Overnight, after I confirm.

Record these in `## Rules` under "Machine limits". Apply the stricter settings in section 4 for a small or busy machine.

## 1. What counts as heavy

These are heavy. Only one runs at a time, always:

- Transcription with a whisper style model (large model, whole video).
- Proxy creation and any full video encode (`ffmpeg` with `libx264`, 4K decode, long files).
- The Agent Editor render (`POST /api/render`).
- Headless browser or Remotion renders and any frame by frame image export.
- Person cutouts and other machine learning mattes.
- Copying very large folders and zipping the project.

These are light and may overlap with one heavy job: reading JSON, `curl` operations to the editor server, `ffprobe`,
single frame stills, measuring loudness of a short excerpt, writing text files.

Agents that call the server's operations (cuts, captions, graphics, effects) do light work. Many such agents can run
together. What must not run together is the heavy list above.

## 2. The five rules

1. **One heavy job at a time.** Across all sessions and all agents on the machine, not per agent. Use the lock in
   section 5.
2. **Low priority.** Start every heavy command with `nice -n 15` (the shipped ingest and render already do this).
3. **Cap threads.** `ffmpeg -threads 4` on a normal laptop, `-threads 2` on a small or busy machine. Tools with their
   own worker option (a render tool's concurrency flag) are set to 1 or 2.
4. **Small steps that can resume.** Work in chunks (one clip, one range of seconds), keep outputs on disk, and make
   each step safe to run again. A crash should cost minutes, not hours.
5. **Check before you start, and stop if the check fails.** Section 3.

Add a sixth for teams of agents: **a sub agent that runs a heavy job must be the only sub agent doing so.** Other
sub agents may place cuts and captions through the server at the same time because those are tiny requests.

## 3. The calm check (run before every heavy job)

Run the read only script in `references/calm_check.sh`:

```
sh references/calm_check.sh /absolute/path/to/the/project
```

It prints CPU count, one minute load average, free disk in GB, the number of heavy looking processes, and whether the
system is paging memory to disk (on macOS it compares `vm_stat` page outs over 5 seconds). It exits 0 when calm and 1
when it says WAIT. The starting thresholds are:

| Signal | WAIT when | Why |
| --- | --- | --- |
| Load average (1 min) | above 70 percent of the CPU count | the machine is already busy |
| Free disk on the project drive | under 5 GB (raise to 10 GB for 4K) | renders and caches need room; a full disk corrupts files |
| Paging | more than about 300 page outs in 5 s | memory is exhausted; swap thrash causes freezes |
| Heavy processes | any `ffmpeg`, whisper, Remotion or Blender already running | another heavy job is active |

Notes and honest limits:

- "Free memory" shown by the system can look healthy while the machine pages hard. Trust the paging signal more
  than a free memory figure. A large swap file is normal on macOS; active paging is the problem.
- The thresholds are approximate. If the user's machine is fine at higher load, raise them in the environment
  variables the script reads (`AE_MAX_LOAD_FRACTION`, `AE_MIN_FREE_GB`) and note the change.
- On Linux the script skips the paging check; use `free -m` and `cat /proc/pressure/memory` (if present) by hand.
- The script only reads. It never kills anything.

If the check says WAIT: do not start. Wait 30 to 60 seconds and check again, up to a few times. If still not calm,
tell the user what is busy and ask. Never kill the user's own apps.

## 4. Settings by machine size

| Machine | ffmpeg threads | Parallel whisper | Proxy size | Render notes |
| --- | --- | --- | --- | --- |
| 8 GB or less, or heavy multitasking | 2 | 1, use a smaller model if quality allows | 720p | render only when nothing else is open; ask the user to quit big apps |
| 16 GB | 4 | 1 | 720p | one render at a time; avoid 4K sources, cut a 1080p proxy first |
| 32 GB or more | 4 to 6 | 1 | 720p | still one heavy job at a time |
| Remote or cloud | per its size | 1 | 720p | check cost before long runs; ask the user |

For whisper style transcription the model size is the main memory driver. Choose the model with the user: a faster
smaller model for a first pass, the larger one only for the final transcript. If quality drops, say so.

For 4K sources: do not decode 4K for review. The editor makes a 720p proxy for the screen and renders from the
original only at export. If 4K decode is too heavy, ask the user whether a 1080p render is acceptable.

## 5. The lock (one heavy job across everything)

`references/heavy_run.sh` wraps a command in a lock, waits for calm, then runs it at low priority:

```
sh references/heavy_run.sh ffmpeg -v error -y -threads 4 -i in.mp4 out.mp4
```

How it works (tested here with a simple command): it uses an atomic `mkdir` lock folder, writes its process id into
it, removes the lock when it finishes or is interrupted, and clears a stale lock whose process no longer exists.
It waits up to 15 minutes by default (`AE_WAIT_MAX_S`), runs the calm check in a loop and then runs `nice -n 15` on
your command. Environment variables:

- `AE_LOCK_DIR`: where the lock lives (default in the system temp folder; every agent must use the same one).
- `AE_SKIP_CALM=1`: skip the calm check (for tiny jobs only).
- `AE_DISK_PATH`: which drive to check.

If the machine restarted, a lock folder can remain; the script removes it when its stored process id is gone. If the
script never finishes waiting, report it and ask the user; do not delete the lock by hand with a wildcard.

The Agent Editor's own render and ingest call `nice -n 15` and `-threads 4` already, but they do not take this lock.
So before starting one of them, take the lock yourself or run the calm check, and do not start two together.

## 6. Resumable work

Design every long step so it can start again from the middle:

- **Transcription**: for a long file, transcribe in chunks of 5 to 10 minutes into separate JSON files, then merge
  with time offsets. A chunk that finishes is never redone.
- **Render of many pieces**: one piece per command (a clip, a scene, a range of frames), outputs kept in a folder
  with a numbered name. Re run only the missing numbers.
- **Stills**: one frame per command; they are fast and safe.
- **Concatenation**: build the pieces first, join at the end with the concat demuxer, check durations.
- **Always write to a temp name then rename.** Write `part.mp4.tmp` then rename on success, so a crash never leaves a
  half file that looks complete.
- **Keep a step log** (`work/steps.md`): step, start time, end time, result, output file. After a crash the log tells
  you which steps are done.

## 7. Honest time estimates

Before starting a heavy step, give the user a range, never a single number, and the reason. Example:
"Transcribing 6 minutes with the larger model: about 1 to 3 minutes on this machine. Render of 34 s of 1080p: about 3
to 6 minutes. I will check every 30 seconds." After the first run, record the real time in `work/steps.md` and use it
for the next estimate. If a step is running well over the estimate, tell the user right away with the new range.

## 8. Recovery after a freeze or restart

Do these in order, and do not assume anything finished:

1. Tell the user what you know and what you do not. Do not start any heavy work yet.
2. Check what survived: is the editor server still running (`curl -s http://127.0.0.1:8780/api/state`), does the state
   file exist, how many cuts, captions and graphics does it hold? The server saves state to the project folder. If
   the state is empty, check for a saved copy before assuming loss.
3. Check the disk: free space, and look for half written files (names ending `.tmp`, zero byte files, mp4 files
   that `ffprobe` cannot open). List them with absolute paths. Do not delete automatically.
4. Check the lock folder and the step log. Remove a stale lock only through `heavy_run.sh`.
5. Check for orphan processes: `pgrep -fl ffmpeg` and `pgrep -fl whisper`. If one runs with no parent job, tell the user
   and ask before stopping it.
6. Run the calm check. Only when calm, resume the missing step only.
7. Report: what survived, what was redone, how long it took, and what changed to prevent a repeat (fewer threads,
   one agent less).
8. Add a rule or check for the cause (see `ae-owner-notes-to-rules`): for example "never run a render while
   transcribing".

## 9. Cleanup and disk hygiene

- Clean only your own scratch files, using literal absolute paths. Never wildcards, never relative paths.
- Prefer the system Trash for anything the user might want (`trash "/absolute/path"` on macOS).
- Keep at least 5 GB free (10 GB for 4K work). Warn the user at 10 GB.
- Large intermediate files (renders of single scenes, extracted frames) belong in a work folder the user can clear;
  say how big it is.
- Never empty the Trash. The user does that.

## 10. Worked example

A 16 GB laptop, a 3 minute 4K take, seven agents ready.

1. Calm check: load 1.2 of 8, 18 GB free, no paging. Calm.
2. `heavy_run.sh` runs ingest at low priority: 720p proxy first (one job). Waits for it to finish.
3. Transcription starts only after the proxy finished (one job). It runs in 2 chunks. Chunk 2 stalls after a
   restart; the step log shows chunk 1 done. Only chunk 2 is redone.
4. The seven agents send tiny `curl` operations. These do not need the lock.
5. Export day: ask the user to quit large apps, run the calm check, one render request, poll every 30 s.
6. Report: ingest 2 to 3 min, transcription 3 to 5 min, render 4 to 7 min, all one at a time; the machine stayed
   responsive.

## 11. Failure modes

- Starting transcription while a render runs: the classic freeze.
- Starting a second render because the first "looks stuck": check the render state first.
- Trusting "free memory" while the system is paging.
- Full disk during a render: a truncated file that looks fine until played.
- A lock that nobody clears after a crash: use the stale lock logic.
- Estimates given as a single number, then missed: always give a range.
- Hiding that a job had to wait: tell the user.

## 12. Checklist

- [ ] Profile read; machine size and usage recorded.
- [ ] Only one heavy job planned; lock taken (or the calm check run).
- [ ] `nice -n 15` and a thread cap used.
- [ ] Disk free at least 5 GB (10 GB for 4K); no paging; no other heavy process.
- [ ] Work in resumable steps with temp names and a step log.
- [ ] Time estimate given as a range, then compared with the real time.
- [ ] After any crash: survivors checked, only the missing step redone, cause turned into a rule.
- [ ] Deletes only with literal absolute paths and the Trash.

Hand off to: `ae-export-once-workflow`, `ae-run-multi-agent-edit`, `ae-ingest-and-transcribe`, `ae-install-and-run`, `ae-owner-notes-to-rules`.
