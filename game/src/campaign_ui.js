/* The Line and the Hand: the campaign's screens. It sits on top of the game's own screen (ui.js), which it does not change:
   it starts a mission through the same door the page's "new run" buttons use, lays its own title, mission list and place cards
   over the board, and writes the objective into the map screen each time that screen is redrawn. */
(function(){
'use strict';
var LH=window.LH,CP=window.CP,X=window.__LH,root=document.getElementById('game');if(!root||!CP||!X)return;
var A='art/',AS=window.LH_ASSETS||{art:[]};
function has(n){return AS.art.indexOf(n)>=0}
/* a card whose picture has been made wears it, at every rank and as its combo */
(function(){var ca=AS.cardart||{},C=LH.C,id;for(id in C){var b=C[id].base||id;if(ca[b])C[id].art=ca[b]}})();
function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/"/g,'&quot;')}
function $(id){return document.getElementById(id)}
var P={};try{P=JSON.parse(localStorage.getItem('lh-campaign')||'{}')||{}}catch(e){}P.done=P.done||{};P.pack=(P.pack||[]).filter(function(id){return CP.SHOP.indexOf(id)>=0});P.level=P.level||0;P.tips=P.tips||{};P.grow=P.grow||{};P.bond=P.bond||{};P.finds=P.finds||{};
function save(){try{localStorage.setItem('lh-campaign',JSON.stringify(P))}catch(e){}}
var layer=document.createElement('div');layer.className='cp';root.appendChild(layer);root.setAttribute('data-cp','1');
var kick=document.createElement('button');kick.type='button';kick.hidden=true;kick.setAttribute('data-newrun','');document.body.appendChild(kick);
var scr='title',shown=false,ALL=!!window.LH_ALL||/[?&]all\b/.test(location.search);
/* playtest switches (Settings): every mission open, stars to try the fire with. They are kept with the progress and say so on the menu. */
function all(){return ALL||!!P.all}
function open(i){return all()||i===0||!!P.done[CP.ORDER[i-1]]}
function nextId(){for(var i=0;i<CP.ORDER.length;i++)if(!P.done[CP.ORDER[i]])return CP.ORDER[i];return null}
function starRow(n,of){var h='<span class="cp-stars" aria-label="'+n+' of '+of+'">';for(var i=0;i<of;i++)h+='<i class="'+(i<n?'on':'')+'">★</i>';return h+'</span>'}
function show(html,cls){layer.className='cp on '+(cls||'');layer.innerHTML=html;layer.scrollTop=0;if(typeof toastOff==='function'&&tbox)toastOff()}
function hide(){layer.className='cp';layer.innerHTML=''}
/* ---------- stars are what he has to spend at the fire: a camp card costs twice its price in spoils ---------- */
var TALL=CP.ORDER.filter(function(id){return !!CP.MS[id].tall});
function starsAll(){var n=P.bonus||0;CP.ORDER.forEach(function(k){if(P.done[k])n+=P.done[k].stars||0});return n}   /* only missions there are: a retired one's stars are not spent */
function cost(id){return LH.C[id].p*2}
function shelf(){return P.shelfAll?CP.SHOP.slice():CP.shelf(P.done)}
function trimPack(){var sh=shelf();P.pack=P.pack.filter(function(id){return sh.indexOf(id)>=0})}
function findsAll(){var n=0;for(var k in P.finds)n+=P.finds[k]||0;return n}
function purse(){return starsAll()+findsAll()-P.pack.reduce(function(n,id){return n+cost(id)},0)}
/* ---------- growing by cards: marks earned in fights are banked here, and each rank they buy is his to place ---------- */
var WHO={H:'Hollis',A:'Ash',W:'Wren'},WIMG={H:'hollis',A:'ash',W:'wren'};
function gr(id){return P.grow[id]||(P.grow[id]={m:0,picks:[]})}
function due(id){return Math.max(0,CP.levelOf(gr(id).m)-gr(id).picks.length)}
function dueAll(){return Object.keys(WHO).reduce(function(n,id){return n+due(id)},0)}
function syncGrow(){var g={};Object.keys(WHO).forEach(function(id){g[id]=gr(id).picks.slice()});CP.grow=g;CP.bond=P.bond}
/* take what a board has earned: marks for those who fought, a fight nearer a bond for whoever stood beside him */
function bank(G){var e=G&&G.earn,out={marks:{},bonds:[]},k;if(!e)return out;
  for(k in e.marks)if(WHO[k]&&e.marks[k]){gr(k).m+=e.marks[k];out.marks[k]=e.marks[k]}
  for(k in e.bond)if(CP.BONDS[k]&&e.bond[k]){var was=P.bond[k]||0,now=was+e.bond[k];P.bond[k]=now;if((was<CP.BOND1&&now>=CP.BOND1)||(was<CP.BOND2&&now>=CP.BOND2))out.bonds.push(k)}
  G.earn={marks:{},bond:{}};save();syncGrow();return out}
var growBack='company';
function grow(id,back){
  if(back)growBack=back;scr='grow';var g=gr(id),C=LH.C,n=due(id),nextAt=CP.LEVELS[g.picks.length+n];
  var h='<div class="cp-top"><b>'+WHO[id]+'</b>'+btn(growBack,'Back','','mini')+'</div>'+
    '<div class="cp-who me"><img src="'+A+WIMG[id]+'.webp" alt=""><span><b>'+(n?'A rank to give':'Nothing to give yet')+'</b><small>'+g.m+' marks'+(nextAt?' · the next at '+nextAt:' · every card at its third')+'</small><span class="cp-dim">A mark for every fight '+WHO[id]+' takes, another for a foe sent off. Each rank raises every copy of one card, for good.</span></span></div>'+
    '<span class="lbl sec">'+X.svg('deck')+(n?'Choose the card to raise':'The hand as it stands')+'</span><div class="hand3">'+CP.GROW[id].map(function(c){var r=CP.rankOf(g.picks,c),cur=r>1?c+'_'+r:c,nx=r<3?c+'_'+(r+1):null;
      return '<div class="cp-up"><div class="cp-upc">'+X.cardHTML(nx&&n?nx:cur,{tag:nx&&n?'button':'div',cls:nx&&n?'fresh':'',attrs:nx&&n?' data-cp="rank:'+id+':'+c+'"':''})+'</div><small>'+(nx?(n?'Now '+(r>1?['','I','II','III'][r]:'I')+': '+LH.cardText(cur).replace(/<[^>]+>/g,''):'Rank '+['','I','II','III'][r]):'Third rank: as far as it goes')+'</small></div>'}).join('')+'</div>';
  show(h,'scroll fire');
}
/* ---------- a board set down and picked up again: saved whenever it is his move, kept in this browser ---------- */
var SKEY='lh-suspend',stimer=null,slast='';
function suspended(){try{var d=JSON.parse(localStorage.getItem(SKEY)||'null');return d&&d.g&&d.g.u?d:null}catch(e){return null}}
function forgetBoard(){slast='';clearTimeout(stimer);try{localStorage.removeItem(SKEY)}catch(e){}}
function keepBoard(){var G=X.G;if(!G||X.busy||G.clash||(scr!=='play'&&scr!=='road')||(scr==='play'&&(!G.ms||G.over)))return;
  if(G.phase!=='player'||(G.over&&!G.over.win))return;
  try{var j=JSON.stringify({v:1,ms:G.ms||null,road:scr==='road'?CP.road:null,th:root.getAttribute('data-th')||'',co:root.hasAttribute('data-co'),g:G});if(j===slast)return;slast=j;localStorage.setItem(SKEY,j)}catch(e){}}
function keepSoon(){clearTimeout(stimer);stimer=setTimeout(keepBoard,500)}
function resume(){
  var d=suspended();if(!d||X.busy)return;var name=d.ms&&CP.MS[d.ms]?CP.MS[d.ms].n:'The road';if(d.ms&&!CP.MS[d.ms]){forgetBoard();return title()}
  X.curtain('march',esc(name),'Picked up where he left it',function(){
    CP.resumeG=d.g;CP.pending=null;CP.road=d.ms?null:(d.road||roadDeck());
    if(d.ms){root.setAttribute('data-cp','1');root.setAttribute('data-th',d.th||'');if(d.co)root.setAttribute('data-co','1');else root.removeAttribute('data-co')}
    else{root.removeAttribute('data-cp');root.removeAttribute('data-th');root.removeAttribute('data-co')}
    kick.click();scr=d.ms?'play':'road';shown=!d.ms;roadSaved=false;hide();toastOff();sweep();
    var G=X.G;if(!d.ms&&G.over&&G.over.win)setTimeout(function w(){if(X.busy)return setTimeout(w,120);X.after()},60);
  });
}
function names(l){return l.map(function(id){return LH.C[id].n}).join(', ')}
function starCard(id,cls,act){return X.cardHTML(id,{tag:'button',price:1,cls:cls,attrs:' data-cp="'+act+':'+id+'"'}).replace(/<span class="price num">.*?<\/span>/,'<span class="price num star">★ '+cost(id)+'</span>')}
function btnLink(a,label){return '<button type="button" class="linkbtn" data-cp="'+a+'">'+label+'</button>'}
function btn(a,label,small,cls){return '<button type="button" class="act '+(cls||'')+'" data-cp="'+a+'"><b>'+label+'</b>'+(small?'<small>'+small+'</small>':'')+'</button>'}

/* ---------- title, missions, the place card, the telling after ---------- */
/* ---------- the main menu: where he is, and everywhere he can go from here ---------- */
function tile(a,icon,name,small,cls,off){return '<button type="button" class="cp-tile '+(cls||'')+'" data-cp="'+a+'"'+(off?' disabled':'')+'><span class="ti">'+icon+'</span><b>'+name+'</b><small>'+small+'</small></button>'}
function roadOpen(){return all()||!!P.done.c4c}   /* he is on the road once the Steps are behind him */
function met(){var seen={},l=[];CP.ORDER.forEach(function(id,i){if(!open(i))return;var p=CP.profile(id),n;for(n in p.all)if(!seen[n]){seen[n]=1;l.push({n:n,img:p.img[n],first:id})}
    l.forEach(function(o){if(p.all[o.n]){if(p.fights[o.n])o.fights=1;if(p.tends[o.n])o.tends=1;if(p.lends[o.n])o.lend=p.lends[o.n];if(p.img[o.n])o.img=p.img[o.n]}})});return l}
function arm(b){b.classList.add('sure');b._t=b.textContent;b.textContent='Leave? Tap again';setTimeout(function(){b.classList.remove('sure');if(b._t)b.textContent=b._t},3000)}
/* on a phone, as an app (src/app.js, only on the page at /play/): the menu offers the home screen or the full screen
   until it has one, and a sheet says how where the phone will not do it for him */
function appOffer(){var o=window.__APP&&window.__APP.offer();return o?'<div class="cp-acts app-offer">'+btn('app:'+o.k,o.t,o.s)+'</div>':''}
function appSheet(){
  scr='app';var ios=window.__APP&&window.__APP.ios,sh='<span class="glyph"><svg viewBox="0 0 24 24"><path d="M12 15V3M8 7l4-4 4 4M5 11v9h14v-9"/></svg></span>';
  show('<div class="cp-menu app-sheet"><span class="cp-lbl">On his phone</span><h2>The whole screen</h2>'+
    '<p>From the home screen it opens like any app: no browser bars, its own icon, and it plays without signal.</p><ol>'+
    (ios?'<li>In <b>Safari</b>, tap <b>Share</b> '+sh+' in the bar.</li><li>Choose <b>Add to Home Screen</b>, then <b>Add</b>.</li>'
        :'<li>Open the browser\'s <b>menu</b> (the three dots).</li><li>Choose <b>Add to Home screen</b> or <b>Install app</b>.</li>')+
    '<li>Open it from the new icon, and from the icon from then on.</li></ol>'+
    (ios?'<p class="cp-note">On an iPhone the icon keeps its own progress, apart from Safari\'s: add it first, then play.</p>':'')+
    '<div class="cp-acts">'+btn('title','Back to the menu','')+'</div></div>','scroll');
}
function title(){
  scr='title';var nx=nextId(),n=CP.ORDER.filter(function(k){return P.done[k]}).length,M=nx?CP.MS[nx]:null,f=found(),R=P.road||{},sus=suspended(),dn=dueAll();
  show('<div class="cp-menu"><span class="cp-lbl">The Unkneeling</span><h2>The Line and the Hand</h2>'+
    '<div class="cp-crest"><img src="'+A+'high-guard.webp" alt=""></div>'+
    '<div class="cp-acts">'+(sus?btn('resume','Pick it up again',(sus.ms&&CP.MS[sus.ms]?CP.MS[sus.ms].n:'The road')+' · turn '+sus.g.turn,'primary'):'')+(M?btn('intro:'+nx,n?'Go on':'Begin',M.book+' · '+M.n,sus?'':'primary'):btn('list','Every mission is told',CP.END.t,sus?'':'primary'))+'</div>'+
    '<div class="cp-tiles">'+
      tile('list',X.svg('road'),'The journey',n+' of '+CP.ORDER.length+' told · ★ '+starsAll())+
      tile('road',X.svg('swords'),'The road',roadOpen()?(R.best?'Best Renown '+R.best:'Three crossings, his own deck'):'Opens when he is on the road','',!roadOpen())+
      tile('fire:title',X.svg('tent'),'The fire',purse()+' stars to spend')+
      tile('cards:title',X.svg('deck'),'The cards',f[0]+' of '+f[1]+' found')+
      tile('company',X.svg('heart'),'The company',dn?dn+(dn>1?' ranks':' rank')+' to give':met().length?met().length+' beside him so far':'Nobody yet',dn?'hot':'')+
      tile('settings',X.svg('pillar'),'Settings',['Gentle','Standard','Hard'][(P.level||0)+1]+(X.prefs.music?' · music':'')+(X.prefs.sound?' · sound':''))+
    '</div>'+appOffer()+(P.all||P.bonus||P.shelfAll||P.roadAll?'<p class="cp-note">Playtest switches are on (Settings).</p>':'')+'<p class="cp-note">Nothing here changes the story. A mission that goes wrong is only played again: the page has already happened.</p></div>','scroll');
}
/* the journey: the missions as a road, a spur for each fight told larger than the page */
function list(){
  scr='list';var h='<div class="cp-top"><b>The journey</b><span class="cp-topacts">'+btn('fire:list','The fire ★ '+purse(),'','mini')+btn('title','Menu','','mini')+'</span></div><div class="cp-road">',book='',nx=nextId();
  CP.ORDER.forEach(function(id,i){var M=CP.MS[id],d=P.done[id],op=open(i);
    if(M.book!==book){book=M.book;h+='<span class="cp-book">'+esc(book)+'</span>'}
    h+='<button type="button" class="cp-row'+(op?'':' locked')+(d?' done':'')+(M.tall?' tall':'')+(id===nx?' next':'')+'" data-cp="intro:'+id+'"'+(op?'':' disabled')+'><span class="cp-n">'+(d?'★':i+1)+'</span><span class="cp-rt"><b>'+esc(M.n)+'</b><small>'+esc(op?(M.tall?'Told larger than the page · ':'')+M.place:'Not yet')+'</small></span>'+(d?starRow(d.stars,3)+(P.finds[id]?'<span class="cp-fd" title="found on the ground">◆</span>':''):id===nx?'<span class="cp-next">Next</span>':'')+'</button>'});
  h+='</div><div class="cp-end"><b>'+CP.END.t+'</b><span>'+CP.END.s+'</span></div>';
  show(h,'scroll');
}
/* the company: everyone who has stood beside him so far, and what each brings */
function company(){
  scr='company';var l=met(),C=LH.C,last=null;CP.ORDER.forEach(function(id,i){if(open(i))last=id});var p=CP.profile(last),M=CP.MS[last];
  var h='<div class="cp-top"><b>The company</b>'+btn('title','Menu','','mini')+'</div>'+
    '<div class="cp-who me"><img src="'+A+(has('darrow')?'darrow':'darrow1')+'.webp" alt=""><span><b>Ser Darrow</b><small>'+esc(M.level)+'</small><span class="cp-dim">Health '+p.hp+' · '+p.br+' breath · a hand of '+p.hn+' · '+(p.mov?'moves '+p.mov:'held to his place')+' <i>(as of '+esc(M.n)+')</i></span></span></div>';
  h+=l.length?l.map(function(o){var role=[];if(o.fights)role.push('fights with a hand of cards');if(o.tends)role.push('tends');if(!o.fights&&!o.tends)role.push('stands by');
    var gid=null,k;for(k in WHO)if(WHO[k]===o.n)gid=k;var b=P.bond[o.n]||0,B=CP.BONDS[o.n],extra='';
    if(gid&&o.fights){var g=gr(gid),nd=due(gid),na=CP.LEVELS[g.picks.length+nd];extra+='<span class="cp-meter"><i style="width:'+Math.min(100,na?100*g.m/na:100)+'%"></i></span><span class="cp-dim">'+g.m+' marks'+(na?' of '+na:'')+' · '+CP.GROW[gid].map(function(c){return C[c].n+' '+['','I','II','III'][CP.rankOf(g.picks,c)]}).join(', ')+'. A deck of '+CP.KIT[gid].length+', with the Strikes and Guards everyone carries.</span>'+
      (nd?'<button type="button" class="act primary" data-cp="grow:'+gid+'"><b>'+nd+(nd>1?' ranks':' rank')+' to give</b><small>Choose the card to raise</small></button>':'<button type="button" class="linkbtn" data-cp="grow:'+gid+'">See the hand</button>')}
    if(B)extra+='<span class="cp-dim">'+(b>=CP.BOND2?'Bond, twice over: the lent card comes risen, and he starts with block beside '+esc(o.n)+'.':b>=CP.BOND1?'Bond: the lent card comes already risen. '+(CP.BOND2-b)+' more fights together for the second.':'Fights together: '+b+' of '+CP.BOND1+' for a bond.')+'</span>'+(b>=CP.BOND1?'<span class="cp-words">'+esc(B[0])+' <i>'+esc(B[1])+'</i></span>':'');
    return '<div class="cp-who"><img src="'+A+(o.img&&has(o.img)?o.img:'brother')+'.webp" alt=""><span><b>'+esc(o.n)+'</b><small>'+esc(role.join(' · '))+'</small><span class="cp-dim">'+(o.lend&&C[o.lend]?'Lends '+esc(C[o.lend].n)+': '+LH.cardText(o.lend).replace(/<[^>]+>/g,''):'')+' <i>First beside him in '+esc(CP.MS[o.first].n)+'.</i></span>'+extra+'</span></div>'}).join(''):'<span class="cp-dim">Nobody has stood beside him yet.</span>';
  show(h,'scroll');
}
/* settings, inside the game */
var sure=false;
function settings(){
  scr='settings';function seg(l){return '<span class="seg">'+l.join('')+'</span>'}
  function pref(k,v,t){return '<button type="button" data-pref="'+k+'='+v+'" aria-pressed="'+(String(X.prefs[k])===String(v))+'">'+t+'</button>'}
  function lev(v,t){return '<button type="button" data-cplevel="'+v+'" aria-pressed="'+((P.level||0)===v)+'">'+t+'</button>'}
  show('<div class="cp-top"><b>Settings</b>'+btn('title','Menu','','mini')+'</div>'+
    '<div class="cp-set"><span class="lbl">Difficulty</span>'+seg([lev(-1,'Gentle'),lev(0,'Standard'),lev(1,'Hard')])+'<span class="cp-dim">What a foe deals and how long a man stands, from the next mission begun. The road uses it too.</span></div>'+
    '<div class="cp-set"><span class="lbl">Animation</span>'+seg([pref('quick',false,'Full'),pref('quick',true,'Quick')])+'<span class="cp-dim">Quick halves every wait. A curtain goes on at a tap either way.</span></div>'+
    '<div class="cp-set"><span class="lbl">Music</span>'+seg([pref('music',false,'Off'),pref('music',true,'On')])+'</div>'+
    '<div class="cp-set"><span class="lbl">Sound</span>'+seg([pref('sound',false,'Off'),pref('sound',true,'On')])+'</div>'+
    '<div class="cp-set"><span class="lbl">Vibration</span>'+(X.canBuzz()?seg([pref('buzz',false,'Off'),pref('buzz',true,'On')])+'<span class="cp-dim">A short buzz when a foe breaks.</span>':'<span class="cp-dim">A short buzz when a foe breaks, on phones whose browser can. This one cannot (an iPhone\'s has no way to).</span>')+'</div>'+
    '<div class="cp-set"><span class="lbl">Playtest</span>'+
      seg(['<button type="button" data-cp="pt:all:0" aria-pressed="'+!P.all+'">Missions in order</button>','<button type="button" data-cp="pt:all:1" aria-pressed="'+!!P.all+'">Every mission open</button>'])+
      seg(['<button type="button" data-cp="pt:shelf:0" aria-pressed="'+!P.shelfAll+'">The fire as earned</button>','<button type="button" data-cp="pt:shelf:1" aria-pressed="'+!!P.shelfAll+'">Every card at the fire</button>'])+
      seg(['<button type="button" data-cp="pt:deck:0" aria-pressed="'+!P.roadAll+'">The road with his deck</button>','<button type="button" data-cp="pt:deck:1" aria-pressed="'+!!P.roadAll+'">With every camp card</button>'])+
      seg([pref('rounds',1,'A clash on the road: one hand'),pref('rounds',3,'Up to three rounds')])+
      '<span class="cp-acts2"><button type="button" class="act" data-cp="pt:stars"><b>Ten stars</b><small>'+(P.bonus?P.bonus+' given so far':'To try the fire with')+'</small></button><button type="button" class="act" data-cp="pt:marks"><b>A rank for each fighter</b><small>Marks to the next rank, for Hollis, Ash and Wren</small></button></span>'+
      '<span class="cp-dim">For trying things. Every mission open also opens the road. None of it is fair play; Forget my progress turns it all off.</span></div>'+
    '<div class="cp-set"><span class="lbl">Progress</span><button type="button" class="act'+(sure?' warn':'')+'" data-cp="forget"><b>'+(sure?'Tap again to forget everything':'Forget my progress')+'</b><small>'+(sure?'Stars, cards, the pack and the rules he has met':'Start from the ford again')+'</small></button><span class="cp-dim">Kept in this browser only.</span></div>');
}
/* the road: three crossings of the game itself, with the deck he has in the campaign and the pack from the fire */
function roadDeck(){var d=null;CP.ORDER.forEach(function(id,i){var k=CP.MS[id].party.D.deck;if(open(i)&&k&&k.length>=10)d=k});return (d||[]).concat(P.pack,P.roadAll?CP.SHOP.filter(function(c){return P.pack.indexOf(c)<0}):[])}
var roadSaved=false;
function road(){
  if(X.busy||!roadOpen())return;
  X.curtain('march','The road','Three crossings, three captains',function(){
    CP.pending=null;CP.road=roadDeck();X.prefs.level=P.level||0;root.removeAttribute('data-cp');root.removeAttribute('data-th');root.removeAttribute('data-co');
    kick.click();scr='road';shown=true;roadSaved=false;hide();sweep();
  });
}
function leaveRoad(){if(X.busy)return;bank(X.G);forgetBoard();CP.road=null;root.setAttribute('data-cp','1');title()}
function intro(id){
  scr='intro';var M=CP.MS[id];
  show('<div class="cp-card">'+(has('place-'+M.art)?'<div class="cp-pic"><img src="'+A+'place-'+M.art+'.webp" alt=""></div>':'')+
    '<span class="cp-lbl">'+esc(M.book)+(M.book==='Prologue'?'':' · '+esc(M.ch.split(' · ')[0]))+'</span><h2>'+esc(M.n)+'</h2>'+
    '<p class="cp-where">'+esc(M.place)+'<br><span>'+esc(M.when)+'</span></p>'+
    M.intro.map(function(p){return '<p>'+esc(p)+'</p>'}).join('')+
    '<p class="cp-quote">'+esc(M.quote)+'</p>'+
    (M.tall?'<p class="cp-read">'+esc(M.tall)+'</p>':'')+
    '<div class="cp-brief"><span class="cp-lbl">Ser Darrow · '+esc(M.level)+'</span><span>'+esc(typeof M.objective==='function'?briefOf(id):M.objective)+'</span></div>'+
    newsHTML(id)+
    (M.tall?'<div class="cp-brief"><span class="cp-lbl">The pack · from the fire</span><span>'+(P.pack.length?esc(names(P.pack)):'Nothing in it yet.')+' <span class="cp-dim">'+purse()+' stars to spend.</span></span></div>':'')+
    '<div class="cp-acts">'+btn('go:'+id,'Begin','','primary')+(M.tall?btn('fire:intro:'+id,'The fire','Change what he carries'):'')+btn('list','Missions','')+'</div></div>','scroll');
}
/* what is new in a mission, on its place card: who is beside him, what he carries, what he meets */
function nfIcon(x){
  if(x.k==='join')return x.img&&has(x.img)?'<img class="nf" src="'+A+x.img+'.webp" alt="">':'<span class="nf ic-b">'+X.svg('heart')+'</span>';
  if(x.k==='foe')return x.key&&(AS.tok||[]).indexOf(x.key)>=0?'<img class="nf foe" src="'+A+'tok-'+x.key+'.webp" alt="">':'<span class="nf ic-b foe">'+X.svg('swords')+'</span>';
  if(x.k==='card')return '<span class="nf nc t-'+LH.C[x.id].t+'">'+X.svg('deck')+'</span>';
  return '<span class="nf ic-b">'+X.svg(x.k==='body'?'heart':x.k==='lost'?'x':'flag')+'</span>';
}
function newsHTML(id){var l=CP.news(id);if(!l.length)return '';
  return '<div class="cp-news"><span class="cp-lbl">New here</span><ul>'+l.map(function(x){return '<li class="k-'+x.k+'">'+nfIcon(x)+'<span>'+esc(x.t)+'</span></li>'}).join('')+'</ul></div>'}
/* said over the board while he plays: who is new, a beat of the story, a rule the first time it matters. One at a time; a tap sends it on. */
var tq=[],tshow=null,said=[],tbox=document.createElement('div');tbox.className='cp-toasts';tbox.setAttribute('aria-live','polite');root.appendChild(tbox);
function toast(o){said.push(o.t);if(FAST)return;tq.push(o)}
function toastOff(){tq=[];if(tshow){tshow.remove();tshow=null}}
/* a card picked up to read wants the line the note is sitting on */
root.addEventListener('pointerdown',function(e){if(tshow&&tshow._tell&&e.target.closest&&e.target.closest('.hcard'))tshow._gone()},true);
function pump(){
  if(tshow||!tq.length||scr!=='play')return;var bn=$('banner');if(bn&&!bn.hidden)return;
  /* where it sits: on the map over the mission's own box under the board; in a clash over the hint under the heading, or, where a
     short phone has put the hint away, over the line that says how to play. Never over the heading, the board or the foe's blow. */
  var o=tq.shift(),el=document.createElement('button'),rr=root.getBoundingClientRect(),map=$('scr-map'),top,onTell=false;
  if(map&&!map.hidden)top=$('m-rest').getBoundingClientRect().top-rr.top;
  else{var hd=root.querySelector('#scr-clash .scr-top'),tl=$('c-tell');
    var hinted=!!(X.G&&X.G.cs&&X.G.cs.hint)&&!(document.documentElement.classList.contains('app')&&window.innerHeight<=700);   /* the hint may not be drawn yet: go by whether it will be */
    if(hd&&hinted)top=hd.getBoundingClientRect().bottom-rr.top+6;
    else if(tl){top=tl.getBoundingClientRect().top-rr.top;onTell=true}else top=60}
  el.type='button';el.className='cp-toast k-'+(o.k||'say');
  el.innerHTML=(o.imgs||[]).filter(has).slice(0,4).map(function(n){return '<img src="'+A+n+'.webp" alt="">'}).join('')+'<span>'+(o.h?'<b>'+esc(o.h)+'</b> ':'')+esc(o.t)+'</span>';
  tbox.style.top=Math.max(8,top)+'px';tbox.appendChild(el);tshow=el;
  var gone=function(){if(tshow!==el)return;tshow=null;el.classList.add('out');setTimeout(function(){el.remove()},240)};el._gone=gone;el._tell=onTell;
  el.addEventListener('click',gone);setTimeout(gone,o.life||Math.min(6000,1700+o.t.length*42));
}
function drain(){var G=X.G;if(!G||!G.ms||scr!=='play'||!G.cs||!G.cs.toasts)return;
  while(G.cs.toasts.length){var o=G.cs.toasts.shift();toast({k:o.k,t:o.t,imgs:o.img?[o.img]:[]})}
  G.cs._t=G.cs._t||0;while(G.cs._t<G.cs.tips.length){var id=G.cs.tips[G.cs._t++];if(!P.tips[id]){P.tips[id]=1;save();toast({k:'tip',h:CP.TIPS[id][0]+'.',t:CP.TIPS[id][1],life:7000})}}
  pump()}
function list2(a){return a.length<2?a.join(''):a.slice(0,-1).join(', ')+' and '+a[a.length-1]}
function hello(id){if(P.done[id])return;var l=CP.news(id),j=l.filter(function(x){return x.k==='join'}),c=l.filter(function(x){return x.k==='card'});
  if(j.length)toast({k:'join',t:list2(j.map(function(x){return x.who}))+(j.length>1?' are':' is')+' with him.',imgs:j.map(function(x){return x.img})});
  if(c.length)toast({k:'card',t:'New in his hand: '+list2(c.map(function(x){return LH.C[x.id].n+(LH.C[x.id].r?' '+LH.C[x.id].r:'')}))+'.'})}

/* The cards: everything he has held so far, and what is still to find. Collecting is the thread through the missions. */
var cardsBack='title';
function album(){
  var C=LH.C,mine={},lent={},allMine={},allLent={};
  CP.ORDER.forEach(function(id,i){var p=CP.profile(id),n;for(n in p.cards){allMine[n]=1;if(open(i))mine[n]=p.cards[n]}for(n in p.lends){var c=C[p.lends[n]];if(!c)continue;allLent[c.n]=1;if(open(i))lent[c.n]=p.lends[n]}});
  return {mine:mine,lent:lent,nMine:Object.keys(allMine).length,nLent:Object.keys(allLent).length,shelf:shelf()}}
function found(){var a=album();return [Object.keys(a.mine).length+Object.keys(a.lent).length+a.shelf.length+Object.keys(P.tips).length,a.nMine+a.nLent+CP.SHOP.length+Object.keys(CP.TIPS).length]}
function cards(back){
  if(back)cardsBack=back;scr='cards';var a=album(),C=LH.C,f=found(),grace=[],own=[],n,sh=a.shelf;
  for(n in a.mine)(C[a.mine[n]].r==='the Grace'&&P.done.p0?grace:own).push(a.mine[n]);
  function grid(l,cls){return '<div class="hand3">'+l.map(function(id){return X.cardHTML(id,{cls:cls||''})}).join('')+'</div>'}
  function back1(t){return '<div class="card back"><span class="q">?</span><small>'+esc(t)+'</small></div>'}
  var locked=CP.SHOP.filter(function(id){return sh.indexOf(id)<0}).map(function(id){var m=null,k;for(k in CP.GIFT)if(CP.GIFT[k]===id)m=k;
    var st=CP.STARGIFT.filter(function(g){return g[1]===id})[0];return back1(st?'At '+st[0]+' stars':m&&open(CP.ORDER.indexOf(m))?'From: '+CP.MS[m].n:'From a mission not yet open')});
  var h='<div class="cp-top"><b>The cards</b>'+btn(cardsBack,'Back','','mini')+'</div>'+
    '<div class="stats"><div class="stat gold"><span class="si">'+X.svg('deck')+'</span><b class="num">'+f[0]+'<i>/'+f[1]+'</i></b><small>found so far</small></div>'+
      '<div class="stat"><span class="si">★</span><b class="num">'+starsAll()+'<i>/'+CP.ORDER.length*3+'</i></b><small>stars</small></div>'+
      '<div class="stat"><span class="si">'+X.svg('cart')+'</span><b class="num">'+sh.length+'<i>/'+CP.SHOP.length+'</i></b><small>at the fire</small></div></div>'+
    '<span class="lbl sec">'+X.svg('sword')+'His own · '+Object.keys(a.mine).length+' of '+a.nMine+'</span>'+grid(own)+
    (grace.length?'<span class="lbl sec">'+X.svg('x')+'Sealed since the ford</span>'+grid(grace,'sealed'):'')+
    '<span class="lbl sec">'+X.svg('heart')+'Lent by those beside him · '+Object.keys(a.lent).length+' of '+a.nLent+'</span>'+grid(Object.keys(a.lent).map(function(k){return a.lent[k]}))+
    (function(){var who=met().filter(function(o){return o.fights}),ids=[],k;who.forEach(function(o){for(k in WHO)if(WHO[k]===o.n)CP.grown(CP.KIT[k],gr(k).picks).forEach(function(c){if(ids.indexOf(c)<0&&!LH.C[c].basic)ids.push(c)})});
      return who.length?'<span class="lbl sec">'+X.svg('swords')+'The company\'s own · over the Strike and Guard everyone carries</span>'+grid(['b_strike','b_guard'].concat(ids)):''})()+
    '<span class="lbl sec">'+X.svg('cart')+'From the fire · '+sh.length+' of '+CP.SHOP.length+'</span><span class="cp-dim">Each mission told leaves one card the company can spare; stars open the last two.</span><div class="hand3">'+sh.map(function(id){return X.cardHTML(id,{cls:P.pack.indexOf(id)>=0?'owned':''})}).join('')+locked.join('')+'</div>'+
    '<span class="lbl sec">'+X.svg('eye')+'What he has learned · '+Object.keys(P.tips).length+' of '+Object.keys(CP.TIPS).length+'</span><dl class="cp-tips">'+Object.keys(CP.TIPS).filter(function(k){return P.tips[k]}).map(function(k){return '<dt>'+esc(CP.TIPS[k][0])+'</dt><dd>'+esc(CP.TIPS[k][1])+'</dd>'}).join('')+'</dl>'+(Object.keys(P.tips).length?'':'<span class="cp-dim">A rule is written here the first time it matters in a fight.</span>');
  show(h,'scroll fire album');
}

/* The fire: the game's own camp, kept small. What he takes here goes with him into the fights told larger than the page, and nowhere else. */
var fireBack='title',pick=null;
function fire(back){
  if(back)fireBack=back;scr='fire';var pu=purse(),open3=TALL.filter(function(id){return open(CP.ORDER.indexOf(id))}).length,sh=shelf(),shop=sh.filter(function(id){return P.pack.indexOf(id)<0}),
    faces=['darrow','hollis','ash','wren','rae'].filter(has),full=P.pack.length>=CP.PACK;
  if(pick&&shop.indexOf(pick)<0)pick=null;
  var h='<div class="cp-top"><b>The fire</b>'+btn(fireBack,'Back','','mini')+'</div>'+
    '<div class="camphero"><span class="glow"></span><span class="cfaces">'+faces.map(function(n){return '<img src="'+A+n+'.webp" alt="">'}).join('')+'</span></div>'+
    '<div class="stats"><div class="stat gold" id="cp-purse"><span class="si">★</span><b class="num">'+pu+'</b><small>stars to spend</small></div>'+
      '<div class="stat"><span class="si">'+X.svg('deck')+'</span><b class="num">'+P.pack.length+'<i>/'+CP.PACK+'</i></b><small>cards in the pack</small></div>'+
      '<div class="stat"><span class="si">'+X.svg('cart')+'</span><b class="num">'+sh.length+'<i>/'+CP.SHOP.length+'</i></b><small>cards found</small></div></div>'+
    '<p class="cp-note">Every star a mission gives is a star to spend here. The pack goes with him into the fights told larger than the page ('+TALL.map(function(id){return esc(CP.MS[id].n)}).join(', ')+'). The page\'s own scenes keep the page\'s deck.</p>'+
    '<span class="lbl sec">'+X.svg('deck')+'The pack · '+P.pack.length+' of '+CP.PACK+'</span>'+
    (P.pack.length?'<div class="hand3">'+P.pack.map(function(id){return starCard(id,'owned','drop')}).join('')+'</div><span class="cp-dim">Tap a card to put it back and have its stars again.</span>':'<span class="cp-dim">Nothing in it yet.</span>')+
    '<span class="lbl sec">'+X.svg('cart')+'What the company can spare</span>'+(sh.length?'':'<span class="cp-dim">Nothing yet. Each mission told leaves one card here.</span>')+'<div class="hand3">'+shop.map(function(id){return starCard(id,(pick===id?'pick':'')+(cost(id)>pu||full?' poor':''),'pick')}).join('')+'</div>'+(sh.length<CP.SHOP.length?'<span class="cp-dim">'+(CP.SHOP.length-sh.length)+' more to find. '+btnLink('cards:fire','See the cards')+'</span>':'');
  if(pick){var c=LH.C[pick],no=full?'The pack is full: put one back first':cost(pick)>pu?'You have '+pu+' stars':'';
    h+='<div class="panel cp-pick"><span><b>'+esc(c.n)+'</b> <span class="lbl">'+c.c+' breath · '+c.k+'</span></span><span>'+LH.cardText(pick)+'</span>'+
      '<button type="button" class="act primary" data-cp="take"'+(no?' disabled':'')+'><b>Take it for '+cost(pick)+' stars</b><small>'+(no||'Leaves '+(pu-cost(pick)))+'</small></button></div>'}
  var top=layer.scrollTop;show(h,'scroll fire');layer.scrollTop=top;
  var pk=layer.querySelector('.cp-pick');if(pk&&pk.scrollIntoView)pk.scrollIntoView({block:'nearest'});
}
function briefOf(id){var keep=CP.pending,G=CP.start(id,{seed:1});CP.pending=keep;return CP.objective(G)}
var DRAWN={};(AS.drawn||[]).forEach(function(d){DRAWN[d[1]]=1});
function begin(id){
  if(X.busy)return;var M=CP.MS[id];
  X.curtain('march',esc(M.n),esc(M.place),function(){
    CP.pending=id;CP.pack=P.pack.slice();CP.level=P.level||0;kick.click();
    var G=X.G;if(!G||G.ms!==id){CP.pending=null;return}
    root.setAttribute('data-th',M.map.theme||'');
    /* the triangle is drawn under the board only where more than one of them fights */
    if(G.u.filter(function(u){return u.side===0&&u.hp>0&&!u.still&&u.deck&&u.deck.length}).length>1)root.setAttribute('data-co','1');else root.removeAttribute('data-co');
    /* a foe the Chronicle has a face for stands in the clash with that face until a figure is made */
    G.u.forEach(function(u){if(u.side===1&&u.key&&!DRAWN[u.key]&&(AS.tok||[]).indexOf(u.key)>=0)u.img='tok-'+u.key});
    scr='play';shown=false;hide();toastOff();hello(id);sweep();
  });
}
function outro(){
  var G=X.G,S=G.cs,M=CP.MS[G.ms],id=G.ms,won=S.result==='won',n=S.stars.filter(function(s){return s[1]}).length,i=CP.ORDER.indexOf(id),nx=CP.ORDER[i+1];
  var was=P.done[id]?P.done[id].stars:0,gain=won?Math.max(0,n-was):0;
  var before=shelf(),got=bank(G),fnd=S.found||0,fmax=(S.finds||[]).length,fgain=0;forgetBoard();
  if(won&&fnd>(P.finds[id]||0)){fgain=fnd-(P.finds[id]||0);P.finds[id]=fnd}
  var rows=Object.keys(S.tally||{}).map(function(nm){var t=S.tally[nm];return '<li><b>'+esc(nm)+'</b><span>'+t.f+(t.f===1?' fight':' fights')+' · '+t.d+' dealt'+(t.k?' · '+t.k+' sent off':'')+'</span></li>'}).join('');
  var grew=Object.keys(got.marks).map(function(k){return WHO[k]+' +'+got.marks[k]+(due(k)?' (a rank to give)':'')}).join(' · ');
  var result='<div class="cp-result"><span class="cp-lbl">How it went · turn '+G.turn+'</span>'+(rows?'<ul>'+rows+'</ul>':'<span class="cp-dim">Nobody came to blows.</span>')+(grew?'<span class="cp-dim">Marks: '+esc(grew)+'</span>':'')+(fmax?'<span class="cp-dim">◆ Found on the ground: '+fnd+' of '+fmax+(fgain?' · '+fgain+' more for the fire':'')+'</span>':'')+
    got.bonds.map(function(nm){return '<span class="cp-words"><b>A bond with '+esc(nm)+'.</b> '+esc(CP.BONDS[nm][0])+' <i>'+esc(CP.BONDS[nm][1])+'</i></span>'}).join('')+'</div>';
  if(won){P.done[id]={stars:Math.max(was,n)};save()}
  var fresh=shelf().filter(function(c){return before.indexOf(c)<0});
  scr='outro';
  show('<div class="cp-card '+(won?'won':'lost')+'"><span class="cp-lbl">'+esc(M.n)+'</span><h2>'+esc(G.over.t)+'</h2><p class="cp-where"><span>'+esc(G.over.s||'')+'</span></p>'+
    (won?M.outro.map(function(p){return '<p>'+esc(p)+'</p>'}).join('')+
      '<ul class="cp-starlist">'+S.stars.map(function(s){return '<li class="'+(s[1]?'on':'')+'"><i>★</i>'+esc(s[0])+'</li>'}).join('')+'</ul>'+
      '<p class="cp-read">As the page has it: '+esc(M.read)+'.</p>'+result+
      '<p class="cp-gain">'+(gain?'★ '+gain+' more for the fire. ':'')+purse()+' stars to spend.</p>'+
      (fresh.length?'<div class="cp-reward"><span class="cp-lbl">The company can spare '+(fresh.length>1?'these':'this')+' now</span><div class="hand3">'+fresh.map(function(c){return X.cardHTML(c,{cls:'fresh'})}).join('')+'</div><span class="cp-dim">At the fire, for stars: it goes with him into the larger fights.</span></div>':'')
     :'<p>'+esc(M.objective&&typeof M.objective==='string'?M.objective:CP.objective(G))+'</p>'+result)+
    '<div class="cp-acts">'+(won?(nx?btn('intro:'+nx,'Onward',CP.MS[nx].n,'primary'):btn('end',CP.END.t,'','primary')):btn('go:'+id,'Again','From the start','primary'))+(won?btn('go:'+id,'Play it again',''):'')+(dueAll()?btn('company','The company',dueAll()+(dueAll()>1?' ranks':' rank')+' to give'):'')+(won?btn('fire:list','The fire',purse()+' stars to spend'):'')+btn('list','Missions','')+'</div></div>','scroll');
}
function end(){scr='end';show('<div class="cp-title"><span class="cp-lbl">Book II · The Tempering Road</span><h2>'+CP.END.t+'</h2><p class="cp-sub">'+CP.END.s+'</p><div class="cp-acts">'+btn('list','Missions','','primary')+'</div></div>')}
root.addEventListener('click',function(e){
  var fold=e.target.closest('.cp-obj,.cp-hint'),in0=e.target.closest('[data-cp]');if(fold&&(!in0||in0===root)){fold.classList.toggle('open');return} /* on a phone the rule is folded to a line (play.css): a tap opens it */
  var b=e.target.closest('[data-cp]');if(!b||b.disabled||b===root)return;var a=b.getAttribute('data-cp'),k=a.split(':');
  if(k[0]==='title')title();else if(k[0]==='list')list();else if(k[0]==='intro')intro(k[1]);else if(k[0]==='go')begin(k[1]);else if(k[0]==='end')end();
  else if(k[0]==='fire'){pick=null;fire(k.slice(1).join(':')||'title')}
  else if(k[0]==='cards'){cards(k.slice(1).join(':')||'title')}
  else if(k[0]==='pick'){pick=pick===k[1]?null:k[1];fire()}
  else if(k[0]==='take'){if(pick&&P.pack.length<CP.PACK&&cost(pick)<=purse()&&P.pack.indexOf(pick)<0&&shelf().indexOf(pick)>=0){P.pack.push(pick);pick=null;save()}fire()}
  else if(k[0]==='drop'){var di=P.pack.indexOf(k[1]);if(di>=0){P.pack.splice(di,1);save()}fire()}
  else if((k[0]==='quit'||k[0]==='quitroad')&&!b.classList.contains('sure')){arm(b)} /* leaving takes two taps: the first asks */
  else if(k[0]==='quit'){if(!X.busy){bank(X.G);forgetBoard();list()}}
  else if(k[0]==='resume')resume();
  else if(k[0]==='grow')grow(k[1],scr==='outro'?'list':'company');
  else if(k[0]==='rank'){if(due(k[1])>0&&CP.GROW[k[1]].indexOf(k[2])>=0&&CP.rankOf(gr(k[1]).picks,k[2])<3){gr(k[1]).picks.push(k[2]);save();syncGrow()}grow(k[1])}
  else if(k[0]==='company')company();else if(k[0]==='settings'){sure=false;settings()}
  else if(k[0]==='forget'){if(sure){sure=false;P.done={};P.pack=[];P.tips={};P.grow={};P.bond={};P.finds={};P.road=null;P.all=P.shelfAll=P.roadAll=false;P.bonus=0;forgetBoard();syncGrow();save();title()}else{sure=true;settings()}}
  else if(k[0]==='road')road();else if(k[0]==='quitroad')leaveRoad();
  else if(k[0]==='app'){if(window.__APP&&window.__APP.take(k[1])==='steps')appSheet();else title()}
  else if(k[0]==='pt'){if(k[1]==='all')P.all=k[2]==='1';else if(k[1]==='shelf'){P.shelfAll=k[2]==='1';trimPack()}else if(k[1]==='deck')P.roadAll=k[2]==='1';else if(k[1]==='stars')P.bonus=(P.bonus||0)+10;
    else if(k[1]==='marks')Object.keys(WHO).forEach(function(id){var g=gr(id),nx=CP.LEVELS[CP.levelOf(g.m)];if(nx)g.m=nx});save();syncGrow();settings()}
});
var FAST=!!window.LH_FAST;
/* the mission is over: the telling comes up. Where the game draws its curtain across the screen, the telling is laid under it
   once the curtain has closed, so the board is never seen bare between the two; with no curtain (animations off), it follows the board. */
setInterval(function(){var G=X.G;if(scr==='play'&&G&&G.ms&&G.over&&!X.busy&&!shown){shown=true;setTimeout(outro,FAST?0:650)}drain()},200);
function underCurtain(){var G=X.G,bn=$('banner');if(scr==='play'&&G&&G.ms&&G.over&&!shown&&bn&&!bn.hidden&&/\bcur\b/.test(bn.className)){shown=true;setTimeout(outro,X.prefs.quick?170:350)}}

/* ---------- on the game's own screen: the objective, the marked tiles, and the words that fit this board ---------- */
function objHTML(G){var h=G.cs.hint;return '<span class="cp-o"><b>'+esc(CP.objective(G))+'</b></span>'+(h?'<span class="cp-h">'+esc(h)+'</span>':'')}
var pend=false;
function sweep(){
  pend=false;var G=X.G;
  if(G&&scr==='road'){var host=G.over&&G.over.win?$('scr-camp'):$('m-rest');
    if(host&&!host.querySelector('.cp-quit')){var qb=document.createElement('button');qb.type='button';qb.className='linkbtn cp-quit';qb.setAttribute('data-cp','quitroad');qb.textContent='Back to the menu';host.appendChild(qb)}
    if(G.over&&!G.over.win&&!roadSaved){roadSaved=true;bank(G);forgetBoard();var R=P.road||{best:0,runs:0,won:0};R.runs++;if(G.over.done)R.won++;R.best=Math.max(R.best||0,G.run.renown||0);P.road=R;save()}
    if(G.over&&G.over.win)bank(G);if(!G.over)roadSaved=false;keepSoon();return}
  if(!G||!G.ms||scr!=='play')return;underCurtain();
  drain();keepSoon();
  if(G.cs.scrolled){var kk=G.cs.scrolled;G.cs.scrolled=0;if(!FAST)['m-board','m-units'].forEach(function(i2){var e2=$(i2);if(e2&&e2.animate)e2.animate([{transform:'translateY('+(kk/7*100)+'%)'},{transform:'translateY(0)'}],{duration:X.prefs.quick?220:480,easing:'cubic-bezier(.2,.7,.3,1)'})});toast({k:'say',t:'The view follows them down.'})}
  var top=$('m-top'),t=CP.top(G);if(top&&top.textContent!==t)top.textContent=t;
  var rest=$('m-rest'),map=$('scr-map');
  if(rest&&map&&!map.hidden){var o=rest.querySelector('.cp-obj'),h=objHTML(G);if(!o){o=document.createElement('div');o.className='cp-obj';rest.insertBefore(o,rest.firstChild)}if(o._h!==h){o.innerHTML=h;o._h=h}
    if(!rest.querySelector('.cp-quit')&&!G.over){var q=document.createElement('button');q.type='button';q.className='linkbtn cp-quit';q.setAttribute('data-cp','quit');q.textContent='Leave the mission';rest.appendChild(q)}}
  var clash=$('scr-clash');
  if(clash&&!clash.hidden&&clash.children.length){var hh=clash.querySelector('.cp-hint'),tx=G.cs.hint||'';if(!hh){hh=document.createElement('div');hh.className='cp-hint';clash.insertBefore(hh,clash.children[1]||null)}if(hh.textContent!==tx)hh.textContent=tx;if(hh.hidden!==!tx)hh.hidden=!tx;
    var fg=clash.querySelector('#c-foe .fig');if(fg&&G.clash&&G.clash.d.ordeal&&!fg.classList.contains('ordeal'))fg.classList.add('ordeal')}
  var board=$('m-board'),marks={};CP.goals(G).forEach(function(m){marks[m[0]+','+m[1]]=m[2]});
  if(board)for(var i=0;i<board.children.length;i++){var tl=board.children[i],k=tl.getAttribute('data-x')+','+tl.getAttribute('data-y'),want=marks[k]||'';if((tl.getAttribute('data-mark')||'')!==want){if(want)tl.setAttribute('data-mark',want);else tl.removeAttribute('data-mark')}}
  /* the engine's sentences that reach the screen without passing through LH (the screen's own words) */
  var w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT,null),n,list=[];
  while((n=w.nextNode()))list.push(n);
  list.forEach(function(n){var p=n.parentNode;if(!p||!n.nodeValue||n.nodeValue.length<2)return;if(p.closest('.log,.cp,.cp-obj,.cp-hint,.float,.cp-quit'))return;
    var s=CP.say(G,n.nodeValue);
    if(/^ · the carter · /.test(s)&&n.previousSibling&&n.previousSibling.tagName==='B'){var who=G.u.filter(function(u){return u.n===n.previousSibling.textContent})[0];if(who&&who.role)s=s.replace(' · the carter · ',' · '+who.role+' · ')}
    if(s!==n.nodeValue)n.nodeValue=s});
}
function later(){if(!pend){pend=true;Promise.resolve().then(sweep)}}
new MutationObserver(later).observe(root,{childList:true,subtree:true,characterData:true});
function paintLevel(){var b=document.querySelectorAll('[data-cplevel]');for(var i=0;i<b.length;i++)b[i].setAttribute('aria-pressed',String(+b[i].getAttribute('data-cplevel')===(P.level||0)))}
document.addEventListener('click',function(e){var b=e.target.closest('[data-cplevel]');if(!b)return;P.level=+b.getAttribute('data-cplevel');save();paintLevel()});
paintLevel();
trimPack();syncGrow();
document.addEventListener('lh-app',function(){if(scr==='title')title()});
window.__CP={get scr(){return scr},P:P,title:title,list:list,intro:intro,begin:begin,fire:fire,cards:cards,company:company,settings:settings,grow:grow,bank:bank,due:due,resume:resume,suspended:suspended,keepBoard:keepBoard,forgetBoard:forgetBoard,road:road,leaveRoad:leaveRoad,roadDeck:roadDeck,purse:purse,cost:cost,shelf:shelf,found:found,said:said,sweep:sweep,reset:function(){P.done={};P.pack=[];P.tips={};P.grow={};P.bond={};P.finds={};P.road=null;P.all=P.shelfAll=P.roadAll=false;P.bonus=0;forgetBoard();syncGrow();save();title()}};
title();
})();
