# ACL Recovery State — Sun 2026-10-11, revised Mon 2026-10-12 (POD 49, post-op week 7)

*The current program and where things stand, present tense only. Rules live in the Working Rules, the add-on design in the Add-On, the PT's words in `real/visits/pt_notes.md`; `real/README.md` says where each fact lives. Sections 2, 4 and 8 point to where that history lives in this repo.*

- **Program set:** Sun 2026-10-11 checkpoint; revised Mon 10/12 (mid-week, on request): Session B's 10/11 doses as its baseline (clean morning); Session A fixed for Tuesday; the eyes-closed drill is a wobble-board drill, with a BOSU home version; Upper B's row chest-supported for session 2; this week's upper Mon B → Thu A; throwing days added.
- **Last reviewed:** Mon 2026-10-12.
- **Supersedes:** `real/state/archive/recovery_state_2026-10-04.md`.
- **Next:** reviewed at the 10/18 checkpoint (the Phase 3 gate review).
- **Source priority:** latest PT/surgeon instruction (`pt_notes.md`) → rehab master plan → this file and the Working Rules → Whole-Athlete Add-On → sport plan → logs → general ACL knowledge.

---

## 1. Fixed facts

- **Surgery:** 2026-08-24 — LEFT isolated ACL reconstruction, patellar tendon autograft. No meniscus, cartilage, or other procedures. The plan applies unmodified.
- **Injury:** 2026-07-14. Clinic prehab from 2026-07-22.
- **Sport:** a combination of ultimate, court, and field sports. Disc throwing (ultimate, handler) runs on the sport plan, `sport_plan.md`: Phase 3 = seated or square-stance at easy effort, no pivot, no step-out.
- **Surgeon (9/25):** no brace; no crutches; very pleased with flexion and extension; ramp up strength as long as the knee stays quiet.
- **PT:** Cleveland Clinic Rehabilitation & Sports Therapy.
  - Nick Immel PT oversees and treated 10/8; Cody Rardon PTA treats.
  - Weekly, usually Fridays; 10/1 and 10/8 were Thursday reschedules.
  - **Next visit: not booked as of Mon 10/12.** Target Thu 10/15 or Fri 10/16; ask for the quad test when booking.
  - **Nick (10/9): progression is up to the master plan; his approval isn't needed; don't push through pain.**
- **Right-knee reference (pre-op):** extension 0° AROM (hyperextension on a heel prop never measured), flexion 144°, quad 83.7 lb, hamstring 79 lb. **83.7 / 79 lb are the strength targets.**
- **Left pre-op:** extension −1°, flexion 144°, quad 58.9 lb (LSI 70.4%), hamstring 55.8 lb (LSI 70.6%).
- **Body mass baseline:** 159.8 lb (72.5 kg), Sun 10/11, 5:30 PM. Weigh in Sundays at the same time. Protein target 1.6–2.0 g/kg ≈ 116–145 g/day.
- **Calendar:**
  - Post-op week 7 ends Mon 10/12; week 8 = Tue 10/13 – Mon 10/19.
  - Phase 4 earliest: week 9, Tue 10/20 (POD 57).
  - **The graft's weakest window (~weeks 6–12) runs through ~Mon 11/16 (POD 84).**
- **Home equipment:**
  - Have: power rack and barbell with a cable system and ankle attachments; DBs; benches including incline; bands; air bike; BOSU; boxes and steps (6.5", 8", 12", 18"–24" seats); 10 lb weight for the heel prop; strap.
  - Don't have: leg press, leg curl, or knee-extension machine; wobble board.

---

## 2. Current reading

*Not kept here. Each morning is in `real/logs/daily_log.csv` (`python3 engine/darrow.py today`); what stands this week is in `real/NOW.md`. Mon 10/12 was clean after Sunday's Session B, so the 10/11 doses are Session B's baseline (§6).*

---

## 3. Phase status — **Phase 3 (weeks 6–8), entered POD 34 (Sun 9/27)**

### Phase 3 exit gates (= the plan's "Before Phase 4" checklist; review week of 10/18)

| Criterion | Status | Evidence |
|---|---|---|
| Full/symmetric ROM | **Met** | Extension 2° hyperext AROM on 10/8 (third clinic reading at 2°); the right was 0° AROM pre-op. Flexion 146° vs the right's 144°. Refinement: the right knee's passive hyperextension on a heel prop is unmeasured |
| Normal gait | **Met** | Nick 10/8 |
| Minimal/no post-exercise effusion | **Met** | Trace on every graded morning 10/6–10/12 (10/10 not reported), including after the three biggest sessions |
| No post-exercise pain flare | **Met** | Pain ≤2 in every session; no flare since 9/11–12 |
| **Quad LSI ≥70%** | **Unmeasured** | The SL leg press 1RM (64%) is whole-leg, not one of the plan's tests. Target ≈58.6 lb on the left vs 83.7 on the right, or vs the right retested |
| Good step-down / single-leg control | **Probably met** | Forward step-down at home 6.5" 2 × 10, controlled (self, 10/11); SL sit-to-stand 20" unassisted; 12" step-up with knee drive (PT). Needs the PT to watch a step-down |
| Balance / joint-position control | **Met** | BOSU + ball toss; eyes-closed wobble board (PT 10/8) |

**Phase 4 waits on the quad test.**

---

## 4. Measurements log

*Not kept here. Instrument numbers (pre-op, 9/11, 9/25, 10/1, 10/8): `real/logs/measurements.csv` (`python3 engine/darrow.py measures`). Daily self-checks (swelling grade and trend, pain, extension, flexion, catch, wellness) and session minutes and RPE: `real/logs/daily_log.csv` (`python3 engine/darrow.py show daily DATE`). No post-op dynamometer in five visits.*

---

## 5. PT and surgeon instructions in force

- **Nick 10/9 (patient-reported):** progression is up to the master plan; no approval needed; don't push through pain.
- **Nick 10/8 (patient-reported):** keep progressing; add the PT's items alongside the master plan; well-balanced sessions that are challenging and progressing.
- **Surgeon 9/25:** no crutches; ramp up strength while the knee stays quiet.
- **Earlier PT verbal:** painless catch is normal · 18" sit-to-stand OK pain-free · bodyweight/DB/cable substitutes for machine items.

**PT-introduced items (in-plan):**

| Date | Items |
|---|---|
| 10/1 | Wall squat · heel tap slow eccentric · forward step-down 6" · isometric knee extension 90° · weighted heel prop · step hamstring stretch |
| 10/8 | 12" step-up with opposite knee drive · standing heel raise 35# DBs · standing bird dog 8# · multi-hip abduction / extension / flexion · **eyes-closed double-leg stance on a wobble board, 1 min each way** (wobble board per patient, 10/11) · bike level 5 |

**Still through the PT / clinic:**
- quad strength test
- impact prep and drop jumps
- running
- BFR, Spanish squat, seated rotational throws (not in the plan)

### For the next visit (the one list)

1. **Book the quad test, both sides, plus hamstrings** — ask when booking. Test the right too: 83.7 / 79 lb are the targets.
2. Watch a forward step-down (single-leg control gate).
3. The right knee's hyperextension measured on a heel prop.
4. Confirm the home version of the wobble-board drill: both feet on the BOSU dome, eyes closed, 1 min.
5. If wanted: BFR · Spanish squat · seated rotational med-ball throws (~10/24).
6. One-line heads-up: upper body on its own days; the right leg mirrors the left's single-leg work.
7. Which PTA treated on 10/1.
8. Step-up height: he ran the step-up at 18" on Tue 10/13 (your dose was 12", first at home). Is 18" fine from here, or back to 12"?
9. For awareness (sport plan §11): "Seated and square-stance throwing at easy effort now; pivots on the left from Phase 4; max-intent throws from Phase 5." Anything to watch with pivots on the graft side? Any reason to wait on max-intent throws?

---

## 6. Current program — Phase 3

### This week (Sun 10/11 → Sat 10/17)

| Day | Plan |
|---|---|
| Sun 10/11 | ✓ **Session B** (80 min, RPE 7) · heel prop · sauna |
| Mon 10/12 | ✓ Morning verdict (clean) · heel prop · bike 18 → **Upper B** → finisher · book PT |
| Tue 10/13 | **Session A** (fixed Tuesday: keeps a day's gap from PT on Thursday or Friday) |
| Wed 10/14 | Heel prop · **Throwing A** (control + breaks; sport plan). No knee or upper work |
| Thu 10/15 | PT if booked Thursday. Otherwise bike 21 → **Upper A** → finisher |
| Fri 10/16 | PT if booked Friday. **Throwing B** (deception + overheads). If PT was Thursday, throw first, then bike 21 → **Upper A** → finisher (Add-On §2) |
| Sat 10/17 | Heel prop · bike 24 · **Throwing C** (long throws at a controlled range) · film 10–15 min |
| Sun 10/18 | Weigh-in (5:30 PM), **first extension photo**, SLR lag, flexion → checkpoint → **Session B** · Phase 3 gate review |

Rhythm structure and rotation rules: Working Rules. Throwing: the sport plan, week 1 (baseline; minimum 2 × 20 + 1 × 25 min), Phase 3 throwing only.

### Daily minimum

- **Morning check:** swelling grade · extension side by side · pain · stiffness · catch · wellness 1–5.
- **Weighted heel prop: 10 lb, 10 min, once a day.** Weight on the lower thigh, never on the kneecap; quad relaxed.
- Becomes a weekly check once the side-view photo shows the left as straight as the right. The first photo is due Sun 10/18.

### PT items mapped into the home sessions

| PT item | Home slot |
|---|---|
| 12" step-up with knee drive | Step-up slot (A) |
| Standing heel raise 35 lb | Calf slot (A) |
| Multi-hip | Cable hip 4-way (B) |
| Bird dog | Session B |
| Eyes-closed wobble board | Home version (both feet on the BOSU dome, eyes closed, 1 min; confirm at PT). Its own drill after the BOSU ball toss, both sessions |
| Heel tap | A's eccentric item |
| Forward step-down | B's step-down |
| 90° isometric | Beside the cable knee extension (A) |
| Wall squat | Session A |
| SL leg press | SL sit-to-stand at home (both sessions) |

### Machine substitutes at home

- SL sit-to-stand (leg press)
- Standing cable hamstring curl, ankle strap, facing the stack (leg curl)
- Strap isometric at 90°
- **Cable seated knee extension 90°→45°:** facing away from the stack, low pulley behind, cable under the seat, ankle strap. Fallback: band
- Standing cable hip 4-way, ankle strap (multi-hip)
- BOSU dome, both feet, eyes closed (wobble board)

**Clinic numbers:** SL leg press 55# 2 × 10 (10/1), 6 plates (10/8), 1RM R 14 / L 9 plates · leg curl 47.5# · multi-hip 4 plates.

### Current depths and heights

| Item | Current |
|---|---|
| SL sit-to-stand | Unassisted at 20" (10/11, clean). Assisted at 18" (10/6, clean) |
| Wall squat | No deeper than the SL sit-to-stand |
| Heel tap | 5" |
| Forward step-down | 6.5" (10/11, clean, controlled) |
| Step-up | 12" (PT) |

### Progression rules

Full text: Working Rules, load rules 3–7.
- **Pain:** 0–2 fine · 3–4 hold · ≥5 reduce or stop. Never push through pain.
- **Effort:** 2–3 reps left once clean at that dose; new items and new loads at 3–4 left.
- **One change per exercise per session.** One new exercise per session. Load steps ≤10% or one increment.
- A morning that isn't clean reverses every change.

### Session A — knee dominant (next: Tue 10/13)

"→" marks the one change. Monday's morning was clean, so these doses stand; Tuesday's pre-session check still gates them.

| # | Exercise | Dose next | Ladder — one step per session [plan Phase 3 target] |
|---|---|---|---|
| WU | Bike · TKE (optional) | 8 min · 2 × 15 | — |
| 1 | SL sit-to-stand | L 2 × 12 → **at 18", unassisted** · R same. If 18" isn't clean: 20" → **3 × 12** instead | 18" unassisted → 3 × 12 → DB in hand [3 × 8–12] |
| 2 | Step-up, 12" with opposite knee drive (PT 10/8) | L 2 × 15 · R 2 × 15, bodyweight (PT dose; first at home) | 3 × 12 → DBs at 12"; or slow lowering [3 × 8–10] |
| 3 | Split squat, unassisted | 2 × 8/side → **3 × 8** | DBs, +5 lb steps; or slow lowering [3 × 8–10] |
| 4 | **Cable seated knee extension 90° → 45° — NEW** | L 2 × 15, slow, RPE 5–6, lightest setting that loads the quad · R 2 × 15 | 3 × 15 → 3 × 20 → +1 plate [2–3 × 15–20, RPE 5–7]. Front-of-knee pain >2 → shorten the range or lighten |
| 5 | Isometric knee extension 90°, strap (PT 10/1) | L 10 × 10 s, max effort | add 60° |
| 6 | Heel tap, 5", slow eccentric (PT 10/1) | L 2 × 10 | 3 × 10 → 6" |
| 7 | Wall squat (PT 10/1) | 2 × 10, no deeper than the SL sit-to-stand | 3 × 10 → depth (depth rule) |
| 8 | Standing heel raise, 35 lb DBs (PT 10/8) | 2 × 15 (PT dose; first at home) | 3 × 15 → single-leg straight-knee hold 3 × 30 s → single-leg L → + DB [3–4 × 10–15] |
| 9 | SL balance + ball toss on BOSU · then the eyes-closed drill | 3 × 45 s · 1 min, both feet on the BOSU dome, eyes closed, inside the rack with hands hovering near the uprights | + perturbation |
| CD | Posture cooldown (Add-On §3) | ~6 min | chin nod → deep neck flexor hold |

- **Batch:** knee extension (new) · SL sit-to-stand to 18" unassisted · split squat third set · step-up 12" · heel raise 35 lb · eyes-closed drill (first at home).
- **Short on time:** drop 9 → 8 → 7 → 6 → 3. On a short day, the posture cooldown is the 90/90 hip lift and chin nods.
- **Minimum session:** warm-up + 1, 2, 4, 5 (~30 min).

### Session B — posterior / single-leg (next: Sun 10/18)

Baseline = 10/11 (clean on 10/12). Next = one change each, if the mornings after Session A and PT are clean.

| # | Exercise | Baseline (10/11) | Next | Ladder [plan target] |
|---|---|---|---|---|
| WU | Bike | 8 min (2.06 mi) | 8 min | — |
| 1 | Forward step-down, 6.5" | L 2 × 10, controlled | **3 × 10** | 7" → 8" [3 × 8–10] |
| 2 | SL sit-to-stand | 20", 2 × 12, no assist | Same as Session A's result | Same ladder |
| 3 | RDL, DBs | 45 lb/hand × 3 × 10, easy | **50 lb/hand × 3 × 10** (one DB step; 45 left more than 3 reps) | +5 lb/hand; or slow lowering [3 × 8–12] |
| 4 | Lateral lunge | 2 × 8/side, short range | **3 × 8** | Full range [3 × 8 each direction] |
| 5 | Cable hamstring curl, ankle strap | 1 × 10 @ 20 + 2 × 10 @ 30 lb, each leg | **3 × 10 @ 30** | +1 plate → 3 × 15 [3 × 10–15] |
| 6 | SL bridge | 3 × 8 each side | **3 × 10** | 3 s hold → load |
| 7 | Cable hip 4-way, ankle strap | 20 lb × 2 × 10 each leg | **2 × 15** | 3 × 15 → +1 plate [2–3 × 10–15] |
| 8 | Standing bird dog | 15 lb × 2 × 10 | **2 × 15** | — |
| 9 | SL balance + ball toss on BOSU · eyes-closed drill | 45 s (sets not stated) · not done | 3 × 45 s · 1 min (as in Session A) | + perturbation |
| CD | Posture cooldown (Add-On §3) | not done | ~6 min | — |

- **If a morning before 10/18 isn't clean:** Session B runs at the 10/11 baseline with no changes.
- **Short on time:** drop 9 → 8 → 7 → 5.
- **Minimum session:** warm-up + 1, 2, 3 (~25 min).

### Conditioning

- Bike easy, legs only, on off days.
- **Ladder:** 15 (Fri 10/9, 3.47 mi) → **18 (Mon 10/12)** → 21 → 24 → 27 → 30, +3 min per ride. Missed rides aren't made up.

### Pre-session check

Swelling **graded** and not up vs the previous morning · extension side by side · pain ≤2 · no hard or painful catch. Fail → last clean doses, 2 sets, no changes.

**Own adjuncts (logged, not evaluated):** Game Ready / Go Ready, LLLT, red light, sauna (9/27, 9/30, 10/8, 10/11 — no swelling change after any).

---

## 7. Add-On status

| | |
|---|---|
| **Placement** | Own days, alternating A → B, ≥2 days apart. This week: **Mon 10/12 B (session 2)** → **Upper A (session 3) on Thu 10/15, or Fri 10/16 if PT lands Thursday** |
| **Sessions run** | 2 since 9/20: Upper A Fri 10/9 · Upper B Mon 10/12. The week of 10/4 ended 1 of 2 |
| **Block** | Block 0 (re-entry) through the week of 10/18. Block 1 from 10/25 if 2 of 2 in the weeks of 10/11 and 10/18 |
| **Unlocks** | Upper session 3: standing options and the chest pass. Saturday power & mobility earliest Sat 10/24. Seated throws need the PT's OK |
| **Optional items** | **Off for the week of 10/11** (accessory day): the week of 10/4 had missed daily-minimum days |
| **New from Mon 10/12** | Upper warm-up: thoracic extension → **doorway pec sequence** (contract-relax, chosen 10/12) → face pull with external rotation (seated) · tissue & trunk finisher · posture cooldown after every knee session (first attempt 10/11 skipped) |

**Upper B, 10/12 — last dose and next (session 4, ~Mon 10/19).** Bike 18 first. C ran 2 of 3 rounds; the Copenhagen was skipped. 75 min, session RPE 7.5/10. He will run the next one as written below.

| Lift | 10/12 | Next |
|---|---|---|
| Face pull with external rotation (warm-up) | 50 lb × 2 × 15, standing, a few reps left | Same (standing is allowed from session 3) |
| Incline barbell press | 95 × 5 / 8 / 5, last set ~2 in reserve: heavier than a first exposure should be | **85 × 3 × 8–10** (one step down, 3–4 in reserve) |
| One-arm chin-grip cable pulldown | 80 × 3 × 8/side (one-arm in place of two-arm) | Same load, reps toward 10 |
| C1 row | Chest-supported DB row 15s × 2 × 8 | **One-arm DB row** (hand on the bench, both feet on the floor), new: set 1 finds the load (~25 lb), 8/side |
| C2 seated neutral-grip DB press | 20s × 2 × 8 (top of the range) | 20s × 3 × 6–8: the third round is the change. Rest 60–90 s before it |
| C3 | Chest-supported DB reverse fly 5s × 2 × 10 | **Prone incline Y-raise** ~5 lb × 10–12 (Add-On, revised 10/12) |

**Upper A, 10/9 — last dose and next (session 3).** Session RPE 7/10.

| Lift | 10/9 | Next |
|---|---|---|
| Seated med-ball chest pass | — | **4 × 3, first time** (unlocks at session 3) |
| Bench press | 105 × 2 × 8, "pretty tough" | 105 × 3 × 8 if 2+ reps were left; 95 × 3 × 8 if 0–1 were left |
| One-arm cable pulldown | 80 × 2 × 8/side | Same load, 3 sets |
| Landmine press | 25 lb + bar × 2 × 8/side | Same load, 3 sets (standing allowed from session 3) |
| Chest-supported DB row | 15s × 2 × 10 | Same load, 3 sets |

**Right leg:** mirrors inside the knee sessions, including the cable knee extension. Reference: SL leg press 1RM 14 plates (10/8).

---

## 8. Week in review

*Not kept here. Each week's review is `real/checkpoints/<Sunday>.md`; the week of 10/4 is `real/checkpoints/2026-10-11.md`.*

---

## 9. Patterns and concerns

1. **Joint tolerance is high and still rising.** Three big batches in six days (10/6, 10/8, 10/11), including the RDL +80% jump: trace every morning after each. Swelling no longer tracks load, hours on feet, or the sauna.
2. **Quad strength is the only unmeasured gate, and PT isn't booked yet.** If the quad test isn't done at the next visit, Phase 4 can't open on 10/20. The cable knee extension starts Tuesday.
3. **Extension:** 2° hyperext at three clinic readings. It held with few home heel-prop rounds; once a day is maintenance. Remaining target: the right knee's passive hyperextension. First photo due 10/18.
4. **Off days and Saturdays produce little.**
   - Daily minimum 4 of 7 in the week of 10/4.
   - The Saturday bike has been missed five weeks running.
   - Zero days: 10/4, 10/5 (on feet).
   - Upper is improving: 1 session after three weeks at 0.
5. **More when it feels good:**
   - Batches of 5 → 7 → ~12 → ~8 changes.
   - First-exposure jumps: RDL 25 → 45 lb/hand (+80%, 10/11); step-up to 25 lb DBs with the band off (10/6); SL sit-to-stand 24" → 18" (10/6).
   - The knee tolerated all of it, and 45 lb felt easy, so the RDL start was simply light. The next step is still one DB increment. One change per exercise is the guardrail now that PT approval isn't the brake.
6. **Logging gaps:**
   - Session minutes and RPE: 1 of 9 loaded days since 9/20 (10/11: 80 min, RPE 7).
   - Morning stiffness, catch and wellness are now the items most often missing.
   - Step-down quality: reported 10/11 (controlled).
7. **Graft weak window through ~11/16.** A quiet knee is what this window feels like. Strength ramps; impact, running, rotation, and pivoting stay behind the plan's gates.
8. **Posterior-knee tightness** (9/30) not reported since. If it ever becomes calf pain or calf swelling: surgeon, not Claude.

---

## 10. Next milestones

- [x] **Mon 10/12:** graded morning = verdict on the Session B batch and the RDL jump — clean
- [ ] **Book PT today**; ask for the quad test (both sides, plus hamstrings) when booking
- [ ] Daily minimum **7 of 7**; a swelling grade, stiffness, catch and wellness 1–5 every morning
- [ ] **Minutes and RPE for every session** (Sun ✓)
- [ ] Upper **2 of 2** (Mon B, Thu or Fri A); bike 3 rides (18 → 21 → 24)
- [ ] Posture cooldown after both knee sessions; warm-up (with the pec sequence) and finisher on both upper days
- [ ] **Session A (Tue):** cable knee extension (new); SL sit-to-stand at 18" unassisted; step-up 12"; first home eyes-closed drill
- [ ] **Next PT visit:** quad test; watch a step-down; confirm the wobble-board home version
- [ ] **Sun 10/18:** weigh-in (same time), **first extension photo**, SLR lag, flexion → checkpoint → Phase 3 gate review. Phase 4 earliest Tue 10/20; quad LSI is the only open gate
