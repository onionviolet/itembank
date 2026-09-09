import assert from "node:assert/strict";
import test from "node:test";

import { SYNTHETIC_SOURCE, draftOutline, draftTeachingCandidate } from "./demo.mjs";

test("a deterministic caller-supplied model yields one unaccepted candidate", async () => {
  let received = null;
  const result = await draftOutline(async (system, user) => {
    received = { system, user };
    return JSON.stringify({
      languageDirective: "Teach in English.",
      courseTitle: "Changes of State",
      outlines: [{
        id: "fixture-1",
        type: "slide",
        title: "Heat changes state",
        description: "A draft explanation of melting and evaporation.",
        keyPoints: ["melting", "evaporation"],
        order: 1,
      }],
    });
  });

  assert.equal(result.status, "candidate");
  assert.equal(result.error, null);
  assert.equal(result.candidate.courseTitle, "Changes of State");
  assert.equal(result.candidate.outlines.length, 1);
  assert.match(received.user, new RegExp(SYNTHETIC_SOURCE.slice(0, 30)));
  assert.equal("score" in result.candidate, false);
});

test("malformed fixture output remains an invalid unaccepted result", async () => {
  const result = await draftOutline(async () => "not a JSON outline");
  assert.equal(result.status, "invalid_model_output");
  assert.equal(result.candidate, null);
  assert.equal(typeof result.error, "string");
});

test("a deterministic model yields one generated teaching-scene candidate", async () => {
  let received = null;
  const result = await draftTeachingCandidate(async (system, user) => {
    received = { system, user };
    return JSON.stringify({
      elements: [{
        type: "text",
        left: 80,
        top: 60,
        width: 840,
        height: 100,
        content: "Heating ice melts it into liquid water.",
      }],
      background: { type: "solid", color: "#ffffff" },
      remark: "Fixture teaching candidate.",
    });
  });

  assert.equal(result.status, "candidate");
  assert.equal(result.error, null);
  assert.equal(result.candidate.elements[0].content, "Heating ice melts it into liquid water.");
  assert.match(received.user, /Heat changes water's state/);
  assert.equal("score" in result.candidate, false);
});

test("malformed teaching-scene fixture has no candidate", async () => {
  const result = await draftTeachingCandidate(async () => JSON.stringify({ background: {} }));
  assert.equal(result.status, "invalid_model_output");
  assert.equal(result.candidate, null);
  assert.equal(typeof result.error, "string");
});
