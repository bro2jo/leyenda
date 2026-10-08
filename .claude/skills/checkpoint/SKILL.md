---
name: checkpoint
description: Sunday weekly checkpoint — real-world weekly recap (nutrition, weight trend, rehab sessions vs plan, gates, next week's plan) and the chapter's climax in the story (dice, outcome by the week's tier, a choice). Use when the user says checkpoint, or on his first message of a Sunday.
argument-hint: "[optional: the Sunday date]"
allowed-tools: Bash(python3 engine/darrow.py *) Bash(git *) Read Edit Write
---

# /checkpoint: the week closes, the chapter climaxes

Do the Ledger fully before writing any story.

## A. Close out the week
1. `git pull --rebase origin main`.
2. If Saturday (or any earlier day this week) isn't closed, close it now (the `/log` close procedure, including its scene).
3. `python3 engine/darrow.py chapter-close`. This freezes last week's score and tier as `chapter N` and prints the breakdown. Note **N** and the **tier**.
4. `python3 engine/darrow.py week --date <last Saturday>` for the table.

## B. The Ledger recap (real only)
Write `real/checkpoints/<Sunday>.md` and give him a ≤15-line summary in chat:
- **Nutrition:** average kcal, protein, carbs, fat, fiber vs targets; days at target; micros averaging below the reference in `nutrition_guide.md`; sodium, sat fat and sugar well above; fish count. Use `nutrition_log.csv`.
- **Weight:** weekly average (needs ≥3 morning readings), change vs last week, and the guide's rule (after ~2 consistent weeks: losing/flat → +150–250 kcal; gaining 0.25–0.75 lb/wk → hold; >1 lb/wk → −150–200). If the target changes, update `real/config.json → nutrition_targets` with the source and date.
- **Rehab:** loaded days and next-morning responses; floor X/7; swelling graded X/7 and the trend; sessions vs plan; progressions made and whether they followed the one-change rule; PT notes this week.
- **Add-on:** upper sessions 2 of 2? (decides block advancement, add-on §6); bike X of 3; accessory/power.
- **Gates:** status of the next phase gate (`real/config.json → rehab.next_gate`), with evidence. **If a gate was passed with PT/surgeon clearance or measured criteria this week:** `python3 engine/darrow.py knot tie N --date … --evidence "…"`, update `rehab.current_phase` / `phase_entered` / `next_gate`, and run `sync`.
- **Next week:** the plan, day by day, with doses. If the program changed, write a new `real/state/ACL_Recovery_State_<Sunday>.md` in the same structure as the previous one.
- Update the top section of `real/NOW.md` for the new week.

## C. The climax (story only)
Read `saga/bible/style.md`, `saga/bible/_gm/arc.md` (current Book), `saga/state/world.json` (`chapter_plan.climax`), `threads.md`, and the chapter so far.

**The tier sets the shape of the outcome:**
- **Triumph:** Darrow's plan works; a clean win, plus something extra (an ally, a secret, an item).
- **Hard-won:** he wins, and it costs something real (an injury in-story, a relationship strained, a resource lost).
- **Costly:** partial: he gets one thing he wanted and loses another.
- **Setback:** the enemy gains ground. Darrow survives, and the reversal sets up the next chapter. Never humiliating, never a lecture.

**The dice decide the details.** 2–4 checks at the moments of real stakes:
`python3 engine/darrow.py roll ch<NN>-<slug> --stat <might|vigor|finesse|resolve> --dc <8–20> --prof --chapter <N>`
(`--prof` when an Art or trained skill applies; `--adv` when an Art grants advantage; `--dis` when the situation is against him.) Write each roll on its own line exactly as returned, then narrate the result. If he has Inspiration and a roll fails at a key moment, you may offer the reroll as part of the choice rather than spending it yourself.

Write **900–1,800 words** under `## Climax — <Title>` in the current chapter file. End with **the choice** (2–3 options, gated options marked per `style.md`).

## D. Turn the page
1. Create the next chapter file `saga/chronicle/<NN+1>-<slug>.md` with its heading and an epigraph. If a Knot tied this week, it's the **transition chapter** into the next Book (see `arc.md`).
2. Update `saga/state/world.json`: chapter number/title/file, `chapter_plan` for the new chapter (from `arc.md` core beats first, then expandable beats if the gate is still far off), `core_beats`, scenes reset, `last_beat`, quest, struggle.
3. Update `threads.md` (plants and payoffs), `codex.md`, and the narrative top of `saga/NOW.md` (the open choice goes there).
4. `python3 engine/darrow.py sync`, then `git add -A && git commit -m "checkpoint <Sunday>: chapter N <tier>" && git push origin HEAD:main`.
