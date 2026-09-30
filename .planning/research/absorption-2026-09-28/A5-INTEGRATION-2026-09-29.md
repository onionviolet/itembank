# A5 integration evidence

Date: 2026-09-29. Owner: integration chat `01a0f048-1de1-7932-a29b-47917e192787`.
Dispatch: `PARALLEL-IMPLEMENTATION-2026-09-29.md`.

## Initial state

Read the dispatch, execution context, agent workflow, current STATE excerpts,
staged/checker packets and explicit package inventory. The checkout is dirty;
existing changes remain with their owners. A1-A4 were active at the first compact
status snapshot. No shared parser/runtime/course/source file ownership has
transferred. No commit, push, installation, release or real learner-file write
is authorized.

## Integration gates

- Wait for lane evidence and released ownership before shared wiring.
- Review checker and stage semantics against the sole runtime authority.
- Compare fresh packaged bytes with source and explicit inventory.
- Run focused repairs before one stable combined full preflight.
- Keep physical touch, screen-reader and learning-transfer acceptance explicit.

No implementation or combined validation is claimed by this initial record.

## Initial package regression

Added `tests/a5_integrated_package_roundtrip.py` (before: absent). Inventory
check passes: 191 source members match a freshly built candidate byte for byte;
all static local root-module imports are staged. This is not a stable final
candidate while builders remain active.

`python3 tests/a5_integrated_package_roundtrip.py --offline-restore` fails in
the clean copied-test tree, which imports runtime modules only from the fresh
zipapp. `course_package._validated_evidence_events` opens response schema using
`dirname(__file__)`, raising `NotADirectoryError` inside the zipapp. This is a
production packaging defect, not an unavailable external gate. A4 owns
`course_package.py` until completion; A5 will replace its archive-resource lookup
through the existing resource authority after release, then rerun the concrete
failing journey. No concurrent edit or inter-chat message was sent.

## Released A4 integration

A4 completed and released ownership, verified by a compact completed-turn
snapshot. Its `course_package.py` release fingerprint was
`76f1afa21592eefc2fba391ff43720a824190de5c4ffe9ee077688f10483dd4f`.
A5 saved that exact before image in the ignored repository-local
`.reasonix/a5-integration-20260929/before/` snapshot tree and repaired the
schema read through `resources.read_text`.

The new native quote-note journey found a second concrete export gap: private
notes were ignored when the course had no reading occurrences. The existing
reading transport now carries explicitly included note-only backups and their
source target locator companions. It still uses existing package validation,
staged restore and private-note consent. Research inclusion state stays private
and is explicitly reported as `_research/research-scope.json` in the existing
unregistered-file loss report. No personal selection is auto-restored.

Added `surfaces/research_context.py` and
`tests/a5_research_context_roundtrip.py` (before: absent). The native form seam
previews exact accepted occurrences, separates Link from Copy quote, uses the
existing note pair and CAS writer, saves explicit source/note inclusion through
A4's scope writer, requests local advisory context without calling a provider,
and routes note undo through the journal. Course sources parsed as assessment
banks are refused; runtime disclosure is not bypassed. Shared daemon routing
still awaits A1 release at this point.

`python3 tests/a5_research_context_roundtrip.py` exits 0: second duplicate
occurrence at line 4, read-only preview, cancel without a destination, distinct
link/copy notes, excluded sentinel absent, separate learner-note labels,
assessment-source refusal, clean byte-identical note-only backup and exact
citation return, named scope omission, undo and stale-scope refusal pass.
Development-only test setup failures were corrected: note writers return
acceptance metadata rather than full Markdown, and an ordinary restore needs
an approved existing destination. The resulting note-only omission was a real
production failure and was fixed, not waived.

`python3 tests/a5_integrated_package_roundtrip.py --offline-restore` exits 0
after repairs. All six clean archive-only suites pass: course package, reading
package, source-binding forms, mocked companion health, A4 source recovery and
A5 native context. The copied daemon test helper launches the fresh archive;
no checkout Python modules exist in its temporary root. That launcher repair
corrects test isolation, not production behavior. The package inventory now
contains 192 byte-identical source members. The candidate remains intermediate
while A1/A3 are active. Scoped `git diff --check` exits 0.

## A2 readiness review

A2 completed and froze its dated evidence. P1 can reuse existing fill fields,
drafts and scoring after an explicit escaped layout declaration and authored
marker validation. P2-P5 remain executable prototypes: practice commitment and
release, linked child evidence/crash/concurrency, accepted span declarations,
polynomial outcome/schema/authored-test semantics, and versioned activity graph
identities are unpassed production gates. No advisory polynomial scorer or
prototype presentation sidecar is promoted to runtime authority.

## September 30 build deferral

The wrap-up owner relayed the user's direct instruction: "short term, doont make
new builds or anything until all the backlog and audited stuff is completed".
A5 pauses fresh application archive builds and packaging from this point, and
does not install or release. Earlier archive results retain their exact scope;
later source changes create explicit archive drift. Final gates run source
checks and existing-candidate inspection; build-dependent checks remain deferred.
A1/A2/A3/A4 have all completed and released ownership. Shared routing and the
opt-in inline fill presentation are now owned by A5. No duplicate full suite is
running in another lane.

## Frozen source implementation and observed gates, September 30

A1's completion released its shared parser/runtime/quiz/daemon/schema paths.
A3's completion released its proposal/readiness/history paths. A5 verified the
release fingerprints before shared edits and preserved their dirty before
images. Python snapshots use `.py.txt` extensions because the sole-authority
scanner also inspects ignored Python files. No ignored duplicate parser/scorer
or writer is left by the A5 snapshot route.

Delivered source work:

- Native Build routing calls A3's existing outline adapter. Duplicate fields,
  caller target paths, foreign-origin writes, stale drafts/course/source/rights
  are refused. Corrected preview, cancel, accept once, restart and journal undo
  run through existing accepted-file authorities. A safe lesson return validates
  admitted course/bank/sitting identity and existing selection admission without
  opening or advancing another sitting.
- Native Sources links to local exact passage preview, explicit context
  inclusion, private Link/Copy quote and undo. Source and learner-note payloads
  remain separate; requests preview only explicitly selected local content.
  Assessment-shaped sources are refused. No model or remote companion is called.
- `FILL-LAYOUT: inline` is an opt-in presentation over existing fill fields.
  Each `{{field_id}}` must occur exactly once. Missing, repeated, unknown,
  malformed or duplicate declarations fail existing fill lint/runtime entry.
  Legacy undeclared stems remain unchanged, including literal braces. Native
  and both rich clients retain labelled text inputs, same field IDs, originals,
  drafts and sole-runtime scoring. Item schema version 1 gains one optional
  presentation property; session/response schemas and old evidence are unchanged.
- The two structural ordering copies now reuse the guarded dragover handler
  on dragenter. No new external drag trust, selection rule or scoring path was
  introduced. The completed A1 closure test now asserts the actual production
  hook before comparing the historical missing-hook behavior.
- Source-only preflight explicitly defers fresh app archive tests, sample build
  and dependency installation; normal CI/default mode still runs them. Tests
  verify those exclusions and unchanged default inventory. Existing JS deps
  must match the pin before the source-only Node gate can run.

Commands actually completed:

| Command | Result |
| --- | --- |
| `python3 tests/a5_inline_fields_roundtrip.py` | Exit 0: grammar/private projection, legacy compatibility, native position order, reviewed authoring, invalid no-write, raw formal response and withholding. |
| `python3 itembank.py id-assign fixtures/a5_inline_fields.md` and `lint` | One synthetic ID/hash assigned; final lint exit 0, one item, zero errors/warnings. No real learner artifact was changed. |
| `python3 tests/a5_research_context_roundtrip.py` | Exit 0: exact duplicate occurrence, explicit scope, link/copy/cancel, quote rights, assessment refusal, clean note-only restore, named scope omission, undo and stale refusal. |
| `python3 tests/a5_served_integration_roundtrip.py` | Exit 0: ordinary native HTTP corrected outline, stale/cancel/accept/restart/byte-exact undo, duplicate/cross-origin guards, selected local context, inline invalid/raw entry and admitted lesson return. |
| `python3 tests/a3_course_workflows_roundtrip.py` | Exit 0. Malformed evidence warnings are intentional corruption fixtures. |
| `python3 tests/a2_question_families_roundtrip.py` | Exit 0, 12 tests. Existing reader ResourceWarnings remain outside this source slice. This is prototype proof. |
| `python3 tests/preflight_roundtrip.py` | Exit 0: 15 CI steps, 13 mirrors, 2 CI-only. Source-only omits archive launch/install and default mode remains complete. |
| `node --test tests/js/ordering_workflow.test.mjs tests/js/structural_drag_closure.test.mjs` | Exit 0, 10 checks after the production hook. |
| `node --test tests/js/a5_inline_fields.test.mjs tests/js/structural_drag_closure.test.mjs` | Exit 0, 6 checks, including escaped text, existing control identity and guarded production arrival. |
| `python3 itembank.py guard .` | Exit 0, zero offenders after A2 moved its bank under its fixture root. |
| Scoped `git diff --check` and module compilation | Exit 0. |

Development test assumptions were repaired: model lint returns its existing
error/warning tuple, native forms use form_token and their existing POST action,
and invalid native submissions return 400 while retaining originals. Missing
`re` in the new native marker renderer was a reproducible implementation defect,
fixed before the passing source gates. No failure was waived as acceptance.

Actual production source Chrome proof used a disposable ordinary ordering
daemon, without the proposal proxy or synthetic drag-event dispatch. Trusted
pointer input assigned right to position 2, left to position 3 and start to
position 1. Reload retained `start,right,left`. Keyboard Remove/Add restored
the same ID array. Runtime submission withheld exam feedback; a second valid
order left the distractor unused, and the ordinary report recorded 2/2.
Two response events, exact arrays and current quiz hash were saved in ignored
`ordering-browser-evidence.json`; proof images are `ordering-source.png` and
`ordering-source-report.png` under the A5 local evidence root. This closes the
source automation drag gate, not physical touch or screen-reader acceptance.

A separate source matching tab visibly assigned a/b by actual pointer input,
refused forbidden reuse, and submitted through its native form with exam
feedback withheld. Native menu-arrow/typeahead automation was inconsistent and
the tab later became unavailable. An over-specific post-run evidence assertion
failed before the response copy, and normal disposable cleanup removed that
temporary root. No final matching score/second task or physical keyboard-menu
acceptance is claimed from that browser run. A1's earlier complete package
matching proof and the ordinary source HTTP matching regression retain their
own scope. The browser artifact limitation does not reopen verified ordering
or block the final source suite. No additional browser journey was repeated.

## Current source, archive, installed and final-run states

`build.py` already stages the new surface via its explicit `surfaces` allowlist;
all shipped root imports remain in STAGE_FILES. No unnecessary inventory change
was made. Before the build hold, the final A5 intermediate clean archive test
had 192 byte-identical source members and all six source/restore suites passed.
Its SHA-256 was `4e4474dea2cea1fcbcd922c71a6f8244fea2da350d5136c313c3f0dca9d7900d`.
That temporary archive was removed by the test and predates final routing,
inline and structural drag source changes.

The preserved existing ordering archive remains SHA-256
`ac17ac70807dbbcb3c5848e8af0ccd269252a5ea1b11ff74d3983b99694f19da`.
Read-only `--existing` comparison exited 0 and recorded explicit drift: missing
`surfaces/research_context.py`; changed course_package, model, runtime, item
schema, agent_operation, course_workbench, daemon, quiz_page and retention_view.
This is inspection success, not a package compatibility pass. No fresh archive
was built after the user's hold. The active installed learner app/sitting was
not replaced or exercised by A5. Human accessibility, learning transfer and
installed final-source behavior remain unaccepted.

The source/test freeze is recorded in ignored `source-freeze-20260930.json`,
including the latest presentation, Home, reading desk, lesson, theme and settings
bytes used by UI D4-D7. After this freeze A5 changes owning documentation only.
Wrap-up chat `01a0f075-e39e-7801-8767-adea4d73134a` now owns the ONE final
`python3 scripts/preflight.py --source-only` run. A5 did not launch an equivalent
full suite. Its exact results are pending from that owner; no full pass is
claimed here. Fresh app archive/sample-build checks and installation stay
explicitly deferred. Preserved dirty edits cannot satisfy the clean-tree gate.

Gate timing correction: wrap-up's earlier start fingerprint precedes one final
source edit in `surfaces/research_context.py`, at 2026-09-30 00:36:33 EDT.
`apply` now recognizes Cancel before reading the course or private roots, so a
cancel request does not fail merely because a course is stale. No accepted
write, response, scoring or egress behavior changed. The final file SHA-256 is
`01e6739ad5dc4e16d666b8e1229e828136377bebd635b79460ec7fddafd31f1d`.
The native-context and ordinary served A5 scripts both exited 0 on those final
bytes after that edit. Wrap-up will also rerun those two affected scripts after
the full inventory, without another full run. It confirmed its other sampled
production/preflight owners remain unchanged. A5's final source freeze has zero
subsequent production/test drift. This timing is explicit rather than treating
the run as wholly frozen at its earlier start.

The authoritative final log is
`.reasonix/chat-wrapup-20260930/preflight-source-only.log`. Its running inventory
contains 169 Python files with three app archive tests explicitly deferred.
Current completion/results are still owned by wrap-up; A5's owning-record
updates do not claim those tests passed before its returned result.

P2-P5, live companion identity/auth/provider transport, ordinary whole-root
restore crash/race publication and human gates retain the precise prerequisites
in A2/A3/A4 evidence and the existing staged/checker packets. They are not
reclassified as implementation completion. Current ranked resume is STATE's
September 30 surface; earlier September 8 current-position/next-packet labels
are explicitly historical.

## Final source fingerprints and recovery

All A5 changed paths and exact before/after SHA-256 values are in the ignored
`final-fingerprints.json`, next to `source-freeze-20260930.json`, `archive-drift.json`
and `task-only.patch` under `.reasonix/a5-integration-20260929/`. The before
images preserve the actual released dirty inputs, not HEAD. Core final values:

| Source path | Final SHA-256 |
| --- | --- |
| `model.py` | `316626717ef9dad85bd433b8d780c7854285a914f8eee6d19777217a4b011f96` |
| `runtime.py` | `9b1347ac82bf65091666f7c26a294b26b8fbe9f0a1241e4ca31841ccc2ff6f9c` |
| `schemas/item.schema.json` | `0bf7c46a1fda484d8137a69bb24f6b7666a4bef11bee5955a726b55339cb1411` |
| `surfaces/quiz_page.py` | `8ced1a101cbcc374b368c9c84187d1bbf0c814a8629d11d4270375615eaaa69d` |
| `surfaces/daemon.py` | `fba16ed51d34d15289922215547665b682167223da5fe0f69b8ac23844658346` |
| `course_package.py` | `8c46b923bce9f244e2390f2f4477ce89bbd1a688c9984863fdaaf7ffed75bb79` |
| `scripts/preflight.py` | `359f4dc2559e8da59430bd38dbbae0c8d6f90dc939825c4e852665c0f69a8166` |

Additional changed paths are the new research surface, four A5 Python gates,
inline JavaScript gate, strengthened structural-arrival gate, synthetic inline
fixture, preflight mirror test, README and existing STATE/FEATURE-INVENTORY/
question BACKLOG/absorption/dispatch owners. A2-A4 production paths remain
their completed lane changes except A5's named package and routing integration.
No build.py, journal.py, course.py, source-adapter or notes change was necessary
in A5. No source file changed after the final A5 freeze.

`git apply --reverse --check` passed for the scoped recovery patch. This was
read-only; no reverse patch was applied. Undo only reviewed A5 hunks or restore
their matched before images. Verify current bytes against the recorded after
fingerprints first, and never restore a snapshot or reverse documentation over
subsequent wrap-up results or another writer's changes. Remove only A5's named
new files if reversing the whole slice. Synthetic accepted operations separately
recover through tested proposal Cancel and existing journal Undo.

Large parser/runtime/daemon/quiz/package modules were sampled by symbols and
scoped windows, not read whole. This is bounded implementation evidence, not an
exhaustive product, dependency, accessibility or learner-efficacy audit. A5 owns
no further production edits or full-suite launch. After final record release,
wrap-up owns the pending final gate result and its current-state projection.

A5 source and bounded record work is complete. STATE, this evidence owner and
the dispatch packet are released to wrap-up `01a0f075-e39e-7801-8767-adea4d73134a`.
The final source-only combined gate is explicitly pending that owner; it was
at 58/169 in the last returned progress update. A5 is not kept active merely to
wait for that inventory. No new source/test edit, archive build or equivalent
full suite follows this release. The late Cancel timing and required two
post-inventory targeted checks remain recorded above.


## Wrap-up verification and record release, September 30

The wrap-up took released ownership and ran one complete source-only preflight.
Its 169-file inventory executed 166 Python scripts and explicitly deferred
`a5_integrated_package_roundtrip.py`, `math_offline_roundtrip.py` and
`packaging_roundtrip.py`. Sample build and dependency installation were also
deferred. The captured full run exited 1 on tests and the preserved dirty tree.
All other executed fast gates and its JavaScript gate passed.

Preflight prints only the first twenty diagnostic lines of a failed gate.
Six named failures hid four later failures. To avoid treating a truncated log
as complete evidence, wrap-up ran the 71 scripts after model_phase again with
full output and per-script exit codes. Four failed there. Those four plus the
six visible failures were resolved and rerun successfully. This is verification
across the full run, diagnostic tail and targeted repairs, not a claim that the
original run or a repeated clean full preflight passed.

Repairs: three new native routes now have CLI inventory entries and the
capability manifest is regenerated. Surface coverage classifies outline and
research routes under their real objects. Optional exact-sitting navigation
preserves legacy pathless callers. Offline matching/ordering no longer carry
storage code; served recovery bytes are unchanged by that repair. The study
default test reads the current nested accent setting, and the accessibility
selector check recognizes stable build controls while still excluding visual
commit selects. No parser, scorer, evidence or rights authority was changed.

All ten affected Python scripts pass after repair: capabilities, daemon, gate,
ia_route, lesson, model_phase, paced_lesson_tracer, surface_coverage_check,
surface_roundtrip and visual_accessibility. The late cancellation edit was
also checked with native-context and served-integration scripts on final bytes.
The complete final Node run passes 106 tests. Paced lesson reports 8 passing
scenarios; visual accessibility reports 13 positive browser gates and the
expected negative equivalence case. These are automated checks, not human
screen-reader, physical touch or learning-transfer acceptance.

Operational finding: Playwright was installed but its cached browser executable
was absent. The already installed Chrome launched successfully without an
installation. `tools/visual_qa.py` now accepts the optional
`ITEMBANK_VISUAL_QA_CHANNEL` environment setting and retains its existing default.
The successful browser checks used `ITEMBANK_VISUAL_QA_CHANNEL=chrome`.
For this machine, future source-only runs use that same environment prefix;
other environments retain their installed/pinned browser policy.

Logs and before snapshots are in `.reasonix/chat-wrapup-20260930/`.
`preflight-source-only.log` preserves the original failures;
`post-model-results.json` records all 71 diagnostic-tail results;
individual `*-final.log` files record repairs and browser checks;
`js-final.log` records all 106 JavaScript tests. Final source fingerprints and
expected-base owner mutations are recorded in `final-source-fingerprints.json`
and `owner-update.jsonl`. Recovery snapshots preserve inherited dirty bytes;
never restore HEAD or overwrite later owner edits. Large modules were sampled
by symbol and exact failing assertions, not read whole.

Read-only inspection of the preserved ordering archive still reports the same
missing research surface and nine changed members. Its SHA-256 is unchanged.
No new app archive, install, commit or push occurred. The dirty-tree gate remains
unsatisfied because authorized and inherited edits remain local. CI-only setup
and published-schema pipeline remain unrun. P2-P5, ordinary whole-root restore,
live companion, installed and human gates retain their existing prerequisites.
STATE's current September 30 resume list is authoritative; this record adds no
competing queue. All completed chats are idle and no gate process is left running.

Final record checks: `python3 scripts/preflight.py --quick --source-only`
exited 0 on executed fast gates; its build/full-suite/clean/JavaScript skips
are explicit, not additional pass evidence. Final whitespace and skill-mirror
checks pass. All 27 final source/test/tool inputs match the captured manifest.
