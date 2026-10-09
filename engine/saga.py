#!/usr/bin/env python3
"""THE UNKNEELING - the saga engine (GM side).

Keeps the story's state machines so the writer never re-derives them from memory:
the consequence ledger (saga/state/_gm/consequences.json), Darrow's Bearing
(saga/state/bearing.json), the chapter plan and position (saga/state/_gm/plan.json),
roads per Book, and sections of the GM arc (saga/bible/_gm/arc.md). Standard library only.
Real numbers never move anything here; only choices and chapter tiers do.

Commands (run from the repo root):
  now                                   the digest: position, road, next slot, owed world moves, quests, micro, bearing, due items, rules (<= 30 lines)
  due [--at ch02:s1|book2|...] [--all]  pending ledger items: due or overdue now; --at X adds the items aimed exactly at X (labelled); --all: every pending item
  check                                 validate ledger, plan, bearing, world.json choices, arc ids, formatting, and reconcile the chapter file with the
                                        plan's slots, world.json scenes[] and the Ledger's closed days; exit 1 on problems (an unreadable state file is named)
  fmt                                   rewrite the four state JSON files canonically
  add 'JSON' [--witnessed a,b] [--pending] [--dry-run]   append a ledger entry, resolve `at`, apply its `now` deltas; every flag it sets
                                        gets a due item for the arc's Downstream line (fire where honoured, void with a reason)
  fire ID --where ch03:s2               mark a due item fired there
  void ID --why TEXT                    mark a due item void
  bearing POLE N --why ID [--force]     move the Bearing: |N| <= 4 unless --force; --why is a ledger id (c01.3) or gm:<reason>
  bearing show
  route decide --book N [--road low|main|high --why TEXT] | route show
                                        a Book already decided is only re-decided with --road … --why …
  plan next [--date D] [--full]         the slot for a day (default: the first next/planned slot) and any world move owed; --full adds the arc section
  plan done N --wrote ch01:s3 [--force] | --skipped
                                        a written/skipped slot is refused without --force; --wrote restores stage=scene, pays off owed world moves,
                                        and closes the slot's quest when its arc stages are used up or the slot carries "last": true
  plan micro open N                     open the slot's micro; records the scene key of the slot just written (from slot.wrote or last_written)
  plan micro close [--option K] [--by darrow|bearing]   --by bearing with no --option takes the slot's default
  plan slot N key=value ...             edit a planned slot in place (plan, kind, beat, quest, stage, last, pov, micro, float, day);
                                        micro is passed as JSON (micro='{"axis":…,"ask":…,"options":[…],"bearing":[…],"default":1}');
                                        a written/skipped slot is refused without --force
  plan climax                           the chapter's question, climax plan, checks, options, default and the world moves left
  plan chapter template --week_start YYYY-MM-DD
                                        print a canonical skeleton for the next chapter (7 dated slots, spine on Sunday and Saturday, two
                                        float quest placeholders, world_moves, climax); fill it in a scratch file and pass it to `plan chapter open`
  plan chapter open --number N 'JSON'   N must follow the current chapter (--force otherwise); refused while a micro is open; keeps climax.default; warns about the outgoing chapter's unwritten slots
                                        and carries its still-owed world moves to the front of the new chapter's world_moves
  plan book open N                      enter Book N: position.book/beat, route.bookN, core beats and quests seeded from arc.md, Book N-1's planned beats folded,
                                        its unrun optional quests dropped; required ones are kept available and warned (re-skin on the road or drop by hand)
  plan quest ID k=v ... | plan beat ID status=... | plan flag [--new] k=v (true/false/null; --new to add a flag) | plan temptation add TEXT
  plan companion arrive ID              move a companion from companions_to_come to world.json (keeps bond)
  plan set key=value                    stage=choice only follows climax; stage=climax pays off owed world moves
  arc ID                                print one section of _gm/arc.md (<= 40 lines)
  archive                               move spent entries older than two Books to consequences_archive.json

`when` / `at` grammar (ledger due items):
  next            the next scene (resolved by `add` to chNN:sN; at the climax, choice or transition stage: the next chapter's s1)
  chNN            anywhere in chapter NN            chNN:sN      scene N of chapter NN
  chNN:climax     chapter NN's climax or choice     bookN        anywhere in Book N
  bookN:beatK     while core beat bN.K is in_progress   bookN:climax   Book N's last climax (what `finale` resolves to)
  transitionN     Book N's transition chapter       finale       = book6:climax
  on:<flag>       when plan.json flags.<flag> becomes true
  any             standing: shown until fired or void

`if` grammar (ledger rules):
  operators  && || ! ( )  >= <= > < == !=   numbers  "strings"  true false
  terms      approval.<id>  bearing.<pole>  flags.<name>  route.bookN  factions.<id>  tether.stage
             temptation.count  quests.<id>.status
  bearing.<pole> reads the axis value if the pole is the axis's right word, negated if left.
  Missing or null terms read as 0/false; comparisons between unlike types are false.
"""
import argparse
import ast
import csv
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
P = {
    "world": ROOT / "saga/state/world.json",
    "bearing": ROOT / "saga/state/bearing.json",
    "plan": ROOT / "saga/state/_gm/plan.json",
    "ledger": ROOT / "saga/state/_gm/consequences.json",
    "archive": ROOT / "saga/state/_gm/consequences_archive.json",
    "arc": ROOT / "saga/bible/_gm/arc.md",
    "threads": ROOT / "saga/state/_gm/threads.md",
    "chapters": ROOT / "saga/state/chapters.csv",
    "config": ROOT / "real/config.json",
    "daily": ROOT / "real/logs/daily_log.csv",
    "nutrition": ROOT / "real/logs/nutrition_log.csv",
    "food": ROOT / "real/logs/food_entries.csv",
    "sheet": ROOT / "saga/state/darrow.json",
}
STATE_FILES = ("world", "bearing", "plan", "ledger")

SLOT_KINDS = ("spine", "quest", "interlude", "cutaway")
SLOT_STATUS = ("planned", "next", "written", "skipped")
WEIGHTS = ("color", "scene", "route", "fate")
STAGES = ("scene", "climax", "choice", "transition")
QUEST_STATUS = ("available", "live", "done", "dropped")
BEAT_STATUS = ("planned", "in_progress", "done", "folded")
ROADS = ("low", "main", "high")
ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII"]
NOW_CAP = 30

WHEN_RE = re.compile(r"^(next|ch\d{2}|ch\d{2}:s\d+|ch\d{2}:climax|book\d|book\d:beat\d+|book\d:climax|transition\d|finale|on:[a-z][a-z0-9_]*|any)$")
WHERE_RE = re.compile(r"^(ch\d{2}(:(s\d+|climax|interlude(-\d+)?|choice|transition|between-\d+))?|book\d(:climax|:beat\d+)?)$")
ENTRY_ID_RE = re.compile(r"^c(\d{2})\.(\d+)$")
DUE_ID_RE = re.compile(r"^c(\d{2})\.(\d+)([a-z])$")
WROTE_RE = re.compile(r"^ch(\d{2}):(s(\d+)|interlude(-\d+)?|climax|transition)$")


# ---------------------------------------------------------------- io
def load_json(path):
    """Parse a JSON file; a truncated or malformed file is named and exits 1 instead of a traceback."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"✗ {rel(path)}: invalid JSON ({e}); restore it from git")
        sys.exit(1)


def dumps(obj):
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


def save_json(path, obj):
    """Atomic write: the text goes to a .tmp beside the file and is renamed over it, so an interrupted run never leaves a half-written state file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(dumps(obj))
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def read_csv(path):
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        rows = [dict(r) for r in csv.DictReader(f)]
    return [r for r in rows if any(str(v or "").strip() for k, v in r.items() if k is not None)]


def today_local():
    if os.environ.get("DARROW_TODAY"):
        return dt.date.fromisoformat(os.environ["DARROW_TODAY"])
    try:
        cfg = load_json(P["config"])
        from zoneinfo import ZoneInfo
        return dt.datetime.now(ZoneInfo(cfg.get("timezone", "America/New_York"))).date()
    except Exception:
        utc = dt.datetime.now(dt.timezone.utc)
        return (utc - dt.timedelta(hours=4 if 3 <= utc.month <= 10 else 5)).date()


class State:
    """All four state files, loaded lazily; `save()` writes only the ones marked dirty."""

    def __init__(self):
        self._d = {}
        self.dirty = set()

    def __getattr__(self, key):
        if key in STATE_FILES:
            if key not in self._d:
                self._d[key] = load_json(P[key])
            return self._d[key]
        raise AttributeError(key)

    def touch(self, *keys):
        self.dirty.update(keys)

    def save(self, dry=False):
        for k in sorted(self.dirty):
            if dry:
                print(f"(dry run) would write {rel(P[k])}")
            else:
                save_json(P[k], self._d[k])
        if not dry:
            self.dirty.clear()


def die(msg):
    sys.exit(f"saga.py: {msg}")


def rel(path):
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def short(text, n):
    text = " ".join(str(text or "").split())
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def ch2(n):
    return f"ch{int(n):02d}"


# ---------------------------------------------------------------- bearing
def pole_axis(bearing, pole):
    """(axis_id, sign) for a pole word, case-insensitive; sign +1 for right, -1 for left. None if unknown."""
    p = str(pole).strip().lower()
    for aid, ax in bearing["axes"].items():
        if ax["right"].lower() == p:
            return aid, 1
        if ax["left"].lower() == p:
            return aid, -1
    return None


def pole_value(bearing, pole):
    r = pole_axis(bearing, pole)
    if not r:
        return 0
    aid, sign = r
    return bearing["axes"][aid]["value"] * sign


def axis_word(bearing, aid):
    ax = bearing["axes"][aid]
    v = ax["value"]
    pole = ax["right"] if v > 0 else ax["left"]
    if abs(v) >= bearing["name_at"]:
        return f"named {pole}"
    if abs(v) >= bearing["lean_at"]:
        return f"leans {pole}"
    return "even"


def recompute_bearing(bearing):
    """Refresh `leans` and `epithet` from the axis values and the history (ties go to the pole moved last)."""
    leans, named = [], []
    for aid, ax in bearing["axes"].items():
        v = ax["value"]
        pole = ax["right"] if v > 0 else ax["left"]
        if abs(v) >= bearing["lean_at"]:
            leans.append(pole)
        if abs(v) >= bearing["name_at"]:
            named.append((abs(v), aid, pole))
    bearing["leans"] = leans
    if not named:
        bearing["epithet"] = None
        return
    best = max(v for v, _, _ in named)
    tied = [(aid, pole) for v, aid, pole in named if v == best]
    if len(tied) > 1:
        last = {}
        for i, h in enumerate(bearing.get("history", [])):
            last[h["axis"]] = i
        tied.sort(key=lambda t: last.get(t[0], -1), reverse=True)
    bearing["epithet"] = bearing["names"].get(tied[0][1], tied[0][1])


BEARING_MAX_MOVE = 4
WHY_RE = re.compile(r"^(c\d{2}\.\d+|gm:.+)$")


def move_bearing(st, pole, n, why, quiet=False, force=False):
    """Move toward `pole` by n (n > 0; a negative n moves away). Returns (axis, old, new).
    A single move is at most ±4 (betrayal or sacrifice) unless force; `why` is a ledger id or gm:<reason>."""
    b = st.bearing
    r = pole_axis(b, pole)
    if not r:
        die(f"unknown pole {pole!r}; poles: " + ", ".join(w for ax in b["axes"].values() for w in (ax["left"], ax["right"])))
    if not WHY_RE.match(str(why or "")):
        die(f"--why {why!r} must be a ledger id (c01.3) or start with gm:")
    if abs(int(n)) > BEARING_MAX_MOVE and not force:
        die(f"a single move is at most ±{BEARING_MAX_MOVE} (betrayal or sacrifice); split it or pass --force")
    aid, sign = r
    ax = b["axes"][aid]
    old = ax["value"]
    new = clamp(old + sign * int(n), -b["range"], b["range"])
    ax["value"] = new
    b.setdefault("history", []).append({"why": why, "date": today_local().isoformat(), "axis": aid, "delta": new - old})
    recompute_bearing(b)
    st.touch("bearing")
    if not quiet:
        print(f"bearing {aid}: {old:+d} → {new:+d} ({axis_word(b, aid)}) · epithet: {b['epithet'] or '—'}")
    return aid, old, new


def bearing_line(bearing):
    parts = []
    for aid, ax in bearing["axes"].items():
        parts.append(f"{ax['left']}/{ax['right']} {ax['value']:+d} {axis_word(bearing, aid)}")
    ep = f" · epithet: {bearing['epithet']}" if bearing.get("epithet") else " · no epithet"
    return "Bearing: " + " · ".join(parts) + ep


# ---------------------------------------------------------------- position & targets
def book_of_chapter(plan, chapter):
    for key, r in plan.get("route", {}).items():
        if int(chapter) in [int(c) for c in r.get("chapters", [])]:
            return int(key[4:])
    return plan["position"]["book"]


def resolve_at(when, plan):
    """Static target for a `when`: `next` becomes ch<chapter>:s<next_scene>, or ch<chapter+1>:s1 while the stage is
    climax/choice/transition (the closed chapter gets no more scenes); everything else is itself."""
    if when == "next":
        pos = plan["position"]
        if pos.get("stage") in ("climax", "choice", "transition"):
            return f"{ch2(int(pos['chapter']) + 1)}:s1"
        return f"{ch2(pos['chapter'])}:s{pos['next_scene']}"
    if when == "finale":
        return "book6:climax"
    return when


def at_status(at, st):
    """'due' | 'future' | 'overdue' | 'unknown' for a resolved target against the current position."""
    pos = st.plan["position"]
    book, chapter, nxt, stage = int(pos["book"]), int(pos["chapter"]), int(pos["next_scene"]), pos["stage"]
    if at == "any":
        return "due"
    m = re.match(r"^on:(\w+)$", at)
    if m:
        return "due" if st.plan.get("flags", {}).get(m.group(1)) else "future"
    m = re.match(r"^ch(\d{2})(?::(s(\d+)|climax))?$", at)
    if m:
        c = int(m.group(1))
        if chapter > c:
            return "overdue"
        if chapter < c:
            return "future"
        sub = m.group(2)
        if not sub:
            return "due"
        if sub == "climax":
            return "due" if stage in ("climax", "choice", "transition") else "future"
        s = int(m.group(3))
        if stage != "scene":
            return "overdue"
        if nxt == s:
            return "due"
        return "overdue" if nxt > s else "future"
    m = re.match(r"^book(\d)(?::(beat(\d+)|climax))?$", at)
    if m:
        b = int(m.group(1))
        if book > b:
            return "overdue"
        if book < b:
            return "future"  # a later Book, seeded or not: `plan book open N` seeds its beats when it opens
        sub = m.group(2)
        if not sub:
            return "due"
        if sub == "climax":
            return "due" if stage in ("climax", "choice") else "future"
        beat = st.plan.get("core_beats", {}).get(f"b{b}.{m.group(3)}")
        if beat is None:
            return "unknown"
        return {"in_progress": "due", "planned": "future"}.get(beat.get("status"), "overdue")
    m = re.match(r"^transition(\d)$", at)
    if m:
        b = int(m.group(1))
        if book > b:
            return "overdue"
        if book < b:
            return "future"
        tc = st.plan.get("route", {}).get(f"book{b}", {}).get("transition_chapter")
        return "due" if tc is not None and int(tc) == chapter else "future"
    return "unknown"


def pending_items(ledger):
    for e in ledger.get("entries", []):
        for it in e.get("due", []):
            if it.get("status") == "pending":
                yield e, it


# ---------------------------------------------------------------- rule evaluator
RULE_NODES = (ast.Expression, ast.BoolOp, ast.And, ast.Or, ast.UnaryOp, ast.Not, ast.USub, ast.Compare,
              ast.Attribute, ast.Name, ast.Constant, ast.Load,
              ast.Gt, ast.GtE, ast.Lt, ast.LtE, ast.Eq, ast.NotEq)
KNOWN_ROOTS = ("approval", "bearing", "flags", "route", "factions", "temptation", "quests", "tether")


def tether_stage():
    """The Tether's stage from the engine's sheet (darrow.py owns it; saga.py only reads it). 0 if untied or unknown."""
    try:
        t = load_json(P["sheet"]).get("tether") or {}
        return int(t.get("stage") or 0)
    except (OSError, ValueError, json.JSONDecodeError):
        return 0


def rule_source(expr):
    s = str(expr)
    s = s.replace("&&", " and ").replace("||", " or ")
    s = re.sub(r"!(?!=)", " not ", s)
    s = re.sub(r"\btrue\b", "True", s)
    s = re.sub(r"\bfalse\b", "False", s)
    return s.strip()  # a leading `!` became " not …", and a leading space reads as an indent


def parse_rule(expr):
    """ast tree or None (malformed)."""
    try:
        tree = ast.parse(rule_source(expr), mode="eval")
    except SyntaxError:
        return None
    for node in ast.walk(tree):
        if not isinstance(node, RULE_NODES):
            return None
        if isinstance(node, ast.Constant) and not isinstance(node.value, (int, float, str, bool)):
            return None
    return tree


def dotted(node):
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if not isinstance(node, ast.Name):
        return None
    parts.append(node.id)
    return list(reversed(parts))


def term_lookup(parts, st):
    """(known: bool, value). Missing/null → 0/false."""
    root = parts[0]
    world, plan, bearing = st.world, st.plan, st.bearing
    if root == "approval" and len(parts) == 2:
        cid = parts[1]
        comp = world.get("companions", {})
        known = cid in comp or cid in plan.get("companions", {}) or cid in plan.get("companions_to_come", {})
        return known, (comp.get(cid, {}).get("approval") or 0)
    if root == "bearing" and len(parts) == 2:
        return pole_axis(bearing, parts[1]) is not None, pole_value(bearing, parts[1])
    if root == "flags" and len(parts) == 2:
        flags = plan.get("flags", {})
        return parts[1] in flags, bool(flags.get(parts[1]))
    if root == "route" and len(parts) == 2 and re.match(r"^book[1-6]$", parts[1]):
        return True, (plan.get("route", {}).get(parts[1], {}).get("road") or "")
    if root == "factions" and len(parts) == 2:
        f = plan.get("factions", {})
        return parts[1] in f, (f.get(parts[1]) or 0)
    if root == "temptation" and parts[1:] == ["count"]:
        return True, len(plan.get("temptation", {}).get("planted", []))
    if root == "quests" and len(parts) >= 3 and parts[-1] == "status":
        qid = ".".join(parts[1:-1])
        q = plan.get("quests", {})
        return qid in q, (q.get(qid, {}).get("status") or "")
    if root == "tether" and parts[1:] == ["stage"]:
        return True, tether_stage()
    return False, 0


def rule_terms(tree):
    out, rooted = [], set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            parts = dotted(node)
            if parts:
                out.append(parts)
            inner = node.value
            while isinstance(inner, ast.Attribute):
                inner = inner.value
            if isinstance(inner, ast.Name):
                rooted.add(id(inner))
    # keep only maximal chains (an Attribute's inner Attribute is also walked)
    chains = {".".join(p) for p in out}
    terms = [p for p in out if not any(c != ".".join(p) and c.startswith(".".join(p) + ".") for c in chains)]
    # a bare name (`shard_found` without `flags.`) is an unknown term, never a silent 0
    terms += [[node.id] for node in ast.walk(tree) if isinstance(node, ast.Name) and id(node) not in rooted]
    return terms


def same_kind(a, b):
    if isinstance(a, bool) or isinstance(b, bool):
        return isinstance(a, bool) and isinstance(b, bool)
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return True
    return isinstance(a, str) and isinstance(b, str)


def eval_node(node, st):
    if isinstance(node, ast.Expression):
        return eval_node(node.body, st)
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Attribute):
        parts = dotted(node)
        return term_lookup(parts, st)[1] if parts else 0
    if isinstance(node, ast.Name):
        return 0
    if isinstance(node, ast.UnaryOp):
        if isinstance(node.op, ast.USub):  # a negative number, e.g. approval.rae <= -25
            v = eval_node(node.operand, st)
            return -v if isinstance(v, (int, float)) and not isinstance(v, bool) else 0
        return not bool(eval_node(node.operand, st))
    if isinstance(node, ast.BoolOp):
        vals = [bool(eval_node(v, st)) for v in node.values]
        return all(vals) if isinstance(node.op, ast.And) else any(vals)
    if isinstance(node, ast.Compare):
        left = eval_node(node.left, st)
        for op, comp in zip(node.ops, node.comparators):
            right = eval_node(comp, st)
            if not same_kind(left, right):
                return False
            ok = {ast.Gt: left > right, ast.GtE: left >= right, ast.Lt: left < right, ast.LtE: left <= right,
                  ast.Eq: left == right, ast.NotEq: left != right}[type(op)]
            if not ok:
                return False
            left = right
        return True
    return False


def rule_state(rule, st):
    """('MALFORMED'|'UNKNOWN TERM'|'ARMED'|'NOT MET', detail)."""
    tree = parse_rule(rule.get("if", ""))
    if tree is None:
        return "MALFORMED", rule.get("if", "")
    unknown = [".".join(p) for p in rule_terms(tree) if not term_lookup(p, st)[0]]
    if unknown:
        return "UNKNOWN TERM", ", ".join(sorted(set(unknown)))
    return ("ARMED" if eval_node(tree, st) else "NOT MET"), ""


def rule_near(rule, st, within=15):
    """Numeric terms within reach of their threshold, for an unarmed rule.
    A term still at exactly 0 has not moved and is never 'near'; a threshold under 15 uses a relative
    window of max(2, 30% of the threshold), larger ones the absolute `within`."""
    tree = parse_rule(rule.get("if", ""))
    if tree is None:
        return []
    near = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Compare) or len(node.comparators) != 1:
            continue
        a, b = node.left, node.comparators[0]
        if isinstance(a, (ast.Constant, ast.UnaryOp)):
            a, b = b, a
        if isinstance(b, ast.UnaryOp) and isinstance(b.op, ast.USub) and isinstance(b.operand, ast.Constant) and isinstance(b.operand.value, (int, float)) and not isinstance(b.operand.value, bool):
            b = ast.Constant(value=-b.operand.value)  # a negative threshold
        if isinstance(a, ast.Attribute) and isinstance(b, ast.Constant) and isinstance(b.value, (int, float)) and not isinstance(b.value, bool):
            parts = dotted(a)
            if not parts:
                continue
            known, val = term_lookup(parts, st)
            if not (known and isinstance(val, (int, float)) and not isinstance(val, bool)) or val == 0:
                continue
            window = max(2, 0.3 * abs(b.value)) if abs(b.value) < 15 else within
            if abs(val - b.value) <= window:
                near.append(f"{'.'.join(parts)}={val} vs {b.value}")
    return near


# ---------------------------------------------------------------- chapters & roads
def chapter_rows():
    return {int(r["chapter"]): r for r in read_csv(P["chapters"]) if str(r.get("chapter", "")).strip()}


def road_score(chapters, rows):
    score, tiers, missing = 0, [], []
    for c in chapters:
        r = rows.get(int(c))
        if not r:
            missing.append(int(c))
            continue
        t = r.get("tier", "")
        tiers.append((int(c), t))
        score += {"Triumph": 1, "Setback": -1}.get(t, 0)
    return score, tiers, missing


def decide_road(chapters, rows):
    score, tiers, missing = road_score(chapters, rows)
    last = tiers[-1][1] if tiers else None
    if score <= -2 or (len(chapters) <= 2 and last == "Setback"):
        return "low"
    if score >= 2 or (len(chapters) <= 2 and last == "Triumph"):
        return "high"
    return "main"


def road_line(st):
    plan = st.plan
    book = plan["position"]["book"]
    r = plan.get("route", {}).get(f"book{book}", {})
    chapters = [int(c) for c in r.get("chapters", [])]
    rows = chapter_rows()
    score, tiers, missing = road_score(chapters, rows)
    if not tiers:
        closed = "no chapters closed yet"
    else:
        closed = ", ".join(f"ch{c} {t}" for c, t in tiers) + f" → score {score:+d}"
    road = r.get("road")
    tail = f"road {road}" + (" (override)" if r.get("override") else "") if road else f"would read {decide_road(chapters, rows)} if decided now"
    return f"Road (Book {ROMAN[book]}): {closed} · {tail}"


# ---------------------------------------------------------------- arc sections
HEAD_RE = re.compile(r"^(#{1,4})\s+(.*?)\s*$")
ID_RE = re.compile(r"^(b\d\.\d+|q\d\.[a-z0-9_]+|t\d(\.(high|main|low))?|book\d\.question|rae\.[a-z0-9_]+|pacing|truths|motifs|beliefs|temptation|flags)\b")


def arc_sections():
    """{id: (level, title, [lines])} for every heading whose text starts with an id, plus the plain heading text as a key."""
    if not P["arc"].exists():
        return {}
    lines = P["arc"].read_text(encoding="utf-8").splitlines()
    heads = []
    for i, line in enumerate(lines):
        m = HEAD_RE.match(line)
        if m:
            heads.append((i, len(m.group(1)), m.group(2)))
    out = {}
    for k, (i, lvl, text) in enumerate(heads):
        end = len(lines)
        for j, l2, _ in heads[k + 1:]:
            if l2 <= lvl:
                end = j
                break
        body = lines[i:end]
        m = ID_RE.match(text)
        key = m.group(1) if m else None
        if key and key not in out:
            out[key] = (lvl, text, body)
        out.setdefault(text, (lvl, text, body))
    return out


def arc_ids():
    return {k for k in arc_sections() if ID_RE.match(k) and ID_RE.match(k).group(1) == k}


def arc_quest_stage_count(qid):
    sec = arc_sections().get(qid)
    if not sec:
        return None
    return sum(1 for l in sec[2] if re.match(r"^###\s+stage\s+\d+", l, re.I)) or None


def print_arc(key, cap=40):
    secs = arc_sections()
    sec = secs.get(key)
    if not sec:
        ids = sorted(k for k in secs if ID_RE.match(k) and ID_RE.match(k).group(1) == k)
        hint = ", ".join(ids[:12]) if ids else "none in the id convention yet (old arc.md layout)"
        die(f"no section `{key}` in {rel(P['arc'])}; ids: {hint}")
    lines = [l for l in sec[2]]
    while lines and not lines[-1].strip():
        lines.pop()
    for l in lines[:cap]:
        print(l)
    if len(lines) > cap:
        print(f"… ({len(lines) - cap} more lines; open the file for the rest)")


# ---------------------------------------------------------------- colour (GM only, never reader-facing)
def yes(v):
    return str(v or "").strip().lower() in {"y", "yes", "true", "1", "done", "full"}


def colour_for(day):
    """GM colour of a day from the real logs. A daily_log row that carries a status field is read in full; a daily row
    that carries only date/closed counts as no status row (the close writes one before the colour is read), so a day
    with only food (a nutrition_log row with data, or food_entries rows) is cold below the fuel band, else mild, and
    still reports closed/open from the flag; only a day with nothing logged anywhere is missed."""
    rows = [r for r in read_csv(P["daily"]) if r.get("date") == day]
    nut = next((n for n in read_csv(P["nutrition"]) if n.get("date") == day), {})
    food = [f for f in read_csv(P["food"]) if f.get("date") == day]
    nut_logged = any(str(nut.get(k) or "").strip() for k in ("kcal", "protein_g", "weight_lb", "creatine", "shake"))
    try:
        kcal, prot = float(nut.get("kcal") or 0), float(nut.get("protein_g") or 0)
        if not str(nut.get("kcal") or "").strip() and food:
            kcal = sum(float(f.get("kcal") or 0) for f in food)
            prot = sum(float(f.get("protein_g") or 0) for f in food)
        t = load_json(P["config"])["nutrition_targets"]
        fuel_ok = kcal >= 0.9 * t["kcal"] and prot >= 0.9 * t["protein_g"]
    except Exception:
        fuel_ok = False
    STATUS_KEYS = ("am_swelling", "am_pain", "am_extension", "floor_am", "floor_pm", "knee_session", "knee_min", "pt", "addon_session",
                   "addon_min", "conditioning_type", "conditioning_min", "sport_min", "light", "sleep_h", "hours_on_feet")
    closed = any(yes(r.get("closed")) for r in rows)
    data_rows = [r for r in rows if any(str(r.get(k) or "").strip() for k in STATUS_KEYS)]
    if not data_rows:
        if not nut_logged and not food:
            return "missed (nothing logged)"
        return f"{'mild' if fuel_ok else 'cold'} ({'closed' if closed else 'open'}; food only, no status row)"
    r = data_rows[0]
    session = any(str(r.get(k) or "").strip() for k in ("knee_session", "addon_session", "conditioning_type", "conditioning_min")) or yes(r.get("pt"))
    fam, fpm = yes(r.get("floor_am")), yes(r.get("floor_pm"))
    if str(r.get("light") or "").strip().lower() == "red":
        c = "rest"
    elif fam and fpm and (session or fuel_ok):
        c = "warm"
    elif not fam and not fpm and not session:
        c = "cold"
    else:
        c = "mild"
    state = "closed" if closed else "open"
    return f"{c} ({state})"


# ---------------------------------------------------------------- plan helpers
def slot_by_n(plan, n):
    for s in plan["chapter"].get("slots", []):
        if str(s.get("n")) == str(n):
            return s
    die(f"no slot {n} in chapter {plan['chapter'].get('number')}")


def owed_moves(plan):
    """Skipped slots whose off-page world move has not yet opened a scene or the climax."""
    return [s for s in plan["chapter"].get("slots", []) if s.get("status") == "skipped" and s.get("world_move") and not s.get("world_move_used")]


def pay_owed_moves(plan, where):
    """Mark every owed world move used and say what `where` (the scene or climax) opens on."""
    owed = owed_moves(plan)
    for s in owed:
        s["world_move_used"] = True
    if owed:
        print(f"open the {where} on: " + " / ".join(f"{s['world_move']} (slot {s['n']})" for s in owed))
    return owed


def micro_scene_key(plan, s):
    """The scene key of the slot a micro sits in: from the slot's own `wrote`, else position.last_written ('interlude' allowed), else the scene before next."""
    m = WROTE_RE.match(str(s.get("wrote") or plan["position"].get("last_written") or ""))
    if m:
        return m.group(3) or m.group(2)
    return str(int(plan["position"]["next_scene"]) - 1)


def slot_label(s):
    what = s.get("beat") if s.get("kind") == "spine" else (f"{s.get('quest')} stage {s.get('stage')}" if s.get("kind") == "quest" else s.get("pov") or "")
    day = s.get("day") or "no day"
    dow = ""
    if s.get("day"):
        try:
            dow = " " + dt.date.fromisoformat(s["day"]).strftime("%a")
        except ValueError:
            pass
    return f"slot {s.get('n')} · {day}{dow} · {s.get('kind')} {what or ''}".rstrip() + (" · float" if s.get("float") else "")


def next_slot(plan, date=None):
    slots = plan["chapter"].get("slots", [])
    if date:
        for s in slots:
            if s.get("day") == date:
                return s
        die(f"no slot for {date} in chapter {plan['chapter'].get('number')} (week of {plan['chapter'].get('week_start')}); use `plan chapter open` or Edit the slots")
    for status in ("next", "planned"):
        for s in sorted(slots, key=lambda x: float(x.get("n", 0))):
            if s.get("status") == status:
                return s
    return None


SLOT_FIELDS = ("kind", "beat", "quest", "stage", "last", "pov", "plan", "micro", "float", "day")


def chapter_template(ws, plan):
    """A canonical next-chapter skeleton for `plan chapter open`: 7 dated slots from the Sunday `ws`, spine on Sunday
    and Saturday, two float quest placeholders (slots 3 and 5, non-adjacent so both may carry a micro), empty
    world moves and climax. The placeholders name the first two quests still available in this Book (falling back
    to the Book's q<N>.* ids); every "" is for the writer to fill, and `plan chapter open` accepts the result as is."""
    book = int(plan["position"]["book"])
    avail = [k for k, q in plan.get("quests", {}).items() if k.startswith(f"q{book}.") and q.get("status") == "available"]
    avail += [k for k in plan.get("quests", {}) if k.startswith(f"q{book}.") and k not in avail]
    avail += [f"q{book}.quest_a", f"q{book}.quest_b"]
    beat = plan["position"].get("beat") or f"b{book}.1"
    slots = []
    for n in range(1, 8):
        s = {"n": n, "day": (ws + dt.timedelta(n - 1)).isoformat()}
        if n in (3, 5):
            s.update({"kind": "quest", "quest": avail[0 if n == 3 else 1], "stage": 1, "float": True})
        else:
            s.update({"kind": "spine", "beat": beat, "float": False})
        s.update({"plan": "", "micro": None})
        slots.append(s)
    return {"week_start": ws.isoformat(), "question": "", "slots": slots, "world_moves": ["", "", ""],
            "climax": {"plan": "", "checks": [], "options": ["", "", ""], "default": 1}}


def print_slot(s, full=False, plan=None):
    print(slot_label(s) + f" · {s.get('status')}" + (f" · wrote {s['wrote']}" if s.get("wrote") else ""))
    print(f"  plan: {s.get('plan')}")
    m = s.get("micro")
    if m:
        print(f"  micro ({m.get('axis')}): {m.get('ask')}")
        for i, opt in enumerate(m.get("options", []), 1):
            b = (m.get("bearing") or [None] * len(m["options"]))[i - 1]
            bt = f" [{', '.join(f'{k} {v:+d}' for k, v in b.items())}]" if b else ""
            print(f"    {i}. {opt}{bt}" + ("  (default)" if m.get("default") == i else ""))
    if s.get("world_move"):
        print(f"  world move {'paid' if s.get('world_move_used') else 'owed'}: {s['world_move']}")
    if plan is not None and s.get("status") != "skipped":
        for o in owed_moves(plan):
            print(f"  world move owed (from skipped slot {o['n']}): {o['world_move']}")
    if s.get("day"):
        print(f"  colour: {colour_for(s['day'])}")
    if full:
        key = s.get("beat") if s.get("kind") == "spine" else s.get("quest")
        if key:
            print(f"  --- arc {key} ---")
            secs = arc_sections()
            if key in secs:
                print_arc(key)
            else:
                print(f"  (no `{key}` section in arc.md yet)")
            m = re.match(r"^b(\d)\.(\d+)$", str(key))
            if s.get("kind") == "spine" and m and int(m.group(2)) > 1:  # the choice that closed the last beat bends this one
                prev = f"b{m.group(1)}.{int(m.group(2)) - 1}"
                down = [l for l in secs.get(prev, (0, "", []))[2] if "Downstream" in l]
                if down:
                    print(f"  --- arc {prev}: the Downstream line of the choice that closed it (honour it in this beat) ---")
                    for l in down:
                        print(l)


def parse_value(v):
    if v in ("null", "none", "None"):
        return None
    if v in ("true", "True"):
        return True
    if v in ("false", "False"):
        return False
    try:
        return int(v)
    except ValueError:
        pass
    try:
        return float(v)
    except ValueError:
        pass
    if v.startswith(("[", "{")):
        try:
            return json.loads(v)
        except json.JSONDecodeError:
            pass
    return v


def parse_kv(pairs):
    out = {}
    for p in pairs:
        if "=" not in p:
            die(f"expected key=value, got {p!r}")
        k, v = p.split("=", 1)
        out[k.strip()] = parse_value(v.strip())
    return out


# ---------------------------------------------------------------- commands: digest & due
def cmd_now(args):
    st = State()
    plan, world, ledger, bearing = st.plan, st.world, st.ledger, st.bearing
    pos = plan["position"]
    lines = []
    beat = plan.get("core_beats", {}).get(pos.get("beat"), {})
    title = f" — {world.get('chapter_title', '')}" if int(world.get("chapter", -1)) == int(pos["chapter"]) else " (world.json still on chapter %s)" % world.get("chapter")
    lines.append(f"Book {ROMAN[int(pos['book'])]} · Chapter {pos['chapter']}{title} · {pos.get('beat')} {beat.get('title', '')} ({beat.get('status', '?')}) · stage {pos['stage']} · next scene {pos['next_scene']}")
    planned_beats = [k for k, v in plan.get("core_beats", {}).items() if re.match(rf"^b{pos['book']}\.", k) and v.get("status") == "planned"]
    warn = f" · ⚠ {len(planned_beats)} core beats still planned: compress ahead if the Knot nears" if len(planned_beats) > 2 else ""
    lines.append(f"Last written {pos.get('last_written')} · chapter question: {short(plan['chapter'].get('question'), 110)}{warn}")
    lines.append(road_line(st))
    s = next_slot(plan)
    if s:
        lines.append("Next: " + slot_label(s) + (" · micro " + s["micro"]["axis"] if s.get("micro") else ""))
        lines.append("  " + short(s.get("plan"), 150))
    else:
        lines.append("Next: no slot planned; `plan chapter open --number N '<json>'`")
        lines.append("  (every slot written or skipped)")
    for o in owed_moves(plan):
        lines.append(f"World move owed (slot {o['n']}): {short(o['world_move'], 120)}")
    q = plan.get("quests", {})
    live = [f"{k} (stage {v.get('stage')})" for k, v in q.items() if v.get("status") == "live"]
    avail = [f"{k} ({v.get('priority')})" for k, v in q.items() if v.get("status") == "available"]
    lines.append("Quests live: " + (", ".join(live) or "none"))
    lw = str(pos.get("last_written") or "")
    lw_key = (WROTE_RE.match(lw).group(3) or WROTE_RE.match(lw).group(2)) if WROTE_RE.match(lw) else ""
    betweens = [x for x in st.world.get("scenes", []) if str(x.get("scene", "")).startswith("between-") and str(x.get("after", "")) == lw_key]
    if betweens:
        lines.append(f"Between pieces after the last scene: {len(betweens)} of 2 (" + ", ".join(str(x.get("scene")) for x in betweens) + ")")
    lines.append("Quests available: " + short(", ".join(avail) or "none", 160))
    if int(pos["chapter"]) >= 2 and not live:
        first_req = next((k for k, v in q.items() if v.get("status") == "available" and v.get("priority") == "required"), None)
        lines.append("⚠ no quest live; plan a stage of " + (first_req or "any available quest") + " (design §5.2)")
    om = plan.get("open_micro")
    if om:
        lines.append(f"Open micro (slot {om.get('slot')}, scene {om.get('scene')}, {om.get('axis')}): {om.get('ask')}")
        lines.append("  " + short(" / ".join(f"{i}. {o}" for i, o in enumerate(om.get("options", []), 1)), 170))
    else:
        lines.append("Micro: none open")
    lines.append(bearing_line(bearing))
    due_now, overdue, future = [], [], 0
    for e, it in pending_items(ledger):
        s_ = at_status(it.get("at", ""), st)
        if s_ == "due":
            due_now.append(it)
        elif s_ == "overdue":
            overdue.append(it)
        else:
            future += 1
    dues = [f"DUE NOW {it['id']} [{it.get('weight')}] @{it.get('at')}: {short(it.get('what'), 120)}" for it in due_now]
    dues += [f"OVERDUE {it['id']} [{it.get('weight')}] @{it.get('at')}: {short(it.get('what'), 120)}" for it in overdue]
    if dues:
        lines += dues[:6]
        if len(dues) > 6:
            lines.append(f"  (+{len(dues) - 6} more due/overdue; `saga.py due`)")
    else:
        lines.append("Due now: nothing")
    shown, other = [], 0
    for r in ledger.get("rules", []):
        state, detail = rule_state(r, st)
        if state in ("UNKNOWN TERM", "MALFORMED"):
            shown.insert(0, f"RULE {state} {r['id']}: {detail}")
        elif state == "ARMED" and r.get("if", "").strip() != "true":
            shown.append(f"RULE ARMED {r['id']} ({r.get('where')}): {short(r.get('then'), 100)}")
        else:
            near = rule_near(r, st)
            if near and state == "NOT MET":
                shown.append(f"RULE near {r['id']}: {'; '.join(near)}")
            else:
                other += 1
    lines += shown[:4]
    if len(shown) > 4:
        lines.append(f"  (+{len(shown) - 4} more rules armed/near)")
    lines.append(f"+{future} pending later, +{other} rules quiet; `saga.py due --all` · `saga.py check`")
    if len(lines) > NOW_CAP:
        lines = lines[: NOW_CAP - 1] + [lines[-1]]
    print("\n".join(lines))


def cmd_due(args):
    st = State()
    items = list(pending_items(st.ledger))

    def show(rows, label=None):
        for e, it in rows:
            tag = label or at_status(it.get("at", ""), st).upper()
            print(f"{it['id']} [{it.get('weight')}] when={it.get('when')} at={it.get('at')} {tag} · from {e['id']} ({e['made'].get('date')}: {short(e.get('chose'), 60)})")
            print(f"  {it.get('what')}")

    if args.all:
        if not items:
            print("nothing pending")
        show(items)
        return
    now_rows = [(e, it) for e, it in items if at_status(it.get("at", ""), st) in ("due", "overdue")]
    if args.at:
        exact = [(e, it) for e, it in items if it.get("at") == args.at or it.get("at") == "any"]
        rest = [(e, it) for e, it in now_rows if (e, it) not in exact]
        print(f"aimed at {args.at}:" + ("" if exact else " nothing pending"))
        show(exact, label=f"AT {args.at}")
        print("also due or overdue now:" + ("" if rest else " nothing"))
        show(rest)
        return
    if not now_rows:
        print("nothing pending")
        return
    show(now_rows)


# ---------------------------------------------------------------- commands: ledger writes
def validate_entry(entry, ledger, plan, bearing=None, world=None, pending=False):
    """Shape and target checks for a ledger entry. Every refusal is found here, before cmd_add applies or prints
    anything: ids, made, chose, the `now` keys, Bearing moves (known pole, |n| <= BEARING_MAX_MOVE), approval
    targets (a world.json companion, or with --pending one in companions_to_come) and the due items."""
    probs = []
    eid = entry.get("id", "")
    if not ENTRY_ID_RE.match(eid):
        probs.append(f"id {eid!r} must look like c01.3")
    ids = {e["id"] for e in ledger["entries"]} | {it["id"] for e in ledger["entries"] for it in e.get("due", [])}
    if eid in ids:
        probs.append(f"id {eid} already in the ledger")
    made = entry.get("made")
    if not isinstance(made, dict) or not {"chapter", "scene", "date"} <= set(made):
        probs.append("made must be {chapter, scene, date}")
    elif ENTRY_ID_RE.match(eid) and int(ENTRY_ID_RE.match(eid).group(1)) != int(made["chapter"]):
        probs.append(f"id chapter {ENTRY_ID_RE.match(eid).group(1)} != made.chapter {made['chapter']}")
    if not entry.get("chose"):
        probs.append("chose is required")
    now = entry.setdefault("now", {})
    for k in now:
        if k not in ("approval", "bearing", "flags", "factions"):
            probs.append(f"now.{k} is not one of approval/bearing/flags/factions")
    for pole, n in (now.get("bearing") or {}).items():
        if not isinstance(n, int) or isinstance(n, bool) or abs(n) > BEARING_MAX_MOVE:
            probs.append(f"now.bearing.{pole} {n!r}: a choice moves one axis by ±1 (micro), ±2/3 (climax), ±4 (betrayal or sacrifice)")
        if bearing is not None and pole_axis(bearing, pole) is None:
            probs.append(f"now.bearing: unknown pole {pole!r}; poles: " + ", ".join(w for ax in bearing["axes"].values() for w in (ax["left"], ax["right"])))
    known_flags = plan.get("flags", {})
    for k, v in (now.get("flags") or {}).items():
        if k not in known_flags:
            probs.append(f"now.flags.{k}: not a flag in plan.json (add it first: `plan flag --new {k}=false`, and list it in the arc's ## flags)")
        if not (v is None or isinstance(v, bool)):
            probs.append(f"now.flags.{k} {v!r}: a flag is true, false or null")
    if world is not None:
        for cid, dlt in (now.get("approval") or {}).items():
            if cid in world.get("companions", {}):
                continue
            if pending and cid in plan.get("companions_to_come", {}):
                continue
            probs.append(f"now.approval.{cid}: not a companion in world.json (use --pending for companions_to_come)")
    for i, it in enumerate(entry.setdefault("due", [])):
        did = it.get("id", "")
        if not DUE_ID_RE.match(did) or not did.startswith(eid):
            probs.append(f"due[{i}].id {did!r} must be {eid} plus a letter")
        if did in ids:
            probs.append(f"due id {did} already in the ledger")
        if not WHEN_RE.match(str(it.get("when", ""))):
            probs.append(f"due[{i}].when {it.get('when')!r} not in the grammar (see --help)")
        mo = re.match(r"^on:(\w+)$", str(it.get("when", "")))
        if mo and mo.group(1) not in known_flags:
            probs.append(f"due[{i}].when 'on:{mo.group(1)}': not a flag in plan.json")
        if it.get("weight") not in WEIGHTS:
            probs.append(f"due[{i}].weight must be one of {WEIGHTS}")
        if not it.get("what"):
            probs.append(f"due[{i}].what is required")
        it.setdefault("status", "pending")
        if it["status"] != "pending":
            probs.append(f"due[{i}].status must start pending")
        it["at"] = resolve_at(it.get("when"), plan) if WHEN_RE.match(str(it.get("when", ""))) else it.get("when")
        # canonical key order
        ordered = {k: it[k] for k in ("id", "when", "at", "weight", "what", "status") if k in it}
        ordered.update({k: v for k, v in it.items() if k not in ordered})
        entry["due"][i] = ordered
    return probs


LETTERS = "abcdefghijklmnopqrstuvwxyz"


def downstream_due(entry, plan):
    """One due item per flag the entry sets, so the arc's Downstream line for this choice is owed to what follows and
    printed by `now` until fired or void, never left to memory. A flag the entry's own due items already name is skipped.
    A climax choice aims at the next chapter (the Downstream line bends the next beat); a micro at the next scene."""
    flags = (entry.get("now") or {}).get("flags") or {}
    eid = str(entry.get("id", ""))
    if not flags or not ENTRY_ID_RE.match(eid):
        return []
    pos = plan.get("position", {})
    when = ch2(int(pos.get("chapter", 0)) + 1) if pos.get("stage") in ("climax", "choice", "transition") else "next"
    beat = pos.get("beat") or "the beat"
    dues = entry.setdefault("due", [])
    used = {str(it.get("id", ""))[-1:] for it in dues}
    made = []
    for flag in flags:
        if any(flag in str(it.get("what", "")) for it in dues):
            continue
        letter = next((c for c in LETTERS if c not in used), None)
        if letter is None:
            break
        used.add(letter)
        dues.append({"id": f"{eid}{letter}", "when": when, "weight": "scene",
                     "what": f"Downstream of `{flag}` ({beat}): open what follows the way the arc's Downstream line for this "
                             f"choice says (`saga.py arc {beat}`); fire where it is honoured, void with a reason if the story made it moot"})
        made.append(f"{eid}{letter}")
    return made


def cmd_add(args):
    st = State()
    try:
        entry = json.loads(args.entry)
    except json.JSONDecodeError as e:
        die(f"entry is not valid JSON: {e}")
    ledger, plan, world = st.ledger, st.plan, st.world
    auto = downstream_due(entry, plan)  # one due item per flag set: the Downstream line is owed, not remembered
    # first pass: shape, poles, magnitudes, the entry's own approval targets
    probs = validate_entry(entry, ledger, plan, bearing=st.bearing, world=world, pending=args.pending)
    if probs:
        die("refusing the entry:\n  " + "\n  ".join(probs))
    now = entry["now"]
    witnessed = [w.strip() for w in (args.witnessed or "").split(",") if w.strip()]
    # companion-preference approval from bearing deltas (computed quietly; printed only once everything is accepted)
    pref_delta = {}
    for cid in witnessed:
        prefs = [p.lower() for p in plan.get("companions", {}).get(cid, {}).get("prefers", [])]
        if cid not in plan.get("companions", {}):
            die(f"--witnessed {cid}: not in plan.json companions")
        for pole, n in (now.get("bearing") or {}).items():
            aid, sign = pole_axis(st.bearing, pole)
            ax = st.bearing["axes"][aid]
            opposite = ax["left"].lower() if sign > 0 else ax["right"].lower()
            toward = n > 0
            if pole.lower() in prefs:
                pref_delta[cid] = pref_delta.get(cid, 0) + (2 if toward else -2)
            elif opposite in prefs:
                pref_delta[cid] = pref_delta.get(cid, 0) + (-2 if toward else 2)
    folded = []
    if pref_delta:
        appr = now.setdefault("approval", {})
        for cid, dlt in pref_delta.items():
            appr[cid] = appr.get(cid, 0) + dlt
            folded.append(f"witnessed {cid}: preference {dlt:+d} folded into now.approval")
        # the folded approval targets must be companions too, before anything is printed as applied
        bad = [cid for cid in pref_delta if cid not in world.get("companions", {}) and not (args.pending and cid in plan.get("companions_to_come", {}))]
        if bad:
            die("refusing the entry:\n  " + "\n  ".join(f"now.approval.{cid} (folded from --witnessed): not a companion in world.json (use --pending for companions_to_come)" for cid in bad))
    for line in folded:
        print(line)
    # apply approval
    for cid, dlt in (now.get("approval") or {}).items():
        comp = world.get("companions", {})
        if cid in comp:
            old = comp[cid].get("approval", 0)
            comp[cid]["approval"] = clamp(old + int(dlt), -100, 100)
            print(f"approval {cid}: {old} → {comp[cid]['approval']}")
            st.touch("world")
        else:  # validate_entry accepted it, so it is in companions_to_come with --pending
            c = plan["companions_to_come"][cid]
            old = c.get("approval_pending", 0)
            c["approval_pending"] = old + int(dlt)
            print(f"approval_pending {cid}: {old} → {c['approval_pending']}")
            st.touch("plan")
    for pole, n in (now.get("bearing") or {}).items():
        move_bearing(st, pole, n, entry["id"])
    for k, v in (now.get("flags") or {}).items():
        old = plan.setdefault("flags", {}).get(k, None)
        plan["flags"][k] = v
        print(f"flag {k}: {old} → {v}")
        st.touch("plan")
    for fid, dlt in (now.get("factions") or {}).items():
        f = plan.setdefault("factions", {})
        old = f.get(fid, 0)
        f[fid] = clamp(old + int(dlt), -100, 100)
        print(f"faction {fid}: {old} → {f[fid]}")
        st.touch("plan")
    ordered = {k: entry[k] for k in ("id", "made", "chose", "now", "due") if k in entry}
    ordered.update({k: v for k, v in entry.items() if k not in ordered})
    ledger["entries"].append(ordered)
    st.touch("ledger")
    for it in ordered["due"]:
        print(f"due {it['id']} when={it['when']} → at={it['at']} [{it['weight']}]" + ("  (auto: the flag's Downstream line)" if it["id"] in auto else ""))
    st.save(dry=args.dry_run)
    print(("(dry run) " if args.dry_run else "") + f"ledger entry {entry['id']} recorded with {len(ordered['due'])} due item(s)")


def find_due(ledger, did):
    for e in ledger["entries"]:
        for it in e.get("due", []):
            if it["id"] == did:
                return e, it
    die(f"no due item {did} in the ledger")


def cmd_fire(args):
    st = State()
    if not WHERE_RE.match(args.where):
        die(f"--where {args.where!r} must look like ch03:s2, ch03:climax, ch03:interlude or book2")
    e, it = find_due(st.ledger, args.id)
    if it["status"] != "pending":
        die(f"{args.id} is already {it['status']}")
    it["status"] = f"fired@{args.where}"
    st.touch("ledger")
    st.save()
    print(f"{args.id} fired at {args.where}: {it['what']}")


def cmd_void(args):
    st = State()
    e, it = find_due(st.ledger, args.id)
    if it["status"] != "pending":
        die(f"{args.id} is already {it['status']}")
    it["status"] = f"void:{args.why}"
    st.touch("ledger")
    st.save()
    print(f"{args.id} void: {args.why}")


def cmd_archive(args):
    st = State()
    ledger, plan = st.ledger, st.plan
    cur = int(plan["position"]["book"])
    keep, gone = [], []
    for e in ledger["entries"]:
        spent = all(it.get("status") != "pending" for it in e.get("due", []))
        if spent and book_of_chapter(plan, e["made"]["chapter"]) <= cur - 2:
            gone.append(e)
        else:
            keep.append(e)
    if not gone:
        print("nothing to archive")
        return
    arch = load_json(P["archive"]) if P["archive"].exists() else {"_about": "Archived ledger entries (all due items fired or void, older than two Books). Never read by `now`.", "entries": []}
    arch["entries"] += gone
    ledger["entries"] = keep
    save_json(P["archive"], arch)
    st.touch("ledger")
    st.save()
    print(f"archived {len(gone)} entr{'y' if len(gone) == 1 else 'ies'}: " + ", ".join(e["id"] for e in gone))


# ---------------------------------------------------------------- commands: bearing / route
def cmd_bearing(args):
    st = State()
    if args.pole == "show":
        b = st.bearing
        for aid, ax in b["axes"].items():
            v = ax["value"]
            width = b["range"] * 2
            marker = v + b["range"]
            bar = "".join("●" if i == marker else "─" for i in range(width + 1))
            print(f"{ax['left']:>7} {bar} {ax['right']:<8} {v:+d} · {axis_word(b, aid)}")
        print(f"epithet: {b['epithet'] or '— (none named yet)'} · leans: {', '.join(b['leans']) or 'none'} · moves: {len(b.get('history', []))}")
        return
    if args.n is None or not args.why:
        die("usage: bearing <pole> <n> --why <ledger id | gm:reason> [--force]")
    move_bearing(st, args.pole, args.n, args.why, force=args.force)
    st.save()


def cmd_route(args):
    st = State()
    plan = st.plan
    rows = chapter_rows()
    if args.action == "show":
        for key, r in plan.get("route", {}).items():
            chapters = [int(c) for c in r.get("chapters", [])]
            score, tiers, missing = road_score(chapters, rows)
            closed = ", ".join(f"ch{c} {t}" for c, t in tiers) or "none closed"
            miss = f" · unclosed: {missing}" if missing else ""
            print(f"{key}: chapters {chapters} · {closed} · score {score:+d}{miss} · road {r.get('road') or 'undecided'}"
                  + (f" (override: {r['override']})" if r.get("override") else "")
                  + (f" · transition ch{r['transition_chapter']}" if r.get("transition_chapter") else ""))
        return
    key = f"book{args.book}"
    r = plan.setdefault("route", {}).setdefault(key, {"chapters": [], "road": None, "override": None, "transition_chapter": None})
    chapters = [int(c) for c in r.get("chapters", [])]
    score, tiers, missing = road_score(chapters, rows)
    if r.get("road") and not args.road:
        die(f"{key} already decided ({r['road']}{' by override' if r.get('override') else ''}); pass --road … --why … to change it")
    if args.road:
        if not args.why:
            die("--road needs --why")
        r["road"] = args.road
        r["override"] = args.why
        print(f"{key}: road {args.road} by override ({args.why}); scored {score:+d} over {len(tiers)} closed chapter(s)")
    else:
        if missing:
            die(f"{key}: chapters {missing} have no chapters.csv row; run darrow.py chapter-close first, or decide with --road … --why …")
        if not chapters:
            die(f"{key}: no chapters listed in route")
        r["road"] = decide_road(chapters, rows)
        r["override"] = None
        print(f"{key}: road {r['road']} (score {score:+d}: " + ", ".join(f"ch{c} {t}" for c, t in tiers) + ")")
    if r.get("transition_chapter") is None and chapters:
        r["transition_chapter"] = max(chapters)
        print(f"{key}: transition_chapter set to {r['transition_chapter']} (the Book's last listed chapter); Edit if wrong")
    st.touch("plan")
    st.save()


# ---------------------------------------------------------------- commands: plan
def cmd_plan(args):
    st = State()
    plan = st.plan
    a = args.action
    if a == "next":
        s = next_slot(plan, args.date)
        if not s:
            print("no next or planned slot; open the next chapter with `plan chapter open`")
            for o in owed_moves(plan):
                print(f"  world move owed (from skipped slot {o['n']}): {o['world_move']}")
            return
        print_slot(s, full=args.full, plan=plan)
        return
    if a == "climax":
        ch = plan["chapter"]
        c = ch.get("climax") or {}
        print(f"chapter {ch.get('number')} · question: {ch.get('question')}")
        print(f"  plan: {c.get('plan')}")
        print("  checks: " + ("; ".join(c.get("checks") or []) or "none"))
        for i, o in enumerate(c.get("options") or [], 1):
            print(f"  {i}. {o}" + ("  (default)" if c.get("default") == i else ""))
        if c.get("default") is not None:
            print(f"  default: option {c['default']} (taken by the Bearing if the choice is still open at the second close of the next chapter)")
        print("  world moves left: " + (" / ".join(ch.get("world_moves") or []) or "none"))
        for o in owed_moves(plan):
            print(f"  world move owed (from skipped slot {o['n']}): {o['world_move']}")
        return
    if a == "done":
        s = slot_by_n(plan, args.n)
        if s.get("status") in ("written", "skipped") and not args.force:
            die(f"slot {s['n']} is already {s['status']}" + (f" ({s.get('wrote')})" if s.get("wrote") else "") + "; pass --force to redo")
        if args.force and s.get("world_move") and not s.get("world_move_used"):
            # redoing a skipped slot: its unused off-page move goes back to the front of the chapter pool
            plan["chapter"].setdefault("world_moves", []).insert(0, s["world_move"])
            print(f"world move returned to the chapter: {s['world_move']}")
        if args.force:
            s.pop("world_move", None)
            s.pop("world_move_used", None)
        if args.skipped and args.wrote:
            die("pass --skipped or --wrote, not both")
        if args.skipped:
            s["status"] = "skipped"
            s["wrote"] = None
            moves = plan["chapter"].setdefault("world_moves", [])
            if moves:
                s["world_move"] = moves.pop(0)
                s["world_move_used"] = False
                print(f"slot {s['n']} skipped; the next scene opens with one off-page world move: {s['world_move']}")
            else:
                print(f"slot {s['n']} skipped; no world_moves left in the chapter, invent one off-page move")
            if s.get("kind") == "spine":
                print("a skipped spine slot's content folds into the next spine slot or the climax")
        else:
            if not args.wrote or not WROTE_RE.match(args.wrote):
                die("--wrote must look like ch01:s3 or ch01:interlude")
            m = WROTE_RE.match(args.wrote)
            if int(m.group(1)) != int(plan["position"]["chapter"]):
                die(f"--wrote {args.wrote} names chapter {int(m.group(1))}; the plan is on chapter {plan['position']['chapter']}")
            if m.group(3) and int(m.group(3)) > int(plan["position"].get("next_scene") or 1):
                die(f"--wrote {args.wrote} skips ahead; the next scene is {plan['position'].get('next_scene')}")
            heads = chapter_headings(st.world)
            key = m.group(3) or m.group(2)
            if heads is not None and key not in {k for k, _ in heads}:
                want = f"### Scene {key}" if m.group(3) else "### " + key.split("-")[0].capitalize()
                print(f"⚠ {st.world.get('chapter_file')} has no `{want}` heading yet; write the scene before `saga.py check`")
            s["status"] = "written"
            s["wrote"] = args.wrote
            plan["position"]["last_written"] = args.wrote
            plan["position"]["stage"] = "scene"
            if m.group(3):
                plan["position"]["next_scene"] = max(int(plan["position"].get("next_scene") or 1), int(m.group(3)) + 1)
            if s.get("kind") == "quest" and s.get("quest"):
                q = plan.setdefault("quests", {}).setdefault(s["quest"], {"status": "available", "stage": 0, "priority": "optional"})
                q["stage"] = int(s.get("stage") or q.get("stage", 0) + 1)
                total = arc_quest_stage_count(s["quest"])
                q["status"] = "done" if (total and q["stage"] >= total) or s.get("last") else "live"
                print(f"quest {s['quest']}: stage {q['stage']}" + (f"/{total}" if total else "") + f" · {q['status']}" + (" (slot marked last)" if s.get("last") and q["status"] == "done" else ""))
            if s.get("kind") == "spine" and s.get("beat"):
                b = plan.setdefault("core_beats", {}).setdefault(s["beat"], {"title": s["beat"], "status": "planned"})
                if b.get("status") == "planned":
                    b["status"] = "in_progress"
                plan["position"]["beat"] = s["beat"]
            print(f"slot {s['n']} written as {args.wrote} · next scene {plan['position']['next_scene']} · stage scene")
            if s.get("micro"):
                print(f"slot {s['n']} carries a micro: if the scene ended on it, `plan micro open {s['n']}`")
            pay_owed_moves(plan, "scene")
        nxt = next((x for x in sorted(plan["chapter"]["slots"], key=lambda x: float(x.get("n", 0))) if x.get("status") == "planned"), None)
        if nxt and not any(x.get("status") == "next" for x in plan["chapter"]["slots"]):
            nxt["status"] = "next"
            print(f"next: {slot_label(nxt)}")
        st.touch("plan")
        st.save()
        return
    if a == "slot":
        s = slot_by_n(plan, args.n)
        if s.get("status") in ("written", "skipped") and not args.force:
            die(f"slot {s['n']} is {s['status']}" + (f" ({s.get('wrote')})" if s.get("wrote") else "") + "; --force to edit it")
        kv = parse_kv(args.kv)
        for k in kv:
            if k not in SLOT_FIELDS:
                die(f"slot field {k!r} not editable here (fields: {', '.join(SLOT_FIELDS)}); status/wrote move with `plan done`")
        for k, v in kv.items():
            if k == "kind" and v not in SLOT_KINDS:
                die(f"slot kind must be one of {SLOT_KINDS}")
            if k == "micro" and v is not None and not isinstance(v, dict):
                die("micro must be JSON (micro='{\"axis\":…,\"ask\":…,\"options\":[…],\"bearing\":[…],\"default\":1}') or null")
            if k == "day" and v is not None:
                try:
                    dt.date.fromisoformat(str(v))
                except ValueError:
                    die(f"day {v!r} is not a date")
                v = str(v)
            if k == "float" and not isinstance(v, bool):
                die("float must be true or false")
            print(f"slot {s['n']}.{k}: {s.get(k)!r} → {v!r}")
            s[k] = v
        print_slot(s)
        st.touch("plan")
        st.save()
        print("run `saga.py check`")
        return
    if a == "micro":
        if args.sub == "open":
            s = slot_by_n(plan, args.n)
            if not s.get("micro"):
                die(f"slot {args.n} has no micro planned")
            if s.get("status") != "written":
                die(f"slot {args.n} is {s.get('status')}: write its scene and `plan done {args.n} --wrote …` first (the micro takes its scene key from the slot)")
            if plan.get("open_micro"):
                die(f"a micro is already open (slot {plan['open_micro'].get('slot')}); close it first (it resolves to its default if unanswered)")
            m = dict(s["micro"])
            scene_key = micro_scene_key(plan, s)
            plan["open_micro"] = {"slot": s["n"], "chapter": int(plan["chapter"].get("number")), "scene": scene_key, "opened": today_local().isoformat(), **m}
            print(f"micro open from slot {s['n']} at scene {scene_key} ({m.get('axis')}): {m.get('ask')} · default {m.get('default')}")
            print(f"  world.json choices[] entry: chapter {plan['chapter'].get('number')}, scene \"{scene_key}\", kind micro")
        else:
            om = plan.get("open_micro")
            if not om:
                die("no micro is open")
            opt = args.option if args.option is not None else (om.get("default") if args.by == "bearing" else None)
            if opt is None:
                die("pass --option K (or --by bearing to take the slot's default)")
            s = next((x for x in plan["chapter"]["slots"] if str(x.get("n")) == str(om.get("slot"))), None)
            if s is not None and s.get("micro") is not None:
                if opt not in range(1, len(s["micro"].get("options") or []) + 1):
                    die(f"option {opt} is not one of slot {s['n']}'s {len(s['micro'].get('options') or [])} options")
                s["micro"]["answer"] = {"option": opt, "by": args.by}
            plan["open_micro"] = None
            print(f"micro from slot {om.get('slot')} (scene {om.get('scene')}) closed: option {opt} by {args.by}" + (" (the slot's default)" if args.option is None else ""))
        st.touch("plan")
        st.save()
        return
    if a == "chapter" and args.sub == "template":
        try:
            ws = dt.date.fromisoformat(args.week_start or "")
        except ValueError:
            die("--week_start must be a date (the Sunday), YYYY-MM-DD")
        if ws.weekday() != 6:
            die(f"--week_start {ws} is not a Sunday")
        print(dumps(chapter_template(ws, plan)))
        return
    if a == "chapter":
        if not args.number or not args.json:
            die("plan chapter open needs --number N and the chapter JSON (start from `plan chapter template --week_start <Sunday>`)")
        if plan.get("open_micro"):
            om = plan["open_micro"]
            die(f"a micro is still open (slot {om.get('slot')}, scene {om.get('scene')}); resolve it first: /choose, or `plan micro close --option {om.get('default')} --by bearing`")
        try:
            ch = json.loads(args.json)
        except json.JSONDecodeError as e:
            die(f"chapter JSON invalid: {e}")
        ch["number"] = int(args.number)
        cur_n = int(plan["position"].get("chapter", 0))
        if int(args.number) != cur_n + 1 and not args.force:
            die(f"chapter {args.number} does not follow chapter {cur_n}; chapters open in order, one per calendar week (--force to open it anyway)")
        if not ch.get("week_start"):
            die("chapter JSON needs week_start (the Sunday)")
        ch.setdefault("slots", [])
        ch.setdefault("world_moves", [])
        ch.setdefault("climax", {"plan": "", "checks": [], "options": []})
        ordered = {k: ch[k] for k in ("number", "week_start", "question", "slots", "world_moves", "climax") if k in ch}
        ordered.update({k: v for k, v in ch.items() if k not in ordered})
        for s in ordered["slots"]:
            s.setdefault("status", "planned")
            s.setdefault("wrote", None)
            s.setdefault("micro", None)
            s.setdefault("float", False)
        if ordered["slots"] and not any(s.get("status") == "next" for s in ordered["slots"]):
            ordered["slots"][0]["status"] = "next"
        # what the outgoing chapter leaves behind: unwritten slots are named; owed world moves carry over
        old = plan.get("chapter", {})
        left = [s for s in old.get("slots", []) if s.get("status") in ("planned", "next")]
        owed = owed_moves(plan) if old.get("slots") else []
        if left:
            print(f"⚠ chapter {old.get('number')} leaves slots {[s['n'] for s in left]} unwritten (their content folds into the climax you have written)")
        for o in owed:
            print(f"⚠ world move still owed (slot {o['n']} of chapter {old.get('number')}): {o['world_move']} → carried to chapter {args.number}'s world_moves")
        ordered["world_moves"] = [o["world_move"] for o in owed] + list(ordered.get("world_moves") or [])
        plan["chapter"] = ordered
        book = plan["position"]["book"]
        r = plan.setdefault("route", {}).setdefault(f"book{book}", {"chapters": [], "road": None, "override": None, "transition_chapter": None})
        if int(args.number) not in [int(c) for c in r["chapters"]]:
            r["chapters"].append(int(args.number))
        plan["position"].update({"chapter": int(args.number), "next_scene": 1, "stage": "scene"})
        st.touch("plan")
        st.save()
        print(f"chapter {args.number} opened (week of {ch['week_start']}, {len(ordered['slots'])} slots" + (f", climax default {ordered['climax'].get('default')}" if ordered.get("climax", {}).get("default") is not None else "") + "); run `saga.py check`")
        return
    if a == "book":
        n = int(args.n)
        pos = plan["position"]
        cur = int(pos["book"])
        if n <= cur:
            die(f"already in Book {cur}; `plan book open` only moves forward")
        if n > cur + 1:
            print(f"note: skipping Book {cur + 1}; Books open one at a time as a rule")
        r = plan.setdefault("route", {}).setdefault(f"book{n}", {"chapters": [], "road": None, "override": None, "transition_chapter": None})
        beats = plan.setdefault("core_beats", {})
        seeded = []
        for k, (lvl, title, _) in arc_sections().items():
            if re.match(rf"^(b{n}\.\d+|t{n})$", k) and k not in beats:
                beats[k] = {"title": title.split("—", 1)[1].strip() if "—" in title else k, "status": "planned"}
                seeded.append(k)
        if f"t{n}" not in beats and any(f"t{n}.{road}" in arc_sections() for road in ROADS):
            beats[f"t{n}"] = {"title": f"Book {ROMAN[n]} transition", "status": "planned"}
            seeded.append(f"t{n}")
        folded = []
        for k, b in beats.items():
            if re.match(rf"^b{cur}\.\d+$", k) and b.get("status") == "planned":
                b["status"] = "folded"
                folded.append(k)
        # quests: seed Book N's from the arc (priority from its `- **priority:**` line); drop the old Book's
        # unrun optional quests; required ones stay available and are warned (floating ones may run anywhere)
        quests = plan.setdefault("quests", {})
        q_seeded, q_dropped, q_required = [], [], []
        for k, (lvl, title, body) in arc_sections().items():
            if re.match(rf"^q{n}\.[a-z0-9_]+$", k) and k not in quests:
                pr = "optional"
                for l in body:
                    mp = re.match(r"^\s*-\s*\*\*priority:\*\*\s*(required|optional|floating)", l, re.I)
                    if mp:
                        pr = mp.group(1).lower()
                        break
                quests[k] = {"status": "available", "stage": 0, "priority": pr}
                q_seeded.append(f"{k} ({pr})")
        for k, q in quests.items():
            if re.match(rf"^q{cur}\.", k) and q.get("status") == "available":
                if q.get("priority") == "optional":
                    q["status"] = "dropped"
                    q["why"] = f"Book {ROMAN[cur]} closed before it ran"
                    q_dropped.append(k)
                elif q.get("priority") == "required":
                    q_required.append(k)
        pos["book"] = n
        pos["beat"] = f"b{n}.1"
        if f"b{n}.1" not in beats:
            print(f"warning: arc.md has no `## b{n}.1 — …` heading; add it (or Edit core_beats) before `saga.py check`")
        st.touch("plan")
        st.save()
        print(f"Book {ROMAN[n]} opened: position.book {cur} → {n}, beat b{n}.1 · route.book{n} {'seeded' if not r['chapters'] else 'kept'}"
              + f" · core beats seeded: {', '.join(seeded) or 'none new'}"
              + (f" · Book {ROMAN[cur]} beats folded: {', '.join(folded)}" if folded else "")
              + f" · quests seeded: {', '.join(q_seeded) or 'none new'}"
              + (f" · Book {ROMAN[cur]} optional quests dropped: {', '.join(q_dropped)}" if q_dropped else ""))
        if q_required:
            print(f"⚠ required quest(s) never ran: {', '.join(q_required)}; re-skin on the road (kept available) or drop by hand: "
                  f"plan quest {q_required[0]} status=dropped why=\"…\"")
        if beats.get(f"t{cur}", {}).get("status") not in (None, "done"):
            print(f"note: t{cur} is {beats[f't{cur}'].get('status')}; `plan beat t{cur} status=done` once the transition is written")
        print(f"next: set world.json book to {n}, then `plan chapter open --number N '<json>'` (it files under route.book{n})")
        return
    if a == "quest":
        q = plan.setdefault("quests", {}).setdefault(args.id, {"status": "available", "stage": 0, "priority": "optional"})
        for k, v in parse_kv(args.kv).items():
            if k == "status" and v not in QUEST_STATUS:
                die(f"quest status must be one of {QUEST_STATUS}")
            print(f"{args.id}.{k}: {q.get(k)} → {v}")
            q[k] = v
        st.touch("plan")
        st.save()
        return
    if a == "beat":
        b = plan.setdefault("core_beats", {}).get(args.id)
        if b is None:
            die(f"no core beat {args.id} in plan.json")
        for k, v in parse_kv(args.kv).items():
            if k == "status" and v not in BEAT_STATUS:
                die(f"beat status must be one of {BEAT_STATUS}")
            print(f"{args.id}.{k}: {b.get(k)} → {v}")
            b[k] = v
        if b.get("status") == "in_progress":
            plan["position"]["beat"] = args.id
        st.touch("plan")
        st.save()
        return
    if a == "flag":
        flags = plan.setdefault("flags", {})
        for k, v in parse_kv(args.kv).items():
            if k not in flags and not args.new:
                die(f"{k} is not a flag in plan.json; `plan flag --new {k}=false` adds it (list it in the arc's ## flags too)")
            if not (v is None or isinstance(v, bool)):
                die(f"flag {k}={v!r}: a flag is true, false or null")
            old = flags.get(k)
            flags[k] = v
            print(f"flag {k}: {old} → {v}")
        st.touch("plan")
        st.save()
        return
    if a == "temptation":
        t = plan.setdefault("temptation", {"planted": []})
        t["planted"].append({"text": args.text, "book": plan["position"]["book"], "chapter": plan["position"]["chapter"], "date": today_local().isoformat()})
        st.touch("plan")
        st.save()
        print(f"temptation planted ({len(t['planted'])} so far): {args.text}")
        return
    if a == "companion":
        c = plan.get("companions_to_come", {}).get(args.id)
        if c is None:
            die(f"{args.id} is not in companions_to_come")
        world = st.world
        if args.id in world.get("companions", {}):
            die(f"{args.id} is already a companion in world.json")
        approval = int(c.get("approval_pending", 0))
        world.setdefault("companions", {})[args.id] = {"approval": approval, "present": True, "note": c.get("note", ""), **({"bond": c["bond"]} if "bond" in c else {})}
        ledger = st.ledger
        summed = sum(int((e.get("now", {}).get("approval") or {}).get(args.id, 0)) for e in ledger["entries"])
        ledger["baseline"]["approval"][args.id] = approval - summed
        plan.setdefault("companions", {}).setdefault(args.id, {"prefers": c.get("prefers", [])})
        del plan["companions_to_come"][args.id]
        st.touch("plan", "world", "ledger")
        st.save()
        print(f"{args.id} arrived: approval {approval}, present" + (f", bond {c['bond']}" if "bond" in c else "") + f"; baseline set to {approval - summed}. Give them a saga/characters file and an Edit to the note.")
        return
    if a == "set":
        pos = plan["position"]
        for k, v in parse_kv(args.kv).items():
            if k not in pos:
                die(f"position has no field {k}; fields: {', '.join(pos)}")
            if k == "stage" and v not in STAGES:
                die(f"stage must be one of {STAGES}")
            if k in ("book", "chapter", "next_scene") and (not isinstance(v, int) or isinstance(v, bool) or v < 1):
                die(f"{k} must be a positive integer")
            if k == "stage" and v == "choice" and pos.get("stage") != "climax":
                die(f"stage=choice only follows climax (stage is {pos.get('stage')}); the next chapter is already open: leave the stage alone and fire what the consequence pays off with --where chNN:climax")
            print(f"position.{k}: {pos[k]} → {v}")
            pos[k] = v
            if k == "stage" and v == "climax":
                pay_owed_moves(plan, "climax")
        st.touch("plan")
        st.save()
        return
    die(f"unknown plan action {a}")


# ---------------------------------------------------------------- the chapter file
SCENE_HEAD_RE = re.compile(r"^###\s+Scene\s+(\d+)\s*[—–-]\s*(.+)$")
INTERLUDE_HEAD_RE = re.compile(r"^###\s+Interlude\s*[—–-]\s*(.+)$")
BETWEEN_HEAD_RE = re.compile(r"^###\s+Between\s*[—–-]\s*(.+)$")
CLIMAX_HEAD_RE = re.compile(r"^##\s+Climax\s*[—–-]\s*(.+)$")
CHOICE_HEAD_RE = re.compile(r"^###\s+Choice\s*[—–-]\s*(.+)$")


def chapter_headings(world):
    """The current chapter file's scene-like headings in order, as [(key, title)] with build_site's keys
    ('1', 'interlude', 'interlude-2', 'between-1', 'climax', 'choice'). None when the file is missing."""
    cf = world.get("chapter_file")
    path = ROOT / cf if cf else None
    if not path or not path.exists():
        return None
    out, n_int, n_btw = [], 0, 0
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        m = SCENE_HEAD_RE.match(s)
        if m:
            out.append((m.group(1), m.group(2).strip()))
            continue
        m = INTERLUDE_HEAD_RE.match(s)
        if m:
            n_int += 1
            out.append(("interlude" if n_int == 1 else f"interlude-{n_int}", m.group(1).strip()))
            continue
        m = BETWEEN_HEAD_RE.match(s)
        if m:
            n_btw += 1
            out.append((f"between-{n_btw}", m.group(1).strip()))
            continue
        m = CLIMAX_HEAD_RE.match(s)
        if m:
            out.append(("climax", m.group(1).strip()))
            continue
        m = CHOICE_HEAD_RE.match(s)
        if m:
            out.append(("choice", m.group(1).strip()))
    return out


def norm_title(t):
    return re.sub(r"\s+", " ", str(t or "")).strip().lower().strip(" .")


def day_logged(date):
    """The Ledger's open-day test, read here only to reconcile the slots with it: a daily_log row with any status
    field, a nutrition_log row with data, or a food_entries row. Only a day with none of these is missed."""
    skip = {"date", "dow", "pod", "post_op_week", "dash_week_start"}
    for r in read_csv(P["daily"]):
        if r.get("date") == date and any(str(v or "").strip() for k, v in r.items() if k and k not in skip):
            return True
    for r in read_csv(P["nutrition"]):
        if r.get("date") == date and any(str(v or "").strip() for k, v in r.items() if k and k not in ("date", "day", "week", "wk_post_op")):
            return True
    return any(r.get("date") == date for r in read_csv(P["food"]))


def reconcile_chapter(st, probs):
    """The chapter file, the plan's slots, world.json's scenes[] and the Ledger's closed days must tell one story:
    every written slot has its heading and every heading its slot; next_scene follows the file; scenes[] matches the
    headings and their titles; at most two Betweens run together; a Climax on the page means the stage has moved;
    a written slot's day is closed, a skipped slot's day has nothing logged, and a closed day's slot is written."""
    world, plan = st.world, st.plan
    ch = plan.get("chapter", {})
    pos = plan.get("position", {})
    if ch.get("number") is not None and int(ch.get("number")) != int(pos.get("chapter", -1)):
        probs.append(f"plan.chapter.number {ch.get('number')} is not position.chapter {pos.get('chapter')}")
    heads = chapter_headings(world)
    cf = world.get("chapter_file")
    if heads is None:
        probs.append(f"world.json chapter_file {cf!r} is missing")
        return
    keys = [k for k, _ in heads]
    titles = dict(heads)
    scene_keys = [k for k in keys if k.isdigit()]
    inter_keys = [k for k in keys if k.startswith("interlude")]
    between_keys = [k for k in keys if k.startswith("between-")]
    slots = ch.get("slots", [])
    chn = ch2(pos.get("chapter", 0))
    plan_scenes, plan_inter = set(), set()
    for s in slots:
        if s.get("status") != "written":
            continue
        m = WROTE_RE.match(str(s.get("wrote") or ""))
        if not m:
            continue
        if int(m.group(1)) != int(pos.get("chapter", -1)):
            probs.append(f"slot {s.get('n')} wrote {s.get('wrote')}: not this chapter")
            continue
        key = m.group(3) or m.group(2)
        (plan_scenes if m.group(3) else plan_inter).add(key)
        if key not in keys:
            want = f"### Scene {key}" if m.group(3) else "### " + key.split("-")[0].capitalize()
            probs.append(f"slot {s.get('n')} is written as {s.get('wrote')} but {cf} has no `{want}` heading")
    if slots:
        for k in scene_keys:
            if k not in plan_scenes:
                probs.append(f"{cf} has `### Scene {k}` but no written slot records it (`saga.py plan done N --wrote {chn}:s{k}`)")
        for k in inter_keys:
            if k not in plan_inter:
                probs.append(f"{cf} has an interlude ({k}) but no written slot records it (`saga.py plan done N --wrote {chn}:{k}`)")
    elif scene_keys:
        probs.append(f"the chapter has no slots (a cutaway chapter: interludes only) but {cf} has numbered scenes")
    expect_next = (max(int(k) for k in scene_keys) + 1) if scene_keys else 1
    if str(pos.get("next_scene")) != str(expect_next):
        probs.append(f"position.next_scene is {pos.get('next_scene')} but {cf}'s last scene is {expect_next - 1}: expected {expect_next}")
    wkeys = [str(s.get("scene")) for s in world.get("scenes", [])]
    for k in scene_keys + inter_keys + between_keys:
        if k not in wkeys:
            probs.append(f"world.json scenes[] has no entry for {k} ({titles[k]!r}) of {cf}")
    for s in world.get("scenes", []):
        k = str(s.get("scene"))
        if k not in keys:
            probs.append(f"world.json scenes[] lists {k!r} ({s.get('title')!r}) but {cf} has no such heading")
            continue
        if norm_title(s.get("title")) != norm_title(titles.get(k)):
            probs.append(f"world.json scenes[] titles {k} {s.get('title')!r}; {cf} says {titles.get(k)!r}")
        if k.startswith("between-"):
            before = [kk for kk in keys[: keys.index(k)] if not kk.startswith("between-")]
            if before and str(s.get("after", "")) != before[-1]:
                probs.append(f"world.json scenes[] {k} says after={s.get('after')!r}; in {cf} it follows {before[-1]!r}")
    run = 0
    for k in keys:
        run = run + 1 if k.startswith("between-") else 0
        if run == 3:
            probs.append("three Betweens in a row: at most two between two scenes (a third is two lines and the moment passes)")
    if "climax" in keys and pos.get("stage") == "scene":
        probs.append(f"{cf} has a Climax but position.stage is 'scene' (`plan set stage=climax` comes before writing it)")
    if "choice" in keys and "climax" not in keys:
        probs.append(f"{cf} has a Choice block but no Climax")
    daily = {r.get("date"): r for r in read_csv(P["daily"]) if r.get("date")}
    for s in slots:
        day = s.get("day")
        if not day:
            continue
        closed = yes(daily.get(day, {}).get("closed"))
        if s.get("status") == "written" and not closed:
            probs.append(f"slot {s.get('n')} ({day}) is written but the Ledger has not closed {day} (`darrow.py close {day}`)")
        if s.get("status") == "skipped" and day_logged(day):
            probs.append(f"slot {s.get('n')} ({day}) is skipped but {day} has logs: a day with any row is open and gets its scene (`plan done {s.get('n')} --force --wrote …`)")
        if s.get("status") in ("planned", "next") and closed:
            probs.append(f"{day} is closed in the Ledger but slot {s.get('n')} is still {s.get('status')}: write its scene, then `plan done {s.get('n')} --wrote {chn}:s{pos.get('next_scene')}`")


# ---------------------------------------------------------------- check & fmt
def cmd_fmt(args):
    for k in STATE_FILES:
        if P[k].exists():
            obj = load_json(P[k])
            text = dumps(obj)
            if P[k].read_text(encoding="utf-8") != text:
                save_json(P[k], obj)
                print(f"rewrote {rel(P[k])}")
    print("canonical")


def cmd_check(args):
    probs, notes = [], []
    for k in STATE_FILES:
        if not P[k].exists():
            probs.append(f"missing {rel(P[k])}")
    if probs:
        print("\n".join(probs))
        sys.exit(1)
    st = State()
    world, bearing, plan, ledger = st.world, st.bearing, st.plan, st.ledger

    # formatting
    for k in STATE_FILES:
        if P[k].read_text(encoding="utf-8") != dumps(load_json(P[k])):
            probs.append(f"{rel(P[k])} is not in canonical format; run `saga.py fmt`")
    if not P["threads"].exists():
        probs.append(f"missing {rel(P['threads'])}")

    # world.json: no GM keys
    for k in ("chapter_plan", "core_beats", "flags", "factions"):
        if k in world:
            probs.append(f"world.json carries GM key {k!r}; it belongs in _gm/plan.json")
    if "summary" in world.get("current_quest", {}):
        probs.append("world.json current_quest.summary is GM-only (plan.json quest_summary)")
    if int(world.get("chapter", -1)) != int(plan.get("position", {}).get("chapter", -2)) or int(world.get("book", -1)) != int(plan.get("position", {}).get("book", -2)):
        probs.append(f"world.json is on Book {world.get('book')} Chapter {world.get('chapter')}, plan.json position on Book {plan.get('position', {}).get('book')} Chapter {plan.get('position', {}).get('chapter')}")
    for cid, c in world.get("companions", {}).items():
        if "approval" not in c:
            probs.append(f"world.json companion {cid} has no approval (companions to come live in plan.json)")

    # ledger
    ids = {}
    for e in ledger.get("entries", []):
        eid = e.get("id", "")
        if not ENTRY_ID_RE.match(eid):
            probs.append(f"ledger entry id {eid!r} malformed")
        ids[eid] = ids.get(eid, 0) + 1
        if not isinstance(e.get("made"), dict) or not {"chapter", "scene", "date"} <= set(e.get("made", {})):
            probs.append(f"ledger {eid}: made must be {{chapter, scene, date}}")
        for it in e.get("due", []):
            did = it.get("id", "")
            ids[did] = ids.get(did, 0) + 1
            if not DUE_ID_RE.match(did) or not did.startswith(eid):
                probs.append(f"ledger {eid}: due id {did!r} malformed")
            if not WHEN_RE.match(str(it.get("when", ""))):
                probs.append(f"ledger {did}: when {it.get('when')!r} not in the grammar")
            at = str(it.get("at", ""))
            if at == "next" or not WHEN_RE.match(at) or (at_status(at, st) == "unknown"):
                probs.append(f"ledger {did}: at {at!r} not resolvable")
            mo = re.match(r"^on:(\w+)$", at)
            if mo and mo.group(1) not in plan.get("flags", {}):
                probs.append(f"ledger {did}: at 'on:{mo.group(1)}' names a flag plan.json does not have")
            if it.get("weight") not in WEIGHTS:
                probs.append(f"ledger {did}: weight {it.get('weight')!r}")
            stt = str(it.get("status", ""))
            if not (stt == "pending" or stt.startswith("fired@") or stt.startswith("void:")):
                probs.append(f"ledger {did}: status {stt!r}")
            if stt.startswith("fired@") and not WHERE_RE.match(stt[6:]):
                probs.append(f"ledger {did}: fired position {stt[6:]!r} malformed")
    for i, n in ids.items():
        if n > 1:
            probs.append(f"ledger id {i} appears {n} times")
    rule_ids = {}
    for r in ledger.get("rules", []):
        rule_ids[r.get("id")] = rule_ids.get(r.get("id"), 0) + 1
        state, detail = rule_state(r, st)
        if state == "MALFORMED":
            probs.append(f"rule {r.get('id')} MALFORMED: {detail}")
        elif state == "UNKNOWN TERM":
            probs.append(f"rule {r.get('id')} UNKNOWN TERM: {detail}")
        if r.get("where") and not WHEN_RE.match(str(r["where"])):
            probs.append(f"rule {r.get('id')}: where {r['where']!r} not in the grammar")
    for i, n in rule_ids.items():
        if n > 1:
            probs.append(f"rule id {i} appears {n} times")

    # approval reconciliation
    base = ledger.get("baseline", {}).get("approval", {})
    for cid, c in world.get("companions", {}).items():
        if cid not in base:
            probs.append(f"ledger baseline has no approval for {cid}")
            continue
        total = base[cid] + sum(int((e.get("now", {}).get("approval") or {}).get(cid, 0)) for e in ledger.get("entries", []))
        if total != c.get("approval"):
            probs.append(f"approval {cid}: baseline {base[cid]} + ledger = {total}, world.json says {c.get('approval')}")

    # bearing
    for aid, ax in bearing.get("axes", {}).items():
        if not isinstance(ax.get("value"), int) or abs(ax["value"]) > bearing.get("range", 10):
            probs.append(f"bearing {aid} value {ax.get('value')!r} out of range")
        for side in ("left", "right"):
            if ax.get(side) not in bearing.get("names", {}):
                probs.append(f"bearing {aid}.{side} {ax.get(side)!r} has no epithet in names")
    snapshot = json.dumps(bearing, sort_keys=True)
    recompute_bearing(bearing)
    if json.dumps(bearing, sort_keys=True) != snapshot:
        probs.append("bearing leans/epithet do not match the axis values; run `saga.py bearing show` after fmt or move with `saga.py bearing`")

    # plan: position
    pos = plan.get("position", {})
    for k in ("book", "chapter", "beat", "next_scene", "stage", "last_written"):
        if k not in pos:
            probs.append(f"plan.position missing {k}")
    if pos.get("stage") not in STAGES:
        probs.append(f"plan.position.stage {pos.get('stage')!r} not in {STAGES}")
    if pos.get("beat") and pos["beat"] not in plan.get("core_beats", {}):
        probs.append(f"plan.position.beat {pos['beat']} not in core_beats")
    for bid, b in plan.get("core_beats", {}).items():
        if b.get("status") not in BEAT_STATUS:
            probs.append(f"core beat {bid} status {b.get('status')!r}")
    for qid, q in plan.get("quests", {}).items():
        if q.get("status") not in QUEST_STATUS:
            probs.append(f"quest {qid} status {q.get('status')!r}")
        if q.get("priority") not in ("required", "optional", "floating"):
            probs.append(f"quest {qid} priority {q.get('priority')!r}")
    for k, v in plan.get("flags", {}).items():
        if not (v is None or isinstance(v, bool)):
            probs.append(f"flag {k} is {v!r}; a flag is true, false or null")
    live = [q for q in plan.get("quests", {}).values() if q.get("status") == "live" and not q.get("standing")]
    if len(live) > 2:
        probs.append(f"{len(live)} quests live; never more than two (a `standing` quest, the Tether, is not counted)")
    for key, r in plan.get("route", {}).items():
        if not re.match(r"^book[1-6]$", key):
            probs.append(f"route key {key!r}")
        if r.get("road") not in (None,) + ROADS:
            probs.append(f"route {key} road {r.get('road')!r}")
    if pos.get("chapter") is not None and int(pos["chapter"]) not in [int(c) for c in plan.get("route", {}).get(f"book{pos.get('book')}", {}).get("chapters", [])]:
        probs.append(f"route.book{pos.get('book')}.chapters does not list the current chapter {pos.get('chapter')}")

    # plan: chapter slots
    ch = plan.get("chapter", {})
    slots = ch.get("slots", [])
    try:
        ws = dt.date.fromisoformat(ch.get("week_start", ""))
    except ValueError:
        ws = None
        probs.append(f"plan.chapter.week_start {ch.get('week_start')!r} is not a date")
    if ws and ws.weekday() != 6:
        probs.append(f"plan.chapter.week_start {ws} is not a Sunday")
    day_slots = [s for s in slots if s.get("day")]
    if len(day_slots) > 7:
        probs.append(f"{len(day_slots)} day slots in the chapter; at most 7")
    ns = [str(s.get("n")) for s in slots]
    if len(set(ns)) != len(ns):
        probs.append("slot numbers repeat")
    micro_days = []
    for s in slots:
        n = s.get("n")
        if s.get("kind") not in SLOT_KINDS:
            probs.append(f"slot {n} kind {s.get('kind')!r} not in {SLOT_KINDS}")
        if s.get("status") not in SLOT_STATUS:
            probs.append(f"slot {n} status {s.get('status')!r}")
        if s.get("day"):
            try:
                day = dt.date.fromisoformat(s["day"])
                if ws and not (ws <= day <= ws + dt.timedelta(6)):
                    probs.append(f"slot {n} day {s['day']} outside the week of {ws}")
            except ValueError:
                probs.append(f"slot {n} day {s['day']!r} is not a date")
        elif s.get("kind") != "interlude":
            probs.append(f"slot {n} has no day (only an interlude may float free of a day)")
        if s.get("kind") == "spine" and s.get("beat") not in plan.get("core_beats", {}):
            probs.append(f"slot {n} spine beat {s.get('beat')!r} not in core_beats")
        if s.get("kind") == "quest" and s.get("quest") not in plan.get("quests", {}):
            probs.append(f"slot {n} quest {s.get('quest')!r} not in quests")
        if s.get("kind") == "quest" and plan.get("quests", {}).get(s.get("quest"), {}).get("standing") and s.get("status") in ("planned", "next"):
            need = int(s.get("stage") or 0)
            have = tether_stage()
            if need > have:
                probs.append(f"slot {n} plans {s.get('quest')} stage {need}, but the engine's Tether stands at {have}; a stage is written only once the Ledger has unlocked it")
        if s.get("float") and s.get("kind") != "quest":
            probs.append(f"slot {n} float is only for quest slots")
        if s.get("status") == "written" and not s.get("wrote"):
            probs.append(f"slot {n} written without wrote")
        m = s.get("micro")
        if m:
            if m.get("axis") not in bearing.get("axes", {}):
                probs.append(f"slot {n} micro axis {m.get('axis')!r} not a bearing axis")
            opts = m.get("options") or []
            if not 2 <= len(opts) <= 3:
                probs.append(f"slot {n} micro needs 2–3 options")
            if m.get("default") not in range(1, len(opts) + 1):
                probs.append(f"slot {n} micro default {m.get('default')!r} not an option number")
            for b in (m.get("bearing") or []):
                if b:
                    for pole, v in b.items():
                        r = pole_axis(bearing, pole)
                        if not r or r[0] != m.get("axis"):
                            probs.append(f"slot {n} micro moves {pole!r}, not a pole of {m.get('axis')}")
                        if abs(int(v)) != 1:
                            probs.append(f"slot {n} micro moves {pole} by {v}; micros move ±1")
            micro_days.append(s)
    if len(slots) >= 2 and sum(1 for s in slots if s.get("kind") == "spine") < 2:
        probs.append("fewer than 2 spine slots in the chapter")
    if sum(1 for s in slots if s.get("kind") == "interlude") > 1:
        probs.append("more than one interlude in the chapter")
    if sum(1 for s in slots if s.get("float")) > 2:
        probs.append("more than two float slots")
    if ws:
        sat = (ws + dt.timedelta(6)).isoformat()
        sat_slot = next((s for s in slots if s.get("day") == sat), None)
        if sat_slot and sat_slot.get("kind") != "spine":
            probs.append(f"Saturday's slot ({sat}) must be spine")
        if len(day_slots) == 7 and not sat_slot:
            probs.append(f"7 day slots but none on Saturday {sat}")
    dated = sorted([s for s in micro_days if s.get("day")], key=lambda s: s["day"])
    for a_, b_ in zip(dated, dated[1:]):
        if (dt.date.fromisoformat(b_["day"]) - dt.date.fromisoformat(a_["day"])).days < 2:
            probs.append(f"micros in adjacent slots {a_['n']} and {b_['n']}")
    axes_touched = {s["micro"]["axis"] for s in micro_days if s.get("micro")}
    if len(micro_days) >= 2 and len(axes_touched) < 2:
        probs.append("the chapter's micros touch only one axis; plan ≥ 2")
    om = plan.get("open_micro")
    if om and not any(str(s.get("n")) == str(om.get("slot")) for s in slots):
        probs.append(f"open_micro points at slot {om.get('slot')} which is not in the chapter")
    if om and ch.get("number") is not None and int(om.get("chapter", ch.get("number"))) != int(ch.get("number")):
        probs.append(f"open_micro belongs to chapter {om.get('chapter')}, the plan is on chapter {ch.get('number')}; it must be closed before the chapter changes")
    cl = ch.get("climax") or {}
    if cl.get("default") is not None and cl.get("default") not in range(1, len(cl.get("options") or []) + 1):
        probs.append(f"chapter.climax.default {cl.get('default')!r} is not an option number (1–{len(cl.get('options') or [])})")
    if ws:
        sat_slot = next((s for s in slots if s.get("day") == (ws + dt.timedelta(6)).isoformat()), None)
        if sat_slot and sat_slot.get("status") == "skipped":
            notes.append("Saturday skipped: its spine content folds into the climax")
    quest_counts = {}
    for s in slots:
        if s.get("kind") == "quest" and s.get("quest"):
            quest_counts[s["quest"]] = quest_counts.get(s["quest"], 0) + 1
    for qid, n in quest_counts.items():
        if n > 2:
            probs.append(f"quest {qid} appears in {n} slots; at most two stages of one quest per chapter")
    if int(pos.get("chapter") or 0) >= 2 and slots and not quest_counts and any(q.get("status") == "available" for q in plan.get("quests", {}).values()):
        probs.append("chapter has no quest slot while quests are available (design §5.2)")

    # the chapter file, the slots, world.json's scenes[] and the Ledger's closed days must tell one story
    reconcile_chapter(st, probs)

    # arc ids
    ids_in_arc = arc_ids()
    if ids_in_arc:
        wanted = set(plan.get("core_beats", {})) | set(plan.get("quests", {}))
        for k in plan.get("route", {}):
            n = k[4:]
            if plan["route"][k].get("road"):
                wanted.add(f"t{n}.{plan['route'][k]['road']}")
        for i in sorted(wanted):
            if re.match(r"^t\d$", i):
                if not any(f"{i}.{road}" in ids_in_arc for road in ROADS) and i not in ids_in_arc:
                    probs.append(f"{i} has no `## {i}.high/main/low` headings in arc.md")
            elif i not in ids_in_arc:
                probs.append(f"{i} has no `## {i} — …` heading in arc.md")
    else:
        print("note: arc.md has no id headings yet (old layout); id validation skipped")

    # world.json choices
    ledger_ids = {e["id"] for e in ledger.get("entries", [])}
    scene_keys = {str(s.get("scene")) for s in world.get("scenes", [])}
    for i, c in enumerate(world.get("choices", [])):
        need = {"chapter", "scene", "kind", "option", "text", "date", "ledger", "by"}
        missing = need - set(c)
        if missing:
            probs.append(f"world.json choices[{i}] missing {sorted(missing)}")
        if c.get("kind") not in ("climax", "micro"):
            probs.append(f"world.json choices[{i}] kind {c.get('kind')!r}")
        if c.get("by") not in ("darrow", "bearing"):
            probs.append(f"world.json choices[{i}] by {c.get('by')!r}")
        if c.get("ledger") not in ledger_ids:
            probs.append(f"world.json choices[{i}] ledger {c.get('ledger')!r} has no ledger entry")
        if c.get("kind") == "micro" and str(c.get("scene")) not in scene_keys and int(c.get("chapter", -1)) == int(world.get("chapter", -2)):
            probs.append(f"world.json choices[{i}] scene {c.get('scene')!r} is not a scene key of chapter {world.get('chapter')}")
        if not isinstance(c.get("chapter"), int):
            probs.append(f"world.json choices[{i}] chapter must be an int")

    for n in notes:
        print(f"note: {n}")
    if probs:
        print("\n".join(f"✗ {p}" for p in probs))
        sys.exit(1)
    print("ok: ledger, bearing, plan, world.json choices and formatting all check out")


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("now")
    s = sub.add_parser("due"); s.add_argument("--at"); s.add_argument("--all", action="store_true")
    sub.add_parser("check")
    sub.add_parser("fmt")
    sub.add_parser("archive")
    s = sub.add_parser("add"); s.add_argument("entry"); s.add_argument("--witnessed"); s.add_argument("--pending", action="store_true"); s.add_argument("--dry-run", action="store_true")
    s = sub.add_parser("fire"); s.add_argument("id"); s.add_argument("--where", required=True)
    s = sub.add_parser("void"); s.add_argument("id"); s.add_argument("--why", required=True)
    s = sub.add_parser("bearing"); s.add_argument("pole", help="a pole word, or `show`"); s.add_argument("n", nargs="?", type=int); s.add_argument("--why"); s.add_argument("--force", action="store_true", help="allow a move beyond ±4")
    s = sub.add_parser("route"); s.add_argument("action", choices=["decide", "show"]); s.add_argument("--book", type=int); s.add_argument("--road", choices=ROADS); s.add_argument("--why")
    s = sub.add_parser("plan"); ps = s.add_subparsers(dest="action", required=True)
    x = ps.add_parser("next"); x.add_argument("--date"); x.add_argument("--full", action="store_true")
    x = ps.add_parser("done"); x.add_argument("n"); x.add_argument("--wrote"); x.add_argument("--skipped", action="store_true"); x.add_argument("--force", action="store_true", help="redo a slot already written or skipped")
    x = ps.add_parser("slot"); x.add_argument("n"); x.add_argument("kv", nargs="+", help="key=value; micro as JSON"); x.add_argument("--force", action="store_true", help="edit a slot already written or skipped")
    x = ps.add_parser("micro"); x.add_argument("sub", choices=["open", "close"]); x.add_argument("n", nargs="?"); x.add_argument("--option", type=int); x.add_argument("--by", choices=["darrow", "bearing"], default="darrow")
    x = ps.add_parser("climax")
    x = ps.add_parser("chapter"); x.add_argument("sub", choices=["open", "template"]); x.add_argument("--number", type=int); x.add_argument("json", nargs="?"); x.add_argument("--week_start", help="template: the Sunday the chapter covers"); x.add_argument("--force", action="store_true", help="open a chapter out of sequence")
    x = ps.add_parser("book"); x.add_argument("sub", choices=["open"]); x.add_argument("n", type=int)
    x = ps.add_parser("quest"); x.add_argument("id"); x.add_argument("kv", nargs="+")
    x = ps.add_parser("beat"); x.add_argument("id"); x.add_argument("kv", nargs="+")
    x = ps.add_parser("flag"); x.add_argument("kv", nargs="+"); x.add_argument("--new", action="store_true", help="add a flag the plan does not have yet")
    x = ps.add_parser("temptation"); x.add_argument("sub", choices=["add"]); x.add_argument("text")
    x = ps.add_parser("companion"); x.add_argument("sub", choices=["arrive"]); x.add_argument("id")
    x = ps.add_parser("set"); x.add_argument("kv", nargs="+")
    s = sub.add_parser("arc"); s.add_argument("id")
    args = ap.parse_args()
    if args.cmd == "route" and args.action == "decide" and not args.book:
        die("route decide needs --book N")
    {
        "now": cmd_now, "due": cmd_due, "check": cmd_check, "fmt": cmd_fmt, "archive": cmd_archive,
        "add": cmd_add, "fire": cmd_fire, "void": cmd_void, "bearing": cmd_bearing, "route": cmd_route,
        "plan": cmd_plan, "arc": lambda a: print_arc(a.id),
    }[args.cmd](args)


if __name__ == "__main__":
    main()
