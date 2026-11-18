/* How each mission plays: three players go through every one of them many times.
     planned   follows the mission's sensible plan and plays its hands with care
     careless  walks the same plan but plays cards at random, and sometimes stops early
     idle      ends every turn without doing anything
   and the planned player again with luck held to one side: every hand the best the pile could give, or the worst (the pile is put in
   order before each fight, but he still has to go through the whole deck before a card comes round again).
   What to read: a mission where the careless player does as well as the planned one asks for no skill; one that always ends on the
   same turn with the same health has no variety; one the planned player never loses, with every star, has no teeth.
     node game/test/campaign.play.js [runs] [mission id] */
var B=require('./campaign.bots.js'),LH=B.LH,CP=B.CP,N=+process.argv[2]||60,only=process.argv[3]||null;
function rng(seed){var s=seed|0||1;return function(){s=(Math.imul(s,1664525)+1013904223)|0;return ((s>>>8)&0xffffff)/0x1000000}}
function sd(a){if(a.length<2)return 0;var m=a.reduce(function(x,y){return x+y},0)/a.length;return Math.sqrt(a.reduce(function(x,y){return x+(y-m)*(y-m)},0)/a.length)}
function mean(a){return a.length?a.reduce(function(x,y){return x+y},0)/a.length:0}
function play(id,kind){
  var r={won:0,stars:[],turns:[],hp:[],clashes:[],found:0,why:{},dec:0,opt:0,played:0,pat:{}};
  for(var i=1;i<=N;i++){var st={decisions:0,options:0,played:0};B.MODE.stat=st;B.MODE.rand=kind==='careless'?rng(i*7919+13):null;B.MODE.luck=kind==='lucky'?'best-cycle':kind==='unlucky'?'worst-cycle':null;
    var G=B.run(id,i*37+11,kind==='idle'?function(){}:null),S=G.cs,w=S.result==='won';
    if(w){r.won++;var n=S.stars.filter(function(x){return x[1]}).length;r.stars.push(n);r.turns.push(G.turn);r.hp.push(G.u[0].hp/G.u[0].max);r.pat[S.stars.map(function(x){return x[1]?1:0}).join('')]=1}
    else r.why[S.why||(G.over?'down':'unfinished')]=(r.why[S.why||(G.over?'down':'unfinished')]||0)+1;
    r.clashes.push(S.clashes);r.found+=S.found||0;r.dec+=st.decisions;r.opt+=st.options;r.played+=st.played}
  B.MODE.stat=B.MODE.rand=B.MODE.luck=null;return r}
function pct(a){return Math.round(100*a/N)}
console.log('mission'.padEnd(31)+'planned: won ★   turns±sd  hp%±sd  clash cards/clash choices | careless: won ★ | idle won | lucky / unlucky draws | ways lost (planned)');
CP.ORDER.forEach(function(id){if(only&&only!==id)return;var M=CP.MS[id],p=play(id,'planned'),c=play(id,'careless'),d=play(id,'idle'),lu=play(id,'lucky'),un=play(id,'unlucky');
  console.log((id+' '+M.n).slice(0,30).padEnd(31)+(pct(p.won)+'%').padStart(13)+' '+mean(p.stars).toFixed(1)+'  '+(mean(p.turns).toFixed(1)+'±'+sd(p.turns).toFixed(1)).padStart(9)+'  '+(Math.round(100*mean(p.hp))+'±'+Math.round(100*sd(p.hp))).padStart(6)+'  '+mean(p.clashes).toFixed(1).padStart(5)+' '+(p.played/Math.max(1,p.clashes.reduce(function(x,y){return x+y},0))).toFixed(1).padStart(8)+'    '+(p.dec?(p.opt/p.dec).toFixed(1):'-').padStart(5)+'    |'+(pct(c.won)+'%').padStart(12)+' '+mean(c.stars).toFixed(1)+' |'+(pct(d.won)+'%').padStart(7)+'   |'+(pct(lu.won)+'% / '+pct(un.won)+'%').padStart(14)+'         | '+(Object.keys(p.why).map(function(k){return k+' '+p.why[k]}).join(', ')||'none')+' · star patterns '+Object.keys(p.pat).length)});
