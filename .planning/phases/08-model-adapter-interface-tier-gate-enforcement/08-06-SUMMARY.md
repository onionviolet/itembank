---
phase: 08-model-adapter-interface-tier-gate-enforcement
plan: 06
subsystem: release-gate
tags: [model-adapter, tier-gate, release-gate, cross-surface, offline-matrix, authority-regressions, payload-scan, contract-audit, uat-precondition]

# Dependency graph
requires:
  - phase: 08-model-adapter-interface-tier-gate-enforcement
    provides: tier-gate (08-01), model-adapter boundary (08-02), model_interaction/mark_proposal evidence events (08-03), typed do_hint/do_rubric_review surfaces (08-04), identifier-safe assist routes + AgentAssist surface (08-05), blocking human UAT PASS in 08-05-UAT-EVIDENCE.md
provides:
  - "tests/model_phase_roundtrip.py — one deterministic cross-surface suite: run_full_scenario (hosted + local fake backends through the shared adapter and tier gate, evidence recovery, pending rubric proposal with the human-only cmd_mark accept, adversarial key-disclosure drop with descriptor-only evidence, replay idempotency), run_offline_matrix (nine provider-failure rows in stable order), run_authority_regressions (scoring/evidence/protocol/hint/daemon/serve, runner when present), run_payload_scan (flatten() forbidden-phrase discipline over every learner-facing artifact), run_contract_audit (no auto-accept, suggestion_reveal, human-only guard, no fractional score, no invented figures, agent_usage/COVERAGE, D-18 record, ROADMAP criterion 1-14 mapping)"
  - "The Phase 8 release gate verdict: the adversarial corpus, the offline matrix, the single-authority invariants, and the recorded human UAT all agree — phase 08 may ship"
affects: [phase 08 closure, future MCP surface when V2-INT-02 lands, future learner-facing model surfaces]

# Actuals
actuals:
  tokens: 26000
  tasks: 3
  commits: 1

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "One deterministic cross-surface suite, no framework: every assertion is a plain function over the real CLI, the real adapter/gate/evidence/runtime modules, and fixture-backed fake providers (hosted CLI script + loopback OpenAI server); the gate is self-contained and runs as `python tests/model_phase_roundtrip.py`"
    - "Fixture-driven fakes: the passing hint candidate echoes the request's learner_response as its focus_span (the tests/model_ui_roundtrip.py precedent) and references tier0.lesson_ref on fixtures/lesson_bank.md — one genuine wrong answer unlocks tier 0, whose lesson facts are allowed and non-ambiguous, so the gate passes deterministically"
    - "Expected-output equality: the scenario's generated payload is asserted equal to tier_gate.render_hint(plan, manifest) computed in the test, so the surface path cannot diverge from the gate's own renderer"
    - "Flatten() forbidden-phrase discipline reused from evidence_roundtrip/model_ui: fixture-private phrases and authority vocabulary scanned over every learner-facing artifact, keys and values alike"

key-files:
  created:
    - tests/model_phase_roundtrip.py
    - .planning/phases/08-model-adapter-interface-tier-gate-enforcement/08-06-SUMMARY.md
  modified:
    - .planning/STATE.md
    - .planning/ROADMAP.md
    - .planning/HANDOFF-PHASE08.md (created)

key-decisions:
  - "The gate drives the real CLI and surfaces (start/submit/hint/rubric-review/mark/evidence/report/lesson) rather than calling runtime functions directly, so the path a learner or agent actually takes is the path under test"
  - "The passing-hint scenario runs on fixtures/lesson_bank.md (tier-0 lesson facts), not sample_bank.md: the runtime rebuilds each item's teaching record from live evidence before a transition, and only SHOWN tiers persist (the response event's hint_tier field), so on the sample bank the effective permitted tier stays 0 with no allowed fact and no candidate can pass. One wrong answer on the lesson bank unlocks tier 0, where tier0.lesson_ref is allowed and non-ambiguous"
  - "run_authority_regressions invokes exactly the plan's list (scoring/evidence/protocol/hint/daemon/serve, runner when present); the phase-local model_* plan tests are covered by the full suite and are named in the criterion mapping (criteria 6/7)"
  - "The payload scan scopes the private-key-NAME check to the assist artifacts: the session envelope and reports legitimately carry metadata keys such as notes in their retention trace, so disclosure is proven by the fixture-phrase scan across every artifact plus the name check on assist payloads"
  - "The 'mark' artifact is the human marker's own operator-facing output (its rubric points echo the marker's input), so the fixture-private phrase check is skipped for it while authority-string, private-key, and dropped-candidate checks still apply"
  - "The invented-figure scan targets NUMBER-prefixed performance units, so the D-19 prohibition prose itself ('no invented tok/s figure') is not a false positive"

patterns-established:
  - "Release-gate shape: one tracer scenario first (hosted/local parity, proposal, drop), then the offline matrix, then authority regressions, then the payload scan, then the contract audit — the plan's own task order, wired into main() after run_full_scenario"
  - "Stable-order matrix: the nine offline rows iterate a declared tuple and the gate asserts the executed order equals it, so the matrix is counted, never approximated"
  - "Criterion-to-assertion mapping: every ROADMAP Phase 8 criterion 1-14 maps to the specific green assertion that proves it, printed on completion"

requirements-completed: [TEACH-04, TEACH-05, TEACH-06, TEACH-07, TEACH-08, TEACH-09, MODEL-01, MODEL-02, MODEL-03, MODEL-04, MODEL-05]

# Coverage metadata
coverage:
  - id: G1
    description: "Cross-surface tracer (Task 1): a real mc wrong answer produces a hint whose learner payload equals tier_gate.render output with the exact learner span, from both a fake hosted CLI profile and a loopback OpenAI-compatible profile switched in via settings only (MODEL-02) — identical normalized payload shape and evidence field set; the model_interaction event is retrievable by session with the same interaction id; replaying the scenario is idempotent (same interaction id, already_recorded evidence statuses, D-12)"
    requirement: MODEL-01
    verification:
      - kind: unit
        ref: "tests/model_phase_roundtrip.py#_hosted_hint_pass"
        status: pass
      - kind: unit
        ref: "tests/model_phase_roundtrip.py#_local_parity"
        status: pass
    human_judgment: false
  - id: G2
    description: "Pending rubric proposal and human-only accept (Task 1): a short answer generates a pending mark_proposal linked to the response and interaction; cmd_mark --proposal with the human's N-boolean rubric settles it (marker human, proposal_ref, verdict, rubric N booleans); marks_by_event returns the settled mark and the response's review_state derives to marked — no model path ever settles a mark (D-13/D-14/D-23/D-24/D-25)"
    requirement: TEACH-09
    verification:
      - kind: unit
        ref: "tests/model_phase_roundtrip.py#_short_proposal_human_mark"
        status: pass
    human_judgment: false
  - id: G3
    description: "Adversarial drop (Task 1): a key-disclosure candidate (protected tier5.why fact) invoked through the same path drops whole — generic drop copy with no reason/tier/provider detail, the authored fallback stays usable, and the evidence event stores descriptors only (outcome, gate_reason, sha256 fingerprints, byte counts; never candidate text, D-08/D-16)"
    requirement: MODEL-05
    verification:
      - kind: unit
        ref: "tests/model_phase_roundtrip.py#_adversarial_drop"
        status: pass
    human_judgment: false
  - id: G4
    description: "Offline matrix (Task 2): all nine named provider-failure rows (disabled, missing hosted executable, nonzero exit, timeout, malformed JSON, oversized output, refused output, unreachable endpoint, HTTP failure) run the full core loop in stable order — submit/scoring, lessons, authored hints, evidence append/read, reports, and explicit human marking all pass; only generated assistance is unavailable (D-04/MODEL-03)"
    requirement: MODEL-03
    verification:
      - kind: unit
        ref: "tests/model_phase_roundtrip.py#run_offline_matrix"
        status: pass
    human_judgment: false
  - id: G5
    description: "Authority regressions (Task 2): scoring_roundtrip, evidence_roundtrip, protocol_roundtrip, hint_roundtrip, daemon_roundtrip, serve_roundtrip (runner_roundtrip when present) all pass unchanged — one scorer, one event writer, one protocol, Phase 6 hint authority, authoritative daemon API, untrusted served page (08-VALIDATION.md 'Existing authority regressions')"
    requirement: MODEL-02
    verification:
      - kind: unit
        ref: "tests/model_phase_roundtrip.py#run_authority_regressions"
        status: pass
    human_judgment: false
  - id: G6
    description: "Payload-boundary scan + corpus (Task 2): every learner-facing JSON document the scenario produced is clean of fixture-private phrases and authority vocabulary (tier indexes, gate reasons, profile/backend identifiers, secret references), the dropped candidate's text appears in no artifact, and the adversarial corpus count is asserted >= 30, never approximated"
    requirement: MODEL-04
    verification:
      - kind: unit
        ref: "tests/model_phase_roundtrip.py#run_payload_scan"
        status: pass
    human_judgment: false
  - id: G7
    description: "Contract and decision audit (Task 3): no auto-accept path exists structurally (settings-schema key walk + Phase 8 module source scan), suggestion_reveal ships all three locked values with default after-self-mark, mark_event still raises ValueError for any non-human marker, the new event builders carry no score/verdict field, no invented tok/s or latency figure appears in modules or Phase 8 docs (D-19), agent_usage.schema.json validates and COVERAGE.md's matrix parses, the hosted CLI is documented as the default backend when enabled (D-18), and every ROADMAP Phase 8 criterion 1-14 maps to a green assertion printed on completion"
    requirement: MODEL-04
    verification:
      - kind: unit
        ref: "tests/model_phase_roundtrip.py#run_contract_audit"
        status: pass
    human_judgment: false
  - id: G8
    description: "UAT precondition (plan must_have): 08-05-UAT-EVIDENCE.md exists with a PASS verdict and environment/checklist/privacy/accessibility/trusted-local-review evidence — asserted before the gate's release scenario runs"
    verification: []
    human_judgment: true
    rationale: "The blocking human checkpoint is a human decision by definition; the gate asserts the durable evidence file exists with the PASS marker, exactly as the plan's precondition requires."

# Metrics
duration: ~60min
completed: 2026-08-11
status: complete
---

# Phase 08 Plan 06: Cross-Surface Phase 8 Release Gate — Summary

**The release gate is green: one deterministic suite (`tests/model_phase_roundtrip.py`) proves the adversarial corpus, the offline matrix, the single-authority invariants, and the recorded human UAT all agree — the phase ships only when they cannot diverge.**

## Performance

- **Duration:** ~60 min
- **Completed:** 2026-08-11
- **Tasks:** 3
- **Files modified:** 1 code/test file (`tests/model_phase_roundtrip.py`, 1149 lines) plus this SUMMARY, STATE.md, ROADMAP.md, and the new HANDOFF-PHASE08.md

## Accomplishments

- **Task 1 — the tracer.** `run_full_scenario()` proves one real end-to-end scenario: with a fake hosted CLI profile, a wrong answer on the fixture lesson bank's mc item produces a hint whose learner payload equals `tier_gate.render_hint(plan, manifest)` computed in the test — status pass, fixed-template text, the exact learner span present — and the `model_interaction` event is retrievable by session with the same interaction id. With the local loopback OpenAI-compatible profile switched in via settings only, the identical scenario yields the same normalized payload shape and the same evidence field set (MODEL-02); credentials ride the Authorization header to the provider only, never the request body, evidence, or learner payloads (D-03/D-15). A short answer generates a pending `mark_proposal`; the human accepts via `cmd_mark --proposal` with an N-boolean rubric; `marks_by_event` returns the settled mark with `marker: human` and `proposal_ref`, and the response's `review_state` derives to `marked`. An adversarial key-disclosure candidate is dropped whole — generic drop copy, authored fallback usable, descriptor-only evidence (sha256 fingerprints, byte counts, never candidate text). Replaying the scenario is idempotent (D-12): a second hint reports `already_recorded` with the same interaction id and an identical re-submit dedupes to the same event id.
- **Task 2 — offline matrix, authority regressions, payload scan.** `run_offline_matrix()` runs all nine named provider-failure rows (disabled, missing hosted executable, nonzero exit, timeout, malformed JSON, oversized output, refused output, unreachable endpoint, HTTP failure) in a stable, asserted order; each row runs the full core loop through the CLI and surfaces — submit/scoring, the lesson surface, the authored hint fallback, evidence append/read, the report, and an explicit human mark all pass; only generated assistance changes. `run_authority_regressions()` invokes scoring/evidence/protocol/hint/daemon/serve (`runner_roundtrip` when present) and fails on any non-zero exit — one scorer, one event writer, one protocol, unchanged. `run_payload_scan()` applies the flatten() forbidden-phrase discipline over every learner-facing artifact the scenario produced (22 artifacts), with forbidden material derived from the fixture items, plus authority vocabulary, secret references, profile identifiers, and the dropped candidate's text. The corpus count is asserted `>= 30`, never approximated.
- **Task 3 — the contract and decision audit.** `run_contract_audit()` proves: no auto-accept path exists structurally (a settings-schema key walk plus a source scan over every Phase 8 module); `suggestion_reveal` ships all three locked enum values with the `after-self-mark` default; `mark_event` still raises `ValueError` for any non-human marker; the new `model_interaction_event`/`mark_proposal_event` builders carry no score/verdict field (no fractional score exists); no invented tok/s or latency figure appears in `model_adapter.py`, `tier_gate.py`, `evidence.py`, or the Phase 8 docs (D-19) — `elapsed_ms` is the only timing field; `schemas/agent_usage.schema.json` validates (supported keywords + the full documented instance) and COVERAGE.md's matrix parses to 2 INTEGRATE / 4 OPT-OUT rows; the hosted CLI is documented as the design-target default backend (D-18, TRANSPORT_REGISTRY order + 08-CONTEXT/COVERAGE); and every ROADMAP Phase 8 criterion 1-14 maps to the green assertion that proves it, printed on completion.

## Task Commits

| Task | Commit | Type |
|------|--------|------|
| Tasks 1-3 (one atomic commit per plan) | `04701eb` | test |

**Plan metadata:** `test(08-06): add the cross-surface Phase 8 release gate` — the single commit carries only `tests/model_phase_roundtrip.py`; the docs commit (this SUMMARY, STATE.md, ROADMAP.md, HANDOFF-PHASE08.md) follows as `docs(08-06): ...`.

## Files Created/Modified

- `tests/model_phase_roundtrip.py` - the cross-surface Phase 8 release gate (run_full_scenario, run_offline_matrix, run_authority_regressions, run_payload_scan, run_contract_audit, criterion mapping)
- `.planning/phases/08-model-adapter-interface-tier-gate-enforcement/08-06-SUMMARY.md` - this summary
- `.planning/STATE.md` - phase 08 plan 6 of 6 complete, phase 08 closed, progress counts advanced
- `.planning/ROADMAP.md` - Phase 8 checkbox, 6/6 plans line, 08-06 wave-5 checkbox
- `.planning/HANDOFF-PHASE08.md` - phase 08 closure handoff (created)

## Decisions Made

- The gate drives the real CLI and surfaces rather than calling runtime functions directly — the learner/agent path is the path under test.
- The passing-hint scenario runs on `fixtures/lesson_bank.md` (tier-0 lesson facts): the runtime rebuilds teaching records from live evidence where only SHOWN tiers persist (the response `hint_tier` field), so on `sample_bank.md` the effective tier stays 0 with no allowed fact. One wrong answer on the lesson bank unlocks tier 0, where `tier0.lesson_ref` is allowed and non-ambiguous — the same fixture strategy tests/model_ui_roundtrip.py already proves.
- `run_authority_regressions` invokes exactly the plan's module list; the phase-local `model_*` plan tests are covered by the full suite and named in the criterion mapping (criteria 6/7).
- The payload scan scopes the private-key-NAME check to the assist artifacts and skips the fixture-phrase check for the `mark` artifact (operator-facing echo of the human marker's own rubric), while every other check still applies — disclosure is proven by the fixture-phrase scan across all artifacts.

## Verification

- `python tests/model_phase_roundtrip.py` — **green** (`model phase roundtrip: ok`): full scenario, 9-row offline matrix in stable order, 6 authority regressions, 22-artifact payload scan, contract audit with the 1-14 criterion mapping.
- Full suite (every `tests/*.py`, CI-mirroring driver) — **42/43 green**. The one failure, `packaging_roundtrip.py`, is an environment precondition, not a regression: it requires the gitignored PyInstaller-frozen Windows sidecar (`dist/`) AND a working Windows-executable launcher, and this session's WSL interop is broken (even `python.exe` fails with `run-detectors: unable to find an interpreter`), so the frozen `.exe` cannot handshake from here. `dist/` is gitignored (absent from any fresh checkout), the artifact is untracked in the main tree, and `packaging_shell_roundtrip.py` (the build-script shape gate) passes. All six authority regressions and every other suite — including the phase-local `model_gate/model_adapter/model_evidence/model_surface/model_ui` — pass unchanged.
- `08-05-UAT-EVIDENCE.md` PASS precondition — asserted before the gate's scenario runs; the file is present on main with `status: pass`.
- `python schema_validate.py --all` — **not a CLI this repo ships** (same known deviation as 08-05): `schema_validate.py` is a two-argument validator. All-schemas validation is covered by the green suite (`protocol_roundtrip` check_schema's the seven published contracts; `model_gate`/`model_adapter`/`config`/`model_surface` validate tier_gate/model_adapter/settings/agent_usage; this gate's `run_contract_audit` additionally check_schema's + validates `agent_usage` and walks `settings`).

## Deviations

**1. [Scenario fixture] The passing-hint scenario uses `fixtures/lesson_bank.md`, not `sample_bank.md`**
- **Issue:** The plan's scenario implies any mc item. On `sample_bank.md`'s mc item (no lesson content) no candidate can pass: the runtime rebuilds each item's teaching record from live evidence before a transition and only SHOWN tiers persist, so the effective permitted tier stays 0 with no allowed fact (`fact_unknown` drop) and no authored fallback content.
- **Fix:** One genuine wrong answer on the lesson bank's mc item unlocks tier 0, whose `tier0.lesson_ref` fact is allowed and non-ambiguous — the exact fixture strategy `tests/model_ui_roundtrip.py`'s passing fake already proves. The fake candidates echo the request's `learner_response` as the focus_span, so the span always matches.
- **Verification:** the gate's hosted/local pass tests are green with the lesson bank, and the drop/matrix/proposal paths are unchanged.

**2. [Verification deviation] `python schema_validate.py --all` is not a CLI this repo ships**
- **Issue:** `schema_validate.py` is a two-argument (`schema instance`) validator; there is no `--all` mode.
- **Fix:** All-schemas validation is covered by the green suite (see Verification) plus this gate's own `run_contract_audit` validation of `agent_usage` and `settings`.
- **Verification:** `python tests/protocol_roundtrip.py` (green), `python tests/model_gate_roundtrip.py` (green), `python tests/model_adapter_roundtrip.py` (green), this gate's contract audit (green).

**3. [Environment condition, not fixed] `packaging_roundtrip.py` cannot run in this session**
- **Issue:** The test requires the gitignored PyInstaller-frozen Windows sidecar and a working Windows-executable launcher; this WSL session cannot launch any Windows executable (even `python.exe` fails with `run-detectors: unable to find an interpreter`), so the frozen `.exe` never handshakes.
- **Fix:** None possible in this environment. The artifact is untracked in the main tree (built artifact, gitignored), the failure reproduces identically on a fresh checkout, and nothing under the worktree or main tree was modified to chase it. 42/43 suites pass.
- **Verification:** `python tests/packaging_roundtrip.py` fails only at the frozen-handshake step; `python tests/packaging_shell_roundtrip.py` passes.

**4. [State files] `.planning/config.json` carries no per-plan or per-phase state**
- **Issue:** The instruction named `config.json` alongside `STATE.md`, but `config.json` (verified against its git history) holds workflow/ship/hooks settings and has never tracked plan completion.
- **Fix:** No truthful field exists to flip, so `config.json` was left byte-identical rather than inventing a field. Completion is recorded in `STATE.md` (plan 6 of 6, phase closed, progress counts) and `ROADMAP.md` (Phase 8 checkbox, 6/6 line, wave-5 checkbox) — the repo's actual plan tracker, matching the 08-05 closure commit's precedent.

**5. [Test hygiene] The pre-existing suite leaves a scratch file in cwd**
- **Issue:** `tests/model_adapter_roundtrip.py`'s `test_request_envelope_and_unknown_field` calls `hosted_profile("", name="unused")`, which writes `fake_hosted_unused.py` into the process cwd (the repo root when the suite runs from there). This is pre-existing test behaviour, not a change from this plan.
- **Fix:** The scratch file was deleted after the full-suite run; nothing was committed. No change to the pre-existing test (the plan's authority regressions must pass unchanged).

## Issues Encountered

- **WSL interop is broken in this session:** no Windows executable can be launched (`python.exe` fails with `run-detectors: unable to find an interpreter`), which is exactly why the frozen-sidecar handshake in `packaging_roundtrip.py` cannot run. All stdlib/Linux-side tests are unaffected.
- No code defects found in the Phase 8 surface; the gate and every other suite it can run are green.

## User Setup Required

None — no external service configuration required. The gate exercises hosted and local transports with fake CLI executables and a loopback server only; the shipped default remains the disabled backend.

## Next Phase Readiness

- **Phase 08 is complete:** 6/6 plans executed, the release gate green, and the blocking human UAT recorded PASS. `HANDOFF-PHASE08.md` documents what shipped and the open items carried forward (no auto-accept, descriptor-only drop audit, tier-3 stays a peer of the human marker, bench still owed and off the critical path).
- A provider-connected pass path needs only a configured backend profile; rendering, disclosure, and lock behaviour are already asserted over the rendered template.

---
*Phase: 08-model-adapter-interface-tier-gate-enforcement*
*Completed: 2026-08-11*

## Self-Check: PASSED

- Created files: `tests/model_phase_roundtrip.py` exists (1149 lines); `.planning/phases/08-model-adapter-interface-tier-gate-enforcement/08-06-SUMMARY.md` exists.
- Commits: `04701eb test(08-06): add the cross-surface Phase 8 release gate` verified on `gsd/phase-08-06`; the `docs(08-06): ...` metadata commit follows with SUMMARY.md, STATE.md, ROADMAP.md, HANDOFF-PHASE08.md.
- Verification: `python tests/model_phase_roundtrip.py` green; full suite 42/43 green (the sole failure is the environment-bound frozen-sidecar packaging test, unchanged from a fresh checkout); all six authority regressions green; `08-05-UAT-EVIDENCE.md` PASS precondition asserted.

## PLAN COMPLETE
