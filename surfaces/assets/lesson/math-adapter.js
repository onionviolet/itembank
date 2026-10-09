<script>
(function () {
  var content = document.getElementById("lesson-content");
  if (!content) { return; }
  var note = function (cls, text) {
    var n = document.createElement("p");
    n.className = cls;
    n.textContent = text;
    return n;
  };
  if (typeof window.katex === "undefined" ||
      typeof window.renderMathInElement !== "function") {
    content.appendChild(note("lesson-math-note", %(unavailable)s));
    return;
  }
  var displays = content.querySelectorAll(".katex-display");
  try {
    renderMathInElement(content, {
      delimiters: [
        {left: "$$", right: "$$", display: true},
        {left: "$", right: "$", display: false}
      ],
      ignoredTags: ["pre", "code", "script", "noscript", "style", "textarea"],
      throwOnError: false,
      trust: false,
      maxExpand: 1000,
      maxSize: 50
    });
  } catch (e) {
    content.appendChild(note("lesson-math-note", %(parse_failure)s));
    return;
  }
  // Display math owns its horizontal overflow in a named wrapper
  // (09-UI-SPEC Responsive): auto-render emits `.katex-display`, and the
  // page wraps each in `.lesson-math-display` so a wide formula scrolls
  // inside the card instead of widening the viewport.
  content.querySelectorAll(".katex-display").forEach(function (el) {
    var wrap = document.createElement("div");
    wrap.className = "lesson-math-display";
    el.parentNode.insertBefore(wrap, el);
    wrap.appendChild(el);
  });
  // One parse failure leaves KaTeX's own error node (the source, readable)
  // plus the exact explanatory note beside it; no error handler deletes it.
  content.querySelectorAll(".katex-error").forEach(function (el) {
    if (el.parentNode.classList.contains("lesson-math-note")) { return; }
    var n = note("lesson-math-note", %(parse_failure)s);
    el.parentNode.insertBefore(n, el.nextSibling);
  });
})();
</script>