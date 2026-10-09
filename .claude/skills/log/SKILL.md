---
name: log
description: Record anything from real life (food or a photo of a meal/label, weigh-in, creatine, morning knee check, floor minimum, knee session, PT, upper body, conditioning, sport drills, sleep) or close the day. Use whenever a message contains something to record, even without /log.
argument-hint: "[what you ate / did / felt]  or  close day"
allowed-tools: Bash(python3 engine/darrow.py *) Bash(python3 engine/saga.py *) Bash(python3 engine/build_site.py *) Bash(git *) Read Edit Write
---

# /log

Input: $ARGUMENTS (plus any attached photo).

## 1. Parse
- **Date:** default today in America/New_York (`python3 engine/darrow.py today` prints it). Resolve "yesterday", "last night", "this morning". A log sent after midnight about "dinner" belongs to the previous day; say which day you used.
- Sort everything into:
  - **food items** → `food_entries.csv`
  - **day nutrition fields** → `nutrition_log.csv` (`weight_lb`, `creatine`, `shake`, `notes`)
  - **day status and sessions** → `daily_log.csv` (`am_swelling`, `am_pain`, `am_extension`, `am_notes`, `floor_am`, `floor_pm`, `knee_session`, `knee_min`, `knee_rpe`, `knee_as_planned`, `pt`, `addon_session`, `addon_min`, `addon_rpe`, `conditioning_type`, `conditioning_min`, `sport_min`, `hours_on_feet`, `gym_min_on_feet`, `sleep_h`, `light`, `notes`)
  - **exercise detail** → `ACL_Exercise_Log.csv`
  - **sport drills** → `sport_log.csv`
  - **"close day"** → step 6
  - **an answer to an open story choice** ("2", "go the long way", "tell her the truth") → handled **first**, through `/choose`, before anything else in the message. A bare number is an answer only while a choice is open (`python3 engine/saga.py now` prints the open micro-choice; a climax choice is in `saga/NOW.md`); otherwise it is a quantity or a number from the day.

## 2. Safety screen (before anything else)
- **Red flags** (fever, calf pain/swelling, chest pain, shortness of breath, wound changes, giving way, sudden swelling, loss of extension, inability to walk normally): reply in plain language and tell him to contact the surgical team/PT. Still log what he said. Set `light=red`. No story today.
- **Yellow** (pain 3–4, mild new swelling, stiffer than usual, pre-check fails): note the plan's response (last clean doses, 2 sets, no changes; Working Rules / recovery state §6). `light=yellow`.
- **Off-plan work** (something not yet cleared: impact, running, jumping, pivoting; several changes at once; a load jump bigger than one DB step or 10%): log it truthfully, set `knee_as_planned=N` if it was a knee session, and name the plan's rule in one plain sentence. No scolding. No story reward.

## 3. Food
For each item:
1. `python3 engine/darrow.py food lib "<words>"`. If it's in the library, use those numbers × quantity. **If a library row has blank fields** (e.g. kcal or protein missing), estimate the blanks at log time, set `source=library+estimate`, and in the Ledger reply ask him **once** for the label numbers for that item. When he gives them, update that row in `real/logs/foods.csv` (and note `label` as the source). Never invent label values; leave the existing partial rows as they are until he supplies the numbers.
2. Otherwise estimate from the label (if shown), the photo, or typical values. **Fill every nutrient column you reasonably can** (kcal, protein, carbs, fat, fiber, sat fat, sugar, sodium, potassium, calcium, iron, magnesium, zinc, vit C, vit D, omega-3); blank only what's truly unknowable. Set `source` = `label`, `library`, `photo` or `estimate`.
3. State your assumption when a quantity is guessed ("assumed ~1.5 cups rice"). Ask only if the guess could swing >200 kcal, and then still log your best estimate.
4. Add all items in one call: `python3 engine/darrow.py food add '[{...},{...}]'`.
5. If he gives label numbers for a new recurring item, add it to `real/logs/foods.csv`.

## 4. Status, sessions, details
- `python3 engine/darrow.py set daily DATE key=value …` (and `set nutrition DATE weight_lb=… creatine=Y`).
- To see what a day already holds, `python3 engine/darrow.py show daily DATE` (or `show nutrition|food|ex|sport DATE`): key: value lines, nothing to count. Never open a CSV and read it by column position.
- Keep `notes` short. A weekly recap or any paragraph goes to `real/checkpoints/<Sunday>.md`; the cell gets a pointer.
- `knee_as_planned=Y` only when he says or clearly implies the session ran as written (one change per exercise at most, per the Working Rules).
- Exercise detail: `python3 engine/darrow.py ex add '[…]'`. Use the existing CSV's style (see recent rows). If he just says "Session A as written", one row is enough: `{"date":…, "session":"home", "block":"knee", "exercise":"Session A as written", "side":"L"}`.
- Upper body: `session` = `upperA`/`upperB`/`accessory`/`power`/`arms`; log main lifts with sets × reps × load.
- Sport: `python3 engine/darrow.py sport add '[…]'` (see `real/plan/sport/` for skill names).

## 5. Sync and reply
- `python3 engine/darrow.py sync`. Read the **RECKONING CHANGES** lines.
- Reply in the CLAUDE.md "Reply shape for a log" format: Ledger first (items, running totals vs targets, what's done, what's still open today), then **one** bracketed Reckoning line only if something changed. Keep it short enough to read on a phone.
- If today's remaining plan changed, update the top section of `real/NOW.md`.

## 6. Close day (when he says so, or when a new day's first log arrives and the previous day has something logged and its `closed` column in `daily_log.csv` isn't `Y`)
- If the previous week's chapter is unclosed (`python3 engine/saga.py route show`), run `/checkpoint` before closing any day of the new week; `plan next --date` has no slot for a new-week day until the next chapter is open.
- **`daily_log.csv → closed` is the single source of truth.** Check it first (`python3 engine/darrow.py today --date DATE` shows "day closed"). If it is already `Y`, do not write another scene for that day.
- **A log for an already-closed day:** record it (steps 1–5), `sync`, reply with the Ledger. The engine's totals, XP and the week's tier update (the tier keeps moving until `chapter-close` freezes it). No new scene unless he asks for one.
- `python3 engine/darrow.py set daily DATE closed=Y`, then `sync`, then `python3 engine/saga.py now` and `python3 engine/saga.py plan next --date DATE --full`: the day's **slot** (its kind: spine, quest, interlude or cutaway; the planned content; the beat or quest stage from the arc; any micro-choice it carries) and the day's **colour** (`warm` / `mild` / `cold` / `rest`), which is GM-only and never said to him.
- Ledger: the day's totals vs targets, sessions vs plan, anything open for tomorrow, flags. **While a story choice is open, the reply ends with** "Still waiting on Darrow: 1 … / 2 … / 3 …".
- **The open micro-choice:** it carries across one scene. If it is still open when this day closes, Darrow answers for himself with the slot's planned `default`: run `/choose` for that option with `--by bearing`, say so in one Ledger line, and fold the consequence into this scene's opening. If this day's slot carries a new micro-choice while one is still open, the open one resolves by default first. **The open climax choice:** it carries across the first two scenes of the next chapter (slot 1 may be written while it is open: it covers the Sunday and ends before the choice is felt); if it is still open at the second close, it resolves to the climax's planned `default` (`python3 engine/saga.py plan climax` prints it), recorded `by: "bearing"` through `/choose`, and its `### Choice` block is written then.
- Chronicle: read the last scene and `saga/state/_gm/threads.md`, then write that day's **scene** (CLAUDE.md "Closing a day"; `saga/bible/style.md`) in the slot's kind. The content is the slot's; the day's deeds set only the tone (warm or cold in him, a stage that goes well or costs more); the outcome waits for the climax. Fold in the DUE NOW / OVERDUE items from `saga.py now` that fit. Append it to the current chapter file.
- If the day was red-light (`rest`), the scene is a **cutaway**: another POV, or Darrow made to rest. No setback framing. A day with nothing logged at all (no `daily_log.csv`, `nutrition_log.csv` or `food_entries.csv` row; `show daily DATE`, `show nutrition DATE` and `food list DATE` all print nothing) is **missed**: never create a row, no scene; `python3 engine/saga.py plan done N --skipped`, and the next scene opens on the world move `plan next` (and `now`) prints as owed. A day with any row at all, even food alone, is open and gets its scene.
- Then the bookkeeping: `python3 engine/saga.py plan done N --wrote chNN:sK` (it refuses a slot already written or skipped; `--force` to redo one; if that was the quest's last stage, a slot marked `"last": true` or the arc's stage count reached marks the quest done by itself, otherwise `python3 engine/saga.py plan quest <id> status=done`) → `python3 engine/saga.py fire ID --where chNN:sK` for each due item you used (`void ID --why "…"` for one the story made impossible) → `python3 engine/saga.py plan micro open N` if the scene ended on the slot's micro-choice (written in the `style.md` format). Update `saga/state/world.json` by Edit (`scenes[]`, `location.place`, `last_beat`, `current_quest.on_the_page`, `current_struggle`; never approval), `saga/state/_gm/threads.md`, `codex.md`, and the narrative top of `saga/NOW.md`.
- **The cast and the site:** a file in `saga/characters/` for anyone new on the page (contract: `saga/characters/README.md`); update `last_seen`, `last_seen_doing`, `now`, `appearances`, `known_facts` (and `appearance`/`status` if changed) for everyone in the scene; `saga/state/places.json` for a new place; `world.json → location.place`. Then `python3 engine/saga.py check` and `python3 engine/build_site.py`: both must pass before you commit.

## 7. Save
`git add -A && git commit -m "log DATE: <short summary>" && git push origin HEAD:main` (the rebuilt `docs/` goes in the same commit).
If the push is rejected: `git pull --rebase origin main`, then push again.
