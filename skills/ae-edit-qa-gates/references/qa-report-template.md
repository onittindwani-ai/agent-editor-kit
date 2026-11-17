# QA report template

Copy to `project/qa/QA-REPORT.md`. Fill every line. Keep the file; each round adds a section.

```
# QA report: <working title>

Date and time:
Edit version (state counts): cuts <n>, captions <n>, graphics <n>, fx <n>, music <yes or no>
Render checked: <path and time, or "no render yet">
Format: <size, fps> for <platforms>
Safe zones: <the user's measurement, or "approximate defaults, not verified on the user's phone">

## Verdict
BLOCKED | HOLD | READY FOR THE USER'S REVIEW
One sentence why.

## Findings (ranked)
1. [blocker] <gate ID> <time> <what is wrong> | evidence: <file or number> | fix owner: <role>
2. [major] ...
3. [minor] ...

## Gate table
| ID | Result | Evidence class | Evidence (file, number or one line of what was seen) |
| A1 | pass | S | script dated 2 days before first graphic |
| ... | | | |
(every gate from the table, none blank; use SKIPPED with a reason)

## Not checked, and why
- <gate IDs and the reason: no render yet, no phone measurement, no dictionary installed>

## Decision needed from the user (at most one)
Question, 2 to 4 options, my recommendation.

## Re run after notes (add a section per round)
Round <n>, date: notes handled <list>; gates re run <list>; results <list>.
```

Rules: the verdict word is one of the three; findings name a gate and a fix owner; "seen" always carries one line of what was seen; no row says done, fixed or working.
