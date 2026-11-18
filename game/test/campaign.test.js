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
/* the fire: what he buys with stars goes into the fights told larger than the page, and nowhere else */
(function(){if(only)return;var C=LH.C,T=CP.ORDER.filter(function(id){return !!CP.MS[id].tall});
  ok(CP.PACK===3&&CP.SHOP.length>=12&&CP.SHOP.every(function(id){return C[id]&&C[id].p>0&&!C[id].spoil&&!C[id].spoilKill}),'the fire offers camp cards, and none that only pay spoils');
  ok(T.length===3,'three fights are told larger than the page');
  T.forEach(function(id){var base=CP.start(id,{seed:1}).u[0].deck.length,G=CP.start(id,{seed:1,pack:['digin','bloodup','callco','twice','spoils']}),D=G.u[0];
    ok(D.deck.length===base+3&&D.deck.indexOf('digin')>=0&&D.deck.indexOf('bloodup')>=0&&D.deck.indexOf('callco')>=0&&D.deck.indexOf('twice')<0,id+': the pack goes in, three cards and no more');
    ok(D.dk.draw.length===D.deck.length,id+': and is shuffled into the pile');
    var kinds={},trees={};G.u.forEach(function(u){if(u.side===1&&u.hp>0){kinds[u.type]=1;trees[u.t]=1}});
    ok(Object.keys(kinds).length>=3&&Object.keys(trees).length>=2,id+': more than one kind of foe, of more than one tree ('+Object.keys(kinds).join(', ')+')');
    ok(G.u.some(function(u){return u.side===1&&u.rally}),id+': one of them makes the others strike harder');
    ok(D.deck.indexOf('c_far1')>=0,id+': he has the Far Cast, learned under the House')});
  CP.ORDER.filter(function(id){return !CP.MS[id].tall}).forEach(function(id){var a=CP.start(id,{seed:1}).u[0].deck||[],b=CP.start(id,{seed:1,pack:['digin','bloodup']}).u[0].deck||[];ok(a.join()===b.join(),id+': the page\'s own scene keeps the page\'s deck')});
  /* difficulty: one step on what a foe deals and how long a man stands; the length of an ordeal is the page's */
  var n0=CP.start('c5b',{seed:1}),h1=CP.start('c5b',{seed:1,level:1}),g1=CP.start('c5b',{seed:1,level:-1}),s0=n0.u.filter(function(u){return u.type==='sergeant'})[0],s1=h1.u.filter(function(u){return u.type==='sergeant'})[0],sg=g1.u.filter(function(u){return u.type==='sergeant'})[0];
  ok(s1.atk===s0.atk+2&&s1.max>s0.max&&s1.ans[0].d===s0.ans[0].d+2,'Hard: a foe strikes 2 harder and stands longer');ok(sg.atk===s0.atk-2&&sg.max<s0.max&&sg.ans[0].d===s0.ans[0].d-2,'Gentle: the other way');
  var o0=CP.start('p1',{seed:1}),o1=CP.start('p1',{seed:1,level:1}),a0=o0.u.filter(function(u){return u.ordeal})[0],a1=o1.u.filter(function(u){return u.ordeal})[0];
  ok(a1.max===a0.max&&a1.ans[0].d===a0.ans[0].d+2,'an ordeal is no longer on Hard, only harder on him');
  CP.ORDER.forEach(function(id){var G=CP.start(id,{seed:1,level:-1});ok(G.u.every(function(u){return u.side!==1||(u.atk>=0&&u.ans.every(function(x){return x.d>=1}))}),id+': Gentle never takes a blow below 1')});
  /* what he is told: every mission's news reads clean, the shelf fills one card a mission, the story's beats are said aloud */
  CP.ORDER.forEach(function(id,i){var l=CP.news(id);ok(l.every(function(x){return x.t&&!/undefined|NaN|\bthe The\b/.test(x.t)})&&(i>0||!l.length),id+': its news reads clean ('+l.length+' lines)')});
  ok(CP.news('c5b').some(function(x){return x.k==='join'&&x.who==='Ash'})&&CP.news('c4b').some(function(x){return x.k==='join'&&/Hollis stands with him now/.test(x.t)}),'someone new beside him is announced, and someone who was only watching before is said to stand with him now');
  ok(CP.news('p1').some(function(x){return x.k==='lost'})&&CP.news('c2').some(function(x){return x.k==='card'&&/risen to/.test(x.t)}),'the Grace lost and an Art risen are both news');
  var gifts=Object.keys(CP.GIFT).map(function(k){return CP.GIFT[k]});ok(Object.keys(CP.GIFT).length===CP.ORDER.length&&gifts.every(function(c,j){return CP.SHOP.indexOf(c)>=0&&gifts.indexOf(c)===j})&&gifts.length+CP.STARGIFT.length===CP.SHOP.length,'each mission leaves one card at the fire, none twice, and stars open the rest');
  var dn={};ok(CP.shelf(dn).length===0,'the shelf is empty before the first mission');CP.ORDER.forEach(function(id){dn[id]={stars:3}});ok(CP.shelf(dn).length===CP.SHOP.length,'and full when every mission is told with every star');
  var W=CP.start('c1',{seed:1});W.cs.toasts.length=0;CP.api.log(W,'The wicket shuts.','good');CP.api.log(W,'A quiet line.','dimm');ok(W.cs.toasts.length===1&&W.cs.toasts[0].t==='The wicket shuts.','a beat of the story is said aloud; a quiet line is only logged');
  var E=CP.start('c5b',{seed:1}),ED=E.u[0],ES=E.u.filter(function(u){return u.type==='sergeant'})[0];ES.x=ED.x;ES.y=ED.y-1;E.u.forEach(function(u){if(u!==ES&&u.x===ES.x&&u.y===ES.y)u.x=5});LH.engage(E,ED,ES);
  ok(E.cs.tips.indexOf('brk')>=0&&E.cs.tips.indexOf('enrage')>=0&&E.cs.tips.indexOf('ordeal')<0,'a fight notes the rules that matter in it, each once');
  /* words */
  ok(CP.say(CP.start('p1',{seed:1}),'Their turn')==='Time passes'&&CP.say(CP.start('c5b',{seed:1}),'Their turn')==='Their turn','against a hall, time passes; against men, it is their turn');
  ok(CP.say(CP.start('c5b',{seed:1}),'Banner')==='The horn'&&CP.say(CP.start('c5c',{seed:1}),'The banner is up: he strikes 2 harder.').indexOf('A name is being read')===0,'what rallies them is named for the mission');
  /* a full pack should help in the hardest of them */
  var w0=0,w1=0,N=30;for(var sd=1;sd<=N;sd++){var A=CP.start('c5b',{seed:sd*13+5}),n=0;while(!A.over&&n++<40){PLAN.c5b(A);endTurn(A)}if(A.cs.result==='won')w0++;
    var B=CP.start('c5b',{seed:sd*13+5,pack:['hewT','follow','closeup']});n=0;while(!B.over&&n++<40){PLAN.c5b(B);endTurn(B)}if(B.cs.result==='won')w1++}
  console.log('the yard, simple player: '+w0+'/'+N+' with the page\'s deck, '+w1+'/'+N+' with Hollis\'s Hew, Follow Through and Close Up in the pack');ok(w1>=w0,'a pack from the fire does not make the yard harder ('+w0+' -> '+w1+')');
})();
/* growing by cards, words between friends, things to reach, the long stair, and a board picked up again */
(function(){if(only)return;var C=LH.C;
  Object.keys(CP.GROW).forEach(function(id){CP.GROW[id].forEach(function(c){ok(C[c]&&C[c+'_2']&&C[c+'_3']&&C[c+'_2'].r==='II'&&C[c+'_3'].base===c&&LH.cardText(c+'_3')!==LH.cardText(c),id+': '+c+' has a second and a third rank that read differently')})});
  ok(CP.levelOf(0)===0&&CP.levelOf(3)===1&&CP.levelOf(12)===3&&CP.levelOf(99)===CP.LEVELS.length&&CP.LEVELS.length===6,'marks buy up to six ranks: every card of a fighter\'s to its third');
  var G=CP.start('c5b',{seed:1,grow:{H:['hew','hew','hew','fast'],W:['stone']}}),H=U(G,'H'),W=U(G,'W'),A=U(G,'A');
  ok(H.deck.join()==='hew_3,hew_3,fast_2,fast_2,bellow'&&W.deck.filter(function(c){return c==='stone_2'}).length===2&&A.deck.indexOf('legs')>=0&&H.dk.draw.length===5,'a pick raises every copy of that card, never past the third rank, and only that fighter\'s');
  var D=G.u[0],S=G.u.filter(function(u){return u.type==='pike'})[0];S.x=H.x;S.y=H.y-1;G.u.forEach(function(u){if(u!==S&&u.x===S.x&&u.y===S.y)u.x=5});S.hp=1;var K1=LH.engage(G,H,S);K1.hand=['hew_3'];K1.fb=0;LH.play(G,0);LH.closeClash(G);
  ok(G.earn.marks.H===2&&G.cs.tally.Hollis&&G.cs.tally.Hollis.k===1,'a fight is a mark, a foe felled is another, and the mission keeps the tally');
  var B=CP.start('c5b',{seed:2,bond:{Maelis:CP.BOND1,Hollis:CP.BOND2}}),BD=B.u[0],BS=B.u.filter(function(u){return u.type==='pike'})[0];BS.x=BD.x;BS.y=BD.y-1;B.u.forEach(function(u){if(u!==BS&&u!==BD&&u.x===BS.x&&u.y===BS.y)u.x=5});
  CP.bond={Maelis:CP.BOND1,Hollis:CP.BOND2};var K=LH.engage(B,BD,BS);CP.bond={};
  ok(K.hand.indexOf('c_now2')>=0&&K.block>=2&&B.earn.bond.Hollis===1&&B.earn.bond.Maelis===1,'a first bond brings the friend\'s lent card already risen, a second gives him block, and each fight together counts toward both');
  /* the words are the page's own */
  var fs=require('fs'),path=require('path'),dir=path.resolve(__dirname,'../../saga/chronicle'),page=fs.readdirSync(dir).filter(function(f){return /\.md$/.test(f)}).map(function(f){return fs.readFileSync(path.join(dir,f),'utf8')}).join(' ');
  Object.keys(CP.BONDS).forEach(function(n){ok(page.indexOf(CP.BONDS[n][0])>=0,'the words by the fire for '+n+' are on the page as written')});
  /* things to reach */
  var F=CP.start('c6b',{seed:1}),FA=U(F,'A'),f0=F.cs.finds[0],n0=F.u[0].deck.length;FA.x=f0.x;FA.y=f0.y-1;F.u.forEach(function(u){if(u!==FA&&u.x===FA.x&&u.y===FA.y)u.y=6});
  ok(CP.goals(F).some(function(m){return m[2]==='find'})&&LH.move(F,FA,f0.x,f0.y)&&f0.got===1&&F.cs.found===1&&F.u[0].deck.length===n0+1&&F.u[0].dk.draw[F.u[0].dk.draw.length-1]==='c_bar'&&!CP.goals(F).some(function(m){return m[2]==='find'}),'a friend who reaches his stick sends it to the top of his pile, once');
  ['c5b','c5c','c6b','c4c'].forEach(function(id){var g=CP.start(id,{seed:1});ok(g.cs.finds.length>=1&&g.cs.finds.every(function(f){return LH.ok(g,f.x,Math.min(6,f.y))||f.y>6}),id+' has something to reach, on ground that can be stood on')});
  /* the long stair */
  var L=CP.start('c4c',{seed:1}),Wd=CP.MS.c4c.world;ok(Wd.rows.length===21&&Wd.rows.every(function(r){return r.length===6})&&L.cs.ahead.length===3&&CP.api.foes(L).length===1,'the Steps are three boards long, and only what is in view is on the board');
  L.u.forEach(function(u){if(u.side===1)u.hp=0});L.u.forEach(function(u,i){if(u.side===0){u.x=i%6;u.y=u.id==='D'?5:3}});var k=CP.march(L);
  ok(k===3&&L.cs.top===3&&L.map.rows.join()===Wd.rows.slice(3,10).join()&&L.u[0].y===2&&L.map.name.replace(/\u200b/g,'')==='The Thousand Steps'&&L.map.name!=='The Thousand Steps','the view follows the company down by as far as the rearmost has come');
  ok(CP.api.foes(L).some(function(u){return u.type==='reach'&&u.y===4})&&L.cs.ahead.length===2&&L.cs.finds[0].y===3,'what was ahead comes onto the board where it stands, and what is to be found moves with the ground');
  /* a board set down and picked up again plays on exactly as it would have */
  ['c5b','c4c','c1'].forEach(function(id){var a=CP.start(id,{seed:9}),n=0;while(!a.over&&n++<3){PLAN[id](a);endTurn(a)}
    var b=JSON.parse(JSON.stringify(a));CP.resumeG=b;var c=LH.newRun({});ok(c===b&&c.ms===id,'a saved board comes back through the same door');
    n=0;while(!a.over&&n++<40){PLAN[id](a);endTurn(a)}n=0;while(!c.over&&n++<40){PLAN[id](c);endTurn(c)}
    ok(a.over&&c.over&&a.cs.result===c.cs.result&&a.turn===c.turn&&a.u[0].hp===c.u[0].hp,id+': picked up again, it ends as it would have ('+a.cs.result+', turn '+a.turn+')')});
})();
/* someone a mission holds to his place has no move at all: not even the step back through a friend that the game allows */
CP.ORDER.forEach(function(id){if(only&&only!==id)return;var G=CP.start(id,{seed:2});G.u.forEach(function(u){if(u.side===0&&u.hp>0&&!(u.mov>0))ok(Object.keys(LH.reach(G,u)).length===1,id+': '+u.n+' cannot move, and has nowhere to move to')})});
console.log(fails?fails+' of '+checks+' checks failed':'all '+checks+' checks passed');process.exit(fails?1:0);
