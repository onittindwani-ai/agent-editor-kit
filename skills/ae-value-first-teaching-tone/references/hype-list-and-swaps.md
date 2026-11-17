# Banned hype list and swaps

A hype word is a signal that a fact is missing. Replace the word with the fact behind it. If no fact exists, delete the sentence.

## Banned in points and in the body

| Word or phrase | Why | Swap with |
| --- | --- | --- |
| insane, crazy, unreal | pressure with no content | the measured size of the thing |
| game changer, revolutionary, groundbreaking | claims a change nobody checked | what changed, by how much, measured how |
| mind blowing, unbelievable, jaw dropping | tells the viewer how to feel | the surprising fact itself |
| secret, hidden trick, they do not want you to know | implies concealment you cannot prove | "something that is easy to miss" if true |
| must have, you need this, you have to try this now | pressure | "if you want X, then try Y" |
| nobody is talking about this | an unprovable absence | "I looked and found few write ups" only if you did |
| magic, magical, effortless | hides the work | the real steps and time |
| explosive growth, skyrocket | invented trajectory | the real numbers with dates |
| guaranteed, 100 percent, foolproof | promise you cannot keep | "in my tests", "usually" |
| the best, the ultimate, number one | needs a comparison | name the comparison and the criterion |
| only today, last chance, limited spots | fake scarcity | state real limits only |
| you will not believe | fake disbelief | state it and let them react |
| everyone is doing this, most people | invented prevalence | a sourced figure, or drop it |
| literally changed my life | unprovable intensity | what changed for you, specifically |
| 10x, 100x | needs a baseline | the baseline and the measurement |
| for free (unchecked) | free tiers have limits | "free up to [limit], checked on [date]" |

## Allowed with care

| Phrase | Condition |
| --- | --- |
| "Here is the part the coverage skipped" | you checked what the coverage left out |
| "Most of the coverage is about [A]" | describes coverage you actually read |
| "I tried it myself" | the user did |
| "bold" hook claim | every word true and sourced, ledger row exists |

## Tone checks

- Would a calm friend say this sentence out loud without cringing?
- Does the sentence say what the thing does, or how to feel about it?
- Could the sentence be moved to any other video? If yes, it is filler.

## Scan procedure

1. Search the script for each phrase above, case insensitive.
2. For each hit: write the fact it hides, or delete.
3. Report the count of hits before and after.

```python
import re, sys
bad = ["insane","crazy","game changer","mind blowing","unbelievable","secret","revolutionary",
       "must have","you need this","nobody is talking","magic","guaranteed","100 percent",
       "the best","only today","you will not believe","literally changed"]
t = open(sys.argv[1], encoding="utf-8").read().lower()
for b in bad:
    for m in re.finditer(re.escape(b), t):
        print(b, "at", m.start())
```

The scan finds words, not meaning. A script can sell without any of these words; read it as a stranger too.
