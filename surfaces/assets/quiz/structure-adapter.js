<script id="quiz-structure-adapter">
(function () {
  var host = document.getElementById("host");
  if (!host) { return; }
  var observer;
  var scheduled = false;
  var pending = new Set();
  function sentences(text) {
    var source = String(text || "").trim();
    if (!source) { return []; }
    var parts = [];
    var start = 0;
    var ambiguous = false;
    function nextNonSpace(at) {
      while (at < source.length && /\s/.test(source[at])) { at += 1; }
      return at;
    }
    function isBoundary(at) {
      var mark = source[at];
      if (mark !== "." && mark !== "!" && mark !== "?") { return false; }
      var next = nextNonSpace(at + 1);
      if (mark === "." && /\d/.test(source[at - 1] || "") &&
          /\d/.test(source[next] || "")) { return false; }
      var before = source.slice(0, at + 1);
      if (mark === "." && /(?:\b(?:mr|mrs|ms|dr|prof|sr|jr|st|vs|etc|e\.g|i\.e))\.$/i.test(before)) {
        ambiguous = true;
        return false;
      }
      if (next < source.length && !/[A-Z\u00c0-\u024f\u201c\"]/.test(source[next])) {
        ambiguous = true;
        return false;
      }
      return next >= source.length || /\s/.test(source[at + 1] || "");
    }
    for (var index = 0; index < source.length; index += 1) {
      if (!isBoundary(index)) { continue; }
      parts.push(source.slice(start, index + 1).trim());
      start = nextNonSpace(index + 1);
      index = start - 1;
    }
    if (start < source.length) { parts.push(source.slice(start).trim()); }
    return ambiguous ? [source] : parts.filter(Boolean);
  }
  function formatArgument(el) {
    if (el.dataset.structureRendered === "true") { return; }
    el.dataset.structureRendered = "true";
    var text = el.textContent || "";
    var match = text.match(/^([\s\S]*?\bargument\s*:\s*)["\u201c]([^"\u201d]+)["\u201d]([\s\S]*)$/i);
    if (!match) { return; }
    var lines = sentences(match[2]);
    if (lines.length < 2 || !/^(therefore|thus|hence)\b/i.test(lines[lines.length - 1])) {
      return;
    }
    var fragment = document.createDocumentFragment();
    if (match[1]) { fragment.appendChild(document.createTextNode(match[1].trim())); }
    var group = document.createElement("span");
    group.className = "quiz-argument";
    group.setAttribute("role", "list");
    group.setAttribute("aria-label", "Argument structure");
    lines.forEach(function (line, index) {
      var row = document.createElement("span");
      row.className = "quiz-argument-line";
      row.setAttribute("role", "listitem");
      var label = document.createElement("span");
      label.className = "quiz-argument-label";
      label.textContent = index === lines.length - 1 ? "Conclusion" :
        "Premise " + (index + 1);
      var body = document.createElement("span");
      body.className = "quiz-argument-text";
      body.textContent = line;
      row.appendChild(label);
      row.appendChild(body);
      group.appendChild(row);
    });
    fragment.appendChild(group);
    if (match[3]) { fragment.appendChild(document.createTextNode(match[3])); }
    el.replaceChildren(fragment);
  }
  function enhance() {
    scheduled = false;
    if (document.hidden) { return; }
    if (observer) { observer.disconnect(); }
    pending.forEach(function (el) {
      if (el.isConnected) { formatArgument(el); }
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
    if (!el) { return; }
    var stem = el.closest(".stem");
    if (stem) { pending.add(stem); }
    if (el.matches(".stem")) { pending.add(el); }
    el.querySelectorAll(".stem").forEach(function (item) { pending.add(item); });
  }
  observer = new MutationObserver(function (records) {
    records.forEach(function (record) {
      record.addedNodes.forEach(queue);
    });
    if (pending.size) { schedule(); }
  });
  host.querySelectorAll(".stem").forEach(function (el) { pending.add(el); });
  enhance();
  document.addEventListener("visibilitychange", schedule);
})();
</script>