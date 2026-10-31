# ACL Recovery State — Sun 2026-10-18 (POD 55, post-op week 8) — revised Wed 10/21 (POD 58, week 9), Tue 10/27 (POD 64, week 10) and Wed 10/28 (POD 65, week 10)

*The current program and where things stand, present tense only. Rules live in the Working Rules, the add-on design in the Add-On, the PT's words in `real/visits/pt_notes.md`; `real/README.md` says where each fact lives. Sections 2, 4 and 8 point to where that history lives in this repo.*

- **Program set:** Sun 2026-10-18 checkpoint (written Sat 10/17 evening, on request; Sunday morning's checks folded in 10/18 AM: the heel prop becomes a weekly check). The Phase 3 → 4 gate is met (PT 11, 10/17); Phase 4 opened Tue 10/20 (Knot III) and Session A became the plan's Phase 4 Session A from that day.
- **Revised in place Wed 10/21 (folded in here Thu 10/22, `/ingest`):** Sunday's Session B and Monday's Upper B recorded; Session A moved Tue → Wed and run as the master plan's Phase 4 A; **10/21 recalibration**: that session's loads became the Session A baselines (§6); PT asked for Friday. Later the same day, the **knee-session review** (redundant items cut, items with a reason kept, four oversights fixed: §6) and the **upper and add-on review** (§7); the Working Rules and the Add-On were re-issued (their revision histories, 10/21).
- **Last reviewed:** Tue 2026-10-27 (the checkpoint for Sun 10/25, written late: Sat 10/24 – Mon 10/26 away, no training; `real/checkpoints/2026-10-25.md`). Doses unchanged; the week's days, Block 1, the PT list and the patterns revised in place.
- **Revised in place Wed 10/28 (from the dashboard's correction, `/ingest`):** Nick's 10/28 instruction (patient-reported, `pt_notes.md`): the plan's criteria and minimum times decide, impact included; the drop vertical jump cleared on its criteria. So: **impact prep onto the home program** (§6, from today's Session A) · **the single-leg squat test runs at home**, filmed, today and then Sundays until it passes · **the left knee extension off the 40 lb hold** (the plan's Phase 4 dose) · the drop vertical jump placed in the sequence · Tuesday's Upper B (Block 1, session 6) recorded with the next B's doses (§7). The Working Rules' clearance list corrected the same day.
- **Supersedes:** `real/state/archive/recovery_state_2026-10-11.md`.
- **Next:** the Sun 11/1 checkpoint (the first week with impact prep and the single-leg squat test).
- **Source priority:** latest PT/surgeon instruction (`pt_notes.md`) → rehab master plan → this file and the Working Rules → Whole-Athlete Add-On → sport plan → logs → general ACL knowledge.

---

## 1. Fixed facts

- **Surgery:** 2026-08-24 — LEFT isolated ACL reconstruction, patellar tendon autograft. No meniscus, cartilage, or other procedures. The plan applies unmodified.
- **Injury:** 2026-07-14. Clinic prehab from 2026-07-22.
- **Sport:** a combination of ultimate, court, and field sports. Disc throwing (ultimate, handler) runs on the sport plan, `sport_plan.md`; what the knee allows and where throwing sits in the week is the Add-On §3: days without a knee session, feet planted or slight pivots on the planted foot (Cody 10/15), the step-out with the PT's OK.
- **Surgeon (9/25):** no brace; no crutches; very pleased with flexion and extension; ramp up strength as long as the knee stays quiet.
- **PT:** Cleveland Clinic Rehabilitation & Sports Therapy.
  - Nick Immel PT oversees (treated 10/8; ran the quad test 10/17, his account). Cody Rardon PTA treats (10/15). Who treated 10/1: not recorded.
  - Weekly; the last three visits were Thursdays (10/1, 10/8, 10/15), the quad test Sat 10/17.
  - **Next visit: Wed 11/4** (Wed 10/28's was cancelled).
  - **Nick (10/9): progression is up to the master plan; his approval isn't needed; don't push through pain. Nick (10/28): the plan's criteria and minimum times decide, impact included; the drop vertical jump is cleared once its criteria are met.**
- **Strength references:**
  - Right pre-op: quad 83.7 lb, hamstring 79 lb, extension 0° AROM, flexion 144°.
  - Left pre-op: quad 58.9 lb (LSI 70.4%), hamstring 55.8 lb (LSI 70.6%), extension −1°, flexion 144°.
  - **PT 11 (10/17), isometric quad peak on a torque monitor:** R 77.2 lb, L 69.8 lb (best of two rounds), **LSI 90.4%**; vs the right's pre-op 83.7 lb, 83.4%. The right is 7.8% below its own pre-op number. Hamstrings not yet tested.
- **Body mass:** **starting weight 154.0 lb, Mon 9/28, 8:30 am fasted** (the nutrition guide's start; pre-injury 164, goal lean ~170; the guide's steps 154 → 160 → 164 → ~170). Weekly averages since: 155.2 (wk of 9/27, 2 readings) · 156.1 (10/4, 3) · 157.2 (10/11, 7) · 157.6 (10/18, 2) · 160.3 (10/25, 3 so far, salt-heavy days). 158.4 lb, Sun 10/18 morning, is the first Sunday-morning reading; the 10/11 reading (159.8) was a 5:30 PM weight, so readings are mornings from there. Weigh in Sunday mornings; the weekly average is the trend. Nutrition targets: `real/config.json → nutrition_targets` (3,000 kcal, 150–160 g protein; the Add-On's 1.6–2.0 g/kg is 115–145 g).
- **Calendar:**
  - Post-op week 8 ended Mon 10/19; **week 9 = Tue 10/20 – Mon 10/26: Phase 4; Knot III tied Tue 10/20 (POD 57).**
  - Phase 4 = weeks 9–12, through Mon 11/16 (POD 84). **That is also the end of the graft's weakest window (~weeks 6–12).**
  - Running: earliest week 13 (Tue 11/17, POD 85), and only with its gate met and the rehab team's agreement.
- **Home equipment:**
  - Have: power rack and barbell with a cable system and ankle attachments; DBs **to 52.5 lb** (10/31: not buying heavier; past 52.5 a lift moves to the barbell, §6 "Dumbbells at their top"); benches including incline; bands; air bike; BOSU; boxes and steps (6.5", 7.5", 8", 12", 18"–24" seats); 10 lb weight for the heel prop; strap; 8 lb med ball.
  - Don't have: leg press, leg curl, or knee-extension machine; wobble board.

---

## 2. Current reading

*Not kept here. Each morning is in `real/logs/daily_log.csv` (`python3 engine/darrow.py today`); what stands this week is in `real/NOW.md`. Every graded morning 10/6–10/21 was trace, including after PT 11's max-effort quad test, Sunday's 110-minute B and Wednesday's recalibrated A; Thu 10/22: none, down from trace, extension good, wellness 5.*

---

## 3. Phase status — **Phase 4 (weeks 9–12), entered POD 57 (Tue 10/20)**

### Phase 3 exit gates (= the plan's "Before Phase 4" checklist): **all met, Sat 10/17**

| Criterion | Status | Evidence |
|---|---|---|
| Full/symmetric ROM | **Met** | 2° hyperext AROM at three clinic readings; extension photo passes 10/18; flexion 146° vs the right's 144°. Home, Sun 10/18 (self): SLR without lag; flexion near full |
| Normal gait | **Met** | Nick 10/8; Cody 10/15 "no deviations" |
| Minimal/no post-exercise effusion | **Met** | Trace on every graded morning since 10/6 |
| No post-exercise pain flare | **Met** | None since 9/11–12 |
| Quad LSI ≥70% | **Met: 90.4%** | 10/17 dynamometer: L 69.8 / R 77.2 lb; 83.4% vs the pre-op right |
| Good step-down / single-leg control | **Met** | Nick 10/17: step-downs passed |
| Balance / joint-position control | **Met** | BOSU + ball toss; eyes-closed wobble board (PT) |

**Knot III tied Tue 10/20** (the plan's earliest date, week 9) on this evidence; `rehab.current_phase` is 4 and the next gate is Phase 4's exit (below).

### Phase 4 exit = the plan's "Before Running" gate (the next gate)

| Criterion | Status | Evidence / next step |
|---|---|---|
| Full extension | **Met** | Photo 10/18; 2° hyperext at the clinic |
| Flexion ≥95% of the right | **Met** | 146° vs 144° |
| No or trace effusion | **Met** | Trace every graded morning; none on 10/22 |
| Normal gait | **Met** | — |
| Quad LSI >80% | **Met on 10/17** | 90.4%, or 83.4% vs the pre-op right. Retest ~week 12 (plan: every 3–5 weeks) |
| Hamstring LSI ≥80% | **Unmeasured** | Pre-op 70.6%. Ask for the test at the next visit |
| Glute med/max ≥80% | **Unmeasured** | Pre-op hip 5/5 was a manual test, not a symmetry number. Slight left hip drop at the bottom of the 6.5" step-down (10/18). Ask at the next visit |
| 10 controlled single-leg squats to ~60° | **First test Wed 10/28** | At home, filmed, judged on the plan's checklist (§6); Sundays until it passes. Single-leg control is the soft spot (§9, item 6) |
| Pain-free low-level impact prep | **Started Wed 10/28** | At home, the plan's sequence from small double-leg pogos (§6); Nick 10/28 |
| Good landing mechanics | Not yet | Judged on the low vertical jump and landing, then the drop vertical jump (§6; cleared by Nick 10/28 once the rungs before it are clean) |
| Rehabilitation team agrees | — | — |
| Minimum time | Week 13+ (from Tue 11/17) | — |

**Phase 4 work:** heavier strength (main lifts toward RPE 7–8, 60–85% of estimated 1RM), single-leg mechanics, and early impact prep on the plan's own start criteria ("when basic strength, control, and knee response permit"): small double-leg pogos → snap-downs → low jump and landing → the drop vertical jump (§6). The plan's first rung, leg-press or shuttle jumps, has no home equipment.

---

## 4. Measurements log

*Not kept here. Instrument numbers (pre-op, 9/11, 9/25, 10/1, 10/8, 10/17): `real/logs/measurements.csv` (`python3 engine/darrow.py measures`). Daily self-checks (swelling grade and trend, pain, extension, flexion, catch, wellness) and session minutes and RPE: `real/logs/daily_log.csv` (`python3 engine/darrow.py show daily DATE`). Session loads (RPE × minutes) are computed from the columns, never stored.*

---

## 5. PT and surgeon instructions in force

- **Nick 10/28 (patient-reported, no visit):** the master plan is good; go with it, as long as the criteria and the times match the plan. **The drop vertical jump is cleared** if the plan asks for it and the other criteria to unlock it are met. Read as: the plan's criteria and minimum times decide when something starts, impact included; where the plan waits for a criterion or a week, the wait stands. Reconfirm at 11/4.
- **Cody 10/28 (patient-reported):** this week's visit cancelled; keep progressing and get further into it.
- **Nick 10/17 (patient-reported):** step-downs passed · **Copenhagen on both sides OK** (read as the short-lever version done 10/17; the long lever isn't covered) · hamstrings not tested ("should be about the same").
- **Cody 10/15 (patient-reported):**
  - Step-up at 12" or 18" is fine.
  - **Pivots OK "within reason."** Applied to slight pivots on the planted foot in disc throwing. Step-out throws, throwing on the move, marking, cutting and rotational drills wait until the PT clears the specific drill (Add-On §3).
  - Knee extension full range, both legs up, left alone down (clinic 10 lb). Range and load now follow the plan's Phase 4 dose (Nick 10/28).
- **Nick 10/9:** progression is up to the master plan; no approval needed; don't push through pain.
- **Nick 10/8:** keep progressing; add the PT's items alongside the master plan; well-balanced sessions that are challenging and progressing.
- **Surgeon 9/25:** no crutches; ramp up strength while the knee stays quiet.
- **Earlier PT verbal:** painless catch is normal · 18" two-leg sit-to-stand OK pain-free · bodyweight/DB/cable substitutes for machine items.

**PT-introduced items (in-plan):**

| Date | Items |
|---|---|
| 10/1 | Wall squat · heel tap slow eccentric · forward step-down 6" · isometric knee extension 90° · weighted heel prop · step hamstring stretch |
| 10/8 | 12" step-up with opposite knee drive · standing heel raise 35# DBs · standing bird dog 8# · multi-hip abduction / extension / flexion · eyes-closed double-leg stance on a wobble board · bike level 5 |
| 10/15 | Cable TKE 3.5 plates · goblet squat 15 → 25 lb · heel tap 6" · forward lunge 2 × 10/side · banded backward walk 2 × 5 · knee extension full range, two up / left down, 10 lb · single-leg leg curl 25 → 32.5 lb · SL leg press 70 lb |
| 10/17 | Copenhagen, both sides (short lever) |

**Still through the PT / clinic:**
- running (week 13 at the earliest, and the rehabilitation team agrees)
- hamstring and glute strength tests (the clinic's equipment)
- step-out throws, throwing on the move, marking
- BFR, Spanish squat, seated rotational throws (not in the plan)

**No longer through the PT (Nick 10/28):** impact prep (the plan's Phase 4 sequence, at home) · the single-leg squat test (at home, filmed) · the drop vertical jump, once the rungs before it are clean · the left knee extension's range and load (the plan's Phase 4 dose).

### For the next visit (the one list)

1. **Wed 11/4** (scheduled; 10/28's visit was cancelled: `pt_notes.md`, 2026-10-28, Cody's and Nick's entries). Keep a day between it and the nearest home session.
2. **Hamstring test, both sides.** The before-running gate needs ≥80%; pre-op was 70.6%. **Glute med/max too**, and mention the slight left hip drop at the bottom of the 6.5" step-down (10/18). Unmeasured, these are the likeliest thing holding 11/17.
3. **Reconfirm Nick's 10/28 words** (relayed): the plan's criteria and times govern, impact included; the drop vertical jump cleared on its criteria. Show where the impact ladder stands and the single-leg squat video.
4. **Throwing:** are step-out throws OK yet, and does the pivot foot matter? (Right-handed, so the conventional pivot is the left foot: the surgical knee.)
5. The written note from 10/17 (device, knee angle), so the numbers are on record.
6. If wanted: BFR · Spanish squat · seated rotational med-ball throws.
7. Still from the repo's list: the right knee's hyperextension measured on a heel prop (the extension target until the clinic measures it) · who treated 10/1.

---

## 6. Current program — Phase 4

### This week (Sun 10/25 → Sat 10/31)

Last week in one line: loaded days 3 of 3 (Sun B, Wed A, **Fri B in the PT slot**, at a vacation gym), upper 2 of 2, bike 2 of 3, throwing 1 of 2, mornings 6 of 7; Sat 10/24 – Mon 10/26 away with no training, no checks, creatine 1 of 3 (`real/checkpoints/2026-10-25.md`). Nothing reverses, nothing is repaid: every session resumes at its last clean dose with one change.

| Day | Plan |
|---|---|
| Sun 10/25 | Away: nothing (the weekly checks and Session B did not run) |
| Mon 10/26 | Travel day: nothing (creatine ✓) |
| Tue 10/27 | ✓ 160.7 lb · morning check (trace) · bike 30 ✓ · **Upper B, session 6: Block 1's first** ✓ (~60 min, RPE 7; §7) · throwing, the finisher and the Copenhagen not done |
| Wed 10/28 | ✓ 159.2 lb · **PT cancelled** (next Wed 11/4) → morning check → **the single-leg squat test first**, fresh and filmed (§6, impact and the SL squat test) → bike 8 → ball toss → **pogos 2 × 5**, quiet (first impact) → **Session A** in the PT's place (goblet 40 × 3 × 10 · knee extension 40 × 3 × 12 both legs · RFESS 3 × 8 · hamstring curl 70 × 3 × 10 with heel raise 40s × 4 × 15 · step-up 2 × 10 · lateral heel tap 3 × 10 · full cooldown) |
| Thu 10/29 | ✓ 161.0 lb · morning check (trace, pain 0, wellness 5: **clean after Wednesday's hops**) · creatine ✓ · **bike, throwing and Upper A not done** (a long day, very tired; his call: sleep). Missed, not repaid (load rule 10; Add-On rule 4) |
| Fri 10/30 | Morning check → **Session B** (the 10/25 column below) with the impact block: one change from Wednesday's if Thursday was clean |
| Sat 10/31 | Morning check → bike 30 → throwing → **Upper A, session 7** (Block 1; §7; back on Saturday by his call 10/29, as the 10/27 plan had it: 4 days after Tuesday's B, 2 before Monday's) → finisher with the Copenhagen 2 × 25 s. Saturday power & mobility waits for the next free Saturday |
| Sun 11/1 | Weekly checks (morning weigh-in, photo + heel prop, SLR, flexion, **the single-leg squat test**) → checkpoint → **Session A** (one change from Wednesday's, the impact block included) |

- **Two loaded days this week** (Wed A, Fri B), with the PT visit cancelled; the weekend away stays unpaid (load rule 10).

- **Throwing:** never on a knee day (a home session or a PT visit); on upper days after the bike and before lifting; on Saturday after the bike. Feet planted or slight pivots on the planted foot; the pivot foot named in the log (Add-On §3; sport plan §5, §9). Thu and Sat this week (Tuesday's didn't run).
- **The week is judged by** (Working Rules, load rule 10): loaded days 2 this week (Wed A, Fri B; the PT visit cancelled, the weekend away not repaid) · morning checks 7 · bike rides 3 (Tue ✓, Thu, Sat) · upper 2 (Tue B ✓, Sat A: planned Thursday, not run (tired), back on Saturday by his call 10/29) · bike rides 2 of 3 likely (Thursday's not run; not repaid).
- **The remaining off day is rest by default** (Add-On §2): the week's only day without knee or upper work; the optional accessory day can go there (no slot left this week).

### Daily minimum and weekly checks

- **Daily:** the morning check: **swelling grade** · extension side by side · pain · stiffness · catch · wellness 1–5. **This is the whole daily minimum since Sun 10/18.** A missed morning check costs nothing else (Add-On rule 1, 10/21).
- **Weekly (Sunday morning):** weigh-in · extension photo with the weighted heel prop (10 lb × 10 min; weight on the lower thigh, never on the kneecap, quad relaxed) · SLR lag · flexion vs the right · **the single-leg squat test, filmed, until it passes** (below; from Sun 11/1).
- **The heel prop goes back to daily** if a photo or a morning shows the left visibly bent.

### PT items mapped into the home sessions

| PT item | Home slot |
|---|---|
| Goblet squat (10/15) | Squat slot (A) |
| Knee-extension machine, two up / left down, full range (10/15) | Cable knee extension (A) |
| Forward lunge (10/15) | Lunge → RFESS slot (A); **RFESS from 10/21** |
| Step-up with knee drive, 12" (18" permitted) | Step-up (A): bodyweight control drill, no right push-off |
| Heel tap 6" (10/15) | A's eccentric item; **lateral at 7.5" from 10/21** |
| Standing heel raise 35 lb (10/8) | Calf slot (A) |
| 90° isometric (10/1) | The knee extension's fallback (front-of-knee pain >2, or a PT range limit) |
| Cable TKE · banded backward walk (10/15) | Optional in A's warm-up (Working Rules optional extras) |
| Forward step-down (passed 10/17) | Step-down (B) |
| SL leg press (clinic) | SL sit-to-stand (B) |
| Single-leg leg curl (10/15) | Cable hamstring curl (**A and B**) |
| Multi-hip (10/8: abduction, extension, flexion) | **Cable hip abduction (B).** Extension → RDL and bridge; flexion → the step-up's knee drive (A); adduction (the plan's, not the PT's) → Copenhagen (upper-day finisher) |
| Bird dog (10/8) | **Dropped 10/21:** covered by the BOSU work, the bridge, the side plank and the cooldown |
| Eyes-closed wobble board (10/8) | **Dropped 10/30 (his call):** the ball toss carries the balance work |
| Wall squat (10/1) | Replaced by the goblet squat |
| Copenhagen, both sides (10/17) | The upper-day finisher (short lever) |

### Machine substitutes at home

- SL sit-to-stand (leg press)
- Standing cable hamstring curl, ankle strap, facing the stack (leg curl)
- **Cable seated knee extension:** facing away from the stack, low pulley behind, cable under the seat, ankle strap on the left. Both legs up (right foot hooked under the left ankle), left alone down. Fallback: band
- Standing cable hip abduction, ankle strap (multi-hip)
- Banded backward walk: band around the waist, anchored to the rack
- Strap isometric at 90° (the knee extension's fallback)

**Clinic numbers:** SL leg press 55# 2 × 10 (10/1), 6 plates (10/8), 70# 2 × 10 (10/15); 1RM R 14 / L 9 plates · leg curl 47.5# (9/25, 10/1), single-leg 32.5# (10/15) · knee-extension machine 10# two up / left down (10/15) · multi-hip 4 plates · cable TKE 3.5 plates.

### Current depths and heights

| Item | Current |
|---|---|
| SL sit-to-stand | 20" unassisted, 3 × 12 (10/18; the left slightly shaky). 18": the left still needs a slight assist (10/6, 10/13); the 18" seat was unavailable 10/18 |
| Goblet squat | To an 18" box, paused (10/21) |
| Heel tap | Lateral, 7.5" (10/21). PT: forward, 6" (10/15) |
| Forward step-down | 6.5"; slight hip drop at the bottom (10/18); passed at PT 10/17 |
| Step-up | 18", right foot passive (10/21) |
| RFESS rear box | 7.5" (10/21) |
| Impact | Small double-leg pogo, 2 × 5 (from 10/28) |

### Progression rules (Phase 4)

Full text: Working Rules, load rules 3–7.
- **10/21 recalibration (his decision).** The Session A starting doses (mostly the PT's 10/15 doses) were well below capacity, so Wednesday's loads replace them as the baselines: goblet squat 40 lb · knee extension 40 lb · hamstring curl 60–70 lb · heel raise 40s · cable TKE 60 lb · RFESS and lateral heel tap at 7.5". In-plan load progression is his to make (Nick 10/9); this is not a PT clearance. The day itself stays logged as past the plan (the doses as they stood that morning).
  - **Thu 10/22's morning was clean, so the baselines stand.** (Had it not been, every 10/21 change would have reversed to the last clean doses: 10/13 home and the PT's 10/15.)
  - **From here the normal mechanics apply:** one change per exercise per session; ≤10% or one increment.
  - **Left knee extension: off the 40 lb hold (Wed 10/28).** It had waited for the PT; Nick's 10/28 instruction puts it on the plan's Phase 4 dose (2–3 × 8–12 toward RPE 7–8; "progress range and load gradually, if the donor site tolerates"). 10/28: the third set at 40; the next A: +1 plate. **It stays the one exercise whose step is never more than one plate**, whatever the reps in reserve: open-chain extension near straight is the graft's highest-strain position, and the graft is at its weakest through ~11/16.
- **Pain:** 0–2 fine · 3–4 hold · ≥5 reduce or stop. Front of the knee watched most on the knee extension, goblet squat, RFESS, heel tap and step-down.
- **Effort:** Phase 4 main lifts work toward **RPE 7–8 (2–3 reps left)** once clean at a dose. New items and new loads start at 3–4 left. Never to failure.
- **Rep ranges come down as load goes up:** the plan's Phase 4 targets are in brackets in each ladder.
- **Dumbbells at their top (52.5 lb, 10/31):** a lift that outgrows them moves to the barbell at about the same total load, then climbs in +5 lb steps: the RDL now (115 from the next B), the goblet squat after 52.5 (a back squat to the same box, empty bar first), the standing calf raise after single-leg with one 52.5 (a barbell on the back), the seated calf raise (a padded bar across the thighs), the RFESS after 52.5s (a bar on the back in the rack). The hip thrust starts on the barbell. Single-leg work stays on dumbbells while they last: they balance better. The upper lifts have room (row 30, press 25s, chest-supported row 20s); past 52.5 they go to the barbell or the cable.
- **One change per exercise per session · one new exercise per session · load steps ≤10% or one increment.**
- A morning that isn't clean reverses every change.
- **Impact prep is on the home program from Wed 10/28** (below): the plan's dose and the lifts' rule (one change per exercise, one new exercise per session; from 10/30), and the impact block is the first thing reversed when a morning isn't clean (Working Rules, load rule 5).

### Impact preparation and the single-leg squat test (plan Phase 4; from Wed 10/28)

**Why now:** the plan starts early plyometric preparation in Phase 4 "when basic strength, control, and knee response permit," and Nick (10/28) put the plan's criteria and times in charge. Strength: quad LSI 90.4%. Knee response: trace or none on every graded morning since 10/6. Control: step-downs passed 10/17, but single-leg control is the soft spot (the hip drop, the shaky 18" sit-to-stand), so the sequence starts double-leg, at the bottom.

**Where:** knee days only (A and B), after the warm-up's ball toss and before lift 1, fresh. Stop while mechanics are still excellent: landings quiet, knees over the feet, even on both legs.

| Rung | Exercise | Dose | Moves on when |
|---|---|---|---|
| 0 | Leg-press or shuttle jump | No home equipment: skipped | — |
| 1 | **Small double-leg pogo** | **2 × 5 (Wed 10/28)** → 3 × 5 → 3 × 8 | 3 × 8 quiet, with clean mornings after |
| 2 | + Snap-down (the second exercise; the plan's cap is two) | 2 × 5 → 3 × 5 → 3 × 8 | The same |
| 3 | Low vertical jump and landing (in the pogo's place) | 2 × 5 → 3 × 5 | Landings quiet and even, a clean morning after |
| 4 | **Drop vertical jump** | A filmed check, not a ladder: the plan's list (symmetrical loading, controlled knee and hip flexion, no major valgus collapse, stable trunk, quiet landing, no pain or swelling afterward). Box height set when it's due | **Cleared by Nick (10/28)** once rung 3 has run cleanly. Not due before then |
| 5 | **Single-leg pogo**, each leg, small | 2 × 5 (hop, land, reset) → 3 × 5 → 3 × 8 repeated (continuous, quiet) | **The plan's return-to-run gate asks for it** ("pain-free repeated single-leg pogos"), so running waits on this rung. Left control first: the single-leg squat test is the measure |

- **Plan's dose:** 2 exercises · 2–3 sets · 5–8 contacts a set.
- **Pacing (from Fri 10/30, his call: the plan sets no one-change-per-session limit):** the lifts' rule. One change per exercise per session (sets or contacts) and one new rung per session, inside the plan's caps (2 exercises, 2–3 sets, 5–8 contacts a set). A morning that isn't clean reverses the impact block first (back one rung; on rung 1, out until a clean morning), then the session's other changes (load rule 5).
- **Where it lands:** with a clean morning after every knee session, about one rung a session: snap-downs from 10/30, the low jump and landing in the next sessions, then the drop vertical jump and single-leg pogos, with repeated single-leg pogos around mid-November, in time for the run gate (week 13, Tue 11/17).
- **Logged** in the exercise log, `block` = `plyo`: the rung, sets × contacts, and whether the landings were quiet.

**The single-leg squat test** (the plan's Phase 4 test; at home, no further condition):
- **First run Wed 10/28**, before the bike, fresh. Then **every Sunday with the weekly checks until it passes.**
- 10 controlled single-leg squats to at least ~60° knee flexion, left, then the right for comparison; **filmed from the front** (and the side if there's a second phone).
- Judged on the plan's checklist: knee tracks over the foot · pelvis stays controlled · no major trunk compensation · no obvious unloading of the surgical leg · smooth depth and tempo. **Pass = all 10 with every item.**
- Logged as `sl_squat_reps` in `measurements.csv` (controlled reps out of 10, one row per side; method `home video`).

### Session B — next: Fri 10/30 (~60 min; the vacation-gym B of Fri 10/23 had a clean morning after it, his report 10/30, so its doses carry)

Baseline = 10/18 (clean on 10/19), then 10/23 (clean on 10/24). One change per exercise; several exercises change on the same day. Trimmed in the 10/21 review (below Session A).

| # | Exercise | 10/23 (vacation gym) | Next (Fri 10/30) | Ladder [plan Phase 4 target] |
|---|---|---|---|---|
| WU | Bike · BOSU SL balance + ball toss (L) · impact | Bike 8 · ball toss 3 × 45 s | Bike 8 · ball toss 3 × 45 s · **impact: two-leg pogos 3 × 8 + snap-downs 2 × 5 (new)** | Ball toss + perturbation · impact per its ladder (above) |
| 1 | Forward step-down, 6.5", **left only** | ~6" step, L 3 × 10 (hip drop not reported). 10/18: 6.5", slight hip drop at the bottom | **L 6.5" 3 × 10; each set ends at the first hip drop.** The third set counts only with the hip level | 7.5" → 8" once 3 × 10 is level [3 × 8–12] |
| 2 | SL sit-to-stand | ~17–18" bench, 2 × 12 each leg, unassisted | **18" × 3 × 12** each leg. Needs help → 20" × 3 × 12 | → DB in hand [SL leg press 3 × 8–10] |
| 3 | RDL — pair with 6 | 55 lb/hand × 3 × 8 | 60 × 3 × 8 planned; **ran 52.5 × 3 × 8 (the DBs' top), effort 4/10** | **Barbell RDL from the next B: 115 × 3 × 8** (bar + 35 a side; the DBs' 105 felt easy) → +5 lb steps [3–4 × 6–10] |
| 4 | Lateral lunge | 3 × 8/side; set 3 shortened (front of knee 2–3) | **Full range, 3 × 8, bodyweight** (held for the 2–3) | → lightest DB [3 × 8 each direction]. Also the off-season Phase 1 Lower B item that rehab Phase 4 unlocks (Add-On §8) |
| 5 | Cable hamstring curl, ankle strap | Machine 40 × 3 × 10 (not comparable). Last cable: A 10/21, 60 / 60 / 70 | **70 × 3 × 10**, each leg; hold if the last set is above RPE 8 | +1 plate → 3 × 12 [3 × 8–12]. Shared with A: one change per session from the last session's dose |
| 6 | Cable hip abduction, standing, ankle strap — pair with 3 | Seated machine 85 × 2 × 15, both legs (not comparable). Last cable 20 × 2 × 10 (10/11) | **20 lb × 2 × 15**, each leg | 3 × 15 → +1 plate [plan: 2–3 × 10–15] |
| 7 | SL bridge — pair with 8 | Not done. 10/18: 3 × 10 each side | **3 × 10** (hold) | → loaded bilateral hip thrust (Add-On §7): the new exercise in the next B |
| 8 | **Seated calf raise, left loaded** | Machine, lightest, 3 × 12 (first time) | **Lightest DB, 3 × 12** (first at home: the new setup is the change). **DB on a folded towel across the lower thigh, just above the kneecap; not on the kneecap or the tendon (harvest site)** | → 3 × 15 → 4 × 12 → heavier DBs to 52.5 → a padded barbell across the thighs, same spot [3–4 × 10–15, plan Phase 4 B] |
| CD | Posture cooldown (Add-On §3) | Not done | **Full, ~6 min** | Chin nod → deep neck flexor hold |

- **Short on time:** drop 5 (also in A) → 7 → 4. Keep 6: it's the glute med work behind Sunday's hip drop.
- **Minimum session:** warm-up + 1, 2, 3 + the 3-minute cooldown (90/90 hip lift and chin nods), ~30 min.
- **Gap vs the plan's Phase 4 B:** it opens with a bilateral leg press, and there is no home equivalent, so bilateral knee-dominant lifting runs once a week (A's squat). Accepted for now.

### Session A — Phase 4 (baseline Wed 10/21, clean on 10/22; next Wed 10/28, in the cancelled PT visit's place, ~65 min with the test and the impact block)

The master plan's Phase 4 A (squat, knee extension, RFESS, hamstring curl, standing calf raise) plus the PT's step-up and heel tap. **Baselines = 10/21** (the recalibration above); Thursday's morning was clean, so they stand.

| # | Exercise | 10/21 | Next | Ladder [plan Phase 4 target] |
|---|---|---|---|---|
| T | Single-leg squat test (10/28, then Sundays) | — | **Wed 10/28: first, fresh, filmed** (the test above) | Until it passes |
| WU | Bike · BOSU ball toss (L) · impact | Bike 8 (2.06 mi) · TKE 60 lb × 2 × 10 · ball toss 3 × 45 s (done at the end) | Bike 8 · **ball toss 2 × 45 s, first** · **small double-leg pogos 2 × 5, quiet (first impact)** · cable TKE optional (Working Rules optional extra) | Impact per its ladder (above) |
| 1 | Goblet squat to an 18" box, paused | 40 lb × 2 × 10 | **40 × 3 × 10** | → 3–4 s lowering (the off-season Phase 1 emphasis, Add-On §8; 3 s ran 10/28) → +5 lb steps to **52.5, the DBs' top** (45/45/50 ran 10/28) → **then the barbell: a back squat in the rack to the same 18" box, paused, empty bar first**, +5 lb steps → 3 × 8 at RPE 7–8 [3–4 × 6–10, RPE 7–8] |
| 2 | Cable knee extension, full range: both legs up, left alone down over 3 s · R solo both ways | 40 lb × 2 × 12 each side, pain 0 | **40 × 3 × 12, both legs** (the third set; the left off its hold, Nick 10/28) | Next A: +1 plate → 3 × 12 → +1 plate [2–3 × 8–12, RPE 7–8, if the donor site tolerates]. **Never more than one plate a step on the left.** The right progresses on its own. Front-of-knee pain >2 → stop short of straight first, then lighten; the 90° isometric (5 × 10 s) is the fallback |
| 3 | RFESS, bodyweight, rear foot on a 7.5" box | 2 × 8/side (first time) | **3 × 8/side** | → 3 s lowering → DBs, +5 lb steps to 52.5s → a barbell on the back in the rack [3 × 8/side]. **Rear box stays at 7.5" for now:** on the right-leg sets the left is the rear leg, in a loaded quad stretch on the harvest side. Stop each rep before the left knee touches the floor (no kneeling on the left). Raise the box only with front-of-knee 0–2 on those sets |
| 4 | Cable hamstring curl, ankle strap — pair with 5 | 60 / 60 / 70 lb × 10, each leg | **70 × 3 × 10**, each leg (B's 10/25 dose didn't run at home) | Shared with B |
| 5 | Standing heel raise, DBs (calf slot) | 40s × 3 × 15 | **40s × 4 × 15** | → single-leg L + DB (52.5s × 3 × 12 ran both legs on 10/30, in B: two-leg work is at the DBs' top, so single-leg is next; past one 52.5, a barbell on the back in the rack) [4 × 10–15] |
| 6 | Step-up, 18", opposite knee drive, right foot passive | Bodyweight 2 × 15/side, no push-off | **Bodyweight 2 × 10/side** | No load ladder: it stays a control drill (the PT's no-push-off cue, 10/15) and the week's hip-flexion work. The RFESS carries the strength progression |
| 7 | Heel tap, lateral, 7.5", slow lowering | L 2 × 10 | **L 3 × 10**; watch the hip as well as the knee | → 8" |
| CD | Posture cooldown (Add-On §3) | Skipped (time) | **Full, ~6 min** | Chin nod → deep neck flexor hold |

- **Short on time:** drop 4 (also in B) → 6 → 7.
- **Minimum session:** warm-up + 1, 2, 3 + the 3-minute cooldown, ~35 min.
- **Out of A:** the 90° isometric (now the knee extension's fallback) · cable TKE as a default (optional) · SL sit-to-stand (B only) · wall squat (→ goblet squat) · split squat and forward lunge (→ RFESS).

### Knee-session review (10/21)

His question: were the 76–110-minute sessions carrying redundant work? Checked item by item against the plan, the PT notes, the Add-On and the off-season mapping.

- **Cut (covered elsewhere, or never programmed):**
  - 90° isometric → the knee extension's fallback
  - cable TKE → optional
  - standing bird dog → covered by the BOSU work, the bridge, the side plank and the cooldown
  - hip 4-way → abduction only. The PT's multi-hip was abduction, extension and flexion; adduction came from the plan. Copenhagen (adduction), RDL and bridge (extension) and the step-up's knee drive (flexion) cover the rest
  - right-leg step-down → never on the right-leg mirror list
- **Kept, for a reason:**
  - step-up: the PT's no-push-off cue, and the week's hip-flexion work
  - lateral lunge: off-season Phase 1 Lower B, which rehab Phase 4 unlocks; lateral strength for the sport
  - balance in both sessions: the off-season tissue block runs it twice a week; the problem was its place at the end
  - the full cooldown after both sessions: the posture plan's only home for the pelvic-tilt and neck work
- **Deliberate repeats:** hamstring curl in A and B, plus the clinic's leg curl (the hamstring gate is open) · standing and seated calf (different muscles; both in the plan) · heel tap and step-down (single-leg lowering control: the hip drop and the single-leg squat test).
- **Oversights fixed:** the right knee extension had been tied to the left's cap · the RFESS rear-leg position on the harvest side · the seated-calf DB placement · slow-lowering tempo missing from the squat and RFESS ladders.
- **Dependency:** adductor work now lives only in the upper-day finisher (Copenhagen); a missed upper day takes it with it.

### Conditioning

- Bike easy, legs only, on off days. **Ladder:** 15 (10/9) → 18 (10/12) → 21 (10/17) → 24 (10/19 ✓) → **27 (Thu)** → **30 (Sat)**, +3 min per ride. Missed rides aren't made up.
- **Bike intervals** (Add-On §5): after two weeks of 30 min with clean mornings and a PT OK: 3 × 4 → 4 × 4 min at RPE 7–8. Earliest ~the week of 11/8.

### Pre-session check

Swelling **graded** and not up vs the previous morning · extension side by side · pain ≤2 · no hard or painful catch. Fail → last clean doses, 2 sets, no changes.

**Own adjuncts (logged, not evaluated):** Game Ready / Go Ready, LLLT, red light, sauna (latest: sauna 20 min 10/19).

---

## 7. Add-On status

| | |
|---|---|
| **Placement** | Upper on its own days, A → B alternating, ≥2 days apart, after the bike and any throwing. This week: **Upper B Tue 10/27 (session 6) ✓** → **Upper A Sat 10/31 (session 7**; moved to Thursday 10/29, not run there (tired), back on Saturday by his call) → **Upper B Mon 11/2 (session 8)**, back on the Mon/Thu rhythm. Friday is the knee day |
| **Time** | Upper days run ~45 min (warm-up ~5, core ~30–35, finisher ~8) plus the bike (24–30) and throwing (~15–30), so Thursday is ~90–95 min. Block 1 adds ~10 |
| **Sessions run** | 6 since 9/20: A 10/9, B 10/12, A 10/17, B 10/19, A 10/22 (vacation gym, substitutes), **B 10/27 (Block 1's first)**. Weeks of 10/11 and 10/18: 2 of 2 |
| **Block** | **Block 1 from Tue 10/27** (two 2-of-2 weeks): main lifts 4 × 6–8 at RPE 7–8, accessories 3 × 8–10, speed bench 5 × 3 at 45–55%, the incline down to 2 × 8–10. Loads start where Block 0 left them (the 10/19 Upper B doses; 10/22's machine numbers don't carry): the first sessions back will feel heavier than their numbers, which is not a reason to add |
| **Unlocks** | Standing options and the chest pass: unlocked (session 3); the Pallof press runs standing (or half-kneeling, right knee down). **Saturday power & mobility:** the first run (10/24) was missed (away); Sat 10/31 carries Upper A again (Thursday's did not run), so it waits for the next free Saturday (seated throws still need the PT). **Loaded carries: in with Phase 4.** The suitcase carry replaces the accessory day's seated DB hold; the first one is judged by the next morning |
| **Optional items** | Accessory day (no slot left this week) and the Saturday session. **They no longer depend on the daily minimum** (Add-On rule 1's penalty dropped 10/21): `config.json → optional_from` has the accessory day from 10/21 and power & mobility from 10/24 |
| **Copenhagen** | Both sides, short lever (Nick 10/17). **The week's only adductor work** since the 10/21 knee review, so it stays when the rest of the finisher is cut. Ladder: +5 s per hold after a clean morning, 2 × 20 → 3 × 30 s. Last: 2 × 20 s (10/19); not done Thu 10/22 or Tue 10/27 → **2 × 25 s next (Sat 10/31, with Upper A)**. The long lever on the left waits for Phase 6 |
| **Disc throwing** | Last week 3 sessions (~240 throws), slight pivots. This week: Mon not reported, Wed skipped (knee day), **Thu ✓** (140 throws in 30 min, RPE 3: BH 30, FH 30, hammer 15, scoober 30, controlled-range FH long throws 35; planted and slight pivots mixed, **pivot foot: left**; the week's count dial up from ~60); Sat missed (away). Friday's morning was trace after Thursday's pivots with no knee session between, so **the next session runs feet planted** at the last count before the jump (~60 throws), and the dial waits. Limits: Add-On §3. **Pivot foot: left** (named 10/22), the surgical side; whether it matters is on the PT list (§5, item 4) |
| **Leg up between upper sets** | Optional since 10/21 (extension restored 10/18) |

**Upper B — session 6 (Tue 10/27; Block 1's first; ~60 min, RPE 7) and next (session 8, Mon 11/2).** Block 1: main lifts 4 × 6–8 at RPE 7–8, accessories 3 × 8–10, the speed bench 5 × 3, the incline 2 × 8–10. The next doses start from what was lifted.

| Lift | 10/27 | Next (session 8, Mon 11/2) |
|---|---|---|
| Warm-up | Thoracic extension · pec sequence · face pull 50 lb × 2 × 15 | Same |
| Speed bench | 65 × 13 (one set; the bar didn't slow), then 85 × 3 × 2: 3 sets of the 5, and one of them far past 3 reps | **70 × 5 × 3: three reps a set, however fast the bar moves.** 70 sits in Block 1's 45–55%; 85 was past it (the dashboard's correction, 10/28) |
| B1 Incline barbell press | 85 × 10, then 90 × 10 | **90 × 2 × 8–10** |
| B2 One-arm chin-grip cable pulldown | 80 × 10 → 90 × 8 → 100 × 8 × 2, each side | **100 × 4 × 6–8**, each side (main lift) |
| C1 One-arm DB row | 25 × 3 × 8/side, "way easy, not challenging" | **30 × 3 × 8–10/side** (one DB step) |
| → rest 60–90 s | — | — |
| C2 Seated neutral-grip DB press | 25s × 3 × 8 (up from 20s) | **25s × 3 × 8–10** (hold; first session at 25s) |
| C3 Prone incline Y-raise | 5 lb × 3 × 10 | Same |
| Finisher | Not done | All four; the Copenhagen per its ladder (after Saturday's 2 × 25 s) |

**Upper A — last home dose (10/17, session 3; 45 min, RPE 8; 10/22's vacation-gym numbers don't carry) and next (session 7, Sat 10/31 (planned Thu 10/29, not run); Block 1: main lifts 4 × 6–8 at RPE 7–8, accessories 3 × 8–10, loads from where Block 0 left them).**

| Lift | 10/17 | Next (session 7, Block 1) |
|---|---|---|
| A Seated med-ball chest pass | 8 lb × 4 × 3 (first time) | **8 lb × 4 × 3**, max intent, full reset each rep (skipped 10/22: no ball) |
| B1 Bench press | 105 × 3 × 8, "pretty easy" | **110 × 4 × 6–8** (main lift), 2–3 reps left. Feet flat, no leg drive. Alternate sets with B2 |
| B2 Band-assisted pull-up | 3 × 5, challenging (replaced the pulldown) | Same band, **4 × 5–6** (main lift; Block 1's first), building to 4 × 8, then a lighter band. Step down to a box; no dropping |
| C1 Standing landmine press | 25 lb + bar × 3 × 8/side, challenging (left arm) | **25 + bar × 3 × 8/side** (accessory, 3 × 8–10); start each set with the left |
| C2 Chest-supported DB row | 15s × 3 × 10, easy | **20s × 3 × 10** (accessory; one DB step, as planned for 10/22) |
| Finisher | All four, Copenhagen both sides | Same; **Copenhagen 2 × 25 s/side** (the ladder's next step; owed since 10/22). Short on time: keep the Copenhagen |

- **Short on time (Add-On rule 10):** the finisher except the Copenhagen goes first, then the C pair. The bike stays at 30 when it can: two weeks of 30-minute rides with clean mornings is the bike-interval gate (Add-On §5).
- **Rest (the plans set none here; general guidance):** chest pass ~45–60 s between sets · B1/B2 alternated, ~90 s after each (about 3 min between sets of the same lift) · C1/C2 alternated, ~60 s after each · finisher holds ~20–30 s apart.

**Saturday power & mobility — first run Sat 10/24 (optional; ~45 min with the bike, plus throwing).** Bike 30 → throwing → Pallof press, standing (or half-kneeling, right knee down), 3 × 8/side × 3 s, light to start → open book 6–8/side → supine hip flexor at the table edge, 45 s/side (left: let it hang) → seated wall slide with lift-off, 2 × 6–8. Seated rotational throws wait for the PT. The arms-only aerobic block is out (the 30-minute bike covers it).

**Upper and add-on review (10/21).** Checked against the Add-On, the off-season plan and the knee sessions.
- **Fixed:** the cut order no longer drops the Copenhagen (the only adductor work) · the Copenhagen gets a hold ladder · carries programmed (suitcase carry) · the Pallof press runs standing · the throwing check-in asks for the pivot foot · Add-On rule 1's penalty dropped, and rule 2 (leg up between sets) made optional · time budgets match the real sessions · the remaining off day is rest by default.
- **Cut as duplicates:** Saturday's arms-only aerobic (the 30-minute bike covers it) · the accessory day's Y-raise (its lower-trap raise is the same movement, and Upper B has the Y-raise).
- **Kept on purpose:** face pull in every warm-up plus Upper B's Y-raise (rounded shoulders, pull-biased) · side plank plus the Pallof (anti-rotation first) · hip flexor stretch on Saturday and in both knee cooldowns (pelvic tilt) · chest pass in A and speed bench in B (one power item each) · tibialis and eversion (ankle prep for running and cutting).

**Right leg:** mirrors inside the knee sessions (SL sit-to-stand, step-up, RFESS and lateral lunge, SL bridge, hamstring curl, knee extension, calf raise), including the knee extension (40 lb solo both ways, 10/21), which progresses on its own. Control drills (step-down, heel tap) are left only; the step-down is left only from 10/25. Right quad 77.2 lb on 10/17 (−7.8% vs pre-op), so the right's mirrored sets progress on their own healthy-leg terms (Add-On §3).

---

## 8. Week in review

*Not kept here. Each week's review is `real/checkpoints/<Sunday>.md`; the week of 10/11 is `real/checkpoints/2026-10-18.md`.*

---

## 9. Patterns and concerns

1. **Joint tolerance stays high.** Trace on every graded morning 10/6–10/21 and none on 10/22, across big batches, a PT session, throwing, a max quad test, Sunday's 110-minute B and Wednesday's recalibrated A. No flare since 9/11–12.
2. **Strength:** quad LSI 90.4% (83.4% vs the pre-op right). The left is 18.5% above its pre-op number; **the right is 7.8% below its own**, which flatters the symmetry. Keep the right's mirrored work progressing (healthy-leg criteria).
3. **Extension is done:** the photo passed; the heel prop is weekly; the leg up between upper sets is optional.
4. **Consistency:** last week the daily minimum 6 of 7 (Fri 10/16's heel prop; the dashboard's own record had it 7 of 7, and the repo's stands), upper 2 of 2, loaded days 3 of 3, minutes and RPE every session. This week: Session A slipped a day (Tue → Wed), which moves PT to Friday.
5. **More when it feels good — and his read: the starting doses lagged capacity.**
   - Batches of 5 → 7 → ~12 → ~8 changes; bench 105 instead of 95; left Copenhagen before the PT's OK.
   - 10/18: hamstring curl 20/30/30 → 40/50/60; lateral lunge range and volume together.
   - 10/21: nearly every Session A item well above its starting dose, the knee extension doubled (20 → 40). Recorded as a recalibration (§6), not a rule change; the day stays logged as past the plan.
   - The knee has tolerated all of it. Inside the graft's weak window (through ~11/16), the next-morning verdict and one change per exercise carry the load progression from here; the left knee extension moves one plate at a time, never more (10/28).
6. **Single-leg control:** slight left hip drop at the bottom of the 6.5" step-down (10/18); the left slightly shaky on the 20" sit-to-stand; the knee tracked fine on the RFESS, step-up and lateral heel tap (10/21). 18" unassisted still not done. Nick passed the step-downs on 10/17. **It is the soft spot the impact sequence starts around** (double-leg first) **and the single-leg squat test measures** (first 10/28, then Sundays).
7. **Disc throwing:** slight pivots load the planted knee in rotation; the pivot foot isn't named yet, and for a right-hander the conventional pivot is the left (surgical) foot. The step-out waits for the PT. Elbow and wrist volume build gradually: one dial a week.
8. **Graft weak window through ~11/16 = all of Phase 4.** Strength ramps toward RPE 7–8; impact climbs the plan's sequence one rung at a time from 10/28 (the guards in §6); running and sport pivoting at speed stay behind the plan's gates and the PT. A quiet knee is not evidence they can come forward.
9. **Protein and sodium.** The week of 10/11 averaged 130 g protein (target 150–160) and 4,136 mg sodium (over 2,300 every day): quiet days run ~112 g. Fish once.
10. **Weight:** 157.2 lb average for the week of 10/11 (+1.1 lb), mixed times of day: no change to the target. Review at 10/25 with two weeks of morning readings.
11. **Posterior-knee tightness** (9/30) not reported since; no soreness after the 10/18 hamstring jump. If it ever becomes calf pain or calf swelling: surgeon, not Claude.
12. **The session tail gets cut.** The eyes-closed drill was skipped 10/11, 10/18 and 10/21 (dropped from the plan 10/30); the full posture cooldown hasn't run at home (10/11 none, 10/13 short, 10/18 chin nods only, 10/21 none). From the next sessions the balance work leads both warm-ups (short in A; full, with the eyes-closed drill, in B), and the 3-minute cooldown is part of the minimum session.
13. **Session length:** B 10/18 ran 110 min, A 10/21 76 min. The 10/21 review trims them to ~60 and ~55 min by removing redundant work, not gated or PT-purposed work (§6).
15. **The away weekend (Sat 10/24 – Mon 10/26):** no training, no morning checks, creatine 1 of 3; food logged after the fact (~2,200 / 107 g, ~2,400 / 89 g, ~4,550 / 99 g). Tue 10/27: 160.7 lb (+3 on the week's average; salt and water until three readings say otherwise). Nothing reverses (no unclean morning reported) and nothing is repaid; the first sessions back feel heavier than their numbers.
14. **No full rest day by design.** The only day without knee or upper work is the accessory-day slot, so it's rest by default from 10/21. Upper days run 90–95 min with the bike and throwing.

---

## 10. Next milestones

- [x] **Phase 3 complete** (10/17): quad LSI 90.4%; step-downs passed
- [x] Extension photo passes (10/18): heel prop weekly
- [x] Sun 10/18: Session B (110 min, RPE 7) → Mon 10/19 clean
- [x] Mon 10/19: bike 24 → Upper B (session 4)
- [x] **Phase 4 started** (Tue 10/20, Knot III); first Phase 4 Session A Wed 10/21
- [x] **Mid-week checkpoint (Wed 10/21):** knee and upper reviews; the Add-On and the Working Rules re-issued (folded into the repo Thu 10/22)
- [x] **Thu 10/22:** clean morning → the 10/21 baselines stand · throwing done (slight pivots) · [ ] bike 27 → Upper A (session 5) → finisher (Copenhagen 2 × 25 s)
- [x] Fri 10/23: no PT; **Session B run in its slot** (vacation gym)
- [x] Tue 10/27: bike 30 · **Upper B, Block 1's first** (throwing and the finisher not done)
- [ ] **Wed 10/28:** PT cancelled (next Wed 11/4) → **the single-leg squat test** (first, filmed) → **first impact** (pogos 2 × 5) → Session A (the left knee extension off its hold)
- [ ] Fri 10/30: Session B (the 10/25 column) + the impact block's next step if Thursday is clean
- [ ] **Wed 11/4 PT:** hamstring and glute tests; reconfirm Nick's 10/28 words; step-out throws and the pivot foot
- [ ] **A graded morning every day**, with stiffness, catch and wellness
- [x] Upper **2 of 2** (10/19, 10/22) → **Block 1 from Tue 10/27**; Saturday power & mobility's first run missed (10/24, away)
- [ ] Bike 27 → 30
- [ ] **Sun 11/1:** morning weigh-in, photo + heel prop, SLR, flexion, **the single-leg squat test** → checkpoint → Session A (one change from Wednesday's)
- [x] Throwing pivot foot named: left (10/22)
- [ ] Protein ≥150 g on quiet days; a second fish meal
- [ ] **Toward the Phase 4 exit:** hamstring and glute ≥80% (unmeasured; the clinic) · the single-leg squat test passed (home, Sundays) · the impact sequence through the low jump and landing, then the drop vertical jump (cleared, Nick 10/28) · quad retest ~week 12 · running not before week 13 (Tue 11/17) and the team's agreement
