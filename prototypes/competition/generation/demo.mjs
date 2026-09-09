#!/usr/bin/env node
/**
 * Generator-only OpenMAIC package trial.
 *
 * This script prepares one unaccepted lesson-outline candidate. It does not
 * create files, start agents, score a response, or accept an Itembank artifact.
 */

import {
  generateSceneContent,
  generateSceneOutlinesFromRequirements,
} from "@openmaic/generation";

export const SYNTHETIC_SOURCE = `Water changes state when heat energy changes.
Heating ice can melt it into liquid water. Continued heating can turn liquid
water into water vapor. Cooling reverses those changes.`;

const REQUIREMENT = "Draft one concise teaching outline about changes of state for a beginner.";
const LOCAL_URL = "http://127.0.0.1:11434/api/generate";
const LOCAL_MODEL = "qwen3.5:4b";
const LOCAL_TIMEOUT_MS = 30_000;
const LOCAL_MAX_TOKENS = 700;

export const SINGLE_SCENE_OUTLINE = {
  id: "synthetic-water-states-1",
  type: "slide",
  title: "Heat changes water's state",
  description: "Teach the source-grounded sequence: ice melts when heated, then liquid water can evaporate into vapor.",
  keyPoints: [
    "Heating ice can melt it into liquid water.",
    "Continued heating can turn liquid water into water vapor.",
    "Cooling reverses those changes.",
  ],
  order: 1,
};

function localCall(systemPrompt, userPrompt) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), LOCAL_TIMEOUT_MS);
  return fetch(LOCAL_URL, {
    method: "POST",
    headers: { "content-type": "application/json" },
    signal: controller.signal,
    body: JSON.stringify({
      model: LOCAL_MODEL,
      system: systemPrompt,
      prompt: userPrompt,
      stream: false,
      options: { num_predict: LOCAL_MAX_TOKENS },
    }),
  })
    .then(async (response) => {
      if (!response.ok) throw new Error(`Local model returned HTTP ${response.status}`);
      const body = await response.json();
      if (typeof body.response !== "string") throw new Error("Local model returned no text response");
      return body.response;
    })
    .finally(() => clearTimeout(timer));
}

export async function draftOutline(aiCall) {
  const result = await generateSceneOutlinesFromRequirements(
    { requirement: REQUIREMENT },
    SYNTHETIC_SOURCE,
    undefined,
    aiCall,
  );
  return {
    status: result.success ? "candidate" : "invalid_model_output",
    candidate: result.success ? result.data : null,
    error: result.success ? null : result.error || "OpenMAIC outline generation failed",
  };
}

export async function draftTeachingCandidate(aiCall) {
  try {
    const content = await generateSceneContent(SINGLE_SCENE_OUTLINE, aiCall, {
      languageDirective: "Teach in clear English for a beginner.",
    });
    return {
      status: content ? "candidate" : "invalid_model_output",
      candidate: content || null,
      error: content ? null : "OpenMAIC scene content was missing or malformed",
    };
  } catch (error) {
    return {
      status: "invalid_model_output",
      candidate: null,
      error: error instanceof Error ? error.message : String(error),
    };
  }
}

if (import.meta.url === new URL(process.argv[1], "file:").href) {
  if (!process.argv.slice(2).includes("--local")) {
    console.error("Usage: npm run demo -- --local");
    console.error("This optional mode sends only the built-in synthetic source to loopback Ollama.");
    process.exitCode = 2;
  } else {
    const draft = await draftTeachingCandidate(localCall);
    process.stdout.write(`DRAFT\n${JSON.stringify(draft, null, 2)}\n`);
    if (draft.status !== "candidate") process.exitCode = 1;
  }
}
