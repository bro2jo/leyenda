#!/usr/bin/env python3
"""THE UNKNEELING — the site builder. Renders the reader-facing site into docs/ from the Chronicle only.

Reads (and nothing else):
  saga/chronicle/*.md                      the story, by chapter
  saga/characters/*.json                   the cast, as the page has shown it
  saga/state/world.json, places.json, factions.json, darrow.json, bearing.json, codex.md, codex_art.json, chapters.csv, rolls.csv,
  looks.json                               (his finished looks, for the Wardrobe; world.json → tether: the Tether stages
                                           the page has paid, which open the Wardrobe's pieces for the two of them)
  engine/rules.json                        game data (knots, arts, ranks)
  engine/site/                             the stylesheet and the scripts (site.css, site.js, forge.js), published as they are
  engine/wardrobe.json                     the Wardrobe's pieces, what opens each, the references and the image prompt
                                           (engine/wardrobe.md says how each field works),
                                           the sets and the Collection's ranks (darrow/collection.html)
  saga/art/                                images and songs the user supplies, published as files when places.json names one
                                           or factions.json names one (image, image_alt, image_caption, image_focus; only
                                           for an entry already on the page), or codex_art.json names one for a codex.md
                                           entry (same keys plus name) or a character file does (portrait,
                                           portrait_alt, portrait_focus, portrait_zoom for the small round copies,
                                           portrait_label and portraits_earlier: a look from an earlier Book the
                                           character page's frame swipes back to). Every picture sits
                                           in a fixed frame (places 16:9, portraits square) and is cropped to fit, never
                                           stretched; *_focus ("50% 30%") picks the crop's centre; tap shows it whole.
                                           A song (saga/art/songs/, codex_art.json audio + audio_title) plays in its Codex
                                           entry and from a small button in the story where the page sings it.
                                           Small pictures use the copies in saga/art/thumbs/ (engine/thumbs.py; a missing or
                                           stale copy falls back to the picture, with a note); the full file loads only when
                                           an entry is opened or a picture tapped. saga/art/site/: the favicon's bitmaps.
                                           saga/art/arts/<art id>.webp (or .png, .jpg): an Art's card picture, found by its
                                           name, shown on Darrow's page once the Art has a rank.
                                           saga/art/looks/: his finished looks (saga/state/looks.json) and the Wardrobe's
                                           references (engine/wardrobe.json), on the Wardrobe page (darrow/wardrobe.html);
                                           every piece, the sets and his rank on the Collection (darrow/collection.html).
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
import datetime as dt
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
WARDROBE = ROOT / "engine" / "wardrobe.json"   # the Wardrobe's pieces and what opens each; the finished looks are saga/state/looks.json
SITE_SRC = ROOT / "engine" / "site"   # the stylesheet and the scripts, published as they are (site.css, site.js, forge.js)
CSS, JS, FORGE_JS = ((SITE_SRC / n).read_text(encoding="utf-8") for n in ("site.css", "site.js", "forge.js"))
IMAGE_TYPES = {".webp", ".png", ".jpg", ".jpeg"}
IMAGE_MAX_BYTES = 3 * 1024 * 1024
AUDIO_TYPES = {".mp3", ".m4a", ".ogg", ".opus"}
AUDIO_MAX_BYTES = 10 * 1024 * 1024
READ_ALLOW = [CHRON, CHARS, ART, STATE / "world.json", STATE / "places.json", STATE / "factions.json",
              STATE / "darrow.json", STATE / "bearing.json", STATE / "codex.md", STATE / "codex_art.json", STATE / "chapters.csv",
              STATE / "rolls.csv", RULES, WARDROBE, STATE / "looks.json"]

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
    return uslt_lines(path.read_bytes())


def uslt_lines(b):
    """The lyric lines in an MP3's bytes (ID3v2 USLT frames), or None. Shared with `saga.py songs`, which holds a
    track waiting GM-side to the same check the build will make once it is released."""
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
       "ink": "#E8E2D4", "dim": "#9AA2AE", "faint": "#646D79", "raw": "#262D37", "plate": "#161B22", "t3": "#A86B3C", "t4": "#7A4D86",
       "t4_text": "#A77FB5", "t5": "#4062A3", "t6": "#8BB2D3", "t2": "#D9AE5F", "night": "#0F1217", "leather": "#4A3826", "rule": "#2B323D"}
SVG_LABEL_FONT = "Alegreya Sans SC, Alegreya Sans, Segoe UI, sans-serif"
SVG_DISPLAY_FONT = "Grenze Gotisch, Georgia, serif"


def svg_tree(tree, size=22):
    """A glyph per Art tree: a sword, two footprints, three breaths of wind, a looped rope, an eye, a stone in flight."""
    body = {
        "Blade": '<path d="M12 2.5 L14.2 6 L14.2 15.5 L9.8 15.5 L9.8 6 Z M6.5 15.8 L17.5 15.8 M12 16 L12 20.2"/><circle cx="12" cy="21.4" r="1.2"/>',
        "Footing": f'<g fill="{PAL["brass"]}" stroke="none"><ellipse cx="8" cy="13.2" rx="2.9" ry="3.6"/><ellipse cx="8" cy="19.6" rx="2.1" ry="1.9"/><ellipse cx="16" cy="5.7" rx="2.9" ry="3.6"/><ellipse cx="16" cy="12.1" rx="2.1" ry="1.9"/></g>',
        "Breath": '<path d="M4 8 H13.5 a2.5 2.5 0 1 0 -2.5 -2.5 M4 13 H17.5 a2.5 2.5 0 1 1 -2.5 2.5 M4 18 H10.5 a2 2 0 1 0 -2 -2"/>',
        "Binding": '<path d="M2 17 C6.5 17 7.5 5 12.5 5 C18.5 5 18.5 13.5 12.5 13.5 C8 13.5 9 17 22 17"/>',
        "Insight": '<path d="M3 12 C8 5 16 5 21 12 C16 19 8 19 3 12 Z"/><circle cx="12" cy="12" r="3"/>',
        "Cast": '<path d="M3 20.5 Q6.5 9.5 13 8.2" stroke-dasharray="2 2.6"/><circle cx="17" cy="8" r="3.4"/>',
    }.get(tree, '<circle cx="12" cy="12" r="7"/>')
    return (f'<svg class="tg" viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="{PAL["brass"]}" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{body}</svg>')


def svg_lock(size=10):
    """A small padlock: a sealed Art's card carries it where the rank's numeral would be."""
    return (f'<svg class="lk" viewBox="0 0 12 12" width="{size}" height="{size}" aria-hidden="true">'
            f'<path d="M3.8 5.6 V4.1 a2.2 2.2 0 0 1 4.4 0 V5.6" fill="none" stroke="{PAL["dim"]}" stroke-width="1.4"/>'
            f'<rect x="2.2" y="5.4" width="7.6" height="5.6" rx="1.1" fill="{PAL["dim"]}"/></svg>')


def rank_ring(rank, n, frac=0.0, label="", size=32, sealed=False):
    """An Art's rank as a ring of n segments: the filled ones its rank, the next one filling with practice; the numeral inside.
    Grey while the Art is sealed (its rank banked)."""
    import math
    r, c = 14, 18
    circ = 2 * math.pi * r
    step, gap = circ / max(n, 1), 3.0
    on = PAL["faint"] if sealed else PAL["brass"]
    part = PAL["faint"] if sealed else PAL["brass_dim"]
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
           f'font-weight="700" fill="{PAL["dim"] if sealed else PAL["ink"]}">{roman(rank) if rank else "·"}</text>')
    return f'<svg class="rring" viewBox="0 0 36 36" width="{size}" height="{size}" role="img" aria-label="{esc(label or f"rank {rank} of {n}")}">{"".join(segs)}{num}</svg>'


SEAL_DEVICES = {
    "triumph": '<circle cx="24" cy="24" r="4.5"/><path d="M24 8 L24 14 M24 34 L24 40 M8 24 L14 24 M34 24 L40 24 M12.7 12.7 L17 17 M31 31 L35.3 35.3 M35.3 12.7 L31 17 M17 31 L12.7 35.3"/>',
    "hardwon": '<path d="M24 9 L24 31 M17 31 L31 31 M24 31 L24 38 M20.5 13.5 L24 9 L27.5 13.5 M24 20 L27 23"/>',
    "costly": '<path d="M24 11 L24 37 M19 37 L29 37 M12 20 L36 16 M12 20 L8 29 L16 29 Z M36 16 L32 25 L40 25 Z"/>',
    "setback": '<path d="M15 19 L24 29 L33 19"/><path d="M24 6 L22 11 L25.5 14.5"/>',
    "whole": '<path d="M13 24 C13 15 35 15 35 24 C35 33 13 33 13 24 Z M8 24 H13 M35 24 H40"/>',
}


def _seal(kind, col, size, label, cls="", dashed=False):
    """A wax seal: a plate disc with a coloured rim, a dotted inner ring and a device. dashed: the rim is broken, for a
    seal not yet set (a chapter still running)."""
    rim = ' stroke-dasharray="4 3"' if dashed else ""
    return (f'<svg class="seal {kind}{(" " + cls) if cls else ""}" viewBox="0 0 48 48" width="{size}" height="{size}" role="img" aria-label="{esc(label)}">'
            f'<circle cx="24" cy="24" r="21" fill="{PAL["plate"]}" stroke="{col}" stroke-width="2"{rim}/>'
            f'<circle cx="24" cy="24" r="17.5" fill="none" stroke="{col}" stroke-opacity=".55" stroke-width="1" stroke-dasharray="2 2.5"/>'
            f'<g fill="none" stroke="{col}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">{SEAL_DEVICES[kind]}</g></svg>')


def svg_seal(tier, size=44, open_=False):
    """A chapter's tier as a wax seal: a sunburst (Triumph), a notched sword (Hard-won), a tipped balance (Costly), a cracked
    ring (Setback). open_: the chapter is still running, so the rim is not yet closed."""
    kind = TIER_SEAL.get(tier)
    if not kind:
        return ""
    col = PAL["ember"] if kind in ("costly", "setback") else PAL["brass"]
    label = TIER_SO_FAR.get(tier, tier) if open_ else TIER_DONE.get(tier, tier)
    return _seal(kind, col, size, label, "open" if open_ else "", dashed=open_)


def seal_whole(size=28):
    """The seal on a set of the Wardrobe once every piece of it is his: a knot in brass."""
    return _seal("whole", PAL["brass"], size, "whole")


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


# The metal of each rank, in the order of rules.json → levels.ranks (CSS .metal-*): the crest, the portrait's frame, the
# plate's rivets and Darrow's round picture on the Now page take it. A rank past the end of this list keeps the last metal.
METALS = ("iron", "brass", "steel", "silver", "ember", "gold", "white-gold")
# An Art card's frame, by its rank I-V (rules.json → art_ranks); bronze, not brass, so rank II never reads as gold. A sealed
# Art is grey. Violet is kept for a tier above gold (a legendary Art), should one come: nothing else on the Arts panel uses it.
ART_METALS = ("iron", "bronze", "steel", "silver", "gold")


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


# The kinds of place drawn as a label on the terrain, never as a marker.
MAP_TERRAIN = ("region", "forest", "waste", "mountains", "river", "road", "hills", "stair")


def map_point(p):
    """True when a place is drawn as a marker on the map (a town, a house, a ford), not as a label on the terrain."""
    return bool(p) and p.get("draw") is not False and p.get("kind") not in MAP_TERRAIN


def route_legs(route, P):
    """places.json → route as legs of (x, y): each entry a place id or an [x, y] waypoint; null ends a leg and starts the next."""
    legs, leg = [], []
    for r in route:
        if r is None:
            if leg:
                legs.append(leg)
            leg = []
        elif isinstance(r, (list, tuple)) and len(r) == 2:
            leg.append((r[0], r[1]))
        elif isinstance(r, str) and r in P:
            leg.append((P[r]["x"], P[r]["y"]))
    if leg:
        legs.append(leg)
    return legs


# ------------------------------------------------------------ the map's terrain (drawn here, the same every build)
# One 400x300 country: the sea and its coast in the west, the Greywater across the north, the Thornwild in the east,
# the Wend from the forest to the sea, the Holloway down the middle. Only terrain: nothing here names a place, and a
# feature the page has not shown stays unlabelled (the grey waste in the south-east). Colours are written on the
# drawing itself, so it never depends on the stylesheet; the labels, the markers and the route keep their CSS classes.
MAP_COAST = "M58 0 C48 40 70 70 56 110 C44 150 66 190 52 230 C42 260 62 280 54 300"
# The Wend rises in the western Greywater and runs south, then east across the Lowmarch past the Wend landing; at the
# border it turns north along the Thornwild's edge (the Lowmarch on its west bank, the wood on its east), past Harrow Ford,
# and goes east into the Thornwild and out of the map. Points along its course, source first.
MAP_WEND_COURSE = [(112, 78), (114, 98), (118, 122), (122, 148), (126, 172), (134, 192), (150, 207), (172, 213), (192, 214),
                   (211, 212), (230, 212), (250, 208), (272, 212), (292, 206), (304, 194), (310, 174), (312, 152), (310, 128),
                   (307, 104), (306, 90), (314, 80), (332, 76), (354, 79), (378, 74), (406, 72)]
# the river road: down the Wend's west bank from the ford to the bend, where the barges take over
MAP_RIVER_ROAD = [(300, 106), (302, 126), (304, 150), (303, 172), (298, 190), (288, 200)]
MAP_STREAM = "M247 156 C252 168 244 182 251 196 C254 202 252 206 251 209"
MAP_THORNWILD = [(320, 94), (336, 90), (354, 92), (372, 89), (392, 92), (408, 90), (408, 214), (392, 210), (374, 214),
                 (356, 209), (338, 214), (324, 208), (318, 192), (321, 176), (317, 160), (320, 144), (317, 126), (320, 110)]
MAP_WASTE = [(324, 222), (344, 218), (366, 224), (388, 222), (392, 240), (390, 270), (384, 288), (356, 286), (336, 280), (320, 268), (316, 246)]
MAP_TARN = [(213, 151), (216, 145), (222, 141), (232, 139), (244, 140), (252, 144), (254, 150), (251, 156), (243, 159), (230, 159), (220, 157)]
# the Holloway: from the winch-house over the rise, down the Elbow (the hairpin above the tarn) past Coldmere to the Wend
# landing, across the river, and on to Calden
MAP_HOLLOWAY = ("M214 118 C212 125 210 131 209 136 C208 140 203 140 203 143 C203 146 210 144 210 147 C210 150 206 150 206 153 "
                "C206 158 207 164 208 172 C209 186 212 200 211 212 C210 230 213 252 214 272")
MAP_STEPS = "M200 68 L212 74 L198 80 L212 86 L198 92 L212 98 L200 104 L214 110 L214 118"
# the Greywater: (x, base y, half width, height), back row first
MAP_PEAKS = [(128, 60, 12, 20), (152, 54, 12, 24), (176, 48, 11, 22), (228, 48, 12, 24), (254, 54, 12, 22), (278, 60, 11, 18),
             (116, 72, 11, 17), (140, 70, 13, 25), (164, 64, 13, 30), (188, 58, 12, 26), (206, 56, 15, 34),
             (232, 62, 13, 28), (258, 68, 13, 22), (282, 72, 10, 16)]
MAP_HILLS = [(70, 112, 1.0), (84, 106, .8), (96, 116, 1.05), (64, 126, .85), (82, 124, .9), (106, 104, .75)]
MAP_COPSES = [(98, 150, 6), (150, 252, 5), (262, 246, 5), (178, 118, 4), (96, 262, 4), (244, 102, 3), (276, 182, 3)]
MAP_TUFTS = (218, 96, 290, 134)  # the moor the drove road loops over, north and east of the tarn


def _rand(seed):
    s = [seed % 2147483647 or 1]

    def r():
        s[0] = (s[0] * 48271) % 2147483647
        return s[0] / 2147483647
    return r


def _inside(x, y, poly):
    c, j = False, len(poly) - 1
    for i in range(len(poly)):
        (xi, yi), (xj, yj) = poly[i], poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            c = not c
        j = i
    return c


def _f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".") if abs(v - round(v)) > 1e-9 else str(int(round(v)))


def _smooth(pts):
    """A closed curve through the points (Catmull-Rom as cubic Béziers)."""
    n = len(pts)
    d = f"M{_f(pts[0][0])} {_f(pts[0][1])}"
    for i in range(n):
        p0, p1, p2, p3 = pts[(i - 1) % n], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{_f(c1[0])} {_f(c1[1])} {_f(c2[0])} {_f(c2[1])} {_f(p2[0])} {_f(p2[1])}"
    return d + " Z"


def _scallop(poly, step=6.5, bulge=2.4):
    """A wood's edge: small outward arcs all round the polygon, like the crowns of its outer trees."""
    pts = []
    for i, a in enumerate(poly):
        b = poly[(i + 1) % len(poly)]
        k = max(1, round(((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** .5 / step))
        pts += [(a[0] + (b[0] - a[0]) * j / k, a[1] + (b[1] - a[1]) * j / k) for j in range(k)]
    d = f"M{_f(pts[0][0])} {_f(pts[0][1])}"
    for i, a in enumerate(pts):
        b = pts[(i + 1) % len(pts)]
        mx, my, dx, dy = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2, b[0] - a[0], b[1] - a[1]
        ln = (dx * dx + dy * dy) ** .5 or 1
        nx, ny = dy / ln, -dx / ln
        if _inside(mx + nx, my + ny, poly):
            nx, ny = -nx, -ny
        d += f" Q{_f(mx + nx * bulge * 2)} {_f(my + ny * bulge * 2)} {_f(b[0])} {_f(b[1])}"
    return d + " Z"


def _open_curve(pts):
    """An open curve through the points (Catmull-Rom as cubic Béziers): [(start, c1, c2, end)] per stretch."""
    out = []
    for i in range(len(pts) - 1):
        p0, p1, p2 = pts[max(i - 1, 0)], pts[i], pts[i + 1]
        p3 = pts[min(i + 2, len(pts) - 1)]
        out.append((p1, (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6),
                    (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6), p2))
    return out


def _curve_d(segs):
    return f"M{_f(segs[0][0][0])} {_f(segs[0][0][1])}" + "".join(
        f" C{_f(a[0])} {_f(a[1])} {_f(b[0])} {_f(b[1])} {_f(c[0])} {_f(c[1])}" for _, a, b, c in segs)


def _bez(seg, t):
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = seg
    u = 1 - t
    return (u ** 3 * x0 + 3 * u * u * t * x1 + 3 * u * t * t * x2 + t ** 3 * x3, u ** 3 * y0 + 3 * u * u * t * y1 + 3 * u * t * t * y2 + t ** 3 * y3)


MAP_WEND = _open_curve(MAP_WEND_COURSE)
MAP_WEND_PTS = [_bez(s, t / 8) for s in MAP_WEND for t in range(9)]


def _near_wend(x, y, d):
    return any((x - px) ** 2 + (y - py) ** 2 < d * d for px, py in MAP_WEND_PTS)


def map_label_box(p):
    """Roughly where a place's map label sits (x0, y0, x1, y1), so the trees and the tufts leave it a clearing."""
    text = p.get("label") or p["name"]
    kind = p.get("kind")
    if kind in MAP_TERRAIN:
        cw = 5.2 if kind in ("road", "stair", "river") else 7.4
        lines = text.split(" ", 1) if p.get("lines") == 2 and " " in text else [text]
        w, x, y = max(len(t) for t in lines) * cw, p["x"], p["y"] + 11 * (len(lines) - 1)
        anchor = p.get("anchor", "middle")
    else:
        w, x = len(text) * 6.2, p["x"]
        y = p["y"] + (4 if p.get("label_right") else 14 if p.get("label_below") else -11 if kind in ("city", "house") else -8)
        anchor = "start" if p.get("label_right") else "end" if x > 330 else ("start" if x < 70 else "middle")
        x += 9 if p.get("label_right") else 0
    x0 = x - w / 2 if anchor == "middle" else (x - w if anchor == "end" else x)
    return (x0 - 3, y - 11, x0 + w + 3, y + 4)


def map_roads():
    """What is drawn over any base: the river road, the Holloway and its bridge, the Steps, the stones at Harrow Ford."""
    rr = _curve_d(_open_curve(MAP_RIVER_ROAD))
    return ('<path d="M298 99 v6 M297 108 v5 M316 98 v6 M317 107 v6" stroke="#B4BBC6" stroke-width="1.5" stroke-linecap="round"/>'
            f'<path d="{rr}" fill="none" stroke="#7A6440" stroke-width=".8" stroke-dasharray="2 2.2" stroke-linecap="round"/>'
            f'<path d="{MAP_HOLLOWAY}" fill="none" stroke="#0E1116" stroke-width="2.6" stroke-linecap="round"/>'
            f'<path d="{MAP_HOLLOWAY}" fill="none" stroke="#9A7D4C" stroke-width="1" stroke-dasharray="3 2.4" class="mp-road"/>'
            '<path d="M207 209 h8 M207 215 h8" stroke="#B4BBC6" stroke-width="1" stroke-linecap="round"/>'
            f'<path d="{MAP_STEPS}" fill="none" stroke="#9AA2AE" stroke-width="1" stroke-linejoin="round" class="mp-steps"/>')


def map_painted(href):
    """A painted base (places.json → base_image): the picture fills the layout guide's frame, 450 x 300 from x = -25, so
    the map's 400 x 300 shows its middle; a little shade sits it on the dark page; the roads go over it."""
    return ('<defs><radialGradient id="mp-vig" cx="50%" cy="50%" r="75%"><stop offset=".55" stop-color="#000" stop-opacity="0"/>'
            '<stop offset="1" stop-color="#000" stop-opacity=".45"/></radialGradient></defs>'
            f'<image href="{href}" x="-25" y="0" width="450" height="300" preserveAspectRatio="none"/>'
            '<rect width="400" height="300" fill="#0F1217" opacity=".16"/><rect width="400" height="300" fill="url(#mp-vig)"/>'
            + map_roads())


def map_terrain(places):
    """The country under the labels, drawn: land, sea, mountains, wood, water, roads. Deterministic."""
    boxes = [map_label_box(p) for p in places if p.get("draw") is not False or p.get("kind") in MAP_TERRAIN]
    clear = lambda x, y, pad=0: not any(b[0] - pad <= x <= b[2] + pad and b[1] - pad <= y <= b[3] + pad for b in boxes)
    r = _rand(1117)
    o = []
    o.append('<defs>'
             '<radialGradient id="mp-land" cx="52%" cy="46%" r="70%"><stop offset="0" stop-color="#1A2028"/><stop offset=".65" stop-color="#161B22"/><stop offset="1" stop-color="#101318"/></radialGradient>'
             '<linearGradient id="mp-deep" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#0A1018"/><stop offset="1" stop-color="#122033"/></linearGradient>'
             '<radialGradient id="mp-vig" cx="50%" cy="50%" r="75%"><stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".38"/></radialGradient>'
             '<filter id="mp-grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" seed="7" stitchTiles="stitch"/>'
             '<feColorMatrix values="0 0 0 0 .9  0 0 0 0 .85  0 0 0 0 .75  0 0 0 .07 0"/></filter>'
             '<g id="mp-oak"><circle r="4" fill="#1F2B26" stroke="#0B100E" stroke-width=".8"/>'
             '<path d="M-3 -1 A3.1 3.1 0 0 1 1 -3" fill="none" stroke="#7E9B88" stroke-width=".8" stroke-linecap="round"/></g>'
             '<g id="mp-oak-s"><circle r="3.3" fill="#1D2924" stroke="#0B100E" stroke-width=".8"/>'
             '<path d="M-2.4 -.8 A2.5 2.5 0 0 1 .8 -2.4" fill="none" stroke="#7E9B88" stroke-width=".75" stroke-linecap="round"/></g>'
             '<g id="mp-pine"><path d="M0 -5.6 L3.3 2.2 L-3.3 2.2 Z" fill="#1B2722" stroke="#0B100E" stroke-width=".8" stroke-linejoin="round"/>'
             '<path d="M-.5 -3.9 L-1.9 -.6" stroke="#7E9B88" stroke-width=".7" stroke-linecap="round" opacity=".8"/></g>'
             '<g id="mp-hill"><path d="M-6.5 0 C-4.4 -6 4.4 -6 6.5 0" fill="#181D24" stroke="#8A929E" stroke-width=".9" stroke-linecap="round"/>'
             '<path d="M1.6 -3.6 L3.4 -.6 M3.4 -2.6 L4.9 -.4" stroke="#545D69" stroke-width=".6" stroke-linecap="round"/></g>'
             '<g id="mp-tuft"><path d="M-1.7 0 L-2.6 -2.1 M0 0 V-2.8 M1.7 0 L2.6 -2.1" stroke="#535C68" stroke-width=".6" stroke-linecap="round"/></g>'
             '<g id="mp-wave"><path d="M-6 0 q3 -2.4 6 0 t6 0" fill="none" stroke="#4A6FB0" stroke-width=".7" stroke-linecap="round"/></g>'
             '</defs>')
    # land and sea
    o.append('<rect width="400" height="300" fill="url(#mp-land)"/>')
    o.append(f'<path d="{MAP_COAST} L0 300 L0 0 Z" fill="url(#mp-deep)"/>')
    for dx, op in ((-3.5, .5), (-7.5, .3), (-12.5, .15)):  # the water lines along the shore
        o.append(f'<path d="{MAP_COAST}" transform="translate({dx} 0)" fill="none" stroke="#4062A3" stroke-width=".7" opacity="{op}"/>')
    o.append(f'<path d="{MAP_COAST}" fill="none" stroke="#5A7FBF" stroke-width="1.3"/>')
    for x, y in ((18, 40), (30, 92), (14, 146), (34, 176), (20, 222), (30, 268)):
        o.append(f'<use href="#mp-wave" x="{x}" y="{y}" opacity=".55"/>')
    # the moor above the tarn
    tufts = []
    for _ in range(70):
        x, y = 70 + r() * 240, 84 + r() * 196
        if (clear(x, y, 3) and not _inside(x, y, MAP_THORNWILD) and not _inside(x, y, MAP_WASTE) and not _near_wend(x, y, 6)
                and abs(x - 209) > 8 and not (MAP_TUFTS[0] < x < MAP_TUFTS[2] and MAP_TUFTS[1] < y < MAP_TUFTS[3]) and not _inside(x, y, MAP_TARN)):
            tufts.append(f'<use href="#mp-tuft" x="{_f(x)}" y="{_f(y)}" opacity=".7"/>')
    for _ in range(26):
        x, y = MAP_TUFTS[0] + r() * (MAP_TUFTS[2] - MAP_TUFTS[0]), MAP_TUFTS[1] + r() * (MAP_TUFTS[3] - MAP_TUFTS[1])
        if clear(x, y, 2) and not _inside(x, y, MAP_TARN) and abs(x - 212) > 6:
            tufts.append(f'<use href="#mp-tuft" x="{_f(x)}" y="{_f(y)}"/>')
    o.append("".join(tufts))
    # the grey waste: stippled, never named until the page names it
    dots = []
    for _ in range(420):
        x, y = 266 + r() * 114, 210 + r() * 80
        if _inside(x, y, MAP_WASTE) and clear(x, y):
            dots.append(f"M{_f(x)} {_f(y)}h0")
    o.append(f'<path d="{_smooth(MAP_WASTE)}" fill="#14171C" stroke="#4A5360" stroke-width=".6" stroke-dasharray="1.5 2.5"/>')
    o.append(f'<path d="{"".join(dots)}" stroke="#7D8692" stroke-width="1.05" stroke-linecap="round" opacity=".55"/>')
    # Edgemoor's hills
    o.append("".join(f'<use href="#mp-hill" transform="translate({x} {y}) scale({s})"/>' for x, y, s in MAP_HILLS + [(104, 84, .6), (122, 86, .55)]))
    # the Greywater: shaded on the east faces, snow on the tops; foothills under it
    pk = []
    for x, by, w, h in MAP_PEAKS:
        ax, ay = x + w * .08, by - h
        lx, rx = x - w, x + w
        pk.append(f'<path d="M{_f(lx)} {by} L{_f(ax)} {_f(ay)} L{_f(rx)} {by} Z" fill="#181D25"/>')
        pk.append(f'<path d="M{_f(ax)} {_f(ay)} L{_f(rx)} {by} L{_f(x + w * .25)} {by} L{_f(x + w * .02)} {_f(by - h * .5)} Z" fill="#0F1318"/>')
        hatch = "".join(f"M{_f(ax + (rx - ax) * t + 1)} {_f(ay + (by - ay) * t + .5)} L{_f(ax + (rx - ax) * t - w * .28)} {_f(ay + (by - ay) * t + h * .16)}" for t in (.45, .6, .75, .9))
        pk.append(f'<path d="{hatch}" stroke="#3E4652" stroke-width=".55" stroke-linecap="round"/>')
        sl = .3 if h > 20 else .24
        snow = (f"M{_f(ax)} {_f(ay)} L{_f(ax + (rx - ax) * sl)} {_f(ay + h * sl)} L{_f(ax + (rx - ax) * sl * .45)} {_f(ay + h * sl * .7)} "
                f"L{_f(ax)} {_f(ay + h * sl * 1.05)} L{_f(ax - (ax - lx) * sl * .5)} {_f(ay + h * sl * .75)} L{_f(ax - (ax - lx) * sl)} {_f(ay + h * sl)} Z")
        pk.append(f'<path d="{snow}" fill="#C9CED6" opacity=".82"/>')
        pk.append(f'<path d="M{_f(lx)} {by} L{_f(ax)} {_f(ay)} L{_f(rx)} {by}" fill="none" stroke="#A3ABB7" stroke-width=".95" stroke-linejoin="round" stroke-linecap="round"/>')
    o.append("".join(pk))
    o.append("".join(f'<use href="#mp-hill" transform="translate({x} {y}) scale({s})"/>' for x, y, s in
                     ((112, 76, .6), (130, 75, .55), (150, 74, .62), (176, 69, .5), (226, 67, .5), (244, 72, .6), (268, 75, .55), (288, 75, .5))))
    # the Thornwild: a scalloped edge, then the trees, back to front, with a clearing for its name and the river's course
    o.append(f'<path d="{_scallop(MAP_THORNWILD)}" fill="#131B18" stroke="#4E6658" stroke-width=".8" stroke-linejoin="round"/>')
    trees, y, row = [], 95.0, 0
    while y < 238:
        x = 306 + (row % 2) * 3.3
        while x < 410:
            jx, jy = x + (r() - .5) * 2.6, y + (r() - .5) * 2.2
            if (all(_inside(jx + dx, jy + dy, MAP_THORNWILD) for dx, dy in ((-2.5, 0), (2.5, 0), (0, -3), (0, 3)))
                    and not _near_wend(jx, jy, 5.6) and clear(jx, jy, 1.5)):
                v = r()
                trees.append((jy, jx, "pine" if v < .14 else "oak-s" if v < .45 else "oak"))
            x += 6.6
        y += 5.4
        row += 1
    for x, y, n in MAP_COPSES:  # small woods in the open country
        for _ in range(n):
            jx, jy = x + (r() - .5) * 12, y + (r() - .5) * 6
            if clear(jx, jy, 2) and not _near_wend(jx, jy, 5):
                trees.append((jy, jx, "pine" if r() < .3 else "oak-s"))
    o.append("".join(f'<use href="#mp-{kind}" x="{_f(x)}" y="{_f(y)}"/>' for y, x, kind in sorted(trees)))
    # the tarn at Coldmere and the Wend, wide at the sea and narrow in the wood
    o.append(f'<path d="{_smooth(MAP_TARN)}" fill="#0E1726" stroke="#5A7FBF" stroke-width="1"/>')
    o.append(f'<path d="{_smooth([(232 + (x - 235) * .7, 150 + (y - 150) * .62) for x, y in MAP_TARN])}" fill="none" stroke="#4062A3" stroke-width=".5" opacity=".5"/>')
    o.append(f'<path d="{MAP_STREAM}" fill="none" stroke="#4A6FB0" stroke-width=".9" stroke-linecap="round"/>')
    o.append(f'<path d="{_curve_d(MAP_WEND)}" fill="none" stroke="#4062A3" stroke-width="4.4" stroke-linecap="round" opacity=".22"/>')
    n = len(MAP_WEND)
    for i, seg in enumerate(MAP_WEND):  # narrow at its source in the hills, wide where it leaves the map
        o.append(f'<path d="{_curve_d([seg])}" fill="none" stroke="#5A7FBF" stroke-width="{1.1 + 1.9 * i / (n - 1):.2f}" stroke-linecap="round"/>')
    # Harrow Ford's stones, the river road, the Holloway and the Steps
    o.append(map_roads())
    # grain and shade over the whole country
    o.append('<rect width="400" height="300" filter="url(#mp-grain)"/><rect width="400" height="300" fill="url(#mp-vig)"/>')
    return "".join(o)


def map_frame():
    """The border and the compass, drawn over everything but the labels."""
    corners = "".join(f'<path d="M{x} {y - 3.2} L{x + 3.2} {y} L{x} {y + 3.2} L{x - 3.2} {y} Z" fill="#CFA65F"/>' for x, y in ((5, 5), (395, 5), (5, 295), (395, 295)))
    rose = ('<g class="mp-compass" transform="translate(372 34)">'
            '<circle r="10.5" fill="#12161C" fill-opacity=".7" stroke="#8A7044" stroke-width=".7"/><circle r="7.6" fill="none" stroke="#8A7044" stroke-width=".4"/>'
            '<path d="M0 -14 L2.6 0 L0 14 L-2.6 0 Z M-14 0 L0 2.6 L14 0 L0 -2.6 Z" fill="#8A7044"/>'
            '<path d="M0 -14 L2.6 0 L0 0 Z M14 0 L0 2.6 L0 0 Z M0 14 L-2.6 0 L0 0 Z M-14 0 L0 -2.6 L0 0 Z" fill="#CFA65F"/>'
            '<path d="M-6 -6 L1 0 L-6 6 M6 -6 L-1 0 L6 6" fill="none" stroke="#8A7044" stroke-width=".6" opacity=".8" transform="rotate(0)"/>'
            '<text y="-17" text-anchor="middle" fill="#CFA65F">N</text></g>')
    return (f'<rect x="3" y="3" width="394" height="294" fill="none" stroke="#8A7044" stroke-width=".9"/>'
            f'<rect x="6.5" y="6.5" width="387" height="287" fill="none" stroke="#8A7044" stroke-width=".35" opacity=".7"/>{corners}{rose}')


def map_label(p, text, cls):
    """A terrain label: straight, or bowed along a gentle arc when places.json gives it one ("arc": + bows up, - sags)."""
    x, y, anchor = p["x"], p["y"], p.get("anchor", "middle")
    arc = p.get("arc")
    if p.get("lines") == 2 and " " in text:  # two lines: the first word over the rest
        a, b = text.split(" ", 1)
        return (f'<text x="{x}" y="{y}" text-anchor="{esc(anchor)}" class="{cls}"><tspan x="{x}" class="sm">{a}</tspan>'
                f'<tspan x="{x}" dy="11">{b}</tspan></text>')
    if not arc:
        return f'<text x="{x}" y="{y}" text-anchor="{esc(anchor)}" class="{cls}">{text}</text>'
    half = max(40, len(p.get("label") or p["name"]) * 5)
    pid = f'mp-arc-{esc(p["id"])}'
    return (f'<path id="{pid}" d="M{x - half} {y} Q{x} {y - 2 * arc} {x + half} {y}" fill="none"/>'
            f'<text class="{cls}"><textPath href="#{pid}" startOffset="50%" text-anchor="middle">{text}</textPath></text>')


def svg_map(places, route, current_id, rel, base=None):
    """An original map of the story's country. Terrain is drawn here (map_terrain); places and the route come from
    places.json. The route's last leg is the road he is on now (bright; the legs before it fainter) and Darrow stands at
    its end. A place the page has named is a link to its Codex entry."""
    P = {p["id"]: p for p in places}
    cur = P.get(current_id)
    title = "Map of Darrow's country" + (f". Darrow: {cur.get('label') or cur['name']}" if cur else "")
    out = [f'<svg class="map" viewBox="0 0 400 300" aria-labelledby="map-t"><title id="map-t">{esc(title)}</title>',
           map_painted(base) if base else map_terrain(places)]

    def linked(p, inner):
        if not p.get("on_page"):
            return inner
        return f'<a href="{rel}codex/index.html#place-{esc(p["id"])}" class="mp-a">{inner}</a>'

    # the road so far, by legs: the one he is on is bright
    legs = route_legs(route, P)
    for i, leg in enumerate(legs):
        if len(leg) > 1:
            d = " ".join(f"{'M' if j == 0 else 'L'}{x} {y}" for j, (x, y) in enumerate(leg))
            out.append(f'<path d="{d}" class="mp-route{"" if i == len(legs) - 1 else " past"}" fill="none" stroke="#E2713B"/>')
    out.append(map_frame())
    # terrain labels, by kind: regions in spaced capitals, water in italic blue, roads in italic
    for p in places:
        kind = p.get("kind")
        if kind in MAP_TERRAIN:
            style = "water" if kind == "river" else "way" if kind in ("road", "stair") else "region"
            cls = f"mp-lbl {style}" + (" big" if p.get("big") else "") + ("" if p.get("on_page") else " faint")
            out.append(linked(p, map_label(p, esc(p.get("label") or p["name"]), cls)))
    for p in places:
        if not map_point(p):
            continue
        x, y = p["x"], p["y"]
        here = p["id"] == current_id
        kind = p.get("kind")
        cls = "mp-pt" + (" visited" if p.get("visited") else "") + (" current" if here else "") + ("" if p.get("on_page") else " faint")
        g = [f'<g class="{cls}">']
        if here:
            g.append(f'<circle cx="{x}" cy="{y}" r="9" class="mp-ring" fill="none" stroke="#E2713B"/>')
        if kind == "city":  # a walled town with a spire
            g.append(f'<path d="M{x - 6} {y + 4} V{y - 2} h1.8 v-2 h1.4 v2 h1.6 L{x} {y - 11} L{x + 1.2} {y - 2} h1.6 v-2 h1.4 v2 h1.8 V{y + 4} Z" '
                     f'class="mp-dot" fill="#7D8692" stroke="#0E1116" stroke-width=".8" stroke-linejoin="round"/>')
        elif kind == "house":  # a hall with its bell tower
            g.append(f'<path d="M{x - 6} {y + 4} V{y - 1} L{x - 2.5} {y - 4} L{x + 1} {y - 1} V{y + 4} Z M{x + 1} {y + 4} V{y - 5} L{x + 3} {y - 9} L{x + 5} {y - 5} V{y + 4} Z" '
                     f'class="mp-dot" fill="#7D8692" stroke="#0E1116" stroke-width=".8" stroke-linejoin="round"/>')
        elif kind == "landing":  # a jetty on the bank, its posts in the water
            g.append(f'<path d="M{x - 9} {y - 1.6} h7 v3.2 h-7 Z M{x - 7} {y + 1.6} v2.4 M{x - 3.6} {y + 1.6} v2.4" '
                     f'class="mp-dot" fill="#7D8692" stroke="#0E1116" stroke-width=".7"/>')
        else:
            g.append(f'<circle cx="{x}" cy="{y}" r="3.2" class="mp-dot" fill="#7D8692" stroke="#0E1116" stroke-width="1.1"/>')
        anchor = "end" if x > 330 else ("start" if x < 70 else "middle")
        dy = -11 if kind in ("city", "house") else -8
        dx = 0
        if p.get("label_below"):
            dy = 14
        if p.get("label_right"):
            anchor, dx, dy = "start", 9, 4
        if here:  # the current place sits clear of the terrain, to the right of its marker
            anchor, dx, dy = "start", 12, 4
        g.append(f'<text x="{x + dx}" y="{y + dy}" text-anchor="{anchor}" class="mp-lbl">{esc(p.get("label") or p["name"])}</text>')
        g.append("</g>")
        out.append(linked(p, "".join(g)))
    # Darrow, at the end of the road so far, when he is on a road or in open country rather than at a place with a marker
    if legs and not map_point(cur):
        x, y = legs[-1][-1]
        out.append(f'<g class="mp-here"><circle cx="{x}" cy="{y}" r="9" class="mp-ring" fill="none" stroke="#E2713B"/>'
                   f'<circle cx="{x}" cy="{y}" r="3.6" class="mp-dot" fill="#E2713B" stroke="#161B22" stroke-width="1.2"/></g>')
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


def medallion(name, score, mod=None, fell=None, size=56, tone=None, cls=""):
    """An attribute as a medallion: the score on a plate disc inside a ring; the modifier under it. With the Knight Who
    Fell's number, an arc round the ring runs the score's share of it, that number faint at the top right; once the score
    has passed it the arc closes in ember (.hot). tone: borrowed (blue), earned (brass) or unlit (grey) for a Reckoning
    read by the Eye; the colours are drawn in, as with every drawing here."""
    import math
    c, r = 32, 25
    try:
        s = int(score)
    except (TypeError, ValueError):
        s = None
    f = as_int(fell) if fell is not None else None
    hot = f is not None and s is not None and f > 0 and s >= f
    ink = {"borrowed": PAL["t6"], "earned": PAL["brass"], "unlit": PAL["dim"]}.get(tone, PAL["ink"])
    ring = {"borrowed": PAL["t5"], "unlit": PAL["faint"]}.get(tone, PAL["brass"])
    parts = [f'<circle cx="{c}" cy="{c}" r="{r}" fill="{PAL["plate"]}" stroke="{PAL["raw"]}" stroke-width="5"/>']
    if f and s is not None:
        circ = 2 * math.pi * r
        frac = min(s / f, 1.0)
        L = circ * frac
        parts.append(f'<circle cx="{c}" cy="{c}" r="{r}" fill="none" stroke="{PAL["ember"] if hot else PAL["brass_dim"]}" stroke-width="5" '
                     f'stroke-linecap="{"butt" if frac >= 1 else "round"}" stroke-dasharray="{L:.2f} {circ:.2f}" transform="rotate(-90 {c} {c})"/>')
    parts.append(f'<circle cx="{c}" cy="{c}" r="{r - 4.5}" fill="none" stroke="{ring}" stroke-width="1.2" stroke-opacity=".85"/>')
    y = c + (1 if mod is None else -2.5)
    parts.append(f'<text x="{c}" y="{y}" text-anchor="middle" dominant-baseline="central" font-family="{SVG_DISPLAY_FONT}" '
                 f'font-size="{22 if s is None or s < 100 else 17}" font-weight="700" fill="{ink}">{esc(score)}</text>')
    if mod is not None:
        parts.append(f'<text x="{c}" y="{c + 12.5}" text-anchor="middle" dominant-baseline="central" font-family="{SVG_LABEL_FONT}" font-size="9" '
                     f'font-weight="700" fill="{PAL["dim"]}">{mod:+d}</text>')
    if f:
        col = PAL["ember"] if hot else PAL["faint"]
        parts.append(f'<circle cx="52.5" cy="11.5" r="8.5" fill="{PAL["night"]}" stroke="{col}" stroke-width="1"/>'
                     f'<text x="52.5" y="12" text-anchor="middle" dominant-baseline="central" font-family="{SVG_LABEL_FONT}" font-size="8.5" '
                     f'font-weight="700" fill="{col}">{f}</text>')
    label = f"{name} {score}" + (f" ({mod:+d})" if mod is not None else "") + (f"; the Knight Who Fell: {f}" if f else "")
    return (f'<svg class="medal{" hot" if hot else ""}{(" " + cls) if cls else ""}" viewBox="0 0 64 64" width="{size}" height="{size}" role="img" '
            f'aria-label="{esc(label)}">{"".join(parts)}</svg>')


FLAME_TONGUES = {"Guttering": 1, "Low": 1, "Steady": 2, "Bright": 3, "Blazing": 3}


def flame(kind="ember", tier=None, size=28, label=""):
    """A fire as a brazier: a bowl, and tongues of flame by its state. ember: warm, one tongue at Guttering or Low, two at
    Steady, three at Bright, three and a brass halo at Blazing (.blazing); grace: three blue tongues, borrowed; none: the
    coal alone, grey."""
    kind = kind or "none"
    n = 3 if kind == "grace" else 0 if kind == "none" else FLAME_TONGUES.get(str(tier), 2)
    low = kind == "ember" and str(tier) in ("Guttering", "Low")
    blazing = kind == "ember" and str(tier) == "Blazing"
    outer = PAL["t5"] if kind == "grace" else PAL["ember"]
    core = PAL["t6"] if kind == "grace" else PAL["t2"]
    coal = PAL["t3"] if kind == "ember" else PAL["t5"] if kind == "grace" else PAL["faint"]
    tongues = {1: [(14, 9 if low else 6)], 2: [(10.5, 8), (17.5, 6)], 3: [(8, 10), (14, 3), (20, 10)]}.get(n, [])
    parts = []
    if blazing:
        parts.append(f'<circle cx="14" cy="13" r="12.5" fill="none" stroke="{PAL["brass"]}" stroke-opacity=".75" stroke-width="1"/>')
    for x, tip in tongues:
        parts.append(f'<path d="M{x} 19.5 C{x - 3.2} 15.5 {x - 1.4} 12.5 {x} {tip} C{x + 1.4} 12.5 {x + 3.2} 15.5 {x} 19.5 Z" fill="{outer}"/>')
    if n >= 2:  # the bright core of the tallest tongue
        x, tip = max(tongues, key=lambda t: -t[1])
        parts.append(f'<path d="M{x} 19.5 C{x - 1.4} 17 {x - .7} 15 {x} {tip + 6} C{x + .7} 15 {x + 1.4} 17 {x} 19.5 Z" fill="{core}"/>')
    parts.append(f'<path d="M4 19 Q14 26.5 24 19 Z" fill="{PAL["plate"]}" stroke="{coal}" stroke-width="1.4" stroke-linejoin="round"/>'
                 f'<path d="M3 19 H25" stroke="{PAL["brass_dim"]}" stroke-width="1.2" stroke-linecap="round"/>')
    aria = f'role="img" aria-label="{esc(label)}"' if label else 'aria-hidden="true"'
    return f'<svg class="flame {kind}{" blazing" if blazing else ""}" viewBox="0 0 28 28" width="{size}" height="{size}" {aria}>{"".join(parts)}</svg>'


def thread_track(stage, of, frac=0.0, names=()):
    """The Tether as a finer thread under the Knot rope: a knot per stage, the reached ones lit and named, the next one's
    length drawn by frac. Only reached stages are named; the rest keep their numerals."""
    of, stage = max(as_int(of) or 1, 1), max(as_int(stage) or 0, 0)
    frac = max(0.0, min(float(frac or 0.0), 1.0))
    step = 380 / of
    label = f"The Tether: stage {roman(stage)} of {roman(of)}" + (f", on the way to {roman(stage + 1)}" if stage < of else "")
    out = [f'<svg class="thread" viewBox="0 0 400 36" role="img" aria-label="{esc(label)}">',
           f'<path d="M10 14 H390" stroke="{PAL["leather"]}" stroke-width="1.6" fill="none"/>']
    lit = 10 + (stage - 0.5) * step + (frac * step if stage < of else 0) if stage else 10
    if lit > 10:
        out.append(f'<path d="M10 14 H{lit:.1f}" stroke="{PAL["ember"]}" stroke-width="1.6" stroke-linecap="round" fill="none"/>')
    for k in range(1, of + 1):
        x = 10 + (k - 0.5) * step
        on = k <= stage
        out.append(f'<g class="th-knot{" on" if on else ""}"><path d="M{x - 6} 14 C{x - 6} 7 {x + 6} 7 {x + 6} 14 C{x + 6} 21 {x - 6} 21 {x - 6} 14" '
                   f'fill="{PAL["ember"] if on else PAL["raw"]}" stroke="{PAL["t2"] if on else PAL["faint"]}" stroke-width="1.4"/>')
        word = names[k - 1] if on and k - 1 < len(names) else roman(k)
        out.append(f'<text x="{x}" y="32" text-anchor="middle" font-family="{SVG_LABEL_FONT}" font-size="{9 if on else 8}" letter-spacing=".06em" '
                   f'fill="{PAL["ember"] if on else PAL["faint"]}">{esc(word)}</text></g>')
    out.append("</svg>")
    return "".join(out)


# Small line glyphs in the house style (a stroke of brass, round caps): the kinds of block in the story, the kinds of entry
# in the Codex, the Wardrobe's categories, and a few marks for the sheet. Decorative: hidden from screen readers.
GLYPHS = {
    "quest": '<path d="M6 3 V21 M6 4.5 H18.5 L14.5 8.5 L18.5 12.5 H6"/>',
    "swords": '<path d="M4 4 L20 20 M20 4 L4 20 M3.5 15.5 L8.5 20.5 M15.5 20.5 L20.5 15.5"/>',
    "work": '<path d="M4 20 L11.5 12.5 M9.5 6.5 L13.5 2.5 L21.5 10.5 L17.5 14.5 Z"/>',
    "hp": '<path d="M12 3 L20 6 V12 C20 17 16 20 12 21 C8 20 4 17 4 12 V6 Z"/><path d="M12 15.5 C12 15.5 8.5 13.5 8.5 11 C8.5 9.2 10.8 8.6 12 10.4 C13.2 8.6 15.5 9.2 15.5 11 C15.5 13.5 12 15.5 12 15.5 Z"/>',
    "prof": '<path d="M12 3 L14.2 9.8 L21 12 L14.2 14.2 L12 21 L9.8 14.2 L3 12 L9.8 9.8 Z"/>',
    "scene": '<path d="M4.5 4.5 H14 L19.5 10 V19.5 H4.5 Z M14 4.5 V10 H19.5 M7.5 13.5 H16.5 M7.5 16.5 H13"/>',
    "between": '<circle cx="7" cy="12" r="3"/><circle cx="17" cy="12" r="3"/><path d="M10 12 H14"/>',
    "interlude": '<path d="M14.5 3 A9 9 0 1 0 21 15.5 A7 7 0 0 1 14.5 3 Z"/>',
    "climax": '<path d="M4.5 18.5 H19.5 M4.5 18.5 L3.5 8 L8.5 12 L12 4.5 L15.5 12 L20.5 8 L19.5 18.5"/>',
    "choice": '<path d="M12 21 V12 M12 12 L5.5 5.5 M12 12 L18.5 5.5 M5.5 10 V5.5 H10 M18.5 10 V5.5 H14"/>',
    "chosen": '<circle cx="12" cy="12" r="9"/><path d="M8 12.5 L11 15.5 L16.5 9"/>',
    "place": '<path d="M6 21 V7 H8 V4 H10 V7 H14 V4 H16 V7 H18 V21 Z M10 21 V15 H14 V21"/>',
    "faction": '<path d="M12 3 L20 6 V12 C20 17 16 20 12 21 C8 20 4 17 4 12 V6 Z M5 12 H19"/>',
    "saying": '<path d="M7 10 C5.5 10 4.5 11 4.5 12.5 C4.5 14 5.5 15 7 15 C8.5 15 9.5 14 9.5 12.5 C9.5 9 7.5 7.5 6 7 M17 10 C15.5 10 14.5 11 14.5 12.5 C14.5 14 15.5 15 17 15 C18.5 15 19.5 14 19.5 12.5 C19.5 9 17.5 7.5 16 7"/>',
    "thing": '<path d="M4 9 H20 V20 H4 Z M9 9 V6 H15 V9 M4 13 H20"/>',
    "song": '<circle cx="7" cy="18" r="2.6"/><circle cx="17" cy="16" r="2.6"/><path d="M9.6 18 V6 L19.6 4 V16"/>',
    "beast": '<circle cx="7" cy="9" r="1.8"/><circle cx="11" cy="6.5" r="1.8"/><circle cx="15.5" cy="7" r="1.8"/><circle cx="19" cy="10" r="1.8"/><path d="M13 11.5 C9.5 11.5 6.5 14 6.5 16.5 C6.5 18.5 8 19.5 10 18.8 C11 18.4 12 18 13 18 C14 18 15 18.4 16 18.8 C18 19.5 19.5 18.5 19.5 16.5 C19.5 14 16.5 11.5 13 11.5 Z"/>',
    "build": '<circle cx="12" cy="5" r="2.5"/><path d="M12 8 V15 M6 10.5 L12 8 L18 10.5 M12 15 L8.5 21 M12 15 L15.5 21"/>',
    "clothing": '<path d="M8 4 L3.5 7 L5.5 11 L8 10 V20 H16 V10 L18.5 11 L20.5 7 L16 4 C15 6 9 6 8 4 Z"/>',
    "cloak": '<path d="M12 3 C8 5 5 10 4 20 H20 C19 10 16 5 12 3 Z M12 9 V20"/><circle cx="12" cy="6.5" r="1.2"/>',
    "hair": '<path d="M4.5 8 H19.5 V11.5 H4.5 Z M6.5 11.5 V16.5 M9.5 11.5 V18 M12 11.5 V16.5 M14.5 11.5 V18 M17.5 11.5 V16.5"/>',
    "beard": '<path d="M6 8 C6 15 8 19 12 20.5 C16 19 18 15 18 8 M9 12.5 C10 14.5 14 14.5 15 12.5"/>',
    "expression": '<circle cx="12" cy="12" r="8.5"/><path d="M9 10 V10.8 M15 10 V10.8 M8.5 14.5 C10 16.5 14 16.5 15.5 14.5"/>',
    "pose": '<circle cx="13" cy="4.5" r="2.3"/><path d="M12 7.5 L10 13 L6 15 M12 7.5 L17 10 L19 14 M10 13 L13 17 L10.5 21 M13 17 L16.5 21"/>',
    "hand": '<path d="M8 12 V7 M11 12 V5 M14 12 V6 M17 12 V8 M8 12 C8 16 10 21 15 21 H17 C19 21 20 19 20 17 V12 M8 14 L5 11"/>',
    "feet": '<path d="M7 3 H13 V14 C15 16 19 17 20 20 V21 H4 V18 L7 14 Z M13 14 H7"/>',
    "extra": '<path d="M6 10 C6 8 8 7 12 7 C16 7 18 8 18 10 L19 19 C19 20.5 16 21 12 21 C8 21 5 20.5 5 19 Z M9 7 V4.5 H15 V7 M6 11.5 H18"/>',
    "side": '<circle cx="8" cy="6" r="2.2"/><circle cx="16" cy="6" r="2.2"/><path d="M4 21 V14 C4 11 6 10 8 10 C10 10 12 11 12 14 V21 M12 21 V14 C12 11 14 10 16 10 C18 10 20 11 20 14 V21"/>',
}


def glyph(name, size=18, cls=""):
    """One of GLYPHS at the given size; nothing for a name it does not know."""
    body = GLYPHS.get(name)
    if not body:
        return ""
    return (f'<svg class="ic ic-{esc(name)}{(" " + cls) if cls else ""}" viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="{PAL["brass"]}" '
            f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{body}</svg>')


# ============================================================ components
def chip(text, cls=""):
    return f'<span class="chip {cls}">{esc(text)}</span>'


def badge(text, cls="dim"):
    return f'<span class="state {cls}">{esc(text)}</span>'


def chip_glyph(name, text, cls=""):
    """A chip with one of the small glyphs before its words."""
    return f'<span class="chip ic-chip {cls}">{glyph(name, 14)}{esc(text)}</span>'


def bar(have, need, label, cls="", show=None, text=None, quiet=False, ticks=None, lead=""):
    """A progress bar. text: what screen readers hear instead of the numbers (used for approval, which is never shown as a number).
    quiet: no visible label row (the line above the bar already names it); screen readers still hear the label.
    ticks: an int divides the bar into that many segments; a list of fractions (0-1) marks each one (the Ember's tiers).
    lead: a drawing (a flame, a glyph) set before the label."""
    need = max(need, 1)
    pct = max(0, min(100, 100.0 * have / need))
    txt = f'<span class="num">{show}</span>' if show is not None else ""
    if text is not None:
        aria = f'role="img" aria-label="{esc(label)}: {esc(text)}"'
    else:
        aria = f'role="progressbar" aria-label="{esc(label)}" aria-valuemin="0" aria-valuemax="{need}" aria-valuenow="{have}"'
    head = "" if quiet else f'<div class="bar-l"><span>{lead}{esc(label)}</span>{txt}</div>'
    marks = ""
    if isinstance(ticks, int) and ticks > 1:
        marks = f'<span class="ticks" style="--n:{ticks}" aria-hidden="true"></span>'
    elif ticks:
        marks = "".join(f'<span class="tick" style="--x:{100.0 * min(max(float(t), 0.0), 1.0):.1f}%" aria-hidden="true"></span>' for t in ticks)
    return f'<div class="bar-row">{head}<div class="bar {cls}" {aria}><i style="--w:{pct:.1f}%"></i>{marks}</div></div>'


def pips(have, need, cls=""):
    s = "".join(f'<span class="pip{" on" if i < have else ""}"></span>' for i in range(need))
    return f'<span class="pips {cls}" role="img" aria-label="{have} of {need}">{s}</span>'


BEARING_LABEL = "who his choices are making him"  # the site's own label for the Bearing section (exempt from the GM-sentence check)


LEVEL_NEWS_DAYS = 3  # the Now page carries a level-up banner this many days after the level came (darrow.json → level_reached)
FINE_PRINT = "Only what the story has shown so far."  # the one line that replaces a disclaimer on every section head


def sec(title, label, inner, cls="", hid="", label_html=""):
    """A section with its head: the title, and a label at the right (label is text; label_html may carry a drawing)."""
    hid = f' id="{hid}"' if hid else ""
    lbl = f'<span class="lbl">{label_html or esc(label)}</span>' if (label or label_html) else ""
    return f'<section class="sec {cls}"{hid}><div class="sec-h"><h2>{esc(title)}</h2>{lbl}</div>{inner}</section>'


def panel(title, meta, inner, pid=""):
    """A section folded shut until opened (Darrow's page): the heading and one line of what is inside on the closed row."""
    pid = f' id="{pid}"' if pid else ""
    meta = f'<span class="meta">{meta}</span>' if meta else ""
    return f'<details class="panel"{pid}><summary><h2>{esc(title)}</h2>{meta}</summary><div class="panel-body">{inner}</div></details>'


def details(summary, inner, open_=False):
    return f'<details{" open" if open_ else ""}><summary>{esc(summary)}</summary><div class="dt-body">{inner}</div></details>'


STATUS_CLS = {"alive": "good", "fallen": "bad", "hollowed": "sealed", "missing": "warn", "unknown": "dim"}

COMPANY, POSE, HELD, FACE = "side", "pose", "hand", "expression"  # the Wardrobe's categories its rules read (engine/wardrobe.json)


def wardrobe_clash(ca, a, cb, b):
    """Whether piece a (of category ca) and piece b (of cb) cannot be worn together: one needs another piece of the
    other's category; a piece for someone (with: a companion, or alone) beside anyone else at his side; a pose with
    something held in more hands than it leaves free, or with no weapon in a fight; a battle face out of a fight, or a
    fierce or battle face in a tender pose."""
    for (cx, x), (cy, y) in (((ca, a), (cb, b)), ((cb, b), (ca, a))):
        if (x.get("needs") or {}).get(cy, y["id"]) != y["id"]:
            return True
        if cy == COMPANY and x.get("with") and x["with"] != ("alone" if y["id"] == "none" else y["id"]):
            return True
        if cx == POSE and cy == HELD and (y.get("hands", 1) > x.get("free_hands", 2) or (x.get("fight") and not y.get("weapon"))):
            return True
        if cx == POSE and cy == FACE and ((y.get("mood") == "battle" and not x.get("fight")) or (x.get("tender") and y.get("mood"))):
            return True
    return False


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
# the reader's text size: a small AA in the masthead opens a panel with a smaller and a larger A (site.js fills the steps
# and the name, and scales the reader's text; nothing is kept, a new page starts at the default)
TEXT_SIZE = ('<div class="ts"><button class="ts-btn" type="button" aria-expanded="false" aria-controls="ts-panel" title="Text size">'
             '<span aria-hidden="true"><span class="s">A</span><span class="b">A</span></span><span class="sr">Text size</span></button>'
             '<div class="ts-panel" id="ts-panel" role="group" aria-label="Text size" hidden>'
             '<div class="ts-head"><span class="lbl">Text size</span><span class="ts-name" aria-live="polite"></span></div>'
             '<div class="ts-row"><button type="button" data-ts="-1" aria-label="Smaller text"><span aria-hidden="true">A</span></button>'
             '<span class="ts-steps" aria-hidden="true"></span>'
             '<button class="big" type="button" data-ts="1" aria-label="Larger text"><span aria-hidden="true">A</span></button></div></div></div>')


def asset_v(name):
    """A short hash of the stylesheet or the script: its link changes whenever its content does, so a browser never pairs a new
    page with a stylesheet it cached before the change."""
    if name not in ASSET_V:
        ASSET_V[name] = hashlib.sha1({"css": CSS, "js": JS, "forge": FORGE_JS}[name].encode("utf-8")).hexdigest()[:10]
    return ASSET_V[name]


def shell(title, body, rel, current, cls="", desc=""):
    nav = "".join(f'<a href="{rel}{href}"{CUR if name == current else ""}>{name}</a>' for name, href in NAV)
    meta_desc = f'<meta name="description" content="{esc(desc)}">' if desc else ""
    reader = "reader-page" in cls.split()
    progress = '<div class="progress" aria-hidden="true"><i></i></div>\n' if reader else ""
    # a chapter or a tale: the text-size control in the masthead (site.js runs it; without the script it is not shown)
    ts = TEXT_SIZE if reader else ""
    ts_off = "<noscript><style>.ts{display:none}</style></noscript>\n" if reader else ""
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
{ts_off}</head>
<body class="{cls}">
<a class="skip" href="#main">Skip to content</a>
{progress}<header class="mast"><div class="wrap mast-in"><a class="brand" href="{rel}index.html">The Unkneeling</a><nav class="nav" aria-label="Site">{nav}</nav>{ts}</div></header>
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
        self.map_base = pl.get("base_image") or None  # {"image", "alt"}: a painted base under the map's names and roads
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
        for r in self.route:
            ok = r is None or (isinstance(r, str) and r in self.place_by_id) or (
                isinstance(r, list) and len(r) == 2 and all(isinstance(v, (int, float)) for v in r))
            if not ok:
                problem(f"places.json: route entry {json.dumps(r)} is not a place id, an [x, y] waypoint or null (a new leg)")
        legs = route_legs(self.route, self.place_by_id)
        cur = self.place_by_id.get(self.current_place)
        if map_point(cur) and (not legs or legs[-1][-1] != (cur["x"], cur["y"])):
            problem(f"places.json: the route ends at {list(legs[-1][-1]) if legs else 'nothing'} but Darrow is at {cur['id']}: "
                    f"extend the route to where he is (the map draws him at its end)")
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
        # Every link carries a short hash of the picture, so a picture replaced under the same name shows at once instead
        # of the copy a browser cached; its small and medium copies are made from it, so the same hash marks them too.
        v = f"?v={file_sha1(src)[:10]}"
        sm, md = self.thumb(src, rel_src, "sm") or path, self.thumb(src, rel_src, "md") or path
        return path + v, image_size(src), sm + v, md + v

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
        # the link carries a short hash of the file, so a song replaced under the same name plays at once, not a cached copy
        self.songs[anchor] = {"path": f"{path}?v={file_sha1(src)[:10]}", "title": str(title or e["name"]).strip(), "cues": cues}
        e["_song"] = self.songs[anchor]

    def char_portrait(self, c):
        """The portrait, its small round copies (zoomed in on portrait_focus by portrait_zoom), and the earlier portraits
        (portraits_earlier: [{label, portrait, portrait_alt, portrait_focus}], a look from an earlier Book) the page's frame
        swipes back to; the current one is labelled portrait_label ("Now" when unset)."""
        where = f"saga/characters/{c['id']}.json"
        got = self.register_image(f"{where}: portrait", c["portrait"], c.get("portrait_alt"))
        if not got:
            return
        c["_portrait_path"], c["_portrait_size"], c["_portrait_sm"], c["_portrait_md"] = got
        c["_portrait_focus"] = self.focus_style(f"{where}: portrait_focus", c.get("portrait_focus"), "50% 30%")
        c["_portrait_face"] = self.face_transform(where, c.get("portrait_focus"), c.get("portrait_zoom"))
        earlier = c.get("portraits_earlier") or []
        if not isinstance(earlier, list):
            problem(f"{where}: portraits_earlier must be a list of {{label, portrait, portrait_alt}}")
            earlier = []
        shots = [{"label": str(c.get("portrait_label") or "Now").strip(), "path": got[0], "size": got[1], "md": got[3],
                  "focus": c["_portrait_focus"], "alt": c.get("portrait_alt", "")}]
        for i, e in enumerate(earlier):
            w = f"{where}: portraits_earlier[{i}]"
            if not isinstance(e, dict) or not str(e.get("label") or "").strip() or not e.get("portrait"):
                problem(f"{w} needs a label (e.g. \"Book I\") and a portrait")
                continue
            g = self.register_image(f"{w}.portrait", e["portrait"], e.get("portrait_alt"))
            if g:
                shots.append({"label": str(e["label"]).strip(), "path": g[0], "size": g[1], "md": g[3],
                              "focus": self.focus_style(f"{w}.portrait_focus", e.get("portrait_focus"), "50% 30%"),
                              "alt": e.get("portrait_alt", "")})
        labels = [s["label"] for s in shots]
        if len(set(labels)) != len(labels):
            problem(f"{where}: portrait labels must differ ({', '.join(labels)})")
        c["_portraits"] = shots

    @staticmethod
    def face_transform(where, focus, zoom):
        """portrait_zoom (1-4) for the small round copies of a portrait (avatars, name previews): a CSS transform that
        scales the picture by the zoom and brings portrait_focus to the circle's centre, held so the picture still fills
        it. "" without a zoom (the whole picture, as before)."""
        if zoom is None:
            return ""
        try:
            z = float(zoom)
        except (TypeError, ValueError):
            z = 0
        if not 1 <= z <= 4:
            problem(f"{where}: portrait_zoom '{zoom}' must be a number from 1 to 4")
            return ""
        if z == 1:
            return ""
        m = re.fullmatch(r"\s*(\d{1,3})%\s+(\d{1,3})%\s*", str(focus or "50% 30%"))
        fx, fy = (int(m.group(1)), int(m.group(2))) if m else (50, 30)
        lo = 100 * (1 - z)
        tx, ty = min(0, max(lo, 50 - z * fx)), min(0, max(lo, 50 - z * fy))
        return f"transform-origin:0 0;transform:translate({tx:.1f}%,{ty:.1f}%) scale({z:g})"

    def portrait_figure(self, c, rel, overlay=""):
        """A character's portrait at the head of their page: a square frame, cropped to fit, tap or click to see it whole.
        overlay (the level crest) sits on the frame's corner and lets taps through to the picture. With earlier portraits
        the frame swipes between them, newest first, and a row of tabs under it (shown by the script) jumps to one."""
        if not c.get("_portrait_path"):
            return ""
        shots = c.get("_portraits") or []
        if len(shots) > 1:
            return self.swipe_frame(shots, rel, "Portraits", overlay)
        href = rel + c["_portrait_path"]
        wh = c.get("_portrait_size")
        dims = f' width="{wh[0]}" height="{wh[1]}"' if wh else ""
        alt = esc(c.get("portrait_alt", ""))
        return (f'<figure class="portrait"><a href="{href}" data-zoom aria-label="Enlarge: {alt}">'
                f'<img src="{rel}{c["_portrait_md"]}" alt="{alt}"{dims}{c.get("_portrait_focus", "")} decoding="async"></a>{overlay}</figure>')

    @staticmethod
    def swipe_frame(shots, rel, label, overlay=""):
        """Pictures in one frame that swipes between them, the first shown first, and a row of tabs under it (shown by
        the script) that jumps to one: a character's portraits by Book. Each shot is
        {label, path, size, md, focus, alt}; tap or click one to see it whole."""
        slides = []
        for s in shots:
            dims = f' width="{s["size"][0]}" height="{s["size"][1]}"' if s.get("size") else ""
            a = esc(s["alt"])
            slides.append(f'<a href="{rel}{s["path"]}" data-zoom aria-label="Enlarge: {a}">'
                          f'<img src="{rel}{s["md"]}" alt="{a}"{dims}{s["focus"]} decoding="async"></a>')
        tabs = "".join(f'<button type="button" data-pf-i="{i}" aria-pressed="{"true" if i == 0 else "false"}">{esc(s["label"])}</button>'
                       for i, s in enumerate(shots))
        return (f'<figure class="portrait multi" data-pf><div class="pf-frame"><div class="pf-strip">{"".join(slides)}</div>{overlay}</div>'
                f'<div class="pf-tabs" role="group" aria-label="{label}" hidden>{tabs}</div></figure>')

    def named_picture(self, folder, stem, alt):
        """saga/art/<folder>/<stem>.webp (or .png, .jpg), registered for the site: (path, size, sm, md), or None if there is none."""
        src = next((p for p in sorted((ART / folder).glob(stem + ".*")) if p.suffix.lower() in IMAGE_TYPES), None)
        return self.register_image(f"saga/art/{folder}/{src.name}", src.relative_to(ART).as_posix(), alt) if src else None

    @staticmethod
    def stray_pictures(folder, stems, named_for):
        """Every file in saga/art/<folder>/ must be a picture (.webp, .png, .jpg) named for one of stems, one per name; the
        build fails on anything else and says what is wrong. Hidden files (.DS_Store) and folders are let be."""
        seen = {}
        for p in sorted((ART / folder).glob("*")):
            if p.name.startswith(".") or not p.is_file():
                continue
            if p.suffix.lower() not in IMAGE_TYPES:
                problem(f"saga/art/{folder}/{p.name}: a picture must be one of {', '.join(sorted(IMAGE_TYPES))}")
            elif p.stem not in stems:
                problem(f"saga/art/{folder}/{p.name}: '{p.stem}' is not {named_for}")
            elif p.stem in seen:
                problem(f"saga/art/{folder}/{p.name}: {seen[p.stem]} is already the picture for '{p.stem}'; keep one")
            else:
                seen[p.stem] = p.name

    def avatar(self, c, rel, size, cls=""):
        """A round portrait in place of a sigil (roster cards, the Now page); empty when the character has none. With a
        portrait_zoom it is a circle zoomed in on the face (the medium copy, so the zoom stays sharp)."""
        if not c or not c.get("_portrait_path"):
            return ""
        k = f'avatar{(" " + cls) if cls else ""}'
        if c.get("_portrait_face"):
            return (f'<span class="{k} zoomed"><img src="{rel}{c["_portrait_md"]}" alt="" width="{size}" height="{size}" '
                    f'style="{c["_portrait_face"]}" decoding="async"></span>')
        return (f'<img class="{k}" src="{rel}{c["_portrait_sm"]}" alt="" '
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
                                      "i": c.get("_portrait_md") if c.get("_portrait_face") else c.get("_portrait_sm"),
                                      "k": "face", "f": focus_of(c.get("_portrait_focus")), "z": c.get("_portrait_face", "")}
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
            if t.get("z"):
                attrs += f' data-pv-z="{esc(t["z"])}"'
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
                # consecutive dice lines are one check: a cast, an Inspiration line, the cast again (style.md §3);
                # they are gathered here and drawn as one block by dice_check() below
                if out and isinstance(out[-1], list):
                    out[-1].append((b[1], b[2]))
                else:
                    out.append([(b[1], b[2])])
            elif kind == "choice-h":
                out.append(f'<h3 class="choice-h">{glyph("choice", 20)}{esc(b[1])}</h3>')
            elif kind == "ol":
                items, is_choice = b[1], b[2]
                out.append(self.choice_list(items, self.choice_for(ch, scene["key"]) if is_choice else None, bool(is_choice)))
            elif kind == "ul":
                out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in b[1]) + "</ul>")
        return "".join(self.dice_check(x) if isinstance(x, list) else x for x in out)

    @staticmethod
    def dice_check(lines):
        """One check on the page: the die, the stat and DC, the total and the outcome on one line; a tap opens the casts
        in full (the modifiers, and any Inspiration spent and the cast again), so the arithmetic never stops the prose."""
        rows, last, casts = [], None, 0
        for tag, body in lines:
            if tag.strip().upper() == "INSPIRATION":
                if rows and rows[-1].startswith('<div class="dice-row">'):  # the cast before an Inspiration line is the one it replaces
                    rows[-1] = '<div class="dice-row superseded">' + rows[-1][len('<div class="dice-row">'):]
                rows.append(f'<div class="dice-row insp"><span class="insp-glyph" aria-hidden="true">✦</span><span class="dice-tag">Inspiration</span> <span class="dice-body">{inline(body)}</span></div>')
                continue
            m_nat = re.search(r"d20\s+\*{0,2}(\d+)(?:/(\d+))?", body)
            m_res = re.search(r"\*?((?:Critical )?(?:[Ss]uccess|[Ff]ailure)|Partial[^*—]*)\*?", body)
            m_tot = re.search(r"=\s*\*{0,2}(-?\d+)\*{0,2}", body)
            res = m_res.group(1).strip() if m_res else ""
            die = d20_glyph(m_nat.group(1), res) if m_nat else ""
            rows.append(f'<div class="dice-row">{die}<span class="dice-body">{inline(body)}</span></div>')
            last, casts = (tag, die, m_tot.group(1) if m_tot else "", res), casts + 1
        if last is None:  # only an Inspiration line: nothing to sum up
            return f'<div class="dice">{"".join(rows)}</div>'
        tag, die, total, res = last
        if casts == 1:  # one cast: the summary already shows its die and its tag, so the tap shows the sum alone
            rows = [re.sub(r'^<div class="dice-row">.*?<span class="dice-body">', '<div class="dice-row"><span class="dice-body">', r, count=1) for r in rows]
        times = f'<span class="dice-times">✦ cast ×{casts}</span>' if casts > 1 else ""
        total_html = f'<b class="dice-total">{esc(total)}</b>' if total else ""
        res_html = f'<span class="dice-res">{esc(res)}</span>' if res else ""
        return (f'<details class="dice"><summary title="Show the roll">{die}<span class="dice-tag">{esc(tag)}</span>'
                f'{total_html}{res_html}{times}</summary><div class="dice-full">{"".join(rows)}</div></details>')

    @staticmethod
    def scene_kind(s):
        """The kind of block a scene is, for its glyph: scene, between, interlude, climax or choice."""
        if s.get("between"):
            return "between"
        k = str(s.get("key", ""))
        if k.startswith("interlude"):
            return "interlude"
        return k if k in ("climax", "choice") else "scene"

    @staticmethod
    def choice_list(items, rec=None, is_choice=True):
        """A numbered list. For a choice with a recorded answer (rec): the option taken marked 'chosen' (and 'answered for
        himself' when the Bearing answered), or, when he took none of them, his own answer after the list. A choice is
        framed as a decision (a brass bracket)."""
        taken = as_int(rec.get("option")) if rec else None
        free = (rec.get("text") or "").strip() if rec and taken is None else ""
        mark = f' <span class="state good">{glyph("chosen", 13)}chosen</span>' + (' <span class="state dim">answered for himself</span>' if rec and rec.get("by") == "bearing" else "")
        lis = []
        for i, it in enumerate(items, 1):
            cls = ' class="taken"' if taken == i else ""
            lis.append(f"<li{cls}>{inline(it)}{mark if taken == i else ''}</li>")
        out = f'<ol class="{"choice" if is_choice else ""}">{"".join(lis)}</ol>'
        out += f'<p class="chosen-free">{mark.strip()} {esc(free)}</p>' if free else ""
        return f'<div class="decision">{out}</div>' if is_choice else out

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
            lab = f'<span class="scene-n">{glyph(self.scene_kind(s), 16)}{esc(s["label"])}</span>' if s["label"] else ""
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
                f'<li><a href="{rel}chronicle/{ch["slug"]}.html#{s["anchor"]}">{glyph(self.scene_kind(s), 14)}{esc((s["label"] + " — " if s["label"] else "") + s["title"])}</a></li>'
                for s in ch["scenes"] if s["title"] or s["label"])
            n_bt = sum(1 for s in ch["scenes"] if s.get("between"))
            n_sc = len(ch["scenes"]) - n_bt
            count = "no scene yet" if ch["empty"] else (f'{n_sc} scene{"s" if n_sc != 1 else ""}' + (f' · {n_bt} between' if n_bt else "") + f' · about {ch["words"]:,} words')
            tier_row = next((r for r in self.chapters_csv if str(r.get("chapter")) == str(ch["number"])), None) if ch["number"] else None
            seal = (svg_seal(tier_row["tier"], 22) + " ") if tier_row and tier_row.get("tier") in TIER_SEAL else ""
            line = f'<span class="m num">{seal}{count}{" · now" if now else ""}</span>'
            fold = (f'<details class="scn"{" open" if now else ""}><summary>{line}</summary><ul class="scenes">{scenes}</ul></details>'
                    if scenes else line)
            items.append(f'<li class="ch{" now" if now else ""}"><a class="ch-link" href="{rel}chronicle/{ch["slug"]}.html"><b>{esc(ch["label"])} — {esc(ch["title"])}</b></a>'
                         f'{fold}</li>')
        first = self.chapters[0] if self.chapters else None
        start = (f'<p class="m">Or <a href="{rel}chronicle/{first["slug"]}.html">start from the beginning</a>: '
                 f'{esc(first["label"] + " — " + first["title"])}.</p>') if first else ""
        body = (f'<section class="plate"><p class="lbl">The Chronicle</p><h1>Books, chapters and scenes</h1>'
                f'<p class="dim">Read in order. The current chapter is marked in brass; tap a chapter\'s line to see its scenes.</p>{self.continue_button(rel)}{start}</section>')
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
        lvl = rk.get("level")
        if eye >= 1:
            head = f'Level {lvl} · {esc(rk.get("rank"))}' if lvl is not None else esc(rk.get("rank") or "")
            rows.append(f'<p class="rk-line">{head}</p>')
        else:
            rows.append(f'<p class="rk-line">{unread}</p>')
        if eye >= 2:
            at = rk.get("attributes") or {}
            cells = "".join(f'<div class="rk-attr {kcls}">{medallion(k.capitalize(), at.get(k, "—"), None, None, 46, tone=kcls)}<span class="lbl">{k.capitalize()}</span></div>'
                            for k in ("might", "vigor", "finesse", "resolve"))
            rows.append(f'<div class="rk-attrs">{cells}</div>')
            fl = {"grace": "Grace", "ember": "Ember", "none": "Unlit"}[kind]
            rows.append(f'<p class="rk-line {kcls}">{flame(kind if kind in ("grace", "ember") else "none", None, 24)}<span class="lbl">{fl}</span> {esc(fire.get("state", ""))}'
                        + (' <span class="chip blue">borrowed</span>' if kind == "grace" else "") + "</p>")
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
        framed = (" framed" + self.metal(lvl)) if eye >= 1 else ""
        return f'<div class="rk-card{framed}">{"".join(rows)}{note_}</div>'

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
        not 'alive' (alive is the default and goes unsaid), and Darrow's names. The faction is said once, under its shield;
        on Darrow's page its shield stands beside the title that names it, and where he stands (XP, Ember, Inspiration)
        runs across the foot of the plate, so the level is said once, on the crest."""
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
        sub = f'<p class="sub">{esc(c.get("epithet", ""))}</p>'
        foot = ""
        if c["id"] == "darrow" and c["tier"] != "fallen" and self.darrow:
            inner = f'{sigil(fac, sg.get("mark"), 22)}<span>{esc(c.get("epithet", ""))}</span>'
            sub = (f'<a class="sub fac-sub" href="{rel}codex/index.html#faction-{esc(c["faction"])}">{inner}</a>' if fac.get("on_page")
                   else f'<p class="sub fac-sub">{inner}</p>')
            row, foot = "", self.darrow_standing()
        who = (f'<div class="who"><h1>{esc(c["name"])}</h1>{sub}'
               + (f'<div class="chips">{"".join(chips)}</div>' if chips else "") + '</div>')
        fig = self.portrait_figure(c, rel, "" if c["tier"] == "fallen" else cr)
        hero = f'<div class="hero with-portrait">{fig}{who}</div>' if fig else f'<div class="hero">{cr}{who}</div>'
        return f'<section class="plate{self.metal(level)}">{hero}{row}{foot}<p class="fine">{FINE_PRINT}</p></section>'

    def xp_bar(self):
        """The bar to the next level, in ten segments; when the next level opens a rank, the label names it."""
        d = self.darrow
        xp_into = d["xp"] - d["xp_this_level"]
        xp_span = d["xp_next_level"] - d["xp_this_level"]
        nxt = d["level"] + 1
        rank = next((r["name"] for r in self.rules["levels"]["ranks"] if r["from"] == nxt), None)
        label = f"XP toward Level {nxt}" + (f" · {rank}" if rank else "")
        return bar(xp_into, xp_span, label, "", f"{xp_into:,} / {xp_span:,}", ticks=10)

    def ember_bar(self, effect=False):
        """The Ember's bar with a tick at each tier's foot and the brazier before its label; effect: the tier's effect under it."""
        e = self.darrow["ember"]
        tier = e.get("tier") or "unlit"
        ticks = sorted(t["min"] / 100.0 for t in self.rules["ember"]["tiers"] if 0 < t.get("min", 0) < 100)
        html = bar(e["value"] or 0, 100, f"Ember · {tier}", "ember", e["value"], ticks=ticks, lead=flame("ember", tier, 22))
        if effect and e.get("effect"):
            html += f'<p class="ember-effect">{esc(e["effect"])}</p>'
        return html

    def darrow_standing(self):
        """Where Darrow stands, at the foot of his plate: his rank and XP, the bar to the next level, Ember and Inspiration."""
        d = self.darrow
        return (f'<div class="stand"><p class="reck-line">{esc(d["rank"])} · <span class="num">XP {d["xp"]:,}</span></p>'
                f'{self.xp_bar()}'
                f'<div class="row2"><div>{self.ember_bar(effect=True)}</div>'
                f'<div class="insp"><span class="lbl">Inspiration</span>{pips(d["inspiration"], d["inspiration_cap"], "spark")}</div></div></div>')

    def metal(self, level):
        """' metal-<name>', the class for the metal of the rank a level falls in (METALS); empty when no level is read."""
        if not isinstance(level, int):
            return ""
        rank = sum(1 for r in self.rules["levels"]["ranks"] if level >= r["from"])
        return f" metal-{METALS[min(max(rank, 1), len(METALS)) - 1]}"

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

    def read_level(self, c):
        """A character's level as Darrow's Eye reads it: the number, '—' for one with no level of their own (borrowed
        strength), or None while the page has not let the script read them (or the Eye is too weak, or they fell)."""
        rk = c.get("reckoning")
        if c["tier"] != "fallen" and isinstance(rk, dict) and not rk.get("unread") and self.eye >= 1:
            return rk["level"] if rk.get("level") is not None else "—"
        return None

    def avatar_crest(self, c, rel, size, cls=""):
        """A character's round picture (or their sigil) with their level crest pinned to its corner, when the Eye reads one:
        the party's faces on the Now page and the roster."""
        sg = c.get("sigil") or {}
        pic = self.avatar(c, rel, size, cls) or sigil(self.factions.get(sg.get("faction"), {}), sg.get("mark"), size)
        level = self.read_level(c)
        cr = crest(level) if level is not None else ""
        return f'<span class="ava">{pic}{cr}</span>'

    def render_character(self, c):
        rel = "../"
        level = self.read_level(c)
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
        wm = sigil(self.factions.get(sg.get("faction"), {}), sg.get("mark"), 84, "wm") if sg.get("faction") else ""
        return (f'<a class="card" href="{rel}{self.char_href(c["id"])}" data-faction="{esc(c["faction"])}" data-status="{esc(c["status"])}">{wm}'
                f'{self.avatar_crest(c, rel, 56)}<div class="card-body"><b>{esc(c["name"])}</b><span class="dim">{esc(c.get("epithet", ""))}</span>'
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
        """The Reckoning under Darrow's plate, always open: the look he wears (a strip that opens the Wardrobe), his chips,
        and the four attributes. His level, XP, Ember and Inspiration are on the plate above it (darrow_standing)."""
        d, rules = self.darrow, self.rules
        a = d["attributes"]
        tiles = []
        for k in ("might", "vigor", "finesse", "resolve"):
            x = a[k]
            spec = rules["attributes"][k]
            prev = spec["divisor"] * (x["raw"] - spec["base"]) ** 2
            have = x["temper"] - prev
            need = x["next_at"] - prev
            cap = f'<span class="s sealed-line">held by the Binding at {x["cap"]}</span>' if x.get("banked") else ""
            tiles.append(f'<div class="stk{" hot" if x["score"] >= x["fell"] else ""}">{medallion(k.capitalize(), x["score"], x["mod"], x["fell"], 60)}'
                         f'<span class="n">{k.capitalize()}</span>'
                         f'{bar(have, need, k.capitalize() + " temper", "temper")}<span class="s">temper {x["temper"]} · next at {x["next_at"]}</span>{cap}</div>')
        wear = self.wearing_strip(rel)
        chips = (f'<div class="chips">{chip_glyph("hp", "HP " + str(d["hp_max"]))}{chip_glyph("prof", "Proficiency +" + str(d["proficiency"]))}{self.tether_chip()}'
                 f'{self.works_chip()}{"" if wear else self.wardrobe_chip(rel)}{self.collection_chip(rel)}</div>')
        stats = chips + f'<div class="streaks">{"".join(tiles)}</div><p class="hint">The small number on each is who he was: the Knight Who Fell.</p>'
        inner = f'<div class="screen">{self.wearing_figure(rel)}<div class="screen-stats">{wear}{stats}</div></div>' if wear else stats
        return sec("The Reckoning", "", f'<div class="reck">{inner}</div>', cls="reck-sec", hid="reckoning")

    def wearing_strip(self, rel):
        """The look he wears (looks.json → wearing, else the newest) at the head of his Reckoning: a small picture and its
        name in a strip framed in his rank's metal, opening the Wardrobe. Empty while no look is filed. On a wide screen
        the strip gives way to wearing_figure."""
        lk = self.looks[0] if self.looks else None
        if not lk:
            return ""
        return (f'<a class="wear-strip{self.metal(self.darrow["level"])}" href="{rel}darrow/wardrobe.html">'
                f'<img src="{rel}{lk["_sm"]}" alt="{esc(lk["alt"])}" width="64" height="96" decoding="async">'
                f'<span><span class="lbl">Wearing</span><b>{esc(lk["name"])}</b><span class="go">The Wardrobe →</span></span></a>')

    def wearing_figure(self, rel):
        """The look he wears standing full length beside his numbers (the character screen), on a screen wide enough for
        both: the medium copy on the stage, framed in his rank's metal, its name under it, opening the Wardrobe."""
        lk = self.looks[0] if self.looks else None
        if not lk:
            return ""
        return (f'<a class="wear-fig{self.metal(self.darrow["level"])}" href="{rel}darrow/wardrobe.html">'
                f'<span class="wear-stage"><img src="{rel}{lk["_md"]}" alt="{esc(lk["alt"])}" width="200" height="300" loading="lazy" decoding="async"></span>'
                f'<span class="wear-cap"><span class="lbl">Wearing</span><b>{esc(lk["name"])}</b><span class="go">The Wardrobe →</span></span></a>')

    def darrow_panels(self, rel):
        """Darrow's sheet below the Reckoning, each section folded shut with a line of what it holds: (meta, title, html, id)."""
        d, rules = self.darrow, self.rules
        trees = defaultdict(list)
        for art in d["arts"]:
            trees[art["tree"]].append(art)
        order = ["Blade", "Footing", "Breath", "Binding", "Insight", "Cast"]
        thresholds = list(rules.get("art_ranks") or [1, 6, 15, 30, 50])
        n_pips = len(thresholds)
        self.stray_pictures("arts", {a["id"] for a in d["arts"]}, "the id of an Art in engine/rules.json")
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
                rows.append(f'<li class="art{" sealed" if sealed else ""}{" on" if rank and not sealed else ""}">{self.art_pic(art, rank, tree, rel, bool(sealed))}'
                            f'<div class="art-txt"><div class="art-top"><b>{esc(art["name"])}</b>{ring}</div>'
                            f'<span class="m">{st}</span><span class="e">{esc(art["effect"])}</span></div></li>')
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

    def art_pic(self, art, rank, tree, rel, sealed=False):
        """An Art's card picture, saga/art/arts/<art id>.webp (or .png, .jpg), once the Art has a rank, framed in the rank's
        metal (ART_METALS) with the rank's numeral on the frame; the frame gains studs at III, a second rule at IV and a glow
        at V (CSS .art-pic.rN). While it is sealed the card is greyed out: a plain grey frame, the picture grey and dim, a lock
        where the numeral would be. Before its first rank, or until its picture is drawn, the tree's glyph stands in its
        place: a dashed blank before the first rank, the ranked frame after."""
        lock = f'<span class="art-rank lock" aria-hidden="true">{svg_lock()}</span>' if sealed else ""
        if not rank:
            return f'<span class="art-pic back">{svg_tree(tree, 28)}{lock}</span>'
        step = min(rank, len(ART_METALS))
        cls = "art-pic" + ("" if sealed else f" metal-{ART_METALS[step - 1]} r{step}")
        tab = lock or f'<span class="art-rank" aria-hidden="true">{roman(rank)}</span>'
        got = self.named_picture("arts", art["id"], art["name"])
        if not got:
            return f'<span class="{cls}"><span class="art-in">{svg_tree(tree, 28)}</span>{tab}</span>'
        name = esc(art["name"])
        return (f'<a class="{cls}" href="{rel}{got[0]}" data-zoom aria-label="Enlarge: {name}">'
                f'<span class="art-in"><img src="{rel}{got[2]}" alt="{name}" width="58" height="58" loading="lazy" decoding="async"></span>{tab}</a>')

    @property
    def n_knots(self):
        return len(self.rules.get("knots") or []) or 7

    def tether_chip(self):
        """The Tether, once tied: its stage and the page's word for it. Nothing before stage I."""
        t = self.darrow.get("tether") or {}
        if not t.get("stage"):
            return ""
        return chip(f"The Tether {roman(t['stage'])} of {roman(t.get('of', 5))} · {t.get('name', '')}", "ember")

    def tether_thread(self, line=True):
        """The Tether as the finer thread under the rope, once tied: its stages, the reached ones named (rules.json →
        tether.names, as far as the sheet has climbed), and how far along the next one is. Nothing before stage I.
        line: the stage in words under it (left off where the chip beside it already says so)."""
        t = self.darrow.get("tether") or {}
        stage = as_int(t.get("stage")) or 0
        if not stage:
            return ""
        rules = self.rules.get("tether") or {}
        stages, names = list(rules.get("stages") or []), list(rules.get("names") or [])
        of = as_int(t.get("of")) or len(stages) or 5
        days, nxt = as_int(t.get("days")) or 0, as_int(t.get("next_at"))
        prev = stages[stage - 1] if stage - 1 < len(stages) else 0
        frac = (days - prev) / (nxt - prev) if nxt and nxt > prev else 0.0
        words = f'<p class="m">{esc(f"The Tether · {roman(stage)} of {roman(of)} · {t.get("name", "")}")}</p>' if line else ""
        return f'<div class="thread-row">{thread_track(stage, of, frac, names[:stage])}{words}</div>'

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
        return rope_knots(tied, knots) + self.tether_thread() + f'<ul class="knots">{"".join(rows)}</ul>{soft}'

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

    # ---------------------------------------------------------------- the wardrobe
    def wardrobe_chip(self, rel):
        return f'<a class="chip brass" href="{rel}darrow/wardrobe.html">The Wardrobe</a>' if self.wardrobe else ""

    def collection_chip(self, rel):
        """The Collection's rank, on his Reckoning: it opens the shelf of every piece."""
        if not self.wardrobe:
            return ""
        col = self.collection_stats()
        return f'<a class="chip brass" href="{rel}darrow/collection.html">The Collection · {esc(col["rank"])}</a>'

    def reference(self, r, where):
        """A reference picture for the image prompt: {label, image under saga/art/, file (its name when downloaded), use
        (what the prompt says it is for)}, published with its small copy."""
        got = self.register_image(where, r.get("image"), r.get("label"))
        if not got or not r.get("file") or not r.get("use"):
            problem(f"{where}: a reference needs label, image, file and use")
            return None
        return {"label": r["label"], "href": got[0], "sm": got[2], "file": r["file"], "use": r["use"]}

    def load_wardrobe(self):
        """engine/wardrobe.json (every piece and what opens it) and saga/state/looks.json (the finished looks). A piece
        opens once every condition of its unlock holds: the sheet's (a level, an Art's rank, a Knot: darrow.json → wardrobe)
        and the page's (a scene its page key names, which must be on the page; a Tether stage the page has paid, world.json
        → tether). Locked, it is greyed with what opens it, or left off the site entirely while it is hidden. A piece that
        needs another (needs: {category: piece}) is usable only with it open, and a look must wear what its pieces need.
        A look shows once every piece it wears is open, the newest first; its picture is published only then."""
        self.wardrobe, self.looks = None, []
        if not WARDROBE.exists():
            return
        w, where = load_json(WARDROBE), "engine/wardrobe.json"
        arts = {a["id"]: a["name"] for a in self.rules["arts"] + self.rules.get("sport_arts", {}).get("arts", [])}
        on_page = {f'{c["code"]}:{sc["key"]}': (f'{c["label"]} · {sc["label"]} — {sc["title"]}' if sc["label"] else f'{c["label"]} — {sc["title"]}',
                                                 f'{self.page_dir(c)}{c["slug"]}.html#{sc["anchor"]}') for c in self.chapters + self.tales for sc in c["scenes"]}
        knots = {k["n"]: k["name"] for k in self.rules.get("knots") or []}
        mid = lambda name: "the " + name[4:] if name.startswith("The ") else name  # "Opened by the Knot of Standing"
        tether = list((self.rules.get("tether") or {}).get("names") or [])
        paid = {}  # the Tether stages the page has paid (world.json → tether): stage → the page key of the scene that paid it
        for t in self.world.get("tether") or []:
            m = re.match(r"^ch(\d+):(?:s(\d+)|(.+))$", str(t.get("key")))
            key = m and f"{m[1]}:{m[2] or m[3]}"
            if t.get("name") not in tether or key not in on_page:
                problem(f"saga/state/world.json: tether {t}: needs a stage name of engine/rules.json → tether and the key of a scene on the page (saga.py project rebuilds it)")
            else:
                paid.setdefault(tether.index(t["name"]) + 1, key)
        earned, known = set(self.darrow.get("wardrobe") or []), set()
        for cat in w["categories"]:
            for o in cat["options"]:
                oid, u = f'{cat["id"]}.{o["id"]}', o.get("unlock") or {}
                if not isinstance(u, dict):
                    problem(f"{where}: {oid} has an unlock that is not a set of conditions: {u!r}")
                    u = {}
                o["_unlock"] = u
                if oid in known or not o.get("name") or not o.get("prompt"):
                    problem(f"{where}: {oid} is listed twice, or has no name or prompt")
                known.add(oid)
                if (set(u) - {"level", "art", "rank", "knot", "page", "tether"} or ("art" in u and u["art"] not in arts)
                        or ("rank" in u and ("art" not in u or not isinstance(u["rank"], int))) or ("knot" in u and u["knot"] not in range(1, self.n_knots + 1))
                        or ("level" in u and not isinstance(u["level"], int)) or ("tether" in u and u["tether"] not in range(1, len(tether) + 1))):
                    problem(f"{where}: {oid} has an unlock the Wardrobe cannot read: {u} (any of level, art with rank, knot, tether, page)")
                if "page" in u and u["page"] not in on_page:
                    problem(f"{where}: {oid} opens on {u['page']}, which is not a scene on the page (a piece the story has not shown stays out)")
                # open once every condition holds: the sheet's (darrow.json → wardrobe) and the page's (a scene shown, a Tether stage paid)
                o["_open"] = (("page" not in u or u["page"] in on_page) and ("tether" not in u or u["tether"] in paid)
                              and (not {"level", "art", "knot"} & set(u) or oid in earned))
                parts = ([f'the Tether {roman(u["tether"])}'] if "tether" in u else []) + ([f'Level {u["level"]}'] if "level" in u else []) \
                    + ([f'{mid(arts.get(u["art"], ""))} {roman(u.get("rank", 1))}'] if "art" in u else []) + ([mid(knots.get(u["knot"], ""))] if "knot" in u else [])
                o["_lock"] = " and ".join(parts)  # what opens it: "the Knot of the Road"
        # the steps: the Forge's order, each earlier choice ruling which later pieces fit (who is in the picture first)
        cats = {c["id"]: c for c in w["categories"]}
        order = [cid for st in w.get("steps") or [] for cid in st.get("cats") or []]
        if sorted(order) != sorted(cats) or not all(st.get("title") for st in w.get("steps") or []):
            problem(f"{where}: steps must name every category once, each step with a title")
            order = list(cats)
            w["steps"] = [{"title": "The pieces", "cats": order}]
        if not {COMPANY, POSE, HELD, FACE} <= set(cats):
            problem(f"{where}: the Forge's rules need the categories {COMPANY}, {POSE}, {HELD} and {FACE}")
        w["categories"] = [cats[cid] for cid in order if cid in cats]
        pieces = {c["id"]: {o["id"]: o for o in c["options"]} for c in w["categories"]}
        fields = {"with": lambda c, v: v == "alone" or v in pieces.get(COMPANY, {}), "free_hands": lambda c, v: c == POSE and v in (0, 1, 2),
                 "fight": lambda c, v: c == POSE and v is True, "tender": lambda c, v: c == POSE and v is True,
                 "hands": lambda c, v: c == HELD and v in (0, 1, 2), "weapon": lambda c, v: c == HELD and v is True,
                 "mood": lambda c, v: c == FACE and v in ("fierce", "battle")}
        for cat in w["categories"]:
            for o in cat["options"]:
                oid, needs = f'{cat["id"]}.{o["id"]}', o.get("needs") or {}
                if not isinstance(needs, dict) or any(c == cat["id"] or v not in pieces.get(c, {}) for c, v in needs.items()):
                    problem(f"{where}: {oid} needs {needs}: a mapping of other categories to one piece of each")
                    o["needs"] = {}
                bad = [k for k, ok in fields.items() if k in o and not ok(cat["id"], o[k])]
                if bad:
                    problem(f"{where}: {oid}: {', '.join(f'{k}={o[k]!r}' for k in bad)} (with: alone or a companion; pose: free_hands 0-2, fight, tender; "
                            f"{HELD}: hands 0-2, weapon; {FACE}: mood fierce or battle)")
                    for k in bad:
                        del o[k]
        for cat in w["categories"]:
            for o in cat["options"]:
                oid = f'{cat["id"]}.{o["id"]}'
                for c, v in (o.get("needs") or {}).items():  # what the needed piece rules out, this one must rule out too, so choosing it settles in one step
                    y = pieces[c][v]
                    if not o.get("hidden") and y.get("hidden"):
                        problem(f"{where}: {oid} needs a hidden piece, so its greyed entry would name it; hide it too, or need something else")
                    if any(wardrobe_clash(c, y, d["id"], q) and not wardrobe_clash(cat["id"], o, d["id"], q) for d in w["categories"] if d["id"] not in (c, cat["id"]) for q in d["options"]):
                        problem(f"{where}: {oid} needs {c}.{v}, which rules out more than {oid} does; give {oid} the same with, hands or needs")
                # usable: open, and in every other category some open piece goes with it; that is what the reader sees as open
                blocked = [d for d in w["categories"] if d is not cat and not any(q["_open"] and not wardrobe_clash(cat["id"], o, d["id"], q) for q in d["options"])]
                o["_usable"] = o["_open"] and not blocked
                if o["_open"] and blocked:
                    later = [q["name"] for q in blocked[0]["options"] if not q.get("hidden") and not wardrobe_clash(cat["id"], o, blocked[0]["id"], q)]
                    o["_lock"] = "needs " + (later[0] if later else "more pieces")
                elif o["_open"]:
                    o["_lock"] = ""
                o["_shown"] = o["_usable"] or not o.get("hidden")  # a hidden piece is not on the site at all until it can be worn
                ref = o.get("reference")
                if ref and (not all(ref.get(k) for k in ("label", "image", "file", "use")) or not (ART / str(ref["image"])).is_file()):
                    problem(f"{where}: {oid}.reference needs label, image (a picture under saga/art/), file and use")
                elif ref and o["_usable"]:  # checked now, published only once the piece can be worn
                    o["_ref"] = self.reference(ref, f"{where}: {oid}.reference")
            if not any(o["_usable"] for o in cat["options"]):
                problem(f"{where}: {cat['id']} has no piece open; give it one open from the start, so the Forge always has one to show")
        self.wardrobe_reasons(w, where, arts, knots, mid, on_page, paid)
        if earned - known:
            problem(f"saga/state/darrow.json: wardrobe names {', '.join(sorted(earned - known))}, which {where} does not; run python3 engine/darrow.py sync")
        w["_refs"] = [r for r in (self.reference(r, f"{where}: references[{i}]") for i, r in enumerate(w.get("references") or [])) if r]
        self.wardrobe = w
        refs = list(w.get("references") or []) + [o["reference"] for c in w["categories"] for o in c["options"] if o.get("reference")]
        stems = {Path(str(r.get("image"))).stem for r in refs if str(r.get("image")).startswith("looks/")}
        path = STATE / "looks.json"
        book = load_json(path) if path.exists() else {}
        for i, lk in enumerate(book.get("looks", [])):
            lw = f"saga/state/looks.json: looks[{i}]"
            stems.add(Path(str(lk.get("image"))).stem)
            if any(not lk.get(k) for k in ("id", "name", "made", "image", "alt", "values")) or not isinstance(lk["values"], dict):
                problem(f"{lw}: a look needs id, name, made, image, alt and values (a mapping: category → piece id, from the Look line)")
                continue
            bad = [f"{c}={v}" for c, v in lk["values"].items() if v not in pieces.get(c, {})] + [f"{c} missing" for c in pieces if c not in lk["values"]]
            vals = list(lk["values"].items())
            broke = [] if bad else [f"{c}={v} with {d}={u}" for i, (c, v) in enumerate(vals) for d, u in vals[i + 1:]
                                    if wardrobe_clash(c, pieces[c][v], d, pieces[d][u])]
            if bad:
                problem(f"{lw} ({lk['id']}): {', '.join(bad)}: one piece of {where} per category (a piece a look wears is never removed or renamed)")
            elif broke:
                problem(f"{lw} ({lk['id']}): {', '.join(broke)}: pieces that cannot be worn together (engine/wardrobe.json's rules)")
            elif not (ART / lk["image"]).is_file():
                problem(f"{lw} ({lk['id']}): saga/art/{lk['image']} does not exist")
            elif all(pieces[c][v]["_usable"] for c, v in lk["values"].items()):
                got = self.register_image(lw, lk["image"], lk["alt"])
                if got:
                    self.looks.append({**lk, "_path": got[0], "_sm": got[2], "_md": got[3], "_i": i})
        self.looks.sort(key=lambda x: (x["made"], x["_i"]), reverse=True)  # newest first; on a shared date, the later entry
        wearing = book.get("wearing")  # the look he wears on his page, when he has chosen one; else the newest
        if wearing:
            worn = next((lk for lk in self.looks if lk["id"] == wearing), None)
            if worn:
                self.looks.remove(worn)
                self.looks.insert(0, worn)
            else:
                problem(f"saga/state/looks.json: wearing names '{wearing}', which is not a look whose pieces are all open")
        self.stray_pictures("looks", stems, "a look in saga/state/looks.json or a reference in engine/wardrobe.json")

    def wardrobe_reasons(self, w, where, arts, knots, mid, on_page, paid):
        """Why each piece is his, for the picker, the lookbook and the Collection. Each option gets _ch (the chapter it opened
        in: darrow.json → wardrobe for the sheet's conditions, the scene's chapter for the page's; never a date),
        _new (opened this chapter or the one before, the same on every device), _desc (what it looks like: its prompt),
        _tag (the short reason on its card) and _why (the reason in full, as HTML with its links: the scene, the Binding,
        his Arts, his Reckoning). Checks each category's groups and chips, each quote against its scene, the sets and the
        Collection's ranks."""
        rel = "../"
        opened = self.darrow.get("wardrobe") if isinstance(self.darrow.get("wardrobe"), dict) else {}  # piece → chapter (a list: an older sheet)
        now_ch = as_int((self.darrow.get("chapter_now") or {}).get("chapter")) or 0
        proves = {k["n"]: k.get("proves", "") for k in self.rules.get("knots") or []}
        page_ch = lambda key: int(key.split(":")[0]) if key and key.split(":")[0].isdigit() else None
        links = {"knot": ("index.html#binding", "The Binding"), "art": ("index.html#arts", "His Arts"), "level": ("index.html#reckoning", "His Reckoning")}

        def when(n):  # ", in Chapter 6" with its link, or the Prologue
            ch = self.chapter_by_number.get(n) if n is not None else None
            if not ch:
                return ""
            label = "the Prologue" if n == 0 else ch["label"]
            return f', in <a href="{rel}chronicle/{ch["slug"]}.html">{esc(label)}</a>'

        for cat in w["categories"]:
            groups = cat.get("groups")
            gids = [g.get("id") for g in groups or [] if isinstance(g, dict) and g.get("id") and g.get("label")]
            if groups is not None and (not isinstance(groups, list) or len(gids) != len(groups) or len(set(gids)) != len(gids)):
                problem(f"{where}: {cat['id']}.groups must be a list of {{id, label}}, each id once")
            if "chips" in cat and cat["chips"] is not True:
                problem(f"{where}: {cat['id']}.chips is true or absent")
            for o in cat["options"]:
                oid, u = f'{cat["id"]}.{o["id"]}', o["_unlock"]
                if groups is not None and o.get("group") not in gids:
                    problem(f"{where}: {oid} needs a group of {cat['id']}.groups ({', '.join(gids)})")
                elif groups is None and "group" in o:
                    problem(f"{where}: {oid} has a group, but {cat['id']} has no groups")
                story = u["page"] if "page" in u else paid.get(u.get("tether"))  # the page key of the scene that showed it, or paid its Tether stage
                chs = ([opened[oid]] if opened.get(oid) is not None and {"level", "art", "knot"} & set(u) else []) + ([page_ch(story)] if page_ch(story) is not None else [])
                o["_ch"] = max(chs) if o["_usable"] and chs else None
                o["_new"] = o["_ch"] is not None and o["_ch"] >= now_ch - 1
                text = re.sub(r";\s*only .* drawn$", "", o["prompt"]).strip()
                o["_desc"] = "" if text == "none" else text[:1].upper() + text[1:] + ("" if text.endswith(".") else ".")
                q = o.get("quote")
                if q is not None:
                    reg = self.registry.get(tuple(story.split(":", 1))) if story else None
                    if not isinstance(q, str) or len(norm(q)) < 12 or not reg:
                        problem(f"{where}: {oid}.quote needs a page or tether unlock and a verbatim excerpt of that scene, a few words at least")
                        q = None
                    elif norm(q) not in scene_text(reg["scene"]):
                        problem(f"{where}: {oid}.quote is not in {story} as written: {q!r}")
                        q = None
                conds = ([("tether", f'the Tether {roman(u["tether"])}')] if "tether" in u else []) + ([("level", f'Level {u["level"]}')] if "level" in u else []) \
                    + ([("art", f'{mid(arts.get(u["art"], ""))} {roman(u.get("rank", 1))}')] if "art" in u else []) + ([("knot", mid(knots.get(u["knot"], "")))] if "knot" in u else [])
                bare = " + ".join(re.sub(r"^the ", "", n) for _, n in conds)
                named = " and ".join(f"<b>{esc(n)}</b>" for _, n in conds)
                why_knot = f' — {esc(proves.get(u["knot"], ""))}' if "knot" in u and proves.get(u["knot"]) else ""
                go = " · ".join(f'<a href="{h}">{t} →</a>' for k, (h, t) in links.items() if k in u)
                go = f" {go}" if go else ""
                scene = on_page.get(story) if story else None
                if o["_usable"]:
                    kick = "Why he has it"
                    o["_tag"] = "From the start" if not u else "From the story" if not conds else bare
                    if not u:
                        reason = "There from the start."
                    elif not conds:
                        reason = f'From the story: <a href="{rel}{scene[1]}">{esc(scene[0])}</a>.'
                    else:
                        at = f', in <a href="{rel}{scene[1]}">{esc(scene[0])}</a>' if "tether" in u and scene else when(o["_ch"])
                        reason = f'{"Opened at" if [k for k, _ in conds] == ["level"] else "Opened by"} {named}{at}{why_knot}.{go}'
                elif o["_open"]:
                    kick, o["_tag"] = "Not yet", o["_lock"][:1].upper() + o["_lock"][1:]
                    reason = (f'It {esc(o["_lock"])}, which is not open yet.' if o["_lock"] != "needs more pieces"
                              else "Nothing open yet goes with it.")
                else:
                    kick, o["_tag"] = "Not yet", "Opens: " + bare
                    reason = f'{"Opens at" if [k for k, _ in conds] == ["level"] else "Opens with"} {named}{why_knot}.{go}'
                quote = f'<q>{esc(q)}</q>' if q and o["_usable"] else ""
                o["_why"] = (f'<span class="h">{kick}</span><b class="n">{esc(o["name"])}</b>'
                             + (f'<span class="d">{esc(o["_desc"])}</span>' if o["_desc"] else "") + quote + f'<span class="r">{reason}</span>')
        # the sets: pieces that belong together, across categories; a hidden piece is never in one (it would name the secret)
        pieces = {f'{c["id"]}.{o["id"]}': o for c in w["categories"] for o in c["options"]}
        seen = set()
        for i, s in enumerate(w.get("sets") or []):
            if not s.get("id") or s["id"] in seen or not s.get("name") or not s.get("about") or not s.get("pieces"):
                problem(f"{where}: sets[{i}] needs an id (once), a name, an about line and its pieces")
            seen.add(s.get("id"))
            for p in s.get("pieces") or []:
                if p not in pieces:
                    problem(f"{where}: set {s.get('id')} names {p}, which is not a piece (category.piece)")
                elif pieces[p].get("hidden"):
                    problem(f"{where}: set {s.get('id')} names {p}, a hidden piece; a set never shows what is still hidden")
        col = w.get("collection") or {}
        ats = [r.get("at") for r in col.get("ranks") or []]
        if not ats or ats[0] != 0 or any(not isinstance(a, int) for a in ats) or ats != sorted(set(ats)) \
                or not all(r.get("name") for r in col.get("ranks") or []) or not col.get("complete"):
            problem(f"{where}: collection needs ranks [{{at, name}}…] from at 0 upward, each at once, and a name for complete")

    def collection_stats(self):
        """The Collection's count: the pieces he can wear (a hidden one counts once it opens) of every piece, the rank its
        count has reached (engine/wardrobe.json → collection; load checks the ranks start at 0) and the next. Worked out once."""
        if getattr(self, "_col", None) is None:
            w = self.wardrobe
            allp = [o for c in w["categories"] for o in c["options"]]
            have = sum(o["_usable"] for o in allp)
            ranks = (w.get("collection") or {}).get("ranks") or [{"at": 0, "name": "Threadbare"}]
            rank = [r for r in ranks if have >= r["at"]][-1] if have >= ranks[0]["at"] else ranks[0]  # a bad first rank is load's problem, not a crash
            done = have == len(allp)
            self._col = {"have": have, "of": len(allp), "rank": (w.get("collection") or {}).get("complete") if done else rank["name"],
                         "next": next((r for r in ranks if r["at"] > have), None), "ranks": ranks, "rank_at": rank["at"], "complete": done}
        return self._col

    def render_wardrobe(self):
        """The Wardrobe (darrow/wardrobe.html): his looks and the Forge. The stage shows the chosen look if it is painted,
        with its pieces and why each is his under it (the lookbook's details). The Forge goes in steps (who is in the
        picture, the pose, what he holds, him, his dress); each category is a picker in the page, not a menu: a row that
        opens a tray of cards (or, for a short one, a row of chips), each card its piece, what it looks like and the short
        reason it is his, the locked ones greyed with what opens them; a tap on any card shows why in full under the tray.
        Each step offers what goes with the steps before it (wardrobe_clash). The prompt, the references and the Look line
        paint a new one; on a phone, Share sends the prompt and the references to ChatGPT at once (forge.js)."""
        w = self.wardrobe
        if not w:
            return
        rel, d = "../", self.darrow
        cur = self.looks[0] if self.looks else None
        start = dict(cur["values"]) if cur else {}
        if not cur:  # no look yet: in step order, the first open piece that goes with the ones chosen before it
            chosen = []
            for c in w["categories"]:
                o = next((o for o in c["options"] if o["_usable"] and not any(wardrobe_clash(c["id"], o, k, q) for k, q in chosen)), c["options"][0])
                chosen.append((c["id"], o))
                start[c["id"]] = o["id"]
        col = self.collection_stats()
        hide = "" if cur else " hidden"
        href = f' href="{rel}{cur["_path"]}"' if cur else ""  # no look yet: nothing to fetch
        img = f' src="{rel}{cur["_path"]}" alt="{esc(cur["alt"])}"' if cur else ' alt=""'  # the stage is large: the full picture, not a copy
        stage = (f'<a id="forge-zoom"{href} data-zoom{hide}><img id="forge-img"{img} decoding="async"></a>'
                 f'<div class="forge-empty" id="forge-empty"{"" if not cur else " hidden"}><span class="glyph" aria-hidden="true">✧</span>'
                 '<b>Not painted yet</b><span>Every piece is chosen; the prompt below will paint it.</span></div>')
        plate = (f'<section class="plate wardrobe-plate{self.metal(d["level"])}"><p class="lbl"><a href="index.html">Ser Darrow of Edgemoor</a></p>'
                 '<h1>The Wardrobe</h1><p class="sub">Looks he has earned; more opens as he grows.</p>'
                 f'<div class="chips"><a class="chip brass" href="collection.html">The Collection · {esc(col["rank"])} · {col["have"]} of {col["of"]}</a></div>'
                 f'<figure class="forge-stage" id="forge-stage">{stage}</figure>'
                 f'<p class="forge-cap"><b id="forge-name">{esc(cur["name"]) if cur else "A new look"}</b>'
                 f'<span class="lbl" id="forge-state">{"his look now" if cur else "not painted yet"}</span></p>'
                 '<details class="tip look-detail" id="look-detail" hidden><summary>What he wears, and why</summary><ul class="look-pieces" id="look-pieces"></ul></details>'
                 '<div class="btn-row" id="look-wear-row" hidden><button class="btn ghost" type="button" id="look-wear">Make this his look</button></div>'
                 '<p class="hint" id="look-wear-hint" hidden>Copied. Send it to Claude, and this look goes on his page.</p></section>')
        tiles = "".join(f'<a class="look-tile" href="{rel}{lk["_path"]}" data-look="{esc(lk["id"])}"><img src="{rel}{lk["_md"]}" alt="" loading="lazy" decoding="async">'
                        f'{"<i class=" + chr(34) + "look-worn" + chr(34) + ">His look</i>" if lk is cur else ""}<span>{esc(lk["name"])}</span></a>' for lk in self.looks)
        n = len(self.looks)
        book = sec("The lookbook", f'{n} look{"" if n == 1 else "s"}', (f'<div class="look-grid">{tiles}</div>'
                   if tiles else '<p class="empty">No look painted yet.</p>'))
        shown = {c["id"]: [o for o in c["options"] if o["_shown"]] for c in w["categories"]}
        n_all = sum(len(v) for v in shown.values())
        n_open = sum(o["_usable"] for v in shown.values() for o in v)
        n_hidden = sum(len(c["options"]) for c in w["categories"]) - n_all
        label = {c["id"]: c["label"] for c in w["categories"]}
        lock = svg_lock(11)
        new = '<i class="new">New</i>'

        def card(cid, o):  # a piece in a tray: its name, what it looks like, and the short reason it is his (or what opens it)
            desc = f'<span class="d">{esc(o["_desc"])}</span>' if o["_desc"] else ""
            return (f'<button type="button" class="pc{"" if o["_usable"] else " locked"}" role="radio" aria-checked="false" data-id="{esc(o["id"])}" id="piece-{esc(cid)}-{esc(o["id"])}"'
                    f'{"" if o["_usable"] else ' aria-disabled="true"'}><b>{"" if o["_usable"] else lock}{esc(o["name"])}</b>{desc}'
                    f'<span class="t">{new if o["_new"] else ""}{esc(o["_tag"])}</span></button>')

        def chip_(cid, o):  # a piece in a short category: its name, and what opens it while locked
            return (f'<button type="button" class="pchip{"" if o["_usable"] else " locked"}" role="radio" aria-checked="false" data-id="{esc(o["id"])}" id="piece-{esc(cid)}-{esc(o["id"])}"'
                    f'{"" if o["_usable"] else ' aria-disabled="true"'}>{"" if o["_usable"] else lock}{esc(o["name"])}'
                    f'{"" if o["_usable"] else "<small>" + esc(re.sub(r"^Opens: ", "", o["_tag"])) + "</small>"}{new if o["_new"] else ""}</button>')

        def who(o):  # a card for who is in the picture: their reference's small copy, or a mark for him alone
            pic = (f'<img src="{rel}{o["_ref"]["sm"]}" alt="" loading="lazy" decoding="async">' if o.get("_ref")
                   else '<span class="glyph" aria-hidden="true">✧</span>')
            lk = "" if o["_usable"] else f'<span class="who-lock">{esc(o["_tag"])}</span>'
            return (f'<button type="button" class="who-btn{"" if o["_usable"] else " locked"}" role="radio" aria-checked="false" data-id="{esc(o["id"])}" id="piece-{COMPANY}-{esc(o["id"])}"'
                    f'{"" if o["_usable"] else ' aria-disabled="true"'}>'
                    f'<span class="who-pic">{pic}</span><b>{esc(o["name"])}{new if o["_new"] else ""}</b>{lk}</button>')

        def picker(cid):
            c = next(c for c in w["categories"] if c["id"] == cid)
            opts = shown[cid]
            if cid == COMPANY:
                return (f'<div class="pk pk-who" data-cat="{esc(cid)}"><div class="who-grid" role="radiogroup" aria-label="{esc(label[cid])}">'
                        f'{"".join(who(o) for o in opts)}</div><div class="pk-info" aria-live="polite"></div></div>')
            if c.get("chips"):
                n_locked = sum(not o["_usable"] for o in opts)
                more = (f'<button type="button" class="pchip more" data-more="{n_locked}" aria-expanded="false">{lock}{n_locked} more</button>'
                        if n_locked else "")
                return (f'<div class="pk pk-chipset" data-cat="{esc(cid)}"><span class="pk-lbl" id="pk-l-{esc(cid)}">{esc(label[cid])}</span>'
                        f'<div class="pk-chips" role="radiogroup" aria-labelledby="pk-l-{esc(cid)}">{"".join(chip_(cid, o) for o in opts)}{more}</div>'
                        f'<div class="pk-info sm" aria-live="polite"></div></div>')
            if c.get("groups"):
                inner = "".join(f'<p class="pk-g" data-g="{esc(g["id"])}">{esc(g["label"])}</p><div class="pk-grid" role="radiogroup" data-g="{esc(g["id"])}" '
                                f'aria-label="{esc(label[cid])}: {esc(g["label"])}">{"".join(card(cid, o) for o in opts if o.get("group") == g["id"])}</div>'
                                for g in c["groups"] if any(o.get("group") == g["id"] for o in opts))
            else:
                inner = f'<div class="pk-grid" role="radiogroup" aria-label="{esc(label[cid])}">{"".join(card(cid, o) for o in opts)}</div>'
            return (f'<div class="pk" data-cat="{esc(cid)}"><button type="button" class="pk-row" aria-expanded="false" aria-controls="pk-tray-{esc(cid)}">'
                    f'<span class="pk-row-t"><span class="pk-lbl">{esc(label[cid])}</span><b class="pk-cur"></b><span class="pk-tag"></span></span>'
                    f'<span class="pk-row-r"><span class="pk-cnt"></span><span class="chev" aria-hidden="true"></span></span></button>'
                    f'<div class="pk-tray" id="pk-tray-{esc(cid)}" hidden>{inner}<div class="pk-info" aria-live="polite"></div></div></div>')

        steps = []
        for i, st in enumerate(w["steps"], 1):
            steps.append(f'<fieldset class="forge-step"><legend><span class="step-n">{i}</span>{esc(st["title"])}</legend>'
                         f'<div class="forge-stack">{"".join(picker(cid) for cid in st["cats"])}</div></fieldset>')
        secret = ("" if not n_hidden else " One more stays hidden until it opens." if n_hidden == 1
                  else f" {n_hidden} more stay hidden until they open.")
        fresh = [o["name"] for c in w["categories"] for o in shown[c["id"]] if o["_new"] and o["_usable"]]
        fresh_html = (f'<details class="tip"><summary>New this chapter · {len(fresh)}</summary><p class="hint">{esc(" · ".join(fresh))}</p></details>' if fresh else "")
        forge = sec("The Forge", f"{n_open} of {n_all} pieces open",
                    f'<div class="forge"><div class="tips"><details class="tip"><summary>How it works</summary><p class="hint">Choose from what he has earned, a step at a time: '
                    f'each step offers only what goes with the steps before it. Tap any piece, open or not, to see what it looks like and where it comes from.{secret}</p></details>'
                    f'{fresh_html}</div>{"".join(steps)}'
                    '<p class="forge-fit" id="forge-fit" aria-live="polite" hidden></p>'
                    '<details class="tip forge-notes"><summary>Small touches · optional</summary><textarea id="forge-details" rows="2" aria-label="Small touches" '
                    'placeholder="a scar on the brow, rain on the cloak, wind in his hair"></textarea></details>'
                    '<p class="forge-result" id="forge-result" aria-live="polite"></p></div>')
        cards = [self.ref_card(r, rel, n=i + 1) for i, r in enumerate(w["_refs"])]
        cards += [self.ref_card(o["_ref"], rel, f'{c["id"]}.{o["id"]}') for c in w["categories"] for o in c["options"] if o.get("_ref")]
        paint = sec("Paint it", "", '<details class="tip"><summary>How to paint it</summary><ol class="forge-steps">'
                    '<li id="forge-share-step" hidden>Tap <b>Share to ChatGPT</b> and choose ChatGPT: the references go with it, in order, and the prompt is copied too. '
                    'If it arrives without the words, paste them.</li>'
                    '<li class="forge-manual">Copy the prompt.</li><li class="forge-manual">Download the references and attach them to your ChatGPT message in order, Image 1 first.</li>'
                    '<li>Send it. If the background comes back as anything but one flat, bright colour behind him, reply: '
                    '<i>Put the picture on one solid, flat background of the colour the prompt names, edge to edge, and nothing else.</i></li>'
                    '<li>Send the finished picture to Claude with the Look line: it goes into the lookbook for good.</li></ol></details>'
                    '<div class="btn-row"><button class="btn" type="button" id="forge-share" hidden>Share to ChatGPT</button>'
                    '<button class="btn" type="button" id="forge-copy">Copy prompt</button>'
                    '<a class="btn ghost" href="https://chatgpt.com/" target="_blank" rel="noopener">Open ChatGPT</a></div>'
                    '<p class="hint" id="forge-share-note" hidden></p>'
                    f'<div class="ref-grid">{"".join(cards)}</div>'
                    '<div class="btn-row"><button class="btn ghost" type="button" id="forge-copy-line">Copy the Look line</button></div>'
                    '<details class="tip"><summary>See the prompt and the Look line</summary>'
                    '<textarea class="forge-prompt" id="forge-prompt" readonly rows="10" aria-label="The image prompt"></textarea>'
                    '<p class="lbl">The Look line</p><code class="look-line" id="forge-line"></code></details>'
                    '<noscript><p class="empty">The Forge needs JavaScript; the lookbook works without it.</p></noscript>')
        flat = [(c["id"], o) for c in w["categories"] for o in shown[c["id"]]]
        data = {"cats": [{"id": c["id"], "label": c["label"], "options": [
                    {"id": o["id"], "name": o["name"], "prompt": o["prompt"], "open": o["_usable"], "tag": o["_tag"], "why": o["_why"]}
                    for o in shown[c["id"]]]} for c in w["categories"]],
                "clash": [[f"{ca}.{a['id']}", f"{cb}.{b['id']}"] for i, (ca, a) in enumerate(flat) for cb, b in flat[i + 1:]
                          if ca != cb and wardrobe_clash(ca, a, cb, b)],  # the pairs that cannot be worn together, among the pieces on the page
                "refs": [{"file": r["file"], "use": r["use"], "href": rel + r["href"]} for r in w["_refs"]],
                "optRefs": {f'{c["id"]}.{o["id"]}': {"file": o["_ref"]["file"], "use": o["_ref"]["use"], "href": rel + o["_ref"]["href"]}
                            for c in w["categories"] for o in c["options"] if o.get("_ref")},
                "looks": [{"id": lk["id"], "name": lk["name"], "alt": lk["alt"], "values": lk["values"], "details": lk.get("details") or "",
                           "full": rel + lk["_path"], "worn": lk is cur} for lk in self.looks],
                "start": start, "company": COMPANY, "template": "\n".join(w["prompt"])}
        for c in data["cats"]:  # the names and notes the Forge shows get the page's curly quotes; the prompt stays as written
            for o in c["options"]:
                for k in ("name", "tag"):
                    if isinstance(o.get(k), str):
                        o[k] = curl(o[k])[0]
                if isinstance(o.get("why"), str):
                    o["why"] = smart_quotes(o["why"])  # HTML: its links keep their straight attribute quotes
        for lk in data["looks"]:
            for k in ("name", "alt", "details"):
                if isinstance(lk.get(k), str):
                    lk[k] = curl(lk[k])[0]
        blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
        body = (plate + book + forge + paint + f'<script type="application/json" id="forge-data">{blob}</script>'
                f'<script src="{rel}forge.js?v={asset_v("forge")}" defer></script>')
        self.pages["darrow/wardrobe.html"] = shell("The Wardrobe", body, rel, "Darrow", "wardrobe-page", desc="Darrow's looks, and the Forge that paints new ones.")

    def render_collection(self):
        """The Collection (darrow/collection.html): every piece of the Wardrobe and where it came from. His rank (the count
        of pieces he can wear against engine/wardrobe.json → collection.ranks) with the bar to the next and the ladder; the
        sets, each with its pieces and a seal once whole; then a shelf per category, every piece on it with its reason and
        the chapter it opened in, the locked ones greyed with what opens them, the hidden ones only counted. A piece opens
        its card in the Forge (wardrobe.html#piece-<category>-<piece>)."""
        w = self.wardrobe
        if not w:
            return
        rel, d = "../", self.darrow
        col = self.collection_stats()
        pieces = {f'{c["id"]}.{o["id"]}': o for c in w["categories"] for o in c["options"]}
        lock, new = svg_lock(11), '<i class="new">New</i>'
        nxt = col["next"]
        if col["complete"]:
            meter = '<p class="col-next">Every piece in the Wardrobe is his.</p>'
        elif nxt:
            meter = (bar(col["have"] - col["rank_at"], nxt["at"] - col["rank_at"], "Toward " + nxt["name"], "brass", show=f'{col["have"]} of {nxt["at"]}')
                     + f'<p class="col-next">Next: <b>{esc(nxt["name"])}</b> at {nxt["at"]} pieces.</p>')
        else:
            meter = f'<p class="col-next">Every rank reached. {col["of"] - col["have"]} pieces still to open.</p>'
        ladder = "".join(f'<li class="{"on" if col["have"] >= r["at"] else ""}{" cur" if r["at"] == col["rank_at"] and not col["complete"] else ""}">'
                         f'<span class="num">{r["at"]}</span><b>{esc(r["name"])}</b></li>' for r in col["ranks"])
        ladder += f'<li class="{"on cur" if col["complete"] else ""}"><span class="num">all</span><b>{esc((w.get("collection") or {}).get("complete", ""))}</b></li>'
        ladder = f'<ol class="col-ladder col-rail">{ladder}</ol>'
        plate = (f'<section class="plate col-plate{self.metal(d["level"])}"><p class="lbl"><a href="index.html">Ser Darrow of Edgemoor</a> · <a href="wardrobe.html">The Wardrobe</a></p>'
                 '<h1>The Collection</h1><p class="sub">Every piece he can wear, and where each one came from. More opens as he grows, and as the story shows him new things.</p>'
                 f'<div class="col-rank"><span class="lbl">His rank</span><b>{esc(col["rank"])}</b><span class="num col-count">{col["have"]} of {col["of"]} pieces</span></div>'
                 f'{meter}{ladder}</section>')

        def tile(cid, o, ic=False):  # ic: the category's glyph before the name, where tiles of several categories sit together (a set)
            ch = (f' · in the Prologue' if o["_ch"] == 0 else f' · Chapter {o["_ch"]}') if o["_usable"] and o["_ch"] is not None else ""
            return (f'<li><a class="ctile{"" if o["_usable"] else " locked"}" href="wardrobe.html#piece-{esc(cid)}-{esc(o["id"])}">'
                    f'<b>{glyph(cid, 14) if ic else ""}{"" if o["_usable"] else lock}{esc(o["name"])}</b>'
                    f'<span class="t">{new if o["_new"] else ""}{esc(o["_tag"])}{esc(ch)}</span></a></li>')

        sets, n_whole = [], 0
        for s in w.get("sets") or []:
            mem = [(p.split(".")[0], pieces[p]) for p in s.get("pieces") or [] if p in pieces]
            have = sum(o["_usable"] for _, o in mem)
            whole = bool(mem) and have == len(mem)
            n_whole += whole
            seal = f'{seal_whole(30)}<span class="sr">whole</span>' if whole else ""
            sets.append(f'<div class="cset{" whole" if whole else ""}"><div class="cset-h"><b>{esc(s["name"])}</b>'
                        f'<span class="num">{have} of {len(mem)}</span>{seal}</div>'
                        f'<p class="m">{esc(s["about"])}</p>{pips(have, len(mem), "brass")}'
                        f'<ul class="ctiles sm">{"".join(tile(c, o, True) for c, o in mem)}</ul></div>')
        sets_html = sec("The sets", f"{n_whole} of {len(sets)} whole", f'<div class="csets">{"".join(sets)}</div>') if sets else ""
        shelves = []
        for c in w["categories"]:
            opts = [o for o in c["options"] if o["_shown"]]
            hid = len(c["options"]) - len(opts)
            have = sum(o["_usable"] for o in c["options"])
            if c.get("groups"):
                inner = "".join(f'<p class="pk-g">{esc(g["label"])}</p><ul class="ctiles">{"".join(tile(c["id"], o) for o in opts if o.get("group") == g["id"])}</ul>'
                                for g in c["groups"] if any(o.get("group") == g["id"] for o in opts))
            else:
                inner = f'<ul class="ctiles">{"".join(tile(c["id"], o) for o in opts)}</ul>'
            if hid:
                inner += f'<p class="hint col-hidden"><span class="glyph" aria-hidden="true">?</span> {hid} more {"stays" if hid == 1 else "stay"} hidden until {"it opens" if hid == 1 else "they open"}.</p>'
            shelves.append(panel(c["label"], f'{glyph(c["id"], 16)}{have} of {len(c["options"])}', inner, f'shelf-{c["id"]}'))
        body = plate + sets_html + sec("The shelves", f'{col["have"]} of {col["of"]}', f'<div class="panels">{"".join(shelves)}</div>'
                                       '<p class="hint">Tap a piece to see it in the Forge.</p>')
        self.pages["darrow/collection.html"] = shell("The Collection", body, rel, "Darrow", "collection-page", desc="Every piece of Darrow's Wardrobe, and where each came from.")

    @staticmethod
    def ref_card(r, rel, for_piece="", n=0):
        """A reference to download and attach, numbered in the order the prompt names them (Image 1, Image 2…); one a
        piece brings (for_piece) shows only while that piece is chosen, and the Forge numbers it then."""
        if not r:
            return ""
        attr = f' data-ref-for="{esc(for_piece)}" hidden' if for_piece else ""
        return (f'<a class="ref-card" href="{rel}{r["href"]}" download="{esc(r["file"])}"{attr}><img src="{rel}{r["sm"]}" alt="" loading="lazy" decoding="async">'
                f'<span class="ref-t"><i class="ref-n">{f"Image {n}" if n else ""}</i><b>{esc(r["label"])}</b><span class="ref-d">Download</span></span></a>')

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
        """The latest checks: one entry per check, its casts in order (a cast, Inspiration spent, the cast again: the
        rolls.csv labels chain as label, label#reroll, label#reroll#reroll), the outcome of the last cast on the top line,
        the arithmetic of each cast on its own line, and where it was cast."""
        groups, order = {}, []
        for r in sorted(self.rolls, key=lambda r: r.get("when", "")):
            base = (r.get("label") or "").split("#")[0]
            if base not in groups:
                groups[base] = []
                order.append(base)
            groups[base].append(r)
        latest = [groups[b] for b in order[::-1][:n]]
        if not latest:
            return '<p class="empty">No dice have been cast yet.</p>'
        rows = []
        for casts in latest:
            first, last = casts[0], casts[-1]
            res = last.get("result", "")
            cls = "good" if "SUCCESS" in res else ("warn" if "PARTIAL" in res else "bad")
            where = self.roll_where(first.get("label", ""), rel)
            times = f'<span class="roll-times">cast ×{len(casts)}</span>' if len(casts) > 1 else ""
            lines = []
            for i, c in enumerate(casts):
                if i:
                    note = (c.get("note") or "").lower()
                    how = "paid at the choice" if "paid by the choice" in note else "spent"
                    lines.append(f'<li class="roll-insp"><span class="insp-glyph" aria-hidden="true">✦</span>Inspiration {how} · cast again</li>')
                d20 = c.get("d20", "") + (f"/{c['d20_b']}" if c.get("d20_b") else "")
                cres = c.get("result", "")
                sup = " superseded" if i < len(casts) - 1 else ""
                lines.append(f'<li class="roll-cast{sup}">{d20_glyph(c.get("d20"), cres, 26)}<span class="roll-math num">d20 <b>{esc(d20)}</b> {esc(c.get("mods", ""))} = <b>{esc(c.get("total"))}</b></span>'
                             f'<span class="roll-res">{esc(cres.title())}</span></li>')
            rows.append(f'<li class="roll"><div class="roll-top">{d20_glyph(last.get("d20"), res)}<span class="dice-tag">{esc(first.get("stat", "").upper() or "FLAT")} · DC {esc(first.get("dc"))}</span>{times}'
                        f'{badge(res.title(), cls)}</div>'
                        f'<details class="roll-more"><summary>the roll</summary><ul class="roll-casts">{"".join(lines)}</ul></details>'
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
        return f'<div class="knots-brief">{rope_knots(tied, knots)}<p class="m">{line}.</p>{self.tether_thread(line=False)}{soft}</div>'

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
        detail = loc.get("detail") if isinstance(loc, dict) else ""
        pname = place.get("name", "")
        bare = re.sub(r"^the\s+", "", pname.lower())
        if detail and bare and bare in detail.lower():  # the detail already names the place: say it once
            where = detail[:1].upper() + detail[1:]
        else:
            where = pname + (f", {detail}" if detail else "")
        scene_row = ""
        if latest and after:  # the newest piece is a Between: the scene it follows gets its own row
            scene_row = (f'<dt>Latest scene</dt><dd><a href="{rel}chronicle/{ch["slug"]}.html#{latest["anchor"]}">{glyph(self.scene_kind(latest), 14)}'
                         f'{esc((latest["label"] + " — " if latest["label"] else "") + latest["title"])}</a></dd>')
        book_line = f"Book {roman(w.get('book', 1))} — {w['book_title']}" if w.get("book_title") else ""
        tier = (d.get("chapter_now") or {}).get("tier_so_far")
        tier_chip = (f'<div class="seal-row">{svg_seal(tier, 30, open_=True)}{chip(TIER_SO_FAR[tier], TIER_CLS.get(tier, ""))}</div>'
                     if tier in TIER_SO_FAR else "")
        plate = (f'<section class="plate now-plate"{self.place_backdrop(place, rel)}><p class="lbl">{esc(book_line)}</p>'
                 f'<h1>{esc("Chapter " + str(w.get("chapter")) + " — " + w.get("chapter_title", ""))}</h1>{tier_chip}'
                 f'<dl class="kv"><dt>Where</dt><dd>{esc(where)}</dd><dt>Season</dt><dd>{esc(w.get("season", ""))}</dd>{scene_row}</dl>'
                 f'<div class="beat"><span class="lbl">Just happened</span><p>{esc(w.get("last_beat", ""))}</p></div>{self.continue_button(rel)}</section>')
        q = w.get("current_quest") or {}
        work = "".join(f'<div class="qrow"><span class="qic">{glyph("work", 18)}</span><div><span class="lbl">Work in hand</span>'
                       f'<p class="prose">{esc(pr.get("name", ""))}, stage {pr.get("stage")} of {pr.get("of")}: {esc(pr.get("visible", ""))}</p>'
                       f'{pips(as_int(pr.get("stage")) or 0, as_int(pr.get("of")) or 1, "brass") if as_int(pr.get("of")) else ""}</div></div>'
                       for pr in getattr(self, "projects", []) or [] if pr.get("status") == "live")
        qlog = (f'<div class="qlog"><div class="qhead">{glyph("quest", 22)}<b>{esc(q.get("name", ""))}</b></div>'
                f'<p class="obj">{esc(q.get("on_the_page", ""))}</p>'
                f'<div class="qrow"><span class="qic">{glyph("swords", 18)}</span><div><span class="lbl">What he is fighting</span>'
                f'<p class="prose">{esc(w.get("current_struggle", ""))}</p></div></div>{work}</div>')
        quest = sec("The quest", "", qlog)
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
            open_html = sec(self.choice_title(oc["kind"], None, oc["scene"]["key"]), "",
                            self.choice_list(oc["items"]) + f'<p class="dim">From <a href="{rel}chronicle/{oc["chapter"]["slug"]}.html#{oc["scene"]["anchor"]}">{esc(oc["chapter"]["label"] + " — " + oc["scene"]["title"])}</a>.</p>',
                            cls="choice-open", label_html=glyph("choice", 15) + " waiting on Darrow")
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
            mood = approval_word(int(comp["approval"])) if "approval" in comp else "at his side"
            regard = (bar(int(comp["approval"]) + 100, 200, "Regard for Darrow", "approval", text=mood, quiet=True) if "approval" in comp else "")
            comps.append(f'<a class="comp" href="{rel}{self.char_href(cid)}">{self.avatar_crest(c, rel, 48, "sm")}'
                         f'<div><div class="comp-top"><b>{esc(c["name"])}</b><span class="lbl">{mood_mark(mood)}{esc(mood)}</span></div>'
                         f'<span class="m">{esc(c.get("last_seen_doing", ""))}</span>{regard}</div></a>')
        companions = sec("With him", "", f'<div class="comps">{"".join(comps)}</div>' if comps else '<p class="empty">No one yet.</p>')
        a = d["attributes"]
        rk = "".join(f'<div class="mini-attr{" hot" if a[k]["score"] >= a[k]["fell"] else ""}">{medallion(k.capitalize(), a[k]["score"], a[k]["mod"], a[k]["fell"], 48)}'
                     f'<span class="lbl">{k.capitalize()}</span></div>'
                     for k in ("might", "vigor", "finesse", "resolve"))
        bchip = (self.bearing_chip() or "") + self.tether_chip() + self.works_chip()
        card = (f'<div class="rk-mini"><div class="hero{self.metal(d["level"])}">{self.avatar(self.chars.get("darrow"), rel, 86, "big") or crest(d["level"])}<div class="who"><h3>{esc(d["name"])}</h3><p class="sub">Level {d["level"]} · {esc(d["rank"])}</p>'
                f'<div class="chips">{chip_glyph("hp", "HP " + str(d["hp_max"]))}{chip_glyph("prof", "Proficiency +" + str(d["proficiency"]))}</div>'
                f'<div class="insp"><span class="lbl">Inspiration</span>{pips(d["inspiration"], d["inspiration_cap"], "spark")}</div>'
                + (f'<div class="chips">{bchip}</div>' if bchip else "") + '</div></div>'
                f'{self.xp_bar()}'
                f'<div class="mini-attrs">{rk}</div><p class="hint">The faint numbers are the ones he read behind his own.</p>'
                f'{self.ember_bar()}'
                f'{self.knots_brief(rel)}'
                f'<p class="links"><a href="{rel}darrow/index.html#reckoning">The full Reckoning</a> · <a href="{rel}darrow/index.html#binding">All the Knots</a></p></div>')
        reck = sec("The Reckoning", "", card)
        base = None
        if self.map_base:
            reg = self.register_image("places.json base_image", self.map_base.get("image"), self.map_base.get("alt"))
            base = (rel + reg[0]) if reg else None
            self.thumb_missing.discard(Path(str(self.map_base.get("image"))).as_posix())  # the map always shows it whole
        map_html = sec("The map", "", svg_map(self.places, self.route, self.current_place, rel, base)
                       + '<p class="legend"><span><span class="lg ember">●</span> Darrow</span> <span><span class="lg brass">●</span> visited</span> <span><span class="lg faint">●</span> not yet</span> '
                       '<span><svg class="lg-route" width="22" height="6" aria-hidden="true"><path d="M1 3 H21"/></svg> the road so far</span></p>'
                       '<p class="hint">Tap a name on the map to read about the place.</p>')
        dice = sec("The dice", "", self.dice_html(rel))
        body = self.level_news(rel) + self.wardrobe_news(rel) + plate + open_html + quest + companions + reck + tales_html + map_html + answered_html + dice
        self.pages["index.html"] = shell("Now", body, rel, "Now", "now-page", desc="What is going on now in The Unkneeling.")

    def place_backdrop(self, place, rel):
        """The style attribute that puts the place he is at faint behind the Now plate (site.css .now-plate::before): its
        medium copy and its focus. Empty until the place and its picture are on the page."""
        if not (place.get("on_page") and place.get("image")):
            return ""
        reg = self.register_image(f"places.json {place.get('id')} image", place["image"], place.get("image_alt"))
        if not reg:
            return ""
        m = re.fullmatch(r"\s*(\d{1,3})%\s+(\d{1,3})%\s*", str(place.get("image_focus") or ""))
        focus = f"{m.group(1)}% {m.group(2)}%" if m else "50% 50%"
        return f' style="--bg:url({rel}{reg[3]});--focus:{focus}"'

    def level_news(self, rel):
        """The level-up banner at the head of the Now page, for LEVEL_NEWS_DAYS after the level came: the crest in the
        rank's metal, the level, and the sheet's HP and proficiency as they stand; a level that opens a rank names it."""
        d = self.darrow
        if not d.get("level_reached"):
            return ""
        if not 0 <= (dt.date.fromisoformat(d["asof"]) - dt.date.fromisoformat(d["level_reached"])).days <= LEVEL_NEWS_DAYS:
            return ""
        new_rank = any(r["from"] == d["level"] for r in self.rules["levels"]["ranks"])
        head = f'Level {d["level"]}' + (f' · {esc(d["rank"])}' if new_rank else "")
        line = ("A new rank. " if new_rank else "") + f'HP {d["hp_max"]} · Proficiency +{d["proficiency"]}'
        return (f'<a class="lvl-news{self.metal(d["level"])}" href="{rel}darrow/index.html#reckoning">{crest(d["level"])}'
                f'<span><span class="lbl">A new level</span><b>{head}</b><span class="m">{line}</span></span></a>')

    def wardrobe_news(self, rel):
        """New in the Wardrobe, at the head of the Now page: every piece opened this chapter or the one before, whatever
        opened it (a level, an Art, a Knot, a scene, the Tether), the same on every device, with the Collection's rank.
        Nothing when no piece is new."""
        w = self.wardrobe
        if not w:
            return ""
        names = [o["name"] for c in w["categories"] for o in c["options"] if o["_new"]]
        if not names:
            return ""
        col = self.collection_stats()
        some = " · ".join(esc(x) for x in names[:4]) + (f" · and {len(names) - 4} more" if len(names) > 4 else "")
        return (f'<a class="ward-news" href="{rel}darrow/wardrobe.html"><span class="glyph" aria-hidden="true">✧</span>'
                f'<span><span class="lbl">New in the Wardrobe</span><b>{len(names)} new piece{"" if len(names) == 1 else "s"}</b>'
                f'<span class="m">{some}</span><span class="m faint">The Collection: {esc(col["rank"])} · {col["have"]} of {col["of"]}</span></span></a>')

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
                f'<li{(" id=" + chr(34) + it["id"] + chr(34)) if it.get("id") else ""}><details><summary><span><span class="rn num">{i}</span>{esc(it["name"])}</span>{it.get("tag", "")}</summary><div class="dt-body">{it["html"]}</div></details></li>'
                for i, it in enumerate(items, start)) + "</ol>"

        def add(title, sid, count, inner, kind="", label_html=""):
            secs.append(sec(title, str(count), inner, hid=sid, label_html=label_html))
            jumps.append(f'<a class="chip ic-chip" href="#{sid}">{glyph(kind, 13) if kind else ""}{esc(title)}</a>')

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
        n_places = len(been) + len(named)
        found = f'<span class="num">{len(been)} of {n_places} reached</span>' if n_places else ""
        add("Places", "places", n_places, inner or '<p class="empty">Nothing yet.</p>', kind="place", label_html=found)
        facs = []
        for f in self.factions.values():
            if not f.get("on_page"):
                continue
            facs.append({"name": f["name"], "id": f"faction-{f['id']}", "tag": self.codex_thumb(f, rel),
                         "html": self.codex_figure(f, rel) + f'<div class="fac">{sigil(f, None, 44)}<p>{esc(f["description"])}</p></div>'})
        add("Factions", "factions", len(facs), rows(facs), kind="faction")
        sayings = [{"name": s["name"].strip('"“”'), "tag": "", "html": f"<p>{inline(s['text'])}</p>"} for s in self.codex.get("Sayings", [])]
        add("Sayings", "sayings", len(sayings), rows(sayings), kind="saying")
        things, beasts, extra = [], [], {}
        for key, bucket, e, anchor in self.codex_things():
            item = {"name": e["name"], "id": anchor, "tag": self.codex_thumb(e, rel),
                    "html": self.codex_figure(e, rel) + self.codex_song(e, rel) + f"<p>{inline(e['text'])}</p>"}
            (things if bucket == "things" else beasts if bucket == "beasts" else extra.setdefault(key, [])).append(item)
        add("Things", "things", len(things), rows(things) if things else '<p class="empty">Nothing yet.</p>', kind="thing")
        if beasts:
            add("Beasts and others", "beasts", len(beasts), rows(beasts), kind="beast")
        for key, items in extra.items():
            if items:
                add(key, "sec-" + slug(key), len(items), rows(items), kind="song" if "song" in key.lower() or "verse" in key.lower() else "scene")
        jump = f'<nav class="jump chips" aria-label="Codex sections">{"".join(jumps)}</nav>'
        body = ('<section class="plate"><p class="lbl">The Codex</p><h1>Places, factions, sayings</h1><p class="dim">Only what the page has shown. '
                f'Names on the map that the story has not reached yet are names and nothing more.</p>{jump}</section>' + "".join(secs))
        self.pages["codex/index.html"] = shell("Codex", body, rel, "Codex", desc="Places, factions and sayings of The Unkneeling.")

    # ---------------------------------------------------------------- run
    def build(self):
        self.load_wardrobe()
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
        self.render_wardrobe()
        self.render_collection()
        self.render_now()
        self.render_codex()
        self.pages["site.css"] = CSS
        self.pages["site.js"] = JS
        self.pages["forge.js"] = FORGE_JS
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
             r"treadmill", r"gym", r"supplements?", r"step-downs?", r"post-op",
             r"sports?", r"frisbees?"]
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
Antagonists Voice Wants Fears Hides Carries Flaw Arc Rank Ranks Might Vigor Finesse Resolve Insight Blade Breath Footing Binding Arts Art
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
    s = html.unescape(s).translate(STRAIGHT)
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
        low_re = re.compile(r"\b(" + "|".join(re.escape(n.lower()) for n in sorted(names, key=len, reverse=True)) + r")\b")  # whole words: "grandmother" does not name a "Grand"
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


# ============================================================ typography
# Curly quotes for the published pages: “ ” ‘ ’ in place of " and '. It runs after every check, on the finished HTML: text
# only (never inside a tag, a script, a style or code), plus the link previews' text and the alt and title attributes.
STRAIGHT = str.maketrans({"“": '"', "”": '"', "‘": "'", "’": "'"})
QUOTE_SKIP = ("script", "style", "code", "pre", "textarea")
QUOTE_INLINE = ("a", "i", "b", "em", "strong", "s", "span", "small", "sup", "sub", "abbr", "mark", "u", "q", "cite")
QUOTE_ATTR_RE = re.compile(r'(\s(?:data-pv-[tsxz]|alt|title|aria-label)=")([^"]*)(")')


def curl(text, prev=" "):
    """(text with curly quotes, its last character). prev is the character before the text (a space at a block's start)."""
    out = []
    n = len(text)
    for i, ch in enumerate(text):
        nxt = text[i + 1] if i + 1 < n else ""
        if ch == '"':
            if prev.isspace() or prev in "([{“‘":
                ch = "“"
            elif prev in "—–-/":  # after a dash: opening only when a word follows at once
                ch = "“" if nxt.isalnum() else "”"
            else:
                ch = "”"
        elif ch == "'":
            ch = "‘" if (prev.isspace() or prev in "([{“—–") and nxt.isalpha() else "’"
        out.append(ch)
        prev = ch
    return "".join(out), prev


def curl_attr(m):
    v = curl(html.unescape(m.group(2)))[0]
    return m.group(1) + html.escape(v, quote=True) + m.group(3)


def smart_quotes(page):
    if '"' not in page and "'" not in page and "&quot;" not in page and "&#x27;" not in page:
        return page
    parts = re.split(r"(<!--.*?-->|<[^>]+>)", page, flags=re.S)
    out, skip, prev = [], 0, " "
    for part in parts:
        if not part:
            continue
        if part.startswith("<"):
            m = re.match(r"<(/?)([a-zA-Z][a-zA-Z0-9-]*)", part)
            if m:
                tag = m.group(2).lower()
                if tag in QUOTE_SKIP:
                    skip += -1 if m.group(1) else (0 if part.endswith("/>") else 1)
                    skip = max(skip, 0)
                if tag not in QUOTE_INLINE:
                    prev = " "
                if not m.group(1) and not skip:
                    part = QUOTE_ATTR_RE.sub(curl_attr, part)
            out.append(part)
            continue
        if skip or ('"' not in part and "'" not in part and "&quot;" not in part and "&#x27;" not in part and "&#39;" not in part):
            if not skip and part.strip():
                prev = html.unescape(part)[-1]
            out.append(part)
            continue
        txt, prev = curl(html.unescape(part), prev)
        out.append(html.escape(txt, quote=False))
    return "".join(out)


# ============================================================ assets
# The favicon: a brass-rimmed shield with a knot on its rope, in the site's colours. saga/art/site/ holds the same drawing
# as favicon-32.png and, on a full dark square, apple-touch-icon.png (180 px); redraw both if this changes.
FAVICON = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
           '<path d="M32 4 L57 10.5 V32 C57 47.5 46.5 56.5 32 61 C17.5 56.5 7 47.5 7 32 V10.5 Z" fill="#161B22" stroke="#CFA65F" stroke-width="4" stroke-linejoin="round"/>'
           '<path d="M13 31 H51" stroke="#CFA65F" stroke-width="4" stroke-linecap="round"/>'
           '<circle cx="32" cy="31" r="8.5" fill="#E2713B" stroke="#CFA65F" stroke-width="3"/></svg>\n')

# ============================================================ main
def main():
    try:
        site = Site()
        site.build()
        tmp = Path(tempfile.mkdtemp(prefix="unkneeling-site-"))
        run_checks(site, tmp)
        for k in site.pages:  # typography last, on pages that have passed every check
            if k.endswith(".html"):
                site.pages[k] = smart_quotes(site.pages[k])
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
