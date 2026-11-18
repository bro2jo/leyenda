/* The campaign on the real page, in a browser: it opens, every mission starts clean, and the prologue plays to its end by taps.
   python3 game/build_campaign.py, then: node game/test/campaign.ui.test.js */
const {chromium}=require('playwright');const path=require('path');
let fails=0,checks=0;function ok(c,m){checks++;if(!c){fails++;console.log('  FAIL '+m)}}
(async()=>{
  const b=await chromium.launch();
  for(const vp of [{width:390,height:844},{width:1200,height:900}]){
    const p=await b.newPage({viewport:vp});const errs=[];
    p.on('pageerror',e=>errs.push(e.message));p.on('console',m=>{if(m.type()==='error'&&!/net::|Failed to load/.test(m.text()))errs.push(m.text())});
    await p.addInitScript(()=>{window.LH_FAST=true;try{localStorage.removeItem('lh-campaign');localStorage.removeItem('lh-suspend')}catch(e){}});
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
    await p.click('#m-rest .cp-quit');ok(await p.evaluate(()=>__CP.scr==='road'&&/Leave\?/.test(document.querySelector('#m-rest .cp-quit').textContent)),'leaving asks first');
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
    ok(await p.locator('.prompt pre').count()>=16&&await p.locator('[data-copy]').count()>=16,'the page has prompts for the pictures still to make');
    /* growing by cards: marks are banked, a rank is his to place, and it is in the hand next time */
    await p.evaluate(()=>{__CP.begin('c5b')});await p.waitForTimeout(100);
    await p.evaluate(()=>{var G=__LH.G;G.earn={marks:{H:4,W:1},bond:{Hollis:3,Maelis:1}};__CP.bank(G);__CP.company()});
    ok(await p.evaluate(()=>__CP.due('H')===1&&__CP.due('W')===0&&__CP.P.bond.Hollis===3)&&await p.locator('.cp.on [data-cp="grow:H"].act').count()===1,'four marks are a rank for Hollis to give, and the company screen says so');
    ok(/in the middle of a lesson/.test(await p.locator('.cp.on').innerText())&&/Fights together: 1 of 3/.test(await p.locator('.cp.on').innerText()),'three fights together are a bond, with its words from the page; one is a start');
    await p.click('.cp.on [data-cp="grow:H"].act');ok(await p.locator('.cp.on [data-cp^="rank:H:"]').count()===3,'the choice is among the cards of Hollis\'s own hand');
    await p.click('.cp.on [data-cp="rank:H:hew"]');ok(await p.evaluate(()=>__CP.P.grow.H.picks.join()==='hew'&&__CP.due('H')===0&&CP.grow.H.join()==='hew')&&await p.locator('.cp.on [data-cp^="rank:"]').count()===0,'one card is raised, and the rank is spent');
    await p.evaluate(()=>{__CP.begin('c5b')});await p.waitForTimeout(100);
    ok(await p.evaluate(()=>{var G=__LH.G,H=G.u.filter(function(u){return u.id==='H'})[0];return H.deck.filter(function(c){return c==='hew_2'}).length===2&&H.fights>=2}),'next time both his Hews are second rank, and his lent card comes risen for the bond');
    /* something to reach, and one foe's reach alone */
    ok(await p.locator('#m-board .tile[data-mark="find"]').count()===1,'the yard has something to reach, marked on the board');
    {const f=await p.evaluate(()=>{var G=__LH.G,u=G.u.filter(function(x){return x.type==='pitch'})[0];return [u.x,u.y]});await tap(5,3);await tap(f[0],f[1]);
     const one=await p.locator('#m-board .tile.dz').count();await p.click('#game [data-a="dz"]');const all=await p.locator('#m-board .tile.dz').count();await p.click('#game [data-a="dz"]');ok(one>0&&one<all,'tapping one foe shows where he alone can strike ('+one+' tiles of '+all+')')}
    /* how it went: the telling ends with the fight's own account */
    await p.evaluate(()=>{var G=__LH.G,D=G.u[0],f=G.u.filter(function(u){return u.type==='sergeant'})[0];G.u.forEach(function(u){if(u.side===1&&u!==f)u.hp=0;if(u!==f&&u!==D&&u.x===D.x&&u.y===D.y-1)u.x=5});f.x=D.x;f.y=D.y-1;f.hp=1;D.moved=false;D.attacked=false});
    {const d=await p.evaluate(()=>{var u=__LH.G.u[0];return [u.x,u.y]});await tap(5,3);await tap(d[0],d[1]);if(!(await p.$('#game .tok.sel')))await tap(d[0],d[1]);await tap(d[0],d[1]-1);await p.click('#game [data-a="go"]');await p.waitForTimeout(200);
     await p.evaluate(()=>{var K=__LH.G.clash;K.hand=['c_stick'];K.fb=0;K.en=3});const c=p.locator('#c-hand .hcard').first();await p.evaluate(()=>{__LH.LH.play(__LH.G,0);__LH.LH.closeClash(__LH.G);__LH.after()});
     await p.waitForFunction(()=>__CP.scr==='outro',null,{timeout:8000}).catch(()=>{});
     ok(await p.evaluate(()=>__CP.scr==='outro')&&/How it went/.test(await p.locator('.cp-result').innerText())&&/Darrow/.test(await p.locator('.cp-result').innerText())&&/Found on the ground: 0 of 1/.test(await p.locator('.cp-result').innerText()),'the telling ends with how it went: who fought, what was found')}
    /* the long stair: the view follows the company down */
    await p.evaluate(()=>{__CP.begin('c4c')});await p.waitForTimeout(100);
    ok(await p.evaluate(()=>{var G=__LH.G;G.u.forEach(function(u){if(u.side===1)u.hp=0});G.u.forEach(function(u,i){if(u.side===0&&u.id!=='D'){u.x=i%6;u.y=3}});var D=G.u[0];D.x=4;D.y=4;D.moved=false;return __LH.LH.move(G,D,4,5)&&G.cs.top===3})&&/step \d+ of 1117/.test(await p.locator('#m-top').innerText()),'on the Steps the board moves on when the company has come down, and the heading counts the steps');
    await tap(5,0);await p.waitForTimeout(80);ok(await p.evaluate(()=>{var G=__LH.G,t=document.querySelector('#m-board .tile[data-x="1"][data-y="4"]');return G.map.rows[4]==='~d~~~~'&&t.getAttribute('data-t')==='d'&&!!document.querySelector('.unit[data-u^="reach"]')}),'and the ground and what stands on it are drawn anew');
    /* set down and picked up again */
    await p.evaluate(()=>{__CP.begin('c5b')});await p.waitForTimeout(100);
    {const d=await p.evaluate(()=>{var G=__LH.G,D=G.u[0];__LH.LH.move(G,D,D.x,D.y-1);__CP.keepBoard();return [D.x,D.y,G.turn]});
     ok(await p.evaluate(()=>{var s=__CP.suspended();return !!s&&s.ms==='c5b'&&s.g.u[0].moved===true}),'the board is kept whenever it is his move');
     /* as if the page had been closed: the board in the game is thrown away, and only what was kept remains */
     await p.evaluate(()=>{var G=__LH.G;window.__old=G;G.u[0].x=0;G.u[0].y=6;G.turn=99;__CP.title()});
     ok(await p.evaluate(()=>__CP.scr==='title')&&await p.locator('.cp.on [data-cp="resume"]').count()===1&&/The Yard at Coldmere/.test(await p.locator('.cp.on [data-cp="resume"]').innerText()),'the menu offers to pick it up again, by name');
     await p.click('.cp.on [data-cp="resume"]');await p.waitForTimeout(150);
     ok(await p.evaluate(d=>{var G=__LH.G,D=G.u[0];return __CP.scr==='play'&&G!==window.__old&&G.ms==='c5b'&&D.x===d[0]&&D.y===d[1]&&D.moved&&G.turn===d[2]&&document.getElementById('game').getAttribute('data-th')==='yard'&&!!document.querySelector('#m-rest .cp-obj')},d),'and the board is as he left it: where he stood, his move spent, the aim under the board');
     ok(await p.evaluate(()=>{var G=__LH.G,W=G.u.filter(function(u){return u.id==='W'})[0];var r=__LH.LH.reach(G,W);var k=Object.keys(r).filter(function(q){return q!==W.x+','+W.y})[0].split(',');return __LH.LH.move(G,W,+k[0],+k[1])&&__LH.LH.endTurn(G)}),'and it plays on');
     await p.evaluate(()=>{__CP.forgetBoard()})}
    /* playtest switches, in Settings: everything the old playtest page could do, inside the game */
    await p.evaluate(()=>{__CP.reset();__CP.settings()});
    ok(await p.locator('.cp.on [data-cp^="pt:"]').count()===8&&await p.locator('.cp.on [data-pref^="rounds"]').count()===2,'Settings has a Playtest section');
    await p.evaluate(()=>{__CP.list()});const locked0=await p.locator('.cp-row.locked').count();await p.evaluate(()=>{__CP.settings()});
    await p.click('.cp.on [data-cp="pt:all:1"]');await p.evaluate(()=>{__CP.list()});ok(locked0>0&&await p.locator('.cp-row.locked').count()===0,'every mission can be opened');
    await p.evaluate(()=>{__CP.title()});ok(await p.evaluate(()=>!document.querySelector('.cp-tile[data-cp="road"]').disabled)&&/Playtest switches are on/.test(await p.locator('.cp-menu').innerText()),'which opens the road too, and the menu says the switches are on');
    await p.evaluate(()=>{__CP.settings()});await p.click('.cp.on [data-cp="pt:stars"]');await p.click('.cp.on [data-cp="pt:shelf:1"]');await p.click('.cp.on [data-cp="pt:marks"]');
    ok(await p.evaluate(()=>__CP.purse()===10&&__CP.shelf().length===CP.SHOP.length&&__CP.due('H')===1&&__CP.due('W')===1),'ten stars, every card at the fire, a rank for each fighter');
    await p.click('.cp.on [data-cp="pt:deck:1"]');await p.click('.cp.on [data-pref="rounds=3"]');ok(await p.evaluate(()=>__CP.roadDeck().length>=10+CP.SHOP.length&&__LH.prefs.rounds===3),'the road can be taken with every camp card, and with clashes of three rounds');
    await p.click('.cp.on [data-pref="rounds=1"]');await p.evaluate(()=>{__CP.reset()});ok(await p.evaluate(()=>__CP.purse()===0&&!__CP.P.all&&!__CP.P.roadAll),'forgetting progress turns the switches off');
    /* what the old page showed and the game's page now shows */
    ok(await p.locator('#sfx-table tr').count()>=30&&await p.locator('#market-gallery .card').count()>=18&&await p.locator('.words dt').count()>=10,'the page lists the sounds to make, the cards and what the icons mean');
    {const pr=await p.evaluate(()=>[].map.call(document.querySelectorAll('.prompt pre'),function(e){return e.textContent}));
     {const fs=require('fs'),has=(k,n)=>fs.existsSync(path.resolve(__dirname,'../art/'+k+'/'+n+'.webp')),dir=k=>fs.readdirSync(path.resolve(__dirname,'../art/'+k)).filter(f=>/\.webp$/.test(f)).length;
     const L=await p.evaluate(()=>['who','tok','card'].map(k=>[].map.call(document.querySelectorAll('h3[data-'+k+']'),e=>e.getAttribute('data-'+k))));
     ok(L[0].length===19-dir('figures')&&L[0].every(n=>!has('figures',n))&&L[1].length>=5&&L[1].every(n=>!has('tokens',n))&&L[2].length>=25-dir('cards')&&L[2].every(n=>!has('cards',n)),'a prompt for every figure, every token of what is only seen on the map, and every card still wanting a picture, and none for one that is filed');}
     ok(await p.evaluate(()=>{var l=document.querySelectorAll('ol.ranked>li h3');return l[0].getAttribute('data-who')==='hollis'&&!document.querySelector('h3[data-who="pikeman"],h3[data-who="captain"],h3[data-card="b_strike"]')&&[].every.call(document.querySelectorAll('ol.ranked>li .why'),function(e){return e.textContent.length>8})}),'they are in order, the most noticed first, each with its reason, and what is made has left the list');
     ok(pr.every(function(t){return t.split(/\s+/).length<=150&&/^Fantasy RPG /.test(t)&&/Painterly semi-realistic/.test(t)}),'every prompt is whole and short: the kind of picture first, its own style and format, 150 words at most');
     ok(pr.every(function(t){return !/gambeson|kettle|madder|hauberk|cuirass|coif|lymer|surcoat|buff coat/i.test(t)}),'and in plain words an image model knows');
     ok(await p.locator('h3[data-who="crossbowman"] .todo').count()===1&&/Made already: .*Captain/.test(await p.locator('#cp-made').innerText()),'what is still to make is marked, and what is made is named')}
    ok(errs.length===0,'no script errors at '+vp.width+': '+errs.slice(0,3).join(' | '));
    await p.close();
  }
  await b.close();console.log(fails?fails+' of '+checks+' checks failed':'all '+checks+' checks passed');process.exit(fails?1:0);
})();
