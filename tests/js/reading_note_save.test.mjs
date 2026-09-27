import test from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { JSDOM } from "jsdom";
import { python } from "./python_bin.mjs";

const script = execFileSync(python, ["-c", `
from surfaces.reading_desk import SCRIPT
print(SCRIPT.replace('__CONTEXT__', '{"course_id":"course","expected_fingerprint":"course-revision","occurrence_id":"occurrence","revision_id":"revision"}'))
`], { cwd: new URL("../..", import.meta.url), encoding: "utf8" });

const html = `
<p id="reading-state"></p><p id="source-state"></p><div id="source-content"></div>
<button id="mark-read" disabled>I have read this range</button>
<p id="note-state"></p><textarea id="note"></textarea>
<button id="save-note" disabled>Save to my notes</button><p id="save-state"></p>
<div id="saved-notes"></div>`;

const view = () => ({
  reading_state: { state: "not-reported" },
  availability: { state: "available", message: "Available" },
  content: "Source text", note_error: null, notes: [], notes_fingerprint: null,
});
const response = body => ({ ok: true, json: async () => body });
const deferred = () => {
  let resolve;
  const promise = new Promise(done => { resolve = done; });
  return { promise, resolve };
};
const settle = () => new Promise(done => setImmediate(done));

async function setup() {
  const dom = new JSDOM(html, { url: "http://localhost/", runScripts: "outside-only" });
  const { window } = dom;
  const requests = [];
  const saves = [];
  let ids = 0;
  Object.defineProperty(window.crypto, "randomUUID", {
    value: () => `note-${++ids}`, configurable: true,
  });
  window.fetch = (url, options) => {
    const body = JSON.parse(options.body);
    requests.push({ url, body });
    if (url.endsWith("/save-reading-note")) {
      const pending = deferred();
      saves.push(pending);
      return pending.promise;
    }
    if (url.endsWith("/confirm-reading")) return Promise.resolve(response({ intent_id: "intent" }));
    if (url.endsWith("/declare-reading")) return Promise.resolve(response({ status: "saved" }));
    return Promise.resolve(response(view()));
  };
  window.eval(script);
  await settle();
  const get = id => window.document.getElementById(id);
  const type = wording => {
    get("note").value = wording;
    get("note").dispatchEvent(new window.Event("input", { bubbles: true }));
  };
  return { dom, window, get, type, requests, saves };
}

test("typing during a pending save keeps the newer draft and its unsaved state", async () => {
  const app = await setup();
  try {
    app.type("First wording");
    app.get("save-note").click();
    assert.equal(app.requests.at(-1).body.wording, "First wording");
    app.type("Newer wording");
    app.saves[0].resolve(response({ status: "saved" }));
    await settle();
    assert.equal(app.get("note").value, "Newer wording");
    assert.match(app.get("save-state").textContent, /Current draft is unsaved/);
    app.get("save-note").click();
    assert.equal(app.requests.at(-1).body.wording, "Newer wording");
    assert.notEqual(app.requests.at(-1).body.note_id, "note1");
    app.saves[1].resolve(response({ status: "saved" }));
    await settle();
  } finally { app.dom.window.close(); }
});

test("an unchanged successful save clears only its submitted draft", async () => {
  const app = await setup();
  try {
    app.type("Finished note");
    app.get("save-note").click();
    app.saves[0].resolve(response({ status: "saved" }));
    await settle();
    assert.equal(app.get("note").value, "");
    assert.equal(app.get("save-state").textContent, "Saved to your notes.");
    assert.equal(app.get("save-note").disabled, false);
  } finally { app.dom.window.close(); }
});

test("an uncertain failure preserves wording and retries its original note identity", async () => {
  const app = await setup();
  try {
    app.type("Keep this wording");
    app.get("save-note").click();
    app.saves[0].resolve({ ok: false });
    await settle();
    assert.equal(app.get("note").value, "Keep this wording");
    assert.match(app.get("save-state").textContent, /Keep your draft/);
    app.get("save-note").click();
    assert.equal(app.requests.at(-1).body.note_id, "note1");
    assert.equal(app.requests.at(-1).body.wording, "Keep this wording");
    app.saves[1].resolve(response({ status: "saved" }));
    await settle();
  } finally { app.dom.window.close(); }
});

test("editing after an uncertain failure uses a new identity for new wording", async () => {
  const app = await setup();
  try {
    app.type("Possibly saved");
    app.get("save-note").click();
    app.type("Distinct new note");
    app.saves[0].resolve({ ok: false });
    await settle();
    assert.equal(app.get("note").value, "Distinct new note");
    app.get("save-note").click();
    assert.equal(app.requests.at(-1).body.wording, "Distinct new note");
    assert.equal(app.requests.at(-1).body.note_id, "note2");
    app.saves[1].resolve(response({ status: "saved" }));
    await settle();
  } finally { app.dom.window.close(); }
});

test("a reading refresh cannot re-enable save during a pending request", async () => {
  const app = await setup();
  try {
    app.type("One request");
    app.get("save-note").click();
    app.get("mark-read").click();
    await settle();
    assert.equal(app.get("save-note").disabled, true);
    app.get("save-note").dispatchEvent(new app.window.Event("click"));
    assert.equal(app.saves.length, 1);
    app.saves[0].resolve(response({ status: "saved" }));
    await settle();
    assert.equal(app.get("save-note").disabled, false);
  } finally { app.dom.window.close(); }
});
