/* THE UNKNEELING — the Forge (darrow/wardrobe.html). Choose a look from the pieces he has earned, see it on the stage
   if it has been painted, and copy the prompt that paints it, with the Look line Claude files it by. Its data is the
   JSON in #forge-data, written by the build; the choice, and which pieces this browser has already seen open, are
   remembered in this browser only. A piece that needs another (the stick under his arm needs the stick) brings it when
   chosen; a piece that no longer fits what was just chosen falls back to his own look's, or the first that fits. */
(function(){
"use strict";
var dataEl = document.getElementById("forge-data");
if (!dataEl) { return; }
var D = JSON.parse(dataEl.textContent), SAVE = "unkneeling-forge", SEEN = "unkneeling-forge-seen", state = {}, base;
var $ = function(id){ return document.getElementById(id); };
var each = function(list, fn){ Array.prototype.forEach.call(list, fn); };
var pieces = {};
D.cats.forEach(function(c){ pieces[c.id] = {}; c.options.forEach(function(o){ pieces[c.id][o.id] = o; }); });
var fits = function(cat, id){  /* open, and everything it needs is what is chosen now */
  var o = pieces[cat][id];
  return !!(o && o.open) && Object.keys(o.needs || {}).every(function(k){ return state[k] === o.needs[k]; });
};
var settle = function(fixed){  /* every other piece that no longer fits falls back */
  for (var pass = 0; pass < 3; pass += 1) {
    D.cats.forEach(function(c){
      if (fixed[c.id] || fits(c.id, state[c.id])) { return; }
      var back = fits(c.id, D.start[c.id]) ? D.start[c.id] : null;
      c.options.forEach(function(o){ if (!back && fits(c.id, o.id)) { back = o.id; } });
      state[c.id] = back || state[c.id];
    });
  }
};
var choose = function(cat, id){
  var fixed = {}, needs = (pieces[cat][id] || {}).needs || {};
  state[cat] = id; fixed[cat] = true;
  Object.keys(needs).forEach(function(k){ state[k] = needs[k]; fixed[k] = true; });
  settle(fixed);
};
var wear = function(v){
  D.cats.forEach(function(c){ state[c.id] = pieces[c.id][v[c.id]] ? v[c.id] : D.start[c.id]; });
  state.details = typeof v.details === "string" ? v.details : "";
  settle({});
};
var norm = function(t){ return String(t || "").trim().replace(/\s+/g, " ").toLowerCase(); };
var keyOf = function(values, details){ return D.cats.map(function(c){ return values[c.id]; }).join("|") + "|" + norm(details); };
base = keyOf(D.start, "");  /* his current look: a remembered choice holds only while it is still the newest */
var selects = document.querySelectorAll("select[data-cat]"), notes = $("forge-details");
var tiles = document.querySelectorAll(".look-tile[data-look]");

/* New since this browser last saw the Forge: marked in its menu and named above it (nothing on a first visit) */
(function(){
  var open = [], fresh = [];
  D.cats.forEach(function(c){ c.options.forEach(function(o){ if (o.open) { open.push(c.id + "." + o.id); } }); });
  try {
    var seen = JSON.parse(localStorage.getItem(SEEN) || "null");
    if (Array.isArray(seen)) { fresh = open.filter(function(k){ return seen.indexOf(k) < 0; }); }
    localStorage.setItem(SEEN, JSON.stringify(open));
  } catch (e) { return; }
  if (!fresh.length) { return; }
  fresh.forEach(function(k){
    var cat = k.split(".")[0], id = k.slice(cat.length + 1), sel = document.querySelector('select[data-cat="' + cat + '"]');
    each(sel ? sel.options : [], function(opt){ if (opt.value === id) { opt.textContent += " · new"; } });
    var label = sel && sel.parentNode.querySelector("label");
    if (label && !label.querySelector(".forge-new")) {
      var tag = document.createElement("span"); tag.className = "forge-new"; tag.textContent = "New"; label.appendChild(tag);
    }
  });
  var line = $("forge-fresh");
  line.innerHTML = "<b>New since you last looked:</b> ";
  line.appendChild(document.createTextNode(fresh.map(function(k){
    var cat = k.split(".")[0]; return pieces[cat][k.slice(cat.length + 1)].name;
  }).join(", ") + "."));
  line.hidden = false;
})();

var render = function(){
  var key = keyOf(state, state.details), look = null;
  D.looks.forEach(function(l){ if (!look && keyOf(l.values, l.details) === key) { look = l; } });
  each(selects, function(s){ s.value = state[s.getAttribute("data-cat")]; });
  if (look) { $("forge-img").src = look.full; $("forge-img").alt = look.alt; $("forge-zoom").href = look.full; }
  $("forge-zoom").hidden = !look;
  $("forge-empty").hidden = !!look;
  $("forge-name").textContent = look ? look.name : "A new look";
  $("forge-state").textContent = look ? (look.worn ? "his look now" : "in the lookbook") : "not painted yet";
  $("forge-result").innerHTML = look ? "<b>Painted.</b> This look is in the lookbook."
    : "<b>Not painted yet.</b> The prompt below paints it.";
  each(tiles, function(t){ t.setAttribute("aria-current", String(!!look && t.getAttribute("data-look") === look.id)); });
  var refs = D.refs.slice(), n = 0;
  each(document.querySelectorAll(".ref-card"), function(card){
    var k = card.getAttribute("data-ref-for"), on = !k || state[k.split(".")[0]] === k.split(".")[1];
    card.hidden = !on;
    if (on && k) { refs.push(D.optRefs[k]); }
    if (on) { n += 1; card.querySelector(".ref-n").textContent = "Image " + n; }
  });
  each(document.querySelectorAll("[data-from]"), function(el){
    var o = pieces[el.getAttribute("data-from")][state[el.getAttribute("data-from")]];
    el.textContent = o.from;
    if (o.href) { var a = document.createElement("a"); a.href = o.href; a.textContent = o.story; el.appendChild(a); }
  });
  var design = D.cats.map(function(c){ return "- " + c.label + ": " + pieces[c.id][state[c.id]].prompt; }).join("\n");
  var listed = refs.map(function(r, i){ return "Image " + (i + 1) + " (" + r.file + "): " + r.use; }).join("\n");
  $("forge-prompt").value = D.template.split("{references}").join(listed).split("{design}").join(design)
    .split("{details}").join(state.details.trim() || "none");
  $("forge-line").textContent = "Look: " + D.cats.map(function(c){ return c.id + "=" + state[c.id]; }).join(" ")
    + (state.details.trim() ? " · touches: " + state.details.trim() : "");
  try { localStorage.setItem(SAVE, JSON.stringify({base: base, state: state})); } catch (e) { /* the choice is only a convenience */ }
};

var copy = function(text, btn, fallback){
  var label = btn.getAttribute("data-label") || btn.textContent;
  btn.setAttribute("data-label", label);
  var said = function(msg){ btn.textContent = msg; setTimeout(function(){ btn.textContent = label; }, 2200); };
  var manual = function(){ fallback(); said("Selected: copy it"); };
  if (navigator.clipboard && navigator.clipboard.writeText) { navigator.clipboard.writeText(text).then(function(){ said("Copied"); }, manual); }
  else { manual(); }
};

wear(D.start);
try { var saved = JSON.parse(localStorage.getItem(SAVE) || "null"); if (saved && saved.base === base) { wear(saved.state); } } catch (e) { /* start from his look */ }
if (notes) { notes.value = state.details; notes.addEventListener("input", function(){ state.details = notes.value; render(); }); }
each(selects, function(s){
  s.addEventListener("change", function(){ choose(s.getAttribute("data-cat"), s.value); render(); });
});
each(tiles, function(t){
  t.addEventListener("click", function(e){
    var look = D.looks.filter(function(l){ return l.id === t.getAttribute("data-look"); })[0];
    if (!look || e.metaKey || e.ctrlKey || e.shiftKey) { return; }
    e.preventDefault();
    wear(Object.assign({details: look.details}, look.values));
    if (notes) { notes.value = state.details; }
    render();
    $("forge-stage").scrollIntoView({behavior: "smooth", block: "center"});
  });
});
$("forge-copy").addEventListener("click", function(){
  copy($("forge-prompt").value, $("forge-copy"), function(){ $("forge-prompt").focus(); $("forge-prompt").select(); });
});
$("forge-copy-line").addEventListener("click", function(){
  copy($("forge-line").textContent, $("forge-copy-line"), function(){
    var r = document.createRange(); r.selectNodeContents($("forge-line"));
    var sel = window.getSelection(); sel.removeAllRanges(); sel.addRange(r);
  });
});
render();
})();
