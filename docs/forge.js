/* THE UNKNEELING — the Forge (darrow/wardrobe.html). Build a look a step at a time from the pieces he has earned, see
   it on the stage if it has been painted, and copy the prompt that paints it, with the Look line Claude files it by.
   Its data is the JSON in #forge-data, written by the build: the pieces in step order, and the pairs that cannot be worn
   together (the build's wardrobe_clash). Each step offers only what goes with the steps before it; when an earlier
   choice changes, a later piece that no longer goes with it falls back to his own look's, or the first that fits, and
   the Forge says so. The choice, and which pieces this browser has seen open, are remembered in this browser only. */
(function(){
"use strict";
var dataEl = document.getElementById("forge-data");
if (!dataEl) { return; }
var D = JSON.parse(dataEl.textContent), SAVE = "unkneeling-forge", SEEN = "unkneeling-forge-seen", state = {}, fresh = {}, base;
var $ = function(id){ return document.getElementById(id); };
var each = function(list, fn){ Array.prototype.forEach.call(list, fn); };
var pieces = {}, clash = {}, at = {};
D.cats.forEach(function(c, i){ at[c.id] = i; pieces[c.id] = {}; c.options.forEach(function(o){ pieces[c.id][o.id] = o; }); });
D.clash.forEach(function(p){ clash[p[0] + "|" + p[1]] = clash[p[1] + "|" + p[0]] = true; });
var goes = function(ci, id){  /* goes with every piece the earlier steps chose */
  var k = D.cats[ci].id + "." + id;
  for (var j = 0; j < ci; j += 1) { if (clash[k + "|" + D.cats[j].id + "." + state[D.cats[j].id]]) { return false; } }
  return true;
};
var fits = function(ci, id){ var o = pieces[D.cats[ci].id][id]; return !!(o && o.open) && goes(ci, id); };
var settle = function(from){  /* the later steps follow the earlier ones; returns what moved */
  var moved = [];
  for (var ci = from; ci < D.cats.length; ci += 1) {
    var c = D.cats[ci], back = null;
    if (fits(ci, state[c.id])) { continue; }
    if (fits(ci, D.start[c.id])) { back = D.start[c.id]; }
    c.options.forEach(function(o){ if (!back && fits(ci, o.id)) { back = o.id; } });
    if (back) { state[c.id] = back; moved.push(c.label + ": " + pieces[c.id][back].name); }
  }
  return moved;
};
var wear = function(v){
  D.cats.forEach(function(c){ state[c.id] = pieces[c.id][v[c.id]] ? v[c.id] : D.start[c.id]; });
  state.details = typeof v.details === "string" ? v.details : "";
  settle(0);
};
var norm = function(t){ return String(t || "").trim().replace(/\s+/g, " ").toLowerCase(); };
var keyOf = function(values, details){ return D.cats.map(function(c){ return values[c.id]; }).join("|") + "|" + norm(details); };
base = keyOf(D.start, "");  /* his current look: a remembered choice holds only while it is still the newest */
var selects = document.querySelectorAll("select[data-cat]"), whos = document.querySelectorAll(".who[data-who]");
var notes = $("forge-details"), tiles = document.querySelectorAll(".look-tile[data-look]");

/* New since this browser last saw the Forge: marked on the piece and its step, and named above them (not on a first visit) */
(function(){
  var open = [], seen = null;
  D.cats.forEach(function(c){ c.options.forEach(function(o){ if (o.open) { open.push(c.id + "." + o.id); } }); });
  try { seen = JSON.parse(localStorage.getItem(SEEN) || "null"); localStorage.setItem(SEEN, JSON.stringify(open)); } catch (e) { return; }
  if (!Array.isArray(seen)) { return; }
  var names = [];
  open.forEach(function(k){
    if (seen.indexOf(k) >= 0) { return; }
    var cat = k.split(".")[0], id = k.slice(cat.length + 1);
    fresh[k] = true;
    names.push(pieces[cat][id].name);
    var host = cat === D.company ? document.querySelector('.who[data-who="' + id + '"] b')
      : (document.querySelector('select[data-cat="' + cat + '"]') || {}).parentNode;
    host = host && (host.tagName === "B" ? host : host.querySelector("label"));
    if (host && !host.querySelector(".forge-new")) {
      var tag = document.createElement("span"); tag.className = "forge-new"; tag.textContent = "New"; host.appendChild(tag);
    }
  });
  if (!names.length) { return; }
  var line = $("forge-fresh");
  line.innerHTML = "<b>New since you last looked:</b> ";
  line.appendChild(document.createTextNode(names.join(", ") + "."));
  line.hidden = false;
})();

var fill = function(sel){  /* a step's menu: what goes with the earlier steps; the locked ones greyed with what opens them */
  var cat = sel.getAttribute("data-cat"), ci = at[cat];
  sel.textContent = "";
  D.cats[ci].options.forEach(function(o){
    if (!goes(ci, o.id)) { return; }
    var opt = document.createElement("option");
    opt.value = o.id;
    opt.disabled = !o.open;
    opt.textContent = o.name + (!o.open ? " · " + o.lock : fresh[cat + "." + o.id] ? " · new" : "");
    sel.appendChild(opt);
  });
  sel.value = state[cat];
};

var render = function(){
  var key = keyOf(state, state.details), look = null;
  D.looks.forEach(function(l){ if (!look && keyOf(l.values, l.details) === key) { look = l; } });
  each(selects, fill);
  each(whos, function(b){ b.setAttribute("aria-pressed", String(state[D.company] === b.getAttribute("data-who"))); });
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

var choose = function(cat, id){
  state[cat] = id;
  var moved = settle(at[cat] + 1), note = $("forge-fit");
  note.textContent = moved.length ? "To go with that: " + moved.join("; ") + "." : "";
  note.hidden = !moved.length;
  render();
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
each(selects, function(s){ s.addEventListener("change", function(){ choose(s.getAttribute("data-cat"), s.value); }); });
each(whos, function(b){ b.addEventListener("click", function(){ choose(D.company, b.getAttribute("data-who")); }); });
each(tiles, function(t){
  t.addEventListener("click", function(e){
    var look = D.looks.filter(function(l){ return l.id === t.getAttribute("data-look"); })[0];
    if (!look || e.metaKey || e.ctrlKey || e.shiftKey) { return; }
    e.preventDefault();
    wear(Object.assign({details: look.details}, look.values));
    if (notes) { notes.value = state.details; }
    $("forge-fit").hidden = true;
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
