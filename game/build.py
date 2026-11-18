#!/usr/bin/env python3
"""THE LINE AND THE HAND: builds the side game into game/dist/ (one page, its pictures and sounds beside it).

  python3 game/build.py

The page is game/src/ put together: style.css, page.html, engine.js (the rules, no screen) and ui.js (the screen).
Pictures of Darrow, the company and the Arts are the small copies the site already keeps (saga/art/thumbs/); pictures and
sounds made for the game alone are in game/art/ and game/sfx/ (filed by game/tools/file_art.py). The page is told what
exists (window.LH_ASSETS), so a missing picture shows its placeholder and a missing sound plays its stand-in tone.
game/dist/ is not kept in git: build it, then open game/dist/line-and-hand.html, or publish it.
"""
import json
import shutil
from pathlib import Path

from PIL import Image

GAME = Path(__file__).resolve().parent
ROOT = GAME.parent
SRC, DIST = GAME / "src", GAME / "dist"
THUMBS = ROOT / "saga" / "art" / "thumbs"
# what the game calls a picture -> the site's small copy of it
SITE_ART = {a: f"arts/{a}.sm.webp" for a in ["seated_blade", "hammerfall", "stillwater", "long_breath", "menders_patience", "wardens_eye",
                                               "groundbreaker", "measured_hand", "overwall", "far_cast", "thunderstep", "long_road"]}
SITE_ART.update({"darrow": "characters/darrow-book2.sm.webp", "hollis": "characters/hollis-garrow-book2.sm.webp", "ash": "characters/ash-book2.sm.webp",
                 "wren": "characters/wren-ashdown-book2.sm.webp", "rae": "characters/rae-thorne-book2.sm.webp", "maelis": "characters/maelis-vorne-book2.sm.webp",
                 "high-guard": "looks/the-high-guard.md.webp"})
HEAD = """<title>The Line and the Hand</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Grenze+Gotisch:wght@500;700&family=Alegreya+Sans:ital,wght@0,400;0,500;0,700;1,400&family=Alegreya+Sans+SC:wght@500;700&display=swap">
"""


def main():
    if DIST.exists():
        for old in list((DIST / "art").glob("*")) + list((DIST / "sfx").glob("*")) + list((DIST / "music").glob("*")):
            old.unlink()
    (DIST / "art").mkdir(parents=True, exist_ok=True)
    (DIST / "sfx").mkdir(parents=True, exist_ok=True)
    (DIST / "music").mkdir(parents=True, exist_ok=True)
    assets = {"art": [], "fig": [], "tok": [], "sfx": {}, "music": {}}
    for name, rel in sorted(SITE_ART.items()):
        if (THUMBS / rel).is_file():
            shutil.copyfile(THUMBS / rel, DIST / "art" / f"{name}.webp")
            assets["art"].append(name)
    for f in sorted((GAME / "art" / "figures").glob("*.webp")):
        Image.open(f).convert("RGBA").resize((512, 768), Image.LANCZOS).save(DIST / "art" / f"fig-{f.stem}.webp", "WEBP", quality=86, method=6)
        assets["fig"].append(f.stem)
    for f in sorted((GAME / "art" / "tokens").glob("*.webp")):
        Image.open(f).convert("RGB").resize((256, 256), Image.LANCZOS).save(DIST / "art" / f"tok-{f.stem}.webp", "WEBP", quality=86, method=6)
        assets["tok"].append(f.stem)
    for f in sorted((GAME / "sfx").glob("*.*")):
        shutil.copyfile(f, DIST / "sfx" / f.name)
        assets["sfx"][f.stem] = f"sfx/{f.name}"
    for f in sorted((GAME / "music").glob("*.*")):  # background music: one track for the map and camp, one for the clash
        shutil.copyfile(f, DIST / "music" / f.name)
        assets["music"][f.stem] = f"music/{f.name}"
    page = (HEAD + "<style>\n" + (SRC / "style.css").read_text(encoding="utf-8") + "</style>\n\n" + (SRC / "page.html").read_text(encoding="utf-8")
            + "\n<script>window.LH_ASSETS=" + json.dumps(assets, separators=(",", ":")) + "</script>\n"
            + "<script>\n" + (SRC / "engine.js").read_text(encoding="utf-8") + "</script>\n<script>\n" + (SRC / "ui.js").read_text(encoding="utf-8") + "</script>\n")
    (DIST / "line-and-hand.html").write_text(page, encoding="utf-8")
    files = sorted(str(p.relative_to(DIST)) for p in list((DIST / "art").glob("*")) + list((DIST / "sfx").glob("*")) + list((DIST / "music").glob("*")))
    (DIST / "files.json").write_text(json.dumps(files, indent=1), encoding="utf-8")
    print(f"built game/dist/line-and-hand.html ({len(page) // 1024} KB) · {len(assets['art'])} site pictures, {len(assets['fig'])} figures, "
          f"{len(assets['tok'])} tokens, {len(assets['sfx'])} sounds, {len(assets['music'])} music tracks")


if __name__ == "__main__":
    main()
