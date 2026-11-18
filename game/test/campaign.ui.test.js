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
    /* the fire: stars are spent on a pack for the larger fights, and can be had back */
    await p.evaluate(()=>{var P=__CP.P;P.done={};['p0','p1','c1','c2','c3','c4a','c4b','c4c','c5'].forEach(function(k){P.done[k]={stars:2}});P.pack.length=0;__CP.title()});
    ok(await p.evaluate(()=>__CP.purse()===18),'eighteen stars earned are eighteen to spend');
    await p.click('.cp.on [data-cp="fire:title"]');ok(await p.evaluate(()=>__CP.scr==='fire')&&await p.locator('.cp.fire .camphero').count()===1,'the fire opens from the title');
    ok(await p.locator('.cp.fire [data-cp^="pick:"]').count()===9&&await p.evaluate(()=>__CP.shelf().length===9&&__CP.shelf().indexOf('digin')<0),'nine missions told have left nine cards at the fire, and no more');
    await p.click('.cp.fire [data-cp="pick:callco"]');ok((await p.locator('.cp-pick').innerText()).indexOf('Take it for 8 stars')>=0,'a card is read before it is taken, with its price in stars');
    await p.click('.cp.fire [data-cp="take"]');ok(await p.evaluate(()=>__CP.P.pack.join()==='callco'&&__CP.purse()===10&&JSON.parse(localStorage.getItem('lh-campaign')).pack.join()==='callco'),'taking it spends the stars and is kept');
    ok((await p.locator('#cp-purse b').innerText())==='10','the purse on the screen is right');
    await p.click('.cp.fire [data-cp="pick:secondwind"]');await p.click('.cp.fire [data-cp="take"]');ok(await p.evaluate(()=>__CP.P.pack.length===2&&__CP.purse()===2),'a second card, and two stars are left');
    await p.click('.cp.fire [data-cp="pick:hewT"]');ok(await p.locator('.cp.fire [data-cp="take"][disabled]').count()===1,'with too few stars left the next cannot be taken');
    await p.click('.cp.fire [data-cp="drop:secondwind"]');ok(await p.evaluate(()=>__CP.P.pack.join()==='callco'&&__CP.purse()===10),'a card put back gives its stars back');
    ok(await p.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth+1),'the fire fits at '+vp.width);
    await p.evaluate(()=>{__CP.intro('c5b')});ok((await p.locator('.cp-card').innerText()).indexOf('Call the Company')>=0&&await p.locator('.cp.on [data-cp="fire:intro:c5b"]').count()===1,'a larger fight\'s card says what he carries, with a way to the fire');
    await p.evaluate(()=>{__CP.begin('c5b')});await p.waitForTimeout(100);
    ok(await p.evaluate(()=>{var G=__LH.G;return G.ms==='c5b'&&G.u[0].deck.indexOf('callco')>=0&&G.cs.pack.join()==='callco'}),'and it is in his deck when the yard begins');
    /* he is told what is happening: on the place card, over the board, and afterwards */
    await p.evaluate(()=>{__CP.intro('c5b')});{const t=await p.locator('.cp-news').innerText();ok(/Ash fights beside him now/.test(t)&&/The Far Cast/.test(t)&&/Boy with the Horn: makes the others strike harder/.test(t)&&/two tiles/.test(t),'the place card says who is new beside him, what he has learned, what he meets')}
    ok(await p.evaluate(()=>{__CP.intro('p0');return document.querySelectorAll('.cp-news').length===0}),'the first mission has nothing new to announce');
    await p.evaluate(()=>{__CP.said.length=0;delete __CP.P.done.c4b;__CP.begin('c4b')});await p.waitForTimeout(100);
    ok(await p.evaluate(()=>__CP.said.some(function(t){return /^Hollis is with him\.$/.test(t)})&&__CP.said.some(function(t){return /^New in his hand: /.test(t)})),'a mission begun for the first time says who is with him and what is new in his hand');
    await p.evaluate(()=>{__CP.P.done.c4b={stars:2};__CP.said.length=0;__CP.P.tips={};__CP.begin('c5b')});await p.waitForTimeout(100);
    {const d=await p.evaluate(()=>{var u=__LH.G.u[0];return [u.x,u.y]});await tap(d[0],d[1]);await p.evaluate(()=>{var G=__LH.G,f=G.u.filter(function(u){return u.type==='sergeant'})[0],D=G.u[0];G.u.forEach(function(u){if(u!==f&&u.x===D.x&&u.y===D.y-1)u.x=5});f.x=D.x;f.y=D.y-1});
     await tap(d[0],d[1]-1);await p.click('#game [data-a="go"]');await p.waitForTimeout(350);
     ok(await p.evaluate(()=>!!__CP.P.tips.brk&&!!__CP.P.tips.enrage&&__CP.said.some(function(t){return /halved/.test(t)})),'a rule is said the first time it matters (Broken, the sergeant at half health)');
     await p.evaluate(()=>{__CP.said.length=0});await p.click('#game [data-a="endhand"]');await p.waitForTimeout(300);await p.evaluate(()=>{__CP.begin('c5b')});await p.waitForTimeout(100);
     const d2=await p.evaluate(()=>{var G=__LH.G,f=G.u.filter(function(u){return u.type==='sergeant'})[0],D=G.u[0];G.u.forEach(function(u){if(u!==f&&u.x===D.x&&u.y===D.y-1)u.x=5});f.x=D.x;f.y=D.y-1;return [D.x,D.y]});await tap(d2[0],d2[1]);if(!(await p.$('#game .tok.sel')))await tap(d2[0],d2[1]);await tap(d2[0],d2[1]-1);await p.click('#game [data-a="go"]');await p.waitForTimeout(350);
     ok(await p.evaluate(()=>!__CP.said.some(function(t){return /halved/.test(t)})),'and only that once')}
    /* the cards: found so far, and what is still to find */
    await p.evaluate(()=>{__CP.cards('title')});ok(await p.evaluate(()=>__CP.scr==='cards')&&await p.locator('.cp.album .card.back').count()===await p.evaluate(()=>CP.SHOP.length-__CP.shelf().length),'the cards screen shows what is found and a place for each still to find');
    ok(/Sealed since the ford/.test(await p.locator('.cp.album').innerText())&&await p.locator('.cp.album .cp-tips dt').count()>=2,'the Grace\'s cards are kept as sealed, and the rules he has met are written down');
    ok(await p.evaluate(()=>{var f=__CP.found();return f[0]>20&&f[0]<f[1]}),'the count of cards found is short of the whole');
    ok(await p.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth+1),'the cards fit at '+vp.width);
    await p.evaluate(()=>{__CP.P.pack.length=0;__CP.P.pack.push('callco')});
    /* the main menu, and everywhere it leads */
    await p.evaluate(()=>{__CP.title()});ok(await p.locator('.cp-menu .cp-tile').count()===6&&await p.locator('.cp-menu [data-cp^="intro:"]').count()===1,'the menu offers the next mission and six places to go');
    ok(/9 of 14 told/.test(await p.locator('.cp-tile[data-cp="list"]').innerText())&&/found/.test(await p.locator('.cp-tile[data-cp="cards:title"]').innerText()),'each tile says where things stand');
    await p.click('.cp-tile[data-cp="list"]');ok(await p.locator('.cp-road .cp-row.next').count()===1&&await p.locator('.cp-road .cp-row.tall').count()===3&&await p.locator('.cp-road .cp-row.done').count()===9,'the journey is a road: what is told, what is next, a spur for each larger fight');
    await p.evaluate(()=>{__CP.company()});ok(await p.locator('.cp-who').count()>=6&&/Lends/.test(await p.locator('.cp.on').innerText())&&/First beside him in/.test(await p.locator('.cp.on').innerText()),'the company lists everyone who has stood beside him and what each lends');
    await p.evaluate(()=>{__CP.settings()});ok(await p.locator('.cp.on [data-cplevel]').count()===3&&await p.locator('.cp.on [data-pref^="music"]').count()===2,'settings are inside the game');
    await p.click('.cp.on [data-cplevel="1"]');ok(await p.evaluate(()=>__CP.P.level===1)&&await p.getAttribute('.cp.on [data-cplevel="1"]','aria-pressed')==='true','difficulty set from the menu');await p.click('.cp.on [data-cplevel="0"]');
    await p.click('.cp.on [data-cp="forget"]');ok(await p.evaluate(()=>Object.keys(__CP.P.done).length===9),'forgetting progress asks twice');await p.evaluate(()=>{__CP.title()});
    /* the road: the game itself, with his deck and the pack */
    ok(await p.evaluate(()=>!document.querySelector('.cp-tile[data-cp="road"]').disabled),'the road is open once he is on the road');
    await p.click('.cp-tile[data-cp="road"]');await p.waitForTimeout(150);
    ok(await p.evaluate(()=>{var G=__LH.G,g=document.getElementById('game');return __CP.scr==='road'&&!G.ms&&G.map.name==='The Two Fords'&&G.run.deck.indexOf('c_stick')>=0&&G.run.deck.indexOf('callco')>=0&&!g.hasAttribute('data-cp')&&!g.hasAttribute('data-th')}),'it is a run of the game, on the game\'s first ground, with his campaign deck and the pack');
    ok(await p.evaluate(()=>__LH.LH.nm(__LH.G.u.filter(function(u){return u.boss})[0])==='the Captain')&&await p.locator('#m-rest .cp-quit[data-cp="quitroad"]').count()===1,'the game\'s own words stand, and there is a way back to the menu');
    await p.evaluate(()=>{var G=__LH.G;G.u[0].hp=0;G.over={lost:1,t:'The line is broken',s:''};G.run.renown=7;__CP.sweep()});await p.waitForTimeout(80);
    ok(await p.evaluate(()=>__CP.P.road&&__CP.P.road.best===7&&__CP.P.road.runs===1),'a run\'s Renown is kept as his best');
    await p.click('#m-rest .cp-quit');ok(await p.evaluate(()=>__CP.scr==='title'&&document.getElementById('game').getAttribute('data-cp')==='1'&&CP.road===null)&&/Best Renown 7/.test(await p.locator('.cp-tile[data-cp="road"]').innerText()),'leaving the road comes back to the menu, which remembers it');
    await p.evaluate(()=>{__CP.begin('c6')});await p.waitForTimeout(100);ok(await p.evaluate(()=>__LH.G.ms==='c6'&&__LH.LH.nm(__LH.G.u.filter(function(u){return u.type==='ysra'})[0])==='Ysra Tal'),'and a mission after the road is a mission again');
    await p.evaluate(()=>{__CP.begin('c5b')});await p.waitForTimeout(100);
    ok(await p.evaluate(()=>document.getElementById('game').hasAttribute('data-co')&&getComputedStyle(document.querySelector('#m-rest .trio')).display!=='none'),'where the company fights, the triangle is drawn under the board');
    await p.evaluate(()=>{__CP.begin('c6')});await p.waitForTimeout(100);
    ok(await p.evaluate(()=>{var G=__LH.G;return G.u[0].deck.indexOf('digin')<0&&!document.getElementById('game').hasAttribute('data-co')&&getComputedStyle(document.querySelector('#m-rest .trio')).display==='none'}),'the page\'s own scene keeps the page\'s deck, and has no triangle to draw');
    ok(await p.evaluate(()=>{var y=__LH.G.u.filter(function(u){return u.type==='ysra'})[0];return y&&y.img==='tok-ysra-tal'}),'Ysra Tal stands in the clash with the face the Chronicle has for her');
    /* difficulty is the campaign's own switch, and the game's other switches work here */
    ok(await p.locator('[data-cplevel]').count()===3&&await p.getAttribute('[data-cplevel="0"]','aria-pressed')==='true','a difficulty switch on the page, Standard to begin');
    await p.click('[data-cplevel="1"]');await p.evaluate(()=>{__CP.begin('c5b')});await p.waitForTimeout(100);
    ok(await p.evaluate(()=>__LH.G.cs.level===1&&__CP.P.level===1&&__LH.G.ms==='c5b'),'Hard applies from the next mission begun, and does not start a run of the game');
    await p.click('[data-cplevel="0"]');await p.click('[data-pref="quick=true"]');ok(await p.evaluate(()=>__LH.prefs.quick===true&&__LH.G.ms==='c5b'),'quick animation can be set without leaving the mission');await p.click('[data-pref="quick=false"]');
    ok(await p.locator('.prompt pre').count()>=9&&await p.locator('[data-copy]').count()>=9,'the page has prompts for the pictures still to make');
    ok(errs.length===0,'no script errors at '+vp.width+': '+errs.slice(0,3).join(' | '));
    await p.close();
  }
  await b.close();console.log(fails?fails+' of '+checks+' checks failed':'all '+checks+' checks passed');process.exit(fails?1:0);
})();
