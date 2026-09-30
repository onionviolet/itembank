# Remaining UI criteria after the September 30 overhaul

Date: 2026-09-30. Status: independent bounded source/served review.
Owner: original overhaul coordinator, read-only production scope.
Inputs: [overhaul packet](ui-overhaul-2026-09-30.md), V/N/W lane evidence,
and the historical `.reasonix/ui-detail-review-2026-09-19.md` U1-U5 record.
This report is evidence and narrow patch requests, not a second backlog or
authorization to change assessment contracts.

## Result

Two current continuity failures were reproduced on the real daemon with
fictional material. A full-page symbol-reference return preserves sitting
identity but loses the unfinished radio choice and long-question position.
The compact mobile frame resolves the sampled old prompt-placement issue.
Comparison controls still reset on reopen, matching their explicitly temporary
contract rather than establishing a regression. Human acceptance stays open.

All eight production sources and six integration test inputs matched
`.reasonix/ui-overhaul-20260930/final.sha256` at review. This proves the reviewed
bytes match the integrated handoff, not that every UI criterion passes.

## Narrow patch requests

### R1: Preserve unfinished single-choice input during a reference detour

Priority P2. Reproduced at 390px using a disposable `symbols.md` bank derived
from `tests/quiz_symbol_return_roundtrip.py: BANK`. The first stem was extended
with 55 repetitions of fictional text to require scrolling. Select the first
radio with Space, open its symbol's existing full-page `href`, then activate
the definition page's return link. Before leaving, a radio was checked. On
return, no radio was checked. No answer was submitted during this probe.

Source explanation: `surfaces/quiz_page.py` `installDraft` at line 5109 selects
textareas/text inputs, table/matching selects and build selects. Its general
field selector at line 5148 excludes radios and checkboxes. Therefore the
existing draft recovery does not reconstruct a pending single-choice answer.
This probe establishes single-choice loss only; checkbox loss is a source
inference until a separate multi-choice fixture reproduces it.

Requested patch: extend the existing presentation-only draft adapter for native
choice controls, validating stored option identity against the current public
item and response declaration. Restore only unfinished input, never feedback,
correctness, or a submitted response. Clear stale/incompatible drafts visibly;
preserve existing post-submit cleanup. Do not introduce another scorer or
automatically post recovered input. Record the intended same-item/sitting and
revision boundaries rather than changing historical draft semantics silently.

Gate: choose with keyboard, visit the full-page reference and activate Return,
verify the same checked option and exact sitting/item, then reload and verify
the supported draft policy. Repeat with changed public options and unavailable
storage; neither may silently apply an incompatible answer. Assert no response
event until explicit submission. Keep the inline quick lookup working too.

### R2: Restore the question anchor and focus on a contextual return

Priority P2. Same served probe: before leaving, `scrollY=2161` and focus was
the selected INPUT. After the reference return, `scrollY=0` and focus was H1.
The long prompt began at y=133 and its answer area required scrolling again.
This is an explicit return-link failure, not a reproduced browser-Back failure.

Source explanation: the served-baseline initialization at
`surfaces/quiz_page.py:5218-5221` restores supported drafts then focuses the stem
with `preventScroll`, without restoring a saved question-position anchor for
this path. The exact-sitting reference route preserves identity, not viewport
or focus. Reading has a separate revision-aware Resume previous reading
position control; it must not be mistaken for quiz restoration.

Requested patch: add an explicit contextual-return marker and presentation
anchor/focus recovery scoped to the admitted sitting/item and public revision.
Separate contextual return from a fresh launch and deliberate Next. Restore
after layout is ready, or offer an accessible Resume position action if automatic
restoration conflicts with orientation. Do not move focus on ordinary input
updates or reuse stale coordinates after a changed item/layout without fallback.

Gate: at 390px and 320px, leave a lower-page control through its full-page
reference, return and continue from the same occurrence with useful focus.
Check browser Back separately, resized viewport, changed item/revision, and
storage refusal. Runtime cursor/evidence must remain unchanged by navigation.

## U1-U5 reconciliation

| Historical criterion | Current bounded evidence | Remaining disposition |
| --- | --- | --- |
| U1, explainer state through detours | Real `/lesson/comparison` slider changed from 18 to 19 with ArrowRight. Open practice, explicitly reopen lesson: returns to 18. `lesson_interaction.py:67` initializes from the authored default and existing tests forbid storage in the trusted script. The fixture visibly promises temporary state and reset on reopen. | Unresolved experience choice, not a hidden regression. To meet the older detour goal, approve bounded per-tab, revision-scoped exploration continuity, revise the temporary copy/test contract, preserve static meaning and keep this state out of evidence. No broad durable-persistence claim. |
| U2, reading position and focus | Current full-page quiz reference return loses pending single-choice input and viewport/focus as measured above. Existing handoff proves exact sitting/item, which is a different criterion. | R1/R2 reproduced and actionable. Browser Back and changed-revision restoration remain separate checks. |
| U3, activity sooner on phones | In current served quiz at 320px and 390px, substantive stem starts at y=133; document scrollWidth equals viewport width. The intentionally long stem creates vertical reading length, not navigation overhead. | Sampled quiz criterion passes. This does not certify every authoring, format-picker, diagram or help layout. |
| U4, stable course return through feedback | Synthetic course-linked practice shows one visible exact course link before and after incorrect feedback and after correct feedback. Screenshots were inspected. The normal practice probe did not establish a held-feedback pause; explicit reopening after correct submission presented subsequent runtime state. | Link-stability observation passes. A mode explicitly configured to hold feedback still needs an exact course-detour/return check; do not label normal runtime advancement a defect. |
| U5, interruptible help and visible recovery | At 390px, Enter on the symbol anchor opens one native popover; Escape closes it and focus remains an A element. The integrated journey already records injected 503, draft reload and save retry, but those broader checks were not rerun in this review. | Partial independent pass. Exact occurrence focus, physical touch dismissal, overlap at 320px, source-change recovery and screen-reader behavior remain representative gates. |

## Evidence, sampling and recovery

Actual probes used Python Playwright with installed Chrome, the existing
`daemon_roundtrip.start_daemon` helper, local temporary banks and the synthetic
course fixture from `ui_overhaul_journey_roundtrip.fixture`. Each owned daemon
was terminated and each temporary root cleaned. No real learner data was read,
uploaded, overwritten or answered. Fictional runtime attempts were disposable.

The first reference probe used a click intercepted by inline quick lookup, then
mistakenly tried the hidden mobile brand as a return link; that probe timed out.
It is excluded from return evidence. The corrected probe navigated to the real
symbol `href` and clicked its exact quiz-return link, producing the R1/R2 values.
Inline help was then tested separately with Enter/Escape. Keep full-page
references and inline popovers as distinct paths when writing regression tests.

Screenshots under `.reasonix/ui-remaining-20260930/`:
`comparison-return-390.png`, `long-question-reference-return-390.png`,
`feedback-course-return-390.png`, and `held-feedback-course-return-390.png`.
The last filename describes the intended probe; it does not prove a held pause.
The incorrect-feedback screenshot was visually inspected. Terminal measurements
above are the independent behavior evidence; the old integration report remains
the owner of its broader source matrix and tests.

Large modules were sampled at draft/initialization, lesson interaction and
reading-continuity symbols, not read whole. No full preflight or production
source edit was performed. Human visual preference, keyboard task usability,
screen-reader, physical touch and learning-transfer acceptance cannot be inferred
from geometry, screenshot inspection or scripted browser passes. Fresh package
and installed acceptance remain deferred under the existing build hold.

Recovery: remove this report and its disposable screenshots. No shared owner,
source, test, accepted artifact, commit, app build or installation was changed.
Route R1/R2 to the current integrator for a scoped continuity repair; retain U1
as an explicit contract choice and U4/U5 as bounded remaining verification.
