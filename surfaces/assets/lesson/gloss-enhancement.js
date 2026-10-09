<script>
(function () {
  var LOADING = %(loading)s;
  var UNAVAILABLE = %(unavailable)s;
  document.addEventListener("click", function (ev) {
    var t = ev.target && ev.target.closest
        ? ev.target.closest("[data-gloss-fetch]") : null;
    if (!t) { return; }
    var panel = document.getElementById(t.getAttribute("aria-details"));
    var def = panel && panel.querySelector(".gloss-def");
    if (!def) { return; }
    ev.preventDefault();
    if (panel.showPopover && !panel.matches(':popover-open')) { panel.showPopover(); }
    if (def.getAttribute("data-gloss-state") === "done") { return; }
    def.textContent = LOADING;
    def.setAttribute("data-gloss-state", "loading");
    fetch(t.getAttribute("data-gloss-fetch"))
      .then(function (r) { return r.json(); })
      .then(function (d) {
        def.textContent = d && d.def ? d.def : UNAVAILABLE;
        def.setAttribute("data-gloss-state", "done");
      })
      .catch(function () {
        def.textContent = UNAVAILABLE;
        def.setAttribute("data-gloss-state", "done");
      });
  }, true);
})();
</script>