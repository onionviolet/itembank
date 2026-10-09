import test from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { JSDOM } from "jsdom";
import { python } from "./python_bin.mjs";

const html = execFileSync(python, ["-c", `
import sys
sys.path.insert(0, 'tests')
from ui_overhaul_workspace_roundtrip import reading_page
print(reading_page())
`], { cwd: new URL("../..", import.meta.url), encoding: "utf8" });

const key = 'itembank-reading:["synthetic","synthetic-reading","revision-one"]:workspace';
const settle = () => new Promise(done => setImmediate(done));

async function setup(stored = null, blocked = false, storageKey = key) {
  const dom = new JSDOM(html, { url: "http://localhost/", runScripts: "outside-only" });
  const { window } = dom;
  const requests = [];
  window.scrollTo = () => {};
  window.matchMedia = () => ({ matches: false, addEventListener() {} });
  if (stored !== null) window.sessionStorage.setItem(storageKey, stored);
  if (blocked) Object.defineProperty(window, "sessionStorage", {
    get() { throw new Error("Storage refused"); }, configurable: true,
  });
  window.fetch = async (url, options) => {
    requests.push({ url, body: JSON.parse(options.body) });
    return { ok: true, json: async () => ({
      occurrence: { source_ref: { source_fingerprint: "source-revision" } },
      reading_state: { state: "not-reported" }, availability: { state: "available" },
      content: "The same source passage.", notes: [], note_error: null,
    }) };
  };
  const script = Array.from(window.document.scripts).find(row => row.textContent.includes("const ctx="));
  window.eval(script.textContent);
  await settle();
  const get = id => window.document.getElementById(id);
  const mode = name => window.document.querySelector(`[data-reading-mode-button="${name}"]`).click();
  return { dom, window, get, mode, requests };
}

test("reading modes retain local wording and never save or declare reading", async () => {
  const app = await setup();
  try {
    const field = app.get("note");
    field.value = "My unfinished thought";
    field.dispatchEvent(new app.window.Event("input", { bubbles: true }));
    app.mode("read");
    assert.equal(app.window.document.querySelector(".reading-notes").hidden, true);
    app.mode("notebook");
    assert.equal(app.window.document.activeElement, field);
    assert.equal(field.value, "My unfinished thought");
    app.mode("study");
    assert.equal(field.value, "My unfinished thought");
    assert.deepEqual(app.requests.map(row => row.url), ["/api/course/reading-view"]);
    const prefs = app.window.sessionStorage.getItem(key);
    const restored = await setup(prefs);
    try {
      assert.equal(restored.window.document.querySelector(".reading-layout").dataset.readingMode, "study");
      assert.equal(restored.get("note").value, "", "view preferences cannot become learner notes");
    } finally { restored.dom.window.close(); }
  } finally { app.dom.window.close(); }
});

test("valid view preferences survive reopening without moving focus or accepting data", async () => {
  const app = await setup(JSON.stringify({ mode: "read", size: "22", measure: "58", width: "400" }));
  try {
    assert.equal(app.get("reading-size").value, "22");
    assert.equal(app.get("reading-measure").value, "58");
    assert.equal(app.get("companion-width").value, "400");
    assert.equal(app.get("companion-width").disabled, true);
    assert.equal(app.window.document.querySelector(".reading-notes").hidden, true);
    assert.equal(app.window.document.activeElement, app.window.document.body);
    app.get("reading-note-open").click();
    assert.equal(app.window.document.querySelector(".reading-layout").dataset.readingMode, "notebook");
    assert.equal(app.get("source-content").tabIndex, 0);
    app.window.document.querySelector(".reading-return").click();
    assert.equal(app.window.document.querySelector(".reading-layout").dataset.readingMode, "read");
    assert.equal(app.window.document.activeElement, app.get("source-content"));
    assert.equal(app.get("source-content").tabIndex, -1);
    assert.deepEqual(app.requests.map(row => row.url), ["/api/course/reading-view"]);
  } finally { app.dom.window.close(); }
});

test("malformed preferences and unavailable storage keep the usable study desk", async () => {
  for (const [stored, blocked] of [
    ["{broken", false], [JSON.stringify({ mode: "constructor", size: "900", measure: "2" }), false],
    [null, true],
  ]) {
    const app = await setup(stored, blocked);
    try {
      assert.equal(app.get("reading-size").value, "18");
      assert.equal(app.get("reading-measure").value, "70");
      assert.equal(app.window.document.querySelector(".reading-notes").hidden, false);
      app.mode("read");
      app.mode("notebook");
      assert.equal(app.window.document.activeElement, app.get("note"));
    } finally { app.dom.window.close(); }
  }
});

test("a different reading revision cannot restore the prior workspace choices", async () => {
  const app = await setup(JSON.stringify({ mode: "read", size: "22", measure: "58" }),
                          false, key.replace("revision-one", "revision-old"));
  try {
    assert.equal(app.get("reading-size").value, "18");
    assert.equal(app.get("reading-measure").value, "70");
    assert.equal(app.window.document.querySelector(".reading-layout").dataset.readingMode, "study");
    assert.equal(app.window.document.querySelector(".reading-notes").hidden, false);
  } finally { app.dom.window.close(); }
});
