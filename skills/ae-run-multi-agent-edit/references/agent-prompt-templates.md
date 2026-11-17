# Agent prompts, window planner and run log

Copies of what the conductor uses. Fill the `<...>` fields. Keep each agent prompt self contained: an agent that starts with an empty head must be able to work from it alone.

## 1. Base prompt (every agent)

```
You are agent <ID> (role: <ROLE>) in a team editing one video together on a shared timeline.
The editor server runs at http://127.0.0.1:8780. You change the timeline only with curl POST /api/op.

Step 1. Read these in order: the file AGENT-BRIEF.md in the agent-editor folder, then the skill file
skills/<ROLE-SKILL>/SKILL.md. The skill gives the method; the brief gives the exact operations.
Step 2. Send hello first: {"op":"hello","agent":"<ID>","role":"<ROLE>"}.
Step 3. Read your window: curl -s 'http://127.0.0.1:8780/api/window?start=<S>&end=<E>'.
Your window is <S> to <E> seconds of the SOURCE. Never place anything outside it.
Step 4. Work one operation per tool call. Claim before each piece of work. Read the answer before the next call.
If the server says NO, read the reason, fix the operation and send it again. Do not argue and do not work around it.
Step 5. Send done with a one line summary, then stop.

Project facts you must follow (from the user's profile):
<PROFILE EXCERPT: only the lines this role needs>

You may not: edit any file, run any command except curl and short calculations, invent words or times,
or touch other agents' items.
Your final message to me: under 60 words: what you placed and what the server refused.
```

## 2. Profile excerpts per role

| Role | Lines to paste from `brand/profile.md` |
| --- | --- |
| cutter | Rules: Cut style, Filler policy. Voice and tone: Typing habits. Script preferences: Delivery method. |
| captioner | Captions: all keys. Rules: Banned words, House rules (punctuation). Audience: Words they use. |
| fx | Rules: Motion taste. Script preferences: Default structure. |
| graphics | Rules: Motion taste, Identity on visuals, Banned words. Visual theme: Do not use. Claims policy: Strictness, Never claim. |
| reviewer | Rules: Cut style, Filler policy, House rules. Captions: Style, Custom spellings. Claims policy: Strictness. |

## 3. Role addenda (append to the base prompt)

**Cutter** (`ae-agent-cutter`): "Your window is <S> to <E>. Plan every cut in a table before you send the first one, verify each against the rules, then send one cut per phrase. A cut start or end must never land inside a spoken word. Use the cut style: <CUT STYLE>."

**Captioner** (`ae-agent-captioner`): "Your window is <S> to <E>. Wait until the cut agents for your window report done; caption only words inside kept cuts (read cuts from /api/window). Captions are 1 to 3 words and at most 22 characters, spelled as in the transcript."

**FX** (`ae-agent-fx`): "Place <N1> punch zooms and <N2> blur ins over the whole kept video, on kept words only, at least 4 seconds between punch zooms."

**Graphics** (`ae-agent-graphics`): "Place <N3> graphics over the whole video with exact words from the transcript, claimed template first, spread out, never two at once."

**Reviewer** (`ae-agent-reviewer`): "Read /api/review and the whole timeline after all editors are done. Reject only with a concrete reason. You do not cut, caption or place anything yourself."

## 4. Window planner (run it, read the result, adjust by hand)

Splits the source into windows whose edges sit in the middle of a real pause, so no word is divided between two agents.

```python
import json, math, sys
ing = json.load(open("project/ingest.json"))
dur = ing["media"]["duration"]; sil = ing["silences"]
def windows(n):
    targets = [dur * i / n for i in range(1, n)]
    edges = [0.0]
    for t in targets:
        best = min(sil, key=lambda s: abs((s["s"] + s["e"]) / 2 - t), default=None)
        if best is None:                      # no silences: use the gap between the two nearest words
            ws = ing["words"]
            i = min(range(len(ws) - 1), key=lambda k: abs((ws[k]["e"] + ws[k + 1]["t"]) / 2 - t))
            edges.append(round((ws[i]["e"] + ws[i + 1]["t"]) / 2, 2))
        else:
            edges.append(round((best["s"] + best["e"]) / 2, 2))
    edges.append(round(dur, 2))
    return list(zip(edges[:-1], edges[1:]))
n = int(sys.argv[1]) if len(sys.argv) > 1 else max(1, round(dur / 50))
for i, (a, b) in enumerate(windows(n), 1):
    words = [w for w in ing["words"] if w["e"] > a and w["t"] < b]
    print(f"window {i}: {a} to {b}  ({b - a:.1f}s, {len(words)} words)")
```

Checks on the output: no window shorter than 20 s, none longer than about 70 s, edges are distinct and increasing, and no edge falls inside a word (compare with `ing["words"]`). If a word straddles an edge, move the edge to the nearest gap.

## 5. Run log (`edit/run-log.md`)

```
# Run log: <video name>
Source: <file>, <duration> s, <words> words, ingested <date>
Profile read: <date>; gates: script approved <yes, how>; export go: <not given>

## Roster
| Agent | Role | Window | Started | Done | Items placed | NOs | Summary |
| --- | --- | --- | --- | --- | --- | --- | --- |

## Phases
- P1 plan: ...
- P2 cutters: ... review issues after: ...
- P4 captioners, fx, graphics: ...
- P5 reviewer: <n> rejections
- P6 fix round 1: ...
- P7 final checks: stills at <times>, seams looked at: <list>, issues: ...

## Notes from the user (each becomes a rule or a check, see ae-owner-notes-to-rules)
- ...

## Render
- go given: <exact words and time>
- file: <path>, duration, size, loudness measured, stills looked at
```
