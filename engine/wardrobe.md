# The Wardrobe

`engine/wardrobe.json` holds every piece Darrow's looks can be made of, what opens each, what goes with what, the sets, the Collection's ranks and the image prompt. The site shows it on two pages: **the Wardrobe** (`darrow/wardrobe.html`: the lookbook, the Forge, the prompt) and **the Collection** (`darrow/collection.html`: his rank, the sets, a shelf per category). Finished looks live in `saga/state/looks.json`, their pictures in `saga/art/looks/` (`saga/art/README.md` → looks).

## A piece

Each category (`categories[]`: `id`, `label`, `options`) lists its pieces. A piece:

| Field | What it is |
|---|---|
| `id` | unique in its category; a look names it as `category=id` |
| `name` | what the picker shows: generic, nothing the page has not shown (no faction's colours or crest) |
| `prompt` | the words the image prompt uses; the picker also shows it as what the piece looks like |
| `unlock` | the conditions that open it, all of which must hold; none: open from the start |
| `group` | its heading in the tray, when the category has `groups` (the poses) |
| `quote` | a line from the scene its `page` or `tether` unlock names, word for word (the build checks it) |
| `reference` | its own reference picture: `{label, image (under saga/art/), file, use}`, like Ash; the Forge numbers it as the next Image while the piece is chosen |
| `hidden: true` | off the site entirely until it can be worn; only counted |

A category may also carry `chips: true` (a short list: a row of chips instead of a tray of cards) and `groups: [{id, label}]` (every piece then needs a `group`). `steps` sets the Forge's order (who is in the picture first); each step offers only the pieces that go with the steps before it.

## What opens a piece

| `unlock` | Opens when | Decided by |
|---|---|---|
| `{"level": N}` | he reaches level N | the engine (`darrow.py sync`) |
| `{"art": id, "rank": R}` | that Art reaches rank R (a sealed Art never) | the engine |
| `{"knot": N}` | Knot N is tied | the engine |
| `{"tether": N}` | the Tether's stage N is paid on the page (reached, and its scene written) | the site (`world.json → tether`) |
| `{"page": "NN:key"}` | that scene is on the page: a chapter's code and scene key (`"04:5"`, `"04:between-9"`) or a tale piece (`"tale01:p1"`) | the site |

The engine writes what the sheet opens to `saga/state/darrow.json → wardrobe`: each piece with the chapter it opened in (the week its last condition came true; `0` is the Prologue; null when the day is not known). `sync` names newly opened pieces. The site adds the scene's chapter for `page` and `tether`. A piece opened this chapter or the one before is **New**: the same on every device, marked on its card and named at the head of the Now page.

**Poses follow the Knots**, so a look never shows the leg doing what the story has not let it: a pose that stands, walks or moves names the Knot that allows it (`engine/rules.json → knots`), or the scene that showed it.

## What goes with what

The build's `wardrobe_clash` (in `engine/build_site.py`) decides; the Forge offers only what fits, and the build refuses a filed look that breaks a rule.

| Field | On | Rule |
|---|---|---|
| `with` | any piece | `"alone"`, or a companion's id from `side`: the piece is only for that picture |
| `free_hands` | a pose | 0–2 (default 2), against a held piece's `hands` |
| `hands` | a held piece | 0–2 (default 1); what is worn, like a sword at the belt, takes none |
| `fight` | a pose | only with a held piece that has `weapon` |
| `weapon` | a held piece | it is a weapon |
| `tender` | a pose | no face with a `mood` |
| `mood` | an expression | `fierce`, or `battle` (only in a fight pose) |
| `needs` | any piece | `{category: piece}`: only with that piece, and choosing it brings it; it must rule out at least what the needed piece rules out, and a shown piece never needs a hidden one |

## Sets and the Collection

`sets: [{id, name, about, pieces: ["category.piece", …]}]` are pieces that belong together across categories, shown on the Collection with a seal once all are open. A set never names a hidden piece, since it would give away the secret. A new batch of pieces can bring its own set.

**The Collection's ranks** (`collection.ranks: [{at, name}]`, from `at: 0` upward; `complete`: the title for every piece open). His rank is the highest whose `at` the count of pieces he can wear has reached; hidden pieces count once they open. The thresholds follow the story's length. At Chapter 5, about 47 pieces were open. With about 500 XP a chapter, the Knots on the rehab timeline and the story adding a piece every other chapter, that puts 50 near Chapter 6, 60 near 10, 70 near 14, 80 near 18, 90 near 24 and 105 near the story's end: a rank roughly every four to eight chapters, wider apart as it goes. New pieces raise the count; move a threshold only forward.

## The prompt and the references

`prompt` is written for OpenAI's image generation and joined line by line. The Forge fills `{references}` (Image 1, Image 2… in the order they are attached: `references`, then the chosen pieces' own), `{design}` (one line per category, from each piece's `prompt`), `{details}` (the small touches) and `{screen}` (the background: chroma blue #0000FF, or chroma green #00FF00 when the design names anything blue, so the screen never eats the look). On a phone, Share sends the prompt and the reference pictures to ChatGPT together; the Look line comes back with the finished picture, and `python3 engine/looks.py add` files it: it keys out the screen and checks the pieces.

## Adding a piece

1. Add it to its category with `id`, `name`, `prompt` and `unlock`. A pose also gets a `group` and, if it stands or moves, the Knot that allows it. A piece the page showed gets `"unlock": {"page": "NN:key"}` and, when one line shows it, a `quote` from that scene.
2. Give it the fit fields it needs (`with`, `free_hands`, `hands`, `fight`, `weapon`, `tender`, `mood`, `needs`).
3. Put it in a set if it belongs to one; adjust nothing else.
4. Run `python3 engine/darrow.py ship -m "Wardrobe: …"`; `sync` dates it and the build checks every rule above.

Never remove or rename a piece a filed look wears: the build fails on a look that names a missing piece.
