/* Try balance settings against both test players: node game/test/sweep.js */
const B = require('./bots.js'), P = require('./playtest.js'), LH = require('../src/engine.js').LH;
const base = Object.assign({}, LH.T), NE = +process.argv[2] || 60;
const cfgs = [ { ansD: 2, foeAtk: -2 }, { ansD: 2, foeAtk: -2, rest: 10 }, { ansD: 1, foeAtk: -2 } ];
cfgs.forEach(c => { Object.assign(LH.T, base, c);
  const e = P.measure(NE, {}), f = B.measure(1, 'fair', 200), r = B.measure(1, 'rush', 200), S = e.S;
  const dp = ['strike', 'guard', 'seated', 'hammer', 'still', 'ground', 'over', 'far', 'hand'].reduce((n, id) => n + (S.played[id] || 0), 0) / NE;
  console.log(JSON.stringify(c).padEnd(30), '| D takes ans/turn', Math.round(S.dAns / NE) + '/' + Math.round(S.dEnemy / NE), 'D cards', dp.toFixed(0), 'blocked', Math.round(100 * S.blockedAll / S.answered) + '%', '| look-ahead', e.won + '%', 'lost', e.lostAt.join('/'), 'stall', e.stalled, 'hp after', [1, 2, 3].map(b => e.tn[b] ? Math.round(S.hpAfter[b] / e.tn[b]) : '-').join('/'), 'turns', [1, 2, 3].map(b => e.tn[b] ? (S.turns[b] / e.tn[b]).toFixed(1) : '-').join('/'), '| sensible', f.won + '%', f.lostAt.join('/'), '| rush', r.won + '%'); });
