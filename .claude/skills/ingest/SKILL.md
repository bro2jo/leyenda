---
name: ingest
description: Bring a new or updated real-world document into the Ledger — a PT note, a program, the working rules, a recovery-state checkpoint, an old log CSV, nutrition instructions, a sport plan — and update targets, schedule, phase and gates to match. Use whenever the user shares a plan, program, PT instructions or log file.
argument-hint: "[file or pasted text]"
allowed-tools: Bash(python3 engine/darrow.py *) Bash(python3 engine/saga.py *) Bash(git *) Read Edit Write
---

# /ingest

1. Read the whole document first. Decide what it is:
   - **A PT or surgeon visit note** (written or as he reports it): `real/visits/YYYY-MM-DD_PTn.md` (or `_surgeon.md`) with the headings Measured · Session · Instructions · Questions · Next morning; every measured number also goes to `real/logs/measurements.csv` (`python3 engine/darrow.py measure add '[…]'`, one row per side, `visit` = the file's stem); exercise rows to the exercise log with `session=PT`; `daily_log` gets `pt=Y` and a one-line `notes` pointer to the file. Then NOW's top: the next visit's questions (drop the ones answered), the gate, and "PT n outranks the state file until the checkpoint folds it in".
   - **Authority** (rehab plan, Working Rules, a program): goes to `real/plan/`. Keep the original filename. Give it markdown `##` headings for its numbered sections (wording unchanged) so `doc` can read it a section at a time, and add it to the `doc` names in `engine/darrow.py` if it will be read often.
   - **A recovery-state checkpoint:** it becomes the one file in `real/state/`, in the current structure (`python3 engine/darrow.py doc state` prints the outline); the previous one moves to `real/state/archive/`. Any week-in-review or measurements log in it goes to the matching `real/checkpoints/<Sunday>.md` and `measurements.csv`, not into the state file.
   - **Log** (e.g., `ACL_Daily_Log.csv`, an older nutrition log): merge into the matching file in `real/logs/` by date. Map columns to the current schema, never duplicate a date, and keep any column that doesn't map in `notes`. Run `python3 engine/darrow.py check`.
   - **Nutrition project instructions:** save to `real/plan/nutrition_instructions.md` and adopt its food-line and recap formats in `.claude/skills/log/SKILL.md` and `CLAUDE.md` ("Reply shape for a log"), keeping the Ledger-then-Chronicle structure.
   - **Sport material:** hand over to `/sport`.
2. Update what it changes, citing the document in each `source`/`evidence` field:
   - `real/config.json`: nutrition targets, `weekly_template`, `rehab.current_phase`, `next_gate`, `knot_gates`, milestones.
   - `CLAUDE.md` → Golden rule 1's source-priority list, if it's a new authority.
   - the top section of `real/NOW.md` (plan in force, next PT visit and its questions, the gate, flags).
3. Contradictions: if it conflicts with something already here (dates, doses, targets), the source priority in CLAUDE.md decides. Say plainly what changed and what you couldn't reconcile, and ask one question if needed.
4. Never touch the story here. If it ties a Knot (a gate passed with PT/surgeon clearance or measured criteria), record it with `python3 engine/darrow.py knot tie …`, then `python3 engine/saga.py now`; the remaining `planned` slots of the week are re-planned toward the crossing (`python3 engine/saga.py plan slot N key=value …`: plan, kind, beat or quest+stage, micro as JSON; then `python3 engine/saga.py check`), and Sunday's climax is the Book's transition (`/checkpoint` runs `route decide`, then `plan book open N+1` before the next chapter opens).
5. `python3 engine/darrow.py sync`, then commit and push: `git add -A && git commit -m "ingest: <file>" && git push origin HEAD:main`.
6. Reply: what the document is, what it changed (targets, schedule, gates), and anything still open. Real only.
