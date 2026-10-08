---
name: choose
description: Record Darrow's answer to an open story choice and play out its immediate consequence. Use when the user answers a choice ("2", "expose him", "stay hidden") or tells Darrow what to do in the story.
argument-hint: "[option number or what Darrow does]"
allowed-tools: Bash(python3 engine/darrow.py *) Bash(git *) Read Edit Write
---

# /choose

1. `git pull --rebase origin main`. Find the open choice in `saga/NOW.md` / the current chapter.
2. Match $ARGUMENTS to an option. If he invents his own option, accept it if it fits the world and his sheet. A free-form action may need a roll (`python3 engine/darrow.py roll ch<NN>-<slug> --stat … --dc … [--prof]`).
3. Gated options: check the requirement against `python3 engine/darrow.py sheet --json`. If he doesn't meet it, say so in-world and offer the alternatives, or offer to spend Inspiration if the option allows (`python3 engine/darrow.py inspire --reason "…"`).
4. Record it in `saga/state/world.json → choices` as `{chapter, option, text, date}`. Apply approval shifts (usually ±5 to ±15; bigger only for betrayals or sacrifices) and set any flags (`anselm_spared`, `vane_unbound`, …).
5. Write the immediate consequence: **100–250 words** appended to the chapter file under `### Choice — <title>`. Companions react in their own voices; approval changes show in what they say, never as numbers.
6. Update `chapter_plan` in `world.json` (the choice should bend the next scenes), `threads.md`, and `saga/NOW.md`.
7. **The cast and the site:** the companions who reacted get their `last_seen`, `last_seen_doing`, `now` and `appearances` updated (the consequence's anchor is `#choice`); new `known_facts` for anything the consequence revealed; approval changes show on the site by themselves. Then `python3 engine/build_site.py` (must pass).
8. Commit and push: `git add -A && git commit -m "choice: <summary>" && git push origin HEAD:main`.
