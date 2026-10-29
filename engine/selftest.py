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


def page_of(path):
    """A built page's text, or "" when the build did not produce it (the check that reads it then fails, it never crashes)."""
    path = Path(path)
    return path.read_text(encoding="utf-8") if path.exists() else ""


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
        if mode == ["--climax"]:
            check("use DC" in out or "odds: the DCs are set once" in out, "brief --climax prints the dice odds for the tier (or says the tier is not frozen yet)", out[-400:])
    code, out = run(["engine/saga.py", "now"], ROOT)
    check(code == 0 and len(out.splitlines()) <= 30, "now stays within 30 lines", out[-200:])
    # the dice's odds: the same rule as the die, exactly (deterministic: no die is cast)
    code, out = run(["engine/darrow.py", "odds", "--bonus", "4", "--dc", "13", "--json"], ROOT)
    try:
        o = json.loads(out.strip().splitlines()[-1])
    except (ValueError, IndexError):
        o = None
    code2, brute = run(["-c", "import sys; sys.path.insert(0, 'engine'); import darrow; "
                        "ns = [darrow.check_result(n, n + 4, 13) for n in range(1, 21)]; "
                        "print(sum(r in ('SUCCESS', 'CRITICAL SUCCESS') for r in ns) / 20, sum(r.startswith('PARTIAL') for r in ns) / 20)"], ROOT)
    bs, bp = (brute.split() + ["0", "0"])[:2]
    row = (o or {}).get("rows", {}).get("13") or {}
    check(code == 0 and code2 == 0 and row and abs(row["success"] - float(bs)) < 1e-6 and abs(row["partial"] - float(bp)) < 1e-6 and abs(sum(row.values()) - 1) < 1e-6,
          "odds match the die's own rule and sum to one", out[-300:] + " | " + brute[-200:])
    code, out = run(["engine/darrow.py", "odds", "--stat", "resolve", "--prof", "--target", "0.8", "--json"], ROOT)
    tdc = ((json.loads(out.strip().splitlines()[-1]) if code == 0 and out.strip() else {}) or {}).get("target_dc")
    check(code == 0 and isinstance(tdc, int) and 5 <= tdc <= 30, "odds --target names a DC", out[-200:])

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
        # a name the GM files know and the page has not spoken, picked from the copy as it stands (a fixed name goes stale
        # the day the page speaks it); read from the engine itself, so it never sits in this file
        r = subprocess.run([PY, "-c", "import sys; sys.path.insert(0, 'engine'); import saga; print(' '.join(sorted(saga.gm_unspoken_names())))"],
                           cwd=tmp, capture_output=True, text=True, env=ENV)
        unspoken = r.stdout.split()
        if unspoken:
            code, out = run(saga + ["glimpse", "add", "--kind", "body" if other_kind != "body" else "weather", f"Brother {unspoken[0]} counts the stores again."], tmp, expect=1)
            check(unspoken[0] in out and "refusing" in out, "glimpse add refuses a name the GM files know and the page has not spoken")
        else:
            skip("glimpse add refusing an unspoken name: the GM files hold none the page has not spoken")
        lines = [l for l in (tmp / "saga/state/glimpses.md").read_text(encoding="utf-8").splitlines() if l.startswith("- ")]
        check(len(lines) <= 20 and lines[-1].endswith("Tests: 1."), "the glimpses file holds the last 20, newest last")

        # the title ladder: a lean is kept through a dip and lapses once the axis has clearly left it; both ways long enough is a name of its own
        def bearing_move(pole, n):
            """A shift of n toward a pole, in the engine's steps: a single move is at most ±4 (betrayal or sacrifice)."""
            code, out, n = 0, "", int(n)
            while n > 0 and code == 0:
                step = min(4, n)
                code, out = run(saga + ["bearing", pole, str(step), "--why", "gm:self-test"], tmp)
                n -= step
            return code, out

        b0 = jload(tmp / "saga/state/bearing.json")
        v0 = b0["axes"]["hearth_banner"]["value"]
        code, out = bearing_move("hearth", max(1, 5 + v0) if v0 > -5 else 1)
        b = jload(tmp / "saga/state/bearing.json")
        kins = b["names"].get("Hearth.lean")
        # the move never gives an epithet (only a climax or a Choice block that speaks it does); with none given yet the
        # lean's own name is next in line, and an epithet already given stays next while its title holds
        check(code == 0 and any(t["rung"] == "lean" and t["pole"] == "Hearth" for t in b["titles"]) and b["epithet"] == b0.get("epithet")
              and b["epithet_next"] == (b0.get("epithet") or kins),
              "a lean at 4 or more holds its title and queues the epithet without giving it", json.dumps(b.get("titles")) + f" next {b.get('epithet_next')}")
        v1 = b["axes"]["hearth_banner"]["value"]
        bearing_move("banner", -2 - v1)  # back to −2: a dip, not a lapse
        b = jload(tmp / "saga/state/bearing.json")
        check(b["axes"]["hearth_banner"]["value"] == -2 and any(t["pole"] == "Hearth" for t in b["titles"]), "a dip to 2 keeps the title (hysteresis)", json.dumps(b.get("titles")))
        bearing_move("banner", 2)  # to 0: lapsed
        b = jload(tmp / "saga/state/bearing.json")
        check(b["axes"]["hearth_banner"]["value"] == 0 and not any(t["pole"] == "Hearth" for t in b["titles"]), "back at 0 the lean lapses")
        for pole in ("mercy", "mercy", "flint", "flint"):
            run(saga + ["bearing", pole, "3", "--why", "gm:self-test"], tmp)
        b = jload(tmp / "saga/state/bearing.json")
        # mixed outranks a lean, so a mixed name is next in line (another axis may hold a mixed title of its own in a live copy)
        mixed_names = {t["name"] for t in b["titles"] if t["rung"] == "mixed"}
        check(b["axes"]["mercy_flint"]["value"] == 0 and any(t["rung"] == "mixed" and t["axis"] == "mercy_flint" for t in b["titles"]) and b["epithet_next"] in mixed_names,
              "six each way inside the lean is a mixed name, next in line", json.dumps(b.get("titles")) + f" next {b.get('epithet_next')}")
        code, out = run(saga + ["check"], tmp)
        check(code == 0, "check passes with the ladder's titles", out[-400:])
        code, out = run(saga + ["bearing", "show"], tmp)
        check(code == 0 and "titles held:" in out and "next in line" in out, "bearing show prints the titles and the epithet next in line", out[-300:])

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

            # callbacks: one that fits Wren's company (worth a beat), one that waits for a companion still to come and lapses after this scene at a cost
            cb = {"id": f"c{ch:02d}.981", "made": {"chapter": ch, "scene": "s0", "date": day}, "chose": "Promised two things (self-test).", "now": {},
                  "due": [{"id": f"c{ch:02d}.981a", "when": "later", "weight": "color", "fits": "present.wren", "priority": 3, "what": "A thing owed in Wren's hearing (self-test)."},
                          {"id": f"c{ch:02d}.981b", "when": "later", "weight": "color", "fits": "present.ysra", "valid_until": key, "if_void": {"approval": {"wren": -2}}, "what": "A promise to keep by this scene (self-test)."}]}
            code, out = run(saga + ["add", json.dumps(cb)], tmp)
            check(code == 0 and "2 due item(s)" in out, "add takes a callback's fits, priority, valid_until and if_void", out[-300:])
            bad_cb = {"id": f"c{ch:02d}.982", "made": {"chapter": ch, "scene": "s0", "date": day}, "chose": "x", "now": {},
                      "due": [{"id": f"c{ch:02d}.982a", "when": "later", "weight": "color", "fits": "present.nobody_here", "what": "x"}]}
            code, out = run(saga + ["add", json.dumps(bad_cb)], tmp, expect=1)
            check("unknown term" in out, "a callback whose fits names nobody the registries know is refused")
            code, out1 = run(saga + ["brief", "--between", "--with", "wren-ashdown"], tmp)
            check(code == 0 and f"c{ch:02d}.981a" in out1 and f"c{ch:02d}.981b" not in out1 and "wait for other company" in out1, "the brief lists a callback where it fits and only counts the ones that wait for other company", out1[-300:])
            wren_before = jload(tmp / "saga/state/world.json")["companions"]["wren"]["approval"]
            # regard moves only for who saw it or heard of it; Betweens raise an old friend less than a new one
            pres = {"id": f"c{ch:02d}.983", "made": {"chapter": ch, "scene": "s0", "date": day}, "chose": "Said a kind thing of Maelis (self-test).", "now": {"approval": {"maelis": 1}}, "due": []}
            code, out = run(saga + ["add", json.dumps(pres)], tmp, expect=1)
            check("nobody saying they were there" in out, "an approval delta for a companion nobody saw or told is refused")
            code, out = run(saga + ["add", json.dumps(pres), "--learned", "maelis:Wren told her at the ovens"], tmp)
            check(code == 0 and "approval maelis" in out, "--learned accounts for a companion who was not there", out[-300:])
            hol0 = jload(tmp / "saga/state/world.json")["companions"]["hollis"]["approval"]
            # what Betweens have already raised him this chapter counts against the cap (a live copy may carry some)
            so_far = sum(int(((e.get("now") or {}).get("approval") or {}).get("hollis", 0))
                         for e in jload(tmp / "saga/state/_gm/consequences.json").get("entries", [])
                         if int((e.get("made") or {}).get("chapter", -1)) == ch and str((e.get("made") or {}).get("scene", "")).startswith("between"))
            btw = {"id": f"c{ch:02d}.985", "made": {"chapter": ch, "scene": "between-77", "date": day}, "chose": "Won a game off Hollis (self-test).", "now": {"approval": {"hollis": 6}}, "due": []}
            code, out = run(saga + ["add", json.dumps(btw), "--witnessed", "hollis"], tmp)
            hol1 = jload(tmp / "saga/state/world.json")["companions"]["hollis"]["approval"]
            want = max(0, min(6, (6 if hol0 < 40 else 4 if hol0 < 70 else 2) - so_far))
            check(code == 0 and hol1 - hol0 == want, f"a Between raises a companion at regard {hol0} by what is left of its cap this chapter (+{want}; got {hol1 - hol0:+d})", out[-300:])
            code, out = run(saga + ["approval", "forecast"], tmp)
            check(code == 0 and "hollis" in out and "rule(s) met for free" in out, "approval forecast names every companion and a verdict", out[-300:])

            # the scene recorded: a refusal first, then the record, then the projections
            with open(chapter, "a", encoding="utf-8") as f:
                f.write(f"\n### Scene {next_scene} — The Self-Test\n\nRae came up the last flight at dusk with a letter in blue wax, and called him Darrow. Wren counted the steps she took, aloud, and wrote the number down twice. The Quorrel stood at the gate with a lamp.\n")
            bad = json.dumps({"key": key, "date": day, "people": [{"id": "wren-ashdown", "did": "counted"}]})
            code, out = run(saga + ["record", bad], tmp, expect=1)
            check("last_beat is required" in out and "Quorrel" in out and key not in page_of(tmp / f"saga/state/events/ch{ch:02d}.jsonl"),
                  "record refuses a missing last_beat and an unregistered name, writing nothing")
            code, out = run(saga + ["due"], tmp)
            due_id = next((x for x in re.findall(r"^(c\d+\.\d+[a-z])\s", out, re.M)), None)
            if not due_id:  # nothing due now: a callback (when=later) fires wherever it fits, this scene included
                code, out = run(saga + ["due", "--later"], tmp)
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
                # a consequence is proved, never only marked: a bare id and a wrong excerpt are refused, the block's words pass
                bare = dict(good, fired=[due_id])
                code, out = run(saga + ["record", json.dumps(bare, ensure_ascii=False)], tmp, expect=1)
                check("no evidence" in out, "a fired item without the block's words is refused", out[-300:])
                wrong = dict(good, fired=[{"id": due_id, "evidence": "words the scene never says"}])
                code, out = run(saga + ["record", json.dumps(wrong, ensure_ascii=False)], tmp, expect=1)
                check("not a verbatim excerpt" in out, "a fired item with words the block does not carry is refused", out[-300:])
                good["fired"] = [{"id": due_id, "evidence": "wrote the number down twice"}]
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
                check(item["status"] == f"fired@{key}" and item.get("evidence") == "wrote the number down twice", "the due item the scene honoured is fired there, with the words that pay it")
                code, out = run(saga + ["history", "--chapter", str(ch), "--last", "1"], tmp)
                check(code == 0 and f"paid {due_id}" in out and "wrote the number down twice" in out, "history prints what the block paid with its words", out[-300:])
            else:
                skip("no due item to fire in the scene")
            if tid is not None:
                thr = jload(tmp / "saga/state/_gm/threads.json")
                t = next(t for t in thr["threads"] if t["id"] == tid)
                check(f"{ch:02d}:s{next_scene}" in t["on_page"] and t["who_knows"] == "The House; the reader.", "the thread's plants and who-knows follow the record")
            ledger = jload(tmp / "saga/state/_gm/consequences.json")
            items = {it["id"]: it for e in ledger["entries"] for it in e["due"]}
            a_, b_ = items.get(f"c{ch:02d}.981a") or {}, items.get(f"c{ch:02d}.981b") or {}
            check(a_.get("offered") == 1 and a_.get("offered_at") == [key] and a_.get("status") == "pending", "a callback that fit the scene and was not paid counts one offer", json.dumps(a_)[:200])
            wren_after = jload(tmp / "saga/state/world.json")["companions"]["wren"]["approval"]
            auto = [e for e in ledger["entries"] if e.get("auto")]
            check(str(b_.get("status", "")).startswith("void:expired@") and wren_after == wren_before - 2 and auto and auto[-1]["now"]["approval"] == {"wren": -2},
                  "a callback past its valid_until lapses at the record, at its if_void cost, through an entry the engine writes", f"{b_.get('status')} wren {wren_before}→{wren_after}")
            code, out = run(saga + ["due", "--later"], tmp)
            check(code == 0 and "offered 1×" in out and "fits: present.wren" in out, "due --later shows a callback's fit and its offers", out[-300:])
            run(saga + ["plan", "flag", "--new", "selftest_orphan=false"], tmp)
            code, out = run(saga + ["check"], tmp)
            check(code == 0 and "flag selftest_orphan has no reader" in out, "check notes a flag nothing reads (a plant without a payoff), without failing", out[-300:])
            code, out = run(saga + ["history", "--person", "rae-thorne", "--last", "1"], tmp)
            check(code == 0 and key in out and "called him Darrow" in out, "history reads the record back")
            code, out = run(saga + ["record", json.dumps(good, ensure_ascii=False)], tmp, expect=1)
            check("already recorded" in out, "a block is not recorded twice without --force")
        else:
            skip(f"the day close and the scene: the live chapter is at stage {pos.get('stage')} with {len(open_slots)} open slot(s)")

        # the climax: recorded with its choice; the choice survives the chapter open; the answer and its Choice block
        # a climax choice carried from the last chapter (most weeks, right after the checkpoint): the copy settles it by its
        # default, the way the second close would, so the chapter flow below can run
        oc_live = plan.get("open_choice")
        if pos.get("stage") == "scene" and oc_live and not plan.get("answered_choice"):
            oc_ch = int(oc_live.get("chapter"))
            settle = {"id": f"c{oc_ch:02d}.980", "chose": "Answered for himself with the default (self-test).", "now": {}, "due": []}
            code, out = run(saga + ["choose", "--by", "bearing", "--which", "climax", json.dumps(settle)], tmp)
            check(code == 0 and f"option {oc_live.get('default')} by bearing" in out, "a carried climax choice resolves to its default by the Bearing", out[-400:])
            oc_file = next(iter(sorted(tmp.glob(f"saga/chronicle/{oc_ch:02d}-*.md"))), None)
            if code == 0 and oc_file:
                with open(oc_file, "a", encoding="utf-8") as f:
                    f.write("\n### Choice — Settled by the Self-Test\n\nHe let the matter stand as it was, and the House went on with its night.\n")
                code, out = run(saga + ["record", json.dumps({"key": f"ch{oc_ch:02d}:choice", "last_beat": "He let the matter stand.", "people": [{"id": "darrow", "did": "Let the matter stand."}]})], tmp)
                check(code == 0 and "ok:" in out, "the settled choice's block records into its own chapter", out[-500:])
            plan = jload(tmp / "saga/state/_gm/plan.json")
            pos = plan["position"]
        has_climax = any(l.startswith("## Climax") for l in chapter.read_text(encoding="utf-8").splitlines())
        if pos.get("stage") == "scene" and not has_climax and not plan.get("open_choice") and not plan.get("answered_choice"):
            code, out = run(saga + ["plan", "set", "stage=climax"], tmp)
            check(code == 0, "plan set stage=climax")
            with open(chapter, "a", encoding="utf-8") as f:
                f.write("\n## Climax — The Test of the Stair\n\nDarrow laid the night out before the House, and Hollis said nothing.\n\n**What does Darrow do?**\n1. **Ask Maelis.**\n2. **Send Wren.** *[Inspiration]*\n3. **Ask the Prior.**\n")
            climax = {"key": f"ch{ch:02d}:climax", "where": {"place": "saint-ysoldes", "detail": "the hall"}, "last_beat": "The House waited on his answer.",
                      "people": [{"id": "darrow", "did": "Laid the night out before the House."}, {"id": "hollis-garrow", "did": "Said nothing."}],
                      "choice": {"ask": "What does Darrow do?", "options": ["Ask Maelis.", "Send Wren. *[Inspiration]*", "Ask the Prior."], "default": 3},
                      "recap": "The House heard the night laid out.", "story_so_far": {"hollis-garrow": "He kept the Grey Cot through the week."}}
            bad_default = dict(climax, choice={**climax["choice"], "default": 2})
            code, out = run(saga + ["record", json.dumps(bad_default, ensure_ascii=False)], tmp, expect=1)
            check("Inspiration" in out, "a climax whose default costs Inspiration is refused", out[-300:])
            ep0 = jload(tmp / "saga/state/bearing.json").get("epithet")
            code, out = run(saga + ["record", json.dumps(climax, ensure_ascii=False)], tmp)
            check(code == 0 and "climax choice open" in out, "the climax is recorded and its choice opened", out[-600:])
            check("EPITHET PENDING" in out and jload(tmp / "saga/state/bearing.json").get("epithet") == ep0, "a climax that does not speak the pending epithet leaves it pending (the one he has, if any, stays)", out[-400:])
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
            made = not any(tmp.glob(f"saga/chronicle/{ch + 1:02d}-*.md"))
            if made:
                nxt_file.write_text(f"# Chapter {ch + 1} — The Test\n\n*A test epigraph.*\n\n— a test source\n\n---\n", encoding="utf-8")
            code, out = run(saga + ["plan", "chapter", "open", "--number", str(ch + 1), json.dumps(t)], tmp)
            check(code == 0, "the next chapter opens from the template as filled (the template respects the live-quest cap)", out[-600:])
            if code != 0 and made:
                nxt_file.unlink()  # a refused open leaves no empty chapter behind to fail every later build
            code, out = run(saga + ["plan", "choice", "show"], tmp)
            check(f"chapter {ch}" in out and "default 3" in out, "the open choice survives the chapter open with its own default")
            entry = {"id": f"c{ch:02d}.990", "chose": "Sent Wren down with a lamp (self-test).", "now": {"approval": {"wren": 3}, "bearing": {"guile": 2}}, "due": []}
            # option 2 costs Inspiration: refused while he holds none (writing nothing), spent when he does
            sp_path = tmp / "saga/state/spends.csv"
            sp_before = sp_path.read_text(encoding="utf-8")
            held = int(jload(tmp / "saga/state/darrow.json").get("inspiration") or 0)
            with open(sp_path, "a", encoding="utf-8") as f:
                for _ in range(held):
                    f.write(f"{dt.date.today().isoformat()},inspiration,self-test drain\n")
            run(darrow + ["sync"], tmp)
            code, out = run(saga + ["choose", "--option", "2", json.dumps(entry), "--witnessed", "hollis", "--learned", "wren:Hollis told her"], tmp, expect=1)
            led_ids = {e["id"] for e in jload(tmp / "saga/state/_gm/consequences.json")["entries"]}
            check("holds none" in out and f"c{ch:02d}.990" not in led_ids, "an *[Inspiration]* option is refused while he holds none, and nothing is written", out[-300:])
            sp_path.write_text(sp_before, encoding="utf-8")
            run(darrow + ["sync"], tmp)
            if held < 1:
                skip("the spend on choose: the live sheet holds no Inspiration")
            code, out = run(saga + ["choose", "--option", "2", json.dumps(entry), "--witnessed", "hollis"], tmp, expect=1)
            check("nobody saying they were there" in out, "choose refuses an approval delta for a companion nobody saw or told")
            code, out = run(saga + ["choose", "--option", "2", json.dumps(entry), "--witnessed", "hollis", "--learned", "wren:Hollis told her"], tmp)
            check(code == 0 and "answered: option 2" in out, "choose records the entry, the row and closes the choice", out[-600:])
            if held >= 1:
                check("Inspiration spent" in out and "choice ch" in sp_path.read_text(encoding="utf-8"), "choose spends the Inspiration the option costs, under the choice's name", out[-300:])
                led = jload(tmp / "saga/state/_gm/consequences.json")["entries"][-1]
                check(led.get("inspiration") is True and led.get("declined") == ["Ask Maelis.", "Ask the Prior."], "the entry marks the spend and keeps the options he declined", json.dumps(led)[:300])
            world = jload(tmp / "saga/state/world.json")
            check(world["choices"][-1]["ledger"] == f"c{ch:02d}.990" and world["choices"][-1]["chapter"] == ch, "the choices[] row the site reads is written")
            code, out = run(saga + ["brief", "--choice"], tmp)
            check(code == 0 and f"ch{ch:02d}:choice" in out, "brief --choice prints the answered choice")
            # an invitation let pass costs its person: planned on the new chapter's second slot, passed by hand
            inv = {"who": "hollis-garrow", "kind": "favour", "want": "a hand with the beech leg's strap", "why_now": "the strap broke at the dusk bell", "if_ignored": "he mended it himself and swore at it"}
            code, out = run(saga + ["plan", "slot", "2", "invite=" + json.dumps(inv)], tmp)
            hol0 = jload(tmp / "saga/state/world.json")["companions"]["hollis"]["approval"]
            code2, out2 = run(saga + ["invite", "2", "pass"], tmp)
            hol1 = jload(tmp / "saga/state/world.json")["companions"]["hollis"]["approval"]
            check(code == 0 and code2 == 0 and "its cost" in out2 and hol1 == hol0 - 2, "an invitation let pass costs its person's regard through an entry the engine writes", out[-200:] + " | " + out2[-300:])
            pending = jload(tmp / "saga/state/bearing.json").get("epithet_next") or "the Even-Handed"
            with open(chapter, "a", encoding="utf-8") as f:
                f.write(f"\n### Choice — The Lamp Goes Down\n\nWren went, and Hollis disapproved in the usual way. \"{pending[0].upper() + pending[1:]},\" he said, \"sends nobody.\"\n")
            choice = {"key": f"ch{ch:02d}:choice", "where": {"place": "saint-ysoldes", "detail": "the hall"}, "last_beat": "Wren went down with the lamp.",
                      "people": [{"id": "wren-ashdown", "did": "Went down with the lamp."}, {"id": "hollis-garrow", "did": "Disapproved."}]}
            code, out = run(saga + ["record", json.dumps(choice, ensure_ascii=False)], tmp)
            check(code == 0 and "ok:" in out, "the Choice block records into its own chapter once the next is open, and check passes", out[-900:])
            b = jload(tmp / "saga/state/bearing.json")
            check(b.get("epithet") == pending and b.get("epithet_since") == f"ch{ch:02d}:choice" and "spoken in the block" in out, "a Choice block that speaks the pending epithet gives it", out[-300:])
            plan3 = jload(tmp / "saga/state/_gm/plan.json")
            check(plan3.get("answered_choice") is None and plan3.get("open_choice") is None and plan3["position"]["chapter"] == ch + 1, f"the answered choice is cleared; the plan is on chapter {ch + 1}")
            code, out = run(saga + ["brief", "--between", "--with", "hollis-garrow"], tmp)
            check(code == 0 and f"ch{ch + 1:02d}:between-" in out, "a Between's brief in the new chapter keys the new chapter")
        else:
            skip("the climax flow: the live chapter has its climax, an open or answered choice, or is past the scene stage")
        code, out = run(saga + ["check"], tmp)
        check(code == 0, "check passes at the end of the chapter flow", out[-900:])
        # Inspiration at the cap: a climax check that fails outright rerolls by itself; --paid casts again without a second spend
        rules_path = tmp / "engine/rules.json"
        rules_json = jload(rules_path)
        held = int(jload(tmp / "saga/state/darrow.json").get("inspiration") or 0)
        closed = [r for r in (tmp / "saga/state/chapters.csv").read_text(encoding="utf-8").splitlines()[1:] if r.strip()]
        sp_path = tmp / "saga/state/spends.csv"
        if closed:
            # Inspiration is counted in order with the cap applied as it goes, so the one sure way to stand him at the cap is
            # no spends and a cap of one: whatever he has earned, he holds exactly one
            cap0 = rules_json["inspiration"]["cap"]
            sp_text = sp_path.read_text(encoding="utf-8")
            sp_path.write_text(sp_text.splitlines()[0] + "\n", encoding="utf-8")
            rules_json["inspiration"]["cap"] = 1
            rules_path.write_text(json.dumps(rules_json, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            run(darrow + ["sync"], tmp)
            at_cap = int(jload(tmp / "saga/state/darrow.json").get("inspiration") or 0) >= 1
            chap = closed[-1].split(",")[0]
            code, out = run(darrow + ["roll", "selftest-cap", "--stat", "might", "--dc", "40", "--dis", "--chapter", chap], tmp)
            dice = [l for l in out.splitlines() if l.startswith("`[") and not l.startswith("`[INSPIRATION]")]  # the d20 lines only
            sp_after = len(sp_path.read_text(encoding="utf-8").splitlines())
            if not at_cap:
                skip("the cap's auto-reroll: nothing earned yet in the copy")
            elif dice and "Critical success" in dice[0]:
                check(code == 0 and len(dice) == 1 and sp_after == 1, "a critical success at the cap is not rerolled")
            else:
                # one held (the cap of one): the failure is cast again on it, once, and the spend is written
                check(code == 0 and len(dice) == 2 and "1 → 0 · cast again" in out and sp_after == 2, "an outright failure of a climax check rerolls by itself on his Inspiration and spends one", f"code {code} · dice {len(dice)} · spends.csv lines {sp_after}\n" + out[-400:])
            sp_path.write_text(sp_text, encoding="utf-8")
            rules_json["inspiration"]["cap"] = cap0
            rules_path.write_text(json.dumps(rules_json, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            run(darrow + ["sync"], tmp)
        else:
            skip("the cap's auto-reroll: no closed chapter in the copy")
        sp_n = len(sp_path.read_text(encoding="utf-8").splitlines())
        run(darrow + ["roll", "selftest-paid", "--stat", "might", "--dc", "12"], tmp)
        code, out = run(darrow + ["roll", "selftest-paid", "--stat", "might", "--dc", "12", "--reroll", "--paid"], tmp)
        sp_after = len(sp_path.read_text(encoding="utf-8").splitlines())
        check(code == 0 and "#reroll" in out and sp_after == sp_n, "--reroll --paid casts again without a second spend", out[-300:])

        # the works and the tales: a project, its tale, a task reported, the piece written and recorded, the keepsake, the site
        for q in [q for q in jload(tmp / "real/projects.json").get("projects", []) if q.get("status") == "live"]:  # every live project in the copy is set aside first
            run(darrow + ["project", "drop", "--id", q["id"], "--why", "self-test"], tmp, expect=None)
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
        dropped = {q["id"] for q in jload(tmp / "real/projects.json").get("projects", []) if q.get("status") == "dropped"}
        resting = [f"tale{int(b['n']):02d}" for b in jload(tmp / "saga/state/_gm/plan.json").get("tales") or [] if b.get("project") in dropped]
        w_tales = {t["id"]: t for t in jload(tmp / "saga/state/world.json").get("tales") or []}
        if resting:
            check(all(w_tales[t]["rests"] or w_tales[t]["done"] for t in resting if t in w_tales),
                  "a tale whose work was set aside rests (told in part), and the drop rebuilt the projections", str(w_tales)[:300])
        else:
            skip("no set-aside work in the live state to rest a tale")
        code, out = run(darrow + ["project", "open", "Sell the cart", "--tasks", "Clean it", "Park it", "List it"], tmp)
        check(code == 0 and "sell-the-cart" in out and "due Sat" in out, "project open starts the week's work with three tasks, due Saturday", out[-300:])
        code, out = run(darrow + ["project", "open", "Another", "--tasks", "Sweep the yard", "Mend the fence"], tmp)
        check(code == 0 and "alongside: sell-the-cart" in out, "a second project opens alongside the first", out[-300:])
        code, out = run(darrow + ["today"], tmp)
        check("Project: Sell the cart" in out and "Project: Another" in out, "today names every live project, one line each", out[-400:])
        code, out = run(darrow + ["project", "done", "1"], tmp, expect=1)
        check("needs --id" in out, "with two live, a task number alone is refused (it needs --id)", out[-300:])
        code, out = run(darrow + ["project", "drop", "--why", "x"], tmp, expect=1)
        check("--id" in out, "with two live, drop asks which (--id)", out[-300:])
        code, out = run(darrow + ["project", "drop", "--id", "another", "--why", "self-test: the second one"], tmp)
        check(code == 0 and "set aside" in out, "drop --id sets one of two aside", out[-300:])
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
        code, out = run(["engine/report.py"], tmp)
        check(code == 0 and (tmp / "real/trends.html").exists() and "trends:" in out and "<title>The Ledger</title>" in (tmp / "real/trends.html").read_text(encoding="utf-8"),
              "the trends page builds from the copy's logs", out[-300:])
        code, out = run(["engine/build_site.py"], tmp)
        page = page_of(tmp / "docs/darrow/index.html")
        check(code == 0 and 'class="slot pending"' in page and 'class="told"' in page and "Nothing kept yet" in page,
              "the empty shelf shows the tale in progress, its pieces told, and what the shelf is for", out[-300:])
        check(re.search(r'href="\.\./site\.css\?v=[0-9a-f]{10}"', page) is not None and re.search(r'src="\.\./site\.js\?v=[0-9a-f]{10}"', page) is not None,
              "pages link the stylesheet and the script by a version that changes with their content")
        check('class="rring"' in page and 'stroke="#262D37"' in page and 'class="tg"' in page and 'stroke="#CFA65F"' in page,
              "the drawings carry their own colours, so an older stylesheet never turns them black")
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
        p3["keepsake"] = {"name": "Quickstep", "text": "The name the Ninth gave him, for the feet.", "to": "darrow", "mark": "saddle"}
        code, out = run(saga + ["record", json.dumps(p3, ensure_ascii=False)], tmp, expect=1)
        check("mark" in out, "a keepsake mark the shelf cannot draw is refused")
        p3["keepsake"]["mark"] = "word"
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
        page = page_of(tmp / "docs/darrow/index.html")
        check("Works ·" in page and "What he keeps" in page and "Quickstep" in page, "Darrow's page shows the work and the keepsake")
        check('class="slot kept"' in page and 'class="tally"' in page and 'class="rring"' in page and 'class="tg"' in page, "Darrow's page draws the shelf, the tally, the rank rings and the tree glyphs")
        code, out = run(["-c", "import sys; sys.path.insert(0, 'engine'); import records, build_site; print(set(records.KEEPSAKE_MARKS) == build_site.SHELF_MARKS)"], tmp)
        check(code == 0 and out.strip().endswith("True"), "the record's keepsake marks and the shelf's are the same set", out[-200:])
        tale_page = tmp / f"docs/tales/{tale.stem}.html"
        check("Piece 3" in page_of(tale_page), "the tale has its page")
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
