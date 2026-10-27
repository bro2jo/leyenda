#!/usr/bin/env python3
"""THE UNKNEELING — the site builder. Renders the reader-facing site into docs/ from the Chronicle only.

Reads (and nothing else):
  saga/chronicle/*.md                      the story, by chapter
  saga/characters/*.json                   the cast, as the page has shown it
  saga/state/world.json, places.json, factions.json, darrow.json, bearing.json, codex.md, codex_art.json, chapters.csv, rolls.csv
  engine/rules.json                        game data (knots, arts, ranks)
  saga/art/                                images and songs the user supplies, published as files when places.json names one
                                           or factions.json names one (image, image_alt, image_caption, image_focus; only
                                           for an entry already on the page), or codex_art.json names one for a codex.md
                                           entry (same keys plus name) or a character file does (portrait,
                                           portrait_alt, portrait_focus). Every picture sits
                                           in a fixed frame (places 16:9, portraits square) and is cropped to fit, never
                                           stretched; *_focus ("50% 30%") picks the crop's centre; tap shows it whole.
                                           A song (saga/art/songs/, codex_art.json audio + audio_title) plays in its Codex
                                           entry and from a small button in the story where the page sings it.
                                           Small pictures use the copies in saga/art/thumbs/ (engine/thumbs.py; a missing or
                                           stale copy falls back to the picture, with a note); the full file loads only when
                                           an entry is opened or a picture tapped. saga/art/site/: the favicon's bitmaps.
Never: real/, engine/deeds.csv, saga/bible/ or any _gm/ directory (the checks open saga/bible/_gm/*.md and
saga/state/_gm/*.md only to build blocklists; nothing from them is ever rendered).

Conventions the parser and the checks rely on:
  Scenes      '## I. Title' (prologue parts), '### Scene N — Title', '## Climax — Title', '### Choice — Title'.
  Interlude   '### Interlude — Title': another POV, not tied to a day. Scene key and anchor 'interlude'
              (a second one in the same chapter: 'interlude-2'), label "Interlude".
  Between     '### Between — Title': a role-play piece between two scenes (the /play skill): the scene extended by
              Darrow's own action, a moment (short), no choice list. Scene key and anchor 'between-K' (K counts up
              within the chapter), label "Between". Rendered smaller, listed with the scenes, never counted as one.
  Choices     a heading line '**What does Darrow do?**' (the chapter's climax choice) or
              '**What does Darrow say?**' (a small choice inside a scene) followed by a numbered list.
              world.json → choices[] records answers as {chapter, scene, kind, option, text, date, ledger, by}:
              'scene' is the key of the scene whose list it answers ('climax', '3', 'interlude'), chapters compare
              as ints, kind is 'climax' or 'micro', by is 'darrow' or 'bearing' (the latter renders
              "answered for himself"). The Now page titles a micro "A small choice" and a climax "The choice".
  Links       in the story's prose the first mention in a scene of a character (to their page), a place or faction on
              the page, or a codex.md thing (to its Codex entry, #place-<id> / #faction-<id> / #codex-<slug>) is a link
              carrying a preview: its picture if it has one, a title and one line (characters: name and epithet only).
              Hover or focus on a desktop; first tap on a touch screen. Places and factions may list `aliases`.
  Songs       a codex.md entry with audio in codex_art.json: the Codex shows the browser's player; in the story a small
              play button follows the first linked mention of its name in a scene, or ends the first block (paragraph,
              quote, epigraph) that sings one of the lines its entry quotes in italics (four words or more). Once per
              scene. An MP3's embedded lyrics (ID3 USLT) must all be lines the chronicle already has (the build fails
              otherwise; the rest of a song stays in the Annals until the page sings it).
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
import hashlib
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
TALES = CHRON / "tales"   # the tales: the past, a piece per task of a work (design.md §12); NN-slug.md under `### Piece K — Title`
CHARS = SAGA / "characters"
STATE = SAGA / "state"
ART = SAGA / "art"
THUMBS = ART / "thumbs"   # small and medium copies of every picture, made by engine/thumbs.py (manifest.json names their source)
SITE_ART = ART / "site"   # the favicon's bitmaps (the SVG is FAVICON below), published at the site's root
RULES = ROOT / "engine" / "rules.json"
IMAGE_TYPES = {".webp", ".png", ".jpg", ".jpeg"}
IMAGE_MAX_BYTES = 3 * 1024 * 1024
AUDIO_TYPES = {".mp3", ".m4a", ".ogg", ".opus"}
AUDIO_MAX_BYTES = 10 * 1024 * 1024
READ_ALLOW = [CHRON, CHARS, ART, STATE / "world.json", STATE / "places.json", STATE / "factions.json",
              STATE / "darrow.json", STATE / "bearing.json", STATE / "codex.md", STATE / "codex_art.json", STATE / "chapters.csv",
              STATE / "rolls.csv", RULES]

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


_SHA1 = {}


def file_sha1(path):
    """The SHA-1 of a file under the allow-list (a thumbnail's manifest names the exact picture it was made from)."""
    path = Path(path)
    if not any(path == a or a in path.parents for a in READ_ALLOW):
        raise SystemExit(f"build refuses to read {path}")
    if path not in _SHA1:
        _SHA1[path] = hashlib.sha1(path.read_bytes()).hexdigest()
    return _SHA1[path]


def image_size(path):
    """(width, height) of a WebP, PNG or JPEG from its header, or None. Standard library only."""
    path = Path(path)
    if not any(path == a or a in path.parents for a in READ_ALLOW):
        raise SystemExit(f"build refuses to read {path}")
    b = path.read_bytes()
    le = lambda x: int.from_bytes(x, "little")
    if b[:4] == b"RIFF" and b[8:12] == b"WEBP":
        kind = b[12:16]
        if kind == b"VP8X":
            return 1 + le(b[24:27]), 1 + le(b[27:30])
        if kind == b"VP8 " and b[23:26] == b"\x9d\x01\x2a":
            return le(b[26:28]) & 0x3FFF, le(b[28:30]) & 0x3FFF
        if kind == b"VP8L" and b[20] == 0x2F:
            bits = le(b[21:25])
            return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
        return None
    if b[:8] == b"\x89PNG\r\n\x1a\n":
        return int.from_bytes(b[16:20], "big"), int.from_bytes(b[20:24], "big")
    if b[:2] == b"\xff\xd8":
        i = 2
        while i + 9 < len(b):
            if b[i] != 0xFF:
                i += 1
                continue
            marker = b[i + 1]
            if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
                i += 2
                continue
            seg = int.from_bytes(b[i + 2:i + 4], "big")
            if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                return int.from_bytes(b[i + 7:i + 9], "big"), int.from_bytes(b[i + 5:i + 7], "big")
            i += 2 + seg
    return None


def mp3_lyrics(path):
    """The lyrics an MP3 carries in its ID3v2 tag (USLT frames), as a list of lines, or None when it carries none.
    Standard library only; anything it cannot parse reads as no lyrics."""
    path = Path(path)
    if not any(path == a or a in path.parents for a in READ_ALLOW):
        raise SystemExit(f"build refuses to read {path}")
    b = path.read_bytes()
    if b[:3] != b"ID3" or b[3] not in (3, 4):
        return None
    ver, flags = b[3], b[5]
    synch = lambda x: (x[0] << 21) | (x[1] << 14) | (x[2] << 7) | x[3]
    tag = b[10:10 + synch(b[6:10])]
    if flags & 0x80:  # whole-tag unsynchronisation
        tag = tag.replace(b"\xff\x00", b"\xff")
    i = 0
    if flags & 0x40:  # extended header
        i = synch(tag[:4]) if ver == 4 else 4 + int.from_bytes(tag[:4], "big")
    out = []
    while i + 10 <= len(tag) and tag[i:i + 4].strip(b"\0"):
        fid, raw = tag[i:i + 4], tag[i + 4:i + 8]
        size = synch(raw) if ver == 4 else int.from_bytes(raw, "big")
        fflags = int.from_bytes(tag[i + 8:i + 10], "big")
        data = tag[i + 10:i + 10 + size]
        i += 10 + size
        if fid != b"USLT" or len(data) < 5:
            continue
        if ver == 4 and fflags & 0x0002:
            data = data.replace(b"\xff\x00", b"\xff")
        if ver == 4 and fflags & 0x0001:
            data = data[4:]
        enc, body = data[0], data[4:]
        codec, nul = {0: ("latin-1", b"\0"), 1: ("utf-16", b"\0\0"), 2: ("utf-16-be", b"\0\0")}.get(enc, ("utf-8", b"\0"))
        j = 0
        while True:  # the content descriptor ends at the first null on a character boundary
            j = body.find(nul, j)
            if j < 0 or len(nul) == 1 or j % 2 == 0:
                break
            j += 1
        text = body[j + len(nul):] if j >= 0 else body
        try:
            text = text.decode(codec)
        except UnicodeDecodeError:
            continue
        out += [ln.strip() for ln in re.split(r"\s+/\s+|[\r\n]+", text.strip("\0")) if ln.strip()]
    return out or None


def words_of(s):
    """Plain words, for matching sung lines against the page whatever the punctuation, emphasis or line breaks."""
    s = html.unescape(str(s)).lower().replace("’", "'").replace("‘", "'")
    return " ".join(re.findall(r"[a-z0-9]+(?:'[a-z0-9]+)*", s))


def esc(s):
    return html.escape("" if s is None else str(s), quote=True)


def slug(s):
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s or "x"


def excerpt(text, limit=150):
    """One short line for a name's preview card: the first clause (to the first '; ' or '. '), without a trailing
    source note like "(Ch 1)", capitalised and capped. Only ever fed reader-safe text already shown on the site."""
    s = re.sub(r"\*\*|\*|`|~~", "", str(text or "")).strip()
    cut = [i for i in (s.find("; "), s.find(". ")) if i > 0]
    if cut:
        s = s[:min(cut)]
    s = re.sub(r"\s*\((?:Prologue|Ch(?:apter)?\b)[^)]*\)\s*\.?$", "", s).rstrip(" .,:;")
    if len(s) > limit:
        s = s[:limit].rsplit(" ", 1)[0].rstrip(" ,;:") + "…"
    elif s:
        s += "."
    return s[:1].upper() + s[1:]


ROMAN = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
         (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]


def roman(n):
    """Roman numerals for any positive whole number; 0 is empty (a rank not yet held)."""
    n = as_int(n) if not isinstance(n, int) else n
    if n is None or n < 0:
        return str(n)
    out = ""
    for v, s in ROMAN:
        while n >= v:
            out, n = out + s, n - v
    return out


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
BETWEEN_RE = re.compile(r"^###\s+Between\s*[—–-]\s*(.+)$")
CLIMAX_RE = re.compile(r"^##\s+Climax\s*[—–-]\s*(.+)$")
CHOICE_RE = re.compile(r"^###\s+Choice\s*[—–-]\s*(.+)$")
HEAD_RE = re.compile(r"^(#{2,3})\s+(.+)$")
CHAPTER_RE = re.compile(r"^(Chapter\s+(\d+)|Prologue)\s*[—–-]\s*(.+)$")
TALE_RE = re.compile(r"^#\s+Tale\s+(\d+)\s*[—–-]\s*(.+)$")
PIECE_RE = re.compile(r"^###\s+Piece\s+(\d+)\s*[—–-]\s*(.+)$")
CHOICE_HEAD_RE = re.compile(r"^\*\*What does Darrow (do|say)\?\*\*$")


def parse_chapter(path):
    return parse_chapter_text(read(path), path)


def parse_tale(path):
    """A tale file, parsed like a chapter: `# Tale N — Title`, the italic line of when it is set, `---`, then
    `### Piece K — Title` blocks. It comes back in the chapter's shape (scenes are its pieces) with tale=True, so the
    registry, the links and the character pages treat a piece like a scene."""
    text = read(path)
    out, n_tale = [], None
    for ln in text.split("\n"):
        m = TALE_RE.match(ln.strip())
        if m and n_tale is None:
            n_tale = int(m.group(1))
            out.append(f"# Chapter {m.group(1)} — {m.group(2)}")
            continue
        mp = PIECE_RE.match(ln.strip())
        if mp:
            out.append(f"### Scene {mp.group(1)} — {mp.group(2)}")
            continue
        if re.match(r"^#{1,3}\s+(Scene|Interlude|Between|Climax|Choice)\b", ln.strip(), re.I):
            problem(f"tales/{path.name}: a tale holds pieces only ('### Piece K — Title'), not '{ln.strip()}'")
        out.append(ln)
    if n_tale is None:
        problem(f"tales/{path.name}: no '# Tale N — Title' heading")
        n_tale = 0
    ch = parse_chapter_text("\n".join(out), path)
    m = re.match(r"^(\d+)-", path.name)
    if m and int(m.group(1)) != n_tale:
        problem(f"tales/{path.name}: the file is numbered {int(m.group(1))} but its heading says Tale {n_tale}")
    ch.update({"tale": True, "code": f"tale{n_tale:02d}", "number": n_tale, "label": f"Tale {n_tale}", "book": None,
               "when": " ".join(ch["epigraph"]["lines"]) if ch.get("epigraph") else ""})
    ch["epigraph"] = None
    for sc in ch["scenes"]:
        if sc["key"].isdigit():
            sc.update({"key": "p" + sc["key"], "label": "Piece " + sc["key"], "anchor": "piece-" + sc["key"]})
        else:
            problem(f"tales/{path.name}: text before the first piece ('{sc['title'] or sc['key']}'); a tale is its pieces")
    return ch


def parse_chapter_text(text, path):
    lines = text.split("\n")
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

    def scene(key, label, title, anchor, between=False):
        if anchor in anchors_seen:
            problem(f"{path.name}: two scenes share the anchor '{anchor}'")
        anchors_seen.add(anchor)
        s = {"key": key, "label": label, "title": title, "anchor": anchor, "blocks": [], "between": between}
        ch["scenes"].append(s)
        return s

    para = []
    pending_choice = None  # None, or "do" / "say": which choice heading the next numbered list answers
    n_interludes = 0
    n_between = 0

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
        m = BETWEEN_RE.match(s)
        if m:
            flush()
            n_between += 1
            key = f"between-{n_between}"
            cur = scene(key, "Between", m.group(1).strip(), key, between=True)
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
            if re.match(r"^(Scene\b|Interlude\b|Climax\b|Choice\b|Between\b)", head, re.I):
                problem(f"{path.name}: heading '{s}' must be '### Scene N — Title', '### Interlude — Title', '### Between — Title', '## Climax — Title' or '### Choice — Title'")
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
            if pending_choice and cur.get("between"):
                problem(f"{path.name}: a Between ('{cur['title']}') carries a choice list; choices belong to scenes and climaxes (style.md §3)")
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
                elif not rk.get("unread") and ((rk.get("fire") or {}).get("kind")) not in ("grace", "ember", "none"):
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
            ev = f.get("evidence")
            if ev is not None:
                # the excerpt is the fact's proof: a few words of the cited scene, verbatim, or the build stops
                if not isinstance(ev, str) or len(norm(ev)) < 12:
                    problem(f"{p.name}: known_fact '{str(f.get('fact'))[:50]}' evidence must be a verbatim excerpt of the page, a few words at least")
                elif key in registry and norm(ev) not in scene_text(registry[key]["scene"]):
                    problem(f"{p.name}: known_fact '{str(f.get('fact'))[:50]}' cites evidence that chapter {key[0]} scene {key[1]} does not carry: {ev!r}")
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
MARKS = {"none", "knot", "horn", "needle", "pencil", "spyglass", "key", "stone", "note", "knife", "quill", "cup", "candle", "star", "wheel"}
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
    if mark == "wheel":
        return ('<circle cx="50" cy="82" r="14" class="sg-l"/><circle cx="50" cy="82" r="3" class="sg-l"/>'
                '<path d="M50 68 L50 96 M36 82 L64 82 M40 72 L60 92 M60 72 L40 92" class="sg-s"/>')
    if mark == "bell":
        return '<path d="M50 64 C41 66 41 78 38 88 L62 88 C59 78 59 66 50 64 Z" class="sg-l"/><path d="M45 92 a5 5 0 0 0 10 0" class="sg-l"/><path d="M50 60 L50 64" class="sg-l"/>'
    if mark == "hand":
        return '<path d="M41 96 L41 78 M47 96 L47 70 M53 96 L53 68 M59 96 L59 74 M41 96 C41 101 59 101 59 96 M41 80 L35 86 L41 94" class="sg-l"/>'
    if mark == "word":
        return '<path d="M35 70 L65 70 L65 88 L48 88 L42 95 L42 88 L35 88 Z" class="sg-l"/><path d="M41 77 L59 77 M41 82 L54 82" class="sg-s"/>'
    if mark == "cord":
        return '<path d="M37 82 C37 70 63 70 63 82 C63 94 37 94 37 82 Z" class="sg-l"/><path d="M44 73 C51 79 51 85 44 91 M56 73 C49 79 49 85 56 91" class="sg-s"/>'
    if mark == "coin":
        return '<circle cx="50" cy="82" r="13" class="sg-l"/><circle cx="50" cy="82" r="7" class="sg-s"/><path d="M50 75 L50 89" class="sg-s"/>'
    return ""


SHELF_MARKS = (MARKS - {"none"}) | {"bell", "hand", "word", "cord", "coin"}  # a keepsake's drawing on the shelf (records.py → KEEPSAKE_MARKS names the same set)
TIER_SEAL = {"Triumph": "triumph", "Hard-won": "hardwon", "Costly": "costly", "Setback": "setback"}


# The palette, as in CSS :root. The drawings below carry their colours in the SVG itself, so a page shows them right even while a
# browser still holds an older stylesheet; the stylesheet only places them.
PAL = {"brass": "#CFA65F", "brass_dim": "#8A7044", "ember": "#E2713B", "good": "#72B396", "warn": "#D9A441", "bad": "#D0634D",
       "ink": "#E8E2D4", "faint": "#646D79", "raw": "#262D37", "plate": "#161B22", "t3": "#A86B3C", "t4": "#7A4D86",
       "t4_text": "#A77FB5", "t5": "#4062A3", "t6": "#8BB2D3"}
SVG_LABEL_FONT = "Alegreya Sans SC, Alegreya Sans, Segoe UI, sans-serif"
SVG_DISPLAY_FONT = "Grenze Gotisch, Georgia, serif"


def svg_tree(tree, size=22):
    """A glyph per Art tree: a sword, two footprints, three breaths of wind, a looped rope, an eye, a thrown disc."""
    body = {
        "Blade": '<path d="M12 2.5 L14.2 6 L14.2 15.5 L9.8 15.5 L9.8 6 Z M6.5 15.8 L17.5 15.8 M12 16 L12 20.2"/><circle cx="12" cy="21.4" r="1.2"/>',
        "Footing": f'<g fill="{PAL["brass"]}" stroke="none"><ellipse cx="8" cy="13.2" rx="2.9" ry="3.6"/><ellipse cx="8" cy="19.6" rx="2.1" ry="1.9"/><ellipse cx="16" cy="5.7" rx="2.9" ry="3.6"/><ellipse cx="16" cy="12.1" rx="2.1" ry="1.9"/></g>',
        "Breath": '<path d="M4 8 H13.5 a2.5 2.5 0 1 0 -2.5 -2.5 M4 13 H17.5 a2.5 2.5 0 1 1 -2.5 2.5 M4 18 H10.5 a2 2 0 1 0 -2 -2"/>',
        "Binding": '<path d="M2 17 C6.5 17 7.5 5 12.5 5 C18.5 5 18.5 13.5 12.5 13.5 C8 13.5 9 17 22 17"/>',
        "Insight": '<path d="M3 12 C8 5 16 5 21 12 C16 19 8 19 3 12 Z"/><circle cx="12" cy="12" r="3"/>',
        "Sport": '<ellipse cx="13.5" cy="11.5" rx="7.5" ry="3"/><path d="M3 16 L8 15 M3 19.5 L10 17.5"/>',
    }.get(tree, '<circle cx="12" cy="12" r="7"/>')
    return (f'<svg class="tg" viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="{PAL["brass"]}" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{body}</svg>')


def rank_ring(rank, n, frac=0.0, label="", size=32, sealed=False):
    """An Art's rank as a ring of n segments: the filled ones its rank, the next one filling with practice; the numeral inside.
    Violet while the Art is sealed (its rank banked)."""
    import math
    r, c = 14, 18
    circ = 2 * math.pi * r
    step, gap = circ / max(n, 1), 3.0
    on = PAL["t4"] if sealed else PAL["brass"]
    part = PAL["t4"] if sealed else PAL["brass_dim"]
    segs = [f'<circle cx="{c}" cy="{c}" r="{r}" fill="none" stroke="{PAL["raw"]}" stroke-width="4"/>']
    for i in range(n):
        if i < rank:
            L, col, op = step - gap, on, ""
        elif i == rank and frac > 0:
            L, col, op = max(0.0, (step - gap) * min(frac, 1.0)), part, ' stroke-opacity=".7"' if sealed else ""
        else:
            continue
        segs.append(f'<circle cx="{c}" cy="{c}" r="{r}" fill="none" stroke="{col}"{op} stroke-width="4" stroke-dasharray="{L:.2f} {circ - L:.2f}" '
                    f'stroke-dashoffset="{-i * step:.2f}" transform="rotate(-90 {c} {c})"/>')
    num = (f'<text x="{c}" y="{c + 0.5}" text-anchor="middle" dominant-baseline="central" font-family="{SVG_LABEL_FONT}" font-size="11" '
           f'font-weight="700" fill="{PAL["t4_text"] if sealed else PAL["ink"]}">{roman(rank) if rank else "·"}</text>')
    return f'<svg class="rring" viewBox="0 0 36 36" width="{size}" height="{size}" role="img" aria-label="{esc(label or f"rank {rank} of {n}")}">{"".join(segs)}{num}</svg>'


def svg_seal(tier, size=44):
    """A chapter's tier as a wax seal: a sunburst (Triumph), a notched sword (Hard-won), a tipped balance (Costly), a cracked ring (Setback)."""
    kind = TIER_SEAL.get(tier)
    if not kind:
        return ""
    dev = {
        "triumph": '<circle cx="24" cy="24" r="4.5"/><path d="M24 8 L24 14 M24 34 L24 40 M8 24 L14 24 M34 24 L40 24 M12.7 12.7 L17 17 M31 31 L35.3 35.3 M35.3 12.7 L31 17 M17 31 L12.7 35.3"/>',
        "hardwon": '<path d="M24 9 L24 31 M17 31 L31 31 M24 31 L24 38 M20.5 13.5 L24 9 L27.5 13.5 M24 20 L27 23"/>',
        "costly": '<path d="M24 11 L24 37 M19 37 L29 37 M12 20 L36 16 M12 20 L8 29 L16 29 Z M36 16 L32 25 L40 25 Z"/>',
        "setback": '<path d="M15 19 L24 29 L33 19"/><path d="M24 6 L22 11 L25.5 14.5"/>',
    }[kind]
    col = PAL["ember"] if kind in ("costly", "setback") else PAL["brass"]
    return (f'<svg class="seal {kind}" viewBox="0 0 48 48" width="{size}" height="{size}" role="img" aria-label="{esc(TIER_DONE.get(tier, tier))}">'
            f'<circle cx="24" cy="24" r="21" fill="{PAL["plate"]}" stroke="{col}" stroke-width="2"/>'
            f'<circle cx="24" cy="24" r="17.5" fill="none" stroke="{col}" stroke-opacity=".55" stroke-width="1" stroke-dasharray="2 2.5"/>'
            f'<g fill="none" stroke="{col}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">{dev}</g></svg>')


def tally(n, size=18):
    """n strokes in fives: four uprights and a strike through them."""
    n = max(0, int(n or 0))
    if not n:
        return ""
    groups, rem = divmod(n, 5)
    w = groups * 22 + (rem * 5 + 2 if rem else 0) + 2
    parts, x = [], 2
    for _ in range(groups):
        parts.append(f'<path d="M{x} 2 V18 M{x + 5} 2 V18 M{x + 10} 2 V18 M{x + 15} 2 V18 M{x - 2} 16 L{x + 18} 4"/>')
        x += 22
    for i in range(rem):
        parts.append(f'<path d="M{x + i * 5} 2 V18"/>')
    return (f'<svg class="tally" viewBox="0 0 {w} 20" width="{w * size / 20:.0f}" height="{size}" fill="none" stroke="{PAL["brass"]}" stroke-width="2" '
            f'stroke-linecap="round" role="img" aria-label="{n} finished">{"".join(parts)}</svg>')


MOOD_FLAMES = {"devoted": 3, "loyal": 3, "fond": 2, "warming": 1, "civil": 0, "wary": 0, "cold": 0, "hostile": 0, "an enemy": 0}
MOOD_COAL = {"devoted": "t3", "loyal": "t3", "fond": "t3", "warming": "t3", "civil": "t3", "wary": "faint", "cold": "t5", "hostile": "t5", "an enemy": "t5"}


def mood_mark(word, size=16):
    """A companion's regard as an ember: the coal warm, grey or cold, a tongue of flame per degree of warmth, a halo when devoted."""
    w = str(word or "")
    flames = MOOD_FLAMES.get(w, 0)
    xs = {1: [10], 2: [7.5, 12.5], 3: [5.5, 10, 14.5]}.get(flames, [])
    tongues = "".join(f'<path d="M{x} 14 C{x - 2.5} 10 {x - 1} 8 {x} 3 C{x + 1} 8 {x + 2.5} 10 {x} 14 Z" fill="{PAL["ember"]}"/>' for x in xs)
    halo = f'<circle cx="10" cy="13" r="8.5" fill="none" stroke="{PAL["brass"]}" stroke-opacity=".8" stroke-width="1"/>' if w == "devoted" else ""
    crack = f'<path d="M7 15 L10 11 L12.5 15.5" fill="none" stroke="{PAL["t6"]}" stroke-width="1.3"/>' if w in ("hostile", "an enemy") else ""
    return (f'<svg class="mood" viewBox="0 0 20 20" width="{size}" height="{size}" role="img" aria-label="{esc(w)}">'
            f'{halo}<ellipse cx="10" cy="16" rx="7" ry="2.6" fill="{PAL[MOOD_COAL.get(w, "faint")]}"/>{tongues}{crack}</svg>')


def d20_glyph(nat, result="", size=32):
    """A twenty-sided die with the number it showed; coloured by the outcome, lit for a natural twenty or one."""
    try:
        n = int(str(nat).split("/")[0])
    except (TypeError, ValueError):
        n = None
    res = str(result or "").lower()
    col = PAL["good"] if "success" in res else PAL["warn"] if "partial" in res else PAL["bad"] if "fail" in res else PAL["brass_dim"]
    crit = n in (20, 1)
    lit = f' fill="{PAL["brass"]}" fill-opacity=".14"' if crit else ' fill="none"'
    num = (f'<text x="16" y="17.5" text-anchor="middle" dominant-baseline="central" font-family="{SVG_DISPLAY_FONT}" font-size="{13 if crit else 12}" '
           f'font-weight="700" fill="{PAL["brass"] if crit else PAL["ink"]}">{n}</text>') if n is not None else ""
    return (f'<svg class="d20" viewBox="0 0 32 32" width="{size}" height="{size}" role="img" aria-label="d20 {n if n is not None else ""}">'
            f'<path d="M16 2 L28 9 L28 23 L16 30 L4 23 L4 9 Z"{lit} stroke="{col}" stroke-width="1.4" stroke-linejoin="round"/>'
            f'<path d="M16 9 L25 22 L7 22 Z" fill="none" stroke="{col}" stroke-width="1.2" stroke-linejoin="round"/>'
            f'<path d="M16 2 L16 9 M28 9 L25 22 M4 9 L7 22 M28 23 L25 22 M4 23 L7 22 M16 30 L16 22" fill="none" stroke="{col}" stroke-opacity=".6" stroke-width="1"/>'
            f'{num}</svg>')


def told_marks(told, of, size=10):
    """A tale's pieces as small diamonds, the told ones lit."""
    of = max(1, int(of or 1))
    step = size + 4
    w = of * step
    parts = []
    for i in range(of):
        x = i * step + step / 2
        on = i < int(told or 0)
        parts.append(f'<path d="M{x:.1f} 1 L{x + size / 2 - 1:.1f} {size / 2 + 1:.1f} L{x:.1f} {size} L{x - size / 2 + 1:.1f} {size / 2 + 1:.1f} Z" '
                     f'fill="{PAL["brass"] if on else "none"}" stroke="{PAL["brass"] if on else PAL["brass_dim"]}" stroke-width="1"/>')
    return f'<svg class="told" viewBox="0 0 {w} {size + 2}" width="{w}" height="{size + 2}" role="img" aria-label="{told} of {of} told">{"".join(parts)}</svg>'


def shelf_mark(mark, size=40):
    """A keepsake's mark on the shelf: the sigil drawings, with their colour carried in the SVG."""
    return (f'<svg class="km" viewBox="28 56 44 48" width="{size}" height="{int(size * 1.1)}" aria-hidden="true">'
            f'<g fill="none" stroke="{PAL["brass"]}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round">{svg_mark(mark)}</g></svg>')


def shelf_unknown(size=40):
    """The mark of a keepsake still to come: a dashed ring and a question."""
    return (f'<svg class="km" viewBox="28 56 44 48" width="{size}" height="{int(size * 1.1)}" aria-hidden="true">'
            f'<circle cx="50" cy="80" r="15" fill="none" stroke="{PAL["brass_dim"]}" stroke-width="2.2" stroke-dasharray="3.5 4.5" stroke-linecap="round"/>'
            f'<text x="50" y="81" text-anchor="middle" dominant-baseline="central" font-family="{SVG_DISPLAY_FONT}" font-size="18" font-weight="700" fill="{PAL["brass_dim"]}">?</text></svg>')


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


def bar(have, need, label, cls="", show=None, text=None, quiet=False):
    """A progress bar. text: what screen readers hear instead of the numbers (used for approval, which is never shown as a number).
    quiet: no visible label row (the line above the bar already names it); screen readers still hear the label."""
    need = max(need, 1)
    pct = max(0, min(100, 100.0 * have / need))
    txt = f'<span class="num">{show}</span>' if show is not None else ""
    if text is not None:
        aria = f'role="img" aria-label="{esc(label)}: {esc(text)}"'
    else:
        aria = f'role="progressbar" aria-label="{esc(label)}" aria-valuemin="0" aria-valuemax="{need}" aria-valuenow="{have}"'
    head = "" if quiet else f'<div class="bar-l"><span>{esc(label)}</span>{txt}</div>'
    return f'<div class="bar-row">{head}<div class="bar {cls}" {aria}><i style="--w:{pct:.1f}%"></i></div></div>'


def pips(have, need, cls=""):
    s = "".join(f'<span class="pip{" on" if i < have else ""}"></span>' for i in range(need))
    return f'<span class="pips {cls}" role="img" aria-label="{have} of {need}">{s}</span>'


BEARING_LABEL = "who his choices are making him"  # the site's own label for the Bearing section (exempt from the GM-sentence check)


FINE_PRINT = "Only what the story has shown so far."  # the one line that replaces a disclaimer on every section head


def sec(title, label, inner, cls="", hid=""):
    hid = f' id="{hid}"' if hid else ""
    lbl = f'<span class="lbl">{esc(label)}</span>' if label else ""
    return f'<section class="sec {cls}"{hid}><div class="sec-h"><h2>{esc(title)}</h2>{lbl}</div>{inner}</section>'


def panel(title, meta, inner, pid=""):
    """A section folded shut until opened (Darrow's page): the heading and one line of what is inside on the closed row."""
    pid = f' id="{pid}"' if pid else ""
    meta = f'<span class="meta">{meta}</span>' if meta else ""
    return f'<details class="panel"{pid}><summary><h2>{esc(title)}</h2>{meta}</summary><div class="panel-body">{inner}</div></details>'


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


TIER_DONE = {"Triumph": "A triumph", "Hard-won": "Hard-won", "Costly": "Costly", "Setback": "A setback"}
TIER_SO_FAR = {"Triumph": "so far: a triumph", "Hard-won": "so far: hard-won", "Costly": "so far: costly", "Setback": "so far: turning against him"}
TIER_CLS = {"Triumph": "brass", "Hard-won": "brass", "Costly": "ember", "Setback": "ember"}


# ============================================================ page shell
CUR = ' aria-current="page"'
NAV = [("Now", "index.html"), ("Chronicle", "chronicle/index.html"), ("Tales", "tales/index.html"), ("Characters", "characters/index.html"),
       ("Darrow", "darrow/index.html"), ("Codex", "codex/index.html")]
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Grenze+Gotisch:wght@500;700&family=Alegreya+Sans:ital,wght@0,400;0,500;0,700;1,400&family=Alegreya+Sans+SC:wght@500;700&display=swap">')


ASSET_V = {}


def asset_v(name):
    """A short hash of the stylesheet or the script: its link changes whenever its content does, so a browser never pairs a new
    page with a stylesheet it cached before the change."""
    if name not in ASSET_V:
        ASSET_V[name] = hashlib.sha1((CSS if name == "css" else JS).encode("utf-8")).hexdigest()[:10]
    return ASSET_V[name]


def shell(title, body, rel, current, cls="", desc=""):
    nav = "".join(f'<a href="{rel}{href}"{CUR if name == current else ""}>{name}</a>' for name, href in NAV)
    meta_desc = f'<meta name="description" content="{esc(desc)}">' if desc else ""
    progress = '<div class="progress" aria-hidden="true"><i></i></div>\n' if "reader-page" in cls.split() else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="dark">
<title>{esc(title)} · The Unkneeling</title>
{meta_desc}
<link rel="icon" href="{rel}favicon-32.png" sizes="32x32" type="image/png">
<link rel="icon" href="{rel}favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{rel}apple-touch-icon.png">
{FONTS}
<link rel="stylesheet" href="{rel}site.css?v={asset_v("css")}">
</head>
<body class="{cls}">
<a class="skip" href="#main">Skip to content</a>
{progress}<header class="mast"><div class="wrap mast-in"><a class="brand" href="{rel}index.html">The Unkneeling</a><nav class="nav" aria-label="Site">{nav}</nav></div></header>
<main id="main" class="wrap">
{body}
</main>
<footer class="foot"><div class="wrap"><p>What is given can be taken. What is built is yours.</p><p class="faint">An original saga. The Chronicle is kept as it happens; the Reckoning is read, never written.</p></div></footer>
<script src="{rel}site.js?v={asset_v("js")}" defer></script>
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
        self.tales = [parse_tale(p) for p in sorted(TALES.glob("*.md"))] if TALES.exists() else []
        for t in self.tales:
            if t["empty"]:
                note(f"tales/{t['file']}: no piece yet")
        self.registry = {}
        for ch in self.chapters + self.tales:
            for s in ch["scenes"]:
                self.registry[(ch["code"], s["key"])] = {
                    "href": f"{self.page_dir(ch)}{ch['slug']}.html#{s['anchor']}", "chapter": ch, "scene": s,
                    "label": (f"{ch['label']} · {s['label']}" if s["label"] else ch["label"]) + (f" — {s['title']}" if s["title"] else "")}
        self.chapter_by_number = {ch["number"]: ch for ch in self.chapters}
        self.tale_by_code = {t["code"]: t for t in self.tales}
        self.bearing = self.load_bearing()
        self.check_world()
        self.chars = load_characters(self.registry, self.factions, self.place_by_id)
        self.assets = {}  # published path -> source file (binary, copied as is)
        self.thumbs, self.thumb_missing = self.load_thumbs(), set()
        for c in self.chars.values():
            if c.get("portrait"):
                self.char_portrait(c)
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
            if p.get("image"):
                self.codex_image("places.json", p)
        for f in self.factions.values():
            if f.get("image"):
                self.codex_image("factions.json", f)
        for key, comp in (self.world.get("companions") or {}).items():
            if not isinstance(comp, dict):
                problem(f"world.json: companions.{key} must be an object")
                continue
            hits = [c for c in self.chars if c.split("-")[0] == key]
            if len(hits) > 1:
                problem(f"world.json: companions.{key} matches more than one character file ({', '.join(hits)})")
        self.codex = self.parse_codex()
        self.attach_codex_art()
        self.eye = next((a["rank"] for a in self.darrow.get("arts", []) if a["id"] == "wardens_eye"), 0)
        self.linkers = self.build_linkers()

    @staticmethod
    def page_dir(ch):
        """Where a parsed chapter or tale is published: chronicle/ or tales/."""
        return "tales/" if ch.get("tale") else "chronicle/"

    def register_image(self, where, img, alt):
        """Validate an image under saga/art/ and register it as an asset at art/<path>. Returns (path, size) or None."""
        src = (ART / str(img)).resolve()
        if ART.resolve() not in src.parents:
            problem(f"{where} '{img}' must be a path under saga/art/")
            return None
        if src.suffix.lower() not in IMAGE_TYPES:
            problem(f"{where} '{img}' must be one of {', '.join(sorted(IMAGE_TYPES))}")
            return None
        if not src.is_file():
            problem(f"{where} '{img}' does not exist under saga/art/")
            return None
        if src.stat().st_size > IMAGE_MAX_BYTES:
            problem(f"{where} '{img}' is over {IMAGE_MAX_BYTES // (1024 * 1024)} MB; shrink it before publishing")
        if not str(alt or "").strip():
            problem(f"{where} has no alt text (what the picture shows, for screen readers)")
        rel_src = src.relative_to(ART.resolve()).as_posix()
        path = f"art/{rel_src}"
        self.assets[path] = src
        return path, image_size(src), self.thumb(src, rel_src, "sm") or path, self.thumb(src, rel_src, "md") or path

    def load_thumbs(self):
        """saga/art/thumbs/manifest.json (engine/thumbs.py writes it): {"images": {source path under saga/art/: {sha1, sm, md}}}."""
        path = THUMBS / "manifest.json"
        if not path.exists():
            return {}
        try:
            return json.loads(read(path)).get("images") or {}
        except json.JSONDecodeError as e:
            problem(f"saga/art/thumbs/manifest.json: invalid JSON ({e}); run python3 engine/thumbs.py")
            return {}

    def thumb(self, src, rel_src, size):
        """The small (sm, rows, avatars, previews of a face) or medium (md, a portrait's frame, a place's preview) copy of
        a picture, published at art/thumbs/…, or None when engine/thumbs.py has not made it from this very file (the
        page then shows the picture itself, and the build says so)."""
        t = THUMBS / f"{Path(rel_src).with_suffix('').as_posix()}.{size}.webp"
        e = self.thumbs.get(rel_src) or {}
        if not t.is_file() or e.get("sha1") != file_sha1(src):
            self.thumb_missing.add(rel_src)
            return None
        path = f"art/thumbs/{t.relative_to(THUMBS).as_posix()}"
        self.assets[path] = t
        return path

    @staticmethod
    def focus_style(where, focus, default):
        """An object-position for the crop: "X% Y%" (0-100 each); anything else is a problem and falls back to the default."""
        if focus is None:
            return f' style="object-position:{default}"'
        m = re.fullmatch(r"\s*(\d{1,3})%\s+(\d{1,3})%\s*", str(focus))
        if not m or int(m.group(1)) > 100 or int(m.group(2)) > 100:
            problem(f"{where} focus '{focus}' must look like \"50% 30%\" (each 0-100%)")
            return f' style="object-position:{default}"'
        return f' style="object-position:{m.group(1)}% {m.group(2)}%"'

    def codex_image(self, src, p):
        """A codex entry's picture (a place in places.json or a faction in factions.json): only once it is on the page.
        A codex.md entry's picture comes from codex_art.json (attach_codex_art)."""
        pid = p.get("id", "?")
        if not p.get("on_page"):
            problem(f"{src}: {pid} has an image but is not on the page yet (an image would show it early)")
            return
        got = self.register_image(f"{src}: {pid}.image", p["image"], p.get("image_alt"))
        if got:
            p["_image_path"], p["_image_size"], p["_image_sm"], p["_image_md"] = got
            p["_image_focus"] = self.focus_style(f"{src}: {pid}.image_focus", p.get("image_focus"), "50% 50%")

    def attach_codex_art(self):
        """saga/state/codex_art.json (optional): pictures and songs for codex.md entries, {"entries": [{name, image,
        image_alt, image_caption, image_focus, audio, audio_title}]}, each with an image, an audio file or both. The name
        must be an entry the Codex renders outside Sayings. A song (audio) plays in its Codex entry, and in the story
        wherever the page sings its lines (the italic lines of its codex.md entry) or links its name."""
        self.songs = {}  # codex anchor -> {path, title, cues}
        path = STATE / "codex_art.json"
        if not path.exists():
            return
        by_name = {e["name"]: (e, anchor) for _sec, _bucket, e, anchor in self.codex_things()}
        seen = set()
        for a in load_json(path).get("entries", []):
            nm = str(a.get("name") or "")
            where = f"codex_art.json: {nm or '?'}"
            if nm in seen:
                problem(f"{where} is listed twice")
                continue
            seen.add(nm)
            e, anchor = by_name.get(nm) or (None, None)
            if not e:
                problem(f"{where} is not a codex.md entry the Codex shows (Sayings take no pictures or songs; a person, place or "
                        f"faction with its own file takes its picture there)")
                continue
            if not a.get("image") and not a.get("audio"):
                problem(f"{where} has neither an image nor an audio file")
                continue
            if a.get("image"):
                got = self.register_image(f"{where}.image", a.get("image"), a.get("image_alt"))
                if got:
                    e["_image_path"], e["_image_size"], e["_image_sm"], e["_image_md"] = got
                    e["_image_focus"] = self.focus_style(f"{where}.image_focus", a.get("image_focus"), "50% 50%")
                    e["image_alt"], e["image_caption"] = a.get("image_alt", ""), a.get("image_caption", "")
            if a.get("audio"):
                self.attach_song(where, e, anchor, a.get("audio"), a.get("audio_title"))

    def attach_song(self, where, e, anchor, audio, title):
        """A codex entry's song: registered as an asset, its cues (the lines its codex.md entry quotes in italics, four
        words or more) taken for the story, and its embedded lyrics, if any, held to what the page has already sung."""
        src = (ART / str(audio)).resolve()
        if ART.resolve() not in src.parents:
            problem(f"{where}.audio '{audio}' must be a path under saga/art/")
            return
        if src.suffix.lower() not in AUDIO_TYPES:
            problem(f"{where}.audio '{audio}' must be one of {', '.join(sorted(AUDIO_TYPES))}")
            return
        if not src.is_file():
            problem(f"{where}.audio '{audio}' does not exist under saga/art/")
            return
        if src.stat().st_size > AUDIO_MAX_BYTES:
            problem(f"{where}.audio '{audio}' is over {AUDIO_MAX_BYTES // (1024 * 1024)} MB; shrink it before publishing")
        if title is not None and not str(title).strip():
            problem(f"{where}.audio_title is empty (leave it out to use the entry's name)")
        path = f"art/{src.relative_to(ART.resolve()).as_posix()}"
        self.assets[path] = src
        cues = []
        for seg in re.findall(r"(?<!\*)\*(?!\*)([^*]+)\*", e["text"]):
            cues += [w for w in (words_of(x) for x in seg.split(" / ")) if len(w.split()) >= 4]
        if not cues:
            note(f"{where}: its codex.md entry quotes no lines in italics, so the story offers the song only where its name is linked")
        lyrics = mp3_lyrics(src) if src.suffix.lower() == ".mp3" else None
        if lyrics is None:
            note(f"{where}: the audio carries no lyrics the build can read; make sure it sings only what the page has sung")
        else:
            page = f' {words_of(chr(10).join(read(p) for p in sorted(CHRON.glob("*.md"))))} '
            for ln in lyrics:
                if words_of(ln) and f" {words_of(ln)} " not in page:
                    problem(f"{where}.audio sings a line the page has not: {ln[:60]!r} (a song may carry only what the "
                            f"chronicle has already sung; the rest stays in the Annals)")
        self.songs[anchor] = {"path": path, "title": str(title or e["name"]).strip(), "cues": cues}
        e["_song"] = self.songs[anchor]

    def char_portrait(self, c):
        got = self.register_image(f"saga/characters/{c['id']}.json: portrait", c["portrait"], c.get("portrait_alt"))
        if got:
            c["_portrait_path"], c["_portrait_size"], c["_portrait_sm"], c["_portrait_md"] = got
            c["_portrait_focus"] = self.focus_style(f"saga/characters/{c['id']}.json: portrait_focus", c.get("portrait_focus"), "50% 30%")

    def portrait_figure(self, c, rel, overlay=""):
        """A character's portrait at the head of their page: a square frame, cropped to fit, tap or click to see it whole.
        overlay (the level crest) sits on the frame's corner and lets taps through to the picture."""
        if not c.get("_portrait_path"):
            return ""
        href = rel + c["_portrait_path"]
        wh = c.get("_portrait_size")
        dims = f' width="{wh[0]}" height="{wh[1]}"' if wh else ""
        alt = esc(c.get("portrait_alt", ""))
        return (f'<figure class="portrait"><a href="{href}" data-zoom aria-label="Enlarge: {alt}">'
                f'<img src="{rel}{c["_portrait_md"]}" alt="{alt}"{dims}{c.get("_portrait_focus", "")} decoding="async"></a>{overlay}</figure>')

    def avatar(self, c, rel, size, cls=""):
        """A round portrait in place of a sigil (roster cards, the Now page); empty when the character has none."""
        if not c or not c.get("_portrait_path"):
            return ""
        return (f'<img class="avatar{(" " + cls) if cls else ""}" src="{rel}{c["_portrait_sm"]}" alt="" '
                f'width="{size}" height="{size}"{c.get("_portrait_focus", "")} decoding="async">')

    def codex_figure(self, p, rel):
        """The place's picture: shown full width, tap or click to see it whole (a plain link without JavaScript). The full
        file, lazy: it sits in a closed Codex entry, so the browser fetches it only when the entry is opened."""
        if not p.get("_image_path"):
            return ""
        href = rel + p["_image_path"]
        wh = p.get("_image_size")
        dims = f' width="{wh[0]}" height="{wh[1]}"' if wh else ""
        cap = p.get("image_caption") or ""
        alt = esc(p.get("image_alt", ""))
        return (f'<figure class="codex-art"><a href="{href}" data-zoom aria-label="Enlarge: {alt}">'
                f'<img src="{href}" alt="{alt}"{dims}{p.get("_image_focus", "")} loading="lazy" decoding="async"></a>'
                f'<figcaption>{esc(cap)}{" · " if cap else ""}<span class="zoom-hint"><span class="t">Tap</span><span class="c">Click</span> to enlarge</span></figcaption></figure>')

    def codex_thumb(self, p, rel):
        song = '<span class="song-tag" title="A song">♪</span>' if p.get("_song") else ""
        if not p.get("_image_path"):
            return song
        return song + f'<img class="thumb" src="{rel}{p["_image_sm"]}" alt=""{p.get("_image_focus", "")} decoding="async">'

    def codex_song(self, e, rel):
        """A codex entry's song: the browser's own player (works without JavaScript)."""
        s = e.get("_song")
        if not s:
            return ""
        href = rel + s["path"]
        return (f'<figure class="codex-song"><figcaption>♪ {esc(s["title"])}</figcaption>'
                f'<audio controls preload="metadata" src="{href}"><a href="{href}">Listen</a></audio></figure>')

    def song_button(self, s, rel, compact=False):
        """The small play button in the story: a link to the song that site.js plays in place (without it, the link
        opens the file). compact: an icon only, after a linked name; otherwise an icon and the song's title."""
        t = esc(s["title"])
        label = "" if compact else f'<span class="sg-t">{t}</span>'
        return (f'<a class="song{" compact" if compact else ""}" href="{rel}{s["path"]}" data-song="{t}" aria-label="Play {t}" title="Play {t}">'
                f'<svg class="sg-i" viewBox="0 0 16 16" aria-hidden="true"><path class="sg-play" d="M4 2.2v11.6L13.4 8z"/>'
                f'<path class="sg-pause" d="M3.5 2.5h3v11h-3zm6 0h3v11h-3z"/></svg>{label}</a>')

    def song_cues(self, md, seen, rel):
        """Play buttons for the songs whose lines this block sings and that have no button yet in this scene."""
        if not self.songs:
            return ""
        w = f" {words_of(md)} "
        out = []
        for anchor, s in self.songs.items():
            key = "song:t:" + anchor
            if key not in seen and any(f" {c} " in w for c in s["cues"]):
                seen.add(key)
                out.append(self.song_button(s, rel))
        return " ".join(out)

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
        projects = w.get("projects")
        if projects is None:
            projects = []
        if not isinstance(projects, list):
            problem("world.json: projects must be a list")
            projects = []
        for i, pr in enumerate(projects):
            if not isinstance(pr, dict):
                problem(f"world.json projects[{i}] must be an object")
                continue
            for k in ("id", "name", "place", "visible"):
                if not str(pr.get(k) or "").strip():
                    problem(f"world.json projects[{i}]: missing {k}")
            if pr.get("place") not in self.place_by_id:
                problem(f"world.json projects[{i}]: place {pr.get('place')!r} is not in places.json")
            if not isinstance(pr.get("stage"), int) or not isinstance(pr.get("of"), int) or not 1 <= pr["stage"] <= pr["of"]:
                problem(f"world.json projects[{i}]: stage must be an int from 1 to of")
            if pr.get("status") not in ("live", "done"):
                problem(f"world.json projects[{i}]: status must be live or done")
            for d in pr.get("decisions") or []:
                if not isinstance(d, dict) or not str(d.get("chose") or "").strip() or not isinstance(d.get("stage"), int):
                    problem(f"world.json projects[{i}]: each decision needs stage (int) and chose (text)")
        self.projects = projects
        keeps = w.get("keepsakes")
        if keeps is None:
            keeps = []
        if not isinstance(keeps, list):
            problem("world.json: keepsakes must be a list")
            keeps = []
        for i, kp in enumerate(keeps):
            if not isinstance(kp, dict):
                problem(f"world.json keepsakes[{i}] must be an object")
                continue
            for k in ("name", "text", "to", "tale", "piece"):
                if not str(kp.get(k) or "").strip():
                    problem(f"world.json keepsakes[{i}]: missing {k}")
            if (str(kp.get("tale")), str(kp.get("piece"))) not in self.registry:
                problem(f"world.json keepsakes[{i}]: {kp.get('tale')} {kp.get('piece')} is not a piece of a tale on the page")
            if kp.get("mark") and kp["mark"] not in SHELF_MARKS:
                problem(f"world.json keepsakes[{i}]: mark {kp.get('mark')!r} is not one the shelf can draw ({', '.join(sorted(SHELF_MARKS))})")
        self.keepsakes = keeps
        tales = w.get("tales")
        if tales is None:
            tales = []
        if not isinstance(tales, list):
            problem("world.json: tales must be a list")
            tales = []
        for i, t in enumerate(tales):
            if not isinstance(t, dict) or not str(t.get("id") or "").strip():
                problem(f"world.json tales[{i}] must be an object with an id")
                continue
            if t["id"] not in self.tale_by_code:
                problem(f"world.json tales[{i}]: {t['id']} has no file under saga/chronicle/tales/")
            if not isinstance(t.get("pieces"), int) or not isinstance(t.get("told"), int):
                problem(f"world.json tales[{i}]: pieces and told are counts")
        self.tale_state = {t["id"]: t for t in tales if isinstance(t, dict) and t.get("id")}
        for t in self.tales:
            if t["code"] not in self.tale_state:
                problem(f"tales/{t['file']}: not in world.json → tales[] (bind it: `saga.py tale bind`, or `saga.py project`)")
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

    def codex_things(self):
        """codex.md entries the Codex renders outside Sayings, each with its anchor id, in order: [(section, bucket, entry, id)].
        Under Things and Beasts, an entry named for a place or a character is skipped (it has its own entry or page)."""
        place_names = {p["name"].lower() for p in self.places}
        char_names = {c["name"].lower() for c in self.chars.values()} | {a.lower() for c in self.chars.values() for a in c.get("aliases") or []}
        out = []
        for key, entries in self.codex.items():
            if key == "Sayings":
                continue
            bucket = "things" if key in ("Places and things", "Things") else "beasts" if key in ("People", "Beasts") else key
            for e in entries:
                nm = e["name"].lower()
                if bucket in ("things", "beasts") and (nm in place_names or nm in char_names or nm.replace("the ", "") in char_names):
                    continue
                out.append((key, bucket, e, f"codex-{slug(e['name'])}"))
        return out

    def build_linkers(self):
        """Every name the Chronicle links, longest first: a character (to their page), a place or faction on the page, or a
        codex thing (to its Codex entry). Each target carries a preview: its picture if it has one, a title, one line."""
        pats = []
        self.link_targets = {}

        def article_variants(nm):
            v = {nm}
            if nm.startswith("The "):
                v.add("the " + nm[4:])
            elif nm.startswith("the "):
                v.add("The " + nm[4:])
            return v

        def focus_of(style):
            m = re.search(r"object-position:([^\"]+)", style or "")
            return m.group(1) if m else ""

        for cid, c in self.chars.items():
            name_tokens = {t.lower().strip("'") for t in re.split(r"[\s-]+", c["name"]) if len(t) > 2 and t.lower() not in ("ser", "the", "of")}
            names = [c["name"]]
            if c["name"].startswith("Ser "):
                names.append(c["name"][4:])
            for a in c.get("aliases") or []:
                toks = {t.lower() for t in re.split(r"[\s-]+", a)}
                if toks & name_tokens:
                    names.append(a)
            key = "c:" + cid
            self.link_targets[key] = {"href": self.char_href(cid), "t": c["name"], "s": c.get("epithet", ""), "x": "",
                                      "i": c.get("_portrait_sm"), "k": "face", "f": focus_of(c.get("_portrait_focus"))}
            for nm in names:
                variants = {nm}
                if nm.lower().startswith("the "):
                    variants.add("The " + nm[4:])
                    variants.add("the " + nm[4:])
                for v in variants:
                    pats.append((v, key))
        for p in self.places:
            if not p.get("on_page"):
                continue
            key = "p:" + p["id"]
            self.link_targets[key] = {"href": f"codex/index.html#place-{p['id']}", "t": p["name"], "s": p.get("subtitle") or "A place",
                                      "x": excerpt(p.get("description")), "i": p.get("_image_md"), "k": "wide", "f": focus_of(p.get("_image_focus"))}
            for nm in [p["name"], p.get("label")] + list(p.get("aliases") or []):
                for v in article_variants(nm or ""):
                    if v:
                        pats.append((v, key))
        for f in self.factions.values():
            if not f.get("on_page"):
                continue
            key = "f:" + f["id"]
            self.link_targets[key] = {"href": f"codex/index.html#faction-{f['id']}", "t": f["name"], "s": "A faction",
                                      "x": excerpt(f.get("description")), "i": f.get("_image_md"), "k": "wide", "f": focus_of(f.get("_image_focus"))}
            for nm in [f["name"]] + list(f.get("aliases") or []):
                for v in article_variants(nm or ""):
                    if v:
                        pats.append((v, key))
        for _sec, _bucket, e, anchor in self.codex_things():
            key = "t:" + anchor
            nm = e["name"]
            self.link_targets[key] = {"href": f"codex/index.html#{anchor}", "t": nm, "s": "From the Codex", "x": excerpt(e["text"]),
                                      "i": e.get("_image_md"), "k": "wide", "f": focus_of(e.get("_image_focus"))}
            names = set(article_variants(nm))
            rest = nm[4:] if nm.startswith("The ") else ""
            if rest and (len(rest.split()) >= 2 or rest[:1].isupper()):
                names.add(rest)  # "two fires", "Emberwardens"; never a bare common word like "writ"
            if "-" in nm.split()[0] or (len(nm.split()) >= 2 and nm.split()[1][:1].islower() and not nm.startswith("The ")):
                names.add(nm[:1].lower() + nm[1:])  # "field-stones"
            for n in list(names):
                last = n.split()[-1]
                if last.endswith("s") and not last.endswith(("'s", "ss")) and len(last) > 3:
                    names.add(n[:-1])  # "field-stone", "Emberwarden"
            for v in names:
                pats.append((v, key))
        pats.sort(key=lambda t: -len(t[0]))  # stable: for the same words, a character beats a place beats a faction beats a thing
        self.alias_to_id = {}
        for ptn, key in pats:
            self.alias_to_id.setdefault(esc(ptn), key)
        if self.alias_to_id:
            alts = sorted(self.alias_to_id, key=len, reverse=True)
            self.name_re = re.compile(r"(?<![\w-])(" + "|".join(re.escape(a) for a in alts) + r")(?![\w-])")
        else:
            self.name_re = None
        return pats

    def link_html(self, key, text, rel):
        """A linked name with its preview card's data (shown on hover, or on a first tap on touch screens)."""
        t = self.link_targets[key]
        attrs = f' data-pv-t="{esc(t["t"])}"'
        if t.get("s"):
            attrs += f' data-pv-s="{esc(t["s"])}"'
        if t.get("x"):
            attrs += f' data-pv-x="{esc(t["x"])}"'
        if t.get("i"):
            attrs += f' data-pv-i="{rel}{t["i"]}" data-pv-k="{t["k"]}"' + (f' data-pv-f="{esc(t["f"])}"' if t.get("f") else "")
        return f'<a class="nm" href="{rel}{t["href"]}"{attrs}>{text}</a>'

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
                key = self.alias_to_id.get(m.group(1))
                if not key or key == exclude or key in seen:
                    return m.group(1)
                seen.add(key)
                song = self.songs.get(key[2:]) if key.startswith("t:") else None
                if song and "song:" + key not in seen:
                    seen.add("song:" + key)
                    return self.link_html(key, m.group(1), rel) + self.song_button(song, rel, compact=True)
                return self.link_html(key, m.group(1), rel)
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
                cue = self.song_cues(b[1], seen, rel)
                out.append(f"<p>{self.link_names(inline(b[1]), seen, rel)}{' ' + cue if cue else ''}</p>")
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
                cue = self.song_cues(" ".join(b[1]), seen, rel)
                lines = "".join(f"<p>{self.link_names(inline(x), seen, rel)}</p>" for x in b[1] if x)
                if cue:
                    lines += f'<p class="song-cue">{cue}</p>'
                out.append(f"<blockquote>{lines}</blockquote>")
            elif kind == "dice":
                # consecutive dice lines are one check: a cast, an Inspiration line, the cast again (style.md §3)
                if b[1].strip().upper() == "INSPIRATION":
                    row = f'<div class="dice-row insp"><span class="insp-glyph" aria-hidden="true">✦</span><span class="dice-tag">Inspiration</span> <span class="dice-body">{inline(b[2])}</span></div>'
                else:
                    m_nat = re.search(r"d20\s+\*{0,2}(\d+)(?:/(\d+))?", b[2])
                    m_res = re.search(r"\*?(Success|Failure|Partial[^*—]*)\*?", b[2])
                    die = d20_glyph(m_nat.group(1), m_res.group(1) if m_res else "") if m_nat else ""
                    row = f'<div class="dice-row">{die}<span class="dice-tag">{esc(b[1])}</span> <span class="dice-body">{inline(b[2])}</span></div>'
                if out and out[-1].startswith('<div class="dice">') and out[-1].endswith("</div></div>"):
                    prev = out.pop()[:-len("</div>")]
                    if "dice-row insp" in row:  # the cast before an Inspiration line is the one it replaces
                        k = prev.rfind('<div class="dice-row">')
                        if k >= 0:
                            prev = prev[:k] + '<div class="dice-row superseded">' + prev[k + len('<div class="dice-row">'):]
                    out.append(prev + row + "</div>")
                else:
                    out.append(f'<div class="dice">{row}</div>')
            elif kind == "choice-h":
                out.append(f'<h3 class="choice-h">{esc(b[1])}</h3>')
            elif kind == "ol":
                items, is_choice = b[1], b[2]
                out.append(self.choice_list(items, self.choice_for(ch, scene["key"]) if is_choice else None, bool(is_choice)))
            elif kind == "ul":
                out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in b[1]) + "</ul>")
        return "".join(out)

    @staticmethod
    def choice_list(items, rec=None, is_choice=True):
        """A numbered list. For a choice with a recorded answer (rec): the option taken marked 'chosen' (and 'answered for
        himself' when the Bearing answered), or, when he took none of them, his own answer after the list."""
        taken = as_int(rec.get("option")) if rec else None
        free = (rec.get("text") or "").strip() if rec and taken is None else ""
        mark = ' <span class="state good">chosen</span>' + (' <span class="state dim">answered for himself</span>' if rec and rec.get("by") == "bearing" else "")
        lis = []
        for i, it in enumerate(items, 1):
            cls = ' class="taken"' if taken == i else ""
            lis.append(f"<li{cls}>{inline(it)}{mark if taken == i else ''}</li>")
        out = f'<ol class="{"choice" if is_choice else ""}">{"".join(lis)}</ol>'
        return out + (f'<p class="chosen-free">{mark.strip()} {esc(free)}</p>' if free else "")

    def render_chapter(self, idx):
        ch = self.chapters[idx]
        rel = "../"
        prev_ch = self.chapters[idx - 1] if idx > 0 else None
        next_ch = self.chapters[idx + 1] if idx + 1 < len(self.chapters) else None
        head = []
        if ch["book"]:
            head.append(f'<p class="book-line">{esc(ch["book"])}</p>')
        head.append(f'<h1 class="ch-title"><span class="lbl">{esc(ch["label"])}</span>{esc(ch["title"])}</h1>')
        tier_row = next((r for r in self.chapters_csv if str(r.get("chapter")) == str(ch["number"])), None) if ch["number"] else None
        if tier_row and tier_row.get("tier") in TIER_SEAL:
            head.append(f'<div class="seal-row">{svg_seal(tier_row["tier"], 44)}<span class="lbl">{esc(TIER_DONE.get(tier_row["tier"], tier_row["tier"]))}</span></div>')
        recap = (self.world.get("recaps") or {}).get(ch["slug"])
        if recap:  # the reader's reminder, under the title and before the chapter's own first words
            head.append(f'<aside class="previously"><span class="lbl">Previously</span><p>{esc(recap)}</p></aside>')
        if ch["epigraph"]:
            lines = "".join(f"<p>{inline(x)}</p>" for x in ch["epigraph"]["lines"])
            cue = self.song_cues(" ".join(ch["epigraph"]["lines"]), set(), rel)
            src = f'— {inline(ch["epigraph"]["source"])}' if ch["epigraph"]["source"] else ""
            src = f'<figcaption>{src}{" " if src and cue else ""}{cue}</figcaption>' if src or cue else ""
            head.append(f'<figure class="epigraph"><blockquote>{lines}</blockquote>{src}</figure>')
        body = []
        for s in ch["scenes"]:
            seen = set()
            lab = f'<span class="scene-n">{esc(s["label"])}</span>' if s["label"] else ""
            title = esc(s["title"]) if s["title"] else ""
            cls = "scene between" if s.get("between") else "scene"
            body.append(f'<section class="{cls}" id="{s["anchor"]}"><h2 class="scene-h">{lab}{title}</h2>{self.render_blocks(ch, s, rel, seen)}</section>')
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

    @property
    def current_chapter(self):
        """world.json's current chapter (check_world has already failed a chapter_file the chronicle lacks)."""
        slug = str(self.world.get("chapter_file") or "").split("/")[-1].replace(".md", "")
        return next((c for c in self.chapters if c["slug"] == slug), None)

    def latest_pieces(self):
        """(chapter, latest scene, the Betweens after it): the newest scene of the current chapter that is not a Between,
        then the Betweens that follow it. A chapter whose first pieces are Betweens, before its first scene: (chapter,
        None, those Betweens)."""
        ch = self.current_chapter
        if not ch or not ch["scenes"]:
            return ch, None, []
        latest = next((s for s in reversed(ch["scenes"]) if not s.get("between")), None)
        if latest:
            return ch, latest, [s for s in ch["scenes"][ch["scenes"].index(latest) + 1:] if s.get("between")]
        return ch, None, [s for s in ch["scenes"] if s.get("between")]

    def continue_button(self, rel):
        """Continue reading: the newest piece on the page (the current chapter's latest scene or the Between after it; the
        end of the chapter before while the new one waits for its first scene)."""
        ch, latest, after = self.latest_pieces()
        target = after[-1] if after else latest
        if target is None:
            done = [c for c in self.chapters if c["scenes"] and (ch is None or c["number"] < ch["number"])]
            if not done:
                return ""
            ch, target = done[-1], done[-1]["scenes"][-1]
        what = ch["label"] + " · " + (target["label"] + " — " if target["label"] else "") + target["title"]
        href = f'{rel}chronicle/{ch["slug"]}.html#{target["anchor"]}'
        return (f'<div class="btn-row"><a class="btn" href="{href}">Continue reading</a>'
                f'<a class="btn-note" href="{href}">{esc(what)}</a></div>')

    def render_chronicle_index(self):
        rel = "../"
        cur_slug = (self.current_chapter or {}).get("slug")
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
            n_bt = sum(1 for s in ch["scenes"] if s.get("between"))
            n_sc = len(ch["scenes"]) - n_bt
            count = "no scene yet" if ch["empty"] else (f'{n_sc} scene{"s" if n_sc != 1 else ""}' + (f' · {n_bt} between' if n_bt else "") + f' · about {ch["words"]:,} words')
            tier_row = next((r for r in self.chapters_csv if str(r.get("chapter")) == str(ch["number"])), None) if ch["number"] else None
            seal = (svg_seal(tier_row["tier"], 22) + " ") if tier_row and tier_row.get("tier") in TIER_SEAL else ""
            items.append(f'<li class="{"now" if now else ""}"><a class="ch-link" href="{rel}chronicle/{ch["slug"]}.html"><b>{esc(ch["label"])} — {esc(ch["title"])}</b></a>'
                         f'<span class="m num">{seal}{count}{" · now" if now else ""}</span>'
                         f'<ul class="scenes">{scenes}</ul></li>')
        first = self.chapters[0] if self.chapters else None
        start = (f'<p class="m">Or <a href="{rel}chronicle/{first["slug"]}.html">start from the beginning</a>: '
                 f'{esc(first["label"] + " — " + first["title"])}.</p>') if first else ""
        body = (f'<section class="plate"><p class="lbl">The Chronicle</p><h1>Books, chapters and scenes</h1>'
                f'<p class="dim">Read in order. The current chapter is marked in brass.</p>{self.continue_button(rel)}{start}</section>')
        n_num = sum(1 for c in self.chapters if c["number"])
        n_pro = len(self.chapters) - n_num
        count = (("a prologue and " if n_pro else "") + f"{n_num} chapter{'s' if n_num != 1 else ''}") if n_num else "a prologue"
        body += sec("Timeline", count, f'<ul class="chron">{"".join(items)}</ul>')
        self.pages["chronicle/index.html"] = shell("Chronicle", body, rel, "Chronicle", desc="The Unkneeling, by book, chapter and scene.")

    # ---------------------------------------------------------------- reckoning blocks
    def reckoning_of(self, c, rel):
        """The Reckoning as Darrow reads it, gated by his Warden's Eye rank (the section's heading names it; the card does not again)."""
        rk = c.get("reckoning")
        eye = self.eye
        if c.get("tier") == "fallen":
            return '<div class="rk-card sealed-box"><p class="sealed-line">The script does not read those who did not come back.</p></div>'
        if rk is None or rk.get("unread"):  # unread: the page has not yet let the script read this person
            return '<div class="rk-card sealed-box"><p class="sealed-line">⟦ unread ⟧</p></div>'
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
        return f'<div class="rk-card">{"".join(rows)}{note_}</div>'

    # ---------------------------------------------------------------- characters
    @staticmethod
    def mention_only(c):
        """Only ever named on the page, never present in a scene."""
        apps = c.get("appearances") or []
        return bool(apps) and all(a.get("mention") for a in apps)

    def faction_link(self, fid, rel):
        """A faction's name, linked to its Codex entry once the page has shown it."""
        f = self.factions.get(fid, {})
        name = esc(f.get("name", fid))
        return f'<a class="fac-name" href="{rel}codex/index.html#faction-{esc(fid)}">{name}</a>' if f.get("on_page") else f'<span class="fac-name">{name}</span>'

    def identity_plate(self, c, rel, level):
        """Portrait (or crest), name, epithet; chips only for what the rest of the plate does not say: the status when it is
        not 'alive' (alive is the default and goes unsaid), and Darrow's names. The faction is said once, under its shield."""
        sg = c.get("sigil") or {}
        chips = []
        if c["id"] == "darrow":
            chips.append(chip("the Faithless"))
            ep = (self.bearing or {}).get("epithet")
            if ep:
                chips.append(chip(ep, "ember"))
        if c["status"] != "alive":
            chips.append(badge(c["status"], STATUS_CLS.get(c["status"], "dim")))
        fac = self.factions.get(sg.get("faction"), {})
        if c["tier"] == "fallen":
            cr = sigil(fac, sg.get("mark"), 86, "big", c["name"])
            row = f'<div class="sigil-row"><span class="sealed-line">in memory</span>{self.faction_link(c["faction"], rel)}</div>'
        else:
            cr = crest(level if level is not None else "?")
            row = f'<div class="sigil-row">{sigil(fac, sg.get("mark"), 44)}{self.faction_link(c["faction"], rel)}</div>'
        who = (f'<div class="who"><h1>{esc(c["name"])}</h1><p class="sub">{esc(c.get("epithet", ""))}</p>'
               + (f'<div class="chips">{"".join(chips)}</div>' if chips else "") + '</div>')
        fig = self.portrait_figure(c, rel, "" if c["tier"] == "fallen" else cr)
        hero = f'<div class="hero with-portrait">{fig}{who}</div>' if fig else f'<div class="hero">{cr}{who}</div>'
        return f'<section class="plate">{hero}{row}<p class="fine">{FINE_PRINT}</p></section>'

    def shelf_html(self, c, rel):
        """A character's keepsakes as a shelf: a slot per keepsake with its mark, a dashed slot per tale of theirs still being told,
        and blank slots to fill the row, so the next one is in view before it is earned. Returns (html, kept, pending)."""
        kept = [kp for kp in getattr(self, "keepsakes", []) or [] if kp.get("to") == c["id"]]
        done_tales = {kp.get("tale") for kp in kept}
        pending = []
        for t in self.tales:
            stt = self.tale_state.get(t["code"]) or {}
            if stt.get("of") == c["id"] and t["code"] not in done_tales and not stt.get("done") and not stt.get("rests"):
                pending.append(t)  # a tale still being told; one that rests (told in part) leaves nothing to wait for
        slots = []
        for kp in kept:
            src = self.scene_ref({"chapter": kp["tale"], "scene": kp["piece"]}, rel)
            slots.append(f'<li class="slot kept">{shelf_mark(kp.get("mark") or "star")}'
                         f'<b>{esc(kp["name"])}</b><p class="m">{esc(kp["text"])}</p><span class="src">{src}</span></li>')
        for t in pending:
            stt = self.tale_state.get(t["code"]) or {}
            slots.append(f'<li class="slot pending">{shelf_unknown()}<span class="lbl">{esc(t["label"])}</span>'
                         f'<b><a href="{rel}tales/{t["slug"]}.html">{esc(t["title"])}</a></b>'
                         f'{told_marks(stt.get("told", 0), stt.get("pieces") or 1)}<p class="m">kept when it is told in full</p></li>')
        n = len(slots)
        width = max(4, -(-n // 4) * 4)
        phone_row = max(2, -(-n // 2) * 2)  # on a phone the shelf is two wide: blanks past the first row it needs are hidden there
        slots += [f'<li class="slot blank{" wide" if i >= phone_row else ""}" aria-hidden="true"></li>' for i in range(n, width)]
        html = f'<ul class="shelf">{"".join(slots)}</ul><div class="shelf-ledge" aria-hidden="true"></div>'
        if not kept:
            html += '<p class="hint shelf-note">Nothing kept yet. When a tale is told in full, what it leaves is set here.</p>'
        return html, len(kept), len(pending)

    def appearances_html(self, c, rel):
        """(label, html): the scenes a character is in, grouped under their chapter; a scene they are only named in is marked."""
        groups, n_present, n_named = {}, 0, 0
        for a in c.get("appearances") or []:
            r = self.registry.get((str(a.get("chapter")), str(a.get("scene"))))
            if not r:
                continue
            named = bool(a.get("mention"))
            n_named += named
            n_present += not named
            ch, s = r["chapter"], r["scene"]
            tag = ' <span class="state dim">named</span>' if named else ""
            groups.setdefault(ch["code"], (ch, []))[1].append(
                f'<li class="{"named" if named else ""}"><a href="{rel}{r["href"]}">{esc((s["label"] + " — " if s["label"] else "") + s["title"])}</a>{tag}</li>')
        items = "".join(f'<li><a class="ch-link" href="{rel}{self.page_dir(ch)}{ch["slug"]}.html"><b>{esc(ch["label"])} — {esc(ch["title"])}</b></a>'
                        f'<ul class="scenes">{"".join(rows)}</ul></li>' for ch, rows in groups.values())
        label = f"{n_present} scene{'s' if n_present != 1 else ''}" + (f" · named in {n_named}" if n_named else "")
        return label, f'<ul class="chron">{items}</ul>'

    def character_sections(self, c, rel):
        """The sections of a character's page, in order, as dicts: title, label (the section head's right-hand note; most
        have none, the plate's one line of fine print covers them), meta (the closed row of a panel on Darrow's page),
        html, and panel_html where a panel shows it differently."""
        out = []
        minor = c.get("tier") == "minor"
        out.append(dict(key="appearance", title="Appearance", html=f'<p class="prose">{esc(c["appearance"])}</p>'))
        ls = c.get("last_seen") or {}
        pl = self.place_by_id.get(ls.get("place"), {})
        ref = self.scene_ref(ls, rel)
        where = f' · {esc(pl["name"])}' if pl and pl["name"].lower() not in re.sub(r"<[^>]+>", "", ref).lower() else ""
        r = self.registry.get((str(ls.get("chapter")), str(ls.get("scene"))))
        short = (r["chapter"]["label"] + (" · " + r["scene"]["label"] if r["scene"]["label"] else "")) if r else ""
        seen = f'<p class="seen"><span class="lbl">{"Named in" if self.mention_only(c) else "Last seen"}</span> {ref}{where}</p>'
        out.append(dict(key="now", title="Now", meta=esc(short), html=seen + f'<p class="prose">{esc(c["now"])}</p>'))
        out.append(dict(key="story", title="Story so far", html=f'<p class="prose">{esc(c["story_so_far"])}</p>'))
        q = c.get("quote")
        if q and q.get("text"):
            out.append(dict(key="quote", title="Quote", html=f'<figure class="quote"><blockquote><p>{esc(q["text"])}</p></blockquote><figcaption>{self.scene_ref(q, rel)}</figcaption></figure>'))
        elif not minor:
            out.append(dict(key="quote", title="Quote", html='<p class="empty">No line of theirs is on the page yet.</p>'))
        rels = []
        comp = (self.world.get("companions") or {}).get(c["id"].split("-")[0]) if c["id"] != "darrow" else None
        if comp and "approval" in comp:
            a = int(comp["approval"])
            rels.append(f'<li class="rel regard"><div class="rel-top"><b>Toward Darrow</b><span class="lbl">{mood_mark(approval_word(a))}{esc(approval_word(a))}</span></div>'
                        f'{bar(a + 100, 200, "Regard for Darrow", "approval", text=approval_word(a), quiet=True)}</li>')
        for rr in c.get("relationships") or []:
            to = rr.get("to", "")
            who = f'<a href="{rel}{self.char_href(to)}">{esc(self.chars[to]["name"])}</a>' if to in self.chars else esc(to)
            rels.append(f'<li class="rel"><b>{who}</b><span class="lbl">{esc(rr.get("label", ""))}</span><p class="dim">{esc(rr.get("note", ""))}</p></li>')
        n_rel = len(c.get("relationships") or [])
        if rels or not minor:
            out.append(dict(key="relationships", title="Relationships", meta=str(n_rel) if n_rel else "",
                            html=f'<ul class="rels">{"".join(rels)}</ul>' if rels else '<p class="empty">None on the page yet.</p>'))
        if c["id"] != "darrow":
            out.append(dict(key="reckoning", title="The Reckoning", html=self.reckoning_of(c, rel)))
        facts = c.get("known_facts") or []
        fl = '<ul class="facts">' + "".join(f'<li><span>{esc(f["fact"])}</span><span class="src">{self.scene_ref(f, rel)}</span></li>' for f in facts) + "</ul>"
        out.append(dict(key="facts", title="Known facts", meta=str(len(facts)),
                        html=details(f"What the page has shown ({len(facts)})", fl) if facts else '<p class="empty">Nothing yet.</p>',
                        panel_html=fl if facts else '<p class="empty">Nothing yet.</p>'))
        shelf, n_kept, n_pending = self.shelf_html(c, rel)
        if n_kept or n_pending or c["id"] == "darrow":
            meta = (f"{n_kept} kept" if n_kept else "nothing yet") + (f" · {n_pending} to come" if n_pending else "")
            out.append(dict(key="keepsakes", title="What he keeps" if c["id"] == "darrow" else "Keepsakes", meta=meta, html=shelf))
        label, apps = self.appearances_html(c, rel)
        out.append(dict(key="appearances", title="Appearances", label=label, meta=esc(label), html=apps))
        return out

    def render_character(self, c):
        rel = "../"
        rk = c.get("reckoning")
        level = None
        if c["tier"] != "fallen" and isinstance(rk, dict) and not rk.get("unread") and self.eye >= 1:
            level = rk["level"] if rk.get("level") is not None else "—"
        body = self.identity_plate(c, rel, level) + "".join(sec(x["title"], x.get("label", ""), x["html"]) for x in self.character_sections(c, rel))
        ep = c.get("epithet", "")
        ep = ep[0].lower() + ep[1:] if ep[:2] in ("A ", "An", "Th") else ep
        self.pages[f"characters/{c['id']}.html"] = shell(c["name"], body, rel, "Characters", "char-page",
                                                        desc=f"{c['name']}, as the Chronicle has shown: {ep}.")

    def card(self, c, rel):
        """A roster card: the status only when it is not 'alive', the faction only when the epithet does not already name it."""
        f = self.factions.get(c["faction"], {})
        sg = c.get("sigil") or {}
        ls = c.get("last_seen") or {}
        r = self.registry.get((str(ls.get("chapter")), str(ls.get("scene"))))
        last = esc(r["label"]) if r else ""
        seen_lbl = "Named in" if self.mention_only(c) else "Last seen"
        fname = f.get("name", "")
        named = re.sub(r"^the\s+", "", fname.lower()) in c.get("epithet", "").lower()
        chips = (badge(c["status"], STATUS_CLS.get(c["status"], "dim")) if c["status"] != "alive" else "") + ("" if named or not fname else chip(fname))
        return (f'<a class="card" href="{rel}{self.char_href(c["id"])}" data-faction="{esc(c["faction"])}" data-status="{esc(c["status"])}">'
                f'{self.avatar(c, rel, 56) or sigil(self.factions.get(sg.get("faction"), {}), sg.get("mark"), 56)}<div class="card-body"><b>{esc(c["name"])}</b><span class="dim">{esc(c.get("epithet", ""))}</span>'
                + (f'<div class="chips">{chips}</div>' if chips else "") +
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
        """The Reckoning at the head of Darrow's page: level, XP, Ember, Inspiration and the four attributes, always open."""
        d, rules = self.darrow, self.rules
        a = d["attributes"]
        xp_into = d["xp"] - d["xp_this_level"]
        xp_span = d["xp_next_level"] - d["xp_this_level"]
        xp_show = f"{xp_into:,} / {xp_span:,}"
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
        inner = (f'<p class="reck-line"><b>Level {d["level"]}</b> · {esc(d["rank"])} · <span class="num">XP {d["xp"]:,}</span></p>'
                 f'<div class="chips">{chip("HP " + str(d["hp_max"]))}{chip("Proficiency +" + str(d["proficiency"]))}{self.tether_chip()}{self.works_chip()}</div>'
                 f'{bar(xp_into, xp_span, "XP toward Level " + str(d["level"] + 1), "", xp_show)}'
                 f'<div class="row2"><div>{bar(d["ember"]["value"] or 0, 100, "Ember · " + str(d["ember"]["tier"] or "unlit"), "ember", d["ember"]["value"])}</div>'
                 f'<div class="insp"><span class="lbl">Inspiration</span>{pips(d["inspiration"], d["inspiration_cap"])}</div></div>'
                 f'<div class="streaks">{"".join(tiles)}</div>')
        return sec("The Reckoning", "", f'<div class="reck">{inner}</div>', cls="reck-sec", hid="reckoning")

    def darrow_panels(self, rel):
        """Darrow's sheet below the Reckoning, each section folded shut with a line of what it holds: (meta, title, html, id)."""
        d, rules = self.darrow, self.rules
        trees = defaultdict(list)
        for art in d["arts"]:
            trees[art["tree"]].append(art)
        order = ["Blade", "Footing", "Breath", "Binding", "Insight", "Sport"]
        thresholds = list(rules.get("art_ranks") or [1, 6, 15, 30, 50])
        n_pips = len(thresholds)
        tree_html, n_learned, n_sealed = [], 0, 0
        for tree in [x for x in order if x in trees] + sorted(x for x in trees if x not in order):
            rows = []
            for art in trees[tree]:
                sealed = art.get("sealed_until_knot")
                rank = art["rank"] if not sealed else art.get("banked_rank", 0)
                n_sealed += bool(sealed)
                n_learned += bool(not sealed and art["rank"] > 0)
                if sealed:
                    st = f'<span class="sealed-line">sealed until Knot {roman(sealed)}</span>' + (f' <span class="dim num">· {art["practice"]} days banked</span>' if art["practice"] else "")
                elif art["rank"] > 0:
                    st = f'<span class="brass">rank {roman(art["rank"])}</span>' + (f' <span class="dim num">· next at {art["next_at"]} days ({art["practice"]} so far)</span>' if art.get("next_at") else "")
                else:
                    st = '<span class="dim">not yet learned</span>'
                prev = thresholds[rank - 1] if rank else 0
                nxt = art.get("next_at")
                frac = (art["practice"] - prev) / (nxt - prev) if nxt and nxt > prev else 0.0
                ring = rank_ring(rank, n_pips, frac, label=f"{art['name']}: rank {rank} of {n_pips}", sealed=bool(sealed))
                rows.append(f'<li class="art{" sealed" if sealed else ""}{" on" if rank else ""}"><div class="art-top"><b>{esc(art["name"])}</b>{ring}</div>'
                            f'<span class="m">{st}</span><span class="e">{esc(art["effect"])}</span></li>')
            tree_html.append(f'<div class="tree"><h3>{svg_tree(tree)}{esc(tree)}</h3><ul class="arts">{"".join(rows)}</ul></div>')
        chap_rows = []
        titles = {str(ch["number"]): ch for ch in self.chapters}
        closed = sorted(self.chapters_csv, key=lambda r: int(r["chapter"]))
        for r in closed:
            ch = titles.get(r["chapter"])
            t = f'<a href="{rel}chronicle/{ch["slug"]}.html">{esc(ch["label"])} — {esc(ch["title"])}</a>' if ch else f"Chapter {esc(r['chapter'])}"
            chap_rows.append(f'<li class="sealed-row">{svg_seal(r["tier"], 28)}<div><b>{t}</b><span class="m">{esc(TIER_DONE.get(r["tier"], r["tier"]))}</span></div></li>')
        sheet = [("arts", "Arts", f"{n_learned} learned · {n_sealed} sealed", "".join(tree_html))]
        if self.bearing:
            sheet.append(("bearing", "Bearing", esc(self.bearing_summary()),
                          f'<p class="hint">{esc(BEARING_LABEL[:1].upper() + BEARING_LABEL[1:])}.</p>' + self.bearing_html()))
        sheet.append(("chapters", "Chapters", f"{len(closed)} closed" if closed else "none closed yet",
                      f'<ul class="chron">{"".join(chap_rows)}</ul>' if chap_rows else '<p class="empty">No chapter has closed yet.</p>'))
        return sheet

    @property
    def n_knots(self):
        return len(self.rules.get("knots") or []) or 7

    def tether_chip(self):
        """The Tether, once tied: its stage and the page's word for it. Nothing before stage I."""
        t = self.darrow.get("tether") or {}
        if not t.get("stage"):
            return ""
        return chip(f"The Tether {roman(t['stage'])} of {roman(t.get('of', 5))} · {t.get('name', '')}", "ember")

    def works_chip(self):
        """The works: how many he has finished, once there is one. The count is the sheet's; what they were is not the page's."""
        w = self.darrow.get("works") or {}
        n = as_int(w.get("finished")) or 0
        return f'<span class="chip brass works-chip">Works · {n} finished {tally(n, 13)}</span>' if n else ""

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
        """Darrow's page: who he is, then the Reckoning, open; below them every other section folded shut (a link to one
        of them, e.g. #binding, opens it)."""
        rel = "../"
        c = self.chars.get("darrow")
        d = self.darrow
        if not c:
            problem("saga/characters/darrow.json is missing")
            return
        sheet = "".join(panel(t, m, h, k) for k, t, m, h in self.darrow_panels(rel))
        first = ("now", "story", "keepsakes")  # on his own page, where he stands comes before what he looks like, and what he keeps right after
        parts = sorted(self.character_sections(c, rel), key=lambda x: (x["key"] not in first, first.index(x["key"]) if x["key"] in first else 0))
        story = "".join(panel(x["title"], x.get("meta", ""), x.get("panel_html", x["html"]), x["key"]) for x in parts)
        binding = sec("The Binding", f"Knots tied {roman(d['knots_count'])} of {roman(self.n_knots)}", self.knots_html(d, rel), hid="binding")
        body = (self.identity_plate(c, rel, d["level"]) + self.darrow_reckoning(rel) + binding
                + f'<div class="panels"><p class="lbl panels-h">The sheet</p>{sheet}<p class="lbl panels-h">On the page</p>{story}</div>')
        self.pages["darrow/index.html"] = shell("Ser Darrow of Edgemoor", body, rel, "Darrow", "char-page darrow-page", desc="Darrow's page and his full Reckoning.")

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

    def bearing_summary(self):
        """The Bearing in a word or two: the epithet if there is one, else the strongest lean, else 'even'."""
        ep = (self.bearing or {}).get("epithet")
        if ep:
            return ep
        leans = sorted(((abs(p - 0.5), w) for _, _, w, p in self.bearing_words() if w != "even"), reverse=True)
        return leans[0][1] if leans else "even"

    def bearing_chip(self):
        """One chip for the Now page's Reckoning card."""
        if not self.bearing:
            return ""
        return chip("Bearing · " + self.bearing_summary(), "brass" if self.bearing.get("epithet") else "")

    def roll_where(self, label, rel):
        """Where in the story a roll was cast, as a link: its label starts chNN-<scene key> (rolls.csv) when the scene is on
        the page; otherwise its chapter. Never the label itself (an engine key)."""
        m = re.match(r"ch(\d+)-([^#]*)", label or "")
        ch = next((c for c in self.chapters if m and c["code"] == m.group(1).zfill(2)), None)
        if not ch:
            return ""
        rest = m.group(2)
        for sc in sorted(ch["scenes"], key=lambda x: -len(x["key"])):  # between-12 before between-1
            k = sc["key"].lower()
            if rest == k or rest.startswith(k + "-") or rest in ("s" + k, "scene-" + k) or rest.startswith(("s" + k + "-", "scene-" + k + "-")):
                r = self.registry[(ch["code"], sc["key"])]
                return f'<a href="{rel}{r["href"]}">{esc(r["label"])}</a>'
        return f'<a href="{rel}chronicle/{ch["slug"]}.html">{esc(ch["label"] + " — " + ch["title"])}</a>'

    def dice_html(self, rel, n=5):
        """The latest rolls: the check and its result on one line with where it was cast, the arithmetic on its own line."""
        rolls = sorted(self.rolls, key=lambda r: r.get("when", ""), reverse=True)[:n]
        if not rolls:
            return '<p class="empty">No dice have been cast yet.</p>'
        rows = []
        for r in rolls:
            d20 = r.get("d20", "") + (f"/{r['d20_b']}" if r.get("d20_b") else "")
            res = r.get("result", "")
            cls = "good" if "SUCCESS" in res else ("warn" if "PARTIAL" in res else "bad")
            where = self.roll_where(r.get("label", ""), rel)
            rows.append(f'<li class="roll"><div class="roll-top">{d20_glyph(r.get("d20"), res)}<span class="dice-tag">{esc(r.get("stat", "").upper() or "FLAT")} · DC {esc(r.get("dc"))}</span>'
                        f'{badge(res.title(), cls)}</div>'
                        f'<p class="roll-math num">d20 <b>{esc(d20)}</b> {esc(r.get("mods", ""))} = <b>{esc(r.get("total"))}</b></p>'
                        + (f'<p class="roll-where">{where}</p>' if where else "") + '</li>')
        return f'<ul class="rolls">{"".join(rows)}</ul>'

    def knots_brief(self, rel):
        """The Knots on the Now page: the rope, how many are tied and the next one; the full list lives on Darrow's page."""
        d = self.darrow
        tied = set(d.get("knots_tied") or [])
        knots = self.rules.get("knots") or []
        nxt = next((k for k in knots if k["n"] not in tied), None)
        line = f'Knots tied {roman(len(tied))} of {roman(self.n_knots)}'
        if nxt:
            line += f' · next, {esc(nxt["name"])}: {esc(nxt["proves"])}'
        soft = '<p class="hint">The soft season: do not trust the quiet.</p>' if d.get("soft_season") else ""
        return f'<div class="knots-brief">{rope_knots(tied, knots)}<p class="m">{line}.</p>{soft}</div>'

    def render_now(self):
        """What is going on now, in the order he would act on it: the chapter and the way back into it, an open choice,
        the quest, who is with him, his Reckoning, the map, the last answered choice, the latest dice. Each world.json field
        has one job here: last_beat the latest scene, current_quest.on_the_page the quest, current_struggle what he fights,
        and a companion's line is their last_seen_doing (their page carries the rest)."""
        rel = ""
        w, d = self.world, self.darrow
        ch, latest, after = self.latest_pieces()
        place = self.place_by_id.get(self.current_place, {})
        loc = w.get("location") or {}
        where = place.get("name", "") + (f", {loc.get('detail')}" if isinstance(loc, dict) and loc.get("detail") else "")
        scene_row = ""
        if latest and after:  # the newest piece is a Between: the scene it follows gets its own row
            scene_row = (f'<dt>Latest scene</dt><dd><a href="{rel}chronicle/{ch["slug"]}.html#{latest["anchor"]}">'
                         f'{esc((latest["label"] + " — " if latest["label"] else "") + latest["title"])}</a></dd>')
        book_line = f"Book {roman(w.get('book', 1))} — {w['book_title']}" if w.get("book_title") else ""
        tier = (d.get("chapter_now") or {}).get("tier_so_far")
        tier_chip = f'<div class="chips">{chip(TIER_SO_FAR[tier], TIER_CLS.get(tier, ""))}</div>' if tier in TIER_SO_FAR else ""
        plate = (f'<section class="plate now-plate"><p class="lbl">{esc(book_line)}</p>'
                 f'<h1>{esc("Chapter " + str(w.get("chapter")) + " — " + w.get("chapter_title", ""))}</h1>{tier_chip}'
                 f'<dl class="kv"><dt>Where</dt><dd>{esc(where)}</dd><dt>Season</dt><dd>{esc(w.get("season", ""))}</dd>{scene_row}</dl>'
                 f'<div class="beat"><span class="lbl">Just happened</span><p>{esc(w.get("last_beat", ""))}</p></div>{self.continue_button(rel)}</section>')
        q = w.get("current_quest") or {}
        work = "".join(f'<h3 class="sub-h">Work in hand</h3><p class="prose">{esc(pr.get("name", ""))}, stage {pr.get("stage")} of {pr.get("of")}: {esc(pr.get("visible", ""))}</p>'
                       for pr in getattr(self, "projects", []) or [] if pr.get("status") == "live")
        quest = sec("The quest", q.get("name", ""), f'<p class="prose">{esc(q.get("on_the_page", ""))}</p><h3 class="sub-h">What he is fighting</h3><p class="prose">{esc(w.get("current_struggle", ""))}</p>' + work)
        tales_html = ""
        if self.tales:
            items = []
            for t in self.tales:
                stt = self.tale_state.get(t["code"], {})
                last = t["scenes"][-1] if t["scenes"] else None
                state = "told in full" if stt.get("done") else f'told in part, {stt.get("told", len(t["scenes"]))} of {stt.get("pieces", "?")}' if stt.get("rests") else f'{stt.get("told", len(t["scenes"]))} of {stt.get("pieces", "?")} told'
                link = f'<a href="{rel}tales/{t["slug"]}.html{"#" + last["anchor"] if last else ""}"><b>{esc(t["label"])} — {esc(t["title"])}</b></a>'
                items.append(f'<li>{link}<span class="m num">{esc(state)}' + (f' · latest: {esc(last["label"] + " — " + last["title"])}' if last else "") + "</span></li>")
            tales_html = sec("The tales", f"{len(self.tales)}", f'<ul class="chron">{"".join(items)}</ul><p class="dim">The past, a piece at a time. <a href="{rel}tales/index.html">All the tales</a>.</p>')
        oc = self.open_choice()
        open_html = answered_html = ""
        if oc:
            open_html = sec(self.choice_title(oc["kind"], None, oc["scene"]["key"]), "waiting on Darrow",
                            self.choice_list(oc["items"]) + f'<p class="dim">From <a href="{rel}chronicle/{oc["chapter"]["slug"]}.html#{oc["scene"]["anchor"]}">{esc(oc["chapter"]["label"] + " — " + oc["scene"]["title"])}</a>.</p>',
                            cls="choice-open")
        else:
            lc = self.latest_choice()
            if lc:
                answered_html = sec(self.choice_title(lc["kind"], lc["rec"], lc["scene"]["key"]), "answered",
                                    self.choice_list(lc["items"], lc["rec"]) + f'<p class="dim">From <a href="{rel}chronicle/{lc["chapter"]["slug"]}.html#{lc["scene"]["anchor"]}">{esc(lc["chapter"]["label"] + " — " + lc["scene"]["title"])}</a>.</p>')
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
            comps.append(f'<a class="comp" href="{rel}{self.char_href(cid)}">{self.avatar(c, rel, 48, "sm") or sigil(self.factions.get(sg.get("faction"), {}), sg.get("mark"), 48)}'
                         f'<div><div class="comp-top"><b>{esc(c["name"])}</b><span class="lbl">{mood_mark(mood)}{esc(mood)}</span></div><span class="m">{esc(c.get("last_seen_doing", ""))}</span></div></a>')
        companions = sec("With him", "", f'<div class="comps">{"".join(comps)}</div>' if comps else '<p class="empty">No one yet.</p>')
        a = d["attributes"]
        rk = "".join(f'<div class="mini-attr"><span class="lbl">{k.capitalize()}</span><span class="v num">{a[k]["score"]}</span><span class="fell num">{a[k]["fell"]}</span></div>'
                     for k in ("might", "vigor", "finesse", "resolve"))
        bchip = (self.bearing_chip() or "") + self.tether_chip() + self.works_chip()
        card = (f'<div class="rk-mini"><div class="hero">{self.avatar(self.chars.get("darrow"), rel, 86, "big") or crest(d["level"])}<div class="who"><h3>{esc(d["name"])}</h3><p class="sub">Level {d["level"]} · {esc(d["rank"])} · HP {d["hp_max"]}</p>'
                f'<div class="insp"><span class="lbl">Inspiration</span>{pips(d["inspiration"], d["inspiration_cap"])}</div>'
                + (f'<div class="chips">{bchip}</div>' if bchip else "") + '</div></div>'
                f'<div class="mini-attrs">{rk}</div><p class="hint">The faint numbers are the ones he read behind his own.</p>'
                f'{bar(d["ember"]["value"] or 0, 100, "Ember · " + str(d["ember"]["tier"] or "unlit"), "ember", d["ember"]["value"])}'
                f'{self.knots_brief(rel)}'
                f'<p class="links"><a href="{rel}darrow/index.html#reckoning">The full Reckoning</a> · <a href="{rel}darrow/index.html#binding">All the Knots</a></p></div>')
        reck = sec("The Reckoning", "", card)
        map_html = sec("The map", "", svg_map(self.places, self.route, self.current_place, rel)
                       + '<p class="legend"><span class="lg ember">●</span> Darrow <span class="lg brass">●</span> visited <span class="lg faint">●</span> not yet <span class="lg route">—</span> the road so far</p>')
        dice = sec("The dice", "", self.dice_html(rel))
        body = plate + open_html + quest + companions + reck + tales_html + map_html + answered_html + dice
        self.pages["index.html"] = shell("Now", body, rel, "Now", "now-page", desc="What is going on now in The Unkneeling.")

    # ---------------------------------------------------------------- tales
    def render_tale(self, idx):
        """A tale's page: its title and when it is set, its pieces as a reader, the people in it, a pager to the next tale."""
        t = self.tales[idx]
        rel = "../"
        prev_t = self.tales[idx - 1] if idx > 0 else None
        next_t = self.tales[idx + 1] if idx + 1 < len(self.tales) else None
        stt = self.tale_state.get(t["code"], {})
        head = [f'<p class="book-line">The tales</p>', f'<h1 class="ch-title"><span class="lbl">{esc(t["label"])}</span>{esc(t["title"])}</h1>']
        if t.get("when"):
            head.append(f'<p class="when">{inline(t["when"])}</p>')
        state = ("told in full" if stt.get("done") else f'told in part: {stt.get("told", len(t["scenes"]))} of {stt.get("pieces", "?")} pieces, and the rest left untold'
                 if stt.get("rests") else f'{stt.get("told", len(t["scenes"]))} of {stt.get("pieces", "?")} pieces told; the rest is still to come')
        head.append(f'<p class="dim">{esc(state)}.</p>')
        body = []
        for s in t["scenes"]:
            seen = set()
            lab = f'<span class="scene-n">{esc(s["label"])}</span>' if s["label"] else ""
            body.append(f'<section class="scene" id="{s["anchor"]}"><h2 class="scene-h">{lab}{esc(s["title"])}</h2>{self.render_blocks(t, s, rel, seen)}</section>')
        if not t["scenes"]:
            body.append('<p class="empty">The first piece is still to come.</p>')
        keeps = [kp for kp in self.keepsakes if kp.get("tale") == t["code"]]
        keep_html = ""
        if keeps:
            rows = "".join(f'<li class="keep"><b>{esc(kp["name"])}</b><p class="prose">{esc(kp["text"])}</p>'
                           f'<span class="src">kept by <a href="{rel}{self.char_href(kp["to"])}">{esc(self.chars[kp["to"]]["name"] if kp["to"] in self.chars else kp["to"])}</a></span></li>' for kp in keeps)
            keep_html = f'<div class="cast"><span class="lbl">What this tale left</span><ul class="keeps">{rows}</ul></div>'
        cast = [c for c in self.chars.values() if any(str(a.get("chapter")) == t["code"] and not a.get("mention") for a in c.get("appearances") or [])]
        cast_html = ""
        if cast:
            cast_html = '<div class="cast"><span class="lbl">On the page in this tale</span><div class="chips">' + "".join(
                f'<a class="chip brass" href="{rel}{self.char_href(c["id"])}">{esc(c["name"])}</a>' for c in cast) + "</div></div>"
        nav = '<nav class="pager" aria-label="Tales">'
        nav += f'<a href="{rel}tales/{prev_t["slug"]}.html"><span class="lbl">Previous</span>{esc(prev_t["label"] + " — " + prev_t["title"])}</a>' if prev_t else '<span></span>'
        nav += f'<a class="next" href="{rel}tales/{next_t["slug"]}.html"><span class="lbl">Next</span>{esc(next_t["label"] + " — " + next_t["title"])}</a>' if next_t else f'<a class="next" href="{rel}tales/index.html"><span class="lbl">The tales</span>All the tales</a>'
        nav += "</nav>"
        page = f'<article class="reader">{"".join(head)}{"".join(body)}</article>{keep_html}{cast_html}{nav}'
        self.pages[f"tales/{t['slug']}.html"] = shell(f"{t['label']} — {t['title']}", page, rel, "Tales", "reader-page",
                                                      desc=f"{t['label']} of The Unkneeling: {t['title']}.")

    def render_tales_index(self):
        rel = "../"
        items = []
        for t in self.tales:
            stt = self.tale_state.get(t["code"], {})
            pieces = "".join(f'<li><a href="{rel}tales/{t["slug"]}.html#{s["anchor"]}">{esc(s["label"] + " — " + s["title"])}</a></li>' for s in t["scenes"])
            state = "told in full" if stt.get("done") else f'told in part, {stt.get("told", len(t["scenes"]))} of {stt.get("pieces", "?")}' if stt.get("rests") else f'{stt.get("told", len(t["scenes"]))} of {stt.get("pieces", "?")} told'
            items.append(f'<li class="{"now" if not stt.get("done") else ""}"><a class="ch-link" href="{rel}tales/{t["slug"]}.html"><b>{esc(t["label"])} — {esc(t["title"])}</b></a>'
                         f'<span class="m num">{esc(state)}' + (f' · {esc(t["when"])}' if t.get("when") else "") + f' · about {t["words"]:,} words</span>'
                         f'<ul class="scenes">{pieces}</ul></li>')
        n_done = sum(1 for t in self.tales if self.tale_state.get(t["code"], {}).get("done"))
        body = ('<section class="plate"><p class="lbl">The tales</p><h1>The past, a piece at a time</h1>'
                '<p class="dim">What came before the Steps: who they were, where they rode, what they kept. Each tale is told in pieces, '
                'and what it leaves behind goes to the one who keeps it.</p></section>')
        body += sec("Told so far", (f"{len(self.tales)} tale{'s' if len(self.tales) != 1 else ''}" + (f" · {n_done} in full" if n_done else "")) if self.tales else "",
                    f'<ul class="chron">{"".join(items)}</ul>' if items else '<p class="empty">No tale has begun yet.</p>')
        self.pages["tales/index.html"] = shell("Tales", body, rel, "Tales", desc="The tales of The Unkneeling: the past, a piece at a time.")

    # ---------------------------------------------------------------- codex
    def project_html(self, place_id):
        """What Darrow changed at a place: the Book's project trace from world.json → projects[] (reader-safe, in the page's words)."""
        out = []
        for pr in getattr(self, "projects", []) or []:
            if pr.get("place") != place_id:
                continue
            state = "finished" if pr.get("status") == "done" else f"stage {pr.get('stage')} of {pr.get('of')}"
            dec = "".join(f"<li>{esc(d.get('chose', ''))}</li>" for d in pr.get("decisions") or [] if d.get("chose"))
            out.append(f'<h3 class="sub-h">What Darrow changed here</h3><p>{esc(pr.get("name", ""))} · {esc(state)}. {esc(pr.get("visible", ""))}</p>'
                       + (f'<ul class="plain">{dec}</ul>' if dec else ""))
        return "".join(out)

    def render_codex(self):
        """The Codex: places (where he has been, then the ones named but not reached), factions, sayings, things; a jump
        bar to each section at the top. The row numerals count within a section."""
        rel = "../"
        secs, jumps = [], []

        def rows(items, start=1):
            return f'<ol class="archive" start="{start}">' + "".join(
                f'<li{(" id=" + chr(34) + it["id"] + chr(34)) if it.get("id") else ""}><details><summary><span><span class="rn">{roman(i)}</span>{esc(it["name"])}</span>{it.get("tag", "")}</summary><div class="dt-body">{it["html"]}</div></details></li>'
                for i, it in enumerate(items, start)) + "</ol>"

        def add(title, sid, count, inner):
            secs.append(sec(title, str(count), inner, hid=sid))
            jumps.append(f'<a class="chip" href="#{sid}">{esc(title)}</a>')

        been, named = [], []
        for p in self.places:
            if not p.get("on_page"):
                continue
            fs = p.get("first_seen") or {}
            src = self.scene_ref(fs, rel) if fs else ""
            name = p["name"] + (f" · {p['subtitle']}" if p.get("subtitle") else "")
            (been if p.get("visited") else named).append({
                "name": name, "id": f"place-{p['id']}", "tag": self.codex_thumb(p, rel),
                "html": self.codex_figure(p, rel) + f'<p>{esc(p["description"])}</p>' + self.project_html(p["id"]) + f'<p class="m">First on the page: {src}</p>'})
        offmap = [p["name"] for p in self.places if not p.get("on_page")]
        inner = ""
        if been:
            inner += f'<h3 class="sub-h">Where he has been <span class="num">· {len(been)}</span></h3>' + rows(been)
        if named:
            inner += f'<h3 class="sub-h">Named, not yet reached <span class="num">· {len(named)}</span></h3>' + rows(named, len(been) + 1)
        if offmap:
            inner += f'<p class="dim">On the map but not yet in the story: {esc(", ".join(offmap))}.</p>'
        add("Places", "places", len(been) + len(named), inner or '<p class="empty">Nothing yet.</p>')
        facs = []
        for f in self.factions.values():
            if not f.get("on_page"):
                continue
            facs.append({"name": f["name"], "id": f"faction-{f['id']}", "tag": self.codex_thumb(f, rel),
                         "html": self.codex_figure(f, rel) + f'<div class="fac">{sigil(f, None, 44)}<p>{esc(f["description"])}</p></div>'})
        add("Factions", "factions", len(facs), rows(facs))
        sayings = [{"name": s["name"].strip('"“”'), "tag": "", "html": f"<p>{inline(s['text'])}</p>"} for s in self.codex.get("Sayings", [])]
        add("Sayings", "sayings", len(sayings), rows(sayings))
        things, beasts, extra = [], [], {}
        for key, bucket, e, anchor in self.codex_things():
            item = {"name": e["name"], "id": anchor, "tag": self.codex_thumb(e, rel),
                    "html": self.codex_figure(e, rel) + self.codex_song(e, rel) + f"<p>{inline(e['text'])}</p>"}
            (things if bucket == "things" else beasts if bucket == "beasts" else extra.setdefault(key, [])).append(item)
        add("Things", "things", len(things), rows(things) if things else '<p class="empty">Nothing yet.</p>')
        if beasts:
            add("Beasts and others", "beasts", len(beasts), rows(beasts))
        for key, items in extra.items():
            if items:
                add(key, "sec-" + slug(key), len(items), rows(items))
        jump = f'<nav class="jump chips" aria-label="Codex sections">{"".join(jumps)}</nav>'
        body = ('<section class="plate"><p class="lbl">The Codex</p><h1>Places, factions, sayings</h1><p class="dim">Only what the page has shown. '
                f'Names on the map that the story has not reached yet are names and nothing more.</p>{jump}</section>' + "".join(secs))
        self.pages["codex/index.html"] = shell("Codex", body, rel, "Codex", desc="Places, factions and sayings of The Unkneeling.")

    # ---------------------------------------------------------------- run
    def build(self):
        for i in range(len(self.chapters)):
            self.render_chapter(i)
        self.render_chronicle_index()
        for i in range(len(self.tales)):
            self.render_tale(i)
        self.render_tales_index()
        for c in self.chars.values():
            if c["id"] != "darrow":
                self.render_character(c)
        self.render_roster()
        self.render_darrow()
        self.render_now()
        self.render_codex()
        self.pages["site.css"] = CSS
        self.pages["site.js"] = JS
        self.pages["favicon.svg"] = FAVICON
        for name in ("favicon-32.png", "apple-touch-icon.png"):  # the favicon as bitmaps, for browsers that take no SVG
            if (SITE_ART / name).is_file():
                self.assets[name] = SITE_ART / name
            else:
                problem(f"saga/art/site/{name} is missing (the favicon's bitmap; draw it from FAVICON in build_site.py)")
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
Bearing Leans Named Even Epithet Small Answered Himself Interlude Waiting Songs Verses Histories Annals
Tales Tale Piece Pieces Keepsakes Keepsake Works Told Kept All Shelf Finished Devoted Loyal Fond Warming Civil Wary Cold Hostile Enemy""".split()
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


def scene_text(scene):
    """The normalized text of one parsed scene: every string in its blocks, in order (the evidence check searches it)."""
    def walk(x):
        if isinstance(x, str):
            yield x
        elif isinstance(x, (list, tuple)):
            for y in x:
                yield from walk(y)
    return norm(" ".join(walk(scene.get("blocks") or [])))


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


def gm_strings(obj, out=None):
    """Every string value in a JSON structure (the GM records), one per line."""
    if out is None:
        out = []
    if isinstance(obj, dict):
        for v in obj.values():
            gm_strings(v, out)
    elif isinstance(obj, list):
        for v in obj:
            gm_strings(v, out)
    elif isinstance(obj, str):
        out.append(obj)
    return out


def gm_blocklists(chron_text, allowed_words, extra_gm="", allowed_text=""):
    """Sentences and unrevealed names from the GM files. Nothing from here is rendered; it only builds the checks.
    GM files: every .md under saga/bible/_gm/ and saga/state/_gm/ (JSON there is not scanned: every name it carries is
    also in a GM .md). A GM sentence is exempt when the chronicle or allowed_text (engine/rules.json strings and the
    Bearing's pole words / current epithet) already carries it."""
    gm_text = "\n".join(p.read_text(encoding="utf-8") for d in GM_DIRS if d.exists() for p in sorted(d.rglob("*.md")))
    # the GM records as data: every string in the notes (saga/state/_gm/notes/*.jsonl) and the threads (threads.json) is GM prose too
    for d in GM_DIRS:
        if not d.exists():
            continue
        for p in sorted(list(d.rglob("*.jsonl")) + [d / "threads.json"]):
            if not p.exists():
                continue
            try:
                rows = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] if p.suffix == ".jsonl" else [json.load(open(p, encoding="utf-8"))]
            except (OSError, ValueError):
                continue
            gm_text += "\n" + "\n".join(gm_strings(rows))
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
    chron_text = "\n".join(read(p) for p in sorted(CHRON.glob("*.md")) + (sorted(TALES.glob("*.md")) if TALES.exists() else []))
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
    for nm in (site.rules.get("tether") or {}).get("names", []):  # the Tether's stage words are game rules too
        allowed.update(re.findall(r"[A-Za-z']+", nm))
    allowed.add("Tether")
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
    allowed_text += [str(nm) for nm in (site.rules.get("tether") or {}).get("names", [])]
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
            href, frag = m.group(1).split("?", 1)[0], m.group(2)
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
            if target not in site.pages and target not in site.assets:
                problem(f"{k}: broken link '{href}' (no such file {target})")
                continue
            if frag and frag != "#" and target in ids and frag[1:] not in ids[target]:
                problem(f"{k}: broken anchor '{href}{frag}'")


# ============================================================ assets
# The favicon: a brass-rimmed shield with a knot on its rope, in the site's colours. saga/art/site/ holds the same drawing
# as favicon-32.png and, on a full dark square, apple-touch-icon.png (180 px); redraw both if this changes.
FAVICON = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
           '<path d="M32 4 L57 10.5 V32 C57 47.5 46.5 56.5 32 61 C17.5 56.5 7 47.5 7 32 V10.5 Z" fill="#161B22" stroke="#CFA65F" stroke-width="4" stroke-linejoin="round"/>'
           '<path d="M13 31 H51" stroke="#CFA65F" stroke-width="4" stroke-linecap="round"/>'
           '<circle cx="32" cy="31" r="8.5" fill="#E2713B" stroke="#CFA65F" stroke-width="3"/></svg>\n')

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
html{background:var(--night);scroll-padding-top:calc(var(--mast-h,104px) + 12px)}
html:focus-within{scroll-behavior:smooth}  /* smooth for a link followed on the page, never for the jump a page opens with */
@media (min-width:560px){html{--mast-h:58px}}
html.mast-away{scroll-padding-top:16px}
body{margin:0;background:var(--night);color:var(--ink);font-family:var(--body);font-size:16px;line-height:1.45;-webkit-font-smoothing:antialiased;overflow-x:hidden}
img,svg{max-width:100%}
.wrap{max-width:640px;margin:0 auto;padding-inline:16px}
main.wrap{padding-block:20px 56px;display:grid;gap:30px}
h1,h2,h3,h4{margin:0;text-wrap:balance;overflow-wrap:break-word}
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
.mast{border-bottom:1px solid var(--rule);background:var(--night);position:sticky;top:0;z-index:5;transition:transform .25s ease}
html.mast-away .mast{transform:translateY(-100%)}
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
.beat{display:grid;gap:3px;color:var(--dim);border-left:2px solid var(--brass-dim);padding-left:10px;font-size:.95rem;line-height:1.5}
.btn{display:inline-block;font-family:var(--label);font-weight:700;letter-spacing:.06em;line-height:1.3;white-space:nowrap;border:1px solid var(--brass);border-radius:4px;padding:7px 14px;color:var(--night);background:var(--brass)}
.btn:hover{text-decoration:none;filter:brightness(1.08)}
.btn-row{display:flex;flex-wrap:wrap;align-items:center;gap:6px 12px}
.btn-note{font-size:.9rem;color:var(--dim);min-width:0}
.btn-note:hover{color:var(--brass);text-decoration:none}
.plain{list-style:none;margin:0;padding:0;display:grid;gap:3px}
.fine{font-size:.82rem;color:var(--faint);font-style:italic}

/* section heads */
.sec{display:grid;gap:14px}
.sec-h{display:flex;align-items:baseline;gap:12px;border-bottom:1px solid var(--rule);padding-bottom:6px}
.sec-h h2{font-family:var(--display);font-weight:700;font-size:1.45rem;color:var(--ink)}
.sec-h h2{flex:none;max-width:100%}
.sec-h .lbl{margin-left:auto;text-align:right;min-width:0}
.sub-h{font-family:var(--label);font-weight:700;font-size:.85rem;letter-spacing:.08em;color:var(--dim);margin-top:8px}

/* hero / identity */
.hero{display:grid;grid-template-columns:86px minmax(0,1fr);gap:16px;align-items:center}
.who{display:grid;gap:6px;min-width:0}
.who h1,.who h2,.who h3{font-family:var(--display);font-weight:700;font-size:1.7rem;line-height:1.1;color:var(--ink)}
.who .sub{color:var(--dim);font-size:.95rem}
.sigil-row{display:flex;align-items:center;gap:10px;font-size:.9rem;border-top:1px dotted var(--rule);padding-top:10px}
.fac-name{color:var(--dim)} a.fac-name:hover{color:var(--brass)}
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
.state{display:inline-block;font-family:var(--label);font-size:.78rem;letter-spacing:.08em;padding:1px 8px;border-radius:3px;border:1px solid currentColor;line-height:1.4;white-space:nowrap}
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
.chron .scenes li{display:block}
.chron .scenes .state{margin-left:6px;vertical-align:1px}

/* archive rows */
.archive{list-style:none;margin:0;padding:0;display:grid;gap:0}
.archive li{border-bottom:1px solid var(--rule)}
.archive details{border:0;padding:9px 0}
.archive summary{color:var(--ink);font-family:var(--body);font-size:.98rem;letter-spacing:0;align-items:center;justify-content:flex-start}
.archive summary>span:first-child{flex:1 1 auto;min-width:0;display:flex;align-items:baseline}
.archive summary .state{margin-right:4px}
.archive+.sub-h{margin-top:18px}
.jump .chip{color:var(--brass);border-color:var(--brass-dim)}
.archive summary .rn{font-family:var(--display);color:var(--brass);width:2.2em;flex:none;display:inline-block;font-size:1.3rem;line-height:1}
.archive .dt-body{color:var(--dim);max-width:62ch;display:grid;gap:6px}
.archive .dt-body p{line-height:1.5}
.archive .m{font-size:.86rem;color:var(--faint)}

/* place pictures: full width in the codex entry, tap to see whole */
.archive summary .thumb{flex:none;width:56px;height:32px;object-fit:cover;border-radius:3px;border:1px solid var(--rule);margin-right:6px}
.archive .dt-body:has(>.codex-art){max-width:none}
.archive .dt-body:has(>.codex-art)>p,.archive .dt-body:has(>.codex-art)>.fac{max-width:62ch}
.codex-art{margin:2px 0 6px}
.codex-art a{display:block;aspect-ratio:16/9;border:1px solid var(--rule);border-radius:6px;overflow:hidden;background:var(--plate);cursor:zoom-in}
.codex-art a:focus-visible{outline:2px solid var(--brass);outline-offset:2px}
.codex-art img{display:block;width:100%;height:100%;object-fit:cover}
.codex-art figcaption{font-size:.82rem;color:var(--faint);margin-top:6px}
.zoom-hint .c{display:none}
/* portraits: one square frame on every character page, scaling with the screen (about a third of a phone, 200px on
   anything wider), cropped to fit and never stretched; the level crest pinned to the frame's corner; round in cards */
.hero.with-portrait{grid-template-columns:clamp(112px,34vw,200px) minmax(0,1fr)}
.portrait{margin:0;position:relative;min-width:0}
.portrait a{display:block;aspect-ratio:1/1;border:1px solid var(--brass-dim);border-radius:6px;overflow:hidden;background:var(--plate);cursor:zoom-in;box-shadow:0 0 0 4px rgba(207,166,95,.06)}
.portrait a:focus-visible{outline:2px solid var(--brass);outline-offset:2px}
.portrait img{display:block;width:100%;height:100%;object-fit:cover}
.portrait .crest{position:absolute;left:-8px;bottom:-10px;width:clamp(38px,11vw,52px);height:auto;pointer-events:none;filter:drop-shadow(0 2px 4px rgba(0,0,0,.7))}
.avatar{display:block;width:56px;height:56px;border-radius:50%;object-fit:cover;border:1px solid var(--brass-dim);background:var(--plate)}
.avatar.big{width:86px;height:86px;border:2px solid var(--brass-dim)}
.avatar.sm{width:48px;height:48px}
@media (hover:hover) and (pointer:fine){.zoom-hint .c{display:inline}.zoom-hint .t{display:none}}
dialog.zoom{padding:0;border:0;margin:0;inset:0;background:transparent;width:100vw;height:100vh;height:100dvh;max-width:none;max-height:none}
dialog.zoom[open]{display:flex;align-items:center;justify-content:center}
dialog.zoom::backdrop{background:rgba(6,8,11,.92)}
dialog.zoom img{max-width:100vw;max-height:100vh;max-height:100dvh;width:auto;height:auto;object-fit:contain;cursor:zoom-out}
dialog.zoom .x{position:fixed;top:10px;right:12px;width:40px;height:40px;border-radius:50%;border:1px solid var(--rule);background:rgba(15,18,23,.75);color:var(--ink);font-size:1.5rem;line-height:1;cursor:pointer}
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

/* Darrow's page: the Reckoning open at the top, every other section a panel folded shut */
.reck{display:grid;gap:12px}
.reck-line{font-size:1.05rem} .reck-line b{font-family:var(--display);font-size:1.35rem;font-weight:700;color:var(--brass)}
.reck .streaks{margin-top:6px}
.panels{display:grid;gap:10px}
.panels-h{margin-top:4px}
.panels-h+.panel{margin-top:-2px}
.panel+.panels-h{margin-top:18px}
.panel{border:1px solid var(--rule);border-radius:6px;padding:0;background:var(--plate)}
.panel[open]{border-color:var(--brass-dim);background:linear-gradient(180deg,var(--plate-hi),var(--plate) 120px)}
.panel>summary{display:flex;align-items:center;gap:12px;padding:12px 14px;color:var(--ink);font-family:var(--body);font-size:1rem;letter-spacing:0}
.panel>summary h2{font-family:var(--display);font-weight:700;font-size:1.3rem;line-height:1.15;flex:none}
.panel>summary .meta{margin-left:auto;font-family:var(--label);font-size:.8rem;letter-spacing:.06em;color:var(--dim);text-align:right;min-width:0}
.panel>summary::after{content:"";flex:none;width:8px;height:8px;margin:0 2px 4px 0;border-right:2px solid var(--brass);border-bottom:2px solid var(--brass);transform:rotate(45deg);transition:transform .2s}
.panel[open]>summary::after{content:"";transform:rotate(-135deg);margin-bottom:-4px}
.panel>summary:hover h2{color:var(--brass)}
.panel-body{padding:4px 14px 16px;display:grid;gap:12px}
.panel-body>.tree:last-child{margin-bottom:0}

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
.comp-top{display:flex;justify-content:space-between;align-items:baseline;gap:8px;flex-wrap:wrap}
.comp .m{font-size:.88rem;color:var(--dim)}
.rk-mini{display:grid;gap:12px}
.rk-mini .who h3{font-size:1.35rem}
.mini-attrs{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}
.mini-attr{display:grid;gap:0;border-top:2px solid var(--rule);padding-top:6px}
.mini-attr .v{font-family:var(--display);font-weight:700;font-size:1.8rem;line-height:1}
.mini-attr .fell{font-size:.8rem;color:var(--faint)}
.rolls{list-style:none;margin:0;padding:0;display:grid;gap:8px}
.roll{display:grid;gap:5px;border-bottom:1px dotted var(--rule);padding-bottom:8px}
.roll-top{display:flex;align-items:center;gap:10px}
.roll-top .state{margin-left:auto}
.roll-where{font-size:.84rem;color:var(--faint)}
.roll-where a{color:var(--dim)} .roll-where a:hover{color:var(--brass)}
.roll-math{font-size:.92rem;color:var(--ink)}
.knots-brief{display:grid;gap:6px}
.knots-brief .m{font-size:.86rem;color:var(--dim)}

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
.rel{display:grid;gap:3px;border-bottom:1px dotted var(--rule);padding-bottom:8px}
.rel>.lbl{color:var(--dim);line-height:1.35}
.rel-top{display:flex;justify-content:space-between;gap:8px;align-items:baseline;flex-wrap:wrap}
.rel-top b{flex:0 0 auto} .rel-top .lbl{margin-left:auto;text-align:right}
.seen{font-size:.92rem;color:var(--dim)} .seen .lbl{margin-right:6px}
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
.previously{color:var(--dim);background:var(--plate);border:1px solid var(--rule);border-radius:6px;padding:10px 14px;max-width:65ch;display:grid;gap:2px}
.reader .previously p{font-size:.95rem;line-height:1.5}
.book-line{font-family:var(--label);letter-spacing:.14em;color:var(--brass);font-size:.9rem}
.ch-title{font-family:var(--display);font-weight:700;font-size:2.1rem;line-height:1.1;display:grid;gap:4px}
.ch-title .lbl{font-size:.85rem}
.epigraph{margin:0;padding:0 0 4px}
.epigraph blockquote{margin:0;border-left:2px solid var(--brass-dim);padding-left:14px}
.epigraph p{font-style:italic;color:var(--dim);font-size:17px;max-width:60ch}
.epigraph figcaption{font-family:var(--label);letter-spacing:.06em;color:var(--faint);font-size:.85rem;margin-top:8px;padding-left:14px;display:flex;flex-wrap:wrap;align-items:center;gap:8px 10px}
.scene-h{font-family:var(--display);font-weight:700;font-size:1.55rem;line-height:1.15;border-bottom:1px solid var(--rule);padding-bottom:6px;display:flex;gap:12px;align-items:baseline;flex-wrap:wrap}
.scene.between{margin-left:14px;padding-left:14px;border-left:2px solid var(--rule)}
.scene.between .scene-h{font-size:1.15rem;border-bottom:0;padding-bottom:0}
.scene.between .scene-n{color:var(--dim)}
.scene-n{font-family:var(--label);font-size:.85rem;letter-spacing:.1em;color:var(--brass)}
.reader h3{font-family:var(--display);font-weight:700;font-size:1.3rem}
hr.break{border:0;border-top:1px solid var(--rule);width:40%;margin:4px auto}
.ornament{text-align:center;color:var(--brass-dim);letter-spacing:.4em;font-size:.9rem}
.reader blockquote{margin:0;border-left:2px solid var(--brass-dim);padding-left:14px;color:var(--dim)}
.reckoning{border:1px solid var(--brass-dim);border-radius:6px;padding:12px 14px;background:linear-gradient(180deg,rgba(207,166,95,.08),transparent);display:grid;gap:4px;max-width:65ch}
.reckoning p{font-size:1rem;line-height:1.5;color:var(--t1);font-family:var(--body)}
.reckoning .rk-h{color:var(--brass)}
.dice{font-family:var(--body);display:flex;flex-direction:column;gap:6px;border:1px dashed var(--rule);border-radius:4px;padding:8px 10px;max-width:65ch}
.dice-row{display:flex;flex-wrap:wrap;gap:6px 10px;align-items:center}
.dice-row.superseded{opacity:.55}
.dice-row.insp{padding-left:4px}
.insp-glyph{display:inline-block;width:32px;text-align:center;font-size:1.25rem;line-height:32px;color:var(--brass)}
.dice-tag{font-family:var(--label);letter-spacing:.08em;font-size:.82rem;color:var(--brass);border:1px solid var(--brass-dim);border-radius:3px;padding:1px 7px;white-space:nowrap}
.dice-body{font-variant-numeric:tabular-nums}
.choice-h{font-family:var(--display);font-size:1.35rem;color:var(--brass)}
ol.choice{margin:0;padding-left:1.4em;display:grid;gap:8px;max-width:65ch;font-size:17px;line-height:1.5}
ol.choice li.taken{color:var(--ink)} ol.choice li.taken::marker{color:var(--good)}
ol.choice li{color:var(--dim)}
ol.choice li s{color:var(--faint)}
.reader ul,.reader ol:not(.choice){max-width:65ch;font-size:17px;line-height:1.55}
.nm{color:var(--ink);border-bottom:1px dotted var(--brass-dim)}
.nm:hover,.nm.pv-on{border-bottom-color:var(--brass);color:var(--brass);text-decoration:none}
/* name previews: a small card over a linked name (hover, or first tap on a touch screen) */
.pv{position:absolute;z-index:40;width:min(290px,calc(100vw - 24px));background:var(--plate-hi);border:1px solid var(--brass-dim);border-radius:8px;box-shadow:0 12px 32px rgba(0,0,0,.6);overflow:hidden;pointer-events:none;font-family:var(--body);font-size:.9rem;line-height:1.4}
.pv[hidden]{display:none}
.pv.touch{pointer-events:auto}
.pv-img{display:block;background:var(--plate);overflow:hidden}
.pv-img img{display:block;width:100%;height:100%;object-fit:cover}
.pv-img.wide{aspect-ratio:16/9;border-bottom:1px solid var(--rule)}
.pv.pv-face{display:grid;grid-template-columns:84px minmax(0,1fr);align-items:center}
.pv.pv-face[hidden]{display:none}
.pv-img.face{width:72px;height:72px;margin:10px 0 10px 10px;border-radius:50%;border:2px solid var(--brass-dim)}
.pv-body{padding:10px 12px;display:grid;gap:3px;min-width:0}
.pv-t{font-family:var(--display);font-weight:700;font-size:1.15rem;line-height:1.1;color:var(--ink)}
.pv-s{font-family:var(--label);font-size:.78rem;letter-spacing:.06em;color:var(--brass)}
.pv-x{color:var(--dim)}
.pv-open{display:inline-block;margin-top:4px;color:var(--brass);font-family:var(--label);letter-spacing:.06em;font-size:.82rem}
.archive li:target>details{background:linear-gradient(90deg,rgba(207,166,95,.10),transparent 70%)}
.archive li:target>details>summary{color:var(--brass)}
.cast{display:grid;gap:8px;border-top:1px solid var(--rule);padding-top:12px}
/* drawn things: tree glyphs, rank rings, tier seals, tally marks, mood embers, the d20, the keepsake shelf. Their colours are
   drawn into the SVG itself (build_site.py → PAL), so they never render black under an older stylesheet; these rules only place them. */
.tree h3{display:flex;align-items:center;gap:8px}
.tg,.rring,.seal,.d20,.told,.km{flex:none}
.seal{vertical-align:middle}
.seal-row{display:flex;align-items:center;gap:10px}
.chron li.sealed-row{grid-template-columns:auto minmax(0,1fr);gap:2px 10px;align-items:center}
.sealed-row>div{display:grid;gap:2px}
.tally{vertical-align:-2px;margin-left:3px}
.works-chip{display:inline-flex;align-items:center;gap:2px}
.mood{vertical-align:-3px;margin-right:4px}
.roll-top .d20{margin-right:2px}
.shelf{list-style:none;margin:0;padding:0 6px;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}
.slot{display:grid;gap:5px;justify-items:center;align-content:start;text-align:center;border:1px solid var(--rule);border-radius:6px 6px 2px 2px;padding:12px 8px 10px;min-height:124px;background:linear-gradient(180deg,var(--plate-hi),var(--plate))}
.slot.kept{border-color:var(--brass-dim);box-shadow:inset 0 0 18px rgba(207,166,95,.07)}
.slot.pending{border-style:dashed;border-color:var(--brass-dim)}
.slot.blank{border-style:dotted;background:rgba(0,0,0,.18);opacity:.5}
.slot b{font-family:var(--display);font-weight:700;font-size:1.05rem;line-height:1.1;color:var(--ink)}
.slot b a{color:var(--brass)}
.slot .lbl{font-size:.7rem;line-height:1}
.slot .m{font-size:.78rem;color:var(--dim);line-height:1.3}
.slot .src{font-size:.74rem;color:var(--faint)}
.shelf-ledge{height:7px;margin:-2px 0 0;border-radius:0 0 4px 4px;background:linear-gradient(180deg,var(--leather),#2a2016);box-shadow:0 3px 6px rgba(0,0,0,.4)}
.shelf-note{margin-top:10px}
@media (max-width:440px){.shelf{grid-template-columns:repeat(2,minmax(0,1fr))}.slot.blank.wide{display:none}}
.keeps{list-style:none;margin:0;padding:0;display:grid;gap:10px}
.keep{display:grid;gap:3px;border-left:2px solid var(--brass-dim);padding-left:12px}
.keep b{font-family:var(--display);font-size:1.15rem;color:var(--brass)}
.keep .src{font-size:.82rem;color:var(--faint)}
.reader .when{font-style:italic;color:var(--dim);font-size:17px}
.pager{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;border-top:1px solid var(--rule);padding-top:14px}
.pager a{display:grid;gap:2px;align-content:start;color:var(--ink)}
.pager a.next{text-align:right}
.pager .lbl{font-size:.75rem}
/* songs: a small play button where the story sings (site.js plays it in place), the browser's player in the Codex */
.song{display:inline-flex;align-items:center;gap:6px;vertical-align:.1em;min-height:26px;padding:3px 11px 3px 8px;border:1px solid var(--brass-dim);border-radius:999px;
  font-family:var(--label);font-style:normal;font-size:.8rem;letter-spacing:.06em;line-height:1;color:var(--brass);white-space:nowrap;
  background:linear-gradient(90deg,rgba(207,166,95,.22) var(--p,0%),transparent var(--p,0%))}
.song:hover{text-decoration:none;border-color:var(--brass)}
.song .sg-i{width:11px;height:11px;fill:currentColor;flex:none}
.song .sg-pause,.song.on .sg-play{display:none}
.song.on .sg-pause{display:inline}
.song.on{border-color:var(--brass)}
.song.compact{width:26px;height:26px;padding:0;justify-content:center;margin-left:4px}
.reader blockquote p.song-cue{font-size:inherit}
.song-dock{position:fixed;right:12px;bottom:12px;z-index:30;display:flex;align-items:center;gap:8px;max-width:calc(100vw - 24px);padding:6px 6px 6px 8px;
  background:var(--plate-hi);border:1px solid var(--brass-dim);border-radius:999px;box-shadow:0 8px 24px rgba(0,0,0,.5);font-family:var(--label);font-size:.82rem;letter-spacing:.06em;color:var(--ink)}
.song-dock[hidden]{display:none}
.song-dock .song{min-height:30px}
.song-dock .x{width:28px;height:28px;border:0;border-radius:50%;background:transparent;color:var(--dim);font-size:1.2rem;line-height:1;cursor:pointer}
.song-dock .x:hover{color:var(--ink)}
.codex-song{margin:2px 0 6px;display:grid;gap:6px}
.codex-song figcaption{font-family:var(--label);letter-spacing:.06em;font-size:.85rem;color:var(--brass)}
.codex-song audio{width:100%;max-width:440px;height:40px}
.archive summary .song-tag{flex:none;color:var(--brass);margin-right:8px;font-size:1rem;line-height:1}

@media (prefers-reduced-motion:reduce){
  html,html:focus-within{scroll-behavior:auto}
  .rp-knot.on{animation:none}
  .mp-ring{animation:none;opacity:.6}
  .bar>i{transition:none}
  .mast,.panel>summary::after{transition:none}
}
"""

JS = r"""/* THE UNKNEELING — small helpers. Every page works without this file. */
(function(){
"use strict";
var root = document.documentElement;
/* reading progress (chapter pages carry the bar) */
var bar = document.querySelector(".progress>i");
if (bar) {
  var tick = function(){
    var max = root.scrollHeight - root.clientHeight;
    bar.style.width = (max > 0 ? Math.min(100, 100 * root.scrollTop / max) : 0).toFixed(1) + "%";
  };
  window.addEventListener("scroll", tick, {passive:true}); tick();
}
/* the masthead slides away while reading down and comes back on the way up (the progress bar stays). A jump to a
   heading on the page puts it away first and holds it there while the page moves, so the heading lands in sight;
   scroll-padding in site.css matches whichever way the masthead is. */
var mast = document.querySelector(".mast"), holdUntil = 0;
var mastAway = function(on){ root.classList.toggle("mast-away", on); };
if (mast) {
  var lastY = window.pageYOffset;
  var measure = function(){ root.style.setProperty("--mast-h", mast.offsetHeight + "px"); };
  measure(); window.addEventListener("resize", measure);
  window.addEventListener("scroll", function(){
    var y = window.pageYOffset, dy = y - lastY;
    lastY = y;
    if (Date.now() < holdUntil) { return; }
    if (y <= mast.offsetHeight) { mastAway(false); }
    else if (dy > 6) { mastAway(true); }
    else if (dy < -6) { mastAway(false); }
  }, {passive:true});
  mast.addEventListener("focusin", function(){ mastAway(false); });
}
var hold = function(){ if (mast) { mastAway(true); holdUntil = Date.now() + 1000; } };
/* a link to a place on this same page: the masthead goes first, then the browser jumps */
document.addEventListener("click", function(e){
  var a = e.target.closest && e.target.closest("a[href*='#']");
  if (!a || e.defaultPrevented || a.hasAttribute("data-pv-t") || a.origin !== location.origin || a.pathname !== location.pathname || !a.hash) { return; }
  var t = document.getElementById(decodeURIComponent(a.hash.slice(1)));
  if (t) { hold(); }
});
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
/* picture zoom: a link with data-zoom opens its picture in a full-screen dialog (without this file the link opens the picture) */
var zoomLinks = document.querySelectorAll("a[data-zoom]");
if (zoomLinks.length && typeof HTMLDialogElement === "function") {
  var dlg = document.createElement("dialog");
  dlg.className = "zoom";
  dlg.innerHTML = '<button class="x" type="button" aria-label="Close">×</button><img alt="">';
  document.body.appendChild(dlg);
  var big = dlg.querySelector("img");
  dlg.addEventListener("click", function(){ dlg.close(); });
  dlg.addEventListener("close", function(){ big.removeAttribute("src"); });
  Array.prototype.forEach.call(zoomLinks, function(a){
    a.addEventListener("click", function(e){
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.button) { return; }
      e.preventDefault();
      var img = a.querySelector("img");
      big.src = a.getAttribute("href");
      big.alt = img ? img.alt : "";
      dlg.showModal();
    });
  });
}
/* name previews: a linked name in the story (data-pv-t) shows a small card with its picture, if it has one, and one
   line. Hover or keyboard focus on a desktop; on a touch screen the first tap shows the card and the second (or Open)
   follows the link. Without this file every name is a plain link. */
var pvLinks = document.querySelectorAll("a[data-pv-t]");
if (pvLinks.length) {
  var fine = !!(window.matchMedia && window.matchMedia("(hover: hover) and (pointer: fine)").matches);
  var card = document.createElement("div");
  card.className = "pv"; card.id = "pv"; card.setAttribute("role", "tooltip"); card.hidden = true;
  document.body.appendChild(card);
  var cur = null, timer = null;
  var el = function(tag, cls, text){ var n = document.createElement(tag); if (cls) { n.className = cls; } if (text) { n.textContent = text; } return n; };
  var place = function(a){
    var r = a.getBoundingClientRect(), w = card.offsetWidth, h = card.offsetHeight, vw = document.documentElement.clientWidth;
    var x = Math.min(Math.max(8, r.left), vw - w - 8), y = r.bottom + 8;
    if (y + h > window.innerHeight - 8 && r.top - h - 8 > 0) { y = r.top - h - 8; }
    card.style.left = (x + window.pageXOffset) + "px"; card.style.top = (y + window.pageYOffset) + "px";
  };
  var hide = function(){
    clearTimeout(timer);
    if (cur) { cur.classList.remove("pv-on"); cur.removeAttribute("aria-describedby"); }
    cur = null; card.hidden = true;
  };
  var show = function(a, touch){
    clearTimeout(timer);
    if (cur && cur !== a) { cur.classList.remove("pv-on"); cur.removeAttribute("aria-describedby"); }
    cur = a; a.classList.add("pv-on"); a.setAttribute("aria-describedby", "pv");
    while (card.firstChild) { card.removeChild(card.firstChild); }
    var src = a.getAttribute("data-pv-i"), kind = a.getAttribute("data-pv-k") === "face" ? "face" : "wide";
    card.className = "pv" + (src && kind === "face" ? " pv-face" : "") + (touch ? " touch" : "");
    if (src) {
      var box = el("span", "pv-img " + kind), img = el("img");
      img.src = src; img.alt = "";
      if (a.getAttribute("data-pv-f")) { img.style.objectPosition = a.getAttribute("data-pv-f"); }
      img.addEventListener("load", function(){ if (cur === a) { place(a); } });
      box.appendChild(img); card.appendChild(box);
    }
    var body = el("span", "pv-body");
    body.appendChild(el("span", "pv-t", a.getAttribute("data-pv-t")));
    if (a.getAttribute("data-pv-s")) { body.appendChild(el("span", "pv-s", a.getAttribute("data-pv-s"))); }
    if (a.getAttribute("data-pv-x")) { body.appendChild(el("span", "pv-x", a.getAttribute("data-pv-x"))); }
    if (touch) { var go = el("a", "pv-open", "Open →"); go.href = a.href; body.appendChild(go); }
    card.appendChild(body);
    card.hidden = false; place(a);
  };
  Array.prototype.forEach.call(pvLinks, function(a){
    if (fine) {
      a.addEventListener("mouseenter", function(){ clearTimeout(timer); timer = setTimeout(function(){ show(a, false); }, 90); });
      a.addEventListener("mouseleave", function(){ clearTimeout(timer); timer = setTimeout(hide, 90); });
      a.addEventListener("focus", function(){ show(a, false); });
      a.addEventListener("blur", hide);
    } else {
      a.addEventListener("click", function(e){ if (cur !== a) { e.preventDefault(); show(a, true); } });
    }
  });
  document.addEventListener("click", function(e){ if (cur && !e.target.closest("a[data-pv-t]") && !e.target.closest(".pv")) { hide(); } });
  document.addEventListener("keydown", function(e){ if (e.key === "Escape") { hide(); } });
  window.addEventListener("resize", hide);
}
/* songs: a link with data-song plays its song in place, one song at a time (the Codex's players included); press it
   again to pause. While it plays out of sight a small dock keeps a pause button in reach. Without this file the link
   opens the song. */
var songLinks = document.querySelectorAll("a[data-song]");
var players = document.querySelectorAll("audio");
var hushPlayers = function(except){ Array.prototype.forEach.call(players, function(p){ if (p !== except && !p.paused) { p.pause(); } }); };
if (songLinks.length && typeof Audio === "function") {
  var tune = new Audio(), from = null, inView = true;
  tune.preload = "none";
  var dock = document.createElement("div");
  dock.className = "song-dock"; dock.hidden = true;
  dock.innerHTML = '<a class="song" href="#" role="button" aria-pressed="true"><svg class="sg-i" viewBox="0 0 16 16" aria-hidden="true">' +
    '<path class="sg-play" d="M4 2.2v11.6L13.4 8z"/><path class="sg-pause" d="M3.5 2.5h3v11h-3zm6 0h3v11h-3z"/></svg><span class="sg-t"></span></a>' +
    '<button class="x" type="button" aria-label="Stop">×</button>';
  document.body.appendChild(dock);
  var dockBtn = dock.querySelector(".song");
  var watch = typeof IntersectionObserver === "function" ? new IntersectionObserver(function(es){
    es.forEach(function(en){ if (en.target === from) { inView = en.isIntersecting; } });
    paint();
  }) : null;
  var paint = function(){
    var on = !!from && !tune.paused;
    Array.prototype.forEach.call(songLinks, function(a){
      var me = a === from;
      a.classList.toggle("on", me && on);
      a.setAttribute("aria-pressed", String(me && on));
      if (!me) { a.style.removeProperty("--p"); }
    });
    dockBtn.classList.toggle("on", on);
    dockBtn.setAttribute("aria-pressed", String(on));
    dockBtn.setAttribute("aria-label", (on ? "Pause " : "Play ") + (from ? from.getAttribute("data-song") : ""));
    dock.hidden = !from || (inView && !!watch);
  };
  var stop = function(){
    tune.pause();
    if (from && watch) { watch.unobserve(from); }
    if (from) { from.style.removeProperty("--p"); }
    from = null; inView = true; dockBtn.style.removeProperty("--p"); paint();
  };
  var toggle = function(){
    if (!tune.paused) { tune.pause(); return; }
    hushPlayers(null);
    var pr = tune.play();
    if (pr && pr.catch) { pr.catch(paint); }
  };
  Array.prototype.forEach.call(songLinks, function(a){
    a.setAttribute("role", "button");
    a.setAttribute("aria-pressed", "false");
    a.addEventListener("click", function(e){
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.button) { return; }
      e.preventDefault();
      if (from === a) { toggle(); return; }
      stop();
      from = a; tune.src = a.getAttribute("href");
      dock.querySelector(".sg-t").textContent = a.getAttribute("data-song");
      if (watch) { watch.observe(a); }
      toggle();
    });
  });
  dockBtn.addEventListener("click", function(e){ e.preventDefault(); toggle(); });
  dock.querySelector(".x").addEventListener("click", stop);
  tune.addEventListener("play", paint);
  tune.addEventListener("pause", paint);
  tune.addEventListener("ended", stop);
  tune.addEventListener("timeupdate", function(){
    if (!from || !tune.duration) { return; }
    var p = (100 * tune.currentTime / tune.duration).toFixed(1) + "%";
    from.style.setProperty("--p", p); dockBtn.style.setProperty("--p", p);
  });
  Array.prototype.forEach.call(players, function(p){ p.addEventListener("play", function(){ tune.pause(); hushPlayers(p); }); });
} else {
  Array.prototype.forEach.call(players, function(p){ p.addEventListener("play", function(){ hushPlayers(p); }); });
}
/* a link to a folded entry or section (a Codex entry, a panel on Darrow's page) opens it, and every jump to a place on
   a page lands below the masthead's spot with the masthead put away */
var openTarget = function(){
  var id = decodeURIComponent(location.hash.slice(1)), t = id && document.getElementById(id);
  if (!t) { return; }
  var d = t.tagName === "DETAILS" ? t : t.querySelector(":scope > details");
  if (d && !d.open) { d.open = true; }
  for (var p = t.parentElement; p; p = p.parentElement) { if (p.tagName === "DETAILS" && !p.open) { p.open = true; } }
  hold();
  t.scrollIntoView({block: "start", behavior: "instant"});
};
openTarget();
window.addEventListener("hashchange", openTarget);
/* the page may still grow or shrink once its fonts and pictures arrive: until the reader moves, land on the target again */
var moved = false;
["wheel", "touchstart", "keydown"].forEach(function(t){ window.addEventListener(t, function(){ moved = true; }, {passive:true, once:true}); });
var settle = function(){ if (!moved && location.hash) { openTarget(); } };
if (document.fonts && document.fonts.ready) { document.fonts.ready.then(settle); }
window.addEventListener("load", settle);
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
    for k, src in site.assets.items():
        p = tmp / k
        p.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, p)
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
    n_songs = sum(1 for k in site.assets if Path(k).suffix.lower() in AUDIO_TYPES)
    n_img = sum(1 for k in site.assets if Path(k).suffix.lower() in IMAGE_TYPES and not k.startswith("art/thumbs/") and "/" in k)
    print(f"site built: {n_pages} pages, {len(site.chars)} characters, {len(site.chapters)} chapters, {len(site.tales)} tale{'' if len(site.tales) == 1 else 's'}, {n_img} image{'' if n_img == 1 else 's'}"
          + (f", {n_songs} song{'' if n_songs == 1 else 's'}" if n_songs else "") + " → docs/" + (
        f"  (with {len(PROBLEMS)} problem(s), forced)" if PROBLEMS else "  · all checks passed"))
    if site.thumb_missing:
        print(f"note: {len(site.thumb_missing)} picture(s) have no current small copies, so the site loads them at full size: "
              f"run python3 engine/thumbs.py ({', '.join(sorted(site.thumb_missing))})")
    if PROBLEMS:
        for p in PROBLEMS:
            print("  - " + p, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
