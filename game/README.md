# The Line and the Hand

A side game. Darrow and the company move on a small map; each fight is played as a hand of cards. Three battles make a run.

**It is not the Chronicle.** Nothing here is canon, nothing here reads `real/`, and nothing here writes to `saga/`. The foes are a hired road company made up for the game. A run lends cards and ends: an Art, a rank or a point of Might only ever comes from the Ledger.

Published (private) at https://claude.ai/artifact/JGWHh6XqNT5NNVPtSgBzgQ. To update it, build, then publish `game/dist/line-and-hand.html` to that URL with the files listed in `game/dist/files.json`.

## Where things are

| Path | What it is |
|---|---|
| `src/engine.js` | The rules, with no screen: maps, foes, cards, the clash, the enemy's turn, the camp. Every card is data, and its text is generated from that data. The balance knobs are the `T` object at the top. |
| `src/ui.js` | The screen and the sound: the map, the card table, the camp, the animations. It only shows and paces what the engine decides. The list of sounds (`SFX`) is here. |
| `src/style.css`, `src/page.html` | The look, and the page around the game (how to play, the sound list, the picture prompts, the design notes). |
| `art/figures/`, `art/tokens/` | Pictures made for the game alone: a cut-out full figure for the clash and a square portrait for the map, one of each for a foe. |
| `sfx/` | Sounds made for the game, one file a sound, named as the list names it. |
| `tools/file_art.py` | Files a picture or a sound under its proper name. |
| `build.py` | Puts it together into `dist/` (not kept in git). |
| `test/` | `engine.test.js` (the rules), `ui.test.js` (the real page in a browser), `flicker.js` (counts what is rebuilt on screen: it should be nothing), `playtest.js` (a test player that looks ahead, and its report), `bots.js` and `sweep.js` (balance). |

Pictures of Darrow, the company and the Arts are not copied here: the build takes the small copies the site already keeps in `saga/art/thumbs/`. The game's foes never go in `saga/art/`, which is for what the Chronicle has shown.

## Build, play, test

```
python3 game/build.py                 # -> game/dist/line-and-hand.html, with art/ and sfx/ beside it
node game/test/engine.test.js         # the rules: every card does what it says, 4,000 random games, the bots
node game/test/ui.test.js             # the screen: needs the build first, and Playwright
node game/test/playtest.js            # a look-ahead player plays 300 runs and reports how hands and battles went
node game/test/playtest.js cards      # what each camp card is worth to that player
node game/test/sweep.js               # try balance settings against both test players
node game/test/flicker.js             # after a build: what a tap or a card play rebuilds on screen (should be nothing)
```

Open `game/dist/line-and-hand.html` in a browser to play the build.

## When he sends a picture or a sound

```
python3 game/tools/file_art.py figure pikeman  PICTURE [--preview DIR]   # chroma screen keyed out the Wardrobe's way, 2:3
python3 game/tools/file_art.py token  pikeman  PICTURE                   # square, for the map
python3 game/tools/file_art.py sound  battle_won FILE                    # by its name in the game's list
```

A picture's name is who it shows: `pikeman`, `swordsman`, `crossbowman`, `skirmisher`, `shieldbearer`, `bannerman`, `captain`, or `hollis`, `ash`, `wren` for the company's clash figures. A sound's name is one of the names in the page's "Sounds to make" table; the tool refuses any other. Then build, run both tests, publish, and ship. The page marks what is made and what is still to make by itself.

Made so far: the pikeman and the swordsman (figure and token each), and the sounds `battle_won` and `run_won`.

## The game in one page

- **The map.** Six by seven. Wood and fords cost two steps; wood gives cover. Footing beats Blade beats Cast beats Footing.
- **The company.** Darrow's deck is the sheet: one card for each Art, plus Strikes and Guards. Hollis, Ash and Wren have small decks of their own. Rae does not fight: three times a battle she tends a friend beside her, and a fighter beside her is lent her hand (its strength follows the Tether's stage).
- **A clash.** One hand, played on that fighter's breath; then the foe answers once. Start a fight against the tree yours beats, land a hit, and he is Broken: his answer is halved. From two tiles Darrow throws on one less breath, and most foes cannot answer at all. Friends placed to help lend a card. Block left over stays as guard through the enemy's turn, and guard that holds a blow strikes back.
- **The foes.** Each has one habit: the pikeman braces, the shieldbearer is Tough, the skirmisher answers in a flurry, the crossbowman's bolt leaves a Wound, the bannerman makes the others strike harder, the captain enrages at half health and holds his ground until someone comes near.
- **The clock.** The captain holds his ground until someone comes near, his men are thinned, or turn 8. A battle not won by turn 30 is lost at nightfall.
- **The camp.** Every man felled pays a spoil, one more if Darrow's own hand felled him. Between battles: five cards on offer, one of each; mend; hone a Strike or a Guard; leave a card behind. Spoils kept count toward Renown, as does each turn under 10 in a battle won.

## Balance, as last measured

Three test players on Standard, one hand a clash: the one that looks ahead (`playtest.js`) wins about 91% of runs; the sensible but careless one (`bots.js`, "fair") about 35%; the one that only chases the captain about 15%. Most losses are on the third ground. With three rounds a clash the careless player drops to about 19%. Gentle and Hard move every foe's strength one step.

What the look-ahead player taught, and what was changed for it: a free throw from two tiles was worth 39 points of win rate (now one a battle); Broken used to cancel the answer (now halves it); unlimited tending rewarded stalling (now three a battle); fleeing could draw a battle out for ever (now nightfall on turn 30). It still keeps Darrow back and lets the companions fight, which is the next thing to watch with a person playing.

These are bots, not him: the numbers that matter are in `T`, and `sweep.js` shows what moving them does.
