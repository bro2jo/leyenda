# ⚠️ GM EYES ONLY — The Grand Arc (spoilers)

> If you are Darrow (the reader), stop here unless you want the twists. Claude reads this file so it can plant and pay off. You don't have to.

---

## 0. How the arc is paced

The story is divided into **Books**. A Book ends only when a **Knot** of the Binding is tied, and a Knot is tied only when the real-world gate is passed and recorded in `real/config.json` (see CLAUDE.md, "Knots"). The calendar never ends a Book.

Every Book has:
- **Core beats**, in order. They must all happen before the Book's transition chapter.
- **Expandable beats**, used when the real gate takes longer than expected. Each is a self-contained episode (a companion quest, a mystery, a set piece) that deepens the world without spending the core plot.
- **A transition chapter**, written in the week the Knot is tied, which carries Darrow into the next Book.

If a gate arrives **early**, compress the remaining core beats into the transition chapter; nothing essential is skipped. If a gate arrives **late**, spend expandable beats, and keep at least one core beat in reserve so the transition still has weight.

| Book | Knots tied when it opens | Real-world phase | Rough real window (estimate only) |
|---|---|---|---|
| Prologue | — | injury → surgery | (already happened) |
| I — The House of Menders | I, II | Phase 3 | Oct 2026 → Phase 4 entry (earliest 10/20) |
| II — The Tempering Road | III | Phase 4 | ~late Oct → Dec |
| III — The Running Dark | IV | Phase 5 | ~Dec → Jan/Feb |
| IV — Lightning in the Marches | V | Phase 6 | ~Feb → Apr |
| V — The Turning Blade | VI | Phase 7 | ~Apr → Jun |
| VI — The Unkneeling | VII | Phase 8 → return | ~Jun → Aug 2027+ |

---

## 1. The truths (reveal schedule)

| # | Truth | Who knows at the start | Reveal |
|---|---|---|---|
| T1 | **The Oathstones don't give, they take.** Each sworn knight tithes life upward through the stones to the First Stone. The Grace is the knights' own strength, harvested, pooled and lent back. The king keeps the interest, and it keeps him alive. | Aurel; Vane (partly); Maelis suspects | End of Book II, at the Stonewright ruin |
| T2 | **The Three Heartbeats** were the First Stone drawing everything at once. The king was failing and fed. Two hundred knights paid. | Aurel; Vane knew it was coming | Hinted in Book I (the tithe-shard), confirmed with T1 |
| T3 | **Vane knew.** He was warned the night before and reined back one heartbeat early. The order to charge reached Hollis under Vane's seal. | Vane; Hollis has the writ but doesn't understand it | Hollis's letter, Book II |
| T4 | **The Hollowed are the drained.** Tithed knights eventually burn out into husks. The Crown discards them into the Ashen Fields; they drift east. The Thornwild clans have been fighting the Vaelmark's dead for generations. | the clans; the Confessors | Book III |
| T5 | **Harrow Ford was no battle.** The clans were fleeing a Hollow Tide across the ford. The Lances were sent to cut them down at the water. | Ilse of Corrach | Book III (Ilse) |
| T6 | **Wren's mother** (Dame Elspeth Ashdown) was a secret Ember initiate who refused to re-kneel. The Confessors Hollowed her on purpose, and she taught Wren the script before it took her. | nobody living except, possibly, Mother Ione | Book III, Wren's quest |
| T7 | **The Grace is stolen Ember.** The same fire, taken instead of built. A sworn knight who stops kneeling can slowly rebuild their own. The Unkneeling is possible for anyone, if they are willing to go the long road. | Maelis | Book IV |
| T8 | **Maelis was a Confessor**, thirty years ago, sent to hunt the last Warden. The Warden mended her instead of killing her, and she has been paying it back ever since. She has done the Binding twice before Darrow. One knight trusted the soft season and tore it; one re-knelt, and the Grace ate the thread. Both are dead. | Maelis | Book IV (approval-gated: earlier if approval ≥ 60) |

**Planting rules:** each truth gets at least two plants before its reveal. Log plants in `saga/state/threads.md` with the chapter they appeared in.

---

## 2. Book I — The House of Menders

**Question of the Book:** *Who is hollowing the wounded, and can a knight who can't stand protect anyone?*
**Darrow's state:** can walk, can't run, stairs are hard (descending hardest), can't kneel. Fights seated or braced. Wits and the Seated Blade.

### Core beats
1. **The Confessor at the Steps** (Ch 1). The **Reckoning awakened at the end of Scene 1** (the script of light at the infirmary window; Maelis, unsurprised: "Close the door, Captain"); Scene 2 is her explanation. The chapter's **climax is Marrant at the gate**: Confessor Ivo Marrant climbs the Steps with six men and a writ listing the Faithless at Saint Ysolde's, Darrow first on it; he reads the writ, Mother Ione has Old Mercy rung, and sanctuary holds. Marrant smiles and camps in the lower court "until the bell grows tired": sanctuary must be renewed by ringing at every dawn and dusk, and Sister Pell is old. Darrow's confrontation with him (Insight / Resolve; Warden's Eye applies). Choice at the end: step forward and answer to his name, stay hidden among the wounded, or send Wren to spy on the Confessors' camp (matches `world.json → chapter_plan.climax`).
2. **The Grey Cot** (Ch 2). Ser Benedek Orrin is found Hollowed at dawn: breathing, empty. Frost on his lips; a chip of black glass under his tongue. Marrant accuses "Ember witchcraft" (he is fishing for Maelis). The House is frightened. Darrow investigates from his cot, with Wren as his legs.
3. **The Undercroft** (Ch 3). Darrow insists on going down himself. The undercroft stair is the hardest thing his knee has faced ("every step down is a negotiation"). Below: a Warden hall, the First Precept, murals of the Reckoning, and, set in an alcove beneath the infirmary floor, a **tithe-shard**, a sliver of Oathstone drawing on the Grace-sworn wounded above. (Plants T1 and T2.)
4. **The Almoner's Sister** (Ch 4). The shard came up the Steps in Brother Anselm's letter-satchel. Marrant holds Anselm's sister Mirren in Calden. **Choice:** expose Anselm (to Marrant or to the House), shield him, or use him to feed Marrant false word. (Approval: Maelis favors truth, Wren favors use, Hollis favors mercy.)
5. **Old Mercy** (Book I climax). Marrant moves before Vane arrives. Sister Pell is hurt, the bell falls silent, and sanctuary lapses at dusk unless it rings. Darrow holds the bell-tower stair **seated** (the Seated Blade) while Wren climbs to ring. Boss: Marrant and his men. Use dice; the week's tier sets the modifier.

### Transition — The Descent (Knot III)
Maelis reads the Third Knot and, for the first time, says *"Permitted."* Darrow walks down the Thousand Steps on his own legs: 1,117 steps, every one counted by Wren aloud. Hollis rides a mule, Ash limps beside him, and Maelis comes, which no one expected, carrying her surgeon's roll and a sword wrapped in oilcloth from the undercroft. The sword is a plain Warden blade inscribed *PATIENCE*; Darrow thinks it's a joke. Far below on the Holloway: Vane's banners, coming.

### Expandable beats (use as needed, any order)
- **The Wager of the Two Cripples.** Hollis's first walk on the wooden leg, and a bet with Darrow about who reaches the chapel first.
- **Steam and Iron.** A parley with Marrant in the hot springs: a verbal duel (Insight and Resolve checks). Marrant lets slip that "the Crown counts what it is owed."
- **The Far Cots.** The Hollowed turn their heads toward the undercroft at night (toward the shard). Wren's mother's cot.
- **Wren's Ledger.** Darrow catches Wren reading Warden script off a lintel. She lies; he lets her.
- **Letters from Aldric.** Vane writes, lovingly. Darrow burns the first, keeps the second, answers the third (or doesn't: a choice).
- **The Long Snow.** A storm closes the Steps; firewood runs short; a cold night where the Ember keeps someone alive.
- **Hollow Night.** (Use the week of real Halloween.) The Vaelmark festival of lamps for the Hollowed; something walks on the Steps.
- **The Kennel.** Ash, and why the hound picked Darrow.
- **The Door That Reads.** An undercroft door that opens only to someone who can see the Reckoning.

---

## 3. Book II — The Tempering Road

**Question:** *What is the Grace, really?* **State:** Darrow can fight on his feet but can't run. Every fight must be **held**, not chased; choose the ground and refuse the pursuit.

Core beats: (1) The Lowmarch in fear: levies, empty villages, Hollowed on this side of the Wend. (2) **Ysra Tal** finds him. He can't match her footwork; he survives by refusing to move (Stillwater Stance, Might). She has orders to take him alive and doesn't understand why he won't kneel. (3) **The Mill at Coldmere:** Darrow holds a bridge so refugees can cross, the mirror of Harrow Ford, and this time he holds. (4) **Hollis's writ:** the charge order bore Vane's seal (T3). (5) **The Stonewright Ruin:** Wren reads the old script; T1 and T2 confirmed. (6) **Transition — The First Run (Knot IV):** pursued across the frozen flats of the Wend, Darrow runs.

Expandables: Ysra's doubts; the Holloway inn; a Grace-burned knight who keeps re-kneeling (a cautionary mirror); the Lantern Market contact; a letter from Elinor Vane; Maelis teaches the Long Breath.

## 4. Book III — The Running Dark

**Question:** *Who are the real enemy?* **State:** Darrow can run, in bursts at first and then steadily; the story's movement opens up (chases, journeys, escapes). No leaping or hard turning yet.

Core beats: into the Thornwild; **Ilse of Corrach** (why she saved him); T4 and T5; Wren's mother (T6); the **Long Night** (real midwinter), a Hollow Tide against the clan holdfast; Ysra's choice (defect or die, set by earlier choices). **Transition — Lightning (Knot V):** Darrow leaps a broken bridge with the Tide behind him.

## 5. Book IV — Lightning in the Marches

**Question:** *Can the Unkneeling be more than one man?* **State:** power, speed and the stop return; deceleration is a weapon ("Anchor": stopping a charge dead).

Core beats: gathering the Unkneeling (Faithless, clans, deserters); set-piece battles; T7; Maelis's past (T8); **Hollis's last stand** (survives only with high approval and a specific prior choice); Darrow learns that the Warden's master form is **the Turning Blade**, the pivot. **Transition (Knot VI):** he turns at speed on purpose for the first time since the ford.

## 6. Book V — The Turning Blade

**Question:** *Can he trust the leg?* **State:** reactive, cutting, full speed. The enemy here is fear. Use **Resolve checks against the memory of the Three Heartbeats** (the saga's version of psychological readiness).

Core beats: the march back to Harrow Ford; the memory; the duel with **Aldric Vane on the ford stones**. Vane is full of borrowed Grace; Darrow has only what he built. Darrow must turn on the same stones where it broke. **Choice:** kill, spare, or unbind Vane. **Transition (Knot VII):** the Seventh Knot ties on the ford.

## 7. Book VI — The Unkneeling (finale)

Calden. The Oathspire. The Evergreen King, who is pitiable and terrified of dying, and believes the realm will die with him.

**Final choice** (options gated by approval and flags):
- **Shatter the First Stone.** Every sworn knight loses the Grace at once, a kingdom-wide Three Heartbeats. This time it is warned of, and the Unkneeling stand ready to catch them. Costly, honest.
- **Take the Stone.** Darrow becomes the new Evergreen. The dark ending; it should feel genuinely tempting.
- **Return the tithe.** Unwind the Stone slowly, give each knight back their own, and teach the Ember: the long road for everyone. Requires Maelis ≥ 50, Wren ≥ 50, and the flag `anselm_spared` or `vane_unbound`.

**The final image:** Darrow kneels, freely and once, and his knee holds. *Kneel because you can, not because you must.*
- **Trigger:** the real milestone **first comfortable, cleared kneeling on the left knee** (the harvest site). Record it as `milestones.first_kneel` in `real/config.json`. If it arrives before the finale, give it one private, quiet scene when it happens (Darrow kneels alone in a chapel, tells no one) and save the public kneel for the end.

The sword's full inscription, revealed when he kneels: *PATIENCE IS A BLADE THAT CUTS ONLY FORWARD.*

---

## 8. Recurring motifs (use, don't overuse)

- **Counting.** Wren counts the steps; Darrow counts names; the Reckoning counts what's earned. The first and last chapters each contain a count.
- **The two-finger fist ("hold").** Darrow hated giving it; by Book V it is his most-used signal.
- **Frost** marks a tithe-draw; **warmth** marks the Ember.
- **Bells** mean law; silence means danger.
- **Turning.** Every Book contains one moment where Darrow chooses not to turn, until Book V, when he does.

---

## 9. What the common folk believe vs. what is true (moved from world.md §7)

| Belief | Status |
|---|---|
| The Grace is the king's gift, flowing from his own sanctity | *see GM arc* |
| The Three Heartbeats were the Grace abandoning faithless knights | false |
| The clans brought the Hollowing | false |
| The Emberwardens were murderers and blasphemers | Crown propaganda; partly true of a few |
| King Aurel is three hundred years old because he is holy | he is three hundred years old |
