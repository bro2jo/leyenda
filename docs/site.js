/* THE UNKNEELING — small helpers. Every page works without this file. */
(function(){
"use strict";
var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
/* reading progress */
var bar = document.querySelector(".progress>i");
if (bar && document.body.classList.contains("reader-page")) {
  var tick = function(){
    var h = document.documentElement, max = h.scrollHeight - h.clientHeight;
    bar.style.width = (max > 0 ? Math.min(100, 100 * h.scrollTop / max) : 0).toFixed(1) + "%";
  };
  window.addEventListener("scroll", tick, {passive:true}); tick();
} else if (bar) { bar.parentNode.removeChild(bar); }
/* roster filters */
var box = document.querySelector("[data-filters]");
if (box) {
  var cards = Array.prototype.slice.call(document.querySelectorAll(".card"));
  var active = {faction:null, status:null};
  var apply = function(){
    cards.forEach(function(c){
      var ok = (!active.faction || c.getAttribute("data-faction") === active.faction) &&
               (!active.status || c.getAttribute("data-status") === active.status);
      c.hidden = !ok;
    });
    box.querySelectorAll("button").forEach(function(b){
      var f = b.getAttribute("data-filter");
      b.setAttribute("aria-pressed", f === "all" ? String(!active.faction && !active.status) : String(active[f] === b.getAttribute("data-value")));
    });
  };
  box.addEventListener("click", function(e){
    var b = e.target.closest("button[data-filter]"); if (!b) return;
    var f = b.getAttribute("data-filter"), v = b.getAttribute("data-value");
    if (f === "all") { active.faction = null; active.status = null; }
    else { active[f] = active[f] === v ? null : v; }
    apply();
  });
  apply();
}
/* picture zoom: a link with data-zoom opens its picture in a full-screen dialog (without this file the link opens the picture) */
var zoomLinks = document.querySelectorAll("a[data-zoom]");
if (zoomLinks.length && typeof HTMLDialogElement === "function") {
  var dlg = document.createElement("dialog");
  dlg.className = "zoom";
  dlg.innerHTML = '<button class="x" type="button" aria-label="Close">×</button><img alt="">';
  document.body.appendChild(dlg);
  var big = dlg.querySelector("img");
  dlg.addEventListener("click", function(){ dlg.close(); });
  dlg.addEventListener("close", function(){ big.removeAttribute("src"); });
  Array.prototype.forEach.call(zoomLinks, function(a){
    a.addEventListener("click", function(e){
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.button) { return; }
      e.preventDefault();
      var img = a.querySelector("img");
      big.src = a.getAttribute("href");
      big.alt = img ? img.alt : "";
      dlg.showModal();
    });
  });
}
/* name previews: a linked name in the story (data-pv-t) shows a small card with its picture, if it has one, and one
   line. Hover or keyboard focus on a desktop; on a touch screen the first tap shows the card and the second (or Open)
   follows the link. Without this file every name is a plain link. */
var pvLinks = document.querySelectorAll("a[data-pv-t]");
if (pvLinks.length) {
  var fine = !!(window.matchMedia && window.matchMedia("(hover: hover) and (pointer: fine)").matches);
  var card = document.createElement("div");
  card.className = "pv"; card.id = "pv"; card.setAttribute("role", "tooltip"); card.hidden = true;
  document.body.appendChild(card);
  var cur = null, timer = null;
  var el = function(tag, cls, text){ var n = document.createElement(tag); if (cls) { n.className = cls; } if (text) { n.textContent = text; } return n; };
  var place = function(a){
    var r = a.getBoundingClientRect(), w = card.offsetWidth, h = card.offsetHeight, vw = document.documentElement.clientWidth;
    var x = Math.min(Math.max(8, r.left), vw - w - 8), y = r.bottom + 8;
    if (y + h > window.innerHeight - 8 && r.top - h - 8 > 0) { y = r.top - h - 8; }
    card.style.left = (x + window.pageXOffset) + "px"; card.style.top = (y + window.pageYOffset) + "px";
  };
  var hide = function(){
    clearTimeout(timer);
    if (cur) { cur.classList.remove("pv-on"); cur.removeAttribute("aria-describedby"); }
    cur = null; card.hidden = true;
  };
  var show = function(a, touch){
    clearTimeout(timer);
    if (cur && cur !== a) { cur.classList.remove("pv-on"); cur.removeAttribute("aria-describedby"); }
    cur = a; a.classList.add("pv-on"); a.setAttribute("aria-describedby", "pv");
    while (card.firstChild) { card.removeChild(card.firstChild); }
    var src = a.getAttribute("data-pv-i"), kind = a.getAttribute("data-pv-k") || "wide";
    card.className = "pv" + (src && kind === "portrait" ? " portrait" : "") + (touch ? " touch" : "");
    if (src) {
      var box = el("span", "pv-img " + kind), img = el("img");
      img.src = src; img.alt = "";
      if (a.getAttribute("data-pv-f")) { img.style.objectPosition = a.getAttribute("data-pv-f"); }
      img.addEventListener("load", function(){ if (cur === a) { place(a); } });
      box.appendChild(img); card.appendChild(box);
    }
    var body = el("span", "pv-body");
    body.appendChild(el("span", "pv-t", a.getAttribute("data-pv-t")));
    if (a.getAttribute("data-pv-s")) { body.appendChild(el("span", "pv-s", a.getAttribute("data-pv-s"))); }
    if (a.getAttribute("data-pv-x")) { body.appendChild(el("span", "pv-x", a.getAttribute("data-pv-x"))); }
    if (touch) { var go = el("a", "pv-open", "Open →"); go.href = a.href; body.appendChild(go); }
    card.appendChild(body);
    card.hidden = false; place(a);
  };
  Array.prototype.forEach.call(pvLinks, function(a){
    if (fine) {
      a.addEventListener("mouseenter", function(){ clearTimeout(timer); timer = setTimeout(function(){ show(a, false); }, 90); });
      a.addEventListener("mouseleave", function(){ clearTimeout(timer); timer = setTimeout(hide, 90); });
      a.addEventListener("focus", function(){ show(a, false); });
      a.addEventListener("blur", hide);
    } else {
      a.addEventListener("click", function(e){ if (cur !== a) { e.preventDefault(); show(a, true); } });
    }
  });
  document.addEventListener("click", function(e){ if (cur && !e.target.closest("a[data-pv-t]") && !e.target.closest(".pv")) { hide(); } });
  document.addEventListener("keydown", function(e){ if (e.key === "Escape") { hide(); } });
  window.addEventListener("resize", hide);
}
/* songs: a link with data-song plays its song in place, one song at a time (the Codex's players included); press it
   again to pause. While it plays out of sight a small dock keeps a pause button in reach. Without this file the link
   opens the song. */
var songLinks = document.querySelectorAll("a[data-song]");
var players = document.querySelectorAll("audio");
var hushPlayers = function(except){ Array.prototype.forEach.call(players, function(p){ if (p !== except && !p.paused) { p.pause(); } }); };
if (songLinks.length && typeof Audio === "function") {
  var tune = new Audio(), from = null, inView = true;
  tune.preload = "none";
  var dock = document.createElement("div");
  dock.className = "song-dock"; dock.hidden = true;
  dock.innerHTML = '<a class="song" href="#" role="button" aria-pressed="true"><svg class="sg-i" viewBox="0 0 16 16" aria-hidden="true">' +
    '<path class="sg-play" d="M4 2.2v11.6L13.4 8z"/><path class="sg-pause" d="M3.5 2.5h3v11h-3zm6 0h3v11h-3z"/></svg><span class="sg-t"></span></a>' +
    '<button class="x" type="button" aria-label="Stop">×</button>';
  document.body.appendChild(dock);
  var dockBtn = dock.querySelector(".song");
  var watch = typeof IntersectionObserver === "function" ? new IntersectionObserver(function(es){
    es.forEach(function(en){ if (en.target === from) { inView = en.isIntersecting; } });
    paint();
  }) : null;
  var paint = function(){
    var on = !!from && !tune.paused;
    Array.prototype.forEach.call(songLinks, function(a){
      var me = a === from;
      a.classList.toggle("on", me && on);
      a.setAttribute("aria-pressed", String(me && on));
      if (!me) { a.style.removeProperty("--p"); }
    });
    dockBtn.classList.toggle("on", on);
    dockBtn.setAttribute("aria-pressed", String(on));
    dockBtn.setAttribute("aria-label", (on ? "Pause " : "Play ") + (from ? from.getAttribute("data-song") : ""));
    dock.hidden = !from || (inView && !!watch);
  };
  var stop = function(){
    tune.pause();
    if (from && watch) { watch.unobserve(from); }
    if (from) { from.style.removeProperty("--p"); }
    from = null; inView = true; dockBtn.style.removeProperty("--p"); paint();
  };
  var toggle = function(){
    if (!tune.paused) { tune.pause(); return; }
    hushPlayers(null);
    var pr = tune.play();
    if (pr && pr.catch) { pr.catch(paint); }
  };
  Array.prototype.forEach.call(songLinks, function(a){
    a.setAttribute("role", "button");
    a.setAttribute("aria-pressed", "false");
    a.addEventListener("click", function(e){
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.button) { return; }
      e.preventDefault();
      if (from === a) { toggle(); return; }
      stop();
      from = a; tune.src = a.getAttribute("href");
      dock.querySelector(".sg-t").textContent = a.getAttribute("data-song");
      if (watch) { watch.observe(a); }
      toggle();
    });
  });
  dockBtn.addEventListener("click", function(e){ e.preventDefault(); toggle(); });
  dock.querySelector(".x").addEventListener("click", stop);
  tune.addEventListener("play", paint);
  tune.addEventListener("pause", paint);
  tune.addEventListener("ended", stop);
  tune.addEventListener("timeupdate", function(){
    if (!from || !tune.duration) { return; }
    var p = (100 * tune.currentTime / tune.duration).toFixed(1) + "%";
    from.style.setProperty("--p", p); dockBtn.style.setProperty("--p", p);
  });
  Array.prototype.forEach.call(players, function(p){ p.addEventListener("play", function(){ tune.pause(); hushPlayers(p); }); });
} else {
  Array.prototype.forEach.call(players, function(p){ p.addEventListener("play", function(){ hushPlayers(p); }); });
}
/* the Codex: a link to an entry (#place-…, #faction-…, #codex-…) opens it */
var openTarget = function(){
  var id = decodeURIComponent(location.hash.slice(1)), t = id && document.getElementById(id);
  if (!t) { return; }
  var d = t.tagName === "DETAILS" ? t : t.querySelector("details");
  if (d && !d.open) { d.open = true; }
  t.scrollIntoView({block: "start"});
};
openTarget();
window.addEventListener("hashchange", openTarget);
if (reduce) { document.documentElement.classList.add("reduce"); }
})();
