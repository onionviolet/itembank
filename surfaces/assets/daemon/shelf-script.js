<script>
(function () {
  var status = document.querySelector("[data-shelf-status]");
  document.querySelectorAll("form[data-shelf-form]").forEach(function (form) {
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      var button = event.submitter || form.querySelector("button[name=action]");
      if (!button) { return; }
      if (status) { status.textContent = "Working..."; }
      fetch("/api/shelf", {
        method: "POST", headers: {"Content-Type": "application/json"},
        body: JSON.stringify({action: button.value})
      }).then(function (response) {
        if (!response.ok) { throw new Error("That action was refused."); }
        window.location.href = "/";
      }).catch(function (error) {
        if (status) { status.textContent = error.message; }
      });
    });
  });

  var shelf = document.querySelector("[data-course-shelf]");
  if (!shelf) { return; }
  var fingerprint = shelf.getAttribute("data-workspace-fingerprint") || null;
  var dragging = null;
  var pointerStartOrder = null;
  var pointerId = null;
  var pointerMoved = false;
  var saving = false;

  function cards() { return Array.from(shelf.querySelectorAll("[data-course-id]")); }
  function ids() { return cards().map(function (card) { return card.dataset.courseId; }); }
  function sameOrder(left, right) {
    return left.length === right.length && left.every(function (id, index) {
      return id === right[index];
    });
  }
  function restore(order) {
    var focused = shelf.contains(document.activeElement) ? document.activeElement : null;
    order.forEach(function (id) {
      var card = shelf.querySelector('[data-course-id="' + CSS.escape(id) + '"]');
      if (card) { shelf.appendChild(card); }
    });
    syncButtons();
    if (focused && focused.isConnected) { focused.focus(); }
  }
  function syncButtons() {
    var rows = cards();
    rows.forEach(function (card, index) {
      var mark = card.querySelector('.course-mark');
      if (mark) { mark.textContent = String(index + 1).padStart(2, '0'); }
      var up = card.querySelector('[data-move="up"]');
      var down = card.querySelector('[data-move="down"]');
      if (up) { up.disabled = saving || index === 0; }
      if (down) { down.disabled = saving || index === rows.length - 1; }
    });
    var focus = document.querySelector('.desk-focus');
    var first = rows.find(function (row) { return row.dataset.resumable === 'true'; }) || rows[0];
    if (focus && first) {
      var action = first.querySelector('.course-card-actions a');
      var focusAction = focus.querySelector('.desk-focus-actions a');
      focus.querySelector('h2').textContent = first.querySelector('h2').textContent;
      focus.querySelector('.resume-cue').textContent = first.querySelector('.resume-cue').textContent;
      focus.querySelector('.desk-eyebrow').textContent = first.dataset.resumable === 'true'
        ? 'Continue a saved session' : 'First in your course order';
      var context = focus.querySelector('.desk-session-context');
      context.textContent = first.dataset.sessionContext || '';
      context.hidden = !context.textContent;
      focusAction.textContent = action.textContent;
      focusAction.setAttribute('aria-label', action.getAttribute('aria-label'));
      focusAction.href = action.href;
    }
  }
  function saveOrder(previous) {
    if (sameOrder(previous, ids())) { syncButtons(); return Promise.resolve(); }
    var failureMessage = "Could not confirm the saved course order. Reload to check it before trying again.";
    saving = true;
    syncButtons();
    if (status) { status.textContent = "Saving course order..."; }
    return fetch("/api/shelf", {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({action: "reorder_courses", course_ids: ids(),
                           expected_fingerprint: fingerprint})
    }).then(function (response) {
      if (!response.ok) {
        if (response.status === 409) {
          failureMessage = "Course order changed elsewhere. Reload and try again.";
        } else if (response.status >= 400 && response.status < 500) {
          failureMessage = "Course order could not be saved. Reload and try again.";
        }
        throw new Error(failureMessage);
      }
      return response.json();
    }).then(function (result) {
      if (!result || typeof result.fingerprint !== "string" || !result.fingerprint) {
        throw new Error(failureMessage);
      }
      fingerprint = result.fingerprint;
      shelf.setAttribute("data-workspace-fingerprint", fingerprint);
      saving = false;
      if (status) { status.textContent = "Course order saved."; }
      syncButtons();
    }).catch(function () {
      saving = false;
      restore(previous);
      if (status) { status.textContent = failureMessage; }
    });
  }

  shelf.addEventListener("click", function (event) {
    var button = event.target.closest("button[data-move]");
    if (!button || saving) { return; }
    var card = button.closest("[data-course-id]");
    var rows = cards();
    var index = rows.indexOf(card);
    var target = button.dataset.move === "up" ? rows[index - 1] : rows[index + 1];
    if (!target) { return; }
    var previous = ids();
    if (button.dataset.move === "up") { shelf.insertBefore(card, target); }
    else { shelf.insertBefore(target, card); }
    syncButtons();
    saveOrder(previous);
    var summary = card.querySelector('.course-details summary');
    if (summary) { summary.focus(); }
  });

  shelf.addEventListener("pointerdown", function (event) {
    var handle = event.target.closest("[data-drag-handle]");
    if (!handle || saving || dragging || event.isPrimary === false || event.button !== 0) { return; }
    dragging = handle.closest("[data-course-id]");
    pointerStartOrder = ids();
    pointerId = event.pointerId;
    pointerMoved = false;
    dragging.classList.add("is-dragging");
    shelf.setPointerCapture(pointerId);
    event.preventDefault();
  });
  shelf.addEventListener("pointermove", function (event) {
    if (!dragging || event.pointerId !== pointerId) { return; }
    var under = document.elementFromPoint(event.clientX, event.clientY);
    var target = under && under.closest("[data-course-id]");
    if (!target || target === dragging || !shelf.contains(target)) { return; }
    var box = target.getBoundingClientRect();
    shelf.insertBefore(dragging, event.clientY < box.top + box.height / 2
                       ? target : target.nextSibling);
    pointerMoved = true;
    event.preventDefault();
  });
  shelf.addEventListener("pointerup", function (event) {
    if (!dragging || event.pointerId !== pointerId) { return; }
    var previous = pointerStartOrder;
    dragging.classList.remove("is-dragging");
    dragging = null;
    pointerStartOrder = null;
    pointerId = null;
    shelf.releasePointerCapture(event.pointerId);
    if (pointerMoved) { saveOrder(previous); }
    pointerMoved = false;
  });
  function cancelDrag(returnFocus) {
    if (!dragging) { return; }
    var previous = pointerStartOrder;
    var handle = dragging.querySelector('[data-drag-handle]');
    var capturedPointer = pointerId;
    dragging.classList.remove("is-dragging");
    dragging = null;
    pointerStartOrder = null;
    pointerId = null;
    pointerMoved = false;
    restore(previous);
    if (shelf.hasPointerCapture && shelf.hasPointerCapture(capturedPointer)) {
      shelf.releasePointerCapture(capturedPointer);
    }
    if (returnFocus && handle) { handle.focus(); }
    if (status) { status.textContent = "Course move cancelled."; }
  }
  shelf.addEventListener("pointercancel", function (event) {
    if (event.pointerId === pointerId) { cancelDrag(false); }
  });
  shelf.addEventListener("lostpointercapture", function (event) {
    if (event.pointerId === pointerId) { cancelDrag(false); }
  });
  document.addEventListener("keydown", function (event) {
    if (dragging && event.key === "Escape") {
      event.preventDefault();
      cancelDrag(true);
    }
  });
  syncButtons();
})();
</script>