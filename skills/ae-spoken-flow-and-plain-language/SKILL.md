---
name: ae-spoken-flow-and-plain-language
description: Writes scripts for the ear: joined sentences with connectors, every technical term explained in plain words, grade level targets, teleprompter format and a read aloud pass. Use when the user says "make it flow", "it sounds choppy", "it sounds like an article", "simplify the words", "explain it for beginners", or after any draft before it goes to approval.
---

# Spoken flow and plain language

Read `brand/profile.md`. If it is missing or a section this skill needs (`## Audience`, `## Voice and tone`, `## Script preferences`) is empty, stop and run `ae-setup-interview` for that section (ask the user, with options), do not guess.

## Why scripts fail when spoken

Text is read at the reader's speed and can be reread. Speech goes by once. A script that looks fine on the page fails aloud in four common ways: it is choppy (a string of short full stop lines), it is dense (long sentences that need rereading), it uses words the viewer must stop and decode, or it asks the viewer to remember a term for several lines before explaining it. The user usually reads from a teleprompter word for word, so a stumble in the script becomes a stumble on camera.

## Rule 1: Beats are joined sentences, not strings of fragments

Each beat is one or two flowing spoken sentences of about 15 to 30 words, joined with connectors. Strings of 3 to 5 word sentences ending in full stops read as slogans and sound choppy.

| Job | Connectors |
| --- | --- |
| Cause | because, since, which is why |
| Result | so, so that, which means, and that is why |
| Contrast | but, though, even though, still |
| Addition | and, and also, plus |
| Sequence | first, then, after that, and once that is done |
| Example | like, for example, say you |
| Condition | if, when, as long as, unless |

Exception: one short causal contrast pair is a deliberate beat ("The key was public. That was normal.") when the second line explains the first. Use at most one per script, and the contrast must be real.

Before (choppy, 24 words in 6 sentences): "Dough needs rest. Yeast makes gas. Gas lifts bread. A short rest fails. The loaf is dense. Give it time."
After (flowing, 33 words in 2 sentences): "Dough needs time to rest because the yeast makes gas while it sits, and that gas is what lifts the bread, so if you cut the rest short you end up with a dense loaf."

## Rule 2: Every beat leads into the next

The end of a line must make the viewer want the start of the next. After "here is the catch", say what the catch means for the viewer before moving on. After an example, say plainly what the thing did with it. If a line could be moved to any other place in the script, it is not connected: add the reason it belongs here, or cut it.

## Rule 3: Explain every technical word the first time, in 3 or 4 plain words, right after it

Pattern: term, then a short definition, then one line of what it does in everyday terms.
"Underproofing, which just means the dough did not rest long enough, so there is not enough gas in it to lift the loaf."
- Define at first use, not later. Never leave a term unexplained for more than one line.
- Keep the correct term; do not replace "model" with "helper". The definition does the lifting.
- If the audience always knows a term (check `## Audience`), do not define it; it sounds condescending.
- A hard to say name gets a pronunciation hint in brackets in the teleprompter file only, for example "Muir (pronounced MEER)". The hint is not spoken, not captioned and not counted as words.

## Rule 4: Grade level and word choice

- Target about grade 5 to 7 vocabulary for a general audience (everyday words a friend outside the field knows). Ask the audience question in the interview: (a) complete beginners, (b) some experience, (c) professionals, (d) mixed. Adjust: professionals get shorter definitions, beginners get an example for every term.
- Prefer short common words: use, not utilise; show, not demonstrate; start, not commence; about, not approximately.
- Average sentence about 12 to 17 words. A sentence over 25 words must be a single clear chain (cause then result), never a list of ideas. The hook may run to 20 words when the payoff lands in the first 9.
- One idea per sentence, one thought per breath: read it aloud; if you need to inhale in the middle, split or add a comma at the natural pause.
- Contractions for a conversational voice ("it's", "you'll"), unless the profile says formal.
- Numbers: write them as numerals ("11", "2,400", "3 steps"), because the user reads faster and the captions match. In the teleprompter file, spell out a number the user said they trip over.
- Avoid: stacked prepositions, nested clauses, passive voice that hides who did it, abbreviations (spell out the first use), parentheses, semicolons, slashes ("and/or"), and homophone traps ("to/too", "read/red" when ambiguous).
- No dashes in prose written for the user's public text if the profile forbids them; use commas, periods, colons or a new sentence.

## Rule 5: Make it personal and concrete

Put the viewer in the sentence ("you", "your"). Use a concrete noun where a vague one sits ("a 50 pound flour bag", not "inventory"). Use a short real example where an abstraction sits. Do not use invented prevalence ("everyone", "most people", "90 percent") without a source. Examples marked as examples must say so.

## Rule 6: Read it aloud (the pass that catches everything)

Do this on every draft before showing it. You cannot hear, so simulate: read each line at the pace the user speaks and mark trouble.

| Check | Fail sign | Fix |
| --- | --- | --- |
| Breath | More than about 20 words without a natural pause | Split with a connector or add a comma |
| Tongue | Repeated sibilants or hard clusters ("the sixth sick sheikh") | Reword |
| Echo | The same word 3 times in a line | Vary or remove |
| Missing word | "click one" with no object | Add the noun |
| Decode | A word the viewer must pause to decode | Replace or define |
| Rhythm | Five lines of the same length | Vary: one long, one short |
| Ear trap | A homophone or number that reads two ways | Rephrase |
| Fragment | A noun phrase standing alone after a clause | Join it to the clause with "where" or "which" |

Also read the first and the last lines slowly: the hook and the action carry the most risk.

## Rule 7: Teleprompter format

The saved spoken file is spoken words only:
- One beat per paragraph, blank line between paragraphs.
- No labels, no stage directions, no timing marks, no on screen text, no source notes.
- Pronunciation hints in brackets, short.
- Emphasis: at most one word in capitals per beat, only if the user wants it; keep the user's own marks if they add any.
- For platforms with different endings (for example one that has no direct messages), put a clearly separated final section, headed with a single heading line that the user chose.
- Keep two copies in step: a labelled copy for review in chat, and the clean spoken copy for the prompter.
- Never reformat the user's edited prompter file.

## Rule 8: Humour and friend tone live in the voice, not the facts

If the profile voice includes light humour, put it in the reaction and commentary, never in the numbers, instructions or names. Do not target a private person. See `ae-value-first-teaching-tone`.

## A rewrite procedure (use on any draft)

1. Split the draft into lines. Number them.
2. Label every sentence's length in words; flag every sentence under 5 or over 25 words (except designed beats).
3. Join runs of three or more short sentences with connectors, and say which connector you used and why.
4. Find every technical term and note where it is first explained. Move the definition to the first use.
5. Replace each abstract word with a concrete one.
6. Read aloud pass (Rule 6) line by line.
7. Compare before and after word counts. If the rewrite is longer, say so and say whether the runtime is still inside the budget (`ae-script-structure`).
8. Show the user a table: old line, new line, reason. The user decides.

## Worked example (placeholder)

Draft, as an article:
"Hydration percentage is the ratio of water to flour by weight. A higher ratio produces an open crumb but increases handling difficulty. Beginners should start lower."

Rewrite for the ear:
"Hydration is just how much water you add compared to the flour, so a wetter dough gives you bigger holes in the bread, but it also gets stickier and harder to handle. If you are new to this, start with less water, and add a little more each time you bake."

Changes: defined the term in plain words at first use ("how much water compared to the flour"); replaced "ratio by weight", "open crumb" and "handling difficulty" with plain pictures (holes, sticky); joined three short sentences with "so" and "but"; added a second person "you"; added a concrete next step. Word count 31 to 63, because the explanation is the value; if the budget is tight, cut "and add a little more each time you bake".

Another pair, for a product line:
Before: "The tool has a function. It scales recipes. It supports metric units. It is free."
After: "If you want to double a recipe without doing the math, there is a free tool where you type in the amounts, and it scales every ingredient for you, in cups or in grams."
(This also follows value, then name, then ease; see `ae-value-first-teaching-tone`.)

## Failure modes

| Failure | Fix |
| --- | --- |
| Article voice (nominalisations: "the utilisation of") | Turn nouns back into verbs ("use") |
| Define the term three lines late | Move the definition to first use |
| Jargon stack in the hook | One term at most, only if the audience always knows it |
| Every line the same length | Vary rhythm |
| Over explaining for experts | Check the audience; trim definitions |
| Humour in the facts | Move it to the reaction |
| Rewriting the user's edited words | Suggest, never overwrite (`ae-script-first-workflow`) |

## Checklist

- [ ] Beats are one or two joined sentences, 15 to 30 words.
- [ ] Every technical term defined at first use in 3 to 4 plain words.
- [ ] Average sentence 12 to 17 words; none over 25 unless a clear chain.
- [ ] No choppy runs of fragments; at most one designed contrast pair.
- [ ] Numerals for numbers; no invented prevalence.
- [ ] Read aloud pass done with the table above.
- [ ] Clean teleprompter file: spoken words only; pronunciation hints in brackets.
- [ ] Before and after table shown; runtime recomputed.

## Hand off to

`ae-value-first-teaching-tone`, `ae-script-structure`, `ae-hook-writing`, `ae-claims-and-truth-ledger`, `ae-script-review-gate`, `ae-voice-capture`, then `ae-script-first-workflow` for approval. For delivery rhythm after approval see `ae-pacing-and-rhythm`.

See `references/connector-and-rewrite-bank.md` for more before and after pairs and a plain word swap list.
