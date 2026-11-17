# Output time helper for the reviewer (read only)

The server stores every item in source seconds. The finished video contains only the kept cuts, joined in order. To judge spacing and seams the way a viewer experiences them, convert to output time. This reads `/api/state` and changes nothing. Standard library only.

```python
import json, urllib.request

BASE = "http://127.0.0.1:8780"
state = json.load(urllib.request.urlopen(BASE + "/api/state"))
cuts = sorted((c for c in state["cuts"] if c["status"] == "ok"), key=lambda c: c["start"])

def cut_of(t):
    return next((c for c in cuts if c["start"] - 1e-3 <= t <= c["end"] + 1e-3), None)

def out_time(t):
    acc = 0.0
    for c in cuts:
        if c["start"] - 1e-3 <= t <= c["end"] + 1e-3:
            return round(acc + t - c["start"], 2)
        acc += c["end"] - c["start"]
    return None

print("finished length:", round(sum(c["end"] - c["start"] for c in cuts), 2), "s")
for kind in ("fx", "graphics"):
    for it in sorted((i for i in state[kind] if i["status"] == "ok"), key=lambda i: i["at"]):
        c = cut_of(it["at"])
        label = it.get("type") or it.get("template")
        if c is None:
            print(kind, it["id"], label, "source", it["at"], "START IN REMOVED MATERIAL")
        else:
            seam = " CROSSES SEAM" if it["at"] + it["dur"] > c["end"] + 1e-3 else ""
            print(kind, it["id"], label, "out", out_time(it["at"]), "dur", it["dur"], seam)

# join gaps: silence kept at each seam = tail of cut i + head of cut i+1 (needs ingest words)
ing = json.load(urllib.request.urlopen(BASE + "/api/ingest"))
words = ing["words"]
def inside(c):
    return [w for w in words if c["start"] <= (w["t"] + w["e"]) / 2 <= c["end"]]
for a, b in zip(cuts, cuts[1:]):
    wa, wb = inside(a), inside(b)
    if wa and wb:
        tail = a["end"] - wa[-1]["e"]
        head = wb[0]["t"] - b["start"]
        flag = "  LONG" if tail + head > 0.35 else ""
        print(f"join {a['id']} to {b['id']}: tail {tail:.2f} + head {head:.2f} = {tail + head:.2f} s{flag}")
```

Reading it:

- `START IN REMOVED MATERIAL` means the render skips the item. Reject it, or ask for it to be moved.
- `CROSSES SEAM` on a graphic means the card will sit over words from a different part of the source.
- Join lines show the silence a viewer hears at each seam. Over 0.35 s feels like a dropped beat; 0.10 to 0.20 s is the usual target for a tight edit.

If the cuts list is empty, the script prints a finished length of 0 and flags everything as removed, which is correct for an empty timeline.
