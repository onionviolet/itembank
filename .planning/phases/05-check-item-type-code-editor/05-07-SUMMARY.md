---
phase: 05-check-item-type-code-editor
plan: 07
subsystem: docs-schema-gate
tags: [render, schema, readme, claim-word-gate, checkpoint]

requires:
  - phase: 05-check-item-type-code-editor (05-04)
    provides: 05-SPIKE-RESULT.md (the record the claim-word gate covers; PENDING measurement, blocker documented)
  - phase: 05-check-item-type-code-editor (05-06)
    provides: the per-case matrix, the three refusal states, the honest-limits line on every check item

provides:
  - check branches in runtime.answer_text() and runtime.response_text(), and the attempt file rendering the submitted source
  - check_item + interaction_contract/renderer_config/response_schema/interaction_result/case_observation $defs in schemas/item.schema.json, 'check' in the type enum
  - the README check-type section (bounds, match modes, harness, the CSCI 1100 note) pointing at `itembank spec` + HONEST_LIMITS_NOTE without copying the constant
  - the honest-limits identity assertion and the claim-word gate with exact per-file counts
  - the end-of-phase manual pass, recorded PENDING (human checkpoint)

affects: [phase closeout, 05-VALIDATION.md manual rows, ROADMAP Phase 5 closure]

actuals:
  tokens: 45000
  tasks: 3
  commits: 5

tech-stack:
  added: []
  patterns:
    - "The claim-word gate is a loop over an explicit file list with an expected count per file; the failure message names the file and the term"
    - "The schema's interaction_result verdict is boolean-or-null (null exactly for a killed-at-timeout run), matching response.schema.json's score: null"

key-files:
  created: []
  modified:
    - runtime.py
    - evidence.py
    - schemas/item.schema.json
    - README.md
    - tests/check_roundtrip.py
    - tests/protocol_roundtrip.py
    - .planning/phases/05-check-item-type-code-editor/05-02-SUMMARY.md
    - .planning/phases/05-check-item-type-code-editor/05-03-SUMMARY.md
    - .planning/phases/05-check-item-type-code-editor/05-04-SUMMARY.md

key-decisions:
  - "The attempt file renders check_source (the learner's code) rather than the results vector, because the evidence answer for a check item is the vector and a marker needs the code; response_text bounds the rendering at 40 lines with a pointer to the log."
  - "The README example avoids the `Q1.` marker so `itembank guard .` does not parse the documentation itself as a bank (guard walks every .md outside fixtures/); the CASE) lines still appear, satisfying the plan's CASE)-in-README gate."
  - "The claim-word gate's covered set is exactly the plan's: README.md and surfaces/quiz.py carry one pre-existing occurrence of the first term each (both about the browser's own file-page behaviour), and model/runner/quiz_page/session/daemon/GRADING plus this phase's SPIKE-RESULT and SUMMARY records carry zero of either term. The third term named by the UI-SPEC is dropped with the plan's stated reason (it matches ordinary English). Earlier summaries were reworded (the phrase meaning standalone -> 'when run alone') because the literal second-term substring trips the case-insensitive gate."
  - "Task 3 (the end-of-phase manual pass) is recorded PENDING: this session's shell cannot keep a daemon alive across tool calls (background jobs denied) and cannot drive a real browser, so the five items need a human at a served page. The jsdom runner already executes the keyboard/gutter behaviours against the real vendored bundle, which covers the automated half of item 5 and parts of items 1-2."

requirements-completed: [CODE-02, CODE-03, CODE-05]

coverage:
  - id: R1
    description: "answer_text/response_text return meaningful text for a check item; the attempt file shows the submitted source; every check public_item validates against the published schema; a renderer-independent consumer submits through /api/submit to the same scorer; invalid contracts/versions/responses are rejected"
    requirement: CODE-02
    verification:
      - kind: integration
        ref: "tests/check_roundtrip.py#check_schema_consumer (schema validation + negative fixtures + live /api/submit consumer)"
        status: pass
      - kind: integration
        ref: "tests/check_roundtrip.py#check_render_attempt (render branches + attempt file source fragment)"
        status: pass
      - kind: integration
        ref: "tests/protocol_roundtrip.py#test_check_contract_pins (check in type enum, $defs present, reason enum, boolean-or-null verdict, additionalProperties false)"
        status: pass
    human_judgment: false
  - id: R2
    description: "The honest-limits statement is provably one string in both required places, and the claim-word gate runs in the suite with exact per-file counts over source + README + this phase's records"
    requirement: CODE-05
    verification:
      - kind: integration
        ref: "tests/check_roundtrip.py#check_honest_limits_gate (identity + per-file counts; README points to spec/HONEST_LIMITS_NOTE without copying; the two terms' counts as the gate asserts)"
        status: pass
    human_judgment: false
  - id: R3
    description: "The five end-of-phase manual items: gutter alignment at 500 lines, Tab/Shift-Tab/undo feel, ten-case readout + pending verdict, the limits reading pass, keyboard-only parity"
    requirement: CODE-03
    verification:
      - kind: other
        ref: "05-07-SUMMARY.md Task 3 section — recorded PENDING (human checkpoint; headless session cannot keep a daemon alive for a real browser)"
        status: pending
    human_judgment: true
    rationale: "Plan's Task 3 is a blocking human checkpoint. This session cannot run a real browser against a live server (background daemon denied, browser backend cannot reach a dying server). Partial automated evidence exists: node --test tests/js/ executes Tab/Shift-Tab/Enter, read-only-after-submit, gutter growth, and no-wrap against the real vendored bundle; the 500-line pixel pass, ten-case scroll, and reading pass remain human."

duration: 150min
completed: 2026-08-11
status: complete-with-pending
---

# Phase 05: Check item type — Plan 07 Summary

**A check submission is now readable everywhere the other five types are (attempt file,
study/export surfaces), its served shape is published and validates (item.schema.json gains
the versioned interaction envelope, the declarative renderer config, the raw-source response
schema, and the normalized result with its stable observation reason enum), the README
documents the type and its bounds in the project's own voice, and CODE-05 stops being a
promise: the honest-limits statement is provably one constant read by SPEC and the rendered
page, and a claim-word gate runs in the suite with exact per-file counts over the source, the
README, and the records this phase wrote about itself. The end-of-phase manual pass is
recorded PENDING for a human at a served page.**

## Performance

- **Duration:** 150 min
- **Tasks:** 3 (2 automated + 1 human checkpoint)
- **Commits:** 5 (1 test + 1 feat + 1 docs-reword + 1 docs plan + 1 metadata)

## Task 1 — what a check submission looks like in an attempt file and in the schema

- `runtime.answer_text()` now describes a check item ("code check: N hidden test case(s)
  (lang)") for the study/export surfaces; `runtime.response_text()` returns the submitted
  source, bounded at 40 lines with a pointer to the evidence log's `check_source`.
- `evidence.render_attempt_md` gains a check branch: it renders `check_source` as the
  "Source, submitted" code block plus the results vector — a marker sees the code, not a
  vector of 1s and 0s.
- `schemas/item.schema.json`: `check` in the type enum; `check_item` (which deliberately
  carries no cases/expected/key and says so), `interaction_contract` (literal version 1,
  type check), `check_renderer_config` (language/starter_source/hidden_case_count,
  `additionalProperties: false` so a bank cannot smuggle executable payload), the
  `check_response_schema` (raw source string), `interaction_result` (verdict boolean-or-null
  — null exactly for a killed-at-timeout run, criterion 12), and `case_observation` (stable
  1-based case_index, passed, reason enum passed|wrong_output|timeout|output_cap, bounded
  actual, post-submit expected, expected_kind output|pattern, input).
- `tests/check_roundtrip.py#check_schema_consumer`: every check public_item validates;
  negative fixtures reject unknown version, extra/executable renderer fields, unknown
  renderer keys, non-string responses, and string verdicts; a real killed-at-timeout result
  validates with null verdict/score; a renderer-independent consumer (imports no
  quiz-page module) submits the declared raw source through `/api/submit` and gets the same
  normalized result semantics.
- `tests/protocol_roundtrip.py#test_check_contract_pins`: pins the new $defs/enums and the
  two new lint codes `item.no_normalizer` and `item.tolerance_unstated`.

## Task 2 — the README section and the claim-word gate

- README gains a `check` row in the item-types table and a full section: the CASE) marker
  syntax, the three match modes and default, the harness/tolerance mode, the two bounds and
  their settings keys, the default-closed network refusal, and the CSCI 1100 note (this type
  runs the learner's own code with no model in the path, so an AI-use ban is not engaged).
- It points readers to the `check` section of `itembank spec` and names
  `model.HONEST_LIMITS_NOTE` as the canonical limits text **without copying the sentence**
  (D-10: exactly two locations, both reading one constant). The example deliberately avoids
  a `Q1.` marker so `itembank guard .` does not parse the documentation itself as a bank.
- The gate: `tests/check_roundtrip.py#check_honest_limits_gate` asserts the identity
  (SPEC and the served page carry the same sentence) and then the claim-word gate — a loop
  over an explicit file list with expected per-file counts. The first term: exactly 1 in
  README.md and 1 in surfaces/quiz.py (both the pre-existing accurate browser-file-page
  occurrences), 0 elsewhere in the covered set; the second term: 0 everywhere covered; the
  third term named by the UI-SPEC is dropped with the plan's stated reason. The covered set
  is source + README + this phase's SPIKE-RESULT and SUMMARY records; the phase's input
  documents are outside it by design (they discuss the terms to forbid them). Earlier
  summaries were reworded so their prose (the standalone-phrase) no longer trips the literal
  case-insensitive gate.

## Task 3 — end-of-phase pass (PENDING, human checkpoint)

**PENDING — human verification required.** The plan's Task 3 needs a real browser against a
served page for five items:

1. Gutter alignment at 500 lines (paste 500 lines, confirm line 500 sits on line 500, no
   wrap on a long line).
2. Tab/Shift-Tab/undo feel (Tab inserts a tab and keeps focus; Shift-Tab dedents one line
   only; Ctrl-Z walks sensibly).
3. Ten-or-more-case readout stays navigable by ordinary scroll; a never-terminating run
   renders the pending treatment with the timed-out case row in the warning colour
   (criterion 12).
4. The reading pass: does any sentence in SPEC/README/page copy/refusals imply a safety
   promise?
5. Keyboard-only parity: focus source → Check → verdict → one case row via Enter/Space, and
   browser vs /api/submit semantics equivalent.

This session could not execute it: the shell denies background daemons and the browser
backend cannot reach a server that dies between tool calls (verified: serve starts, browser
gets ERR_CONNECTION_REFUSED once the launcher exits). Partial automated evidence exists and
is recorded: `node --test tests/js/` executes Tab insert + focus, Shift-Tab dedent, Enter
newline, read-only-after-submit with the source visible, 1-based gutter growth, and no-wrap
against the real vendored bundle. The five items are recorded in 05-VALIDATION.md as the
manual rows they always were; a human runs `python itembank.py serve fixtures/check_bank.md`
and works through the plan's five steps.

## Task Commits

1. `8716073` (test) — render branches, schema consumer + negative fixtures, honest-limits gate
2. `b90ce47` (feat) — runtime/evidence render branches, item.schema.json, README, gate
3. `b659741` (docs) — reword earlier summaries to clear the claim-word gate
4. (docs) — this SUMMARY

**Plan metadata:** 05-07-SUMMARY.md commit below.

## Files Created/Modified

- runtime.py — answer_text/response_text check branches
- evidence.py — attempt-file check branch rendering check_source
- schemas/item.schema.json — check_item + envelope/result/observation $defs, check in enum
- README.md — the check section + table row
- tests/check_roundtrip.py — check_schema_consumer, check_render_attempt, check_honest_limits_gate
- tests/protocol_roundtrip.py — test_check_contract_pins
- .planning/phases/05-check-item-type-code-editor/05-{02,03,04}-SUMMARY.md — reworded for the gate

## Deviations from Plan

- **README example avoids the `Q1.` marker** so `itembank guard .` (a plan-required gate)
  does not parse the documentation as a bank; the CASE) lines and all required copy remain.
- **Task 3 recorded PENDING** (see above): the plan's checkpoint is inherently human, and
  this headless session cannot drive a real browser against a live server.
- **Summary rewordings:** the gate's covered set includes the phase's SUMMARY records, and
  three earlier summaries contained the literal second-term substring (the standalone-phrase
  "in ..."); reworded to "when run alone" (4 lines changed) so the gate passes without an
  exception list.
## Issues Encountered

- `itembank guard .` flagged the new README as a question bank (the `Q1.` + `[TYPE: check]`
  + `CASE)` example parsed as one item); fixed by dropping the `Q1.` marker from the example.
- Validating the interaction_result $def required a synthetic root because
  schema_validate resolves `#/$defs/` refs against the passed root; documented in the test.

## User Setup Required

**Yes — one human action closes this plan's PENDING Task 3:** run
`python itembank.py serve fixtures/check_bank.md` on this machine and work through the five
items in 05-07-PLAN.md Task 3 (paste the five observations, then type "verified"). This
overlaps the 05-04 human checkpoint (both need a live Windows/browser session).

## Next Phase Readiness

- Phase closeout can proceed: all automated plans (05-01..05-03, 05-05..05-07 T1/T2) are
  green; the two human checkpoints (05-04 spike, 05-07 Task 3) are recorded PENDING with
  full evidence and a named resume action.

---
*Phase: 05-check-item-type-code-editor*
*Completed: 2026-08-11 (Task 3 PENDING human)*
