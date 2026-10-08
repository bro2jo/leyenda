# Style Guide — how the Chronicle is written

The test for every page: **a stranger who has never heard of ACL rehab, calories or this repo should read it and want the next chapter.** If a sentence only makes sense to someone who knows the real logs, cut it.

---

## 1. The wall between the Ledger and the Chronicle

The real world drives the story's **outcomes**; it never appears in the story's **content**.

**Never in the prose:** foods, meals-as-metric, calories, protein, macros, supplements, weigh-ins, body weight, exercise names (squat, bridge, step-down, bike, bench), sets, reps, loads, RPE, PT, physio, ACL, graft, surgery, rehab, phases, dates or numbers from the real logs, anything that winks at the reader ("Darrow felt like he'd skipped breakfast").

**Characters can still eat, sleep and train** like people in any novel. A camp meal, a feast, a soldier's drill all belong to the world. What's forbidden is mirroring: no scene exists *because* of a food log, and no in-world meal or drill corresponds to a real one.

**How real effort shows up instead:**

| Real side (Ledger) | Story side (Chronicle): show it like this |
|---|---|
| Fuel / Ember (nutrition) | warmth vs. cold in Darrow's body; color in his face; how fast cuts close; whether he lasts through a long scene; how loud the Grace-dreams are when Ember is low |
| Floor minimum, morning checks | quiet discipline: the dawn vigil, the Mender's forms, Warden's Eye; Darrow catching his own lies |
| Knee sessions | Maelis working the Binding: "the forms," slow and exacting, never named as exercises; the leg answering, or not |
| PT visit | the Reading of the Knots (Maelis's weekly examination) |
| Upper-body work | the Seated Blade with Hollis; grip, shoulders, a sword that feels lighter |
| Conditioning | the Long Breath; the Steps; wind on the ridge; endurance in a fight |
| Sport-skill work | the Arts tied to them (see `mechanics.md`) |
| A strong week | the chapter's climax goes his way; allies arrive; the plan works |
| A thin week | the climax is costly; the enemy advances; a plan fails. **This is a plot turn, never a punishment and never a lecture.** |
| A red-light/rest day (plan says stop) | the story cuts away to another thread (Wren, Vane, the House), or Darrow is made to rest by others. Resting is never failure. |
| A missed day | the world moves without him. No guilt. |

Numbers that are *game* numbers (Level, Might 11, Ember "Steady", DC 13, a d20) may appear, but only inside Reckoning boxes and dice lines, never in narration.

---

## 2. Voice and craft

- **POV:** close third person on Darrow, past tense. At most one short **interlude** per chapter from another POV (Wren, Vane, Maelis, Marrant, the king's hall), set off with `* * *`.
- **Register:** grounded and specific. Concrete nouns, working verbs. Soldiers' humor. Earned emotion. Think *The First Law* dialogue, *Chalion* interiority, *Baldur's Gate 3* companions.
- **Every scene:** someone wants something, something stops them, something turns. End on movement: a decision, a door, a line of dialogue, a new problem. Never end on a summary.
- **Dialogue does the heavy lifting.** Use each character's voice line (`characters.md`). Let people interrupt, deflect, lie.
- **The body is real.** Darrow's knee is a presence: stiffness at dawn, the hot ache after the forms, the terror of a stair going down, the moment it holds. Write it the way a wounded soldier would feel it, never the way a clinic would describe it.
- **Plant and pay off.** Before writing, read `saga/state/threads.md`. Every chapter should touch at least one open thread and plant at most one new one.
- **Variety:** rotate scene types: dialogue-driven, action, investigation, quiet/character, set piece. No two consecutive scenes of the same type.

**Banned (or once a Book at most):** "a testament to", "little did he know", "in that moment", "a dance of", "the weight of the world", "he let out a breath he didn't know he was holding", "something shifted", "steeled himself", eyes that "sparkle", any sentence that tells the reader what to feel. No moralizing narrator. No "lesson" paragraphs.

---

## 3. Formats

### A daily scene (written when a day is closed)
- **150–400 words**, one scene. Heading: `### Scene N — Title`. Appended to the current chapter file.
- Tone and outcome are coloured by that day's deeds (see the table above), but the plot moves forward every day regardless.
- Reckoning notifications, if the engine reported any, go at the end of the scene in a box.

### The Reckoning box (LitRPG notifications)
Rare in prose, always at a scene's end, never more than 6 lines:
```
> ⟦ THE RECKONING ⟧
> Art learned: **Iron Grip** I. *No one takes your blade from your hand.*
> Might 11 → 12
> Level 5 · Kindled
```
The first Reckoning (end of Chapter 1) is the only time it's described in prose: pale, angular script of light that only Darrow sees, which reads the same with his eyes closed.

### Dice (Baldur's Gate style)
Show the check on its own line, before the outcome is narrated:
```
`[MIGHT · DC 13]` d20 **14** +2 = **16** — *Success*
```
- Rolls come only from `python3 engine/darrow.py roll` and are written exactly as returned. **No invented rolls. No rerolls** except by spending Inspiration (`--reroll`).
- Use rolls for moments with real stakes: 1–2 per daily scene at most (often zero), 2–4 in a chapter climax.
- A failure is never a dead end. It's a complication, a cost, a different road.
- DCs: easy 8 · moderate 11 · hard 14 · very hard 17 · near impossible 20.

### The weekly climax (written at the Sunday checkpoint)
- **900–1,800 words**: the chapter's battle, confrontation or revelation. Close the chapter with the week's tier (Triumph / Hard-won / Costly / Setback) setting the shape of the outcome, and the dice deciding the details.
- End with **a choice for Darrow** (2–3 options), in this format:
```
**What does Darrow do?**
1. **Expose Anselm to the Mother Prior.** *(Maelis approves.)*
2. **Use him to feed Marrant a lie.** *[Resolve 10]* *(Wren approves; risky.)*
3. **Say nothing — yet.**
```
  Gated options show the requirement in brackets; if Darrow doesn't meet it, show it struck through: ~~[Finesse 14] Leap the gap~~.

### Chapter epigraphs
Each chapter opens with 1–3 lines from an in-world document, in italics, with a source line: *Wren's ledgers*, a Warden precept, a Confessor's writ, a lancers' marching song, a letter from Aldric Vane, a children's counting rhyme. Original text only.

### File layout
- `saga/chronicle/NN-slug.md`, one file per chapter. Front matter line: `# Chapter N — Title`, then the epigraph, then scenes in order, then `## Climax — Title`, then the choice.
- Book openings get a title page line: `# BOOK II — THE TEMPERING ROAD`.

---

## 4. Copyright and originality
All names, songs, verse and lore are original. Never quote or imitate real song lyrics or poems. Never borrow named characters, places or spells from existing games or books.
