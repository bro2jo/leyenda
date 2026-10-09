# Art — pictures for the site

Images the user supplies for the Chronicle's public site (`docs/`). Reader-safe only: a picture may show only what the page has already put on the page.

- `places/<place-id>.webp` (or `.png`, `.jpg`): one picture per place, named for its id in `saga/state/places.json`.
- To publish one, set the place's `image` (path under `saga/art/`, e.g. `places/saint-ysoldes.webp`), `image_alt` (what the picture shows) and optionally `image_caption`. The place must already be `on_page`.
- `python3 engine/build_site.py` copies it to `docs/art/…` and shows it in the place's Codex entry: full width, a thumbnail in the row, tap or click to see it whole. Keep each file under 3 MB (the build refuses larger); WebP around 1600 px wide is plenty.
