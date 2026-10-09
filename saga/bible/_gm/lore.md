# ⚠️ GM EYES ONLY — The Annals: history and texture of the Vaelmark

> Read in sections, never whole: `python3 engine/saga.py lore` (the index), `lore <id>` (one entry), `lore grep <word>`, `lore pick saying|verse|maxim|rhyme` (a line for a glimpse). Entries are canon the Chronicle must not contradict; they are never a plan. Nothing here reaches a reader-safe file until the page has spoken it.

## doctrine — How the Annals are used

1. **The scene first.** A scene has a want, an obstacle and a turn, and it does its slot's work. Lore is seasoning. **At most one lore touch per scene**, none in the action beats of a climax, and never one that answers the scene's question for it. If a touch would slow the turn, cut the touch.
2. **The tenth.** Show a tenth and let the rest be felt: a name and a half-line, a custom done without comment, two lines of a song, an epigraph. Never a paragraph of history in the narrator's voice. Lore enters through a person (what they know and how they say it), an object, a habit, a bell, a coin.
3. **Double duty.** A touch earns its place only if it also does a second job: characterises the speaker, raises the stakes, or sets the texture of the place. A fact that only informs is cut.
4. **Received, not revealed.** The Annals hold what people believe and tell. The truths live in `arc.md` and reveal on their schedule. Where history brushes a truth, the entry gives the received version and a `⟪gm: …⟫` pointer; the pointer is never on the page and never told by `/lore`. The arc wins every conflict, and the lore is corrected to it.
5. **No new plot.** No faction with an agenda, no antagonist, no prophecy, no object of power. History, places, customs, crafts, songs, sayings, weather, beasts.
6. **Canon once written.** Fixed numbers hold everywhere: 1,117 steps · 40 cots · a Lance is sixty knights and sixty squires · twelve Lances · the Quenching three hundred years ago · Ysolde's bell four hundred and twenty years ago. New names come from the palette (`_gm/characters.md`). When the page speaks an entry, mark it (`saga.py lore spoke <id> --where chNN:sK`) and give `codex.md` its reader-safe line. `saga.py check` warns of any capitalised name in the current chapter that no registry knows (codex, cast, places, factions, the Annals).
7. **Growth.** One new entry per chapter at most, and only when a scene needs one; `/lore` adds `common` entries only, one per question. Entries run two to eight lines. The Annals stay a book of tenths.
8. **Tiers.** `common`: the kitchen knows it; `/lore` may tell it, paraphrasing around any name in `names:` the page has not spoken. `learned`: a Mender, a clerk or an elder knows it; told on the page only by someone who would know, and by `/lore` only once `spoken:` is set.

Entry shape: `## kind.id — Title`, then `- **tier:** … · **spoken:** … · **names:** …` (`names`: proper nouns the entry uses that the page may not have spoken; `—` when none), then `- **use:** …` (where it comes up without being forced), then the text. Verse goes in `>` lines, one stanza per block; sayings and maxims are `- "…" (note)` lines, which `lore pick` draws from.

---

# The ages, as the realm tells them

## age.count — The two counts of years
- **tier:** common · **spoken:** — · **names:** Aurel
- **use:** a clerk's date on a writ; Wren's ledgers; a Mender's margin.

The Crown dates everything by the Reign: this is the three hundred and eleventh year of it, and nobody in the Lowmarch finds that strange, because nobody has known another. The Menders of the Greywater keep an older count under it, the Bell-count, from the morning Ysolde's bell first rang over the valley: four hundred and twenty this autumn. A Mender writes both on a death-chit, and the Crown's clerks strike out the second.

## age.stones — The Old Stones
- **tier:** common · **spoken:** Prologue I (the standing stones at the ford) · **names:** —
- **use:** a ford, a hill-shoulder, a child's dare.

Grey standing stones at fords, on hill-shoulders, and in a ring in the marsh country east of Calden, older than any road. The Crown's chronicle says the first kings raised them; the clans say they were there before the trees; the carters say they make oxen uneasy and leave it at that. Children dare each other to lay a palm on one at dusk. Nobody knows who cut them, and the only people who ever claimed to were burned three hundred years ago. ⟪gm: Stonewright work; some are Oathstone (T1); b2.5's ring.⟫

## age.wardens — The Warden years
- **tier:** common · **spoken:** Ch 1 Sc 2 (the Emberwardens named) · **names:** —
- **use:** a nursery threat; a plastered lintel; Maelis's silence.

Before the Oathstones there was no Grace, and the realm's strength was built the slow way. The Emberwardens built most of it: a small order of knights and healers, ten years in the making each, who kept halls on high ground and wrote in a script of strokes and dots. The Crown's chronicle calls them the fire-cult and says they ate children's warmth. Lowland mothers still tell a child who won't sleep that the Warden under the stair will have him, and masons still plaster over the old lintels without asking why. ⟪gm: T7, T8; the maxims the Menders keep are theirs.⟫

## age.quenching — The Quenching
- **tier:** common · **spoken:** Prologue III, Ch 1 Sc 2 · **names:** —
- **use:** a herald's cadence; a burned-hall story; a Confessor's pride.

Three hundred years ago the king raised the Oathstones, and a thousand kneeling knights outmatched a hundred Wardens in one summer. The Crown calls it the Quenching and keeps its day as a feast; the Greywater does not. Halls were pulled down to the sills, books burned in the squares, the script made a hanging matter, and the Confessors were founded to finish the work and have been finishing it ever since. Every village got a bell-house that year, and a field-stone chapel under it, and a herald. ⟪gm: T1, T2.⟫

## age.peace — The Long Reign
- **tier:** common · **spoken:** — · **names:** Aurel, Evergreen
- **use:** a toast; a coin; a herald's formula ("in the king's unending year").

The same king has reigned since the Quenching, and the realm has three ways of saying so: the pious say he is holy, the clerks say he is well advised, and the taprooms say nothing with great care. He has not been seen outside the Oathspire in nine years. In three hundred years the Vaelmark has fought nobody but the clans, a ford-war a generation and three in the last sixty, and the Lances have become the only thing a Lowmarch boy can imagine becoming. ⟪gm: T1, T2; three hundred years old because the Stone feeds him; Book VI.⟫

## age.hollowing — The Hollowing
- **tier:** common · **spoken:** Prologue III (the far cots) · **names:** —
- **use:** a family's shame; a novice's duty; a lamp.

Within living memory the first knights came home gone behind the eyes: breathing, walking, doing what they were told, and nobody there. The heralds named it clan witchery and the name stuck. There are more every decade. Families keep them a season and then send them to a House of the Menders with a chit and a lamp, and do not visit. The far cots at Saint Ysolde's were an empty end of the hall in Maelis's first year there. ⟪gm: T4, the drained; never said before Book III.⟫

## age.now — The summer of Harrow Ford
- **tier:** common · **spoken:** Prologue I–II · **names:** —
- **use:** how the valley tells it, which is not how Darrow remembers it.

As the Lowmarch has it: at midsummer the Lances rode to the ford to stop a clan host, and in the middle of the river the Grace left the faithless among them for three heartbeats and the river took them. The heralds read it at every bell-house inside the week. The survivors who have not knelt anew are the Faithless, and their names are on lists. That the clan line was carts and children, and that the Second never got wet, are not in the telling.

# Saint Ysolde's

## house.ysolde — Ysolde of the springs
- **tier:** common · **spoken:** — (the House is named on the page; she is not) · **names:** —
- **use:** the kitchen on her feast; a lay brother's version against a Mender's.

A lowland bone-setter with a wasting sickness who had herself carried up to the hot springs to die in warm water, and did not. She hung a bell on the mountain's shoulder and rang it each dawn so the valley would know she had lived another day, and sick people started climbing toward the sound. The men who had carried her up stayed as the first lay brothers. The valley calls her a saint. The Menders do not, on the grounds that she would have hit anyone who did with the bell. Her feast is the first new moon after the first snow: bread given away, no work done that can be left, and the kitchen's book runs wild.

## house.steps — The Thousand Steps
- **tier:** common · **spoken:** Prologue II · **names:** —
- **use:** anyone climbing; Wren's count; the rule of the hundredth step.

Cut into the cliff over forty years by masons and lay brothers, switchback over switchback, from the winch-house to the gate. Everyone says a thousand. Wren has counted eleven hundred and seventeen and has made a note of everyone who disagrees. The stretches have names the lay brothers use without thinking: the Shins, the first steep run; the Elbow, the turn at the cloud line; the Long Reach; and the Last Hundred under the gate. At the hundredth step from the top there is a niche with a lamp in it, Ysolde's lamp, and the lay brothers will not go below it after dark. The sick are carried up and the dead carried down, and the Steps count everyone twice.

## house.bells — The bells of the House
- **tier:** common · **spoken:** Ch 1 Sc 1 (the dawn bell, the bell tower; the names not yet) · **names:** Old Mercy
- **use:** the hours of any scene; the bell-cant at the cage; a death on the far cots.

Three bells. **Old Mercy**, the sanctuary bell, oldest and heaviest, cracked once in the Quenching's winter and recast with the crack's bronze in it; rung at dawn and dusk while the House claims sanctuary and at no other time, and the valley knows its voice from the others. **The Hour**, Sister Pell's working bell, which tells the day. **The Small**, rung once, flat, when someone dies on the far cots, so that the House knows without being told. The winch-brothers keep a bell-cant besides, on the little bell by the cage: one for a load, two for a letter, three for a litter.

## house.law_of_bells — Sanctuary and the law of bells
- **tier:** common · **spoken:** — · **names:** Old Mercy
- **use:** Mother Ione; a Confessor's courtesy; the grey of the lower terrace.

By a right older than the Crown's chronicle, while the sanctuary bell is rung at dawn and dusk no blade may climb the Steps or pass the gate, and the Crown has honoured it for three hundred years because bells are the Crown's own law, and it cannot unmake one without loosening the rest. The law covers the Steps and the gate. The lower terrace, where the springs steam outside the gate and inside the wall, is a grey, and everyone knows it. A dawn or a dusk unrung and sanctuary lapses until the next ringing; this has happened twice in the Bell-count, both times for snow. Beside it stands the older **law of guests**: whoever comes up unarmed is warmed and fed one night, whoever sent them.

## house.order — The Menders
- **tier:** common · **spoken:** Prologue II–III · **names:** —
- **use:** who outranks whom in a corridor; a lay brother's grievance.

A Prior, Mother or Father, over the House; the Mender, who is the senior surgeon and answers to the Prior in everything but the knife; the vowed Sisters and Brothers; the lay brothers, unvowed, who carry, cook, winch, dig and bury, and run the House in every way that matters; and the novices, who feed the far cots and learn by being shouted at. The vow is four words: *to mend what climbs*. There are Houses of the Menders down the Lowmarch and in the Marches, some fallen quiet, and Saint Ysolde's is the oldest and the highest and does not let the others forget it.

## house.springs — The grey springs
- **tier:** common · **spoken:** Ch 1 Sc 1 ("the springs") · **names:** —
- **use:** steam in a cold scene; a Mender's prescription; the smell.

Hot water comes out of the mountain grey with stone-flour and stinking of sulphur, and pools on three terraces. The upper pools are for the sick and smell of boiled linen; the lower terrace lies outside the gate. The water takes the knot out of a shoulder and the colour out of cloth, and the lay brothers say it takes the lies out of a man if he sits long enough. In the first snows the terraces steam like a kitchen.

## house.hall — The infirmary hall
- **tier:** common · **spoken:** Prologue III, Ch 1 Sc 1 · **names:** —
- **use:** the geography of every scene set in it.

Forty cots in two rows under a dark roof, a fire at the gate end and a lamp at the far end that is never let go out. The near cots are the ones who will walk down; the far cots are the Hollowed, who will not, and the novices feed them and turn them. Hollis says the hall is a road with the living at one end, and he says it facing the fire. Wren's ledger counts the cots at every bell, full and empty, and the kitchen counts loaves against the number.

## house.cage — The winch-cage
- **tier:** common · **spoken:** Prologue II, Ch 1 Sc 1 · **names:** —
- **use:** anything arriving or leaving; a letter; a load that comes up light.

An iron-bound cage on a rope the thickness of a wrist, from the winch-house at the foot of the cliff to the drum at the top, worked by the winch-brothers in pairs. Up: salt, oil, flour, linen, letters, and the ones too hurt to be carried. Down: the House's letters, the effects of its dead in bundles with a tag, and the ones who can stand but not walk. It does not run after the dusk bell; a splice that let go in the dark is a story every winch-brother tells and none of them was there for. Everything that comes up is weighed, and Wren writes it down.

## house.undercroft — The undercroft
- **tier:** learned · **spoken:** — · **names:** —
- **use:** a cold draught; the key at the Prior's belt; what the lay brothers will not do.

Under the hall there is older stone than the House: a vaulted undercroft the masons found when they cut the foundations, and built on rather than through. It is kept locked with a key the Prior wears, the lay brothers do not go down, and the flagstones above it are the coldest in the hall. ⟪gm: a Warden hall; b1.3, q1.door. Say nothing of what is in it.⟫

## house.kitchen — The kitchen and its book
- **tier:** common · **spoken:** Ch 1 Sc 1 (the kitchen) · **names:** —
- **use:** anything overheard; a wager; bread.

The kitchen hears everything first, because everything passes its door on the way to the hall, and it keeps a book on anything the House can see from a window: how long a snow will hold, whether a knight will walk, which way a cart will turn at the Elbow. Stakes are bread and chores. It counts loaves the way Wren counts cots, and the two counts are compared at the dusk bell and argued over. Bitterleaf grows on the south terrace; surgeons chew it or smoke it to keep their hands steady, and a few only hold it in their teeth.

## house.kennel — The kennels
- **tier:** common · **spoken:** — · **names:** —
- **use:** dogs on the Steps in snow; the kennel-master's temper.

Below the cloister, reached by a ramp and not a stair, so that a dog with a bad leg can be got up it: lymers for finding people in snow on the Steps, two House hounds that are nobody's, and whatever strays climb. The kennel-master feeds them on what the kitchen won't admit to, and holds that the Menders waste good meat on bad knights.

# The realm

## realm.name — The Vaelmark and its tongue
- **tier:** common · **spoken:** Prologue I ("rough Vaelish") · **names:** Saltreach, Marches
- **use:** a stranger's accent; a map; a clerk's pedantry.

The mark of the Vael, the lowland people who came up the river valleys with oxen and bells before anyone wrote anything down. Vaelish is the tongue of the Lowmarch and the court; the Greywater speaks it slower and the fog coast faster. The realm's parts, as a child recites them: the Lowmarch, which is grain, mills, levies and the Holloway; the Marches, hill country toward the coast, sheep and quarries; the Greywater, the peaks and the Houses; the coast, fog, salt and smugglers; and beyond the Wend the Thornwild, which is not the realm's and knows it.

## realm.calden — Calden and the Spire
- **tier:** common · **spoken:** Prologue II, Ch 1 · **names:** First Stone
- **use:** a herald's pride; what every knight remembers of being sworn.

White stone on a white rock above the river road, and a hundred bells that ring the hours in a peal that rolls from the gate to the Spire and back. At its centre the Oathspire, black glass and iron, raised in the Quenching's year; the First Stone sits at the top of it, and every Oathstone in the realm answers to the First. Knights are sworn there once, climbing the Spire's stair on their knees, and most of them are glad never to see it again.

## realm.lances — The Lances
- **tier:** common · **spoken:** Prologue I · **names:** —
- **use:** precedence; signals; a captain's habits.

Twelve by the old count, each sixty knights and sixty squires, numbered by precedence of founding. The First is the king's own and never leaves Calden. The Second is the oldest that rides, and knows it. The Sixth and the Ninth are Lowmarch lances, raised from farm sons and horse-breeders, and the Ninth has been "the fast one" for longer than anyone can say why. A lance's field-stone travels with it on a cart. The signals are the raised fist, ready; the fist with two fingers out, hold; and the open hand swept outward, ride wide, which means give the flank room. No captain has ever liked giving the second.

## realm.oath — The Oath of the Bended Knee
- **tier:** common · **spoken:** Prologue I (the knighting; the field-stones) · **names:** —
- **use:** Benedek at every bell; a herald's demand; what Darrow can no longer do.

Sworn kneeling on the left knee with both palms flat on an Oathstone: at knighting, before every battle at the lance's field-stone, and whenever the Crown bids. The words are short enough for a frightened boy: *Stone and Crown, knee and hand. What I am given I hold. What I hold I give.* The Grace comes up through the palms as warmth and settles in the chest, and old knights call it the Crown's hand on your back. A knight who cannot kneel cannot be sworn, which is why "stiff-kneed" is an insult. ⟪gm: the third line is a tithe-oath in truth (T1). Never gloss it.⟫

## realm.grace_talk — What is said of the Grace
- **tier:** common · **spoken:** Prologue I, Ch 1 Between · **names:** —
- **use:** barracks talk; a squire's questions; a superstition.

That it is warm. That it makes a horse run on your legs. That a lance full of it can cross a river in flood laughing. That it is thinnest when you have not knelt in a season and thickest the morning after a field-stone. That frost on a sworn man's mail is the worst omen there is, and nobody will say why. That no one who has it has ever seen the script the Wardens were burned for. The Menders say only what Maelis says: it holds things up. ⟪gm: T1, T7.⟫

## realm.confessors — The Confessors
- **tier:** common · **spoken:** Ch 1 Sc 1 · **names:** —
- **use:** how the valley fears them; a writ at a gate.

Founded in the Quenching to hunt what was left of the Wardens and never disbanded: now the order that keeps the realm's oaths. Grey cloaks, a censer of iron on a chain whose smoke they call the Crown's breath, writs under seal, and a list. They read names at bell-houses and never draw steel before witnesses; the law is the blade, they say, and they have the law. A Knight-Confessor commands them from Calden. The Lowmarch fears them more than it fears the clans, and will not say so where the smoke can hear.

## realm.heralds — Heralds and bell-houses
- **tier:** common · **spoken:** Prologue II · **names:** —
- **use:** how news moves; a proclamation's cadence.

Every village has a bell-house with a field-stone chapel under it and a herald who keeps both. Proclamations are cried from its steps after the noon bell, and a thing cried at the bell is law in that village by dusk. News goes down the Holloway at the pace of a herald's horse and up it at the pace of a cart, which is why the mountain is always a day behind and a day wiser. A man named at the bell may answer at the bell, and some have.

## realm.levies — The Lowmarch levies
- **tier:** common · **spoken:** — · **names:** —
- **use:** boys with billhooks; a sergeant's voice; the levy's verse.

When the bell-house rings the long peal, every mill and farm sends a man or a boy with a billhook, a sergeant counts them on the green, and they walk to wherever the Lances need bodies to hold a line the Lances have already won. They sing on the road, which is how you know a levy is coming before you see it.

> Billhook, billhook, who d'you serve?
> The bell that rang and the man with the nerve.
> Billhook, billhook, where's your pay?
> Home by harvest, or not, they say.

## realm.coin — Coin
- **tier:** common · **spoken:** — · **names:** —
- **use:** a wager; a bribe; an insult.

Copper **wicks**, small and thin, a dozen to a loaf; silver **marks**, stamped with the river; gold **spires**, stamped with the Spire, which a Lowmarch farmer may see twice in his life. "Not worth a wick" is the bottom of the scale and "a spire for your horse" is a compliment. Wagers in the House are in wicks and chores, and the kitchen's book will take a chore before a wick.

## realm.holloway — The Holloway
- **tier:** common · **spoken:** Prologue II, Ch 1 · **names:** —
- **use:** any journey; a carter's bell; the milestones.

The old road north from Calden to the Greywater landing, worn by three hundred years of carts until it runs below the fields between banks, hollow as its name. Milestones every mile, numbered from Calden, and every carter knows the road by them: "past the second milestone" means a thing and "short of the twelfth" means another. Salt and oil go up it from the coast and letters come down. A Holloway carter wears an ox-bell at the belt so a cart in fog is heard before it is hit, and a carter without a bell is a thief until proved otherwise.

## realm.coldmere — Coldmere
- **tier:** common · **spoken:** Ch 1 Sc 1 · **names:** —
- **use:** the last warmth before the climb; news; a fair.

The last village below the mountain, on a tarn that never warms: an inn whose taproom hears everything the Holloway carries, a bell-house, a mill on the outflow, and a horse-fair in autumn that the Lowmarch rides to. Carts for the House stop there last, and the House's dead stop there first. Half the lay brothers were born within a mile of its bell.

## realm.edgemoor — Edgemoor and its greys
- **tier:** common · **spoken:** Prologue I (Darrow of Edgemoor; the grey mare) · **names:** —
- **use:** Darrow's childhood; a horse's quality; a saying.

Hill country west of the Lowmarch where the grass is thin and the horses are not: the Edgemoor grey, long-legged and sure on a slope, is the mount the Lances buy, and each lance brands its own. A horse-breeder's son from Edgemoor learns to ride before he can argue and to walk at a horse's head before that. Lowmarch saying: an Edgemoor horse and an Edgemoor man both go better uphill, and neither will tell you why they came down.

## realm.wend — The Wend
- **tier:** common · **spoken:** Prologue I · **names:** —
- **use:** any crossing; cold; the border.

Cold, fast and brown in rain, running east out of the Greywater through the Lowmarch to the border and on into country the realm does not map. Its fords are the realm's doors: Harrow Ford is the broadest, with the Old Stones on both banks. Barges work the lower reaches to the landing. "Wend-cold" is the lowland word for anything terrible, and a Wend wedding is one where the bride has crossed from the other bank. The clans are on the far side and have been as long as the river.

## realm.hollowed — The Hollowed, as the valley has them
- **tier:** common · **spoken:** Prologue III, Ch 1 Sc 1 · **names:** —
- **use:** how people speak of the far cots; the lamps; a herald's line.

Knights who came home with the Grace gone and themselves gone after it: breathing, obeying, nobody in. The heralds say the clans do it with witchery out of the grey country east of the Wend, and that a lamp keeps it off, which is why the Lowmarch burns lamps in autumn and the clans are said to burn them all year. Families send theirs to the Menders with a chit and do not come back for the lamp. ⟪gm: T4.⟫

## realm.writs — Writs and seals
- **tier:** common · **spoken:** Prologue I, Ch 1 Interlude · **names:** —
- **use:** a paper that is law; how a soldier carries one.

A writ is the Crown's voice on paper under a seal, and whoever holds it holds that much of the Crown. A soldier breaks the wax with his thumb, reads the words, and keeps the paper folded small against his skin, wax inward, until the thing it ordered is done; a writ carried wax outward is a writ you mean to show someone. Seals are matched by clerks, not soldiers, and most knights could not tell you whose seal they broke.

# The Thornwild

## folk.clans — The clans
- **tier:** common · **spoken:** Prologue I · **names:** Corrach, Haskel, Nine Rivers, Morna, Teague
- **use:** a Lowmarch slur; a clan custom done plainly.

Named for rivers and holdfasts and called by given name and clan, Morna of this and Teague of that. Boar spears and long knives; carts and dogs; a lamp at every door; no kneeling to anything. They raid across the fords when the lowland granaries are full and the Lowmarch calls it a war. What the Lowmarch knows of them is red hands, witch-light and the ford-songs, and what the clans know of the Lowmarch is the Lances. ⟪gm: the red hands are those who have stood at the water against the Tide (T4). Clans: Corrach, Haskel, the Nine Rivers. The red-handed woman is unnamed until b3.2.⟫

## folk.words — A few clan words
- **tier:** learned · **spoken:** — · **names:** —
- **use:** a carter's grandmother's words; a parley; a greeting done right.

What a Lowmarch carter's grandmother might have kept: *brann*, the hearth-fire, and so a household; *corr*, the heron, and so a watcher; *tal*, a gift laid down before a request, without which the request is an insult; *greth*, the grey country east of the river; *haud*, hold, said with the open palm and never the fist; *ruadh*, red; and a name for the river that is not Wend and that they do not give to lowlanders. ⟪gm: Rae's grandmother; b3.1, a gift before the ask. Keep to these.⟫

## folk.lamps — Lamps at every door
- **tier:** common · **spoken:** — · **names:** —
- **use:** witch-light seen from a ford; the Lowmarch's borrowing.

Every clan door burns a lamp from dusk to dawn, all year, and the Lowmarch calls it witch-light and borrows it every autumn without noticing. The clans say a lamp is a door's way of saying someone is home. ⟪gm: against the Hollowed (T4).⟫

# Songs, rhymes and sayings

## rhyme.counting — The Lowmarch counting rhyme
- **tier:** common · **spoken:** Prologue (epigraph, first stanza) · **names:** —
- **use:** children at a gate; an epigraph; a sum that will not come out.

A clapping rhyme for two, the sums never matching because the lances come home fewer, which children do not notice and their mothers do. ⟪gm: Book V adds a last verse about a knight who would not kneel (q5.rhyme); do not write it before.⟫

> Count the lances on the west bank, child,
> count them, one through nine.
> Count them going, count them coming home,
> and never get the same sum twice.

> Count the bells in the bell-house, child,
> count them, dawn to dark.
> Count the one that rings for the river,
> and that one leaves no mark.

> Count your fingers, count your knees,
> count the knight who stands.
> One knee down and one knee up,
> and that's the count of hands.

## song.greymare — The Grey Mare of Edgemoor
- **tier:** common · **spoken:** — · **names:** —
- **use:** a road song; a thing hummed in an inn; what the Ninth sang on the march.

The Lowmarch's road song, three verses everybody knows and nine nobody agrees on. The Ninth sang it on every march, and one of them sang it worse than the rest and more often. ⟪gm: Tobin's song; his mother hums it (q5.tobin); the nineteen know it. The Sixth's is song.sixth.⟫

> Oh the grey mare of Edgemoor, she carried me far,
> by the Wend and the Holloway, by the bell and the star,
> and she never once asked me the why or the where,
> for a grey mare of Edgemoor goes anywhere.

> Oh the grey mare of Edgemoor, she carried me home,
> by the mill and the ford and the long white road,
> and she stood at the gate while they counted us in,
> and she counted us back with a toss of her chin.

## song.sixth — Sixty and a Mule
- **tier:** common · **spoken:** — · **names:** —
- **use:** Hollis in his cups; a lance marching out; a joke on the Sixth.

The Sixth's marching song, which has more verses than the Sixth has men and gets worse as it goes. ⟪gm: b4.4, the Sixth "singing badly".⟫

> Sixty men and a mule went down to the river,
> sixty men and a mule, and the mule was the giver,
> for the mule had the sense that the captain had not,
> and the mule's at the inn and the captain is shot.

> Sixty men and a mule came home from the river,
> fifty-nine and a mule, and the mule still the giver,
> for the one that was lost had his pay in his hat,
> and the mule's got the hat, and we'll leave it at that.

## song.lullaby — The far-cot lullaby
- **tier:** common · **spoken:** — · **names:** —
- **use:** a novice at the far end at night; a Greywater mother.

Sung low over the far cots by novices who were sung it in the valley, to the tune of the Hour.

> Hush, the bell is counting,
> one for you and one for me,
> hush, the snow is mounting
> on the Steps and on the sea.

> Sleep till the Small bell wakes you,
> sleep till the lamp burns low,
> hush, the mountain takes you,
> and the mountain lets you go.

## song.menders — The dusk verse
- **tier:** common · **spoken:** — · **names:** Old Mercy
- **use:** the dusk ringing; a thing Wren says instead of praying.

Said, not sung, by whoever rings the sanctuary bell at dusk, one line to each stroke.

> Day's done and the door's shut,
> the blade stays below.
> What climbed, we keep,
> and the bell says so.

## rhyme.knucklebones — Knucklebones
- **tier:** common · **spoken:** — · **names:** —
- **use:** a Between with Hollis; a lay brothers' game; stakes in wicks.

Five sheep's knuckles. Throw one up, sweep the rest, catch the one: ones, twos, threes, fours, then "the stone", all five swept and the thrown bone caught on the back of the hand. A miss passes the bones. Stakes are wicks, chores, or a story told true. The rhyme is chanted by whoever is losing.

> One for the stone and two for the crown,
> three for the knight who won't come down,
> four for the bell and five for the hand,
> and the bones go to him who can stand.

## saying.steps — Sayings of the Steps
- **tier:** common · **spoken:** glimpse (the mountain keeps its own count) · **names:** —
- **use:** lay brothers climbing; a glimpse; a shrug.

- "The mountain keeps its own count." (said when the wind gets under a cloak; nobody can say what it means and everybody says it)
- "Up is a prayer, down is a bill." (the lay brothers, of carrying)
- "Nobody's carried up twice." (a kindness or a threat, depending on the brother)
- "Past the hundredth after dark, you're on your own." (the lamp niche; said to novices)
- "Count the Steps and the Steps count you." (Wren hates it)
- "Ysolde climbed it dying. What's your excuse?" (to anyone who stops at the Elbow)

## saying.lowmarch — Lowmarch proverbs
- **tier:** common · **spoken:** Prologue (Wend-cold; kneel to that) · **names:** —
- **use:** farmers, carters, innkeepers; a glimpse.

- "Wend-cold." (terrible; the river's cold is the measure of all cold)
- "Bells take it." (an oath: may the bells carry it off)
- "Kneel to that." (agreement; ironic among the Faithless since the ford)
- "A writ is warm for a day." (the law cools as it travels)
- "Salt goes up and letters come down." (carters, of the Holloway; also of bad news)
- "Three days' rain and the ford's a king." (the Wend decides who crosses)
- "Grace-fed." (of a horse or a man carried by something not his own; an insult in Edgemoor)
- "Road's the road." (a carter's shrug: it is what it is ⟪gm: Rae's saying; spoken when she says it⟫)

## saying.soldiers — Lancers' talk
- **tier:** common · **spoken:** Prologue I (ride wide; Stone and Crown) · **names:** —
- **use:** Hollis and Darrow; barracks shorthand.

- "Ride wide." (give the flank room; also: be careful, which no lancer would say plainly)
- "Stone and Crown." (the oath's first words, used as a curse and a vow both)
- "Two fingers." (hold; also of a captain who holds too much)
- "Stiff-kneed." (proud; treasonous; unable to kneel; all three at once)
- "Counting the west bank." (brooding on the dead)
- "Full of Grace and empty of sense." (of a young knight; the Sixth's whole opinion of the Second)

## maxim.menders — The Menders' maxims
- **tier:** common · **spoken:** Prologue III, Ch 1 Sc 1 · **names:** —
- **use:** Maelis; a novice reciting; a line cut into the hall's lintel.

- "Time makes it possible. Proof makes it permitted." (the first thing a novice learns and the last thing a Mender says; its origin is not asked ⟪gm: Warden⟫)
- "You don't bind a river in flood." (swelling first, then the work)
- "Strength before the binding." (bring a weak leg and get a weak knee)
- "Mend what climbs." (the vow)
- "Wrong question." (Maelis's own: what the patient feels is not what the leg did)
- "A Mender who lies to a patient buries him." (why they offer no comfort they cannot back)
- "The quiet is a liar." (Maelis, of the soft season)

## saying.kitchen — Kitchen talk
- **tier:** common · **spoken:** glimpse (somebody's colour) · **names:** —
- **use:** the passage by the kitchen door; a line overheard.

- "He's got somebody's colour." (of a sick man looking better than he should)
- "Loaves don't lie." (the kitchen's count against Wren's)
- "Feed the far end first." (the novices' rule; also: do the hard thing before breakfast)
- "If the Mender's smiling, somebody's dying." (unfair, and said daily)

# Crafts, seasons and weather

## craft.menders — What the valley knows of the Menders' craft
- **tier:** common · **spoken:** Prologue III · **names:** —
- **use:** why people climb; what they expect; what they do not know.

Bone-setting, boiled linen, splints of beech and leather, the springs, bitterleaf for pain and for steady hands, and patience, which is the one the valley complains of. The Lowmarch knows that Saint Ysolde's mends what the lowland surgeons send away and does not ask how, which suits the Menders. ⟪gm: the Binding and emberthread are Warden art (T8); the valley has never heard the word.⟫

## craft.carting — Carting
- **tier:** common · **spoken:** Prologue II · **names:** —
- **use:** a carter at work; a manifest; the road's law.

Oxen on the Holloway, because a mule will not stand at the winch-house and an ox will stand all winter. A cart carries a manifest, and the manifest is law at every bell-house, which is why a good carter can read one upside down and a great one can write one that says what she needs it to. The road's law: a cart with a bell has the right of way, a cart without one has a story to tell, and nobody passes a cart on the Elbow.

## craft.script — The forbidden script
- **tier:** learned · **spoken:** Ch 1 Sc 1 (the Reckoning's script) · **names:** —
- **use:** a plastered lintel; a mason's habit; a child's warning.

Strokes and dots, angular, cut into old lintels and door-frames all over the Greywater and plastered over by every mason since the Quenching. To read it is a hanging matter in the chronicle and a joke in the Lowmarch, since no one living can. Children are told it burns the eyes. ⟪gm: Warden script; Wren can read it (T6).⟫

## calendar.year — The turning of the year
- **tier:** common · **spoken:** Prologue I (midsummer), Ch 1 Sc 1 (first snow) · **names:** —
- **use:** dating a scene without a date; a feast as a slot's texture.

The realm's season is the real season. Midsummer, when the Lances ride and the fords are low. Harvest, when the levies are let home. **First Snow on the Steps**, which the House marks by moving the far cots nearer the fire. **Ysolde's feast**, the first new moon after that snow. **The Night of Lamps** in late autumn, when the Lowmarch sets a lamp at every door for its Hollowed and the House sets one lamp per far cot down the Steps at dusk, as far as the hundredth step and no further. **Midwinter**, the longest night, when Calden's hundred bells ring till dawn and the mountain rings its dusk bell twice. Then the thaw, and the fords are kings again.

## beast.greywater — Weather and beasts of the Greywater
- **tier:** common · **spoken:** Prologue II, Ch 1 Sc 1 · **names:** —
- **use:** any outdoor scene; the sound of the place.

The wind comes round the mountain's shoulder with a knife in it from the first snow to the thaw, and the valley fills with cloud until noon. Ravens keep the Steps and know the bell-cant better than the novices. Goats on the terraces, lymers in the kennel, and in the hardest winters a mountain cat that takes a goat and is blamed for everything else. Snow comes early and stays late, and the Steps are swept by whoever Mother Ione is displeased with.
