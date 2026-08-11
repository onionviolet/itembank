---
phase: 09-subject-invariant-loop-emt-math-cs-integration
plan: 04
subsystem: offline-math
tags: [katex, vendoring, offline, math-adapter, allowlist, packaging]

requires:
  - phase: 09-subject-invariant-loop-emt-math-cs-integration (09-03)
    provides: approved katex=0.18.4 (official KaTeX/KaTeX tag v0.18.4, MIT, npm sha512 integrity IMPntbRLOU+eu88XDiFKqQ8Akhr9Tv7jDMXqPhjG9SI1JMA4DIgXk4x9k4skJz2NZJXBRbC+2pYBLj9olqcZow==)
  - phase: 09-subject-invariant-loop-emt-math-cs-integration (09-01/09-02)
    provides: subjects.select_profile/session_profile/load_registry, lesson.math capability, v3 session snapshot
provides:
  - Vendored immutable KaTeX 0.18.4 browser distribution under vendor/katex/ (katex.min.css, katex.min.js, contrib/auto-render.min.js, all 60 CSS-referenced fonts, LICENSE)
  - Explicit vendor staging in build.STAGE_DIRS; checkout/.pyz byte parity through resources.read_bytes()
  - Closed KATEX_ASSETS route map in surfaces/daemon.py serving GET /assets/katex/<known-name> with exact MIME types; hostile names 404
  - Lesson-scoped renderMathInElement adapter (trust:false, throwOnError:false, maxExpand:1000, maxSize:50, display-before-inline, #lesson-content only, pre/code immune) with exact unavailable/parse-failure copy
  - tests/math_offline_roundtrip.py: local-only asset graph, exact MIME/bytes, hostile 404s, profile gating, code-fence immunity, zero evidence/session delta, packaged parity
affects: [09-05 runnable-code clients + fixtures, Phase 10]

actuals:
  tokens: 0
  tasks: 2
  commits: 1

tech-stack:
  added:
    - "katex 0.18.4 (vendored browser distribution only; no npm/runtime/build dependency)"
  patterns:
    - "The one resource reader (resources.read_bytes) is the sole asset source in checkout and archive; STAGE_DIRS is the explicit bundled-directory allowlist"
    - "A closed URL-suffix -> (archive-relative path, MIME) map, never a request-derived filesystem path (T-09-09)"

key-files:
  created:
    - vendor/katex/
    - tests/math_offline_roundtrip.py
    - .planning/phases/09-subject-invariant-loop-emt-math-cs-integration/09-04-SUMMARY.md
  modified:
    - build.py
    - surfaces/daemon.py
    - surfaces/lesson.py
    - tests/packaging_roundtrip.py
    - tests/lesson_roundtrip.py

key-decisions:
  - "The tarball sha512 base64 and npm shasum (sha1) were verified at fetch time; the plan's 64-hex sha256 was computed from the verified bytes and recorded here: 0090b1ebccc77d1402ec95e85ee539e1da514d6cd6934156c00baf39dcb0e3aa."
  - "Only the browser distribution is vendored: the three minified browser files, LICENSE, and every font URL katex.min.css references (20 families x 3 formats = 60). No katex.js (unminified), katex.mjs/esm, source maps, README, package.json, contrib extras (mhchem/copy-tex), src/, or build tooling entered the repository (Task 1 Test 4)."
  - "The daemon lesson route resolves the subject profile exactly as a session would (subjects.select_profile over the bank) so the served page's math flag is authoritative; cmd_lesson passes no profile, keeping a static render source-only (enhancement is a served-page capability). The stored-snapshot consumption and explicit --profile wiring land in 09-05."
  - "The KATEX_ASSETS map is closed over the reviewed inventory: the three browser files plus the exact font set the CSS names. Font names are data in the map, never derived from a request; the name regex admits only [A-Za-z0-9_./-] and the handler does a dict lookup, so encoded/traversal/query-manipulated names are 404s with no path join."
  - "The adapter adds the exact 09-UI-SPEC copy: a missing/corrupt asset set appends one lesson-level 'Math unavailable. Formula source is shown.'; a parse failure leaves KaTeX's own error output (source, readable) plus 'Math could not be rendered. Formula source is shown.' beside it. No CDN fallback, no deletion of source, no math-derived value reaches scoring/feedback/evidence (D-08)."

patterns-established:
  - "Presentation-only enhancement rides the existing profile/presentation seam: lesson_page(..., profile=snapshot) switches on only lesson.math; EMT/plain profiles render the pre-09-04 reader byte-for-byte."
  - "Static assets are a closed route map, not a filesystem walk: the daemon serves exactly the reviewed vendored names, and the packaging test proves the .pyz carries the identical bytes."

requirements-completed: [LOOP-02]

coverage:
  - id: D6
    description: "Inline $...$ and display $$...$$ math render inside lesson content from the approved local KaTeX distribution with no CDN or build step: the math page references only /assets/katex/ URLs in CSS-then-core-then-auto-render order, and a daemon running from the .pyz serves archive bytes identical to the checkout."
    requirement: LOOP-02
    verification:
      - kind: integration
        ref: "tests/math_offline_roundtrip.py#test_math_profile_page_emits_local_assets_in_order"
        status: pass
      - kind: integration
        ref: "tests/math_offline_roundtrip.py#test_packaged_artifact_serves_the_same_assets"
        status: pass
    human_judgment: false
  - id: D7
    description: "Invalid or unsupported math remains readable as source with an honest unavailable/error state: the adapter keeps raw source in the page, uses throwOnError:false, and appends exactly the locked parse-failure or unavailable copy."
    requirement: LOOP-02
    verification:
      - kind: unit
        ref: "tests/math_offline_roundtrip.py#test_math_profile_page_emits_local_assets_in_order"
        status: pass
    human_judgment: false
  - id: D8
    description: "Math enhancement never enters runtime.score_response, item verification, feedback policy, or evidence: the rendered page carries no /api/* call, no fetch/XMLHttpRequest, no score_response/evidence reference, and fetching a lesson plus its assets writes no evidence and no session file."
    requirement: LOOP-02
    verification:
      - kind: integration
        ref: "tests/math_offline_roundtrip.py#test_offline_page_writes_no_evidence_and_no_session_delta"
        status: pass
    human_judgment: false
  - id: D9
    description: "The complete CSS/JS/font distribution is present in a checkout and the built .pyz, and every asset request is allowlisted: the closed KATEX_ASSETS map serves exact MIME/bytes for every CSS-referenced font and the three browser files, while unknown, encoded, nested, traversal, and query-manipulated names are 404s with no bytes leaked."
    requirement: LOOP-02
    verification:
      - kind: integration
        ref: "tests/math_offline_roundtrip.py#test_asset_route_exact_mime_and_checkout_bytes"
        status: pass
      - kind: integration
        ref: "tests/math_offline_roundtrip.py#test_hostile_asset_names_are_404"
        status: pass
    human_judgment: false
  - id: D10
    description: "Enhancement is scoped to #lesson-content with display-before-inline delimiters, trust:false, throwOnError:false, maxExpand:1000, maxSize:50, ignored pre/code; EMT/plain profiles emit no math adapter, and a dollar-shaped code fence survives verbatim."
    requirement: LOOP-02
    verification:
      - kind: integration
        ref: "tests/math_offline_roundtrip.py#test_emt_and_plain_profiles_emit_no_math_adapter"
        status: pass
      - kind: unit
        ref: "tests/math_offline_roundtrip.py#test_profile_snapshot_drives_the_presentation_seam"
        status: pass
    human_judgment: false

verification-runs:
  - command: "python tests/math_offline_roundtrip.py"
    exit: 0
  - command: "python tests/lesson_roundtrip.py"
    exit: 0
  - command: "python tests/packaging_roundtrip.py"
    exit: 1
    notes: "All packaging assertions pass including the new vendored-katex inventory; the process exits 1 only at the Phase 13-03 onedir sidecar handshake, which is environment-blocked in this WSL session (the Windows PE itembank-sidecar.exe cannot be exec'd by the Linux interpreter) -- the documented pre-existing block, not a 09-04 regression."
  - command: "python tests/daemon_roundtrip.py"
    exit: 0
  - command: "python tests/subject_loop_roundtrip.py"
    exit: 0
  - command: "python tests/protocol_roundtrip.py"
    exit: 0
  - command: "python tests/agent_roundtrip.py"
    exit: 0
  - command: "python tests/config_roundtrip.py"
    exit: 0
  - command: "python tests/evidence_roundtrip.py"
    exit: 0
  - command: "python tests/scoring_roundtrip.py"
    exit: 0
  - command: "python tests/selection_roundtrip.py"
    exit: 0
  - command: "python tests/hint_roundtrip.py"
    exit: 0
  - command: "python tests/serve_roundtrip.py"
    exit: 0
  - command: "python tests/style_roundtrip.py"
    exit: 0
  - command: "python tests/surface_roundtrip.py"
    exit: 0
  - command: "python tests/theme_roundtrip.py"
    exit: 0
  - command: "python tests/update_roundtrip.py"
    exit: 0
  - command: "python tests/presentation_roundtrip.py"
    exit: 0
  - command: "python tests/day_roundtrip.py"
    exit: 0
  - command: "python tests/day_edit_roundtrip.py"
    exit: 0
  - command: "python tests/due_roundtrip.py"
    exit: 0
  - command: "python tests/durability_roundtrip.py"
    exit: 0
  - command: "python tests/gift_export_roundtrip.py"
    exit: 0
  - command: "python tests/import_roundtrip.py"
    exit: 0
  - command: "python tests/launcher_roundtrip.py"
    exit: 0
  - command: "python tests/model_adapter_roundtrip.py"
    exit: 0
  - command: "python tests/model_evidence_roundtrip.py"
    exit: 0
  - command: "python tests/model_gate_roundtrip.py"
    exit: 0
  - command: "python tests/model_surface_roundtrip.py"
    exit: 0
  - command: "python tests/anki_keys_roundtrip.py"
    exit: 0
  - command: "python tests/packaging_shell_roundtrip.py"
    exit: 0
  - command: "python itembank.py guard ."
    exit: 0
  - command: "python itembank.py lint fixtures/sample_bank.md"
    exit: 0

human-check:
  - "Open the packaged Math lesson with networking disabled and confirm one inline and one display expression render, malformed TeX remains readable, and code fences containing dollar signs are unchanged (glyph/layout pass; the automated suite proves the offline resource graph and DOM/state contract)."
