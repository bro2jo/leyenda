/* Counts what is rebuilt on screen during ordinary actions. A card or a token that is thrown away and made again
   flashes: its picture has to be decoded again. Run after a build: node game/test/flicker.js */
const { chromium } = require('playwright');
const fs = require('fs');
const dir = __dirname + '/../dist/';
(async () => {
  fs.writeFileSync(dir + '_probe.html', '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><script>window.LH_SEED=11</script></head><body>' + fs.readFileSync(dir + 'line-and-hand.html', 'utf8') + '</body></html>');
  const b = await chromium.launch(), p = await (await b.newContext({ viewport: { width: 400, height: 860 }, hasTouch: true })).newPage();
  await p.goto('file://' + dir + '_probe.html'); await p.waitForTimeout(700);
  const idle = () => p.waitForFunction(() => document.getElementById('game').getAttribute('data-busy') === '0');
  const count = async (label, fn) => { await p.evaluate(() => { window.__made = { cards: 0, imgs: 0, toks: 0 }; window.__obs = new MutationObserver(ms => ms.forEach(m => m.addedNodes.forEach(n => { if (n.nodeType !== 1) return; const all = [n].concat(Array.from(n.querySelectorAll('*'))); all.forEach(e => { if (e.classList.contains('hcard') && !e.classList.contains('ghost')) window.__made.cards++; if (e.tagName === 'IMG') window.__made.imgs++; if (e.classList.contains('tok')) window.__made.toks++; }); }))); window.__obs.observe(document.getElementById('game'), { childList: true, subtree: true }); });
    await fn(); await idle(); await p.waitForTimeout(500); const r = await p.evaluate(() => { window.__obs.disconnect(); return window.__made; }); console.log(label.padEnd(44) + JSON.stringify(r)); return r; };
  const T = (x, y) => `#game .tile[data-x="${x}"][data-y="${y}"]`;
  await count('tap Darrow on the map', () => p.tap(T(2, 4)));
  await count('move Darrow one tile', () => p.tap(T(3, 4)));
  await p.tap(T(3, 4)); await p.tap(T(2, 4)).catch(() => { }); await p.evaluate(() => { const g = window.__LH.G; g.u[0].x = 2; g.u[0].y = 4; g.u[0].moved = false; }); await p.tap(T(0, 6)); await p.tap(T(2, 4)); await p.tap(T(2, 2)); await p.tap('#game [data-a="go"]'); await idle(); await p.waitForTimeout(900);
  const i = await p.evaluate(() => { const g = window.__LH.G, LH = window.__LH.LH; return g.clash.hand.findIndex((id, i) => !LH.playable(g, i) && LH.C[id].dmg && !LH.C[id].draw); });
  await count('lift a card', () => p.tap(`#game .hcard[data-i="${i}"]`, { position: { x: 14, y: 40 } }));
  await count('play it (no draw)', () => p.tap(`#game .hcard[data-i="${i}"]`, { position: { x: 14, y: 40 } }));
  const j = await p.evaluate(() => { const g = window.__LH.G, LH = window.__LH.LH; return g.clash.hand.findIndex((id, i) => !LH.playable(g, i) && LH.C[id].draw); });
  if (j >= 0) { await p.tap(`#game .hcard[data-i="${j}"]`, { position: { x: 14, y: 40 } }); await count('play a card that draws', () => p.tap(`#game .hcard[data-i="${j}"]`, { position: { x: 14, y: 40 } })); }
  await b.close();
})();
