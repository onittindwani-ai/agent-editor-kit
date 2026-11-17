# Spelling fixer (writes only with --apply, and only after making a backup copy)

Save as `fix_spellings.py`. It changes the spelling of words in `project/ingest.json` and the sentence text, nothing else. Times are never touched. A word list entry that spans several transcript words (for example "sour dough") merges them into one word that keeps the first start and the last end.

`fixes.json` maps the wrong spelling to the user's spelling:

```
{"sour dough": "sourdough", "levin": "Levain"}
```

Run it in this order:

```
python3 fix_spellings.py project/ingest.json fixes.json            # dry run, prints every change with its time
python3 fix_spellings.py project/ingest.json fixes.json --apply    # copies ingest.json to ingest.json.before-spelling, then writes
```

Then restart the server so it reads the new file. The timeline is kept because the server reloads `project/state.json` on start.

```python
import json, re, shutil, sys

# usage: python3 fix_spellings.py project/ingest.json fixes.json [--apply]
# fixes.json: {"sour dough": "sourdough", "levin": "Levain"}   (wrong spelling -> the user's spelling)
path, fixes_path = sys.argv[1], sys.argv[2]
apply = "--apply" in sys.argv
d = json.load(open(path))
fixes = json.load(open(fixes_path))
norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())

def case_like(src, new):
    return new if not src[:1].isupper() or new[:1].isupper() else new[:1].upper() + new[1:]

words, log = d["words"], []
i = 0
while i < len(words):
    hit = False
    for wrong, right in fixes.items():
        parts = wrong.split()
        seg = words[i:i + len(parts)]
        if len(seg) == len(parts) and [norm(w["w"]) for w in seg] == [norm(p) for p in parts]:
            if len(parts) == 1:
                tail = re.search(r"[^A-Za-z0-9]*$", seg[0]["w"]).group(0)
                new = case_like(seg[0]["w"], right) + tail
                log.append((seg[0]["t"], seg[0]["w"], new))
                seg[0]["w"] = new
            else:
                # several transcript words become one: keep the first word's start, the last word's end
                tail = re.search(r"[^A-Za-z0-9]*$", seg[-1]["w"]).group(0)
                new = case_like(seg[0]["w"], right) + tail
                log.append((seg[0]["t"], " ".join(w["w"] for w in seg), new))
                words[i:i + len(parts)] = [{"t": seg[0]["t"], "e": seg[-1]["e"], "w": new}]
            hit = True
            break
    i += 1

for s in d["sentences"]:
    for wrong, right in fixes.items():
        s["text"] = re.sub(r"\b" + re.escape(wrong) + r"\b", right, s["text"], flags=re.I)

for t, old, new in log:
    print(f"{t:7.2f}  {old!r} -> {new!r}")
print(len(log), "changes")
if apply and log:
    shutil.copyfile(path, path + ".before-spelling")        # a copy, never an overwrite of the only version
    json.dump(d, open(path, "w"))
    print("written; backup at", path + ".before-spelling", "; restart the server to load it")
elif not apply:
    print("dry run: nothing written (add --apply)")
```

Rules for using it:

1. Only spelling the user confirmed. If a name has two plausible spellings, ask, with the candidates as options.
2. Attached punctuation stays ("Levin," becomes "Levain,"). Capitalisation of the first letter follows the original word.
3. Never use it to change what was said. A wrong word (not a wrong spelling) is a transcription error: tell the user and let them decide, because the audio is the truth.
4. The sentence list is only a navigation aid; the script updates its text so the screen matches.
