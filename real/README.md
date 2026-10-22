# real/ — the Ledger

The real-world side of this repo: his ACL rehab, training, nutrition and sport, as plans and as logs. Truth only; nothing from the story. `CLAUDE.md` is the operating manual. This file is the map: what each file is for, where each fact lives, how things get updated, and how files are named. How it came to be laid out (and the old file names): `CHANGELOG.md`.

**One home per fact.** Each fact is written in one file; other files point to it rather than copy it. `NOW.md`'s top is the one exception: a short page of what stands this week, pointing at the State for detail.

---

## Start here

1. `NOW.md`: what stands this week. Read every session.
2. `python3 engine/darrow.py today` / `week`: the day and the week, from the logs.
3. Then only the section a question needs: `python3 engine/darrow.py doc <name> <section>` (no section: the outline). The logs are read through the engine (`show <log> DATE`, `food list DATE`, `measures`, `recap`), never raw.

```
real/
  README.md        this map
  NOW.md           what stands this week; the engine's counts in a block at the bottom
  trends.html      the trends page (Trends and Days views), one standalone file for the phone, built from the logs by engine/report.py when he asks for it
  CHANGELOG.md     how real/ came to be laid out; old names → new
  config.json      the engine's settings: targets, the weekly template, plan changes, daily minimum, phase and gates, sport stage
  projects.json    the works: the week's real goal outside the knee and its tasks (darrow.py project); finished and set-aside ones kept
  plan/            the documents: rules and designs this repo keeps, and reference documents it never edits
  state/           recovery_state.md, the current program; archive/ keeps the one each Sunday replaced
  visits/          pt_notes.md, every PT and surgeon note; a dated file for anyone else's instruction
  checkpoints/     one review per week, named for the Sunday after it
  logs/            the CSVs; archive/ holds imported originals, never written
```

---

## The files

| File | `doc` | What it is | Changes | Belongs here | Doesn't belong here |
|---|---|---|---|---|---|
| `visits/pt_notes.md` | `ptnotes <date>` | Every PT and surgeon note, word for word, plus relayed verbal instructions and later clarifications. **Top-priority source** | Append only, the same day | The note word for word · his account · a short reading | Next-visit lists, program changes, booking status (→ State) |
| `plan/rehab_master_plan.md` | `master` | The rehab protocol: phases, exit criteria, doses, pain and swelling rules, red flags | **Reference:** never edited here; a new version replaces it whole | — | — |
| `state/recovery_state.md` | `state` | **The current program**: fixed facts and equipment (§1), phase and gates (§3), PT instructions in force and the next-visit list (§5), this week and the sessions with doses and ladders (§6), add-on status (§7), patterns (§9), milestones (§10). §2, §4 and §8 point to the logs and the checkpoint | Reviewed every Sunday; replaced when the program changes (the old one to `state/archive/`); mid-week only on request | Anything current about the program | History: readings, measurements, the week in review |
| `plan/working_rules.md` | `rules` | How the rehab runs: definitions, load and pain rules, clearance, red flags, check-in questions, the weekly rhythm's **structure**, the Sunday checkpoint, the log columns | Only when a rule changes | Rules and definitions that hold for weeks | Dates, doses, counts, statuses, this week |
| `plan/whole_athlete_addon.md` | `addon` | The **design** of everything around the knee: upper sessions and blocks, warm-up, tissue/trunk finisher, posture work, the right leg, conditioning stages, how the off-season program comes back, sport settings | Only when the design changes | Session templates, block structure, add-on rules, the phase map | Which days it ran, loads, block dates (→ State §7) |
| `plan/offseason_program_24_week.md` | `offseason` | The healthy-athlete 24-week off-season program (v4) for speed, cutting and jumping sports; the Add-On's source, gated by the rehab plan (Add-On §8) | **Reference:** never edited here; a new version replaces it whole | — | — |
| `plan/sport_plan.md` | `sport` | The disc-throwing plan (ultimate, handler): skills (the `sport_log.csv` ids), what each rehab phase allows (Phase 3 seated or planted at easy effort; slight pivots from Phase 4, the step-out with the PT's OK; max intent from Phase 5), the week (three sessions on days without a knee session, film), logging, reviews | Only when the sport plan changes (`/sport`) | Throwing skills, stages by phase, weekly placement | Anything that loads the left knee ahead of the rehab plan's phase |
| `plan/ultimate_offseason_guide.md` | `sportguide` | The guide the sport plan runs on, as written (Oct 2026 → late spring 2027): the content of every session and week | **Reference:** never edited here; a new version replaces it whole, then `sport_plan.md` is reviewed against it | — | — |
| `plan/nutrition_guide.md` | `guide` | Calories, protein, micronutrient reference values, the weight rule | **Reference:** never edited here; a new version replaces it whole | — | — |
| `NOW.md` | `now` | What stands this week: plan in force, next PT visit, the gate, flags, open items; the engine's block of counts | Its top whenever something stands or changes; the block on every `sync` | Short pointers and what changed since the State | Doses and tables (→ State), history (→ checkpoints) |
| `trends.html` | — | **The trends page**, one standalone file (open it on the phone): the streaks, the engine's week score by week, a calendar of the daily habits, sessions against the plan, the knee's mornings, weight, calories and protein, the latest measurements; a range control scopes every chart, and each chart has a table. Its Days view: the month as a grid of what each day carried (one colour and place per kind: knee, upper, conditioning, sport, PT, sauna, Game Ready, light therapy) and the selected day's card with everything logged (the habits, sessions with minutes and effort, exercises, throwing, food items, adjuncts, notes) | On request: `python3 engine/report.py` when he asks for the trends (`ship` does not run it; the footer says when it was built, and the next `ship` commits that build); never edited by hand | — | Anything typed in: it shows the logs only |
| `config.json` | — | What the engine needs: nutrition targets, the weekly template the week is scored on, plan changes by date, daily-minimum rounds, phase and gates, sport stage | When a target, the template or a phase changes | Values with their `source` | Prose |
| `projects.json` | `project show` | The works: one real goal at a time outside the knee, in 2–5 tasks, with the day each task was reported done; finished and set-aside projects kept, for the count | `darrow.py project open|done|drop` (`/project`) | The goal and its tasks in his words, the dates | Anything of the story: the tale a project pays for is the Chronicle's (`saga/chronicle/tales/`) |
| `checkpoints/<Sunday>.md` | `checkpoint` (newest) | The week in review (Sun–Sat), named for the Sunday after it; its numbers block is the engine's | Written at the checkpoint; then an archive | The week's numbers and their meaning | The current program |
| `visits/<date>_<who>_<kind>.md` | — | An instruction from anyone but the PT or surgeon (a trainer's), one file each | Once, the day it comes | What was said and what it changed | PT or surgeon notes (→ `pt_notes.md`) |
| `logs/daily_log.csv` | `show daily` | One row per day: morning check, daily minimum, sessions with minutes and RPE, pain, time on feet | As he reports (`/log`) | The columns (Working Rules → Log files); `am_swelling` the grade only | Decisions, instructions, plans |
| `logs/exercise_log.csv` | `show ex` | One row per exercise instance | As he reports | Exercise, block, side, sets, reps, hold, load, assist | — |
| `logs/nutrition_log.csv` · `food_entries.csv` · `food_library.csv` | `show nutrition` · `food list` · `food lib` | Day totals with weight and creatine · one row per food item · the food library | As he reports | — | — |
| `logs/sport_log.csv` | `show sport` | One row per skill worked in a throwing or film session | As he reports | — | — |
| `logs/measurements.csv` | `measures` | Every measured number, one row per side (goniometer, dynamometer, 1RM, hop tests later) | Each visit or test | The number, its source and method | Daily self-checks (→ daily log) |
| `state/archive/`, `logs/archive/` | — | History: each replaced State; the old dashboard's daily log as uploaded (column map: its README) | Never (path corrections aside) | History | Anything current |

---

## Where each fact lives

| Fact | Home |
|---|---|
| What the PT or surgeon said | `pt_notes.md` (the State quotes the ones in force) |
| What they measured | `measurements.csv` (`measures`); the words around it in `pt_notes.md` |
| Phase criteria, plan doses | Master plan |
| Definitions, load and pain rules, clearance, the log columns | Working Rules |
| Phase and gate status | State §3 (NOW → Gate keeps it short) |
| Daily readings: swelling grade and trend, pain, extension, flexion, catch, wellness | `daily_log.csv` |
| Body mass | `nutrition_log.csv` (the baseline: State §1) |
| PT-introduced items, the next-visit list, PT booking | State §1 and §5 (NOW adds only what came in since) |
| Weekly rhythm | Structure → Working Rules; this week's days → State §6; what the engine scores → `config.json → weekly_template` and `plan_changes` |
| Daily minimum | What it means → Working Rules; dose → State §6; rounds that make it full → `config.json → daily_minimum` |
| Doses, ladders, session tables, equipment substitutes, depths and heights | State §6 (home equipment: State §1) |
| Upper session design, warm-up, blocks, finisher, posture work, sport settings | Add-On |
| Conditioning | The Phase 3 rule → Working Rules; later stages → Add-On §5; the current ladder → State §6 |
| Upper status: sessions run, block, unlocks | State §7 |
| Throwing: what's allowed now, the week's throwing days | Sport plan; what the knee allows and where throwing sits in the week: Add-On §3 (this week's days also in State §6) |
| Nutrition targets | `config.json → nutrition_targets` (from the nutrition guide) |
| The week's work (a goal outside the knee) and its tasks | `projects.json` (`project show`); only its count reaches the sheet |
| Patterns and tendencies | State §9 |
| The week in review | `checkpoints/<Sunday>.md` |
| Exercise and day data | The logs |

---

## How things get updated

- **A log** (food, the morning check, a session, the bike, throwing): written as he sends it (`/log`), every session with minutes and RPE.
- **A PT or surgeon visit:** a new entry at the bottom of `pt_notes.md` the same day (the note word for word, his account, a short reading); numbers to `measurements.csv`; exercises to `exercise_log.csv` (`session=PT`); `daily_log` `pt=Y`; NOW's top says what it changed. It outranks the State until the checkpoint folds it in.
- **A decision mid-week** (moving a session, a new dose): NOW's top, and for a moved session `config.json → plan_changes`. The State takes it at the checkpoint, or mid-week when he asks.
- **Sunday checkpoint** (`/checkpoint`): the week's review into `checkpoints/<Sunday>.md`; the State reviewed (replaced when the program changed, else its "Last reviewed" line); NOW's top for the new week; the Working Rules or the Add-On only if a rule or the design changed.
- **Every change** ends with `python3 engine/darrow.py ship -m "…"`: checks, sync, the site build, one commit, pushed to `main`.
- **A new document** (`/ingest`): into `plan/` under these naming rules, with a row in this file and a `doc` name in `engine/darrow.py` if it will be read often.

---

## Naming rules

- **lowercase snake_case** for every file and folder, and no prefix the folder already says (no `ACL_`). Prose is `.md`, logs `.csv`, settings `.json`.
- **UPPERCASE** only for the entry files: `README.md`, `NOW.md`, `CHANGELOG.md`.
- **Current files keep one name** (`state/recovery_state.md`, `visits/pt_notes.md`, `plan/*.md`); a document's version and date live in its title, not its file name.
- **Dates are ISO** (`2026-10-11`). A file that is one event starts with its date (`checkpoints/2026-10-11.md`, `visits/2026-10-10_trainer_instruction.md`); an archived version ends with it (`state/archive/recovery_state_2026-10-04.md`).
- **A new file** gets a row here. **A renamed or moved file** gets a line in `CHANGELOG.md`, and every reference follows it (`grep -rn '<old name>' --exclude-dir=docs .`).
- **Archives are history:** never current, never edited beyond correcting a path.

**Habits that keep it clean:** end every session report with minutes and RPE · one swelling grade every morning, plus stiffness, catch and wellness · decisions go to NOW and the State, never into a log's `notes`.
