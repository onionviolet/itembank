---
phase: 09-subject-invariant-loop-emt-math-cs-integration
plan: 05
subsystem: subject-invariant-loop
tags: [runnable-code, runner, profile-wiring, common-loop, matrix]

requires:
  - phase: 09-subject-invariant-loop-emt-math-cs-integration (09-01)
    provides: subjects.select_profile/session_profile/load_registry, v3 session snapshot, EMT semantic table wrapper
  - phase: 09-subject-invariant-loop-emt-math-cs-integration (09-02)
    provides: subject_profiles settings registry, configuration-only fourth profile
  - phase: 09-subject-invariant-loop-emt-math-cs-integration (09-04)
    provides: vendored KaTeX + /assets/katex route + lesson math adapter
  - phase: 05-check-item-type-code-editor
    provides: runner.run_cases/_spawn_and_drain bounds, check settings group, LAN/language refusal policy
provides:
  - runner.run_source(language, source, stdin_text, timeout_seconds, max_output_bytes, languages) -- the one process primitive shared by lesson observations and run_cases(); stderr + exit_code (None on deadline-kill) added to the drain
  - surfaces/daemon.execution_refusal(handler, language, check_settings) -- the shared LAN-default + language-allowlist gate; _check_refusal_body keeps check-submit refusal bodies byte-for-behavior
  - POST /api/lesson/run -- accepts exactly {session_id, block_id, language, source}; resolves session + stored profile + bank + parsed-lesson fence; gates profile/settings/LAN/source-size before one run_source() call; observation-only response (no passed/score/correct/verdict)
  - Runnable lesson-code UI in surfaces/lesson.py -- stable sequential data-code-block ids, Example-code/source labels, textarea, keyboard help, native Run example, persistent role=status, labelled non-live stdout/stderr, exact 09-UI-SPEC state copy, static/disabled/LAN states, adapter ships only when a block rendered a Run control
  - One subject-profile id wired through CLI start/lesson (--subject-profile), /api/start (profile), and /lesson/<bank>?profile=; only the id crosses a client boundary; do_start(..., profile_id=None) resolves once and persists the snapshot
  - fixtures/subject_loop_{emt,math,cs}.md -- three synthetic guided-discovery fixtures; tests/subject_loop_roundtrip.py table-driven four-profile matrix; tests/lesson_code_roundtrip.py
affects: [Phase 10 retention (subject_profile + retention coexist in the session), resume fidelity]

actuals:
  - "run_cases() delegates its plain-case process invocation to run_source() with the comparison contract byte-unchanged (per-case dict keys passed/actual/timed_out/truncated/case_index; timeout -> no verdict via the scorer)."
  - "The 09-05 main-merge (0ce8a2c) and the handoff-mandated Phase-5 merge (8c9ddf3) brought main's phases 3.1/6.1/6.2/8-05/9.1/10 and Phase 5's runner onto the branch; 8 conflicts (main) + 4 (phase-05) resolved keeping both phases' behavior -- including runtime.visual_interaction_result (renamed so Phase 5's interaction_result keeps the shared name), the evidence index context column (a main-side latent 06.2 gap, INDEX_VERSION 3), and the visual item type added to the profile allowlists."
  - "A hint request on a check item no longer demands source text (the check-source branch runs only for submit actions), unlocking the CS row of the shared guided-discovery loop."
  - "lesson_page gained session_id/lan_refused params; cmd_lesson and the daemon route resolve the profile through the same selector so fence copy is byte-identical; math enhancement stays served-page only."

key-files:
  created:
    - fixtures/subject_loop_emt.md
    - fixtures/subject_loop_math.md
    - fixtures/subject_loop_cs.md
    - tests/lesson_code_roundtrip.py
    - .planning/phases/09-subject-invariant-loop-emt-math-cs-integration/09-05-SUMMARY.md
  modified:
    - runner.py
    - surfaces/daemon.py
    - surfaces/lesson.py
    - surfaces/session.py
    - surfaces/cli.py
    - evidence.py
    - tests/subject_loop_roundtrip.py
    - tests/check_roundtrip.py
    - tests/lesson_roundtrip.py
    - tests/daemon_roundtrip.py
    - tests/math_offline_roundtrip.py
    - tests/model_ui_roundtrip.py
    - tests/scoring_roundtrip.py
    - tests/evidence_roundtrip.py
    - tests/visual_roundtrip.py
    - tests/visual_authoring_roundtrip.py
    - fixtures/lesson_golden_phase3_content.txt
    - itembank.json
    - schemas/settings.schema.json
    - build.py
    - tests/config_roundtrip.py
    - surfaces/settings.py
    - .planning/STATE.md (merge: main's version, orchestrator-owned)

key-decisions:
  - "One runner: lesson Run and check submission share run_source() + the Phase 5 bounds/tree-cleanup; there is no second process implementation (D-09). A run the deadline killed reports exit_code None (no exit of its own), mirroring the scorer's no-verdict contract."
  - "Lesson Run is observation only: the endpoint returns stdout/stderr/exit_code/timed_out/truncated and touches no cursor, teaching state, or evidence (D-11); the page's role=status announces only the concise summary and stdout/stderr are never live."
  - "The daemon resolves the block id against the parsed lesson's ordered fence list -- lesson_fence_languages() walks headings with the same _FENCE_RE + open-to-closer consumption as the renderer, so a data-code-block id always names the same fence (D-05, no reparse)."
  - "The subject-profile flag is --subject-profile (the plan's bare --profile is already the selection-profile flag); /api/start accepts profile as an allowed identifier while profile CONTENT stays forbidden on every route (api_read_json allowed_ids)."
  - "A known profile with no runnable languages renders fences like an unknown profile (static copy), keeping the 09-04 byte-identity contract between profile and no-profile renders; a non-empty runnable list makes an outside language the disabled-language state."
  - "The adapter and runnable CSS/JS ship only when at least one fence actually rendered a Run control: no runnable blocks -> no empty runner panel and no script (the gated/no-run reader stays script-free)."

requirements-completed: [LOOP-01, LOOP-03, LOOP-04, LOOP-05]

coverage:
  - id: D9-D11
    description: "One runner shared by lesson and check execution; server-side profile/language/settings/LAN/source gates before invocation; observation payloads carry no correctness authority; Run changes no session or evidence state."
    requirement: LOOP-03
  - id: D1-D4
    description: "CLI, API, reader, and resumed sessions resolve one profile id through the same server-side selector; only the id crosses a client boundary; unknown/mixed fail before writes without path disclosure; resume consumes the stored snapshot."
    requirement: LOOP-01
  - id: D12-D15
    description: "EMT, Math, CS, and a configuration-only fourth profile traverse one table-driven driver with identical transitions, cursor progression, authored tier-0 hint, evidence spine, and final outcome; only fixture path, profile id, medium assertion, item type, verifier, and response vary."
    requirement: LOOP-01/04/05
  - id: UI-SPEC
    description: "Runnable-code state machine and exact copy (ready/running/completed/timeout/truncated/request-error/disabled/static/LAN), data-code-block identity, non-live labelled streams, edit retention, independent blocks, focus/escape hooks, reduced-motion and narrow/zoom CSS hooks are implemented and machine-asserted; keyboard/narrow/assistive behavior is the manual phase-verification item."
    requirement: LOOP-03
