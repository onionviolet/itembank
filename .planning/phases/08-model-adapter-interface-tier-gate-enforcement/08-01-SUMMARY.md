---
phase: 08-model-adapter-interface-tier-gate-enforcement
plan: 01
subsystem: model-adapter
tags: [tier-gate, fact-manifest, drop-whole, learner-payload, adversarial-corpus, no-leak]

requires:
  - phase: 06-hint-ladder-cursor-hold-feedback-modes
    provides: six-tier authored ladder (HINT_TIERS), authored_hint(q, tier, canonical) seam, v2 sessions
provides:
  - tier_gate.py: build_fact_manifest / evaluate_candidate / render_hint / render_proposal / learner_payload + GATE_REASON_CODES + TIER_FACTS + fixed tutoring-move templates
  - schemas/tier_gate.schema.json: closed hint_plan and rubric_proposal candidate shapes (additionalProperties false, no free-prose channel)
  - fixtures/model_gate_cases.json: deterministic 30-case Wave-0 adversarial corpus across five classes
  - tests/model_gate_roundtrip.py: corpus runner, pass/drop/unavailable assertions, payload-boundary scan
affects: [08-02 model adapter interface, 08-03 evidence events, 08-04 gate wiring, UI/release plans]

actuals:
  tokens: 20814
  tasks: 3
  commits: 5

tech-stack:
  added: []
  patterns:
    - Five-step gate algorithm (RESEARCH Pattern 1): manifest -> schema -> span -> fact -> move, fail closed at each layer
    - Conservative ambiguity rule: a fact whose resolved text overlaps a normalized protected fragment is ambiguous and may never be referenced
    - Single learner-payload constructor; drop/unavailable carry status + null generated, never a reason
    - Deterministic replay: the same candidate twice returns the same outcome and reason

key-files:
  created:
    - tier_gate.py
    - schemas/tier_gate.schema.json
    - fixtures/model_gate_cases.json
    - tests/model_gate_roundtrip.py
  modified: []

key-decisions:
  - "The manifest maps the Phase 6 six-tier ladder: tier 0 lesson pointer, 1 objective, 2 trap, 3 da for the picked option only, 4 disc/second, 5 why/notes; correct and model are protected at every tier."
  - "The gate is code executed after generation, never a prompt instruction (D-05/D-06); a leaking candidate is dropped whole, never rewritten into a sanitized version."
  - "learner_payload is the only constructor surfaces may call; drop/unavailable never reveal why (D-08)."
  - "The empty-points rubric proposal is valid and renders pending/unknown, never a default pass (D-13/D-14)."
  - "Protected-fragment overlap detection uses casefold + whitespace collapse normalization with a MIN_FRAGMENT_LEN floor so the conservative rule stays useful."

patterns-established:
  - "Fact ids are stable internal ids resolved only against the runtime-built manifest; provider labels are never trusted (Pitfall 1)."
  - "The schema validator cannot express maxItems/maxLength, so the bounded-plan ceiling (max 2 fact_ids, maxLength 240 rationale) is gate policy enforced after schema validation."
  - "The adversarial corpus is checked-in, sorted-by-id, deterministic, and replayed twice per case to prove reason-code stability."

requirements-completed: [TEACH-04, TEACH-05, TEACH-06, MODEL-03]

coverage:
  - id: D1
    description: "tier_gate.py exports the manifest gate, the four-layer evaluate_candidate, fixed-template render_hint/render_proposal, learner_payload, GATE_REASON_CODES, TIER_FACTS, and the tutoring-move templates; a legal bounded hint plan passes and renders only a fixed runtime template with the learner's exact span and exactly one allowed fact."
    requirement: TEACH-05
    verification:
      - kind: integration
        ref: "tests/model_gate_roundtrip.py#test_legal_hint_passes_and_renders_fixed_template"
        status: pass
      - kind: integration
        ref: "tests/model_gate_roundtrip.py#test_manifest_exposes_allowed_and_protected_facts"
        status: pass
    human_judgment: false
  - id: D2
    description: "A protected-fact reference, an extra free-prose field, an unmatched or ambiguous span, an unknown move, and oversized fact sets all drop whole with a stable GATE_REASON_CODES reason and never render."
    requirement: TEACH-04
    verification:
      - kind: integration
        ref: "tests/model_gate_roundtrip.py#test_protected_fact_drops_whole"
        status: pass
      - kind: integration
        ref: "tests/model_gate_roundtrip.py#test_extra_field_drops_schema_invalid"
        status: pass
    human_judgment: false
  - id: D3
    description: "schemas/tier_gate.schema.json is a closed candidate contract: kind-discriminated oneOf, additionalProperties false everywhere, no learner-facing free-prose property, and it validates with only schema_validate.SUPPORTED keywords."
    requirement: TEACH-05
    verification:
      - kind: unit
        ref: "tests/model_gate_roundtrip.py#test_schema_uses_supported_keywords_only"
        status: pass
    human_judgment: false
  - id: D4
    description: "fixtures/model_gate_cases.json is a deterministic 30-case Wave-0 adversarial corpus: >=10 disclosure, >=8 entailment, >=4 malformed, >=4 allowed, >=4 rubric, sorted by id; every disclosure/entailment row expects drop with a named reason; identical replays return the same outcome and reason."
    requirement: MODEL-03
    verification:
      - kind: integration
        ref: "tests/model_gate_roundtrip.py#test_corpus_counts"
        status: pass
      - kind: integration
        ref: "tests/model_gate_roundtrip.py#test_corpus_runner"
        status: pass
    human_judgment: false
  - id: D5
    description: "The learner-payload boundary is a single constructor: pass -> status + generated; drop and unavailable -> status + null generated, with no reason code, tier number, fact text, provider bytes, or detector detail anywhere in any corpus payload."
    requirement: TEACH-06
    verification:
      - kind: integration
        ref: "tests/model_gate_roundtrip.py#test_learner_payload_shape"
        status: pass
      - kind: integration
        ref: "tests/model_gate_roundtrip.py#test_payload_boundary_scan"
        status: pass
    human_judgment: false
  - id: D6
    description: "The authored-fallback seam (Phase 6 runtime.authored_hint) returns the tier's authored content when present and never falls back to a lower tier when the tier is unavailable, keeping the ladder usable on drop/unavailable (MODEL-03 degrade-never-block)."
    requirement: MODEL-03
    verification:
      - kind: integration
        ref: "tests/model_gate_roundtrip.py#test_authored_hint_seam"
        status: pass
      - kind: integration
        ref: "tests/scoring_roundtrip.py"
        status: pass
    human_judgment: false

duration: ~35min
completed: 2026-08-11
status: complete
---

# Phase 08 — Plan 08-01: Deterministic tier gate, closed candidate contract, authored fallback, and a 30-case Wave-0 adversarial corpus

**A production tier gate between provider output and the learner: a closed hint-plan candidate contract with a manifest gate, drop-whole policy, single learner-payload constructor, and a checked-in 30-case adversarial corpus proving no leak reaches a learner before any provider connects.**

## Performance

- **Duration:** ~35 min (continuation close-out of prior executor's Tasks 1-2)
- **Started:** 2026-08-10 (Task 1-2 by prior executor)
- **Completed:** 2026-08-11
- **Tasks:** 3/3
- **Files modified:** 4 created (tier_gate.py, schemas/tier_gate.schema.json, fixtures/model_gate_cases.json, tests/model_gate_roundtrip.py)

## Accomplishments
- Five-step gate algorithm shipping in `tier_gate.py`: manifest build, strict schema validation, span resolution, fact resolution, move validation — every leakage class drops whole with a stable reason code.
- Closed candidate contract in `schemas/tier_gate.schema.json` (kind-discriminated, `additionalProperties: false`, no free-prose channel), validated with only the in-repo validator's SUPPORTED keywords.
- Deterministic 30-case adversarial corpus (`fixtures/model_gate_cases.json`) — 10 disclosure, 8 entailment, 4 malformed, 4 allowed, 4 rubric — replayed twice per case to prove reason-code stability.
- Single `learner_payload` constructor; drop/unavailable payloads carry no reason, tier, fact, provider, or detector detail; a flatten()-style boundary scan proves it over every corpus payload.
- Authored-fallback seam verified: `runtime.authored_hint` keeps the Phase 6 ladder usable at the already-unlocked tier when the gate declines — MODEL-03's degrade-never-block property.

## Task Commits

Each task was committed atomically (TDD: test -> feat where applicable):

1. **Task 1: Tracer — one legal candidate passes the manifest gate and renders; one leak drops whole** — `92d0a4c` (test) + `a4ad406` (feat)
2. **Task 2: The 30-plus-case adversarial corpus and the deterministic policy layer** — `82bdba7` (test) + `44c89ac` (feat corpus)
3. **Task 3: Lock the learner-payload boundary and the authored-fallback seam** — `782d873` (test)

**Plan metadata:** `docs(08-01)` — final commit message "docs(08-01): complete deterministic tier gate plan"

## Files Created/Modified
- `tier_gate.py` - The five-step tier gate: fact manifest, candidate evaluation, fixed-template rendering, single learner-payload constructor
- `schemas/tier_gate.schema.json` - Closed hint_plan and rubric_proposal candidate shapes
- `fixtures/model_gate_cases.json` - 30 labeled candidate fixtures across the five Wave-0 classes
- `tests/model_gate_roundtrip.py` - Wave-0 release gate: corpus runner, pass/drop/unavailable assertions, payload-boundary scan
- `runtime.py` - reused (not modified); Phase 6 `authored_hint(q, tier, canonical)` is the declared seam

## Decisions Made
- The manifest maps the Phase 6 six-tier ladder; `correct` and `model` are protected at every tier (D-07/D-09).
- The gate never rewrites a leaking hint into a sanitized version; uncertain output is dropped whole (D-06).
- `learner_payload` is the only constructor surfaces may call; a drop never reveals why (D-08).
- An empty-points rubric proposal is valid and renders pending/unknown, never a default pass.
- Protected-fragment overlap detection normalizes with casefold + whitespace collapse and a MIN_FRAGMENT_LEN floor.

## Deviations from Plan

### Auto-fixed Issues

**1. Plan contract mismatch — `authored_hint` signature is the pre-existing Phase 6 seam `(q, tier, canonical)`, not `(q, tier)`**
- **Found during:** Task 3 (lock the learner-payload boundary and the authored-fallback seam)
- **Issue:** The plan's Task 3 signature says `authored_hint(q, tier)`; the pre-existing Phase 6 function takes `(q, tier, canonical)` and returns `{"index", "name", "available", "content", "label"}` with `available: false` for a missing tier (not Python `None`).
- **Fix:** Reused the Phase 6 function as the declared seam — no duplicate implementation. The Task 3 acceptance (tier content when present, never a lower-tier fallback, scoring_roundtrip unchanged) is satisfied and asserted against the real signature in `test_authored_hint_seam`. The `canonical` parameter is how tier-3 resolves the da for the learner's picked option.
- **Files modified:** tests/model_gate_roundtrip.py (test only; runtime.py untouched)
- **Verification:** `python tests/model_gate_roundtrip.py` and `python tests/scoring_roundtrip.py` both pass
- **Committed in:** `782d873` (part of the Task 3 test commit)

**2. Verification command substitution — `python schema_validate.py --all` does not exist in this CLI**
- **Found during:** plan verification list
- **Issue:** `schema_validate.py` takes a schema path and has no `--all` mode; the plan's verification line cannot run as written.
- **Fix:** The plan's intent — "the new tier-gate schema validates and uses only SUPPORTED keywords" — is covered by `test_schema_uses_supported_keywords_only()` (`schema_validate.check_schema` over the tier-gate schema), plus `python itembank.py schema --all` and `tests/protocol_roundtrip.py` for the full published-schema set.
- **Files modified:** none (test assertions already in the roundtrip suite)
- **Verification:** `python tests/model_gate_roundtrip.py`, `python itembank.py schema --all`, `python tests/protocol_roundtrip.py` all pass
- **Committed in:** n/a (covered by the Task 1-3 commits)

**3. Stale git worktree removal — `.phase10-wt` unblocked the scorer scan**
- **Found during:** verification (`python tests/scoring_roundtrip.py`)
- **Issue:** The stale, gitignored `.phase10-wt` worktree (branch `phase10`, HEAD == main, uncommitted WIP) shipped a second `runtime.py` with `score_response`, breaking the structural "exactly one scorer" gate the plan verifies against.
- **Fix:** Reapplied the prior user-approved decision ("Move it out of the repo, preserve WIP"): refreshed the `Downloads\CTF\phase10-wt-backup` copy (retention.py differed), then `git worktree remove --force` + `git worktree prune`, keeping branch `phase10` and all WIP.
- **Files modified:** none (worktree moved out of the repo; branch and backup preserved)
- **Verification:** `python tests/scoring_roundtrip.py` -> "scoring contract: ok (6 items, one scorer)"
- **Committed in:** n/a (environment fix, not a commit)

---

**Total deviations:** 3 auto-fixed (1 contract mismatch, 1 verification-command substitution, 1 environment fix)
**Impact on plan:** All necessary for correctness and to meet the plan's verification list. No scope creep; `runtime.py` remained untouched as the plan's seam declaration intended.

## Issues Encountered
- The `.phase10-wt` git worktree silently broke the required scoring verification; resolved by moving it out per the prior user-approved decision and preserving its WIP in `phase10-wt-backup`.
- Task 3 tests were absent from the committed roundtrip suite (the `forbidden_phrases()` helper and `_PAYLOADS` list existed but were never invoked by `main()`); added the three Task 3 tests plus the disclosure/entailment drop-reason assertion and verified the boundary scan catches a deliberately leaked option text.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- `tier_gate.py` and the closed schema are ready for the 08-02 adapter interface plan to call into.
- The authored-fallback seam is declared and testable; the call site lands in plan 08-04.
- The 30-case corpus is a checked-in, deterministic release gate the UI and release plans depend on.
- Evidence event shapes for gate outcomes are declared in the threat register; plan 08-03 implements the builders.

---
*Phase: 08-model-adapter-interface-tier-gate-enforcement*
*Completed: 2026-08-11*

---

# Self-Check

- [x] Task 1: legal hint plan passes and renders a fixed template; protected-fact reference and extra free-prose field drop whole with stable reasons; schema uses only SUPPORTED keywords
- [x] Task 2: corpus has 30 cases (10/8/4/4/4 across the five classes); every disclosure/entailment row drops with a named reason; replays are deterministic; no row renders a forbidden phrase; empty-points rubric proposal renders pending/unknown, never a default pass
- [x] Task 3: learner_payload is the single constructor with the exact pass/drop/unavailable shapes; payload-boundary scan over all corpus payloads proves no fixture key, option label, or model answer leaks; authored_hint returns tier content or unavailable per tier, never a lower-tier fallback; scoring_roundtrip passes unchanged
- [x] Verification list green: `python tests/model_gate_roundtrip.py`, `python tests/scoring_roundtrip.py`, schema check (SUPPORTED-keyword gate + `itembank schema --all`)
- [x] SUMMARY.md written, STATE.md updated, roadmap progress updated, final docs commit created

**Self-Check: PASSED**
