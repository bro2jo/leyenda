---
name: play
description: Role-play Darrow between scenes — he does or says something in the story's present moment that is not an answer to an open choice and not a log, and the scene extends from it (banter, a question put to someone, a look around, a small game). Use when the user narrates or asks for a Darrow action in the story ("Darrow goes to the kitchen and finds Rae", "RP: Darrow tells Hollis…", "/play …").
argument-hint: "[what Darrow does or says, in the story's present]"
allowed-tools: Bash(python3 engine/darrow.py *) Bash(python3 engine/saga.py *) Bash(python3 engine/build_site.py *) Bash(git *) Read Edit Write
---

# /play: a Between

A **Between** is the scene extended by Darrow's own hand: the story's present moment, between the last written scene and the next slot. **Every Between changes an understanding, a relationship, or a small obligation**: people answer him in voice, disagree with him, a thing said cannot be unsaid, and he carries something out of it. It never does the plan's work: nothing from the next slot, no scheduled revelation ahead of its time, no name, place or thing the page has not spoken, nothing with the knee the plan has not cleared.

## 1. Sort the message
- An answer to an open choice is `/choose`, first. Anything that reads like a log is `/log`, first (the Ledger reply, a rule, then the Between). A red flag: the red-flag reply, and no Between today.
- Otherwise: `git pull --rebase origin main`, then the brief.

## 2. The brief
`python3 engine/saga.py brief --between --with <who is in it: ids or names, comma-separated>`. It says how many Betweens have followed the last scene (**at most two**; a third is two lines and the moment passes), what the next slot owns (off limits), whether an invitation is waiting (then the other person opens with their want, not Darrow), what is owed, where he is and who is there by the page, each person's voice and tactic and regard, the threads, callbacks that fit, and the format. Read `saga/bible/style.md` §1 and §2, and the last block for its rhythm. `saga.py lore grep <word>` for a place, a custom or a game the Between touches.

## 3. The bounds
- **His action is honoured** when it fits the world, the cast and the sheet. People answer by their own tactic (the brief's under-pressure lines) and may refuse, deflect, lie or laugh; a question gets the whole answer, part of it, the wrong one, or none, and none is the rarest. Nothing the Annals mark `common` is withheld by anyone who would know it.
- **The knee:** nothing the real plan has not cleared (the brief's knee line); the world refuses in voice, never a lecture, never a reward for trying.
- **Scale:** as long as the exchange needs, usually 300–500 words; repeated movement, suppressed jokes and closing silences are cut before anything that changes something. It ends on a line that hands the moment back, **never on a choice list**.
- **Dice:** zero or one, only with stakes or a game: `python3 engine/darrow.py roll chNN-between-K-<slug> --stat … --dc … [--prof] [--adv|--dis]` (never `--chapter`), its first line pasted exactly. A failure costs a copper, a laugh or a line. Games: knucklebones with Hollis (Finesse 11; the rhyme `saga.py lore rhyme.knucklebones`), the pebble into the well-bucket (Finesse 12, `--prof` with The Measured Hand I), Wren's count (Resolve 10), the kitchen's book (a wager), name-the-load with Rae (Resolve 12). Stakes are in-world: a wick, a bottle, a chit in Wren's ledger, a line he has to hear again, approval ±1. **Never** XP, Inspiration, Ember, an Art, a Knot, the Tether.
- **The project:** a Between may lay a hand on the Book's project (`python3 engine/saga.py project ID work --where chNN:between-K --what "…"`); it never advances a stage.

## 4. Write
Append `### Between — Title` after the last block of the chapter file: a moment, close third on Darrow, past tense, the cast in voice. A dice line where the roll happens. No Reckoning box, no glimpse in this reply. Then the reread (`style.md` §4).

## 5. The consequence (one ledger entry at most)
Nearly every Between gets **one** terse entry (design §2; `made.scene` = `"between-K"`): `approval` −3 … +3 for those present who would care (Betweens move one companion at most ±6 net a chapter; the engine trims past that), `bearing` ±1 on **one** axis only when the action plainly lands on it, `flags` only by their names in `plan.json` and only ones the arc lets a Between set, `due[]` for anything the next scene must honour (`when: next`, weight `color` or `scene`), and a `when: "later"` callback for what has no date (a joke, a kindness, a promise for someday), with where it fits (`"fits": "present.hollis"`, `"place.saint_ysoldes"`, any term of the rule grammar), how much it is worth (`"priority"`: 1 a line, 2 the default, 3 worth a beat) and, for a promise, when it lapses and what that costs (`"valid_until": "book1"`, `"if_void": {"approval": {"rae": -3}}`). `python3 engine/saga.py add '<json>' --witnessed <ids present>` (`--learned <id>:<how>` for a companion who was not there and hears of it; an approval delta for anyone else is refused: regard moves only for who saw it or was told). Never edit approval or the Bearing by hand. Nothing in a Between ties a Knot, moves a quest stage, pays a due item of the plan's, or closes a slot.

## 6. Record
`python3 engine/saga.py record '<the brief's skeleton, filled>'`: `where` (always: where he is at the Between's end), `time`, `last_beat`, the people with `did` / `now` / new `facts` (with `evidence` where the README requires it), codex items for a new saying or thing, threads touched, a callback fired (`"fired": [{"id": …, "evidence": "<the Between's words that pay it>"}]`, one per block at most), `"invite": {"slot": N, "action": "take"}` when it answered an invitation, `gm.note` only when a later scene must honour something (name the ledger id). It rebuilds world.json, the character files, the Codex and the NOW page, then runs `check`.

## 7. Reply and save
The Between, as written, in story voice; nothing else, unless a Ledger came first. "Still waiting on Darrow: 1 … / 2 … / 3 …" if a choice is open. `python3 engine/darrow.py ship -m "play chNN between-K: <title>"`.
