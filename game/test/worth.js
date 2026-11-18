/* What each camp card is worth to the look-ahead player, measured on every core at once.
   Each card is put in Darrow's deck from the start, with no camp, and the runs won are compared with the plain deck
   over the same seeds. Hard is the default level: on Standard that player wins too often for a card to show.
     node game/test/worth.js [runs] [level] [rounds]        e.g. node game/test/worth.js 160 1 */
const { fork } = require('child_process'), os = require('os');
const P = require('./playtest.js'), LH = require('../src/engine.js').LH, C = LH.C;
const N = +process.argv[2] || 160, level = process.argv[3] === undefined ? 1 : +process.argv[3], rounds = +process.argv[4] || 1;
const OWN = ['hammer', 'strike', 'guard', 'seated', 'eye'];
if (process.send) {
  process.on('message', job => {
    let deck = LH.BASE_DECK.slice();
    if (job.add) deck.push(job.add); if (job.cut) deck.splice(deck.indexOf(job.cut), 1);
    const m = P.measure(N, { camp: 'none', level, rounds, deck });
    process.send({ job, won: m.won, plays: job.add ? +((m.S.played[job.add] || 0) / N).toFixed(1) : 0 });
  });
} else {
  const jobs = [{}].concat(LH.POOL.map(id => ({ add: id })), OWN.map(id => ({ cut: id }))), out = [], k = Math.min(os.cpus().length, jobs.length);
  let live = 0;
  for (let i = 0; i < k; i++) {
    const w = fork(__filename, process.argv.slice(2)); live++;
    const next = () => { const j = jobs.shift(); if (j) w.send(j); else { w.kill(); if (!--live) report(); } };
    w.on('message', r => { out.push(r); next(); }); next();
  }
  function report() {
    const base = out.filter(r => !r.job.add && !r.job.cut)[0].won, sign = d => (d >= 0 ? '+' : '') + d;
    console.log('Runs won by the look-ahead player with no camp, level ' + level + ', ' + rounds + ' round(s), ' + N + ' runs each. The plain deck wins ' + base + '%.');
    console.log('With one copy added from the start:');
    out.filter(r => r.job.add).sort((a, b) => b.won - a.won).forEach(r => console.log('  ' + sign(r.won - base).padStart(4) + '  ' + C[r.job.add].n.padEnd(20) + ' price ' + C[r.job.add].p + ' · played ' + r.plays + ' a run'));
    console.log('With one copy of his own card taken out:');
    out.filter(r => r.job.cut).sort((a, b) => a.won - b.won).forEach(r => console.log('  ' + sign(r.won - base).padStart(4) + '  ' + C[r.job.cut].n));
  }
}
