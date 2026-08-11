---
phase: 05-check-item-type-code-editor
verified: 2026-08-11
status: human_needed
score: "5/5 automated must-haves verified; 2 human-gated items recorded PENDING, never claimed verified"
behavior_unverified: 2
overrides_applied: 0
human_verification:
  - test: "On the target Windows 11 machine, run the six steps of plan 05-04 Task 1 (platform, new_job_object, kill test, tasklist, 50-iteration escape measurement, forced fallback) and paste the six results."
    expected: "Job Object kill-on-close works; the escape rate over 50 iterations is a measured number; the fallback kills the tree too."
    why_human: "The 05-04 spike requires sys.platform == 'win32'; this session's shell is WSL2 and cannot spawn any Windows process (verified three ways), so the measurement is recorded PENDING, not faked."
  - test: "Serve fixtures/check_bank.md and work through the five items of plan 05-07 Task 3 (gutter alignment at 500 lines, Tab/Shift-Tab/undo feel, ten-case readout + pending verdict, the limits reading pass, keyboard-only parity)."
    expected: "Gutter row N sits on editor line N at 500 lines and a long line scrolls; Tab/Shift-Tab/undo behave; ten+ case rows stay navigable; no sentence implies a safety promise; keyboard-only submission matches /api/submit semantics."
    why_human: "Plan 05-07 Task 3 is a blocking human checkpoint; this headless session cannot keep a daemon alive for a real browser (background jobs denied, browser backend cannot reach a dying server). Partial automated evidence exists (node --test tests/js/ executes the keyboard/gutter behaviours)."
---

# Phase 5: Check Item Type & Code Editor — Verification Report

**Phase Goal:** A learner can write and run their own code against a `check` item, in a real
editor, and get a dichotomous verdict through the same scorer as every other item type.
**Verified:** 2026-08-11
**Status:** human_needed (two human-gated items recorded PENDING with full evidence; nothing
human is claimed verified)

## User Flow Coverage

User story: "As a learner, I want to write and run my own code against a `check` item in a
real editor and get a dichotomous verdict through the same scorer as every other item type."

| Step | Expected | Evidence | Status |
|------|----------|----------|--------|
| Author a check item | `CASE)`/`[LANG:]`/`[MATCH:]`/`[HARNESS:]`/`[TOLERANCE:]` parse; lint is clean; the format contract documents the type | `model.py` parse/lint/fingerprint; `itembank spec` check section; `tests/check_roundtrip.py#check_parse_and_defaults` PASS | ✓ automated |
| Run the learner's code | One interpreter per case, stdin closed at EOF, bounded by timeout and output cap, tree killed on both platforms | `runner.py` `run_cases`/`_spawn_and_drain`; `tests/check_kill_roundtrip.py` PASS (POSIX); Windows job-object path recorded PENDING in 05-SPIKE-RESULT.md | ✓ automated (Windows half → human PENDING) |
| Score dichotomously | The pass vector goes through the one scorer; a killed-at-timeout run scores None, never False | `runtime.score_response` check branch; `tests/check_roundtrip.py#check_scoring_identities` PASS | ✓ automated |
| Edit code in a real editor | Vendored CodeMirror 6: 1-based gutter, Tab inserts a tab, Shift-Tab dedents, read-only after submit, no wrap | `assets/vendor/codemirror/` bundle + boot script; `node --test tests/js/` 7/7 PASS (Tab/Shift-Tab/Enter/read-only/gutter/no-wrap executed) | ✓ automated (500-line pixel pass → human PENDING) |
| See what happened | Per-case matrix: Case N, status from stable reason, input/expected/actual, bound stops in the warning role; null verdict renders pending | `close()` check branch; `tests/check_roundtrip.py#check_matrix_contract` PASS | ✓ automated (appearance → human PENDING) |
| Be refused honestly | Three distinct sentences for offline/network/language; offline skip records nothing | `asCheck` !SERVE branch + daemon refusal JSON; `tests/check_roundtrip.py#check_refusal_states` PASS | ✓ automated |
| Read the evidence | Attempt file shows the submitted source; study/export show a description | `runtime.response_text`/`answer_text` + `evidence.render_attempt_md`; `check_render_attempt` PASS | ✓ automated |

## Goal Achievement

### Observable Truths (automated)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | The `check` item type parses, lints, fingerprints and documents: CASE) pairs, [LANG:], [MATCH:] (exact/trimmed/regex), [HARNESS:] + [TOLERANCE:], with the honest-limits sentence in the SPEC | ✓ VERIFIED | `model.py` MARKERS/parse; `itembank spec`; `tests/check_roundtrip.py#check_parse_and_defaults`, `check_markers_shared`, `check_harness_end_to_end` PASS |
| 2 | The runner executes source once per case under the deadline and the output cap, fails a truncated case, and kills the tree; the Windows kill is bounded and measured | ✓ VERIFIED (POSIX); Windows half PENDING | `tests/check_kill_roundtrip.py` PASS on the POSIX path; `05-SPIKE-RESULT.md` records the blocker and 0 of 50 runs executed on Windows (PENDING) |
| 3 | Scoring is dichotomous through the one scorer; a killed-at-timeout run is None, never False, and stays pending/human-markable | ✓ VERIFIED | `runtime.score_response`; `tests/check_roundtrip.py#check_scoring_identities`, `check_timeout_not_a_verdict` PASS |
| 4 | The served `check` shape is published: versioned interaction envelope, declarative renderer config (no executable payload), raw-source response schema, normalized result with boolean-or-null verdict and stable observation reasons | ✓ VERIFIED | `schemas/item.schema.json` check_item + $defs; `tests/check_roundtrip.py#check_schema_consumer` + `tests/protocol_roundtrip.py#test_check_contract_pins` PASS |
| 5 | Both submit paths gate on the runner and refuse network-bound execution by default with distinct locked sentences | ✓ VERIFIED | `surfaces/session.py#run_check_source`; daemon `_refuse_check_execution` + refusal JSON; `tests/check_roundtrip.py#check_network_refusal`, `check_agent_path` PASS |
| 6 | The editor is a vendored CM6 with a working keyboard contract (Tab insert + focus, Shift-Tab dedent current line only, Enter newline, read-only after submit, 1-based gutter, no wrap), loaded from a local bundle with no CDN | ✓ VERIFIED (executed) | `node --test tests/js/` 7/7; `tests/check_roundtrip.py#check_vendor_integrity` PASS |
| 7 | The per-case readout renders from the shared normalized observations; a mixed pass/fail stays dichotomous; a null verdict renders pending; no case material reaches the page before answering | ✓ VERIFIED (payload/source) | `tests/check_roundtrip.py#check_matrix_contract` PASS |
| 8 | Three refusal causes have three distinct locked sentences; the offline page offers a skip that records and counts nothing; the honest-limits line survives all three | ✓ VERIFIED | `tests/check_roundtrip.py#check_refusal_states` PASS |
| 9 | The honest-limits statement is one constant with two readers (SPEC and page), and the claim-word gate runs with exact per-file counts over source + README + this phase's records | ✓ VERIFIED | `tests/check_roundtrip.py#check_honest_limits_gate` PASS; `python itembank.py guard .` PASS |
| 10 | A `check` submission is readable in the attempt file and described on study/export | ✓ VERIFIED | `runtime.answer_text`/`response_text` + `evidence.render_attempt_md`; `check_render_attempt` PASS |

**Score:** 10/10 automated truths verified. 2 human-gated items recorded PENDING and never
claimed verified (see Human Verification Required).

### Deferred Items

None deferred. The two PENDING items are not deferred gaps — they are the phase's own human
checkpoints, recorded with full evidence and a named resume action:
1. The Windows process-tree kill spike measurement (05-04 Task 1) — PENDING.
2. The end-of-phase manual pass over the five items only a human can see (05-07 Task 3) —
   PENDING.

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | ----------- | ------ | ------- |
| `runner.py` | Out-of-process execution, timeout + output cap, process-tree kill, POSIX + Windows | ✓ VERIFIED (POSIX; Windows PENDING) | `run_cases`, `run_one_case`, `_spawn_and_drain`, `kill_tree`, job-object helpers; kill test PASS on POSIX; 05-SPIKE-RESULT.md records the Windows blocker |
| `model.py` `HONEST_LIMITS_NOTE` + `check` SPEC section | One honest-limits constant, two readers | ✓ VERIFIED | `check_honest_limits_gate` identity assertion PASS |
| `runtime.py` | `check` branches in canonical/score/public_item/explain + answer_text/response_text | ✓ VERIFIED | `check_scoring_identities`, `check_render_attempt`, `check_explain_payload` PASS |
| `surfaces/session.py` | The one shared runner gate, settings-derived bounds, unknown-language refusal | ✓ VERIFIED | `run_check_source`; `check_agent_path`, `check_network_refusal` PASS |
| `surfaces/daemon.py` | Both submit gates, network refusal, language refusal as normal JSON | ✓ VERIFIED | `_refuse_check_execution`, `_refusal_from_exit`; `check_network_refusal` PASS |
| `surfaces/quiz.py` | `record_answer` returns (score, run_result); CM6 bundle/boot + honest-limits substitution | ✓ VERIFIED | `check_explain_threading`, `check_vendor_integrity` PASS |
| `surfaces/quiz_page.py` | asCheck, .codewrap mount, per-case matrix, three refusals, skip control | ✓ VERIFIED (rendering → human) | `check_matrix_contract`, `check_refusal_states`, `check_vendor_integrity` PASS |
| `assets/vendor/codemirror/` | Pinned CM6 bundle + boot script + VENDOR.md (§4a) | ✓ VERIFIED | SHA-256 recomputed and matched; no CDN URL; `check_vendor_integrity` PASS |
| `schemas/item.schema.json` | check_item + envelope/result/observation $defs; 'check' in the enum | ✓ VERIFIED | `check_schema_consumer`, `test_check_contract_pins` PASS |
| `README.md` | The check type documented; points to spec + HONEST_LIMITS_NOTE without copying | ✓ VERIFIED | `check_honest_limits_gate` README assertions PASS |
| `tests/js/check_editor.test.mjs` | The interactive contract executed (ruling 16) | ✓ VERIFIED | `node --test tests/js/` 7/7 PASS |

### Key Link Verification

| From | To | Via | Status |
| ---- | --- | --- | ------ |
| `runner.py` | `runtime.score_response` | the results vector is the only thing the scorer sees | ✓ WIRED (`check_scoring_identities`) |
| `runtime.score_response` | `surfaces/session.py` + `surfaces/quiz.py` | `run_check_source` is the one gate both surfaces call | ✓ WIRED (`check_cross_path`, `check_explain_threading`) |
| `surfaces/quiz_page.py` | `assets/vendor/codemirror/` | `__CM6_TAG__`/`__CM6_BOOT__` substituted from the local files; no CDN | ✓ WIRED (`check_vendor_integrity`) |
| `model.HONEST_LIMITS_NOTE` | SPEC + rendered page | one constant, two readers | ✓ WIRED (`check_honest_limits_gate`) |
| `surfaces/daemon.py` | both submit routes | refusal JSON with `refused_reason` | ✓ WIRED (`check_network_refusal`, `check_refusal_states`) |
| `schemas/item.schema.json` | `runtime.public_item` | served check item validates; a non-page consumer submits through /api/submit | ✓ WIRED (`check_schema_consumer`) |

### Behavioral Spot-Checks

| Behavior | Command | Result |
| -------- | ------- | ------ |
| One runner invocation per submission; per-case actual output reaches both surfaces | `python tests/check_roundtrip.py` (check_explain_threading) | PASS |
| Vendored bundle integrity; page embeds locally; sample_bank byte-identical | `python tests/check_roundtrip.py` (check_vendor_integrity) | PASS |
| Tab/Shift-Tab/Enter/read-only/gutter/no-wrap executed against the real bundle | `node --test tests/js/` | PASS (7/7) |
| Mixed pass/fail maps to distinct case/reason; null verdict pending | `python tests/check_roundtrip.py` (check_matrix_contract) | PASS |
| Three refusal states; offline skip records nothing; honest-limits survives | `python tests/check_roundtrip.py` (check_refusal_states) | PASS |
| Attempt file shows the submitted source | `python tests/check_roundtrip.py` (check_render_attempt) | PASS |
| Schema consumer + negative fixtures + live /api/submit | `python tests/check_roundtrip.py` (check_schema_consumer) | PASS |
| Claim-word gate + identity | `python tests/check_roundtrip.py` (check_honest_limits_gate) | PASS |
| No real question bank committed | `python itembank.py guard .` | PASS |
| Full suite | `python tests/*_roundtrip.py` + `node --test tests/js/` | PASS (except pre-existing packaging/presentation environmental exclusions documented in 05-02-SUMMARY) |

### Requirements Coverage

| Requirement | Description | Status | Evidence |
| ----------- | ----------- | ------ | -------- |
| CODE-01 | The `check` format contract: parse, lint, fingerprint, SPEC | ✓ SATISFIED | `check_parse_and_defaults`, `check_markers_shared` PASS |
| CODE-02 | One scorer, dichotomous verdict, renderer-independent contract, published schema | ✓ SATISFIED | `check_scoring_identities`, `check_schema_consumer` PASS |
| CODE-03 | A real editor with line-accurate citations and keyboard parity | ✓ SATISFIED | `node --test tests/js/` 7/7 (pixel pass → human) |
| CODE-04 | Execution bounded by timeout and output cap, tree cleaned up on both platforms | ✓ SATISFIED (POSIX); Windows PENDING | `tests/check_kill_roundtrip.py` PASS; 05-SPIKE-RESULT.md |
| CODE-05 | Honest limits: no safety claim the runtime lacks; one statement, two readers; claim-word gate | ✓ SATISFIED | `check_honest_limits_gate` PASS |

### Anti-Patterns Found

None in files modified by Phase 5. The one environmental finding is recorded, not hidden: the
05-04 spike could not execute on Windows from this session's shell (WSL2 cannot spawn PE
processes — verified with three binaries, direct and via subprocess), and the record says so
rather than fabricating a measurement.

### Human Verification Required

The automated evidence above is green. The following require a human (per 05-VALIDATION.md's
manual rows and the two blocking checkpoints). **Both are recorded PENDING; neither is
claimed verified.**

1. **The Windows process-tree kill spike (05-04 Task 1).** Run the six steps on a Windows
   terminal on this machine and paste the results (05-04-PLAN.md lists them). The shell here
   reports `linux` and cannot spawn Windows processes, so the escape rate, both kill paths'
   outcomes, and the enum constant are PENDING — never guessed.
2. **The end-of-phase pass (05-07 Task 3).** `python itembank.py serve fixtures/check_bank.md`
   and work through the five items: gutter alignment at 500 lines, Tab/Shift-Tab/undo feel,
   the ten-case readout + pending verdict for a never-terminating run, the limits reading
   pass, and keyboard-only parity. This session could not drive a real browser against a live
   server (background daemons denied; browser backend got ERR_CONNECTION_REFUSED), so the
   five observations are PENDING.

### Gaps Summary

No code gaps were found: all automated truths verify, all required artifacts exist, are
substantive, wired, and flow real data, and no blocker anti-patterns were found. The phase
status is `human_needed` because two items are the phase's own human checkpoints, recorded
PENDING with full evidence and named resume actions — exactly the honest-limits posture the
phase exists to practice.

---
_Verified: 2026-08-11_
_Verifier: the agent (gsd-verifier)_
