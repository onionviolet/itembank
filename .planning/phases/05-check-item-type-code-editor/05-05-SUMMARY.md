---
phase: 05-check-item-type-code-editor
plan: 05
subsystem: editor-surface
tags: [codemirror, vendor, editor, keyboard, js-test-runner, honest-limits]

requires:
  - phase: 05-check-item-type-code-editor (05-01)
    provides: runner.run_cases, score_response check branches, explain_payload's run_result parameter, model.HONEST_LIMITS_NOTE
  - phase: 05-check-item-type-code-editor (05-03)
    provides: the check settings group, both submit gates, the network refusal decision

provides:
  - asCheck() in the dispatch table of both clients, the .codewrap mount, the honest-limits copy plumbing (one constant, two readers), the CM6 boot script, and the vendored CodeMirror 6 bundle under assets/vendor/codemirror/
  - The per-case run result threaded into both surfaces' explain payloads from the one run that produced the score
  - The CM6 keyboard contract (Tab insert, Shift-Tab dedent, Enter newline, read-only submit lock, no wrap) executed by a jsdom test runner against the real vendored bundle
  - The §4a supply-chain record (VENDOR.md) for the bundle, the boot script and the pinned jsdom runner

affects: [05-06 per-case readout + refusal states, 05-07 render branches/schema/README, Phase 11 authoring surface]

actuals:
  tokens: 60000
  tasks: 3
  commits: 7

tech-stack:
  added:
    - jsdom 29.1.1 (test-time only, pinned in tests/js/package-lock.json) under the §4a rule
  patterns:
    - "One boot script (check-editor-boot.js) is the only place the editor is configured; the page embeds it and the JS test runner loads the same file"
    - "The honest-limits sentence is substituted into both client scripts from model.HONEST_LIMITS_NOTE (D-10: one constant, two readers)"

key-files:
  created:
    - assets/vendor/codemirror/codemirror.bundle.js
    - assets/vendor/codemirror/check-editor-boot.js
    - assets/vendor/codemirror/VENDOR.md
    - tests/js/check_editor.test.mjs
    - tests/js/package.json
    - tests/js/package-lock.json
  modified:
    - surfaces/quiz.py
    - surfaces/quiz_page.py
    - surfaces/session.py
    - surfaces/daemon.py
    - tests/check_roundtrip.py
    - .github/workflows/ci.yml

key-decisions:
  - "The 06-02 adapter already routes both submit paths through session.do_action, which builds the check explain with run_result; the real Task 1 gap was that handle_quiz_answer and handle_api_submit then clobbered it with a run_result-less rebuild. The fix threads run_result through the do_action return for check items and passes it into both explain rebuilds, keeping every non-check response byte-identical."
  - "The editor configuration lives in one vendored boot script (check-editor-boot.js) that the served page embeds and the jsdom test loads -- 'boot the same boot script the page uses' is structural, not a second copy."
  - "The read-only submit lock uses EditorState.readOnly through a Compartment, and the editing key bindings (Tab/Enter/Shift-Tab) are guarded against it, because CM6's insertTab/insertNewline do not consult readOnly themselves."
  - "jsdom 29.1.1 is a pinned test-time dependency with a committed lockfile (the §4a record); it is never loaded by the served page. The CM6 bundle and boot script are committed files embedded inline -- no CDN."
  - "CM6's measurement APIs are shimmed to zero geometry in the jsdom test; the tests assert state and DOM structure, and the 500-line pixel pass stays a manual row in 05-VALIDATION.md."
  - "jsdom does not synthesize native keyboard activation of a focused button, so the Enter/Space-on-Check path is asserted structurally (the control is a real button; the editor's Enter binding never submits) plus the click path -- noted in the test's header comment."

requirements-completed: [CODE-02, CODE-03, CODE-05]

coverage:
  - id: E1
    description: "Per-case actual output, timeout and truncation flags reach both surfaces' response bodies from the one run that produced the score; other item types' payloads are byte-identical"
    requirement: CODE-03
    verification:
      - kind: integration
        ref: "tests/check_roundtrip.py#check_explain_threading"
        status: pass
      - kind: integration
        ref: "tests/check_roundtrip.py#check_http_roundtrip"
        status: pass
    human_judgment: false
  - id: E2
    description: "The check item renders a CodeMirror 6 editor in a .codewrap mount with the honest-limits line from model.HONEST_LIMITS_NOTE, and the CM6 bundle is vendored, pinned, hashed and license-reviewed under §4a"
    requirement: CODE-05
    verification:
      - kind: integration
        ref: "tests/check_roundtrip.py#check_vendor_integrity (bundle SHA-256 vs VENDOR.md, page embeds locally, no CDN URL, locked copy present, sample_bank byte-identical)"
        status: pass
    human_judgment: false
  - id: E3
    description: "Tab inserts a tab and keeps focus; Shift-Tab dedents the current line only; Enter inserts a newline; the editor locks read-only after submit; the gutter is 1-based and grows; a long line does not wrap -- executed against the real vendored bundle"
    requirement: CODE-03
    verification:
      - kind: integration
        ref: "node --test tests/js/ (7/7, jsdom + vendored bundle + boot script)"
        status: pass
    human_judgment: false
  - id: E4
    description: "Browser and /api/submit share the declared response/version, sole-scorer verdict, observations and evidence semantics; no second grader appeared"
    requirement: CODE-02
    verification:
      - kind: integration
        ref: "tests/check_roundtrip.py#check_explain_threading (identical per-case rows via both routes) + python tests/scoring_roundtrip.py"
        status: pass
    human_judgment: false

duration: 180min
completed: 2026-08-11
status: complete
---

# Phase 05: Check item type — Plan 05 Summary

**A real code editor: the check item now renders a vendored CodeMirror 6 field in a
`.codewrap` mount with a scroll-locked 1-based gutter, Tab inserting a tab and Shift-Tab
dedenting the current line only, the honest-limits sentence rendered beside it from the one
constant SPEC reads, and the whole keyboard contract executed by a jsdom test runner against
the same vendored bundle and boot script the page embeds — while the per-case run result now
reaches both surfaces from the one run that produced the score.**

## Performance

- **Duration:** 180 min
- **Tasks:** 3
- **Commits:** 7 (3 test + 3 feat + 0 docs; plan metadata below)

## Task 1 — thread the per-case run result through to the page

The branch's 06-02 adapter already routes both submit paths through `session.do_action`,
which builds the check explain **with** `run_result` (session.py:367). The real gap: both
daemon routes then **clobbered** it with a `run_result`-less `explain_payload` rebuild, so
the browser page would have seen no actual output. Fixed by carrying `run_result` on the
`do_action` submit return for check items and passing it into both explain rebuilds
(handle_quiz_answer, handle_api_submit). `record_answer()` returns `(score, run_result)`
for the CLI contract. Every non-check response body is byte-identical (asserted by exact
key set in `check_explain_threading`). The one-run guarantee is asserted by a side-effecting
fixture whose marker file must hold exactly one line.

## Task 2 — vendor CM6, then the editor mount

- **Vendoring (§4a):** `assets/vendor/codemirror/codemirror.bundle.js` (249 KB IIFE, global
  `CodeMirror`) built by esbuild from pinned `@codemirror/state@6.7.1`, `view@6.43.8`,
  `commands@6.10.4` plus their resolved closure (all MIT). `VENDOR.md` records versions,
  npm shasums, the bundle SHA-256 and a dated license review. `check-editor-boot.js` is the
  one place the editor is configured. The served and built pages embed both locally; no CDN
  URL anywhere (asserted — the page's only http(s) token is the SVG namespace inside the
  bundle).
- **Markup/copy:** `.codewrap` wrapper (one shared monospace declaration inherited by CM6's
  layers), `LABEL.check = "code check"`, the locked placeholder `# Write your code here.`,
  the `runs against %d hidden test case%s` hint, the `Running…` in-flight state, and the
  `__HONEST_LIMITS__` placeholder substituted from `model.HONEST_LIMITS_NOTE` in both client
  scripts (D-10: SPEC and the page read one constant).
- **Byte-identity:** the CM6 tags substitute to empty for a bank with no check item, so
  `sample_bank.md` builds byte-identical to before (asserted with `cmp`).

## Task 3 — CM6 configuration and the JS test runner

- **Boot script:** `check-editor-boot.js` — `lineNumbers()` (1-based, grows), a keymap
  (Tab→insertTab, Shift-Tab→dedent current line only ≤4 spaces, Enter→insertNewline,
  undo/redo), the locked placeholder, `EditorState.readOnly` via a Compartment, and
  deliberately **no** `lineWrapping` (a long line scrolls; gutter row N is line N).
- **Read-only guard:** CM6's editing commands do not consult `state.readOnly`, so the
  editing key bindings are guarded against it — after submit, Tab/Enter/Shift-Tab no longer
  change the document, and the submitted source stays visible.
- **JS test runner (ruling 16):** `tests/js/check_editor.test.mjs` (7 tests) loads the real
  vendored bundle + boot script into pinned jsdom 29.1.1 (`pretendToBeVisual`,
  `runScripts: outside-only` + VM context, geometry shims for CM6's measure loop) and
  executes the contract: Tab inserts a literal tab and keeps focus, Shift-Tab dedents the
  current line only and never past column 0, Enter inserts a newline, the editor is
  read-only after submit with the source visible, the gutter numbers 1..N and grows, and
  the long line stays one line with `lineWrapping` off. jsdom's lack of native button
  keyboard activation is documented in the header; the submission path is asserted through
  the real button's click handler plus the structural fact that the Check control is a
  `<button>` and the editor's Enter binding never submits.
- **CI:** `.github/workflows/ci.yml` gains `actions/setup-node@v4` (Node 20),
  `npm ci --prefix tests/js` and `node --test tests/js/`.
- **Scope:** no syntax highlighting, bracket matching, auto-indent or block-indent — the
  plan's out-of-contract grep is 0, asserted in `check_vendor_integrity`.

## Task Commits

1. `0082ce3` (test) + `005ea95` (feat) — explain threading, both surfaces, one run
2. `1a65e53` (test) + `fe8bbcc` (feat) — vendor bundle, asCheck mount, honest-limits plumbing
3. `48553a2` (test) + `ad6f08b` (feat) — boot script, jsdom test runner, CI wiring

**Plan metadata:** no docs commit yet (05-05-SUMMARY.md is this file's commit).

## Files Created/Modified

- assets/vendor/codemirror/{codemirror.bundle.js, check-editor-boot.js, VENDOR.md} — the §4a vendored editor and its record
- tests/js/{check_editor.test.mjs, package.json, package-lock.json} — the pinned jsdom runner
- surfaces/quiz_page.py — asCheck in both clients, .codewrap CSS, LABEL.check, honest-limits placeholder, CM6 tag/boot placeholders
- surfaces/quiz.py — record_answer returns (score, run_result); CM6 bundle/boot + honest-limits substitution
- surfaces/session.py — do_action returns run_result for check submits
- surfaces/daemon.py — both explain rebuilds pass run_result
- tests/check_roundtrip.py — check_explain_threading, check_vendor_integrity, extended http roundtrip
- .github/workflows/ci.yml — Node step + node --test tests/js/

## Deviations from Plan

- **`grep -c 'check:\s*asCheck'` counts 2, not 1:** the plan's grep assumed a single client
  script, but quiz_page.py ships two (OFFLINE_JS and SERVED_JS), each legitimately carrying
  the dispatch entry. Presence is satisfied in both; the count reflects the file's real
  two-client shape.
- **Task 1 callers differ from the plan's text:** the plan said `record_answer`'s callers
  would be updated, but the 06-02 adapter (already in this branch's base) routes
  `handle_quiz_answer` through `session.do_action`. The plan's intent — the per-case run
  result reaches both surfaces from one run — is met; the threading point moved from
  `record_answer` to the adapter's return + both daemon rebuilds.
- **jsdom vendored as a pinned lockfile install, not committed bytes:** the 39-package
  closure is 26 MB; committing it wholesale would dwarf the repo. The §4a record pins
  jsdom 29.1.1 exactly in a committed lockfile (integrity hashes per package) and CI
  reproduces it with `npm ci --prefix tests/js`. The runtime-facing bundle and boot script
  remain committed files; the served page never loads jsdom.

## Issues Encountered

- **esbuild/npm pruning:** `npm install` in the scratch dir pruned previously installed
  packages each time (npm's --no-save behavior); the bundle build needed the full set
  installed in one command.
- **`lineWrapping` is an extension, not a facet:** the first bundle entry tried to export
  `EditorView.lineWrapping` as a named export; the structural assertion now reads the
  `view.lineWrapping` getter instead.
- **CM6 editing commands ignore `state.readOnly`:** insertTab/insertNewline dispatch even in
  a read-only state; the boot script guards the editing key bindings against it.
- **jsdom lacks layout and native button keyboard activation:** geometry APIs shimmed to
  zero; the Enter/Space-on-Check path asserted structurally + via click (documented in the
  test header). Both limitations are noted in 05-VALIDATION.md's manual rows.
- **Variable-shadowing bug caught by serve_roundtrip:** the boot-script HTML substitution
  initially reused the name `boot`, clobbering the JSON bootstrap object; renamed to
  `cm6_boot_html` and serve_roundtrip passes again.

## User Setup Required

None. The JS runner is pinned and reproducible via `npm ci --prefix tests/js`; no global
install is needed beyond Node 20 (present on this machine and in CI).

## Next Phase Readiness

- 05-06 consumes `asCheck` (refusal branch swaps in for the offline page), the per-case
  explain payload (now carrying actual output on both routes), and the `.case` styles it
  will add.
- 05-07's honest-limits identity assertion can now compare SPEC text and rendered page copy
  — both read `model.HONEST_LIMITS_NOTE`.

---
*Phase: 05-check-item-type-code-editor*
*Completed: 2026-08-11*
