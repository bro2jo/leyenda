---
name: saga
description: Story-only view — where Darrow is, the current quest, the battle or struggle he's in, companions, the last scene, the open choice, and his Reckoning. Use when the user asks about the story, Darrow, the chapter, or "what's happening". No real-world numbers.
argument-hint: "[optional: recap | read | threads]"
allowed-tools: Bash(python3 engine/darrow.py *) Bash(git *) Read
---

# /saga: the Chronicle, right now

1. `git pull --rebase origin main`. Read `saga/NOW.md`, `saga/state/world.json`, and the current chapter file in `saga/chronicle/`.
2. Default answer (story voice for the content, plain headings for structure):
   - **Book · Chapter** and where Darrow is.
   - **The fight right now:** the external threat (quest, enemy, clock) and the internal one (what he's struggling with).
   - **With him:** each present companion in one line, with their mood toward him (from approval, said in words, never as a number).
   - **Last time:** 2–3 sentences recapping the most recent scene, ending on its last beat.
   - **Waiting on you:** the open choice, if there is one, exactly as written in the chapter.
   - **The Reckoning:** `python3 engine/darrow.py sheet` in a code block.
   - **How the chapter is going:** the tier so far in story terms ("the week is turning against him", "hard-won so far"), never the score.
3. Variants from $ARGUMENTS: `read` prints the latest full scene; `recap` gives a "previously on" of the whole Book so far (no spoilers from `_gm/arc.md`); `threads` lists open threads **he has seen on the page** (never GM-only truths).
4. **The wall:** no foods, numbers from logs, exercises, PT or rehab terms. Game numbers (level, attributes, DCs) are fine.
