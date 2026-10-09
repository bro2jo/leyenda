# Character files — the reader-facing cast

One JSON file per character who has **appeared or been named on the page** in `saga/chronicle/`. The site build (`engine/build_site.py`) renders these. Darrow has a file too, for everything except his numbers; his Reckoning comes from `saga/state/darrow.json` and is never hand-edited.

## Evidence rules (these are hard rules; the build and the audit enforce them)

- Every sentence must be supported by text already in `saga/chronicle/`. If the page does not show it, it is not here.
- Exception: **appearance** and **voice** may draw on `saga/bible/cast.md` (reader-safe: looks and voice lines only, for people already on the page).
- Never read or use `saga/bible/_gm/`, `saga/state/_gm/` (the plan, the consequence ledger, `threads.md`), `real/`, or `engine/deeds.csv`.
- No real-world words: no foods, numbers or dates from logs, exercises, therapy, rehabilitation terms. Game numbers (level, Might, Ember, dice) are fine.
- A name the page has not spoken is not spoken here. The red-handed woman has no name. The man leading the grey cloaks has no name.
- Secrets, true identities and stat rationale go in `saga/bible/_gm/characters.md`, never here.

## Fields

```json
{
  "id": "maelis-vorne",
  "name": "Maelis Vorne",
  "aliases": ["Maelis", "Mender Vorne", "the Mender"],
  "epithet": "Senior Mender of Saint Ysolde's",
  "tier": "major",                      // major | minor | fallen
  "faction": "menders",                 // id from saga/state/factions.json
  "status": "alive",                    // alive | fallen | hollowed | missing | unknown
  "sigil": {"faction": "menders", "mark": "needle"},     // mark may be "none"
  "appearance": "2–4 sentences: build, face, clothing, scars, how they carry themselves.",
  "portrait": "characters/maelis-vorne.jpg",   // optional: a picture he supplies, path under saga/art/ (see saga/art/README.md)
  "portrait_alt": "What the portrait shows, for screen readers.",
  "portrait_focus": "50% 30%",                // optional: the centre of the square crop (default 50% 30%)
  "first_seen": {"chapter": "00", "scene": "II", "place": "saint-ysoldes", "anchor": "chronicle/00-prologue-the-three-heartbeats.html#part-ii"},
  "last_seen":  {"chapter": "01", "scene": "1",  "place": "saint-ysoldes", "anchor": "chronicle/01-the-confessor-at-the-steps.html#scene-1"},
  "last_seen_doing": "One sentence: what they were doing the last time they were on the page.",
  "now": "1–3 sentences on what they are up to as of the latest chapter, as far as the reader knows. Offstage: where last known and what they were last known to intend. Rumor only if the rumor was on the page.",
  "story_so_far": "2–5 sentences, spoiler-free.",
  "quote": {"text": "The quiet is a liar.", "chapter": "01", "scene": "1"},
  "known_facts": [
    {"fact": "One fact, one sentence.", "chapter": "00", "scene": "III"}
  ],
  "relationships": [
    {"to": "darrow", "label": "the knight whose knee she bound", "note": "One sentence, as seen on the page."}
  ],
  "reckoning": {
    "fire": {"kind": "ember", "state": "steady"},     // kind: ember (earned) | grace (borrowed) | none (unlit)
    "level": 12, "rank": "Tempered",
    "attributes": {"might": 9, "vigor": 10, "finesse": 12, "resolve": 17},
    "arts": [{"name": "The Mender's Patience", "rank": 4}],
    "deeper": ["Lines Darrow could read only with a stronger Warden's Eye."]
  },
  "appearances": [{"chapter": "00", "scene": "II"}, {"chapter": "00", "scene": "III"}, {"chapter": "01", "scene": "1"}]
}
```

- `reckoning` is **null** for the fallen (the script does not read the dead). Darrow's file has no `reckoning` key at all.
- `quote` is **null** when the character has not spoken a line on the page (the site then says so). Never invent one.
- `appearances` lists the scenes the character is **present in**. A scene where they are only named gets `"mention": true`; a character who has only been named (not yet seen) has only mentions, and `first_seen`/`last_seen` point at those. `last_seen` is the latest presence, or the latest mention if there is no presence.
- Grace-sworn characters carry the rank word `Oathsworn` (a game term for borrowed strength, with `level: null`); everyone else uses the Ember ranks from `engine/rules.json`.
- Keep NPC sheets conservative: no Art or deeper line that would hint at a hidden link or a future turn. The GM's true numbers live in `saga/bible/_gm/characters.md`; the public sheet may be lower than the truth.
- Titles and roles count as facts, not appearance: an epithet must use words the page has used ("Captain of the Ninth Lance", not a title from the character bible).
- `status: fallen` may rest on what the page showed and the reader is meant to understand (a knight who went under in the river and was not among those who came back), but the file's own sentences still describe only what was seen; they never add "he drowned" if no sentence says so.
- Companion approval is **not** stored here; the build reads it from `saga/state/world.json` and shows words and a bar, never a number. Darrow's Bearing is not stored here either: it comes from `saga/state/bearing.json` and is shown in words.
- Grace-sworn strength is borrowed (`fire.kind = "grace"`): the build colors it icy blue and labels it borrowed. Earned strength (`ember`) is brass and ember. `none` means nothing is kindled and the Grace is gone.
- What Darrow can read of another's Reckoning is gated by his Warden's Eye rank in `darrow.json`: I shows level and rank; II the attributes; III the Arts; IV and up the deeper lines. Everything else renders as ⟦ unread ⟧.

## Couplings the build relies on

- **Companions:** `world.json → companions` is keyed by the first hyphen-separated token of the character id (`maelis` ↔ `maelis-vorne`). A companion with `present: false` is left off the Now page. The build fails if a key matches more than one file.
- **Name links in the reader:** the build links the `name` (with and without "Ser") and every alias that shares a word with the name (`Mender Vorne` yes, `the Mender` no), first mention per scene. Keep aliases to names the page has spoken.
- **Relationship labels** describe the *linked* person as this character sees them ("the knight whose knee she bound" on Maelis's page, not "his Mender").
- **Sigil mark `none`** means the faction device alone: use it until the page has put something in the character's hands.
- `reckoning.level: null` with rank `Oathsworn` draws the crest with a dash in blue (borrowed strength), not the violet unread mark.

## Scene registry (copy anchors exactly)

| chapter | scene | title | anchor |
|---|---|---|---|
| `00` | `I` | Harrow Ford | `chronicle/00-prologue-the-three-heartbeats.html#part-i` |
| `00` | `II` | The Steps | `chronicle/00-prologue-the-three-heartbeats.html#part-ii` |
| `00` | `III` | The Binding | `chronicle/00-prologue-the-three-heartbeats.html#part-iii` |
| `01` | `1` | The Reading of the Knots | `chronicle/01-the-confessor-at-the-steps.html#scene-1` |
| `01` | `interlude` | The Wax | `chronicle/01-the-confessor-at-the-steps.html#interlude` |
| `01` | `2` | Two Fires | `chronicle/01-the-confessor-at-the-steps.html#scene-2` |

New chapters: scenes are `### Scene N — Title` → anchor `chronicle/<file>.html#scene-N`; an interlude (`### Interlude — Title`, another POV) is `#interlude` (a second in the same chapter: `#interlude-2`), scene key `interlude`; the climax is `#climax`; a climax choice's consequence (`### Choice — Title`) is `#choice`. A small choice at the end of a scene has no anchor of its own. The build fails on an anchor it cannot find.

## Choices (`world.json → choices[]`)

The build marks answered options from `saga/state/world.json → choices[]`. Every key is required: `{"chapter": 1, "scene": "climax", "kind": "climax", "option": 2, "text": "…", "date": "2026-10-11", "ledger": "c01.1", "by": "darrow"}`. A small choice has `kind: "micro"` and `scene` = the key of the scene whose numbered list it answers (`"3"`, `"interlude"`); `by` is `"darrow"` or `"bearing"` (Darrow answered for himself; the site adds "answered for himself"). Chapters are ints; `ledger` names the consequence-ledger entry, written by `python3 engine/saga.py add` before this entry is added by Edit.

## Place ids

`harrow-ford` · `the-wend` · `the-thornwild` · `the-lowmarch` · `thousand-steps` · `saint-ysoldes` · `coldmere` · `holloway` · `calden` · `oathspire` · `edgemoor` · `greywater-peaks` (see `saga/state/places.json`; only places the page has named).

## Sigil marks the build can draw

Faction devices come from `factions.json`: `lance` (with the lance's numeral), `bell`, `censer`, `crown`, `redhand`, `knee`. Personal marks: `knot`, `horn`, `needle`, `pencil`, `spyglass`, `key`, `stone`, `note`, `knife`, `quill`, `cup`, `candle`, `star`.

## Maintenance (every scene, climax or choice)

1. New on the page → new file (and an entry in `saga/bible/cast.md`). 2. Everyone on the page → `last_seen`, `last_seen_doing`, `now`, `appearances`, new `known_facts`, `appearance` if the story changed them, `status` if it changed. 3. `story_so_far` at chapter end. 4. `quote` when a better line lands. 5. Then `python3 engine/saga.py check`, `python3 engine/build_site.py`, and commit `docs/` with the rest.
