# ACL Recovery State — Sun 2026-11-15 (POD 83, post-op week 12) — rewritten Thu 11/19 (POD 87, week 13) for Phase 5

*The current program and where things stand, present tense only. Rules live in the Working Rules, the add-on design in the Add-On, the PT's words in `real/visits/pt_notes.md`; `real/README.md` says where each fact lives. Sections 2, 4 and 8 point to where that history lives in this repo.*

- **Program set:** Thu 2026-11-19, a mid-week rewrite on his request, after **Knot IV (Mon 11/16: the surgeon and the PT cleared the running gate, PT 15)** and the trainer's new week (11/19). **Phase 5, Return to Running:** the walk-jog progression on the high days · the knee sessions at the master plan's running-phase doses · the upper sessions merged with the trainer's exercises and moved onto the high days · zone 2 and throwing on the low days.
- **What this rewrite moved:** §1 (calendar, the trainer) · §3 (the Phase 5 exit is the gate) · §5 (PT 15; the trainer's part) · §6 (the week's shape, next week, the calendar, running, Session A's Phase 5 doses, conditioning) · §7 (placement, the merged upper sessions) · §9–10. The checks were simplified on 11/16 and 11/17 (Working Rules): the morning check is the swelling grade, the full check on Sundays.
- **Supersedes:** `real/state/archive/recovery_state_2026-10-18.md` (Phase 4: its gate tables, its week-by-week revisions).
- **Last reviewed:** Sun 11/22 checkpoint (`real/checkpoints/2026-11-22.md`): the program stands; §6's week corrected for what was not logged (Friday's knee session is B; Monday's upper is A); the sport stage is Phase 5 (§7).
- **Next:** the Sun 11/29 checkpoint (the sport plan's month check is still owed).
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
  - **Last visit: Mon 11/16, PT 15 (PTA; Cody on the calendar): the running gate cleared.** Next: Cody Thu 11/19; the calendar to 12/5 is in §6.
  - **Nick (10/9): progression is up to the master plan; his approval isn't needed; don't push through pain. Nick (10/28): the plan's criteria and minimum times decide, impact included; the drop vertical jump is cleared once its criteria are met.**
- **Trainer:** programs the upper and whole-body sessions and the low days from 11/17 (his instructions: `real/visits/`, patient-reported). Add-on work only; what touches the left knee stays with the plan and the clinic (§5).
- **Strength references:**
  - Right pre-op: quad 83.7 lb, hamstring 79 lb, extension 0° AROM, flexion 144°.
  - Left pre-op: quad 58.9 lb (LSI 70.4%), hamstring 55.8 lb (LSI 70.6%), extension −1°, flexion 144°.
  - **PT 11 (10/17), isometric quad peak on a torque monitor:** R 77.2 lb, L 69.8 lb (best of two rounds), **LSI 90.4%**; vs the right's pre-op 83.7 lb, 83.4%. The right is 7.8% below its own pre-op number.
  - **PT 13 (11/10), hamstring on the dynamometer:** R 65 lb, L 65 lb, **LSI 100%**; vs the right's pre-op 79 lb, 82%. The right is 18% below its own pre-op number (the left +16% on its 55.8). Flexion L 149°.
- **Body mass:** **starting weight 154.0 lb, Mon 9/28, 8:30 am fasted** (the nutrition guide's start; pre-injury 164, goal lean ~170; the guide's steps 154 → 160 → 164 → ~170). Weekly averages since: 155.2 (wk of 9/27, 2 readings) · 156.1 (10/4, 3) · 157.2 (10/11, 7) · 157.6 (10/18, 2) · 160.3 (10/25, 3 so far, salt-heavy days). 158.4 lb, Sun 10/18 morning, is the first Sunday-morning reading; the 10/11 reading (159.8) was a 5:30 PM weight, so readings are mornings from there. Weigh in Sunday mornings; the weekly average is the trend. Nutrition targets: `real/config.json → nutrition_targets` (3,000 kcal, 150–160 g protein; the Add-On's 1.6–2.0 g/kg is 115–145 g).
- **Calendar:**
  - **Phase 5 = weeks 13–16+ (Return to Running). Knot IV tied Mon 11/16 (POD 84)**, the last day of week 12 and of the graft's weakest window (~weeks 6–12); week 13 began Tue 11/17.
  - Phase 4 ran Tue 10/20 – Mon 11/16 (Knot III to Knot IV).
  - Phase 6 (power, plyometrics, sprinting, agility) is months 4–6: about Thu 12/24 at the earliest, on its gate (§3).
- **Home equipment:**
  - Have: power rack and barbell with a cable system and ankle attachments; DBs **to 52.5 lb** (10/31: not buying heavier; past 52.5 a lift moves to the barbell, §6 "Dumbbells at their top"); benches including incline; bands; air bike; BOSU; boxes and steps (6.5", 7.5", 8", 12", 18"–24" seats); 10 lb weight for the heel prop; strap; 8 lb med ball.
  - Don't have: leg press, leg curl, or knee-extension machine; wobble board.

---

## 2. Current reading

*Not kept here. Each morning is in `real/logs/daily_log.csv` (`python3 engine/darrow.py today`); what stands this week is in `real/NOW.md`. Every graded morning 10/6–10/21 was trace, including after PT 11's max-effort quad test, Sunday's 110-minute B and Wednesday's recalibrated A; Thu 10/22: none, down from trace, extension good, wellness 5.*

---

## 3. Phase status — **Phase 5 (Return to Running, weeks 13–16+), entered Mon 11/16 (POD 84), Knot IV**

**Knot IV tied Mon 11/16:** the surgeon and the PT cleared the running gate (PT 15, `pt_notes.md`). Standing at the clearance: full extension and flexion 149° (11/10) · no or trace effusion · normal gait · quad LSI 90.4% (10/17) · hamstring LSI 100% (11/10) · 10 controlled single-leg squats (11/1, 11/8) · good landings (Nick's read of the 11/8 drop-jump film) · single-leg pogos under the clinic's eye (assisted, 3 × 8 each leg, 11/16). The glute test never ran; the clearance stands without it. The Phase 3 and Phase 4 gate tables are in the archived State.

### Phase 5 exit (the next gate; master plan: before significant jumping, sprinting and agility; Knot V)

| Criterion | Status | Evidence / next step |
|---|---|---|
| Running progression well tolerated | **Starting** | Session 1 Thu 11/19; ten sessions, then continuous easy running (§6, Running) |
| No pain or effusion after running | — | Each run is judged by the next morning |
| Full ROM maintained | **Holding** | Extension matches the right, flexion 149° (11/10); the Sunday check watches it |
| Quad LSI ~≥85% | **Met on the last number: 90.4% (10/17)** | The formal retest's date is open (§5); ask for a body-weight-normalized number too (the right is 7.8% under its own pre-op) |
| Basic hop and landing work tolerated | **In progress** | Home: box drop-down, single-leg pogos, short decels from Sat 11/21 (§6, Impact) |
| Good single-leg control | **Watched** | The Sunday squat test (10 of 10 on 11/8; the left's ascent not yet smooth); the hip drop on the step-down |

**Also for Knot V (`config.json → knot_gates`):** running tolerated · quad ~≥85% · hop ~≥85% (unmeasured: a clinic hop test) · no meaningful effusion · good landing and single-leg force absorption. By the plan's calendar Phase 6 is months 4–6, about Thu 12/24 at the earliest; the criteria decide.

---

## 4. Measurements log

*Not kept here. Instrument numbers (pre-op, 9/11, 9/25, 10/1, 10/8, 10/17): `real/logs/measurements.csv` (`python3 engine/darrow.py measures`). Daily self-checks (swelling grade and trend, pain, extension, flexion, catch, wellness) and session minutes and RPE: `real/logs/daily_log.csv` (`python3 engine/darrow.py show daily DATE`). Session loads (RPE × minutes) are computed from the columns, never stored.*

---

## 5. PT and surgeon instructions in force

- **PT 16, Thu 11/19 (Cody; `pt_notes.md`):** **stiff landing on the left with jogging** (the gait observation) · **kneeling on the left OK to comfort, not pushed; the trainer's all-fours hold OK** (his account) · the clinic's light jog was the day's run · its impact moved on: the 12" drop decel 2 × 10, double-leg pogos without the cord, a quiet jump to a single-leg landing from 6", a Bulgarian split-squat jump.
- **PT 15, Mon 11/16 (PTA; `pt_notes.md`):** **the running gate is cleared, the surgeon and the PT** · continue the master plan · **short decelerations ("stopping and dropping hips", for confidence) and box drop-downs** added, "and other things in the master plan".
- **The trainer (patient-reported; `real/visits/2026-11-17_…`, `11-18_…`, `11-19_trainer_instruction.md`):** aerobic-only days 11/17 (40 min) and 11/18 (zone 2, 45 min). **11/19: the upper sessions go on the PT days (the high days), low days and aerobic work between; whole-body "functional" exercises join the upper sessions.** The trainer changes add-on work only: any exercise of his that loads the left knee and is not in the master plan (kneeling on the left, crawling, lunging, jumping, rotating on a planted foot) goes to the clinic first (Add-On §7).
- **Nick 11/10 (PT 13, `pt_notes.md`):** **the elliptical machine and slow form work for running are approved** · keep using the master plan and progressing. Read with the surgeon's 11/4 answer: form work at slow speed and the elliptical now; the first walk-jog from the week of 11/15 with the gate's other items. The form drills and their dose are not named (ask Thursday). Hamstring 65/65 lb (100%); flexion 149°; extension normal; the quad not tested. **Also (patient-reported, the same visit):** the drop vertical jump film looked good · some impact is okay · **bike intervals OK**, ramping the intensity as the plan calls for.
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
| 11/4 | Single-leg knee-extension isometrics, 0° and 45°, 30 s (home: Session A) |
| 11/12 | Tidal tank "around the world" on one leg · continuous-tension lunge, front foot on a 4" box · single-leg calf press on the leg press |
| 11/10 | Single-leg RDL holding a tidal tank · single-leg-stance trunk rotation with a tidal tank · calf raise with the forefoot on a plate · **the elliptical** · **slow running-form work** (drills not named) |
| 11/16 | Sprinter knee drive with a band · Shuttle kickbacks · resisted runs · two-point start · 12" drop decel · assisted single-leg pogos · sub-max knee-extension isometric (5 s holds) · **for home: short decels and box drop-downs** |

**Still through the PT / clinic:**
- running: **cleared 11/16**; the walk-jog's symptom rule and the home doses for the decels and drop-downs are not given (the master plan's running rules and the clinic's 11/16 dose stand meanwhile); the form drills are not named
- the trainer's knee-touching exercises: **kneeling on the left and the all-fours hold answered 11/19 (to comfort)**; anything else of his that crawls, lunges, jumps or rotates on a planted foot still goes to the clinic first
- the glute strength test and the formal quad retest (the clinic's equipment); the hamstring test is done (11/10, 100%)
- step-out throws, throwing on the move, marking
- BFR, Spanish squat, seated rotational throws (not in the plan)

**No longer through the PT (Nick 10/28):** impact prep (the plan's Phase 4 sequence, at home) · the single-leg squat test (at home, filmed) · the drop vertical jump, once the rungs before it are clean · the left knee extension's range and load (the plan's Phase 4 dose).

### For the next visit (the one list)

0. **Answered Mon 11/16 (PT 15): the running gate cleared by the surgeon and the PT;** single-leg pogos ran under the clinic's eye (assisted, 3 × 8 each leg). Still open from it: the glute test (item 2; no longer a gate item), the walk-jog's symptom rule (item 13), and **the home doses for the PT's short decels and box drop-downs** (box height, how many, which days; at home meanwhile: the clinic's 12" × 2 × 8 and the master plan's Level 1 decel, 2 × 5, §6).
1. **Mon 11/16, Cody** (PT 14 on 11/12 answered nothing on this list in its note: `pt_notes.md`, 2026-11-12; PT 13 on 11/10 answered the hamstring test, 100%, and gave the elliptical and slow running-form work: `pt_notes.md`, 2026-11-10). Then Thu 11/19, Mon 11/23, Wed 11/25, Mon 11/30; Nick Thu 12/3 (the calendar, §6). **Running form work:** which drills, how many, how often, on which days (knee days or off days). **The formal quad test:** when (planned 11/10, not done). **The tidal-tank items** at home: what to hold instead (a DB, the med ball). **Impact on the clinic days:** from 11/15 there is one home knee session a week, so the impact ladder (single-leg pogos, which the run gate needs) moves once a week; can it also run at or after a clinic visit?
2. **Glute med/max test** (the last unmeasured Phase 4 exit item), and mention the slight left hip drop at the bottom of the 6.5" step-down (10/18).
3. **Reconfirm Nick's 10/28 words** (relayed): the plan's criteria and times govern, impact included; the drop vertical jump cleared on its criteria. Show where the impact ladder stands and the single-leg squat video. **And say that single-leg hops ran twice last week ahead of the ladder** (left and right 2 × 5 on 10/28, left 2 × 5 on 10/30; quiet, pain 0, clean mornings): ask whether single-leg pogos may come forward, or wait for rung 3 and the drop vertical jump as the plan orders.
4. **Throwing:** are step-out throws OK yet, and does the pivot foot matter? (Right-handed, so the conventional pivot is the left foot: the surgical knee.)
5. The written note from 10/17 (device, knee angle), so the numbers are on record.
6. If wanted: BFR · Spanish squat · seated rotational med-ball throws.
7. Still from the repo's list: the right knee's hyperextension measured on a heel prop (the extension target until the clinic measures it) · who treated 10/1.
8. **Loaded days (added 11/8):** this week runs two visits plus two home sessions, four loaded days; the plan's Phase 4 says 2–3 strength sessions a week and the Working Rules two visits plus one home session. Is four what he wants while the visits run twice a week? From 11/15 the calendar is back to three.
9. **The quad test's conditions:** Session A ran Sun 11/8, 48 h before (the squat, the knee extension, the isometrics, the RFESS). The same device and knee angle as 10/17; and a body-weight-normalized number (Nm/kg) alongside the symmetry percentage, since the right is 7.8% below its own pre-op number and flatters the LSI.
10. **The drop vertical jump film** (8" box, 2 × 4, front and side): what he looks for; does it clear single-leg pogos (planned Sat 11/14, which did not run; now Sat 11/21 at home, or at the clinic first); does "pain-free" for pogos mean during, after, or the next morning.
11. **Front-of-knee (graft-site) pain:** record it separately in the morning check after impact days? What next-day response means hold, and what means a rung back.
12. **The left knee extension's one-plate cap:** tied to the graft's window through ~11/16; does it lift after that, or stay until he says?
13. **Running, once the gate is passed:** what symptom rule governs each walk–jog step (published protocols give almost none). Bike intervals too (§6: 30-minute rides since 10/27).
14. **Kneeling on the left: answered Thu 11/19 (Cody):** OK to comfort, not pushed. Padded; never for range or load.
15. **The trainer's all-fours hold: answered Thu 11/19 (Cody): OK.** Still open from it: which kinds of the trainer's exercises should come to the clinic first as his program grows (crawling, lunging, jumping, rotation on a planted foot).
16. **The stiff landing on the left with jogging (PT 16, 11/19):** what to change (a cue, a drill, cadence, the surface), and what "normal" looks like before the walk-jog moves past session 1.

---

## 6. Current program — Phase 5

### The week's shape (from Thu 11/19: high days and low days)

- **High days: the clinic days and the home knee session's day.** In order: the clinic visit or the knee session → **the walk-jog** when one is due (runs go on high days only, never on consecutive days) → **the upper session** (the trainer, 11/19), capped at about 45 minutes. High days are never back to back: a low day or the rest day sits between two.
- **Low days:** zone 2 on the bike (the trainer's dose) and the throwing. No lifting, no impact, no running (the master plan: non-impact conditioning on off days).
- **Sunday: rest**, with the full check, the squat test and the checkpoint.
- **Knee strength stays 2–3 sessions a week** (the master plan: running does not replace strength training): the clinic's two visits plus one home session, A and B alternating regardless of day.
- **Upper A and B alternate regardless of day, at least 2 days apart.** On the home knee session's day the upper session is optional and comes later in the day, after the knee work.
- **A long high day is cut from the upper session first** (§7, the cut order); the clinic, the knee session's minimum and a due walk-jog are never the cut.

### This week (Sun 11/22 → Sat 11/28) · Block 1 repeats · his plan of 11/19, corrected at the 11/22 checkpoint

Last week in one line: high days 2 of 3 (Mon PT 15, Thu PT 16; Sat Session B not run, the third time since 10/30); mornings 0 all seven days; floor 7/7; the run was the clinic's jog Thu 11/19 (stiff landing on the left); upper 0 logged (Thu's merged A not logged); bike Tue 40 · Wed 45 · Sat the trainer's intervals (moved from Fri); throwing 1 of 2 (Wed); weight 163.1 avg, +0.4 (`real/checkpoints/2026-11-22.md`).

| Day | Plan |
|---|---|
| Sun 11/22 | Rest · the full check, the weigh-in, the squat test → checkpoint |
| Mon 11/23 | **High: PTA** → **walk-jog session 1** (walk 5 / jog 1 × 5), after the clinic and if the mornings since Friday are clean; the left's landing is the thing to watch (PT 16) → **Upper A** (§7, the merged session: A, because Thursday's A was not logged; if it ran, this is B) |
| Tue 11/24 | Low: zone 2 on the bike (the trainer's dose) · throwing, short |
| Wed 11/25 | **High: PTA** → **walk-jog session 2** (session 1 repeated in its dose), if Tuesday's morning was clean and Monday's landing looked normal → **Upper B** (§7) |
| Thu 11/26 | Thanksgiving: rest (an easy ride or a throw is extra, never owed) |
| Fri 11/27 | **High: Session B** (§6, its doses and the impact block: box drop-down 12" × 2 × 8, single-leg pogos, the short decels; ~95 min) — **B, not A:** B did not run on 11/21, and the sessions alternate regardless of day (Working Rules); A at its Phase 5 doses comes next → later in the day **Upper A, optional** (his call that day) |
| Sat 11/28 | Low: zone 2 · throwing, the long session |

- **Runs: two** (Mon, Wed), each waiting on a clean morning after the one before. No run with Friday's Session B (it carries the impact block).
- **Throwing:** Tue short, Sat long, the Phase 5 throwing (§7; sport plan §3): the first session back (Wed 11/18) held the Phase 4 footwork, so the pivots and the max-intent throws may start this week, one dial at a time. Whether the pivot foot matters is still §5 item 4.
- **The week is judged by:** high days 3 · morning grades 7 · conditioning 4 (two runs, two zone 2 rides) · upper 2 (Friday's is extra).

### Next week (Sun 11/29 → Sat 12/5)

The calendar below; the 11/29 checkpoint writes it out.

### The calendar to Sat 12/5 (the visits from his appointment list; the shape from 11/19)

Visits: **PTA (Cody) Mon 11/23, Wed 11/25, Mon 11/30** · **PT (Nick) Thu 12/3**. Each week's doses come from that Sunday's checkpoint; this sets the days (`config.json → plan_changes`).

| Week | Sun | Mon | Tue | Wed | Thu | Fri | Sat |
|---|---|---|---|---|---|---|---|
| 11/15 · week 13 · Phase 5 from Mon | Rest · checkpoint | **PTA** (PT 15: running cleared) | Aerobic only (the trainer): bike 40 | Zone 2, bike 45 (the trainer) · throwing | **PTA** · walk-jog 1 · **Upper A** (merged) | Low: bike · throwing | **Session B** |
| 11/22 · Block 1 repeats | Rest · full check + squat test · checkpoint | **PTA** · walk-jog · **Upper B** | Zone 2 · throwing | **PTA** · walk-jog · **Upper A** | Thanksgiving: rest | **Session A** (Phase 5 doses) · Upper B optional, later | Zone 2 · throwing |
| 11/29 | Rest · full check + squat test · checkpoint | **PTA** · walk-jog · **upper** (next in the rotation) | Zone 2 · throwing | Zone 2 · throwing | **PT, Nick** · walk-jog · **upper** | Zone 2 · throwing | **Session B** |

- **High days are never back to back.** The home knee session runs once a week while the visits run twice: B Sat 11/21 → A Fri 11/27 → B Sat 12/5 (A and B alternate regardless of day).
- **Upper:** A Thu 11/19 → B Mon 11/23 → A Wed 11/25 → (B Fri 11/27, optional) → the next in the rotation Mon 11/30 and Thu 12/3. At least 2 days apart.
- **Runs** on the high days only, never on consecutive days; each waits on a clean morning.
- **Low days:** zone 2 and the throwing. Sunday is the rest day.

### Daily minimum and weekly checks

- **Daily, the morning check (his call): the swelling grade (from Tue 11/17) and last night's sleep in minutes (from Thu 11/19).** The two together are the whole daily minimum; his sleep targets are 480 min a night and 3,360 a week (`config.json → sleep_targets`; the plan's line is 8–9 h). On a morning that judges or precedes a run or a home knee session he also looks at pain and extension and reports them only when off (the running rules' next-morning verdict and the pre-session check read "nothing reported worse"; blank, never 0). Red flags any time. A missed morning check costs nothing else (Add-On rule 1).
- **Weekly (Sunday morning), the full check:** swelling grade · pain 0–10 and where · extension matches the right? · wellness 1–5 · anything new (a catch, stiffness, giving way) · weigh-in · **the single-leg squat test, filmed** (below; kept on Sundays, his call).
- **Retired 11/16 (his call):** the Sunday heel prop and side-view photo, the SLR lag and the flexion heel slide. Extension matched the right and flexion read 149° at the clinic (11/10), with no lag for months. **They come back** when a morning shows extension short of the right (the heel prop then goes daily), flexion down, or the quad not firing.

### Running — Phase 5 (the master plan's return-to-running progression; cleared Mon 11/16)

| Session | Main work | Status |
|---|---|---|
| 1 | Walk 5 min / jog 1 min × 5 | **Mon 11/23, after the clinic** (Thu 11/19's run was the clinic's light jog, 50 ft and back × 5; the note: stiff landing on the left) |
| 2 | Walk 5 / jog 1 × 5 | Wed 11/25, if 1 ran clean and the landing looked normal |
| 3–4 | Walk 4 / jog 2 × 5 | — |
| 5–6 | Walk 3 / jog 3 × 5 | — |
| 7–8 | Walk 2 / jog 4 × 5 | — |
| 9–10 | Walk 1 / jog 5 × 5 | — |
| Then | Continuous easy running | — |

- **Where:** high days only, after the clinic visit; with a home knee session only when a checkpoint places it. Never on consecutive days.
- **The plan's rules:** a walking warm-up and cool-down · forgiving surfaces when practical · non-impact conditioning on off days · duration before pace · never two variables at once · weekly volume up gradually (≤10% as a conservative rule) · no progress after a pain or swelling flare.
- **A session moves on only when** the next morning shows no increased swelling, no meaningful pain increase, no loss of extension and no next-day deterioration, and the running looked normal. Otherwise the same session repeats; a flare holds the progression, and the impact block steps back first (load rule 5).
- **The clinic's symptom rule:** not given yet (§5 item 13).
- **Logged:** `conditioning_type` walk-jog with its minutes, and an exercise row (`block` run): the session number, the walk and jog minutes × rounds as run, the surface, pain during and after, RPE, the average heart rate when he has it.

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

### Progression rules (Phases 4–5)

Full text: Working Rules, load rules 3–7.
- **Phase 5 targets (master plan, "Strength During the Running Phase", 2–3 sessions a week):** knee extension 4 × 5–8 at RPE 7–9 if the donor site tolerates · squat or leg press 3–4 × 5–8 · RFESS 3 × 6–10 · RDL 3–4 × 6–8 · hamstring curl 3 × 8–12 · calf raise 4 × 8–12. Each lift gets there one variable at a time from where it stands (the session tables); reps come down as load goes up.
- **10/21 recalibration (his decision).** The Session A starting doses (mostly the PT's 10/15 doses) were well below capacity, so Wednesday's loads replace them as the baselines: goblet squat 40 lb · knee extension 40 lb · hamstring curl 60–70 lb · heel raise 40s · cable TKE 60 lb · RFESS and lateral heel tap at 7.5". In-plan load progression is his to make (Nick 10/9); this is not a PT clearance. The day itself stays logged as past the plan (the doses as they stood that morning).
  - **Thu 10/22's morning was clean, so the baselines stand.** (Had it not been, every 10/21 change would have reversed to the last clean doses: 10/13 home and the PT's 10/15.)
  - **From here the plan's mechanics apply:** one major variable at a time per exercise; ≤10% or one increment.
  - **Left knee extension: off the 40 lb hold (Wed 10/28).** It had waited for the PT; Nick's 10/28 instruction puts it on the plan's Phase 4 dose (2–3 × 8–12 toward RPE 7–8; "progress range and load gradually, if the donor site tolerates"). 10/28: the third set at 40, and the left lifted alone as well (unplanned); every rep clean and the morning quiet, so the next A (11/1) takes +1 plate. **It stays the one exercise whose step is never more than one plate**, whatever the reps in reserve: open-chain extension near straight is the graft's highest-strain position, and the graft is at its weakest through ~11/16.
- **Pain:** 0–2 fine · 3–4 hold · ≥5 reduce or stop. Front of the knee watched most on the knee extension, goblet squat, RFESS, heel tap and step-down.
- **Effort:** Phase 4 main lifts work toward **RPE 7–8 (2–3 reps left)** once clean at a dose. New items and new loads start at 3–4 left. Never to failure.
- **Rep ranges come down as load goes up:** the plan's Phase 4 targets are in brackets in each ladder.
- **Dumbbells at their top (52.5 lb, 10/31):** a lift that outgrows them moves to the barbell at about the same total load, then climbs in +5 lb steps: the RDL now (**105 at the next B**, the DBs' 2 × 52.5; corrected 11/15 from 115, which changed the implement and the load together), the goblet squat after 52.5 (a back squat to the same box, empty bar first), the standing calf raise after single-leg with one 52.5 (a barbell on the back), the seated calf raise (a padded bar across the thighs), the RFESS after 52.5s (a bar on the back in the rack). The hip thrust starts on the barbell. Single-leg work stays on dumbbells while they last: they balance better. The upper lifts have room (row 30, press 25s, chest-supported row 20s); past 52.5 they go to the barbell or the cable.
- **The master plan's rule (from 11/1, his call; Working Rules, load rule 5): one major variable at a time per exercise** (load, reps, sets, range, speed, impact or complexity), and **any number of exercises may progress in the same session**, new exercises included. Load steps ~2.5–10% or one increment.
- A morning that isn't clean reverses every change.
- **Impact prep is on the home program from Wed 10/28** (below): the plan's dose and the plan's one-variable rule per exercise, and the impact block is the first thing reversed when a morning isn't clean (Working Rules, load rule 5).

### Impact preparation and the single-leg squat test (plan Phase 4; from Wed 10/28)

**Why now:** the plan starts early plyometric preparation in Phase 4 "when basic strength, control, and knee response permit," and Nick (10/28) put the plan's criteria and times in charge. Strength: quad LSI 90.4%. Knee response: trace or none on every graded morning since 10/6. Control: step-downs passed 10/17, but single-leg control is the soft spot (the hip drop, the shaky 18" sit-to-stand), so the sequence starts double-leg, at the bottom.

**Where:** knee days only (A and B), after the warm-up's ball toss and before lift 1, fresh. Stop while mechanics are still excellent: landings quiet, knees over the feet, even on both legs.

| Rung | Exercise | Dose | Moves on when |
|---|---|---|---|
| 0 | Leg-press or shuttle jump | No home equipment: skipped | — |
| 1 | **Small double-leg pogo** | **2 × 5 (Wed 10/28)** → 3 × 5 → 3 × 8 | 3 × 8 quiet, with clean mornings after |
| 2 | + Snap-down (the second exercise; the plan's cap is two) | 2 × 5 (10/30) → 3 × 5 (11/1) → 3 × 8 | Stays the second exercise until the drop vertical jump takes its place |
| 3 | Low vertical jump and landing (in the pogo's place, 11/1) | 2 × 5 → 3 × 5 → 3 × 8 | One session with landings quiet and even and a clean morning after opens rung 4 |
| 4 | **Drop vertical jump** (in the snap-down's place) | A filmed check, not a ladder: step off the **8" box**, land on both feet and jump straight up, **2 × 4**, filmed from the front; 12" (about the standard test height) once the 8" looks right. The plan's list: symmetrical loading, controlled knee and hip flexion, no major valgus collapse, stable trunk, quiet landing, no pain or swelling afterward | **Cleared by Nick (10/28)** once rung 3 has run cleanly. **Ran Sun 11/8; the film read as good by Nick (11/10): passed.** Saturday 11/14 holds it (Monday's morning slightly up) |
| 5 | **Single-leg pogo**, each leg, small | 2 × 5 (hop, land, reset) → 3 × 5 → 3 × 8 repeated (continuous, quiet) | The run gate's item; **the clinic ran 3 × 8 each leg, assisted (11/16), and cleared the gate**. At home it starts unassisted at 2 × 5 (Sat 11/21) and climbs one variable at a time. Left control first |
| PT | **Box drop-down** (PT 15) | 12" × 2 × 8: step off, land on both feet and stick (the clinic's dose 11/16) | Landings quiet and even, knees over the feet (the plan's landing checklist); the box height is a question for the clinic (§5 item 0) |
| PT | **Short decel** (PT 15; the master plan's deceleration Level 1) | 2 × 5: a few easy jogging steps, then stop over 4–5 steps, hips dropped | Level 2 (a moderate run, a controlled 3-step stop) once Level 1 is easy with clean mornings; one variable at a time. Not a jump, so it sits outside the two-jump cap |

- **Plan's dose:** 2 exercises · 2–3 sets · 5–8 contacts a set.
- **Pacing (11/1, his call):** the master plan's rule: each impact exercise moves one variable at a time (sets, contacts, or on to the next rung), inside the plan's caps (2 exercises, 2–3 sets, 5–8 contacts a set). No per-session limit on how many exercises move. A morning that isn't clean reverses the impact block first (back one rung; on rung 1, out until a clean morning), then the session's other changes (load rule 5).
- **Where it lands:** with a clean morning after every knee session, about one rung a session: the low jump 11/1 (done, landings good), the drop vertical jump check **Sun 11/8** (Fri 11/6 did not run; film it from the front, and from the side if a second phone is there: the plan's list has valgus and symmetry, which the front shows, and knee and hip bend and the trunk, which the side shows), **Nick read the film as good (11/10)**. Monday's morning was trace, so Saturday 11/14 holds Sunday's dose, and **single-leg pogos 2 × 5 start at the next knee session after a clean morning** (Sat 11/21's B), then 3 × 5 and 3 × 8 repeated. **From 11/15 there is one home knee session a week**, so the ladder moves once a week: about 12/5 for 3 × 8 at that pace (whether impact can also run on the clinic days is the question for Cody, §5). A morning that isn't clean costs a session on this line.
- **Logged** in the exercise log with the rung, sets × contacts, and whether the landings were quiet; `block` by the drill (Working Rules → Log files): `landing` for the small double-leg pogo, the snap-down and the box drop-down, `plyo` for the low vertical jump, the drop vertical jump and the single-leg pogo, `decel` for the short decel.

**The single-leg squat test** (the plan's Phase 4 test; at home, no further condition):
- **First run Wed 10/28**, before the bike, fresh. Then **every Sunday with the weekly checks until it passes.**
- 10 controlled single-leg squats to at least ~60° knee flexion, **touching down on the 24" seat** (about 65–75° at 6 ft; the seat used 10/28, so the Sundays compare), left, then the right for comparison; **filmed from the front** (and the side if there's a second phone).
- Judged on the plan's checklist: knee tracks over the foot · pelvis stays controlled · no major trunk compensation · no obvious unloading of the surgical leg · smooth depth and tempo. **Pass = all 10 with every item.**
- Logged as `sl_squat_reps` in `measurements.csv` (controlled reps out of 10, one row per side; method `home video`).

### Session B — ran Fri 10/30, clean on 10/31; not run Fri 11/6 (visitation hours), Sat 11/14 or Sat 11/21, its doses stand; **next Fri 11/27** (~95 min with the RDL's bar, the hip thrust, the seated calf, the curl, the isometrics and the short decels: measured, B ran 69 min on 10/30 without the curl and the bridge, A 86 and 85)

Baseline = 10/18, then 10/23, then 10/30 (each clean the next morning). One major variable at a time per exercise (the plan); any number of exercises progress the same day. Trimmed in the 10/21 review (below Session A).

| # | Exercise | Last (Fri 10/30) | Next (Sat 11/14; set for 11/6, which did not run) | Ladder [plan Phase 4 target] |
|---|---|---|---|---|
| WU | Bike · BOSU SL balance + ball toss (L) · impact | Bike 8 (2.13 mi) · ball toss 3 × 45 s · pogos 3 × 15 · snap-down 2 × 5 · single-leg hops L 2 × 5 (ahead of the ladder) | Bike 8 · ball toss 3 × 45 s · **box drop-down 12" × 2 × 8 + single-leg pogos 2 × 5 each leg, unassisted + short decels 2 × 5 (Level 1)** (PT 15, 11/16; the drop-down in the low vertical jump's place), if the mornings since the last knee day are clean | Ball toss + perturbation · impact per its ladder (above) |
| 1 | Forward step-down, 6.5", **left only** — pair with 8 | L 3 × 10 (R too); challenging; the left's last half-inch less smooth | **L 6.5" 3 × 10** (hold); each set ends at the first hip drop | 7.5" → 8" once 3 × 10 is level [3 × 8–12] |
| 2 | SL sit-to-stand | 18" × 3 × 12 each leg; the left very tough | **18" × 3 × 12** (hold) | → DB in hand [SL leg press 3 × 8–10] |
| 3 | RDL — pair with 6 | DBs 52.5 × 3 × 8 (their top), effort 4/10 | **Barbell 105 × 3 × 8** (bar + 30 a side: the DBs' total, so the switch to the bar is the one change; corrected 11/15 from 115, which added load on the first barbell exposure) | 110 next, then +5 lb steps [3–4 × 6–10] |
| 4 | Lateral lunge — pair with 7 | Bodyweight, full range, 3 × 8/side; front of knee 0 | **Lightest DB × 3 × 8/side** | → +5 lb steps [3 × 8 each direction]. Also the off-season Phase 1 Lower B item (Add-On §8) |
| 5 | Cable hamstring curl, ankle strap | Not done (time). Last: A 10/21, 60 / 60 / 70 | **80 × 3 × 8 → 10** (A 11/8: 80 × 3 × 8, the first session at the new plate; reps the one variable). Each leg, last in the session, then **the PT's isometrics, 0° and 45°, 30 s, both legs, light** (added 11/15) | +1 plate → 3 × 12 [3 × 8–12]. Shared with A |
| 6 | Cable hip abduction, standing, ankle strap | **30** × 2 × 15 each leg (planned 20); challenging, controlled | **30 × 3 × 15** (the third set) | → +1 plate [plan: 2–3 × 10–15] |
| 7 | **Barbell hip thrust (new; replaces the SL bridge)** | SL bridge not done; last 3 × 10 each side (10/18) | **Bar alone, 45 lb, 3 × 10**, pad on the hips, shoulders on the bench; ribs down, a slight posterior tilt at the top | +10 lb steps while 3 × 10 is clean [Add-On §7] |
| 8 | **Seated calf raise, left loaded** | Not done (standing 52.5s × 3 × 12 ran instead) | **Lightest DB, 3 × 12**, on a folded towel across the lower thigh, just above the kneecap; not on the kneecap or the tendon (harvest site) | → 3 × 15 → 4 × 12 → heavier DBs to 52.5 → a padded barbell across the thighs, same spot [3–4 × 10–15] |
| CD | Posture cooldown (Add-On §3) | Full ✓ | **Full, ~6 min** | Chin nod → deep neck flexor hold |

- **Pairs (they save time; the full session still runs ~95 min):** 1 + 8 (both left-only, low effort) · 3 + 6 · 7 + 4 · then 5 alone.
- **Short on time:** drop 5 first (the RDL and the hip thrust carry the hamstrings that day) → 4. Keep 6: it's the glute med work behind the hip drop.
- **Minimum session:** warm-up + 1, 2, 3 + the 3-minute cooldown (90/90 hip lift and chin nods), ~30 min.
- **Gap vs the plan's Phase 4 B:** it opens with a bilateral leg press, and there is no home equivalent, so bilateral knee-dominant lifting runs once a week (A's squat). Accepted for now.
- **Phase 5 targets for B's lifts:** the RDL 3–4 × 6–8 (the bar starts at 105 × 3 × 8) · the curl 3 × 8–12 · the seated calf toward 4 × 8–12; the rest are control and hip work at their own ladders.

### Session A — Phase 5 doses (ran Wed 10/28, Sun 11/1, Sun 11/8; **next after Session B**, ~85 min measured)

The master plan's running-phase strength session (squat, knee extension, RFESS, hamstring curl, calf raise) plus the PT's isometrics and the heel tap. One variable at a time per exercise, from Sun 11/8's doses toward the Phase 5 targets.

| # | Exercise | Last (Sun 11/8) | Next (Fri 11/27) | Ladder [Phase 5 target] |
|---|---|---|---|---|
| WU | Bike 8 · BOSU ball toss (L) 3 × 45 s · impact | Low vertical jump 3 × 5 · drop vertical jump, 8" box, 2 × 4 (read as good, Nick 11/10) | **The impact block as Sat 11/21's B leaves it**, one variable each: box drop-down 12" × 2 × 8 · single-leg pogos (3 × 5 if B's 2 × 5 were quiet and the mornings clean) · short decels 2 × 5 | Impact per its ladder (above) |
| 1 | Back squat to the 18" box, paused — pair with 5 | 45 / 65 / 75 × 10 (the first barbell day, past the plan's empty-bar start; Monday trace, Tuesday 0) | **75 × 3 × 8** after a 45 and a 65 warm-up set: three working sets at the top load he has lifted (the one change), reps into the Phase 5 range. Rate reps left | +5 lb steps at 3 × 8 → a fourth set [3–4 × 5–8] |
| 2 | Cable knee extension, full range, the left solo, 5–7 s lowering — pair with 4 | L 50 × 3 × 8, front-of-knee pain 2 · R 50 × 3 × 12 | **L 50 × 4 × 8** (the fourth set is the one change; the lowering unchanged) if the front of the knee stays ≤2; pain 3–4 holds 3 × 8. R on its own terms | → +1 plate (a 5 lb step if the stack takes one) at 5–8 reps [4 × 5–8, RPE 7–9, if the donor site tolerates]. **Never more than one plate a step on the left** until the clinic answers (§5 item 12). Front-of-knee pain >2 → stop short of straight first, then lighten |
| 2b | The PT's isometrics, 0° and 45°, 30 s, light | L done (90°, 0°, 45°) · R not done (time) | **Both legs, 0° and 45° × 30 s** | The PT's dose (11/4); the clinic ran sub-max 2 × 10 × 5 s on 11/16 |
| 3 | RFESS, rear foot on the 7.5" box | 20s × 3 × 8/side | **25s × 3 × 8/side** (one DB step) | +5 lb steps to 52.5s → a barbell [3 × 6–10]. No kneeling on the left |
| 4 | Cable hamstring curl, standing, ankle strap — pair with 2 | 80 × 3 × 8 each leg (the first session at the plate) | **80 × 3 × the next rep step after B's** (10 if B held 8; 12 if B reached 10) | → 3 × 12 → +1 plate [3 × 8–12]. Stays when time runs short |
| 5 | Single-leg standing calf raise — pair with 1 | 5 lb DB × 3 × 12 each leg | **5 lb × 4 × 12** (the fourth set, Phase 5's shape) | → DB steps to 52.5 → a barbell [4 × 8–12] |
| 6 | Heel tap, lateral, slow lowering, left | 7.5" × 3 × 10 (8" planned, held) | **8" × 3 × 10** if the 7.5" is level | A control drill; watch the hip |
| 7 | Step-up, 18", opposite knee drive | Not done (time), three sessions running | Bodyweight 2 × 10/side **if time** | The first cut; the RFESS carries the strength |
| CD | Posture cooldown (Add-On §3) | Full | **Full, ~6 min** | — |

- **Pairs:** 1 + 5 · 2 + 4 (one cable, one ankle strap) · 3 alone · 6 + 7.
- **Short on time:** drop 7 → 6 → 5. **The curl (4) stays.**
- **Minimum session:** warm-up + 1, the 2 + 4 pair, 3 + the 3-minute cooldown, ~40 min.
- **No walk-jog on this day this week;** Upper B, optional, later in the day (the week's shape, above).

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

### Conditioning — Phase 5

- **The running is the hard conditioning now** (Add-On §5, Phase 5: the walk-jog progression is the running); extensive tempo only once continuous easy running is established.
- **Low days: zone 2 on the bike** (the trainer): **45 min now, building quickly to 60** (his word, 11/19; each step is the trainer's). 40 min on Tue 11/17 (avg HR 149, RPE 4) and **45 min on Wed 11/18 (avg HR 145, RPE 5)**, the air bike, arms and legs. The trainer sets the minutes: `config.json → conditioning.cap_min` is 45, and a longer prescribed ride carries `cond_min` in its plan change. Zone 2 is a conversational effort; the average heart rate goes in the log when he has it.
- **The trainer's interval work on the low days (from Fri 11/20):** "aerobic power intervals" below the anaerobic threshold (untested: heart rate limited to 70–75%; without a monitor, a pace just past nose breathing), on a low-impact machine (the air bike, elliptical, arc trainer), walking rest at his prescription; with his warm-up, under an hour. First: 3 × 3 min ("Wk 1, Lvl 1"). The Add-On's own Phase 4 intervals (3 × 4 min at RPE 7–8: moved 11/11 and 11/18, never run) are retired in its place. Hard running intervals stay Phase 7 (Add-On §5).
- **The elliptical** (approved, Nick 11/10) may stand in for part of an easy ride; its first time is judged by the next morning.
- A ride is not a loaded day; a walk-jog sits on a high day. The knee-session warm-up bike stays ≤8 min.

### Pre-session check

Swelling **graded** and not up vs the previous morning · nothing reported off (extension side by side, pain ≤2, no hard or painful catch: he looks, and reports them only when off; Working Rules 11/17). Fail → last clean doses, 2 sets, no changes.

**Own adjuncts (logged, not evaluated):** Game Ready / Go Ready, LLLT, red light, sauna (latest: sauna 20 min 10/19).

---

## 7. Add-On status

| | |
|---|---|
| **Placement** | **From Thu 11/19 (the trainer): Upper A and B on the high days** (the clinic days; optional on the home knee session's day, later in the day), A → B alternating regardless of day, at least 2 days apart, after the clinic and any walk-jog. Thu 11/19's merged A was not logged, so: Mon 11/23 A → Wed 11/25 B → Fri 11/27 A (optional). History: the weeks of 10/11, 10/18 and 10/25 ran 2 of 2; 11/1 and 11/8 1 of 2 (A lost both); Tue 11/17's A dropped by the trainer |
| **Time** | **Capped at about 45 min on a high day** (the clinic ~60 and a walk-jog ~30 come first). Measured: Upper B's full core + finisher ran 65 and 73 min for ~20 sets (11/2, 11/9); the merged session is ~16 sets |
| **Sessions run** | 8 since 9/20: A 10/9, B 10/12, A 10/17, B 10/19, A 10/22 (vacation gym, substitutes), B 10/27 and A 10/31 (Block 1's first week: 2 of 2), **B 11/2 (session 8; A lost that week)**, **B 11/9 (session 9: incline 95 × 2 × 8 instead of 90 for reps, pulldown 110 × 4 × 6, row 35s, press 30s, Copenhagen 2 × 30; 73 min; A lost that week)**. Weeks of 10/11, 10/18 and 10/25: 2 of 2; weeks of 11/1 and 11/8: 1 of 2 |
| **Block** | **Block 1 repeats from Sun 11/22, on the anchor lifts** (below): main lifts 4 × 6–8 at RPE 7–8; the speed bench 5 × 3 at 45–55%; the incline 2 × 8–10. The week of 11/15 was its deload. A block advances on two weeks of 2 of 2 (Add-On §4); load goes up when every rep is clean with 2+ in reserve: +5 lb on the bar, one DB step, one cable plate |
| **Unlocks** | Standing options and the chest pass: unlocked (session 3); the Pallof press runs standing (or half-kneeling, right knee down). **Saturday power & mobility:** not yet run (10/24 away; 10/31 carried Upper A); **first run Sat 11/7** (optional; seated throws still need the PT).** The suitcase carry replaces the accessory day's seated DB hold; the first one is judged by the next morning |
| **Optional items** | Accessory day (no slot left this week) and the Saturday session. **They no longer depend on the daily minimum** (Add-On rule 1's penalty dropped 10/21): `config.json → optional_from` has the accessory day from 10/21 and power & mobility from 10/24 |
| **Copenhagen** | Both sides, short lever (Nick 10/17). **The week's only adductor work** since the 10/21 knee review, so it stays when the rest of the finisher is cut. Ladder: +5 s per hold after a clean morning, 2 × 20 → 3 × 30 s. Last: **2 × 25 s/side, Sat 10/31** (the step owed since 10/22) → **2 × 30 s next (Mon 11/2)**, after a clean morning. The long lever on the left waits for Phase 6 |
| **Disc throwing** | **Last full session Thu 10/22** (140 throws in 30 min, RPE 3; slight pivots, **pivot foot: left**; trace the next morning). Since then only short sets after knee sessions (Wed 10/28 ~17 FH; Fri 10/30 ~20, FH and BH); Saturday's didn't run. **Week of 11/1: 0 of 3.** **Week of 11/15: 1 of 2 (Wed 11/18, the long session; Fri's short one not logged).** **On the low days, never on a high day (from 11/19):** short sessions (~20 min) and one long one (~25–30 min) a week, with the zone 2 ride; one dial for the week, count or intensity, not both. **Phase 5 opens, by the sport plan §3:** game-tempo pivots and shimmies in planned sequences, and max-intent long throws (up to 8–10 a session, one such session a week to start, on dry ground); throwing after movement waits for the PT's OK per drill. The first session back holds the Phase 4 footwork (feet planted or slight pivots on the left): no step up after three weeks without a full session. The sport plan's week 5 (same throw, different arrival; the dominant hammer; hucks with different arrival shapes); the week 4 month check is owed. Limits: Add-On §3. Whether the pivot foot matters is on the PT list (§5) |
| **Leg up between upper sets** | Optional since 10/21 (extension restored 10/18) |

**The merged upper sessions (from Thu 11/19; his call with the trainer).** Each session: the posture warm-up → the power item when time allows → **two anchor lifts** on the block's doses (the lifts with a progression history; the bench and the pull-up are two of his own standards) → **the trainer's exercises** → the Copenhagen. About 45 min.

| | Upper A | Upper B |
|---|---|---|
| Warm-up (posture) | Thoracic extension · doorway pec sequence · face pull 50 × 2 × 15 | Same |
| Power (if time) | Seated chest pass 8 lb × 4 × 3 | Speed bench 75 × 5 × 3 |
| Anchors, alternated | **Bench** 115 × 4 × 7–8 (+5 once all four sets reach 8 with 2 left) · **band-assisted pull-up**, same band, 4 × 6 → 4 × 8 → a lighter band | **Incline press** 95 × 2 × 8–10 (+5 once both sets reach 10 with 2 left) · **one-arm chin-grip pulldown** 110 × 4 × 6–8 each side |
| The trainer's (11/19) | All-fours hold 3 × 20 s (OK'd by Cody 11/19) · standing landmine press 25 + bar × 3 × 6/side · short seated pulldown 3 × 6 · ½-kneel cable lift 30 × 3 × 6/side (either knee down, to comfort, padded) | **Not given yet** (ask the trainer). Until then B's own accessories as time allows: the one-arm row 35s, the seated DB press 30s and the Y-raise, 2–3 × 8–10 |
| Finisher | Copenhagen (2 × 30 s → 3 × 30 s/side) · tibialis raise and banded eversion 2 × 15 if time (ankle prep for the running) | Same |

- **Out of A, as redundant with the trainer's work:** the chest-supported row (the pulldown and the pull-up are its pulls) · the side plank (the all-fours hold and the cable lift carry the trunk). The landmine press stays as the trainer's, standing.
- **Short on time, in this order:** the ankle items → the power item → the trainer's block down to 2 sets → the anchors down to 3 sets. The Copenhagen stays (the week's only adductor work).
- **The knee's rule for the trainer's exercises:** kneeling on the left to comfort, padded, never pushed (Cody 11/19); nothing that crawls, lunges, jumps or rotates on a planted foot until the clinic has seen it (§5).
- **Thu 11/19 is the deload's version:** the anchors 3 sets, the chest pass 2 × 3, the loads held.
- The two tables below are the sessions as they stood before the merge: the anchors' history and the accessories' last doses.

**Upper B — session 8 (Mon 11/2; Block 1's second B; core + finisher 65 min, RPE 7) and next (session 9, Mon 11/9).** Block 1: main lifts 4 × 6–8 at RPE 7–8, accessories 3 × 8–10, the speed bench 5 × 3, the incline 2 × 8–10. Load goes up when every rep is clean with 2+ in reserve: +5 lb on the bar, one DB step, one cable plate (Add-On §4). Session 6 (10/27): `show ex 2026-10-27`.

| Lift | 11/2 (session 8) | Next (session 9, Mon 11/9) |
|---|---|---|
| Warm-up | Thoracic extension · pec sequence · face pull 50 lb × 2 × 15 | Same |
| Speed bench | 75 × 5 × 3 (planned 70; very light, the first set fast) | **75 × 5 × 3** (hold: the top of Block 1's 45–55% of an estimated ~140 from 115 × 7; three reps a set, however fast the bar moves) |
| B1 Incline barbell press | 90 × 2 × 8, ~3 left | **90 × 2 × 8–10** (reps first; +5 once both sets reach 10 with 2 in reserve) |
| B2 One-arm chin-grip cable pulldown | 100 × 4 × 8 each side, ~2 left | **110 × 4 × 6–8**, each side (+1 plate: every rep clean with 2 in reserve, the Add-On's trigger; his call 11/8) |
| C1 One-arm DB row | 30 × 3 × 10/side, too easy (~5–10 left) | **35 × 3 × 8–10/side** (one DB step) |
| → rest 60–90 s | — | — |
| C2 Seated neutral-grip DB press | 25s × 3 × 10, too easy (~5 left) | **30s × 3 × 8–10** (one DB step) |
| C3 Prone incline Y-raise | 5 lb × 3 × 10, still challenging | Same |
| Extra | Cable chest fly 2 sets (30 × 12, 50 × 10; not in the plan) | Not in the plan: it adds push to a pull-biased design (Add-On §3: heavy push and pull sets stay matched; the posture goal is the rounded shoulders). If it stays, a pull set matches it |
| Finisher | All four; Copenhagen 2 × 30 s/side | All four; **Copenhagen 3 × 30 s/side** (the ladder's top; 11/3's morning was clean) |

**Upper A — session 7 (Sat 10/31; Block 1's first A) and next (session 10: planned Thu 11/5, Sat 11/7 and Fri 11/13, none run, so these doses stand; **it runs Tue 11/17 as the deload**, sets cut per §6 "This week").** Block 1: main lifts 4 × 6–8 at RPE 7–8, accessories 3 × 8–10. Load goes up when every rep is clean with 2+ in reserve: +5 lb on the bar, one DB step (Add-On §4).

| Lift | 10/31 | Next (session 10, Fri 11/13) |
|---|---|---|
| A Seated med-ball chest pass | Not logged | **8 lb × 4 × 3**, max intent, full reset each rep |
| B1 Bench press | **115** × 6, 7, 7, 7 (planned 110; +10 from 105, past the +5 step; "decently easy", reps held) | **115 × 4 × 7–8** (reps first; +5 once all four sets reach 8 with 2 in reserve). Feet flat, no leg drive. Alternate with B2 |
| B2 Band-assisted pull-up | Same band, 5, 6, 5, 5; set 3 tough | Same band, **4 × 6**, building to 4 × 8, then a lighter band. Step down to a box; no dropping |
| C1 Standing landmine press | 25 lb + bar × 3 × 8/side, challenging | **25 + bar × 3 × 9–10/side** (reps first); start each set with the left |
| C2 Chest-supported DB row | 20s × 2 × 10, then 25s × 10 (up on the fly; harder) | **25s × 3 × 10** |
| Finisher | Copenhagen 2 × 25 s/side ✓; tibialis raise done; the rest not confirmed | All four; **Copenhagen 3 × 30 s/side** (the ladder's top; 11/2's 2 × 30 had a clean morning after). Short on time: keep the Copenhagen |

- **Short on time (Add-On rule 10):** the finisher except the Copenhagen goes first, then the C pair. The bike stays at 30 when it can: two weeks of 30-minute rides with clean mornings is the bike-interval gate (Add-On §5).
- **Rest (the plans set none here; general guidance):** chest pass ~45–60 s between sets · B1/B2 alternated, ~90 s after each (about 3 min between sets of the same lift) · C1/C2 alternated, ~60 s after each · finisher holds ~20–30 s apart.

**Saturday power & mobility — first run Sat 11/7 (optional; ~45 min with the bike, plus throwing).** Bike 30 → throwing → Pallof press, standing (or half-kneeling, right knee down), 3 × 8/side × 3 s, light to start → open book 6–8/side → supine hip flexor at the table edge, 45 s/side (left: let it hang) → seated wall slide with lift-off, 2 × 6–8. Seated rotational throws wait for the PT. The arms-only aerobic block is out (the 30-minute bike covers it).

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
   - The knee has tolerated all of it. Inside the graft's weak window (through ~11/16), the next-morning verdict and the plan's one-variable-per-exercise rule carry the load progression from here; the left knee extension moves one plate at a time, never more (10/28).
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
16. **The week of 11/8 is the densest yet:** four loaded days, upper twice, three rides and three throws, no rest day (Sunday rest starts 11/15), in the last week of the graft's window. Its guards are the plan's own: the morning check reverses, the pre-session check shrinks the session, loaded days never touch. An upper day runs ~115 min with the bike and a short throw (§7), and the thing placed last is the thing that gets cut, so throwing goes before the lifting (Add-On §2) and Friday's Upper A is planned to the real budget.
17. **The high days are long (from 11/19):** the clinic ~60 min, a walk-jog ~30 and an upper session ~45. The upper session is the cut (§7), never the clinic, the knee session's minimum or a due run. The home days were the ones lost in the weeks of 11/1 and 11/8.
18. **Two programmers now: the plan and the clinic for the knee, the trainer for the rest.** His whole-body exercises are where the two meet: Sun 11/15's session (box jumps, a lateral shuffle, kneeling on the left) ran ahead of the plan. The rule in force: his knee-touching exercises go to the clinic first (§5; Add-On §7).
19. **Running begins on top of everything else:** the first weeks add impact while the clinic, the home session and the impact block continue. The next morning's grade is the monitor, and a flare holds the run progression before anything else moves.

---

## 10. Next milestones

- [x] **Phase 4 complete; Knot IV tied Mon 11/16** (the surgeon and the PT cleared the running gate)
- [x] **Thu 11/19:** PT 16: kneeling to comfort and the all-fours hold OK'd; the clinic's light jog (stiff landing on the left) · [ ] the merged Upper A
- [ ] **Mon 11/23:** walk-jog session 1 after the clinic; the left's landing
- [ ] **Sat 11/21:** Session B (the barbell RDL 105, the hip thrust, the seated calf; box drop-down, single-leg pogos 2 × 5, short decels)
- [ ] **Week of 11/22:** walk-jog sessions 1–2 (Mon, Wed) · Upper B Mon, Upper A Wed · **Fri 11/27, Session A at the Phase 5 doses** · Block 1 repeats
- [ ] **Thu 12/3, Nick:** the formal quad retest (with a body-weight-normalized number) · the glute test · a hop test's date · the walk-jog's symptom rule · the knee extension's one-plate cap
- [ ] The walk-jog progression through session 10, then continuous easy running
- [ ] Single-leg pogos to 3 × 8 repeated; short decels to Level 2
- [ ] The trainer's exercises for Upper B, and his zone 2 dose for the low days
- [ ] The sport plan's month check (owed since week 4); the first Phase 5 throwing session
- [ ] Tape girths: about four weeks after 11/9
- [ ] **Toward the Phase 5 exit (Knot V; about 12/24 at the earliest by the plan's calendar):** running well tolerated · no pain or effusion after runs · full ROM · quad ~≥85% · hop and landing work tolerated (a hop test ~≥85%) · good single-leg control
