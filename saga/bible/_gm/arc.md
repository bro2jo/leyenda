# ⚠️ GM EYES ONLY — The Grand Arc (spoilers)

> If you are Darrow (the reader), stop here unless you want the twists. Claude reads this file so it can plant and pay off. You don't have to.

Headings are parseable: `python3 engine/saga.py arc <id>` prints one section (`b1.3`, `q1.steam`, `t1.low`, `book2.question`, `temptation`). State (status, stage, flags, road) lives in `saga/state/_gm/plan.json`; this file is the prose plan. Ledger rules are referenced by their ids in `saga/state/_gm/consequences.json`. Flags by their names in `plan.json → flags`.

## pacing
The story is divided into **Books**. A Book ends only when a **Knot** of the Binding is tied, and a Knot is tied only when the real-world gate is passed and recorded (`real/config.json`, `darrow.py knot tie`). The calendar never ends a Book.

Every Book has: a **question**; **core beats** in order (`bN.K`), which all happen before the Book's transition; **side quests** (`qN.id`) that run as daily scenes when the gate is slow (§5.2 of the design: once Chapter 2 opens at least one is live, never more than two; stages in order, finished within two chapters; `required` first; `floating` quests may run in any Book at the House or be re-skinned on the road); and a **transition chapter** (`tN`), written in the week the Knot is tied, in one of three shapes (`tN.high / main / low`) chosen by `saga.py route decide` from the Book's chapter tiers.

**The compress rule.** If a gate arrives **early**, fold the remaining core beats into the transition chapter in order; nothing essential is skipped and nobody is rushed on the page. If a gate arrives **late**, spend quests and keep at least one core beat in reserve so the transition still has weight. `saga.py now` warns when planned core beats outnumber the chapters that could remain. A Knot tied mid-week re-plans the rest of the week toward the crossing; Sunday's climax becomes the transition. Anything that makes a beat or a person "arrive a chapter early" (a road, a due item, a rule) fires at most once per Book, whichever source armed it: `r.once.early_arrival`.

Days inside a chapter are **colour, never content**: the slot's content is planned; the day's real deeds set only warmth or cold. Outcome is set only at the climax, by the tier. Missed days get no scene; the next scene opens on one planned off-page world move.

**Book I, compressed (likely).** Phase 4 can arrive as early as the week of 10/18, so Book I may be three chapters, not five. The shape that keeps every reveal and nobody rushed: **Chapter 2** = b1.2 (the Grey Cot) with q1.letters stage 1, q1.cart stage 1 and q1.kennel's first stage; **Chapter 3** = b1.3 and b1.4 folded (the undercroft found and the almoner's satchel named in the same week; its climax is the shard under the far cots and Anselm's choice); **b1.5 becomes the transition's climax** (Old Mercy held on the Knot's week, the bell-tower stair and then the Steps down in one night and one dawn), with `tN.<road>` written straight after it. Quests not run (q1.wager, q1.steam, q1.farcots, q1.ledger) are dropped with one line or re-skinned on the road (q1.ledger → b2.5; q1.steam → a parley at the Coldmere inn). If the gate slips past 10/25, the five-chapter shape stands.

| Book | Knots tied when it opens | Real-world phase | Rough real window (estimate only) |
|---|---|---|---|
| Prologue | — | injury → surgery | (already happened) |
| I — The House of Menders | I, II | Phase 3 | Oct 2026 → Phase 4 entry (earliest 10/20) |
| II — The Tempering Road | III | Phase 4 | ~late Oct → Dec |
| III — The Running Dark | IV | Phase 5 | ~Dec → Jan/Feb |
| IV — Lightning in the Marches | V | Phase 6 | ~Feb → Apr |
| V — The Turning Blade | VI | Phase 7 | ~Apr → Jun |
| VI — The Unkneeling | VII | Phase 8 → return | ~Jun → Aug 2027+ |

## truths
| # | Truth | Who knows at the start | Reveal (never earlier) | Two planned plants (ids) |
|---|---|---|---|---|
| T1 | **The Oathstones don't give, they take.** Each sworn knight tithes life upward through the stones to the First Stone. The Grace is the knights' own strength, harvested, pooled and lent back. The king keeps the interest, and it keeps him alive. | Aurel; Vane (partly); Maelis suspects | End of Book II, at the Stonewright ruin (b2.5) | b1.3 (the shard drawing on the wounded above) · q1.steam ("the Crown counts what it is owed") · q1.farcots (heads turn toward the shard) |
| T2 | **The Three Heartbeats** were the First Stone drawing everything at once. The king was failing and fed. Two hundred knights paid. | Aurel; Vane knew it was coming | Hinted in Book I (the shard), confirmed with T1 (b2.5) | b1.3 (frost on the shard's stone) · b2.2 (Ysra: "the Second was told to hold the bank that morning") |
| T3 | **Vane knew.** He was warned the night before and reined back one heartbeat early. The order to charge reached Hollis under Vane's seal. | Vane; Hollis has the writ but doesn't understand it | Hollis's writ, Book II (b2.4) | opening interlude (the writ hidden in the leg, wax unlooked-at) · q1.letters stage 1 (Hollis watches the blue wax curl in the brazier and leaves the hall: he has wax of his own he has not looked at) · b1.1 (Marrant's writ at the gate; Hollis stares at the wax) |
| T4 | **The Hollowed are the drained.** Tithed knights eventually burn out into husks. The Crown discards them into the Ashen Fields; they drift east. The Thornwild clans have been fighting the Vaelmark's dead for generations. | the clans; the Confessors | Book III (b3.3) | prologue (grey figures under the trees) · b1.2 (frost and black glass on a devout man) · q1.hollownight (a knight hollowed on the road, this side of the Wend) |
| T5 | **Harrow Ford was no battle.** The clans were fleeing a Hollow Tide across the ford. The Lances were sent to cut them down at the water. | Ilse of Corrach | Book III (b3.3, Ilse) | prologue (the carts; "Look. Remember it.") · b2.3 (the refugees at the mill drawn up the same wrong way) |
| T6 | **Wren's mother** (Dame Elspeth Ashdown) was a secret Ember initiate who refused to re-kneel. The Confessors Hollowed her on purpose, and she taught Wren the script before it took her. | nobody living except, possibly, Mother Ione | Book III, Wren's quest (b3.4) | q1.ledger (Wren reads a lintel and lies) · q1.farcots (she stands too long at one cot) · q1.door (she stands at the frame as if she has read it) · b2.5 (she finishes the line Darrow cannot; the why waits) |
| T7 | **The Grace is stolen Ember.** The same fire, taken instead of built. A sworn knight who stops kneeling can slowly rebuild their own. The Unkneeling is possible for anyone, if they are willing to go the long road. | Maelis | Book IV (b4.2) | prologue ("it had help for twelve of them") · b1.3 (the mural: a kneeling knight, the light running *up* out of him) · q2.inn (the re-kneeling knight's hands are colder each time) |
| T8 | **Maelis was a Confessor**, thirty years ago, sent to hunt the last Warden. The Warden mended her instead of killing her, and she has been paying it back ever since. She has done the Binding twice before Darrow. One knight trusted the soft season and tore it; one re-knelt, and the Grace ate the thread. Both are dead. | Maelis | Book IV (b4.3); earlier only if `r.t8.early` arms | Ch 1 Sc 1 ("Enough to know what the soft season looks like") · b1.3 (she walks the undercroft without a lamp) · q1.steam (Marrant: "tell the Mender the Order has a long memory") · t1 (the sword from the undercroft) |

**Planting rules:** at least two plants before any reveal, logged in `saga/state/_gm/threads.md` with the scene they appeared in. Plants may be added; reveals never move earlier. A reveal happens in a core beat, never in a quest, so the compress rule cannot skip it.

## motifs
- **Counting.** Wren counts the steps; Darrow counts names; the Reckoning counts what's earned. The first and last chapters each contain a count.
- **The two-finger fist ("hold").** Darrow hated giving it; by Book V it is his most-used signal.
- **Frost** marks a tithe-draw; **warmth** marks the Ember.
- **Bells** mean law; silence means danger.
- **Turning.** Every Book contains one moment where Darrow chooses not to turn, until Book V, when he does.

## beliefs
What the common folk believe vs. what is true (GM only; the reader learns it on the schedule above).

| Belief | Status |
|---|---|
| The Grace is the king's gift, flowing from his own sanctity | false (T1) |
| The Three Heartbeats were the Grace abandoning faithless knights | false (T2) |
| The clans brought the Hollowing | false (T4) |
| The Emberwardens were murderers and blasphemers | Crown propaganda; partly true of a few |
| King Aurel is three hundred years old because he is holy | he is three hundred years old |

## flags
Existing (`plan.json`): `reckoning_awakened`, `knows_wardens_exist`, `ash_met`, `anselm_suspected`, `anselm_spared`, `benedek_hollowed`, `vane_unbound`, `hollis_truth`, `ysra_spared`. New flags this arc needs, one line each:
- `named_himself` — Darrow stepped forward and answered to his name at the gate (b1.1 climax, option 1).
- `marrant_offer` — Marrant offered to strike two names from the list for "the witch" (q1.steam); resurfaces in b1.4 and b1.5.
- `shard_found` — Darrow has seen the tithe-shard under the infirmary floor (b1.3).
- `wren_script_seen` — Darrow caught Wren reading Warden script and let her lie (q1.ledger).
- `vane_answered` — Darrow wrote back to Aldric (q1.letters, third letter, option 1).
- `sanctuary_writ` — the House was left under a Confessor's writ, Mother Ione answerable (t1.low).
- `elinor_letter` — a letter from Elinor Vane reached Darrow (q2.lantern).
- `ilse_named` — the red-handed woman has been named on the page (b3.2).
- `elspeth_named` — Wren's mother has been named on the page (b3.4).
- `hollis_fell` — Hollis died at his last stand (b4.4; set when `r.b4.hollis_lives` did not arm).
- `vane_spared` — Vane was spared alive and still sworn (b5.4, option 2); `vane_unbound` covers option 3.
- `first_kneel_private` — the quiet private kneel has been written (triggered by `real/config.json → milestones.first_kneel`).
- `thistle_found` — the grey mare is Darrow's again, delivered by Rae (rae.tether stage 3).
- `rae_market_told` — Rae told him she carries for the Lantern Market before he found it (q2.lantern); false if he found the oilcloth first.
- `rae_vow` — the private vow with no knee bent has been written (rae.tether stage 5).
- `hollis_told_shard` — Darrow told Hollis and the far cots' keepers of the shard before the Prior (b1.3, option 2): b1.4 opens with Hollis already at the almoner.
- `stair_watched` — Darrow told no one and watched the stair (b1.3, option 3): Wren catches Anselm in any tier, and the Prior learns the shard was kept from her (menders −5).
- `marrant_told` — Darrow told Marrant what the Reckoning showed him (b1.5, option 1): Book II's writs name "the ember-mad captain", and Ysra has been told what to look for.
- `wren_blooded` — Wren went down after the camp with a knife that was not for show (b1.5, option 3): she comes back changed, and b3.4 she reads alone.

# Book I — The House of Menders

## book1.question
*Who is hollowing the wounded, and can a knight who cannot stand protect anyone?*
**Darrow's state:** can walk, can't run, stairs are hard (descending hardest), can't kneel. Fights seated or braced. Wits and the Seated Blade. Knots I and II tied; III ends the Book.

## opening
Already on the page (Chapter 1; slots 1–4 of the week are covered by Scene 1).
- **Scene 1 — The Reading of the Knots.** First snow; the dawn forms; Maelis's Reading and the soft-season warning ("The quiet is a liar."); Wren from the bell tower: six grey cloaks, a cart and a censer on the Holloway, a list read at the inn in Coldmere that Rae Thorne heard and climbed through the night to bring up, Hollis second, Darrow first; at the window the Reckoning awakens (`reckoning_awakened`), and below it Darrow knows her cart at the winch-house; Maelis, unsurprised: "So it's begun." / "Close the door, Captain." (Revised 10/9: the Prologue's last cart is Rae's; she is on the page from there.)
- **Interlude — The Wax** (Hollis). The charge order folded inside his shirt, the seal he broke with his thumb and has never looked at; Benedek Orrin on the next cot (a boar spear through the shoulder; says his oath at every bell; "What does it mean? Second."); the beech leg under the cot, nine steps yesterday; two days without a drink; the thought of teaching the Captain to fight from a chair; Hollis lies kindly ("Nobody's taking anyone") and hides the writ, still folded, in the cup of the leg. Ends: the cell door opens down the hall.
- Scene 2 continues straight from "Close the door" (b1.1). Threads live: 1, 2 (paper located, seal unexamined), 7, 8, 9 (paid off in Scene 2), 11; new: Benedek on the page (feeds b1.2).

## b1.1 — The Confessor at the Steps
Chapter 1. **Question:** will the House stand between him and the list? Scene 2: behind the cell door Maelis explains the Reckoning and the Ember in as few words as she can; the Wardens were burned for it; she forbids him to tell anyone, Hollis most of all; she does not explain her own past (`knows_wardens_exist`). Then Mother Ione's council (sanctuary, Old Mercy, the rule of the bell at dawn and dusk; Sister Pell is old); the grey cloaks reach the foot of the Steps, censer smoke rising through the cloud; the House counts what it has.
**Climax — Marrant at the gate.** Confessor Ivo Marrant climbs with six men and a writ listing the Faithless at Saint Ysolde's, Darrow first; he reads it; Mother Ione has Old Mercy rung; sanctuary holds. He smiles and camps in the lower court "until the bell grows tired." Checks: Resolve DC 13 (Mender's Patience), Insight DC 13 (Warden's Eye: Darrow reads him and finds nothing of his own in him). Marrant is named on the page here (`saga/characters/` file due).
**Plants:** Hollis stares at the wax on the writ Marrant reads and looks away (T3); Marrant's eyes go to Maelis and stay a beat too long (T8); Benedek, listening, is not on the list and is relieved (b1.2). Rae Thorne at the council (slot 6: she heard the list read; afterwards she asks Darrow, flat, whether he rode a grey at the ford, and does not say why) and on the gate wall (slot 7: the grey cloaks reach the winch-house and put a man on her cart; she could go down past them and does not, yet). The climax leaves a grey cloak at the winch-house with his boots on her cart: the cage, the House's larder and letter-box, is in the Order's hand (q1.cart). Threads 8, 2, 14. The list names the Faithless of Harrow Ford who have not knelt anew, captains first whatever their legs (the far cots, who can neither kneel nor answer, are not named); Benedek knelt anew before a Confessor's field-stone at the bell-house below the Steps on the road up, the heralds' mercy taken early, and says his oath at every bell, so the Order counts him sworn and he is not on it, which is why Marrant can Hollow him with no name on paper (b1.2).
- *Triumph:* Old Mercy rings before Marrant reaches the third name; he reads the rest to a shut gate in the snow, and the House laughs that night for the first time since the cart came.
- *Hard-won:* the bell rings on the last name; Marrant camps smiling; Darrow holds his face through the reading and loses it once, after, where only Wren sees.
- *Costly:* Sister Pell's hands are slow and two grey cloaks are inside the gate before the bell; a lay brother is knocked down; Marrant goes back down with a face he did not have before: Maelis's.
- *Setback:* the bell rings only because Mother Ione climbs and rings it herself; Marrant leaves one man inside the gate "as a guest under the law of bells," and the House has a Confessor at its table.
**Choice:** 1. Step forward and answer to his name (candor +2; Maelis approves, Wren does not; `named_himself`). 2. Stay hidden among the wounded and let the Prior answer for the House (guile +2; Wren approves). 3. Send Wren to spy on the camp *[Guile 1]* (guile +3; Wren approves; risky).

## b1.2 — The Grey Cot
Chapter 2. **Question:** who did this, and from where? Ser Benedek Orrin is found Hollowed at dawn: breathing, empty, frost on his lips, a chip of black glass under his tongue (`benedek_hollowed`). Marrant, from the lower court, names it "Ember witchcraft" and asks for the Mender by title: he is fishing for Maelis. The House is frightened; the kitchen counts loaves. Darrow investigates from his cot with Wren as his legs: who passed the far cots in the night, which doors were barred, what the novices heard. Hollis will not leave Benedek's side and sits the first watch with the boy's hand in his.
**Plants:** frost on a Grace-sworn man's mouth (T1/T4); the glass is Oathstone (T1); the trail of cold runs along the east wall to the undercroft stair (b1.3); Wren's tally includes the almoner's satchel going down and coming up lighter, which nobody yet understands (b1.4, `anselm_suspected` stays false); Rae ran the cage that night and knows the satchel's weight both ways, and nobody has asked her (q1.cart stage 2); shown the frost on Benedek's mouth she says only, "I've had that cold in my cart," and will not be drawn (T1: `_gm/characters.md`, the cold she knows). Thread: Benedek.
- *Triumph:* Wren's count fixes the hour and the stair; Darrow lays the whole night out before the Prior and the House believes him over Marrant.
- *Hard-won:* the stair is found; half the House still believes Marrant, and Maelis is asked, politely, to stop treating the far cots.
- *Costly:* a lay brother swears to Marrant he saw the Mender at Benedek's cot in the night; Mother Ione must put her own word against his at the gate.
- *Setback:* the Prior forbids the undercroft outright and Marrant's camp raises a priest's tent; the lower court is becoming a chapel, and the House begins to split.
**Choice:** 1. Ask Maelis to take him down herself and go on her terms (sworn +2: his rank, his hall, and he puts both under her count: one step at a time, a hand on Wren's shoulder, her right to say stop; she may still say no, and then he waits). 2. Send Wren down with a lamp (guile +2; Hollis disapproves). 3. Ask Mother Ione for the key and wait (mercy +2; Hollis approves).

## b1.3 — The Undercroft
Chapter 3. **Question:** what is under the House? The stair is taken the way the b1.2 choice set it: (1) with Maelis's leave, at her count, one hand on Wren's shoulder, Hollis's voice from the top telling him to look at the wall and not the floor; (2) Wren goes down first with the lamp and he follows at dawn the same way, on what she reported; (3) the Prior's key opens the door and Maelis walks him down herself. In no shape does he go down against the Mender's word, and the stair never costs the knee: "every step down is a negotiation" is texture, not stake. Each shape leaves its own mark: (1) costs him a day of asking and buys Maelis's first unforced yes (thread 7 warms: she knows the way down too well); (2) Wren is alone with the murals first and leaves one line out of her report (T6 plant; `wren_script_seen` stays false); (3) the Prior's key comes with her condition that she is told everything found below, so the b1.3 choice's option 2 becomes a lie to her face. Below: a Warden hall, the First Precept over the door, murals of the Reckoning, and in an alcove beneath the infirmary floor a **tithe-shard**, a sliver of Oathstone set in fresh mortar, frost spreading from it across the stone, drawing on the Grace-sworn wounded above (`shard_found`). Maelis walks the dark without a lamp (coming down after them in shapes 1 and 2; leading, in shape 3).
**Plants:** T1 and T2 (the shard, the frost); T7 (the mural: a kneeling knight, light running *up* out of him along a thread); T8 (Maelis knows the way); the mortar is a week old and the alcove is the width of a letter-satchel (b1.4); Ash, if met, growls at the floor above it (q1.kennel); Rae, told of the frost, names a crate she once carried to Calden's lower door that froze her cart-bed in midsummer, and does not know what was in it (T1; she asks nothing and is asked nothing). Threads 6, 10.
- *Triumph:* Darrow reads the murals aloud as the Reckoning lets him, and brings the shard up wrapped in oilcloth; the frost burns through to his hands and the Hollowed on the far cots turn their heads to follow it.
- *Hard-won:* the shard is too cold to lift and stays; he has seen it and the fresh mortar, and that is enough to know it was carried.
- *Costly:* the shard is gone when they return with Maelis, mortar still wet: someone in the House moved it between dusk and dawn.
- *Setback:* the alcove is empty and newly broken, and at dusk Marrant announces he will "inspect the undercroft for witchery" under the writ; the pressure moves onto the almoner before Darrow is ready.
**Choice:** 1. Tell the Prior everything, shard and murals (candor +2; Maelis approves). 2. Tell Hollis and the far cots' keepers first and the Prior only after: his own people before the House's law (hearth +2; Hollis approves, Maelis disapproves; `hollis_told_shard`). 3. Tell no one yet and watch the stair (unsworn +2; risky; `stair_watched`). **Downstream (b1.4):** with `hollis_told_shard`, Hollis has already put the satchel to Anselm before the chapter opens, so Anselm cannot come to Darrow of his own accord: the Triumph shape becomes Hollis bringing him, shaking, and Anselm's confession is to a man he fears; with `stair_watched`, Wren catches him at the winch-cage in any tier, the Prior learns the shard was kept from her (menders −5, through the ledger), and her condition on the undercroft becomes a condition on Darrow.

## b1.4 — The Almoner's Sister
Chapter 4. **Question:** what do you do with a good man who did a terrible thing for love? The shard came up the Steps in Brother Anselm's letter-satchel (`anselm_suspected`). Marrant holds Anselm's sister Mirren in Calden: a letter from her comes up the winch-cage, and a lock of hair. Anselm is found, or comes to Darrow himself, and the Captain of the Ninth must decide what the House is for. If `marrant_offer`, Marrant renews it: the almoner's name for two others.
**Plants:** Marrant's method (the lever, never the blade; b1.5); Anselm names the "clerk in grey" who gave him the shard, a man he never saw kneel (T1); Mirren's letter is in Aldric Vane's secretary's hand (q1.letters), and it comes up Rae's cage: she has seen that hand before, forty-one times, on the tags of the Ninth's effects (Tether IV; she says only "I've seen that hand").
- *Triumph:* Anselm comes to Darrow himself, with the second shard still in the satchel, unplaced.
- *Hard-won:* Wren catches him at the winch-cage at dusk with the satchel; he does not run.
- *Costly:* a second shard is already under the far cots when he is found, and Darrow chooses with the floor still cold.
- *Setback:* Marrant has the confession first, read aloud at the gate in Mirren's hand, and calls Anselm down the Steps; Darrow's choice is whether to let him go.
**Choice (sets `anselm_spared`):** 1. Expose him to the Prior and the House (candor +3; Maelis approves; `anselm_spared=true` if the House keeps him). 2. Shield him and say nothing of the satchel (mercy +3; Hollis approves; `anselm_spared=true`). 3. Use him to feed Marrant false word *[Resolve 10]* (guile +3; Wren approves; risky; `anselm_spared=false` if Marrant learns it). Giving him to Marrant is never an option Darrow is offered; if the Setback hands him over, it is Marrant's doing and `anselm_spared=false`.

## b1.5 — Old Mercy
Chapter 5 (or the last chapter before the Knot). **Question:** can a knight who cannot stand hold a stair? Marrant moves before Vane arrives: Sister Pell is hurt, the bell falls silent, and sanctuary lapses at dusk unless it rings. Darrow holds the bell-tower stair **seated** (the Seated Blade, taught by Hollis; named on the page here if not before) while Wren climbs to ring; Hollis holds the tower door below from his chair; Ash, if met, holds the lower court's dog. Boss: Marrant and his six. Dice via `roll --chapter N`; the tier sets the modifier.
**Plants:** Marrant, unarmed to the last, asks Maelis by a name that is not hers (T8); the censer's iron is Oathstone-black (T1). Before he moves he has the cage rope cut at the winch-house, so the House's larder and letter-box are gone and the bell-tower stair is all that is left to hold; but the winter's salt and oil are already up (Rae's night drive, which only the kitchen's loaf-count explains), and in the Triumph and Hard-won shapes the tower's firewood came up by a second line nobody saw, hers; Rae, below, sees the rope fall and climbs the Steps in the dark, and is on the gate wall when the bell rings or does not. Threads 8, 7, 14.
- *Triumph:* the bell rings with light to spare and six grey cloaks go back down the Steps in the dark behind a Confessor who has stopped smiling.
- *Hard-won:* it rings on the last of the light; one of the six goes over the stair rail and lives; Marrant leaves with his writ and a limp.
- *Costly:* it rings a breath after dusk, and only Mother Ione's reading of the law ("the sun is down when the Prior says it is") holds; Marrant's writ gains a line against her.
- *Setback:* it rings, but Marrant is inside the tower with the bell when it does; the law is argued, not won; he goes down leaving a man and a paper, and the Prior signs it to keep her roof (sets up `t1.low`).
**Choice:** 1. Go down to the lower court at dawn and tell Marrant, before his men, what the Reckoning showed him (banner +2: he makes himself the Confessors' quarry so the writ stops at his name, and every stranger on every list in the Lowmarch below has a captain standing in front of him for once; Maelis disapproves, because it tells a Confessor what the Reckoning is; `marrant_told`). 2. Let him go and ring the bell for him as he leaves, as the law says (sworn +2; Mother Ione's road). 3. Have Wren follow his camp down with a lamp and a knife, and the knife is not for show *[Guile 4]* (flint +3; risky; `wren_blooded`). **Downstream:** with `marrant_told`, Book II's writs name "the ember-mad captain" and Ysra (b2.2) has been told what to look for: she tests him with a lie on the weir, and the Warden's Eye check decides whether he sees it coming; with `wren_blooded`, Wren comes back from the camp with a knife she has used or has not, and will not say which; her lean to Guile shows in every count after, and in b3.4 she reads the page alone whatever the tier.

## q1.kennel — The Kennel
- **priority:** required (sets `ash_met`; Ash's bond then moves to `world.json` with `plan companion arrive ash`)
- **hook:** A grey hound in the House kennels has bitten two lay brothers and the farrier, will not eat, and sleeps against the door that faces the infirmary. The kennel-master wants her put down before the Confessors come up and see what the Menders feed.
### stage 1
Wren brings Darrow down the kennel ramp (a ramp, not a stair; he takes the stick he refuses) because "you've got something in common": the bitch has a splinted hind leg. The snarling stops when he sits down on the straw. She puts the splinted leg across his boot and goes to sleep. Ends: the kennel-master gives him until the grey cloaks are gone to prove she's worth the feed.
### stage 2
She eats only from his hand. He re-splints her leg with Maelis's bad grace ("I don't do dogs"), and she growls, not at people, at the floor: at the grate over the undercroft. The kennel-master wants her chained. Ends on the micro.
### stage 3
Marrant's men have a lymer in the lower court and she fights it through the bars until her mouth bleeds. Darrow names her Ash: for her colour, Hollis says, and because she's what's left when the fire's gone. `ash_met`. Ends: she follows him up the ramp on three legs and lies down under his cot, where no lay brother will move her.
### compressed
1. The ramp, the leg across his boot, the chain (micro). 2. The growl at the grate, the lymer, the name; she comes up the ramp behind him.
### micro
- **at:** stage 2 · **ask:** The kennel-master wants her chained. What does Darrow do? · **axis:** mercy_flint
- **options:** 1. "Leave her loose. If she bites me, that's mine." (mercy +1) · 2. "Chain her. I'll sit with her chained." (flint +1) · 3. Say nothing; sit down beside her. (0)
- **default:** 1
- **payoff:** a companion; `flags.ash_met`; the growl at the grate points at the undercroft (b1.3).
- **spine link:** b1.3 (the grate), b1.5 (the lymer), t1 (she limps beside him down the Steps).
- **can run when:** Chapter 2 onward, before t1; Wren present; any weather.

## q1.letters — Letters from Aldric
- **priority:** required to its second letter; the third letter is a micro on sworn_unsworn
- **hook:** The winch-cage brings a letter in blue wax addressed to *the Captain of the Ninth, at the House of Menders*, in a hand Darrow has known since they were boys holding other men's horses.
### stage 1
The first letter, carried up from the winch-house by Rae Thorne, who took it from a grey cloak's hand at the bottom and did not like his smile: loving, specific, remembers Thistle's name. *"Come home, brother. Kneel, and be whole."* Darrow burns it in the infirmary brazier. Hollis watches the wax curl and says nothing at all, which is unlike him, and leaves the hall on the beech leg. Ends: Wren: "There'll be another. There's always another."
### stage 2
With the Confessors in the lower court, Marrant carries the second letter up to the gate himself and hands it through the bars: Aldric knows where he is, has known. It asks the one question only a brother would: *"Did you turn? Tell me you did not turn toward the boy."* Darrow keeps it folded under the mattress. Ends: the letter is dated before the list was read at Coldmere.
### stage 3
The third: *"Answer me, or I will come myself."* Ends on the micro; whatever he chooses, the next scene opens with Wren reporting riders on the Holloway under a banner that is not grey.
### compressed
1. The first letter burned; Hollis silent at the wax. 2. The second and third arrive together through Marrant; the micro.
### micro
- **at:** stage 3 · **ask:** What does Darrow do with his brother's letter? · **axis:** sworn_unsworn
- **options:** 1. Write back as a brother: he will not kneel, and why (sworn +1; `vane_answered`) · 2. Burn it unread (unsworn +1) · 3. Keep it sealed, with the second (0)
- **default:** 1
- **payoff:** Aldric's voice on the page (quoted letters); thread 1 kept warm; `flags.vane_answered` (Book V: Vane quotes the answer on the ford); T3 plants (wax in front of Hollis twice on the page, his own still unlooked-at; he recognises nothing until b2.4).
- **spine link:** b1.1 (Marrant as courier), b1.5 ("I will come myself": Vane is on the road), b2.4.
- **can run when:** stage 1 from Chapter 2; stage 2 after Marrant camps (b1.1 done); stage 3 any chapter before t1. If t1 comes first, the third letter is read on the Steps going down.

## q1.wager — The Wager of the Two Cripples
- **priority:** optional
- **hook:** Hollis has nine steps on the beech leg and a bottle he hasn't opened, and he bets Darrow the bottle that he reaches the chapel door first on the feast of Saint Ysolde.
### stage 1
The terms, argued across two cots with Wren as notary: distance (the cloister gallery), sticks (one each), witnesses, a clause about falling. The kitchen runs a book. Benedek blesses the bet if he is still himself. Ends: Mother Ione hears of it and, instead of forbidding it, lays a coin on Hollis.
### stage 2
The race: dry flagstones swept for it, spring-steam at the far end, the whole House on the gallery; Maelis marshals it: a walk is what she says a walk is, and she walks one step behind Darrow with her hand up. Darrow does not run (he cannot, and will not in the soft season); he walks it like a knight. Ten yards from the door Hollis goes down hard and the leg comes off. Ends on the micro; the bottle is opened either way, and shared.
### compressed
1. Terms and race in one scene; the fall and the micro at its end.
### micro
- **at:** stage 2 · **ask:** Hollis is down ten yards from the door. What does Darrow do? · **axis:** hearth_banner
- **options:** 1. Stop, get a shoulder under his arm with Wren and bring him up between them, and lose (hearth +1) · 2. Walk on and win, because the House needs to see one of the Faithless win something (banner +1) · 3. Stand where he is until Hollis gets up on his own (0)
- **default:** 1
- **payoff:** Hollis's approval (through the ledger); the beech leg in motion on the page; the seed of the Seated Blade lessons ("You'll never win on your feet, Captain. Sit down and I'll teach you to win sitting.").
- **spine link:** b1.5 (the Seated Blade on the tower stair).
- **can run when:** Chapters 2–4, before b1.5; a dry day; Hollis and Maelis present.

## q1.steam — Steam and Iron
- **priority:** optional (parley)
- **hook:** A courteous note comes up on the winch rope: the law of bells covers the Steps and the gate, the hot springs lie below the gate, and the Confessor would be honoured if the Captain of the Ninth would bathe with him. Unarmed. In steam. In the snow.
### stage 1
The lower terrace, outside the gate and inside the House's wall: a legal grey, which is why he chose it. Marrant in the water, bald head steaming, the censer on a rock. A verbal duel: Insight DC 13 (Warden's Eye: nothing of his own in him; all of it borrowed), Resolve DC 13 (not to answer the question about the Mender). Marrant lets slip that "the Crown counts what it is owed" and makes his offer: two names off the list for "the witch" (`marrant_offer`). Ends: "Tell the Mender the Order has a long memory."
### stage 2
The terrace stair back up, which is the hardest thing he has done this week, with Wren below him in case. Ends on the micro, and on Maelis's answer: "He asked for me by name?" "No." "Then he knows it."
### compressed
1. The springs; the micro on the stair.
### micro
- **at:** stage 2 · **ask:** What does Darrow tell Maelis? · **axis:** candor_guile
- **options:** 1. Exactly what was offered, and for whom (candor +1) · 2. That Marrant asked after her, and nothing more (guile +1) · 3. Tell Hollis first, and let him decide what she hears (0)
- **default:** 1
- **payoff:** T1 plant; T8 plant; Marrant's voice; `flags.marrant_offer` (renewed in b1.4 and thrown in his face in b1.5); Confessors faction.
- **spine link:** b1.1 (after he camps), b1.4, b1.5.
- **can run when:** Marrant camped (b1.1 done); Chapters 2–4; not in a storm.

## q1.farcots — The Far Cots
- **priority:** optional
- **hook:** The novice who feeds the Hollowed says they have started turning their heads at night: all of them, the same way, at the same moment, toward the east end of the hall.
### stage 1
A night watch on the far cots with Wren and a shuttered lamp (Hollis will not come near them). At the second bell every head turns toward the floor by the east wall. Frost on one mouth. Wren stands too long at one cot and says nothing. Darrow puts his palm on the flagstone where they look: cold as the river. Ends on the micro.
### compressed
1. As stage 1.
### micro
- **at:** stage 1 · **ask:** Wren asks him not to tell Maelis which cot she stood at. What does Darrow say? · **axis:** candor_guile
- **options:** 1. "I'll not lie to her if she asks." (candor +1) · 2. "What cot?" (guile +1) · 3. Say nothing; put a hand on her shoulder. (0)
- **default:** 2
- **payoff:** T1/T4 plant (frost on the Hollowed); T6 plant (the cot); points the House at the undercroft (b1.3); thread 10 stirred.
- **spine link:** b1.2 (Benedek joins the far cots), b1.3.
- **can run when:** Chapter 2 or 3, at night, Wren present; best before b1.3.

## q1.ledger — Wren's Ledger
- **priority:** optional
- **hook:** Snow has brought the plaster off a cloister lintel and there is script under it, angular strokes and dots, and Darrow catches Wren reading it with her lips moving in the right order.
### stage 1
He says nothing. Later he asks what the ledger is for, and she shows him: loaves, bells, cots, debts the House is owed, the names on the list, and a column she will not explain. He asks about the lintel. "I was counting the cracks." He lets her (`wren_script_seen`). Ends: she asks what *he* looks at in the empty air; she has noticed.
### stage 2
The next day she asks again, with the ledger open and the pencil ready, as if she means to write the answer down. Ends on the micro, and on the dusk bell.
### compressed
1. The lintel and the ledger; the micro at the end.
### micro
- **at:** stage 2 · **ask:** What does Darrow say about what he sees? · **axis:** candor_guile
- **options:** 1. The truth: the script of light, and what it reads (candor +1; breaks Maelis's prohibition, through the ledger) · 2. "Snow in my eyes." (guile +1) · 3. "Ask Maelis." (0)
- **default:** 2
- **payoff:** T6 plant (she reads; nothing of why); sets up b2.5; two liars who have each let the other lie.
- **spine link:** b1.3 (she reads the First Precept over the door before Maelis translates it, and stops herself).
- **can run when:** Chapter 2 or 3, after `knows_wardens_exist`; Wren present.

## q1.snow — The Long Snow
- **priority:** floating (any Book at the House; on the road, a blizzard camp)
- **hook:** A storm shuts the Steps; the winch-cage freezes on its rope; the firewood is counted in days.
### stage 1
The House rations. Marrant's camp in the lower court is dying of cold and Mother Ione proposes sending wood down under the law of guests. Darrow organises the hall from his cot: who sleeps nearest the fire; the Hollowed moved in from the far end. Ends on the micro.
### stage 2
The coldest night. Rae and Wren go out to free the winch-cage, Rae on the rope and Wren counting; Rae comes in soaked to the skin and shaking, and Darrow holds her against the warmth that is in him, which is more than the room has. She lives, and in the morning it is Wren who says it: "She says you're warm. Technically, the room isn't." Ends: the Steps clear, and below, the camp's smoke still rising. They lived too.
### compressed
1. Both nights in one; the micro in the middle.
### micro
- **at:** stage 1 · **ask:** Wood for the Confessors' camp? · **axis:** hearth_banner
- **options:** 1. "Send it. The law of bells is the law of guests, or it's nothing." (banner +1) · 2. "Keep it for the hall. They have cloaks." (hearth +1) · 3. Send half, and say nothing of where the rest went. (0)
- **default:** 2
- **payoff:** the Ember made visible as heat (T7-adjacent); hearth_banner; Menders and Confessors factions; Wren has noticed his warmth, and Rae has felt it.
- **spine link:** b1.5 (the firewood stacks become the tower-stair barricade) or any road camp.
- **can run when:** weather permitting; any Book.

## q1.hollownight — Hollow Night
- **priority:** floating; pinned to the week of real Halloween if Book I is still open; otherwise any Book, re-skinned as a village lamp-night on the road
- **hook:** The Vaelmark festival of lamps for the Hollowed: one lamp per far cot, set down the Steps at dusk, and the lay brothers will not go past the hundredth step after dark.
### stage 1
Lamps lit; Wren's count; for once the Hollowed turn their heads toward the Steps, not the floor. Marrant's camp keeps its own vigil with the censer. Then something climbs: a figure in grey armour, slow, and the lamps go out behind it one by one. The House bars the gate; Darrow at it, Hollis in his chair beside him. Ends: it stops at the gate and does not knock.
### stage 2
Dawn: a Hollowed knight, frost on his face, no name anyone knows, who walked up from the Lowmarch on his own. The first Hollowed from *this* side of the Wend the House has seen. Marrant claims him for the Crown; Mother Ione claims him for sanctuary. Ends on the micro, and on the gate opening one way or the other.
### compressed
1. The lamps and the climber; the dawn and the micro.
### micro
- **at:** stage 2 · **ask:** The knight at the gate. What does Darrow say? · **axis:** mercy_flint
- **options:** 1. "He climbed the Steps. Bring him in." (mercy +1) · 2. "He's the Crown's. Let the Confessor have him." (flint +1) · 3. Say nothing; the Prior decides. (0)
- **default:** 1
- **payoff:** T4 plant (hollowing on the road); the grey figures of the prologue back on the page (thread 4); lamps and bells.
- **spine link:** b1.2 (what Hollowing looks like, before or after Benedek), b2.1.
- **can run when:** real Halloween week if Book I is open; else any Book, re-skinned.

## q1.door — The Door That Reads
- **priority:** floating (after b1.3; any Book at the House; on the road, a Stonewright or Warden door in a ruin, see b2.5)
- **hook:** A door in the undercroft with no handle and script round the frame. It did not open for two lay brothers with a crowbar. Maelis says to leave it.
### stage 1
Darrow and Wren with a lamp. He reads the frame as he read his own palms: the door asks what he has built, not what he was given. He lays his hand on it and it opens: it reads the Reckoning. Inside, a Warden's cell: a cot, a shelf of oilcloth bundles (one long one), script scratched into the wall by someone who sat here a long time. Wren stands at the frame as if she has read it and does not step through; the door will not hold for her. Ends: Maelis's voice from the stair behind them, not angry. She knew.
### stage 2
Maelis in the cell with them, naming nothing. Ends on the micro, and on her hand resting on the long bundle a moment before she leaves it where it lies.
### compressed
1. The door and the cell; Maelis; the micro.
### micro
- **at:** stage 2 · **ask:** "Who else knows this door opens for you?" What does Darrow say? · **axis:** sworn_unsworn
- **options:** 1. "No one, and no one will. You have my word." (sworn +1) · 2. "Wren knows. I'm done with oaths; I'll keep quiet because I choose to." (unsworn +1) · 3. Say nothing. (0)
- **default:** 1
- **payoff:** a place (the Warden's cell; `places.json` when on the page); the sword planted for t1; T8 plant; T6 plant; Resolve check optional.
- **spine link:** b1.3, t1 (the oilcloth bundle is the sword PATIENCE).
- **can run when:** after b1.3 (`shard_found`); Wren and Maelis present.

## q1.cart — The Winch-house
- **priority:** optional (Rae's thread through Book I; runs early)
- **hook:** The grey cloaks have camped on the lower terrace, and one of them sits at the winch-house below with his boots up on Rae Thorne's cart. The cage is the House's larder and its letter-box, and the Order has its hand on the rope.
### stage 1
Rae must go down for her oxen: no writ names a carter, and the law of bells lets anyone down. Darrow on the gate wall watches her take the Steps the way she takes them, not counting, with Wren beside him counting for her. She comes back up at dusk with the oxen stabled under a grey cloak's eye, what the camp below is eating, and the first letter in blue wax (q1.letters stage 1 may share the slot or follow it). Ends: he asks her why she asked whether he rode a grey. "When you're at the bottom. I'll show you." Not a dare: a day she will not name, and he does not go to Maelis to ask for it.
### stage 2
A load the grey cloaks have "inspected" comes up the cage light; Rae and Wren on the rope at the top, Rae's palms showing what the rope has done to them over the years. She says, flat, what the almoner's satchel weighed going down last week and what it weighed coming up (b1.2's clue, before anyone has asked her). Then, because it is the only thing she has ever brought up the mountain that was not on a manifest: the grey mare is alive, lame, and a Holloway dealer's; she can be had for the dealer's debt, and Darrow owns a shirt and a stick. Ends on the micro.
### stage 3
The dusk bell catches her at the top: the Steps after dark are for lay brothers and fools, and the cage does not run at night, so the kitchen counts her as a guest and Hollis offers commentary. On the gate wall she and Darrow watch the camp's fires on the terrace below and the winch-house's one lamp far down in the dark. She does not ask him anything. Ends: `plan companion arrive rae` (present while she is at the House; she goes down in the morning), and the law of guests has given the House a carter for a night.
### compressed
1. The Steps down and up, the oxen, the letter, the grey-mare question (stage 1). 2. The light load, the satchel's weight, the mare's price and the micro; she stays past the bell.
### micro
- **at:** stage 2 · **ask:** The mare can be had for the dealer's debt. What does Darrow send down? · **axis:** candor_guile
- **options:** 1. His name, as surety: a captain's word, though the Faithless have no credit in the Lowmarch and he knows it (candor +1) · 2. Word, through Rae, that the mare is wanted for the House's stables, in Mother Ione's name (guile +1; a lie in the Prior's name) · 3. Nothing. Leave her where she is. (0)
- **default:** 1
- **payoff:** Rae on the page in scenes of her own; `plan companion arrive rae`; b1.2's clue (the satchel's weight) in the House's hands; the mare's price set for Tether III; the cage as the Order's lever (b1.5).
- **spine link:** b1.2 (the satchel), b1.4 (Mirren's letter comes up her cage), b1.5 (the rope cut), t1 (the cart at the bottom).
- **can run when:** Chapter 2 onward, Marrant camped (b1.1 done); stage 1 best in Chapter 2 beside q1.letters stage 1; not in a storm (q1.snow has its own cage night).

## rae.tether — The Tether
- **priority:** floating and **standing** (`plan.json → quests.rae.tether.standing`): it does not count toward the two-live limit and finishes when the Ledger says, not within two chapters. **A stage is planned only once the engine has unlocked it** (`darrow.py sheet` → THE TETHER · N of V; `check` refuses a slot ahead of it). One scene per stage, in the next free quest slot of whichever Book it lands in, re-skinned to wherever the company is. The day's deeds colour it like any scene; approval sets whether she is warm or careful in it. The scene closes with the Reckoning box line `The Tether: **<name>**.`, and the first of them is the only place the page explains it: a second thread, read on his palms beside the first, counting something that is not his alone.
- **hook:** The script on his hands has begun to count something that is not his alone.
### stage 1 — a name
She calls him Darrow. Not Ser, not Captain: "I don't drive for the Ninth. I drive for the House." And why Thorne: the village's word for her grandmother, worn smooth, and kept. (At the House: the gate wall or the kitchen. On the road: a cart-tail at dusk.)
### stage 2 — a hand
Her palms: the rope-burn ridges, the crooked thumb; the cage, her father, the splice that went quiet before it went. A rope is softest where it is worn smooth, she says, which is the only thing she and Maelis have ever agreed on without knowing it. Then her question, the one a carter would ask: why he does not take the fast road down and kneel and have it all back, when she would, if anyone offered it to carters. Ends on the micro.
### stage 3 — a road
Thistle. At the House: Rae brings the mare to the foot of the Steps and climbs with the halter rope, and puts it in his hand, the first thing he has owned since the river (`world.json → inventory`: Thistle's halter rope). On the road: the mare walks into camp behind the cart. `thistle_found`. He does not ride her yet and does not try; she carries his gear and he walks at her head, which is where he walked as a boy. Riding, when the road is long and Maelis says nothing against it, belongs to Book II.
### stage 4 — a door
What was in her cart on the road back from the ford: forty-one bundles and the tags, in a clerk's hand she has seen since. She can say them. He asks her to stop. She stops. Later, in the same scene or the next she is in, he asks her to go on, and she says them and does not count. (Tobin Marsh's name is hers to say here, reading the tag from memory; Darrow's own saying of it stays for Book V.) Hollis, before or after, plants the custom as a jibe: a knight weds kneeling, Captain; you'll die a bachelor.
### stage 5 — a home
There is no form for it, so they make one (the Unkneeling's rite of q4.deserters, turned to this). Before the finale: a private vow with no knee bent, in a chapel or a barn, witnessed by Wren, who writes it down ("Oaths sworn standing: 1"), and by Maelis, who says Permitted to something that is not the knee; `rae_vow`. If `r.rae.form` arms, the public form is the epilogue's last image after the final kneel: he kneels once because he can, and stands up to her.
### compressed
The stages never compress: each waits for its day.
### micro
- **at:** stage 2 · **ask:** "Why not the fast road, then? Down, kneel, have it back." What does Darrow say? · **axis:** candor_guile
- **options:** 1. "Because it wasn't mine. This is." (candor +1) · 2. "Because they'd hang me at the bottom of the Steps before I reached a stone." (guile +1; true, and not the reason) · 3. Say nothing; show her the knee. (0)
- **default:** 1
- **payoff:** the romance, stage by stage; `thistle_found`; `rae_vow`; `r.rae.form`.
- **spine link:** every Book: the stage lands where the Ledger lands it.
- **can run when:** stage N only once `tether.stage >= N`; Rae present (while `r.rae.parts` holds her away, the stage waits for her).

## rae.road — Rae on the road
Her place in every Book, so the romance and the plot stay one story. She comes down the Steps in every shape of t1 and drives for the company after; she lives in every road and is never the price of anything (design principle 4).
- **t1:** she is at the winch-house with the cart. *High:* cart and both oxen, the Confessors' camp gone down ahead of her. *Main:* the cart and one ox (the other sold against the mare's debt if `thistle_found`, else lamed on the Holloway). *Low:* the Confessors have seized the cart under the writ and she comes with a handcart, the ox-bell, and the mare if she has her. "Road's the road."
- **Book I (the rest):** the winter's stores already up before the rope is cut; a camp read by what it bought; a padded manifest; a second line nobody saw; and the cold she knows from her own cart-bed, said once and not explained (`_gm/characters.md`, quiet competence).
- **Book II:** the company's wheels. Hollis rides the cart when the mule will not have him; Maelis's roll and the oilcloth sword ride under the salt. b2.1: Coldmere is her village and the innkeeper her uncle (the Triumph shape is his doing, for her), and the levy sergeant leaves knowing nothing after an hour of oxen with her, in any tier. b2.2: a carter can make a road lie, two carts' tracks out of one, and Ysra's hunt follows the wrong pair; Costly: Ysra takes the oxen for an hour instead of Wren if Rae is nearer. b2.3: her cart is the mill bridge's barricade, and she reads the refugees' line before Darrow does. q2.lantern: the drop at the river mill is hers (`rae_market_told`: she tells him on the road before they reach it, or he finds the oilcloth under the salt), and she can tell a writ from a love letter by wax and weight without reading either.
- **Book III:** the clan way of asking, a gift before the ask, which she has from her grandmother and he does not; her few clan words buy the first hearing (b3.1); she counts the holdfast's stores and gives Ilse a number Ilse's people got wrong (b3.3); for the winter move she draws the carts up *right*, the reverse of the ford, so the Tide sees a line that is not fleeing (b3.5 Costly); the seized ledger comes whole because she knew which crate it rode in (b3.4, `r.rae.ledger`); she and Ilse understand each other too well for Darrow's comfort.
- **Book IV:** the host's quartermaster without the title: every mill, barn and ford-house on the Holloway (b4.1); q4.marches, the forty boys go home in her cart because she tells them what their sergeant said of them in Coldmere; her oxen smell the Tide's frost first (b4.4 colour); q4.censer, she can name the crate Marrant's leash-ledger rides in.
- **Book V:** the Holloway reversed is her road: b5.1's villages open because she is known on it; the Second's baggage train is carters and word ran through them (q5.second); she knows where the field-stones' frames have been moved and where Vane will stand (b5.2); q5.tobin, she carted Tobin's bundle to the inn at the ford village and knows his mother's face.
- **Book VI:** the Lantern Market's carters inside Calden's walls are her trade (b6.1, q6.market); the Oathspire's lower door opens for carts and she has driven to it once, with a crate that froze her cart-bed (T1, paid here); she drives the last cart to that door, which is what carts are for.
- **`r.rae.parts`:** at approval ≤ −25 she drives home at the next transition (a cost on company, never a death), and the Tether's scenes wait; she is back a Book later, because the road is the road. **`r.rae.form`:** Tether V and approval ≥ 50: the epilogue's image after the final kneel.

## t1.high
The Knot of Standing, tied with the House's blessing and something extra. Marrant's camp is broken and gone down ahead of him. The descent is in daylight with the whole House on the gate wall; Mother Ione gives Darrow the **Prior's writ of sanctuary** (any House of the Menders in the Lowmarch must open to him under the law of bells) and Sister Pell gives Wren her glass. Hollis has a farrier's leg that fits, and rides the mule without swearing at it. Ash limps beside him (met at the kennels in one paragraph if not `ash_met`). Maelis comes, which no one expected, with her surgeon's roll and the oilcloth sword from the undercroft, *PATIENCE* on the blade; Darrow thinks it's a joke. Wren counts all 1,117 aloud. At the winch-house Rae Thorne has the cart and both oxen, and takes the company's load without being asked (`rae.road`). Far below on the Holloway: Vane's banners, coming, a day further off than they should be.
- *If he leans Candor:* the Prior's blessing is said aloud to the whole gate; *if Guile:* she gives it to Wren to pass on, "since he'll believe it from you."
- **carry-forward:** `r.route.book1.high` → the Mender houses of the Lowmarch open to him (a bed and a bell at Coldmere's chapel); the lower Lowmarch has heard the Faithless captain was blessed by Saint Ysolde's (Faithless faction rises; Menders +); Hollis is sound on his leg from b2.1.

## t1.main
The present transition. Maelis reads the Third Knot and, for the first time, says *"Permitted."* Darrow walks down the Thousand Steps on his own legs: 1,117, every one counted by Wren aloud. Hollis rides a mule and curses the mule. Ash limps beside him; if not `ash_met`, he meets her at the kennels on the way to the gate, one paragraph, and she follows him down without being asked. Maelis comes, which no one expected, carrying her surgeon's roll and a sword wrapped in oilcloth from the undercroft, a plain Warden blade inscribed *PATIENCE*; Darrow thinks it's a joke. The House rings the dawn bell behind him as he goes. At the winch-house Rae Thorne has the cart and one ox, and the mare if he has her; she takes the company's load and says the road is the road (`rae.road`). Far below on the Holloway: Vane's banners, coming. Marrant's camp has gone down ahead to meet them.
- *If he leans Sworn:* Mother Ione asks him to carry the House's word to any Mender he meets; *if Unsworn:* she asks him for nothing and gives him bread.
- **carry-forward:** none (no ledger rule; Book II opens clean).

## t1.low
Sanctuary spent. The House is left under a **Confessor's writ**, Mother Ione answerable for every name under her roof (`sanctuary_writ`). The descent is at night, in weather, with *"Permitted"* said in a hurry by lamplight at the top of the stair. **Hollis stays behind** to stand surety for the wounded: he is second on the list and offers himself before anyone can stop him, so Darrow goes down without the Seated Blade's teacher. Wren counts in the dark, by feel. Ash comes (she is a dog; no writ binds her). Maelis still comes, surgeon's roll and the oilcloth sword; she reads the Knots wherever he is. Nobody is lectured, nobody is left to die, and the knee is not the price: the price is the House behind him and the man who taught him to fight sitting down. At the winch-house the Confessors have seized the cart under the writ; Rae Thorne comes anyway, with a handcart and the ox-bell (`rae.road`).
- *If he leans Hearth:* Hollis's parting line is about the Captain, not the list; *if Banner:* it is about the forty cots.
- **carry-forward:** `r.route.book1.low` → no safe House behind him; the lower Lowmarch has heard the Menders harboured a heretic (Menders −, Confessors +); Hollis rejoins only at b2.3; the mill bridge must be held longer by fewer of his own people, never by fewer refugees.

# Book II — The Tempering Road

## book2.question
*What is the Grace, really?* **State:** Darrow fights on his feet but cannot run; every fight must be **held**, not chased: choose the ground and refuse the pursuit. Knot III tied; IV ends the Book. Low road: Hollis absent until b2.3. Vane's column, seen from the Steps, turns back at Coldmere on a summons to Calden (the king failing; T2 under the surface) and sends Ysra in his place, which is why the Second is not met before Book V; b2.1 may show the turned column's tracks.

## b2.1 — The Lowmarch in Fear
Levies on the Holloway, villages empty or barred, a Hollowed knight walking east through a turnip field at noon: the Hollowing is on this side of the Wend now. The inn at Coldmere where the list was read, which is Rae's village and her uncle's inn (`rae.road`). Darrow learns to lead five people, a cart and a dog who all go faster than he does. **Plants:** T4 (the Hollowed drift east); the Confessors' writs now name "the Mender Vorne" (T8). Threads 4, 8.
- *Triumph:* Coldmere's innkeeper hides them and sends the levy sergeant the wrong way; the village has heard of the bell.
- *Hard-won:* they sleep in a barn and leave before the bell; Ash gives them away once and is forgiven.
- *Costly:* the levy sergeant knows Hollis's name and they leave Coldmere at a walk with the village watching.
- *Setback:* a Confessor's writ is nailed to the inn door with his epithet on it (if he has earned one; else "the stiff-kneed captain"), and the Lowmarch knows what he is called before he does.
**Choice:** go east along the river road (banner +2: toward the refugees), or north by the mill tracks (hearth +2: safest for his own).

## b2.2 — The Needle
Ysra Tal finds him on a frozen weir. He cannot match her footwork and does not try: Stillwater Stance, Might, he survives by refusing to move, and she cannot understand a man who will not be moved and will not kneel. She has orders to take him alive and does not know why. **Plants:** T2/T3 ("the Second was told to hold the west bank that morning; everyone knew the Grace would be thin"); her Finesse, which the Reckoning shows him in full. Thread 1.
- *Triumph:* he holds until she tires and talks; she leaves him standing and tells her men he was not there.
- *Hard-won:* he holds; Maelis sews him afterward; Ysra takes a wound she did not expect from a seated man.
- *Costly:* he holds, but Wren is taken for an hour and talks her way out, and Ysra now knows the girl's face.
- *Setback:* he holds only because Ash takes Ysra's blade hand; Ysra withdraws with the dog's blood on her and a grudge.
**Choice (sets `ysra_spared`):** spare her when she is down (mercy +3; `ysra_spared=true`), strike (flint +3; `ysra_spared=false`), or let her go with a message for Vane (candor +2; `ysra_spared=true`).

## b2.3 — The Mill at Coldmere
Refugees at a mill bridge over a Wend tributary, drawn up the same wrong way as the clans at the ford: carts behind, children shushed, everyone looking back. Something is coming through the fields. Darrow holds the bridge so they can cross: the mirror of Harrow Ford, and this time he holds. Rae's cart is the barricade, and she reads the line before he says it (`rae.road`). On the low road Hollis rides in at the worst moment and holds the far end from the saddle. **Plants:** T5 (the shape of the line); the thing in the fields is Hollowed, many of them (T4). Threads 3, 11 (he says Tobin's name here if ever).
- *Triumph:* every cart crosses and the bridge comes down behind them on his word; the millers follow him.
- *Hard-won:* every cart crosses; the bridge is held past dark and Darrow is carried off it.
- *Costly:* every cart crosses; the mill burns, and the millers have nowhere to go but with him.
- *Setback:* every cart crosses; the Hollowed cross too, and the company runs north for two days with them behind.
**Choice:** stay with the millers (hearth +2) or send them to Saint Ysolde's (banner +2; on the low road, to a House under a Confessor's writ).

## b2.4 — Hollis's Writ
Hollis takes the paper out of the leg and looks at the wax at last: Vane's seal (T3 revealed). The order to charge, into a river the Second had been told to hold. He asks Darrow what he saw from the water. **Plants:** none new; this is a payoff of the interlude, q1.letters and b1.1. Threads 1, 2 paid off.
- *Triumph:* Hollis hears it sober and whole, and asks for the second letter to read Aldric's hand himself.
- *Hard-won:* Hollis hears it and goes out into the snow for an hour; comes back.
- *Costly:* Hollis hears it drunk, and the next day is the first he has missed teaching.
- *Setback:* Hollis finds the seal alone and Darrow must tell him with Ysra's men a field away.
**Choice (sets `hollis_truth`):** tell him everything, the horse already turned (candor +3; `hollis_truth=true`; Maelis approves), or spare him the heartbeat and tell him only the seal (guile +2; `hollis_truth=false`; Wren approves).

## b2.5 — The Stonewright Ruin
A ring of broken Oathstone in a frozen marsh, older than Calden. Darrow reads what the Reckoning lets him; Wren finishes the line he cannot and does not say how (the first time her reading is on the page; the why is Book III). The script says what the stones are for: T1 and T2 confirmed. Maelis says, "Yes," and nothing else. **Plants:** T6 (Wren reads); T7 (the stones were built to take what the Wardens built). Threads 6, 10.
- *Triumph:* they read the whole ring by lamplight and Darrow understands the ford before anyone tells him.
- *Hard-won:* they read enough; Ysra's men find the lamps and the reading ends early.
- *Costly:* they read it with the Confessors' censer smoke already on the wind.
- *Setback:* Marrant reaches the ruin first and has broken two stones; the rest must be read in his hearing.
**Choice:** tell the company what the stones say (candor +2) or carry it alone until he knows what to do with it (guile +2).

## q2.inn — The Holloway Inn
- **priority:** optional · **hook:** A dice night at an inn, and a Grace-burned knight who re-kneels at every roadside field-stone and lifts a cart off a child with hands going colder each time (the Book II temptation).
- **stages (compressed):** 1. The wager with him at dice; he shows what he can still do. 2. His hands, his frost, his certainty; the micro.
- **micro:** axis mercy_flint · 1. Tell him what the stones do, plainly (mercy +1) · 2. Let him keep his comfort (flint +1) · 3. Buy him a drink and say nothing (0) · default 2
- **payoff / spine link / can run when:** T7 plant; the temptation entry; b2.5 · Chapters after b2.1; an inn or a camp.

## q2.needle — Ysra's Doubts
- **priority:** optional (requires `ysra_spared`) · **hook:** She shadows them for three days and then asks, at a frozen weir, for a parley: why he will not kneel.
- **stages (compressed):** 1. The parley; she asks the question plainly and he answers plainly or not. 2. She tests him once more, by the forms; the micro.
- **micro:** axis sworn_unsworn · 1. "I keep the oaths I made to men. The stone had none of mine." (sworn +1) · 2. "I owe nothing I didn't build." (unsworn +1) · 3. Answer with the two-finger fist (0) · default 1
- **payoff / spine link / can run when:** Ysra's approval before she is a companion; `r.b3.ysra_fate` · b3.5 · after b2.2.

## q2.lantern — The Lantern Market Contact
- **priority:** optional · **hook:** A smuggler's letter-drop at a river mill sells writs, names and script; a letter for Darrow is waiting, from Elinor Vane (`elinor_letter`). The drop is Rae's (`rae_market_told`: told on the road, or found in oilcloth under the salt; `rae.road`).
- **stages (compressed):** 1. The drop, the price, Wren's bargaining. 2. Elinor's letter: Aldric does not sleep; the micro.
- **micro:** axis candor_guile · 1. Answer her honestly, through the market (candor +1) · 2. Answer as Aldric would want to hear (guile +1) · 3. Keep the letter (0) · default 2
- **payoff / spine link / can run when:** Elinor on the page; the market as a faction; feeds b5.4 and q5.second · after b2.1; a mill town.

## t2.high
The Knot of the Road ties at the Stonewright ring with Ysra's men turned back by the reading and the millers' word running ahead of him. The First Run: pursued across the frozen flats of the Wend, Darrow runs, badly and then well, and the company keeps up with him for once. He carries the ring's rubbing and a Lowmarch that half believes him.
- **carry-forward:** `r.route.book2.high` → the clans' outriders have heard of the bridge and meet him at the Wend as a guest (b3.1 opens with a parley, not a chase), and Ilse comes to the river herself: b3.2 arrives a chapter early (`r.once.early_arrival`).

## t2.main
The Knot ties in a marsh camp with Maelis's two fingers on his knee and the censer smoke a mile off. The First Run across the frozen Wend, Ash ahead and Wren counting breaths instead of steps. Ysra watches from the bank and does not follow.
- **carry-forward:** none.

## t2.low
The Knot ties at night, Permitted said at a run. The First Run is a rout, not a race: the company scatters across the ice and finds itself again on the far bank with the millers gone back and Ysra's horse between them and the trees. Nobody is lost; everything else is.
- **carry-forward:** `r.route.book2.low` → no word runs ahead of him; the clans meet him as a Vaelmark captain with a sword, and b3.2 costs a chapter more to earn.

# Book III — The Running Dark

## book3.question
*Who are the real enemy?* **State:** Darrow can run, in bursts and then steadily; chases, journeys, escapes. No leaping or hard turning yet. Knot IV tied; V ends the Book.

## b3.1 — Across the Wend
Into the Thornwild in deep winter. The clans' watch finds them; a chase through old forest that Darrow can finally run; Rae's few clan words and her grandmother's name buy the first hearing (`rae.road`). **Plants:** the clans' burned Oathstone chips worn as charms against the Hollowed (T4); every clan door has a lamp. Thread 5.
- *Triumph:* the watch takes them in as guests of the bridge. · *Hard-won:* taken in as prisoners, fed anyway.
- *Costly:* two days running before a parley. · *Setback:* taken in after Ash is hurt; the clans want the dog, not him.
**Choice:** give up his sword at the holdfast door (sworn +2) or keep it and stand outside (unsworn +2).

## b3.2 — Ilse of Corrach
The red-handed woman, named at last (`ilse_named`). Why she saved him: "Someone from the Vaelmark had to see, and you were the one looking." Her Reckoning in full, if his Eye is high enough. **Plants:** T5 (the carts); T4 (what the grey figures were). Thread 5 paid off.
- *Triumph:* she tells it by the fire with the clan listening. · *Hard-won:* she tells him alone and asks him to carry it.
- *Costly:* she tells him after a duel he loses with grace. · *Setback:* she tells him because the Tide is a day off and there is no time not to.
**Choice:** tell her what he saw on the west bank (candor +2) or hold it until he knows her price (guile +2).

## b3.3 — The Hollow Tide
T4 and T5 revealed: the Hollowed are the drained, the Vaelmark's own; Harrow Ford was a slaughter of people fleeing them. A night action at the river line: Darrow runs between two palisades and holds neither; he carries. **Plants:** the Tide turns toward anyone Grace-sworn first (b4.2). Thread 3, 4 paid off.
- *Triumph:* the line holds and the clans see a Vaelmark knight carry their children. · *Hard-won:* the line bends; he runs all night.
- *Costly:* the outer palisade burns; the holdfast holds. · *Setback:* the river line is lost and the Long Night will be fought at the holdfast wall.
**Choice:** carry the wounded (hearth +2) or carry the word to the next holdfast (banner +2).

## b3.4 — The Far Cot's Name
Wren's quest: a clan elder, or a Confessor's seized ledger, has the name Dame Elspeth Ashdown (`elspeth_named`). The ledger travels by cart like all the Order's paper, and if `r.rae.ledger` is armed it is Rae who knew which crate and had it off the Holloway whole, and says nothing of it until Wren asks; otherwise the page is half burned (the Setback shape in any tier). T6 revealed: an Ember initiate who would not re-kneel, Hollowed on purpose; she taught her daughter the script before it took her. Wren reads the page herself. **Plants:** the Confessors keep ledgers of the Hollowed (b4.5, q4.censer). Thread 10 paid off.
- *Triumph:* Wren reads it aloud and then counts the holdfast's lamps until she can speak again. · *Hard-won:* she reads it alone and tells Darrow at dawn.
- *Costly:* Marrant's ledger names Mother Ione as witness. · *Setback:* the page is half burned and the rest she must take on Ilse's word.
**Choice:** write the name in his own hand on the holdfast's lamp-post (candor +2) or let Wren decide who hears it (hearth +2).

## b3.5 — The Long Night
Real midwinter. A Hollow Tide against the clan holdfast; Darrow runs the wall all night. Ysra's choice: `r.b3.ysra_fate` (defects if `ysra_spared`; otherwise dies holding a gate she was sent to open). **Plants:** the Tide's frost on the Grace-sworn deserter among the clans (b4.2). Threads 4, 11.
- *Triumph:* the wall holds to dawn and the Tide breaks on the river. · *Hard-won:* the inner gate holds; the outer yard is lost and retaken.
- *Costly:* the holdfast holds; the clan's winter stores burn and they must move. · *Setback:* the holdfast is abandoned at dawn in good order, everyone alive, and the Tide has the valley.
**Choice:** stay with the clans through the thaw (hearth +2) or go west at once to raise the Lowmarch (banner +2).

## q3.hunt — The Night Hunt
- **priority:** optional · **hook:** A clan rite: a boar run through the Thornwild by torchlight; a guest who runs it is kin.
- **stages (compressed):** 1. The run, which he can do now and loves. 2. The kill, and whose spear it was; the micro.
- **micro:** axis hearth_banner · 1. Give the kill to the clan boy who turned it (hearth +1) · 2. Take it, because the clan needs to see the Vaelmark bleed for them (banner +1) · 3. Give it to Ilse (0) · default 1
- **payoff / spine link / can run when:** clan standing; thornwild faction · b3.3 · after b3.2.

## q3.needle — The Needle's Oath
- **priority:** optional (requires `ysra_spared`) · **hook:** Ysra comes to the holdfast alone, under a truce lamp, with Vane's new orders in her hand.
- **stages (compressed):** 1. The orders, read aloud. 2. She asks what oath she could swear to him; the micro.
- **micro:** axis sworn_unsworn · 1. "Swear to the people on the wall, not to me." (sworn +1) · 2. "Swear nothing. Stay or go." (unsworn +1) · 3. Give her the two-finger fist (0) · default 1
- **payoff / spine link / can run when:** Ysra as companion (`plan companion arrive ysra`) · b3.5 · after b3.2.

## q3.lamps — Lamps on the Wend
- **priority:** floating (q1.hollownight re-skinned) · **hook:** A Hollowed Vaelmark knight wanders into the holdfast's lamps and the clan wants him burned.
- **stages (compressed):** 1. The knight, the lamps, the clan's law. 2. Darrow's word in the circle; the micro.
- **micro:** axis mercy_flint · 1. "He was a man. Give him the far cot." (mercy +1) · 2. "Burn him. It's what's left." (flint +1) · 3. Ask Ilse (0) · default 1
- **payoff / spine link / can run when:** T4 made personal; thornwild faction · b3.3 · any Book III chapter.

## t3.high
Knot V ties at the holdfast with the clans calling him kin. Lightning: he leaps a broken bridge with the Tide behind him and Ilse's riders waiting on the far side. He carries a clan token and a column of volunteers.
- **carry-forward:** `r.route.book3.high` → the clans ride west with him; b4.1 opens with a host, not a handful.

## t3.main
Knot V ties in the thaw camp. Lightning: the broken bridge, the leap, the landing, the Tide stopping at the water as it always does. Ilse comes; the clans do not, yet.
- **carry-forward:** none.

## t3.low
Knot V ties on the move, the holdfast behind them. Lightning: the leap is made in the dark because the bridge is the only way out, and the company crosses one by one with the Tide's breath on the boards. Ilse comes alone.
- **carry-forward:** `r.route.book3.low` → the clans blame the Vaelmark captain for the lost valley; no clan rides west; b4.1's gathering starts from the Faithless alone.

# Book IV — Lightning in the Marches

## book4.question
*Can the Unkneeling be more than one man?* **State:** power, speed and the stop return; deceleration is a weapon (Anchor: stopping a charge dead). Knot V tied; VI ends the Book.

## b4.1 — The Gathering
An abandoned Mender house in the Marches: Faithless, clans, deserters, millers, and a Confessor's prisoner who asks to stay. Darrow learns that leading men who can run is harder than leading men who cannot. **Plants:** a deserter's hands warm for the first time in years (T7). Thread 8.
- *Triumph:* two hundred by the first bell. · *Hard-won:* sixty, and the right sixty.
- *Costly:* sixty, and a Confessor spy among them who is found kindly. · *Setback:* thirty, and the Marches' levies told to hunt them.
**Choice:** take the Mender house's bell for the host (sworn +2) or leave the house as it was (unsworn +2).

## b4.2 — The Stolen Fire
T7 revealed: a sworn knight who stops kneeling sees his first Reckoning, faint as frost; the Grace is Ember taken instead of built. Maelis teaches the first forms to a yard of knights who cannot kneel because they will not. **Plants:** Maelis teaches as one who was taught (T8). Thread 6 paid off.
- *Triumph:* a dozen Reckonings in a week. · *Hard-won:* three, and the rest patient.
- *Costly:* one, and a knight who re-kneels in secret and is not punished. · *Setback:* none yet; the host doubts, and holds anyway.
**Choice:** teach it openly, in the yard (banner +2) or to the few he trusts (hearth +2).

## b4.3 — Maelis's Story
T8 revealed (earlier only if `r.t8.early`): she was a Confessor sent to hunt the last Warden, who mended her; two Bindings before Darrow, both dead. She tells it once. **Plants:** the sword PATIENCE was the Warden's. Thread 7 paid off.
- *Triumph:* she tells the host. · *Hard-won:* she tells Darrow and Wren.
- *Costly:* Marrant tells it first, at a parley, and she confirms it. · *Setback:* she tells it because a knight tore his Binding by trusting the quiet, and the host must hear why.
**Choice:** keep her secret from the host (guile +2) or stand beside her when she tells it (candor +2).

## b4.4 — The Last Stand of the Sixth
Hollis holds a ford-house with the Sixth's survivors so the host can cross. `r.b4.hollis_lives` (approval ≥ 50 and `hollis_truth`) decides whether he comes back; if not, `hollis_fell`. Either way he fights sitting down and nobody is lectured. **Plants:** Marrant leads the Confessors' van with a Hollow leash (q4.censer).
- *Triumph:* the ford-house holds and the Sixth marches out singing badly. · *Hard-won:* it holds; Hollis is carried out.
- *Costly:* it holds; the ford-house burns behind them. · *Setback:* it holds until the host is across, and the Sixth is scattered, not lost.
**Choice:** turn the host back for him (hearth +3) or hold the far bank as he asked (sworn +3).

## b4.5 — The Turning Blade
Darrow learns from Ilse, or from a Warden mural, that the master form is the pivot: *turn at speed and strike from the turn*. He is not cleared to do it; Maelis forbids it; he watches Ilse do it and counts. **Plants:** the ford stones (b5.4). Thread: the memory.
- *Triumph:* he teaches the stop to the host and the Confessors' charge breaks on it. · *Hard-won:* the stop holds the yard; he does not turn.
- *Costly:* the stop holds; he nearly turns, and Wren says the number of the step aloud. · *Setback:* the host retreats in good order, and he does not turn.
**Choice:** march for the ford now (banner +2) or winter the host (hearth +2).

## q4.deserters — The Oath Unsaid
- **priority:** optional · **hook:** A sworn knight asks Darrow to witness him *not* kneeling at a field-stone: there is no form for it, so they make one.
- **stages (compressed):** 1. The stone, the knight, the host watching. 2. The words; the micro.
- **micro:** axis sworn_unsworn · 1. Give him the Ninth's old words, turned (sworn +1) · 2. "Say nothing. Stand up." (unsworn +1) · 3. Let Maelis speak (0) · default 2
- **payoff / spine link / can run when:** the Unkneeling as a rite; T7 · b4.2 · after b4.1.

## q4.marches — The Levy Road
- **priority:** optional · **hook:** A village levy, boys with billhooks, marched toward the ford by a Confessor's sergeant.
- **stages (compressed):** 1. Taking the column without a death. 2. What to do with forty boys; the micro (the ones sent home go in Rae's cart).
- **micro:** axis hearth_banner · 1. Send them home (hearth +1) · 2. Arm them (banner +1) · 3. Let them choose (0) · default 1
- **payoff / spine link / can run when:** crown and faithless factions · b4.4 · any Book IV chapter.

## q4.censer — Marrant's Return
- **priority:** optional · **hook:** Marrant, with a leash of Hollowed, taken at last at a river crossing, unarmed as always.
- **stages (compressed):** 1. The taking, and what he says to Maelis. 2. The host wants him; the micro.
- **micro:** axis mercy_flint · 1. Keep him alive for the ford (mercy +1) · 2. Give him to the Sixth (flint +1) · 3. Give him to Mother Ione's law, by letter (0) · default 1
- **payoff / spine link / can run when:** Marrant's fate; confessors faction · b4.4, b5.4 · after b4.3.

## t4.high
Knot VI ties in a yard full of Reckonings. The first turn on purpose since the ford: at speed, on a dry stone, with the host watching and Maelis's hand lifted to say Permitted before he asks. He carries a host and Hollis's voice from the back of it.
- **carry-forward:** `r.route.book4.high` → the Second Lance's rank and file send word they will not charge the Unkneeling (q5.second opens as a parley already half won).

## t4.main
Knot VI ties on the march. The turn: on a river stone at dawn, alone but for Wren counting, and it holds. Then he does it again so she can see.
- **carry-forward:** none.

## t4.low
Knot VI ties in retreat. The turn is made because a Confessor's rider is behind him and there is no other way to face him; it holds, and he stands over a man he does not kill. The host is smaller and all alive.
- **carry-forward:** `r.route.book4.low` → the Marches close their gates to the Unkneeling; the march back to the ford is made on the Holloway in the open, and Vane knows the day he will arrive.

# Book V — The Turning Blade

## book5.question
*Can he trust the leg?* **State:** reactive, cutting, full speed. The enemy here is fear: Resolve checks against the memory of the Three Heartbeats. Knot VI tied; VII ends the Book.

## b5.1 — The March Back
The Holloway reversed, village by village, the counting rhyme sung at him from doorways with the sum changed; it is Rae's road, and the villages that open, open to her first (`rae.road`). Confessors' writs on every bell-house door carry his epithet. **Plants:** the field-stones' iron frames still stand on the west bank (b5.2). Thread 11.
- *Triumph:* villages open and feed the host. · *Hard-won:* they watch and do not hinder.
- *Costly:* the Second's outriders burn the bridges ahead. · *Setback:* a Lowmarch levy must be talked out of the road twice, and the host arrives late and tired.
**Choice:** march under the Ninth's old banner (sworn +2) or under none (unsworn +2).

## b5.2 — The Memory
The west bank of Harrow Ford. The frames. The place he knelt. The memory comes for him in daylight: Resolve DC 14 against the Three Heartbeats, and the leg answers or the breath does. Rae, through the Holloway's carters, knows the Second has been moving the field-stones' iron frames and where Vane means to stand on the day (`rae.road`). **Plants:** none; a payoff of the prologue. Thread 11 paid off (he says Tobin's name, if ever, here).
- *Triumph:* he walks into the shallows and back without anyone seeing what it cost. · *Hard-won:* Wren counts him through it.
- *Costly:* he cannot cross that day, and says so to the host. · *Setback:* he crosses only because Vane is already on the far bank and the choice is taken from him.
**Choice:** tell the host about the heartbeats he saw from the water (candor +2) or let them believe he is unafraid (guile +2).

## b5.3 — The Form
Ysra, if alive, drills the turn with him in the river meadow; else Ilse. The pivot, done a hundred times slow before it is done once fast. Maelis says Permitted for the last form she will ever have to say it for. **Plants:** PATIENCE's full inscription is not yet read (finale).
- *Triumph:* the turn at speed, clean, and the host cheers. · *Hard-won:* clean, in private, and he keeps it for the ford.
- *Costly:* he turns on a wet stone and goes down and gets up, and nobody says a word. · *Setback:* the drilling is cut short by Vane's herald, and the turn is untested when it matters.
**Choice:** show Vane's herald the turn (banner +2) or send him back with nothing (hearth +2).

## b5.4 — Vane on the Ford Stones
The duel on the stones where it broke. Vane full of borrowed Grace; Darrow with only what he built. Vane quotes his answer if `vane_answered`. Darrow turns at speed on the same stone and strikes from the turn; the Seventh Knot waits on it. **Plants:** Vane's hands are cold (T1 made personal). Threads 1, 2.
- *Triumph:* Vane is down on the stone and the Second lowers its lances. · *Hard-won:* Vane is down; the Second holds its line and waits for the word.
- *Costly:* both are down in the water and Ysra, Ilse or Hollis drags them out. · *Setback:* Vane withdraws across the ford unbeaten, and the choice is made at a parley on the stones at dusk.
**Choice:** 1. Kill him (flint +4: a betrayal of the brother; if it names him, Elinor says *Flintheart* on the stones). 2. Spare him, sworn as he is (mercy +3; `vane_spared`). 3. Unbind him: hold him at the field-stone and let the Grace go out of him with Maelis's hands on his back *[Mercy 4 or Candor 4]* (mercy +3; `vane_unbound=true`; feeds `r.finale.return`).

## q5.rhyme — The Counting Rhyme
- **priority:** optional · **hook:** A festival night in a Lowmarch village: lamps, cider, children singing the rhyme at the host with a new last verse about a knight who would not kneel.
- **stages (compressed):** 1. The night, and what the children have made of him. 2. A mother asks if her son on the list is alive; the micro.
- **micro:** axis candor_guile · 1. The truth, whatever it is (candor +1) · 2. "He was brave." (guile +1) · 3. Say nothing; sit with her (0) · default 1
- **payoff / spine link / can run when:** the counting motif; the Lowmarch's version of him · b5.1 · any Book V chapter.

## q5.second — The Second Lance
- **priority:** optional · **hook:** Elinor Vane, under a truce lamp, with the Second's captains behind her: they will hear him once. The Second's baggage train is carters, and word of the bridge and the host ran through them before any herald: Rae's network, never named as such (`rae.road`).
- **stages (compressed):** 1. The parley at the river meadow. 2. What he offers the Second; the micro.
- **micro:** axis sworn_unsworn · 1. "Keep your oaths to each other. Break the one to the stone." (sworn +1) · 2. "Owe nothing. Stand with us or go home." (unsworn +1) · 3. Let Elinor speak for him (0) · default 1
- **payoff / spine link / can run when:** Elinor on the page in person; the Second's tier at b5.4 · b5.4 · after `elinor_letter` or b5.1.

## q5.tobin — Tobin's Song
- **priority:** optional · **hook:** Tobin Marsh's mother keeps the inn at the ford village and has never been told how. Rae carted his bundle there after the ford and knows her face (`rae.road`).
- **stages (compressed):** 1. The inn; the song, which she hums. 2. She asks; the micro.
- **micro:** axis mercy_flint · 1. "He went under his horse. I turned toward him. I was too slow." (flint +1; the whole truth, with his own name in it) · 2. "He died in the water with the Ninth. He didn't suffer." (mercy +1) · 3. Say his name, and nothing else (0) · default 2
- **payoff / spine link / can run when:** thread 11 paid; the name said aloud · b5.2 · before b5.4.

## t5.high
The Seventh Knot ties on the ford stones with the Second's lances down and the river low. He carries a brother, bound or spared, and a Lance that will march to Calden behind two banners.
- **carry-forward:** `r.route.book5.high` → the Second Lance marches with the Unkneeling; Calden's gates are opened from inside (b6.1).

## t5.main
The Seventh Knot ties on the far bank at dusk, Maelis's fingers on the joint and the river loud. He crosses back to the west bank on his own legs, and does not look at the frames.
- **carry-forward:** none.

## t5.low
The Seventh Knot ties in the river meadow with the Second withdrawn unbeaten and the host thinner, all alive. He goes toward Calden with what he has and a road that is watched.
- **carry-forward:** `r.route.book5.low` → Calden is warned and the Oathspire sealed; b6.1 is a siege of bells, not an entry, and Marrant (if alive) holds the Spire's door.

# Book VI — The Unkneeling

## book6.question
*Now that he can kneel, what will he kneel to?* **State:** whole for battle. Knot VII tied; the Book ends on the finale, not a Knot. The epilogue's shape is `t6`.

## b6.1 — The Hundred Bells
Calden: white stone, a hundred bells, writs on every door. The Lantern Market's people inside the walls; Saltreach's fog on the river. The Unkneeling enter by the road the Book V road gives them. **Plants:** the bells of Calden ring the hours but have never rung sanctuary (b6.3).
- *Triumph:* the gates open from inside. · *Hard-won:* a night entry by the river stairs.
- *Costly:* a fight at the gate, no one lost. · *Setback:* a siege of bells, and the city made to choose.
**Choice:** silence the bells (guile +2) or ring them all at once for sanctuary (candor +2).

## b6.2 — The Oathspire Stair
Black glass and iron; the stair every knight has climbed on his knees. Darrow climbs it on his feet with Maelis, Wren and whoever the roads left him. The green-lit hall; the sound of very slow breathing. **Plants:** every Oathstone's frost runs toward the Spire (T1 made visible).
- *Triumph:* the stair is empty; the Oathsworn would not hold it. · *Hard-won:* held floor by floor with Anchor and the turn.
- *Costly:* Marrant on the last landing, unarmed, talking. · *Setback:* the First Stone draws as they climb, and the sworn among the host must be carried.
**Choice:** carry the Grace-sworn up (hearth +2) or leave them below with the Second (banner +2).

## b6.3 — The Evergreen
King Aurel, three hundred years old because the Stone feeds him: pitiable, terrified of dying, certain the realm dies with him. He asks Darrow to kneel, once, as a courtesy. **Plants:** none; everything is paid. The finale follows directly.
- *Triumph:* the hall is his and the king's guard has knelt to no one. · *Hard-won:* the hall is held; the king talks.
- *Costly:* the king's guard fights and is spared. · *Setback:* the king has begun the draw and the finale is chosen with the floor cold.

## finale
The three options stay as they are; which are offered is read from the ledger before the climax is written:
- **Shatter the First Stone** (`r.finale.shatter`, always offered). Every sworn knight loses the Grace at once, a kingdom-wide Three Heartbeats: this time warned of, and the Unkneeling stand ready to catch them. Costly, honest.
- **Take the Stone** (`r.finale.take.tempting`: a true temptation when `temptation.count >= 3` and he leans Banner or Flint; otherwise written flat). Darrow becomes the new Evergreen. The dark ending.
- **Return the tithe** (`r.finale.return`: Maelis ≥ 50, Wren ≥ 50, and `anselm_spared` or `vane_unbound`). Unwind the Stone slowly, give each knight back their own, and teach the Ember: the long road for everyone.
**The final image:** Darrow kneels, freely and once, and his knee holds. *Kneel because you can, not because you must.* The sword's full inscription, read as he kneels: *PATIENCE IS A BLADE THAT CUTS ONLY FORWARD.* The last chapter contains a count (Wren's). If `r.rae.form` is armed, the image after it is the form they made (rae.tether stage 5): he stands up to her.
- **Trigger:** the real milestone **first comfortable, cleared kneeling on the left knee**, recorded as `milestones.first_kneel` in `real/config.json`. If it arrives before the finale, give it one private, quiet scene when it happens (he kneels alone in a chapel and tells no one; `first_kneel_private`) and save the public kneel for the end.

## q6.bells — The Bell-Ringers
- **priority:** optional · **hook:** Calden's ringers are a guild, and a guild can be bargained with: a night in the ringing-loft above the city.
- **stages (compressed):** 1. The loft, the ropes, the guild-master's price. 2. What the bells will say at dawn; the micro.
- **micro:** axis candor_guile · 1. Tell the city plainly what the Stone is (candor +1) · 2. Ring sanctuary and let them wonder (guile +1) · 3. Ring the hours as always (0) · default 1
- **payoff / spine link / can run when:** bells as law, one last time · b6.1 · before b6.2.

## q6.market — The Lantern Market
- **priority:** optional · **hook:** The Market sells the words that open the Spire's lower door, and wants something only Darrow has: a true account of the ford, in his hand.
- **stages (compressed):** 1. The bargain in the fog. 2. Who else is buying; the micro.
- **micro:** axis hearth_banner · 1. Buy the door-words for his own people only (hearth +1) · 2. Buy the account's printing for the whole realm (banner +1) · 3. Walk away (0) · default 2
- **payoff / spine link / can run when:** lantern_market faction; the account on the page · b6.2 · after b6.1.

## t6.high
The epilogue after a high Book: the Unkneeling hold Calden with the Second; the Houses of the Menders ring at every dawn; Mother Ione sees the Steps from the bottom.
- **carry-forward:** `r.route.book6.high` → the epilogue is written from Saint Ysolde's gate with the whole company present.

## t6.main
The epilogue on the Holloway, going north, Wren counting the miles because there are no steps.
- **carry-forward:** none.

## t6.low
The epilogue with fewer of his own around him and all of them alive; the realm slow to believe; the long road begun anyway.
- **carry-forward:** `r.route.book6.low` → the epilogue is written from the road, not the House; Hollis's absence (if `hollis_fell`) is felt in one line, never explained twice.

## temptation
From Book II on, one beat per Book where the fast, borrowed way visibly works for someone, and its bill comes due a Book later. Record each with `saga.py plan temptation add "…"`; `temptation.count` feeds `r.finale.take.tempting`.
- **Book II (q2.inn):** the Grace-burned knight re-kneels at a roadside stone and lifts a cart off a child. Bill, Book III: they find him at the edge of the Ashen Fields, Hollowed, walking east. If q2.inn is not run, the same knight appears for one paragraph at the Coldmere inn in b2.1 and is recorded then (`plan temptation add`).
- **Book III (b3.3 / b3.5):** Ilse's rival swears at a captured field-stone and holds a palisade alone. Bill, Book IV: he is the first Hollowed of the Thornwild, and the clans blame the Vaelmark captain who brought the stone's war to them.
- **Book IV (b4.2):** a captain of the Unkneeling kneels in secret and wins a field for the host. Bill, Book V: Vane turns him, and he leads the Confessors' van at the ford.
- **Book V (b5.3 / q5.second):** Vane offers the Grace back to the whole host for one knee on the stone; one of Darrow's captains takes it for his men and they stand like gods for a day. Bill, Book VI: they are the ones who fall first when the Stone is shattered, or who hold it for him if he takes it.
- **Book VI (b6.3):** the king offers Darrow the Stone itself, and it would work: the realm kept, the Hollowing ended by decree, every knight fed. Bill: the finale's second option, and the reason it must feel tempting.
