#!/usr/bin/env python3
"""Check the Agent Editor Kit skills.

Usage: python3 scripts/check_kit.py [--min-skills 40] [--min-lines 100]

Checks every skills/<name>/SKILL.md for: front matter with a matching name and a description, enough
detail (line count), no local paths or email addresses, no em or en dashes, and that every `ae-...`
skill name mentioned inside a skill exists. Prints one line per problem and exits 1 if there is any.
"""
import argparse, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, "skills")
PATHS = re.compile(r"(/Users/|/home/[a-z]|C:\\Users|~/)")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
DASH = re.compile("[\u2013\u2014]")
NAME = re.compile(r"\bae-[a-z0-9]+(?:-[a-z0-9]+)*\b")


def read(p):
    return open(p, encoding="utf-8").read()


def front(text):
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    out = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-skills", type=int, default=40)
    ap.add_argument("--min-lines", type=int, default=100)
    a = ap.parse_args()
    problems = []
    if not os.path.isdir(SKILLS):
        sys.exit("no skills folder")
    names = sorted(d for d in os.listdir(SKILLS) if os.path.isdir(os.path.join(SKILLS, d)))
    if len(names) < a.min_skills:
        problems.append(f"only {len(names)} skills, expected at least {a.min_skills}")
    known = set(names)
    for n in names:
        p = os.path.join(SKILLS, n, "SKILL.md")
        if not os.path.exists(p):
            problems.append(f"{n}: SKILL.md missing")
            continue
        text = read(p)
        fm = front(text)
        if fm is None:
            problems.append(f"{n}: no front matter")
        else:
            if fm.get("name") != n:
                problems.append(f"{n}: front matter name is {fm.get('name')!r}")
            if len(fm.get("description", "")) < 40:
                problems.append(f"{n}: description missing or too short")
        lines = text.count("\n") + 1
        if lines < a.min_lines:
            problems.append(f"{n}: only {lines} lines (minimum {a.min_lines})")
        for pat, label in ((PATHS, "local path"), (EMAIL, "email address"), (DASH, "em or en dash")):
            for i, line in enumerate(text.splitlines(), 1):
                if pat.search(line):
                    problems.append(f"{n}/SKILL.md:{i}: {label}")
                    break
        for ref in sorted(set(NAME.findall(text)) - known):
            problems.append(f"{n}: mentions unknown skill {ref}")
    for n in names:
        rd = os.path.join(SKILLS, n, "references")
        if os.path.isdir(rd):
            for f in os.listdir(rd):
                t = read(os.path.join(rd, f)) if f.endswith(".md") else ""
                for pat, label in ((PATHS, "local path"), (EMAIL, "email address"), (DASH, "em or en dash")):
                    if pat.search(t):
                        problems.append(f"{n}/references/{f}: {label}")
    for p in problems:
        print("PROBLEM", p)
    print(f"{len(names)} skills checked, {len(problems)} problems")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
