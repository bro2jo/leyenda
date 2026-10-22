# real/ — changelog

How the Ledger's files came to be laid out, newest first. The current map is `README.md`. A rule's own history is the "Revision history" at the top of `plan/working_rules.md` and `plan/whole_athlete_addon.md`; a week's is its `checkpoints/<Sunday>.md`.

## 2026-10-22 · the dashboard's 10/15–10/21 revisions folded in

The dashboard project kept running beside the repo for ten days, and on 10/21 he re-issued its Working Rules and Add-On and revised its Recovery State of 10/18 in place (two reviews: the knee sessions, then the upper and add-on work). All three were ingested here (`/ingest`).
1. **Working Rules and Add-On:** the rule and design changes went into the repo's adapted copies (the file names, `/checkpoint`, the repo's log columns and the sport-plan pointer stay); each file's revision history carries the 10/15, 10/18 and 10/21 lines and a 10/22 (repo) line. Two repo-only items: the Add-On's "from Block 1 the incline drops to 2 sets" was kept (the re-issue doesn't contradict it); its 10/12 "throw first" order gave way to the re-issue's bike → throwing → lifting.
2. **State:** revised in place under 10/18 ("revised Wed 10/21"); §2, §4 and §8 stay pointers. The 10/21 Session A loads are its baselines, confirmed by Thursday's clean morning.
3. **Throwing:** where the uploads and the repo's sport plan disagreed, the State and the Add-On won (source priority): throwing on days without a knee session, slight pivots on any throwing day, no pivot bouts on knee days, the step-out and throwing on the move only with the PT's OK per drill; the pivot foot is named in each pivot row's `drill` (no new column). `config.json`: the sport days are Wed, Thu and Sat; the optional items' penalty is gone (`optional_from`: accessory 10/21, power 10/24); `sport.stage` reworded.
4. **PT notes:** a patient-reported clarification entry (Nick ran the 10/17 test; the Copenhagen OK is short-lever; Cody's knee-extension range and load).
5. **Left as the repo logged it:** Fri 10/16's heel prop (missed here, done in the dashboard's week table); 10/20–10/21's morning grades (trace here, "not reported" there).

## 2026-10-12 · one naming scheme

Every file and folder in `real/` renamed to lowercase snake_case with no `ACL_` prefix; current files keep a stable name, dates only on archives and one-event files (`README.md` → "Naming rules"). Older checkpoints, commit messages and git history use the old names:

| Old | New |
|---|---|
| `plan/ACL_Project_Index.md` | `README.md` (its audit history: below) |
| `plan/ACL_Dashboard_Working_Rules.md` (briefly `ACL_Working_Rules.md`) | `plan/working_rules.md` |
| `plan/ACL_Whole_Athlete_AddOn.md` | `plan/whole_athlete_addon.md` |
| `plan/ACL_Reconstruction_Rehab_Master_Plan.md` | `plan/rehab_master_plan.md` |
| `plan/24-week-offseason-program-v4.md` | `plan/offseason_program_24_week.md` (still v4) |
| `plan/sport/sport_plan.md` | `plan/sport_plan.md` |
| `plan/sport/Ultimate_Offseason_Development_Guide.md` | `plan/ultimate_offseason_guide.md` |
| `plan/sport/README.md` | folded into `README.md` |
| `state/ACL_Recovery_State_2026-10-11.md` | `state/recovery_state.md` (the current State always has this name) |
| `state/archive/ACL_Recovery_State_2026-10-04.md` | `state/archive/recovery_state_2026-10-04.md` |
| `state/archive/ACL_Recovery_State_2026-10-04_rev10-09_dashboard.md`, `…_v10-04.md` | removed: the dashboard's upload and the version as set 10/4 are in git history |
| `visits/ACL_PT_Notes.md` | `visits/pt_notes.md` |
| `visits/2026-10-01_PT8.md`, `2026-10-08_PT9.md`, `2026-10-09_Nick-instruction.md` | folded into `visits/pt_notes.md` (same day, below) |
| `visits/2026-10-10_trainer-instruction.md`, `2026-10-12_trainer-session.md` | `visits/2026-10-10_trainer_instruction.md`, `visits/2026-10-12_trainer_session.md` |
| `logs/ACL_Exercise_Log.csv` | `logs/exercise_log.csv` |
| `logs/foods.csv` | `logs/food_library.csv` |
| `logs/archive/ACL_Daily_Log.csv` | `logs/archive/dashboard_daily_log.csv` |
| `checkpoints/.gitkeep` | removed |

`engine/darrow.py` follows: `doc state` reads `state/recovery_state.md`; `doc visit` is gone (`doc ptnotes <date>` reads a visit); a checkpoint names the State its week ran by its Sunday.

## 2026-10-12 · moved into the repo

The ACL dashboard (a separate project) was retired and its files became this repo's own.
1. The dashboard's thread workflow (kickoff prompt, one thread per week, CSV copies) is gone: `CLAUDE.md` and the skills run the week, and logs are written as he sends them.
2. **State:** §2, §4 and §8 point to the daily log, `measurements.csv` and the checkpoint, as the repo's States always did; the Sunday checkpoint writes it.
3. **PT notes** became the one home for the PT's words; the per-visit files for PT 8, PT 9 and Nick's 10/9 instruction were folded into it (their numbers were already in `measurements.csv`).
4. **Throwing** named in the index, the Working Rules, the Add-On and the State. Sat 10/10 corrected: heel prop and weigh-in done (the dashboard had it as a zero day). Side plank from the feet on both sides, as the Add-On writes it.
5. **Logs:** the dashboard's audited exercise log replaced the repo's for 9/23, 10/8, 10/9 and 10/11 (earlier dates identical); its daily log replaced the archived copy; 10/11 minutes, RPE, pains and gait filled into `daily_log.csv`; a `wellness` column added. No XP or sheet change.

## 2026-10-12 · dashboard audit (mid-week checkpoint)

1. **State:** revised in place for Mon 10/12: Session B verdict (clean) and its doses as the baseline; Session A fixed for Tuesday; the eyes-closed drill corrected to a wobble-board drill with a BOSU home version; Upper B's row chest-supported for session 2; PT not yet booked.
2. **PT notes:** appended the 10/11 clarification that the 10/8 "WB" drill was on a wobble board.
3. **Add-On:** the doorway pec sequence replaces the 30 s stretch and moves ahead of the face pull; Upper B's one-arm row is a standing hinge, so it's chest-supported in sessions 1–2 (it conflicted with rule 3); Phase 4 bike intervals build 3 × 4 → 4 × 4 min, matching the off-season plan.
4. **Working Rules:** pre-session pain ≤2 (it said ≤1–2, against ≤2 everywhere else); the bike intervals credited to the Add-On; check-ins add single-leg control, the cooldown, and the upper warm-up/finisher; mid-week checkpoint written down; exercise-log `block` defined; the graft-window date moved out.
5. **Logs:** daily 10/11 minutes (80) and RPE (7), evening pain and gait; exercise 10/11 single-leg items split into L and R rows, the 10/8 drill relabelled as a wobble board, the 10/11 eyes-closed drill logged as not done.
6. **Checked and left alone:** the master plan and the off-season program (never edited).

## 2026-10-10 · dashboard audit

1. **Working Rules:** stripped to rules only. Moved to the State: swelling and goniometer history, PT items by date, daily-minimum dose, conditioning ladder, PT-item mapping, machine substitutes, clinic numbers, depths, and known tendencies (merged into State §9).
2. **Add-On:** design only. Moved to the State: rollout status, this week's days, loads, block dates, the PT question list. No separate prehab/posture plan: posture work is built into the Add-On (upper warm-up + knee-session cooldown). Sport recorded as ultimate + court + field.
3. **PT notes:** the header states the entry format; next-visit lists live only in State §5. Older entries unchanged.
4. **State:** rebuilt as the single home for current facts.
5. **Logs:** `swelling_am` normalized to the grade only, with descriptors moved to the trend column; new columns `conditioning_min` and `wellness_1to5`; exercise-log `side` normalized.
