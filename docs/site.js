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
if (reduce) { document.documentElement.classList.add("reduce"); }
})();
