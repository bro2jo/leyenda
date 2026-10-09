#!/usr/bin/env python3
"""THE UNKNEELING - the saga engine (GM side).

Keeps the story's state machines so the writer never re-derives them from memory:
the consequence ledger (saga/state/_gm/consequences.json), Darrow's Bearing
(saga/state/bearing.json), the chapter plan and position (saga/state/_gm/plan.json),
roads per Book, and sections of the GM arc (saga/bible/_gm/arc.md). Standard library only.
Real numbers never move anything here; only choices and chapter tiers do.

Commands (run from the repo root):
  now                                   the digest: position, road, next slot, quests, micro, bearing, due items, rules (<= 30 lines)
  due [--at ch02:s1|book2|...] [--all]  pending ledger items that match a target (--all: every pending item)
  check                                 validate ledger, plan, bearing, world.json choices, arc ids, formatting; exit 1 on problems
  fmt                                   rewrite the four state JSON files canonically
  add 'JSON' [--witnessed a,b] [--pending] [--dry-run]   append a ledger entry, resolve `at`, apply its `now` deltas
  fire ID --where ch03:s2               mark a due item fired there
  void ID --why TEXT                    mark a due item void
  bearing POLE N --why ID | bearing show
  route decide --book N [--road low|main|high --why TEXT] | route show
  plan next [--date D] [--full]         the slot for a day (default: the first next/planned slot); --full adds the arc section
  plan done N --wrote ch01:s3 | --skipped
  plan micro open N | plan micro close [--option K --by darrow|bearing]
  plan chapter open --number N 'JSON'
  plan quest ID k=v ... | plan beat ID status=... | plan flag k=v | plan temptation add TEXT
  plan companion arrive ID | plan set key=value
  arc ID                                print one section of _gm/arc.md (<= 40 lines)
  archive                               move spent entries older than two Books to consequences_archive.json

`when` / `at` grammar (ledger due items):
  next            the next scene (resolved by `add` to chNN:sN)
  chNN            anywhere in chapter NN            chNN:sN      scene N of chapter NN
  chNN:climax     chapter NN's climax or choice     bookN        anywhere in Book N
  bookN:beatK     while core beat bN.K is in_progress
  transitionN     Book N's transition chapter       finale       = book6:climax
  on:<flag>       when plan.json flags.<flag> becomes true
  any             standing: shown until fired or void

`if` grammar (ledger rules):
  operators  && || ! ( )  >= <= > < == !=   numbers  "strings"  true false
  terms      approval.<id>  bearing.<pole>  flags.<name>  route.bookN  factions.<id>
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

WHEN_RE = re.compile(r"^(next|ch\d{2}|ch\d{2}:s\d+|ch\d{2}:climax|book\d|book\d:beat\d+|transition\d|finale|on:[a-z][a-z0-9_]*|any)$")
WHERE_RE = re.compile(r"^(ch\d{2}(:(s\d+|climax|interlude(-\d+)?|choice|transition))?|book\d(:climax|:beat\d+)?)$")
ENTRY_ID_RE = re.compile(r"^c(\d{2})\.(\d+)$")
DUE_ID_RE = re.compile(r"^c(\d{2})\.(\d+)([a-z])$")
WROTE_RE = re.compile(r"^ch(\d{2}):(s(\d+)|interlude(-\d+)?|climax|transition)$")


# ---------------------------------------------------------------- io
def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def dumps(obj):
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


def save_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(dumps(obj))


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


def move_bearing(st, pole, n, why, quiet=False):
    """Move toward `pole` by n (n > 0; a negative n moves away). Returns (axis, old, new)."""
    b = st.bearing
    r = pole_axis(b, pole)
    if not r:
        die(f"unknown pole {pole!r}; poles: " + ", ".join(w for ax in b["axes"].values() for w in (ax["left"], ax["right"])))
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
    """Static target for a `when`: `next` becomes ch<chapter>:s<next_scene>; everything else is itself."""
    if when == "next":
        pos = plan["position"]
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
            return "future"
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
RULE_NODES = (ast.Expression, ast.BoolOp, ast.And, ast.Or, ast.UnaryOp, ast.Not, ast.Compare,
              ast.Attribute, ast.Name, ast.Constant, ast.Load,
              ast.Gt, ast.GtE, ast.Lt, ast.LtE, ast.Eq, ast.NotEq)
KNOWN_ROOTS = ("approval", "bearing", "flags", "route", "factions", "temptation", "quests")


def rule_source(expr):
    s = str(expr)
    s = s.replace("&&", " and ").replace("||", " or ")
    s = re.sub(r"!(?!=)", " not ", s)
    s = re.sub(r"\btrue\b", "True", s)
    s = re.sub(r"\bfalse\b", "False", s)
    return s


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
    return False, 0


def rule_terms(tree):
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            parts = dotted(node)
            if parts and isinstance(node, ast.Attribute):
                out.append(parts)
    # keep only maximal chains (an Attribute's inner Attribute is also walked)
    chains = {".".join(p) for p in out}
    return [p for p in out if not any(c != ".".join(p) and c.startswith(".".join(p) + ".") for c in chains)]


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
    """Numeric terms within `within` of their threshold, for an unarmed rule."""
    tree = parse_rule(rule.get("if", ""))
    if tree is None:
        return []
    near = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Compare) or len(node.comparators) != 1:
            continue
        a, b = node.left, node.comparators[0]
        if isinstance(a, ast.Constant):
            a, b = b, a
        if isinstance(a, ast.Attribute) and isinstance(b, ast.Constant) and isinstance(b.value, (int, float)) and not isinstance(b.value, bool):
            parts = dotted(a)
            if not parts:
                continue
            known, val = term_lookup(parts, st)
            if known and isinstance(val, (int, float)) and not isinstance(val, bool) and abs(val - b.value) <= within:
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
ID_RE = re.compile(r"^(b\d\.\d+|q\d\.[a-z0-9_]+|t\d(\.(high|main|low))?|book\d\.question|pacing|truths|motifs|beliefs|temptation|flags)\b")


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
    rows = [r for r in read_csv(P["daily"]) if r.get("date") == day]
    if not rows:
        return "missed (no daily row)"
    r = rows[0]
    nut = next((n for n in read_csv(P["nutrition"]) if n.get("date") == day), {})
    try:
        t = load_json(P["config"])["nutrition_targets"]
        kcal, prot = float(nut.get("kcal") or 0), float(nut.get("protein_g") or 0)
        fuel_ok = kcal >= 0.9 * t["kcal"] and prot >= 0.9 * t["protein_g"]
    except Exception:
        fuel_ok = False
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
    state = "closed" if yes(r.get("closed")) else "open"
    return f"{c} ({state})"


# ---------------------------------------------------------------- plan helpers
def slot_by_n(plan, n):
    for s in plan["chapter"].get("slots", []):
        if str(s.get("n")) == str(n):
            return s
    die(f"no slot {n} in chapter {plan['chapter'].get('number')}")


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


def print_slot(s, full=False):
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
        print(f"  world move owed: {s['world_move']}")
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
    q = plan.get("quests", {})
    live = [f"{k} (stage {v.get('stage')})" for k, v in q.items() if v.get("status") == "live"]
    avail = [f"{k} ({v.get('priority')})" for k, v in q.items() if v.get("status") == "available"]
    lines.append("Quests live: " + (", ".join(live) or "none"))
    lines.append("Quests available: " + short(", ".join(avail) or "none", 160))
    om = plan.get("open_micro")
    if om:
        lines.append(f"Open micro (slot {om.get('slot')}, {om.get('axis')}): {om.get('ask')}")
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
    if args.all:
        rows = items
    elif args.at:
        rows = [(e, it) for e, it in items if it.get("at") == args.at or it.get("at") == "any"]
    else:
        rows = [(e, it) for e, it in items if at_status(it.get("at", ""), st) in ("due", "overdue")]
    if not rows:
        print("nothing pending" + (f" at {args.at}" if args.at else ""))
        return
    for e, it in rows:
        tag = at_status(it.get("at", ""), st).upper()
        print(f"{it['id']} [{it.get('weight')}] when={it.get('when')} at={it.get('at')} {tag} · from {e['id']} ({e['made'].get('date')}: {short(e.get('chose'), 60)})")
        print(f"  {it.get('what')}")


# ---------------------------------------------------------------- commands: ledger writes
def validate_entry(entry, ledger, plan):
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
    for i, it in enumerate(entry.setdefault("due", [])):
        did = it.get("id", "")
        if not DUE_ID_RE.match(did) or not did.startswith(eid):
            probs.append(f"due[{i}].id {did!r} must be {eid} plus a letter")
        if did in ids:
            probs.append(f"due id {did} already in the ledger")
        if not WHEN_RE.match(str(it.get("when", ""))):
            probs.append(f"due[{i}].when {it.get('when')!r} not in the grammar (see --help)")
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


def cmd_add(args):
    st = State()
    try:
        entry = json.loads(args.entry)
    except json.JSONDecodeError as e:
        die(f"entry is not valid JSON: {e}")
    ledger, plan, world = st.ledger, st.plan, st.world
    probs = validate_entry(entry, ledger, plan)
    if probs:
        die("refusing the entry:\n  " + "\n  ".join(probs))
    now = entry["now"]
    witnessed = [w.strip() for w in (args.witnessed or "").split(",") if w.strip()]
    # companion-preference approval from bearing deltas
    pref_delta = {}
    for cid in witnessed:
        prefs = [p.lower() for p in plan.get("companions", {}).get(cid, {}).get("prefers", [])]
        if cid not in plan.get("companions", {}):
            die(f"--witnessed {cid}: not in plan.json companions")
        for pole, n in (now.get("bearing") or {}).items():
            r = pole_axis(st.bearing, pole)
            if not r:
                die(f"now.bearing: unknown pole {pole!r}")
            aid, sign = r
            ax = st.bearing["axes"][aid]
            opposite = ax["left"].lower() if sign > 0 else ax["right"].lower()
            toward = n > 0
            if pole.lower() in prefs:
                pref_delta[cid] = pref_delta.get(cid, 0) + (2 if toward else -2)
            elif opposite in prefs:
                pref_delta[cid] = pref_delta.get(cid, 0) + (-2 if toward else 2)
    if pref_delta:
        appr = now.setdefault("approval", {})
        for cid, dlt in pref_delta.items():
            appr[cid] = appr.get(cid, 0) + dlt
            print(f"witnessed {cid}: preference {dlt:+d} folded into now.approval")
    # apply approval
    for cid, dlt in (now.get("approval") or {}).items():
        comp = world.get("companions", {})
        if cid in comp:
            old = comp[cid].get("approval", 0)
            comp[cid]["approval"] = clamp(old + int(dlt), -100, 100)
            print(f"approval {cid}: {old} → {comp[cid]['approval']}")
            st.touch("world")
        elif args.pending and cid in plan.get("companions_to_come", {}):
            c = plan["companions_to_come"][cid]
            old = c.get("approval_pending", 0)
            c["approval_pending"] = old + int(dlt)
            print(f"approval_pending {cid}: {old} → {c['approval_pending']}")
            st.touch("plan")
        else:
            die(f"approval.{cid}: not a companion in world.json (use --pending for companions_to_come)")
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
        print(f"due {it['id']} when={it['when']} → at={it['at']} [{it['weight']}]")
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
        die("usage: bearing <pole> <n> --why <ledger id>")
    move_bearing(st, args.pole, args.n, args.why)
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
            return
        print_slot(s, full=args.full)
        return
    if a == "done":
        s = slot_by_n(plan, args.n)
        if args.skipped:
            s["status"] = "skipped"
            moves = plan["chapter"].setdefault("world_moves", [])
            if moves:
                s["world_move"] = moves.pop(0)
                print(f"slot {s['n']} skipped; the next scene opens with one off-page world move: {s['world_move']}")
            else:
                print(f"slot {s['n']} skipped; no world_moves left in the chapter, invent one off-page move")
            if s.get("kind") == "spine":
                print("a skipped spine slot's content folds into the next spine slot or the climax")
        else:
            if not args.wrote or not WROTE_RE.match(args.wrote):
                die("--wrote must look like ch01:s3 or ch01:interlude")
            m = WROTE_RE.match(args.wrote)
            s["status"] = "written"
            s["wrote"] = args.wrote
            plan["position"]["last_written"] = args.wrote
            if m.group(3):
                plan["position"]["next_scene"] = int(m.group(3)) + 1
            if s.get("kind") == "quest" and s.get("quest"):
                q = plan.setdefault("quests", {}).setdefault(s["quest"], {"status": "available", "stage": 0, "priority": "optional"})
                q["stage"] = int(s.get("stage") or q.get("stage", 0) + 1)
                total = arc_quest_stage_count(s["quest"])
                q["status"] = "done" if total and q["stage"] >= total else "live"
                print(f"quest {s['quest']}: stage {q['stage']}" + (f"/{total}" if total else "") + f" · {q['status']}")
            if s.get("kind") == "spine" and s.get("beat"):
                b = plan.setdefault("core_beats", {}).setdefault(s["beat"], {"title": s["beat"], "status": "planned"})
                if b.get("status") == "planned":
                    b["status"] = "in_progress"
                plan["position"]["beat"] = s["beat"]
            print(f"slot {s['n']} written as {args.wrote} · next scene {plan['position']['next_scene']}")
        nxt = next((x for x in sorted(plan["chapter"]["slots"], key=lambda x: float(x.get("n", 0))) if x.get("status") == "planned"), None)
        if nxt and not any(x.get("status") == "next" for x in plan["chapter"]["slots"]):
            nxt["status"] = "next"
            print(f"next: {slot_label(nxt)}")
        st.touch("plan")
        st.save()
        return
    if a == "micro":
        if args.sub == "open":
            s = slot_by_n(plan, args.n)
            if not s.get("micro"):
                die(f"slot {args.n} has no micro planned")
            if plan.get("open_micro"):
                die(f"a micro is already open (slot {plan['open_micro'].get('slot')}); close it first (it resolves to its default if unanswered)")
            m = dict(s["micro"])
            plan["open_micro"] = {"slot": s["n"], "scene": str(plan["position"]["next_scene"]), "opened": today_local().isoformat(), **m}
            print(f"micro open from slot {s['n']} ({m.get('axis')}): {m.get('ask')} · default {m.get('default')}")
        else:
            om = plan.get("open_micro")
            if not om:
                die("no micro is open")
            s = next((x for x in plan["chapter"]["slots"] if str(x.get("n")) == str(om.get("slot"))), None)
            if s is not None and s.get("micro") is not None:
                s["micro"]["answer"] = {"option": args.option, "by": args.by}
            plan["open_micro"] = None
            print(f"micro from slot {om.get('slot')} closed" + (f": option {args.option} by {args.by}" if args.option else ""))
        st.touch("plan")
        st.save()
        return
    if a == "chapter":
        try:
            ch = json.loads(args.json)
        except json.JSONDecodeError as e:
            die(f"chapter JSON invalid: {e}")
        ch["number"] = int(args.number)
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
        plan["chapter"] = ordered
        book = plan["position"]["book"]
        r = plan.setdefault("route", {}).setdefault(f"book{book}", {"chapters": [], "road": None, "override": None, "transition_chapter": None})
        if int(args.number) not in [int(c) for c in r["chapters"]]:
            r["chapters"].append(int(args.number))
        plan["position"].update({"chapter": int(args.number), "next_scene": 1, "stage": "scene"})
        st.touch("plan")
        st.save()
        print(f"chapter {args.number} opened (week of {ch['week_start']}, {len(ordered['slots'])} slots); run `saga.py check`")
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
        for k, v in parse_kv(args.kv).items():
            old = plan.setdefault("flags", {}).get(k)
            plan["flags"][k] = v
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
        world.setdefault("companions", {})[args.id] = {"approval": approval, "present": True, "note": c.get("note", "")}
        ledger = st.ledger
        summed = sum(int((e.get("now", {}).get("approval") or {}).get(args.id, 0)) for e in ledger["entries"])
        ledger["baseline"]["approval"][args.id] = approval - summed
        plan.setdefault("companions", {}).setdefault(args.id, {"prefers": c.get("prefers", [])})
        del plan["companions_to_come"][args.id]
        st.touch("plan", "world", "ledger")
        st.save()
        print(f"{args.id} arrived: approval {approval}, present; baseline set to {approval - summed}. Give them a saga/characters file and an Edit to the note.")
        return
    if a == "set":
        pos = plan["position"]
        for k, v in parse_kv(args.kv).items():
            if k not in pos:
                die(f"position has no field {k}; fields: {', '.join(pos)}")
            if k == "stage" and v not in STAGES:
                die(f"stage must be one of {STAGES}")
            print(f"position.{k}: {pos[k]} → {v}")
            pos[k] = v
        st.touch("plan")
        st.save()
        return
    die(f"unknown plan action {a}")


# ---------------------------------------------------------------- check & fmt
def cmd_fmt(args):
    for k in STATE_FILES:
        if P[k].exists():
            obj = load_json(P[k])
            text = dumps(obj)
            if P[k].read_text(encoding="utf-8") != text:
                P[k].write_text(text, encoding="utf-8")
                print(f"rewrote {rel(P[k])}")
    print("canonical")


def cmd_check(args):
    probs = []
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
        if r.get("where") and not (WHEN_RE.match(str(r["where"])) or r["where"] == "book6:climax"):
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
    live = [q for q in plan.get("quests", {}).values() if q.get("status") == "live"]
    if len(live) > 2:
        probs.append(f"{len(live)} quests live; never more than two")
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
    s = sub.add_parser("bearing"); s.add_argument("pole", help="a pole word, or `show`"); s.add_argument("n", nargs="?", type=int); s.add_argument("--why")
    s = sub.add_parser("route"); s.add_argument("action", choices=["decide", "show"]); s.add_argument("--book", type=int); s.add_argument("--road", choices=ROADS); s.add_argument("--why")
    s = sub.add_parser("plan"); ps = s.add_subparsers(dest="action", required=True)
    x = ps.add_parser("next"); x.add_argument("--date"); x.add_argument("--full", action="store_true")
    x = ps.add_parser("done"); x.add_argument("n"); x.add_argument("--wrote"); x.add_argument("--skipped", action="store_true")
    x = ps.add_parser("micro"); x.add_argument("sub", choices=["open", "close"]); x.add_argument("n", nargs="?"); x.add_argument("--option", type=int); x.add_argument("--by", choices=["darrow", "bearing"], default="darrow")
    x = ps.add_parser("chapter"); x.add_argument("sub", choices=["open"]); x.add_argument("--number", required=True, type=int); x.add_argument("json")
    x = ps.add_parser("quest"); x.add_argument("id"); x.add_argument("kv", nargs="+")
    x = ps.add_parser("beat"); x.add_argument("id"); x.add_argument("kv", nargs="+")
    x = ps.add_parser("flag"); x.add_argument("kv", nargs="+")
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
