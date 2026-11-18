/* The Line and the Hand: the campaign's screens. It sits on top of the game's own screen (ui.js), which it does not change:
   it starts a mission through the same door the page's "new run" buttons use, lays its own title, mission list and place cards
   over the board, and writes the objective into the map screen each time that screen is redrawn. */
(function(){
'use strict';
var LH=window.LH,CP=window.CP,X=window.__LH,root=document.getElementById('game');if(!root||!CP||!X)return;
var A='art/',AS=window.LH_ASSETS||{art:[]};
function has(n){return AS.art.indexOf(n)>=0}
function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/"/g,'&quot;')}
function $(id){return document.getElementById(id)}
var P={};try{P=JSON.parse(localStorage.getItem('lh-campaign')||'{}')||{}}catch(e){}P.done=P.done||{};P.pack=(P.pack||[]).filter(function(id){return CP.SHOP.indexOf(id)>=0});P.level=P.level||0;P.tips=P.tips||{};
function save(){try{localStorage.setItem('lh-campaign',JSON.stringify(P))}catch(e){}}
var layer=document.createElement('div');layer.className='cp';root.appendChild(layer);root.setAttribute('data-cp','1');
var kick=document.createElement('button');kick.type='button';kick.hidden=true;kick.setAttribute('data-newrun','');document.body.appendChild(kick);
var scr='title',shown=false,ALL=!!window.LH_ALL||/[?&]all\b/.test(location.search);
function open(i){return ALL||i===0||!!P.done[CP.ORDER[i-1]]}
function nextId(){for(var i=0;i<CP.ORDER.length;i++)if(!P.done[CP.ORDER[i]])return CP.ORDER[i];return null}
function starRow(n,of){var h='<span class="cp-stars" aria-label="'+n+' of '+of+'">';for(var i=0;i<of;i++)h+='<i class="'+(i<n?'on':'')+'">★</i>';return h+'</span>'}
function show(html,cls){layer.className='cp on '+(cls||'');layer.innerHTML=html;layer.scrollTop=0;if(typeof toastOff==='function'&&tbox)toastOff()}
function hide(){layer.className='cp';layer.innerHTML=''}
/* ---------- stars are what he has to spend at the fire: a camp card costs twice its price in spoils ---------- */
var TALL=CP.ORDER.filter(function(id){return !!CP.MS[id].tall});
function starsAll(){var n=0;for(var k in P.done)n+=P.done[k].stars||0;return n}
function cost(id){return LH.C[id].p*2}
function shelf(){return CP.shelf(P.done)}
function trimPack(){var sh=shelf();P.pack=P.pack.filter(function(id){return sh.indexOf(id)>=0})}
function purse(){return starsAll()-P.pack.reduce(function(n,id){return n+cost(id)},0)}
function names(l){return l.map(function(id){return LH.C[id].n}).join(', ')}
function starCard(id,cls,act){return X.cardHTML(id,{tag:'button',price:1,cls:cls,attrs:' data-cp="'+act+':'+id+'"'}).replace(/<span class="price num">.*?<\/span>/,'<span class="price num star">★ '+cost(id)+'</span>')}
function btnLink(a,label){return '<button type="button" class="linkbtn" data-cp="'+a+'">'+label+'</button>'}
function btn(a,label,small,cls){return '<button type="button" class="act '+(cls||'')+'" data-cp="'+a+'"><b>'+label+'</b>'+(small?'<small>'+small+'</small>':'')+'</button>'}

/* ---------- title, missions, the place card, the telling after ---------- */
function title(){
  scr='title';var nx=nextId(),n=Object.keys(P.done).length,M=nx?CP.MS[nx]:null;
  show('<div class="cp-title"><span class="cp-lbl">The Unkneeling</span><h2>The Line and the Hand</h2><p class="cp-sub">The campaign: the Chronicle, played from where he was put.</p>'+
    '<div class="cp-crest"><img src="'+A+'high-guard.webp" alt=""></div>'+
    '<div class="cp-acts">'+(M?btn('intro:'+nx,n?'Go on':'Begin',M.book+' · '+M.n,'primary'):btn('list','Every mission is told',CP.END.t,'primary'))+btn('list','Missions',n+' of '+CP.ORDER.length+' told')+btn('fire:title','The fire',purse()+' stars to spend')+btn('cards:title','The cards',found()[0]+' of '+found()[1]+' found')+'</div>'+
    '<p class="cp-note">Nothing here changes the story. A mission that goes wrong is only played again: the page has already happened.</p></div>');
}
function list(){
  scr='list';var h='<div class="cp-top"><b>Missions</b><span class="cp-topacts">'+btn('fire:list','The fire ★ '+purse(),'','mini')+btn('title','Back','','mini')+'</span></div>',book='';
  CP.ORDER.forEach(function(id,i){var M=CP.MS[id],d=P.done[id];
    if(M.book!==book){book=M.book;h+='<span class="cp-book">'+esc(book)+'</span>'}
    h+='<button type="button" class="cp-row'+(open(i)?'':' locked')+(d?' done':'')+(M.tall?' tall':'')+'" data-cp="intro:'+id+'"'+(open(i)?'':' disabled')+'><span class="cp-n">'+(i+1)+'</span><span class="cp-rt"><b>'+esc(M.n)+'</b><small>'+esc(open(i)?M.place:'Not yet')+'</small></span>'+(d?starRow(d.stars,3):'')+'</button>'});
  h+='<div class="cp-end"><b>'+CP.END.t+'</b><span>'+CP.END.s+'</span></div>';
  show(h,'scroll');
}
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
function pump(){
  if(tshow||!tq.length||scr!=='play')return;var bn=$('banner');if(bn&&!bn.hidden)return;
  var o=tq.shift(),el=document.createElement('button'),hb=root.querySelector('#scr-clash .cp-hint'),an=($('scr-map')&&!$('scr-map').hidden?root.querySelector('.cp-obj'):(hb&&!hb.hidden?hb:$('c-tell')))||root,r=an.getBoundingClientRect(),rr=root.getBoundingClientRect();
  el.type='button';el.className='cp-toast k-'+(o.k||'say');
  el.innerHTML=(o.imgs||[]).filter(has).slice(0,4).map(function(n){return '<img src="'+A+n+'.webp" alt="">'}).join('')+'<span>'+(o.h?'<b>'+esc(o.h)+'</b> ':'')+esc(o.t)+'</span>';
  tbox.style.top=Math.max(8,r.top-rr.top)+'px';tbox.appendChild(el);tshow=el;
  var gone=function(){if(tshow!==el)return;tshow=null;el.classList.add('out');setTimeout(function(){el.remove()},240)};
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
  var before=shelf();
  if(won){P.done[id]={stars:Math.max(was,n)};save()}
  var fresh=shelf().filter(function(c){return before.indexOf(c)<0});
  scr='outro';
  show('<div class="cp-card '+(won?'won':'lost')+'"><span class="cp-lbl">'+esc(M.n)+'</span><h2>'+esc(G.over.t)+'</h2><p class="cp-where"><span>'+esc(G.over.s||'')+'</span></p>'+
    (won?M.outro.map(function(p){return '<p>'+esc(p)+'</p>'}).join('')+
      '<ul class="cp-starlist">'+S.stars.map(function(s){return '<li class="'+(s[1]?'on':'')+'"><i>★</i>'+esc(s[0])+'</li>'}).join('')+'</ul>'+
      '<p class="cp-read">As the page has it: '+esc(M.read)+'.</p>'+
      '<p class="cp-gain">'+(gain?'★ '+gain+' more for the fire. ':'')+purse()+' stars to spend.</p>'+
      (fresh.length?'<div class="cp-reward"><span class="cp-lbl">The company can spare '+(fresh.length>1?'these':'this')+' now</span><div class="hand3">'+fresh.map(function(c){return X.cardHTML(c,{cls:'fresh'})}).join('')+'</div><span class="cp-dim">At the fire, for stars: it goes with him into the larger fights.</span></div>':'')
     :'<p>'+esc(M.objective&&typeof M.objective==='string'?M.objective:CP.objective(G))+'</p>')+
    '<div class="cp-acts">'+(won?(nx?btn('intro:'+nx,'Onward',CP.MS[nx].n,'primary'):btn('end',CP.END.t,'','primary')):btn('go:'+id,'Again','From the start','primary'))+(won?btn('go:'+id,'Play it again',''):'')+(won?btn('fire:list','The fire',purse()+' stars to spend'):'')+btn('list','Missions','')+'</div></div>','scroll');
}
function end(){scr='end';show('<div class="cp-title"><span class="cp-lbl">Book II · The Tempering Road</span><h2>'+CP.END.t+'</h2><p class="cp-sub">'+CP.END.s+'</p><div class="cp-acts">'+btn('list','Missions','','primary')+'</div></div>')}
root.addEventListener('click',function(e){
  var b=e.target.closest('[data-cp]');if(!b||b.disabled||b===root)return;var a=b.getAttribute('data-cp'),k=a.split(':');
  if(k[0]==='title')title();else if(k[0]==='list')list();else if(k[0]==='intro')intro(k[1]);else if(k[0]==='go')begin(k[1]);else if(k[0]==='end')end();
  else if(k[0]==='fire'){pick=null;fire(k.slice(1).join(':')||'title')}
  else if(k[0]==='cards'){cards(k.slice(1).join(':')||'title')}
  else if(k[0]==='pick'){pick=pick===k[1]?null:k[1];fire()}
  else if(k[0]==='take'){if(pick&&P.pack.length<CP.PACK&&cost(pick)<=purse()&&P.pack.indexOf(pick)<0&&shelf().indexOf(pick)>=0){P.pack.push(pick);pick=null;save()}fire()}
  else if(k[0]==='drop'){var di=P.pack.indexOf(k[1]);if(di>=0){P.pack.splice(di,1);save()}fire()}
  else if(k[0]==='quit'){if(!X.busy)list()}
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
  pend=false;var G=X.G;if(!G||!G.ms||scr!=='play')return;underCurtain();
  drain();
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
trimPack();
window.__CP={get scr(){return scr},P:P,title:title,list:list,intro:intro,begin:begin,fire:fire,cards:cards,purse:purse,cost:cost,shelf:shelf,found:found,said:said,sweep:sweep,reset:function(){P.done={};P.pack=[];P.tips={};save();title()}};
title();
})();
