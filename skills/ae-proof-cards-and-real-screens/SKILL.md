---
name: ae-proof-cards-and-real-screens
description: Show real pages, posts, reports, documents and products on screen as proof: capture, crop, highlight the exact words, make them readable on a phone, add a source line, respect rights and label any mock up. Use when a script says "see for yourself", "here is the report", "it says right here", when the user wants a quote highlighted on a real page, a scrolling article card, a screenshot proof beat, or says "show the proof".
---

# Proof cards and real screens

Read `brand/profile.md`. If it is missing or a section it needs is empty, stop and run `ae-setup-interview` for that section (ask the user, with options), do not guess. This skill needs `## Visual theme`, `## Claims policy`, `## Rules` and `## Platforms and formats`; read `brand/theme.json` for colours and radius.

## The point of proof

Proof works because the viewer sees the real words, not a paraphrase. That only holds if the page is real, the quote is exact, the part that matters is readable on a phone and a source is visible. A fake or unreadable proof card does more harm than no card.

## Hard rules

1. **Real things only.** Capture a real page, post, report, product screen or document. Never redraw a page from memory and present it as real. If a real screen is not available, that is a blocker: ask the user to supply a screenshot, or label a mock up (rule 8).
2. **Exact wording.** The highlighted text must match the source word for word. Open the page and read it; confirm the quote is real and in context before capturing (`ae-claims-and-truth-ledger`: primary source, date checked, safe wording).
3. **Public pages only.** Never log in to capture, never include private data (names, emails, account numbers, tokens, other people's messages). If a page shows private data, crop it out or blur it, or do not use it.
4. **Rights.** A public page is evidence, not permission to republish its media. Prefer text, a short crop and a source line over copying photos or logos. For third party images, logos, charts or video, record the source and the basis for use in the ledger; if unsure, use a typeset quote or ask the user. This is not legal advice; the user decides.
5. **Source line on every card**: site or document name and the date checked, small but readable (24 px or more on a 1080 px wide canvas).
6. **Readable at phone size.** After crop and zoom, the proof text is at least 40 px high on the 1080 px canvas. Test: shrink the still to 360 px wide; if you cannot read the highlighted words, enlarge or crop tighter.
7. **Never present a headline as the publisher's endorsement** of the user's claim. The card shows what the source says, nothing more.
8. **Mock ups are labelled.** A made up interface or illustrative number carries the word "Example" at 28 px or more.
9. **Recheck on posting day.** Pages change. Add the page to the posting day recheck list in the ledger.
10. **Do not copy**: no other creator's footage, thumbnails or distinctive graphics. Real pages and the user's own screens only.

## Step 1: choose and verify the source

1. Read the script line that needs proof. Name the exact words to show (a sentence, a row, a number).
2. Open the page (a browser tool or fetch). Confirm the exact words appear. Record in the ledger: URL, title, publication date, date checked, the quote, the evidence class.
3. Decide the card type:

| Card type | When | Treatment |
|---|---|---|
| Highlighted sentence on a page | The claim rests on one sentence | Crop to the paragraph, marker over the sentence |
| Scrolling page | The sentence is far down a long page | Fast scroll then land and hold (rule below) |
| Headline card plus pull quote | A news item | Headline crop first, then the quote typeset or cropped, key words marked |
| Table row or number | A price, a score, a count | Crop the single row, enlarge, spotlight, counter if spoken (`ae-counters-and-numbers`) |
| Post or comment | A public post said something | Crop to the post text; remove avatars or names of private people |
| Product or app screen | "This is what it does" | Screen recording crop or screenshot with the relevant control spotlit |
| Typeset quote | The source is too small, busy or unclear to read | Rebuild the exact quote in the theme font with a source line (never invent words) |

## Step 2: capture

Use a headless or normal browser to capture the page at 2x device pixel ratio so text stays sharp after zoom.

- Find each phrase's rectangles in the page (one rectangle per wrapped line) rather than guessing by eye. A script can search the page text, build a DOM range around it and read the client rectangles. If the phrase is not found the text differs: fix the phrase to the real wording, never guess a rectangle.
- Pages taller than about 16,000 device pixels can glitch if captured in one shot (a sticky header repeats, content below goes wrong). Capture in clips of about 6,000 px and stitch.
- Hide cookie banners, chat widgets and sticky bars before capture when you can do so without changing the content (page styles only, never edit the text).
- Save: the stitched full image, a scaled scroll image for animation, and a JSON of the rectangles with the scale used. A reference outline is in `references/capture-outline.md`. Tool behaviour changes between versions, so test on the real page and read the result.
- For an image or PDF with no DOM, use OCR (a local OCR tool if the user has one) to get word boxes, or typeset the exact quote and underline the typeset text instead.

## Step 3: crop for the one thing that matters

1. Crop to the one row, sentence or short paragraph. Remove photos, ads and navigation. A whole busy page is never the card.
2. Enlarge until the text is at least 40 px high on the canvas. Choose the crop column so the text fills about 70 to 80 percent of the card width. For long article pages the readable column is often 600 to 700 css px wide; check the real page.
3. Dim everything outside the named part to about 70 percent and add a soft spotlight on the named part. Keep the dimming gentle: the rest of the page stays recognisable.
4. A highlight inside a crop: `((rect.x - crop.x) * scale, (rect.y - crop.y) * scale, rect.w * scale, rect.h * scale)` in image pixels.
5. Centre the target in the card. Never let a sticky header, cookie banner or junk show in the card (look at the real crop).
6. If the old page has its own annotation boxes or watermark, crop them out or typeset the quote.

## Step 4: animate it (as a pure function of time)

Follow `ae-motion-design-principles` and `ae-word-synced-graphics`.

| Move | Frames at 30 fps | Notes |
|---|---|---|
| Card entrance | 12 to 20 | ease out, enters with its content on the same frame (no empty card) |
| Fast scroll to a passage far down | 60 to 90 | ease in out; motion blur proportional to speed and capped (about 8 px); land and hold at least 30 frames before the highlight |
| Highlight marker draw | 18 to 30 | grows along the text line by line; start when the first quoted word is spoken; blend so text stays readable (multiply blend) |
| Hold after highlight | at least 36 | read time (30 frames plus 8 per extra word of the quote) |
| Source line | enters with the card or 6 frames after | stays to the end of the card |
| Exit | 4 to 10 or a hard cut | per `ae-transitions-and-blur` |

- At most **2 hand drawn marks** (a loop, an arrow, a tag) per video, drawn in 9 to 14 frames with the arrowhead last.
- A stamp, badge or verdict label should be a quiet line (a thin accent hairline, small caps label, one line of text), not a tilted rubber stamp box.
- Underlines sit on the real text: use measured rectangles, not eye placement. Look at a still at the moment each underline lands.
- Nothing sits on top of a document: no counters, labels or numbers overlapping it. A number that matters gets its own space.
- A subtle 3D tilt or bob is optional and only if the theme allows motion of that kind; keep it under 3 degrees and never while text is being read.
- Source tag, highlight and card all use theme tokens; do not hard code colours.

## Step 5: review

1. Render a still at the highlight landing frame at full resolution and one at 360 px wide.
2. Check: quote exact, highlight covers exactly the quoted words, source line present, nothing private visible, nothing clipped, contrast step against the background (`ae-theme-builder`), safe zones respected.
3. Compare the spoken line with the on screen quote. If the speaker paraphrases, the card shows the exact source and the speaker's words are not put in quotation marks.
4. Add the card to the ledger with its capture date. Add it to the posting day recheck list.

## Questions to ask the user

1. Which pages or documents may be shown? (a) only public pages, (b) public pages plus my own screens, (c) I will supply every screenshot.
2. When a source is too small to read: (a) typeset the exact quote with the source line, (b) zoom and pan the real page, (c) ask me each time.
3. Proof style: (a) calm crop with a soft highlight, (b) scrolling page then highlight, (c) real screenshot with a hand drawn circle (at most 2 per video).
4. Should the source line show the full address or only the site name? options: site name only, site name plus date checked, full address.
5. Do you want a "verified" style label? (a) none (recommended), (b) a small caps line "Source", (c) other.

Record choices in `## Visual theme` through `ae-profile-schema`.

## Worked example (synthetic)

A bakery video says: "The flour supplier's own guide says to rest the dough for at least 8 hours." Steps: open the supplier's public guide page; confirm the sentence reads "rest the dough for at least 8 hours"; record URL, date checked and the quote in the ledger. Capture at 2x; the phrase rectangles come back as two lines. Crop a 620 css px wide column around the paragraph; enlarge so the text is 44 px high on the canvas. Dim the rest to 70 percent. Spoken word "least" is at 11.40 s; the marker starts at frame 340 (11.33 s) and draws over 24 frames, hold 54 frames (30 plus 3 extra words times 8). Source line: "Supplier guide, checked 17 Nov". At 360 px wide the highlighted sentence is still readable. Recheck on posting day is added to the list.

## Failure modes

- Showing a whole page nobody can read.
- A highlight placed by eye that covers the wrong words.
- A quote that differs from the source by a word.
- Private data visible in a corner.
- A mock up shown as if real.
- A paywalled or login page captured.
- A card that appears empty for a few frames.
- Proof that contradicts the spoken claim; stop and fix the script instead.

## Checklist

- [ ] Quote verified at the source; ledger row with date
- [ ] Capture at 2x; tall pages stitched; phrase rectangles measured
- [ ] Crop to one row or sentence; text at least 40 px on canvas
- [ ] Rest dimmed to about 70 percent; spotlight on the target
- [ ] Source line present; no private data; rights basis recorded
- [ ] Highlight starts on the first quoted word; hold met
- [ ] At most 2 hand drawn marks; mock ups labelled "Example"
- [ ] Still checked at 360 px wide; posting day recheck added

## Hand off to

`ae-claims-and-truth-ledger`, `ae-word-synced-graphics`, `ae-motion-design-principles`, `ae-counters-and-numbers`, `ae-theme-builder`, `ae-phone-safe-zones-and-formats`, `ae-agent-graphics`, `ae-edit-qa-gates`.
