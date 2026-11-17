# Templates for the script first workflow

## STATUS.md template

```
# Status
Project: <short name>
Date opened: <date>
Current gate: <G0 to G8>
Next action: <one line, who does it>

## Gates
G0 Intake ............ done / open
G1 Summary ........... done / open
G2 Ledger ............ done / open (rows: N, unverified: N)
G3 Script ............ sent / approved / changed (round N)
G4 Review gate ....... scores: <hook> <flow> <truth> <cta> ... total /10
G5 Plan .............. open / agreed
G6 Build ............. not started / in progress / finished
G7 QC ................ not started / evidence attached
G8 Export, publish ... waiting for the user's go

## Resource or giveaway
State: not needed / planned / built and tested / NOT BUILT
Counts promised in the script: <list>
Counts that really exist: <list>

## Stale list (items to redo after the last script change)
- <item>

## Open questions for the user (at most 3)
1. <question with options>
```

## Edit round log template (append one block per round)

```
Round <n>, <date>
User note (verbatim): "<their words>"
Lines changed (old -> new): ...
Words saved or added: <number>
Ledger rows touched: <ids>
Stale items: <list>
Superseded copy: project/script/superseded/<file>
```

## Safe copy command pattern

Use a literal absolute path for the copy and never a wildcard:

```
cp "/absolute/path/to/project/script/SCRIPT.txt" "/absolute/path/to/project/script/superseded/SCRIPT-2026-01-01-1.txt"
```

## Brief questions card (show this when starting intake)

1. How long should it be? (a) 30 to 35 seconds (b) 45 to 60 seconds (c) 60 to 90 seconds (d) long form (e) something else
2. Where will it live? (a) Instagram and YouTube Shorts (b) TikTok (c) LinkedIn (d) all of them with the same words
3. What should the viewer leave with? (a) one thing to do (b) one idea corrected (c) one news item explained (d) a choice made easier
4. What happens at the end? (a) comment a word to get a resource (b) link in the description (c) follow for the next part (d) no action
5. Where do the facts come from? (a) your own experience (b) a page you will name (c) news we verify together (d) a tool we test first
