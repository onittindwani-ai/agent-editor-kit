---
name: ae-setup-interview
description: The long onboarding interview that creates `brand/profile.md` and `brand/theme.json`. Use when the user says "set up", "start", "onboard me", "my brand", "change my colours", "update my profile", or when any skill finds the profile missing or a section empty. It asks about business, audience, offer and call to action, voice, script style, visual theme, captions, sound, platforms, rules and claims in 12 rounds with 3 to 5 options and an example for each, confirms everything, then writes the files.
---

# ae-setup-interview: the onboarding interview

This skill is the only way `brand/profile.md` and `brand/theme.json` get created. Every other skill in the kit reads them and refuses to guess. Take this seriously: a careful interview here saves dozens of corrections later. A rushed or invented profile poisons everything downstream.

This skill creates the profile, so it does not start with "read the profile". It starts by checking whether one exists (section 2).

## 1. Ground rules for asking

1. **Rounds, not a wall.** 12 rounds, one at a time. At most 5 questions per message. Tell the user the round number ("Round 4 of 12") and what it is about.
2. **Options with examples.** Every question that has a fixed set of answers shows 3 to 5 lettered options, each with a one line example, exactly as written in the question banks. Always add "or tell me in your own words".
3. **Free answers win.** If the user answers outside the options, use their words. Do not force a letter.
4. **Shortcuts the user may use:** `skip` (leave this key NOT SET), `you choose` (apply the stated default and mark it as a default), `back` (re ask the previous question), `stop` (save the draft and pause).
5. **Never invent.** If the user does not know, record `NOT SET`. Never fill a key with a plausible guess. Never copy answers from an example, another project or an earlier user.
6. **Facts need the user.** Names, numbers, results, prices, links and claims come only from the user. If a user answer contains a claim that sounds like a measured result, record it only with its source (see round 11) or label it `founder context, unverified`.
7. **Neutral tone.** Do not lead ("most people choose A"). You may recommend a default in one short sentence, labelled as a recommendation.
8. **One language.** Ask in the language the user writes in; keep key names and option letters as they are in the files.
9. **Respect time.** At the start say the estimate (about 40 minutes for the full interview of about 90 questions, about 8 minutes for the quick start) and let the user choose between them. Offer the quick start again if the user hesitates later.
10. **No secrets.** If the user pastes a password, token or private key, do not store it. Say so and continue.
11. **Never fetch brand assets from the internet for the user.** Ask for the files or the hex codes.
12. **Confirm before writing.** Nothing is written to `brand/profile.md` until the user confirms the summary (section 7).

## 2. Preflight (do this before round 1)

1. Check what exists: `ls brand 2>/dev/null`, `test -f brand/profile.md`, `test -f brand/theme.json`, `test -f brand/.interview-draft.md`.
2. Pick the mode:

| Situation | Mode |
| --- | --- |
| No profile, no draft | **First run**: all 12 rounds |
| A draft exists | **Resume**: show what the draft holds, ask whether to continue at the next round or start over (starting over moves the draft to `brand/history/` first) |
| A profile exists and the user wants a change | **Section refresh**: ask only the rounds for the named sections (section 9) |
| The user only wants colours, fonts, background | **Theme mode**: rounds 6 and 7 only, then write `brand/theme.json` and the two sections |

3. Ask whether the user has existing brand material (a style guide, a website, old captions, a bio). If yes, ask them to paste or point to files, and use them only to suggest pre filled answers in the options ("your bio says 'friendly teacher', is that round 4 option B?"). The user still confirms each answer.
4. Explain in 4 lines: what the profile is, that nothing public happens, that answers can be changed later, and the shortcuts.
5. `mkdir -p brand brand/history` (never overwrite existing files).

## 3. The round map

| Round | Topic | Questions | Writes to | Question bank |
| --- | --- | --- | --- | --- |
| 1 | Business | Q1.1 to Q1.6 | `## Business` | `references/questions-rounds-1-to-4.md` |
| 2 | Audience | Q2.1 to Q2.7 | `## Audience` | same |
| 3 | Offer and call to action | Q3.1 to Q3.8 | `## Offer and call to action` | same |
| 4 | Voice and tone | Q4.1 to Q4.9 | `## Voice and tone` | same |
| 5 | Script preferences | Q5.1 to Q5.9 | `## Script preferences` | `references/questions-rounds-5-to-8.md` |
| 6 | Visual theme | Q6.1 to Q6.9 | `## Visual theme`, `brand/theme.json` | same, plus `references/palettes-fonts-and-contrast.md` |
| 7 | Captions | Q7.1 to Q7.7 | `## Captions` | same |
| 8 | Sound | Q8.1 to Q8.7 | `## Sound` | same |
| 9 | Platforms and formats | Q9.1 to Q9.7 | `## Platforms and formats` | `references/questions-rounds-9-to-12.md` |
| 10 | House rules | Q10.1 to Q10.7 | `## Rules` | same |
| 11 | Claims policy | Q11.1 to Q11.7 | `## Claims policy` | same |
| 12 | Delivery gates and working setup | Q12.1 to Q12.8 | `## Rules` | same |

Before each round, open the matching bank and ask the questions exactly with their options and examples. Do not paraphrase the options away; the examples are what make a choice easy.

## 4. Quick start mode (offered at the start, and again if the user hesitates)

Ask a reduced set, mark everything else `NOT SET`, and tell the user which skills will ask later:
- Round 1: Q1.1, Q1.2, Q1.4.
- Round 2: Q2.1, Q2.2.
- Round 3: Q3.1, Q3.2.
- Round 4: Q4.1, Q4.2.
- Round 5: Q5.1, Q5.2.
- Round 6: Q6.2, Q6.3, Q6.4 (theme.json needs at least these).
- Round 7: Q7.1, Q7.2.
- Round 9: Q9.1, Q9.2.
- Round 12: Q12.1, Q12.2.
Rounds 8, 10 and 11 apply their documented defaults, marked `(default, confirm later)`. The result is Status: draft sections. Tell the user the profile can be deepened any time with a section refresh.

## 5. Running a round (the loop)

For each round:
1. Say: "Round N of 12: <topic>. <number> questions."
2. Ask the questions of the round, up to 5 per message, each with options and examples. If a round has more than 5, ask the first 5, wait, ask the rest.
3. Read the answers. For each, record the key, the value and a provenance tag in `brand/.interview-draft.md` (format in `references/writing-the-files.md`).
4. Run the follow up checks in section 6 for that round. Ask a clarifying question only when an answer is ambiguous or contradicts an earlier one.
5. Echo a one line summary of the round: "Got it: smart friend voice, light humour, warm energy, I as the speaker." Invite corrections, then move on.
6. After every 4 rounds, offer a pause ("saved; want to continue?").

### Branching rules

- Round 3 Q3.1 answer E (nothing to offer): skip Q3.2 to Q3.8 and write `Offer type: none`.
- Q3.2 not "comment a keyword": skip Q3.4 (keyword).
- Q3.3 reveals the offer cannot be delivered today: record `Fulfilment: NOT READY` and warn that call to action writing will block a CTA that promises it.
- Q7.1 E (no burned in captions): skip Q7.2 to Q7.5 and Q7.7, write `Style: none`.
- Q8.1 A (no music) and Q8.4 A (no effects): skip Q8.2, Q8.3 and Q8.5.
- Q9.2 includes only landscape: tell the user safe zone numbers in `ae-phone-safe-zones-and-formats` will be marked not applicable.
- Q6.1 gives a full palette: skip Q6.2 and Q6.3, but still run the contrast check.
- Q12.1 C (the user supplies a final script): tell the user hooks and structure advice stays optional.

## 6. Cross checks (catch contradictions)

Run these after the relevant rounds. When one triggers, say what clashes and ask which answer wins; record the winner.

| Clash | What to say |
| --- | --- |
| Persona "calm teacher" with humour "playful throughout" | "Those pull in different directions. Which should lead?" |
| Knowledge level "complete beginner" with explanation depth "assume knowledge" | "Beginners will not follow unexplained terms. Which one wins?" |
| Length 15 to 25 s with 5 points | "That is about 4 seconds per point, too tight. Fewer points or longer video?" |
| Captions 1 word at a time with a pace of fast speech | "Single word captions at that pace flash very quickly. Use 2 words?" |
| Strictness "light" with regulated topics | "Health, money and law need sourced claims. Recommend standard or strict." |
| Cut style "tight" with persona "storyteller" or energy "calm and low" | "Tight cuts remove the pauses that make this voice work. Natural instead?" |
| CTA "comment a keyword" with Fulfilment NOT READY | "A keyword promise needs delivery. Set up the delivery first or choose another ask." |
| Dark background with dark ink | Fails the contrast check; show the ratio and suggest the nearest passing value. |
| Identity on visuals "none" with logo "corner mark" | "A logo is identity. Keep the logo or remove it?" |
| Round 12 export gate B (draft renders) with a light laptop | "Draft renders cost time and disk on a light laptop. Stills only?" |

## 7. The confirm step (never skip it)

1. Build a summary table with one row per section: section name, the 3 to 6 most important values, and the count of `NOT SET` and default values.
2. Show the theme as a swatch table: role, hex, contrast ratio line where it matters.
3. Ask: "Anything wrong or missing? Name a section or a question to change. Say 'confirm' when it is right."
4. For each change, re ask only that question, update the draft, show the changed row again.
5. Accept only an explicit confirmation ("confirm", "yes, write it", "looks right"). A silence or a vague "ok" about one section is not confirmation of the whole.
6. If the user confirms with unresolved defaults, list them and say they are marked `(default, confirm later)`.

## 8. Writing the files

Follow `references/writing-the-files.md` exactly:
1. Back up any existing profile or theme into `brand/history/`.
2. Write `brand/profile.md` in the layout from `ae-profile-schema` with the 11 headings, each with a `Status:` line.
3. Write `brand/theme.json` with the exact shape.
4. Run the heading check, the theme validation, and the contrast check. All must pass.
5. Append to `brand/profile-changes.md`. Move `brand/.interview-draft.md` to `brand/history/` (do not delete; if the user wants it removed, delete only with the literal absolute path).
6. Report: file locations, per section status, unresolved defaults, next steps.

If the contrast check fails, do not write a failing theme silently. Show the failing pair, offer two nearby fixes, and re run.

## 9. Section refresh mode

1. Ask which sections change ("business", "voice", "colours", "all captions"). Map them with the round map above.
2. Read the existing section from `brand/profile.md` and show it to the user first.
3. Ask only that round's questions, with the old value shown as "current" next to the options.
4. Confirm only the changed section (section 7, scoped).
5. Back up the profile, replace only that section's body (keep the other ten sections byte for byte), update `Last updated`, append to `brand/profile-changes.md`.
6. If the Visual theme section changed, update `brand/theme.json` and hand off to `ae-theme-builder`.
7. Tell the user which skills are affected (for example, a changed claims policy affects `ae-claims-and-truth-ledger` and `ae-script-review-gate`).

## 10. When another skill sends you here

Another skill found a missing section or key. Do not run the full interview. Do this:
1. Run section refresh mode for exactly that section, asking only the missing keys.
2. Show the user why it matters in one line ("the caption skill needs your caption look").
3. Write the answer, then return control: "Section done. Going back to <skill>."

## 11. Worked example (placeholder content, abbreviated)

Assistant: "Round 1 of 12, about your business. Question 1.1: what kind of business is this? A. Local service or shop (a neighbourhood bakery). B. Creator or educator (I teach guitar on video). C. Software or app. D. Agency or freelancer. E. Personal brand or hobby. Or tell me in your own words."
User: "A, a small bakery that wants to teach home baking."
Assistant records `Business type: Local service or shop (a small bakery)`. Next: "1.2 Say what it is in one sentence: '[Name] helps [who] to [get what] by [how]'."
User: "The bakery helps neighbours learn sourdough at home by sharing short lessons."
...
Round 4. User on Q4.1: "A, smart friend." Q4.2: "you choose." Assistant records `Humour: A dry aside now and then (default, confirm later)`.
Round 6. Q6.2: "C warm and earthy." Q6.3: "my own hex, #B5532B." Assistant loads the C row, replaces the accent with the user's hex, runs the contrast check: accent on bg about 4.2, ink on bg about 13. Everything passes.
Confirm: summary table shows 11 rows, 3 defaults. User: "Change the CTA to link in bio." Assistant re asks Q3.2 and Q3.3 only. User: "confirm". Files written, validated, reported.

## 12. Failure modes

| Failure | Prevention |
| --- | --- |
| Asking 20 questions in one message | Max 5 per message, one round at a time. |
| Skipping examples to save space | Examples are the point; show them. |
| Writing the profile before the confirm step | The draft file holds answers until the user says confirm. |
| Silently picking defaults | Mark every default and list them in the confirm step. |
| Overwriting an existing profile | Always copy to `brand/history/` first. |
| Treating a skipped section as complete | Status `NOT SET`; the skill that needs it will ask later. |
| Putting a result or number in the profile that the user cannot source | Record it as `unverified` or leave it out. |
| Failing contrast accepted because the user likes the colour | Show the ratio; if the user insists on a failing pair, record `contrast waived by user` in Visual theme and warn that captions and cards may be hard to read. |
| Leaving the user with no next step | End with the hand off list below. |

## Checklist

- [ ] Checked existing files and chose a mode.
- [ ] Asked all rounds for the mode, 5 questions or fewer per message, options with examples.
- [ ] Recorded provenance for every answer in the draft.
- [ ] Ran the cross checks and resolved clashes.
- [ ] Showed the full summary and received an explicit confirm.
- [ ] Backed up existing files, wrote both files, ran heading, theme and contrast checks.
- [ ] Reported statuses, defaults and the next skill.

Hand off to: `ae-profile-schema` (format questions), `ae-theme-builder` (turn the theme into working tokens), `ae-install-and-run`, `ae-script-first-workflow`, `ae-start-here` (menu).
