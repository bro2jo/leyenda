# THE UNKNEELING

*What is given can be taken. What is built is yours.*

A real ACL comeback, logged honestly, driving an original fantasy saga about **Ser Darrow**: a knight whose knee gave way at the Battle of Harrow Ford, who can no longer kneel, and who for the first time in his life cannot be bound.

You log real life. Claude keeps the real numbers on one side (**the Ledger**), turns your effort into XP, attributes and outcomes (**the engine**), and writes the story on the other side (**the Chronicle**). The story never mentions food, reps or rehab. It reads like a novel, with the stats of a LitRPG and the dice of Baldur's Gate.

---

## Get it running (one time)

1. **Make a private GitHub repo** (e.g. `darrow-saga`) and get this folder into it. Easiest: create the repo empty and ask Claude to attach it and push everything. Or from your computer: unzip, `cd darrow-saga`, `git remote add origin <repo url>`, `git push -u origin main` (it's already a git repo with one commit). Avoid GitHub's drag-and-drop uploader: it can skip the hidden `.claude/` folder, which holds all the commands.
2. **Open it in Claude Code**: on the web at claude.ai/code, in the **Code** tab of the Claude mobile app, in the Desktop app, or with `claude` in a terminal. Connect GitHub when it asks.
3. **First message** (paste this once):

   > Read CLAUDE.md, real/NOW.md and saga/NOW.md, run `python3 engine/darrow.py sync`, and tell me in five lines what you see on each side. Then help me catch up: I'll send what I did Sun 10/4 – today for the rehab side.

After that, just talk to it.

> Claude commits and pushes every change to `main`, so a new session (say, from your phone tomorrow) always starts with the latest logs and story.

---

## Daily use

You don't need commands; anything that looks like a log gets logged. Commands exist when you want to be explicit.

| You send | You get |
|---|---|
| `premier shake, 2 eggs + toast, creatine` | the Ledger: each item's kcal/protein, running totals vs 3,000 / 150, what's left today |
| `swelling trace, pain 0, floor AM done` | logged; Warden's Eye practice counted |
| `session A as written, upper A: bench 3x10 @ 95` | logged; one bracketed line if Darrow gained something |
| `close day` | day summary **+ the day's scene** in the Chronicle |
| `/today` | real plan for today with doses, what's done, what's left, kcal/protein to go |
| `/week` | real week table: nutrition, weigh-ins, floor, checks, sessions vs plan |
| `/saga` | story only: where Darrow is, the fight he's in, companions, last scene, open choice |
| `/sheet` | Darrow's Reckoning (the LitRPG character sheet) |
| `/checkpoint` (Sundays) | real weekly recap + the chapter's **climax** with dice + a choice |
| `/choose 2` | Darrow does it; consequences follow |
| `/ingest` + a file | new PT notes / program / working rules folded into the Ledger |
| `/sport` | set up your sport; its skills become Darrow's Arts |

---

## How real life becomes story

| You do (real) | Darrow gets (story) |
|---|---|
| hit calories and protein | **Ember** (his inner fire): warmth, healing, staying power |
| floor minimum AM + PM, graded morning checks | **Resolve**, *The Mender's Patience*, *Warden's Eye* |
| knee sessions, PT | **Might**, **Finesse**, *Stillwater Stance* |
| upper body / accessory / power | **Might**, *The Seated Blade*, *Iron Grip*, *Hammerfall* |
| conditioning | **Vigor**, *The Long Breath* |
| sport skills | **Finesse**, **Vigor**, and sport **Arts** you define |
| a full week | the chapter's tier: **Triumph · Hard-won · Costly · Setback** sets how the climax goes |
| a real rehab gate passed (PT-cleared) | a **Knot** of the Binding ties, and a new Book of the saga opens |
| a choice you make in the story | his **Bearing** (Mercy or Flint, Candor or Guile, Hearth or Banner, Sworn or Unsworn): who his choices are making him, shown in words and, in time, an epithet; and a line in the **consequence ledger**, which the story pays off later, sometimes much later |

The **Seven Knots** are your real phase gates. Book I lasts until Phase 4; Darrow can't run in the story until you're cleared to run; he can't turn at speed until you're cleared to cut. The story can never get ahead of your knee. Training more than prescribed earns nothing extra, and a rest the plan calls for is never held against you.

Real effort sets the **tone** of each day's scene and the **outcome** of each week's climax; it never changes what the scene is about. Your story choices (the small ones at the end of a scene, the big one after a climax) are the only thing that moves the Bearing and the ledger. A missed day is not a punishment: the world simply moves a step without him.

---

## The site

`docs/` is a reader-facing site: what's going on now (with a map), the Chronicle by book, chapter and scene, a character sheet for everyone on the page, Darrow's full Reckoning, and a Codex. Claude rebuilds it (`python3 engine/build_site.py`) whenever a scene is written, and the build refuses to run if anything real-world or unrevealed would leak onto it.

- **Locally:** `python3 -m http.server -d docs 8000`, then open http://localhost:8000/ (or open `docs/index.html` straight from the folder).
- **GitHub Pages:** in the repo, Settings → Pages → Source "Deploy from a branch" → branch `main`, folder `/docs`. The site is public even from a private repo, which is why it shows story only.

## What's where

```
real/      the Ledger: NOW.md (today/this week), plans, recovery state, logs (CSV)
engine/    darrow.py (the real math) + rules.json (the exchange rates; tweak freely) + saga.py (the story's bookkeeping) + build_site.py (the site)
saga/      the Chronicle: NOW.md (story right now), bible/ (style, cast, mechanics), state/ (world, bearing, places, factions, codex), characters/ (the cast), chronicle/ (the chapters)
           saga/bible/_gm/ and saga/state/_gm/ hold the plot, the plan, the consequence ledger and the character secrets: everything the page
           has not said yet. Don't open them unless you want spoilers. Nothing in them is ever rendered on the site.
docs/      the site, generated; never edited by hand
archive/   the old nutrition-only game (retired)
```

Start reading at `saga/chronicle/00-prologue-the-three-heartbeats.md`.
