# Open issue repair chain

## Link 1: issue 23

Outcome: repaired the reproduced basename and shared-date shortcuts in
`scripts/vision_audit.py`. Paths resolve exactly against the referencing file's
directory and repository root. Distinct matches are ambiguous. Downstream
verification requires a local inline Markdown link to the exact vision heading.
Title text is only a candidate. Existing report labels and zero exit behavior
remain, with the tightened downstream-count meaning documented in the footer.
The script remains read-only.

Evidence: `tests/vision_audit_roundtrip.py` passes five synthetic cases covering
the original reproduction, relative paths, ambiguous roots, same-date entries,
wrong targets, unknown anchors, legacy prose and duplicate headings. Every case
checks input bytes remain unchanged. Quick preflight passed all executed gates.
Python-wide, JavaScript and clean-tree checks were skipped by quick mode.
`git diff --check` passed. No commit, push, issue comment or closure was made.

The live audit reports 10 unresolved paths, four ambiguous path references,
53 entries without verified links, eight title-text candidates and zero
unreadable files. These counts describe supported structural coverage, not lost
ideas or absent implementation. Remote links, reference-style links, formatted
headings and other legacy prose remain outside verification. No historical
quotation was rewritten. Issue 23's local repair is verified within these limits.

## Remaining issue dispositions

| Issue | Disposition | Owner and next action |
| --- | --- | --- |
| 22 | Local demonstration complete, unpublished | Existing research owner compares exact reference checking, a derived index and the historical heuristic. Product revision and human gates remain unaccepted. |
| 20 | Open prototype comparison | UI owner exercises equal-content desktop and phone compositions after criteria are explicit. Human acceptance remains human-owned. |
| 21 | Open read-only history prototype | History owner uses exact originals and the corrected audit's limits. Begin with one real decision thread. |
| 24 | Open retrieval experiment | Source owner inventories local capabilities and defines one judged synthetic corpus before selecting retrieval dependencies. |
| 7 | Audited locally, implementation issue remains open | Daemon owner retains current routed behavior. Weibao owns real browser and phone checks and historical command reconciliation. See Link 3 matrix. |
| 3 | Closed upstream, dependency reconciled within limits | Present tests do not certify the historical pure refactor. No external mutation performed. |

## Link 2 handoff

GOAL: Complete issue 22's bounded fresh-evaluation demonstration on one existing
UI or architecture decision, preserving the current operating choice until an
explicit revision is accepted.

OWNER: Weibao decides product acceptance. One successor owns this review.

SCOPE: Existing `.planning/AGENT-WORKFLOW.md` fresh-evaluation addendum and its
owning research document. Reuse
`.planning/research/ui-and-project-memory-proposal-2026-09-09.md` if suitable.
Read the live issue 22 criteria. Define present needs first, compare a credible
alternative and retaining the current choice, separate fitness from switching
cost, preserve contrary evidence, state the recommendation and revisit trigger.

DO NOT TOUCH: Preserve all pre-existing dirty changes in AGENT-WORKFLOW,
IDEA-LEDGER, SOURCE-TO-READING-COMBINED-AUDIT, USER-VISION-INBOX, USER-VISION and
three research files. Extend an existing owner narrowly when needed, without
replacing its draft. No production redesign, new durable schema, private course
data, external writes, commit or push is authorized by this packet. Preserve
the uncommitted issue 23 repair and tests.

CONTEXT: Live GitHub inventory returned issues 7 and 20 through 24. Current
STATE points to an older source-reading packet and is not the scope for this
new issue request. No other visible task was active in this checkout at intake.
The user requested efficient routing and daisy chaining. Use this same local
checkout because the relevant inputs and Link 1 changes are uncommitted.

EVIDENCE: Link 1 above owns the executed checks and limitations. Inspect its
actual diff if dependent on its behavior. No full-module audit was performed.

AUDITS: This file reconciles Link 1. The three pre-existing research drafts
remain their owners' evidence, not verified implementations. Reconcile the
chosen decision's observations within its existing owner and link it here.

NEXT ACTION: Read issue 22 and the existing fresh-evaluation addendum, then
choose the smallest decision with inspectable present evidence.

GATE: Saved comparison addresses every issue 22 criterion with source paths,
verified facts versus inference, contrary evidence and limits. Review actual
diff and run required checks. Do not claim human experience acceptance.

RETURN: Report the comparison path, recommendation, checks, unresolved gates
and next issue. Continue the authorized chain only after a stable link with a
known next gate. Final reconciliation must preserve dispositions for all open
issues. Local completion does not mean published or GitHub-closed.

## Link 2 result

The [fresh architecture evaluation](research/ui-and-project-memory-proposal-2026-09-09.md#fresh-architecture-evaluation-demonstration-2026-09-09)
compares the current exact vision-reference resolver, a disposable local index
and the historical heuristic against explicit present needs. Recommendation:
retain exact structural verification and preserve the index as an unbuilt
issue 21 prototype. Zero verified links in the legacy corpus is contrary
evidence against treating the checker as a complete history navigator.

All five live issue 22 criteria are mapped in the existing research owner.
Prior exposure to the incumbent is disclosed. Visual label withholding was
not tested because this is an architecture comparison. The workflow links the
demonstration without adding a competing policy. Historical research statements
about an unmodified script are explicitly scoped to their earlier pass.

The five synthetic vision tests passed on rerun. The live audit exited zero.
Its counts and unsupported coverage are retained in the comparison. No product
choice was overturned and no human acceptance was certified. The pre-existing
research drafts remain proposals. Issues 20, 21 and 24 remain implementation
or experiment work, with no completion inferred from this review.

Quick preflight passed every executed gate. Full Python, JavaScript and
clean-tree gates were skipped. The actual additive documentation and issue 23
diff were reviewed. `git diff --check` passed. No code changed in Link 2.

## Link 3 handoff

GOAL: Reconcile issue 7's historical daemon request against current code and
observable tests, yielding an exact satisfied, failed or unverified matrix and
at most one bounded repair packet if a concrete gap remains.

OWNER: Existing daemon owner for implementation. Weibao owns scope changes.
BUILDER: One successor using its configured model in this same local checkout.
VERIFIER: Inspect actual symbols and test assertions rather than old summaries.

SCOPE: Read live issue 7 and its dependency issue 3. Locate current command,
daemon, route and launch tests symbol-first. Exercise only safe synthetic local
gates for one process serving surfaces, duplicate launch behavior and session
persistence after browser disconnect. Reuse this chain file for the compact
reconciliation unless an existing daemon audit owner is a better fit.

DO NOT TOUCH: Preserve every dirty path listed in Link 2's packet, the issue 23
code and tests, and Link 2's additive workflow and research changes. No private
course data, new durable schema, production redesign, commit, push, GitHub
comment or closure. No implementation edit in this reconciliation link.
Do not disturb a running learner daemon or certify human gates.

CONTEXT: Issue 7 was read live on 2026-09-09. It requests one routed daemon,
duplicate launch opening the running instance and browser closure preserving
an in-flight session. Its historical route list and LAN request require
reconciliation with current accepted command behavior, not automatic restoration
of an old URL design. Link 2 reached a stable local documentation result.

TOOLS NEEDED: Read-only GitHub access and local synthetic test execution.
EVIDENCE: Link 1 and Link 2 own their results. No daemon claim was tested here.
AUDITS: The linked Link 2 comparison is reconciled within its stated structural
scope. Other research drafts remain unimplemented proposals.
NEXT ACTION: Read live issues 7 and 3, then locate launcher and daemon tests.
GATE: Every issue 7 acceptance clause has a source path, exact observed test or
explicit missing evidence, and disposition. Review the actual documentation
diff and run appropriate checks. An audit-only result is not issue completion.
RETURN: Report evidence, limits, remaining defects and the next bounded gate.
Continue only if the next unit is known and authorized. Stop for a required
human or external gate rather than creating speculative implementation work.

## Link 3 result: daemon reconciliation

Live reads of [issue 7](https://github.com/onionviolet/itembank/issues/7) and
[issue 3](https://github.com/onionviolet/itembank/issues/3) returned OPEN and
CLOSED respectively on this run. Code base: `5f3aaf33b1896657f5a52bd6136a5ac1fbb616fa`
plus the preserved dirty inputs above. Only this packet changed in Link 3.
The audit found no reproduced session-loss defect within the exercised scope.
It does not complete issue 7.

### Criterion-to-evidence matrix

| Criterion | Current source and observed evidence | Disposition and limit |
| --- | --- | --- |
| One process serves every named surface | `surfaces/daemon.py:396` ROUTES and `serve_scoped` share one handler/server. A fresh synthetic process returned 200 for `/`, `/quiz/sample_bank`, `/study/sample_bank`, `/day/sample_plan`, and `/report`, then recorded an `/api/submit` response. | Satisfied for the issue's named surface families. Not an exhaustive exercise of every modern course route. |
| Fixed port and duplicate launch avoids contention | `surfaces/daemon.py:start_server`, `surfaces/cli.py:859`. Observed `check_startup_second_attaches`: second CLI exits 0, emits no new bound-server banner, first marker still answers. `check_probe_non_itembank_listener` also passes. | Satisfied for `daemon` using an explicitly selected free port. Default configured port was not occupied or probed. |
| Second invocation opens the running browser instance | `start_server` calls `launcher.open_window`. A mocked occupied-port/probe branch asserted exactly one call with the running URL, `app`, and `no_open=False`, followed by exit 0. | Satisfied at the dispatch boundary only. Actual browser opening remains unverified. The process test deliberately uses `--no-open`. |
| Closing the tab does not lose an in-flight session | `_ensure_quiz_session`, `handle_quiz_get`, and `surfaces/session.py:do_next`. Synthetic submit recorded evidence. All HTTP responses closed before a fresh quiz GET. The rendered session ID persisted, no session file was added, and every stored field except `served_ts` remained equal. Original process remained alive. | Satisfied for disconnected HTTP clients while the process lives. Actual browser lifecycle, unsubmitted text, process termination and restart recovery are not certified. |
| `/` is the day view | Current ROUTES uses `handle_index`; `/day` and `/day/<stem>` serve day views. `check_day_route` passed. `SOURCE-TO-COURSE.md` makes courses the primary object. | Historical literal route differs. Preserve the current course-oriented home. This is a reconciliation point, not authorization to restore the old root URL. |
| One `itembank serve` front door and `day.cmd` becomes a launcher | `surfaces/quiz.py:cmd_serve` and `surfaces/day.py:cmd_day` both delegate to `serve_scoped`. Its documented scoped path still uses free-port fallback, while `cmd_daemon` adopts `start_server`. README names `itembank daemon <dir>` as the consolidated app. No tracked `day.cmd` was found by filename search. `USER-VISION.md:448` records the front-door question. | Literal historical command request is not fully satisfied. Shared implementation does not imply every scoped invocation attaches. Scope decision remains with Weibao. No private launcher or Windows execution inspected. |
| `/api/*` is the same runtime used by the adapter | Observed `check_route_cli_inventory`, `check_api_route_scope`, `check_surface_parity`, and `check_api_cli_parity` pass. `handle_api_next` calls `session.do_next`. | Satisfied for tested inventory and API/CLI parity. No exhaustive parser/scorer or adapter audit claimed. |
| `--lan` remains available, loopback is default, no accounts | `cmd_daemon` resolves LAN mode and `serve_scoped` binds the requested host. `check_startup_loopback_by_default` passed. | LAN code is present. No all-interface bind or real phone test ran. No full authentication or outbound-network audit. Synthetic settings used `update_policy=opt_in`. |
| Issue 3 split into model/runtime/server/surfaces | Current module layout and shared daemon/session calls match the extraction shape. Current parity checks above pass. | Dependency is CLOSED upstream. Literal historical five-tests-unchanged, flag identity, stdlib-only and `day.cmd` behavior were not reconstructed at the refactor revision. Present behavior cannot prove a historical pure refactor. |

### Executed checks and limits

The disposable `itembank-link3-audit.py` runner in the system temporary
directory imported existing test functions and used copied synthetic fixtures,
fresh ports, no browser opening, and opt-in update settings. Ten existing
checks passed: `check_startup_second_attaches`,
`check_probe_non_itembank_listener`, `check_route_cli_inventory`,
`check_api_route_scope`, `check_surface_parity`, `check_study_route`,
`check_day_route`, `check_report_in_progress`, `check_api_cli_parity`, and
`check_startup_loopback_by_default`. The two additional observations were the
same-process route/reconnect probe and mocked browser dispatch above.

Initial sandbox execution could not bind a loopback socket. Approved execution
then encountered one connection timeout in `check_day_route`. The unchanged
retry passed that check and all ten selected checks. The first reconnect
assertion incorrectly required byte-identical session files. Inspection showed
only `served_ts` changed, as `do_next` explicitly requires. The final complete
runner passed with exact equality for all other fields and a rendered-ID
assertion. No production assertion or implementation was changed.

Quick preflight passed all executed gates. Full Python, JavaScript and clean-tree
checks were skipped. The additive packet diff and disposition rows were reviewed.
`git diff --check` passed. The initial GitHub read lacked network access, and the
approved read succeeded. Source inspection was symbol-sized, not a whole-module
audit of daemon, session, model or runtime. No private course data or running
learner daemon was used. Human visual, touch, screen-reader and phone acceptance
remain uncertified.

### Reconciliation and next gate

Links 1 and 2 retain their recorded local results and exclusions. Issues 20,
21 and 24 remain their respective prototypes or experiments. No new repair
packet is justified by the observed reconnect behavior. Issue 7 still needs
real browser duplicate-launch and close/reopen evidence, phone evidence if LAN
acceptance is pursued, and an owner decision on the historical `serve` and
`day.cmd` wording. Stop this link at that human/scope gate. Do not spawn a
speculative implementation successor or treat this audit as issue closure.

Recovery: remove only this Link 3 result and restore the prior issue 7 table
row if this documentation is rejected. Preserve all earlier dirty inputs.

## Proposed usage-flow test scope

User follow-up: scope a reasonable usage-flow test and available tools.
This section scopes the next test run. It reports no new browser pass and
does not authorize production changes or external test-service uploads.
Browser close/reopen and launch dispatch are automatable behavior. Human
judgment remains necessary for usability and accessibility acceptance.
The earlier Link 3 stopping point does not mean all remaining checks require
the user to operate the browser manually.

### First slice and acceptance

Use one isolated synthetic course with one lesson and three practice items,
including a pending-review prose item. Reuse a validated existing fixture.
Start a fresh daemon on a free loopback port with updates opt-in. Keep the
learner daemon and private course roots untouched. Keep one writer.

| Test | Visible journey | Required evidence |
| --- | --- | --- |
| U1 Start and find the activity | Open the normal home, find the course, open its lesson, enter practice through visible controls, return home. | Every transition is reachable without guessed URLs. Course and activity context remain clear. Record dead ends and missing controls as findings. |
| U2 Practice and resume | Submit a wrong answer, use a permitted hint, continue with a correct answer, close the actual tab, reopen the home and resume. Repeat with a fresh browser context. | Runtime session ID, cursor, saved response and hint evidence agree with the visible resume cue. No duplicate response on Back or reload. Served timestamp refresh is permitted. No early keyed disclosure. |
| U3 One running instance | Launch the isolated daemon twice on its allocated port with browser opening enabled. | Observe the second invocation exit, the actual window/tab open at the first instance, and the same first process still serve the session. Test browser dispatch separately if the automation browser cannot receive OS launch events. |
| U4 Finish and inspect evidence | Finish auto-marked work, reach the prose item, inspect available report and home views. | Prose stays pending review. Visible totals state their scope and agree with canonical evidence. No unsupported completion or mastery claim. Missing report navigation is a finding. |
| U5 Input and failure behavior | Repeat key transitions by keyboard and at desktop and phone sizes. Interrupt one request and restore connectivity. | Focus remains usable, controls remain reachable, errors offer a recovery action and retries do not duplicate evidence. Test unsent text separately without presuming autosave. |

Run Chromium desktop first. After the journey is stable, repeat in WebKit and
one touch-emulated phone layout with identical content. Device emulation does
not establish real iPhone Safari behavior or actual LAN reachability. Add one
real phone pass for those claims. A short user pass should assess whether the
next action and resume state are understandable without coaching.

### Tool choice and availability

| Tool | Useful coverage | Current status and boundary |
| --- | --- | --- |
| Available computer-use browser controls | Exploratory visible-control walkthrough, screenshots, tab lifecycle and native launch observation where the surface is supported. | Callable in this session. No browser was launched during scoping. Start here for the first observed journey. |
| Playwright Test | Repeatable browser interaction, isolated contexts, browser engines, mobile emulation, screenshots and traces. | Recommended optional development harness. `tests/js/package.json` currently declares jsdom only. A Playwright import check in `tests/paced_lesson_tracer.py` is not proof of a working installed harness. Verify runtime and browser availability before setup. |
| axe-core through Playwright | Detectable accessibility issues in each important rendered state, including opened menus and feedback. | Proposed development dependency. No installation or scan performed. Retain incomplete results for review. |
| Existing stdlib runtime tests | Session identity, scoring, disclosure, evidence and duplicate-launch checks. | Reuse Link 3's checks and canonical evidence as the behavioral oracle. Browser assertions must not add a second scorer. |
| Real phone, optionally BrowserStack later | Actual mobile browser and touch behavior. BrowserStack can reach localhost through its Local tunnel. | Prefer a local synthetic phone pass first. Cloud service use adds account/setup cost and remote traffic. No cloud connection or upload is authorized by this scope. |

Official references checked during scoping:
[Playwright isolation](https://playwright.dev/docs/browser-contexts),
[emulation](https://playwright.dev/docs/emulation),
[trace viewer](https://playwright.dev/docs/trace-viewer),
[axe integration and manual limits](https://playwright.dev/docs/accessibility-testing),
and [BrowserStack Local](https://www.browserstack.com/docs/live/local-testing).

### Evidence and bounded continuation

Capture revision, fixture identity, browser/version, viewport, exact actions,
visible result and canonical session/evidence checks. Save local traces on
failure and selected screenshots. Use pass, fail, unavailable and not-run
separately. Preserve the first failure even when a retry passes. A screenshot
alone cannot prove persistence or accessibility.

The first deliverable is one observed U1-U4 journey plus U5's keyboard and
phone-layout sample, with reproducible findings. Only then encode stable
steps as repeatable tests. No new testing platform, production redesign or
full cross-browser matrix is needed before that observation. Follow-on scope
can cover source import, notes, formal testing, reviewed changes and undo,
then daemon restart and offline restore. Those are separate recovery gates.

Owner: the next test operator executes the synthetic browser pass. Weibao
owns experience acceptance and changes to command scope. No successor task
was created during this scoping turn. Existing issue dispositions remain.
