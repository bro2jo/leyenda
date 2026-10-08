---
name: sport
description: Set up or update the sport-specific add-on — the sport, its key skills and drills, which are safe in each rehab phase, how to log them — and turn each skill into an Art in the saga. Use when the user mentions his sport, sends a sport program, or wants sport work tracked.
argument-hint: "[sport, skills, or a program file]"
allowed-tools: Bash(python3 engine/darrow.py *) Bash(git *) Read Edit Write
---

# /sport

## 1. Gather (one message, only what's missing)
Sport and position · season dates / target return · the 5–8 skills that matter most · the drills he does for each and how they're measured (reps, makes, time, distance, velocity) · equipment and where he trains · any coach or program file (if there is one, read it first and ask less).

## 2. Gate every skill by the rehab plan
Using `real/plan/ACL_Reconstruction_Rehab_Master_Plan.md` and the add-on's §10 table, give each skill and drill the **earliest Knot** at which it's allowed:
- seated / static / upper-body / hands-only technique → Knot II (now)
- standing, symmetric stance, no impact → Knot III (Phase 4), only if the PT agrees
- running-based → Knot IV · jumping, landing, sprinting, decel → Knot V · cutting, pivoting, reactive, contact, game speed → Knot VI · full competition → Knot VII
When unsure, choose the later Knot and list it as a question for the PT. **Nothing here may move a left-knee item earlier than the plan allows.**

## 3. Write the real side
- `real/plan/sport/sport_plan.md`: the skills, drills, metrics, Knot gate per drill, weekly placement (respecting the add-on's no-back-to-back-loaded-days rule), and the PT questions.
- `real/config.json → sport`: name, position, season.
- `real/config.json → weekly_template`: add sport sessions only where the plan has room.
- The logging format: `sport_log.csv` columns `date, session, skill, drill, sets, reps, minutes, rpe, metric, value, notes`; `skill` must be one of the skill ids you defined.

## 4. Write the saga side
- Add one entry per skill to `engine/rules.json → sport_arts.arts`: `{"skill": "<id>", "id": "<art_id>", "name": "<Art name>", "tree": "Sport", "knot": <n>, "effect": "<what it lets Darrow do>"}`.
- Art names: evocative, grounded, medieval-martial, never cheesy and never the sport's own terms (a passing skill might become "The Long Thread"; a shooting skill "Kingfisher's Strike"). Effects must be things a knight can use in a fight, a chase or a council.
- Add the new Arts to the table in `saga/bible/mechanics.md`.
- Add a planned scene to `saga/state/world.json → chapter_plan.later_scenes` where someone teaches the first of these Arts (Hollis, or later Ysra Tal). **Never name the real sport in the prose.**

## 5. Finish
`python3 engine/darrow.py sync` · commit and push · reply with the skill→Art map, the gates, and the PT questions.
