---
name: ae-publish-packaging
description: Prepares everything the user needs to post a finished video by hand: title options, description, captions for Reels and TikTok, chapters from the final cut, pinned comment, thumbnail brief, hashtags, link checks, disclosures and a pre publish checklist. It never posts, schedules, uploads or messages anyone. Use when the user says "write the description", "titles for this video", "chapters", "pinned comment", "caption for Instagram", "thumbnail ideas", "is it ready to publish", or after the edit passes the QA gates.
---

# ae-publish-packaging

Read `brand/profile.md`. If it is missing or a section it needs (`## Offer and call to action`, `## Voice and tone`, `## Platforms and formats`, `## Rules`, `## Claims policy`) is empty, stop and run `ae-setup-interview` for that section (ask the user, with options), do not guess. Also read `brand/rules.md` and `brand/tokens.json` if they exist.

Hard limits of this skill: you prepare, the user publishes. You never post, schedule, upload, comment, pin, message anyone, change a link or edit an account. You never invent a number, a quote, a result or a promise the video does not deliver. Every number and name in the copy has a row in the claims ledger (`ae-claims-and-truth-ledger`). The call to action is the one in the profile and the script (`ae-call-to-action-writing`). A final video file is never copied to a delivery folder or exported without the user's explicit go (`ae-export-once-workflow`).

## When to run

After the final cut exists (chapters need final times) and, ideally, after `ae-edit-qa-gates` says READY FOR THE USER'S REVIEW. Titles and a thumbnail brief can start from the approved script earlier, but they are re checked against the final cut.

## Step 1: Questions (only what the profile does not answer)

1. Platforms to prepare copy for: YouTube long form, YouTube Shorts, Instagram Reels, TikTok, LinkedIn. Pick all that apply.
2. Title style: plain and descriptive, curiosity with a true payoff, or how to. (Never a promise the video does not keep.)
3. Link policy: one resource link in the description and pinned comment; a link in the bio instead; no links; a shortener the user already uses.
4. Hashtags: none, 3 to 5, or the platform's maximum. (YouTube shows the first three above the title and may ignore all of them when there are too many; check the current help page.)
5. Disclosures that apply: sponsorship, affiliate links, paid partnership, AI generated or synthetic media labels required by a platform, music or footage credits.
6. Scheduling: the user schedules; do you propose a slot to test? Options: no suggestion, a suggestion with the reason, a test of two slots.

Write the answers under `## Platforms and formats` and `## Rules` if they are durable.

## Step 2: Inputs and folder

Read from disk, in this turn: the approved script, the final cut transcript (`project/ingest.json` plus the accepted cuts), the claims ledger, the profile sections above, the QA report if any, and the list of resources the call to action promises. Make `publish/` in the project and fill:

| File | Content |
| --- | --- |
| `publish/PUBLISH-COPY-<platform>.txt` | Labelled sections (templates in `references/publish-tools.md`) |
| `publish/titles-worksheet.md` | Title waves, scores, top three |
| `publish/thumbnail-brief.md` | Concepts A and B and the test plan |
| `publish/checklist.md` | The pre publish checklist with what was checked |

## Step 3: Titles (25 options in waves)

1. Write the promise of the video in one true sentence from the approved script. Every title must be a different way to say that promise, never a bigger one.
2. Wave 1: ten titles from five families. Wave 2: ten more reusing the best three words. Wave 3: five plain versions. Families:

| Family | Shape | Example (placeholder: a bakery sourdough video) |
| --- | --- | --- |
| Outcome | The result the viewer wants | Keep a sourdough starter alive for years |
| Mistake | The thing that goes wrong | The feeding mistake that kills most starters |
| Contrast | Two things set side by side | One cup of flour, 48 hours, a loaf with real bubbles |
| Number | A specific number from the video | 3 signs your starter is ready to bake |
| How to | Plain instruction | How to feed a starter without a scale |
| Question | Only when specific and answered | Why does my starter smell like nail polish? |

3. Score every title 1 to 5 on: specificity, honest curiosity, clarity, audience fit (from `## Audience`), proof (every number in it has a ledger row), and fit (70 characters or less is a safe default; hard limits differ by platform). Total them; the table lives in the worksheet.
4. Rules: true to the video; no claim without a ledger row; no all capitals; no trailing punctuation unless the user's style uses it; avoid words the profile bans; do not repeat the thumbnail text; Shorts titles can be shorter and more direct.
5. Pair each of the top three with a thumbnail idea so the two say different things that belong together (the title states the promise, the thumbnail shows the proof or the feeling).
6. Give the user three titles with one reason each and your recommendation. The user picks.

## Step 4: Description (YouTube long form)

Layout, top to bottom:
1. Line 1: the one thing the viewer should do or get (the resource link, or the one sentence promise). It is the line visible before "more". Keep it under about 150 characters.
2. Two short paragraphs: what the video shows and who it is for, in the profile's voice. No new claims.
3. Chapters from the final cut (Step 7).
4. Sources as bullets with a blank line between them, each with its link, only for facts stated in the video.
5. Disclosures (sponsor, affiliate, credits).
6. Hashtags last (3 to 5 unless the user wants more).

Shorts and other short form platforms: a short caption in the same voice. Line 1 completes the video (never repeats the first spoken line word for word); the call to action appears once; a comment keyword is stated exactly as in the video; hashtags 3 to 5. If the call to action promises a message or a link after a comment, tell the user: "the automation that sends it is set up by you after posting; I do not set it up", and add that to the checklist.

LinkedIn: first two lines carry the point (they show before "see more"), short paragraphs with blank lines, one link at most in the post, the rest in a comment if the user prefers.

## Step 5: Pinned comment

One or two sentences. The same call to action and the same link as the description, no new promise, no new number. It can name the next video if the user has one. Write it in the user's voice from the profile (`ae-voice-capture`), never in marketing language.

## Step 6: Link hygiene

1. One link per resource. A second "download" link beside the first is clutter.
2. The link goes to the page the viewer should land on, not to a file that starts a download at once and not to a page that needs a login the viewer lacks.
3. The same link appears everywhere the video mentions it: spoken (if it says "link below"), description, pinned comment, caption.
4. Test every link: `curl -sIL -o /dev/null -w "%{http_code} %{url_effective}\n" "URL"` expects 200 and the right final address. Also open each in a private window, signed out, to see what a stranger sees.
5. No shorteners unless the user chose one and owns it; no tracking parameters unless the user uses analytics and asked.
6. A dead link blocks the publish package.
7. Text must contain no secrets, tokens, private emails or personal phone numbers.

## Step 7: Chapters from the final cut

Chapters are times in the output video, not the source.
1. List the chapter card times if chapter cards were used (`ae-lower-thirds-and-chapter-cards`), else the sentence boundaries where the topic changes. Convert source times with `time_map.py` or the cut mapping (`ae-owner-notes-to-rules` has the tool).
2. Rules: the first chapter at `00:00`; at least three chapters; each at least 10 s long; ascending order; labels are plain steps or questions, not conclusions ("Feeding the starter", not "The secret is flour"); formatted `MM:SS Label` or `H:MM:SS Label`, one per line.
3. Re derive the chapters after any re cut; a stale chapter list is a classic error.
4. Shorts and Reels do not use chapters.

## Step 8: Thumbnail and cover brief

1. One idea that carries the promise in two seconds; three words at most, and not a repeat of the title.
2. Subject: a real frame from the video (eyes open, sharp, clear expression, not mid blink) or a photo the user supplies. Never alter the face, never invent a face. Never generate a person unless the user asks.
3. Contrast: text and subject at least 4.5 contrast against the background (`brand/tokens.json`); one accent colour.
4. Readability: view it at about 168 pixels wide (the small suggested video size) and at phone size; if you cannot read it, the idea is too detailed.
5. Sizes (verify current rules): YouTube 1280 by 720 (16:9), small file; a Reels cover is 9:16 but the profile grid shows a centre crop, so keep the subject and text in the middle 80 percent.
6. Two concepts A and B that are clearly different; the user decides whether to test; a written swap rule and date go in the brief.
7. Assets and licences are listed; no third party logos or faces without rights.

## Step 9: Disclosures, rights, claims

1. Sponsored, affiliate or paid partnership content must be labelled as the platform requires: use the platform's own setting (the user clicks it) and a plain sentence in the description.
2. Synthetic or AI generated media: some platforms ask for a label when content looks real; check the current help page, tell the user, and let them set it.
3. Music, sound effects, fonts, footage and images: credits where the licence requires, recorded in `publish/checklist.md`.
4. Claims: run through the ledger once more on the final text. A number that changed during the edit must be changed in the copy too.
5. Privacy: no client names, customer data or private screenshots unless the user has the right and said so.

## Step 10: Lint and the checklist

```
python3 brand/tools/copy_lint.py publish/PUBLISH-COPY-youtube.txt --platform youtube_long --no-dashes --check-links
```

(Add `--no-dashes` and `--no-emoji` only when `## Rules` says so.) ERROR lines (limits, hashtags, chapters, dead links) must be fixed; WARN lines are fixed or explained. Then tick `publish/checklist.md` honestly: what was checked and how, and what could not be (no network, no phone, no private window).

File names for the finished video: a clear, versioned name such as `<Title>_<Platform>_v1.mp4`; a new version never overwrites an old one. Moving or copying the final file anywhere happens only on the user's go, with literal absolute paths.

## Step 11: Hand over and after posting

Report in under 120 words: files written, the three titles with a recommendation, any dead link or ledger gap, what you could not verify, and the one decision needed. Then wait. You do not publish.

When the user shares the posted link: open it and check the title, thumbnail, description, chapters, the pinned comment link and that the video plays; list differences from the package; do not change the live post. Suggest a review plan the user runs themselves: first hour (playback, link, comments), day one and day seven (views, average view duration, drop off points). Platform numbers differ by definition and one video proves nothing, so compare like with like and record what the data does and does not show. Turn the user's learnings into rules (`ae-owner-notes-to-rules`).

## Worked example (placeholder: a bakery, 41 s sourdough Short, plus a 9 minute explainer)

Promise (true): "Feeding a starter twice a day for 48 hours makes it ready to bake." Ledger rows: twice a day (the baker's own routine, the user's own statement), 48 hours (the baker's own timing, the user's own statement).

Shorts copy (Instagram):

```
CAPTION:
The feeding routine that gets a starter ready in 48 hours.

Comment STARTER and I will send the free feeding chart.

#sourdough #baking #breadtok
```
Lint: 0 errors; the first line is 61 characters; one call to action, same keyword as spoken at 36 s. Checklist item added: "the user sets up the automatic reply for STARTER after posting".

Long form copy (excerpt):

```
TITLE: How to keep a sourdough starter alive for years
DESCRIPTION:
The free feeding chart used in this video: https://example.com/starter-chart

CHAPTERS:
00:00 Why starters die
01:10 The feeding routine
03:45 Reading the bubbles
06:20 Baking the first loaf
```
Lint: title 52 characters; chapters ascending and over 10 s; the link answered 200 with the right final address; one link appears in the description and the same one in the pinned comment (allowed on purpose). Thumbnail concepts: A a close up of the jar with "48 hours" (the user's words in the video, a ledger row), B the baker holding a loaf with the text "ready?". The user chose A and approved the second of three titles.

## Failure modes

1. A title that promises more than the video delivers: the viewer leaves and the algorithm notices.
2. A new number in the description that is not in the ledger.
3. Stale chapters after a re cut.
4. The call to action differs between the video, caption and pinned comment.
5. A dead or login gated link.
6. A comment keyword promise with no automation behind it.
7. A thumbnail that repeats the title: wasted space.
8. Hashtag stuffing, or emoji and dashes the profile forbids.
9. Doing something outside the brief: posting, scheduling, pinning, editing the live post.
10. Copying text from another creator's description: write from the video and the profile only.

## Checklist

- [ ] Profile read; platforms, link policy, hashtags, disclosures answered.
- [ ] Final cut times used for chapters; chapters pass the rules.
- [ ] 25 title options scored; top three with reasons; the user picks.
- [ ] Description, caption and pinned comment share one call to action and one link.
- [ ] Every number and name has a ledger row; no new claims.
- [ ] Every link tested (status and private window); no shortener unless chosen.
- [ ] Thumbnail brief with two concepts, small size readability, rights listed.
- [ ] Disclosures and credits written; `copy_lint.py` has no ERROR.
- [ ] `publish/checklist.md` ticked honestly; nothing posted, scheduled or uploaded.

More: `references/publish-tools.md` (the lint tool and the file templates).

Hand off to: `ae-call-to-action-writing` (wording and mechanics of the call to action), `ae-claims-and-truth-ledger` (every claim in the copy), `ae-edit-qa-gates` (final checks), `ae-export-once-workflow` (the single export and delivery), `ae-theme-builder` (thumbnail colours), `ae-voice-capture` (the user's voice), `ae-owner-notes-to-rules` (learning after posting).
