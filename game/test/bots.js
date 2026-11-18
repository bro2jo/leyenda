/* Bots for measuring balance. rush: go for the captain. fair: a sensible player who fights what is in front of him. */
const LH = require('../src/engine.js').LH, C = LH.C;
const WANT = ['bloodup', 'steady', 'digin', 'secondwind', 'hewT', 'follow', 'finish', 'twice', 'closeup', 'pinshot', 'callco', 'strip', 'readline', 'bellow', 'stitch', 'bandage', 'legs', 'spoils'];
function cardScore(G, K, id) { const c = C[id]; let s = 0;
  const it = LH.intent(G), need = it.none ? 0 : Math.max(0, it.d * it.n - K.block), wantBreak = K.canBreak && !K.broken && K.p.can;
  if (c.stance) s += 70; if (c.en || c.draw) s += 60; if (c.spoil) s += 30; if (c.open && !K.open) s += 45;
  if (c.dmg) { const tot = LH.hitList(K, c).reduce((a, b) => a + b, 0), thru = c.pierce ? tot : Math.max(0, tot - K.fb); s += 12 + tot / (c.c + .5); if (wantBreak && thru > 0) s += 40; if (K.d.hp <= thru) s += 80; if (thru === 0) s -= 14; }
  if (c.assist) s += K.p.lend.length ? 10 + 6 * K.p.lend.length : -20;
  if (c.halve) s += need > 0 && !wantBreak ? 35 : -5;
  if (c.blk) s += (need > 0 && !wantBreak) ? 28 + Math.min(c.blk, need) : (K.a.id === 'D' ? 6 : 2);
  if (c.heal) s += K.a.hp <= K.a.max - c.heal ? 22 : (c.cleanse && LH.wounds(K.a) + K.hand.filter(x => x === 'wound').length ? 15 : -5);
  if (c.mark) s += 8; if (c.pin && !c.dmg) s += 6; return s; }
function clash(G, st) { const K = G.clash; let n = 0;
  while (G.clash && n++ < 400) {
    if (K.phase === 'play') {
      const can = K.hand.map((_, i) => i).filter(i => !LH.playable(G, i));
      if (!can.length) { st.hands++; LH.endHand(G); continue; }
      can.sort((x, y) => cardScore(G, K, K.hand[y]) - cardScore(G, K, K.hand[x]));
      if (cardScore(G, K, K.hand[can[0]]) <= 0) { st.hands++; LH.endHand(G); } else { st.played[K.hand[can[0]]] = (st.played[K.hand[can[0]]] || 0) + 1; LH.play(G, can[0]); }
    } else if (K.phase === 'choice') { const ni = LH.nextIntent(G); if (K.a.hp > ni.d * ni.n * 2 + 4) LH.pressOn(G); else LH.leave(G); }
    else { if (K.a.id === 'D') st.dAns += K.taken; LH.closeClash(G); }
  } }
function camp(G, st, kind) { let n = 0; const D = G.u[0];
  while (n++ < 20) {
    if (D.hp <= 36 && LH.campMend(G)) { st.mends++; continue; }
    const pick = WANT.filter(id => G.camp.market.indexOf(id) >= 0 && C[id].p <= G.run.spoils)[0];
    if (pick && LH.campBuy(G, pick)) { st.bought.push(pick); continue; }
    if (kind === 'fair' && G.run.spoils >= LH.T.honeCost && LH.campHone(G, 'strike')) { st.hones++; continue; }
    break; }
  LH.nextBattle(G); }
function run(seed, rounds, kind, deck) {
  const G = LH.newRun({ seed, rounds, deck }), st = { hands: 0, played: {}, dAns: 0, dEnemy: 0, fell: 0, wounds: 0, bought: [], mends: 0, hones: 0, spoils: 0, turns: [0, 0, 0, 0] }; let guard = 0;
  while (guard++ < 5000) {
    if (G.over) { st.turns[G.run.n] = G.turn; if (G.over.win) { camp(G, st, kind); continue; } break; }
    if (G.phase === 'enemy') { const ev = LH.enemyStep(G); if (ev && ev.k === 'foe') { if (ev.target === 'D') st.dEnemy += ev.dmg; if (ev.targetDown) st.fell++; if (ev.wound) st.wounds++; } continue; }
    const order = kind === 'fair' ? ['W', 'A', 'H', 'D'] : ['D', 'H', 'A', 'W'];
    { // Rae: get beside whoever is most hurt, out of reach of the foe if she can, and tend; else stay near Darrow
      const R = LH.byId(G, 'R'); if (R && LH.canAct(R)) { const dz = LH.dangerSet(G), mates = LH.matesUp(G).filter(m => m !== R), D = G.u[0];
        if (!LH.tendTargets(G, R).length && !R.moved) { const r = LH.reach(G, R); let best = null, bs = -1e9;
          Object.keys(r).forEach(k => { const p = k.split(','), px = +p[0], py = +p[1]; let s = dz[k] ? -30 : 0;
            mates.forEach(m => { if (Math.abs(m.x - px) + Math.abs(m.y - py) === 1) s += 4 + (m.max - m.hp) * 1.2 + LH.wounds(m) * 6 + (m.id === 'D' ? 5 : 0); });
            s -= (Math.abs(D.x - px) + Math.abs(D.y - py)) * 1.5; if (s > bs) { bs = s; best = p; } });
          if (best && (+best[0] !== R.x || +best[1] !== R.y)) LH.move(G, R, +best[0], +best[1]); }
        const tt = LH.tendTargets(G, R).sort((a, b) => (b.max - b.hp + LH.wounds(b) * 6) - (a.max - a.hp + LH.wounds(a) * 6));
        if (tt.length && (tt[0].max - tt[0].hp >= 4 || LH.wounds(tt[0]))) { LH.tend(G, R, tt[0]); st.tends = (st.tends || 0) + 1; } else LH.hold(G, R); } }
    order.map(id => LH.byId(G, id)).forEach(u => { let n = 0;
      while (!G.over && LH.canAct(u) && n++ < 4) {
        const dz = LH.dangerSet(G), r = u.moved ? { [u.x + ',' + u.y]: 0 } : LH.reach(G, u), foes = LH.foesUp(G), mates = LH.matesUp(G); let best = null, bs = -1e9;
        Object.keys(r).forEach(k => { const p = k.split(','), px = +p[0], py = +p[1];
          const adj = mates.filter(m => m !== u && Math.abs(m.x - px) + Math.abs(m.y - py) === 1).length;
          const risk = dz[k] ? (u.id === 'W' || u.id === 'A' ? 14 : u.hp < 25 ? 16 : 4) : 0;
          if (!u.attacked) foes.forEach(f => { const d = Math.abs(f.x - px) + Math.abs(f.y - py); if (d < 1 || d > (u.throws > 0 ? 2 : u.rng)) return;
            const t = LH.tri(u, f), canAns = d <= f.rng, a0 = f.ans[f.ai % f.ans.length], ans = a0.d * a0.n; let s = 20 + t * 28 + adj * 6 - risk + (f.fought ? 14 : 0) + (f.hp <= 12 ? 18 : 0) + (f.rally ? 16 : 0) - (f.tough ? 6 : 0) - (canAns && t <= 0 ? ans * (u.hp < ans + 8 ? 4 : .9) : 0);
            if (kind === 'rush') s += f.boss ? 200 : 0; else s += f.boss ? (foes.length <= 2 ? 30 : 4) : 0;
            if (s > bs) { bs = s; best = { px, py, f }; } });
          let tgt = foes; if (kind === 'rush') tgt = tgt.filter(f => f.boss);
          const near = Math.min.apply(null, tgt.map(f => Math.abs(f.x - px) + Math.abs(f.y - py)));
          const s0 = (kind === 'rush' ? -near * 6 : -near * 2 + adj * 5 - risk * 1.5) - 6; if (s0 > bs) { bs = s0; best = { px, py, f: null }; } });
        if (!best) break;
        if (best.px !== u.x || best.py !== u.y) { if (!LH.move(G, u, best.px, best.py)) break; }
        if (best.f && !u.attacked) { if (!LH.engage(G, u, best.f)) break; clash(G, st); } else { if (!u.attacked) LH.hold(G, u); break; }
      } });
    if (!G.over) LH.endTurn(G);
  }
  st.spoils = G.run.spoils; st.renown = G.run.renown;
  return { out: G.over ? (G.over.done ? 'won' : 'lost') : 'stalled', at: G.run.n, st, G };
}
function measure(rounds, kind, N, deck) { let won = 0, lostAt = [0, 0, 0, 0], stalled = 0, hands = 0, dAns = 0, dEn = 0, fell = 0, wounds = 0, ren = 0, bought = 0, t = [0, 0, 0, 0], tn = [0, 0, 0, 0]; const played = {};
  for (let s = 1; s <= N; s++) { const r = run(s * 31 + 5, rounds, kind, deck); if (r.out === 'won') won++; else if (r.out === 'lost') lostAt[r.at]++; else stalled++; hands += r.st.hands; dAns += r.st.dAns; dEn += r.st.dEnemy; fell += r.st.fell; wounds += r.st.wounds; ren += r.st.renown || 0; bought += r.st.bought.length;
    Object.keys(r.st.played).forEach(k => played[k] = (played[k] || 0) + r.st.played[k]); for (let b = 1; b <= 3; b++) if (r.st.turns[b]) { t[b] += r.st.turns[b]; tn[b]++; } }
  return { won: Math.round(100 * won / N), lostAt: lostAt.slice(1), stalled, handsPerRun: +(hands / N).toFixed(1), darrowFromAnswers: +(dAns / N).toFixed(0), darrowFromEnemyTurn: +(dEn / N).toFixed(0), companionsFell: +(fell / N).toFixed(1), wounds: +(wounds / N).toFixed(1), renown: +(ren / N).toFixed(0), bought: +(bought / N).toFixed(1), turnsPerBattle: [1, 2, 3].map(b => tn[b] ? +(t[b] / tn[b]).toFixed(1) : 0), played }; }
module.exports = { run, measure, cardScore };
if (require.main === module) { const N = +process.argv[2] || 300;
  [['fair', 1], ['rush', 1], ['fair', 3], ['rush', 3]].forEach(([k, r]) => { const m = measure(r, k, N), pl = m.played; delete m.played; console.log(k + ' rounds=' + r, JSON.stringify(m)); if (k === 'fair' && r === 1) console.log('  never played:', Object.keys(C).filter(id => !C[id].dead && !pl[id] && !/2$/.test(id)).join(', ') || 'none'); }); }
