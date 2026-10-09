# UI GM programme, October 4

STATUS: source released for integration

Owner: UI lane. Authorization: UI-GM.md and current delegated task. Source
baseline HEAD: 28bf561865cf0696a8beb42dd6f356b8bf6ec648 plus inherited dirty
bytes. No Git, package, install, provider, scheduling or private learner writes.
Only fictional fixtures in a disposable local daemon are exercised.

## Frozen finite programme

| ID | Outcome | Wave | Observable gate |
| --- | --- | --- | --- |
| U1 | Compact continuous lesson orientation and reachable section outline | 1 | Less header depth on identical 1280/390/320 content; title, course return, guided switch, semantic material and keyboard/static outline remain available. |
| U2 | Honest learner-facing section practice previews and course context | 1 | No raw fence delimiters or author-only orphan diagnostics in the reader; safe plain/code/math previews; admitted course and exact saved sitting remain intact through practice and return, with no automatic submission. |
| U3 | Direct reader keeps passage foremost and groups secondary tools | 2 | Passage moves upward on identical narrow content; Read/Study/Notebook and deliberate note action remain available; source lookup, text/width tools, note draft/save/reload, stale-source refusal and static source/notes survive. |

No new scoring, durable formats, grammar, rights, canonical operations or
navigation catalogue are selected. U1/U2 own lesson presentation only; U3 owns
reader presentation only. Other reserved files remain unchanged unless a defect
needed to complete these outcomes is demonstrated. At most three ready outcomes.

## Authority, inputs and readiness

Read task packet, shared GM prompt, coordination, execution context, workflow
reading/execution/reporting sections, current STATE October 4 position,
SOURCE-TO-COURSE learner experience and UI-SPEC section 8. Sampled UI goal
review's goal, October 3 findings F1-F5, prior character correction, remaining
continuity criteria and October 1 reading modes. This is not a whole-codebase
or whole-vision audit. Current records supersede earlier gap labels.

Readiness: user goal, writer, current baseline, presentation boundaries,
observable gates, recovery and open human/installed gates are named. Accepted
files and runtime remain authoritative. Local browser egress is loopback only.
Source changes use bounded context-checked patches against pinned dirty bytes;
the original bytes are recoverable without resetting another lane's work.

## Baseline and evidence

Installed Chrome via existing Python Playwright 1.62.0 captured 30 actual native
views across desktop 1280, narrow 390/320, light/dark, reduced motion and 390
script-free fallback. Receipts and screenshot files live in ignored
`.reasonix/product-gm-ui-20261004/before/`. Its `result.json` records all nine
reserved presentation input hashes; `base/*.py.txt` preserves the inherited
bytes. Viewports inspected: continuous lesson 1280/390 and direct reader 390.

F1: continuous lesson repeats Application and a bank-oriented byline above the
material. First section is visibly below a large header gap; outline is absent
in the sampled coding unit. F2: backlinks still use raw stem truncation and a
bare quiz URL. F3: the direct reader's expanded selection and context toolbar
pushes the passage down on narrow screens. Existing reader tint/serif character
and notes are useful and will be retained.

Coverage: D1 learning content sampled, unchanged semantic fidelity required;
D2 learner composition inspected and in progress; D3 existing lesson/source/
practice integration sampled; D4 draft/return/stale/fallback gates pending;
D5 symbol-first maintenance, focused checks and recovery inputs established.

## Shared requests for integration

S1: course-level repeated context and competing resume labels remain owned by
integration's daemon/course-frame paths (latest UI review F1/F2). This lane
does not implement that shared change. Preserve read-only entry and distinct
pending/unavailable sessions if integration adopts it.

S2: lesson section actions now reuse admitted matching-bank `context_nav` hrefs.
The existing daemon accepts exact sitting context through a validated `return`
URL and these section links preserve it. Ordinary Learn-to-lesson entry supplies
course context only, so it cannot promise exact saved-sitting selection. A native
browser check reproduced this distinction. Course-aware saved-sitting selection
from ordinary Learn, or targeting a referenced Q2 while a saved sitting is on
Q1, belongs to daemon/runtime integration and is not inferred in presentation.

S3: integration owns compatibility updates for intentional presentation changes.
`tests/lesson_roundtrip.py` fails its Phase 3 HTML golden (3550 versus 3415
characters), and later checks still expect orphan diagnostics and no auto
outline at three headings. `tests/lesson_progressive_roundtrip.py` still expects
About to be absent in continuous/paced. U1/U2 remove those diagnostics, expose
visible outlines and collapse secondary metadata. Update these assertions and
the owning golden after inspecting the new reader, without weakening content,
required-gate, keyed-disclosure or guided-stage equivalence checks.

## Implementation and repair

U1/U2 lesson worker released its first patch and six focused checks plus eight
existing suites. Evidence is in `lesson-worker.md`. U3 groups source support
inside native Reading tools while keeping mode and note controls prominent.
Escape closes tools and returns keyboard focus; note/context detours close the
panel without saving or declaring reading. Original source/notes colors and
serif material remain. Current reader checks: 7 reading-desk, 14 declaration,
3 workspace, 4 existing workspace JS and 3 new keyboard-tool JS tests pass.

After capture passed 30 native views with no viewport overflow at 1280/390/320.
Lesson 390 first section moved from about 420 to 300px; source passage moved
up approximately 65px. Screens visually inspected: lesson 1280/390 and reader
390. Parent requested one U1 repair: the newly exposed auto outline used the
legacy 18ch rail at desktop, creating a small wrapping stub. Automatic outlines
will use the existing in-flow column; explicit authored rails remain available.

Verification retries: the new native snapshot initially counted the existing
saved-sitting serialization `.json.lock` creation as content mutation. Its
receipt now permits only that exact coordination file, existing served_ts and
known derived evidence indexes, and still asserts canonical data/response
stability. The first joined browser assumed Learn implicitly admitted a saved
sitting; the actual href has only course. The harness now checks that truthful
path separately from the existing validated exact `return` path. These were
harness corrections, not production scoring or persistence repairs.

## Current limitations and recovery

Source is uncommitted and not packaged or installed. Human visual preference,
screen reader, physical touch and learning effectiveness remain unverified.
Only integration may run the combined broad gate after explicit path release.
Undo only this lane's reviewed diff against current files; never overwrite the
shared checkout with its baseline copies. Additional evidence will be appended
here during implementation and release.

## Final outcome receipts and release

U1-U3 finish their bounded source/browser gates. Automatic outlines now use an
in-flow column in continuous reading; guided retains its original first-section
position and honors explicit outline preferences. U2 preserves the exact admitted
quiz URL and says Return to saved sitting when a runtime-owned item is already
active. It does not promise to select the previewed question. U3 keeps passage,
draft, note and source state distinct, with secondary tools grouped deliberately.

Final source screenshots: `.reasonix/product-gm-ui-20261004/release/`, 30 actual
native views. Joined browser receipt: `.reasonix/product-gm-ui-20261004/journey-final/`.
Both commands completed with exit 0 on the final source. Comparison is available
in [comparison.html](comparison.html), using actual before/release screenshots.
No viewport overflow at 1280/390/320; light/dark, reduced-motion and 390px
script-free source, lesson, guided, course and practice were inspected or measured.
Visual inspections include final lesson 1280/320, guided390, direct reader320,
earlier light/dark390, script-free390 and explicit stale-source320 screenshots.

| Surface | Width | Before first material y | Final y | Change |
| --- | --- | --- | --- | --- |
| Continuous lesson | 1280 | 447.34 | 323.00 | 124.34px higher |
| Continuous lesson | 390 | 415.34 | 291.00 | 124.34px higher |
| Continuous lesson | 320 | 474.53 | 357.00 | 117.53px higher |
| Direct source passage | 1280 | 564.84 | 545.63 | 19.21px higher |
| Direct source passage | 390 | 618.77 | 549.14 | 69.63px higher |
| Direct source passage | 320 | 670.77 | 549.14 | 121.63px higher |
| Guided first section | 1280/390/320 | 303.39 / 271.39 / 311.39 | Same | No added header depth |

Final joined browser exercises course -> Learn -> continuous lesson -> section
practice, ordinary course context versus validated exact sitting return,
unchanged active question, unsubmitted native radio draft through course return
and reload, no new response, keyboard outline, tool Enter/Escape, invalid selection
retry focus, Read -> Notebook -> exact passage/mode/scroll return, refused note
save, draft reload, successful retry, saved-note display and stale-source refusal
with copyable prior wording. Widths 1280 light, 390 light and 320 dark pass.
Explicit saved-sitting GET permits only its serialization lock and served_ts;
canonical course/notes/evidence/session content remains unchanged before any
explicit note save or other learner action.

Independent delta review in [REVIEW.md](REVIEW.md) reproduced and resolved one
introduced P2 defect: invalid Ask about selection activation closed its tool
panel and lost focus. Removing the unconditional close preserves the existing
validation and retry focus. New JSDOM and full native Chrome checks pass after
repair. Review found no other concrete introduced defects in its sampled delta.
The review is not human accessibility certification.

### Exact focused commands

```
python3 tests/product_gm_ui_lesson_roundtrip.py
python3 tests/product_gm_ui_journey_roundtrip.py --browser-shots .reasonix/product-gm-ui-20261004/journey-final
python3 .planning/research/product-gm-2026-10-04/ui/capture.py --output .reasonix/product-gm-ui-20261004/release
node --test tests/js/product_gm_ui_reader_tools.test.mjs tests/js/reading_workspace_modes.test.mjs
python3 tests/reading_desk_roundtrip.py
python3 tests/reading_declarations_roundtrip.py
python3 tests/ui_overhaul_workspace_roundtrip.py
python3 tests/ui_overhaul_journey_roundtrip.py
python3 tests/quiz_symbol_return_roundtrip.py
python3 tests/course_guidance_journey_roundtrip.py
node --test tests/js/reading_note_save.test.mjs tests/js/lesson_craft.test.mjs tests/js/lesson_exploration_continuity.test.mjs tests/js/product_gm_ui_reader_tools.test.mjs
git diff --check -- surfaces/lesson.py surfaces/reading_desk.py
```

All listed commands passed. New lesson suite has eight cases; reader tool and
workspace JS have eight combined; the broader focused JS group had 21 passing
cases before the additional invalid-selection regression, which subsequently
passed in the final eight-case command. The worker record names eight additional
passing lesson/source/UI suites and focused existing guided checks. The two
integration-owned compatibility suites listed in S3 remain failed on their old
golden/assertions; neither is reported as a full pass. No broad preflight run.

The final course-guidance native journey also passed current changed-source,
changed-bank, rights and ambiguous-sitting refusal, pending/blind feedback,
exact detour/reload/restart and retraction checks. Its malformed/future evidence
warnings come from intentionally injected synthetic failure cases.

Process evidence: one builder worker, one independent reviewer, three scoped
repairs (desktop auto-outline composition, guided header depth and invalid
selection focus), two harness assumption corrections and one mobile navigation
locator correction. Mobile Course area is a native closed disclosure; actual
keyboard/click journeys must open it before selecting Learn rather than clicking
the hidden desktop link. The saved-sitting serialization lock is coordination,
not a response or canonical content change. These reusable observations stay
here rather than in provider memory.

### Released paths and fingerprints

All packet presentation reservations are released to integration, including
unchanged paths. Only reading_desk.py and lesson.py differ from UI input copies:

```
surfaces/presentation.py
surfaces/home.py
surfaces/reading_desk.py
surfaces/lesson.py
surfaces/day.py
surfaces/day_document.py
surfaces/quiz_page.py
surfaces/quiz.py
surfaces/study.py
tests/product_gm_ui_lesson_roundtrip.py
tests/product_gm_ui_journey_roundtrip.py
tests/js/product_gm_ui_reader_tools.test.mjs
.planning/research/product-gm-2026-10-04/ui/
```

| Changed file | Released SHA-256 |
| --- | --- |
| surfaces/lesson.py | 77dd3fcab85db682f9ecfe1c0028e885e4f22100af87cda23b55a7b288d7dcca |
| surfaces/reading_desk.py | 0b6fddc95880c5323f0557b8930b8fae184cb89153c3a4395a0a213cc5db559d |
| tests/product_gm_ui_lesson_roundtrip.py | e7cd4916e9bcb294a41800ab91d0d028d9541e25b4f0bab46e6fedd51c1ac32f |
| tests/product_gm_ui_journey_roundtrip.py | 473a21889a2a3ee0cd72d4082c808b313d249c137353ffe934013eef8f3815e2 |
| tests/js/product_gm_ui_reader_tools.test.mjs | 945a3e06e2520557cc3a4511fa10cc1346709abda97e8138b2347d6de7398790 |

`release/result.json` records all nine reserved final hashes; the seven unchanged
sources match `before/result.json`. No shared/backend path or existing shared test
was edited by this lane. Each disposable daemon and browser from capture/journey
was terminated and its synthetic root cleaned on completion. No active child
writer remains. Source is local, uncommitted and released for integration.

Coverage at release: D1 semantic/static fidelity sampled, learning effectiveness
unverified; D2 U1-U3 measured and exercised, human preference/screen reader/physical
touch open; D3 admitted course/source/lesson/practice flow exercised, targeted-item
selection limit named in S2; D4 draft/refusal/reload/stale/fallback gates pass for
sampled synthetic paths, broader restore owned by integration; D5 bounded diffs,
input/output hashes, regression checks and recovery evidence retained.

Next integration action: reconcile S3 presentation compatibility assertions and
run the sole combined broad gate after the other writer lanes also release.
S1 course header/resume composition and S2 ordinary Learn saved-sitting semantics
remain reviewed shared requests, not claims of completed UI parity. Human,
package/install and exact format decisions stay with their existing owners.
