# Native interaction craft, October 1

Status: native source implemented and checked in a disposable loopback preview.
The user authorized parallel implementation after the specimen's A1-A5 pass.
The prototype remains frozen at its released final bytes. No app build,
installation, commit, push, external message or new chat occurred.

## Scope and observed outcomes

| Code | Native work and evidence |
| --- | --- |
| D1 | Guided reading puts the current concept ahead of secondary reading controls. The first concept starts at y=303.4 in a 1030x571 viewport; the historical native capture put it at y=606.8. About this reading and Reading options retain metadata and tools. Explicit Next reveals and scrolls to the new stage while retaining focus. Continuous reading remains available. |
| D2 | Native glossary popovers retain the static appendix and runtime disclosure gate. Fine-pointer hover, focus, deliberate pin, keyboard entry, Close and Escape use the same term origin. Closing now suppresses synchronous focus restoration across the entire native hide operation. Widget opened and closed at 390x844 with return focus and no console exception. Its panel fit inside x=18.8 to 360.8 and y=401.2 to 657.2. |
| D3 | Already-rendered public inert code has exact-source Select and Copy. Selection focuses the local code region. Copy deduplicates pending requests, retains button focus and distinguishes empty, unavailable, denied and successful states. Runnable editors are unchanged. Exact payload is checked by the focused JS test. The browser showed success, but native clipboard readback timed out, so readback is not verified. |
| D4 | One native [COMPARE:] teaching example has a visible 44px B handle, a retained native range, exact entry and step controls. A 4px threshold and off-center grab offset avoid jumps. Release keeps the hypothetical value; cancellation restores the start. This promotion uses the existing teaching treatment rather than changing tentative assessment renderers or runtime authority. |
| D5 | A real disposable native course links Learn, the objective map, sources, both reading modes and saved practice. Exact course Resume preserves the saved session and B draft. A browser-reproduced header overlap was repaired in shared presentation CSS: after scrolling, the course link now receives its own click rather than the app-logo click. |

## Browser task details

The preview helper uses real course and runtime APIs with synthetic fixtures in
a temporary directory. It does not read learner roots. Confidence stays unknown;
presentation changes do not create mastery, completion or learner evidence.
Source copies use .txt so course scanning does not mistake them for duplicate
assessment banks. Tests also check that course and practice HTML withhold key
labels. The test's answer submission happens only in its disposable test root.
The manually inspected browser sitting retained an unsubmitted draft.

D1: First-screen composition was checked at 1030x571. Next showed the second of
five available stages, with its heading at y=87.9 and focus still on Next. The
button's bottom was y=573.5 in a 571px viewport, so this observation is not a full
focus-visibility certification. Initial render and Restart do not auto-scroll.

D2: Click, ArrowDown, Escape and Close were exercised on Widget in a 390x844
viewport. A real browser exposed a hide/focus reentrancy exception that simple
DOM doubles missed. The repaired test now models synchronous opener focus
restoration during hide. Final browser logs had no errors or warnings.

D3: The short code example fits at 320px: client and scroll width both 267px.
A labeled document-only long-line fault had width 1556px inside the 267px code
region; ArrowRight scrolled it by 40px with zero page overflow. A labeled
clipboard denial showed the manual-selection recovery message. These faults
were removed by reload. The long-line screenshot was taken after selection,
so its visible status says Code selected rather than Copy denied.

D4: At 1030px the track was 870px wide. An off-center 2px movement left B=18
and no preview; a larger move previewed B=22. Escape restored B=18 and cleared
preview. An outside release clamped B=24. At 390px, native ArrowLeft changed
24 to 23 without page overflow. A final actual held-pointer drag previewed 20;
resizing from 1030x571 to 390x844 restored 18 and cleared preview before release.
Focused tests cover blur, cancellation, lost capture, page exit, bounds,
per-instance isolation and final release coordinates.

D5: The course query and anchor were correct before repair. At the scrolled
anchor's center, hit testing reached the overlapping itembank logo. Shared
desktop CSS now keeps one sticky context band for this standalone sitting.
After repair, hit testing and an actual click reached the course overview;
its exact Resume returned to the same saved session with B still checked.
The generic lesson Continue to practice link retains course context but omits
the saved-session identifier. Exact resumption was proved through course Resume.

## Executed checks

| Code | Check and result |
| --- | --- |
| T1 | Lesson, lesson-code and progressive Python roundtrips passed; progressive Python 3/3 and combined progressive/craft JS 6/6 passed. Golden normalization ignores only the exact new presentation controls and pre attributes; teaching and code bytes remain pinned. |
| T2 | Native comparison Python 17/17 and JS 6/6 passed. Existing Python resource/deprecation warnings were observed. |
| T3 | Native journey HTTP roundtrip passed, including course links, lesson modes, saved session, course return after synthetic submission and key withholding. Parent reran it after the final shared-frame repair. |
| T4 | Responsive product Python 5/5 passed. Presentation harness passed in an isolated rerun. Its printed two-heading FAIL is an intentional negative-fixture self-check. An earlier overlapping run did not print the daemon URL before the helper deadline; that startup failure did not recur, and its cause is unconfirmed. |
| T5 | Every executed quick source-only preflight gate passed. Sample build, full Python/JS suites, clean-tree and CI-only output-schema gates were not run. Scoped diff whitespace checks passed. |

Four representative final native screenshots were visually inspected:
[guided](guided-1030.jpg), [comparison](comparison-390.jpg),
[glossary](glossary-390.jpg) and [course return](return-link-1030.jpg).
The intermediate guided capture is not an untouched before image. The
historical native guided capture lives one level above this directory.
Screenshots were checked against their actual viewport dimensions.

## Authority, recovery and remaining gates

The operation journal records the source base revision, final fingerprints,
owned paths, protected paths and additive owner publication. The bounded
tracked-source recovery patch excludes unrelated coding/reading work. Apply
recovery only after checking matching bytes and later edits; never use a broad
checkout or reset. New helper/tests began from absence. Owner appends can be
removed only as the matching dated suffix. No accepted learner files changed.

This pass sampled the relevant renderer and progressive/glossary/comparison
symbols; it did not read the large lesson module whole or audit all runtime
and quiz internals. The existing dirty runtime, schemas, daemon, quiz, reading
desk, session, STATE and IDEA-LEDGER bytes were fingerprint-checked unchanged.

Installed application behavior, physical touch, screen readers, browser-native
zoom, full accessibility review, human visual preference and learning benefit
remain unverified. Focused source and browser checks prepare those gates.

## Dated operational findings

O1: A new IAB tab can reset the browser viewport override. Set the override after
tab creation, then inspect innerWidth and innerHeight before labeling a capture.

O2: A stopped preview can leave an IAB data error page whose enormous URL is
blocked even for close/navigation. Do not work around that block. Use a fresh
tab in the already-selected browser; temporary tabs clean up at turn end.

O3: A child agent's PTY session ID was not addressable in the parent's tool
session. The owning child stopped its preview. The parent owned and stopped
the final preview itself. This is a dated observation, not a universal rule.

O4: Native popover hide can restore focus synchronously. Guard the whole hide,
including focus restoration, against a focus-triggered reopen; an already-open
show guard alone does not cover that sequence.

O5: A correct href does not prove the visible anchor receives a click. For
overlapping sticky layers, compare the rendered anchor center with hit testing
and then exercise the actual navigation. The native clipboard readback timeout
also remains a tool limitation, not evidence that Copy failed.
