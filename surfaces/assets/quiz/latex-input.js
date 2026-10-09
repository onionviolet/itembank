<script id="latex-input-adapter">
(function () {
  function install(textarea, host) {
    if (!textarea || textarea.dataset.latexReady === "true") return;
    textarea.dataset.latexReady = "true";
    textarea.spellcheck = false;
    textarea.setAttribute("autocapitalize", "none");
    textarea.placeholder = "Type LaTeX source, for example x^2 + 2x + 1";
    var note = document.createElement("p");
    note.className = "latex-entry-note";
    note.textContent = "Enter LaTeX source. The exact source is saved; the preview does not grade it.";
    var preview = document.createElement("div");
    preview.className = "latex-preview";
    preview.setAttribute("aria-label", "Rendered LaTeX preview");
    host.appendChild(note);
    host.appendChild(preview);
    function render() {
      var source = textarea.value.trim();
      if (!source) {
        preview.dataset.previewState = "empty";
        preview.textContent = "Preview appears here.";
        return;
      }
      preview.dataset.previewState = "source";
      preview.textContent = source;
      if (typeof window.katex !== "undefined") {
        try {
          window.katex.render(source, preview, {displayMode:true,
            throwOnError:false, trust:false, maxExpand:1000, maxSize:50});
          preview.dataset.previewState = "rendered";
        } catch (error) {
          preview.textContent = source;
        }
      }
    }
    textarea.addEventListener("input", render);
    render();
  }
  function scan(root) {
    root = root || document;
    if (root.matches && root.matches('textarea[data-input-format="latex"]')) {
      install(root, root.parentNode);
    }
    root.querySelectorAll('textarea[data-input-format="latex"]')
      .forEach(function (textarea) { install(textarea, textarea.parentNode); });
  }
  window.ItembankLatexInput = {install:install, scan:scan};
  var host = document.getElementById("host");
  if (!host) { return; }
  var pending = new Set();
  var scheduled = false;
  function flush() {
    scheduled = false;
    if (document.hidden) { return; }
    pending.forEach(function (root) {
      if (root.isConnected) { scan(root); }
    });
    pending.clear();
  }
  function schedule() {
    if (!scheduled && !document.hidden) {
      scheduled = true;
      window.requestAnimationFrame(flush);
    }
  }
  function queue(node) {
    if (node.nodeType !== 1) { return; }
    if (node.matches('textarea[data-input-format="latex"]') ||
        node.querySelector('textarea[data-input-format="latex"]')) {
      for (var root of pending) {
        if (root.contains(node)) { return; }
        if (node.contains(root)) { pending.delete(root); }
      }
      pending.add(node);
      schedule();
    }
  }
  pending.add(host);
  flush();
  new MutationObserver(function (records) {
    records.forEach(function (record) {
      record.addedNodes.forEach(queue);
    });
  }).observe(host, {childList:true, subtree:true});
  document.addEventListener("visibilitychange", schedule);
})();
</script>