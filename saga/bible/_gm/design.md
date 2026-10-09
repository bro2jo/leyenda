# ⚠️ GM EYES ONLY — Design: the systems behind the Chronicle

The final reference for how the story is run. `CLAUDE.md` has the per-session steps; `style.md` has the craft rules and the formats (scene kinds, interlude heading, micro-choice list, Reckoning box); `_gm/arc.md` has the plot. This file has the machinery. Everything here is executed by `python3 engine/saga.py`; the engine does the bookkeeping, you do the writing.

Four principles bind every piece:
1. **Real world outranks the realm.** Nothing here changes how deeds become XP or attributes (`darrow.py` owns that). Bearing, roads and consequences move only with story choices and chapter tiers, never with real numbers. The knee is cleared only by real gates and is never the price of anything.
2. **The wall.** Reader-safe surfaces (`saga/` outside any `_gm/` directory, `docs/`, `CLAUDE.md`, `README.md`, the skills) never carry a name, place, thing or plan the Chronicle has not put on the page. Everything else lives under `saga/bible/_gm/` or `saga/state/_gm/`. The build scans the GM `.md` files to block their sentences and names from the site; JSON under `_gm/` is never rendered.
3. **Context-light.** Per session read `CLAUDE.md`, `real/NOW.md`, `saga/NOW.md`, and `saga.py now` (≤ 30 lines). Consult the arc, ledger and plan through `saga.py` sections, never whole.
4. **No shame, no penalties, no recklessness rewarded.** Low roads cost Darrow ground, standing and company, never survivors and never the knee. Missed days are plot turns.

Decision of record: Arts and Knots are a skill tree, shown sealed on the site by design; they are not plot and need no planting.

---

## 1. Files

| File | Who | What |
|---|---|---|
| `saga/state/world.json` | reader-safe | book/chapter, `scenes[]`, location, season, `current_quest {name, on_the_page}`, struggle, last_beat, on-page `companions` (approval, present, note), `choices[]`, inventory, recaps |
| `saga/state/bearing.json` | reader-visible | the four axes, names, epithet, leans, history (§3) |
| `saga/state/_gm/plan.json` | GM | position, chapter plan (slots, world moves, climax), core beats, quests, route, flags, factions, companion preferences, companions to come, `quest_summary`, open micro, temptation (§5) |
| `saga/state/_gm/consequences.json` | GM | the consequence ledger: baseline approval, entries, rules (§2) |
| `saga/state/_gm/threads.md` | GM | open plants and payoffs, by hand |
| `saga/bible/_gm/arc.md` | GM | the plot, in id-headed sections (`saga.py arc <id>`) |

`saga.py fmt` keeps the four JSON files canonical (2-space indent, key order preserved, trailing newline); `check` fails when a hand Edit left one non-canonical. Approval and Bearing are never edited by hand: only `saga.py add` (and `bearing`) move them, so the ledger always reconciles (`baseline + Σ now.approval == world.json`).

`world.json → choices[]` entry (every key required): `{"chapter": 1, "scene": "climax", "kind": "climax", "option": 2, "text": "…", "date": "2026-10-11", "ledger": "c01.1", "by": "darrow"}`. A micro has `kind: "micro"`, `scene` = the key of the scene whose numbered list it answers (`"3"`, `"interlude"`), `by: "darrow" | "bearing"`. Chapters are ints.

## 2. The consequence ledger

Every choice gets **one terse entry**: what it changed now and what it will change later, with triggers the engine resolves. Never re-derive consequences from memory or the arc; `saga.py now` prints the ones that apply.

```json
{"id": "c01.1", "made": {"chapter": 1, "scene": "climax", "date": "2026-10-11"},
 "chose": "Stepped forward and answered to his name at the gate",
 "now": {"approval": {"maelis": 5, "wren": -5}, "bearing": {"candor": 2}, "flags": {"named_himself": true}, "factions": {"confessors": -5}},
 "due": [{"id": "c01.1a", "when": "ch02", "weight": "scene", "what": "The Confessor uses his rank in front of the House"},
         {"id": "c01.1b", "when": "next", "weight": "color", "what": "Wren will not meet his eye; she counts the gate's hinges aloud"}]}
```
- `id`: `c<chapter, two digits>.<n>`; due items append a letter. `made` is structured.
- `when` is what you wrote; `at` is the static target `add` computes (`next` → `ch<chapter>:s<next_scene>`; else `at = when`). Vocabulary: `next` · `chNN` · `chNN:sN` · `chNN:climax` · `bookN` · `bookN:beatK` (while core beat `bN.K` is `in_progress`) · `transitionN` · `finale` (= `book6:climax`) · `on:<flag>` · `any` (standing).
- `weight`: `color` (a line) · `scene` (a beat of a scene) · `route` (bends a road) · `fate` (a life or an ending). `status`: `pending` → `fired@ch03:s2` or `void:<reason>`.
- **Due now** = `at` matches the current position; **overdue** = `at` is behind the position and still pending; both print in `now` until fired or void. `saga.py due` with no arguments lists everything due or overdue now (owed world moves included); `due --at <target>` is an exact-target lookup that also shows what is due now; `due --all` is the whole ledger. Fire what you used (`saga.py fire ID --where ch03:s2`); void what the story made impossible, with a reason.
- `now.*` deltas are applied only by `saga.py add`: approval → `world.json` companions (clamped −100…100; a companion not yet in `world.json` needs `--pending`, which banks it in `companions_to_come.<id>.approval_pending`), bearing → `bearing.json`, flags/factions → `plan.json`. `--witnessed maelis,wren` adds ±2 approval per witness whose preferred pole (or its opposite) the entry's bearing move lands on, and writes it into the entry's `now.approval` so the record is complete. `--dry-run` prints every old → new and writes nothing.
- **Rules** (`rules[]`) are standing conditions the finale, roads and a few fates consult: `{"id": "r.finale.return", "if": "approval.maelis >= 50 && approval.wren >= 50 && (flags.anselm_spared || flags.vane_unbound)", "then": "…", "where": "book6:climax"}`. Grammar: `&& || !`, parentheses, `>= <= > < == !=`, numbers, quoted strings, `true/false`, and the terms `approval.<id>`, `bearing.<pole>` (axis value if the pole is the axis's right word, negated if left), `flags.<name>` (null → false), `route.bookN` (`""` while undecided), `factions.<id>`, `temptation.count`, `quests.<id>.status`. Evaluation is an `ast` walk over a whitelist; anything else is MALFORMED and reported by `check`. Missing terms read 0/false; unlike types compare false. `now` shows rules ARMED, near (a numeric term within 15 of its threshold) or UNKNOWN TERM; `check` fails on malformed rules and unknown identifiers. Fixed ids the arc writes to: `r.finale.shatter`, `r.finale.take.tempting`, `r.finale.return`, `r.t8.early`, `r.b4.hollis_lives`, `r.b3.ysra_fate`, `r.route.bookN.low|high`, `r.once.early_arrival`.
- `saga.py archive` moves entries whose due items are all fired/void and older than two Books to `consequences_archive.json`, which `now` never reads.

## 3. The Bearing

Who his choices are making him: four axes, −10 … +10, story-only, reader-visible in words.

| Axis | Left | Right | Decides |
|---|---|---|---|
| mercy_flint | Mercy | Flint | the guilty and the beaten: pardon or punishment |
| candor_guile | Candor | Guile | the plain truth vs. the useful lie |
| hearth_banner | Hearth | Banner | whom he spends himself for: the few he knows vs. the many he does not |
| sworn_unsworn | Sworn | Unsworn | the old bonds (brother, rank, the Lances' forms, the law of bells) vs. owing nothing he did not build |

- No axis concerns the leg; no micro-option and no climax option in any Book is about testing the knee or defying the Mender on it.
- Moves: ±1 (micro), ±2/±3 (climax), ±4 only for a betrayal or a sacrifice. `saga.py bearing <pole> <n> --why <ledger id>` moves toward that pole, clamped, and appends to `history`; normally the ledger entry's `now.bearing` does it for you.
- **Leans** at |value| ≥ 4 ("leans Candor"); **named** at ≥ 8. The **epithet** is the named pole with the largest |value| (ties → the pole moved most recently): Mercy → *Open-hand* · Flint → *Flintheart* · Candor → *Plainspoken* · Guile → *the Fox of Edgemoor* · Hearth → *Hearthkeeper* · Banner → *Captain of Strangers* (Hollis's jibe, turned into a name) · Sworn → *the Faithful* · Unsworn → *the Masterless*.
- **An epithet must be spoken on the page** (a writ, an enemy's mouth, a companion's jibe) in the scene or climax whose choice earns it. The site shows pole words and the epithet; prose shows no numbers, only how people address him, which options exist, the epithet in writs and talk.
- **Companion preferences** (`plan.json → companions.<id>.prefers`): Maelis Candor, Sworn · Wren Guile, Unsworn · Hollis Mercy, Hearth. A choice on a companion's pole, witnessed or learned of, rides ±2 approval (`add --witnessed`).
- **Gating:** an option may require a Bearing value: `*[Guile 1]*` for a first step, `*[Guile 4]*` for a lean; struck through when unmet, like a stat gate. Roads and endings consult Bearing only through ledger rules.

## 4. Roads: one per Book

`saga.py route decide --book N` scores the Book's closed chapters (`route.bookN.chapters`, Knot week included) from `chapters.csv`: Triumph +1, Setback −1, others 0. **Low** if score ≤ −2, or ≤ 2 chapters and the last climax was a Setback; **High** if ≥ +2, or ≤ 2 chapters and the last was a Triumph; **Main** otherwise. It refuses while a listed chapter has no `chapters.csv` row unless `--road … --why …` (recorded as `override`). The decision sets `route.bookN.transition_chapter` to the last listed chapter if unset.

Every transition chapter has three written shapes in the arc (`tN.high`, `tN.main`, `tN.low`). In all three the Knot ties, the next Book's first core beat happens, nobody is lectured or humiliated, no survivor count drops, the knee is never the price. What differs: the circumstances of the crossing, who is with him, what he carries, what the world believes of him, and **one carry-forward** per road as a ledger rule `r.route.bookN.<road>` (low: a cost on ground, standing or company; high: a boon; main: none). A road's text may key one line on a Bearing lean. "Arrives a chapter early" fires at most once per Book whichever source armed it (`r.once.early_arrival`).

A Knot tied mid-week: re-plan the rest of the week's slots toward the crossing, Sunday's climax becomes the transition, and `route decide` runs at that checkpoint after `darrow.py chapter-close`. From Book II on, one **temptation** beat per Book shows the fast, borrowed way working for someone (its bill due a Book later); `plan temptation add "…"` records each and `temptation.count` feeds `r.finale.take.tempting`.

## 5. Day → week → Book

### 5.1 Scene kinds (every daily scene is exactly one)
- **Spine:** advances the chapter's core beat. ≥ 2 per chapter; Saturday's slot is always spine; if Saturday is missed, `plan done N --skipped` and its spine content folds into the climax (Friday's slot is never promoted; nothing is re-planned).
- **Quest:** one stage of an active side quest. ≤ 2 stages of one quest per chapter.
- **Interlude:** another POV, ≤ 1 per chapter, heading `### Interlude — Title`, not tied to a day (a slot with `"day": null`, outside the 7-day count). It is written on any close-day of its chapter, after that day's own scene (never instead of it), or at the checkpoint before the climax if still unwritten; `plan done N --wrote chNN:interlude` closes it.
- **Cutaway:** a red-light day; the world moves without him. Never a setback frame.

**Days.** A day with a row in `daily_log.csv`, `nutrition_log.csv` or `food_entries.csv` is **open** until `closed=Y` (food alone opens a day); it gets its slot when closed, in any order (`plan next --date D`). Only a day with nothing logged at all is **missed**: no row is ever created for it, no scene; `plan done N --skipped` records it, pops one off-page **world move** from `chapter.world_moves[]` onto the slot, and `now` and `plan next` print that move as owed until the next scene or climax opens on it (`plan done --wrote` and `plan set stage=climax` mark it used). A skipped spine slot's content folds into the next spine slot or the climax. The two `float: true` quest slots are the first dropped. `plan done N --force` redoes a slot already written or skipped.

**Colour, never content.** The slot's content is fixed in advance; the day's real deeds set only the tone (warmth or cold; the stage goes well or costs more; people are kind or short). Outcome is set only at the climax by the tier. `plan next --date D` prints the colour in one line, computed from the logs vs `real/config.json → nutrition_targets`: `rest` if light = red; `warm` if both floor rounds and (a session or both kcal and protein ≥ 90%); `cold` if neither floor round and no session; else `mild`. GM-only; it never appears anywhere reader-facing.

### 5.2 Side quests
Each quest in `arc.md` (`## q1.wager — Title`) has `priority` (`required | optional | floating`), `hook`, 2–4 `### stage N` sections (one daily scene each, ending on movement) plus `### compressed` (two stages), one `### micro` at its turn, `payoff`, `spine link`, `can run when`. Once Chapter 2 opens at least one quest is live, never more than two; stages run in order and finish within two chapters; `required` first; a quest dropped for plot reasons is `dropped` with one line of why; `floating` quests may run in any Book at the House or be re-skinned on the road. `plan done` on a quest slot advances `quests[q].stage` and sets `live`/`done` (done when the slot carries `"last": true` or the stage count in the arc is reached; quests whose arc stages are compressed into one line have no count, so close them with `plan quest ID status=done` by hand after their last stage). From Chapter 2 on `now` warns when no quest is live.

Book I: `q1.kennel` (required; Ash; sets `flags.ash_met`), `q1.letters` (required to its second letter; the third is a micro on sworn_unsworn), `q1.wager`, `q1.steam`, `q1.farcots`, `q1.ledger` (optional), `q1.snow`, `q1.hollownight` (pinned to the week of real Halloween if the Book is still open), `q1.door` (floating). Core beats `b1.1` … `b1.5`; transition `t1`.

### 5.3 plan.json
`position {book, chapter, beat, next_scene, stage ∈ scene|climax|choice|transition, last_written}` is the cursor every `at` resolves against. `chapter {number, week_start, question, slots[], world_moves[], climax {plan, checks, options, default}}`; a slot: `{n, day, kind, beat | quest+stage (+ last: true on a quest's final stage) | pov, plan, micro, float, status ∈ planned|next|written|skipped, wrote, world_move}`; a micro: `{ask, axis, options[2–3], bearing[per option, one axis, ±1 or null], default}`. `core_beats` (`planned|in_progress|done|folded`), `quests` (`available|live|done|dropped`, stage, priority), `route.bookN {chapters, road, override, transition_chapter}`, `flags`, `factions`, `companions.<id>.prefers`, `companions_to_come.<id> {note, bond, approval_pending}` (→ `plan companion arrive ID` when they step on the page), `quest_summary` (the GM's version of the quest line), `open_micro`, `temptation.planted[]`. New flags a Book needs are listed in the arc under `## flags`.

### 5.4 Chapter (week) and Book
A chapter has a **question** (a sub-question of the Book question) that the climax answers in the tier's shape; the choice bends the next chapter's slots. Planning a chapter (`plan chapter open --number N '<json>'`, checkpoint step D): 7 slots Sun–Sat (≥ 2 spine, Saturday spine, ≤ 1 interlude, two `float` quest slots), micros in non-adjacent slots touching ≥ 2 axes, `world_moves`, the climax plan with checks, options and a `default`; required quests first; the chapter touches ≥ 1 open thread. Across a Book's climaxes all four axes must be offered at least once, and no axis in more than three of them; the planner enforces this, `check` cannot. `check` enforces the shape; `plan chapter open` refuses while a micro is open (resolve it first), and `plan climax` prints the current chapter's question, climax plan, checks, options, default and world moves left. A Book opens with `plan book open N` (sets `position.book`, seeds `route.bookN` and the Book's core beats from the arc, marks the old Book's unwritten beats `folded`). A Book: its question, core beats, quests, road, transition variants; the Knot ends it. Core beats unwritten when the Knot ties fold into the transition in order; `now` warns when more than two core beats are still `planned`.

### 5.5 Micro-choices
At most one open at a time, one per scene, in non-adjacent slots; exactly one axis, ±1 per option, 2–3 options (format in `style.md`; the parser accepts "What does Darrow do?" and "say?"). Opened with `plan micro open N` when the scene is written; answered in any later message while open (a bare number is an answer only while a choice is open); `/choose` records it (ledger entry → `add` → `choices[]` → `plan micro close --option K`), and the consequence is folded into the opening of the next scene, no separate block. Unanswered, it carries across one scene; still open at the following close, it resolves to the slot's `default` (set at planning: the option the highest-approval companion present would pick, else the one that moves the quest), recorded `by: "bearing"` and closed with `--by bearing`; the Ledger reply says in one line that Darrow answered for himself. Every close-day Ledger reply ends with "Still waiting on Darrow: 1 … / 2 … / 3 …" while a choice is open. If a new micro is due while one is open, the open one resolves by default first (`plan micro close --by bearing` with no `--option` takes the planned default). The site labels a micro "A small choice" and a climax "The choice".

**The climax choice** carries across the first two scenes of the next chapter; if still open at the second close it resolves to `chapter.climax.default` (set at planning by the micro rule: the option the highest-approval companion present would pick), recorded `by: "bearing"`, and its `### Choice` block is written then. Slot 1 may be written while the choice is open: it covers the Sunday and ends before the choice is felt.

## 6. The arc file
`saga.py arc <id>` prints one section (≤ 40 lines) of `_gm/arc.md` by heading id: `## bookN.question`, `## bN.K — Title` (core beats), `## qN.id — Title` (quests, §5.2 fields), `## tN.high|main|low` (transition shapes, ending `- **carry-forward:**` matching the ledger rule), `## temptation`, `## flags`, and the top sections `## pacing`, `## truths`, `## motifs`, `## beliefs`. `check` validates every plan id against these headings. Never reveal a truth ahead of its schedule; plant twice first; the schedule may add plants, never move a reveal earlier.

## 7. Procedures (command sequences)

**Close a day** (the `/log` close). First the day's standing: **missed** means nothing logged at all (`darrow.py show daily D`, `show nutrition D` and `food list D` all print nothing): never create a row or a scene for it; `saga.py plan done N --skipped` and carry its world move into the next scene (`now` and `plan next` print it as owed). A day with any row at all is open: `darrow.py set daily D closed=Y` → `darrow.py sync` → `saga.py now` → `saga.py plan next --date D --full` → read the last scene (and `threads.md`) → write the scene in the slot's kind, the day's colour as tone, opening on any owed world move, folding in any open micro's answer and the due items you use → `saga.py plan done N --wrote chNN:sK` (it resets the stage to `scene`; `--force` to redo a slot; a quest's last stage marks the quest done when the slot carries `last: true` or the arc's count is reached, else `plan quest ID status=done`) → `saga.py fire ID --where chNN:sK` for each used item (`void` what the story made impossible) → `plan micro open N` if the slot had one → world.json (`scenes[]`, location, last_beat, quest `on_the_page`), characters, places, `NOW.md`, `threads.md` → `build_site.py` → commit.

**Choose** (`/choose`): identify the open choice (climax or micro) → write the ledger entry with `now` deltas (approval, bearing, flags by plan.json names, factions) and due items → `saga.py add '<json>' --witnessed a,b` → only then hand-edit `world.json → choices[]` with Edit, never Write → for a micro `saga.py plan micro close --option K [--by bearing]`; for a climax: if `saga.py now` still shows the climax's chapter at stage `climax`, `plan set stage=choice` (the engine refuses it at any other stage); if the next chapter is already open (the normal case after a checkpoint), do not touch the stage; then play the consequence as its own block, `fire ID --where chNN:climax` for what it pays off → `saga.py check`.

**Checkpoint** (Sunday): close Saturday (missed → `plan done N --skipped`, its spine content folds into the climax) → resolve any open micro by its default (`plan micro close --by bearing`) → `darrow.py chapter-close` → the real recap → `plan set stage=climax` → `saga.py now` (read ARMED and near rules and every DUE NOW / OVERDUE item before writing; `saga.py due` lists everything owed) → `saga.py plan climax` (question, plan, checks, options, default, world moves left) and `arc <beat>` → the climax (dice via `darrow.py roll --chapter N`; options may carry Bearing gates) ending in a choice → `/choose` when answered → `plan beat bN.K status=done` (the climax answered the chapter's beat) → if a Knot tied: `saga.py route decide --book N`, write the matching `tN.<road>` transition, `plan beat tN status=done`, `saga.py plan book open N+1` → `saga.py plan chapter open --number N+1 '<json>'` (refused while a micro is open) → world.json chapter fields and `recaps` by Edit → `saga.py check` → `build_site.py` → commit.

**Every session:** `saga.py now` after `darrow.py sync`; `saga.py check` before every commit that touched `saga/`.
