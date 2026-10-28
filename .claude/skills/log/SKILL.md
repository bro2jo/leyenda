---
name: log
description: Record anything from real life (food or a photo of a meal/label, weigh-in, creatine, morning knee check, floor minimum, knee session, PT, upper body, conditioning, sport drills, sleep, time together). Use whenever a message contains something to record, even without /log. Closing a day is /close.
argument-hint: "[what you ate / did / felt]"
allowed-tools: Bash(python3 engine/darrow.py *) Bash(python3 engine/saga.py *) Bash(git *) Read Edit Write
---

# /log

Input: $ARGUMENTS (plus any attached photo). Ledger first, Chronicle after. Closing a day and writing its scene is `/close`, not here.

## 1. Sort the message
- **Date:** today in America/New_York (`python3 engine/darrow.py today` prints it); "yesterday", "last night", "this morning" resolve against it. A log sent after midnight about dinner belongs to the previous day: say which day you used.
- **An answer to an open choice** ("2", "go the long way", "tell her the truth") is handled **first**, through `/choose`. A Darrow action while nothing is open is `/play`, after the Ledger reply and instead of the glimpse. A bare number is an answer only while a choice is open (`python3 engine/saga.py now` shows one).
- **"close day"**, or a new day's first log while the previous day has something logged and is not closed: `/close`, after this log.
- **A task of the week's work done** ("car's clean", "listed it"): `/project` step 2, after the Ledger part of this log: `project done`, then its piece of the tale in the same reply (it takes the glimpse's place). A new goal for the week, or "drop it": `/project`.
- Everything else sorts into: **food** → `food add` · **weigh-in, creatine, shake** → `set nutrition` · **the morning check, the daily minimum, sessions, sleep, time together** → `set daily` · **exercise detail** → `ex add` · **throwing or film** → `sport add` · **a measured number** (goniometer, dynamometer, 1RM, hop) → `measure add` · **a PT or surgeon visit** → `/ingest`'s visit procedure (its rows here, the note in `real/visits/pt_notes.md`, `pt=Y`) · **a session the plan itself moves, cancels or rests** → `real/config.json → plan_changes` (`{"date", "drop": [codes], "add": [codes], "source", "why"}`; never a miss; a rest day the plan orders gets a row with `light=red`; a booked PT visit he did not go to is `pt=missed`).

## 2. Safety screen (before anything else)
- **Red flags** (fever, calf pain or swelling, chest pain, shortness of breath, wound changes, giving way, sudden swelling, loss of extension, inability to walk normally): reply in plain language and tell him to contact the surgical team/PT. Still log what he said. `light=red`. No story today.
- **Yellow** (pain 3–4, mild new swelling, stiffer than usual, pre-check fails): note the plan's response (`python3 engine/darrow.py doc state "pre-session check"`). `light=yellow`.
- **Off-plan work** (not yet cleared: impact past the State's current rung or more than one change to it, running, jumping outside the impact ladder, step-out throws or throwing on the move; several changes at once; a load jump past one DB step or 10%): log it truthfully, `knee_as_planned=N` if a knee session, and name the plan's rule in one plain sentence. No scolding. No story reward.

## 3. Food
1. `python3 engine/darrow.py food lib "<words>"`: a library row's numbers × quantity. A row with blank fields: estimate the blanks, `source=library+estimate`, ask him **once** for the label; when he gives it, update `real/logs/food_library.csv`. Never invent label values.
2. Otherwise estimate from the label, the photo, or typical values; fill every nutrient column you reasonably can; `source` = `label`, `library`, `photo` or `estimate`. State a guessed quantity ("assumed ~1.5 cups rice"); ask only if it could swing >200 kcal, and log your best estimate anyway.
3. All items in one call: `python3 engine/darrow.py food add '[{…},{…}]'`. A new recurring item with label numbers goes in the library.

## 4. Status and sessions
- `python3 engine/darrow.py set daily DATE key=value …` · `set nutrition DATE weight_lb=… creatine=Y` · `ex add '[…]'` · `sport add '[…]'`. What a day already holds: `show daily|nutrition|food|ex|sport DATE`. Never read a CSV raw.
- **The words are fixed** (`real/config.json → vocabulary`; the engine refuses anything else, so a code never silently pays or costs): `knee_session` A/B/min/home/partial · `addon_session` upperA/upperB/accessory/power/arms (joined with +) · `light` green/yellow/red · `pt` Y/missed · `floor_am`/`floor_pm`, `knee_as_planned`, `together`, `creatine` Y/N · exercise `session` home/PT/floor/HEP/upperA/upperB/accessory/power/conditioning and `block` from the list · sport `session` A/B/C/film/test/review, `skill` from `config.json → sport.skills`. A new code goes in the list first.
- **What to ask for:** the Working Rules' check-in set (`doc rules check-in`): a morning **grade** (0/trace/1+/2+/3+; "quiet", "same" go in `am_trend`), stiffness (`am_notes`), catch, wellness 1–5; after a session its minutes and RPE; after a throwing session the throws by type, the stance (planted / slight pivots), the **pivot foot** (named in the row's `drill`), minutes and RPE; nothing about the leg between upper sets (optional since 10/21). The heel prop is a weekly check since 10/18: asked and logged (`floor_am=Y`) on Sundays only, never on an off day. A session cut below its minimum is `knee_session=partial`: not a loaded day.
- `knee_as_planned=Y` when the session ran **as prescribed**: the State's doses for that day (`doc state "session a"` / `"session b"`), a planned progression included, with nothing past the plan; `N` when an item went past the plan, a change the plan did not call for was made, or the session was cut short. It is the one deed that pays for discipline (Resolve), so it is a judgment made every knee session, never left blank. A planned item he skipped may be an exercise row whose notes start `NOT DONE`: a record, never a deed. Upper sessions: the main lifts as rows, the warm-up and the finisher as one "as written" row each (`block` warmup/finisher), the posture cooldown as one row.
- **Time together on purpose** ("dinner with Rae", date night, a walk, a trip): `together=Y` on that date, and that is the whole record: nothing else logged or asked. It feeds the Tether only.
- Sport rows: one per skill worked (`doc sport logging`); the phase decides what is allowed (`config.json → sport.stage`; `doc sport 3`); anything ahead of its phase is logged truthfully with its gate named in one plain sentence.
- Keep `notes` short: a visit goes to `pt_notes.md`, a paragraph to the week's checkpoint file; the cell gets a pointer. Column meanings: `doc rules "log files"`; what the engine pays for each field: `engine/rules.json`.

## 5. Sync and reply
- `python3 engine/darrow.py sync`: read the **RECKONING CHANGES** lines (a `TETHER TIED` / `TETHER DRAWN` line is one of them: it goes in the bracketed Reckoning line, unexplained).
- Reply in the shape of `.claude/skills/log/reply.md`: Ledger first (items, running totals vs targets, done, still open today), the **level-up block** if `sync` printed LEVEL UP, **one** bracketed Reckoning line only if something changed, then **the glimpse**: `python3 engine/saga.py glimpse show --n 3` (no kind twice running, no reused image), one or two italic sentences of life at the House drawn from how the day has gone, the sheet and his choices, never plot, never the log mirrored, never a mechanic explained; a saying or verse comes from `python3 engine/saga.py lore pick saying|verse`, never invented. `python3 engine/saga.py glimpse add --kind <house|overheard|ledger|saying|verse|body|weather> "…"` keeps it (it refuses a name the page has not spoken and a repeated kind). No glimpse in a red-flag reply or when the story is off that day.
- If the plan in force, the next PT visit, the gate or a flag changed, update the top section of `real/NOW.md`. Never counts there.

## 6. Save
`python3 engine/darrow.py ship -m "log DATE: <short summary>"`: every log ships, because the site shows the sheet from it. If it stops at a step, fix what that step printed and ship again. The message is reader-safe (CLAUDE.md).
