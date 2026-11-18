/* The game as an app (game/dist/play/, what the site serves at /play/), on phone screens: it fills the screen and never
   scrolls the page, every button that matters is in reach without scrolling, it offers the home screen, and it opens
   again with no signal.   python3 game/build.py, then: node game/test/play.ui.test.js */
const {chromium}=require('playwright');const path=require('path'),fs=require('fs'),http=require('http');
const ROOT=path.resolve(__dirname,'../dist/play');
const TYPES={'.html':'text/html; charset=utf-8','.js':'text/javascript','.webmanifest':'application/manifest+json','.png':'image/png','.webp':'image/webp','.mp3':'audio/mpeg'};
let fails=0,checks=0;function ok(c,m){checks++;if(!c){fails++;console.log('  FAIL '+m)}}
(async()=>{
  const srv=http.createServer((q,r)=>{let u=decodeURIComponent(q.url.split('?')[0]);if(u.endsWith('/'))u+='index.html';const f=path.join(ROOT,u);
    if(!f.startsWith(ROOT)||!fs.existsSync(f)){r.writeHead(404);r.end();return}r.writeHead(200,{'Content-Type':TYPES[path.extname(f)]||'application/octet-stream'});fs.createReadStream(f).pipe(r)});
  await new Promise(d=>srv.listen(0,'127.0.0.1',d));const URL='http://127.0.0.1:'+srv.address().port+'/';
  const b=await chromium.launch();
  const inView=(p,sel)=>p.evaluate(s=>{var H=innerHeight,W=innerWidth,l=[].filter.call(document.querySelectorAll(s),e=>!e.disabled&&!e.closest('[hidden]')&&e.getBoundingClientRect().width>0);
    return l.length>0&&l.every(function(e){var r=e.getBoundingClientRect();return r.top>=-1&&r.bottom<=H+1&&r.left>=-1&&r.right<=W+1})},sel);
  for(const vp of [{width:390,height:844},{width:390,height:664},{width:360,height:640}]){
    const at=' at '+vp.width+'×'+vp.height;
    const c=await b.newContext({viewport:vp,isMobile:true,hasTouch:true});const p=await c.newPage();const errs=[];
    p.on('pageerror',e=>errs.push(e.message));p.on('console',m=>{if(m.type()==='error'&&!/net::|Failed to load|fonts\./.test(m.text()))errs.push(m.text())});
    await p.addInitScript(()=>{window.LH_FAST=true;window.__buzz=[];try{Object.defineProperty(Navigator.prototype,'vibrate',{configurable:true,value:function(ms){window.__buzz.push(ms);return true}})}catch(e){}});
    await p.goto(URL);await p.waitForTimeout(500);
    const still=()=>p.evaluate(()=>{var e=document.documentElement,g=document.getElementById('game').getBoundingClientRect();return e.scrollHeight<=innerHeight+1&&e.scrollWidth<=innerWidth+1&&Math.abs(g.height-innerHeight)<=1&&g.width<=innerWidth+1});
    ok(await p.evaluate(()=>__CP.scr==='title'&&document.documentElement.classList.contains('app')),'it opens on the menu, as the app'+at);
    ok(await still(),'the game is the whole screen and the page does not scroll'+at);
    ok(await p.locator('.cp.on .app-offer .act').count()===1&&await inView(p,'.cp.on .cp-acts .act.primary'),'the menu offers the full screen, and Begin is in reach'+at);
    /* a mission's card: Begin without scrolling, however long the card */
    await p.evaluate(()=>{__CP.P.all=1;__CP.intro('c5c')});await p.waitForTimeout(150);
    ok(await inView(p,'.cp.on .cp-card>.cp-acts .act'),'on a mission\'s card Begin and the ways back are in reach without scrolling'+at);
    /* the map */
    await p.evaluate(()=>{__CP.begin('c5c')});await p.waitForTimeout(250);
    ok(await still(),'the map does not scroll the page'+at);
    ok(await inView(p,'#m-board')&&await p.evaluate(()=>{var b=document.getElementById('m-board').getBoundingClientRect(),t=document.querySelector('#m-board .tile').getBoundingClientRect();return b.height>t.height*6.5&&t.width>=37}),'the whole board is on the screen, its tiles large enough to tap'+at);
    ok(await inView(p,'#m-rest>.acts .act'),'what he can do is in reach without scrolling'+at);
    ok(await inView(p,'#game>.foot .tgl')&&await inView(p,'#game .cp-quit'),'music, sound and the way out are at the top'+at);
    ok(await p.evaluate(()=>getComputedStyle(document.querySelector('#m-rest .cp-obj .cp-h')).webkitLineClamp==='1'),'the mission\'s rule is folded to a line');
    await p.tap('#m-rest .cp-obj');ok(await p.evaluate(()=>document.querySelector('#m-rest .cp-obj').classList.contains('open')),'a tap opens it');await p.tap('#m-rest .cp-obj');
    /* leaving takes two taps */
    await p.tap('#game .cp-quit');ok(await p.evaluate(()=>__CP.scr==='play'&&/Leave\?/.test(document.querySelector('#game .cp-quit').textContent)),'the first tap on the way out only asks');
    await p.tap('#game .cp-quit');await p.waitForTimeout(150);ok(await p.evaluate(()=>__CP.scr==='list'),'the second leaves');
    /* a clash: the hand and the tray without scrolling */
    await p.evaluate(()=>{__CP.begin('c5c')});await p.waitForTimeout(250);
    const t=await p.evaluate(()=>{var G=__LH.G,d=G.u[0],f=G.u.filter(u=>u.side===1&&u.hp>0&&u.key==='greycloak')[0];d.x=f.x;d.y=f.y+1;G.u.forEach(u=>{if(u!==d&&u.x===d.x&&u.y===d.y)u.y=6});d.mov=Math.max(d.mov,1);return [d.x,d.y,f.x,f.y]});
    await p.tap(`#m-board .tile[data-x="${t[0]}"][data-y="${t[1]}"]`,{force:true});await p.waitForTimeout(100);
    await p.tap(`#m-board .tile[data-x="${t[2]}"][data-y="${t[3]}"]`,{force:true});await p.waitForTimeout(150);
    ok(await inView(p,'#m-rest>.acts .act'),'Engage and Hold are in reach under the forecast'+at);
    await p.locator('#game [data-a="go"]').first().tap();await p.waitForTimeout(500);
    ok(await p.evaluate(()=>!!__LH.G.clash),'the clash opens');
    ok(await inView(p,'#scr-clash .hcard')&&await inView(p,'#c-tray button')&&await inView(p,'#c-stage'),'the stage, the whole hand and the tray are on the screen at once'+at);
    ok(await p.evaluate(()=>{var s=document.getElementById('scr-clash');return s.scrollHeight<=s.clientHeight+1})&&await still(),'and nothing there needs scrolling'+at);
    await p.tap('#scr-clash .hcard');await p.waitForTimeout(150);
    ok(await inView(p,'#c-tray button')&&(await p.locator('#c-tell').innerText()).length>10,'a card read still leaves the tray in reach'+at);
    /* a foe breaks: one short buzz in the hand, and none with it turned off */
    {await p.waitForFunction(()=>!__LH.busy,null,{timeout:3000}).catch(()=>{});
     const id=await p.evaluate(()=>{var G=__LH.G,K=G.clash,L=__LH.LH,C=L.C;K.canBreak=true;K.broken=false;K.fb=0;K.d.hp=K.d.max=60;K.en=9;window.__buzz.length=0;
       var i=-1;K.hand.forEach(function(c,j){if(i<0&&C[c]&&C[c].dmg&&!L.playable(G,j))i=j});return i<0?null:K.hand[i]});
     for(let n=0;id&&n<2;n++){if(await p.evaluate(()=>__LH.G.clash.broken))break;const at2=await p.evaluate(id=>{var e=document.querySelector('#scr-clash .hcard[data-id="'+id+'"]'),r=e.getBoundingClientRect(),x,y;   /* a point of the card that is really on top: in a fanned hand most of it is under a neighbour */
         for(y=r.top+6;y<r.bottom-4;y+=8)for(x=r.left+4;x<r.right-4;x+=6){var top=document.elementFromPoint(x,y);if(top&&e.contains(top))return [x,y]}return null},id);
       if(!at2)break;await p.touchscreen.tap(at2[0],at2[1]);await p.waitForTimeout(150);await p.waitForFunction(()=>!__LH.busy,null,{timeout:3000}).catch(()=>{})}
     await p.waitForFunction(()=>window.__buzz.length>0,null,{timeout:1500}).catch(()=>{});
     ok(!id||await p.evaluate(()=>__LH.G.clash&&__LH.G.clash.broken&&window.__buzz.length===1&&window.__buzz[0]>=20&&window.__buzz[0]<=80),'when the foe breaks the phone gives one short buzz'+at);
     await p.evaluate(()=>{__CP.settings()});ok(await p.locator('.cp.on [data-pref="buzz=false"]').count()===1,'and Settings can turn it off');
     await p.tap('.cp.on [data-pref="buzz=false"]');ok(await p.evaluate(()=>__LH.prefs.buzz===false&&JSON.parse(localStorage.getItem('lh-prefs')).buzz===false),'which is kept');
     await p.evaluate(()=>{__LH.prefs.buzz=true})}
    ok(errs.length===0,'no errors'+at+(errs.length?': '+errs[0]:''));
    await c.close();
  }
  /* on an iPhone the phone will not do it for him: the menu's offer opens the steps; from the home screen there is no offer */
  {const c=await b.newContext({viewport:{width:390,height:664},isMobile:true,hasTouch:true,userAgent:'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'});
   const p=await c.newPage();await p.addInitScript(()=>{window.LH_FAST=true});await p.goto(URL);await p.waitForTimeout(400);
   await p.tap('.cp.on .app-offer .act');await p.waitForTimeout(150);
   ok(/Add to Home Screen/.test(await p.locator('.cp.on').innerText())&&await p.locator('.cp.on [data-cp="title"]').count()===1,'on an iPhone the offer shows the two steps to the home screen, and a way back');
   await c.close();
   const c2=await b.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true});const p2=await c2.newPage();
   await p2.addInitScript(()=>{window.LH_FAST=true;Object.defineProperty(Navigator.prototype,'standalone',{get:function(){return true}})});await p2.goto(URL);await p2.waitForTimeout(400);
   ok(await p2.locator('.cp.on .app-offer').count()===0&&await p2.evaluate(()=>document.documentElement.classList.contains('standalone')),'opened from the home screen it offers nothing: it is already there');
   await c2.close()}
  /* what a phone needs to keep it: the manifest, the icons, and the page again with no signal */
  {const c=await b.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true});const p=await c.newPage();await p.addInitScript(()=>{window.LH_FAST=true});
   await p.goto(URL);await p.waitForTimeout(400);
   const m=await p.evaluate(async()=>{var l=document.querySelector('link[rel=manifest]'),j=await (await fetch(l.href)).json(),okIcons=true;for(var i=0;i<j.icons.length;i++){var r=await fetch(new URL(j.icons[i].src,l.href));okIcons=okIcons&&r.ok}
     var a=await fetch(document.querySelector('link[rel=apple-touch-icon]').href);return {d:j.display,s:j.start_url,n:j.icons.length,ok:okIcons&&a.ok,mask:j.icons.some(function(i){return i.purpose==='maskable'}),o:j.orientation}});
   ok(m.d==='standalone'&&m.s==='./'&&m.n>=3&&m.ok&&m.mask&&m.o==='portrait','the manifest asks for the whole screen, upright, with its icons there');
   ok(await p.evaluate(()=>navigator.serviceWorker.ready.then(function(){return true})),'the page is kept for later');
   await p.waitForTimeout(1500);await p.reload();await p.waitForTimeout(600);
   ok(await p.evaluate(()=>!!navigator.serviceWorker.controller),'and looked after from then on');
   ok(await p.evaluate(async()=>{var ks=await caches.keys(),c=await caches.open(ks.filter(function(k){return k.indexOf('lh-')===0})[0]),r=await c.match('music/map.mp3');return !!r}),'the music is fetched in the background for later');
   await c.setOffline(true);await p.reload().catch(()=>{});await p.waitForTimeout(700);
   ok(await p.evaluate(()=>typeof __CP!=='undefined'&&__CP.scr==='title').catch(()=>false),'with no signal it still opens on the menu');
   ok(await p.evaluate(()=>{var i=document.querySelector('.cp-crest img');return !!i&&i.complete&&i.naturalWidth>0}).catch(()=>false),'with its pictures');
   ok(await p.evaluate(async()=>{var r=await fetch('music/map.mp3',{headers:{Range:'bytes=0-99'}});var b=await r.arrayBuffer();return r.status===206&&b.byteLength===100}).catch(()=>false),'and its music, a piece at a time as a player asks for it');
   await c.close()}
  await b.close();srv.close();
  console.log(fails?fails+' of '+checks+' checks failed':'all '+checks+' checks passed');process.exit(fails?1:0);
})();
