# Sport Plan — Ultimate (handler) · offseason Oct 2026 → late spring 2027

*The operating layer for the sport: skills, the progression by rehab phase, weekly placement, logging, reviews. The content of the skill work is the guide, `Ultimate_Offseason_Development_Guide.md` (kept as written). This file decides when each part of it is allowed. Set up Fri 2026-10-09 (POD 46, Phase 3); the phase gates were set by him the same day: seated or standing throwing at easy effort now, pivoting from Phase 4, Phases 5–6 by the logic in §3.*

**Source priority:** latest PT/surgeon instruction → rehab master plan → recovery state and Working Rules → Whole-Athlete Add-On → **this file** → the guide → logs. Nothing here moves a written left-knee item of the rehab plan; when a phase and the guide's calendar disagree, the phase wins (the guide's own Rule 7: "Whenever movement and ACL recovery conflict, rehab clearance wins"). The add-on's §10 "standing throws" are the off-season program's med-ball power throws, a different element; disc throwing is set here.

Read a section: `python3 engine/darrow.py doc sport <number or words>`; the guide: `doc sportguide "week 3"`.

## 1. The sport, the season, the setup

- **Sport / position:** ultimate · handler. **Throws right-handed; pivot foot: the left** (the graft side). Every pivot and step-out turns on the left knee, which is why pivots have their own gate (§3).
- **Where:** a net through the Ohio winter (indoors or out) and the field outdoors when the weather allows. A partner sometimes, never relied on: every session in this plan works solo (§6).
- **Goal:** return as a more complete elite handler (guide, "The Goal"): speed and touch control, inside and around breaks, mark manipulation, scoober and hammer both hands, deeper and more catchable hucks, better defensive positioning and footwork.
- **Season:** the offseason runs from the week of Sun 10/11 (guide Week 1) to late spring 2027.
- **The rehab clock:** ultimate is a cutting and pivoting sport. The master plan treats **nine months (Mon 2027-05-24) as a minimum reference point** for return to competition, after the return-to-sport battery and clearance. The guide's late-spring target is realistic only if every gate falls on time; criteria decide, not the calendar.

| Rehab phase (Knot that opens it) | Earliest by the calendar | Opens for the sport |
|---|---|---|
| 3 (now; Knot II tied) | — | seated or square-stance standing throwing at easy effort; film |
| 4 (Knot III) | Tue 10/20 | **the throwing pivot and step-out**, planned, walking tempo; game-range long throws; defense Level 2a |
| 5 (Knot IV) | Tue 11/17 | max-intent long throws; game-tempo pivots and shimmies; throwing after a straight-line walk or jog |
| 6 (Knot V) | ~Thu 12/24 (month 4) | throwing after planned decelerations and cuts; defense Level 2b (planned shuffles and patterns) |
| 7 (Knot VI) | ~Wed 2/24/2027 (month 6) | live marks, reactive work, give-go, hard pivots at game speed; defense Level 3 |
| 8 (Knot VII) | ~Mon 5/24/2027 (month 9) | team practice, small-sided play, then competition; defense Level 4 |

The graft's weakest window runs through ~Mon 11/16. A quiet knee is not evidence that pivoting, lateral or reactive work can come forward.

## 2. Skills (the `skill` ids for `sport_log.csv`)

| id | Covers (guide priority) | First allowed |
|---|---|---|
| `control` | speed, spin, height, edge, shape, distance, arrival angle; the three-speed ladder; same target, different arrival (1) | Phase 3 (now) |
| `breaks` | inside and around releases, high/low releases, quick release; the pivot and step-out from Phase 4 (2) | Phase 3 (release shapes) |
| `deception` | upper-body fakes (shoulder, head, arm), rhythm and release-height changes; pivot fakes and shimmies from Phase 4; against a live mark from Phase 7 (2) | Phase 3 (upper body) |
| `overheads` | scoober and hammer, dominant and off-hand (3) | Phase 3 |
| `hucks` | long throws: BH and FH, IO / flat / OI, three gears (controlled, game range, stretch) (4) | Phase 3 (controlled gear, square stance) |
| `defense_iq` | film and study: stance, leverage, hips, first steps, force, upline and breakside positioning (5, Level 1) | Phase 3 |
| `defense_footwork` | Level 2a walking-pace stance and positioning (Phase 4) → 2b planned shuffles and patterns (Phase 6) → 3 reactive (Phase 7) → 4 game movement (Phase 8) (5) | Phase 4 |

## 3. The progression by phase

### The logic

1. **The knee's load in throwing is the pivot.** The left foot stays planted while the body turns over it, and the step-out loads it again. A square-stance throw turns the trunk above still hips and feet; that is the line between Phase 3 and Phase 4.
2. **One variable at a time, in the master plan's own order:** step width → tempo → direction (one side, then the other, then alternating) → force (effort) → movement before the throw → unpredictability (planned → chosen → cued → reactive). It is the shape of the plan's lateral-agility and cutting progressions ("planned → faster → greater angle → greater force → multiple possible directions → reactive").
3. **Each new variable is a batch item.** It is judged by the next morning (the Working Rules' clean morning); a morning that isn't clean reverses it. The Working Rules' one-change-per-exercise rule applies to the pivot work as to any exercise.
4. **Mechanics end the set before effort does** (Working Rules, load rule 5). The pivot turns on the ball of the left foot with the heel light, the knee tracking over the toes, the hips turning with the foot. Stop the set at: the knee drifting inside the foot, a flat foot grinding into the floor, a wobbling step-out, front-of-knee or joint-line pain above 2 (load rule 4).
5. **Pivots are knee load and ride the loaded days;** the days between stay pivot-free (§5).
6. **Effort is the last dial.** Max-intent rotation waits for Phase 5, where the add-on also puts power throws.
7. **Footing.** Dry, flat ground. No ice, frost, mud or wet leaves. No high-grip rubber gym floors for pivots: the sole grabs and the turn goes into the knee. On grass, turf shoes rather than long cleats while pivots are new. Cold days: a longer warm-up before the first fast throw.
8. **Criteria over calendar.** A phase's throwing opens when its Knot ties, not on its date.

### Phase 3 — now (Knot II)

- **Allowed:** seated (left foot resting, not braced) or **standing with both feet planted**: square stance, weight even, no pivot, no step-out. **Easy effort** (RPE ≤5–6; "fast" in the three-speed ladder means crisp, not maximal).
- **What that covers:** FH and BH control and three speeds; inside and around release shapes and angles; high and low releases; quick release from a compact set; scoober and hammer with both hands; upper-body fakes (shoulder, head, arm, rhythm, release height); long throws at controlled range from the square stance (outdoors); film (defense Level 1). Walking to collect discs is fine.
- **Not yet:** pivots, step-outs, shimmies with the feet, game- or stretch-range long throws, throwing after movement.

### Phase 4 — the pivot (Knot III; earliest Tue 10/20)

- **Opens:** the throwing pivot on the left foot and the step-out, planned, at walking tempo, against the net or an imaginary mark; game-range long throws (≤~80% effort) with a step and pivot; defense Level 2a.
- **First bout:** ~20–30 pivot throws, **one direction** (whichever feels easier), a short step (about shoulder width), walking tempo.
- **Ladder, one rung per bout after a clean morning:** the other direction → a wider step (full stance) → +10 throws → both directions in a set order → slow planned shimmies (weight shifts on the pivot) → game-range long throws with a step and pivot.
- **Dose:** two pivot bouts a week, on knee-session days (§5); up to ~60 pivot throws a bout by the end of Phase 4. Square-stance throwing continues on the other days as in Phase 3.
- **Defense Level 2a:** stance, mark positioning, approaching a thrower at walking pace, planned small steps; mirroring only a known pattern.
- **Still out:** max-intent throws, game-tempo shimmies, throwing after jogging or running, any reaction.

### Phase 5 — return to running (Knot IV; earliest Tue 11/17)

- **Max-intent long throws** (stretch range): up to 8–10 a session, after a full warm-up and some game-range throws, on dry ground; one such session a week to start, then two.
- **Game-tempo pivots and shimmies,** both directions, planned sequences (fake → opposite release at speed); quick release off the pivot.
- **Throwing after movement, only what the running progression has already cleared:** walk or jog in a straight line to a spot, slow to a stop over 3–4 steps, set the pivot, throw. No hard plants, no cuts.
- **Moving receivers** when a partner is there (they move; he doesn't need to).
- **Defense:** Level 2a with a straight-line jog approach and a gradual stop.
- **Dose:** up to three pivot bouts a week, still on loaded days (knee or running days).
- **Still out:** cuts, hard stops, lateral shuffles at speed, any reaction.

### Phase 6 — power, plyometrics, sprinting, agility (Knot V; earliest ~12/24)

- **Throwing after planned decelerations and cuts,** each only at the level the plan's deceleration (1–5) and cutting progressions have reached that week. For example: 45° planned cut → catch → set the pivot → throw.
- **Defense Level 2b:** controlled shuffles, planned handler-defense patterns at moderate speed, approach-and-break-down at the deceleration level reached, planned mark-and-recover.
- **Long throws** after a jog approach; quick release after planned movement; normal long-throw volume.
- **Planned two-option sequences:** he chooses before the rep, not in reaction to anything.
- **Still out:** anything reactive (cues, a live mark, mirroring a partner's free movement) → Phase 7.

### Phase 7 — reactive (Knot VI; earliest ~2/24/2027)

Live and active marks, short stall, live resets, give-go at increasing speed, throwing after reactive cuts, hard pivots at game speed (the plan's "criteria before hard cutting/pivoting": quad and hop ≥90%), defense Level 3 (mirror work, partner cues, live marking, reactions to fakes).

### Phase 8 — team and games (Knot VII; earliest ~5/24/2027)

The master plan's return-to-competition progression: non-contact team practice → restricted team drills and small-sided work → full practice → restricted competition minutes → unrestricted. Defense Level 4.

## 4. Drills by phase

| Guide work | Phase 3 (now) | Phase 4 | Phase 5 | Phase 6+ |
|---|---|---|---|---|
| Warm-up (5–8 min easy throwing) | seated or square | + a few slow pivots | + jog | normal |
| Three-speed ladder, FH and BH | square; "fast" = crisp | + off the pivot | full speed | after movement |
| Same target, different arrival | yes | yes | yes | yes |
| Inside / around breaks | release shape only, no step | with the pivot and step-out, planned | game tempo | after planned movement; live mark at Phase 7 |
| High / low releases | yes | + from the step-out | yes | yes |
| Quick release, compact setups | yes | yes | off the pivot | after movement |
| Fakes | upper body | + pivot fakes, slow shimmies | game-tempo shimmies | planned two-option sequences |
| Scoober, hammer (both hands) | yes, several distances | yes | yes | yes |
| Long throws: controlled gear | square stance | with a step and pivot | yes | yes |
| Long throws: game range (70–85%) | — | yes | yes | yes |
| Long throws: stretch range (max intent) | — | — | yes (≤8–10 a session) | yes |
| Long-throw consistency test (Weeks 8, 12) | controlled range, square | game range | game range | game range |
| Defense Level 1: film | yes | yes | yes | yes |
| Defense Level 2a: stance, positioning, walking approach | — | yes | + jog approach | yes |
| Defense Level 2b: planned shuffles and patterns | — | — | — | yes |
| Defense Level 3: reactive | — | — | — | Phase 7 |
| Defense Level 4: game movement | — | — | — | Phase 8 |

## 5. The week

- **Three skill sessions, 90–110 min in all, plus 10–15 min of film** (guide §1).
- **Phase 3 (now):** Wed Session A (control + breaks), Fri Session B (deception + overheads), Sat Session C (long throws). Any day works; the point is three. Not knee load: like an add-on session, fine next to anything, never instead of the daily minimum.
- **From Phase 4, pivots are knee load and share the knee-session days** (Sun and Tue/Wed): a pivot bout of 15–25 min runs as its own bout, before the knee session or at least 2–3 hours after it, never straight after the main lifts when the quad is tired. The other days stay pivot-free (square-stance control, overheads, upper-body fakes, net work). In practice the pivot parts of Sessions A and B move to the knee days and the rest of the throwing stays where it was. From Phase 5 the same rule covers running days.
- **Minimum-viable week:** 2 × 20 min throwing + 1 × 25 min long throws. That is enough.
- **Missed sessions are not repaid** and never doubled (guide Rule 1; Working Rules load rule 10). High rehab or training load → less skill volume (Rule 3). Stop while you still want a few more throws (Rule 2). One primary purpose per session (Rule 4).
- **The Ohio winter:** the net on bad days; long-throw work bunched into the dry, calm days outdoors (a skipped outdoor day is not repaid either). Wind goes in `notes` on long-throw rows.
- The weekly template (`real/config.json`) carries `sport` on Wed, Fri and Sat from the week of 10/11. When Phase 4 opens, the template stays (three sessions); where the pivot bouts sit is this section's rule.

## 6. Solo first: the net, the field, a partner

- **The net:** tape target zones (a 3 × 3 grid, a release-height line) for `on_target` counts by speed, shape and release; overheads into the net; long-throw mechanics into the net when the field is out (no flight feedback, so no huck test indoors).
- **The field, solo:** a stack of discs (10 or more), cones at paced or measured ranges, a target zone about 5 m across. A long throw is **usable** if it lands in the zone at the chosen range with the intended shape; **lane** is left or right of the line; **shape** is IO / flat / OI as intended. Walk to collect.
- **A partner (bonus):** catchability judged by a real catch; moving receivers from Phase 5; a passive mark from Phase 4 (standing still), an active one from Phase 7.

## 7. The first 12 weeks, by the calendar

Weeks run Sun–Sat. Each week's content is in the guide (`doc sportguide "week N"`); this table is how it runs at the phase the calendar allows at the earliest. The Knots decide.

| Wk | Dates | Guide focus | Earliest phase | How it runs |
|---|---|---|---|---|
| 1 | 10/11–10/17 | Baseline | 3 | seated or square: comfortable FH/BH, three speeds, compact inside/around releases, dominant scoober; controlled-range long throws outdoors; note what feels different. Film: starting position |
| 2 | 10/18–10/24 | Speed control | 3 → 4 from 10/20 if Knot III ties | the guide's 70–85% long throws wait for Phase 4; first pivot bout on a knee day once it opens |
| 3 | 10/25–10/31 | Inside breaks | 3/4 | inside release shapes; with the pivot and a short step once Phase 4 opens (one direction first) |
| 4 | 11/1–11/7 | Around breaks · **month check** | 3/4 | around shapes; the second pivot direction is its own rung; dominant hammer begins |
| 5 | 11/8–11/14 | Same throw, different arrival | 4 | touch work suits any phase |
| 6 | 11/15–11/21 | Deception | 4 → 5 from 11/17 | slow pivot fakes and shimmies in Phase 4; game tempo only from Phase 5. The graft window ends ~11/16 |
| 7 | 11/22–11/28 | Off-hand scoober | any | begin close |
| 8 | 11/29–12/5 | Long-throw consistency · **month check** | 4/5 | the test at game range, outdoors on a dry day (controlled range from the square if still Phase 3) |
| 9 | 12/6–12/12 | Quick release | any | compact setups; off the pivot from Phase 4 |
| 10 | 12/13–12/19 | Off-hand hammer | any | start conservatively |
| 11 | 12/20–12/26 | Combinations | 5 → 6 from ~12/24 | combinations of planned pieces; after movement only as far as the running and deceleration progressions reach |
| 12 | 12/27–1/2 | Test + consolidate · **12-week review** | — | repeat the Week 8 test; overheads rated weapon / usable / developmental |

## 8. January → late spring

| Guide block | Needs | Notes |
|---|---|---|
| Jan–Feb · Expansion | Phases 5–6 | controlled defensive movement = Level 2b (Phase 6) |
| Feb–Mar · Integration | Phase 7 for live marks, throwing after reactive movement, reactive D | moving receivers are fine from Phase 5; throwing after planned movement from Phase 6 |
| Mar–Apr · Pressure | Phase 7 | active mark, handler movement, give-go, reactive defense, hard pivots at game speed |
| Apr–May · Game transfer | Phase 8 | small-sided and possession games come after the return-to-sport battery |
| Late spring · Sharpening | Phase 8 | competition by the return-to-competition progression |

## 9. Logging

`python3 engine/darrow.py sport add '<json rows>'` into `real/logs/sport_log.csv`: `date, session, skill, drill, sets, reps, minutes, rpe, metric, value, notes`.

- **session:** `A`, `B`, `C`, `film`, `test`, `review`.
- **skill:** one of the seven ids in §2 (`darrow.py check` flags anything else). A session that works two skills is two rows.
- **drill:** what was done, with the stance and place: `seated`, `square`, `pivot FH side` / `pivot BH side` / `pivot both`, `after jog`; `net` or `field`; the hand for overheads ("off-hand scoober, net, square").
- **reps:** pivot throws are counted as reps on pivot rows (the Phase 4 dose).
- **metric / value** (only when measured; the guide says look for patterns, not percentages):
  - `on_target` · "7/10" (a speed, shape or release on a net zone or field target)
  - long-throw test (Weeks 8, 12): `usable`, `lane`, `shape` · "x/10", one row per side
  - `range_m` · the distance of a gear (controlled / game / stretch in `drill`)
  - `status` · weapon / usable / developmental (overheads, Week 12)
  - `rating` · 1–5 (session `review`: one row per category of the month check or the 12-week review)
- **notes:** the week's question answered, what felt different, wind on outdoor long throws.
- Example: `[{"date":"2026-10-14","session":"A","skill":"control","drill":"three-speed ladder FH+BH, square, net","minutes":15,"rpe":4},{"date":"2026-10-14","session":"A","skill":"breaks","drill":"inside/around release shapes, square, net","minutes":12,"rpe":4,"metric":"on_target","value":"6/10"}]`
- Work past the current phase (a pivot in Phase 3, max intent in Phase 4) is logged truthfully and named in one plain sentence, like off-plan knee work. No scolding.

## 10. Reviews

- **Weekly:** the guide's weekly question, answered in `notes` of that week's last session; the checkpoint's Sport section summarises sessions vs plan, the phase, and any new rung of the pivot ladder.
- **Monthly** (end of Weeks 4, 8, 12, then every four weeks): the 1–5 ratings as `review` rows, and the guide's seven review questions answered in that week's checkpoint (`real/checkpoints/<Sunday>.md` → Sport), including "what does my rehab now allow that it did not last month?" against §3.
- **Video** occasionally (guide Rule 8), especially the first pivot bouts from the side and front (the knee over the toes, the heel light): note the date in `notes`.

## 11. The PT

He set the throwing phases himself (10/9); Nick's 10/9 instruction leaves progression to the master plan, and nothing here changes a written rehab item. For awareness at the next visit, one line: "I'm throwing seated and square-stance at easy effort; pivots on the left from Phase 4, max-intent throws from Phase 5." Worth asking:

1. Pivoting on the left (the graft side) from Phase 4: anything he wants watched? (Here: the ball of the foot, the heel light, the knee over the toes.)
2. Max-intent long throws from Phase 5: any reason to wait?

## 12. Still to confirm

- How many discs (a solo long-throw test needs about 10).
- Shoes for pivoting on grass and on the net's floor.
