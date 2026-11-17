# Visual storytelling scorecard, in depth

This rescoring uses the deeper evidence and the live site as it actually renders. The Chronicle still scores highest where it guards the story: spoiler gating, songs, the Wardrobe and the dice all stay close to their benchmarks. The live measurements pull several middle scores down:

- map links, Codex rows and most fold headings are too small for a thumb;
- the Codex downloads about 1.65 MB of songs before anyone presses play;
- the Now page opens on Wardrobe news and arithmetic, with no picture on its first screen and the map below two screens of game state.

The lowest scores are still where the story itself should show: the Now page's opening, the sheet's countdowns, Books, and pictures for story moments. Almost every idea that would raise them is builder work that costs him no time. The evidence and sources are in [the main report](Visual%20storytelling%20in%20depth.md), and "change N" below refers to its numbered changes.

## The scale

Each area is rated against the named benchmark, not against an abstract ideal:

- **5**: matches the best examples the research found.
- **4**: strong, with small gaps.
- **3**: solid, but with clear gaps.
- **2**: present, but weak.
- **1**: absent.

Half points are used. Under "To raise it", the rating after each idea assumes the ideas listed above it in that section are done too. "None" means no cost in his time: the work is Claude's, in the builder.

| Area | Rating | Benchmark |
|---|---|---|
| Spoiler gating | 4.5 | Heaven's Vault's tagged timeline |
| Songs and audio | 4 | Visual-novel music rooms |
| Wardrobe as self-avatar | 4 | Mask of the Rose; avatar studies |
| Dice, odds and stakes | 4 | XCOM; Disco Elysium's checks |
| Map and journey | 3.5 | 80 Days' locked routes |
| Rank and tier language | 3.5 | TWI ranks; Borderlands colours |
| Codex and name previews | 3.5 | Wikipedia previews; Obra Dinn |
| Portraits and change over time | 3.5 | Darkest Dungeon II; Wildermyth |
| Phone reading and accessibility | 3 | NN/g touch targets; WCAG 2.2 |
| Relationships | 3 | 80 Days' trait words; Hades |
| Art direction and the AI pipeline | 3 | Darkest Dungeon; Pentiment |
| The Now page's first screens (new) | 2.5 | NN/g scroll attention |
| Character sheet: shown vs discovered | 2.5 | Darkest Dungeon's stress meter |
| Books, time and the timeline | 2.5 | Sunless Skies' regional palettes |
| Pictures for story moments | 1.5 | Visual-novel event CGs |

## What changed since the first scorecard

- **Songs and audio: 4.5 → 4.** The Codex fetches about 1.65 MB of song audio as it opens. That makes it 1.86 MB, against at most 0.66 MB for every other page.
- **Map and journey: 4 → 3.5.** Its place links are 9 to 22 px tall and are the only links. NN/g finds that maps cause touch errors and should default to a list. On the Now page it sits below about two screens of game state.
- **Rank and tier language: 4 → 3.5.** The crest word "LEVEL" renders at 2.8 to 4.5 px, and the medallion numbers at 6 to 8 px. Neither is readable on a phone.
- **Codex and name previews: 4 → 3.5.**
  - A row's tappable line is 22.7 px, not the 40 px the first audit estimated.
  - The page weighs 1.86 MB on open.
  - Its enlarge view is barely bigger than the inline picture.
  - Person previews load a 640 px copy to fill a 72 px circle.
- **Phone reading and accessibility: 3.5 → 3.** More controls measured under 24 px than the first audit estimated, and some portrait copies are oversized. Prose comfort and contrast held up better than expected.
- **Character sheet: 3 → 2.5.** The live pages show more arithmetic by default than the code audit counted:
  - the Now page's card shows figures and the next Knot;
  - the Collection opens on its full ladder with thresholds;
  - Darrow's page lists untied Knots and what each opens.
- **New area: the Now page's first screens, 2.5.** This is the live audit's main finding.
- **Held, on different evidence:**
  - *Wardrobe*: stronger evidence on identification, weaker on effort, and the drop-out claim was misattributed.
  - *Pictures for story moments*: a quiet picture is less risky than thought, but illustrated versions earned no engagement gain.
  - *Dice*: Solomon and Meier are now read in full.
  - *Art direction*: the tools changed.

## Spoiler gating: 4.5

**Why.** Every kind of picture is gated on whether the page has shown its subject:

- a place or faction picture waits until the page names it;
- a character not yet seen has no portrait;
- hidden Wardrobe pieces are only counted;
- poses follow the Knots;
- an MP3 is refused if its lyrics hold a line the page has not sung.

Live, the Codex keeps "Where he has been" separate from "Named, not yet reached". The designer practice now read in full works the same way:

- Heaven's Vault tags each timeline entry with the knowledge that unlocks it (D, full).
- Fallen London's map "will fill in slowly" (D, full).
- 80 Days locked its routes (D, full).

The genre's biggest fan wiki only warns readers and hides one status field (Docs, full). The half point is lost on two counts. What a picture depicts is still checked only by eye, and AI scenes with several people are where figures get added or dropped (Paper, full). And cast and Codex pages show the current state with no "as of" marker.

**To raise it.**

- Add a spoiler checklist to the style guide: count the figures; allow call-backs only, never a detail that foreshadows; show the season as the prose has it; include no real-world objects. Cost: part of the guide's evening (change 4). → 4.5, held as the pictures multiply.
- Add "as of Chapter N" to cast and Codex pages, and show a status only once the prose has stated it. Cost: none (change 9). → 5.

## Songs and audio: 4

**Why.** Songs play only on a tap, one at a time, with a dock to stop them, and the live site behaves exactly so. The button sits beside the line that sings the song, or in the Codex. This matches the evidence:

- lyrics heard under reading cost comprehension (META, abstract);
- music that matches a story helped children's comprehension (META, full);
- browsers block autoplay with sound anyway (Docs, summary).

The new cost is weight. The Codex's players are marked to load only metadata, yet Chromium fetched three MP3s almost whole as the page opened, about 1.65 MB. This was not measured on a real phone. Also, 4 of the 6 "Songs and verses" entries have audio.

**To raise it.**

- Set the Codex players to load nothing until tapped. Cost: none (change 3). → 4.5.
- Make the two missing songs when he wants, built on one recurring motif shared across all the songs, as inkle's and Failbetter's composers do (D, full). Cost: an hour or so each, with his own tools. → 5.
- Add nothing under the reading. Cost: none. → holds.

## Wardrobe as self-avatar: 4

**Why.** He designs each look in the Forge, pieces open from progress the story has paid for, and poses follow the Knots. The Wardrobe is the only page that opens on a picture: the painted look fills 47% of its first screen. The evidence read in full is now sharper:

- customisation strongly raises identification (d = 0.69; ηp² = .69) but not fun or real performance (CTRL, full);
- customising with no purposeful task went with lower resilience to a low mood (CTRL, abstract), so keeping the Wardrobe inside the story loop is right;
- realistic bodies with a few idealised touches avoided the effort cost that idealised bodies carried (CTRL, summary);
- change that arrived gradually, caused by the user's own effort, beat an instant switch on sense of agency (CTRL n=32, full).

There are three gaps:

- The round portrait and the full-length looks are made separately, and full-body framing is where AI identity drifts most (Paper, full).
- Each piece's reason does not link to its scene.
- The stage loads the full 1024×1536 look to show it at 322×484.

**To raise it.**

- Link each piece's reason to the scene that earned it. Cost: none (change 8). → 4.5.
- Keep one identity master pair (a full-body figure and a face close-up) for both the portrait and the looks, and make each new look from it in a fresh conversation. Cost: an hour, once (change 4). → 4.5, held.
- Add a history line to the prompt (wear, repairs, an inherited piece), so earned gear looks used. Cost: none beyond each look (change 4). → 5.

## Dice, odds and stakes: 4

**Why.** Each check is one line with a result glyph and its arithmetic in a fold, and no odds appear before a roll. Both designer warnings are now read in full: Solomon's players read 85% as a sure hit (D via C, full), and Meier's "paranoia sets in" (D via C, full). There are three gaps:

- Nothing marks a once-only climax roll as different, which Disco Elysium's red checks do (summary).
- "The roll" folds on the Now page are 18.5 px tall.
- A result label inside a closed fold is 3.0:1 against the background.

**To raise it.**

- Give climax rolls a distinct rim. Cost: none (change 7). → 4.5.
- Pad the roll folds and lift that label's contrast. Cost: none (change 3). → 5.
- Keep rolls static and odds off the page. Cost: none. → holds.

## Map and journey: 3.5

**Why.** The structure is right, and the deeper evidence supports it more strongly:

- The route is drawn only as far as he has gone. 80 Days' postmortem found that showing every route made players stop reading (D, full).
- Markers change once a place is visited, and tapping a place opens its Codex row (measured).
- Readers do not build a sense of space from prose unprompted, so a map supplies what they skip (CTRL, abstract).

The live map fails under the thumb and in its placement:

- it renders at 374×281 on a phone, with labels of 8.8 to 10.2 px;
- its 14 place links are 9 to 22 px tall, are the only links, and two fail even the spacing exception;
- NN/g says maps on touchscreens cause errors and a list should be the default (full);
- on the Now page it sits below about two screens of game state, past where most viewing time goes;
- there are no notes in the hero's voice, which Firewatch's map has.

**To raise it.**

- Add 44 px hit areas and a list of visited places under the map. Cost: none (change 6). → 4.
- Move the map directly under the story plate. Cost: none (change 1). → 4.5.
- Add one line quoted from the page per visited place, linked to its scene, and draw a landmark where the route bends. Cost: none (change 6). → 5.

## Rank and tier language: 3.5

**Why.** Rank is metal throughout, drawn in one brass idiom, and colour stays off the rank code. That is The Wandering Inn's rule of colour for kind and metal for rank (Community, full), and it avoids the rarity colours gaming readers carry (C, full). The live site shows three legibility problems:

- the word "LEVEL" on crests renders at 2.8 to 4.5 px, which is unreadable;
- crest numerals run 9.4 to 11.3 px, and medallion numbers 6 to 8 px;
- the two ladders share metal names, and neighbouring metals are hard to tell apart at phone size, where accessible practice pairs colour with a shape or symbol (C and D, full).

**To raise it.**

- Drop the crest word, let the numeral stand, and fold the tiny numbers. Cost: none (changes 2, 3). → 4.
- Give each ladder its own shape plus pips or a numeral, and run a Color Oracle check. Cost: none (change 3). → 4.5.
- Keep Book accent colours off crests and frames, so colour never becomes a second rank code. Cost: none (change 7). → 5.

## Codex and name previews: 3.5

**Why.** The previews are measured working. The first tap opens a small card and the second follows the link, and without JavaScript they are plain links. That matches NN/g's guidance for short, dismissible overlays (full). The Codex is built only from the prose, splits places reached from places only named, and keeps its full pictures lazy inside closed rows. The live site shows six weaknesses:

- a row's tappable line is 22.7 px, and the preview's "Open →" link is 18 px;
- the page weighs 1.86 MB on open because of song audio;
- a person's preview loads a 640 px copy to fill a 72 px circle;
- the enlarge view is 390×218 against 356×199 inline, where NN/g asks for at least twice the size (full);
- nothing marks what each chapter added, as Heaven's Vault's tagged entries and the Wandering Inn wiki's "revealed" rows do (D, full; Community, full);
- 5 of 17 places have pictures, and the current place is not one of them.

**To raise it.**

- Pad the rows and "Open →", stop the audio preload, use small face crops, and make the enlarge view fill the screen. Cost: none (change 3). → 4.
- Add a "New in the Codex" row at each chapter's foot. Cost: none (change 8). → 4.5.
- Paint the current place, so the previews he meets most often carry a picture. Cost: one picture per place he stays (change 5). → 4.5, held.
- Later, add a reader-position filter for readers catching up. Cost: none. → 5.

## Portraits and change over time: 3.5

**Why.** Coverage is good. 18 of 19 roster entries have a portrait. Book I and Book II portraits swipe with tabs that follow the swipe, and without JavaScript the strip still scrolls (measured). This is the right idea: Darkest Dungeon II's "grow the characters up" (D via C, full) and Wildermyth's piece-by-piece change (C, full). The evidence adds a warning: readers judge character from faces, and they notice inconsistency in AI art (CTRL, abstract). The gaps:

- Book tabs are 20.4 px tall;
- both slides load at once;
- nothing fixes crop and light across the cast;
- tabs do not link to where the prose described the change;
- one companion's page runs 5,556 px, with about 90 appearance links each 15 px tall.

**To raise it.**

- Fix crop, light direction and eye-line in the style guide. Cost: an hour, within the guide (change 4). → 4.
- Link each Book tab to the chapter where the change was written. Cost: none (change 8). → 4.5.
- Use labelled thumbnails and taller tabs, lazy-load the second slide, and fold Appearances by chapter. Cost: none (changes 3, 9). → 4.5, held as Books accumulate.

## Phone reading and accessibility: 3

**Why.** The measured strengths are real:

- chapter prose is 18 px at about 50 characters a line;
- contrast is at least 4.69:1 on every visible text;
- every page works without JavaScript;
- layout shift is zero or near it, and the largest paint comes at 0.84 s;
- the blackletter is kept to titles of about 20 px and up.

The measured failures are more numerous than the first audit estimated:

- most fold headings and list links are 15 to 23.5 px tall;
- map links are 9 to 22 px tall;
- the drawn devices hold text of 2.8 to 8 px;
- six 640 px portrait copies fill 48 to 86 px circles, about 250 KB that could be saved;
- the Codex preloads about 1.6 MB of audio;
- desktop lines run 88 to 93 characters.

The dark-only theme runs against NN/g's review, which finds light mode better for acuity and notes that users decide at the system level (full). The forge identity is a deliberate choice, and that edge is modest.

**To raise it.**

- Pad every fold heading and list link to at least 24 px, toward 44. Cost: none (change 3). → 3.5.
- Use small portrait crops, stop the audio preload, and lazy-load later slides. Cost: none (change 3). → 4.
- Cap the desktop prose width, and optionally add a light reading theme that follows the phone's setting. Cost: none; the theme is his call (change 12). → 4.5.

## Relationships: 3

**Why.** A companion's regard shows as a word, an ember glyph and a bar with no number. NN/g finds icons need words beside them (full), and the site provides them. On a character page, relationships are prose with one regard bar toward Darrow (measured). The gap is timing. Nothing shows when or why regard changed. Ingold's lesson is to prove attention fast, and Vanaman's is that once a notice is learned, its absence reads as "nothing changed" (D via C, full).

**To raise it.**

- Where the page has shown a change in regard, link the regard word to that scene. Cost: none (change 8). → 3.5.
- Link each keepsake to the tale piece that gave it. Cost: none (change 8). → 4.
- Make any mark of a regard change appear every time, or not at all. Cost: none. → holds.

## Art direction and the AI pipeline: 3

**Why.** The painted layer and the brass line art are each consistent, and live, the period fonts load and carry the feel. But only the Wardrobe's looks have a written style anchor; portraits, places, cards and the map rely on his memory. The tools have changed:

- OpenAI's GPT-Image-2.6 takes 16 inputs, always reads them at high fidelity, and its guide recommends chained edits (Official, full);
- Midjourney's Edit Model replaced Omni Reference (Official, summary);
- identity drifts with every chained edit, and drifts most in full-body framing (Paper, full);
- models put an unspecified mark on a default side, which is how a scar ends up on the wrong side (Paper, full).

There is no disclosure. The AI label lowers ratings most under reflective viewing, and short interpretive captions reduce that penalty (CTRL, full).

**To raise it.**

- Write the one-page style guide. Cost: an evening, once (change 4). → 3.5.
- Work from a master pair, start each picture in a fresh conversation, allow at most two or three refinements, name both sides of every mark, and compare against the master and a flipped master at thumbnail size. Cost: minutes per picture (change 4). → 4.
- Add a footer disclosure line, and caption each picture with the line it shows. Cost: none (change 11). → 4.5.

## The Now page's first screens: 2.5

**Why.** This area is new, added from the live audit.

- The first screen opens on a "New in the Wardrobe" banner, then the story plate, with no picture.
- Continue reading sits about 680 px down.
- The Reckoning card and the dice fill roughly two of the page's five screens, and the map comes after them.
- NN/g puts 74% of viewing time in the first two screens, and people rarely go past the third (full).

The plate itself is good: Book, chapter, place, season, latest scene and Continue reading.

**To raise it.**

- Shrink the Wardrobe news to one line inside the Reckoning card. Cost: none (change 1). → 3.
- Put the map directly under the plate, and fold the Reckoning card's figures. Cost: none (changes 1, 2). → 3.5.
- Paint the current place as the plate's backdrop. Cost: one picture per place he stays (change 5). → 4.

## Character sheet: shown vs discovered: 2.5

**Why.** The sheet has story-native devices: medallion arcs against his former self, the rope, and metal-framed Art cards. Elsewhere the site hides mechanics well: other people's sheets stay unread until the story allows, and hidden Wardrobe pieces are only counted. But the live pages lead with arithmetic:

- Darrow's first screen holds 20 digits;
- the Collection opens on 33, its full ladder with each rank's threshold;
- the Now card shows its figures and the next Knot;
- untied Knots are each listed with what they will let the leg do.

The evidence read in full sharpens the gap. Darkest Dungeon shows the meter but never the consequence table (D, full). Ingold warns that visible points invite min-maxing (D via C, full). Visible counters drive minimal keep-alive actions (FIELD, full), and counting lowers enjoyment (CTRL, abstract).

**To raise it.**

- Fold every countdown, threshold and "so far" figure on Darrow's page, the Collection's ladder (keeping his rank and the next) and the untied Knots. Cost: none (change 2). → 3.5.
- Fold the Now card's figures and its next-Knot line. Cost: none (changes 1, 2). → 4.
- Put one line from the page on each Art card, linked to its scene. Cost: none (change 8). → 4.5.

## Books, time and the timeline: 2.5

**Why.** The recap structure is sound and measured working: a Timeline with a knot and tier seal per chapter, a "Previously" box, and Continue reading. But Books are text lines, and answered choices appear only as a numbered list with a "chosen" mark. The Chronicle's chapter links (23.2 px) and scene folds (20 to 22 px) are small for a thumb. The benchmark is now read in full: Failbetter gave each Sunless Skies region "its own distinctive colour palette" for navigation (D, full), and Obra Dinn gave each chapter a musical theme as a landmark (D, full). A colour arc at the level of a Book remains an inference.

**To raise it.**

- Give each Book an accent colour once it opens. Cost: none (change 7). → 3.
- Mark every answered choice on the Timeline. Cost: none (change 7). → 3.5.
- Paint one closing picture per Book and use it as the Book's emblem. Cost: one picture per Book (change 7). → 4.

## Pictures for story moments: 1.5

**Why.** All 8 chapter pages and every tale hold no images, and the Now page's first screen holds none (measured). The half point is for the name-preview cards, which show a picture wherever the person or place has one. The evidence has shifted both ways. A quiet, matching picture is less harmful than the first scorecard assumed (META via citing full text), and placement at the start still does the most damage (CTRL, abstract). But an illustrated version of a story earned no engagement gain, and text-only readers felt more (CTRL, abstract). Pictures here should stay scarce, and their payoff may be smaller than the benchmark suggests.

**To raise it.**

- Paint the place he stands in. Cost: one picture per place he stays (change 5). → 2.
- Paint one closing picture per Book. Cost: one picture per Book (change 7). → 3.
- Add an optional picture at the end of the climax block, captioned with its line, and show no empty frame in weeks without one. Cost: up to one picture per chapter, only when he wants (change 10). → 4.5.
