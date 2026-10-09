# ⚠️ GM EYES ONLY — Characters: wants, fears, arcs, secrets and hidden sheets

Everything about a character that is **not on the page** lives here: never in `saga/characters/*.json` (rendered on a public site) and never in `cast.md` (reader-safe; appearance and voice only, for people the page has shown). Reveal only on the schedule in `arc.md`, and plant twice first. Companion **approval** (−100 to +100) lives in `saga/state/world.json` and moves only through the consequence ledger (`saga.py add`), never with real-life numbers and never by hand.

For people already on the page, appearance and voice are in `cast.md` and this file keeps the rest. For people not yet on the page, the whole entry is here; the day they appear, appearance and voice move to `cast.md` and they get a `saga/characters/` file.

---

## On the page

### Ser Darrow of Edgemoor — Knight-Captain of the Ninth Lance
Appearance and voice: `cast.md`.
- A horse-breeder's son from a minor house in the Edgemoor hills, raised to captain by talent rather than birth. Before Harrow Ford his men called him **Quickstep**: the fastest blade in the Lowmarch, and he fought from his feet, footwork, angles, turning a man before the man knew he had been turned. Proud of it, careless with it, fed by the Grace like everyone else.
- Nineteen of his sixty came home. He remembers every name of the forty-one who did not, and says none aloud. When he finally says Tobin Marsh's name it should cost him.
- **Now:** the leg is bound and weak; for the first time in his life he has to wait, and waiting does not come naturally.
- **Flaw:** he wants the old self back, and that wish is the trap. **Arc:** from wanting to be who he was to choosing who he is building; from fighting to get back to fighting to go forward.
- **Signature:** in the Ninth, a raised fist with two fingers out meant "hold." He hated giving that signal.
- **The Knight Who Fell (the benchmark):** the Reckoning sometimes shows him, faintly, the measure he had at Harrow Ford: Might 15 · Vigor 15 · Finesse 18 · Resolve 12. Surpassing each is a story moment. Resolve is the first he will pass, and he will not notice when he does.

### Maelis Vorne — the Mender
Appearance and voice: `cast.md`.
- Former field surgeon of three campaigns; now senior Mender at Saint Ysolde's. She performed the Binding and reads it each week with two fingers and her eyes shut (the Reading of the Knots).
- **Rule of the saga:** Maelis never clears Darrow for anything the real-world plan has not cleared. Her verdicts track the PT's.
- **Wants:** to see one Binding hold. **Fears:** the soft season.
- **Hides:** thirty years of Warden practice (T8); she saw his Reckoning begin before he said a word. She tells her own story only in Book IV, or earlier if `r.t8.early` arms.

### Ser Hollis Garrow — the Old Captain
Appearance and voice: `cast.md`.
- Knight-Captain of the Sixth Lance. He will teach Darrow **the Seated Blade**, the art of fighting without footwork, from a chair across a practice ring; he learned it in his own chair, recently and badly. The Art is not named on the page until he teaches it there.
- He also teaches throwing from a chair, the first lesson of winning sitting: **The Measured Hand** (a Sport Art, open now), then **Overwall**. Neither is named on the page until he teaches it (threads: Sport Arts).
- Calls Darrow "Captain" to mock him, and later means it. Never "the boy".
- **Wants:** a drink; absolution; someone to have been worth it. **Carries:** the order to charge, the writ he broke with his thumb at the ford without looking at the seal, its words known by heart, its seal never once looked at; since the Interlude it lies folded in the cup of the beech leg (T3: the seal is Vane's; b2.4 is where he finally looks). **Flag:** `hollis_truth`; `r.b4.hollis_lives` decides his last stand in Book IV.

### Wren Ashdown — the Runner
Appearance and voice: `cast.md`.
- Grew up in the House after her mother, a knight, was brought up the Steps Hollowed when Wren was nine. Runner, ledger-keeper and resident liar of Saint Ysolde's; counts everything (steps, 1,117; bells; cots; debts). In Book I she is Darrow's legs. Her ledgers supply chapter epigraphs.
- **Wants:** to know what happened to her mother. **Hides:** that she can read Warden script (T6). The page may catch her at it before then (q1.ledger, the Stonewright ruin at the end of Book II); the why, and her mother's name, stay for Book III.
- Her mother was **Dame Elspeth Ashdown**, a secret Ember initiate who refused to re-kneel, Hollowed on purpose by the Confessors; she died on the far cots four years ago. Neither the name, the Hollowing nor the death is on the page yet; the page has only "one of the far cots".

### Rae Thorne — the carter
Appearance and voice: `cast.md`. On the page since the Prologue (the last cart; revised 10/9) and named in Chapter 1 (Wren's news; the cart at the winch-house seen from the window). The love interest; the romance is **the Tether** (`design.md` §8).
- Thirty, of Coldmere. She holds the House's carting: the last cart from the barge landing up the Holloway to the winch-house at the foot of the Steps, and the winch-cage itself, which her father built for the House and died on, six winters ago, when a rotten splice let go with him in it; she re-laid the rope, rebuilt the cage and has run it since. Up: salt, oil, flour, linen, letters, the wounded. Down: the House's letters, the effects of the dead, and the ones who walk down. She has brought a great many men to the foot of the Steps. She does not count them (Wren counts); she remembers faces, and which ones came down again.
- The name is the village's word worn smooth: her grandmother was Thornwild-born, a clanswoman who came over the Wend with a Lowmarch drover, and Coldmere called the family "the Thornwild woman's" until it wore down to Thorne, and they kept it. Rae has a few dozen clan words from her, a knack with oxen that Coldmere calls witchy when it is angry with her, and her grandmother's stories of what walks out of the grey country east of the Wend, which she has never believed (T4). In Book III the words make her the company's bridge to the clans; at the mill (b2.3) she reads a cart line drawn up to flee the way Darrow read it at the ford, carts behind and everyone looking back (T5).
- **The forty-one.** After the ford she carted the Ninth's dead's effects down the Holloway to the bell-house at Coldmere for the Crown's clerks: forty-one bundles, each with a tag in a clerk's hand. She never counted them; she remembers every tag. The hand on the tags was Vane's secretary's (the Second was the only lance whole enough to do the clerking), the hand that will address Mirren's letter in b1.4: she has seen it forty-one times. Payoffs: Tether IV (she can say the names; he asks her to stop), q5.tobin (she carted Tobin's bundle to his mother's inn).
- **Quiet competence.** She is the most capable person in the company and the last to say so; the page shows the result, and someone else (Wren's count, Hollis's grudging oath, Maelis's one word) notices the cause, usually late. Never a flourish, never a speech. By Book: **I** — she drove through the night with the winter's last load, not only the news: she heard the list and understood what a camp at the winch-house would mean, so the House's salt and oil are already up when the rope is cut (b1.5), and only the kitchen's loaf-count says why. She reads a camp by what it buys: from the flour the grey cloaks took at Coldmere she can say how many men and how many days they mean to stay (q1.cart stage 1). She pads a manifest so the "inspected" load the Confessors let up is the one she wanted up (stage 2). A rope you can see is a rope that can be cut (her father's saying): when Marrant has the cage cut, there is a second line nobody saw. **II** — a carter can make a road lie: two carts' tracks out of one cart by shifting the load (b2.2, Ysra's hunt); the levy sergeant leaves Coldmere knowing nothing, having talked oxen with her for an hour (b2.1, any tier); the Market drop she has run for years without a seized letter, telling a writ from a love letter by wax and weight without reading either (q2.lantern). **III** — the clan way of asking, a gift before the ask, which she has from her grandmother and Darrow does not (b3.1); she counts the holdfast's stores and gives Ilse a number Ilse's own people got wrong (b3.3); for the winter move she draws the carts up *right*, the reverse of the ford, so the Tide sees a line that is not fleeing (b3.5). **IV** — quartermaster of the host without the title (b4.1); the levy boys go home because she tells them what their sergeant said of them in Coldmere (q4.marches); **the Confessors' ledgers travel by cart, and she knows whose**: that is how a seized ledger comes whole into Wren's hands (b3.4 with `r.rae.ledger`; q4.censer, Marrant's leash-ledger rides in a crate she can name). **V** — the carters of the Holloway are a network and she is of it: the Second Lance's baggage train is carters, word runs through them (q5.second), and she knows the Second has been moving the field-stones' iron frames and where Vane means to stand (b5.2). **VI** — the Oathspire's lower door opens for carts; she has driven to it once (below); the Market's carters inside Calden's walls are her trade (b6.1, q6.market).
- **The cold she knows (T1, her key plant).** Years ago she carried a Market crate to Calden's lower door and never knew what was in it; her cart-bed froze in midsummer under it and the oxen would not stand near. When the frost comes to Benedek's mouth and the undercroft floor (b1.2, b1.3) she is the first to know it for what it is, and says only, "I've had that cold in my cart." Nothing more until Book II confirms it. **Her Reckoning grows** on the road: Resolve 13 → 15 and Level 3 → 5 by Book IV, Kindled, which Darrow reads and does not say. She never takes a knight's Art; what the page may give her by Book IV is Warden's Eye I, earned the way she earns everything, by looking.
- **Thistle.** The grey mare came out of the Wend at the mill weir below the ford, lame in the off fore, and went to a Holloway horse-dealer at the Coldmere fair. Rae knew the Ninth's brand on her quarter and has paid for the mare's feed out of her own purse since, without saying why, or knowing exactly why. She asks whether the captain of the Ninth rode a grey (Chapter 1, slot 6). Nothing of this is on the page; the codex has "fate unknown". Payoffs: q1.cart stage 2 (the price), Tether III (the mare delivered; `thistle_found`).
- **Wants:** the cart and the oxen free of the debt on them (owed to her uncle, who keeps the inn at Coldmere where the list was read); to see one thing she carried up come down whole. **Fears:** the rope; being the last person to have seen a face. **Hides:** she carries for the Lantern Market too, because a carter carries for everyone: the letter-drop at the river mill on the Holloway (q2.lantern) is hers, writs and names and script in oilcloth under the salt. She has never sold a name and has read none of it. `rae_market_told`: whether she tells him before he finds it.
- **How she speaks to him:** nothing at all, which everyone notices, until Tether I; then Darrow, never Ser, never Captain ("I don't drive for the Ninth. I drive for the House."). Her saying is *"Road's the road."* (codex when the page speaks it). She never asks him to come down the Steps; she comes up. She would take the fast road herself, she says, if anyone offered it to carters: Tether II's question.
- **Arc:** from the woman who carries other people's lives up and down a cliff to one who picks a road and a person to walk it with. The Tether's stages are the Ledger's and its shape is his choices'; her approval is story-only and moves only through the ledger (`plan companion arrive rae` when q1.cart stage 3 writes; before that a choice she saw carries an explicit `now.approval.rae` with `saga.py add --pending`, since `--witnessed` only knows companions already arrived). On the road from t1 in every shape (`arc.md → rae.road`): she drives for the company. She lives in every road and is never the price of anything, and neither is the knee (design principle 4).
- **The form.** Knights marry kneeling (`world.md` §6); she would not have him kneel anyway. Tether V with approval ≥ 50 arms `r.rae.form`: the epilogue's one image after the final kneel. **Flags:** `thistle_found`, `rae_market_told`, `rae_vow`. **Rules:** `r.rae.form`, `r.rae.parts` (approval ≤ −25: she drives home for a Book; the stages never fall), `r.rae.ledger` (approval ≥ 40 by b3.4: the seized ledger comes whole, her doing; else half burned).

### Ser Aldric Vane — the Knight-Confessor
Appearance and voice: `cast.md`.
- Darrow's sworn brother: squired together, knighted the same morning kneeling side by side; rode at Darrow's left hand at Harrow Ford. Now leads the Confessors, charged with bringing the Faithless of Harrow Ford to the Oathspire to kneel again. Devout, disciplined.
- Writes Darrow letters that are genuinely loving: *"Come home, brother. Kneel, and be whole."* None has reached the page yet.
- **Wants:** order; his sister Elinor safe; Darrow back. He is not a liar. He believes.
- **Hides:** he knew the Three Heartbeats were coming (T2) and turned his horse one beat early; the charge order bore his seal (T3). The page has Darrow *believing* the list was written in his hand; nothing has confirmed it. **Flag:** `vane_unbound` (Book VI).

### Tobin Marsh
Appearance and voice: `cast.md`.
- Youngest knight of the Ninth; went under his own horse in the current while Darrow turned toward him. Dead at the ford. The site shows a memorial line instead of a sheet.

### Mother Ione — Prior of Saint Ysolde's
Appearance and voice: `cast.md`.
- Appearance and voice (not yet on the page; move to `cast.md` the day she is seen): the Prior of Saint Ysolde's, in her seventies, gentle in face and manner, with iron under the gentleness. She speaks in questions, and the questions are never idle.
- Holds the sanctuary right and will die before she yields it. **Wants:** every name under her roof kept. **Fears:** the bell falling silent at a dusk when it must ring.
- **Hides:** possibly what happened to Elspeth Ashdown (T6). In the low road of Book I she is left answerable to a Confessor's writ for every name in the House.

### Sister Pell — keeper of the bells
Appearance and voice: `cast.md`.
- Appearance and voice (not yet on the page; move to `cast.md` the day she is seen): keeper of the House's bells, old, and nearly deaf from fifty years of them. She reads lips, has no patience for fools, and says what the bells have left her breath for and not a word more.
- Sanctuary is renewed by ringing at every dawn and dusk, and Sister Pell is old: that is the hinge of Book I's climax (Old Mercy, b1.5), where she is hurt and the bell falls silent until Wren climbs to ring it. Her glass in the bell tower saw the grey cloaks first.

### The red-handed woman
Appearance and voice: `cast.md` (unnamed there, as on the page).
- Pulled Darrow out of the Wend onto the far bank and made him look. See *Identities* below; the public sheet understates her (table).

---

## Not yet on the page (full entries)

### Confessor Ivo Marrant — the Hound of the Oath (Book I antagonist)
- Vane's lieutenant; the man leading the six grey cloaks and the censer on the Holloway. 40s, bald, smiling, smells of the iron censer he carries. A zealot who enjoys his work, polite to the point of menace. Never touches a weapon in front of witnesses.
- **Voice:** soft, courteous, every sentence a door he is holding open for you; uses first names uninvited; thanks people for their candour. *"Bells grow tired."* *"The Crown counts what it is owed."*
- **Wants:** Maelis (he suspects Ember work in the House and is fishing for her); Darrow as the prize that makes his name with Vane. **Plan:** read the writ at the gate, be refused by Old Mercy, camp in the lower court until the bell lapses (Ch 1 climax); Hollow Benedek to frighten the House (b1.2); work Anselm through his sister (b1.4); move before Vane arrives (b1.5).
- Gets a `saga/characters/` file when he is named or steps on the page (planned: Chapter 1 climax). Until then reader-safe files say "the Confessor who leads them".

### Brother Anselm — the almoner
- 40s, soft-spoken, beloved, keeps the stores and the letters. Always tired. Has a sister in Calden he mentions too often.
- **Voice:** apologetic and gentle, trails off mid-sentence, thanks people for things they have not done yet.
- **Wants:** Mirren safe. **Hides:** the tithe-shard came up the Steps in his letter-satchel (b1.2 → b1.4); Marrant works him through Mirren. **Flags:** `anselm_suspected`, `anselm_spared` (feeds `r.finale.return`).

### Mirren — Anselm's sister
- In Calden, in Marrant's keeping: the lever on the almoner. Present in Book I only as a letter, a lock of hair or a name said too often; never seen unless a road brings her. If she appears: thirties, quick, braver than her brother, angry at having been used.

### Ser Benedek Orrin — a knight of the Sixth
- On the cot next to Hollis. Grace-sworn, devout, kind, terrified of the Confessors and more terrified of being Faithless. Asks what "second on the list" means and watches Hollis for the answer.
- **Voice:** earnest and formal, prays half-aloud, apologises for being afraid.
- **Standing:** he knelt anew before a Confessor's field-stone at the bell-house below the Steps on the road up (the heralds' mercy, taken early), so the Crown counts him sworn: he is not on the list, the warmth he says he feels is thin and real, and he is still tithed, which is why b1.2 can take him.
- **Fate:** found Hollowed at dawn in Chapter 2 (b1.2): breathing, empty, frost on his lips, a chip of black glass under his tongue. Flag `benedek_hollowed`. Nothing of this reaches the page before then. The Chapter 1 interlude puts him on the page; his `cast.md` entry and `saga/characters/benedek-orrin.json` are written from that prose, and from nothing here.

### Ash — the hound
- A grey wolfhound bitch in the House kennels with a splinted hind leg, bad-tempered with everyone except Darrow, for no reason anyone can name. She heals alongside him. She does not fetch.
- Appears in `q1.kennel` (why the hound picked Darrow) or, failing that, at the kennels in the transition (`t1`), one paragraph. `flags.ash_met`; her bond waits in `plan.json → companions_to_come.ash` until she is on the page. Not in `saga/NOW.md`, `world.json → companions` or any reader-safe file until then.

### King Aurel the Evergreen
- Reigning for 311 years; not seen in public for nine. Present as bells, writs and the weight of the Oathspire. When Darrow is weakest he dreams of a green-lit hall and the sound of very slow breathing.
- **Hides:** T1 and T2. He is three hundred years old because the Stones feed him. Never on the page in person before Book VI.

### Elinor Vane — Aldric's sister
- The person Aldric wants kept safe, and what the Crown holds over him. A letter from her is a Book II expandable. If she appears: late twenties, Aldric's face without the severity, braver with words than he is.

### Ysra Tal, "the Needle of Calden" (Book II companion)
- Oathsworn duelist, 29, precise and cold, the finest footwork Darrow has ever seen. Sent to bring him in alive; does not understand why he will not kneel. Becomes his Finesse mentor if he earns it. As his mentor she teaches **The Liar's Shoulder**, **The Wicket Gate** and **The Shadow-Step** (Sport Arts).
- **Voice:** courteous, clipped, deadly literal. **Wants:** an order she can respect. **Fate:** defects or dies in Book III, set by earlier choices (`flags.ysra_spared`, `r.b3.ysra_fate`).

### Ilse of Corrach (Book III companion)
- Thornwild war-leader, 40s; dragged a drowning Vaelmark captain out of the Wend at Harrow Ford for reasons she has not explained. **Voice:** slow, amused, says less than she knows. **Wants:** her people through the winter; someone from the Vaelmark to have *seen*. **Knows:** T4 and T5 (the grey figures under the trees were the Hollow Tide; Harrow Ford was no battle).

---

## Identities the reader does not have yet
- **The red-handed woman** is **Ilse of Corrach**. Her `saga/characters/` file and her `cast.md` entry carry no name until Darrow learns it on the page (Book III).
- **The man leading the grey cloaks**, the one with the censer, is **Confessor Ivo Marrant**. Reader-safe files call him "the Confessor who leads them" until the page names him (planned: Chapter 1 climax).
- **The hand that wrote the list** is Aldric Vane's. Darrow believes it (Ch 1); the page has not confirmed it. Aldric's file states it as Darrow's belief, attributed as belief.
- **Ash** the hound has not appeared in the prose: no file and no mention in `saga/NOW.md` until she does.
- **Wren's mother** is Dame Elspeth Ashdown, one of the far cots. The page has the far cots and nothing about whose mother lay there.

## Bearing preferences (companions)
When a choice lands on a companion's pole and they witnessed it or learn of it, ±2 approval rides along (`saga.py add --witnessed maelis,wren`). The machine-readable copy is `saga/state/_gm/plan.json → companions.<id>.prefers`; this table is the why.

| Companion | Prefers | Why |
|---|---|---|
| Maelis | **Candor**, **Sworn** | A surgeon who lies to a patient kills him, and she has kept one vow for thirty years under a burned name; she cannot respect a man who keeps none. |
| Wren | **Guile**, **Unsworn** | The House's resident liar: a useful lie is how a girl with no rank keeps forty cots fed, and the oaths she has watched sworn are the ones that took her mother. |
| Hollis | **Mercy**, **Hearth** | He has seen enough of the beaten and knows which side of the list he is on, and he spends himself for the men he knows by name, never for a banner. |
| Rae (to come: `companions_to_come`, `--pending` until q1.cart stage 3) | **Banner**, **Candor** | A carter carries for everyone on the road or for no one: she has hauled the far cots' families and the Confessors' oxen alike, and the only lie that ever cost her anything was read from a bell-house step by a herald. The one companion who pulls against Hollis's Hearth, so that choosing her costs him. |

Later companions (Ysra, Ilse, and Ash's bond if it ever counts) get their row here and their `prefers` in `plan.json` the day they arrive (`saga.py plan companion arrive <id>`), not before. Rae's `prefers` already sit in `companions_to_come`.

## Hidden Reckonings (what the gating hides, and why the numbers are what they are)
NPC numbers are set by the GM for canon consistency; they are never derived from the real logs. Scale: Darrow at Level 4 is Might 11 · Vigor 8 · Finesse 9 · Resolve 9; the Knight Who Fell (a veteran captain at full Grace) was 15 · 15 · 18 · 12.

| Character | Fire | Level · rank | Mi · Vi · Fi · Re | Arts | Why |
|---|---|---|---|---|---|
| Maelis Vorne | ember, steady | 12 · Tempered | 9 · 10 · 12 · 17 | Mender's Patience IV, Warden's Eye IV (hidden from the public sheet until she reads the Reckoning on the page), Stillwater II | Thirty years of Warden practice (T8). High Warden's Eye = she sees Darrow's Reckoning begin before he says a word |
| Hollis Garrow | none (Grace gone, nothing kindled yet) | 2 · Bound | 13 · 7 · 5 · 10 | Seated Blade I (public sheet gets it when he teaches it on the page), Iron Grip II | Still strong in the arm; the leg and the drink have the rest. Seated Blade learned "recently and badly" |
| Wren Ashdown | ember, faint | 3 · Bound | 6 · 13 · 12 · 11 | Long Breath II; **hidden:** she can read Warden script (T6) | Runs the 1,117 Steps daily; the deeper line must not mention the script until Book III |
| Aldric Vane | grace, full (borrowed) | — · Oathsworn | 16 · 15 · 16 · 14 borrowed | none of his own | Grace-sworn: nothing of his own to count. His true Ember is near zero |
| Ivo Marrant | grace, full (borrowed) | — · Oathsworn | 12 · 12 · 11 · 15 borrowed | none of his own | Never touches a weapon in front of witnesses; the Resolve is real and the rest is the Crown's. Public sheet when he is named on the page |
| Benedek Orrin | grace, thin (borrowed) | — · Oathsworn | 9 · 6 · 8 · 11 borrowed | none of his own | Knelt anew before a field-stone below the Steps; not Faithless, so still tithed (b1.2); the public sheet shows borrowed, thin |
| Red-handed woman (Ilse) | ember, banked | 7 · Kindled (public sheet shows 4 · Bound until Book III) | 12 · 13 · 12 · 15 | Stillwater III, Iron Grip II (public sheet: Iron Grip only) | Clan war-leader who has fought the Hollow Tides for years (T4) |
| Sister Pell | ember, low | 4 · Bound | 6 · 7 · 8 · 14 | Warden's Eye II (reads lips) | Fifty years of bells |
| Rae Thorne | ember, banked, all her own | 3 · Bound | 10 · 12 · 8 · 13 | Iron Grip I (the rope), Long Breath I (the Steps) | Never knelt to a stone: nothing in her is borrowed and nothing can be taken; the public sheet is the truth, nothing hidden |
| Mother Ione | ember, steady and old | 9 · Kindled | 5 · 7 · 7 · 18 | Mender's Patience III | Iron underneath; possibly knows about Elspeth Ashdown (T6) |
| Tobin Marsh | — | fallen | — | — | Dead at the ford; the site shows a memorial line instead of a sheet |

Deeper lines (Warden's Eye IV+) in the files are written to be safe if read early; anything that would spoil stays in this table.

## Naming palette
- **Vaelmark (people, places):** Darrow, Hollis, Aldric, Elinor, Benedek, Anselm, Ione, Mirren, Edgemoor, Holloway, Calden, Coldmere, Ashby, Orrin, Marrant, Hale, Wick, Thorne.
- **Thornwild clans:** Ilse, Corrach, Haskel, Brannagh, Teague, Morna, Siv, Oddny, Ruadh.
- **Warden/old words:** ember, kindling, temper, knot, reckoning, ward, hearth, forge.
