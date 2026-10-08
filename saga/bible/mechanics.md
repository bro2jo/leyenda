# Mechanics — the game under the story

The numbers live in `engine/rules.json` and are computed by `engine/darrow.py`. This file explains them in-world and for the GM. **Claude never computes XP, attributes or rolls by hand; it runs the engine and reports what it says.**

---

## The Reckoning (the character sheet)

```
⟦ THE RECKONING ⟧
Ser Darrow of Edgemoor · Level 4 · Bound
XP 735 ▰▰▰▱▱▱▱▱▱▱ 1,000
HP 32 · Ember 76 (Steady) · Inspiration 0/4 · Proficiency +2

MIGHT    11 (+0)   the Knight Who Fell: 15
VIGOR     8 (-1)   the Knight Who Fell: 15
FINESSE   9 (-1)   the Knight Who Fell: 18
RESOLVE   9 (-1)   the Knight Who Fell: 12

THE BINDING · Knots tied II of VII · the soft season (do not trust the quiet)
ARTS · Stillwater Stance II · The Mender's Patience I · Warden's Eye I
```

| Element | In the world | Driven by (real side) |
|---|---|---|
| **Level / Rank** | how much Ember he has kindled overall. Ranks: Bound → Kindled → Tempered → Warden-Errant → Emberknight → Unbowed → Warden of the Ember | total XP from every logged deed |
| **Might** | strength of arm and body | knee sessions, PT, upper-body, accessory and power work |
| **Vigor** | endurance, breath, staying power | conditioning minutes, sport sessions |
| **Finesse** | footwork, balance, speed, timing | knee sessions (control), PT, sport skills, later agility work |
| **Resolve** | discipline, patience, honesty with oneself | floor minimum AM+PM, graded morning checks, running sessions as written |
| **Ember** (0–100) | the inner fire: warmth, healing, staying power | rolling 7-day fuel score from logged nutrition (calories and protein vs. target) |
| **Inspiration** (max 4) | moments of clarity; spend to reroll a die or take a bold option | a week with the floor minimum every day; a Triumph week |
| **HP** | how much punishment he can take in a fight | level and Vigor |
| **The Knight Who Fell** | the faint shadow of who he was at Harrow Ford | fixed benchmarks; passing each one is a story moment |

**Attribute growth:** each attribute = base + ⌊√(temper ÷ divisor)⌋. Growth is fast early and slower later, the way real strength returns.

**No XP for overshooting.** Calories and protein stop paying at the target. Doing *more* rehab than prescribed earns nothing extra; running a session *as written* earns Resolve. Following a plan-directed rest (red light) is excused from the week score, not counted against it.

---

## The Binding and its Knots (the real gates)

The Binding has seven Knots (see `world.md`). **A Knot is tied only when the matching real-world gate is passed and recorded** (`python3 engine/darrow.py knot tie N --date … --evidence "…"`), and the evidence must be a PT/surgeon clearance or the plan's measured criteria. The calendar never ties a knot.

While a Knot is untied, the Binding **caps** some attributes. Temper earned above a cap is **banked** and released the moment the next Knot ties, so the hard work done while waiting surges out all at once. That surge is a story moment.

| Knots tied | Vigor cap | Finesse cap | Opens |
|---|---|---|---|
| II (now) | 12 | 10 | Book I: the House of Menders |
| III | 14 | 12 | Book II: walking out; fighting on foot |
| IV | 18 | 14 | Book III: running |
| V | — | 18 | Book IV: leaping, sprinting, stopping |
| VI | — | 22 | Book V: turning at speed |
| VII | — | — | Book VI: the field |

**The soft season:** post-op weeks 6–12. The sheet flags it. In story: Maelis's warnings, the thread loose under the skin, the danger of feeling strong. The story must never reward Darrow for testing the leg early. If he does something reckless with it, it costs him.

---

## Arts (techniques)

Arts are earned by **practice**: the number of separate days a matching kind of real work was logged. Ranks I–V at 1 / 6 / 15 / 30 / 50 days. Each Art is tied to a Knot; practice done before that Knot ties is banked toward the Art (shown as *sealed*).

| Art | Tree | Fed by | Opens at |
|---|---|---|---|
| **The Seated Blade** | Blade | upper-body sessions | now |
| **Iron Grip** | Blade | accessory days | now |
| **Hammerfall** | Blade | power & mobility (throws) | now |
| **Stillwater Stance** | Footing | balance work / knee sessions | now |
| **The Long Breath** | Breath | conditioning ≥10 min | now |
| **The Mender's Patience** | Binding | floor minimum AM+PM | now |
| **Warden's Eye** | Insight | graded morning checks | now |
| **Groundbreaker** | Footing | lower-body sessions | Knot III |
| **Soft Landing** | Footing | landing drills | Knot III |
| **The Long Road** | Breath | running | Knot IV |
| **Thunderstep** | Footing | plyometrics | Knot V |
| **Hawk's Stoop** | Footing | sprinting | Knot V |
| **Anchor** | Footing | deceleration | Knot V |
| **The Turning Blade** | Blade | cutting | Knot VI |
| **The Quickening** | Insight | reactive agility | Knot VI |
| *Sport Arts* | Sport | your sport's skills (set up with `/sport`) | per the sport plan |

In story, Arts are things Darrow can *do*: options in a fight, bonuses on checks, ways out of trouble. Use them. An Art at rank III should visibly change how a scene plays out.

---

## Checks and the chapter tier

- A check is d20 + attribute modifier (+ proficiency if an Art or training applies) + situational bonuses vs. a DC.
- **The chapter tier** comes from the week's real adherence (floor, planned sessions, fuel, morning checks, weigh-ins, logging): **Triumph** (+3), **Hard-won** (+1), **Costly** (+0), **Setback** (−2). It modifies the climax rolls and sets the shape of the climax (see `style.md`).
- **Ember** effects: Blazing +1 to everything; Bright +1 Vigor; Guttering −1 Might and Vigor.
- Results: success, *partial* (within 3: success at a cost), failure. Natural 20 / natural 1 are criticals.
- **Approval** with companions (−100 to +100) moves only with story choices, never with real numbers.

---

## Story state vs. engine state

| File | Owned by | Contains |
|---|---|---|
| `saga/state/darrow.json` | engine (never hand-edit) | the computed sheet |
| `saga/state/rolls.csv`, `spends.csv`, `chapters.csv` | engine | every die rolled, every Inspiration spent, each chapter's frozen tier |
| `saga/state/world.json` | Claude | Book, chapter, location, companions and approval, flags, choices, inventory |
| `saga/state/threads.md` | Claude | open plot threads and plants |
| `saga/state/codex.md` | Claude | canon invented in play |
