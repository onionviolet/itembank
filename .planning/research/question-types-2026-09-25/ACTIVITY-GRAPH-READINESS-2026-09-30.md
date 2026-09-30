# Activity graph readiness, September 30, 2026

Status: tested executable P5 prototype. Format acceptance and production
promotion remain pending. Source handoff `b1a96707d668f5d49ebc4838c27ea6d9247fa737`
released this lane's startup write gate. This lane owns only
`prototypes/activity-graph-contract-20260930/`,
`tests/activity_graph_contract_roundtrip.py` and this report.

## Findings and reused authority

F1: A2 P5 and AUDIT-REMAINING F6 correctly name the missing graph contract.
The existing `prototypes/audit-question-families/families.py:Journey` already
journals static branches and a simulated seconds checkpoint. It does not
validate graph nodes, edges, required-unit paths or ending identities. Its
practice refusal predates production staged commitments. The new prototype
reuses its component journal pattern, not its old exam transport or a second
assessment cursor.

F2: `runtime.staged_binding`, `validate_staged_binding`, `staged_case` and
`session_view`, plus `surfaces.session.do_action`, now supply complete-unit
selection, immutable bank/case bindings, committed children and disclosure.
The prototype never submits, scores, edits or repairs a sitting. Synthetic
tests submit only through `do_action`. `_runtime` calls the existing private
`session._reconcile_staged` on a copy and refuses if repair is needed. The
existing `do_next` owns durable repair. A production public authority seam is
needed rather than copying that reconciler into the graph implementation.

F3: Existing authorities remain separate. `model.ACTIVITY_COLUMNS` carries
activity semantics and static/a11y fallback, `MEDIA_COLUMNS` carries rights,
availability and integrity, and `surfaces.lesson.paced_view_steps` projects
existing lesson steps. `reading.confirm` and `reading.declare` own actual
accepted-source reading evidence. Prototype transcript checkpoints are only
journaled presentation traces; they never call those reading APIs or become
canonical source-read declarations. No media playback or dwell-time mastery
claim is justified by this prototype.

The source sampling was bounded: AGENTS, EXEC-CONTEXT, STATE current entries,
AGENT-WORKFLOW reading mode, SOURCE-TO-COURSE durable reading section, A2 P5,
AUDIT-REMAINING F6, existing branch/checkpoint methods, staged helpers and
targeted tests. Large parser/runtime/lesson/journal modules were read by symbol,
not whole. No exhaustive vision, schema, package or donor audit is claimed.

## Proposed format choices requiring acceptance

| Ref | Exact proposal | Boundary or cost |
| --- | --- | --- |
| D1 | Standalone version-1 JSON graph with `occurrence_id`, `entry`, ordered `nodes`, ordered `edges`, `version`. A content-addressed accepted revision hashes the entire declaration, including ordered arrays. Node/edge IDs are unique and unchanged within the accepted revision; an ending is an immutable node identity, not a score label. | No production syntax added. Renaming, changed transcript, changed demand or routing produces a new revision; earlier checkpoints never transfer automatically. Nodes have `id`, `kind`, `modes`, `required`, `activity_id`, `children`, `transcript`, `ending`; edges have `id`, `source`, `target`, `modes`, `policy`, `label`. |
| D2 | Assessment nodes name exactly one existing two-child staged activity. Every route visits all selected assessment units in their declared runtime order, before descriptive transcripts. Graph reads derive closure from the runtime cursor passing both committed child positions. | Partial units, duplicate children/activity IDs, randomized unit order inconsistent with the graph, extra ordinary items and descriptive barriers before later assessment refuse. General ordinary-item/assessment graphs and interleaved teaching need a runtime-owned progression contract first. |
| D3 | Practice branches use explicit learner choice after whole-unit commitment. `continue` is the single-edge policy; `choice` is mandatory on all edges at a branch. There is no answer, score, correctness or arbitrary predicate field. Exam/diagnostic paths have one response-independent `continue` destination and neutral endings, with no teaching transcript. | Correctness-based practice branching also remains outside this minimal contract. Formal route labels, identities and HTML match for right and wrong responses. Unopened transcripts never appear in the public preview. Timed sittings refuse until runtime expiry has a public projection. |
| D4 | Presentation component stores accepted graph fingerprint, occurrence, sitting ID, bank fingerprint, selected edge/path history, transcript paragraph anchor, explicit `reported_read` and cancellation. Existing journal CAS and atomic writes own every mutation. | Restart means reopen the same sitting/occurrence/branch/checkpoint. Cancel blocks mutation but preserves all records; resume reopens them. Starting a new assessment is a separate runtime operation, not clearing this sidecar. Production acceptance must resolve source-backed reading occurrence bindings and rights. |
| D5 | `descriptive` and `neutral` are ending kinds, never mastery. Expose assessment selected-child denominator separately from selected transcript count and reported-read count. The descriptive denominator stays provisional until an ending. | Example: two settled runtime child events across two objectives remain two child responses; one reported-read transcript is one descriptive trace, never a third assessed success. Unselected alternate transcripts do not count as failed or completed. Replaying/reopening adds no response event. |

The executable validator rejects duplicate IDs, cycles anywhere, missing
destinations, non-ending dead ends, per-mode unreachable nodes, outgoing
ending edges, required-unit skips, unknown policy fields and invalid formal
routes. Bounds are 64 nodes, 128 edges, 512 ending paths and 4096 route visits
per mode; larger graphs return refusal rather than silently truncate.

## Measured verification

Commands run from the primary repository checkout:

```sh
python3 tests/activity_graph_contract_roundtrip.py
python3 tests/staged_production_roundtrip.py
python3 tests/activity_declaration_check.py
python3 tests/paced_view_roundtrip.py
python3 prototypes/activity-graph-contract-20260930/activity_graph.py
git diff --check
```

The graph suite passes 17 tests. The staged production suite passes 11 tests;
the activity declaration check and paced view roundtrip pass. The declaration
CLI prints the proposed JSON with revision
`sha256:f63f016581d91f2b0f77fd7beede068485df0f7ca4be3fbdaa8164f460cd1242`.
This is a proposal fingerprint, not a reviewer signature or accepted format.

The graph suite proves portable declaration roundtrip, frozen tuple identity,
unknown policy refusal, graph failures, exact staged-unit binding, one and two
case journeys, unopened/partial-child skip refusal, changed graph/bank/sitting
refusal, stale CAS, out-of-band sidecar conflicts, journal failure preservation,
one winner for competing choices, explicit cancel/resume, fresh-process restart
at the same branch/paragraph, valid endings, separate denominators and no new
response evidence from descriptive actions. Exam and diagnostic route identity
and rendered ending remain equal for correct and incorrect first responses.
Injected after-evidence/before-session-write failure requires canonical runtime
recovery and never causes graph-owned repair or rescoring.

One useful operational finding: `do_next` may update a sitting timestamp even
when serving a view. Graph checkpoint reads therefore use pure runtime
projection and the copied reconciliation check, rather than treating the
command as a byte-preserving read. Another: complete units can be ordered
differently by ordinary exam selection. The graph refuses that mismatch;
the multi-unit synthetic test requests the existing pair selector to preserve
the bound order. This does not authorize overriding runtime selection.

SHA-256 file fingerprints:

| File | SHA-256 |
| --- | --- |
| `prototypes/activity-graph-contract-20260930/activity_graph.py` | `d63f6c66c3799907d59d6bfe8e6dda89fca71d2769ac79f6b0852fd1c318d613` |
| `tests/activity_graph_contract_roundtrip.py` | `1ff0588ec45017db73240dc35747e146d270d759619f9b7c4913d96ba227fe55` |

## Recovery and minimum production gate

The durable presentation object is a journal-owned `component` in the
fictional temporary root. Runtime sitting/evidence remain the sole assessment
objects. Approved egress is none; all fixture content and journal events are
local. Graph/bank/session mismatches preserve files and instruct recovery of
the accepted originals, not automatic migration. Sidecar byte divergence is a
journal conflict. Stale CAS leaves the last applied revision untouched.
Journal undo/reconciliation remain existing primitives; no new undo algorithm
is supplied or independently verified here. Prototype repository recovery is
reversion of the single scoped plan commit under later Git authorization.

Accept D1-D5 in the owning format/product contracts before promotion. Then
assign exclusive parser/runtime/schema writers to register the graph
declaration, accepted revision/proposal journal route and public committed-unit
projection. Preserve complete-unit selection and runtime ordering. Bind
descriptive source occurrences through existing reading/lesson authorities,
with explicit rights, static transcript identity, checkpoints and revision
migration. Wire native controls to the existing client operation path and
verify restart, disclosure and loss reporting through that production surface.

No browser keyboard, physical touch, screen-reader, human preference or learning
transfer acceptance is claimed. Native control markup and complete text
transcripts are inspected by tests, but the preview has no wired HTTP handler.
No full preflight, push, shared production/schema/owner-doc edit, archive/app
build, install, release or real learner-data access occurred. The installed
sitting and fresh-build hold remain protected. Media playback stays deferred
until transcript/source-revision identity, pause/resume/cancel, offline/missing
media and keyboard/static recovery semantics are accepted.
