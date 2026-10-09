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
| **Might** | strength of arm and body | the real side's leg work, upper-body, accessory and power work |
| **Vigor** | endurance, breath, staying power | conditioning minutes, sport sessions |
| **Finesse** | footwork, balance, speed, timing | the real side's leg work (control), sport skills, later agility work |
| **Resolve** | discipline, patience, honesty with oneself | floor minimum AM+PM, graded morning checks, running sessions as written |
| **Ember** (0–100) | the inner fire: warmth, healing, staying power | rolling 7-day fuel score from logged nutrition (calories and protein vs. target) |
| **Inspiration** (max 4) | moments of clarity; spend to reroll a die or take a bold option | a week with the floor minimum every day; a Triumph week |
| **HP** | how much punishment he can take in a fight | level and Vigor |
| **The Knight Who Fell** | the faint shadow of who he was at Harrow Ford | fixed benchmarks; passing each one is a story moment |

**Attribute growth:** each attribute = base + ⌊√(temper ÷ divisor)⌋. Growth is fast early and slower later, the way real strength returns.

**No XP for overshooting.** Calories and protein stop paying at the target. Doing *more* rehab than prescribed earns nothing extra; running a session *as written* earns Resolve. Following a plan-directed rest (red light) is excused from the week score, not counted against it.

---

## The Binding and its Knots (the real gates)

The Binding has seven Knots (their lore is in `saga/bible/_gm/world.md`, GM only; the reader meets them in the Chronicle). **A Knot is tied only when the matching real-world gate is passed and recorded** (`python3 engine/darrow.py knot tie N --date … --evidence "…"`), and the evidence must be a real-side clearance or the plan's measured criteria. The calendar never ties a knot.

While a Knot is untied, the Binding **caps** some attributes. Temper earned above a cap is **banked** and released the moment the next Knot ties, so the hard work done while waiting surges out all at once. That surge is a story moment.

| Knots tied | Vigor cap | Finesse cap | Opens |
|---|---|---|---|
| II (now) | 12 | 10 | Book I |
| III | 14 | 12 | Book II |
| IV | 18 | 14 | Book III |
| V | — | 18 | Book IV |
| VI | — | 22 | Book V |
| VII | — | — | Book VI |

**The soft season:** the weeks after the Binding when the thread is weakest; the sheet flags it. In story: Maelis's warnings, the thread loose under the skin, the danger of feeling strong. The story must never reward Darrow for testing the leg early. If he does something reckless with it, it costs him.

---

## Arts (techniques)

Arts are earned by **practice**: the number of separate days a matching kind of real work was logged. Ranks I–V at 1 / 6 / 15 / 30 / 50 days. Each Art is tied to a Knot; practice done before that Knot ties is banked toward the Art (shown as *sealed*).

| Art | Tree | Fed by | Opens at |
|---|---|---|---|
| **The Seated Blade** | Blade | upper-body sessions | now |
| **Iron Grip** | Blade | accessory days | now |
| **Hammerfall** | Blade | power & mobility (throws) | now |
| **Stillwater Stance** | Footing | balance work / the real side's leg work | now |
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
| **The Measured Hand** | Sport | throwing-control sessions | now |
| **The Wicket Gate** | Sport | break throws | now |
| **The Liar's Shoulder** | Sport | fakes and deception | now |
| **Overwall** | Sport | overhead throws | now |
| **Tell-Reading** | Sport | film and study of defense | now |
| **The Far Cast** | Sport | long throws | Knot III |
| **The Shadow-Step** | Sport | defensive footwork | Knot V |

In story, Arts are things Darrow can *do*: options in a fight, bonuses on checks, ways out of trouble. Use them. An Art at rank III should visibly change how a scene plays out.

---

## Checks and the chapter tier

- A check is d20 + attribute modifier (+ proficiency if an Art or training applies) + situational bonuses vs. a DC.
- **The chapter tier** comes from the week's real adherence (floor, planned sessions, fuel, morning checks, weigh-ins, logging): **Triumph** (+3), **Hard-won** (+1), **Costly** (+0), **Setback** (−2). It modifies the climax rolls and sets the shape of the climax (see `style.md`).
- **Ember** effects: Blazing +1 to everything; Bright +1 Vigor; Guttering −1 Might and Vigor.
- Results: success, *partial* (within 3: success at a cost), failure. Natural 20 / natural 1 are criticals.
- **Approval** with companions (−100 to +100) moves only with story choices, never with real numbers.
- **The Bearing** (`saga/state/bearing.json`) is who Darrow's choices are making him: four story axes (Mercy–Flint, Candor–Guile, Hearth–Banner, Sworn–Unsworn), each −10 to +10, moved only by story choices (a small choice ±1, a climax ±2 or ±3, a betrayal or a sacrifice ±4). He *leans* a way at 4 and is *named* for it at 8; the name is an epithet the page must speak before the site shows it. Options may require a Bearing value (`*[Guile 1]*`, or `*[Guile 4]*` for a lean), struck through when unmet, like stat gates. Never a number in prose; the site shows words.

---

## Story state vs. engine state

| File | Owned by | Contains |
|---|---|---|
| `saga/state/darrow.json` | engine (never hand-edit) | the computed sheet |
| `saga/state/rolls.csv`, `spends.csv`, `chapters.csv` | engine | every die rolled, every Inspiration spent, each chapter's frozen tier |
| `saga/state/world.json` | Claude (approval through `saga.py add` only) | Book, chapter, scenes, location, the quest as the page knows it, companions and approval, choices, inventory, recaps |
| `saga/state/bearing.json` | `saga.py bearing` | Darrow's Bearing: the four axes, leans and epithet |
| `saga/state/_gm/plan.json` | `saga.py plan` (GM only) | position, the chapter's slots, flags, factions, quests, roads |
| `saga/state/_gm/consequences.json` | `saga.py add / fire / void` (GM only) | the consequence ledger: what each choice changed and what it still owes |
| `saga/state/_gm/threads.md` | Claude (GM only) | open plot threads and plants |
| `saga/state/codex.md` | Claude | canon invented in play |
| `saga/state/glimpses.md` | Claude | the last ~20 glimpses (the line of the House closing a log reply); texture, never plot; the site never reads it |
