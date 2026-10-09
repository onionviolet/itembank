# Boundary lab: UI character implementation study

Status: reversible, original design prototype. Three screens share one shell:
course map, concept experiment and a fixed repair example. This is a proposal,
not accepted production UI or comparative learning evidence.

Owner: this prototype for the rendered specimen and checks; the existing
[UI goal review](../../.planning/research/ui-goal-review-2026-09-29.md) owns
experience direction. The [coding record](../../.planning/research/coding-learning-2026-10-01.md)
retains current runtime/feedback implementation ownership.

Preview: serve this directory using Python's stdlib HTTP server and open
index.html. There are no remote assets or dependencies. Original content and
presentation-only interaction stay inside this page. The code example is
read-only; observations are fixed teaching content, not a scored learner run.
Reload restores the selected screen through its URL fragment but resets the
experiment. This specimen does not offer durable learner work or claim native
assessment behavior. A static explanation remains readable without JavaScript.

## Observed bottleneck

The current native synthetic lesson was opened in continuous and guided modes.
In the guided viewport at 1030 by 571 pixels, its first concept heading began
at y=606.8. The visible area held global navigation, application metadata,
the full bank/lesson title, explanatory mode copy and several reader controls.
This is direct rendered evidence of hierarchy on one source-preview route,
not an installed-app or whole-product audit.

The prototype gives the topic, experiment and explanation clear roles. An
original margin mark, dark navigation ground, warm concept stage and semantic
boundary diagram supply character. Course and repair use different compositions
while retaining navigation and typography. This does not imply that a side rail,
the palette, font choices or the exact sample wording are already accepted.

## D1-D5: proposed implementation order

| Code | Work and exact source seam | Observable result and limit |
| --- | --- | --- |
| D1 | Correct the guided lesson's hierarchy in `surfaces/lesson.py:lesson_page` and its existing progressive presentation. Place the current concept before secondary mode/detail controls. Keep continuous reading available and avoid exposing unreleased blocks. | The learner sees what they are learning and can begin in the first viewport. Preserve existing lesson modes, links and runtime-released content. |
| D2 | Give the shared frame and type/control roles one owner in `surfaces/presentation.py`; keep palette ownership in `surfaces/theme.py`. Reconcile older overlapping declarations at their actual owners when implementing. | Course, Learn and Practice remain recognizable as one app, with purposeful hierarchy. Adopt the strongest composition after rendered review; no new theme/profile system is necessary for this slice. |
| D3 | Join the existing native coding unit through course entry, teaching and practice. Use subject-specific workspace composition, `quiz_page.py:question_stem_html`, `baseline_for` and `_check_feedback_html`, and the existing editor. | Predict, inspect a native failing case, use permitted help, repair and return to the right concept with the same session/draft. The current coding lane owns its dirty source; integrate after its handoff rather than overwriting it. |
| D4 | Carry the chosen pattern to one visual unit in a second subject using existing semantic lesson/visual capabilities. The diagram in this specimen is a design demonstration, not a new durable lesson grammar. | Direct manipulation helps explain a concept, with a useful static form and keyboard/touch controls. Add a new semantic capability only if the current contract cannot express the chosen treatment. |
| D5 | Review the complete journey in the final native candidate: course entry, concept, answer, allowed feedback, reference and exact return. Then verify the built and installed candidate through the same task. | Desktop/narrow, light/dark, reload/draft/focus and disclosure checks protect behavior. Direct human visual and teaching review judge quality. Source checks alone do not establish installed or learning acceptance. |

Begin D1 with the current synthetic lesson. Implement one visible native
journey before spreading styling across every screen. Character should come
from the subject, readable composition, meaningful control feedback and concise
human wording. Mascots, decorative scenes, reward systems and a new frontend
framework are not dependencies of this slice; existing optional dispositions
remain available.

## Operation and recovery

Read scope: current project records, targeted presentation/lesson symbols and
the original synthetic source preview. Write scope: this absent-before prototype,
one additive UI goal section and one exact inbox entry. No public upload,
learner material, account, production source, runtime, schema, app, commit or
push is changed. The existing coding and reading-mode writers retain their
paths. New files start from absence; owner appends compare their expected bytes
and publish atomically. The research section records those base fingerprints.

Undo removes this prototype and only the two exact October 1 additions. Keep
other source changes and any later appended entries. This sample is not a fork
of a donor app and introduces no external maintenance dependency.

## Checks

Rendered observations and screenshots live under evidence/. Check results are
recorded after the final specimen inspection. The screenshots show a prototype,
not production integration. Runtime modules were not reviewed; presentation
and lesson modules were sampled by the named symbols rather than read whole.


Final specimen checks: the 1280 by 720 viewport has zero horizontal overflow;
the concept experiment begins at y=269.6 and its observation ends at y=698.1.
The 390 by 844 view also has zero horizontal overflow. Native radio selection
changes equality from excluded to included; Arrow Right changes the selected
value from ten to eleven; Reset returns to strict ten and excludes it. Course
entry, concept/repair navigation and explicit example inspection were exercised.
Reload preserves the selected URL screen and resets temporary experiment/theme
state as documented. Light/dark, course, repair and phone screenshots were saved
and the final desktop/phone images were visually inspected. Temporary viewport
overrides were reset.

HTML IDs are unique, JavaScript syntax passes Node's check and no remote assets
are loaded. Quick source-only preflight passes all executed gates; build, full
Python/JS suites and clean-tree checks are skipped. Local file/anchor references
resolve. The read-only vision audit reports one legacy unresolved link and
existing coverage debt, with no un-routed inbox entries. No screen-reader,
physical-touch, installed-app or human learning/preference acceptance is claimed.


## Direct marker refinement, October 1

[P-20261001-01](../../.planning/PROBLEM-LEDGER.md#p-20261001-01-boundary-marker-looks-draggable-but-is-decorative)
owns the exact feedback and state. This repair supersedes the original separate
slider presentation, whose earlier screenshots remain historical.

The triangle now drags directly; points can be clicked. The gesture uses
[pointer capture](https://developer.mozilla.org/en-US/docs/Web/API/Element/setPointerCapture),
[SVG coordinate mapping](https://developer.mozilla.org/en-US/docs/Web/API/SVGGraphicsElement/getScreenCTM)
and declared [touch behavior](https://developer.mozilla.org/en-US/docs/Web/CSS/touch-action).
Marker grabs retain their offset, preventing an initial jump. The control snaps
to whole numbers and clamps at its bounds. The native range stays exposed for
keyboard and screen-reader use, with focus visibly indicated at the marker.
A 44px hit area, grab/grabbing cursor, state halo and diagram-only selection
suppression improve the same control without introducing a second visible bar.

Browser checks pass: original marker drag reproduced no change, repaired drag
moves ten to thirteen, out-of-track drag clamps to thirteen, point click selects
nine, Home/End and arrows adjust the native value, and a 390px off-center grab
moves seven to eleven. Measured hit width is 44px at both sizes. Overflow is zero
and dragged number labels produce no selected text. New screenshots have the
direct-marker prefix. Temporary viewport overrides were reset.

Operational limits: the browser's read-only evaluator does not expose DOMPoint
construction or ownerSVGElement here. Measure an SVG using its DOM bounding
rectangle, viewBox and preserve-aspect-ratio scale; the page itself uses native
getScreenCTM. Screenshot clipping uses document coordinates; return to scroll
top or include the scroll offset when measuring a clip. In-app CDP rejects
Input.dispatchTouchEvent, so mouse checks are not described as touch proof.
Physical touch, screen-reader, pointer cancellation and human preference remain
open. No production code or scoring/evidence authority changes.

Operation journal: expected index SHA-256
23364962d2a089ae3a65b9978505f9fcff4a820f4398244609cb6133c0666a90;
repaired index SHA-256
594b9dfca1deaaf76b9c8c9e8fce72b4f3474843b17a926403932ed34cac2050.
The prior bytes are evidence/before-direct-marker.html. Restore only after
checking the current fingerprint, and retain later changes and ledger history.


Final repair validation: unique HTML IDs and Node JavaScript syntax pass.
Quick source-only preflight passes every executed gate at the repaired revision;
app build, full Python/JS suites and clean-tree checks are skipped. The bounded
vision/link audit has no unresolved new links or un-routed inbox entries; one
legacy unresolved reference remains. git diff --check passes. The final direct
marker detail image was visually inspected. P-20261001-01 remains a prototype
repair with human acceptance and native integration separate.


## Broader craft pass, October 1

This extends C4-C6 under [the UI goal owner](../../.planning/research/ui-goal-review-2026-09-29.md#october-1-broader-interaction-craft-pass).
The exact user request is captured in the inbox. Findings F1-F5 below are local
to this implementation pass and do not replace older audit codes. This section
supersedes the earlier temporary experiment/theme and separate-bar descriptions.

| Code | Reproduced gap or concrete refinement | Implemented result |
| --- | --- | --- |
| F1 | Old navigation replaced its one history entry; Back left the specimen. Course also showed a link back to itself. | Real screen links, Back/Forward routing, current-tab scroll/focus return and a plain course overview label. P-20261001-02 owns the reproduced defect. |
| F2 | Experiment/rule/theme reset on reload. | Typed, versioned disposable UI cache restores the selected value, rule, theme and open case explanation. No score, note or assessment session is stored. |
| F3 | The explanation revealed through a remote button had no corresponding close state. | Inspect from the mismatch row, explain inline, expose expanded state and close by the same control or Escape without moving focus elsewhere. |
| F4 | Phone layout hid the theme action; code soft wrapping damaged visible structure; diagram labels shrank with the illustration. | One visible 44px theme control on all widths, local keyboard-scrollable code preserving indentation, content-sized code panel and diagram labels with a 12px rendered minimum. |
| F5 | Focus/hover cues were uneven; numeric labels did not select their values; Reset could leave its result off-screen. | Whole-option keyboard focus, contrasting rail focus, clickable values, marker-specific focus, no repeated identical save notices, correct disabled Reset state and immediate visible return to the experiment. |

The local cache key is itembank.boundary-design-study.v1, scoped to this
specimen's origin. Only version/value/rule/night/inspection are stored. Unknown,
malformed or out-of-range saved data is preserved and writes stay blocked until
Reset. A denied write keeps usable state in this tab and reports that state.
This is disposable presentation data, not a new accepted-content or assessment
contract. No learner root, provider call, upload or remote dependency is involved.

Actual checks: browser Back and Forward route correctly; an in-document Back
restores the opener and y=236. Reload restores eleven, inclusive comparison and
night theme; an open case survives reload and Escape closes it. At 390px and
320px there is zero page overflow and the theme control remains 44px. A number
label click selects thirteen; Reset makes the whole experiment visible with
focus at the marker's native range. Axis label glyph bounds are 14px at 320px,
and the drag hit area is 44px. At 320px, the code region has client width 240 and
scroll width 289; Arrow Right produces positive local scroll while page overflow
stays zero. Code, course, inspector and experiment states remain ungraded.

Additional deterministic checks execute the actual cache functions: valid
restore; malformed JSON, future version and out-of-range preservation; denied
write fallback. HTML IDs and final JavaScript syntax pass. Earlier screenshots
remain historical; craft-prefixed captures own this pass. Current screenshots
were visually inspected. Physical touch, screen-reader and human preference
remain open; no installed application changes occurred.

Operation journal: expected index SHA-256
594b9dfca1deaaf76b9c8c9e8fce72b4f3474843b17a926403932ed34cac2050;
final index SHA-256
db447dd3225908175caa05005a1f075da7ebaf177a880dc43071fd0f70f464e9. The previous bytes are
evidence/before-craft-pass.html. Source publication and existing-owner appends
compare their base bytes and use atomic replacement. Undo restores only the
matching specimen snapshot and removes only this pass's additive direction
records; preserve later changes, problem observations and history. Reset returns
the experiment's comparison and value to their defaults. The theme and unrelated
learner work are not reset.

Runtime modules were not read or changed. This pass sampled the current
prototype and its UI/problem owners; it is not an exhaustive native-app audit.


Final gate result for this craft pass: every executed quick source-only preflight
gate passes. Build, full Python/JS suites and clean-tree checks are skipped.
git diff --check passes; new local continuation links resolve and no inbox entry
lacks a disposition. The vision audit retains one unrelated legacy unresolved
link. The final content-sized desktop repair screenshot was visually inspected.
No commit, push, app build, installation or publication occurred.


## A1-A5 receiving implementation pass, October 1

Status: prototype implementation and focused/browser checks complete. This
executes [NEXT-PASS](NEXT-PASS.md); its released baseline stays historical.
F1-F5 and the original synthetic teaching/visual direction are preserved.

| Code | Improvement and disposition |
| --- | --- |
| A1 | Repaired cancellation that previously saved a cancelled drag. A 4px intent threshold and retained grab offset prevent jumps. Release commits; Escape, blur, resize, cancel, lost capture and leaving the view restore the start. Preview never enters the saved cache; native range focus stays intact. |
| A2 | Prototyped one reference on Strictly greater, reusing its static explanation. Hover/focus, deliberate click, Pin/Close, viewport fitting, keyboard entry and Escape return are implemented. Pin state stays temporary. |
| A3 | Added Select code and exact-source Copy code with pending, success, denial and empty states. Copy keeps focus and indentation; code selection and horizontal scroll stay local. |
| A4 | Added saving retry without losing focused controls. Changed/future/corrupt cache bytes stay protected until explicit Start fresh or Reset. Labels distinguish browser settings from tab-only state; identical saves/notices are not repeated. |
| A5 | Kept the solved navigation and content-sized layouts. Added reference keyboard return, visible case expansion and shorter gesture help. Long labels, empty code, dark/light and narrow layouts were checked. |

Desktop 1280x720 and narrow 390x844/320x844 browser tasks pass. A 640px reflow
check also has no page overflow. Escape restores ten after previewing twelve;
outside release saves thirteen; actual resize cancels. Narrow off-center dragging
moves seven to eleven. The final desktop result ends at y=692.9. Copy matches
all 142 source characters in the page clipboard. Back restores the opener at
y=236; reload retains cached settings and URL but starts with BODY focus at y=0.

[Exact actions, fault labels, limits and operational findings](evidence/interaction-checks.md)
include denial/retry, changed/future cache preservation, keyboard Pin/Close,
representative contrast values, before/after captures and native symbols sampled.
Clipboard proof uses only the just-copied synthetic text; the browser tool's
clipboard mirror did not match the page write. Document-only faults were removed
by reload. Four final representative screenshots were visually inspected.

Run `node prototypes/ui-character-20261001/evidence/focused-checks.mjs` from the
repo root. It executes actual gesture/cache/copy functions with controlled doubles,
including fault recovery, and checks source equivalence, IDs/links and JS syntax.
It passes. Every executed `python3 scripts/preflight.py --quick --source-only`
gate passes; build, full Python/JS suites and clean-tree checks are skipped.
git diff --check passes; the browser console has no errors or warnings.

Ranked native opportunities refine the existing D1-D5 route:

| Rank/code | Existing seam and next gate |
| --- | --- |
| 1 / D1 | lesson.py:lesson_page/progressive reader: put the concept in the first viewport, preserving released content and continuous mode. |
| 2 / D3 | lesson.py:_code_block: exact selection/copy for appropriate public examples, with denial, indentation, keyboard scroll and editor/session focus checks. Coordinate with the coding owner. |
| 3 / D4 | quiz_page.py:renderTimeline and sibling tentative-state renderers: direct manipulation in one treatment, preserving runtime commit authority and proving interruption rollback. |
| 4 / D2 | lesson.py:gloss_css/_gloss_trigger_html/GLOSS_HOVER_JS: reuse native glossary/popovers for bounded pin/close/return and viewport tasks; keep presentation/theme ownership and disclosure semantics. |
| 5 / D5 | Complete native course/concept/repair/reference/return task, then separate built/installed and direct human visual/teaching review. |

Physical touch, browser-native zoom, screen readers, human preference and learning
effectiveness remain unverified. This is prototype evidence only. Native source
seams were sampled, not reviewed whole; runtime modules were not read or edited.
Other dirty writers retain their source, fixtures, prototypes and planning files.
No commit, push, app build/install, external message or new chat occurred.

[Operation journal](evidence/interaction-operation.json) records released index
SHA-256 db447dd3225908175caa05005a1f075da7ebaf177a880dc43071fd0f70f464e9 and final
SHA-256 c1b11518d944f8f0f1d0ae503901e8d25f1a5f61de556edd9ea53e2b87dde374.
The initial publication compared the base and replaced it atomically; README
appends compare expected bytes and publish atomically. Recovery snapshots are
evidence/before-interaction-pass.html and evidence/before-interaction-readme.md.
Restore only matching owned bytes or remove only this dated addition, preserving
later work. No remote egress or accepted course/evidence authority changed.


## D1-D5 native parallel implementation, October 1

Status: native source implemented, focused checks and disposable native browser
tasks complete. The existing D1-D5 route now has three parallel lanes: lesson
hierarchy/code/glossary, one comparison visual, and native journey verification.
The frozen prototype and earlier A1-A5 record remain historical.

Guided reading now starts with the concept in the first viewport. Public inert
code has exact Select/Copy, glossary Close/Escape returns to its term, and the
native comparison handle supports threshold, off-center dragging and interruption
rollback. A shared-frame repair prevents app navigation from covering the
scrolled sitting's course-return link. Exact Resume preserves the saved draft.

The [native evidence](evidence/native/checks.md) separates actual browser tasks,
controlled faults, passing focused checks and remaining gates. The
[operation journal](evidence/native/operation.json) records source fingerprints,
protected work and recovery. Reproduce a disposable real course with
`python3 prototypes/ui-character-20261001/native-preview.py`; stop it with Enter.
Run `python3 tests/interaction_craft_native_roundtrip.py` for its HTTP journey gate.

Every executed quick source-only preflight gate passes, together with lesson,
comparison, native-journey, responsive and isolated presentation checks. Native
clipboard readback remains unverified. Exact resumption uses course Resume;
generic Continue to practice retains course context without a session ID.
Installed app, touch, screen-reader, zoom, human preference and learning review
remain open. Source modules were sampled by symbol, not reviewed whole.
No commit, push, app build/install, external message or new chat occurred.
