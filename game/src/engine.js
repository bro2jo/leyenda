/* The Line and the Hand: the rules. No drawing, no timers, no DOM. Every function takes the game G. */
(function(root){
'use strict';
var W=6,H=7,HAND_CAP=8,MAX_HP=58,HELD_MAX=2,MIN_DECK=10;
/* Balance knobs, in one place. */
/* atkBy, hpBy: how much harder the foes of the second and third battle are than the first. */
var T={atkBy:[0,1,1],hpBy:[0,.1,.2],rest:8,par:10,maxTurns:30,mend:15,mendCost:3,removeCost:2,honeCost:3,spoilFoe:1,spoilBoss:4,spoilOwn:1,market:5,foeAtk:-2,ansD:2,capHolds:3,pressUp:4,pressBreath:1,rally:2,woodBlock:4,woodCover:3,tend:5,tends:3,capPatience:8,levelAtk:1,levelHp:.1,throws:1};
/* What the game takes from the sheet as it stands. The Tether's stage sets what Rae's hand gives. */
var SHEET={hp:58,tether:2};
var TREE={blade:'Blade',foot:'Footing',cast:'Cast',breath:'Breath',bind:'Binding',eye:'Insight'};
var BEAT={foot:'blade',blade:'cast',cast:'foot'};
/* Three grounds. . grass  w wood (2 steps, cover)  d road  ~ deep water  f ford (2 steps)  b bridge */
var MAPS=[
  {name:'The Two Fords',rows:['.wd...','..d.w.','w.d...','~~f~f~','.wd...','..d.w.','..d...'],pos:{D:[2,4],H:[4,4],A:[1,5],W:[3,5],R:[4,6]},foes:[['P',2,2],['S',4,2],['X',3,1],['C',2,0]]},
  {name:'The Wood Road',rows:['w.d.w.','.wd...','..d.ww','w.d...','..dw..','.wd...','..d...'],pos:{D:[2,5],H:[3,5],A:[1,6],W:[3,6],R:[4,6]},foes:[['C',2,0],['B',2,2],['X',4,1],['K',0,2],['J',5,3]]},
  {name:'The Bridge',rows:['..d.w.','.wd...','..d..w','~~b~f~','.wd...','..d.w.','..d...'],pos:{D:[2,4],H:[3,4],A:[1,5],W:[3,5],R:[2,6]},foes:[['C',2,0],['F',3,1],['B',2,2],['P',4,2],['X',1,1]]}];
/* Foes. ans: what he does when your hand ends, in turn (b block first, d strike, n times).
   Traits: tough (each hit on him deals that much less) · barbed (a strike that gets through leaves a Wound) · rally (while he stands the others strike harder) · enrage (at half health he strikes harder) */
var FOES={
  P:{n:'Pikeman',key:'pikeman',t:'foot',hp:26,mov:2,rng:1,atk:9,ans:[{b:6,d:9},{b:0,d:12}]},
  S:{n:'Swordsman',key:'swordsman',t:'blade',hp:24,mov:3,rng:1,atk:8,ans:[{b:0,d:10},{b:4,d:8}]},
  X:{n:'Crossbowman',key:'crossbowman',t:'cast',hp:20,mov:2,rng:2,atk:7,barbed:1,ans:[{b:0,d:9},{b:3,d:7}]},
  K:{n:'Skirmisher',key:'skirmisher',t:'blade',hp:20,mov:4,rng:1,atk:8,ans:[{b:0,d:5,n:2},{b:0,d:4,n:3}]},
  B:{n:'Shieldbearer',key:'shieldbearer',t:'foot',hp:28,mov:2,rng:1,atk:8,tough:2,ans:[{b:6,d:8},{b:3,d:10}]},
  F:{n:'Bannerman',key:'bannerman',t:'cast',hp:22,mov:2,rng:1,atk:5,rally:1,ans:[{b:4,d:5},{b:6,d:4}]},
  C:{n:'Captain',key:'captain',t:'blade',hp:44,mov:2,rng:1,atk:12,boss:1,enrage:3,ans:[{b:8,d:12},{b:0,d:16}]}
};
FOES.J=FOES.K;
var BASE_DECK=['strike','strike','strike','guard','guard','seated','hammer','still','breath','mender','eye','ground','road','hand','over','far'];
/* A card is data: what it says is generated from what it does (cardText), so the two cannot drift apart.
   k kind · c breath cost · p price in spoils at camp · m melee (not from two tiles) · ex once a battle · lent gone after the clash */
var C={
  /* Darrow's own: the sheet */
  strike:{n:'Strike',t:'blade',k:'Attack',c:1,m:1,dmg:7,hone:'strike2'},
  guard:{n:'Guard',t:'foot',k:'Skill',c:1,blk:6,hone:'guard2'},
  strike2:{n:'Strike',r:'honed',t:'blade',k:'Attack',c:1,m:1,dmg:10},
  guard2:{n:'Guard',r:'honed',t:'foot',k:'Skill',c:1,blk:9},
  seated:{n:'The Seated Blade',r:'II',t:'blade',k:'Attack',c:1,m:1,dmg:6,dmgStood:10,art:'seated_blade'},
  hammer:{n:'Hammerfall',r:'I',t:'blade',k:'Attack',c:2,m:1,ex:1,dmg:12,pin:1,art:'hammerfall'},
  still:{n:'Stillwater Stance',r:'III',t:'foot',k:'Skill',c:1,blk:11,art:'stillwater'},
  breath:{n:'The Long Breath',r:'II',t:'breath',k:'Skill',c:0,ex:1,en:2,art:'long_breath'},
  mender:{n:"The Mender's Patience",r:'IV',t:'bind',k:'Skill',c:1,ex:1,heal:8,cleanse:1,art:'menders_patience'},
  eye:{n:"Warden's Eye",r:'IV',t:'eye',k:'Skill',c:0,draw:2,art:'wardens_eye'},
  ground:{n:'Groundbreaker',r:'III',t:'foot',k:'Attack',c:2,m:1,dmg:10,push:1,art:'groundbreaker'},
  road:{n:'The Long Road',r:'I',t:'breath',k:'Skill',c:0,draw:1,again:1},
  hand:{n:'The Measured Hand',r:'II',t:'cast',k:'Attack',c:0,dmg:4,art:'measured_hand'},
  over:{n:'Overwall',r:'I',t:'cast',k:'Attack',c:1,dmg:6,pierce:1,art:'overwall'},
  far:{n:'The Far Cast',r:'I',t:'cast',k:'Attack',c:1,dmg:6,art:'far_cast'},
  /* the company's own decks, and what the camp sells */
  hew:{n:'Hew',t:'blade',k:'Attack',c:1,m:1,dmg:8,p:3},
  fast:{n:'Stand Fast',t:'foot',k:'Skill',c:1,blk:8},
  bellow:{n:'Bellow',t:'eye',k:'Skill',c:0,halve:1,p:3},
  legs:{n:'Take the Legs',t:'foot',k:'Attack',c:1,m:1,dmg:6,pin:1,p:3},
  worry:{n:'Worry',t:'foot',k:'Attack',c:1,m:1,dmg:4,open:1,p:2},
  slip:{n:'Slip Away',t:'foot',k:'Skill',c:0,blk:4},
  stone:{n:'Thrown Stone',t:'cast',k:'Attack',c:1,dmg:5,p:2},
  count:{n:'The Count',t:'eye',k:'Skill',c:0,mark:1,p:2},
  duck:{n:'Duck',t:'foot',k:'Skill',c:0,blk:5},
  stitch:{n:"Maelis's Stitch",t:'bind',k:'Skill',c:1,ex:1,heal:6,p:3,art:'maelis'},
  twice:{n:'Second Cut',t:'blade',k:'Attack',c:1,m:1,dmg:4,hits:2,p:3},
  finish:{n:'Finish It',t:'blade',k:'Attack',c:1,m:1,dmg:5,dmgLow:12,p:4},
  follow:{n:'Follow Through',t:'blade',k:'Attack',c:2,m:1,dmg:11,carry:1,p:4},
  closeup:{n:'Close Up',t:'foot',k:'Skill',c:1,blk:5,guardFriends:4,p:3},
  callco:{n:'Call the Company',t:'eye',k:'Attack',c:1,assist:4,p:4},
  strip:{n:'Strip the Fallen',t:'blade',k:'Attack',c:1,m:1,dmg:6,spoilKill:2,p:3},
  spoils:{n:'Spoils of the Road',t:'breath',k:'Skill',c:0,ex:1,spoil:2,p:3},
  secondwind:{n:'Second Wind',t:'breath',k:'Skill',c:0,en:1,draw:1,p:4},
  readline:{n:'Read the Line',t:'eye',k:'Skill',c:0,draw:1,drawOpen:2,p:2},
  bandage:{n:'Clean Bandage',t:'bind',k:'Skill',c:1,cleanse:1,heal:4,p:2},
  pinshot:{n:'Pinning Throw',t:'cast',k:'Attack',c:1,dmg:3,pin:1,p:3},
  digin:{n:'Dig In',t:'foot',k:'Stance',c:1,ex:1,stance:'blockStart',sv:3,p:4},
  bloodup:{n:'Blood Up',t:'blade',k:'Stance',c:2,ex:1,stance:'atkUp',sv:2,p:5},
  steady:{n:'Steady Hand',t:'eye',k:'Stance',c:1,ex:1,stance:'drawUp',sv:1,p:5},
  wound:{n:'Wound',t:'bind',k:'Wound',c:0,dead:1},
  /* lent by a friend placed to help */
  lH:{n:"Hollis's Shoulder",t:'foot',k:'Skill',c:0,lent:1,blk:5,art:'hollis'},
  lA:{n:'Ash at Heel',t:'foot',k:'Attack',c:0,lent:1,dmg:4,art:'ash'},
  lW:{n:"Wren's Count",t:'eye',k:'Skill',c:0,lent:1,open:1,art:'wren'},
  lD:{n:"Captain's Word",t:'eye',k:'Skill',c:0,lent:1,en:1,art:'darrow'},
  lH2:{n:"Hollis's Shoulder",r:'risen',t:'foot',k:'Skill',c:0,lent:1,blk:9,art:'hollis'},
  lA2:{n:'Ash at Heel',r:'risen',t:'foot',k:'Attack',c:0,lent:1,dmg:7,art:'ash'},
  lW2:{n:"Wren's Count",r:'risen',t:'eye',k:'Skill',c:0,lent:1,open:1,draw:1,art:'wren'},
  lD2:{n:"Captain's Word",r:'risen',t:'eye',k:'Skill',c:0,lent:1,en:1,draw:1,art:'darrow'},
  lR:{n:"Rae's Hand",t:'bind',k:'Skill',c:0,lent:1,heal:2*SHEET.tether,art:'rae'},
  lR2:{n:"Rae's Hand",r:'risen',t:'bind',k:'Skill',c:0,lent:1,heal:2*SHEET.tether+3,cleanse:1,art:'rae'}
};
var POOL=Object.keys(C).filter(function(id){return C[id].p});
var STANCE={blockStart:['Dig In','Starts every clash with %n block.'],atkUp:['Blood Up','Every hit he lands deals %n more.'],drawUp:['Steady Hand','Draws %n more card each hand.']};

/* ---------- chance: one seeded stream, so a game can be replayed ---------- */
function rnd(G){G.seed=(G.seed+0x6D2B79F5)|0;var t=G.seed;t=Math.imul(t^(t>>>15),t|1);t^=t+Math.imul(t^(t>>>7),t|61);return((t^(t>>>14))>>>0)/4294967296}
function R(G,n){return Math.floor(rnd(G)*n)}
function shuf(G,a){a=a.slice();for(var i=a.length-1;i>0;i--){var j=R(G,i+1),t=a[i];a[i]=a[j];a[j]=t}return a}
function sg(n){return n>0?1:n<0?-1:0}

/* ---------- a run, a battle ---------- */
function newRun(opts){
  opts=opts||{};
  var G={seed:(opts.seed===undefined?Date.now():opts.seed)|0,opts:{rounds:opts.rounds||1,level:opts.level|0},run:{n:1,deck:(opts.deck||BASE_DECK).slice(),hp:MAX_HP,insp:3,spoils:0,felled:0,won:0,quick:0,renown:0}};
  startBattle(G);return G;
}
function unit(G,o){o.max=o.hp;o.guard=0;o.bank=0;o.fights=0;o.ai=0;o.st={blockStart:0,atkUp:0,drawUp:0};if(o.deck)o.dk={draw:shuf(G,o.deck),disc:[],gone:[]};return o}
function startBattle(G){
  var k=G.run.n-1,M=MAPS[k],lv=G.opts.level;   /* level: -1 gentle, 0 standard, 1 hard */
  G.map=M;G.turn=1;G.phase='player';G.clash=null;G.over=null;G.camp=null;G.ei=0;
  G.log=[[k===0?'Their captain holds the far bank. Bring him down.':k===1?'The road runs into the trees, and they are waiting in them.':'One bridge, one ford, and a banner on the far side.']];
  G.u=[
    unit(G,{id:'D',n:'Darrow',side:0,t:'blade',hp:MAX_HP,mov:3,rng:1,far:1,throws:T.throws,br:3,hn:5,rip:6,img:'darrow',lend:'lD',deck:G.run.deck.slice()}),
    unit(G,{id:'H',n:'Hollis',side:0,t:'blade',hp:40,mov:2,rng:1,br:2,hn:3,rip:6,img:'hollis',lend:'lH',deck:['hew','hew','fast','fast','bellow']}),
    unit(G,{id:'A',n:'Ash',side:0,t:'foot',hp:30,mov:4,rng:1,br:2,hn:3,rip:4,img:'ash',lend:'lA',deck:['legs','legs','worry','worry','slip']}),
    unit(G,{id:'W',n:'Wren',side:0,t:'cast',hp:26,mov:3,rng:2,br:2,hn:3,rip:3,img:'wren',lend:'lW',deck:['stone','stone','count','count','duck']}),
    /* Rae, the carter. She does not fight: she tends whoever is beside her, and lends a hand to a fighter beside her. */
    unit(G,{id:'R',n:'Rae',side:0,t:'foot',hp:28,mov:3,rng:0,br:0,hn:0,rip:0,img:'rae',lend:'lR',tend:T.tend,tends:T.tends})];
  G.u.forEach(function(u){u.x=M.pos[u.id][0];u.y=M.pos[u.id][1]});
  M.foes.forEach(function(f){var b=FOES[f[0]],o={id:f[0],side:1,x:f[1],y:f[2]};for(var key in b)o[key]=b[key];
    o.hp=Math.round(b.hp*(1+T.hpBy[k]+T.levelHp*lv));o.atk=Math.max(1,b.atk+T.atkBy[k]+T.foeAtk+T.levelAtk*lv);o.ans=b.ans.map(function(a){var n=a.n||1;return {b:a.b||0,d:Math.max(1,a.d+T.atkBy[k]+T.levelAtk*lv+(n>1?0:T.ansD)),n:n}});   /* a flurry is not made heavier blow by blow */G.u.push(unit(G,o))});
  G.u[0].hp=Math.max(1,Math.min(MAX_HP,G.run.hp));
}

/* ---------- the map ---------- */
function nm(u,cap){return u.side?(cap?'The ':'the ')+u.n:u.n}
function byId(G,id){for(var i=0;i<G.u.length;i++)if(G.u[i].id===id)return G.u[i];return null}
function at(G,x,y){for(var i=0;i<G.u.length;i++){var u=G.u[i];if(u.hp>0&&u.x===x&&u.y===y)return u}return null}
function ter(G,x,y){return G.map.rows[y].charAt(x)}
function ok(G,x,y){return x>=0&&y>=0&&x<W&&y<H&&ter(G,x,y)!=='~'}
function cost(G,x,y){var c=ter(G,x,y);return c==='w'||c==='f'?2:1}
function dist(a,b){return Math.abs(a.x-b.x)+Math.abs(a.y-b.y)}
function inRange(a,d){var k=dist(a,d);return k>=1&&k<=a.rng}
function tri(a,d){return BEAT[a.t]===d.t?1:(BEAT[d.t]===a.t?-1:0)}
function canAct(u){return u.side===0&&u.hp>0&&!(u.attacked&&!u.free)}
function live(G){return !G.over&&!G.clash&&G.phase==='player'}
function foesUp(G){return G.u.filter(function(o){return o.side===1&&o.hp>0})}
function matesUp(G){return G.u.filter(function(o){return o.side===0&&o.hp>0})}
function reach(G,u){
  var seen={},q=[[u.x,u.y,0]];seen[u.x+','+u.y]=0;
  while(q.length){q.sort(function(a,b){return a[2]-b[2]});var c=q.shift();
    [[1,0],[-1,0],[0,1],[0,-1]].forEach(function(d){var x=c[0]+d[0],y=c[1]+d[1],k=x+','+y;if(!ok(G,x,y)||at(G,x,y))return;var n=c[2]+cost(G,x,y);if(n>u.mov||(seen[k]!==undefined&&seen[k]<=n))return;seen[k]=n;q.push([x,y,n])})}
  return seen;
}
function dangerSet(G){
  var z={};
  foesUp(G).forEach(function(e){var r=(e.pinned||holding(G,e))?{}:reach(G,e);r[e.x+','+e.y]=0;
    Object.keys(r).forEach(function(k){var p=k.split(','),px=+p[0],py=+p[1];
      for(var dx=-e.rng;dx<=e.rng;dx++)for(var dy=-e.rng;dy<=e.rng;dy++){var m=Math.abs(dx)+Math.abs(dy);if(m>=1&&m<=e.rng&&ok(G,px+dx,py+dy))z[(px+dx)+','+(py+dy)]=1}})});
  return z;
}
function move(G,u,x,y){
  if(!live(G)||!canAct(u)||u.moved||(x===u.x&&y===u.y))return false;
  if(reach(G,u)[x+','+y]===undefined)return false;
  u.from=u.attacked?null:[u.x,u.y];u.x=x;u.y=y;u.moved=true;if(u.attacked)u.free=false;return true;
}
/* Nothing is hidden on the map, so a move can be taken back until that fighter does something else. */
function canUnmove(G,u){return live(G)&&u.side===0&&u.hp>0&&u.moved&&!u.attacked&&!!u.from&&!at(G,u.from[0],u.from[1])}
function unmove(G,u){if(!canUnmove(G,u))return false;u.x=u.from[0];u.y=u.from[1];u.from=null;u.moved=false;return true}
function hold(G,u){if(!live(G)||!canAct(u)||u.attacked)return false;u.attacked=true;u.moved=true;u.free=false;u.from=null;u.guard+=4;return true}
function tendTargets(G,u){if(!live(G)||!canAct(u)||u.attacked||!u.tend||u.tends<1)return [];return matesUp(G).filter(function(o){return o!==u&&dist(o,u)===1&&(o.hp<o.max||wounds(o)>0)})}
function tend(G,u,t){
  if(tendTargets(G,u).indexOf(t)<0)return null;
  var h=Math.min(u.tend,t.max-t.hp),w=false;t.hp+=h;
  if(t.dk){var p=t.dk.disc.indexOf('wound')>=0?t.dk.disc:(t.dk.draw.indexOf('wound')>=0?t.dk.draw:null);if(p){p.splice(p.indexOf('wound'),1);w=true}}
  u.attacked=true;u.moved=true;u.free=false;u.from=null;u.fights++;u.tends--;
  G.log=[[u.n+' tends '+t.n+': '+h+' mended'+(w?', a Wound set aside':'')+'.','good']];
  return {heal:h,wound:w};
}
/* A fight can be started within reach; Darrow, a few times a battle, can open one from two tiles with a throw. */
function canEngage(u,d){var k=dist(u,d);return k>=1&&k<=(u.throws>0?2:u.rng)}
function targets(G,u){if(!live(G)||!canAct(u)||u.attacked)return [];return G.u.filter(function(d){return d.side===1&&d.hp>0&&canEngage(u,d)})}

/* ---------- what makes a foe's blow bigger ---------- */
function rallied(G,e){return G.u.some(function(o){return o.side===1&&o.hp>0&&o.rally&&o!==e})}
function enraged(e){return !!e.enrage&&e.hp>0&&e.hp*2<=e.max}
function bonus(G,e){return (rallied(G,e)?T.rally:0)+(enraged(e)?e.enrage:0)}
function holding(G,e){if(!e.boss||!T.capHolds||foesUp(G).length<=2||G.turn>=T.capPatience)return false;var b=99;matesUp(G).forEach(function(o){var k=dist(o,e);if(k<b)b=k});return b>T.capHolds}
function fell(G,f,fx){if(f.side!==1||f.paid)return;f.paid=true;var n=f.boss?T.spoilBoss:T.spoilFoe;G.run.spoils+=n;G.run.felled++;if(fx)fx.push({k:'spoils',n:n})}
function wounds(u){if(!u.dk)return 0;var n=0;['draw','disc'].forEach(function(p){u.dk[p].forEach(function(id){if(id==='wound')n++})});return n}

/* ---------- before a clash: what the ground gives ---------- */
function ansText(a){return (a.b?'braces for '+a.b+', then strikes':'strikes')+' for '+a.d+(a.n>1?(a.n===2?' twice':' '+a.n+' times'):'')}
function preview(G,a,d){
  var base=d.ans[d.ai%d.ans.length],p={tri:tri(a,d),wood:ter(G,d.x,d.y)==='w',mark:!!d.marked,open:!!d.fought,far:dist(a,d)===2,can:inRange(d,a)};
  p.ans={b:base.b,d:base.d+bonus(G,d),n:base.n};
  p.lend=G.u.filter(function(o){return o.side===0&&o.hp>0&&o!==a&&(dist(o,a)===1||inRange(o,d))});
  p.en=Math.max(1,a.br+(p.tri<0?-1:0)+(p.mark?1:0)+a.bank-(p.far?(a.far||0):0));p.chips=[];
  if(p.tri>0)p.chips.push([TREE[a.t]+' beats '+TREE[d.t]+': land a hit and his answer is halved','up']);
  if(p.tri<0)p.chips.push([TREE[d.t]+' beats '+TREE[a.t]+': 1 less breath','dn']);
  p.lend.forEach(function(o){p.chips.push([o.n+' is with you: a card lent'+(o.fights>=2?', risen':''),'up'])});
  if(a.bank)p.chips.push(['Held breath: +'+a.bank,'up']);
  if(p.mark)p.chips.push(['Marked: +1 breath','up']);
  if(p.open)p.chips.push(['He has fought already: Open','up']);
  if(p.wood)p.chips.push(['He is in the wood: '+T.woodBlock+' block','dn']);
  if(d.tough)p.chips.push(['Tough: each hit deals '+d.tough+' less','dn']);
  if(d.barbed&&p.can)p.chips.push(['Barbed: a blow that lands leaves a Wound','dn']);
  if(rallied(G,d))p.chips.push(['Rallied by the banner: +'+T.rally,'dn']);
  if(enraged(d))p.chips.push(['Enraged: +'+d.enrage,'dn']);
  if(p.far)p.chips.push(['From two tiles: thrown cards only'+(a.far?', '+a.far+' less breath. Uses his throw for this battle':''),a.far?'dn':'']);
  if(p.can&&p.ans.d*p.ans.n>=a.hp)p.chips.push(['This could put '+a.n+' down','dn']);
  p.txt=p.can?'He '+ansText(p.ans)+'.':'He cannot reach to answer.';
  p.worst=p.can?Math.max(0,a.hp-p.ans.d*p.ans.n):a.hp;p.cards=a.hn+a.st.drawUp+p.lend.length;
  return p;
}

/* ---------- the clash ---------- */
function draw(G,u,n){var K=G.clash,got=0;while(n-->0&&K.hand.length<HAND_CAP){if(!u.dk.draw.length){if(!u.dk.disc.length)break;u.dk.draw=shuf(G,u.dk.disc);u.dk.disc=[]}K.hand.push(u.dk.draw.pop());got++}return got}
function engage(G,a,d){
  if(targets(G,a).indexOf(d)<0)return null;
  var p=preview(G,a,d),base=d.ans[d.ai%d.ans.length];d.ai++;d.marked=false;a.bank=0;a.from=null;if(p.far&&a.far&&a.throws>0)a.throws--;
  var K=G.clash={a:a,d:d,p:p,round:1,en:p.en,block:a.st.blockStart,intent:{b:base.b,d:base.d,n:base.n},fb:base.b+(p.wood?T.woodBlock:0),open:p.open,far:p.far,canBreak:p.tri>0,halved:false,broken:false,push:false,pin:false,again:false,
    hand:[],phase:'play',redrawn:false,dealt:0,taken:0,played:0,lines:[]};
  draw(G,a,a.hn+a.st.drawUp);p.lend.forEach(function(o){if(K.hand.length<HAND_CAP)K.hand.push(o.lend+(o.fights>=2?'2':''))});
  return K;
}
/* the hits a card will make, before his block: one number for each blow */
function hitList(K,c){
  var n=c.dmg,d=K.d;if(c.dmgStood&&!K.a.moved)n=c.dmgStood;if(c.dmgLow&&d.hp*2<=d.max)n=c.dmgLow;n+=K.a.st.atkUp;
  var out=[];for(var i=0;i<(c.hits||1);i++){var h=n;if(i===0&&K.open)h=Math.round(h*1.5);out.push(Math.max(0,h-(d.tough||0)))}return out;
}
function cardDmg(K,c){return hitList(K,c)[0]}
function playable(G,i){
  var K=G.clash;if(!K||K.phase!=='play')return 'Not now.';
  var c=C[K.hand[i]];if(!c)return 'No such card.';
  if(c.dead)return 'A Wound cannot be played. It is gone after the battle.';
  if(K.far&&c.m)return 'From two tiles only thrown cards reach him.';
  if(K.en<c.c)return 'Needs '+c.c+' breath. You have '+K.en+'.';
  return '';
}
/* one blow on the foe in the clash: Open, then Tough, then his block. Returns what was left over if it felled him. */
function strikeFoe(G,K,n,pierce,fx,by,raw){
  var d=K.d,crit=false,ab=0;
  if(raw){if(K.open){n=Math.round(n*1.5);K.open=false;crit=true}n=Math.max(0,n-(d.tough||0))}
  else if(K.open){K.open=false;crit=true}
  if(!pierce){ab=Math.min(K.fb,n);K.fb-=ab}
  var thru=n-ab,before=d.hp;d.hp=Math.max(0,d.hp-thru);K.dealt+=Math.min(thru,before);
  fx.push({k:'dmg',n:thru,blocked:ab,crit:crit,by:by||null});
  if(thru>0&&K.canBreak&&!K.broken){K.broken=true;fx.push({k:'status',who:'d',t:'Broken'})}
  if(d.enrage&&before*2>d.max&&d.hp>0&&d.hp*2<=d.max)fx.push({k:'status',who:'d',t:'Enraged'});
  return thru-before;
}
function play(G,i){
  if(playable(G,i))return null;
  var K=G.clash,id=K.hand[i],c=C[id],a=K.a,d=K.d,fx=[],j;
  K.en-=c.c;K.hand.splice(i,1);K.played++;
  if(c.dmg){
    var hs=hitList(K,c);
    for(j=0;j<hs.length&&d.hp>0;j++){var over=strikeFoe(G,K,hs[j],c.pierce,fx,null,false);
      if(d.hp<=0&&c.carry&&over>0){var nb=foesUp(G).filter(function(o){return o!==d&&dist(o,d)===1}).sort(function(x,y){return x.hp-y.hp})[0];
        if(nb){var cd=Math.max(0,over-(nb.tough||0));nb.hp=Math.max(0,nb.hp-cd);fx.push({k:'carry',id:nb.id,n:cd,down:nb.hp<=0});if(nb.hp<=0)fell(G,nb,fx)}}}
  }
  if(c.assist&&d.hp>0)K.p.lend.forEach(function(o){if(o.hp>0&&d.hp>0)strikeFoe(G,K,c.assist,false,fx,o.n,true)});
  if(d.hp>0){
    if(c.open){K.open=true;fx.push({k:'status',who:'d',t:'Open'})}
    if(c.pin){K.pin=true;fx.push({k:'status',who:'d',t:'Pinned'})}
    if(c.push){K.push=true;fx.push({k:'status',who:'d',t:'Driven back'})}
    if(c.halve){K.halved=true;fx.push({k:'status',who:'d',t:'Halved'})}
    if(c.mark){d.marked=true;fx.push({k:'status',who:'d',t:'Marked'})}
  }
  if(c.blk){K.block+=c.blk;fx.push({k:'block',n:c.blk})}
  if(c.guardFriends)matesUp(G).forEach(function(o){if(o!==a&&dist(o,a)===1){o.guard+=c.guardFriends;fx.push({k:'friend',id:o.id,n:c.guardFriends})}});
  if(c.cleanse){var where=K.hand.indexOf('wound')>=0?K.hand:(a.dk.disc.indexOf('wound')>=0?a.dk.disc:(a.dk.draw.indexOf('wound')>=0?a.dk.draw:null));if(where){where.splice(where.indexOf('wound'),1);fx.push({k:'cleanse'})}}
  if(c.heal){var h=Math.min(c.heal,a.max-a.hp);a.hp+=h;fx.push({k:'heal',n:h})}
  if(c.en){K.en+=c.en;fx.push({k:'breath',n:c.en})}
  if(c.spoil){G.run.spoils+=c.spoil;fx.push({k:'spoils',n:c.spoil})}
  if(c.stance){a.st[c.stance]+=c.sv;if(c.stance==='blockStart'){K.block+=c.sv}fx.push({k:'stance',t:STANCE[c.stance][0]})}
  if(c.draw){fx.push({k:'draw',n:draw(G,a,(c.drawOpen&&K.open)?c.drawOpen:c.draw)})}
  if(c.again){K.again=true;fx.push({k:'status',who:'a',t:'Move again'})}
  if(!c.lent)(c.ex?a.dk.gone:a.dk.disc).push(id);
  if(d.hp<=0){fx.push({k:'down',who:'d'});fell(G,d,fx);if(a.id==='D'&&T.spoilOwn){G.run.spoils+=T.spoilOwn;fx.push({k:'spoils',n:T.spoilOwn,own:1})}if(c.spoilKill){G.run.spoils+=c.spoilKill;fx.push({k:'spoils',n:c.spoilKill})}settle(G,'won')}
  return fx;
}
function redraw(G){
  var K=G.clash;if(!K||K.phase!=='play'||K.a.id!=='D'||G.run.insp<1||K.redrawn)return false;
  G.run.insp--;K.redrawn=true;var a=K.a,keep=[];
  K.hand.forEach(function(id){if(C[id].lent)keep.push(id);else a.dk.disc.push(id)});K.hand=[];draw(G,a,a.hn+a.st.drawUp);
  keep.forEach(function(id){if(K.hand.length<HAND_CAP)K.hand.push(id)});return true;
}
/* What he will do when the hand ends, as it stands right now. */
function intent(G){
  var K=G.clash;if(!K.p.can)return {none:'reach'};
  var d=K.intent.d+bonus(G,K.d);if(K.broken)d=Math.ceil(d/2);if(K.halved)d=Math.ceil(d/2);return {d:d,n:K.intent.n,halved:K.halved||K.broken,broken:K.broken,up:bonus(G,K.d)};
}
function nextIntent(G){var K=G.clash,d=K.d,nx=d.ans[d.ai%d.ans.length];return {b:nx.b,d:nx.d+T.pressUp*K.round+bonus(G,d),n:nx.n}}
function endHand(G){
  var K=G.clash;if(!K||K.phase!=='play')return null;
  var a=K.a,it=intent(G),fx=[];
  K.hand.forEach(function(id){if(!C[id].lent)a.dk.disc.push(id)});K.hand=[];
  if(it.none)fx.push({k:'answer',none:it.none});
  else{var tot=0,abT=0;for(var i=0;i<it.n&&a.hp>0;i++){var n=it.d,ab=Math.min(K.block,n);K.block-=ab;n-=ab;a.hp=Math.max(0,a.hp-n);tot+=n;abT+=ab}
    K.taken+=tot;fx.push({k:'answer',n:tot,blocked:abT,hits:it.n});
    if(tot>0&&K.d.barbed&&a.hp>0){a.dk.disc.push('wound');fx.push({k:'wound'})}}
  if(a.hp<=0){fx.push({k:'down',who:'a'});settle(G,'lost')}
  else if(K.round<G.opts.rounds)K.phase='choice';
  else settle(G,'after');
  return fx;
}
function pressOn(G){
  var K=G.clash;if(!K||K.phase!=='choice')return false;var a=K.a,d=K.d,nx=d.ans[d.ai%d.ans.length];
  d.ai++;K.round++;K.block=a.st.blockStart;K.intent={b:nx.b,d:nx.d+T.pressUp*(K.round-1),n:nx.n};K.fb=K.intent.b+(K.p.wood?T.woodBlock:0);
  K.en=Math.max(1,a.br+(K.p.tri<0?-1:0)-(K.far?(a.far||0):0)-T.pressBreath*(K.round-1));K.halved=false;K.broken=false;K.canBreak=false;K.redrawn=false;K.phase='play';
  draw(G,a,a.hn+a.st.drawUp);return true;
}
function leave(G){var K=G.clash;if(!K||K.phase!=='choice')return false;settle(G,'after');return true}
function settle(G,how){
  var K=G.clash,a=K.a,d=K.d,L=[];K.phase=how;
  K.hand.forEach(function(id){if(!C[id].lent)a.dk.disc.push(id)});K.hand=[];
  a.fights++;d.fought=true;a.attacked=true;a.free=false;
  L.push([a.n+' on '+nm(d)+': '+K.dealt+' dealt, '+K.taken+' taken.',K.taken>K.dealt?'hurt':'good']);
  if(d.hp<=0)L.push([nm(d,1)+' is down.','good']);
  if(a.hp<=0){a.guard=0;a.bank=0;L.push([a.n+' falls back.','hurt']);K.lines=L;return}
  if(d.hp>0){
    if(K.pin){d.pinned=true;L.push(['He will not move next turn.','good'])}
    if(K.push){var dx=d.x-a.x,dy=d.y-a.y,sx=Math.abs(dx)>=Math.abs(dy)?sg(dx):0,sy=sx?0:sg(dy),nx=d.x+sx,ny=d.y+sy;
      if(ok(G,nx,ny)&&!at(G,nx,ny)){d.x=nx;d.y=ny;L.push(['He is driven back a tile.','good'])}}
  }
  a.guard+=K.block;a.bank=Math.min(HELD_MAX,K.en);
  if(K.again){a.moved=false;a.free=true}
  if(d.hp<=0&&!a.more){a.more=true;a.attacked=false;a.moved=false;a.free=false;L.push(['A man down. '+a.n+' may act again.','good'])}
  if(a.guard||a.bank)L.push([a.n+' keeps '+(a.guard?a.guard+' guard':'')+(a.guard&&a.bank?' and ':'')+(a.bank?a.bank+' breath':'')+'.','dimm']);
  K.lines=L;
}
function closeClash(G){var K=G.clash;if(!K||(K.phase!=='after'&&K.phase!=='won'&&K.phase!=='lost'))return false;G.log=K.lines;G.clash=null;check(G);return true}

/* ---------- the enemy's turn, one foe at a time so it can be shown ---------- */
function endTurn(G){if(!live(G))return false;G.phase='enemy';G.ei=0;G.log=[];return true}
/* How far every tile is from the nearest of these units on foot, going round the water. */
function walkDist(G,us){
  var seen={},q=[];us.forEach(function(u){seen[u.x+','+u.y]=0;q.push([u.x,u.y,0])});
  while(q.length){q.sort(function(a,b){return a[2]-b[2]});var c=q.shift();
    [[1,0],[-1,0],[0,1],[0,-1]].forEach(function(d){var x=c[0]+d[0],y=c[1]+d[1],k=x+','+y;if(!ok(G,x,y))return;var n=c[2]+cost(G,x,y);if(seen[k]!==undefined&&seen[k]<=n)return;seen[k]=n;q.push([x,y,n])})}
  return seen;
}
function actFoe(G,e){
  var foes=matesUp(G);if(!foes.length)return null;
  var ev={k:'foe',id:e.id,from:[e.x,e.y],to:[e.x,e.y],pinned:false,holds:false,target:null,dmg:0,held:false,rip:0,wound:false,targetDown:false,foeDown:false};
  function near(px,py){var b=99;foes.forEach(function(o){var k=Math.abs(o.x-px)+Math.abs(o.y-py);if(k<b)b=k});return b}
  if(e.pinned){e.pinned=false;ev.pinned=true;G.log.push([nm(e,1)+' is still finding his feet.','dimm'])}
  else if(holding(G,e)){ev.holds=true}
  else if(!foes.some(function(o){return inRange(e,o)})){
    var r=reach(G,e),pd=walkDist(G,foes),best=null,bs=1e9;
    Object.keys(r).forEach(function(k){var p=k.split(','),n=near(+p[0],+p[1]),sc=(n>=1&&n<=e.rng)?(-100-n+r[k]*.1):((pd[k]===undefined?99:pd[k])*10+r[k]*.1);if(sc<bs){bs=sc;best=p}});
    if(best){e.x=+best[0];e.y=+best[1];ev.to=[e.x,e.y]}
  }
  var inr=foes.filter(function(o){return inRange(e,o)}).sort(function(a,b){return a.hp-b.hp});
  if(inr.length){
    var t=inr[0],n=Math.max(1,e.atk+bonus(G,e)+tri(e,t)*2-(ter(G,t.x,t.y)==='w'?T.woodCover:0)),ab=Math.min(t.guard,n);t.guard-=ab;n-=ab;t.hp=Math.max(0,t.hp-n);
    ev.target=t.id;ev.dmg=n;
    if(n){G.log.push([nm(e,1)+' strikes '+t.n+' for '+n+'.','hurt']);
      if(t.hp<=0){ev.targetDown=true;G.log.push([t.n+' falls back.','hurt'])}
      else if(e.barbed&&t.dk){t.dk.disc.push('wound');ev.wound=true;G.log.push([t.n+' takes a Wound.','hurt'])}}
    else{ev.held=true;
      if(inRange(t,e)){ev.rip=t.rip+t.st.atkUp;e.hp=Math.max(0,e.hp-ev.rip);G.log.push([nm(e,1)+' strikes '+t.n+'. The guard holds, and '+t.n+' answers for '+ev.rip+'.','good']);if(e.hp<=0){ev.foeDown=true;fell(G,e);G.log.push([nm(e,1)+' is down.','good'])}}
      else G.log.push([nm(e,1)+' strikes '+t.n+'. The guard holds.','good'])}
    check(G);
  }
  return ev;
}
function enemyStep(G){
  if(G.phase!=='enemy')return null;
  while(G.ei<G.u.length&&!G.over){var e=G.u[G.ei++];if(e.side!==1||e.hp<=0)continue;var ev=actFoe(G,e);if(ev)return ev}
  var heals=[];
  if(!G.log.length)G.log.push(['They hold where they stand.','dimm']);
  G.u.forEach(function(u){u.moved=false;u.attacked=false;u.free=false;u.fought=false;u.more=false;u.from=null;
    if(u.side===0)u.guard=0});
  G.turn++;G.phase='player';
  /* a battle cannot be drawn out for ever: by nightfall the far bank is still theirs */
  if(!G.over&&G.turn>T.maxTurns){G.over={lost:1,night:1,t:'Night falls',s:'The far bank is still theirs when the light goes. The company draws off, and the run ends here.'};G.run.renown=renown(G)}
  return {k:'turn',heals:heals};
}

/* ---------- winning, losing, the camp between battles ---------- */
function renown(G){return G.run.spoils+6*G.run.won+G.run.quick+2*(G.over&&G.over.done?matesUp(G).length-1:0)+Math.floor(G.u[0].hp/8)}
function check(G){
  if(G.over)return;var cap=G.u.filter(function(u){return u.boss})[0];
  if(G.u[0].hp<=0){G.over={lost:1,t:'The line is broken',s:'Darrow is carried back from the water. The run ends here.'};G.run.renown=renown(G)}
  else if(cap.hp<=0){
    fell(G,cap);G.run.won++;G.run.quick+=Math.max(0,T.par-G.turn);
    if(G.run.n<MAPS.length){G.over={win:1};G.camp={market:shuf(G,POOL).slice(0,T.market),bought:[]}}
    else{G.over={done:1,t:'The road is held',s:'Three crossings, three captains. Nothing from the run goes on the sheet.'};G.run.renown=renown(G)}
  }
}
function inCamp(G){return !!(G.over&&G.over.win&&G.camp&&!G.clash)}
function campBuy(G,id){if(!inCamp(G))return false;var j=G.camp.market.indexOf(id);if(j<0||G.run.spoils<C[id].p)return false;G.run.spoils-=C[id].p;G.camp.market.splice(j,1);G.camp.bought.push(id);G.run.deck.push(id);return true}
function campMend(G){if(!inCamp(G)||G.run.spoils<T.mendCost||G.u[0].hp>=MAX_HP)return false;G.run.spoils-=T.mendCost;G.u[0].hp=Math.min(MAX_HP,G.u[0].hp+T.mend);return true}
function campRemove(G,id){if(!inCamp(G)||G.run.spoils<T.removeCost||G.run.deck.length<=MIN_DECK)return false;var j=G.run.deck.indexOf(id);if(j<0)return false;G.run.spoils-=T.removeCost;G.run.deck.splice(j,1);return true}
function campHone(G,id){if(!inCamp(G)||G.run.spoils<T.honeCost||!C[id]||!C[id].hone)return false;var j=G.run.deck.indexOf(id);if(j<0)return false;G.run.spoils-=T.honeCost;G.run.deck[j]=C[id].hone;return true}
function nextBattle(G){
  if(!inCamp(G))return false;
  G.run.hp=Math.min(MAX_HP,G.u[0].hp+T.rest);G.run.n++;startBattle(G);return true;
}

/* ---------- what is in force, said in words: for tokens, chips and the panel ---------- */
function E(id,label,text,tone,n){return {id:id,label:label,text:text,tone:tone,n:n===undefined?null:n}}
function effects(G,u){
  var out=[],t=ter(G,u.x,u.y);
  if(u.side===0){
    if(u.guard)out.push(E('guard','Guard '+u.guard,'Soaks the next '+u.guard+' damage on their turn. If it holds a blow whole, '+u.n+' strikes back for '+(u.rip+u.st.atkUp)+'.','good',u.guard));
    if(u.bank)out.push(E('held','Held breath '+u.bank,u.bank+' more breath in '+u.n+"'s next clash.",'good',u.bank));
    var w=wounds(u);if(w)out.push(E('wound',w+(w>1?' Wounds':' Wound'),'Dead cards in the deck until the battle ends. A Clean Bandage or The Mender\'s Patience sets one aside.','bad',w));
    for(var s in u.st)if(u.st[s])out.push(E('stance',STANCE[s][0],STANCE[s][1].replace('%n',u.st[s]),'good',u.st[s]));
    if(u.tend)out.push(u.tends>0?E('tend','Tends ×'+u.tends,'Rae does not fight. On her turn she mends a friend beside her for '+u.tend+' and sets aside a Wound, '+u.tends+' more time'+(u.tends>1?'s':'')+' this battle. A fighter beside her is lent her hand.','good',u.tends):E('tend','Cart is bare','Rae has nothing left to tend with this battle. A fighter beside her is still lent her hand.','plain',0));
    if(u.fights>=2)out.push(E('risen','Risen','The card '+u.n+' lends has risen.','good'));
    if(u.throws>0)out.push(E('throw','A throw in hand'+(u.throws>1?' ×'+u.throws:''),'Once this battle '+u.n+' can open a fight from two tiles: thrown cards only, one less breath, and most foes cannot answer.','good',u.throws));
    if(u.attacked&&u.free)out.push(E('again','May still move','The Long Road: one more move this turn.','good'));
    if(t==='w')out.push(E('cover','In the wood','Blows on their turn deal '+T.woodCover+' less here.','good'));
  }else{
    if(u.pinned)out.push(E('pinned','Pinned','He will not move on his next turn.','good'));
    if(u.marked)out.push(E('marked','Marked','The next friend to fight him has 1 more breath.','good'));
    if(u.fought)out.push(E('open','Open','He has fought this turn. The next first hit on him lands for half again.','good'));
    if(u.tough)out.push(E('tough','Tough '+u.tough,'Each hit on him deals '+u.tough+' less. Few big blows beat many small ones.','bad',u.tough));
    if(u.barbed)out.push(E('barbed','Barbed','A blow of his that gets through leaves a Wound in the deck.','bad'));
    if(u.rally)out.push(E('banner','Banner','While he stands, every other foe strikes '+T.rally+' harder.','bad'));
    if(rallied(G,u))out.push(E('rallied','Rallied +'+T.rally,'The banner is up: he strikes '+T.rally+' harder.','bad',T.rally));
    if(u.enrage)out.push(enraged(u)?E('enraged','Enraged +'+u.enrage,'At half health or less he strikes '+u.enrage+' harder.','bad',u.enrage):E('temper','Will enrage','At half health he will strike '+u.enrage+' harder.','plain'));
    if(holding(G,u))out.push(E('holds','Holds his ground','He will not come forward until someone is within '+T.capHolds+' tiles, his men are thinned, or turn '+T.capPatience+' comes.','plain'));
    if(u.ans.some(function(a){return a.n>1}))out.push(E('flurry','Flurry','His answer is several small blows. Block soaks each one.','plain'));
    if(t==='w')out.push(E('cover','In the wood','He starts a clash with '+T.woodBlock+' block.','bad'));
  }
  return out;
}
function clashEffects(G){
  var K=G.clash,a=K.a,d=K.d,A=[],D=[],it=K.phase==='play'?intent(G):null;
  if(K.block)A.push(E('block','Block '+K.block,'Soaks his answer. What is left stays on '+a.n+' as guard.','good',K.block));
  for(var s in a.st)if(a.st[s])A.push(E('stance',STANCE[s][0],STANCE[s][1].replace('%n',a.st[s]),'good',a.st[s]));
  if(K.again)A.push(E('again','Moves again','After this clash '+a.n+' may move once more.','good'));
  if(K.far)A.push(E('far','Two tiles off','Only thrown cards reach him from here'+(a.far?', and '+a.n+' has '+a.far+' less breath for it':'')+'.','plain'));
  if(K.p.tri<0)A.push(E('down','Outmatched',TREE[d.t]+' beats '+TREE[a.t]+': 1 less breath.','bad'));
  var w=K.hand.filter(function(x){return x==='wound'}).length;if(w)A.push(E('wound',w+(w>1?' Wounds':' Wound')+' in hand','Dead cards. Gone after the battle.','bad',w));
  if(K.fb)D.push(E('block','Block '+K.fb,'Soaks your hits before they reach him. Overwall goes over it.','bad',K.fb));
  if(K.open)D.push(E('open','Open','Your next hit lands for half again.','good'));
  if(K.broken)D.push(E('broken','Broken','His answer this hand is halved.','good'));
  else if(K.canBreak&&K.p.can)D.push(E('edge','Can be Broken',TREE[a.t]+' beats '+TREE[d.t]+'. Land one hit and his answer is halved.','good'));
  if(K.halved)D.push(E('halved','Shaken','Bellow: his blow lands for half'+(K.broken?' again':'')+'.','good'));
  if(K.pin)D.push(E('pinned','Pinned','He will not move on his next turn.','good'));
  if(K.push)D.push(E('pushed','Driven back','He gives a tile when the clash ends, if there is room.','good'));
  if(d.marked)D.push(E('marked','Marked','The next friend to fight him has 1 more breath.','good'));
  if(d.tough)D.push(E('tough','Tough '+d.tough,'Each hit on him deals '+d.tough+' less.','bad',d.tough));
  if(d.barbed&&K.p.can)D.push(E('barbed','Barbed','If his answer gets through, a Wound goes into the deck.','bad'));
  if(rallied(G,d))D.push(E('rallied','Rallied +'+T.rally,'The banner is up: he strikes '+T.rally+' harder.','bad',T.rally));
  if(d.enrage)D.push(enraged(d)?E('enraged','Enraged +'+d.enrage,'At half health or less he strikes '+d.enrage+' harder.','bad',d.enrage):E('temper','Will enrage','At half health he will strike '+d.enrage+' harder.','plain'));
  if(it&&!it.none&&it.n>1)D.push(E('flurry','Flurry ×'+it.n,'He strikes '+it.n+' times. Block soaks each blow in turn.','plain',it.n));
  return {a:A,d:D};
}

/* ---------- what a card says, made from what it does ---------- */
function times(n){return n===2?' twice':' '+n+' times'}
function cardText(id,K){
  var c=C[id],s=[];
  if(c.dead)return 'Cannot be played. Gone after the battle.';
  if(c.dmg){
    if(K){var hs=hitList(K,c),base=c.dmg,mod=function(n){return n!==base?'<em>'+n+'</em>':''+n};
      s.push('Deal '+(hs.length>1&&hs[0]!==hs[1]?mod(hs[0])+', then '+mod(hs[1])+(hs.length>2?times(hs.length-1):''):mod(hs[0])+(hs.length>1?times(hs.length):''))+(c.pierce?' over his guard':'')+'.')}
    else s.push('Deal '+c.dmg+(c.hits?times(c.hits):'')+(c.dmgStood?', or '+c.dmgStood+' if you stood your ground this turn':'')+(c.dmgLow?', or '+c.dmgLow+' if he is at half health or less':'')+(c.pierce?' over his guard':'')+'.');
  }
  if(c.carry)s.push('What is left over hits a foe beside him.');
  if(c.assist)s.push('Each friend with you strikes him for '+c.assist+(K?' ('+K.p.lend.length+' with you)':'')+'.');
  if(c.open)s.push('He is Open.');
  if(c.pin)s.push('He cannot move next turn.');
  if(c.push)s.push('Drive him back a tile.');
  if(c.blk)s.push('Block '+c.blk+'.');
  if(c.guardFriends)s.push('Each friend beside you gains '+c.guardFriends+' guard.');
  if(c.cleanse)s.push('Set aside a Wound.');
  if(c.heal)s.push('Heal '+c.heal+'.');
  if(c.en)s.push('Gain '+c.en+' breath.');
  if(c.spoil)s.push('Gain '+c.spoil+' spoils.');
  if(c.spoilKill)s.push('If this fells him, gain '+c.spoilKill+' spoils.');
  if(c.stance)s.push('For the rest of the battle: '+STANCE[c.stance][1].replace('%n',c.sv).replace(/^(.)/,function(m){return m.toLowerCase()}));
  if(c.draw)s.push('Draw '+c.draw+(c.drawOpen?', or '+c.drawOpen+' if he is Open':'')+'.');
  if(c.again)s.push('Then move again.');
  if(c.halve)s.push('His answer is halved.');
  if(c.mark)s.push('Mark him: the next friend to fight him has 1 more breath.');
  if(c.ex&&!c.stance)s.push('Once a battle.');
  return s.join(' ');
}

root.LH={T:T,SHEET:SHEET,W:W,H:H,MAPS:MAPS,FOES:FOES,TREE:TREE,BEAT:BEAT,C:C,POOL:POOL,STANCE:STANCE,BASE_DECK:BASE_DECK,HAND_CAP:HAND_CAP,MAX_HP:MAX_HP,HELD_MAX:HELD_MAX,MIN_DECK:MIN_DECK,
  newRun:newRun,nm:nm,byId:byId,at:at,ter:ter,ok:ok,cost:cost,dist:dist,inRange:inRange,tri:tri,canAct:canAct,reach:reach,dangerSet:dangerSet,foesUp:foesUp,matesUp:matesUp,
  move:move,canUnmove:canUnmove,unmove:unmove,hold:hold,canEngage:canEngage,tendTargets:tendTargets,tend:tend,targets:targets,preview:preview,engage:engage,hitList:hitList,cardDmg:cardDmg,playable:playable,play:play,redraw:redraw,intent:intent,nextIntent:nextIntent,ansText:ansText,
  endHand:endHand,pressOn:pressOn,leave:leave,closeClash:closeClash,endTurn:endTurn,enemyStep:enemyStep,rallied:rallied,enraged:enraged,holding:holding,wounds:wounds,
  inCamp:inCamp,campBuy:campBuy,campMend:campMend,campRemove:campRemove,campHone:campHone,nextBattle:nextBattle,renown:renown,effects:effects,clashEffects:clashEffects,cardText:cardText};
})(typeof module!=='undefined'&&module.exports?module.exports:window);
