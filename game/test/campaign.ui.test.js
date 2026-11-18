/* The campaign on the real page, in a browser: it opens, every mission starts clean, and the prologue plays to its end by taps.
   python3 game/build_campaign.py, then: node game/test/campaign.ui.test.js */
const {chromium}=require('playwright');const path=require('path');
let fails=0,checks=0;function ok(c,m){checks++;if(!c){fails++;console.log('  FAIL '+m)}}
(async()=>{
  const b=await chromium.launch();
  for(const vp of [{width:390,height:844},{width:1200,height:900}]){
    const p=await b.newPage({viewport:vp});const errs=[];
    p.on('pageerror',e=>errs.push(e.message));p.on('console',m=>{if(m.type()==='error'&&!/net::|Failed to load/.test(m.text()))errs.push(m.text())});
    await p.addInitScript(()=>{window.LH_FAST=true;try{localStorage.removeItem('lh-campaign')}catch(e){}});
    await p.goto('file://'+path.resolve(__dirname,'../dist/campaign/campaign.html'));await p.waitForTimeout(250);
    const tap=async(x,y)=>{await p.click(`#m-board .tile[data-x="${x}"][data-y="${y}"]`,{force:true});await p.waitForTimeout(60)};
    ok(await p.evaluate(()=>__CP.scr==='title'),'opens on the title');
    ok(await p.locator('.cp.on [data-cp="intro:p0"]').count()===1,'the first mission is offered');
    await p.click('[data-cp="list"]');
    ok(await p.locator('.cp-row').count()===await p.evaluate(()=>CP.ORDER.length),'every mission is listed');
    ok(await p.locator('.cp-row.locked').count()===await p.evaluate(()=>CP.ORDER.length-1),'all but the first are locked at the start');
    ok(await p.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth+1),'no sideways scroll at '+vp.width);
    /* the prologue, by taps */
    await p.click('[data-cp="intro:p0"]');ok(await p.locator('.cp-card h2').innerText()==='The Grace','the place card names the mission');
    await p.click('[data-cp="go:p0"]');await p.waitForTimeout(120);
    ok(await p.evaluate(()=>__LH.G.ms==='p0'&&__CP.scr==='play'),'the mission starts');
    ok(await p.locator('#m-rest .cp-obj').count()===1,'the objective is on the map screen');
    ok(await p.locator('#m-board .tile[data-mark="go"]').count()===1,'the field-stone is marked');
    ok(await p.evaluate(()=>getComputedStyle(document.querySelector('.unit[data-u="Z"]')).display==='none'),'the marker captain is not shown');
    await tap(3,6);await tap(3,5);ok(await p.evaluate(()=>__LH.G.cs.grace===1&&__LH.G.u[0].br===5),'kneeling gives the Grace');
    await tap(3,4);await tap(3,3);await p.click('#game [data-a="go"]');await p.waitForTimeout(200);
    ok(await p.evaluate(()=>!!__LH.G.clash&&__LH.G.clash.hand.length===5),'the first hand is the Grace\'s');
    ok((await p.locator('#c-tray .endbtn small').innerText()).indexOf('pulls')>=0,'the river pulls; it does not strike');
    ok(await p.locator('#scr-clash .cp-hint').count()===1,'the hint is on the card table');
    await p.click('#game [data-a="endhand"]');await p.waitForTimeout(200);await p.click('#game [data-a="press"]');await p.waitForTimeout(200);
    ok(await p.evaluate(()=>__LH.G.clash.hand.join()==='frost,frost,turn,frost'&&__LH.G.clash.en===0),'the Grace fails: frost in the hand, no breath');
    const t=p.locator('#c-hand .hcard[data-id="turn"]');await t.click();await t.click().catch(()=>{});await p.waitForTimeout(200);
    await p.click('#game [data-a="endhand"]');await p.waitForFunction(()=>__CP.scr==='outro',null,{timeout:8000}).catch(()=>{});
    ok(await p.evaluate(()=>__CP.scr==='outro'&&__CP.P.done.p0&&__CP.P.done.p0.stars===3),'the fall ends the mission and is kept');
    ok(await p.locator('.cp.on [data-cp="intro:p1"]').count()===1,'the next mission is offered');
    ok(await p.evaluate(()=>JSON.parse(localStorage.getItem('lh-campaign')).done.p0.stars===3),'progress is saved in the browser');
    /* every mission starts, shows its aim, and says nothing broken */
    const ids=await p.evaluate(()=>CP.ORDER);
    for(const id of ids){
      await p.evaluate(i=>{__CP.intro(i);__CP.begin(i)},id);await p.waitForTimeout(100);
      const r=await p.evaluate(()=>{var G=__LH.G,g=document.getElementById('game');return {ms:G.ms,obj:(document.querySelector('#m-rest .cp-obj')||{}).textContent||'',top:document.getElementById('m-top').textContent,text:g.innerText,
        imgs:[].slice.call(g.querySelectorAll('.unit img')).filter(function(i){return i.complete&&!i.naturalWidth}).map(function(i){return i.getAttribute('src')}),th:g.getAttribute('data-th')}});
      ok(r.ms===id&&r.obj.length>10,id+' starts with its objective');ok(!/undefined|NaN|\bthe The\b|Battle \d of 3/.test(r.text),id+' reads clean');ok(r.imgs.length===0,id+' has every face: '+r.imgs.join(' '));ok(!!r.th,id+' has its ground');
      const d=await p.evaluate(()=>{var u=__LH.G.u[0];return [u.x,u.y]});await tap(d[0],d[1]);
      const tg=await p.evaluate(()=>{var G=__LH.G,t=__LH.LH.targets(G,G.u[0]);return t.length?[t[0].x,t[0].y]:null});
      if(tg){await tap(tg[0],tg[1]);await p.click('#game [data-a="go"]');await p.waitForTimeout(150);
        const k=await p.evaluate(()=>document.getElementById('scr-clash').innerText);ok(!/undefined|NaN|\bthe The\b|will (strikes|pulls|presses|tells|climbs)/.test(k),id+' clash reads clean');
        await p.click('#game [data-a="endhand"]');await p.waitForTimeout(250);}
      await p.evaluate(()=>{});
    }
    ok(errs.length===0,'no script errors at '+vp.width+': '+errs.slice(0,3).join(' | '));
    await p.close();
  }
  await b.close();console.log(fails?fails+' of '+checks+' checks failed':'all '+checks+' checks passed');process.exit(fails?1:0);
})();
