---
name: today
description: Real-world plan for today — sessions with their current doses, what's already logged, what's left, nutrition still to go. Use when the user asks what today's plan is, what's left, or what to do now. Ledger only, no story.
argument-hint: "[optional date]"
allowed-tools: Bash(python3 engine/darrow.py *) Bash(git *) Read
---

# /today: the Ledger, one day

1. `git pull --rebase origin main`, then `python3 engine/darrow.py today` (add `--date` if $ARGUMENTS names a day).
2. Read the newest `real/state/ACL_Recovery_State_*.md` §6 (current program, ladders, minimum sessions) and `real/plan/Whole_Athlete_AddOn.md` (upper, accessory, conditioning, power). Check `real/NOW.md` for open items and the PT question list.
3. Answer, real numbers only, compact enough for a phone:
   - **Planned today:** each session with today's doses (e.g., Session A: SL sit-to-stand 24" 2 × 12 L …), the floor minimum, conditioning, and the minimum version if he's short on time (the plan's "short on time" cut order).
   - **Done so far** (from the engine).
   - **Still open**, in priority order: floor first, then the knee session, then add-ons.
   - **Nutrition:** kcal and protein to go, and one practical way to close the gap (based on what he usually eats).
   - **PT day:** list the questions to ask.
4. No story content. If he wants the story, that's `/saga`.
