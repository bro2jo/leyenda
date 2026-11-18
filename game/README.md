# The Line and the Hand

A side game. Darrow and the company move on a small map; each fight is played as a hand of cards. Three battles make a run.

**It is not the Chronicle.** Nothing here is canon, nothing here reads `real/`, and nothing here writes to `saga/`. The foes are a hired road company made up for the game. A run lends cards and ends: an Art, a rank or a point of Might only ever comes from the Ledger.

Published (private) at https://claude.ai/artifact/JGWHh6XqNT5NNVPtSgBzgQ. To update it, build, then publish `game/dist/line-and-hand.html` to that URL with the files listed in `game/dist/files.json`.

## The campaign

Published (private) at https://claude.ai/artifact/QwnxGFmj8i8erJ24qwTWrP, apart from the playtest page. To update it, build, then publish `game/dist/campaign/campaign.html` to that URL with the files listed in `game/dist/campaign/files.json`.

A second page, built from the same game: **the Chronicle, played.** Fourteen missions, from the morning at Harrow Ford to the night on the mill bridge, each set in a scene the page has shown. The prologue is the tutorial: he has the Grace and the sealed Arts for one hand, and loses them. After that his reach on the board follows the Knots the page has tied (a step, or none, in the House of Menders), and his cards carry the rank each Art had in that chapter.

It is laid **over** the game and changes none of it: `src/engine.js`, `src/ui.js`, `src/style.css`, `src/page.html` and `build.py` do not know it exists, so the playtest page is exactly what it was. The campaign wraps the functions the rules export, builds each mission's board on a normal battle, and decides for itself when a mission is won or lost.

| Path | What it is |
|---|---|
| `src/campaign.js` | The campaign's rules, no screen: its cards (an Art at each rank), its foes and ordeals, how a mission's board is built, the objective check, and the wording (a river "pulls", Ysra Tal is "she"). |
| `src/missions.js` | The missions: map, who is there and what each can do, the deck, the aim, the lines before and after. **Reader-safe:** every name, place and quoted line is on the page already. |
| `src/campaign_ui.js`, `src/campaign.css`, `src/campaign.html` | The title, the mission list, the place cards, the telling afterwards, the objective under the board, the grounds. |
| `build_campaign.py` | Builds `dist/campaign/campaign.html` with its pictures beside it. Faces and places come from the site's small copies; a foe with no picture gets a drawn token, and the page lists those. |
| `test/campaign.test.js`, `test/campaign.ui.test.js` | Every mission is well formed and a simple player can finish it; the real page in a browser, and the prologue played through by taps. |

```
python3 game/build_campaign.py        # -> game/dist/campaign/campaign.html
node game/test/campaign.test.js -v    # the missions' rules, and how a simple player fares in each
node game/test/campaign.ui.test.js    # the page in a browser (after the build)
```

**Its rules with the story.** The campaign retells; it never tells. It reads nothing from `real/` and writes nothing to `saga/`; a mission's outcome changes nothing anywhere, and one that goes wrong is played again. A mission is written only after its chapter is closed, from the chapter's own prose, never from `_gm/`: nothing the page has not spoken. **People, places and things stay canon; the fights need not** (his word, 2026-11-18). Most missions play a scene as the page tells it, and where that scene has no blow (the ford, the hall, the Steps, the road above Coldmere) the river, the stair or the cold is fought as a clash. A mission marked `tall` is a full company battle the page does not have (the levy in the inn yard, the grey cloaks at the fold, the dark riders at the weir): it uses only people and places the page has shown, says on its card that the page tells it otherwise, and says in its last line how the page has it. To add one after a chapter closes: a `CP.add({...})` in `missions.js`, any new foe in `campaign.js`, then both campaign tests.

**Still to do:** the three tales as side missions; clash figures and tokens for the grey cloaks, the Confessor's men, the walkers and Ysra Tal; the balance, which so far only a test player has felt.

## Where things are

| Path | What it is |
|---|---|
| `src/engine.js` | The rules, with no screen: maps, foes, cards, the clash, the enemy's turn, the camp. Every card is data, and its text is generated from that data. The balance knobs are the `T` object at the top. |
| `src/ui.js` | The screen and the sound: the map, the card table, the camp, the animations, the curtains between scenes, the music. It only shows and paces what the engine decides. The list of sounds (`SFX`) and the one set of drawn icons (`IC`) are here. |
| `src/style.css`, `src/page.html` | The look, and the page around the game (how to play, the sound list, the picture prompts, the design notes). |
| `art/figures/`, `art/tokens/` | Pictures made for the game alone: a cut-out full figure for the clash and a square portrait for the map, one of each for a foe. |
| `sfx/` | Sounds made for the game, one file a sound, named as the list names it. |
| `music/` | Background music: `map` plays under the map and the camp, `clash` at the card table. |
| `tools/file_art.py` | Files a picture, a sound or a music track under its proper name. |
| `build.py` | Puts it together into `dist/` (not kept in git). |
| `test/` | `engine.test.js` (the rules), `ui.test.js` (the real page in a browser), `flicker.js` (counts what is rebuilt on screen: it should be nothing), `playtest.js` (a test player that looks ahead, and its report), `worth.js` (what each camp card is worth to that player, on every core), `try.js` (one balance setting, one line), `bots.js` and `sweep.js` (balance). |

Pictures of Darrow, the company and the Arts are not copied here: the build takes the small copies the site already keeps in `saga/art/thumbs/`. The game's foes never go in `saga/art/`, which is for what the Chronicle has shown.

## Build, play, test

```
python3 game/build.py                 # -> game/dist/line-and-hand.html, with art/ and sfx/ beside it
node game/test/engine.test.js         # the rules: every card does what it says, 4,000 random games, the bots
node game/test/ui.test.js             # the screen: needs the build first, and Playwright
node game/test/playtest.js            # a look-ahead player plays 300 runs and reports how hands and battles went
node game/test/worth.js 150 1         # what each camp card is worth to that player: runs each, level (1 is Hard)
node game/test/try.js '{"pressUp":3}' 80 3   # one setting of T, measured: runs, rounds a clash
node game/test/sweep.js               # try balance settings against both test players
node game/test/flicker.js             # after a build: what a tap or a card play rebuilds on screen (should be nothing)
```

Open `game/dist/line-and-hand.html` in a browser to play the build.

## When he sends a picture or a sound

```
python3 game/tools/file_art.py figure pikeman  PICTURE [--preview DIR]   # chroma screen keyed out the Wardrobe's way, 2:3
python3 game/tools/file_art.py token  pikeman  PICTURE                   # square, for the map
python3 game/tools/file_art.py sound  battle_won FILE                    # by its name in the game's list
python3 game/tools/file_art.py music  map FILE                           # map (the map and the camp) or clash (the card table)
```

A picture's name is who it shows: `pikeman`, `swordsman`, `crossbowman`, `skirmisher`, `shieldbearer`, `bannerman`, `captain`, or `hollis`, `ash`, `wren` for the company's clash figures. A sound's name is one of the names in the page's "Sounds to make" table; the tool refuses any other. Then build, run both tests, publish, and ship. The page marks what is made and what is still to make by itself.

Made so far: the pikeman and the swordsman (figure and token each), the sounds `battle_won` and `run_won`, and both music tracks.

## The game in one page

- **The map.** Six by seven. Wood and fords cost two steps; wood gives cover. Footing beats Blade beats Cast beats Footing. One of the company with a friend right behind him can fall back through that friend to the open tile beyond: straight back, one friend, the whole move. The foes cannot.
- **The company.** Darrow's deck is the sheet: one card for each Art, plus Strikes and Guards. Hollis, Ash and Wren have small decks of their own. Rae does not fight: three times a battle she tends a friend beside her, and a fighter beside her is lent her hand (its strength follows the Tether's stage).
- **A clash.** One hand, played on that fighter's breath; then the foe answers once. Start a fight against the tree yours beats, land a hit, and he is Broken: his answer is halved. From two tiles Darrow throws on one less breath, and most foes cannot answer at all. Friends placed to help lend a card. Block left over stays as guard through the enemy's turn, and guard that holds a blow strikes back.
- **The foes.** Each has one habit: the pikeman braces, the shieldbearer is Tough, the skirmisher answers in a flurry, the crossbowman's bolt leaves a Wound, the bannerman makes the others strike harder, the captain enrages at half health and holds his ground until someone comes near.
- **The clock.** The captain holds his ground until someone comes near, his men are thinned, or turn 8. A battle not won by turn 30 is lost at nightfall.
- **The camp.** Every man felled pays a spoil, one more if Darrow's own hand felled him. Between battles: five cards on offer from a pool of eighteen, one of each; mend; hone a Strike or a Guard; leave a card behind. Spoils kept count toward Renown, as does each turn under 10 in a battle won.

## Balance, as last measured

Three test players on Standard, one hand a clash: the one that looks ahead (`playtest.js`) wins about 93% of runs; the sensible but careless one (`bots.js`, "fair") about 40%; the one that only chases the captain about 35%. Most losses are on the third ground. With three rounds a clash the look-ahead player wins about 60% and the careless one about 28%. Gentle and Hard move every foe's strength: the look-ahead player wins about 77% on Hard.

What the look-ahead player taught, and what was changed for it: a free throw from two tiles was worth 39 points of win rate (now one a battle); Broken used to cancel the answer (now halves it); unlimited tending rewarded stalling (now three a battle); fleeing could draw a battle out for ever (now nightfall on turn 30); no camp card was clearly worth buying and Hammerfall was dead weight (the pool is eighteen stronger cards; taking Hammerfall out now costs 6 points on Hard). Falling back through a friend changed nothing on Standard and was worth about 8 points on Hard, so Hard's foes strike 2 harder than Standard's (`T.levelAtk`); `T.fallBack: 0` switches the rule off for measuring.

`worth.js` cannot see the worth of a card that pays spoils or mends: it plays with no camp. These are bots, not him: the numbers that matter are in `T`, and `try.js` and `sweep.js` show what moving them does.
