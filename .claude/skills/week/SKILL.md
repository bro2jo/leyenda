---
name: week
description: Real-world view of this week (Sun–Sat) — daily table of nutrition, weigh-ins, floor, checks, sessions; averages vs targets; what's left in the plan; flags. Use when the user asks how the week is going or what this week's plan is. Ledger only, no story.
argument-hint: "[optional date in the week]"
allowed-tools: Bash(python3 engine/darrow.py *) Bash(git *) Read
---

# /week: the Ledger, one week

1. `git pull --rebase origin main`, then `python3 engine/darrow.py week` (add `--date` if asked about another week).
2. Show the engine's table and summary lines as they are.
3. Add, from the plan files:
   - **Remaining this week:** each day's planned sessions and doses, PT day, the optional items (and whether they're earned: a missed floor day costs next week its optional items, per the add-on §2).
   - **Targets check:** average kcal and protein vs target; weigh-ins so far vs 3; the nutrition guide's adjustment rule if two consistent weeks are in.
   - **Rehab flags** from the recovery state "patterns and concerns": e.g., floor X/7, swelling graded X/7, upper 2/2, bike 3/3, phase-gate items still open.
4. Real numbers only. No story, no week score. If he wants to know how the chapter is going, that's `/saga`.
