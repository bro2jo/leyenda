# ACL Dashboard — Working Rules

Rules, definitions, and workflow established in-thread that are not written in the rehab plan. This file changes rarely; the Recovery State file changes every Sunday. Read both at the start of every new thread.

**Revised Fri 2026-10-09:** Nick Immel PT (10/9, patient-reported) said progression is up to the master plan, his approval isn't needed, and the main thing is not pushing through pain. Changes:
- The "held for the PT" list is gone for anything the plan writes. Seated knee extension 90°→45° (plan Phase 3) joins Session A.
- A pain rule taken from the plan (load rule 4).
- The daily floor is cut to a morning check plus one weighted heel prop a day. NMES, quad sets, heel slides, SLR, and patellar glides are dropped; the plan uses them for poor quad activation and early ROM, and both are resolved.
- PT 10/8 items are mapped into the home sessions, and the two-leg banded sit-to-stand is retired.
- Upper body moves to its own days (user, 10/5).
- Knee sessions alternate A/B instead of sitting on fixed days.
- `conditioning` is added as an exercise-log session value.

Earlier revisions: 10/4 (home progression rules, floor minimum, add-on redesign) · 9/27 (Phase 3 entry) · 9/20 (PT clarifications, Add-On).

**Dashboard week = Sunday → Saturday. Checkpoint every Sunday morning. One thread per dashboard week.**

---

## New-thread kickoff prompt

Paste this as the first message of each new thread:

> Continue as my ACL Recovery Dashboard. This thread covers the dashboard week starting today (Sunday) through Saturday. Before responding, read the project files in this order: (1) ACL_Dashboard_Working_Rules.md — these rules and definitions override generic behavior; (2) the latest ACL_Recovery_State file — my current phase, gates, program, and open items; (3) ACL_PT_Notes.md — the top-priority source for instructions, clearances, and measurements; (4) ACL_Whole_Athlete_AddOn.md — upper body, right leg, and conditioning around the knee plan; it never overrides a left-knee item; (5) ACL_Daily_Log.csv and ACL_Exercise_Log.csv — my full history, use them for trends and never treat a day in isolation; (6) the rehab plan for phase criteria. Do not re-explain the plan or the files back to me. Confirm in a few lines: today's date, my post-op day and week, current phase and which exit gates are open, the next PT visit, where I am in the weekly rhythm (last loaded day, next loading day), the add-on rollout stage and this week's add-on sessions, and any unresolved items you need answered. Then ask only what you need for today, using the Phase check-in question set from the Working Rules.

---

## Definitions

- **Swelling scale** (plan's none / trace / 1+ / 2+ / 3+), judged against the right knee:
  - none = looks the same
  - trace = only visible side by side
  - 1+ = obvious puffiness, kneecap outline still clear
  - 2+ = kneecap outline blurred
  - 3+ = tight, tense

  **Grade it every morning.** "Quiet," "same," "no additional," and "great" are trends, not grades; they go alongside the grade, not instead of it. Grades so far: 1+ (9/20–9/24) → 1+ very close to trace (9/27) → **trace 10/6–10/9** (10/9 "barely visible").
- **Extension:**
  - Goniometer anchors: 2° hyperext 9/11 · −3° 9/25 (read as 3° short; the outlier) · 2° hyperext after a weighted stretch 10/1 · **2° hyperext AROM 10/8**.
  - The right knee measured 0° AROM pre-op, so by the clinic's method the left is at least as straight.
  - Remaining target: the right knee's passive hyperextension on a heel prop, never measured. Home check is the **weekly side-view photo** (both legs, same setup, on the heel prop). A photo can't see 2–3°, so ask the clinic for a quick measure when convenient.
- **Clean morning:** swelling same or down vs the previous morning, extension unchanged, pain ≤2, no new stiffness, no hard or painful patellar sticking. This is the verdict on the previous day's load. It is the home version of the plan's "returns to baseline by the following morning" and the PT's "no considerable return of swelling, no pain after."
- **Painless kneecap catch:** normal per PT as long as there is no hard or painful sticking. It does not fail the pre-session check or a clean morning. Logged present / absent.
- **Loaded day:** a home strength session (Session A or B, run at least to its minimum version) or a PT visit. These are not loaded days:
  - floor-only days
  - partial days below the minimum
  - conditioning bike rides
  - add-on sessions
- **Add-on session:** upper core blocks, the accessory day, power & mobility, arms-only conditioning (ACL_Whole_Athlete_AddOn.md). Seated, lying, or prone with the left leg up for the first two upper sessions. **Not a knee variable.** Upper runs on its own days (user's choice, 10/5).
- **Time on feet:** hours standing or walking, gym minutes on feet included. It counts as load and is logged daily. It has stopped moving the swelling (9/26, 9/27, 10/3, 10/4, 10/5), so it is not a reason to skip a knee session.
- **Batch:** everything changed in one session — sets, reps, load, range, height, speed, support, a new exercise, or a PT item at home for the first time. Judged together by the next morning and reversed together if that morning is not clean.
- **In-plan / out-of-plan (revised 10/9):**
  - **In-plan** = anything the master plan writes for the current or an earlier phase, at the plan's doses and progressions, plus anything the PT has introduced. Nick (10/9): progression within the plan doesn't need his approval.
  - PT-introduced items, 10/1: wall squat · heel tap slow eccentric · forward step-down 6" · isometric knee extension at 90° · weighted heel prop · step hamstring stretch.
  - PT-introduced items, 10/8: 12" step-up with opposite knee drive · standing heel raise with 35 lb DBs · standing bird dog 8 lb · multi-hip abduction / extension / flexion · eyes-closed balance.
  - **Progressions of plan exercises along the plan's own variables** (load, reps, sets, range, speed) are in-plan. Examples: load on the bridge, slow-eccentric tempo on the split squat or RDL.
  - **Out-of-plan** = modalities or exercises the plan doesn't contain (BFR, Spanish squat, seated rotational throws). Mention these to the PT first.
  - **Later-phase items** stay behind the plan's phase criteria (load rule 9).
- **Minimum session:**
  - Session A = warm-up + SL sit-to-stand + step-up + seated knee extension 90°→45° + 90° isometric (~30 min).
  - Session B = warm-up + forward step-down + SL sit-to-stand + RDL (~25 min).
  - Cut from the bottom of the session table. Below the minimum, the day is partial, not loaded.
- **Dashboard week:** Sunday through Saturday, identified by its Sunday date (`dash_week_start`).
- **Post-op week:** counts from surgery (Mon 2026-08-24). Week n = POD 7n−6 to 7n, Tuesday → Monday (`postop_week`). On POD 43, 6 weeks + 1 day have passed and post-op week 7 has begun.

## Load rules

1. **Pre-session check gates every loading session:** swelling graded and not up vs the previous morning · extension side by side · pain ≤1–2 · no hard or painful sticking. If it fails: last clean doses, 2 sets, no changes, or floor-only.
2. **No back-to-back loaded days by design.** A forced back-to-back (PT reschedule) is acceptable: 9/30–10/1 produced a clean morning, unlike 9/10–11. Don't schedule one on purpose.
3. **Progression is response-driven, inside the master plan.**
   - Sources: PT 9/20; PT 9/30 "continue to ramp up"; surgeon 9/25 "ramp up strength while the knee stays quiet"; Nick 10/8 "keep progressing, challenging, well-balanced"; Nick 10/9 "up to the master plan, no approval needed, don't push through pain."
   - PT doses are the starting point, not the ceiling.
4. **Pain rule (plan pain guide + Nick 10/9).** Never push through pain to finish a set.
   - In-session 0–2: fine.
   - 3–4: hold that exercise at its current dose; don't progress it.
   - ≥5: reduce load or range, or stop.
   - Front-of-knee / donor-site pain is watched most closely: knee extension, isometric, wall squat, heel tap, step-down.
5. **Progression mechanics (10/4):**
   - **Effort:** working sets end with 2–3 clean reps left (RPE 7–8) once that exercise has produced a clean morning at its current dose. New exercises and new loads start at 3–4 in reserve. Never to failure (plan Phase 3).
   - **Mechanics end the set before effort does:** knee drifting in, hip dropping, rushed lowering, compensation onto the right.
   - **One change per exercise per session**, made on the last set, only if the earlier sets were clean. Several exercises may change on the same day.
   - **Load steps:** one DB increment or ≤10% (plan: 2.5–10%). No first-exposure jumps. Past examples: 9/30 RDL bodyweight → 25 lb DBs; 10/6 step-up bodyweight → 25 lb DBs with the band removed; 10/6 SL sit-to-stand 24" → 18".
   - **One new exercise per session, bodyweight or lightest load first.** PT items run at the PT's dose don't count as new.
   - **Ladders** for every exercise live in the Recovery State, section 6. Move one rung at a time.
   - A morning that isn't clean reverses **every** change from the previous session.
6. **Progress only after a clean morning.** A slightly-up morning holds the dose.
7. **Reduce in this order when yellow** (plan: volume → load → range/impact/complexity):
   1. Reverse the most recent batch.
   2. Drop the third set on the offending exercise.
   3. Drop the exercise.
   4. Floor-only day.
8. **The next morning is the main verdict.** In-session pain has never exceeded 2; if it does, rule 4 applies.
9. **Response drives dosing, not graft loading.**
   - Swelling and pain report joint irritation, not graft strength.
   - The graft is at its weakest at roughly weeks 6–12, **now through ~11/16**.
   - Impact, running, rotation and pivoting, and anything from a later phase stay gated by the plan's criteria, its minimum healing time, and its own clearance steps. Impact prep and drop jumps come "only when appropriately cleared," and running needs "rehabilitation team agrees."
   - Nick's 10/9 instruction does not remove these. A quiet knee is not evidence that they can come forward.
10. **Missed sessions are not repaid.** A missed or partial session is gone; the next one runs at its planned dose, never doubled. The week is judged by:
    - loaded days (3)
    - daily-minimum days (7)
    - conditioning rides (3+)
    - upper sessions (2)

## Program structure

- **Weekly rhythm (Sun → Sat, revised 10/9):**

  | Day | Knee | Around it |
  |---|---|---|
  | Sun | Knee session (next in the A/B rotation) | — |
  | Mon | — | Bike → Upper A |
  | Tue or Wed | Knee session | — |
  | Thu | — | Bike → Upper B |
  | Fri | PT | — |
  | Sat | — | Bike |

  - Every day: the daily minimum.
  - Knee sessions **alternate A → B → A** regardless of day; whichever is next runs. Three loaded days a week (two home sessions + PT).
  - If the PT visit moves, keep a day between it and the nearest home session where possible.
  - Session content lives in the Recovery State, section 6.
- **Daily minimum — every day (revised 10/9):**
  - **Morning check (~30 s):** swelling grade · extension side by side · pain · catch.
  - **Weighted heel prop, 10 lb, 10 min, once a day.** Weight on the lower thigh just above the kneecap, never on it. Quad relaxed. A stretch behind the knee is fine; sharp pain is not. Weight and time are plan decisions now (Nick 10/9).
  - Runs until the side-view photo shows the left as straight as the right; then it becomes a weekly check.
  - Rest periods between upper sets (leg up) count as extra heel-prop time.
- **Dropped 10/9:** NMES, quad sets, heel slides, SLR, patellar glides, routine compression. The plan uses NMES "when quadriceps activation is poor," and the rest are Phase 1–2 early-ROM and activation work. Evidence that both are resolved:
  - SLR no lag
  - full TKE lockout
  - maximal strap isometric, pain-free
  - flexion 146° vs the right's 144°
  - extension 2° hyperext
- **Weekly checks (Sunday):** SLR lag (one rep) · flexion (one heel slide vs the right) · extension photo · body mass.
- **Optional:** Game Ready / compression after big sessions · step hamstring stretch · posture bolt-on (chin nod, 90/90 hip lift as separate drills) · TKE in the warm-up.
- **Conditioning (plan Phase 3: low impact, 3–5 days a week, 15–30 min):**
  - Bike, easy, legs only, on Mon, Thu, Sat and any other off day.
  - Build minutes first: +3 min per ride from 15 (10/9) toward 30. Distance logged.
  - Not a loaded day. The knee-session warm-up bike stays ≤8 min. Hard intervals stay arms-only.
- **PT items replace plan equivalents rather than stacking:**
  - 12" step-up with opposite knee drive (10/8) = step-up slot.
  - Standing heel raise with 35 lb DBs (10/8) = calf slot.
  - Multi-hip abduction / extension / flexion (10/8) = Session B hip slot. At home: standing band at the ankle, plus adduction from the plan.
  - Standing bird dog (10/8): added to Session B.
  - Eyes-closed double-leg stance (10/8): after BOSU in both sessions.
  - SL sit-to-stand = leg-press slot (both sessions; the plan's Workout B has a partial SL leg press).
  - Heel tap slow eccentric = Session A's eccentric single-leg item.
  - Forward step-down 6" = Session B's step-down slot.
  - 90° isometric stays beside the moving knee extension. Wall squat stays in Session A.
  - **Two-leg banded sit-to-stand retired 10/9:** skipped three times and superseded by the SL sit-to-stand at 18".
- **Machine items at home:** there is no leg press, leg curl, or knee-extension machine. Substitutes (PT 9/23: bodyweight or DB):
  - SL sit-to-stand (leg press)
  - band hamstring curl (leg curl)
  - strap isometric at 90° (seated, feet hanging, ankle strapped to the bench leg, kick into the strap without moving)
  - **seated knee extension 90°→45°** with a band anchored behind the bench leg or an ankle weight (equipment to confirm)

  Clinic numbers: SL leg press 55# 2 × 10 (10/1) · SL leg press 1RM R 14 / L 9 plates (10/8) · leg curl 47.5#.
- **Depths and heights:**
  - SL sit-to-stand: 18" (clean morning 10/6).
  - Wall squat: depth is a plan decision; pain-free, and no deeper than the SL sit-to-stand until a clean morning at that depth.
  - Step height (step-up, heel tap, step-down) goes up only when the current height is fully unassisted with clean control. The PT used a 12" step-up on 10/8.
- **The plan's exercises are tools; the gates are the program.** Being handed a Phase 3 exercise doesn't change the phase. The response-based gates hold a phase open, not the calendar.
- **Right leg** mirrors the left's single-leg strength work inside the knee sessions, so 83.7 / 79 lb don't drift down and flatter the symmetry number.

## Gait

- **Surgeon 9/25:** no crutches.
- **PT 10/8:** good pattern, equal weight bearing bilaterally, no device, no brace.
- A limp returning under fatigue means shorter bouts and a sit, not a crutch.
- Time on feet is still logged, though swelling no longer tracks it.

## Priority and clearance

- **Priority:** latest PT/surgeon instruction → rehab plan → Recovery State → Whole-Athlete Add-On → logs → general ACL knowledge. The dashboard never clears a major progression. The add-on never changes a left-knee item.
- **Nick 10/9:** the master plan governs progression; in-plan items don't need PT approval. They are allowed at home and response-judged (load rules 3–7).
- **Still goes through the PT / clinic:**
  - the quad strength test, both sides (equipment; the Phase 4 gate needs it)
  - phase-gate measurements that can't be taken at home
  - impact preparation and the drop vertical jump (plan: "when appropriately cleared")
  - running (plan: "rehabilitation team agrees")
  - modalities and exercises not in the plan (BFR, Spanish squat, seated rotational throws)
- **Patient-reported verbal PT instructions** are written into ACL_PT_Notes.md, labelled as patient-reported, and carry PT priority. Anything that changes a gate or a restriction gets reconfirmed at the next visit.
- **Own adjuncts** (Game Ready / Go Ready, LLLT, red light, sauna) are logged, not evaluated. Ibuprofen can mask the morning feel — trust swelling and extension.

## Red flags (from the plan) — contact the surgical team, not the dashboard

Fever · calf pain or calf swelling · wound drainage or spreading redness · rapidly increasing swelling · sudden loss of extension · giving-way · chest pain or shortness of breath.

**Other triggers:**
- **Kneecap catch → PT** if it turns painful, becomes a hard stop that has to be worked free, or comes with giving-way.
- **Extension → PT** before the next session if the left looks visibly bent next to the right, or a hard block appears at the end of the stretch.
- **Back-of-knee tightness** that becomes calf pain or calf swelling → surgical team.

## Check-in question set for Phase 3 (revised 10/9)

- **Morning:** **swelling grade** (none / trace / 1+ — ask for the grade, not a trend) and vs yesterday · extension side by side · pain · stiffness · catch present / absent · planned hours on feet.
- **After a knee session:** which session (A or B) · what was done at what doses, including anything changed on the fly · the batch · pain during (front of knee especially) and after · fullness stable or building · gait after · minutes and RPE.
- **On an off day:** weighted heel prop done? (ask directly) · bike minutes and distance.
- **On an add-on day:** which block · minutes and RPE · main-lift loads · leg up between sets? · anything about the setup the knee noticed.
- **Weekly (Sunday):** body mass, same time · extension photo · SLR lag (one rep) · flexion vs the right.
- **Every PT visit:** any numbers taken (goniometer, dynamometer, 1RM) · anything said verbally · who treated.

## Known tendencies to watch for (updated 10/9)

- **Off days produce little.**
  - Weighted heel prop: 2 home rounds 10/4–10/8 (Tue, Wed) against a twice-daily target. Cut to once a day 10/9 so it can run 7 of 7.
  - Extension held at 2° hyperext anyway (10/8).
- **Upper add-on not happening.**
  - 0 of 2 in the weeks of 9/20 and 9/27.
  - 0 so far in the week of 10/4 (Upper A planned Fri 10/9, Upper B Sat 10/10).
  - Placement moved to its own days at the user's choice (10/5). If it misses again, ask what the actual barrier is before redesigning.
- **Conditioning bike:** first off-day ride Fri 10/9 (15 min, 3.47 mi). The Saturday bike was missed four weeks running through 10/3.
- **Swelling grading improved:** graded trace 10/6–10/9; Sun/Mon 10/4–10/5 not graded.
- **Batches growing in-session:** 5 changes on 9/28, 7 on 9/30, ~12 on 10/6. All produced clean mornings, but the mornings couldn't name a cause. With PT approval no longer a brake, load rule 5 is the main guardrail.
- **First-exposure jumps:**
  - RDL bodyweight → 25 lb DBs (9/30)
  - step-up bodyweight → 25 lb DBs with the band off (10/6)
  - SL sit-to-stand 24" → 18" in one step (10/6)
- **Sessions displaced by time on feet:** Session A was skipped Sun and Mon 10/4–10/5 after 3 h and half a day on feet, though time on feet hasn't changed a morning since 9/26.
- **Reading a good-feeling knee as a strong graft** (load rule 9): the live risk through ~11/16, sharper now that PT approval isn't the brake.

## Weekly checkpoint workflow (every Sunday)

1. **PT day:** paste the PT note into the thread. The dashboard appends it verbatim to ACL_PT_Notes.md, at checkpoint or on request. Verbal instructions relayed in-thread are appended as patient-reported.
2. **Saturday:** daily minimum + bike; evening log as usual.
3. **Sunday morning, before the loading session:**
   - Log the morning reading (graded).
   - Weigh in, take the extension photo, and do the SLR lag and flexion checks.
   - Say **"checkpoint"**. The dashboard reads the current ACL_Daily_Log.csv and ACL_Exercise_Log.csv from project knowledge, appends the week's rows (Sun → Sat) from the thread, and produces:
     - a new `ACL_Recovery_State_<Sunday date>.md` (including an add-on section)
     - updated copies of both CSVs
     - an updated ACL_PT_Notes.md if there was a visit or a relayed instruction
4. **In project knowledge:** replace the previous Recovery State, both CSVs, and PT Notes. Keep this Working Rules file and the Add-On; the dashboard re-issues either one only when its content changes.
5. **Open a new thread** with the kickoff prompt. Its first working message is Sunday's "plan today". The Sunday session and its Monday reading belong to the new week.

**Mid-week updates:** on request, the dashboard brings the logs, PT Notes, and the current Recovery State up to date in place (done 10/8 and 10/9). Sunday still produces the new Recovery State.

The Recovery State is named by the Sunday it was produced and covers the previous Sunday → Saturday.

## Log files (for analytics)

- **ACL_Daily_Log.csv** — one row per day. Columns:
  - session type, knee-session minutes and RPE
  - add-on session with minutes and RPE
  - floor done
  - swelling (grade + trend)
  - pain (AM / session / PM)
  - extension, flexion
  - catch/sticking, crutches
  - hours on feet, gym minutes on feet
  - gait notes, body mass (weekly)
  - adjuncts, notes

  Details:
  - Empty cell = not logged that day.
  - Session load = RPE × minutes, computed from the columns rather than stored.
  - `loaded_day` values: `Y` / `N` / `N (partial)`.
  - From 10/9, `floor_done` means the daily minimum (one weighted heel prop).
  - Conditioning rides go in `notes` and in the exercise log.
  - Corrected 10/4: `postop_week` for 9/15–9/17 set to 4.
- **ACL_Exercise_Log.csv** — one row per exercise instance: date, session, block, exercise, side, sets, reps, hold/duration, load or band, assist level, notes.
  - `session` values: `home` / `PT` / `HEP` / `floor` for the knee · `conditioning` for off-day bike rides (from 10/9) · `upperA` / `upperB` / `accessory` / `power` / `arms` for the add-on.
  - Right-leg mirrored sets are logged as knee-session rows with side `R`.
  - Add-on logging: main lifts in full; accessories as a single "as written" row unless something changed.
  - Corrected 10/4: the 9/18 single-leg leg press load is 40 lb.
- Both logs carry `dash_week_start` (the Sunday date) for weekly grouping; the daily log carries `postop_week` separately.
- Daily chat logs stay conversational; the dashboard converts them to rows at the Sunday checkpoint or on request. Log doses, loads, band colors, step and seat heights, minutes, RPE, and any on-the-fly changes in chat so the rows are complete.
- Measurement anchors (goniometer, dynamometer, 1RM) come from PT notes; home readings are marked "(self)" or "(est)".
