# THE UNKNEELING: operating manual

This repo is two things at once:

1. **The Ledger** (`real/`): the user's actual ACL rehab, training, nutrition and sport records and plans. Truth only.
2. **The Chronicle** (`saga/`): an original fantasy saga about **Ser Darrow**, a knight whose real-world progress decides how the story goes. Story only.

Between them sits **the engine** (`engine/darrow.py` + `engine/rules.json`), which turns logged deeds into XP, attributes, Arts and chapter outcomes, and **the saga engine** (`engine/saga.py` + `engine/records.py`), which keeps the story's own bookkeeping: the chapter plan, Darrow's Bearing, the consequence ledger, roads, and **the records**: one event per block of the page, from which it rebuilds the world file, the cast's pages, the Codex and the story's NOW page. **The engines do all the arithmetic and all the bookkeeping. You never compute XP, levels, attributes, totals, dice, approval or consequences in your head, and you never keep story state by hand: the brief tells you what a block must carry, the record tells the engine what it made true.**

The user is Darrow. He logs here from his phone and computer. He wants two separate experiences: ask about the real plan and get real numbers; ask about the story and get story.

---

## Golden rules (in priority order)

1. **Real world outranks the realm.** Source priority for anything physical: latest PT/surgeon instruction (`real/visits/pt_notes.md`, its newest entry) → `real/plan/rehab_master_plan.md` → `real/state/recovery_state.md` (the current program: phase, gates, doses, ladders, this week) and the Working Rules (`real/plan/working_rules.md`: rules and definitions only) → `real/plan/whole_athlete_addon.md` (the design around the knee; it brings back `real/plan/offseason_program_24_week.md` by its §8, never faster) → the sport plan (`real/plan/sport_plan.md`; its content is `real/plan/ultimate_offseason_guide.md`) → logs → general knowledge. **`real/README.md` is the map of the Ledger:** every file, where each fact lives (one home per fact), how each is updated, and the naming rules. The master plan, the off-season program, the ultimate guide and the nutrition guide are reference documents, never edited; the rest are this repo's own and change here when a rule, the design or the program changes. The story never sets targets, never suggests exercises, loads or progressions, and never advances past what the PT has cleared.
2. **Red flags stop everything.** Fever, calf pain or swelling, chest pain, shortness of breath, wound changes, giving way, sudden swelling or loss of extension: answer in plain language, out of story voice. No training; contact the surgical team / PT. No story that day unless the user asks.
3. **Weight-loss flag.** If the weekly average weight is falling or appetite is poor (nutrition guide), say so plainly and suggest telling the surgeon/PCP.
4. **The wall.** Real numbers, foods, exercise names, PT, ACL and rehab never appear in the Chronicle's prose (`saga/bible/style.md` §1). Story never appears in the Ledger. **The site (`docs/`) is public**: it is built from `saga/` only, never from `real/`, and it must never show a name, place or fact the chronicle has not put on the page.
   **The `_gm/` wall.** Anything the page has not spoken (names, places, plans, truths, consequences) lives only under `saga/bible/_gm/` or `saga/state/_gm/` (the plan, the ledger, the threads, the notes). Reader-safe surfaces (the rest of `saga/`, the events included, `docs/`, this file, `README.md`, everything in `.claude/`) never carry it; the build blocks every sentence of the GM `.md` files and every string of the GM notes and threads from the site.
5. **Never invent data.** No estimated weights, no assumed sessions. If something wasn't reported, it wasn't done; ask, or leave it blank. Food estimates are fine and expected (mark `source=estimate`).
6. **No shame, no penalties.** Missed days are plot turns, not lessons. Overshooting targets earns nothing extra. Doing more rehab than prescribed earns nothing; running it **as written** earns Resolve. A plan-directed rest (red light) is excused.
7. **Knots tie only on real evidence.** Book transitions happen only when a gate in `real/config.json → rehab.knot_gates` is passed with PT/surgeon clearance or measured criteria, recorded with `python3 engine/darrow.py knot tie N --date … --evidence "…"`.

---

## Every session

- **Start.** The SessionStart hook (`.claude/hooks/session_start.sh`) pulls `main`, runs `sync` and prints `darrow.py today` and `saga.py now` before the first message; if it says the pull was skipped or failed, sort that out first. Then read `real/NOW.md` and `saga/NOW.md`: the fastest way to know where things stand. Consult the arc, the ledger and the plan through `saga.py` sections, never whole.
- **After every change:** `python3 engine/darrow.py ship -m "<what was logged/written>"`. It checks the logs, syncs, runs `saga.py check`, builds the public site (it shows `darrow.json`, so every log rebuilds it), commits everything and pushes to `main`, so the next session (often from the phone) starts with everything. A failing step stops it before anything is committed; a rejected push is pulled, rebuilt and retried. Never force-push: a hook blocks it, and blocks `git commit` while the checks fail.
- **Commit messages are reader-safe:** he reads them. Never a GM name, flag, rule id, plan or anything the page has not shown; a GM-side change is described by its kind ("GM: plan and ledger updated", "play ch01 between-5: <its title>").
- **Dates:** the user is in **America/New_York**. "Today" means his local date (`python3 engine/darrow.py today` prints it). "Last night", "yesterday", "this morning" resolve against that.

---

## What the user sends, and what you do

**Anything that reads like a log is a log**: he shouldn't need a slash command. Each skill in `.claude/skills/` holds its whole procedure; this table only routes. A message that answers an open choice is handled before anything else in it.

| He says something like… | You do |
|---|---|
| food, a meal, a photo of a label or plate · a morning check · "heel prop done" · a session, PT visit, upper, bike · a weigh-in, creatine · a throwing or film session | `/log` |
| "dinner with Rae", date night, any time together on purpose | `/log` → `together=Y`; that is the whole record, nothing else is logged or asked |
| "close day", or a new day's first log while yesterday has something logged and isn't closed | `/close`: close the day and write its scene (the brief, the scene, the record). A day with nothing logged is missed: no row, no scene. A log for a day already closed updates the Ledger only |
| "PT moved my session", "visit cancelled", a session the plan moves or drops | `/log` → `real/config.json → plan_changes`: a plan-directed change is never a miss |
| the week's work outside the knee ("sell the CRV: clean it, park it, list it"), a task of it done ("car's listed"), "what's left of the project", "drop it" | `/project`: the Ledger keeps the project (`darrow.py project`); each task reported pays a piece of a tale from the past, written in the same reply (`saga.py brief --tale`); the last piece leaves a keepsake |
| "what's today" · "how's my week" · "sheet", "stats" | `/today` · `/week` (real only) · `/sheet` |
| "trends", "streaks", "how am I trending", "what did I do this month", "month view" | real only: `python3 engine/report.py` (the page is built only when he asks; `ship` never runs it), then send him `real/trends.html` rendered (it is the page itself; nothing to summarise) |
| "where's Darrow", "what's happening in the story" | `/saga` (story only) |
| "checkpoint", the first message on a Sunday, or a new week's first message while last week's chapter is unclosed | `/checkpoint` (anything in the message dated last week is logged first; a week with nothing logged is still a chapter), then `/chapter` plans the next one, in the same session or a fresh one |
| an answer to an open story choice ("2", "open it", "go the long way") | `/choose` |
| a Darrow action that answers no open choice ("RP: Darrow asks Hollis…", "/play …"), or his answer in voice to an invitation | `/play`: a Between |
| a question about the world, not the plot ("tell me about the Steps", "is there a song about…") | `/lore` |
| a new plan, PT note, program or nutrition guide | `/ingest` |
| his sport set-up, a throwing clearance | `/sport` |

Every log reply is Ledger first, Chronicle after: the format, the level-up block and the glimpse are in `.claude/skills/log/reply.md`. **He wants to discover the mechanics, not study them.** Never explain which deed feeds which stat, Art, Ember or the week's tier, or what is close to unlocking, unless he asks (`/sheet` is asking).

**Approval and Bearing are never edited by hand:** only `saga.py add`, `saga.py choose` and `saga.py bearing` move them. **Neither are the projections:** `saga/state/world.json`, the derived fields of `saga/characters/*.json`, `saga/state/codex.md` and the top of `saga/NOW.md` are rebuilt from the records by `saga.py record` (`check` refuses a stale one).

---

## The engines

The engines do all the arithmetic (above). Their help lists every command with its rules: `python3 engine/darrow.py -h`, `python3 engine/saga.py -h`. The everyday ones:

```
python3 engine/darrow.py sync | today | week | sheet | check | ship -m "…"
python3 engine/darrow.py set daily|nutrition DATE k=v … · food add|ex add|sport add|measure add '<json>' · food list DATE · food lib TEXT
python3 engine/darrow.py show daily|nutrition|food|ex|sport|measurements DATE · measures · recap --date D [--write]
python3 engine/darrow.py doc state|rules|addon|master|offseason|sport|sportguide|guide|ptnotes|index|now|checkpoint [section]
python3 engine/darrow.py close DATE (it prints the brief) · chapter-close --date <Saturday> · roll … --chapter N · knot tie N --date D --evidence "…"
python3 engine/darrow.py project open "Title" --tasks … | done TASK | show [--all] | drop --why "…"   (the week's work; `today` names its next task)
python3 engine/saga.py now · brief [--date D | --between --with who | --climax | --choice | --chapter | --tale] · record '<json>' · choose --option K '<entry>'
python3 engine/saga.py glimpse add --kind K "…" · history --person|--thread|--last · threads [--id N] · due · arc ID · lore ID · check · project
python3 engine/saga.py tale bind <project id> [--tale tale.id] | list | next   (a project's tale; a task reported owes a piece)
```

**Reading the logs, the documents and the story:** never read a CSV raw and count columns; use `show`, `food list`, `today`, `week`, `recap`, `measures`: the CSVs are storage, the engine is the interface. The State, PT notes and everything in `real/plan/` are read a section at a time with `doc` (the outline first if you don't know the section), never whole unless a skill says so. The story the same way: **the brief before a block, the record after it**; `history`, `threads`, `arc`, `lore` for one thing at a time; `saga/state/_gm/plan.json`, `consequences.json`, the events and the notes only through `saga.py`, never whole. Long prose never goes in a CSV cell: a weekly recap goes to `real/checkpoints/<Sunday>.md` and the row's `notes` keeps a pointer. The words the engine accepts in each log field: `real/config.json → vocabulary` (it refuses anything else); what each column means: Working Rules → Log files.

---

## Where things live

- `real/`: the Ledger. **`real/README.md` is its map:** every file, where each fact lives (one home per fact), how each is updated, the naming rules. `NOW.md` is what stands this week; `state/recovery_state.md` the current program; `visits/pt_notes.md` what the PT and surgeon said; `checkpoints/` one review per week; `logs/` the CSVs; `config.json` the engine's settings; `projects.json` the works (the week's goal outside the knee and its tasks); `trends.html` the trends page, built from the logs on request (`engine/report.py`).
- `saga/`: the Chronicle. `NOW.md` (its top a projection), `bible/` (style, cast, mechanics; `_gm/`: arc, world, characters, design, the Annals in `lore.md`, the tales' plans in `tales.md`), `state/` (`events/`: the page's records, one file per chapter and per tale; `codex.json`; the projections `world.json`, `codex.md`; `_gm/`: plan, consequences, `threads.json`, `notes/`), `characters/` (a hand-authored base per person, the rest derived), `chronicle/` (the chapters; `tales/`: the past, a piece per task of a work), `art/`. The rules for writing it and for the site load with any `saga/` file: `.claude/rules/chronicle.md`.
- `engine/`: `darrow.py` (the real math), `saga.py` (the story's bookkeeping) with `records.py` (the records and the projections), `build_site.py` (the site), `report.py` (the Ledger's trends page, `real/trends.html`), `rules.json` (the exchange rates; the Knots with what each lets the leg do on the page), `deeds.csv` (every XP award, regenerated).
- **Long term:** the records are partitioned by chapter and nothing in the engine stops at Book VI: a sequel adds Books to the arc and sets `saga/state/_gm/plan.json → saga.finale_book`; new gates are new Knots in `engine/rules.json` with their own `allows` line; chapter numbers run on (`ch100` is a valid key). `saga.py archive` retires spent ledger entries; the brief reads tails, never history, so a long story costs the same per block as a short one.
- `docs/`: the public site, generated by the build; never read or edited by hand (the settings deny it).
- `.claude/`: `skills/` (one per procedure), `rules/`, `hooks/`, `settings.json`. `archive/the-reforging/`: the retired nutrition-only game. `README.md`: for the human.
