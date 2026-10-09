# Cross-repo continuation, October 3

Status: registered-course source search implemented and native-tested. Exact
Q1-Q4 format choices remain pending. Source is uncommitted; app delivery and
human acceptance remain separate.

## Scope and authority

Direct user instruction: "implement accordingly" after the F1-F5 remaining-work
review. Existing dirty source is the baseline and must remain preserved. No
commit, push, app installation, live provider request or learner-data access is
included. Native tests use fictional temporary courses and loopback services.

Q1/Q2/Q4 exact domain, anchor and source-question adapter decisions, and Q3's
authored versus accepted-reading transcript choice, were requested directly.
Those format promotions remain pending until answered. The existing reviewed
specimens retain authority; this record does not replace them.

Independent ready work: broaden local literal retrieval from saved research
context to registered course sources. Reuse the source/locator, course,
assessment-exclusion and research-preview owners. Search stays read-only and
does not include private notes, unregistered files, change saved model context,
invoke a provider or create response/reading evidence. Show bounded coverage,
unavailable/rights/assessment exclusions, exact match ranges and explicit return
to the same query. No new durable format or root grant is added.

Owned source: new `surfaces/course_source_search.py`, bounded research panel
hooks and dedicated source/native tests. Integration followed the prior writer's
recorded final source checks and preserves its Unicode selected-context matching,
pagination and control styles. A typed course refusal now leaves the search page
usable when the source picker cannot admit an edited sidecar. Source help and all
other inherited work remain preserved.

The predecessor's single full source-only run exercised 206 Python scripts and
JS; six failed suites passed scoped repairs. Its original failed run remains
failed. This continuation ran scoped tests, required quick gates and one
completed combined source-only run against its frozen search source.
The inherited dirty tree cannot satisfy a clean checkout assertion.

## Delivered scope

The existing Sources to Research entry now also supports deliberate search of
registered course sources without a saved model context. The first version is
literal and case-sensitive, bounded to 64 sources, 128 passages, 8 MiB of source
bytes, 2 MiB per source/sidecar and 32 hits. Coverage limits and unavailable,
rights, assessment or revision omissions are visible rather than reported as a
complete zero-result search. This does not implement every approved root,
semantic retrieval, remote lookup or extraction-fidelity measurement.

Each hit retains accepted source identity/fingerprint, exact locator, original
code-point range and location label. Native preview re-admits the source and
quote rights, highlights the exact occurrence and provides a query-preserving
return. Search and preview change no course, note, research selection, sitting
or evidence bytes. Private notes, unregistered files and assessment content do
not become the corpus. Returned sources are rechecked after the scan; changed
or unaccepted locator bytes cannot redirect duplicate quotes.

The controls reuse the existing context-search presentation, including 44-pixel
input/button sizing and keyboard focus. Plain forms work without scripts. The
static source files retain the underlying study content; no new durable format,
source import, model operation or rights grant was introduced.

The combined run also exposed truncated JS diagnostics: preflight printed only
the first 20 output lines, which hid the actual failed case. Its diagnostics now
retain complete Python and JS suite failures. A regression drives the real
preflight main function with a late failure after 30 passing lines and verifies
that the failure and traceback remain visible with a failing exit status.

## Executed evidence and limits

Local receipts are in `.reasonix/cross-repo-continuation-20261003/`.

| Check | Result |
| --- | --- |
| `tests/course_source_search_roundtrip.py` | 11 pass: exact duplicate/Unicode positions, unchanged saved context/private notes, assessment/unregistered exclusion, read/quote refusal, stale/unsafe/missing sources, accepted locator provenance, late source/course changes, bounded reads and fresh-process reopen. |
| `tests/course_source_search_native_roundtrip.py` | Four real HTTP/fresh-daemon checks pass: search, highlighted L4 preview, retained query/range refusal, stale-sidecar recovery and no durable changes. |
| Native Chrome at 1280/390/320 with scripts enabled and disabled | Six keyboard search/preview/return journeys pass. Controls are at least 44 pixels high; narrow scripted views have no horizontal overflow. Screenshots and `browser/observations.json` are retained. |
| Existing research integration | Seven selected-context tests, eight context-help tests and the A5 research/context/transport checks pass. Concurrent Unicode matching and pagination remain preserved. |
| Full source-only preflight | All 209 executed Python scripts pass out of 212 discovered; the three existing app-build checks stay deferred. The original run fails on inherited dirty state and JS. |
| Isolated full JS rerun | 132 tests pass. No JS implementation was changed. The original failure could not be identified from the truncated output and is not called repaired or relabeled as passed. |
| Preflight diagnostic regression and final quick source-only gates | Pass after the diagnostics-only repair. No equivalent Python suite was repeated for that logging change. |
| Source integrity and whitespace | The four search source/test files match the frozen hashes throughout the combined run; `git diff --check` passes. The whole-tree manifest detected concurrent additions to USER-VISION-INBOX and the UI goal review. Those prose changes are named limits, not runtime-source edits or format acceptance. |

The first browser run used an incorrect URL glob requiring a slash before the
fragment. The actual route navigated correctly; the harness glob was corrected.
The first full preflight was interrupted after screenshot review found small
default controls, then the corrected presentation was frozen for the completed
run. Both earlier logs are retained. The failed JS receipt stays failed; the
later isolated success does not establish its original cause.

Large course/source/journal/daemon authorities were sampled by relevant symbols,
not audited whole. No live provider or real learner content was used. Human
touch, screen-reader, learning quality, installed delivery, full root retrieval,
large-corpus latency and the pending exact formats remain separate gates.

## Recovery and continuation

Reverse only this task's research-panel hooks and remove its new search module
and two tests after checking later dependencies. Preserve the earlier reader,
selected-context, due-practice, artifact and restore work. The preflight change
is a separate bounded diagnostics hunk with its existing test extension.
Before-images, source pins and failed/passed receipts remain in the ignored
evidence folder. No accepted learner data needs undo because these operations
are read-only.

Reusable operational finding: diagnostic preservation must include the JS gate,
whose passing-case prefix can otherwise hide the failing case. Recovery copies
of Python source use `.py.txt`, preventing the authority scan from treating
backups as second production writers.

Next action: answer the already presented Q1/Q2/Q4 specimens and Q3 transcript
choice, then promote the selected contracts sequentially through their existing
owners. Generic implementation authorization has not supplied those answers.
