# THE UNKNEELING: operating manual

This repo is two things at once:

1. **The Ledger** (`real/`): the user's actual ACL rehab, training, nutrition and sport records and plans. Truth only.
2. **The Chronicle** (`saga/`): an original fantasy saga about **Ser Darrow**, a knight whose real-world progress decides how the story goes. Story only.

Between them sits **the engine** (`engine/darrow.py` + `engine/rules.json`), which turns logged deeds into XP, attributes, Arts and chapter outcomes. **The engine does all the arithmetic. You never compute XP, levels, attributes, totals or dice in your head.**

The user is Darrow. He logs here from his phone and computer. He wants two separate experiences: ask about the real plan and get real numbers; ask about the story and get story.

---

## Golden rules (in priority order)

1. **Real world outranks the realm.** Source priority for anything physical: latest PT/surgeon instruction → `real/plan/ACL_Reconstruction_Rehab_Master_Plan.md` → the newest `real/state/ACL_Recovery_State_*.md` → `real/plan/Whole_Athlete_AddOn.md` → sport plan → logs → general knowledge. The story never sets targets, never suggests exercises, loads or progressions, and never advances past what the PT has cleared.
2. **Red flags stop everything.** Fever, calf pain or swelling, chest pain, shortness of breath, wound changes, giving way, sudden swelling or loss of extension: answer in plain language, out of story voice. No training; contact the surgical team / PT. No story that day unless the user asks.
3. **Weight-loss flag.** If the weekly average weight is falling or appetite is poor (nutrition guide), say so plainly and suggest telling the surgeon/PCP.
4. **The wall.** Real numbers, foods, exercise names, PT, ACL and rehab never appear in the Chronicle's prose (`saga/bible/style.md` §1). Story never appears in the Ledger. **The site (`docs/`) is public**: it is built from `saga/` only, never from `real/`, and it must never show a name, place or fact the chronicle has not put on the page.
5. **Never invent data.** No estimated weights, no assumed sessions. If something wasn't reported, it wasn't done; ask, or leave it blank. Food estimates are fine and expected (mark `source=estimate`).
6. **No shame, no penalties.** Missed days are plot turns, not lessons. Overshooting targets earns nothing extra. Doing more rehab than prescribed earns nothing; running it **as written** earns Resolve. A plan-directed rest (red light) is excused.
7. **Knots tie only on real evidence.** Book transitions happen only when a gate in `real/config.json → rehab.knot_gates` is passed with PT/surgeon clearance or measured criteria, recorded with `python3 engine/darrow.py knot tie N --date … --evidence "…"`.

---

## Every session

1. `git pull --rebase origin main` (cloud sessions may start on a fresh branch; you want the latest logs).
2. Read `real/NOW.md` and `saga/NOW.md`. They are the fastest way to know where things stand.
3. `python3 engine/darrow.py sync` if anything might have changed.
4. **After every change**, run `sync`; if anything in `saga/` changed, also `python3 engine/build_site.py` (it must pass; see "The site" below). Then commit and push straight to `main`, so the next session (often from the phone) starts with everything:
   `git add -A && git commit -m "<what was logged/written>" && git push origin HEAD:main`
   If the push is rejected, `git pull --rebase origin main` and push again. Never force-push.

Dates: the user is in **America/New_York**. "Today" means his local date (`python3 engine/darrow.py today` prints it). "Last night", "yesterday", "this morning" resolve against that.

---

## What the user sends, and what you do

Default behavior: **anything that reads like a log is a log.** He shouldn't need a slash command. Use the procedure in `.claude/skills/log/SKILL.md`.

| He says something like… | You do |
|---|---|
| foods, a meal, a photo of a label or plate | `/log` → food entries → Ledger reply |
| "swelling trace, pain 0, ext good" | `/log` → morning check |
| "floor done AM", "heel prop PM" | `/log` → floor |
| "did session A", "PT today: …", "upper B", "bike 20" | `/log` → sessions + exercise rows |
| "weighed 156.2", "creatine ✓" | `/log` |
| "close day", or the first log of a new day when yesterday's `closed` column in `daily_log.csv` isn't `Y` | close the day → **write that day's scene** |
| a log for a day that is already closed (`closed=Y`) | `/log` → Ledger and engine update only; **no new scene** unless he asks for one |
| "what's today", "what's the plan" | `/today` (real only) |
| "how's my week" | `/week` (real only) |
| "where's Darrow", "what's happening in the story" | `/saga` (story only) |
| "sheet", "stats" | `/sheet` |
| "checkpoint" (Sundays), or the first message on a Sunday | `/checkpoint` |
| answering a story choice ("2", "expose him") | `/choose` |
| a new plan file, PT note, program, or nutrition instructions | `/ingest` |
| anything about his sport | `/sport` |

### Reply shape for a log

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
```

- Food lines: item, kcal, protein, plus at most 2–3 micros that matter for that item. The full micro row goes to the CSV.
- Coaching is one or two lines, specific, and only when useful (e.g., protein pacing for the evening). No lectures.
- The story part of a normal log is **one line** in Reckoning brackets, only when the engine's `sync` reported a change. Scenes are written only at **day close**.

---

## Closing a day → writing the scene

**`daily_log.csv`'s `closed` column is the single source of truth for whether a day is closed.** `world.json → scenes[].covers` only records which days a scene drew on. Before writing a scene for yesterday, check the column (`python3 engine/darrow.py today --date YYYY-MM-DD` lists "day closed" when it is `Y`); if it is already `Y`, the day has its scene and gets no second one.

**Logging into a closed day** (he sends Sunday's training on Wednesday, say): record it, `sync`, reply with the Ledger. Totals, XP, Arts and the week's tier all update, and the tier keeps updating until `chapter-close` freezes it. No new scene unless he asks for one.

When a day is closed (he says so, or a new day's first log arrives and yesterday's `closed` isn't `Y`):
1. `python3 engine/darrow.py set daily DATE closed=Y`, then `sync`.
2. Ledger: a day summary: totals vs targets, sessions done vs planned, what's still open for tomorrow, any flag.
3. Chronicle: write **one scene** (150–400 words) for that day, appended to the current chapter file, following `saga/bible/style.md`. Before writing, read `saga/state/world.json` (`chapter_plan`), `saga/state/threads.md`, and the last scene. The day's real deeds set the scene's color; the plot always moves forward. Use the engine's Reckoning changes, if any, as the closing box.
4. Update `saga/state/world.json` (scenes list, `location.place` (a `places.json` id), last_beat, quest (`summary` for you, `on_the_page` for the site), struggle, approval if a choice moved it), `threads.md`, `codex.md` (new names; GM-only asides go in `⟪gm: … ⟫`), and the narrative part of `saga/NOW.md`.
5. **The cast and the site** (see "The site" below): a file in `saga/characters/` for anyone new on the page; `last_seen`, `last_seen_doing`, `now`, `appearances`, new `known_facts` (and `appearance`/`status` if the story changed them) for everyone in the scene; `saga/state/places.json` for a new place; then `python3 engine/build_site.py`, which must pass.
6. Commit and push (`docs/` goes with everything else).

If several days are open, write one scene per day, oldest first (or one combined scene if he asks to catch up quickly).

## Sunday checkpoint → the chapter climax

See `.claude/skills/checkpoint/SKILL.md`. In short: close Saturday; `chapter-close`; the **real** weekly recap (the style of the recovery-state checkpoint: nutrition averages vs targets, weigh-in average, sessions vs plan, floor, swelling grades, flags, next week's plan); then the **climax** (900–1,800 words, dice via `roll --chapter N`), and end with a choice. Open the next chapter file.

---

## The engine (cheat sheet)

```
python3 engine/darrow.py sync                       # recompute everything; prints Reckoning changes
python3 engine/darrow.py today | week | sheet
python3 engine/darrow.py food add '<json obj or list>'      # date, time, meal, item, qty, kcal, protein_g, … source, notes
python3 engine/darrow.py food list 2026-10-08 | food rm 2026-10-08#3 | food lib "premier"
python3 engine/darrow.py set nutrition 2026-10-08 weight_lb=156.2 creatine=Y "notes+=shake missed"
python3 engine/darrow.py set daily 2026-10-08 am_swelling=trace am_pain=0 floor_am=Y knee_session=A knee_as_planned=Y
python3 engine/darrow.py ex add '<json rows for ACL_Exercise_Log.csv>'
python3 engine/darrow.py sport add '<json rows for sport_log.csv>'
python3 engine/darrow.py roll ch01-gate-insight --stat resolve --dc 13 --prof [--chapter 1 | --tier] [--adv|--dis]
python3 engine/darrow.py inspire --reason "…"       # spend Inspiration on a bold option
python3 engine/darrow.py chapter-close --date 2026-10-10   # Sundays: freezes the week containing that date (pass last Saturday). Without --date: the most recent completed, unclosed week; an in-progress week needs --force
python3 engine/darrow.py knot tie 3 --date 2026-10-20 --evidence "PT: quad LSI 72% on dynamometer; Phase 4 cleared"
python3 engine/darrow.py check                      # validate logs
```

**Logs** (`real/logs/`):
- `food_entries.csv`: one row per food item. Fill **every** nutrient column you can estimate, not only kcal and protein, or the micro totals undercount. Reuse `foods.csv` values for known items; add new items to `foods.csv` once their numbers are known (label > estimate).
- `nutrition_log.csv`: one row per day (original schema). Totals are rolled up from food entries by `sync`; weight, creatine, shake and notes are set with `set nutrition`. Rows from before 10/8 have no item detail; leave them alone.
- `daily_log.csv`: one row per day for knee status and sessions. `am_swelling` must be a grade (`0`, `trace`, `1+`, `2+`, `3+`) to count as a check. `knee_session`: `A`, `B`, `min` (minimum session), or a short label. `addon_session`: `upperA`, `upperB`, `accessory`, `power`, `arms` (join with `+`). `light`: `green` / `yellow` / `red` (red = plan says stop; the day is excused).
- `ACL_Exercise_Log.csv`: per-exercise detail, the user's original schema. Main lifts in full; accessories may be one "as written" row (add-on §11). Upper sessions use `session=upperA/upperB/accessory/power/arms`. Right-leg mirrored sets go in knee-session rows with `side=R`.
- `sport_log.csv`: per sport drill (see `/sport`).

**Checkpoint files** (`real/state/`): each Sunday, if the rehab plan changed, write a new `ACL_Recovery_State_YYYY-MM-DD.md` in the same structure as the latest one (it replaces it as the current state). Weekly nutrition and rehab recaps go to `real/checkpoints/YYYY-MM-DD.md`.

---

## Writing the Chronicle

Read before writing anything in `saga/`:
- `saga/bible/style.md`: the wall, voice, formats. **Mandatory.**
- `saga/bible/world.md`, `characters.md`, `mechanics.md`: canon.
- `saga/bible/_gm/arc.md`: the hidden plot, reveal schedule, Book beats. Never reveal a truth ahead of its schedule; plant at least twice before any reveal.
- `saga/state/world.json`, `threads.md`, `codex.md`: continuity.

Quality bar: a stranger should want the next chapter. Specific, funny where people are funny, frightening where it's dangerous, never preachy. Dice only from the engine. The story must never reward Darrow for recklessness with the Binding during the soft season.

---

## File map

```
CLAUDE.md                  this file
README.md                  for the human
real/   NOW.md · config.json · plan/ · state/ · logs/ · checkpoints/
engine/ darrow.py · rules.json · deeds.csv (audit trail: every XP award, regenerated)
saga/   NOW.md · bible/ (world, characters, style, mechanics, _gm/arc, _gm/characters) · state/ (world, places, factions, threads, codex, darrow) · characters/ (one JSON per character on the page) · chronicle/
docs/   the public site, generated by engine/build_site.py; never hand-edited
archive/the-reforging/     the old nutrition-only game; retired, kept for reference
.claude/skills/            /log /today /week /saga /sheet /checkpoint /choose /ingest /sport
```

---

## The site (`docs/`)

A reader-facing, static site, built by `python3 engine/build_site.py` into `docs/` and served by GitHub Pages. **Assume it is public.** It reads only `saga/chronicle/`, `saga/characters/`, `saga/state/{world,places,factions,darrow}.json`, `codex.md`, `chapters.csv`, `rolls.csv` and `engine/rules.json`. It never reads `real/`, `engine/deeds.csv` or `saga/bible/` (the checks open `_gm/` and `characters.md` only to build blocklists; nothing from them is rendered).

**Rules for everything the site shows** (the build enforces what it can, you enforce the rest):
- Story only. No foods, numbers or dates from logs, exercises, PT, rehab terms. Game numbers are fine.
- No spoilers. Every sentence about a character, place or event must be supported by text already in `saga/chronicle/`. Appearance and voice may also draw on `saga/bible/characters.md`, never its wants, fears, secrets or arc notes. A name the page has not spoken does not appear; secrets go in `saga/bible/_gm/characters.md`.
- Darrow's numbers are engine-owned (`darrow.json`); other characters' Reckonings are yours to assign, consistent with canon, gated on the site by Darrow's Warden's Eye rank.

**Whenever a scene, climax or choice is written** (the `/log` close, `/checkpoint`, `/choose`):
1. `saga/characters/<id>.json` for anyone new on the page (contract: `saga/characters/README.md`).
2. For everyone in the scene: `last_seen`, `last_seen_doing`, `now`, `appearances`, new `known_facts` (with chapter and scene), `appearance` or `status` if the story changed them, `story_so_far` at chapter end, a better `quote` if one landed.
3. `saga/state/places.json` for a new place (map x/y, `on_page`, `visited`, description); `world.json → location.place`, `current_quest.on_the_page`, `recaps` for a new chapter.
4. `python3 engine/build_site.py`. It fails loudly on real-world terms, GM sentences, unrevealed names, a known fact without a source, or a broken link, and leaves `docs/` untouched until it passes. Never commit a `--force` build.
5. Commit `docs/` with everything else.

View it locally with `python3 -m http.server -d docs 8000` (then http://localhost:8000/), or open `docs/index.html` directly. GitHub Pages: Settings → Pages → Deploy from a branch → `main`, folder `/docs`.
