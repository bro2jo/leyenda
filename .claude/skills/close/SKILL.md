---
name: close
description: Close a day of the Ledger and write its scene in the Chronicle. Use when the user says "close day", or when a new day's first log arrives while the previous day has something logged and is not closed yet.
argument-hint: "[date; default: the last open day]"
allowed-tools: Bash(python3 engine/darrow.py *) Bash(python3 engine/saga.py *) Bash(python3 engine/build_site.py *) Bash(git *) Read Edit Write
---

# /close: the day's scene

One block of the page. The engine says what it must carry and may use (**the brief**), you write it, the engine records it (**the record**) and rebuilds every page from the records. Nothing about the story is edited by hand.

## 1. Which day
- `daily_log.csv → closed` is the truth. A day with any row at all (food alone counts) is open and gets its scene. A day with nothing logged is **missed**: never a row, never a scene: `python3 engine/saga.py plan done N --skipped` (N: its slot; `saga.py now` names it), and the next scene opens on the world move the brief then prints as owed. Several open days: oldest first, one scene each (one combined scene if he asks to catch up).
- A day already closed has its scene: a late log updates the Ledger only (`/log`).
- A new week's day while last week's chapter is unclosed: `/checkpoint` first; the engine refuses the close until the next chapter is open.
- A plan-directed rest day (`light=red`) is not missed: its scene is a **cutaway**, another POV or Darrow made to rest by others, never a setback frame.

## 2. Close, and read the brief
`python3 engine/darrow.py close DATE`: it sets `closed=Y`, syncs (read the **RECKONING CHANGES**: a LEVEL UP gets the reply's level-up block; a TETHER line means a stage's scene is owed to a float quest slot; the **RECKONING LINE** it prints is the reply's bracketed line, pasted whole: `.claude/skills/log/reply.md`) and prints **the brief** for the day's slot (`python3 engine/saga.py brief --date DATE` prints it again at any time). The brief is the whole picture:
- **MUST:** the slot's plan and turn, its device, the small choice it ends on, and what is owed: the open choice and its default, the DUE items, the owed world move, a rank beat, the Tether's line.
- **CONTINUITY:** where he is, the last block and its last beat, the season, what the knee may do on the page, what is in hand, the Betweens since the last scene and what they changed, today's glimpses, who is there by the page.
- **MAY:** the people the slot names (voice, tactic, regard, what they know), the threads with their plant counts and whether they may reveal, the Annals the plan names, callbacks that fit, the arc section.
- **FORMAT** and the **RECORD** skeleton.

Nothing else needs opening: not the character files, not the threads, not world.json, not the plan. On demand only: `python3 engine/saga.py arc <id>`, `lore <id>` / `lore grep <word>`, `history --person <id>` / `--thread N` / `--last 3`, `threads --id N`, and a person's full entry in `saga/bible/_gm/characters.md` (grep its `###` heading).

- **An open small choice** from the last scene, still unanswered: Darrow answers for himself with its default: `python3 engine/saga.py choose --by bearing '<ledger entry>'`; say so in one Ledger line; the consequence opens this scene in a clause. **An open climax choice** carries two scenes into the new chapter, then resolves the same way (`--which climax`), and its `### Choice` block is written then (`/choose` step 4).
- **A Tether stage** the sync reported: its scene is the next free float quest slot's (this chapter or the next, never a spine slot), and the brief says when a slot is it; a stage ahead of the story waits (`check` refuses it; the sheet climbs anyway).

## 3. Write
Read `saga/bible/style.md` §1 (the wall) and §2 (the craft), and the last block of the chapter file for its rhythm. Write the scene to the brief's **turn**, in the slot's kind, as long as its want, obstacle and turn need: the opening carries at most two things owed, each in a clause; the day's deeds colour Darrow alone (warm or cold in him, how he reads the room), never how others treat him; the content is the slot's; the outcome waits for the climax. A device runs as the brief says: a challenge's rolls through `python3 engine/darrow.py roll chNN-sK-<slug> …` with `python3 engine/saga.py challenge N success|fail` after each; an invitation is one in-world sentence as the reply's last line and the plan does not wait for it; a project stage writes its decision into the page. Lore touches as the scene's meaning needs (often one), received, never revealed. The Reckoning box at the end only for what `sync` reported; the small choice last if the slot carries one, in the brief's exact form. Append it under its heading. Then the reread (`style.md` §4): canon, who knows, continuity, debts, the turn, the sound.

## 4. Record
`python3 engine/saga.py record '<the brief's skeleton, filled>'`. One call writes the event and its GM note, marks the slot written, opens the small choice (`"micro_opened": true` when the scene ended on it), fires what the scene honoured (`"fired"`: due items, callbacks, rules, each with the scene's own words that pay it, verbatim: a consequence is proved on the page, never only marked), marks the Annals spoken (`"lore"`), takes a rank or Tether line, and rebuilds world.json, the character files, the Codex, the threads and the NOW page; then it runs `check`. An invitation offered at the last close that he did not answer is passed by this record, at its cost with that person (design §5.6): say so in one Ledger line. It refuses, writing nothing, a wrong key, a title that is not the heading, a person with no file, evidence that is not in the block, a name the page has not spoken (a codex item or a character file registers it; `--allow-names A,B` for a word that is not a name), an unknown thread or lore id. Fix what it names and run it again; `--force` re-records a revised block.

What goes in it: every person present (`did`, `now`, new `facts`, with `evidence` wherever a fact says what someone thought, meant, believed or knew), everyone only named (`mention`), `where` and `time`, `last_beat`, new codex items, the threads touched or planted (a new one in `gm.threads` with `"new": true`), `struggle` / `quest` / `season` / `inventory` when they changed, `now.against` and `now.next` when they moved, and `gm.note` for what the plan should know and what was kept off the page. A new person on the page: their base file first (`saga/characters/README.md`: identity, appearance, voice, relationships, reckoning; everything else is derived) and their entry in `saga/bible/cast.md`; a new place: `saga/state/places.json`.

## 5. Reply and save
Ledger: the day's totals vs targets, sessions vs plan, anything open for tomorrow, flags; the level-up block if `sync` reported one; the scene in story voice (no glimpse in a close reply); the invitation's sentence last if the slot carried one; "Still waiting on Darrow: 1 … / 2 … / 3 …" while a choice is open. Then `python3 engine/darrow.py ship -m "close DATE: chNN scene K, <title>"`.
