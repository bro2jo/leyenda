#!/usr/bin/env python3
"""THE UNKNEELING - the engine's self-test. Run from the repo root: python3 engine/selftest.py [--keep]

Read-only on the repo: the live state is only checked; every mutation runs on a scratch copy of engine/, saga/ and
real/ under a temporary directory (the engines find their root from their own file, so the copy's engine works on the
copy). It adapts to wherever the story stands: it takes the current chapter's next open slot as "today" (DARROW_TODAY),
the first due item, the first open thread and an armed rule from the live state, and skips the climax flow when the
live chapter has already passed it. It exercises the whole flow a session runs: the checks, the projections, the brief
in every mode, a day closed and its scene recorded, a climax recorded and its choice carried across a chapter open, the
answer and its Choice block, the vocabulary gate, a rule fired, a glimpse kept, and the works: a project opened, its
tale bound, a task reported, the pieces recorded (refused ahead of their task), the keepsake (the lesser one when the
project came late), the site built with the tale. Exit 1 on the first failure, with the output that failed.
"""
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable
FAILED = []
ENV = dict(os.environ)


def run(args, cwd, expect=0, quiet=True):
    r = subprocess.run([PY] + args, cwd=cwd, capture_output=True, text=True, env=ENV)
    out = (r.stdout + r.stderr).strip()
    ok = True if expect is None else (r.returncode == 0) if expect == 0 else (r.returncode != 0)
    if not ok:
        FAILED.append(f"$ {' '.join(args)}\n  expected exit {'0' if expect == 0 else 'non-zero'}, got {r.returncode}\n  {out[-1500:]}")
    return r.returncode, out


def check(cond, what, detail=""):
    print(("  ok   " if cond else "  FAIL ") + what)
    if not cond:
        FAILED.append(what + ("\n  " + detail if detail else ""))


def skip(what):
    print("  skip " + what)


def jload(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    keep = "--keep" in sys.argv
    print("live repo")
    code, out = run(["engine/darrow.py", "check"], ROOT)
    check(code == 0 and out.endswith("all logs look clean"), "darrow.py check: all logs look clean", out[-400:])
    code, out = run(["engine/saga.py", "check"], ROOT)
    check(code == 0, "saga.py check passes", out[-600:])
    code, out = run(["engine/saga.py", "project", "--dry"], ROOT)
    check(code == 0 and "none" in out, "every projection is fresh against the records", out)
    live_plan = jload(ROOT / "saga/state/_gm/plan.json")
    live_stage = live_plan["position"].get("stage")
    modes = [(["--between", "--with", "hollis-garrow"], 30000), (["--chapter"], 24000)]
    if live_stage == "scene" and any(s.get("status") in ("planned", "next") for s in live_plan["chapter"].get("slots", [])):
        modes.insert(0, ([], 36000))
    if live_stage in ("scene", "climax"):
        modes.append((["--climax"], 40000))
    for mode, budget in modes:
        code, out = run(["engine/saga.py", "brief"] + mode + ["--size"], ROOT)
        marker = "== TEMPLATE" if mode == ["--chapter"] else "== RECORD"
        check(code == 0 and marker in out and len(out) <= budget, f"brief {' '.join(mode) or '(next slot)'} prints within {budget:,} chars (got {len(out):,})", out[-300:])
    code, out = run(["engine/saga.py", "now"], ROOT)
    check(code == 0 and len(out.splitlines()) <= 30, "now stays within 30 lines", out[-200:])

    tmp = Path(tempfile.mkdtemp(prefix="unkneeling-selftest-"))
    try:
        for d in ("engine", "saga", "real"):
            shutil.copytree(ROOT / d, tmp / d, ignore=shutil.ignore_patterns("__pycache__", "*.tmp"))
        (tmp / "docs").mkdir()
        print(f"scratch copy at {tmp}")
        saga, darrow = ["engine/saga.py"], ["engine/darrow.py"]
        plan = jload(tmp / "saga/state/_gm/plan.json")
        pos = plan["position"]
        ch, next_scene = int(pos["chapter"]), int(pos["next_scene"])
        chapter = tmp / jload(tmp / "saga/state/world.json")["chapter_file"]
        slots = plan["chapter"].get("slots", [])
        open_slots = [s for s in slots if s.get("day") and s.get("kind") != "interlude" and s.get("status") in ("planned", "next")]
        key = f"ch{ch:02d}:s{next_scene}"

        # the vocabulary gate
        day0 = (open_slots[0]["day"] if open_slots else dt.date.today().isoformat())
        code, out = run(darrow + ["set", "daily", day0, "knee_session=skipped"], tmp, expect=1)
        check("refused" in out, "set daily refuses a code outside the vocabulary, writing nothing")
        code, out = run(darrow + ["ex", "add", json.dumps([{"date": day0, "session": "Upper B", "block": "push", "exercise": "x"}])], tmp, expect=1)
        check("refused" in out, "ex add refuses a misspelt session")

        # a glimpse
        last_kind = next((l.split(" · ")[1] for l in reversed((tmp / "saga/state/glimpses.md").read_text(encoding="utf-8").splitlines()) if l.startswith("- ")), "weather")
        code, out = run(saga + ["glimpse", "add", "--kind", last_kind, "a test glimpse"], tmp, expect=1)
        check("rotate" in out, "glimpse add refuses the same kind twice running")
        other_kind = "ledger" if last_kind != "ledger" else "house"
        code, out = run(saga + ["glimpse", "add", "--kind", other_kind, "From Wren's ledgers, a page headed Tests: 1."], tmp)
        check(code == 0 and "note:" in out, "glimpse add keeps a new one and only notes a capitalised common noun")
        code, out = run(saga + ["glimpse", "add", "--kind", "body" if other_kind != "body" else "weather", "Brother Anselm counts the stores again."], tmp, expect=1)
        check("Anselm" in out and "refusing" in out, "glimpse add refuses a name the GM files know and the page has not spoken")
        lines = [l for l in (tmp / "saga/state/glimpses.md").read_text(encoding="utf-8").splitlines() if l.startswith("- ")]
        check(len(lines) <= 20 and lines[-1].endswith("Tests: 1."), "the glimpses file holds the last 20, newest last")

        # a rule fired has state (the first armed rule the digest shows)
        code, out = run(saga + ["now"], tmp)
        m = re.search(r"RULE armed[^\n]*?(r\.[a-z0-9_.]+)", out)
        if m:
            rid = m.group(1)
            code, out = run(saga + ["fire", rid, "--where", key], tmp)
            check(code == 0 and "honoured" in out, "fire takes a rule id", out[-300:])
            code, out = run(saga + ["now"], tmp)
            check(rid not in out, "a fired rule leaves the digest")
        else:
            skip("no armed rule in the digest to fire")

        # the day close prints the brief, and refuses a second close
        did_scene = False
        if pos.get("stage") == "scene" and open_slots:
            slot = open_slots[0]
            day = slot["day"]
            ENV["DARROW_TODAY"] = day  # the scratch engines live on the slot's day
            code, out = run(darrow + ["set", "daily", day, "am_swelling=0", "am_pain=0"], tmp)
            check(code == 0, f"the slot's day {day} gets a morning check so it can close", out[-300:])
            code, out = run(darrow + ["close", day], tmp)
            check(code == 0 and "== RECORD" in out and key in out, "darrow.py close closes the day and prints the brief for its slot", out[-500:])
            code, out = run(darrow + ["close", day], tmp, expect=1)
            check("already closed" in out, "a closed day is refused a second close")

            # the scene recorded: a refusal first, then the record, then the projections
            with open(chapter, "a", encoding="utf-8") as f:
                f.write(f"\n### Scene {next_scene} — The Self-Test\n\nRae came up the last flight at dusk with a letter in blue wax, and called him Darrow. Wren counted the steps she took, aloud, and wrote the number down twice. The Quorrel stood at the gate with a lamp.\n")
            bad = json.dumps({"key": key, "date": day, "people": [{"id": "wren-ashdown", "did": "counted"}]})
            code, out = run(saga + ["record", bad], tmp, expect=1)
            check("last_beat is required" in out and "Quorrel" in out and key not in (tmp / f"saga/state/events/ch{ch:02d}.jsonl").read_text(encoding="utf-8"),
                  "record refuses a missing last_beat and an unregistered name, writing nothing")
            code, out = run(saga + ["due"], tmp)
            due_id = next((x for x in re.findall(r"^(c\d+\.\d+[a-z])\s", out, re.M)), None)
            code, out = run(saga + ["threads"], tmp)
            tid = next((int(x) for x in re.findall(r"^\s*(\d+)\s+open", out, re.M)), None)
            good = {"key": key, "date": day, "where": {"place": "saint-ysoldes", "detail": "the gate wall at dusk"}, "time": "dusk",
                    "last_beat": "Rae put the letter in his hand and called him Darrow.",
                    "people": [{"id": "darrow", "did": "Counted her down and got his name back.", "now": "Holds a letter he has not opened."},
                               {"id": "rae-thorne", "did": "Came up the last flight with a letter in blue wax.", "now": "Up at the House again, her oxen stabled below.",
                                "facts": [{"fact": "She called him Darrow, not Ser, not Captain.", "evidence": "called him Darrow"}]},
                               {"id": "wren-ashdown", "did": "Counted Rae's steps aloud and wrote the number down twice.",
                                "facts": [{"fact": "She wrote the count down twice.", "evidence": "wrote the number down twice"}]}],
                    "codex": [{"section": "Places and things", "name": "The Quorrel", "text": f"A lamp at the gate (Ch {ch} Sc {next_scene})."}],
                    "now": {"against": "Marrant and his grey cloaks on the lower terrace.", "next": "The letter under the mattress."},
                    "gm": {"note": "Self-test scene."}}
            if tid is not None:
                good["threads"] = [{"id": tid, "how": "touch"}]
                good["gm"]["threads"] = [{"id": tid, "who_knows": "The House; the reader."}]
            if due_id:
                good["fired"] = [due_id]
            code, out = run(saga + ["record", json.dumps(good, ensure_ascii=False)], tmp)
            check(code == 0 and "recorded" in out and "ok:" in out, "record accepts the scene and check passes afterwards", out[-900:])
            did_scene = code == 0
            world = jload(tmp / "saga/state/world.json")
            check(world["scenes"][-1]["scene"] == next_scene and world["location"]["detail"] == "the gate wall at dusk", "world.json follows the record (the scene, the location)")
            rae = jload(tmp / "saga/characters/rae-thorne.json")
            check(rae["last_seen"]["scene"] == str(next_scene) and rae["known_facts"][-1]["evidence"] == "called him Darrow", "the character file follows the record (last_seen, the fact)")
            codex = (tmp / "saga/state/codex.md").read_text(encoding="utf-8")
            check("**The Quorrel**" in codex, "the Codex page carries the new entry")
            now_md = (tmp / "saga/NOW.md").read_text(encoding="utf-8")
            check("The Self-Test" in now_md and "The letter under the mattress." in now_md, "the NOW page follows the record")
            plan2 = jload(tmp / "saga/state/_gm/plan.json")
            s2 = next(s for s in plan2["chapter"]["slots"] if s["n"] == slot["n"])
            check(s2["status"] == "written" and s2["wrote"] == key and plan2["position"]["next_scene"] == next_scene + 1, f"the plan moved: slot {slot['n']} written, next scene {next_scene + 1}")
            if due_id:
                ledger = jload(tmp / "saga/state/_gm/consequences.json")
                item = next(it for e in ledger["entries"] for it in e["due"] if it["id"] == due_id)
                check(item["status"] == f"fired@{key}", "the due item the scene honoured is fired there")
            else:
                skip("no due item to fire in the scene")
            if tid is not None:
                thr = jload(tmp / "saga/state/_gm/threads.json")
                t = next(t for t in thr["threads"] if t["id"] == tid)
                check(f"{ch:02d}:s{next_scene}" in t["on_page"] and t["who_knows"] == "The House; the reader.", "the thread's plants and who-knows follow the record")
            code, out = run(saga + ["history", "--person", "rae-thorne", "--last", "1"], tmp)
            check(code == 0 and key in out and "called him Darrow" in out, "history reads the record back")
            code, out = run(saga + ["record", json.dumps(good, ensure_ascii=False)], tmp, expect=1)
            check("already recorded" in out, "a block is not recorded twice without --force")
        else:
            skip(f"the day close and the scene: the live chapter is at stage {pos.get('stage')} with {len(open_slots)} open slot(s)")

        # the climax: recorded with its choice; the choice survives the chapter open; the answer and its Choice block
        has_climax = any(l.startswith("## Climax") for l in chapter.read_text(encoding="utf-8").splitlines())
        if pos.get("stage") == "scene" and not has_climax and not plan.get("open_choice") and not plan.get("answered_choice"):
            code, out = run(saga + ["plan", "set", "stage=climax"], tmp)
            check(code == 0, "plan set stage=climax")
            with open(chapter, "a", encoding="utf-8") as f:
                f.write("\n## Climax — The Test of the Stair\n\nDarrow laid the night out before the House, and Hollis said nothing.\n\n**What does Darrow do?**\n1. **Ask Maelis.**\n2. **Send Wren.**\n3. **Ask the Prior.**\n")
            climax = {"key": f"ch{ch:02d}:climax", "where": {"place": "saint-ysoldes", "detail": "the hall"}, "last_beat": "The House waited on his answer.",
                      "people": [{"id": "darrow", "did": "Laid the night out before the House."}, {"id": "hollis-garrow", "did": "Said nothing."}],
                      "choice": {"ask": "What does Darrow do?", "options": ["Ask Maelis.", "Send Wren.", "Ask the Prior."], "default": 3},
                      "recap": "The House heard the night laid out.", "story_so_far": {"hollis-garrow": "He kept the Grey Cot through the week."}}
            code, out = run(saga + ["record", json.dumps(climax, ensure_ascii=False)], tmp)
            check(code == 0 and "climax choice open" in out, "the climax is recorded and its choice opened", out[-600:])
            hol = jload(tmp / "saga/characters/hollis-garrow.json")
            check(hol["story_so_far"] == "He kept the Grey Cot through the week.", "story_so_far follows the climax's record")
            days = sorted(s["day"] for s in slots if s.get("day"))
            last_day = dt.date.fromisoformat(days[-1])
            next_sunday = last_day + dt.timedelta(days=(6 - last_day.weekday()) % 7 or 7)  # the Sunday after the chapter's week
            code, tpl = run(saga + ["plan", "chapter", "template", "--week_start", next_sunday.isoformat()], tmp)
            t = json.loads(tpl)
            for s in t["slots"]:
                s["plan"], s["turn"] = "a test slot", "by the end something turns"
            t.update({"question": "a test question", "world_moves": ["a move", "another", "a third"], "climax": {"plan": "test", "checks": [], "options": ["a", "b"], "default": 1}})
            nxt_file = tmp / f"saga/chronicle/{ch + 1:02d}-the-test.md"
            if not any(tmp.glob(f"saga/chronicle/{ch + 1:02d}-*.md")):
                nxt_file.write_text(f"# Chapter {ch + 1} — The Test\n\n*A test epigraph.*\n\n— a test source\n\n---\n", encoding="utf-8")
            code, out = run(saga + ["plan", "chapter", "open", "--number", str(ch + 1), json.dumps(t)], tmp)
            check(code == 0, "the next chapter opens while the climax choice is open", out[-600:])
            code, out = run(saga + ["plan", "choice", "show"], tmp)
            check(f"chapter {ch}" in out and "default 3" in out, "the open choice survives the chapter open with its own default")
            entry = {"id": f"c{ch:02d}.990", "chose": "Sent Wren down with a lamp (self-test).", "now": {"approval": {"wren": 3}, "bearing": {"guile": 2}}, "due": []}
            code, out = run(saga + ["choose", "--option", "2", json.dumps(entry), "--witnessed", "hollis"], tmp)
            check(code == 0 and "answered: option 2" in out, "choose records the entry, the row and closes the choice", out[-600:])
            world = jload(tmp / "saga/state/world.json")
            check(world["choices"][-1]["ledger"] == f"c{ch:02d}.990" and world["choices"][-1]["chapter"] == ch, "the choices[] row the site reads is written")
            code, out = run(saga + ["brief", "--choice"], tmp)
            check(code == 0 and f"ch{ch:02d}:choice" in out, "brief --choice prints the answered choice")
            with open(chapter, "a", encoding="utf-8") as f:
                f.write("\n### Choice — The Lamp Goes Down\n\nWren went, and Hollis disapproved in the usual way.\n")
            choice = {"key": f"ch{ch:02d}:choice", "where": {"place": "saint-ysoldes", "detail": "the hall"}, "last_beat": "Wren went down with the lamp.",
                      "people": [{"id": "wren-ashdown", "did": "Went down with the lamp."}, {"id": "hollis-garrow", "did": "Disapproved."}]}
            code, out = run(saga + ["record", json.dumps(choice, ensure_ascii=False)], tmp)
            check(code == 0 and "ok:" in out, "the Choice block records into its own chapter once the next is open, and check passes", out[-900:])
            plan3 = jload(tmp / "saga/state/_gm/plan.json")
            check(plan3.get("answered_choice") is None and plan3.get("open_choice") is None and plan3["position"]["chapter"] == ch + 1, f"the answered choice is cleared; the plan is on chapter {ch + 1}")
            code, out = run(saga + ["brief", "--between", "--with", "hollis-garrow"], tmp)
            check(code == 0 and f"ch{ch + 1:02d}:between-" in out, "a Between's brief in the new chapter keys the new chapter")
        else:
            skip("the climax flow: the live chapter has its climax, an open or answered choice, or is past the scene stage")
        code, out = run(saga + ["check"], tmp)
        check(code == 0, "check passes at the end of the chapter flow", out[-900:])

        # the works and the tales: a project, its tale, a task reported, the piece written and recorded, the keepsake, the site
        run(darrow + ["project", "drop", "--why", "self-test"], tmp, expect=None)  # a live project in the copy is set aside first (nothing to drop is fine)
        settled = 0
        for _ in range(12):  # a piece the live state already owes (a task reported, its piece not yet written) is settled first, so the flow starts clean
            code, out = run(saga + ["brief", "--tale"], tmp, expect=None)
            m = re.search(r"THIS BLOCK: (tale(\d+):p(\d+))", out)
            if code != 0 or not m:
                break
            okey, on, ok_ = m.group(1), int(m.group(2)), int(m.group(3))
            ofile = tmp / re.search(r"· the file: (\S+)", out).group(1)
            with open(ofile, "a", encoding="utf-8") as f:
                f.write(f"\n### Piece {ok_} — Settled by the Self-Test\n\nThe House kept its count and said nothing of it.\n")
            rec = {"key": okey, "last_beat": "The House said nothing of it.", "people": [{"id": "darrow", "did": "Kept the count."}]}
            if "THE KEEPSAKE" in out or "THE LESSER KEEPSAKE" in out:
                rec["keepsake"] = {"name": "A count kept", "text": "The House kept its count and said nothing of it.", "to": "darrow"}
            code, out = run(saga + ["record", json.dumps(rec)], tmp)
            check(code == 0 and "ok:" in out, f"an owed piece the live state carried ({okey}) is settled first", out[-400:])
            settled += 1
        if settled:
            print(f"  (settled {settled} owed piece(s) from the live state)")
        code, out = run(darrow + ["project", "open", "Sell the cart", "--tasks", "Clean it", "Park it", "List it"], tmp)
        check(code == 0 and "sell-the-cart" in out and "due Sat" in out, "project open starts the week's work with three tasks, due Saturday", out[-300:])
        code, out = run(darrow + ["project", "open", "Another", "--tasks", "a", "b"], tmp, expect=1)
        check("already open" in out, "a second live project is refused: one at a time")
        code, out = run(saga + ["brief", "--tale"], tmp, expect=1)
        check("no piece is owed" in out, "brief --tale refuses while no task is reported")
        code, out = run(saga + ["tale", "bind", "sell-the-cart", "--tale", "tale.quickstep", "--force"], tmp)
        n = int((re.search(r"tale (\d+) bound", out) or re.search(r"(\d+)", "0")).group(1))
        tid1 = f"tale{n:02d}"
        tale = next(iter(tmp.glob(f"saga/chronicle/tales/{n:02d}-*.md")), None)
        check(code == 0 and n > 0 and tale is not None, "tale bind starts the tale's file and keeps the binding", out[-400:])
        code, out = run(darrow + ["project", "done", "clean"], tmp)
        check(code == 0 and "task 1/3 done" in out, "project done takes a few words of the task", out[-300:])
        code, out = run(darrow + ["sync"], tmp)
        check("WORK: a task done" in out, "sync reports the task as a work", out[-300:])
        code, out = run(saga + ["now"], tmp)
        check(f"TALE OWED: {tid1} piece 1 of 3" in out, "now shows the piece owed", out[-300:])
        code, out = run(saga + ["brief", "--tale", "--size"], tmp)
        check(code == 0 and f"{tid1}:p1" in out and "== RECORD" in out and "THE KEEPSAKE" not in out and len(out) <= 12000,
              f"brief --tale prints the first piece's brief without the keepsake, within 12,000 chars (got {len(out):,})", out[-400:])
        with open(tale, "a", encoding="utf-8") as f:
            f.write("\n### Piece 1 — The Breeder's Son\n\nThe boy walked at the grey's head down the hill before he could argue, and his father said nothing and opened the gate.\n")
        piece = {"key": f"{tid1}:p1", "last_beat": "His father said nothing and opened the gate.", "where": {"place": "edgemoor", "detail": "the paddock gate"},
                 "people": [{"id": "darrow", "did": "Walked at the grey's head down the hill.", "facts": [{"fact": "As a boy he walked at a horse's head before he could argue.", "evidence": "before he could argue"}]}],
                 "gm": {"note": "Self-test piece.", "next_must_know": "The grey mare is in the far field."}}
        code, out = run(saga + ["record", json.dumps(piece, ensure_ascii=False)], tmp)
        check(code == 0 and f"{tid1}:p1 recorded" in out and "ok:" in out, "the piece is recorded and check passes", out[-600:])
        code, out = run(saga + ["record", json.dumps({**piece, "key": f"{tid1}:p2"}, ensure_ascii=False)], tmp, expect=1)
        check("no piece 2" in out or "not owed yet" in out, "a piece ahead of its task is refused")
        code, out = run(saga + ["brief", "--between", "--with", "hollis-garrow"], tmp)
        people = out[out.index("== MAY: the people"):out.index("== MAY: threads")]
        dar_lines = people[people.index("· Ser Darrow"):].split("\n· ")[0]
        check(code == 0 and "fact (p1)" not in dar_lines and "the past, from the tales (" in dar_lines and "kept from the tales" not in out,
              "a block's brief keeps the present's facts and gives the tale one line; no keepsake yet", dar_lines[-500:])
        dar = jload(tmp / "saga/characters/darrow.json")
        check(any(a.get("chapter") == tid1 and a.get("scene") == "p1" for a in dar["appearances"]) and dar["last_seen"]["chapter"] != tid1,
              "the tale adds an appearance and never moves last_seen")
        for task in ("2", "3"):
            code, out = run(darrow + ["project", "done", task], tmp)
        check(code == 0 and "project finished" in out and "in its week" in out, "the last task finishes the project, in its week", out[-300:])
        code, out = run(darrow + ["sync"], tmp)
        check("WORK FINISHED:" in out and "INSPIRATION +1" in out, "sync reports the finished work and its Inspiration", out[-400:])
        code, out = run(darrow + ["sheet"], tmp)
        check("WORKS ·" in out, "the sheet shows WORKS")
        with open(tale, "a", encoding="utf-8") as f:
            f.write("\n### Piece 2 — The Grey\n\nShe stood in the thistles to be left alone, and he named her for it.\n")
        p2 = {"key": f"{tid1}:p2", "last_beat": "He named her for the thistles.", "people": [{"id": "darrow", "did": "Named the filly."}]}
        code, out = run(saga + ["threads"], tmp)
        tid = next((int(x) for x in re.findall(r"^\s*(\d+)\s+open", out, re.M)), None)
        if tid is not None:
            p2["threads"] = [{"id": tid, "how": "touch"}]
        code, out = run(saga + ["record", json.dumps(p2, ensure_ascii=False)], tmp)
        check(code == 0 and "ok:" in out, "the second piece records with a thread touch", out[-400:])
        with open(tale, "a", encoding="utf-8") as f:
            f.write("\n### Piece 3 — The Name\n\nThe sergeant said it down the line and the Ninth said it back, and he answered to it: Quickstep.\n")
        code, out = run(saga + ["brief", "--tale"], tmp)
        check(code == 0 and f"{tid1}:p3" in out and "THE KEEPSAKE" in out, "the last piece's brief carries the keepsake")
        p3 = {"key": f"{tid1}:p3", "last_beat": "He answered to the name.", "people": [{"id": "darrow", "did": "Answered to the name the Ninth gave him."}]}
        code, out = run(saga + ["record", json.dumps(p3, ensure_ascii=False)], tmp, expect=1)
        check("keepsake" in out, "the last piece without its keepsake is refused")
        p3["keepsake"] = {"name": "Quickstep", "text": "The name the Ninth gave him, for the feet.", "to": "darrow"}
        code, out = run(saga + ["record", json.dumps(p3, ensure_ascii=False)], tmp)
        check(code == 0 and "told in full" in out and "ok:" in out, "the last piece records with its keepsake and the tale is told in full", out[-500:])
        world = jload(tmp / "saga/state/world.json")
        check(world["keepsakes"][-1]["to"] == "darrow" and world["keepsakes"][-1].get("lesser") is None and next(t for t in world["tales"] if t["id"] == tid1)["done"] is True,
              "world.json carries the full keepsake and the tale's state")
        code, out = run(saga + ["brief", "--between", "--with", "hollis-garrow"], tmp)
        check(code == 0 and "kept from the tales" in out and "Quickstep (darrow)" in out, "a block's brief lists the keepsake for an echo")
        code, out = run(darrow + ["recap"], tmp)
        check(code == 0 and "**Works:**" in out, "the weekly recap carries the works", out[-300:])
        code, out = run(["engine/build_site.py"], tmp)
        n_tales = len(list(tmp.glob("saga/chronicle/tales/*.md")))
        check(code == 0 and f"{n_tales} tale" in out, "the site builds with the tale", out[-600:])
        page = (tmp / "docs/darrow/index.html").read_text(encoding="utf-8")
        check("Works ·" in page and "What he keeps" in page and "Quickstep" in page, "Darrow's page shows the work and the keepsake")
        tale_page = tmp / f"docs/tales/{tale.stem}.html"
        check(tale_page.exists() and "Piece 3" in tale_page.read_text(encoding="utf-8"), "the tale has its page")
        # a late project: due the Saturday of the week it opened, finished after it; the lesser keepsake
        today = dt.date.fromisoformat(ENV.get("DARROW_TODAY") or dt.date.today().isoformat())
        early = (today - dt.timedelta(days=9)).isoformat()
        code, out = run(darrow + ["project", "open", "Late one", "--tasks", "a", "b", "--date", early], tmp)
        check(code == 0 and "due Sat" in out, "a project is due the Saturday of the week it opens", out[-300:])
        for task in ("1", "2"):
            code, out = run(darrow + ["project", "done", task], tmp)
        check(code == 0 and "LATE" in out, "a project finished after its due day is late", out[-300:])
        code, out = run(saga + ["now"], tmp)
        check("TALE UNBOUND: project late-one" in out, "now names a project with tasks reported and no tale bound")
        code, out = run(saga + ["tale", "bind", "late-one", "--tale", "tale.hollis_table", "--force"], tmp)
        n2 = int((re.search(r"tale (\d+) bound", out) or re.search(r"(\d+)", "0")).group(1))
        tid2 = f"tale{n2:02d}"
        tale2 = next(iter(tmp.glob(f"saga/chronicle/tales/{n2:02d}-*.md")), None)
        check(code == 0 and tale2 is not None, "a finished project can still be bound with --force", out[-300:])
        code, out = run(saga + ["brief", "--tale"], tmp)
        check(code == 0 and f"{tid2}:p1" in out and "lesser" in out, "the brief of a late project's tale names the lesser keepsake ahead", out[-300:])
        with open(tale2, "a", encoding="utf-8") as f:
            f.write("\n### Piece 1 — The Stake\n\nHollis said pay, then, and the table went quiet.\n")
        code, out = run(saga + ["record", json.dumps({"key": f"{tid2}:p1", "last_beat": "The table went quiet.", "people": [{"id": "darrow", "did": "Won the game."}, {"id": "hollis-garrow", "did": "Said pay, then."}]})], tmp)
        check(code == 0 and "ok:" in out, "the late tale's first piece records", out[-400:])
        with open(tale2, "a", encoding="utf-8") as f:
            f.write("\n### Piece 2 — Paid\n\nHollis showed him the stone on the back of the hand, and that was all he paid.\n")
        code, out = run(saga + ["record", json.dumps({"key": f"{tid2}:p2", "last_beat": "That was all he paid.", "people": [{"id": "darrow", "did": "Learned the catch."}],
                                                     "keepsake": {"name": "The stone on the back of the hand", "text": "The catch Hollis showed him, a trick and not a stake.", "to": "darrow"}})], tmp)
        check(code == 0 and "the lesser one" in out and "ok:" in out, "the late tale's last piece records its keepsake as the lesser one", out[-400:])
        world = jload(tmp / "saga/state/world.json")
        check(world["keepsakes"][-1].get("lesser") is True, "world.json marks the lesser keepsake")
        code, out = run(darrow + ["project", "open", "Next", "--tasks", "a", "b"], tmp)
        check(code == 0, "a new project opens once the last is finished", out[-300:])
        code, out = run(darrow + ["project", "drop", "--why", "not this week"], tmp)
        check(code == 0 and "set aside" in out, "a project can be set aside")
        code, out = run(saga + ["check"], tmp)
        check(code == 0, "check passes after the tales", out[-600:])
    finally:
        if keep:
            print(f"scratch copy kept at {tmp}")
        else:
            shutil.rmtree(tmp, ignore_errors=True)
    if FAILED:
        print(f"\n{len(FAILED)} failure(s):")
        for f in FAILED:
            print("- " + f)
        sys.exit(1)
    print("\nall tests passed")


if __name__ == "__main__":
    main()
