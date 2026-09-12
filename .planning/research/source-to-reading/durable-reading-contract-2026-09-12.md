# Durable reading activity contract

Date: 2026-09-12
Status: accepted for bounded implementation on 2026-09-12. Link 5B original
journal and source-companion transport passes twelve focused restore tests.
Private-note transport policy and final integration remain pending.
Owner: Weibao owns product choices and human acceptance.
Coordinator: the current Link 5B task owns implementation and STATE. Its
journal/source subset is stable pending the private-note policy question.
No successor has been dispatched. The earlier coordinator retains A4 evidence.

## Acceptance and current scope, 2026-09-12

After the recommendation to implement A3 with permanent reading and binding
identities, separate completion for repeated assignments, and history preserved
through rename and placement changes, Weibao instructed:

> work accordinlg

The same instruction explicitly invokes `daisy-chain-work` and
`efficient-agent-routing`.

This accepts LA-Q2 and the concrete delta including D3 for implementation.
It authorizes bounded continuation through the data, declaration and supported
UI integration gates. The collection label LA-Q1 can retain the prototype's
Resources label without a navigation redesign. The user did not authorize Git
mutation, real-course writes, parity-backend work or release.

The first unit is graph-only. The later declaration unit persists explicit
reported-read history. Exact scroll-position resume, multi-span ranges and
occurrence-private notes remain deferred as already stated in this contract.
Source-anchored learner notes reuse the existing notes authority. Human review
and real-course acceptance remain uncertified.

The sections below preserve the original proposal, findings and verification.
Their prior proposal-only scope and next-action statements are superseded by
this acceptance and the implementation chain at the end of this document.

## Scope and evidence

The September 12 parallel dispatch authorizes preparing this concrete delta
before deciding LA-Q1 and LA-Q2. It supersedes the September 10 handoff's
design-start ordering only. It does not accept a durable format. The September
10 visual direction permits continued design. Human accessibility and final
aesthetic checks remain deferred, not passed.

Only this file changes in A3. Production modules were sampled by symbol, not
read in full. Inputs were the September 10 implementation plan and handoff,
current STATE and parallel dispatch, SOURCE-TO-COURSE learner experience and
workspace boundaries, AGENT-WORKFLOW sections 1 through 6, and USER-VISION's
September 10 reading and September 11 examination-alignment entries.

| Finding | Verified implementation fact | Consequence |
| --- | --- | --- |
| F1 | `graph.SECTION_COLUMNS["Bindings"]` has no permanent binding ID or revision. `graph.add_binding` permits separate rows with the same endpoints. | An endpoint tuple or row number cannot identify a permanent binding. |
| F2 | `graph.parse_course` and `serialize_course` preserve unknown sections and columns. `course_graph.schema.json` is a closed object with optional table properties. | Add an optional section and properties, retain legacy bytes, and test schema compatibility separately from Markdown round-trip. |
| F3 | `evidence.lesson_complete_event` requires a bank basename, lesson slug and namespaced objectives. Its dedupe tuple has no occurrence. | Reusing it would conflate different assignments or invent a bank heading. Keep its behavior unchanged. |
| F4 | `evidence.append_event` is the one writer. `append_line_checked` deduplicates only within `DEDUPE_WINDOW_BYTES`. `events` warns and skips unknown event types. | Permanent replay needs a bounded extension inside this writer, not a surface check or a second log. Old consumers cannot project new reading evidence. |
| F5 | `notes.note_record`, `write_note_document` and `note.schema.json` already own note identity, owner, wording, objectives and source anchors. The writer replaces sidecar then Markdown separately. | Reuse notes. Do not promise pairwise crash atomicity from the existing two replacements alone. |

Canonical event schema is `schemas/response.schema.json`, despite its name.
`schemas/source_locator.schema.json` already connects source ID, fingerprint and
span IDs to medium-specific locations. The prototype's `occurrences`, `resolve`
and page script use temporary IDs and reset note/completion state on reload.

## Proposed product-contract insertion

Insert after SOURCE-TO-COURSE's learner-experience paragraphs only after review:

> A reading occurrence is one deliberate use of an accepted source range in a
> course. It has stable identity and immutable accepted revisions. Two
> occurrences may share the same source and binding without sharing completion.
> Each revision names its course, objectives, permanent binding revision,
> accepted source fingerprint, exact locator and assignment context. Opening a
> source and reading time imply no completion. Only an explicit learner
> declaration recorded by the existing evidence writer marks that occurrence
> revision as reported read. Reading declarations and learner notes never
> become response scores or mastery. Availability, staleness, acceptance and
> learner declarations remain separate states. Legacy courses gain no inferred
> activity or history. Accepted revisions and learner records survive restart
> and preserve reviewable conflicts and explicit export or restore losses.

LA-Q1 recommendation: use **Resources** for the learner-facing collection,
including optional readings and accepted learning artifacts. Keep **Sources**
as the source-management view inside it and preserve existing source IDs and
operations. This matches the accepted prototype while retaining precise source
administration. It is a presentation choice, independent of the format.

LA-Q2 recommendation: mint permanent binding identity plus immutable revision
identity in the existing Bindings table. Every occurrence pins that pair.
Weibao must accept this additive durable-format choice before implementation.
An endpoint hash fails when two deliberate claims share endpoints. A row index
fails on reorder. A whole-graph fingerprint would invalidate bindings on
unrelated edits. A copied binding without a permanent reference is only a
snapshot and cannot reliably resolve later review or conflicts.

## Concrete graph delta

Keep graph schema version 1 under the existing additive convention. Add optional
columns to Bindings: `binding_id`, `binding_revision_id`,
`supersedes_binding_revision_id`, `source_fingerprint`. Blank legacy columns
mean unversioned, not a generated identity. A material binding change appends
a new revision row, retaining the old row. Resolve by the pair, never by the
latest row, endpoints, path or title. Same pair with divergent content is a
conflict. Changed rights do not rewrite historical binding snapshots.

Add optional `## Reading occurrences` to the sidecar and `reading_occurrences`
to the graph schema. Use the existing Blueprint pattern: table columns
`occurrence_id`, `revision_id`, `document`. `document` is canonical
JSON for one closed record below. Other columns are human-readable projections
and must equal it when validating. `graph.py` owns parsing and validation.
No consumer reparses source or table bytes independently.

| Field | Proposed rule |
| --- | --- |
| `occurrence_id`, `revision_id` | Nonempty opaque IDs minted through existing identity helpers. Occurrence ID persists across revisions. Revision ID is immutable and unique within that occurrence. |
| `supersedes_revision_id` | Prior revision ID or null. Retain old rows. Reject cycles, missing parents and divergent same-ID rows. Concurrent sibling successors are conflicts until explicitly resolved. |
| `course_id` | Exactly the graph's `course_object_id`, not a course slug or pathname. |
| `objective_ids` | Nonempty unique existing graph objective IDs. These are not silently converted into the legacy namespaced assessment objectives. Objective migration does not transfer completion. |
| `binding_ref` | Closed object with `binding_id` and `binding_revision_id`. Referenced row must be a direct-reading treatment and its objective must belong to this occurrence. |
| `source_ref` | Closed object with `source_object_id`, `source_fingerprint`, `locator`, `range`. Must agree with the pinned binding revision. Locator retains the existing binding string. Range has the closed shape specified below. |
| `purpose` | Nonempty plain text defining the reading task. No embedded source copy or keyed assessment material. |
| `preparation_mode`, `path_role`, `learning_phase` | Explicit authored strings. Initial recognized values reuse P1's preread/prelearn/none, required-instructor-work/recommended-preparation/optional-enrichment and Ahead/Deepen/not-applicable. Unknown values remain visible but have no scheduling or gate authority. |
| `sequence_evidence` | Closed object with `status` (Published, Bounded, unknown) and `citation` (string or null). Published requires a nonempty authoritative citation. Bounded labels an estimate, not instructor instruction. |
| `assignment_provenance` | Closed object with `authority` (instructor, learner, proposed, unknown) and `citation` (string or null). Instructor authority requires a citation. No inferred deadline field. |
| `assistance_policy` | Closed object with `status` (specified, unknown), `citation` (string or null), `instruction` (string or null). Specified requires both strings. Unknown grants no assistance authority. |

Every new record requires all fields above. Nullable values express uncertainty.
The first unit supports exactly one normalized span per occurrence.
`range` is a closed object with `span_id` (nonempty), `locator_id` (nonempty
string or null) and `locator_sidecar_fingerprint` (fingerprint or null).
For native Markdown, both nullable fields are null and the existing normalizer
must resolve the binding string uniquely to that exact span on the pinned
source bytes. For adapted content, both are nonnull and the pinned locator
sidecar must join `locators[].id` to the same `span_id` and source fingerprint.
The whole normalized span is the range. Multiple spans, partial spans and
ambiguous headings are unsupported in the first unit, never silently widened.
Equality compares all source_ref fields exactly. The fingerprint identifies
accepted readable source bytes, including derived Markdown for an adapter,
while its locator sidecar retains original-medium provenance. Source movement
does not change identity. A regenerated sidecar requires reviewed revision.

Accepted revision status and reviewer belong to the existing operation journal,
not an independently writable completion or acceptance flag in this table.
The accepted head is reconstructed from the latest successfully committed,
validated course-graph revision in journal order, after journal recovery has
resolved interrupted operations. Each occurrence's unique unsuperseded row is
its head. All retained ancestor rows remain accepted historical revisions.
Draft rows stay outside the accepted graph. A proposed write with two successor
heads is refused before commit. Resolve competing proposals by accepting one
against the current graph fingerprint and leaving the other proposed outside
the graph. A manually diverged graph or missing commit provenance is a conflict
or acceptance-unknown state and cannot authorize a first declaration.
Enrollment and occurrence creation receipts identify the committed graph
fingerprint and the introduced row pairs. Those receipts are journal-backed
provenance, not another independently editable acceptance registry.
Changes to the occurrence revision record mint a new revision. Historical
completion remains inspectable but never transfers automatically. Title and
activation are excluded from that record under correction D3 below.

### D3: preserve declarations across display and placement edits

The initial proposal would have replaced A/RA1 with A/RA2 after a rename or
Now-to-Library move. Since projection looks up the current revision, E1 for
A/RA1 would have remained historical while the visible reading became
not-reported. That consequence is incorrect for an unchanged reading task.
This correction supersedes the earlier all-row-changes revision rule.

Add optional `## Reading placement` and graph property `reading_placement`
alongside Reading occurrences. Its closed rows contain `occurrence_id`,
`title` and `activation`. Each occurrence has exactly one placement row.
Title is nonempty plain display text. Activation recognizes Now and Library.
Unknown activation is preserved and shown as unsupported placement, never
silently scheduled. Placement is keyed by occurrence, not source or binding.
It contains no completion or acceptance flag and no second copy of purpose,
source range or assistance policy. The immutable occurrence rows no longer
contain title or activation. Plain Markdown readers can join the two tables
by occurrence ID.

Both sections remain canonical in the same course-graph file and use graph.py's
one parser. A metadata edit changes that file's accepted journal revision and
fingerprint through the existing compare-and-swap operation. It does not mutate
an immutable occurrence revision or its supersedes chain. Placement history
remains in accepted graph snapshots and journal receipts. Export and restore
include the placement section through those same snapshots.

Renaming or moving A between Now and Library therefore leaves A/RA1 and E1
unchanged. Library can hide A from the Now list but still shows its existing
reported-read state. Returning A to Now shows E1 again. There is no evidence
copy, new declaration, completion transfer or derived completion cache.
An outstanding first-declaration request with an old graph fingerprint still
gets the existing stale-request refusal and refresh path. The saved declaration
itself remains valid across the metadata edit.

Only title and activation are metadata-only in this first contract. Changes to
source, range, binding revision, objectives, purpose, preparation mode, path
role, learning phase, sequence evidence, assignment provenance or assistance
policy remain revisioned conservatively. Rights availability changes remain
independent and do not erase history. A rename cannot smuggle new instructions
into a label: changed task demand must be expressed in purpose or conditions
and use a new revision. Classification is checked by the graph operation's
field allowlist, never a client-supplied metadata-only flag.

If an edit changes both title and purpose, atomically update placement and
append a new occurrence revision. A failed compare-and-swap preserves both
old sections. A material range change requires a fresh declaration for the
new revision, even if the title stays the same. A reviewed rereading assignment
may also create a new occurrence so it remains independent of the old one.

A binding enrollment operation must target an exact row in an expected graph
fingerprint and assign IDs only after review. Duplicate legacy rows require
explicit selection. No global auto-migration is authorized. A new occurrence
cannot point at an unversioned binding. The enrollment and occurrence append
must be one journaled graph-file mutation, preserving all unrelated sections.

## Declaration and persistence delta

Add `reading_declared` to KNOWN_EVENT_TYPES and a closed branch in
`response.schema.json`, preserving event schema version 2 and all existing
branches. It must not enter the permissive fallback branch. Add an
`evidence.reading_declared_event` constructor, invoked by an authorized local
operation and persisted only with `evidence.append_event`.

Required fields: `schema_version`, `event_id`, `event_type`, `ts`, `session_id`,
`intent_id`, `base_retraction_id`, `actor`, `course_id`, `occurrence_id`, `occurrence_revision_id`, `objective_ids`,
`binding_ref`, `source_ref`, `declaration`, `dedupe_key`. Declaration is the
constant `read`. Actor is `learner` in this local single-learner unit.
Session ID is a server-generated action correlation ID, not an assessment
session and not part of replay identity. No `bank`, `score`, correctness,
mastery or duration fields. No automatic insertion into the lesson review queue.

The server resolves IDs, objectives, binding, locator and fingerprints from the
accepted revision. A request supplies occurrence ID, revision ID, expected
graph fingerprint and explicit declaration intent, not a trusted source path.
Validate acceptance, current revision and read rights before a first write.
Reject stale rendered requests. A previously recorded identical request returns
its original receipt even if rights have since changed, without reopening the
source or making a new declaration. Availability remains separately reported.

Dedupe key is SHA-256 of canonical JSON
`["reading_declared", course_id, occurrence_id, occurrence_revision_id, "read"]`.
Canonical encoding is UTF-8, `ensure_ascii=False`, compact comma/colon
separators, no trailing newline, and strings exactly as stored without Unicode
normalization. Proposed nested-record comparisons use sorted keys under the
same encoding. Source and journal fingerprints retain existing identity helpers.
Exclude time, timezone, source path, session ID and view state. The evidence root
is the learner scope today. Multi-learner log sharing remains unsupported.
The same key with conflicting occurrence, objective, binding or source fields
is an integrity conflict. Intent, retraction epoch and receipt metadata may
differ between fresh confirmations and are excluded from that comparison.

The writer must check the complete live history for this event family while
holding the same append lock. A disposable key index is allowed only with
freshness checks and a full-log fallback under that lock. Keep the existing
bounded response path unchanged. Appending in a surface after an unlocked
dedupe read is forbidden. A deterministic hash alone does not fix tail expiry.

`intent_id` is an opaque server-issued action token retained across retries.
Its server-validated confirmation context binds the occurrence revision and
`base_retraction_id`, the latest retraction of a declaration for this revision
or null. Store both fields in the event. A fresh explicit confirmation obtains
a new token against current retraction state. Check recorded intent IDs across
all history under the append lock before checking the live logical dedupe key.
An identical recorded intent returns its original receipt and current retracted
status. Reusing an intent with conflicting payload is refused. An unrecorded
intent whose base_retraction_id is stale is refused, even if its earlier retry
returned another intent's live receipt. Thus deduped requests cannot resurrect
completion after a later retraction. Tokens must be server-verifiable across
restart through the existing operation receipt mechanism, not client claims.
If confirmation context is lost, require a new explicit confirmation.

Use existing retraction events for an explicit learner correction. Projection
uses `evidence.live_events`. Retracting a declaration returns this revision to
not-reported. A later explicit declaration may then be recorded with the same
logical key. A recorded intent's replay returns its retracted receipt and cannot
resurrect completion. An unrecorded stale intent is refused. Only a fresh
confirmed intent against current retraction state may record a new declaration.

Completion is a derived lookup by course, occurrence and revision over live
events. Do not store a second mutable completed flag in graph, notes or browser
storage. Restart reconstructs it from the graph and log. Current event readers
skip unknown event types. They cannot currently project reading state. The new
compatibility view must show unsupported reading state when a required format
is unreadable, not not-started. No elapsed-time or scroll inference is permitted.

The narrow first implementation persists declarations only. Exact scroll or
last-opened resume is deferred. Return navigation carries the launching
occurrence and revision and validates them on return. An unsupported cursor
returns to the occurrence's beginning with an explicit notice.

## Rights, notes and recovery

Availability is a derived object independent of `reported-read` or
`not-reported`: available, rights-unknown, rights-denied, source-unavailable,
offline-remote, locator-missing, revision-conflict, unsupported, or error.
Resolve current rights through `course.rights_for_binding`. Do not treat the
binding's rights snapshot as current authorization. Read does not imply quote,
transform, remote-process, package, export or share. This unit has no egress.

A moved file with the same source ID and fingerprint resolves through the
registry. Divergent bytes never retarget a locator silently. An accepted new
range or source revision needs a new binding and occurrence revision. A lost
old source leaves an inspectable historical declaration and unavailable
content, not a fabricated completed current activity. Rights revocation blocks
new source access, but does not erase past learner declarations.

Reuse learner-owned notes with existing source targets, source fingerprint,
locator and objective IDs. Notes may be deliberately visible beside both
occurrences because their target is shared content. They remain one note with
one owner. Do not copy wording into each occurrence or share its completion.
Occurrence-private note anchoring is deferred rather than adding another note
format here. Anchor failure retains learner wording and objective attachment.
Do not put private wording in course graphs, evidence payloads or error logs.

Graph changes use expected fingerprint, validated temporary bytes, atomic
replacement and the existing journal. Evidence append is not a graph mutation.
Hold a compatible operation lock or revalidate under a shared serialization
boundary so revision acceptance cannot race a first declaration. Do not claim
multi-file atomicity from separate replacements.

Before any accepted receipt, evidence persistence must guarantee the line is
durably written. The current writer's sampled append path has no explicit
fsync, so crash durability needs implementation and fault-injection evidence.
A crash after durable append but before response must replay to the same event
ID. A partial trailing record must be detected and repaired or quarantined
through the evidence owner before append, never joined to the next JSON line.
Disk-full and denied writes return failure with last accepted state preserved.
No cross-file completion cache is needed to recover this unit.

Export and restore must inventory occurrence/revision pairs, referenced binding
revisions, graph fingerprint, source IDs and fingerprints, locator sidecars,
authorized source bytes, learner-note documents and live/retracted event
history. The manifest records included, omitted-by-rights, missing, unsupported
and conflicting objects individually. Preserve original IDs and timestamps.
Restore into a clean offline root validates checksums and references before
activation. A divergent same-ID object is a conflict, never an overwrite.

Missing source bytes permit historical declarations with unavailable content.
Missing evidence means reading history unavailable, not not-reported.
Missing graph or binding revisions leave orphan evidence visible in a loss
report and excluded from current projections. Missing notes or locator sidecars
are separately named losses. Unsupported versions remain byte-preserved and
read-only. Missing external source grants do not become granted on restore.
No clean offline restore or lossless packaging is claimed by this proposal.
Include the course object's journal history, required accepted graph snapshots,
enrollment receipts and declaration confirmation receipts in the manifest.
Restore verifies their fingerprints and reconstructs the accepted heads.
If acceptance provenance is absent, report acceptance-unknown and disable new
declarations. Lost confirmation receipts require fresh confirmation, never
implicit retry. Journal export applies existing rights and privacy screening
instead of copying unrelated object history.

## Illustrative synthetic fixtures and acceptance matrix

These are compact proposed-format examples, not production-valid fixtures.
`S1` abbreviates one SHA-256 fingerprint of synthetic tide-source bytes.
`B1/RB1` names a versioned direct-reading row targeting objective `O1`, source
`SRC1`, fingerprint `S1` and exact locator `source.md#reading-range`.

```json
{
  "shared": {"course_id":"C1","objective_ids":["O1"],
    "binding_ref":{"binding_id":"B1","binding_revision_id":"RB1"},
    "source_ref":{"source_object_id":"SRC1","source_fingerprint":"S1",
      "locator":"source.md#reading-range",
      "range":{"span_id":"SPAN1","locator_id":null,
        "locator_sidecar_fingerprint":null}}},
  "occurrences": [
    {"occurrence_id":"A","revision_id":"RA1","preparation_mode":"preread"},
    {"occurrence_id":"B","revision_id":"RB2","preparation_mode":"prelearn"}
  ],
  "live_declarations": [{"event_id":"E1","occurrence_id":"A",
    "occurrence_revision_id":"RA1","declaration":"read"}],
  "expected": {"A/RA1":"reported-read","B/RB2":"not-reported"}
}
```

| Gate | Input or interruption | Required acceptance observation | Current evidence |
| --- | --- | --- | --- |
| G1 isolation | Fixture above, mark A | B unchanged, shared source bytes unchanged, exactly one live declaration | P1 deterministic behavior only |
| G2 restart | Exit after E1, rebuild view without browser storage | Same E1 completes only A/RA1 | Required future production test |
| G3 replay | Retry from another session after more than the dedupe window of other events, plus two concurrent writers | Original E1 receipt, one live event | Current tail scan is insufficient |
| G4 revision | Accept A/RA2 pointing to B1/RB3 and new source fingerprint | E1 remains historical, A/RA2 not-reported, B/RB2 unchanged | Required future test |
| G5 rights | Revoke read after E1, retry E1, then first declaration for B | Existing receipt returned without access, B refused, availability denied | P1 covers refusal copy only |
| G6 legacy | Old graph and lesson_complete events with no occurrence metadata | Old bytes and event behavior preserved, no generated occurrence/history | Compatibility probe below |
| G7 torn/failed write | Kill before append, partial append, after durable append before receipt, disk-full | No false success, repairable tail, retry returns durable receipt | Required future fault injection |
| G8 restore | Clean offline restore with source omitted by rights, or log omitted | First case retains E1 and unavailable source. Second reports unknown history | Required future restore test |
| G9 corrections/conflicts | Retract E1, delayed retry, fresh learner action, duplicate divergent revision | Old retry cannot resurrect, fresh action may declare, divergence refused | Required future test |
| G10 notes | Source moves or disappears, occurrence removed | Learner wording and ownership retained, broken anchor explicit | Existing schema fit only |
| G11 metadata | Complete A/RA1 as E1, rename it, move Now to Library and back, then restart | Occurrence and revision stay A/RA1, same E1 remains reported-read, no new event, B unchanged. Placement survives restart from accepted graph. | Disposable projection probe passed, production persistence still unimplemented |
| G12 material range | Keep A's title, change its pinned source range and accept A/RA2, then restart | E1 remains only on A/RA1. A/RA2 is not-reported until a fresh declaration. A mixed title/purpose edit has the same revision requirement. | Disposable projection probe passed, production persistence still unimplemented |

## Verification and bounded next unit

Observed on 2026-09-12:

| Check actually run | Result and limit |
| --- | --- |
| `python3 tests/course_preparation_prototype_roundtrip.py` | Passed. Synthetic P1 isolation, recovery labels and unchanged accepted-state snapshot. It proves no restart persistence. |
| Disposable `probe.py` in the A3 temporary root | Passed: legacy graph byte roundtrip, unknown Reading occurrences section byte preservation, current closed lesson-completion schema, score absence, session-independent legacy key, and distinct proposed A/RA1, B/RB2, A/RA2 keys. No new production format was validated. |
| `python3 scripts/preflight.py --quick` | All ten executed gates passed. Python suite, clean-tree and JavaScript suite skipped by quick mode. CI-only schema pipeline not run. |
| `git diff --no-index --check /dev/null` against this file | Passed. Reviewed the actual new-file patch. |
| D3 correction: disposable `metadata_probe.py` | Passed G11/G12 proposal-model assertions after JSON save/reload. Rename and Now/Library/Now preserve RA1 and E1 without event mutation. Range change to RA2 has no declaration. This does not exercise production graph, journal or evidence persistence. |

D3 quick preflight was rerun after the correction. All ten executed gates
passed with the same three quick-mode skips. The earlier independent review
below predates D3 and does not certify this metadata correction. The correction
was locally inspected against the revision lookup and bounded synthetic probe.

The disposable probe imports the current graph, evidence and schema validator.
It serializes `graph.new_course`, appends an unknown Reading occurrences table,
and asserts exact parse/serialize equality. It validates an event from
`lesson_complete_event` with `response.schema.json` and compares the proposed
hash tuple across two occurrences and one successor revision. Generated JSON
and script live only in the A3 temporary root. These are compatibility and
identity probes, not production reading persistence or a second parser.

Concurrent edits were observed in journal.py, surfaces/ia.py, treatment
prototype paths and other lane artifacts. They were preserved. No failures
were observed in the executed gates, and no full integrated green is claimed.
Matrix rows remain requirements unless explicitly marked observed.

Independent review: Sol at medium effort performed a bounded read-only review
of identity, evidence and locator fit. Its initial three blockers were retry
identity after retraction, reconstructing accepted heads and precise range
identity. This revision addresses them with intent/epoch receipts, journal
provenance and unique-head rules, and a pinned single-span range. The reviewer
re-read those deltas and returned PASS for all three as a proposed contract.
It ran no tests and certified no implementation. Multi-span ranges and
occurrence-private notes remain explicitly deferred rather than lost ideas.

| Implementation seam | Exact bounded extension after acceptance |
| --- | --- |
| `graph.SECTION_ORDER`, `SECTION_COLUMNS`, `new_record`, `parse_course`, `serialize_course`, `validate_binding` | Optional versioned binding columns, immutable occurrence document section, occurrence-keyed placement section and cross-reference validation. `schemas/course_graph.schema.json` adds only optional legacy-facing properties with closed new record definitions. |
| `course._bind`, `bind_treatment`, `rights_for_binding`, `course_ops.run` | Reviewed enrollment and occurrence operations through journaled expected-fingerprint writes. Existing published operation schema and route registration must be extended together. |
| `evidence.lesson_complete_event`, `append_event`, `append_line_checked`, `live_events` and `schemas/response.schema.json` | New sibling scoreless constructor and projection, full-history reading replay under the writer lock, explicit durability and retraction behavior. Keep lesson completion semantics unchanged. |
| `notes.note_record`, `target_record`, `read_note_document` | Reuse source anchors and learner ownership. Occurrence-specific note formats and pairwise note-write repair are outside the first unit. |
| Prototype `occurrences`/`resolve`, source locator contract and existing export/restore owner | Replace simulated state only after server gates pass. Verify declared omissions and clean offline restoration before claiming portable reading history. |

Smallest next unit, after Weibao accepts LA-Q2 and the delta: graph-only
binding enrollment, occurrence revision and placement parsing/validation with
legacy byte-roundtrip, metadata preservation and conflict fixtures. No evidence
or UI writes in that unit.
Then a separate declaration unit must prove G2, G3, G5, G7 and G9 through the
one writer before any Mark read UI claims persistence. LA-Q1 may be reviewed
independently. Integration A4 can proceed with reading persistence unavailable.

Recovery for this proposal: remove this new file. No production or learner
state was changed. No commit, push, shared-index update or successor is made.
Next action: coordinator presents this concrete delta for Weibao's review.

## Implementation chain, started 2026-09-12

GOAL: Link 1 represents versioned bindings and reading tasks through the one
graph parser, retaining old graph bytes and rejecting ambiguous or conflicting
references. This is a foundation gate, not learner-visible persistence.

OWNER: The current coordinator owns this record, contract adoption, final diff
review and continuation. One Sol worker at medium effort owns graph.py,
schemas/course_graph.schema.json and focused graph tests. This bounded worker
keeps implementation and targeted verification together while the coordinator
records acceptance and prepares the dependent gate. No parallel code writer
or blanket audit is needed.

SCOPE: Optional binding identities and source fingerprints, immutable occurrence
documents, occurrence-keyed title/placement, pure graph helpers, schema and
cross-reference validation. Enrollment selects an exact legacy row explicitly.
No global migration or automatically inferred reading history is permitted.

DO NOT TOUCH: Existing recovery, course-resume and table-export lane patches.
Link 1 adds no disk operation, evidence event, note format, source read, route,
scorer or UI write. No real course, external service, commit, push, branch
switch, release or parity-backend work is authorized by this packet.

CONTEXT: A4's final full run resolved course-ops and file-fault cleanup and
retained the known local-model parity unavailable and expected dirty-tree
failures. Actual browser practice restart/resume passed. Reading declarations
and note controls were unavailable on the exercised route. Those results are
baseline evidence, not a pass for this new graph delta.

EVIDENCE: The September 10 prototype precedes this format adoption. This
document's G1 through G12 retain explicit production requirements. The current
worker must return its actual patch and targeted results. This link's results
will be appended here rather than duplicated into another audit report.

AUDITS: The original independent proposal review resolved receipt/retraction,
accepted-head and exact-span concerns at the proposal level. D3's earlier
disposable check is not a production pass. The bounded readiness check below
is reconciled against the accepted clauses and current ownership. No whole
vision or whole-codebase audit is claimed.

| Readiness obligation | Current disposition and verification owner |
| --- | --- |
| Contract translation and provenance | SOURCE-TO-COURSE now carries reading identity, declaration authority and D3. IL-20260912-01 records accepted direction. This document retains exact fields and the user's continuation. |
| Dependency and authority | Graph is a pure model. The successor operation owner checks journal acceptance, source bytes, locator and current rights. The evidence owner records scoreless declarations. UI and notes consume those authorities. No cycle or second completion store is introduced. |
| Prototype, migration and failure state | The existing workspace prototype precedes the schema. Legacy graphs receive no generated IDs. Missing or conflicting references are refused. Unknown presentation modes remain visible without authority. Source unavailability and history remain separate in later projections. |
| Compatibility and sequence | Link 1 proves structural roundtrip and D3 identity preservation. Link 2 adds journaled operations with source/locator checks. The next declaration gate proves restart, replay, retraction and failed-write behavior before UI uses it. Final integration owns the single full candidate preflight and offline-restore evidence. |

NEXT ACTION: Implement and verify the graph-only unit, then inspect the actual
diff. Expand only the next journaled-operation packet after this gate passes.

GATE: New graph regression plus existing graph and affected binding suites
pass. Require explicit enrollment, two tasks sharing one binding, independent
immutable revisions, metadata-only identity preservation, missing/cyclic/
branching lineage refusal, source/binding mismatch refusal, malformed closed
records, and legacy plus unknown-field byte preservation. Run quick preflight
at handoff. Source-byte and journal acceptance are explicitly outside this gate.

RETURN: Changed paths and signatures, exact test outcomes, reviewed diff,
remaining limitations, baseline failures, reversible patch boundaries and one
next action. The coordinator alone may create the next task after the worker
stops and this gate is stable.

Recovery: revert only this link's named diff, leaving prior A1/A2/A5 work
intact. No learner objects are mutated by Link 1. The documentation's inspected
base fingerprints were STATE `e8b59a42325bfbf8510f71759749da5f28eb98a318d7b87f3fad117b135f79bf`,
SOURCE-TO-COURSE `4d3544b07294b2626c96adaddb337161507dab80191cf93ef34cf4214e7dfd8d`,
IDEA-LEDGER `dede27d8aaf9c7efcd2dbda97305992cea3c12b0e98b1a662df5f6a67a6567d4`,
and this original proposal `2634dec220a4b20a3127b90901b96470cb321fc4910a82eb3d33b487a7d4c395`.
Context-checked patches preserve the preceding evidence and unrelated edits.

### Link 1 implementation result, 2026-09-12

Link 1 is implemented and verified on the current uncommitted candidate.
The Sol worker stopped after its named implementation and focused tests.
The coordinator inspected the new graph logic, schema delta and regression
assertions, fixed the last layout and no-op cases, and reran the narrow gate.
Large graph.py was sampled around changed symbols and its diff. Unchanged
graph functions were not comprehensively reviewed.

Changed implementation paths: graph.py, schemas/course_graph.schema.json,
tests/graph_roundtrip.py and new tests/reading_graph_roundtrip.py. Contract
adoption also changes this document, SOURCE-TO-COURSE, IDEA-LEDGER and STATE.
All prior recovery, resume and table-export edits remain outside this link.

| Check actually run on the final code candidate | Result |
| --- | --- |
| `python3 tests/reading_graph_roundtrip.py` | Passed. Legacy empty/populated golden fixtures, unknown columns and sections, enrollment and later row alignment, two tasks sharing a binding, metadata roundtrip, material revision, malformed input, lineage and reference conflicts, and closed schema validation. |
| `python3 tests/graph_roundtrip.py` | Passed, including the amended additive public API list. |
| `python3 tests/binding_roundtrip.py` | All five checks passed. Python and served binding operations retain the one rights-gated path. |
| `python3 scripts/preflight.py --quick` | All ten executed gates passed. Full Python, JavaScript and clean-tree checks skipped. CI-only pipeline and human gates not run. |
| `git diff --check` | Passed. |

Review reconciliation:

| Finding | Disposition and owner |
| --- | --- |
| L1-F1: new-code-only legacy test missed empty old table widening | Fixed. Parser retains authored section-column metadata. Actual golden pre-change empty and populated tables preserve their bytes. |
| L1-F2: enrollment discarded unknown-column layout for later additions | Fixed by the coordinator. Enrollment retains the first row's authored layout, and an added unversioned row survives reparse with its locator and blank identity intact. |
| L1-F3: unsafe indexes, table text and nested objective values | Fixed. Negative/bool indexes, noncanonical table cells and malformed objective values are refused with the original graph intact. |
| L1-F4: empty or unchanged occurrence updates minted a new revision | Fixed by the coordinator. A new occurrence revision now requires changed task content. |

The original F1 is resolved at the graph-representation layer. Durable
enrollment still belongs to Link 2. Original F2's compatibility claim now has
production graph fixtures. The decoded canonical occurrence object is validated
by graph.py because its outer Markdown table cell is a JSON string. The schema
publishes the closed decoded definition as well as the outer row shape.
Original F3 through F5 remain owned by the declaration and notes successors.
No lesson-completion, evidence-writer or note-write behavior changed here.

G1, G6, G11 and G12 have graph-layer evidence only. No live declaration E1,
restart receipt, source access, locator resolution, note save or offline restore
is claimed. G2, G3, G5, G7, G8, G9 and G10 remain dependent production gates.
The earlier A4 parity-unavailable and dirty-tree results remain the full-run
baseline. This quick pass does not establish repository-wide green.

Final reviewed code fingerprints:

| Path | SHA-256 |
| --- | --- |
| graph.py | `2e6aee802d045deb9358e310af283f02aee61ba21d35b7ccee5fd2dacd92054b` |
| schemas/course_graph.schema.json | `5d292a797296eea33a02dd95e46a71d2040beb037c7bd052310c6e27cd10d189` |
| tests/graph_roundtrip.py | `441759a443838882533f8a7f6e0bccaedc3d922f69c597299896ec9276f8b36f` |
| tests/reading_graph_roundtrip.py | `33867f1c030765785115db5e801522f69c8bc4db439f4dd54f6d79c19813d53b` |

Next action: dispatch Link 2 below in the same local checkout so it receives
the verified uncommitted candidate. No code writer remains active in Link 1.

### Link 2 packet: journaled reading operations

Link 1's reviewed graph gate passed. This is the ready successor packet.

Dispatch: task `01a095cf-3727-7281-a5db-d03a35f4af8b` was created as
**Implement journaled reading operations** in the same saved local project
with medium reasoning and no model override. One status check confirmed it
active and implementing this packet. It now owns code, this record and STATE
for Link 2. The Link 1 coordinator stops edits after this dispatch record.

GOAL: A synthetic local course can create, revise and rename or place a reading
task through published operations, with exact source validation and one
journaled course-graph mutation per accepted action.

OWNER: The successor is the sole implementation and integration owner for its
link. It also owns this record and the current STATE pointer after dispatch.
Weibao retains material product changes and human acceptance.

SCOPE: Extend course.py, surfaces/course_ops.py, the published course-operation
schema, its itembank.py CLI declarations, and narrowly required daemon route
registration. Add focused reading-operation tests. Reuse graph helpers,
auditor.normalize_source, the source registry, current rights and locator
sidecars. Changes to graph helpers are allowed only for a demonstrated defect
in the passed Link 1 gate. Inspect relevant symbols, not whole large modules.

DO NOT TOUCH: Runtime scoring/disclosure, evidence writer, note formats,
prototype design, real courses, source adapter generation, external services,
parity backend, unrelated dirty patches, Git history or releases. This link
does not expose a Mark read control or claim saved completion.

CONTEXT: course.write_course already uses journal.commit_operation.
surfaces.course_ops._edit_sidecar is the closest existing operation pattern,
but its optional fingerprint fallback must not weaken the new reading request:
require the rendered expected fingerprint for every accepted reading write.
The existing journal remains recovery authority. No new operation journal or
source parser is needed.

NEXT ACTION: Reuse Link 1's verified helper signatures and create one synthetic
registered local source, objective and direct-reading binding. Reproduce the
source-resolution and compare-and-swap requirements before adding operations.

GATE: Test one atomic enrollment-plus-occurrence creation from an explicitly
selected binding row. Verify shared binding references, immutable material
revisions and combined metadata/material edits. Validate uniquely resolved
single-span native and already-adapted sources against pinned bytes and locator
sidecars. Refuse stale fingerprints, missing acceptance provenance, missing or
ambiguous locators, mismatched source bytes, denied or unknown read rights,
outside-root sources, and attempted ancestor mutation. Failed actions preserve
prior graph bytes. Restart reconstructs the accepted occurrence heads from
course graph and journal. Undo restores the exact prior graph. Published
schema, CLI and HTTP operation contracts agree and legacy routes still pass.
Report unsupported source ranges explicitly. Run affected narrow checks and
quick preflight, then review the actual diff. Do not repeat the full repository
suite before the final integrated candidate unless a concrete failure requires it.

AUDITS AND EVIDENCE: The current document owns graph acceptance and the earlier
proposal findings. The A4 integrated-study-journey report owns the baseline
recovery/resume results. Reconcile results here, preserving failed observations.
Technical source resolution and journal provenance remain new checks for this
link, not inherited passes from the graph-only unit.

RETURN: Operation signatures, changed paths, actual checks and source-resolution
observations, receipt and recovery behavior, known failures and unrun gates.
Once stable, prepare the scoreless declaration unit under this contract's G2,
G3, G5, G7 and G9. Apply daisy-chain-work, efficient-agent-routing and
evidence-gated-handoff to any successor. Continue only for the accepted A3
outcome through declarations, supported notes/UI and final restore/integration.
Keep exact cursor resume and other explicitly deferred breadth deferred.


### Link 2 implementation result, 2026-09-12

The journaled reading-operation packet is implemented and locally reviewed.
The four Link 1 graph fingerprints still exactly match their recorded values.
No Link 1 graph helper changed. Existing recovery, resume, exporter, prototype
and concurrent vision edits remain in the shared dirty checkout.

Published operations are `create_reading`, `revise_reading` and `place_reading`.
Their HTTP paths use hyphens under `/api/course/`. Their CLI twins are
`itembank course create-reading`, `revise-reading` and `place-reading`.
Every write requires `expected_fingerprint`, spelled `--expect` on the CLI.
Create accepts closed `values`, title, activation and either an explicit
zero-based legacy `binding_index` or an existing permanent `binding_ref`.
Enrollment and creation are one graph write. Revise requires the occurrence
and current revision IDs plus closed `changes`. Its optional `revise_binding`
appends a binding revision from changed source_ref fields in the same write.
It cannot rewrite an ancestor. Title and activation may accompany material
changes, but must be supplied together. Place accepts only identity, title,
activation and the expected graph fingerprint.

The engine returns the committed graph fingerprint and revision, exact applied
journal entry ID, occurrence/revision document and binding pair. That entry
can be passed to journal.undo for exact restoration. These are receipts over
the existing journal, not a second acceptance registry. No declaration or
completion record is written.

`course.accepted_reading_graph` checks the current graph against the journal's
reconstructed registry and matching prepared/applied provenance before a write.
`course.validate_reading_source` checks approved-root containment, current
journal read rights, source identity and fingerprint, unresolved operations,
and the one selected span from auditor.normalize_source. Native locators must
uniquely match a span ID, `line N`, exact span text or a normalized heading path.
A heading names only its own span here. A section or multi-span selection is
explicitly unsupported, never widened. Already-adapted sources require a
locator ID equal to the binding locator, matching source/span joins, the pinned
sidecar fingerprint, schema validity and exact journaled companion bytes.
A changed sidecar or missing acceptance provenance is refused.

The CLI declarations actually live in surfaces/cli.py, reached by itembank.py.
That file was changed instead of placing declarations in the entry wrapper.
A narrow journal extension was necessary for current rights: an optional
trusted read-only precommit validator runs inside the existing write lock.
Without it, source validation followed by graph commit allowed a journaled
rights change between the two. The new reading test proves that competing
rights writes receive journal.busy while this validator runs. Existing callers
retain the default behavior. No source adapter generation changed.

| Check actually run | Result and limit |
| --- | --- |
| `python3 -W ignore::ResourceWarning tests/reading_ops_roundtrip.py` | Nine synthetic tests pass. Atomic enrollment, repeated assignments sharing a binding, immutable material and binding revisions, combined edits and refusal, placement, restart in a new Python process, exact undo, stale/missing graph provenance, unsupported and ambiguous native spans, source bytes and rights, escaped sources, adapted locator joins, sidecar changes, failed graph replacement, locked rights check, live HTTP creation and CLI placement. |
| `python3 tests/course_ops_roundtrip.py` | Pass. Legacy operations and new schema/CLI required-field agreement. |
| `python3 tests/journal_roundtrip.py` | Pass. Existing recovery and rights behavior with the additive callback. |
| `python3 tests/mcp_roundtrip.py` | Pass. Generated tool table, closed schemas and shared dispatch. |
| Reading graph, graph, binding and source_adapters roundtrips | All pass on the current candidate. Adapter suite exercises existing generation as regression coverage only. |
| `python3 scripts/preflight.py --quick` | All executed gates pass. Full Python, JavaScript and clean-tree gates remain skipped. |
| Actual diff review and `git diff --check` | Pass. New course operations, request definitions, CLI, route registrations and the bounded journal hook were reviewed. Large modules were inspected by symbol and diff, not read in full. |

Initial checks caught missing CLI requiredness for `--expect`, an unsupported
schema minProperties keyword and a reused journal iterator in provenance
validation. Those were corrected and the affected checks rerun. The adapted
sidecar assertion was reconciled with the final explicit companion-provenance
check. These are resolved observations, not pending findings. ResourceWarning
suppression only avoids existing resources.py unclosed-read warnings in the
new unittest runner. It does not skip tests.

Reconciliation: Link 1 identity evidence is unchanged. Link 2 now proves graph
operation persistence and recovery. G2/G3/G5/G7/G9 declaration durability,
G8 offline restoration and G10 supported notes remain open for their own units.
G11/G12 have graph-operation evidence only, not saved learner declaration
proof. No Mark read UI, learner-note persistence, full-repository green,
human acceptance or real-course acceptance is claimed. No Git mutation ran.

Final Link 2 code fingerprints:

| Path | SHA-256 |
| --- | --- |
| course.py | `5156b5d3e2a62d5df702b34ff40c8e54f118f38593556b07cdb04fab30ef71bb` |
| journal.py | `12cbf03c286f47c8975f9be1e438837e7888fe1658b3161895ba670613432a47` |
| schemas/course_operation.schema.json | `dafc09a26e3c42de461cad680f446abc52da2d5a57768753956d6a80cab340c5` |
| surfaces/cli.py | `70264b2b1f904d87fa6f093de5257d97882cb1f593730571e2262c8d3e846927` |
| surfaces/course_ops.py | `ce2d3a3ff2e2082e6803b79c9e8a0a888a6b9452bd0c316aee0b567d2d3093f5` |
| surfaces/daemon.py | `d924595c8a4f42374045c51372c525f6558fd0274122a9584e333ddcd6bd68c9` |
| tests/reading_ops_roundtrip.py | `a0229dad9a66f8ec334809c5adb4054b92fa7dd4a7b19d75103a99ffa565666e` |

### Link 3 packet: scoreless reading declarations

GOAL: A synthetic local learner can explicitly declare one accepted reading
revision read, permanently replay that action after restart, retract it and
make a fresh confirmed declaration without inventing scores or completion for
another occurrence. Durable success must survive the specified failed writes.

OWNER: The successor is the sole implementation and state owner for Link 3 in
this same local checkout. Weibao owns material new decisions and human review.
Use one implementation owner, the configured default primary model and medium
effort. Do not delegate by default.

SCOPE: The existing evidence writer and event schema, a bounded reading
confirmation/declaration operation in course.py or its direct domain peer,
course operation schema and dispatch, CLI and minimal daemon registration,
and focused declaration tests. Reuse Link 2 accepted graph/source checks and
journal authority. Read this contract's Declaration and persistence delta,
rights/stale/retraction rules, G2/G3/G5/G7/G9 and Link 2 result before edits.
A trusted validator may need the existing evidence append lock to keep replay
and first-write checks atomic. Keep the response event path unchanged.

DO NOT TOUCH: Runtime scoring/disclosure, existing response semantics, source
adapter generation, prototype design, learner UI or Mark read controls, note
formats, real courses, unrelated dirty patches, external services, parity
backends, Git operations or releases. Do not rework Link 1 or Link 2 without a
specific failing gate. Exact cursor resume, multiple spans, occurrence-private
notes and human/real-course acceptance stay deferred.

CONTEXT: The candidate is uncommitted, so use the saved project directly in the
same local checkout. The new source checks use journal-backed state and reject
missing prepared/applied graph provenance. Receipts carry entry_id, graph
fingerprint and exact occurrence/binding pairs. Locators are intentionally
single-span. Imported sidecars must already be accepted journal companions.
The evidence writer, not a surface, must own full-history replay under its
append lock. Existing receipts must replay without reopening a now-denied or
missing source. A first declaration still requires accepted current graph,
current revision, current rights and exact source validation. A new intent
binds the retraction epoch. A delayed old retry cannot resurrect a retraction.
Read the complete accepted delta for fields and canonical dedupe encoding.

NEXT ACTION: Locate evidence.append_event, append_line_checked, events,
live_events and the existing retraction/lock helpers by symbol. Reproduce the
tail-window replay and failed-append gaps with synthetic focused tests before
extending the one writer. Publish the closed scoreless event branch and
explicit confirmation context, preserving response and lesson-complete paths.

GATE: Prove restart reconstruction, full-history replay beyond the response
dedupe window, concurrent identical requests, conflict refusal, retraction,
delayed retry refusal and fresh confirmation, rights revoked after receipt,
first-write refusal under denied/unknown rights, stale revision and graph
refusal, no scores or mastery fields, separate repeated assignments, and
failed/torn append plus post-durable-append retry behavior. Validate captured
events against response.schema.json. Run only affected narrow checks and quick
preflight and review the actual diff. Do not run the full repository suite
until final integrated A3 unless a named failure requires it.

AUDITS: This document owns Link 1 and Link 2 evidence and resolved observations.
The A4 integrated-study-journey report remains the full-run baseline with
local-model parity unavailable and expected dirty-tree failures.

RETURN: Changed paths, operation signatures, event and confirmation receipt
behavior, actual tests, unresolved risks and explicitly unrun gates. Append
results and reconciliation here and update STATE's current pointer while
preserving older evidence. Once stable, prepare the supported source-anchored
notes/UI unit, then offline restore and final integration. Apply
$daisy-chain-work, $efficient-agent-routing and $evidence-gated-handoff to each
successor, preserve scope and check once that it is active. Stop when A3 is
complete, a material decision/external state is needed, or the same blocker
survives three links. Do not turn deferred gates into passes.


### Link 3 implementation result, 2026-09-12

Scoreless declarations now persist through the existing evidence writer.
`reading.py` is the direct domain peer so course.py retains its structural
separation from evidence and its migration behavior. Link 2 course.py,
journal.py and tests/reading_ops_roundtrip.py hashes remain unchanged.
No runtime scoring or disclosure code changed. All unrelated dirty edits
remain in place. No Git mutation, real-course write or external service ran.

The closed `confirm_reading` request requires course_id (the local route slug),
occurrence_id, revision_id, expected_fingerprint and confirmation=`read`.
The closed `declare_reading` request requires the same context plus intent_id
instead of confirmation. HTTP paths use `/api/course/confirm-reading` and
`/api/course/declare-reading`. CLI twins use `course confirm-reading` and
`course declare-reading`, with `--expect`, `--occurrence-id`, `--revision-id`,
and `--confirmation read` or `--intent-id`. Both support `--json`.
The evidence event's course_id is the permanent course object ID, not the slug.

Confirmation resolves accepted graph facts and source rights under the journal
lock, then captures the current correction epoch under the evidence lock.
It writes one existing director declare-intent checkpoint with a server-issued
operation ID, exact event and expected graph fingerprint. The trusted optional
checkpoint/lock-held parameters on director.begin_operation are not request
fields. The event time records explicit confirmation time. Event and action
correlation IDs are minted there and remain immutable across declaration retry.
The checkpoint is confirmation context, not a second completion store.

Declaration verifies that checkpoint under the journal lock and calls
`evidence.append_event(..., precommit=trusted_validator)`. Its reading branch
holds the existing evidence lock through strict full-history inspection,
intent replay, correction epoch validation, logical-key comparison and append.
First writes revalidate the accepted current graph, current occurrence head,
source bytes, exact single span, locator acceptance and current read rights.
Existing receipts replay without source access or current-graph validation.
The same logical key cannot change source/objective/binding payload even after
retraction. A recorded old intent replays its original retracted event. An
unrecorded stale intent is refused. Fresh explicit confirmation may create the
next event against the current epoch. The response dedupe window is unchanged.

The shared append-line path now loops over short writes, fsyncs evidence and
POSIX directory entries, and truncates back to the prior offset on a failed
write or sync. Before append, an unterminated tail is durably quarantined to
an exclusive `evidence.jsonl.torn-<id>` file and removed from the active log.
Malformed complete records and unsupported history refuse reading writes.
Replay fsyncs complete existing records too, covering a process that died
between its write and sync. These are tested macOS filesystem guarantees,
not a hardware power-loss or Windows directory-durability certification.

`evidence.reading_state` derives state through live_events after a strict
compatibility check. Missing history reports unavailable. Unsupported or
conflicting history reports unsupported. Missing history after confirmation
cannot silently recreate completion. Lost confirmation receipts require a
fresh explicit confirmation. `reading.availability` separately reports current
registry/filesystem availability without reopening source bytes. Its returned
`source_bytes_rechecked: false` deliberately does not attest current content
integrity. A first write has separately performed the full source validation.
The next UI must use the full source validator before displaying source text.

| Check actually run | Result and limit |
| --- | --- |
| `python3 -W ignore::ResourceWarning tests/reading_declarations_roundtrip.py` | All 14 synthetic tests pass. Includes a log exceeding the real 8 MiB response dedupe window, new-process replay, concurrent processes, original event identity, separate assignments, D3 placement, revision changes, denied/unknown rights, missing sources/history/confirmation receipts, retraction epochs, conflicting live and retracted payloads, closed scoreless schema, lock serialization, partial/disk-full/denied/fsync failures, process exit mid-line, process exit after durable append, failed replay sync and recovery, and real HTTP confirmation plus plain CLI declaration and HTTP replay. |
| `tests/evidence_roundtrip.py`, `tests/lesson_retention_roundtrip.py`, `tests/protocol_roundtrip.py` | Pass. Existing response, retraction, evidence/index, lesson-completion queue, event versions and published schema behavior remain compatible. |
| `tests/director_roundtrip.py`, `tests/journal_roundtrip.py` | Pass. Existing operation protocol and recovery behavior remain compatible with the trusted checkpoint hook. |
| `tests/course_ops_roundtrip.py`, `tests/mcp_roundtrip.py`, `tests/reading_ops_roundtrip.py` | Pass. Closed requests, all route registrations, CLI required fields, shared dispatch and Link 2's nine tests. |
| `python3 scripts/preflight.py --quick` and `git diff --check` | All executed gates pass. Full Python/JS and clean-tree gates intentionally remain unrun at this link. |

Review resolved three concrete observations: repeated-assignment fixtures must
reuse a versioned binding rather than enroll it twice, daemon route registration
must update API_ROUTES/ROUTE_CLI/SURFACE_PARITY together, and plain CLI output
must handle declaration receipts rather than expecting graph-write fields.
Further review added missing-history refusal, replay sync, and logical payload
immutability after retraction. The final 14-test run includes these repairs.
Large modules were reviewed by symbol and actual diff rather than whole-file
reads. The new domain module and test were read in full. No independent agent
or human review was performed. Full-history reading scans are O(log size),
with no disposable index added in this bounded unit.

Reconciliation: G2/G3/G5/G7/G9 now have declaration-level evidence. G1/G4/G11/G12
also have live declaration projection evidence. This does not close the
supported learner UI, source-anchored notes, G8 offline restore, real-course or
human accessibility gates. A4 remains the full-run baseline with local-model
parity unavailable and expected dirty-tree failures. No repository-wide green
is claimed. Original proposal and Link 1/2 evidence remain preserved above.

Final Link 3 file fingerprints:

| Path | SHA-256 |
| --- | --- |
| reading.py | `8ac8d5f617776b1786ef42465ea8dc90d6198e48cb67ecbadb49ec05de25dcbe` |
| evidence.py | `b44d912f6fe42fe012e6f2eaa9c7c9fecb7c13e5fa75468ba9333db671da02ef` |
| director.py | `75f6e107f6295f89e5050f04369c1a69bc28cd8b0753b8b70ed51ae305836872` |
| schemas/response.schema.json | `a46d93afca6c327d15682ad184a9453c62a296b941506d5afb3081c693f1ab28` |
| schemas/course_operation.schema.json | `b83b94f4f6d1b2e2c0c5c7ae98d233eea439c89c34866cb17750c7b7748f9c0e` |
| surfaces/course_ops.py | `97588b42b7163bd4065ec30f1a39e6a4c6d40d094ed989c07d952f0a85b8017e` |
| surfaces/cli.py | `cc2bea6fd9c5e311248b3c6e2bad1cbc699e7589f608417c3d84a48ab659849f` |
| surfaces/daemon.py | `adabe4c6a63a7ef6ed7016f4797ce1cdd2c3133cc53d994eba1fef2fc2aba83f` |
| tests/reading_declarations_roundtrip.py | `42abb1d206fdc8d4f5ce5dcfa94212e602b00fa08c7886d62ae29fb46dde0b30` |


### Link 4 packet: supported source-anchored notes and reading UI

GOAL: One synthetic learner journey opens an accepted single-span reading from
its occurrence, explicitly reports it read, saves a source-anchored learner
note, leaves and restarts, and sees the same declaration and note through a
supported local UI. A repeated assignment shares source notes but retains its
own completion. No UI says saved before the durable owner returns success.

OWNER: The successor is the sole implementation and STATE/contract owner in
this same local checkout. Weibao owns material product decisions and human
acceptance. Use the configured default primary model at medium effort with
one implementation owner and no delegation by default. Apply
$daisy-chain-work, $efficient-agent-routing and $evidence-gated-handoff.

SCOPE: Read Link 3's result and this contract's notes, rights and recovery
sections. Integrate the accepted September 10 study-desk direction into the
smallest supported reading route and course entry. Locate the accepted local
prototype before drafting a replacement. Use existing presentation primitives,
reading.py, course accepted/source validators, graph identities, evidence
projection and notes.py/notes schema. Add bounded same-origin local operations
and CLI parity where required. Changes to notes persistence must retain its
existing schema, identity, owner and source target. Audit notes.write_note_document
before promising saved state: it currently replaces sidecar and Markdown
separately without durable pairwise acceptance. Close the actual save/recovery
gap through the existing journal/companion authority, without inventing a
second note format or evidence log. A sampled note save fault must preserve
learner wording and expose recovery instead of claiming success.

DO NOT TOUCH: Runtime scoring/disclosure, existing response semantics, source
adapter generation, other prototypes or their design work, real courses,
parity backends, external services, unrelated dirty changes, Git operations or
release files. Preserve current recovery, resume, exporter and vision edits.
Exact cursor resume, multiple spans, occurrence-private notes and human or
real-course acceptance stay deferred. Do not add a general navigation redesign.
Resources may retain its accepted label. No new rights or remote processing.

CONTEXT: Source access requires the full current validator before rendering.
The declaration receipt's availability metadata intentionally does not reopen
or revalidate bytes. Completion is only a live-event projection for the exact
course/occurrence/revision, not graph state or browser storage. The UI must keep
one server-issued intent token on retry and request fresh confirmation only
for a new explicit learner action. A retracted receipt must not display read.
Missing/unsupported history is not not-started. Navigation carries and checks
occurrence/revision context. Without cursor support, return to the beginning
with explicit copy. Shared source notes must be labeled as such and never
copied into both assignments. Missing anchors retain wording and objectives.
Private note wording cannot appear in course graphs, evidence or error logs.

NEXT ACTION: Verify ownership and Link 3 hashes, locate the accepted prototype
and supported course route, then read notes.note_record, target_record,
write_note_document/read_note_document and relevant presentation controls by
symbol. Implement the bounded persisted journey using the existing authorities.

GATE: Focused synthetic tests prove separate assignment completion, restart,
retraction and retry rendering, stale rights/revision refusal, missing-history
copy, note identity/wording retained through source move/missing anchor and
occurrence removal, failed note save/recovery, and unchanged assessment behavior.
Exercise the actual local browser UI for open/read/explicit declaration/note
save/leave/restart and capture the verified route and observations. Include
keyboard and narrow-viewport browser checks without calling them human
screen-reader/touch/zoom acceptance. Run affected narrow checks and quick
preflight, review actual diffs, and append the result and reconciled limitations
here. Preserve A4's baseline and defer full candidate preflight to final A3.

AUDITS: This document owns the accepted contract and Link 1/2/3 evidence.
The original prototype remains design evidence. No saved audit establishes
human acceptance. The note writer's separate replacements are a known gap to
resolve within this unit before saved-note UI claims persistence.

RETURN: Exact changed paths, local route, declarations/notes authority and undo,
tests and actual browser observations, open limitations and next gate. Update
STATE without erasing prior evidence. At this stable gate, prepare and create
the offline restore/final integration successor with the same named skills,
same local checkout, exclusions and one active-state check. Include required
graph/source/locator/note/journal/confirmation/evidence histories in its packet.
Stop once A3 is complete, a material decision/external state is needed, or the
same blocker survives three links. Do not turn deferred gates into passes.


### Link 4 implementation result, 2026-09-12

The supported local journey now opens through course Learn at
`/course/<course_id>/reading/<occurrence_id>/<revision_id>`. It uses the
September 10 study-desk direction from `prototypes/course-preparation`, the
shared presentation shell and primary controls, a named assignment path,
editorial source column, purpose, and contextual private notes. The prototype
files were not changed. Placement titles distinguish repeated assignments.

`reading_desk.snapshot` requires journal-accepted graph bytes and calls
`course.validate_reading_source` before returning verbatim source content.
Unavailable or stale content is withheld independently of historical reading
state. The route pins occurrence and revision. Old or removed occurrences
keep course notes visible with explicit anchor-loss copy. Return starts at the
beginning and says so. This unit adds no cursor store.

The browser calls the existing `confirm_reading` and `declare_reading`
authorities. One server-issued intent is retained when a declaration request
fails. Successful display comes from the current `evidence.reading_state`
projection, so a retracted receipt cannot alone produce reported-read. Notes
and completion do not enter browser storage. Read history missing or
unsupported remains explicitly unavailable rather than not-started.

`reading_view` and `save_reading_note` have closed request definitions, shared
course dispatch, HTTP routes and CLI twins. Both the page and its private
view API require the loopback write-side origin gate, even though the view
itself is read-only. Note content cannot be read through a LAN daemon.
Saving validates the current accepted occurrence, source and read right.
The new path saves learner wording as a private learner claim, never a quote
or accepted course claim. Its source target stores identity, fingerprint,
locator and a hash. It grants no new source right.

F5 is resolved for this supported journey. `notes.write_note_document` now
uses `journal.commit_operation` with the existing component kind for the
NOTE-01 document and Markdown as a companion. The existing note schema,
identity, owner, objective attachment, target and learner wording are retained.
The pre-existing `delete_note` tombstone extension is validated without
changing its format or the schema. The transaction journal lives beneath the
private `_notes` root, separate from the course graph journal. Its entries
contain identity, hashes and recovery metadata. Private before-image blobs
remain inside that private root and must be inventoried for restore and
privacy screening. Neither course graphs, evidence nor error messages receive
note wording.

The UI submits the observed pair fingerprint, or explicit null for creation.
The writer checks that base again under the journal lock, and the Markdown
companion has its own exact-byte digest guard. The reader takes the same lock
and refuses unresolved prepared, mixed, missing, divergent or unsupported
pairs. Removing both accepted files cannot silently create an empty new
history. Symlinks outside the note root are refused. Existing Python callers
retain their signature with an optional expected fingerprint. Interactive
callers must provide it. A stable note ID makes an unchanged save retry
idempotent. The UI only reports saved after durable acceptance.

A caught write fault rolls back the pair through the existing journal. A
process-style interruption after the sidecar replacement leaves a named mixed
transaction, blocks saved-state reads, and recovers through `journal.undo`
against the private note root and exact entry ID. This is the existing
recovery authority, not a second recovery log. Unsaved browser wording remains
in the textarea with a leave warning. Automatic disk autosave of drafts is
not claimed. Journal before-images retain prior private revisions, so deleting
a current note is not a claim of erasing recovery history.

Verification performed on this uncommitted candidate:

| Check | Result and actual scope |
| --- | --- |
| `python3 -W ignore::ResourceWarning tests/reading_desk_roundtrip.py` | Seven tests pass. Separate completion and shared notes, new-process CLI read, correction/retraction, missing history, rollback and interrupted-pair undo, source movement and loss, occurrence removal, privacy, revision and placement changes, stale note base, denied rights and changed source bytes, exact-byte tamper and symlink refusal, missing accepted pair, HTTP origin refusal, supported page and CLI note save. |
| `tests/reading_declarations_roundtrip.py`, `tests/reading_ops_roundtrip.py` | All 14 declaration and nine reading-operation tests pass unchanged. |
| `tests/note_schema_roundtrip.py`, `tests/note_trio_roundtrip.py` | Eight and nine checks pass. Existing note format, projection and portable document use remain compatible. |
| `tests/course_ops_roundtrip.py`, `tests/mcp_roundtrip.py`, `tests/protocol_roundtrip.py` | Pass. The added course read is included in the existing read-side nonmutation gate, and every required request field has CLI parity. |
| `tests/journal_roundtrip.py`, `tests/course_resume_roundtrip.py`, `tests/scoring_roundtrip.py` | Pass. Existing recovery and canonical practice resume remain intact. The one-scorer check passes. |
| `tests/note_promotion_roundtrip.py` | Five checks pass and three baseline assertions fail. The same three failures reproduce after substituting the original HEAD note module in an isolated process: settings-schema baseline hash, event count 16 versus 17, and the lifecycle pair no longer being last after `reading_declared`. The delete-note persistence check now completes. No baseline was rewritten. Final integration owns reconciliation. |
| `python3 scripts/preflight.py --quick` and `git diff --check` | Pass. Quick preflight skips full Python, JS and clean-tree checks by design. No full suite was run for this link. |

Actual CUA browser observations on the local synthetic daemon:

- B1: Entered from course Learn, opened only the accepted first paragraph,
  clicked the explicit reading declaration, and saw reported-read.
- B2: Saved one learner note, opened the repeated assignment, and saw that same
  note while its declaration remained not-reported. Restarted the daemon and
  verified both the first declaration and the note persisted.
- B3: Made the synthetic private note directory nonwritable, attempted a
  second note, and saw refusal with the exact textarea draft still present.
  Restored permissions and retried successfully. No duplicate note was made.
- B4: Appended a synthetic retraction through the evidence owner, reloaded,
  and saw not-reported. A fresh explicit browser action produced a new live
  declaration. Notes survived both states and another daemon restart.
- B5: Inspected the final desktop layout and a 375px viewport. Browser DOM
  reported client and scroll widths both 375. Tab from the textarea focused
  Save with a solid visible outline and a 46px control height. The viewport
  override was reset. These are browser checks, not human screen-reader,
  touch-device, zoom or aesthetic acceptance.

Exercised route:
`http://127.0.0.1:58039/course/synthetic/reading/b9b9cd42e0084eea/5455e4034e914cf1`.
The temporary synthetic root and launch details are in the machine-local
`.reasonix/REASONIX.md` Link 4 note. Port availability is not durable evidence.

Changed paths for Link 4 are `notes.py`, new `reading_desk.py`, new
`surfaces/reading_desk.py`, `schemas/course_operation.schema.json`,
`surfaces/course_ops.py`, `surfaces/cli.py`, `surfaces/daemon.py`, new
`tests/reading_desk_roundtrip.py`, and three added lines in the existing
`tests/course_ops_roundtrip.py` read-field gate. This document and STATE own
reconciliation. Existing recovery, resume, exporter, source-adapter, prototype,
vision and scoring edits remain intact. Large modules were read by relevant
symbols and diff windows, not exhaustively. No commit, staging, push, branch
switch, real-course write or release occurred.

Final Link 4 implementation fingerprints:

| Path | SHA-256 |
| --- | --- |
| notes.py | `ab88f4a60013688615459e690339106aba7d459cdf9db309eaf16c7e8963d2d2` |
| reading_desk.py | `d378c8ca3a35e2a938de9137a541bf3676e1bedf1a071c698470e33e54ad27a1` |
| surfaces/reading_desk.py | `f1e18a11bf2a21dafe210ad3a43b3ce73ef67403039e9135a5659d23b1e109ca` |
| schemas/course_operation.schema.json | `2597c9fccf892bb2c84ebd36501956eb2279f2bf8a232849f06b0ed0a58730ce` |
| surfaces/course_ops.py | `498674c9b8c493a93ef7de876c0ffcf739a870531371cca9011f9b6628731527` |
| surfaces/cli.py | `f6d53777b8c4501dfee370f79f1c00ad7c63215babb5489339fe273fc1b61162` |
| surfaces/daemon.py | `8e674d5e3716feef1a36a8b9715cb527390a0844b3fa1f2ab4fffe6e5fd71510` |
| tests/reading_desk_roundtrip.py | `e80054a5e98d836885f0f086d12c6c4dd6b6314f58171b62c4c785dbe9e8516b` |
| tests/course_ops_roundtrip.py | `989ff4f85fa5f67961a54810092a8e93bb0b45b1d33d238cb97662ae52ac4d57` |


### Link 5 packet: offline restore and final A3 integration

GOAL: Prove a clean offline restore of the accepted reading journey and its
private notes, with exact preserved identities, truthful losses, and no
accidental new history. Then run the final integrated A3 candidate checks and
reconcile A1/A2/A3/A4 evidence without claiming human or real-course acceptance.

OWNER: The successor is the sole implementation and STATE/contract owner upon
dispatch in this same local checkout. Use the configured default primary model
at medium effort, one implementation owner, and no delegation by default.
Apply $daisy-chain-work, $efficient-agent-routing and $evidence-gated-handoff.
Weibao owns material decisions and human acceptance. Bounded implementation
and chaining are already authorized. Do not ask again for that authorization.

SCOPE: Read the accepted contract, Link 2/3/4 results, current STATE and A4's
integration report. Inventory `course_package.py`, current export/restore
manifests, journal provenance and private companion handling before extending
existing authorities. Use the existing packaging and journal protocols.
Repair the smallest demonstrated omission needed for this gate. Validate
checksums and references before activating a clean restored root. Include the
new reading and notes modules in any existing required code/resource packaging
inventory if the final candidate check exposes an omission.

DO NOT TOUCH: Runtime scoring/disclosure, source-adapter generation, other
prototype design, real courses, parity backends, external services, release
files, unrelated dirty work or Git mutation. Preserve recovery, resume,
exporter and vision edits. Do not stage, commit, push, switch branches or create
a worktree missing this uncommitted candidate. No new rights or remote
processing. Exact cursor resume, multiple spans, occurrence-private notes and
human/real-course acceptance remain deferred.

CONTEXT AND INVENTORY: The Link 4 synthetic fixture contains two permanent
occurrences sharing one binding revision and one native single-span source.
The accepted course object is `0ffacca90f574e13` with fingerprint
`sha256:1a42589957bfb8eacff65b4d771af89c8c55f4b90c2e16ea9ad6af5937e6338d`.
Source `e2d5bebb26fe4e8b` resolves to `sources/example.md` with fingerprint
`sha256:8fc4c4b839f8bacad6b924939fa001a36be2557af35d5ed35f23c2dbb271128d`.
This native fixture has no locator sidecar by design. The adapted-source
locator case still needs its own restore fixture. The root course journal has
16 entries including two director confirmation checkpoints. Evidence contains
two reading declarations and one retraction, with only one live declaration.
`_notes/notes.md` and `_notes/notes.md.json` contain two learner-owned source
notes. Their separate private `_notes/_journal` contains six entries including
the sampled refused save and accepted writes. The source is read/transform
allowed in the synthetic fixture, not automatically package/export/share
allowed. Inventory its actual grants rather than assuming export permission.

Inventory all required accepted course snapshots, graph/binding/occurrence
revisions, source bytes and grants, native or adapted locator sidecars and
accepted companion descriptors, current note pairs and private before-images,
course and private-note journal history, enrollment receipts, director
confirmation receipts, and live plus retracted evidence. Preserve original IDs
and timestamps. Classify included, omitted-by-rights, missing, unsupported and
conflicting objects individually. Never copy unrelated course histories.

NEXT ACTION: Verify live ownership and Link 4 hashes, then inspect the existing
package inventory and restore validation by symbol. Build a fresh synthetic
native and adapted restore probe. Use that probe to name the precise gaps
before writing package changes.

GATE: Offline clean-root restore preserves the current source-reading route,
separate assignment completion, shared note identity/wording/owner/objectives,
confirmation replay and correction epochs. Source omitted by rights retains
historical declarations and notes with unavailable content. Missing evidence
reports history unavailable. Missing confirmation receipt requires fresh
confirmation. Missing acceptance provenance disables new declarations.
Missing graph/binding revisions report orphan evidence, and missing note or
locator companions produce named losses. Unsupported versions remain preserved
and read-only. Divergent same-ID bytes are refused without overwrite. Sample
interruption preserves the old valid state. Test exported private-note recovery
history according to existing privacy and rights screening, never by copying
unrelated histories or leaking note wording into manifest error logs.

Run the affected focused gates, an actual local browser journey on the restored
root, then full candidate preflight once. A4's existing baseline is local-model
parity unavailable and expected dirty-tree failures. Link 4 also proved three
pre-existing `note_promotion_roundtrip` baseline failures against the original
note module. Reconcile these exact assertions against their owning current
contracts during final integration. Do not silently count them as passes or
change runtime behavior to satisfy obsolete counts. Do not rerun full suites
without a named new failure or change. Review actual diffs and preserve older
failed observations.

AUDITS: This contract owns Link 1/2/3/4 evidence. The A4 integrated-study report
owns the earlier full-run baseline. F5's pair-save defect is repaired for the
supported journey. G8 remains open. F3/F4 declaration and graph work retain
Link 2/3 gates. Human, real-course and exact cursor gates remain deferred.

RETURN: Append exact changed paths, restore inventory/loss results, browser
observations, test evidence, known failures and reconciled dispositions here.
Update STATE. Stop when integrated A3 is complete, a material decision or
external state is required, or the same blocker survives three links. If a
further bounded successor is actually needed, preserve the same skills,
authority, local checkout and exclusions, and check its active state once.

### Link 5A result: reading history transport and degraded restore, 2026-09-12

Link 5 began with the native packaging suite, which passed all seven groups.
Fresh native and synthetic adapted-source probes then demonstrated gaps that
that suite did not cover. This result is a stable subset of Link 5, not final
G8 or A3 acceptance. The companion and journal transport work remains in the
Link 5B packet below. No full candidate preflight has run in this link.

| Finding | Verified result and disposition |
| --- | --- |
| L5-F1 reading evidence selection | Before repair, each native/adapted fixture contained two declarations and one correction but restored zero events. Fixed in `course_package.py`: exact permanent course identity selects reading records, even after occurrence removal, and their direct retractions travel in original order. Foreign course identity cannot be overridden by shared source, objective or session. |
| L5-F2 history replay | Selecting the events exposed the existing first-reading-write validator requirement and the absence of event-ID dedupe for retractions. Fixed through the existing evidence writer with a package-validated historical-transport callback. Exact existing event identities are skipped after full-content equality checks. Divergent identities refuse. A private temporary evidence copy exercises the same writer before destination object writes, including correction epochs. This creates no new completion store and no fresh learner declaration. |
| L5-F3 false acceptance provenance | Both probes showed `accepted_reading_graph` accepting newly minted restore entries despite omitted original enrollment and journal receipts. Guarded: a transport restore without an undo `reverses_entry` blocks new reading declarations. An early guard also blocked ordinary undo, which the reading-operations test caught. The corrected guard preserves undo. The reading desk can display history from a clean matching graph while acceptance is unknown, but withholds source content and note/declaration writes. Link 5B must provide verified provenance before replacing this conservative transport guard. |
| L5-F4 missing transport closure | Still open. Both probes lose current private notes and original rights. Adapted source also loses its locator companion. Root journal history is reported as omitted, but private note journal before-images are skipped by the unregistered-file walk and receive no individual inventory. Enrollment, confirmation receipts and prior accepted snapshots are not transported. Link 5B owns the complete rights/privacy-screened closure. |
| L5-F5 misleading completeness and remaining validation | Still open. `restore_package.complete` currently means every manifest payload restored, even with these named losses. Do not treat it as complete reading activation. Orphan reading events are now retained but still need named orphan/reference losses. Missing versus known-empty history, missing confirmation receipts, future versions retained read-only, missing note/locator companions, object conflict preflight and interruption of the full restored closure remain final restore gates. |

The native and adapted probes now restore all three original history events.
The first occurrence has one live declaration after correction. Sources omitted
by rights do not erase that history. Original source grants are not inferred
or expanded. The package integrity digest still binds the exact evidence bytes.
The original before-fix probes reported `complete: true`, unknown source read
rights, empty notes, and acceptance without original provenance. These are
retained failed observations, not passes. The probe runner is saved in the
machine-local `.reasonix/link5_restore_probe.py` for reproduction.

Changed production files in this subset are `course_package.py`, the additional
transport-provenance guard inside `course.accepted_reading_graph`, the
acceptance-unknown fallback in `reading_desk.snapshot`, and the availability
message rendering in `surfaces/reading_desk.py`. New
`tests/reading_package_roundtrip.py` owns five focused tests. Existing Link 4
note/schema/dispatch/CLI/daemon hashes still match the recorded Link 4 hashes.
Large modules were sampled by symbol and diff, not read exhaustively. Runtime
scoring, evidence implementation, source-adapter generation and unrelated
patches were not changed by Link 5A.

| Check actually run | Result |
| --- | --- |
| `tests/reading_package_roundtrip.py` | Five pass. Exact IDs/timestamps and correction order, separate repeated-assignment state, rights omissions, idempotent repeated restore including retractions, orphan-history retention, checksum tamper refusal, same-ID divergent correction refusal without destination changes, and foreign-course payload refusal even with a recomputed manifest checksum. |
| `tests/course_package_roundtrip.py` | All seven groups pass before and after the changes, including existing manifest, archive, rights, evidence-integrity and snapshot gates. |
| `tests/reading_declarations_roundtrip.py` | All 14 pass. |
| `tests/reading_ops_roundtrip.py` | All nine pass after correcting the transport-versus-undo distinction. Earlier run had one failure in `test_atomic_shared_revision_placement_restart_undo`. |
| `tests/reading_desk_roundtrip.py` | All seven pass after the degraded snapshot and availability message changes. |
| `tests/journal_roundtrip.py`, `tests/course_resume_roundtrip.py`, `tests/protocol_roundtrip.py` | Pass. Journal and protocol emit their intentional malformed-fixture warnings. |
| `python3 scripts/preflight.py --quick`, `git diff --check` | Pass. Full Python, JS and clean-tree checks are explicitly skipped by quick preflight. |

Actual CUA browser verification used a clean restored synthetic root, separate
from the exporting fixture. It showed first assignment reported-read, repeated
assignment not-reported, unavailable source content, and disabled declaration
and note-save controls. Restarting the daemon preserved both states. Final UI
copy reads: "Acceptance history is missing. Restore it before adding reading
declarations or notes." This verifies degraded restore only. Notes were absent
from this package, so this is not a restored-note pass. No human accessibility,
real-course, complete source availability or final A3 acceptance is claimed.
The browser fixture pointer and stopped daemon recipe are in
`.reasonix/REASONIX.md`. No real courses or external services were used.

A4's full-run parity-unavailable and dirty-tree baseline remains unchanged.
The three note-promotion assertions remain unresolved as recorded in Link 4.
No full preflight is justified until the remaining restore transport is part
of the candidate. This avoids counting an intermediate subset as integration.

### Link 5B packet: journal and companion transport, then final integration

GOAL: Finish the original Link 5 gate by transporting the rights-authorized
reading closure through `course_package.py`, validating original acceptance
provenance and companions before activation, and completing final A3 checks.

OWNER: The successor is the sole implementation and STATE/contract owner on
dispatch in the same local checkout. Use the configured default primary model
at medium effort, one owner, no delegation by default. Apply
$daisy-chain-work, $efficient-agent-routing and $evidence-gated-handoff.
Bounded implementation and chaining remain authorized. No new user approval
is needed for that scope. Weibao owns material product or rights decisions.

SCOPE: Reuse the original Link 5 packet's exact inventory and acceptance gate.
Link 5A has completed only historical evidence transport and safe degraded
rendering. Extend existing package/journal protocols for the demonstrated
missing closure: current and historical graph snapshots, root course journal,
original enrollment and director confirmation receipts, rights-granted source
bytes and locator companions, current private note pairs, and separately
screened private note recovery history. Preserve identities, timestamps,
source fingerprints, learner wording and owner, objectives, exact accepted
heads and all correction epochs. Do not blindly copy an entire workspace or
unrelated journal history. Do not infer grants from the presence of files.

DO NOT TOUCH: All original Link 5 exclusions still apply. No Git mutation,
real-course writes, scoring/disclosure changes, source-adapter generation,
parity-backend changes, other prototype work, external services, release files
or new remote processing. Preserve existing recovery, resume, exporter and
vision patches. Exact cursor resume, multiple spans, occurrence-private notes
and human/real-course acceptance remain deferred.

CONTEXT: `course_package._restore_evidence` now uses the existing evidence
writer with a historical restore validator after manifest checksum/schema
validation. It preserves exact event identities, refuses divergence, and does
not mint a new confirmation. A private disposable evidence simulation runs
before object restore when reading records are present. It is not a global
multi-file activation transaction. Revalidate the destination or use the
existing staging/publication authority for the complete closure rather than
claiming the preflight alone prevents every concurrent race. The existing
`complete` return field is still payload-count completeness, not G8 success.

`course.accepted_reading_graph` now conservatively rejects transport restore
entries unless they are journal undo records with `undo.reverses_entry`.
Replace that condition only when verifiable original acceptance history is
available, never merely because new restore entries validate. Ordinary undo
must continue to work. `reading_desk.snapshot` exposes historical state and
notes from clean matching graph bytes when acceptance is unknown, with no
source access or write authorization. Missing notes still need a truthful
individual loss state. The new five-test reading package suite is a base to
extend, not complete G8 coverage.

NEXT ACTION: Read this result and the original Link 5 inventory. Inspect the
existing journal record validation, before-image descriptors, companion
validation, restore staging/publication and package manifest schema before
choosing the smallest additive transport format. Run the saved native/adapted
probe only if needed to inspect an unresolved mechanism. Do not repeat the
completed audit or delegate it back to another agent.

GATE: The original Link 5 matrix remains binding. Add clean native and adapted
restore tests with readable rights-granted source content, exact private note
pair and screened recovery history, confirmation replay and correction epochs.
Cover rights omissions, missing history/provenance/receipts/companions, orphan
references, future versions preserved read-only, divergent same-ID objects and
interruption without false activation. Require a restored-root browser journey
with actual notes and source content. Then reconcile the exact three obsolete
note-promotion assertions against their current owning contracts, verify any
missing resource inventory entries, run affected focused gates, and run full
candidate preflight once. Preserve A4's baseline and distinguish every skipped
or human-only gate. Do not update baseline assertions merely to turn them green.

AUDITS: This contract owns all Link 1 through 5A results and the five reconciled
findings above. L5-F1/F2 are fixed. L5-F3 is conservatively guarded pending
verified original provenance. L5-F4/F5 and G8 remain open. There is no repeated
external blocker: this is remaining implementation exposed by concrete probes.
The A4 report owns the previous full-run results. Reconcile both before closure.

RETURN: Append exact changed paths, hashes, checks, restored browser results,
loss classifications and final dispositions here. Update STATE. Stop when A3
is complete or a material decision/external state is required. Create another
successor only if meaningful work remains at a stable gate under the same
existing authorization. Do not claim this handoff completes A3.

Final Link 5A implementation fingerprints:

| Path | SHA-256 |
| --- | --- |
| course_package.py | `0b28eeaef1503b55a4af8f21d8319808152d717064d9403f21a96214ae845b43` |
| course.py | `c5c8bc7c78c514e6ca915bc12befe71a3d208d181a6535af4cebe84c22b83a7e` |
| reading_desk.py | `e6c9e2bbbe93de86a1f8d85dab11b23a767af2b3f8870b9ab28f01fb3ae7b402` |
| surfaces/reading_desk.py | `b8365aaf27faab2e54af2e87ce979f89b2e664c677f15a0d1a9820f5a1797a70` |
| tests/reading_package_roundtrip.py | `db428772286aaed7e4f69a0145f30450fd1425cce8f27794e00f658dace38ded` |

### Link 5B partial result: original journal and source companions, 2026-09-12

The five final Link 5A hashes matched before editing. This task owns the same
uncommitted local checkout. It added no subagents, Git operations, external
processing, real-course writes or release. All earlier results remain history.
This is a stable implementation subset, not G8 or A3 completion.

`journal.validate_transport` validates selected original receipt identities,
prepared/applied linkage, revision chains and same-object undo references.
`journal.restore_transport` uses the original append authority in an empty
private staging journal. It preserves original IDs, timestamps, rights,
revisions and director confirmation checkpoints. Registry data is rebuilt
from that journal. It does not introduce a second acceptance store.

`course_package.py` adds a digest-bound `reading-transport.json` package
component and the optional manifest `reading_transport_fingerprint`. The
component carries only the course and packaged reading-source receipts,
their required historical snapshots and accepted source locator companions.
Recovery blobs must match their content-addressed names and descriptors.
Every accepted historical fingerprint must resolve to transported bytes.
Current source package rights still gate inclusion. Unrelated operations and
private note history are not copied. A missing acceptance closure produces a
named degraded restore rather than trusting new restore receipts.

Restore constructs and syncs the directory privately before the existing
no-replace directory publication. It compares an existing destination without
writing and refuses divergent payload, event or original-receipt identity.
Empty destination removal and publication each refuse a raced nonempty root.
The focused interruption test fails publication and observes an empty original
destination. This is staging plus atomic directory publication, not an atomic
transaction across separate live file replacements. Existing nonempty roots
are not merged. `complete` retains payload-copy semantics and the additive
`reading_acceptance` reports accepted or unknown. Neither means a full reading
journey is complete.

| Finding | Current disposition |
| --- | --- |
| L5-F1/F2 evidence selection and replay | Retained. Exact evidence identity and correction order still pass. |
| L5-F3 original acceptance | Fixed for validated scoped course histories. The conservative legacy restore guard in `course.py` is unchanged. Original receipts restore acceptance without manufacturing enrollment. Missing snapshots fall back to acceptance-unknown. |
| L5-F4 transport closure | Course/source history, snapshots, current source rights, director receipts and locator companions now pass native/adapted tests. Private current notes and recovery history remain excluded pending Q5B-P1 below. |
| L5-F5 final acceptance | Missing versus known-empty evidence, missing confirmation, orphan occurrence losses, locator loss, tampering, divergent destinations and interrupted publication pass focused tests. Full future-version byte preservation, private-note loss/recovery inventory, supported-surface reporting of reading acceptance, and complete restored-note browser acceptance remain open. |
| Link 4 baseline assertions | Reconciled against Phase 20's additive `presentation_profile` and Link 3's additive `reading_declared`. The original hash, count 16 and lifecycle ordering are reconstructed after removing only those additions. No recorded baseline or runtime behavior changed. Eight checks pass. |
| Code/resource inventory | `build.py` omitted `reading.py` and `reading_desk.py`. Both are now in `STAGE_FILES`. The existing recursive surface/resource inventory covers the reader surface and schemas. Packaging passes with its explicit unbuilt Windows onedir skip. |

Q5B-P1 is a material privacy policy question, not another request for bounded
implementation permission. The packet assumes existing private-note screening,
but `notes.py` supplies private persistence and promotion semantics only.
`course_package.py` supplies source package rights but has no personal-backup
purpose or private-note inclusion control. Default course export therefore
cannot safely assume that private current notes, or deleted wording retained
in before-images, should travel. The proposed policy is two explicit,
default-off personal-backup options: include current private notes, and
separately include private recovery history. The alternative is to keep notes
excluded and label that restore limitation. This question was sent to Weibao
and has no answer at this gate. No private-note transport change was made.

| Check actually run | Result |
| --- | --- |
| `tests/reading_package_roundtrip.py` | Twelve pass. Native source content, exact original journal/registry, adapted locator content and descriptor, pending confirmation replay, original graph undo, missing provenance and idempotent degraded restore, known-empty/missing evidence, missing confirmation with fresh intent, named orphan history, exact corrections, manifest/receipt tampering, destination conflict and publication interruption. |
| `tests/course_package_roundtrip.py` | All seven groups pass. Its additive loss-category assertion now includes `reading-transport-loss`. The initial run correctly failed on that vocabulary extension. |
| `tests/journal_roundtrip.py` | Pass, including existing recovery faults and concurrency. Intentional malformed-fixture warnings remain. |
| `tests/reading_declarations_roundtrip.py`, `tests/reading_ops_roundtrip.py`, `tests/reading_desk_roundtrip.py` | Fourteen, nine and seven tests pass respectively. |
| `tests/note_promotion_roundtrip.py` | Eight pass after the exact baseline reconciliation. The initial run reproduced all three prior failures. |
| `tests/packaging_roundtrip.py` | Pass. Windows onedir sidecar checks explicitly skipped because that artifact is not built. No release was performed. |
| `tests/course_resume_roundtrip.py`, `tests/protocol_roundtrip.py`, `tests/course_ops_roundtrip.py` | Pass. Protocol emits its intentional unknown-event warning. |
| `python3 scripts/preflight.py --quick`, `git diff --check` | Pass. Full Python, JS and clean-tree checks were skipped by quick preflight. |

The saved native/adapted probe now reports available source content and all
three history events with zero notes. Its old output label
`accepted_without_original_provenance` is stale: original provenance now
travels. The focused tests compare original journals directly and own the
new acceptance evidence. No new CUA browser journey ran in this partial link.
The prior Link 5A browser evidence remains degraded-only. Full preflight is
reserved for the candidate containing the remaining approved note closure.
A4's known parity-unavailable and expected dirty-tree baseline remain open.

Changed files in this link are `journal.py`, `course_package.py`, `build.py`,
`tests/reading_package_roundtrip.py`, `tests/course_package_roundtrip.py`,
`tests/note_promotion_roundtrip.py`, this contract and STATE. Large modules
were sampled by symbol and reviewed in relevant diff windows, not read whole.
The Link 5A hashes for `course.py`, `reading_desk.py` and its surface still
match. Existing recovery, resume, vision and prototype work was preserved.

| Path | SHA-256 at this gate |
| --- | --- |
| journal.py | `2508799797a367edaed102beba967374e329eab7299eb36611c325e5d9719372` |
| course_package.py | `dc222fee883d15fc905d264fb2a4e7b62229be9399129704d6115853b0e8b449` |
| build.py | `61d35cd1a094729ecfec3099f61e14ec2da58e7d2e21559a2fc5b05b48ceabaf` |
| tests/reading_package_roundtrip.py | `40a075f5ab645e0445b5c8c14250b061df99a1e2e82186653adfe072b3059065` |
| tests/course_package_roundtrip.py | `cf97db2065d20634a6bfdd381f514b11eafb7e0efb0d6d8ebc05d95e93a85e23` |
| tests/note_promotion_roundtrip.py | `37d92abdec1cf3b732a00ed5091d7b2b5cb7ffac8d2ab0f0528ae9b3ccb4b676` |

Resume after Q5B-P1 is answered. Keep the same local checkout and one owner.
Apply the accepted privacy choice through the existing notes/package/journal
authorities, then finish the remaining original Link 5 matrix and restored
browser journey. Run full candidate preflight once after that closure is
implemented. No successor is dispatched while the material decision is
pending. Exact cursor, multiple spans, occurrence-private notes, human and
real-course acceptance remain deferred rather than passed.
