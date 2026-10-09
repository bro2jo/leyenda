#!/usr/bin/env python3
"""THE UNKNEELING — the site builder. Renders the reader-facing site into docs/ from the Chronicle only.

Reads (and nothing else):
  saga/chronicle/*.md                      the story, by chapter
  saga/characters/*.json                   the cast, as the page has shown it
  saga/state/world.json, places.json, factions.json, darrow.json, bearing.json, codex.md, chapters.csv, rolls.csv
  engine/rules.json                        game data (knots, arts, ranks)
Never: real/, engine/deeds.csv, saga/bible/ or any _gm/ directory (the checks open saga/bible/_gm/*.md and
saga/state/_gm/*.md only to build blocklists; nothing from them is ever rendered).

Conventions the parser and the checks rely on:
  Scenes      '## I. Title' (prologue parts), '### Scene N — Title', '## Climax — Title', '### Choice — Title'.
  Interlude   '### Interlude — Title': another POV, not tied to a day. Scene key and anchor 'interlude'
              (a second one in the same chapter: 'interlude-2'), label "Interlude".
  Choices     a heading line '**What does Darrow do?**' (the chapter's climax choice) or
              '**What does Darrow say?**' (a small choice inside a scene) followed by a numbered list.
              world.json → choices[] records answers as {chapter, scene, kind, option, text, date, ledger, by}:
              'scene' is the key of the scene whose list it answers ('climax', '3', 'interlude'), chapters compare
              as ints, kind is 'climax' or 'micro', by is 'darrow' or 'bearing' (the latter renders
              "answered for himself"). The Now page titles a micro "A small choice" and a climax "The choice".
  Bearing     saga/state/bearing.json (optional): four axes, each {value, left, right}, plus names and epithet.
              Rendered in words only: "even" / "leans X" / "named X", a marker on a bar, the current epithet as a
              chip. The pole words are always allowed on the site; the current epithet only once the chronicle has
              spoken it (the build fails otherwise); the names table is never rendered and never allow-listed.
  GM wall     world.json must not carry chapter_plan, core_beats, flags, factions or current_quest.summary;
              those live under saga/state/_gm/. Every sentence in a _gm/*.md file is blocked from the site
              unless the chronicle, engine/rules.json or the Bearing's pole words / current epithet already carry it.

Usage: python3 engine/build_site.py [--verbose] [--force]
  Builds into a temporary directory, runs the checks, and replaces docs/ only when every check passes.
  --force writes docs/ even when a check fails (for debugging a failing build; never commit that).
Standard library only (Python 3.9+). Plain HTML + one stylesheet + a little JS; every page works with JavaScript off.
"""
import csv
import html
import json
import re
import shutil
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SAGA = ROOT / "saga"
DOCS = ROOT / "docs"
CHRON = SAGA / "chronicle"
CHARS = SAGA / "characters"
STATE = SAGA / "state"
RULES = ROOT / "engine" / "rules.json"
READ_ALLOW = [CHRON, CHARS, STATE / "world.json", STATE / "places.json", STATE / "factions.json",
              STATE / "darrow.json", STATE / "bearing.json", STATE / "codex.md", STATE / "chapters.csv", STATE / "rolls.csv", RULES]

VERBOSE = "--verbose" in sys.argv
FORCE = "--force" in sys.argv
PROBLEMS = []


def problem(msg):
    PROBLEMS.append(msg)


def note(msg):
    if VERBOSE:
        print("  " + msg)


def read(path):
    """The only way the renderer reads a file: refuses anything outside the allow-list."""
    path = Path(path)
    if not any(path == a or a in path.parents for a in READ_ALLOW):
        raise SystemExit(f"build refuses to read {path}")
    return path.read_text(encoding="utf-8")


def esc(s):
    return html.escape("" if s is None else str(s), quote=True)


def slug(s):
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s or "x"


ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]


def roman(n):
    return ROMAN[n] if 0 <= n < len(ROMAN) else str(n)


def as_int(x):
    s = str(x).strip() if x is not None else ""
    return int(s) if s.isdigit() else None


# ============================================================ markdown (the subset the chapters use)
def inline(md):
    s = esc(md)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"~~(.+?)~~", r"<s>\1</s>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', s)
    return s


DICE_RE = re.compile(r"^`\[([^\]]+)\]`\s*(.*)$")
ROLL_LINE_RE = re.compile(r"^(?:🎲\s*)?(\S+)\s*·\s*([A-Z]+) check DC (\d+):\s*(.*)$")
OL_RE = re.compile(r"^(\d+)\.\s+(.*)$")
PART_RE = re.compile(r"^##\s+(I|II|III|IV|V|VI|VII|VIII|IX|X)\.\s+(.+)$")
SCENE_RE = re.compile(r"^###\s+Scene\s+(\d+)\s*[—–-]\s*(.+)$")
INTERLUDE_RE = re.compile(r"^###\s+Interlude\s*[—–-]\s*(.+)$")
CLIMAX_RE = re.compile(r"^##\s+Climax\s*[—–-]\s*(.+)$")
CHOICE_RE = re.compile(r"^###\s+Choice\s*[—–-]\s*(.+)$")
HEAD_RE = re.compile(r"^(#{2,3})\s+(.+)$")
CHAPTER_RE = re.compile(r"^(Chapter\s+(\d+)|Prologue)\s*[—–-]\s*(.+)$")
CHOICE_HEAD_RE = re.compile(r"^\*\*What does Darrow (do|say)\?\*\*$")


def parse_chapter(path):
    lines = read(path).split("\n")
    ch = {"slug": path.stem, "code": path.stem[:2], "file": path.name, "book": None, "label": None,
          "number": None, "title": None, "epigraph": None, "scenes": [], "words": 0}
    i, n = 0, len(lines)
    while i < n:
        ln = lines[i].rstrip()
        if ln.startswith("# BOOK"):
            ch["book"] = ln[2:].strip()
        elif ln.startswith("# "):
            m = CHAPTER_RE.match(ln[2:].strip())
            if not m:
                problem(f"{path.name}: chapter heading '{ln}' is not 'Chapter N — Title' or 'Prologue — Title'")
                ch["label"], ch["number"], ch["title"] = ln[2:].strip(), 0, ln[2:].strip()
            else:
                ch["label"] = m.group(1)
                ch["number"] = int(m.group(2)) if m.group(2) else 0
                ch["title"] = m.group(3).strip()
            i += 1
            break
        i += 1
    if ch["label"] is None:
        problem(f"{path.name}: no '# Chapter N — Title' or '# Prologue — Title' heading")
        ch["label"], ch["number"], ch["title"] = path.stem, 0, path.stem
    epi, src, j = [], None, i
    while j < n and lines[j].strip() != "---" and not lines[j].lstrip().startswith(("#", ">")):
        s = lines[j].strip()
        if s.startswith("—") or s.startswith("–"):
            src = s.lstrip("—– ").strip()
        elif s:
            epi.append(s.strip("*"))
        j += 1
    if j < n and lines[j].strip() == "---":
        i = j + 1
        if epi:
            ch["epigraph"] = {"lines": epi, "source": src}
    elif epi:
        problem(f"{path.name}: the epigraph must be followed by a '---' line before the first scene (see style.md §3)")
    anchors_seen = set()
    cur = None

    def scene(key, label, title, anchor):
        if anchor in anchors_seen:
            problem(f"{path.name}: two scenes share the anchor '{anchor}'")
        anchors_seen.add(anchor)
        s = {"key": key, "label": label, "title": title, "anchor": anchor, "blocks": []}
        ch["scenes"].append(s)
        return s

    para = []
    pending_choice = None  # None, or "do" / "say": which choice heading the next numbered list answers
    n_interludes = 0

    def flush():
        nonlocal para, pending_choice
        if para and cur is not None:
            text = " ".join(x.strip() for x in para)
            cur["blocks"].append(("p", text))
            ch["words"] += len(text.split())
            pending_choice = None
        para = []

    while i < n:
        ln = lines[i].rstrip()
        s = ln.strip()
        m = PART_RE.match(s)
        if m:
            flush()
            cur = scene(m.group(1), m.group(1), m.group(2).strip(), "part-" + m.group(1).lower())
            i += 1
            continue
        m = SCENE_RE.match(s)
        if m:
            flush()
            cur = scene(m.group(1), "Scene " + m.group(1), m.group(2).strip(), "scene-" + m.group(1))
            i += 1
            continue
        m = INTERLUDE_RE.match(s)
        if m:
            flush()
            n_interludes += 1
            key = "interlude" if n_interludes == 1 else f"interlude-{n_interludes}"
            cur = scene(key, "Interlude", m.group(1).strip(), key)
            i += 1
            continue
        m = CLIMAX_RE.match(s)
        if m:
            flush()
            cur = scene("climax", "Climax", m.group(1).strip(), "climax")
            i += 1
            continue
        m = CHOICE_RE.match(s)
        if m:
            flush()
            cur = scene("choice", "The choice", m.group(1).strip(), "choice")
            i += 1
            continue
        m = HEAD_RE.match(s)
        if m:
            flush()
            pending_choice = None
            head = m.group(2).strip()
            if re.match(r"^(Scene\b|Interlude\b|Climax\b|Choice\b)", head, re.I):
                problem(f"{path.name}: heading '{s}' must be '### Scene N — Title', '### Interlude — Title', '## Climax — Title' or '### Choice — Title'")
            if cur is None:
                cur = scene(slug(head), "", head, slug(head))
            else:
                cur["blocks"].append(("h", head))
            i += 1
            continue
        if cur is None:
            if s:
                cur = scene("opening", "", "", "opening")
            else:
                i += 1
                continue
        if not s:
            flush()
            i += 1
            continue
        if s == "---":
            flush()
            cur["blocks"].append(("hr",))
            i += 1
            continue
        if s in ("* * *", "***"):
            flush()
            cur["blocks"].append(("orn",))
            i += 1
            continue
        if s.startswith(">"):
            flush()
            q = []
            while i < n and lines[i].strip().startswith(">"):
                q.append(lines[i].strip()[1:].strip())
                i += 1
            if q and "THE RECKONING" in q[0]:
                cur["blocks"].append(("reck", q[1:]))
            else:
                cur["blocks"].append(("quote", q))
            continue
        m = DICE_RE.match(s)
        if m:
            flush()
            cur["blocks"].append(("dice", m.group(1), m.group(2)))
            i += 1
            continue
        m = ROLL_LINE_RE.match(s)
        if m:
            flush()
            cur["blocks"].append(("dice", f"{m.group(2)} · DC {m.group(3)}", m.group(4).replace("→", "—")))
            i += 1
            continue
        m = OL_RE.match(s)
        if m:
            flush()
            items = []
            while i < n and OL_RE.match(lines[i].strip()):
                items.append(OL_RE.match(lines[i].strip()).group(2))
                i += 1
            cur["blocks"].append(("ol", items, pending_choice))
            pending_choice = None
            continue
        if s.startswith("- "):
            flush()
            items = []
            while i < n and lines[i].strip().startswith("- "):
                items.append(lines[i].strip()[2:])
                i += 1
            cur["blocks"].append(("ul", items))
            continue
        m = CHOICE_HEAD_RE.match(s)
        if m:
            flush()
            cur["blocks"].append(("choice-h", f"What does Darrow {m.group(1)}?", m.group(1)))
            pending_choice = m.group(1)
            i += 1
            continue
        para.append(ln)
        i += 1
    flush()
    # an empty chapter is allowed only while it is world.json's current chapter (the week between the climax
    # and scene 1); Site.__init__ fails any other chapter without a scene
    ch["empty"] = not ch["scenes"]
    return ch


# ============================================================ data
def load_json(path):
    return json.loads(read(path))


def load_csv(path):
    text = read(path)
    rows = list(csv.DictReader(text.splitlines()))
    return [r for r in rows if any((v or "").strip() for v in r.values())]


def load_characters(registry, factions, places):
    chars = {}
    for p in sorted(CHARS.glob("*.json")):
        try:
            c = load_json(p)
        except json.JSONDecodeError as e:
            problem(f"{p.name}: invalid JSON ({e})")
            continue
        cid = c.get("id") or p.stem
        if cid != p.stem:
            problem(f"{p.name}: id '{cid}' does not match the file name")
        missing = [k for k in ("name", "tier", "status", "faction", "appearance", "first_seen", "last_seen", "last_seen_doing",
                               "now", "story_so_far", "known_facts", "relationships", "appearances", "sigil") if k not in c]
        if cid != "darrow" and "reckoning" not in c:
            missing.append("reckoning")
        if missing:
            problem(f"{p.name}: missing field(s) {', '.join(missing)}; file skipped")
            continue
        if (c.get("tier") == "fallen") != (c.get("status") == "fallen"):
            problem(f"{p.name}: tier and status must both be 'fallen' or neither (tier {c.get('tier')}, status {c.get('status')})")
        if cid != "darrow":
            rk = c.get("reckoning")
            if c.get("tier") == "fallen" and rk is not None:
                problem(f"{p.name}: a fallen character's reckoning must be null")
            if c.get("tier") != "fallen":
                if not isinstance(rk, dict):
                    problem(f"{p.name}: reckoning must be an object for the living (null is only for the fallen)")
                elif ((rk.get("fire") or {}).get("kind")) not in ("grace", "ember", "none"):
                    problem(f"{p.name}: reckoning.fire.kind must be grace, ember or none")
        if c.get("tier") not in ("major", "minor", "fallen"):
            problem(f"{p.name}: tier must be major, minor or fallen")
        if c.get("status") not in ("alive", "fallen", "hollowed", "missing", "unknown"):
            problem(f"{p.name}: status '{c.get('status')}' is not alive/fallen/hollowed/missing/unknown")
        if c.get("faction") not in factions:
            problem(f"{p.name}: faction '{c.get('faction')}' is not in factions.json")
        sg = c.get("sigil") or {}
        if sg.get("faction") not in factions:
            problem(f"{p.name}: sigil.faction '{sg.get('faction')}' is not in factions.json")
        if (sg.get("mark") or "none") not in MARKS:
            problem(f"{p.name}: sigil.mark '{sg.get('mark')}' is not one the build can draw ({', '.join(sorted(MARKS))})")
        for ref_name in ("first_seen", "last_seen"):
            ref = c.get(ref_name) or {}
            key = (str(ref.get("chapter")), str(ref.get("scene")))
            if key not in registry:
                problem(f"{p.name}: {ref_name} points at chapter {ref.get('chapter')} scene {ref.get('scene')}, which is not in the chronicle")
            elif ref.get("anchor") != registry[key]["href"]:
                problem(f"{p.name}: {ref_name}.anchor '{ref.get('anchor')}' should be '{registry[key]['href']}'")
            if ref.get("place") and ref.get("place") not in places:
                problem(f"{p.name}: {ref_name}.place '{ref.get('place')}' is not in places.json")
        for f in c.get("known_facts") or []:
            key = (str(f.get("chapter")), str(f.get("scene")))
            if not f.get("fact"):
                problem(f"{p.name}: a known_fact has no text")
            if key not in registry:
                problem(f"{p.name}: known_fact '{str(f.get('fact'))[:50]}' has no chapter/scene source in the chronicle")
        for a in c.get("appearances") or []:
            key = (str(a.get("chapter")), str(a.get("scene")))
            if key not in registry:
                problem(f"{p.name}: appearance chapter {a.get('chapter')} scene {a.get('scene')} is not in the chronicle")
        q = c.get("quote")
        if q and (str(q.get("chapter")), str(q.get("scene"))) not in registry:
            problem(f"{p.name}: quote has no chapter/scene source in the chronicle")
        if cid == "darrow" and "reckoning" in c:
            problem(f"{p.name}: Darrow's numbers are engine-owned; remove 'reckoning' from his file")
        chars[cid] = c
    known = {p.stem for p in CHARS.glob("*.json")}
    for cid, c in chars.items():
        for r in c.get("relationships") or []:
            if r.get("to") not in known:
                problem(f"{cid}.json: relationship 'to' value '{r.get('to')}' is not a character file id")
    return chars


# ============================================================ svg
MARKS = {"none", "knot", "horn", "needle", "pencil", "spyglass", "key", "stone", "note", "knife", "quill", "cup", "candle", "star"}
DEVICES = {"lance", "bell", "censer", "crown", "redhand", "knee"}


def svg_device(device, numeral=""):
    """Faction device, drawn in the upper half of a 100x116 shield. Line style, no fills but the red hand."""
    if device == "lance":
        num = f'<text x="64" y="58" text-anchor="middle" class="sg-num">{esc(numeral)}</text>' if numeral else ""
        return ('<path d="M22 56 L58 16" class="sg-l"/><path d="M58 16 L63 12 L60 21 Z" class="sg-f"/>'
                '<path d="M46 26 L54 32 L50 22" class="sg-l"/>' + num)
    if device == "bell":
        return ('<path d="M50 16 C38 16 35 28 35 40 L33 48 L67 48 L65 40 C65 28 62 16 50 16 Z" class="sg-l"/>'
                '<path d="M44 52 C44 58 56 58 56 52" class="sg-l"/><circle cx="50" cy="13" r="2.5" class="sg-l"/>')
    if device == "censer":
        return ('<path d="M50 10 L50 20 M38 20 L50 32 L62 20" class="sg-l"/>'
                '<path d="M36 32 C36 48 64 48 64 32 Z" class="sg-l"/><path d="M42 50 L58 50" class="sg-l"/>'
                '<path d="M44 26 c-3 -6 3 -8 0 -14 M56 26 c3 -6 -3 -8 0 -14" class="sg-s"/>')
    if device == "crown":
        return ('<path d="M30 50 L30 24 L41 36 L50 18 L59 36 L70 24 L70 50 Z" class="sg-l"/>'
                '<path d="M30 56 L70 56" class="sg-l"/>')
    if device == "redhand":
        return ('<path d="M42 58 L42 34 C42 29 48 29 48 34 L48 26 C48 21 54 21 54 26 L54 24 C54 19 60 19 60 24 L60 30 '
                'C60 26 66 26 66 31 L66 46 C66 56 60 60 54 60 L46 60 C40 60 36 56 36 48 L36 40 C36 36 42 36 42 40 Z" class="sg-red"/>'
                '<path d="M24 58 C30 50 32 42 28 34 M26 40 L30 44 M28 30 L24 32" class="sg-l"/>')
    if device == "knee":
        return ('<path d="M50 14 L50 56" class="sg-l"/><circle cx="50" cy="36" r="5" class="sg-l"/>'
                '<path d="M32 58 L68 58" class="sg-l"/>')
    return ""


def svg_mark(mark):
    """Personal mark, drawn in the lower part of the shield (centre 50,82)."""
    if mark == "knot":
        return '<path d="M38 82 C38 70 62 70 62 82 C62 94 38 94 38 82 M44 76 L56 88 M56 76 L44 88" class="sg-l"/>'
    if mark == "horn":
        return '<path d="M34 76 C40 94 58 96 66 80 L62 76 C56 86 44 84 40 72 Z" class="sg-l"/><path d="M62 76 L68 72" class="sg-l"/>'
    if mark == "needle":
        return '<path d="M36 92 C36 72 56 68 64 72" class="sg-l"/><path d="M64 72 L68 68" class="sg-l"/><path d="M40 92 c6 -2 10 2 16 0 s10 2 14 -2" class="sg-s"/>'
    if mark == "pencil":
        return '<path d="M36 94 L60 70 L66 76 L42 100 Z" class="sg-l"/><path d="M36 94 L34 102 L42 100" class="sg-l"/>'
    if mark == "spyglass":
        return '<path d="M34 92 L52 74 M50 72 L56 78 M56 70 L64 78 M62 68 L68 74" class="sg-l"/><path d="M34 92 l-2 2" class="sg-l"/>'
    if mark == "key":
        return '<circle cx="42" cy="78" r="7" class="sg-l"/><path d="M48 82 L66 96 M60 92 L64 88 M56 88 L60 84" class="sg-l"/>'
    if mark == "stone":
        return '<path d="M34 72 L66 72 L66 94 L34 94 Z" class="sg-l"/><path d="M40 78 L60 78 M40 84 L60 84 M40 90 L54 90" class="sg-s"/>'
    if mark == "note":
        return '<path d="M56 68 L56 92" class="sg-l"/><ellipse cx="50" cy="93" rx="7" ry="5" class="sg-l"/><path d="M56 68 C64 70 66 78 62 82" class="sg-l"/>'
    if mark == "knife":
        return '<path d="M38 96 L66 68 L70 72 L48 94 Z" class="sg-l"/><path d="M38 96 L34 100" class="sg-l"/>'
    if mark == "quill":
        return '<path d="M38 96 C40 78 54 68 68 68 C66 82 56 92 42 94" class="sg-l"/><path d="M38 96 L58 76" class="sg-s"/>'
    if mark == "cup":
        return '<path d="M38 72 L62 72 L58 94 L42 94 Z" class="sg-l"/><path d="M44 100 L56 100" class="sg-l"/>'
    if mark == "candle":
        return '<path d="M44 76 L56 76 L56 98 L44 98 Z" class="sg-l"/><path d="M50 76 L50 70 C46 66 50 62 50 60 C50 62 54 66 50 70" class="sg-l"/>'
    if mark == "star":
        return '<path d="M50 66 L54 78 L66 78 L56 85 L60 97 L50 90 L40 97 L44 85 L34 78 L46 78 Z" class="sg-l"/>'
    return ""


def sigil(faction, mark, size=64, cls="", label=""):
    f = faction or {}
    aria = f'role="img" aria-label="{esc(label)}"' if label else 'aria-hidden="true"'
    return (f'<svg class="sigil {cls}" width="{size}" height="{int(size * 1.16)}" viewBox="0 0 100 116" {aria}>'
            '<path d="M50 3 L95 14 V56 C95 84 75 102 50 113 C25 102 5 84 5 56 V14 Z" class="sg-shield"/>'
            '<path d="M50 9 L89 18.5 V56 C89 80 72 96 50 106 C28 96 11 80 11 56 V18.5 Z" class="sg-inner"/>'
            '<path d="M14 64 L86 64" class="sg-s"/>'
            + svg_device(f.get("device"), f.get("numeral", "")) + svg_mark(mark) + "</svg>")


def crest(level, big=False):
    lv = esc(level)
    size = 30 if (isinstance(level, int) and level >= 10) else 36
    if level in ("?", "—"):
        size = 40
    label = "Level unread" if level == "?" else ("No level of his own: borrowed strength" if level == "—" else f"Level {lv}")
    return (f'<svg class="crest{" unread" if level == "?" else " borrowed" if level == "—" else ""}" viewBox="0 0 86 100" aria-label="{label}" role="img">'
            '<path d="M43 3 L82 13 V48 C82 73 65 88 43 97 C21 88 4 73 4 48 V13 Z" class="cr-shield"/>'
            '<path d="M43 9 L76 17.5 V48 C76 69 61.5 82 43 90 C24.5 82 10 69 10 48 V17.5 Z" class="cr-inner"/>'
            f'<text class="lvl" x="43" y="31" text-anchor="middle" font-size="9">LEVEL</text>'
            f'<text class="lv" x="43" y="{70 if size < 40 else 72}" text-anchor="middle" font-size="{size}">{lv}</text></svg>')


def svg_map(places, route, current_id, rel):
    """An original map of the story's country. Regions are drawn here; points come from places.json."""
    P = {p["id"]: p for p in places}
    out = ['<svg class="map" viewBox="0 0 400 300" role="img" aria-label="Map of Darrow\'s country">',
           '<defs><pattern id="ash" width="6" height="6" patternUnits="userSpaceOnUse"><path d="M0 6 L6 0" class="mp-hatch"/></pattern>'
           '<pattern id="wood" width="14" height="14" patternUnits="userSpaceOnUse"><path d="M7 2 L11 10 L3 10 Z" class="mp-tree"/></pattern></defs>',
           '<rect x="0" y="0" width="400" height="300" class="mp-bg"/>',
           # the sea and the coast, west
           '<path d="M0 0 L58 0 C48 40 70 70 56 110 C44 150 66 190 52 230 C42 260 62 280 54 300 L0 300 Z" class="mp-sea"/>',
           '<path d="M58 0 C48 40 70 70 56 110 C44 150 66 190 52 230 C42 260 62 280 54 300" class="mp-coast"/>',
           # the peaks, north
           '<path d="M120 62 L138 34 L152 56 L166 28 L182 54 L200 22 L218 54 L234 30 L250 58 L266 36 L280 62" class="mp-peaks"/>',
           '<path d="M130 70 L146 50 L160 68 M236 68 L252 48 L268 68" class="mp-peaks2"/>',
           # the Edgemoor hills, west
           '<path d="M54 104 C62 92 76 92 84 104 M72 112 C80 100 94 100 102 112" class="mp-hills"/>',
           # the Thornwild, east
           '<path d="M318 96 C340 90 372 96 392 106 L396 232 C370 226 344 236 320 226 C312 190 310 140 318 96 Z" class="mp-wood"/>',
           # a grey waste in the south-east: drawn as terrain, never labelled, until the page names it
           '<path d="M272 218 C300 212 340 236 372 240 L368 282 C334 278 300 286 272 272 Z" class="mp-ash"/>',
           # the Wend
           '<path d="M98 186 C130 180 160 204 196 196 C230 188 262 200 300 190 C330 182 356 190 396 176" class="mp-river"/>',
           '<path d="M300 182 L300 198 M292 184 L292 196 M308 184 L308 196" class="mp-stones"/>',
           # the Holloway
           '<path d="M214 118 C206 150 212 190 210 222 C209 240 213 250 214 258" class="mp-road"/>',
           # the Thousand Steps
           '<path d="M200 68 L212 74 L198 80 L212 86 L198 92 L212 98 L200 104 L214 110 L214 118" class="mp-steps"/>',
           ]
    # route traveled
    pts = []
    for r in route:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            pts.append((r[0], r[1]))
        elif r in P:
            pts.append((P[r]["x"], P[r]["y"]))
    if pts:
        d = " ".join(f"{'M' if i == 0 else 'L'}{x} {y}" for i, (x, y) in enumerate(pts))
        out.append(f'<path d="{d}" class="mp-route"/>')
    # region labels (map only)
    for p in places:
        if p.get("kind") in ("region", "forest", "waste", "mountains", "river", "road", "hills", "stair"):
            cls = "mp-lbl region" + ("" if p.get("on_page") else " faint")
            out.append(f'<text x="{p["x"]}" y="{p["y"]}" text-anchor="{esc(p.get("anchor", "middle"))}" class="{cls}">{esc(p.get("label") or p["name"])}</text>')
    for p in places:
        if p.get("draw") is False or p.get("kind") in ("region", "forest", "waste", "mountains", "river", "road", "hills", "stair"):
            continue
        x, y = p["x"], p["y"]
        cur = p["id"] == current_id
        vis = p.get("visited")
        cls = "mp-pt" + (" visited" if vis else "") + (" current" if cur else "") + ("" if p.get("on_page") else " faint")
        out.append(f'<g class="{cls}">')
        if cur:
            out.append(f'<circle cx="{x}" cy="{y}" r="9" class="mp-ring"/>')
        if p.get("kind") == "city":
            out.append(f'<path d="M{x-5} {y+4} L{x-5} {y-3} L{x} {y-8} L{x+5} {y-3} L{x+5} {y+4} Z" class="mp-dot"/>')
        elif p.get("kind") == "house":
            out.append(f'<path d="M{x-5} {y+4} L{x-5} {y-2} L{x} {y-7} L{x+5} {y-2} L{x+5} {y+4} Z M{x} {y-11} L{x} {y-7}" class="mp-dot"/>')
        else:
            out.append(f'<circle cx="{x}" cy="{y}" r="3.2" class="mp-dot"/>')
        anchor = "end" if x > 330 else ("start" if x < 70 else "middle")
        dy = -11 if p.get("kind") in ("city", "house") else -8
        dx = 0
        if p.get("label_below"):
            dy = 14
        if cur:  # the current place sits clear of the terrain, to the right of its marker
            anchor, dx, dy = "start", 12, 4
        out.append(f'<text x="{x + dx}" y="{y + dy}" text-anchor="{anchor}" class="mp-lbl">{esc(p.get("label") or p["name"])}</text>')
        out.append("</g>")
    out.append("</svg>")
    return "".join(out)


def rope_knots(tied, knots):
    """The Knots as a rope: tied knots lit with the temper gradient."""
    out = ['<svg class="rope" viewBox="0 0 400 44" role="img" aria-label="Knots tied: ' + f'{len(tied)} of {len(knots)}">']
    out.append('<defs><linearGradient id="temper" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="var(--t1)"/>'
               '<stop offset=".22" stop-color="var(--t2)"/><stop offset=".45" stop-color="var(--t3)"/><stop offset=".63" stop-color="var(--t4)"/>'
               '<stop offset=".82" stop-color="var(--t5)"/><stop offset="1" stop-color="var(--t6)"/></linearGradient></defs>')
    out.append('<path d="M10 22 L390 22" class="rp-line"/>')
    n = len(knots)
    for k in knots:
        x = 10 + (k["n"] - 0.5) * (380 / n)
        on = k["n"] in tied
        out.append(f'<g class="rp-knot{" on" if on else ""}" style="--i:{k["n"]}">')
        out.append(f'<path d="M{x-10} 22 C{x-10} 10 {x+10} 10 {x+10} 22 C{x+10} 34 {x-10} 34 {x-10} 22" class="rp-k"/>')
        out.append(f'<text x="{x}" y="42" text-anchor="middle" class="rp-n">{roman(k["n"])}</text></g>')
    out.append("</svg>")
    return "".join(out)


# ============================================================ components
def chip(text, cls=""):
    return f'<span class="chip {cls}">{esc(text)}</span>'


def badge(text, cls="dim"):
    return f'<span class="state {cls}">{esc(text)}</span>'


def bar(have, need, label, cls="", show=None, text=None):
    """A progress bar. text: what screen readers hear instead of the numbers (used for approval, which is never shown as a number)."""
    need = max(need, 1)
    pct = max(0, min(100, 100.0 * have / need))
    txt = f'<span class="num">{show}</span>' if show is not None else ""
    if text is not None:
        aria = f'role="img" aria-label="{esc(label)}: {esc(text)}"'
    else:
        aria = f'role="progressbar" aria-label="{esc(label)}" aria-valuemin="0" aria-valuemax="{need}" aria-valuenow="{have}"'
    return (f'<div class="bar-row"><div class="bar-l"><span>{esc(label)}</span>{txt}</div>'
            f'<div class="bar {cls}" {aria}><i style="--w:{pct:.1f}%"></i></div></div>')


def pips(have, need, cls=""):
    s = "".join(f'<span class="pip{" on" if i < have else ""}"></span>' for i in range(need))
    return f'<span class="pips {cls}" role="img" aria-label="{have} of {need}">{s}</span>'


BEARING_LABEL = "who his choices are making him"  # the site's own label for the Bearing section (exempt from the GM-sentence check)


def sec(title, label, inner, cls="", hid=""):
    hid = f' id="{hid}"' if hid else ""
    return (f'<section class="sec {cls}"{hid}><div class="sec-h"><h2>{esc(title)}</h2>'
            f'<span class="lbl">{esc(label)}</span></div>{inner}</section>')


def details(summary, inner, open_=False):
    return f'<details{" open" if open_ else ""}><summary>{esc(summary)}</summary><div class="dt-body">{inner}</div></details>'


STATUS_CLS = {"alive": "good", "fallen": "bad", "hollowed": "sealed", "missing": "warn", "unknown": "dim"}

APPROVAL_WORDS = [(75, "devoted"), (50, "loyal"), (25, "fond"), (10, "warming"), (0, "civil"),
                  (-10, "wary"), (-25, "cold"), (-50, "hostile"), (-101, "an enemy")]


def approval_word(a):
    for t, w in APPROVAL_WORDS:
        if a >= t:
            return w
    return "an enemy"


TIER_WORDS = {"Triumph": "The chapter is his, so far.", "Hard-won": "Hard-won, so far.",
              "Costly": "Costly, so far.", "Setback": "The chapter is turning against him."}
TIER_DONE = {"Triumph": "A triumph", "Hard-won": "Hard-won", "Costly": "Costly", "Setback": "A setback"}


# ============================================================ page shell
CUR = ' aria-current="page"'
NAV = [("Now", "index.html"), ("Chronicle", "chronicle/index.html"), ("Characters", "characters/index.html"),
       ("Darrow", "darrow/index.html"), ("Codex", "codex/index.html")]
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Grenze+Gotisch:wght@500;700&family=Alegreya+Sans:ital,wght@0,400;0,500;0,700;1,400&family=Alegreya+Sans+SC:wght@500;700&display=swap">')


def shell(title, body, rel, current, cls="", desc=""):
    nav = "".join(f'<a href="{rel}{href}"{CUR if name == current else ""}>{name}</a>' for name, href in NAV)
    meta_desc = f'<meta name="description" content="{esc(desc)}">' if desc else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="dark">
<title>{esc(title)} · The Unkneeling</title>
{meta_desc}
{FONTS}
<link rel="stylesheet" href="{rel}site.css">
</head>
<body class="{cls}">
<a class="skip" href="#main">Skip to content</a>
<div class="progress" aria-hidden="true"><i></i></div>
<header class="mast"><div class="wrap mast-in"><a class="brand" href="{rel}index.html">The Unkneeling</a><nav class="nav" aria-label="Site">{nav}</nav></div></header>
<main id="main" class="wrap">
{body}
</main>
<footer class="foot"><div class="wrap"><p>What is given can be taken. What is built is yours.</p><p class="faint">An original saga. The Chronicle is kept as it happens; the Reckoning is read, never written.</p></div></footer>
<script src="{rel}site.js" defer></script>
</body>
</html>
"""


# ============================================================ the build
class Site:
    def __init__(self):
        self.rules = load_json(RULES)
        self.world = load_json(STATE / "world.json")
        self.darrow = load_json(STATE / "darrow.json")
        pl = load_json(STATE / "places.json")
        self.places = pl["places"]
        self.place_by_id = {p["id"]: p for p in self.places}
        self.route = pl.get("route", [])
        self.factions = {f["id"]: f for f in load_json(STATE / "factions.json")["factions"]}
        self.chapters_csv = load_csv(STATE / "chapters.csv") if (STATE / "chapters.csv").exists() else []
        self.rolls = load_csv(STATE / "rolls.csv") if (STATE / "rolls.csv").exists() else []
        self.chapters = [parse_chapter(p) for p in sorted(CHRON.glob("*.md"))]
        cur = Path(str(self.world.get("chapter_file") or "")).name
        for c in self.chapters:
            if c["empty"] and c["file"] != cur:
                problem(f"{c['file']}: no scenes found (headings are '## I. Title' for prologue parts or '### Scene N — Title'); "
                        f"only the current chapter ({cur or 'world.json chapter_file'}) may wait for its first scene")
        self.registry = {}
        for ch in self.chapters:
            for s in ch["scenes"]:
                self.registry[(ch["code"], s["key"])] = {
                    "href": f"chronicle/{ch['slug']}.html#{s['anchor']}", "chapter": ch, "scene": s,
                    "label": (f"{ch['label']} · {s['label']}" if s["label"] else ch["label"]) + (f" — {s['title']}" if s["title"] else "")}
        self.chapter_by_number = {ch["number"]: ch for ch in self.chapters}
        self.bearing = self.load_bearing()
        self.check_world()
        self.chars = load_characters(self.registry, self.factions, self.place_by_id)
        self.pages = {}  # path -> html
        loc = self.world.get("location") or {}
        self.current_place = loc.get("place") if isinstance(loc, dict) else None
        if self.current_place not in self.place_by_id:
            problem(f"world.json: location.place '{self.current_place}' is not in places.json")
        if not (self.world.get("current_quest") or {}).get("on_the_page"):
            problem("world.json: current_quest.on_the_page is missing (the site shows only page-supported text)")
        for p in self.places:
            for k in ("id", "name", "kind", "x", "y"):
                if k not in p:
                    problem(f"places.json: place {p.get('id', '?')} is missing '{k}'")
            if p.get("on_page") and not p.get("description"):
                problem(f"places.json: {p.get('id')} is on the page but has no description")
        for key, comp in (self.world.get("companions") or {}).items():
            if not isinstance(comp, dict):
                problem(f"world.json: companions.{key} must be an object")
                continue
            hits = [c for c in self.chars if c.split("-")[0] == key]
            if len(hits) > 1:
                problem(f"world.json: companions.{key} matches more than one character file ({', '.join(hits)})")
        self.codex = self.parse_codex()
        self.eye = next((a["rank"] for a in self.darrow.get("arts", []) if a["id"] == "wardens_eye"), 0)
        self.linkers = self.build_linkers()

    # ---------------------------------------------------------------- helpers
    WORLD_GM_KEYS = ("chapter_plan", "core_beats", "flags", "factions")
    CHOICE_KEYS = ("chapter", "scene", "kind", "option", "ledger")

    def load_bearing(self):
        """saga/state/bearing.json, if it exists: four axes {value, left, right}, names, epithet. Missing file → no Bearing on the site.
        The epithet is rendered, so it must already be spoken in the chronicle; the names table is never rendered."""
        path = STATE / "bearing.json"
        if not path.exists():
            note("bearing.json not found: the Bearing section is skipped")
            return None
        try:
            b = load_json(path)
        except json.JSONDecodeError as e:
            problem(f"bearing.json: invalid JSON ({e})")
            return None
        axes = b.get("axes")
        if not isinstance(axes, dict) or not axes:
            problem("bearing.json: 'axes' must be a non-empty object")
            return None
        rng = b.get("range", 10)
        if not isinstance(rng, int) or rng <= 0:
            problem(f"bearing.json: range must be a positive integer (got {rng!r})")
            return None
        for aid, ax in axes.items():
            if not isinstance(ax, dict) or not all(k in ax for k in ("value", "left", "right")):
                problem(f"bearing.json: axis '{aid}' needs value, left and right")
                continue
            if not isinstance(ax["value"], int) or abs(ax["value"]) > rng:
                problem(f"bearing.json: axis '{aid}' value {ax['value']!r} is not an integer within ±{rng}")
        names = b.get("names") or {}
        if not isinstance(names, dict):
            problem("bearing.json: 'names' must be an object of pole → epithet")
        ep = b.get("epithet")
        if ep is not None and not isinstance(ep, str):
            problem(f"bearing.json: epithet must be a string or null (got {ep!r})")
        elif ep is not None:
            if ep not in names.values():
                problem(f"bearing.json: epithet {ep!r} is not one of the names")
            chron_text = "\n".join(read(p) for p in sorted(CHRON.glob("*.md")))
            if ep.strip().lower() not in chron_text.lower():
                problem(f"bearing.json: epithet {ep!r} has not been spoken in the chronicle yet; "
                        "write it into the scene that earns it before it can show on the site (or set epithet to null)")
        return b

    def check_world(self):
        """The reader-safe world.json: no GM keys, a chapter_file the chronicle has, well-formed choices that point at scenes the chronicle has."""
        w = self.world
        for k in self.WORLD_GM_KEYS:
            if k in w:
                problem(f"world.json: GM key '{k}' does not belong in the reader-safe file (it lives in saga/state/_gm/plan.json)")
        cf = w.get("chapter_file")
        cur_slug = str(cf or "").split("/")[-1].replace(".md", "")
        if not cur_slug:
            problem("world.json: chapter_file is missing (the Now page needs the current chapter)")
        elif not any(ch["slug"] == cur_slug for ch in self.chapters):
            problem(f"world.json: chapter_file {cf!r} is not a chronicle file (have: "
                    f"{', '.join(ch['slug'] + '.md' for ch in self.chapters) or 'none'})")
        if isinstance(w.get("current_quest"), dict) and "summary" in w["current_quest"]:
            problem("world.json: current_quest.summary is GM text; keep only name and on_the_page (the summary lives in _gm/plan.json)")
        choices = w.get("choices")
        if choices is None:
            choices = []
        if not isinstance(choices, list):
            problem("world.json: choices must be a list")
            return
        for i, c in enumerate(choices):
            if not isinstance(c, dict):
                problem(f"world.json: choices[{i}] is not an object")
                continue
            missing = [k for k in self.CHOICE_KEYS if k not in c]
            if missing:
                problem(f"world.json: choices[{i}] is missing {', '.join(missing)} (every choice needs {', '.join(self.CHOICE_KEYS)})")
                continue
            chn = as_int(c.get("chapter"))
            if chn is None:
                problem(f"world.json: choices[{i}].chapter {c.get('chapter')!r} is not a chapter number")
                continue
            if c.get("kind") not in ("climax", "micro"):
                problem(f"world.json: choices[{i}].kind must be 'climax' or 'micro' (got {c.get('kind')!r})")
            if c.get("by") not in (None, "darrow", "bearing"):
                problem(f"world.json: choices[{i}].by must be 'darrow' or 'bearing' (got {c.get('by')!r})")
            opt = c.get("option")
            if opt is not None and as_int(opt) is None:
                problem(f"world.json: choices[{i}].option {opt!r} is neither a list number nor null")
            if as_int(opt) is None and not (c.get("text") or "").strip():
                problem(f"world.json: choices[{i}] has no option number and no text; one of them must say what was chosen")
            ch = self.chapter_by_number.get(chn)
            if ch is None:
                problem(f"world.json: choices[{i}] points at chapter {chn}, which is not in the chronicle")
                continue
            key = (ch["code"], str(c.get("scene")))
            if key not in self.registry:
                problem(f"world.json: choices[{i}].scene {c.get('scene')!r} is not a scene key of {ch['label']} "
                        f"(keys: {', '.join(s['key'] for s in ch['scenes'])})")
            elif not any(b[0] == "ol" and b[2] for b in self.registry[key]["scene"]["blocks"]):
                problem(f"world.json: choices[{i}] answers {ch['label']} scene {c.get('scene')!r}, which has no choice list on the page")

    def choice_for(self, ch, scene_key):
        """The recorded choice for one choice block: strict match on (chapter as int, scene key)."""
        for c in self.world.get("choices") or []:
            if as_int(c.get("chapter")) == ch["number"] and str(c.get("scene")) == str(scene_key):
                return c
        return None

    @staticmethod
    def choice_title(block_kind, rec=None, scene_key=None):
        """'The choice' for the chapter's climax (the climax/choice scene keys, whatever the heading word says, or a recorded
        climax); 'A small choice' for a micro (a 'say' heading, a recorded micro, or a list inside a daily scene)."""
        if scene_key is not None and str(scene_key) in ("climax", "choice"):
            return "The choice"
        if block_kind == "say" or (rec and rec.get("kind") == "micro"):
            return "A small choice"
        if rec and rec.get("kind") == "climax":
            return "The choice"
        if scene_key is not None:
            return "A small choice"
        return "The choice"

    def char_href(self, cid):
        return "darrow/index.html" if cid == "darrow" else f"characters/{cid}.html"

    def build_linkers(self):
        pats = []
        for cid, c in self.chars.items():
            name_tokens = {t.lower().strip("'") for t in re.split(r"[\s-]+", c["name"]) if len(t) > 2 and t.lower() not in ("ser", "the", "of")}
            names = [c["name"]]
            if c["name"].startswith("Ser "):
                names.append(c["name"][4:])
            for a in c.get("aliases") or []:
                toks = {t.lower() for t in re.split(r"[\s-]+", a)}
                if toks & name_tokens:
                    names.append(a)
            for nm in names:
                variants = {nm}
                if nm.lower().startswith("the "):
                    variants.add("The " + nm[4:])
                    variants.add("the " + nm[4:])
                for v in variants:
                    pats.append((v, cid))
        pats.sort(key=lambda t: -len(t[0]))
        self.alias_to_id = {esc(p): cid for p, cid in pats}
        if pats:
            self.name_re = re.compile(r"(?<![\w-])(" + "|".join(re.escape(esc(p)) for p, _ in pats) + r")(?![\w-])")
        else:
            self.name_re = None
        return pats

    def link_names(self, frag, seen, rel, exclude=None):
        if not self.name_re:
            return frag
        parts = re.split(r"(<[^>]+>)", frag)
        out, in_a = [], 0
        for part in parts:
            if part.startswith("<"):
                if re.match(r"<a[\s>]", part):
                    in_a += 1
                elif part.startswith("</a"):
                    in_a = max(0, in_a - 1)
                out.append(part)
                continue
            if in_a:
                out.append(part)
                continue

            def repl(m):
                cid = self.alias_to_id.get(m.group(1))
                if not cid or cid == exclude or cid in seen:
                    return m.group(1)
                seen.add(cid)
                return f'<a class="nm" href="{rel}{self.char_href(cid)}">{m.group(1)}</a>'
            out.append(self.name_re.sub(repl, part))
        return "".join(out)

    def scene_ref(self, ref, rel):
        key = (str(ref.get("chapter")), str(ref.get("scene")))
        r = self.registry.get(key)
        if not r:
            return esc(f"chapter {ref.get('chapter')} scene {ref.get('scene')}")
        return f'<a href="{rel}{r["href"]}">{esc(r["label"])}</a>'

    def parse_codex(self):
        text = read(STATE / "codex.md")
        sections, cur = {}, None
        for raw in text.splitlines():
            ln = re.sub(r"⟪\s*gm\b[^⟫]*⟫", "", raw, flags=re.I)
            if "⟪" in ln or "⟫" in ln:
                problem(f"codex.md: unbalanced or mis-typed ⟪gm: … ⟫ aside in line: {raw[:60]!r}")
                continue
            if ln.startswith("## "):
                cur = ln[3:].strip()
                sections[cur] = []
            elif cur and re.match(r"^\s*[-*]\s", ln):
                m = re.match(r"^\s*[-*]\s+\*\*(.+?)\*\*\s*[—–:-]\s*(.+)$", ln)
                if m:
                    sections[cur].append({"name": m.group(1).strip(), "text": m.group(2).strip()})
                else:
                    problem(f"codex.md: entry under '{cur}' is not '- **Name** — text': {ln[:60]!r}")
        return sections

    # ---------------------------------------------------------------- chronicle rendering
    def render_blocks(self, ch, scene, rel, seen):
        out = []
        for b in scene["blocks"]:
            kind = b[0]
            if kind == "p":
                out.append(f"<p>{self.link_names(inline(b[1]), seen, rel)}</p>")
            elif kind == "h":
                out.append(f"<h3>{inline(b[1])}</h3>")
            elif kind == "hr":
                out.append('<hr class="break">')
            elif kind == "orn":
                out.append('<div class="ornament" role="separator">✶ ✶ ✶</div>')
            elif kind == "reck":
                lines = "".join(f"<p>{inline(x)}</p>" for x in b[1] if x)
                out.append(f'<aside class="reckoning"><p class="rk-h">⟦ THE RECKONING ⟧</p>{lines}</aside>')
            elif kind == "quote":
                lines = "".join(f"<p>{self.link_names(inline(x), seen, rel)}</p>" for x in b[1] if x)
                out.append(f"<blockquote>{lines}</blockquote>")
            elif kind == "dice":
                out.append(f'<div class="dice"><span class="dice-tag">{esc(b[1])}</span> <span class="dice-body">{inline(b[2])}</span></div>')
            elif kind == "choice-h":
                out.append(f'<h3 class="choice-h">{esc(b[1])}</h3>')
            elif kind == "ol":
                items, is_choice = b[1], b[2]
                taken, free, by_self = None, None, False
                if is_choice:
                    rec = self.choice_for(ch, scene["key"])
                    if rec:
                        taken = as_int(rec.get("option"))
                        free = rec.get("text") if taken is None else None
                        by_self = rec.get("by") == "bearing"
                mark = ' <span class="state good">chosen</span>' + (' <span class="state dim">answered for himself</span>' if by_self else "")
                lis = []
                for i, it in enumerate(items, 1):
                    cls = ' class="taken"' if taken == i else ""
                    lis.append(f"<li{cls}>{inline(it)}{mark if taken == i else ''}</li>")
                out.append(f'<ol class="{"choice" if is_choice else ""}">{"".join(lis)}</ol>')
                if free:
                    out.append(f'<p class="chosen-free">{mark.strip()} {esc(free)}</p>')
            elif kind == "ul":
                out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in b[1]) + "</ul>")
        return "".join(out)

    def render_chapter(self, idx):
        ch = self.chapters[idx]
        rel = "../"
        prev_ch = self.chapters[idx - 1] if idx > 0 else None
        next_ch = self.chapters[idx + 1] if idx + 1 < len(self.chapters) else None
        head = []
        recap = (self.world.get("recaps") or {}).get(ch["slug"])
        if recap:
            head.append(f'<p class="previously"><span class="lbl">Previously</span> {esc(recap)}</p>')
        if ch["book"]:
            head.append(f'<p class="book-line">{esc(ch["book"])}</p>')
        head.append(f'<h1 class="ch-title"><span class="lbl">{esc(ch["label"])}</span>{esc(ch["title"])}</h1>')
        if ch["epigraph"]:
            lines = "".join(f"<p>{inline(x)}</p>" for x in ch["epigraph"]["lines"])
            src = f'<figcaption>— {inline(ch["epigraph"]["source"])}</figcaption>' if ch["epigraph"]["source"] else ""
            head.append(f'<figure class="epigraph"><blockquote>{lines}</blockquote>{src}</figure>')
        body = []
        for s in ch["scenes"]:
            seen = set()
            lab = f'<span class="scene-n">{esc(s["label"])}</span>' if s["label"] else ""
            title = esc(s["title"]) if s["title"] else ""
            body.append(f'<section class="scene" id="{s["anchor"]}"><h2 class="scene-h">{lab}{title}</h2>{self.render_blocks(ch, s, rel, seen)}</section>')
        cast = [c for c in self.chars.values() if any(str(a.get("chapter")) == ch["code"] and not a.get("mention") for a in c.get("appearances") or [])]
        cast_html = ""
        if cast:
            cast_html = '<div class="cast"><span class="lbl">On the page in this chapter</span><div class="chips">' + "".join(
                f'<a class="chip brass" href="{rel}{self.char_href(c["id"])}">{esc(c["name"])}</a>' for c in cast) + "</div></div>"
        nav = '<nav class="pager" aria-label="Chapters">'
        nav += f'<a href="{rel}chronicle/{prev_ch["slug"]}.html"><span class="lbl">Previous</span>{esc(prev_ch["label"] + " — " + prev_ch["title"])}</a>' if prev_ch else '<span></span>'
        nav += f'<a class="next" href="{rel}chronicle/{next_ch["slug"]}.html"><span class="lbl">Next</span>{esc(next_ch["label"] + " — " + next_ch["title"])}</a>' if next_ch else f'<a class="next" href="{rel}index.html"><span class="lbl">The story continues</span>Back to Now</a>'
        nav += "</nav>"
        page = f'<article class="reader">{"".join(head)}{"".join(body)}</article>{cast_html}{nav}'
        self.pages[f"chronicle/{ch['slug']}.html"] = shell(f"{ch['label']} — {ch['title']}", page, rel, "Chronicle", "reader-page",
                                                           desc=f"{ch['label']} of The Unkneeling: {ch['title']}.")

    def render_chronicle_index(self):
        rel = "../"
        cur_slug = self.world.get("chapter_file", "").split("/")[-1].replace(".md", "")
        items = []
        book_shown = None
        for ch in self.chapters:
            if ch["book"] and ch["book"] != book_shown:
                book_shown = ch["book"]
                items.append(f'<li class="book"><b>{esc(ch["book"])}</b></li>')
            now = ch["slug"] == cur_slug
            scenes = "".join(
                f'<li><a href="{rel}chronicle/{ch["slug"]}.html#{s["anchor"]}">{esc((s["label"] + " — " if s["label"] else "") + s["title"])}</a></li>'
                for s in ch["scenes"] if s["title"] or s["label"])
            n_sc = len(ch["scenes"])
            count = "no scene yet" if ch["empty"] else f'{n_sc} scene{"s" if n_sc != 1 else ""} · about {ch["words"]:,} words'
            items.append(f'<li class="{"now" if now else ""}"><a class="ch-link" href="{rel}chronicle/{ch["slug"]}.html"><b>{esc(ch["label"])} — {esc(ch["title"])}</b></a>'
                         f'<span class="m num">{count}{" · now" if now else ""}</span>'
                         f'<ul class="scenes">{scenes}</ul></li>')
        first = self.chapters[0] if self.chapters else None
        start = f'<p><a class="btn" href="{rel}chronicle/{first["slug"]}.html">Start reading</a></p>' if first else ""
        body = f'<section class="plate"><p class="lbl">The Chronicle</p><h1>Books, chapters and scenes</h1><p class="dim">Read in order. The current chapter is marked in brass.</p>{start}</section>'
        n_num = sum(1 for c in self.chapters if c["number"])
        n_pro = len(self.chapters) - n_num
        count = (("a prologue and " if n_pro else "") + f"{n_num} chapter{'s' if n_num != 1 else ''}") if n_num else "a prologue"
        body += sec("Timeline", count, f'<ul class="chron">{"".join(items)}</ul>')
        self.pages["chronicle/index.html"] = shell("Chronicle", body, rel, "Chronicle", desc="The Unkneeling, by book, chapter and scene.")

    # ---------------------------------------------------------------- reckoning blocks
    def reckoning_of(self, c, rel):
        """The Reckoning as Darrow reads it, gated by his Warden's Eye rank."""
        rk = c.get("reckoning")
        eye = self.eye
        if c.get("tier") == "fallen":
            return '<div class="rk-card sealed-box"><p class="rk-h">⟦ THE RECKONING ⟧</p><p class="sealed-line">The script does not read those who did not come back.</p></div>'
        if rk is None:
            return '<div class="rk-card sealed-box"><p class="rk-h">⟦ THE RECKONING ⟧</p><p class="sealed-line">⟦ unread ⟧</p></div>'
        fire = (rk.get("fire") or {})
        kind = fire.get("kind", "none")
        kcls = {"grace": "borrowed", "ember": "earned", "none": "unlit"}.get(kind, "unlit")
        unread = '<span class="sealed-line">⟦ unread ⟧</span>'
        rows = []
        if eye >= 1:
            lvl = rk.get("level")
            head = f'Level {lvl} · {esc(rk.get("rank"))}' if lvl is not None else esc(rk.get("rank") or "")
            rows.append(f'<p class="rk-line">{head}</p>')
        else:
            rows.append(f'<p class="rk-line">{unread}</p>')
        if eye >= 2:
            at = rk.get("attributes") or {}
            cells = "".join(f'<div class="rk-attr {kcls}"><span class="lbl">{k.capitalize()}</span><span class="v num">{at.get(k, "—")}</span></div>'
                            for k in ("might", "vigor", "finesse", "resolve"))
            rows.append(f'<div class="rk-attrs">{cells}</div>')
            fl = {"grace": "Grace", "ember": "Ember", "none": "Unlit"}[kind]
            rows.append(f'<p class="rk-line {kcls}"><span class="lbl">{fl}</span> {esc(fire.get("state", ""))}' + (' <span class="chip blue">borrowed</span>' if kind == "grace" else "") + "</p>")
        else:
            rows.append(f'<p class="rk-line"><span class="lbl">Might · Vigor · Finesse · Resolve</span> {unread}</p>')
            rows.append(f'<p class="rk-line"><span class="lbl">The fire</span> {unread}</p>')
        if eye >= 3:
            arts = rk.get("arts") or []
            rows.append('<p class="rk-line"><span class="lbl">Arts</span> ' + (" · ".join(f"{esc(a['name'])} {roman(int(a.get('rank', 0)))}" for a in arts) if arts else "none") + "</p>")
        else:
            rows.append(f'<p class="rk-line"><span class="lbl">Arts</span> {unread}</p>')
        if eye >= 4:
            for d in rk.get("deeper") or []:
                rows.append(f'<p class="rk-line deeper">{esc(d)}</p>')
        else:
            rows.append(f'<p class="rk-line"><span class="lbl">Deeper</span> {unread}</p>')
        ranks = " · ".join(r["name"] for r in self.rules["levels"]["ranks"][:3])
        note_ = (f'<p class="hint">Read with Warden\'s Eye {roman(eye)}. Stronger sight reads deeper. '
                 f'The ranks of the Ember run {esc(ranks)} and up; Oathsworn is borrowed strength.</p>')
        return f'<div class="rk-card"><p class="rk-h">⟦ THE RECKONING ⟧</p>{"".join(rows)}{note_}</div>'

    # ---------------------------------------------------------------- characters
    def identity_plate(self, c, rel, level):
        f = self.factions.get(c["faction"], {})
        sg = c.get("sigil") or {}
        chips = [chip(f.get("name", c["faction"]), "brass")]
        if c["id"] == "darrow":
            chips.append(chip("the Faithless"))
            ep = (self.bearing or {}).get("epithet")
            if ep:
                chips.append(chip(ep, "ember"))
        chips.append(badge(c["status"], STATUS_CLS.get(c["status"], "dim")))
        fac = self.factions.get(sg.get("faction"), {})
        if c["tier"] == "fallen":
            cr = sigil(fac, sg.get("mark"), 86, "big", c["name"])
            row = f'<div class="sigil-row"><span class="sealed-line">in memory</span><span class="dim">{esc(f.get("name", ""))}</span></div>'
        else:
            cr = crest(level if level is not None else "?")
            row = f'<div class="sigil-row">{sigil(fac, sg.get("mark"), 44)}<span class="dim">{esc(f.get("name", ""))}</span></div>'
        return (f'<section class="plate"><div class="hero">{cr}<div class="who"><h1>{esc(c["name"])}</h1>'
                f'<p class="sub">{esc(c.get("epithet", ""))}</p><div class="chips">{"".join(chips)}</div></div></div>{row}</section>')

    def character_sections(self, c, rel):
        parts = []
        minor = c.get("tier") == "minor"
        mention_only = all(a.get("mention") for a in c.get("appearances") or []) and bool(c.get("appearances"))
        parts.append(sec("Appearance", "in brief", f'<p class="prose">{esc(c["appearance"])}</p>'))
        ls = c.get("last_seen") or {}
        pl = self.place_by_id.get(ls.get("place"), {})
        ref = self.scene_ref(ls, rel)
        where = f' · {esc(pl["name"])}' if pl and pl["name"].lower() not in re.sub(r"<[^>]+>", "", ref).lower() else ""
        parts.append(sec("Named in" if mention_only else "Last seen", "on the page", f'<p class="prose">{ref}{where}</p><p class="prose dim">{esc(c.get("last_seen_doing", ""))}</p>'))
        parts.append(sec("Now", "as far as the reader knows", f'<p class="prose">{esc(c["now"])}</p>'))
        parts.append(sec("Story so far", "spoiler-free", f'<p class="prose">{esc(c["story_so_far"])}</p>'))
        q = c.get("quote")
        if q and q.get("text"):
            parts.append(sec("Quote", "", f'<figure class="quote"><blockquote><p>{esc(q["text"])}</p></blockquote><figcaption>{self.scene_ref(q, rel)}</figcaption></figure>'))
        elif not minor:
            parts.append(sec("Quote", "", '<p class="empty">No line of theirs is on the page yet.</p>'))
        rels = []
        comp = (self.world.get("companions") or {}).get(c["id"].split("-")[0]) if c["id"] != "darrow" else None
        if comp and "approval" in comp:
            a = int(comp["approval"])
            rels.append(f'<li class="rel"><div class="rel-top"><b>Toward Darrow</b><span class="lbl">{esc(approval_word(a))}</span></div>'
                        f'{bar(a + 100, 200, "Regard for Darrow", "approval", text=approval_word(a))}</li>')
        for r in c.get("relationships") or []:
            to = r.get("to", "")
            if to in self.chars:
                who = f'<a href="{rel}{self.char_href(to)}">{esc(self.chars[to]["name"])}</a>'
            else:
                who = esc(to)
            rels.append(f'<li class="rel"><div class="rel-top"><b>{who}</b><span class="lbl">{esc(r.get("label", ""))}</span></div><p class="dim">{esc(r.get("note", ""))}</p></li>')
        if rels or not minor:
            parts.append(sec("Relationships", "as seen on the page", f'<ul class="rels">{"".join(rels)}</ul>' if rels else '<p class="empty">None on the page yet.</p>'))
        if c["id"] != "darrow":
            parts.append(sec("The Reckoning", "as Darrow reads it", self.reckoning_of(c, rel)))
        facts = c.get("known_facts") or []
        fl = "".join(f'<li><span>{esc(f["fact"])}</span><span class="src">{self.scene_ref(f, rel)}</span></li>' for f in facts)
        parts.append(sec("Known facts", f"{len(facts)}", details(f"What the page has shown ({len(facts)})", f'<ul class="facts">{fl}</ul>') if facts else '<p class="empty">Nothing yet.</p>'))
        apps, n_present, n_named = [], 0, 0
        for a in c.get("appearances") or []:
            r = self.registry.get((str(a.get("chapter")), str(a.get("scene"))))
            if r:
                named = bool(a.get("mention"))
                n_named += named
                n_present += not named
                tag = ' <span class="state dim">named</span>' if named else ""
                apps.append(f'<li class="{"named" if named else ""}"><a href="{rel}{r["href"]}"><b>{esc(r["chapter"]["label"])}</b><span class="m">{esc((r["scene"]["label"] + " — " if r["scene"]["label"] else "") + r["scene"]["title"])}{tag}</span></a></li>')
        label = f"{n_present} scene{'s' if n_present != 1 else ''}" + (f" · named in {n_named}" if n_named else "")
        parts.append(sec("Appearances", label, f'<ul class="chron">{"".join(apps)}</ul>'))
        return "".join(parts)

    def render_character(self, c):
        rel = "../"
        rk = c.get("reckoning")
        level = None
        if c["tier"] != "fallen" and isinstance(rk, dict) and self.eye >= 1:
            level = rk["level"] if rk.get("level") is not None else "—"
        body = self.identity_plate(c, rel, level) + self.character_sections(c, rel)
        ep = c.get("epithet", "")
        ep = ep[0].lower() + ep[1:] if ep[:2] in ("A ", "An", "Th") else ep
        self.pages[f"characters/{c['id']}.html"] = shell(c["name"], body, rel, "Characters", "char-page",
                                                        desc=f"{c['name']}, as the Chronicle has shown: {ep}.")

    def card(self, c, rel):
        f = self.factions.get(c["faction"], {})
        sg = c.get("sigil") or {}
        ls = c.get("last_seen") or {}
        r = self.registry.get((str(ls.get("chapter")), str(ls.get("scene"))))
        last = esc(r["label"]) if r else ""
        mention_only = bool(c.get("appearances")) and all(a.get("mention") for a in c.get("appearances"))
        seen_lbl = "Named in" if mention_only else "Last seen"
        return (f'<a class="card" href="{rel}{self.char_href(c["id"])}" data-faction="{esc(c["faction"])}" data-status="{esc(c["status"])}">'
                f'{sigil(self.factions.get(sg.get("faction"), {}), sg.get("mark"), 56)}<div class="card-body"><b>{esc(c["name"])}</b><span class="dim">{esc(c.get("epithet", ""))}</span>'
                f'<div class="chips">{badge(c["status"], STATUS_CLS.get(c["status"], "dim"))}{chip(f.get("name", ""))}</div>'
                f'<span class="m">{seen_lbl}: {last}</span></div></a>')

    def render_roster(self):
        rel = "../"
        order = {"major": 0, "minor": 1, "fallen": 2}
        chars = sorted(self.chars.values(), key=lambda c: (order.get(c["tier"], 3), c["id"] != "darrow", c["name"]))
        living = [c for c in chars if c["tier"] != "fallen"]
        fallen = [c for c in chars if c["tier"] == "fallen"]
        facs = sorted({c["faction"] for c in chars})
        stats = sorted({c["status"] for c in chars})
        filters = ('<div class="filters" data-filters><span class="fgrp"><span class="lbl">Faction</span>' + "".join(
            f'<button type="button" class="chip" data-filter="faction" data-value="{esc(f)}">{esc(self.factions.get(f, {}).get("name", f))}</button>' for f in facs)
            + '</span><span class="fgrp"><span class="lbl">Status</span>' + "".join(f'<button type="button" class="chip" data-filter="status" data-value="{esc(s)}">{esc(s)}</button>' for s in stats)
            + '</span><span class="fgrp"><button type="button" class="chip brass" data-filter="all">all</button></span></div>')
        body = f'<section class="plate"><p class="lbl">The cast</p><h1>Characters</h1><p class="dim">Everyone the page has shown or named. Nothing here runs ahead of the story.</p>{filters}</section>'
        body += sec("Roster", f"{len(living)}", '<div class="grid">' + "".join(self.card(c, rel) for c in living) + "</div>")
        if fallen:
            body += sec("The fallen", f"{len(fallen)}", '<div class="grid memorial">' + "".join(self.card(c, rel) for c in fallen) + "</div>", cls="memorial-sec")
        self.pages["characters/index.html"] = shell("Characters", body, rel, "Characters", desc="The cast of The Unkneeling, as the Chronicle has shown them.")

    # ---------------------------------------------------------------- darrow
    def darrow_reckoning(self, rel):
        d, rules = self.darrow, self.rules
        a = d["attributes"]
        xp_into = d["xp"] - d["xp_this_level"]
        xp_span = d["xp_next_level"] - d["xp_this_level"]
        n_knots = len(rules.get("knots") or []) or 7
        xp_show = f"{xp_into:,} / {xp_span:,}"
        plate = (f'<section class="plate"><div class="hero">{crest(d["level"])}<div class="who"><h2>The Reckoning</h2>'
                 f'<p class="sub">{esc(d["name"])} · Level {d["level"]} · {esc(d["rank"])} · XP {d["xp"]:,}</p>'
                 f'<div class="chips">{chip("HP " + str(d["hp_max"]), "")}{chip("Proficiency +" + str(d["proficiency"]))}{chip("Knots " + roman(d["knots_count"]) + " of " + roman(n_knots), "brass")}</div></div></div>'
                 f'{bar(xp_into, xp_span, "XP toward Level " + str(d["level"] + 1), "", xp_show)}'
                 f'<div class="row2"><div>{bar(d["ember"]["value"] or 0, 100, "Ember · " + str(d["ember"]["tier"] or "unlit"), "ember", d["ember"]["value"])}</div>'
                 f'<div class="insp"><span class="lbl">Inspiration</span>{pips(d["inspiration"], d["inspiration_cap"])}</div></div></section>')
        tiles = []
        for k in ("might", "vigor", "finesse", "resolve"):
            x = a[k]
            spec = rules["attributes"][k]
            prev = spec["divisor"] * (x["raw"] - spec["base"]) ** 2
            have = x["temper"] - prev
            need = x["next_at"] - prev
            cap = f'<span class="s sealed-line">held by the Binding at {x["cap"]}</span>' if x.get("banked") else ""
            tiles.append(f'<div class="stk{" hot" if x["score"] >= x["fell"] else ""}"><span class="v num">{x["score"]}<small>{x["mod"]:+d}</small></span>'
                         f'<span class="n">{k.capitalize()}</span><span class="s faint num">behind his own · {x["fell"]}</span>'
                         f'{bar(have, need, k.capitalize() + " temper", "temper")}<span class="s">temper {x["temper"]} · next at {x["next_at"]}</span>{cap}</div>')
        attrs = sec("Attributes", "against the fainter numbers behind his own", f'<div class="streaks">{"".join(tiles)}</div>')
        if self.bearing:
            attrs += sec("Bearing", BEARING_LABEL, self.bearing_html())
        trees = defaultdict(list)
        for art in d["arts"]:
            trees[art["tree"]].append(art)
        order = ["Blade", "Footing", "Breath", "Binding", "Insight", "Sport"]
        n_pips = len(rules.get("art_ranks") or [1, 6, 15, 30, 50])
        tree_html = []
        for tree in [x for x in order if x in trees] + sorted(x for x in trees if x not in order):
            arts = trees.get(tree)
            if not arts:
                continue
            rows = []
            for art in arts:
                sealed = art.get("sealed_until_knot")
                rank = art["rank"] if not sealed else art.get("banked_rank", 0)
                if sealed:
                    st = f'<span class="sealed-line">sealed until Knot {roman(sealed)}</span>' + (f' <span class="dim num">· {art["practice"]} days banked</span>' if art["practice"] else "")
                elif art["rank"] > 0:
                    st = f'<span class="brass">rank {roman(art["rank"])}</span>' + (f' <span class="dim num">· next at {art["next_at"]} days ({art["practice"]} so far)</span>' if art.get("next_at") else "")
                else:
                    st = f'<span class="dim">not yet learned</span>'
                rows.append(f'<li class="art{" sealed" if sealed else ""}{" on" if rank else ""}"><div class="art-top"><b>{esc(art["name"])}</b>{pips(rank, n_pips, "rank")}</div>'
                            f'<span class="m">{st}</span><span class="e">{esc(art["effect"])}</span></li>')
            tree_html.append(f'<div class="tree"><h3>{esc(tree)}</h3><ul class="arts">{"".join(rows)}</ul></div>')
        arts_sec = sec("Arts", "learned, sealed, banked", "".join(tree_html))
        knots = sec("The Binding", f"Knots tied {roman(d['knots_count'])} of {roman(n_knots)}", self.knots_html(d, rel))
        chap_rows = []
        titles = {str(ch["number"]): ch for ch in self.chapters}
        for r in sorted(self.chapters_csv, key=lambda r: int(r["chapter"])):
            ch = titles.get(r["chapter"])
            t = f'<a href="{rel}chronicle/{ch["slug"]}.html">{esc(ch["label"])} — {esc(ch["title"])}</a>' if ch else f"Chapter {esc(r['chapter'])}"
            chap_rows.append(f'<li><b>{t}</b><span class="m">{esc(TIER_DONE.get(r["tier"], r["tier"]))}</span></li>')
        chaps = sec("Chapters", "how each one ended", f'<ul class="chron">{"".join(chap_rows)}</ul>' if chap_rows else '<p class="empty">No chapter has closed yet.</p>')
        return plate + attrs + arts_sec + knots + chaps

    def knots_html(self, d, rel):
        tied = set(d.get("knots_tied") or [])
        knots = self.rules.get("knots") or []
        rows = []
        for k in knots:
            on = k["n"] in tied
            opens = f'<span class="m faint">opens Book {roman(k["opens"])}</span>' if on else ""
            rows.append(f'<li class="knot{" on" if on else ""}"><span class="rn">{roman(k["n"])}</span><div><b>{esc(k["name"])}</b>'
                        f'<span class="m">{esc(k["proves"])}</span>{opens}</div>'
                        f'{badge("tied", "good") if on else badge("untied", "dim")}</li>')
        soft = '<p class="hint">The soft season: do not trust the quiet.</p>' if d.get("soft_season") else ""
        return rope_knots(tied, knots) + f'<ul class="knots">{"".join(rows)}</ul>{soft}'

    def render_darrow(self):
        rel = "../"
        c = self.chars.get("darrow")
        d = self.darrow
        if not c:
            problem("saga/characters/darrow.json is missing")
            return
        body = self.identity_plate(c, rel, d["level"]) + self.character_sections(c, rel)
        body += '<div class="sec-gap" id="reckoning"></div>' + self.darrow_reckoning(rel)
        self.pages["darrow/index.html"] = shell("Ser Darrow of Edgemoor", body, rel, "Darrow", "char-page", desc="Darrow's page and his full Reckoning.")

    # ---------------------------------------------------------------- now
    def open_choice(self):
        """The newest choice block (any chapter, newest first) whose (chapter, scene key) has no recorded choice."""
        for ch in reversed(self.chapters):
            for s in reversed(ch["scenes"]):
                for b in reversed(s["blocks"]):
                    if b[0] == "ol" and b[2] and not self.choice_for(ch, s["key"]):
                        return {"chapter": ch, "scene": s, "items": b[1], "kind": b[2]}
        return None

    def latest_choice(self):
        """The newest recorded choice whose block the chronicle has (for the Now page when nothing is open)."""
        for ch in reversed(self.chapters):
            for s in reversed(ch["scenes"]):
                for b in reversed(s["blocks"]):
                    if b[0] == "ol" and b[2]:
                        rec = self.choice_for(ch, s["key"])
                        if rec:
                            return {"chapter": ch, "scene": s, "items": b[1], "kind": b[2], "rec": rec}
        return None

    def bearing_words(self):
        """Each axis as words: (left, right, word, position 0..1). Never a number on the page."""
        b = self.bearing
        if not b:
            return []
        rng = b.get("range", 10)
        lean_at, name_at = b.get("lean_at", 4), b.get("name_at", 8)
        rows = []
        for aid, ax in (b.get("axes") or {}).items():
            if not isinstance(ax, dict) or not all(k in ax for k in ("value", "left", "right")):
                continue
            v = ax["value"] if isinstance(ax["value"], int) else 0
            pole = ax["right"] if v > 0 else ax["left"]
            word = "even" if abs(v) < lean_at else (f"named {pole}" if abs(v) >= name_at else f"leans {pole}")
            rows.append((ax["left"], ax["right"], word, (v + rng) / (2.0 * rng)))
        return rows

    def bearing_html(self):
        rows = []
        for left, right, word, pos in self.bearing_words():
            rows.append(f'<li class="bearing-row"><span class="pole l">{esc(left)}</span>'
                        f'<span class="bearing-bar" role="img" aria-label="{esc(left)} to {esc(right)}: {esc(word)}"><i style="--p:{100.0 * pos:.1f}%"></i></span>'
                        f'<span class="pole r">{esc(right)}</span><span class="word{" on" if word != "even" else ""}">{esc(word)}</span></li>')
        ep = (self.bearing or {}).get("epithet")
        ep_html = f'<p class="hint">Named on the page: <span class="brass">{esc(ep)}</span>.</p>' if ep else '<p class="hint">No name has stuck to him yet.</p>'
        return f'<ul class="bearing">{"".join(rows)}</ul>{ep_html}'

    def bearing_chip(self):
        """One chip for the Now page's Reckoning card: the epithet if there is one, else the strongest lean, else 'even'."""
        if not self.bearing:
            return ""
        ep = self.bearing.get("epithet")
        if ep:
            return chip(f"Bearing · {ep}", "brass")
        leans = sorted(((abs(p - 0.5), w) for _, _, w, p in self.bearing_words() if w != "even"), reverse=True)
        return chip("Bearing · " + (leans[0][1] if leans else "even"))

    def render_now(self):
        rel = ""
        w, d = self.world, self.darrow
        cur_slug = w.get("chapter_file", "").split("/")[-1].replace(".md", "")
        ch = next((c for c in self.chapters if c["slug"] == cur_slug), None)
        latest = ch["scenes"][-1] if ch and ch["scenes"] else None
        place = self.place_by_id.get(self.current_place, {})
        loc = w.get("location") or {}
        where = place.get("name", "") + (f", {loc.get('detail')}" if isinstance(loc, dict) and loc.get("detail") else "")
        latest_html = (f'<a href="{rel}chronicle/{ch["slug"]}.html#{latest["anchor"]}">{esc((latest["label"] + " — " if latest["label"] else "") + latest["title"])}</a>' if latest else "—")
        book_line = f"Book {roman(w.get('book', 1))} — {w['book_title']}" if w.get("book_title") else ""
        plate = (f'<section class="plate now-plate"><p class="lbl">{esc(book_line)}</p>'
                 f'<h1>{esc("Chapter " + str(w.get("chapter")) + " — " + w.get("chapter_title", ""))}</h1>'
                 f'<dl class="kv"><dt>Latest scene</dt><dd>{latest_html}</dd><dt>Where</dt><dd>{esc(where)}</dd><dt>Season</dt><dd>{esc(w.get("season", ""))}</dd></dl>'
                 f'<p class="beat">{esc(w.get("last_beat", ""))}</p></section>')
        map_html = sec("The map", "where Darrow is", svg_map(self.places, self.route, self.current_place, rel)
                       + '<p class="legend"><span class="lg ember">●</span> Darrow <span class="lg brass">●</span> visited <span class="lg faint">●</span> not yet <span class="lg route">—</span> the road so far</p>')
        q = w.get("current_quest") or {}
        quest = sec("The quest", esc(q.get("name", "")), f'<p class="prose">{esc(q.get("on_the_page", ""))}</p><h3 class="sub-h">What he is fighting</h3><p class="prose">{esc(w.get("current_struggle", ""))}</p>')
        oc = self.open_choice()
        if oc:
            lis = "".join(f"<li>{inline(it)}</li>" for it in oc["items"])
            choice = sec(self.choice_title(oc["kind"], None, oc["scene"]["key"]), "waiting on Darrow",
                         f'<ol class="choice">{lis}</ol><p class="dim">From <a href="{rel}chronicle/{oc["chapter"]["slug"]}.html#{oc["scene"]["anchor"]}">{esc(oc["chapter"]["label"] + " — " + oc["scene"]["title"])}</a>.</p>')
        else:
            lc = self.latest_choice()
            if lc:
                rec = lc["rec"]
                taken = as_int(rec.get("option"))
                by_self = rec.get("by") == "bearing"
                mark = ' <span class="state good">chosen</span>' + (' <span class="state dim">answered for himself</span>' if by_self else "")
                lis = "".join(f'<li{" class=\"taken\"" if taken == i else ""}>{inline(it)}{mark if taken == i else ""}</li>'
                              for i, it in enumerate(lc["items"], 1))
                free = f'<p class="chosen-free">{mark.strip()} {esc(rec.get("text") or "")}</p>' if taken is None and (rec.get("text") or "").strip() else ""
                choice = sec(self.choice_title(lc["kind"], rec, lc["scene"]["key"]), "answered",
                             f'<ol class="choice">{lis}</ol>{free}<p class="dim">From <a href="{rel}chronicle/{lc["chapter"]["slug"]}.html#{lc["scene"]["anchor"]}">{esc(lc["chapter"]["label"] + " — " + lc["scene"]["title"])}</a>.</p>')
            else:
                choice = sec("The choice", "", '<p class="empty">No choice waits on Darrow yet.</p>')
        comps = []
        for key, comp in (w.get("companions") or {}).items():
            if not isinstance(comp, dict) or comp.get("present") is False:
                continue
            cid = next((c for c in self.chars if c.split("-")[0] == key), None)
            if not cid:
                continue
            c = self.chars[cid]
            sg = c.get("sigil") or {}
            mood = approval_word(int(comp["approval"])) if "approval" in comp else "at his side"
            comps.append(f'<a class="comp" href="{rel}{self.char_href(cid)}">{sigil(self.factions.get(sg.get("faction"), {}), sg.get("mark"), 48)}'
                         f'<div><b>{esc(c["name"])}</b><span class="lbl">{esc(mood)}</span><span class="m">{esc(c.get("now", ""))}</span></div></a>')
        companions = sec("With him", f"{len(comps)}", f'<div class="comps">{"".join(comps)}</div>' if comps else '<p class="empty">No one yet.</p>')
        a = d["attributes"]
        rk = "".join(f'<div class="mini-attr"><span class="lbl">{k.capitalize()}</span><span class="v num">{a[k]["score"]}</span><span class="fell num">{a[k]["fell"]}</span></div>'
                     for k in ("might", "vigor", "finesse", "resolve"))
        bchip = self.bearing_chip()
        card = (f'<div class="rk-mini"><div class="hero">{crest(d["level"])}<div class="who"><h3>{esc(d["name"])}</h3><p class="sub">Level {d["level"]} · {esc(d["rank"])} · HP {d["hp_max"]}</p>'
                f'<div class="insp"><span class="lbl">Inspiration</span>{pips(d["inspiration"], d["inspiration_cap"])}</div>'
                + (f'<div class="chips">{bchip}</div>' if bchip else "") + '</div></div>'
                f'<div class="mini-attrs">{rk}</div><p class="lbl">the faint numbers are the ones he read behind his own</p>'
                f'{bar(d["ember"]["value"] or 0, 100, "Ember · " + str(d["ember"]["tier"] or "unlit"), "ember", d["ember"]["value"])}'
                f'<p><a href="{rel}darrow/index.html#reckoning">The full Reckoning</a></p></div>')
        reck = sec("The Reckoning", "Darrow", card)
        knots = sec("The Binding", f"Knots tied {roman(d['knots_count'])} of {roman(len(self.rules.get('knots') or []) or 7)}", self.knots_html(d, rel))
        tier = (d.get("chapter_now") or {}).get("tier_so_far")
        going = sec("The chapter so far", "", f'<p class="prose">{esc(TIER_WORDS.get(tier, "Not yet begun."))}</p>')
        rolls = sorted(self.rolls, key=lambda r: r.get("when", ""), reverse=True)[:12]
        if rolls:
            rows = []
            for r in rolls:
                d20 = r.get("d20", "") + (f"/{r['d20_b']}" if r.get("d20_b") else "")
                res = r.get("result", "")
                cls = "good" if "SUCCESS" in res else ("warn" if "PARTIAL" in res else "bad")
                rows.append(f'<li class="roll"><span class="dice-tag">{esc(r.get("stat", "").upper() or "FLAT")} · DC {esc(r.get("dc"))}</span>'
                            f'<span class="dice-body num">d20 <b>{esc(d20)}</b> {esc(r.get("mods", ""))} = <b>{esc(r.get("total"))}</b></span>'
                            f'{badge(res.title(), cls)}<span class="m">{esc(r.get("label", ""))}</span></li>')
            dice = sec("The dice", "latest rolls", f'<ul class="rolls">{"".join(rows)}</ul>')
        else:
            dice = sec("The dice", "", '<p class="empty">No dice have been cast yet.</p>')
        body = plate + map_html + quest + choice + companions + reck + knots + going + dice
        self.pages["index.html"] = shell("Now", body, rel, "Now", "now-page", desc="What is going on now in The Unkneeling.")

    # ---------------------------------------------------------------- codex
    def render_codex(self):
        rel = "../"
        secs = []

        def rows(items):
            return '<ol class="archive">' + "".join(
                f'<li><details><summary><span><span class="rn">{roman(i)}</span>{esc(it["name"])}</span>{it.get("tag", "")}</summary><div class="dt-body">{it["html"]}</div></details></li>'
                for i, it in enumerate(items, 1)) + "</ol>"

        places = []
        for p in self.places:
            if not p.get("on_page"):
                continue
            fs = p.get("first_seen") or {}
            src = self.scene_ref(fs, rel) if fs else ""
            tag = badge("visited", "good") if p.get("visited") else badge("not yet", "dim")
            name = p["name"] + (f" · {p['subtitle']}" if p.get("subtitle") else "")
            places.append({"name": name, "tag": tag, "html": f'<p>{esc(p["description"])}</p><p class="m">First on the page: {src}</p>'})
        offmap = [p["name"] for p in self.places if not p.get("on_page")]
        extra = f'<p class="dim">On the map but not yet in the story: {esc(", ".join(offmap))}.</p>' if offmap else ""
        secs.append(sec("Places", f"{len(places)}", rows(places) + extra))
        facs = []
        for f in self.factions.values():
            if not f.get("on_page"):
                continue
            facs.append({"name": f["name"], "tag": "", "html": f'<div class="fac">{sigil(f, None, 44)}<p>{esc(f["description"])}</p></div>'})
        secs.append(sec("Factions", f"{len(facs)}", rows(facs)))
        sayings = [{"name": s["name"].strip('"“”'), "tag": "", "html": f"<p>{inline(s['text'])}</p>"} for s in self.codex.get("Sayings", [])]
        secs.append(sec("Sayings", f"{len(sayings)}", rows(sayings)))
        place_names = {p["name"].lower() for p in self.places}
        char_names = {c["name"].lower() for c in self.chars.values()} | {a.lower() for c in self.chars.values() for a in c.get("aliases") or []}
        things, beasts, extra_secs = [], [], []
        for key, entries in self.codex.items():
            if key == "Sayings":
                continue
            bucket = things if key in ("Places and things", "Things") else beasts if key in ("People", "Beasts") else None
            if bucket is None:
                extra_secs.append((key, [{"name": e["name"], "tag": "", "html": f"<p>{inline(e['text'])}</p>"} for e in entries]))
                continue
            for e in entries:
                nm = e["name"].lower()
                if nm in place_names or nm in char_names or nm.replace("the ", "") in char_names:
                    continue
                bucket.append({"name": e["name"], "tag": "", "html": f"<p>{inline(e['text'])}</p>"})
        secs.append(sec("Things", f"{len(things)}", rows(things) if things else '<p class="empty">Nothing yet.</p>'))
        if beasts:
            secs.append(sec("Beasts and others", f"{len(beasts)}", rows(beasts)))
        for key, items in extra_secs:
            if items:
                secs.append(sec(key, f"{len(items)}", rows(items)))
        body = '<section class="plate"><p class="lbl">The Codex</p><h1>Places, factions, sayings</h1><p class="dim">Only what the page has shown. Names on the map that the story has not reached yet are names and nothing more.</p></section>' + "".join(secs)
        self.pages["codex/index.html"] = shell("Codex", body, rel, "Codex", desc="Places, factions and sayings of The Unkneeling.")

    # ---------------------------------------------------------------- run
    def build(self):
        for i in range(len(self.chapters)):
            self.render_chapter(i)
        self.render_chronicle_index()
        for c in self.chars.values():
            if c["id"] != "darrow":
                self.render_character(c)
        self.render_roster()
        self.render_darrow()
        self.render_now()
        self.render_codex()
        self.pages["site.css"] = CSS
        self.pages["site.js"] = JS
        self.pages[".nojekyll"] = ""


# ============================================================ checks
FORBIDDEN = [r"kcal", r"calori\w*", r"protein\w*", r"creatin\w*", r"macros?", r"rehab\w*", r"physio\w*", r"therap\w*",
             r"surgery", r"surgical", r"graft\w*", r"ligament\w*", r"reps?", r"squat\w*", r"bik(?:e|es|ing)", r"bicycl\w*",
             r"weigh-ins?", r"dynamometer", r"exercis\w*", r"workout\w*", r"dumbbells?", r"barbells?", r"kettlebells?",
             r"treadmill", r"gym", r"supplements?", r"step-downs?", r"post-op"]
FORBIDDEN_CS = ["ACL", "PT", "RPE"]
UI_WORDS = """Faction Factions Status Roster Previously Appearance Quote Relationships Known Facts Appearances Timeline Places Sayings Things
Attributes Chapters Legend Season Latest Where Skip Content Level Inspiration Proficiency Regard Toward Borrowed Unread Deeper Start Reading
Characters Codex Chronicle Now Darrow Unkneeling Books Chapter Scene Scenes Climax Choice Previous Next Back Map Quest Fighting
Visited Arts Learned Sealed Banked Tied Untied Opens Book Knots Binding Reckoning Dice Latest Rolls Cast Page Site Memorial Fallen Alive
Hollowed Missing Unknown Major Minor Earned Grace Ember Unlit Fire Might Vigor Finesse Resolve Rank Ranks Temper Days Days Keeper Prior
Runner Senior Mender Menders Captain Knight Youngest Warrior Clan Clans Keeper Spoiler Spoilers
Bearing Leans Named Even Epithet Small Answered Himself Interlude Waiting""".split()
STOP = set("""Seventh Present Former Scale Mid Magic Violence Tone Praise Speaks Talks Grounded Grants Grew Fights Families Companies Customs Geography Naming Peoples Recurring Reigning Surpassing Unwind Shatter Hinted Bible Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec Wits Voices Signature Somber Stiff Steam Kennel Cripples Wager Magic
About After Again Against Already Always Among Anyone Anything Around Because Before Behind Below Between Beyond
Book Books Both Chapter Chapters Choice Choices Claude Core Could Darrow Does Each Early Either Ember End Every Everyone Expandable Expandables
First Four Five From Full Game Give Given Hard Have Here High His How If In Into Its Just Keep Knot Knots Late Later Less Level List Log Lower
Made Make Many More Most Much Must Never Next Nine No None Not Nothing Now Once One Only Open Other Our Over Part Phase Phases Plant Planting Plants
Question Real Reveal Rough Rule Rules Same Scene Second Seven Since Six Some Someone Something State Still Story Such Than That The Their Then There These They
This Those Three Through Time Transition Truth Truths Two Under Until Upper Use Used Uses Very What When Where Which While Who Why Will With Within
Without Would Your Yes Final Image Trigger Record Week Weeks Gate Gates Window Earliest Reader Readers Spoilers Darrow's Darrows Companion Companions Antagonist
Antagonists Voice Wants Fears Hides Carries Flaw Arc Rank Ranks Might Vigor Finesse Resolve Insight Blade Breath Footing Binding Sport Arts Art
Might's Dice Checks Check Approval Inspiration Eye Tier Tiers Climax Expandables Mother Sister Brother Ser Dame Knight Confessor Confessors Crown Menders
Mender Hound Runner Captain Captains Old Young Prior Lance Lances Boss Interlude Scenes Pages Page Table Entry Entries Format Formats Files File Notes Note
Secrets Secret Identity Identities Reckoning Reckonings Grace Oath Oaths Bound Kindled Tempered Unbowed Emberknight Warden Wardens Oathsworn Oathstone
Oathstones Stone Stones Field Road Lightning Turning Standing Walking Straightening Steps Step Harrow Ford River Peaks House Hall Gate Tower Bell Bells
Hollowed Faithless Vaelish Codex Chronicle Ledger Engine Script Clan Clans Lowmarch Thornwild Calden Coldmere Holloway Fields
Greywater Edgemoor Thousand Saint Ysolde's Ysolde Wend Patience Stillwater Stance Groundbreaker Hammerfall Grip Iron Seated Long Soft Landing Thunderstep
Hawk's Stoop Anchor Quickening Mender's Warden's Knight's Reading North South East West Dawn Dusk Winter Summer Autumn Spring Midsummer Midwinter
Yes No Maybe Also Thus Whatever Whoever Whenever Wherever Please Thank Thanks Hello Dear Sincerely Best Regards Ever Even Almost Enough Rather Quite
Set Sets Takes Take Took Gets Get Got Goes Go Went Comes Come Came Sees See Saw Says Say Said Knows Know Knew Thinks Think Thought Wants Want Wanted
Needs Need Needed Keeps Kept Holds Hold Held Reads Read Writes Write Wrote Uses Loses Lose Lost Wins Win Won Finds Find Found Tells Tell Told Puts Put
Approved Approves Favors Favor Refuses Refuse Requires Require Required Earned Earns Earn Tied Ties Tie Written Done Doing Using Making Being Having
Nobody Somebody Everybody Anybody Itself Himself Herself Themselves Myself Yourself Ourselves""".split())


def norm(s):
    s = html.unescape(s)
    s = re.sub(r"[*_`#>\[\]()|]", " ", s)
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s.strip(" .,;:!?\"'“”‘’—–-")


def text_of(h):
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", h, flags=re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


GM_DIRS = [SAGA / "bible" / "_gm", SAGA / "state" / "_gm"]


def gm_blocklists(chron_text, allowed_words, extra_gm="", allowed_text=""):
    """Sentences and unrevealed names from the GM files. Nothing from here is rendered; it only builds the checks.
    GM files: every .md under saga/bible/_gm/ and saga/state/_gm/ (JSON there is not scanned: every name it carries is
    also in a GM .md). A GM sentence is exempt when the chronicle or allowed_text (engine/rules.json strings and the
    Bearing's pole words / current epithet) already carries it."""
    gm_text = "\n".join(p.read_text(encoding="utf-8") for d in GM_DIRS if d.exists() for p in sorted(d.glob("*.md")))
    chron_norm = norm(chron_text)
    allowed_norm = norm(allowed_text)
    sentences = set()
    for chunk in re.split(r"[\n|]", gm_text + "\n" + extra_gm):
        for s in re.split(r"(?<=[.!?;:])\s+", chunk):
            s2 = norm(s)
            if len(s2) >= 28 and s2 not in chron_norm and s2 not in allowed_norm:
                sentences.add(s2)
    # names: capitalised words in GM-side files that the page has never spoken
    chron_words = {w.lower() for w in re.findall(r"[A-Za-z]+", chron_text)}
    allowed = {w.lower() for w in allowed_words} | {w.lower() for w in UI_WORDS}
    src = gm_text
    lower_words = set(re.findall(r"\b[a-z]{3,}\b", src))
    names = set()
    for w in re.findall(r"\b[A-Z][a-z]{2,}\b", src):
        if w in STOP or w.lower() in chron_words or w.lower() in allowed or w.lower() in lower_words:
            continue
        names.add(w)
    return sentences, names


def run_checks(site, out_dir):
    pages = {k: v for k, v in site.pages.items() if k.endswith(".html")}
    all_text = {k: text_of(v) for k, v in pages.items()}
    # 1. real-world terms, whole words, in every generated file (pages, css, js)
    pat = re.compile(r"\b(" + "|".join(FORBIDDEN) + r")\b", re.I)
    pat_cs = re.compile(r"\b(" + "|".join(FORBIDDEN_CS) + r")\b")
    for k, v in site.pages.items():
        for m in pat.finditer(v):
            problem(f"{k}: real-world term '{m.group(1)}' at …{v[max(0, m.start() - 40):m.end() + 40]!r}")
        for m in pat_cs.finditer(v):
            problem(f"{k}: real-world term '{m.group(1)}' at …{v[max(0, m.start() - 40):m.end() + 40]!r}")
    # 2. GM sentences and unrevealed names
    chron_text = "\n".join(read(p) for p in sorted(CHRON.glob("*.md")))
    allowed = set()
    all_arts = site.rules.get("arts", []) + site.rules.get("sport_arts", {}).get("arts", [])  # sport Arts are game rules too
    for a in all_arts:
        allowed.update(re.findall(r"[A-Za-z']+", a["name"] + " " + a["tree"]))
    for k in site.rules.get("knots", []):
        allowed.update(re.findall(r"[A-Za-z']+", k["name"]))
    for r in site.rules["levels"]["ranks"]:
        allowed.update(r["name"].split())
    for t in site.rules["ember"]["tiers"]:
        allowed.add(t["name"])
    for p in site.places:
        allowed.update(re.findall(r"[A-Za-z']+", p["name"] + " " + p.get("subtitle", "")))
    for f in site.factions.values():
        allowed.update(re.findall(r"[A-Za-z']+", f["name"]))
    allowed.update(["Unkneeling", "Previously", "Codex", "Chronicle", "Now", "Characters", "Appearance", "Relationships", "Known", "Appearances", "Timeline", "Roster"])
    # the sentence exemption: what the chronicle, the game's own rules, or the Bearing's rendered words already say is not a GM secret
    allowed_text = []
    for k in site.rules.get("knots", []):
        allowed_text += [str(k.get("name", "")), str(k.get("proves", ""))]
    for a in all_arts:
        allowed_text += [str(a.get("name", "")), str(a.get("effect", ""))]
    for r in site.rules["levels"]["ranks"]:
        allowed_text.append(str(r.get("name", "")))
    for t in site.rules["ember"]["tiers"]:
        allowed_text += [str(t.get("name", "")), str(t.get("effect", ""))]
    if site.bearing:
        # only what the Bearing renders: the section's own label, the pole words always, the current epithet
        # (load_bearing has already required it to be on the page). The names table is never allow-listed:
        # a future name stays blocked until the chronicle speaks it.
        allowed_text.append(BEARING_LABEL)
        for ax in (site.bearing.get("axes") or {}).values():
            if isinstance(ax, dict):
                poles = f"{ax.get('left', '')} {ax.get('right', '')}"
                allowed.update(re.findall(r"[A-Za-z']+", poles))
                allowed_text.append(poles)
        ep = site.bearing.get("epithet")
        if isinstance(ep, str) and ep:
            allowed.update(re.findall(r"[A-Za-z']+", ep))
            allowed_text.append(ep)
    # GM text that may still sit in world.json (the checks above already report the keys); blocked from the site all the same
    extra_gm = json.dumps(site.world.get("chapter_plan") or {}) + "\n" + str((site.world.get("current_quest") or {}).get("summary", ""))
    sentences, names = gm_blocklists(chron_text, allowed, extra_gm, "\n".join(allowed_text))
    note(f"GM blocklist: {len(sentences)} sentences, {len(names)} unrevealed names (not printed)")
    name_re = re.compile(r"\b(" + "|".join(re.escape(n) for n in sorted(names, key=len, reverse=True)) + r")\b") if names else None
    for k, txt in all_text.items():
        t_norm = norm(txt)
        for s in sentences:
            if s in t_norm:
                import hashlib
                problem(f"{k}: contains a sentence from the GM files (length {len(s)}, sha1 {hashlib.sha1(s.encode()).hexdigest()[:10]}); search the GM files for it")
        if name_re:
            for m in name_re.finditer(txt):
                problem(f"{k}: unrevealed name '{m.group(1)}' at …{txt[max(0, m.start() - 50):m.end() + 50]!r}")
    # engine keys rendered on the Now page (roll labels and notes) are lowercase slugs: check them case-insensitively
    if names:
        low_re = re.compile(r"(" + "|".join(re.escape(n.lower()) for n in sorted(names, key=len, reverse=True)) + r")")
        for r in site.rolls:
            blob = (r.get("label", "") + " " + r.get("note", "")).lower()
            for m in low_re.finditer(blob):
                problem(f"rolls.csv: label/note '{r.get('label')}' names '{m.group(1)}', which the page has not spoken")
    # 3. internal links and anchors
    ids = {}
    for k, v in pages.items():
        ids[k] = set(re.findall(r'\sid="([^"]+)"', v))
    for k, v in pages.items():
        base = Path(k).parent
        for m in re.finditer(r'(?:href|src)="([^"#]*)(#[^"]*)?"', v):
            href, frag = m.group(1), m.group(2)
            if href.startswith(("http:", "https:", "mailto:")):
                continue
            if href == "":
                target = k
            else:
                target = str((base / href).as_posix())
                target = re.sub(r"^(\./)+", "", target)
                parts = []
                for seg in target.split("/"):
                    if seg == "..":
                        if not parts:
                            problem(f"{k}: link '{href}' escapes the site")
                            break
                        parts.pop()
                    elif seg and seg != ".":
                        parts.append(seg)
                target = "/".join(parts)
            if target not in site.pages:
                problem(f"{k}: broken link '{href}' (no such file {target})")
                continue
            if frag and frag != "#" and target in ids and frag[1:] not in ids[target]:
                problem(f"{k}: broken anchor '{href}{frag}'")


# ============================================================ assets
CSS = r"""/* THE UNKNEELING — one stylesheet. Dark only, by choice: a forge at night. */
:root{
  --night:#0F1217; --plate:#161B22; --plate-hi:#1C222B; --rule:#2B323D; --raw:#262D37; --leather:#4A3826;
  --ink:#E8E2D4; --dim:#9AA2AE; --faint:#7D8692; --faint-stroke:#646D79; --t4-text:#A77FB5;
  --brass:#CFA65F; --brass-dim:#8A7044; --ember:#E2713B; --good:#72B396; --warn:#D9A441; --bad:#D0634D;
  --t1:#EADBA6; --t2:#D9AE5F; --t3:#A86B3C; --t4:#7A4D86; --t5:#4062A3; --t6:#8BB2D3;
  --display:"Grenze Gotisch","UnifrakturMaguntia",Georgia,serif;
  --body:"Alegreya Sans","Gill Sans","Segoe UI",system-ui,sans-serif;
  --label:"Alegreya Sans SC","Alegreya Sans","Segoe UI",system-ui,sans-serif;
  --mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace;
  color-scheme:dark;
}
*,*::before,*::after{box-sizing:border-box}
html{background:var(--night);scroll-behavior:smooth}
body{margin:0;background:var(--night);color:var(--ink);font-family:var(--body);font-size:16px;line-height:1.45;-webkit-font-smoothing:antialiased;overflow-x:hidden}
img,svg{max-width:100%}
.wrap{max-width:640px;margin:0 auto;padding-inline:16px}
main.wrap{padding-block:20px 56px;display:grid;gap:30px}
h1,h2,h3,h4{margin:0;text-wrap:balance;overflow-wrap:anywhere}
p{margin:0}
a{color:var(--brass);text-decoration:none}
a:hover{text-decoration:underline;text-underline-offset:2px}
.num{font-variant-numeric:tabular-nums lining-nums}
.lbl{font-family:var(--label);font-size:.8rem;letter-spacing:.08em;color:var(--dim)}
.dim{color:var(--dim)} .faint{color:var(--faint)} .brass{color:var(--brass)}
.hint{font-size:.85rem;color:var(--faint);font-style:italic}
.empty{color:var(--faint);font-size:.95rem;font-style:italic}
.prose{max-width:62ch;line-height:1.55}
:focus-visible{outline:2px solid var(--brass);outline-offset:2px}
.skip{position:absolute;left:-999px;top:8px;background:var(--brass);color:var(--night);padding:6px 10px;border-radius:4px;z-index:10}
.skip:focus{left:8px}

/* masthead and navigation */
.mast{border-bottom:1px solid var(--rule);background:var(--night);position:sticky;top:0;z-index:5}
.mast-in{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;padding-block:10px}
.brand{font-family:var(--display);font-weight:700;font-size:1.5rem;letter-spacing:.01em;color:var(--brass)}
.brand:hover{text-decoration:none}
.nav{display:flex;gap:4px 14px;flex-wrap:wrap}
.nav a{font-family:var(--label);font-size:.85rem;letter-spacing:.08em;color:var(--dim);padding:4px 0;border-bottom:2px solid transparent}
.nav a[aria-current=page]{color:var(--brass);border-bottom-color:var(--brass)}
.progress{position:fixed;left:0;top:0;height:3px;width:100%;z-index:6;pointer-events:none}
.progress>i{display:block;height:100%;width:0;background:linear-gradient(90deg,var(--brass-dim),var(--ember))}
.foot{font-size:.82rem;color:var(--faint);border-top:1px solid var(--rule);padding-block:14px 24px}
.foot .wrap{display:grid;gap:4px}

/* plates: only each page's identity / now block */
.plate{
  border:1px solid var(--rule);border-radius:6px;padding:18px 16px 16px;display:grid;gap:12px;
  background:
    radial-gradient(circle at 9px 9px,var(--brass-dim) 0 1.6px,transparent 2.2px),
    radial-gradient(circle at calc(100% - 9px) 9px,var(--brass-dim) 0 1.6px,transparent 2.2px),
    radial-gradient(circle at 9px calc(100% - 9px),var(--brass-dim) 0 1.6px,transparent 2.2px),
    radial-gradient(circle at calc(100% - 9px) calc(100% - 9px),var(--brass-dim) 0 1.6px,transparent 2.2px),
    linear-gradient(180deg,var(--plate-hi),var(--plate));
}
.plate h1{font-family:var(--display);font-weight:700;font-size:1.8rem;line-height:1.1}
.plate h2{font-family:var(--display);font-weight:700;font-size:1.6rem;line-height:1.1}
.kv{display:grid;grid-template-columns:auto minmax(0,1fr);gap:4px 14px;margin:0;font-size:.95rem}
.kv dt{font-family:var(--label);font-size:.8rem;letter-spacing:.08em;color:var(--dim)}
.kv dd{margin:0}
.beat{font-style:italic;color:var(--dim);border-left:2px solid var(--brass-dim);padding-left:10px}
.btn{display:inline-block;font-family:var(--label);font-weight:700;letter-spacing:.06em;border:1px solid var(--brass);border-radius:4px;padding:8px 14px;color:var(--night);background:var(--brass)}
.btn:hover{text-decoration:none;filter:brightness(1.08)}

/* section heads */
.sec{display:grid;gap:14px}
.sec-h{display:flex;align-items:baseline;gap:12px;border-bottom:1px solid var(--rule);padding-bottom:6px}
.sec-h h2{font-family:var(--display);font-weight:700;font-size:1.45rem;color:var(--ink)}
.sec-h .lbl{margin-left:auto;text-align:right}
.sub-h{font-family:var(--label);font-weight:700;font-size:.85rem;letter-spacing:.08em;color:var(--dim);margin-top:8px}
.sec-gap{height:4px}

/* hero / identity */
.hero{display:grid;grid-template-columns:86px minmax(0,1fr);gap:16px;align-items:center}
.who{display:grid;gap:6px;min-width:0}
.who h1,.who h2,.who h3{font-family:var(--display);font-weight:700;font-size:1.7rem;line-height:1.1;color:var(--ink)}
.who .sub{color:var(--dim);font-size:.95rem}
.sigil-row{display:flex;align-items:center;gap:10px;font-size:.9rem;border-top:1px dotted var(--rule);padding-top:10px}
.crest{width:86px;height:auto;display:block}
.cr-shield{fill:var(--plate);stroke:var(--brass);stroke-width:2}
.cr-inner{fill:none;stroke:var(--brass-dim);stroke-width:1}
.crest .lv{font-family:var(--display);font-weight:700;fill:var(--ink)}
.crest .lvl{font-family:var(--label);fill:var(--dim);letter-spacing:.12em}
.crest.unread .cr-shield{stroke:var(--t4)} .crest.unread .lv{fill:var(--t4-text)}
.crest.borrowed .cr-shield{stroke:var(--t5)} .crest.borrowed .lv{fill:var(--t6)}

/* sigils (original heraldry, line style) */
.sigil{display:block;flex:none}
.sg-shield{fill:var(--plate);stroke:var(--brass);stroke-width:2.5}
.sg-inner{fill:none;stroke:var(--brass-dim);stroke-width:1}
.sg-l{fill:none;stroke:var(--brass);stroke-width:3;stroke-linecap:round;stroke-linejoin:round}
.sg-s{fill:none;stroke:var(--brass-dim);stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.sg-f{fill:var(--brass)}
.sg-red{fill:var(--bad);stroke:var(--bad);stroke-width:1.5;stroke-linejoin:round}
.sg-num{font-family:var(--display);font-weight:700;font-size:26px;fill:var(--ink)}

/* chips, badges, bars, pips */
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{font-family:var(--label);font-size:.78rem;letter-spacing:.06em;border:1px solid var(--rule);border-radius:999px;padding:2px 9px;color:var(--dim);background:transparent;line-height:1.4}
.chip.brass{border-color:var(--brass-dim);color:var(--brass)}
.chip.blue{border-color:var(--t5);color:var(--t6)}
.chip.ember{border-color:var(--ember);color:var(--ember)}
a.chip:hover{text-decoration:none;border-color:var(--brass)}
button.chip{cursor:pointer;font:inherit;font-family:var(--label);font-size:.78rem}
button.chip[aria-pressed=true]{background:var(--brass);color:var(--night);border-color:var(--brass)}
.state{display:inline-block;font-family:var(--label);font-size:.78rem;letter-spacing:.08em;padding:1px 8px;border-radius:3px;border:1px solid currentColor;line-height:1.4}
.state.good{color:var(--good)} .state.warn{color:var(--warn)} .state.bad{color:var(--bad)} .state.dim{color:var(--dim)} .state.sealed{color:var(--t4-text)}
.bar-row{display:grid;gap:5px}
.bar-l{display:flex;justify-content:space-between;gap:8px;font-size:.9rem}
.bar{height:10px;background:var(--raw);border-radius:2px;position:relative;overflow:hidden}
.bar>i{position:absolute;inset:0 auto 0 0;width:var(--w);background:linear-gradient(90deg,var(--brass-dim),var(--brass));transition:width .9s cubic-bezier(.2,.7,.2,1)}
.bar.ember>i{background:linear-gradient(90deg,#8E3B26,var(--ember))}
.bar.approval>i{background:linear-gradient(90deg,var(--t3),var(--t2))}
.bar.temper>i{background:linear-gradient(90deg,var(--t3),var(--t1))}
.pips{display:inline-flex;gap:4px;align-items:center;vertical-align:middle}
.pip{width:10px;height:10px;transform:rotate(45deg);border:1px solid var(--brass-dim);background:transparent}
.pip.on{background:var(--brass);border-color:var(--brass)}
.pips.rank .pip{width:8px;height:8px}
.insp{display:flex;gap:10px;align-items:center}
.row2{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:16px;align-items:end}
@media (max-width:440px){.row2{grid-template-columns:minmax(0,1fr)}}

/* details */
details{border-top:1px solid var(--rule);padding-top:8px}
summary{cursor:pointer;font-family:var(--label);letter-spacing:.06em;color:var(--dim);font-size:.9rem;list-style:none;display:flex;justify-content:space-between;gap:8px}
summary::-webkit-details-marker{display:none}
summary::after{content:"+";color:var(--brass);flex:none}
details[open]>summary::after{content:"\2212"}
.dt-body{padding-top:8px}
.sec-h+details{border-top:0;padding-top:0}
.chosen-free{font-size:17px;max-width:65ch}

/* timeline */
.chron{list-style:none;margin:0;padding:0;display:grid;gap:10px}
.chron li{display:grid;gap:2px;border-left:2px solid var(--rule);padding-left:12px}
.chron li.now{border-left-color:var(--brass)}
.chron li.book{border-left-color:transparent;padding-left:0}
.chron li.named{border-left-style:dotted}
.chron li.book b{font-family:var(--label);letter-spacing:.1em;color:var(--brass);font-weight:700}
.chron b{font-weight:700}
.chron .m{font-size:.86rem;color:var(--dim)}
.chron a{color:var(--ink)} .chron a b{color:var(--ink)}
.chron li>a{display:grid;gap:2px}
.chron li.now a b{color:var(--brass)}
.chron .scenes{list-style:none;margin:6px 0 0;padding:0;display:grid;gap:4px;font-size:.92rem}
.chron .scenes a{color:var(--dim)}

/* archive rows */
.archive{list-style:none;margin:0;padding:0;display:grid;gap:0}
.archive li{border-bottom:1px solid var(--rule)}
.archive details{border:0;padding:9px 0}
.archive summary{color:var(--ink);font-family:var(--body);font-size:.98rem;letter-spacing:0;align-items:center;justify-content:flex-start}
.archive summary>span:first-child{flex:1 1 auto;min-width:0}
.archive summary .state{margin-right:4px}
.archive summary .rn{font-family:var(--display);color:var(--brass);width:2.2em;display:inline-block;font-size:1.3rem;line-height:1}
.archive .dt-body{color:var(--dim);max-width:62ch;display:grid;gap:6px}
.archive .dt-body p{line-height:1.5}
.archive .m{font-size:.86rem;color:var(--faint)}
.fac{display:grid;grid-template-columns:auto minmax(0,1fr);gap:12px;align-items:start}

/* sealed */
.sealed-line{color:var(--t4-text);font-family:var(--label);letter-spacing:.06em}
.sealed-box{border-color:var(--t4)}

/* streak-style attribute tiles */
.streaks{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}
.stk{display:grid;gap:4px;border-top:2px solid var(--rule);padding-top:8px;min-width:0}
.stk .v{font-family:var(--display);font-weight:700;font-size:2rem;line-height:1;color:var(--ink)}
.stk .v small{font-size:.9rem;color:var(--dim);margin-left:3px;font-family:var(--body)}
.stk .n{font-family:var(--label);font-size:.85rem;letter-spacing:.06em;color:var(--ink)}
.stk .s{font-size:.76rem;color:var(--dim);line-height:1.3}
.stk .s.faint{color:var(--faint)}
.stk.hot{border-top-color:var(--ember)}
.stk .bar-row{margin-top:2px} .stk .bar-l{display:none} .stk .bar{height:6px}

/* bearing: four axes in words, a marker on a line */
.bearing{list-style:none;margin:0;padding:0;display:grid;gap:10px}
.bearing-row{display:grid;grid-template-columns:5.5em minmax(0,1fr) 5.5em;grid-template-areas:"l bar r" "w w w";gap:2px 10px;align-items:center}
.bearing-row .pole{font-family:var(--label);font-size:.85rem;letter-spacing:.06em;color:var(--dim)}
.bearing-row .pole.l{grid-area:l;text-align:right} .bearing-row .pole.r{grid-area:r}
.bearing-bar{grid-area:bar;position:relative;height:10px;display:block}
.bearing-bar::before{content:"";position:absolute;left:0;right:0;top:50%;border-top:1px solid var(--rule);transform:translateY(-50%)}
.bearing-bar::after{content:"";position:absolute;left:50%;top:1px;bottom:1px;border-left:1px dotted var(--faint-stroke)}
.bearing-bar>i{position:absolute;top:50%;left:var(--p);width:10px;height:10px;margin:-5px 0 0 -5px;border-radius:50%;background:var(--brass);box-shadow:0 0 0 2px var(--night);transition:left .9s cubic-bezier(.2,.7,.2,1)}
.bearing-row .word{grid-area:w;text-align:center;font-size:.82rem;color:var(--faint);font-style:italic}
.bearing-row .word.on{color:var(--brass);font-style:normal}
@media (max-width:440px){.streaks{grid-template-columns:repeat(2,minmax(0,1fr))}}

/* arts */
.tree{display:grid;gap:8px;margin-bottom:14px}
.tree h3{font-family:var(--label);font-weight:700;font-size:.85rem;letter-spacing:.1em;color:var(--dim)}
.arts{list-style:none;margin:0;padding:0;display:grid;gap:8px}
.art{display:grid;gap:3px;border-left:2px solid var(--rule);padding-left:12px}
.art.on{border-left-color:var(--brass)}
.art.sealed{border-left-color:var(--t4)}
.art-top{display:flex;justify-content:space-between;gap:8px;align-items:center}
.art .m{font-size:.86rem;color:var(--dim)}
.art .e{font-size:.86rem;color:var(--faint);font-style:italic}
.art.sealed .pip.on{background:var(--t4);border-color:var(--t4)}

/* knots */
.rope{width:100%;height:auto;display:block}
.rp-line{stroke:var(--leather);stroke-width:4;fill:none}
.rp-k{fill:var(--raw);stroke:var(--rule);stroke-width:2}
.rp-knot.on .rp-k{fill:url(#temper);stroke:var(--brass)}
.rp-n{font-family:var(--label);font-size:9px;fill:var(--faint);letter-spacing:.08em}
.rp-knot.on .rp-n{fill:var(--brass)}
.rp-knot.on{animation:heat .8s ease-out both;animation-delay:calc(var(--i) * 90ms)}
@keyframes heat{0%{opacity:.35;filter:brightness(1.8)}100%{opacity:1;filter:none}}
.knots{list-style:none;margin:0;padding:0;display:grid;gap:8px}
.knot{display:grid;grid-template-columns:2.2em minmax(0,1fr) auto;gap:4px 10px;align-items:start;border-bottom:1px dotted var(--rule);padding-bottom:6px}
.knot .rn{font-family:var(--display);color:var(--faint);font-size:1.3rem;line-height:1}
.knot.on .rn{color:var(--brass)}
.knot>div{display:grid;gap:1px}
.knot b{font-weight:700;color:var(--dim)} .knot.on b{color:var(--ink)}
.knot .m{font-size:.86rem;color:var(--dim)}

/* map */
.map{width:100%;height:auto;display:block;border:1px solid var(--rule);border-radius:6px}
.mp-bg{fill:var(--plate)}
.mp-sea{fill:#121a24}
.mp-coast{fill:none;stroke:var(--t5);stroke-width:1.2;opacity:.8}
.mp-peaks{fill:none;stroke:var(--dim);stroke-width:1.4;stroke-linejoin:round}
.mp-peaks2{fill:none;stroke:var(--faint-stroke);stroke-width:1}
.mp-hills{fill:none;stroke:var(--faint-stroke);stroke-width:1}
.mp-wood{fill:url(#wood);stroke:var(--faint-stroke);stroke-width:.8}
.mp-tree{fill:none;stroke:var(--faint-stroke);stroke-width:.8}
.mp-ash{fill:url(#ash);stroke:var(--faint-stroke);stroke-width:.6;opacity:.8}
.mp-hatch{stroke:var(--faint-stroke);stroke-width:.6}
.mp-river{fill:none;stroke:var(--t5);stroke-width:2;stroke-linecap:round}
.mp-stones{stroke:var(--dim);stroke-width:1.2}
.mp-road{fill:none;stroke:var(--brass-dim);stroke-width:1;stroke-dasharray:3 3}
.mp-steps{fill:none;stroke:var(--dim);stroke-width:1;stroke-linejoin:round}
.mp-route{fill:none;stroke:var(--ember);stroke-width:1.6;stroke-dasharray:4 3;opacity:.9}
.mp-dot{fill:var(--faint);stroke:none}
.mp-pt.visited .mp-dot{fill:var(--brass)}
.mp-pt.current .mp-dot{fill:var(--ember)}
.mp-ring{fill:none;stroke:var(--ember);stroke-width:1.5;opacity:.8;transform-origin:center;transform-box:fill-box;animation:ring 2.4s ease-out infinite}
@keyframes ring{0%{transform:scale(.55);opacity:.9}100%{transform:scale(1.25);opacity:0}}
.mp-lbl{font-family:var(--label);font-size:9.5px;fill:var(--ink);letter-spacing:.04em;paint-order:stroke;stroke:var(--plate);stroke-width:3px;stroke-linejoin:round}
.mp-lbl.region{fill:var(--dim);font-size:9px;letter-spacing:.14em;text-transform:uppercase}
.mp-lbl.faint,.mp-pt.faint .mp-lbl{fill:var(--faint)}
.mp-pt.current .mp-lbl{fill:var(--brass);font-weight:700;font-size:10.5px}
.legend{font-size:.82rem;color:var(--dim);display:flex;gap:6px 12px;flex-wrap:wrap}
.lg.ember{color:var(--ember)} .lg.brass{color:var(--brass)} .lg.faint{color:var(--faint)} .lg.route{color:var(--ember);letter-spacing:-.1em}

/* now page */
.comps{display:grid;gap:10px}
.comp{display:grid;grid-template-columns:auto minmax(0,1fr);gap:12px;align-items:start;color:var(--ink);border:1px solid var(--rule);border-radius:6px;padding:10px}
.comp:hover{text-decoration:none;border-color:var(--brass-dim)}
.comp>div{display:grid;gap:2px;min-width:0}
.comp .m{font-size:.88rem;color:var(--dim)}
.rk-mini{display:grid;gap:12px}
.mini-attrs{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}
.mini-attr{display:grid;gap:0;border-top:2px solid var(--rule);padding-top:6px}
.mini-attr .v{font-family:var(--display);font-weight:700;font-size:1.8rem;line-height:1}
.mini-attr .fell{font-size:.8rem;color:var(--faint)}
.rolls{list-style:none;margin:0;padding:0;display:grid;gap:8px}
.roll{display:grid;grid-template-columns:auto minmax(0,1fr) auto;gap:4px 10px;align-items:center;border-bottom:1px dotted var(--rule);padding-bottom:6px}
.roll .m{grid-column:1/-1;font-size:.82rem;color:var(--faint)}

/* roster */
.filters{display:flex;flex-wrap:wrap;gap:8px 20px;align-items:center}
.fgrp{display:inline-flex;flex-wrap:wrap;gap:6px;align-items:center}
.filters .lbl{margin-right:2px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:10px}
.card{display:grid;grid-template-columns:auto minmax(0,1fr);gap:12px;align-items:start;padding:10px;border:1px solid var(--rule);border-radius:6px;color:var(--ink)}
.card:hover{text-decoration:none;border-color:var(--brass-dim)}
.card-body{display:grid;gap:4px;min-width:0}
.card .m{font-size:.82rem;color:var(--faint)}
.card[hidden]{display:none}
.memorial .card{border-color:var(--brass-dim);background:linear-gradient(180deg,rgba(207,166,95,.08),transparent)}

/* character pages */
.quote blockquote{margin:0;font-family:var(--body);font-size:1.15rem;font-style:italic;color:var(--ink);border-left:2px solid var(--brass);padding-left:12px;line-height:1.5}
.quote figcaption{font-size:.85rem;color:var(--dim);margin-top:6px}
.rels{list-style:none;margin:0;padding:0;display:grid;gap:10px}
.rel{display:grid;gap:4px;border-bottom:1px dotted var(--rule);padding-bottom:8px}
.rel-top{display:flex;justify-content:space-between;gap:8px;align-items:baseline;flex-wrap:wrap}
.rel-top b{flex:0 0 auto} .rel-top .lbl{margin-left:auto;text-align:right}
.rel p{font-size:.92rem}
.facts{list-style:none;margin:0;padding:0;display:grid;gap:6px}
.facts li{display:grid;gap:2px;font-size:.95rem;border-bottom:1px dotted var(--rule);padding-bottom:5px}
.facts .src{font-size:.8rem;color:var(--faint)}
.rk-card{border:1px solid var(--brass-dim);border-radius:6px;padding:12px 14px;display:grid;gap:8px;background:linear-gradient(180deg,rgba(207,166,95,.06),transparent)}
.rk-h{font-family:var(--label);letter-spacing:.12em;color:var(--brass);font-size:.9rem}
.rk-line{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.rk-line.borrowed{color:var(--t6)} .rk-line.earned{color:var(--ink)} .rk-line.unlit{color:var(--dim)}
.rk-line.deeper{color:var(--t1);font-style:italic}
.rk-attrs{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}
.rk-attr{display:grid;border-top:2px solid var(--rule);padding-top:6px}
.rk-attr .v{font-family:var(--display);font-weight:700;font-size:1.6rem;line-height:1}
.rk-attr.borrowed{border-top-color:var(--t5)} .rk-attr.borrowed .v{color:var(--t6)}
.rk-attr.earned{border-top-color:var(--brass-dim)} .rk-attr.earned .v{color:var(--brass)}
.rk-attr.unlit .v{color:var(--dim)}

/* the reader */
.reader{display:grid;gap:22px}
.reader p{font-size:18px;line-height:1.65;max-width:65ch}
.reader p+p{margin-top:0}
.reader .scene{display:grid;gap:18px}
.previously{font-size:.95rem;color:var(--dim);border-left:2px solid var(--brass-dim);padding-left:10px;max-width:65ch;line-height:1.5}
.previously .lbl{display:block;margin-bottom:2px}
.book-line{font-family:var(--label);letter-spacing:.14em;color:var(--brass);font-size:.9rem}
.ch-title{font-family:var(--display);font-weight:700;font-size:2.1rem;line-height:1.1;display:grid;gap:4px}
.ch-title .lbl{font-size:.85rem}
.epigraph{margin:0;padding:0 0 4px}
.epigraph blockquote{margin:0;border-left:2px solid var(--brass-dim);padding-left:14px}
.epigraph p{font-style:italic;color:var(--dim);font-size:17px;max-width:60ch}
.epigraph figcaption{font-family:var(--label);letter-spacing:.06em;color:var(--faint);font-size:.85rem;margin-top:8px;padding-left:14px}
.scene-h{font-family:var(--display);font-weight:700;font-size:1.55rem;line-height:1.15;border-bottom:1px solid var(--rule);padding-bottom:6px;display:flex;gap:12px;align-items:baseline;flex-wrap:wrap}
.scene-n{font-family:var(--label);font-size:.85rem;letter-spacing:.1em;color:var(--brass)}
.reader h3{font-family:var(--display);font-weight:700;font-size:1.3rem}
hr.break{border:0;border-top:1px solid var(--rule);width:40%;margin:4px auto}
.ornament{text-align:center;color:var(--brass-dim);letter-spacing:.4em;font-size:.9rem}
.reader blockquote{margin:0;border-left:2px solid var(--brass-dim);padding-left:14px;color:var(--dim)}
.reckoning{border:1px solid var(--brass-dim);border-radius:6px;padding:12px 14px;background:linear-gradient(180deg,rgba(207,166,95,.08),transparent);display:grid;gap:4px;max-width:65ch}
.reckoning p{font-size:1rem;line-height:1.5;color:var(--t1);font-family:var(--body)}
.reckoning .rk-h{color:var(--brass)}
.dice{font-family:var(--body);display:flex;flex-wrap:wrap;gap:6px 10px;align-items:center;border:1px dashed var(--rule);border-radius:4px;padding:8px 10px;max-width:65ch}
.dice-tag{font-family:var(--label);letter-spacing:.08em;font-size:.82rem;color:var(--brass);border:1px solid var(--brass-dim);border-radius:3px;padding:1px 7px;white-space:nowrap}
.dice-body{font-variant-numeric:tabular-nums}
.choice-h{font-family:var(--display);font-size:1.35rem;color:var(--brass)}
ol.choice{margin:0;padding-left:1.4em;display:grid;gap:8px;max-width:65ch;font-size:17px;line-height:1.5}
ol.choice li.taken{color:var(--ink)} ol.choice li.taken::marker{color:var(--good)}
ol.choice li{color:var(--dim)}
ol.choice li s{color:var(--faint)}
.reader ul,.reader ol:not(.choice){max-width:65ch;font-size:17px;line-height:1.55}
.nm{color:var(--ink);border-bottom:1px dotted var(--brass-dim)}
.nm:hover{text-decoration:none;color:var(--brass)}
.cast{display:grid;gap:8px;border-top:1px solid var(--rule);padding-top:12px}
.pager{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;border-top:1px solid var(--rule);padding-top:14px}
.pager a{display:grid;gap:2px;align-content:start;color:var(--ink)}
.pager a.next{text-align:right}
.pager .lbl{font-size:.75rem}

@media (prefers-reduced-motion:reduce){
  html{scroll-behavior:auto}
  .rp-knot.on{animation:none}
  .mp-ring{animation:none;opacity:.6}
  .bar>i{transition:none}
}
"""

JS = r"""/* THE UNKNEELING — small helpers. Every page works without this file. */
(function(){
"use strict";
var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
/* reading progress */
var bar = document.querySelector(".progress>i");
if (bar && document.body.classList.contains("reader-page")) {
  var tick = function(){
    var h = document.documentElement, max = h.scrollHeight - h.clientHeight;
    bar.style.width = (max > 0 ? Math.min(100, 100 * h.scrollTop / max) : 0).toFixed(1) + "%";
  };
  window.addEventListener("scroll", tick, {passive:true}); tick();
} else if (bar) { bar.parentNode.removeChild(bar); }
/* roster filters */
var box = document.querySelector("[data-filters]");
if (box) {
  var cards = Array.prototype.slice.call(document.querySelectorAll(".card"));
  var active = {faction:null, status:null};
  var apply = function(){
    cards.forEach(function(c){
      var ok = (!active.faction || c.getAttribute("data-faction") === active.faction) &&
               (!active.status || c.getAttribute("data-status") === active.status);
      c.hidden = !ok;
    });
    box.querySelectorAll("button").forEach(function(b){
      var f = b.getAttribute("data-filter");
      b.setAttribute("aria-pressed", f === "all" ? String(!active.faction && !active.status) : String(active[f] === b.getAttribute("data-value")));
    });
  };
  box.addEventListener("click", function(e){
    var b = e.target.closest("button[data-filter]"); if (!b) return;
    var f = b.getAttribute("data-filter"), v = b.getAttribute("data-value");
    if (f === "all") { active.faction = null; active.status = null; }
    else { active[f] = active[f] === v ? null : v; }
    apply();
  });
  apply();
}
if (reduce) { document.documentElement.classList.add("reduce"); }
})();
"""


# ============================================================ main
def main():
    try:
        site = Site()
        site.build()
        tmp = Path(tempfile.mkdtemp(prefix="unkneeling-site-"))
        run_checks(site, tmp)
    except Exception:
        if PROBLEMS:
            print(f"problems found before the build crashed ({len(PROBLEMS)}):", file=sys.stderr)
            for p in PROBLEMS:
                print("  - " + p, file=sys.stderr)
        raise
    for k, v in site.pages.items():
        p = tmp / k
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(v, encoding="utf-8")
    if PROBLEMS and not FORCE:
        print(f"BUILD FAILED: {len(PROBLEMS)} problem(s). docs/ left untouched.", file=sys.stderr)
        for p in PROBLEMS:
            print("  - " + p, file=sys.stderr)
        shutil.rmtree(tmp, ignore_errors=True)
        sys.exit(1)
    if DOCS.exists():
        shutil.rmtree(DOCS)
    shutil.copytree(tmp, DOCS)
    shutil.rmtree(tmp, ignore_errors=True)
    n_pages = sum(1 for k in site.pages if k.endswith(".html"))
    print(f"site built: {n_pages} pages, {len(site.chars)} characters, {len(site.chapters)} chapters → docs/" + (
        f"  (with {len(PROBLEMS)} problem(s), forced)" if PROBLEMS else "  · all checks passed"))
    if PROBLEMS:
        for p in PROBLEMS:
            print("  - " + p, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
