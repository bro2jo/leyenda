# Character files — the reader-facing cast

One JSON file per character who has **appeared or been named on the page** in `saga/chronicle/`. The site build (`engine/build_site.py`) renders these. Darrow has a file too, for everything except his numbers; his Reckoning comes from `saga/state/darrow.json` and is never hand-edited.

## Evidence rules (these are hard rules; the build and the audit enforce them)

- Every sentence must be supported by text already in `saga/chronicle/`. If the page does not show it, it is not here.
- Exception: **appearance** and **voice** may draw on `saga/bible/characters.md`, but never that file's Wants, Fears, Carries, Hides, Flaw, Arc, Rule-of-the-saga or secret lines.
- Never read or use `saga/bible/_gm/`, `saga/state/threads.md`, `real/`, or `engine/deeds.csv`.
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
  "sigil": {"faction": "menders", "mark": "needle"},
  "appearance": "2–4 sentences: build, face, clothing, scars, how they carry themselves.",
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
    {"to": "darrow", "label": "his Mender", "note": "One sentence, as seen on the page."}
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
- Companion approval is **not** stored here; the build reads it from `saga/state/world.json` and shows words and a bar, never a number.
- Grace-sworn strength is borrowed (`fire.kind = "grace"`): the build colors it icy blue and labels it borrowed. Earned strength (`ember`) is brass and ember. `none` means nothing is kindled and the Grace is gone.
- What Darrow can read of another's Reckoning is gated by his Warden's Eye rank in `darrow.json`: I shows level and rank; II the attributes; III the Arts; IV and up the deeper lines. Everything else renders as ⟦ unread ⟧.

## Scene registry (copy anchors exactly)

| chapter | scene | title | anchor |
|---|---|---|---|
| `00` | `I` | Harrow Ford | `chronicle/00-prologue-the-three-heartbeats.html#part-i` |
| `00` | `II` | The Steps | `chronicle/00-prologue-the-three-heartbeats.html#part-ii` |
| `00` | `III` | The Binding | `chronicle/00-prologue-the-three-heartbeats.html#part-iii` |
| `01` | `1` | The Reading of the Knots | `chronicle/01-the-confessor-at-the-steps.html#scene-1` |

New chapters: scenes are `### Scene N — Title` → anchor `chronicle/<file>.html#scene-N`; the climax is `#climax`; a choice's consequence is `#choice`. The build fails on an anchor it cannot find.

## Place ids

`harrow-ford` · `the-wend` · `the-thornwild` · `the-lowmarch` · `thousand-steps` · `saint-ysoldes` · `coldmere` · `holloway` · `calden` · `oathspire` · `edgemoor` · `greywater-peaks` · `saltreach` · `ashen-fields` (see `saga/state/places.json`).

## Sigil marks the build can draw

Faction devices come from `factions.json`: `lance` (with the lance's numeral), `bell`, `censer`, `crown`, `redhand`, `knee`. Personal marks: `knot`, `horn`, `needle`, `pencil`, `spyglass`, `key`, `stone`, `note`, `knife`, `quill`, `cup`, `candle`, `star`.

## Maintenance (every scene, climax or choice)

1. New on the page → new file. 2. Everyone on the page → `last_seen`, `last_seen_doing`, `now`, `appearances`, new `known_facts`, `appearance` if the story changed them, `status` if it changed. 3. `story_so_far` at chapter end. 4. `quote` when a better line lands. 5. Then `python3 engine/build_site.py` and commit `docs/` with the rest.
