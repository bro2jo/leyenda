# Art — pictures for the site

Images the user supplies for the Chronicle's public site (`docs/`). Reader-safe only: a picture may show only what the page has already put on the page.

- `places/<place-id>.webp` (or `.png`, `.jpg`): one picture per place, named for its id in `saga/state/places.json`.
- `characters/<character-id>.jpg` (or `.webp`, `.png`): one portrait per character, named for their file in `saga/characters/`. Square works best.
- To publish a place picture, set the place's `image` (path under `saga/art/`, e.g. `places/saint-ysoldes.webp`), `image_alt` (what the picture shows) and optionally `image_caption`. The place must already be `on_page`.
- `python3 engine/build_site.py` copies it to `docs/art/…` and shows it in the place's Codex entry: full width, a thumbnail in the row, tap or click to see it whole. Keep each file under 3 MB (the build refuses larger); WebP around 1600 px wide is plenty.
- To publish a portrait, set `portrait` (path under `saga/art/`, e.g. `characters/darrow.jpg`) and `portrait_alt` in the character's file. The site shows it framed at the head of their page (tap to enlarge), round on their roster card, and, for Darrow, on the Now page's Reckoning card. A portrait shows only what the page allows: a character not yet seen has no portrait.
- **Sizing is automatic.** Every picture sits in a fixed frame and is cropped to fit, never stretched: place pictures 16:9 at the full width of the column, portraits a square that scales with the screen (about a third of a phone's width, 200 px on anything wider) with the level crest on its corner. Any shape or size of upload works; tapping shows the whole uncropped picture. If the crop cuts off something that matters, set `image_focus` or `portrait_focus` to the point to keep centred, as `"X% Y%"` (e.g. `"50% 20%"` keeps the top of a tall portrait).
