# Swim Plan — learning to swim, to comfortable in deep water · from Sunday 29 November 2026 → summer 2027

*This repo's own plan for the pool, built on his notes of Fri 11/27 (`real/plan/learn_to_swim_notes.md`, kept as written). Sections 1–11 are written by hand and change when the plan changes. The last section is printed from the ladder (`real/swim.json`) on every `sync`: where he stands, the next pool session, and every milestone with its drills. **Nothing here outranks the PT on the knee (§6) or an instructor on a drill.** The drills and estimates are general adult learn-to-swim practice: the lowest source, never a dose from the clinic.*

## 1. The goal and the start

- **The goal, in his notes' words:** to go into summer 2027 able to jump into a pool, keep his hands away from his nose, come back to the surface calmly and stay afloat without touching the bottom. Then, with an instructor, a headfirst dive.
- **Where he starts:** he can put his whole head under water. He holds his nose to do it. Deep water frightens him. He has not floated or swum unaided.
- **The shape of it:** one pool visit a week of 45 to 60 minutes with a buddy who can swim and a lifeguard on duty, and a short home routine three times a week. It starts **Sunday 11/29** (his call, 11/28). Twenty milestones in four stages; his targets for each stage are in §3.

## 2. How the plan moves

**The milestones are the program.** There is no calendar in it: his monthly targets are targets, never deadlines.

- Each milestone has **what it needs first**. When those are done it is **ready**, and the next pool session is built from what is ready (`python3 engine/darrow.py swim next`, or the last section of this page). Check one off and the session changes by itself: a block whose milestones are all done shrinks to a two-minute keep, and the time goes to what is still open.
- A milestone done early, or out of order, is simply done. One that takes six visits takes six visits: its drills and its *if stuck* line are there for that.
- **In a visit:** one new thing per block. Stay on a drill until it is boring, then take the next. Finish each block on a good one. If something spikes his heart rate, go back one drill, do that well once, and leave the block there for the day.
- **Recording:** a milestone is recorded the day it happens, with what was seen (how many, how long, how far, how deep) and who watched. `darrow.py swim` shows the ladder.
- **Every fourth visit is a review** (his notes' week 5): no new drills; repeat what was learned, find the block that still makes him nervous and give it the spare time. If two reviews in a row show no milestone moved, the answer is a lesson (§8), not more of the same.

## 3. The road, stage by stage

The default order, with his own targets. The session that is actually due is always the printed one at the bottom; this table is the map.

| Visits (default) | His target | The work | Milestones in reach |
|---|---|---|---|
| 1 | December, week 1 | going under with the hands down; a slow leak of air through the nose; goggles on, eyes open; ears in the water with a hand under the head | Submerge without pinching · Exhale through the nose · Ears underwater |
| 2 | week 2 | coming up slowly and breathing in, not out; the supported back float; standing up out of a float | Resurface calmly · Float with assistance · Recover to standing |
| 3 | week 3 | less and less support; the front float and the glide; sculling with the hands, standing | Float independently (begun) |
| 4 | week 4 | the push-off float; glides with a kick; treading with the feet up for 5 to 10 seconds; the roll, holding the wall | Float independently |
| 5 | week 5 | review visit: the weakest block twice; re-try every open milestone | Stage 1 finished |
| 6–9 | January | the roll alone; swimming on the back, then the front with a roll for air; treading to 30 seconds; the first deep-water rungs, on the wall | Roll front to back · Swim 10 yards · Tread 30 seconds |
| 10–13 | February | a length by swim, float, swim; a minute afloat; letting go of the wall in deep water | Swim 25 yards · Afloat 1 minute |
| 14–18 | March | two minutes afloat; leaving the wall and coming back; the slide-in entry | Afloat 2 minutes · Feet-first entry |
| 19–22 | April | deep-water swims that feel calm; the step in; the five parts of the competency sequence, then all at once | Deep water with confidence · Water competency |
| 23–26 | May | jumps with the hum; up, breathe, look, swim | Jump without holding the nose · Resurface and swim to the wall |
| 27–39 | June to August | the dive, taught; visits with no drills at all | Headfirst dive · Enjoy deep water |

**Two changes from his notes, and why.** Standing up out of a float comes *before* floating alone, not after: knowing he can get his feet under him is what makes letting go safe. And the first swimming is on the back, with a roll onto the back for air when on the front: it gets him to a continuous length honestly, and leaves the front crawl's side breathing (the hardest skill in swimming) for later, when nothing depends on it.

## 4. The pool visit

- **The frame** (his notes' session): warm-up 5 · underwater breathing 10 · floating, recovery and rolling 15 · treading 10 · swimming 15 · deep water 10 once it opens · cool-down 5. Early visits run short because the later blocks are not open yet; that is by design, and spare minutes go to the block he likes least.
- **In and out by the steps or the ladder.** Standing-depth water for everything until the deep-water block opens. Breaks whenever he wants them.
- **Where it sits in the week.** The week runs on high days (a clinic day or the home knee session) and low days, with Sunday as rest. The pool goes on a **low day or on Sunday, never on a high day**, and he names the day. It then joins the weekly template as the session `swim`: `today` shows it open until it is logged, the checkpoint counts it, and a closed pool or a moved visit is a plan change, never a miss.
- **A second, shorter visit** in a week is allowed and helps more than a longer single one: frequency is what moves fear and floating. It is never owed.
- **The first three visits are a new load for the knee:** the morning after each one gets the usual check, and a morning with more swelling than usual means the next visit drops the frog kick, the eggbeater and the push-offs, and the PT hears about it.

## 5. The home routine

**Three times a week** (his call, 11/28; his notes said five), handled like the morning check: `today` lists it under *Still open* until the week (Sunday to Saturday) has its three, and a fourth is fine and pays nothing more. It is his notes' routine made to follow the ladder like the pool session does: **the drills of the milestones that are ready** (a drill several of them share is done once; up to three), then picturing a calm float and a calm resurfacing for two minutes. The day before a pool visit, read the session. The routine for now: `python3 engine/darrow.py swim home`, or §12 below. **The video is off for now** (his call, 11/27).

- **Stage 1 at home is one drill in the bath: the calm float and the sink.** Lie back into a float with the ears under, a few slow breaths, then hum and let the whole face go under, a count longer each round. It trains going under without the hands, the slow nose exhale, coming up calm, ears in the water and the feel of the float at once, and it trains them face up, where water runs into the nose most easily. It is his own change of the notes' "reserve full submersion for the pool" (11/27): he is already at ease face under in the tub. No bath that day: the shower, face into the spray, humming.
- Then the floor and the bed carry stage 2's shapes (the way up, the float's balance, the roll, the kick); stage 3 is sculling and breathing pace; stage 4 is picturing it.
- On a short day, the first drill is the routine.
- Logged as one row a day (`session=home`, `skill=breath`). It is practice, not a test: milestones are judged in the pool.
- **Every second under is a breath out.** Nothing in this plan holds the breath, and the bath rounds stop the moment the air runs low, never after; light-headed means done for the day. His dry breath holds stay dry (§7).

## 6. The knee

**The PT's word (relayed Fri 11/27; `pt_notes.md`, 2026-11-27): "anything in water is okay."** Recorded in the engine (`real/swim.json → cleared`), so a visit and a milestone pay from that day. That clears water walking, floating, every kick (the flutter, the bicycle, the frog or whip kick, the eggbeater), push-offs and deep-water entries. What stays is the plan's own care, not a limit from the clinic:

- **The deck is the real risk to the graft:** wet tile, a slip, a twist. Sandals with grip to the water's edge, walking, the steps or the ladder in and out.
- **Kicks:** start with the flutter and the slow bicycle, which move the knee in a straight line. The frog kick and the eggbeater twist it most: learn them small and slow once the rest is easy, and a morning with more swelling than usual drops them first.
- **No jumping or stepping into water he can stand in:** that is a landing on the pool's floor, outside "in water". Deep-water entries have no landing; the push-off from the deck is smaller than the clinic's 12" box jumps.
- **Kneeling on the deck** (climbing out without the ladder, the kneeling dive): on the left to comfort and never pushed (PT 16); lead with the right.
- **The first three visits are a new load:** the morning after each gets the usual check.

## 7. Safety

- **Never alone.** A lifeguard on duty and a buddy who knows what he is working on, every visit. Deep water only supervised, until the water competency milestone is done.
- **No breath-holding in the water, ever, and no deep fast breathing before going under.** Holding the breath after over-breathing can cause a blackout under water with no warning, in strong swimmers too. His breath-hold work belongs on land and stays there.
- **Diving only in a marked diving area, only with the instructor.** Never the shallow end, a lake, a river or a pool he does not know.
- **When it goes wrong in the water:** roll onto the back, breathe, then decide. That is why the roll and the back float come before distance.
- Cold, cramp, a racing heart that will not settle, or a knee that complains: the visit is over, and that is a good visit.

## 8. Lessons

His notes ask for at least three private lessons, and this plan ties each to the ladder:

1. **In the first two visits: floating.** Being held in a float by someone who knows how is the fastest way through stage 1 and the first half of stage 2. A buddy can learn the hold by watching once.
2. **When treading reaches 30 seconds, before leaving the wall in deep water:** treading and the deep-water rungs. This is where fear stalls people, and an instructor in the water beside him changes it.
3. **The dive.** Required: the milestone is not done without one.

A group adult learn-to-swim course (the Red Cross's, a Y's, a Masters club's) covers the same ground with the supervision built in, and its lessons count as pool visits.

## 9. Is it feasible

**Yes, with honest margins.** These are planning estimates and nothing depends on them.

- Adults without much fear usually reach a float, a glide and a short swim in standing depth within 8 to 12 half-hour lessons. A fearful start takes longer, and it follows calm hours in the water far more than weeks on a calendar.
- By stage: stage 1 in about 2 to 5 visits (he already goes under) · stage 2 in 6 to 12 more (floating alone and the full length are where lean adults stall: lean legs sink, and that is no fault) · treading and two minutes afloat in 4 to 8 · deep-water confidence in 4 to 10, the widest range because it is fear, not skill · entries in 2 to 5 · the dive in 1 to 3 lessons.
- That is roughly 19 to 43 visits against his 26 by June and 39 by August: his timeline sits inside the range, toward its quicker half. **What moves it:** visits per week (two short beat one long), the first lesson early, and never skipping the home breathing. **What slips it:** long gaps, and pushing the deep-water rungs before they are boring.
- If the timeline slips, the order does not change and nothing is lost: a milestone waits for him.

## 10. Logging and the week

- **A pool visit:** one row per block worked (`darrow.py swim add`: `session=pool`, `skill` breath / float / roll / stroke / tread / deep, the drill, the minutes, anything counted in `metric` and `value`); the warm-up and cool-down may be one row with no skill.
- **The home routine:** one row (`session=home`, `skill=breath`); what to do is `swim home`.
- **A milestone:** `darrow.py swim pass <id> --evidence "…" --witness "…"`, the day it happens.
- **Today and the week:** `today` and `week` carry a Swim line (milestones, what is ready, the week's visit and home days). Once the pool has a day, it is a planned session like any other.
- **The Sunday checkpoint** has a Swim section: the visit against the plan, the home days, each milestone done with what was seen, what stalled, the next visit's focus, and the knee's morning after the pool. "Next week" places the pool day.

## 11. Still to confirm

- Which pool, its depths, and where 10 and 25 yards fall in it. · Who the buddy is, and whether they have held a float before. · The pool day. · Goggles; earplugs or a nose clip if wanted; deck sandals. · The first lesson, booked.

## 12. Where he stands, the next session and the ladder

<!-- engine:start -->
_Printed from `real/swim.json` by `sync` · as of Sat 2026-11-28 · never edited by hand_

### Where you stand

- **0 of 20 milestones.** The PT's word on the pool: 2026-11-27: His PT: anything in water is okay (relayed 11/27; pt_notes.md 2026-11-27): every kick, push-offs, deep-water entries
- Stage 1, Underwater confidence: 0/4 · his target: December (a target, never a deadline)
- Stage 2, Floating and swimming: 0/6 · his target: January to February (a target, never a deadline)
- Stage 3, Deep-water readiness: 0/5 · his target: March to April (a target, never a deadline)
- Stage 4, My ultimate goal: 0/5 · his target: April to August (a target, never a deadline)

### The next pool session

Next pool session · 45 to 60 minutes, once a week, with a buddy who can swim and a lifeguard on duty
1. Warm-up · 5 min: In by the steps or the ladder. Water walking forward, backward and sideways in chest-deep water, shoulders under; three slow breaths out with your mouth at the surface.
2. Underwater breathing · 10 min · work toward: Submerge my head without pinching my nose
   - Judged: head fully under in standing-depth water with both hands off the nose, three times in one visit.
   - Work 1. Bubbles at the surface: chin in the water, hum through your nose so the water in front of your face ripples. 5 slow breaths out. From here on your hands stay on the wall or on your thighs, never near your face.
   - Work 2. Nose in: start the hum, lower until the water covers your nose, come up. 5 times. The hum is what keeps the water out, so it starts before you go under and stops after you are up.
   - Work 3. Eyes in, goggles on: hum, lower until the goggles are under, look at your own hands for a slow count of 3, come up. 5 times.
   - Work 4. All the way: hum, sink until the top of your head is wet, count 3, stand. Three in a row with your hands on your thighs is the milestone.
   - If stuck: Water up the nose means the breath out stopped or the chin tipped back: tuck the chin a little, hum louder, and come up before the air runs out, never after. A nose clip for a visit or two is a fair bridge for every other block; take it off for this one.
   Also ready in this block: Exhale gently through my nose underwater (`swim show nose_exhale`)
3. Floating, recovery and rolling · 15 min · work toward: Feel comfortable with my ears underwater
   - Judged: ears under for about 30 seconds while breathing normally (a supported back float counts), and his own word that it felt fine.
   - Work 1. Standing, holding the wall: lean one ear into the water, then the other, then tip your head back until both are under. Listen to how quiet it is. 5 slow breaths.
   - Work 2. The cradle: your buddy stands behind you with a hand under the back of your head. Lean back until your ears are under, eyes on the ceiling, feet still on the bottom. 3 times, 10 seconds each.
   - Work 3. The same with the hand between your shoulder blades and your feet off the bottom. Work up to 30 seconds of ordinary breathing.
   - If stuck: If the feeling of water in your ears is the whole problem, wear earplugs and move on. A tight neck means you are holding your head up: let the water take its weight.
   Also ready in this block: Float on my back with assistance (`swim show float_assisted`)
4. Treading water · not yet: it opens after Recover from floating to standing
5. Swimming · not yet: it opens after Recover from floating to standing; Exhale gently through my nose underwater
6. Deep water · not yet: it opens after Float or tread water for 1 minute
7. Cool-down · 5 min: An easy back float or water walking. Say one thing that felt better than last week. Out by the steps.
About 35 minutes. Spare minutes go to the block that makes you most nervous.
Milestones you could check off this visit: Submerge my head without pinching my nose; Exhale gently through my nose underwater; Feel comfortable with my ears underwater; Float on my back with assistance.
Stop on a good one. A milestone is recorded the day it happens: tell me what you saw (how many, how long, how far) and who watched.

### The home routine now

Home routine · about 8 minutes, 3 times a week · log it as one row (`session=home`, `skill=breath`)
1. The calm float and the sink (bath), 6 min (toward: Submerge my head without pinching my nose; Exhale gently through my nose underwater; Feel comfortable with my ears underwater; Float on my back with assistance): Lie back in a full tub until your ears are under and the water takes the weight of your head: arms loose, hands resting on your belly, eyes on the ceiling. Take three slow breaths there, in fully so you feel your chest lift, then half out so you feel yourself settle. That is the float. Then start the hum and let your head sink until your nose and your whole face are under. Count 3, come up slowly, let the water run off, and only then breathe in. 6 to 8 rounds, a count longer each round, toward 6. Face up is where water runs into the nose most easily, which is why the hum starts before your nose goes under and keeps going until it is out. Every second under is a breath out, never a hold: stop the round the moment the air runs low, and stop for the day if you feel light-headed. No bath that day: the shower, face straight into the spray with your hands down, humming, for 3 minutes.
2. Picture it, 2 min: a calm float and a calm resurfacing, as clearly as you can.
The day before a pool visit, read the session (`swim next`).

### The ladder: every milestone and the drills that lead to it

#### Stage 1 — Underwater confidence

**[ ] Submerge my head without pinching my nose** · `no_pinch` · ready
- Judged: head fully under in standing-depth water with both hands off the nose, three times in one visit.
- Work 1. Bubbles at the surface: chin in the water, hum through your nose so the water in front of your face ripples. 5 slow breaths out. From here on your hands stay on the wall or on your thighs, never near your face.
- Work 2. Nose in: start the hum, lower until the water covers your nose, come up. 5 times. The hum is what keeps the water out, so it starts before you go under and stops after you are up.
- Work 3. Eyes in, goggles on: hum, lower until the goggles are under, look at your own hands for a slow count of 3, come up. 5 times.
- Work 4. All the way: hum, sink until the top of your head is wet, count 3, stand. Three in a row with your hands on your thighs is the milestone.
- If stuck: Water up the nose means the breath out stopped or the chin tipped back: tuck the chin a little, hum louder, and come up before the air runs out, never after. A nose clip for a visit or two is a fair bridge for every other block; take it off for this one.
- At home: The calm float and the sink (bath) (below)

**[ ] Exhale gently through my nose underwater** · `nose_exhale` · ready
- Judged: a slow, steady stream of bubbles through the nose for about five seconds, three times in one visit (no forceful humming).
- Work 1. The slow leak: face in, let the air out through the nose as thin as you can make it. Count how many seconds the stream lasts. 5 tries; aim for 5 seconds.
- Work 2. One long 'mmmm' under water on one breath. If the bubbles come out in a burst, you pushed: start again, quieter.
- Work 3. Bobs: under with bubbles, up for one easy breath in through the mouth, straight back under. 5 in a row, then 10. This rhythm is the one that will look after you in deep water.
- If stuck: Running out of air in two seconds means you are blowing, not leaking. Add one second to the stream each visit. The shower is where this gets easy: the same hum with the spray on your face.
- At home: The calm float and the sink (bath) (below)

**[ ] Resurface calmly** · `calm_surface` · after: Submerge my head without pinching my nose
- Judged: up from a full submersion with no gasp, no grab for the wall and no rush to wipe the face, three times in one visit.
- Work 1. Come up slowly: rise until your mouth is clear, let the water run off, and only then breathe in. Hands stay down: no wiping, no reaching.
- Work 2. Finish the breath out as your mouth clears the surface, so that the first thing you do in the air is breathe in.
- Work 3. Say one calm word out loud after each one before you do anything else. Three in a row is the milestone.
- If stuck: Coming up with a gasp means you stayed down too long: cut the time under to a count of 2 and build back up. Coming up calm matters more than staying down long.
- At home: The calm float and the sink (bath) (below)

**[ ] Feel comfortable with my ears underwater** · `ears_under` · ready
- Judged: ears under for about 30 seconds while breathing normally (a supported back float counts), and his own word that it felt fine.
- Work 1. Standing, holding the wall: lean one ear into the water, then the other, then tip your head back until both are under. Listen to how quiet it is. 5 slow breaths.
- Work 2. The cradle: your buddy stands behind you with a hand under the back of your head. Lean back until your ears are under, eyes on the ceiling, feet still on the bottom. 3 times, 10 seconds each.
- Work 3. The same with the hand between your shoulder blades and your feet off the bottom. Work up to 30 seconds of ordinary breathing.
- If stuck: If the feeling of water in your ears is the whole problem, wear earplugs and move on. A tight neck means you are holding your head up: let the water take its weight.
- At home: The calm float and the sink (bath) (below)


#### Stage 2 — Floating and swimming

**[ ] Float on my back with assistance** · `float_assisted` · ready
- Judged: a back float held about 15 seconds with a hand under the shoulders, ears in the water.
- Work 1. From the cradle (ears in, a hand under your head), have your buddy slide the hand down to between your shoulder blades. Arms out wide, palms up, chin a little up.
- Work 2. Breathe low and slow. A full breath lifts you; let half of it out, feel yourself settle, fill again. 15 seconds with the hand there is the milestone.
- Work 3. Then the hand becomes two fingers, then hovers under you without touching. Ask not to be told when it lets go.
- If stuck: Legs that drop are normal for lean, muscular legs: let them hang, or add a small slow kick from the hips. A float with the legs low and the face dry is a float. With no buddy that day, a noodle under your knees or a kickboard hugged to your chest stands in.
- At home: The calm float and the sink (bath) (below)

**[ ] Recover from floating to standing** · `float_to_stand` · after: Submerge my head without pinching my nose
- Judged: from a back float and from a front float, feet back under him and standing with no help, three times each.
- Work 1. From the back: tuck your knees toward your chest, drop your chin, and scoop both hands forward as if pulling a chair under you. Your feet swing down; stand. 5 with your buddy's hand there, then 5 without.
- Work 2. From the front (holding the wall or your buddy's hands, face in, legs floating): pull your knees under you, press down with both hands, lift your head last. Stand. 5 times.
- Work 3. Then let go: a front float from standing (arms forward, face in, count 3) and stand up out of it by yourself. Three each way is the milestone.
- If stuck: Lifting the head first is what makes the feet miss the floor: knees in first, head last. Do it in water no deeper than your ribs until it is automatic. This is the skill that makes every float safe, so it comes before floating alone.
- Knee: Both feet go down together and softly.
- At home: The way up from a float (floor) (below)

**[ ] Float independently** · `float_alone` · after: Float on my back with assistance; Recover from floating to standing
- Judged: a back float held about 15 seconds with no one touching him; a small kick or scull to keep the legs up counts (lean legs sink).
- Work 1. Push-off float: crouch with your shoulders under and your back to the open water, lean back until your ears are in, and let your feet come up by themselves. Count 5, stand. Add 2 seconds a try.
- Work 2. Find your balance: arms stretched back past your head moves weight that way and lifts the legs; arms at your sides drops them. Try both, keep what works.
- Work 3. The working float: a slow flutter kick from the hips and small sculling circles with your hands by your sides, only enough to keep your legs near the surface. 15 seconds untouched is the milestone.
- Work 4. The front float too: face in, arms forward, legs long, 5 to 10 seconds, stand.
- If stuck: Stiff is what sinks. Before each try, one long breath out through the nose with your face in, shoulders dropped. If the fear is of not being held, have your buddy stand an arm's length away with hands in the water, not on you.
- Knee: Kick small and from the hips.
- At home: The float's balance (floor) (below)

**[ ] Roll from front to back** · `roll_over` · after: Float independently; Resurface calmly
- Judged: from a front float or glide, roll onto the back and breathe without touching the bottom, three times, unassisted.
- Work 1. On the wall: hold the gutter with one hand, float face down, and turn your whole body like a log toward the open side until you are looking at the ceiling. Keep hold. 5 each way.
- Work 2. With hands: your buddy holds your hips lightly while you front float with bubbles for a count of 3, then roll: one shoulder drops, the head turns with the body, the chin comes up last. Two breaths on your back. 5 times.
- Work 3. Alone: a front glide off the wall, bubbles for 3, roll, breathe, float, stand. Three in a row without touching is the milestone.
- Work 4. Back to front as well, so you can go under, look where you are going, and come back up for air.
- If stuck: Lifting your head to breathe before the roll finishes sinks you: the head stays in line and the eyes follow the shoulder. Slow is fine, with bubbles all the way round.
- At home: The roll (bed or carpet) (below)

**[ ] Swim 10 yards continuously** · `swim_10` · after: Recover from floating to standing; Exhale gently through my nose underwater
- Judged: 10 yards by any stroke without touching the bottom or the wall, in standing-depth water.
- Work 1. Glides first: push off the wall on your front, arms long, face in, bubbles, and see how far one push carries you. Stand. Then the same on your back. 4 each.
- Work 2. Add the kick: the same glides with a small quick flutter kick from the hips, legs long, toes pointed, knees soft. On the back first, where you can breathe, then the front.
- Work 3. The back is the easy road. On your back, kicking, add a slow double-arm pull: hands slide up your sides to your armpits, reach out, sweep down to your thighs, glide. Most adults make 10 yards this way within a few visits.
- Work 4. On the front: glide, kick, and reach with big slow pulls. When you want air, roll to your back, take two breaths, and roll back or stay there. That counts.
- Work 5. Measure it: ask the lifeguard where 10 yards is (usually a little past the first flags).
- If stuck: Leave the front crawl's side breathing for later: it is the hardest thing in swimming and this milestone does not need it. Tiring in 5 yards means kicking from the knees or holding your breath: longer legs, steady bubbles.
- Knee: Any kick (PT, 11/27: anything in water is okay). Start with the flutter: it is the easiest to learn and moves the knee in a straight line. Push off the wall gently, with both feet.
- At home: Arms and kick (standing, then the bed) (below)

**[ ] Swim 25 yards continuously** · `swim_25` · after: Swim 10 yards continuously; Roll from front to back
- Judged: one 25-yard length by any stroke without touching the bottom or the wall.
- Work 1. Build by landmarks: 10 yards, then to the far flags, then the wall. One longer try a visit, after two or three easy ones.
- Work 2. Swim, float, swim: on your front for as long as it is comfortable, roll to your back and rest there with a gentle kick, roll back. A length done this way counts, and it is the pattern that gets a tired swimmer home.
- Work 3. Slow down: three kicks to each arm pull, and a glide. A length that takes a minute is a better length than one that takes 30 seconds and leaves you gasping.
- Work 4. Swim in the lane beside the wall, in water you can stand in the whole way if the pool has it.
- If stuck: A stall around 15 yards is breath, not strength: make the first half deliberately lazy. If lifting your head sinks your legs, do the whole length on your back.
- Knee: Any kick; easy push-offs.
- At home: The kick with the breathing (bed) (below)


#### Stage 3 — Deep-water readiness

**[ ] Tread water for 30 seconds** · `tread_30` · after: Recover from floating to standing
- Judged: head above the surface for 30 seconds with nothing touching the bottom or the wall (in standing depth with the feet up, or deep and supervised).
- Work 1. Hands first, standing with your shoulders under: sculling. Palms down, sweep both hands out and in as if smoothing sand, thumbs tilted down on the way out and up on the way in. You should feel the water push up on your palms. 3 rounds of 20 seconds.
- Work 2. Legs second, holding the wall or a noodle: a slow bicycle, or a small flutter kick straight below you, body upright.
- Work 3. Together, feet off the floor: in chest-deep water, scull and kick with your knees drawn up so your feet clear the bottom. 5 seconds, stand. Then 10, 15, 20, 30.
- Work 4. Slow and wide beats fast and small: head tipped back a little, mouth just clear, lungs full.
- If stuck: Sinking to the eyebrows means you are trying to hold too much of yourself out of the water: only your face needs to be dry. If the legs will not carry it yet, tread with a noodle under your arms and take it away a visit later.
- Knee: The kick is the knee's question. Any kick is cleared (PT, 11/27), but start with the slow bicycle and the flutter. The eggbeater and the frog kick twist the knee most: learn them small and slow once the rest is easy, and a morning with more swelling than usual drops them first.
- At home: Sculling and the slow bicycle (below)

**[ ] Float or tread water for 1 minute** · `afloat_60` · after: Tread water for 30 seconds
- Judged: one minute afloat by floating, treading or both, nothing touching.
- Work 1. Mix it: 20 seconds treading, roll onto your back and float for 20, come back up and tread for 20. Changing over is the skill.
- Work 2. Add 10 seconds a visit to whichever part is easier, and hold the other where it is.
- Work 3. Do it once fresh and once near the end of the session, when you are a little tired.
- If stuck: If the treading runs out first, let the back float carry most of the minute. This one is about staying up by any calm means.
- At home: The pace of staying up (below)

**[ ] Float or tread water for 2 minutes** · `afloat_120` · after: Float or tread water for 1 minute
- Judged: two minutes afloat by floating, treading or both, nothing touching.
- Work 1. Two minutes is pacing. Start slower than you think you need to and breathe in a pattern: in for 2, out for 4.
- Work 2. Give yourself jobs while you are up there: turn a full circle, find the nearest exit, hold one hand out of the water for 5 seconds, say the alphabet.
- Work 3. Once it is easy in standing depth, do it within arm's reach of the wall where the water is over your head, supervised.
- If stuck: A stall around 90 seconds is usually tight shoulders: drop them, widen the scull, and lean back onto the water a little.
- At home: The pace of staying up (below)

**[ ] Pass a supervised water competency assessment** · `competency` · after: Swim 25 yards continuously; Float or tread water for 1 minute; Perform a supervised feet-first deep-water entry
- Judged: the Red Cross sequence in one go, supervised: into water over his head and back to the surface, float or tread for one minute, turn a full circle and find the exit, swim 25 yards to it, and get out without the ladder.
- Work 1. Rehearse the five parts one at a time in the deep end, beside the wall: step in where it is over your head and come back up; float or tread for a minute; turn one full circle and point at your exit; swim 25 yards to it; get out without the ladder.
- Work 2. Getting out without the ladder: both hands flat on the deck, bob down once and use the rise to press up to straight arms, turn and sit. It is an arm exercise.
- Work 3. Chain them two at a time (the entry and the minute; the minute, the circle and the swim), then all five. Ask a lifeguard or an instructor to watch the whole sequence: many pools run it as their swim test.
- If stuck: The part that fails is nearly always the minute afloat straight after the entry, because the entry spends your calm. Take three slow breaths on your back before you start counting.
- Knee: The step in is a feet-first entry into deep water, so there is no landing. The climb out can put a knee on the deck: kneeling on the left is allowed to comfort and not pushed (PT 16), so lead with the right, or use the ladder until it is comfortable and finish that part later.
- At home: The sequence, rehearsed (below)

**[ ] Swim in deep water with confidence** · `deep_confident` · after: Float independently; Resurface calmly
- Judged: two visits in a row swimming in water over his head, supervised, each of which he rates calm (4 or 5 of 5).
- Work 1. Rung 1, the wall: hand over hand along the gutter from the shallow end to the deep end and back, shoulders under. Stop over the deep water and look down through your goggles. Twice.
- Work 2. Rung 2, under and up: holding the gutter with both hands in the deep end, 5 bobs: arms straight, under with bubbles, pull up, breathe.
- Work 3. Rung 3, letting go: one hand off, then both, for a count of 1, then 2, then 5, sculling and kicking. The wall stays within reach.
- Work 4. Rung 4, floating it: back to the wall, lean back into a float with your head toward the middle of the lane, count 10, roll, and take two strokes back to the wall.
- Work 5. Rung 5, leaving and coming back (once you can swim 10 yards): push gently off the wall, glide a body length out, turn round, swim back. Then two lengths out.
- Work 6. Rung 6, along the wall (once you can stay afloat a minute): swim the deep half of a length in the lane beside the wall, your buddy walking the deck beside you.
- Work 7. Rung 7, across the line: swim from where you can stand to where you cannot, and on to the far wall. Then start from the deep end. Two visits in a row of this, each rated calm, is the milestone.
- If stuck: Stay on a rung for as many visits as it takes to be bored there: boredom is the signal to move up. If a rung sends your heart racing, drop back one, do that one well once, and end the block there. This block is never done without a lifeguard on duty and someone on the deck who knows what you are working on.
- At home: The next deep-water rung, pictured (below)


#### Stage 4 — My ultimate goal

**[ ] Perform a supervised feet-first deep-water entry** · `feet_first` · after: Float or tread water for 1 minute
- Judged: a step or a jump in, feet first, where the water is over his head, supervised.
- Work 1. Slide in: sit on the edge at the deep end, hands on the deck beside you, turn and lower yourself in holding the wall. Then the same, letting go as you go under and coming back up to the wall.
- Work 2. From sitting: lean forward and push off with your hands so you drop in feet first a foot from the wall, bubbles through the nose all the way down and up. Turn, take the wall.
- Work 3. The step: stand at the edge with your toes over it, look at the far wall and not down, take one big step out and bring your feet together. Press your arms down through the water as you go under to stop the drop. Up, breathe, three breaths on your back, swim to the wall. One supervised step or jump is the milestone.
- If stuck: If the drop is the fear, stay with the seated entry until it is dull. If the fear is of not coming up, do 5 deep-end bobs on the wall first: the water pushes you up every single time.
- Knee: Deep water only, so the feet touch nothing. Never jump or step into water you can stand in: that is a landing on a hard floor, outside the PT's "in water". The push-off from the deck is a small jump, smaller than the clinic's box jumps.
- At home: The step in, pictured (below)

**[ ] Jump into deep water without holding my nose** · `jump_no_pinch` · after: Perform a supervised feet-first deep-water entry; Exhale gently through my nose underwater
- Judged: a jump into deep water with both hands away from the face.
- Work 1. Start the hum before you leave the deck. The breath out through the nose begins in the air and does not stop until your face is back in the air.
- Work 2. Give your hands a job: arms out to the sides, or each hand holding the opposite elbow across your chest.
- Work 3. Steps in first, then a small two-foot jump out from the edge. Three good ones a visit is plenty.
- If stuck: Water up the nose on the way in means the hum stopped or the chin lifted: chin level, eyes on the far wall, a louder hum. A nose clip is no failure, but this milestone is done without one.
- Knee: A small two-foot push-off from the deck into deep water only.
- At home: The hum before the face goes in (shower) (below)

**[ ] Resurface and swim to the wall calmly** · `surface_to_wall` · after: Perform a supervised feet-first deep-water entry
- Judged: after a jump: up, a breath, and an unhurried swim to the wall, three times in one visit.
- Work 1. Say the routine before you go: up, breathe, look, swim. Come up, take one full breath (on your back if you like), find the wall with your eyes, and swim to it at your slow-length pace.
- Work 2. Go in further out each time: a foot from the wall, then a body length, then from the corner so that the swim back is 5 or 10 yards.
- Work 3. Three in one visit, each unhurried, is the milestone.
- If stuck: If you race for the wall, add a rule: 5 seconds of treading or back floating after every entry before you are allowed to swim.
- At home: Up, breathe, look, swim (below)

**[ ] Perform a safe headfirst dive with an instructor** · `dive` · after: Pass a supervised water competency assessment; Resurface and swim to the wall calmly
- Judged: a headfirst entry taught and watched by an instructor, in a designated diving area.
- Work 1. This one is taught, so book the lesson. It happens only in a marked diving area (the Red Cross asks for at least 9 feet of water for a dive from the deck) and nowhere else: never the shallow end, a lake, a river or a hotel pool.
- Work 2. The usual ladder, each rung with the instructor: a sitting dive from the edge (arms locked over your ears, hands together, roll forward); a kneeling dive; a compact dive from a crouch; a standing dive.
- Work 3. Your arms stay locked over your head until you have surfaced: the hands meet the water, not the head, and they steer you up.
- If stuck: A belly flop means the head came up: chin to chest, eyes on your knees as you roll in. Stay with the sitting dive until it is clean. Nobody needs the standing dive on a schedule.
- Knee: The kneeling dive puts a knee on the deck: use a mat and kneel on the right, or skip that rung with the instructor's agreement.
- At home: The sitting dive, pictured (below)

**[ ] Enjoy deep-water swimming** · `enjoy_deep` · after: Swim in deep water with confidence
- Judged: his own word, after a visit in deep water he stayed in because he wanted to.
- Work 1. One visit with no drills: get in at the deep end, float, swim where you like, get out when you want.
- Work 2. Notice what you choose to do when nothing is assigned. That is what the pool is for from now on.
- If stuck: If it still feels like a test, it is not this milestone's day yet. Nothing about it can be forced.

#### The home drills

- **The calm float and the sink (bath)**, 6 min: Lie back in a full tub until your ears are under and the water takes the weight of your head: arms loose, hands resting on your belly, eyes on the ceiling. Take three slow breaths there, in fully so you feel your chest lift, then half out so you feel yourself settle. That is the float. Then start the hum and let your head sink until your nose and your whole face are under. Count 3, come up slowly, let the water run off, and only then breathe in. 6 to 8 rounds, a count longer each round, toward 6. Face up is where water runs into the nose most easily, which is why the hum starts before your nose goes under and keeps going until it is out. Every second under is a breath out, never a hold: stop the round the moment the air runs low, and stop for the day if you feel light-headed. No bath that day: the shower, face straight into the spray with your hands down, humming, for 3 minutes.
- **The way up from a float (floor)**, 2 min: On your back on the floor or the bed: knees to your chest, chin down, both hands scoop forward, roll up to sitting. 5 slow ones. Then face down: knees under you, hands press, head up last. 5 more.
- **The float's balance (floor)**, 2 min: Lie in the float shape (arms wide, palms up, chin a little up, neck loose). Sweep your arms overhead and back to your sides and feel where your weight goes; finish with small sculling circles of the hands by your hips. In the bath, the same shape after the float rounds.
- **The roll (bed or carpet)**, 2 min: Log rolls from your front to your back, head kept in line with your shoulders, eyes following the shoulder, chin up last. 5 each way.
- **Arms and kick (standing, then the bed)**, 3 min: Standing, the back stroke's arms 10 slow times (hands up your sides to the armpits, out wide, sweep down to your thighs, pause). Then face down on the bed with your legs off the edge from the hips, a small flutter kick from the hip with soft knees, 3 × 20 seconds.
- **The kick with the breathing (bed)**, 3 min: Face down on the bed, the same small kick, 3 × 30 seconds, with the breathing you will use in the pool: hum out for a few kicks, turn your head, breathe in.
- **Sculling and the slow bicycle**, 3 min: Standing, palms down, thumbs tilting down on the way out and up on the way in: 3 × 30 seconds. Then on your back on the floor, a slow bicycle with the legs, 3 × 20 seconds.
- **The pace of staying up**, 2 min: Sitting still, by the clock: in for 2, out for 4. This is the pace that makes a minute afloat easy. Once a minute afloat is done, finish by picturing two minutes in the deep end: the circle, the exit, the wall.
- **The sequence, rehearsed**, 3 min: Picture the five parts in order, as clearly as you can, twice: in, up, a minute afloat, the circle and the exit, the swim, out. Then 10 slow push-ups with your hands on the edge of a counter: getting out without the ladder is an arm press.
- **The next deep-water rung, pictured**, 2 min: Picture the next rung of the deep-water ladder (`swim show deep_confident`) from start to finish, calm, twice.
- **The step in, pictured**, 2 min: Picture the step in, twice: toes over the edge, eyes on the far wall, the hum starting, the step, the arms pressing down, coming up, three breaths on your back.
- **The hum before the face goes in (shower)**, 2 min: Start the hum before your face goes into the spray and keep it going until you are out of it, with your hands crossed on your chest.
- **Up, breathe, look, swim**, 1 min: Before bed, say the routine out loud (up, breathe, look, swim) and picture it three times.
- **The sitting dive, pictured**, 2 min: Picture the sitting dive the instructor taught: arms locked over your ears, hands together, the roll forward, the hands steering you up.
<!-- engine:end -->
