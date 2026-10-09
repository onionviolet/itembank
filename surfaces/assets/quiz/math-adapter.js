<script id="quiz-math-adapter">
(function () {
  var host = document.getElementById("host");
  if (!host) { return; }
  var observer;
  var scheduled = false;
  var pending = new Set();
  function expressionNodes(root) {
    var expressions = root.querySelectorAll(".stem,.ot,.rowtext");
    if (root.matches && root.matches(".stem,.ot,.rowtext")) {
      expressions = [root].concat(Array.from(expressions));
    }
    expressions.forEach(function (el) {
      if (el.querySelector(".katex,.quiz-math-source")) { return; }
      Array.from(el.childNodes).forEach(function (node) {
        if (node.nodeType !== 3 || node.nodeValue.indexOf("`") < 0) { return; }
        var parts = node.nodeValue.split(/(`[^`\n]+`)/g);
        if (parts.length < 2) { return; }
        var frag = document.createDocumentFragment();
        parts.forEach(function (part) {
          if (part.length > 1 && part[0] === "`" && part[part.length - 1] === "`") {
            var code = document.createElement("code");
            code.className = "quiz-math-source";
            code.textContent = part.slice(1, -1);
            frag.appendChild(code);
          } else if (part) {
            frag.appendChild(document.createTextNode(part));
          }
        });
        node.parentNode.replaceChild(frag, node);
      });
    });
  }
  function note(text) {
    if (host.querySelector(".quiz-math-note")) { return; }
    var n = document.createElement("p");
    n.className = "quiz-math-note";
    n.textContent = text;
    host.appendChild(n);
  }
  function enhance() {
    scheduled = false;
    if (document.hidden) { return; }
    if (observer) { observer.disconnect(); }
    pending.forEach(function (root) {
      if (!root.isConnected) { return; }
      expressionNodes(root);
      var hasMath = (root.matches && root.matches(".quiz-math-source")) ||
        root.querySelector(".quiz-math-source") ||
        /\$\$?[\s\S]+?\$\$?/.test(root.textContent || "");
      if (!hasMath) { return; }
      if (typeof window.katex === "undefined" ||
          typeof window.renderMathInElement !== "function") {
        note("Math unavailable. Formula source is shown.");
        return;
      }
      try {
        renderMathInElement(root, {
          delimiters: [
            {left: "$$", right: "$$", display: true},
            {left: "$", right: "$", display: false}
          ],
          ignoredTags: ["pre", "script", "noscript", "style", "textarea"],
          throwOnError: false,
          trust: false,
          maxExpand: 1000,
          maxSize: 50
        });
        var sources = root.querySelectorAll(".quiz-math-source:not([data-math-rendered])");
        if (root.matches && root.matches(".quiz-math-source:not([data-math-rendered])")) {
          sources = [root].concat(Array.from(sources));
        }
        sources.forEach(function (el) {
          var source = el.textContent;
          try {
            katex.render(source, el, {throwOnError:false, trust:false,
              maxExpand:1000, maxSize:50});
            el.dataset.mathRendered = "true";
          } catch (e) {
            el.textContent = source;
          }
        });
        root.querySelectorAll(".katex-display").forEach(function (el) {
          if (el.parentNode.classList.contains("quiz-math-display")) { return; }
          var wrap = document.createElement("div");
          wrap.className = "quiz-math-display";
          el.parentNode.insertBefore(wrap, el);
          wrap.appendChild(el);
        });
      } catch (e) {
        note("Math could not be rendered. Formula source is shown.");
      }
    });
    pending.clear();
    if (observer) { observer.observe(host, {childList:true, subtree:true}); }
  }
  function schedule() {
    if (!scheduled && !document.hidden) {
      scheduled = true;
      window.requestAnimationFrame(enhance);
    }
  }
  function queue(node) {
    var el = node.nodeType === 1 ? node : node.parentElement;
    if (!el || !el.isConnected) { return; }
    var root = el.closest(".stem,.ot,.rowtext") || el;
    if (root.closest(".latex-preview")) { return; }
    if ((root.matches && root.matches(".quiz-math-source")) ||
        root.querySelector(".quiz-math-source") ||
        /[`$]/.test(root.textContent || "")) {
      for (var existing of pending) {
        if (existing.contains(root)) { return; }
        if (root.contains(existing)) { pending.delete(existing); }
      }
      pending.add(root);
    }
  }
  observer = new MutationObserver(function (records) {
    records.forEach(function (record) {
      record.addedNodes.forEach(queue);
    });
    if (pending.size) { schedule(); }
  });
  pending.add(host);
  enhance();
  document.addEventListener("visibilitychange", schedule);
})();
</script>