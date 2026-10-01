# Implementation packets from older audits and backend research

Date: 2026-09-30. Writer: A. Integrator: C. These proposals retain existing
CAP/F ownership. They authorize no new format, installation, service, Git or
learner-file change. Read live bytes before leasing a production file.

## A1: find an admitted passage and return to the task

Route: CAP-06/07/04/15, APP-04, September 6 O8. Proposed registered slice.
Goal: from a synthetic course, search its admitted source passages and
explicitly included private notes, open one exact occurrence, then return to
the same task. This is local retrieval, with zero model egress.

Current seam: `surfaces/research_context.py::_safe_source`, `apply`, `panel`;
`source_adapters.py::resolve_context_scope`; existing source-note and reading
occurrence identities. `surfaces/discovery_cache.py` caches file classification,
not passage text. The sampled daemon catalogue has research-context routes but
no course passage-search route. This is a bounded absence finding, not proof
that every search facility is missing.

First action: C reproduces an actual query failure against this synthetic
context. Start with bounded literal search over the already resolved admitted
passages. Reuse source adapters and model parser exclusions. A bank's keyed
text is never a search corpus. Show duplicates as separate occurrences and
report unavailable/stale/excluded counts separately from zero hits. Avoid a
second discovery walk or a new canonical search database.

Gate: exact occurrence among duplicate quotes, source and private-note labels,
unknown/denied rights, excluded source, symlink escape, stale source, malformed
query, zero hit, canceled query, bounded input/output, task-return focus and
no response event. Verify fresh restart offline. Test the normal served route,
not just a helper. Reuse `tests/a5_research_context_roundtrip.py` and add only
the new query/return cases. Human accessibility stays separate.

Alternative: SQLite FTS5 over disposable snapshots if the simple scan fails a
measured latency or relevance task. Key by course, accepted revision,
fingerprint, locator and disclosure scope. Drop/rebuild after corruption or
rights change. A cached hit must be re-admitted against current owners before
showing a snippet. `sqlite-utils` supplies inspected FTS rebuild patterns;
stdlib SQLite avoids a new runtime dependency. Ranking is not relevance proof.
Direct import adds package dependencies and does not solve admission.

Recovery: search writes no accepted object, note, attempt or journal. Delete
only derived index state to rebuild. Do not send content to remote embedding
services. A semantic retrieval variant remains prototype until an actual
literal-search loss and approved model/span/egress operation exist.

## A2: expose and recover an interrupted author request

Route: CAP-05/24/18, older reuse audit retry row. Proposed registered slice.
Goal: show a named request while a model call is in flight; after restart,
explain whether it produced a persisted proposal, needs retry, was canceled or
failed. Accepted files remain unchanged until the existing accept path.

Current seam: `surfaces/agent_operation.py::start` creates the persisted
proposal only after `model_adapter.invoke` returns; the sampled path has no
durable pre-invoke attempt record. Existing four-state machine, `director`
checkpoint/outcome slots, journal locks, proposal IDs, source fingerprints and
acceptance/undo are the owners to reuse. `tests/agent_operation_roundtrip.py`
passes its current lifecycle checks. No claim is made that all long-job
systems lack checkpoints.

First action: C runs a delayed synthetic adapter in a disposable process and
reads Activity/status before completion, then interrupts it. Reconcile this
result with `director.resume_point` before selecting storage or adding states.
Use an existing operation checkpoint with a bounded attempt ID if its accepted
contract supports the needed facts. If it does not, prepare a binding-format
decision rather than silently extending canonical fields.

Gate: interrupt before invoke, during invoke, after candidate persistence and
during accept; restart resolves each to one explicit next action. Retry must
name parent attempt, recheck source/target fingerprints and never duplicate an
accepted write. Cancellation during backoff stops subsequent calls. Timeout
means unresolved transport outcome, not evidence that a remote service did
nothing. Test concurrent retry/accept, invalid response, auth refusal, source
change and unavailable backend with unchanged accepted bytes.

Compare: Huey has inspected SQLite queue, retry and revocation mechanisms;
OpenMAIC's existing pinned retry helper separates abort from retryable errors.
Adapt only bounded mechanics into the native journal/proposal path. Direct
Huey adoption creates task serialization, consumer lifecycle and shutdown
obligations; a dequeued task is not proof of exactly-once completion. Keep a
queue package registered for a measured multi-job requirement, not rejected.
No arbitrary pickle/task payload from learner or remote input is admitted.

Recovery: restart reads the native operation journal and proposals. Retry can
create a new draft but never implicitly accept one. Hosted calls retain exact
span/rights/egress declarations and potentially repeated-call cost disclosure.

## A3: test extraction losses before adding a richer extractor

Route: CAP-06/09/23, phase-16 source/reading-order and September 8 acquisition
records. Proposed prototype with a concrete promotion trigger.
Goal: compare native extraction with a pinned Docling adapter on one synthetic
two-column document containing a table, caption and duplicated phrase.

First action: native-only fixture first through `source_adapters.import_source`.
Record exact reading order, table-cell lineage, page locators and named losses.
Do not install Docling in this lane. An optional adapter packet becomes ready
only after an observed native loss and dependency/model approval.

Source: Docling conversion pipeline and document model were inspected at
`d6f03078ad364108df3e7e82e8f0dcc3fd7f39ea`. Code license is MIT; model weights,
OCR engines and optional adapters need separate rights and dependency pins.
Retain page provenance and table structure, not only flattened Markdown.
Normalize into the existing source/locator contract. Never parse a bank or
settle a score through the donor.

Gate: compare against independently authored page/row/cell truth, unavailable
model, encrypted/malformed input, cancel, timeout, oversized input, changed
source and clean offline restore. A nicer rendered paragraph does not prove
correct reading order. Revisit when a named accepted source fails native
table/layout fidelity. Model downloads, packaging and maintenance dominate
cost. Static text plus explicit loss remains the safe fallback.

## A4: protect extension and notebook trust boundaries

Route: CAP-25/12/17 and F4/F7/F8. Existing first-party registry remains core;
third-party and notebook adapters remain prototype/backburner.
Goal: show one declared capability with compatible version, useful fallback
and typed unavailable behavior; preserve notebook cell identity without
executing or trusting imported output.

Current seam: `extension_registry.build_registry` validates exact metadata,
callable handlers, versions, names and duplicates. Its focused test passes.
Pluggy's inspected `check_pending` and hook signature verification supply
compatibility ideas. Auto-loading installed entry points grants execution and
is a separate authority choice, not metadata validation.

Notebook source: nbformat's schema carries cell IDs; its signature store
checks a local HMAC-derived trust decision. Import admission, runtime scoring
and notebook-output trust are distinct. Read-only cell import may normalize
into existing source/learner-artifact owners; execution needs the declared
runner, interruption and file-recovery gates. No `.ipynb` was accepted here.

Gate: wrong version, unknown capability, missing fallback, malformed hook,
duplicate handler, untrusted HTML/JavaScript output, reused cell ID with changed
bytes, absent kernel, cancel and offline static reading. Do not execute an
import just because a notebook says it ran successfully. Revisit for a named
repeat authoring task or course notebook objective. Direct dependency reuse is
viable after the exact compatibility/license/packaging packet, not refused.

## Retained further mechanisms

These are not additional ready implementation actions. APScheduler misfire and
coalescing policy belongs to CAP-14/16 only when a named due-notification job
exists. Joplin diff-chain checkpoints belong to CAP-07/24 only after measured
history/storage pressure and package-history semantics. A py-fsrs comparator
belongs to CAP-14/26: native objective replay already exists, so define exact
rating/time/identity equivalence before claiming algorithm parity or replacing
it. Source pins and switching tests are in BACKEND-COMPARISON.md. No viable
mechanism was hard-rejected, and none grants a new authority by presentation.
