#!/usr/bin/env python3
"""THE UNKNEELING — files Darrow's looks for the Wardrobe: the picture in saga/art/looks/, its entry in saga/state/looks.json.

  python3 engine/looks.py add PICTURE "Look: side=… pose=… … · touches: …" --name "Title" --alt "what it shows" [--id ID]
  python3 engine/looks.py replace ID PICTURE [--alt "what the new one shows"]   a new picture for a look already filed
  python3 engine/looks.py check PICTURE [--preview DIR]                         the background and the cut-out, nothing filed
  any of them: --drop X,Y clears one separate piece of the finished picture (a stray third boot), never one joined to him

The picture: a chroma screen (the Forge asks for flat #0000FF blue, or #00FF00 green when the look wears blue) is keyed
out; one with a real alpha channel is kept as it is. Either way it is cut to 2:3 at 1024x1536 and saved as WebP. Anything
else (a painted backdrop, a checkerboard, a dark wash) is refused: ask for the screen again (the Forge's Paint it, step 3).
The Look line must name one piece of every category, pieces that go together (engine/build_site.py wardrobe_clash).
--preview DIR writes the cut-out over the site's stage and over a contrasting colour, to look at before filing.
Then: python3 engine/darrow.py ship -m "Wardrobe: …". Needs Pillow and numpy.
"""
import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
LOOKS = ROOT / "saga" / "state" / "looks.json"
PICTURES = ROOT / "saga" / "art" / "looks"
WARDROBE = ROOT / "engine" / "wardrobe.json"
SIZE = (1024, 1536)          # every look: 2:3
LO, HI = 25, 170             # how far the screen's channel stands above the other two: at or below LO solid, at or above HI screen
BAND = 24                    # the screen's tint is pulled back within 2*BAND px of the outline (painted haze at a post's foot reaches far)
SOLID_FROM = 160             # this far from the screen colour (RGB distance), a pixel is solid whatever its hue (a navy cloak on blue)
STAGE, CONTRAST = (33, 31, 33), {0: (0, 170, 255), 1: (220, 0, 200), 2: (255, 170, 0)}  # previews: the site's stage; a colour far from the screen

sys.path.insert(0, str(ROOT / "engine"))


def die(msg):
    sys.exit(f"looks: {msg}")


# ---------------------------------------------------------------- the picture
def background(rgba):
    """('alpha', None) for a real alpha channel, ('screen', channel) for a flat chroma screen, or (None, why)."""
    if (rgba[..., 3] < 10).mean() > 0.05:
        return "alpha", None
    a = rgba[..., :3]
    edge = np.concatenate([a[:10].reshape(-1, 3), a[-10:].reshape(-1, 3), a[:, :10].reshape(-1, 3), a[:, -10:].reshape(-1, 3)])
    med = np.median(edge, axis=0)
    flat = (np.linalg.norm(edge - med, axis=1) < 40).mean()  # a post or a wall may run off the frame: most of the edge is enough
    dom = int(np.argmax(med))
    others = [med[i] for i in range(3) if i != dom]
    if med[dom] >= 150 and max(others) <= 110 and flat >= 0.8:
        return "screen", dom
    return None, (f"the background is neither transparent nor a flat chroma screen (edge colour {med.round().astype(int).tolist()}, "
                  f"{100 * flat:.0f}% of the edge that colour)")


def key(rgba, dom):
    """The screen keyed out: alpha from how far the screen's channel stands above the other two (anything far from the
    screen colour is solid); the faint edge pixels take the colour of the solid pixels near them; a band along the outline
    has the screen's colour pulled back to neutral (only there, so the figure's own greys and eyes keep their cast); specks
    with no solid core near them are cleared."""
    a = rgba[..., :3]
    o1, o2 = [i for i in range(3) if i != dom]
    edge = np.concatenate([a[:10].reshape(-1, 3), a[-10:].reshape(-1, 3), a[:, :10].reshape(-1, 3), a[:, -10:].reshape(-1, 3)])
    screen = np.median(edge, axis=0)
    keyness = a[..., dom] - np.maximum(a[..., o1], a[..., o2])
    alpha = np.clip((HI - keyness) / (HI - LO), 0, 1)
    alpha = np.maximum(alpha, np.clip((np.linalg.norm(a - screen, axis=2) - (SOLID_FROM - 40)) / 40, 0, 1))
    rgb = a.copy()
    solid = (alpha >= 0.9).astype(np.float32)

    def blur(x, r):
        return np.asarray(Image.fromarray(np.clip(x, 0, 255).astype(np.uint8)).filter(ImageFilter.BoxBlur(r))).astype(np.float32)

    def near_colour(r):  # the average colour of the solid pixels within r, and how much of the neighbourhood is solid
        wt = blur(solid * 255, r) / 255
        return np.dstack([blur(a[..., i] * solid, r) for i in range(3)]) / np.maximum(wt, 1e-3)[..., None], wt

    col5, w5 = near_colour(5)
    col15, w15 = near_colour(15)
    soft = (alpha > 0) & (alpha < 0.9)
    use5 = soft & (w5 > 0.02)
    use15 = soft & ~use5 & (w15 > 0.005)
    rgb[use5], rgb[use15] = col5[use5], col15[use15]
    alpha[soft & ~use5 & ~use15] = 0  # a wisp with nothing solid near it
    clear = Image.fromarray(((alpha < 0.05) * 255).astype(np.uint8))
    for _ in range(BAND):  # BAND steps of 2 px out from the outline
        clear = clear.filter(ImageFilter.MaxFilter(5))
    band = (np.asarray(clear) > 0) & (alpha > 0)
    neutral = np.minimum((rgb[..., o1] + rgb[..., o2]) / 2 + 4, np.maximum(rgb[..., o1], rgb[..., o2]))
    rgb[..., dom] = np.where(band, np.minimum(rgb[..., dom], neutral), rgb[..., dom])
    alpha[~near_core(alpha >= 0.9)] = 0
    return np.dstack([rgb, alpha * 255])


def near_core(solid):
    """What lies within about 12 px of a solid core 9 px across: the figure with its thin wisps and a sword's tip, but
    not a speck, nor the faint strokes left where a dropped piece stood."""
    core = Image.fromarray((solid * 255).astype(np.uint8))
    for _ in range(4):
        core = core.filter(ImageFilter.MinFilter(3))
    for _ in range(6):
        core = core.filter(ImageFilter.MaxFilter(5))
    return np.asarray(core) > 0


def fit(rgba):
    """Cut to 2:3 about the middle (the margin, never the figure, when the picture is close to 2:3) and scale to SIZE."""
    h, w = rgba.shape[:2]
    im = Image.fromarray(np.clip(rgba, 0, 255).round().astype(np.uint8), "RGBA")
    if abs(w / h - 2 / 3) > 0.002:
        if w / h > 2 / 3:
            tw = round(h * 2 / 3)
            im = im.crop(((w - tw) // 2, 0, (w - tw) // 2 + tw, h))
        else:
            th = round(w * 3 / 2)
            im = im.crop((0, (h - th) // 2, w, (h - th) // 2 + th))
    return im.convert("RGBa").resize(SIZE, Image.LANCZOS).convert("RGBA")


def drop(out, points):
    """Clear each separate piece of the finished picture at an (x, y) point of the 1024x1536 result: something ChatGPT
    drew that the look does not wear (a stray third boot). A piece joined to the figure is never cleared."""
    arr = np.asarray(out).copy()
    notes = []
    for x, y in points:
        solid = arr[..., 3] >= 160  # pieces are traced by their solid pixels: faint edges touch everything
        if not (0 <= x < SIZE[0] and 0 <= y < SIZE[1]) or not solid[y, x]:
            die(f"--drop {x},{y} is not on anything solid in the picture (see the previews; the picture is {SIZE[0]}x{SIZE[1]})")
        m = Image.fromarray((solid * 255).astype(np.uint8)).copy()
        ImageDraw.floodfill(m, (x, y), 128)
        piece = np.asarray(m) == 128
        share = piece.sum() / solid.sum()
        if share > 0.15:
            die(f"--drop {x},{y}: that piece is joined to the figure ({100 * share:.0f}% of everything drawn); nothing dropped")
        rim = Image.fromarray((piece * 255).astype(np.uint8))
        for _ in range(3):  # its own soft edge, a few pixels out, and never another piece's solid pixels
            rim = rim.filter(ImageFilter.MaxFilter(3))
        arr[(np.asarray(rim) > 0) & ~(solid & ~piece), 3] = 0
        arr[~near_core(arr[..., 3] >= 230), 3] = 0  # the faint strokes it leaves behind
        notes.append(f"dropped a separate piece of {int(piece.sum())} px at {x},{y}")
    return Image.fromarray(arr, "RGBA"), notes


def cut_out(path, preview=None, drops=()):
    """The picture as a finished look (an RGBA image at SIZE) and a line about what was done; refuses what it cannot cut."""
    try:
        rgba = np.asarray(Image.open(path).convert("RGBA")).astype(np.float32)
    except (OSError, ValueError) as e:
        die(f"cannot open {path}: {e}")
    kind, dom = background(rgba)
    if kind is None:
        die(f"{dom}. Ask for the picture on one solid, flat chroma blue (#0000FF), or green (#00FF00) when he wears blue.")
    out = fit(key(rgba, dom) if kind == "screen" else rgba)
    out, dropped = drop(out, drops)
    o = np.asarray(out).astype(int)
    seen = "a real alpha channel, kept" if kind == "alpha" else f"a {('red', 'green', 'blue')[dom]} screen, keyed out"
    tinted = 0 if kind == "alpha" else int(((o[..., 3] > 0) & (o[..., dom] > np.maximum(*[o[..., i] for i in range(3) if i != dom]) + 12)).sum())
    note = f"{seen}; {100 * (o[..., 3] == 0).mean():.0f}% clear" + (f", {tinted} pixels still tinted by the screen" if kind == "screen" else "")
    if dropped:
        note += "; " + "; ".join(dropped)
    if preview:
        d = Path(preview)
        d.mkdir(parents=True, exist_ok=True)
        for name, col in (("stage", STAGE), ("contrast", CONTRAST[dom if dom is not None else 2])):
            Image.alpha_composite(Image.new("RGBA", SIZE, col + (255,)), out).convert("RGB").save(d / f"preview-{name}.png")
        note += f"; previews in {d}"
    return out, note


# ---------------------------------------------------------------- the book
def load_book():
    return json.loads(LOOKS.read_text(encoding="utf-8")) if LOOKS.exists() else {"_about": "", "looks": []}


def save_book(book):
    """looks.json as it is kept: one key per line, the values on one line."""
    out = ["{"]
    keys = list(book)
    for i, k in enumerate(keys):
        tail = "," if i < len(keys) - 1 else ""
        if k != "looks":
            out.append(f"  {json.dumps(k)}: {json.dumps(book[k], ensure_ascii=False)}{tail}")
            continue
        out.append('  "looks": [')
        for j, lk in enumerate(book["looks"]):
            body = ",\n".join(f"      {json.dumps(f)}: {json.dumps(v, ensure_ascii=False)}" for f, v in lk.items())
            out.append("    {\n" + body + "\n    }" + ("," if j < len(book["looks"]) - 1 else ""))
        out.append("  ]" + tail)
    out.append("}")
    LOOKS.write_text("\n".join(out) + "\n", encoding="utf-8")


def parse_look(line):
    """'Look: side=rae pose=rae-cup … · touches: rain on the cloak' → ({category: piece}, touches)."""
    text = re.sub(r"^\s*Look:\s*", "", line.strip())
    text, _, touches = text.partition("· touches:")
    values = {}
    for tok in text.split():
        if "=" not in tok:
            die(f"'{tok}' in the Look line is not category=piece")
        c, v = tok.split("=", 1)
        values[c] = v
    return values, touches.strip()


def check_pieces(values):
    """One piece of every category, each a real piece, all of them going together."""
    from build_site import wardrobe_clash
    cats = {c["id"]: {o["id"]: o for o in c["options"]} for c in json.loads(WARDROBE.read_text(encoding="utf-8"))["categories"]}
    bad = [f"{c}={v}" for c, v in values.items() if v not in cats.get(c, {})] + [f"{c} missing" for c in cats if c not in values]
    if bad:
        die(f"the Look line does not match engine/wardrobe.json: {', '.join(bad)}")
    pairs = list(values.items())
    clash = [f"{c}={v} with {d}={u}" for i, (c, v) in enumerate(pairs) for d, u in pairs[i + 1:] if wardrobe_clash(c, cats[c][v], d, cats[d][u])]
    if clash:
        die(f"these pieces do not go together: {', '.join(clash)}")
    return {c: values[c] for c in [cid for cid in cats]}


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def save_picture(img, look_id):
    PICTURES.mkdir(parents=True, exist_ok=True)
    dest = PICTURES / f"{look_id}.webp"
    img.save(dest, "WEBP", quality=90, method=6)
    return f"looks/{look_id}.webp"


# ---------------------------------------------------------------- commands
def cmd_add(args):
    values, touches = parse_look(args.look)
    values = check_pieces(values)
    book = load_book()
    look_id = args.id or slug(args.name)
    if not look_id or any(lk["id"] == look_id for lk in book["looks"]):
        die(f"a look named '{look_id}' is already filed: give another --name or --id, or use replace")
    img, note = cut_out(args.picture, args.preview, args.drop)
    book["looks"].append({"id": look_id, "name": args.name, "made": dt.datetime.now(ZoneInfo("America/New_York")).date().isoformat(),
                          "image": save_picture(img, look_id), "alt": args.alt, "values": values, "details": touches})
    save_book(book)
    print(f"filed {look_id} ({args.name}): {note}. Then ship.")


def cmd_replace(args):
    book = load_book()
    lk = next((x for x in book["looks"] if x["id"] == args.id), None)
    if not lk:
        die(f"no look '{args.id}' in saga/state/looks.json ({', '.join(x['id'] for x in book['looks'])})")
    img, note = cut_out(args.picture, args.preview, args.drop)
    lk["image"] = save_picture(img, lk["id"])
    if args.alt:
        lk["alt"] = args.alt
    save_book(book)
    print(f"{lk['id']} has its new picture: {note}{'' if args.alt else '; its alt is as it was'}. Then ship.")


def cmd_check(args):
    _, note = cut_out(args.picture, args.preview, args.drop)
    print(note)


def point(text):
    try:
        x, y = (int(v) for v in text.split(","))
    except ValueError:
        raise argparse.ArgumentTypeError("a point is X,Y in the finished 1024x1536 picture, e.g. 630,1380")
    return x, y


def main():
    p = argparse.ArgumentParser(prog="looks.py", description=__doc__.split("\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add", help="file a new look from its picture and Look line")
    a.add_argument("picture")
    a.add_argument("look", help='the Look line: "Look: side=… pose=… … · touches: …"')
    a.add_argument("--name", required=True, help="its title in the lookbook")
    a.add_argument("--alt", required=True, help="what the picture shows, for readers who cannot see it")
    a.add_argument("--id", help="its id (default: from the name)")
    a.add_argument("--preview", help="a folder for the previews")
    a.add_argument("--drop", type=point, action="append", default=[], help="X,Y: clear the separate piece there (a stray boot)")
    r = sub.add_parser("replace", help="a new picture for a look already filed")
    r.add_argument("id")
    r.add_argument("picture")
    r.add_argument("--alt", help="what the new picture shows (default: keep the old)")
    r.add_argument("--preview", help="a folder for the previews")
    r.add_argument("--drop", type=point, action="append", default=[], help="X,Y: clear the separate piece there (a stray boot)")
    c = sub.add_parser("check", help="what the picture's background is, and the cut-out, nothing filed")
    c.add_argument("picture")
    c.add_argument("--preview", help="a folder for the previews")
    c.add_argument("--drop", type=point, action="append", default=[], help="X,Y: clear the separate piece there (a stray boot)")
    args = p.parse_args()
    {"add": cmd_add, "replace": cmd_replace, "check": cmd_check}[args.cmd](args)


if __name__ == "__main__":
    main()
