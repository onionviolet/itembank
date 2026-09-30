# Staged and polynomial learner UI, 2026-09-30

Status: implemented and tested on the source daemon with synthetic material.
Owner: parallel learner UI lane. This is bounded verification evidence, not
human acceptance or an installed-release claim.

## Changed behavior

The native served form and JSON client render the runtime's public activity,
carry its activity identity, child identity and submission token, and show the
committed answer during the reason stage. An answer commitment opens the reason
without a correctness cue. Final practice feedback names answer and reason
separately. Exam and diagnostic payloads withhold keyed feedback until the
runtime allows review. A nested submit action forwards the same bounded token
fields; duplicate top-level and nested binding fields refuse before mutation.
Static staged builds refuse explicitly with a serve-required recovery action
before preparing keyed item data or replacing an existing output. The authored
Markdown retains the shared stimulus and both prompts for direct reading.

Polynomial fields use existing native labelled text inputs. Public grammar,
expanded-form instruction, an independent static example and the 160-character
limit are visible. Private targets, authored tests and diagnostic IDs never
enter the learner page. Native refusal and JSON entry-error paths preserve the
original string, including surrounding spaces, and do not advance the cursor
or append a response. Help and refusal are associated with the input, and the
refused input exposes aria-invalid. A reproduced narrow-layout defect made the
long grammar displace the input to a small third flex column. Scoped fill-field
grid rules now give the input full width and place help below it.

The existing choice/position continuity work was protected and extended only
where the independent variants needed it: an incompatible choice draft clears
with a visible revision notice; a resized contextual return restores the
surviving control anchor instead of reusing the old viewport coordinates.
Presentation storage remains disposable and never submits a recovered answer.

## Evidence

Commands completed successfully:

```text
python3 tests/staged_checker_ui_roundtrip.py --browser-shots .reasonix/staged-checker-ui-20260930
python3 tests/staged_checker_continuity_roundtrip.py --browser-shots .reasonix/staged-checker-ui-20260930
python3 tests/quiz_reference_continuity_roundtrip.py --browser
python3 tests/serve_roundtrip.py
python3 tests/fill_surface_roundtrip.py
python3 tests/question_workflow_recovery_roundtrip.py
node --test tests/js/quiz_reference_continuity.test.mjs tests/js/hint_ladder.test.mjs tests/js/question_workflow_recovery.test.mjs
```

The staged/checker suite exercises actual native form POST and JSON nested
submit, practice and exam forms plus diagnostic API, committed answer/reason,
reload, two separate released feedback sections, ordinary successors, private
string scans, unsupported checker refusal with no response event, preserved
draft/reload and a successful equivalent-expression retry. Installed Chrome
passes native keyboard and layout observations at 1280, 390 and 320 pixels.
The input-width and help-placement assertions cover the reproduced defect.
The CLI static-build refusal also preserves a pre-existing synthetic output.

The independent continuity journey passes at the same widths: explicit
reference return, browser Back, resized return with control focus in view,
Enter/Escape help with the exact symbol occurrence retaining focus, changed
public revision with visible choice clearing, and a genuinely held wrong
ordinary response followed by a course detour returning to the same sitting,
item and response count. Injected unavailable local/session storage keeps the
native form usable without recording an answer. The existing reference suite
also passes at 1280 and 390 pixels. Fourteen scoped JS tests pass.

Screenshots live under `.reasonix/staged-checker-ui-20260930/`:
`staged-feedback-{1280,390,320}.png`,
`polynomial-refusal-{1280,390,320}.png`, and
`reference-return-{1280,390,320}.png`.
The final 320-pixel staged feedback and polynomial refusal screenshots were
visually inspected. Polynomial label, full-width raw input, grammar, refusal
and retry control are readable; staged feedback carries two separate verdicts
and completed-case copy. `continuity-measurements.json` records the variant
matrix. This is scripted browser and screenshot evidence, not physical touch
or screen-reader acceptance.

## Limits and recovery

Ordinary script-free quiz GET/teaching paths refresh timing/help presentation
state. Therefore checker-refusal integration asserts unchanged cursor,
responses, status and response evidence, rather than byte identity of the
entire session surrounding those reads. No scoring authority was added.

Historical U1 comparison exploration persistence stays an unresolved product
choice. Its temporary reset-on-reopen contract was not changed. Human learning
value, visual preference, physical touch, screen-reader and installed-app
acceptance remain open. No package, archive, app build, install, commit or push
was performed by this lane. The coordinator owns the source-wide preflight.

Large modules were sampled at public rendering, draft, return-position,
submission and report symbols rather than read whole. All browser banks and
responses were temporary fictional data; owned daemons were terminated and
temporary roots cleaned. Input snapshots and fingerprints were saved outside
scanned source roots as `.py.txt` files. Existing dirty user/agent edits were
preserved. Recovery is a bounded diff against those snapshots, removing the
two new test files and this report while preserving concurrent implementation.

Coordinator recovery follow-up: the three original UI-start snapshots were
copied into `.reasonix/staged-checker-production-20260930/ui-baseline/` as
`quiz.py.txt`, `quiz_page.py.txt` and `daemon.py.txt`. Exact baseline/final
SHA-256 values and bounded task diffs are recorded in that directory's parent
`recovery-manifest.json`. These copies preserve the inherited dirty source;
never reset a whole shared file over subsequent work.
