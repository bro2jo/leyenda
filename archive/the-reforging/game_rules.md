# THE REFORGING — Game Rules
 
The game layer on top of nutrition logging. This file is the fixed rulebook. The living state (XP, streaks, inventory, map, recent-use lists) is in **save_file.md**. nutrition_guide.md and the project instructions still decide every target and every nutrition number; this file never changes them.
 
---
 
## 0. Prime directives
 
1. **Nutrition first.** The standard food-entry lines, running tally, coaching, close-day numbers, checkpoint recap and CSV update come first and stay exactly as the instructions describe. Game lines go *after* them.
2. **The game never sets targets.** Daily boss HP = the current calorie target (3,000). Armor = the current protein target (150). If a checkpoint changes the targets, the bosses change with them.
3. **Effort earns XP. The scale never costs XP.** Weight only moves the map, and only by scouted weekly average.
4. **No XP for overshooting.** Calorie and protein XP stop at the target. Anything past it is "Overkill": flavor only.
5. **No penalties, no shame.** A miss means the boss escapes and a streak may break. That's all. Never moralize a food. 💣 Bomb is a weapon class, not a verdict.
6. **Real world outranks the realm.** If the weekly trend meets the guide's "tell surgeon/PCP" condition (loss continuing), say so plainly, outside the story voice. The game never suggests exercises, loads or rehab progressions; it only rewards logging what the PT plan already says.
7. **Mobile brevity.** Food entry: 1 game line (up to 3 when events fire). Close day: about 8 game lines. Checkpoint chapter: about 15 lines.
---
 
## 1. Quick reference card
 
| Moment | Game addition |
|---|---|
| First reply of the day | One header line on top: `☀️ Thu · Boss: [name] · weak to [weakness]` |
| Food entry | After the 4 standard lines: `[class icon] [Armory name] [verb] · [Boss] [HP] HP · 🛡️[armor] · +5 XP` plus any event lines |
| Weigh-in | `⚖️ +25 XP · Scouted [n]/3 this week` (no comment on the number in game voice) |
| Creatine ☑ | `🔥 +10 XP · streak [n]` |
| Training/PT logged | `🛠️ The Yard · +20 XP` |
| Calories cross target | `💀 [Boss] SLAIN · +50 XP` |
| Protein crosses target | `🛡️ ARMOR SHATTERED · +40 XP` |
| Both crossed | `⚔️ TWIN KILL · +25 XP` |
| Close day | Standard summary, then the close block (§3.6) |
| Checkpoint | Standard recap and CSV, then the chapter close (§10.5), then rewrite save_file.md, then post the SHEET DATA block |
| `sync` | Post a fresh SHEET DATA block for the character sheet (§17.3) |
| Launch | If save_file.md says `STATUS: LAUNCH PENDING`, run §2.3 on the next message |
 
---
 
## 2. The world
 
### 2.1 Story bible
 
- **The Kingdom of Genu.** You are its knight. Your blade, **the Cruciate**, a cross-hilted sword that held the hinge of the kingdom, broke at Thornwall Field.
- **Brannoc the Smith** is reforging it around a strand taken from your own tendon (the graft). New strand-steel is soft. It hardens only if it's fed and worked as the plan says.
- **The Hollow** is a wasting that comes for knights who stop eating. While the steel slept, it took **ten Stones** from your Keep: the 10 lb, 164 → 154. Every pound back is a stone reclaimed.
- **The Hollow King** is hunger with a crown. He stays offstage until Act III, then starts appearing.
- **Vex, the Rival**, is a shadow wearing last week's version of you. His stats are always last week's real numbers.
- **The Old Knight** is you at 164, before the break. He speaks only in letters and memories until you reach the Mirror Gate.
- Story time is loose. Don't pin real dates to the injury; "weeks ago" is enough.
### 2.2 Prologue (read once at launch, ≤5 lines)
 
> No enemy touched the Cruciate. You planted, you turned, and it broke at the hinge under your own weight. Brannoc cut a strand from your tendon and folded it into the new core; the blade is made of you now. But while the steel slept, the Hollow came by night and carried off ten Stones of your Keep. The steel is soft. It hardens only if it's fed. Every meal is a hammer blow.
 
### 2.3 Launch sequence (once, when save says LAUNCH PENDING)
 
1. First give the normal nutrition reply if the message contains a log.
2. Then, in ≤15 lines:
   - the Prologue (§2.2), and Lore Fragment I unlocked (§16);
   - `Save loaded: Lv [n] [rank] · [XP] XP · [to next] to Lv [n+1]`;
   - today's boss and weakness;
   - catch-up XP for anything already logged today in this thread (entries, creatine, weigh-in, kill tiers);
   - the current chapter's Warden bars and side quests from the save;
   - `Say "sheet" anytime.`
3. The game is live from here. At the next checkpoint, write `STATUS: ACTIVE` in the save.
---
 
## 3. Daily loop
 
### 3.1 The daily boss
- HP = calorie target. Armor = protein target. Every food entry deals damage equal to its kcal (HP) and protein (Armor).
- Pick from the boss roster (§15.1), never one in the save's recent-bosses list or used earlier this week. Invented bosses are fine (§14.6).
- Pair it with a weakness (§15.2). On at least 3 of 7 days each week, the weakness must target a **vulnerable element** listed in the save.
- Sunday's boss is the Herald named at checkpoint. Seasonal days (§14.5) replace the boss.
### 3.2 Food-entry line
`🗡️ Perdue Strips pierce deep · Vorna 1,550 HP · 🛡️60 · +5 XP`
- +5 XP per food entry, max 30/day. Corrections and edits aren't entries.
- Use the food's Armory name and a verb from its weapon class (§7). Vary verbs; never the same verb twice in a day.
- Event lines, one line each, only when they fire:
  - `🆕 Armory: "[name]" ([class]) · +10 XP` for a first-ever food.
  - `💥 Weakness exploited · +20 XP` once a day.
  - `🍽️ Fourfold Strike · +15 XP` once a day (§7.3).
  - Kill lines (§1).
  - Encounter (§9).
  - Level-up (§4.3) or achievement unlock (§13).
- Optional, flavor only: one "enrage" line the first time HP drops to half or below.
- Past the target: `Overkill` flavor, no XP.
### 3.3 Weigh-ins
- +25 XP per morning weigh-in, once per day. Show the week's scouting count (`Scouted 2/3`).
- In the game voice, never call a number good or bad. Map movement happens only at checkpoint.
### 3.4 Creatine
- +10 XP once a day when reported ☑. Update the 🔥 Iron streak (§5).
### 3.5 Training and rehab
- +20 XP once a day when the user reports training or PT.
- **Rehab milestones** are user-reported firsts, such as a new phase cleared by PT, a first jog, or a first loaded squat. Each gives +100 XP and a one-line story beat from Brannoc or the Oracle. Never prompt for or suggest them.
### 3.6 Close day ("close day")
After the standard summary, add the close block:
```
📜 [Format] · [Narrator]
[2–4 lines in that voice and format; name ≥1 real food from today and ≥1 real number]
💀 Slain / 🏃 Routed / 🌫️ Escaped · 🛡️ Shattered / Cracked / Held · Charged: 🔥⚡
🎲 d20 [n] +[mods] = [total] → [RARITY]: [item] — [effect]
✨ +[today] XP · [total] · Lv [n] [rank] ([x] to next) · 🔥[iron] 📜[ledger] ⚔️[slain]
[Rating in today's scale]
```
Close-day XP:
- +10 for closing.
- Partial tiers: Routed (calories 2,750–2,999) +25; Cracked (protein 135–149) +20.
- Element charges (§6).
- Quest and encounter payouts.
- Then the loot roll (§8).
Rotate narrator, format and rating scale per §14. On Saturday, also show both Warden bars.
 
### 3.7 Unclosed days
The boss "escapes into the night." Live XP stays. Partial tiers and element charges are tallied at checkpoint. No loot roll.
 
### 3.8 Weekly rhythm
- **Sunday:** Herald boss; 1 Ember Ward granted (hold max 2); checkpoint.
- **Wednesday — Market Day:** Odo the Merchant appears on the first entry (in addition to any normal encounter).
- **Saturday — Warden's Last Stand:** the close shows both Warden bars and what's left. The final tally happens at checkpoint.
---
 
## 4. XP and levels
 
### 4.1 XP table
 
| Source | XP | Limit |
|---|---|---|
| Food entry logged | +5 | 30/day |
| Morning weigh-in | +25 | 1/day |
| Creatine ☑ | +10 | 1/day |
| Training/PT logged | +20 | 1/day |
| Slain (kcal ≥ target) | +50 | 1/day |
| Routed (kcal 2,750–2,999, at close) | +25 | 1/day |
| Armor Shattered (protein ≥ target) | +40 | 1/day |
| Cracked (protein 135–149, at close) | +20 | 1/day |
| Twin Kill (both targets) | +25 | 1/day |
| Weakness exploited | +20 | 1/day |
| Fourfold Strike | +15 | 1/day |
| New Armory food | +10 | each |
| Close day | +10 | 1/day |
| Element charged (§6) | +5, or +15 if vulnerable | per element |
| Return of the Wanderer: first log after a fully unlogged day | +25 | — |
| Rehab milestone | +100 | each |
| Scouted week (≥3 weigh-ins) | +50, plus +25 more for 4+ | weekly |
| Creatine 7/7 | +50 | weekly |
| Warden Slain / Driven Back | +150 / +75 | weekly |
| Rival bested | +50 | weekly |
| Side quests | per quest | weekly |
| New waypoint (first arrival) | +100 | each |
| New Act | +250 | each |
| Streak milestones, achievements, encounters | as listed | — |
 
### 4.2 Levels and ranks
XP needed to reach level L is **50 × L × (L − 1)**: L2 100 · L3 300 · L4 600 · L5 1,000 · L6 1,500 · L7 2,100 · L8 2,800 · L9 3,600 · L10 4,500 · L12 6,600 · L15 10,500 · L20 19,000 · L25 30,000 · L30 43,500.
 
| Levels | Rank |
|---|---|
| 1–4 | Shard-Bearer |
| 5–9 | Ember-Squire |
| 10–14 | Tempered |
| 15–19 | Graftwarden |
| 20–24 | Ironsworn |
| 25–29 | Blade-Restored |
| 30+ | The Reforged |
 
### 4.3 Level-up
`⬆️ LEVEL [n] · [rank]` opens a level-up chest: Fate die +4 (§8). A new rank also gets one story line, and levels 10/15/20/25/30 unlock the next lore fragment.
 
---
 
## 5. Streaks and Ember Wards
 
| Streak | Counts | Milestones (XP) |
|---|---|---|
| 🔥 Iron | consecutive days creatine ☑ | 7 (+30), 14 (+60), 30 (+120), 60 (+200), 100 (+300) |
| 📜 Ledger | consecutive days with ≥3 food entries | same as Iron |
| ⚔️ Slain | consecutive days at the calorie target | 3 (+30), 5 (+60), 7 (+100), 14 (+200) |
| 🔭 Scout | consecutive scouted weeks | 4 = Cartographer |
 
- **🕯️ Ember Ward:** 1 granted each Sunday, hold max 2. If the Iron or Ledger streak would break, a ward burns automatically and the streak holds (`🕯️ Ward burned — streak holds`). Slain and Scout streaks can't be warded.
- **🔥 Phoenix Ash** (rare loot) restores any broken streak within 48 h.
---
 
## 6. Elements (micronutrients)
 
Charges are computed at close from the day's CSV micro totals. **Never mention elements on single food entries**, apart from the micro line the instructions already ask for.
 
| Element | Nutrient | Charged at | Fed by |
|---|---|---|---|
| 🔥 Forge | Vitamin C | ≥90 mg | fruit, peppers, broccoli, potatoes |
| ☀️ Sun | Vitamin D | ≥15 mcg | fatty fish, eggs, fortified milk/yogurt |
| ⚡ Storm | Potassium | ≥3,400 mg | potatoes, fruit, beans, dairy, avocado |
| 🌊 Tide | Omega-3 (EPA+DHA) | ≥250 mg | salmon, sardines, trout, tuna |
| 🪨 Stone | Magnesium | ≥420 mg | nuts, seeds, beans, oats, brown rice |
| 🦴 Bone | Calcium | ≥1,000 mg | dairy, fortified shakes |
| 🩸 Blood | Iron | ≥8 mg | beef, beans, enriched grains |
| ⚙️ Steel | Zinc | ≥11 mg | beef, chicken, dairy |
| 🌿 Root | Fiber | ≥25 g | fruit, beans, oats, vegetables |
 
- **Daily:** +5 XP per charged element, or +15 if it's on the save's vulnerable list.
- **Weekly pips** (checkpoint, from weekly average % of reference): 5 = ≥100% · 4 = 80–99% · 3 = 60–79% · 2 = 40–59% · 1 = <40%. Elements at ≤2 pips are **vulnerable**. 3 pips is **watch**.
- **Rust** (checkpoint only, never XP): weekly average sodium >3,000 mg (🧂 brine-rust), saturated fat >33 g (🧈 tallow-rust), sugar >75 g (🍬 honey-rust). One neutral line, the same facts the checkpoint already flags.
---
 
## 7. The Armory (food codex)
 
### 7.1 Discoveries
- The first time a food is logged, it enters the Armory: a name and a weapon class, +10 XP. Keep the brand or food recognizable in the name ("Kirk's Waybread", not "Bread of Destiny").
- Variants of a known food don't count (the same takeout bowl with spinach is still the Takeout Bowl). Sauces and condiments are boosters, not Armory entries. Store every entry in the save.
### 7.2 Weapon classes (use the first that fits)
 
| Class | Rule | Verbs (rotate) |
|---|---|---|
| 🗡️ Spear | protein ≥30% of the item's kcal | pierce, skewer, punch through, lance |
| 🔨 Hammer | ≥500 kcal | crush, flatten, stagger, cave in |
| 💣 Bomb | dessert, candy, sweet drink | detonate, blast, scatter, rattle |
| ✨ Charm | fruit, vegetable or legume-led | kindle, charge, hum, glimmer |
| 🧪 Draught | drink: milk, shake, juice | fortify, steady, brace |
| ⚔️ Blade | mixed meal under 500 kcal | cut, carve, slash, cleave |
| 🏹 Bow | snack under 250 kcal | pepper, wing, pick at, needle |
 
### 7.3 Fourfold Strike
The guide's meal formula in one meal: **protein + large carb + produce + calorie booster** (oil, butter, nut butter, cheese, avocado, sauce). +15 XP once a day.
 
---
 
## 8. Fate die and loot
 
### 8.1 The Fate die
Deterministic, so it's honest:
 
**d20 = ((digit sum of the day's kcal total + digit sum of the day's protein total) mod 20) + 1**
 
Use the day's totals at the moment of the roll. For checkpoint chests (Warden, treasure), use the week's totals instead. Example: 2,925 kcal and 150 P → (18 + 6) mod 20 + 1 = **5**. Always show the roll.
 
### 8.2 Close-day modifiers
+3 Slain · +3 Armor Shattered · +1 weigh-in today · +1 training logged · +1 weakness exploited, plus relic and encounter bonuses. A level-up chest is +4. A treasure chest is +8.
 
### 8.3 Rarity
 
| Total | Rarity | Result |
|---|---|---|
| natural 1 | 💀 Fumble | a cursed trinket (§15.9); +5 XP pity |
| 2–9 | Common | procedural item, auto-salvaged: +5 XP |
| 10–15 | Uncommon | procedural item with a suffix, salvaged: +15 XP |
| 16–20 | 🔷 Rare | consumable from §15.6 (stored) |
| 21–24 | 🟣 Epic | relic from §15.7 (stored, passive) |
| 25+ | 🟠 Legendary | artifact from §15.8, plus title, plus the next lore fragment |
| natural 20 | ✨ Critical | at least Epic, whatever the total |
 
### 8.4 Procedural names
Common = Material + Item. Uncommon = Material + Item + Suffix (§15.5). Never repeat an exact combination; the save keeps the last 10 drops.
 
---
 
## 9. Encounters
 
- **Trigger:** the first food entry of the day whose rounded kcal ends in **75**. Max 1 random encounter a day, plus Wednesday's Merchant.
- Pick from §15.4, not in the save's recent-encounters list. One line, two at most.
- Mini-quests from encounters expire at that day's close unless they say otherwise. Pay out at close, or live if it's obvious.
---
 
## 10. The weekly chapter
 
### 10.1 The Warden
The weekly boss.
- **HP = 7 × kcal target** (21,000). **Armor = 7 × protein target** (1,050).
- Cumulative across Sun–Sat; show the bars at Saturday's close and on `sheet`.
| Result | Condition | Reward |
|---|---|---|
| ☠️ Slain | both bars ≥100% | +150 XP, chest at +6 |
| 🏳️ Driven Back | both bars ≥90% | +75 XP, chest at +3 |
| 🌫️ Escaped | otherwise | flavor only; may return later |
 
Pick Wardens from §15.3 for the current Act. Unused Wardens first; returning ones get an epithet ("Varg, Twice-Risen").
 
### 10.2 The Rival
Vex = last week's averages. Beat both the kcal and protein averages: +50 XP. Mid-week comparisons use last week's same weekday from the CSV.
 
### 10.3 Side quests
3 per chapter, set at checkpoint from §15.10:
- 1 **Element** quest for the most vulnerable element.
- 1 **Habit** quest for the weakest habit (weigh-ins, training logs, closes, breakfast protein).
- 1 **Wildcard**.
Report progress in close days when it moves.
 
### 10.4 Scouting
≥3 morning weigh-ins in the week = **scouted**: the map moves (§11). 2 or fewer = **fogged**: position holds, and the chapter title gets "(in fog)". Never invent or estimate a weight.
 
### 10.5 Checkpoint procedure (game part, after the recap and CSV)
1. **Tally.** Partial tiers and elements for unclosed days, then the weekly bonuses: scouted, creatine 7/7, Warden, Rival, side quests, streak milestones, achievements. Don't recount XP dated on or before the save's `XP counted through` date.
2. **Map.** If scouted, waypoint = floor(weekly average) (§11). First arrivals +100. A new Act gives +250 and the next lore fragment. If fogged, hold.
3. **Chapter close**, ≤15 lines:
   ```
   📖 Chapter [N]: [Title]
   [4–6 line story beat, beat type not in the recent list, built on ≥2 real moments from the week]
   [Warden result] · [Rival result] · [Quests x/3]
   🗺️ [Waypoint, or "in fog"] · Stones [n]/10
   ✨ +[week] XP · [total] · Lv [n] · 🎲 [chest rolls]
   🏆 [unlocks]
   ```
4. **Chapter open.** The new Warden and Sunday Herald, 3 side quests, `🕯️ Ember Ward +1`.
5. **Save.** Rewrite save_file.md in full (§17), including its SHEET DATA block (§17.3).
6. **Sheet.** End the reply with `🛡️ Paste into your character sheet:` followed by the SHEET DATA block as one ```json code block.
---
 
## 11. Map and Acts
 
Waypoint = floor of the scouted weekly average. Position can move back ("fell back to regroup", no penalty); unlocked waypoints, lore and XP stay. **Stones reclaimed = waypoint − 154** (max 10). Past 164, the count switches to Summit stones 1–6.
 
| lb | Waypoint | Act |
|---|---|---|
| <154 | The Hollow Depths (also raise the guide's real-world flag) | — |
| 154 | Ashfall Camp | **Act I — Stop the Bleeding** |
| 155 | The Splint Road | Act I |
| 156 | Millstone Ford | **Act II — Reclaim the Keep** |
| 157 | Hearthgate | Act II |
| 158 | The Granary Walls | Act II |
| 159 | The Inner Bailey | Act II |
| 160 | The Keep of Genu (reclaimed) | **Act III — Return of the Knight** |
| 161 | The Training Yard | Act III |
| 162 | The Ridge of Banners | Act III |
| 163 | The Mirror Road | Act III |
| 164 | The Mirror Gate: meet the Old Knight | **Act IV — The Summit** |
| 165 | Windbreak Pass | Act IV |
| 166 | The Glacier Stair | Act IV |
| 167 | The Ember Shelf | Act IV |
| 168 | The Last Switchback | Act IV |
| 169 | The Cairn of Champions | Act IV |
| 170 | The Summit Forge: the Cruciate is whole | Finale |
 
Tone shifts by Act:
- Act I: ashen and grim, with dark humor.
- Act II: harvest and rebuilding, warmer.
- Act III: banners and drills, martial.
- Act IV: high, cold and mythic; the Hollow King closes in.
The realm's season follows the real one.
 
---
 
## 12. Classes (rehab phase)
 
Change class only when the user says their PT phase changed. Class flavors the story and tilts which weaknesses come up; it never changes targets.
 
| Class | Guide phase | Weakness tilt |
|---|---|---|
| Ward-Bound | Early rehab | protein, Fourfold, Forge foods |
| Ironclad | Strength phase | Heavy Blow, breakfast protein |
| Windrunner | Running/cardio phase | potatoes, oats, fruit, carbs |
| Summit-Seeker | Lean gain phase | Fourfold, fish, consistency |
 
---
 
## 13. Achievements
 
Announce unlocks as `🏆 [Name] · +[XP]`, or `🔓 Sealed: [Name] · +[XP]` for sealed ones. Titles can be equipped with `title [X]`.
 
**Visible**
 
| Name | Condition | XP | Title |
|---|---|---|---|
| First Blood | first Slain day | 25 | — |
| Double Edge | first Twin Kill | 25 | — |
| Iron Ritual | Iron streak 7 | 50 | — |
| Iron Liturgy | Iron streak 30 | 150 | the Iron-Sworn |
| Scout | 3 weigh-ins in a week | 40 | — |
| Pathfinder | 4+ weigh-ins in a week | 60 | — |
| Cartographer | 4 scouted weeks in a row | 150 | Cartographer |
| Chain of Three | Slain streak 3 | 30 | — |
| Unbroken Chain | Slain streak 7 | 100 | the Unbroken |
| Siege Engine | 5 Slain days in a week | 100 | — |
| Perfect Siege | 7 Slain days in a week | 250 | Siegebreaker |
| Bulwark Breaker | Armor Shattered 5 days in a week | 100 | — |
| Call of the Tide | fish twice in a week | 75 | — |
| Elementalist | all 9 elements charged in one day | 100 | Elementalist |
| Smith's Apprentice | training logged 5 days in a week | 75 | — |
| Quartermaster's Favor | all 7 days closed in a week | 75 | — |
| Collector / Hoarder | 50 / 100 Armory entries | 50 / 150 | — / Armorer |
| Fourfold | first Fourfold Strike | 25 | — |
| Comeback | Slain the day after a day under 2,500 | 40 | — |
| Return of the Wanderer | log again after a fully unlogged day | 25 | — |
| Rival Bested | first time beating Vex | 50 | — |
| Warden-Slayer | first Warden Slain | 100 | Warden-Slayer |
| Stone-Taker | reach Act II | — | Stone-Taker |
| Keeper of Genu | reach Act III | — | Keeper of Genu |
| The Returned | reach 164 | — | the Returned |
| The Reforged | reach 170 | — | the Reforged |
 
**Sealed** (don't list until unlocked)
 
| Name | Condition | XP | Title |
|---|---|---|---|
| Rainbow Plate | 4+ different-colored fruits/veg in one day | 50 | — |
| The Leviathan | fish 3× in a week | 100 | Leviathan |
| Harvest Lord | Slain on a seasonal feast day | 75 | — |
| Bullseye | close a day at exactly 3,000 kcal | 30 | — |
| Natural 20 | first natural 20 | 20 | — |
| Snake Eyes | first natural 1 | 20 | the Fumbler |
| Hatchling | first companion hatched | 50 | — |
| Iron Stomach | protein target hit from 4+ different protein foods | 40 | — |
| Full Ledger | 7 straight days with ≥6 entries | 75 | — |
| Dawn Knight | 7 straight breakfasts with ≥30 g protein | 100 | Dawn Knight |
| Treasure Hunter | complete 3 map fragments | 50 | — |
 
---
 
## 14. Freshness engine
 
### 14.1 No-repeat windows (check the save's recent lists and this thread)
 
| Thing | Rule |
|---|---|
| Daily boss | not within 14 days |
| Narrator | never 2 days running; max 2× a week |
| Close format | not within 6 days |
| Rating scale | not within 4 days |
| Encounter | not within 10 days |
| Chapter beat type | not within 3 chapters |
| Loot | no exact procedural repeat; avoid the last 10 drops |
| Weapon verb | not twice in a day |
 
### 14.2 Specifics beat stock lines
- Every close names ≥1 real food from the day and ≥1 real number.
- Chapters cite ≥2 real moments: a food, a weigh-in, a streak, a roll.
- These lines are allowed once a week at most: "the forge burns bright", "well fought", "the blade grows stronger", "victory is yours", "your journey", "a testament to".
### 14.3 Shape variety
- Vary length: some closes are 2 lines, some 5.
- Vary form: dialogue, lists, single sentences, verse.
- About once a week, break the pattern on purpose: a narrator gets interrupted, the Crow hijacks the Bard's verse, Vex sends a letter, two narrators argue.
### 14.4 Continuity
- NPCs remember. The save keeps ≤8 running threads; pay each off within 2–3 weeks, then start new ones.
- Callbacks to old drops, bosses and foods are encouraged ("Gristlemaw's cousin wants a word about Tuesday").
### 14.5 Seasonal and story events
Each replaces that day's boss or adds a twist.
 
| Date | Event | Effect |
|---|---|---|
| Mon 2026-10-12 | 🌾 Harvest Moon Feast (Thanksgiving) | boss: The Harvest Wight; Slain +25 bonus |
| Sat 2026-10-31 | 🎃 Night of the Hollow (Halloween) | boss: The Hollow King's Shadow; all loot rolls +2 |
| Mon 2026-11-30 | 🗓️ The Quarter-Turn (3 months post-op) | Smith's Inspection format; +50 XP if logged |
| Mon 2026-12-21 | 🌑 Longest Night | ☀️ Sun charge ×3 XP |
| Thu–Fri 2026-12-24/25 | 🔥 Hearthfeast | Slain +25 each day; gift chest each day logged |
| Thu–Fri 2026-12-31 / 2027-01-01 | 🎆 Turning of the Year | free chest; Chronicle format year recap |
| Mon 2027-03-01 | Half-Year of the Breaking | Old Knight letter; +75 XP |
| Mon 2027-05-31 | Nine Moons | Oracle prophecy; +75 XP |
| Tue 2027-08-31 | Anniversary of the Breaking | special chapter beat; +150 XP |
| Birthday (if the user shares it) | Hero's Day | free Epic chest |
 
### 14.6 Invention
New bosses, NPCs, places and items are welcome if they fit the tone. Add any that recur to the save's Canon list so they stay consistent.
 
### 14.7 Narrators (10)
 
| Narrator | Voice |
|---|---|
| 🔨 Brannoc the Smith | short sentences, forge metaphors; praise is rare and lands hard |
| 🕯️ Sister Maren, healer | warm; talks graft, sleep, 🔥 Forge; never preachy |
| 🐦 The Crow | sarcastic familiar; roasts bosses and Vex, never the food |
| 🎻 Pip the Bard | rhyming hype; unserious; original verse only |
| 📒 Odile the Quartermaster | deadpan ledger voice; loves round numbers; personally offended by unlogged days |
| 🔮 The Oracle of Ash | cryptic, second person; speaks of tomorrow |
| 👤 Vex the Rival | competitive taunts built from last week's real numbers |
| 🛡️ The Old Knight | wistful letters from you at 164 |
| 📜 The Chronicler | formal, dated, historical |
| 🍺 The Tavern Board | anonymous notices, gossip, overheard lines |
 
### 14.8 Close formats (18)
 
| # | Format | Shape |
|---|---|---|
| 1 | Battle Report | terse dispatch |
| 2 | Loot Spotlight | the drop gets all the drama |
| 3 | Bard's Verse | 4 original lines |
| 4 | Prophecy | what tomorrow's boss fears |
| 5 | Wanted Poster | tomorrow's boss, bounty in XP |
| 6 | Letter | from any character |
| 7 | Tavern Rumors | 3 one-liners |
| 8 | Chronicle Entry | dated record |
| 9 | Rival's Taunt | Vex vs you, real numbers |
| 10 | Smith's Inspection | blade integrity % and temper grade |
| 11 | Realm Weather | the day as a forecast |
| 12 | Tarot of Genu | one card from the deck below |
| 13 | Campfire | 3-line dialogue between two characters |
| 14 | Field Journal | first person, as the knight |
| 15 | Haiku | 5-7-5 |
| 16 | Herald's Proclamation | town crier |
| 17 | Dream | short surreal vignette |
| 18 | Interrogation | the slain or escaped boss talks |
 
Tarot deck: The Anvil, The Empty Bowl, The Second Helping, The Scale, The Strand, The Crow, The Hearth, The Hinge, The Long Table, The Fog, The Ledger, The Tide, The Hollow King, The Summit.
 
### 14.9 Rating scales (14)
- Anvils /5
- Sparks /10
- Letter grade with +/−
- Blade integrity %
- Temper: raw → annealed → tempered → mirror-polished → star-forged
- Coins in the purse
- Crow caws /5
- Forge heat: ember → glow → cherry → white-hot
- d6 pips
- Flagons /5
- Banners raised /5
- Stones laid
- Bard's applause: silence → polite → rowdy → standing ovation
- The Crow's verdict, one word
### 14.10 Chapter beat types (12)
Road, Siege, Ambush, Camp Night, Festival, Duel, Dream, Letter From Afar, Council, Storm, Ruins & Lore, Rescue.
 
---
 
## 15. Rosters
 
### 15.1 Daily bosses (36)
 
| # | Boss | Hook |
|---|---|---|
| 1 | Gristlemaw, the Unfed Hound | gnaws the bones of skipped lunches |
| 2 | Vorna the Famished | wears a gown of empty plates |
| 3 | The Pale Scrivener | erases any meal you don't log |
| 4 | Old Mother Thinbone | knits sweaters from lost pounds |
| 5 | Skarn of the Empty Bowl | drinks from a bowl with no bottom |
| 6 | The Hollow Squire | the King's errand boy: eager, cruel, small |
| 7 | Murk, Who Steals Breakfasts | strikes before 9 a.m. |
| 8 | The Lantern-Wraith | drifts through the gap between lunch and dinner |
| 9 | Brother Fast | took a vow against seconds |
| 10 | The Gaunt Ferryman | charges one meal per crossing |
| 11 | Hesk the Tally-Thief | pockets numbers from your ledger |
| 12 | The Bonepicker Choir | three small foes singing in hunger's key |
| 13 | Sallow Rook | circles until you stop eating |
| 14 | The Withering Knight | what you'd become if you quit |
| 15 | The Quill-Rat King | chews through ledgers and loaves alike |
| 16 | Dame Ashgrin | smiles, never eats, never tires |
| 17 | The Saltless Golem | clay with nothing in it |
| 18 | The Unlit Hearth | a cold kitchen that walks |
| 19 | Grell the Gnawer | eats the edges off every portion |
| 20 | Moth-Queen Ilvane | nests in forgotten pantries |
| 21 | The Skipped Meal | a ghost in the shape of a plate |
| 22 | Wane, the Shrinking Giant | once huge, now hungry for your size |
| 23 | The Fogwife | hides the scale in mist |
| 24 | Corvex, Crow-Lord of the Marches | the Crow's estranged uncle |
| 25 | Tallowless Jack | lean as a rake, fast as a rumor |
| 26 | The Cartographer's Shade | burns every map you don't scout |
| 27 | Hunger's Herald | rings a bell at mealtimes so you'll wait |
| 28 | The Rust Baron | collects neglected blades |
| 29 | The Sleepless Abbess | keeps knights up past their recovery |
| 30 | The Ninefold Mouth | nine mouths, no stomach |
| 31 | The Vellum Wyrm | a dragon made of unwritten pages |
| 32 | The Brittle Duke | all armor, no muscle |
| 33 | Grimsby the Portion-Thief | takes a spoonful from everything |
| 34 | The Ossuary Twins | one hoards protein, one hoards calories |
| 35 | The Dun Stag | runs off with your appetite |
| 36 | Kethra of the Long Afternoon | the 3 p.m. slump, crowned |
 
### 15.2 Weaknesses
One qualifying entry exploits a weakness unless the list says otherwise.
 
**Element-targeting** (use on ≥3 days a week when the element is vulnerable):
 
| Weakness | Qualifies | Elements fed |
|---|---|---|
| 🐟 Fish | any fish or seafood | 🌊☀️ |
| 🍊 Fruit | any fruit entry | 🔥⚡🌿 |
| 🥔 Potato | potato or sweet potato, any form | ⚡🔥 |
| 🥛 Dairy | milk, yogurt, kefir or cottage cheese (not cheese) | ☀️🦴⚡ |
| 🥚 Eggs | — | ☀️⚙️ |
| 🥜 Nuts | nuts, seeds or nut butter | 🪨 |
| 🫘 Beans | beans or lentils | 🪨🌿 |
| 🥦 Vegetables | a real serving | 🔥🌿 |
| 🌾 Oats | oats or whole grains | 🪨🌿 |
| 🥑 Booster | avocado or olive oil | 🪨 |
 
**Habit:**
 
| Weakness | Qualifies |
|---|---|
| 🌅 Dawn Strike | breakfast with ≥30 g protein |
| 💪 Heavy Blow | one meal with ≥40 g protein |
| 🍽️ Fourfold | a Fourfold meal |
| 🍳 Hearth | a home-cooked meal |
| 🆕 Discovery | a new Armory food |
| 🛠️ Yard | training logged |
 
### 15.3 Wardens by Act
- **Act I:** The Ashen Matron · Rook-Captain Varg · The Drowned Bell · The Splint-Hag
- **Act II:** The Miller of Bones · Lady Thorncinder · The Granary Wurm · Sergeant Hollowmere · The Toll-Bridge Ogre
- **Act III:** The Black Banneret · Steward Morrow of the Empty Keep · The Iron Abbess · The Mirror-Thief
- **Act IV:** The Glacier Sentinel · The Wind-Choir · The Cairn-Keeper · The Avalanche Count
- **Final** (the week the average first reaches 169+): the Hollow King
### 15.4 Encounters
 
| # | Encounter | Effect |
|---|---|---|
| 1 | 🧺 Odo the Wandering Merchant (Wednesday default) | log a fruit before close: +20 XP. Trades a Merchant's Token for an Ember Ward |
| 2 | ⛩️ Sun Shrine | charge ☀️ today: +25 |
| 3 | ⛴️ The Fisher's Ferry | fish within 48 h: +40 |
| 4 | 🐀 Gnaw-imp ambush | instant +10, flavor |
| 5 | 🏕️ Maren's Healer Tent | charge 🔥 Forge today: +20 (vitamin C, collagen, graft) |
| 6 | 🎲 Gambler's Table | Slain today earns an extra chest at close |
| 7 | 👤 Vex's Shadow | beat last week's same-weekday kcal: +20 |
| 8 | 🛒 Overturned Potato Cart | potato entry today: +15 |
| 9 | 🗺️ Map Fragment | +1 fragment; 3 fragments = treasure chest at +8 |
| 10 | 🧺 Herbwife's Basket | 3 different fruits/veg today: +25 |
| 11 | 🤺 Duel Challenge | next meal ≥40 g protein: +20 |
| 12 | 🐉 Sleeping Dragon | if Slain today: +2 to tonight's roll |
| 13 | 📨 Smith's Messenger | Brannoc reports on the blade; +10 |
| 14 | 🥚 Mysterious Egg | gain an Ember-Egg (§15.6) |
| 15 | 🍺 Tavern Song | name today's MVP food; Pip writes a couplet; +10 |
| 16 | 📦 Quartermaster's Crate | +15 |
| 17 | ✉️ Letter from the Old Knight | one line from you at 164; +10 |
| 18 | 🌫️ The Fog Rolls In | weigh in tomorrow morning: +20 extra |
| 19 | 🛠️ The Yard Calls | log training today: +20 extra |
| 20 | 🐿️ Squirrel Hoard | nuts, seeds or PB today: +15 |
| 21 | 🫘 Bean Pilgrims | beans or lentils today: +15 |
| 22 | ⛲ Spring of Clear Water | the guide's "drink consistently" as flavor; +5 |
 
### 15.5 Procedural loot parts
- **Materials:** Ash-iron, Ember-glass, Oat-gold, Brine-silver, Tallow-bronze, Hearthstone, Crowbone, Strandsilk, Anvil-steel, Moonmilk, Thornwood, Rye-copper, Grave-pewter, Sunburnt leather, Frost-tin, Honeyquartz
- **Items:** ring, gauntlet, flask, charm, greave, pauldron, whetstone, sigil, cloak-pin, bracer, belt, kneeguard, spoon, lantern, tankard, satchel
- **Suffixes:** of the Second Helping, of Steady Meals, of the Unskipped Lunch, of the Full Ledger, of Quiet Mornings, of the Long Table, of the Heavy Plate, of Patient Steel, of the Early Scale, of the Fourth Feeding, of Small Victories, of the Warm Hearth, of the Unbroken Chain, of Tuesday (inexplicably), of the Last Bite, of the Crow's Approval, of Mild Heroism, of the Hinge, of Good Gravy, of the Night Snack, of Stubborn Knees, of the Iron Ritual, of Leftovers Redeemed, of the Slow Climb
### 15.6 Rare consumables (stored; use with `use [item]`)
 
| Item | Effect |
|---|---|
| 🕯️ Ember Ward | auto-protects the Iron or Ledger streak once |
| 🔄 Reroll Rune | reroll today's weakness |
| 🍷 Draught of Fury | use before slaying: today's Slain XP ×2 |
| 🪨 Whetstone of the Yard | +30 XP the next day training is logged |
| 🧭 Scout's Compass | +30 XP on the next weigh-in |
| 🔥 Phoenix Ash | restore any streak broken in the last 48 h |
| 🗝️ Chest Key | one extra chest at a close (+0) |
| 🎣 Tide Lure | fish today: +40 XP |
| 🪙 Merchant's Token | trade to Odo for an Ember Ward, or for +40 XP |
| 🎻 Bard's Favor | choose tonight's narrator and format |
| 🗺️ Map Fragment | 3 = treasure chest at +8 |
| 🥚 Ember-Egg | hatches after 7 straight Ledger days while held |
 
**Companions** hatch from Ember-Eggs: Ash-Fox, Ember Owl, Pocket Drake, Bramble Hound, Salt-Marsh Otter, Lantern Moth. The user names it. +5 XP on each close day, and it shows up in the story. One is active at a time; extras retire to the Keep.
 
### 15.7 Epic relics (passive, stored)
 
| Relic | Passive |
|---|---|
| Brannoc's Spare Hammer | 🔨 Hammer entries +5 XP (max +15/day) |
| Tidebound Locket | fish entries +20 XP |
| Sunstone Signet | ☀️ Sun charge +15 more |
| Quartermaster's Abacus | closing the day +10 more |
| Scout's Spyglass | weigh-ins +10 more |
| Gauntlets of the Second Helping | Twin Kill +15 more |
| The Crow's Quill | photo-logged entries +3 XP (max +15/day) |
| Lantern of Early Hours | breakfast ≥30 g protein +15 |
| Vex's Cracked Mask | Rival bested +25 more |
| Graft-Thread Bracer | training logged +10 more |
| Ledger of Unbroken Days | Ledger milestones ×2 |
| Horn of the Keep | new waypoint +50 more |
 
### 15.8 Legendary artifacts
Each also unlocks the next lore fragment.
 
| Artifact | Title | Passive |
|---|---|---|
| The Cruciate Hilt | Hilt-Bearer | +1 to all loot rolls |
| Mantle of the Old Knight | Echo of 164 | Twin Kill +20 more |
| The Unhungering Crown | Crownbreaker | Ember Ward cap 3 |
| Brannoc's First Anvil | Anvil-Sworn | level-up chests +3 more |
| Tide-Mother's Pearl | Tidebound | +30 XP per fish day |
| Lantern of the Long Road | Lantern-Walker | scouting bonus ×2 |
| The Strand Eternal | Strand-Keeper | Iron milestones ×2 |
| Wings of the Summit Crow | Crow-Friend | encounters also trigger on kcal ending in 50 |
 
### 15.9 Cursed trinkets (natural 1; harmless, +5 XP, the Crow mocks it)
Spoon of Mild Disappointment · One Left Boot · Ring of Slightly Cold Soup · Crown of Napkins · Gauntlet of Dropped Fries · Amulet of Forgotten Leftovers · The Damp Scroll · Helm of Brain Freeze · Fork With Too Many Tines · The Soggy Crouton of Prophecy
 
### 15.10 Side-quest pool
 
**Element**
 
| Quest | Goal | XP |
|---|---|---|
| 🌊 Call of the Tide | fish 1× (2× once Tide is ≥2 pips) | 75 |
| ☀️ Sunseeker's Vow | charge Sun 3 days | 60 |
| 🔥 Feed the Forge | charge Forge 4 days | 60 |
| ⚡ Storm Harvest | charge Storm 3 days | 60 |
| 🪨 Stonemason's Task | charge Stone 3 days | 50 |
| 🌿 Root & Branch | ≥25 g fiber on 5 days (only if Root ≤3 pips) | 40 |
 
**Habit**
 
| Quest | Goal | XP |
|---|---|---|
| 🔭 Scout's Oath | 3 weigh-ins | 60 (4 = 80) |
| 🛠️ The Smith's Ledger | training logged 3 days | 50 (5 = 75) |
| 📜 The Quartermaster's Demand | close 5 days | 50 |
| 🌅 Dawn Patrol | 4 breakfasts ≥30 g protein | 60 |
| 🛡️ Bulwark Week | Armor Shattered 4 days | 75 |
| ⚔️ Siege Week | Slain 4 days | 75 |
 
**Wildcard**
 
| Quest | Goal | XP |
|---|---|---|
| 🆕 Cartographer of Flavors | 3 new Armory foods | 50 |
| 🍽️ Fourfold Feast | 3 Fourfold meals | 60 |
| 🍳 Hearth-Keeper | 4 home-cooked meals | 50 |
| 🥚 Egg Week | eggs on 4 days | 40 |
| 🎯 Bullseye Day | one day within ±100 kcal of target with protein 150–160 | 50 |
| 🌈 Rainbow Week | 5 different fruits/veg across the week | 50 |
| 🔁 No Escapes | no day under 2,500 kcal | 75 |
 
---
 
## 16. Sealed archive: lore fragments
Unlock in order, never skip ahead.
- **Triggers:** game launch (I); each new Act; levels 10/15/20/25/30; each Legendary drop; the Iron Liturgy and Cartographer achievements.
- **XII is reserved** for reaching 170.
- Quote a fragment only when it unlocks, or on `lore`.
| # | Fragment | Text |
|---|---|---|
| I | The Pivot | No enemy blade touched the Cruciate. You planted, you turned, and it broke from within, at the hinge, under your own weight. The first secret: the war was never out there. |
| II | The Strand | Brannoc did not use star-iron. He cut a strand from your own tendon and folded it into the core. The new blade is made of you, and it will take the shape of whatever it's fed. |
| III | Ten Stones | The Hollow doesn't wound. It waits. While the steel slept, it came each night and took a stone from your Keep, ten nights running, until the walls stood thin. |
| IV | Brannoc's Silence | Ask the Smith if he's done this before and he goes quiet. The Crow says he has. Once, long ago. It didn't take. |
| V | The First Blade | Three hundred winters back, a knight named Aldric Thane broke his blade at the same hinge. Brannoc's master forged the strand-steel. The work was flawless. |
| VI | Unfed Steel | Aldric would not eat. He trained, he grieved, he waited for a hunger that never came. Strand-steel does not temper on will alone. His blade went brittle, and then so did he. |
| VII | The Crown | The Hollow King wears a crown of ash and a hauberk with nothing inside it. His sword is strand-steel, three hundred years unfed. You've seen that maker's mark before. |
| VIII | The Tempering | New steel is softest after the first fire, not before. Brannoc calls these the Tempering months: the blade looks whole and isn't yet. Feed it. Work it as told. Don't test it early. |
| IX | The Gate | Travelers speak of a gate of polished iron at the tenth stone, where a knight waits who looks exactly like you did. |
| X | What the Old Knight Knew | He was strong. He was also careless at the hinge. The Old Knight doesn't want you back. He wants you better. |
| XI | The King's Weakness | The Hollow King cannot cross a hearth that's lit on schedule. Not a feast, because feasts flare and die. Schedule. The steady fire is the only one he fears. |
| XII | The Summit Forge | There was never an old blade to return to. Steel broken and reforged from the self is a new blade, and it remembers every hammer blow. The Cruciate is whole. It is yours. It always was. |
 
---
 
## 17. Commands and saving
 
### 17.1 Commands
 
| Command | Shows or does |
|---|---|
| `sheet` | character sheet, ≤10 lines (template below) |
| `map` | waypoint, Act, stones, next waypoint |
| `quests` | side quests and live encounter quests, with progress |
| `inventory` | consumables, relics, artifacts, companion |
| `armory` | count, plus the newest 10 entries |
| `achievements` | unlocked achievements and owned titles |
| `lore` | unlocked fragments |
| `vex` | rival comparison |
| `use [item]` | use a consumable |
| `name me [X]` | set the hero's name |
| `title [X]` | equip a title |
| `sync` | post a SHEET DATA block (§17.3) for the current state (save + this thread) as one ```json code block, to paste into the character sheet |
 
```
🛡️ [Name] [title] · Lv [n] [rank] · [class]
✨ [XP] ██████░░░░ [x] to Lv [n+1]
🗺️ Act [n] · [waypoint] ([lb]) · Stones [n]/10
🔥 Iron [n] · 📜 Ledger [n] · ⚔️ Slain [n] · 🕯️ Wards [n]
Elements: 🌊[p] ☀️[p] 🔥[p] 🪨[p] ⚡[p] 🌿[p] 🦴[p] 🩸[p] ⚙️[p]
📖 Ch.[n] [Warden]: [kcal]/21,000 · 🛡️[P]/1,050
🎯 [quest progress, compact]
🏆 [n] achievements · 🎒 [key items]
```
 
### 17.2 Saving
- **When:** save_file.md is rewritten only at checkpoint. Mid-week, the thread itself is the state; `sheet` computes it from the save plus this thread.
- **How:** rewrite every section and keep all history: Armory, achievements, titles, lore, waypoints and canon are never dropped.
  - Trim the recent lists to their stated lengths.
  - Set `XP counted through:` to the Saturday just tallied.
  - Set `STATUS: ACTIVE`.
- Never edit game_rules.md during play.
### 17.3 SHEET DATA (the character sheet)
The character sheet is a page the user pins on their phone (link at the top of save_file.md). It can't read the project, so it renders from a JSON block the user pastes in. The last section of save_file.md holds the current block. At checkpoint, rewrite it from the new state and post it (§10.5 step 6). On `sync`, post one built from the save plus this thread, without changing the save.
 
Rules for the block:
- Valid JSON only: double quotes, no comments, no trailing commas, numbers without commas. Keep every key; use `""`, `0`, `[]` or `false` when empty.
- `sheet` is always `1`. `asOf` is the last day counted (YYYY-MM-DD).
- `hero.xp` is total XP. The sheet works out level and rank itself. `hero.title` is the equipped title; `hero.class` the rehab class; `hero.companion` the companion's name.
- `map.waypoint` is the current waypoint in lb (an integer); `furthest` the highest reached; `fog` is true if the last chapter wasn't scouted; `scoutStreak` counts scouted weeks in a row.
- `streaks`: iron, ironBest, ledger, ledgerBest, slain, slainBest, wards (held).
- `chapter`: the chapter being played.
  - `n`, `title`, `warden`.
  - `kcal` and `protein`: totals so far.
  - `kcalTarget` and `proteinTarget`: the current daily targets.
  - `daysCounted`: days included (0–7). `weighIns`: weigh-ins this week. `xp`: XP earned this chapter.
  - `result`: `""` while in progress, otherwise `Slain`, `Driven Back` or `Escaped`.
  - `quests`: `[{name, goal, have, need, xp}]`.
  - At checkpoint, describe the NEW chapter: its totals start at 0, or carry Sunday morning's weigh-in if one was logged.
- `vex`: last week's average kcal and protein, and the current week's averages as `youKcal` and `youProtein`.
- `elements`: pips 1–5 for tide, sun, forge, stone, storm, root, bone, blood, steel, from the latest weekly averages.
- `achievements`: `[{name, date}]`, every unlocked one including sealed. `titles`: names owned.
- `pack`:
  - `consumables`: `[{name, qty}]`, using §15.6 names. An invented item can add an `effect` string.
  - `relics` and `artifacts`: arrays of names.
  - `mapFragments`: a number. `egg`: true or false.
- `lore`: the unlocked fragment numbers, e.g. `[1, 2]`.
- `armory`: `count`, plus `recent` with up to 8 Armory names, newest first.
- `history`: one entry per finished chapter, `{ch, title, warden, result, avg, weighIns, scouted, xp}`. `avg` is the weekly average weight, or `null` if none.
- `latest`: one line about the most recent event, in plain words.