# Recheck procedure (filming day and posting day)

Volatile facts change between writing and posting: prices, versions, free tier limits, availability, rankings, benchmark results, star counts, follower counts, policy text, news developments.

## When

1. When the script is first drafted (the ledger is built).
2. On the day of filming: reopen every volatile row's source and compare.
3. On the day of posting: repeat. If any number moved, tell the user before posting.
4. After a script change: recheck only the changed rows and the rows that depend on them.

## What to do for each row

1. Open the source. Read the passage again.
2. Same? Update "Date checked", leave wording.
3. Changed slightly? Choose the safe wording that is true now, update the script line, list it as stale (`ae-script-first-workflow`), and tell the user.
4. Changed a lot or gone? Mark RECHECK, tell the user, propose cut or rewrite.
5. A number that clears a spoken threshold by a hair ("over 10,000") is flagged to the user: leave a margin or say "about".

## News items

- Confirm the event at its primary source, with the date.
- Separate the event from the reactions. Check that the numbers quoted in coverage match the primary.
- Do not state a cause that no source states.
- Time the story: if it is over about 30 days old, say when.
- Record whether the company has confirmed, denied or said nothing, and use the matching verb.

## Report format

```
Recheck <date>:
C2 unchanged (checked 09:10)
C5 price changed from [a] to [b]: script line 9 needs "as of [date]" wording. Proposed line: "..."
C7 source page removed: propose cut.
```

Never say "all verified". Say what was rechecked, what changed, what could not be reached.
