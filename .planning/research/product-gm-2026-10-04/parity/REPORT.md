# Feature parity implementation report, October 4

STATUS: source released for integration

The frozen source programme is implemented: F1 registered-course source search
pages/Unicode matching and F2 exact changed-source reading/treatment impact.
Necessary review and visual repairs are complete. F1's required source/native
and browser gates pass. F2's feature/revision/no-write and browser inspection
gates pass; explicit source-origin return remains the integration request below.
The complete task/status map is [MATRIX](MATRIX.md). Current native baseline
receipts are in [BASELINE-VERIFICATION](BASELINE-VERIFICATION.md).
The 604 historical findings are source observations mapped into 27 capability
groups, not missing features or a full-parity denominator.

## Integration requests and reservations

F1 needs no shared route change. It extends research form handling
in the reserved `research_context` module. F2 extends the existing Sources route
projection in reserved workbench/context_view modules. Integration owns final
broad gates, packaging registration checks and source composition.

I1, source-review origin return: the new F2 impact links correctly open exact
reading, lesson, map and runtime tasks, but those tasks' explicit back controls
still lead to their standard Learn/overview origin. Keep F2 continuity partial
until a shared source-origin return gate passes. Proposed additive query field:
`return_source=<source_object_id>`, emitted only from impact task links. Resolve
it against the admitted course source list, deriving the current
`/course/<id>/sources?source=<index>#source-<index>` link, never accepting a URL.
Duplicate, unknown, cross-course or removed IDs retain the existing fallback.
Readings need daemon routing plus the UI owner's reading back-control support;
lesson/practice need the shared origin state/return projection. Map can be
handled in this lane's context helper once the common seam is settled. Source
review itself is read-only. Gate: changed-source Sources -> exact assigned
reading/lesson/map -> explicit source return after reload/restart at 320px and
script-free, with unchanged durable files and no changed-source text release.
This is an integration request, not a silent claim of implemented continuity.

Parity I1 caller seam is now implemented against integration I2.2: actual
impacted map/reading/lesson/practice/formal-test links emit exactly one
`return_source` carrying the selected source's stable ID. Existing course,
occurrence, item/mode and fragment fields remain intact. The final parity
native test follows these emitted links and asserts the source ID on every
impact-task link. Shared fallback/admission and explicit back-control gates
remain with integration/UI until their linked current receipts pass.

All assignment-reserved source paths are released, including changed
`surfaces/course_source_search.py`, `surfaces/research_context.py`,
`surfaces/course_workbench.py`, `surfaces/course_context_view.py`, and untouched
`surfaces/learner_artifacts.py`, `surfaces/agent_operation.py`,
`surfaces/context_help.py`, `surfaces/course_ops.py`,
`surfaces/restore_workspace.py`, `notes.py`, `discovery.py`, `workspace.py`,
`retention.py`, `progress_claims.py`. The three new parity tests below and this
directory are released too. No worker or test process remains active after the
final receipts. Integration may apply source-origin return and run the one final
combined source gate against these released bytes, preserving inherited work.

## Delivered task changes

F1 previously stopped at the first 32 matches and required exact capitalization.
Search now serves up to 32 results per page, bounded by offset 4096, the existing
64-source/128-passage/8 MiB corpus and source-size limits. Optional Unicode case
folding maps matches back to original character ranges, including expanded
characters. Default direct calls remain case-sensitive. Preview and return
carry the exact query, mode and page through normal script-free forms; every
page re-admits revisions, rights and accepted locators. Source scope and private
notes are unchanged.

Independent [SEARCH-REVIEW](SEARCH-REVIEW.md) reproduced two material defects.
R1: a late change to an early source consumed bounded page slots and falsely
ended later-source results. The repaired scan withholds that unreliable page
and offers an explicit same-page retry instead of releasing sparse results.
R2: a rejected partial Unicode expansion skipped a later valid whole-character
match (`sß` versus `ss`). Rejected candidates now advance one folded position;
valid matches keep existing non-overlap semantics. Both exact repros pass at
the reviewed repaired pins, with new native/regression coverage. Later panel
recovery changes preserve those search/helper branches, and their regression
gates pass again at the final hashes below.

R3: a native page-two preview refused after quote rights changed lost its exact
return action. The reproduced failed gate is retained. The search panel now
recovers the query, mode and validated offset from retained fields, and offers
the same-page return even on refusal. The new native gate verifies 400, no
released snippet, exact return fields, rights recheck and no durable mutation.

F2 previously named only affected objectives. It now joins exact accepted
source IDs, active binding revisions and validated current reading occurrence
revisions. Superseded history remains recorded and counted separately; reading
declarations stay on their original revisions. Links open existing admitted
reading, lesson and runtime tasks. Missing/unsupported/ambiguous routes and
restrictive rights remain explicit; changed source text is withheld. Visual
review moved long revision IDs into expandable details, and repaired an exact
direct-reading binding that was incorrectly labeled unavailable. Task links and
assigned ranges now precede secondary metadata. Explicit source return is I1.

## Exact checks and current source pins

| Exact command | Actual result |
| --- | --- |
| `python3 tests/product_gm_parity_search_roundtrip.py` | 8 cases pass: three-page original Unicode ranges/no writes, rights/stale page refusal, invalid forms/forged preview, omitted-source page slots, final-admission explicit retry, partial-expansion native highlight, native page/preview/return/fresh-daemon recovery and refused-preview exact page/mode recovery. |
| `python3 tests/course_source_search_roundtrip.py` | 11 existing cases pass, including default exact-case compatibility, duplicate locators, corpus bounds, private/assessment exclusion and concurrent refusal. |
| `python3 tests/course_source_search_native_roundtrip.py` | 4 actual native/fresh-daemon cases pass. |
| `python3 tests/selected_context_search_roundtrip.py` | 7 existing cases pass after the shared literal-range helper repair. |
| `python3 tests/a5_research_context_roundtrip.py` | Exact occurrence, explicit selection, Link/Copy, cancel, no assessment disclosure, note restore/named scope loss/undo pass. |
| `python3 tests/product_gm_parity_search_browser_roundtrip.py --browser .reasonix/product-gm-20261004/parity-search/browser-release` | Six installed-Chrome keyboard/page/preview/return/reload journeys pass at 1280/390/320, scripts on/off; no overflow or durable mutation. Dark at 390 and reduced motion configured. The matching earlier 320px layout screenshot was inspected; the recovery-only change adds no markup on this success path. |
| `python3 tests/product_gm_parity_source_impact_roundtrip.py` | Exact current reading/treatment identity, superseded history, native source/task opening/restart, restrictive rights/missing source and unchanged durable files pass after final visual/link repairs. |
| `python3 tests/product_gm_parity_source_impact_roundtrip.py --browser .reasonix/product-gm-20261004/parity-impact/browser-release` | Four Chrome task inspection/browser-history-return/reload journeys pass at 1280/390/320, with script-free 320. Emitted links carry exact source origin. No overflow or changed source disclosure; 320px final layout screenshot inspected. Shared explicit source-back control remains I1. |
| `python3 tests/course_context_journey_roundtrip.py` | Existing exact prerequisite/source return, restart and changed-source/no-write gates pass after final F2 changes. |
| `python3 tests/course_workbench_roundtrip.py` | Existing native navigation, proposal review, accept/undo/conflict/report-only gates pass after final F2 changes. |
| `python3 tests/course_guidance_journey_roundtrip.py` | Existing truthful history/pending/blind boundaries, detour/reload/restart/retraction pass; expected deliberately damaged-evidence warnings retained. |
| `python3 tests/backlog_course_roundtrip.py` | 4 cases pass after final F2 changes: current local inventory/source impact, prerequisite/context/native no-write gates. |
| `python3 tests/course_guidance_engine_roundtrip.py` | 14 cases pass, including due ordering, admitted sources, pending precedence, latest correction and read-only evidence joins. Later F2 edits only change task-link filtering/rendering and are covered above. |

The five inherited native jobs and the separate 15-case native restore gate
pass at their recorded hashes in BASELINE-VERIFICATION. Restore's browser-named
script without flags is preview-only; the added default native restore suite
actually exercises consent/copy/exact reopen, daemon restart, a fresh destination
process and restrictive rights. The due helper's HTTPError cleanup warning is
retained, not a production assertion failure. No broad preflight was run by this
lane; integration is its sole owner.

Final `python3 -m py_compile` on the four changed source modules and three new
tests exits 0. Scoped `git diff --check` exits 0. The new parity reports/tests
contain no em dash matches. No equivalent full suite was rerun.

| Released changed path | SHA-256 |
| --- | --- |
| `surfaces/course_source_search.py` | `6c978964a6d5a349175ffac6c9fb3b808e4b26d6c4ed5a397a56bb4396d7556a` |
| `surfaces/research_context.py` | `caac56e280bceb80cbce4b538d03725efd573c71714b3ed30d93fd00526a49af` |
| `surfaces/course_workbench.py` | `85c741a627854fe24e18043ae5c6abffa0991727842c4eab678985ff7c60220a` |
| `surfaces/course_context_view.py` | `e4528cf7e8b78a4dfeb512d183172b728a7b0a33bb577c8e3c2cb76edf0549d1` |
| `tests/product_gm_parity_search_roundtrip.py` | `4349c6a8e0383f4c904f51c54682e34b2b4aa9e47d9b27665e3d437e5fee6bc1` |
| `tests/product_gm_parity_search_browser_roundtrip.py` | `4660e88bb1a36f73ce445540fb916528850285c6e469a384fae890b0afe07170` |
| `tests/product_gm_parity_source_impact_roundtrip.py` | `978cc5cc2faaf0e00ad5fbc0d2c9eaa9b3e54da75baa309a53bcd0e42a750fe1` |

Starting source-search and research-context before-image hashes were
`6f6fbb6c21b44a022c77fdac6200de9f9c436d8a63224f4667d0734ecb25ffdf`
and `504d12c3e95683e51ab2560cfb38b62348c23f71d16fc3098a1a84132b56b4b6`.
Their ignored before-images are under parity-search/before. Workbench/context
before-images and original worker pins are in SOURCE-IMPACT. The parent's later
visual/link repairs supersede that worker's released workbench/test pins, with
the current hashes and reruns recorded here. Shared daemon and UI files may
change concurrently; their baseline receipts do not certify later bytes.

## Process findings and limits

The first new search test run failed because a fixture changed the raw input
file rather than the imported registered source, and because a range assertion
ignored earlier sources. Those fixture mistakes were corrected against exact
registered identity. The added Unicode edge test initially landed after 70
earlier valid matches and needed its actual third result page. These failed
runs remain failures; no runtime rule was weakened to make them pass.

Reusable findings: an early final-admission failure can invalidate pagination
even when late-source snippets are safe; a bounded search must refill or expose
an explicit retry. Unicode folded offsets need rejected-candidate advancement
tests as well as positive expanded-character tests. A script name containing
`browser` does not establish that its default entrypoint runs browser, copy or
reopen assertions. Recovery source snapshots use `.py.txt`, preserving the
existing authority scan's single-writer interpretation.

## Authority and limits

Accepted source IDs/fingerprints/locators, course graph and reading revisions
remain canonical. Search and impact views are local read-only projections.
Sources require current admission and read/quote rights before snippet release.
Private context, notes, assessments and evidence are not changed by these views.
No new scorer, settled prose mark, format promotion or access policy is selected.
Packaged, installed, live-provider, human accessibility and learning equivalence
remain separate from source and synthetic native checks.

Recovery: reverse only context-checked owned hunks against the ignored
before-images, preserving inherited and later changes. No learner-data undo is
needed for the read-only slices. No commit, push, package, installation,
publication, scheduling, paid provider call, donor execution or private learner
mutation occurred. Broad and installed/packaged/human/learning gates remain
separate. Relevant large modules and vision/contract entries were sampled by
symbols and task sections, not audited whole. Final next action belongs to
integration: implement parity I1 with UI, consume released hashes, run the one
combined gate and update the remaining partial comparison states from evidence.
