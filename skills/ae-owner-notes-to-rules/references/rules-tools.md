# Rule and log tools

Save each block into `brand/tools/` (the first comment line gives the file name). Both only read files. `run_rules.py` runs a rule's check command without a shell and only for a short list of read only programs, so a rules file cannot delete or move anything.

## 1. run_rules.py: validate brand/rules.md and run the checks

```
python3 brand/tools/run_rules.py brand/rules.md
python3 brand/tools/run_rules.py brand/rules.md --run
```

```python
# file: run_rules.py
#!/usr/bin/env python3
"""Validate brand/rules.md and run the read only checks the rules carry.

    python3 run_rules.py brand/rules.md            # list rules, validate structure, show which have a check
    python3 run_rules.py brand/rules.md --run      # also run each active rule's Check command and report pass or fail

Rule format (one block per rule, blocks start with a line "## RULE-NNN"):

    ## RULE-007
    Statement: A caption never ends on a function word.
    Why: Note of 2026-05-02: captions that end on "the" look unfinished.
    Area: captions
    Strength: hard            (hard or default)
    Check: python3 brand/tools/check_caption_groups.py project/state.json --ingest project/ingest.json
    Applies to: ae-caption-style-and-grouping, ae-agent-captioner
    Added: 2026-05-02
    Status: active            (active, or "superseded by RULE-012")

A Check is optional (rules about taste are checked by eye). Commands are split into words and run without a shell. Only these programs
are allowed: python3, ffprobe, ffmpeg, curl, test, grep, shasum. Anything else is refused, so a rules file can never delete or move files.
Exit code: 0 everything valid and every run check passed, 1 a validation problem or a failed check, 2 unreadable file.
"""
import argparse, re, shlex, subprocess, sys

REQUIRED = ("Statement", "Area", "Strength", "Added")
ALLOWED = {"python3", "ffprobe", "ffmpeg", "curl", "test", "grep", "shasum"}


def parse(text):
    rules, cur = [], None
    for line in text.splitlines():
        m = re.match(r"^##\s+(RULE-\d+)\s*$", line)
        if m:
            cur = {"id": m.group(1)}
            rules.append(cur)
            continue
        if cur is not None:
            kv = re.match(r"^([A-Za-z ]+):\s*(.*)$", line)
            if kv:
                cur[kv.group(1).strip()] = kv.group(2).strip()
    return rules


def validate(rules):
    problems, ids = [], set()
    for r in rules:
        if r["id"] in ids:
            problems.append("%s appears twice" % r["id"])
        ids.add(r["id"])
        for k in REQUIRED:
            if not r.get(k):
                problems.append("%s: missing %s" % (r["id"], k))
        if r.get("Strength") and r["Strength"].split()[0] not in ("hard", "default"):
            problems.append("%s: Strength must be hard or default" % r["id"])
        st = r.get("Status", "active")
        if not (st.startswith("active") or st.startswith("superseded by")):
            problems.append("%s: Status must be active or superseded by RULE-NNN" % r["id"])
    for r in rules:
        m = re.match(r"superseded by (RULE-\d+)", r.get("Status", ""))
        if m and m.group(1) not in ids:
            problems.append("%s: superseded by %s, which does not exist" % (r["id"], m.group(1)))
    return problems


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("rules")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--timeout", type=int, default=120)
    a = ap.parse_args(argv)
    try:
        rules = parse(open(a.rules, encoding="utf-8").read())
    except OSError as e:
        print("cannot read rules:", e)
        return 2
    bad = validate(rules)
    active = [r for r in rules if r.get("Status", "active").startswith("active")]
    print("%d rules, %d active, %d with a check" % (len(rules), len(active), len([r for r in active if r.get("Check")])))
    for p in bad:
        print("PROBLEM:", p)
    failed = 0
    for r in active:
        chk = r.get("Check")
        if not chk:
            print("%s  manual    %s" % (r["id"], r.get("Statement", "")[:70]))
            continue
        if not a.run:
            print("%s  has check %s" % (r["id"], chk[:90]))
            continue
        try:
            argv_ = shlex.split(chk)
        except ValueError as e:
            print("%s  REFUSED  cannot parse: %s" % (r["id"], e))
            failed += 1
            continue
        if not argv_ or argv_[0] not in ALLOWED:
            print("%s  REFUSED  program not allowed: %s" % (r["id"], argv_[0] if argv_ else "(empty)"))
            failed += 1
            continue
        try:
            res = subprocess.run(argv_, capture_output=True, text=True, timeout=a.timeout)
        except (OSError, subprocess.TimeoutExpired) as e:
            print("%s  FAIL     %s" % (r["id"], e))
            failed += 1
            continue
        if res.returncode == 0:
            print("%s  pass" % r["id"])
        else:
            failed += 1
            tail = (res.stdout.strip().splitlines() or res.stderr.strip().splitlines() or [""])[-1]
            print("%s  FAIL     exit %d: %s" % (r["id"], res.returncode, tail[:100]))
    return 1 if (bad or failed) else 0


if __name__ == "__main__":
    sys.exit(main())
```

## 2. time_map.py: from a time in the render to the items on the timeline

```
python3 brand/tools/time_map.py project/state.json 14.2
```

```python
# file: time_map.py
#!/usr/bin/env python3
"""Turn a time the user saw in the rendered video into the source time and the items on the timeline at that moment.

    python3 time_map.py project/state.json 14.2 [--window 0.5]

The user watches the render (output time). The editor stores cuts, captions, graphics and effects in source time. This lists, for an output
time, the source time, the cut, and every accepted caption, graphic and effect that is on screen within the window around it, so a note
such as "at 0:14 the caption is wrong" points at an exact item id. Exit code 0 found a cut, 1 the time is outside the kept cuts, 2 unreadable.
Standard library only; the file is only read.
"""
import argparse, json, sys


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("state")
    ap.add_argument("out_time", type=float)
    ap.add_argument("--window", type=float, default=0.5)
    a = ap.parse_args(argv)
    try:
        st = json.load(open(a.state, encoding="utf-8"))
    except (OSError, ValueError) as e:
        print("cannot read state:", e)
        return 2
    cuts = sorted([c for c in st.get("cuts", []) if c.get("status") == "ok"], key=lambda c: c["start"])
    acc, src, cut_id, starts = 0.0, None, None, {}
    for c in cuts:
        starts[c["id"]] = acc
        if acc <= a.out_time <= acc + (c["end"] - c["start"]):
            src, cut_id = c["start"] + (a.out_time - acc), c["id"]
        acc += c["end"] - c["start"]

    def to_out(t):
        for c in cuts:
            if c["start"] - 1e-3 <= t <= c["end"] + 1e-3:
                return starts[c["id"]] + (t - c["start"])
        return None

    if src is None:
        print("output time %.2f s is outside the kept cuts (total %.2f s)" % (a.out_time, acc))
        return 1
    print("output %.2f s = source %.2f s, in cut %s" % (a.out_time, src, cut_id))
    lo, hi = a.out_time - a.window, a.out_time + a.window
    for kind, key, span in (("caption", "captions", lambda x: (x["start"], x["end"])), ("graphic", "graphics", lambda x: (x["at"], x["at"] + x["dur"])),
                            ("fx", "fx", lambda x: (x["at"], x["at"] + x["dur"]))):
        for it in st.get(key, []):
            if it.get("status") != "ok":
                continue
            s, e = span(it)
            so, eo = to_out(s), to_out(e)
            if so is None:
                continue
            eo = eo if eo is not None else so + (e - s)
            if so <= hi and eo >= lo:
                label = it.get("text") or it.get("type") or ""
                print("  %-8s %-5s '%s' output %.2f to %.2f (source %.2f to %.2f) by %s" % (kind, it["id"], label, so, eo, s, e, it.get("agent", "?")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

## 3. Templates

### brand/rules.md (start with this header, then one block per rule)

```
# Project rules (learned from the user's notes)

Read this file at the start of every edit session. A rule here beats a default in a kit skill. Strength "hard" never bends without the
user's word; "default" bends when the user asks for something else for one video. Never delete a rule: mark it superseded.

## RULE-001
Statement: <one standalone sentence with a number or a clear test>
Why: <the note, shortened, with its date>
Area: captions | graphics | cuts | sound | look | script | publish | process
Strength: hard | default
Check: <a read only command, or leave the line out when the rule is checked by eye>
Applies to: <skill names>
Added: <date>
Status: active
```

### brand/notes-log.md (append only)

```
# Notes log (append only)

## N-0001
Date: <date>
About: <file, version, and the time in the render and in the source>
Note (verbatim): "<the user's words>"
Type: T1 fact | T2 one off | T3 preference | T4 hard rule | T5 process
Fix done: <what was changed, which item ids>
Rule: <RULE-NNN, or "none, because ...">
Check: <the check added or re run, and its result>
Places updated: <files>
```

### Examples of well formed rules (invented, for the shape only; they are not defaults)

```
## RULE-101
Statement: A caption group never ends on the, a, to, and, of, your or another function word.
Why: Note of the first review round: captions ending on "the" looked unfinished.
Area: captions
Strength: hard
Check: python3 brand/tools/check_caption_groups.py project/state.json --ingest project/ingest.json
Applies to: ae-caption-style-and-grouping, ae-agent-captioner
Added: 2026-01-12
Status: active

## RULE-102
Statement: The first graphic of a short appears no earlier than 1.5 s, so the opening is the speaker alone.
Why: The user found a card at 0.4 s too busy.
Area: graphics
Strength: default
Added: 2026-01-12
Status: active

## RULE-103
Statement: Music starts only after the hook sentence ends.
Why: Note about music under the hook.
Area: sound
Strength: default
Added: 2026-01-13
Status: active
```
