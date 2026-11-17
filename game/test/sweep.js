/* Try balance settings against the bots: node game/test/sweep.js */
const { measure } = require('./bots.js'); const LH = require('../src/engine.js').LH;
const N = 160, base = Object.assign({}, LH.T);
const cfgs = [
  { tend: 4, rest: 4, scaleHp: .2, foeAtk: 1 }, { tend: 5, rest: 6, scaleAtk: 2 }, { tend: 5, rest: 4, foeAtk: 1, scaleHp: .15 }, { tend: 5, rest: 6, foeAtk: 1, scaleHp: .2 },
];
cfgs.forEach(c => { Object.assign(LH.T, base, c);
  const f = measure(1, 'fair', N), r = measure(1, 'rush', N), f3 = measure(3, 'fair', N);
  console.log(JSON.stringify(c), '| fair', f.won + '%', 'lost', f.lostAt.join('/'), 'turns', f.turnsPerBattle.join('/'), 'fell', f.companionsFell, '| rush', r.won + '%', '| fair3', f3.won + '%'); });
