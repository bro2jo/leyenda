# Visual storytelling scorecard

Against the best examples the research found, the Chronicle's site scores highest where it guards the story. Its spoiler gating is stricter than any fan wiki in the research, and the songs, Wardrobe, dice and map are close to their benchmarks. It scores lowest where it should show the story itself: chapters, Books and the passage of time get almost no visual support, and the character sheet shows more of the arithmetic than either the evidence or his own wish to discover the mechanics favours. Most of the ideas that would raise the low scores are builder work that costs him no time. Only a few call for his own paintings, all at the story's peaks. The full evidence and sources are in [the main report](Visual%20storytelling%20for%20the%20Chronicle.md), and "change N" below refers to its numbered changes.

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
| Spoiler gating | 4.5 | Coppermind's no-unreleased rule; Ren'Py galleries |
| Songs and audio | 4.5 | Ren'Py Music Room |
| Wardrobe as self-avatar | 4 | Avatar customisation studies; Mask of the Rose |
| Dice, odds and stakes | 4 | Disco Elysium's white and red checks |
| Map and journey | 4 | 80 Days globe; Firewatch map |
| Rank and tier language | 4 | TBATE's core colours; card-frame finishes |
| Codex and name previews | 4 | Wikipedia previews; Heaven's Vault timeline |
| Portraits and change over time | 3.5 | Crusader Kings III; Wildermyth |
| Phone reading and accessibility | 3.5 | WCAG 2.2; web.dev |
| Character sheet: shown vs discovered | 3 | Disco Elysium's sheet; Outer Wilds |
| Relationships | 3 | Hades keepsakes; Mass Effect |
| Art direction and the AI pipeline | 3 | Darkest Dungeon; The Banner Saga |
| Books, time and the timeline | 2.5 | Heaven's Vault timeline; Journey, Gris |
| Pictures for story moments | 1.5 | Visual-novel event CGs |

## Spoiler gating: 4.5

**Why.** Every kind of picture is gated by whether the page has shown its subject:

- the build refuses a place or faction picture before that place or faction is on the page;
- a character not yet seen has no portrait;
- hidden Wardrobe pieces stay off the site entirely;
- poses follow the Knots;
- an MP3 is refused if its embedded lyrics hold a line the page has not sung.

That is stricter than fan wikis, which mostly warn and "cannot guarantee a reader will not be spoiled" (TWI wiki, Community). It matches Coppermind's rule of adding nothing unreleased (Docs). The half point is lost because two things are still only checked by eye or not marked at all. What a picture actually depicts is checked only by eye. And the cast and Codex pages show the current state with no "as of" marker, the infobox problem wikis struggle with (wiki policy).

**To raise it.**
- Add a spoiler checklist for every new picture to the style guide: no unrevealed figure, the season as the prose has it, no real-world objects. Cost: an hour, once (change 3). → 4.5, held as the picture count grows.
- Add the chapter number to "Only what the story has shown so far." on cast and Codex pages. Cost: none (change 9). → 5.

## Songs and audio: 4.5

**Why.** Songs play only on a tap, one at a time and never automatically. The button sits beside the line that sings the song, or in the Codex, which is the visual-novel "Music Room" pattern (Ren'Py, Docs). This fits the evidence:

- lyrics playing under reading cost comprehension (meta-analysis, Study);
- listening as its own activity raises imagery and absorption (Study).

The lyric check is the only piece of media content the build verifies by machine. The half point is lost on two counts. Only 4 of the 6 "Songs and verses" entries have audio. And the dock lets him keep reading under a lyric, a mild cost that is his choice. No study tests reading the same words one is hearing sung.

**To raise it.**
- Make the two missing songs when he wants them. Cost: an hour or so each, with his own tools. → 5.
- Add nothing under the reading. An ambient track is the only under-reading audio the research does not penalise, and it would cost his time for little gain. Cost: none. → holds.

## Wardrobe as self-avatar: 4

**Why.** He designs each look himself in the Forge, pieces open from progress the story has paid for, and poses follow the Knots, so the body never runs ahead of reality. That matches the best avatar evidence:

- customisation raises identification and motivation, and cut drop-out in a field study (Birk, CTRL);
- a realistic self beats an idealised one (Koulouris, CTRL);
- people act like their avatar, the Proteus effect (META).

There are two gaps. His round head portrait and the full-length looks are made by separate processes, so Darrow has two depictions that can drift apart. And each piece lists a reason and chapter but does not link back to its scene. The evidence comes from VR and photo-real selves, so expect a weaker effect on a phone. That part cannot be fixed.

**To raise it.**
- Link each piece's reason to the scene that earned it. Cost: none (change 6). → 4.5.
- Use one face master for both the portrait and the looks. Cost: an hour (change 6). → 4.5.
- Add a "wear" line to the prompt for scuffs, repairs and an inherited piece, so earned gear looks used. Cost: none beyond each look (change 6). → 5.

## Dice, odds and stakes: 4

**Why.** Each check collapses to one line: a die glyph coloured by its outcome, the result and where it was cast, with the arithmetic folded behind a tap. No odds appear before a roll. That avoids two failure modes designers describe:

- the "85% means success" trap (XCOM and Civilization, D);
- Baldur's Gate 3's long roll animation (C).

What is missing is Disco Elysium's white-and-red distinction (D/W): nothing marks a once-only climax roll as different from an ordinary one.

**To raise it.**
- Give climax rolls a distinct rim or seal. Cost: none (change 7). → 5.
- Keep the roll static and the odds off the page. Cost: none. → holds.

## Map and journey: 4

**Why.** The map has the strongest structure the research found:

- a painted base;
- a route drawn leg by leg, only as far as the prose has gone;
- grey, brass and ember markers for not yet visited, visited and current;
- earlier Books' legs drawn fainter;
- a build that refuses any route not ending where Darrow stands.

That matches 80 Days' lit routes (Designer, C) and the finding that readers' spatial memory follows the protagonist (CTRL). The gaps are on the phone and in the voice:

- labels render at about 9 px and are the only links to the places, the same complaint 80 Days drew (F);
- there is no text list of places;
- there are no notes in the hero's voice, which Firewatch's map has (C/D).

No study tests fantasy maps directly.

**To raise it.**
- Give each marker a 44 px hit area and add a list of visited places under the map. Cost: none (change 4). → 4.5.
- Add one short page-quoted line per visited place, linked to its scene. Cost: none (change 4). → 5.
- Draw each Book's leg in that Book's accent colour. Cost: none (change 2). → holds 5.

## Rank and tier language: 4

**Why.** Rank is metal throughout, drawn as brass line art in one heraldic idiom:

- crests, frame edges and rivets all take the rank's metal;
- Art card frames add studs, a second rule and a glow as they rise;
- violet is reserved above gold, like TBATE's off-ladder purple (fan wiki).

The palette also avoids the WoW rarity colours that gaming readers carry (fan wiki). There are two gaps. The character ladder and the Art ladder share metal names but differ in their steps. And brass against gold, or steel against silver, are hard to tell apart at phone size. Accessible practice pairs colour with a numeral or a shape (fan project).

**To raise it.**
- Give each ladder its own shape plus a pip or numeral. Cost: none (change 7). → 4.5.
- Check the metal tones for contrast and colour blindness at phone size. Cost: none. → 5.

## Codex and name previews: 4

**Why.** The name previews already meet their benchmark. A first mention becomes a dotted link, and tapping it opens a small card (a face crop or a 16:9 picture, a title, one line) that falls back to a plain link without JavaScript. That matches Wikipedia's previews, which about 0.01% of readers turned off (Data), and avoids the popups that block reading (Community). The Codex itself is strong in structure:

- it is built only from what the prose has said;
- places are split into "where he has been" and "named, not yet reached", a partial-knowledge view like Outer Wilds' log (W).

It falls short on three counts:

- nothing marks the moment a chapter adds an entry, the way Heaven's Vault's pop-up does (C);
- most preview cards are text, with pictures for 5 of 17 places and a single thing;
- pages show only the current state.

**To raise it.**
- Add a "New in the Codex" row at each chapter's foot. Cost: none (change 8). → 4.5.
- Paint the place he is in, so the previews he meets most often carry a picture. Cost: one picture per new place he stays in (change 3). → 4.5, held.
- Add an optional reader-position filter for readers catching up. Cost: none for him (change 9). → 5.

## Portraits and change over time: 3.5

**Why.** Coverage is good:

- 18 of 19 characters have a portrait;
- six carry swipeable Book I and Book II portraits;
- a fallen character gets a sigil "in memory".

That is the Crusader Kings III and Mass Effect idea of change on the same figure (D, W). Consistency is weaker:

- framing varies from close-ups to wide shots, which is why a zoom field exists;
- nothing fixes light or crop across the cast;
- the Book tabs are about 20 px tall;
- a new portrait does not link to where the prose described the change, while Wildermyth pairs every change with its scene (C).

No study tests portraits in serial fiction, so this rests on designer practice.

**To raise it.**
- Fix crop, light direction and eye-line in the style guide. Cost: an hour, once (change 3). → 4.
- Link each Book tab to the chapter where the change was written. Cost: none (change 6). → 4.5.
- Make the tabs a comfortable tap size. Cost: none (change 7). → 4.5, held.

## Phone reading and accessibility: 3.5

**Why.** The site is built phone-first:

- one column, with a masthead that hides on scroll;
- folds everywhere and a text-size control;
- small WebP copies of every picture, with width and height set;
- reduced motion honoured;
- every page works without JavaScript;
- alt text required, and contrast that passes comfortably.

Three things fall below standard:

- chips (about 23 px) and portrait tabs (about 20 px) are under WCAG 2.2's 24 px minimum (Spec);
- map labels are about 9 px;
- every slide of a portrait frame loads eagerly (web.dev, Docs).

The dark-only theme runs against NN/g's modest lean toward light mode for normal vision (Study review). It is a deliberate identity, though, and that evidence edge is small.

**To raise it.**
- Raise chips, tabs, nav links and the song button toward 44 px. Cost: none (change 7). → 4.
- Lazy-load portrait slides after the first, and keep the first visible image eager. Cost: none (change 7). → 4.5.
- Fix the map's targets. Cost: none (change 4). → 4.5, held.

## Character sheet: shown vs discovered: 3

**Why.** The sheet has story-native devices:

- medallion arcs measured against the Knight Who Fell, a change on the same figure;
- the rope and its Knots;
- metal-framed Art cards.

Elsewhere, the site hides mechanics well: other people's Reckonings read "⟦ unread ⟧", and hidden Wardrobe pieces are only counted. But Darrow's page opens on the arithmetic. Each tile shows "temper … · next at …", each Art row "next at … (… so far)", on the page that is also the site's main picture of him. The evidence on this is clear:

- counting output raises effort but lowers enjoyment and the urge to return (Etkin, CTRL ×6);
- points and levels raise quantity, not intrinsic motivation (Mekler, CTRL).

No study compares hidden with visible mechanics directly.

**To raise it.**
- Fold every countdown and threshold into a closed fold, so that opening it is the asking. Cost: none (change 1). → 4.
- Put one line from the page on each Art card, Disco Elysium's "skill as a character" move. Cost: none. → 4.5.

## Relationships: 3

**Why.** A companion's regard toward Darrow shows as a word, an ember glyph and a bar with no number. That is the middle path between Mass Effect's visible meters and Baldur's Gate 3's hidden approval (D/C). The keepsake shelf echoes Hades' keepsakes (W). There are two gaps. Every other relationship is a label and a note in words. And nothing shows when or why regard changed, though Ingold's point is that a game must quickly prove it noticed (D). No controlled study tests relationship visuals.

**To raise it.**
- Where the page has shown a change in regard, link the regard word to that scene. Cost: none (change 6). → 3.5.
- Link each keepsake to the tale piece that gave it. Cost: none (change 6). → 4.

## Art direction and the AI pipeline: 3

**Why.** The painted art is coherent today (painterly, cold and muted), and the drawn layer is one brass idiom. The Forge's process for looks follows vendor advice: reference images, a constructed prompt, a chroma screen, and a key-out step that refuses checkerboards (Official). The weak points:

- only looks have a written style anchor, so portraits, places, cards and the map rely on his memory;
- aspect and framing vary across picture kinds;
- nothing corrects ChatGPT's warm colour cast (Secondary);
- there is no disclosure line, though fantasy readers punish undisclosed AI art (Secondary).

Darkest Dungeon and The Banner Saga each held mixed art together by committing to one tradition (Primary).

**To raise it.**
- Write a one-page style guide: one lineage, rules for each picture type, an identity block for each recurring face, and a near-miss page. Cost: an evening, once (change 3). → 4.
- Colour-correct after keying, and check each new picture against its master at thumbnail size. Cost: minutes per picture (change 3). → 4.
- Add one footer line saying how the pictures and songs are made. Cost: none (change 10). → 4.5.

## Books, time and the timeline: 2.5

**Why.** The recap structure is sound. The Chronicle's Timeline rail has a knot per chapter with tier seals, each chapter opens with a "Previously" recap, and Continue reading leads to the newest block. But the larger arc has little visual form:

- Books are text lines, with no colour, cover or emblem;
- the season is a single line of text;
- choices appear only as the last one answered.

The benchmarks are Heaven's Vault's timeline (C) and the colour arcs of Journey and Gris (D). Applying a colour arc at the level of a Book is inference.

**To raise it.**
- Give each Book an accent colour once it opens. Cost: none (change 2). → 3.
- Add fork marks for answered choices on the rail. Cost: none (change 2). → 3.5.
- Paint one closing picture per Book and use it as the Book's emblem on the rail. Cost: one picture per Book (change 2). → 4.

## Pictures for story moments: 1.5

**Why.** No chapter, climax, Book or tale has a picture. The chapter template has no image slot, so pictures reach the reading only through name-preview cards. The Now page's place backdrop is missing today, because the current place is one of the 12 of 17 places without a picture. The benchmarks are clear:

- visual novels spend full illustrations on peaks, and the last one becomes the route's lasting memory (practitioner essay);
- light-novel plates spoil when placed up front (poll);
- Dickens gave each part two plates (scholarly).

The evidence favours scarce pictures placed after the scene. A striking still image beside key text does the most harm (META), and moving it to the end removed the harm (CTRL). The half point is for the place backdrop and the previews.

**To raise it.**
- Paint the place he is in. Cost: one picture per new place he stays in (change 3). → 2.
- Paint one closing picture per Book. Cost: one picture per Book (change 2). → 3.
- Add an optional picture at the end of the climax block, with no empty frame in weeks without one. Cost: up to one picture per chapter, only when he wants (change 5). → 4.5.
