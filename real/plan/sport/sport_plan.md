# Sport Plan — Ultimate (handler) · offseason Oct 2026 → late spring 2027

*The operating layer for the sport: skills, rehab gates, weekly placement, logging, PT questions. The content of the skill work is the guide, `Ultimate_Offseason_Development_Guide.md` (kept as written). This file decides when each part of it is allowed. Set up Fri 2026-10-09 (POD 46, Phase 3).*

**Source priority:** latest PT/surgeon instruction → rehab master plan → recovery state and Working Rules → Whole-Athlete Add-On → **this file** → the guide → logs. Nothing here moves a left-knee item earlier than the rehab plan allows; when a stage and the guide's calendar disagree, the stage wins (the guide's own Rule 7: "Whenever movement and ACL recovery conflict, rehab clearance wins").

Read a section: `python3 engine/darrow.py doc sport <number or words>`; the guide: `doc sportguide "week 3"`.

## 1. The sport and the season

- **Sport / position:** ultimate · handler.
- **Goal:** return as a more complete elite handler (guide, "The Goal"): speed and touch control, inside and around breaks, mark manipulation, scoober and hammer both hands, deeper and more catchable hucks, better defensive positioning and footwork.
- **Season:** the offseason runs from the week of Sun 10/11 (guide Week 1) to late spring 2027.
- **The rehab clock:** ultimate is a cutting and pivoting sport. The master plan treats **nine months (Mon 2027-05-24) as a minimum reference point** for return to competition, after the return-to-sport battery and clearance, not automatic clearance. The guide's late-spring target is realistic only if every gate below falls on time; criteria decide, not the calendar.

| Rehab phase (Knot that opens it) | Earliest by the calendar | What it opens for the sport |
|---|---|---|
| 3 (now; Knot II tied) | — | seated throwing (S0), film |
| 4 (Knot III) | Tue 10/20 | standing square-stance throwing (S1), with the PT's OK |
| 5 (Knot IV) | Tue 11/17 | max-effort standing throws (S2), with the PT's OK; jogging |
| 6 (Knot V) | ~Thu 12/24 (month 4) | planned pivots and step-outs (S3), controlled defensive footwork, with the PT's OK |
| 7 (Knot VI) | ~Wed 2/24/2027 (month 6) | live marks, reactive work, throwing on the move (S4) |
| 8 (Knot VII) | ~Mon 5/24/2027 (month 9) | team practice, small-sided play, then competition (S5) |

The graft's weakest window runs through ~Mon 11/16. A quiet knee is not evidence that pivoting, lateral or reactive work can come forward.

## 2. Skills (the `skill` ids for `sport_log.csv`)

| id | Covers (guide priority) | First allowed |
|---|---|---|
| `control` | speed, spin, height, edge, shape, distance, arrival angle; the three-speed ladder; same target, different arrival (1) | S0 now |
| `breaks` | inside and around releases, high/low releases, quick release; the pivot and step-out footwork from S3 (2) | S0 now (release shapes) |
| `deception` | upper-body fakes (shoulder, head, arm), rhythm and release-height changes; shimmies and pivot suggestion with the feet from S3; against a live mark from S4 (2) | S0 now (upper body) |
| `overheads` | scoober and hammer, dominant and off-hand (3) | S0 now |
| `hucks` | long throws: BH and FH, IO / flat / OI, three gears (controlled, game range, stretch) (4) | S0 now (controlled gear, seated) |
| `defense_iq` | film and study: stance, leverage, hips, first steps, force, upline and breakside positioning (5, Level 1) | now |
| `defense_footwork` | Level 2 controlled → Level 3 reactive → Level 4 game movement (5) | Knot V, with the PT's OK |

## 3. Stages and gates

Each stage needs its Knot **and** the PT's OK where marked. Throwing a disc is not in the rehab plan, so every standing or moving stage goes past the PT first (Working Rules: out-of-plan items are mentioned to the PT first). Record each clearance in `real/visits/` and update this table.

| Stage | What it allows | Gate |
|---|---|---|
| **S0 · Seated** | Sitting on a bench or chair, left foot resting flat (or on a low stool), not braced, pelvis still: the throw comes from the arm and upper trunk. Controlled effort, RPE ≤6–7, no max-intent throws. Forehand and backhand at short to medium range, three speeds, inside/around release shapes, high/low releases, overheads both hands, upper-body fakes, quick-release mechanics, controlled-gear long throws within seated reach. No kneeling of any kind on the left (the harvest site) | **Now** (Knot II; seated upper-body work is not a knee variable, add-on §2) |
| S0+ · Seated, max intent | Full-effort seated throws (stretch-range attempts) | PT OK first (like the add-on's seated rotational throws) |
| **S1 · Standing, square stance** | Both feet planted, weight even, no pivot, no step, hips quiet. Everything in S0 standing; long throws up to game range at ~70–85% effort (guide Week 2) | Knot III (Phase 4) **and** PT OK |
| S2 · Standing, max intent | Stretch-range long throws from a square stance | Knot IV (Phase 5) **and** PT OK (add-on §10: standing throws, Phase 5–6) |
| **S3 · Planned pivot and step-out** | The throwing pivot and step-outs at walking pace against an imaginary or passive mark: compact pivots, breaks around a mark, shimmies with the feet, pivot suggestion; throwing after a walk or jog; defense Level 2 | Knot V (Phase 6: planned lateral agility) **and** PT OK. From here a throwing session is knee load: it counts as a loaded day for the no-back-to-back rule and is judged by the next morning, until the PT says otherwise |
| **S4 · Live and reactive** | Active mark, short stall, live resets, throwing after cutting, give-go, hucks to real cuts; defense Level 3 (mirror work, live marking, reactions to fakes) | Knot VI (Phase 7: reactive agility and cutting progressions) |
| **S5 · Team and games** | Non-contact team practice → restricted small-sided work → full practice → restricted competition minutes → unrestricted (master plan, return-to-competition progression); defense Level 4 | Knot VII (return-to-sport battery and clearance) |

**Pivot foot.** A right-handed thrower's usual pivot foot is the left: the graft side. Every pivot and step-out then rotates on the left knee, which is why S3 waits for Phase 6. If the PT clears a gentler version earlier (for example pivoting on the right foot while the left steps out), it is recorded in `real/visits/` and changes this table.

## 4. Drills by stage

| Guide work | S0 seated (now) | S1 standing square | S3 and later |
|---|---|---|---|
| Warm-up (5–8 min easy throwing) | seated | standing | — |
| Three-speed ladder (soft → medium → fast), FH and BH | yes; "fast" stays controlled | full | full, after movement from S3 |
| Same target, different arrival (float, normal, fast; change shape) | yes | yes | yes |
| Inside / around breaks | release shape and angle only, no step | same, standing | with the pivot and step-out (S3), against a live mark (S4) |
| High / low releases | within seated reach | yes | yes |
| Quick release, compact setups (Week 9) | yes: it needs no pivot | yes | yes |
| Fakes: shoulder, head, arm, rhythm hesitation | yes | yes | + shimmies and pivot suggestion with the feet (S3) |
| Scoober, hammer (dominant, off-hand) | short range first, several distances | longer | yes |
| Huck lab: controlled gear | seated controlled range | standing | yes |
| Huck lab: game range (70–85% effort) | — | yes | yes |
| Huck lab: stretch range | — (S0+ with PT OK) | S2 | yes |
| Huck consistency test (Weeks 8 and 12) | seated version (controlled range) | game range | game range |
| Defense Level 1: film and study | yes | yes | yes |
| Defense Level 2: controlled stance changes, planned lateral steps, approach a thrower | — | — | S3 (Knot V, PT OK) |
| Defense Level 3: mirror, partner cues, live marking, reactions | — | — | S4 (Knot VI) |
| Defense Level 4: live handler D, give-go, transition, small-sided | — | — | S5 (Knot VII) |

## 5. The week

- **Three skill sessions, 90–110 min in all, plus 10–15 min of film** (guide §1). Default placement: **Wed Session A** (control + breaks), **Fri Session B** (deception + overheads), **Sat Session C** (huck lab). Any day works; the point is three. Film on any day.
- **Minimum-viable week:** 2 × 20 min throwing + 1 × 25 min long throws. That is enough.
- **Missed sessions are not repaid** and never doubled (guide Rule 1; Working Rules load rule 10).
- **Never instead of the daily minimum.** At S0–S2 a throwing session is like an add-on session: not a loaded day, not a knee variable, fine next to anything. From S3 it is knee load (§3).
- **High rehab or training load → less skill volume** (guide Rule 3). Stop while you still want a few more throws (Rule 2). One primary purpose per session (Rule 4).
- The weekly template (`real/config.json`) carries `sport` on Wed, Fri and Sat from the week of 10/11.

## 6. The first 12 weeks, by the calendar

Weeks run Sun–Sat. The stage column is the earliest the calendar allows; the gates decide. Each week's content is in the guide (`doc sportguide "week N"`).

| Wk | Dates | Guide focus | Earliest stage | How it runs |
|---|---|---|---|---|
| 1 | 10/11–10/17 | Baseline | S0 | seated: comfortable FH/BH, three speeds, compact inside/around releases, dominant scoober; seated controlled-range long throws; note what feels different. Film: starting position |
| 2 | 10/18–10/24 | Speed control | S0 → S1 from 10/20 if Knot III ties and the PT agrees | 70–85% long throws only once standing (S1); seated stays controlled |
| 3 | 10/25–10/31 | Inside breaks | S0/S1 | inside release shapes; imaginary mark, upper-body threats only |
| 4 | 11/1–11/7 | Around breaks · **month check** | S0/S1 | around shapes, high/low releases; dominant hammer begins |
| 5 | 11/8–11/14 | Same throw, different arrival | S0/S1 | touch work suits any stage |
| 6 | 11/15–11/21 | Deception | S0/S1 (S2 from 11/17 with the PT's OK) | upper-body fakes only: no shimmy footwork or pivot suggestion until S3. The graft window ends ~11/16 |
| 7 | 11/22–11/28 | Off-hand scoober | any | begin close |
| 8 | 11/29–12/5 | Long-throw consistency · **month check** | S1/S2 | the test at the stage reached (seated test if still S0) |
| 9 | 12/6–12/12 | Quick release | any | compact setups need no pivot |
| 10 | 12/13–12/19 | Off-hand hammer | any | start conservatively |
| 11 | 12/20–12/26 | Combinations | S2 → S3 from ~12/24 with the PT's OK | combinations stay upper-body until S3 |
| 12 | 12/27–1/2 | Test + consolidate · **12-week review** | — | repeat the Week 8 test; overheads rated weapon / usable / developmental |

## 7. January → late spring

| Guide block | Needs | Notes |
|---|---|---|
| Jan–Feb · Expansion | S2–S3 | controlled defensive movement = Level 2 (Knot V) |
| Feb–Mar · Integration | S4 for live marks, throwing after movement, reactive D | moving receivers are fine from S1 (the receiver moves, not him) |
| Mar–Apr · Pressure | S4 | active mark, handler movement, give-go, reactive defense |
| Apr–May · Game transfer | S5 | small-sided and possession games come after the return-to-sport battery |
| Late spring · Sharpening | S5 | competition by the return-to-competition progression |

## 8. Logging

`python3 engine/darrow.py sport add '<json rows>'` into `real/logs/sport_log.csv`: `date, session, skill, drill, sets, reps, minutes, rpe, metric, value, notes`.

- **session:** `A`, `B`, `C`, `film`, `test`, `review`.
- **skill:** one of the seven ids in §2 (`darrow.py check` flags anything else). A session that works two skills is two rows.
- **drill:** what was done, with the stage and hand where it matters ("three-speed ladder FH, seated", "off-hand scoober, 10 m, seated").
- **metric / value** (only when measured; the guide says look for patterns, not percentages):
  - `on_target` · "7/10" (a speed or a shape on a target)
  - huck test (Weeks 8, 12): `usable`, `lane`, `shape` · "x/10", one row per side
  - `range_m` · the distance of a gear (controlled / game / stretch in `drill`)
  - `status` · weapon / usable / developmental (overheads, Week 12)
  - `rating` · 1–5 (session `review`: one row per category of the month check or the 12-week review)
- **notes:** the week's question answered, what felt different.
- Example: `[{"date":"2026-10-14","session":"A","skill":"control","drill":"three-speed ladder FH+BH, seated","minutes":15,"rpe":4},{"date":"2026-10-14","session":"A","skill":"breaks","drill":"compact inside/around release shapes, seated","minutes":12,"rpe":4}]`

## 9. Reviews

- **Weekly:** the guide's weekly question, answered in `notes` of that week's last session; the checkpoint's Sport section summarises sessions vs plan and the stage.
- **Monthly** (end of Weeks 4, 8, 12, then every four weeks): the 1–5 ratings as `review` rows, and the guide's seven review questions answered in that week's checkpoint (`real/checkpoints/<Sunday>.md` → Sport), including "what does my rehab now allow that it did not last month?" against §3.
- **Video** occasionally (guide Rule 8): note the date in `notes`.

## 10. For the PT

Throwing is not in the rehab plan, so these go to the PT; record each answer in `real/visits/` and update §3:

1. **Seated throwing** (left foot resting, not braced, controlled effort): fine now? Max-effort seated throws: when?
2. **Standing throwing from a square stance** (no pivot, no step): from Phase 4 (earliest Tue 10/20), or later?
3. **The throwing pivot and step-out** (planned, walking pace): which phase? My pivot foot is the left if I throw right-handed. Is pivoting on the other foot a sensible bridge?
4. **Max-effort standing long throws:** when? (The add-on puts standing rotational throws at Phase 5–6.)
5. **Controlled defensive footwork** (planned stance changes, lateral steps at walking pace): Phase 6 as the plan's lateral agility, or earlier?
6. **Half-kneeling throwing** (right knee down, left foot flat) as a step between seated and standing?

## 11. Still to confirm

- Throwing hand (decides the pivot foot).
- Who or what he throws to (partner, net, wall) and where (indoor / outdoor in winter); discs on hand.
