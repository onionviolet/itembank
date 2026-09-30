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
<button id="resume-reading" hidden>Resume previous reading position</button>
<p id="reading-state"></p><p id="source-state"></p><div id="source-content"></div>
<button id="mark-read" disabled>I have read this range</button>
<p id="note-state"></p><div id="previous-drafts"></div><textarea id="note"></textarea>
<button id="save-note" disabled>Save to my notes</button><p id="save-state"></p>
<div id="saved-notes"></div>`;

const view = () => ({
  occurrence: { source_ref: { source_fingerprint: "source-revision" } },
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

test("stale-source refresh explains recovery without exposing an internal code", async () => {
  const currentView = view();
  currentView.content = null;
  currentView.availability = { state: "course.reading_source_stale" };
  const app = await setup({ currentView });
  try {
    assert.match(app.get("source-state").textContent, /The source changed/);
    assert.match(app.get("source-state").textContent, /source binding/);
    assert.doesNotMatch(app.get("source-state").textContent, /course\.reading/);
    assert.equal(app.get("save-note").disabled, true);
  } finally { app.dom.window.close(); }
});

async function setup({ stored = null, currentView = view() } = {}) {
  const dom = new JSDOM(html, { url: "http://localhost/", runScripts: "outside-only" });
  const { window } = dom;
  const requests = [];
  const saves = [];
  const continuityKey = 'itembank-reading:["course","occurrence","revision"]';
  if (stored) window.sessionStorage.setItem(continuityKey, stored);
  const scrolls = [];
  window.scrollTo = options => scrolls.push(options);
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
    return Promise.resolve(response(currentView));
  };
  window.eval(script);
  await settle();
  const get = id => window.document.getElementById(id);
  const type = wording => {
    get("note").value = wording;
    get("note").dispatchEvent(new window.Event("input", { bubbles: true }));
  };
  return { dom, window, get, type, requests, saves, continuityKey, scrolls };
}

test("a long-source detour recovers local wording and resumes position only on request", async () => {
  const first = await setup({ currentView: { ...view(), content: "Synthetic paragraph.\n".repeat(600) } });
  first.type("Local wording awaiting review");
  first.get("note").focus();
  Object.defineProperty(first.window, "scrollY", { value: 2400 });
  first.window.dispatchEvent(new first.window.Event("pagehide"));
  const stored = first.window.sessionStorage.getItem(first.continuityKey);
  first.dom.window.close();
  const returned = await setup({ stored });
  try {
    assert.equal(returned.get("note").value, "Local wording awaiting review");
    assert.match(returned.get("save-state").textContent, /local unsaved draft/);
    assert.equal(returned.saves.length, 0, "returning cannot accept a note");
    assert.equal(returned.scrolls.length, 0, "navigation cannot move focus or scroll silently");
    returned.get("resume-reading").click();
    assert.equal(returned.window.document.activeElement, returned.get("note"));
    assert.equal(returned.scrolls[0].top, 2400);
    returned.get("save-note").click();
    returned.saves[0].resolve(response({ status: "saved" }));
    await settle();
    assert.equal(JSON.parse(returned.window.sessionStorage.getItem(returned.continuityKey)).draft, "");
  } finally { returned.dom.window.close(); }
});

test("changed or unavailable source bytes cannot recover a prior draft or position", async () => {
  const stored = JSON.stringify({ source: "source-revision", y: 900, draft: "Stale wording" });
  for (const currentView of [
    { ...view(), occurrence: { source_ref: { source_fingerprint: "different-source" } } },
    { ...view(), content: null },
  ]) {
    const app = await setup({ stored, currentView });
    try {
      assert.equal(app.get("note").value, "");
      assert.equal(app.get("resume-reading").disabled, true);
      assert.match(app.get("resume-reading").textContent, /were not restored/);
      assert.equal(app.scrolls.length, 0);
      assert.equal(app.saves.length, 0);
      const recovery = app.get("previous-drafts").querySelector("textarea");
      assert.equal(recovery.value, "Stale wording");
      assert.equal(recovery.readOnly, true);
      app.window.dispatchEvent(new app.window.Event("pagehide"));
      assert.equal(app.window.sessionStorage.getItem(app.continuityKey), stored,
        "leaving a changed source cannot overwrite the prior draft");
      app.type("New-source wording");
      assert.match(app.get("save-state").textContent, /Copy this new wording/);
      app.window.dispatchEvent(new app.window.Event("pagehide"));
      assert.equal(app.window.sessionStorage.getItem(app.continuityKey), stored);
    } finally { app.dom.window.close(); }
  }
});

test("a reload after an uncertain save retries the same note identity", async () => {
  const first = await setup();
  first.type("Possibly accepted wording");
  first.get("save-note").click();
  const originalId = first.requests.at(-1).body.note_id;
  first.saves[0].resolve({ ok: false });
  await settle();
  const stored = first.window.sessionStorage.getItem(first.continuityKey);
  first.dom.window.close();
  const returned = await setup({ stored });
  try {
    returned.get("save-note").click();
    assert.equal(returned.requests.at(-1).body.note_id, originalId);
    assert.equal(returned.requests.at(-1).body.wording, "Possibly accepted wording");
    returned.saves[0].resolve(response({ status: "saved" }));
    await settle();
  } finally { returned.dom.window.close(); }
});

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
