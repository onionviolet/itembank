---
phase: 09-subject-invariant-loop-emt-math-cs-integration
plan: 01
subsystem: subjects
tags: [subject-profile, session-v3, emt-tracer, semantic-table, fallback]

requires:
  - phase: 03-lesson-format-in-app-reader
    provides: model.parse_lesson, surfaces.lesson.render_markdown/lesson_page, fenced language-* classes, semantic tables
  - phase: 06-hint-ladder-cursor-hold-feedback-modes
    provides: runtime.teaching_transition, surfaces.session do_start/do_action/do_hint, SESSION_VERSION 2 upgrade seam
provides:
  - subjects.py: PROFILE_SCHEMA_VERSION, DEFAULT_PROFILE, SubjectProfileError, validate_registry, subject_ids, select_profile, session_profile
  - Version-3 session subject_profile snapshot with v2-to-v3 upgrade (nullable slot, filled once on first action)
  - EMT tracer: lesson -> wrong -> authored hint -> retry -> evidence under one persisted profile
  - Shared semantic table wrapper (.lesson-table-scroll, scope=col, labelled focusable region)
affects: [09-02 settings registry, 09-04 math, 09-05 clients + runnable code, Phase 10 scheduling]

actuals:
  tokens: 0
  tasks: 2
  commits: 1

tech-stack:
  added: [subjects.py, tests/subject_loop_roundtrip.py]
  patterns:
    - Surface-free profile data policy; surfaces select, never dispatch
    - Session-owned snapshot consumed on resume (D-04); live registry edits cannot change a sitting
    - One extractor (evidence.subject_of) for namespaced objectives

key-files:
  created:
    - subjects.py
    - tests/subject_loop_roundtrip.py
  modified:
    - runtime.py
    - schemas/session.schema.json
    - surfaces/session.py
    - surfaces/lesson.py
    - build.py
    - tests/lesson_roundtrip.py
    - fixtures/lesson_golden_phase3_content.txt

key-decisions:
  - "The subject profile resolves from the items actually selected into the sitting, not the whole bank: an objective-filtered session over a mixed-namespace bank is not ambiguous, while an unfiltered mixed sitting still refuses (D-04). select_profile itself stays bank-generic and refuses any mixed input without an explicit id."
  - "Shipped subjects remain a temporary REGISTRY constant in subjects.py at this plan; plan 09-02 moves EMT/Math/CS into the validated subject_profiles settings group and keeps only the conservative default code-owned (D-03)."
  - "The D-13 resolution ships in the shared reader: native <table><thead><th scope=col><tbody><td> inside a labelled, keyboard-focusable .lesson-table-scroll region that owns horizontal overflow, with overflow-wrap:anywhere cells. The Phase 3.1 content golden and the byte-identical block-branch golden were regenerated to the new wrapper; the diff is only the wrapper line."
  - "The session adapter fills a legacy v2 session's null subject_profile slot once, from the session's own item list, on the first action (D-04); session_view exposes subject_id + profile metadata only from the stored snapshot."

patterns-established:
  - "subjects.select_profile(qs, registry, explicit_id=None, requested_capabilities=()) returns a JSON-native snapshot; every negative path raises SubjectProfileError naming subject/profile/capability, never a path."
  - "runtime SESSION_VERSION advances by exactly one per phase; the v2->v3 upgrade adds a nullable slot only and never inspects a bank or settings."
  - "The lesson reader emits one semantic table wrapper for every bank; there is no EMT-specific renderer branch."

requirements-completed: [LOOP-01, LOOP-04]

coverage:
  - id: D1
    description: "An EMT bank with one unambiguous namespaced objective enters the existing practice lesson -> wrong response -> authored hint -> retry -> evidence loop under a persisted EMT profile (D-01, D-04, D-12, D-14)."
    requirement: LOOP-01
    verification:
      - kind: integration
        ref: "tests/subject_loop_roundtrip.py#test_emt_learner_loop_with_persisted_profile"
        status: pass
    human_judgment: false
  - id: D2
    description: "A resumed session consumes its stored profile snapshot rather than reinterpreting the bank or current settings (D-04); the stored snapshot is byte-for-byte unchanged after a registry edit."
    requirement: LOOP-01
    verification:
      - kind: integration
        ref: "tests/subject_loop_roundtrip.py#test_emt_learner_loop_with_persisted_profile (resume-drift step)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Unknown/unnamespaced input returns the conservative plain-markdown/runtime profile and names every requested unavailable capability; mixed namespaces refuse without an explicit id; disallowed item types refuse before a session exists (D-03, D-04)."
    requirement: LOOP-01
    verification:
      - kind: integration
        ref: "tests/subject_loop_roundtrip.py#test_conservative_fallback_and_capability_report, test_mixed_subject_refusal_and_explicit_resolution, test_disallowed_item_type_refuses_before_write"
        status: pass
    human_judgment: false
  - id: D4
    description: "EMT prose, lists and semantic tables remain in source order and retain table/header/cell semantics at a narrow viewport via the shared labelled focusable overflow wrapper (D-12, D-13)."
    requirement: LOOP-04
    verification:
      - kind: integration
        ref: "tests/subject_loop_roundtrip.py#test_emt_lesson_semantic_table; fixtures/lesson_golden_phase3_content.txt regenerated (diff = wrapper line only)"
        status: pass
    human_judgment: false
  - id: D5
    description: "Version-3 session schema publishes the nullable subject_profile snapshot; v2 sessions upgrade with a null slot that validates, and the first action fills and persists it once."
    requirement: LOOP-01
    verification:
      - kind: integration
        ref: "tests/subject_loop_roundtrip.py#test_legacy_session_fills_snapshot_once; schemas/session.schema.json x-itembank-version 3"
        status: pass
    human_judgment: false
  - id: D6
    description: "No production surface contains a subject-name dispatch table or subclass; an AST guard over surfaces/ rejects if/match branches keyed by the shipped subject ids (D-02)."
    requirement: LOOP-01
    verification:
      - kind: unit
        ref: "tests/subject_loop_roundtrip.py#test_no_subject_dispatch_in_surfaces"
        status: pass
    human_judgment: false

verification-runs:
  - command: "python tests/subject_loop_roundtrip.py"
    exit: 0
  - command: "python tests/scoring_roundtrip.py"
    exit: 0
  - command: "python tests/lesson_roundtrip.py"
    exit: 0
  - command: "python tests/hint_roundtrip.py"
    exit: 0
  - command: "python tests/protocol_roundtrip.py"
    exit: 0
  - command: "python tests/agent_roundtrip.py"
    exit: 0
  - command: "python tests/evidence_roundtrip.py"
    exit: 0
  - command: "python tests/selection_roundtrip.py"
    exit: 0
  - command: "python tests/serve_roundtrip.py"
    exit: 0
  - command: "python tests/config_roundtrip.py"
    exit: 0
  - command: "python tests/daemon_roundtrip.py"
    exit: 0
    notes: "Intermittently fails under concurrent load from other active phase worktrees (hostile-bank /tmp snapshot sees foreign mkdtemp dirs); passes standalone. Unrelated to this diff: the hostile stem 404s on the daemon stem allowlist before do_start."
  - command: "python tests/presentation_roundtrip.py"
    exit: 0
    notes: "Prints an expected self-check FAIL line; exit 0. Intermittent exit 1 under machine load, reproduces on clean main."
  - command: "python tests/packaging_roundtrip.py"
    exit: 1
    notes: "Environment-blocked at the Phase 13-03 onedir sidecar handshake: this bash session's python is a WSL/Linux interpreter and cannot exec the Windows PE itembank-sidecar.exe ('run-detectors: unable to find an interpreter'); Windows cmd/powershell invocation is blocked by the approval gate. The pyz portion (build, resource commands, checksums, launchers, no-bank/no-evidence) passes, including the new subjects.py staging."

duration: 65min
completed: 2026-08-11
status: complete
---

# Phase 9 Plan 01: Subject-Profile Seam and EMT Tracer

**The thinnest production subject-invariant slice: an EMT learner enters the already-built lesson and practice-feedback loop under one selected, persisted data profile**

## Performance

- **Duration:** ~65 min (including Phase-5 gate polling overlap)
- **Started:** 2026-08-11T02:05:00Z (approx)
- **Completed:** 2026-08-11T03:10:00Z (approx)
- **Tasks:** 2 (Task 1 tracer + Task 2 fallback/ambiguity; both TDD)
- **Files modified:** 9

## Accomplishments
- `subjects.py` is the surface-free profile-data module: closed-shape `validate_registry()`, first-seen `subject_ids()` over `evidence.subject_of()`, deterministic `select_profile()` with explicit-id/known-subject/conservative-default/mixed-refusal semantics, capability reporting, and the `session_profile()` stored-snapshot helper.
- Sessions advance to schema v3 with a nullable `subject_profile` snapshot; the v2→v3 upgrade is a one-function entry in `SESSION_UPGRADES` that never touches a bank or settings. New sessions persist the complete snapshot; a legacy session's null slot is filled once, from its own item list, on the first action.
- The EMT tracer drives the real Phase 3 reader, Phase 6 `do_start`/`do_action`, and the one evidence writer end-to-end: wrong submit → hold, authored hint tier 0 → reveal_tier, correct retry → advance, with exactly two response events and one hint event recorded, and `subject=emt` on the response events.
- Resume drift is proven: mutating the live registry after start cannot change the stored snapshot byte-for-byte.
- The D-13 table contract ships in the shared reader — native table semantics inside a labelled, focusable `.lesson-table-scroll` overflow region with `scope="col"` headers and wrapping cells — and the two Phase 3.1 goldens were regenerated to the new wrapper (diff confined to the wrapper line).
- `subjects.py` joined `build.STAGE_FILES` so the new root module ships in the `.pyz`.

## Decisions
- **Selected-items subject resolution in `do_start`:** the profile resolves from the items actually selected into the sitting. An objective-filtered session over a mixed-namespace bank (the existing `evidence_roundtrip` cross-subject fixture) is not ambiguous; an unfiltered mixed sitting still refuses with a named error before any session/evidence file exists. `select_profile` itself remains bank-generic and refuses any mixed input without an explicit id.
- **Temporary `REGISTRY` constant:** shipped known subjects stay in code for this plan only; plan 09-02 replaces them with the validated `subject_profiles` settings group and keeps the conservative default code-owned (D-03).
- **No `lesson_layout` yet:** the 09-01 profile shape is exactly the plan's key set; `lesson_layout` (folded from Phase 3.1 D-04) is added by plan 09-02 per its schema contract.

## Regression Note
- `packaging_roundtrip.py` is environment-blocked at the frozen-sidecar handshake (Windows PE exec unavailable from this WSL bash; cmd/powershell blocked by the approval gate). All pyz-based packaging checks pass, including the staged `subjects.py`. This is upstream Phase 13-03's test, not a Phase 9 deliverable.
