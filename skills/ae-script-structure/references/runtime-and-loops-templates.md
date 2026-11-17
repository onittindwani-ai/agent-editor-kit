# Runtime calculator and loop table templates

## Quick runtime table (words to seconds)

| Words | At 3.0 wps | At 2.7 wps | At 2.5 wps |
| --- | --- | --- | --- |
| 60 | 20 s | 22 s | 24 s |
| 80 | 27 s | 30 s | 32 s |
| 100 | 33 s | 37 s | 40 s |
| 120 | 40 s | 44 s | 48 s |
| 150 | 50 s | 56 s | 60 s |
| 180 | 60 s | 67 s | 72 s |
| 250 | 83 s | 93 s | 100 s |
| 1500 | 8:20 | 9:15 | 10:00 |

Report the range from the 3.0 and 2.5 columns and call it an estimate until a real take exists.

## Python snippet to count and estimate

```python
import re, sys
text = open(sys.argv[1], encoding="utf-8").read()
words = re.findall(r"[A-Za-z0-9][A-Za-z0-9'%$.,-]*", text)
n = len(words)
print(n, "words;", round(n / 3.0), "to", round(n / 2.5), "seconds")
```

Run on the spoken-only file so labels are not counted.

## LOOPS.md template

```
| Loop (question the viewer has) | Opened at (line or time) | Closes at | Closed by | Same specificity? |
| --- | --- | --- | --- | --- |
```

## Line function map template

```
| # | Line (first words) | Job | Needed? | Cut test result |
| --- | --- | --- | --- | --- |
```
Jobs: HOOK, RELEVANCE, EVIDENCE, DEFINITION, MECHANISM, STEP, CATCH, PAYOFF, ACTION.

## Choppy to flowing (structure level)

Before (5 beats of 4 words each, no links):
"Dough needs rest. Yeast makes gas. Gas lifts bread. Short rest fails. Dense loaf."
After (one flowing beat, 32 words): "Dough needs time to rest because the yeast makes gas while it sits, and that gas is what lifts the bread, so if you cut the rest short, you bake a dense loaf."

## Long form re hook examples (placeholder)

- At 3 minutes: "That is the easy half. The half that costs people money is the next one."
- At 6 minutes: "Hold that thought, because the number I just gave you changes when you look at it per loaf."
Each re hook must correspond to a real payoff that comes.
