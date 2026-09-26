import test from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { JSDOM } from "jsdom";
import { python } from "./python_bin.mjs";

const fixture = JSON.parse(execFileSync(python, ["-c", `
import json
from surfaces import daemon
cards = [
    {"course_id": "first", "name": "Logic and proofs",
     "attention": "ready", "token": "ready", "chip": "Ready",
     "resume_cue": "No sessions yet", "cta_href": "/course/first",
     "cta_label": "Start Logic and proofs", "actions": (), "degraded": False},
    {"course_id": "second", "name": "Biology field notes",
     "attention": "needs_input", "token": "needs-input", "chip": "Needs input",
     "resume_cue": "Choose a recorded session", "cta_href": "/course/second",
     "cta_label": "Choose Biology field notes", "actions": (), "degraded": False},
]
shelf = {"cards": cards, "reorderable": True,
         "workspace_fingerprint": "sha256:before",
         "empty_heading": "No courses yet", "empty_body": "Add a course"}
print(json.dumps({"body": daemon._course_shelf_body(shelf),
                  "script": daemon.SHELF_SCRIPT}))
`], { cwd: new URL("../..", import.meta.url), encoding: "utf8" }));

function setup(response) {
  const dom = new JSDOM(fixture.body, {
    url: "http://localhost/", runScripts: "outside-only",
  });
  const { window } = dom;
  window.CSS = { escape: value => value };
  const requests = [];
  window.fetch = (url, options) => {
    requests.push({ url, options });
    return Promise.resolve(response);
  };
  window.eval(fixture.script.replace(/^<script[^>]*>|<\/script>$/g, ""));
  const shelf = window.document.querySelector("[data-course-shelf]");
  shelf.setPointerCapture = () => {};
  shelf.releasePointerCapture = () => {};
  const focus = window.document.querySelector(".desk-focus");
  const status = window.document.querySelector("[data-shelf-status]");
  const order = () => [...shelf.querySelectorAll("[data-course-id]")]
    .map(card => card.dataset.courseId);
  const marks = () => [...shelf.querySelectorAll(".course-mark")]
    .map(mark => mark.textContent);
  const lead = () => ({
    title: focus.querySelector("h2").textContent,
    cue: focus.querySelector(".resume-cue").textContent,
    label: focus.querySelector(".desk-focus-actions a").textContent,
    accessibleLabel: focus.querySelector(".desk-focus-actions a").getAttribute("aria-label"),
    href: new URL(focus.querySelector(".desk-focus-actions a").href).pathname,
  });
  return { dom, window, shelf, focus, status, requests, order, marks, lead };
}

async function settle() {
  await new Promise(resolve => setImmediate(resolve));
}

function pointer(window, target, type, properties = {}) {
  const event = new window.Event(type, { bubbles: true, cancelable: true });
  for (const [name, value] of Object.entries({
    pointerId: 1, pointerType: "mouse", button: 0, clientX: 40,
    clientY: 10, ...properties,
  })) {
    Object.defineProperty(event, name, { value });
  }
  target.dispatchEvent(event);
}

test("visible drag handle saves a mouse reorder", async () => {
  const app = setup({ ok: true, json: () => Promise.resolve({
    fingerprint: "sha256:after", course_ids: ["second", "first"],
  }) });
  try {
    const first = app.shelf.querySelector('[data-course-id="first"]');
    const second = app.shelf.querySelector('[data-course-id="second"]');
    const handle = first.querySelector('[data-drag-handle]');
    assert.equal(handle.closest("details"), null, "drag must be visible without opening options");
    assert.match(handle.textContent, /Drag/);
    second.getBoundingClientRect = () => ({ top: 0, height: 100 });
    app.window.document.elementFromPoint = () => second;
    pointer(app.window, handle, "pointerdown");
    pointer(app.window, app.shelf, "pointermove", { clientY: 90 });
    pointer(app.window, app.shelf, "pointerup", { clientY: 90 });
    await settle();
    assert.deepEqual(app.order(), ["second", "first"]);
    assert.equal(app.status.textContent, "Course order saved.");
    assert.deepEqual(JSON.parse(app.requests[0].options.body).course_ids,
      ["second", "first"]);
  } finally {
    app.dom.window.close();
  }
});

test("cancelled touch drag restores the original order", () => {
  const app = setup({ ok: true, json: () => Promise.resolve({}) });
  try {
    const first = app.shelf.querySelector('[data-course-id="first"]');
    const second = app.shelf.querySelector('[data-course-id="second"]');
    second.getBoundingClientRect = () => ({ top: 0, height: 100 });
    app.window.document.elementFromPoint = () => second;
    pointer(app.window, first.querySelector('[data-drag-handle]'),
      "pointerdown", { pointerType: "touch" });
    pointer(app.window, app.shelf, "pointermove",
      { pointerType: "touch", clientY: 90 });
    pointer(app.window, app.shelf, "pointercancel", { pointerType: "touch" });
    assert.deepEqual(app.order(), ["first", "second"]);
    assert.equal(app.requests.length, 0);
  } finally {
    app.dom.window.close();
  }
});

test("move down saves the rendered shelf order and updates its lead", async () => {
  const app = setup({ ok: true, json: () => Promise.resolve({
    fingerprint: "sha256:after", course_ids: ["second", "first"],
  }) });
  try {
    assert.deepEqual(app.order(), ["first", "second"]);
    assert.deepEqual(app.marks(), ["01", "02"]);
    assert.equal(app.lead().label, "Start");
    assert.equal(app.lead().accessibleLabel, "Start Logic and proofs");
    const move = app.shelf.querySelector('[data-course-id="first"] [data-move="down"]');
    move.closest('details').open = true;
    move.focus();
    move.click();
    await settle();
    assert.deepEqual(app.order(), ["second", "first"]);
    assert.deepEqual(app.marks(), ["01", "02"]);
    assert.deepEqual(app.lead(), {
      title: "Biology field notes", cue: "Choose a recorded session",
      label: "Choose", accessibleLabel: "Choose Biology field notes", href: "/course/second",
    });
    assert.equal(app.shelf.dataset.workspaceFingerprint, "sha256:after");
    assert.equal(app.status.textContent, "Course order saved.");
    assert.equal(app.window.document.activeElement,
      app.shelf.querySelector('[data-course-id="first"] summary'),
      "the moved row must keep a usable keyboard focus target");
    assert.equal(app.requests.length, 1);
    assert.equal(app.requests[0].url, "/api/shelf");
    assert.deepEqual(JSON.parse(app.requests[0].options.body), {
      action: "reorder_courses", course_ids: ["second", "first"],
      expected_fingerprint: "sha256:before",
    });
  } finally {
    app.dom.window.close();
  }
});

test("rejected save restores the rendered order, lead, and status", async () => {
  const app = setup({ ok: false });
  try {
    const move = app.shelf.querySelector('[data-course-id="first"] [data-move="down"]');
    move.closest('details').open = true;
    move.focus();
    move.click();
    await settle();
    assert.deepEqual(app.order(), ["first", "second"]);
    assert.deepEqual(app.marks(), ["01", "02"]);
    assert.deepEqual(app.lead(), {
      title: "Logic and proofs", cue: "No sessions yet",
      label: "Start", accessibleLabel: "Start Logic and proofs", href: "/course/first",
    });
    assert.equal(app.shelf.dataset.workspaceFingerprint, "sha256:before");
    assert.equal(app.status.textContent,
      "Course order changed elsewhere. Reload and try again.");
    assert.equal(app.requests.length, 1);
    assert.equal(app.window.document.activeElement,
      app.shelf.querySelector('[data-course-id="first"] summary'),
      "rollback must restore focus with the moved course");
  } finally {
    app.dom.window.close();
  }
});
