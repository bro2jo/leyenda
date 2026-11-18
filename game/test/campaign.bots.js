/* The campaign's test players: a plan for each mission that a sensible person would follow, and the hands that go with it.
   Used by campaign.test.js (can every mission be finished?) and campaign.play.js (how does each one play?). */
var LH=require('../src/engine.js').LH,CP=require('../src/campaign.js').CP;require('../src/missions.js');
function U(G,id){return CP.api.U(G,id)}
function bfs(G,sx,sy){var seen={},q=[[sx,sy,0]];seen[sx+','+sy]=0;while(q.length){var c=q.shift();[[1,0],[-1,0],[0,1],[0,-1]].forEach(function(d){var x=c[0]+d[0],y=c[1]+d[1],k=x+','+y;if(!LH.ok(G,x,y)||seen[k]!==undefined)return;seen[k]=c[2]+LH.cost(G,x,y);q.push([x,y,seen[k]]);q.sort(function(a,b){return a[2]-b[2]})})}return seen}
/* move u as near as it can get to a tile (or onto it) */
function go(G,u,tx,ty,adj){
  if(!u||u.hp<=0||!LH.canAct(u)||u.moved)return;var d=bfs(G,tx,ty),r=LH.reach(G,u),best=null,bs=d[u.x+','+u.y];if(bs===undefined)bs=99;
  if(adj&&Math.abs(u.x-tx)+Math.abs(u.y-ty)===1)return;
  Object.keys(r).forEach(function(k){var v=d[k];if(v===undefined)return;if(adj&&v===0)return;if(v<bs){bs=v;best=k}});
  if(best){var p=best.split(',');LH.move(G,u,+p[0],+p[1])}
}
/* play a hand: block what is coming if it would hurt, then hit, then whatever is free */
function hand(G,opt){
  opt=opt||{};if(MODE.stat)opt.stat=MODE.stat;if(MODE.rand)opt.rand=MODE.rand;var K=G.clash,guard=0;
  while(K&&K.phase==='play'&&guard++<40){
    var it=LH.intent(G),inc=it.none?0:it.d*it.n,best=-1,bv=-1;
    if(opt.stat||opt.rand){var can=[];K.hand.forEach(function(id,i){if(!LH.playable(G,i))can.push(i)});if(opt.stat){opt.stat.decisions++;opt.stat.options+=can.length}
      if(opt.rand){if(!can.length||opt.rand()<.2)break;LH.play(G,can[Math.floor(opt.rand()*can.length)]);if(opt.stat)opt.stat.played++;K=G.clash;if(!K||K.phase!=='play')break;continue}}
    K.hand.forEach(function(id,i){if(LH.playable(G,i))return;var c=LH.C[id],v=0;
      if(id==='turn')v=100;
      if(c.en||c.draw)v=Math.max(v,50);
      if(c.blk&&inc>K.block)v=Math.max(v,30+Math.min(c.blk,inc-K.block)+(c.halve?3:0));
      if(c.halve&&inc>K.block)v=Math.max(v,28);
      if(c.dmg){var h=LH.hitList(K,c).reduce(function(a,b){return a+b},0);if(h>0)v=Math.max(v,(opt.blockFirst&&inc>K.block?5:20)+h/Math.max(1,c.c))}
      if(c.heal&&K.a.hp<K.a.max-c.heal)v=Math.max(v,25);
      if(c.open||c.mark||c.pin)v=Math.max(v,10);
      if(v>bv){bv=v;best=i}});
    if(best<0||bv<=0)break;if(opt.stat)opt.stat.played++;LH.play(G,best);K=G.clash;if(!K||K.phase!=='play')break;
  }
  K=G.clash;if(K&&K.phase==='play')LH.endHand(G);
  K=G.clash;guard=0;
  while(K&&K.phase==='choice'&&guard++<5){if(opt.press&&opt.press(G,K)){LH.pressOn(G);hand(G,opt);return}else LH.leave(G);K=G.clash}
  if(G.clash)LH.closeClash(G);
}
/* how good a card is, roughly: what it does for the breath it costs. Used to deal a fighter the best or the worst of the pile. */
function worth(id){var c=LH.C[id];if(!c||c.dead)return -5;var v=(c.dmg||0)*(c.hits||1)+(c.blk||0)+(c.heal||0)+3*(c.draw||0)+4*(c.en||0)+(c.halve?6:0)+(c.open?3:0)+(c.pin?2:0)+(c.stance?6:0);return v/Math.max(.6,c.c||0)}
/* luck, held to one side: before a fight the pile is put in order, so that hand after hand comes up the best it could, or the worst */
function rig(u){if(!MODE.luck||!u.dk)return;var cyc=/cycle/.test(MODE.luck),all=cyc?u.dk.draw.slice():u.dk.draw.concat(u.dk.disc);if(!cyc)u.dk.disc=[];all.sort(function(a,b){return worth(a)-worth(b)});if(/worst/.test(MODE.luck))all.reverse();u.dk.draw=all}
function fight(G,u,opt){if(!u||u.hp<=0||G.over)return false;var t=LH.targets(G,u);if(!t.length)return false;rig(u);t.sort(function(a,b){return a.hp-b.hp});if(!LH.engage(G,u,t[0]))return false;hand(G,opt);return true}
function tendD(G,id,min){var m=U(G,id),D=G.u[0];if(!m||G.over)return;var t=LH.tendTargets(G,m);if(t.indexOf(D)>=0&&D.max-D.hp>=(min||5))LH.tend(G,m,D)}
function endTurn(G){if(G.over)return;if(!LH.endTurn(G))return;var n=0;while(LH.enemyStep(G)&&n++<200){}}
function nearestFoe(G,u){var f=CP.api.foes(G).filter(function(e){return !e.scripted});f.sort(function(a,b){return CP.api.dist(a,u)-CP.api.dist(b,u)});return f[0]}
/* a plain fight: everyone goes at the nearest foe, the Mender keeps by Darrow */
function battle(G){var D=G.u[0];CP.api.mates(G).forEach(function(u){if(G.over||u.hp<=0||u.still)return;
  if(u.tend){go(G,u,D.x,D.y,true);tendD(G,u.id,5);return}if(!u.dk)return;
  var f=nearestFoe(G,u);if(!f)return;if(u.mov>0&&!LH.targets(G,u).length)go(G,u,f.x,f.y,true);fight(G,u,{blockFirst:u.hp<u.max*.4})})}
var PLAN={c5b:battle,c5c:battle,c6b:battle,
  p0:function(G){var D=G.u[0];if(!G.cs.grace)go(G,D,3,5);if(G.cs.grace){go(G,D,3,4);fight(G,D,{press:function(){return true}})}},
  p1:function(G){var D=G.u[0],f=nearestFoe(G,D);if(f)go(G,D,f.x,f.y,true);go(G,U(G,'M'),D.x+1,D.y);tendD(G,'M',4);fight(G,D,{blockFirst:D.hp<12})},
  c1:function(G){go(G,U(G,'W'),5,6);var D=G.u[0];go(G,U(G,'L'),0,5);go(G,U(G,'R'),0,4);go(G,U(G,'B'),0,3);fight(G,D,{blockFirst:D.hp<14})},
  c2:function(G){go(G,U(G,'W'),4,0);fight(G,G.u[0],{})},
  c3:function(G){var D=G.u[0];go(G,D,2,2);go(G,U(G,'W'),3,2);go(G,U(G,'M'),2,3);fight(G,D,{blockFirst:true,press:function(G,K){return K.a.hp>20}})},
  c4a:function(G){fight(G,G.u[0],{blockFirst:G.u[0].hp<16})},
  c4b:function(G){fight(G,G.u[0],{blockFirst:G.u[0].hp<20});fight(G,U(G,'H'),{blockFirst:U(G,'H').hp<16})},
  c4c:function(G){var D=G.u[0],f=nearestFoe(G,D);
    if(!f){var bx=-1;for(var x=0;x<6;x++)if(bx<0&&LH.ok(G,x,6)&&!LH.at(G,x,6))bx=x;/* nothing in the way: everyone down, the rearmost first, and the view follows */
      CP.api.mates(G).slice().sort(function(a,b){return b.y-a.y}).forEach(function(u){go(G,u,bx<0?u.x:bx,6)});return}
    go(G,D,f.x,f.y,true);['M','W','A'].forEach(function(id){var u=U(G,id);if(u)go(G,u,D.x,D.y,true)});tendD(G,'M',5);fight(G,D,{blockFirst:D.hp<16})},
  c5:function(G){var T={1:[['R',3,3],['M',4,5],['D',3,4],['A',4,6]],2:[['D',4,4],['R',4,3],['W',3,4],['M',5,5]],3:[['D',5,4],['R',5,3],['W',4,3],['A',4,5]]}[G.turn]||[];
    T.forEach(function(m){LH.move(G,U(G,m[0]),m[1],m[2])})},
  c6:function(G){var D=G.u[0];tendD(G,'M');if(!fight(G,D,{blockFirst:D.hp<24}))if(LH.canAct(D)&&!D.attacked)LH.hold(G,D)},
  c7:function(G){var D=G.u[0];tendD(G,'M',8);fight(G,D,{blockFirst:D.hp<24})}
};
function run(id,seed,plan){
  var G=CP.start(id,{seed:seed}),n=0;
  while(!G.over&&n++<40){(plan||PLAN[id])(G);endTurn(G)}
  return G;
}
var MODE={stat:null,rand:null,luck:null};
module.exports={worth:worth,MODE:MODE,LH:LH,CP:CP,U:U,bfs:bfs,go:go,hand:hand,fight:fight,tendD:tendD,endTurn:endTurn,nearestFoe:nearestFoe,battle:battle,PLAN:PLAN,run:run};
