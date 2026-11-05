/* THE UNKNEELING — the Forge (darrow/wardrobe.html). Build a look a step at a time from the pieces he has earned, see
   it on the stage if it has been painted, with its pieces and why each is his, and copy (or, on a phone, share) the
   prompt that paints it, with the Look line Claude files it by. Its data is the JSON in #forge-data, written by the
   build: the pieces in step order, each with its short reason (tag) and its reason in full (why, HTML), and the pairs
   that cannot be worn together (the build's wardrobe_clash). Each category is a picker in the page: a row that opens a
   tray of cards, or a row of chips; a tap on an open piece wears it, a tap on any piece shows why under the tray. Each
   step offers only what goes with the steps before it; when an earlier choice changes, a later piece that no longer
   goes with it falls back to his own look's, or the first that fits, and the Forge says so. The choice is remembered
   in this browser only. wardrobe.html#piece-<category>-<piece> opens that piece's card (the Collection links there). */
(function(){
"use strict";
var dataEl = document.getElementById("forge-data");
if (!dataEl) { return; }
var D = JSON.parse(dataEl.textContent), SAVE = "unkneeling-forge", state = {}, peek = {}, refsNow = [], base;
var $ = function(id){ return document.getElementById(id); };
var each = function(list, fn){ Array.prototype.forEach.call(list, fn); };
var esc = function(s){ return String(s).replace(/[&<>"]/g, function(c){ return {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]; }); };
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
  peek = {};
  settle(0);
};
var norm = function(t){ return String(t || "").trim().replace(/\s+/g, " ").toLowerCase(); };
var keyOf = function(values, details){ return D.cats.map(function(c){ return values[c.id]; }).join("|") + "|" + norm(details); };
base = keyOf(D.start, "");  /* his current look: a remembered choice holds only while it is still the newest */
var pks = document.querySelectorAll(".pk[data-cat]"), notes = $("forge-details"), tiles = document.querySelectorAll(".look-tile[data-look]");

var place = function(info, card, t){  /* the reason opens under the row of the card it is about, not at the foot of a long tray */
  var grid = card && !card.hidden ? card.parentNode : null;
  if (!grid || !grid.classList.contains("pk-grid")) { t.appendChild(info); return; }
  var row = Array.prototype.filter.call(grid.children, function(x){ return x.hasAttribute("data-id") && !x.hidden && x.offsetTop === card.offsetTop; });
  var last = row[row.length - 1] || card;
  if (last.nextElementSibling !== info) { last.after(info); }
};
var paint = function(pk){  /* one picker: what goes with the earlier steps, the one chosen, and why (the chosen, or the one last tapped) */
  var cat = pk.getAttribute("data-cat"), ci = at[cat], shown = 0, open = 0;
  each(pk.querySelectorAll("[data-id]"), function(b){
    var id = b.getAttribute("data-id"), ok = goes(ci, id);
    b.hidden = !ok;
    if (ok) { shown += 1; open += pieces[cat][id].open ? 1 : 0; }
    b.setAttribute("aria-checked", String(state[cat] === id));
    b.classList.toggle("peek", peek[cat] === id && state[cat] !== id);
  });
  each(pk.querySelectorAll(".pk-grid[data-g]"), function(g){
    var any = !!g.querySelector("[data-id]:not([hidden])"), h = pk.querySelector('.pk-g[data-g="' + g.getAttribute("data-g") + '"]');
    g.hidden = !any;
    if (h) { h.hidden = !any; }
  });
  var o = pieces[cat][state[cat]], q = pieces[cat][peek[cat]] || o, el;
  if ((el = pk.querySelector(".pk-cur"))) { el.textContent = o.name; }
  if ((el = pk.querySelector(".pk-tag"))) { el.textContent = o.tag; }
  if ((el = pk.querySelector(".pk-cnt"))) { el.textContent = open + " of " + shown + " open"; }
  if ((el = pk.querySelector(".pk-info"))) {
    if (!pk.querySelector(".pk-tray")) { el.hidden = !peek[cat]; }  /* chips and who: the reason waits for a tap */
    el.innerHTML = q.why;
    el.classList.toggle("locked", !q.open);
    var t = pk.querySelector(".pk-tray");
    if (t && !t.hidden) { place(el, pk.querySelector('[data-id="' + q.id + '"]'), t); }
  }
};

var tray = function(pk, open){
  var row = pk.querySelector(".pk-row"), t = pk.querySelector(".pk-tray");
  if (row && t) { row.setAttribute("aria-expanded", String(open)); t.hidden = !open; }
};
var reveal = function(pk){  /* keep an opened tray in sight: the one above it may just have closed */
  var top = pk.getBoundingClientRect().top;
  if (top < 0 || top > window.innerHeight * 0.6) { pk.scrollIntoView({block: "start", behavior: "smooth"}); }
};
var toggle = function(pk){
  var open = pk.querySelector(".pk-row").getAttribute("aria-expanded") !== "true";
  each(pks, function(x){ if (x !== pk) { tray(x, false); } });
  tray(pk, open);
  if (open) { paint(pk); reveal(pk); }
};
var goTo = function(cat, id){  /* open a picker on a piece: from the stage's list, or a link from the Collection */
  var pk = document.querySelector('.pk[data-cat="' + cat + '"]');
  if (!pk) { return; }
  if (id && pieces[cat][id]) { peek[cat] = id; }
  if (pk.querySelector(".pk-row")) { each(pks, function(x){ tray(x, x === pk); }); }
  render();
  var card = id && $("piece-" + cat + "-" + id), shown = card && !card.hidden && card.offsetParent;
  (shown ? card : pk).scrollIntoView({block: shown ? "center" : "start", behavior: "smooth"});
};

var details = function(look){  /* under the stage: the pieces on it, each with the short reason it is his */
  var list = $("look-pieces");
  if (!list) { return; }
  var rows = D.cats.map(function(c){
    var o = pieces[c.id][state[c.id]];
    return '<li><button type="button" data-goto="' + esc(c.id) + '"><span class="k">' + esc(c.label) + '</span><span class="v"><b>' + esc(o.name)
      + '</b><span class="t">' + esc(o.tag) + '</span></span></button></li>';
  });
  if (state.details.trim()) { rows.push('<li><span class="k">Small touches</span><span class="v"><b>' + esc(state.details.trim()) + '</b></span></li>'); }
  list.innerHTML = rows.join("");
  $("look-detail").hidden = false;
  $("look-wear-row").hidden = !look || look.worn;
  $("look-wear").setAttribute("data-name", look ? look.name : "");
};

var render = function(){
  var key = keyOf(state, state.details), look = null;
  D.looks.forEach(function(l){ if (!look && keyOf(l.values, l.details) === key) { look = l; } });
  each(pks, paint);
  if (look) { $("forge-img").src = look.full; $("forge-img").alt = look.alt; $("forge-zoom").href = look.full; }
  $("forge-zoom").hidden = !look;
  $("forge-empty").hidden = !!look;
  $("forge-name").textContent = look ? look.name : "A new look";
  $("forge-state").textContent = look ? (look.worn ? "his look now" : "in the lookbook") : "not painted yet";
  $("forge-result").innerHTML = look ? "<b>Painted.</b> This look is in the lookbook."
    : "<b>Not painted yet.</b> The prompt below paints it.";
  each(tiles, function(t){ t.setAttribute("aria-current", String(!!look && t.getAttribute("data-look") === look.id)); });
  details(look);
  var refs = D.refs.slice(), n = 0;
  each(document.querySelectorAll(".ref-card"), function(card){
    var k = card.getAttribute("data-ref-for"), on = !k || state[k.split(".")[0]] === k.split(".")[1];
    card.hidden = !on;
    if (on && k) { refs.push(D.optRefs[k]); }
    if (on) { n += 1; card.querySelector(".ref-n").textContent = "Image " + n; }
  });
  refsNow = refs;
  var design = D.cats.map(function(c){ return "- " + c.label + ": " + pieces[c.id][state[c.id]].prompt; }).join("\n");
  var listed = refs.map(function(r, i){ return "Image " + (i + 1) + " (" + r.file + "): " + r.use; }).join("\n");
  /* the background: a chroma screen Claude keys out (engine/looks.py); green when the look wears blue, so the screen never eats it */
  var screen = /blue/i.test(design) ? "chroma green (#00FF00)" : "chroma blue (#0000FF)";
  $("forge-prompt").value = D.template.split("{references}").join(listed).split("{design}").join(design).split("{screen}").join(screen)
    .split("{details}").join(state.details.trim() || "none");
  $("forge-line").textContent = "Look: " + D.cats.map(function(c){ return c.id + "=" + state[c.id]; }).join(" ")
    + (state.details.trim() ? " · touches: " + state.details.trim() : "");
  try { localStorage.setItem(SAVE, JSON.stringify({base: base, state: state})); } catch (e) { /* the choice is only a convenience */ }
};

var choose = function(cat, id){
  state[cat] = id;
  peek[cat] = id;
  var moved = settle(at[cat] + 1), note = $("forge-fit");
  note.textContent = moved.length ? "To go with that: " + moved.join("; ") + "." : "";
  note.hidden = !moved.length;
  render();
};

var copy = function(text, btn, fallback, done, manualLabel){
  var label = btn.getAttribute("data-label") || btn.textContent;
  btn.setAttribute("data-label", label);
  var said = function(msg){ btn.textContent = msg; setTimeout(function(){ btn.textContent = label; }, 2200); };
  var manual = function(){ fallback(); said(manualLabel || "Selected: copy it"); };
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(function(){ said("Copied"); if (done) { done(); } }, manual);
  } else { manual(); }
};

/* Share: on a phone, the prompt and the references go to ChatGPT in one go (the share sheet); the prompt is copied too,
   for an app that takes the pictures and leaves the words. The pictures are fetched once, when the prompt comes near. */
var files = {};
var fetchRef = function(r){
  if (files[r.href]) { return Promise.resolve(files[r.href]); }
  return fetch(r.href).then(function(res){ if (!res.ok) { throw new Error("not found"); } return res.blob(); })
    .then(function(b){ return (files[r.href] = new File([b], r.file, {type: b.type || "image/jpeg"})); });
};
var canShare = false;
try {
  canShare = !!(navigator.share && navigator.canShare && window.matchMedia && matchMedia("(pointer: coarse)").matches
    && navigator.canShare({files: [new File(["x"], "x.jpg", {type: "image/jpeg"})]}));
} catch (e) { canShare = false; }
if (canShare && $("forge-share")) {
  $("forge-share").hidden = false;
  $("forge-share-step").hidden = false;
  each(document.querySelectorAll(".forge-manual"), function(li){ li.hidden = true; });
  var warm = function(){ refsNow.forEach(function(r){ fetchRef(r).catch(function(){}); }); };
  if (window.IntersectionObserver) {
    new IntersectionObserver(function(es, ob){ if (es.some(function(x){ return x.isIntersecting; })) { warm(); } }, {rootMargin: "600px"}).observe($("forge-prompt"));
  } else { warm(); }
  $("forge-share").addEventListener("click", function(){
    var text = $("forge-prompt").value, refs = refsNow.slice(), note = $("forge-share-note");
    if (navigator.clipboard && navigator.clipboard.writeText) { navigator.clipboard.writeText(text).catch(function(){}); }
    var send = function(list){ return navigator.share({files: list, text: text}); };
    var ready = refs.every(function(r){ return files[r.href]; });
    (ready ? send(refs.map(function(r){ return files[r.href]; })) : Promise.all(refs.map(fetchRef)).then(send)).then(function(){
      note.hidden = true;
    }, function(err){
      if (err && err.name === "AbortError") { return; }
      note.textContent = err && err.name === "NotAllowedError" ? "The pictures are ready now: tap Share to ChatGPT again."
        : "This phone would not share them. Copy the prompt and download the references instead.";
      note.hidden = false;
      each(document.querySelectorAll(".forge-manual"), function(li){ li.hidden = false; });
    });
  });
}

wear(D.start);
try { var saved = JSON.parse(localStorage.getItem(SAVE) || "null"); if (saved && saved.base === base) { wear(saved.state); } } catch (e) { /* start from his look */ }
if (notes) {
  notes.value = state.details;
  if (state.details) { notes.closest("details").open = true; }
  notes.addEventListener("input", function(){ state.details = notes.value; render(); });
}
document.addEventListener("click", function(e){
  var t = e.target.closest ? e.target : e.target.parentNode;
  var row = t.closest(".pk-row");
  if (row) { toggle(row.closest(".pk")); return; }
  var b = t.closest(".pk [data-id]");
  if (b) {
    var cat = b.closest(".pk").getAttribute("data-cat"), id = b.getAttribute("data-id");
    if (pieces[cat][id].open && state[cat] !== id) { choose(cat, id); }
    else { peek[cat] = peek[cat] === id ? null : id; render(); }  /* a second tap on the same piece puts its reason away */
    return;
  }
  var more = t.closest("[data-more]");
  if (more) {
    var all = more.closest(".pk").classList.toggle("all");
    more.setAttribute("aria-expanded", String(all));
    more.lastChild.textContent = all ? "fewer" : more.getAttribute("data-more") + " more";
    return;
  }
  var g = t.closest("[data-goto]");
  if (g) { goTo(g.getAttribute("data-goto"), null); }
});
var resized;
window.addEventListener("resize", function(){ clearTimeout(resized); resized = setTimeout(function(){ each(pks, paint); }, 150); });
document.addEventListener("keydown", function(e){
  if (e.key !== "Escape") { return; }
  each(pks, function(pk){
    var row = pk.querySelector(".pk-row");
    if (row && row.getAttribute("aria-expanded") === "true") { tray(pk, false); row.focus(); }
  });
});
each(tiles, function(t){
  t.addEventListener("click", function(e){
    var look = D.looks.filter(function(l){ return l.id === t.getAttribute("data-look"); })[0];
    if (!look || e.metaKey || e.ctrlKey || e.shiftKey) { return; }
    e.preventDefault();
    wear(Object.assign({details: look.details}, look.values));
    if (notes) { notes.value = state.details; }
    $("forge-fit").hidden = true;
    render();
    $("forge-stage").scrollIntoView({behavior: "smooth", block: "start"});
  });
});
$("forge-copy").addEventListener("click", function(){
  copy($("forge-prompt").value, $("forge-copy"), function(){ $("forge-prompt").closest("details").open = true; $("forge-prompt").focus(); $("forge-prompt").select(); });
});
$("forge-copy-line").addEventListener("click", function(){
  copy($("forge-line").textContent, $("forge-copy-line"), function(){
    $("forge-line").closest("details").open = true;
    var r = document.createRange(); r.selectNodeContents($("forge-line"));
    var sel = window.getSelection(); sel.removeAllRanges(); sel.addRange(r);
  });
});
$("look-wear").addEventListener("click", function(){
  var msg = "Switch his look to “" + $("look-wear").getAttribute("data-name") + "”.", hint = $("look-wear-hint");
  copy(msg, $("look-wear"), function(){ hint.textContent = "Send Claude: " + msg; hint.hidden = false; },
    function(){ hint.textContent = "Copied. Send it to Claude, and this look goes on his page."; hint.hidden = false; }, "Copy it from below");
});
render();
var deep = /^#piece-([a-z]+)-([\w-]+)$/.exec(location.hash);
if (deep && pieces[deep[1]] && pieces[deep[1]][deep[2]]) {
  goTo(deep[1], deep[2]);
  window.addEventListener("load", function(){ goTo(deep[1], deep[2]); });
}
})();
