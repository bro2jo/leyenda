/* A stronger test player, and what it sees. It looks ahead: for each fighter it tries the fights on offer, plays each
   hand out several ways on a copy of the game, and keeps the best. Used to find what is too strong, too weak or never used.

   node game/test/playtest.js            a report: win rates, where runs are lost, how hands are played, every card and foe
   node game/test/playtest.js cards      what each camp card is worth: win rate with it in the deck from the start, against without
   node game/test/playtest.js N          the report over N runs (default 300)
*/
const LH = require('../src/engine.js').LH, C = LH.C, T = LH.T;

/* a copy of the game that can be played forward without touching the real one */
function clone(G) {
  const u = G.u.map(o => { const c = Object.assign({}, o); c.st = Object.assign({}, o.st); if (o.dk) c.dk = { draw: o.dk.draw.slice(), disc: o.dk.disc.slice(), gone: o.dk.gone.slice() }; return c; });
  const H = Object.assign({}, G, { u, run: Object.assign({}, G.run, { deck: G.run.deck.slice() }), log: G.log.slice(), camp: G.camp ? { market: G.camp.market.slice(), bought: G.camp.bought.slice() } : null });
  if (G.clash) { const K = G.clash, at = o => u[G.u.indexOf(o)];
    H.clash = Object.assign({}, K, { a: at(K.a), d: at(K.d), p: Object.assign({}, K.p, { lend: K.p.lend.map(at) }), hand: K.hand.slice(), intent: Object.assign({}, K.intent), lines: K.lines.slice() }); }
  return H;
}
/* how good a position is for the company: their health and his, weighted, less what the foe can do next turn */
const memo = new Map();
function threat(G) { // for each of the company, the damage they should expect on the enemy's turn
  const key = G.turn + '|' + G.u.map(u => u.hp > 0 ? u.id + u.x + u.y + (u.side ? (u.pinned ? 'p' : '') + (LH.enraged(u) ? 'e' : '') : (u.hp < 12 ? 'l' + u.hp : '')) : '').join(''); const hit = memo.get(key); if (hit) return hit; if (memo.size > 4000) memo.clear();
  const mates = LH.matesUp(G), out = {}; mates.forEach(m => out[m.id] = 0);
  LH.foesUp(G).forEach(e => { if (LH.holding(G, e)) return; const r = e.pinned ? {} : LH.reach(G, e); r[e.x + ',' + e.y] = 0; const can = [];
    mates.forEach(m => { for (const k in r) { const p = k.split(','), d = Math.abs(m.x - p[0]) + Math.abs(m.y - p[1]); if (d >= 1 && d <= e.rng) { can.push(m); break; } } });
    if (!can.length) return; can.sort((a, b) => a.hp - b.hp); const t = can[0], atk = e.atk + (LH.rallied(G, e) ? T.rally : 0) + (LH.enraged(e) ? e.enrage : 0) + LH.tri(e, t) * 2;
    out[t.id] += atk; });
  memo.set(key, out); return out;
}
function value(G) {
  if (G.over) return G.over.lost ? -5000 : 3000 + G.u[0].hp * 3 + G.run.spoils * 4;
  let v = 0; const th = threat(G);
  G.u.forEach(u => {
    if (u.side === 1) { if (u.hp > 0) v -= u.hp * 1.1 + (u.boss ? 40 : 14) + (u.rally ? 10 : 0); else v += 0; if (u.hp > 0 && u.pinned) v += 5; if (u.hp > 0 && u.marked) v += 3; }
    else { const w = u.id === 'D' ? 2.2 : u.id === 'R' ? 1 : .8; if (u.hp <= 0) { v -= u.id === 'D' ? 5000 : 30; return; }
      const hit = Math.max(0, (th[u.id] || 0) - u.guard), left = u.hp - hit; v += u.hp * w - hit * w * 1.1 - (left <= 0 ? (u.id === 'D' ? 3000 : 28) : 0) + Math.min(u.guard, th[u.id] || 0) * .3 + u.bank * 1.5 - LH.wounds(u) * 5;
      v += (u.st.blockStart + u.st.atkUp * 2 + u.st.drawUp * 3) * 4; }
  });
  return v + G.run.spoils * 3;
}
function cheap(G, K, id) { const c = C[id]; let s = 0; if (c.stance) s += 50; if (c.en || c.draw) s += 40; if (c.dmg) s += 10 + LH.hitList(K, c).reduce((a, b) => a + b, 0); if (c.assist) s += 4 * K.p.lend.length; if (c.open) s += 9; if (c.blk) s += c.blk * .8; if (c.heal) s += 4; if (c.halve) s += 6; if (c.ex) s -= 2; return s; }
/* play the hand out on copies, a few of the likeliest cards at each step, and return the best line */
function bestHand(G, depth, budget) {
  budget = budget || { n: 0 }; let best = { v: -1e9, line: [] };
  (function go(S, line) {
    if (budget.n++ > 70) return; const K = S.clash;
    { const E = clone(S); LH.endHand(E); let v; // stopping here
      if (E.clash && E.clash.phase === 'choice') { const L = clone(E); LH.leave(L); LH.closeClash(L); v = value(L);
        if ((depth || 0) < 2 && E.clash.a.hp > 12) { const P = clone(E); LH.pressOn(P); const r = bestHand(P, (depth || 0) + 1, { n: 0 }); if (r.v > v + 2) { v = r.v; line = line.concat(['press']); } } }
      else { LH.closeClash(E); v = value(E); }
      v -= line.filter(x => x !== 'press' && C[x] && C[x].ex && !C[x].stance).length * 1.5; if (v > best.v) best = { v, line: line.slice() }; }
    const can = K.hand.map((id, i) => i).filter(i => !LH.playable(S, i)); if (!can.length || line.length > 9) return;
    const seen = {}; can.sort((x, y) => cheap(S, K, K.hand[y]) - cheap(S, K, K.hand[x]));
    let tried = 0; for (const i of can) { const id = K.hand[i]; if (seen[id]) continue; seen[id] = 1; if (tried++ >= (line.length < 2 ? 3 : 2)) break;
      const N = clone(S); LH.play(N, i); if (!N.clash || N.clash.phase !== 'play') { LH.closeClash(N); const v = value(N) + 8; if (v > best.v) best = { v, line: line.concat([id]) }; continue; }
      go(N, line.concat([id])); }
  })(G, []);
  return best;
}
function playHand(G, st) { // play the line the search chose, on the real game
  let guard = 0;
  while (G.clash && guard++ < 40) { const K = G.clash;
    if (K.phase === 'play') { const r = bestHand(G, K.round - 1); const line = r.line; let played = 0, pressed = false;
      for (const id of line) { if (id === 'press') { pressed = true; break; } const i = K.hand.indexOf(id); if (i < 0 || LH.playable(G, i)) break; st.note(K, id); LH.play(G, i); played++; if (!G.clash || G.clash.phase !== 'play') break; }
      if (G.clash && G.clash.phase === 'play') { st.hand(G, K, played); LH.endHand(G); if (G.clash && G.clash.phase === 'choice') { if (pressed) LH.pressOn(G); else LH.leave(G); } } }
    else if (K.phase === 'choice') LH.leave(G);
    else { st.clash(K); LH.closeClash(G); } }
}
function turn(G, st) {
  const order = ['W', 'A', 'H', 'D'];
  for (let pass = 0; pass < 2; pass++) for (const id of order) { const u = LH.byId(G, id); let n = 0;
    while (!G.over && u && LH.canAct(u) && n++ < 3) {
      const r = u.moved ? { [u.x + ',' + u.y]: 0 } : LH.reach(G, u), base = value(G); let best = { v: base - 1e-6, f: null }, tried = 0;
      const opts = [];
      if (!u.attacked) LH.foesUp(G).forEach(f => { const tiles = Object.keys(r).map(k => k.split(',').map(Number)).filter(p => { const d = Math.abs(f.x - p[0]) + Math.abs(f.y - p[1]); return d >= 1 && d <= (u.throws > 0 ? 2 : u.rng); });
        tiles.map(p => ({ p, s: LH.matesUp(G).filter(m => m !== u && Math.abs(m.x - p[0]) + Math.abs(m.y - p[1]) === 1).length * 3 + (LH.ter(G, p[0], p[1]) === 'w' ? 2 : 0) - r[p[0] + ',' + p[1]] * .2 + (Math.abs(f.x - p[0]) + Math.abs(f.y - p[1]) > f.rng ? 4 : 0) }))
          .sort((a, b) => b.s - a.s).slice(0, 2).forEach(t => opts.push({ p: t.p, f })); });
      for (const o of opts) { if (tried++ > 5) break; const S = clone(G), su = LH.byId(S, id); if ((o.p[0] !== su.x || o.p[1] !== su.y) && !LH.move(S, su, o.p[0], o.p[1])) continue; if (!LH.engage(S, su, LH.byId(S, o.f.id))) continue;
        const res = bestHand(S, 0); if (res.v > best.v) best = { v: res.v, p: o.p, f: o.f }; }
      // not fighting: the best place to stand, held
      { const ox = u.x, oy = u.y, og = u.guard, fs = LH.foesUp(G);
        Object.keys(r).forEach(k => { const p = k.split(',').map(Number); u.x = p[0]; u.y = p[1]; if (!u.attacked) u.guard = og + 4;
          const near = Math.min.apply(null, fs.map(f => Math.abs(f.x - p[0]) + Math.abs(f.y - p[1]))); const v = value(G) - near * .9 - 3; if (v > best.v) best = { v, p, f: null }; });
        u.x = ox; u.y = oy; u.guard = og; }
      if (!best.p) break;
      if (best.p[0] !== u.x || best.p[1] !== u.y) { if (!LH.move(G, u, best.p[0], best.p[1])) break; }
      if (best.f && !u.attacked) { if (!LH.engage(G, u, best.f)) break; st.engage(G); playHand(G, st); } else { if (!u.attacked) LH.hold(G, u); break; }
    } }
  // Rae: beside whoever needs her most, out of reach if she can be
  const R = LH.byId(G, 'R'); if (R && LH.canAct(R) && !G.over) { const dz = LH.dangerSet(G), mates = LH.matesUp(G).filter(m => m !== R), D = G.u[0];
    if (!LH.tendTargets(G, R).length && !R.moved) { const r = LH.reach(G, R); let best = null, bs = -1e9;
      Object.keys(r).forEach(k => { const p = k.split(',').map(Number); let s = dz[k] ? -30 : 0; mates.forEach(m => { if (Math.abs(m.x - p[0]) + Math.abs(m.y - p[1]) === 1) s += 4 + (R.tends ? (m.max - m.hp) * 1.2 + LH.wounds(m) * 6 : 0) + (m.id === 'D' ? 6 : 0); });
        s -= (Math.abs(D.x - p[0]) + Math.abs(D.y - p[1])) * 1.5; if (s > bs) { bs = s; best = p; } });
      if (best && (best[0] !== R.x || best[1] !== R.y)) LH.move(G, R, best[0], best[1]); }
    const tt = LH.tendTargets(G, R).sort((a, b) => (b.max - b.hp + LH.wounds(b) * 6) - (a.max - a.hp + LH.wounds(a) * 6));
    if (tt.length && (tt[0].max - tt[0].hp >= T.tend || LH.wounds(tt[0]))) { LH.tend(G, R, tt[0]); st.s.tends++; } else LH.hold(G, R); }
}
const WANT = ['bloodup', 'steady', 'digin', 'secondwind', 'hewT', 'follow', 'finish', 'twice', 'closeup', 'pinshot', 'callco', 'strip', 'readline', 'bellow', 'stitch', 'bandage', 'legs', 'spoils'];
function camp(G, st, policy) { const D = G.u[0]; let n = 0;
  while (n++ < 20) { if (policy === 'none') break;
    if (D.hp <= 34 && LH.campMend(G)) { st.s.mends++; continue; }
    const pick = WANT.filter(id => G.camp.market.indexOf(id) >= 0 && C[id].p <= G.run.spoils)[0];
    if (pick && LH.campBuy(G, pick)) { st.s.bought[pick] = (st.s.bought[pick] || 0) + 1; continue; }
    if (G.run.spoils >= T.honeCost && LH.campHone(G, 'strike')) { st.s.hones++; continue; }
    if (D.hp < 50 && LH.campMend(G)) { st.s.mends++; continue; }
    break; }
  st.s.spoilsKept[G.run.n] = G.run.spoils; LH.nextBattle(G); }
function stats() { const s = { hands: 0, clashes: 0, played: {}, kinds: { Attack: 0, Skill: 0, Stance: 0 }, cardsPerHand: 0, breathLeft: 0, handsWithBreathLeft: 0, handsLeftPlayable: 0, noAnswer: 0, answered: 0, blockedAll: 0, tookDmg: 0, dAns: 0, dEnemy: 0, byFoe: {}, fell: {}, wounds: 0, tends: 0, mends: 0, hones: 0, bought: {}, spoilsKept: {}, turns: {}, hpAfter: {}, ripostes: 0, broken: 0 };
  return { s,
    engage() { s.clashes++; },
    note(K, id) { s.played[id] = (s.played[id] || 0) + 1; s.kinds[C[id].k] = (s.kinds[C[id].k] || 0) + 1; s.cardsPerHand++; },
    hand(G, K, played) { s.hands++; if (K.en > 0) { s.handsWithBreathLeft++; s.breathLeft += K.en; } if (K.hand.some((_, i) => !LH.playable(G, i))) s.handsLeftPlayable++; const it = LH.intent(G); if (it.none) s.noAnswer++; else { s.answered++; if (it.broken) s.broken++; if (K.block >= it.d * it.n) s.blockedAll++; } },
    clash(K) { if (K.a.id === 'D') s.dAns += K.taken; if (K.taken > 0) s.tookDmg++; } }; }
function run(seed, opts) { opts = opts || {};
  const G = LH.newRun({ seed, rounds: opts.rounds || 1, deck: opts.deck, level: opts.level || 0 }), st = stats(), s = st.s; let guard = 0;
  while (guard++ < 400) {
    if (G.over) { s.turns[G.run.n] = G.turn; s.hpAfter[G.run.n] = G.u[0].hp; if (G.over.win) { camp(G, st, opts.camp); continue; } break; }
    if (G.phase === 'enemy') { const ev = LH.enemyStep(G); if (ev && ev.k === 'foe' && ev.target) { const e = LH.byId(G, ev.id), key = e.n; s.byFoe[key] = (s.byFoe[key] || 0) + ev.dmg; if (ev.target === 'D') s.dEnemy += ev.dmg; if (ev.targetDown) s.fell[ev.target] = (s.fell[ev.target] || 0) + 1; if (ev.wound) s.wounds++; if (ev.rip) s.ripostes++; } continue; }
    turn(G, st); if (!G.over) LH.endTurn(G);
  }
  return { out: G.over ? (G.over.done ? 'won' : 'lost') : 'stalled', at: G.run.n, s, renown: G.run.renown, G };
}
function measure(N, opts) { const agg = { won: 0, lostAt: [0, 0, 0, 0], stalled: 0, renown: 0 }, S = stats().s, sum = (a, b) => { for (const k in b) { if (typeof b[k] === 'number') a[k] = (a[k] || 0) + b[k]; else if (b[k] && typeof b[k] === 'object') { a[k] = a[k] || {}; sum(a[k], b[k]); } } };
  const tn = {}; for (let i = 1; i <= N; i++) { const r = run(i * 37 + 11, opts); if (r.out === 'won') agg.won++; else if (r.out === 'lost') agg.lostAt[r.at]++; else agg.stalled++; agg.renown += r.renown || 0; sum(S, r.s); for (const b in r.s.turns) tn[b] = (tn[b] || 0) + 1; }
  return { N, won: Math.round(100 * agg.won / N), lostAt: agg.lostAt.slice(1), stalled: agg.stalled, renown: +(agg.renown / N).toFixed(0), S, tn };
}
module.exports = { run, measure, clone, bestHand, value };

if (require.main === module) {
  const arg = process.argv[2], pct = (a, b) => b ? Math.round(100 * a / b) + '%' : '-', per = (a, n) => +(a / n).toFixed(1);
  if (arg === 'cards') { const N = +process.argv[3] || 150, base = measure(N, { camp: 'none' });
    console.log('What each card is worth to the look-ahead player: runs won with it in the deck from the start, no camp, against ' + base.won + '% without (' + N + ' runs each).');
    const rows = LH.POOL.map(id => { const m = measure(N, { camp: 'none', deck: LH.BASE_DECK.concat([id]) }); return { id, n: C[id].n, p: C[id].p, won: m.won, d: m.won - base.won, plays: per(m.S.played[id] || 0, N) }; }).sort((a, b) => b.d - a.d);
    rows.forEach(r => console.log('  ' + (r.d >= 0 ? '+' : '') + r.d + '  ' + r.n.padEnd(20) + ' price ' + r.p + ' · won ' + r.won + '% · played ' + r.plays + ' a run'));
    const cut = ['strike', 'guard', 'seated', 'hammer', 'still', 'breath', 'mender', 'eye', 'ground', 'road', 'hand', 'over', 'far'].map(id => { const d = LH.BASE_DECK.slice(); d.splice(d.indexOf(id), 1); const m = measure(N, { camp: 'none', deck: d }); return { n: C[id].n, d: m.won - base.won }; }).sort((a, b) => a.d - b.d);
    console.log('What each of his own cards is worth: the change in runs won when one copy is taken out.'); cut.forEach(r => console.log('  ' + (r.d >= 0 ? '+' : '') + r.d + '  ' + r.n));
  } else { const N = +arg || 300;
    [[1, 0, 'one hand'], [3, 0, 'three rounds'], [1, -1, 'one hand, gentle'], [1, 1, 'one hand, hard']].forEach(([rounds, level, name], idx) => { const m = measure(idx ? Math.round(N / 2) : N, { rounds, level }), S = m.S, n = m.N;
      console.log('\n== ' + name + ' · ' + n + ' runs · won ' + m.won + '% · lost in battle 1/2/3: ' + m.lostAt.join('/') + ' · stalled ' + m.stalled + ' · renown ' + m.renown);
      if (idx) return;
      console.log('turns a battle: ' + [1, 2, 3].map(b => m.tn[b] ? per(S.turns[b], m.tn[b]) : '-').join(' / ') + ' · Darrow\'s health after each: ' + [1, 2, 3].map(b => m.tn[b] ? per(S.hpAfter[b], m.tn[b]) : '-').join(' / '));
      console.log('a run: ' + per(S.clashes, n) + ' clashes, ' + per(S.hands, n) + ' hands, ' + per(S.cardsPerHand, S.hands) + ' cards a hand · attacks ' + pct(S.kinds.Attack, S.cardsPerHand) + ', skills ' + pct(S.kinds.Skill, S.cardsPerHand) + ', stances ' + pct(S.kinds.Stance, S.cardsPerHand));
      console.log('hands: breath left over in ' + pct(S.handsWithBreathLeft, S.hands) + ' · a playable card left unplayed in ' + pct(S.handsLeftPlayable, S.hands) + ' · he could not answer in ' + pct(S.noAnswer, S.hands) + ' · of the hands he did answer: Broken (halved) ' + pct(S.broken, S.answered) + ', fully blocked ' + pct(S.blockedAll, S.answered));
      console.log('Darrow takes ' + per(S.dAns, n) + ' from answers and ' + per(S.dEnemy, n) + ' on their turn, a run · guard held and struck back ' + per(S.ripostes, n) + ' times · wounds ' + per(S.wounds, n) + ' · Rae tends ' + per(S.tends, n));
      console.log('damage on their turn by foe: ' + Object.keys(S.byFoe).sort((a, b) => S.byFoe[b] - S.byFoe[a]).map(k => k + ' ' + per(S.byFoe[k], n)).join(', '));
      console.log('fell back, a run: ' + Object.keys(S.fell).map(k => LH.byId(run(1).G, k).n + ' ' + per(S.fell[k], n)).join(', '));
      console.log('camp: bought ' + Object.keys(S.bought).sort((a, b) => S.bought[b] - S.bought[a]).map(k => C[k].n + ' ' + per(S.bought[k], n)).join(', ') + ' · mends ' + per(S.mends, n) + ' · hones ' + per(S.hones, n) + ' · spoils left after camp 1/2: ' + [1, 2].map(b => per(S.spoilsKept[b] || 0, m.tn[b] || 1)).join('/'));
      const pl = Object.keys(C).filter(id => !C[id].dead).map(id => [C[id].n + (C[id].r === 'risen' ? ' (risen)' : C[id].r === 'honed' ? ' (honed)' : ''), per(S.played[id] || 0, n)]).sort((a, b) => b[1] - a[1]);
      console.log('cards played a run: ' + pl.map(x => x[0] + ' ' + x[1]).join(', ')); }); }
}
