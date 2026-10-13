---
paths:
  - "saga/**"
---

# Writing the Chronicle, and the site

*Loads whenever a file under `saga/` is read or edited. Moved from CLAUDE.md unchanged; the wall itself (golden rule 4) stays there.*

## Writing the Chronicle

Read before writing anything in `saga/`:
- `saga/bible/style.md`: the wall, voice, formats (scene kinds, interlude, micro-choices, the Bearing in prose) and the reread (§4) every scene, climax, Between and Choice block gets before its bookkeeping. **Mandatory.**
- `saga/bible/cast.md` (appearance and voice of everyone on the page). `mechanics.md` only when a Reckoning box, a Knot or an Art is on the page.
- `saga/bible/_gm/arc.md` (one section at a time: `saga.py arc <id>`) for the beat or quest you are writing; `_gm/characters.md` only the entries of the people in the scene (grep the `###` heading); `_gm/world.md` on demand for a place or custom. Never whole. Never reveal a truth ahead of its schedule; plant at least twice before any reveal.
- `saga/bible/_gm/design.md`: the systems in full (ledger, Bearing, roads, slots, quests, micro-choices, and §5.6: the devices, a challenge, the Book's project, an invitation, the callbacks, with the pacing rule that rotates them); read on demand, not every session.
- `saga/bible/_gm/lore.md`: **the Annals**, the realm's history and texture (the ages, the House, the realm, the clans, songs, sayings, crafts, the calendar), read one entry at a time (`python3 engine/saga.py lore <id>`; the index `saga.py lore` once per chapter; `lore grep <word>` for a place or custom a slot touches). Its doctrine, at its top, is the rule: **the scene first; as many lore touches as the scene's meaning needs** (no fixed count; often one), a climax's action beats kept clear where possible, never one that answers the scene's question; a touch earns its place if it also characterises, raises the stakes, sets the place or makes the scene clear; received, not revealed (the arc wins every conflict); no new plot. When the page speaks an entry, `saga.py lore spoke <id> --where chNN:sK` and `codex.md` gets the reader-safe line.
- `saga/state/world.json`, `bearing.json`, `codex.md`, `_gm/threads.md`: continuity, read directly. `_gm/plan.json` and `_gm/consequences.json` are read only through `saga.py now`, `plan next`, `plan climax` and `due`; never open them whole. Where you must Edit JSON by hand, keep it canonical (`saga.py fmt`).

- **The Tether** (`saga/bible/_gm/design.md` §8): the romance with Rae Thorne is staged by the Ledger and shaped by his choices. When `sync` prints `TETHER TIED` or `TETHER DRAWN` (one line per stage crossed), the next free quest slot carries that stage's scene: the first float quest slot whose day has not closed, this chapter or the next, never a spine slot or a required quest's stage (`saga.py arc rae.tether`; `plan slot N kind=quest quest=rae.tether stage=K plan=…`; `check` refuses a stage the engine has not reached, a stage out of order, and a stage whose `stage_gates` condition the story has not met: the sheet climbs anyway and the scene waits), closing with `> The Tether: **<name>**.` in the Reckoning box. Her approval moves only through the ledger. Never a scene because an evening was logged.

Quality bar: a stranger should want the next chapter. Specific, funny where people are funny, frightening where it's dangerous, never preachy. Dice only from the engine. The story must never reward Darrow for recklessness with the Binding during the soft season.

## The site (`docs/`)

A reader-facing, static site, built by `python3 engine/build_site.py` into `docs/` and served by GitHub Pages. **Assume it is public.** It reads only `saga/chronicle/`, `saga/characters/`, `saga/state/{world,places,factions,darrow,bearing,codex_art}.json`, `codex.md`, `chapters.csv`, `rolls.csv`, `engine/rules.json`, and the images and songs in `saga/art/` that `places.json`, `factions.json`, `codex_art.json` or a character file names (published as files under `docs/art/`; a song plays in its Codex entry and from a small button where the story sings it). It never reads `real/`, `engine/deeds.csv`, `saga/bible/` or any `_gm/` directory (the checks open the GM `.md` files only to build blocklists; nothing from them is rendered).

**Rules for everything the site shows** (the build enforces what it can, you enforce the rest):
- Story only. No foods, numbers or dates from logs, exercises, PT, rehab terms. Game numbers are fine.
- No spoilers. Every sentence about a character, place or event must be supported by text already in `saga/chronicle/`. Appearance and voice may also draw on `saga/bible/cast.md`. A name the page has not spoken does not appear; wants, fears, secrets and arc notes go in `saga/bible/_gm/characters.md`.
- Darrow's numbers are engine-owned (`darrow.json`); other characters' Reckonings are yours to assign, consistent with canon, gated on the site by Darrow's Warden's Eye rank.

**Whenever a scene, climax or choice is written** (the `/log` close, `/checkpoint`, `/choose`):
1. `saga/characters/<id>.json` for anyone new on the page (contract: `saga/characters/README.md`; a portrait he supplies goes in `saga/art/characters/<id>.jpg` with `portrait` and `portrait_alt`).
2. For everyone in the scene: `last_seen`, `last_seen_doing`, `now`, `appearances`, new `known_facts` (with chapter and scene), `appearance` or `status` if the story changed them, `story_so_far` at chapter end, a better `quote` if one landed.
3. `saga/state/places.json` for a new place (map x/y, `on_page`, `visited`, description; a picture he supplies goes in `saga/art/places/<id>.webp` with `image`, `image_alt`, `image_caption`: see `saga/art/README.md`; `aliases` for other words the story uses for it, e.g. "the Steps", so its first mention in a scene links to its Codex entry with a preview); `world.json → location.place`, `current_quest.on_the_page`, `recaps` for a new chapter. Darrow's Bearing (`bearing.json`) shows on the site in words only; an epithet appears there only once the page has spoken it.
4. `python3 engine/saga.py check`, then `python3 engine/build_site.py`. It fails loudly on real-world terms, GM sentences, unrevealed names, a known fact without a source, a GM key in `world.json`, or a broken link, and leaves `docs/` untouched until it passes. Never commit a `--force` build.
5. Commit `docs/` with everything else.

View it locally with `python3 -m http.server -d docs 8000` (then http://localhost:8000/), or open `docs/index.html` directly. GitHub Pages: Settings → Pages → Deploy from a branch → `main`, folder `/docs`.
