#!/usr/bin/env python3
"""THE UNKNEELING — small copies of the site's pictures.

For every picture under saga/art/characters, places, factions and codex, makes a small copy (sm: 256 px on its long
side) and a medium copy (md: 640 px) as WebP under saga/art/thumbs/, mirroring the folders, and writes
saga/art/thumbs/manifest.json naming the exact file (SHA-1) each pair was made from. The site shows the copies where a
picture is small: avatars, Codex rows and name previews take sm; a portrait's frame and a place's preview take md. The
picture itself loads only when it is opened: a Codex entry unfolded, a picture tapped to see it whole. build_site.py
falls back to the picture itself, and says so, for any picture whose copies are missing or were made from another file.

Usage: python3 engine/thumbs.py [--check]
  --check   make nothing; list the pictures without current copies and exit 1 if there are any
Copies are made only when missing or stale, and copies of a picture that is gone are removed. Needs Pillow; without it
nothing is made, the run says so and exits 0 (the site still builds, with the full pictures). `darrow.py ship` runs it
before the build.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ART = ROOT / "saga" / "art"
OUT = ART / "thumbs"
MANIFEST = OUT / "manifest.json"
KINDS = ("characters", "places", "factions", "codex")
SIZES = {"sm": 256, "md": 640}
TYPES = {".webp", ".png", ".jpg", ".jpeg"}
ABOUT = ("Small (sm, 256 px) and medium (md, 640 px) WebP copies of the pictures under saga/art/, made by engine/thumbs.py "
         "from the file whose SHA-1 is named here. Generated: never edit by hand; run the script.")


def sources():
    for kind in KINDS:
        d = ART / kind
        if d.is_dir():
            yield from (p for p in sorted(d.rglob("*")) if p.is_file() and p.suffix.lower() in TYPES)


def copies_of(rel):
    stem = OUT / Path(rel).with_suffix("")
    return {k: stem.parent / f"{stem.name}.{k}.webp" for k in SIZES}


def main():
    check = "--check" in sys.argv
    images = json.loads(MANIFEST.read_text(encoding="utf-8")).get("images", {}) if MANIFEST.exists() else {}
    want, todo = {}, []
    for src in sources():
        rel = src.relative_to(ART).as_posix()
        sha = hashlib.sha1(src.read_bytes()).hexdigest()
        want[rel] = (src, sha)
        if (images.get(rel) or {}).get("sha1") != sha or not all(p.is_file() for p in copies_of(rel).values()):
            todo.append(rel)
    gone = sorted(rel for rel in images if rel not in want)
    if check:
        for rel in todo:
            print(f"  no current copies: saga/art/{rel}")
        for rel in gone:
            print(f"  copies of a picture that is gone: saga/art/{rel}")
        print(f"thumbnails: {len(want) - len(todo)} of {len(want)} pictures have current copies")
        sys.exit(1 if todo or gone else 0)
    if not todo and not gone:
        print(f"thumbnails: all {len(want)} pictures have current copies")
        return
    try:
        from PIL import Image, ImageOps
    except ImportError:
        print(f"thumbnails: Pillow is not installed, so {len(todo)} picture(s) show at full size on the site "
              "(pip install Pillow, then run python3 engine/thumbs.py)")
        return
    for rel in todo:
        src, sha = want[rel]
        entry = {"sha1": sha}
        with Image.open(src) as im:
            im = ImageOps.exif_transpose(im)
            alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
            im = im.convert("RGBA" if alpha else "RGB")
            for size, side in SIZES.items():
                c = im.copy()
                c.thumbnail((side, side), Image.LANCZOS)  # keeps the shape; never enlarges
                out = copies_of(rel)[size]
                out.parent.mkdir(parents=True, exist_ok=True)
                c.save(out, "WEBP", quality=80, method=6)
                entry[size] = list(c.size)
        images[rel] = entry
        print(f"  made copies of saga/art/{rel}")
    for rel in gone:
        for p in copies_of(rel).values():
            p.unlink(missing_ok=True)
        del images[rel]
        print(f"  removed the copies of saga/art/{rel} (the picture is gone)")
    OUT.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps({"_about": ABOUT, "images": dict(sorted(images.items()))}, indent=1) + "\n", encoding="utf-8")
    print(f"thumbnails: {len(todo)} made, {len(gone)} removed; {len(want)} pictures have current copies")


if __name__ == "__main__":
    main()
