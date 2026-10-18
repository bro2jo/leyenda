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
  fire ID --where ch03:s2               mark a due item fired there; a rule id (r.…) marks the rule honoured there (once per Book for a standing rule)
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
  plan slot N key=value ...             edit a planned slot in place (plan, turn, kind, beat, quest, stage, last, pov, micro, float, day);
                                        micro is passed as JSON (micro='{"axis":…,"ask":…,"options":[…],"bearing":[…],"default":1}');
                                        a written/skipped slot is refused without --force
  plan climax                           the chapter's question, climax plan, checks, options, default and the world moves left; the open climax choice first
  plan choice open 'JSON' | show | close [--option K] [--by darrow|bearing]
                                        the climax choice as the page offers it ({"ask", "options", "default"}): it stays open across the chapter open,
                                        so its default is its own; `saga.py choose` answers it (close is its bookkeeping half)
  plan chapter cutaway                  a week with nothing logged whose chapter was already planned: its slots cleared, world moves kept (one interlude, no climax)
  plan chapter template --week_start YYYY-MM-DD
                                        print a canonical skeleton for the next chapter (7 dated slots, spine on Sunday and Saturday, two
                                        float quest placeholders, each with an empty plan and turn, world_moves, climax); fill it in a scratch file
                                        and pass it to `plan chapter open` (it warns about slots whose turn is still empty)
  plan chapter open --number N 'JSON'   N must follow the current chapter (--force otherwise); refused while a micro is open; keeps climax.default; warns about the outgoing chapter's unwritten slots
                                        and carries its still-owed world moves to the front of the new chapter's world_moves
  plan book open N                      enter Book N: position.book/beat, route.bookN, core beats and quests seeded from arc.md, Book N-1's planned beats folded,
                                        its unrun optional quests dropped; required ones are kept available and warned (re-skin on the road or drop by hand)
  plan quest ID k=v ... | plan beat ID status=... | plan flag [--new] k=v (true/false/null; --new to add a flag) | plan temptation add TEXT
  plan companion arrive ID              move a companion from companions_to_come to world.json (keeps bond)
  plan set key=value                    stage=choice only follows climax; stage=climax pays off owed world moves;
                                        rank_on_page=<rank> once a scene has carried a rank crossing (`now` prints RANK OWED until then)
  challenge N success|fail|show|void    a slot's challenge (design §5.6): move a counter after each roll; it resolves when progress or strain fills
  invite N take|pass|show               a slot's invitation: taken when he answers in voice (a Between), passed at the next close if he has not
  plan invite_rule WHO EXPR             a person's standing condition for coming to Darrow at all (rae: tether.stage >= 1); `check` refuses an invite while it is not met
  plan quest ID gate='beats.b1_1.status == "done"'   a quest's gate in the rule grammar (a beat id with its dot as an underscore; also quests.ID.status, flags.x, approval.x, tether.stage):
                                        `check` refuses a planned slot of the quest while it is not met; `plan next` prints it
  project ID show | work --where chNN:between-K --what TEXT
                                        the Book's project quest: note a hand laid on it between stages; its trace lives in world.json → projects[]
  due --later                           callbacks: due items with when=later; each may carry fits (the rule grammar, with present.<id> and place.<id>),
                                        priority 1-3, valid_until (it lapses after that position, at its if_void cost); the brief lists the ones that
                                        fit the block, most worth first; a record counts the ones it could have paid and did not (offered)
  arc ID                                print one section of _gm/arc.md (<= 40 lines)
  lore | lore ID | lore grep WORD | lore pick saying|verse|maxim|rhyme [--all] | lore spoke ID --where chNN:sK
                                        the Annals (_gm/lore.md): the index, one entry, a search, a line for a glimpse, mark an entry spoken
  names [--all]                         capitalised names in the current chapter (--all: every chapter) that no registry knows:
                                        codex, cast, places, factions, the Annals, the game's own words; `check` notes them too
  archive                               move spent entries older than two Books to consequences_archive.json

The records (engine/records.py; design.md §11): the story is kept as one event per block, and every page is rebuilt from them.
  brief [--date D | --between --with WHO | --climax | --choice | --chapter] [--size]
                                        what the next block must carry (the slot, what is owed), its continuity, what it may use (the people,
                                        the threads, the Annals, callbacks, the arc), the format, and the record skeleton to send back
  record 'JSON' [--force] [--slot N] [--allow-names A,B]
                                        one block of the page recorded: validated against the heading, the registries and the plan; the event
                                        and the GM note written; the slot done, a micro or the climax choice opened, due items fired, the
                                        Annals marked spoken; world.json, the character files, the Codex, the threads and NOW.md rebuilt; check
  choose --option K [--by darrow|bearing] [--which micro|climax] [--text …] 'ENTRY' [--witnessed a,b] [--pending]
                                        his answer in one step: the ledger entry, the choices[] row, the choice closed (a climax's `### Choice` block follows);
                                        an option tagged *[Inspiration]* spends one (refused while he holds none; never the default); the entry keeps
                                        the options he declined, and the brief names the last two
  project [--dry]                       rebuild every projection from the records (or list what would change)
  history [--person ID] [--thread N] [--place ID] [--chapter N] [--last N] [--gm]   the records as a timeline
  threads [--id N] [--all] | --id N --set k=v … | --new 'JSON'   the threads as data (GM)
  glimpse add --kind K "TEXT" | glimpse show [--n N]   the line of the House after a log reply (rotated kinds, the last 20 kept)

The tales (design.md §12): the past, told a piece at a time, paid for by the works (real/projects.json; `darrow.py project`).
  tale bind PROJECT [--tale tale.id] [--force]   bind the live project to a plan of _gm/tales.md with as many pieces as the project has
                                        tasks (the first unbound one that fits, or --tale): starts saga/chronicle/tales/NN-slug.md, keeps the
                                        binding in the plan (plan.json → tales[])
  tale list | tale next                 every bound tale (pieces told, owed, done) and the plans still unbound · the piece owed now
  brief --tale                          the piece owed (a task reported, its piece not yet told): the tale's plan, this piece's, what it may
                                        plant and must never say, the keepsake on the last piece, the people, the record skeleton
  record '{"key": "taleNN:pK", …}'      a piece recorded: its event (events/taleNN.jsonl) and note; people, facts, codex, threads, lore; the
                                        keepsake on the last piece; the projections rebuilt (a person's appearances and facts, world.json →
                                        keepsakes[] and tales[]); never the plan's position, approval or the ledger

`when` / `at` grammar (ledger due items):
  next            the next scene (resolved by `add` to chNN:sN; at the climax, choice or transition stage: the next chapter's s1)
  later           a callback: never due or overdue, listed by `due --later`, fired wherever it fits (one per scene at most)
  chNN            anywhere in chapter NN            chNN:sN      scene N of chapter NN
  chNN:climax     chapter NN's climax or choice     bookN        anywhere in Book N
  bookN:beatK     while core beat bN.K is in_progress   bookN:climax   Book N's last climax (what `finale` resolves to)
  transitionN     Book N's transition chapter       finale       = the saga's last Book's climax (plan.json → saga.finale_book, 6 unless a sequel moves it)
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
import random
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import records as R  # the events store and the projections (engine/records.py)

ROOT = Path(__file__).resolve().parent.parent
P = {
    "world": ROOT / "saga/state/world.json",
    "bearing": ROOT / "saga/state/bearing.json",
    "plan": ROOT / "saga/state/_gm/plan.json",
    "ledger": ROOT / "saga/state/_gm/consequences.json",
    "archive": ROOT / "saga/state/_gm/consequences_archive.json",
    "arc": ROOT / "saga/bible/_gm/arc.md",
    "threads": ROOT / "saga/state/_gm/threads.json",
    "codex_json": ROOT / "saga/state/codex.json",
    "events": ROOT / "saga/state/events",
    "notes": ROOT / "saga/state/_gm/notes",
    "lore": ROOT / "saga/bible/_gm/lore.md",
    "tales_plan": ROOT / "saga/bible/_gm/tales.md",
    "tales_dir": ROOT / "saga/chronicle/tales",
    "projects": ROOT / "real/projects.json",
    "codex": ROOT / "saga/state/codex.md",
    "cast": ROOT / "saga/bible/cast.md",
    "characters": ROOT / "saga/characters",
    "places": ROOT / "saga/state/places.json",
    "factions": ROOT / "saga/state/factions.json",
    "rules": ROOT / "engine/rules.json",
    "chronicle": ROOT / "saga/chronicle",
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
STATS = ("might", "vigor", "finesse", "resolve")
# devices (design §5.6): what a slot may carry beside its content; the pacing rule lives in `check`
DEVICE_KINDS = ("challenge", "project", "invite")
INVITE_KINDS = ("favour", "diversion", "opinion", "problem")
INVITE_STATUS = ("waiting", "taken", "passed", "void")
CHALLENGE_STATUS = ("open", "won", "lost", "void")
CALLBACK_CAP = 10  # due items with when=later alive at once (they fit, count their offers and lapse: design §5.6)
VALID_UNTIL_RE = re.compile(r"^(ch\d{2,}(:(s\d+|climax))?|book\d+(:climax)?|transition\d+|finale)$")  # a callback's valid_until: the position it lapses after
QUEST_STATUS = ("available", "live", "done", "dropped")
BEAT_STATUS = ("planned", "in_progress", "done", "folded")
ROADS = ("low", "main", "high")
NOW_CAP = 30
DEFAULT_FINALE_BOOK = 6  # plan.json → saga.finale_book overrides it: a sequel moves the finale, the grammar's `finale` follows


def roman(n):
    """Roman numerals for any Book or Knot number (a sequel is not stopped at VII)."""
    n = int(n)
    if n <= 0:
        return str(n)
    out = ""
    for v, s in ((1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"), (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")):
        while n >= v:
            out += s
            n -= v
    return out


class _Roman:
    def __getitem__(self, n):
        return roman(n)


ROMAN = _Roman()

# ids: chapters are two digits or more (ch02 … ch100), Books one digit or more, so nothing here ends at Book VI
WHEN_RE = re.compile(r"^(next|later|ch\d{2,}|ch\d{2,}:s\d+|ch\d{2,}:climax|book\d+|book\d+:beat\d+|book\d+:climax|transition\d+|finale|on:[a-z][a-z0-9_]*|any)$")
WHERE_RE = re.compile(r"^(ch\d{2,}(:(s\d+|climax|interlude(-\d+)?|choice|transition|between-\d+))?|book\d+(:climax|:beat\d+)?)$")
ENTRY_ID_RE = re.compile(r"^c(\d{2,})\.(\d+)$")
DUE_ID_RE = re.compile(r"^c(\d{2,})\.(\d+)([a-z])$")
WROTE_RE = re.compile(r"^ch(\d{2,}):(s(\d+)|interlude(-\d+)?|climax|transition)$")
BLOCK_KEY_RE = re.compile(r"^ch(\d{2,}):(s(\d+)|interlude(-\d+)?|between-(\d+)|climax|choice|[IVX]+)$")  # every block the page can hold


def finale_book(plan):
    return int((plan.get("saga") or {}).get("finale_book") or DEFAULT_FINALE_BOOK)


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
        self.ctx = {}  # what a block's context makes true for the rule grammar: {"present": {ids}, "place": id} (callbacks' `fits`)

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
BETWEEN_APPROVAL_CAP = 6  # net approval Betweens may move one companion in one chapter (design §9)
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
        return f"book{finale_book(plan)}:climax"
    return when


def at_status(at, st):
    """'due' | 'future' | 'overdue' | 'unknown' for a resolved target against the current position."""
    pos = st.plan["position"]
    book, chapter, nxt, stage = int(pos["book"]), int(pos["chapter"]), int(pos["next_scene"]), pos["stage"]
    if at == "any":
        return "due"
    if at == "later":
        return "later"  # a callback: never due, never overdue; fired wherever it fits
    m = re.match(r"^on:(\w+)$", at)
    if m:
        return "due" if st.plan.get("flags", {}).get(m.group(1)) else "future"
    m = re.match(r"^ch(\d{2,})(?::(s(\d+)|climax))?$", at)
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
    m = re.match(r"^book(\d+)(?::(beat(\d+)|climax))?$", at)
    if m:
        b = int(m.group(1))
        if book > b:
            return "overdue"
        if book < b:
            return "future"  # a later Book, seeded or not: `plan book open N` seeds its beats when it opens
        sub = m.group(2)
        if not sub:
            return "due"
        tc = st.plan.get("route", {}).get(f"book{b}", {}).get("transition_chapter")
        at_transition = tc is not None and int(tc) == chapter
        if sub == "climax":  # the Book's climax is its transition chapter's, not every chapter climax in the Book
            return "due" if (stage in ("climax", "choice", "transition") and at_transition) else "future"
        k = int(m.group(3))
        beats = st.plan.get("core_beats", {})
        beat = beats.get(f"b{b}.{k}")
        if beat is None:
            return "unknown"
        if beat.get("status") == "planned":
            # a beat that never got its own chapter is being folded now: into the transition, or into a later beat
            # already on the page; what was owed to it is owed there, not after the Book has moved on
            later_started = any(v.get("status") in ("in_progress", "done") for kk, v in beats.items()
                                if re.match(rf"^b{b}\.(\d+)$", kk) and int(kk.split(".")[1]) > k)
            return "due" if (at_transition or later_started) else "future"
        return {"in_progress": "due"}.get(beat.get("status"), "overdue")
    m = re.match(r"^transition(\d+)$", at)
    if m:
        b = int(m.group(1))
        if book > b:
            return "overdue"
        if book < b:
            return "future"
        tc = st.plan.get("route", {}).get(f"book{b}", {}).get("transition_chapter")
        return "due" if tc is not None and int(tc) == chapter else "future"
    return "unknown"


def item_status(it, st):
    """A due item's status, with one courtesy: a `color` line made for `next` stays due through the block after its
    own, so a scene's opening never has to carry every line owed to it (style.md §3, the opening)."""
    s_ = at_status(it.get("at", ""), st)
    if s_ != "overdue" or it.get("weight") != "color" or it.get("when") != "next":
        return s_
    m = re.match(r"^ch(\d{2,}):s(\d+)$", str(it.get("at", "")))
    pos = st.plan["position"]
    if not m or int(m.group(1)) != int(pos["chapter"]):
        return s_
    k, nxt = int(m.group(2)), int(pos["next_scene"])
    if pos["stage"] == "scene" and nxt == k + 1:
        return "due"
    if pos["stage"] in ("climax", "choice") and nxt == k + 1:  # the scene it was aimed at was the chapter's last
        return "due"
    return s_


def rule_where_book(where, plan=None):
    """The Book a rule's `where` belongs to (bookN…, transitionN, finale = the saga's finale Book), or None for `any` and the like."""
    w = str(where or "")
    m = re.match(r"^(?:book|transition)(\d+)", w)
    if m:
        return int(m.group(1))
    return finale_book(plan or {}) if w == "finale" else None


def rule_fired_in_book(rule, plan, book):
    """A rule already honoured: for a standing rule (`where: any`, once per Book), fired in this Book; for any other, fired at all."""
    fired = rule.get("fired") or []
    if not fired:
        return False
    if str(rule.get("where")) != "any":
        return True
    for where in fired:
        m = re.match(r"^ch(\d{2,})", str(where))
        if m and book_of_chapter(plan, int(m.group(1))) == int(book):
            return True
    return False


def rule_timing(rule, st):
    """Where a rule's moment stands against the position: 'due' | 'future' | 'overdue' | 'any' | 'unknown'."""
    w = str(rule.get("where") or "any")
    if w == "any":
        return "any"
    return at_status(resolve_at(w, st.plan), st)


def knot_line(plan):
    """A Knot tied on the Ledger (darrow.py knot tie) that the story has not crossed yet: Book N ends at Knot N+2."""
    try:
        sheet = load_json(P["sheet"])
    except (OSError, ValueError, json.JSONDecodeError):
        return None
    tied = int(sheet.get("knots_count") or 0)
    book = int(plan["position"]["book"])
    need = book + 2
    if tied < need:
        return None
    road = (plan.get("route", {}).get(f"book{book}") or {}).get("road")
    left = [k for k, v in plan.get("core_beats", {}).items() if re.match(rf"^b{book}\.\d+$", k) and v.get("status") == "planned"]
    more = (len(left) + 1) // 2  # each chapter after this one lands at most two beats: one in its week, one as its climax
    when = ("at this chapter's climax (its beat folds into the transition)" if not left else
            f"in {more} chapter{'s' if more > 1 else ''} after this one: {len(left)} core beat{'s are' if len(left) > 1 else ' is'} still unwritten "
            f"({', '.join(sorted(left))}); each chapter lands at most two, one in its week with its full choice and one as its climax, "
            f"and the last one's climax is the transition (arc pacing)")
    if road:
        return f"KNOT {ROMAN[need]} tied · Book {ROMAN[book]}'s road decided ({road}): write t{book}.{road}, then `plan book open {book + 1}`"
    return f"KNOT {ROMAN[need]} tied on the Ledger · Book {ROMAN[book]}'s transition is due {when}"


def pending_items(ledger):
    for e in ledger.get("entries", []):
        for it in e.get("due", []):
            if it.get("status") == "pending":
                yield e, it


# ---------------------------------------------------------------- rule evaluator
RULE_NODES = (ast.Expression, ast.BoolOp, ast.And, ast.Or, ast.UnaryOp, ast.Not, ast.USub, ast.Compare,
              ast.Attribute, ast.Name, ast.Constant, ast.Load,
              ast.Gt, ast.GtE, ast.Lt, ast.LtE, ast.Eq, ast.NotEq)
KNOWN_ROOTS = ("approval", "bearing", "flags", "route", "factions", "temptation", "quests", "tether", "beats", "present", "place")
_CHAR_IDS = None


def char_ids():
    global _CHAR_IDS
    if _CHAR_IDS is None:
        _CHAR_IDS = set(R.char_files())
    return _CHAR_IDS


def tether_stage():
    """The Tether's stage from the engine's sheet (darrow.py owns it; saga.py only reads it). 0 if untied or unknown."""
    try:
        t = load_json(P["sheet"]).get("tether") or {}
        return int(t.get("stage") or 0)
    except (OSError, ValueError, json.JSONDecodeError):
        return 0


def sheet_rank():
    """Darrow's rank from the engine's sheet (Bound, Kindled, …); None if unknown. darrow.py owns it."""
    try:
        return load_json(P["sheet"]).get("rank") or None
    except (OSError, ValueError, json.JSONDecodeError):
        return None


def rank_owed(plan):
    """(on the page, on the sheet) when a rank crossing has not yet had its prose beat (style.md §3), else None."""
    onp, rk = plan.get("position", {}).get("rank_on_page"), sheet_rank()
    return (onp, rk) if onp and rk and onp != rk else None


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
        to_come = plan.get("companions_to_come", {})
        known = cid in comp or cid in plan.get("companions", {}) or cid in to_come
        if cid not in comp and cid in to_come:  # not on the road with him yet: what she has banked still counts
            return known, int(to_come[cid].get("approval_pending") or 0)
        return known, (comp.get(cid, {}).get("approval") or 0)
    if root == "bearing" and len(parts) == 2:
        return pole_axis(bearing, parts[1]) is not None, pole_value(bearing, parts[1])
    if root == "flags" and len(parts) == 2:
        flags = plan.get("flags", {})
        return parts[1] in flags, bool(flags.get(parts[1]))
    if root == "route" and len(parts) == 2 and re.match(r"^book\d+$", parts[1]):
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
    if root == "beats" and len(parts) == 3 and parts[-1] == "status":  # beats.b1_1.status (the beat id with its dot written as an underscore)
        bid = parts[1].replace("_", ".", 1)
        b = plan.get("core_beats", {})
        return bid in b, (b.get(bid, {}).get("status") or "")
    ctx = getattr(st, "ctx", None) or {}
    if root == "present" and len(parts) == 2:  # the person is in the block: a companion's short id, or a character id with its hyphen as an underscore
        who = parts[1]
        known = (who in char_ids() or who.replace("_", "-") in char_ids() or who in plan.get("companions", {})
                 or who in plan.get("companions_to_come", {}) or who in world.get("companions", {}))
        pres = ctx.get("present") or set()
        return known, (who in pres or who.replace("_", "-") in pres)
    if root == "place" and len(parts) == 2:  # the block's place (places.json id, its hyphens as underscores)
        pid = parts[1].replace("_", "-")
        return pid in known_place_ids(), ctx.get("place") == pid
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
ID_RE = re.compile(r"^(b\d+\.\d+|q\d+\.[a-z0-9_]+|t\d+(\.(high|main|low))?|book\d+\.question|rae\.[a-z0-9_]+|pacing|truths|motifs|beliefs|temptation|flags)\b")


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


SLOT_FIELDS = ("kind", "beat", "quest", "stage", "last", "pov", "plan", "turn", "micro", "challenge", "invite", "float", "day")
TURN_HINT = "who can, must, believes, risks or chooses what by the end that they could not at the start, and what Darrow attempts"


def chapter_template(ws, plan):
    """A canonical next-chapter skeleton for `plan chapter open`: 7 dated slots from the Sunday `ws`, spine on Sunday
    and Saturday, two float quest placeholders (slots 3 and 5, non-adjacent so both may carry a micro), empty
    world moves and climax. The placeholders continue the quests live now at their next stage first, then open the
    Book's available quests (required before optional), never more than two counted quests live at once (the cap
    `plan chapter open` enforces; the Tether and the Book's project are not counted), falling back to the Book's
    q<N>.* ids; every "" is for the writer to fill (a slot's `plan` is its content, its `turn` is who can, must,
    believes, risks or chooses what by the end, and what Darrow attempts), and `plan chapter open` accepts the result as is."""
    book = int(plan["position"]["book"])
    quests = plan.get("quests", {})
    counted = lambda q: not q.get("standing") and not q.get("project")
    live = [k for k, q in quests.items() if k.startswith(f"q{book}.") and q.get("status") == "live" and counted(q)]
    avail = [k for k, q in quests.items() if k.startswith(f"q{book}.") and q.get("status") == "available" and counted(q)]
    avail.sort(key=lambda k: 0 if quests[k].get("priority") == "required" else 1)
    order = live + avail + [f"q{book}.quest_a", f"q{book}.quest_b"]
    live_now, next_stage, picks = set(live), {k: int(quests[k].get("stage") or 0) + 1 for k in live}, []
    for _ in range(2):  # slot 3, then slot 5: a quest not yet in this chapter first, else the next stage of one already in it
        used, choice = {p[0] for p in picks}, None
        for repeat in (False, True):
            for k in order:
                if (k in used) != repeat or (repeat and k not in live_now):
                    continue
                st, total = next_stage.get(k, 1), (arc_quest_stage_count(k) if k in quests else None)
                if (total and st > total) or (k not in live_now and len(live_now) >= 2):
                    continue
                choice = (k, st)
                break
            if choice:
                break
        k, st = choice or (order[0], next_stage.get(order[0], 1))
        picks.append((k, st))
        live_now.add(k)
        next_stage[k] = st + 1
        total = arc_quest_stage_count(k) if k in quests else None
        if total and st >= total:
            live_now.discard(k)
    beat = plan["position"].get("beat") or f"b{book}.1"
    cur = plan.get("core_beats", {}).get(beat, {})
    if plan["position"].get("stage") in ("climax", "choice", "transition") or cur.get("status") in ("done", "folded"):
        # planned at a checkpoint (or after a cutaway): the current beat is answered, so the new chapter's spine is the next one
        beats = plan.get("core_beats", {})
        nxt = [k for k, v in beats.items() if re.match(rf"^b{book}\.\d+$", k) and v.get("status") == "planned"]
        nxt.sort(key=lambda k: int(k.split(".")[1]))
        if nxt:
            beat = nxt[0]
    slots = []
    for n in range(1, 8):
        s = {"n": n, "day": (ws + dt.timedelta(n - 1)).isoformat()}
        if n in (3, 5):
            q_, st_ = picks[0 if n == 3 else 1]
            s.update({"kind": "quest", "quest": q_, "stage": st_, "float": True})
        else:
            s.update({"kind": "spine", "beat": beat, "float": False})
        s.update({"plan": "", "turn": "", "micro": None, "challenge": None, "invite": None})
        slots.append(s)
    return {"week_start": ws.isoformat(), "question": "", "slots": slots, "world_moves": ["", "", ""],
            "climax": {"plan": "", "checks": [], "options": ["", "", ""], "default": 1}}


UP_SKIP = {"Ser", "The", "Confessor", "Brother", "Mother", "Sister", "King", "Dame", "Lady", "Lord"}


def under_pressure_for(text):
    """[(who, line)] for every GM character entry whose name the text mentions: the *Under pressure* drafting note
    (`_gm/characters.md`), printed with a slot so the tactic is in front of the writer. GM-only output."""
    path = ROOT / "saga/bible/_gm/characters.md"
    if not path.exists():
        return []
    words = set(re.findall(r"[A-Za-z][A-Za-z'-]+", text or ""))
    out, head, note = [], None, None
    sections = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("### "):
            if head:
                sections.append((head, note))
            head, note = line[4:].split(" — ")[0].split(" (")[0].strip(), None
        elif head and line.startswith("- **Under pressure:**"):
            note = line[len("- **Under pressure:**"):].strip()
    if head:
        sections.append((head, note))
    for head, note in sections:
        if not note:
            continue
        # the name proper: the words before any comma or quote in the heading, titles dropped ("Ser Darrow of Edgemoor" → Darrow,
        # Edgemoor; "King Aurel the Evergreen" → Aurel; "The red-handed woman" → the phrase itself)
        name = re.split(r"[,\"]", head)[0]
        if head.lower().startswith("the "):
            if head.lower() in (text or "").lower():
                out.append((head, note))
            continue
        keys = [w for w in re.findall(r"[A-Z][A-Za-z'-]{2,}", name) if w not in UP_SKIP]
        keys = [k for k in keys if k not in ("Evergreen",)]
        if any(k in words for k in keys):
            out.append((head, note))
    return out


def known_places():
    """{id: entry} from saga/state/places.json, whichever shape the file takes (a list, or an object keyed by id or holding a `places` list)."""
    path = ROOT / "saga/state/places.json"
    if not path.exists():
        return {}
    data = load_json(path)
    if isinstance(data, dict):
        inner = data.get("places")
        if isinstance(inner, list):
            data = inner
        elif isinstance(inner, dict):
            return dict(inner)
        else:
            return {k: v for k, v in data.items() if not str(k).startswith("_")}
    return {(x.get("id") if isinstance(x, dict) else str(x)): (x if isinstance(x, dict) else {}) for x in data}


def known_place_ids():
    return set(known_places().keys())


def art_names():
    """{art id: name} from engine/rules.json, the knightly Arts and the sport Arts alike."""
    rules = load_json(ROOT / "engine/rules.json")
    out = {a["id"]: a["name"] for a in rules.get("arts", [])}
    out.update({a["id"]: a["name"] for a in (rules.get("sport_arts") or {}).get("arts", [])})
    return out


def arts_spoken():
    """The Art ids the chronicle has named, in prose or a Reckoning box. An Art on the sheet but not on the page is locked for devices."""
    text = "\n".join(p_.read_text(encoding="utf-8") for p_ in sorted((ROOT / "saga/chronicle").glob("*.md"))).lower()
    return {aid for aid, name in art_names().items() if name.lower() in text}


def character_status(who):
    """(id, status) of the character file `who` names (an id, or its first token), or (None, None) when nobody on the page matches."""
    who = str(who or "").strip().lower()
    for p_ in sorted((ROOT / "saga/characters").glob("*.json")):
        if p_.stem == who or p_.stem.split("-")[0] == who:
            try:
                return p_.stem, (load_json(p_).get("status") or "")
            except Exception:
                return p_.stem, ""
    return None, None


def character_place(cid):
    """(last_seen place id, companion present flag or None) for a character file id."""
    path = ROOT / "saga/characters" / f"{cid}.json"
    try:
        c = load_json(path)
    except Exception:
        return None, None
    place = ((c.get("last_seen") or {}).get("place")) or None
    return place, None


def invite_narrative_problems(inv, s, st):
    """Why this person cannot come to Darrow now (design §5.6, the narrative gates): [(hard: bool, message)].
    Hard: no why_now; a `when` or a per-person invite rule not met; a companion marked absent; the person last seen
    somewhere Darrow is not, unless the slot's own plan names them (then a note: the scene must bring them first)."""
    out = []
    who = str(inv.get("who") or "").strip().lower()
    if not str(inv.get("why_now") or "").strip():
        out.append((True, f"invite from {who!r} has no why_now: one line of why this person comes to him now, from their want and the moment"))
    if inv.get("when"):
        state, detail = gate_state(inv["when"], st)
        if state == "NOT MET":
            out.append((True, f"invite from {who!r}: its when ({inv['when']}) is not met; the situation is not there yet"))
        elif state != "MET":
            out.append((True, f"invite from {who!r}: when {inv['when']!r} {state}: {detail}"))
    cid, _ = character_status(who)
    key = (cid or who).split("-")[0]
    rule = (st.plan.get("invite_rules") or {}).get(key) or (st.plan.get("invite_rules") or {}).get(cid or "")
    if rule:
        state, detail = gate_state(rule, st)
        if state == "NOT MET":
            out.append((True, f"{cid or who} does not come to him yet: the invite rule ({rule}) is not met"))
        elif state != "MET":
            out.append((True, f"invite rule for {key} {rule!r} {state}: {detail}"))
    if cid:
        comp = (st.world.get("companions") or {}).get(key)
        if isinstance(comp, dict) and comp.get("present") is False:
            out.append((True, f"{cid} is not with him (world.json companions.{key}.present is false)"))
        here = (st.world.get("location") or {}).get("place")
        there, _ = character_place(cid)
        if here and there and there != here:
            named = re.search(r"\b" + re.escape(key) + r"\b", str(s.get("plan") or ""), re.I) is not None
            if named:
                out.append((False, f"{cid} was last seen at {there} and Darrow is at {here}: the slot's scene must bring them to him before the invitation is offered"))
            else:
                out.append((True, f"{cid} was last seen at {there} and Darrow is at {here}: they cannot come to him until the story brings them (name them in the slot's plan, or plan the invitation later)"))
    return out


def unknown_names_in(texts):
    """Capitalised words, not sentence-first, in GM device text that no registry knows: a name the page has not spoken
    would leak through a scene or a Between. Takes one text or a list (each text starts its own sentence); a possessive
    or a contraction is read as its word ("Confessor's" is the Confessor, "You'll" is you)."""
    reg = registered_names()
    found = set()
    for text in ([texts] if isinstance(texts, str) else texts or []):
        for sent in re.split(r"(?<=[.!?:;])\s+|\n", str(text or "")):
            words = re.findall(r"[A-Za-z][A-Za-z'’-]+", sent)
            for w in words[1:]:
                w = re.sub(r"[’']s$|[’'](ll|re|ve|d|m|t)$", "", w).strip("-'’")
                if not w[:1].isupper() or len(w) < 3:
                    continue
                if w in NAME_STOP or w.lower() in reg or w.rstrip("s") in NAME_STOP or w.lower().rstrip("s") in reg:
                    continue
                found.add(w)
    return found


def gate_state(expr, st):
    """('MET'|'NOT MET'|'MALFORMED'|'UNKNOWN TERM', detail) for a quest gate written in the rule grammar (design §5.6)."""
    state, detail = rule_state({"id": "gate", "if": str(expr), "then": "", "where": ""}, st)
    return ("MET" if state == "ARMED" else state), detail


def stage_gate_for(quests, qid, stage):
    """A quest's per-stage gate (`quests[qid].stage_gates["N"]`, rule grammar): the sheet may reach a stage before the
    story is ready for its scene; then the scene waits (design §8, the Tether's later stages)."""
    return ((quests.get(qid) or {}).get("stage_gates") or {}).get(str(stage))


def quest_live_peak(plan, slots=None):
    """Walk a chapter's unwritten quest slots in day order from the quests live now, and return the most
    non-standing, non-project quests that would be live at once, with the slot where that happens (design §5.2:
    never more than two). A stage that is its quest's last takes the quest off the count after its day."""
    quests = plan.get("quests", {})
    live = {q for q, v in quests.items() if v.get("status") == "live" and not v.get("standing") and not v.get("project")}
    peak, where = len(live), None
    dated = [x for x in (slots if slots is not None else plan.get("chapter", {}).get("slots", [])) if x.get("day")]
    for x in sorted(dated, key=lambda y: y["day"]):
        if x.get("kind") != "quest" or x.get("status") not in ("planned", "next"):
            continue
        qid = x.get("quest")
        q = quests.get(qid) or {}
        if q.get("standing") or q.get("project"):
            continue
        live.add(qid)
        if len(live) > peak:
            peak = len(live)
            if where is None and peak > 2:  # the first slot that opens one quest too many
                where = (x.get("n"), sorted(live))
        total = arc_quest_stage_count(qid)
        if x.get("last") or (total and int(x.get("stage") or 0) >= total):
            live.discard(qid)
    return peak, where


def device_kinds(slots, quests):
    """The device kinds a chapter carries (design §5.6): challenge, invite, project (a quest slot of a project quest)."""
    kinds = set()
    for s in slots:
        if s.get("challenge"):
            kinds.add("challenge")
        if s.get("invite"):
            kinds.add("invite")
        if s.get("kind") == "quest" and (quests or {}).get(s.get("quest"), {}).get("project"):
            kinds.add("project")
    return kinds


def device_summary(plan):
    """One phrase per device in the chapter, for the digest."""
    out, quests = [], plan.get("quests", {})
    for s in plan.get("chapter", {}).get("slots", []):
        n, c, inv = s.get("n"), s.get("challenge"), s.get("invite")
        if c:
            out.append(f"challenge slot {n} ({c.get('status')}: {c.get('progress', 0)}/{c.get('goal')} won, {c.get('strain', 0)}/{c.get('limit')} strain)")
        if inv:
            out.append(f"invite slot {n} ({inv.get('who')}, {inv.get('status')})")
        if s.get("kind") == "quest" and quests.get(s.get("quest"), {}).get("project"):
            out.append(f"project {s.get('quest')} stage {s.get('stage')} slot {n} ({s.get('status')})")
    return out


def print_challenge(s, indent="  "):
    c = s.get("challenge") or {}
    print(f"{indent}challenge ({c.get('status')}): {c.get('objective')}")
    spoken, names = arts_spoken(), art_names()
    for a in c.get("approaches") or []:
        art = f" + {a['art']}" if a.get("art") else ""
        lock = f"  ⚠ locked: the page has not named {names.get(a['art'], a['art'])}" if a.get("art") and a["art"] not in spoken else ""
        print(f"{indent}  · {a.get('name')}: {a.get('stat')}{art} · DC {a.get('dc')}{lock}")
    res = c.get("result") or {}
    print(f"{indent}  progress {c.get('progress', 0)}/{c.get('goal')} · strain {c.get('strain', 0)}/{c.get('limit')} · if won: {short(res.get('won'), 90)} · if lost: {short(res.get('lost'), 90)}")
    print(f"{indent}  after each roll: `saga.py challenge {s.get('n')} success|fail`; the counters never reach the page")


def print_invite(s, indent="  "):
    inv = s.get("invite") or {}
    print(f"{indent}invite ({inv.get('kind')}, {inv.get('status')}): {inv.get('who')} wants {inv.get('want')}")
    print(f"{indent}  why now: {inv.get('why_now') or '(none: state one)'}" + (f" · when: {inv['when']}" if inv.get("when") else ""))
    for hard, msg in invite_narrative_problems(inv, s, State()):
        print(f"{indent}  {'⚠ locked' if hard else 'note'}: {msg}")
    print(f"{indent}  if ignored: {inv.get('if_ignored')} · offer it in one in-world line at the end of the close reply; `invite {s.get('n')} take|pass`")


def print_slot(s, full=False, plan=None):
    print(slot_label(s) + f" · {s.get('status')}" + (f" · wrote {s['wrote']}" if s.get("wrote") else ""))
    print(f"  plan: {s.get('plan')}")
    print(f"  turn: {s.get('turn') or '(none planned: state one in a line before writing: ' + TURN_HINT + ')'}")
    m = s.get("micro")
    if m:
        print(f"  {'beat choice' if m.get('beat') else 'micro (' + str(m.get('axis')) + ')'}: {m.get('ask')}")
        for i, opt in enumerate(m.get("options", []), 1):
            b = (m.get("bearing") or [None] * len(m["options"]))[i - 1]
            bt = f" [{', '.join(f'{k} {v:+d}' for k, v in b.items())}]" if b else ""
            print(f"    {i}. {opt}{bt}" + ("  (default)" if m.get("default") == i else ""))
    if plan is not None and s.get("kind") == "quest":
        gate = (plan.get("quests", {}).get(s.get("quest")) or {}).get("gate")
        if gate:
            state, detail = gate_state(gate, State())
            print(f"  gate: {gate} · {state}" + (" (locked: the slot cannot be written yet)" if state != "MET" else "") + (f" · {detail}" if detail else ""))
        sg = stage_gate_for(plan.get("quests", {}), s.get("quest"), s.get("stage"))
        if sg:
            state, detail = gate_state(sg, State())
            print(f"  stage gate: {sg} · {state}" + (" (locked: the stage is on the sheet, its scene waits for the story)" if state != "MET" else ""))
    if s.get("challenge"):
        print_challenge(s)
    if s.get("invite"):
        print_invite(s)
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
        inv = s.get("invite") or {}
        ups = under_pressure_for(" ".join([s.get("plan") or "", s.get("turn") or "", str(inv.get("who") or "").capitalize(), inv.get("want") or ""]))
        if ups:
            print("  --- under pressure: what each person named here notices, how they push, what they do when it fails ---")
            for who, line in ups:
                print(f"  {who}: {line}")
        print("  then: write to the turn; the reread (style.md §4); then `plan done`")


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
INSPIRATION_RE = re.compile(r"\[\s*inspiration\s*\]", re.I)  # an option's gate: `*[Inspiration]*` costs one when he picks it


def inspiration_held():
    """(held, cap) from the sheet (saga/state/darrow.json); (0, 4) when it cannot be read."""
    try:
        s = load_json(P["sheet"])
        return int(s.get("inspiration") or 0), int(s.get("inspiration_cap") or 4)
    except (OSError, ValueError, json.JSONDecodeError, TypeError):
        return 0, 4


def costs_inspiration(option_text):
    return bool(INSPIRATION_RE.search(str(option_text or "")))


def inspiration_default_problem(options, default, label):
    """An *[Inspiration]* option is his to pick and costs one, so it is never the default taken for him."""
    try:
        if default is not None and costs_inspiration(options[int(default) - 1]):
            return f"{label}: the default (option {default}) costs Inspiration; the default is never an *[Inspiration]* option (it is taken for him)"
    except (IndexError, ValueError, TypeError):
        return None
    return None


def inspiration_line(options):
    """The line the writer needs beside a choice that offers an *[Inspiration]* option: whether it is open or struck."""
    if not any(costs_inspiration(o) for o in options or []):
        return None
    held, cap = inspiration_held()
    return f"  Inspiration held: {held} of {cap}: the *[Inspiration]* option is {'open (`choose` spends it)' if held else 'struck through: he holds none'}"


def open_choice_lines(plan, cap=170):
    """The climax choice still open, if one is (plan.open_choice: it survives `plan chapter open`, so the default it
    resolves to is the climax's own, never the next chapter's)."""
    oc = plan.get("open_choice")
    if not oc:
        return []
    lines = [f"OPEN CHOICE (chapter {oc.get('chapter')} climax; carries {oc.get('carries', 2)} scenes into the next chapter, then its default): {short(oc.get('ask'), 100)}"]
    lines.append("  " + short(" / ".join(f"{i}. {o}" for i, o in enumerate(oc.get("options", []), 1)), cap) + f" · default {oc.get('default')} · answer: `saga.py choose --option K …`")
    il = inspiration_line(oc.get("options"))
    if il:
        lines.append(il)
    return lines


def rule_lines(st):
    """(broken, armed, waiting, near, quiet_count): the ledger's rules against the position (design §2). A rule is
    ARMED when its condition holds and its moment (`where`) is due or overdue; one whose moment is still ahead in this
    Book waits; one already honoured (`fired`: `saga.py fire r.id --where …`), whose Book has passed, or whose `if` is
    simply `true` is quiet."""
    plan, ledger = st.plan, st.ledger
    pos = plan["position"]
    cur_book = int(pos["book"])
    broken, armed, waiting, near_, quiet = [], [], [], [], 0
    for r in ledger.get("rules", []):
        state, detail = rule_state(r, st)
        if state in ("UNKNOWN TERM", "MALFORMED"):
            broken.append(f"RULE {state} {r['id']}: {detail}")
            continue
        wb = rule_where_book(r.get("where"), plan)
        if (wb is not None and wb < cur_book) or rule_fired_in_book(r, plan, cur_book) or str(r.get("if", "")).strip() == "true":
            quiet += 1
            continue
        if state == "ARMED":
            timing = rule_timing(r, st)
            if timing in ("due", "overdue", "any"):
                armed.append(f"RULE ARMED {r['id']} ({r.get('where')}{', overdue' if timing == 'overdue' else ''}): {short(r.get('then'), 100)} · `fire {r['id']} --where …` once the page honours it")
            elif wb == cur_book:
                waiting.append(f"RULE armed, waits for {r.get('where')} · {r['id']}: {short(r.get('then'), 90)}")
            else:
                quiet += 1
            continue
        near = rule_near(r, st)
        if near:
            near_.append(f"RULE near {r['id']} ({r.get('where')}): {'; '.join(near)}")
        else:
            quiet += 1
    return broken, armed, waiting, near_, quiet


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
    kl = knot_line(plan)
    if kl:
        lines.append(kl)
    s = next_slot(plan)
    if s:
        lines.append("Next: " + slot_label(s) + ((" · beat choice" if s["micro"].get("beat") else " · micro " + str(s["micro"].get("axis"))) if s.get("micro") else ""))
        lines.append("  " + short(s.get("plan"), 150))
        lines.append("  turn: " + (short(s.get("turn"), 150) if s.get("turn") else "none planned (state one before writing)"))
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
    dev = device_summary(plan)
    if dev:
        lines.append("Devices: " + " · ".join(dev))
    if int(pos["chapter"]) >= 2 and not live:
        first_req = next((k for k, v in q.items() if v.get("status") == "available" and v.get("priority") == "required"), None)
        lines.append("⚠ no quest live; plan a stage of " + (first_req or "any available quest") + " (design §5.2)")
    om = plan.get("open_micro")
    if om:
        lines.append(f"Open {'beat choice' if om.get('beat') else 'micro'} (slot {om.get('slot')}, scene {om.get('scene')}{'' if om.get('beat') else ', ' + str(om.get('axis'))}): {om.get('ask')}")
        lines.append("  " + short(" / ".join(f"{i}. {o}" for i, o in enumerate(om.get("options", []), 1)), 170))
    else:
        lines.append("Micro: none open")
    lines += open_choice_lines(plan)
    t_rows = tale_state(st)
    for t in t_rows:
        if t["owed"]:
            lines.append(f"TALE OWED: {t['id']} piece {t['told'] + 1} of {t['pieces']} (task {t['told'] + 1} of {t['project']} reported): `saga.py brief --tale`, written now")
    for pid, done in unbound_projects(t_rows):
        lines.append(f"TALE UNBOUND: project {pid} has {done} task(s) reported and no tale: `saga.py tale bind {pid}`, then its piece(s)")
    lines.append(bearing_line(bearing))
    ro = rank_owed(plan)
    if ro:
        lines.append(f"RANK OWED: {ro[0]} → {ro[1]}: one prose beat in the next scene, the script changing as he notices it (style.md §3); then `plan set rank_on_page={ro[1]}`")
    broken, armed, waiting, near_, quiet = rule_lines(st)
    lines += broken + armed  # before the due items: an armed rule changes what the next scene may be
    due_now, overdue, future, later = [], [], 0, 0
    for e, it in pending_items(ledger):
        s_ = item_status(it, st)
        if s_ == "due":
            due_now.append(it)
        elif s_ == "overdue":
            overdue.append(it)
        elif s_ == "later":
            later += 1
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
    if later:
        stale = sum(1 for e, it in pending_items(ledger) if it.get("at") == "later" and int(it.get("offered") or 0) >= 4)
        lines.append(f"Callbacks waiting for a fit: {later} (`saga.py due --later`; one per scene at most" + (f"; {stale} offered 4+ times unfired: rewrite or void" if stale else "") + ")")
    shown = waiting[:2] + near_[:3]
    lines += shown
    more = len(waiting) + len(near_) - len(shown)
    if more:
        lines.append(f"  (+{more} more rules waiting/near; `saga.py check` lists the rules)")
    lines.append(f"+{future} pending later, +{quiet} rules quiet; `saga.py brief` before writing · `saga.py due --all` · `saga.py check`")
    if len(lines) > NOW_CAP:  # the digest is a digest: it says what it cut, and where the whole picture is
        cut = len(lines) - NOW_CAP + 1
        lines = lines[: NOW_CAP - 2] + [f"  (digest cut {cut} line(s): `saga.py brief` has the whole picture for the next block, `saga.py due` every item)", lines[-1]]
    print("\n".join(lines))


def cmd_due(args):
    st = State()
    items = list(pending_items(st.ledger))

    def show(rows, label=None):
        for e, it in rows:
            tag = label or item_status(it, st).upper()
            print(f"{it['id']} [{it.get('weight')}] when={it.get('when')} at={it.get('at')} {tag} · from {e['id']} ({e['made'].get('date')}: {short(e.get('chose'), 60)})")
            print(f"  {it.get('what')}")
            extras = [x for x in (f"fits: {it['fits']}" if it.get("fits") else None,
                                  f"priority {it['priority']}" if it.get("priority") else None,
                                  f"until {it['valid_until']}" if it.get("valid_until") else None,
                                  f"offered {it['offered']}× unfired ({', '.join(it.get('offered_at') or [])})" if it.get("offered") else None,
                                  f"if void: approval {json.dumps((it.get('if_void') or {}).get('approval'))}" if it.get("if_void") else None) if x]
            if extras:
                print("  " + " · ".join(extras))

    for o in owed_moves(st.plan):
        print(f"WORLD MOVE owed (from skipped slot {o['n']}): the next scene or the climax opens on it: {o['world_move']}")
    if args.all:
        if not items:
            print("nothing pending")
        show(items)
        return
    if getattr(args, "later", False):
        rows = [(e, it) for e, it in items if it.get("at") == "later"]
        print(f"callbacks waiting for a fit: {len(rows)} (cap {CALLBACK_CAP}; at most one fired per scene: `fire ID --where …`, or `void ID --why …`)")
        show(rows, label="LATER")
        return
    now_rows = [(e, it) for e, it in items if item_status(it, st) in ("due", "overdue")]
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
def validate_entry(entry, ledger, plan, bearing=None, world=None, pending=False, st=None):
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
        # a callback (when: later) may say where it fits, how much it is worth, when it lapses and what lapsing costs (design §5.6)
        later = it.get("when") == "later"
        for k_ in ("fits", "priority", "valid_until"):
            if it.get(k_) is not None and not later:
                probs.append(f"due[{i}].{k_}: only a callback (when: later) carries it")
        if it.get("fits") is not None:
            tree = parse_rule(it["fits"]) if isinstance(it["fits"], str) else None
            if tree is None:
                probs.append(f"due[{i}].fits {it.get('fits')!r} is malformed (the rule grammar: present.<id>, place.<id>, flags.x, approval.x, quests.x.status …)")
            elif st is not None:
                unk = sorted({".".join(p) for p in rule_terms(tree) if not term_lookup(p, st)[0]})
                if unk:
                    probs.append(f"due[{i}].fits: unknown term(s) {', '.join(unk)}")
        if it.get("priority") is not None and (isinstance(it["priority"], bool) or it["priority"] not in (1, 2, 3)):
            probs.append(f"due[{i}].priority {it.get('priority')!r}: 1 (a line if it fits), 2 (the default) or 3 (worth a beat)")
        if it.get("valid_until") is not None and not VALID_UNTIL_RE.match(str(it["valid_until"])):
            probs.append(f"due[{i}].valid_until {it.get('valid_until')!r}: the position it lapses after (chNN, chNN:sN, chNN:climax, bookN, bookN:climax, transitionN, finale)")
        iv = it.get("if_void")
        if iv is not None:
            if not isinstance(iv, dict) or set(iv) - {"approval"} or not isinstance(iv.get("approval"), dict) or not iv["approval"]:
                probs.append(f"due[{i}].if_void is {{\"approval\": {{\"<companion>\": -N}}}}: what lapsing or voiding it costs")
            else:
                for cid, dlt in iv["approval"].items():
                    if isinstance(dlt, bool) or not isinstance(dlt, int):
                        probs.append(f"due[{i}].if_void.approval.{cid} {dlt!r} is not an integer")
                    if world is not None and cid not in world.get("companions", {}) and cid not in plan.get("companions_to_come", {}):
                        probs.append(f"due[{i}].if_void.approval.{cid}: not a companion")
        # canonical key order
        ordered = {k: it[k] for k in ("id", "when", "at", "weight", "what", "fits", "priority", "valid_until", "if_void", "status") if k in it}
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
    add_entry(st, entry, args.witnessed, args.pending, args.dry_run)


def add_entry(st, entry, witnessed_csv, pending=False, dry_run=False):
    """Record one ledger entry: validate, fold the witnesses' preference, trim a Between's approval to its cap, apply the
    `now` deltas (approval, Bearing, flags, factions), append it, save. Used by `add` and by `choose`."""
    ledger, plan, world = st.ledger, st.plan, st.world
    auto = downstream_due(entry, plan)  # one due item per flag set: the Downstream line is owed, not remembered
    # first pass: shape, poles, magnitudes, the entry's own approval targets
    probs = validate_entry(entry, ledger, plan, bearing=st.bearing, world=world, pending=pending, st=st)
    if probs:
        die("refusing the entry:\n  " + "\n  ".join(probs))
    now = entry["now"]
    witnessed = [w.strip() for w in (witnessed_csv or "").split(",") if w.strip()]
    # companion-preference approval from bearing deltas (computed quietly; printed only once everything is accepted)
    pref_delta = {}
    to_come = plan.get("companions_to_come", {})
    banked = set()  # witnesses not yet on the road with him: their preference banks as approval_pending
    for cid in witnessed:
        if cid in plan.get("companions", {}):
            prefs = [p.lower() for p in plan["companions"][cid].get("prefers", [])]
        elif cid in to_come:
            prefs = [p.lower() for p in to_come[cid].get("prefers", [])]
            banked.add(cid)
        else:
            die(f"--witnessed {cid}: not in plan.json companions or companions_to_come")
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
        bad = [cid for cid in pref_delta if cid not in world.get("companions", {}) and not ((pending or cid in banked) and cid in to_come)]
        if bad:
            die("refusing the entry:\n  " + "\n  ".join(f"now.approval.{cid} (folded from --witnessed): not a companion in world.json (use --pending for companions_to_come)" for cid in bad))
    for line in folded:
        print(line)
    # a Between moves regard a little: at most BETWEEN_APPROVAL_CAP net per companion per chapter (design §9), so
    # role-play colours how people stand with him and the choices still decide it
    made = entry.get("made") or {}
    if str(made.get("scene", "")).startswith("between") and now.get("approval"):
        prior = {}
        for e in ledger["entries"]:
            em = e.get("made") or {}
            if int(em.get("chapter", -1)) == int(made.get("chapter", -2)) and str(em.get("scene", "")).startswith("between"):
                for cid, dlt in ((e.get("now") or {}).get("approval") or {}).items():
                    prior[cid] = prior.get(cid, 0) + int(dlt)
        for cid in list(now["approval"]):
            dlt, before = int(now["approval"][cid]), prior.get(cid, 0)
            kept = max(-BETWEEN_APPROVAL_CAP - before, min(BETWEEN_APPROVAL_CAP - before, dlt))
            kept = kept if (kept > 0) == (dlt > 0) or kept == 0 else 0
            if kept != dlt:
                print(f"Between approval {cid}: {dlt:+d} → {kept:+d} (Betweens move a companion at most ±{BETWEEN_APPROVAL_CAP} a chapter; this chapter so far {before:+d})")
            if kept:
                now["approval"][cid] = kept
            else:
                del now["approval"][cid]
        if not now["approval"]:
            del now["approval"]
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
    st.save(dry=dry_run)
    print(("(dry run) " if dry_run else "") + f"ledger entry {entry['id']} recorded with {len(ordered['due'])} due item(s)")
    return ordered


def find_due(ledger, did):
    for e in ledger["entries"]:
        for it in e.get("due", []):
            if it["id"] == did:
                return e, it
    die(f"no due item {did} in the ledger")


def fire_item(st, did, where, evidence=None):
    """Mark a due item fired at `where`; a rule id (r.…) marks the rule honoured there. `evidence` is the block's own
    words that pay it (the record requires it; from the command line it is a courtesy). Returns the line to print."""
    if not WHERE_RE.match(str(where or "")):
        die(f"--where {where!r} must look like ch03:s2, ch03:climax, ch03:interlude or book2")
    proof = f" · proved: “{short(evidence, 100)}”" if evidence else " · unproved: the record should carry the block's words that pay it"
    if str(did).startswith("r."):  # a rule honoured on the page: it has state, so `now` stops arming it (once per Book for a standing rule)
        r = next((x for x in st.ledger.get("rules", []) if x.get("id") == did), None)
        if not r:
            die(f"no rule {did} in the ledger")
        r.setdefault("fired", []).append(where)
        if evidence:
            r.setdefault("evidence", {})[where] = evidence
        st.touch("ledger")
        return f"rule {did} honoured at {where}: {r.get('then')}" + (" (a standing rule: it may arm again in a later Book)" if str(r.get("where")) == "any" else "") + proof
    e, it = find_due(st.ledger, did)
    if it["status"] != "pending":
        die(f"{did} is already {it['status']}")
    it["status"] = f"fired@{where}"
    if evidence:
        it["evidence"] = evidence
    st.touch("ledger")
    return f"{did} fired at {where}: {it['what']}{proof}"


def void_item(st, did, why):
    e, it = find_due(st.ledger, did)
    if it["status"] != "pending":
        die(f"{did} is already {it['status']}")
    it["status"] = f"void:{why}"
    st.touch("ledger")
    cost = apply_if_void(st, it, f"void of {did} ({short(why, 40)})")
    return f"{did} void: {why}" + (f"\n{cost}" if cost else "")


# ---------------------------------------------------------------- callbacks: where they fit, what they cost when they lapse
def presence_ctx(people_ids, place):
    """The context a callback's `fits` is read against: who is in the block, in every spelling the grammar takes
    (hollis-garrow, hollis_garrow, hollis), and where it is."""
    pres = set()
    for cid in people_ids or []:
        cid = str(cid or "")
        if cid:
            pres.update({cid, cid.replace("-", "_"), cid.split("-")[0]})
    return {"present": pres, "place": place}


def callback_fits(it, st, ctx):
    """(fits here, specificity): a callback with no `fits` fits anywhere; specificity is the number of terms it names."""
    expr = it.get("fits")
    if not expr:
        return True, 0
    tree = parse_rule(expr)
    if tree is None:
        return False, 0
    old = st.ctx
    st.ctx = ctx or {}
    try:
        ok = bool(eval_node(tree, st))
    finally:
        st.ctx = old
    return ok, len(rule_terms(tree))


def next_entry_id(ledger, chapter):
    ns = [int(m.group(2)) for e in ledger.get("entries", []) for m in [ENTRY_ID_RE.match(str(e.get("id", "")))] if m and int(m.group(1)) == int(chapter)]
    return f"c{int(chapter):02d}.{(max(ns) + 1) if ns else 1}"


def auto_entry(st, chose, now, scene):
    """A terse entry the engine writes for a cost the rules set (a promise lapsed, an invitation passed): it goes through
    `add_entry` like any other, so the ledger's invariant holds and `history` can name it. Its `made.scene` never reads
    as a Between, so the Between cap leaves it alone."""
    plan = st.plan
    chapter = int(plan["chapter"].get("number") or plan["position"]["chapter"])
    entry = {"id": next_entry_id(st.ledger, chapter), "made": {"chapter": chapter, "scene": scene, "date": today_local().isoformat()},
             "chose": chose, "now": now, "due": [], "auto": True}
    return add_entry(st, entry, "", pending=True, dry_run=False)


def apply_if_void(st, it, chose):
    """What a due item's `if_void` costs, applied: approval through an auto entry. Returns the line to print, or None."""
    appr = {k: int(v) for k, v in ((it.get("if_void") or {}).get("approval") or {}).items()}
    if not appr:
        return None
    ordered = auto_entry(st, f"{chose}: {short(it.get('what'), 80)}", {"approval": appr}, scene=f"auto:{it.get('id')}")
    return f"  its cost ({ordered['id']}): approval " + ", ".join(f"{k} {v:+d}" for k, v in appr.items())


def expire_callbacks(st, where):
    """A callback past its valid_until lapses at `where`: void:expired, its if_void cost applied, each printed loudly."""
    out = []
    for e, it in list(pending_items(st.ledger)):
        vu = it.get("valid_until")
        if not vu or it.get("at") != "later":
            continue
        if at_status(resolve_at(vu, st.plan), st) == "overdue":
            it["status"] = f"void:expired@{where}"
            st.touch("ledger")
            out.append(f"callback {it['id']} lapsed at {where} (valid until {vu}): {short(it.get('what'), 100)}")
            cost = apply_if_void(st, it, f"lapsed: {it['id']}")
            if cost:
                out.append(cost)
    return out


def cmd_fire(args):
    st = State()
    line = fire_item(st, args.id, args.where, getattr(args, "evidence", None))
    st.save()
    print(line)


def cmd_void(args):
    st = State()
    line = void_item(st, args.id, args.why)
    st.save()
    print(line)


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
def plan_done_written(st, s, wrote):
    """A slot's scene is on the page: the slot, the position, its quest or beat, the owed world moves (the --wrote half of
    `plan done`; `record` calls it too)."""
    plan = st.plan
    if not wrote or not WROTE_RE.match(wrote):
        die("--wrote must look like ch01:s3 or ch01:interlude")
    m = WROTE_RE.match(wrote)
    if int(m.group(1)) != int(plan["position"]["chapter"]):
        die(f"--wrote {wrote} names chapter {int(m.group(1))}; the plan is on chapter {plan['position']['chapter']}")
    if m.group(3) and int(m.group(3)) > int(plan["position"].get("next_scene") or 1):
        die(f"--wrote {wrote} skips ahead; the next scene is {plan['position'].get('next_scene')}")
    heads = chapter_headings(st.world)
    key = m.group(3) or m.group(2)
    if heads is not None and key not in {k for k, _ in heads}:
        want = f"### Scene {key}" if m.group(3) else "### " + key.split("-")[0].capitalize()
        print(f"⚠ {st.world.get('chapter_file')} has no `{want}` heading yet; write the scene before `saga.py check`")
    s["status"] = "written"
    s["wrote"] = wrote
    plan["position"]["last_written"] = wrote
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
    print(f"slot {s['n']} written as {wrote} · next scene {plan['position']['next_scene']} · stage scene")
    if (s.get("invite") or {}).get("status") == "waiting":
        print("  the slot's invitation is waiting: the close reply ends on its one in-world line; `invite N take` when he answers in voice, `invite N pass` at the next close if he has not")
    if (s.get("challenge") or {}).get("status") == "open":
        print("  the slot's challenge is still open: it may run into the next scene, then `challenge N success|fail` resolves it and `saga.py add` records what it changed")
    if s.get("kind") == "quest" and plan.get("quests", {}).get(s.get("quest"), {}).get("project"):
        print("  a project stage: world.json → projects[] (stage, the decision, one visible line in the page's words), the place's description in places.json")
    if s.get("micro"):
        print(f"slot {s['n']} carries a micro: if the scene ended on it, it opens now (`record` with \"micro_opened\": true, or `plan micro open {s['n']}`)")
    pay_owed_moves(plan, "scene")
    st.touch("plan")


def open_micro(st, s):
    plan = st.plan
    if not s.get("micro"):
        die(f"slot {s.get('n')} has no micro planned")
    if s.get("status") != "written":
        die(f"slot {s.get('n')} is {s.get('status')}: its scene is recorded first (the micro takes its scene key from the slot)")
    if plan.get("open_micro"):
        die(f"a micro is already open (slot {plan['open_micro'].get('slot')}); close it first (it resolves to its default if unanswered)")
    m = dict(s["micro"])
    scene_key = micro_scene_key(plan, s)
    plan["open_micro"] = {"slot": s["n"], "chapter": int(plan["chapter"].get("number")), "scene": scene_key, "opened": today_local().isoformat(), **m}
    st.touch("plan")
    print(f"{'beat choice' if m.get('beat') else 'micro'} open from slot {s['n']} at scene {scene_key} ({'its arc weights' if m.get('beat') else m.get('axis')}): {m.get('ask')} · default {m.get('default')}")
    print("  his answer: `saga.py choose --option K '<ledger entry>'` (the consequence is folded into the next scene's opening; the brief carries it)")


def advance_next_slot(plan):
    nxt = next((x for x in sorted(plan["chapter"]["slots"], key=lambda x: float(x.get("n", 0))) if x.get("status") == "planned"), None)
    if nxt and not any(x.get("status") == "next" for x in plan["chapter"]["slots"]):
        nxt["status"] = "next"
        print(f"next: {slot_label(nxt)}")


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
    if a == "choice":
        oc = plan.get("open_choice")
        if args.sub == "show":
            print("\n".join(open_choice_lines(plan)) if oc else "no climax choice is open")
            return
        if args.sub == "open":
            if oc:
                die(f"a climax choice is already open (chapter {oc.get('chapter')}); `saga.py choose` answers it first")
            try:
                c = json.loads(args.json or "")
            except json.JSONDecodeError as e:
                die(f"choice JSON invalid ({e}): {{\"ask\": …, \"options\": [\"…\", \"…\"], \"default\": 1}}")
            opts = c.get("options") or []
            if not 2 <= len(opts) <= 3 or not all(str(o).strip() for o in opts):
                die("a climax choice has 2–3 options, each the option's text as the page has it")
            if c.get("default") not in range(1, len(opts) + 1):
                die(f"default must be an option number (1–{len(opts)}): the one the highest-approval companion present would pick")
            p_i = inspiration_default_problem(opts, c.get("default"), "the climax choice")
            if p_i:
                die(p_i)
            if plan["position"].get("stage") not in ("climax", "choice", "transition"):
                die(f"the stage is {plan['position'].get('stage')}: a climax choice opens once the climax is written (`plan set stage=climax` first)")
            plan["open_choice"] = {"chapter": int(plan["chapter"].get("number")), "scene": "climax", "ask": c.get("ask") or "What does Darrow do?",
                                   "options": [str(o) for o in opts], "default": int(c["default"]), "opened": today_local().isoformat(), "carries": int(c.get("carries") or 2)}
            st.touch("plan")
            st.save()
            print("\n".join(open_choice_lines(plan)))
            return
        if not oc:
            die("no climax choice is open")
        opt = args.option if args.option is not None else (oc.get("default") if args.by == "bearing" else None)
        if opt is None:
            die("pass --option K (or --by bearing to take the climax's default)")
        if opt not in range(1, len(oc.get("options") or []) + 1):
            die(f"option {opt} is not one of the {len(oc.get('options') or [])} options")
        plan["open_choice"] = None
        st.touch("plan")
        st.save()
        print(f"climax choice of chapter {oc.get('chapter')} closed: option {opt} by {args.by}" + (" (the climax's default)" if args.option is None else ""))
        print("  recorded only through `saga.py choose` (its ledger entry moves the Bearing, its choices[] row marks the page); the `### Choice` block comes next")
        return
    if a == "climax":
        ch = plan["chapter"]
        c = ch.get("climax") or {}
        for l in open_choice_lines(plan):
            print(l)
        print(f"chapter {ch.get('number')} · question: {ch.get('question')}")
        print(f"  plan: {c.get('plan')}")
        print("  checks: " + ("; ".join(c.get("checks") or []) or "none"))
        for i, o in enumerate(c.get("options") or [], 1):
            print(f"  {i}. {o}" + ("  (default)" if c.get("default") == i else ""))
        if c.get("default") is not None:
            print(f"  default: option {c['default']} (taken by the Bearing if the choice is still open at the second close of the next chapter)")
        held_i, cap_i = inspiration_held()
        print(f"  Inspiration held: {held_i} of {cap_i} (an `*[Inspiration]*` option is offered open while he holds one, struck through at none; never the default)")
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
            # what the slot carried does not happen by itself: say so, and close the devices that cannot wait
            if s.get("kind") == "quest" and s.get("quest"):
                print(f"quest {s['quest']} stage {s.get('stage')} did not run: re-plan it into a later float slot "
                      f"(`plan slot N kind=quest quest={s['quest']} stage={s.get('stage')} plan=…`), or let it wait for the next chapter")
            if s.get("micro"):
                print("its micro-choice did not run; it comes back only if the stage is re-planned")
            if (s.get("invite") or {}).get("status") == "waiting":
                s["invite"]["status"] = "void"
                print(f"its invitation ({s['invite'].get('who')}) is void: nobody came to a day that did not happen")
            if (s.get("challenge") or {}).get("status") == "open":
                s["challenge"]["status"] = "void"
                print("its challenge is void; re-plan it with the stage if it still matters")
        else:
            plan_done_written(st, s, args.wrote)
        advance_next_slot(plan)
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
            if k in ("challenge", "invite") and v is not None and not isinstance(v, dict):
                die(f"{k} must be JSON or null (the shape is in design.md §5.6)")
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
            open_micro(st, slot_by_n(plan, args.n))
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
            print("  the answer is recorded only through /choose: its ledger entry (`saga.py add`, which moves the Bearing) and a world.json choices[] row; `check` refuses an answered micro without them")
        st.touch("plan")
        st.save()
        return
    if a == "chapter" and args.sub == "cutaway":
        # a week with nothing logged whose chapter was already planned (the checkpoint before it opened it): it
        # becomes a cutaway chapter, one interlude and no slots, no climax (checkpoint skill, section A)
        chp = plan.get("chapter", {})
        wrote = [x.get("n") for x in chp.get("slots", []) if x.get("status") == "written"]
        if wrote:
            die(f"chapter {chp.get('number')} has written slots {wrote}: a cutaway chapter is a week with nothing on the page")
        if plan.get("open_micro"):
            die("a micro is open; resolve it first (/choose with its default)")
        owed = [x["world_move"] for x in chp.get("slots", []) if x.get("world_move") and not x.get("world_move_used")]
        n_slots = sum(1 for x in chp.get("slots", []) if x.get("status") in ("planned", "next"))
        chp["world_moves"] = owed + list(chp.get("world_moves") or [])  # a skipped day's owed move stays owed
        chp["slots"] = []
        chp["climax"] = {"plan": "", "checks": [], "options": [], "default": None}
        plan["position"].update({"next_scene": 1, "stage": "scene"})
        st.touch("plan")
        st.save()
        print(f"chapter {chp.get('number')} is now a cutaway chapter ({n_slots} planned slots cleared; world moves kept for its interlude): "
              f"write its one `### Interlude — Title`, record it in world.json scenes[], then open the next chapter")
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
            die(f"a micro is still open (slot {om.get('slot')}, scene {om.get('scene')}); resolve it first through /choose with its default, option {om.get('default')}, by bearing (a ledger entry, a choices[] row, then `plan micro close --by bearing`)")
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
            s.setdefault("turn", "")
            s.setdefault("challenge", None)
            s.setdefault("invite", None)
        if ordered["slots"] and not any(s.get("status") == "next" for s in ordered["slots"]):
            ordered["slots"][0]["status"] = "next"
        no_turn = [s.get("n") for s in ordered["slots"] if not str(s.get("turn") or "").strip()]
        if no_turn:
            print(f"⚠ slots {no_turn} have no turn ({TURN_HINT}): `plan slot N turn=\"…\"` before their day closes")
        cl_ = ordered.get("climax") or {}
        p_i = [p for p in [inspiration_default_problem(cl_.get("options") or [], cl_.get("default"), "climax")]
               + [inspiration_default_problem((s.get("micro") or {}).get("options") or [], (s.get("micro") or {}).get("default"), f"slot {s.get('n')} micro") for s in ordered["slots"] if s.get("micro")] if p]
        if p_i:
            die("refusing the plan:\n  " + "\n  ".join(p_i))
        old = plan.get("chapter", {})  # the outgoing chapter: read before anything replaces it
        ordered["previous_devices"] = sorted(device_kinds(old.get("slots", []), plan.get("quests", {})))
        clash = sorted(device_kinds(ordered["slots"], plan.get("quests", {})) & set(ordered["previous_devices"]))
        if clash:
            print(f"⚠ {', '.join(clash)} ran in chapter {old.get('number')} too; a device kind rests a chapter (design §5.6): `check` will refuse the plan")
        for s in ordered["slots"]:
            gate = (plan.get("quests", {}).get(s.get("quest")) or {}).get("gate") if s.get("kind") == "quest" else None
            if gate and gate_state(gate, st)[0] != "MET":
                print(f"⚠ slot {s.get('n')} plans {s.get('quest')} while its gate ({gate}) is not met: locked; `check` will refuse it until the story gets there")
            sg = stage_gate_for(plan.get("quests", {}), s.get("quest"), s.get("stage")) if s.get("kind") == "quest" else None
            if sg and gate_state(sg, st)[0] != "MET":
                print(f"⚠ slot {s.get('n')} plans {s.get('quest')} stage {s.get('stage')} while its stage gate ({sg}) is not met: locked; the scene waits for the story")
        peak, where = quest_live_peak(plan, ordered["slots"])
        if peak > 2 and where and not args.force:
            die(f"refusing the plan: slot {where[0]} would make {len(where[1])} quests live at once ({', '.join(where[1])}), {peak} at the most; never more than two "
                f"(the Tether and the Book's project are not counted). Finish one quest before the next opens, or move a stage to the next chapter (design §5.2)")
        # what the outgoing chapter leaves behind: unwritten slots are named; owed world moves carry over
        left =[s for s in old.get("slots", []) if s.get("status") in ("planned", "next")]
        owed = owed_moves(plan) if old.get("slots") else []
        if left:
            print(f"⚠ chapter {old.get('number')} leaves slots {[s['n'] for s in left]} unwritten (their content folds into the climax you have written)")
        for o in owed:
            print(f"⚠ world move still owed (slot {o['n']} of chapter {old.get('number')}): {o['world_move']} → carried to chapter {args.number}'s world_moves")
        blanks = [m for m in (ordered.get("world_moves") or []) if not str(m or "").strip()]
        if blanks:
            print(f"⚠ {len(blanks)} empty world move(s) dropped: a missed day pops one, so each must say what the world did")
        ordered["world_moves"] = [o["world_move"] for o in owed] + [m for m in (ordered.get("world_moves") or []) if str(m or "").strip()]
        plan["chapter"] = ordered
        book = plan["position"]["book"]
        r = plan.setdefault("route", {}).setdefault(f"book{book}", {"chapters": [], "road": None, "override": None, "transition_chapter": None})
        if int(args.number) not in [int(c) for c in r["chapters"]]:
            r["chapters"].append(int(args.number))
        plan["position"].update({"chapter": int(args.number), "next_scene": 1, "stage": "scene"})
        first_beat = next((x.get("beat") for x in sorted(ordered["slots"], key=lambda y: str(y.get("day") or "")) if x.get("kind") == "spine" and x.get("beat")), None)
        if first_beat and first_beat in plan.get("core_beats", {}):
            plan["position"]["beat"] = first_beat  # what is owed to this beat falls due from the chapter's first scene
            if plan["core_beats"][first_beat].get("status") == "planned":
                plan["core_beats"][first_beat]["status"] = "in_progress"
        for line_ in expire_callbacks(st, ch2(int(args.number))):
            print(line_)
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
        for line_ in expire_callbacks(st, f"book{n}"):
            print(line_)
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
        tc = plan.get("companions_to_come", {})
        if tc:
            print("still to come (rules read their banked approval; `plan companion arrive ID` the day they step on the road with him): "
                  + "; ".join(f"{k} ({short(str(v.get('note') or ''), 70)})" for k, v in tc.items()))
            print("  every road of the transition just written may have put someone on the road: arrive them now if it did (arc rae.road; Ash in t1)")
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
    if a == "invite_rule":
        rules_ = plan.setdefault("invite_rules", {})
        if args.expr in ("null", "none", ""):
            rules_.pop(args.id, None)
            print(f"invite_rules.{args.id} removed")
        else:
            state, detail = gate_state(args.expr, st)
            if state in ("MALFORMED", "UNKNOWN TERM"):
                die(f"invite rule {args.expr!r} {state}: {detail}")
            rules_[args.id] = args.expr
            print(f"invite_rules.{args.id}: {args.expr} · {state} now")
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


# ---------------------------------------------------------------- the Annals (lore)
LORE_ID_RE = re.compile(r"^(age|house|realm|folk|song|rhyme|saying|maxim|craft|calendar|beast)\.[a-z0-9_]+$")
LORE_HEAD_RE = re.compile(r"^##\s+([a-z]+\.[a-z0-9_]+)\s*[—–-]\s*(.+?)\s*$")
LORE_TIERS = ("common", "learned")
LORE_POOLS = {"saying": ("saying.",), "maxim": ("maxim.",), "verse": ("song.", "rhyme."), "rhyme": ("rhyme.",)}


def lore_entries():
    """The Annals as ({id: entry}, [repeated ids]) in file order; an entry has title, lines, tier, spoken, names, use."""
    out, dupes, cur = {}, [], None
    if not P["lore"].exists():
        return out, dupes
    for line in P["lore"].read_text(encoding="utf-8").splitlines():
        m = LORE_HEAD_RE.match(line)
        if m:
            if m.group(1) in out:
                dupes.append(m.group(1))
            cur = {"id": m.group(1), "title": m.group(2), "lines": [], "tier": "", "spoken": "", "names": "", "use": ""}
            out[m.group(1)] = cur
            continue
        if line.startswith("#"):
            cur = None
            continue
        if cur is None:
            continue
        cur["lines"].append(line)
        if line.startswith("- **"):
            for k, v in re.findall(r"\*\*(\w+):\*\*\s*(.*?)(?=\s*·\s*\*\*\w+:\*\*|$)", line):
                if k in ("tier", "spoken", "names", "use"):
                    cur[k] = v.strip()
    return out, dupes


def lore_pool(entries, kind):
    """What `lore pick` draws from: sayings and maxims as quoted lines, verse as stanzas (runs of `>` lines)."""
    items = []
    for e in entries.values():
        if not e["id"].startswith(LORE_POOLS[kind]):
            continue
        if kind in ("saying", "maxim"):
            for l in e["lines"]:
                m = re.match(r'^- "(.+?)"\s*(\(.*\))?\s*$', l)
                if m:
                    items.append((e, m.group(1), (m.group(2) or "").strip("()")))
        else:
            stanza = []
            for l in e["lines"] + [""]:
                if l.startswith(">"):
                    stanza.append(l[1:].strip())
                elif stanza:
                    items.append((e, "\n".join(stanza), ""))
                    stanza = []
    return items


def lore_spoke(entry_id, where):
    """Mark an entry of the Annals spoken at `where` (the field keeps every place it was spoken). Returns (old, new)."""
    text = P["lore"].read_text(encoding="utf-8")
    lines = text.splitlines()
    head = next((i for i, l in enumerate(lines) if LORE_HEAD_RE.match(l) and LORE_HEAD_RE.match(l).group(1) == entry_id), None)
    if head is None:
        die(f"no entry `{entry_id}` in the Annals")
    for i in range(head + 1, len(lines)):
        if lines[i].startswith("#"):
            break
        if "**spoken:**" in lines[i]:
            old = re.search(r"\*\*spoken:\*\*\s*(.*?)(?=\s*·\s*\*\*\w+:\*\*|$)", lines[i]).group(1)
            fresh = not old or old.strip() in ("—", "-", "unspoken") or old.strip().startswith("—")
            joined = where if fresh else (old if where in old else f"{old}; {where}")
            lines[i] = re.sub(r"(\*\*spoken:\*\*\s*)(.*?)(?=\s*·\s*\*\*\w+:\*\*|$)", lambda m: m.group(1) + joined, lines[i], count=1)
            P["lore"].write_text("\n".join(lines) + ("\n" if text.endswith("\n") else ""), encoding="utf-8")
            return old, joined
    die(f"{entry_id} has no **spoken:** field")


def cmd_lore(args):
    entries, dupes = lore_entries()
    if not entries:
        die(f"no Annals at {rel(P['lore'])}")
    what, arg = args.what, args.arg
    if what is None:
        print(f"The Annals · {len(entries)} entries · `lore <id>` one entry · `lore grep WORD` · `lore pick saying|verse|maxim|rhyme` · `lore spoke <id> --where chNN:sK`")
        kinds = ("age", "house", "realm", "folk", "song", "rhyme", "saying", "maxim", "craft", "calendar", "beast")
        order = sorted(entries.values(), key=lambda e: (kinds.index(e["id"].split(".")[0]) if e["id"].split(".")[0] in kinds else 99, list(entries).index(e["id"])))
        kind = None
        for e in order:
            k = e["id"].split(".")[0]
            if k != kind:
                kind = k
                print(f"[{kind}]")
            sp = e["spoken"] if e["spoken"] and e["spoken"] != "—" else "unspoken"
            print(f"  {e['id']:<20} {short(e['title'], 34):<34} {e['tier']:<8} {short(sp, 44)}")
        return
    if what == "grep":
        if not arg:
            die("lore grep needs a word")
        q = arg.lower()
        hits = 0
        for e in entries.values():
            lines = [l for l in e["lines"] if q in l.lower() and not l.startswith("- **")]
            if q in e["title"].lower() or lines:
                hits += 1
                print(f"{e['id']} — {e['title']} · {e['tier']} · spoken: {e['spoken'] or '—'}")
                for l in lines[:2]:
                    print("   " + short(l.strip(), 140))
        if not hits:
            print(f"nothing in the Annals mentions {arg!r}; `/lore` may add a common entry, or leave it unsaid")
        return
    if what == "pick":
        if arg not in LORE_POOLS:
            die("lore pick saying|verse|maxim|rhyme")
        pool = lore_pool(entries, arg)
        if not pool:
            die(f"the Annals have no {arg} lines yet")
        for e, text, note in (pool if args.all else [random.choice(pool)]):
            text, note = (re.sub(r"\s*⟪[^⟫]*⟫", "", x).strip() for x in (text, note))  # a GM aside never reaches a glimpse
            print(text + (f"  ({note})" if note else ""))
            print(f"  — {e['id']} · {e['title']} · spoken: {e['spoken'] or '—'}")
        return
    if what == "spoke":
        if not arg or arg not in entries:
            die(f"lore spoke <id> --where chNN:sK; ids: {', '.join(list(entries)[:8])}…")
        if not args.where:
            die("--where is required (chNN:sK, chNN:climax, chNN:between-K, Prologue II, glimpse)")
        old, joined = lore_spoke(arg, args.where)
        print(f"{arg} spoken: {old or '—'} → {joined}; its reader-safe line goes to the Codex through `record` (a codex item)")
        return
    e = entries.get(what)
    if not e:
        hint = ", ".join(k for k in entries if k.startswith(what.split(".")[0])) or ", ".join(list(entries)[:10])
        die(f"no entry `{what}` in the Annals; try: {hint}")
    print(f"## {e['id']} — {e['title']}")
    print("\n".join(e["lines"]).strip())


# ---------------------------------------------------------------- names on the page
NAME_STOP = set("""I Ser Dame Captain Mender Menders Sister Brother Mother Father Prior Saint Lord Lady King Queen Knight Knights
Confessor Confessors Herald Heralds Grace Ember Reckoning Binding Knot Knots Art Arts Steps Stone Crown Hollowed Faithless
Lance Lances Oathstone Oathstones Oathsworn Warden Wardens Emberwardens Vaelish Vaelmark First Second Third Fourth Fifth Sixth
Seventh Eighth Ninth Tenth Eleventh Twelfth Book Chapter Scene Interlude Between Climax Choice Level Might Vigor Finesse Resolve""".split())


def registered_names():
    """Every capitalised word a registry knows, lowercased: codex.md, cast.md, the Annals, character names and aliases,
    place and faction names and aliases, and the game's own words (Arts, Knots, ranks, Ember tiers, the Tether, the Bearing)."""
    words = set()

    def add(t):
        words.update(w.lower() for w in re.findall(r"[A-Z][a-z]+", str(t or "")))

    for key in ("codex", "cast", "lore"):
        if P[key].exists():
            add(P[key].read_text(encoding="utf-8"))
    for f in sorted(P["characters"].glob("*.json")):
        try:
            c = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for s in [c.get("name"), c.get("epithet")] + list(c.get("aliases") or []):
            add(s)
    for key, field in (("places", "places"), ("factions", "factions")):
        try:
            for x in json.loads(P[key].read_text(encoding="utf-8")).get(field, []):
                for s in [x.get("name"), x.get("subtitle")] + list(x.get("aliases") or []):
                    add(s)
        except (OSError, ValueError):
            pass
    try:
        rules = json.loads(P["rules"].read_text(encoding="utf-8"))
        for a in rules.get("arts", []) + rules.get("sport_arts", {}).get("arts", []):
            add(a.get("name")); add(a.get("tree"))
        for k in rules.get("knots", []):
            add(k.get("name"))
        for r in rules.get("levels", {}).get("ranks", []):
            add(r.get("name"))
        for t in rules.get("ember", {}).get("tiers", []):
            add(t.get("name"))
        for nm in rules.get("tether", {}).get("names", []):
            add(nm)
    except (OSError, ValueError):
        pass
    try:
        b = json.loads(P["bearing"].read_text(encoding="utf-8"))
        for ax in b.get("axes", {}).values():
            add(ax.get("left")); add(ax.get("right"))
        for v in b.get("names", {}).values():
            add(v)
    except (OSError, ValueError):
        pass
    return words


def gm_unspoken_names():
    """Capitalised words the GM files use (the arc, the characters, the world, the Annals, the design, the notes, the threads)
    that no reader-safe registry knows and the page has never spoken: the names a block or a glimpse must never carry.
    A word that the GM files also use in lowercase is a common noun, not a name (the site build draws the same line)."""
    texts = []
    gm_dir = ROOT / "saga/bible/_gm"
    for p_ in sorted(gm_dir.glob("*.md")) if gm_dir.exists() else []:
        texts.append(p_.read_text(encoding="utf-8"))
    for row in R.load_notes() + R.load_tale_notes():
        texts.append(json.dumps(row, ensure_ascii=False))
    if P["threads"].exists():
        texts.append(P["threads"].read_text(encoding="utf-8"))
    gm_text = "\n".join(texts)
    page = "\n".join(p_.read_text(encoding="utf-8") for p_ in sorted(P["chronicle"].glob("*.md")) + sorted(P["tales_dir"].glob("*.md"))).lower()
    page_words = set(re.findall(r"[a-z]+", page))
    lower_words = set(re.findall(r"\b[a-z]{3,}\b", gm_text))
    reg = registered_names()
    out = set()
    for w in set(re.findall(r"\b[A-Z][a-z]{2,}\b", gm_text)):
        if w in NAME_STOP or w.lower() in reg or w.lower() in page_words or w.lower() in lower_words or w.lower().rstrip("s") in reg:
            continue
        out.add(w)
    return out


def name_problems(text, registered, allow=(), label="the block"):
    """(refusals, notes) for a text's capitalised words: a name the GM files know and the page has not spoken is refused
    (it would leak), any other unregistered word is noted (register it, or it is not a name)."""
    found = {w for w in names_in_text(text, registered) if w not in set(allow)}
    gm = gm_unspoken_names()
    leaks = sorted(w for w in found if w in gm)
    others = sorted(w for w in found if w not in gm)
    refusals, notes = [], []
    if leaks:
        refusals.append(f"{label} names {', '.join(leaks)}, which the page has not spoken and the GM files know: nothing the page has not said may reach it")
    if others:
        notes.append(f"note: {label} has capitalised words no registry knows: {', '.join(others)}: a coinage gets a codex item or a character file; a common noun needs nothing")
    return refusals, notes


def names_in(path, registered):
    """Capitalised words in a chapter file that appear at least once mid-sentence and that no registry knows."""
    return names_in_text(path.read_text(encoding="utf-8"), registered)


def names_in_text(text, registered):
    found = {}
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith(("#", ">", "`")):
            continue
        for m in re.finditer(r"(?<![\w'’])([A-Z][a-z]{2,})(?![\w])", line):
            before = line[: m.start()].rstrip()
            if not before or before[-1] in '.!?"“”‘’*>—–-([:;':
                continue  # a sentence start proves nothing
            w = m.group(1)
            if w in NAME_STOP or w.lower() in registered or w.rstrip("s") in NAME_STOP or w.lower().rstrip("s") in registered:
                continue
            found[w] = found.get(w, 0) + 1
    return found


def unregistered_names(world, all_chapters=False):
    """[(file, {name: count})] for the current chapter, or every chapter with --all."""
    reg = registered_names()
    if all_chapters:
        files = sorted(P["chronicle"].glob("*.md"))
    else:
        cf = world.get("chapter_file")
        files = [ROOT / cf] if cf and (ROOT / cf).exists() else []
    return [(f, names_in(f, reg)) for f in files]


def cmd_names(args):
    st = State()
    rows = unregistered_names(st.world, all_chapters=args.all)
    clean = True
    for f, found in rows:
        if found:
            clean = False
            print(f"{rel(f)}: " + ", ".join(f"{w} ×{n}" if n > 1 else w for w, n in sorted(found.items())))
    if clean:
        print("every capitalised name on the page is registered (codex, cast, places, factions, the Annals)")
    else:
        print("register each: codex.md (a thing, a saying, a song), saga/characters/ (a person), places.json, factions.json, or the Annals (`lore`)")


# ---------------------------------------------------------------- the chapter file
SCENE_HEAD_RE = re.compile(r"^###\s+Scene\s+(\d+)\s*[—–-]\s*(.+)$")
INTERLUDE_HEAD_RE = re.compile(r"^###\s+Interlude\s*[—–-]\s*(.+)$")
BETWEEN_HEAD_RE = re.compile(r"^###\s+Between\s*[—–-]\s*(.+)$")
CLIMAX_HEAD_RE = re.compile(r"^##\s+Climax\s*[—–-]\s*(.+)$")
CHOICE_HEAD_RE = re.compile(r"^###\s+Choice\s*[—–-]\s*(.+)$")


def chapter_blocks(world):
    """The current chapter file's scene-like blocks in order, as [(key, title, words)] with build_site's keys
    ('1', 'interlude', 'interlude-2', 'between-1', 'climax', 'choice'); words counts every line under the heading
    up to the next one. None when the file is missing."""
    cf = world.get("chapter_file")
    path = ROOT / cf if cf else None
    if not path or not path.exists():
        return None
    out, n_int, n_btw = [], 0, 0
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        key = title = None
        m = SCENE_HEAD_RE.match(s)
        if m:
            key, title = m.group(1), m.group(2)
        elif INTERLUDE_HEAD_RE.match(s):
            n_int += 1
            key, title = ("interlude" if n_int == 1 else f"interlude-{n_int}"), INTERLUDE_HEAD_RE.match(s).group(1)
        elif BETWEEN_HEAD_RE.match(s):
            n_btw += 1
            key, title = f"between-{n_btw}", BETWEEN_HEAD_RE.match(s).group(1)
        elif CLIMAX_HEAD_RE.match(s):
            key, title = "climax", CLIMAX_HEAD_RE.match(s).group(1)
        elif CHOICE_HEAD_RE.match(s):
            key, title = "choice", CHOICE_HEAD_RE.match(s).group(1)
        if key is not None:
            out.append([key, title.strip(), 0, False])
        elif out and s:
            out[-1][2] += len(s.split())
            if s.startswith("**What does Darrow"):
                out[-1][3] = True  # a small choice: the scene may run to 800 (style.md §3)
    return [tuple(b) for b in out]


def chapter_headings(world):
    """[(key, title)] of the current chapter file's scene-like headings; None when the file is missing."""
    blocks = chapter_blocks(world)
    return None if blocks is None else [(k, t) for k, t, _, _ in blocks]


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


# ---------------------------------------------------------------- commands: devices (design §5.6)
def cmd_challenge(args):
    st = State()
    s = slot_by_n(st.plan, args.n)
    c = s.get("challenge")
    if not c:
        die(f"slot {s['n']} has no challenge (`plan slot {s['n']} challenge='{{…}}'`; the shape is in design.md §5.6)")
    if args.action == "show":
        print_challenge(s)
        return
    if args.action == "void":
        c["status"], c["why"] = "void", args.why or ""
    else:
        if c.get("status") != "open":
            die(f"the challenge in slot {s['n']} is {c.get('status')}")
        key = "progress" if args.action == "success" else "strain"
        c[key] = int(c.get(key, 0)) + 1
        if int(c.get("progress", 0)) >= int(c.get("goal", 1)):
            c["status"] = "won"
        elif int(c.get("strain", 0)) >= int(c.get("limit", 1)):
            c["status"] = "lost"
    print_challenge(s)
    if c["status"] in ("won", "lost"):
        print(f"  resolved: {c['status']}. Record what it changed with `saga.py add` (a flag, approval, a due item); a lost one is a cost or a turn, never a wall")
    st.touch("plan")
    st.save()


def cmd_invite(args):
    st = State()
    s = slot_by_n(st.plan, args.n)
    inv = s.get("invite")
    if not inv:
        die(f"slot {s['n']} has no invitation (`plan slot {s['n']} invite='{{…}}'`; the shape is in design.md §5.6)")
    if args.action == "show":
        print_invite(s)
        return
    if inv.get("status") != "waiting":
        die(f"the invitation in slot {s['n']} is already {inv.get('status')}")
    inv["status"] = "taken" if args.action == "take" else "passed"
    if args.action == "take":
        print(f"invite slot {s['n']} taken: the Between opens on {inv.get('who')}'s first line, not Darrow's; his answer goes through the ledger like any Between")
    else:
        print(f"invite slot {s['n']} passed: the next scene opens on it in a clause: {inv.get('if_ignored')}")
    st.touch("plan")
    st.save()


def cmd_project_quest(args):
    st = State()
    q = st.plan.get("quests", {}).get(args.id)
    if not q:
        die(f"no quest {args.id} in plan.json")
    if not q.get("project"):
        die(f"{args.id} is not a project quest (`plan quest {args.id} project=true`; design §5.6)")
    if args.action == "work":
        if not args.where or not WHERE_RE.match(args.where):
            die("--where must be a position like ch02:between-1 or ch02:s3")
        if not args.what:
            die("--what says what hand he laid on it")
        q.setdefault("work", []).append({"where": args.where, "what": args.what})
        st.touch("plan")
        st.save()
        print(f"{args.id}: work noted at {args.where}; the next stage's scene shows it")
    total = arc_quest_stage_count(args.id)
    if q.get("gate"):
        g_state, g_detail = gate_state(q["gate"], st)
        print(f"gate: {q['gate']} · {g_state}" + (" (locked)" if g_state != "MET" else "") + (f" · {g_detail}" if g_detail else ""))
    print(f"{args.id} · {q.get('status')} · stage {q.get('stage', 0)}" + (f"/{total}" if total else "") + f" · work noted: {len(q.get('work', []))}")
    for w in q.get("work", []):
        print(f"  {w.get('where')}: {w.get('what')}")
    entry = next((p_ for p_ in st.world.get("projects", []) or [] if p_.get("id") == args.id), None)
    if entry:
        print(f"  on the page: stage {entry.get('stage')}/{entry.get('of')} · {entry.get('visible')}")
    else:
        print("  not yet on the page (world.json → projects[] once its first stage is written)")


# ---------------------------------------------------------------- check & fmt
def check_records(st, probs, notes):
    plan, pos = st.plan, st.plan.get("position", {})
    try:
        evs = R.load_events()
        R.load_notes()
    except ValueError as e:
        probs.append(str(e))
        return
    files = R.chapter_files()
    char_ids = set(R.char_files())
    seen, cache = {}, {}
    for ev in evs:
        key = ev.get("key")
        parsed = R.parse_key(key)
        if not parsed:
            probs.append(f"event key {key!r} malformed (ch02:s4, ch02:between-9, ch02:interlude, ch02:climax, ch02:choice, ch00:II)")
            continue
        seen[key] = seen.get(key, 0) + 1
        ch, sk, kind = parsed
        if ch not in files:
            probs.append(f"event {key}: no chronicle file for chapter {ch}")
            continue
        blocks = cache.setdefault(ch, {k: t for k, t, _ in R.blocks_of(files[ch])})
        if sk not in blocks:
            probs.append(f"event {key}: {files[ch].name} has no such block")
        elif norm_title(ev.get("title")) != norm_title(blocks[sk]):
            probs.append(f"event {key}: title {ev.get('title')!r}, but the heading says {blocks[sk]!r} (re-record it with --force)")
        for p in ev.get("people") or []:
            if p.get("id") not in char_ids:
                probs.append(f"event {key}: people id {p.get('id')!r} has no character file")
        if kind == "scene" and not ev.get("date") and ch == int(pos.get("chapter", 0)):
            notes.append(f"event {key}: no date (the day the scene covers)")
    for k, n in seen.items():
        if n > 1:
            probs.append(f"event {k} is recorded {n} times")
    cur = int(pos.get("chapter", 0))
    if cur in files:
        for k, t, _ in R.blocks_of(files[cur]):
            if R.make_key(cur, k) not in seen:
                probs.append(f"{files[cur].name} has `{t}` ({k}) but no event: `saga.py record '<json>'` (the page is not recorded until it is)")
    try:
        thr = R.load_threads()
        tids = {}
        for t in thr.get("threads", []):
            tids[t.get("id")] = tids.get(t.get("id"), 0) + 1
            if t.get("status") not in ("open", "paid"):
                probs.append(f"thread {t.get('id')}: status {t.get('status')!r} must be open or paid")
            if not str(t.get("title") or "").strip():
                probs.append(f"thread {t.get('id')}: no title")
        for i, n in tids.items():
            if n > 1:
                probs.append(f"thread id {i} appears {n} times")
        if P["codex_json"].exists() and P["codex_json"].read_text(encoding="utf-8") != dumps(load_json(P["codex_json"])):
            probs.append(f"{rel(P['codex_json'])} is not in canonical format; run `saga.py fmt`")
    except (OSError, ValueError, json.JSONDecodeError) as e:
        probs.append(f"threads/codex store unreadable: {e}")
    try:
        for f in R.project_all(plan, write=False):
            probs.append(f"{f} is stale against the records: run `saga.py project` (a projection is never edited by hand; the records are)")
    except Exception as e:  # a projection that cannot be built is a problem, never a traceback
        probs.append(f"projections cannot be rebuilt: {e}")


def cmd_fmt(args):
    for k in STATE_FILES + ("codex_json", "threads"):
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
        for w in (r.get("fired") or []):
            if not WHERE_RE.match(str(w)):
                probs.append(f"rule {r.get('id')}: fired position {w!r} malformed")
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
    live = [q for q in plan.get("quests", {}).values() if q.get("status") == "live" and not q.get("standing") and not q.get("project")]
    if len(live) > 2:
        probs.append(f"{len(live)} quests live; never more than two (a `standing` quest, the Tether, and the Book's `project` quest are not counted)")
    peak, where = quest_live_peak(plan)
    if peak > 2 and where:
        probs.append(f"the chapter's plan makes {len(where[1])} quests live at once at slot {where[0]} ({', '.join(where[1])}); never more than two: "
                     f"finish one before the next opens, or move a stage to the next chapter (design §5.2)")
    if sum(1 for q in plan.get("quests", {}).values() if q.get("project") and q.get("status") in ("available", "live")) > 1:
        probs.append("more than one project quest available or live; one per Book (design §5.6)")
    for key, r in plan.get("route", {}).items():
        if not re.match(r"^book\d+$", key):
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
        if s.get("kind") == "quest" and plan.get("quests", {}).get(s.get("quest"), {}).get("standing") and s.get("status") in ("planned", "next"):
            with_ = "rae-thorne"
            her_place = character_place(with_)[0]
            if her_place and world.get("location", {}).get("place") and her_place != world["location"]["place"]:
                notes.append(f"slot {n} plans a stage of {s.get('quest')}, but by the page {with_} is at {her_place} and Darrow at {world['location']['place']}: the scene must bring them together first, or the stage waits for a slot where they are (design §8)")
        if s.get("float") and s.get("kind") != "quest":
            probs.append(f"slot {n} float is only for quest slots")
        ans = (s.get("micro") or {}).get("answer")
        if ans:
            key_ = micro_scene_key(plan, s)
            row_ = next((c for c in world.get("choices", []) if c.get("kind") == "micro" and int(c.get("chapter", -1)) == int(ch.get("number", -2)) and str(c.get("scene")) == str(key_)), None)
            if row_ is None:
                probs.append(f"slot {n}'s micro was answered (option {ans.get('option')}, by {ans.get('by')}) but world.json choices[] has no row for chapter {ch.get('number')} scene {key_}: record it through /choose (its ledger entry moves the Bearing)")
            elif row_.get("ledger") and not any(e.get("id") == row_["ledger"] for e in ledger.get("entries", [])):
                probs.append(f"slot {n}'s micro choice names ledger entry {row_['ledger']}, which the ledger does not have")
        if s.get("status") == "written" and not s.get("wrote"):
            probs.append(f"slot {n} written without wrote")
        m = s.get("micro")
        if m and m.get("beat"):
            # a folded core beat's own choice, carried by a daily scene (arc pacing): its options keep the arc's
            # weights, one pole per option at up to ±3, and it opens and closes like a micro
            opts = m.get("options") or []
            if not 2 <= len(opts) <= 3:
                probs.append(f"slot {n} beat choice needs 2–3 options")
            if m.get("default") not in range(1, len(opts) + 1):
                probs.append(f"slot {n} beat choice default {m.get('default')!r} not an option number")
            for b in (m.get("bearing") or []):
                if b:
                    if len(b) != 1:
                        probs.append(f"slot {n} beat choice option moves {len(b)} poles; one per option")
                    for pole, v in b.items():
                        if not pole_axis(bearing, pole):
                            probs.append(f"slot {n} beat choice moves unknown pole {pole!r}")
                        if not 1 <= abs(int(v)) <= 3:
                            probs.append(f"slot {n} beat choice moves {pole} by {v}; a folded beat keeps its climax weight, ±2 or ±3")
            if s.get("kind") != "spine":
                probs.append(f"slot {n} carries a beat choice but is {s.get('kind')}; only a spine slot carries a core beat's choice")
            if ws and s.get("day") == (ws + dt.timedelta(6)).isoformat():
                probs.append(f"slot {n} carries a beat choice on Saturday; it must resolve before the climax, so never the last day")
            micro_days.append(s)
        elif m:
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
    for s in slots:
        if s.get("status") in ("planned", "next") and not str(s.get("turn") or "").strip():
            notes.append(f"slot {s.get('n')} ({s.get('day') or 'interlude'}) has no turn ({TURN_HINT}): `plan slot {s.get('n')} turn=\"…\"`, or state one in a line before writing")
    # lengths are the story's to decide (style.md §3: a scene runs as long as its want, obstacle and turn need), so no length notes here
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
    # devices (design §5.6): one per slot, none on neighbouring days, the chapter's kinds capped and rotated;
    # and gated by the page: an Art the chronicle has named, a person with a character file who is alive, a quest gate that is met
    quests_ = plan.get("quests", {})
    # a standing quest's stages (the Tether) go in order, one scene each: stage I is the one that explains the thread
    for qid_, q_ in quests_.items():
        if not q_.get("standing"):
            continue
        expect = int(q_.get("stage") or 0) + 1
        for s in sorted([x for x in slots if x.get("kind") == "quest" and x.get("quest") == qid_ and x.get("status") in ("planned", "next") and x.get("day")], key=lambda x: x["day"]):
            got = int(s.get("stage") or 0)
            if got != expect:
                probs.append(f"slot {s.get('n')} plans {qid_} stage {got}, but the next stage to write is {expect}: the stages go in order, one scene each")
            expect += 1
    devices, kinds = [], {}
    arts_, spoken_ = art_names(), arts_spoken()
    for who_, rule_ in (plan.get("invite_rules") or {}).items():
        r_state, r_detail = gate_state(rule_, st)
        if r_state in ("MALFORMED", "UNKNOWN TERM"):
            probs.append(f"invite_rules.{who_} {rule_!r} {r_state}: {r_detail}")
    for qid, q in quests_.items():
        if q.get("gate"):
            g_state, g_detail = gate_state(q["gate"], st)
            if g_state in ("MALFORMED", "UNKNOWN TERM"):
                probs.append(f"quest {qid} gate {q['gate']!r} {g_state}: {g_detail}")
        for stg, expr in (q.get("stage_gates") or {}).items():
            g_state, g_detail = gate_state(expr, st)
            if g_state in ("MALFORMED", "UNKNOWN TERM"):
                probs.append(f"quest {qid} stage_gates.{stg} {expr!r} {g_state}: {g_detail}")
    for s in slots:
        n, dev = s.get("n"), []
        if s.get("micro"):
            dev.append("micro")
        c = s.get("challenge")
        if c is not None:
            dev.append("challenge")
            if not isinstance(c, dict):
                probs.append(f"slot {n} challenge must be an object (design §5.6)")
            else:
                if not str(c.get("objective") or "").strip():
                    probs.append(f"slot {n} challenge has no objective")
                apps = c.get("approaches") or []
                if not 1 <= len(apps) <= 3:
                    probs.append(f"slot {n} challenge needs 1–3 approaches")
                for a in apps:
                    if not isinstance(a, dict) or a.get("stat") not in STATS or not isinstance(a.get("dc"), int) or not 8 <= a["dc"] <= 20 or not str(a.get("name") or "").strip():
                        probs.append(f"slot {n} challenge approach {a!r}: needs name, stat in {STATS}, dc 8–20 (art optional)")
                        continue
                    if a.get("art"):
                        if a["art"] not in arts_:
                            probs.append(f"slot {n} challenge approach {a.get('name')!r}: no Art {a['art']!r} in rules.json")
                        elif a["art"] not in spoken_:
                            probs.append(f"slot {n} challenge approach {a.get('name')!r} uses {arts_[a['art']]}, which the page has not named yet: locked until it is taught or earned on the page (design §5.6)")
                unk = unknown_names_in([str(c.get("objective") or "")] + [str(a.get("name") or "") for a in apps if isinstance(a, dict)] + [str(v) for v in (c.get("result") or {}).values()])
                if unk:
                    notes.append(f"slot {n} challenge names {', '.join(sorted(unk))}, which no registry knows: nothing the page has not spoken may reach a scene")
                if not isinstance(c.get("goal"), int) or not 1 <= c["goal"] <= 4 or not isinstance(c.get("limit"), int) or not 1 <= c["limit"] <= 3:
                    probs.append(f"slot {n} challenge: goal 1–4 and limit 1–3")
                if c.get("status") not in CHALLENGE_STATUS:
                    probs.append(f"slot {n} challenge status {c.get('status')!r} not in {CHALLENGE_STATUS}")
        inv = s.get("invite")
        if inv is not None:
            dev.append("invite")
            if not isinstance(inv, dict):
                probs.append(f"slot {n} invite must be an object (design §5.6)")
            else:
                for k in ("who", "want", "if_ignored"):
                    if not str(inv.get(k) or "").strip():
                        probs.append(f"slot {n} invite has no {k}")
                if inv.get("kind") not in INVITE_KINDS:
                    probs.append(f"slot {n} invite kind {inv.get('kind')!r} not in {INVITE_KINDS}")
                if inv.get("status") not in INVITE_STATUS:
                    probs.append(f"slot {n} invite status {inv.get('status')!r} not in {INVITE_STATUS}")
                cid_, cstat = character_status(inv.get("who"))
                if cid_ is None:
                    probs.append(f"slot {n} invite from {inv.get('who')!r}: nobody on the page by that name (no saga/characters/ file); people not yet on the page cannot invite (design §5.6)")
                elif cstat != "alive":
                    probs.append(f"slot {n} invite from {cid_}, whose status is {cstat!r}: the invitation cannot come from them")
                if inv.get("status") == "waiting":
                    for hard, msg in invite_narrative_problems(inv, s, st):
                        (probs if hard else notes).append(f"slot {n} " + msg + ("" if hard else "") + (" (design §5.6)" if hard else ""))
                unk = unknown_names_in([str(inv.get("want") or ""), str(inv.get("if_ignored") or ""), str(inv.get("why_now") or "")])
                if unk:
                    notes.append(f"slot {n} invite names {', '.join(sorted(unk))}, which no registry knows: nothing the page has not spoken may reach a Between")
        if s.get("kind") == "quest" and quests_.get(s.get("quest"), {}).get("project"):
            dev.append("project")
        if s.get("kind") == "quest" and s.get("status") in ("planned", "next"):
            gate = quests_.get(s.get("quest"), {}).get("gate")
            if gate and gate_state(gate, st)[0] == "NOT MET":
                probs.append(f"slot {n} plans {s.get('quest')} stage {s.get('stage')} while its gate ({gate}) is not met: locked until the story gets there (design §5.6)")
            sg = stage_gate_for(quests_, s.get("quest"), s.get("stage"))
            if sg and gate_state(sg, st)[0] == "NOT MET":
                probs.append(f"slot {n} plans {s.get('quest')} stage {s.get('stage')} while its stage gate ({sg}) is not met: the sheet has the stage, the scene waits for the story (design §8)")
        if len(dev) > 1:
            probs.append(f"slot {n} carries {len(dev)} devices ({', '.join(dev)}); one at most (design §5.6)")
        if dev:
            devices.append((s.get("day"), dev[0], n))
            for k in dev:
                if k != "micro":
                    kinds[k] = kinds.get(k, 0) + 1
    dated = sorted([d for d in devices if d[0]], key=lambda d: d[0])
    for a_, b_ in zip(dated, dated[1:]):
        try:
            gap = (dt.date.fromisoformat(b_[0]) - dt.date.fromisoformat(a_[0])).days
        except ValueError:
            continue
        if gap < 2:
            probs.append(f"devices on neighbouring days: slot {a_[2]} ({a_[1]}) and slot {b_[2]} ({b_[1]}); never two in adjacent slots (design §5.6)")
    if kinds.get("challenge", 0) > 1:
        probs.append("more than one challenge in the chapter; one at most (design §5.6)")
    if kinds.get("invite", 0) > 2:
        probs.append("more than two invitations in the chapter (design §5.6)")
    if len(kinds) > 2:
        probs.append(f"the chapter carries {len(kinds)} device kinds ({', '.join(sorted(kinds))}); at most two of challenge, project, invite (design §5.6)")
    for k in sorted(kinds):
        if k in (ch.get("previous_devices") or []):
            probs.append(f"a {k} ran in the previous chapter too; a device kind rests a chapter (design §5.6)")
    # the Book's project on the page (world.json → projects[]) and the callback cap
    places_ = known_places()
    for pr in world.get("projects", []) or []:
        pid = pr.get("id")
        if pid not in quests_ or not quests_[pid].get("project"):
            probs.append(f"world.json projects[] {pid!r} is not a project quest in plan.json")
        if pr.get("place") not in places_:
            probs.append(f"world.json project {pid}: place {pr.get('place')!r} is not in places.json")
        elif not (places_.get(pr.get("place")) or {}).get("on_page"):
            probs.append(f"world.json project {pid}: place {pr.get('place')!r} is not on the page yet; a project lives only where the story has been")
        if not isinstance(pr.get("stage"), int) or not isinstance(pr.get("of"), int) or not 1 <= pr["stage"] <= pr["of"]:
            probs.append(f"world.json project {pid}: stage must be an int from 1 to of")
        if pr.get("status") not in ("live", "done"):
            probs.append(f"world.json project {pid}: status {pr.get('status')!r} must be live or done")
        if not str(pr.get("visible") or "").strip() or not str(pr.get("name") or "").strip():
            probs.append(f"world.json project {pid}: needs a name and a visible line in the page's words")
        for d_ in pr.get("decisions") or []:
            if not isinstance(d_, dict) or not WHERE_RE.match(str(d_.get("scene", ""))) or not str(d_.get("chose") or "").strip() or not isinstance(d_.get("stage"), int):
                probs.append(f"world.json project {pid}: decision {d_!r} needs stage (int), chose (text) and scene (chNN:sK)")
    for qid, q in quests_.items():
        if q.get("project") and int(q.get("stage") or 0) >= 1 and not any(p_.get("id") == qid for p_ in world.get("projects", []) or []):
            notes.append(f"project {qid} is at stage {q.get('stage')} but world.json → projects[] has no entry: the page's trace is missing")
    for e, it in pending_items(ledger):
        if it.get("at") == "later":
            unk = unknown_names_in(it.get("what"))
            if unk:
                notes.append(f"callback {it.get('id')} names {', '.join(sorted(unk))}, which no registry knows")
            if it.get("fits") is not None:  # a hand edit is checked the way `add` checks a new one
                tree = parse_rule(it["fits"]) if isinstance(it["fits"], str) else None
                if tree is None:
                    probs.append(f"callback {it.get('id')}: fits {it.get('fits')!r} is malformed")
                else:
                    unk_t = sorted({".".join(p) for p in rule_terms(tree) if not term_lookup(p, st)[0]})
                    if unk_t:
                        probs.append(f"callback {it.get('id')}: fits names unknown term(s) {', '.join(unk_t)}")
            if it.get("valid_until") is not None and not VALID_UNTIL_RE.match(str(it["valid_until"])):
                probs.append(f"callback {it.get('id')}: valid_until {it.get('valid_until')!r} is not a position (chNN, chNN:sN, chNN:climax, bookN, bookN:climax, transitionN, finale)")
            if it.get("priority") is not None and it["priority"] not in (1, 2, 3):
                probs.append(f"callback {it.get('id')}: priority {it.get('priority')!r} is 1, 2 or 3")
            if int(it.get("offered") or 0) >= 4:
                notes.append(f"callback {it.get('id')} offered {it['offered']} times unfired ({', '.join(it.get('offered_at') or [])}): rewrite it or void it at the checkpoint")
    later_n = sum(1 for e, it in pending_items(ledger) if it.get("at") == "later")
    if later_n > CALLBACK_CAP:
        notes.append(f"{later_n} callbacks waiting (cap {CALLBACK_CAP}): fire the ones that fit or void the stale ones at the checkpoint")
    # an *[Inspiration]* option spends through `choose`, which marks its entry: a choice's spend with no such entry behind it is a note
    sp_path = ROOT / "saga/state/spends.csv"
    if sp_path.exists():
        try:
            choice_spends = sum(1 for r in read_csv(sp_path) if str(r.get("reason", "")).startswith("choice "))
            marked = sum(1 for e in ledger.get("entries", []) if e.get("inspiration"))
            if choice_spends > marked:
                notes.append(f"{choice_spends - marked} Inspiration spend(s) for a choice with no ledger entry marked `inspiration`: a `choose` that stopped after spending; add its entry, or note the spend in spends.csv")
        except (OSError, ValueError):
            pass
    axes_touched = set()
    for s in micro_days:
        m_ = s.get("micro") or {}
        if m_.get("axis"):
            axes_touched.add(m_["axis"])
        for b in (m_.get("bearing") or []):  # a beat choice spans the axes its options move
            for pole in (b or {}):
                r = pole_axis(bearing, pole)
                if r:
                    axes_touched.add(r[0])
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
    # an *[Inspiration]* option is his to pick (it costs one): never a default, at the climax or in a slot's micro
    for p_i in [inspiration_default_problem(cl.get("options") or [], cl.get("default"), "chapter.climax")] + \
               [inspiration_default_problem((s.get("micro") or {}).get("options") or [], (s.get("micro") or {}).get("default"), f"slot {s.get('n')} micro") for s in slots if s.get("micro")]:
        if p_i:
            probs.append(p_i)
    oc = plan.get("open_choice")
    if oc:
        opts_ = oc.get("options") or []
        if not isinstance(opts_, list) or not 2 <= len(opts_) <= 3 or oc.get("default") not in range(1, len(opts_) + 1):
            probs.append("open_choice needs 2–3 options and a default among them")
        p_i = inspiration_default_problem(opts_ if isinstance(opts_, list) else [], oc.get("default"), "open_choice")
        if p_i:
            probs.append(p_i)
        carries = int(oc.get("carries") or 2)
        if int(pos.get("chapter", 0)) > int(oc.get("chapter", 0)) + 1:
            probs.append(f"the climax choice of chapter {oc.get('chapter')} is still open two chapters on: it resolves to its default, option {oc.get('default')}, by bearing (`saga.py choose --by bearing …`)")
        elif int(pos.get("chapter", 0)) > int(oc.get("chapter", 0)) and int(pos.get("next_scene", 1)) > carries + 1:
            probs.append(f"the climax choice of chapter {oc.get('chapter')} is still open after {carries} scenes of chapter {pos.get('chapter')}: it resolves to its default, option {oc.get('default')}, by bearing (`saga.py choose --by bearing …`), and its `### Choice` block is written then")
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

    # the records: every event parses, keys are unique and name a block with the same title, every person has a file,
    # the current chapter's blocks are all recorded, the threads are well formed, and every projection is fresh
    check_records(st, probs, notes)
    # the tales: every binding has its file and project, every piece its event (told in order, never ahead of its task),
    # the last piece its keepsake; a piece owed is a note (it is written in the session that reports the task)
    check_tales(st, probs, notes)

    # the Annals: parseable, unique ids, known kinds, tiers, a spoken field
    entries, dupes = lore_entries()
    for d_ in dupes:
        probs.append(f"lore.md: id {d_} appears twice")
    for e in entries.values():
        if not LORE_ID_RE.match(e["id"]):
            probs.append(f"lore.md: id {e['id']} is not kind.name with a known kind ({', '.join(sorted(set(k for k in LORE_ID_RE.pattern[2:].split(')')[0].split('|'))))})")
        if e["tier"] not in LORE_TIERS:
            probs.append(f"lore.md: {e['id']} tier {e['tier']!r} must be common or learned")
        if not e["spoken"]:
            probs.append(f"lore.md: {e['id']} has no **spoken:** field")
    # names on the page that no registry knows: a note, so a new coinage gets registered before it drifts
    for f, found in unregistered_names(world):
        if found:
            notes.append(f"names in {rel(f)} that no registry knows: " + ", ".join(sorted(found)) + " · register them (codex, characters, places, factions, the Annals) or `saga.py names`")

    # arc ids
    ids_in_arc = arc_ids()
    if ids_in_arc:
        wanted = set(plan.get("core_beats", {})) | set(plan.get("quests", {}))
        for k in plan.get("route", {}):
            n = k[4:]
            if plan["route"][k].get("road"):
                wanted.add(f"t{n}.{plan['route'][k]['road']}")
        for i in sorted(wanted):
            if re.match(r"^t\d+$", i):
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




# ---------------------------------------------------------------- the brief: what a block needs, before it is written
REGARD_WORDS = ((-25, "cold toward him"), (0, "wary of him"), (15, "civil with him"), (30, "warm toward him"), (50, "fond of him"), (101, "devoted to him"))


def regard_words(v):
    for lim, w in REGARD_WORDS:
        if int(v) < lim:
            return w
    return "devoted to him"


def cast_entries():
    """{name: {appearance, voice}} from saga/bible/cast.md."""
    out, cur = {}, None
    if not P["cast"].exists():
        return out
    for line in P["cast"].read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            cur = line[3:].strip()
            out[cur] = {"appearance": "", "voice": ""}
        elif cur and line.startswith("- **Appearance:**"):
            out[cur]["appearance"] = line[len("- **Appearance:**"):].strip()
        elif cur and line.startswith("- **Voice:**"):
            out[cur]["voice"] = line[len("- **Voice:**"):].strip()
    return out


def gm_character_lines(name):
    """The GM entry's drafting lines for a name: wants/fears/now/under pressure (never the hides: those stay on demand)."""
    path = ROOT / "saga/bible/_gm/characters.md"
    if not path.exists():
        return []
    lines, head, keep = [], None, False
    want = norm_title(name)
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("### "):
            head = line[4:].split(" — ")[0].split(" (")[0].strip()
            keep = norm_title(head) == want
            continue
        if line.startswith("## "):
            keep = False
        if keep and line.startswith(("- **Under pressure:**", "- **Wants:**", "- **Now:**", "- **Fears:**")):
            l = line[2:].strip()
            # only the tactic, the want, the fear and the now: what a person hides, carries or will do in a later Book stays on demand (`_gm/characters.md`)
            l = re.split(r"\s*\*\*(?!Wants:|Fears:|Now:|Under pressure:)[A-Z][^*]{0,40}:\*\*", l)[0].strip()
            lines.append(l)
    return lines


def people_index():
    """{id: file} and a name → id map from the character files (name, aliases, epithet words)."""
    files, by_word = R.char_files(), {}
    names = {}
    for cid, p in files.items():
        try:
            c = load_json(p)
        except (OSError, ValueError):
            continue
        names[cid] = c
        for s in [c.get("name")] + list(c.get("aliases") or []):
            for w in re.findall(r"[A-Z][a-z]{2,}", str(s or "")):
                if w in UP_SKIP:
                    continue
                by_word.setdefault(w, set()).add(cid)
    return names, by_word


def people_in(texts, names, by_word):
    """Character ids a text names (a word of their name or an alias), in order of first mention."""
    out = []
    for text in texts:
        for w in re.findall(r"[A-Z][a-z]{2,}", str(text or "")):
            for cid in sorted(by_word.get(w, ())):
                if cid not in out:
                    out.append(cid)
    return out


def person_brief(cid, c, world, cast, thr_rows=None, facts_n=2):
    """One person for the brief: voice, under pressure, regard, now, their last facts, what they know on the touched threads."""
    name = c.get("name") or cid
    key = cid.split("-")[0]
    comp = (world.get("companions") or {}).get(key)
    lines = [f"· {name}" + (f" ({regard_words(comp.get('approval', 0))}, approval {comp.get('approval')})" if comp else "") + (f" · status {c.get('status')}" if c.get("status") not in (None, "alive") else "")]
    ce = cast.get(name) or {}
    if ce.get("voice"):
        lines.append(f"  voice: {ce['voice']}")
    for l in gm_character_lines(name):
        lines.append(f"  {l}")
    if c.get("last_seen_doing"):
        lines.append(f"  last seen: {c['last_seen_doing']} ({(c.get('last_seen') or {}).get('scene')}, {(c.get('last_seen') or {}).get('place')})")
    if c.get("now"):
        lines.append(f"  now: {short(c['now'], 260)}")
    facts = c.get("known_facts") or []
    present = [f for f in facts if not str(f.get("chapter") or "").startswith("tale")]
    past = [f for f in facts if str(f.get("chapter") or "").startswith("tale")]
    for f in present[-facts_n:]:
        lines.append(f"  fact ({f.get('scene')}): {short(f.get('fact'), 160)}")
    if past:  # the tales' facts never crowd the present out: one line, the latest, and where the rest are
        lines.append(f"  the past, from the tales ({len(past)} fact{'s' if len(past) != 1 else ''}; `history --person {cid}`): {short(past[-1].get('fact'), 140)}")
    for t in thr_rows or []:
        if name.split()[-1].lower() in str(t.get("who_knows") or "").lower() or name.split()[0].lower() in str(t.get("who_knows") or "").lower():
            lines.append(f"  knows (thread {t['id']}): {short(t.get('who_knows'), 160)}")
    return lines


def knee_line(rules):
    try:
        sheet = load_json(P["sheet"])
        tied = int(sheet.get("knots_count") or 0)
    except (OSError, ValueError, json.JSONDecodeError):
        return None
    kn = next((k for k in rules.get("knots", []) if int(k.get("n", 0)) == tied), None)
    return f"Knots tied {ROMAN[tied]}: {kn.get('allows')}" if kn and kn.get("allows") else None


def betweens_since_last_scene(st):
    """[(event, [ledger chose lines])] for the Betweens written after the last scene of the current chapter."""
    plan, ledger = st.plan, st.ledger
    ch = int(plan["position"]["chapter"])
    evs = [e for e in R.load_events(ch)]
    last_scene = max((i for i, e in enumerate(evs) if e.get("kind") == "scene"), default=-1)
    out = []
    for e in evs[last_scene + 1:]:
        if e.get("kind") != "between":
            continue
        made = [x for x in ledger.get("entries", []) if int((x.get("made") or {}).get("chapter", -1)) == ch and str((x.get("made") or {}).get("scene")) == e.get("scene")]
        out.append((e, [x.get("chose") for x in made]))
    return out


def threads_for_brief(ch, cap=6):
    thr = R.load_threads()
    rows = [t for t in thr.get("threads", []) if t.get("status") == "open"]
    touched = [t for t in rows if any(k.startswith(f"{ch:02d}:") for k in t.get("on_page") or [])]
    rest = [t for t in rows if t not in touched]
    rest.sort(key=lambda t: len(t.get("on_page") or []))
    return (touched + rest)[:cap], len(rows)


def thread_line(t):
    n = len(t.get("on_page") or [])
    state = "may reveal (two plants on the page)" if n >= 2 else ("one plant: plant again before any reveal" if n == 1 else "unplanted: plant only")
    return f"· thread {t['id']} ({t.get('truth') or '—'}, {n} on the page, last {(t.get('on_page') or ['—'])[-1]}; {state}): {short(t.get('title'), 120)}\n    who knows: {short(t.get('who_knows'), 170)}"


def lore_for_brief(texts, cap=3):
    """Entries the slot names as lore:<id>, printed in full (capped), and the ids of the Annals' index for the rest."""
    entries, _ = lore_entries()
    ids = []
    for text in texts:
        for m in re.finditer(r"lore:([a-z]+\.[a-z0-9_]+)", str(text or "")):
            if m.group(1) in entries and m.group(1) not in ids:
                ids.append(m.group(1))
    out = []
    for lid in ids[:cap]:
        e = entries[lid]
        body = [l for l in e["lines"] if not l.startswith("- **")]
        out.append(f"· {lid} — {e['title']} ({e['tier']}; spoken: {e['spoken'] or 'never'})")
        out += ["    " + l for l in body if l.strip()][:8]
    return out


def callbacks_for_brief(st, ctx=None, cap=4):
    """The callbacks that fit this block, the way Hades picks a line: eligible first (`fits` against who is here and where),
    then by priority, then by how specific the fit is, then the oldest; the rest are counted, never listed."""
    rows = [(e, it) for e, it in pending_items(st.ledger) if it.get("at") == "later"]
    fitting, waiting = [], 0
    for i, (e, it) in enumerate(rows):
        ok, spec = callback_fits(it, st, ctx or {})
        if ok:
            fitting.append((-int(it.get("priority") or 2), -spec, i, it))
        else:
            waiting += 1
    fitting.sort(key=lambda t: t[:3])
    out = []
    for *_, it in fitting[:cap]:
        tags = [t for t in (f"priority {it['priority']}" if it.get("priority") else None,
                            f"offered {it['offered']}× unfired" if int(it.get("offered") or 0) >= 2 else None,
                            f"until {it['valid_until']}" if it.get("valid_until") else None) if t]
        out.append(f"· {it['id']}" + (f" ({' · '.join(tags)})" if tags else "") + f": {short(it.get('what'), 170)}")
    if len(fitting) > cap:
        out.append(f"  (+{len(fitting) - cap} more that fit here: `saga.py due --later`)")
    if waiting:
        out.append(f"  (+{waiting} wait for other company or places: `saga.py due --later`)")
    return out


# the kinds of check a climax plan names, as `darrow.py roll` takes them (Insight = Resolve + proficiency + Warden's Eye)
CHECK_KINDS = {"insight": ("resolve", True, "wardens_eye"), "might": ("might", False, None), "vigor": ("vigor", False, None),
               "finesse": ("finesse", False, None), "resolve": ("resolve", False, None)}


def darrow_odds(extra):
    """`darrow.py odds --json …` as a dict, or None when the engine refuses (an Art not learned, a chapter not frozen)."""
    r = subprocess.run([sys.executable, str(ROOT / "engine/darrow.py"), "odds", "--json"] + [str(x) for x in extra],
                       cwd=ROOT, capture_output=True, text=True)
    if r.returncode:
        return None
    try:
        return json.loads(r.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return None


def odds_line(label, extra, dc=None):
    """One line of odds for a check: his total modifier and, for `dc` (or the target DC the extra args asked for), the
    chance of a full success, a partial and an outright failure. An Art he has not learned falls back to the bare stat."""
    o = darrow_odds(extra)
    if o is None and "--art" in extra:
        i = extra.index("--art")
        o = darrow_odds(extra[:i] + extra[i + 2:])
    if o is None:
        return f"  {label}: odds unavailable (`darrow.py odds {' '.join(str(x) for x in extra)}`)"
    dc = dc if dc is not None else o.get("target_dc")
    row = (o.get("rows") or {}).get(str(dc))
    if not row:
        return f"  {label} ({o['mods_text']} = {o['mods']:+d}): DC {dc} is outside the table (`darrow.py odds --dc {dc} …`)"
    verb = "use DC" if dc == o.get("target_dc") and o.get("target") is not None else "DC"
    return f"  {label} ({o['mods_text']} = {o['mods']:+d}): {verb} {dc} → success {row['success']:.0%} · partial {row['partial']:.0%} · fail {row['failure']:.0%}", o


def climax_odds_lines(ch, checks, rules, frozen):
    """The climax's dice before they are cast: for every kind of check, his modifier under the frozen tier and Ember
    and the DC at which a full success has the tier's chance (rules.json → week_score.tiers[].target_odds), with what
    the planned DC would give beside it. The tier's roll modifier stays in the dice line; the DC is what answers it."""
    tiers = {t["name"]: t for t in rules.get("week_score", {}).get("tiers", [])}
    tier_name = frozen.get("tier") if frozen else None
    target = (tiers.get(tier_name) or {}).get("target_odds") if tier_name else None
    if target is None:
        return ["odds: the DCs are set once `darrow.py chapter-close` freezes the tier (`darrow.py odds --chapter N --target P`); until then plan them as written"]
    planned = {}
    for text in checks:
        m = re.match(r"^\s*(insight|might|vigor|finesse|resolve)\b.*?DC\s*(\d+)", str(text), re.I)
        if m:
            planned.setdefault(m.group(1).lower(), []).append(int(m.group(2)))
    out = [f"odds ({tier_name}: each check's DC is set so a full success has a {target:.0%} chance; the dice line keeps the tier's modifier; partial = within 3, success at a cost; the planned DCs are advisory):"]
    for kind, (stat, prof, art) in CHECK_KINDS.items():
        extra = ["--stat", stat, "--chapter", ch, "--target", target] + (["--prof"] if prof else []) + (["--art", art] if art else [])
        got = odds_line(kind, extra)
        if isinstance(got, str):
            out.append(got)
            continue
        line, o = got
        for pdc in planned.get(kind, []):
            row = (o.get("rows") or {}).get(str(pdc))
            if row and pdc != o.get("target_dc"):
                line += f" · planned DC {pdc} would be {row['success']:.0%}"
        out.append(line)
    return out


def format_lines(kind, slot=None):
    if kind == "scene":
        out = ["heading: `### Scene N — Title` appended to the chapter file (N is the key's number)",
               "a die, only with stakes: `python3 engine/darrow.py roll chNN-sK-<slug> --stat <might|vigor|finesse|resolve> --dc <8–20> [--prof] [--art <id>] [--adv|--dis]`; paste its first line as printed, on its own line, before the outcome",
               "the Reckoning box at the end, only when sync reported a change: `> ⟦ THE RECKONING ⟧` then one line per change (`> Might 11 → 12`, `> Level 5 → 6 · Kindled`, `> The Tether: **a name**.`, `> Rank: **Kindled**.`)"]
        if slot and slot.get("micro"):
            out.append("ends on the small choice, exactly: `**What does Darrow say?**` (or do?) then `1. **…**` `2. **…**` `3. **…**`, one line each, nothing after it")
        return out
    if kind == "between":
        return ["heading: `### Between — Title` appended after the last block; close third on Darrow, past tense; 300–500 words unless the exchange needs more",
                "zero or one die, only with stakes or a game: `python3 engine/darrow.py roll chNN-between-K-<slug> --stat … --dc …` (never --chapter or --tier); its first line pasted as printed",
                "no Reckoning box, no choice list; it ends on a line that hands the moment back (a look, a bell, a door, a last word)"]
    if kind == "climax":
        return ["heading: `## Climax — Title`; 900–1,800 words, the space on the decision and its cost",
                "2–4 dice at the moments of real stakes: `python3 engine/darrow.py roll chNN-<slug> --stat … --dc … [--prof] [--art <id>] --chapter N`; each first line pasted as printed",
                "ends on the choice, exactly: `**What does Darrow do?**` then `1. **…**` `2. **…**` `3. **…**`, a gate in brackets (`*[Resolve 10]*`, `*[Guile 1]*`, `*[Inspiration]*` for a bold way or a reroll that costs one), struck through if unmet, who approves in italics; the default never carries `*[Inspiration]*`",
                "the Reckoning box before the choice if sync reported a change"]
    if kind == "choice":
        return ["heading: `### Choice — Title` appended to the climax's chapter file; 100–250 words: the moment the choice lands, companions reacting in voice by their under-pressure lines; approval shows in what they say, never as numbers",
                "a Book's last climax: this block is the crossing itself (`saga.py arc tN.<road>`), as long as it needs"]
    if kind == "tale":
        return ["heading: `### Piece K — Title` appended to the tale's file (K is the key's number); 400–700 words, past tense, close third on the tale's own person",
                "a whole small story each time: a want, a turn, a last image; the piece may end on the line the present will rhyme with, never on a lesson",
                "no dice, no choice list, no Reckoning box; the present never intrudes except as an echo the reader can feel",
                "the last piece ends on the keepsake in the page's words (the thing, the name, the song or the saying); the record names it"]
    return []


def record_skeleton(key, kind, date, people_ids, place, extra=None):
    ev = {"key": key}
    if kind == "scene":
        ev["date"] = date
    ev.update({"where": {"place": place, "detail": "<where in it he is at the end>"}, "time": "<story time>",
               "last_beat": "<the last beat, one or two sentences, the page's words>",
               "people": [{"id": cid, "did": "<one line>", "now": "<1–3 sentences, as far as the reader knows>", "facts": [{"fact": "<one sentence>", "evidence": "<verbatim words of the block>"}]} for cid in people_ids]
               + [{"id": "<only named>", "mention": True}],
               "codex": [{"section": "Places and things", "name": "<new thing>", "text": "<what it is (Ch N Sc K)>"}],
               "lore": [], "threads": [{"id": 0, "how": "plant|touch|payoff"}],
               "fired": [{"id": "<a due item, callback or rule id this block pays>", "evidence": "<verbatim words of the block that pay it>"}], "voided": [],
               "struggle": None, "quest": None, "season": None, "inventory": None, "tether": None, "rank": None,
               "now": {"against": "<one line>", "next": "<one line, spoiler-free>"},
               "gm": {"note": "<what the block did for the plan; what was kept off the page>", "next_must_know": "<what the next block must honour>",
                      "threads": [{"id": 0, "who_knows": "<updated>", "note": "<updated>"}]}})
    if kind == "scene":
        ev["micro_opened"] = False
    if kind == "climax":
        ev["choice"] = {"ask": "What does Darrow do?", "options": ["<option 1 as written>", "<option 2>", "<option 3>"], "default": 1}
        ev["recap"] = "<one spoiler-free line for the top of this chapter in the reader>"
        ev["story_so_far"] = {cid: "<2–5 sentences, spoiler-free, for the chapter just closed>" for cid in people_ids[:3]}
    if kind == "between":
        ev["invite"] = {"slot": "<N if this Between answers slot N's invitation>", "action": "take"}
    if extra:
        ev.update(extra)
    return ev


def cmd_brief(args):
    st = State()
    plan, world, ledger, bearing = st.plan, st.world, st.ledger, st.bearing
    rules = load_json(P["rules"])
    pos = plan["position"]
    ch = int(pos["chapter"])
    cast = cast_entries()
    names, by_word = people_index()
    try:
        sheet = load_json(P["sheet"])
    except (OSError, ValueError, json.JSONDecodeError):
        sheet = {}
    if getattr(args, "tale", False):
        return brief_tale(st, args)
    L = []
    mode = "chapter" if args.chapter else "climax" if args.climax else "choice" if args.choice else "between" if args.between else "slot"

    def section(title):
        L.append("")
        L.append(f"== {title} ==")

    # ---------------- the header: where the story stands
    evs = R.load_events(ch)
    last = evs[-1] if evs else None
    files = R.chapter_files()
    L.append(f"BRIEF · Book {ROMAN[int(pos['book'])]} · Chapter {ch} — {world.get('chapter_title', '')} · {kl}" if (kl := knot_line(plan)) else f"BRIEF · Book {ROMAN[int(pos['book'])]} · Chapter {ch} — {world.get('chapter_title', '')}")
    L.append(f"chapter question: {plan['chapter'].get('question')}")
    tier = (sheet.get("chapter_now") or {}).get("tier_so_far")
    L.append(f"the week so far: {tier or '—'} (colour and tier are GM-only; the page never says them) · Ember {(sheet.get('ember') or {}).get('tier', '—')} · {bearing_line(bearing)}")

    # ---------------- which block
    key = slot = None
    if mode == "slot":
        slot = next_slot(plan, args.date)
        if not slot:
            die("no slot to write: `plan chapter open` first (or `brief --between` for a Between)")
        if slot.get("kind") == "interlude":
            n_int = sum(1 for e in evs if e.get("kind") == "interlude")
            key = f"{ch2(ch)}:interlude" + (f"-{n_int + 1}" if n_int else "")
            kind = "interlude"
        elif slot.get("kind") == "cutaway":
            key, kind = f"{ch2(ch)}:s{pos['next_scene']}", "scene"
        else:
            key, kind = f"{ch2(ch)}:s{pos['next_scene']}", "scene"
        L.append(f"THIS BLOCK: {key} · {slot_label(slot)} · {slot.get('status')}" + (f" · colour {colour_for(slot['day'])}" if slot.get("day") else ""))
    elif mode == "between":
        n_btw = sum(1 for e in evs if e.get("kind") == "between")
        key, kind = f"{ch2(ch)}:between-{n_btw + 1}", "between"
        since = betweens_since_last_scene(st)
        L.append(f"THIS BLOCK: {key} · a Between ({len(since)} of 2 written since the last scene" + ("; a third is two lines and the moment passes" if len(since) >= 2 else "") + ")")
    elif mode == "climax":
        key, kind = f"{ch2(ch)}:climax", "climax"
        L.append(f"THIS BLOCK: {key} · the chapter's climax · stage {pos.get('stage')}" + ("" if pos.get("stage") in ("climax", "choice") else " (⚠ `plan set stage=climax` first: it pays the owed world moves and makes the climax-targeted items due)"))
    elif mode == "choice":
        key, kind = f"{ch2(ch)}:choice", "choice"
        ac = plan.get("answered_choice")
        if not ac:
            die("no answered climax choice is waiting for its block (`saga.py choose` first)")
        key = f"{ch2(int(ac['chapter']))}:choice"
        L.append(f"THIS BLOCK: {key} · the consequence of the climax choice of chapter {ac['chapter']}: option {ac['option']} by {ac['by']}: {ac.get('text')}")
    else:
        kind = "chapter"

    if mode == "chapter":
        return brief_chapter(st, L, args)

    # ---------------- MUST
    section("MUST: what this block carries")
    if mode == "slot":
        L.append(f"plan: {slot.get('plan')}")
        L.append(f"turn: {slot.get('turn') or '(none planned: state one in a line first: ' + TURN_HINT + ')'}")
        m = slot.get("micro")
        if m:
            L.append(f"ends on {'the beat choice' if m.get('beat') else 'a small choice (' + str(m.get('axis')) + ')'}: {m.get('ask')}")
            for i, opt in enumerate(m.get("options", []), 1):
                b = (m.get("bearing") or [None] * len(m["options"]))[i - 1]
                L.append(f"  {i}. {opt}" + (f" [{', '.join(f'{k} {v:+d}' for k, v in b.items())}]" if b else "") + ("  (default)" if m.get("default") == i else ""))
        if slot.get("challenge"):
            c = slot["challenge"]
            L.append(f"device, a challenge ({c.get('status')}): {c.get('objective')} · approaches: " + "; ".join(f"{a.get('name')} ({a.get('stat')}{' + ' + a['art'] if a.get('art') else ''}, DC {a.get('dc')})" for a in c.get("approaches") or []) + f" · after each roll `saga.py challenge {slot['n']} success|fail`; the counters never reach the page")
            for a_ in c.get("approaches") or []:
                if a_.get("stat") in ("might", "vigor", "finesse", "resolve") and a_.get("dc"):
                    got = odds_line(f"approach {a_.get('name')}", ["--stat", a_["stat"], "--dc", a_["dc"]] + (["--prof", "--art", a_["art"]] if a_.get("art") else []), dc=int(a_["dc"]))
                    L.append(got if isinstance(got, str) else got[0])
        if slot.get("invite"):
            inv = slot["invite"]
            L.append(f"device, an invitation ({inv.get('status')}): {inv.get('who')} wants {inv.get('want')} · why now: {inv.get('why_now')} · offer it in one in-world sentence as the reply's last line; if ignored by the next close: {inv.get('if_ignored')}")
        if slot.get("kind") == "quest" and plan.get("quests", {}).get(slot.get("quest"), {}).get("project"):
            L.append("device, a project stage: the stage's decision goes into the page, then world.json → projects[] through the record")
        for o in owed_moves(plan):
            L.append(f"owed world move (open on it, one clause): {o['world_move']}")
        mm = re.match(r"^b(\d+)\.(\d+)$", str(slot.get("beat") or ""))
        if slot.get("kind") == "spine" and mm and int(mm.group(2)) > 1:
            prev = f"b{mm.group(1)}.{int(mm.group(2)) - 1}"
            for l in [l for l in arc_sections().get(prev, (0, "", []))[2] if "Downstream" in l]:
                L.append(f"downstream of {prev}'s choice (honour it in this beat): {short(l, 300)}")
    if mode == "between":
        s_next = next_slot(plan)
        if s_next:
            L.append(f"off limits (the next slot owns it): {short(s_next.get('plan'), 220)}")
        waiting = [s for s in plan["chapter"].get("slots", []) if (s.get("invite") or {}).get("status") == "waiting"]
        for s in waiting:
            inv = s["invite"]
            L.append(f"an invitation is waiting (slot {s['n']}): if this Between answers it, {inv.get('who')} opens with their first line, not Darrow's: they want {inv.get('want')} ({inv.get('why_now')}); record it with \"invite\": {{\"slot\": {s['n']}, \"action\": \"take\"}}")
        L.append("every Between changes an understanding, a relationship or a small obligation; its consequence is one terse ledger entry at most (`saga.py add`, made.scene between-K); never the plan's work, never a name or place the page has not spoken, nothing with the knee the plan has not cleared")
    if mode == "climax":
        c = plan["chapter"].get("climax") or {}
        L.append(f"climax plan: {c.get('plan')}")
        L.append("checks: " + ("; ".join(c.get("checks") or []) or "none planned"))
        for i, o in enumerate(c.get("options") or [], 1):
            L.append(f"  option {i}: {o}" + ("  (default)" if c.get("default") == i else ""))
        held_i, cap_i = inspiration_held()
        L.append(f"Inspiration held: {held_i} of {cap_i}: an option tagged `*[Inspiration]*` (a bold way, or the reroll of a check that failed here) is offered open while he holds one and struck through at none; never the default; `saga.py choose` spends it, and a reroll is cast in the Choice block with `--reroll --paid`")
        rows = chapter_rows()
        frozen = rows.get(ch)
        L.append(f"the tier: {frozen.get('tier') + ' (frozen by chapter-close; roll with --chapter ' + str(ch) + ')' if frozen else 'NOT FROZEN YET: `darrow.py chapter-close --date <Saturday>` first; the dice read the frozen tier'}")
        L.append("the tier's shape: Triumph, the plan works and something extra; Hard-won, he wins and it costs something real; Costly, one thing won and one lost; Setback, the enemy gains ground and the reversal sets up the next chapter (never humiliating, never a lecture)")
        L += climax_odds_lines(ch, c.get("checks") or [], rules, frozen)
        for o in owed_moves(plan):
            L.append(f"owed world move (open on it): {o['world_move']}")
        beat = pos.get("beat")
        sec = arc_sections().get(beat)
        if sec:
            tiers = [l for l in sec[2] if re.match(r"^- \*(Triumph|Hard-won|Costly|Setback)", l)]
            for l in tiers:
                L.append(f"arc {beat}: {short(l, 260)}")
            choice_l = [l for l in sec[2] if l.startswith("**Choice:**")]
            for l in choice_l:
                L.append(f"arc {beat} {short(l, 400)}")
    if mode == "choice":
        ac = plan["answered_choice"]
        L.append(f"the choice: {ac.get('ask')} → {ac['option']}. {ac.get('text')} (by {ac['by']}; ledger {ac.get('ledger')})")
        e = next((x for x in ledger.get("entries", []) if x.get("id") == ac.get("ledger")), None)
        if e:
            L.append(f"its ledger entry: {short(e.get('chose'), 200)} · now: {json.dumps(e.get('now') or {}, ensure_ascii=False)}")
            for it in e.get("due") or []:
                L.append(f"  it owes: {it['id']} [{it.get('weight')}] at {it.get('at')}: {short(it.get('what'), 180)}")
        beat = pos.get("beat")
        sec = arc_sections().get(beat)
        if sec:
            for l in [l for l in sec[2] if "Downstream" in l]:
                L.append(f"arc {beat}: {short(l, 300)}")
        L.append("companions react in their own voices by their under-pressure lines; an epithet earned must be spoken on the page here")
    # owed things, every mode
    om = plan.get("open_micro")
    if om and mode in ("slot", "climax"):
        L.append(f"OPEN small choice from scene {om.get('scene')} ({om.get('ask')}): if still unanswered, Darrow answers for himself with its default, option {om.get('default')} (`saga.py choose --by bearing '<entry>'`), said in one Ledger line, and the consequence opens this block in a clause")
    for l in open_choice_lines(plan):
        L.append(l)
    for e in [e for e in ledger.get("entries", []) if e.get("declined")][-2:]:
        L.append(f"declined lately ({e['id']}, {short(e.get('chose'), 60)}): " + " / ".join(short(x, 70) for x in e["declined"]) + " · a line may notice the road not taken, never explain it")
    ac = plan.get("answered_choice")
    if ac and mode != "choice":
        L.append(f"ANSWERED climax choice of chapter {ac['chapter']} (option {ac['option']}: {short(ac.get('text'), 100)}) still waits for its `### Choice` block: `saga.py brief --choice`")
    due_now = [it for e, it in pending_items(ledger) if item_status(it, st) in ("due", "overdue")]
    for it in due_now:
        L.append(f"DUE {it['id']} [{it.get('weight')}] @{it.get('at')} ({item_status(it, st)}): {it.get('what')}")
    if not due_now:
        L.append("due now: nothing")
    ro = rank_owed(plan)
    if ro:
        L.append(f"RANK OWED: {ro[0]} → {ro[1]}: one short prose beat of the script changed, as he notices it; the box names the rank; record \"rank\": \"{ro[1]}\"")
    if mode == "slot" and slot.get("kind") == "quest" and str(slot.get("quest")) == "rae.tether":
        t = sheet.get("tether") or {}
        L.append(f"THE TETHER stage {t.get('stage')} ({t.get('name')}): this scene pays it; its box ends `> The Tether: **{t.get('name')}**.`; record \"tether\": \"{t.get('name')}\"")
    section("CONTINUITY (from the records)")
    loc = world.get("location") or {}
    places = known_places()
    pl = places.get(loc.get("place") or "", {})
    L.append(f"where he is: {pl.get('name') or loc.get('place')}" + (f", {pl['subtitle']}" if pl.get("subtitle") else "") + f"; {loc.get('detail')}")
    if last:
        L.append(f"last block: {last['key']} · {last.get('title')}" + (f" · {last.get('time')}" if last.get("time") else "") + (f" · covers {last.get('date')}" if last.get("date") else ""))
        if last.get("last_beat"):
            L.append(f"  its last beat: {short(last['last_beat'], 400)}")
    if world.get("season"):
        L.append(f"season: {world['season']}")
    kl2 = knee_line(rules)
    if kl2:
        L.append(f"the knee, on the page: {kl2}")
    if world.get("inventory"):
        L.append("in hand: " + "; ".join(world["inventory"]))
    kept = world.get("keepsakes") or []
    if kept:
        L.append("kept from the tales (the page has them; an echo is allowed, never explained): " + " · ".join(f"{k.get('name')} ({k.get('to')})" for k in kept))
    since = betweens_since_last_scene(st)
    if since and mode != "between":
        for e, chose in since:
            L.append(f"since the last scene, a Between: {e.get('title')}: {short(e.get('last_beat'), 220)}" + (f" · it changed: {short(' / '.join(c for c in chose if c), 200)}" if any(chose) else ""))
    elif since and mode == "between":
        for e, chose in since:
            L.append(f"the Between before this one: {e.get('title')}: {short(e.get('last_beat'), 220)}")
    today = (slot or {}).get("day") or today_local().isoformat()
    head, grows = R.glimpse_lines()
    todays = [g for g in grows if g["date"] == today]
    for g in todays[-3:]:
        L.append(f"a glimpse already given today ({g['kind']}; the block may echo it, never contradicts it): {short(g['text'], 160)}")
    here, here_ids = [], []
    for cid, c in names.items():
        if cid == "darrow" or c.get("status") not in ("alive", "hollowed"):
            continue
        if (c.get("last_seen") or {}).get("place") == loc.get("place"):
            here.append(f"{c.get('name')} ({short(c.get('last_seen_doing'), 70)})")
            here_ids.append(cid)
    if here:
        L.append("by the page, here: " + " · ".join(here))
    # ---------------- MAY
    section("MAY: the people in the room (voice, tactic, regard, what they know)")
    texts = []
    if mode == "slot":
        texts = [slot.get("plan"), slot.get("turn"), str((slot.get("invite") or {}).get("who") or "").replace("-", " ").title()]
    elif mode == "climax":
        texts = [(plan["chapter"].get("climax") or {}).get("plan")]
    elif mode == "choice":
        texts = [plan["answered_choice"].get("text"), (plan["chapter"].get("climax") or {}).get("plan")]
    elif mode == "between" and args.with_:
        texts = [args.with_.replace(",", " ").replace("-", " ").title()]
    ids = people_in(texts, names, by_word)
    comps = [cid for cid in names if cid.split("-")[0] in (world.get("companions") or {}) and (world["companions"][cid.split("-")[0]].get("present") is not False)]
    for cid in comps:
        if cid not in ids and (mode == "between" or mode == "climax"):
            ids.append(cid)
    if "darrow" in ids:
        ids.remove("darrow")
    ids = ["darrow"] + ids
    thr_rows, n_open = threads_for_brief(ch)
    for cid in ids[:6]:
        L += person_brief(cid, names[cid], world, cast, thr_rows, facts_n=2)
    if len(ids) > 6:
        L.append(f"(+{len(ids) - 6} more named: `saga.py history --person <id>`)")
    section(f"MAY: threads ({n_open} open; `saga.py threads` for all)")
    for t in thr_rows:
        L.append(thread_line(t))
    L.append("plant and pay off: touch at least one open thread a chapter, plant at most one new one (a new thread goes in gm.threads with \"new\": true); a truth is revealed only after two plants")
    lore_lines = lore_for_brief(texts)
    if lore_lines:
        section("MAY: the Annals the plan names (received, not revealed; as many touches as the scene's meaning needs, often one)")
        L += lore_lines
    else:
        L.append("lore: the plan names no entry; `saga.py lore grep <word>` for a place or custom the block touches, `lore pick saying` for a line in someone's mouth")
    cbs = callbacks_for_brief(st, presence_ctx(set(ids) | set(here_ids), loc.get("place")))
    if cbs:
        section("MAY: callbacks waiting for a fit (one per block at most; record it in \"fired\" with the block's words that pay it)")
        L += cbs
    if mode == "slot":
        arc_key = slot.get("beat") if slot.get("kind") == "spine" else slot.get("quest")
        if arc_key and arc_key in arc_sections():
            section(f"THE ARC: {arc_key} (the plan above is this slot's share of it)")
            sec = arc_sections()[arc_key]
            lines = [l for l in sec[2]]
            while lines and not lines[-1].strip():
                lines.pop()
            L += lines[:40]
            if len(lines) > 40:
                L.append(f"… ({len(lines) - 40} more lines: `saga.py arc {arc_key}`)")
    elif mode == "climax" and pos.get("beat") in arc_sections():
        section(f"THE ARC: {pos.get('beat')}")
        sec = arc_sections()[pos.get("beat")]
        L += [l for l in sec[2] if l.strip()][:40]
    section("FORMAT")
    L += ["· " + l for l in format_lines(kind if mode != "slot" else "scene", slot)]
    L.append("· the wall: no foods, numbers, exercises, therapy or rehab words; the day's deeds colour only Darrow (warmth or cold in him, how he reads a room), never how others treat him; the outcome waits for the climax")
    L.append("· names: only what the page has spoken, or what this record registers; unnamed novices, lay brothers and the kitchen are fine")
    L.append("· then the reread (style.md §4), then `saga.py record` with the skeleton below, then `darrow.py ship`")
    section("RECORD (send this back, filled; drop what does not apply)")
    present = [cid for cid in ids if cid != "darrow"][:4]
    L.append(json.dumps(record_skeleton(key, kind if mode != "slot" else "scene", today if mode == "slot" else None, ["darrow"] + present, loc.get("place")), ensure_ascii=False, indent=None))
    text = "\n".join(L)
    print(text)
    if args.size:
        print(f"\n[brief: {len(text):,} chars ≈ {len(text) // 4:,} tokens]")


def brief_chapter(st, L, args):
    """The planning brief: the next chapter's skeleton with the pacing rule applied, the quests that may run, the beats left, the threads owed a touch."""
    plan, world = st.plan, st.world
    pos = plan["position"]
    book = int(pos["book"])
    cur = plan.get("chapter", {})
    try:
        ws = dt.date.fromisoformat(cur.get("week_start")) + dt.timedelta(7)
    except (TypeError, ValueError):
        die("the current chapter has no week_start; pass the Sunday by opening the chapter from `plan chapter template --week_start`")
    L.append(f"THIS BLOCK: the plan of chapter {int(cur.get('number', 0)) + 1} (week of Sunday {ws}) · `plan chapter open --number {int(cur.get('number', 0)) + 1} '<json>'`")
    L.append("")
    L.append("== MUST ==")
    beats = plan.get("core_beats", {})
    left = sorted([k for k, v in beats.items() if re.match(rf"^b{book}\.\d+$", k) and v.get("status") == "planned"], key=lambda k: int(k.split(".")[1]))
    curb = pos.get("beat")
    L.append(f"the Book's beats: current {curb} ({beats.get(curb, {}).get('status')}); planned after it: {', '.join(left) or 'none (the transition is next)'}")
    kl = knot_line(plan)
    if kl:
        L.append(kl)
    L.append("shape: 7 slots Sun–Sat (≥ 2 spine, Saturday spine, ≤ 1 interlude, two float quest slots); micros in non-adjacent slots touching ≥ 2 axes; world_moves (3); the climax plan with checks, options and a default (the option the highest-approval companion present would pick); the chapter touches ≥ 1 open thread")
    prev = sorted(device_kinds(cur.get("slots", []), plan.get("quests", {})))
    L.append(f"devices: one per slot, none on neighbouring days, at most two kinds of challenge/invite/project, ≤ 1 challenge, ≤ 2 invites; last chapter carried {', '.join(prev) or 'none'}, so those kinds rest this chapter")
    quests = plan.get("quests", {})
    live = [k for k, q in quests.items() if q.get("status") == "live" and not q.get("standing") and not q.get("project")]
    L.append(f"quests live now: {', '.join(f'{k} (stage {quests[k].get(chr(115)+chr(116)+chr(97)+chr(103)+chr(101))})' for k in live) or 'none'}; never more than two live at once; required first; a quest finishes within two chapters")
    cands = []
    for k, q in quests.items():
        if q.get("status") != "available":
            continue
        gate = q.get("gate")
        g = gate_state(gate, st)[0] if gate else "MET"
        cands.append((0 if q.get("priority") == "required" else 1 if q.get("priority") == "optional" else 2, k, q.get("priority"), g, gate))
    cands.sort()
    for _, k, pr, g, gate in cands[:10]:
        L.append(f"  candidate {k} ({pr}; gate {g}{': ' + gate if gate and g != 'MET' else ''}): {short(' '.join(arc_sections().get(k, (0, '', ['']))[2][1:3]), 160)}")
    t = (load_json(P["sheet"]).get("tether") or {}) if P["sheet"].exists() else {}
    rt = quests.get("rae.tether") or {}
    if int(t.get("stage") or 0) > int(rt.get("stage") or 0):
        L.append(f"THE TETHER: the sheet stands at stage {t.get('stage')} ({t.get('name')}) and the page at {rt.get('stage') or 0}: the first float quest slot carries stage {int(rt.get('stage') or 0) + 1}")
    L.append("the climax choice carries two scenes into this chapter if unanswered, then its default; slot 1 may be written while it is open")
    oc = plan.get("open_choice")
    if oc:
        L += open_choice_lines(plan)
    L.append("")
    L.append("== MAY ==")
    thr_rows, n_open = threads_for_brief(int(pos["chapter"]))
    for tr in thr_rows:
        L.append(thread_line(tr))
    nxt = left[0] if left and pos.get("stage") in ("climax", "choice", "transition") else curb
    if nxt in arc_sections():
        L.append("")
        L.append(f"== THE ARC: {nxt} (the next spine beat) ==")
        L += [l for l in arc_sections()[nxt][2] if l.strip()][:40]
    L.append("")
    L.append("== TEMPLATE (fill plan, turn, micro, devices, world_moves, climax; keep the rest) ==")
    tpl = chapter_template(ws, plan)
    for s in tpl["slots"]:
        s["device_allowed"] = s["n"] in (1, 3, 5, 7)  # a device every other day keeps them off neighbouring days; move them as the week needs
    L.append(json.dumps(tpl, ensure_ascii=False, indent=1))
    text = "\n".join(L)
    print(text)
    if args.size:
        print(f"\n[brief: {len(text):,} chars ≈ {len(text) // 4:,} tokens]")

# ---------------------------------------------------------------- the records: record, project, history, threads, glimpse, choose
RECORD_KEYS = ("key", "chapter", "scene", "kind", "title", "date", "written", "after", "where", "time", "last_beat", "people", "codex",
               "lore", "threads", "fired", "voided", "quest", "struggle", "season", "book_title", "inventory", "tether", "rank", "now",
               "recap", "story_so_far", "choice", "micro_opened", "invite")


def record_people_names(ev):
    out = set()
    for p in ev.get("people") or []:
        try:
            c = load_json(P["characters"] / f"{p.get('id')}.json")
        except (OSError, ValueError):
            continue
        for s in [c.get("name"), c.get("epithet")] + list(c.get("aliases") or []):
            out.update(w.lower() for w in re.findall(r"[A-Z][a-z]+", str(s or "")))
    for it in ev.get("codex") or []:
        out.update(w.lower() for w in re.findall(r"[A-Z][a-z]+", str(it.get("name") or "")))
    return out


def cmd_record(args):
    """One block of the page, recorded: validated against the chapter file, the registries and the plan; its event
    appended (reader-safe) and its GM note (if any); the plan moved (the slot done, a micro opened, the climax's
    choice opened, due items fired, the Annals marked spoken); every projection rebuilt; then `check`."""
    st = State()
    plan, world = st.plan, st.world
    pos = plan["position"]
    try:
        ev = json.loads(args.json)
    except json.JSONDecodeError as e:
        die(f"the record is not valid JSON: {e}")
    if not isinstance(ev, dict):
        die("the record is a JSON object")
    key = str(ev.get("key") or "")
    tk = R.parse_tale_key(key)
    if tk:
        return record_tale(args, ev, st, key, *tk)
    parsed = R.parse_key(key)
    if not parsed:
        die("key must look like ch02:s4, ch02:between-9, ch02:interlude, ch02:climax, ch02:choice, or tale01:p2 for a tale's piece")
    ch, sk, kind = parsed
    ac = plan.get("answered_choice") or {}
    prev_choice = kind == "choice" and int(ac.get("chapter", -1)) == ch  # a climax's Choice block belongs to its own chapter, even once the next is open
    if ch != int(pos["chapter"]) and not args.force and not prev_choice:
        die(f"{key} is chapter {ch}; the plan is on chapter {pos['chapter']} (--force re-records an older block)")
    files = R.chapter_files()
    path = files.get(ch)
    if not path:
        die(f"no chronicle file for chapter {ch}")
    blocks = R.blocks_of(path)
    block = next((b for b in blocks if b[0] == sk), None)
    if not block:
        want = {"scene": f"### Scene {sk} — Title", "between": "### Between — Title", "interlude": "### Interlude — Title", "climax": "## Climax — Title", "choice": "### Choice — Title"}.get(kind, sk)
        die(f"{path.name} has no block {sk}: write it first under `{want}`")
    _, btitle, btext = block
    if ev.get("title") and norm_title(ev["title"]) != norm_title(btitle):
        die(f"title {ev['title']!r} does not match the heading {btitle!r}")
    ev["title"] = btitle
    existing = {e["key"] for e in R.load_events(ch)}
    if key in existing and not args.force:
        die(f"{key} is already recorded; --force re-records it")
    probs, unknown_keys = [], [k for k in ev if k not in RECORD_KEYS and k != "gm"]
    if unknown_keys:
        probs.append(f"unknown field(s) {', '.join(unknown_keys)}; fields: {', '.join(RECORD_KEYS)}, gm")
    if kind == "scene" and int(sk) != int(pos["next_scene"]) and not args.force:
        probs.append(f"the next scene is {pos['next_scene']}, not {sk}")
    if kind == "between":
        earlier = [k for k, _, _ in blocks if k.startswith("between-") and int(k.split("-")[1]) < int(sk.split("-")[1])]
        missing = [k for k in earlier if R.make_key(ch, k) not in existing]
        if missing and not args.force:
            probs.append(f"record {R.make_key(ch, missing[0])} first: Betweens are recorded in page order")
        before = [k for k, _, _ in blocks[: [b[0] for b in blocks].index(sk)] if not k.startswith("between-")]
        ev["after"] = before[-1] if before else "climax"
    if kind == "climax" and pos.get("stage") not in ("climax", "choice", "transition") and not args.force:
        probs.append("the stage is still 'scene': `plan set stage=climax` comes before the climax is written (it pays the owed world moves)")
    if kind == "climax" and not isinstance(ev.get("choice"), dict):
        probs.append('a climax record carries the choice as the page offers it: "choice": {"ask": …, "options": […], "default": K}')
    if kind == "choice" and not ac and not args.force:
        probs.append("no answered climax choice is waiting for its block (`saga.py choose` first)")
    if kind != "prologue" and not str(ev.get("last_beat") or "").strip():
        probs.append("last_beat is required: the block's last beat in a line or two, in the page's words (the NOW page's 'Just happened')")
    if kind == "scene" and not ev.get("date"):
        probs.append("date is required for a scene: the day it covers (YYYY-MM-DD)")
    for d_ in ("date", "written"):
        if ev.get(d_):
            try:
                dt.date.fromisoformat(str(ev[d_]))
            except ValueError:
                probs.append(f"{d_} {ev[d_]!r} is not a date")
    places = known_places()
    where = ev.get("where")
    if where is not None:
        if not isinstance(where, dict) or not where.get("place"):
            probs.append('where is {"place": <places.json id>, "detail": "where in it he is at the end"}')
        elif where["place"] not in places:
            probs.append(f"where.place {where['place']!r} is not in places.json (add the place first)")
    elif kind not in ("prologue", "choice"):
        print("note: no `where`: his location carries forward from the last block")
    char_ids = set(R.char_files())
    for p in ev.get("people") or []:
        cid = p.get("id")
        if cid not in char_ids:
            probs.append(f"people: no file saga/characters/{cid}.json; a new person gets their base file first (saga/characters/README.md), then the record")
            continue
        if p.get("place") and p["place"] not in places:
            probs.append(f"{cid}: place {p['place']!r} is not in places.json")
        for f in p.get("facts") or []:
            if not str(f.get("fact") or "").strip():
                probs.append(f"{cid}: a fact with no text")
            evd = f.get("evidence")
            if evd is not None and (len(R.norm(evd)) < 12 or R.norm(evd) not in R.norm(btext)):
                probs.append(f"{cid}: evidence {evd!r} is not a verbatim excerpt of this block (a few words at least)")
        for k_ in p:
            if k_ not in ("id", "mention", "did", "now", "facts", "place", "present", "status", "quote", "story_so_far"):
                probs.append(f"{cid}: unknown people field {k_!r}")
    # names: a name the GM files know and the page has not spoken is refused (it would leak); any other unregistered
    # capitalised word is noted (a coinage is registered in this very record by a codex item or a person; a common noun needs nothing)
    reg = registered_names() | record_people_names(ev)
    allow = {w.strip() for w in str(args.allow_names or "").split(",") if w.strip()}
    refusals, name_notes = name_problems(btext, reg, allow, label="the block")
    probs += refusals
    for n_ in name_notes:
        print(n_)
    thr = R.load_threads()
    tids = {int(t["id"]) for t in thr.get("threads", [])}
    for t in ev.get("threads") or []:
        tid = t.get("id") if isinstance(t, dict) else t
        if tid is None or int(tid) not in tids:
            probs.append(f"threads: no thread {tid!r} (`saga.py threads --new '<json>'` first, or name it in gm.threads with \"new\": true)")
        elif isinstance(t, dict) and t.get("how") not in (None, "plant", "touch", "payoff"):
            probs.append(f"threads: how {t.get('how')!r} is plant, touch or payoff")
    entries, _ = lore_entries()
    for lid in ev.get("lore") or []:
        if lid not in entries:
            probs.append(f"lore: no entry {lid!r} in the Annals")
    ledger = st.ledger
    # what the block paid: each fired item carries the block's own words that pay it, so a consequence is proved on the
    # page, never only marked (a bare id passes only when --force re-records a block already recorded)
    fired_items = []
    for f_ in ev.get("fired") or []:
        f_ = {"id": f_} if isinstance(f_, str) else (f_ if isinstance(f_, dict) else {})
        did = str(f_.get("id") or "")
        if not did:
            probs.append('fired items are {"id": "<a due item, callback or rule id>", "evidence": "<verbatim words of the block that pay it>"}')
            continue
        evd = f_.get("evidence")
        if evd is None or not str(evd).strip():
            if not (args.force and key in existing):
                probs.append(f"fired {did}: no evidence; quote the block's words that pay it (a few words at least, verbatim)")
            evd = None
        elif len(R.norm(evd)) < 12 or R.norm(evd) not in R.norm(btext):
            probs.append(f"fired {did}: evidence {evd!r} is not a verbatim excerpt of this block (a few words at least)")
        if did.startswith("r."):
            if not any(r.get("id") == did for r in ledger.get("rules", [])):
                probs.append(f"fired: no rule {did}")
        else:
            hit = next((it for e in ledger["entries"] for it in e.get("due", []) if it["id"] == did), None)
            if hit is None:
                probs.append(f"fired: no due item {did}")
            elif hit.get("status") != "pending" and not args.force:
                probs.append(f"fired: {did} is already {hit['status']}")
        fired_items.append({"id": did, "evidence": evd} if evd is not None else {"id": did})
    ev["fired"] = fired_items
    for v in ev.get("voided") or []:
        if not isinstance(v, dict) or not v.get("id") or not v.get("why"):
            probs.append('voided items are {"id": …, "why": …}')
    codex = R.load_codex()
    if args.force:
        R.unapply_codex_key(codex, key)
    probs += R.apply_codex_items(codex, ev.get("codex"), key)
    gm = ev.pop("gm", None) or {}
    if gm and not isinstance(gm, dict):
        probs.append("gm is an object: {note, kept_off, next_must_know, threads: [{id | new+title, who_knows, status, note}]}")
        gm = {}
    for tu in gm.get("threads") or []:
        if tu.get("new"):
            if not str(tu.get("title") or "").strip():
                probs.append("a new thread needs a title")
        elif tu.get("id") is None or int(tu["id"]) not in tids:
            probs.append(f"gm.threads: no thread {tu.get('id')!r}")
    if kind in ("scene", "interlude"):
        s = find_slot_for(plan, ev, kind, args.slot)
        if s is None:
            probs.append("no slot for this block: a scene's slot is the one whose day is its date (`--slot N` names it; `plan slot N day=…` moves one)")
    if probs:
        die("refusing the record (nothing written):\n  " + "\n  ".join(probs))
    # callbacks that fit this block and were not paid are counted as offered, so the checkpoint sees what keeps passing by
    rec_ctx = presence_ctx([p.get("id") for p in ev.get("people") or [] if not p.get("mention")],
                           (where or {}).get("place") or (world.get("location") or {}).get("place"))
    paid_ids = {f_["id"] for f_ in ev.get("fired") or []}
    for e_, it_ in pending_items(st.ledger):
        if it_.get("at") == "later" and it_["id"] not in paid_ids and key not in (it_.get("offered_at") or []) and callback_fits(it_, st, rec_ctx)[0]:
            it_["offered"] = int(it_.get("offered") or 0) + 1
            it_.setdefault("offered_at", []).append(key)
            st.touch("ledger")
    # ---- the plan moves
    today = today_local().isoformat()
    wrote = f"{ch2(ch)}:{'s' + sk if kind == 'scene' else sk}"
    if kind in ("scene", "interlude"):
        if s.get("status") == "written" and s.get("wrote") == wrote:
            print(f"slot {s['n']} already written as {wrote}")
        else:
            plan_done_written(st, s, wrote)
            advance_next_slot(plan)
        if ev.get("micro_opened"):
            open_micro(st, s)
    if kind == "climax":
        c = ev["choice"]
        opts = c.get("options") or []
        if not 2 <= len(opts) <= 3 or c.get("default") not in range(1, len(opts) + 1):
            die("the climax's choice needs 2–3 options and a default among them")
        p_i = inspiration_default_problem(opts, c.get("default"), "the climax's choice")
        if p_i:
            die(p_i)
        oc = plan.get("open_choice") or {}
        if ch != int(pos["chapter"]):  # --force on an older chapter's climax: the plan has moved on, so only a still-open choice's wording follows the page
            if int(oc.get("chapter", -1)) == ch:
                oc.update({"ask": c.get("ask") or oc.get("ask"), "options": [str(o) for o in opts], "default": int(c["default"])})
                print("climax choice (still open) follows the page: " + " / ".join(f"{i}. {o}" for i, o in enumerate(opts, 1)) + f" · default {c['default']}")
            else:
                print(f"{key} re-recorded; its choice is no longer open, so the plan is unchanged")
        else:
            if pos.get("stage") == "scene":
                pos["stage"] = "climax"
                pay_owed_moves(plan, "climax")
            plan["open_choice"] = {"chapter": int(plan["chapter"].get("number")), "scene": "climax", "ask": c.get("ask") or "What does Darrow do?",
                                   "options": [str(o) for o in opts], "default": int(c["default"]), "opened": today, "carries": int(c.get("carries") or 2)}
            print("climax choice open: " + " / ".join(f"{i}. {o}" for i, o in enumerate(opts, 1)) + f" · default {c['default']}")
    if kind == "choice":
        if pos.get("stage") == "climax":
            pos["stage"] = "choice"
        plan.pop("answered_choice", None)
    inv = ev.get("invite")
    if isinstance(inv, dict) and inv.get("slot") is not None:
        s_inv = slot_by_n(plan, inv["slot"])
        if (s_inv.get("invite") or {}).get("status") == "waiting":
            s_inv["invite"]["status"] = "taken" if inv.get("action", "take") == "take" else "passed"
            print(f"invite slot {s_inv['n']} {s_inv['invite']['status']}")
    for f_ in ev.get("fired") or []:
        did, evd = f_["id"], f_.get("evidence")
        where_ = wrote if WHERE_RE.match(wrote) else f"{ch2(ch)}"
        if args.force and not str(did).startswith("r."):  # a revised block keeps what it already paid
            _, it_ = find_due(st.ledger, did)
            if it_.get("status") == f"fired@{where_}":
                if evd and not it_.get("evidence"):
                    it_["evidence"] = evd
                    st.touch("ledger")
                print(f"{did} already fired at {where_} (kept)")
                continue
        print(fire_item(st, did, where_, evd))
    for v in ev.get("voided") or []:
        print(void_item(st, v["id"], v["why"]))
    for lid in ev.get("lore") or []:
        old, new = lore_spoke(lid, wrote)
        print(f"{lid} spoken: {old or '—'} → {new}")
    if ev.get("rank"):
        pos["rank_on_page"] = ev["rank"]
        print(f"rank on the page: {ev['rank']}")
    for line_ in expire_callbacks(st, wrote if WHERE_RE.match(wrote) else ch2(ch)):  # a promise past its day lapses here, at its cost
        print(line_)
    # ---- the records
    ev.update({"chapter": ch, "scene": sk, "kind": kind})
    ev.setdefault("written", today)
    ev.setdefault("date", None)
    ordered = {k: ev[k] for k in RECORD_KEYS if k in ev and k not in ("micro_opened", "invite")}
    R.put_event(ordered, replace=args.force)
    note = {k: v for k, v in gm.items() if k != "threads" and v}
    for tu in gm.get("threads") or []:
        if tu.get("new"):
            nid = max([int(t["id"]) for t in thr["threads"]] + [0]) + 1
            thr["threads"].append({"id": nid, "title": tu["title"], "truth": tu.get("truth"), "feeds": tu.get("feeds", ""), "status": "open",
                                   "who_knows": tu.get("who_knows", ""), "note": tu.get("note", ""), "on_page": []})
            ordered.setdefault("threads", []).append({"id": nid, "how": "plant"})
            print(f"thread {nid} opened: {tu['title']}")
        else:
            t = next(x for x in thr["threads"] if int(x["id"]) == int(tu["id"]))
            for f_ in ("who_knows", "status", "note", "title", "truth", "feeds"):
                if tu.get(f_) is not None:
                    t[f_] = tu[f_]
    if any(t.get("new") for t in gm.get("threads") or []):
        R.put_event(ordered, replace=True)
    if note or gm.get("threads"):
        note.update({"key": key, "chapter": ch, "written": today, "threads": [tu for tu in gm.get("threads") or []]})
        R.put_note({k: note[k] for k in ("key", "chapter", "written", "note", "kept_off", "next_must_know", "threads") if k in note}, replace=True)
    R.save_codex(codex)
    R.save_threads(thr)
    st.touch("plan")
    st.save()
    changed = R.project_all(plan, write=True)
    print(f"{key} recorded: {btitle} · people {len(ordered.get('people') or [])} · facts {sum(len(p.get('facts') or []) for p in ordered.get('people') or [])} "
          f"· codex {len(ordered.get('codex') or [])} · threads {len(ordered.get('threads') or [])} · projections rebuilt: {', '.join(changed) or 'none'}")
    r = subprocess.run([sys.executable, str(Path(__file__).resolve()), "check"], cwd=ROOT, capture_output=True, text=True)
    sys.stdout.write(r.stdout + r.stderr)
    if r.returncode:
        sys.exit(r.returncode)
    print("next: `python3 engine/darrow.py ship -m \"…\"`")


def find_slot_for(plan, ev, kind, slot_n=None):
    slots = plan["chapter"].get("slots", [])
    if slot_n is not None:
        return next((s for s in slots if str(s.get("n")) == str(slot_n)), None)
    if kind == "interlude":
        return next((s for s in slots if s.get("kind") == "interlude" and s.get("status") in ("planned", "next", "written")), None)
    return next((s for s in slots if s.get("day") == ev.get("date") and s.get("kind") != "interlude"), None)


def cmd_project(args):
    st = State()
    changed = R.project_all(st.plan, write=not args.dry)
    if args.dry:
        print("projections that would change: " + (", ".join(changed) or "none (all fresh)"))
    else:
        print("projections rebuilt: " + (", ".join(changed) or "none (all were fresh)"))


def cmd_history(args):
    evs = R.load_events() + R.load_tale_events()
    notes = {n.get("key"): n for n in R.load_notes() + R.load_tale_notes()} if args.gm else {}
    rows = []
    for ev in evs:
        parsed = R.parse_key(ev.get("key", ""))
        tale = R.parse_tale_key(ev.get("key", ""))
        if not parsed and not tale:
            continue
        ch = parsed[0] if parsed else None
        if args.chapter is not None and ch != int(args.chapter):
            continue
        if getattr(args, "tale", None) is not None and (not tale or tale[0] != int(args.tale)):
            continue
        if args.place and (ev.get("where") or {}).get("place") != args.place:
            continue
        pid = (args.person or "").strip().lower()
        person = next((p for p in ev.get("people") or [] if pid and (p.get("id") == pid or str(p.get("id", "")).split("-")[0] == pid)), None)
        if pid and not person:
            continue
        tid = args.thread
        touch = next((t for t in ev.get("threads") or [] if tid is not None and int(t.get("id") if isinstance(t, dict) else t) == int(tid)), None)
        if tid is not None and not touch:
            continue
        rows.append((ev, person, touch))
    if args.last:
        rows = rows[-int(args.last):]
    if not rows:
        print("nothing recorded matches")
        return
    for ev, person, touch in rows:
        head = f"{ev['key']} · {ev.get('title')}" + (f" · {ev['date']}" if ev.get("date") else "") + (f" · at {ev['where']['place']}" if ev.get("where") else "")
        print(head)
        if person:
            if person.get("mention"):
                print("  named only")
            if person.get("did"):
                print(f"  did: {person['did']}")
            if person.get("now"):
                print(f"  now: {short(person['now'], 220)}")
            for f in person.get("facts") or []:
                print(f"  · {f.get('fact')}")
        elif touch:
            how = touch.get("how", "touch") if isinstance(touch, dict) else "touch"
            print(f"  {how}" + (f": {short(ev['last_beat'], 200)}" if ev.get("last_beat") else ""))
        else:
            if ev.get("last_beat"):
                print(f"  {short(ev['last_beat'], 220)}")
            if ev.get("people"):
                print("  with: " + ", ".join(p["id"] + ("*" if p.get("mention") else "") for p in ev["people"]))
        for f_ in ev.get("fired") or []:  # what the block paid, with the words that pay it
            if isinstance(f_, dict):
                print(f"  paid {f_.get('id')}" + (f": “{short(f_.get('evidence'), 120)}”" if f_.get("evidence") else " (unproved)"))
            else:
                print(f"  paid {f_} (recorded before the words were kept)")
        n = notes.get(ev["key"])
        if n:
            print(f"  GM: {short(n.get('note'), 300)}")
            for tu in n.get("threads") or []:
                print(f"  GM thread {tu.get('id')}: " + "; ".join(f"{k} {short(v, 90)}" for k, v in tu.items() if k not in ("id",) and v))
    if args.gm and args.chapter is not None:
        extra = [n for n in R.load_notes() if n.get("chapter") == int(args.chapter) and not R.parse_key(n.get("key", ""))]
        for n in extra:
            print(f"{n.get('key')} (GM): {short(n.get('note'), 300)}")


def cmd_threads(args):
    thr = R.load_threads()
    rows = thr.get("threads", [])
    if args.new:
        try:
            t = json.loads(args.new)
        except json.JSONDecodeError as e:
            die(f"--new is not valid JSON: {e}")
        if not str(t.get("title") or "").strip():
            die("a thread needs a title")
        nid = max([int(x["id"]) for x in rows] + [0]) + 1
        rows.append({"id": nid, "title": t["title"], "truth": t.get("truth"), "feeds": t.get("feeds", ""), "status": "open",
                     "who_knows": t.get("who_knows", ""), "note": t.get("note", ""), "on_page": []})
        R.save_threads(thr)
        print(f"thread {nid} opened: {t['title']} (its first plant is the block that records it: threads [{{\"id\": {nid}, \"how\": \"plant\"}}])")
        return
    if args.set:
        t = next((x for x in rows if str(x["id"]) == str(args.id)), None)
        if not t:
            die(f"no thread {args.id}")
        for k, v in parse_kv(args.set).items():
            if k not in ("who_knows", "status", "note", "title", "truth", "feeds"):
                die(f"thread field {k!r} is not editable (who_knows, status, note, title, truth, feeds)")
            if k == "status" and v not in ("open", "paid"):
                die("status is open or paid")
            print(f"thread {t['id']}.{k}: {short(t.get(k), 60)!r} → {short(v, 60)!r}")
            t[k] = v
        R.save_threads(thr)
        return
    if args.id is not None:
        t = next((x for x in rows if str(x["id"]) == str(args.id)), None)
        if not t:
            die(f"no thread {args.id}")
        print(f"thread {t['id']} · {t.get('status')} · {t.get('truth') or '—'} · feeds: {t.get('feeds')}")
        print(f"  {t.get('title')}")
        print(f"  who knows: {t.get('who_knows')}")
        print(f"  on the page ({len(t.get('on_page') or [])}): {', '.join(t.get('on_page') or []) or 'nowhere yet'}")
        print(f"  note: {t.get('note')}")
        for n in R.load_notes():
            for tu in n.get("threads") or []:
                if str(tu.get("id")) == str(t["id"]):
                    print(f"  {n.get('key')}: " + "; ".join(f"{k} {short(v, 120)}" for k, v in tu.items() if k != "id" and v))
        return
    shown = [t for t in rows if args.all or t.get("status") == "open"]
    print(f"threads: {sum(1 for t in rows if t.get('status') == 'open')} open, {sum(1 for t in rows if t.get('status') == 'paid')} paid · `threads --id N` for one, `--all` for the paid ones")
    for t in shown:
        onp = t.get("on_page") or []
        print(f"{t['id']:>3} {t.get('status'):4} {str(t.get('truth') or '—'):3} plants {len(onp):>2} last {onp[-1] if onp else '—':<14} {short(t.get('title'), 80)}")
        print(f"     knows: {short(t.get('who_knows'), 110)}")


def cmd_glimpse(args):
    if args.action == "show":
        head, rows = R.glimpse_lines()
        for r in rows[-(args.n or 6):]:
            print(f"- {r['date']} · {r['kind']} · {r['text']}")
        return
    if not args.kind or not args.text:
        die("glimpse add --kind house|overheard|ledger|saying|verse|body|weather \"text\"")
    refusals, name_notes = name_problems(args.text, registered_names(), label="the glimpse")
    if refusals:
        die("refusing the glimpse: " + "; ".join(refusals))
    for n_ in name_notes:
        print(n_)
    probs = R.glimpse_add(args.date or today_local().isoformat(), args.kind, args.text)
    if probs:
        die("refusing the glimpse:\n  " + "\n  ".join(probs))
    print(f"glimpse kept ({args.kind}); the file holds its last {R.GLIMPSE_KEEP}")


def cmd_choose(args):
    """His answer to the open choice, in one step: the ledger entry (approval, Bearing, flags, factions, the Downstream
    due items), the choices[] row the site reads, and the open micro or climax choice closed."""
    st = State()
    plan, world = st.plan, st.world
    om, oc = plan.get("open_micro"), plan.get("open_choice")
    which = args.which or ("micro" if om else "climax" if oc else None)
    if which is None:
        die("nothing is open: no micro-choice and no climax choice (a Darrow action with nothing open is a Between: /play)")
    target = om if which == "micro" else oc
    if not target:
        die(f"no {which} choice is open")
    opts = target.get("options") or []
    opt = args.option if args.option is not None else (target.get("default") if args.by == "bearing" else None)
    if opt is None:
        die("pass --option K, or --by bearing to take the planned default")
    if opt not in range(1, len(opts) + 1):
        die(f"option {opt} is not one of the {len(opts)} options: " + " / ".join(f"{i}. {o}" for i, o in enumerate(opts, 1)))
    costs = costs_inspiration(opts[opt - 1])
    if costs:  # an *[Inspiration]* option: his to pick while he holds one; never taken for him
        if args.by == "bearing":
            die("the default never costs Inspiration: an *[Inspiration]* option is his to pick, not taken for him")
        held, cap = inspiration_held()
        if held < 1:
            die(f"option {opt} costs Inspiration and he holds none (0 of {cap}): on the page it is struck through; pick another option")
    if not args.entry:
        die("the ledger entry JSON is required (one terse entry, design §2): {\"id\": \"cNN.n\", \"made\": {…}, \"chose\": …, \"now\": {…}, \"due\": […]}")
    try:
        entry = json.loads(args.entry)
    except json.JSONDecodeError as e:
        die(f"the entry is not valid JSON: {e}")
    chapter = int(plan["chapter"].get("number"))
    made = entry.setdefault("made", {})
    made.setdefault("chapter", chapter if which == "micro" else int(oc.get("chapter", chapter)))
    made.setdefault("scene", str(om.get("scene")) if which == "micro" else "climax")
    made.setdefault("date", today_local().isoformat())
    entry["declined"] = [o for i, o in enumerate(opts, 1) if i != opt]  # the roads not taken: a later line may notice one
    if costs:
        entry["inspiration"] = True
        # the entry is proved before the point is spent, so a spend never goes without its entry
        probs = validate_entry(json.loads(json.dumps(entry)), st.ledger, plan, bearing=st.bearing, world=world, pending=args.pending, st=st)
        probs += [f"--witnessed {w}: not in plan.json companions or companions_to_come" for w in (args.witnessed or "").split(",")
                  if w.strip() and w.strip() not in plan.get("companions", {}) and w.strip() not in plan.get("companions_to_come", {})]
        if probs:
            die("refusing the entry (nothing spent):\n  " + "\n  ".join(probs))
        r = subprocess.run([sys.executable, str(ROOT / "engine/darrow.py"), "inspire", "--reason", f"choice {ch2(int(made['chapter']))} {which} option {opt}"],
                           cwd=ROOT, capture_output=True, text=True)
        if r.returncode:
            die("the spend failed, nothing written: " + (r.stdout + r.stderr).strip())
        print((r.stdout or "").strip())
        subprocess.run([sys.executable, str(ROOT / "engine/darrow.py"), "sync"], cwd=ROOT, capture_output=True, text=True)  # the sheet shows the spend
    ordered = add_entry(st, entry, args.witnessed, args.pending, False)
    row = {"chapter": int(made["chapter"]), "scene": str(made["scene"]), "kind": which, "option": int(opt), "text": args.text or opts[opt - 1],
           "date": today_local().isoformat(), "ledger": ordered["id"], "by": args.by}
    world.setdefault("choices", []).append(row)
    st.touch("world")
    if which == "micro":
        s = next((x for x in plan["chapter"]["slots"] if str(x.get("n")) == str(om.get("slot"))), None)
        if s is not None and s.get("micro") is not None:
            s["micro"]["answer"] = {"option": int(opt), "by": args.by}
        plan["open_micro"] = None
        print(f"micro from slot {om.get('slot')} (scene {om.get('scene')}) answered: option {opt} by {args.by}; the consequence is folded into the next scene's opening (the brief carries it)")
    else:
        plan["open_choice"] = None
        plan["answered_choice"] = {"chapter": int(oc.get("chapter", chapter)), "ask": oc.get("ask"), "option": int(opt), "text": row["text"], "by": args.by, "ledger": ordered["id"]}
        print(f"climax choice of chapter {oc.get('chapter')} answered: option {opt} by {args.by}; write its `### Choice — Title` block in that chapter's file "
              f"(the brief: `saga.py brief --choice`), then `saga.py record` it")
    st.touch("plan")
    st.save()
    R.project_all(plan, write=True)

# ---------------------------------------------------------------- the tales: the past, a piece per task of a work (design.md §12)
TALE_PLAN_HEAD_RE = re.compile(r"^##\s+(tale\.[a-z0-9_]+)\s*[—–-]\s*(.+?)\s*$")
TALE_PIECE_HEAD_RE = re.compile(r"^###\s+piece\s+(\d+)\s*[—–-]\s*(.+?)\s*$", re.I)
TALE_RECORD_KEYS = ("key", "tale", "piece", "kind", "title", "written", "where", "time", "last_beat", "people", "codex", "lore", "threads", "keepsake")
TALE_FIELDS = ("of", "when", "pieces", "keepsake", "keepsake_late", "plants", "never")


def tale_plans():
    """The tales' plans from _gm/tales.md: {id: {id, title, fields (of, when, pieces, keepsake, plants, never), lines, pieces {k: {title, lines}}}}."""
    out, cur, piece = {}, None, None
    if not P["tales_plan"].exists():
        return out
    for line in P["tales_plan"].read_text(encoding="utf-8").splitlines():
        m = TALE_PLAN_HEAD_RE.match(line)
        if m:
            cur = {"id": m.group(1), "title": m.group(2).strip(), "fields": {}, "lines": [], "pieces": {}}
            out[cur["id"]] = cur
            piece = None
            continue
        if line.startswith("## ") or line.startswith("# "):
            cur, piece = None, None
            continue
        if cur is None:
            continue
        mp = TALE_PIECE_HEAD_RE.match(line)
        if mp:
            piece = {"title": mp.group(2).strip(), "lines": []}
            cur["pieces"][int(mp.group(1))] = piece
            continue
        if piece is None and line.startswith("- **"):
            for k, v in re.findall(r"\*\*(\w+):\*\*\s*(.*?)(?=\s*·\s*\*\*\w+:\*\*|$)", line):
                if k in TALE_FIELDS:
                    cur["fields"][k] = v.strip()
            continue
        (piece["lines"] if piece else cur["lines"]).append(line)
    for t in out.values():
        try:
            t["n_pieces"] = int(t["fields"].get("pieces") or len(t["pieces"]))
        except ValueError:
            t["n_pieces"] = len(t["pieces"])
    return out


def projects_data():
    try:
        return load_json(P["projects"])
    except (OSError, ValueError, json.JSONDecodeError):
        return {"projects": []}


def tale_state(st):
    """One row per bound tale (records.tales_state) plus the project's side: tasks reported, its status, the pieces owed."""
    rows = R.tales_state(st.plan)
    projects = {p.get("id"): p for p in projects_data().get("projects", [])}
    for t in rows:
        pr = projects.get(t.get("project")) or {}
        t["tasks_done"] = sum(1 for x in pr.get("tasks", []) if x.get("done"))
        t["project_status"] = pr.get("status")
        t["owed"] = max(0, min(t["tasks_done"], t["pieces"]) - t["told"])
        t["due"], t["late"] = pr.get("due"), bool(pr.get("late"))
    return rows


def unbound_projects(rows):
    """Projects with a task reported and no tale bound: a piece is being earned that nothing will tell."""
    bound = {t.get("project") for t in rows}
    out = []
    for p in projects_data().get("projects", []):
        done = sum(1 for x in p.get("tasks", []) if x.get("done"))
        if p.get("id") not in bound and done and p.get("status") in ("live", "done"):
            out.append((p["id"], done))
    return out


def tale_line(t):
    state = "told in full" if t["done"] else f"{t['told']} of {t['pieces']} told" + (f" · OWED {t['owed']}" if t["owed"] else "")
    pr = f"project {t['project']} ({t['project_status'] or 'missing'}, {t['tasks_done']} tasks reported)"
    return f"{t['id']} · Tale {t['n']} — {t['title']} · of {t['of'] or '—'} · {pr} · {state} · {t['file']}"


def cmd_tale(args):
    st = State()
    plan = st.plan
    plans = tale_plans()
    rows = tale_state(st)
    bound = {t.get("tale") for t in rows}
    if args.action == "list":
        print(f"tales: {len(rows)} bound" + (f", {sum(1 for t in rows if t['done'])} told in full" if rows else ""))
        for t in rows:
            print(tale_line(t))
            for kp in t.get("keepsakes") or []:
                print(f"    keepsake: {kp.get('name')} → {kp.get('to')}" + (" (the lesser one: the work came late)" if kp.get("lesser") else ""))
        free = [t for t in plans.values() if t["id"] not in bound]
        print("plans in tales.md not yet bound: " + (", ".join(f"{t['id']} ({t['n_pieces']} pieces, of {t['fields'].get('of', '—')})" for t in free) or "none; plan one (design.md §12)"))
        return
    if args.action == "next":
        owed = [t for t in rows if t["owed"]]
        if not owed:
            print("no piece owed: a tale pays one piece per task reported (`darrow.py project done TASK`)")
            return
        for t in owed:
            print(f"OWED: {t['id']} piece {t['told'] + 1} of {t['pieces']} (task {t['told'] + 1} of {t['project']} reported): `saga.py brief --tale`")
        return
    # bind
    if not args.id:
        die("tale bind PROJECT_ID [--tale tale.id]: the live project's id (`darrow.py project show`)")
    pr = next((p for p in projects_data().get("projects", []) if p.get("id") == args.id), None)
    if not pr:
        die(f"no project {args.id!r} in real/projects.json (`darrow.py project open` first)")
    if pr.get("status") != "live" and not args.force:
        die(f"project {pr['id']} is {pr.get('status')}: only a live project binds a tale (--force to bind anyway)")
    if any(t.get("project") == pr["id"] for t in rows):
        die(f"project {pr['id']} is already bound: " + tale_line(next(t for t in rows if t.get("project") == pr["id"])))
    n_tasks = len(pr.get("tasks") or [])
    if args.tale:
        tp = plans.get(args.tale)
        if not tp:
            die(f"no plan {args.tale!r} in {rel(P['tales_plan'])}; plans: " + ", ".join(plans) if plans else f"no plan {args.tale!r}: {rel(P['tales_plan'])} has none")
        if tp["id"] in bound and not args.force:
            die(f"{tp['id']} is already bound to another project (--force to tell it again as a new tale)")
    else:
        tp = next((t for t in plans.values() if t["id"] not in bound and t["n_pieces"] == n_tasks), None)
        if not tp:
            die(f"no unbound plan in {rel(P['tales_plan'])} has {n_tasks} pieces; plans: "
                + (", ".join(f"{t['id']} ({t['n_pieces']})" for t in plans.values() if t["id"] not in bound) or "none")
                + ". Fit one (a piece per task) or write a new one, then `tale bind` again, or name one with --tale")
    if tp["n_pieces"] != n_tasks and not args.force:
        die(f"{tp['id']} plans {tp['n_pieces']} pieces; the project has {n_tasks} tasks: a piece per task. Fit the plan in tales.md, pick another with --tale, or --force (the tale then has {n_tasks} pieces)")
    pieces = n_tasks
    n = max([int(b.get("n", 0)) for b in plan.get("tales") or []] + list(R.tale_files()) + [0]) + 1
    slug = re.sub(r"[^a-z0-9]+", "-", tp["title"].lower()).strip("-") or tp["id"].split(".")[-1]
    path = P["tales_dir"] / f"{n:02d}-{slug}.md"
    if path.exists():
        die(f"{rel(path)} exists already")
    when = tp["fields"].get("when", "").strip()
    refusals, name_notes = name_problems(when, registered_names(), label="the tale's opening line")
    if refusals:
        die("refusing to open the tale: " + "; ".join(refusals) + " (the `when` line of its plan goes on the page: keep it to what the page may say)")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# Tale {n} — {tp['title']}\n\n" + (f"*{when}*\n\n" if when else "") + "---\n", encoding="utf-8")
    plan.setdefault("tales", []).append({"n": n, "tale": tp["id"], "project": pr["id"], "of": tp["fields"].get("of") or None, "pieces": pieces,
                                         "file": rel(path), "title": tp["title"], "bound": today_local().isoformat()})
    st.touch("plan")
    st.save()
    R.project_all(plan, write=True)
    print(f"tale {n} bound: {tp['id']} — {tp['title']} ({pieces} pieces, of {tp['fields'].get('of') or '—'}) ↔ project {pr['id']} ({n_tasks} tasks) · {rel(path)} started")
    print("each task reported (`darrow.py project done TASK`) owes a piece: `saga.py brief --tale`, the piece written, `saga.py record`, `darrow.py ship`")


def brief_tale(st, args):
    """The brief for the piece owed: the tale's plan and this piece's, the keepsake on the last, what it must never say,
    the pieces told so far, the people, the Annals the plan names, the format and the record skeleton."""
    plan, world = st.plan, st.world
    rows = [t for t in tale_state(st) if t["owed"] > 0]
    if not rows:
        die("no piece is owed: a tale pays one piece per task reported (`darrow.py project done TASK`, then `darrow.py sync`); `saga.py tale list` shows every tale")
    t = rows[0]
    plans = tale_plans()
    tp = plans.get(t["tale"]) or {"fields": {}, "lines": [], "pieces": {}, "title": t["title"]}
    f = tp.get("fields", {})
    k = t["told"] + 1
    key = R.tale_key(t["n"], k)
    cast = cast_entries()
    names, by_word = people_index()
    L = []

    def section(title):
        L.append("")
        L.append(f"== {title} ==")

    L.append(f"BRIEF · Tale {t['n']} — {t['title']} · piece {k} of {t['pieces']} · the past of {t['of'] or '—'}" + (f" · {f.get('when')}" if f.get("when") else ""))
    L.append(f"THIS BLOCK: {key} · owed by task {k} of project {t['project']} ({t['tasks_done']} tasks reported, {t['told']} pieces told); it is written now, before anything else in the session")
    section("MUST: what this piece carries")
    for l in [l for l in tp.get("lines", []) if l.strip()]:
        L.append(f"the tale: {l.strip()}")
    pp = tp.get("pieces", {}).get(k)
    if pp:
        L.append(f"piece {k} — {pp['title']} (a working title; the page's own may differ)")
        L += ["  " + l.strip() for l in pp["lines"] if l.strip()]
    else:
        L.append(f"piece {k}: no plan in tales.md; state its want, its turn and its last image in a line before writing")
    if k == t["pieces"]:
        if t.get("late"):
            L.append(f"THE PROJECT CAME LATE (due {t.get('due')}; finished after it): THE LESSER KEEPSAKE, not the full one: "
                     f"{f.get('keepsake_late') or '<none planned: cut the full one down in tales.md: a smaller, plainer thing from this past>'}"
                     " · the piece ends on it in the page's words, smaller than the tale promised and never explained; the record carries \"keepsake\": {\"name\": …, \"text\": …, \"to\": …, \"mark\": <its drawing on the shelf: " + ", ".join(R.KEEPSAKE_MARKS) + ">} (the engine marks it lesser)")
            L.append(f"(the full keepsake, which this tale no longer gives: {f.get('keepsake')})")
        else:
            L.append(f"THE KEEPSAKE (this is the last piece; the project finished in its week): {f.get('keepsake') or '<none planned: an object, a name, a song or a saying from this past, to the tale\'s person>'}"
                     " · the piece ends on it in the page's words, and the record carries \"keepsake\": {\"name\": …, \"text\": <one line, the page's words>, \"to\": <character id>, \"mark\": <its drawing on the shelf: " + ", ".join(R.KEEPSAKE_MARKS) + ">}")
    else:
        L.append(f"pieces left after this one: {t['pieces'] - k}; the keepsake waits for the last" + (f" (due {t['due']}: finished in its week it is the full one, after it the lesser)" if t.get("due") else ""))
    if f.get("never"):
        L.append(f"NEVER (the present's secrets stay sealed): {f['never']}")
    if f.get("plants"):
        L.append(f"plants (set down, never explained): {f['plants']}")
    L.append("a tale is the past: it moves no approval, no Bearing, no ledger entry, no quest, no scene of the chapter; it may plant a thread (record it) and touch the Annals; it never contradicts a known fact on a person's page")
    section("CONTINUITY (from the records)")
    told = R.load_tale_events(t["n"])
    if told:
        for e in told:
            L.append(f"piece {R.parse_tale_key(e['key'])[1]} · {e.get('title')}: {short(e.get('last_beat'), 300)}")
    else:
        L.append("the tale opens here" + (f": {t['when']}" if t.get("when") else ""))
    who = t.get("of")
    c = names.get(who) if who else None
    if c:
        for fact in (c.get("known_facts") or [])[-4:]:
            L.append(f"known of {c.get('name')} ({fact.get('chapter')}:{fact.get('scene')}): {short(fact.get('fact'), 160)}")
        if c.get("story_so_far"):
            L.append(f"{c.get('name')} in the present, for the echo only: {short(c['story_so_far'], 240)}")
    kept = world.get("keepsakes") or []
    if kept:
        L.append("keepsakes already kept: " + "; ".join(f"{x.get('name')} ({x.get('to')})" for x in kept))
    section("MAY: the people in it (voice, tactic; what the page knows of them)")
    texts = list(tp.get("lines", [])) + ([pp["title"]] + list(pp["lines"]) if pp else []) + [str(f.get("keepsake") or ""), str(f.get("plants") or "")]
    ids = people_in(texts, names, by_word)
    if who and who in names and who not in ids:
        ids.insert(0, who)
    for cid in ids[:6]:
        L += person_brief(cid, names[cid], world, cast, None, facts_n=3)
    if len(ids) > 6:
        L.append(f"(+{len(ids) - 6} more named: `saga.py history --person <id>`)")
    L.append("a person without a file gets a base file first (saga/characters/README.md; status as the present knows it) and the record names them; the tale may leave people unnamed")
    thr = R.load_threads()
    tids = {int(x) for x in re.findall(r"thread (\d+)", " ".join(texts))}
    rows_t = [x for x in thr.get("threads", []) if int(x["id"]) in tids]
    if rows_t:
        section("MAY: threads the plan names (a plant in the past counts)")
        for x in rows_t:
            L.append(thread_line(x))
    lore_lines = lore_for_brief(texts)
    if lore_lines:
        section("MAY: the Annals the plan names (received, not revealed)")
        L += lore_lines
    else:
        L.append("lore: the plan names no entry; `saga.py lore grep <word>` for the place or custom the piece touches")
    section("FORMAT")
    L += ["· " + l for l in format_lines("tale")]
    L.append(f"· the file: {t['file']}")
    L.append("· the wall: no foods, numbers, exercises, therapy or rehab words; nothing of the project itself, whose words never reach the page")
    L.append("· names: only what the page has spoken, what this record registers, or what the plan above names; a place not in places.json is described, not named")
    L.append("· then the reread (style.md §4), `saga.py record` with the skeleton below, then `darrow.py ship`")
    section("RECORD (send this back, filled; drop what does not apply)")
    present = ids[:4]
    sk = {"key": key, "where": {"place": None, "detail": "<where the piece ends, in words; a places.json id in place when it has one>"}, "time": "<when, in the past>",
          "last_beat": "<the last beat, one or two sentences, the page's words>",
          "people": [{"id": cid, "did": "<one line>", "facts": [{"fact": "<one sentence>", "evidence": "<verbatim words of the piece>"}]} for cid in present] + [{"id": "<only named>", "mention": True}],
          "codex": [{"section": "Histories", "name": "<new thing>", "text": "<what it is (Tale N, Piece K)>"}], "lore": [], "threads": [{"id": 0, "how": "plant|touch"}],
          "gm": {"note": "<what the piece did for the tale; what was kept off the page>", "next_must_know": "<what the next piece must honour>"}}
    if k == t["pieces"]:
        sk["keepsake"] = {"name": "<the thing, the name, the song or the saying>", "text": "<one line, the page's words>", "to": who or "<character id>", "mark": "<one of: " + ", ".join(R.KEEPSAKE_MARKS) + ">"}
    L.append(json.dumps(sk, ensure_ascii=False))
    text = "\n".join(L)
    print(text)
    if args.size:
        print(f"\n[brief: {len(text):,} chars ≈ {len(text) // 4:,} tokens]")


def record_tale(args, ev, st, key, n, k):
    """One piece of a tale recorded: validated against its file, the binding, the project's tasks and the registries; its
    event and note written; the Codex and the threads updated; the projections rebuilt (never the plan's position)."""
    plan = st.plan
    t = next((x for x in tale_state(st) if x["n"] == n), None)
    if not t:
        die(f"no bound tale {R.tale_id(n)} (`saga.py tale bind <project>` first; `tale list`)")
    path = ROOT / t["file"] if t.get("file") else None
    if not path or not path.exists():
        die(f"{R.tale_id(n)}: its file {t.get('file')} is missing")
    pieces = R.pieces_of(path)
    block = next((b for b in pieces if b[0] == k), None)
    if not block:
        die(f"{path.name} has no piece {k}: write it first under `### Piece {k} — Title`")
    _, btitle, btext = block
    if ev.get("title") and norm_title(ev["title"]) != norm_title(btitle):
        die(f"title {ev['title']!r} does not match the heading {btitle!r}")
    ev["title"] = btitle
    existing = {e["key"] for e in R.load_tale_events(n)}
    if key in existing and not args.force:
        die(f"{key} is already recorded; --force re-records it")
    probs = []
    unknown = [x for x in ev if x not in TALE_RECORD_KEYS and x != "gm"]
    if unknown:
        probs.append(f"unknown field(s) {', '.join(unknown)}; a tale's record has: {', '.join(TALE_RECORD_KEYS)}, gm (no fired, voided, now, quest or tether: the past moves nothing)")
    if key not in existing and k != t["told"] + 1 and not args.force:
        probs.append(f"the next piece is {t['told'] + 1}, not {k}: pieces are told in order")
    if k > t["tasks_done"] and not args.force:
        probs.append(f"piece {k} is not owed yet: {t['tasks_done']} task(s) of {t['project']} reported; the task comes first (`darrow.py project done TASK`, then `sync`)")
    if k > t["pieces"]:
        probs.append(f"the tale has {t['pieces']} pieces; piece {k} is past its end")
    if not str(ev.get("last_beat") or "").strip():
        probs.append("last_beat is required: the piece's last beat in a line or two, in the page's words")
    if ev.get("written"):
        try:
            dt.date.fromisoformat(str(ev["written"]))
        except ValueError:
            probs.append(f"written {ev['written']!r} is not a date")
    places = known_places()
    where = ev.get("where")
    if where is not None:
        if not isinstance(where, dict):
            probs.append('where is {"place": <places.json id or null>, "detail": "where the piece ends, in words"}')
        elif where.get("place") and where["place"] not in places:
            probs.append(f"where.place {where['place']!r} is not in places.json (null and a detail for a place the map does not hold)")
    char_ids = set(R.char_files())
    for p in ev.get("people") or []:
        cid = p.get("id")
        if cid not in char_ids:
            probs.append(f"people: no file saga/characters/{cid}.json; a new person gets their base file first (saga/characters/README.md), then the record")
            continue
        for f in p.get("facts") or []:
            if not str(f.get("fact") or "").strip():
                probs.append(f"{cid}: a fact with no text")
            evd = f.get("evidence")
            if evd is not None and (len(R.norm(evd)) < 12 or R.norm(evd) not in R.norm(btext)):
                probs.append(f"{cid}: evidence {evd!r} is not a verbatim excerpt of this piece (a few words at least)")
        for k_ in p:
            if k_ not in ("id", "mention", "did", "facts", "quote"):
                probs.append(f"{cid}: unknown people field {k_!r} (a tale's people carry id, mention, did, facts, quote: the past moves no one's now, place or status)")
    ks = ev.get("keepsake")
    if k == t["pieces"]:
        if not isinstance(ks, dict) or not str(ks.get("name") or "").strip() or not str(ks.get("text") or "").strip():
            probs.append('the last piece carries the keepsake: "keepsake": {"name": …, "text": <one line, the page\'s words>, "to": <character id>}')
        elif ks.get("to") not in char_ids:
            probs.append(f"keepsake.to {ks.get('to')!r} is not a character id")
        elif set(ks) - {"name", "text", "to", "lesser", "mark"}:
            probs.append("keepsake carries name, text, to and an optional mark only")
        elif ks.get("mark") and ks["mark"] not in R.KEEPSAKE_MARKS:
            probs.append(f"keepsake.mark {ks['mark']!r} is not one the site can draw ({', '.join(R.KEEPSAKE_MARKS)})")
        else:
            ks = {k_: v for k_, v in ks.items() if k_ != "lesser"}
            if t.get("late"):
                ks["lesser"] = True  # the project finished after its week: the tale gives the lesser keepsake, and the record says so
            ev["keepsake"] = ks
    elif ks:
        probs.append("a keepsake comes with the last piece only")
    reg = registered_names() | record_people_names(ev)
    allow = {w.strip() for w in str(args.allow_names or "").split(",") if w.strip()}
    refusals, name_notes = name_problems(btext, reg, allow, label="the piece")
    probs += refusals
    for n_ in name_notes:
        print(n_)
    thr = R.load_threads()
    tids = {int(x["id"]) for x in thr.get("threads", [])}
    for x in ev.get("threads") or []:
        tid = x.get("id") if isinstance(x, dict) else x
        if tid is None or int(tid) not in tids:
            probs.append(f"threads: no thread {tid!r} (`saga.py threads --new '<json>'` first, or name it in gm.threads with \"new\": true)")
        elif isinstance(x, dict) and x.get("how") not in (None, "plant", "touch"):
            probs.append(f"threads: how {x.get('how')!r} is plant or touch (a tale pays nothing off)")
    entries, _ = lore_entries()
    for lid in ev.get("lore") or []:
        if lid not in entries:
            probs.append(f"lore: no entry {lid!r} in the Annals")
    codex = R.load_codex()
    if args.force:
        R.unapply_codex_key(codex, key)
    probs += R.apply_codex_items(codex, ev.get("codex"), key)
    gm = ev.pop("gm", None) or {}
    if gm and not isinstance(gm, dict):
        probs.append("gm is an object: {note, kept_off, next_must_know, threads: [{id | new+title, who_knows, status, note}]}")
        gm = {}
    for tu in gm.get("threads") or []:
        if tu.get("new"):
            if not str(tu.get("title") or "").strip():
                probs.append("a new thread needs a title")
        elif tu.get("id") is None or int(tu["id"]) not in tids:
            probs.append(f"gm.threads: no thread {tu.get('id')!r}")
    if probs:
        die("refusing the record (nothing written):\n  " + "\n  ".join(probs))
    today = today_local().isoformat()
    for lid in ev.get("lore") or []:
        old, new = lore_spoke(lid, key)
        print(f"{lid} spoken: {old or '—'} → {new}")
    ev.update({"tale": R.tale_id(n), "piece": k, "kind": "piece"})
    ev.setdefault("written", today)
    ordered = {x: ev[x] for x in TALE_RECORD_KEYS if x in ev}
    R.put_event(ordered, replace=args.force)
    note = {x: v for x, v in gm.items() if x != "threads" and v}
    for tu in gm.get("threads") or []:
        if tu.get("new"):
            nid = max([int(x["id"]) for x in thr["threads"]] + [0]) + 1
            thr["threads"].append({"id": nid, "title": tu["title"], "truth": tu.get("truth"), "feeds": tu.get("feeds", ""), "status": "open",
                                   "who_knows": tu.get("who_knows", ""), "note": tu.get("note", ""), "on_page": []})
            ordered.setdefault("threads", []).append({"id": nid, "how": "plant"})
            print(f"thread {nid} opened: {tu['title']}")
        else:
            x = next(y for y in thr["threads"] if int(y["id"]) == int(tu["id"]))
            for f_ in ("who_knows", "status", "note", "title", "truth", "feeds"):
                if tu.get(f_) is not None:
                    x[f_] = tu[f_]
    if any(tu.get("new") for tu in gm.get("threads") or []):
        R.put_event(ordered, replace=True)
    if note or gm.get("threads"):
        note.update({"key": key, "tale": R.tale_id(n), "written": today, "threads": [tu for tu in gm.get("threads") or []]})
        R.put_note({x: note[x] for x in ("key", "tale", "written", "note", "kept_off", "next_must_know", "threads") if x in note}, replace=True)
    R.save_codex(codex)
    R.save_threads(thr)
    changed = R.project_all(plan, write=True)
    print(f"{key} recorded: {btitle} · people {len(ordered.get('people') or [])} · facts {sum(len(p.get('facts') or []) for p in ordered.get('people') or [])} "
          f"· codex {len(ordered.get('codex') or [])} · threads {len(ordered.get('threads') or [])}" + (f" · keepsake: {ks['name']} → {ks['to']}" + (" (the lesser one)" if ks.get("lesser") else "") if isinstance(ks, dict) else "")
          + f" · projections rebuilt: {', '.join(changed) or 'none'}")
    r = subprocess.run([sys.executable, str(Path(__file__).resolve()), "check"], cwd=ROOT, capture_output=True, text=True)
    sys.stdout.write(r.stdout + r.stderr)
    if r.returncode:
        sys.exit(r.returncode)
    if k >= t["pieces"]:
        print(f"the tale is told in full; its keepsake goes on {ks['to']}'s page with the build. next: `python3 engine/darrow.py ship -m \"…\"`")
    elif t["tasks_done"] > k:
        print(f"piece {k + 1} is owed too (task {k + 1} of {t['project']} is reported): `saga.py brief --tale` next, then `darrow.py ship`")
    else:
        print(f"piece {k + 1} waits for task {k + 1} of {t['project']}. next: `python3 engine/darrow.py ship -m \"…\"`")


def check_tales(st, probs, notes):
    try:
        evs = R.load_tale_events()
        R.load_tale_notes()
    except ValueError as e:
        probs.append(str(e))
        return
    t_rows = tale_state(st)
    rows = {t["n"]: t for t in t_rows}
    tfiles = R.tale_files()
    char_ids = set(R.char_files())
    plans = tale_plans()
    for pid, done in unbound_projects(t_rows):
        notes.append(f"project {pid}: {done} task(s) reported and no tale bound (`saga.py tale bind {pid}`)")
    for b in st.plan.get("tales") or []:
        n = int(b.get("n") or 0)
        t = rows.get(n)
        if n not in tfiles:
            probs.append(f"tale {n} ({b.get('tale')}): no file {b.get('file')} under {rel(P['tales_dir'])}")
        if b.get("tale") not in plans:
            notes.append(f"tale {n}: its plan {b.get('tale')} is no longer in tales.md")
        if t and t["project_status"] is None:
            probs.append(f"tale {n}: project {b.get('project')} is not in real/projects.json")
        if t and t["told"] > t["pieces"]:
            probs.append(f"tale {n}: {t['told']} pieces told of {t['pieces']}")
        if t and t["owed"]:
            notes.append(f"tale {n}: piece {t['told'] + 1} is owed (task {t['told'] + 1} of {t['project']} reported): `saga.py brief --tale`")
    seen = {}
    for ev in evs:
        key = ev.get("key")
        parsed = R.parse_tale_key(key)
        if not parsed:
            probs.append(f"tale event key {key!r} malformed (tale01:p2)")
            continue
        seen[key] = seen.get(key, 0) + 1
        n, k = parsed
        if n not in tfiles:
            probs.append(f"event {key}: no tale file for tale {n}")
            continue
        pieces = {kk: tt for kk, tt, _ in R.pieces_of(tfiles[n])}
        if k not in pieces:
            probs.append(f"event {key}: {tfiles[n].name} has no piece {k}")
        elif norm_title(ev.get("title")) != norm_title(pieces[k]):
            probs.append(f"event {key}: title {ev.get('title')!r}, but the heading says {pieces[k]!r} (re-record it with --force)")
        for p in ev.get("people") or []:
            if p.get("id") not in char_ids:
                probs.append(f"event {key}: people id {p.get('id')!r} has no character file")
        t = rows.get(n)
        if t is None:
            probs.append(f"event {key}: tale {n} has no binding in the plan (`saga.py tale bind`)")
            continue
        if t["project_status"] is not None and k > t["tasks_done"]:
            probs.append(f"event {key}: piece {k} told before task {k} of {t['project']} was reported")
        ks = ev.get("keepsake")
        if k == t["pieces"] and not isinstance(ks, dict):
            probs.append(f"event {key}: the last piece has no keepsake")
        if isinstance(ks, dict) and ks.get("to") not in char_ids:
            probs.append(f"event {key}: keepsake.to {ks.get('to')!r} is not a character id")
    for k_, n_ in seen.items():
        if n_ > 1:
            probs.append(f"event {k_} is recorded {n_} times")
    for n, path in tfiles.items():
        if n not in rows:
            probs.append(f"{path.name}: tale {n} has no binding in the plan (`saga.py tale bind`)")
        for k, title, _ in R.pieces_of(path):
            if R.tale_key(n, k) not in seen:
                probs.append(f"{path.name} has `{title}` (piece {k}) but no event: `saga.py record '<json>'`")


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("now")
    s = sub.add_parser("due"); s.add_argument("--at"); s.add_argument("--all", action="store_true"); s.add_argument("--later", action="store_true")
    sub.add_parser("check")
    sub.add_parser("fmt")
    sub.add_parser("archive")
    s = sub.add_parser("add"); s.add_argument("entry"); s.add_argument("--witnessed"); s.add_argument("--pending", action="store_true"); s.add_argument("--dry-run", action="store_true")
    s = sub.add_parser("challenge"); s.add_argument("n"); s.add_argument("action", choices=["success", "fail", "show", "void"]); s.add_argument("--why")
    s = sub.add_parser("invite"); s.add_argument("n"); s.add_argument("action", choices=["take", "pass", "show"])
    s = sub.add_parser("project"); s.add_argument("id", nargs="?", help="a project quest id (show|work), or nothing: rebuild the projections"); s.add_argument("action", nargs="?", choices=["show", "work"]); s.add_argument("--where"); s.add_argument("--what"); s.add_argument("--dry", action="store_true", help="list the projections that would change, write nothing")
    s = sub.add_parser("fire"); s.add_argument("id"); s.add_argument("--where", required=True); s.add_argument("--evidence", help="the block's own words that pay it (verbatim); the record carries it by itself")
    s = sub.add_parser("void"); s.add_argument("id"); s.add_argument("--why", required=True)
    s = sub.add_parser("bearing"); s.add_argument("pole", help="a pole word, or `show`"); s.add_argument("n", nargs="?", type=int); s.add_argument("--why"); s.add_argument("--force", action="store_true", help="allow a move beyond ±4")
    s = sub.add_parser("route"); s.add_argument("action", choices=["decide", "show"]); s.add_argument("--book", type=int); s.add_argument("--road", choices=ROADS); s.add_argument("--why")
    s = sub.add_parser("plan"); ps = s.add_subparsers(dest="action", required=True)
    x = ps.add_parser("next"); x.add_argument("--date"); x.add_argument("--full", action="store_true")
    x = ps.add_parser("done"); x.add_argument("n"); x.add_argument("--wrote"); x.add_argument("--skipped", action="store_true"); x.add_argument("--force", action="store_true", help="redo a slot already written or skipped")
    x = ps.add_parser("slot"); x.add_argument("n"); x.add_argument("kv", nargs="+", help="key=value; micro as JSON"); x.add_argument("--force", action="store_true", help="edit a slot already written or skipped")
    x = ps.add_parser("micro"); x.add_argument("sub", choices=["open", "close"]); x.add_argument("n", nargs="?"); x.add_argument("--option", type=int); x.add_argument("--by", choices=["darrow", "bearing"], default="darrow")
    x = ps.add_parser("invite_rule"); x.add_argument("id", help="a character id or its first token (rae, benedek)"); x.add_argument("expr", help="rule grammar; null removes")
    x = ps.add_parser("climax")
    x = ps.add_parser("choice"); x.add_argument("sub", choices=["open", "show", "close"]); x.add_argument("json", nargs="?", help='open: {"ask": …, "options": […], "default": K}'); x.add_argument("--option", type=int); x.add_argument("--by", choices=["darrow", "bearing"], default="darrow")
    x = ps.add_parser("chapter"); x.add_argument("sub", choices=["open", "template", "cutaway"]); x.add_argument("--number", type=int); x.add_argument("json", nargs="?"); x.add_argument("--week_start", help="template: the Sunday the chapter covers"); x.add_argument("--force", action="store_true", help="open a chapter out of sequence")
    x = ps.add_parser("book"); x.add_argument("sub", choices=["open"]); x.add_argument("n", type=int)
    x = ps.add_parser("quest"); x.add_argument("id"); x.add_argument("kv", nargs="+")
    x = ps.add_parser("beat"); x.add_argument("id"); x.add_argument("kv", nargs="+")
    x = ps.add_parser("flag"); x.add_argument("kv", nargs="+"); x.add_argument("--new", action="store_true", help="add a flag the plan does not have yet")
    x = ps.add_parser("temptation"); x.add_argument("sub", choices=["add"]); x.add_argument("text")
    x = ps.add_parser("companion"); x.add_argument("sub", choices=["arrive"]); x.add_argument("id")
    x = ps.add_parser("set"); x.add_argument("kv", nargs="+")
    s = sub.add_parser("arc"); s.add_argument("id")
    s = sub.add_parser("lore"); s.add_argument("what", nargs="?", help="an entry id, or grep | pick | spoke"); s.add_argument("arg", nargs="?"); s.add_argument("--where"); s.add_argument("--all", action="store_true")
    s = sub.add_parser("names"); s.add_argument("--all", action="store_true", help="every chapter, not only the current one")
    s = sub.add_parser("brief"); s.add_argument("--date", help="the slot of that day (default: the next slot)"); s.add_argument("--between", action="store_true"); s.add_argument("--climax", action="store_true"); s.add_argument("--choice", action="store_true"); s.add_argument("--chapter", action="store_true", help="the next chapter's planning brief"); s.add_argument("--tale", action="store_true", help="the tale piece owed by a task reported"); s.add_argument("--with", dest="with_", help="between: who is in it (ids or names, comma-separated)"); s.add_argument("--size", action="store_true", help="print the brief's size")
    s = sub.add_parser("tale"); s.add_argument("action", choices=["bind", "list", "next"]); s.add_argument("id", nargs="?", help="bind: the live project's id"); s.add_argument("--tale", help="bind: a plan id in tales.md (default: the first unbound plan with a piece per task)"); s.add_argument("--force", action="store_true")
    s = sub.add_parser("record"); s.add_argument("json", help="the block's record (fields: saga.py -h, the records section)"); s.add_argument("--force", action="store_true", help="re-record a block already recorded"); s.add_argument("--slot", help="the slot the scene fills, when its date does not say"); s.add_argument("--allow-names", help="capitalised words in the block that are not names, comma-separated")
    s = sub.add_parser("history"); s.add_argument("--person"); s.add_argument("--thread", type=int); s.add_argument("--place"); s.add_argument("--chapter", type=int); s.add_argument("--tale", type=int, help="one tale's pieces"); s.add_argument("--last", type=int); s.add_argument("--gm", action="store_true", help="with the GM notes")
    s = sub.add_parser("threads"); s.add_argument("--id"); s.add_argument("--all", action="store_true"); s.add_argument("--set", nargs="+", help="with --id: who_knows=… status=open|paid note=… title=… truth=… feeds=…"); s.add_argument("--new", help='{"title": …, "truth": "T1", "feeds": …, "who_knows": …, "note": …}')
    s = sub.add_parser("glimpse"); s.add_argument("action", choices=["add", "show"]); s.add_argument("text", nargs="?"); s.add_argument("--kind", choices=list(R.GLIMPSE_KINDS)); s.add_argument("--date"); s.add_argument("--n", type=int)
    s = sub.add_parser("choose"); s.add_argument("entry", nargs="?", help="the ledger entry JSON"); s.add_argument("--option", type=int); s.add_argument("--by", choices=["darrow", "bearing"], default="darrow"); s.add_argument("--which", choices=["micro", "climax"]); s.add_argument("--text", help="the option as the page has it (default: the option's text)"); s.add_argument("--witnessed"); s.add_argument("--pending", action="store_true")
    args = ap.parse_args()
    if args.cmd == "route" and args.action == "decide" and not args.book:
        die("route decide needs --book N")
    if args.cmd == "project" and not args.id:
        cmd_project(args)
        return
    if args.cmd == "project" and not args.action:
        die("project ID show|work, or `project` alone to rebuild the projections")
    {
        "now": cmd_now, "due": cmd_due, "check": cmd_check, "fmt": cmd_fmt, "archive": cmd_archive,
        "add": cmd_add, "fire": cmd_fire, "void": cmd_void, "bearing": cmd_bearing, "route": cmd_route,
        "plan": cmd_plan, "challenge": cmd_challenge, "invite": cmd_invite, "project": cmd_project_quest, "arc": lambda a: print_arc(a.id), "lore": cmd_lore, "names": cmd_names,
        "brief": cmd_brief, "record": cmd_record, "history": cmd_history, "threads": cmd_threads, "glimpse": cmd_glimpse, "choose": cmd_choose,
        "tale": cmd_tale,
    }[args.cmd](args)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:  # piped into head: not an error
        pass
