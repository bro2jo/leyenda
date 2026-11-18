/* The campaign's rules: every mission is well formed, a simple player can finish each one, and the ways to lose are real.
   node game/test/campaign.test.js [mission id] [-v] */
var LH=require('../src/engine.js').LH,CP=require('../src/campaign.js').CP;require('../src/missions.js');
var only=process.argv[2]&&process.argv[2]!=='-v'?process.argv[2]:null,V=process.argv.indexOf('-v')>=0,fails=0,checks=0;
function ok(c,m){checks++;if(!c){fails++;console.log('  FAIL '+m)}}
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
  opt=opt||{};var K=G.clash,guard=0;
  while(K&&K.phase==='play'&&guard++<40){
    var it=LH.intent(G),inc=it.none?0:it.d*it.n,best=-1,bv=-1;
    K.hand.forEach(function(id,i){if(LH.playable(G,i))return;var c=LH.C[id],v=0;
      if(id==='turn')v=100;
      if(c.en||c.draw)v=Math.max(v,50);
      if(c.blk&&inc>K.block)v=Math.max(v,30+Math.min(c.blk,inc-K.block)+(c.halve?3:0));
      if(c.halve&&inc>K.block)v=Math.max(v,28);
      if(c.dmg){var h=LH.hitList(K,c).reduce(function(a,b){return a+b},0);if(h>0)v=Math.max(v,(opt.blockFirst&&inc>K.block?5:20)+h/Math.max(1,c.c))}
      if(c.heal&&K.a.hp<K.a.max-c.heal)v=Math.max(v,25);
      if(c.open||c.mark||c.pin)v=Math.max(v,10);
      if(v>bv){bv=v;best=i}});
    if(best<0||bv<=0)break;LH.play(G,best);K=G.clash;if(!K||K.phase!=='play')break;
  }
  K=G.clash;if(K&&K.phase==='play')LH.endHand(G);
  K=G.clash;guard=0;
  while(K&&K.phase==='choice'&&guard++<5){if(opt.press&&opt.press(G,K)){LH.pressOn(G);hand(G,opt);return}else LH.leave(G);K=G.clash}
  if(G.clash)LH.closeClash(G);
}
function fight(G,u,opt){if(!u||u.hp<=0||G.over)return false;var t=LH.targets(G,u);if(!t.length)return false;t.sort(function(a,b){return a.hp-b.hp});if(!LH.engage(G,u,t[0]))return false;hand(G,opt);return true}
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
  c1:function(G){go(G,U(G,'W'),5,6);var D=G.u[0];go(G,U(G,'R'),2,1);go(G,U(G,'L'),0,5);go(G,U(G,'B'),1,6);fight(G,D,{blockFirst:D.hp<14})},
  c2:function(G){go(G,U(G,'W'),4,0);fight(G,G.u[0],{})},
  c3:function(G){var D=G.u[0];go(G,D,2,2);go(G,U(G,'W'),3,2);go(G,U(G,'M'),2,3);fight(G,D,{blockFirst:true,press:function(G,K){return K.a.hp>20}})},
  c4a:function(G){fight(G,G.u[0],{blockFirst:G.u[0].hp<16})},
  c4b:function(G){fight(G,G.u[0],{blockFirst:G.u[0].hp<20});fight(G,U(G,'H'),{blockFirst:U(G,'H').hp<16})},
  c4c:function(G){var D=G.u[0],f=nearestFoe(G,D);if(!f)return;go(G,D,f.x,f.y,true);['M','W','A'].forEach(function(id){var u=U(G,id);if(u)go(G,u,D.x,D.y,true)});tendD(G,'M',5);fight(G,D,{blockFirst:D.hp<16})},
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
CP.ORDER.forEach(function(id){
  if(only&&only!==id)return;var M=CP.MS[id];console.log(id+' · '+M.n);
  var G=CP.start(id,{seed:7});
  ok(M.map.rows.length===LH.H&&M.map.rows.every(function(r){return r.length===LH.W}),'map is '+LH.W+' by '+LH.H);
  ok(G.u[0].id==='D','Darrow is first');
  var seen={};G.u.forEach(function(u){if(u.side===2)return;var k=u.x+','+u.y;ok(LH.ok(G,u.x,u.y),u.n+' stands on ground ('+k+')');ok(!seen[k],u.n+' shares a tile '+k);seen[k]=1;
    (u.deck||[]).forEach(function(c){ok(!!LH.C[c],'card '+c)});if(u.side===0&&u.lend){ok(!!LH.C[u.lend],'lend '+u.lend);ok(!!LH.C[u.lend+'2'],'lend '+u.lend+'2')}
    if(u.side===0&&!u.dk)ok(!u.rng,u.n+' has no deck, so must not start a fight');
    ok(Array.isArray(LH.effects(G,u)),'effects')});
  ok(typeof CP.objective(G)==='string'&&CP.objective(G).length>5,'an objective');ok(M.intro.length>=2&&M.outro.length>=2,'words before and after');
  ok(!G.over,'not over at the start');
  var wins=0,N=40,turns=0,stars=0;
  for(var s=1;s<=N;s++){var R=run(id,s*977);ok(!!R.over,'ends (seed '+s+')');ok(!!R.cs.result,'has a result');if(R.cs.result==='won'){wins++;turns+=R.turn;stars+=R.cs.stars.filter(function(x){return x[1]}).length}
    ok(R.log.every(function(l){return !/\bthe The\b|undefined|NaN/.test(l[0])}),'log reads clean: '+JSON.stringify(R.log.map(function(l){return l[0]})));
    if(V&&s===1)console.log('   ',R.cs.result,R.over.t,'| turn',R.turn,'| D',R.u[0].hp+'/'+R.u[0].max,'|',JSON.stringify(R.cs.stars),'\n   ',R.log.map(function(l){return l[0]}).join(' / '))}
  console.log('   simple player wins '+wins+'/'+N+(wins?' · about '+(turns/wins).toFixed(1)+' turns, '+(stars/wins).toFixed(1)+' stars':''));
  ok(wins>=N*.5,'a simple player can finish it at least half the time ('+wins+'/'+N+')');
  /* doing nothing must not win, where there is a way to lose */
  if(M.lose){var I=run(id,5,function(){});ok(!I.over||I.cs.result!=='won'||id==='c4b'||id==='c7','standing still does not win: '+(I.cs.result||'still going'))}
});
/* someone a mission holds to his place has no move at all: not even the step back through a friend that the game allows */
CP.ORDER.forEach(function(id){if(only&&only!==id)return;var G=CP.start(id,{seed:2});G.u.forEach(function(u){if(u.side===0&&u.hp>0&&!(u.mov>0))ok(Object.keys(LH.reach(G,u)).length===1,id+': '+u.n+' cannot move, and has nowhere to move to')})});
console.log(fails?fails+' of '+checks+' checks failed':'all '+checks+' checks passed');process.exit(fails?1:0);
