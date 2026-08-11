# Phase 8 Validation Strategy

## Purpose

Phase 8 is complete only when generated guidance is useful about the learner's latest genuine error and the runtime can prove that no reserved, higher-tier, or ambiguous fact reaches a learner payload. Provider success is optional; authored teaching, scoring, evidence, reports, and manual grading remain available when generation is disabled or unavailable.

## Wave 0: Tier-gate proof before provider integration

`tests/model_gate_roundtrip.py` and `fixtures/model_gate_cases.json` are created before any hosted CLI or local HTTP adapter is connected. The fixture corpus is checked in, deterministic, and contains at least 30 labeled candidates:

| Fixture class | Minimum | Required assertion |
|---|---:|---|
| Direct or encoded disclosure | 10 | Entire candidate is `drop`; no generated text is rendered or returned |
| Semantic entailment, elimination, or higher-tier leakage | 8 | Entire candidate is `drop`, including ambiguity cases |
| Malformed output, refusal, oversize, timeout/unavailable descriptors | 4 | Typed non-pass outcome; authored loop remains usable |
| Allowed, error-specific guidance | 4 | `pass`; renderer uses only permitted fact IDs and exact learner spans |
| Rubric-review proposals | 4 | Per-point suggestions remain pending and cannot create an accepted mark |

Each fixture declares the permitted manifest, reserved manifest, current tier, candidate, expected gate result, and expected rendered/fallback result. Tests must derive forbidden values from fixture-private item data rather than relying only on key names.

## Verification map

| Concern | Primary executable check | Contract proven |
|---|---|---|
| Permitted/reserved manifest and whole-candidate drop | `python tests/model_gate_roundtrip.py` | D-05 through D-09, D-11 |
| Hosted/local adapter parity and typed unavailability | `python tests/model_adapter_roundtrip.py` | D-01 through D-04, D-17 |
| Append-only interaction retrieval and safe drop descriptors | `python tests/model_evidence_roundtrip.py` | D-12, D-13, D-15, D-16 |
| Pending-only rubric proposals and human mark boundary | `python tests/model_evidence_roundtrip.py` | D-13, D-14, MODEL-05 |
| CLI and agent usage contract | `python tests/model_surface_roundtrip.py` | MODEL-03, MODEL-04 |
| Daemon payload allowlist and learner UI states | `python tests/model_ui_roundtrip.py` and `python tests/daemon_roundtrip.py` | TEACH-04 through TEACH-09 |
| Cross-surface parity, degradation, and single-authority invariants | `python tests/model_phase_roundtrip.py` | all Phase 8 requirements |

## Existing authority regressions

The Phase 8 gate must run alongside these existing tests:

- `python tests/scoring_roundtrip.py` — `runtime.score_response` remains the only scorer.
- `python tests/evidence_roundtrip.py` — `evidence.append_event` remains the only event writer and retraction/index behavior stays intact.
- `python tests/protocol_roundtrip.py` — published JSON documents remain schema-valid.
- `python tests/hint_roundtrip.py` — Phase 6 alone owns entitlement, authored tiers, cursor hold, and authored fallback.
- `python tests/daemon_roundtrip.py` and `python tests/serve_roundtrip.py` — the API remains authoritative and the served page remains an untrusted renderer.
- `python tests/runner_roundtrip.py` when present — Phase 5 keeps execution/capture authority; the adapter does not create a runner.

## Payload-boundary checks

The API/browser tests parse every learner-facing JSON document, HTML response, and rendered assist region. They assert that permitted-tier indexes, item keys, rationales, correct answers, reserved facts, source text, provider-native output, secret references, backend/profile identifiers, gate reasons, and dropped candidate text are absent. A policy drop returns only the public typed state and approved generic copy. The evidence test separately proves that safe operator metadata is retrievable without making private candidate content retrievable.

## Offline and provider-failure matrix

Run each core action with `model_backend` disabled, a missing hosted executable, non-zero exit, timeout, malformed JSON, oversized output, refused output, an unreachable local endpoint, and an HTTP failure. In every row, submit/scoring, lessons, authored hints, evidence append/read, reports, and explicit human marking still pass; only generated assistance is unavailable.

## End-of-phase UAT

After every automated check is green, serve a temporary lesson bank and verify at 1280px, 768px, 375px, and 320px/200% zoom:

1. `Help and evidence` is subordinate to the response controls and `Get optional guidance` is opt-in.
2. Requested/thinking/pass/drop/unavailable/retry states announce once without moving focus; reduced motion removes nonessential animation.
3. Passed support carries the generated-content disclosure and never resembles an authored tier or chat transcript.
4. A dropped or unreachable model shows the approved generic copy while the authored hint remains usable.
5. A short-response proposal shows each rubric point as `Pending rubric suggestion — human review required`; no model control records a mark.
6. `Record human mark` is the only acceptance path and its event identifies a human marker.
7. Keyboard-only, CSS-off, and screen-reader inspection reveal no private tier/fact/key/backend/profile/drop detail.

## Phase release gate

Phase 8 may be marked complete only after all six plan-local test commands, the existing authority regressions, the 30-case minimum corpus count, hosted/local parity, offline matrix, payload-boundary scan, and end-of-phase UAT pass. Any leak fixture that is not deterministically classified is a release blocker and must resolve to whole-candidate `drop`, never partial rendering or rewriting.
