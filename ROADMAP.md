# itembank roadmap

## North star

`itembank` is a local-first assessment protocol and runtime for human and AI
tutors. An agent must be able to request a test, receive items without answer
leakage, submit responses, obtain deterministic evidence, explain the result,
and choose a useful next test. Browser HTML, terminal use, Anki export, and any
future MCP or function-calling adapter are surfaces over the same runtime.

The durable boundary is:

```text
private bank markdown -> parser -> item model -> assessment runtime
                                      |             |
                                      |             +-> JSON agent interface
                                      +-> HTML quiz, study, Anki TSV
```

The tool repository contains code and synthetic fixtures only. Real banks and
learner evidence remain in private storage.

## Completed

- Machine-readable format contract and actionable lint errors.
- Six item types, including manually graded constructed response.
- Offline HTML quiz and loopback server with incremental attempt writes.
- Deterministic JSON sessions with `start`, `next`, `submit`, and `report`.
- Answer-key withholding and deterministic scoring for structured responses.
- Local session evidence grouped by objective.
- Dependency-free flashcard and Learn surface through `study`.
- Generic Basic and Cloze Anki TSV export through `export`.
- Synthetic fixture tests for server, agent, study, and export paths.
- Repository guard against real question-bank content.

## Next improvements, in order

### 1. Stabilize the protocol

- Add explicit schema versions for items, sessions, responses, and reports.
- Add stable author-provided item IDs, not only `Qn` positions.
- Emit machine-readable lint errors with error codes and fields.
- Define resume and idempotency behavior for repeated `submit` calls.
- Add a public JSON schema or equivalent contract fixture.

### 2. Improve assessment selection

- Add selection modes for diagnostic, practice, remediation, and exam.
- Track recent exposure and avoid accidental repeats.
- Select by objective, prerequisite, item type, and difficulty.
- Add discrimination-pair support for common confusions.
- Keep the first selector rule-based and inspectable.

### 3. Improve evidence without becoming a hosted analytics product

- Preserve response time and learner confidence when available.
- Track objective history, error category, and manual-review state.
- Separate raw evidence from derived mastery estimates.
- Add import and export for private learner state.
- Make all evidence updates auditable and reversible.

### 4. Add agent adapters

- Keep the JSON CLI as the canonical contract.
- Add a thin function-calling adapter only after the JSON behavior is stable.
- Add MCP only as transport, never as a second parser or scorer.
- Provide an agent usage contract covering permissions, answer leakage, retries,
  manual grading, and what the agent may or may not infer.

### 5. Strengthen content quality

- Validate objective coverage and prerequisite references.
- Detect near-duplicate stems and answer explanations.
- Add source and provenance fields with confidence states.
- Add ambiguity, unsupported-superlative, and answer-leakage warnings.
- Add fixture banks for every linter rule and every response type.

### 6. Keep the boundaries honest

- Do not add question generation to the runtime.
- Do not auto-grade prose into mastery without a review state.
- Do not add a hosted account or gradebook before local use proves the need.
- Do not fold Mandarin-specific TTS and third-party Anki packaging into this
  generic bank tool. That remains a separate private content pipeline.

## Acceptance for the agentic goal

A fresh agent with no repository context can:

1. Ask the tool for its contract.
2. Start a session targeting an objective.
3. Present the returned item to a learner without leaking the key.
4. Submit a structured or prose response.
5. Resume after interruption without duplicating an attempt.
6. Receive evidence that distinguishes correct, incorrect, and pending review.
7. Choose a remediation test using the evidence.

The tool is successful when the agent can perform that loop reliably without
scraping HTML, reimplementing scoring, or pretending uncertain grading is fact.
