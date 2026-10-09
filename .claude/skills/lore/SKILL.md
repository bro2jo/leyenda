---
name: lore
description: Tell him about the world in its own voice from the Annals — a place, a custom, a song, a saying, how something in the realm works — without touching the story's plan, the ledger or the page. Use when he asks about the world rather than the plot ("tell me about the Steps", "what are the Lances", "is there a song about…", "how does sanctuary work", "what do they use for money").
argument-hint: "[what he wants to know about the world]"
allowed-tools: Bash(python3 engine/saga.py *) Bash(git *) Read Edit Write
---

# /lore: the Annals, told

A telling, not a scene. The Annals (`saga/bible/_gm/lore.md`) hold the realm's history and texture; this skill lets him hear the part the kitchen knows, in the House's voice, and nothing moves for it.

## 1. Find it
- `git pull --rebase origin main`, then `python3 engine/saga.py lore` (the index) and `python3 engine/saga.py lore grep <word>` for his subject; read only the entries that answer him (`python3 engine/saga.py lore <id>`), never the file whole.
- Read `saga/state/codex.md` and the names in `saga/characters/` only to know what the page has already named.

## 2. What may be told
- A `common` entry: freely.
- A `learned` entry: only if its `spoken:` is set (the page has opened it). Otherwise the answer is, in voice, that it is a Mender's question, or a clerk's, or an elder's, and nothing of the content.
- **Never:** a `⟪gm: …⟫` aside, a truth from the arc, anything from the chapter plan, the quests, the climax or the consequence ledger, anything from `real/`, a mechanic of the game, or a name in an entry's `names:` field that the page has not spoken. Paraphrase around such a name ("the king", "the fog coast", "the sanctuary bell") rather than saying it.

## 3. How it is told
- In a House voice chosen for the question, 60–200 words: Wren with a number, Hollis with a grudge, a lay brother on the Steps, the kitchen passage, a Mender's margin, or the song itself in two to four lines. One voice per telling.
- It is texture, not plot: no Darrow acting or deciding, no one else deciding anything either, no dice, no choice list, no Reckoning box, no glimpse, nothing the next scene must honour. Nothing told here is "on the page"; it binds the world, not the story.
- Keep it short enough to read on a phone. End when the telling ends.

## 4. When the Annals have no answer
- Invent one that fits, under the doctrine at the top of `lore.md`: received, not revealed; no new plot (no faction with an agenda, no antagonist, no prophecy, no object of power); the fixed numbers hold; names from the palette in `saga/bible/_gm/characters.md`; nothing that forecloses a planned beat (when unsure, `python3 engine/saga.py arc pacing` and the beat ids the entry would touch).
- **Write it into `lore.md` first**, as a `common` entry in the file's shape (`## kind.id — Title`, the tier/spoken/names line, the use line, two to eight lines of text), under the right kind; then tell it. One new entry per question at most.
- `python3 engine/saga.py check` (it parses the Annals), then `git add -A && git commit -m "lore: <id>" && git push origin HEAD:main`.

## 5. Afterwards
- If the Chronicle later speaks the entry, that scene's close marks it (`python3 engine/saga.py lore spoke <id> --where chNN:sK`) and gives `codex.md` its reader-safe line. This skill never does that.
