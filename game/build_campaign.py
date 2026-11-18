#!/usr/bin/env python3
"""THE LINE AND THE HAND, the campaign: builds it into game/dist/campaign/ (one page, its pictures and sounds beside it).

  python3 game/build_campaign.py

It is the same game (src/engine.js, src/ui.js and src/style.css, untouched) with the campaign laid over it: src/campaign.js
(the missions' rules), src/missions.js (the missions), src/campaign_ui.js and src/campaign.css (its screens), src/campaign.html
(the page). game/build.py and the page it builds know nothing of any of this.

Pictures come from the small copies the site keeps (saga/art/thumbs/): the company as they looked in each Book, the people a
mission puts on the board, the places for the title cards. A foe or an ordeal with no picture gets a plain drawn token, and the
page lists those as pictures still to make; a figure filed in game/art/figures/ under the same name replaces the drawn one
(its token is cut from the figure's head; a token filed in game/art/tokens/ outranks that).
"""
import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from build import HEAD, SITE_ART, THUMBS, head

GAME = Path(__file__).resolve().parent
SRC, DIST = GAME / "src", GAME / "dist" / "campaign"
C = "characters/"
ART = dict(SITE_ART)  # the Arts, the company in Book II, the high guard
ART.update({"darrow0": C + "darrow.sm.webp", "darrow1": C + "darrow.sm.webp", "hollis0": C + "hollis-garrow.sm.webp", "hollis1": C + "hollis-garrow.sm.webp",
            "wren1": C + "wren-ashdown.sm.webp", "rae1": C + "rae-thorne.sm.webp", "maelis1": C + "maelis-vorne.sm.webp", "ash1": C + "ash.sm.webp",
            "aldric": C + "aldric-vane.sm.webp", "pell": C + "sister-pell.sm.webp"})
ART.update({f"place-{p}": f"places/{p}.md.webp" for p in ["harrow-ford", "saint-ysoldes", "winch-house", "coldmere", "the-lowmarch"]})
# a foe's token from a face the Chronicle already has
TOKENS = {"ysra-tal": C + "ysra-tal.sm.webp", "hollis-foe": C + "hollis-garrow.sm.webp", "greycloak": "factions/confessors.sm.webp"}
EMBLEM = {"greycloak"}  # not a face, only a badge: the head of the man's own figure outranks it
# men who wear one of the game's own pictures until theirs is made (figure and token)
ALIAS = {"hornboy": "pitchfork", "sergeant": "captain", "guest": "greycloak"}
# everything else on the board that has no picture yet: name, what it is, a letter, a colour
DRAWN = [("wend", "The Wend in spate", "W", "#244860"), ("hall", "The length of the hall", "H", "#4A3F33"), ("question", "The hall's question", "?", "#5A4A6A"),
         ("sliver", "The black glass", "*", "#0B0D11"), ("guest", "The Confessor's men", "G", "#4E5560"), ("steps", "A stretch of the Steps", "S", "#55585E"),
         ("rider", "An outrider of the Second", "II", "#3D4E6B"), ("walker", "A walker, frost in his beard", "~", "#6F7F8C"), ("darkcoat", "A rider in a dark coat", "D", "#23262E"), ("brother", "A lay brother", "B", "#6B5A3C"),
         ("lymer", "The grey cloaks' lymer, on its long leash", "L", "#5B4A3A")]


def disc(letter, colour, size=256):
    im = Image.new("RGB", (size, size), colour)
    d = ImageDraw.Draw(im)
    d.ellipse([18, 18, size - 18, size - 18], outline="#CFA65F", width=5)
    try:
        f = ImageFont.load_default(size=int(size * (.42 if len(letter) > 1 else .56)))
    except TypeError:
        f = ImageFont.load_default()
    box = d.textbbox((0, 0), letter, font=f)
    d.text(((size - box[2] - box[0]) / 2, (size - box[3] - box[1]) / 2), letter, fill="#E8E2D4", font=f)
    return im


def square(src, size=256):
    im = Image.open(src).convert("RGB")
    w, h = im.size
    s = min(w, h)
    return im.crop(((w - s) // 2, max(0, (h - s) // 4), (w - s) // 2 + s, max(0, (h - s) // 4) + s)).resize((size, size), Image.LANCZOS)


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    for d in ("art", "sfx", "music"):
        (DIST / d).mkdir(parents=True, exist_ok=True)
    assets = {"art": [], "fig": [], "tok": [], "sfx": {}, "music": {}, "drawn": [], "cardart": {}, "lent": {}}
    for name, rel in sorted(ART.items()):
        if (THUMBS / rel).is_file():
            shutil.copyfile(THUMBS / rel, DIST / "art" / f"{name}.webp")
            assets["art"].append(name)
    made = {f.stem: f for f in (GAME / "art" / "tokens").glob("*.webp")}
    figs = {f.stem: f for f in (GAME / "art" / "figures").glob("*.webp")}
    for key, src in ALIAS.items():  # lent pictures: a real one replaces it by being filed under the man's own name
        if key not in figs and src in figs:
            figs[key] = figs[src]
            assets["lent"][key] = src
            if key not in made and src in made:
                made[key] = made[src]
    for key, f in sorted(figs.items()):  # a figure with no token of its own: one is cut from its head
        if key not in made and (key not in TOKENS or key in EMBLEM):
            head(f).save(DIST / "art" / f"tok-{key}.webp", "WEBP", quality=86, method=6)
            assets["tok"].append(key)
    for key, rel in TOKENS.items():
        if key not in made and not (key in figs and key in EMBLEM) and (THUMBS / rel).is_file():
            square(THUMBS / rel).save(DIST / "art" / f"tok-{key}.webp", "WEBP", quality=86)
            assets["tok"].append(key)
    for key, what, letter, colour in DRAWN:
        if key in made or key in figs:
            continue
        im = disc(letter, colour)
        im.save(DIST / "art" / f"tok-{key}.webp", "WEBP", quality=86)
        assets["tok"].append(key)
        assets["drawn"].append([what, key])
        if key == "brother":  # a friend's face is asked for by name, not as a token
            im.save(DIST / "art" / "brother.webp", "WEBP", quality=86)
            assets["art"].append("brother")
    for key, f in made.items():
        Image.open(f).convert("RGB").resize((256, 256), Image.LANCZOS).save(DIST / "art" / f"tok-{key}.webp", "WEBP", quality=86, method=6)
        assets["tok"].append(key)
    for key, f in sorted(figs.items()):
        Image.open(f).convert("RGBA").resize((512, 768), Image.LANCZOS).save(DIST / "art" / f"fig-{key}.webp", "WEBP", quality=86, method=6)
        assets["fig"].append(key)
    for f in sorted((GAME / "art" / "cards").glob("*.webp")):  # a card's own picture, by the card's id
        shutil.copyfile(f, DIST / "art" / f"c-{f.stem}.webp")
        assets["art"].append(f"c-{f.stem}")
        assets["cardart"][f.stem] = f"c-{f.stem}"
    for kind in ("sfx", "music"):
        for f in sorted((GAME / kind).glob("*.*")):
            shutil.copyfile(f, DIST / kind / f.name)
            assets[kind][f.stem] = f"{kind}/{f.name}"

    def src(name):
        return (SRC / name).read_text(encoding="utf-8")
    page = (HEAD.replace("<title>The Line and the Hand</title>", "<title>The Unkneeling Campaign</title>")
            + "<style>\n" + src("style.css") + src("campaign.css") + "</style>\n\n" + src("campaign.html")
            + "\n<script>window.LH_ASSETS=" + json.dumps(assets, separators=(",", ":")) + "</script>\n"
            + "".join("<script>\n" + src(n) + "</script>\n" for n in ("engine.js", "campaign.js", "missions.js", "ui.js", "campaign_ui.js")))
    (DIST / "campaign.html").write_text(page, encoding="utf-8")
    files = sorted(str(p.relative_to(DIST)) for d in ("art", "sfx", "music") for p in (DIST / d).glob("*"))
    (DIST / "files.json").write_text(json.dumps(files, indent=1), encoding="utf-8")
    print(f"built game/dist/campaign/campaign.html ({len(page) // 1024} KB) · {len(assets['art'])} site pictures, {len(assets['tok'])} tokens "
          f"({len(assets['drawn'])} drawn for now), {len(assets['sfx'])} sounds, {len(assets['music'])} music tracks")


if __name__ == "__main__":
    main()
