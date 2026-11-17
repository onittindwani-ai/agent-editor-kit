# Writing the files after the interview

Exact steps for the write phase of `ae-setup-interview`. The file formats are defined in `ae-profile-schema`; read it before writing.

## 1. Draft file during the interview

After every round, append the round's answers to `brand/.interview-draft.md`:

```
## Round 4 (voice and tone), saved YYYY-MM-DD HH:MM
- Q4.1 Persona: Smart friend [user]
- Q4.2 Humour: Light and frequent, never at anyone's expense [user]
- Q4.3 Energy: Warm and even [default]
- Q4.9 Voice samples: skipped [skipped]
```

Provenance tags: `[user]` the user chose or wrote it, `[default]` the user said "you choose" and you applied the stated default, `[skipped]` the user skipped. If the session is interrupted, the draft lets you resume at the next round. The draft is not a profile and never passes the gate.

## 2. Mapping from answers to profile keys

Each question in the banks names its key on the `writes:` line. Rules for turning answers into values:
1. Write the user's words when they gave free text; write the option's label when they picked a letter, followed by the user's own example if any.
2. Use sentence fragments, not paragraphs. One fact per line.
3. Lists are written as `- item` lines under the key line.
4. A skipped question writes `NOT SET` on that key. A defaulted one writes the default and `(default, confirm later)`.
5. Never add a key the schema does not define. Never add a heading.
6. Never put a secret (password, token, private key) in the profile. If the user pastes one, stop, tell them to remove it, and do not write it.
7. Paths are relative to the project root (for example `brand/background.mp4`).

## 3. Section status values

Each section starts with a `Status:` line:
- `Status: confirmed` when every key was answered by the user or a confirmed default.
- `Status: draft` when at least one key is `NOT SET` or `(default, confirm later)`.
- `Status: NOT SET` when the whole section was skipped.

## 4. Deriving `brand/theme.json`

Take from round 6:

| Answer | Field |
| --- | --- |
| Look plus accent choice (or the user's hex codes) | `palette.bg`, `palette.surface`, `palette.ink`, `palette.muted`, `palette.accent`, `palette.ok`, `palette.warn` |
| Font option | `fonts.heading`, `fonts.body`, `fonts.accent` (family names exactly as installed or as the font file's family name) |
| Background choice | `background.type` (one of `solid`, `gradient`, `image`, `video`, `none`) and `background.path` (relative path or `null`) |
| Corners | `radius` (number) |
| Depth | `shadow` (`soft` or `none`) |

File shape, exactly:

```json
{
  "palette": {"bg": "#F4F6FA", "surface": "#FFFFFF", "ink": "#14181F", "muted": "#5B6475", "accent": "#1F6FEB", "ok": "#1E8E4E", "warn": "#C26A00"},
  "fonts": {"heading": "Inter Bold", "body": "Inter Medium", "accent": "Fraunces Italic"},
  "background": {"type": "solid", "path": null},
  "radius": 28,
  "shadow": "soft"
}
```

All hex values are `#` plus six hex digits, uppercase or lowercase. No comments in JSON. No extra keys unless `ae-theme-builder` adds them later.

## 5. Back up, then write

1. Create the folder if missing: `mkdir -p brand brand/history`.
2. If `brand/profile.md` or `brand/theme.json` already exists, copy it to `brand/history/` with a timestamp in the name before changing anything (`cp brand/profile.md brand/history/profile-YYYYMMDD-HHMM.md`). Never overwrite without a copy.
3. Write `brand/profile.md` with the Write tool in the schema's exact layout, then `brand/theme.json`.
4. Create or append `brand/profile-changes.md` with one line: date, mode (first run, section refresh), sections touched.

## 6. Validate (all must pass before you say it is written)

```
for h in "## Business" "## Audience" "## Offer and call to action" "## Voice and tone" "## Script preferences" "## Visual theme" "## Captions" "## Sound" "## Platforms and formats" "## Rules" "## Claims policy"; do grep -qxF "$h" brand/profile.md && echo "ok   $h" || echo "MISSING $h"; done
grep -c "^## " brand/profile.md          # must print 11
python3 - <<'PY'
import json, re
t = json.load(open("brand/theme.json"))
assert set(t) == {"palette", "fonts", "background", "radius", "shadow"}, "unexpected top level keys"
assert set(t["palette"]) == {"bg", "surface", "ink", "muted", "accent", "ok", "warn"}, "palette keys"
assert all(re.fullmatch(r"#[0-9A-Fa-f]{6}", v) for v in t["palette"].values()), "hex values"
assert set(t["fonts"]) == {"heading", "body", "accent"}, "font keys"
assert t["background"]["type"] in {"solid", "gradient", "image", "video", "none"}, "background type"
assert t["shadow"] in {"soft", "none"} and isinstance(t["radius"], (int, float)), "radius or shadow"
print("theme.json: valid")
PY
```

Then run the contrast check in `palettes-fonts-and-contrast.md`. If any check fails, fix the file and run again. Do not tell the user it is written until all of these print their success lines.

Also check the files for banned punctuation if the profile's house rules ask for it (for example no dashes): search the profile for the long dash characters and the spaced hyphen, and fix any hit.

## 7. After writing

Tell the user: where the files are, the one line summary of each section, which keys are `NOT SET` or default, and how to change a section later (`ae-setup-interview` in section refresh mode). Then hand off to `ae-theme-builder` (turn the theme into working tokens) and `ae-install-and-run`.
