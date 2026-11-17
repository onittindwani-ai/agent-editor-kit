---
name: ae-profile-schema
description: The exact file formats of `brand/profile.md` and `brand/theme.json`, with every key, a validation checklist and a validator, plus how to read one value and how to update a single section safely. Use when the user asks "what does my profile look like", when a skill needs to know where a value lives, when the profile looks broken, or before writing or editing either file.
---

# ae-profile-schema: the profile and theme file formats

Two files describe the user to every skill: `brand/profile.md` (words) and `brand/theme.json` (look). This skill is the single reference for their shape. Other skills read the files; only `ae-setup-interview` creates them, and only through section refreshes do they change.

If you are about to read a value and the file or section is missing or empty, do not guess: stop and run `ae-setup-interview` for that section (ask the user, with options).

## 1. Principles

1. Plain Markdown the user can open and edit by hand. No front matter, no tables inside sections (lists only), so a human edit never breaks parsing.
2. **Exactly eleven second level headings**, spelled exactly, in this order. No extra `##` headings anywhere (a changelog lives in a separate file).
3. Inside a section: a `Status:` line, then `Key: value` lines or `Key:` followed by `- item` lines.
4. A value the user has not given is `NOT SET`. Never an empty value, never a guess.
5. A defaulted value ends with `(default, confirm later)`.
6. Paths are relative to the project root.
7. No secrets. No personal data beyond what the user wants on screen.
8. The user's own wording is preserved. Agents never normalise typing habits, spelling or capitalisation in the profile.

## 2. The layout

```
# Brand profile

Profile version: 1
Last updated: YYYY-MM-DD
Interview status: complete | partial (list the sections with Status: NOT SET or draft)

## Business
Status: confirmed | draft | NOT SET
Name: ...
What it is: one sentence
Business type: ...
Stage: ...
Main goal of the videos: ...
Location or market: ... (optional)
Facts the agents may state:
- fact | where it can be verified
Things never to say about the business:
- ...

## Audience
Status: ...
Primary viewer: ...
Knowledge level: ...
Main problem or wish:
- ... (up to 3, in the viewer's words)
Where they watch: ...
Language and region: spoken language | spelling variant | units | currency | time zone
Words they use:
- ...
What they dislike or distrust:
- ...
Secondary viewer: ... (optional)

## Offer and call to action
Status: ...
Offer: ...
Offer type: free resource | paid product | service call | community | none
CTA type: comment keyword | link in bio | link in description | follow or watch next | reply or message | none
CTA wording pattern: one spoken sentence the user likes
Keyword: ... (only if CTA type is comment keyword; default per video)
Fulfilment: who delivers, how fast, where it lives | NOT READY
Counts and numbers allowed:
- "12 recipes" | verified how
CTA placement: end only | soft mention and end | caption only
Pricing policy: ...
Link rules: ...

## Voice and tone
Status: ...
Persona: ...
Humour: ...
Energy: ...
Point of view: I | we | you | mix
Vocabulary level: ...
Words to use:
- ...
Words never to use:
- ...
Swearing policy: ...
Spelling variant: ...
Typing habits: ... (what must never be normalised)
Voice samples: relative path or NOT SET

## Script preferences
Status: ...
Default length: seconds range and word range
Hook styles allowed:
- ...
Hook styles avoided:
- ...
Default structure: ...
Points per video: ...
Explanation depth: ...
Delivery method: teleprompter | outline | memorised | voiceover
Pace: words per second
Numbers written as: ...
Sign off style: ...

## Visual theme
Status: ...
Look name: ...
Theme file: brand/theme.json
Existing brand assets: ...
Logo: relative path | none, plus where it may appear
Background: summary of theme.json background
Do not use:
- ...
Face and room handling: ...

## Captions
Status: ...
Style: ...
Words per caption: 1 | 2 | up to 3
Highlight method: ...
Position: ...
Case: ...
Custom spellings:
- ...
On by default per platform: ...

## Sound
Status: ...
Music policy: ...
Music library location: folder or NOT SET
Music level under speech: dB value
SFX policy: ...
SFX source: folder or NOT SET
Banned sounds:
- file or description
Loudness target: LUFS and true peak

## Platforms and formats
Status: ...
Platforms:
- ...
Formats per platform: ...
Max lengths: ... or verify at upload
Cut variants: ...
Safe zone notes: phone and apps used for verification
Cadence: ...
Posting handled by: ...

## Rules
Status: ...
House rules:
- ...
Banned words:
- ...
Identity on visuals: ...
Cut style: tight | natural | relaxed
Filler policy: ...
Third party material: ...
Motion taste: ...
Gate script approval: ...
Gate export: ...
Gate publish: the kit never publishes
Notes policy: ...
Laptop limits: threads, disk to keep free, shared machine yes or no
Working setup: folders
Cleanup policy: ...
Credits: ...

## Claims policy
Status: ...
Strictness: strict | standard | light
Evidence classes:
- ...
Results and testimonials: ...
Regulated topics: ... plus disclaimer wording
Date handling: ...
Third party mentions: ...
Never claim:
- ...
```

Keys may be added by a section refresh only if this skill's list is updated first, so every skill still finds what it expects. If a user wants a custom note, write it under the key `Notes:` in the relevant section.

## 3. `brand/theme.json`

Exactly this shape (see `ae-setup-interview/references/palettes-fonts-and-contrast.md` for the values):

```json
{
  "palette": {"bg": "#F4F6FA", "surface": "#FFFFFF", "ink": "#14181F", "muted": "#5B6475", "accent": "#1F6FEB", "ok": "#1E8E4E", "warn": "#C26A00"},
  "fonts": {"heading": "Inter Bold", "body": "Inter Medium", "accent": "Fraunces Italic"},
  "background": {"type": "solid", "path": null},
  "radius": 28,
  "shadow": "soft"
}
```

| Field | Type | Allowed values and notes |
| --- | --- | --- |
| `palette.*` | string | seven keys exactly: `bg`, `surface`, `ink`, `muted`, `accent`, `ok`, `warn`; each `#RRGGBB` |
| `fonts.heading`, `fonts.body`, `fonts.accent` | string | family and weight names as the font file reports them; at most two distinct families overall |
| `background.type` | string | `solid`, `gradient`, `image`, `video`, `none` |
| `background.path` | string or null | relative path for `image` and `video`, otherwise `null` |
| `radius` | number | pixels at 1080 wide, typical 8, 16, 28, 44 |
| `shadow` | string | `soft` or `none` |

No other top level keys. A skill that needs derived tokens (spacing, type sizes, caption sizes) computes them in its own working files or in `ae-theme-builder` output, never inside `theme.json`.

## 4. Reading one value (how skills should do it)

1. Open `brand/profile.md` and find the heading with an exact line match.
2. Read until the next line that starts with `## `.
3. Find the key line that begins with `Key:`; a list value is the `- ` lines that follow.
4. If the value is `NOT SET` or the key is absent, stop and run `ae-setup-interview` for that section.
5. If `Status:` is `draft`, you may use confirmed keys but tell the user which unconfirmed values you relied on.

Quick shell reader for one section (prints the body):

```
awk -v h="## Voice and tone" '$0==h{p=1;next} /^## /{p=0} p' brand/profile.md
```

## 5. Validation checklist (run after any change)

- [ ] File starts with `# Brand profile` and has `Profile version`, `Last updated`, `Interview status`.
- [ ] Exactly 11 lines start with `## ` and they match the 11 headings, in order.
- [ ] Every section has a `Status:` line with a valid value.
- [ ] No key has an empty value (use `NOT SET`).
- [ ] No defaulted value lacks the `(default, confirm later)` marker unless the user confirmed it.
- [ ] `Words per caption` is not above 3; the caption character limit of 22 is respected in examples.
- [ ] Every relative path in the file exists on disk (`Voice samples`, `Logo`, the theme background path, music and sound folders).
- [ ] `brand/theme.json` parses, has exactly the five top level keys, seven palette keys with `#RRGGBB`, three font keys, valid background type and shadow.
- [ ] Contrast pairs pass (ink and muted at least 4.5 on bg and surface, accent at least 3).
- [ ] No secrets or tokens. No banned punctuation if the house rules ban it.

Validator (Python 3, standard library only):

```python
import json, os, re, sys
H = ["Business", "Audience", "Offer and call to action", "Voice and tone", "Script preferences", "Visual theme",
     "Captions", "Sound", "Platforms and formats", "Rules", "Claims policy"]
p = open("brand/profile.md", encoding="utf-8").read().splitlines()
heads = [l[3:] for l in p if l.startswith("## ")]
errs = []
if heads != H: errs.append(f"headings differ: found {heads}")
body, cur = {}, None
for l in p:
    if l.startswith("## "): cur = l[3:]; body[cur] = []
    elif cur: body[cur].append(l)
for h in H:
    s = [x for x in body.get(h, []) if x.startswith("Status:")]
    if not s or s[0].split(":", 1)[1].strip() not in ("confirmed", "draft", "NOT SET"):
        errs.append(f"{h}: missing or invalid Status line")
for i, l in enumerate(p):
    if re.match(r"^[A-Za-z][A-Za-z ]+:\s*$", l) and not (i + 1 < len(p) and p[i + 1].startswith("- ")):
        errs.append(f"line {i+1}: key with no value and no list: {l}")
t = json.load(open("brand/theme.json"))
if set(t) != {"palette", "fonts", "background", "radius", "shadow"}: errs.append("theme top level keys")
if set(t.get("palette", {})) != {"bg", "surface", "ink", "muted", "accent", "ok", "warn"}: errs.append("palette keys")
if not all(re.fullmatch(r"#[0-9A-Fa-f]{6}", v) for v in t.get("palette", {}).values()): errs.append("palette hex")
bg = t.get("background", {})
if bg.get("type") not in ("solid", "gradient", "image", "video", "none"): errs.append("background type")
if bg.get("type") in ("image", "video") and not (bg.get("path") and os.path.isfile(bg["path"])): errs.append("background path missing")
print("OK" if not errs else "\n".join(errs)); sys.exit(1 if errs else 0)
```

## 6. Updating one section safely

1. Copy the current file to `brand/history/profile-YYYYMMDD-HHMM.md` (same for theme).
2. Read the current section body in full and show it to the user.
3. Run `ae-setup-interview` in section refresh mode for the matching round, with the current values as "current".
4. Replace only the lines between that section's heading and the next heading. Leave every other byte untouched.
5. Set `Last updated` to today. Recompute `Interview status`.
6. Append `YYYY-MM-DD | section refresh | <section names> | <one line reason>` to `brand/profile-changes.md`.
7. Re run the validation checklist. If the change affects theme values, update `brand/theme.json` in the same pass.
8. List which skills care about the change (see the table).

| Section changed | Skills affected |
| --- | --- |
| Voice and tone, Script preferences | `ae-hook-writing`, `ae-script-structure`, `ae-spoken-flow-and-plain-language`, `ae-value-first-teaching-tone`, `ae-voice-capture`, `ae-script-review-gate` |
| Offer and call to action | `ae-call-to-action-writing`, `ae-publish-packaging` |
| Claims policy | `ae-claims-and-truth-ledger`, `ae-script-review-gate`, `ae-edit-qa-gates` |
| Visual theme | `ae-theme-builder`, `ae-lower-thirds-and-chapter-cards`, `ae-word-synced-graphics`, `ae-proof-cards-and-real-screens` |
| Captions | `ae-caption-style-and-grouping`, `ae-agent-captioner` |
| Sound | `ae-sound-effects-placement`, `ae-music-bed-and-mixing`, `ae-loudness-mastering` |
| Platforms and formats | `ae-phone-safe-zones-and-formats`, `ae-export-once-workflow`, `ae-publish-packaging` |
| Rules | every skill; the gates and cut style change run behaviour |

## 7. Worked example (placeholder content)

A baker's `## Captions` section:

```
## Captions
Status: confirmed
Style: rounded pill, dark translucent fill, white text
Words per caption: up to 3
Highlight method: none (render side feature not enabled)
Position: lower third, about 78 percent of the height
Case: sentence case
Custom spellings:
- sourdough
- proofing
On by default per platform: all vertical versions on, landscape version off
```

A skill that needs the caption position reads `Position`, a skill that needs the spelling list reads `Custom spellings`. If the user later says "make captions one word at a time", the section refresh changes only `Words per caption`, backs up the file first, and lists `ae-caption-style-and-grouping` and `ae-agent-captioner` as affected.

## 8. Failure modes

| Failure | Prevention |
| --- | --- |
| Extra `##` headings (for example a changelog) | Keep the changelog in `brand/profile-changes.md`. |
| A skill writes a key the schema does not list | Add the key here first, or use `Notes:`. |
| `NOT SET` treated as a value | Always stop and ask. |
| Paths left absolute to a machine that changes | Use relative paths from the project root. |
| Theme edited by hand into invalid JSON | Re run the validator before any render. |
| Agents normalising the user's typing habits | Read `Typing habits` before editing user text. |

Hand off to: `ae-setup-interview` (to fill or change anything), `ae-theme-builder` (to turn the theme into working tokens), `ae-start-here` (gate and menu), `ae-edit-qa-gates` (profile check inside the delivery gate table).
