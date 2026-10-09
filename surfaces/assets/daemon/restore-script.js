<script>
(function () {
  var KEY = "itembank.ia.restore";
  function contextOffset() {
    var bar = document.querySelector("[data-surface-context]");
    return bar ? bar.offsetHeight : 0;
  }
  function fullyInView(el) {
    var r = el.getBoundingClientRect();
    return r.top >= 0 && r.bottom <= (window.innerHeight ||
      document.documentElement.clientHeight);
  }
  function focusHeading() {
    var h1 = document.querySelector("h1");
    if (h1) { h1.tabIndex = -1; h1.focus({preventScroll: true}); }
  }
  function revealMissing() {
    var note = document.querySelector("[data-anchor-missing]");
    if (note) { note.removeAttribute("hidden"); }
  }
  function restoreStored() {
    var raw = null;
    try { raw = window.sessionStorage.getItem(KEY); } catch (e) { return; }
    if (!raw) { return; }
    var saved = null;
    try { saved = JSON.parse(raw); } catch (e) { return; }
    if (!saved || saved.path !== location.pathname) { return; }
    window.scrollTo(0, saved.scrollY || 0);
    var prior = saved.activeId && document.getElementById(saved.activeId);
    if (prior) { prior.tabIndex = -1; prior.focus({preventScroll: true}); }
    else { focusHeading(); }
  }
  function onLoad() {
    var hash = location.hash;
    if (!hash) { restoreStored(); return; }
    var target = document.getElementById(hash.slice(1));
    if (!target) { focusHeading(); revealMissing(); return; }
    if (!fullyInView(target)) {
      target.scrollIntoView({block: "start"});
      window.scrollBy(0, -contextOffset());
    }
    target.tabIndex = -1;
    target.focus({preventScroll: true});
  }
  window.addEventListener("pagehide", function () {
    var active = document.activeElement;
    try {
      window.sessionStorage.setItem(KEY, JSON.stringify({
        path: location.pathname, hash: location.hash,
        scrollY: window.scrollY,
        activeId: active && active.id ? active.id : ""
      }));
    } catch (e) { /* a browser refusing storage loses only the cue */ }
  });
  var dirty = false;
  function warnOnUnsaved(e) {
    if (!dirty) { return; }
    e.preventDefault();
    e.returnValue = "";
  }
  document.addEventListener("input", function (e) {
    if (e.target && e.target.closest("form")) {
      dirty = true;
      window.addEventListener("beforeunload", warnOnUnsaved);
    }
  });
  document.addEventListener("submit", function () {
    dirty = false;
    window.removeEventListener("beforeunload", warnOnUnsaved);
  });
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", onLoad);
  } else { onLoad(); }
})();
</script>