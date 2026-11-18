/* The campaign's rules: every mission is well formed, a simple player can finish each one, and the ways to lose are real.
   node game/test/campaign.test.js [mission id] [-v] */
var B=require('./campaign.bots.js'),LH=B.LH,CP=B.CP,U=B.U,bfs=B.bfs,go=B.go,hand=B.hand,fight=B.fight,tendD=B.tendD,endTurn=B.endTurn,nearestFoe=B.nearestFoe,battle=B.battle,PLAN=B.PLAN,run=B.run;
var only=process.argv[2]&&process.argv[2]!=='-v'?process.argv[2]:null,V=process.argv.indexOf('-v')>=0,fails=0,checks=0;
function ok(c,m){checks++;if(!c){fails++;console.log('  FAIL '+m)}}
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
  /* and no two plays open quite alike: across the seeds a foe's first answer is not always the same number */
  if(M.vary!==0&&(M.foes||[]).some(function(f){return !CP.FD[f.k].scripted})){var firsts={};for(var q=1;q<=12;q++){var Q=CP.start(id,{seed:q*101});Q.u.forEach(function(u){if(u.side===1&&u.hp>0&&!u.scripted)firsts[u.type+':'+u.ai+':'+u.ans[0].d]=1})}ok(Object.keys(firsts).length>1,'its foes do not open the same way every time')}
  /* doing nothing must not win, where there is a way to lose */
  /* doing nothing never wins, anywhere: not by waiting out a clock, not by nightfall */
  [5,6,7].forEach(function(sd){var I=run(id,sd,function(){});ok(I.cs.result!=='won','ending every turn without a move does not win ('+(I.cs.result||'still going')+')')});
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
  ok(H.deck.join()==='b_strike,b_strike,b_guard,b_guard,hew_3,hew_3,fast_2,fast_2,bellow'&&W.deck.filter(function(c){return c==='stone_2'}).length===3&&A.deck.indexOf('legs')>=0&&H.dk.draw.length===9,'a pick raises every copy of that card, never past the third rank, and only that fighter\'s');
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
  ok(CP.goals(F).some(function(m){return m[2]==='find'})&&LH.move(F,FA,f0.x,f0.y)&&f0.got===1&&F.cs.found===1&&F.u[0].deck.length===n0+1&&['c_bar','c_stick','c_still3'].indexOf(F.u[0].dk.draw[F.u[0].dk.draw.length-1])>=0&&!CP.goals(F).some(function(m){return m[2]==='find'}),'a friend who reaches his stick sends it to the top of his pile, once');
  ['c5b','c5c','c6b','c4c'].forEach(function(id){var g=CP.start(id,{seed:1});ok(g.cs.finds.length>=1&&g.cs.finds.every(function(f){return LH.ok(g,f.x,Math.min(6,f.y))||f.y>6}),id+' has something to reach, on ground that can be stood on')});
  /* a fighter's deck: the basics everyone carries under the cards that are that fighter's own, nine deep, so the draw matters for them too */
  Object.keys(CP.KIT).forEach(function(id){var k=CP.KIT[id],basics=k.filter(function(c){return C[c].basic}).length;
    ok(k.length===9&&basics>=3&&basics<=4&&CP.GROW[id].every(function(c){return k.indexOf(c)>=0})&&k.indexOf('b_strike')>=0&&k.indexOf('b_guard')>=0,id+': nine cards, three or four of them the shared Strike and Guard, the rest that fighter\'s own')});
  var KG=CP.start('c5b',{seed:4});ok(['H','A','W'].every(function(id){var u=U(KG,id);return u.deck.slice().sort().join()===CP.KIT[id].slice().sort().join()&&u.hn<u.deck.length/2}),'in a mission each of them fights from that deck, and a hand is less than half of it');
  /* combos: a card that wants something first is played as its stronger twin when it has it, and goes back in the pile as itself */
  Object.keys(CP.COMBO).forEach(function(id){ok(C[id+'_c']&&C[id+'_c'].combo&&LH.cardText(id).indexOf(CP.COMBO[id].text)>=0,id+' says on the card what it wants')});
  var CG=CP.start('c5b',{seed:3}),CH=U(CG,'H'),CS=CG.u.filter(function(u){return u.type==='pike'})[0];CS.x=CH.x;CS.y=CH.y-1;CG.u.forEach(function(u){if(u!==CS&&u.x===CS.x&&u.y===CS.y)u.x=5});CS.hp=CS.max=60;
  var CK=LH.engage(CG,CH,CS);CK.hand=['hew','fast','hew'];CK.en=5;CK.fb=0;var f1=LH.play(CG,0),d1=f1.filter(function(e){return e.k==='dmg'})[0].n;
  ok(d1===8&&CP.eff(CK,'hew')==='hew','with no block up, a Hew is a plain Hew');LH.play(CG,0);ok(CP.eff(CK,'hew')==='hew_c'&&/Combo/.test(LH.cardText('hew',CK)),'with Stand Fast played, the Hew in his hand reads as its combo');
  var f2=LH.play(CG,0);ok(f2[0].k==='status'&&f2[0].t==='Combo'&&f2.filter(function(e){return e.k==='dmg'})[0].n===12&&CH.dk.disc.indexOf('hew_c')<0&&CH.dk.disc.filter(function(c){return c==='hew'}).length===2&&CG.cs.tips.indexOf('combo')>=0,'played then, it lands for 12, is called a combo, and goes to the pile as a plain Hew');
  var AG=CP.start('c5b',{seed:3}),AA=U(AG,'A'),AS=AG.u.filter(function(u){return u.type==='pike'})[0];AS.x=AA.x;AS.y=AA.y-1;AG.u.forEach(function(u){if(u!==AS&&u.x===AS.x&&u.y===AS.y)u.x=5});AS.hp=AS.max=60;
  var AK=LH.engage(AG,AA,AS);AK.hand=['worry','legs'];AK.en=5;AK.fb=0;LH.play(AG,0);var f3=LH.play(AG,0);ok(f3[0].t==='Combo'&&f3.filter(function(e){return e.k==='dmg'})[0].n===15,'Worry, then Take the Legs: 10 on an Open foe, and half again for the opening');
  /* a find is a gamble: what it holds is drawn from its pool, and is not the same every time */
  ['c5b','c5c','c6b'].forEach(function(id){var seen={};for(var sd=1;sd<=40;sd++){var g=CP.start(id,{seed:sd*53}),f=g.cs.finds[0],u=g.u.filter(function(x){return x.side===0&&x.hp>0&&x.id!=='D'&&!x.still&&x.mov>=2})[0];
      var nb=[[1,0],[-1,0],[0,1],[0,-1]].map(function(d){return [f.x+d[0],f.y+d[1]]}).filter(function(q){return LH.ok(g,q[0],q[1])})[0];g.u.forEach(function(x){if(x!==u&&x.side!==2&&((x.x===nb[0]&&x.y===nb[1])||(x.x===f.x&&x.y===f.y))){x.x=0;x.y=0}});
      u.x=nb[0];u.y=nb[1];u.moved=false;u.attacked=false;u.mov=3;LH.move(g,u,f.x,f.y);var fa=g.cs.finds[0];if(fa.got)seen[fa.card||(fa.heal?'rest':fa.insp?'luck':'?')]=1}
    ok(Object.keys(seen).length>=3&&!seen['?'],id+': what its find holds is one of several things ('+Object.keys(seen).join(', ')+')')});
  /* a deeper deck: three more plain cards, never an Art, so that the draw matters */
  CP.ORDER.forEach(function(id){var M=CP.MS[id],base=(M.party.D.deck||[]),D=CP.start(id,{seed:1,pack:[]}).u[0],dk=D.deck||[];if(M.deep===0||base.length<9){ok(dk.length===base.length,id+': a short or scripted deck is left as it is');return}
    var extra=dk.slice(base.length);ok(dk.length===base.length+CP.DEEP&&extra.every(function(c){return !C[c].r&&!C[c].ex&&base.indexOf(c)>=0}),id+': his deck is three plain cards deeper ('+extra.join(', ')+')')});
  /* and luck is worth having: held to the bad side hand after hand, the planned player does worse than held to the good side */
  var lw=0,uw=0,MD=require('./campaign.bots.js').MODE;['c4a','c6','c5c'].forEach(function(id){for(var sd=1;sd<=25;sd++){MD.luck='best-cycle';if(run(id,sd*37+11).cs.result==='won')lw++;MD.luck='worst-cycle';if(run(id,sd*37+11).cs.result==='won')uw++}});MD.luck=null;
  console.log('luck held to one side, three missions: '+lw+'/75 won with the best of the pile each hand, '+uw+'/75 with the worst');ok(lw>uw+5,'bad draws time after time lose more often than good ones ('+uw+' against '+lw+')');
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
