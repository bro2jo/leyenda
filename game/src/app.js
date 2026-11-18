/* THE LINE AND THE HAND as an app: what a phone needs and the game does not know about. It keeps the page for when there
   is no signal (sw.js), says whether it is on the home screen already, asks the phone to put it there or to go full screen,
   and keeps the screen awake while he plays. window.__APP is all the campaign's menu sees of it. */
(function(){
'use strict';
var d=document,n=navigator,ua=n.userAgent||'',prompt=null;
var ios=/iPad|iPhone|iPod/.test(ua)||(n.platform==='MacIntel'&&n.maxTouchPoints>1);
function mm(q){try{return window.matchMedia(q).matches}catch(e){return false}}
function standalone(){return mm('(display-mode: standalone)')||mm('(display-mode: fullscreen)')||n.standalone===true}
function full(){return !!(d.fullscreenElement||d.webkitFullscreenElement)}
function canFull(){var e=d.documentElement;return !ios&&!!(e.requestFullscreen||e.webkitRequestFullscreen)}
function goFull(){var e=d.documentElement,f=e.requestFullscreen||e.webkitRequestFullscreen;if(!f)return false;try{var p=f.call(e,{navigationUI:'hide'});if(p&&p.catch)p.catch(function(){})}catch(x){return false}return true}
function leaveFull(){var f=d.exitFullscreen||d.webkitExitFullscreen;if(f&&full())try{f.call(d)}catch(e){}}
window.addEventListener('beforeinstallprompt',function(e){e.preventDefault();prompt=e;tell()});
window.addEventListener('appinstalled',function(){prompt=null;tell()});
d.addEventListener('fullscreenchange',tell);d.addEventListener('webkitfullscreenchange',tell);
function tell(){try{d.dispatchEvent(new CustomEvent('lh-app'))}catch(e){}}
/* what the menu offers: nothing once it is on the home screen; else the phone's own install, else full screen, else the steps */
function offer(){
  if(standalone())return null;
  if(prompt)return {k:'install',t:'Put it on the home screen',s:'Full screen, its own icon, plays without signal'};
  if(ios)return {k:'steps',t:'Play it full screen',s:'Add it to the home screen: two taps'};
  if(canFull())return full()?{k:'leave',t:'Leave full screen',s:'Back to the browser'}:{k:'full',t:'Go full screen',s:'Hide the browser\'s bars'};
  return null;
}
function take(k){
  if(k==='install'&&prompt){var p=prompt;prompt=null;try{p.prompt();if(p.userChoice)p.userChoice.then(tell,tell)}catch(e){}return 'asked'}
  if(k==='full')return goFull()?'full':'steps';
  if(k==='leave'){leaveFull();return 'left'}
  return 'steps';
}
/* awake while he plays: asked again whenever the page comes back to the front */
var lock=null;
function wake(){if(!n.wakeLock||lock||d.visibilityState!=='visible')return;try{n.wakeLock.request('screen').then(function(l){lock=l;l.addEventListener('release',function(){lock=null})},function(){})}catch(e){}}
d.addEventListener('visibilitychange',wake);d.addEventListener('pointerdown',wake,{passive:true});
/* a long press is not a menu here, and two fingers do not zoom the board */
d.addEventListener('contextmenu',function(e){if(e.target.closest&&e.target.closest('#game'))e.preventDefault()});
d.addEventListener('gesturestart',function(e){e.preventDefault()});
/* the page kept for when there is no signal */
var sw='idle';
if('serviceWorker' in n&&(location.protocol==='https:'||location.hostname==='localhost'||location.hostname==='127.0.0.1')){
  window.addEventListener('load',function(){n.serviceWorker.register('sw.js').then(function(r){sw='on';
    n.serviceWorker.ready.then(function(g){if(g.active)g.active.postMessage({warm:(window.LH_WARM||[])})});return r},function(){sw='off'})});
}
if(standalone())d.documentElement.classList.add('standalone');
window.__APP={ios:ios,standalone:standalone,offer:offer,take:take,full:full,get sw(){return sw},get prompt(){return !!prompt}};
})();
