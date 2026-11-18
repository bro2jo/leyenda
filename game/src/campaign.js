/* The Line and the Hand: the campaign's rules. No drawing, no DOM.
   It changes nothing in engine.js: it wraps the functions LH exports, builds each mission's board on top of a normal battle,
   and decides for itself when a mission is won or lost. A page that does not load this file plays exactly as before.
   The missions themselves (maps, decks, words) are in missions.js. */
(function(root,LH){
'use strict';
var C=LH.C,FOES=LH.FOES,O={},MS={},ORDER=[],CUR=null;
['newRun','move','unmove','hold','tend','engage','play','redraw','endHand','pressOn','leave','closeClash','endTurn','enemyStep','nm','preview','effects','clashEffects','cardText','ansText','playable'].forEach(function(k){O[k]=LH[k]});

/* ---------- cards the campaign adds. Arts carry the rank the page had given them by that chapter. ---------- */
var ROM=['','I','II','III','IV','V'];
function add(id,c){C[id]=c}
function ranks(base,art,name,tree,kind,list){list.forEach(function(v){var c={n:name,r:ROM[v.r],t:tree,k:kind,art:art};for(var k in v)if(k!=='r')c[k]=v[k];add(base+v.r,c)})}
/* what he has before any Art: his own body */
add('c_step',{n:'A Step',t:'foot',k:'Attack',c:1,m:1,dmg:5,art:'darrow1'});
add('c_brace',{n:'Brace',t:'foot',k:'Skill',c:1,blk:5,art:'darrow1'});
add('c_shoulder',{n:'Shoulder',t:'foot',k:'Attack',c:1,m:1,dmg:5,art:'darrow1'});
add('c_word',{n:'A Plain Word',t:'eye',k:'Attack',c:1,m:1,dmg:5,art:'darrow1'});
add('c_stand',{n:'Stand',t:'foot',k:'Skill',c:1,blk:5,art:'darrow1'});
add('c_pull',{n:'Pull',t:'foot',k:'Attack',c:1,m:1,dmg:6,art:'darrow1'});
add('c_slack',{n:'Let It Have the Weight',t:'breath',k:'Skill',c:1,blk:8,art:'long_breath'});
add('c_wood',{n:'Wooden Sword',t:'blade',k:'Attack',c:1,m:1,dmg:5,art:'darrow1'});
add('c_bind',{n:'The Bind',t:'blade',k:'Skill',c:1,blk:4,halve:1,art:'seated_blade'});
add('c_stick',{n:'The Stick',t:'foot',k:'Attack',c:1,m:1,dmg:5,art:'darrow'});
add('c_bar',{n:'The Stick, Barred',t:'foot',k:'Skill',c:1,blk:8,art:'darrow'});
add('c_patience',{n:'Patience',t:'blade',k:'Attack',c:1,m:1,dmg:7,art:'high-guard'});
add('c_guard',{n:'Guard',t:'foot',k:'Skill',c:1,blk:6,art:'darrow'});
ranks('c_still','stillwater','Stillwater Stance','foot','Skill',[{r:1,c:1,blk:7},{r:2,c:1,blk:9},{r:3,c:1,blk:11}]);
ranks('c_mend','menders_patience',"The Mender's Patience",'bind','Skill',[{r:1,c:1,ex:1,heal:4},{r:2,c:1,ex:1,heal:5},{r:3,c:1,ex:1,heal:6,cleanse:1},{r:4,c:1,ex:1,heal:8,cleanse:1}]);
ranks('c_eye','wardens_eye',"Warden's Eye",'eye','Skill',[{r:1,c:0,draw:1},{r:2,c:0,draw:1,open:1},{r:3,c:0,draw:2},{r:4,c:0,draw:2,open:1}]);
ranks('c_breath','long_breath','The Long Breath','breath','Skill',[{r:1,c:0,ex:1,en:1},{r:2,c:0,ex:1,en:2}]);
ranks('c_ground','groundbreaker','Groundbreaker','foot','Attack',[{r:2,c:2,m:1,dmg:8,push:1},{r:3,c:2,m:1,dmg:10,push:1}]);
ranks('c_far','far_cast','The Far Cast','cast','Attack',[{r:1,c:1,dmg:6}]);
ranks('c_seated','seated_blade','The Seated Blade','blade','Attack',[{r:2,c:1,m:1,dmg:6,dmgStood:10}]);
ranks('c_hand','measured_hand','The Measured Hand','cast','Attack',[{r:1,c:0,dmg:3},{r:2,c:0,dmg:4}]);
ranks('c_over','overwall','Overwall','cast','Attack',[{r:1,c:1,dmg:6,pierce:1}]);
/* the Knight Who Fell, with the Grace in him: the Arts that are sealed now */
add('g_thunder',{n:'Thunderstep',r:'the Grace',t:'foot',k:'Attack',c:1,m:1,dmg:12,art:'thunderstep'});
add('g_turning',{n:'The Turning Blade',r:'the Grace',t:'blade',k:'Attack',c:1,m:1,dmg:9,hits:2,art:'high-guard'});
add('g_stoop',{n:"Hawk's Stoop",r:'the Grace',t:'foot',k:'Attack',c:1,m:1,dmg:10,pierce:1,art:'high-guard'});
add('g_anchor',{n:'Anchor',r:'the Grace',t:'foot',k:'Skill',c:1,blk:14,art:'stillwater'});
add('g_quick',{n:'The Quickening',r:'the Grace',t:'eye',k:'Skill',c:0,draw:2,en:1,art:'wardens_eye'});
add('frost',{n:'Frost',t:'bind',k:'Wound',c:0,dead:1});
add('turn',{n:'Turn',t:'foot',k:'Skill',c:0,art:'darrow1'});
/* lent by whoever stands with him. Each needs its risen twin (the engine asks for id+'2' after two fights). */
function lend(id,c,up){c.lent=1;c.c=0;add(id,c);var d={};for(var k in c)d[k]=c[k];for(k in up)d[k]=up[k];d.r='risen';add(id+'2',d)}
lend('c_now',{n:'Maelis: "Now"',t:'bind',k:'Skill',en:1,art:'maelis'},{draw:1});
lend('c_bro',{n:"A Brother's Shoulder",t:'foot',k:'Skill',blk:4,art:'brother'},{blk:6});
lend('c_raesh',{n:"Rae's Shoulder",t:'foot',k:'Attack',dmg:6,art:'rae1'},{dmg:8});
lend('c_lampw',{n:"Wren's Lamp",t:'eye',k:'Skill',draw:1,art:'wren1'},{draw:2});
lend('c_ashdrop',{n:'Ash on the Drop Side',t:'foot',k:'Skill',blk:4,art:'ash1'},{blk:6});
lend('c_lamp',{n:'The Lamp',t:'eye',k:'Skill',halve:1,pin:1,art:'wren'},{});
lend('c_wide',{n:'"Ride Wide"',t:'eye',k:'Skill',blk:6,art:'aldric'},{});
/* words for cards whose effect is the story's, not a number */
var CT={turn:'Plant the left foot and turn on it, fast and low, the way he has ten thousand times.',frost:'The warmth is gone.'};

/* ---------- foes and ordeals. hp, atk and ans here are exactly what the mission plays with (no difficulty scaling). ---------- */
var FD={
  Z:{n:'',key:'zz',t:'foot',hp:1,mov:0,rng:0,atk:0,boss:1,ans:[{b:0,d:0}]},   /* never seen: the engine wants a captain on every board */
  wend:{n:'The Wend',key:'wend',t:'cast',hp:90,mov:0,rng:1,atk:1,ordeal:1,ans:[{b:0,d:6},{b:0,d:8}]},
  hall1:{n:'The Length of the Hall',key:'hall',t:'foot',hp:14,mov:0,rng:1,atk:1,ordeal:1,ans:[{b:0,d:5},{b:0,d:6}]},
  hall2:{n:'Without the Stick',key:'hall',bare:1,t:'foot',hp:18,mov:0,rng:1,atk:1,ordeal:1,ans:[{b:0,d:7},{b:0,d:6}]},
  doorman:{n:'Man at the Wicket',key:'greycloak',t:'blade',hp:24,mov:0,rng:1,atk:5,tough:1,ans:[{b:4,d:7},{b:0,d:9}]},
  seeker:{n:'Grey Cloak',key:'greycloak',t:'blade',hp:20,mov:0,rng:0,atk:1,scripted:1,ans:[{b:0,d:1}]},
  question:{n:'The Question',key:'question',t:'foot',hp:25,mov:0,rng:1,atk:1,ordeal:1,ans:[{b:0,d:10},{b:4,d:12}]},
  sliver:{n:'The Black Glass',key:'sliver',t:'foot',hp:30,mov:0,rng:1,atk:1,ordeal:1,tough:99,ans:[{b:0,d:11},{b:0,d:14},{b:0,d:17}]},
  spar:{n:'Hollis',key:'hollis-foe',t:'blade',hp:46,mov:0,rng:1,atk:8,proper:1,ans:[{b:6,d:12},{b:0,d:16},{b:9,d:11}]},
  guest:{n:"Confessor's Man",key:'guest',t:'blade',hp:18,mov:2,rng:1,atk:5,ans:[{b:3,d:7},{b:0,d:9}]},
  bigman:{n:'Big Man',key:'guest',t:'blade',hp:40,mov:2,rng:1,atk:11,tough:1,ans:[{b:5,d:14},{b:0,d:18}]},
  last:{n:'The Last Hundred',key:'steps',t:'foot',hp:22,mov:0,rng:1,atk:1,ordeal:1,ans:[{b:0,d:11},{b:0,d:13}]},
  reach:{n:'The Long Reach',key:'steps',t:'foot',hp:28,mov:0,rng:1,atk:1,ordeal:1,ans:[{b:0,d:13},{b:0,d:15}]},
  elbow:{n:'The Elbow',key:'steps',t:'foot',hp:24,mov:0,rng:1,atk:1,ordeal:1,ans:[{b:4,d:14},{b:0,d:16}]},
  shins:{n:'The Shins',key:'steps',t:'foot',hp:20,mov:0,rng:1,atk:1,ordeal:1,ans:[{b:0,d:12},{b:0,d:12}]},
  /* for the fights told larger than the page tells them */
  pike:{n:'Levy Pike',key:'pikeman',t:'foot',hp:20,mov:2,rng:1,atk:6,ans:[{b:5,d:8},{b:0,d:11}]},
  pitch:{n:'Boy with a Pitchfork',key:'pitchfork',t:'cast',hp:16,mov:2,rng:2,atk:6,ans:[{b:0,d:7},{b:0,d:9}]},          /* reaches two tiles; Cast, so Hollis is his answer */
  horn:{n:'Boy with the Horn',key:'hornboy',t:'foot',hp:16,mov:2,rng:1,atk:4,rally:1,ans:[{b:3,d:5},{b:4,d:4}]},      /* while he stands, the others strike harder */
  lymer:{n:'Lymer',key:'lymer',t:'cast',hp:18,mov:4,rng:1,atk:7,ans:[{b:0,d:4,n:2},{b:0,d:3,n:3}]},                 /* the grey cloaks' hound: quick, and it bites more than once */
  lister:{n:'Grey Cloak with the List',key:'greycloak',t:'blade',hp:28,mov:2,rng:1,atk:8,rally:1,ans:[{b:4,d:9},{b:0,d:11}]},
  darkmail:{n:'Dark Coat in Mail',key:'darkcoat',t:'foot',hp:34,mov:3,rng:1,atk:10,tough:2,ans:[{b:5,d:10},{b:0,d:13}]},
  darklead:{n:'First Rider',key:'darkcoat',t:'blade',hp:34,mov:4,rng:1,atk:11,rally:1,enrage:3,ans:[{b:0,d:12},{b:6,d:10}]},
  sergeant:{n:'Levy Sergeant',key:'sergeant',t:'blade',hp:38,mov:2,rng:1,atk:9,enrage:3,ans:[{b:6,d:11},{b:0,d:14}]},
  cloak:{n:'Grey Cloak',key:'greycloak',t:'blade',hp:34,mov:3,rng:1,atk:11,ans:[{b:0,d:13},{b:5,d:11}]},
  darkcoat:{n:'Dark Coat',key:'darkcoat',t:'blade',hp:32,mov:4,rng:1,atk:11,ans:[{b:0,d:8,n:2},{b:0,d:6,n:3}]},
  rider:{n:'Outrider',key:'rider',t:'blade',hp:30,mov:0,rng:0,atk:1,scripted:1,ans:[{b:0,d:1}]},
  ysra:{n:'Ysra Tal',key:'ysra-tal',t:'blade',hp:72,mov:3,rng:1,atk:13,proper:1,ans:[{b:0,d:7,n:3},{b:8,d:18},{b:0,d:22}]},
  walker:{n:'Walker',key:'walker',t:'foot',hp:22,mov:1,rng:1,atk:7,barbed:1,ans:[{b:0,d:12},{b:0,d:15}]}
};
FOES.Z=FD.Z;

/* ---------- the fire: camp cards he may carry into the larger fights, paid for in stars ---------- */
var PACK=3,SHOP=LH.POOL.filter(function(id){return !C[id].spoil&&!C[id].spoilKill});

/* ---------- small tools ---------- */
function lcg(seed){var s=(seed|0)||1;return function(n){s=(Math.imul(s,1664525)+1013904223)|0;return ((s>>>8)%n+n)%n}}
function shuffle(a,rn){a=a.slice();for(var i=a.length-1;i>0;i--){var j=rn(i+1),t=a[i];a[i]=a[j];a[j]=t}return a}
function clone(o){return JSON.parse(JSON.stringify(o))}
function U(G,id){for(var i=0;i<G.u.length;i++)if(G.u[i].id===id)return G.u[i];return null}
function up(u){return !!u&&u.hp>0}
function foes(G){return G.u.filter(function(o){return o.side===1&&o.hp>0})}
function mates(G){return G.u.filter(function(o){return o.side===0&&o.hp>0})}
function foe(G,type){return G.u.filter(function(o){return o.side===1&&o.type===type&&o.hp>0})[0]||null}
function on(u,x,y){return !!u&&u.x===x&&u.y===y}
function dist(a,b){return Math.abs(a.x-b.x)+Math.abs(a.y-b.y)}
function log(G,t,c){G.log.push([t,c||'',1]);if(G.log.length>6)G.log.splice(0,G.log.length-6);if(c==='good'||c==='hurt')toast(G,t,c)}
/* said aloud over the board: a beat of the story as it happens, someone new beside him */
function toast(G,t,kind,img){if(G.cs&&G.cs.toasts)G.cs.toasts.push({t:t,k:kind||'',img:img||''})}
/* a rule, the first time it matters. The screen shows each once, ever, and keeps them to read again. */
var TIPS={
  brk:['Broken','His tree beats theirs. Land one hit and the answer this hand is halved.'],
  lent:['A lent card','Whoever stands beside him lends a card. It costs nothing, and it is gone when the fight ends.'],
  far:['From two tiles','Only thrown cards reach from here, on one less breath. Most foes cannot answer at all.'],
  guard:['Guard','Block he did not need stays as guard through their turn. Guard that holds a blow whole strikes back.'],
  held:['Held breath','Breath he did not spend is held, up to 2, for his next hand.'],
  wound:['A Wound','A dead card in the hand until the battle ends. The Mender\'s Patience, or a tending hand, sets one aside.'],
  tough:['Tough','Every blow on this one lands for less. One big blow beats two small ones.'],
  flurry:['Several blows','The answer comes as several small blows. Block soaks each in turn.'],
  rally:['The others strike harder','While this one stands, every other foe strikes harder. Send this one off first.'],
  enrage:['Half health','At half health this one strikes harder. Finish it quickly, or block.'],
  ordeal:['Not a man','A river, a stair, the cold: what he deals is ground covered, and its answer is what it costs him.'],
  rounds:['Press on, or break off','After the answer he may press on for another round, a little dearer each time, or break off with what he has.'],
  cover:['Cover','Whoever stands in cover takes less on their turn, and a foe in cover starts with block.'],
  rise:['Risen','After two fights a friend\'s lent card comes back stronger.']
};
function tip(G,id){if(G.cs&&G.cs.tips&&TIPS[id]&&G.cs.tips.indexOf(id)<0)G.cs.tips.push(id)}
function tipsFor(G,K){
  var d=K.d;if(K.canBreak)tip(G,'brk');if(K.p&&K.p.lend&&K.p.lend.length){tip(G,'lent');if(K.hand.some(function(c){return C[c]&&C[c].r==='risen'}))tip(G,'rise')}if(K.p&&K.p.far)tip(G,'far');if(K.p&&K.p.wood)tip(G,'cover');
  if(d.ordeal)tip(G,'ordeal');else{if(d.tough)tip(G,'tough');if(d.ans.some(function(x){return x.n>1}))tip(G,'flurry');if(d.rally)tip(G,'rally');if(d.enrage)tip(G,'enrage')}
}
function hint(G,t){G.cs.hint=t||''}
/* a pile set by hand: these ids are drawn first, in this order; the rest of the deck is shuffled under them */
function stack(G,u,ids){var rest=u.deck.slice(),rn=lcg(G.seed^0x5bd1);ids.forEach(function(id){var j=rest.indexOf(id);if(j>=0)rest.splice(j,1)});u.dk={draw:shuffle(rest,rn).concat(ids.slice().reverse()),disc:[],gone:[]}}
/* one step toward a tile, round the walls and round whoever stands in the way; false when there is no way */
function stepToward(G,u,gx,gy){
  var seen={},q=[[gx,gy,0]];seen[gx+','+gy]=0;
  while(q.length){var c=q.shift();[[1,0],[-1,0],[0,1],[0,-1]].forEach(function(d){var x=c[0]+d[0],y=c[1]+d[1],k=x+','+y;if(!LH.ok(G,x,y)||seen[k]!==undefined)return;var w=LH.at(G,x,y);if(w&&w!==u)return;seen[k]=c[2]+1;q.push([x,y,c[2]+1])})}
  var here=seen[u.x+','+u.y];if(here===undefined||here===0)return false;
  var best=null;[[1,0],[-1,0],[0,1],[0,-1]].forEach(function(d){var x=u.x+d[0],y=u.y+d[1],k=x+','+y;if(seen[k]!==undefined&&seen[k]<here&&!LH.at(G,x,y)&&(!best||seen[k]<best[2]))best=[x,y,seen[k]]});
  if(!best)return false;u.x=best[0];u.y=best[1];return true;
}
function spawn(G,type,x,y,over){
  if(!G.tpl[type]||LH.at(G,x,y))return null;var o=clone(G.tpl[type]);G.cs.n=(G.cs.n||0)+1;o.id=type+'_s'+G.cs.n;o.x=x;o.y=y;o.hp=o.max;if(over)for(var k in over)o[k]=over[k];G.u.push(o);return o;
}
var api={U:U,up:up,foes:foes,mates:mates,foe:foe,on:on,dist:dist,log:log,hint:hint,toast:toast,tip:tip,stack:stack,stepToward:stepToward,spawn:spawn};

/* ---------- a mission's board, built on a normal battle ---------- */
function setDeck(G,u,deck,first){u.deck=deck.slice();if(first)stack(G,u,first);else u.dk={draw:shuffle(u.deck,lcg(G.seed^(u.id.charCodeAt(0)*7919))),disc:[],gone:[]}}
function dress(G,u,p){
  for(var k in p)if(k!=='at'&&k!=='deck'&&k!=='first'&&k!=='from'&&k!=='hp')u[k]=p[k];
  if(p.hp){u.hp=u.max=p.hp}
  if(p.deck)setDeck(G,u,p.deck,p.first);else if(p.deck===null){delete u.deck;delete u.dk;u.hn=0;u.br=0}
  if(p.at){u.x=p.at[0];u.y=p.at[1]}
  if(p.still){u.mov=0;u.rng=0;u.throws=0;u.tend=0;u.tends=0}
}
function start(id,opts){
  var M=MS[id];if(!M)throw new Error('no such mission: '+id);opts=opts||{};
  var lvl=opts.level!==undefined?opts.level:(CP.level||0),pack=M.tall?(opts.pack||CP.pack||[]).filter(function(c){return SHOP.indexOf(c)>=0}).slice(0,PACK):[];
  var pos={},keys=[],fl=[['Z',0,0]];['D','H','A','W','R'].forEach(function(k){pos[k]=(M.party[k]&&M.party[k].at)||[0,0]});
  (M.foes||[]).forEach(function(f,i){var key=f.k+'_'+i;FOES[key]=FD[f.k];keys.push(key);fl.push([key,f.at?f.at[0]:0,f.at?f.at[1]:0])});
  var keep=LH.MAPS[0],G;LH.MAPS[0]={name:M.map.name,rows:M.map.rows,pos:pos,foes:fl};
  try{G=O.newRun({seed:opts.seed,rounds:M.rounds||1,level:0,deck:['c_brace']})}finally{LH.MAPS[0]=keep;keys.forEach(function(k){delete FOES[k]})}
  G.ms=id;G.cs={hint:'',turnsHeld:0,clashes:0,hurt:0,result:null,level:lvl,pack:pack,toasts:[],tips:[]};G.tpl={};G.run.insp=M.insp||0;G.run.spoils=0;
  /* the marker captain: off the board, on nobody's side */
  var z=U(G,'Z');z.side=2;z.x=-9;z.y=-9;
  /* the foes, with the mission's own numbers */
  var gone=[];
  (M.foes||[]).forEach(function(f,i){var u=U(G,f.k+'_'+i),d=FD[f.k];u.type=f.k;u.hp=u.max=d.hp;u.atk=d.atk;u.ans=d.ans.map(function(x){return {b:x.b||0,d:x.d,n:x.n||1}});
    for(var k in f)if(k!=='k'&&k!=='at'&&k!=='tpl')u[k]=f[k];if(f.hp)u.max=f.hp;
    if(lvl&&!d.scripted){u.ans.forEach(function(x){x.d=Math.max(1,x.d+(x.n>1?1:2)*lvl)});if(!d.ordeal){u.atk=Math.max(1,u.atk+2*lvl);u.hp=u.max=Math.max(1,Math.round(u.max*(1+.1*lvl)))}}
    if(f.tpl){G.tpl[f.k]=clone(u);gone.push(u)}});
  /* the company: who is here, and what each can do in this chapter */
  var tplR=clone(U(G,'R')),tplW=clone(U(G,'W'));
  ['D','H','A','W','R'].forEach(function(k){var u=U(G,k);if(!M.party[k]){if(k!=='D')gone.push(u);return}dress(G,u,M.party[k])});
  (M.party.more||[]).forEach(function(p){var u=clone(p.from==='R'?tplR:tplW);u.id=p.id;u.fights=0;u.guard=0;u.bank=0;dress(G,u,p);G.u.splice(G.u.indexOf(z),0,u)});
  G.u=G.u.filter(function(u){return gone.indexOf(u)<0});
  if(!M.party.D.hp)G.u[0].hp=G.u[0].max;
  /* what he bought at the fire goes with him into the fights told larger than the page, and nowhere else */
  if(pack.length)setDeck(G,G.u[0],G.u[0].deck.concat(pack),M.party.D.first);
  G.log=[[M.open||'','',1]];CUR=G;
  if(M.on&&M.on.start)M.on.start(G,G.cs,api);
  rest(G);relog(G);return G;
}

/* ---------- what is said: the engine's sentences, turned to fit who or what is on the board ---------- */
var PRO={she:[[/\bHe\b/g,'She'],[/\bhe\b/g,'she'],[/\bHis\b/g,'Her'],[/\bhis\b/g,'her'],[/\bhim\b/g,'her']],
  it:[[/\bHe\b/g,'It'],[/\bhe\b/g,'it'],[/\bHis\b/g,'Its'],[/\bhis\b/g,'its'],[/\bhim\b/g,'it'],[/ · strikes for \d+ on its turn\./g,'.']],
  they:[[/\bHe is\b/g,'They are'],[/\bHe has\b/g,'They have'],[/\bHe (strikes|braces|cannot|will)\b/g,'They $1'],[/\bHe\b/g,'They'],[/\bhe\b/g,'they'],[/\bHis\b/g,'Their'],[/\bhis\b/g,'their'],[/\bhim\b/g,'them']]};
/* cover is whatever the place has: the engine calls it the wood */
var COVER={yard:'in the hay',road:'behind the wall',court:'in the drifted snow',hall:'behind a cot',under:'behind a pillar',tower:'on the stair',steps:'against the cliff'};
var RULES={};
function rules(M){
  if(RULES[M.id])return RULES[M.id];var r=[];
  Object.keys(FD).forEach(function(k){var d=FD[k];if(d.n&&(d.proper||d.bare||/^The /.test(d.n))){var nm=d.n.replace(/^The /,'');r.push([new RegExp('\\b[Tt]he (The )?'+nm.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+'\\b','g'),function(m){return (d.proper||d.bare?'':(m.charAt(0)==='T'?'The ':'the '))+nm}])}});
  var cv=COVER[M.map.theme];if(cv)r.push([/\b([Ii])n the wood\b/g,function(m,i){return (i==='I'?cv.charAt(0).toUpperCase():cv.charAt(0))+cv.slice(1)}]);
  (PRO[M.pro]||[]).forEach(function(p){r.push(p)});
  (M.say||[]).forEach(function(p){r.push(p)});
  r.push([/^Their turn(\.?)$/,function(m,d){return (M.their||(M.pro==='it'?'Time passes':'Their turn'))+d}]);
  if(M.pro==='it')r.push([/^They move$/,'Nothing here waits for him']);
  if(M.rally)r.push([/\bThe banner is up\b/g,M.rally[1]],[/^Banner$/,M.rally[0]]);
  r.push([/A man down\. /g,''],[/ is down\./g,' '+(M.down||'gives way')+'.'],[/They hold where they stand\./g,M.idle||''],[/The run ends here\.?/g,''],[/Three crossings, three captains/g,'']);
  r.push([/\bwill (strike|brace|pull|wear|press|tell|climb)s\b/g,'will $1']);
  return RULES[M.id]=r;
}
function say(G,s){if(typeof s!=='string'||!s||!G||!G.ms)return s;rules(MS[G.ms]).forEach(function(p){s=s.replace(p[0],p[1])});return s}
function relog(G){G.log=G.log.map(function(l){return l[2]?l:[say(G,l[0]),l[1],1]}).filter(function(l){return l[0]})}
LH.nm=function(u,cap){var s=O.nm(u,cap);return CUR&&CUR.ms?say(CUR,s):s};
LH.ansText=function(a){var s=O.ansText(a);return CUR&&CUR.ms?say(CUR,s):s};
LH.cardText=function(id,K){if(CT[id])return CT[id];var s=O.cardText(id,K);return CUR&&CUR.ms?say(CUR,s):s};
LH.playable=function(G,i){return say(G,O.playable(G,i))};
LH.preview=function(G,a,d){var p=O.preview(G,a,d);if(G.ms){p.txt=say(G,p.txt);p.chips=p.chips.map(function(c){return [say(G,c[0]),c[1]]})}return p};
function sayFx(G,l){return l.map(function(e){e.label=say(G,e.label);e.text=say(G,e.text);return e})}
LH.effects=function(G,u){if(u.side===2)return [];var l=O.effects(G,u);return G.ms?sayFx(G,l):l};
LH.clashEffects=function(G){var f=O.clashEffects(G);if(G.ms){f.a=sayFx(G,f.a);f.d=sayFx(G,f.d)}return f};

/* ---------- winning and losing: the mission's own ---------- */
function ev(G,name,a,b){var M=MS[G.ms];if(M.on&&M.on[name])return M.on[name](G,G.cs,api,a,b)}
function finish(G,res,why){
  var M=MS[G.ms],S=G.cs;if(S.result)return;S.result=res;S.why=why||'';
  var t=res==='won'?(typeof M.win==='function'?M.win(G,S):M.win):((M.lose&&M.lose[why])||(M.lose&&M.lose.any)||{t:'Not this time',s:''});
  S.stars=(M.stars?M.stars(G,S,api):[]).map(function(s){return [s[0],res==='won'&&!!s[1]]});
  G.over=(res==='won'&&!t.somber)?{done:1,cp:1,t:t.t,s:t.s}:{lost:1,cp:1,t:t.t,s:t.s};
  G.run.renown=0;
}
function check(G){
  var M=MS[G.ms],S=G.cs;if(S.result)return;
  if(G.over){var r=M.fallen?M.fallen(G,S,api):'lost';return finish(G,r==='won'?'won':'lost',G.over.night?'night':'down')}
  if(G.clash)return;
  var f=M.fail&&M.fail(G,S,api);if(f)return finish(G,'lost',f);
  if(M.goal&&M.goal(G,S,api))return finish(G,'won');
}
/* someone who is only there to be seen (a watcher on the bank, a man on his cot) never has a turn to take */
function rest(G){G.u.forEach(function(u){if(u.still&&u.side===0){u.attacked=true;u.moved=true;u.free=false}})}
function after(G){CUR=G;relog(G);check(G)}

/* ---------- the wrapped moves. Each does what the engine does, then lets the mission look at the board. ---------- */
/* the game's own settings (its difficulty, its try-everything deck) are for a run of the game: a mission takes only the seed */
LH.newRun=function(opts){if(CP.pending){var id=CP.pending;CP.pending=null;return start(id,{seed:opts&&opts.seed})}return O.newRun(opts)};
LH.move=function(G,u,x,y){var r=O.move(G,u,x,y);if(r&&G.ms){ev(G,'moved',u);after(G)}return r};
LH.hold=function(G,u){var r=O.hold(G,u);if(r&&G.ms){ev(G,'held',u);after(G)}return r};
LH.tend=function(G,u,t){var r=O.tend(G,u,t);if(r&&G.ms)after(G);return r};
LH.engage=function(G,a,d){if(!G.ms)return O.engage(G,a,d);CUR=G;ev(G,'before',a,d);var K=O.engage(G,a,d);if(K){G.cs.clashes++;K.p.txt=say(G,K.p.txt);tipsFor(G,K);ev(G,'engage',K)}return K};
LH.play=function(G,i){var id=G.ms&&G.clash?G.clash.hand[i]:null,fx=O.play(G,i);if(fx&&G.ms){var x=ev(G,'play',id,fx);if(x)x.forEach(function(e){fx.push(e)})}return fx};
LH.endHand=function(G){if(G.ms&&G.clash&&G.clash.phase==='play')ev(G,'ending',G.clash);var K=G.clash,fx=O.endHand(G);if(fx&&G.ms){if(fx[0]&&fx[0].n)G.cs.hurt+=fx[0].n;if(fx.some(function(e){return e.k==='wound'}))tip(G,'wound');if(K&&K.phase==='choice')tip(G,'rounds');ev(G,'ended',K,fx)}return fx};
LH.pressOn=function(G){var r=O.pressOn(G);if(r&&G.ms)ev(G,'round',G.clash);return r};
LH.closeClash=function(G){var K=G.clash,r=O.closeClash(G);if(r&&G.ms){if(K.a.hp>0&&K.a.guard>0)tip(G,'guard');if(K.a.hp>0&&K.a.bank>0)tip(G,'held');ev(G,'clashEnd',K);after(G)}return r};
LH.endTurn=function(G){
  if(G.ms&&!G.over&&!G.clash&&G.phase==='player'){ev(G,'night');after(G);if(G.over)return false;
    foes(G).forEach(function(e){if(e.ordeal){e._r=e.rng;e.rng=0}})}   /* an ordeal answers in the clash and nowhere else */
  return O.endTurn(G);
};
LH.enemyStep=function(G){
  var e=O.enemyStep(G);
  if(e&&G.ms){if(e.k==='turn'){G.u.forEach(function(u){if(u._r!==undefined){u.rng=u._r;delete u._r}});if(!G.over)ev(G,'turn',G.turn);rest(G)}after(G)}
  return e;
};

/* ---------- what is new in a mission: worked out from the missions themselves, so it cannot drift from them ---------- */
var PROF={};
function rk(id){return Math.max(0,ROM.indexOf(C[id].r||''))}
function profile(id){
  if(PROF[id])return PROF[id];var keep=CUR,G=start(id,{seed:1,level:0,pack:[]});CUR=keep;
  var D=G.u[0],M=MS[id],p={all:{},here:{},fights:{},tends:{},lends:{},img:{},cards:{},foes:{},mov:D.mov,br:D.br,hn:D.hn,hp:D.max,rounds:M.rounds||1,insp:M.insp||0,thr:(D.throws>0&&D.far)?1:0,tall:!!M.tall};
  G.u.forEach(function(u){
    if(u.side===0&&u.id!=='D'&&u.hp>0){p.all[u.n]=1;p.img[u.n]=u.img;if(u.lend)p.lends[u.n]=u.lend;if(!u.still){p.here[u.n]=1;if(u.deck&&u.deck.length)p.fights[u.n]=1;if(u.tend&&u.tends>0)p.tends[u.n]=1}}
    if(u.side===1&&u.hp>0&&u.n&&!p.foes[u.type])p.foes[u.type]=u});
  for(var t in G.tpl)if(!p.foes[t])p.foes[t]=G.tpl[t];
  (D.deck||[]).forEach(function(c){p.cards[C[c].n]=c});
  return PROF[id]=p;
}
function habit(u){
  if(u.ordeal)return 'not a man: what he deals is ground covered, and its answer is what it costs him';
  var h=[];if(u.rng>1)h.push('reaches two tiles');if(u.tough)h.push('takes less from every blow');if(u.ans&&u.ans.some(function(x){return x.n>1}))h.push('answers with several small blows');
  if(u.barbed)h.push('leaves a Wound where a blow lands');if(u.rally)h.push('makes the others strike harder');if(u.enrage)h.push('strikes harder at half health');if(u.scripted)h.push('does not fight: walks for what was sent for');
  return h.join(', ');
}
function news(id){
  var i=ORDER.indexOf(id),out=[];if(i<=0)return out;
  var P=profile(id),prev=profile(ORDER[i-1]),S={all:{},here:{},fights:{},tends:{},cards:{},foes:{},rounds:1,insp:0,thr:0,tall:0,ordeal:0},n,j;
  for(j=0;j<i;j++){var q=profile(ORDER[j]);['all','here','fights','tends','foes'].forEach(function(k){for(var x in q[k])S[k][x]=1});
    for(n in q.cards)S.cards[n]=Math.max(S.cards[n]||0,rk(q.cards[n])+1);for(n in q.foes)if(q.foes[n].ordeal)S.ordeal=1;
    S.rounds=Math.max(S.rounds,q.rounds);S.insp=Math.max(S.insp,q.insp);S.thr=Math.max(S.thr,q.thr);S.tall=Math.max(S.tall,q.tall?1:0)}
  /* who is beside him */
  for(n in P.here){var f=P.fights[n],t=P.tends[n];
    if(!S.here[n])out.push({k:'join',who:n,img:P.img[n],t:n+(S.all[n]?' stands with him now.':' is with him here for the first time.')+(f?' '+n+' fights with a hand of cards: tap to choose who goes in.':t?' '+n+' tends: tap, then a hurt friend alongside.':'')});
    else if(f&&!S.fights[n])out.push({k:'join',who:n,img:P.img[n],t:n+' fights beside him now, with a hand of cards.'});
    else if(t&&!S.tends[n])out.push({k:'join',who:n,img:P.img[n],t:n+' can tend now: tap, then a hurt friend alongside.'})}
  /* what he carries */
  var lost=0;for(n in prev.cards)if(!P.cards[n]&&C[prev.cards[n]].r==='the Grace')lost++;
  if(lost)out.push({k:'lost',t:'The Grace is gone, and the Arts that stood on it are sealed.'});
  for(n in P.cards){var c=P.cards[n],r=rk(c);
    if(!S.cards[n])out.push({k:'card',id:c,t:(C[c].r?'A new Art: ':'A new card: ')+n+(C[c].r?' '+C[c].r:'')+'.'});
    else if(r+1>S.cards[n])out.push({k:'card',id:c,t:n+' has risen to '+C[c].r+'.'})}
  /* his body */
  var b=[];if(P.mov!==prev.mov)b.push(P.mov===0?'he cannot move':'he moves '+P.mov+(P.mov===1?' step':' steps')+' a turn');
  if(P.hp!==prev.hp&&P.hp>0&&prev.hp>0)b.push('health '+P.hp+' (it was '+prev.hp+')');if(P.br!==prev.br&&P.br>0&&prev.br>0)b.push(P.br+' breath a hand (it was '+prev.br+')');if(P.hn!==prev.hn&&P.hn>0&&prev.hn>0)b.push('a hand of '+P.hn);
  if(b.length){var bs=b.join(', ');out.push({k:'body',t:bs.charAt(0).toUpperCase()+bs.slice(1)+'.'})}
  /* rules that begin here */
  if(P.rounds>1&&S.rounds<2)out.push({k:'rule',t:TIPS.rounds[1]});
  if(P.insp&&!S.insp)out.push({k:'rule',t:'Inspiration: once a fight he may throw in the hand for a new one.'});
  if(P.thr&&!S.thr)out.push({k:'rule',t:'Once a battle he can open a fight from two tiles, with a thrown card.'});
  if(P.tall&&!S.tall)out.push({k:'rule',t:'A fight told larger than the page: the pack from the fire goes with him.'});
  /* what he meets */
  for(n in P.foes){var u=P.foes[n],h=habit(u);if(S.foes[n]||!h)continue;if(u.ordeal&&S.ordeal){continue}out.push({k:'foe',key:u.key,t:u.n+': '+h+'.'})}
  return out;
}
/* ---------- the fire's shelf fills as he goes: each mission told leaves one card the company can spare, and stars open the last two ---------- */
var GIFT={p0:'bandage',p1:'stitch',c1:'closeup',c2:'readline',c3:'bellow',c4a:'hewT',c4b:'callco',c4c:'secondwind',c5:'legs',c5b:'twice',c5c:'pinshot',c6:'finish',c6b:'follow',c7:'digin'},STARGIFT=[[24,'bloodup'],[32,'steady']];
function shelf(done){var out=[],stars=0;ORDER.forEach(function(id){if(done&&done[id]){stars+=done[id].stars||0;if(GIFT[id]&&SHOP.indexOf(GIFT[id])>=0)out.push(GIFT[id])}});
  STARGIFT.forEach(function(g){if(stars>=g[0]&&SHOP.indexOf(g[1])>=0)out.push(g[1])});return out}

/* ---------- what the screen asks ---------- */
function progress(){try{return JSON.parse(root.localStorage.getItem('lh-campaign')||'{}')}catch(e){return {}}}
var CP={pending:null,pack:[],level:0,PACK:PACK,SHOP:SHOP,TIPS:TIPS,GIFT:GIFT,STARGIFT:STARGIFT,shelf:shelf,news:news,profile:profile,habit:habit,MS:MS,ORDER:ORDER,FD:FD,api:api,start:start,say:say,check:check,
  add:function(M){MS[M.id]=M;ORDER.push(M.id)},
  mission:function(G){return G&&G.ms?MS[G.ms]:null},
  objective:function(G){var M=MS[G.ms];return typeof M.objective==='function'?M.objective(G,G.cs,api):M.objective},
  top:function(G){var M=MS[G.ms];return M.top?M.top(G,G.cs,api):'Turn '+G.turn},
  goals:function(G){var M=MS[G.ms];return M.marks?M.marks(G,G.cs,api):[]},
  progress:progress};
root.CP=CP;
})(typeof module!=='undefined'&&module.exports?module.exports:window,typeof module!=='undefined'&&module.exports?require('./engine.js').LH:window.LH);
