<script>
(function () {
  var media = matchMedia("(hover:hover) and (pointer:fine)");
  var openTimer = null, closeTimer = null, origin = null, returning = false;
  function cancel() { clearTimeout(openTimer); clearTimeout(closeTimer); }
  function panelFor(term) {
    return document.getElementById(term.getAttribute("aria-details"));
  }
  function pinned() {
    return document.querySelector('.gloss:popover-open[data-gloss-open="click"]');
  }
  function remember(term, gloss) {
    if (!term.id) { term.id = "gloss-origin-" + Date.now().toString(36); }
    origin = term.id;
    gloss.dataset.glossOrigin = term.id;
  }
  function setPinned(gloss, value) {
    gloss.dataset.glossOpen = value ? "click" : "hover";
    var pin = gloss.querySelector('.gloss-pin');
    if (pin) { pin.setAttribute('aria-pressed', String(value)); pin.textContent = value ? 'Unpin' : 'Pin'; }
  }
  function hide(gloss, restore) {
    var previous = returning;
    returning = true;
    try {
      gloss.hidePopover();
      var term = restore && document.getElementById(gloss.dataset.glossOrigin);
      if (term) term.focus({preventScroll:true});
    } finally { returning = previous; }
  }
  function close(gloss) {
    cancel();
    hide(gloss, true);
  }
  document.addEventListener('toggle', function (ev) {
    var gloss = ev.target;
    if (!gloss.classList || !gloss.classList.contains('gloss')) return;
    var pin = gloss.querySelector('.gloss-pin');
    if (pin) pin.hidden = false;
  }, true);
  document.addEventListener('focusin', function (ev) {
    var term = ev.target.closest && ev.target.closest('.term');
    if (!term || pinned() || returning) return;
    var gloss = panelFor(term);
    if (!gloss || !gloss.showPopover) return;
    remember(term, gloss);
    setPinned(gloss, false);
    if (!gloss.matches(':popover-open')) gloss.showPopover();
  });
  document.addEventListener('focusout', function (ev) {
    if (returning) return;
    var term = ev.target.closest && ev.target.closest('.term');
    var gloss = (ev.target.closest && ev.target.closest('.gloss')) || (term && panelFor(term));
    if (!gloss || gloss.dataset.glossOpen !== 'hover') return;
    if (ev.relatedTarget && (gloss.contains(ev.relatedTarget) || ev.relatedTarget === term)) return;
    if (gloss.hidePopover) hide(gloss, false);
  });
  document.addEventListener('keydown', function (ev) {
    var term = ev.target.closest && ev.target.closest('.term');
    var gloss = ev.target.closest && ev.target.closest('.gloss');
    if (term && ev.key === 'ArrowDown') {
      gloss = panelFor(term);
      if (!gloss || !gloss.showPopover) return;
      ev.preventDefault();
      remember(term, gloss); setPinned(gloss, true);
      if (!gloss.matches(':popover-open')) gloss.showPopover();
      gloss.querySelector('a,button').focus();
    } else if (ev.key === 'Escape') {
      gloss = gloss || (term && panelFor(term));
      if (gloss && gloss.matches(':popover-open')) { ev.preventDefault(); close(gloss); }
    }
  });
  document.addEventListener("pointerenter", function (ev) {
    if (!media.matches) return;
    var term = ev.target.closest && ev.target.closest(".term");
    var panel = ev.target.closest && ev.target.closest(".gloss");
    clearTimeout(closeTimer);
    if (!term || pinned()) { return; }
    openTimer = setTimeout(function () {
      if (pinned()) { return; }
      var gloss = panelFor(term);
      if (gloss && gloss.showPopover) {
        remember(term, gloss); setPinned(gloss, false);
        if (!gloss.matches(':popover-open')) gloss.showPopover();
      }
    }, 180);
  }, true);
  document.addEventListener("pointerleave", function (ev) {
    if (!media.matches) return;
    var term = ev.target.closest && ev.target.closest(".term");
    var panel = ev.target.closest && ev.target.closest(".gloss");
    if (!term && !panel) { return; }
    clearTimeout(openTimer);
    closeTimer = setTimeout(function () {
      var gloss = panel || (term && panelFor(term));
      if (gloss && gloss.dataset.glossOpen === "hover") { hide(gloss, false); }
    }, 260);
  }, true);
  document.addEventListener("click", function (ev) {
    var term = ev.target.closest && ev.target.closest(".term");
    if (term) {
      var gloss = panelFor(term);
      if (gloss && gloss.showPopover) {
        ev.preventDefault();
        remember(term, gloss); setPinned(gloss, true);
        if (!gloss.matches(':popover-open')) gloss.showPopover();
      }
    }
    var pin = ev.target.closest && ev.target.closest('.gloss-pin');
    if (pin) { var gloss = pin.closest('.gloss'); setPinned(gloss, gloss.dataset.glossOpen !== 'click'); }
    var closer = ev.target.closest && ev.target.closest('.gloss-close');
    if (closer && closer.closest('.gloss').hidePopover) {
      ev.preventDefault(); close(closer.closest('.gloss'));
    }
    var more = ev.target.closest && ev.target.closest(".gloss-more a");
    if (more) {
      var panel = more.closest(".gloss");
      var entry = document.querySelector(more.getAttribute("href"));
      if (origin && entry) {
        var back = entry.nextElementSibling && entry.nextElementSibling.querySelector(".gloss-back");
        if (back) { back.href = "#" + origin; back.textContent = "Back to the text"; }
      }
      if (panel) { hide(panel, false); }
    }
  }, true);
  ["scroll", "pointerdown", "keydown", "visibilitychange"].forEach(function (name) {
    addEventListener(name, cancel, true);
  });
})();
</script>