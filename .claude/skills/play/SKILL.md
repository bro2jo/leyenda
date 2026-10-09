---
name: play
description: Role-play Darrow between scenes — he does or says something in the story's present moment that is not an answer to an open choice and not a log, and the scene extends from it (banter, a question put to someone, a look around, a small game). Use when the user narrates or asks for a Darrow action in the story ("Darrow goes to the kitchen and finds Rae", "RP: Darrow tells Hollis…", "/play …").
argument-hint: "[what Darrow does or says, in the story's present]"
allowed-tools: Bash(python3 engine/darrow.py *) Bash(python3 engine/saga.py *) Bash(python3 engine/build_site.py *) Bash(git *) Read Edit Write
---

# /play: a Between

A **Between** is the scene extended by Darrow's own hand: the story's present moment, between the last written scene and the next slot, played out from what he does. It is texture with teeth: people answer him in voice, a small thing can be won or lost, a thing said cannot be unsaid. It never does the plan's work. The plan does not move for it, and it does not move for the plan.

## 1. Sort the message first
- An answer to an **open choice** (climax or micro: `python3 engine/saga.py now` prints the micro, `saga/NOW.md` the climax's) is `/choose`, handled first; the rest of the message may then be played.
- Anything that **reads like a log** is `/log` first; the Ledger reply comes first, then a rule, then the Between.
- A **red flag** in the message: the `/log` red-flag reply, and no Between that day.
- Otherwise: `git pull --rebase origin main`, `python3 engine/saga.py now`, and this skill.

## 2. Read before writing
The last scene and any Betweens after it (the current chapter file); `saga/bible/style.md` §1 and §3 ("A Between"); `saga/bible/cast.md` for everyone present; `saga/bible/_gm/characters.md` **only** the `###` entries of those present; `saga/state/_gm/threads.md`; the tail of `saga/state/glimpses.md` (a Between may echo a glimpse, never contradicts one). `python3 engine/saga.py plan next --full` only to see what the next slot owns, so the Between stays off it; never to use its content.

## 3. The bounds (the whole point)
- **When and where:** the story's present, after the last written scene, before the next slot. The same place, or wherever the House (or the camp, on the road) lets him go on his own legs within what the page has already allowed.
- **His action is honoured** when it fits the world, the cast and the sheet. People answer in their own voices (`cast.md`), and they may refuse, deflect, lie or laugh. If he asks a question the schedule has not answered, the person answers the way they would: Maelis with a sharper question, Wren with a number, Hollis with an insult, Rae once and plainly or not at all. **Never a truth ahead of its schedule, never a plant, never a reveal, never a name, place or thing the page has not spoken** (unnamed lay brothers, novices, the kitchen, the kennel-master are fine), nothing from the next slot, the chapter plan, the quests, the world moves or the climax. Nothing real (§1 of `style.md`).
- **The knee.** No stair down, no running, no fight on his feet, no testing the Binding, nothing the real plan has not cleared: the world refuses in voice (Maelis's no, the law of bells, his own leg, Wren's count of his refusals), never a lecture, and never a reward for trying.
- **Scale.** 120–300 words. **At most two Betweens between two scenes**; a third gets two lines and the moment passes (a bell, a door, Maelis's hand), and anything more waits for the next day's scene. A Between ends on a line that hands the moment back (a look, a bell, a door, a last word), **never on a choice list**: choices belong to scenes and climaxes.
- **Dice.** Zero or one roll, only where there are stakes or a game: `python3 engine/darrow.py roll chNN-between-K-<slug> --stat <might|vigor|finesse|resolve> --dc <8–20> [--prof] [--adv|--dis]` (never `--chapter` or `--tier`; a Between is not a climax). Paste the engine's first line exactly, on its own line. A failure costs a copper, a laugh or a line, never the day.
- **Games (optional, when he asks for one or the moment offers it):** knucklebones with Hollis (Finesse DC 11; the stake a copper or a story) · the pebble into the well-bucket (Finesse DC 12, `--prof` if the sheet shows The Measured Hand at rank I or more) · Wren's count (Resolve DC 10: keep a count while she talks at him) · the kitchen's book (a wager on anything the House can see from a window) · name-the-load with Rae (Resolve DC 12: say what a cart carries by the sound of it; she is never wrong). Stakes are in-world: a copper, a bottle, a chit in Wren's ledger, a line he has to hear again, approval ±1. **Never** XP, Inspiration, Ember, an Art, a Knot, the Tether.

## 4. Consequences (one ledger entry at most)
A Between that changes nothing needs no entry. One that does gets **one** terse entry (`saga/bible/_gm/design.md` §2), `made.scene` = `"between-K"`:
- `approval` −3 … +3 for those present who would care (a game lost gracefully, a cruelty, a kindness, a confidence kept or broken);
- `bearing` ±1 on **one** axis, only when the action plainly lands on it (the usual witnessed ±2 applies);
- `flags` only by their names in `plan.json → flags`, and only ones the arc lets a Between set (a secret told is `due`, below, not a flag, unless the arc names one);
- `due[]` for anything the next scene must honour (`when: next`, weight `color` or `scene`; a told secret, a promise, a quarrel): the plan bends to it at the next `plan slot` edit or `plan chapter open`, never by rewriting the slot's content from here.
`python3 engine/saga.py add '<json>' --witnessed <ids present>`; never edit approval or Bearing by hand. Nothing in a Between ties a Knot, moves a quest stage, pays a due item of the plan's, or closes a slot.

## 5. Write it
Append to the current chapter file, after the last block:
```
### Between — Title

…120–300 words, close third on Darrow, past tense, the cast in voice…
```
A dice line goes where the roll happens. No Reckoning box (the engine's notifications belong to scenes). No glimpse in this reply: the Between is the glimpse's big brother.

## 6. Bookkeeping, then the site
- `saga/state/world.json` by Edit: `scenes[]` gets `{"scene": "between-K", "title": "…", "after": "<key of the scene it follows: 2, interlude, climax>", "covers": [], "written": "YYYY-MM-DD"}`; `last_beat` becomes the Between's last beat; `location.detail` if he moved within the place. Never approval.
- The people in it: `last_seen` `{chapter, scene: "between-K", place, anchor: "chronicle/<file>.html#between-K"}`, `last_seen_doing`, `now`, `appearances` (`{"chapter": "NN", "scene": "between-K"}`), new `known_facts` for anything the page now says; `quote` if a better line landed. `codex.md` for a new saying or thing; `saga/state/_gm/threads.md` only when a later scene must honour something (name the ledger id).
- The narrative top of `saga/NOW.md`: one line under "Just happened" if it changed anything.
- `python3 engine/saga.py check` and `python3 engine/build_site.py` (both must pass), then `git add -A && git commit -m "play chNN between-K: <title>" && git push origin HEAD:main`.

## 7. Reply
The Between, as written, in story voice; nothing else, unless a Ledger came first. If a choice is still open, end with "Still waiting on Darrow: 1 … / 2 … / 3 …". The next day's scene opens by taking the Between into account in a clause, then does its own slot's work.
