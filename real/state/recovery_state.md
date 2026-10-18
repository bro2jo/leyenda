# ACL Recovery State — Sun 2026-10-18 (POD 55, post-op week 8)

*The current program and where things stand, present tense only. Rules live in the Working Rules, the add-on design in the Add-On, the PT's words in `real/visits/pt_notes.md`; `real/README.md` says where each fact lives. Sections 2, 4 and 8 point to where that history lives in this repo.*

- **Program set:** Sun 2026-10-18 checkpoint (written Sat 10/17 evening, on request; Sunday morning's checks folded in 10/18 AM: the heel prop becomes a weekly check). The Phase 3 → 4 gate is met (PT 11, 10/17); Phase 4 opens Tue 10/20 by the plan's calendar, and Session A becomes the plan's Phase 4 Session A from that day. Session B runs once more at Phase 3 on Sun 10/18.
- **Last reviewed:** Sun 2026-10-18.
- **Supersedes:** `real/state/archive/recovery_state_2026-10-11.md`.
- **Next:** reviewed at the 10/25 checkpoint (first Phase 4 week; Session B becomes Phase 4's).
- **Source priority:** latest PT/surgeon instruction (`pt_notes.md`) → rehab master plan → this file and the Working Rules → Whole-Athlete Add-On → sport plan → logs → general ACL knowledge.

---

## 1. Fixed facts

- **Surgery:** 2026-08-24 — LEFT isolated ACL reconstruction, patellar tendon autograft. No meniscus, cartilage, or other procedures. The plan applies unmodified.
- **Injury:** 2026-07-14. Clinic prehab from 2026-07-22.
- **Sport:** a combination of ultimate, court, and field sports. Disc throwing (ultimate, handler) runs on the sport plan, `sport_plan.md`: Phase 3 = seated or square-stance at easy effort; Phase 4 opens the planned pivot and step-out on knee-session days.
- **Surgeon (9/25):** no brace; no crutches; very pleased with flexion and extension; ramp up strength as long as the knee stays quiet.
- **PT:** Cleveland Clinic Rehabilitation & Sports Therapy.
  - Nick Immel PT oversees and treated 10/8; Cody Rardon PTA treated 10/15. Who treated 10/17 (the quad test) and 10/1: not recorded.
  - Weekly, usually Fridays; this month's visits moved around (Thu 10/1, Thu 10/8, Thu 10/15, Sat 10/17).
  - **Next visit: not booked.** Book it this week (§5's list).
  - **Nick (10/9): progression is up to the master plan; his approval isn't needed; don't push through pain.**
- **Strength references:**
  - Right pre-op: quad 83.7 lb, hamstring 79 lb, extension 0° AROM, flexion 144°.
  - Left pre-op: quad 58.9 lb (LSI 70.4%), hamstring 55.8 lb (LSI 70.6%), extension −1°, flexion 144°.
  - **PT 11 (10/17), isometric quad peak on a torque monitor:** R 77.2 lb, L 69.8 lb (best of two rounds), **LSI 90.4%**; vs the right's pre-op 83.7 lb, 83%. Hamstrings not yet tested.
- **Body mass:** 158.4 lb, Sun 10/18, morning. The 10/11 baseline (159.8) was a 5:30 PM weight, so the two are not like for like; the week of 10/11 averaged 157.2 lb (7 readings). Weigh in Sunday mornings from here; the weekly average is the trend. Nutrition targets: `real/config.json → nutrition_targets` (3,000 kcal, 150–160 g protein).
- **Calendar:**
  - Post-op week 8 ends Mon 10/19; **week 9 = Tue 10/20 (POD 57): Phase 4 opens and Knot III ties that day.**
  - Phase 4 runs weeks 9–12 (through ~Mon 11/16); running (Phase 5) earliest Tue 11/17, behind its own gate.
  - **The graft's weakest window (~weeks 6–12) runs through ~Mon 11/16 (POD 84).**
- **Home equipment:**
  - Have: power rack and barbell with a cable system and ankle attachments; DBs; benches including incline; bands; air bike; BOSU; boxes and steps (6.5", 8", 12", 18"–24" seats); 10 lb weight for the heel prop; strap.
  - Don't have: leg press, leg curl, or knee-extension machine; wobble board.

---

## 2. Current reading

*Not kept here. Each morning is in `real/logs/daily_log.csv` (`python3 engine/darrow.py today`); what stands this week is in `real/NOW.md`. Every graded morning 10/6–10/17 was trace, including after PT 11's max-effort quad test.*

---

## 3. Phase status — **Phase 3 (weeks 6–8), entered POD 34 (Sun 9/27) · Phase 4 from Tue 10/20**

### Phase 3 exit gates (= the plan's "Before Phase 4" checklist): **all met, Sat 10/17**

| Criterion | Status | Evidence |
|---|---|---|
| Full/symmetric ROM | **Met** | Extension 2° hyperext AROM on 10/8 (third clinic reading at 2°); flexion 146° vs the right's 144°. Home, Sun 10/18 (self): first side-view heel-prop photo, the left as straight as the right; SLR without lag; flexion full, about the right's |
| Normal gait | **Met** | Nick 10/8; PT 10 (10/15): no deviations |
| Minimal/no post-exercise effusion | **Met** | Trace on every graded morning 10/6–10/17 |
| No post-exercise pain flare | **Met** | Pain ≤2 in every session; no flare since 9/11–12 |
| Quad LSI ≥70% | **Met: 90.4%** | PT 11 (10/17): isometric peak, R 77.2 / L 69.8 lb |
| Good step-down / single-leg control | **Met** | PT 11 (10/17): step-downs watched and passed |
| Balance / joint-position control | **Met** | BOSU + ball toss; eyes-closed wobble board (PT 10/8) |

**Knot III ties Tue 10/20** (the plan's earliest date, week 9), with this evidence: `python3 engine/darrow.py knot tie 3 --date 2026-10-20 --evidence "…"`, then `rehab.current_phase` → 4 and the next gate → Phase 4's exit.

### Phase 4 exit (return-to-run preparation; the next gate)

| Criterion | Now |
|---|---|
| Quad LSI >80% | 90.4% (10/17) |
| Hamstring LSI ≥80% | Untested: ask at the next visit |
| Glute strength ~≥80% symmetry | Untested |
| 10 controlled single-leg squats to ~60° | Not yet tested (the plan's single-leg squat test) |
| Pain-free low-level impact prep | Not started: impact prep is "only when appropriately cleared" (PT) |
| Good landing mechanics | Not started |

---

## 4. Measurements log

*Not kept here. Instrument numbers (pre-op, 9/11, 9/25, 10/1, 10/8, 10/17): `real/logs/measurements.csv` (`python3 engine/darrow.py measures`). Daily self-checks (swelling grade and trend, pain, extension, flexion, catch, wellness) and session minutes and RPE: `real/logs/daily_log.csv` (`python3 engine/darrow.py show daily DATE`).*

---

## 5. PT and surgeon instructions in force

- **PT 11, 10/17 (patient-reported):** quad test (LSI 90.4%), PT pleased · step-downs passed · **Copenhagen okay on both sides** · hamstrings not tested ("should be about the same").
- **PT 10, 10/15 (Cody, patient-reported):** step-up at 12" or 18" both fine · pivots okay within reason · knee extension through full range at a light load.
- **Nick 10/9 (patient-reported):** progression is up to the master plan; no approval needed; don't push through pain.
- **Nick 10/8 (patient-reported):** keep progressing; add the PT's items alongside the master plan; well-balanced sessions that are challenging and progressing.
- **Surgeon 9/25:** no crutches; ramp up strength while the knee stays quiet.
- **Earlier PT verbal:** painless catch is normal · bodyweight/DB/cable substitutes for machine items.

**PT-introduced items (in-plan):**

| Date | Items |
|---|---|
| 10/1 | Wall squat · heel tap slow eccentric · forward step-down 6" · isometric knee extension 90° · weighted heel prop · step hamstring stretch |
| 10/8 | 12" step-up with opposite knee drive · standing heel raise 35# DBs · standing bird dog 8# · multi-hip abduction / extension / flexion · eyes-closed double-leg stance on a wobble board, 1 min each way · bike level 5 |
| 10/15 | Cable TKE 3.5 plates · goblet squat 15 → 25 lb · forward lunge · banded retro walk · knee extension machine 10 lb, full range, both legs up, left alone lowering · SL leg press 70 lb · SL hamstring curl 25 → 32.5 lb |
| 10/17 | Copenhagen, both sides |

**Still through the PT / clinic:**
- hamstring strength test, both sides
- impact prep and drop jumps (Phase 4's early plyometric preparation: "only when appropriately cleared")
- running (Phase 5)
- BFR, Spanish squat, seated rotational throws (not in the plan)

### For the next visit (the one list)

1. **Book it.** Ask for the **hamstring test, both sides** (the Phase 4 exit needs hamstring LSI ≥80%; the right's pre-op 79 lb is the reference).
2. **Early plyometric prep:** "Phase 4 opened 10/20. When can I start the plan's low-level impact prep (pogos, small double-leg hops)? Do you want to see it first?"
3. The right knee's hyperextension measured on a heel prop.
4. Confirm the home version of the wobble-board drill: both feet on the BOSU dome, eyes closed, 1 min.
5. If wanted: BFR · Spanish squat · seated rotational med-ball throws (the Saturday power & mobility session's throw needs your OK).
6. For awareness: "Pivot throwing started 10/20 on knee days, one direction, walking tempo, one rung per bout. Anything to watch?"
7. Who treated 10/17 and 10/1.

---

## 6. Current program — Phase 3 → Phase 4 (Tue 10/20)

### This week (Sun 10/18 → Sat 10/24)

| Day | Plan |
|---|---|
| Sun 10/18 | ✓ Weigh-in 158.4 (AM) · ✓ first extension photo, clean · ✓ SLR no lag · ✓ flexion full · morning trace, quiet → **Session B** (Phase 3, last time; doses below) |
| Mon 10/19 | Morning check · bike **24** → **Upper B** (session 4) → finisher |
| Tue 10/20 | **Knot III · Phase 4 opens.** Pre-session check → **first pivot bout** (15–25 min, before the session or 2–3 h after) · **Phase 4 Session A** |
| Wed 10/21 | **Throwing A** (speed control: soft / normal / fast, FH and BH; square stance) |
| Thu 10/22 | Bike **27** → **Upper A** (session 5) → finisher |
| Fri 10/23 | **Throwing B** (scoober at different speeds and heights; upper-body fakes before breaks; square stance) · PT if it books (then Throwing B moves) |
| Sat 10/24 | Bike **30** · **Throwing C** (long throws) · film 10–15 min (handler defenders' hips) |
| Sun 10/25 | Heel prop, photo, SLR lag, flexion, weigh-in (AM) → checkpoint → **Phase 4 Session B** · pivot bout 2 |

- **No optional items this week** (accessory day, Saturday power & mobility): Fri 10/16's missed heel prop costs this week its optional items (Add-On rule 1).
- Rhythm structure and rotation rules: Working Rules. Throwing: the sport plan, week 2 (speed control). The pivot opens with Knot III on Tue; the other throwing days stay pivot-free.

### Daily minimum

- **Morning check:** swelling grade · extension side by side · pain · stiffness · catch · wellness 1–5. **From Sun 10/18 this is the whole daily minimum.**
- **Weighted heel prop: 10 lb, 10 min, now a weekly check.** The Working Rules ran it daily until the side-view photo showed the left as straight as the right; the first photo (Sun 10/18) did. Sundays, before the checkpoint: the prop (weight on the lower thigh, never on the kneecap; quad relaxed), then the photo, the SLR lag and flexion vs the right, and the weigh-in. **Back to daily** if a morning side-by-side look or a clinic reading shows the left short of the right.

### PT items mapped into the home sessions

| PT item | Home slot |
|---|---|
| Goblet squat (10/15) | A's squat slot from 10/20 (replaces the wall squat) |
| Knee extension, full range, both legs up / left lowering (10/15) | A's cable knee extension from 10/20 |
| SL hamstring curl (10/15) | Cable hamstring curl (A and B) |
| SL leg press (10/15) | SL sit-to-stand (B) |
| 12" step-up with knee drive (10/8); 12" or 18" fine (10/15) | Step-up slot (A) |
| Standing heel raise 35 lb | Calf slot (A) |
| Multi-hip | Cable hip 4-way (B) |
| Bird dog | Session B |
| Eyes-closed wobble board | Home version (both feet on the BOSU dome, eyes closed, 1 min; confirm at PT). After the BOSU ball toss, both sessions |
| Heel tap | A |
| Forward step-down | B's step-down |
| 90° isometric | A, last |
| Cable TKE (10/15) | Warm-up (optional) |
| Copenhagen, both sides (10/17) | The upper-day finisher |
| Forward lunge, banded retro walk (10/15) | Not at home yet: the plan's sessions cover the pattern |

### Machine substitutes at home

- SL sit-to-stand (leg press)
- Standing cable hamstring curl, ankle strap, facing the stack (leg curl)
- Strap isometric at 90°
- **Cable seated knee extension:** facing away from the stack, low pulley behind, cable under the seat, ankle strap on the left. Fallback: band. **Both legs up:** hook the right foot behind the left ankle to lift; lower with the left alone
- Standing cable hip 4-way, ankle strap (multi-hip)
- BOSU dome, both feet, eyes closed (wobble board)

**Clinic numbers:** SL leg press 70 lb 2 × 10 (10/15; 1RM R 14 / L 9 plates, 10/8) · SL knee flexion 25 → 32.5 lb (10/15) · knee extension machine 10 lb (10/15) · multi-hip 4 plates.

### Current depths and heights

| Item | Current |
|---|---|
| SL sit-to-stand | 18", slight assist (10/13). Unassisted at 20" (10/11) |
| Squat pattern (depth rule) | No deeper than the 18" sit-to-stand: the goblet squat to an 18" box at first |
| Heel tap | 6" (PT 10/15); 6.5" step at home |
| Forward step-down | 6.5" (10/11, controlled; PT passed it 10/17) |
| Step-up | 18" bodyweight (10/13, easy); 12" or 18" both fine (PT 10/15) |

### Progression rules

Full text: Working Rules, load rules 3–7.
- **Pain:** 0–2 fine · 3–4 hold · ≥5 reduce or stop. Never push through pain. Front-of-knee pain is watched most on the knee extension, now that it runs through full range.
- **Effort:** 2–3 reps left once clean at that dose (plan Phase 4: RPE 7–8); new items and new loads at 3–4 left.
- **One change per exercise per session.** One new exercise per session (PT items at the PT's dose don't count). Load steps ≤10% or one increment.
- A morning that isn't clean reverses every change.

### Session B — posterior / single-leg (Sun 10/18; Phase 3, the last time)

Baseline = 10/11 (clean on 10/12). Every morning since was clean, so "Next" stands. Pre-session check first.

| # | Exercise | Baseline (10/11) | Next (10/18) | Ladder [plan target] |
|---|---|---|---|---|
| WU | Bike | 8 min (2.06 mi) | 8 min | — |
| 1 | Forward step-down, 6.5" | L 2 × 10, controlled | **3 × 10** | 7" → 8" [3 × 8–10] |
| 2 | SL sit-to-stand | 20", 2 × 12, no assist | **18", 2 × 12**, assist only if needed (10/13 needed a slight assist) · R same | 18" unassisted → 3 × 12 → DB in hand |
| 3 | RDL, DBs | 45 lb/hand × 3 × 10, easy | **50 lb/hand × 3 × 10** | +5 lb/hand; or slow lowering [3 × 8–12] |
| 4 | Lateral lunge | 2 × 8/side, short range | **3 × 8** | Full range [3 × 8 each direction] |
| 5 | Cable hamstring curl, ankle strap | 1 × 10 @ 20 + 2 × 10 @ 30 lb, each leg | **3 × 10 @ 30** | +1 plate → 3 × 15 [3 × 10–15] |
| 6 | SL bridge | 3 × 8 each side | **3 × 10** | 3 s hold → load |
| 7 | Cable hip 4-way, ankle strap | 20 lb × 2 × 10 each leg | **2 × 15** | 3 × 15 → +1 plate [2–3 × 10–15] |
| 8 | Standing bird dog | 15 lb × 2 × 10 | **2 × 15** | — |
| 9 | SL balance + ball toss on BOSU · eyes-closed drill | 45 s · not done | 3 × 45 s · 1 min | + perturbation |
| CD | Posture cooldown (Add-On §3) | not done | ~6 min | — |

- **Short on time:** drop 9 → 8 → 7 → 5. **Minimum session:** warm-up + 1, 2, 3 (~25 min).
- **From Sun 10/25 it becomes the plan's Phase 4 Session B** (leg press → SL sit-to-stand, RDL, step-down, single-leg leg press, seated calf raise), written at the 10/25 checkpoint from this session's result.

### Pivot bout 1 — Tue 10/20 (sport plan §3, Phase 4)

- After a clean morning, on the knee day: **before Session A, or 2–3 hours after it**, never straight after the main lifts.
- **~20–30 pivot throws, one direction** (whichever feels easier), **short step** (about shoulder width), **walking tempo**, against the net or a mark. 15–25 min with a square-stance warm-up first.
- **Ladder, one rung per bout after a clean morning:** the other direction → a wider step (full stance) → +10 throws → both directions in a set order → slow planned shimmies → game-range long throws with a step and pivot. Up to ~60 pivot throws a bout by the end of Phase 4. Two bouts a week, knee days only.
- **Still out:** max-intent throws, game-tempo shimmies, throwing after jogging or running, any reaction.

### Session A — Phase 4, knee dominant (Tue 10/20)

The plan's Phase 4 Session A with the PT's items. "→" marks the one change; Tuesday's pre-session check gates it.

| # | Exercise | Dose (10/20) | Ladder — one step per session [plan Phase 4 target] |
|---|---|---|---|
| WU | Bike · cable TKE (optional) | 8 min · 2 × 10 | — |
| 1 | **Goblet squat** (PT 10/15) | 25 lb DB × 2 × 10, to an 18" box (PT dose; first at home) | 3 × 10 → +5 lb → depth (depth rule) [3–4 × 6–10, RPE 7–8] |
| 2 | Cable seated knee extension, full range | L 20 lb × 2 × 12 → **lift with both legs, lower with the left alone over ~3 s** (PT style) | 3 × 12 → +1 plate [2–3 × 8–12, RPE 7–8]. Front-of-knee pain >2 → shorten the range or lighten |
| 3 | **Rear-foot elevated split squat — NEW** (replaces the split squat) | Rear foot on the 6.5" step, bodyweight, 2 × 8/side | 3 × 8 → DBs, +5 lb steps [3 × 8 each side] |
| 4 | Cable hamstring curl, ankle strap | 3 × 10 @ 50 lb each leg if Monday is clean (Sunday ran 40 / 50 / 60, past the planned 30); 30 lb if it isn't | +1 plate (60) → 3 × 12 [3 × 8–12] |
| 5 | Standing heel raise, 35 lb DBs | **3 × 15** (the PT's 2 × 15 + a third set) | 4 × 15 → single-leg L → + DB [4 × 10–15] |
| 6 | Step-up with opposite knee drive, 18" | L 2 × 15 · R 2 × 15, bodyweight (as 10/13) | 3 × 12 → DBs |
| 7 | Heel tap, 6.5", slow eccentric | L 2 × 10 | 3 × 10 → 8" |
| 8 | SL balance + ball toss on BOSU · eyes-closed drill | 3 × 45 s · 1 min, inside the rack, hands hovering near the uprights | + perturbation |
| 9 | Isometric knee extension 90°, strap | L 10 × 10 s, max effort | add 60° |
| CD | Posture cooldown (Add-On §3) | ~6 min | chin nod → deep neck flexor hold |

- **Batch:** the goblet squat (PT item, first at home) · knee extension in the PT's style · RFESS (the one new exercise) · heel raise third set. The SL sit-to-stand moves to Session B only (B's single-leg leg press substitute); the wall squat leaves (the goblet squat takes its slot).
- **Short on time:** drop 9 → 8 → 7 → 6. On a short day, the posture cooldown is the 90/90 hip lift and chin nods.
- **Minimum session:** warm-up + 1, 2, 3, 4 (~35 min).

### Conditioning

- Bike easy, legs only, on off days.
- **Ladder:** 18 (Mon 10/12) → 21 (Sat 10/17) → **24 (Mon 10/19) → 27 (Thu 10/22) → 30 (Sat 10/24)**, +3 min per ride. Missed rides aren't made up.
- **Bike intervals** (Add-On §5, Phase 4): after two weeks of 30 min easy with clean mornings and the PT's OK. Earliest the week of 11/1.

### Pre-session check

Swelling **graded** and not up vs the previous morning · extension side by side · pain ≤2 · no hard or painful catch. Fail → last clean doses, 2 sets, no changes. The same check gates a pivot bout.

**Own adjuncts (logged, not evaluated):** Game Ready / Go Ready, LLLT, red light, sauna (most recently 10/17; no swelling change after any).

---

## 7. Add-On status

| | |
|---|---|
| **Placement** | Own days, alternating A → B, ≥2 days apart. This week: **Mon 10/19 Upper B (session 4)** → **Thu 10/22 Upper A (session 5)** |
| **Sessions run** | 3 since 9/20: Upper A Fri 10/9 · Upper B Mon 10/12 · Upper A Sat 10/17. **The week of 10/11 ran 2 of 2** (the first) |
| **Block** | Block 0 (re-entry). **Block 1 from 10/25** if this week also runs 2 of 2 (Add-On §4: two weeks of 2 of 2) |
| **Unlocks** | Standing options and the chest pass: open (session 3). Saturday power & mobility: after two weeks of 2 of 2; this week's optional items are off (10/16's missed heel prop), so the earliest is Sat 10/31. Seated throws need the PT's OK |
| **Optional items** | **Off for the week of 10/18** (Add-On rule 1) |
| **Every upper day** | Warm-up: thoracic extension → doorway pec sequence (contract-relax) → face pull with external rotation · tissue & trunk finisher with the **Copenhagen on both sides** (PT 11) · left leg up between sets |

**Upper B, 10/12 — last dose and next (session 4, Mon 10/19).** Bike 24 first.

| Lift | 10/12 | Next |
|---|---|---|
| Face pull with external rotation (warm-up) | 50 lb × 2 × 15, a few reps left | Same, standing |
| Incline barbell press | 95 × 5 / 8 / 5, last set ~2 in reserve: heavier than a first exposure should be | **85 × 3 × 8–10** (one step down, 3–4 in reserve) |
| One-arm chin-grip cable pulldown | 80 × 3 × 8/side | Same load, reps toward 10 |
| C1 row | Chest-supported DB row 15s × 2 × 8 | **One-arm DB row** (hand on the bench, both feet on the floor), new: set 1 finds the load (~25 lb), 8/side |
| C2 seated neutral-grip DB press | 20s × 2 × 8 (top of the range) | 20s × 3 × 6–8: the third round is the change. Rest 60–90 s before it |
| C3 | Chest-supported DB reverse fly 5s × 2 × 10 | **Prone incline Y-raise** ~5 lb × 10–12 (Add-On, revised 10/12) |

**Upper A, 10/17 — last dose and next (session 5, Thu 10/22).** 45 min, session RPE 8.

| Lift | 10/17 | Next |
|---|---|---|
| Face pull with external rotation (warm-up) | 50 lb × 2 × 15 | Same |
| Seated med-ball chest pass | 8 lb × 4 × 3, first time | Same |
| Bench press | 105 × 3 × 8, "pretty easy" | **110 × 3 × 8** (+5 lb) |
| Band-assisted pull-up (in place of the cable pulldown) | 3 × 5 | Same band, **3 × 6** |
| Standing landmine press | 25 lb + bar × 3 × 8/side, the left harder | Same |
| Chest-supported DB row | 15s × 3 × 10, easy | **20s × 3 × 10** |

**Right leg:** mirrors inside the knee sessions, including the cable knee extension and the RFESS.

---

## 8. Week in review

*Not kept here. Each week's review is `real/checkpoints/<Sunday>.md`; the week of 10/11 is `real/checkpoints/2026-10-18.md`.*

---

## 9. Patterns and concerns

1. **The knee is quiet under load.** Trace every graded morning since 10/6, including after the RDL jump (10/11), the 18" step-up (10/13), two PT visits and a max-effort quad test (10/17). Swelling no longer tracks load, hours on feet, or the sauna.
2. **Phase 4 adds three new kinds of load at once:** knee extension through full range (donor site), pivot throwing (rotation on the graft side), and the squat pattern under a load. The one-change rule and the morning verdict decide; the pivot ladder moves one rung per bout. This is still the graft's weakest window (through ~11/16).
3. **The daily minimum was the week's weak spot again:** 6 of 7 (Fri 10/16 missed the heel prop), and it costs this week its optional items. From 10/18 the daily minimum is the graded morning check alone (the heel prop is weekly), so 7 of 7 is a grade every morning.
4. **More when it feels good.** The 10/13 session ran two items past the plan (step-up 18", knee extension full range). PT 10 endorsed both, and the knee was fine, but the plan's guardrail is one change per exercise now that the PT's approval isn't the brake.
5. **Protein and sodium.** The week averaged 130 g protein (target 150–160) and 4,136 mg sodium (over 2,300 every day): quiet days run ~112 g. Fish once.
6. **Weight:** 157.2 lb average (+1.1 lb). One week, mixed times of day: no change to the target. Review at 10/25 with two weeks of readings.
7. **Logging:** session minutes and RPE are now reported for most sessions. The Sunday checks started 10/18 (photo clean, SLR no lag, flexion full); the Sunday weigh-in is a morning one from here.
8. **Posterior-knee tightness** (9/30) not reported since. If it ever becomes calf pain or calf swelling: surgeon, not Claude.

---

## 10. Next milestones

- [x] **Sun 10/18 AM:** weigh-in 158.4, first extension photo (clean), SLR no lag, flexion full · [ ] Session B (Phase 3 doses)
- [ ] **Tue 10/20:** Knot III ties, Phase 4 opens · first pivot bout · Phase 4 Session A (goblet squat, knee extension PT style, RFESS)
- [ ] **Book PT;** ask for the hamstring test (both sides) and the early plyometric prep
- [ ] Daily minimum **7 of 7**: a graded morning check every day (it reopens the optional items for the week of 10/25); the heel prop on Sunday
- [ ] Upper **2 of 2** (Mon B, Thu A): opens Block 1 on 10/25 · bench 110 · bike 24 → 27 → 30
- [ ] Throwing 3 sessions (week 2, speed control) + film; the pivot only on knee days
- [ ] Protein ≥150 g on quiet days; a second fish meal
- [ ] **Sun 10/25:** checkpoint · Phase 4 Session B written from Sunday's result · Block 1 if 2 of 2
