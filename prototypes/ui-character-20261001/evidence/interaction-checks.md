## A1-A5 receiving implementation pass, October 1

Status: local prototype implementation and focused/browser verification complete.
This executes [the released packet](../NEXT-PASS.md); its frozen baseline remains
historical. The same original synthetic source and visual direction remain
changeable. F1-F5 were preserved, with only related lifecycle repairs added.

| Code | Disposition and resulting behavior |
| --- | --- |
| A1 | Implemented a reproduced repair. Escape originally kept twelve after dragging from ten. A marker grab now waits for 4 CSS pixels of movement and retains its offset. Release commits the clamped whole-number value; Escape, blur, resize, pointer cancellation, lost capture, navigation and page exit restore the starting value. Preview values never enter the saved cache. A visible preview label distinguishes tentative movement; the existing range retains focus and keyboard semantics. |
| A2 | Prototyped a compact reference on the actual Strictly greater term. It reuses the adjacent explanation and static comparison. Mouse hover and keyboard focus open a transient card; click pins it, including the deliberate opening path intended for touch. Pin/Unpin, Close and Escape work. Tab or Arrow Down enters its controls; Close/Escape returns to the term. The card fits the viewport and leaves the term and diagram visible. It is temporary presentation state, not another lesson or saved annotation. |
| A3 | Implemented Select code and exact Copy code. The source remains byte-equivalent to the original six-line example after HTML decoding. Copy retains focus, blocks duplicate pending activation and distinguishes copying, success, denial and empty content. Denial offers manual selection/copy. Selection covers only code, with a contrasting selection color and local horizontal scrolling. No pre-existing private clipboard text was printed. |
| A4 | Implemented honest cache recovery. Labels name this browser's settings, not durable learner work. Denied storage offers Retry saving. Success keeps that focused button visible as Save again. Changed cache bytes are preserved and block writes; Start fresh explicitly accepts the current specimen settings in their place. Malformed and future caches retain the existing restrictive behavior. Identical saves and notices are not repeated. |
| A5 | Reused the solved history, local scrolling and content-sized panels. Added keyboard traversal/return for the card, nearest-visible expansion for the case explanation, focus-preserving retry and a shorter gesture hint so the desktop result stays in the first viewport. Long-label and empty-code faults reflow without page overflow. Native integration and human visual preference remain separate. |

Browser evidence uses the in-app browser, mouse/CDP mouse input and native
keyboard actions. Desktop is 1280 by 720; narrow views are 390 by 844 and
320 by 844, with one 640 by 720 reflow check. Temporary viewport overrides
were reset. The original course-to-concept-to-fixed-repair journey was walked
before editing. No new code execution or assessment scoring was introduced.

Exact observations: a two-pixel off-center move leaves ten unchanged; a longer
move previews twelve and Escape restores ten across reload. Release outside
the diagram saves thirteen. Resizing during a preview restores ten and clears
grab state. At 390px, a sixteen-pixel off-center grab moves seven to eleven,
keeps range focus and selects no page text. Its hit width is 44px. Page overflow
is zero at every tested width. The final desktop observation ends at y=692.9.

Mouse hover opens unpinned and closes after leaving; keyboard Tab enters Pin,
then Close, and Escape returns to strict-term. At 320px the dark reference spans
x=12 to 308 and y=479.4 to 739.4, below its opener. Code Arrow Right produces
scrollLeft=25 with clientWidth=240 and scrollWidth=289. Select code matches the
complete source and focuses code-example. After a page copy, a same-page
clipboard comparison matches all 142 characters, including indentation.

Clipboard denial, storage denial, future-version cache, changed external bytes,
empty code and a long action label were narrowly injected into this synthetic
page through CDP and labeled as deterministic faults. The real page handlers
show refusal/recovery states, never a fake success. Future and changed cache
bytes remain exact until Start fresh. Retry succeeds after removing the denial,
with focus at retry-save. Reload removes every document-only injection and
restores the original code/labels. These are fault-path checks, not evidence
that the user's browser actually denied permission or that a second tab raced.

Back from repair returns to learn-to-practice at scroll y=236 with value eleven.
Forward opens repair. Reload preserves the URL screen, cached value/rule/theme
and case state, but starts at y=0 with BODY focus. Per-view focus/scroll memory,
reference pin state, selection, copy feedback and preview gestures are temporary.
Representative body/quiet/code text contrast ratios are 12.91/5.37/10.56 in light
and 13.92/8.47/15.47 in dark. This sampling is not an accessibility certification.

Run `node prototypes/ui-character-20261001/evidence/focused-checks.mjs` from the
repository root. It executes the actual gesture/cache/copy functions with
controlled doubles and checks intent, off-center mapping, release bounds,
Escape/cancel/lost-capture/blur/resize/observer rollback, non-primary pointer
isolation, preview preservation, duplicate saves, denied read/write, retry focus,
stale/future/corrupt cache preservation, exact copy, pending duplicate activation,
failure, empty content and copy focus. It also checks unique IDs, local control
and screen links, original code equivalence, no remote assets and JS syntax.
All assertions pass. Browser console reports no errors or warnings.

Before captures: evidence/interaction-before-learn.jpg and
evidence/interaction-before-repair.jpg. Final representative captures:
evidence/interaction-reference-desktop.jpg, evidence/interaction-copy-desktop.jpg,
evidence/interaction-reference-320.jpg and evidence/interaction-code-320.jpg.
All four final captures were visually inspected. Other interaction-prefixed
captures record narrow input, denial, future cache, retry focus and empty/long
content states; earlier direct-marker/craft images remain historical.

Ranked native opportunities refine the existing D1-D5 route, not a new ledger:

| Rank/code | Existing seam and concrete next gate |
| --- | --- |
| 1 / D1 | surfaces/lesson.py:lesson_page and the progressive reader: put the concept before secondary controls. Verify the first viewport on the current synthetic native unit, preserving released-content boundaries and continuous mode. |
| 2 / D3 | surfaces/lesson.py:_code_block, existing static pre/code and runnable textarea paths: add exact-source selection/copy only to appropriate public examples. Gate denial, indentation, keyboard scroll and session/editor focus. Coordinate with the current coding owner before editing its protected source. |
| 3 / D4 | surfaces/quiz_page.py:renderTimeline and sibling tentative-state renderers already have runtime-backed commit and revert controls. Prototype direct manipulation in one representative visual treatment, using its existing commit authority and proving rollback on every interruption. The specimen's local cache cannot substitute for that runtime protocol. |
| 4 / D2 | surfaces/lesson.py:gloss_css, _gloss_trigger_html and GLOSS_HOVER_JS already own native terms/popovers and the static glossary. Apply the bounded keyboard pin/close/return and viewport tasks there; preserve the existing accessible-name/disclosure contract. Shared roles remain in presentation.py and theme.py. |
| 5 / D5 | Course/concept/repair/reference/return in the eventual native candidate: verify focus, draft, reload, failure and released feedback first, then separately review the built/installed candidate and obtain direct human visual/teaching acceptance. |

Physical touch, browser-native zoom, screen-reader usability, human preference
and learning effectiveness were not tested. 640px is a reflow check, not zoom
proof. Blur/cancel/lost-capture use the actual functions under controlled doubles;
the browser independently exercises Escape and resize. No installed-app result
is claimed. No commit, push, app build/install, external message or new chat.

Read scope: AGENTS, EXEC-CONTEXT, the bounded workflow/contract/UI/problem owner
sections and the full small baseline specimen. Native lesson glossary/code,
quiz timeline, shelf drag and palette/day copy seams were sampled symbol-first;
none were edited. Runtime modules were not read. The coding/reading source,
fixtures, other prototypes, STATE and IDEA-LEDGER retain their other writers.

Operational finding: the browser tool's clipboard mirror did not match a page
write. Same-page clipboard comparison immediately after copying the synthetic
source did match. Keep that proof distinct from the mirror and never probe
private prior clipboard content. Hover dismissal needs a condition-based wait
for the delayed close, not an immediate post-move snapshot.

Operation journal: expected index SHA-256
db447dd3225908175caa05005a1f075da7ebaf177a880dc43071fd0f70f464e9;
final index SHA-256 c1b11518d944f8f0f1d0ae503901e8d25f1a5f61de556edd9ea53e2b87dde374. Initial source publication compared the released
base and used atomic replacement. README append compares expected SHA-256
0ab51d79201df0151133a1417ec72c13f948ca88a915b1fc86610338374534b1 and publishes
atomically. Recovery source is evidence/before-interaction-pass.html; the previous
README is evidence/before-interaction-readme.md. Restore only matching owned
bytes, or remove only this dated addition, preserving later work and history.
Disposable cache recovery stays inside this specimen origin. No remote egress,
accepted course/evidence mutation or production authority change occurred.

Final gates: focused-checks.mjs and every executed quick source-only preflight
gate pass. Preflight executes lint, broken fixture, bank guard, skill mirrors,
README commands, schema parse, vendored pin, path-leak and summary rules.
Sample build, full Python suite, clean-tree gate and full JS suite are skipped.
Pinned optional-dependency setup and runtime schema-output validation remain
CI-only. No failed gate remains in this bounded pass. git diff --check passes.
