/* The Line and the Hand: the campaign's missions. One for each thing the Chronicle's page has shown him do with his body,
   in the order the page shows it. Reader-safe: every name, place and line here is on the page already (saga/chronicle/).
   A mission is added only after its chapter is closed. Words in double quotes inside the texts are the page's own.
   People, places and things are the Chronicle's. The fights need not be: a mission marked `tall` tells a scene larger than the page
   does (a search that comes to pikes, riders the forms do not hold), says so on its card, and says afterwards how the page has it.

   Map letters: . floor/ground  w cover (2 steps)  d road/steps  ~ wall or deep water  f ford/ice (2 steps)  b bridge/door
   Darrow's reach on the board follows the Knots the page has tied; his cards carry the rank each Art had in that chapter. */
(function(root,CP){
'use strict';
var LH=(typeof window!=='undefined'&&window.LH)||require('./engine.js').LH;
function rep(id,n){var a=[];while(n-->0)a.push(id);return a}
function deck(){var a=[];for(var i=0;i<arguments.length;i++)a=a.concat(arguments[i]);return a}
var STILL={still:1,deck:null};
function a_tends(G){var m=CP.api.U(G,'M');return m?m.tends:0}
function LH_at(G,x,y){for(var i=0;i<G.u.length;i++){var u=G.u[i];if(u.hp>0&&u.x===x&&u.y===y)return u}return null}

/* ================= PROLOGUE: THE THREE HEARTBEATS ================= */
CP.add({id:'p0',book:'Prologue',ch:'The Three Heartbeats',n:'The Grace',place:'Harrow Ford, on the Wend',when:'Midsummer. The river in spate.',art:'harrow-ford',
  level:'Knight-Captain of the Ninth Lance',quote:'"Ride wide today."',
  intro:['Sixty knights behind him, sixty squires behind them, and the banners hanging wet on their poles. At his left hand, close enough to touch, sits Aldric Vane.',
    'The field-stones have come up on their carts. Kneel at the Ninth\'s, as he always does, and the Crown\'s hand is on his back: every ache quiet, the morning sharp at its edges.',
    'The writ says clear the ford.'],
  objective:function(G,S){return S.frost?'Halfway across, the warmth goes out of him.':S.grace?'Clear the ford. With the Grace in him the river is a road.':'Walk to the Ninth\'s field-stone and kneel.'},
  open:'The Wend is running high for midsummer, brown with three days of rain.',
  map:{name:'Harrow Ford',theme:'ford',rows:['.w..w.','......','~~~f~~','~~~f~~','......','...d..','...d..']},
  rounds:2,vary:0,deep:0,pro:'it',say:[[/Darrow falls back\./g,'He goes under.'],[/^wound$/g,'frost'],[/\bstrikes\b/g,'pulls'],[/\bstrike\b/g,'pull'],[/A Wound cannot be played\. It is gone after the battle\./g,'There is nothing in it. The warmth is gone.'],[/\banswer\b/g,'pull']],
  party:{D:{at:[3,6],t:'blade',mov:1,hp:58,br:3,hn:5,throws:0,far:0,img:'darrow0',
      deck:deck(rep('g_thunder',2),rep('g_turning',2),rep('g_stoop',2),rep('g_anchor',2),rep('g_quick',2)),first:['g_thunder','g_anchor','g_turning','g_quick','g_stoop','g_thunder','g_turning']},
    H:{at:[5,6],still:1,deck:null,img:'hollis0',lend:'lH'},
    more:[{id:'V',from:'W',n:'Aldric',img:'aldric',t:'blade',hp:40,still:1,deck:null,lend:'c_wide',at:[2,6]}]},
  foes:[{k:'wend',at:[3,3]}],
  marks:function(G,S){return S.grace?[[3,3,'go']]:[[3,5,'go']]},
  labels:[[3,5,'Stone','The Ninth\'s field-stone','Kneel here, and the Crown\'s hand is on his back.'],[3,3,'Ford']],
  on:{
    start:function(G,S,a){a.hint(G,'Tap Darrow. Then tap the field-stone, one step ahead.')},
    moved:function(G,S,a,u){if(u.id==='D'&&!S.grace&&a.on(u,3,5))grace(G,S,a,true)},
    before:function(G,S,a){if(!S.grace)grace(G,S,a,false)},
    engage:function(G,S,a,K){if(S.hands)frost(G,S,a,K);else a.hint(G,'Play the hand. Tap a card to read it, tap again to play it. Block soaks the river\'s pull.');S.hands=(S.hands||0)+1},
    round:function(G,S,a,K){frost(G,S,a,K)},
    play:function(G,S,a,id){if(id==='turn'){S.fall=1;a.hint(G,'And the knee goes. Nothing touched him.');return [{k:'status',who:'a',t:'The knee goes'}]}},
    clashEnd:function(G,S,a){if(!S.frost)a.hint(G,'The far bank is still theirs. Go at the ford again.')}
  },
  fallen:function(G,S){return S.frost?'won':'lost'},
  win:{t:'The third heartbeat',s:'He spent it underwater.',somber:1},
  lose:{any:{t:'The writ says clear the ford',s:'And he has not ridden at it.'}},
  stars:function(G,S){return [['Knelt at the stone',!!S.knelt],['Rode at the ford',!!S.hands],['Turned for Tobin',!!S.fall]]},
  outro:['On the first heartbeat, frost bloomed on the rings of his mail, in midsummer. On the second, Tobin Marsh went under his own horse, and Darrow planted his left foot and turned, and the knee went. Nothing touched him.',
    'A hand hauled him east, onto the gravel among the standing stones. The red-handed woman turned his head toward the river. "Look at it. Look. Remember it."',
    'On the west bank the Second Lance sat its horses in perfect order, untouched, watching. Nineteen of the Ninth came home.'],
  read:'Prologue, I. Harrow Ford'});
function grace(G,S,a,knelt){
  var D=G.u[0];S.grace=1;S.knelt=knelt?1:0;D.br=5;D.mov=5;D.moved=false;D.from=null;
  a.log(G,knelt?'The stone is cold, and then it isn\'t. He gets up, and the Ninth is full of Grace.':'He has knelt at the stone as he always does, without thinking about it.','good');
  a.hint(G,'The Grace is in him: 5 breath a hand. Walk to the water and tap the ford to ride at it.');
}
function frost(G,S,a,K){
  S.frost=1;K.hand=['frost','frost','turn','frost'];K.en=0;K.block=0;K.intent={b:0,d:99,n:1};
  a.hint(G,'Tobin Marsh has gone under his horse. Every instinct he owns says: turn.');
}

/* Six weeks, and a knee that floods if he asks too much of it: every Step swells it, a week or the Mender's hand brings it down.
   Too slow and the weeks run out; too fast and he spends one on his back. */
var WEEKS=6,FLOOD=3;
CP.add({id:'p1',book:'Prologue',ch:'The Three Heartbeats',n:'The Binding',place:"Saint Ysolde's, the House of Menders",when:'Six weeks on his back.',art:'saint-ysoldes',
  level:'Level 1 · Bound',quote:'"It isn\'t broken. It\'s undone."',
  intro:['They carried him up the Thousand Steps on a litter, with a girl counting every one aloud. There are eleven hundred and seventeen.',
    'Maelis Vorne will not touch the knee for six weeks. "You don\'t bind a river in flood. The swelling comes down first. The leg straightens first. Strength before the Binding, because a Binding takes the measure of whatever you tie it to."',
    'So he learns to walk the length of the hall with a stick, then without one: six weeks to do it in, on a knee that floods if he asks too much of it. Hollis watches from the next cot and offers commentary.'],
  objective:function(G,S,a){return (a.foe(G,'hall1')?'Walk the length of the hall with the stick, then without it,':'Now without the stick,')+' before the six weeks are out. Do not let the knee flood.'},
  top:function(G){return 'Week '+Math.min(G.turn,WEEKS)+' of '+WEEKS+' · swelling '+(G.cs.sw||0)+' of '+FLOOD},
  open:'The infirmary hall is dark except for her candle and the long double row of cots.',
  map:{name:'The Infirmary Hall',theme:'hall',rows:['~~..~~','~~..~~','~~..~~','~~..~~','~~..~~','~~..~~','~...~~']},
  pro:'it',down:'is walked',say:[[/\bstrikes\b/g,'tells'],[/\bstrike\b/g,'tell'],[/\b(his|its) answer/g,'the leg']],
  party:{D:{at:[2,6],t:'foot',mov:1,hp:24,br:2,hn:4,throws:0,far:0,img:'darrow1',deck:deck(rep('c_step',5),rep('c_brace',3))},
    H:{at:[1,6],still:1,deck:null,img:'hollis1',lend:'lH'},
    more:[{id:'M',from:'R',n:'Maelis',role:'the Mender',img:'maelis1',mov:2,tend:4,tends:3,lend:'c_now',at:[3,6]}]},
  foes:[{k:'hall1',at:[2,4]},{k:'hall2',at:[2,3]}],
  chips:function(G,S){var n=S.sw||0;return [['a','wound','Swelling '+n+' of '+FLOOD,'Each Step swells the knee by one. A new week takes one down, and so does the Mender\'s hand. One more than '+FLOOD+' floods it: he loses a week.',n>=FLOOD?'bad':'plain',n]]},
  on:{
    start:function(G,S,a){S.sw=0;a.hint(G,'Each Step swells the knee by one. A new week takes one down, and so does the Mender\'s hand: tap her, then him. Past '+FLOOD+' it floods, and he loses a week. Maelis beside him lends a card.')},
    play:function(G,S,a,id){var c=LH.C[id]||{};if((c.base||id)!=='c_step')return;S.sw=(S.sw||0)+1;
      if(S.sw>FLOOD){var D=G.u[0];S.sw=2;S.flood=(S.flood||0)+1;S.bed=G.turn+1;D.hp=Math.max(1,D.hp-4);
        a.log(G,'The knee floods. "You don\'t bind a river in flood," says Maelis.','hurt');return [{k:'status',who:'a',t:'Flooded'}]}},
    tended:function(G,S,a,u,t){if(t&&t.id==='D'&&S.sw>0){S.sw--;a.log(G,'Her two first fingers on the joint. The swelling comes down a little.','good')}},
    clashEnd:function(G,S,a,K){if(K.d.hp<=0&&K.d.type==='hall1'){a.log(G,'He leaves the stick against the last cot.','good');a.hint(G,'Now without it. The leg tells harder here: Brace when it does, and mind the swelling.')}},
    turn:function(G,S,a,t){var D=G.u[0];S.sw=Math.max(0,(S.sw||0)-1);
      if(S.bed===t&&D.hp>0){D.attacked=true;D.moved=true;D.free=false;a.log(G,'A week on his back with his heel on a rolled blanket, letting the weight of the leg pull it straight.','hurt')}
      if(t===3)a.log(G,'From the next cot Hollis, still mostly drunk, offers commentary.','dimm')}
  },
  fail:function(G,S){return G.turn>WEEKS?'late':''},
  goal:function(G,S,a){return !a.foe(G,'hall1')&&!a.foe(G,'hall2')},
  win:{t:'The length of the hall',s:'With a stick, then without one.'},
  lose:{late:{t:'"Bring me a weak leg"',s:'"and I\'ll give you a weak knee." She shuts the box, and waits for the leg to come straight.'},
    any:{t:'Not today',s:'Some days he does the dull things and nothing happens. He does them again the next day anyway.'}},
  stars:function(G,S){return [['Walked the hall',true],['The knee never flooded',!S.flood],['With a week to spare',G.turn<WEEKS]]},
  outro:['On the last night Maelis sits down on the end of his cot with a wooden box on her knees. Inside, on black cloth: a curved needle, and a spool that glows the deep orange of a coal when you blow on it.',
    '"It\'ll be exactly as strong as you make it, and not one hair stronger."',
    '"Do it," he says. The emberthread goes in like warmth poured into a cold cup. "Time makes it possible. Proof makes it permitted."'],
  read:'Prologue, III. The Binding'});

/* ================= BOOK I: THE HOUSE OF MENDERS ================= */
/* Two things, and both must be done. The wicket: he shuts it with his hand of cards, and every turn it stands open another grey
   cloak puts down one of those lending him a shoulder; with nobody left beside him, the next is through. The bell: Wren runs for
   the tower, and the two already inside walk for the stair; only Old Mercy stops them. */
var PULLS=2,STAIR=[[0,6],[1,6]];
CP.add({id:'c1',book:'Book I · The House of Menders',ch:'Chapter 1 · The Confessor at the Steps',n:'The Wicket',place:"The gate of Saint Ysolde's",when:'Dusk. Snow in the court.',art:'saint-ysoldes',
  level:'Level 4 · Bound',quote:'"Wren. Now."',
  intro:['Five grey cloaks have come to the bars with a list. Confessor Ivo Marrant reads it there, and the first name on it is Darrow\'s.',
    'While Old Mercy rings, no blade passes the gate and no name under it is taken down against its will. But the bell has not rung, and the wicket has just gone back on its hinges with a third man\'s shoulder in the gap.',
    'Two are inside already, walking toward the wounded the way men walk a market looking for one stall. He puts his shoulder to the wicket, and there are shoulders beside his. Wren can reach the tower.'],
  objective:function(G,S,a){var n=beside(G,a).length;
    return (S.shut?'The wicket is shut. ':'Shut the wicket on the third man. '+(n?n+' beside him to be put down first.':'Nobody is beside him: the next grey cloak is through.')+' ')+
      (S.rung?'Old Mercy is ringing.':S.pull?'Pell has the rope: hold on.':'Get Wren to the tower door before the two inside reach the stair.')},
  top:function(G){var S=G.cs;return 'Turn '+G.turn+' · '+(S.rung?'the bell rings':S.pull?'the rope is in Pell\'s hands':'the bell has not rung')},
  open:'Two grey cloaks put their shoulders to the wicket, and it goes back on its hinges.',
  map:{name:'The Court at Dusk',theme:'court',rows:['~~~f~~','......','......','......','..ww..','......','dd...b']},
  down:'is put back out',idle:'',insp:1,
  party:{D:{at:[3,1],t:'foot',mov:1,hp:30,br:2,hn:4,throws:0,far:0,img:'darrow1',deck:deck(rep('c_shoulder',3),rep('c_brace',2),['c_still2','c_mend1','c_eye2','c_breath1'])},
    W:{at:[2,2],rng:0,deck:null,img:'wren1'},
    R:{at:[2,1],mov:2,tend:0,tends:0,img:'rae1',lend:'c_raesh'},
    more:[{id:'B',from:'W',n:'Gate-ward',img:'brother',t:'foot',hp:20,mov:2,rng:0,deck:null,lend:'c_bro',at:[4,1]},
      {id:'L',from:'W',n:'Lay Brother',img:'brother',t:'foot',hp:20,mov:2,rng:0,deck:null,lend:'c_bro',at:[3,2]}]},
  foes:[{k:'doorman',at:[3,0]},{k:'seeker',at:[1,1]},{k:'seeker',at:[4,2]}],
  marks:function(G,S){var m=STAIR.map(function(q){return [q[0],q[1],'keep']});if(!S.pull)m.push([5,6,'go']);return m},
  labels:[[3,0,'Wicket'],[0,6,'Stair'],[1,6,'Stair'],[5,6,'Tower']],
  on:{
    start:function(G,S,a){var sets=[[[1,1],[4,2]],[[0,1],[5,2]],[[1,1],[5,1]],[[0,1],[4,3]],[[1,1],[4,3]]],pick=sets[Math.abs(G.seed|0)%sets.length],i=0;
      G.u.forEach(function(u){if(u.type==='seeker'&&u.hp>0&&pick[i]){var q=pick[i++];if(!LH.at(G,q[0],q[1])||LH.at(G,q[0],q[1])===u){u.x=q[0];u.y=q[1]}}});
      a.hint(G,'Put the Third Man back out and the wicket shuts. Whoever stands beside him lends a shoulder to his hand; each turn the wicket stands open, another grey cloak puts one of them down. Wren runs for the tower door: tap her, then a tile. The bell rings two turns after she is there.')},
    clashEnd:function(G,S,a,K){if(K.d.type==='doorman'&&K.d.hp<=0){S.shut=G.turn;a.log(G,'The wicket shuts on the third man\'s arm, the arm goes back out, and the bar goes across.','good')}},
    turn:function(G,S,a,t){
      var W=a.U(G,'W');
      /* the wicket: another shoulder in the gap, and one of the House goes down under it */
      if(!S.shut&&a.foe(G,'doorman')){var by=beside(G,a),b=by[0];
        if(b){b.hp=0;S.fell=(S.fell||0)+1;a.log(G,'Another grey cloak puts his shoulder in. '+b.n+' goes down under him, with a sound like a dropped sack.','hurt')}
        else{S.through=1;a.log(G,'Nobody is beside him. A fourth grey cloak is through the wicket, and running.','hurt')}}
      /* the bell */
      if(!S.rung&&a.up(W)&&a.on(W,5,6)){S.pull=(S.pull||0)+1;
        if(S.pull===1){W.still=1;W.mov=0;a.log(G,'Wren is through the tower door. Up the stair, Sister Pell has Old Mercy\'s rope in her hands.','good')}
        if(S.pull>=PULLS){S.rung=G.turn;a.log(G,'Old Mercy rings. The two grey cloaks stop where they stand, a pace short of the first of the wounded.','good')}}
      if(S.rung)return;
      /* the two inside: a pace a turn, unhurried; whoever is in the way is put aside, and it costs them the pace */
      G.u.filter(function(u){return u.type==='seeker'&&u.hp>0}).forEach(function(u){
        if(onStair(u))return;
        var goals=STAIR.slice().sort(function(p,q){return (Math.abs(u.x-p[0])+Math.abs(u.y-p[1]))-(Math.abs(u.x-q[0])+Math.abs(u.y-q[1]))});
        if(a.stepToward(G,u,goals[0][0],goals[0][1])||a.stepToward(G,u,goals[1][0],goals[1][1]))return;
        var o=G.u.filter(function(m){return m.side===0&&m.hp>0&&m.id!=='D'&&a.dist(m,u)===1}).sort(function(x,y){return (x.x+(6-x.y))-(y.x+(6-y.y))})[0];
        if(o){o.hp=Math.max(0,o.hp-6);a.log(G,o.hp>0?'A grey cloak puts '+o.n+' aside, not gently.':o.n+' is put out of the way.','hurt');if(o.hp<=0)S.fell=(S.fell||0)+1}})}
  },
  fail:function(G,S,a){return S.through?'through':!S.rung&&G.u.some(function(u){return u.type==='seeker'&&u.hp>0&&onStair(u)})?'names':''},
  goal:function(G,S){return !!S.rung&&!!S.shut},
  win:{t:'Old Mercy rings',s:'Late and dragging, as if the rope had argued with the hands that found it.'},
  lose:{names:{t:'A name is taken',s:'They reach the gatehouse stair before the bell has a voice.'},
    through:{t:'The wicket stands open',s:'They come through it low and fast, one and then the other, the way men come through a door they have practised.'},
    any:{t:'The leg will not push again',s:'Deep in the knee, along the line of the thread, something says one thing, quite clearly.'}},
  stars:function(G,S){var D=G.u[0];return [['The wicket shut and the bell rung',true],['No more than one of the House put down',(S.fell||0)<=1],['With half his strength left',D.hp*2>=D.max]]},
  outro:['On the second stroke the two grey cloaks stop where they stand, a pace short of the first of the wounded. Nobody has touched them.',
    '"The bell is rung, Confessor," says Mother Ione. "While it rings, no blade climbs the Steps and no blade passes this gate."',
    '"You keep a fine bell," says Marrant. "A little slow on the rope."'],
  read:'Chapter 1, the climax'});
function onStair(u){return STAIR.some(function(q){return u.x===q[0]&&u.y===q[1]})}
/* who is lending him a shoulder at the wicket, in the order they go down: the Gate-ward, the lay brother, then Rae */
function beside(G,a){var D=G.u[0];return ['B','L','R'].map(function(id){return a.U(G,id)}).filter(function(u){return u&&u.hp>0&&a.dist(u,D)===1})}

CP.add({id:'c2',book:'Book I · The House of Menders',ch:'Chapter 2 · The Grey Cot',n:'The Fourth Bell',place:"The infirmary hall, Saint Ysolde's",when:'After the night bell. No wind.',art:'saint-ysoldes',
  level:'Level 6 · Kindled',quote:'"Neither does the cold."',
  intro:['Ser Benedek Orrin lies in the Grey Cot and no longer says his oath at the bells. The Confessor says it was Ember-work, and Ember-work wants a hand to do it. The whole House has come into the hall to ask whose.',
    'Wren has the candle. There is no wind tonight: whatever moves the flame, it is not a draught.',
    'He has to answer the hall, and she has to follow the flame along the east wall, before the fourth bell.'],
  objective:function(G,S,a){return (a.foe(G,'question')?'Answer the hall\'s question. ':'The hall is answered. ')+(S.found?'':'Walk Wren along the east wall; the flame will tell her.')},
  top:function(G,S){var left=Math.max(0,4-Math.floor((G.turn-1)/2));return 'Turn '+G.turn+' · '+['the fourth bell','the third bell','the second bell','the first bell','the night bell'][left]+(left?' rung':' is next')},
  open:'"That\'s all anyone\'s asking, Captain. Whose?"',
  map:{name:'The Hall, by Candle',theme:'hall',rows:['~....~','~.~~.~','~....~','~.~~.~','~....~','~.~~.~','~....~']},
  pro:'it',down:'is answered',say:[[/\bstrikes\b/g,'presses'],[/\bstrike\b/g,'press'],[/\bbraces for (\d+), then presses\b/g,'gathers $1, then presses']],insp:1,
  party:{D:{at:[2,6],t:'foot',mov:2,hp:38,br:3,hn:4,throws:0,far:0,img:'darrow1',deck:deck(rep('c_word',3),rep('c_stand',2),['c_still2','c_mend2','c_eye3','c_breath1'])},
    W:{at:[3,6],mov:2,rng:0,deck:null,img:'wren1',lend:'lW'},
    more:[{id:'M',from:'R',n:'Maelis',role:'the Mender',img:'maelis1',still:1,lend:'c_now',at:[1,4]}]},
  foes:[{k:'question',at:[1,6]}],
  marks:function(G,S){return S.close?[[4,0,'go']]:[]},
  on:{
    start:function(G,S,a){a.hint(G,'Darrow answers the Question beside him. Wren walks: after each move, read what the flame does.')},
    moved:function(G,S,a,u){if(u.id!=='W')return;var d=Math.abs(u.x-4)+Math.abs(u.y-0);
      if(d===0){S.found=1;a.log(G,'At the linen press the flame lies nearly flat, and points at an iron door nobody has opened in her lifetime.','good');return}
      if(d<=2)S.close=1;
      a.log(G,d>=7?'The flame stands straight.':d>=5?'The flame stands straight. Then, a little, it leans.':d>=3?'The flame bends.':'The flame is bent nearly flat.',d<=2?'good':'dimm')},
    clashEnd:function(G,S,a,K){if(K.d.hp<=0)a.log(G,'"Nobody\'s. You\'ve had that from me already. Nobody passed."','good')},
    turn:function(G,S,a,t){if(t===3||t===5||t===7)a.log(G,['','','','The first bell.','','The second bell.','','The third bell. He says his oath at every one; you have all heard him.'][t],'dimm')}
  },
  fail:function(G){return G.turn>=9?'bell':''},
  goal:function(G,S,a){return !!S.found&&!a.foe(G,'question')},
  win:{t:'"It came up."',s:'Doors into the hall: three.'},
  lose:{bell:{t:'The fourth bell',s:'The heads go back up the row, to the foot of the Grey Cot.'},any:{t:'The hall turns',s:'He nearly answers the way you answer a man who carries the enemy\'s word into your camp.'}},
  stars:function(G,S){return [['The door is found',true],['Before the third bell',G.turn<=6],['The hall answered without a second wind',G.run.insp>=1]]},
  outro:['The House walks down the east side of its own hall behind a girl with a candle. At the last cot the flame is bent nearly flat.',
    '"You asked whose hand," he says to the lay brother from the fire. "Nobody\'s. It came up."',
    'The kitchen novice lays a skin of flour across the flags at the door. "Then in the morning we\'ll know."'],
  read:'Chapter 2, the climax'});

CP.add({id:'c3',book:'Book I · The House of Menders',ch:'Chapter 3 · The Undercroft',n:'What Was Carried',place:"The painted hall, under Saint Ysolde's",when:'Thirty-nine steps down, on her count.',art:'saint-ysoldes',
  level:'Level 7 · Kindled',quote:'"You\'ve seen it. Up."',
  intro:['The Binding reads three Knots. "That\'s a stair," Maelis has said, and he has taken the undercroft\'s on her count, with his hand on Wren\'s shoulder.',
    'In the wall under the row, behind a lid of new mortar, a thing the size of a thumb-joint stands on end in the rock. Black the way glass is black, with the lamp sliding on it and finding nothing to hold.',
    'He gave his word that when she says up, it is up. She has not said it.'],
  objective:function(G,S){return S.clashes?'Hold as long as he can. When Maelis says up, it is up.':'Walk him to the alcove and put his hand in.'},
  open:'The mortar does not fight him. It was never part of the wall. It is a lid.',
  map:{name:'The Painted Hall',theme:'under',rows:['~~~~~~','~~.~~~','~....~','~....~','~....~','~....~','~~.~~~']},
  rounds:3,pro:'it',insp:2,say:[[/\bstrikes\b/g,'climbs'],[/\bstrike\b/g,'climb'],[/\b(his|its) answer/g,'the cold'],[/(He|It) has answered\./g,'The white is past the second knuckle.'],[/Break off/g,'Let go'],[/Back to the line/g,'Open the fingers, one at a time']],
  party:{D:{at:[2,5],t:'foot',mov:1,hp:42,br:3,hn:5,throws:0,far:0,img:'darrow1',deck:deck(rep('c_pull',2),rep('c_slack',3),['c_still3','c_breath1','c_mend3','c_eye3','c_ground2'])},
    W:{at:[3,5],mov:2,rng:0,deck:null,img:'wren1',lend:'c_lampw'},
    more:[{id:'M',from:'R',n:'Maelis',role:'the Mender',img:'maelis1',mov:2,tend:5,tends:2,lend:'c_now',at:[2,6]}]},
  foes:[{k:'sliver',at:[2,1]}],
  marks:function(G,S){return S.clashes?[]:[[2,2,'go']]},
  labels:[[2,2,'Alcove','The alcove','Where the black glass is set.']],
  on:{
    start:function(G,S,a){a.hint(G,'Three moves to the alcove. Bring Wren\'s lamp and the Mender with him: whoever stands beside him lends a card.')},
    engage:function(G,S,a){a.hint(G,'Pulling does nothing. Each round the cold climbs higher. Press on to hold; let go when he must.')},
    play:function(G,S,a,id){if(id==='c_pull'){S.pulled=(S.pulled||0)+1;return [{k:'status',who:'d',t:'It does not come'}]}},
    ended:function(G,S,a,K){S.rounds=Math.max(S.rounds||0,K.round)}
  },
  goal:function(G,S){return S.clashes>=1},
  fallen:function(G,S){if(!S.clashes)return 'lost';S.fell=1;return 'won'},
  lose:{any:{t:'The lamp burns down',s:'He has not put his hand in.'}},
  win:function(G,S){return S.fell?{t:'"Up."',s:'Maelis has him under both arms from behind.',somber:1}:{t:'"Up."',s:'He opens his fingers, one at a time, because they will only go one at a time.'}},
  stars:function(G,S){var D=G.u[0];return [['His hand went in',true],['Held to the third round',(S.rounds||0)>=3&&!S.fell],['Stopped pulling: one Pull or none',(S.pulled||0)<=1&&!S.fell]]},
  outro:['It had learned the wall. No hand would take it out of there, and no bar either; what had come away was the lid, and only the lid.',
    'Three of them go up thirty-nine steps with his right hand held against his chest in his left. Hollis sees the hand before he sees anything else. "Fire. Now."',
    '"You\'ll have the use of it by the dawn bell," says Maelis. "The ends of the fingers, not for a week."'],
  read:'Chapter 3, the climax'});

CP.add({id:'c4a',book:'Book I · The House of Menders',ch:'Chapter 4 · Old Mercy',n:'Fight From Where You\'re Put',place:"The cloister, Saint Ysolde's",when:'Two chairs on wet flags. A kitchen watching.',art:'saint-ysoldes',
  level:'Level 7 · Kindled',quote:'"That\'s your feet, wanting their own way."',
  intro:['Two men in chairs, knocking wood together in the cold. He finds in the first minute that every answer he has ever had is in his legs.',
    '"The blade\'s your feet now," says Hollis. "It holds them off, and it holds you up. Both. Same piece of wood."',
    'The kitchen has him at two to one. Against.'],
  objective:'Seated: he cannot move. Hold the bind when Hollis swings, and hit him properly.',
  open:'"First lesson. Stop looking at the floor."',
  map:{name:'The Cloister',theme:'court',rows:['~~~~~~','~....~','~....~','~....~','~....~','~....~','~~~~~~']},
  down:'bends over his knees and cannot find his breath',insp:1,
  party:{D:{at:[3,3],t:'blade',mov:0,hp:42,br:3,hn:5,throws:0,far:0,img:'darrow1',deck:deck(rep('c_wood',3),rep('c_bind',2),['c_seated2','c_seated2','c_still3','c_breath2','c_eye3'])},
    W:{at:[4,5],still:1,deck:null,img:'wren1'},A:{at:[1,5],still:1,deck:null,img:'ash1'}},
  foes:[{k:'spar',at:[2,3]}],
  on:{
    start:function(G,S,a){a.hint(G,'Tap Darrow, then Hollis. The Seated Blade strikes hardest from a man who has not moved, and he cannot move.')},
    turn:function(G,S,a,t){if(t===2)a.log(G,'"The bind. On your feet you\'d step off this and come round. You can\'t. So you keep it."','dimm');if(t===4)a.log(G,'"You\'ve been tapping me. Like a Mender. Hit me properly. Once. So I know what you\'ve got."','dimm')}
  },
  goal:function(G,S,a){return !a.foe(G,'spar')},
  win:{t:'"That\'s what you\'ve got."',s:'The wood comes round under his guard, flat and hard, and takes him across the ribs.'},
  lose:{any:{t:'"Again."',s:'His shoulders went, and the rest of him stayed in the chair.'}},
  stars:function(G,S){var D=G.u[0];return [['Hit him properly',true],['Inside four turns',G.turn<=4],['With half his strength left',D.hp*2>=D.max]]},
  outro:['The breath goes out of Hollis in one piece. His chair rocks back onto two legs and hangs there on his sword, and comes down again.',
    'Darrow pays for it in his hand: the sword goes out of his fingers and skitters across the flags, and stops against the dog. She does not bring it. She does not fetch.',
    'Wren writes it in her ledger, under a heading that says Things the Captain can do: The Seated Blade.'],
  read:'Chapter 4, the lesson in the cloister'});

CP.add({id:'c4b',book:'Book I · The House of Menders',ch:'Chapter 4 · Old Mercy',n:'Old Mercy',place:"The bell tower, Saint Ysolde's",when:'Dusk, and the light climbing the tower.',art:'saint-ysoldes',
  level:'Level 7 · Kindled',quote:'"Count it, Wren. Count me the rungs."',
  intro:['The rope has torn out of Sister Pell\'s hands on the first stroke and gone up through the floor. There is one way left to ring the bell, and it is the ladder.',
    'No bell before dark, no law after it. Marrant\'s three men are unarmed, as the law of guests allows, and they have not come for anyone\'s name. They have come to keep anyone from reaching that bell until the light is gone.',
    'Hollis has had his chair set down in the doorway. Darrow\'s stands on the turn of the stair, with the stick across his knees. Above them, halfway up the ladder, Wren has stopped counting.'],
  objective:function(G,S){return 'Hold the stair and the door until Wren reaches the clapper: eleven rungs. She climbs two a turn while no blow lands on a chair, one when it does, and one more for every man sent back down.'},
  top:function(G,S){return 'Turn '+G.turn+' of 8 · rung '+Math.min(11,S.rung||5)+' of eleven'},
  open:'"Count it, Wren. Count me the rungs."',
  map:{name:'The Bell Tower',theme:'tower',rows:['~~b~~~','~~d~~~','~...~~','~~~d~~','~~~d~~','~~.d~~','......']},
  down:'sits down on the step and puts his head in his hands',insp:1,
  party:{D:{at:[3,3],t:'foot',mov:0,hp:42,br:3,hn:5,throws:0,far:0,img:'darrow1',deck:deck(rep('c_bind',2),rep('c_stick',2),['c_seated2','c_seated2','c_still3','c_breath2','c_mend3','c_eye3','c_ground3'])},
    H:{at:[2,5],mov:0,hp:42,img:'hollis1'},
    W:{at:[2,2],still:1,deck:null,img:'wren1'},
    more:[{id:'P',from:'W',n:'Sister Pell',img:'pell',t:'eye',hp:14,still:1,deck:null,at:[1,2]}]},
  foes:[{k:'bigman',at:[3,4]},{k:'guest',at:[3,5]},{k:'guest',at:[3,6]}],
  marks:function(){return [[2,0,'go']]},
  labels:[[2,0,'Bell']],
  on:{
    start:function(G,S,a){a.hint(G,'Tap a chair, then the man in front of it. The Bind halves his answer; a blow he does not land is a rung she climbs.')},
    struck:function(G,S,a,e){if(e.dmg>0)S.hit=1},
    clashEnd:function(G,S,a,K){if(K.d.hp<=0){S.rung=Math.min(11,(S.rung||5)+1);a.log(G,'One fewer on the stair, and she has a rung for it.','good')}},
    turn:function(G,S,a,t){var w=a.U(G,'W'),was=S.rung||5;S.rung=Math.min(11,was+(S.hit?1:2));S.hit=0;
      if(was<7&&S.rung>=7)a.log(G,'A breath. Then, from above, flat and quick: "Seven. Eight."','good');
      if(was<9&&S.rung>=9){if(w)w.y=1;a.log(G,'"Nine. Ten." The window over his head has gone dark.','good')}
      if(was<11&&S.rung>=11){if(w)w.y=0;a.log(G,'"Eleven. Technically there\'s no twelfth, it\'s a beam—"','good')}}
  },
  fail:function(G,S,a){return !a.up(a.U(G,'H'))?'door':G.turn>8?'late':''},
  goal:function(G,S){return (S.rung||5)>=11},
  win:{t:'Old Mercy rings',s:'A hand on the clapper itself, ragged, every stroke a little early.'},
  lose:{late:{t:'The rope is cut',s:'They are past the chairs before the bell has its voice.'},door:{t:'The door is lost',s:'They come over the beech leg, and there is nobody left in the doorway.'},any:{t:'The stair is lost',s:'The stick goes, and then the shoulder.'}},
  stars:function(G,S,a){var D=G.u[0],H=a.U(G,'H');return [['The bell has its voice',true],['The Captain kept half his strength',D.hp*2>=D.max],['So did the one-legged man',!!H&&H.hp*2>=H.max]]},
  outro:['The big man on the stair lets go of the stick. He is the law\'s man, and the law has just spoken from the tower in a voice the whole valley knows.',
    'Marrant steps out over the beech leg into the court. Hollis shifts it, by about an inch, and the Confessor goes down on one knee on the ice, hard. "Kneel to that," says Hollis.',
    'On the gate wall, against what is left of the west, stands a carter with an ox-bell at her belt who was not in the House at noon.'],
  read:'Chapter 4, the climax'});

CP.add({id:'c4c',book:'Book I · The House of Menders',ch:'Chapter 4 · Old Mercy',n:'Eleven Hundred and Seventeen',place:'The Thousand Steps',when:'Dawn. Old Mercy ringing him down.',art:'winch-house',
  level:'Level 7 · Kindled',quote:'"What climbed, you keep."',
  intro:['He has taken the Confessor\'s list onto himself, and a man this House has rung down cannot lawfully be climbed after. So he goes down, that the House may keep the rest.',
    'Wren walks a step below and says each number as his foot comes down on it, not before, so that it is never a promise, only a record. Maelis comes behind and says now. Ash goes on the drop side, and nobody told her to.',
    'Hollis comes behind on the mule the carter brought up, cursing it.'],
  objective:function(G,S){return 'Walk the Steps to the bottom: the Last Hundred, the Long Reach, the Elbow, the Shins. The view follows the company down, and nobody is left behind.'},
  top:function(G,S){var Wd=CP.MS.c4c.world,D=G.u[0];return 'Turn '+G.turn+' · step '+Math.min(1117,Math.round(((S.top+D.y)/(Wd.rows.length-1))*1117))+' of 1117'},
  open:'He keeps his left hand on the cliff. The stone is cold and wet and he does not care.',
  map:{name:'The Thousand Steps',theme:'steps',rows:['..d..~','~~d~~~','..d...','......','~~~~d~','....d.','......']},
  world:{rows:['..d..~','~~d~~~','..d...','......','~~~~d~','....d.','......','~d~~~~','.d....','......','~~~d~~','...d..','......','~~~~d~','....d.','......','~~d~~~','..d...','~d~~~~','.d....','.d.dd.'],
    finds:[{at:[0,6],n:'A ledge out of the wind',t:'A place to stand a moment.',pool:[{heal:4},{heal:8},{insp:1},{card:'c_brace'}]},{at:[5,15],n:'Out of the cloud',t:'The morning is under them.',pool:[{card:'secondwind'},{card:'c_breath2'},{card:'readline'},{heal:6}]}]},
  pro:'it',down:'is walked',say:[[/\bstrikes\b/g,'tells'],[/\bstrike\b/g,'tell'],[/\b(his|its) answer/g,'the stair']],insp:1,
  party:{D:{at:[2,0],t:'foot',mov:2,hp:42,br:3,hn:5,throws:0,far:0,img:'darrow1',deck:deck(rep('c_step',4),rep('c_brace',2),['c_still3','c_breath2','c_mend3','c_ground3','c_eye3'])},
    W:{at:[3,0],rng:0,deck:null,img:'wren1',lend:'lW'},
    A:{at:[4,0],mov:2,rng:0,deck:null,img:'ash1',lend:'c_ashdrop'},
    more:[{id:'M',from:'R',n:'Maelis',role:'the Mender',img:'maelis1',mov:2,tend:5,tends:3,lend:'c_now',at:[1,0]}]},
  foes:[{k:'last',at:[2,1]},{k:'reach',at:[1,7]},{k:'elbow',at:[4,13]},{k:'shins',at:[1,18]}],
  on:{
    start:function(G,S,a){a.hint(G,'Each stretch is taken like a fight: Steps to walk it, a Brace when the leg tells. The stair goes on below the board: bring everyone down and the view follows. A lit diamond is something worth reaching, though not the same thing twice.')},
    clashEnd:function(G,S,a,K){if(K.d.hp>0)return;var t=K.d.type;
      a.log(G,t==='last'?'Somewhere in the second hundred the knee stops deciding each step, and only takes them.':t==='reach'?'Behind him Hollis curses the mule at the Long Reach, for its ears.':t==='elbow'?'And at the Elbow, for its opinions. They come out of the cloud into the morning.':'"Eleven hundred and fifteen. Eleven hundred and sixteen."','good')}
  },
  goal:function(G,S,a){return !a.foes(G).length&&!S.ahead.length&&S.top>=CP.MS.c4c.world.rows.length-7},
  win:{t:'Eleven hundred and seventeen',s:'"And anybody who tells you it\'s a thousand can go back up and count it themselves."'},
  lose:{any:{t:'A hand on the wall',s:'He stops where he is, and Maelis does not say now.'}},
  stars:function(G,S){var D=G.u[0];return [['On his own legs',true],['With half his strength left',D.hp*2>=D.max],['The Mender\'s hands to spare',a_tends(G)>=1]]},
  outro:['He is standing at the bottom of the Thousand Steps, on his own legs, with a hand on nothing.',
    'Rae Thorne has the cart at the winch-house with Hob and Dun in the traces. She looks at the company the way she looks at a load. "Load\'s going on the cart. Not on any of you."',
    '"Road\'s the road," she says. The cart jolts over the first rut of the Holloway, and the bell at her hip rings, and Rae, watching the road, does not hear it. He does.'],
  read:'Chapter 4, the descent'});

/* ================= BOOK II: THE TEMPERING ROAD ================= */

CP.add({id:'c5b',book:'Book II · The Tempering Road',ch:'Chapter 5 · The Thornwild Woman\'s',n:'The Yard at Coldmere',place:'The inn yard, Coldmere',when:'A sergeant and six, come to search.',art:'coldmere',
  level:'Level 8 · Kindled',quote:'"Fight from where you\'re put."',
  tall:'The page tells this one without a blow: a pitchfork goes through the hay, and Hale talks the boy away. Here it comes to pikes.',
  intro:['On the Holloway a column came over the rise, riders two and two, the banner dark on a pale field. Rae had the oxen onto a drove road he had not seen at all before he had properly looked. "Your road," said Darrow. It brought them down to Coldmere.',
    'A levy sergeant and his pike boys have come to search the inn. They are boys with borrowed pikes, and a man who has been told there is a reward. One boy has the horn they were mustered with; one has brought a pitchfork instead.',
    'The company is in the yard with the cart. He walks with a stick now, two steps at a time; Hollis has the beech leg; Ash goes on three legs and a splint.',
    'Put the sergeant down, and the boys will remember somewhere else to be.'],
  objective:'Bring the sergeant down. The company fights with him now: each has a hand of their own.',
  open:'The sergeant looks at the cart, and at the old man on its tailboard, and stops smiling.',
  map:{name:'The Inn Yard',theme:'yard',rows:['..d...','.wd.w.','..d...','w....w','..ww..','......','......']},
  down:'is out of it',insp:1,
  party:{D:{at:[2,5],t:'foot',mov:2,hp:50,br:3,hn:5,throws:1,far:1,img:'darrow',deck:deck(rep('c_stick',3),rep('c_guard',2),['c_still3','c_seated2','c_seated2','c_ground3','c_breath2','c_mend3','c_eye4','c_hand1','c_far1'])},
    H:{at:[3,5],mov:1,img:'hollis'},A:{at:[1,6],mov:2,hp:26,img:'ash'},W:{at:[4,6],img:'wren'},R:{at:[5,6],mov:2,tend:0,tends:0,img:'rae'},
    more:[{id:'M',from:'R',n:'Maelis',role:'the Mender',img:'maelis',mov:2,tend:5,tends:3,lend:'c_now',at:[2,6]}]},
  foes:[{k:'sergeant',at:[2,0]},{k:'horn',at:[3,0]},{k:'pike',at:[1,2]},{k:'pike',at:[3,2]},{k:'pitch',at:[5,1]}],
  rally:['The horn','The horn is blowing'],
  finds:[{at:[0,2],n:'The tailboard of the cart',t:'Something of the carter\'s, kept for a bad day.',pool:[{card:'bandage'},{card:'secondwind'},{card:'stitch'},{card:'hewT'},{insp:1}]}],
  on:{start:function(G,S,a){a.hint(G,'Footing beats Blade, Blade beats Cast, Cast beats Footing. While the boy with the horn stands, the others strike harder. The pitchfork reaches two tiles: Hollis is the one for him.')}},
  goal:function(G,S,a){return !a.foe(G,'sergeant')},
  win:{t:'The boys remember somewhere else to be',s:'Six pikes go out of the yard a good deal faster than they came in.'},
  lose:{any:{t:'The yard is theirs',s:'There are a great many of them for one stick.'}},
  stars:function(G,S,a){var D=G.u[0];return [['The sergeant is down',true],['Nobody of the company down',a.mates(G).length>=6],['With half his strength left',D.hp*2>=D.max]]},
  outro:['The sergeant sits down in the mud of the yard with his hand to his ribs, and the boys look at him, and at the old man with one leg, and at the dog.',
    'Hale stands in the kitchen door with the book under his arm, like a man who had expected it.',
    'On the page it never came to this. A pitchfork went through the hay a hand from Hollis, and Hale talked the boy away.'],
  read:'Chapter 5, the search of the inn (told there without a blow)'});

CP.add({id:'c5c',book:'Book II · The Tempering Road',ch:'Chapter 5 · The Thornwild Woman\'s',n:'The Fold',place:'The shepherds\' fold, above the tarn',when:'Afternoon. Grey stone against grey hillside.',art:'coldmere',
  level:'Level 8 · Kindled',quote:'"We were never here."',
  tall:'On the page a mill carter bluffs the riders away, and nobody draws. Here they come up the slope.',
  intro:['They have sat all day behind the fold wall with no fire, and heard their own names read across the water.',
    'Two grey cloaks come riding the shore road at the walk of men sent to look at something they do not expect to find. Ash stands up on the wall on three legs and the splint, with every hair along her back on end, and barks.',
    'The nearer rider pulls up his horse and looks up the slope. They have the lymer with them on its long leash, and one of them carries the list.'],
  objective:'Hold the fold. Send every grey cloak back down the slope.',
  open:'Ash had been quiet since the loft, and nobody had ever had to tell her.',
  map:{name:'The Fold',theme:'road',rows:['......','..d...','..d...','.wwww.','......','......','......']},
  down:'goes back down the slope',insp:1,
  party:{D:{at:[2,4],t:'foot',mov:2,hp:50,br:3,hn:5,throws:1,far:1,img:'darrow',deck:deck(rep('c_stick',3),rep('c_guard',2),['c_still3','c_seated2','c_seated2','c_ground3','c_breath2','c_mend3','c_eye4','c_hand1','c_far1'])},
    H:{at:[3,4],mov:1,img:'hollis'},A:{at:[1,4],mov:2,hp:26,img:'ash'},W:{at:[4,5],img:'wren'},
    more:[{id:'M',from:'R',n:'Maelis',role:'the Mender',img:'maelis',mov:2,tend:5,tends:3,lend:'c_now',at:[2,5]}]},
  foes:[{k:'lister',at:[2,0]},{k:'cloak',at:[3,0]},{k:'lymer',at:[1,1]},{k:'cloak',at:[4,1]},{k:'cloak',at:[5,0],tpl:1}],
  rally:['The list','A name is being read'],
  finds:[{at:[5,2],n:'That stone',t:'From up here the whole slope can be read.',pool:[{card:'readline'},{card:'pinshot'},{card:'bellow'},{card:'closeup'},{heal:6}]}],
  on:{start:function(G,S,a){S.wave=3+Math.abs(G.seed|0)%2;a.hint(G,'The wall is cover: whoever stands in it takes less on their turn, and they must come to it. The one with the list makes the others strike harder. The lymer is quick and bites more than once. There are more on the shore road.')},
    turn:function(G,S,a,t){if(t!==S.wave)return;var xs=[0,5,1,4,2,3].filter(function(x){return !LH.at(G,x,0)}),n=0;if(Math.abs(G.seed|0)%3===0)xs.reverse();
      xs.slice(0,2).forEach(function(x){if(a.spawn(G,'cloak',x,0))n++});if(n)a.log(G,(n>1?'Two more grey cloaks come':'Another grey cloak comes')+' up from the shore road.','hurt')}},
  goal:function(G,S,a){return G.turn>(S.wave||3)&&!a.foes(G).length},
  win:{t:'The fold is held',s:'And the cart is on the mill tracks before dawn.'},
  lose:{any:{t:'They have a name off the list',s:'The first on it.'}},
  stars:function(G,S,a){var D=G.u[0],A=a.U(G,'A');return [['Every grey cloak sent back',true],['Ash still on her three legs',a.up(A)],['With half his strength left',D.hp*2>=D.max]]},
  outro:['Ash comes back along the wall with her splint clacking, and sits down on Darrow\'s boot, and looks at nobody.',
    '"Sixty at that stone," says Hollis, getting his breath. "And a mule."',
    'On the page nobody drew. A mill carter talked the riders round, and the company was gone before dawn.'],
  read:'Chapter 5, the climax (told there without a blow)'});

CP.add({id:'c6',book:'Book II · The Tempering Road',ch:'Chapter 6 · The Weir',n:'The Post',place:'The keeper\'s stone, on the weir',when:'The mill rings for bread. The glaze is on the stones.',art:'the-lowmarch',
  level:'Level 9 · Kindled',quote:'"You come to the post."',
  intro:['She has shadowed the cart since the mill tracks, and summoned him under the forms. He walked out a quarter hour before the bell, a stone at a time, so that she would find him standing.',
    'Ysra Tal comes onto the glaze and stops three stones off, and takes her gloves off finger by finger. She has built the morning on everyone moving.',
    'Four riders in dark coats sit their horses on the far bank. On the near one, the company stands where the forms hold it. Nobody can help him, and he cannot go to her.'],
  objective:'Stay on the keeper\'s stone. She has to come to him.',
  open:'"That is an answer," she says. "I have nowhere to put it." And she draws.',
  map:{name:'The Weir',theme:'weir',rows:['.w..w.','......','ffffff','ffdfff','ffffff','......','......']},
  pro:'she',down:'goes down hard on the ice, her hand pressed to her shoulder',insp:1,
  say:[[/is still finding (his|her) feet\./g,'stands on the glaze with her weight on her back foot, and waits, the way a door stands open.']],
  party:{D:{at:[2,3],t:'foot',mov:2,hp:58,br:3,hn:5,throws:1,far:1,img:'darrow',deck:deck(rep('c_patience',3),rep('c_guard',2),['c_still3','c_seated2','c_seated2','c_breath2','c_mend3','c_eye4','c_ground3','c_hand1','c_over1','c_far1'])},
    H:{at:[0,6],still:1,deck:null,img:'hollis'},R:{at:[1,6],still:1,img:'rae'},W:{at:[4,6],still:1,deck:null,img:'wren'},
    more:[{id:'M',from:'R',n:'Maelis',role:'the Mender',img:'maelis',still:1,at:[5,6]}]},
  foes:[{k:'ysra',at:[2,0]}],
  marks:function(){return [[2,3,'keep']]},
  labels:[[2,3,'Stone']],
  on:{
    start:function(G,S,a){a.hint(G,'He does not have to chase her. Hold here for guard, and fight when she is beside him: the Seated Blade is for a man who has not moved.')},
    moved:function(G,S,a,u){if(u.id==='D'&&!a.on(u,2,3)){u.x=2;u.y=3;u.moved=false;u.from=null;S.stepped=1;a.log(G,'The old body says step, step and turn and you have her. He does not. "No. You come to the post."','good')}},
    ended:function(G,S,a,K,fx){if(fx[0]&&fx[0].n>=8&&!S.stick){S.stick=1;S.say='The stick goes out from under his hand and skates away across the ice, over the lip of the fall.'}},
    clashEnd:function(G,S,a,K){var y=a.foe(G,'ysra');
      if(S.say){a.log(G,S.say,'hurt');S.say=''}
      if(y&&!S.back&&y.hp*2<=y.max){S.back=1;S.wait=1;if(!LH_at(G,2,0)){y.x=2;y.y=0}y.pinned=true;a.log(G,'She steps back. One stone. Two. Three. It is the oldest invitation there is.','dimm');a.hint(G,'She is waiting for him to come and finish it. Hold here. End the turn.')}},
    turn:function(G,S,a){var y=a.foe(G,'ysra');if(S.wait&&y){S.wait=0;y.marked=true;a.log(G,'So she comes, because she has to: fast and beautiful, and every part of it needs him to be somewhere else.','good');a.hint(G,'He is where he has been.')}}
  },
  goal:function(G,S,a){return !a.foe(G,'ysra')},
  win:{t:'"You did not move."',s:'It sounds like a complaint.'},
  lose:{any:{t:'Off the stone',s:'His heel goes onto the glaze, and the river is very close under it, and very loud.'}},
  stars:function(G,S){var D=G.u[0];return [['A wound from a man who had not moved',true],['He never tried the step',!S.stepped],['With half his strength left',D.hp*2>=D.max]]},
  outro:['His point goes out and stops where his wrist stops, and that is where she arrives. It takes her high in the left shoulder: he feels her own speed drive it.',
    'On the far bank the four riders have their hands on their reins and stay where they are. The forms hold them.',
    'She lies on the ice and waits for him to decide what she is.'],
  read:'Chapter 6, the climax'});

CP.add({id:'c6b',book:'Book II · The Tempering Road',ch:'Chapter 6 · The Weir',n:'The Forms Break',place:'The weir, and the near bank',when:'Noon. Blood on the glaze.',art:'the-lowmarch',
  level:'Level 9 · Kindled',quote:'"Technically…"',
  tall:'On the page the forms hold the four riders where they sit. Here they do not.',
  intro:['She lies on the ice with her hand pressed to her shoulder, and he is still on the keeper\'s stone, his own blood running off the blade, and no stick.',
    'On the far bank the four riders in dark coats have their hands on their reins. They came to carry whatever she took.',
    'He cannot leave the stone. The company can come to him.'],
  objective:'He cannot move. Bring the company out onto the ice to him, and send the four riders back.',
  open:'On the far bank a horse steps down onto the glaze.',
  map:{name:'The Weir',theme:'weir',rows:['.w..w.','......','ffffff','ffdfff','ffffff','......','......']},
  down:'goes back across the ice',insp:1,
  party:{D:{at:[2,3],t:'foot',mov:0,hp:58,br:3,hn:5,throws:1,far:1,img:'darrow',deck:deck(rep('c_patience',3),rep('c_guard',2),['c_still3','c_seated2','c_seated2','c_ground3','c_breath2','c_mend3','c_eye4','c_hand1','c_over1','c_far1'])},
    H:{at:[1,5],mov:1,img:'hollis'},A:{at:[3,5],mov:3,img:'ash'},W:{at:[4,5],img:'wren'},R:{at:[0,6],still:1,img:'rae'},
    more:[{id:'M',from:'R',n:'Maelis',role:'the Mender',img:'maelis',mov:2,tend:6,tends:3,lend:'c_now',at:[2,5]}]},
  foes:[{k:'darkcoat',at:[0,0]},{k:'darklead',at:[2,0]},{k:'darkmail',at:[3,0]},{k:'darkcoat',at:[5,0]}],
  rally:['The word','The word is given'],
  finds:[{at:[4,4],n:'His stick, on the ice',t:'Whoever reaches it sends it skating back to him.',pool:[{card:'c_bar'},{card:'c_bar'},{card:'c_stick'},{card:'c_still3'}]}],
  marks:function(){return [[2,3,'keep']]},
  labels:[[2,3,'Stone']],
  on:{start:function(G,S,a){G.u[0].hp=40;a.hint(G,'The ice costs two steps. Maelis can reach him in one move, and Wren\'s stones carry two tiles. The first rider gives the word: while he sits his horse the others strike harder. One wears mail, and small blows glance off it.')}},
  goal:function(G,S,a){return !a.foes(G).length},
  win:{t:'The forms, such as they are',s:'Four riders go back the way they came, and one of them is leading her horse.'},
  lose:{any:{t:'Off the stone',s:'Without the stick, and with the river very loud under the glaze.'}},
  stars:function(G,S,a){var D=G.u[0];return [['The riders sent back',true],['Nobody of the company down',a.mates(G).length>=6],['He ended with more than he began',D.hp>=40]]},
  outro:['Maelis has her roll open on the ice beside him and her needle threaded before the last of them is across.',
    'Hollis stands at the oxen\'s heads with his fists at his sides, breathing like a bellows, and says a thing about the forms that Wren does not write down.',
    'On the page the four of them stayed where they were. The forms held.'],
  read:'Chapter 6, the climax (told there with the riders held)'});

CP.add({id:'c7',book:'Book II · The Tempering Road',ch:'Chapter 7 · The Far Bank',n:'The Far Bank',place:'The mill bridge',when:'Night. The last cart is over.',art:'the-lowmarch',
  level:'Level 9 · Kindled',quote:'"Count it."',
  intro:['The bridge is barely wider than a cart. Rae has turned hers across the end of it, rail to rail, so that he is on the span with a wall at his back.',
    'The first of them comes onto the bridge. He wears mail under a surcoat whose colours have washed out past reading, and there is frost in his beard. His eyes are open, and there is nobody behind them.',
    'Wren is up on the cart with a lamp tied to the end of a hay-fork. While a flame burns, nothing on the bridge moves. Each lamp burns shorter than the last.'],
  objective:function(G,S){return 'Hold the bridge for five turns. A blow that lands moves him back a pace: four, and they pass ('+(S.gave||0)+' given). '+((S.lamps===undefined?4:S.lamps)>0?'Lamps left: '+(S.lamps===undefined?4:S.lamps)+'.':'The lamps are out.')},
  top:function(G){return 'Turn '+G.turn+' of 5'},
  open:'He takes the stick in both hands and holds it crosswise, like a bar across a door, and the first man walks into it.',
  map:{name:'The Mill Bridge',theme:'bridge',rows:['~~b~~~','~~b~~~','~~b~~~','~.b.~~','..d...','......','......']},
  down:'lets go',idle:'The line stands, and stares.',insp:1,
  say:[[/\bWounds\b/g,'Colds'],[/\bWound\b/g,'Cold'],[/\bwound\b/g,'cold'],[/Barbed/g,'The cold'],[/A blow of his that gets through leaves a Cold in the deck\./g,'A hand of theirs that gets through leaves Cold in the deck: a dead card.'],[/is still finding his feet\./g,'stands and stares at the flame.']],
  party:{D:{at:[2,3],t:'foot',mov:0,hp:58,br:3,hn:5,throws:0,far:0,img:'darrow',deck:deck(rep('c_bar',3),rep('c_stick',2),['c_still3','c_ground3','c_breath2','c_mend3','c_eye4','c_seated2','c_seated2'])},
    W:{at:[1,3],still:1,deck:null,img:'wren',lend:'c_lamp'},
    R:{at:[3,3],still:1,img:'rae',lend:'lR'},
    H:{at:[4,5],still:1,deck:null,img:'hollis'},
    more:[{id:'M',from:'R',n:'Maelis',role:'the Mender',img:'maelis',mov:0,rng:0,throws:0,tend:6,tends:2,lend:'c_now',at:[2,4]}]},
  foes:[{k:'walker',at:[2,1]},{k:'walker',at:[0,0],tpl:1}],
  on:{
    start:function(G,S,a){S.lamps=4;a.hint(G,'Wren, Rae and the Mender each lend a card. The Lamp halves a walker\'s answer and holds him where he stands. There are four.')},
    before:function(G,S,a){var w=a.U(G,'W');if(w)w.lend=S.lamps>0?'c_lamp':'lW'},
    engage:function(G,S,a,K){if(K.hand.indexOf('c_lamp')>=0||K.hand.indexOf('c_lamp2')>=0){S.lamps--;if(S.lamps===0)a.hint(G,'That was the last lamp.')}},
    struck:function(G,S,a,e){if(e.target==='D'&&e.dmg>0){S.gave=(S.gave||0)+1;a.log(G,S.gave>=4?'He gives a fourth pace, and there is no more bridge behind him.':'He gives a pace. The bridge is a pace shorter.','hurt')}},
    turn:function(G,S,a,t){
      var line=['','','"Eleven breaths," says Wren. The flame shrinks, and goes blue, and goes out.','"Nine."','"Seven. It\'s getting shorter, Captain. Every one\'s shorter than the last."','"Five."'][t];if(line)a.log(G,line,'dimm');
      /* the cold off them grows: every turn each hand is a little heavier */
      a.foes(G).forEach(function(e){e.atk+=2;e.ans.forEach(function(x){x.d+=2})});G.tpl.walker.atk+=2;G.tpl.walker.ans.forEach(function(x){x.d+=2});
      if(t<=5&&a.foes(G).length<3)a.spawn(G,'walker',2,0)}
  },
  fail:function(G,S){return (S.gave||0)>=4?'pass':''},
  goal:function(G){return G.turn>=6},
  win:{t:'The biggest lamp in the hills',s:'Every face on the bridge turns to it, like one head.'},
  lose:{pass:{t:'They pass',s:'A fourth pace, and the bridge is behind him.'},any:{t:'The stick comes down',s:'The cold comes down the wood like water, and his hands have stopped feeling like his own.'}},
  stars:function(G,S){var D=G.u[0],c=0;['draw','disc'].forEach(function(p){D.dk[p].forEach(function(id){if(id==='wound')c++})});return [['Held, and not beaten',true],['A lamp to spare',S.lamps>0],['Fewer than three Cold in his hands',c<3]]},
  outro:['"The lamps hold them," says the miller. "The lamps go out." "A big enough one wouldn\'t." He is not looking at the bridge any more. He is looking at his mill.',
    'The fire goes up through the mill floor by floor, and light goes out across the river, yellow and enormous. The hands open. The cold on the stick is only cold.',
    'His hands will not open off the stick. Maelis opens them for him, one finger at a time. "Yours. All of them. Put them inside your coat."'],
  read:'Chapter 7, the bridge'});

CP.END={t:'The road goes on',s:'The Chronicle is still being written. The next mission comes when its chapter closes.'};
})(typeof module!=='undefined'&&module.exports?module.exports:window,typeof module!=='undefined'&&module.exports?require('./campaign.js').CP:window.CP);
