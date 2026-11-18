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
import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont

from build import HEAD, SITE_ART, THUMBS, head

GAME = Path(__file__).resolve().parent
SRC, DIST = GAME / "src", GAME / "dist" / "campaign"
PLAY = GAME / "play"  # the game as an app, kept in git: the site build serves it at /play/
PLAY_URL = "https://bro2jo.github.io/leyenda/play/"
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


PLAY_HEAD = """<!doctype html>
<html lang="en" class="app">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">
<title>The Line and the Hand</title>
<meta name="description" content="The Chronicle, played: a map to hold, and every fight a hand of cards. A side game of The Unkneeling.">
<meta name="theme-color" content="#0B0E13">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Line and Hand">
<meta property="og:title" content="The Line and the Hand">
<meta property="og:description" content="The Chronicle, played: a map to hold, and every fight a hand of cards.">
<meta property="og:image" content="{url}icon-512.png">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" type="image/png" sizes="192x192" href="icon-192.png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Grenze+Gotisch:wght@500;700&family=Alegreya+Sans:ital,wght@0,400;0,500;0,700;1,400&family=Alegreya+Sans+SC:wght@500;700&display=swap">
"""
SW = """/* THE LINE AND THE HAND: the page kept for when there is no signal. Written by game/build_campaign.py; do not edit. */
var V='lh-__V__',CORE=__CORE__;
self.addEventListener('install',function(e){e.waitUntil(caches.open(V).then(function(c){return c.addAll(CORE)}).then(function(){return self.skipWaiting()}))});
self.addEventListener('activate',function(e){e.waitUntil(caches.keys().then(function(ks){return Promise.all(ks.map(function(k){return k.indexOf('lh-')===0&&k!==V?caches.delete(k):null}))}).then(function(){return self.clients.claim()}))});
/* the music is large: fetched whole in the background once the page is up, so the first visit is not held by it */
self.addEventListener('message',function(e){var w=e.data&&e.data.warm;if(!w||!w.length)return;
  e.waitUntil(caches.open(V).then(function(c){return Promise.all(w.map(function(u){return c.match(u).then(function(hit){return hit||fetch(u).then(function(r){if(r.ok&&r.status===200)return c.put(u,r)})}).catch(function(){})}))}))});
/* a player asks for a sound in pieces: a kept file is cut to the piece asked for */
function piece(req,res){var h=req.headers.get('range'),m=h&&/bytes=(\\d+)-(\\d*)/.exec(h);if(!m)return res;
  return res.arrayBuffer().then(function(b){var s=+m[1],t=m[2]?Math.min(+m[2],b.byteLength-1):b.byteLength-1;
    return new Response(b.slice(s,t+1),{status:206,statusText:'Partial Content',headers:{'Content-Type':res.headers.get('Content-Type')||'audio/mpeg','Content-Range':'bytes '+s+'-'+t+'/'+b.byteLength,'Content-Length':String(t-s+1),'Accept-Ranges':'bytes'}})})}
self.addEventListener('fetch',function(e){var q=e.request,u=new URL(q.url);if(q.method!=='GET')return;
  if(u.origin!==location.origin){ /* the lettering: kept as it comes, refreshed when there is signal */
    if(!/fonts\\.(googleapis|gstatic)\\.com$/.test(u.hostname))return;
    e.respondWith(caches.open(V).then(function(c){return c.match(q).then(function(hit){var net=fetch(q).then(function(r){c.put(q,r.clone());return r}).catch(function(){return hit});return hit||net})}));return}
  if(q.mode==='navigate'){ /* the page itself: the newest when there is signal, the kept one when there is not */
    e.respondWith(fetch(q).then(function(r){if(r.ok){var k=r.clone();caches.open(V).then(function(c){c.put('./',k)})}return r}).catch(function(){return caches.match('./',{cacheName:V})}));return}
  e.respondWith(caches.open(V).then(function(c){return c.match(u.pathname,{ignoreSearch:true}).then(function(hit){
    if(hit)return piece(q,hit);
    if(q.headers.get('range'))return fetch(q);
    return fetch(q).then(function(r){if(r.ok&&r.status===200)c.put(u.pathname,r.clone());return r})})}));
});
"""


def icon(size, pad=0.0):
    """The game's own icon: him in the high guard, head and blade, lit from behind on the night. With no pad it wears a brass
    ring; padded (a phone cuts its own shape out of the middle) his edges fade into the dark and there is no ring."""
    S = 1024
    im = Image.new("RGB", (S, S), "#0B0E13")
    d = ImageDraw.Draw(im)
    for r in range(int(S * .62), 0, -6):  # a warm light behind him
        k = (1 - r / (S * .62)) ** 1.4
        d.ellipse([S / 2 - r, S * .42 - r, S / 2 + r, S * .42 + r], fill=(int(11 + 62 * k), int(14 + 50 * k), int(19 + 26 * k)))
    src = THUMBS / "looks" / "the-high-guard.md.webp"
    if src.is_file():
        f = Image.open(src).convert("RGBA")
        w = f.width
        cut = f.crop((int(w * .22), 0, int(w * .92), int(w * .70)))  # head, shoulders and the raised blade: a square
        side = int(S * (1 - 2 * pad))
        cut = cut.resize((side, side), Image.LANCZOS)
        if pad:  # the cut edges melt away
            fade = Image.new("L", (side, side), 255)
            fd = ImageDraw.Draw(fade)
            n = int(side * .14)
            for i in range(n):
                v = int(255 * i / n)
                fd.line([(i, 0), (i, side)], fill=v)
                fd.line([(side - 1 - i, 0), (side - 1 - i, side)], fill=v)
            cut.putalpha(ImageChops.multiply(cut.split()[3], fade))
        im.paste(cut, ((S - side) // 2, S - side), cut)
    if not pad:
        e = int(S * .03)
        d.ellipse([e, e, S - e, S - e], outline="#CFA65F", width=int(S * .024))
    return im.resize((size, size), Image.LANCZOS)


def play(assets, src):
    """The game as an app, at /play/ on the site: the game alone on the page, the whole screen of a phone, on the home screen
    if he puts it there, playable without signal. game/play/ is kept in git (the site build copies it to docs/play/ and
    lays the music and the sounds beside it: engine/build_site.py); game/dist/play/ is the same with them, to open and test."""
    if PLAY.exists():
        shutil.rmtree(PLAY)
    shutil.copytree(DIST / "art", PLAY / "art")
    for size, name, pad in ((192, "icon-192.png", 0), (512, "icon-512.png", 0), (512, "icon-maskable.png", .1), (180, "apple-touch-icon.png", .04)):
        icon(size, pad).save(PLAY / name, "PNG", optimize=True)
    (PLAY / "manifest.webmanifest").write_text(json.dumps({
        "name": "The Line and the Hand", "short_name": "Line & Hand", "description": "The Chronicle, played: a map to hold, and every fight a hand of cards.",
        "start_url": "./", "scope": "./", "display": "standalone", "display_override": ["fullscreen", "standalone"], "orientation": "portrait",
        "background_color": "#0B0E13", "theme_color": "#0B0E13", "categories": ["games"],
        "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
                  {"src": "icon-maskable.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]}, indent=1) + "\n", encoding="utf-8")
    warm = sorted(assets["music"].values())
    page = (PLAY_HEAD.replace("{url}", PLAY_URL) + "<style>\n" + src("style.css") + src("campaign.css") + src("play.css") + "</style>\n</head>\n<body>\n"
            + '<div class="phone" id="game" aria-label="The Line and the Hand"></div>\n<noscript class="app-no">The Line and the Hand is a game: it needs JavaScript to run.</noscript>\n'
            + "<script>window.LH_ASSETS=" + json.dumps(assets, separators=(",", ":")) + ";window.LH_WARM=" + json.dumps(warm) + "</script>\n"
            + "".join("<script>\n" + src(n) + "</script>\n" for n in ("app.js", "engine.js", "campaign.js", "missions.js", "ui.js", "campaign_ui.js")) + "</body>\n</html>\n")
    (PLAY / "index.html").write_text(page, encoding="utf-8")
    core = ["./", "manifest.webmanifest"] + sorted(str(p.relative_to(PLAY)) for p in PLAY.rglob("*") if p.is_file() and p.name != "index.html" and p.suffix != ".webmanifest") + sorted(assets["sfx"].values())
    stamp = hashlib.sha1()
    for p in sorted(PLAY.rglob("*")) + sorted((GAME / "sfx").glob("*.*")) + sorted((GAME / "music").glob("*.*")):
        if p.is_file():
            stamp.update(p.name.encode() + hashlib.sha1(p.read_bytes()).digest())
    (PLAY / "sw.js").write_text(SW.replace("__V__", stamp.hexdigest()[:12]).replace("__CORE__", json.dumps(core, separators=(",", ":"))), encoding="utf-8")
    full = GAME / "dist" / "play"
    if full.exists():
        shutil.rmtree(full)
    shutil.copytree(PLAY, full)
    for kind in ("sfx", "music"):
        shutil.copytree(DIST / kind, full / kind)
    print(f"built game/play/ ({len(page) // 1024} KB page, {sum(1 for _ in (PLAY / 'art').glob('*'))} pictures, kept in git for the site's /play/) and game/dist/play/ with its sounds")


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
    play(assets, src)
    print(f"built game/dist/campaign/campaign.html ({len(page) // 1024} KB) · {len(assets['art'])} site pictures, {len(assets['tok'])} tokens "
          f"({len(assets['drawn'])} drawn for now), {len(assets['sfx'])} sounds, {len(assets['music'])} music tracks")


if __name__ == "__main__":
    main()
