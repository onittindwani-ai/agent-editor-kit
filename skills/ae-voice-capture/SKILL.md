---
name: ae-voice-capture
description: Learn how the user really speaks by diffing the script the agent wrote against the version the user edits by hand, keep a dated voice log, promote repeated patterns into voice rules, and never normalise the user's own typing. Use whenever a script is drafted or revised, whenever the user returns an edited script (pasted or as a file), and before any rewrite of text the user has touched.
---

# Voice capture: learn the user's voice from their edits

Read `brand/profile.md`. If it is missing or a section it needs is empty, stop and run `ae-setup-interview` for that section (ask the user, with options), do not guess. This skill needs `## Voice and tone`, `## Script preferences` and `## Rules`.

## Why this skill exists

A user who edits a script by hand and then reads it word for word from a teleprompter has told the agent exactly how they want to sound. Every changed comma, capital letter and joining word is evidence. This skill turns that evidence into rules so the next first draft needs fewer fixes, and it protects the user's exact words from being "cleaned up" by an agent that thinks it knows better.

Two jobs, never mixed:

1. **Process A, drafting:** write new text that already sounds like the user, using only evidenced patterns.
2. **Process B, learning:** when the user returns an edited version, diff it, log what changed, and promote patterns.

## Files this skill owns

| File | Purpose |
|---|---|
| `brand/voice-log.md` | One dated entry per batch of user edits (newest last). Never rewritten, only appended. |
| `brand/voice-rules.md` | Promoted patterns with a count of observations and one example each. |
| `brand/superseded/` | Copies of the agent's version before the user's version replaced it. |

Create the folder and files on first use. If `brand/profile.md` `## Voice and tone` is thin, a short reference to `brand/voice-rules.md` may be added there, but only with the user's yes (the profile is edited by `ae-profile-schema` rules).

## Hard rules (these never bend)

1. **The user's text is the truth.** Read the whole edited file from disk in the current turn before touching it. Never rebuild a script from memory, an earlier draft or a generator.
2. **Never normalise.** Capitalisation (an emphasis word in capitals), commas, repeated words, filler words, odd grammar, curly or straight quotes, ellipses, double spaces, lowercase sentence starts and line breaks are all the user's marks. Do not fix them, not even a clear typo, without asking once in one line.
3. **Flag, do not fix.** If something looks like a slip ("you ever wrote down what done means"), ask once: "Line 14 reads X. Intended?" and keep it as written until the user decides.
4. **Change only what was asked.** When the user names a line, change that line. Every other character stays.
5. **Save before a whole rewrite.** Copy the current file to `brand/superseded/` (name it with the date and time) before any rewrite of more than one line.
6. **Evidence threshold.** A pattern seen once is a note. Seen in 3 or more places across at least 2 different scripts, it becomes a rule. Label every inference as an inference. Never invent a preference the user did not show.
7. **Voice covers speech and layout, not facts.** Facts go through `ae-claims-and-truth-ledger`.
8. **The user's profile choices win.** If the voice log contradicts `## Voice and tone`, show both to the user and let them decide which stands.

## Process B: the user returns an edited script

1. **Read** the edited text in full. If pasted in chat, write it to a file first so the diff is repeatable.
2. **Save** the agent's last version to `brand/superseded/<script-name>-<YYYY-MM-DD-HHMM>.txt` if it is not already saved.
3. **Diff** word by word with the helper in `references/voice-diff-script.md` (a small standard library Python script). Run it as `python3 voice_diff.py OLD NEW`. It prints the counts below and changed spans. Read the output, then read the two texts side by side yourself: the tool only finds changes, it does not understand them.
4. **Classify** every change into one of these buckets (a single edit can fall in two):

| Bucket | What to look for | Example |
|---|---|---|
| Added words | New joining words, lead ins, asides | "Let's say that..." added before an example |
| Removed words | Cut setup, hedges, repeated ideas | "basically" or a whole sentence removed |
| Replaced words | Word swaps, simpler verbs, contrast words | "use" becomes "make use of", or the reverse |
| Emphasis | Words newly in capitals, italics marks, repeated words for stress | "BEFORE you start" |
| Connectors | and, so, but, because, then added or removed at line starts | "So" opens every second beat |
| Layout | Line breaks, one beat per paragraph, lists split onto lines | A numbered list turned into one step per line |
| Punctuation | Comma density, full stops versus colons, ellipses, dashes avoided | Shorter sentences joined with commas |
| Order | A beat moved earlier or later | Proof moved above the claim |
| Length | Words and estimated seconds before and after | 182 words became 223 |
| Contractions and register | "do not" versus "don't", "you need to" versus "you should" | Direct address added |

5. **Log** the batch in `brand/voice-log.md` with the template in `references/voice-log-template.md`: date, files, what was added, removed, replaced, capitalised, re laid out, and what the agent infers (marked "inference").
6. **Promote**: for each bucket, count observations across the whole log. When a pattern reaches 3 observations in 2 or more scripts, add it to `brand/voice-rules.md` with the count and one real example. If a new observation contradicts an existing rule, lower its count and note the conflict; do not delete the rule without the user's yes.
7. **Report** to the user in one or two lines what was learned ("You open most beats with So and you put emphasis words in capitals"). No lecture.
8. **Propagate**: hand the pattern to `ae-owner-notes-to-rules` so skills and checks that touch it (hooks, spoken flow, tone) are updated, not only the voice file.

## Process A: drafting a new script in the user's voice

1. Read `brand/voice-rules.md` and the last 3 entries of `brand/voice-log.md`. If both are empty, use only the `## Voice and tone` section and say so; the first draft is a baseline, not a guess at a voice.
2. Draft with the structure from `ae-script-structure` and the tone from `ae-value-first-teaching-tone`, then apply the evidenced rules (and only those). Typical evidenced rules look like:
   - direct address ("You need to...") versus neutral ("One should...");
   - a spoken lead in before a list ("And to do that, follow these steps:");
   - one beat per paragraph and one step per line;
   - one emphasis word in capitals per paragraph at most;
   - connectors at line starts (and, so, but);
   - short contrast pairs ("Use AI for the boring work but use your taste for the rest").
3. Write the capitals, commas and line breaks the user actually uses. Do not add a mark the user has never used.
4. Hand the draft over alone, per `ae-script-first-workflow`. Do not plan graphics yet.
5. After the user edits, run Process B. The loop closes: the diff shows how well the rules worked.

## Questions to ask the user (when the profile is silent)

Ask with options; the user may answer freely. Show one short example per option.

1. **How should the agent treat your edits?**
   a. Treat every edit as final, never revert (recommended)
   b. Treat edits as final, but ask when an edit changes a fact
   c. Treat edits as suggestions the agent may refine
2. **How do you read the script?**
   a. Word for word from a teleprompter (every mark matters)
   b. From notes, improvising around the beats
   c. I memorise it
3. **Emphasis style in text:**
   a. One word in CAPITALS per beat
   b. Italics marks with asterisks
   c. No emphasis marks, I add it by voice
   d. Mixed, I will mark it myself
4. **Casual features you want kept when you add them?** (fillers like "you know", trailing ellipses, lowercase starts) options: keep all, keep only the ones I typed, ask each time.
5. **Do you want pronunciation cues for hard names in brackets in the teleprompter copy only?** yes / no / only when I ask.

Record the answers under `## Voice and tone` through `ae-profile-schema`, never silently.

## Worked example (synthetic)

A user runs a local bakery channel. The agent wrote:

> Sourdough needs a long rest. Rest it overnight. The dough gets stronger.

The user returned:

> Sourdough needs a LONG rest, so rest it overnight, and the dough gets stronger by itself.

Diff output (abridged): added "so", "and", "by itself"; replaced three full stops with two commas and one full stop; capitalised "LONG"; word count 13 became 17.

Log entry (shortened): connectors added at clause joins (2), full stops replaced by commas to join sentences (3), one emphasis word in capitals (1), closing phrase added that ends on the viewer's benefit ("by itself"). Inference (label it): the user prefers one joined sentence per beat. Count after this batch: joining by comma 1 of 3, so it stays a note, not a rule.

After two more scripts show the same behaviour, `voice-rules.md` gains: "Join short sentences with commas and so/and into one spoken sentence per beat (3 observations, 2 scripts). Example: ...".

## Failure modes

- **Tidying.** Fixing "gonna" or a doubled word because it looks wrong. The user hears their own voice; do not touch it.
- **Over learning.** Promoting a rule from one script. Keep a note until the threshold is met.
- **Mirror bias.** Learning only from the user's additions and ignoring cuts. Cuts show what the user finds unnecessary.
- **Stale rules.** Rules that the latest edits no longer follow. Re check counts every 3 batches.
- **Voice over facts.** Letting a nice line survive after a fact changed. Re run `ae-claims-and-truth-ledger`.
- **Silent regeneration.** Re running a generator over a file the user edited. Always read the file first.

## Checklist

- [ ] Edited file read in full from disk this turn
- [ ] Previous version saved under `brand/superseded/`
- [ ] Diff run and read, buckets filled
- [ ] Log entry appended with inferences labelled
- [ ] Counts updated, rules promoted only at 3 observations in 2 scripts
- [ ] Slips flagged once, never fixed
- [ ] User told what was learned in one or two lines
- [ ] Pattern handed to `ae-owner-notes-to-rules`

## Hand off to

`ae-script-first-workflow` (the gated order), `ae-script-review-gate` (score the next draft), `ae-spoken-flow-and-plain-language`, `ae-value-first-teaching-tone`, `ae-hook-writing`, `ae-owner-notes-to-rules`.
