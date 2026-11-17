# The Chronicle's public site as it actually renders: a live audit (November 2026)

Scope and method. This audit checks the earlier code-only audit (`/home/user/leyenda/research_notes/Visual storytelling for the Chronicle/this_site_current_visuals.md`) against the live site at https://bro2jo.github.io/leyenda/. It measures what that audit could only estimate, and adds what only the real pages show.

**What I did:**
- Loaded every page type in headless Chromium (Playwright): Now, the Chronicle timeline, chapter 7 (newest) and chapter 1 (early), the Tales index and Tale 1, the Characters roster, Ser Hollis Garrow (a character with Book tabs), Darrow's page, the Wardrobe, the Collection and the Codex. The map is on the Now page.
- Took each page at 390×844 (deviceScaleFactor 1, touch on), first screen and full page, and at 1280 px wide. Measured the DOM, logged every network response, then tapped, opened and swiped.
- Read the HTML of 17 pages raw with curl for metadata and audio markup.

**Labels.** Each finding is tagged **[measured on the live site]** or **[from code]**; the code is `engine/site/site.js` and `site.css`, read only for class names and behaviour. I did not open `docs/`, `real/` or any `_gm/` path. Mechanic numbers (XP, thresholds, DCs and the like) are described by structure, not copied.

**Screenshots** are in `/tmp/claude-0/-home-user-leyenda/3ab0bcd0-54e3-5141-9e6e-da851479d4f5/scratchpad/live_shots/`:
- per page: `<page>_phone_first.png`, `<page>_phone_full.png`, `<page>_desk_first.png`, `<page>_desk_full.png`
- contact sheets: `sheet_first_A/B/C.png` (phone first screens), `strip_<page>.png` (long phone pages cut side by side), `sheet_desk.png`, `sheet_interact.png`, `sheet_jsoff.png`
- interactions: `int_*.png`; JavaScript off: `jsoff_*.png`

Raw measurements (JSON) are in the scratchpad's `results/` folder.

**Caveats:**
- Network numbers are cold loads with an empty cache in desktop Chromium's engine with phone emulation, not on a real phone.
- The "throttled" runs use Chromium's network emulation (1.6 Mbps down, 150 ms latency) with no CPU slowdown.
- WCAG thresholds (24 px minimum, 44 px comfortable) are as set in the assignment. www.w3.org is outside this session's allowed network, so I could not re-read the criterion's exceptions; I applied them as I know them (see Gaps).

## Which of the earlier audit's claims hold, and which were wrong?

### Takeaway
Nearly all of the earlier audit holds on the live site:
- the layout, the page order, the devices, the absence of chapter pictures and social cards;
- the tap-size estimates, which landed within 1 px;
- the contrast ratios, which match to the first decimal.

Five claims were wrong or need correcting:
1. **Fonts.** The real fonts (Grenze Gotisch blackletter and Alegreya) do load. The earlier mocks only fell back to Georgia because of their sandbox.
2. **Avatars.** Zoomed portraits load 640 px `md` copies even as 48 px avatars, not the 256 px `sm` copies.
3. **Image sizes.** Not every picture carries width and height (but nothing shifts).
4. **Codex row taps.** A Codex row's tappable line is about 23 px tall, not about 40 px.
5. **The Codex's one non-place picture** sits under "Beasts and others", not "Things".

New on the live site: opening the Codex fetches about 1.65 MB of song audio before anyone presses play.

### Cited Findings

**Claims that hold**
- **One dark 640 px column on desktop too. Holds** [measured on the live site].
  - At 1280 px the main column measures 640 px, centred, with about 320 px of empty night on each side.
  - At 390 px it fills the width (358 px of text between 16 px gutters). There is no horizontal overflow on any page.
  - Sources: [Now](https://bro2jo.github.io/leyenda/); `sheet_desk.png`.
- **Sticky masthead that hides while reading down and returns on the way up. Holds** [measured on the live site]. On chapter 7 the masthead (wordmark row plus nav row, 96 px tall on a phone) moved to −96 px after scrolling down and back to 0 after a short scroll up — [Chapter 7](https://bro2jo.github.io/leyenda/chronicle/07-the-far-bank.html)
- **Google Fonts are the only external resource. Holds** [measured on the live site].
  - The stylesheet link asks for Grenze Gotisch 500/700, Alegreya Sans and Alegreya Sans SC, with `display=swap`.
  - The live pages fetch the woff2 files, Grenze Gotisch 41 KB among them. Headings and the wordmark render in the blackletter: page titles 27–34 px, section heads about 23 px.
  - The earlier audit's Georgia fallback was an artefact of its sandbox, not of the site.
  - Sources: [Now](https://bro2jo.github.io/leyenda/); `sheet_first_A.png`.
- **No social card. Holds** [measured on the live site].
  - None of 17 pages checked has `og:*`, `twitter:*`, `theme-color`, `manifest` or `canonical`.
  - Each page has a `<title>` such as "Now · The Unkneeling", plus a generic `description` such as "What is going on now in The Unkneeling." or "Chapter 7 of The Unkneeling: The Far Bank.".
  - The icons exist and return 200: `favicon.svg` (387 B), `favicon-32.png` (1.3 KB), `apple-touch-icon.png` (5.9 KB).
  - Source: curl of the live HTML of all chapters, tales, Codex, Darrow, Wardrobe and Hollis
- **Now page order and contents. Holds** [measured on the live site].
  - In today's state the order is: "New in the Wardrobe" banner, the Now plate, The quest, With him (five companions), The Reckoning card, The tales, The map, "A small choice" (answered), The dice. There is no level-up banner and no open choice today.
  - The plate has no place picture behind it: the current place has no picture, and 0% of the first screen is image.
  - Sources: [Now](https://bro2jo.github.io/leyenda/); `strip_home.png`.
- **Chapters have no picture. Holds** [measured on the live site].
  - Chapter 1 and chapter 7 contain zero `<img>` elements.
  - The head is: Book line on a Book's first chapter, blackletter title, tier seal, "Previously" box, italic epigraph, then folded block headings with their glyphs.
  - Sources: [Chapter 1](https://bro2jo.github.io/leyenda/chronicle/01-the-confessor-at-the-steps.html); [Chapter 7](https://bro2jo.github.io/leyenda/chronicle/07-the-far-bank.html)
- **Fold behaviour. Holds** [measured on the live site].
  - Chapter 7, the current chapter, opens with its newest 2 of 6 blocks open. Chapter 1 opens with 1 of 17 open.
  - The open state is written into the HTML: with JavaScript off, chapter 7 still opens with 2 of 6 open.
  - Source: `jsoff_ch07_first.png`
- **Name previews. Holds** [measured on the live site].
  - The first tap on an underlined name shows a card and keeps the URL. The second tap follows the link.
  - A person's card is 290×106 px, with a 72 px round face, name, epithet and "Open →". A place or Codex-thing card is 290×131 px and text only when the subject has no picture (Calden, Hob).
  - With JavaScript off, the first tap goes straight to the page.
  - Sources: `int_preview_person.png`, `int_preview_place.png`
- **Songs. Holds** [measured on the live site].
  - Pill play buttons appear in the prologue (1), chapter 4 (1) and chapter 5 (4). They sit inside folded blocks, so none is visible until its block is open.
  - Tapped, the button turns to a pause glyph and fills (`--p` reached about 15% after 2.5 s), so the song plays.
  - Scrolled away, a dock appears at the bottom with the song's pause control and a stop "×".
  - Sources: [Chapter 5](https://bro2jo.github.io/leyenda/chronicle/05-the-thornwild-woman-s.html); `int_song_playing.png`, `int_song_dock.png`
- **Portrait Book tabs and swipe. Holds** [measured on the live site].
  - The frame scroll-snaps between portraits, and the tabs follow: `aria-pressed` moved to "Book I" when the strip scrolled to the second slide. Tapping "Book II" scrolled back.
  - With JavaScript off the tabs are hidden and the strip still scrolls (`overflow-x:auto`). This matches the code comment "Without this file the frame still swipes and the tabs stay hidden" [from code: engine/site/site.js L148–149].
  - Note: Chromium's emulated touch gesture did not move the strip, so the swipe was driven by setting `scrollLeft` (see Gaps).
  - Source: [Hollis](https://bro2jo.github.io/leyenda/characters/hollis-garrow.html)
- **The map links to the Codex. Holds** [measured on the live site]. Tapping "Coldmere" on the map went to `codex/index.html#place-coldmere`, scrolled there and unfolded that row, picture and all — `int_map_after_tap.png`
- **Codex layout. Holds** [measured on the live site].
  - It has a jump bar of 7 glyph chips and numbered rows with a + sign. A row with a picture shows a 56×32 px thumbnail.
  - Opened, the picture runs at 356×199 px with a caption ending "Tap to enlarge", then the entry, then "First on the page: …".
  - The enlarge dialog shows the picture at 390×218 px on a phone, with a 40×40 px close button.
  - Sources: [Codex](https://bro2jo.github.io/leyenda/codex/index.html); `int_codex_coldmere.png`, `int_codex_zoom.png`
- **Darrow's look beside the numbers. Holds** [measured on the live site].
  - On a phone the Reckoning starts with a "Wearing" strip (358×114 px with a 64×96 px thumbnail).
  - At 1280 px a full-length figure stands to the left of the chips and medallions.
  - Sources: [Darrow](https://bro2jo.github.io/leyenda/darrow/index.html); `darrow_desk_first.png`
- **Every slide of a multi-portrait frame loads its `md` copy eagerly. Holds** [measured on the live site]. Both portraits load on Darrow's page (45 + 33 KB) and on Hollis's (50 + 44 KB), with no `loading="lazy"`.
- **Codex full pictures are lazy inside closed rows. Holds** [measured on the live site].
  - All 7 full pictures carry `loading="lazy"` and width and height attributes. None loads until its row opens.
  - Opening Coldmere fetched its 1376×768 JPG, 172.5 KB.
- **The Wardrobe stage loads the full look. Holds, with a smaller size** [measured on the live site]. The current look is the full 1024×1536 WebP, 127.5 KB (not about 170 KB), loaded eagerly and shown at 322×484 px on a phone — [Wardrobe](https://bro2jo.github.io/leyenda/darrow/wardrobe.html)
- **Counts. Hold** [measured on the live site].
  - The Codex reads "11 of 17 reached" (11 "Where he has been", 6 "Named, not yet reached").
  - Factions 8, Sayings 34, Songs and verses 6.
  - The roster shows 18 cards plus 1 under "The fallen". One card (Ser Oswin) shows a faction shield in place of a portrait.
  - Sources: `strip_codex.png`, `strip_roster.png`
- **JavaScript off: every page works. Holds** [measured on the live site].
  - Chapter 7, Now and Hollis render the same layout without JavaScript (same page heights within 35 px).
  - The text-size button and the portrait tabs are hidden. Previews become plain links.
  - Source: `sheet_jsoff.png`
- **Contrast table. Holds to the first decimal** [measured on the live site, computed from rendered colours]:

  | Text colour | On night | On plate |
  |---|---|---|
  | faint | 5.09:1 | 4.69:1 |
  | dim | 7.28:1 | 6.72:1 |
  | ember | 5.95:1 | |
  | violet ("hollowed") | 5.67:1 | |
  | brass | 8.29:1 | |

  New: the red "fallen" badge is 4.98:1.

**Claims that were wrong or need correcting**
- **Correction: avatars do not all use `sm` copies** [measured on the live site].
  - The five companions on the Now page, and Darrow's Reckoning portrait, load 640 px `md.webp` copies of 34–70 KB each. Their `<img>` carries width and height of 48 (86 for Darrow), and the element renders at 92–205 px.
  - On the roster the same six zoomed portraits load `md`, while unzoomed ones load 256 px `sm` copies (56×56).
  - On the Now page these six portraits are about 290 KB of the page's 399 KB of images. A person's preview card also loads the `md` copy (49 KB for Wren) to fill a 72 px circle.
- **Inference behind that correction** [inference from the live markup]: the zoomed round crop is drawn by scaling the image up inside a clipped circle. That is why the larger copy is chosen: the image box is bigger than the visible circle.
- **Correction: not every picture carries width and height** [measured on the live site]. These have none:
  - the Wardrobe stage look;
  - the 8 lookbook tiles;
  - the "Who's in the picture" faces;
  - the Codex row thumbnails.

  But cumulative layout shift measured 0 on the Now, Wardrobe, Codex, Darrow and roster pages, so CSS frames reserve the space and nothing jumps.
- **Correction: Codex rows are not about 40 px tap targets** [measured on the live site].
  - A one-line row looks about 42 px tall, but the tappable `<summary>` is 358×22.7 px. Two-line rows reach 68 px.
  - The same pattern recurs: the Chronicle's scene-list folds are 20–22 px tall, the Now page's "the roll" folds 18.5 px, the Wardrobe's "How it works" 19 px, and "What the page has shown (N)" on a character page 20.9 px.
- **Correction: the Codex's non-place picture is under "Beasts and others"** [measured on the live site].
  - "Things" lists 75 entries with no picture. The one picture of that kind (Thistle) sits under "Beasts and others" (1 entry).
  - The 7 Codex pictures are: 5 places (Saint Ysolde's, the winch-house, Coldmere, the Lowmarch, Harrow Ford), 1 faction (the Confessors) and 1 beast.
- **Not in the earlier audit: the Codex loads song audio on open** [measured on the live site].
  - The four `<audio controls preload="metadata">` players are the Codex's song players. Even so, Chromium fetched three of the MP3s almost whole as the page opened: 729 KB, 624 KB and 300 KB. It started and aborted the fourth (1.6 MB).
  - As a result, the Codex weighs about 1.86 MB on open, against 0.13–0.66 MB for every other page.
  - Sources: [Codex](https://bro2jo.github.io/leyenda/codex/index.html); curl `HEAD` of the four MP3s: 307,748 / 746,625 / 639,486 / 1,613,028 bytes.
- **Map label sizes. Close, slightly larger than estimated** [measured on the live site]. The map renders 374×281 px on a 390 px phone (scale 0.936, not about 0.9). See the next section for each size.

**Hover vs tap** [from code]. The earlier audit says previews open on hover on desktop; I tested only the tap path. Text size "is not kept": I saw the panel but did not test a reload with a changed size. Both rest on the code.

### Inferences
- **The earlier audit was reliable.** It was built from the builder's code and its own estimates, and the live build matches `main` closely enough that its inventory can be trusted. Its errors are in loading detail (which copy a zoomed avatar uses, missing size attributes, audio preload), which code reading tends to miss.
- **The live blackletter changes the judgement on headings.** At 27–34 px Grenze Gotisch reads clearly on a phone, and gives the site most of its period character. At 23 px block titles ("The Right Side of the Bridge", "Name the Load") it is still legible, but dense. It is never used below about 20 px, which is wise.

### Gaps
- The hover path for previews on desktop, the level-up banner (not present today), the open-choice block (none open today) and reduced-motion behaviour were not exercised.
- The rope's "heat" animation and the bar fills were seen only as still frames, so whether they read as meaningful on a real phone is still unjudged.
- Chromium's emulated touch swipe did not drive the portrait strip. The swipe-to-tab sync was verified by setting the scroll position in script, not with a real finger.

## Exact measured tap sizes, font sizes, page weights and image loading

### Takeaway
- **Tap targets.** Big story targets are generous: companion cards, roster cards, Forge rows, Collection tiles, pager and Wardrobe tiles all exceed 44 px. Most small controls sit between 18 and 29 px tall. Map links (9–22 px tall) and portrait tabs (20 px) are the clearest failures of the 24 px minimum as a size; they pass only through the spacing exception, or (map) mostly so.
- **Fonts.** Chapter prose is 18 px at about 50 characters a line on a phone, comfortable. On desktop it runs 88–93 characters a line.
- **Smallest text.** It is in the SVG devices: crest "LEVEL" at 2.8–4.5 px, medallion sub-numbers 6–8 px. Map labels run 8.8–10.2 px.
- **Page weight.** Pages weigh 135–660 KB cold, apart from the Codex (1.86 MB). Web fonts are 111–157 KB of every page, the largest single cost on text pages.

### Cited Findings

**Tap targets on a 390 px phone** [measured on the live site, `getBoundingClientRect`; "spacing" = whether an undersized target still clears a 24 px circle around its neighbours]

| Element | Width × height (px) | vs 24 px | vs 44 px |
|---|---|---|---|
| Nav links (6) | 26.8–67 × 28.5 | pass | fail |
| Wordmark link | 145 × 35 | pass | fail |
| Skip link (on focus) | 112 × 35 | pass | fail |
| Text-size "AA" button | 38 × 34 | pass | fail |
| Text-size panel "A" buttons | 46 × 40 | pass | fail (height) |
| Chapter foot chips ("On the page…") | 42–170 × 23.5 | under by 0.5; spacing OK | fail |
| Codex jump chips | 77–147 × 23.5 | under by 0.5; spacing OK | fail |
| Roster filter chips | 38–186 × 24.1 | pass, barely | fail |
| Portrait Book tabs | 43.6–46.7 × 20.4 | fail as size; spacing OK | fail |
| Chapter block fold headings | 328–358 × 21–64 | one-line Between headings 21 px | mostly fail |
| Dice fold in a chapter | 336 × 32 | pass | fail |
| "the roll" folds on Now | 375 × 18.5 | fail as size; spacing OK | fail |
| Codex row (tappable line) | 358 × 22.7 (two-line rows 68) | fail as size; spacing OK | fail |
| Chronicle scene-list folds | 344 × 20–22 | fail; 2 of 8 also fail spacing | fail |
| Chronicle chapter links | 344 × 23.2 | under by 0.8; 1 fails spacing | fail |
| Scene links in Chronicle folds, character "Appearances" | 82–257 × 15 | fail as size (list links, not inline) | fail |
| Inline name links in prose | 26–99 × 19 | exempt as inline text links | fail |
| Map place links (14) | 32–121 × 9–22 | all under 24 tall; 2 fail spacing | fail |
| Song pill in prose | 144 × 26 | pass | fail |
| Song dock: pause / stop | 144 × 30 / 28 × 28 | pass | fail |
| Zoom dialog close | 40 × 40 | pass | fail (barely) |
| Name preview "Open →" link | 180–264 × 18 | fail as size; alone in card | fail |
| Darrow page folded panels (11) | 356 × 47.9 | pass | pass |
| Companion cards (Now) | 375 × 81–121 | pass | pass |
| Roster cards | 358 × 95–174 | pass | pass |
| Wardrobe: look tiles, "who" buttons, picker rows, chips | 113 × 191 · 114 × 120 · 358 × 76 · 72–130 × 32 | pass | tiles, buttons, rows pass; chips fail height |
| Collection tiles / panels | 161–163 × 47–84 / 356 × 48 | pass | pass |
| Pager (prev/next) | 173 × 43–66 | pass | about 44 |

Sources: all pages listed above; raw groups in `results/<page>_phone_v2.json`.

**Font sizes as rendered** [measured on the live site]
- **Chapter and tale prose.** 18 px Alegreya Sans, line height 29.7 px (1.65), 358 px measure on a phone. The median line holds 49–53 characters, at most 57.
  - At 1280 px the measure is 608 px, and lines run 88–93 characters (median), up to 97.
  - Sources: [Chapter 1](https://bro2jo.github.io/leyenda/chronicle/01-the-confessor-at-the-steps.html), [Chapter 7](https://bro2jo.github.io/leyenda/chronicle/07-the-far-bank.html), [Tale 1](https://bro2jo.github.io/leyenda/tales/01-where-not-to-stand.html)
- **Other body text.** Codex entries and character prose are 16 px (line height 24–24.8 px, 52–58 characters a line on a phone, 85–90 at 1280). "Dim" secondary paragraphs are 14.7 px.
- **UI text.**
  - 12.5–13.8 px: chips, labels, "Last seen" lines, captions, the footer.
  - 12.8 px: nav links (small capitals).
  - 11.5 px: portrait tabs and Wardrobe counters.
- **Under 12 px (HTML):**
  - Collection tile sub-lines, 10.9 px. This is the largest body of small text, about 1,200 characters on the page.
  - "New" tags and "his look" tag, 10.6 px.
- **Under 12 px (SVG drawings):**
  - the word "LEVEL" on level crests: 2.8 px on Now-page and roster avatars, 4.5 px on the character-page crest (unreadable);
  - crest numerals 9.4–11.3 px;
  - on the Now-page Reckoning card, the attribute medallions' small "old self" numbers and modifiers at 6.4–6.8 px, and the rope's Knot numerals at 8.4 px;
  - on Darrow's page, the same medallion sub-numbers at 8–8.4 px and rank numerals at 7.2–8.1 px.
- **Map labels** (SVG, scale 0.936):

  | Label | Size | Style |
  |---|---|---|
  | Places | 9.8 px | ink |
  | Current place | 10.2 px | brass |
  | Regions | 8.8 px | the large region 10.2 px |
  | Roads | 9.3 px | italic tan |
  | Water | 9.3 px | italic blue |
  | Small "The" above a split label | 7.4 px | |
  | Compass "N" | 7.9 px | |

  Each label has a 3.6-unit dark halo (stroke drawn under the fill, about 1.7 px a side). Contrast against that halo is 13.0:1 for places, 7.4:1 for the current place, 8.5:1 for regions (6.5:1 for the large region), 7.1:1 for roads and 7.5:1 for water.
  Sources: [Now](https://bro2jo.github.io/leyenda/); `int_map_phone.png`

**Contrast of visible text** [measured on the live site]
- Every visible text pair on the 12 pages measured is at least 4.69:1. The lowest are faint text on a plate (the Collection's locked tile names, 10.9 px) and faint on night (5.09:1: hints, captions, footer, inactive Book tabs, "Last seen" lines).
- **Inside a closed fold** on the Now page (not visible in today's state), a "Critical Failure" result label is styled dim grey on night at 3.0:1. It would fail 4.5:1 if shown.

**Page weight, cold load, phone** [measured on the live site, Playwright response sizes; transfer bytes of bodies]

| Page | On open | After scrolling to the end | Images | Fonts | Phone height |
|---|---|---|---|---|---|
| Now | 588 KB, 17 requests | same | 399 KB (map 108 KB + six `md` portraits) | 157 KB | 4,542 px (≈5.4 screens) |
| Chronicle | 161 KB | same | 0 | 134 KB | 1,265 px |
| Chapter 7 | 194 KB | same | 0 | 157 KB | 14,990 px |
| Chapter 1 | 206 KB | same | 0 | 157 KB | 7,823 px |
| Tales | 135 KB | same | 0 | 111 KB | 990 px |
| Tale 1 | 187 KB | same | 0 | 157 KB | 11,128 px |
| Roster | 537 KB | same | 400 KB | 111 KB | 3,469 px |
| Hollis | 265 KB | same | 94 KB | 135 KB | 5,556 px |
| Darrow | 302 KB (328 KB at 1280) | same | 86 KB | 157 KB | 2,797 px |
| Wardrobe | 638 KB | 662 KB | 457 KB | 157 KB | 3,402 px |
| Collection | 164 KB | same | 0 | 135 KB | 4,553 px |
| Codex | 1,862 KB | 1,886 KB | 52 KB | 134 KB | 7,714 px |

The Codex's other 1,654 KB is MP3 audio.

- **HTML is small once compressed.** For example, chapter 1 is 104 KB raw and about 26 KB transferred; chapter 5 is 216 KB raw; Darrow's page is 191 KB raw and about 35 KB transferred. The stylesheet is 16 KB and the script 6 KB (the Wardrobe adds about 5 KB). GitHub Pages sends `cache-control: max-age=600` on pages and assets — curl `-I` of the live files.
- **Paint and layout shift.** Layout shift measured 0 on the Now, Wardrobe, Codex, Darrow and roster pages, and 0.006 on chapter 7 under throttling.
  - The largest paint on the Now page is a paragraph of text: 0.84 s unthrottled, 0.82 s throttled to 1.6 Mbps/150 ms, with full load at 3.4 s throttled.
  - Chapter 7 throttled: first paint 0.65 s, load 1.7 s.
  - The Wardrobe's largest paint is the look picture (0.41 s unthrottled); Darrow's is his portrait.

**Image loading behaviour** [measured on the live site]
- **Eager (no `loading` attribute):**
  - the painted map (an SVG `<image>`, 108 KB);
  - every portrait on the Now page, the roster and character pages, including the second Book's slide;
  - the Wardrobe stage's full look.
- **Lazy:**
  - Codex full pictures (with width and height);
  - Wardrobe lookbook tiles and picker faces (no width or height);
  - Darrow's Art cards (58×58 attributes, shown at 64 px). These sit inside the folded Arts panel and did not load on a phone at all.
- **Oversized copies:**
  - six `md` copies at 640 px shown in circles of 48–86 px;
  - the stage's 1024×1536 look shown at 322×484 px;
  - the Codex's 256 px thumbnails shown at 56×32 px.

### Inferences
- **Small targets on a phone.** The places a reader is most likely to miss are the map (the labels are the links, 9–22 px tall), the portrait tabs, and the many one-line folds (the roll, Codex rows, scene lists). All are usable with care, but most of these fall below 24 px as a size, and every one falls below a comfortable 44 px.
- **Easy fixes.** Padding on `summary` and on SVG `<a>` hit areas (an invisible rect behind each map label), and a taller tab pill, would lift most of them without changing the look.
- **Weight is mostly fonts and portraits, not prose.** Making zoomed avatars use a cropped small copy, rather than a 640 px image clipped to a circle, would cut about 250 KB from the Now page and the roster. Setting the Codex's audio to `preload="none"` would cut its 1.6 MB.
- **Desktop prose is too wide.** At 88–93 characters a line, it runs well past the 45–75 range usually recommended for reading (general typographic guidance, not re-checked in this session). On phones it sits inside that range.

### Gaps
- **The WCAG criteria are unverified here.** I could not fetch WCAG 2.2's 2.5.8 text (www.w3.org is not allowed in this session's network). The 24 px and 44 px thresholds come from the assignment, and the inline and spacing exceptions are applied from memory.
- **Audio preload on real phones is unmeasured.** iOS Safari and Android Chrome may treat `preload="metadata"` differently from headless Chromium, so the Codex's audio cost on a real phone is unmeasured.
- **Timings are not phone timings.** They are from network emulation on a desktop CPU.
- **Font caching is assumed.** Fonts are counted per cold page. In practice the browser caches them after the first page, but I did not measure a warm session.

## What a reader sees first on each page, and where the story has no visual support

### Takeaway
On a phone, only three pages open on a picture: the Wardrobe (the look painting fills almost half the first screen), Darrow's page and character pages (a 131 px portrait).

The pages read most open on words alone: the Now page, every chapter, the tales and the Chronicle. On the Now page the very first block is a Wardrobe and Collection news banner, above the story's own plate.

Darrow's page and the Collection open on numbers. Chapters, tales, most places and every Codex "thing" have no picture at all. A shared link shows no image, only a title and a generic line.

### Cited Findings

**First screen at 390×844** [measured on the live site; "image" = share of first-screen area that is a picture; "digits" = digit characters in first-screen text]

| Page | What fills the first screen | Image | Digits | Story vs numbers |
|---|---|---|---|---|
| Now | Wardrobe news banner (y 115–250: new pieces and the Collection count). Then the Now plate: Book line, "Chapter 7 — The Far Bank", "so far" tier seal, Where, Season, Latest scene, Just happened, Continue reading. "The quest" heading at the foot | 0% | 9 | mostly story, but a game banner comes first; no picture |
| Chapter 7 | Title, Previously box, epigraph, three fold headings. Prose starts about 680 px down | 0% | 3 | story only; 80% of the screen passes before prose |
| Chapter 1 | Book line, title, "Costly" seal, an epigraph that is an in-world tally. Prose starts about 560 px down | 0% | 11 (story's own tallies) | story only |
| Chronicle | Plate with Continue reading. Timeline rows with scene, Between and word counts | 0% | 41 | navigation and counts |
| Codex | Plate, 7 jump chips, the first places with three 56×32 thumbnails | 1.6% | 13 | list |
| Roster | Title plate and 12 filter chips fill the screen. The first card starts about 580 px down | 5.9% | 4 | controls, not people |
| Hollis | Portrait (131 px) with crest, Book tabs, faction sigil. Then Appearance prose | 10.4% | 1 | story |
| Darrow | Portrait with crest. Then the progression line, XP bar, Ember bar with its number, Inspiration, Reckoning chips | 12.2% | 20 | numbers dominate |
| Wardrobe | The current look, painted, 322×484 px | 47.3% | 5 | picture |
| Collection | His rank, a progress bar, the full rank ladder with each rank's piece threshold | 0% | 33 | numbers |
| Tales | Plate, then three tales with their pieces | 0% | 15 | list |
| Tale 1 | Title, when-line, "told in full.", the first piece's prose | 0% | 2 | story |

Sources: `sheet_first_A.png`, `sheet_first_B.png`, `sheet_first_C.png`.

**What only the real pages show:**
- **The Wardrobe banner leads the Now page** [measured on the live site]. The "New in the Wardrobe" banner sits above the Now plate and names the new pieces and the Collection count. It pushes the chapter plate to about 280 px down, and "Continue reading" to about 680 px — `home_phone_first.png`
- **The Reckoning card on the Now page** [measured on the live site] carries:
  - an XP bar with its figures;
  - four attribute medallions;
  - the Ember bar with its number;
  - the seven-knot rope, with a line naming the next Knot and what it lets the leg do;
  - the Tether thread.

  "The dice" then lists the last five checks, each with stat and difficulty tags and a result badge. Mechanics fill roughly two of the page's five screens — `strip_home.png`
- **Darrow's page lists every Knot** [measured on the live site]. Untied ones are named too, each with what it lets the leg do. The "On the page" panels (Now, Story so far, What he keeps, Appearance, Quote, Relationships, Known facts, Appearances) come after the numbers — `strip_darrow.png`
- **Character pages are long lists** [measured on the live site]. Hollis's page is 5,556 px on a phone. Its lower half is "Appearances": about 90 links, each 15 px tall, grouped by chapter, with "named" badges. Relationships are prose, with one regard bar ("Toward Darrow") — `strip_hollis.png`
- **The tale head has a gap** [measured on the live site]. At 390 px, Tale 1's italic when-line is followed by a large gap and then a detached "told in full." line — `tale01_phone_first.png`
- **The map is the most "story" picture on the Now page** [measured on the live site]. It is 374×281 px: the painted terrain and the route in ember read clearly.
  - Labels are legible thanks to the dark halo, but small (see above).
  - 14 places are labelled. Four of them have a picture behind their Codex entry (Saint Ysolde's, Coldmere, the Lowmarch, Harrow Ford).
  - The current place (the river mill) has none, so its preview and the Now plate are text — `int_map_phone.png`

**Where the story has no visual support** [measured on the live site]
- **Chapters.** No picture on any of 8 chapter pages: no header, no scene vignette, no Book frontispiece. The only visuals are the tier seal, the block glyphs, dice lines and the ✶ ✶ ✶ ornament.
- **Climaxes and choices.** Answered choices show as a numbered list with a "chosen" mark, on the Now page ("A small choice") and inside chapters.
- **Tales.** Index and pages are text only (0 images).
- **Places.** 5 of 17 Codex places have pictures, and the current place has none. Preview cards for Calden and for things like Hob are text only.
- **The Codex.** Of 75 Things, none has a picture. Sayings (34) and Histories are text only. 1 of 8 factions has a picture; the others show only their drawn sigil when opened.
- **People.** 18 of 19 have portraits. One roster card shows a faction shield instead.
- **Sharing.** With no `og:image`, `og:title` or `og:description`, a link pasted into a chat app can show only what the app derives from `<title>` and the generic `description`, with no picture. The `apple-touch-icon` is the only image a phone home screen would use.

### Inferences
- **The heaviest visual weight sits on the meta pages.** On a phone, the paintings lead on the Wardrobe and the character plates, while the weekly experience (the Now plate and the chapter he is reading) has no picture at all. The one picture of "where he is" lives in the map, below roughly two screens of game state.
- **The Now page puts game news ahead of story.** Its first impression today is a collection update, then the story plate. Moving the banner below the plate, or into the Reckoning card, would let the page open on the story.
- **Darrow's page and the Collection are where numbers lead.** That fits the "/sheet is asking" rule, but they are also the site's main picture of the hero. On the Now page the Reckoning card exposes thresholds and the next Knot by default, a lot of mechanics for a page meant to say "what is going on now".
- **Cheapest wins for visual support:**
  - a chapter header slot (the reading surface has none);
  - a picture for the current place (it would light up both the Now plate and the map preview);
  - an `og:image` and `og:description` per chapter.

  All three would reuse existing image kinds and the build's gating.

### Gaps
- **Link previews.** I did not test how specific chat apps (iMessage, WhatsApp, Slack) render a link to the site. The share finding rests on the absence of the tags, not on observed previews.
- **First-screen state changes.** The first-screen analysis reflects today's state: no open choice, no level-up banner, the current place without a picture. On a day with an open choice or a level-up banner, the Now page's first screen would differ.
