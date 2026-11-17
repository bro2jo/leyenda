# The Chronicle's public site today: its visual, graphic, image and audio elements (inventory and assessment)

Scope and method. These notes describe the reader-facing site that `engine/build_site.py` builds from `saga/` into `docs/` and GitHub Pages serves. Sources are the builder, its stylesheet and scripts, the art folder and its rules, the Wardrobe files and the reader-safe registries (`saga/characters/`, `saga/state/{places,factions,codex_art,looks,world,darrow}.json`, `engine/rules.json`). No GM file, no `real/` file and no `docs/` file was opened.

**I could not reach the live site.** The likely address is `https://bro2jo.github.io/leyenda/`, since the remote is `github.com/bro2jo/leyenda` and README.md says Pages serves `main` /docs. The sandbox's proxy refused the connection (`CONNECT tunnel failed, response 403`). I did not serve `docs/` locally either, because the repo's settings deny reading `docs/` (`.claude/settings.json` → `"Read(/docs/**)"`). So every screenshot below is a **mock**. I imported the builder's own drawing functions and `site.css`, rendered them with Playwright at 390×844 (DPR 1) and at 1280 px, and looked at the PNGs. Google Fonts did not load in the sandbox, so the screenshots use the fallback fonts (Georgia and system sans), not Grenze Gotisch or Alegreya. The mocks are saved in `/tmp/claude-0/-home-user-leyenda/3ab0bcd0-54e3-5141-9e6e-da851479d4f5/scratchpad/site_shots/`:
- `phone_part0-2.png`: the map, seals, dice, medallions, crests, rope, thread, art cards, embers, flames, sigils and glyphs.
- `mock_part0-2.png`: the Now plate, companions, a character hero with portrait tabs, relationships, roster cards, a Codex row with its picture, the wear strip and the lookbook.
- `desk_map.png`: the map at desktop width.
- `sheet_chars.png` and `sheet_other.png`: contact sheets of the art.

Line references are to files in the repo at the time of reading.

## Inventory: every page type and visual element, what story information each carries, and how it is gated

### Takeaway
The site is a single dark 640 px column, built as static HTML. About 37 pages fall into ten types: Now, Chronicle index, chapter, Tales index, tale, Characters roster, character page, Darrow's page, Wardrobe and Collection, and Codex.

Its visual vocabulary has two layers:
- **Painted pictures the author supplies.** These are portraits, place, faction and thing pictures, Art cards, full-body "looks" and a painted map base. They are painterly AI fantasy art, and every one is gated by whether the page has shown its subject.
- **Line drawings the builder draws in SVG, in brass.** These are tier seals, level crests in rank metals, faction sigils with personal marks, attribute medallions, a d20, the Knot rope, the Tether thread, rank rings, mood embers, braziers, keepsake marks, tally marks and about 30 small glyphs.

These drawings carry almost all of the game state and progress. The painted pictures carry identity and place. Audio is four songs, played from the Codex and from inline play buttons where the prose sings their lines.

### Cited Findings

**Site-wide shell**
- **Navigation.** Six nav links (Now, Chronicle, Tales, Characters, Darrow, Codex) sit in a sticky masthead with the wordmark "The Unkneeling" in the display font. The masthead slides away while reading down and returns on the way up. The footer carries the motto "What is given can be taken. What is built is yours." — [engine/build_site.py L1570–1628](engine/build_site.py); [engine/site/site.js L28–47](engine/site/site.js)
- **Dark only, by design.** The stylesheet opens with "Dark only, by choice: a forge at night." The palette is night #0F1217, plate #161B22, ink #E8E2D4, brass #CFA65F, ember #E2713B, plus a six-step "temper" ramp (t1–t6, from pale gold through ember and violet to blue). `color-scheme: dark` is set, and there is no light theme — [engine/site/site.css L1–14](engine/site/site.css); [engine/build_site.py L718–722](engine/build_site.py)
- **Fonts.** Grenze Gotisch (display, a blackletter) and Alegreya Sans and Alegreya Sans SC (body and labels) load from Google Fonts. These are the only external resources the pages load — [engine/build_site.py L1572–1573](engine/build_site.py)
- **Column width.** The whole site is one column at most 640 px wide (`.wrap{max-width:640px}`), on desktop too — [engine/site/site.css L22](engine/site/site.css)
- **Favicon.** A brass-rimmed shield with a rope and an ember knot — [engine/build_site.py L4291–4294](engine/build_site.py)
- **No social card.** There are no Open Graph or Twitter image tags, no theme-color and no web manifest (a grep for `og:`, `twitter:`, `theme-color` and `manifest` finds none) — [engine/build_site.py L1596–1628](engine/build_site.py)

**Now page (`index.html`).** The order is: level-up banner, "New in the Wardrobe" banner, the Now plate, the open choice, the quest, "With him", the Reckoning card, the tales, the map, the last answered choice, the dice — [engine/build_site.py L3690–3790](engine/build_site.py)
- **Now plate.** It shows the Book line, "Chapter N — Title", an *open* (dashed-rim) wax seal for the chapter's tier so far, Where and Season, "Just happened", and a Continue reading button. The picture of the current place sits behind the plate at 16% opacity, fading downward, **only when that place has a picture on the page**. The current place has none today, so the plate is plain — [engine/build_site.py L3711–3718, L3792–3802](engine/build_site.py); [engine/site/site.css L452–455](engine/site/site.css); the registry check: the current place has no `image`.
- **Quest log.** A pennant glyph, the quest name, the objective in the page's words, a crossed-swords row for "What he is fighting", and "Work in hand" with diamond pips — [engine/build_site.py L3719–3728](engine/build_site.py)
- **With him.** Each companion card has a round portrait with the level crest pinned to its corner, a mood-ember glyph with its regard word (devoted, fond, wary…), a regard bar that never shows a number, and their last-seen line. Five companions show today — [engine/build_site.py L3750–3763, L826–835](engine/build_site.py)
- **Reckoning card.** Darrow's round portrait (86 px) or his crest, his level and rank, HP and Proficiency chips with glyphs, Inspiration as four-point "sparks", Bearing, Tether and Works chips, the XP bar in ten segments, four attribute medallions, the Ember bar with a brazier and tier ticks, and the Knot rope with the next Knot named — [engine/build_site.py L3764–3778, L3678–3688](engine/build_site.py)
- **Level-up banner.** For three days after a level: the crest in the rank's metal, with one shine sweeping across — [engine/build_site.py L3804–3816](engine/build_site.py); [engine/site/site.css L474–482](engine/site/site.css)
- **Dice.** The last five checks, each with a d20 glyph coloured by its outcome and lit on a natural 20 or 1, the stat and DC tag, a result badge, a fold with the arithmetic, and where in the story it was cast — [engine/build_site.py L3640–3676, L850–864](engine/build_site.py)

**The map** (on the Now page)
- **What it is.** An SVG with a 400×300 viewBox. Today's base is a **painted map picture**: `places.json → base_image`, `saga/art/maps/painted.webp`, 1600×1073, 108 KB. Without one, the builder draws the terrain itself, deterministically: coast, peaks with snow and hatching, forest with scalloped edges, rivers that widen downstream, moor tufts, and a stippled "grey waste" left unlabelled — [engine/build_site.py L951–1209, L1097–1104](engine/build_site.py)
- **What goes over it.** Roads, a brass double-rule frame with corner diamonds, and a compass rose — [engine/build_site.py L1086–1095, L1212–1222](engine/build_site.py)
- **Markers and labels.** Each kind of place has its own marker (a walled town with a spire, a hall with a bell tower, a jetty, a dot). Labels come in four styles: settlements in small capitals, regions in spaced capitals, water in italic blue, roads in italic tan — [engine/build_site.py L1270–1302](engine/build_site.py); [engine/site/site.css L433–440](engine/site/site.css)
- **Story state on the map.** A place's dot is grey before he has been there and brass once visited. The current place is ember with a pulsing ring. The route is an ember dashed line drawn leg by leg: the current leg bright, earlier legs (an earlier Book's road) fainter. A place the page has named links to its Codex entry. A legend reads "Darrow / visited / not yet / the road so far" — [engine/build_site.py L1256–1307, L3784–3787](engine/build_site.py); [engine/site/site.css L421–448](engine/site/site.css)
- **Today's counts.** All 17 places in `places.json` are `on_page`, 11 are visited, and the route has 2 legs — registry count, `saga/state/places.json`

**Chronicle index (`chronicle/index.html`)**
- A plate with Continue reading. Below it, a "Timeline" rail: one unbroken line down each Book, with a knot per chapter (the current chapter's knot in ember, pulsing). Book rows are text-only headings. Each chapter's line shows a small tier seal (once closed), its scene and Between counts and an approximate word count. A fold lists its scenes, each with a glyph for its kind (scene, between, interlude, climax, choice) — [engine/build_site.py L2566–2598](engine/build_site.py); [engine/site/site.css L196–231](engine/site/site.css)

**Chapter page (the reader)**
- **The head.** A Book line in small capitals (on a Book's first chapter), the title in blackletter, a 44 px wax seal for the closed tier, and a "Previously" box (the prior chapter's recap). The epigraph is set in italics with its source and, if it sings a song's line, a play button — [engine/build_site.py L2480–2500](engine/build_site.py)
- **There is no header picture or illustration in any chapter.** The builder has no image slot in the chapter template — [engine/build_site.py L2480–2531](engine/build_site.py)
- **The body.** Each block (scene, Between, interlude, climax, choice) folds under a heading carrying its glyph. On the current chapter the newest two blocks are open; on any other chapter, the first. Betweens are indented on a side rule and set smaller. A thin brass-to-ember reading-progress bar runs at the top. An "AA" text-size control offers four steps — [engine/build_site.py L2502–2519](engine/build_site.py); [engine/site/site.css L562–599](engine/site/site.css); [engine/site/site.js L19–27, L48–94](engine/site/site.js)
- **Devices inside the prose:**
  - The in-world "⟦ THE RECKONING ⟧" box, brass-bordered with pale-gold text.
  - Dice checks collapsed to one line: a d20, the stat and DC, the total, the result, and "✦ cast ×2" for an Inspiration reroll. Tapping opens the arithmetic.
  - The choice heading with its fork glyph, and the options in a brass-bracketed "decision" frame. The taken option is marked "chosen" with a check glyph, plus "answered for himself" when the default answered it.
  - `* * *` drawn as a ✶ ✶ ✶ ornament.

  [engine/build_site.py L2386–2478](engine/build_site.py); [engine/site/site.css L599–630](engine/site/site.css)
- **Name previews.** The first mention in a block of a character, a place or faction on the page, or a Codex thing becomes a dotted-underlined link. Hovering, or a first tap on a phone, shows a preview card: a round face crop for a person (name and epithet only) or a 16:9 picture for a place or thing, a title, and one line. The second tap follows the link — [engine/build_site.py L2229–2357](engine/build_site.py); [engine/site/site.js L171–229](engine/site/site.js); [engine/site/site.css L632–648](engine/site/site.css)
- **Foot.** A row of "On the page in this chapter" chips (names only) and a previous/next pager — [engine/build_site.py L2520–2529](engine/build_site.py)
- **Volume today.** A prologue and 7 chapters, roughly 5k to 24k words each. The busiest chapter has 7 scenes and 14 Betweens. Six chapters are closed: one Costly, one Triumph, four Hard-won — registry count, `saga/chronicle/*.md` headings, `saga/state/chapters.csv`

**Tales (`tales/index.html`, `tales/<slug>.html`)**
- Text only. Each tale shows its title, an italic "when it is set" line, its pieces and "N of M told". The tale page ends with "What this tale left" (the keepsake in words) and its cast chips. Today there are 3 tales — [engine/build_site.py L3835–3890](engine/build_site.py)
- On character pages, tales appear as a **keepsake shelf**: one slot per keepsake, drawn with a line mark (knot, cup, coin, word, cord, hand, bell…). A pending tale shows a dashed "?" ring and diamond "told marks". Blank dotted slots fill out the row, on a leather ledge — [engine/build_site.py L2729–2756, L867–891](engine/build_site.py); [engine/site/site.css L664–676](engine/site/site.css)

**Characters roster (`characters/index.html`)**
- Filter chips by faction and status, then a grid of cards. Each card has a round portrait with a level crest (the crest only when Darrow's Eye reads that person; a crest with a violet "?" for unread, a blue dash for borrowed strength), the faction's shield as a 7% watermark, name, epithet, a status badge (only if not alive) and "Last seen: Chapter N · Scene M". "The fallen" sit in a separate brass-tinted memorial grid — [engine/build_site.py L2853–2886, L912–922](engine/build_site.py); [engine/site/site.css L512–528](engine/site/site.css)

**Character page (`characters/<id>.html`)**
- **Identity plate.** Framed in the metal of the person's rank, with rivets. A square portrait (about 34vw on a phone, 200 px wider) has the level crest pinned to its corner. With earlier portraits the frame swipes between them, and tabs (e.g. "Book II" / "Book I") sit underneath. Then name, epithet, the faction sigil (faction device over a personal mark) and the fine print "Only what the story has shown so far." A fallen character gets a large sigil "in memory" instead of a portrait — [engine/build_site.py L2660–2692, L1914–1944](engine/build_site.py); [engine/site/site.css L258–286](engine/site/site.css)
- **Sections, all in words.** Appearance, Now ("Last seen"), Story so far, Quote, Relationships, the Reckoning, Known facts (folded, each with its scene link), Keepsakes, and Appearances (scenes grouped by chapter, "named" marked) — [engine/build_site.py L2777–2825](engine/build_site.py)
- **Relationships.** Each is a label and a note in words. For a companion, a first row "Toward Darrow" carries a mood ember and a regard bar with no number — [engine/build_site.py L2798–2811](engine/build_site.py)
- **Reading another person's Reckoning.** What Darrow can see is gated by the rank of his "Warden's Eye" Art. Rank I shows level and rank, II the attribute medallions (tinted earned brass, borrowed blue or unlit grey) and the fire as a brazier, III their Arts, IV "deeper" lines. Anything else shows "⟦ unread ⟧" in violet — [engine/build_site.py L2601–2645](engine/build_site.py)
- **Coverage today.** 19 character files: 18 have a portrait (the one without falls back to a sigil). 6 have a Book I and a Book II portrait, and 6 use `portrait_zoom` for their round copies — registry count, `saga/characters/*.json`
- **Text volume.** Major characters carry 13 to 158 known facts. Darrow carries 398 facts and 115 appearances. All of it is text — registry count, `saga/characters/*.json`

**Darrow's page (`darrow/index.html`)**
- **Plate.** Portrait with crest, name, "the Faithless" chip, the epithet chip once one is spoken, and the faction shield beside his title. Across the foot: rank and XP, the XP bar in ten segments (it names the rank the next level opens), the Ember bar with brazier and effect line, and Inspiration sparks — [engine/build_site.py L2660–2720](engine/build_site.py)
- **The Reckoning (always open).** A "Wearing" strip (64 px, 2:3) on a phone. From 560 px up, a full-length figure of his current look stands beside the numbers. Then chips, and four attribute tiles. Each tile is a medallion whose arc runs the score's share of "the Knight Who Fell" (his old self), closing in ember once passed, with a temper bar and text such as "temper … · next at …" — [engine/build_site.py L2889–2931, L1330–1366](engine/build_site.py); [engine/site/site.css L326–348](engine/site/site.css)
- **The Binding.** A seven-knot rope, tied knots filled with the temper gradient and "heating" in sequence. Under it a finer ember thread for the Tether: stages named only once reached. Then a list of the Knots, each with what it proves and "opens Book N" once tied — [engine/build_site.py L3033–3044, L1312–1327, L1398–1419](engine/build_site.py)
- **Folded panels:**
  - Arts, by tree, each tree with its own glyph (sword, footprints, breath, looped rope, eye, stone in flight). Each Art row has a card picture in its rank's metal, a rank ring, a status line ("rank II · next at N days (M so far)", or "sealed until Knot IV" with a lock), and its effect.
  - Bearing: four axes as a brass marker on a line with pole words and "even / leans X / named X", plus the epithet.
  - Chapters: a list with tier seals.
  - Then Now, Story, What he keeps, Appearance, Quote, Relationships, Known facts, Appearances.

  [engine/build_site.py L2933–2998, L3584–3617](engine/build_site.py); [engine/site/site.css L304–315, L368–401](engine/site/site.css)
- **Art cards.** The frame metal climbs iron, bronze, steel, silver, gold for ranks I–V, gaining studs at III, a second rule at IV and a glow at V. A sealed Art goes grey with a lock. Before its first rank, a dashed blank shows the tree glyph — [engine/build_site.py L2980–2997, L909](engine/build_site.py); [engine/site/site.css L374–397](engine/site/site.css)

**Wardrobe and Collection (`darrow/wardrobe.html`, `darrow/collection.html`)**
- **Wardrobe.** A 2:3 "stage" (a warm radial gradient) shows the chosen look, painted, or "Not painted yet". "What he wears, and why" lists each piece with its reason. Below come the lookbook grid of painted looks, then the **Forge**: five steps (Who's in the picture, The pose, In his hands, Him, What he wears), each a picker of cards or chips. Locked pieces are greyed with a lock and "Opens: …", "New" tags mark recent pieces, and hidden pieces are only counted. Last, "Paint it": a copy or share of the image prompt, numbered reference pictures to download, and the "Look line" — [engine/build_site.py L3333–3486](engine/build_site.py); [engine/site/forge.js L1–153](engine/site/forge.js)
- **Wardrobe counts.** 11 categories and 104 pieces in all; 11 are hidden until they open; 9 sets; 9 Collection ranks; 2 reference pictures. 8 looks are filed and 0 is set as "wearing", so the newest is shown — registry count, `engine/wardrobe.json`, `saga/state/looks.json`
- **Collection.** His rank in large display type, "N of M pieces", a bar toward the next rank, and the ranks as a rail of knots (his own in ember, pulsing). Then the sets: name, about, pips, a brass-knot seal once whole. Then a folded shelf per category: tiles with reason and chapter, locked tiles dashed, hidden pieces counted with a "?" — [engine/build_site.py L3488–3551](engine/build_site.py); [engine/site/site.css L827–861](engine/site/site.css)

**Codex (`codex/index.html`)**
- **Layout.** A jump bar of glyph chips, then numbered rows that fold open: Places (split into "Where he has been" and "Named, not yet reached"), Factions, Sayings, Things, Beasts, Songs and verses, Histories. A row with a picture shows a 56×32 thumbnail. Opened, the picture runs full width at 16:9 with a caption and "Tap to enlarge". A song row carries ♪ and, opened, the browser's own audio player. A faction entry shows its line-art sigil beside the description — [engine/build_site.py L3905–3964, L1980–2007](engine/build_site.py); [engine/site/site.css L233–257](engine/site/site.css)
- **Picture and song coverage today:**
  - places: 5 of 17
  - factions: 1 of 8 (all 8 have a drawn sigil device: lance with numeral, bell, censer, crown, red hand, knee)
  - Codex things: 1 picture across the "Places and things" list of 79 entries (some of those are skipped as places or people)
  - songs: 4 audio files for the 6 "Songs and verses" entries
  - Sayings (34) and Histories (5): text only

  registry count, `saga/state/{places,factions,codex_art}.json`, `saga/state/codex.md`

**Audio**
- **Play buttons in the prose.** A small pill play button follows the first linked mention of a song's name, or ends the first block that sings one of its quoted lines (once per scene). The button fills as the song plays. One song plays at a time. While the playing button is off screen, a dock keeps pause and stop at the bottom — [engine/build_site.py L2009–2029, L2346–2355](engine/build_site.py); [engine/site/site.js L230–302](engine/site/site.js); [engine/site/site.css L686–706](engine/site/site.css)
- **The files.** Four MP3s, 300 KB to 1.6 MB. The lore skill says they are made with Suno from the entry's exact lyrics — [saga/art/songs/](saga/art/songs/); [.claude/skills/lore/SKILL.md L33](.claude/skills/lore/SKILL.md)

### Inferences
- **Two visual languages.** The SVG line art is consistent: brass strokes, round caps, the colours drawn into each SVG. It carries the "game" (tiers, levels, knots, regard, rolls). The painted art carries "who" and "where". Most narrative events (a scene, a choice, a revelation, a Book turning) have no picture at all.
- **Pictures are reached through other pages.** The richest picture surfaces are the character pages and the Codex. The pages read most (chapters) show pictures only through hover or tap previews on linked names.

### Gaps
- I could not see the live pages. What the live `docs/` actually shows today (for example whether the last build matches `main`) is unverified; everything above is from the code and registries that build it.
- I did not open the Grenze Gotisch font, so how the blackletter headings read on a phone is not judged; the mocks fell back to Georgia.

## The art pipeline: who makes the pictures, how they are filed, sized, thumbnailed and checked, the Forge, and what the build refuses

### Takeaway
All pictures and songs are made outside the repo by the author (the player). Looks and songs have documented generative workflows: ChatGPT/OpenAI image generation for looks, Suno for songs. Portraits, places, Art cards and the map have no prompt builder or style anchor in the repo.

Claude files each picture by setting fields in a registry file. Tooling then:
- makes 256 px and 640 px WebP copies (`thumbs.py`);
- for looks, keys out a chroma screen and cuts the picture to 2:3 (`looks.py`);
- in the build, enforces type, size, alt text, on-page gating, naming and lyric checks.

Spoiler safety for images is enforced only by whether the subject is on the page. The picture's content is checked by convention, not by code.

### Cited Findings
- **The author supplies the art.** "Images and songs the user supplies for the Chronicle's public site… a picture may show only what the page has already put on the page, and a song may sing only what the page has already sung." — [saga/art/README.md L3](saga/art/README.md)
- **How each kind is filed:**

  | Kind | Where it lives | How it is attached |
  |---|---|---|
  | Place | `places/<id>` | `image`, `image_alt`, `image_caption`, `image_focus` in places.json |
  | Faction | `factions/<id>` | the same fields in factions.json |
  | Codex thing | `codex/<slug>` | via `codex_art.json`, keyed by the entry's bold name |
  | Song | `songs/<slug>.mp3` | via `codex_art.json` |
  | Art card | `arts/<art-id>` | found by file name alone |
  | Look | `looks/<id>` | an entry in looks.json |
  | Portrait | `characters/<id>` | `portrait`, `portrait_alt`, `portrait_focus`, `portrait_zoom`, `portrait_label`, `portraits_earlier` |

  [saga/art/README.md L5–19](saga/art/README.md); [saga/characters/README.md L28–36](saga/characters/README.md)
- **Portraits change by Book.** A new look for a new Book is `characters/<id>-bookN.jpg`. The old portrait moves into `portraits_earlier` and the frame swipes back to it — [saga/art/README.md L15](saga/art/README.md)
- **Sizing is by fixed frames, cropped, never stretched.** Places are 16:9 full width; portraits square (about a third of a phone's width, 200 px wider); Art cards square at 64 px; looks 2:3. `*_focus` ("X% Y%") picks the crop centre, and `portrait_zoom` (1–4) zooms the round copies onto the face — [saga/art/README.md L16](saga/art/README.md); [engine/build_site.py L1765–1774, L1892–1912](engine/build_site.py)
- **Thumbnails.** `engine/thumbs.py` makes `sm` (256 px) and `md` (640 px) WebP copies of every picture, with a SHA-1 manifest. The site uses `sm` for avatars, Codex rows and face previews, and `md` for portrait frames and place previews. The full file loads only when an entry opens or a picture is tapped. A stale or missing copy falls back to the full file with a note. `darrow.py ship` runs it before the build — [engine/thumbs.py L1–30](engine/thumbs.py); [engine/build_site.py L1752–1763](engine/build_site.py)
- **Cache-busting.** Every image link carries a short hash of its file, so a replaced picture shows at once — [engine/build_site.py L1735–1739](engine/build_site.py)
- **What the build refuses (pictures):**
  - a picture outside `saga/art/`, or not .webp/.png/.jpg
  - a missing file, a file over 3 MB, or missing alt text
  - a place or faction picture before it is `on_page`
  - a `codex_art` name that is not a rendered Codex entry, or is a Saying
  - a file in `arts/` named for no Art, or two pictures for the same name
  - a file in `looks/` that is neither a filed look nor a reference
  - a look whose pieces are unknown or clash
  - a `wearing` that is not an open look
  - a `portraits_earlier` entry without a label

  [engine/build_site.py L98–101, L1716–1739, L1776–1822, L1951–1966, L3193–3222](engine/build_site.py)
- **What the build refuses (songs):** audio that is not .mp3/.m4a/.ogg/.opus, a file over 10 MB, or **an MP3 whose embedded lyrics (ID3 USLT) contain any line the chronicle has not already sung** — [engine/build_site.py L1823–1858](engine/build_site.py)
- **A song made ahead waits GM-side.** It goes in with `saga.py songs add`, which keeps it under `_gm/`, and is released once the page sings every line — [saga/art/README.md L8](saga/art/README.md)
- **The Forge (looks only).**
  - The prompt template is "written for OpenAI's image generation". It asks for "Painterly fantasy concept art in the hand-painted style of Image 2… Vertical 2:3 portrait (1024 x 1536)… one solid, flat {screen} filling the whole frame".
  - `{screen}` is chroma blue #0000FF, or green #00FF00 when the design names blue.
  - Two reference images are attached in order: his face (Image 1) and the style and framing (Image 2).
  - On a phone, Share sends the prompt and the references to ChatGPT through the Web Share API.
  - The "Look line" (`Look: build=… pose=… · touches: …`) comes back with the picture.

  [engine/wardrobe.md "The prompt and the references"](engine/wardrobe.md); [engine/site/forge.js L143–151, L176–210](engine/site/forge.js); `engine/wardrobe.json → prompt`, `references`
- **Filing a look.** `engine/looks.py add` keeps a real alpha channel or keys out a flat chroma screen (it measures the edge colour and how flat the edge is), cuts the picture to 1024×1536 WebP, and refuses a painted backdrop, a checkerboard or a dark wash. It checks the Look line's pieces against `wardrobe.json` and the clash rules. `--drop X,Y` clears a separate stray piece. `--preview` writes the cut-out over the site's stage colour and over a contrasting colour for checking — [engine/looks.py L1–60](engine/looks.py); [saga/art/README.md L13](saga/art/README.md)
- **Wardrobe gating is code-enforced.** A piece opens on all of its conditions (a level, an Art rank, a Knot, a Tether stage the page has paid, a scene on the page). Hidden pieces stay off the site entirely until they can be worn. A set may never name a hidden piece. A `page` unlock must point at a scene already on the page, and a piece's `quote` is checked word for word against that scene. "Poses follow the Knots, so a look never shows the leg doing what the story has not let it." — [engine/build_site.py L3084–3183, L3301–3312](engine/build_site.py); [engine/wardrobe.md](engine/wardrobe.md)
- **The art on disk:**

  | Kind | Count and format | Size |
  |---|---|---|
  | Portraits | 24 JPGs, 512 to 2048 px square | 73 to 816 KB |
  | Places, faction, thing | 7 JPG or WebP at 1376×768 or 1672×941 | about 170 to 240 KB |
  | Art cards | 11 WebP, 768 or 1024 square | 41 KB to 2.3 MB (one card is 2.3 MB) |
  | Looks | 9 at 1024×1536, including 1 reference | 117 to 347 KB |
  | Painted map | 1, at 1600×1073 | 108 KB |
  | Thumbnails | 51 `sm` and 51 `md` copies | about 8 KB and 35 KB on average |

  measured with Pillow from `saga/art/` and `saga/art/thumbs/`
- **Style today.** The painted art is consistent: painterly, semi-realistic AI fantasy in a cold, muted palette (snow, stone, grey skies, firelight interiors). Framing varies, from head-and-shoulders close-ups to full figures in wide scenes; that is why `portrait_zoom` exists — contact sheets `sheet_chars.png`, `sheet_other.png` in the scratchpad's site_shots folder

### Inferences
- **No style lock outside the Forge.** Looks have a written style and two reference pictures; nothing equivalent exists for portraits, places, Art cards or the map. Consistency across those depends on the author repeating his own prompts. The current set looks coherent, but nothing enforces it.
- **The spoiler check on picture content is human.** The build can tell that a place is `on_page`, but not whether its picture shows something the prose has not (an unrevealed figure, a later season). The README rule ("a picture may show only what the page has already put on the page") is the only guard. MP3 lyrics are the one piece of media whose content is machine-checked.
- **Adding a new kind of picture is cheap.** Chapter headers, Book frontispieces, keepsake pictures or scene vignettes would follow the existing pattern: a folder, a registry field, `register_image`, the thumbs pass.

### Gaps
- Which image model or prompts made the portraits, places and Art cards is not recorded in reader-safe files. Only the looks' prompt and the songs' Suno route are documented.
- The 2.3 MB Art card shows only through its 256 px copy on the page, so it costs nothing until tapped. Whether that was intended is not stated.

## How the site shows change over time: portraits per Book, rank metals, Knots, the route, chapters and Books, the reader's progress

### Takeaway
Change over time is shown mainly by the brass SVG devices filling, lighting and changing metal:
- metal ladders for character rank and for Art rank;
- the seven-knot rope and the Tether thread;
- tier seals per chapter, open while the chapter runs;
- the map's route by legs (the earlier Book's leg fainter);
- the Collection's rank rail;
- "New" tags and a three-day level banner.

Pictures change only through per-Book portraits (6 characters have a Book I and a Book II portrait, swipeable) and through Darrow's growing lookbook. Books themselves have no visual identity beyond a text line. The site keeps no memory of what an individual reader has read.

### Cited Findings
- **Character rank as metal.** Seven metals, one per rank: iron, brass, steel, silver, ember, gold, white-gold. They tint the level crest, the portrait frame's edge, the plate's rivets, the Reckoning card's frame, the wear strip, the level-up banner and the Wardrobe and Collection plates — [engine/build_site.py L904–906, L2722–2727](engine/build_site.py); [engine/site/site.css L121–130](engine/site/site.css)
- **Art rank as a second metal ladder.** Iron, bronze, steel, silver, gold, plus studs, a second rule and a glow. Bronze rather than brass "so rank II never reads as gold"; violet is "kept for a tier above gold" — [engine/build_site.py L907–909](engine/build_site.py)
- **Art rank as a ring.** A segmented ring (filled segments for the rank, the next segment filling with practice); grey while sealed — [engine/build_site.py L746–767](engine/build_site.py)
- **The Knots.** The rope's seven knots fill with the temper gradient when tied and "heat" one after another on page load; a tied Knot shows "opens Book N" — [engine/build_site.py L1312–1327, L3033–3044](engine/build_site.py); [engine/site/site.css L403–418](engine/site/site.css)
- **The Tether.** A finer leather thread with five knots. Reached stages are lit ember and named with the page's word, and the next stage's length fills partially. Nothing shows before stage I — [engine/build_site.py L1398–1419, L3010–3025](engine/build_site.py)
- **Chapter tiers as wax seals.** Triumph is a sunburst, Hard-won a notched sword, Costly a tipped balance, Setback a cracked ring (brass for the good tiers, ember for the hard ones). A running chapter shows "so far" with a dashed rim — [engine/build_site.py L770–797](engine/build_site.py)
- **The route.** `places.json → route` is a list of place ids and waypoints, where `null` starts a new leg ("a Book's road; the legs before it are drawn fainter"). The build refuses a route that does not end at Darrow's place — [.claude/rules/chronicle.md](.claude/rules/chronicle.md) "After writing"; [engine/build_site.py L934–948, L1256–1261, L1676–1685](engine/build_site.py)
- **Portraits by Book.** The swipe frame defaults to the newest; the tabs read e.g. "Book II", "Book I". Avatars and previews show only the current portrait — [engine/build_site.py L1860–1890, L1930–1944](engine/build_site.py); [engine/site/site.js L148–170](engine/site/site.js)
- **Attributes against his old self.** Each medallion's arc runs the score's share of "the Knight Who Fell" and closes in ember once passed. The hint reads "The small number on each is who he was: the Knight Who Fell." — [engine/build_site.py L1330–1366, L2908](engine/build_site.py)
- **The Bearing.** A brass marker slides along four axis lines, with words only ("even / leans X / named X"); the epithet becomes a chip once spoken — [engine/build_site.py L3584–3609](engine/build_site.py)
- **Regard.** A companion's regard is a bar plus an ember glyph: flame tongues by warmth, a halo at "devoted", a cracked cold coal at "hostile" — [engine/build_site.py L822–835](engine/build_site.py)
- **News banners.** "A new level" banner for three days; "New in the Wardrobe" for pieces opened this chapter or the one before; "New" tags in the Forge and Collection — [engine/build_site.py L1508, L3804–3832, L3225–3261](engine/build_site.py)
- **The Collection.** A rank ladder as a rail, the current rank pulsing; sets get a brass-knot seal when whole — [engine/build_site.py L3488–3534](engine/build_site.py)
- **Tales and works.** Tales show told-marks (diamonds lit per piece told) and a keepsake shelf whose blank slots show "the next one is in view before it is earned". Finished works are a tally-mark chip — [engine/build_site.py L2729–2756, L805–819, L3027–3031](engine/build_site.py)
- **Books.** A Book appears as a text line ("Book II — Title") on the Now plate, as a heading row in the Chronicle rail, and as `# BOOK …` printed as a small-caps line atop the chapter. There is no Book-specific colour, cover, emblem or map treatment — [engine/build_site.py L2486–2488, L2572–2574, L3711](engine/build_site.py)
- **The reader's progress.** There is a reading-progress bar per page, "Continue reading" (to the newest block, the same for everyone) and a "now" marker on the current chapter. Nothing records what a given reader has read. The text size is not kept ("nothing is kept"). Only the Forge's choice is saved, in `localStorage` — [engine/site/site.js L19–27, L48–50](engine/site/site.js); [engine/build_site.py L2551–2564](engine/build_site.py); [engine/site/forge.js L151, L212](engine/site/forge.js)
- **Story time.** Season appears as one text line on the Now plate. No visual shows weather, season or in-world date — [engine/build_site.py L3717](engine/build_site.py)

### Inferences
- **Progression is shown well; story arcs are not.** The site follows a LitRPG grammar: metals, rings, ropes, seals and bars show *mechanical* progression clearly, and in a consistent house style. Narrative change (a Book turning, a place changing, a companion's arc, a choice's consequence) is shown in words or not at all, apart from per-Book portraits.
- **Two metal ladders may confuse.** The character ladder and the Art ladder share names (iron, steel, silver, gold) but differ (brass vs bronze, plus ember and white-gold). A reader might read them as one scale.

### Gaps
- I could not see whether the rope's "heat" animation and the bar fills read as meaningful or decorative on a real phone, because the live site was unreachable.

## What reads well on a phone and what does not (density, contrast, tap targets, dark mode, image weight, numbers vs pictures)

### Takeaway
The layout is built phone-first. It is one 640 px column, with the masthead hiding on scroll, folds everywhere, text-size control, `sm` and `md` thumbnails, lazy full pictures, and colours that pass contrast. In the mocks, the plates, portraits, companions and lookbook read well at 390 px.

The weak spots are:
- the **map** (labels about 8.5 to 9.5 px on a phone, and tap targets that are only those labels);
- small **tap targets** on chips, portrait tabs and the nav;
- **text density** on character and Darrow pages (hundreds of facts and appearances);
- **Darrow's sheet**, which is mostly numbers;
- **chapters**, which have no picture at all.

Desktop adds almost nothing: the column stays 640 px. The one addition is the full-length look figure beside Darrow's numbers.

### Cited Findings
- **The map on a phone.** The map's text is sized in SVG units on a 400-wide viewBox: place labels 10.5, regions 9.5, small tspans 8, compass 8.5. At 390 px the map is about 358 px wide (a scale of about 0.9), so labels render at about 9.4 px, regions about 8.5 px and small tspans about 7 px. The page tells the reader "Tap a name on the map to read about the place." The phone mock shows the labels legible but small, with the route and markers clear — [engine/site/site.css L430–440](engine/site/site.css); [engine/build_site.py L3784–3787](engine/build_site.py); mock `phone_part0.png`
- **Tap target heights.** Estimates from the CSS:

  | Element | Height | Source |
  |---|---|---|
  | Chips (.78rem, 2 px padding) | about 23 px | [site.css L148](engine/site/site.css) |
  | Portrait-tab buttons (.72rem, 2 px padding) | about 20 px | [site.css L278](engine/site/site.css) |
  | Nav links (.8rem, 4 px padding) | about 28 px | [site.css L45–48](engine/site/site.css) |
  | Compact song button | 26 px | [site.css L695](engine/site/site.css) |
  | Text-size button | 38×34 px | [site.css L58](engine/site/site.css) |
  | Zoom-dialog close | 40×40 px | [site.css L286](engine/site/site.css) |
  | Codex rows | about 40 px | [site.css L236](engine/site/site.css) |
  | Forge picker rows and cards | larger | [site.css L758, L772](engine/site/site.css) |
- **Contrast** of the palette, computed with the WCAG luminance formula:

  | Colour | On night | On plate |
  |---|---|---|
  | ink | 14.5:1 | 13.4:1 |
  | dim | 7.3:1 | 6.7:1 |
  | faint (hints, captions) | 5.1:1 | 4.7:1 |
  | brass | 8.3:1 | |
  | ember | 5.9:1 | |
  | violet "unread" text | 5.7:1 | |
  | brass-dim (borders, strokes) | 4.0:1 | |
  | faint-stroke | 3.6:1 | |

  computed from [engine/site/site.css L2–7](engine/site/site.css)
- **Dark mode.** The site is dark only; no `prefers-color-scheme` light variant exists. `prefers-reduced-motion` stops the pulses, flicker, shine, rope heat and bar transitions — [engine/site/site.css L1, L708–716](engine/site/site.css)
- **Image weight per surface:**
  - Avatars, Codex rows and Art cards use `sm` copies (about 8 KB). Portrait frames and place previews use `md` (about 35 KB).
  - Every slide of a multi-portrait frame loads its `md` copy (not lazy).
  - The painted map loads whole (108 KB). The Wardrobe stage loads the full look (about 170 KB). Codex pictures load full (about 200 KB) with `loading="lazy"` inside closed entries.
  - Pictures carry width and height, so they reserve their space while loading.

  [engine/build_site.py L1914–1944, L1968–1998, L2980–2997, L3355–3357, L3779–3783](engine/build_site.py)
- **Numbers vs pictures on Darrow's page.** In the open area: rank and XP as a number pair and a segmented bar, an Ember number and bar, Inspiration pips, HP and Proficiency chips, and four medallions each with score, modifier, the old-self number and the text "temper … · next at …". The Arts panel lines read "next at N days (M so far)". The pictures there are the portrait, the wear strip or figure, and the Art cards (64 px, inside a folded panel). Everything else is SVG or text — [engine/build_site.py L2714–2720, L2889–2910, L2945–2963](engine/build_site.py)
- **Text density.** Darrow's page carries 398 known facts and 115 appearances (folded). Major companions carry 110 to 158 facts. Chapters run up to about 24k words, folded by block. Darrow's sections are folded panels with a one-line summary each — registry count; [engine/build_site.py L3046–3062](engine/build_site.py)
- **Fold behaviour.** Chapters fold by block and open the newest two; a link to a block opens it and the one before. Without JavaScript every page works, and the previews become plain links — [engine/build_site.py L2502–2519](engine/build_site.py); [engine/site/site.js L314–325](engine/site/site.js)
- **Phone breakpoints.** The attribute tiles drop to two columns at ≤440 px, the keepsake shelf to two wide, and the Ember/Inspiration row stacks. The nav tightens at ≤480 px and scrolls sideways at ≤370 px — [engine/site/site.css L47–48, L184, L315, L676](engine/site/site.css)
- **Portraits.** About 132 px square on a 390 px phone (`clamp(112px,34vw,200px)`), next to the name. In the mock it reads as a strong identity block with the crest overlapping its corner. The Book tabs under it are small — [engine/site/site.css L260–280](engine/site/site.css); mock `mock_part0.png`, `mock_part1.png`

### Inferences
- **Small targets.** Several tap targets (chips, portrait tabs, nav links, map labels) fall below the 24×24 CSS px minimum of WCAG 2.2's 2.5.8 (this is my general knowledge; I did not verify it in this session) and far below the 44 to 48 px platform guidance. On a phone, the map's place names are both the smallest text on the site and its only links to places.
- **Discovery vs study.** CLAUDE.md says he "wants to discover the mechanics, not study them". The chapter pages honour that: the only numbers in the prose are dice and Reckoning boxes. Darrow's page is where the mechanics are fully exposed ("next at …" thresholds, temper, practice days). That page is effectively the `/sheet` he asks for, but it is also the site's main picture of him.
- **No sense of place on the Now page.** The plate's place backdrop depends on the current place having a picture. 12 of 17 places have none, including today's, so the Now page often opens with no picture of where he is.

### Gaps
- No real-device measurement: actual tap areas, font rendering of the blackletter, scroll performance and network weight on the live site are unverified.

## Gaps: story elements with no visual support, and inconsistencies between art types

### Takeaway
The story's biggest units (chapters, climaxes, Books, tales) and most of its world (12 of 17 places, 7 of 8 factions, nearly all Codex things, all sayings and histories) have no picture. Relationships beyond Darrow's regard are words only. There is no visual timeline of events, no in-world calendar or season, no consequence or choice history beyond text lists, and no social-share image. The art types are consistent in style but inconsistent in aspect, size and framing. The site also runs two metal ladders and two depictions of Darrow (a head portrait and full-body looks).

### Cited Findings
- **Chapters and climaxes have no image slot.** The chapter head is Book line, title, seal, Previously, epigraph; the body is text and SVG devices only — [engine/build_site.py L2480–2531](engine/build_site.py)
- **Books** have no visual identity beyond text lines and the fainter route leg — [engine/build_site.py L2486–2488, L2572–2574](engine/build_site.py)
- **Tales** have no pictures; keepsakes are line marks and words — [engine/build_site.py L3835–3890, L881–891](engine/build_site.py)
- **Places.** 5 of 17 on-page places have a picture. The current place has none, so the Now plate shows no backdrop — registry count; [engine/build_site.py L3792–3802](engine/build_site.py)
- **Factions.** 1 of 8 has a picture; all 8 have a drawn sigil — registry count; [engine/build_site.py L894–901, L3941–3947](engine/build_site.py)
- **The Codex.** 1 picture across its many things and beasts; Sayings (34) and Histories (5) are text only; 4 of 6 songs and verses have audio — registry count, `saga/state/codex.md`, `saga/state/codex_art.json`
- **People.** 1 of 19 characters has no portrait (a minor one); a fallen character is shown by a sigil "in memory" — registry count; [engine/build_site.py L2675–2677](engine/build_site.py)
- **Relationships.** A label plus a note in words for each; a bar and an ember only for a companion's regard toward Darrow; no relationship graph — [engine/build_site.py L2798–2811](engine/build_site.py)
- **Timeline.** The Chronicle's "Timeline" is a list rail of chapters and scenes; per character, "Appearances" is a list. There is no in-world date, season graphic or event timeline. Choices appear as a "last answered choice" on the Now page and inside chapters; no page collects the choices or their consequences — [engine/build_site.py L2566–2598, L2758–2775, L3739–3749](engine/build_site.py)
- **Other points of view and scene kinds** are distinguished by a 14 to 16 px glyph (a moon for an interlude, two linked rings for a Between, a crown for a climax) — [engine/build_site.py L1424–1435, L2454–2462](engine/build_site.py)
- **Sharing.** No page carries an `og:image`, so a link shared to a chat app shows no picture — [engine/build_site.py L1596–1628](engine/build_site.py)
- **Inconsistent aspect and size:**
  - aspect: places, factions and things 16:9; portraits square; Art cards square; looks 2:3; the map 4:3
  - portrait source sizes: 512 to 2048 px
  - one Art card at 2.3 MB beside others at 41 KB
  - framing: close-ups vs wide scene shots (hence `portrait_zoom`)

  measured from `saga/art/`; [saga/art/README.md L16](saga/art/README.md)
- **Two ladders and two depictions.** The character metals and the Art metals overlap in name but differ in steps — [engine/build_site.py L904–909](engine/build_site.py). Darrow is shown both by a square head portrait (plate, avatar, previews) and by 2:3 full-body looks (Reckoning strip or figure, Wardrobe). The two are made by different processes (a supplied portrait vs the Forge's prompt) — [engine/build_site.py L2889–2931](engine/build_site.py); [saga/art/README.md L13–15](saga/art/README.md)
- **Painted art vs line art.** The painted art is semi-realistic, cold, muted and painterly. The SVG layer is flat brass line art in a heraldic idiom. They meet on the same plates (a portrait with a line-art crest pinned to it, a painted map with SVG labels and markers) — mocks `mock_part0.png`, `phone_part0.png`

### Inferences
- **Highest-leverage gaps.** Mapped against how the story is built, these would be:
  1. chapter or climax header art (the weekly unit the reader experiences);
  2. a Book-level visual identity (cover, frontispiece, colour or route treatment when a Knot opens a Book);
  3. pictures for the current place, so the Now page has a sense of place;
  4. a visual record of choices and consequences;
  5. relationship visuals beyond Darrow-centred regard.
- **The art style is already consistent enough** to extend, but there is no written style or prompt anchor outside the Forge that would keep new kinds of picture matching.

### Gaps
- I could not check which of these gaps the author has already planned; that would live in GM files I did not open.

## Hard constraints any recommendation must respect

### Takeaway
Any visual change must:
- go through the static, stdlib-only Python build and its checks;
- keep the public site story-only and spoiler-safe (gated by what the page has shown, with no real-world terms and no GM text or unrevealed names);
- respect the file limits (3 MB per image, 10 MB per song, with alt text);
- keep "every page works with JavaScript off";
- load nothing external beyond Google Fonts;
- never show approval or Bearing as numbers, or let a pose or picture show the leg doing what the Knots have not cleared;
- respect the player's wish to discover mechanics rather than study them.

### Cited Findings
- **The walls.** The site is public, built from `saga/` only and never `real/`. Anything the page has not spoken lives only under `_gm/` and never reaches the site. The build blocks every sentence of the GM `.md` files and every string of the GM notes and threads — [CLAUDE.md "Golden rules" 4](CLAUDE.md); [.claude/rules/chronicle.md "The site"](.claude/rules/chronicle.md)
- **What the builder may read** is a fixed list (the chronicle, characters, a few state files, rules.json, wardrobe.json, `saga/art/`). It never reads `real/`, `engine/deeds.csv`, `saga/bible/`, the events, or `_gm/` — [engine/build_site.py L4–35, L102–104](engine/build_site.py)
- **Forbidden words.** The build fails on real-world terms anywhere in the output (pages, CSS and JS included): calories, protein, rehab, therapy, surgery, ligament, reps, squat, bike, exercise, workout, gym, sport(s), PT, ACL, RPE and others. Any new UI label or alt text must avoid them — [engine/build_site.py L3997–4002, L4118–4125](engine/build_site.py)
- **Names and sentences.** Unrevealed names and GM sentences fail the build. Allowed words include place and faction names, Art, Knot, rank and Ember-tier names, the Tether's words, and the Bearing's poles. The epithet is allowed only once spoken — [engine/build_site.py L4126–4190](engine/build_site.py)
- **Links.** Every internal link and anchor must resolve — [engine/build_site.py L4191–4220](engine/build_site.py)
- **The build is all or nothing.** It builds into a temporary directory and replaces `docs/` only when every check passes. `docs/` is never edited by hand — [engine/build_site.py L4297–4342](engine/build_site.py); [CLAUDE.md "Where things live"](CLAUDE.md)
- **Stack.** "Standard library only (Python 3.9+). Plain HTML + one stylesheet + a little JS; every page works with JavaScript off." The scripts are three files published as they are — [engine/build_site.py L70](engine/build_site.py); [engine/site/site.js L1](engine/site/site.js)
- **Media limits.** Images: .webp/.png/.jpg, at most 3 MB, alt text required, under `saga/art/`. Audio: at most 10 MB, with embedded lyrics restricted to lines already sung. Thumbnails need Pillow; looks need Pillow and numpy — [engine/build_site.py L98–101](engine/build_site.py); [engine/thumbs.py](engine/thumbs.py); [engine/looks.py L13](engine/looks.py)
- **Spoiler gating by content.** "A picture may show only what the page has already put on the page"; "A portrait shows only what the page allows: a character not yet seen has no portrait"; place and faction pictures only once `on_page` — [saga/art/README.md L3, L14](saga/art/README.md); [engine/build_site.py L1776–1786](engine/build_site.py)
- **Wardrobe gating.** Hidden pieces stay off the site and out of sets; poses are gated by the Knots, so pictures never run ahead of the knee — [engine/wardrobe.md](engine/wardrobe.md); [engine/build_site.py L3164–3176, L3301–3312](engine/build_site.py)
- **Numbers.** Approval is "never shown as a number" (a bar and words), and the Bearing is "rendered in words only". Game numbers appear in the prose only inside Reckoning boxes and dice lines — [engine/build_site.py L59–62, L1480–1490](engine/build_site.py); [saga/bible/style.md §1 L34](saga/bible/style.md)
- **The story never leads the knee.** The story never sets targets or advances past what the PT has cleared, and Darrow can't run in the story until the user is cleared — [CLAUDE.md "Golden rules" 1](CLAUDE.md); [README.md "How real life becomes story"](README.md)
- **Discovery, not study.** "He wants to discover the mechanics, not study them. Never explain which deed feeds which stat, Art, Ember or the week's tier, or what is close to unlocking, unless he asks (`/sheet` is asking; the Wardrobe's greyed pieces name what opens them…)" — [CLAUDE.md "What the user sends"](CLAUDE.md)
- **Visual commitments already made:**
  - dark only by choice;
  - colours written into each SVG so drawings render right under a stale stylesheet;
  - reduced motion honoured;
  - the "Only what the story has shown so far." fine print in place of disclaimers

  [engine/site/site.css L1, L708–716](engine/site/site.css); [engine/build_site.py L716–717, L1509](engine/build_site.py)
- **The author's tools.** The art comes from the player using outside tools: ChatGPT/OpenAI image generation through the Forge, and Suno for songs. Claude files it — [engine/wardrobe.md](engine/wardrobe.md); [.claude/skills/lore/SKILL.md L33](.claude/skills/lore/SKILL.md)

### Inferences
- **Recommendations should be phrased as registry fields plus builder changes.** A visual recommendation is realistic if it can be expressed as:
  1. a new registry field or folder under `saga/art/`, gated on an on-page key (a chapter code or scene key, like the Wardrobe's `page` unlock);
  2. a static SVG or CSS treatment in `build_site.py` and `site.css`;
  3. optional JS that degrades to plain links.

  Anything needing a runtime service, client-side data fetching beyond static files, or external scripts or CDNs breaks the current design.
- **Generated pictures need a content check.** Any picture made by an image model must be checked by a person for spoilers (it may show a future place, person or season) and for real-world leaks (for example gym equipment), because the build checks only the file and its gating, not what it depicts.
- **The cost lands on the player.** Every new picture kind adds to his own time, since he makes the images himself. Recommendations that reuse the existing kinds or are generated in SVG cost him nothing.

### Gaps
- Whether GitHub Pages bandwidth or repo size is a practical limit is not stated in the repo (the build limits single files only). The art folder is about 21 MB today, measured with `du`.
