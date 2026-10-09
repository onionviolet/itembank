import test from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { JSDOM, VirtualConsole } from "jsdom";
import { python } from "./python_bin.mjs";

const markup = JSON.parse(execFileSync(python, ["-c", `
import contextlib, io, json, os, sys, tempfile
sys.path.insert(0, os.path.join(os.getcwd(), "tests"))
from day_edit_roundtrip import HEADER, write_plan, row_for
from surfaces import day
with tempfile.TemporaryDirectory(prefix="day-workspace-js-") as root:
    plan = write_plan(root, [HEADER, row_for("2026-10-04", ["Fictional reading", "Invented proof", "Synthetic code"])])
    with contextlib.redirect_stdout(io.StringIO()):
        state = day.day_state(plan, os.path.join(root, "daily_log.md"),
                              os.path.join(root, "lanes.md"), "2026-10-04", base="/day/plan")
        page = day.day_render(state).decode("utf-8")
    print(json.dumps(page))
`], { cwd: new URL("../..", import.meta.url), encoding: "utf8" }));

function setup() {
  const console = new VirtualConsole();
  console.on("jsdomError", error => {
    if (!error.message.includes("Not implemented: navigation")) throw error;
  });
  const dom = new JSDOM(markup, { url: "http://localhost/day/plan", runScripts: "outside-only", virtualConsole: console });
  const { window } = dom;
  const requests = [];
  const handles = [];
  let nativeStatus = "";
  Object.defineProperty(window, "status", { configurable: true,
    get: () => nativeStatus, set: value => { nativeStatus = String(value); } });
  window.XMLHttpRequest = class {
    open(method, url) { this.method = method; this.url = url; }
    setRequestHeader() {}
    send(body) {
      requests.push({ method: this.method, url: this.url, body: body ? JSON.parse(body) : null });
      handles.push(this);
    }
  };
  const script = [...window.document.scripts].find(node => node.textContent.startsWith("window.__day__="));
  assert.ok(script, "the served day script is present");
  window.eval(script.textContent);
  return { dom, window, document: window.document, requests, handles };
}

test("the native day editor opens, retains changes and discards without opening a notes file", () => {
  const { dom, window, document, requests } = setup();
  try {
    const button = document.getElementById("edit-btn");
    assert.ok(button, "Edit plan is reachable");
    button.click();
    assert.ok(document.getElementById("editor").classList.contains("on"));
    const field = document.querySelector(".day-edit");
    assert.equal(document.activeElement, field);
    const original = field.value;
    field.value = "A revised fictional reading";
    field.dispatchEvent(new window.Event("input", { bubbles: true }));
    assert.equal(document.getElementById("save-edits").disabled, false);
    document.getElementById("discard-edits").click();
    assert.equal(field.value, original);
    assert.equal(document.getElementById("save-edits").disabled, true);
    assert.deepEqual(requests, [], "discard is local and never opens a notes file");
  } finally { dom.window.close(); }
});

test("day ticks send checked lanes and editor confirmation never records a tick", () => {
  const { dom, window, document, requests } = setup();
  try {
    for (const lane of ["EMT", "Math", "Anki"]) {
      const box = document.querySelector('.lane input[name="' + lane + '"]');
      box.checked = true;
      box.dispatchEvent(new window.Event("change", { bubbles: true }));
    }
    assert.deepEqual(requests.at(-1), { method: "POST", url: "/day/plan/save",
      body: { date: "2026-10-04", done: ["EMT", "Math", "Anki"] } });
    assert.match(document.getElementById("verdict").textContent, /Floor met/);
    const before = requests.length;
    const confirmation = document.getElementById("force-confirm");
    confirmation.checked = true;
    confirmation.dispatchEvent(new window.Event("change", { bubbles: true }));
    assert.equal(requests.length, before, "force confirmation grants no tick action");
    assert.equal(document.getElementById("force-btn").disabled, false);
  } finally { dom.window.close(); }
});

test("save sends only changed plan cells to their existing owner", () => {
  const { dom, window, document, requests } = setup();
  try {
    document.getElementById("edit-btn").click();
    const field = document.querySelector(".day-edit");
    field.value = "A revised fictional reading";
    field.dispatchEvent(new window.Event("input", { bubbles: true }));
    document.getElementById("save-edits").click();
    assert.equal(requests.length, 1);
    assert.equal(requests[0].url, "/day/plan/edit");
    assert.equal(requests[0].method, "POST");
    assert.deepEqual(requests[0].body.edits, { [field.name]: "A revised fictional reading" });
    assert.ok(requests[0].body.revision);
    assert.match(document.getElementById("edit-status").textContent, /Saving/);
  } finally { dom.window.close(); }
});

test("a saved plan clears its unsaved-navigation guard before reloading", () => {
  const { dom, window, document, handles } = setup();
  try {
    document.getElementById("edit-btn").click();
    const field = document.querySelector(".day-edit");
    field.value = "Saved fictional reading";
    field.dispatchEvent(new window.Event("input", { bubbles: true }));
    const dirty = new window.Event("beforeunload", { cancelable: true });
    window.dispatchEvent(dirty);
    assert.equal(dirty.defaultPrevented, true);
    document.getElementById("save-edits").click();
    handles[0].responseText = JSON.stringify({ status: "saved", revision: "saved-revision",
      cells: { ...window.__day__.snapshot.cells, [field.name]: field.value } });
    handles[0].onload();
    assert.match(document.getElementById("edit-status").textContent, /Saved/);
    const saved = new window.Event("beforeunload", { cancelable: true });
    window.dispatchEvent(saved);
    assert.equal(saved.defaultPrevented, false, "successful save must not block its own reload");
  } finally { dom.window.close(); }
});

test("interrupted and unreadable save responses retain the draft and expose recovery", () => {
  for (const event of ["network", "unreadable"]) {
    const { dom, window, document, handles } = setup();
    try {
      document.getElementById("edit-btn").click();
      const field = document.querySelector(".day-edit");
      field.value = "Recoverable fictional draft";
      field.dispatchEvent(new window.Event("input", { bubbles: true }));
      document.getElementById("save-edits").click();
      if (event === "network") handles[0].onerror();
      else { handles[0].responseText = "not-json"; handles[0].onload(); }
      assert.equal(field.value, "Recoverable fictional draft");
      assert.equal(document.getElementById("save-edits").disabled, false);
      assert.ok(document.getElementById("edit-recovery").classList.contains("on"));
      assert.match(document.getElementById("edit-status").textContent, /Retry|reload/);
    } finally { dom.window.close(); }
  }
});
