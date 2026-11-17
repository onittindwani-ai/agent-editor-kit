# Voice log entry template

Append one entry per batch of user edits to `brand/voice-log.md`. Never rewrite an older entry.

```
## <YYYY-MM-DD> batch <n>: <script name>

Files: agent version <path under brand/superseded/>, user version <path>
Words: <old count> -> <new count>   Similarity: <0.00 to 1.00>   Estimated seconds: <old> -> <new>

Added:        <phrases, with line number>
Removed:      <phrases, with line number>
Replaced:     <old> -> <new>   (repeat per change)
Emphasis:     <words newly capitalised or marked>
Connectors:   <where and, so, but, because were added or removed>
Layout:       <line breaks, one step per line, paragraphs merged or split>
Punctuation:  <commas, full stops, colons, ellipses>
Order:        <beats that moved>

Inferences (label each as inference, with a confidence of low, medium or high):
- <inference>

Counts after this batch (pattern: observations in this many scripts):
- <pattern>: <n> in <m> scripts   (promote at 3 in 2)

Flagged slips (asked once, kept as written until the user decides):
- <line and the question asked>

Passed on to ae-owner-notes-to-rules: <yes or no, which skills>
```

## Rule file format (`brand/voice-rules.md`)

```
# Voice rules (evidence based)

1. <rule in one sentence>. Observed <n> times in <m> scripts. Example: "<user's own words>". Last confirmed: <date>.
```

Rules keep the user's exact example lines. Rules never contain facts about the business.
