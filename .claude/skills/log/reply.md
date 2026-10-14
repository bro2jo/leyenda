# Reply shape for a log, and the glimpse

*Read by `/log` step 5 for every log reply, and by `/checkpoint` and the day close for the level-up block. Moved from CLAUDE.md unchanged.*

## Reply shape for a log

Mobile-first. Ledger first, Chronicle after, separated by a rule.

```
📒 LEDGER · Thu 10/8
🍽️ Premier shake: 160 kcal · 30 P
🍽️ Chicken rice bowl (est.): 1,450 kcal · 70 P · Na ~1,900 mg
📊 Today 1,610 / 3,000 kcal · 100 / 150 P → 1,390 kcal and 50 P to go
✅ Floor AM · morning check (trace, pain 0)
⏭️ Still today: floor PM · bike 15 · creatine
───
⟦ +45 XP · Warden's Eye II ⟧
*Snow on the sill again. Down the hall, Hollis is swearing at the beech leg one strap at a time, and the leg is winning.*
```

- Food lines: item, kcal, protein, plus at most 2–3 micros that matter for that item. The full micro row goes to the CSV.
- Coaching is one or two lines, specific, and only when useful (e.g., protein pacing for the evening). No lectures.
- Time together on purpose is one word in the ✅ line (`together`), no detail. When `sync` reports a `TETHER` line, it is a Reckoning line like any other (`⟦ The Tether: a hand ⟧`), and nothing is explained.
- The week's work rides the ⏭️ line as its next task (`project: park the CRV`), from the engine's `Project:` line. A task reported done gets its own ✅ (`project: task 2 of 3`) and its piece of the tale after the rule, under its `### Piece K — Title` heading, in place of the glimpse; a finished project is a Reckoning line (`⟦ Works: 1 ⟧`, and the Inspiration), unexplained.
- The story part of a normal log is the Reckoning line in brackets (only when the engine's `sync` reported a change), then **a glimpse** (below). Scenes are written only at **day close**.
- **A level-up gets its own block**, in any reply whose `sync` reported one (a log, a close, a checkpoint), right after the rule and before the Reckoning line: `⟦ LEVEL 6 ⟧` on its own line, then one line of what it gave, taken from `sync` (HP, proficiency when it moves, +1 Inspiration and the new total, the rank when it changes), and for a new rank one more line saying the next scene will show it. This is the one place a reply names what the sheet gained, so that a level feels like something; everything else about the mechanics stays his to discover.
- A close-day reply whose slot carried an **invitation** ends on its offer: one in-world sentence, never a list (`saga/bible/style.md` §3).

## The glimpse (every log reply)

One or two italic sentences, at most ~40 words, after the Reckoning line (or straight after the rule when nothing changed): life at Saint Ysolde's in the story's present moment, between the last scene written and the next. It deepens the world and never moves it. Glimpses are flavour and fun, not canon: one with every log reply that calls for it, no daily cap.

- **Drawn from** how the day has gone so far, the sheet and his choices. A good day shows as warmth, colour and ease in him; a low Ember lets the cold in, never as blame. An Art or attribute that just moved shows as something he now notices or can do. Choices show as how people address him, a companion warmer or cooler by approval, a Bearing lean, an epithet the page has already spoken. It reacts to what was done, never to what is missing: no guilt, no nudge, no lesson.
- **Kinds, rotated:** a moment in the House (someone on the page doing something small) · a line overheard (lay brothers, the kitchen) · a tally from Wren's ledgers (in-world counts only) · a saying, rhyme or verse of the realm (drawn with `python3 engine/saga.py lore pick saying|verse|maxim`, never invented on the spot) · the body (the knee, warmth or cold in his hands) · weather on the Steps.
- **Never** plot: no event the next scene must honour, nothing from the chapter plan, world moves, quests or arc, no plant, no hint, no reveal. Never a name, place or fact the page has not spoken. Never mirroring the log (food logged is not Darrow eating; a session logged is not the forms; an evening logged with Rae is not Rae on the page). Never a mechanic explained, never anything from `real/`. A glimpse is consistent with canon and binds nothing: habitual or interior moments, never where someone is going next.
- **None** in a day-close reply (the scene is the story), in a red-flag reply, or when the story is off that day. A red-light day's glimpse shows the House, not Darrow.
- Before writing one, `python3 engine/saga.py glimpse show --n 3` (no kind twice running, no reused image); then `python3 engine/saga.py glimpse add --kind <kind> "<text>"` keeps it (it refuses a repeated kind and a name the page has not spoken, and keeps the file to its last 20). The site never reads it. The day's brief quotes that day's glimpses before the scene is written, so the scene doesn't contradict them; it may echo one and never has to.
