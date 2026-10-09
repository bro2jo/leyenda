---
name: sheet
description: Show Darrow's Reckoning (LitRPG character sheet) — level, XP, attributes vs the Knight Who Fell, Ember, Inspiration, Knots, Arts and what's close to ranking up. Use when the user says sheet, stats, level, or asks about Darrow's numbers.
allowed-tools: Bash(python3 engine/darrow.py *) Bash(git *) Read
---

# /sheet

1. `git pull --rebase origin main`, then `python3 engine/darrow.py sync` and `python3 engine/darrow.py sheet --json`.
2. Show the text sheet (first part of the output) in a code block, exactly as printed.
3. Below it, at most three short lines of "what's close", derived from the JSON:
   - XP to the next level.
   - Any attribute within a few temper points of its next point (`next_at` vs `temper`), and any attribute capped by the Binding (`banked: true`). Say what's held back: "Finesse is straining against the Binding."
   - Any Art within 2 days of practice of its next rank, and sealed Arts with banked practice.
   - The Tether, once it is tied: days together to its next stage (`tether.next_at` vs `tether.days`), said as days, nothing more.
   Say these in game terms (practice days, temper), never in real-world terms (no foods, no exercises).
