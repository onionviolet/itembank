// Exercise the generated no-baseline served page through its real controls.
// Only fetch is replaced. Runtime verdicts are synthetic public envelopes,
// so these tests never grade a response or reproduce a scoring authority.
import test from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { JSDOM, VirtualConsole } from "jsdom";
import { python } from "./python_bin.mjs";

const pages = JSON.parse(execFileSync(python, ["-c", `
import json, os, runpy, tempfile
from pathlib import Path
from surfaces import quiz
# An optional saved renderer provides red/green evidence without replacing
# shared checkout files. Normal runs always use the live generated page.
if os.environ.get("ITEMBANK_QUIZ_JS_BASELINE"):
    quiz.SERVED_JS = runpy.run_path(os.environ["ITEMBANK_QUIZ_JS_BASELINE"])["SERVED_JS"]
with tempfile.TemporaryDirectory() as tmp:
    bank = Path(tmp) / "synthetic.md"
    bank.write_text("# Synthetic transition checks\\n", encoding="utf-8")
    print(json.dumps({kind: quiz.page_for(str(bank), [{"id": "q1", "type": kind}],
        serve=True, bank_stem="synthetic", mode="practice")
        for kind in ("mc", "check")}))
`], { cwd: new URL("../..", import.meta.url), encoding: "utf8", maxBuffer: 8 * 1024 * 1024 }));

const flush = async () => {
  await new Promise(resolve => setTimeout(resolve, 0));
  await new Promise(resolve => setTimeout(resolve, 0));
};
const options = [
  { key: "A", text: "Alpha" }, { key: "B", text: "Beta" },
  { key: "C", text: "Gamma" }, { key: "D", text: "Delta" },
];

async function bootBaselineDraft(t, { saved, value, feedbackPause = false,
  control = "textarea" }) {
  const pause = feedbackPause ? " data-feedback-pause" : "";
  const field = control === "input"
    ? `<input type="text" name="fill_count" value="${value}">`
    : `<textarea name="answer">${value}</textarea>`;
  const baseline = `<div id="host"><div data-server-baseline${pause}
    data-session-id="session" data-item-id="q1" data-response-type="check">
    <form data-answer-form>${field}</form>
    </div></div>`;
  const html = pages.check[1].replace('<div id="host"></div>', baseline);
  const errors = [];
  let dispose;
  const console = new VirtualConsole();
  console.on("jsdomError", error => errors.push(error));
  const dom = new JSDOM(html, {
    url: "http://localhost/quiz/synthetic", runScripts: "dangerously",
    pretendToBeVisual: true, virtualConsole: console,
    beforeParse(win) {
      dispose = win.close.bind(win);
      win.scrollTo = () => {};
      win.HTMLElement.prototype.scrollIntoView = () => {};
      if (saved !== undefined) {
        win.localStorage.setItem("itembank.draft.synthetic.q1", JSON.stringify([saved]));
      }
    },
  });
  t.after(() => {
    dispose();
    assert.deepEqual(errors.map(error => error.message), []);
  });
  await flush();
  return dom;
}
const choice = (type = "mc", extra = {}) => ({
  id: "q1", type, stem: "Choose the synthetic response.", objective: "synthetic",
  options, response_schema: { select: type === "multi" ? 2 : 1 }, ...extra,
});
const viewFor = (item, position = 0) => ({
  session_id: "synthetic-session", item, position, total: 2,
});
const hold = { action: "hold", score: false, explain: {} };
const complete = {
  action: "complete", score: true, explain: {},
  next: { status: "complete", summary: { auto_attempts: 2, auto_correct: 1, pending_manual: 0 } },
};

async function boot(t, item, replies = [], { initial, next, teach, random = 0,
  draft = undefined } = {}) {
  const requests = [];
  const errors = [];
  let submitIndex = 0;
  let dispose;
  const console = new VirtualConsole();
  console.on("jsdomError", error => errors.push(error));
  const dom = new JSDOM(pages[item?.type === "check" ? "check" : "mc"], {
    url: "http://localhost/quiz/synthetic", runScripts: "dangerously",
    pretendToBeVisual: true, virtualConsole: console,
    beforeParse(win) {
      // The client has a top-level close() for answer feedback.
      dispose = win.close.bind(win);
      win.scrollTo = () => {};
      win.HTMLElement.prototype.scrollIntoView = () => {};
      win.Math.random = () => random;
      if (draft !== undefined) {
        win.localStorage.setItem(`itembank.draft.synthetic.${item.id}`, JSON.stringify([draft]));
      }
      const zero = { x: 0, y: 0, top: 0, left: 0, right: 0, bottom: 0, width: 0, height: 0 };
      win.Range.prototype.getBoundingClientRect = () => zero;
      win.Range.prototype.getClientRects = () => [];
      win.fetch = async (url, init) => {
        const request = { url, payload: JSON.parse(init.body) };
        requests.push(request);
        let data;
        if (url === "/api/start") data = initial || viewFor(item);
        else if (url === "/api/submit") {
          assert.ok(submitIndex < replies.length, "unexpected duplicate answer submission");
          data = replies[submitIndex++];
        } else if (url === "/api/next") data = next || viewFor(item);
        else if (url === "/api/teach") data = teach || { teaching: { available: false } };
        else throw new Error(`Unexpected network route: ${url}`);
        if (data instanceof Error) throw data;
        if (typeof data === "function") data = await data(request);
        return { ok: true, json: async () => structuredClone(data) };
      };
    },
  });
  t.after(() => {
    dispose();
    assert.deepEqual(errors.map(error => error.message), [], "generated page must run without script errors");
  });
  await flush();
  const document = dom.window.document;
  const button = (label = "Submit answer") => Array.from(document.querySelectorAll("button"))
    .find(node => node.textContent.trim() === label);
  const input = key => document.querySelector(`input[name="answer"][value="${key}"]`);
  const submit = async () => {
    const control = button();
    assert.ok(control, "the actual Submit answer control must remain reachable");
    assert.equal(control.disabled, false, "a complete response enables Submit answer");
    control.click();
    await flush();
  };
  return { dom, document, requests, button, input, submit,
    answers: () => requests.filter(request => request.url === "/api/submit").map(request => request.payload.answer) };
}

test("empty MC starts disabled and cannot send an empty answer", async t => {
  const page = await boot(t, choice());
  assert.equal(page.button().disabled, true);
  page.button().click();
  await flush();
  assert.deepEqual(page.answers(), []);
  assert.doesNotMatch(page.document.querySelector(".feedback").textContent, /not correct/i);
});

for (const type of ["mc", "multi"]) {
  test(`${type} wrong answer retains an editable, functioning retry control`, async t => {
    const page = await boot(t, choice(type), [hold, complete]);
    page.input("A").click();
    if (type === "multi") page.input("B").click();
    const originalOrder = Array.from(page.document.querySelectorAll(".choice input"), input => input.value);
    await page.submit();
    assert.match(page.document.querySelector(".feedback").textContent, /not correct/i);
    assert.equal(page.document.querySelectorAll(".choice.right, .choice.wrong").length, 0,
      "a held envelope without option disclosure must not paint option verdicts");
    assert.ok(page.button(), "wrong practice answers must restore Submit answer");
    assert.equal(page.input("C").disabled, false);
    if (type === "multi") page.input("A").click();
    page.input("C").click();
    await page.submit();
    assert.deepEqual(page.answers(), type === "multi" ? [["A", "B"], ["B", "C"]] : ["A", "C"]);
    assert.deepEqual(Array.from(page.document.querySelectorAll(".choice input"), input => input.value), originalOrder);
    assert.ok(page.button("View summary"));
  });
}

test("multi over-limit choice preserves valid picks and announces how to change them", async t => {
  const page = await boot(t, choice("multi"));
  page.input("A").click();
  page.input("B").click();
  page.input("C").click();
  assert.equal(page.input("A").checked, true);
  assert.equal(page.input("B").checked, true);
  assert.equal(page.input("C").checked, false);
  const notices = Array.from(page.document.querySelectorAll('[role="status"], [aria-live="polite"]'))
    .map(node => node.textContent).join(" ");
  assert.match(notices, /(?:already|limit|deselect|uncheck|remove|change)/i);
  assert.equal(page.button().disabled, false);
  assert.deepEqual(page.answers(), []);
});

test("hold without a runtime score never labels the response incorrect", async t => {
  const page = await boot(t, choice(), [{ action: "hold", accepted: false, score: null, explain: {} }]);
  page.input("A").click();
  await page.submit();
  assert.doesNotMatch(page.document.querySelector(".feedback").textContent, /not correct|incorrect/i);
  assert.equal(page.document.querySelectorAll(".choice.right, .choice.wrong").length, 0);
  assert.ok(page.button());
  assert.equal(page.input("B").disabled, false);
});

test("deferred feedback leaves option verdicts undisclosed", async t => {
  const page = await boot(t, choice(), [{ action: "defer_feedback", score: null, explain: {} }]);
  page.input("A").click();
  await page.submit();
  assert.equal(page.document.querySelectorAll(".choice.right, .choice.wrong").length, 0);
  assert.doesNotMatch(page.document.querySelector(".feedback").textContent, /not correct|incorrect/i);
  assert.ok(page.button("Check again"));
});

test("multi held feedback preserves runtime own-selection disclosure without inventing unpicked verdicts", async t => {
  const picks = {
    kind: "own_selections",
    right: [{ key: "A", text: "Alpha" }],
    wrong: [{ key: "B", text: "Beta" }],
    display: "Of the options you picked, these are right: A. These are not: B. Nothing is said here about the options you did not pick.",
  };
  const page = await boot(t, choice("multi"), [{ ...hold, selection_feedback: picks }]);
  page.input("A").click();
  page.input("B").click();
  await page.submit();
  const feedback = page.document.querySelector("[data-selection-feedback]");
  assert.ok(feedback, "runtime own-selection feedback must survive verify and settle");
  assert.match(feedback.textContent, /Alpha/);
  assert.match(feedback.textContent, /Beta/);
  assert.doesNotMatch(feedback.textContent, /Gamma|Delta/);
  for (const key of ["C", "D"]) {
    const label = page.input(key).closest("label");
    assert.equal(label.classList.contains("right"), false);
    assert.equal(label.classList.contains("wrong"), false);
  }
});

test("letter-referential options preserve their original displayed referents", async t => {
  const page = await boot(t, choice("mc", { options: [
    ...options.slice(0, 3), { key: "D", text: "Both A and B" },
  ] }));
  assert.deepEqual(Array.from(page.document.querySelectorAll(".choice"), label => [
    label.querySelector(".k").textContent, label.querySelector("input").value,
  ]), [["A", "A"], ["B", "B"], ["C", "C"], ["D", "D"]]);
});

test("structured argument presentation preserves decimal premises", async t => {
  const page = await boot(t, choice("mc", {
    stem: 'Consider the argument: "A solution has pH 7.4. Therefore, it is neutral."',
  }));
  await new Promise(resolve => setTimeout(resolve, 30));
  const lines = Array.from(page.document.querySelectorAll(".quiz-argument-text"), node => node.textContent);
  assert.deepEqual(lines, ["A solution has pH 7.4.", "Therefore, it is neutral."]);
});

test("ambiguous abbreviation keeps the authored argument text unstructured", async t => {
  const stem = 'Consider the argument: "Dr. Smith measured the sample. Therefore, it is safe."';
  const page = await boot(t, choice("mc", { stem }));
  assert.equal(page.document.querySelector(".quiz-argument"), null);
  assert.equal(page.document.querySelector("h1.stem").textContent, stem);
});

test("released aggregate correctness does not invent option verdicts", async t => {
  const page = await boot(t, choice(), [{ ...complete, explain: {} }]);
  page.input("A").click();
  await page.submit();
  assert.match(page.document.querySelector(".feedback").textContent, /Correct/);
  assert.equal(page.document.querySelectorAll(".choice.right, .choice.wrong").length, 0);
});

test("released table and build correctness do not invent row or step verdicts", async t => {
  const table = await boot(t, {
    id: "q1", type: "table", stem: "Classify each value.", objective: "synthetic",
    rows: [{ id: "one", text: "One" }, { id: "two", text: "Two" }],
    categories: ["Odd", "Even"],
  }, [{ ...complete, explain: {} }]);
  for (const row of table.document.querySelectorAll(".seg")) row.querySelector("button").click();
  await table.submit();
  assert.match(table.document.querySelector(".feedback").textContent, /Correct/);
  assert.equal(table.document.querySelectorAll(".right, .wrong").length, 0);

  const build = await boot(t, {
    id: "q1", type: "build", stem: "Order the steps.", objective: "synthetic",
    steps: ["First", "Then", "Finally"],
  }, [{ ...complete, explain: {} }]);
  for (const option of build.document.querySelectorAll(".opts .opt")) option.click();
  await build.submit();
  assert.match(build.document.querySelector(".feedback").textContent, /Correct/);
  assert.equal(build.document.querySelectorAll(".right, .wrong").length, 0);
});

for (const type of ["mc", "multi"]) {
  test(`${type} lost acknowledgement freezes controls and checks the saved cursor before edits`, async t => {
    const page = await boot(t, choice(type), [new Error("lost acknowledgement"), complete]);
    page.input("A").click();
    if (type === "multi") page.input("B").click();
    await page.submit();
    for (const input of page.document.querySelectorAll(".choice input")) assert.equal(input.disabled, true);
    page.input("C").click();
    assert.equal(page.input("C").checked, false);
    const recovery = page.button("Check saved state");
    assert.ok(recovery, "uncertain acknowledgement requires a cursor read, not blind answer replay");
    recovery.click();
    await flush();
    assert.equal(page.requests.filter(request => request.url === "/api/next").length, 1);
    assert.equal(page.answers().length, 1);
    assert.equal(page.input("C").disabled, false);
    if (type === "multi") page.input("A").click();
    page.input("C").click();
    await page.submit();
    assert.deepEqual(page.answers(), type === "multi" ? [["A", "B"], ["B", "C"]] : ["A", "C"]);
  });
}

test("accepted answer with lost acknowledgement never submits the old answer to the next item", async t => {
  const nextItem = choice("mc", { id: "q2", stem: "Second synthetic question." });
  const page = await boot(t, choice(), [new Error("reply lost after acceptance")], {
    next: viewFor(nextItem, 1),
  });
  page.input("A").click();
  await page.submit();
  const recovery = page.button("Check saved state");
  assert.ok(recovery);
  recovery.click();
  await flush();
  assert.deepEqual(page.answers(), ["A"]);
  assert.equal(page.document.querySelector("h1.stem").textContent, "Choose the synthetic response.");
  const advance = Array.from(page.document.querySelectorAll("button"))
    .find(button => /^(Continue|Next question)/.test(button.textContent));
  assert.ok(advance, "recovered next question waits for explicit advance");
  advance.click();
  await flush();
  assert.equal(page.document.querySelector("h1.stem").textContent, nextItem.stem);
  assert.deepEqual(page.answers(), ["A"]);
});

test("a hint request failure leaves the acknowledged wrong answer and retry intact", async t => {
  const page = await boot(t, choice(), [hold], { teach: new Error("hints temporarily unavailable") });
  page.input("A").click();
  await page.submit();
  assert.match(page.document.querySelector(".feedback").textContent, /not correct/i);
  assert.ok(page.button());
  assert.equal(page.input("B").disabled, false);
  assert.equal(page.button("Check saved state"), undefined);
  assert.deepEqual(page.answers(), ["A"]);
});

test("lost final acknowledgement opens runtime summary only after explicit continuation", async t => {
  const page = await boot(t, choice(), [new Error("final acknowledgement lost")], {
    next: complete.next,
  });
  page.input("A").click();
  await page.submit();
  const recovery = page.button("Check saved state");
  assert.ok(recovery);
  recovery.click();
  await flush();
  assert.ok(page.document.querySelector("h1.stem"));
  assert.ok(page.button("View summary"));
  assert.deepEqual(page.answers(), ["A"]);
  page.button("View summary").click();
  await flush();
  assert.match(page.document.querySelector(".done").textContent, /1\/2/);
  assert.deepEqual(page.answers(), ["A"]);
});

const checkItem = {
  id: "q1", type: "check", stem: "Run this synthetic program.", starter: "print('hello')",
  interaction_contract: { renderer_config: { language: "python", hidden_case_count: 1 } },
};

test("saved code replaces the starter template and is submitted unchanged", async t => {
  const page = await boot(t, checkItem, [complete], { draft: "print('saved draft')" });
  await page.submit();
  assert.deepEqual(page.answers(), ["print('saved draft')"]);
});

test("a deliberately empty saved code draft stays empty over the starter", async t => {
  const page = await boot(t, checkItem, [], { draft: "" });
  assert.equal(page.button().disabled, true);
  page.button().click();
  await flush();
  assert.deepEqual(page.answers(), []);
});

test("a fresh code item still starts from its authored template", async t => {
  const page = await boot(t, checkItem, [complete]);
  await page.submit();
  assert.deepEqual(page.answers(), ["print('hello')"]);
});

test("native reload restores saved code over a nonempty starter", async t => {
  const dom = await bootBaselineDraft(t, {
    saved: "print('saved draft')", value: "print('starter')",
  });
  assert.equal(dom.window.document.querySelector("textarea").value, "print('saved draft')");
});

test("native reload restores the latest fill edit over an earlier invalid echo", async t => {
  const dom = await bootBaselineDraft(t, {
    saved: "5/2", value: "two", control: "input",
  });
  assert.equal(dom.window.document.querySelector('input[type="text"]').value, "5/2");
});

test("native reload preserves a deliberately empty saved draft", async t => {
  const dom = await bootBaselineDraft(t, { saved: "", value: "print('starter')" });
  assert.equal(dom.window.document.querySelector("textarea").value, "");
});

test("acknowledged native submission clears its saved draft", async t => {
  const dom = await bootBaselineDraft(t, {
    saved: "print('submitted')", value: "", feedbackPause: true,
  });
  assert.equal(dom.window.localStorage.getItem("itembank.draft.synthetic.q1"), null);
});

test("code refusal metadata reaches the actual code-check controls", async t => {
  const page = await boot(t, checkItem, [{ refused: true, refused_reason: "language" }]);
  assert.ok(page.document.querySelector(".cm-editor"), "use the actual vendored editor");
  await page.submit();
  const refusal = page.document.querySelector(".refused.err");
  assert.ok(refusal, "verify must retain refusal and refusal reason");
  assert.match(refusal.textContent, /python.*language/i);
  assert.equal(page.button("View summary"), undefined);
});

test("code-check case observations survive the submit response projection", async t => {
  const page = await boot(t, checkItem, [{ ...complete,
    interaction_result: { observations: [{
      case_index: 1, passed: true, reason: "passed", input: "synthetic input",
      expected_kind: "output", expected: "hello", actual: "hello",
    }] },
  }]);
  await page.submit();
  const matrix = page.document.querySelector(".check-matrix");
  assert.ok(matrix);
  assert.equal(matrix.querySelectorAll(".case").length, 1);
  assert.match(matrix.textContent, /Case 1.*Passed/s);
  assert.match(matrix.textContent, /synthetic input/);
  assert.deepEqual(page.answers(), ["print('hello')"]);
});

for (const summary of [
  { auto_attempts: 3, auto_correct: 1, pending_manual: 0 },
  { auto_attempts: 0, auto_correct: 0, pending_manual: 1 },
  { auto_attempts: 0, auto_correct: 0, pending_manual: 0 },
]) {
  test(`resumed summary is truthful with no local miss history: ${JSON.stringify(summary)}`, async t => {
    const page = await boot(t, null, [], {
      initial: { session_id: "synthetic-session", status: "complete", summary },
    });
    const result = page.document.querySelector(".done");
    assert.ok(result);
    assert.doesNotMatch(result.textContent, /clean sweep|nothing to harvest/i);
    assert.match(result.textContent, new RegExp(`${summary.auto_correct}/${summary.auto_attempts}`));
  });
}
