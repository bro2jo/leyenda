# The tales — the past, a piece at a time (GM only)

*What this file is.* The tales are the saga's side narrative: the past of Darrow, of Rae, and of the people around them, told in pieces and paid for by the works (`real/projects.json`; `darrow.py project`). Each task he reports done owes one piece; the last piece of a tale leaves a keepsake on someone's page. The rules are `design.md` §12. This file holds the plans: one `## tale.<id> — Title` per tale, its fields on one line (`of`: whose past, a character id · `when`: the opening line, reader-safe, which goes on the page the day the tale is bound · `pieces`: how many · `keepsake`: what the last piece leaves and to whom, when the project finished in its week · `keepsake_late`: the lesser keepsake, smaller and plainer, when the project finished after its due day (`real/projects.json → due`, the Saturday of the week it was first planned; the brief says which applies, the engine marks the record) · `plants`: what it may set down for the present, threads by number (`thread 4`) and the Annals as `lore:<id>` · `never`: what it must not say), a paragraph on what the tale is, then `### piece K — Title` with each piece's want, turn and last image. `saga.py tale bind <project>` takes the first unbound plan with a piece per task (or `--tale`); `saga.py brief --tale` prints the piece owed, and the plan may be edited until that piece is written. A plan's pieces may be re-cut to fit a project (a piece per task); a piece told stays told.

**Rules of the past.** A tale never reveals a truth (T1–T8, `arc.md`) ahead of its schedule; it may plant, and the plant counts like any other (two on the page before a reveal). It never contradicts a known fact on a person's page, and never makes the present cheaper: nothing of the House, no future, no foreshadowing said aloud; the reader may feel the echo, the prose never points at it. Close third on its own person, past tense, a whole small story in every piece. Names: the page's, the plan's, or none; a new person needs a base file first; a place not in `places.json` is described, not named. The pieces should alternate, over the months, between Darrow's past and Rae's: the plans say whose each is.

---

## tale.quickstep — Quickstep
- **of:** darrow · **when:** Edgemoor and the Lowmarch, in the years before the Ninth was his · **pieces:** 3 · **keepsake:** the name Quickstep, to darrow: the name the Ninth gave him for the feet, said down the whole line and answered to, spoken on the page for the first time in this tale and not heard since the river · **keepsake_late:** a name said once, to darrow: the word said by one man in a yard, which he pretended not to hear and which did not follow him out of it; what the Ninth came to call him stays untold
- **plants:** thread 15 (the grey: how a grey came to him, and her name for what she stood in; nothing of her after the Wend) · thread 11 (the Ninth sang on every march, and one sang worst) · lore:realm.edgemoor · lore:realm.lances
- **never:** what the Grace is or where it comes from (T1, T7); anything of Aldric's seal or foreknowledge (T2, T3); anything that explains Harrow Ford; the grey after the river

How a horse-breeder's son from the Edgemoor hills got the fastest feet in the Lowmarch and the name that went with them, given by the men he would later count back. The feet are the point: every piece shows him moving the way the present cannot, without once saying so. The tale ends on the name, and the reader hears the knee in it.

### piece 1 — The Breeder's Son
A boy of ten or twelve at his father's paddock, walking at a horse's head before he can argue (lore:realm.edgemoor); the greys that go better uphill; the one thing he can do that the older boys cannot: get out of the way of a horse that means him harm, on his feet, in the mud. Want: to be let on the horse nobody can sit. Turn: he gets on it by not being where it expects him. Last image: his father saying nothing and opening the gate for him. A grey mare is in the far field, the one he will ride off the hill.

### piece 2 — The Grey
The day he rides the grey mare off the hill to the Lowmarch muster, a boy of sixteen or so with his father's brand on her quarter. Want: to go. Turn: a lance's sergeant watches him lead the mare through a line of levy boys and billhooks without touching one, and asks whose son he is, and he says his own. Last image: the two of them on the Holloway at dusk, his hand at her head. Plant: a lance buys Edgemoor greys and brands its own (lore:realm.lances); a grey filly out of this mare, standing in the thistles at the edge of the far field to be left alone, whom he has already named for it (the page has her name; nothing of where she goes).

### piece 3 — The Name
Years on: a new knight of the Ninth, not yet its captain, in a yard at a fair or a practice ring, turning a bigger man before the man knows he has been turned; the Ninth watching; the youngest of them then (unnamed; Tobin is not yet in the Ninth) says the word first, and the sergeant makes it stick. Want: to be seen. Turn: the name is given by the men, never asked for; he pretends to hate it and does not. Last image: the name said down the line as they ride out, and him answering to it. Keepsake: *Quickstep*. The piece ends on the name. Late: the word is said once, by one man, in the yard, and nobody takes it up; he rides out with the Ninth and no name.

## tale.thorne_road — Road's the Road
- **of:** rae-thorne · **when:** The Holloway, when Rae Thorne was small enough to ride the box · **pieces:** 3 · **keepsake:** the ox-bell at her belt, to rae-thorne: her grandmother's bell, which the page has heard ring at the foot of the Steps without saying whose it was · **keepsake_late:** the word for stand, to rae-thorne: one clan word of her grandmother's, kept for the oxen; the bell's story stays untold
- **plants:** thread 4 (her grandmother's stories of what walks out of the grey country east of the Wend, told to frighten a child, and not believed) · thread 14 (Rae on the page: what the road made of her) · lore:craft.carting · lore:realm.holloway · lore:realm.coldmere
- **never:** her father and the winch-cage; the forty-one bundles; the grey mare and the fair; the Market and any crate; the debt on the cart; the truth of the clans or the grey country (T4, T5); her grandmother's clan beyond "Thornwild-born, come over the Wend with a drover"

Rae as a girl on the box of her grandmother's cart: how the road's law got into her, how the name wore smooth, where the bell came from. The grandmother is the voice: a few clan words for the oxen, a story at every milestone, and the rule for the Elbow. Nothing of the House, nothing of knights but one who tries to pass on the Elbow and learns. Close third on the girl; the grandmother stays unnamed on the page unless a piece needs her name (then a base file first).

### piece 1 — The Elbow
Want: to drive. The grandmother lets her hold the lines on the straight and takes them back at the Elbow, where nobody passes a cart (lore:craft.carting). A rider in a lance's colours tries; the grandmother does not move the cart an inch, and tells the girl why with the one saying: road's the road. Turn: the girl understands that the road has a law and the law is the bell. Last image: the rider waiting behind them all the way down, and the girl not looking back.

### piece 2 — The Bell-House
Coldmere's bell-house (lore:realm.coldmere); the manifest read right way up by the clerk and upside down by the grandmother, who cannot write and reads a manifest better than he does; the inn hearing everything; the girl learning the Thornwild word for stand, and that Coldmere calls the family "the Thornwild woman's" and the words are wearing down. Want: to be from somewhere. Turn: she decides the worn-down name is hers. Last image: the oxen standing to the clan word, and the clerk pretending not to have heard it. Plant: the grey country east of the Wend in one of the grandmother's stories, told to frighten, and not believed.

### piece 3 — A Carter Without a Bell
The grandmother's last run, or the day she hands over the lines for good; the bell comes off her belt and onto the girl's: a carter without a bell is a thief until proved otherwise (lore:realm.holloway). Want: to not take it yet. Turn: she takes it, because the road is the road. Last image: the bell ringing on the first jolt, and the girl not hearing it. Keepsake: the ox-bell. The piece ends on it. Late: the grandmother keeps the bell this once more, and gives the girl the word for stand instead; the bell's own day is not this one.

## tale.two_boys — Two Boys Holding Horses
- **of:** darrow · **when:** Calden, in the years when he and Aldric Vane held other men's horses · **pieces:** 3 · **keepsake:** the open hand, to darrow: the lance signal for ride wide, which Aldric Vane showed him first as a boy and said to him last at the ford · **keepsake_late:** a wager unpaid, to darrow: the copper from the race Aldric Vane would not win, never paid and never asked for
- **plants:** thread 1 (Aldric's "ride wide" and the open hand, as a boy's lesson; nothing of a heartbeat early) · lore:realm.lances · lore:realm.calden · lore:realm.oath
- **never:** Aldric's foreknowledge or his seal (T2, T3); what the Oath takes (T1); Aldric's sister by name; any judgment of Aldric the page has not earned: he is loving here, and he believes

How Darrow of Edgemoor and Aldric Vane came to be knee to knee: two squires of different fathers holding horses in Calden's yards, one with the better seat and the better manners, one with the feet; what each could do that the other could not; the morning they were knighted side by side in a cold chapel with their palms on the same warming stone. The present stays in the reader's mind and out of the prose. Aldric must be likeable here: the tale is what Darrow lost.

### piece 1 — Other Men's Horses
Two boys of fourteen holding horses at a muster in Calden's yards, assigned to a knight apiece; a horse bolts, Darrow stops it on foot, Aldric stops the knight's temper with manners; each sees what the other has. Want: to be noticed by the knights. Turn: they notice each other instead. Last image: Aldric showing him the open hand swept outward, the signal he learned from his father's lance, and what it means: give the flank room (lore:realm.lances).

### piece 2 — The Better Seat
A ride or a race in the river country: Aldric's seat against Darrow's feet; a wager; a fall that could be either's and is Darrow's, and Aldric, who could have won, pulling up. Want: to beat him. Turn: Darrow learns Aldric will not win a thing that way, and trusts him for it. Last image: the two of them walking the horses back knee to knee, and one word between them that the page does not give.

### piece 3 — The Cold Chapel
The morning of the knighting: the stair climbed on the knees (lore:realm.calden), the cold chapel, the Oathstone warming under their palms, the short words (lore:realm.oath, received as a frightened boy receives them, never glossed), Aldric's shoulder against his. Want: to be sworn. Turn: Darrow feels the warmth come up through his hands and does not ask where it comes from; Aldric, beside him, kneels correctly and watches that Darrow does too. Last image: outside, Aldric's open hand swept outward across the morning: ride wide. Keepsake: the open hand. The piece ends on it. Late: Aldric reminds him of the copper from the race, laughing, and does not take it; the hand stays at his side.

## tale.ninth_road — The Ninth on the Road
- **of:** darrow · **when:** The Holloway, the summer before the river · **pieces:** 4 · **keepsake:** Tobin's verse, to darrow: the verse of the Grey Mare that nobody agrees on, as Tobin Marsh sang it, badly, the whole length of the Holloway · **keepsake_late:** two lines of Tobin's verse, to darrow: the two lines he can still hear; the rest went down the road with the singer
- **plants:** thread 11 (Tobin: nineteen, the gap in his teeth, the singing) · thread 13 (Hollis of the Sixth: the insult that is instruction; nothing of a chair) · lore:song.greymare · lore:realm.levies · lore:realm.holloway · lore:realm.lances
- **never:** the ford, the writ, the clans (T5); the Grace as anything but warmth; Hollis's leg; Tobin's death said or foreshadowed; Rae; Aldric's seal

The Ninth on a summer march up the Holloway to hold a line the Lances had already won: the levies' song coming up the road before the levy, Tobin singing the Grey Mare worse than anyone and more often, the Sixth sharing the road and Hollis Garrow sharing his opinion of the Ninth, a captain's habits (the signals; the fist with two fingers out he hated to give). Four small days of a lance that was whole. The reader knows what the prose never says.

### piece 1 — The Long Peal
The bell-house rings the long peal (lore:realm.levies); the Ninth rides out of the Lowmarch muster; Darrow's first morning as its captain in the field; the signals. Want: to not have to give the hold signal. Turn: he gives it, once, and the Ninth stops dead, and he hates how well it works. Last image: the levy singing up the road before anyone sees it.

### piece 2 — The Worst Singer in the Lowmarch
Tobin Marsh, newest and youngest, singing the Grey Mare off the key the whole road (lore:song.greymare); the Ninth trying to stop him and failing; the gap in his teeth; Darrow deciding not to stop him. Want: quiet. Turn: Darrow learns the lance sings better with the worst singer in it. Last image: sixty men on the verse nobody agrees on, every one of them wrong.

### piece 3 — The Sixth Shares the Road
The Sixth comes up behind them at a milestone (lore:realm.holloway); Hollis Garrow, two legs and a full voice, on the Ninth, on fast lances, on horse-breeders' sons; the first insult, which is the first lesson. Want: to answer back. Turn: Darrow answers with the feet, in a yard at an inn, and Hollis buys the drink and does not say he was wrong. Last image: Hollis's "Captain", said for the first time, to mock him.

### piece 4 — The Line Already Won
The line they were sent to hold, already won when they arrive; the levy boys with billhooks going home by harvest; the Ninth turning for home singing; Tobin's verse, the one he made up, the only verse the Ninth ever agreed on, because it was his. Want: to have done something. Turn: Darrow learns that a lance that comes home whole has done the thing. Last image: Tobin's verse, given in full on the page (original lines, in the Grey Mare's metre), and Darrow riding at the head not singing and knowing every word. Keepsake: Tobin's verse. The piece ends on it. Late: the wind takes most of it; two lines reach the head of the column, and those are the two the page gives.

## tale.hollis_table — Knucklebones
- **of:** darrow · **when:** An inn on the Holloway, some years before the Steps · **pieces:** 2 · **keepsake:** a story told true, to darrow: the stake the Sixth plays knucklebones for, which Hollis Garrow taught him across a table and the page has seen him pay since · **keepsake_late:** the stone on the back of the hand, to darrow: the catch Hollis Garrow showed him, a trick and not a stake
- **plants:** thread 13 (Hollis: the insult as affection; the kind lie to the weak, never to the strong) · lore:realm.coldmere
- **never:** Hollis's leg, his drink as a wound, the writ, the chair; anything of the ford

The first game of knucklebones between Hollis Garrow and Darrow: how the Sixth's stake works (no coin; a story told true, and the table decides whether it was), the stone caught on the back of the hand, and the first true story each told the other, which the page gives in full. Two pieces: the game, and the paying.

### piece 1 — The Stake
Want: to win an old captain's respect at a table. Turn: he wins the game and learns the stake was never the game. Last image: Hollis saying "pay, then," and the table going quiet.

### piece 2 — Paid
The story Darrow tells true (something from Edgemoor; never the grey's fate), and Hollis's in return, told true, which the table did not expect of him; someone at the table tells Darrow afterwards that Hollis lies kindly to the weak and never to the strong, and Darrow understands what Hollis has just decided he is. Want: to know whether Hollis lied. Turn: he learns the old captain's one rule, and that it was applied to him. Last image: the stake named as the Sixth names it. Keepsake: a story told true. The piece ends on it. Late: Hollis pays in a trick instead of a story, the stone on the back of the hand, and the stake's name waits for another table.
