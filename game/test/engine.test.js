/* Rules tests for src/engine.js: named rule checks, a fuzzer with invariants, and bots for balance. */
const LH = require('../src/engine.js').LH;
const C = LH.C, T = LH.T;
let pass = 0, fail = 0;
function ok(cond, name) { if (cond) pass++; else { fail++; console.log('  FAIL: ' + name); } }
function eq(a, b, name) { ok(JSON.stringify(a) === JSON.stringify(b), name + ' (got ' + JSON.stringify(a) + ', want ' + JSON.stringify(b) + ')'); }
const U = (G, id) => LH.byId(G, id);
function place(G, id, x, y) { const u = U(G, id); u.x = x; u.y = y; return u; }
function fresh(seed, rounds) { return LH.newRun({ seed: seed || 7, rounds: rounds || 1 }); }
function battle(n, seed, rounds) { const G = fresh(seed, rounds); G.run.n = n; G.run.hp = 58; reStart(G); return G; }
function reStart(G) { // start the battle G.run.n names, through the public door
  G.run.n--; G.over = { win: 1 }; G.camp = { market: [], bought: [] }; G.clash = null; const hp = G.u[0].hp; G.u[0].hp = 58 - T.rest; LH.nextBattle(G); }
/* a clash with a chosen hand and plenty of breath, for testing single cards */
function rig(G, aid, did, hand, opts) {
  opts = opts || {}; const a = U(G, aid), d = U(G, did);
  const K = LH.engage(G, a, d); if (!K) throw new Error('rig: cannot engage ' + aid + '->' + did);
  if (hand) K.hand = hand.slice(); if (opts.en !== undefined) K.en = opts.en; if (opts.fb !== undefined) K.fb = opts.fb;
  return K;
}
function isolate(G, keep) { G.u.forEach(u => { if (keep.indexOf(u.id) < 0) { if (u.boss) { u.x = 5; u.y = 0; } else u.hp = 0; } }); }
function duel(aid, did, o) { o = o || {}; const G = o.G || fresh(o.seed, o.rounds); isolate(G, [aid, did].concat(o.keep || [])); place(G, aid, 2, 4); const d = place(G, did, 2, o.far ? 6 : 5); if (o.hp) d.hp = d.max = o.hp; return G; }
const done = G => { LH.endHand(G); LH.closeClash(G); };

console.log('1. every card does what its text says');
Object.keys(C).forEach(id => {
  const c = C[id], G = duel('D', 'S', { seed: 3, hp: 99 }), S = U(G, 'S'), D = U(G, 'D'); D.hp = 30; D.moved = true; D.dk.disc.push('wound');
  const K = rig(G, 'D', 'S', [id, 'strike', 'strike', 'strike'], { en: 9, fb: 0 }); K.open = false; K.canBreak = false;
  const b = { hp: S.hp, block: K.block, en: K.en, dhp: D.hp, hand: K.hand.length, sp: G.run.spoils, w: LH.wounds(D) };
  if (c.dead) { ok(LH.playable(G, 0) !== '' && LH.play(G, 0) === null, id + ' cannot be played'); ok(LH.cardText(id).length > 0, id + ' has text'); return; }
  const fx = LH.play(G, 0);
  ok(!!fx, id + ' plays');
  if (c.dmg) eq(b.hp - S.hp, c.dmg * (c.hits || 1), id + ' damage');
  if (c.blk) eq(K.block - b.block, c.blk, id + ' block');
  if (c.heal) eq(D.hp - b.dhp, c.heal, id + ' heal');
  eq(K.en, b.en - c.c + (c.en || 0), id + ' breath');
  if (c.draw) eq(K.hand.length, b.hand - 1 + c.draw, id + ' draw');
  if (c.spoil) eq(G.run.spoils - b.sp, c.spoil, id + ' spoils');
  if (c.cleanse) eq(LH.wounds(D), b.w - 1, id + ' sets a Wound aside');
  if (c.stance) eq(D.st[c.stance], c.sv, id + ' sets its stance');
  ['open', 'pin', 'push'].forEach(f => { if (c[f]) ok(K[f] === true, id + ' ' + f); });
  if (c.halve) ok(K.halved === true, id + ' halves'); if (c.mark) ok(S.marked === true, id + ' marks'); if (c.again) ok(K.again === true, id + ' moves again');
  const inGone = D.dk.gone.indexOf(id) >= 0, inDisc = D.dk.disc.indexOf(id) >= 0;
  ok(c.lent ? (!inGone && !inDisc) : c.ex ? inGone : (inDisc || id === 'strike'), id + ' goes to the right pile');
  ok(D.dk.disc.concat(D.dk.gone, D.dk.draw).every(x => !C[x].lent), id + ' leaves no lent card in a pile');
  ok(LH.cardText(id).length > 0 && LH.cardText(id, K).length > 0, id + ' has text');
  ok(fx.every(f => typeof f.k === 'string'), id + ' reports what happened');
});

console.log('2. damage: Open, block, Tough, many blows, leftovers');
{ const G = duel('D', 'S', { hp: 99 }); U(G, 'D').moved = true; const S = U(G, 'S');
  const K = rig(G, 'D', 'S', ['strike', 'strike', 'over', 'seated'], { en: 9, fb: 6 }); K.canBreak = false; K.open = true;
  let fx = LH.play(G, 0); eq([fx[0].n, fx[0].blocked, fx[0].crit], [5, 6, true], 'Open strike: round(7 x 1.5) = 11, 6 blocked, 5 through'); ok(K.open === false, 'Open is used up by one hit');
  K.fb = 6; fx = LH.play(G, 1); eq([fx[0].n, fx[0].blocked, K.fb], [6, 0, 6], 'Overwall goes over his block and leaves it'); }
{ const G = duel('D', 'S', { hp: 99 }); const K = rig(G, 'D', 'S', ['seated'], { en: 9, fb: 0 }); K.canBreak = false; U(G, 'D').moved = false; LH.play(G, 0); eq(99 - U(G, 'S').hp, 10, 'Seated Blade deals 10 if he stood his ground'); }
{ const G = duel('D', 'S', { hp: 99 }); const K = rig(G, 'D', 'S', ['twice', 'twice'], { en: 9, fb: 0 }); K.canBreak = false; K.open = true;
  const fx = LH.play(G, 0); eq(fx.filter(f => f.k === 'dmg').map(f => f.n), [8, 5], 'Second Cut into an Open foe: 8, then 5'); ok(LH.cardText('twice', K).indexOf('twice') > 0, 'and its text reads as two blows'); }
{ const G = battle(2); isolate(G, ['D', 'B']); place(G, 'D', 2, 4); const B = place(G, 'B', 2, 5); B.hp = B.max = 99; U(G, 'D').moved = true;
  const K = rig(G, 'D', 'B', ['twice', 'strike', 'over', 'hand'], { en: 9, fb: 0 }); K.canBreak = false; K.open = false;
  LH.play(G, 0); eq(99 - B.hp, 6, 'Tough 2: Second Cut lands 3 and 3'); LH.play(G, 0); eq(99 - B.hp, 11, 'Tough 2: Strike lands 5'); K.fb = 5; LH.play(G, 0); eq(99 - B.hp, 15, 'Overwall goes over block but not Tough: 4');
  ok(LH.cardText('hand', K).indexOf('<em>2</em>') >= 0, 'and a card shows the number it will really deal'); }
{ const G = duel('D', 'S', { hp: 99 }); const D = U(G, 'D'); D.st.atkUp = 2; D.moved = true; const K = rig(G, 'D', 'S', ['twice', 'strike'], { en: 9, fb: 0 }); K.canBreak = false; LH.play(G, 0); LH.play(G, 0); eq(99 - U(G, 'S').hp, 7 + 7 + 9, 'Blood Up adds 2 to every blow'); }
{ const G = duel('D', 'S', { hp: 40 }); const S = U(G, 'S'); const K = rig(G, 'D', 'S', ['finish', 'finish'], { en: 9, fb: 0 }); K.canBreak = false; LH.play(G, 0); eq(40 - S.hp, 6, 'Finish It deals 6 to a healthy foe'); S.hp = 20; LH.play(G, 0); eq(S.hp, 6, 'and 14 at half health'); }
{ const G = duel('D', 'S', { keep: ['P'] }); const S = U(G, 'S'), P = place(G, 'P', 3, 5); S.hp = 4; P.hp = 9; const sp = G.run.spoils;
  const K = rig(G, 'D', 'S', ['follow'], { en: 9, fb: 0 }); const fx = LH.play(G, 0); const cr = fx.filter(f => f.k === 'carry')[0];
  ok(S.hp === 0 && cr && cr.id === 'P' && cr.n === 5 && P.hp === 4, 'Follow Through: 9 on a foe with 4 left sends 5 into the man beside him'); eq(G.run.spoils - sp, T.spoilFoe + T.spoilOwn, 'felling him pays spoils, and one more for Darrow\'s own hand'); }
{ const G = duel('D', 'S', { keep: ['P'] }); const S = U(G, 'S'), P = place(G, 'P', 3, 5); S.hp = 4; P.hp = 5; const sp = G.run.spoils; rig(G, 'D', 'S', ['follow'], { en: 9, fb: 0 }); LH.play(G, 0); ok(P.hp === 0, 'the leftover can fell the second man'); eq(G.run.spoils - sp, 2 * T.spoilFoe + T.spoilOwn, 'and both pay'); }
{ const G = duel('D', 'S', { hp: 99, keep: ['H', 'W'] }); place(G, 'H', 1, 4); place(G, 'W', 3, 4); const K = rig(G, 'D', 'S', ['callco'], { en: 9, fb: 0 }); K.canBreak = false; K.hand = ['callco'];
  const fx = LH.play(G, 0); eq(99 - U(G, 'S').hp, 14, 'Call the Company: his own 4, then two friends, 5 each'); eq(fx.filter(f => f.k === 'dmg' && f.by).map(f => f.by), ['Hollis', 'Wren'], 'and each friend\'s blow is named'); }
{ const G = duel('D', 'S'); U(G, 'S').hp = 3; const sp = G.run.spoils; rig(G, 'D', 'S', ['strip'], { en: 9, fb: 0 }); LH.play(G, 0); eq(G.run.spoils - sp, T.spoilFoe + T.spoilOwn + 2, 'Strip the Fallen pays 2 more when it fells him'); }
{ const G = duel('H', 'S'); U(G, 'S').hp = 3; rig(G, 'H', 'S', ['hew'], { en: 9, fb: 0 }); LH.play(G, 0); eq(G.run.spoils, T.spoilFoe, 'a foe felled by a companion pays the plain amount'); }
{ const G = duel('D', 'S'); U(G, 'S').hp = 5; const K = rig(G, 'D', 'S', ['strike', 'guard'], { en: 9, fb: 0 }); const fx = LH.play(G, 0);
  ok(fx.some(f => f.k === 'down') && K.phase === 'won', 'a killing card ends the clash as won'); ok(LH.play(G, 0) === null, 'no card can be played after it is won'); ok(LH.closeClash(G) && !G.clash, 'a won clash closes'); }

console.log('3. the triangle: Break and its limits');
{ const G = duel('W', 'P', { hp: 99 }); const K = rig(G, 'W', 'P', ['stone', 'stone'], { en: 9, fb: 20 }); ok(K.canBreak, 'Wren has the edge on the Pikeman');
  LH.play(G, 0); ok(!K.broken, 'a fully blocked hit does not Break'); K.fb = 0; LH.play(G, 0); ok(K.broken, 'a hit that lands Breaks');
  const W = U(G, 'W'), hp = W.hp, full = K.intent.d; eq(LH.intent(G).d, Math.ceil(full / 2), 'a Broken foe answers for half'); ok(LH.clashEffects(G).d.some(e => e.id === 'broken'), 'and Broken shows');
  K.halved = true; eq(LH.intent(G).d, Math.ceil(Math.ceil(full / 2) / 2), 'Bellow halves it again'); K.halved = false; const fx = LH.endHand(G); eq([fx[0].n, hp - W.hp], [Math.ceil(full / 2), Math.ceil(full / 2)], 'and the halved blow lands'); }
{ const G = duel('D', 'P'); const K = rig(G, 'D', 'P'); ok(!K.canBreak, 'Darrow has no edge on the Pikeman'); eq(K.en, 2, 'fighting the tree that beats you costs a breath'); }
{ const G = duel('D', 'X'); const K = rig(G, 'D', 'X'); ok(K.canBreak && K.en === 3, 'Blade beats Cast: edge, full breath'); }

console.log('4. reach: fighting from two tiles');
{ const G = duel('D', 'P', { far: true, hp: 99 }); const K = rig(G, 'D', 'P', ['strike', 'hand', 'ground', 'far', 'guard'], { en: 9 }); ok(K.far && !K.p.can, 'two tiles: far, and he cannot answer');
  ok(LH.playable(G, 0) !== '' && LH.playable(G, 2) !== '', 'melee cards are refused'); ok(!LH.playable(G, 1) && !LH.playable(G, 3) && !LH.playable(G, 4), 'thrown cards and skills are allowed');
  ok(LH.play(G, 0) === null && K.hand.length === 5 && K.en === 9, 'a refused card changes nothing');
  const hp = U(G, 'D').hp, fx = LH.endHand(G); eq(fx[0], { k: 'answer', none: 'reach' }, 'no answer out of reach'); eq(U(G, 'D').hp, hp, 'no damage out of reach'); }
{ const G = duel('D', 'X', { far: true }); const K = rig(G, 'D', 'X'); ok(K.far && K.p.can, 'a crossbow answers at two tiles'); eq(K.en, 2, 'throwing from two tiles costs Darrow a breath'); }
{ const G = duel('D', 'P', { far: true }); eq(LH.preview(G, U(G, 'D'), U(G, 'P')).en, 1, 'and against the tree that beats him he has one breath left'); const G2 = duel('W', 'P', { far: true }); eq(LH.preview(G2, U(G2, 'W'), U(G2, 'P')).en, 2, 'Wren throws from two tiles at no cost: it is how she fights'); }
{ const G = duel('D', 'S', { far: true, hp: 99 }); const D = U(G, 'D'); eq(D.throws, T.throws, 'Darrow has ' + T.throws + ' opening throw a battle'); ok(LH.effects(G, D).some(e => e.id === 'throw'), 'and it shows'); rig(G, 'D', 'S'); done(G); D.attacked = false; eq([D.throws, LH.targets(G, D).length], [0, 0], 'once it is used he must close to fight'); place(G, 'S', 2, 5); eq(LH.targets(G, D).length, 1, 'hand to hand, as before'); }

console.log('5. guard, striking back, held breath');
{ const G = duel('D', 'S', { hp: 60 }); const S = U(G, 'S'), D = U(G, 'D'); const K = rig(G, 'D', 'S', ['still', 'still', 'guard'], { en: 3, fb: 0 }); LH.play(G, 0); LH.play(G, 0); eq(K.block, 22, 'two Stillwaters stack to 22');
  const ans = K.intent.d; LH.endHand(G); eq([K.taken, D.guard, D.bank], [0, 22 - ans, 1], 'his answer of ' + ans + ' leaves ' + (22 - ans) + ' guard, 1 breath held'); LH.closeClash(G);
  ok(LH.effects(G, D).some(e => e.id === 'guard' && e.n === 22 - ans) && LH.effects(G, D).some(e => e.id === 'held'), 'guard and held breath show as effects');
  LH.endTurn(G); const ev = LH.enemyStep(G); eq([ev.target, ev.dmg, ev.held, ev.rip], ['D', 0, true, 6], 'guard holds the blow and Darrow strikes back for 6'); eq(S.hp, 54, 'the foe took the answer');
  while (LH.enemyStep(G)) { } eq([D.guard, D.bank], [0, 1], 'guard is gone at the start of your turn; held breath waits');
  const K2 = rig(G, 'D', 'S'); eq([K2.en, D.bank], [4, 0], 'held breath is added, and spent'); }
{ const G = duel('D', 'S'); rig(G, 'D', 'S', ['guard'], { en: 3 }); LH.endHand(G); eq(U(G, 'D').bank, 2, 'held breath is capped at 2'); }
{ const G = duel('D', 'S'); const D = U(G, 'D'); LH.hold(G, D); eq(D.guard, 4, 'Hold here gives 4 guard'); ok(!LH.canAct(D), 'and ends his turn'); LH.endTurn(G); const ev = LH.enemyStep(G); ok(ev.dmg > 0 && !ev.held && ev.rip === 0, 'a blow that breaks the guard is not answered'); }
{ const G = duel('D', 'S', { hp: 99, keep: ['H', 'W'] }); const Hh = place(G, 'H', 1, 4), Wn = place(G, 'W', 5, 6); rig(G, 'D', 'S', ['closeup'], { en: 9 }); const fx = LH.play(G, 0); eq([Hh.guard, Wn.guard], [5, 0], 'Close Up gives guard to the friend beside him, not the one across the field'); ok(fx.some(f => f.k === 'friend' && f.id === 'H'), 'and reports it'); }
{ const G = duel('D', 'S', { hp: 60 }); const D = U(G, 'D'); D.st.atkUp = 2; D.guard = 50; LH.endTurn(G); const ev = LH.enemyStep(G); eq(ev.rip, 8, 'Blood Up also adds to the answering blow'); }

console.log('6. friends: lent cards, rising, marks, flanking');
{ const G = duel('D', 'S', { hp: 99, keep: ['H'] }); place(G, 'H', 1, 4); const D = U(G, 'D'), S = U(G, 'S'), Hh = U(G, 'H');
  let K = rig(G, 'D', 'S'); ok(K.hand.indexOf('lH') >= 0 && K.hand.length === 6, 'a friend beside you lends a card on top of the hand'); done(G);
  ok(D.dk.disc.concat(D.dk.draw, D.dk.gone).indexOf('lH') < 0, 'the lent card is in no pile afterwards'); ok(S.fought && LH.effects(G, S).some(e => e.id === 'open'), 'the foe shows as Open to the next attacker');
  Hh.fights = 2; D.attacked = false; ok(LH.effects(G, Hh).some(e => e.id === 'risen'), 'a friend who has fought twice shows Risen');
  K = rig(G, 'D', 'S'); ok(K.hand.indexOf('lH2') >= 0, 'and lends the risen card'); ok(K.open, 'a foe who has fought this turn starts Open'); }
{ const G = duel('D', 'S', { keep: ['W'] }); place(G, 'W', 4, 5); const K = rig(G, 'D', 'S'); ok(K.hand.indexOf('lW') >= 0, 'a friend placed to strike him lends, even if not beside you'); }
{ const G = duel('W', 'S', { hp: 99, keep: ['D'] }); place(G, 'D', 5, 6); place(G, 'W', 2, 3); const S = U(G, 'S');
  rig(G, 'W', 'S', ['count'], { en: 2 }); LH.play(G, 0); done(G); ok(S.marked && LH.effects(G, S).some(e => e.id === 'marked'), 'The Count marks him, and it shows');
  place(G, 'D', 2, 6); const K = rig(G, 'D', 'S'); eq(K.en, 4, 'the next friend has one more breath'); ok(!S.marked, 'and the mark is used'); }

console.log('7. cards that change the map');
{ const G = duel('D', 'S', { hp: 99 }); rig(G, 'D', 'S', ['ground'], { en: 9 }); LH.play(G, 0); done(G); eq([U(G, 'S').x, U(G, 'S').y], [2, 6], 'Groundbreaker drives him back a tile'); }
{ const G = duel('D', 'S', { hp: 99 }); place(G, 'D', 2, 5); place(G, 'S', 2, 4); rig(G, 'D', 'S', ['ground'], { en: 9 }); LH.play(G, 0); done(G); eq([U(G, 'S').x, U(G, 'S').y], [2, 3], 'he can be driven onto a ford'); }
{ const G = duel('D', 'S', { hp: 99 }); place(G, 'D', 1, 5); place(G, 'S', 1, 4); rig(G, 'D', 'S', ['ground'], { en: 9 }); LH.play(G, 0); done(G); eq([U(G, 'S').x, U(G, 'S').y], [1, 4], 'he cannot be driven into deep water'); }
{ const G = duel('D', 'S', { hp: 99 }); const K = rig(G, 'D', 'S', ['hammer'], { en: 9, fb: 0 }); K.canBreak = false; const before = LH.intent(G).d; LH.play(G, 0); const it = LH.intent(G); eq(99 - U(G, 'S').hp, 14, 'Hammerfall deals 14'); ok(it.halved && it.d === Math.ceil(before / 2) || it.halved && it.d === Math.floor(before / 2), 'and halves his answer this hand'); }
{ const G = duel('D', 'S', { hp: 99 }); const S = U(G, 'S'); rig(G, 'D', 'S', ['hammer'], { en: 9 }); LH.play(G, 0); done(G); ok(S.pinned && LH.effects(G, S).some(e => e.id === 'pinned'), 'Hammerfall pins him, and it shows');
  place(G, 'D', 5, 6); place(G, 'S', 0, 0); LH.endTurn(G); const ev = LH.enemyStep(G); ok(ev.pinned && ev.to[0] === 0 && ev.to[1] === 0 && !S.pinned, 'a pinned foe does not move, then recovers'); }
{ const G = duel('D', 'S', { hp: 99 }); const D = U(G, 'D'); rig(G, 'D', 'S', ['road'], { en: 9 }); LH.play(G, 0); done(G);
  ok(LH.canAct(D) && D.free && !D.moved && LH.effects(G, D).some(e => e.id === 'again'), 'The Long Road leaves him free to move, and says so'); eq(LH.targets(G, D).length, 0, 'but not to fight again'); ok(LH.move(G, D, 3, 4), 'he moves'); ok(!LH.canAct(D), 'and is then done'); }
{ const G = duel('D', 'S', { keep: ['P'] }); const D = U(G, 'D'), P = place(G, 'P', 3, 4); U(G, 'S').hp = 3; P.hp = 3;
  rig(G, 'D', 'S', ['strike'], { en: 9, fb: 0 }); LH.play(G, 0); LH.closeClash(G); ok(LH.canAct(D) && !D.attacked && D.more, 'a man down: he may act again');
  rig(G, 'D', 'P', ['strike'], { en: 9, fb: 0 }); LH.play(G, 0); LH.closeClash(G); ok(P.hp === 0 && !LH.canAct(D), 'but only once a turn'); }

console.log('8. the deck: piles, once a battle, a new hand, the hand limit, Wounds');
{ const G = duel('D', 'S', { hp: 999 }); const D = U(G, 'D');
  const total = () => D.dk.draw.length + D.dk.disc.length + D.dk.gone.length + (G.clash ? G.clash.hand.filter(x => !C[x].lent).length : 0);
  let K = rig(G, 'D', 'S'); eq([total(), K.hand.length], [16, 5], 'sixteen cards, a hand of five');
  ok(LH.redraw(G), 'Inspiration deals a new hand'); eq([G.run.insp, K.hand.length, total()], [2, 5, 16], 'it costs one, deals five, loses no card'); ok(!LH.redraw(G), 'only once a clash'); done(G);
  for (let i = 0; i < 6; i++) { D.attacked = false; D.hp = D.max; rig(G, 'D', 'S'); done(G); } eq(total(), 16, 'the played pile is reshuffled when the draw pile runs out'); }
{ const G = duel('D', 'S'); const K = rig(G, 'D', 'S', ['eye', 'eye', 'eye', 'eye', 'strike', 'strike', 'strike'], { en: 9 }); LH.play(G, 0); eq(K.hand.length, 8, 'drawing stops at eight in hand'); LH.play(G, 0); eq(K.hand.length, 8, 'and stays there'); }
{ const G = duel('H', 'S'); const K = rig(G, 'H', 'S'); eq([K.hand.length, K.en], [3, 2], 'a companion plays three cards on two breath'); ok(!LH.redraw(G), 'and cannot spend Inspiration'); }
{ const G = duel('D', 'X', { hp: 99 }); const D = U(G, 'D'); let K = rig(G, 'D', 'X', ['guard'], { en: 0 }); K.canBreak = false; let fx = LH.endHand(G);
  ok(fx.some(f => f.k === 'wound') && LH.wounds(D) === 1, 'a crossbow bolt that lands leaves a Wound'); LH.closeClash(G); ok(LH.effects(G, D).some(e => e.id === 'wound' && e.n === 1), 'and the Wound shows on him');
  D.attacked = false; K = rig(G, 'D', 'X', ['still', 'still'], { en: 9 }); K.canBreak = false; LH.play(G, 0); LH.play(G, 0); fx = LH.endHand(G); ok(!fx.some(f => f.k === 'wound') && LH.wounds(D) === 1, 'a blocked bolt leaves none'); LH.closeClash(G);
  D.attacked = false; K = rig(G, 'D', 'X', ['wound', 'bandage'], { en: 9 }); ok(LH.playable(G, 0).indexOf('Wound') >= 0, 'a Wound in hand cannot be played'); ok(LH.clashEffects(G).a.some(e => e.id === 'wound'), 'and shows in the clash');
  LH.play(G, 1); ok(K.hand.indexOf('wound') < 0, 'a Clean Bandage sets aside the one in hand first'); }
{ const G = duel('D', 'X', { hp: 99 }); const D = U(G, 'D'); place(G, 'X', 2, 6); LH.endTurn(G); const ev = LH.enemyStep(G); ok(ev.wound && LH.wounds(D) === 1, 'a bolt on their turn leaves a Wound too'); }

console.log('9. moving: costs, blocking, the cart, three grounds');
{ const G = fresh(); isolate(G, ['H']); const Hh = place(G, 'H', 2, 4), r = LH.reach(G, Hh); ok(r['2,3'] === 2, 'a ford costs two steps'); ok(r['2,2'] === undefined, 'so Hollis cannot cross in one turn'); ok(r['1,4'] === 2, 'the wood costs two'); ok(r['0,3'] === undefined && r['1,3'] === undefined, 'deep water cannot be entered'); }
{ const G = fresh(); const D = U(G, 'D'); ok(!LH.move(G, D, 4, 4), 'cannot move onto a friend'); ok(!LH.move(G, D, 2, 4), 'cannot move to where he stands'); ok(LH.move(G, D, 3, 4), 'a legal move'); ok(!LH.move(G, D, 2, 4), 'one move a turn'); }
{ const G = fresh(); isolate(G, ['D']); LH.endTurn(G); while (LH.enemyStep(G)) { } eq(G.turn, 2, 'ending the turn with no foe near moves on to turn two'); }
{ const G = battle(3); eq(G.map.name, 'The Bridge', 'the third ground is the bridge'); isolate(G, ['H']); const Hh = place(G, 'H', 2, 4), r = LH.reach(G, Hh); ok(r['2,3'] === 1 && r['2,2'] === 2, 'a bridge costs one step, so Hollis crosses in a turn'); }
LH.MAPS.forEach((M, i) => { ok(M.rows.length === LH.H && M.rows.every(r => r.length === LH.W && /^[.wd~fbc]+$/.test(r)), M.name + ': a well-formed 6 by 7 ground');
  const G = battle(i + 1), seen = {}; ok(G.u.every(u => { const k = u.x + ',' + u.y, good = LH.ok(G, u.x, u.y) && !seen[k]; seen[k] = 1; return good; }), M.name + ': everyone starts on open ground, one to a tile');
  ok(G.u.filter(u => u.boss).length === 1, M.name + ': exactly one captain'); const cap = G.u.filter(u => u.boss)[0]; G.u.forEach(u => { if (u !== cap && u.id !== 'D') u.hp = 0; }); const far = LH.reach(G, Object.assign({}, U(G, 'D'), { mov: 99 }));
  ok([[1, 0], [-1, 0], [0, 1], [0, -1]].some(d => far[(cap.x + d[0]) + ',' + (cap.y + d[1])] !== undefined), M.name + ': the captain can be reached on foot'); });

console.log('9b. Rae, who tends');
{ const G = fresh(), R = U(G, 'R'); ok(R && R.hp === 28 && LH.targets(G, R).length === 0 && LH.engage(G, R, U(G, 'P')) === null, 'Rae is with the company and does not fight'); ok(LH.effects(G, R).some(e => e.id === 'tend'), 'her tending shows as an effect');
  [1, 2, 3].forEach(n => ok(!!U(battle(n), 'R'), 'she is on ground ' + n)); ok(LH.move(G, R, 4, 5) && !LH.move(G, R, 4, 6) && LH.hold(G, R), 'she moves like anyone: one move a turn, and she may still hold after it'); }
{ const G = fresh(); isolate(G, ['D', 'R']); const D = place(G, 'D', 2, 4), R = place(G, 'R', 2, 5); D.hp = 40; D.dk.disc.push('wound');
  eq(LH.tendTargets(G, R).map(u => u.id), ['D'], 'a hurt friend beside her can be tended'); const r = LH.tend(G, R, D); eq([r.heal, r.wound, D.hp, LH.wounds(D)], [T.tend, true, 40 + T.tend, 0], 'tending mends ' + T.tend + ' and sets aside a Wound'); ok(!LH.canAct(R), 'and that is her turn'); ok(LH.tend(G, R, D) === null, 'once a turn'); }
{ const G = fresh(); isolate(G, ['D', 'R', 'H']); const D = place(G, 'D', 2, 4), R = place(G, 'R', 2, 5), Hh = place(G, 'H', 2, 6); Hh.hp = 10; eq(LH.tendTargets(G, R).map(u => u.id), ['H'], 'a friend at full health with no Wound needs no tending'); D.hp = 56; LH.tend(G, R, D); eq(D.hp, 58, 'mending stops at full health');
  const G2 = fresh(); isolate(G2, ['D', 'R']); place(G2, 'D', 2, 4).hp = 30; place(G2, 'R', 2, 6); eq(LH.tendTargets(G2, U(G2, 'R')).length, 0, 'she must be beside them'); }
{ const G = duel('D', 'S', { hp: 99, keep: ['R'] }); const D = U(G, 'D'), R = place(G, 'R', 1, 4); D.hp = 30; let K = rig(G, 'D', 'S'); ok(K.hand.indexOf('lR') >= 0, 'a fighter with Rae beside him is lent her hand'); const i = K.hand.indexOf('lR'); LH.play(G, i); eq(D.hp, 30 + 2 * LH.SHEET.tether, 'which mends by the Tether'); done(G);
  R.fights = 2; D.attacked = false; D.hp = 30; K = rig(G, 'D', 'S'); ok(K.hand.indexOf('lR2') >= 0 && LH.effects(G, R).some(e => e.id === 'risen'), 'after she has tended twice her hand has risen'); }
{ const G = duel('R', 'S', { keep: ['D'] }); place(G, 'D', 5, 6); const R = U(G, 'R'); R.guard = 50; LH.endTurn(G); const ev = LH.enemyStep(G); eq([ev.target, ev.held, ev.rip], ['R', true, 0], 'a foe can strike her, and she does not strike back'); R.guard = 0; R.hp = 2; while (LH.enemyStep(G)) { } LH.endTurn(G); LH.enemyStep(G); ok(R.hp === 0 && !G.over, 'if she falls back the run goes on'); }

{ const G = fresh(); isolate(G, ['D', 'R', 'H']); const D = place(G, 'D', 2, 4), R = place(G, 'R', 2, 5); eq(R.tends, T.tends, 'she can tend ' + T.tends + ' times a battle');
  for (let i = 0; i < T.tends; i++) { D.hp = 20; R.attacked = false; ok(!!LH.tend(G, R, D), 'tend ' + (i + 1)); } D.hp = 20; R.attacked = false; eq(LH.tendTargets(G, R).length, 0, 'then the cart is bare'); ok(LH.effects(G, R).some(e => e.label === 'Cart is bare'), 'and it says so');
  G.run.n = 1; eq(U(battle(2), 'R').tends, T.tends, 'a new battle fills it again'); }

console.log('9c. taking a move back, the captain\'s patience, difficulty');
{ const G = fresh(), D = U(G, 'D'); ok(!LH.canUnmove(G, D), 'nothing to take back before a move'); LH.move(G, D, 3, 4); ok(LH.canUnmove(G, D) && LH.unmove(G, D), 'a move can be taken back'); eq([D.x, D.y, D.moved], [2, 4, false], 'he is where he was and may move again');
  LH.move(G, D, 3, 4); LH.move(G, U(G, 'A'), 2, 4); ok(!LH.canUnmove(G, D) && !LH.unmove(G, D), 'unless someone now stands there'); LH.unmove(G, U(G, 'A')); LH.hold(G, D); ok(!LH.canUnmove(G, D), 'or he has done something since'); }
{ const G = duel('D', 'S', { hp: 99, far: true }); const D = U(G, 'D'); LH.move(G, D, 2, 5); rig(G, 'D', 'S'); done(G); ok(!LH.canUnmove(G, D), 'a fight cannot be walked back'); }
{ const G = fresh(); place(G, 'D', 5, 6); place(G, 'H', 4, 6); place(G, 'A', 5, 5); place(G, 'W', 3, 6); place(G, 'R', 4, 5); const Cp = U(G, 'C'); ok(LH.holding(G, Cp), 'the captain holds early on'); G.turn = T.capPatience; ok(!LH.holding(G, Cp), 'and comes forward when turn ' + T.capPatience + ' arrives'); }
{ const g0 = LH.newRun({ seed: 5 }), g1 = LH.newRun({ seed: 5, level: 1 }), gm = LH.newRun({ seed: 5, level: -1 }), P = g => U(g, 'P'); ok(P(g1).atk === P(g0).atk + T.levelAtk && P(gm).atk === P(g0).atk - T.levelAtk && P(g1).hp > P(g0).hp && P(gm).hp < P(g0).hp, 'Hard and Gentle move the foes\' strength up and down');
  eq(P(g1).ans[0].d - P(g0).ans[0].d, T.levelAtk, 'answers included'); }

{ const G = fresh(); isolate(G, ['D']); place(G, 'D', 5, 6); G.turn = T.maxTurns; LH.endTurn(G); while (LH.enemyStep(G)) { } ok(G.over && G.over.lost && G.over.night, 'a battle not won by turn ' + T.maxTurns + ' is lost at nightfall'); }

console.log('9d. falling back through a friend, and the steps of a move');
{ const G = fresh(); isolate(G, ['D', 'H']); const D = place(G, 'D', 2, 3), Hh = place(G, 'H', 2, 4);
  eq(LH.fallBack(G, D), [2, 5], 'with a friend right behind him he can fall back to the tile beyond'); ok(LH.reach(G, D)['2,5'] === D.mov && LH.fellBack(G, D, 2, 5), 'it is one of his moves, and it costs the whole move');
  eq(LH.path(G, D, 2, 5), [[2, 4], [2, 5]], 'the steps go through the friend'); ok(!LH.fellBack(G, D, 2, 2) && LH.path(G, D, 2, 1).length === 2, 'an ordinary move is not a fall back');
  ok(LH.move(G, D, 2, 5) && D.x === 2 && D.y === 5 && D.moved && Hh.x === 2 && Hh.y === 4, 'he moves, the friend stays'); ok(!LH.move(G, D, 2, 6), 'and that was his move');
  ok(LH.canUnmove(G, D) && LH.unmove(G, D) && D.y === 3, 'it can be taken back like any move'); }
{ const G = fresh(); isolate(G, ['D', 'H', 'A']); const D = place(G, 'D', 2, 3); place(G, 'H', 2, 4); place(G, 'A', 2, 5); ok(!LH.fallBack(G, D) && LH.reach(G, D)['2,5'] === undefined && LH.reach(G, D)['2,6'] === undefined, 'not through two friends, and never further than the tile beyond'); }
{ const G = fresh(); isolate(G, ['D', 'H']); const D = place(G, 'D', 2, 3); place(G, 'H', 2, 2); ok(LH.reach(G, D)['2,1'] === undefined, 'not forward through a friend'); }
{ const G = fresh(); isolate(G, ['D', 'H', 'A']); const D = place(G, 'D', 0, 6); place(G, 'H', 1, 6); place(G, 'A', 0, 5); ok(!LH.fallBack(G, D) && LH.reach(G, D)['2,6'] === undefined, 'not sideways through a friend'); }
{ const G = fresh(); isolate(G, ['D', 'S']); const D = place(G, 'D', 2, 2); place(G, 'S', 2, 3); ok(!LH.fallBack(G, D) && LH.reach(G, D)['2,4'] === undefined, 'not through a foe'); }
{ const G = fresh(); isolate(G, ['D', 'H']); const D = place(G, 'D', 0, 1); place(G, 'H', 0, 2); ok(!LH.fallBack(G, D), 'not into deep water'); }
{ const G = fresh(); isolate(G, ['D', 'H', 'S']); const D = place(G, 'D', 2, 3); place(G, 'H', 2, 4); place(G, 'S', 2, 5); ok(!LH.fallBack(G, D), 'not onto a tile someone stands on'); }
{ const G = fresh(); isolate(G, ['D', 'P', 'S']); place(G, 'D', 5, 6); const P = place(G, 'P', 2, 2); place(G, 'S', 2, 3); ok(!LH.fallBack(G, P) && LH.reach(G, P)['2,4'] === undefined, 'the foes do not fall back through each other'); }
{ let bad = 0, n = 0; [1, 2, 3].forEach(b => { const G = battle(b); G.u.forEach(u => { if (u.hp <= 0) return; const r = LH.reach(G, u); Object.keys(r).forEach(k => { const p = k.split(',').map(Number); if (p[0] === u.x && p[1] === u.y) return; n++;
    const st = LH.path(G, u, p[0], p[1]); let x = u.x, y = u.y, good = st.length > 0 && st[st.length - 1][0] === p[0] && st[st.length - 1][1] === p[1]; st.forEach(q => { if (Math.abs(q[0] - x) + Math.abs(q[1] - y) !== 1) good = false; x = q[0]; y = q[1]; }); if (!good) bad++; }); }); });
  ok(n > 100 && bad === 0, 'every tile a unit can reach has its steps, each one tile from the last (' + n + ' moves on three grounds)'); }
{ const G = fresh(); isolate(G, ['D', 'S']); place(G, 'D', 2, 6); const S = place(G, 'S', 2, 1); LH.endTurn(G); let ev, moved = null; while ((ev = LH.enemyStep(G))) if (ev.id === 'S' && ev.path) moved = ev;
  ok(moved && moved.path.length >= 1 && moved.path[moved.path.length - 1][0] === S.x && moved.path[moved.path.length - 1][1] === S.y, 'a foe\'s move comes with its steps'); }

console.log('10. a clash of several rounds');
{ const G = duel('D', 'X', { rounds: 3, hp: 99 }); const D = U(G, 'D'); let K = rig(G, 'D', 'X', ['strike', 'guard'], { en: 3, fb: 0 }); LH.play(G, 0); ok(K.broken, 'Break in round one'); LH.play(G, 0); LH.endHand(G); eq(K.phase, 'choice', 'after his answer you choose');
  ok(LH.closeClash(G) === false, 'the clash cannot be closed mid-choice'); const ni = LH.nextIntent(G); ok(LH.pressOn(G), 'press on');
  eq([K.round, K.block, K.broken, K.canBreak, K.hand.length, K.en], [2, 0, false, false, 5, 2], 'round two: block gone, Break over, new hand, one less breath'); eq(LH.intent(G).d, ni.d, 'his shown next move is the one he makes');
  LH.endHand(G); ok(LH.leave(G), 'break off'); eq(K.phase, 'after', 'the clash is over'); LH.closeClash(G);
  D.attacked = false; D.hp = D.max; K = rig(G, 'D', 'X'); LH.endHand(G); LH.pressOn(G); LH.endHand(G); LH.pressOn(G); eq(K.round, 3, 'round three'); LH.endHand(G); eq(K.phase, 'after', 'three rounds is the limit'); }

console.log('11. what the foes bring');
{ const G = battle(2); isolate(G, ['D', 'K']); place(G, 'D', 2, 4); place(G, 'K', 2, 5); const D = U(G, 'D'); const K = rig(G, 'D', 'K', ['guard'], { en: 9 }); K.canBreak = false; const it = LH.intent(G);
  eq([it.d, it.n], [5 + T.atkBy[1], 2], 'the Skirmisher answers with two small blows'); ok(LH.clashEffects(G).d.some(e => e.id === 'flurry'), 'and Flurry shows'); LH.play(G, 0); const hp = D.hp; LH.endHand(G);
  eq(hp - D.hp, 2 * (5 + T.atkBy[1]) - 6, 'block soaks across both blows'); }
{ const G = battle(3); const P = U(G, 'P'), F = U(G, 'F'); ok(LH.rallied(G, P) && !LH.rallied(G, F), 'the banner rallies the others, not its bearer'); ok(LH.effects(G, P).some(e => e.id === 'rallied') && LH.effects(G, F).some(e => e.id === 'banner'), 'both show');
  isolate(G, ['D', 'P', 'F']); place(G, 'D', 2, 4); place(G, 'P', 2, 5); place(G, 'F', 5, 6); let K = rig(G, 'D', 'P'); const base = P.ans[0].d; eq(LH.intent(G).d, base + T.rally, 'a rallied answer is 2 harder'); eq(K.p.ans.d, base + T.rally, 'and the forecast said so');
  F.hp = 0; eq(LH.intent(G).d, base, 'the moment the banner falls, it is not'); done(G); }
{ const G = battle(3); isolate(G, ['D', 'P', 'F']); const D = place(G, 'D', 2, 4); place(G, 'P', 2, 5); place(G, 'F', 5, 6); D.guard = 0; LH.endTurn(G); let ev; while ((ev = LH.enemyStep(G)) && ev.id !== 'P') { }
  eq(ev.dmg, U(G, 'P').atk + T.rally + 2, 'a rallied blow on their turn is 2 harder too (and Footing beats Blade for 2 more)'); }
{ const G = duel('D', 'C', { hp: 44 }); const Cp = U(G, 'C'); const K = rig(G, 'D', 'C', ['strike', 'strike', 'strike', 'strike'], { en: 9, fb: 0 }); K.canBreak = false; const d0 = LH.intent(G).d; ok(LH.clashEffects(G).d.some(e => e.id === 'temper'), 'the captain warns that he will enrage');
  Cp.hp = 26; const fx = LH.play(G, 0); ok(fx.some(f => f.t === 'Enraged') && LH.enraged(Cp), 'bringing him to half health enrages him'); eq(LH.intent(G).d, d0 + Cp.enrage, 'and his answer grows at once'); ok(LH.clashEffects(G).d.some(e => e.id === 'enraged'), 'and it shows'); }
{ const G = fresh(); place(G, 'D', 5, 6); place(G, 'H', 4, 6); place(G, 'A', 5, 5); place(G, 'W', 3, 6); place(G, 'R', 4, 5); const Cp = U(G, 'C'); ok(LH.holding(G, Cp) && LH.effects(G, Cp).some(e => e.id === 'holds'), 'the captain holds while his men stand and nobody is near');
  LH.endTurn(G); let ev, cap; while ((ev = LH.enemyStep(G))) if (ev.id === 'C') cap = ev; ok(cap.holds && cap.to[0] === 2 && cap.to[1] === 0, 'and does not move'); }
{ const G = fresh(); isolate(G, ['D', 'H', 'C']); place(G, 'D', 3, 5); place(G, 'H', 3, 4); place(G, 'C', 3, 2); LH.endTurn(G); const ev = LH.enemyStep(G); ok(ev.to[1] === 2 && ev.to[0] !== 3, 'alone and facing deep water, he heads for a ford'); while (LH.enemyStep(G)) { } LH.endTurn(G); ok(LH.enemyStep(G).to[1] === 3, 'and steps onto it the turn after'); }
{ const G = battle(2); const B = U(G, 'B'); ok(LH.effects(G, B).some(e => e.id === 'tough'), 'Tough shows on the Shieldbearer'); ok(LH.effects(G, U(G, 'X')).some(e => e.id === 'barbed'), 'Barbed shows on the Crossbowman'); }
{ const G = fresh(); G.u.forEach(u => LH.effects(G, u).forEach(e => ok(e.id && e.label && e.text && /^(good|bad|plain)$/.test(e.tone), 'effect ' + e.id + ' is fully described'))); }

console.log('12. spoils and the camp');
{ const G = duel('D', 'C', { keep: ['S'] }); const D = U(G, 'D'); D.hp = 31; place(G, 'S', 3, 4).hp = 1; U(G, 'C').hp = 3;
  rig(G, 'D', 'S', ['strike'], { en: 9, fb: 0 }); LH.play(G, 0); LH.closeClash(G); eq(G.run.spoils, T.spoilFoe + T.spoilOwn, 'felling a man by his own hand pays ' + (T.spoilFoe + T.spoilOwn));
  rig(G, 'D', 'C', ['strike'], { en: 9, fb: 0 }); LH.play(G, 0); LH.closeClash(G); ok(G.over && G.over.win && LH.inCamp(G), 'the captain down wins the battle and opens the camp'); eq(G.run.spoils, T.spoilFoe + T.spoilBoss + 2 * T.spoilOwn, 'the captain pays ' + T.spoilBoss + ', and one more for his own hand');
  eq(G.camp.market.length, T.market, 'the camp lays out ' + T.market + ' cards'); ok(new Set(G.camp.market).size === T.market && G.camp.market.every(id => C[id].p > 0), 'all different, all priced');
  ok(!LH.endTurn(G) && !LH.move(G, D, 3, 4), 'nothing moves after the battle');
  G.run.spoils = 20; const pick = G.camp.market[0], price = C[pick].p; ok(LH.campBuy(G, pick), 'a card can be bought'); eq([G.run.spoils, G.run.deck.length], [20 - price, 17], 'for its price, into the deck'); ok(!LH.campBuy(G, pick), 'each card once');
  G.run.spoils = 1; ok(!LH.campBuy(G, G.camp.market[0]) && !LH.campMend(G) && !LH.campRemove(G, 'strike') && !LH.campHone(G, 'strike'), 'nothing without the spoils for it');
  G.run.spoils = 20; ok(LH.campMend(G), 'mend'); eq([D.hp, G.run.spoils], [46, 20 - T.mendCost], 'mending gives 15 for 3');
  ok(LH.campRemove(G, 'guard'), 'a card can be left behind'); eq(G.run.deck.filter(x => x === 'guard').length, 1, 'one Guard fewer'); ok(!LH.campRemove(G, 'nosuch'), 'only a card he has');
  ok(LH.campHone(G, 'strike'), 'a Strike can be honed'); eq(G.run.deck.filter(x => x === 'strike2').length, 1, 'into a better one'); ok(!LH.campHone(G, 'seated'), 'an Art cannot be honed');
  const sp = G.run.spoils; ok(LH.nextBattle(G), 'march on'); eq([G.run.n, G.map.name, G.run.hp], [2, 'The Wood Road', 46 + T.rest], 'battle two on the Wood Road, health carried plus a night of rest');
  const D2 = U(G, 'D'); ok(D2.deck.indexOf(pick) >= 0 && D2.deck.indexOf('strike2') >= 0 && D2.deck.length === 16, 'the deck is the one he left camp with'); eq(G.run.spoils, sp, 'unspent spoils are kept');
  eq(U(G, 'H').hp, 40, 'the company is whole again'); eq(D2.st.atkUp + D2.st.blockStart + D2.st.drawUp, 0, 'stances do not carry between battles'); ok(G.u.some(u => u.id === 'K') && G.u.some(u => u.id === 'B'), 'new foes are on the field');
  eq(U(G, 'B').hp, Math.round(28 * (1 + T.hpBy[1])), 'and later battles are harder'); }
{ const G = fresh(); G.run.deck = G.run.deck.slice(0, LH.MIN_DECK); G.over = { win: 1 }; G.camp = { market: [], bought: [] }; G.run.spoils = 9; ok(!LH.campRemove(G, 'strike'), 'the deck cannot be thinned below ' + LH.MIN_DECK); }
{ const G = battle(3); isolate(G, ['D', 'C']); place(G, 'D', 2, 4); place(G, 'C', 2, 5).hp = 1; G.run.won = 2; G.run.spoils = 5; rig(G, 'D', 'C', ['strike'], { en: 9, fb: 0 }); LH.play(G, 0); LH.closeClash(G);
  ok(G.over && G.over.done, 'the third captain ends the run'); ok(!LH.nextBattle(G) && !LH.inCamp(G), 'there is no fourth battle'); eq(G.run.renown, 5 + T.spoilBoss + T.spoilOwn + 18 + (T.par - 1) + 0 + Math.floor(U(G, 'D').hp / 8), 'renown counts spoils kept, battles won, a quick finish, friends standing and health'); }
{ const G = duel('D', 'C'); const D = U(G, 'D'); D.hp = 4; rig(G, 'D', 'C', ['guard'], { en: 0 }); const fx = LH.endHand(G); ok(fx.some(f => f.k === 'down' && f.who === 'a'), 'Darrow can fall to an answer'); LH.closeClash(G); ok(G.over && G.over.lost && G.run.renown >= 0, 'and that loses the run'); }
{ const G = duel('D', 'C'); U(G, 'D').guard = 99; U(G, 'C').hp = 5; LH.endTurn(G); const ev = LH.enemyStep(G); ok(ev.foeDown && G.over && G.over.win && G.run.spoils === T.spoilBoss, 'a captain felled by an answering blow also wins, and pays'); }
{ const G = duel('W', 'S', { keep: ['D'] }); place(G, 'D', 5, 6); U(G, 'W').hp = 2; LH.endTurn(G); const ev = LH.enemyStep(G); ok(ev.targetDown && U(G, 'W').hp === 0 && !G.over, 'a companion falls back without ending the run'); ok(LH.at(G, 2, 4) === null, 'and leaves the tile'); }

console.log('13. refusals');
{ const G = fresh(); const D = U(G, 'D'); ok(LH.engage(G, D, U(G, 'C')) === null, 'cannot engage out of reach'); ok(LH.endHand(G) === null && LH.play(G, 0) === null && !LH.pressOn(G) && !LH.leave(G) && !LH.closeClash(G), 'clash actions do nothing on the map');
  ok(LH.enemyStep(G) === null, 'the enemy does not act on your turn'); ok(!LH.nextBattle(G) && !LH.campBuy(G, 'hew') && !LH.campMend(G), 'no camp before a win'); ok(!LH.hold(G, U(G, 'P')), 'a foe cannot be ordered');
  rig(G, 'D', 'P'); ok(!LH.move(G, U(G, 'H'), 4, 5) && !LH.endTurn(G), 'the map is frozen during a clash'); ok(!LH.closeClash(G), 'a clash in play cannot be closed'); }

/* ---------- fuzz: random legal play, invariants after every action ---------- */
function invariants(G, tag) {
  const bad = m => { throw new Error('invariant: ' + m + ' @ ' + tag); };
  const seen = {};
  G.u.forEach(u => {
    if (!Number.isInteger(u.hp) || u.hp < 0 || u.hp > u.max) bad(u.id + ' hp ' + u.hp);
    if (!Number.isInteger(u.guard) || u.guard < 0) bad(u.id + ' guard ' + u.guard);
    if (!Number.isInteger(u.bank) || u.bank < 0 || u.bank > LH.HELD_MAX) bad(u.id + ' bank ' + u.bank);
    if (u.hp > 0) { const k = u.x + ',' + u.y; if (seen[k]) bad('two on ' + k); seen[k] = 1; if (!LH.ok(G, u.x, u.y)) bad(u.id + ' off the map'); }
    if (u.dk) {
      const inHand = (G.clash && G.clash.a === u) ? G.clash.hand.filter(x => !C[x].lent) : [];
      const all = u.dk.draw.concat(u.dk.disc, u.dk.gone, inHand).filter(x => x !== 'wound').sort(), want = u.deck.slice().sort();
      if (JSON.stringify(all) !== JSON.stringify(want)) bad(u.id + ' cards lost or made: ' + all.length + ' of ' + want.length);
      if (u.dk.draw.concat(u.dk.disc, u.dk.gone).some(x => C[x].lent)) bad(u.id + ' lent card in a pile'); if (u.dk.gone.indexOf('wound') >= 0) bad('wound set aside wrongly');
    }
    LH.effects(G, u).forEach(e => { if (!e.id || !e.label || !e.text) bad('effect without words on ' + u.id); });
  });
  if (G.clash) { const K = G.clash;
    ['en', 'block', 'fb', 'dealt', 'taken'].forEach(f => { if (!Number.isInteger(K[f]) || K[f] < 0) bad('clash ' + f + ' ' + K[f]); });
    if (K.hand.length > LH.HAND_CAP) bad('hand of ' + K.hand.length); if (K.hand.some(x => !C[x])) bad('unknown card'); if (K.round > G.opts.rounds) bad('round ' + K.round);
    const ce = LH.clashEffects(G); ce.a.concat(ce.d).forEach(e => { if (!e.id || !e.label || !e.text) bad('clash effect without words'); });
    if (K.phase === 'play') { const it = LH.intent(G); if (!it.none && (!Number.isInteger(it.d) || it.d < 0 || it.n < 1)) bad('intent ' + JSON.stringify(it)); K.hand.forEach(id => { if (typeof LH.cardText(id, K) !== 'string') bad('card text'); }); } }
  const r = G.run; if (r.insp < 0 || r.insp > 3 || r.n < 1 || r.n > 3 || !Number.isInteger(r.spoils) || r.spoils < 0 || r.deck.length < LH.MIN_DECK) bad('run state ' + JSON.stringify([r.insp, r.n, r.spoils, r.deck.length]));
  if (r.hp < 1 || r.hp > LH.MAX_HP) bad('run hp ' + r.hp);
}
function rnd(st) { st.s = (st.s * 1664525 + 1013904223) >>> 0; return st.s / 4294967296; }
function fuzzOne(seed, rounds, skill) {
  const G = LH.newRun({ seed, rounds, deck: skill ? LH.BASE_DECK.concat(LH.POOL, ['strike2', 'guard2']) : undefined }), st = { s: seed * 2654435761 >>> 0 }, pick = a => a[Math.floor(rnd(st) * a.length)];
  let steps = 0, outcome = 'stalled'; const seen = {};
  while (steps++ < 8000) {
    invariants(G, 'seed ' + seed + ' step ' + steps);
    if (G.over) { if (G.over.win) { const r = rnd(st);
        if (r < .3 && G.camp.market.length) LH.campBuy(G, pick(G.camp.market)); else if (r < .4) LH.campMend(G); else if (r < .5) LH.campRemove(G, pick(G.run.deck)); else if (r < .6) LH.campHone(G, pick(['strike', 'guard'])); else if (!LH.nextBattle(G)) throw new Error('nextBattle refused');
        continue; } outcome = G.over.lost ? 'lost' : 'done'; break; }
    if (G.phase === 'enemy') { LH.enemyStep(G); continue; }
    const K = G.clash;
    if (K) {
      if (K.phase === 'play') { const can = K.hand.map((_, i) => i).filter(i => !LH.playable(G, i)), r = rnd(st);
        if (can.length && r < .8) { const i = pick(can); seen[K.hand[i]] = 1; if (!LH.play(G, i)) throw new Error('playable card refused'); } else if (r < .85 && LH.redraw(G)) { } else LH.endHand(G); }
      else if (K.phase === 'choice') { if (rnd(st) < .5) LH.pressOn(G); else LH.leave(G); }
      else LH.closeClash(G);
      continue;
    }
    const acts = [], fights = [];
    G.u.forEach(u => { if (!LH.canAct(u)) return; LH.targets(G, u).forEach(d => fights.push(() => LH.engage(G, u, d)));
      if (!u.moved) Object.keys(LH.reach(G, u)).forEach(k => { const p = k.split(','); if (+p[0] !== u.x || +p[1] !== u.y) acts.push(() => LH.move(G, u, +p[0], +p[1])); });
      LH.tendTargets(G, u).forEach(t => acts.push(() => !!LH.tend(G, u, t)));
      if (!u.attacked) acts.push(() => LH.hold(G, u)); if (LH.canUnmove(G, u)) acts.push(() => LH.unmove(G, u)); });
    if (skill && fights.length && rnd(st) < .7) { if (!pick(fights)()) throw new Error('listed fight refused'); continue; }
    const all = acts.concat(fights);
    if (!all.length || rnd(st) < .18) { if (!LH.endTurn(G)) throw new Error('endTurn refused'); } else if (!pick(all)()) throw new Error('listed action refused');
  }
  return { o: outcome + '@' + G.run.n, seen };
}
console.log('14. fuzz: random legal play with invariants checked after every action');
{ const kinds = {};
  [[1, 0], [3, 0], [1, 1], [3, 1]].forEach(([rounds, skill]) => { const tally = {}; let threw = null;
    for (let s = 1; s <= 1000 && !threw; s++) { try { const r = fuzzOne(s, rounds, skill); tally[r.o] = (tally[r.o] || 0) + 1; Object.assign(kinds, r.seen); } catch (e) { threw = e.message; } }
    ok(!threw, 'rounds=' + rounds + (skill ? ', keen to fight' : '') + ': ' + (threw || 'clean')); console.log('   rounds=' + rounds + (skill ? ', keen to fight' : ', aimless') + ' outcomes ' + JSON.stringify(tally)); });
  const never = Object.keys(C).filter(id => !C[id].dead && !kinds[id]); ok(never.length === 0, 'every card was played somewhere in the fuzz' + (never.length ? ': never ' + never.join(', ') : ''));
  const a = fuzzOne(42, 1, 1).o, b = fuzzOne(42, 1, 1).o; eq(a, b, 'the same seed and the same choices give the same game'); }

console.log('15. bots: is it winnable, is it losable, does anything stall');
{ const { measure } = require('./bots.js');
  [[1, 'fair'], [1, 'rush'], [3, 'fair'], [3, 'rush']].forEach(([rounds, kind]) => { const m = measure(rounds, kind, 300), name = kind + ', ' + (rounds === 1 ? 'one hand' : 'three rounds');
    ok(m.stalled === 0, name + ': no run stalls'); ok(kind === 'rush' ? m.won <= 60 : (m.won >= 10 && m.won <= 95), name + (kind === 'rush' ? ': rushing the captain is not the way to win (' : ': winnable and losable (') + m.won + '%)');
    console.log('   ' + name + ': won ' + m.won + '% · lost in battle 1/2/3: ' + m.lostAt.join('/') + ' · turns a battle ' + m.turnsPerBattle.join('/') + ' · hands a run ' + m.handsPerRun + ' · cards bought ' + m.bought + ' · wounds ' + m.wounds + ' · renown ' + m.renown);
    }); const all = measure(1, 'fair', 150, LH.BASE_DECK.concat(LH.POOL)), never = Object.keys(C).filter(id => !C[id].dead && !all.played[id] && !/2$/.test(id)); ok(never.length === 0, 'given every camp card, the sensible bot finds a use for each' + (never.length ? ': never ' + never.join(', ') : '')); }

console.log('\n' + pass + ' passed, ' + fail + ' failed');
process.exit(fail ? 1 : 0);
