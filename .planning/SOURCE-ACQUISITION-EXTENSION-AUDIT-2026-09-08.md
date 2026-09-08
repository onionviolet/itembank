# Source acquisition extension audit

Status: scoped recommendation. No downloader or ASR backend was implemented in
this pass.
Owner: post-Reach source acquisition phase.
Origin: the 2026-09-08 transcript, Canvas downloader, and extension audit
direction in `USER-VISION.md`.

## Answer

Itembank should add a source acquisition layer above its existing source
adapter registry. The adapter registry already turns one available object into
Markdown plus cited locators. The missing layer discovers, downloads, resumes,
and reconciles a set of authorized objects before sending each object through
that existing boundary.

The first vertical slice should import an authorized Canvas course export. The
second should use the Canvas API for live incremental acquisition. Caption
files should be preferred over speech recognition. Local ASR should be the
first transcription backend. Hosted ASR should remain optional and must name
the exact media sent off the machine.

This work starts after the active Reach milestone. It does not expand Reach or
the current 19D recovery path.

## Verified current capability

F1. Ten source adapters already register through one boundary in
`source_adapters.py`. Markdown, text, PDF, DOCX, PPTX, web, transcript, OCR,
EPUB, and ASR are named capabilities.

F2. Transcript import already accepts SRT, WebVTT, and bracketed timestamp
text. It emits millisecond cue locators. It does not create a transcript from
audio or video.

F3. ASR is a registered typed refusal. `ASR_BACKENDS` is empty, so the current
recovery action is to supply a transcript file.

F4. Web capture downloads and snapshots one public HTTP or HTTPS page. It has
scheme, redirect, private-origin, timeout, and size protections. It is not a
crawler and it does not carry an authenticated browser or LMS session.

F5. Canvas LTI work is an outbound delivery surface. It launches an itembank
activity in Canvas and may return a score. It does not import Canvas modules,
pages, assignments, files, captions, or course structure.

F6. `absorb-book` begins after a source is available. It audits a source and
chooses learning treatments. It does not acquire a source from an LMS.

## Capability boundary

The new acquisition layer owns remote discovery and transfer. It produces an
acquisition manifest plus immutable raw objects. Each raw object then enters
the existing adapter and source-binding path.

The acquisition layer must not parse documents a second way. It must not turn
Canvas quiz keys, grades, submissions, or feedback into accepted assessment
truth. It must not treat an authenticated page as permission to copy every
linked resource.

The durable objects are the acquisition job, its manifest, its raw snapshots,
and the source records created by accepted imports. Download queues and indexes
are derived state. The manifest records the remote identity, local fingerprint,
course and module path, access basis, rights state, capture time, outcome, and
recovery action for every discovered object.

## Proposed capability set

D1. Build `canvas-export` first as a Prototype. It imports a learner-provided
Canvas course export without storing credentials. It proves hierarchy,
resource coverage, loss reporting, duplicate handling, and restart behavior
against a stable fixture.

D2. Build `canvas-api` second as a Registered integration adapter. It uses an
explicit learner-provided token or approved OAuth flow. It supports pagination,
rate limits, incremental recheck, and per-resource approval. Credentials stay
outside course artifacts and operation journals.

D3. Keep browser-assisted capture as a Backburner fallback. It is useful when
an institution disables exports and APIs. It is more brittle, harder to resume,
and more likely to blur page display with download authorization.

D4. Add local ASR as a Prototype behind the existing ASR registration. Prefer
published SRT or WebVTT captions. Use local transcription only when captions
are absent or unusable. A hosted backend is a separate opt-in with explicit
remote-process rights and egress disclosure.

D5. Generalize to other LMS providers only after Canvas proves the acquisition
manifest and recovery contract. Moodle backup, IMS Common Cartridge, SCORM,
Blackboard, D2L Brightspace, Panopto, Kaltura, and YouTube captions are
Registered research targets, not one first implementation.

## Coverage and failure audit

R1. A Canvas acquisition manifest should cover syllabus, modules, pages, files,
assignments, discussions, quiz shells, external links, media, and captions.
Each unsupported, forbidden, missing, or skipped object needs a typed outcome.

R2. Keyed quiz content needs a separate assessment-intake decision. Importing a
question bank cannot bypass the runtime's parser, scorer, disclosure, review,
and provenance rules. Student submissions and grades are excluded from the
first slice.

R3. The downloader needs bounded concurrency, pagination, retry limits,
backoff, resumable transfers, content-length and decompression caps, filename
sanitization, MIME verification, and redirect checks. A partial run must resume
from the manifest without redownloading accepted objects.

R4. Incremental sync must distinguish unchanged, changed, moved, deleted,
unreachable, forbidden, and conflicting objects. Remote deletion must create a
tombstone or stale state. It must never silently delete the accepted local
snapshot.

R5. Duplicate bytes with different remote identities and one remote identity
with divergent bytes are different cases. The former may share storage while
preserving provenance. The latter is a conflict that requires review.

R6. Transcript quality needs cue-level confidence, language, speaker labels
when available, caption provenance, and a link back to the original media.
Generated summaries or cleaned transcripts remain derived artifacts.

R7. The final report needs denominators. It should state discovered, downloaded,
imported, skipped, unsupported, failed, unchanged, changed, and pending-review
counts. It should list every loss and the next safe action.

## Proposed command surface

```text
itembank acquire canvas-export --base COURSE --file EXPORT.zip --preview
itembank acquire canvas-api --base COURSE --course-id ID --profile NAME --preview
itembank acquire resume --base COURSE JOB_ID
itembank acquire report --base COURSE JOB_ID
itembank source import --base COURSE --file captions.vtt --adapter transcript
```

`--preview` performs discovery and produces no durable write. Acceptance writes
raw objects and a manifest through expected-base comparison and atomic journaled
commits. Secrets are referenced by profile name and are never copied into the
manifest.

## Implementation sequence

A1. Freeze an acquisition-manifest schema and typed outcome vocabulary. Prove
that it can represent complete, partial, cancelled, offline, forbidden, stale,
and conflicting runs.

A2. Implement Canvas export inventory and dry-run reporting. Feed supported
files through the current source adapters without changing their extractor
contract.

A3. Add accepted batch import with restart, CAS checks, journal entries, and an
undo that removes only objects created by that job.

A4. Add live Canvas API acquisition with credential isolation, pagination,
rate-limit recovery, and incremental recheck.

A5. Register and prove one local ASR backend against the current transcript cue
shape. Run a real Canvas course walkthrough before promoting either capability.

## Acceptance gate

An authorized fixture course and one real learner-approved Canvas course each
complete this path:

```text
discover -> preview manifest -> approve -> download -> adapt -> bind -> audit
         -> interrupt and resume -> remote change recheck -> undo -> offline restore
```

The gate passes only when every discovered object has an outcome, imported
citations resolve offline, no secret appears in artifacts or logs, unsupported
content has a loss report, a cancelled run preserves the last accepted state,
and undo restores the exact pre-job course state.

## Routing and follow-up

Use one strong planner for the manifest, rights, credential, and recovery
contract. Use economy workers for fixture construction and adapter-by-adapter
coverage after the contract is frozen. Keep one writer for shared schemas and
registries. Add an independent security review before any live credential or
hosted ASR path is accepted.

This audit sampled the source adapter registry, CLI surface, Phase 14C records,
Canvas LTI requirements, current Reach state, vision records, and extension
delivery contract. It did not read the complete large source, daemon, or test
modules.
