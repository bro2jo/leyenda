---
paths:
  - "saga/**"
---

# Writing the Chronicle, and the site

*Loads whenever a file under `saga/` is read or edited. The wall itself (golden rule 4) stays in CLAUDE.md.*

## How the story is kept

The story is kept the way the Ledger is kept: **records in, projections out.** One event per block of the page (scene, Between, interlude, climax, Choice) in `saga/state/events/chNN.jsonl` (reader-safe: what the page made true), one GM note per block in `saga/state/_gm/notes/chNN.jsonl`, the threads as data in `saga/state/_gm/threads.json`, the Codex's entries in `saga/state/codex.json`, the plan and the consequence ledger under `saga/state/_gm/`. From the records the engine rebuilds `saga/state/world.json`, the derived fields of every `saga/characters/<id>.json` (first and last seen, last_seen_doing, now, story_so_far, quote, known_facts, appearances), `saga/state/codex.md` and the narrative top of `saga/NOW.md`. **Those four are projections: never edited by hand** (`check` refuses a stale one; `saga.py project` rebuilds). The hand-authored story files are the chapter prose, a character's base (identity, appearance, portrait, relationships, reckoning), `cast.md`, `places.json`, `factions.json`, the bible and the arc.

**The tales** (`saga/bible/_gm/design.md` §12) are kept the same way: the pieces in `saga/chronicle/tales/NN-slug.md` under `### Piece K — Title`, one event per piece in `saga/state/events/taleNN.jsonl`, their plans in `saga/bible/_gm/tales.md` (GM). A piece is owed by a task of the week's work reported done (`/project`): `python3 engine/saga.py brief --tale` prints what it must carry (the tale's plan and this piece's, the keepsake on the last piece, what it must never say, the plants), the pieces told so far, the people, the Annals, the format and the record skeleton; `saga.py record` takes the skeleton back. A tale is the past: it moves nothing in the present (no approval, Bearing, ledger, plan or scene), adds appearances and facts to its people, and leaves a keepsake on someone's page at its end.

## Before writing anything in `saga/`

- **The brief:** `python3 engine/saga.py brief` (the next slot; `--date D`), `brief --between --with <who>`, `brief --climax`, `brief --choice`, `brief --chapter`. It prints what the block **must** carry (the slot's plan and turn, its device, what is owed: the open choice, the DUE items, the owed world move, a rank or Tether line), the **continuity** (where he is, the last block, the knee, what is in hand, the Betweens since the last scene, today's glimpses, who is there by the page), what it **may** use (the people with voice, tactic, regard and what they know; the threads with their plant counts; the Annals the plan names; callbacks that fit; the arc section), the **format**, and the **record** skeleton. Nothing else needs opening.
- `saga/bible/style.md` §1 (the wall), §2 (the craft) and §4 (the reread), every time. The last block of the chapter file, for its rhythm.
- On demand, never whole: `saga.py arc <id>`; `saga.py lore <id>` / `lore grep <word>` / `lore pick saying|verse`; `saga.py history --person <id>` / `--thread N` / `--place <id>` / `--last N` (`--gm` adds the notes); `saga.py threads [--id N]`; a person's full entry in `saga/bible/_gm/characters.md` (grep its `###` heading; what they hide stays there); `saga/bible/_gm/design.md` for a system's full rules; `saga/bible/_gm/world.md` for a place or custom. The Annals' doctrine (the top of `lore.md`) is the rule for lore: the scene first; as many touches as the scene's meaning needs, often one; received, not revealed; no new plot.
- **The Tether** (`design.md` §8): when `sync` prints `TETHER TIED` or `TETHER DRAWN`, the next free float quest slot carries that stage's scene (`check` refuses a stage the engine has not reached or whose stage gate the story has not met); it closes with `> The Tether: **<name>**.` in the Reckoning box. Never a scene because an evening was logged.

## After writing anything in `saga/`

- **The record:** `python3 engine/saga.py record '<the skeleton, filled>'`. It validates the block against the page and the registries (the heading, every person's file, every evidence excerpt, every name the page has not spoken, every thread and lore id), writes the event and the note, moves the plan (the slot done, the small choice opened, the climax choice opened, due items and rules fired, the Annals marked spoken, a rank or Tether line), rebuilds every projection and runs `check`. `--force` re-records a revised block. A choice goes through `python3 engine/saga.py choose` (the ledger entry, the choices[] row, the choice closed). A glimpse goes through `python3 engine/saga.py glimpse add`.
- A new person on the page: their base file (`saga/characters/README.md`) and their entry in `saga/bible/cast.md` before the record. A new place: `saga/state/places.json` (map x/y, `on_page`, `visited`, description, `aliases`). A picture he supplies: `saga/art/README.md`.
- Then `python3 engine/darrow.py ship -m "…"` (it runs `check`, builds the site, commits and pushes). Commit messages are reader-safe.

Quality bar: a stranger should want the next chapter. Specific, funny where people are funny, frightening where it is dangerous, never preachy. Dice only from the engine. The story must never reward Darrow for recklessness with the Binding during the soft season.

## The site (`docs/`)

A reader-facing static site, built by `python3 engine/build_site.py` into `docs/` and served by GitHub Pages. **Assume it is public.** It reads only `saga/chronicle/` (the tales under `chronicle/tales/` included: a *Tales* page, and the keepsakes on the character pages from `world.json`), `saga/characters/`, `saga/state/{world,places,factions,darrow,bearing,codex_art}.json`, `codex.md`, `chapters.csv`, `rolls.csv`, `engine/rules.json`, and the images and songs in `saga/art/` that the registries name. It never reads `real/`, `engine/deeds.csv`, `saga/bible/`, the events, or any `_gm/` directory (the checks open the GM files only to build blocklists: every sentence of a GM `.md` file and every string of the GM notes and threads is blocked from the site; nothing from them is rendered).

**Rules for everything the site shows** (the build enforces what it can, the record enforces the rest):
- Story only. No foods, numbers or dates from logs, exercises, PT, rehab terms. Game numbers are fine.
- No spoilers. Every sentence about a character, place or event is supported by text already in `saga/chronicle/`; a known fact that reports what someone thought, meant, believed or knew carries an `evidence` excerpt the build verifies. A name the page has not spoken does not appear.
- Darrow's numbers are engine-owned (`darrow.json`); other characters' Reckonings are yours to assign in their base file, consistent with canon, gated on the site by Darrow's Warden's Eye rank.

The build fails loudly on real-world terms, GM sentences, unrevealed names, a known fact without a source, a GM key in `world.json`, or a broken link, and leaves `docs/` untouched until it passes. Never commit a `--force` build. View it locally with `python3 -m http.server -d docs 8000`.
