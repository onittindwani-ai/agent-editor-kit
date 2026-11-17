# Output time helper (read only)

The server stores every item in source seconds. The finished video contains only the kept cuts, joined end to end. Use this helper to convert a source time to the time it will have in the finished video, and to measure spacing there.

It only reads `/api/state`. It changes nothing. Run it with Python 3 (standard library only). Change the port if the conductor gave you a different one.

```python
import json, sys, urllib.request

BASE = "http://127.0.0.1:8780"

def get(path):
    with urllib.request.urlopen(BASE + path) as r:
        return json.load(r)

def kept_cuts(state):
    return sorted((c for c in state["cuts"] if c["status"] == "ok"), key=lambda c: c["start"])

def to_out(cuts, t):
    """Source seconds to output seconds, or None when t is in removed material."""
    acc = 0.0
    for c in cuts:
        if c["start"] - 1e-3 <= t <= c["end"] + 1e-3:
            return round(acc + (t - c["start"]), 3)
        acc += c["end"] - c["start"]
    return None

def containing_cut(cuts, t):
    for c in cuts:
        if c["start"] - 1e-3 <= t <= c["end"] + 1e-3:
            return c
    return None

if __name__ == "__main__":
    state = get("/api/state")
    cuts = kept_cuts(state)
    print("kept length:", round(sum(c["end"] - c["start"] for c in cuts), 2), "s in", len(cuts), "cuts")
    items = [("fx", f) for f in state["fx"] if f["status"] == "ok"] + [("graphic", g) for g in state["graphics"] if g["status"] == "ok"]
    rows = []
    for kind, it in items:
        out = to_out(cuts, it["at"])
        cut = containing_cut(cuts, it["at"])
        ends_ok = bool(cut) and it["at"] + it["dur"] <= cut["end"] + 1e-3
        rows.append((out if out is not None else -1, kind, it["id"], it.get("type") or it.get("template"), it["at"], it["dur"], ends_ok))
    for out, kind, iid, sub, at, dur, ends_ok in sorted(rows):
        note = "" if out >= 0 and ends_ok else ("  <- start is in removed material" if out < 0 else "  <- runs past the end of its cut")
        print(f"out {out:7.2f}  {kind:8} {iid:5} {sub:14} source {at:7.2f} dur {dur:4.1f}{note}")
    zooms = [r for r in sorted(rows) if r[3] == "punch_zoom" and r[0] >= 0]
    for a, b in zip(zooms, zooms[1:]):
        gap = round(b[0] - a[0], 2)
        print("zoom spacing in output:", a[2], "to", b[2], gap, "s", "(too close)" if gap < 5 else "")
```

How to read the result:

- `out` is the time in the finished video. Spacing rules for emphasis are judged on this number.
- `start is in removed material` means the render will skip that effect.
- `runs past the end of its cut` means a zoom will be shortened, and a graphic will straddle a seam (it will sit over words from a different part of the source).
- Rejected and removed items are ignored, because the helper keeps only items with status `ok`.

Test it before relying on it: with no cuts yet it prints a kept length of 0 and `start is in removed material` for everything, which is correct.
