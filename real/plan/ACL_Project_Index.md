# ACL Project Index

What each file in `real/` is for, where each fact lives, and how the files get updated. Written Sat 2026-10-10; audited Mon 2026-10-12; rewritten for this repo Mon 2026-10-12, when the old dashboard project was retired and everything moved here. `CLAUDE.md` is the operating manual; this file is the map of the Ledger.

**Principle: one home per fact.** Each fact is written in one file. Other files may point to it, but they don't copy it.
- `real/NOW.md`'s top is the exception: a short page of what stands this week, pointing at the State for detail.

---

## Reading order

Every session starts with `CLAUDE.md` → "Every session" (`real/NOW.md`, `python3 engine/darrow.py today`). When a question needs the plan, read a section at a time (`python3 engine/darrow.py doc <name> <section>`):

1. This index (`doc index`)
2. `ACL_Working_Rules.md` (`doc rules`)
3. The current `ACL_Recovery_State_<Sunday>.md` (`doc state`)
4. `ACL_PT_Notes.md` (`doc ptnotes <date>`)
5. `ACL_Whole_Athlete_AddOn.md` (`doc addon`)
6. The logs, through the engine (`today`, `week`, `show <log> DATE`, `measures`, `recap`), never read raw
7. `ACL_Reconstruction_Rehab_Master_Plan.md` for phase criteria (`doc master`)
8. `24-week-offseason-program-v4.md` only when the add-on or a later phase needs it (`doc offseason`)
9. `sport/sport_plan.md` when a throwing day or the sport comes up (`doc sport`)

---

## The files

| # | File | What it is | Changes | Belongs here | Doesn't belong here |
|---|---|---|---|---|---|
| 1 | `plan/ACL_Reconstruction_Rehab_Master_Plan.md` | The rehab protocol: phases, exit criteria, doses, pain/swelling rules, red flags | **Never edited** | — | — |
| 2 | `plan/24-week-offseason-program-v4.md` | The healthy-athlete off-season program for speed, cutting and jumping sports; the source for the Add-On. Comes back in stages, gated by the rehab plan (Add-On §8) | **Never edited** | — | — |
| 3 | `visits/ACL_PT_Notes.md` | Every PT and surgeon note, word for word, plus patient-reported verbal instructions and later clarifications of a visit. **Top-priority source** | Append only, the same day | The note word for word · the patient's account · a short reading | Next-visit lists, program changes, plans, booking status (→ State) |
| 4 | `plan/ACL_Working_Rules.md` | How the rehab runs: definitions, load and pain rules, clearance, red flags, check-in questions, the weekly rhythm's **structure**, the checkpoint, the log columns | Only when a rule changes | Rules and definitions that hold for weeks | Dates, doses, counts, statuses, this week's schedule, measurements, patterns |
| 5 | `plan/ACL_Whole_Athlete_AddOn.md` | The **design** of everything around the knee: upper sessions and blocks, the warm-up (including the doorway pec sequence), the tissue/trunk finisher, posture work, the right leg, conditioning stages, the off-season mapping and sport settings | Only when the design changes | Session templates, block structure, add-on rules, the phase map | Which days it ran, this week's days, loads, block dates, PT questions (→ State) |
| 6 | `state/ACL_Recovery_State_<Sunday>.md` | **The single source for the current program**: phase and gates, PT instructions in force and the next-visit list, the program with doses and ladders, this week's days, add-on status, patterns, milestones. Sections 2, 4 and 8 point to the logs and the checkpoint | Reviewed every Sunday at the checkpoint (a new file when the program changed); revised in place mid-week only on request | Anything current about the program | History: readings, measurements, the week in review (→ logs, checkpoints) |
| 7 | `plan/sport/sport_plan.md` (its content: `Ultimate_Offseason_Development_Guide.md`) | The disc-throwing plan (ultimate, handler): skills, what each rehab phase allows (Phase 3: seated or square-stance at easy effort, no pivot; the left-foot pivot from Phase 4; max intent from Phase 5), three sessions a week (Wed A, Fri B, Sat C) plus film | Only when the sport plan changes (`/sport`) | Throwing skills, stages by phase, weekly placement | Anything that loads the left knee ahead of the rehab plan's phase |
| 8 | `plan/nutrition_guide.md` | Calorie, protein and micronutrient guidance; the weight rule | When the guide changes | Targets' reasoning, the reference values | Daily intake (→ food log) |
| 9 | `NOW.md` | What stands this week: plan in force, next PT visit, the gate, flags, open items; the engine's block of this week's counts at the bottom | Its top whenever something stands or changes; the block on every `sync` | Short pointers and what changed since the State | Doses and tables (→ State), history (→ checkpoints) |
| 10 | `config.json` | What the engine needs: targets, the weekly template the week is scored on, plan changes by date, daily-minimum rounds, phase and gates, sport stage | When a target, the template or a phase changes | Values with their `source` | Prose |
| 11 | `checkpoints/<Sunday>.md` | The week in review (Sun–Sat), one per week, named for the Sunday after | Written at the checkpoint; then an archive | The week's numbers (engine) and their meaning | The current program |
| 12 | `visits/<date>_<who>-<kind>.md` | An instruction that isn't from the PT or surgeon (a trainer's), one file each | Once, the day it comes | What was said and what it changed | PT or surgeon notes (→ PT Notes) |
| 13 | `logs/daily_log.csv` | One row per day: morning check, the daily minimum, sessions, minutes, RPE, pain, time on feet | As he reports (`/log`) | The columns (Working Rules → Log files). `am_swelling` = the grade only | Decisions, instructions, plans |
| 14 | `logs/ACL_Exercise_Log.csv` | One row per exercise instance | As he reports (`/log`) | Exercise, block, side (L / R / bil; blank for upper and conditioning), sets, reps, hold, load, assist. Single-leg work on both legs = one row per side | — |
| 15 | `logs/nutrition_log.csv` · `food_entries.csv` · `foods.csv` | Day totals, weight and creatine · one row per food item · the food library | As he reports (`/log`) | — | — |
| 16 | `logs/sport_log.csv` | One row per skill worked in a throwing or film session | As he reports (`/log`) | — | — |
| 17 | `logs/measurements.csv` | Every measured number, one row per side (goniometer, dynamometer, 1RM, hop tests later) | Each visit or test | The number, its source and method | Daily self-checks (→ daily log) |
| 18 | `logs/archive/` | The old dashboard's daily log, kept as uploaded (column map: its README) | Never | History | — |

---

## Where each fact lives

| Fact | Home |
|---|---|
| What the PT or surgeon said | PT Notes (the State quotes the ones in force) |
| What they measured | `measurements.csv` (`measures`); the words around it in PT Notes |
| Phase criteria, plan doses | Master plan |
| Definitions, load and pain rules, clearance, the log columns | Working Rules |
| Phase and gate status | State §3 (NOW → Gate keeps it short) |
| Daily readings: swelling grade and trend, pain, extension, flexion, catch, wellness | `daily_log.csv` |
| Body mass | `nutrition_log.csv` (the baseline: State §1) |
| PT-introduced items, the next-visit list, PT booking status | State §1 and §5 (NOW adds only what came in since) |
| Weekly rhythm | Structure → Working Rules; this week's days → State §6; what the engine scores → `config.json → weekly_template` and `plan_changes` |
| Daily minimum | What it means → Working Rules; dose → State §6; rounds that make it full → `config.json → daily_minimum` |
| Current doses, ladders, session tables, equipment substitutes, depths and heights | State §6 (home equipment in State §1) |
| Upper session design, warm-up, block structure, finisher, posture work, sport settings | Add-On |
| Conditioning | The Phase 3 rule → Working Rules; the stages after it → Add-On §5; the current ladder → State §6 |
| Upper status: sessions run, block, unlocks | State §7 |
| Throwing: what's allowed now, the week's throwing days | Sport plan (this week's days also in State §6) |
| Nutrition targets | `config.json → nutrition_targets` (from the nutrition guide) |
| Patterns and tendencies | State §9 |
| The week in review | `checkpoints/<Sunday>.md` |
| Exercise and day data | The logs |

---

## How things get updated

- **A log** (food, the morning check, a session, the bike, throwing): written as he sends it (`/log`), with minutes and RPE for every session.
- **A PT visit:** the note goes into PT Notes word for word the same day (his account and a short reading after it); numbers to `measurements.csv`; exercises to the exercise log (`session=PT`); `daily_log` `pt=Y`; NOW's top says what it changed. It outranks the State until the checkpoint folds it in.
- **A decision mid-week** (moving a session, a new dose): NOW's top and, for a moved session, `config.json → plan_changes`. The State changes at the checkpoint, or mid-week when he asks.
- **Sunday checkpoint** (`/checkpoint`):
  - the week's review into `checkpoints/<Sunday>.md`
  - the State reviewed: a new file for that Sunday when the program changed (the old one to `state/archive/`), else its "Last reviewed" line and whatever status moved
  - NOW's top for the new week
  - the Working Rules or the Add-On only if a rule or the design changed
- **Mid-week checkpoint (on request):** the State revised in place under the week's Sunday name.

---

## History

### Audit 10/10 (in the old dashboard)

1. **Working Rules:** stripped to rules only. Moved to the State: swelling and goniometer history, PT items by date, daily-minimum dose, conditioning ladder, PT-item mapping, machine substitutes, clinic numbers, depths, and known tendencies (merged into State §9).
2. **Add-On:** design only. Moved to the State: rollout status, this week's days, loads, block dates, the PT question list. No separate prehab/posture plan: posture work is built into the Add-On (upper warm-up + knee-session cooldown). Sport recorded as ultimate + court + field.
3. **PT Notes:** the header states the entry format; next-visit lists now live only in State §5. Older entries unchanged.
4. **State:** rebuilt as the single home for current facts.
5. **Logs:** `swelling_am` normalized to the grade only, with descriptors moved to the trend column; new columns `conditioning_min` and `wellness_1to5`; exercise-log `side` normalized.

### Audit 10/12 (in the old dashboard)

1. **State:** revised in place for Mon 10/12: Session B verdict (clean) and its doses as the baseline; Session A fixed for Tuesday; the eyes-closed drill corrected to a wobble-board drill with a BOSU home version; Upper B's row chest-supported for session 2; PT not yet booked.
2. **PT Notes:** appended the 10/11 clarification that the 10/8 "WB" drill was on a wobble board.
3. **Add-On:** the doorway pec sequence replaces the 30 s stretch and moves ahead of the face pull; Upper B's one-arm row is a standing hinge, so it's chest-supported in sessions 1–2 (it conflicted with rule 3); Phase 4 bike intervals build 3 × 4 → 4 × 4 min, matching the off-season plan.
4. **Working Rules:** pre-session pain ≤2 (it said ≤1–2, against ≤2 everywhere else); the bike intervals credited to the Add-On; check-ins add single-leg control, the cooldown, and the upper warm-up/finisher; mid-week checkpoint written down; exercise-log `block` defined; the graft-window date moved out.
5. **Logs:** daily 10/11 minutes (80) and RPE (7), evening pain and gait; exercise 10/11 single-leg items split into L and R rows, 10/8 drill relabelled as a wobble board, 10/11 eyes-closed drill logged as not done.
6. **Checked and left alone:** the master plan and off-season plan (never edited).

### Moved into the repo 10/12

1. The dashboard's thread workflow (kickoff prompt, one thread per week, CSV copies) is gone: `CLAUDE.md` and the skills run the week; logs are written as he sends them. The Working Rules file was renamed `ACL_Working_Rules.md`.
2. **State:** sections 2, 4 and 8 point to the daily log, `measurements.csv` and the checkpoint, as the repo's States always did; the Sunday checkpoint writes it.
3. **PT Notes** became the one home for the PT's words; the per-visit files for PT 8, PT 9 and Nick's 10/9 instruction were folded into it (their numbers were already in `measurements.csv`).
4. **Throwing** named in this index, the Working Rules, the Add-On and the State. Sat 10/10 corrected: heel prop and weigh-in done (the dashboard had it as a zero day). Side plank from the feet on both sides, as the Add-On writes it.

**Habits that keep it clean:**
- End every session report with minutes and RPE.
- Give one swelling grade every morning, plus stiffness, catch and wellness.
- Decisions go to NOW and the State, not to log notes.
