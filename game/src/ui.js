/* The Line and the Hand: what you see and hear. The rules live in LH (engine.js); this file only shows them and paces them. */
(function(){
'use strict';
var LH=window.LH,C=LH.C,TREE=LH.TREE,T=LH.T,A='art/';
/* what the build found: site pictures, figures and tokens made for the game, and real sound files */
var AS=window.LH_ASSETS||{art:[],fig:[],tok:[],sfx:{}};
function has(list,name){return !!name&&list.indexOf(name)>=0}
var root=document.getElementById('game');if(!root)return;
var FAST=!!window.LH_FAST,REDUCED=!!(window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches);
var prefs={rounds:1,quick:false,sound:false,music:true,deck:'sheet',level:0};
try{var sv=JSON.parse(localStorage.getItem('lh-prefs')||'{}');if(sv.rounds===3)prefs.rounds=3;if(sv.quick)prefs.quick=true;if(sv.sound)prefs.sound=true;if(sv.deck==='all')prefs.deck='all';if(sv.level===1||sv.level===-1)prefs.level=sv.level}catch(e){}
function savePrefs(){try{localStorage.setItem('lh-prefs',JSON.stringify(prefs))}catch(e){}}
function best(v){var b=0;try{b=+localStorage.getItem('lh-best')||0;if(v>b){localStorage.setItem('lh-best',String(v));}}catch(e){}return Math.max(b,v||0)}
var runId=0,G,UI={sel:null,fc:null,look:null,danger:false,card:-1,fx:null,buy:null,leave:false,ended:false},busy=false;
function lock(v){busy=v;root.setAttribute('data-busy',v?'1':'0')}
function ms(n){return FAST?0:Math.round(n*(prefs.quick?.45:1))}
function wait(n){n=ms(n);return n?new Promise(function(r){setTimeout(r,n)}):Promise.resolve()}
function anim(el,frames,dur,opts){dur=ms(dur);if(!dur||REDUCED||!el||!el.animate)return Promise.resolve();
  try{var o={duration:dur,easing:'cubic-bezier(.2,.7,.3,1)'};if(opts)for(var k in opts)o[k]=opts[k];return el.animate(frames,o).finished.catch(function(){})}catch(e){return Promise.resolve()}}
function still(el){if(el&&el.getAnimations)el.getAnimations().forEach(function(a){try{a.cancel()}catch(e){}})}
function esc(s){return String(s).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;')}
function $(id){return document.getElementById(id)}

/* ---------- sound: every moment that should make a noise, with a placeholder tone until the real file exists ---------- */
/* name, when it plays, what to record, seconds, placeholder tone(s): [wave, from Hz, to Hz, seconds, delay] */
var SFX=[
  ['ui_tap','Any button','A soft wooden tick',.05,[['triangle',660,660,.04]]],
  ['unit_select','Tapping one of the company','A leather creak, or a short rustle of cloth',.15,[['triangle',440,520,.09]]],
  ['unit_move','A move on the map','Two quick footfalls on earth',.3,[['noise',300,200,.07],['noise',260,180,.07,.12]]],
  ['forecast_open','The forecast opens','Parchment sliding on a table',.2,[['noise',1800,900,.14]]],
  ['clash_start','The banner before a clash','A low drum hit with a ring of steel over it',.7,[['sine',110,60,.35],['triangle',1400,1300,.4,.05]]],
  ['card_deal','Each card dealt into the hand','One card flicked off a deck',.1,[['noise',2600,1600,.05]]],
  ['card_lift','A card lifted to read','Soft paper lifting',.08,[['sine',880,990,.05]]],
  ['card_cant','A card that cannot be played','A dull knock on wood',.15,[['square',140,110,.1]]],
  ['card_attack','An attack card thrown','A fast whoosh',.25,[['noise',900,2800,.18]]],
  ['card_skill','A skill or stance card played','A softer swish',.2,[['noise',700,1500,.14]]],
  ['hit_light','A hit for 1 to 7','A blade on padded cloth',.2,[['noise',500,250,.1],['square',180,120,.08]]],
  ['hit_heavy','A hit for 8 or more, or into an Open foe','A heavy thud and a grunt',.35,[['noise',320,120,.2],['sine',120,60,.25]]],
  ['hit_blocked','A hit that is fully blocked','Steel on a wooden shield',.3,[['triangle',1250,1150,.16],['noise',1500,900,.08]]],
  ['block_gain','Block or guard gained','A shield brought up: strap and thunk',.25,[['sine',240,300,.12]]],
  ['heal','Health restored, or a Wound set aside','Cloth tearing, then a breath out',.5,[['sine',520,780,.3]]],
  ['breath_gain','Breath gained','One sharp breath in',.3,[['noise',600,2400,.22]]],
  ['status_good','Open, Pinned or Marked lands on him','A short rising pluck',.25,[['triangle',520,780,.12]]],
  ['break','He is Broken','Wood splitting',.3,[['noise',2200,400,.22]]],
  ['stance','A stance is taken','Feet set on earth and one low drum',.5,[['sine',150,150,.3],['noise',300,200,.1]]],
  ['wound','A Wound is taken','A wet thud and a hiss',.35,[['noise',260,140,.14],['noise',3200,2600,.2,.1]]],
  ['spoils','Spoils gained','Coins dropped in a purse',.3,[['triangle',1800,2100,.06],['triangle',2200,2500,.06,.07]]],
  ['end_hand','The hand is ended','Cards swept aside',.25,[['noise',1400,600,.18]]],
  ['foe_windup','He begins his answer','A step and a breath in',.25,[['sine',200,260,.16]]],
  ['hurt','One of yours takes damage','An impact and a grunt',.3,[['noise',380,150,.16],['sawtooth',160,90,.2]]],
  ['guard_hold','Guard holds a blow on their turn','A clean clang',.3,[['triangle',1500,1450,.22]]],
  ['riposte','The answering blow after a held guard','A quick slash',.2,[['noise',1200,3200,.12]]],
  ['foe_down','A foe is felled','A body falling and gear clattering',.6,[['noise',300,90,.3],['square',200,70,.3,.05]]],
  ['friend_down','A companion falls back','A stumble and a gasp',.6,[['sawtooth',300,120,.4]]],
  ['enrage','The captain enrages','A short roar',.7,[['sawtooth',110,220,.4],['noise',400,800,.3]]],
  ['enemy_turn','Their turn begins','Two low drum beats',.6,[['sine',90,70,.2],['sine',90,70,.2,.25]]],
  ['your_turn','Your turn begins','One bright horn note, or a small bell',.5,[['triangle',660,660,.3]]],
  ['press_on','Pressing on to another round','A short drum roll',.4,[['sine',130,130,.07],['sine',130,130,.07,.09],['sine',150,150,.12,.18]]],
  ['battle_won','A captain goes down','A short horn flourish',1.5,[['triangle',440,440,.18],['triangle',554,554,.18,.18],['triangle',659,659,.4,.36]]],
  ['camp_buy','A card bought at camp','Coins on a table and a card sliding over',.4,[['triangle',1900,2200,.06],['noise',2000,1200,.1,.1]]],
  ['camp_leave','A card left behind','A card dropped in a box',.3,[['square',220,160,.12]]],
  ['camp_hone','A card honed','A whetstone drawn along steel',.6,[['noise',2800,3600,.4]]],
  ['run_won','The run is won','A longer fanfare',3,[['triangle',440,440,.2],['triangle',554,554,.2,.2],['triangle',659,659,.2,.4],['triangle',880,880,.7,.6]]],
  ['run_lost','The run is lost','A low horn, falling',2.5,[['sawtooth',220,110,.9]]]
];
var SFXMAP={},actx=null;SFX.forEach(function(s){SFXMAP[s[0]]=s});
function tone(name){
  var def=SFXMAP[name];if(!def||FAST)return;
  try{actx=actx||new (window.AudioContext||window.webkitAudioContext)();if(actx.state==='suspended')actx.resume();
    def[4].forEach(function(n){var t0=actx.currentTime+(n[4]||0),g=actx.createGain(),src;g.gain.setValueAtTime(.0001,t0);g.gain.exponentialRampToValueAtTime(.16,t0+.008);g.gain.exponentialRampToValueAtTime(.0001,t0+n[3]);
      if(n[0]==='noise'){var len=Math.max(1,Math.floor(actx.sampleRate*n[3])),buf=actx.createBuffer(1,len,actx.sampleRate),d=buf.getChannelData(0);for(var i=0;i<len;i++)d[i]=Math.random()*2-1;
        src=actx.createBufferSource();src.buffer=buf;var f=actx.createBiquadFilter();f.type='bandpass';f.frequency.setValueAtTime(n[1],t0);f.frequency.exponentialRampToValueAtTime(Math.max(40,n[2]),t0+n[3]);src.connect(f);f.connect(g)}
      else{src=actx.createOscillator();src.type=n[0];src.frequency.setValueAtTime(n[1],t0);src.frequency.exponentialRampToValueAtTime(Math.max(30,n[2]),t0+n[3]);src.connect(g)}
      g.connect(actx.destination);src.start(t0);src.stop(t0+n[3]+.02)});
  }catch(e){}
}
var heard={},played={},auds={};
function hear(name){
  var f=AS.sfx[name];if(!f||FAST)return tone(name);
  try{var a=auds[name]||(auds[name]=new Audio(f));a.currentTime=0;played[name]=(played[name]||0)+1;var pr=a.play();if(pr&&pr.catch)pr.catch(function(){tone(name)})}catch(e){tone(name)}
}
function sfx(name){heard[name]=(heard[name]||0)+1;if(prefs.sound)hear(name)}

/* ---------- music: one track under the map and the camp, one under the clash. It starts on the first tap in the game. ---------- */
var MUS={},MVOL=.3,musWant='map',musStarted=false;
function musEl(k){if(!AS.music||!AS.music[k])return null;if(!MUS[k]){var a=new Audio(AS.music[k]);a.loop=true;a.volume=0;a.preload='none';MUS[k]=a}return MUS[k]}
function fadeTo(a,to,then){clearInterval(a._f);if(FAST){a.volume=to;if(then)then();return}
  a._f=setInterval(function(){var up=to>a.volume,v=a.volume+(up?.03:-.03);if(up?v>=to:v<=to){a.volume=to;clearInterval(a._f);if(then)then()}else a.volume=v},50)}
function musNow(){return !FAST&&prefs.music&&musStarted&&!document.hidden&&AS.music&&AS.music[musWant]?musWant:null}
function music(which){if(which)musWant=which;var on=musNow();
  ['map','clash'].forEach(function(k){var a=k===on||MUS[k]?musEl(k):null;if(!a)return;
    if(k===on){var pr=a.play();if(pr&&pr.catch)pr.catch(function(){});fadeTo(a,MVOL)}else if(!a.paused)(function(el){fadeTo(el,0,function(){el.pause()})})(a)})}
document.addEventListener('visibilitychange',function(){music()});

/* ---------- small drawings ---------- */
var IC={
  sword:'<path d="M12 2.500v13M7.500 15.500h9M12 15.500V21"/>',
  cast:'<path d="M4 20C4 11 11 4.500 20 4.500M16.500 1.500l3.500 3-3.500 3"/>',
  swords:'<path d="M5 5l11 11M19 5L8 16M5 9V5h4M15 5h4v4M4 17l3 3M20 17l-3 3M6 14l4 4M18 14l-4 4"/>',
  shield:'<path d="M12 3l7 3v5c0 5-3.500 8-7 10-3.500-2-7-5-7-10V6z"/>',
  crack:'<path d="M12 3l7 3v5c0 5-3.500 8-7 10-3.500-2-7-5-7-10V6z"/><path d="M13 7l-3 5h4l-3 5"/>',
  coin:'<circle cx="12" cy="12" r="8"/><path d="M12 8v8M9.500 10h3.500a1.500 1.500 0 010 3h-2a1.500 1.500 0 000 3H15"/>',
  deck:'<rect x="4" y="7" width="12" height="14" rx="2"/><path d="M8 7V5a2 2 0 012-2h8a2 2 0 012 2v10a2 2 0 01-2 2h-2"/>',
  drop:'<path d="M12 3c3 4 6 7 6 11a6 6 0 01-12 0c0-4 3-7 6-11z"/>',
  breath:'<path d="M3 9h10a3 3 0 10-3-3M3 15h14a3 3 0 11-3 3M3 12h6"/>',
  pillar:'<path d="M5 21h14M8 21V9M16 21V9M5 9h14M7 5h10v4H7z"/>',
  star:'<path d="M12 3l2.700 5.600 6.200.800-4.500 4.300 1.100 6.100L12 16.900 6.500 19.800l1.100-6.100L3.100 9.400l6.200-.800z"/>',
  arrowR:'<path d="M5 12h14M13 6l6 6-6 6"/>',arrowL:'<path d="M19 12H5M11 6l-6 6 6 6"/>',arrowU:'<path d="M12 19V5M6 11l6-6 6 6"/>',arrowD:'<path d="M12 5v14M6 13l6 6 6-6"/>',
  throw:'<path d="M4 20L18 6M11 6h7v7"/><path d="M4 14v6h6" opacity=".6"/>',
  tree:'<path d="M12 3l6 8h-3l4 6H5l4-6H6zM12 17v4"/>',
  pin:'<circle cx="12" cy="5" r="2"/><path d="M12 7v14M5 13a7 7 0 0014 0M8 11h8"/>',
  target:'<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3"/>',
  square:'<rect x="4" y="4" width="16" height="16" rx="3"/><rect x="9" y="9" width="6" height="6" rx="1"/>',
  barb:'<path d="M4 20L18 6M11 6h7v7M4 20l1-5M4 20l5-1"/>',
  flag:'<path d="M6 21V4M6 4h11l-2.500 4L17 12H6"/>',
  flame:'<path d="M12 3c1 4 5 5.500 5 10a5 5 0 01-10 0c0-2 1-3.500 2-4.500 0 2 1 3 2 3 .500-3-.500-6 1-8.500z"/>',
  bars:'<path d="M5 19l6-14M10 19l6-14M15 19l4-9"/>',
  x:'<path d="M6 6l12 12M18 6L6 18"/>',
  half:'<circle cx="12" cy="12" r="8"/><path d="M12 4a8 8 0 000 16z" fill="currentColor"/>',
  dots:'<circle cx="5" cy="12" r="2"/><circle cx="19" cy="12" r="2"/><path d="M9 12h1M12 12h1M15 12h.500"/>',
  hourglass:'<path d="M7 3h10M7 21h10M8 3c0 5 8 5 8 9s-8 4-8 9M16 3c0 5-8 5-8 9s8 4 8 9"/>',
  undo:'<path d="M4 9h10a5 5 0 010 10H9M4 9l4-4M4 9l4 4"/>',
  heart:'<path d="M12 20s-7-4.500-7-10a4 4 0 017-2.500A4 4 0 0119 10c0 5.500-7 10-7 10z"/>',
  tent:'<path d="M3 20L12 4l9 16zM12 4v16M9 20l3-5 3 5"/>',
  eye:'<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
  cart:'<circle cx="7" cy="18" r="3"/><circle cx="17" cy="18" r="3"/><path d="M3 6h18v8H3zM3 10h18"/>',
  whet:'<path d="M12 3v5M12 16v5M3 12h5M16 12h5M6.500 6.500l2 2M15.500 15.500l2 2M17.500 6.500l-2 2M8.500 15.500l-2 2"/>',
  road:'<path d="M9 3L5 21M15 3l4 18M12 5v2M12 11v2M12 17v2"/>',
  note:'<path d="M9 18V6l10-2v12"/><circle cx="6.500" cy="18" r="2.500"/><circle cx="16.500" cy="16" r="2.500"/>',
  speaker:'<path d="M4 10v4h3l5 4V6L7 10zM16 9.500a3.500 3.500 0 010 5M18.500 7a7 7 0 010 10"/>',
  moon:'<path d="M19 14.500A8 8 0 019.500 5 7 7 0 1019 14.500z"/>'
};
var FXI={throw:'throw',guard:'shield',block:'shield',held:'breath',wound:'drop',stance:'pillar',risen:'star',again:'arrowR',cover:'tree',tend:'heart',pinned:'pin',marked:'target',open:'crack',tough:'square',barbed:'barb',banner:'flag',rallied:'flag',enraged:'flame',temper:'flame',holds:'hourglass',flurry:'bars',far:'dots',down:'arrowD',broken:'x',edge:'arrowU',halved:'half',pushed:'arrowL'};
var TREEI={blade:'sword',foot:'shield',cast:'cast',breath:'breath',bind:'heart',eye:'eye'};
var FXORDER=['wound','throw','pinned','marked','open','enraged','rallied','banner','tough','barbed','held','stance','risen','again','tend','flurry','holds','temper','cover'];
function svg(name,cls){return '<svg class="ic'+(cls?' '+cls:'')+'" viewBox="0 0 24 24" aria-hidden="true">'+(IC[name]||IC.square)+'</svg>'}
function fxIcon(id){return svg(FXI[id]||'square')}
function fxChips(list,side){return '<div class="fxs">'+list.map(function(e,i){return '<button type="button" class="fx tone-'+e.tone+'" data-fx="'+side+':'+i+'" title="'+esc(e.text)+'">'+fxIcon(e.id)+'<span>'+e.label+'</span></button>'}).join('')+'</div>'}
function bar(v,m,c){return '<div class="bar '+(c||'')+'"><i style="width:'+Math.max(0,100*v/m)+'%"></i></div>'}
function pips(n,max,c){var h='';for(var i=0;i<max;i++)h+='<span class="pip '+(c||'')+(i<n?' on':'')+'"></span>';return h}
function logBox(l){return '<div class="log" aria-live="polite">'+l.slice(-5).map(function(x){return '<div class="'+(x[1]||'')+'">'+x[0]+'</div>'}).join('')+'</div>'}
function chipRow(c){return c.length?'<div class="chips">'+c.map(function(x){return '<span class="chip '+x[1]+'">'+x[0]+'</span>'}).join('')+'</div>':''}
function cardHTML(id,o){o=o||{};var c=C[id],tag=o.tag||'div',pr=o.price?'<span class="price num">'+svg('coin')+c.p+'</span>':'';
  return '<'+tag+' class="card t-'+c.t+' k-'+c.k.toLowerCase()+' '+(o.cls||'')+'"'+(tag==='button'?' type="button"':'')+(o.attrs||'')+'>'+(c.dead?'':'<span class="cost num">'+c.c+'</span>')+
    '<span class="gem">'+svg(c.dead?'drop':TREEI[c.t])+'</span>'+(has(AS.art,c.art)?'<span class="art"><img src="'+A+c.art+'.webp" alt="" draggable="false">'+pr+'</span>':'<span class="art ph"><span>'+(c.dead?'wound':'art to make')+'</span>'+pr+'</span>')+
    '<b>'+c.n+'</b><span class="rk">'+(c.r?c.r+' · ':'')+(c.lent?'lent · ':'')+c.k+' · '+TREE[c.t]+'</span><small>'+LH.cardText(id,o.K)+'</small></'+tag+'>'}
function floatAt(layer,x,y,text,cls){
  if(FAST||!layer)return;var el=document.createElement('span');el.className='float '+(cls||'');el.textContent=text;el.style.left=x+'%';el.style.top=y+'%';layer.appendChild(el);
  if(REDUCED||!el.animate){setTimeout(function(){el.remove()},700);return}
  el.animate([{transform:'translate(-50%,-30%) scale(.6)',opacity:0},{transform:'translate(-50%,-60%) scale(1.15)',opacity:1,offset:.18},{transform:'translate(-50%,-110%) scale(1)',opacity:1,offset:.7},{transform:'translate(-50%,-170%) scale(1)',opacity:0}],{duration:Math.max(300,ms(950)),easing:'ease-out'}).finished.then(function(){el.remove()},function(){el.remove()});
}
function pulse(el,cls){if(!el||FAST)return;el.classList.remove(cls);void el.offsetWidth;el.classList.add(cls)}

/* ---------- every action button carries its icon; added in one place, whenever a button appears ---------- */
var ACTI={go:'swords',no:'undo',wait:'shield',end:'hourglass',again:'flag',buy:'coin',mend:'heart',leavemode:'x','hone-strike':'whet','hone-guard':'whet',march:'road',press:'swords',leave:'undo',back:'arrowR'};
function decorate(){var l=root.querySelectorAll('.act[data-a]:not(.deco)');for(var i=0;i<l.length;i++){var n=ACTI[l[i].getAttribute('data-a')];l[i].classList.add('deco');if(n)l[i].insertAdjacentHTML('afterbegin','<span class="bi">'+svg(n)+'</span>');else l[i].classList.add('plain')}}
if(window.MutationObserver)new MutationObserver(decorate).observe(root,{childList:true,subtree:true});

/* ---------- screens ---------- */
root.innerHTML='<div class="scr map" id="scr-map"><div class="scr-top"><b id="m-name"></b><span class="num" id="m-top"></span></div>'+
  '<div class="boardwrap"><div class="board" id="m-board"></div><div class="units" id="m-units"></div><div class="fxl" id="m-fx"></div></div><div class="scr" id="m-rest"></div></div>'+
  '<div class="scr camp" id="scr-camp" hidden></div><div class="scr clash" id="scr-clash" hidden></div>'+
  '<div class="foot"><button type="button" class="tgl" data-toggle="music"></button><button type="button" class="tgl" data-toggle="sound"></button></div><div class="banner" id="banner" hidden></div>';
root.addEventListener('pointerdown',function(){if(!musStarted){musStarted=true;music()}},true);
var $map=$('scr-map'),$mname=$('m-name'),$mtop=$('m-top'),$board=$('m-board'),$units=$('m-units'),$mfx=$('m-fx'),$rest=$('m-rest'),$camp=$('scr-camp'),$clash=$('scr-clash'),$banner=$('banner');
var $stage,$me,$foe,$intent,$cfx,$vs,$tell,$hand,$choice,$tray,$piles,$ctop;
function show(which){$map.hidden=which!=='map';$camp.hidden=which!=='camp';$clash.hidden=which!=='clash';music(which==='clash'?'clash':'map')}

/* ---------- the map ---------- */
function face(u){if(u.side===0)return '<img src="'+A+u.img+'.webp" alt="">';return has(AS.tok,u.key)?'<img src="'+A+'tok-'+u.key+'.webp" alt="">':(u.id==='J'?'K':u.id)}
function tokenIcons(list){var out=[];FXORDER.forEach(function(id){list.forEach(function(e){if(e.id===id&&out.length<3)out.push('<span class="fi tone-'+e.tone+'">'+fxIcon(e.id)+'</span>')})});return out.length?'<span class="fxrow">'+out.join('')+'</span>':''}
function unitInfo(u){
  var fx=LH.effects(G,u),h,an;
  if(u.tend)h='<b>'+u.n+'</b> · the carter · '+u.hp+' of '+u.max+' HP · '+(u.moved?'has moved':'moves '+u.mov)+' · does not fight. Tap a hurt friend beside her to tend them.';
  else if(u.side===0)h='<b>'+u.n+'</b> · '+TREE[u.t]+' · '+u.hp+' of '+u.max+' HP · '+(u.moved?'has moved':'moves '+u.mov)+' · hand of '+(u.hn+u.st.drawUp)+(u.rng>1?' · reaches 2':'');
  else{an=u.ans[u.ai%u.ans.length];h='<b>'+u.n+'</b> · '+TREE[u.t]+' · '+u.hp+' of '+u.max+' HP · moves '+u.mov+(u.rng>1?' · reaches 2':'')+' · strikes for '+(u.atk+(LH.rallied(G,u)?T.rally:0)+(LH.enraged(u)?u.enrage:0))+' on his turn. Next answer: '+LH.ansText({b:an.b,d:an.d+(LH.rallied(G,u)?T.rally:0)+(LH.enraged(u)?u.enrage:0),n:an.n})+'.'}
  h='<span>'+h+'</span>';
  if(fx.length){h+=fxChips(fx,'m');if(UI.fx!==null&&fx[UI.fx])h+='<span class="fxtext"><b>'+fx[UI.fx].label+'.</b> '+fx[UI.fx].text+'</span>';else h+='<span class="fxtext dimm">Tap an effect to read it.</span>'}
  return h;
}
var boardKey='',unitEls={};
function buildBoard(){
  var h='';
  for(var y=0;y<LH.H;y++)for(var x=0;x<LH.W;x++){var c=LH.ter(G,x,y);h+='<button type="button" class="tile'+(c==='w'?' w':c==='~'?' r':c==='f'?' f':c==='d'?' d':c==='b'?' b':'')+'" data-x="'+x+'" data-y="'+y+'" data-t="'+c+'"></button>'}
  $board.innerHTML=h;$units.innerHTML='';unitEls={};walkers={};
}
/* a move is walked, tile by tile; the rules have already moved him, this only shows it */
var walkers={};
function setPos(el,x,y){el.style.left=(x/LH.W*100)+'%';el.style.top=(y/LH.H*100)+'%'}
function dust(x,y){var el=document.createElement('span');el.className='dust';el.style.left=((x+.5)/LH.W*100)+'%';el.style.top=((y+.82)/LH.H*100)+'%';$mfx.appendChild(el);setTimeout(function(){el.remove()},400)}
async function walk(u,path){
  var el=unitEls[u.id];if(FAST||REDUCED||!el||!path||!path.length)return;
  var tk={},step=ms(Math.max(95,Math.min(150,440/path.length))),fx=el._x,fy=el._y,i;walkers[u.id]=tk;el.classList.add('walk');el.style.transitionDuration=step+'ms';
  for(i=0;i<path.length;i++){if(fx!==undefined)dust(fx,fy);fx=path[i][0];fy=path[i][1];setPos(el,fx,fy);
    await new Promise(function(r){setTimeout(r,step)});if(walkers[u.id]!==tk)return}
  delete walkers[u.id];el.classList.remove('walk');el.style.transitionDuration='';setPos(el,u.x,u.y);el._x=u.x;el._y=u.y;
}
var GROUND={'~':'deep water','w':'wood','f':'ford','b':'bridge','d':'road','.':'open ground'};
function syncUnits(acting){
  var s=UI.sel,seen={};
  G.u.forEach(function(u){
    var el=unitEls[u.id];
    if(u.hp<=0){if(el){el.classList.add('gone');(function(e){setTimeout(function(){e.remove()},FAST?0:320)})(el);delete unitEls[u.id]}return}
    if(!el){el=unitEls[u.id]=document.createElement('span');el.className='unit';el.setAttribute('data-u',u.id);
      el.innerHTML='<span class="tok">'+face(u)+'</span><span class="tree '+u.t+'">'+svg(TREEI[u.t])+'</span><span class="fxrow"></span><span class="badge num" hidden></span><span class="hpb'+(u.side?' foe':'')+'"><i></i></span>';$units.appendChild(el)}
    if(!walkers[u.id]){setPos(el,u.x,u.y);el._x=u.x;el._y=u.y}
    el.firstChild.className='tok'+(u.side?' foe':'')+(u.boss?' boss':'')+(u===s?' sel':'')+(u.id===acting?' acting':'')+(u===UI.look?' look':'')+(u.side===0&&!LH.canAct(u)?' spent':'')+(u.side&&has(AS.tok,u.key)?' has':'');
    var ic=tokenIcons(LH.effects(G,u)),row=el.children[2];if(row.getAttribute('data-h')!==ic){row.innerHTML=ic;row.setAttribute('data-h',ic)}
    var bd=el.children[3];bd.hidden=!u.guard;if(u.guard)bd.textContent=u.guard;el.classList.toggle('guarded',!!u.guard);
    el.children[4].firstChild.style.width=(100*u.hp/u.max)+'%';
  });
}
function renderMap(acting){
  var key=G.run.n+'|'+G.map.name+'|'+runId;if(key!==boardKey){boardKey=key;buildBoard()}
  var s=UI.sel,can=s&&LH.canAct(s)&&!busy,r=(can&&!s.moved&&!UI.fc)?LH.reach(G,s):{},fb=(can&&!s.moved&&!UI.fc)?LH.fallBack(G,s):null,fbk=fb&&LH.fellBack(G,s,fb[0],fb[1])?fb[0]+','+fb[1]:'',z=UI.danger?LH.dangerSet(G):{},tg=(can&&!UI.fc)?LH.targets(G,s):[],tt=(can&&!UI.fc)?LH.tendTargets(G,s):[],h='';
  $mname.textContent=G.map.name;$mtop.innerHTML='Battle '+G.run.n+' of 3 · turn '+G.turn+(G.turn>T.maxTurns-8?' of '+T.maxTurns:'')+' · <span class="spoil">'+svg('coin')+G.run.spoils+'</span>';
  var tiles=$board.children;
  for(var i=0;i<tiles.length;i++){var t=tiles[i],x=+t.getAttribute('data-x'),y=+t.getAttribute('data-y'),k=x+','+y,u=LH.at(G,x,y),c=t.getAttribute('data-t');
    t.classList.toggle('dz',!!z[k]);t.classList.toggle('reach',!u&&r[k]!==undefined);t.classList.toggle('back',!u&&k===fbk);t.classList.toggle('hit',!!u&&tg.indexOf(u)>=0);t.classList.toggle('mend',!!u&&tt.indexOf(u)>=0);
    t.setAttribute('aria-label',u?u.n+', '+u.hp+' of '+u.max:GROUND[c])}
  syncUnits(acting);
  h='<div class="legend tri"><span class="trio" title="Footing beats Blade, Blade beats Cast, Cast beats Footing"><span class="tg foot">'+svg('shield')+'Footing</span>'+svg('arrowR')+'<span class="tg blade">'+svg('sword')+'Blade</span>'+svg('arrowR')+'<span class="tg cast">'+svg('cast')+'Cast</span>'+svg('arrowR')+'<span class="tg foot">'+svg('shield')+'</span></span><button class="linkbtn" type="button" data-a="dz">'+(UI.danger?'Hide their reach':'Show their reach')+'</button></div>';
  if(G.over&&!G.over.win&&(UI.ended||!busy)){
    if(!UI.ended){UI.ended=true;sfx(G.over.done?'run_won':'run_lost')}
    h+=logBox(G.log)+'<div class="end"><b>'+G.over.t+'</b><span>'+G.over.s+'</span><span class="renown">Renown <b class="num">'+G.run.renown+'</b> · best <span class="num">'+best(G.run.renown)+'</span></span><span class="legend">Spoils kept, 6 for each battle won, 1 for each turn under '+T.par+' in a battle won, 2 for each friend standing at the end, and a little for health.</span><button class="act primary wide" type="button" data-a="again"><b>A new run</b><small>From the first crossing</small></button></div>';
  }else if(UI.fc){
    var a=UI.fc.a,d=UI.fc.d,p=LH.preview(G,a,d);
    h+='<div class="panel"><span class="lbl">Before you commit</span><b>'+a.n+' on '+LH.nm(d)+' · '+d.hp+' HP</b>'+
      '<span class="num">You play '+p.cards+' cards on '+p.en+' breath. '+p.txt+'</span>'+
      '<span class="num">'+(p.can?'At worst '+a.n+' is left on '+p.worst+' of '+a.max+'.':a.n+' cannot be hurt in this one.')+'</span>'+
      (p.lend.length?'<div class="lenders">'+p.lend.map(function(o){return '<span><img src="'+A+o.img+'.webp" alt="">'+o.n+'</span>'}).join('')+'</div>':'')+chipRow(p.chips)+'</div>'+
      '<div class="acts"><button class="act primary" type="button" data-a="go"><b>Engage</b><small>Play the hand</small></button><button class="act" type="button" data-a="no"><b>Hold</b><small>Think again</small></button></div>';
  }else{
    var info='<span>Tap one of the company. Tap a foe to size him up.</span>',left=G.phase==='player'?LH.matesUp(G).filter(function(o){return LH.canAct(o)&&!o.attacked}).length:0;
    if(G.phase==='enemy')info='<span>Their turn.</span>';else if(s)info=unitInfo(s)+(fbk?'<span class="fxtext">'+svg('arrowD')+' '+s.n+' can fall back through '+LH.at(G,s.x,s.y+1).n+' to the tile behind.</span>':'')+(LH.canUnmove(G,s)?'<button class="linkbtn" type="button" data-a="unmove">Take back the move</button>':'');else if(UI.look)info=unitInfo(UI.look);
    h+=logBox(G.log)+'<div class="panel info">'+info+'</div>';
    h+='<div class="acts"><button class="act" type="button" data-a="wait"'+(can&&!s.attacked?'':' disabled')+'><b>Hold here</b><small>4 guard, and done</small></button><button class="act primary" type="button" data-a="end"'+(busy?' disabled':'')+'><b>End the turn</b><small>'+(left?left+' of yours can still act':'They move')+'</small></button></div>';
  }
  $rest.innerHTML=h;
}
async function turnBanner(text,cls){if(FAST)return;var el=document.createElement('div');el.className='tbanner '+(cls||'');el.textContent=text;$units.parentNode.appendChild(el);
  await anim(el,[{opacity:0,transform:'translateX(-30%)'},{opacity:1,transform:'translateX(0)',offset:.25},{opacity:1,transform:'translateX(0)',offset:.75},{opacity:0,transform:'translateX(30%)'}],cls?640:560);el.remove()}
function tileXY(x,y){return [(x+.5)/LH.W*100,(y+.45)/LH.H*100]}
function flashTile(x,y){if(FAST)return;var u=LH.at(G,x,y);if(u&&unitEls[u.id])pulse(unitEls[u.id],'flash')}
function tapTile(x,y){
  if(busy||G.over||G.clash||G.phase!=='player')return;
  var u=LH.at(G,x,y),s=UI.sel;UI.fx=null;
  if(UI.fc){UI.fc=null}
  if(u&&u.side===0&&s&&s.tend&&LH.tendTargets(G,s).indexOf(u)>=0){var r=LH.tend(G,s,u),p=tileXY(u.x,u.y);UI.sel=null;UI.look=null;renderMap();floatAt($mfx,p[0],p[1],'+'+r.heal,'heal');if(r.wound)floatAt($mfx,p[0],p[1]-7,'Wound set aside','heal');sfx('heal');return}
  if(u&&u.side===0){UI.look=null;UI.sel=LH.canAct(u)?(s===u?null:u):null;if(!UI.sel&&!LH.canAct(u))UI.look=u;sfx('unit_select');return renderMap()}
  if(u){if(s&&LH.targets(G,s).indexOf(u)>=0){UI.fc={a:s,d:u};UI.look=null;sfx('forecast_open')}else{UI.look=UI.look===u?null:u;UI.sel=null;sfx('ui_tap')}return renderMap()}
  var pth=s?LH.path(G,s,x,y):[];
  if(s&&LH.move(G,s,x,y)){sfx('unit_move');walk(s,pth);if(!LH.canAct(s))UI.sel=null}else{UI.sel=null;UI.look=null}
  renderMap();
}
async function runEnemy(){
  if(busy||!LH.endTurn(G))return;lock(true);UI.sel=UI.fc=UI.look=null;UI.fx=null;sfx('enemy_turn');renderMap();await turnBanner('Their turn','foe');
  var ev;
  while((ev=LH.enemyStep(G))){
    if(ev.k==='turn'){renderMap();continue}
    var wk=ev.path&&ev.path.length?walk(LH.byId(G,ev.id),ev.path):null;renderMap(ev.id);
    if(wk){sfx('unit_move');await wk;await wait(90)}
    if(ev.target){
      var t=LH.byId(G,ev.target),p=tileXY(t.x,t.y),e=LH.byId(G,ev.id),q=tileXY(e.x,e.y);
      floatAt($mfx,p[0],p[1],ev.dmg?'-'+ev.dmg:'Held',ev.dmg?'dmg':'blk');sfx(ev.dmg?'hurt':'guard_hold');if(ev.dmg)flashTile(t.x,t.y);
      if(ev.wound){await wait(260);floatAt($mfx,p[0],p[1]-6,'Wound','bad');sfx('wound')}
      if(ev.targetDown)sfx('friend_down');
      if(ev.rip){await wait(300);floatAt($mfx,q[0],q[1],'-'+ev.rip,'dmg');sfx('riposte');flashTile(e.x,e.y);if(ev.foeDown){sfx('foe_down');floatAt($mfx,q[0],q[1]+8,'+'+(e.boss?T.spoilBoss:T.spoilFoe),'gold')}}
      await wait(560);
    }else await wait(ev.pinned||ev.holds?180:120);
  }
  lock(false);await afterMapChange();if(!G.over){sfx('your_turn');turnBanner('Your turn')}
}
/* ---------- from one scene to the next: a curtain crosses the screen with the name of what comes, and the screen changes behind it ---------- */
var CURI={march:'road',win:'flag',lost:'x',night:'moon',done:'star'};
function quiet(fn){var w=busy;busy=false;try{fn()}finally{busy=w}}
async function curtain(kind,title,sub,swap){
  if(FAST||REDUCED){quiet(swap);return}
  var was=busy;lock(true);
  $banner.className='banner cur cur-'+kind;$banner.innerHTML='<span class="cur-rule a"></span><span class="cur-ring">'+svg(CURI[kind]||'flag')+'</span><b>'+title+'</b>'+(sub?'<i>'+sub+'</i>':'')+'<span class="cur-rule b"></span>';$banner.hidden=false;
  await anim($banner,[{clipPath:'inset(0 100% 0 0)'},{clipPath:'inset(0 0 0 0)'}],340,{easing:'cubic-bezier(.7,0,.3,1)'});
  quiet(swap);await wait(kind==='march'?780:1050);
  await anim($banner,[{clipPath:'inset(0 0 0 0)'},{clipPath:'inset(0 0 0 100%)'}],340,{easing:'cubic-bezier(.7,0,.3,1)',fill:'forwards'});
  $banner.hidden=true;still($banner);$banner.className='banner';lock(was);
}
/* after anything on the map that might have ended the battle */
function afterMapChange(){
  if(G.over&&G.over.win){
    if(!$camp.hidden){renderCamp();return Promise.resolve()}
    sfx('battle_won');UI.buy=null;UI.leave=false;
    return curtain('win','The crossing is won',G.map.name+' · '+G.run.spoils+' spoils in the purse',function(){show('camp');renderCamp()})}
  if(G.over&&!UI.ended){UI.ended=true;sfx(G.over.done?'run_won':'run_lost');
    return curtain(G.over.done?'done':G.over.night?'night':'lost',G.over.t,G.over.done?'Three crossings, three captains':'The run ends here',function(){show('map');renderMap()})}
  renderMap();return Promise.resolve();
}

/* ---------- the camp between battles ---------- */
function miniMap(m){var h='<span class="mm" aria-hidden="true">';m.rows.forEach(function(r){for(var i=0;i<r.length;i++){var c=r.charAt(i);h+='<i class="'+(c==='w'?'w':c==='~'?'r':c==='f'?'f':c==='d'?'d':c==='b'?'b':'g')+'"></i>'}});return h+'</span>'}
function renderCamp(){
  var D=G.u[0],m=G.camp.market,nx=LH.MAPS[G.run.n],sp=G.run.spoils,deck={},h,co=G.u.filter(function(u){return u.side===0});
  G.run.deck.forEach(function(id){var n=C[id].n+(C[id].r==='honed'?' (honed)':'');deck[n]=deck[n]||{n:0,id:id};deck[n].n++});
  h='<div class="scr-top"><b>Camp</b><span class="num">After battle '+G.run.n+' of 3</span></div>'+
    '<div class="camphero"><span class="glow"></span><span class="cfaces">'+co.map(function(u,i){return '<img class="'+(i===Math.floor(co.length/2)?'gap':'')+'" src="'+A+u.img+'.webp" alt="'+esc(u.n)+'">'}).join('')+'</span></div>'+
    '<div class="stats"><div class="stat gold" id="camp-sp"><span class="si">'+svg('coin')+'</span><b class="num">'+sp+'</b><small>spoils to spend</small></div>'+
      '<div class="stat"><span class="si">'+svg('heart')+'</span><b class="num">'+D.hp+'<i>/'+D.max+'</i></b><small>Darrow · +'+Math.min(T.rest,D.max-D.hp)+' at dawn</small>'+bar(D.hp,D.max,'me')+'</div>'+
      '<div class="stat"><span class="si">'+svg('star')+'</span><b class="num">'+LH.renown(G)+'</b><small>renown so far</small></div></div>'+
    '<span class="lbl sec">'+svg('cart')+'The company offers · one of each</span><div class="hand3">'+m.map(function(id){return cardHTML(id,{tag:'button',price:1,cls:(UI.buy===id?'pick':'')+(C[id].p>sp?' poor':''),attrs:' data-buy="'+id+'"'})}).join('')+(m.length?'':'<span class="legend">Nothing left on the blanket.</span>')+'</div>';
  if(UI.buy&&m.indexOf(UI.buy)>=0){var c=C[UI.buy];h+='<div class="panel"><span><b>'+c.n+'</b> <span class="lbl">'+c.c+' breath · '+c.k+' · '+TREE[c.t]+'</span></span><span>'+LH.cardText(UI.buy)+'</span></div><div class="acts"><button class="act primary wide" type="button" data-a="buy"'+(c.p>sp?' disabled':'')+'><b>Take it for '+c.p+' spoils</b><small>'+(c.p>sp?'You have '+sp:'Leaves '+(sp-c.p)+'. It joins the deck for the rest of the run')+'</small></button></div>'}
  h+='<span class="lbl sec">'+svg('whet')+'Mend, hone, travel light</span><div class="acts"><button class="act" type="button" data-a="mend"'+(sp<T.mendCost||D.hp>=D.max?' disabled':'')+'><b>Mend'+price(T.mendCost,sp)+'</b><small>Darrow gets '+T.mend+' back</small></button>'+
    '<button class="act'+(UI.leave?' on':'')+'" type="button" data-a="leavemode"'+(sp<T.removeCost||G.run.deck.length<=LH.MIN_DECK?' disabled':'')+'><b>Leave one'+price(T.removeCost,sp)+'</b><small>'+(UI.leave?'Now tap a card below':'A leaner deck draws its best more often')+'</small></button>'+
    '<button class="act" type="button" data-a="hone-strike"'+(sp<T.honeCost||G.run.deck.indexOf('strike')<0?' disabled':'')+'><b>Hone a Strike'+price(T.honeCost,sp)+'</b><small>7 becomes 10</small></button>'+
    '<button class="act" type="button" data-a="hone-guard"'+(sp<T.honeCost||G.run.deck.indexOf('guard')<0?' disabled':'')+'><b>Hone a Guard'+price(T.honeCost,sp)+'</b><small>6 becomes 9</small></button></div>';
  h+='<span class="lbl sec">'+svg('deck')+'The deck · '+G.run.deck.length+' cards</span><div class="decklist'+(UI.leave?' leaving':'')+'">'+Object.keys(deck).sort().map(function(n){return '<button type="button" class="dk" data-leave="'+deck[n].id+'"'+(UI.leave?'':' disabled')+'>'+n+(deck[n].n>1?' ×'+deck[n].n:'')+'</button>'}).join('')+'</div>';
  h+='<div class="marchrow">'+miniMap(nx)+'<button class="act primary" type="button" data-a="march"><b>March on</b><small>'+nx.name+'. Spoils you keep count toward Renown.</small></button></div>';
  $camp.innerHTML=h;
}
function price(n,have){return ' <span class="pr num'+(n>have?' short':'')+'">'+svg('coin')+n+'</span>'}
/* spoils leaving the purse: the number jumps and the cost floats off it */
function spent(n){var el=$('camp-sp');if(!el||FAST||n<=0)return;pulse(el,'pop');var f=document.createElement('span');f.className='spend num';f.textContent='-'+n;el.appendChild(f);setTimeout(function(){f.remove()},800)}

/* ---------- the clash ---------- */
function figure(u){
  if(u.id==='D')return '<div class="fig"><img class="cut" src="'+A+'high-guard.webp" alt="Darrow, practice sword raised" draggable="false"></div>';
  var key=u.side?u.key:u.n.toLowerCase();
  if(has(AS.fig,key))return '<div class="fig"><img class="cut noflip" src="'+A+'fig-'+key+'.webp" alt="'+esc(u.n)+'" draggable="false"></div>';
  if(u.img)return '<div class="fig ph"><img src="'+A+u.img+'.webp" alt="" draggable="false"><span class="phtag">figure to make</span></div>';
  return '<div class="fig ph"><svg viewBox="0 0 40 60" aria-hidden="true"><circle cx="20" cy="11" r="7"/><path d="M7 60V32q0-11 13-11t13 11v28z"/></svg><span class="phtag">'+u.n.toLowerCase()+' 2:3</span></div>';
}
function buildClash(){
  var K=G.clash;
  $clash.innerHTML='<div class="scr-top"><b>The Clash</b><span id="c-top"></span></div>'+
    '<div class="stage g-'+({w:'wood',f:'ford',b:'bridge',d:'road'}[LH.ter(G,K.d.x,K.d.y)]||'grass')+'" id="c-stage"><div class="side me" id="c-me">'+figure(K.a)+'</div><div class="side foe" id="c-foe">'+figure(K.d)+'</div><div class="intent" id="c-intent"></div>'+
    (K.p.lend.length?'<div class="linked">'+K.p.lend.map(function(o){return '<img src="'+A+o.img+'.webp" alt="'+o.n+' is with you">'}).join('')+'</div>':'')+
    '<div class="fxl" id="c-fx"></div></div>'+
    '<div class="vs" id="c-vs"></div><div class="tell" id="c-tell" aria-live="polite"></div>'+
    '<div class="handwrap"><div class="hand" id="c-hand"></div><div class="choice" id="c-choice" hidden></div></div>'+
    '<div class="tray" id="c-tray"></div><div class="pilelist" id="c-piles" hidden></div>';
  $stage=$('c-stage');$me=$('c-me').firstChild;$foe=$('c-foe').firstChild;$intent=$('c-intent');$cfx=$('c-fx');$vs=$('c-vs');$tell=$('c-tell');$hand=$('c-hand');$choice=$('c-choice');$tray=$('c-tray');$piles=$('c-piles');$ctop=$('c-top');
  $hand.addEventListener('pointerdown',cardDown);$hand.addEventListener('keydown',cardKey);
  $stage.addEventListener('click',function(){if(!busy&&UI.card>=0)selectCard(-1)});
}
function shield(n){return '<span class="sh'+(n?'':' zero')+'" title="Block">'+svg('shield','solid')+'<i class="num">'+n+'</i></span>'}
function paintVs(){
  var K=G.clash,a=K.a,d=K.d,fx=LH.clashEffects(G);
  $vs.innerHTML='<div><span class="who"><b>'+a.n+'</b><span class="num">'+a.hp+' / '+a.max+'</span></span><div class="hpline">'+shield(K.block)+bar(a.hp,a.max,'me')+'</div>'+fxChips(fx.a.filter(function(e){return e.id!=='block'}),'a')+'</div>'+
    '<div><span class="who"><b>'+d.n+'</b><span class="num">'+d.hp+' / '+d.max+'</span></span><div class="hpline">'+bar(d.hp,d.max)+shield(K.fb)+'</div>'+fxChips(fx.d.filter(function(e){return e.id!=='block'}),'d')+'</div>';
}
function paintIntent(){
  var K=G.clash;if(K.phase!=='play'){$intent.hidden=true;return}$intent.hidden=false;
  var it=LH.intent(G);$intent.className='intent'+(it.none?' none':'')+(it.halved?' halved':'')+(it.up?' up':'');
  $intent.innerHTML=it.none?'<b>Out of reach</b><small>no answer</small>':svg('sword')+'<b class="num">'+it.d+(it.n>1?'<i>×'+it.n+'</i>':'')+'</b><small>'+(it.broken?'Broken: halved':it.halved?'halved':'his answer')+'</small>';
}
function paintTop(){var K=G.clash;$ctop.textContent=G.opts.rounds>1?'Round '+K.round+' of '+G.opts.rounds:K.a.n+' on '+LH.nm(K.d)}
function paintTray(){
  var K=G.clash,a=K.a,play=K.phase==='play',it=play?LH.intent(G):{none:1},any=play&&K.hand.some(function(_,i){return !LH.playable(G,i)}),dis=play?'':' disabled';
  $tray.innerHTML='<button class="pile" type="button" data-a="pile-draw"'+dis+' aria-label="Draw pile, '+a.dk.draw.length+' cards">'+svg('deck')+'<i class="num">'+a.dk.draw.length+'</i><small>Draw</small></button>'+
    '<div class="orb'+(K.en?'':' empty')+'" id="c-orb" aria-label="'+K.en+' breath"><b class="num">'+K.en+'</b><small>breath</small></div>'+
    (a.id==='D'?'<button class="mini" type="button" data-a="redraw"'+(play&&G.run.insp>0&&!K.redrawn?'':' disabled')+' aria-label="A new hand for one Inspiration, '+G.run.insp+' left"><span class="pip insp on"></span><b class="num">'+G.run.insp+'</b><small>New hand</small></button>':'')+
    '<button class="endbtn'+(play&&!any?' ready':'')+'" type="button" data-a="endhand"'+dis+'><b>End hand</b><small>'+(it.none?'He cannot answer':'He strikes for '+it.d+(it.n>1?' ×'+it.n:''))+'</small></button>'+
    '<button class="pile" type="button" data-a="pile-disc"'+dis+' aria-label="Played pile, '+a.dk.disc.length+' cards">'+svg('deck')+'<i class="num">'+a.dk.disc.length+'</i><small>Played</small></button>';
}
function tell(html,cls){$tell.innerHTML=html?'<div class="'+(cls||'')+'">'+html+'</div>':defaultTell()}
function defaultTell(){
  var K=G.clash;if(K.phase!=='play')return '';
  if(K.round>1)return '<div>Round '+K.round+'. He strikes '+(T.pressUp*(K.round-1))+' harder and you have '+(T.pressBreath*(K.round-1))+' less breath.</div>';
  return '<div class="dimm">Tap a card to read it, tap again or drag it up to play. Tap an effect to read it.</div>';
}
function tellCard(i){
  var K=G.clash,id=K.hand[i],c=C[id],why=LH.playable(G,i);
  tell('<b>'+c.n+'</b> <span class="lbl">'+(c.dead?'':c.c+' breath · ')+c.k+' · '+TREE[c.t]+(c.lent?' · lent':'')+'</span><br>'+LH.cardText(id,K)+(why?' <span class="warn">'+why+'</span>':' <span class="lbl">Tap again or drag up to play.</span>'));
}
function fan(){
  var cards=$hand.children,n=cards.length;if(!n)return;
  var pad=12,Wd=$hand.clientWidth-pad*2,cw=cards[0].offsetWidth||104,step=n>1?Math.min(cw*.86,(Wd-cw)/(n-1)):0,x0=pad+(Wd-(cw+step*(n-1)))/2;
  for(var i=0;i<n;i++){var o=i-(n-1)/2,el=cards[i];el.style.setProperty('--x',(x0+step*i)+'px');el.style.setProperty('--r',(o*3)+'deg');el.style.setProperty('--y',(o*o*2)+'px');el.style.zIndex=i+1}
}
function deal(els){
  els.forEach(function(el,k){var fin=getComputedStyle(el).transform;
    anim(el,[{transform:'translate(-40px,150px) scale(.35)',opacity:0},{transform:fin==='none'?'translate(0,0)':fin,opacity:1}],300,{delay:ms(k*70),fill:'backwards'});
    if(!FAST)setTimeout(function(){sfx('card_deal')},ms(k*70))});
}
function cardEl(id){var t=document.createElement('div');t.innerHTML=cardHTML(id,{cls:'hcard',attrs:' data-id="'+id+'" tabindex="0" role="button"',K:G.clash});return t.firstChild}
/* bring the cards on screen into line with the hand: keep what is still held, drop what is gone, make only what is new */
function syncHand(){
  var K=G.clash,want=K.hand,have=Array.prototype.slice.call($hand.children),p=0,fresh=[],j,k;
  for(j=0;j<want.length;j++){
    var q=-1,el;for(k=p;k<have.length;k++)if(have[k].getAttribute('data-id')===want[j]){q=k;break}
    if(q>=0){for(k=p;k<q;k++)have[k].remove();el=have[q];p=q+1}
    else{el=cardEl(want[j]);$hand.insertBefore(el,have[p]||null);fresh.push(el)}
    var why=LH.playable(G,j),c=C[want[j]],txt=LH.cardText(want[j],K),sm=el.lastChild;
    el.setAttribute('data-i',j);el.classList.toggle('cant',!!why);el.classList.toggle('sel',j===UI.card);el.classList.remove('drag');el.style.transform='';
    el.setAttribute('aria-label',c.n+(c.dead?'':', '+c.c+' breath'));if(sm.innerHTML!==txt)sm.innerHTML=txt;
  }
  for(k=p;k<have.length;k++)have[k].remove();
  fan();return fresh;
}
function paintHand(redeal){
  var K=G.clash,play=K.phase==='play';$hand.hidden=!play;$choice.hidden=K.phase!=='choice';
  if(K.phase==='choice'){var ni=LH.nextIntent(G);
    $choice.innerHTML='<p>Round '+K.round+' of '+G.opts.rounds+' is done. '+K.a.n+' has '+K.a.hp+' HP.</p><div class="acts"><button class="act primary" type="button" data-a="press"><b>Press on</b><small>He will '+LH.ansText(ni)+'. '+T.pressBreath*K.round+' less breath.</small></button><button class="act" type="button" data-a="leave"><b>Break off</b><small>Back to the line</small></button></div>'}
  if(!play){$hand.innerHTML='';return}
  if(redeal)$hand.innerHTML='';
  deal(syncHand());
}
function paintAll(fresh){paintTop();paintVs();paintIntent();paintTray();paintHand(fresh);if(UI.card>=0&&G.clash.hand[UI.card])tellCard(UI.card);else tell('')}
function selectCard(i){UI.card=i;for(var k=0;k<$hand.children.length;k++)$hand.children[k].classList.toggle('sel',k===i);if(i>=0){sfx('card_lift');tellCard(i)}else tell('')}
function sideXY(who){return who==='a'?[22,42]:[76,46]}
function slash(who,heavy){if(FAST||REDUCED)return;var p=sideXY(who),el=document.createElement('span');el.className='slash'+(who==='a'?' flip':'')+(heavy?' heavy':'');el.style.left=p[0]+'%';el.style.top=(p[1]+8)+'%';el.innerHTML='<svg viewBox="0 0 100 100"><path d="M14 84Q70 70 88 14"/></svg>';$cfx.appendChild(el);setTimeout(function(){el.remove()},ms(420))}
function shake(heavy){anim($stage,[{transform:'translate(0,0)'},{transform:'translate('+(heavy?5:3)+'px,-2px)'},{transform:'translate(-'+(heavy?4:2)+'px,1px)'},{transform:'translate(0,0)'}],heavy?220:160)}
var STAT_SFX={Broken:'break',Enraged:'enrage'};
async function showFx(fx){
  for(var j=0;j<fx.length;j++){var f=fx[j],p;
    if(f.k==='dmg'){if(!f.by)anim($me,[{transform:'translateX(0)'},{transform:'translateX(34px)'},{transform:'translateX(0)'}],260);await wait(110);
      p=sideXY('d');if(f.n>0){slash('d',f.n>=8||f.crit);if(f.n>=8||f.crit)shake(true);floatAt($cfx,p[0],p[1],'-'+f.n,'dmg'+(f.crit?' crit':''));pulse($foe,'hit');sfx(f.n>=8||f.crit?'hit_heavy':'hit_light')}else{floatAt($cfx,p[0],p[1],'Blocked','blk');sfx('hit_blocked')}
      if(f.by)floatAt($cfx,p[0],p[1]-20,f.by,'info');
      paintVs();paintIntent();await wait(330)}
    else if(f.k==='block'){p=sideXY('a');floatAt($cfx,p[0],p[1],'+'+f.n,'blk');sfx('block_gain');paintVs();pulse($vs.querySelector('.sh'),'pop');await wait(240)}
    else if(f.k==='heal'){p=sideXY('a');floatAt($cfx,p[0],p[1],'+'+f.n,'heal');sfx('heal');paintVs();await wait(240)}
    else if(f.k==='breath'){p=sideXY('a');floatAt($cfx,p[0],p[1]+18,'+'+f.n+' breath','info');sfx('breath_gain');paintTray();pulse($('c-orb'),'pop');await wait(220)}
    else if(f.k==='draw'){if(f.n){paintHand();await wait(260)}}
    else if(f.k==='status'){p=sideXY(f.who);floatAt($cfx,p[0],p[1]-16,f.t,'info');sfx(STAT_SFX[f.t]||'status_good');paintVs();paintIntent();await wait(260)}
    else if(f.k==='stance'){p=sideXY('a');floatAt($cfx,p[0],p[1]-16,f.t,'info');sfx('stance');paintVs();await wait(300)}
    else if(f.k==='friend'){p=sideXY('a');floatAt($cfx,p[0]-8,p[1]+20,LH.byId(G,f.id).n+' +'+f.n+' guard','info');sfx('block_gain');await wait(240)}
    else if(f.k==='cleanse'){p=sideXY('a');floatAt($cfx,p[0],p[1]-16,'Wound set aside','heal');sfx('heal');paintVs();paintHand();await wait(240)}
    else if(f.k==='spoils'){p=sideXY('d');floatAt($cfx,50,30,'+'+f.n+' spoils','gold');sfx('spoils');await wait(260)}
    else if(f.k==='carry'){floatAt($cfx,88,30,'-'+f.n+' beside him','dmg');sfx('hit_heavy');if(f.down)sfx('foe_down');await wait(320)}
    else if(f.k==='wound'){p=sideXY('a');floatAt($cfx,p[0],p[1]-18,'Wound','bad');sfx('wound');paintVs();await wait(300)}
    else if(f.k==='down'){(f.who==='d'?$foe:$me).classList.add('fallen');sfx(f.who==='d'?'foe_down':'friend_down');await wait(520)}
  }
}
async function startClash(a,d){
  if(busy)return;lock(true);
  if(!LH.engage(G,a,d)){lock(false);return renderMap()}
  UI.sel=UI.fc=UI.look=null;UI.card=-1;UI.fx=null;sfx('clash_start');
  $banner.className='banner vsb';$banner.innerHTML='<span class="duo"><span class="tok">'+face(a)+'</span>'+svg('swords')+'<span class="tok foe'+(has(AS.tok,d.key)?' has':'')+'">'+face(d)+'</span></span><b>'+a.n+'</b><i>ON</i><b>'+LH.nm(d)+'</b>';$banner.hidden=false;
  await anim($banner,[{opacity:0,transform:'scale(1.25)'},{opacity:1,transform:'scale(1)',offset:.3},{opacity:1,transform:'scale(1)',offset:.8},{opacity:0,transform:'scale(.97)'}],620);
  buildClash();show('clash');$banner.hidden=true;paintAll(true);
  anim($me,[{transform:'translateX(-70px)',opacity:0},{transform:'translateX(0)',opacity:1}],320);anim($foe,[{transform:'translateX(70px)',opacity:0},{transform:'translateX(0)',opacity:1}],320);
  await wait(300+70*G.clash.hand.length);lock(false);
}
async function doPlay(i){
  var K=G.clash;if(busy||!K||K.phase!=='play')return;
  var el=$hand.children[i],why=LH.playable(G,i);
  if(why){if(el){el.style.transform='';el.classList.remove('drag');pulse(el,'nudge')}sfx('card_cant');selectCard(i);return}
  lock(true);
  var c=C[K.hand[i]],r=el.getBoundingClientRect(),host=$clash.getBoundingClientRect(),tg=(c.dmg||c.assist||c.open||c.halve||c.mark||c.pin?$foe:$me).getBoundingClientRect();
  var w=el.offsetWidth,hh=el.offsetHeight,k0=r.width/w,ghost=el.cloneNode(true);ghost.className=ghost.className.replace(/\b(hcard|sel|drag|cant|nudge)\b/g,'')+' ghost';ghost.removeAttribute('style');ghost.removeAttribute('tabindex');
  ghost.style.left=(r.left-host.left+(r.width-w)/2)+'px';ghost.style.top=(r.top-host.top+(r.height-hh)/2)+'px';ghost.style.width=w+'px';ghost.style.height=hh+'px';ghost.style.transform='scale('+k0+')';
  var dx=(tg.left+tg.width/2)-(r.left+r.width/2),dy=(tg.top+tg.height/2)-(r.top+r.height/2);
  var fx=LH.play(G,i);UI.card=-1;$clash.appendChild(ghost);el.remove();paintHand();paintTray();tell('<b>'+c.n+'</b>');sfx(c.k==='Attack'?'card_attack':'card_skill');
  await anim(ghost,[{transform:'translate(0,0) scale('+k0+')',opacity:1},{transform:'translate('+dx+'px,'+dy+'px) scale(.8)',opacity:1,offset:.72},{transform:'translate('+dx+'px,'+dy+'px) scale(.4)',opacity:0}],400,{fill:'forwards'});
  ghost.remove();
  await showFx(fx||[]);
  if(G.clash&&G.clash.phase==='won'){paintVs();paintIntent();paintTray();await wait(420);await endClash();lock(false);return}
  paintAll();lock(false);
}
async function doEnd(){
  var K=G.clash;if(busy||!K||K.phase!=='play')return;lock(true);UI.card=-1;sfx('end_hand');
  await anim($hand,[{opacity:1,transform:'translateY(0)'},{opacity:0,transform:'translateY(36px)'}],200,{fill:'forwards'});
  var fx=LH.endHand(G),ev=fx[0],p=sideXY('a'),q=sideXY('d');paintHand();still($hand);paintTray();tell('');
  if(ev.none){floatAt($cfx,q[0],q[1]-10,'Out of reach','info');await wait(520)}
  else{pulse($intent,'pop');sfx('foe_windup');await anim($foe,[{transform:'translateX(0)'},{transform:'translateX(-40px)'},{transform:'translateX(0)'}],300);
    if(ev.n>0){slash('a',ev.n>=8);shake(ev.n>=8);floatAt($cfx,p[0],p[1],'-'+ev.n,'dmg');pulse($me,'hit');sfx('hurt')}else{floatAt($cfx,p[0],p[1],'Blocked','blk');sfx('hit_blocked')}
    paintVs();await wait(620)}
  if(fx.length>1)await showFx(fx.slice(1));
  paintVs();paintIntent();
  if(K.phase==='choice'){paintTop();paintHand();tell('<b>He has answered.</b> Press on for another round, or break off with what you have.');lock(false);return}
  await wait(380);await endClash();lock(false);
}
function doRedraw(){var K=G.clash;if(busy||!K)return;if(LH.redraw(G)){UI.card=-1;paintAll(true);tell('<b>Inspiration spent.</b> A new hand.')}}
function doPress(){if(busy||!G.clash)return;if(LH.pressOn(G)){sfx('press_on');UI.card=-1;paintAll(true)}}
async function doLeave(){if(busy||!G.clash)return;lock(true);if(LH.leave(G))await endClash();lock(false)}
async function endClash(){
  var a=G.clash.a;
  await anim($clash,[{opacity:1},{opacity:0}],200,{fill:'forwards'});
  LH.closeClash(G);$clash.innerHTML='';UI.card=-1;UI.fx=null;UI.sel=(!G.over&&LH.canAct(a))?a:null;
  show('map');still($clash);
  if(G.over){renderMap();await afterMapChange()}
  else{quiet(renderMap);await anim($map,[{opacity:0},{opacity:1}],200)}
}
function showPile(which){
  var K=G.clash,a=K.a,list=which==='draw'?a.dk.draw:a.dk.disc;
  function names(l){var c={};l.forEach(function(id){c[C[id].n]=(c[C[id].n]||0)+1});return Object.keys(c).sort().map(function(n){return '<li>'+n+(c[n]>1?' ×'+c[n]:'')+'</li>'}).join('')||'<li class="none">Empty</li>'}
  $piles.innerHTML='<h3>'+(which==='draw'?'Still to draw, in no order':'Played this battle')+' · '+list.length+'</h3><ul>'+names(list)+'</ul>'+
    (a.dk.gone.length?'<h3>Used up until the next battle · '+a.dk.gone.length+'</h3><ul>'+names(a.dk.gone)+'</ul>':'')+'<p class="legend">Tap anywhere to close.</p>';
  $piles.hidden=false;
}
/* tap to read, tap again to play; or drag the card up onto the field */
function cardDown(e){
  var el=e.target.closest('.hcard');if(!el||busy||!G.clash||G.clash.phase!=='play')return;
  if(e.button!==undefined&&e.button>0)return;
  var i=+el.getAttribute('data-i'),sx=e.clientX,sy=e.clientY,drag=false;e.preventDefault();
  function mv(ev){var dx=ev.clientX-sx,dy=ev.clientY-sy;
    if(!drag&&Math.abs(dx)+Math.abs(dy)>10){drag=true;el.classList.add('drag');if(UI.card!==i)selectCard(i);el.classList.remove('sel')}
    if(drag){el.style.transform='translate(calc(var(--x) + '+dx+'px),calc(var(--y) + '+dy+'px)) scale(1.12)';$stage.classList.toggle('drop',dy<-70)}}
  function up(ev){
    window.removeEventListener('pointermove',mv);window.removeEventListener('pointerup',up);window.removeEventListener('pointercancel',up);$stage.classList.remove('drop');
    if(drag){var dy=ev.clientY-sy;if(ev.type==='pointerup'&&dy<-70)return doPlay(i);el.classList.remove('drag');el.style.transform='';selectCard(i);return}
    if(ev.type!=='pointerup')return;
    if(UI.card===i)doPlay(i);else selectCard(i);
  }
  window.addEventListener('pointermove',mv);window.addEventListener('pointerup',up);window.addEventListener('pointercancel',up);
}
function cardKey(e){if(e.key!=='Enter'&&e.key!==' ')return;var el=e.target.closest('.hcard');if(!el||busy)return;e.preventDefault();var i=+el.getAttribute('data-i');if(UI.card===i)doPlay(i);else selectCard(i)}

/* ---------- buttons ---------- */
function newRun(){runId++;G=LH.newRun({rounds:prefs.rounds,level:prefs.level,seed:window.LH_SEED,deck:prefs.deck==='all'?LH.BASE_DECK.concat(LH.POOL):undefined});UI={sel:null,fc:null,look:null,danger:UI.danger,card:-1,fx:null,buy:null,leave:false,ended:false};show('map');renderMap()}
root.addEventListener('click',function(e){
  if($piles&&!$piles.hidden&&e.target.closest('#c-piles')){$piles.hidden=true;return}
  var f=e.target.closest('[data-fx]');
  if(f){var kv=f.getAttribute('data-fx').split(':'),i=+kv[1];sfx('ui_tap');
    if(kv[0]==='m'){UI.fx=UI.fx===i?null:i;return renderMap()}
    if(G.clash){var list=LH.clashEffects(G)[kv[0]].filter(function(x){return x.id!=='block'});if(list[i]){UI.card=-1;for(var k=0;k<$hand.children.length;k++)$hand.children[k].classList.remove('sel');tell('<b>'+list[i].label+'.</b> '+list[i].text)}}return}
  var bu=e.target.closest('[data-buy]');if(bu&&!busy&&LH.inCamp(G)){UI.buy=UI.buy===bu.getAttribute('data-buy')?null:bu.getAttribute('data-buy');UI.leave=false;sfx('card_lift');return renderCamp()}
  var lv=e.target.closest('[data-leave]');if(lv&&!lv.disabled&&UI.leave&&LH.inCamp(G)){var h0=G.run.spoils;if(LH.campRemove(G,lv.getAttribute('data-leave')))sfx('camp_leave');UI.leave=false;renderCamp();return spent(h0-G.run.spoils)}
  var t=e.target.closest('[data-x]');if(t)return tapTile(+t.getAttribute('data-x'),+t.getAttribute('data-y'));
  var b=e.target.closest('button[data-a]');if(!b||b.disabled)return;var a=b.getAttribute('data-a');
  if(a==='dz'){UI.danger=!UI.danger;sfx('ui_tap');return renderMap()}
  if(busy)return;
  if(a==='again'){sfx('ui_tap');return curtain('march',LH.MAPS[0].name,'Battle 1 of 3',newRun)}
  if(LH.inCamp(G)){var had=G.run.spoils;
    if(a==='buy'&&UI.buy){if(LH.campBuy(G,UI.buy))sfx('camp_buy');UI.buy=null}
    else if(a==='mend'){if(LH.campMend(G))sfx('heal')}
    else if(a==='leavemode'){UI.leave=!UI.leave;UI.buy=null;sfx('ui_tap')}
    else if(a==='hone-strike'||a==='hone-guard'){if(LH.campHone(G,a.slice(5)))sfx('camp_hone')}
    else if(a==='march'){if(LH.nextBattle(G)){UI.sel=UI.fc=UI.look=null;UI.fx=null;UI.ended=false;sfx('your_turn');curtain('march',G.map.name,'Battle '+G.run.n+' of 3',function(){show('map');renderMap()});return}}
    renderCamp();return spent(had-G.run.spoils);
  }
  if(a==='go'&&UI.fc)return startClash(UI.fc.a,UI.fc.d);
  if(a==='no'){UI.fc=null;sfx('ui_tap');return renderMap()}
  if(a==='unmove'&&UI.sel){if(LH.unmove(G,UI.sel))sfx('unit_move');return renderMap()}
  if(a==='wait'&&UI.sel){LH.hold(G,UI.sel);UI.sel=null;sfx('block_gain');return renderMap()}
  if(a==='end')return runEnemy();
  if(a==='endhand')return doEnd();if(a==='redraw')return doRedraw();if(a==='press')return doPress();if(a==='leave')return doLeave();
  if(a==='pile-draw'){sfx('ui_tap');return showPile('draw')}if(a==='pile-disc'){sfx('ui_tap');return showPile('disc')}
});
window.addEventListener('resize',function(){if(G&&G.clash&&$hand&&!$hand.hidden)fan()});

/* playtest settings, outside the screen */
function paintPrefs(){var b=document.querySelectorAll('[data-pref]');for(var i=0;i<b.length;i++){var kv=b[i].getAttribute('data-pref').split('=');b[i].setAttribute('aria-pressed',String(String(prefs[kv[0]])===kv[1]))}
  var tg=document.querySelectorAll('[data-toggle]');for(i=0;i<tg.length;i++){var k=tg[i].getAttribute('data-toggle'),none=k==='music'&&!(AS.music&&AS.music.map);tg[i].setAttribute('aria-pressed',String(!!prefs[k]&&!none));tg[i].disabled=none;tg[i].innerHTML=svg(k==='music'?'note':'speaker')+'<span>'+(k==='music'?'Music ':'Sound ')+(none?'to come':prefs[k]?'on':'off')+'</span>'}}
document.addEventListener('click',function(e){
  if(e.target.closest('[data-newrun]')){if(!busy)newRun();return}
  var tg=e.target.closest('[data-toggle]');if(tg){var tk=tg.getAttribute('data-toggle');prefs[tk]=!prefs[tk];if(tk==='sound'&&prefs.sound)hear('ui_tap');musStarted=true;savePrefs();paintPrefs();music();return}
  var hb=e.target.closest('[data-hear]');if(hb){hear(hb.getAttribute('data-hear'));return}
  var cp=e.target.closest('[data-copy]');if(cp){var src=$(cp.getAttribute('data-copy')),txt=src?src.textContent:'';
    var doneCopy=function(){cp.textContent='Copied';setTimeout(function(){cp.textContent='Copy'},1200)},sel=function(){var r=document.createRange();r.selectNodeContents(src);var s=getSelection();s.removeAllRanges();s.addRange(r);cp.textContent='Selected: copy it'};
    try{navigator.clipboard.writeText(txt).then(doneCopy,sel)}catch(err){sel()}return}
  var b=e.target.closest('[data-pref]');if(!b)return;var kv=b.getAttribute('data-pref').split('=');
  if(kv[0]==='rounds'){prefs.rounds=+kv[1];if(G)G.opts.rounds=prefs.rounds}else if(kv[0]==='quick')prefs.quick=kv[1]==='true';
  else if(kv[0]==='sound'){prefs.sound=kv[1]==='true';if(prefs.sound)hear('your_turn')}
  else if(kv[0]==='music'){prefs.music=kv[1]==='true';musStarted=true}
  else if(kv[0]==='deck'||kv[0]==='level'){if(busy)return;if(kv[0]==='deck')prefs.deck=kv[1];else prefs.level=+kv[1];savePrefs();paintPrefs();newRun();return}
  savePrefs();paintPrefs();music()});
(function(){var l=AS.art.map(function(n){return A+n+'.webp'}).concat(AS.fig.map(function(n){return A+'fig-'+n+'.webp'}),AS.tok.map(function(n){return A+'tok-'+n+'.webp'}));window.__pre=l.map(function(u){var im=new Image();im.src=u;return im})})();
paintPrefs();lock(false);newRun();
window.__LH={LH:LH,get G(){return G},get busy(){return busy},prefs:prefs,heard:heard,played:played,assets:AS,SFX:SFX,get music(){return {want:musWant,playing:musNow(),started:musStarted}}};

/* ---------- lists the page shows: the deck, the camp's cards, the sounds ---------- */
var gal=$('gallery');
if(gal){var g='';LH.BASE_DECK.filter(function(id,i,a){return a.indexOf(id)===i}).forEach(function(id){g+=cardHTML(id)});
  g+='<div class="card t-foot sealed"><span class="cost num">1</span><span class="art"><img src="'+A+'thunderstep.webp" alt=""></span><b>Thunderstep</b><span class="rk">sealed · Footing</span><small>Waits on its Knot.</small></div>';
  ['lH','lH2','lA','lW','lR','lR2'].forEach(function(id){g+=cardHTML(id)});gal.innerHTML=g}
var mk=$('market-gallery');if(mk)mk.innerHTML=LH.POOL.map(function(id){return cardHTML(id,{price:1})}).join('')+cardHTML('strike2')+cardHTML('guard2')+cardHTML('wound');
var st=$('sfx-table');if(st)st.innerHTML=SFX.map(function(s){return '<tr><td><code>'+s[0]+'</code>'+(AS.sfx[s[0]]?' <span class="made">made</span>':'')+'</td><td>'+s[1]+'</td><td>'+s[2]+'</td><td class="num">'+s[3]+' s</td><td><button type="button" class="mini2" data-hear="'+s[0]+'">Hear</button></td></tr>'}).join('');
var gi=document.querySelectorAll('[data-ic]');for(var gk=0;gk<gi.length;gk++)gi[gk].insertAdjacentHTML('afterbegin',svg(gi[gk].getAttribute('data-ic')));
var mu=document.querySelectorAll('[data-music]');for(var mk2=0;mk2<mu.length;mk2++){var mok=AS.music&&AS.music[mu[mk2].getAttribute('data-music')];mu[mk2].insertAdjacentHTML('afterend',' <span class="'+(mok?'made':'todo')+'">'+(mok?'made':'to make')+'</span>')}
var sc=$('sfx-count');if(sc)sc.textContent=SFX.length;
var sm=$('sfx-made');if(sm)sm.textContent=Object.keys(AS.sfx).length;
var who=document.querySelectorAll('[data-who]');for(var wi=0;wi<who.length;wi++){var wk=who[wi].getAttribute('data-who'),f1=has(AS.fig,wk),t1=has(AS.tok,wk);who[wi].insertAdjacentHTML('beforeend',' <span class="'+(f1&&t1?'made':'todo')+'">'+(f1&&t1?'figure and token made':f1?'figure made, token to make':t1?'token made, figure to make':'to make')+'</span>')}
})();
