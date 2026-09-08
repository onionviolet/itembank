# Canvas export acquisition milestone proposal

Status: implementation-ready proposal. No acquisition code is implemented by
this document.
Owner: proposed post-Reach source acquisition milestone.
Decision owner: Weibao decides promotion, real-course access, rights, and any
later credential or browser-session path.
Builder: one strong repository agent. Use economy workers only for disjoint
synthetic fixture expansion after the schema and recovery contract are frozen.
Verifier: a separate review pass over the diff and gates. A human owns the
real Canvas export and visible-flow checks.

## Answer

Build one local `canvas-export` path first. It accepts a learner-provided
Canvas Common Cartridge file (`.imscc`), inventories it without network use,
previews exactly what will and will not import, and then sends each accepted
resource through the existing source-adapter and course-operation authorities.
It preserves Canvas organization as source provenance. It does not treat that
organization as an objective map.

Do not include live Canvas API access, OAuth, personal access tokens,
authenticated browser capture, ASR, or question-bank conversion in this
milestone. Those paths depend on the acquisition manifest proven here, but
each adds a separate authority or disclosure problem.

This remains useful if Canvas access has recently been repaired. A real
learner-approved export can satisfy the promotion gate after the deterministic
fixture passes. No current branch in this checkout implements upstream Canvas
acquisition. The shipped Canvas LTI code remains an outbound activity-delivery
path.

## Corrected access assumption

F1. Canvas officially exports course content as Common Cartridge (`.imscc`),
and a cartridge describes organization and resources through a manifest.

F2. A full `.imscc` export is not a general student download promise. Canvas's
current open-source permission policy permits non-admin users to create ZIP or
user-data exports, while Common Cartridge creation is reserved for users with
the relevant administrative course authority. The first slice therefore
supports an export the learner is authorized to obtain or has been given. The
UI must explain what to do when the export option is absent.

F3. Canvas's API can later expose student-visible modules and module items,
including files, pages, discussions, assignments, quizzes, and external tools.
That makes a read-only API integration a better general learner path than
pretending every learner can generate an `.imscc` file.

Evidence checked 2026-09-08:

- [Canvas Content Exports API](https://developerdocs.instructure.com/services/canvas/resources/content_exports)
- [Canvas content-export permission model](https://github.com/instructure/canvas-lms/blob/master/app/models/content_export.rb)
- [Canvas Modules API](https://developerdocs.instructure.com/services/canvas/resources/modules)
- [1EdTech Common Cartridge overview](https://www.1edtech.org/standards/cc)
- [1EdTech Common Cartridge 1.3 implementation guide](https://www.imsglobal.org/cc/ccv1p3/imscc_Implementation-v1p3.html)

## Existing authorities to reuse

F4. `source_adapters.py` has ten registered adapters and one
`import_source(...)` boundary. It extracts Markdown and writes a locator
sidecar. It does not discover or batch remote objects.

F5. `surfaces.course_ops` already provides course creation, source
registration, source rows, rights decisions, operation declaration, replay,
and operation reversal. `director.py` owns durable operation checkpoints.
`journal.py` owns compare-and-swap writes.

F6. The current journal can restore edits with before-images. It cannot restore
the absence of a newly minted file because a mint has no before-image and is
skipped by `director.reverse_operation`. Exact job undo therefore is a real
prerequisite, not a test to add after the importer is written.

F7. The source adapter's Markdown and locator sidecar are one logical source,
but only the Markdown is currently a journal object. A job-level reversal
would leave the locator sidecar behind unless this pair joins the operation's
recovery record.

## Decisions

D1. Name the capability `canvas-export`, but implement the package reader as a
bounded Common Cartridge inventory. Accept Canvas-produced `.imscc` packages
only in the first milestone. Report other cartridges as `provider_unverified`
until separate fixtures prove them.

D2. Treat the archive as untrusted input. Use stdlib ZIP and XML support behind
one shared hardened archive seam. Enforce normalized member paths, no symlinks,
member and depth limits, per-member and total expanded-byte limits, compression
ratio limits, MIME checks, and XML entity refusal before any extraction or
write.

D3. Parse `imsmanifest.xml` once for package organization and resource
identity. Do not interpret Canvas modules as learning objectives or
prerequisites. Preserve ordered module placements in the acquisition manifest
and Sources view. Let the existing course-design path propose objectives later.

D4. Route readable leaf resources through `source_adapters.import_source`.
HTML, Markdown, text, PDF, DOCX, PPTX, EPUB, SRT, and WebVTT are eligible.
Images, audio, video, QTI, LTI links, external URLs, and provider-specific XML
remain retained metadata or named losses in this slice. Nothing fetches an
external URL.

D5. One manifest resource can appear in several module placements. Import and
adapt its bytes once, mint one source identity, and preserve every placement.
Equal bytes under different resource identities may share storage but keep
distinct provenance. One resource identity with divergent bytes is a conflict.

D6. Preview writes no course, source, manifest, journal, or rights record. The
server may hold an expiring staged upload as derived data. Acceptance must
re-read the staged bytes, match the preview fingerprint, and refuse a stale or
missing stage.

D7. Acceptance is resumable, not one giant transaction. Each completed object
is a valid atomic commit tied to one operation id. A crash leaves the accepted
prefix plus a manifest checkpoint. Resume skips matching accepted objects and
continues from the first non-terminal object.

D8. Undo restores the exact pre-job course and source state while retaining
the append-only operation and reversal evidence. It removes files that the job
minted, restores files it changed, and refuses on any divergent current byte.

D9. Rights are explicit at acceptance. Selecting a package does not grant
transform rights. The review screen records package-level defaults and any
per-resource override. Existing journal rights stay authoritative at each
adapter call.

D10. Assessment packages do not enter the ordinary Sources reader. QTI,
question banks, answer keys, quiz feedback, submissions, and grades receive
`assessment_review_required` or `excluded_private_learner_data`. A later
assessment-intake milestone must pass the runtime disclosure and scoring
contract before converting any of them.

## Durable acquisition manifest

Add `schemas/acquisition_manifest.schema.json` at version 1. The accepted
manifest is a journaled `component` stored at
`_acquisitions/<job_id>/manifest.json`. The staged upload is derived and is not
part of the durable course.

Required top-level fields:

| Field | Contract |
|---|---|
| `schema_version` | Integer `1`. |
| `job_id` | Opaque minted identity. |
| `operation_id` | Existing director operation identity. |
| `course_id` | Existing opaque course identity. |
| `provider` | Constant `canvas`. |
| `mode` | Constant `course_export`. |
| `input` | Original leaf name, package fingerprint, byte size, detected MIME, and capture time. Never an absolute path. |
| `access_basis` | `learner_provided_export` or `shared_authorized_export`. This records provenance, not copyright permission. |
| `rights_defaults` | The seven existing rights states. |
| `state` | `applying`, `partial`, `complete`, `cancelled`, or `failed`. |
| `organizations` | Ordered manifest organizations and nested placements. |
| `resources` | One row per discovered resource. |
| `counts` | Denominators for discovered, selected, ready, imported, reused, skipped, unsupported, restricted, failed, and conflicting. |
| `losses` | Typed losses with resource identity and next safe action. |
| `checkpoint` | Last terminal resource index and accepted manifest fingerprint. |

Each resource row contains a provider resource identifier, normalized package
member, title, declared type, detected MIME, byte size, content fingerprint,
all ordered placement paths, chosen adapter or null, rights snapshot, local raw
object id or null, derived source id or null, source and locator paths or null,
and exactly one outcome.

Preview outcomes are `ready`, `not_selected`, `unsupported`,
`assessment_review_required`, `external_reference`, `missing_member`, and
`unsafe_member`. Accepted outcomes are `imported`, `reused`, `skipped`,
`unsupported`, `restricted`, `failed`, and `conflict`. A completed or partial
manifest has no resource without one of these terminal outcomes.

The manifest must not contain a credential, cookie, authorization header,
browser profile path, absolute local path, quiz key, submission, grade, or
learner response.

## Public surface

Use one course operation named `acquire_canvas_export` with a closed `action`
vocabulary. This keeps the CLI, daemon, and generated MCP table on the shared
course-operation dispatcher.

```text
itembank acquire canvas-export COURSE EXPORT.imscc --preview
itembank acquire canvas-export COURSE EXPORT.imscc --accept \
  --preview-fingerprint SHA256 --grant read --grant transform
itembank acquire status COURSE JOB_ID
itembank acquire resume COURSE JOB_ID
itembank acquire undo COURSE JOB_ID
```

The browser first streams the selected file to a token-gated staging route.
The route returns an opaque `staging_id`, package fingerprint, size, and expiry.
No public JSON request accepts an absolute path or raw credential. CLI file
paths are read only by the local CLI process and translated to the same staged
package contract.

The course-operation request uses these action-specific identities:

- `preview`: `course_id`, `staging_id`.
- `accept`: `course_id`, `staging_id`, `preview_fingerprint`, selected resource
  ids, rights decisions, and expected course fingerprint.
- `status` and `resume`: `course_id`, `job_id`.
- `undo`: `course_id`, `job_id`, and expected current course fingerprint.

The output always returns `job_id` when durable work exists, manifest state,
the full count denominator, losses, next safe action, and an undo description.
It never returns assessment payload bytes.

## Near-term learner experience

U1. The Sources area gains `Add sources` and `Canvas export (.imscc)`. The file
picker says that no network connection or Canvas password is needed. It also
says that Canvas may hide full course export from student roles.

U2. Preview shows the Canvas module tree and five review groups: ready to
import, kept as external references, assessment content requiring separate
review, unsupported content, and unsafe or missing content. Every group shows
a count before any acceptance control.

U3. The rights step states what read and transform mean. Defaults remain
unknown. The learner can apply one decision to selected resources and inspect
per-resource exceptions.

U4. Import progress survives leaving the page. `Resume import` appears for a
partial or interrupted job. The completed view reports every denominator and
links imported sources under their original Canvas module placements.

U5. The primary next action is `Review imported sources`, followed by `Build
course map`. Undo stays visible beside the job report. It does not hide in a
global operation log.

## Existing ecosystem and reuse decisions

Do not invent a general scraper inside itembank. Existing projects are useful
as coverage evidence, capture providers, or optional tools. None should bypass
the acquisition manifest, source adapters, rights review, operation journal,
or accepted-revision boundary.

| Ref | Existing tool or format | Reuse decision | Boundary |
|---|---|---|---|
| R1 | [BrkBuilds Canvas Downloader](https://github.com/BrkBuilds/Canvas-Downloader) | Use its course-content coverage and sync behavior as research input for `canvas-api`. Do not vendor its GPL application code. | Its local database, downloader, transcription, and token lifecycle are a separate application authority. |
| R2 | [Canvas Course Downloader browser extension](https://github.com/jasp-nerd/canvas-course-downloader) | Use its MIT implementation as evidence that an active-session extension can collect modules, pages, files, assignments, discussions, announcements, quizzes, linked files, and a loss manifest. Evaluate code reuse only in the separate extension phase. | Default intake excludes grades, submissions, feedback, and other learner records. The extension must send selected captures through the same manifest and review flow. |
| R3 | [UCF CanvasAPI](https://github.com/ucfopen/canvasapi) | Use it as an API behavior and fixture reference. Reconsider it as an optional dependency during `canvas-api`. | The repository is stdlib-only today. A wrapper must not become a second persistence, retry, or operation authority. |
| R4 | [SingleFile](https://github.com/gildas-lormeau/SingleFile) | Support its self-contained HTML output through the existing local `web` adapter as the cheapest manual capture path. Add learner guidance before adding code. | A saved page is one source snapshot, not a course crawl, module graph, or proof that linked pages were captured. |
| R5 | [Browsertrix Crawler](https://crawler.docs.browsertrix.com/) and [WACZ](https://github.com/webrecorder/specs/blob/main/wacz/1.2.0/index.md) | Register a future WACZ import adapter and an external Browsertrix provider for high-fidelity, scoped captures. | Do not bundle its browser stack or persist its authenticated browser profile in a course. Treat WACZ as untrusted archive input. |
| R6 | [Playwright authentication](https://playwright.dev/docs/auth) | Use Playwright only for a visible, dedicated, temporary browser profile when an API cannot serve an approved route. | Authentication state can impersonate the learner. Never commit it, put it in a manifest, or reuse the learner's daily browser profile. |
| R7 | [ArchiveBox](https://docs.archivebox.io/latest/README.html), [Scrapy](https://docs.scrapy.org/en/master/topics/optimize.html), and [GNU Wget](https://www.gnu.org/software/wget/manual/html_node/Recursive-Download.html) | Allow future external-provider adapters for public sites and approved roots. Prefer an API or bulk export when available. | These tools may produce HTML, PDF, screenshots, WARC, or metadata, but they do not decide rights, identity, acceptance, or source truth. |
| R8 | [yt-dlp](https://github.com/yt-dlp/yt-dlp/blob/master/README.md), [ffprobe](https://ffmpeg.org/ffprobe.html), and [whisper.cpp](https://github.com/ggml-org/whisper.cpp) | Later add captions-first media intake with ffprobe detection. Use an approved yt-dlp executable for provider retrieval and prefer whisper.cpp for optional local ASR. | Provider terms and rights gate retrieval. Existing captions outrank generated text. Every transcript records media fingerprint, language, model, and confidence. |
| R9 | [H5P packages](https://h5p.org/specification) and [Open edX OLX](https://docs.openedx.org/en/latest/educators/olx/what-is-olx.html) | Register package inventory and static semantic extraction as later source adapters. | Never execute imported H5P JavaScript. QTI, grading rules, and interactive behavior remain assessment or runtime work, not source text. |
| R10 | [Google Drive export](https://developers.google.com/workspace/drive/api/reference/rest/v3/files/export), [Dropbox change detection](https://developers.dropbox.com/detecting-changes-guide), [Microsoft Graph delta](https://learn.microsoft.com/en-us/graph/api/driveitem-delta?view=graph-rest-1.0), and [Zotero local API](https://www.zotero.org/support/dev/web_api/v3/basics) | Treat these as later acquisition connectors, not scrapers. Reuse provider ids, revisions or cursors, content fingerprints, tombstones, and the common manifest. | Each connector needs its own credential, egress, deletion, conflict, and stale-state contract. Zotero's local read path is the lowest-risk first library connector. |

The practical order after `canvas-export` is:

P1. `canvas-api`, because it preserves provider identities and student-visible
module structure without scraping rendered pages.

P2. Saved-page and downloaded-folder intake, led by SingleFile-compatible HTML,
because most of the adaptation path already exists and needs no credential
storage.

P3. Captions-first media intake with explicit provider retrieval and optional
local ASR.

P4. WACZ import plus a Browsertrix or dedicated Playwright capture provider for
sites that need a real browser.

P5. Drive, Dropbox, OneDrive, and Zotero connectors. H5P, OLX, Moodle backup,
and other LMS packages stay Registered until a learner-owned fixture and real
need establish their order.

## Realistic later acquisition paths

L1. `canvas-api` should follow this milestone. Use an approved OAuth or token
profile stored outside course artifacts and journals. Discover only content
the calling learner can read. Reuse the manifest, outcomes, adapter routing,
checkpoints, and loss report proven by `canvas-export`. Add pagination, rate
limit recovery, conditional recheck, remote deletion tombstones, and per-call
egress records.

L2. Add Canvas student offline ZIP or HTML-package intake when one real export
is available for a fixture. It can reuse local staging without adding secrets,
but it must not claim module or object fidelity until the observed package
proves it.

L3. Prototype a dedicated browser session only when API credentials are
unavailable. Launch a separate visible browser profile, let the learner sign
in, capture only explicitly selected Canvas course routes, and pass response
snapshots through the web adapter. Do not extract cookies into course files.
Do not attach silently to the learner's everyday browser.

L4. A click-to-capture browser extension plus native messaging is the fallback
when institutional SSO cannot complete in the dedicated session. It requires a
separate signed-extension, permission, update, and uninstall contract. Keep it
Backburner until the API path has a real failed case it cannot serve.

L5. Do not build generic browser scraping, remote-debug attachment, credential
replay, or a headless login workaround. Those paths are hard to scope, brittle
under SSO, and likely to turn visible access into assumed download authority.

## Implementation packet

GOAL: An authorized Canvas `.imscc` completes preview, reviewed acceptance,
source adaptation, course registration, interruption and resume, exact undo,
and offline package restore with one outcome per discovered resource.

SCOPE: the acquisition manifest, hardened local package inventory, staging,
the `acquire_canvas_export` course operation, source-adapter operation markers,
created-file reversal, the Sources review flow, synthetic fixtures, and focused
verification.

DO NOT TOUCH: runtime scoring, keyed disclosure, evidence semantics, LTI,
model providers, ASR, live Canvas API credentials, browser sessions, generic
crawling, real banks, learner data, or unrelated Phase 20 presentation work.

TOOLS NEEDED: Python stdlib ZIP and XML libraries, current journal, director,
source adapters, course operations, daemon token gate, generated MCP table,
and a human-provided real export only for the final promotion check.

RETURN: changed paths, schema and route versions, fixture denominators, exact
commands and results, interruption point tested, undo byte comparison, offline
restore result, losses, large files sampled rather than fully read, and open
human or access decisions.

### A1. Close recovery gaps and freeze the schema

Owned files:

- `journal.py`, `director.py`
- `schemas/acquisition_manifest.schema.json`
- `tests/journal_roundtrip.py`, `tests/director_roundtrip.py`
- `tests/acquisition_roundtrip.py`

Add one journaled restore-to-absence mechanism for files minted by an
operation. It must prepare the reversal, verify the current fingerprint,
atomically move or remove the target, append the applied reversal, update the
registry to a tombstoned or absent state, and remain recoverable after a crash
between prepare and removal. Do not add a second general writer. Keep the six
frozen FILE-03 operation names unchanged and add only the internal recovery
record needed by `journal.undo`.

Make locator sidecars restorable members of the same operation as their source
Markdown. A reversal must remove a job-created pair or restore both previous
files. A fault may leave the old valid pair or new valid pair, never a mixed
pair.

Freeze the manifest fields and outcomes above. Test absent-file reversal,
sidecar-pair reversal, a crash before and after removal, stale-current-byte
refusal, and second undo idempotence before adding Canvas parsing.

Done when a synthetic operation mints two files, edits one file, reverses the
operation, and byte-compares the non-journal course tree to its pre-operation
snapshot.

### A2. Inventory Canvas Common Cartridge without writes

Owned files:

- `acquisition.py`
- `source_adapters.py`
- `tests/corpus_acquisition.py`
- `tests/acquisition_roundtrip.py`

Implement a public hardened archive-read helper and use it from both existing
container adapters and acquisition. Do not copy ZIP or XML safety logic into a
second module. Parse the package manifest namespace-aware. Preserve ordered
organizations, nested placements, resource identifiers, declared types,
normalized members, and external references.

Build one synthetic Canvas-shaped cartridge in the test corpus with two
modules, one resource referenced twice, HTML, PDF, VTT, an external URL, an
assignment descriptor, QTI, a missing member, equal bytes under two resource
ids, and an unsupported media file. Add adversarial variants for path
traversal, symlink members, entity input, excessive XML depth, duplicate member
names, expansion limits, and MIME mismatch.

Preview must leave the entire course root and journal byte-identical. Every
manifest resource receives a preview outcome and the count fields reconcile to
the resource denominator.

Done when the deterministic fixture previews with stable ordering and exact
counts, and every hostile fixture refuses before a write.

### A3. Accept, resume, and undo through existing authorities

Owned files:

- `acquisition.py`, `source_adapters.py`
- `surfaces/course_ops.py`, `schemas/course_operation.schema.json`
- `tests/acquisition_roundtrip.py`, `tests/course_ops_roundtrip.py`

Add an optional operation marker to the source import path and pass it to the
existing journal commit. This is the one deliberate additive reopening of the
Phase 14C public signature. Do not change existing call behavior, adapter keys,
locator fields, span joining, or error codes.

On accept, create one director operation and a journaled manifest. Mint each
selected raw member below `_acquisitions/<job_id>/raw/` with its explicit
rights record. Call `source_adapters.import_source` once per supported unique
resource. Add one Sources row per derived source through the course operation
authority. Attach the same operation id to every created or changed object and
checkpoint the manifest after each terminal resource.

Resume re-reads the journal and manifest. It must reuse matching completed
objects, refuse divergent same-id bytes, and never duplicate Sources rows or
module placements. Undo delegates to the improved operation reversal. It
removes the job-created manifest with the rest of the job-created tree while
the append-only journal reports the operation as reversed.

Done when kill-point tests after every durable commit all resume to the same
final fingerprints and exact counts, then one undo restores the pre-job course
tree byte for byte.

### A4. Publish CLI, API, MCP, and Sources UX

Owned files:

- `surfaces/cli.py`, `surfaces/daemon.py`, `surfaces/course_ops.py`
- `surfaces/home.py` or the current Sources-area owner after Phase 20 lands
- `schemas/course_operation.schema.json`, `schemas/api_request.schema.json`
- `tests/daemon_roundtrip.py`, `tests/mcp_roundtrip.py`
- `tests/acquisition_roundtrip.py`, the focused Sources UI roundtrip

Add the staged-upload route with token, size, expiry, containment, and cleanup
checks. Add the course operation and CLI commands above. Generate rather than
hand-maintain MCP request shapes. The UI uses the five U1 through U5 states and
visible controls. It remains keyboard usable, reflows at 320 CSS pixels, and
does not expose assessment bytes.

If Phase 20 changes the Sources-area owner before execution, re-resolve that
one file and update the plan before editing. Do not merge a stale UI patch into
the new surface.

Done when CLI, JSON API, MCP, and visible Sources flow return the same counts,
job identity, losses, next action, and refusal codes from one handler.

### A5. Prove restore and run the promotion gate

Owned files:

- `tests/acquisition_roundtrip.py`, `tests/packaging_roundtrip.py`
- the milestone summary and verification record created at execution time

Export the synthetic accepted course with the current package operation,
verify it, restore into an empty offline root, and resolve every imported
citation plus the acquisition manifest and Canvas placement path. Report any
deliberately excluded resource as a package loss rather than silently dropping
it.

Then run one learner-approved Canvas export through the visible path. Record
only safe metadata: Canvas role or access basis, package fingerprint, total
resource denominator, outcome counts, interruption point, undo comparison,
offline restore result, and losses. Keep the export and course outside this
repository.

Done only when the synthetic gates pass and the real package either passes or
leaves the milestone explicitly at Prototype with the exact failed resource
and next safe action.

## Acceptance gate

Run at minimum:

```text
python3 tests/acquisition_roundtrip.py
python3 tests/source_adapters_roundtrip.py
python3 tests/journal_roundtrip.py
python3 tests/director_roundtrip.py
python3 tests/course_ops_roundtrip.py
python3 tests/daemon_roundtrip.py
python3 tests/mcp_roundtrip.py
python3 tests/packaging_roundtrip.py
python3 schema_validate.py --all
python3 scripts/vision_audit.py
python3 scripts/preflight.py --quick
python3 itembank.py guard .
git diff --check -- <owned files>
```

The milestone passes when:

1. Preview is byte-for-byte read-only and names every discovered resource.
2. Accepted resources use current adapters, locators resolve offline, and no
   assessment key reaches a learner-facing source.
3. Every kill point resumes without duplicate sources or placements.
4. Undo restores the exact pre-job non-journal tree and rejects divergent
   current bytes.
5. Export, empty-root restore, CLI, API, MCP, and Sources UI agree on job
   identity, denominators, losses, and next safe action.

Human checks remain owed for the real Canvas package, the clarity of the
rights and loss review, and representative keyboard and screen-reader use. An
agent does not self-certify those checks.

## Unresolved decisions

Q1. Can Weibao currently obtain a full `.imscc`, a student offline ZIP, or
only browser-visible course content? This does not block the synthetic build.
It decides which real promotion gate can run.

Q2. What maximum staged and expanded package sizes fit the supported desktop
machines? Measure before freezing defaults. Start from the existing 200 MiB
source input cap, not an invented larger promise.

Q3. Should unsupported but non-assessment raw members be retained locally or
represented only by fingerprint and loss metadata? Decide from one real export
and package-size evidence.

Q4. Does the real Canvas export encode current New Quizzes content inside the
cartridge, as an external package, or as a named omission? Record the observed
case. Do not infer support from Classic Quizzes.

Q5. Which Phase 20 file owns the final Sources page when this milestone starts?
Resolve after the active UI plan lands to preserve one writer per surface.

## Next command

After Reach and the active Phase 20 writer are clear, turn A1 into the first
atomic execution plan:

```text
$gsd-plan-phase source-acquisition --goal "Make operation-created source and locator files exactly reversible, then freeze acquisition_manifest.schema.json"
```
