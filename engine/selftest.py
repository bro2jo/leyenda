#!/usr/bin/env python3
"""THE UNKNEELING - the engine's self-test. Run from the repo root: python3 engine/selftest.py [--keep]

Read-only on the repo: the live state is only checked; every mutation runs on a scratch copy of engine/, saga/ and
real/ under a temporary directory (the engines find their root from their own file, so the copy's engine works on the
copy). It exercises the whole flow a session runs: the checks, the projections, the brief in every mode, a day closed
and its scene recorded, a climax recorded and its choice carried across a chapter open, the answer and its Choice block,
the vocabulary gate, a rule fired, a glimpse kept. Exit 1 on the first failure, with the output that failed.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable
FAILED = []


def run(args, cwd, expect=0, quiet=True):
    r = subprocess.run([PY] + args, cwd=cwd, capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    ok = (r.returncode == 0) if expect == 0 else (r.returncode != 0)
    if not ok:
        FAILED.append(f"$ {' '.join(args)}\n  expected exit {'0' if expect == 0 else 'non-zero'}, got {r.returncode}\n  {out[-1500:]}")
    return r.returncode, out


def check(cond, what, detail=""):
    print(("  ok   " if cond else "  FAIL ") + what)
    if not cond:
        FAILED.append(what + ("\n  " + detail if detail else ""))


def main():
    keep = "--keep" in sys.argv
    print("live repo")
    code, out = run(["engine/darrow.py", "check"], ROOT)
    check(code == 0 and out.endswith("all logs look clean"), "darrow.py check: all logs look clean", out[-400:])
    code, out = run(["engine/saga.py", "check"], ROOT)
    check(code == 0, "saga.py check passes", out[-600:])
    code, out = run(["engine/saga.py", "project", "--dry"], ROOT)
    check(code == 0 and "none" in out, "every projection is fresh against the records", out)
    for mode, budget in (([], 36000), (["--between"], 30000), (["--climax"], 40000), (["--chapter"], 24000)):
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

        # the vocabulary gate
        code, out = run(darrow + ["set", "daily", "2026-10-14", "knee_session=skipped"], tmp, expect=1)
        check("refused" in out, "set daily refuses a code outside the vocabulary, writing nothing")
        code, out = run(darrow + ["ex", "add", '[{"date": "2026-10-14", "session": "Upper B", "block": "push", "exercise": "x"}]'], tmp, expect=1)
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

        # a rule fired has state
        code, out = run(saga + ["fire", "r.b1.seated_blade", "--where", "ch02:s4"], tmp)
        check(code == 0 and "honoured" in out, "fire takes a rule id")
        code, out = run(saga + ["now"], tmp)
        check("r.b1.seated_blade" not in out, "a fired rule leaves the digest")

        # the day close prints the brief, and refuses a second close
        code, out = run(darrow + ["close", "2026-10-14"], tmp)
        check(code == 0 and "== RECORD" in out and "ch02:s4" in out, "darrow.py close closes the day and prints the brief for its slot")
        code, out = run(darrow + ["close", "2026-10-14"], tmp, expect=1)
        check("already closed" in out, "a closed day is refused a second close")

        # the scene recorded: a refusal first, then the record, then the projections
        chapter = tmp / "saga/chronicle/02-the-grey-cot.md"
        with open(chapter, "a", encoding="utf-8") as f:
            f.write("\n### Scene 4 — The Self-Test\n\nRae came up the last flight at dusk with a letter in blue wax, and called him Darrow. Wren counted the steps she took, aloud, and wrote the number down twice. The Quorrel stood at the gate with a lamp.\n")
        bad = json.dumps({"key": "ch02:s4", "date": "2026-10-14", "people": [{"id": "wren-ashdown", "did": "counted"}]})
        code, out = run(saga + ["record", bad], tmp, expect=1)
        check("last_beat is required" in out and "Quorrel" in out and not (tmp / "saga/state/events/ch02.jsonl").read_text(encoding="utf-8").count("ch02:s4"),
              "record refuses a missing last_beat and an unregistered name, writing nothing")
        good = {"key": "ch02:s4", "date": "2026-10-14", "where": {"place": "saint-ysoldes", "detail": "the gate wall at dusk"}, "time": "dusk",
                "last_beat": "Rae put the letter in his hand and called him Darrow.",
                "people": [{"id": "darrow", "did": "Counted her down and got his name back.", "now": "Holds a letter he has not opened."},
                           {"id": "rae-thorne", "did": "Came up the last flight with a letter in blue wax.", "now": "Up at the House again, her oxen stabled below.",
                            "facts": [{"fact": "She called him Darrow, not Ser, not Captain.", "evidence": "called him Darrow"}]},
                           {"id": "wren-ashdown", "did": "Counted Rae's steps aloud and wrote the number down twice.",
                            "facts": [{"fact": "She wrote the count down twice.", "evidence": "wrote the number down twice"}]}],
                "codex": [{"section": "Places and things", "name": "The Quorrel", "text": "A lamp at the gate (Ch 2 Sc 4)."}],
                "threads": [{"id": 14, "how": "touch"}], "fired": ["c02.9a"], "tether": "a name",
                "now": {"against": "Marrant and his grey cloaks on the lower terrace.", "next": "The letter under the mattress."},
                "gm": {"note": "Self-test scene.", "threads": [{"id": 14, "who_knows": "The House; the reader."}]}}
        code, out = run(saga + ["record", json.dumps(good, ensure_ascii=False)], tmp)
        check(code == 0 and "recorded" in out and "ok:" in out, "record accepts the scene and check passes afterwards", out[-900:])
        world = json.loads((tmp / "saga/state/world.json").read_text(encoding="utf-8"))
        check(world["scenes"][-1]["scene"] == 4 and world["location"]["detail"] == "the gate wall at dusk", "world.json follows the record (scene 4, the location)")
        rae = json.loads((tmp / "saga/characters/rae-thorne.json").read_text(encoding="utf-8"))
        check(rae["last_seen"]["scene"] == "4" and rae["known_facts"][-1]["evidence"] == "called him Darrow", "the character file follows the record (last_seen, the fact)")
        codex = (tmp / "saga/state/codex.md").read_text(encoding="utf-8")
        check("**The Quorrel**" in codex, "the Codex page carries the new entry")
        now_md = (tmp / "saga/NOW.md").read_text(encoding="utf-8")
        check("The Self-Test" in now_md and "The letter under the mattress." in now_md, "the NOW page follows the record")
        plan = json.loads((tmp / "saga/state/_gm/plan.json").read_text(encoding="utf-8"))
        slot4 = next(s for s in plan["chapter"]["slots"] if s["n"] == 4)
        check(slot4["status"] == "written" and slot4["wrote"] == "ch02:s4" and plan["position"]["next_scene"] == 5, "the plan moved: slot 4 written, next scene 5")
        ledger = json.loads((tmp / "saga/state/_gm/consequences.json").read_text(encoding="utf-8"))
        item = next(it for e in ledger["entries"] for it in e["due"] if it["id"] == "c02.9a")
        check(item["status"] == "fired@ch02:s4", "the due item the scene honoured is fired there")
        thr = json.loads((tmp / "saga/state/_gm/threads.json").read_text(encoding="utf-8"))
        t14 = next(t for t in thr["threads"] if t["id"] == 14)
        check("02:s4" in t14["on_page"] and t14["who_knows"] == "The House; the reader.", "the thread's plants and who-knows follow the record")
        code, out = run(saga + ["history", "--person", "rae-thorne", "--last", "1"], tmp)
        check(code == 0 and "ch02:s4" in out and "called him Darrow" in out, "history reads the record back")
        code, out = run(saga + ["record", json.dumps(good, ensure_ascii=False)], tmp, expect=1)
        check("already recorded" in out, "a block is not recorded twice without --force")

        # the climax: recorded with its choice; the choice survives the chapter open; the answer and its Choice block
        code, out = run(saga + ["plan", "set", "stage=climax"], tmp)
        check(code == 0, "plan set stage=climax")
        with open(chapter, "a", encoding="utf-8") as f:
            f.write("\n## Climax — The Test of the Stair\n\nDarrow laid the night out before the House, and Hollis said nothing.\n\n**What does Darrow do?**\n1. **Ask Maelis.**\n2. **Send Wren.**\n3. **Ask the Prior.**\n")
        climax = {"key": "ch02:climax", "where": {"place": "saint-ysoldes", "detail": "the hall"}, "last_beat": "The House waited on his answer.",
                  "people": [{"id": "darrow", "did": "Laid the night out before the House."}, {"id": "hollis-garrow", "did": "Said nothing."}],
                  "choice": {"ask": "What does Darrow do?", "options": ["Ask Maelis.", "Send Wren.", "Ask the Prior."], "default": 3},
                  "recap": "The House heard the night laid out.", "story_so_far": {"hollis-garrow": "He kept the Grey Cot through the week."}}
        code, out = run(saga + ["record", json.dumps(climax, ensure_ascii=False)], tmp)
        check(code == 0 and "climax choice open" in out, "the climax is recorded and its choice opened", out[-600:])
        hol = json.loads((tmp / "saga/characters/hollis-garrow.json").read_text(encoding="utf-8"))
        check(hol["story_so_far"] == "He kept the Grey Cot through the week.", "story_so_far follows the climax's record")
        # the next chapter opens with the choice still open; the choice's default stays the old climax's (3), not the new chapter's
        code, tpl = run(saga + ["plan", "chapter", "template", "--week_start", "2026-10-18"], tmp)
        t = json.loads(tpl)
        for s in t["slots"]:
            s["plan"], s["turn"] = "a test slot", "by the end something turns"
        t.update({"question": "a test question", "world_moves": ["a move", "another", "a third"], "climax": {"plan": "test", "checks": [], "options": ["a", "b"], "default": 1}})
        (tmp / "saga/chronicle/03-the-test.md").write_text("# Chapter 3 — The Test\n\n*A test epigraph.*\n\n— a test source\n\n---\n", encoding="utf-8")
        code, out = run(saga + ["plan", "chapter", "open", "--number", "3", json.dumps(t)], tmp)
        check(code == 0, "the next chapter opens while the climax choice is open", out[-600:])
        code, out = run(saga + ["plan", "choice", "show"], tmp)
        check("chapter 2" in out and "default 3" in out, "the open choice survives the chapter open with its own default")
        entry = {"id": "c02.99", "chose": "Sent Wren down with a lamp (self-test).", "now": {"approval": {"wren": 3}, "bearing": {"guile": 2}}, "due": []}
        code, out = run(saga + ["choose", "--option", "2", json.dumps(entry), "--witnessed", "hollis"], tmp)
        check(code == 0 and "answered: option 2" in out, "choose records the entry, the row and closes the choice", out[-600:])
        world = json.loads((tmp / "saga/state/world.json").read_text(encoding="utf-8"))
        check(world["choices"][-1]["ledger"] == "c02.99" and world["choices"][-1]["chapter"] == 2, "the choices[] row the site reads is written")
        code, out = run(saga + ["brief", "--choice"], tmp)
        check(code == 0 and "ch02:choice" in out, "brief --choice prints the answered choice")
        with open(chapter, "a", encoding="utf-8") as f:
            f.write("\n### Choice — The Lamp Goes Down\n\nWren went, and Hollis disapproved in the usual way.\n")
        choice = {"key": "ch02:choice", "where": {"place": "saint-ysoldes", "detail": "the hall"}, "last_beat": "Wren went down with the lamp.",
                  "people": [{"id": "wren-ashdown", "did": "Went down with the lamp."}, {"id": "hollis-garrow", "did": "Disapproved."}]}
        code, out = run(saga + ["record", json.dumps(choice, ensure_ascii=False)], tmp)
        check(code == 0 and "ok:" in out, "the Choice block records into its own chapter once the next is open, and check passes", out[-900:])
        plan = json.loads((tmp / "saga/state/_gm/plan.json").read_text(encoding="utf-8"))
        check(plan.get("answered_choice") is None and plan.get("open_choice") is None and plan["position"]["chapter"] == 3, "the answered choice is cleared; the plan is on chapter 3")
        code, out = run(saga + ["brief", "--between", "--with", "hollis-garrow"], tmp)
        check(code == 0 and "ch03:between-1" in out, "a Between's brief in the new chapter keys ch03:between-1")
        code, out = run(saga + ["check"], tmp)
        check(code == 0, "check passes at the end of the flow", out[-900:])
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
