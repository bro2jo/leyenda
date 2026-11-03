/* THE UNKNEELING — the Forge (darrow/wardrobe.html). Choose a look from the pieces he has earned, see it on the stage
   if it has been painted, and copy the prompt that paints it, with the Look line Claude files it by. Its data is the
   JSON in #forge-data, written by the build; the choice is remembered in this browser only. */
(function(){
"use strict";
var dataEl = document.getElementById("forge-data");
if (!dataEl) { return; }
var D = JSON.parse(dataEl.textContent), SAVE = "unkneeling-forge", state = {}, base;
var $ = function(id){ return document.getElementById(id); };
var pieces = {};
D.cats.forEach(function(c){ pieces[c.id] = {}; c.options.forEach(function(o){ pieces[c.id][o.id] = o; }); });
var isOpen = function(cat, id){ return !!(pieces[cat][id] && pieces[cat][id].open); };
var wear = function(v){
  D.cats.forEach(function(c){ state[c.id] = isOpen(c.id, v[c.id]) ? v[c.id] : D.start[c.id]; });
  state.details = typeof v.details === "string" ? v.details : "";
};
var norm = function(t){ return String(t || "").trim().replace(/\s+/g, " ").toLowerCase(); };
var keyOf = function(values, details){ return D.cats.map(function(c){ return values[c.id]; }).join("|") + "|" + norm(details); };
base = keyOf(D.start, "");  /* his current look: a remembered choice holds only while it is still the newest */
var selects = document.querySelectorAll("select[data-cat]"), notes = $("forge-details");
var tiles = document.querySelectorAll(".look-tile[data-look]");

var render = function(){
  var key = keyOf(state, state.details), look = null;
  D.looks.forEach(function(l){ if (!look && keyOf(l.values, l.details) === key) { look = l; } });
  Array.prototype.forEach.call(selects, function(s){ s.value = state[s.getAttribute("data-cat")]; });
  if (look) { $("forge-img").src = look.full; $("forge-img").alt = look.alt; $("forge-zoom").href = look.full; }
  $("forge-zoom").hidden = !look;
  $("forge-empty").hidden = !!look;
  $("forge-name").textContent = look ? look.name : "A new look";
  $("forge-state").textContent = look ? "in the lookbook" : "not painted yet";
  $("forge-result").innerHTML = look ? "<b>Painted.</b> This look is in the lookbook."
    : "<b>Not painted yet.</b> The prompt below paints it.";
  Array.prototype.forEach.call(tiles, function(t){ t.setAttribute("aria-current", String(!!look && t.getAttribute("data-look") === look.id)); });
  var refs = D.refs.slice();
  Array.prototype.forEach.call(document.querySelectorAll("[data-ref-for]"), function(card){
    var on = state[card.getAttribute("data-ref-for").split(".")[0]] === card.getAttribute("data-ref-for").split(".")[1];
    card.hidden = !on;
    if (on) { refs.push(D.optRefs[card.getAttribute("data-ref-for")]); }
  });
  Array.prototype.forEach.call(document.querySelectorAll("[data-from]"), function(el){
    var o = pieces[el.getAttribute("data-from")][state[el.getAttribute("data-from")]];
    el.textContent = o.from;
    if (o.href) { var a = document.createElement("a"); a.href = o.href; a.textContent = o.story; el.appendChild(a); }
  });
  var n = 0;
  Array.prototype.forEach.call(document.querySelectorAll(".ref-card"), function(card){
    if (!card.hidden) { n += 1; card.querySelector(".ref-n").textContent = "Image " + n; }
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
Array.prototype.forEach.call(selects, function(s){
  s.addEventListener("change", function(){ state[s.getAttribute("data-cat")] = s.value; render(); });
});
Array.prototype.forEach.call(tiles, function(t){
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
