# L3 rich practice readiness, October 3, 2026

Status: bounded readiness complete; Q1 domains, Q2 fixed anchors and Q3
graph/transcript scope remain pending. No production format was promoted.
Coordinator: `01a102a5-223f-7293-ae74-1922372ac0c8`.
The [implementation owner](../cross-repo-implementation-2026-10-03.md) owns
dispatch, leases and the single combined source gate.

## Delivered scope and authority

This lane created `tests/rich_practice_readiness_roundtrip.py` and this report.
The new six-test suite probes the previously untested P5 D6 reading-reference
authority join. It reuses accepted synthetic reading fixtures and
`reading._current`, `reading.confirm`, `reading.declare`, journal undo and the
existing evidence writer. Its test-only resolver is not imported by production,
and no new graph field, route, bank directive or scorer was registered.

Relevant pending-format owners are
[domains](../question-types-2026-09-25/DOMAIN-COMPLETION-2026-09-30.md),
[anchors](../question-types-2026-09-25/EVIDENCE-ANCHOR-READINESS-2026-09-30.md),
[graphs](../question-types-2026-09-25/ACTIVITY-GRAPH-READINESS-2026-09-30.md) and
[P5 D6](../FEATURE-COMPLETION-COORDINATION-2026-09-30.md).
These were reconciled rather than replaced with duplicate domain/anchor/graph
tracers. The September 30 prototype fingerprints still match the current files.

AGENT-WORKFLOW section 5 requires:
> Binding formats, assessment authority, rights or egress changes, hard
> rejections, and milestone scope use the full evidence, prototype, ledger,
> readiness, and direct-user-decision gates.

The coordinator explicitly confirmed Q1-Q3 remain pending during this lane.
Generic implementation authorization therefore does not select these formats.
Authored-only graphs and source-bound graphs remain distinct choices. D6's
nullable reference is the exact pending specimen from its existing owner:

```json
{"reading_ref":{"course_id":"<opaque course ID>","occurrence_id":"<opaque reading occurrence ID>","revision_id":"<opaque accepted reading revision ID>"}}
```

## Current findings

F1: `question_domains.prepare_comparison` returns exact operands and raw input,
without a verdict. Production `runtime.fill_spec_errors` still admits only
text, numeric and polynomial. The current `runtime.score_response` remains the
only settlement authority. Its polynomial lifecycle already supplies raw
responses, private diagnostic outcomes, refusal and actual-mode disclosure.
Domain promotion should extend that lifecycle instead of making a helper scorer.

F2: The fixed-anchor tracer remains a separate journaled presentation adapter
over existing multi responses. It pins original source bytes as well as the
normalized passage because accepted source identity normalizes line endings.
Production model parsing, source admission at preview/submit, revision pinning
and reviewed header proposals remain unimplemented for anchors.

F3: P5 currently reads a private `session._reconcile_staged` on a copy and
refuses required recovery. `session.do_next` can repair and writes `served_ts`,
so it cannot serve as a byte-preserving graph read. A runtime-owned public
committed-unit projection is still needed for promotion. Graph controls must
not decide commitment, repair a sitting or inspect correctness for branching.

F4: D6 can reuse the existing reading authority without a new evidence store.
The new probe verifies exact admitted course identity and current occurrence
revision, separate occurrences over the same source, stale graph/revision and
unknown/denied rights refusal, missing/changed source refusal, byte-preserving
refused admission, exact journal undo, fresh-process resolution, and two
processes declaring one explicitly confirmed intent with one receipt.
Only learner confirmation followed by `reading.declare` creates a scoreless
reading event. The resolver and source opening create no event. A model actor
and an invented confirmation intent refuse.

F5: Replaying an already recorded reading intent preserves its original receipt
after the source becomes unavailable and reports current availability
separately. First publication still rechecks source, accepted revision and
rights. A graph must distinguish historic receipt display from new source
admission. A null D6 reference stays authored presentation only; this probe
does not implement bound transcript display or certify P5 D6 production.

## Minimal sequential promotion packet and interface requests

I1, domains: after exact Q1 approval, lease `model.py`, `runtime.py`,
`surfaces/session.py`, `surfaces/quiz_page.py`, `schemas/item.schema.json`,
`schemas/response.schema.json` and dedicated domain-production tests. Extend
existing FIELDS lint, content/response fingerprint, public entry metadata,
private pinned tests and runtime settlement. Reuse labeled text inputs and the
existing `/api/submit` and served quiz POST. C must route any new typed domain
refusal through the existing API refusal and `_echo_quiz_failure` path, retaining
raw field strings and refusing before attempts. No new domain endpoint is needed.
Change `schemas/session.schema.json` only if a concrete durable pin cannot fit
the existing bank binding. Do not include `schemas/model_adapter.schema.json`,
which C owns for separate Q4 work.

I2, anchors: after exact Q2 approval and domain writer release, lease the same
parser/runtime/session/client files plus the additive item and necessary
session/response contract definitions. Parse one EVIDENCE-ANCHORS directive,
lint the exact source/offset/option declaration, hash its revision and keep
ordinary multi scoring. C must pass an admitted course context to source
resolution for both preview and submit, rather than trust a client path or
course claim. Preserve the source lock/expected-base discipline before evidence
publication. Existing quiz/API routes can remain; use selected anchor IDs for
drafts and the validated option mapping only for runtime submission. The native
author proposal path in `surfaces/agent_operation.py` currently handles a
STAGED-CASES header; it needs a coordinated lease or C extension for anchor
header preview, cancellation, CAS accept and exact undo.

I3, graph: after exact Q3 choice and earlier release, introduce one public
runtime/session committed-unit projection with neutral formal state and explicit
recovery refusal. Keep graph presentation under the existing component journal.
The candidate C-owned native entry is `/course/<course_slug>/activity/<occurrence_id>`;
its view and POST choice/checkpoint/cancel/resume handlers must use an admitted
sitting, accepted graph fingerprint and expected component fingerprint. Exact
endpoint registration waits for the approved graph contract and importable
panel interface. Require complete runtime units in declared order, neutral
formal endings, exact restart and separate descriptive denominators.

I4, D6 only if chosen: C must resolve the opaque course ID against the already
admitted course root. The route's filesystem slug is not the opaque object ID.
Expose the current reading resolver through its existing owner instead of
copying `reading._current` into graph production. Admit accepted course journal,
current occurrence, binding/source/locator and read rights with a separately
supplied expected course fingerprint. Reuse `/api/course/confirm-reading` and
`/api/course/declare-reading` for explicit learner declarations, preserve their
intent replay behavior and show source-backed content from the owner. A graph
checkbox or authored transcript never manufactures source-read evidence.
This requires a specific `reading.py`/`course.py` owner lease beyond L3's initial
production file scope; none was requested or granted in this readiness pass.

I5, acceptance gate: promote one approved slice at a time. Require actual
served practice/formal behavior, malformed/unsupported/stale/rights refusal
before attempts with raw input retained, concurrent replay/process recovery,
source/bank/graph identity, reviewed author accept/cancel/undo, useful Markdown
and native keyboard/narrow presentation, and exact source-matched tests.
Formal/hint disclosure stays with the runtime. Human touch/screen-reader and
learning acceptance, packaged/installed delivery and live-provider checks keep
their separate gates. Only C runs broad preflight after all source writers release.

## Executed verification and source pins

Observed HEAD: `28bf561865cf0696a8beb42dd6f356b8bf6ec648`. The checkout was dirty
at entry and inherited edits were preserved. Local receipts live under
`.reasonix/cross-repo-implementation-20261003/rich-practice/`.
`inputs.sha256` pins the three proposal mechanisms/tests, model, runtime,
session, quiz page, course, reading, graph and journal before the scoped checks.
`additional-inputs.sha256` pins the assessment schemas, native test and repaired
new test. Both manifests rechecked successfully after the scoped runs.
`native-and-author-observed.sha256` records additional post-run observed source;
it is not a whole-daemon frozen revision certificate.

| Command | Result | Local receipt |
| --- | --- | --- |
| `python3 tests/question_domains_roundtrip.py` | 8 pass | `question-domains.log` |
| `python3 tests/evidence_anchor_contract_roundtrip.py` | 13 pass | `evidence-anchor.log` |
| `python3 tests/activity_graph_contract_roundtrip.py` | 17 pass | `activity-graph.log` |
| `python3 tests/staged_production_roundtrip.py` | 11 pass | `staged-production.log` |
| `python3 tests/polynomial_production_roundtrip.py` | 8 pass | `polynomial-production.log` |
| `python3 tests/rich_practice_readiness_roundtrip.py` | 6 pass after harness repair | `reading-ref-repaired.log` |
| `ITEMBANK_VISUAL_QA_CHANNEL=chrome python3 tests/staged_checker_ui_roundtrip.py --browser-shots .reasonix/cross-repo-implementation-20261003/rich-practice/native-shots` | Served form/API practice, exam and diagnostic pass; Chrome keyboard/reload/continuation at 1280, 390, 320 pass | `native-staged-checker.log`, `native-shots/` |

The initial new-test run failed five errors and one failure because the harness
called nonexistent `identity.is_object_id`. Importing the fixture TestCase also
caused unittest to discover nine unrelated fixture tests. Both harness errors
were corrected; the original `reading-ref-initial.log` remains failed.
The new test now imports the fixture module rather than exporting its TestCase.
Its final SHA-256 is
`e3a1ab47f235c7087b1f4d64812029791ec680fe866c54a053546f4fbad6c41d`.

The actual new-file diff was saved as `readiness-test.diff` and inspected.
`git diff --no-index` exits 1 for this expected new-file difference.
The 320px polynomial refusal screenshot was inspected: raw `sin(x)` remains in
the labeled input, the refusal is visible and the submit control has a focus
outline. This is automated/browser and visual source evidence, not human
accessibility or learning acceptance. The native checks exercise existing
approved staged/polynomial formats, not promoted domains/anchors/graphs.

## Recovery, limits and ownership release

All roots and content created by tests are fictional temporary courses. Remote
egress is none; native requests use disposable loopback daemons and installed
Chrome, with no browser download. No real learner data or sitting was accessed.
No production parser/runtime/client/schema, shared planning projection, commit,
push, package build, install, release or broad preflight was changed or run by L3.
Large source modules were sampled by symbols rather than read or audited whole.

Undo for this readiness slice removes only this report and the new test after
coordination; local receipts may be retained. Existing proposal mechanisms and
dirty production bytes are not reverted. Operational findings belong in this
lane report, not provider memory. Q1-Q3 remain the next production gate under
their existing owners. L3 releases its two delivered paths after this handoff;
no new chat or subagent is needed while those direct decisions remain pending.
