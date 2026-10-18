# NOW — the Ledger

*Real numbers only. Nothing from the story appears on this page. Claude keeps the top section to what stands until something changes: the plan in force, the next PT visit, the gate, flags, open items. The engine owns every count and date in the block at the bottom, regenerated on every `sync`. Map of every file: `real/README.md`. History: `real/checkpoints/`. PT notes: `real/visits/pt_notes.md`. Measurements: `python3 engine/darrow.py measures`.*

## Plan in force · Phase 3 → **Phase 4 from Tue 10/20** · State Sun 10/18

Program: `real/state/recovery_state.md` (Sun 10/18): `python3 engine/darrow.py doc state "this week"`, then `doc state "session b"` / `"session a"` / `"pivot bout"`. Rules: `real/plan/working_rules.md` (`doc rules "load rules"`). Where each fact lives: `real/README.md`. Nick (10/9): progression is up to the master plan, no PT approval needed, never push through pain. Last week's review: `real/checkpoints/2026-10-18.md`.

- **Daily minimum (every day):** morning check (swelling **grade**, extension side by side, pain, stiffness, catch, **wellness 1–5**) + **one weighted heel prop, 10 lb, 10 min** + creatine. Fri 10/16's missed heel prop costs this week its optional items (no accessory day, no Saturday power & mobility).
- **Sun 10/18:** weigh-in (5:30 PM), the **first extension photo**, SLR lag, flexion vs the right → **Session B, Phase 3, the last time** (step-down 3 × 10 · SL sit-to-stand 18" · RDL 50 lb/hand · hamstring curl 3 × 10 @ 30 · State §6).
- **Tue 10/20: Knot III, Phase 4 opens.** Pre-session check → **first pivot bout** (~20–30 throws, one direction, short step, walking tempo; before the session or 2–3 h after) → **Phase 4 Session A**: goblet squat 25 lb × 2 × 10 to an 18" box · cable knee extension full range, both legs up, left alone lowering ~3 s · **rear-foot elevated split squat (new)** · hamstring curl · heel raise 3 × 15 · step-up, heel tap, BOSU, isometric · posture cooldown.
- **Upper:** **Mon 10/19 Upper B** (session 4: incline 85 × 3 × 8–10; one-arm DB row new) → **Thu 10/22 Upper A** (session 5: **bench 110 × 3 × 8**, pull-ups 3 × 6 band-assisted, DB row 20s). Finisher with the **Copenhagen on both sides** (PT 11). Block 1 from 10/25 if both run.
- **Bike, legs only, easy:** Mon 24 → Thu 27 → Sat 30.
- **Throwing, week 2 (speed control):** Wed A soft / normal / fast, FH and BH · Fri B scoober speeds and heights, upper-body fakes before breaks · Sat C long throws · film 10–15 min (handler defenders' hips). **The pivot only on knee days** (Tue this week), one rung per bout; the other days stay square. No max intent.
- **Nutrition:** 3,000 kcal · 150–160 g protein · carbs ~350–400 g · fat ~85–100 g · creatine daily. This week's two fixes: a shake or Greek yogurt by mid-afternoon on any day short of protein; a second fish meal, and a carb anchor at breakfast and dinner in place of one salty snack bag a day.

## Last PT visit · **Sat 10/17, PT 11** (quad test; who not named) · next: **not booked**

PT 11 (his account; `pt_notes.md`, 2026-10-17): isometric quad peak on a torque monitor, **LSI 90.4%** (right 77.2, left 69.8 lb; vs the pre-op right 83.7: 83%). Step-downs passed · Copenhagen okay on both sides · hamstrings not tested. PT 10 (10/15) items are folded into the State (§5–6).

For the next visit (State §5): **book it** · hamstring test, both sides · when the plan's early plyometric prep can start · right knee hyperextension on a heel prop · BOSU home version of the wobble-board drill · BFR / Spanish squat / seated throws if wanted · who treated 10/17 and 10/1.

## Gate · Phase 3 → 4 **met (10/17); Knot III ties Tue 10/20** · next: Phase 4 exit (return-to-run preparation)

- Phase 3 → 4: every criterion met with evidence (State §3); Phase 4 opens on the plan's earliest date, Tue 10/20 (week 9).
- **Phase 4 exit:** quad LSI >80% (90.4% now) · **hamstring LSI ≥80% (untested)** · glute strength ~≥80% symmetry · 10 controlled single-leg squats to ~60° · pain-free low-level impact prep (PT clearance first) · good landings. Running is Phase 5, earliest Tue 11/17.

## Flags and notes for the week

- **Last week closed Triumph** on the engine's score: knee 2 of 2, upper 2 of 2 (the first), throwing 3 of 3, every morning trace, the quad test at 90%.
- **Phase 4 adds three new loads at once:** knee extension through full range, the pivot, and a loaded squat. One change per exercise; the morning verdict decides. The graft's weakest window runs through ~11/16.
- **Daily minimum 6 of 7** (Fri 10/16): it's the item that slips on tired evenings, and it cost this week's optional items.
- **Protein and sodium:** protein averaged 130 g (quiet days ~112 g); sodium over 2,300 mg every day (pizza, wings, bread bites, chips). Fish once.
- **Weight:** 157.2 lb average (+1.1 lb), mixed times of day: no target change. Review 10/25 with two weeks of readings.

## Open items

- **For the sport plan:** how many discs you have (a solo long-throw test needs about 10), and your shoes for pivoting on grass and on the net's floor.
- **Book the next PT visit.** When it's booked, move it in `real/config.json → plan_changes` if it isn't Friday.
- **Tue 10/20, in that day's session:** `python3 engine/darrow.py knot tie 3 --date 2026-10-20 --evidence "Phase 3 -> 4 checklist met: quad LSI 90.4% and step-downs passed (PT 11, 10/17), ROM, gait, effusion, pain flare all met; Nick 10/9: progression follows the master plan"`, then `config.json → rehab`: `current_phase` 4, `phase_entered` 2026-10-20, `next_gate` = the Phase 4 exit (State §3); `sport.stage` to Phase 4 (the pivot on knee days), `stage_since` 2026-10-20; then `sync`.

<!-- engine:start -->
_Engine block, regenerated by `sync` · as of Sun 2026-10-18 · POD 55 · post-op week 8 · Phase 3_

### This week (Sun 10/18 – Sat 10/24)

| Day | Plan | kcal | P (g) | Wt | Cr | Floor | Check | Knee | PT | Add-on | Cond | Sport | Together |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Sun 10/18 | knee | | | | | | | | | | | | |
| Mon 10/19 | cond, upper | | | | | | | | | | | | |
| Tue 10/20 | knee | | | | | | | | | | | | |
| Wed 10/21 | sport | | | | | | | | | | | | |
| Thu 10/22 | cond, upper | | | | | | | | | | | | |
| Fri 10/23 | pt, sport | | | | | | | | | | | | |
| Sat 10/24 | cond, sport | | | | | | | | | | | | |

**Weigh-ins:** 0/3 · last week 157.2 (7 readings)
**Morning swelling grades:** none graded
**Sessions (through Sun):** knee 0/1 · floor full 0/1 · graded morning checks 0/1

**Latest measured:** extension L +2° (10/8) · flexion L 146° (10/8) · quad LSI 90.4% (10/17) · hamstring LSI 70.6% (pre-op) · SL leg press LSI 64.3% (10/8)

**Project:** Get the CRV ready to sell · 1/3 done · next: 2. Take pictures · due Sat 10/31
<!-- engine:end -->
