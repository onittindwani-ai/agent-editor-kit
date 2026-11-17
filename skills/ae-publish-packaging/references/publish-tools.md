# Publish packaging tools and templates

Nothing here posts, uploads or schedules anything. The user does that by hand.

## 1. copy_lint.py: check the copy file

Save to `brand/tools/copy_lint.py`.

```
python3 brand/tools/copy_lint.py publish/PUBLISH-COPY.txt --platform youtube_long --no-dashes --no-emoji
python3 brand/tools/copy_lint.py publish/PUBLISH-COPY.txt --platform instagram --no-dashes --check-links
```

Pass `--no-dashes` or `--no-emoji` only when `## Rules` in the profile says so. `--check-links` needs network access and sends a HEAD request to every link. Character limits in the script are approximate: verify on the platform's current help page.

```python
# file: copy_lint.py
#!/usr/bin/env python3
"""Lint a publish copy file: lengths, dashes, hashtags, links, chapters. It never posts or changes anything.

    python3 copy_lint.py publish/PUBLISH-COPY.txt --platform youtube_long [--no-dashes] [--no-emoji] [--allow-shorteners] [--check-links]

The file uses labelled sections, each label at the start of a line (upper case, colon): TITLE:, DESCRIPTION:, CAPTION:, CHAPTERS:,
PINNED COMMENT:, HASHTAGS:. Text under a label runs until the next label. Platforms: youtube_long, youtube_short, instagram, tiktok,
linkedin. Limits below are approximate and change: verify them on the platform's current help page before relying on a number.
Exit code: 0 no ERROR, 1 at least one ERROR, 2 unreadable file. WARN lines are advice. Standard library only.
"""
import argparse, re, sys, urllib.request

LIMITS = {  # approximate, verify
    "youtube_long": {"TITLE": 100, "DESCRIPTION": 5000, "hashtags": 15},
    "youtube_short": {"TITLE": 100, "DESCRIPTION": 5000, "hashtags": 15},
    "instagram": {"CAPTION": 2200, "hashtags": 30},
    "tiktok": {"CAPTION": 2200, "hashtags": 30},
    "linkedin": {"CAPTION": 3000, "hashtags": 5},
}
SHORTENERS = ("bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "buff.ly", "is.gd", "cutt.ly", "rebrand.ly")
LABEL = re.compile(r"^([A-Z][A-Z ]+):\s*(.*)$")
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿️]")


def sections(text):
    out, cur = {}, None
    for line in text.splitlines():
        m = LABEL.match(line)
        if m:
            cur = m.group(1).strip()
            out[cur] = [m.group(2)] if m.group(2) else []
        elif cur:
            out[cur].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}


def seconds(stamp):
    parts = [int(x) for x in stamp.split(":")]
    s = 0
    for p in parts:
        s = s * 60 + p
    return s


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--platform", required=True, choices=sorted(LIMITS))
    ap.add_argument("--no-dashes", action="store_true")
    ap.add_argument("--no-emoji", action="store_true")
    ap.add_argument("--allow-shorteners", action="store_true")
    ap.add_argument("--check-links", action="store_true", help="send a HEAD request to every link (needs network)")
    a = ap.parse_args(argv)
    try:
        text = open(a.file, encoding="utf-8").read()
    except OSError as e:
        print("cannot read file:", e)
        return 2
    sec = sections(text)
    errs, warns = [], []
    lim = LIMITS[a.platform]
    for label, mx in lim.items():
        if label in sec and len(sec[label]) > mx:
            errs.append("%s is %d characters (limit about %d)" % (label, len(sec[label]), mx))
    if a.platform.startswith("youtube"):
        if "TITLE" not in sec:
            errs.append("no TITLE section")
        elif len(sec["TITLE"]) > 70:
            warns.append("title is %d characters; long titles are often cut in lists (aim for about 60 to 70)" % len(sec["TITLE"]))
        d = sec.get("DESCRIPTION", "")
        if d and len(d.split("\n", 1)[0]) > 150:
            warns.append("the first line of the description is over 150 characters; the visible part before 'more' is short, put the key line first")
    else:
        c = sec.get("CAPTION", "")
        if not c:
            errs.append("no CAPTION section")
        elif len(c.split("\n", 1)[0]) > 125:
            warns.append("the first line of the caption is over 125 characters; only the start is visible before 'more'")
    tags = re.findall(r"(?<!\w)#\w+", text)
    if len(tags) > lim.get("hashtags", 99):
        errs.append("%d hashtags (limit about %d)" % (len(tags), lim["hashtags"]))
    if a.no_dashes and re.search("[\u2013\u2014]", text):
        for i, line in enumerate(text.splitlines(), 1):
            if re.search("[\u2013\u2014]", line):
                errs.append("line %d has an en dash or em dash" % i)
    if a.no_emoji and EMOJI.search(text):
        errs.append("emoji found (the profile says none)")
    urls = re.findall(r"https?://[^\s)>\]]+", text)
    seen = {}
    for u in urls:
        u = u.rstrip(".,;")
        seen[u] = seen.get(u, 0) + 1
        host = re.sub(r"^https?://", "", u).split("/")[0].lower()
        if u.startswith("http://"):
            warns.append("insecure link: %s" % u)
        if host in SHORTENERS and not a.allow_shorteners:
            warns.append("short link %s: use it only if the user chose a shortener" % u)
    for u, n in seen.items():
        if n > 1 and a.platform.startswith("youtube"):
            warns.append("link %s appears %d times in one file (one link per resource, unless the pinned comment repeats it on purpose)" % (u, n))
    if a.check_links:
        for u in seen:
            try:
                req = urllib.request.Request(u, method="HEAD", headers={"User-Agent": "copy-lint"})
                code = urllib.request.urlopen(req, timeout=15).getcode()
                if code >= 400:
                    errs.append("link %s answered %d" % (u, code))
            except Exception as e:
                errs.append("link %s failed: %s" % (u, e))
    if "CHAPTERS" in sec:
        ch = []
        for line in sec["CHAPTERS"].splitlines():
            m = re.match(r"^\s*((?:\d{1,2}:)?\d{1,2}:\d{2})\s+(.+)$", line)
            if m:
                ch.append((seconds(m.group(1)), m.group(2)))
            elif line.strip():
                warns.append("chapter line not recognised: '%s'" % line.strip())
        if ch:
            if ch[0][0] != 0:
                errs.append("the first chapter must start at 0:00")
            if len(ch) < 3:
                errs.append("at least 3 chapters are needed (found %d)" % len(ch))
            for (t1, _), (t2, n2) in zip(ch, ch[1:]):
                if t2 <= t1:
                    errs.append("chapter '%s' is not later than the one before" % n2)
                elif t2 - t1 < 10:
                    errs.append("chapter before '%s' is under 10 s long" % n2)
    print("checked %s for %s: %d characters, %d links, %d hashtags" % (a.file, a.platform, len(text), len(seen), len(tags)))
    for e in errs:
        print("ERROR:", e)
    for w in warns:
        print("WARN:", w)
    if not errs and not warns:
        print("OK")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
```

## 2. publish/PUBLISH-COPY.txt (labelled sections, one file per platform)

```
TITLE: <one line>
DESCRIPTION:
<line 1: the resource link or the one sentence promise>

<short paragraph 1>

<short paragraph 2>

CHAPTERS:
00:00 <label>
00:45 <label>
01:30 <label>

SOURCES:
- <source 1 with link>

- <source 2 with link>

HASHTAGS: #one #two #three

PINNED COMMENT:
<one or two sentences, the same call to action and the same link>

CAPTION:
<for Reels, TikTok, LinkedIn: first line, then the rest>
```

Use DESCRIPTION for YouTube and CAPTION for the other platforms. A blank line between list items and between paragraphs keeps copy readable when pasted.

## 3. publish/titles-worksheet.md

```
# Titles worksheet: <working title>

Promise of the video in one sentence (true, from the approved script):
Audience (from the profile):
Proof in the video (ledger rows):

## Wave 1: 10 titles, 5 families, no scoring yet
## Wave 2: 10 more, using the best 3 words from wave 1
## Wave 3: 5 plain versions (shorter, no cleverness)

## Scores (1 to 5): specificity, honest curiosity, clarity, audience fit, proof, fits in 70 characters
| # | Title | S | C | Cl | A | P | L | Total | Note |

## Top 3 with the reason, my recommendation, and the thumbnail pairing
```

## 4. publish/thumbnail-brief.md

```
# Thumbnail brief: <working title> (concepts A and B)

Platform and size: <YouTube 1280 by 720, 16:9 / Reels cover 1080 by 1920 with the centre crop in mind>
Promise it must carry in 2 seconds:
Concept A: subject, expression, background, 3 words at most (not a repeat of the title), colours from brand/tokens.json
Concept B: a clearly different idea, same checks
Source of the face image: <a frame of the video, or a photo the user supplies; never altered; never AI generated unless the user asks>
Other assets and licences:
Readable at 168 px wide? <seen, how>
Pairing with the title: <title and thumbnail say different things that relate>
A or B test plan: <the user decides; written swap rule and date>
```

## 5. publish/checklist.md

```
# Pre publish checklist (tick each, write what was checked)

- [ ] Final cut matches the approved script; chapters use final cut times
- [ ] Title, thumbnail and first frame promise the same thing
- [ ] Every number and name in the copy is in the claims ledger
- [ ] The call to action is word for word the same in the video, caption, description and pinned comment
- [ ] Every link opens (status 200 and the right page), also in a private window
- [ ] Disclosures needed by the platform and by the profile are present
- [ ] Credits and licences for music, footage, fonts and images are recorded
- [ ] copy_lint.py has no ERROR; WARN lines resolved or explained
- [ ] The file name and version are the ones the user approved
- [ ] The user has given the go; the user, not the agent, uploads
```
