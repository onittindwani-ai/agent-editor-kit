# Voice diff helper (standard library only)

Save as `voice_diff.py` in the project's scratch folder. It only reads the two files and prints a report. It never modifies either file.

Usage: `python3 voice_diff.py OLD.txt NEW.txt`

If a file contains a divider line of 8 or more hyphens, only the text below the divider is compared (the part above is a header that is not spoken).

```python
#!/usr/bin/env python3
"""Compare the agent's script with the user's edited script and categorise the changes."""
import difflib
import re
import sys

CONNECTORS = {"and", "so", "but", "now", "then", "plus", "because", "or"}
LEAD_INS = ["you need to", "you must", "let's say", "for example", "in simple terms",
            "here is", "here's", "to do that", "according to"]


def spoken(text):
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if re.match(r"^\s*-{8,}\s*$", line):
            lines = lines[i + 1:]
            break
    return "\n".join(lines)


def tokens(text):
    return re.findall(r"\S+", text)


def norm(tok):
    return re.sub(r"[^a-z0-9']", "", tok.lower())


def allcaps(toks):
    out = []
    for t in toks:
        letters = re.sub(r"[^A-Za-z]", "", t)
        if len(letters) >= 3 and letters.isupper():
            out.append(t.strip(".,!?:;\"'"))
    return out


def sentence_starts(text):
    parts = re.split(r"(?<=[.!?:])[\"']?\s+", text.replace("\n", " "))
    return [norm(p.split()[0]) for p in parts if p.split()]


def main(old_path, new_path):
    old = spoken(open(old_path, encoding="utf-8").read())
    new = spoken(open(new_path, encoding="utf-8").read())
    ot, nt = tokens(old), tokens(new)
    sm = difflib.SequenceMatcher(a=[norm(t) for t in ot], b=[norm(t) for t in nt], autojunk=False)
    print(f"words: {len(ot)} -> {len(nt)}   similarity: {sm.ratio():.2f}")
    print(f"lines: {len(old.splitlines())} -> {len(new.splitlines())}")
    for tag, a0, a1, b0, b1 in sm.get_opcodes():
        if tag == "equal":
            continue
        print(f"{tag:8} OLD[{' '.join(ot[a0:a1])}]  NEW[{' '.join(nt[b0:b1])}]")
    new_caps = [c for c in allcaps(nt) if c not in allcaps(ot)]
    print("new capitalised words:", new_caps)
    added_connectors = [s for s in sentence_starts(new) if s in CONNECTORS]
    old_connectors = [s for s in sentence_starts(old) if s in CONNECTORS]
    print(f"sentences starting with a connector: {len(old_connectors)} -> {len(added_connectors)}")
    low_new = new.lower()
    for phrase in LEAD_INS:
        a, b = old.lower().count(phrase), low_new.count(phrase)
        if a != b:
            print(f"lead in '{phrase}': {a} -> {b}")
    commas_o, commas_n = old.count(","), new.count(",")
    stops_o = len(re.findall(r"[.!?]", old))
    stops_n = len(re.findall(r"[.!?]", new))
    print(f"commas {commas_o} -> {commas_n}; sentence ends {stops_o} -> {stops_n}")
    print(f"estimated seconds at 2.8 words per second: {len(ot)/2.8:.0f} -> {len(nt)/2.8:.0f}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: voice_diff.py OLD NEW")
    main(sys.argv[1], sys.argv[2])
```

Read the printed spans yourself. The script finds changes; the agent decides what they mean.
