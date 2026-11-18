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
var P={};try{P=JSON.parse(localStorage.getItem('lh-campaign')||'{}')||{}}catch(e){}P.done=P.done||{};P.pack=(P.pack||[]).filter(function(id){return CP.SHOP.indexOf(id)>=0});P.level=P.level||0;
function save(){try{localStorage.setItem('lh-campaign',JSON.stringify(P))}catch(e){}}
var layer=document.createElement('div');layer.className='cp';root.appendChild(layer);root.setAttribute('data-cp','1');
var kick=document.createElement('button');kick.type='button';kick.hidden=true;kick.setAttribute('data-newrun','');document.body.appendChild(kick);
var scr='title',shown=false,ALL=!!window.LH_ALL||/[?&]all\b/.test(location.search);
function open(i){return ALL||i===0||!!P.done[CP.ORDER[i-1]]}
function nextId(){for(var i=0;i<CP.ORDER.length;i++)if(!P.done[CP.ORDER[i]])return CP.ORDER[i];return null}
function starRow(n,of){var h='<span class="cp-stars" aria-label="'+n+' of '+of+'">';for(var i=0;i<of;i++)h+='<i class="'+(i<n?'on':'')+'">★</i>';return h+'</span>'}
function show(html,cls){layer.className='cp on '+(cls||'');layer.innerHTML=html;layer.scrollTop=0}
function hide(){layer.className='cp';layer.innerHTML=''}
/* ---------- stars are what he has to spend at the fire: a camp card costs twice its price in spoils ---------- */
var TALL=CP.ORDER.filter(function(id){return !!CP.MS[id].tall});
function starsAll(){var n=0;for(var k in P.done)n+=P.done[k].stars||0;return n}
function cost(id){return LH.C[id].p*2}
function purse(){return starsAll()-P.pack.reduce(function(n,id){return n+cost(id)},0)}
function names(l){return l.map(function(id){return LH.C[id].n}).join(', ')}
function starCard(id,cls,act){return X.cardHTML(id,{tag:'button',price:1,cls:cls,attrs:' data-cp="'+act+':'+id+'"'}).replace(/<span class="price num">.*?<\/span>/,'<span class="price num star">★ '+cost(id)+'</span>')}
function btn(a,label,small,cls){return '<button type="button" class="act '+(cls||'')+'" data-cp="'+a+'"><b>'+label+'</b>'+(small?'<small>'+small+'</small>':'')+'</button>'}

/* ---------- title, missions, the place card, the telling after ---------- */
function title(){
  scr='title';var nx=nextId(),n=Object.keys(P.done).length,M=nx?CP.MS[nx]:null;
  show('<div class="cp-title"><span class="cp-lbl">The Unkneeling</span><h2>The Line and the Hand</h2><p class="cp-sub">The campaign: the Chronicle, played from where he was put.</p>'+
    '<div class="cp-crest"><img src="'+A+'high-guard.webp" alt=""></div>'+
    '<div class="cp-acts">'+(M?btn('intro:'+nx,n?'Go on':'Begin',M.book+' · '+M.n,'primary'):btn('list','Every mission is told',CP.END.t,'primary'))+btn('list','Missions',n+' of '+CP.ORDER.length+' told')+btn('fire:title','The fire',purse()+' stars to spend')+'</div>'+
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
    (M.tall?'<div class="cp-brief"><span class="cp-lbl">The pack · from the fire</span><span>'+(P.pack.length?esc(names(P.pack)):'Nothing in it yet.')+' <span class="cp-dim">'+purse()+' stars to spend.</span></span></div>':'')+
    '<div class="cp-acts">'+btn('go:'+id,'Begin','','primary')+(M.tall?btn('fire:intro:'+id,'The fire','Change what he carries'):'')+btn('list','Missions','')+'</div></div>','scroll');
}
/* The fire: the game's own camp, kept small. What he takes here goes with him into the fights told larger than the page, and nowhere else. */
var fireBack='title',pick=null;
function fire(back){
  if(back)fireBack=back;scr='fire';var pu=purse(),open3=TALL.filter(function(id){return open(CP.ORDER.indexOf(id))}).length,shop=CP.SHOP.filter(function(id){return P.pack.indexOf(id)<0}),
    faces=['darrow','hollis','ash','wren','rae'].filter(has),full=P.pack.length>=CP.PACK;
  if(pick&&shop.indexOf(pick)<0)pick=null;
  var h='<div class="cp-top"><b>The fire</b>'+btn(fireBack,'Back','','mini')+'</div>'+
    '<div class="camphero"><span class="glow"></span><span class="cfaces">'+faces.map(function(n){return '<img src="'+A+n+'.webp" alt="">'}).join('')+'</span></div>'+
    '<div class="stats"><div class="stat gold" id="cp-purse"><span class="si">★</span><b class="num">'+pu+'</b><small>stars to spend</small></div>'+
      '<div class="stat"><span class="si">'+X.svg('deck')+'</span><b class="num">'+P.pack.length+'<i>/'+CP.PACK+'</i></b><small>cards in the pack</small></div>'+
      '<div class="stat"><span class="si">'+X.svg('swords')+'</span><b class="num">'+open3+'<i>/'+TALL.length+'</i></b><small>larger fights open</small></div></div>'+
    '<p class="cp-note">Every star a mission gives is a star to spend here. The pack goes with him into the fights told larger than the page ('+TALL.map(function(id){return esc(CP.MS[id].n)}).join(', ')+'). The page\'s own scenes keep the page\'s deck.</p>'+
    '<span class="lbl sec">'+X.svg('deck')+'The pack · '+P.pack.length+' of '+CP.PACK+'</span>'+
    (P.pack.length?'<div class="hand3">'+P.pack.map(function(id){return starCard(id,'owned','drop')}).join('')+'</div><span class="cp-dim">Tap a card to put it back and have its stars again.</span>':'<span class="cp-dim">Nothing in it yet.</span>')+
    '<span class="lbl sec">'+X.svg('cart')+'What the company can spare</span><div class="hand3">'+shop.map(function(id){return starCard(id,(pick===id?'pick':'')+(cost(id)>pu||full?' poor':''),'pick')}).join('')+'</div>';
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
    scr='play';shown=false;hide();sweep();
  });
}
function outro(){
  var G=X.G,S=G.cs,M=CP.MS[G.ms],id=G.ms,won=S.result==='won',n=S.stars.filter(function(s){return s[1]}).length,i=CP.ORDER.indexOf(id),nx=CP.ORDER[i+1];
  var was=P.done[id]?P.done[id].stars:0,gain=won?Math.max(0,n-was):0;
  if(won){P.done[id]={stars:Math.max(was,n)};save()}
  scr='outro';
  show('<div class="cp-card '+(won?'won':'lost')+'"><span class="cp-lbl">'+esc(M.n)+'</span><h2>'+esc(G.over.t)+'</h2><p class="cp-where"><span>'+esc(G.over.s||'')+'</span></p>'+
    (won?M.outro.map(function(p){return '<p>'+esc(p)+'</p>'}).join('')+
      '<ul class="cp-starlist">'+S.stars.map(function(s){return '<li class="'+(s[1]?'on':'')+'"><i>★</i>'+esc(s[0])+'</li>'}).join('')+'</ul>'+
      '<p class="cp-read">As the page has it: '+esc(M.read)+'.</p>'+
      '<p class="cp-gain">'+(gain?'★ '+gain+' more for the fire. ':'')+purse()+' stars to spend.</p>'
     :'<p>'+esc(M.objective&&typeof M.objective==='string'?M.objective:CP.objective(G))+'</p>')+
    '<div class="cp-acts">'+(won?(nx?btn('intro:'+nx,'Onward',CP.MS[nx].n,'primary'):btn('end',CP.END.t,'','primary')):btn('go:'+id,'Again','From the start','primary'))+(won?btn('go:'+id,'Play it again',''):'')+(won?btn('fire:list','The fire',purse()+' stars to spend'):'')+btn('list','Missions','')+'</div></div>','scroll');
}
function end(){scr='end';show('<div class="cp-title"><span class="cp-lbl">Book II · The Tempering Road</span><h2>'+CP.END.t+'</h2><p class="cp-sub">'+CP.END.s+'</p><div class="cp-acts">'+btn('list','Missions','','primary')+'</div></div>')}
root.addEventListener('click',function(e){
  var b=e.target.closest('[data-cp]');if(!b||b.disabled||b===root)return;var a=b.getAttribute('data-cp'),k=a.split(':');
  if(k[0]==='title')title();else if(k[0]==='list')list();else if(k[0]==='intro')intro(k[1]);else if(k[0]==='go')begin(k[1]);else if(k[0]==='end')end();
  else if(k[0]==='fire'){pick=null;fire(k.slice(1).join(':')||'title')}
  else if(k[0]==='pick'){pick=pick===k[1]?null:k[1];fire()}
  else if(k[0]==='take'){if(pick&&P.pack.length<CP.PACK&&cost(pick)<=purse()&&P.pack.indexOf(pick)<0){P.pack.push(pick);pick=null;save()}fire()}
  else if(k[0]==='drop'){var di=P.pack.indexOf(k[1]);if(di>=0){P.pack.splice(di,1);save()}fire()}
  else if(k[0]==='quit'){if(!X.busy)list()}
});
var FAST=!!window.LH_FAST;
/* the mission is over: the telling comes up. Where the game draws its curtain across the screen, the telling is laid under it
   once the curtain has closed, so the board is never seen bare between the two; with no curtain (animations off), it follows the board. */
setInterval(function(){var G=X.G;if(scr==='play'&&G&&G.ms&&G.over&&!X.busy&&!shown){shown=true;setTimeout(outro,FAST?0:650)}},200);
function underCurtain(){var G=X.G,bn=$('banner');if(scr==='play'&&G&&G.ms&&G.over&&!shown&&bn&&!bn.hidden&&/\bcur\b/.test(bn.className)){shown=true;setTimeout(outro,X.prefs.quick?170:350)}}

/* ---------- on the game's own screen: the objective, the marked tiles, and the words that fit this board ---------- */
function objHTML(G){var h=G.cs.hint;return '<span class="cp-o"><b>'+esc(CP.objective(G))+'</b></span>'+(h?'<span class="cp-h">'+esc(h)+'</span>':'')}
var pend=false;
function sweep(){
  pend=false;var G=X.G;if(!G||!G.ms||scr!=='play')return;underCurtain();
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
window.__CP={get scr(){return scr},P:P,title:title,list:list,intro:intro,begin:begin,fire:fire,purse:purse,cost:cost,sweep:sweep,reset:function(){P.done={};P.pack=[];save();title()}};
title();
})();
