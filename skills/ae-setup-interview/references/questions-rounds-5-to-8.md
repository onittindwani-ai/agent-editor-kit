# Question bank, rounds 5 to 8 (script preferences, visual theme, captions, sound)

Same method as rounds 1 to 4: at most 5 questions per message, lettered options with a one line example, free answers always welcome, record provenance. The `writes:` line names the profile key (see `ae-profile-schema`). Round 6 also fills `brand/theme.json`; use `palettes-fonts-and-contrast.md` for the concrete values.

---

## Round 5: Script preferences (writes to `## Script preferences`)

Say first: "Round 5 of 12, how your scripts should be built."

### Q5.1 Usual video length. (writes: Default length)
- A. 15 to 25 seconds. About 40 to 70 spoken words. Example: one tip.
- B. 30 to 35 seconds. About 85 to 100 words. Example: one idea with proof.
- C. 45 to 60 seconds. About 130 to 170 words. Example: three points.
- D. 60 to 90 seconds. About 170 to 250 words. Example: a short story with a lesson.
- E. Long form, 5 to 15 minutes.
Note: word counts assume about 2.8 to 3 spoken words per second; the pace question below can change it.

### Q5.2 Which hook styles feel like you? Pick up to three. (writes: Hook styles allowed)
- A. Open on the event or the result. Example: "Last week my loaf finally rose, and here is the one change."
- B. A before and after contrast. Example: "Brick on Monday, cloud by Friday."
- C. A specific question. Example: "Why does your crust go soft in an hour?"
- D. A bold true claim. Example: "You do not need a stand mixer."
- E. A personal moment. Example: "I almost quit baking in March."
Then ask which styles to avoid (writes: Hook styles avoided). Common answers: generic "Did you know" questions, fake urgency, shock for its own sake.

### Q5.3 Preferred structure. (writes: Default structure)
- A. A list of points (3 or 5). Example: "Three reasons your dough is flat."
- B. Problem, cause, fix. Example: "Dense bread, too little water, add 20 grams."
- C. Story with a lesson.
- D. Myth versus truth.
- E. Demo: show it, then explain why it works.

### Q5.4 How many points in a short video? (writes: Points per video)
- A. One. B. Two or three. C. Up to five. Rule: more points means shorter points; the kit warns when words per point drop under about 12.

### Q5.5 How deep should explanations go? (writes: Explanation depth)
- A. Explain every term the first time, in a few plain words. B. Explain only specialist terms. C. Assume knowledge.
This should match Round 2 knowledge level; if it does not, point out the mismatch and ask which wins.

### Q5.6 How do you deliver the script? (writes: Delivery method)
- A. Word for word from a teleprompter. B. Bullet outline, freestyle. C. Memorised short lines. D. Voiceover recorded later.
Say what changes: option A means the approved script is the contract and agents never reword it.

### Q5.7 Speaking pace. (writes: Pace)
- A. Slow, about 2.4 words per second. B. Normal, about 2.8. C. Fast, about 3.2. D. Not sure, measure from my footage later.

### Q5.8 Numbers in scripts. (writes: Numbers written as)
- A. Numerals always ("11", "3 steps"). B. Words under ten ("three"), numerals above. C. Whatever reads best aloud.
Also ask how to write money, percentages and dates, and whether to say years in full.

### Q5.9 Sign off and opening habits. (writes: Sign off style)
Ask for any fixed phrase at the very start or end ("Hi, I am ...", "See you in the next one"), or none. Mention that fixed intros cost the first seconds; ask whether the first sentence should be the hook instead.

---

## Round 6: Visual theme (writes to `## Visual theme` and `brand/theme.json`)

Say first: "Round 6 of 12, how your videos look. I will show colour sets with real swatches you can preview in your head, and you can give me your own colours if you already have them."

### Q6.1 Do you already have brand colours, fonts or a logo? (writes: Existing brand assets)
- A. Yes, all three. B. Colours only. C. Logo only. D. Nothing yet.
If yes, collect hex codes (6 digits after #), font names, and the logo file (PNG with transparency or SVG). Never fetch brand assets from the internet for the user. Skip Q6.2 and Q6.3 when the user supplies a full palette; still ask Q6.3.

### Q6.2 Overall look. (writes: Look name; sets palette bg, surface, ink, muted)
- A. Light and clean. Example: soft white background, dark text, one bright accent.
- B. Dark and premium. Example: near black background, light text, one glowing accent.
- C. Warm and earthy. Example: cream background, brown text, a terracotta accent.
- D. Bold and bright. Example: saturated background, black text, a hot accent.
- E. Minimal monochrome. Example: white, grey and black with a single orange mark.
Show the concrete hex sets from `palettes-fonts-and-contrast.md` for the chosen look and confirm.

### Q6.3 Accent colour family. (writes: palette accent, ok, warn)
- A. Blue. B. Green. C. Orange or amber. D. Purple. E. Red or pink. Or "my own hex".
State: one accent colour carries emphasis; ok is for good or done; warn is for caution. In one video an accent keeps one meaning.

### Q6.4 Fonts. (writes: fonts heading, body, accent)
- A. Modern sans for everything, italic serif for emphasis. Example pair: Inter plus an italic serif.
- B. Rounded friendly sans. Example: Poppins or Nunito style.
- C. Bold condensed headings with a plain body. Example: Bebas style plus Inter.
- D. Classic serif headings with a clean sans body. Example: a display serif plus Inter.
- E. Technical mono accents. Example: a mono face for labels and numbers.
Rule: at most two families visible in one frame (heading and body may share one; accent adds a second). Fonts must be licensed for video use; the user supplies or confirms an open licence font file. The kit never bundles font files.

### Q6.5 Background behind graphics. (writes: background type, path)
- A. Solid colour. B. Soft gradient between two palette colours. C. An image the user owns. D. A looping video the user owns. E. None (graphics sit on the footage).
If C or D: ask for the file, copy it into `brand/`, record the relative path. Rule: a background is for graphic scenes only, never a replacement for the speaker's own room.

### Q6.6 Corners and depth. (writes: radius, shadow)
- A. Sharp, radius 8. B. Gentle, radius 16. C. Soft, radius 28. D. Pill like, radius 44 or more.
- Shadow: soft or none.

### Q6.7 Logo use. (writes: Logo)
- A. Small logo corner mark on every graphic. B. Only on the end card. C. Never on screen. D. No logo.
If a logo is used, ask for the safe corner (avoid the zone the platform buttons cover; verify with `ae-phone-safe-zones-and-formats`).

### Q6.8 What to avoid visually. (writes: Do not use)
Prompt with examples: "no neon glow", "no cartoon icons", "no stock photos of handshakes", "no dark red". Ask also: "Is there a colour that means something negative for your audience?"

### Q6.9 Face and room. (writes: Face and room handling)
State the default: the speaker's own room and face are never recoloured, cut out or replaced unless the user asks. Ask if they want that default kept.

---

## Round 7: Captions (writes to `## Captions`)

Say first: "Round 7 of 12, captions. Most viewers watch with the sound off or low, so captions often carry the message."

### Q7.1 Caption look. (writes: Style)
- A. A rounded pill with a dark translucent fill and white text. (This is what the shipped renderer draws.)
- B. Bold plain text with a thin outline, no box.
- C. Plain text with the key word in the accent colour.
- D. Karaoke style, the current word lit up.
- E. No burned in captions (platform captions only).
Honest note for the user: the shipped renderer draws option A. Other looks need a render change through `ae-theme-builder` and `ae-caption-style-and-grouping`.

### Q7.2 Words per caption. (writes: Words per caption)
- A. 1 word at a time (punchy, many captions). B. 2 words. C. Up to 3 words (the editor's limit). The editor refuses more than 3 words or more than 22 characters.

### Q7.3 Highlighting. (writes: Highlight method)
- A. None. B. Accent colour on the key word. C. Italic accent font on the key word. D. Bold.
Note for the user: the editor's caption operation carries text only, so highlight is a render side feature.

### Q7.4 Position. (writes: Position)
- A. Lower third, about 78 percent of the height (the shipped default). B. Centre of the frame. C. Upper third. D. Follow the safe zone for the format.
Remind: it must clear the platform buttons; verify on the user's own phone.

### Q7.5 Capitalisation. (writes: Case)
- A. Sentence case. B. lowercase. C. UPPERCASE. D. As the transcript spells it.

### Q7.6 Spelling list. (writes: Custom spellings)
Ask for names, products, places and terms that must be spelled a certain way ("sourdough" not "sour dough"). Explain that these are fixed in the transcript before captioning, because the editor only accepts caption words that match the transcript.

### Q7.7 Where captions apply. (writes: On by default per platform)
Ask per platform: burned in captions on, off, or only on the 9:16 version.

---

## Round 8: Sound (writes to `## Sound`)

Say first: "Round 8 of 12, sound. I cannot hear audio, so I will measure and report numbers and you decide by ear."

### Q8.1 Music. (writes: Music policy)
- A. No music. B. A quiet bed under speech, same feel all video. C. Upbeat music, strong in the intro and outro only. D. User picks per video.

### Q8.2 Where does music come from? (writes: Music library location)
Ask for the folder of music the user owns or has licensed. The kit bundles none. If they have none: "free for commercial use sources exist, check each licence; I will not download anything without your yes." Record the licence note per track later in `ae-music-bed-and-mixing`.

### Q8.3 Music level under speech. (writes: Music level under speech)
- A. Very low, about -26 dB relative to the music file (the editor allows -30 to -14). B. Low, about -22 dB. C. Moderate, about -18 dB.
Say: starting values only, then verify by ear; the editor mixes the music, then normalises the whole mix.

### Q8.4 Sound effects. (writes: SFX policy)
- A. None. B. A few, on big moments (titles, numbers). C. One per visible action, quiet and varied. D. User picks per video.

### Q8.5 Where do effects come from? (writes: SFX source)
Ask for a folder of recorded effects the user owns or has licensed. Rule: real recorded sounds with a licence, never invented. Record the licence for every file.

### Q8.6 Sounds you dislike. (writes: Banned sounds)
Ask for any effect or sound type to never use (for example a specific whoosh). Each banned item is checked by file name and file hash before export.

### Q8.7 Loudness target. (writes: Loudness target)
- A. -16 LUFS integrated, true peak -1 dB (the editor's built in target; common for short form).
- B. -14 LUFS (some platforms normalise near this).
- C. -23 LUFS (broadcast style, rarely for social).
- D. Not sure, use the default.
Note: the shipped renderer uses one pass loudness normalisation; `ae-loudness-mastering` explains how to verify and when to do two passes.
