# ACL Project Index

What each file in this project is for, where each kind of fact lives, and how the files get updated. Written Sat 2026-10-10; audited again Mon 2026-10-12. Read this first in every new thread.

**Principle: one home per fact.** Each fact is written in one file. Other files may point to it, but they don't copy it.
- The Recovery State is the exception: it's a self-contained snapshot, so it may restate rules briefly. A rule's home is still the Working Rules.

---

## Reading order for a new thread

0. This index (`claude/ACL_Project_Index.md`)
1. `ACL_Dashboard_Working_Rules.md`
2. The latest `ACL_Recovery_State_<Sunday>.md` (from 10/11 the dashboard saves it under `claude/`; only one State is kept)
3. `ACL_PT_Notes.md`
4. `ACL_Whole_Athlete_AddOn.md`
5. `ACL_Daily_Log.csv` and `ACL_Exercise_Log.csv`
6. `ACL_Reconstruction_Rehab_Master_Plan.md` for phase criteria
7. `24-week-offseason-program-v4.md` only when the add-on or a later phase needs it

---

## The files

| # | File | What it is | Changes | Belongs here | Doesn't belong here |
|---|---|---|---|---|---|
| 1 | `ACL_Reconstruction_Rehab_Master_Plan.md` | The rehab protocol: phases, exit criteria, doses, pain/swelling rules, red flags | **Never edited** | — | — |
| 2 | `24-week-offseason-program-v4.md` | The healthy-athlete off-season program for speed, cutting and jumping sports; the source for the Add-On. Comes back in stages, gated by the rehab plan (Add-On §8) | **Never edited** | — | — |
| 3 | `ACL_PT_Notes.md` | Archive of PT and surgeon notes, word for word, plus patient-reported verbal instructions and the patient's later clarifications of a visit. **Top-priority source** | Append only, the same day | The note word for word · the patient's account · a short dashboard reading | Next-visit lists, program changes, plans, booking status (→ Recovery State) |
| 4 | `ACL_Dashboard_Working_Rules.md` | How the dashboard operates: definitions, load and pain rules, clearance, red flags, check-in questions, the weekly rhythm's **structure**, checkpoint workflow, log schema, kickoff prompt | Only when a rule changes | Rules and definitions that hold for weeks | Dates, doses, counts, statuses, this week's schedule, measurements, patterns |
| 5 | `ACL_Whole_Athlete_AddOn.md` | The **design** of everything around the knee: upper sessions and blocks, the warm-up (including the doorway pec sequence), the tissue/trunk finisher, posture work (forward head, rounded shoulders, anterior pelvic tilt), the right leg, conditioning stages, the off-season mapping and sport settings | Only when the design changes | Session templates, block structure, add-on rules, the phase map | Which days it ran, this week's days, loads, block dates, PT questions (→ Recovery State) |
| 6 | `ACL_Recovery_State_<Sunday>.md` | **The single source for "now"**: phase and gates, measurement anchors and recent readings, PT instructions in force, the program with doses and ladders, this week's schedule, add-on status, the next-visit list, patterns, milestones | Replaced every Sunday; revised mid-week only on request, in place, under the same Sunday name | Anything current | Long history (lives in the logs) |
| 7 | `ACL_Daily_Log.csv` | One row per day | Via the thread; written at checkpoint or on request | The columns (schema in Working Rules). `swelling_am` = the grade only. `notes` ≤2 sentences (rows before 10/10 predate this rule and stay as written) | Decisions, instructions, plans |
| 8 | `ACL_Exercise_Log.csv` | One row per exercise instance | Same as the daily log | Exercise, side (L / R / bil; blank for upper and conditioning), sets, reps, hold, load, assist. Single-leg work on both legs = one row per side | — |
| — | The weekly chat thread | Where the week happens | Every day | Conversation, questions, drafts | It isn't a record: anything that matters becomes a row or a State entry |

---

## Where each fact lives

| Fact | Home |
|---|---|
| What the PT or surgeon said or measured | PT Notes (the State quotes the ones in force) |
| Phase criteria, plan doses | Master plan |
| Definitions, load and pain rules, clearance, workflow, log schema | Working Rules |
| Phase and gate status | State §3 |
| Measurement anchors and recent readings | State §4 (raw history in the logs) |
| PT-introduced items, the next-visit list, PT booking status | State §1 and §5 |
| Weekly rhythm | Structure → Working Rules; this week's actual days → State §6 |
| Daily minimum | What it means → Working Rules; dose → State §6 |
| Current doses, ladders, session tables, equipment substitutes, depths and heights | State §6 (home equipment in State §1) |
| Upper session design, warm-up, block structure, finisher, posture work, sport settings | Add-On |
| Conditioning: the Phase 3 rule | Working Rules; the stages after it → Add-On §5; the current ladder → State §6 |
| Upper status: sessions run, loads, block dates, unlocks | State §7 |
| Patterns and tendencies | State §9 |
| Daily and exercise data | The two CSVs |

---

## How things get updated

- **A PT visit:** paste the note. It goes into PT Notes word for word the same day.
- **A decision mid-week** (moving a session, a new dose): it changes the State only, unless it creates a new rule.
- **Logs mid-week:** brought up to date only on request.
- **Sunday checkpoint:**
  - append the week's rows to both logs
  - write a new State
  - update PT Notes if anything new came in
  - re-issue the Working Rules or Add-On only if a rule or the design changed
  - give the kickoff prompt for the new thread
- **Mid-week checkpoint (on request):** the same steps, with the State revised in place under the week's Sunday name; the thread continues, so no kickoff prompt.

---

## Audit 10/10 — what was done

1. **Working Rules:** stripped to rules only. Moved to the State: swelling and goniometer history, PT items by date, daily-minimum dose, conditioning ladder, PT-item mapping, machine substitutes, clinic numbers, depths, and known tendencies (merged into State §9). The kickoff prompt now reads this index first.
2. **Add-On:** design only. Moved to the State: rollout status, this week's days, loads, block dates, the PT question list. No separate prehab/posture plan: posture work is built into the Add-On (upper warm-up + knee-session cooldown). Sport recorded as ultimate + court + field.
3. **PT Notes:** the header states the entry format; next-visit lists now live only in State §5. Older entries unchanged.
4. **State:** rebuilt as the single home for current facts. The measurement log is anchors plus the last three weeks.
5. **Logs:**
   - `swelling_am` normalized to the grade only, with descriptors moved to the trend column. Blank = not reported.
   - New columns `conditioning_min` and `wellness_1to5`.
   - Exercise-log `side` normalized.

## Audit 10/12 — what was done (mid-week checkpoint)

1. **State:** revised in place for Mon 10/12: Session B verdict (clean) and its doses as the baseline; Session A fixed for Tuesday; the eyes-closed drill corrected to a wobble-board drill with a BOSU home version; Upper B's row chest-supported for session 2; PT not yet booked.
2. **PT Notes:** appended the 10/11 clarification that the 10/8 "WB" drill was on a wobble board.
3. **Add-On:** the doorway pec sequence replaces the 30 s stretch and moves ahead of the face pull; Upper B's one-arm row is a standing hinge, so it's chest-supported in sessions 1–2 (it conflicted with rule 3); Phase 4 bike intervals build 3 × 4 → 4 × 4 min, matching the off-season plan.
4. **Working Rules:** pre-session pain ≤2 (it said ≤1–2, against ≤2 everywhere else); the bike intervals credited to the Add-On (the rules called them the rehab plan's, which has none); check-ins add single-leg control, the cooldown, and the upper warm-up/finisher; mid-week checkpoint written down; exercise-log `block` defined; the graft-window date moved out.
5. **Logs:**
   - Daily: 10/11 minutes (80) and RPE (7), evening pain and gait; new 10/12 morning row; 10/9 `addon_rpe` made a number; 9/25 extension descriptor corrected from "read as 3 hyperext" to "likely 3 short of 0, the outlier".
   - Exercise: 10/11 single-leg items split into L and R rows; 10/8 drill relabelled as a wobble board; 10/11 step-down quality and RDL effort added; 10/11 eyes-closed drill logged as not done.
6. **Checked and left alone:** the master plan and off-season plan (never edited; the Add-On's thresholds, doses and sport settings match the off-season plan). Pre-10/10 log notes that are long or hold decisions stay as history.

**Habits that keep it clean:**
- End every session report with minutes and RPE.
- Give one swelling grade every morning, plus stiffness, catch and wellness.
- Keep decisions in the thread; they go to the State, not to log notes.
