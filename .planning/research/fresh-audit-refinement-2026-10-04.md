# Fresh source and learner-flow audit, October 4

Status: five findings repaired in source. The combined source-only gate remains
failed on two LAN-dependent scripts and the inherited dirty-tree gate. This is
a reviewable refinement pass, not an exhaustive semantic audit or a release.

## Request and boundaries

> Audit and refine everything from scratch? Expand as you go?

The request began October 3 and continued after local midnight on October 4.
Interpretation: start from the current contracts and implementation, verify
existing work, repair concrete defects, and expand into useful adjacent seams.
The source-to-course contract, existing runtime authority and unanswered exact
format decisions remain binding. No new assessment grammar, adapter operation,
rights grant, accepted learner artifact, Git action or installation was inferred.

The [state owner](../STATE.md), [workflow](../AGENT-WORKFLOW.md),
[product contract](../SOURCE-TO-COURSE.md), and all 27 rows in the
[capability register](../FEATURE-INVENTORY.md) supplied the live starting point.
The September 30 visual priority and personality/composition interpretations in
[USER-VISION](../USER-VISION.md) were sampled. Older quotations, all historical
unnumbered audits, and every line of large modules were not reread. The
[UI goal owner](ui-goal-review-2026-09-29.md) still owns broader visual direction.

Read/write scope was this repository and its ignored local receipt directory.
Only synthetic fixtures and disposable native/browser workspaces were used.
No private course, live provider, external donor refresh, release or account
operation was performed. The existing dirty source was retained.

## Coverage and method

| Area | Fresh evidence | Limit |
| --- | --- | --- |
| Model, runtime and evidence authority | Existing source suites, targeted draft-revision admission, and exact submitted-text boundaries. | Symbol windows and regression behavior, not every branch inspected manually. |
| Course, sources and guidance | Capability census, current contract, native Learn/Sources inspection, and read-only source activity tests. | Does not certify all 27 capabilities or course-content fidelity. |
| Reading and source search | Exact duplicate-occurrence tests, escaped Unicode excerpts, query return, and direct browser inspection. | Local literal retrieval remains bounded; no semantic retrieval or new approved roots. |
| Learner drafts and review | Two reproduced bank-revision races and no-write refusal tests; existing draft/submit/review suites. | Historical rubric/origin-note provenance remains its existing pending decision. |
| Recovery and agent jobs | Current restore/help owners and their existing source suites were sampled. | No populated-root in-place merge, source-question contract promotion or power-loss certification. |
| Day controls | Reproduced JavaScript parse failure, native save/refresh/tick/reload, and five new behavioral JS cases. | Synthetic local browser use does not certify touch or screen-reader acceptance. |
| Maintenance and portability | AST parsing of 107 production/tool Python files, syntax checks of 16 static JS constants, and inline file-handle census. | Dynamic scripts and whole-module semantics need their existing tests; optional integrations stay separate. |
| Delivery | One combined source-only preflight plus necessary focused checks after the late day-control repair. | Three app-build scripts, sample build, CI-only gates, installed app and human acceptance remain unverified. |

## Findings and source repairs

| ID | Severity | Observed problem | Repair and evidence |
| --- | --- | --- | --- |
| F1 | Medium | A first draft save could silently adopt a question changed between form validation and save. A separate race could hash old bytes while parsing new question bytes. | `surfaces/learner_artifacts.py` now checks the parsed bank against its opening fingerprint and keeps the save pinned to the form's admitted revision. Both regressions failed before repair and now refuse without creating notes. |
| F2 | Medium | Sources rendered assigned readings once for the source and again for each objective. Multiple activity headings and contradictory empty messages followed. | `surfaces/course_workbench.py` now gathers each source's readings and exact linked bank activities into one group. The reproduced duplicate-reading assertion now passes with unchanged durable files. |
| F3 | Low | Inline file reads/writes relied on garbage collection for closure. The lesson parser emitted ResourceWarning during the source-flow check. | 55 operations across 23 files now use context managers, preserving modes, encoding, newline behavior and stdin ownership. A retained-handle parser regression proves closure before return. Existing suites validate behavior. |
| F4 | High | The shipped day script contained a literal newline inside a regex. After that repair, browser use exposed a missing Edit plan button, mismatched tick selector, global `window.status` collision, unrelated button/change actions, a saved draft blocking its own reload, and silent failed responses. | `surfaces/day.py` now parses, exposes Edit plan, records actual checked lanes, isolates editor status and notes-file controls, removes the navigation guard after a save, and retains drafts with visible recovery on interrupted/unreadable responses. Five JS behavior cases and actual native save/tick/reload pass. |
| F5 | Low | Source result excerpts did not emphasize the matched occurrence; repeated controls lacked occurrence descriptions. | `surfaces/course_source_search.py` highlights only the exact Unicode occurrence, escapes source text, describes each control with source/location, and moves detailed ranges under Exact location. The same POST owners and exact-query return remain. Browser reflow at 320 px measures 320 px content width, a 44 px query input and 46 px result buttons. |

F1-F5 are source repairs. F5 is an incremental display improvement and does not
settle the user's broader composition or advanced-interaction preferences.

## Verification

Receipts live under `.reasonix/fresh-audit-20261003/`; that directory retains its
start date. The original failed runs remain unchanged.

| Gate | Result |
| --- | --- |
| Initial `preflight.py --quick --source-only` | Every executed fast gate passed. Source/bank guard reported zero offending files. |
| New `tests/audit_refinement_roundtrip.py` | Six cases pass: two draft races, source grouping, parser closure, shipped day syntax, and exact escaped search emphasis. Original failing receipts are retained. |
| New `tests/js/day_workspace.test.mjs` | Five behavior cases pass: editor entry/discard, actual lane ticks, bounded save, successful-save navigation recovery, and interrupted/unreadable response recovery. |
| Combined `preflight.py --source-only` | 213 discovered Python scripts; 210 executed and 208 passed. `daemon_roundtrip.py` and its delegated run in `model_phase_roundtrip.py` both failed at the LAN preview timeout. JS passed. Dirty-tree gate failed. Three app-build scripts and the sample build were explicitly deferred. |
| Late day changes | Full preflight's JS leg ran after the final day repair. `day_edit_roundtrip.py` and `day_roundtrip.py` pass focused reruns at that final revision. No second full suite was started. |
| Native browser | Source search opens the second exact duplicate and returns to its query. The day editor saves a synthetic change and refreshes; three checked floor lanes survive reload and expose three live events. |
| Static syntax | 107 Python files parse. Sixteen static JS constants parse; the final day constant is additionally checked by the focused regression. |
| Diff | `git diff --check` passes. Source changes are uncommitted. |

The network probe serves one fixed synthetic response on all interfaces.
Loopback returns 200, while this host's advertised LAN address times out.
`network-probe.json` records both observations. This supports a host-network
limitation; it does not prove LAN behavior on a reachable interface. The failed
daemon scripts stop there, so later assertions in those executions are unrun.
No network protection, test expectation or application admission rule was weakened.

Screenshots: `day-saved.jpg`, `search-results.jpg`, and
`search-results-320.jpg` in the receipt directory. These are synthetic browser
evidence, not installed-app or human accessibility approval.

## Remaining routes

| ID | Disposition and next evidence |
| --- | --- |
| R1 | Deferred on host network reachability. Run the two failed scripts on a reachable advertised interface, then inspect the existing LAN read-only and mutation-refusal assertions. Preserve this failed aggregate run. |
| R2 | Deferred on the existing direct decisions. Q1 domains, Q2 anchors, Q3 graph/transcript, Q4 source-question adapter and provenance/root-carry proposals retain their exact existing specimens in the October 3 owners. This broad request does not answer them. |
| R3 | Prototype/registered breadth remains in existing owners. Richer source/reader composition, objective-specific interactions, media and code execution still require their named evidence. Do not replace those routes with another feature inventory. |
| R4 | Deferred delivery/acceptance. Fresh package, installed app, representative human accessibility and learning acceptance remain separate from this source pass. |

## Recovery and handoff

`baseline-files.json`, `baseline-status.txt` and `baseline-diff.patch` capture
the inherited checkout. `.txt` before-images preserve edited files without
introducing duplicate executable writers into authority scans. `task-delta.patch`
contains only this pass's changes relative to those before-images, including its
new records/tests. Check that patch against the current files before applying
its reverse; a later conflicting edit must be reconciled, never overwritten by
a whole-file restore. `final-files.json` pins the reviewed inputs.

Large modules including `model.py`, `runtime.py`, `surfaces/day.py`,
`surfaces/course_workbench.py`, `surfaces/lesson.py` and `surfaces/daemon.py`
were read in symbol windows. Automated syntax/resource scans had broader file
coverage, but they are not substitutes for a manual whole-module review.
This pass ends with five repaired findings and named remaining evidence, not a
claim that every historical proposal or product path is complete.
