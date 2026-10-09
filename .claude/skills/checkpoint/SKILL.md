---
name: checkpoint
description: Sunday weekly checkpoint — real-world weekly recap (nutrition, weight trend, rehab sessions vs plan, gates, next week's plan) and the chapter's climax in the story (dice, outcome by the week's tier, a choice). Use when the user says checkpoint, or on his first message of a Sunday.
argument-hint: "[optional: the Sunday date]"
allowed-tools: Bash(python3 engine/darrow.py *) Bash(python3 engine/saga.py *) Bash(python3 engine/build_site.py *) Bash(git *) Read Edit Write
---

# /checkpoint: the week closes, the chapter climaxes

Do the Ledger fully before writing any story.

## A. Close out the week
1. `git pull --rebase origin main`.
2. If Saturday (or any earlier day this week) isn't closed, close it now (the `/log` close procedure, including its scene). A Saturday with no row at all is missed: `python3 engine/saga.py plan done N --skipped`; its spine content folds into the climax.
3. `python3 engine/darrow.py chapter-close --date <last Saturday>` (always pass the Saturday that just ended, e.g. `--date 2026-10-10`). This freezes that week's score and tier as `chapter N` and prints the breakdown. Note **N** and the **tier**. Without `--date` the engine picks the most recent completed week that isn't closed yet and refuses a week still in progress unless `--force` is given; `--force` is also needed to redo a closed week.
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
Read `saga/bible/style.md`, `python3 engine/saga.py now` (**read the RULE ARMED / near lines and any DUE NOW or OVERDUE item before writing**; `saga.py due --at chNN:climax` for the full list), `python3 engine/saga.py arc <the chapter's beat id>` (its per-tier climax sketch), `saga/state/_gm/plan.json → chapter.climax` (plan, checks, options), `saga/state/_gm/threads.md`, and the chapter so far. Then `python3 engine/saga.py plan set stage=climax`.

**Roads.** The tier also scores the Book's road (`python3 engine/saga.py route show`: Triumph +1, Setback −1; the road is decided only at the Knot). Write the climax so that it answers the chapter's **question** (`plan.json → chapter.question`) in the tier's shape.

**The tier sets the shape of the outcome:**
- **Triumph:** Darrow's plan works; a clean win, plus something extra (an ally, a secret, an item).
- **Hard-won:** he wins, and it costs something real (an injury in-story, a relationship strained, a resource lost).
- **Costly:** partial: he gets one thing he wanted and loses another.
- **Setback:** the enemy gains ground. Darrow survives, and the reversal sets up the next chapter. Never humiliating, never a lecture.

**The dice decide the details.** 2–4 checks at the moments of real stakes:
`python3 engine/darrow.py roll ch<NN>-<slug> --stat <might|vigor|finesse|resolve> --dc <8–20> --prof --chapter <N>`
(`--prof` when an Art or trained skill applies; `--adv` when an Art grants advantage; `--dis` when the situation is against him.) The engine prints the chapter's dice line first, in the style guide's form (`` `[MIGHT · DC 13]` d20 **14** +2 = **16** — *Success* ``); paste that first line into the chapter exactly as printed, on its own line, then narrate the result. The second line is only a note for you. If he has Inspiration and a roll fails at a key moment, you may offer the reroll as part of the choice rather than spending it yourself.

Write **900–1,800 words** under `## Climax — <Title>` in the current chapter file. Fire what you paid off (`python3 engine/saga.py fire ID --where chNN:climax`; `void` what the climax made impossible). End with **the choice** (2–3 options from the climax plan, gated options marked per `style.md`, stat gates and Bearing gates alike); the open choice goes in `saga/NOW.md`. When he answers, `/choose` records it.

**If a Knot tied this week** (`darrow.py knot tie` ran in step B): the chapter is the Book's transition. `python3 engine/saga.py route decide --book N` (it refuses while a listed chapter is unclosed, unless `--road … --why …`), then `python3 engine/saga.py arc tN.<road>` and write the climax in that shape (in all three the Knot ties and nobody is humiliated; only the circumstances, company and carry-forward differ). Afterwards `python3 engine/saga.py plan beat tN status=done`; core beats still `planned` fold into it in order.

## D. Turn the page
1. Create the next chapter file `saga/chronicle/<NN+1>-<slug>.md` with its heading and an epigraph. If a Knot tied this week, the new chapter opens the next Book (`# BOOK N — <TITLE>` title line; `python3 engine/saga.py arc bookN.question`).
2. **Plan the chapter:** `python3 engine/saga.py plan chapter open --number <N+1> '<json>'` (shape in `saga/bible/_gm/design.md` §5.3–5.4): a one-line `question`; 7 slots Sun–Sat with `kind` (≥ 2 `spine`, Saturday always spine, ≤ 1 `interlude`, two quest slots marked `float: true`), each with its `beat` or `quest`+`stage` and a one-line `plan` from `saga.py arc <id>`; micro-choices in non-adjacent slots touching ≥ 2 axes, each with its `default`; `world_moves[]`; the `climax` plan with `checks` and `options`. `required` quests first; never more than two quests live; the chapter touches ≥ 1 open thread. The choice he just made bends these slots.
3. Update `saga/state/world.json` by Edit: chapter number/title/file, `scenes` reset, `last_beat`, `current_quest`, `current_struggle`, a `recaps` line (never approval). Then `saga/state/_gm/threads.md` (plants and payoffs), `codex.md`, and the narrative top of `saga/NOW.md` (the open choice goes there).
4. **The cast and the site:** files in `saga/characters/` for anyone new on the page in the climax (contract: `saga/characters/README.md`); for everyone in it, `last_seen`, `last_seen_doing`, `now`, `appearances`, `known_facts`, `status` if someone fell or was taken, and `story_so_far` for the chapter just closed; `saga/state/places.json` for new places; `world.json → location.place`, `current_quest.on_the_page`, and a one-line spoiler-free `recaps["<new chapter slug>"]`. A tied Knot shows up on the site by itself.
5. `python3 engine/darrow.py sync`, `python3 engine/saga.py check` and `python3 engine/build_site.py` (both must pass), then `git add -A && git commit -m "checkpoint <Sunday>: chapter N <tier>" && git push origin HEAD:main`.
