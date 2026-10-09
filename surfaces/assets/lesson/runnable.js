<script>
(function () {
  "use strict";
  var content = document.getElementById("lesson-content");
  if (!content) { return; }
  var C = %(copies)s;
  var sessionId = content.getAttribute("data-run-session") || "";
  // One delegated handler; each block carries its own state in the DOM and
  // an in-flight flag, so blocks never share source/status/output/request.
  content.addEventListener("click", function (ev) {
    var btn = ev.target;
    if (!btn || btn.className !== "run-go" || btn.disabled) { return; }
    run(btn);
  });
  function blockOf(btn) {
    var el = btn.parentNode;
    while (el && !el.hasAttribute("data-code-block")) { el = el.parentNode; }
    return el;
  }
  function statusOf(block) {
    var el = block.querySelector(".run-status");
    return el || block.appendChild(document.createElement("p"));
  }
  function setStatus(block, text, isError) {
    var s = statusOf(block);
    s.className = "run-status" + (isError ? " run-error" : "");
    if (isError) {
      s.setAttribute("role", "alert");
      s.setAttribute("aria-live", "assertive");
    } else {
      s.removeAttribute("role");
      s.setAttribute("aria-live", "off");
    }
    s.textContent = text;
  }
  function fillOut(block, cls, text) {
    var pre = block.querySelector(cls);
    pre.textContent = text.length ? text : %(no_output)s;
  }
  // Tab inserts a tab, Shift-Tab dedents, Escape arms the next Tab to leave
  // the editor (09-UI-SPEC "CS runnable prose").
  content.addEventListener("keydown", function (ev) {
    var t = ev.target;
    if (!t || t.className !== "run-source") { return; }
    if (ev.key === "Tab") {
      if (t.dataset.escapeArmed === "1") {
        delete t.dataset.escapeArmed;
        return;                      // native focus move leaves the editor
      }
      ev.preventDefault();
      var val = t.value, at = t.selectionStart, end = t.selectionEnd;
      if (ev.shiftKey) {
        var lineStart = val.lastIndexOf("\n", at - 1) + 1;
        var ind = val.slice(lineStart, lineStart + 4);
        var drop = ind.indexOf("\t") === 0 ? 1
                 : (ind.indexOf("    ") === 0 ? 4 : 0);
        t.value = val.slice(0, lineStart) + val.slice(lineStart + drop);
        t.setSelectionRange(Math.max(lineStart, at - drop),
                            Math.max(lineStart, end - drop));
      } else {
        t.value = val.slice(0, at) + "\t" + val.slice(end);
        t.setSelectionRange(at + 1, at + 1);
      }
    } else if (ev.key === "Escape") {
      t.dataset.escapeArmed = "1";
    } else {
      delete t.dataset.escapeArmed;
    }
  });
  function run(btn) {
    var block = blockOf(btn);
    var ta = block.querySelector(".run-source");
    var lang = block.getAttribute("data-lang") || "";
    var id = block.getAttribute("data-code-block");
    btn.disabled = true;
    setStatus(block, C.running, false);
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/api/lesson/run", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onload = function () {
      btn.disabled = false;
      var body = null;
      try { body = JSON.parse(xhr.responseText); } catch (e) { body = null; }
      if (xhr.status !== 200 || !body) {
        setStatus(block, C.request_error, true);
        return;
      }
      if (body.refused) {
        setStatus(block, body.refused, true);
        return;
      }
      if (body.timed_out) { setStatus(block, C.timed_out, true); }
      else if (body.truncated) { setStatus(block, C.truncated, true); }
      else { setStatus(block, C.completed.replace("{code}", String(body.exit_code)), false); }
      fillOut(block, ".run-stdout", body.stdout || "");
      fillOut(block, ".run-stderr", body.stderr || "");
    };
    xhr.onerror = function () {
      btn.disabled = false;
      setStatus(block, C.request_error, true);
    };
    var payload = {session_id: sessionId, block_id: id, language: lang,
                   source: ta.value};
    xhr.send(JSON.stringify(payload));
  }
})();
</script>