---
name: ae-claims-and-truth-ledger
description: Builds and maintains the claim ledger for a script: every number, name, date, comparison and screen gets an evidence class, a source, safe wording and a recheck. Use when the user says "check my facts", "is this true", "add sources", "verify this claim", "fact check the script", "is this safe to say", or before any script is approved or posted.
---

# Claims and truth ledger

Read `brand/profile.md`. If it is missing or a section this skill needs (`## Claims policy`, `## Rules`) is empty, stop and run `ae-setup-interview` for that section (ask the user, with options), do not guess.

## The strong rule

Never invent a fact, number, quote, screen, result, reaction or story. A hook or script may be bold only if every word is true and sourced. When the evidence is weaker than the sentence, change the sentence, not the evidence. A claim you cannot support is removed or rewritten as opinion or as a plan; it is never kept because it sounds good. A missing source is a blocker to report, not a gap to fill with something plausible.

## What counts as a claim

Anything a viewer could repeat as a fact: a number, a percentage, a price, a date, a ranking, a comparison ("faster than", "cheaper than"), a capability ("it can do X"), a cause ("this happens because"), a quote, a named person or company doing something, a result ("this worked for me"), a screen or page shown, a count of things promised (see `ae-call-to-action-writing`), and any claim implied by an image. Opinions are allowed when framed as the user's view.

## Evidence classes (label every row)

| Code | Class | Meaning | Public wording |
| --- | --- | --- | --- |
| P | Primary | The original source: official documentation, the filing, the dataset, the page itself, the researcher's statement | State plainly, cite the source |
| S | Secondary | A reputable report about the primary source | Prefer to find the primary; if kept, say "reported by" |
| V | Vendor claim | A company says it about its own product | "The company says ..." never as independent fact |
| O | Own measured | The user's own test, log, or result, with the method recorded | "In my test ..." with the real scope |
| E | Own experience | The user's story, not measured | "In my experience ..." never as a universal result |
| I | Inference | Your reasoned interpretation | Say "this suggests", "my read is" |
| R | Recommendation | A proposed practice | "I would", "try" |
| X | Unverified | Not established | Do not state; research or cut |
| U | Opinion | A clearly framed judgment | "I think" |

Rules: never upgrade a class (a vendor claim stays V until independent evidence exists; one user's experience stays E and is never presented as a result for everyone; an inference is not a fact). Where sources conflict, record both and use the weaker wording or cut.

## The ledger table

One ledger per video at `project/script/LEDGER.md`. Template file: `references/ledger-template.md`. Columns:

| ID | Claim as spoken | Exact meaning (unit, scope) | Class | Source (title, location) | Date checked | Confidence | Safe wording | Recheck | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

Confidence: high (primary and checked today), medium (reputable, or primary but dated), low (single or unclear source). Status: OK, REWRITE, CUT, BLOCKED (waiting for the user or a source), RECHECK.

Every row maps to a script line number. A script line with a claim and no row is a failed gate. A row with no script line is removed or kept as a note.

## How to build the ledger (steps)

1. Read the script (or the brief for a pre draft). Underline every claim as defined above.
2. For each claim, ask what exactly it counts or compares. Write the unit and scope: per token, per month, of what group, measured how, in which version.
3. Find the source in this order: the user's own records (ask for them), first party documentation or the primary page, a direct dataset or paper, a reputable report. Social posts and videos are leads, not evidence of a capability.
4. Open the source yourself and read the exact passage. Do not rely on a summary or memory. Quote the exact passage in the row (a short excerpt, in your own notes only; never copy long text).
5. Record the date checked, and the source date. Volatile facts (prices, versions, availability, benchmarks, rankings, free tier limits) expire fast.
6. Choose the safe wording: the strongest sentence the evidence supports. See the transformation table below.
7. Mark the class. If it is V, X or E, the script wording must reflect that.
8. Mark the recheck: volatile claims are rechecked on the day of filming and on the day of posting (`references/recheck-procedure.md`).
9. Report to the user: counts by class, rows that need their input, rows that changed the script, rows that are blocked.

## Safe wording transformations

| Evidence says | Do not say | Say |
| --- | --- | --- |
| Up to 40 percent in the vendor's benchmark | "40 percent faster" | "The company's own test shows up to 40 percent faster on [task]." |
| One user's test | "This works" | "In my test, this worked." |
| A study of 200 adults | "People do X" | "In a study of 200 adults, [result]." |
| A price on the page today | "It costs [N]" with no date | "It is [N] a month on their page as of [date]." |
| Source silent on cause | "It failed because of X" | "It failed, and the report points to X." / "The cause is not stated." |
| A beta feature | "It does X" | "In the beta, it can do X." |
| Free tier with limits | "It is free" | "It is free up to [limit]." |
| Two sources with different numbers | pick the bigger | "Estimates range from [a] to [b]." |
| A famous name used a method | "[Name] uses this" | cite their exact public statement or drop it |
| A plan announced | "It launches this month" | "The company says it plans to launch it this month." |
| A competitor comparison | "X beats Y" | "On [named task], with [named setup], X scored [a] and Y scored [b]." |

## Numbers

- Name the unit every time (per month, per token, per task, per person).
- Round fairly: 1,847 can be "about 1,800" or "nearly 1,900", never "over 2,000". "Almost" and "over" must be true.
- Do not put two sources' numbers side by side without naming each source.
- Do not turn a count into a rate or a rate into a count.
- Percent of what? A rise from 2 to 3 is 50 percent and one extra case; say both when the relative figure alone misleads.
- Currency and date go together. Convert only with a dated rate.
- Counters on screen must equal the spoken number and the ledger value (`ae-counters-and-numbers`).

## Dates and old events

An event older than about 30 days is spoken with when it happened relative to today ("last December", "about 2 years ago") and the ledger holds the full date. A thing the company said it would do is spoken as a plan. Time sensitive scripts get a recheck date and a "valid until" line in STATUS.

## Screens, pages and quotes shown on screen

Before you write a line that describes a page, capture or open it yourself and record: the URL or file, the date, the exact headings, labels and numbers on the screen, the part that will be highlighted, and whether it can be shown (rights). Never describe a page from memory, and never show a mock up as real. A shown screen is a claim: it goes in the ledger with a capture reference (`ae-proof-cards-and-real-screens`). A quote on screen is the exact words, the speaker, the place and the date, or it is not shown.

## Borrowed credibility

Using a famous name, company, study, ranking or quote to look credible is allowed only as a verified public fact: primary source, exact wording, date, a ledger row, and no implied personal link, partnership or endorsement. If nobody famous uses the thing, say so to the user rather than implying it. Honest alternatives: cite a respected source that supports the METHOD (checked at the source), name the well known work a tool is built on (and say it is not theirs), or use the user's own recorded result.

## Never claim (hard list)

- A guarantee, a promise of income, health, safety or legal outcomes.
- A result for the audience from one person's experience.
- That a tool makes anything "secure", "compliant", "safe" or "legal".
- A reason for someone else's mistake ("they forgot") without a source.
- A hypothetical as if it happened. Say "imagine", "suppose" or "if".
- Privacy breaking details (client names, customer data, private messages) without the user's written approval; use anonymised or synthetic examples and label them as examples.
- That the user tested something they did not test.
- Statistics, quotes, reviews or testimonials that were not collected.
- "Everyone", "most people", "nobody" without a source.
- Anything the profile's `## Claims policy` forbids.

## Claims policy options (ask the user in the interview)

(a) strict: only primary or own measured facts may be stated as facts; (b) standard: secondary sources allowed if labelled; (c) news mode: every item rechecked on posting day; (d) opinion led: facts are minimal, opinions are labelled. Record the choice in the profile and obey it.

## Output and handoff

Return a short table: rows by class and status, a list of script lines changed because of the ledger (old, new, why), the list of blocked rows with exactly what is needed from the user (for example "the number of loaves in your test", "the page URL"), and the recheck dates. Do not say a script is "verified". Say what was checked, from which source, on which date, and what was not.

## Worked example (placeholder, 4 rows)

Script lines: (1) "A one week feeding schedule brought my starter back in 3 days." (2) "The smell comes from acetone like compounds." (3) "The schedule works for any flour." (4) "The guide has 5 schedules."

| ID | Claim | Meaning | Class | Source | Date | Conf | Safe wording | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C1 | 3 days | one starter, user's own log | O | user log, entries 1 to 3 | 2026-01-05 | medium | "In my test, my starter was back in 3 days." | REWRITE |
| C2 | acetone like compounds | named in the reference page, section 2 | P | baking reference page, section 2 | 2026-01-05 | high | "Bakers often link that smell to acetone like compounds." | OK |
| C3 | any flour | tested on 1 flour only | X | none | n/a | low | "I tested it on whole wheat. I have not tested other flours." | REWRITE |
| C4 | 5 schedules | count of resource files | O | folder count | 2026-01-05 | high | "5 schedules" only if 5 exist today | BLOCKED until built |

Result: lines 1 and 3 rewritten; line 4 held until the guide has 5 schedules. Report to the user: 4 rows, 1 OK, 2 rewritten, 1 blocked.

## Failure modes

| Failure | Fix |
| --- | --- |
| Quoting a summary instead of the source | Open the source and read the passage |
| Vendor claim stated as fact | Add "the company says" |
| One user's result stated as general | Use "in my test" with scope |
| Stale price or version | Date it, recheck on posting day |
| Two sources joined in one number | Split and name each |
| Moving on when a source cannot be found | Rewrite as opinion or cut |
| Calling the script verified | Report what was checked and what was not |

## Checklist

- [ ] Every claim underlined; every claim has a row; every row maps to a line.
- [ ] Classes assigned and never upgraded.
- [ ] Units and scope written; rounding fair.
- [ ] Source opened and the passage read; date checked recorded.
- [ ] Safe wording used in the script; changed lines listed.
- [ ] Borrowed credibility only from verified public facts.
- [ ] Screens captured by you, with the date; mock ups labelled.
- [ ] Rechecks scheduled for volatile claims (filming day, posting day).
- [ ] Blocked rows reported with exactly what is needed.

## Hand off to

`ae-hook-writing` and `ae-value-first-teaching-tone` (wording), `ae-call-to-action-writing` (counts), `ae-script-review-gate` (truth score), `ae-script-first-workflow` (approval), `ae-proof-cards-and-real-screens` and `ae-counters-and-numbers` (on screen facts), `ae-publish-packaging` (links and posting day recheck).
