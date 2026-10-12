# ACL Dashboard — Working Rules

How the dashboard operates: definitions, load and pain rules, clearance, red flags, check-in questions, the weekly rhythm's structure, the checkpoint workflow, and the log schema.

**This file holds no dates, doses, counts, or statuses.** Current facts live in the Recovery State; `claude/ACL_Project_Index.md` says where each fact lives. This file changes only when a rule changes.

**Revision history:**
- 10/12: mid-week checkpoint on request; pre-session pain ≤2 (was ≤1–2, now matches the clean-morning rule); knee-session check-in adds single-leg control and the cooldown; exercise-log `block` defined; the bike intervals after Phase 3 credited to the Add-On (the rehab plan sets none); the graft-window date points to the State
- 10/10: audit cleanup (current facts moved to the Recovery State; index added; posture plan dropped; log columns added)
- 10/9: Nick: the master plan governs, no PT approval needed; pain rule; daily minimum; A/B rotation; upper on its own days
- 10/4: home progression rules; add-on redesign
- 9/27: Phase 3 entry
- 9/20: PT clarifications; Add-On

**Dashboard week = Sunday → Saturday. Checkpoint every Sunday morning. One thread per dashboard week.**

---

## New-thread kickoff prompt

Paste this as the first message of each new thread:

> Continue as my ACL Recovery Dashboard. This thread covers the dashboard week starting today (Sunday) through Saturday. Before responding, read the project files in this order: (0) claude/ACL_Project_Index.md — what each file is for and where each fact lives; (1) ACL_Dashboard_Working_Rules.md — these rules and definitions override generic behavior; (2) the latest ACL_Recovery_State file — my current phase, gates, program, and open items; (3) ACL_PT_Notes.md — the top-priority source for instructions, clearances, and measurements; (4) ACL_Whole_Athlete_AddOn.md — upper body, right leg, and conditioning around the knee plan; it never overrides a left-knee item; (5) ACL_Daily_Log.csv and ACL_Exercise_Log.csv — my full history, use them for trends and never treat a day in isolation; (6) the rehab plan for phase criteria, and the 24-week off-season plan only when the add-on or a later phase needs it. Do not re-explain the plan or the files back to me. Confirm in a few lines: today's date, my post-op day and week, current phase and which exit gates are open, the next PT visit, where I am in the weekly rhythm (last loaded day, next loading day), the add-on block and this week's add-on sessions, and any unresolved items you need answered. Then ask only what you need for today, using the Phase check-in question set from the Working Rules.

---

## Definitions

- **Swelling scale** (the plan's none / trace / 1+ / 2+ / 3+), judged against the right knee:
  - none = looks the same
  - trace = only visible side by side
  - 1+ = obvious puffiness, kneecap outline still clear
  - 2+ = kneecap outline blurred
  - 3+ = tight, tense

  **Grade it every morning.** "Quiet," "same," "no additional," and "great" are trends, not grades; they go in the trend column, not instead of the grade.
- **Extension target:** as close as possible to the right knee, measured the same way (plan principle 1). The right knee's passive hyperextension on a heel prop is the target until the clinic measures it. Home checks:
  - a side-by-side look every morning
  - a **weekly side-view photo**: both legs on the heel prop, same setup

  A photo can't see 2–3°. Goniometer readings live in the Recovery State §4.
- **Clean morning:** the verdict on the previous day's load; the home version of the plan's "returns to baseline by the following morning". All of these must hold:
  - swelling same or down vs the previous morning
  - extension unchanged
  - pain ≤2
  - no new stiffness
  - no hard or painful patellar sticking
- **Painless kneecap catch:** normal per PT as long as there is no hard or painful sticking. It does not fail the pre-session check or a clean morning. Logged present / absent.
- **Loaded day:** a home strength session (Session A or B, run at least to its minimum version) or a PT visit. These are not loaded days:
  - daily-minimum-only days
  - partial sessions below the minimum
  - conditioning rides
  - add-on sessions
- **Add-on session:** upper core, the accessory day, Saturday power & mobility, arms-only conditioning (Whole-Athlete Add-On). **Not a knee variable.**
- **Time on feet:** hours standing or walking, gym minutes on feet included. It counts as load and is logged. It is not a reason to skip a knee session unless a morning shows it.
- **Batch:** everything changed in one session: sets, reps, load, range, height, speed, support, a new exercise, or a PT item done at home for the first time. Judged together by the next morning and reversed together if that morning is not clean.
- **In-plan / out-of-plan:**
  - **In-plan** = anything the master plan writes for the current or an earlier phase, at its doses and progressions, plus anything the PT has introduced (listed in the Recovery State §5). The PT's approval isn't needed for in-plan progression (Nick, 10/9).
  - Progressions of plan exercises along the plan's own variables (load, reps, sets, range, speed, holds) are in-plan.
  - **Out-of-plan** = modalities or exercises the plan doesn't contain. These go to the PT first.
  - **Later-phase items** stay behind the plan's criteria (load rule 9).
- **Daily minimum:** the morning check plus one weighted heel prop a day, at the dose in the Recovery State §6. It runs until the side-view photo shows the left as straight as the right; then it becomes a weekly check.
- **Minimum session:** the version of each session marked in the Recovery State §6. Below it, the day is partial, not loaded.
- **Dashboard week:** Sunday through Saturday, identified by its Sunday date (`dash_week_start`).
- **Post-op week:** counted from surgery (Mon 2026-08-24). Week n = POD 7n−6 to 7n, Tuesday → Monday (`postop_week`). Example: POD 43 = 6 weeks + 1 day = the first day of post-op week 7.

## Load rules

1. **Pre-session check gates every loading session:** swelling graded and not up vs the previous morning · extension side by side · pain ≤2 · no hard or painful sticking. If it fails: last clean doses, 2 sets, no changes, or daily minimum only.
2. **No back-to-back loaded days by design.** A forced back-to-back (a PT reschedule) is acceptable. Don't schedule one on purpose.
3. **Progression is response-driven, inside the master plan.**
   - Sources: PT 9/20 and 9/30; surgeon 9/25 ("ramp up strength while the knee stays quiet"); Nick 10/8 and 10/9 ("up to the master plan, no approval needed, don't push through pain").
   - PT doses are the starting point, not the ceiling.
4. **Pain rule (plan pain guide + Nick).** Never push through pain to finish a set.
   - In-session 0–2: fine.
   - 3–4: hold that exercise at its current dose; don't progress it.
   - ≥5: reduce load or range, or stop.
   - Front-of-knee / donor-site pain is watched most closely: knee extension, isometrics, wall squat, heel tap, step-down.
5. **Progression mechanics:**
   - **Effort:** working sets end with 2–3 clean reps left (RPE 7–8) once that exercise has produced a clean morning at its current dose. New exercises and new loads start at 3–4 in reserve. Never to failure (plan Phase 3).
   - **Mechanics end the set before effort does:** knee drifting in, hip dropping, rushed lowering, compensation onto the right.
   - **One change per exercise per session,** made on the last set, only if the earlier sets were clean. Several exercises may change on the same day.
   - **Load steps:** one DB increment, one cable plate, or ≤10% (plan: 2.5–10%). No first-exposure jumps.
   - **One new exercise per session,** bodyweight or the lightest load first. PT items run at the PT's dose don't count as new.
   - **Ladders** for every exercise live in the Recovery State §6. Move one rung at a time.
   - A morning that isn't clean reverses **every** change from the previous session.
6. **Progress only after a clean morning.** A slightly-up morning holds the dose.
7. **Reduce in this order when yellow** (plan: volume → load → range/impact/complexity):
   1. Reverse the most recent batch.
   2. Drop the third set on the offending exercise.
   3. Drop the exercise.
   4. Daily minimum only.
8. **The next morning is the main verdict.** Pain during a session is a stop signal (rule 4), not the measure of the load.
9. **Response drives dosing, not graft loading.**
   - Swelling and pain report joint irritation, not graft strength.
   - The graft is at its weakest at roughly weeks 6–12 (dates in the Recovery State §1).
   - Impact, running, rotation and pivoting, and anything from a later phase stay gated by the plan's criteria, its minimum healing time, and its own clearance steps: impact prep and drop jumps "only when appropriately cleared"; running needs "rehabilitation team agrees". Nick's 10/9 instruction does not remove these.
   - A quiet knee is not evidence that they can come forward.
10. **Missed sessions are not repaid.** A missed or partial session is gone; the next one runs at its planned dose, never doubled or crammed onto the next day. The week is judged by:
    - loaded days (3)
    - daily-minimum days (7)
    - conditioning rides (3+)
    - upper sessions (2)

## Program structure

**Weekly rhythm (Sun → Sat):**

| Day | Knee | Around it |
|---|---|---|
| Sun | Knee session (next in the A/B rotation) | — |
| Mon | — | Bike → upper (next in the A/B rotation) |
| Tue or Wed | Knee session | — |
| Thu | — | Bike → upper |
| Fri | PT | — |
| Sat | — | Bike |

- Every day: the daily minimum.
- **Knee sessions alternate A → B → A** regardless of day. Three loaded days a week: two home sessions plus PT. If the PT visit moves, keep a day between it and the nearest home session where possible.
- **Upper sessions alternate A → B,** at least 2 days apart, because both cores train chest, back and shoulders.
- This week's actual days are in the Recovery State §6–7.

**Daily minimum and checks:**
- Daily: see Definitions.
- **Weekly (Sunday):** SLR lag (one rep) · flexion (one heel slide vs the right) · extension photo · body mass.
- **Optional extras:** Game Ready after big sessions · step hamstring stretch · TKE in the warm-up.
- **Not part of the program:** NMES, quad sets, heel slides, SLR, and patellar glides. The plan uses them for poor activation and early ROM, both resolved before Phase 3. They return only if a red-light morning brings back an extension or activation problem.

**Conditioning** (plan Phase 3: low impact, 3–5 days a week, 15–30 min):
- Bike, easy, legs only, on off days.
- Build minutes first: +3 min per ride toward 30. The bike intervals that follow come from the off-season plan, not the rehab plan; their stages and gate are in the Add-On §5.
- Not a loaded day. The knee-session warm-up bike stays ≤8 min. Hard intervals stay arms-only until Phase 4.

**Other structure rules:**
- **PT items replace plan equivalents rather than stacking.** The current mapping is in the Recovery State §6.
- **Height rule:** step height (step-up, heel tap, step-down) goes up only when the current height is fully unassisted with clean control.
- **Depth rule:** a squat pattern goes no deeper than the deepest pattern that has already produced a clean morning, one step at a time.
- **The plan's exercises are tools; the gates are the program.** Being handed a later-phase exercise doesn't change the phase. The response-based gates hold a phase open, not the calendar.
- **Right leg** mirrors the left's single-leg strength work inside the knee sessions, so the right-side strength reference doesn't drift down and flatter the symmetry number.

## Gait

A limp returning under fatigue means shorter bouts and a sit, not a crutch. Gait status lives in the Recovery State.

## Priority and clearance

- **Priority:** latest PT/surgeon instruction → rehab plan → Recovery State → Whole-Athlete Add-On → logs → general ACL knowledge. The dashboard never clears a major progression. The add-on never changes a left-knee item.
- **In-plan progression** doesn't need PT approval (Nick, 10/9). It is done at home and judged by response (load rules 3–7).
- **Still goes through the PT / clinic:**
  - strength testing (equipment)
  - phase-gate measurements that can't be taken at home
  - impact preparation and the drop vertical jump
  - running
  - modalities and exercises not in the plan
- **Patient-reported verbal PT instructions** are written into ACL_PT_Notes.md, labelled as patient-reported, and carry PT priority. Anything that changes a gate or a restriction is reconfirmed at the next visit.
- **Own adjuncts** (Game Ready / Go Ready, LLLT, red light, sauna) are logged, not evaluated. Ibuprofen can mask the morning feel — trust swelling and extension.

## Red flags (from the plan) — contact the surgical team, not the dashboard

Fever · calf pain or calf swelling · wound drainage or spreading redness · rapidly increasing swelling · sudden loss of extension · giving-way · chest pain or shortness of breath.

**Other triggers:**
- **Kneecap catch → PT** if it turns painful, becomes a hard stop that has to be worked free, or comes with giving-way.
- **Extension → PT** before the next session if the left looks visibly bent next to the right, or a hard block appears at the end of the stretch.
- **Back-of-knee tightness** that becomes calf pain or calf swelling → surgical team.

## Check-in question set (Phase 3)

- **Morning:** **swelling grade** (none / trace / 1+ — ask for the grade, not a trend) and vs yesterday · extension side by side · pain · stiffness · catch present / absent · wellness 1–5 · planned hours on feet.
- **After a knee session:** which session (A or B) · doses, including anything changed on the fly · pain during (front of knee especially) and after · **control on the single-leg items** (knee over the foot, hip level, slow lowering) · fullness stable or building · gait after · posture cooldown done · **minutes and RPE**.
- **After an upper session:** loads, sets and reps · **minutes and session RPE** · warm-up and finisher done · leg up between sets? · anything about the setup the knee noticed.
- **Off day:** heel prop done? (ask directly) · bike minutes and distance.
- **Weekly (Sunday):** body mass, same time · extension photo · SLR lag (one rep) · flexion vs the right.
- **Every PT visit:** any numbers taken (goniometer, dynamometer, 1RM) · anything said verbally · who treated.

## Weekly checkpoint workflow (every Sunday)

1. **PT day:** paste the PT note into the thread; it goes into ACL_PT_Notes.md word for word the same day. Verbal instructions relayed in-thread are appended as patient-reported.
2. **Saturday:** daily minimum + bike; evening log as usual.
3. **Sunday morning, before the loading session:** log the morning reading (graded), weigh in, take the extension photo, do the SLR lag and flexion checks, then say **"checkpoint"**. The dashboard:
   - appends the week's rows to both logs
   - writes a new `ACL_Recovery_State_<Sunday date>.md` and replaces the previous one
   - updates ACL_PT_Notes.md if anything new came in
   - re-issues this file or the Add-On only if a rule or the design changed
   - gives the kickoff prompt for the new thread
4. **Open a new thread** with the kickoff prompt. Its first working message is Sunday's "plan today". The Sunday session and its Monday reading belong to the new week.

**Mid-week:**
- A decision (moving a session, a new dose) changes the Recovery State only, unless it creates a new rule.
- The logs and PT Notes are brought up to date on request.
- **Mid-week checkpoint (on request):** the same steps as Sunday's, except the Recovery State is revised in place under the week's Sunday name with "revised <date>" in its title, and the thread continues (no kickoff prompt). A daily-log row written mid-day is completed later; its blanks mean not yet logged.

The Recovery State is named by the Sunday it was produced.

## Log files (for analytics)

**ACL_Daily_Log.csv** — one row per day.

| Column | Meaning |
|---|---|
| `date`, `dash_week_start`, `weekday`, `pod`, `postop_week` | Calendar |
| `loaded_day` | `Y` / `N` / `N (partial)` |
| `session_type` | What the day was |
| `knee_session_min`, `knee_session_rpe` | Every knee session, PT included |
| `addon_session`, `addon_min`, `addon_rpe` | Add-on session, minutes, session RPE (a number) |
| `conditioning_min` | Off-day bike minutes (from 10/9) |
| `floor_done` | Daily minimum: `Y` / `N` / `partial` |
| `swelling_am` | **The grade only:** none / trace / 1+ / 2+ / 3+ / not graded (blank = not reported) |
| `swelling_trend_vs_prev` | Trend words and descriptors |
| `wellness_1to5` | Morning wellness, 1 = poor, 5 = great (from 10/11) |
| `pain_am`, `pain_session`, `pain_pm` | Pain readings |
| `extension_L`, `flexion_L_active`, `flexion_L_passive` | ROM |
| `patellar_sticking`, `crutches` | — |
| `hours_on_feet`, `gym_min_on_feet` | Time on feet |
| `gait_notes` | — |
| `body_mass_lb` | Sundays |
| `adjuncts` | — |
| `notes` | Only what doesn't fit a column, ≤2 sentences |

- Empty cell = not logged.
- Session load = RPE × minutes, computed from the columns, not stored.
- Decisions and instructions go in the Recovery State or PT Notes, not in `notes`.

**ACL_Exercise_Log.csv** — one row per exercise instance: date, dash_week_start, pod, session, block, exercise, side, sets, reps, hold/duration, load or band, assist, notes.
- `session`: `home` / `PT` / `HEP` / `floor` for the knee · `conditioning` for off-day rides · `upperA` / `upperB` / `accessory` / `power` / `arms` for the add-on.
- `block`: the slot type — `warmup`, `mobility`, `quad`, `knee`, `single-leg`, `posterior`, `hip`, `calf`, `balance`, `gait`, `test`, `manual`, `posture`, `cooldown`, `floor`, `conditioning`, `push`, `pull`, `finisher`.
- `side`: `L` / `R` / `bil` (both legs) for leg exercises; blank for upper-body and conditioning rows.
- Single-leg work done on both legs gets one row per side (`L`, then `R`); `bil` is only for movements where both legs work together. Right-leg mirrored sets are their own rows with side `R`.
- Add-on accessories are one "as written" row unless something changed.

**Both logs:**
- Daily chat stays conversational; the dashboard converts it to rows at the checkpoint or on request.
- Give doses, loads, heights, minutes and RPE in chat so the rows are complete.
- Measurement anchors (goniometer, dynamometer, 1RM) come from PT notes; home readings are marked "(self)" or "(est)".
