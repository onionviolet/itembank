# Source-search improvement, October 5

Status: completed bounded source delivery after reproduction, implementation,
browser critique and recovery refinement. Source is uncommitted; installed and
human acceptance remain separate. HEAD is 28bf561, with the inherited dirty
checkout preserved. This record owns this packet only; the recurring Product
GM coordinator retains its existing next packet and aggregate gates.

## Request and scope

> iterative in depth improvement of this?

The user clarified: "The itembank app". This packet improves the complete
course-source search -> exact preview -> return -> changed-source recovery job.
It follows the current visual-experience direction and source-to-course contract.
Owned source: [course_source_search.py](../../surfaces/course_source_search.py)
and the research form/preview seams in
[research_context.py](../../surfaces/research_context.py). The new regression is
[source_search_continuity_roundtrip.py](../../tests/source_search_continuity_roundtrip.py).
Existing source admission, runtime assessment, notes and inclusion owners retain
their authority. Inputs are disposable synthetic registered sources.

## Observed defects and released behavior

| Code | Reproduction | Released behavior |
| --- | --- | --- |
| F1 | At 320 pixels, match 54 opened at x=3632 inside a horizontal passage scroll box. | The passage wraps; native fragment navigation focuses and exposes the exact original Unicode occurrence. The return control sits beside the preview. |
| F2 | Returning to page two put match 54 at y=8580, far below the viewport. | A revision/locator/range anchor returns to that result, with visible numbering, keyboard focus and a distinct returned-occurrence label. |
| F3 | The 768-pixel preview expanded to 839 pixels because of the native passage dropdown. Research buttons and selectors also used undersized default controls. | Research forms constrain selectors to their container and use 44-pixel buttons/selectors and clickable confirmation labels. |
| F4 | A disappeared exact occurrence needed a useful return destination and explicit recovery. | Fresh search rechecks rights/revisions. A missing occurrence releases no old snippet, keeps query/mode/page and offers explicit same-page retry or query editing. Restored rights allow that explicit retry to reach the original occurrence. |

The optional return_match field is a validated presentation hint. Its value does
not admit source content, change inclusion, retry automatically or mutate any
learner file. Forged/malformed hints and duplicate form values are exercised.
Source ordering, Unicode offsets, rights checks and search bounds retain their
existing owners. Ordinary exact previews also retain a usable static form.

## Verification and limits

Seven scoped source suites pass: source_search_continuity (3 tests),
course_source_search (11), product_gm_parity_search (8),
course_source_search_native (4), selected_context_search (7),
a5_research_context and a5_served_integration. The new gate also verifies
native server restart and unchanged course/research files.

Eight new installed-Chrome journeys pass at 1280, 768, 390 and 320 pixels,
with scripts enabled and disabled. They exercise keyboard-only page-two match
54 -> exact Unicode preview -> exact result return -> reload -> quote-rights
refusal -> restored-rights explicit retry. Final assertions inspect both axes,
focus, page width, 44-pixel controls, numbered accessible descriptions and
unchanged durable search state. Six existing paged-search browser journeys
also pass. Final narrow preview/return/recovery screenshots were inspected.

The quick source-only preflight exits 0, with every executed gate passing.
App/sample builds, aggregate Python/JS and clean-tree gates are intentionally
unrun in that mode. Scoped diff whitespace validation passes. This packet
does not replace earlier aggregate failures or certify a release, human
accessibility, learning efficacy or installed behavior.

Retained failed attempts: the standalone search-panel return control was
initially omitted, caught by its existing unit test and restored through a
compatible optional presentation argument. The first browser matrix failed
on the tablet dropdown, then passed after its repair. Before/failed/final
receipts are local under .reasonix/in-depth-improvement-20261005; the initial
probe's vertical-only visibility flag was insufficient, so the final gate
checks horizontal and vertical coordinates explicitly.

Read scope: current AGENTS, workflow, execution context, STATE, coordination,
relevant visual vision and UI/contract sections, and source/test symbol windows.
The complete vision/history and large parser/runtime modules were not read.

## Recovery

The ignored packet directory retains before-images as .py.txt, expected and
released SHA-256 values, an append-only source publication journal, screenshots
and the fast-gate log. Writes checked their bases, validated syntax, flushed
temporary files and published them atomically. Reverse only this packet's
matching source hunks and remove its distinctly named test/record. Check for
later writer changes first; preserve all earlier UI/parity work and scheduling.
No real course or learner record requires restoration.
