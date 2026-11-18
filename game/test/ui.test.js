/* Screen tests: the real page in a browser, with real animations for the hand-played parts and a fast mode for whole runs. */
const { chromium } = require('playwright');
const fs = require('fs');
const LH = require('../src/engine.js').LH;
const dir = __dirname + '/../dist/bench/';   // python3 game/build.py first
const page0 = fs.readFileSync(dir + 'line-and-hand.html', 'utf8');
function wrap(name, pre) { fs.writeFileSync(dir + name, '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><style>body{margin:0;font:14px system-ui}</style>' + pre + '</head><body>' + page0 + '</body></html>'); return 'file://' + dir + name; }
const SLOW = wrap('_slow.html', '<script>window.LH_SEED=11</script>');
const FAST = wrap('_fast.html', '<script>window.LH_FAST=1</script>');
let pass = 0, fail = 0; const shots = dir + 'shots/'; fs.mkdirSync(shots, { recursive: true });
function ok(c, name) { if (c) pass++; else { fail++; console.log('  FAIL: ' + name); } }
const G = '#game ';
async function idle(p) { await p.waitForFunction(() => document.getElementById('game').getAttribute('data-busy') === '0', null, { timeout: 15000 }); }
async function watch(p) { const errs = []; p.on('pageerror', e => errs.push('pageerror: ' + e.message)); p.on('console', m => { if (m.type() === 'error') errs.push('console: ' + m.text()); }); p.on('requestfailed', r => errs.push('failed: ' + r.url())); return errs; }
const tile = (x, y) => G + `.tile[data-x="${x}"][data-y="${y}"]`;
const st = p => p.evaluate(() => { const g = window.__LH.G, K = g.clash; return { turn: g.turn, phase: g.phase, over: g.over, map: g.map.name, spoils: g.run.spoils, deck: g.run.deck.length, clash: K ? { phase: K.phase, hand: K.hand.slice(), en: K.en, block: K.block, fb: K.fb, dhp: K.d.hp, ahp: K.a.hp, round: K.round } : null, D: { hp: g.u[0].hp, attacked: !!g.u[0].attacked }, insp: g.run.insp, n: g.run.n }; });
async function inView(p, sel) { return p.$$eval(sel, els => els.every(el => { const r = el.getBoundingClientRect(); return r.left >= -1 && r.right <= window.innerWidth + 1; })); }
const inFrame = (p, sels) => p.evaluate(sels => { const g = document.getElementById('game').getBoundingClientRect(); return sels.every(s => Array.from(document.querySelectorAll(s)).every(e => { const r = e.getBoundingClientRect(); return r.width === 0 || (r.left >= g.left - .5 && r.right <= g.right + .5); })); }, sels);
/* put the captain one blow from defeat beside Darrow, then beat him through the real buttons */
async function winBattle(p, tap, during) { await p.evaluate(() => { const g = window.__LH.G, D = g.u[0], C = g.u.filter(u => u.boss)[0]; g.u.forEach(u => { if (u.side === 1 && !u.boss) u.hp = 0; }); C.x = D.x; C.y = D.y - 1; C.hp = 1; C.ans = [{ b: 0, d: 1, n: 1 }]; D.attacked = false; D.moved = false; });
  const pos = await p.evaluate(() => { const g = window.__LH.G; return [g.u[0].x, g.u[0].y]; });
  await tap(tile(pos[0], pos[1])); if (!(await p.$(G + '.unit[data-u="D"] .tok.sel'))) await tap(tile(pos[0], pos[1])); await tap(tile(pos[0], pos[1] - 1)); await tap(G + '[data-a="go"]'); await idle(p); await p.waitForTimeout(400);
  for (let n = 0; n < 12; n++) { const s = await st(p); if (!s.clash) break; const i = await p.evaluate(() => { const g = window.__LH.G, LH = window.__LH.LH; return g.clash.hand.findIndex((id, i) => !LH.playable(g, i) && LH.C[id].dmg); });
    if (i < 0) { await tap(G + '[data-a="endhand"]'); await idle(p); await p.evaluate(() => { const g = window.__LH.G; g.u[0].attacked = false; }); const q = await p.evaluate(() => { const g = window.__LH.G, C = g.u.filter(u => u.boss)[0]; return [g.u[0].x, g.u[0].y, C.x, C.y]; }); await tap(tile(q[0], q[1])); await tap(tile(q[2], q[3])); await tap(G + '[data-a="go"]'); await idle(p); await p.waitForTimeout(300); continue; }
    await p.tap(G + `.hcard[data-i="${i}"]`, { position: { x: 14, y: 40 } }); await p.waitForTimeout(150); await p.tap(G + `.hcard[data-i="${i}"]`, { position: { x: 14, y: 40 } }); if (during) await during(); await idle(p); }
  await idle(p); await p.waitForTimeout(400); }

(async () => {
  const b = await chromium.launch();
  const heardAll = {};

  console.log('A. a phone, real animations, played by hand');
  {
    const ctx = await b.newContext({ viewport: { width: 400, height: 860 }, hasTouch: true, deviceScaleFactor: 2 }); const p = await ctx.newPage(); const errs = await watch(p); const tap = s => p.tap(s);
    await p.goto(SLOW); await p.waitForTimeout(900);
    ok(await p.$$eval(G + '.tile', t => t.length) === 42, 'the map has 42 tiles'); ok((await p.textContent(G + '#m-name')) === 'The Two Fords', 'the ground is named');
    ok(await p.evaluate(() => Array.from(document.images).every(i => i.naturalWidth > 0)), 'every picture loads');
    ok(!(await p.evaluate(() => document.documentElement.scrollWidth > window.innerWidth)), 'no sideways scroll at 400 wide');
    ok(await p.$$eval(G + '.unit[data-u="X"] .fi', e => e.length) >= 1 && await p.$$eval(G + '.unit[data-u="C"] .fi', e => e.length) >= 1, 'tokens carry icons for what is in force (the bolt, the captain)');
    ok(await p.$$eval(G + '.unit[data-u="P"] .tok.foe.has img', e => e.length === 1 && e[0].naturalWidth > 0), 'the pikeman wears his own picture on the map');
    ok(await p.$$eval(G + '.unit[data-u="R"] .tok img', e => e.length === 1 && e[0].getAttribute('src').includes('rae')), 'Rae is on the field');
    { // Rae tends: put her beside a hurt Darrow, select her, tap him
      const hp0 = await p.evaluate(() => { const g = window.__LH.G, D = g.u[0], R = window.__LH.LH.byId(g, 'R'); D.hp = 30; R.x = D.x + 1; R.y = D.y; return D.hp; });
      await tap(tile(3, 4)); ok(await p.$$eval(G + '.tile.mend', t => t.length) === 1 && (await p.textContent(G + '#m-rest')).includes('does not fight'), 'selecting Rae rings the friend she can tend');
      await tap(tile(2, 4)); const hp1 = await p.evaluate(() => window.__LH.G.u[0].hp); ok(hp1 === hp0 + await p.evaluate(() => window.__LH.LH.T.tend), 'tapping him mends him'); ok(await p.$eval(G + '.unit[data-u="R"] .tok', e => e.classList.contains('spent')), 'and that is her turn');
      await p.evaluate(() => { const g = window.__LH.G, R = window.__LH.LH.byId(g, 'R'); g.u[0].hp = 58; R.x = 4; R.y = 6; R.attacked = false; R.moved = false; }); await tap(tile(0, 6)); }
    await tap(tile(3, 1)); ok((await p.textContent(G + '#m-rest')).includes('Crossbowman') && await p.$$eval(G + '#m-rest .fx', e => e.length) >= 1, 'tapping a foe lists his effects as chips');
    await tap(G + '#m-rest .fx'); ok((await p.textContent(G + '#m-rest .fxtext')).includes('Wound'), 'tapping an effect explains it'); await p.locator('#game').screenshot({ path: shots + '1-inspect.png' });
    await p.evaluate(() => { window.__made = 0; window.__mo = new MutationObserver(ms => ms.forEach(m => m.addedNodes.forEach(n => { if (n.nodeType === 1 && (n.matches('.unit,.tok,.hcard:not(.ghost)') || n.querySelector('.unit,.tok,.hcard:not(.ghost)'))) window.__made++; }))); window.__mo.observe(document.getElementById('game'), { childList: true, subtree: true }); window.__D = document.querySelector('#game .unit[data-u="D"]'); });
    await tap(tile(2, 4)); ok(await p.$$eval(G + '.tile.reach', t => t.length) > 3, 'tapping Darrow lights where he can go');
    const left0 = await p.$eval(G + '.unit[data-u="D"]', e => e.getBoundingClientRect().left); await tap(tile(3, 4)); await p.waitForTimeout(120);
    const mid = await p.$eval(G + '.unit[data-u="D"]', e => e.getBoundingClientRect().left); await p.waitForTimeout(400); const left1 = await p.$eval(G + '.unit[data-u="D"]', e => e.getBoundingClientRect().left);
    ok(mid > left0 + 2 && mid < left1 - 2, 'a moved token slides to its new tile'); ok(await p.evaluate(() => window.__D === document.querySelector('#game .unit[data-u="D"]') && window.__made === 0), 'and no token is rebuilt by tapping or moving');
    ok(!!(await p.$(G + '[data-a="unmove"]')), 'a move just made can be taken back'); await tap(G + '[data-a="unmove"]'); ok(await p.evaluate(() => { const D = window.__LH.G.u[0]; return D.x === 2 && D.y === 4 && !D.moved; }), 'and he is where he was'); await p.waitForTimeout(350); ok(await p.$$eval(G + '.tile.hit', t => t.length) === 1, 'the pikeman two tiles off is ringed');
    await tap(tile(2, 2)); ok(!!(await p.$(G + '[data-a="go"]')) && (await p.textContent(G + '#m-rest')).includes('cannot be hurt'), 'the forecast opens and says he cannot answer from two tiles');
    await tap(G + '[data-a="go"]'); await p.waitForTimeout(250); ok(await p.isVisible(G + '#banner'), 'the banner announces the clash');
    await idle(p); await p.waitForTimeout(500);
    ok(await p.isVisible(G + '#scr-clash') && !(await p.isVisible(G + '#scr-map')), 'the screen is now the card table');
    { const m = await p.evaluate(() => window.__LH.music); ok(m.started && m.want === 'clash' && m.playing === 'clash', 'the music has started with the first tap and is the card table\'s'); }
    let s = await st(p); const n0 = s.clash.hand.length;
    ok(await p.$$eval(G + '.hcard', c => c.length) === n0 && n0 >= 5, 'the hand is dealt: ' + n0 + ' cards');
    const xs = await p.$$eval(G + '.hcard', c => c.map(e => Math.round(e.getBoundingClientRect().left))); ok(xs.every((x, i) => i === 0 || x > xs[i - 1]), 'the hand is fanned left to right'); ok(await inView(p, G + '.hcard'), 'every card is on screen');
    ok((await p.textContent(G + '#c-intent')).includes('Out of reach'), 'his answer is shown above him');
    ok(await p.$$eval(G + '#c-foe img.cut.noflip', e => e.length === 1 && e[0].naturalWidth > 0 && e[0].getAttribute('src').includes('fig-pikeman')), 'the pikeman stands in the clash as his own figure');
    ok(await p.$$eval(G + '#c-vs .fx', e => e.length) >= 2, 'effects in force show as chips under each fighter'); await tap(G + '#c-vs .fx'); await p.waitForTimeout(150); ok((await p.textContent(G + '#c-tell')).length > 20, 'tapping one explains it');
    await p.locator('#game').screenshot({ path: shots + '2-clash.png' });
    const cant = await p.$(G + '.hcard.cant');
    if (cant) { await cant.tap({ position: { x: 14, y: 40 } }); await p.waitForTimeout(200); await cant.tap({ position: { x: 14, y: 40 } }); await p.waitForTimeout(350); ok((await p.$$eval(G + '.hcard', c => c.length)) === n0, 'a card that cannot be played stays in the hand'); ok(!!(await p.$(G + '#c-tell .warn')), 'and says why'); }
    const idx = await p.evaluate(() => { const g = window.__LH.G, LH = window.__LH.LH; return g.clash.hand.findIndex((id, i) => !LH.playable(g, i) && LH.C[id].dmg); });
    const before = await st(p), cardName = await p.evaluate(i => window.__LH.LH.C[window.__LH.G.clash.hand[i]].n, idx);
    await p.tap(G + `.hcard[data-i="${idx}"]`, { position: { x: 14, y: 40 } }); await p.waitForTimeout(250);
    ok(await p.$eval(G + `.hcard[data-i="${idx}"]`, e => e.classList.contains('sel')), 'first tap lifts the card'); ok((await p.textContent(G + '#c-tell')).includes(cardName), 'and shows its text below the field');
    ok(await inView(p, G + '.hcard.sel'), 'the lifted card stays on screen'); ok(await p.evaluate(() => document.querySelector('#game .hcard.sel').getBoundingClientRect().top >= document.getElementById('c-tell').getBoundingClientRect().bottom - 2), 'and does not cover the line that explains it');
    const lifted = await p.$eval(G + '.hcard.sel', e => { const r = e.getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2, r.width]; }); await p.evaluate(() => { window.__made = 0; });
    await p.evaluate(() => { window.__floats = 0; new MutationObserver(m => m.forEach(r => r.addedNodes.forEach(n => { if (n.classList && n.classList.contains('float')) window.__floats++; }))).observe(document.getElementById('game'), { childList: true, subtree: true }); });
    const gh = await p.evaluate(() => { const e = document.querySelector('#game .hcard.sel'), a = e.getBoundingClientRect(), o = { bubbles: true, clientX: a.left + 10, clientY: a.top + 10, pointerId: 1, button: 0 };
      e.dispatchEvent(new PointerEvent('pointerdown', o)); window.dispatchEvent(new PointerEvent('pointerup', o)); const g = document.querySelector('#game .ghost'); if (!g) return null; const r = g.getBoundingClientRect(); return [r.left - a.left, r.top - a.top, r.width - a.width, r.height - a.height].map(Math.abs); });
    ok(gh && gh.every(v => v < 2), 'the card takes off from exactly where it was, at the size it was'); await p.waitForTimeout(120); ok(!!(await p.$(G + '.ghost')), 'second tap sends the card flying');
    await idle(p); s = await st(p);
    ok(s.clash.hand.length === before.clash.hand.length - 1, 'the card has left the hand'); ok(s.clash.dhp < before.clash.dhp || s.clash.fb < before.clash.fb, 'and its damage landed'); ok(await p.evaluate(() => window.__floats) >= 1, 'with a number floating off him'); ok(!(await p.$(G + '.ghost')), 'the flying card is cleaned up'); ok(await p.evaluate(() => window.__made === 0), 'and the cards left in hand were not rebuilt');
    await tap(G + '[data-a="pile-draw"]'); ok(await p.isVisible(G + '#c-piles'), 'the draw pile opens'); await tap(G + '#c-piles'); ok(!(await p.isVisible(G + '#c-piles')), 'and closes');
    await tap(G + '[data-a="endhand"]'); await idle(p); await p.waitForTimeout(300);
    ok(await p.isVisible(G + '#scr-map') && !(await p.isVisible(G + '#scr-clash')), 'ending the hand returns to the map'); ok((await p.textContent(G + '.log')).includes('dealt'), 'the map log sums up the clash'); s = await st(p); ok(!s.clash && s.D.attacked, 'Darrow has fought');
    const heard = await p.evaluate(() => window.__LH.heard); ['unit_select', 'forecast_open', 'clash_start', 'card_deal', 'card_lift', 'card_attack', 'end_hand', 'ui_tap'].forEach(n => ok(heard[n] > 0, 'the sound hook fires: ' + n));
    await tap(G + '[data-a="dz"]'); ok(await p.$$eval(G + '.tile.dz', t => t.length) > 5, 'their reach can be shown'); await tap(G + '[data-a="dz"]');
    { // falling back through a friend, walked tile by tile; then put everyone back
      const keep = await p.evaluate(() => { const g = window.__LH.G, k = g.u.map(u => [u.x, u.y, u.moved, u.attacked, u.hp]), by = id => g.u.filter(u => u.id === id)[0]; g.u.forEach(u => { if (u.side) u.hp = 0; }); by('C').hp = 9; by('C').x = 5; by('C').y = 0;
        g.u.forEach((u, i) => { if (u.side === 0) { u.x = i; u.y = 6; u.moved = false; u.attacked = false; } }); by('D').x = 2; by('D').y = 3; by('H').x = 2; by('H').y = 4; return k; });
      await tap(tile(5, 2)); await tap(tile(2, 3)); ok(await p.$$eval(G + '.tile.back', t => t.length === 1 && t[0].getAttribute('data-x') === '2' && t[0].getAttribute('data-y') === '5'), 'with Hollis behind him, the tile beyond is offered and marked');
      ok((await p.textContent(G + '.panel.info')).includes('fall back through Hollis'), 'and the panel says so');
      await tap(tile(2, 5)); ok(await p.$$eval(G + '.unit.walk', e => e.length) === 1, 'the move is walked, not jumped'); await p.waitForTimeout(700);
      ok(await p.evaluate(() => { const D = window.__LH.G.u[0]; return D.x === 2 && D.y === 5 && D.moved; }) && await p.$$eval(G + '.unit.walk', e => e.length) === 0, 'he ends on the tile behind his friend');
      await tap(G + '[data-a="unmove"]'); ok(await p.evaluate(() => window.__LH.G.u[0].y === 3), 'and it can be taken back');
      await p.evaluate(k => { const g = window.__LH.G; g.u.forEach((u, i) => { u.x = k[i][0]; u.y = k[i][1]; u.moved = k[i][2]; u.attacked = k[i][3]; u.hp = k[i][4]; }); }, keep); await tap(tile(5, 2)); await tap(tile(5, 2)); await p.waitForTimeout(400); }
    { ok(await p.getAttribute(G + '[data-toggle="music"]', 'aria-pressed') === 'true' && (await p.textContent(G + '[data-toggle="music"]')).includes('on'), 'a music switch sits under the game');
      await tap(G + '[data-toggle="music"]'); ok(await p.evaluate(() => !window.__LH.prefs.music && window.__LH.music.playing === null), 'it turns the music off'); await tap(G + '[data-toggle="music"]'); ok(await p.evaluate(() => window.__LH.music.playing === 'map'), 'and on again, the map\'s track'); }
    await tap(G + '[data-a="end"]'); await p.waitForTimeout(500); ok(await p.getAttribute('#game', 'data-busy') === '1', 'the enemy turn is shown step by step'); await idle(p); s = await st(p); ok(s.turn === 2 && s.phase === 'player', 'then it is turn two');
    await p.locator('#game').screenshot({ path: shots + '3-turn-two.png' });
    // win the battle and visit the camp
    await winBattle(p, tap, async () => { await p.waitForSelector(G + '.banner.cur-win', { state: 'visible', timeout: 8000 }); ok(true, 'a curtain crosses the screen when the crossing is won'); }); s = await st(p);
    ok(s.over && s.over.win && await p.isVisible(G + '#scr-camp'), 'felling the captain opens the camp');
    ok((await p.textContent(G + '#camp-sp b')) === String(s.spoils) && await p.isVisible(G + '.camphero') && await p.$$eval(G + '.cfaces img', e => e.length) === 5, 'the camp shows the purse and the company round the fire'); ok(s.spoils >= 4, 'with spoils in hand: ' + s.spoils);
    ok(await p.$$eval(G + '[data-buy]', e => e.length) === 5, 'five cards are on offer'); ok(await inFrame(p, [G + '#scr-camp *']), 'the camp fits inside the frame');
    await p.evaluate(() => { window.__LH.G.run.spoils = 14; }); await tap(G + '[data-buy]'); ok(!!(await p.$(G + '[data-a="buy"]')), 'tapping a card shows it and its price'); await p.locator('#game').screenshot({ path: shots + '4-camp.png' });
    const d0 = (await st(p)).deck; await tap(G + '[data-a="buy"]'); ok(await p.$$eval(G + '#camp-sp .spend', e => e.length) === 1, 'spoils leaving the purse are shown'); s = await st(p); ok((await p.textContent(G + '#camp-sp b')) === String(s.spoils), 'and the purse is right afterwards'); ok(s.deck === d0 + 1 && s.spoils < 14 && await p.$$eval(G + '[data-buy]', e => e.length) === 4, 'buying adds the card, costs spoils, and takes it off the blanket');
    await tap(G + '[data-a="hone-strike"]'); ok(await p.evaluate(() => window.__LH.G.run.deck.indexOf('strike2') >= 0), 'a Strike can be honed');
    await tap(G + '[data-a="leavemode"]'); await tap(G + '.decklist .dk'); ok((await st(p)).deck === d0, 'a card can be left behind');
    const hp0 = (await st(p)).D.hp; if (await p.$(G + '[data-a="mend"]:not([disabled])')) { await tap(G + '[data-a="mend"]'); ok((await st(p)).D.hp >= hp0, 'mending works'); }
    await tap(G + '[data-a="march"]'); ok(await p.isVisible(G + '.banner.cur-march') && (await p.textContent(G + '.banner.cur-march')).includes('The Wood Road'), 'marching on is announced by a curtain'); await idle(p); s = await st(p); ok(s.n === 2 && s.map === 'The Wood Road' && await p.isVisible(G + '#scr-map'), 'marching on opens the Wood Road'); ok(await p.$$eval(G + '.tok.foe', e => e.length) === 5, 'with five foes on it');
    await p.locator('#game').screenshot({ path: shots + '5-wood-road.png' });
    await winBattle(p, tap); await tap(G + '[data-a="march"]'); await idle(p); s = await st(p); ok(s.n === 3 && s.map === 'The Bridge', 'then the Bridge'); ok(await p.$$eval(G + '.tile.b', e => e.length) === 1, 'which has a bridge'); await p.locator('#game').screenshot({ path: shots + '6-bridge.png' });
    await winBattle(p, tap); s = await st(p); ok(s.over && s.over.done && (await p.textContent(G + '#m-rest')).includes('Renown'), 'the third captain ends the run with a Renown score'); await p.locator('#game').screenshot({ path: shots + '7-run-won.png' });
    Object.assign(heardAll, await p.evaluate(() => window.__LH.heard));
    await tap(G + '[data-a="again"]'); await idle(p); s = await st(p); ok(s.n === 1 && s.spoils === 0 && s.deck === 16, 'a new run starts clean');
    ok(errs.length === 0, 'no errors on the phone: ' + errs.join(' | ')); await ctx.close();
  }

  console.log('B. a desktop, a mouse: dragging, the keyboard, the settings and the lists');
  {
    const ctx = await b.newContext({ viewport: { width: 1200, height: 900 } }); const p = await ctx.newPage(); const errs = await watch(p);
    await p.goto(SLOW); await p.waitForTimeout(700);
    ok(!(await p.evaluate(() => document.documentElement.scrollWidth > window.innerWidth)), 'no sideways scroll on a desktop');
    const nS = await p.evaluate(() => window.__LH.SFX.length); ok(await p.$$eval('#sfx-table tr', r => r.length) === nS && nS >= 30, 'the sound list shows all ' + nS + ' sounds');
    ok(await p.$$eval('#sfx-table [data-hear]', r => r.length) === nS, 'each with a stand-in to hear'); await p.click('#sfx-table [data-hear]');
    ok(await p.$$eval('#market-gallery .card', r => r.length) === LH.POOL.length + 3, 'the camp gallery shows every camp card, two honed and the Wound'); ok(await p.$$eval('.prompt pre', r => r.length) === 9 && await p.$$eval('[data-copy]', r => r.length) === 9, 'nine prompts, each with a copy button');
    ok((await p.textContent('#p-C')).includes('captain') && (await p.textContent('#p-style')).includes('#0000FF'), 'the prompts carry the foe and the chroma screen');
    await p.click('[data-pref="sound=true"]'); ok(await p.getAttribute('[data-pref="sound=true"]', 'aria-pressed') === 'true', 'sound can be switched on');
    ok(await p.evaluate(() => window.__LH.assets.sfx.battle_won === 'sfx/battle_won.mp3'), 'the build knows the battle-won sound is made');
    const dur = await p.evaluate(() => new Promise(res => { const a = new Audio('sfx/battle_won.mp3'); a.oncanplaythrough = () => res(a.duration); a.onerror = () => res(-1); setTimeout(() => res(-2), 4000); })); ok(dur > 1 && dur < 2.5, 'and the file loads and is about a second and a half long (' + dur + ')');
    await p.click('[data-hear="battle_won"]'); ok(await p.evaluate(() => window.__LH.played.battle_won === 1), 'pressing Hear plays the real file, not the tone');
    ok(await p.$$eval('#sfx-table .made', e => e.length) === await p.evaluate(() => Object.keys(window.__LH.assets.sfx).length) && (await p.textContent('[data-who="pikeman"]')).includes('figure and token made') && (await p.textContent('[data-who="captain"]')).includes('to make'), 'the lists mark what is made and what is still to make');
    await p.click(tile(2, 4)); await p.click(tile(2, 2)); await p.click(G + '[data-a="go"]'); await idle(p); await p.waitForTimeout(600);
    { // a card he cannot afford is refused, with its own sound
      const j = await p.evaluate(() => { const g = window.__LH.G, K = g.clash; window.__en = K.en; K.en = 0; return K.hand.findIndex(id => window.__LH.LH.C[id].c > 0); }); const n = (await st(p)).clash.hand.length;
      await p.click(G + `.hcard[data-i="${j}"]`, { position: { x: 14, y: 40 } }); await p.waitForTimeout(260); const at0 = await p.$eval(G + `.hcard[data-i="${j}"]`, e => e.getBoundingClientRect().left);
      await p.click(G + `.hcard[data-i="${j}"]`, { position: { x: 14, y: 40 } }); await p.waitForTimeout(90); const at1 = await p.$eval(G + `.hcard[data-i="${j}"]`, e => e.getBoundingClientRect().left); ok(Math.abs(at1 - at0) < 12, 'a refused card shakes where it stands (' + Math.round(at1 - at0) + 'px)'); await p.waitForTimeout(300);
      ok((await st(p)).clash.hand.length === n && await p.evaluate(() => window.__LH.heard.card_cant > 0), 'a card he cannot afford is refused, and says so'); ok((await p.textContent(G + '#c-tell')).includes('Needs'), 'with the reason');
      await p.evaluate(() => { window.__LH.G.clash.en = window.__en; }); await p.click(G + '#c-stage'); Object.assign(heardAll, await p.evaluate(() => window.__LH.heard)); }
    let s = await st(p); const idx = await p.evaluate(() => { const g = window.__LH.G, LH = window.__LH.LH; return g.clash.hand.findIndex((id, i) => !LH.playable(g, i)); });
    const box = await (await p.$(G + `.hcard[data-i="${idx}"]`)).boundingBox(), cx = box.x + 30, cy = box.y + 40;
    await p.mouse.move(cx, cy); await p.mouse.down(); await p.mouse.move(cx + 5, cy - 30, { steps: 4 }); await p.mouse.up(); await p.waitForTimeout(400);
    let s2 = await st(p); ok(s2.clash.hand.length === s.clash.hand.length, 'a short drag puts the card back');
    const box2 = await (await p.$(G + `.hcard[data-i="${idx}"]`)).boundingBox();
    await p.mouse.move(box2.x + 30, box2.y + 40); await p.mouse.down(); await p.mouse.move(box2.x + 40, box2.y - 60, { steps: 5 }); await p.mouse.move(box2.x + 60, box2.y - 170, { steps: 6 });
    ok(await p.$eval(G + '#c-stage', e => e.classList.contains('drop')), 'dragging over the field lights it'); await p.mouse.up(); await idle(p); s2 = await st(p); ok(JSON.stringify(s2.clash) !== JSON.stringify(s.clash), 'a long drag onto the field plays the card');
    s = await st(p); const k = await p.evaluate(() => { const g = window.__LH.G, LH = window.__LH.LH; return g.clash.hand.findIndex((id, i) => !LH.playable(g, i)); });
    if (k >= 0) { await p.focus(G + `.hcard[data-i="${k}"]`); await p.keyboard.press('Enter'); await p.waitForTimeout(200); ok(await p.$eval(G + `.hcard[data-i="${k}"]`, e => e.classList.contains('sel')), 'Enter lifts the focused card');
      await p.focus(G + `.hcard[data-i="${k}"]`); await p.keyboard.press('Enter'); await idle(p); s2 = await st(p); ok(JSON.stringify(s2.clash) !== JSON.stringify(s.clash), 'Enter again plays it'); }
    s = await st(p); await p.click(G + '[data-a="redraw"]'); await p.waitForTimeout(700); s2 = await st(p); ok(s2.insp === s.insp - 1 && s2.clash.hand.length >= 5, 'New hand spends an Inspiration and deals five'); ok(await p.$eval(G + '[data-a="redraw"]', e => e.disabled), 'and can be used once a clash');
    await p.click(G + '[data-a="endhand"]'); await idle(p);
    await p.click('[data-pref="level=1"]'); const hard = await p.evaluate(() => window.__LH.LH.byId(window.__LH.G, 'P').atk); await p.click('[data-pref="level=0"]'); const std = await p.evaluate(() => window.__LH.LH.byId(window.__LH.G, 'P').atk); ok(hard === std + LH.T.levelAtk, 'the difficulty setting starts a new run with stronger foes');
    await p.click(tile(2, 4)); await p.click(tile(3, 4)); await p.click('[data-newrun]'); ok(await p.evaluate(() => window.__LH.G.u[0].x === 2 && window.__LH.G.turn === 1), 'Start a new run does so');
    await p.click('[data-pref="deck=all"]'); s = await st(p); ok(s.deck === 16 + LH.POOL.length && s.turn === 1, 'the try-everything deck starts a new run with every camp card in it'); await p.click('[data-pref="deck=sheet"]'); ok((await st(p)).deck === 16, 'and the sheet deck puts it back');
    ok(errs.length === 0, 'no errors on the desktop: ' + errs.join(' | ')); await ctx.close();
  }

  console.log('C. a small phone, three-round clashes');
  {
    const ctx = await b.newContext({ viewport: { width: 360, height: 740 }, hasTouch: true }); const p = await ctx.newPage(); const errs = await watch(p);
    await p.goto(SLOW); await p.waitForTimeout(700);
    ok(!(await p.evaluate(() => document.documentElement.scrollWidth > window.innerWidth)), 'no sideways scroll at 360 wide');
    await p.tap('[data-pref="rounds=3"]'); ok(await p.getAttribute('[data-pref="rounds=3"]', 'aria-pressed') === 'true', 'the three-round setting takes');
    await p.tap(tile(2, 4)); await p.tap(tile(2, 3)); await p.tap(tile(2, 2)); await p.tap(G + '[data-a="go"]'); await idle(p); await p.waitForTimeout(500);
    ok((await p.textContent(G + '#c-top')).includes('Round 1 of 3'), 'the table shows round 1 of 3'); ok(await inView(p, G + '.hcard'), 'the hand fits a 360 screen'); ok(await inFrame(p, ['#c-tray', '#c-hand', '#c-stage', '#c-vs', '#c-vs .fx']), 'and every part of the table stays inside the frame');
    await p.locator('#game').screenshot({ path: shots + '8-small-phone.png' });
    await p.tap(G + '[data-a="endhand"]'); await idle(p); let s = await st(p);
    if (s.clash) { ok(s.clash.phase === 'choice' && await p.isVisible(G + '[data-a="press"]'), 'after his answer you choose');
      await p.tap(G + '[data-a="press"]'); await p.waitForTimeout(700); s = await st(p); ok(s.clash.round === 2 && s.clash.hand.length >= 5, 'pressing on deals round two');
      await p.tap(G + '[data-a="endhand"]'); await idle(p); s = await st(p); if (s.clash) { await p.tap(G + '[data-a="leave"]'); await idle(p); } s = await st(p); ok(!s.clash && await p.isVisible(G + '#scr-map'), 'breaking off returns to the map'); }
    await winBattle(p, sel => p.tap(sel)); ok(await p.isVisible(G + '#scr-camp') && await inFrame(p, [G + '#scr-camp *']), 'the camp fits a 360 screen'); await p.locator('#game').screenshot({ path: shots + '9-camp-small.png' });
    ok(errs.length === 0, 'no errors on the small phone: ' + errs.join(' | ')); await ctx.close();
  }

  console.log('D. whole runs through the real buttons (animations off)');
  for (const rounds of [1, 3]) {
    const ctx = await b.newContext({ viewport: { width: 400, height: 860 } }); const p = await ctx.newPage(); const errs = await watch(p);
    await p.goto(FAST); await p.waitForTimeout(500); if (rounds === 3) await p.click('[data-pref="rounds=3"]');
    const res = await p.evaluate(async (RUNS) => {
      const H = window.__LH, LH = H.LH, C = LH.C, root = document.getElementById('game'), q = s => root.querySelector(s), tick = () => new Promise(r => setTimeout(r, 0));
      const settle = async () => { let n = 0; do { await tick(); } while (H.busy && n++ < 4000); if (H.busy) throw new Error('stuck busy'); };
      const click = async s => { const e = typeof s === 'string' ? q(s) : s; if (!e) throw new Error('missing ' + s); e.click(); await settle(); };
      const tap = async (x, y) => click(`.tile[data-x="${x}"][data-y="${y}"]`);
      const card = async i => { const e = q(`.hcard[data-i="${i}"]`); if (!e) throw new Error('no card ' + i); const r = e.getBoundingClientRect(), o = { bubbles: true, clientX: r.left + 5, clientY: r.top + 5, pointerId: 1, button: 0 };
        e.dispatchEvent(new PointerEvent('pointerdown', o)); window.dispatchEvent(new PointerEvent('pointerup', o)); await settle(); };
      const score = (K, id) => { const c = C[id]; let s = 1; if (c.stance || c.en || c.draw) s += 50; if (c.dmg) s += 10 + LH.cardDmg(K, c); if (c.blk) s += 6; return s; };
      const out = [], seen = {}; let clashes = 0, cards = 0, camps = 0, bought = 0, fxTaps = 0, tends = 0;
      for (let run = 0; run < RUNS; run++) { let guard = 0;
        while (guard++ < 3000) { const G = H.G;
          if (G.over) { if (!G.over.win) break; camps++; if (q('#scr-camp').hidden) throw new Error('camp not shown');
            for (let n = 0; n < 6; n++) { const pick = G.camp.market.filter(id => C[id].p <= G.run.spoils)[0]; if (!pick) break; await click(`[data-buy="${pick}"]`); if (!q('[data-a="buy"]:not([disabled])')) throw new Error('buy button missing'); await click('[data-a="buy"]'); bought++; }
            if (q('[data-a="mend"]:not([disabled])') && G.u[0].hp < 40) await click('[data-a="mend"]');
            if (camps % 2 && q('[data-a="hone-strike"]:not([disabled])')) await click('[data-a="hone-strike"]');
            if (camps % 3 === 0 && q('[data-a="leavemode"]:not([disabled])')) { await click('[data-a="leavemode"]'); await click('.decklist .dk'); }
            await click('[data-a="march"]'); if (H.G.over || q('#scr-map').hidden) throw new Error('march did not start the next battle'); continue; }
          for (const u of G.u.filter(u => u.side === 0)) { let n = 0;
            if (u.tend) { if (!LH.canAct(u)) continue; if (!q(`.unit[data-u="${u.id}"] .tok.sel`)) await tap(u.x, u.y); const tt = LH.tendTargets(H.G, u);
              if (tt.length) { const hp = tt[0].hp, w = LH.wounds(tt[0]); await tap(tt[0].x, tt[0].y); tends++; if (tt[0].hp === hp && LH.wounds(tt[0]) === w) throw new Error('tend did nothing'); } else if (q('[data-a="wait"]:not([disabled])')) await click('[data-a="wait"]'); continue; }
            while (!H.G.over && LH.canAct(u) && n++ < 4) {
              if (!q(`.unit[data-u="${u.id}"] .tok.sel`)) await tap(u.x, u.y);
              if (n === 1 && q('#m-rest [data-fx]')) { await click('#m-rest [data-fx]'); fxTaps++; if (!q('#m-rest .fxtext')) throw new Error('effect text missing'); }
              let ts = LH.targets(H.G, u);
              if (!ts.length && !u.moved) { const r = LH.reach(H.G, u), foes = LH.foesUp(H.G); let best = null, bd = 99;
                Object.keys(r).forEach(k => { const pp = k.split(','); foes.forEach(f => { const d = Math.abs(f.x - pp[0]) + Math.abs(f.y - pp[1]) + (f.boss ? 0 : .5); if (d >= 1 && d < bd) { bd = d; best = pp; } }); });
                if (best && (+best[0] !== u.x || +best[1] !== u.y)) { await tap(+best[0], +best[1]); if (LH.canAct(u) && !q(`.unit[data-u="${u.id}"] .tok.sel`)) await tap(u.x, u.y); }
                ts = LH.targets(H.G, u); }
              if (!ts.length || u.attacked) { if (!u.attacked && q('[data-a="wait"]:not([disabled])') && (u.id.charCodeAt(0) + G.turn) % 3 === 0) await click('[data-a="wait"]'); break; }
              ts.sort((a, b) => (b.boss ? 1 : 0) - (a.boss ? 1 : 0)); await tap(ts[0].x, ts[0].y); if (!q('[data-a="go"]')) throw new Error('no forecast'); await click('[data-a="go"]'); clashes++;
              let cg = 0; while (H.G.clash && cg++ < 200) { const K = H.G.clash;
                if (K.phase === 'play') { const can = K.hand.map((_, i) => i).filter(i => !LH.playable(H.G, i)).sort((x, y) => score(K, K.hand[y]) - score(K, K.hand[x]));
                  if (cg === 1 && q('#c-vs [data-fx]')) { await click('#c-vs [data-fx]'); fxTaps++; }
                  if (can.length) { const i = can[0], id = K.hand[i], before = K.hand.length; await card(i); await card(i); cards++; seen[id] = 1; if (H.G.clash && H.G.clash === K && K.phase === 'play' && K.hand.length === before && !C[id].draw) throw new Error('card did not play: ' + id); }
                  else { if (K.a.id === 'D' && cg % 5 === 0 && q('[data-a="redraw"]:not([disabled])')) { await click('[data-a="redraw"]'); continue; } await click('[data-a="endhand"]'); } }
                else if (K.phase === 'choice') { await click(K.a.hp > 25 ? '[data-a="press"]' : '[data-a="leave"]'); }
                else await settle(); }
              if (H.G.clash) throw new Error('clash never ended');
              if (!H.G.over && q('#scr-map').hidden) throw new Error('map not shown after clash');
            } }
          if (H.G.over) continue;
          await click('[data-a="end"]'); if (H.G.phase !== 'player') throw new Error('enemy phase did not finish');
        }
        out.push((H.G.over ? (H.G.over.done ? 'won' : 'lost') : 'unfinished') + '@' + H.G.run.n); if (!q('.renown')) throw new Error('no Renown at the end'); if (run < RUNS - 1) await click('[data-a="again"]');
      }
      return { out, clashes, cards, camps, bought, fxTaps, tends, kinds: Object.keys(seen).length, heard: Object.assign({}, H.heard) };
    }, 12).catch(e => ({ error: e.message }));
    ok(!res.error, 'rounds=' + rounds + ': twelve runs through the buttons' + (res.error ? ': ' + res.error : ''));
    if (!res.error) { Object.assign(heardAll, res.heard); ok(res.out.every(o => !o.startsWith('unfinished')), 'every run reaches an ending'); ok(res.camps > 0 && res.bought > 0, 'the camp was used');
      console.log('   rounds=' + rounds + ': ' + res.out.join(' ') + ' · ' + res.clashes + ' clashes, ' + res.cards + ' cards played (' + res.kinds + ' kinds), ' + res.camps + ' camps, ' + res.bought + ' cards bought, ' + res.fxTaps + ' effects read, ' + res.tends + ' tends'); }
    ok(errs.length === 0, 'rounds=' + rounds + ': no errors: ' + errs.slice(0, 3).join(' | ')); await ctx.close();
  }
  { const ctx = await b.newContext(); const p = await ctx.newPage(); await p.goto(FAST); const names = await p.evaluate(() => window.__LH.SFX.map(s => s[0])); const never = names.filter(n => !heardAll[n]);
    ok(never.length === 0, 'every sound in the list fired somewhere in these tests' + (never.length ? ' (never: ' + never.join(', ') + ')' : '')); console.log('   sounds fired: ' + (names.length - never.length) + ' of ' + names.length + (never.length ? ' · not reached: ' + never.join(', ') : '')); await ctx.close(); }

  await b.close();
  console.log('\n' + pass + ' passed, ' + fail + ' failed');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.log('CRASH', e); process.exit(2); });
