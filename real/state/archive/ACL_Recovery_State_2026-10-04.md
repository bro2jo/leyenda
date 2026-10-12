# ACL Recovery State — Sun 2026-10-04 · revised Fri 2026-10-09 (POD 46, post-op week 7)

*The current program and where things stand, present tense only. The dashboard's ten sections are kept, so the Working Rules' references ("ladders live in the Recovery State, section 6") still hold; sections 2, 4 and 8 point to where that history lives in this repo.*

- **Program set:** Sun 2026-10-04 checkpoint, revised Fri 10/9: PT 9 (10/8) folded in, Nick's 10/9 instruction, A/B alternation, upper body on its own days, the daily minimum cut to one weighted heel prop.
- **Last reviewed:** Fri 2026-10-09, ingested from the dashboard. As uploaded: `real/state/archive/ACL_Recovery_State_2026-10-04_rev10-09_dashboard.md`. The 10/4 version: `real/state/archive/ACL_Recovery_State_2026-10-04_v10-04.md`.
- **Next:** the 10/11 checkpoint writes `ACL_Recovery_State_2026-10-11.md` and moves this file to `real/state/archive/`.
- **Source priority:** latest PT/surgeon instruction (`real/visits/`) → rehab master plan → this file and the Working Rules (`real/plan/ACL_Working_Rules.md`) → Whole-Athlete Add-On → logs → general ACL knowledge.

---

## 1. Fixed facts

- **Surgery:** 2026-08-24 — LEFT isolated ACL reconstruction, patellar tendon autograft. No meniscus, cartilage, or other procedures. The plan applies unmodified.
- **Injury:** 2026-07-14. Prehab from 2026-07-22.
- **Surgeon (9/25):** no brace; no crutches; very pleased with flexion and extension; **ramp up strength as long as the knee stays quiet**.
- **PT:** Cleveland Clinic Rehabilitation & Sports Therapy.
  - Nick Immel PT oversees and treated 10/8; Cody Rardon PTA treats.
  - Weekly, usually Fridays; 10/1 and 10/8 were both Thursday reschedules.
  - **Next visit: not set. Usual slot ~Thu 10/15 or Fri 10/16 — confirm.**
  - **Nick (10/9): progression is up to the master plan; his approval isn't needed; don't push through pain.**
- **Right-knee reference (pre-op):** extension 0° AROM (hyperextension on a heel prop never measured), flexion 144°, quad 83.7 lb, hamstring 79 lb. **83.7 / 79 lb are the strength targets.**
- **Left pre-op:** extension −1°, flexion 144°, quad 58.9 lb (LSI 70.4%), hamstring 55.8 lb (LSI 70.6%).
- **Strength testing:** single-leg leg press 1RM (10/8): R 14 plates / L 9 plates = 64%. It is a whole-leg test, not a quad test. **No post-op dynamometer in five visits.**
- **Calendar:**
  - Post-op week n = POD 7n−6 to 7n (Tue → Mon). Week 7 = Tue 10/6 – Mon 10/12; week 8 starts Tue 10/13.
  - Phase 4 earliest by calendar: week 9, Tue 10/20 (POD 57).
  - **The graft's weakest window (~weeks 6–12) runs now through ~Mon 11/16 (POD 84).**

---

## 2. Current reading

*Not kept here. Each morning is in `real/logs/daily_log.csv` (`python3 engine/darrow.py today`); the plan for the next few days is in `real/NOW.md`.*

---

## 3. Phase status — **Phase 3 (weeks 6–8), entered POD 34 (Sun 9/27)**

### Phase 3 exit gates (= the plan's "Before Phase 4" checklist; review week of 10/18)

| Criterion | Status | Evidence |
|---|---|---|
| Full/symmetric ROM | **Met** | Extension 2° hyperext AROM on 10/8, the third clinic reading at 2° (9/11, 10/1); the right was 0° AROM pre-op. Flexion 146° (9/25, 10/8) vs the right's 144°. One refinement left: the right knee's passive hyperextension on a heel prop is unmeasured (weekly photo; ask the clinic) |
| Normal gait | **Met** | Nick 10/8: good pattern, equal weight bearing, no device, no brace |
| Minimal/no post-exercise effusion | **Met** | Trace on every graded morning 10/6–10/9, including after the ~12-change home session (10/6) and the hardest PT session (10/8) |
| No post-exercise pain flare | **Met** | Pain ≤2 in every session; no flare since 9/11–12 |
| **Quad LSI ≥70%** | **Unmeasured** | The SL leg press 1RM (64%) is whole-leg, so the hip and calf can cover for the quad; it is not one of the plan's tests (isokinetic, handheld dynamometer, knee-extension machine). Target ≈58.6 lb on the left vs 83.7 on the right, or vs the right retested |
| Good step-down / single-leg control | **Probably met** | 12" step-up with knee drive (PT), unassisted split squat, SL sit-to-stand 18". Forward 6" step-down not done since 10/1 ("still challenging" then); Session B 10/11 shows it |
| Balance / joint-position control | **Met** | BOSU + ball toss 3 × 45 s; eyes-closed stance (PT 10/8) |

**Phase 4 waits on one thing: the quad test.** Everything else is met or will be shown Sunday.

---

## 4. Measurements log

*Not kept here. Instrument numbers: `real/logs/measurements.csv` (`python3 engine/darrow.py measures`). Daily self-checks (swelling grade and trend, pain, extension, flexion, catch): `real/logs/daily_log.csv` (`python3 engine/darrow.py show daily DATE`).*

---

## 5. Latest PT and surgeon instructions

- **Nick 10/9 (patient-reported):** progression is up to the master plan; his approval isn't needed; don't push through pain.
- **PT 10/8 (visit 9, Nick, written note):**
  - upright bike L5 6'
  - SL leg press 1RM test
  - leg press L only, 6 plates
  - standing double-leg heel raise, 35# DBs, 2 × 15
  - standing bird dog, 8# KB, 2 × 15
  - **12" step-up with opposite knee drive, 2 × 15 L**
  - multi-hip abduction / extension / flexion (knee straight), 4 plates, 2 × 15, alternating
  - eyes-closed double-leg stance, 1' each way
- **Nick 10/8 (patient-reported):** keep progressing; add today's items alongside the master plan; well-balanced sessions that are challenging and progressing.
- **PT 10/1 items (in force):** wall squat · heel tap slow eccentric · forward step-down 6" · isometric knee extension at 90° · weighted heel prop · step hamstring stretch.
- **Surgeon 9/25:** no crutches; ramp up strength while the knee stays quiet.
- **Earlier PT verbal (in force):** painless catch is normal · 18" sit-to-stand OK pain-free · bodyweight/DB substitutes for machine items.
- **No longer held for the PT (Nick 10/9):**
  - seated knee extension 90°→45° (plan Phase 3)
  - heel prop weight
  - wall squat depth
  - isometric angles
  - NMES (dropped)
  - loaded bridge and slow-eccentric tempo (plan-variable progressions)
- **Still through the PT / clinic:**
  - **quad strength test, both sides**
  - impact prep and drop jumps (plan: "when appropriately cleared")
  - running (plan: "rehabilitation team agrees")
  - BFR, Spanish squat, seated rotational throws (not in the plan)

*The questions for the next visit are in `real/NOW.md`.*

---

## 6. Current program — Phase 3 (revised 10/9)

### Weekly rhythm (Sun → Sat)

| Day | Knee | Around it |
|---|---|---|
| Sun | Knee session (next in the A/B rotation) | — |
| Mon | — | Bike → Upper A |
| Tue or Wed | Knee session | — |
| Thu | — | Bike → Upper B |
| Fri | PT | — |
| Sat | — | Bike |

- Every day: the daily minimum.
- Sessions alternate **A → B → A** regardless of day. Three loaded days, none back-to-back by design.
- **Next:** Sun 10/11 **Session B** → Tue/Wed **Session A** → PT (confirm day) → Sun 10/18 Session B.

### Daily minimum — every day

- **Morning check (~30 s):** swelling grade · extension side by side · pain · catch.
- **Weighted heel prop:** 10 lb, 10 min, once a day. Weight on the lower thigh, never on the kneecap; quad relaxed.
  - Stops being daily once the side-view photo shows the left as straight as the right; then it's a weekly check.
  - Upper-set rests with the leg up count as extra minutes.
- **Dropped 10/9:** NMES, quad sets, heel slides, SLR, patellar glides, routine compression. The plan uses them for poor activation and early ROM; both are resolved.
- **Weekly (Sunday):** SLR lag (one rep) · flexion (one heel slide vs the right) · extension photo · body mass.
- **Optional:** Game Ready after big sessions · step hamstring stretch · posture drills.

### Progression rules (full text: Working Rules, load rules 3–7)

- **Pain:** 0–2 fine · 3–4 hold that exercise, don't progress · ≥5 reduce or stop. Front-of-knee pain is watched most closely. Never push through pain.
- **Effort:** every working set ends with **2–3 clean reps left (RPE 7–8)** once that exercise has produced a clean morning at its current dose. New items and new loads start at 3–4 in reserve. Never to failure.
- **Mechanics end the set before effort does:** knee drifting in, hip dropping, rushed lowering.
- **One change per exercise per session,** made on the last set, only if the earlier sets were clean.
- **Load steps:** one DB increment or ≤10%. No first-exposure jumps.
- **One new exercise per session,** bodyweight or lightest load first.
- A morning that isn't clean reverses **every** change from the previous session.

### Session A — knee dominant (next: Tue 10/13 or Wed 10/14)

Doses below are the last clean dose (10/6, clean morning 10/7). "Next" = the one change for the next session.

| # | Exercise | Dose next | Ladder — one step per session [plan Phase 3 target] |
|---|---|---|---|
| WU | Bike · TKE red (optional) | 8 min · 2 × 15 | — |
| 1 | SL sit-to-stand, 18" (leg-press slot) | L 2 × 12, slight R-foot assist → **no assist on the last set** · R 2 × 12 | no assist → 3 × 10 → 3 × 12 → DB in hand [3 × 8–12] |
| 2 | Step-up, 12" with opposite knee drive (PT 10/8) | L 2 × 15 · R 2 × 15, bodyweight. Needs a 12" step (confirm). Fallback: 8", 3 × 10 @ 25 lb DBs | 3 × 12 → DBs at 12" [3 × 8–10] |
| 3 | Split squat, unassisted | 2 × 8/side, bodyweight → **3 × 8** | DBs, +5 lb steps [3 × 8–10] |
| 4 | **Seated knee extension 90° → 45° — NEW** (plan Phase 3) | L 2 × 15, slow tempo, RPE 5–6 · R 2 × 15. Band anchored behind the bench leg or an ankle weight (confirm). Range stops at 45° | 3 × 15 → 3 × 20 → more load [2–3 × 15–20, RPE 5–7]. Front-of-knee pain >2 → shorten the range or lighten |
| 5 | Isometric knee extension 90°, strap (PT 10/1) | L 10 × 10 s, max effort | add 60° (plan: ~60° and 90°) |
| 6 | Heel tap, 5", slow eccentric (PT 10/1) | L 2 × 10 | 3 × 10 → 6" (height rule) |
| 7 | Wall squat (PT 10/1) | 2 × 10, no deeper than the SL sit-to-stand | 3 × 10 → depth (plan decision, pain-free) |
| 8 | Standing heel raise, 35 lb DBs (PT 10/8) | 2 × 15 | 3 × 15 → single-leg L bodyweight → single-leg + DB [3–4 × 10–15] |
| 9 | SL balance + ball toss on BOSU · eyes-closed double-leg stance (PT 10/8) | 3 × 45 s · 1 min each way | + perturbation (partner nudge, off-center tosses) |

- **Next session's batch:** knee extension (new) · SL sit-to-stand assist off · split squat third set · step-up to 12" with knee drive (PT dose) · heel raise 35 lb (PT dose) · eyes-closed stance (PT dose).
- **Short on time:** drop 9 → 8 → 7 → 6 → 3.
- **Minimum session:** warm-up + 1, 2, 4, 5 (~30 min).

### Session B — posterior / single-leg (next: Sun 10/11)

| # | Exercise | Dose next | Ladder [plan Phase 3 target] |
|---|---|---|---|
| WU | Bike | 8 min | — |
| 1 | Forward step-down, 6" (PT 10/1) | L 2 × 10, first time at home (PT dose) | 3 × 10 → 7" → 8" (height rule) [3 × 8–10] |
| 2 | SL sit-to-stand, 18" | same dose as Session A | same ladder |
| 3 | RDL, DBs | 3 × 10 @ 25 lb/hand (third set = the one change) | +5 lb/hand steps; slow-eccentric tempo is an option as its one change [3 × 8–12] |
| 4 | Lateral lunge — **NEW** | 2 × 8/side, short range, bodyweight | 3 × 8 → full range [3 × 8 each direction] |
| 5 | Standing hamstring curl, band | 3 × 10 L · R 3 × 10 | heavier band → 3 × 15 [3 × 10–15] |
| 6 | SL bridge | 3 × 8 each side | 3 × 10 → 3 s hold → load (in-plan from 10/9) |
| 7 | Standing band hip 4-way, band at the ankle (PT 10/8 multi-hip + plan adduction) | abduction · adduction · extension · flexion (knee straight), 2 × 15 each side, alternating | 3 × 15 → heavier band [2–3 × 10–15] |
| 8 | Standing bird dog, 8 lb (PT 10/8) | 2 × 15 | — |
| 9 | SL balance + ball toss on BOSU · eyes-closed double-leg stance | 3 × 45 s · 1 min each way | + perturbation |
| CD | Step hamstring stretch (optional) | 2 × 30 s | — |

- **Batch 10/11:** lateral lunge (new) · forward step-down first time at home (PT dose) · RDL third set · hip 4-way and bird dog at home (PT dose) · eyes-closed stance.
- **Short on time:** drop 9 → 8 → 7 → 5.
- **Minimum session:** warm-up + 1, 2, 3 (~25 min).

### Machine items

| Where | Items |
|---|---|
| Clinic | SL leg press 55# 2 × 10 (10/1) · 6 plates (10/8) · 1RM R 14 / L 9 plates · leg curl 47.5# · multi-hip 4 plates |
| Home | SL sit-to-stand · band curl · strap isometric · seated knee extension with band or ankle weight · standing band hip 4-way |

### Conditioning (plan Phase 3: low impact, 3–5 days a week, 15–30 min)

- Bike easy, legs only: Mon, Thu, Sat and any other off day.
- **Ladder:** 15 (Fri 10/9, 3.47 mi) → **18 (Sat)** → 21 → 24 → 27 → 30, +3 min per ride. Distance logged.
- Hard intervals stay arms-only.

### Pre-session check

Swelling **graded** and not up vs the previous morning · extension side by side · pain ≤2 · no hard or painful catch. Fail → last clean doses, 2 sets, no changes.

**Own adjuncts (logged, not evaluated):** Game Ready / Go Ready, LLLT, red light, sauna (9/27, 9/30, 10/8 — no swelling change after any). Ibuprofen masks the morning feel.

---

## 7. Whole-Athlete Add-On (revised 10/9)

| | |
|---|---|
| **Placement** | Own days (user's choice, 10/5): Upper A Mon, Upper B Thu, after the bike. This week: **Fri 10/9 Upper A, Sat 10/10 Upper B** |
| **Block** | Block 0 re-entry, weeks of 10/4 and 10/11: 3 sets on main lifts, RPE 6 the first time, then 7; seated or lying for the first two sessions. Block 1 from 10/18 if 2 of 2 ran in both weeks |
| **Ran so far** | 0 since the add-on began 9/20 (three straight weeks; first planned today) |
| **Standing upper work** | From the third upper session: pull-ups with a box, half-kneeling with the right knee down, standing landmine press, standing Pallof |
| **Right leg** | Mirrors the left's single-leg strength work inside the knee sessions, including the new seated knee extension |
| **Saturday power & mobility** | Earliest Sat 10/17, after two weeks of 2 of 2; seated throws need the PT's OK |
| **Still open** | Prehab overhead screen result (decides Upper B's seated DB press; until then a second incline press) · body-mass baseline (Sun 10/11) |

---

## 8. Week in review

*Not kept here. Each week's review is `real/checkpoints/<Sunday>.md`. The dashboard's review of Sun 10/4 → Fri 10/9 AM is §8 of the archived 10/9 file; the 10/11 checkpoint folds it in.*

---

## 9. Patterns and concerns (carry forward)

1. **Joint tolerance is high and still rising.** A ~12-change home batch and, two days later, the hardest PT session to date: trace both mornings. Swelling reached trace this week and no longer tracks load or hours on feet.
2. **Quad strength is the only unmeasured gate and the real constraint.**
   - The SL leg press (64%, whole-leg) is the first post-op strength number, but it isn't decisive.
   - Session A now gets the plan's seated knee extension 90°→45°, the most direct quad tool.
   - The clinic test is the one thing to ask for.
3. **Extension:** 2° hyperext at three clinic readings. It held through a week with only two home heel-prop rounds. One round a day is maintenance; the remaining target is the right knee's passive hyperextension.
4. **Off-day work stays thin.** Heel prop 2 rounds in 5 days; the first conditioning ride was Friday; upper is at zero for the third straight week. The daily minimum is cut to one 10-minute heel prop so it can run 7 of 7.
5. **Sessions displaced by time on feet** (10/4, 10/5). The knee no longer needs that caution: five clean mornings after big on-feet days.
6. **Batch growth and first-exposure jumps** (9/30 RDL; 10/6 step-up DBs, SL sit-to-stand 18"). The knee tolerated them; the cost is attribution. With PT approval no longer a brake, one change per exercise is the main guardrail.
7. **Graft weak window through ~11/16.** A quiet knee is what this window feels like. Strength ramps; impact, running, rotation, and pivoting stay behind the plan's gates.
8. **Posterior-knee tightness** (9/30) not reported since. If it ever becomes calf pain or calf swelling: surgeon, not dashboard.

---

## 10. Next milestones

- [ ] Daily minimum **7 of 7** (morning grade + one heel prop)
- [ ] Upper **2 of 2** this week (Fri, Sat) and next (Mon, Thu)
- [ ] Bike 3+ rides a week, +3 min per ride toward 30
- [ ] **Sun 10/11:**
  - [ ] first weigh-in, first extension photo, SLR lag, flexion check
  - [ ] Session B: forward step-down at home (the single-leg control gate), lateral lunge (new)
- [ ] **Next Session A:** seated knee extension 90°→45° (new). Confirm the equipment (band or ankle weight) and a 12" step
- [ ] **Quad test, both sides,** booked at the next visit
- [ ] **Phase 3 gate review, week of 10/18.** Phase 4 earliest Tue 10/20; quad LSI is the only open gate
