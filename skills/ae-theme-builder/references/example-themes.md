# Example themes (placeholders, not recommendations)

Seven starting points of different moods. They are neutral inventions for a fictional bakery explainer channel. Copy one into `brand/theme.json`, change what the user asks, and run `theme_tokens.py`. Numbers are contrast ratios computed with the method in `SKILL.md` step 4 (ink, muted and accent are measured against `bg`; "surf/bg" is the surface to background ratio; "on accent" is the best text colour on the accent and its ratio).

Every one of them passes the minimums. Light themes show a surf/bg ratio under 1.25, which is normal: the tool marks `needs_rim` true and the render draws a 2 px rim plus a soft shadow on cards. Dark themes can pass without a rim.

## 1. Calm paper (editorial, warm light)

```
{"palette":{"bg":"#F4EFE6","surface":"#FFFFFF","ink":"#1E2430","muted":"#5B6270","accent":"#B93A0B","ok":"#2E7D32","warn":"#9A4A0A"},
 "fonts":{"heading":"Inter","body":"Inter","accent":"Instrument Serif"},
 "background":{"type":"solid","path":null},"radius":28,"shadow":"soft"}
```
Ink on bg 13.6, muted 5.4, accent 5.0, surf/bg 1.15 (rim and shadow), on accent white 5.7. Feels like printed paper. Good for teaching, craft, food, books.

## 2. Night studio (dark, cool)

```
{"palette":{"bg":"#0E1117","surface":"#1B2230","ink":"#F3F5F8","muted":"#A5AEBD","accent":"#6AA9FF","ok":"#4ADE80","warn":"#F59E0B"},
 "fonts":{"heading":"Space Grotesk","body":"Space Grotesk","accent":"Instrument Serif"},
 "background":{"type":"gradient","path":null},"radius":24,"shadow":"none"}
```
Ink on bg 17.3, muted 8.5, accent 7.9, surf/bg 1.19 (add a rim or lighten the surface a step if cards look lost), on accent is the dark bg colour at 7.9. Feels like a late night tool demo. Good for software and data topics.

## 3. Citrus bright (friendly, playful)

```
{"palette":{"bg":"#FFF1C9","surface":"#FFFFFF","ink":"#1B1B1F","muted":"#5C5C66","accent":"#D9380A","ok":"#1E7F3A","warn":"#9A5B00"},
 "fonts":{"heading":"Montserrat","body":"Montserrat","accent":"Playfair Display"},
 "background":{"type":"solid","path":null},"radius":32,"shadow":"soft"}
```
Ink on bg 15.3, muted 5.9, accent 4.1 (fine for the large highlight word, under 4.5 so never for text below 36 px), surf/bg 1.12 (rim and shadow), on accent white 4.65. Feels like a cheerful tutorial. Good for consumer topics and beginners.

## 4. Ocean clear (professional, cool light)

```
{"palette":{"bg":"#E6EFFA","surface":"#FFFFFF","ink":"#0B1F3A","muted":"#4B5F7A","accent":"#1F5FD1","ok":"#17703F","warn":"#9A4A0A"},
 "fonts":{"heading":"Manrope","body":"Manrope","accent":"Lora"},
 "background":{"type":"gradient","path":null},"radius":24,"shadow":"soft"}
```
Ink on bg 14.2, muted 5.6, accent 5.0, surf/bg 1.16 (rim and shadow), on accent white 5.8. Feels like a clear briefing. Good for services, finance, operations.

## 5. Sage soft (natural, calm)

```
{"palette":{"bg":"#DDE8DA","surface":"#F8FBF6","ink":"#1F2A22","muted":"#4A5A4F","accent":"#8A4B2A","ok":"#2E7D32","warn":"#8F5400"},
 "fonts":{"heading":"DM Sans","body":"DM Sans","accent":"Fraunces"},
 "background":{"type":"image","path":"brand/backgrounds/linen.jpg"},"radius":28,"shadow":"soft"}
```
Ink on bg 11.8, muted 5.8, accent 5.3, surf/bg 1.21 (rim and shadow), on accent white 6.7, ok on bg 4.1 (use `ok` for chips with a check mark, not for small text). The accent is clay, not green, so it never competes with the `ok` colour: when the mood is green, keep `ok` and `accent` visibly different hues. The image path is a placeholder for the user's own file; run the veil check on it.

## 6. High contrast mono (bold, trailer feel)

```
{"palette":{"bg":"#111111","surface":"#2A2A2A","ink":"#FFFFFF","muted":"#B3B3B3","accent":"#FF4D4F","ok":"#3DDC84","warn":"#FFB020"},
 "fonts":{"heading":"Montserrat","body":"Montserrat","accent":"Playfair Display"},
 "background":{"type":"solid","path":null},"radius":16,"shadow":"none"}
```
Ink on bg 18.9, muted 9.0, accent 5.8, surf/bg 1.32 (passes without a rim), on accent is the dark bg colour at 5.8 (white on this red is only 3.3, so never use white text on it). Good for punchy openings and challenge topics.

## 7. Ink and gold (premium, dark warm)

```
{"palette":{"bg":"#14110F","surface":"#2B2622","ink":"#F6F1E7","muted":"#B9AE9C","accent":"#E0B04A","ok":"#7BD88F","warn":"#F2994A"},
 "fonts":{"heading":"Playfair Display","body":"Inter","accent":"Playfair Display"},
 "background":{"type":"video","path":"brand/backgrounds/slow-loop.mp4"},"radius":20,"shadow":"soft"}
```
Ink on bg 16.7, muted 8.6, accent 9.4, surf/bg 1.26 (passes), on accent is the dark bg colour at 9.4. Heading and accent share one family here (a serif for both, so the italic is the accent voice); this is still two voices at most. The video path is a placeholder for the user's own slow loop; run the veil check on three frames.

## A theme that fails, and the repair

```
{"palette":{"bg":"#FFF8E1","surface":"#FFFFFF","ink":"#1B1B1F","muted":"#9A9AA0","accent":"#FFD23F","ok":"#1E8E3E","warn":"#B26A00"}, ...}
```
Tool output: muted on bg 2.6 FAIL, muted on surface 2.8 FAIL, accent on bg 1.4 FAIL, accent on surface 1.4 FAIL, surf/bg 1.06 (rim required). Suggestions from `--fix`: muted `#717176`, accent `#A98B2A`. The accent became a dull mustard, so the user was offered a second repair: keep the bright yellow as a fill colour for the highlight pill (with the ink colour on it, ratio 11.9) and use ink for any accent coloured word. The user picked the second repair. Both repairs were shown with a sheet before the choice.

## Using an example

1. Show the user two or three sheets (`theme_sheet.py` per candidate), never only one.
2. Replace the placeholder fonts and background paths with files the user supplied.
3. Rerun the tool; a changed colour needs a new table.
4. Save the chosen file as `brand/theme.json` and keep the sheet next to it.
