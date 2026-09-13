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
- Local session evidence grouped by objective, with `retract`, `render`, and
  `mark` as auditable compensating events.
- Dependency-free flashcard and Learn surface through `study`.
- Generic Basic and Cloze Anki TSV export, plus GIFT for LMS import.
- Synthetic fixture tests for server, agent, study, lesson, and export paths.
- Repository guard against real question-bank content.
- Daily cross-subject surface (`day`): dated-plan parsing, floor rule, streak log.
- Daemon consolidation: one process, one port, every surface (Phase 2).
- Packaging and self-update: one `.pyz` release plus per-OS launcher shims,
  SHA256SUMS, opt-in version check (Phase 2.1).
- Lesson format and in-app reader: `## LESSON` grammar, `[LESSON-SRC:]`
  external sources, `[LESSON-REF:]` links, the slug rule (Phase 3).
- Lesson rich blocks: `## TERMS` glossary behind a runtime gate, `[!KEY]`
  callouts with Anki round-trip, one-sentence `Objective:` lines, a
  five-style registry with `render-style` (Phase 3.1).
- Agent onboarding: `AGENTS.md` plus four repo skills (`absorb-book`,
  `curriculum-design`, `guiding-questions`, `author-bank`) in interoperable
  SKILL.md format, mirrored for Codex and Claude Code.

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

### 5. Teach the wrong answer (hint ladder and feedback modes)

- Add a deterministic hint ladder (lesson pointer → objective → trap →
  rationale for the picked option → discriminator → reveal), one tier per
  call, wrong answers holding the cursor.
- Make feedback a property of session mode: drill reveals immediately,
  practice runs the ladder, diagnostic and exam stay silent until the sitting
  ends or the attempt is marked.
- Record `hints_used` per response so `report` distinguishes "right at tier 1"
  from "right at tier 4".
- Gate content reveals in the runtime, never by model reluctance: the locked
  tier is visible runtime state.

### 6. Model adapter and tier-gate enforcement

- Let a tutoring model read the item, the key, the rationale, and the
  learner's actual wrong answer — and write about *that* error at the tier the
  runtime permits; an adversarially prompted reveal is dropped, never shown.
- Keep backend swap a config change: hosted CLI and local OpenAI-compatible
  servers share one code path, and everything degrades offline.
- Route `short` rubric marking through the adapter to a `pending` review
  state; auto-accepting a model suggestion must be impossible.

### 7. Strengthen content quality

- Validate objective coverage and prerequisite references.
- Detect near-duplicate stems and answer explanations.
- Add source and provenance fields with confidence states.
- Add ambiguity, unsupported-superlative, and answer-leakage warnings.
- Add fixture banks for every linter rule and every response type.

### 8. Keep the boundaries honest

- Do not add question generation to the runtime.
- Do not auto-grade prose into mastery without a review state.
- Do not add a hosted account or gradebook before local use proves the need.
- Do not fold Mandarin-specific TTS and third-party Anki packaging into this
  generic bank tool. That remains a separate private content pipeline.

### 9. Make Today the owner-backed work surface

- Replace the lane-first scan with a ranked **Now**, **Next** and **Later** task list while retaining the compact lane summary.
- Show course, due state, estimated time, purpose, completion gate and source on each task card.
- Add a vault course-ledger adapter that reads existing assignment rows without copying them into an Itembank task store.
- Make check and uncheck update the owning row through a fingerprint guard, atomic write and append-only operation record.
- Prove checked, unchecked, externally changed and owner-unavailable fixtures before registering another task provider.

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
