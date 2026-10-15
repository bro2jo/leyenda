#!/usr/bin/env python3
"""THE UNKNEELING - the Chronicle's records (used by saga.py; not a command of its own).

The story is kept the way the Ledger is kept: an append-only record of what each block of the page made true,
and everything else regenerated from it. One event per block (scene, Between, interlude, climax, Choice, a part of
the Prologue) in saga/state/events/chNN.jsonl (reader-safe: what the page says), one GM note per block in
saga/state/_gm/notes/chNN.jsonl (what was kept off the page, what the next scene must know), the threads as data in
saga/state/_gm/threads.json, the Codex's entries in saga/state/codex.json. From those the engine rebuilds:

  saga/state/world.json        scenes[], location, season, the quest, the struggle, last_beat, recaps, inventory,
                               a companion's present flag and note (approval stays the ledger's)
  saga/characters/<id>.json    first/last seen, last_seen_doing, now, story_so_far, quote, known_facts, appearances,
                               status when an event changed it (the base fields are hand-authored and kept)
  saga/state/codex.md          from codex.json
  saga/NOW.md                  the narrative top (the engine block below it is darrow.py sync's)
  threads.json → on_page       from the events' thread touches

`saga.py record` writes one event (and its note) and projects; `saga.py project` rebuilds everything; `saga.py check`
refuses a stale projection. Nothing under saga/state/events, saga/characters (derived keys), world.json, codex.md or
the NOW page's top is edited by hand any more. Standard library only.

The tales (design.md §12) are kept the same way: one event per piece (taleNN:pK) in saga/state/events/taleNN.jsonl, one
GM note per piece in saga/state/_gm/notes/taleNN.jsonl; the pieces live in saga/chronicle/tales/NN-slug.md under
`### Piece K — Title`. A tale is the past: its events add appearances and known facts to the people in it, and its last
piece's keepsake goes to world.json → keepsakes[] (what a person keeps from it); they never move anyone's last_seen,
now or place, and never the plan. world.json → tales[] is the reader-safe state of each tale (pieces told, done).
"""
import datetime as dt
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SAGA = ROOT / "saga"
EVENTS_DIR = SAGA / "state" / "events"
NOTES_DIR = SAGA / "state" / "_gm" / "notes"
THREADS = SAGA / "state" / "_gm" / "threads.json"
CODEX_JSON = SAGA / "state" / "codex.json"
CODEX_MD = SAGA / "state" / "codex.md"
WORLD = SAGA / "state" / "world.json"
PLACES = SAGA / "state" / "places.json"
GLIMPSES = SAGA / "state" / "glimpses.md"
CHARS = SAGA / "characters"
CHRON = SAGA / "chronicle"
TALES_DIR = CHRON / "tales"
NOW_MD = SAGA / "NOW.md"
ENGINE_START = "<!-- engine:start -->"

KINDS = ("prologue", "scene", "between", "interlude", "climax", "choice")
CODEX_SECTIONS = ("People", "Places and things", "Songs and verses", "Histories", "Sayings")
GLIMPSE_KINDS = ("house", "overheard", "ledger", "saying", "verse", "body", "weather")
GLIMPSE_KEEP = 20
# a keepsake's mark: the small drawing on the shelf (the site draws it; the record names it). The same set as the site's SHELF_MARKS.
KEEPSAKE_MARKS = ("knot", "horn", "needle", "pencil", "spyglass", "key", "stone", "note", "knife", "quill", "cup", "candle", "star", "wheel",
                  "bell", "hand", "word", "cord", "coin")
CHAR_DERIVED = ("first_seen", "last_seen", "last_seen_doing", "now", "story_so_far", "quote", "known_facts", "appearances")
CHAR_ORDER = ("id", "name", "aliases", "epithet", "tier", "faction", "status", "sigil", "appearance", "portrait", "portrait_alt",
              "portrait_focus", "first_seen", "last_seen", "last_seen_doing", "now", "story_so_far", "quote", "known_facts",
              "relationships", "reckoning", "appearances")
WORLD_ORDER = ("_about", "book", "book_title", "chapter", "chapter_title", "chapter_file", "scenes", "location", "season",
               "current_quest", "current_struggle", "last_beat", "companions", "choices", "inventory", "keepsakes", "tales", "recaps",
               "projects", "last_updated")

KEY_RE = re.compile(r"^ch(\d{2,}):(s(\d+)|interlude(?:-(\d+))?|between-(\d+)|climax|choice|([IVX]+))$")
SCENE_HEAD_RE = re.compile(r"^###\s+Scene\s+(\d+)\s*[—–-]\s*(.+)$")
INTERLUDE_HEAD_RE = re.compile(r"^###\s+Interlude\s*[—–-]\s*(.+)$")
BETWEEN_HEAD_RE = re.compile(r"^###\s+Between\s*[—–-]\s*(.+)$")
CLIMAX_HEAD_RE = re.compile(r"^##\s+Climax\s*[—–-]\s*(.+)$")
CHOICE_HEAD_RE = re.compile(r"^###\s+Choice\s*[—–-]\s*(.+)$")
PART_HEAD_RE = re.compile(r"^##\s+([IVX]+)\.\s+(.+)$")
CHAPTER_TITLE_RE = re.compile(r"^#\s+(?:Chapter\s+\d+|Prologue)\s*[—–-]\s*(.+?)\s*$")
BOOK_TITLE_RE = re.compile(r"^#\s+BOOK\s+([IVXLC]+)\s*[—–-]\s*(.+?)\s*$")
TALE_KEY_RE = re.compile(r"^tale(\d{2,}):p(\d+)$")
PIECE_HEAD_RE = re.compile(r"^###\s+Piece\s+(\d+)\s*[—–-]\s*(.+)$")
TALE_TITLE_RE = re.compile(r"^#\s+Tale\s+(\d+)\s*[—–-]\s*(.+?)\s*$")


# ---------------------------------------------------------------- io
def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def dumps(obj):
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


def save_text(path, text):
    """Atomic write (a .tmp beside the file, renamed over it)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def save_json(path, obj):
    save_text(path, dumps(obj))


def read_jsonl(path):
    if not path.exists():
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise ValueError(f"{rel(path)} line {i}: invalid JSON ({e})")
    return out


def write_jsonl(path, rows):
    save_text(path, "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))


def rel(path):
    try:
        return str(Path(path).relative_to(ROOT))
    except ValueError:
        return str(path)


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", str(s or "").lower()).strip()


def short(text, n):
    text = " ".join(str(text or "").split())
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def ch2(n):
    return f"ch{int(n):02d}"


# ---------------------------------------------------------------- keys and the page
def parse_key(key):
    """(chapter, scene_key, kind) for a block key: ch02:s3 → (2, '3', 'scene'); ch02:between-7 → (2, 'between-7', 'between');
    ch02:interlude[-2]; ch02:climax; ch02:choice; ch00:II → (0, 'II', 'prologue'). None when it is not a block key."""
    m = KEY_RE.match(str(key or ""))
    if not m:
        return None
    ch = int(m.group(1))
    sub = m.group(2)
    if m.group(3):
        return ch, m.group(3), "scene"
    if sub.startswith("interlude"):
        return ch, sub, "interlude"
    if sub.startswith("between"):
        return ch, sub, "between"
    if sub in ("climax", "choice"):
        return ch, sub, sub
    return ch, sub, "prologue"


def make_key(chapter, scene_key):
    sk = str(scene_key)
    if sk.isdigit():
        return f"{ch2(chapter)}:s{sk}"
    return f"{ch2(chapter)}:{sk}"


def anchor_for(scene_key):
    sk = str(scene_key)
    if sk.isdigit():
        return f"scene-{sk}"
    if re.match(r"^[IVX]+$", sk):
        return "part-" + sk.lower()
    return sk


def chapter_files():
    """{chapter number: path} for every chronicle file (NN-slug.md)."""
    out = {}
    for p in sorted(CHRON.glob("*.md")):
        m = re.match(r"^(\d+)-", p.name)
        if m:
            out[int(m.group(1))] = p
    return out


def chapter_titles(path):
    """(book_title or None, chapter_title or '') from a chapter file's front matter."""
    book, title = None, ""
    for line in path.read_text(encoding="utf-8").splitlines()[:12]:
        mb = BOOK_TITLE_RE.match(line)
        if mb:
            book = mb.group(2).strip()
        mt = CHAPTER_TITLE_RE.match(line)
        if mt:
            title = mt.group(1).strip()
    return book, title


def blocks_of(path):
    """[(scene_key, title, text)] for every block of a chapter file, in page order: scenes ('3'), interludes
    ('interlude', 'interlude-2'), Betweens ('between-K'), 'climax', 'choice', and the Prologue's parts ('I')."""
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
        elif PART_HEAD_RE.match(s):
            key, title = PART_HEAD_RE.match(s).group(1), PART_HEAD_RE.match(s).group(2)
        if key is not None:
            out.append([key, title.strip(), []])
        elif out:
            out[-1][2].append(line)
    return [(k, t, "\n".join(lines).strip()) for k, t, lines in out]


def block_text(chapter, scene_key):
    """The text of one block, or None."""
    path = chapter_files().get(int(chapter))
    if not path:
        return None
    for k, t, text in blocks_of(path):
        if k == str(scene_key):
            return text
    return None


# ---------------------------------------------------------------- the tales (the past, a piece at a time)
def parse_tale_key(key):
    """(tale number, piece number) for tale01:p2; None otherwise."""
    m = TALE_KEY_RE.match(str(key or ""))
    return (int(m.group(1)), int(m.group(2))) if m else None


def tale_id(n):
    return f"tale{int(n):02d}"


def tale_key(n, k):
    return f"{tale_id(n)}:p{int(k)}"


def tale_files():
    """{tale number: path} for every tale file (saga/chronicle/tales/NN-slug.md)."""
    out = {}
    if TALES_DIR.exists():
        for p in sorted(TALES_DIR.glob("*.md")):
            m = re.match(r"^(\d+)-", p.name)
            if m:
                out[int(m.group(1))] = p
    return out


def tale_titles(path):
    """(title, when) from a tale file's head: `# Tale N — Title`, then the italic line before the first `---`."""
    title, when = "", ""
    for line in path.read_text(encoding="utf-8").splitlines()[:12]:
        mt = TALE_TITLE_RE.match(line)
        if mt:
            title = mt.group(2).strip()
        elif line.strip() == "---":
            break
        elif line.strip().startswith("*") and not line.startswith("#"):
            when = line.strip().strip("*").strip()
    return title, when


def pieces_of(path):
    """[(k, title, text)] for every `### Piece K — Title` of a tale file, in page order."""
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = PIECE_HEAD_RE.match(line.strip())
        if m:
            out.append([int(m.group(1)), m.group(2).strip(), []])
        elif out:
            out[-1][2].append(line)
    return [(k, t, "\n".join(lines).strip()) for k, t, lines in out]


# ---------------------------------------------------------------- events, notes, threads, codex
def events_path(chapter):
    return EVENTS_DIR / f"{ch2(chapter)}.jsonl"


def notes_path(chapter):
    return NOTES_DIR / f"{ch2(chapter)}.jsonl"


def store_paths(key):
    """(events file, notes file) for a block key: a chapter's (chNN) or a tale's (taleNN)."""
    if parse_key(key):
        ch = parse_key(key)[0]
        return events_path(ch), notes_path(ch)
    t = parse_tale_key(key)
    if t:
        return EVENTS_DIR / f"{tale_id(t[0])}.jsonl", NOTES_DIR / f"{tale_id(t[0])}.jsonl"
    raise ValueError(f"{key!r} is neither a chapter block key nor a tale piece key")


def load_tale_events(n=None):
    """Every tale event in order (tales ascending, each file in page order), or one tale's."""
    if n is not None:
        return read_jsonl(EVENTS_DIR / f"{tale_id(n)}.jsonl")
    out = []
    if not EVENTS_DIR.exists():
        return out
    for p in sorted(EVENTS_DIR.glob("tale*.jsonl"), key=lambda x: int(re.sub(r"\D", "", x.stem) or 0)):
        out += read_jsonl(p)
    return out


def load_tale_notes():
    out = []
    if not NOTES_DIR.exists():
        return out
    for p in sorted(NOTES_DIR.glob("tale*.jsonl"), key=lambda x: int(re.sub(r"\D", "", x.stem) or 0)):
        out += read_jsonl(p)
    return out


def load_events(chapter=None):
    """Every event in story order (chapters ascending, each file in its page order), or one chapter's."""
    if chapter is not None:
        return read_jsonl(events_path(chapter))
    out = []
    if not EVENTS_DIR.exists():
        return out
    for p in sorted(EVENTS_DIR.glob("ch*.jsonl"), key=lambda x: int(re.sub(r"\D", "", x.stem) or 0)):
        out += read_jsonl(p)
    return out


def load_notes(chapter=None):
    if chapter is not None:
        return read_jsonl(notes_path(chapter))
    out = []
    if not NOTES_DIR.exists():
        return out
    for p in sorted(NOTES_DIR.glob("ch*.jsonl"), key=lambda x: int(re.sub(r"\D", "", x.stem) or 0)):
        out += read_jsonl(p)
    return out


def put_event(ev, replace=False):
    """Append an event to its chapter's (or tale's) file, or replace the one with the same key (`record --force`)."""
    path = store_paths(ev["key"])[0]
    rows = read_jsonl(path)
    idx = next((i for i, r in enumerate(rows) if r.get("key") == ev["key"]), None)
    if idx is not None:
        if not replace:
            raise ValueError(f"{ev['key']} is already recorded; --force re-records it")
        rows[idx] = ev
    else:
        rows.append(ev)
    write_jsonl(path, rows)


def put_note(note, replace=False):
    path = store_paths(note["key"])[1]
    rows = read_jsonl(path)
    idx = next((i for i, r in enumerate(rows) if r.get("key") == note["key"]), None)
    if idx is not None:
        if not replace:
            raise ValueError(f"a note for {note['key']} is already recorded; --force re-records it")
        rows[idx] = note
    else:
        rows.append(note)
    write_jsonl(path, rows)


def load_threads():
    if not THREADS.exists():
        return {"_about": "Open plots, plants and payoffs, as data (GM only). A thread: id, title, truth (T#), feeds, status open|paid, "
                          "who_knows (the knowledge state the page has established), note (the GM's running note), on_page (the block keys "
                          "where it was planted or touched: rebuilt by the engine from the events' thread touches; a truth needs two before "
                          "any scene reveals it). Written through `saga.py record` (a block's note names the threads it touched or changed) "
                          "and `saga.py threads`; read through `saga.py threads` and `saga.py brief`, never whole.", "threads": []}
    return load_json(THREADS)


def save_threads(obj):
    save_json(THREADS, obj)


def load_codex():
    if not CODEX_JSON.exists():
        return {"_about": "The Codex's entries (reader-safe): canon the page invented, one entry per name, in the sections the site renders. "
                          "`saga.py record` appends an event's codex items here and regenerates codex.md; never edit codex.md by hand.",
                "header": "", "sections": [{"name": s, "intro": "", "entries": []} for s in CODEX_SECTIONS]}
    return load_json(CODEX_JSON)


def save_codex(obj):
    save_json(CODEX_JSON, obj)


def render_codex(codex):
    lines = ["# Codex — canon invented in play", ""]
    if codex.get("header"):
        lines += [codex["header"].rstrip(), ""]
    for sec in codex.get("sections", []):
        lines.append(f"## {sec['name']}")
        if sec.get("intro"):
            lines += ["", sec["intro"].rstrip()]
        for e in sec.get("entries", []):
            lines.append(f"- **{e['name']}** — {e['text']}")
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def apply_codex_items(codex, items, key):
    """Fold an event's codex items into the store: {section, name, text}; a name already in the section gets the text
    appended (the entry grows the way the page's knowledge grows), a new name a new entry. Returns problems."""
    probs = []
    by_name = {s["name"]: s for s in codex.get("sections", [])}
    for it in items or []:
        sec = by_name.get(it.get("section"))
        if not sec:
            probs.append(f"codex item {it.get('name')!r}: section {it.get('section')!r} is not one of {', '.join(CODEX_SECTIONS)}")
            continue
        name, text = str(it.get("name") or "").strip(), str(it.get("text") or "").strip()
        if not name or not text:
            probs.append("a codex item needs a name and a text")
            continue
        found = next((e for e in sec["entries"] if e["name"].lower() == name.lower()), None)
        if found:
            found["text"] = (found["text"].rstrip() + " " + text).strip()
            found.setdefault("sources", []).append(key)
        else:
            sec["entries"].append({"name": name, "text": text, "sources": [key]})
    return probs


def unapply_codex_key(codex, key):
    """Drop what one event added to the codex (before re-recording it): entries it created, text it appended."""
    for sec in codex.get("sections", []):
        kept = []
        for e in sec.get("entries", []):
            src = e.get("sources") or []
            if src and all(s == key for s in src):
                continue  # the entry was this event's alone
            if key in src:
                e["sources"] = [s for s in src if s != key]
                e["_rebuild"] = True  # its text carried a part from this event: a rebuild from the events restores it
            kept.append(e)
        sec["entries"] = kept


# ---------------------------------------------------------------- projections
def place_names():
    try:
        data = load_json(PLACES)
    except (OSError, ValueError):
        return {}
    places = data.get("places") if isinstance(data, dict) else data
    return {p["id"]: p for p in (places or []) if isinstance(p, dict) and p.get("id")}


def char_files():
    return {p.stem: p for p in sorted(CHARS.glob("*.json"))}


def derive_characters(events, bases, tale_events=()):
    """Derived fields per character id from the events: {cid: {first_seen, last_seen, last_seen_doing, now, story_so_far,
    quote, known_facts, appearances, status?}}. A person's place carries forward from one explicit place to the next;
    a presence without one is where Darrow is. A tale's pieces (the past) add appearances and facts, and a quote when the
    chapters gave none; someone met only in a tale is first and last seen there; nothing else of theirs moves."""
    files = chapter_files()
    out = {cid: {"appearances": [], "known_facts": [], "first_presence": None, "first_mention": None, "last_presence": None, "last_mention": None,
                 "doing": None, "now": None, "story_so_far": None, "quote": None, "status": None, "place": None} for cid in bases}
    where_place = None
    for ev in events:
        parsed = parse_key(ev.get("key", ""))
        if not parsed:
            continue
        ch, sk, kind = parsed
        if (ev.get("where") or {}).get("place"):
            where_place = ev["where"]["place"]
        slug = files[ch].stem if ch in files else f"{ch:02d}"
        anchor = f"chronicle/{slug}.html#{anchor_for(sk)}"
        for p in ev.get("people") or []:
            cid = p.get("id")
            if cid not in out:
                continue
            d = out[cid]
            mention = bool(p.get("mention"))
            if p.get("place"):
                d["place"] = p["place"]
            elif not mention and where_place:
                d["place"] = where_place
            ref = {"chapter": f"{ch:02d}", "scene": sk, "place": d["place"], "anchor": anchor}
            app = {"chapter": f"{ch:02d}", "scene": sk}
            if mention:
                app["mention"] = True
            d["appearances"].append(app)
            if mention:
                d["last_mention"] = ref
                if d["first_mention"] is None:
                    d["first_mention"] = ref
            else:
                d["last_presence"] = ref
                if d["first_presence"] is None:
                    d["first_presence"] = ref
                if p.get("did"):
                    d["doing"] = p["did"]
            if p.get("now"):
                d["now"] = p["now"]
            if p.get("status"):
                d["status"] = p["status"]
            if p.get("quote"):
                q = p["quote"] if isinstance(p["quote"], dict) else {"text": p["quote"]}
                d["quote"] = {"text": q.get("text"), "chapter": f"{ch:02d}", "scene": sk}
            for f in p.get("facts") or []:
                row = {"fact": f.get("fact"), "chapter": f"{ch:02d}", "scene": sk}
                if f.get("evidence"):
                    row["evidence"] = f["evidence"]
                d["known_facts"].append(row)
        for cid, text in (ev.get("story_so_far") or {}).items():
            if cid in out and text:
                out[cid]["story_so_far"] = text
    tfiles = tale_files()
    for ev in tale_events:
        parsed = parse_tale_key(ev.get("key", ""))
        if not parsed:
            continue
        n, k = parsed
        code, sk = tale_id(n), f"p{k}"
        slug = tfiles[n].stem if n in tfiles else f"{n:02d}"
        anchor = f"tales/{slug}.html#piece-{k}"
        for p in ev.get("people") or []:
            cid = p.get("id")
            if cid not in out:
                continue
            d = out[cid]
            mention = bool(p.get("mention"))
            app = {"chapter": code, "scene": sk}
            if mention:
                app["mention"] = True
            d["appearances"].append(app)
            ref = {"chapter": code, "scene": sk, "place": None, "anchor": anchor}
            if not mention:
                d.setdefault("tale_presence", []).append(ref)
                if p.get("did"):
                    d["tale_doing"] = p["did"]
            else:
                d.setdefault("tale_mention", []).append(ref)
            if p.get("quote") and not d.get("quote"):
                q = p["quote"] if isinstance(p["quote"], dict) else {"text": p["quote"]}
                d["quote"] = {"text": q.get("text"), "chapter": code, "scene": sk}
            for f in p.get("facts") or []:
                row = {"fact": f.get("fact"), "chapter": code, "scene": sk}
                if f.get("evidence"):
                    row["evidence"] = f["evidence"]
                d["known_facts"].append(row)
    return out


def project_character(cid, base, derived):
    c = {k: v for k, v in base.items()}
    d = derived.get(cid) or {}
    first = d.get("first_presence") or d.get("first_mention")  # someone only named so far points at the mention (characters/README.md)
    last = d.get("last_presence") or d.get("last_mention")
    if not first and (d.get("tale_presence") or d.get("tale_mention")):  # met only in a tale: seen there, and only there
        tp = d.get("tale_presence") or d.get("tale_mention")
        first, last = tp[0], tp[-1]
        if d.get("tale_doing") and not d.get("doing"):
            d["doing"] = d["tale_doing"]

    def ref_of(r):
        return {k: r[k] for k in ("chapter", "scene", "place", "anchor") if k in r and (k != "place" or r[k])}

    if first:
        c["first_seen"] = ref_of(first)
    if last:
        c["last_seen"] = ref_of(last)
    if d.get("doing"):
        c["last_seen_doing"] = d["doing"]
    if d.get("now"):
        c["now"] = d["now"]
    if d.get("story_so_far"):
        c["story_so_far"] = d["story_so_far"]
    if d.get("quote"):
        c["quote"] = d["quote"]
    if d.get("status"):
        c["status"] = d["status"]
    c["known_facts"] = d.get("known_facts") or base.get("known_facts") or []
    c["appearances"] = d.get("appearances") or base.get("appearances") or []
    ordered = {k: c[k] for k in CHAR_ORDER if k in c}
    ordered.update({k: v for k, v in c.items() if k not in ordered})
    return ordered


def tales_state(plan, tale_events=None):
    """The reader-safe state of every bound tale, from the plan's bindings and the tale events: id, n, title, of (whose
    past), pieces, told, done, file, keepsakes (the pieces' keepsakes, in order)."""
    evs = load_tale_events() if tale_events is None else tale_events
    tfiles = tale_files()
    out = []
    for b in plan.get("tales") or []:
        n = int(b.get("n", 0))
        path = tfiles.get(n)
        title, when = tale_titles(path) if path else (b.get("title", ""), "")
        mine = [e for e in evs if (parse_tale_key(e.get("key", "")) or (None,))[0] == n]
        keeps = [{"name": e["keepsake"].get("name"), "text": e["keepsake"].get("text"), "to": e["keepsake"].get("to"),
                  "tale": tale_id(n), "piece": f"p{parse_tale_key(e['key'])[1]}", "tale_title": title,
                  **({"mark": e["keepsake"]["mark"]} if e["keepsake"].get("mark") else {}),
                  **({"lesser": True} if e["keepsake"].get("lesser") else {})}
                 for e in mine if isinstance(e.get("keepsake"), dict) and e["keepsake"].get("name")]
        pieces = int(b.get("pieces") or 0)
        out.append({"id": tale_id(n), "n": n, "title": title, "when": when, "of": b.get("of"), "pieces": pieces, "told": len(mine),
                    "done": bool(pieces) and len(mine) >= pieces, "file": rel(path) if path else b.get("file"), "keepsakes": keeps,
                    "project": b.get("project"), "tale": b.get("tale")})
    return out


def project_world(events, plan, world, tale_events=()):
    """world.json from the events and the plan's position; approval, choices and projects stay as they are. The tales
    (reader-safe: pieces told, done) and the keepsakes come from the tale events."""
    files = chapter_files()
    pos = plan["position"]
    chapter = int(pos["chapter"])
    w = dict(world)
    w["book"] = int(pos["book"])
    w["chapter"] = chapter
    if chapter in files:
        book_title, title = chapter_titles(files[chapter])
        w["chapter_title"] = title or w.get("chapter_title", "")
        w["chapter_file"] = rel(files[chapter])
    scenes = []
    state = {"where": None, "season": None, "quest": None, "struggle": None, "last_beat": None, "book_title": None,
             "inventory": list(world.get("inventory") or []), "recaps": {}, "present": {}, "notes": {}, "last_updated": None}
    for ev in events:
        parsed = parse_key(ev.get("key", ""))
        if not parsed:
            continue
        ch, sk, kind = parsed
        for k in ("where", "season", "quest", "struggle", "last_beat", "book_title"):
            if ev.get(k):
                state[k] = ev[k]
        inv = ev.get("inventory") or {}
        if isinstance(inv, dict):
            if inv.get("set") is not None:
                state["inventory"] = list(inv["set"])
            for x in inv.get("add") or []:
                if x not in state["inventory"]:
                    state["inventory"].append(x)
            for x in inv.get("remove") or []:
                state["inventory"] = [i for i in state["inventory"] if i != x]
        if ev.get("recap") and ch in files:
            state["recaps"][files[ch].stem] = ev["recap"]
        for p in ev.get("people") or []:
            key = str(p.get("id", "")).split("-")[0]
            if "present" in p and p["present"] is not None:
                state["present"][key] = bool(p["present"])
        if ev.get("written") and (state["last_updated"] is None or ev["written"] > state["last_updated"]):
            state["last_updated"] = ev["written"]
        if ch == chapter:
            row = {"scene": int(sk) if sk.isdigit() else sk, "title": ev.get("title", "")}
            if kind == "between":
                row["after"] = ev.get("after")
            row["covers"] = [ev["date"]] if ev.get("date") else []
            row["written"] = ev.get("written")
            scenes.append(row)
    w["scenes"] = scenes
    if state["book_title"]:
        w["book_title"] = state["book_title"]
    if state["where"]:
        loc = dict(world.get("location") or {})
        loc["place"] = state["where"].get("place")
        loc["detail"] = state["where"].get("detail")
        w["location"] = {k: loc[k] for k in ("place", "detail", "_about") if k in loc}
    if state["season"]:
        w["season"] = state["season"]
    if state["quest"]:
        cq = dict(world.get("current_quest") or {})
        cq["name"] = state["quest"].get("name")
        cq["on_the_page"] = state["quest"].get("on_the_page")
        w["current_quest"] = {k: cq[k] for k in ("name", "on_the_page", "_about") if k in cq}
    if state["struggle"]:
        w["current_struggle"] = state["struggle"]
    if state["last_beat"]:
        w["last_beat"] = state["last_beat"]
    comps = dict(world.get("companions") or {})
    for key, comp in comps.items():
        if key in state["present"]:
            comp["present"] = state["present"][key]
    w["companions"] = comps
    w["inventory"] = state["inventory"]
    tales = tales_state(plan, list(tale_events))
    w["keepsakes"] = [k for t in tales for k in t["keepsakes"]]
    w["tales"] = [{k: t[k] for k in ("id", "title", "of", "pieces", "told", "done", "file")} for t in tales]
    recaps = dict(world.get("recaps") or {})
    recaps.update(state["recaps"])
    w["recaps"] = recaps
    if state["last_updated"]:
        w["last_updated"] = state["last_updated"]
    ordered = {k: w[k] for k in WORLD_ORDER if k in w}
    ordered.update({k: v for k, v in w.items() if k not in ordered})
    return ordered


def kind_label(kind):
    return {"scene": "Scene", "between": "Between", "interlude": "Interlude", "climax": "Climax", "choice": "Choice", "prologue": "Prologue"}.get(kind, kind)


def project_now(events, plan, world, chars, existing_text):
    """The narrative top of saga/NOW.md, from the records; the engine block below the marker is kept as it is."""
    pos = plan["position"]
    chapter = int(pos["chapter"])
    places = place_names()
    cur = [ev for ev in events if parse_key(ev.get("key", "")) and parse_key(ev["key"])[0] == chapter]
    last = cur[-1] if cur else None
    # "earlier today": the blocks since the last scene before the last block (a day's pieces), oldest first
    earlier = []
    if last and parse_key(last["key"])[2] != "scene":
        i = len(cur) - 1
        while i > 0 and parse_key(cur[i - 1]["key"])[2] != "scene":
            i -= 1
        start = max(i - 1, 0)
        earlier = cur[start:len(cur) - 1]
    now_state = {}
    for ev in events:
        if ev.get("now"):
            now_state.update({k: v for k, v in ev["now"].items() if v})
    loc = world.get("location") or {}
    place = places.get(loc.get("place") or "", {})
    where = place.get("name") or loc.get("place") or "—"
    if place.get("subtitle"):
        where += f", {place['subtitle']}"
    if loc.get("detail"):
        where += f"; {loc['detail']}"
    book = int(pos["book"])
    lines = ["# NOW — the Chronicle", "",
             "*Narrative only, regenerated by the engine from the page's records after every block (`saga.py record`); nothing here is "
             "edited by hand. Nothing from the real logs appears on this page except through the Reckoning.*", ""]
    head = f"**BOOK {roman(book)} — {str(world.get('book_title') or '').upper()} · Chapter {chapter} — {world.get('chapter_title', '')}"
    if last and last.get("time"):
        head += f" · {last['time']}"
    lines.append(head + "**")
    lines.append("")
    lines.append(f"- **Where:** {where}.")
    cq = world.get("current_quest") or {}
    if cq.get("name"):
        lines.append(f"- **The quest:** *{cq['name']}.* {cq.get('on_the_page', '')}")
    if world.get("current_struggle"):
        lines.append(f"- **What Darrow is fighting right now:** {world['current_struggle']}")
    if last:
        k = parse_key(last["key"])[2]
        lines.append(f"- **Just happened ({kind_label(k)}):** *{last.get('title', '')}.* {last.get('last_beat') or ''}".rstrip())
    if earlier:
        parts = [f"*{e.get('title', '')}* ({kind_label(parse_key(e['key'])[2])})" + (f": {short(e['last_beat'], 160)}" if e.get("last_beat") else "") for e in earlier]
        lines.append("- **Earlier today, in order:** " + " · ".join(parts))
    comps = world.get("companions") or {}
    with_him = []
    for key, comp in comps.items():
        if comp.get("present") is False:
            continue
        cid = next((c for c in chars if c.split("-")[0] == key), None)
        c = chars.get(cid) or {}
        line = c.get("name") or key
        tail = c.get("now") or comp.get("note") or ""
        with_him.append(f"{line} ({short(tail, 220)})" if tail else line)
    if with_him:
        lines.append("- **With him:** " + " · ".join(with_him))
    here = []
    for cid, c in chars.items():
        if cid == "darrow" or cid.split("-")[0] in comps:
            continue
        if c.get("status") not in ("alive", "hollowed"):
            continue
        if (c.get("last_seen") or {}).get("place") == loc.get("place"):
            here.append(f"{c.get('name')} ({short(c.get('last_seen_doing'), 140)})" if c.get("last_seen_doing") else c.get("name"))
    if here:
        lines.append("- **Also here:** " + " · ".join(here))
    tl = world.get("tales") or []
    if tl:
        lines.append("- **The tales:** " + " · ".join(f"Tale {int(t['id'][4:])} — {t.get('title')} ({'told in full' if t.get('done') else str(t.get('told')) + ' of ' + str(t.get('pieces')) + ' told'})" for t in tl))
    if now_state.get("against"):
        lines.append(f"- **Against him:** {now_state['against']}")
    if now_state.get("next"):
        lines.append(f"- **Next:** {now_state['next']}")
    oc = plan.get("open_choice")
    om = plan.get("open_micro")
    if oc:
        lines.append(f"- **Open choice (the climax of Chapter {oc.get('chapter')}):** {oc.get('ask')} " + " / ".join(f"{i}. {o}" for i, o in enumerate(oc.get("options", []), 1)))
    elif om:
        lines.append(f"- **Open choice (a small one):** {om.get('ask')} " + " / ".join(f"{i}. {o}" for i, o in enumerate(om.get("options", []), 1)))
    else:
        lines.append("- **Open choice:** none.")
    lines.append("")
    lines.append("*The records behind this page: `saga.py history`, `saga.py threads` (GM), `saga.py brief` before writing. Open threads and the GM's plan live under `saga/state/_gm/` and never appear here.*")
    lines.append("")
    top = "\n".join(lines) + "\n"
    rest = existing_text[existing_text.index(ENGINE_START):] if ENGINE_START in existing_text else ENGINE_START + "\n<!-- engine:end -->\n"
    return top + rest


def roman(n):
    n = int(n)
    out = ""
    for v, s in ((1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"), (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")):
        while n >= v:
            out += s
            n -= v
    return out or str(n)


def threads_on_page(events):
    """{thread id: [keys]} from the events' thread touches, in story order (a tale's touch keys tale01:p2)."""
    out = {}
    for ev in events:
        parsed = parse_key(ev.get("key", ""))
        if parsed:
            ch, sk, kind = parsed
            short_key = f"{ch:02d}:{'s' + sk if sk.isdigit() else sk}"
        elif parse_tale_key(ev.get("key", "")):
            short_key = ev["key"]
        else:
            continue
        for t in ev.get("threads") or []:
            tid = t.get("id") if isinstance(t, dict) else t
            if tid is None:
                continue
            out.setdefault(int(tid), [])
            if short_key not in out[int(tid)]:
                out[int(tid)].append(short_key)
    return out


def project_all(plan, write=True):
    """Regenerate every projection. Returns the list of files that were (or would be) changed."""
    events = load_events()
    changed = []

    def emit(path, text):
        old = path.read_text(encoding="utf-8") if path.exists() else None
        if old != text:
            changed.append(rel(path))
            if write:
                save_text(path, text)

    tale_events = load_tale_events()
    world = load_json(WORLD) if WORLD.exists() else {}
    new_world = project_world(events, plan, world, tale_events)
    emit(WORLD, dumps(new_world))
    bases = {cid: load_json(p) for cid, p in char_files().items()}
    derived = derive_characters(events, bases, tale_events)
    chars = {}
    for cid, base in bases.items():
        c = project_character(cid, base, derived)
        chars[cid] = c
        emit(CHARS / f"{cid}.json", dumps(c))
    codex = load_codex()
    emit(CODEX_MD, render_codex(codex))
    thr = load_threads()
    onp = threads_on_page(events + tale_events)
    for t in thr.get("threads", []):
        t["on_page"] = onp.get(int(t["id"]), [])
    emit(THREADS, dumps(thr))
    existing = NOW_MD.read_text(encoding="utf-8") if NOW_MD.exists() else ""
    emit(NOW_MD, project_now(events, plan, new_world, chars, existing))
    return changed


# ---------------------------------------------------------------- glimpses
def glimpse_lines():
    if not GLIMPSES.exists():
        return [], []
    text = GLIMPSES.read_text(encoding="utf-8").splitlines()
    head = [l for l in text if not l.startswith("- ")]
    rows = []
    for l in text:
        m = re.match(r"^- (\d{4}-\d{2}-\d{2}) · (\w+) · (.*)$", l)
        if m:
            rows.append({"date": m.group(1), "kind": m.group(2), "text": m.group(3)})
    return head, rows


def glimpse_add(date, kind, text):
    """Append a glimpse (no kind twice running, the file kept to its last GLIMPSE_KEEP lines). Returns problems."""
    head, rows = glimpse_lines()
    probs = []
    if kind not in GLIMPSE_KINDS:
        probs.append(f"kind {kind!r} is not one of {', '.join(GLIMPSE_KINDS)}")
    if rows and rows[-1]["kind"] == kind:
        probs.append(f"the last glimpse was a {kind} too: rotate the kind ({', '.join(k for k in GLIMPSE_KINDS if k != kind)})")
    if len(str(text).split()) > 60:
        probs.append("a glimpse is one or two sentences, about 40 words at most")
    if probs:
        return probs
    rows.append({"date": date, "kind": kind, "text": " ".join(str(text).split())})
    rows = rows[-GLIMPSE_KEEP:]
    head_text = "\n".join(head).rstrip() + "\n\n" if head else ""
    save_text(GLIMPSES, head_text + "".join(f"- {r['date']} · {r['kind']} · {r['text']}\n" for r in rows))
    return []
