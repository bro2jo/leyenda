#!/usr/bin/env python3
"""THE LINE AND THE HAND: files a picture or a sound he made for the side game, under its proper name.

  python3 game/tools/file_art.py figure NAME PICTURE [--preview DIR]   a full figure for the clash: the chroma screen is keyed out
                                                                       the way the Wardrobe does it (engine/looks.py), cut to 2:3
  python3 game/tools/file_art.py token  NAME PICTURE                   a square portrait for the map token
  python3 game/tools/file_art.py card   NAME PICTURE                   a card's picture, cut to 4:3; NAME is the card's id
  python3 game/tools/file_art.py sound  NAME FILE                      a sound, by its name in the game's list (game/README.md)
  python3 game/tools/file_art.py music  NAME FILE                      background music: NAME is map (the map and the camp) or clash

NAME for a picture is who it shows (pikeman, swordsman, crossbowman, skirmisher, shieldbearer, bannerman, captain, or one of
the company: hollis, ash, wren, rae). Pictures land in game/art/figures/ and game/art/tokens/ as WebP, sounds in game/sfx/, music in game/music/.
Then: python3 game/build.py, and the game shows or plays them. The foes are not the Chronicle's: nothing here goes in saga/art/.
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent.parent
GAME = ROOT / "game"
sys.path.insert(0, str(ROOT / "engine"))
WHO = ["pikeman", "swordsman", "crossbowman", "skirmisher", "shieldbearer", "bannerman", "captain", "hollis", "ash", "wren", "rae",
       # the campaign's own (game/build_campaign.py)
       "sergeant", "pitchfork", "hornboy", "greycloak", "lymer", "guest", "darkcoat", "rider", "walker", "brother", "ysra-tal", "maelis",
       # what is not a man: a token only
       "wend", "hall", "question", "sliver", "steps"]
SOUND_EXT = [".mp3", ".ogg", ".m4a", ".wav", ".opus"]
MUSIC = ["map", "clash"]


def die(msg):
    sys.exit(f"file_art: {msg}")


def sounds():
    return re.findall(r"^\s*\['([a-z_]+)','", (GAME / "src" / "ui.js").read_text(encoding="utf-8"), re.M)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("kind", choices=["figure", "token", "card", "sound", "music"])
    ap.add_argument("name")
    ap.add_argument("file")
    ap.add_argument("--preview", help="for a figure: a folder for two previews of the cut-out")
    a = ap.parse_args()
    src = Path(a.file)
    if not src.is_file():
        die(f"no such file: {src}")
    if a.kind in ("sound", "music"):
        names = sounds() if a.kind == "sound" else MUSIC
        folder = GAME / ("sfx" if a.kind == "sound" else "music")
        if a.name not in names:
            die(f"'{a.name}' is not a {a.kind} name the game plays. The list: {', '.join(names)}")
        if src.suffix.lower() not in SOUND_EXT:
            die(f"a sound is one of {', '.join(SOUND_EXT)}")
        folder.mkdir(exist_ok=True)
        out = folder / (a.name + src.suffix.lower())
        if src.resolve() != out.resolve():
            shutil.copyfile(src, out)
        for old in folder.glob(a.name + ".*"):  # one file a sound: an earlier take in another format goes
            if old.resolve() != out.resolve():
                old.unlink()
        print(f"filed {out.relative_to(ROOT)} ({out.stat().st_size // 1024} KB)")
        return
    if a.kind == "card":  # a card's picture: 4:3, named by the card's id (the word on the prompt)
        if not re.fullmatch(r"[a-z][a-z0-9_]*", a.name):
            die(f"'{a.name}' is not a card's id")
        im = Image.open(src).convert("RGB")
        w, h = im.size
        cw, ch = (w, w * 3 // 4) if w * 3 <= h * 4 else (h * 4 // 3, h)
        im = im.crop(((w - cw) // 2, (h - ch) // 2, (w - cw) // 2 + cw, (h - ch) // 2 + ch)).resize((640, 480), Image.LANCZOS)
        (GAME / "art" / "cards").mkdir(exist_ok=True)
        out = GAME / "art" / "cards" / (a.name + ".webp")
        im.save(out, "WEBP", quality=86, method=6)
        print(f"filed {out.relative_to(ROOT)} (640x480)")
        return
    if a.name not in WHO:
        die(f"'{a.name}' is not one of: {', '.join(WHO)}")
    if a.kind == "figure":
        import looks  # the Wardrobe's own cut-out: one way of keying a screen in this repo
        img, note = looks.cut_out(src, a.preview)
        out = GAME / "art" / "figures" / (a.name + ".webp")
        img.save(out, "WEBP", quality=90, method=6)
        print(f"filed {out.relative_to(ROOT)} (1024x1536; {note})")
    else:
        im = Image.open(src).convert("RGB")
        w, h = im.size
        s = min(w, h)
        im = im.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s)).resize((512, 512), Image.LANCZOS)
        out = GAME / "art" / "tokens" / (a.name + ".webp")
        im.save(out, "WEBP", quality=88, method=6)
        print(f"filed {out.relative_to(ROOT)} (512x512)")


if __name__ == "__main__":
    main()
