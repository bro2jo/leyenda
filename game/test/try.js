/* One balance setting, measured with the look-ahead player: node game/test/try.js '{"armor":2}' [runs] [rounds] [level] */
const P = require('./playtest.js'), LH = require('../src/engine.js').LH;
const cfg = JSON.parse(process.argv[2] || '{}'), N = +process.argv[3] || 80, rounds = +process.argv[4] || 1, level = +process.argv[5] || 0;
Object.assign(LH.T, cfg); const m = P.measure(N, { rounds, level }), S = m.S;
const dCards = ['strike', 'guard', 'seated', 'hammer', 'still', 'ground', 'over', 'far', 'hand', 'eye', 'road', 'breath', 'mender'].concat(LH.POOL).reduce((n, id) => n + (S.played[id] || 0), 0) / N;
const camp = LH.POOL.reduce((n, id) => n + (S.played[id] || 0), 0) / N, all = Object.keys(S.played).reduce((n, id) => n + S.played[id], 0) / N;
console.log((JSON.stringify(cfg) + ' r' + rounds + ' level ' + level + ' n' + N).padEnd(40), 'won', m.won + '%', 'lost', m.lostAt.join('/'), '| hp after', [1, 2, 3].map(b => m.tn[b] ? Math.round(S.hpAfter[b] / m.tn[b]) : '-').join('/'), '| Darrow plays', dCards.toFixed(0), 'of', all.toFixed(0), 'cards a run (' + Math.round(100 * dCards / all) + '%), camp cards', camp.toFixed(1), '| D takes ans/turn', Math.round(S.dAns / N) + '/' + Math.round(S.dEnemy / N), '| turns', [1, 2, 3].map(b => m.tn[b] ? (S.turns[b] / m.tn[b]).toFixed(1) : '-').join('/'));
