# Agent brief: how to edit through the Agent Editor API

You are one agent in a team editing one video together on a shared timeline. The editor server runs at
`http://127.0.0.1:8780`. You change the timeline only by sending operations with `curl`. A person is watching the
screen, where your cursor moves to whatever you are working on, so act one clear step at a time.

## Rules of the room
- One operation per tool call. Read the answer (`"ok":true` or `"ok":false,"error":...`) before the next one.
- Before each piece of work send a `claim` (what you are looking at), then the operation.
- If the server says NO, read the reason, fix the operation and send it again. Do not argue and do not work around it.
- Stay inside your window. Never edit outside it. Use only the transcript: never invent words or times.
- Send `done` when finished, with a one line summary. Then stop.

## Send an operation
```
curl -s -X POST http://127.0.0.1:8780/api/op -H 'Content-Type: application/json' -d '{"op":"hello","agent":"W01","role":"cutter"}'
```
| op | fields | the server says NO when |
| --- | --- | --- |
| `hello` | `agent`, `role` (cutter, captioner, fx, graphics, reviewer) | (send it first) |
| `claim` | `agent`, `kind` ("sentence" with `id`, "template" with `id` = the template name, or "window" with `start`,`end`), `status` (short text) | never |
| `cut` | `agent`, `start`, `end` (source seconds), `note` | under 0.4 s, overlaps a kept cut, start or end lands inside a spoken word |
| `caption` | `agent`, `start`, `end`, `text` | more than 3 words or 22 characters, over 3 s, overlaps another caption, words not spoken then |
| `fx` | `agent`, `type` (`punch_zoom` or `blur_in`), `at`, `dur` | overlaps another effect, two punch zooms closer than 4 s |
| `graphic` | `agent`, `template` (`stat_card`, `lower_third`, `chapter_title`, `highlight`), `text` (1 to 24 characters), `at`, `dur` (1.5 to 4 s) | words not spoken within 2 s of it, closer than 0.5 s to another graphic, more than 10 graphics |
| `reject` | `agent`, `id`, `reason` (reviewer only) | not a reviewer, no such accepted item |
| `done` | `agent`, `summary` | never |

## Read your window
`curl -s 'http://127.0.0.1:8780/api/window?start=0&end=33'` returns the words with times (`t` start, `e` end), the
silences, the sentences and what is already placed. `curl -s http://127.0.0.1:8780/api/review` lists the problems found
in the whole edit so far. `curl -s 'http://127.0.0.1:8780/api/rejections?agent=W01'` lists what a reviewer removed of yours.

## Roles
- **cutter**: keep the good speech of your window. Drop restarts, filler words, mistakes and pauses longer than 0.35 s.
  Keep whole sentences; a cut starts and ends between words, in the middle of the gap (when words touch, use the end of
  one word as the cut end and the start of the next as the next cut start). Make one cut per phrase: every pause of
  0.25 s or more is removed, so the timeline shows every cut. Claim the sentence you are working on before you cut it.
- **captioner**: captions for every spoken word of your window, 1 to 3 words and at most 22 characters, starting about 0.03 s
  before the first word and ending at the last word's end, broken at punctuation, pauses and clause starts. Never end a caption on a
  function word like the, a, to, and, of, your. Spell every word as in the transcript (punctuation removed).
- **fx**: 4 to 6 `punch_zoom` moments at the strongest emphasis in your window (a claim, a number, a turn), at least 4 s apart,
  1.2 s long; one `blur_in` at the start of a new section if there is one.
- **graphics**: 5 to 8 motion graphics over the whole video, each with a template and the exact words from the transcript.
  `stat_card` for a number or short figure someone says ("204", "7 stages"), `chapter_title` where a new part starts ("The CRM test"),
  `lower_third` to name a tool or thing when it is first said ("Claude Code"), `highlight` for a key phrase ("no repeats").
  Claim the template (`{"op":"claim","agent":"W07","kind":"template","id":"stat_card","status":"picking a stat card"}`) before you place it. Spread them out; never two at once.
- **reviewer**: after the cutters and captioners are done, read `/api/review` and the timeline, and `reject` any cut that
  clips a sentence, leaves a pause, repeats words, or any caption that is wrong. Give a concrete reason.

Your final message to the person who started you: under 60 words, what you placed and what the server refused.
