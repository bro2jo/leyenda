#!/usr/bin/env python3
"""THE LINE AND THE HAND: every picture the game still wants, as a prompt that stands by itself. A picture that is filed
(game/art/figures/, tokens/, cards/) leaves the list by itself the next time this runs.

  python3 game/tools/prompts.py        writes game/art/PROMPTS.md and the prompts section of game/src/campaign.html

One table, three kinds of picture: a full figure for the clash (2:3, on a blue screen, cut out by file_art.py; the build cuts
its map token from its head), a square token for what is seen only on the map, and a card picture (4:3). Each prompt is whole: subject, then style, then format, so it can be pasted as it is.
Rules it holds itself to (and checks): under 150 words; plain words an image model knows (no gambeson, no lymer); one
subject; say which way it faces; nothing vague. A foe faces left, a friend faces right. Attach one of Darrow's looks as the
style reference; for anyone the Chronicle already has a face for, attach that portrait as well and the prompt says so."""
import html
import re
import sys
from pathlib import Path

GAME = Path(__file__).resolve().parent.parent
# The house wording, taken from the prompt that made the Chronicle's own portraits, so the game's pictures sit beside them:
# the kind of picture first, then the subject, then these style words, then what to keep out, then the format.
LOOK = "Painterly semi-realistic video game character art, visible brushwork, grounded dark fantasy, muted medieval palette, realistic skin texture, natural asymmetry, soft daylight."
ART = "Painterly semi-realistic video game art, visible brushwork, grounded dark fantasy, muted medieval palette."  # the same, where no face is the subject; the light is the subject's own
KEEP_OUT = "No caricature, no glamour styling, no exaggerated beauty, no flashy armor. Not a photo or 3D render."
REF = "Match the painting style of the attached image."
STYLE = f"{LOOK} {KEEP_OUT} {REF}"
LEAD = {"figure": "Fantasy RPG character art, full-body figure:", "animal": "Fantasy RPG creature art, full body:", "card": "Fantasy RPG card illustration, a close view of one clear action:",
        "scene": "Fantasy RPG environment art:", "solo": "Fantasy RPG character portrait, tight shoulders-up headshot:"}
FACE = "A distinct, individual face, plain rather than handsome."
def fig(face, what="figure"):
    return (f"Vertical 2:3 image. One {what} only, whole body with a margin all round, turned three-quarters toward the {face} side of the image. "
            "Background: flat pure blue (#0000FF) filling the whole image, like a blue screen. No ground, no shadow, no text. Nothing blue on the " + what + ".")
SCENE = ART + " Square 1:1 image, the subject in the centre with space all round for a circular crop. No people in close-up, no text, no border."
CARD = "Softly blurred background. " + ART + " Not a photo or 3D render. 4:3 landscape. No text, no border, no frame."
SAME = "The same person as in the attached portrait: same face, hair, age and clothes. "

# name, title, group, facing, subject, note (where the look comes from)
FIGURES = [
 ("sergeant", "The levy sergeant", "The campaign's own", "left", "A broad, loud-looking man in his forties in a thick tan leather coat, with a short wooden officer's stick tucked under one arm. Plain iron helmet, heavy boots, a sheathed sword at his belt. His mouth is open as if shouting an order.", "From the page: a broad man in a buff coat, a voice like a barn door, a sergeant's stick under his arm."),
 ("pitchfork", "The boy with the pitchfork", "The campaign's own", "left", "A nervous farm boy of sixteen in a patched brown wool tunic and an iron helmet too big for him. He holds a wooden hay pitchfork in both hands, pointed forward at arm's length, leaning back from it.", "The page has the pitchfork; the boy's look is mine."),
 ("hornboy", "The boy with the horn", "The campaign's own", "left", "A farm boy of fifteen in a patched brown wool tunic, with a curved cow-horn signal horn on a cord round his neck. One hand lifts the horn toward his mouth; the other holds a spear much too long for him.", "The page has the muster horn; the boy's look is mine."),
 ("greycloak", "A grey cloak", "The campaign's own", "left", "A plain, patient man of forty in a long hooded grey wool cloak down to his boots, hood down. A folded paper tucked in his belt, a short wooden club in his hand. Calm face, searching eyes.", "The page gives the grey cloak and the list; the rest is mine."),
 ("lymer", "The lymer", "The campaign's own", "left", "A heavy, low-built bloodhound-type tracking dog with loose wrinkled skin, a broad nose and long hanging ears. Nose low to the ground, pulling forward on a long leather leash that runs out of the right side of the image. No handler.", "From the page: heavy, low-built, loose in the skin, a nose like a spade, ears to its jaw."),
 ("guest", "A Confessor's man", "The campaign's own", "left", "A hard-faced man of thirty with cropped hair and a thick neck, in a dark grey wool coat and leather gloves. He holds a heavy wooden club low in one hand and stands square, watching.", "Mine: the page says only that they are the Confessor's men."),
 ("darkcoat", "A rider in a dark coat", "The campaign's own", "left", "A lean man standing on foot in a long charcoal-black riding coat, tall boots, gloves and a wide-brimmed hat. One hand is raised as if holding a horse's rein; the other rests on the handle of a sheathed sword.", "The page says only: four riders in dark coats."),
 ("walker", "A walker", "The campaign's own", "left", "A gaunt man walking forward with empty hands and blank eyes that look at nothing. He wears chainmail under a sleeveless cloth tunic so faded that its colours cannot be made out. White frost in his beard and hair, pale grey skin.", "From the page: mail under a surcoat whose colours had washed out, frost in his beard."),
 ("ysra-tal", "Ysra Tal", "The campaign's own", "left", SAME + "She stands balanced with a drawn sword held low in one hand.", "Attach her portrait from the site as well."),
 ("hollis", "Hollis", "Beside him", "right", SAME + "He stands ready with a sword in his hand.", "Attach his portrait from the site as well."),
 ("ash", "Ash", "Beside him", "right", "The same dog as in the attached picture: same coat, same size, same markings. She stands alert with her head up and ears forward.", "Attach her picture from the site as well."),
 ("wren", "Wren", "Beside him", "right", SAME + "She has a small round stone in her raised hand, ready to throw.", "Attach her portrait from the site as well."),
 ("pikeman", "Pikeman", "The road's hired company (made up for the game)", "left", "A lean, long-armed man in his thirties with a narrow watchful face. Wide-brimmed iron helmet, padded quilted jacket, a faded brick-red sash. He holds a long wooden pike in both hands, levelled forward.", ""),
 ("swordsman", "Swordsman", "The road's hired company (made up for the game)", "left", "A wiry man in his late twenties with cropped dark hair and an old scar on his chin, bare-headed. A short chainmail shirt under a faded brick-red sleeveless tunic. He holds a straight one-handed sword low and forward.", ""),
 ("crossbowman", "Crossbowman", "The road's hired company (made up for the game)", "left", "A stocky soldier in his forties with a weathered, squinting face. Brown wool hood, thick padded jacket, a faded brick-red sash across his chest. He holds a loaded wooden crossbow at his hip, aimed forward, with a leather case of bolts at his belt.", ""),
 ("skirmisher", "Skirmisher", "The road's hired company (made up for the game)", "left", "A slim young man of about twenty with tangled fair hair and a sharp grin. Short undyed wool tunic, a faded brick-red scarf, bare forearms, soft leather boots. A short curved knife in each hand, crouched low and ready to spring.", ""),
 ("shieldbearer", "Shieldbearer", "The road's hired company (made up for the game)", "left", "A broad, heavy man in his thirties with a thick neck and a calm face. Round iron helmet with a nose bar, knee-length chainmail shirt, faded brick-red belt. A tall wooden shield held in front of him, a short axe in his other hand.", ""),
 ("bannerman", "Bannerman", "The road's hired company (made up for the game)", "left", "A tall, straight-backed man of fifty with a grey moustache. Wide-brimmed iron helmet, plain steel breastplate over a padded jacket. He holds a tall pole with a long faded brick-red banner on it, and has a short sword at his belt.", ""),
 ("captain", "Captain", "The road's hired company (made up for the game)", "left", "A big man in his forties with heavy brows, a broken nose and a short iron-grey beard, bare-headed. Scratched steel breastplate over chainmail, a faded brick-red cloak over one shoulder. He rests a long two-handed sword point-down in front of him.", ""),
]
ORDEALS = [
 ("wend", "The Wend in spate", "A wide brown river in flood: fast muddy water with white foam, seen from the bank under a grey rainy sky."),
 ("hall", "The length of the hall", "A long dark stone hall with two rows of narrow beds, seen down its whole length, with one candle burning in the foreground."),
 ("question", "The hall's question", "A crowd of worried people in a candle-lit stone hall, standing between rows of beds, all turned to look straight at the viewer."),
 ("sliver", "The black glass", "A long splinter of black glass set in a niche in an old stone wall, with thin white frost spreading over the stones around it."),
 ("steps", "A stretch of the Steps", "A steep, narrow stone stair cut into a grey cliff, going down into low cloud, with wet steps and no railing."),
]
CARDS = [
 ("b_strike", "Strike", "everyone", "A gloved hand swinging a plain iron sword in a fast sideways cut, the blade blurred with speed."),
 ("b_guard", "Guard", "everyone", "A forearm raising a round wooden shield as a sword blade strikes it, chips of wood flying."),
 ("hew", "Hew", "Hollis", "Two old, scarred hands bringing a heavy sword down in a hard overhead cut."),
 ("fast", "Stand Fast", "Hollis", "A wooden peg leg and a worn leather boot planted wide apart on wet flagstones, braced against a push."),
 ("bellow", "Bellow", "Hollis, and the fire", "An old soldier's face shouting with his mouth wide open, his breath steaming in cold air."),
 ("legs", "Take the Legs", "Ash, and the fire", "A grey dog lunging low to bite at a man's boot, the man starting to fall."),
 ("worry", "Worry", "Ash", "A grey dog's jaws clamped on a man's coat sleeve, pulling it hard to one side."),
 ("slip", "Slip Away", "Ash", "A grey dog darting away between two pairs of legs, low and fast, ears flat back."),
 ("stone", "Thrown Stone", "Wren", "A small hand at the end of a throw, a round grey stone just leaving the fingers."),
 ("count", "The Count", "Wren", "A girl's hand held up counting on her fingers in the light of a small candle."),
 ("duck", "Duck", "Wren", "A small figure in a wool cloak ducking low as a sword blade passes just over her hood."),
 ("bandage", "Clean Bandage", "the fire", "Two hands wrapping a strip of clean white linen round a forearm."),
 ("closeup", "Close Up", "the fire", "Three people standing shoulder to shoulder with wooden shields touching, seen from behind."),
 ("readline", "Read the Line", "the fire", "A pair of narrowed eyes under a hood, watching a row of distant soldiers on a hillside."),
 ("callco", "Call the Company", "the fire", "A raised arm waving forward, with several figures running up behind it across open ground."),
 ("secondwind", "Second Wind", "the fire", "A tired man straightening up and taking a deep breath, cold mist coming from his mouth, morning light on his face."),
 ("twice", "Second Cut", "the fire", "A sword caught at two moments of one fast double cut, drawn as two blurred blades crossing."),
 ("pinshot", "Pinning Throw", "the fire", "A short spear stuck through the hem of a running man's cloak, pinning it to the ground."),
 ("finish", "Finish It", "the fire", "A sword point held steady a hand's width from the chest of a man who has dropped to one knee."),
 ("follow", "Follow Through", "the fire", "A long sweeping sword cut passing one soldier and reaching toward a second standing beside him."),
 ("digin", "Dig In", "the fire", "A boot heel pressed hard into muddy ground behind a wooden shield planted upright in the earth."),
 ("bloodup", "Blood Up", "the fire", "A clenched fist tight round a sword handle, knuckles white, a red scarf tied at the wrist."),
 ("steady", "Steady Hand", "the fire", "An open hand held out flat and perfectly still above a small candle flame."),
 ("strip", "Strip the Fallen", "the fire", "A hand pulling a leather coin purse from the belt of a fallen soldier lying on the grass."),
 ("spoils", "Spoils of the Road", "the fire", "A few silver coins and a brass ring spilled on a rough wool blanket beside a campfire."),
]
# people seen only on the map: they never stand in a clash, so a token is the whole of it
PEOPLE = [
 ("rider", "An outrider", "A cavalry scout in a short dark green riding jacket over chainmail and an open iron helmet, with an alert, weathered face."),
 ("brother", "A lay brother", "A sturdy man of fifty with short grey hair and a kind, tired face, in a plain undyed wool robe."),
]
SOLO = (FACE + " Softly blurred background. " + f"{LOOK} {KEEP_OUT}" + " Eye-level centered square headshot, shoulders visible, turned slightly to the left, "
        "space all round the head for a circular crop. No text, no border.")
# how much he will notice each one: where it is seen and how often, counted from the missions and the decks. Highest first.
IMPACT = {
 "card:b_strike": (100, "22 copies across the company's decks: the card drawn most often in the whole game"),
 "card:b_guard": (95, "15 copies across the company's decks"),
 "who:hollis": (92, "He fights in four missions and every battle on the road; today a boxed portrait stands in for him"),
 "who:wren": (91, "She fights in four missions and every battle on the road"),
 "who:ash": (90, "She fights in three missions and every battle on the road"),
 "who:captain": (88, "The last fight of every battle on the road"),
 "who:greycloak": (86, "Eight of them across two missions, more than any other foe in the campaign"),
 "card:stone": (84, "12 copies: three in Wren's deck, in every fight she is in"),
 "card:hew": (82, "8 copies, and it is Hollis's combo card"),
 "card:fast": (81, "8 copies: the block that sets up Hew"),
 "card:count": (80, "8 copies in Wren's deck"),
 "who:ysra-tal": (78, "One mission, but she is all of it: every clash of The Post is against her"),
 "who:darkcoat": (76, "All four riders at the weir wear this picture"),
 "who:crossbowman": (74, "On the road in every run"), "who:shieldbearer": (73, "On the road in every run"), "who:skirmisher": (72, "On the road in every run"), "who:bannerman": (71, "On the road in every run"),
 "tok:steps": (70, "Four of them down the long stair, the longest mission there is"),
 "who:guest": (68, "All three men on the bell tower stair; a grey cloak's picture stands in for now"),
 "card:legs": (66, "6 copies, and it is Ash's combo card"), "card:worry": (65, "6 copies: the opening that sets up Take the Legs"), "card:slip": (64, "6 copies in Ash's deck"),
 "tok:wend": (63, "The first thing on the board in the first mission"), "tok:hall": (62, "Both stretches of the second mission"),
 "card:bellow": (60, "4 copies, and one more at the fire"), "card:duck": (59, "4 copies in Wren's deck"),
 "who:walker": (58, "Both walkers on the mill bridge"), "who:lymer": (56, "One fight at the fold, but there is nothing else like it on the board"),
 "tok:question": (54, "One mission"), "tok:sliver": (53, "One mission"),
 "who:sergeant": (50, "One mission, and the captain's picture stands in for now"), "who:pitchfork": (49, "One mission"), "who:hornboy": (48, "One mission, and the pitchfork boy's picture stands in for now"),
 "tok:rider": (40, "Seen only on the map, in one mission"), "tok:brother": (39, "Seen only on the map, in one mission"),
 "who:pikeman": (4, "Made already"), "who:swordsman": (3, "Made already"),
}
LIMIT = 150  # the prompt this wording comes from ran to 330 words and held; the first 150 are what every generator reads
BANNED = ["gambeson", "kettle", "madder", "hauberk", "cuirass", "coif", "lymer", "surcoat", "buff coat", "jack ", "nasal helm", "spate", "levy"]

def figure_prompt(r):
    what = "animal" if r[0] in ("lymer", "ash") else "figure"
    face = "" if what == "animal" or r[4].startswith(SAME) else FACE + " "
    style = f"{ART} Soft daylight. Not a photo or 3D render. {REF}" if what == "animal" else STYLE
    return f"{LEAD[what]} {r[4]} {face}{style} {fig(r[3], what)}"
def words(t):
    return len(re.findall(r"\S+", t))
KIND = {"who": "Figure", "tok": "Token", "card": "Card"}
FOLDER = {"who": "figures", "tok": "tokens", "card": "cards"}
def made(kind, name):
    return (GAME / "art" / FOLDER[kind] / (name + ".webp")).is_file()
def items(everything=False):
    out = [("who", r[0], r[1], figure_prompt(r), r[5]) for r in FIGURES]
    out += [("tok", o[0], o[1], f"{LEAD['scene']} {o[2]} {SCENE}", "") for o in ORDEALS] + [("tok", q[0], q[1], f"{LEAD['solo']} {q[2]} {SOLO}", "") for q in PEOPLE]
    out += [("card", c[0], f"{c[1]} ({c[2]})", f"{LEAD['card']} {c[3]} {CARD}", "") for c in CARDS]
    def score(it):
        return IMPACT.get(it[0] + ":" + it[1], (30, "Only when it is bought at the fire"))
    out.sort(key=lambda it: -score(it)[0])
    return [it + (score(it)[1],) for it in out if everything or not made(it[0], it[1])]
def check():
    bad = []
    allp = [(it[1], it[3]) for it in items(True)]
    for name, p in allp:
        if words(p) > LIMIT:
            bad.append(f"{name}: {words(p)} words")
        for b in BANNED:
            if b in p.lower():
                bad.append(f"{name}: uses '{b.strip()}'")
    if bad:
        sys.exit("prompts: " + "; ".join(bad))
    return allp

def main():
    allp, its = check(), items()
    done = [it for it in items(True) if made(it[0], it[1])]
    was = "Made already: " + ", ".join(f"{it[2]} ({KIND[it[0]].lower()})" for it in done) + "." if done else ""
    md = ["# The Line and the Hand: pictures to make, most noticed first", "",
          "Every prompt here is whole: paste it as it is, and attach one of Darrow's looks as the style reference. Start at the top: they are in order of how much he will notice each one.",
          "Send a picture back with its name and kind, and it is filed with `python3 game/tools/file_art.py figure|token|card NAME FILE`.",
          "A figure is one picture: its map token is cut from its head when the game is built.", "", was, ""]
    h = [f'    <p class="small" id="cp-made">{html.escape(was)}</p>', '    <ol class="prompts ranked">']
    for n, (kind, name, title, prompt, note, why) in enumerate(its, 1):
        pid = f"pp-{kind}-{name}"
        h.append(f'      <li class="prompt"><div class="ph"><h3 data-{kind}="{name}"><span class="rk-n">{n}</span> <span class="kind k-{kind}">{KIND[kind]}</span> {html.escape(title)} <code>{name}</code></h3><button type="button" class="mini2" data-copy="{pid}">Copy</button></div>\n'
                 f'<p class="small why">{html.escape(why)}.</p>\n<pre id="{pid}">{html.escape(prompt)}</pre>' + (f'<p class="small">{html.escape(note)}</p>' if note else "") + "</li>")
        md.extend([f"## {n}. {KIND[kind]}: {title} (`{dict(who='figure', tok='token', card='card')[kind]} {name}`)", "", f"{why}.", "", "```", prompt, "```"] + ([f"_{note}_"] if note else []) + [""])
    h.append("    </ol>")
    md.extend(["## How every prompt is built (for a new one)", "",
               "The wording follows the prompt that made the Chronicle's own portraits, so the game's pictures sit beside them. In this order:", "",
               "1. **The kind of picture first.** " + " · ".join(f"`{v}`" for v in LEAD.values()),
               "2. **The subject, in plain words.** Age, build, face, clothes with their colours, what is in the hands, the pose. Only what a picture can show; one choice, never \"either… or\".",
               f"3. **The look.** `{LOOK}` Where no face is the subject (a card, a place, an animal): `{ART}`",
               f"4. **Kept out.** `{KEEP_OUT}`",
               f"5. **The format.** A figure: `{fig('left')}` A card: `4:3 landscape. Softly blurred background. No text, no border, no frame.` A portrait for the map: `{SOLO.split(KEEP_OUT + ' ')[1]}`",
               "", f"A figure also says `{FACE}` and `{REF}` Foes face left, friends face right. No prompt runs over {LIMIT} words.", ""])
    (GAME / "art" / "PROMPTS.md").write_text("\n".join(md), encoding="utf-8")
    page = GAME / "src" / "campaign.html"
    t = page.read_text(encoding="utf-8")
    a, b = t.index("<!-- prompts:start -->"), t.index("<!-- prompts:end -->")
    page.write_text(t[:a] + "<!-- prompts:start -->\n" + "\n".join(h) + "\n    " + t[b:], encoding="utf-8")
    n = [words(p) for _, p in allp]
    print(f"prompts: {len(done)} made, {len(its)} still to make, in order ({sum(1 for i in its if i[0] == 'who')} figures, {sum(1 for i in its if i[0] == 'tok')} tokens, {sum(1 for i in its if i[0] == 'card')} cards) · longest {max(n)} words, average {sum(n) // len(n)}")

if __name__ == "__main__":
    main()
