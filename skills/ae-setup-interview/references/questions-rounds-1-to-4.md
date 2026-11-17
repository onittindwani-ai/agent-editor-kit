# Question bank, rounds 1 to 4 (business, audience, offer and call to action, voice and tone)

How to use this file: ask one round at a time, at most 5 questions per message. For each question show the options as lettered lines with their one line example, then say "or tell me in your own words". Record the answer with its provenance tag (`user`, `default`, `skipped`). The line `writes:` names the profile key the answer goes to. Keys are defined in `ae-profile-schema`.

---

## Round 1: Business (writes to `## Business`)

Say first: "Round 1 of 12, about your business. Six quick questions."

### Q1.1 What kind of business or channel is this? (writes: Business type)
- A. Local service or shop. Example: "a neighbourhood bakery", "a plumbing company", "a yoga studio".
- B. Creator or educator. Example: "I teach guitar on video", "I explain personal finance basics".
- C. Software or app. Example: "a note taking app for students".
- D. Agency, consultancy or freelancer. Example: "I run ads for dentists", "I design brand identities".
- E. Personal brand, community or hobby. Example: "a running club", "my own journey learning to code".
Default if "you choose": the closest match to what the user already said; never pick for them if nothing was said, ask again with a shorter prompt.

### Q1.2 Say what it is in one sentence. (writes: Name, What it is)
Give a fill in template: "[Name] helps [who] to [get what] by [how]." Example: "The bakery helps neighbours learn to bake sourdough at home by sharing short lessons." Ask for the name exactly as it should be spelled and pronounced. If the user does not want the name on screen, record `Name on screen: no`.

### Q1.3 Where are you in the journey? (writes: Stage)
- A. Just starting. Example: "No audience yet, first ten videos."
- B. Small and steady. Example: "A few hundred followers, one video a week."
- C. Growing. Example: "A small team, videos support sales."
- D. Established. Example: "Known locally or in a niche, videos are routine."
Why it matters: it sets how bold claims may sound and how much proof is needed.

### Q1.4 What are the videos for? Pick the main one. (writes: Main goal of the videos)
- A. Get leads or bookings. Example: "People book a tasting class."
- B. Build trust and be remembered. Example: "Viewers feel they know me before they buy."
- C. Sell a product directly. Example: "A link to a starter kit."
- D. Grow an audience. Example: "More followers and subscribers."
- E. Teach and help, with no sale. Example: "Free lessons for the community."
Ask for a second goal if the user wants one, but record only one primary.

### Q1.5 Facts the agents may state about the business. (writes: Facts the agents may state)
Ask for 3 to 8 true, checkable facts, each with where they can be verified. Example: "Open since 2016 | the user says so", "Teaches 4 classes a week | the class schedule page". Explain: agents will use only facts in this list or the user's script. Anything else must be a labelled claim for `ae-claims-and-truth-ledger`. Accept "skip", then the agents state no facts about the business.

### Q1.6 What must never be said about the business? (writes: Things never to say)
Examples to prompt with: "no price comparisons with named competitors", "no promises about results", "do not mention the old name". Accept "nothing".

---

## Round 2: Audience (writes to `## Audience`)

Say first: "Round 2 of 12, about the people who watch."

### Q2.1 Who is the main viewer? (writes: Primary viewer)
- A. Complete beginners in the topic. Example: "someone who has never baked bread".
- B. People who tried and got stuck. Example: "their loaf is always dense".
- C. People who already do it and want to improve. Example: "home bakers who want a better crust".
- D. Buyers or decision makers. Example: "cafe owners choosing a supplier".
- E. Professionals or peers. Example: "other bakers".
Ask for one sentence describing the person in the viewer's own terms (age range and region optional).

### Q2.2 How much do they already know? (writes: Knowledge level)
- A. Nothing. Every term must be explained. Example: "Explain 'proofing' the first time."
- B. A little. Common terms are fine, specialist terms are explained.
- C. Quite a lot. Only new ideas are explained.
- D. Expert. No explanations; precision matters.

### Q2.3 What is their main problem or wish, in their words? (writes: Main problem or wish)
Ask for a sentence they might type into a search box or say to a friend. Example: "Why is my bread so heavy?" Ask for up to three.

### Q2.4 Where do they watch? (writes: Where they watch)
- A. Phone, scrolling short videos. Example: "in a queue, sound sometimes off".
- B. Phone or computer, searching for an answer. Example: "looking up a how to".
- C. Computer, sitting down to learn. Example: "a 12 minute tutorial".
- D. Mixed.
Why it matters: sound off viewing means captions carry the meaning.

### Q2.5 Language, region and spelling. (writes: Language and region)
Ask: spoken language, written spelling variant (for example US or UK), units (metric, imperial or both), currency, time zone for dates.

### Q2.6 Words your viewers use. (writes: Words they use)
Ask for 5 to 10 words or phrases real viewers use, including slang and misspellings of tool names. Example: "starter", "dough hydration". These guide plain language and caption spelling.

### Q2.7 What do they dislike or distrust? (writes: What they dislike or distrust)
- A. Hype and pressure. Example: "'You must buy this now'".
- B. Jargon.
- C. Being talked down to.
- D. Long intros.
- E. Fake looking results.
Allow several; ask for one example of something that made them leave a video.

---

## Round 3: Offer and call to action (writes to `## Offer and call to action`)

Say first: "Round 3 of 12, about what you offer and what you ask viewers to do."

### Q3.1 What do you give or sell? (writes: Offer, Offer type)
- A. A free resource. Example: "a printable starter schedule".
- B. A paid product. Example: "a recipe book".
- C. A service or a call. Example: "book a tasting class".
- D. A community or membership. Example: "a monthly baking club".
- E. Nothing to offer yet. Example: "I only want followers."
If E: skip Q3.2 to Q3.7, write `Offer type: none` and `CTA type: follow or watch next only`.

### Q3.2 What should viewers do at the end? (writes: CTA type)
- A. Comment a keyword to receive something. Example: "Comment LOAF and I will send the guide."
- B. Click the link in the bio. Example: "The link is in my profile."
- C. Click the link in the description. Example: "The recipe is linked below."
- D. Follow or subscribe, or watch the next video. Example: "Next video shows the shaping step."
- E. Reply or send a message. Example: "Send me a photo of your loaf."

### Q3.3 How does the viewer actually receive it? (writes: Fulfilment)
Ask who delivers it (the user by hand, an automation the user owns, a link in the description), how fast, and where it is stored. Rule: the CTA is only written if this can be fulfilled today. If it cannot, record `Fulfilment: NOT READY` and the CTA skill will block a CTA that promises it.

### Q3.4 If a keyword: which word? (writes: Keyword)
Offer 3 to 4 candidates from the video topic, short, one word, easy to type, not a common word that appears in normal comments. Example for a bread video: LOAF, STARTER, CRUMB. Ask the user to choose; the keyword may change per video, so record it as a default.

### Q3.5 What numbers may be spoken about the offer? (writes: Counts and numbers allowed)
Rule: only numbers that are true today and checkable ("12 recipes", "4 printable pages"). Ask the user to list them. Agents must not round up or pad.

### Q3.6 Where in the video does the CTA go? (writes: CTA placement)
- A. Once, at the very end, after the payoff. Example: last sentence.
- B. A soft mention in the middle and the ask at the end.
- C. Only in the caption or description, never spoken.
Default: A.

### Q3.7 How do you talk about price? (writes: Pricing policy)
- A. Never say a price in the video.
- B. Say the price only if free ("it is free").
- C. Say the price when it is part of the value. Example: "it is 12 dollars once".
- D. Pricing goes only in the link page.

### Q3.8 Link rules. (writes: Link rules)
Ask for the exact link to use, whether it is shown on screen, and any rule such as "link to the home page only, no tracking tails". Remind: one link per offer.

---

## Round 4: Voice and tone (writes to `## Voice and tone`)

Say first: "Round 4 of 12, how you sound. This is the round that decides whether scripts feel like you."

### Q4.1 Pick the persona closest to how you talk on camera. (writes: Persona)
- A. Smart friend. Casual, a little funny. Example: "Okay so this one surprised me."
- B. Calm teacher. Clear, steady, patient. Example: "Let us go through it one step at a time."
- C. Straight talker. Short, direct, no padding. Example: "Here is the mistake. Here is the fix."
- D. Storyteller. Scenes and moments. Example: "Last winter my starter died, and I learned why."
- E. Expert coach. Confident, precise, encouraging. Example: "Do this and your crust changes."

### Q4.2 How much humour? (writes: Humour)
- A. None, serious and useful.
- B. A dry aside now and then.
- C. Light and frequent, never at anyone's expense.
- D. Playful throughout.
Rule to state: humour never targets people, private lives or a group.

### Q4.3 Energy level. (writes: Energy)
- A. Calm and low. B. Warm and even. C. Upbeat. D. High energy.
Say what it does: energy sets sentence length and how many beats per minute.

### Q4.4 Who is speaking? (writes: Point of view)
- A. "I" (one person). B. "We" (a team or business). C. Mostly "you" (direct address). D. Mix, with "you" for advice.

### Q4.5 Vocabulary. (writes: Vocabulary level)
- A. Everyday words only (about grade 5 to 6). B. Everyday with a few trade terms explained. C. Professional.

### Q4.6 Swearing and strong language. (writes: Swearing policy)
- A. Never. B. Mild words are fine on camera but not in captions. C. Allowed when the user wrote them. Agents never add strong language on their own.

### Q4.7 Words and phrases you love and words you hate. (writes: Words to use, Words never to use)
Ask for up to 10 each. Example love: "honestly", "here is the thing". Example hate: "game changer", "unlock". Ask if there are phrases that make them cringe.

### Q4.8 Spelling and casing habits. (writes: Spelling variant, Typing habits)
Ask which spelling (US or UK), whether the user types in a personal way that must never be normalised (capital letters for emphasis, repeated letters, a certain apostrophe), and whether hand edits to scripts must be kept exactly.

### Q4.9 A sample of your real voice. (writes: Voice samples)
Ask for 150 to 300 words the user wrote or said (a caption, a message, a transcript). Say it is optional, local, and used only to match rhythm and word choice by `ae-voice-capture`. Store the file under `brand/` and record its relative path.
