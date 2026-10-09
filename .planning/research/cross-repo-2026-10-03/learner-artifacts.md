# L2 learner artifacts, October 3

Status: existing-format source implementation and targeted checks passed.
L2 releases `notes.py`, `surfaces/learner_artifacts.py`, its new tests and this
report to the coordinator for integration. Coordinator
`01a102a5-223f-7293-ae74-1922372ac0c8` owns daemon integration and broad gates.

## Scope and authority

Connect one learner-authored text, proof or program draft to an existing
short-response activity. NOTE-01 and its private journal own saved wording;
the existing runtime session and response event own explicit submission;
existing human mark/retraction events own review. No code execution or
aggregate rubric score. No generic attachment/submission format, grammar,
runtime/session/schema edits, real learner data, provider calls, commit,
push, install or release. Other dirty writers are preserved.

Base HEAD: `28bf561865cf0696a8beb42dd6f356b8bf6ec648`.
Initial SHA-256 inputs:

- `notes.py`: `e43c6f9db337451bed8c80383c52edee81022f0282d595c26411f56fbd8249f1`.
- `schemas/note.schema.json`: `b1b4660e340807a01ded90d55b93212b7b106a30df3ee7fd898d34b38f3f347d`.
- `surfaces/session.py`: `dee236ff9dab47589fdbe6ae9ac03311f273e7af9d17eaebfdad74933b3b6686`.
- `fixtures/coding_boundary_unit.md`: `8b0aa5a36349d67828feab7ed9a4ba5b39fe362f2f6a00372a96596555857c8f`.

## Interface request to coordinator

Implemented importable surface: `view(bank_path, note_root, course_id, item_ref,
session_file=None, note_id=None, kind='explanation')`; `apply(action, body, *,
bank_path, note_root, course_id, item_ref, session_file=None)`;
`render(view, *, action_url, return_href, panel_href, message='', preview=False,
preserved_wording=None, reviewer_href=None, objective_label=None, theme_css=None)`.

Parent resolves admitted course, bank, private note root and session IDs.
Requests never carry filesystem paths. `form_body` accepts singleton strings:
`action`, `item_ref`, `note_id`, `session_id`, `kind`, `notes_fingerprint`,
`note_revision`, `bank_revision`, `content_revision`, `wording`, `confirmed`.
The surface applies `view`, `save`, `preview`, `submit`, `cancel`; submit needs
`confirmed=yes` and the exact saved content/revision and bank pins.

Coordinator wired GET/POST `/course/<id>/artifacts`. GET lists admitted short
activities or opens `?bank=<stem>&item_ref=<ref>&session_id=<optional>` with
optional `note_id` and presentation `kind`. Form POST action URL has only
`?bank=<stem>`. Parent handles an explicit `start` action, requiring a checked
confirmation and current bank revision before invoking the existing runtime
selector for one exact short activity. View/save never create a sitting.
Parent supplies the existing reviewer URL and exact sitting/course return;
draft navigation preserves bank/item/session/kind and selected note.
No daemon writer lease was requested or taken by L2.

Existing `/api/mark` provides actual human settlement. Existing
`evidence_cli.cmd_retract` or `evidence.retraction_event` via the one evidence
writer provides actual retraction. L2 adds no new settlement/retraction
authority and no provider request. Native reviewer settlement needs its
existing scripted sitting surface or CLI; the artifact draft, explicit start,
preview, cancel and submission forms work without JavaScript.

## Existing-format limit

Existing short response events preserve submitted text verbatim, event ID,
objective and session, but not a historical rubric snapshot or originating
note ID. The surface can name the UTF-8 content hash as submitted revision,
compare it to the current draft and refuse changed authored targets. It must
not claim immutable generic project lineage or original-rubric restoration.
`kind` is presentation metadata, not a newly persisted note field. The
current native slice is one saved NOTE-01 text draft and one exact short
practice sitting. Multi-item/formal sittings remain on their assessment
surface. A mark is read as its existing runtime/evidence fact; criterion
states are never summed into mastery. Missing criteria do not discard text.

One concrete broader specimen, proposal only, could bind the existing objects
as follows. This is not a schema, shipped record or accepted format:

```json
{
  "response_event_id": "synthetic-response-id",
  "origin_note_id": "synthetic-note-id",
  "origin_note_revision": "synthetic-note-revision",
  "submitted_content_revision": "sha256:exact-utf8-content-digest",
  "item_revision": "existing-item-fingerprint",
  "objective_id": "synthetic-objective-id",
  "rubric_snapshot": ["Synthetic inclusive boundary criterion"],
  "return_context": {"course_id": "synthetic-course", "activity_id": "synthetic-activity"}
}
```

Promotion first needs a direct decision on durable owner, immutable rubric/
revision identity, transaction/recovery across note/session/evidence roots,
submission-versus-draft lineage, and package loss/restoration. The retained
alternative is the existing response event and derived content hash used here.

## Evidence and return

Executed checks:

| Command | Observed result and scope |
| --- | --- |
| `python3 tests/learner_artifacts_roundtrip.py` | 9 passed. Private save/reopen, exact submitted whitespace/Unicode/JSON-like strings/CRLF, later draft separation, pending review, authored criteria, actual mark and retraction, fresh Python-process reopen, two competing writers with one CAS winner, cancellation, missing rubric, stale target/formal refusal, text export, and evidence-first session-write fault. |
| `python3 tests/note_schema_roundtrip.py` | 8 passed. Existing NOTE-01 vocabularies, tier imports, schema, anchors and writer contracts. |
| `python3 tests/note_promotion_roundtrip.py` | 8 passed. Existing note promotion and artifact evidence behavior. |
| `ITEMBANK_VISUAL_QA_CHANNEL=chrome python3 tests/learner_artifacts_native_roundtrip.py --browser .reasonix/learner-artifacts-20261003` | Native HTTP normal course entry, deliberate start, save, preview, cancel, submit, input-preserving stale refusal, actual `/api/mark`, mark retraction, daemon restart, exact sitting return and path admission passed. Six installed-Chrome light/dark 1280/390/320 script-free keyboard flows passed with no horizontal overflow. |
| `git diff --check -- notes.py surfaces/learner_artifacts.py tests/learner_artifacts_roundtrip.py tests/learner_artifacts_native_roundtrip.py .planning/research/cross-repo-2026-10-03/learner-artifacts.md` | Passed. Scoped actual diff reviewed; L2 did not edit other lanes. |

The four new files also received `git diff --no-index --check /dev/null
<path>` comparisons. Each returned status 1 because it is an added file,
with no whitespace diagnostics; these are not zero-exit test receipts.

Local screenshots and `observations.json` are in
`.reasonix/learner-artifacts-20261003/`. Screenshot inspection found a blank
objective line because `runtime.public_item` omits objective; L2 added an
explicit public objective field and optional course-owned objective label,
then reran the native/Chrome check after the visible change. Full content
digests and response IDs are inspectable under collapsed revision details.

Original failures are retained as failures: the first adapter run had four
incorrect test assumptions that `do_start` wrote no evidence. Start correctly
records selection, and the test now compares its initial event snapshot.
The first normal native-start check created a sitting successfully but could
not reopen it: parent used the course bank's `_attempts` folder while the
daemon session allowlist scans root `_attempts`. Coordinator repaired that
path; the normal-flow/native/Chrome rerun passed. The prior externally-created
single-item native flow had already passed. These failures are not broad
source-suite or installed-app receipts.

Reusable operational findings: pass JSON-quoted learner wording to the
existing `session.do_action` normalizer to preserve exact original strings;
plain strings are stripped and JSON-like text is parsed. Use course `_notes`
for the existing private-note package route, but daemon root `_attempts` for
native sitting addressing. Source-note and session locks remain with their
existing owners. Submission holds the private note journal lock while handing
captured bytes to the runtime; saved-note edits cannot swap those bytes.

Only the coordinator runs broad preflight. No packaged/installed, human
accessibility, touch, screen-reader or learning-effectiveness acceptance is
claimed. Offline fresh-process reopening and exact single-text download were
tested; full artifact-package restore with historical rubric/draft lineage is
unproved and its omissions are displayed explicitly.

## Undo and handoff

Saved drafts use the existing private journal's recoverable paired write and
before-image history. Reviewer marks retract through existing evidence undo;
submitted response bytes remain inspectable. No real learner files were
changed. To remove this source slice, remove only the three new L2 source/test
files and this report, revert the bounded helper insertion in `notes.py`, and
ask the coordinator to remove its matching route hooks. Preserve every other
dirty edit; do not reset the checkout.

The coordinator owns final integration and implemented the readable
objective-label hook by exact objective ID in the current course. No further
schema or reviewer authority request is needed for this slice.

Final L2 implementation and test SHA-256 pins:

| Path | SHA-256 |
| --- | --- |
| `notes.py` | `334e024d2ca19ac0b128f93785a582a6c3ce84d0adcc1fa7309d1bfe8e95c781` |
| `surfaces/learner_artifacts.py` | `45cd55e5419eefcd0c7a577bd514053dbcfcc2bc47d409de6567fda3a2ea8211` |
| `tests/learner_artifacts_roundtrip.py` | `fee2e46411b525d90d8e1024b6385e196af0e1b56368d734ead4536f1c898359` |
| `tests/learner_artifacts_native_roundtrip.py` | `fea68eb81cac571928f72a45f36ec582f912e39e918ee5259e927c8ea5dde7bb` |

Sampled shared dependency pins for the final native check:
`surfaces/daemon.py` at
`470b7d953cb18141ca6a902226c57aa521f2f5a5e46619e4025ec342c1cc25d4`;
`runtime.py` at
`7c005333989929fc214d906566189a38c289a57fff223f1a77d4baa7a6cfba15`;
`surfaces/session.py` at
`dee236ff9dab47589fdbe6ae9ac03311f273e7af9d17eaebfdad74933b3b6686`.
`model.py` at
`ccfcd3b4229d1419f64ebe11e833518e689fbf742b9f3a010bd598b2373fdb1a`.
The note schema and coding fixture remain at their initial pins above.
The shared daemon continued changing during final lane integration: its
post-run pin is
`6c65442ce8bfbd405f78eaf3ae59dc94248ab8562ead3a6f2a7debecdc942476`.
This preserves the measured input/version limit rather than claiming a frozen
combined candidate. Coordinator's final gate owns the integrated source.

Reading limits: L2 sampled the relevant symbols in the large note/session/
runtime/daemon modules, not their whole files or phase history. Its new
surface and test files received actual-source review. These are bounded
source checks, not whole-module or whole-repository certification.

Ownership released after the final native/Chrome rerun, including the
course-owned readable objective label. First next action is coordinator
review of this bounded diff and its source-matched receipts, then the sole
combined source-only preflight after every lane releases. L2 creates no
successor chat and performs no further writes without a new concrete failure
or coordinator request.

## Prior-implementation refinement

The [October 3 continuation](../prior-implementation-improvements-2026-10-03.md)
adds an explicit local download of the current review details. It contains the
owner's original response event and actual mark/retraction records; current
criteria remain separately labeled. It does not fabricate a draft origin or
rubric snapshot that older evidence never captured. The nine adapter checks
pass with exact Unicode/whitespace, pending review and mark/retraction export.

The proposed optional immutable response provenance has an executable closed
specimen at
[`submission_provenance.schema.json`](../../../prototypes/prior-improvements-20261003/submission_provenance.schema.json).
Its origin-note/revision, submitted-byte hash, item revision, rubric and artifact
kind remain proposed fields. It permits no settled score or criterion verdict.
Direct owner/snapshot acceptance remains pending before production capture.
