# Fresh implementation evaluation, October 11, 2026

## Vision-first criteria

User authority: [the complete supplied brief](../USER-VISION.md#2026-10-11-complete-learner-owned-learning-workspace-brief)
and [the requested evaluation method](../USER-VISION-INBOX.md#2026-10-11-vision-first-implementation-and-improvement).
The brief was read first. Criteria and the initial implementation view were
stated before reading implementation or previous delivery reports. Existing
contracts were then read for compatibility and authority. This reduces one
source of anchoring; it cannot prove freedom from bias. No provider memory,
competitor feature claims or historical test totals establish current fitness.

The most valuable unit of delivery is a completed learner task with a durable
result and an obvious return. Evaluate that unit by time to useful work,
source traceability, cognitive demand, appropriate feedback, persistence,
rediscovery, keyboard access, offline behavior and recoverability. A test
count, component, backend or rendered screen is evidence of its own scope.
Human instructional quality remains a separate gate.

## How I would implement the brief

**D1, shared objects.** Use stable identities and revisions for sources,
locators, objectives, activities, learner notes, sittings, response evidence
and review schedules. An activity is a typed content object with objective
and source relationships; its presentation is replaceable. Viewed, reported
read, attempted, demonstrated and due are different facts. Start with readable
canonical files, validated atomic writes and an operation journal. Use SQLite
for disposable text indexes and derived queries when library scale warrants
it. Avoid requiring generation or network calls for ordinary navigation.

**D2, connected surfaces.** Build a common Home and Course shell around a
context-preserving task workspace. Reading, worked examples, note taking,
practice and review use that shell, while subject activities choose their own
composition. Every detour carries a useful return. Every saved artifact appears
in its course and can be found again. Home should explain the next action and
its evidence rather than displaying speculative mastery statistics.

**D3, authority and extensions.** Put deterministic response validation,
attempts, timing, disclosure and evidence in one runtime. Activity renderers
consume its public state. Model adapters operate on explicit selected context,
produce editable draft objects and record provenance. Open prose keeps machine
interpretation separate from a settled result. Code execution, visual activities
and synchronization need their own bounded contracts and fallback behavior.
Basic learning continues when a provider fails.

Build successive vertical slices. First, import a source and preserve it,
connect one objective, read, save a note, answer a suitable question, get useful
feedback, reopen progress and return. Then add review due and missed-item
practice. Next, make syllabus pacing, authoring, search and portability equally
complete. Expand subject activities through a shared registration boundary
after those core loops are usable. This is a dependency sequence, not a claim
that each subject can use the same teaching template.

## Credible alternatives and current fitness

| Question | Fresh alternative | Recommendation and switching criterion |
| --- | --- | --- |
| Canonical storage | SQLite owns all objects, with readable export | Attractive for high-volume transactions and relational queries. Readable canonical files currently fit explicit ownership and external editing. Retain them here; reconsider database authority only after representative library benchmarks and a tested lossless migration/restore demonstrate a better learner outcome. Prior effort is not the rationale. |
| App shell | Rebuild a new frontend and service around a clean activity API | A unified frontend may improve state and composition, but a rewrite alone does not complete a learner task. Improve a real current journey first. Prototype an alternative shell on the same content/runtime when an observed interaction problem cannot be resolved cleanly at the existing seam. |
| Discovery | Generate a new course immediately from an uploaded document | Faster initial visible output can hide prior work and provenance. Inventory approved roots, show reuse candidates, then fill one objective's actual gap. Measure time to useful practice; do not require exhaustive organization before the learner begins. |
| Notes retrieval | A global notes app or full workspace search | Both are viable. A course-scoped collection first proves that saved work is discoverable without reading keys, creating new storage or including notes in model context. Global search needs typed result adapters and explicit disclosure scope. |
| Delivery unit | Implement every listed mode before testing continuity | Preserve breadth in the routing table below, while shipping complete task loops. The current packet proves saved-note rediscovery only. |

## Bounded current-code comparison

**F1, a rediscovery gap.** The reading desk loads persisted private notes and
shows them beside a source. Learn offered an original-work link and activities,
but no saved-note collection or note query. Course source search deliberately
excludes private notes. A learner therefore had to reopen a reading to find
past wording, and removing an assignment could hide the ordinary entry point
even though the note files survived. Evidence: sampled reading view/save owner,
reading renderer, Learn extras, source-search contract and synthetic fixture.

**F2, reusable authority.** The current note document reader validates its pair,
schema, identity, private-root containment and accepted journal bytes. The
accepted reading graph and source validator already enforce revision and
source availability. Those boundaries fit D1 and D3 for this slice. This
finding supports reuse; it does not certify all product capabilities.

**F3, cost and limit.** File authority supports the proposed collection without
a new schema or data migration. The collection still reads the full private
note pair, then pages rendered results. Source admission happens only for the
displayed page and is cached by exact target. This is bounded rendering, not
a measured large-library performance guarantee. A disposable text index is
the next candidate if representative note libraries reveal a latency problem.

## Implemented packet

Owner: this local session. Writes: `surfaces/course_notes.py`, the Learn extras
and note shortcut in `surfaces/daemon.py`, optional reading-return admission in
`surfaces/routes/course.py`, the reading renderer's optional note return and
browse link, and `tests/course_notes_roundtrip.py`. Documentation lands here
and in the existing vision/inbox/idea owners. No learner files were changed.

The Learn page now offers My course notes. It reads the existing private note
document, searches wording and objective statements locally using Unicode
case folding, displays full escaped wording, authorship/status, objective and
target references, and pages twenty results at a time. Deleted notes are
excluded. The result count is a note count, never progress or mastery.

Matching current source readings are admitted through the existing accepted
graph and source validator, including exact source fingerprint, locator and
quoted-context hash. Following one preserves the query and result page in
the reading's return link and sibling reading navigation. The reader also
offers Browse my course notes. No caller-supplied redirect URL is used.

Changed or removed sources and removed assignments leave wording and objective
references visible, with unavailable reading links. Empty, no-match, invalid
query, invalid page, out-of-range page and note recovery states have explicit
paths back. Unsupported/conflicted note pairs do not yield partial snippets.
The Learn page's LAN preview does not load or display private notes, retaining
the existing reading desk's loopback privacy boundary. The feature performs
no model operation, source transformation, evidence append or accepted write.

Read scope: the opened local course's graph and private note document; source
validation for matching visible readings. Source of truth: existing canonical
files and authorities. Egress: none. Revision/conflict: existing note reader and
reading admission, with read-only recovery copy. Migration: none. Maintenance:
one small view module plus optional integration seams. Undo: reverse only this
packet's source/doc hunks and remove its two new files. Notes created through
normal use retain their original format and remain readable after code undo.

## Capability routing

This table routes the entire supplied brief by section number. It is an
implementation recommendation; it does not count an existing backend as a
finished capability or replace the existing milestone/contract. All rows are
owned by the linked vision's capability owners; current-code breadth outside
the notes slice was not audited.

| Brief sections | Disposition and concrete route | Dependency, cost and next gate |
| --- | --- | --- |
| 1, 33-36, 44 | Core: canonical local objects, provenance, backup, restore, explicit external-folder operations | Revision/rights/recovery owners; test clean offline restore with exact loss report before transport completion. |
| 2-3, 25, 29 | Core: inventory, intake, library and typed workspace retrieval | Source adapters and approved roots; next retrieval gate joins a real prior artifact to its course without exposing keys or silently importing notes. |
| 4-6 | Core: objective graph, treatment choice and sourced pacing | Course/treatment owners; verify syllabus dates, missing evidence and alternative paths in a real course. |
| 7-9, 28 | Core: connected Learn workspace and durable notes | Current packet implements saved-note rediscovery; broader annotations, contextual help and end-session follow-through require their own journeys. |
| 10, 20-22 | Prototype: thinking interactions, subject workspaces, editable visuals and notebooks | Activity/execution/accessibility owners; compare distinct subject tasks with static fallbacks before a new durable format. |
| 11, 19 | Registered: rapid card study and purposeful matching | Card/study owners; verify author/edit/study/reopen with history and keyboard/touch controls, including large-deck editing. |
| 12 | Core: retention state and review-due loop | Retention/evidence owner; verify scheduled return and transparent uncertainty, then benchmark a representative library. |
| 13-18 | Core: production-appropriate practice, feedback and distinct assessment | Runtime/model owners; verify misconception feedback, retry/disclosure, pending prose and missed-question return across subjects. |
| 23-24, 37-38 | Core: provider-independent drafts, authoring and review | Provider/authoring owners; verify failure recovery, save/edit/reopen and visible provenance without changing settled scoring. |
| 26-27 | Core: useful evidence views with distinct state axes | Evidence/progress owners; verify denominators and next-action usefulness in a real sitting. |
| 30-32 | Core: readable shell, responsive composition and keyboard access | Surface/theme owners; automation covers reflow, while screen-reader, physical touch and human preference need direct trials. |
| 39-43, 45-52 | Core: modular engineering and complete-task quality gates; Prototype for unevaluated adoption ideas | Existing workflow/quality owners; preserve all viable breadth and compare current behavior rather than repeating historical claims. Original synthetic content supports tests; human learning and installed delivery remain separate. |

No proposal is rejected. Global retrieval and indexed note search remain
Prototype recommendations pending scope and performance evidence. The code
packet uses accepted formats and does not promote the proposed architecture
alternatives or all future capabilities into new binding contracts.

## Verification and remaining acceptance

Gate receipts are recorded below after the final source revision. The intended
gate is an actual browser save, course reopen, case-insensitive note query,
source reading and exact query/page return, followed by reload and a fresh
process read. Synthetic recovery, escaped markup, pagination, deleted-note and
LAN privacy checks cover observed risks. Canonical bytes must remain unchanged
by retrieval. Accessibility automation does not certify human accessibility.

Large modules sampled by symbol: `course.py`, `notes.py`, `graph.py`,
`surfaces/daemon.py`, `surfaces/routes/course.py` and related test helpers.
The small new view module was read whole. Product contract, workflow and state
were read for binding scope; historical delivery records were not evidence for
success. External learner folders were not inventoried because this packet
does not author educational content or mutate learner data.

Next proposed product gate: measure normal-entry time to useful practice with
matched source/topic inputs and a next-day return. This packet leaves the
existing Product GM queue intact. The full application standard in the brief
is not satisfied by this slice. Global search, broad subject modes, real-course
instructional quality and installed/human acceptance are open at their existing
owners. Git commits, packaging and deployment were not requested or performed.


### Final gate receipt

- **T1:** new `tests/course_notes_roundtrip.py` passes seven cases: Unicode/objective retrieval, escaped wording, no-write reads including empty state, validation/recovery, stable pagination and exact second-page return, deletion, source/assignment loss, private pair conflict, LAN withholding, native reading return and fresh-process reopen.
- **T2:** actual headless installed-Chrome save plus six query/reload/reading-return journeys pass at 1280, 390 and 320, with JavaScript enabled and disabled. Dark mode at 390 and reduced motion were included. No page errors or horizontal overflow; retrieval preserves every fixture file. Final 320 script-free screenshot was visually inspected. Source metadata uses the source title and locator rather than an internal object identifier.
- **T3:** existing reading-desk suite passes seven cases, exact source-return integration passes eleven cases, and course-shell checks pass. These exercise the touched return/render seams; no full-product claim follows.
- **T4:** final `python3 scripts/preflight.py --quick` passes every executed gate, including the synthetic offline HTML build. It skips the broad Python/JS and clean-tree gates by design. Module-size warnings remain informational. A full app package or installed application was not built. Existing resource warnings in the native helpers remain outside this change.
- **T5:** skill mirrors match, scoped changed-code/doc whitespace checks pass, and the supplied brief round-trips exactly from its quotation. The whole diff's seven trailing-space notices are original Markdown line breaks in that verbatim brief and were preserved. Vision audit reports 94 vision entries, 99 inbox entries, zero missing dated interpretations and zero missing planning-effect fields. Its legacy path/link/relationship findings remain reported; this structural audit is not whole-product acceptance.

Ignored evidence: `.reasonix/fresh-vision-20261011/receipt.json`, `native.txt`,
`browser.json`, `browser-log.txt`, `preflight.txt`, `vision-audit.txt` and six
screenshots. Initial fixture mistakes were corrected: a folder name was used
instead of the course object's identity, and an exact browser link label omitted
the shell's arrow prefix. Those failures were test errors, not repaired product
regressions. The passing results above follow their correction.

Drift check: the original brief is exact, interpretation is separate, broader
architecture choices remain recommendations, every brief section has a route,
no rejection was added, existing authority formats remain intact, and mirror
parity holds. Current-code sampling and human/installed/performance limits are
explicit above. The new notes collection is a verified source slice; primary
learning-workspace usefulness still requires representative learner trials.


### Later October 11 comparison feedback

The user reports that a clean Quizlet-style study app built from a supplied
prompt was better than current Itembank and asks about archiving and restarting.
The [fresh candidate assessment](itembank-reset-2026-10-11/ASSESSMENT.md)
revisits the incremental-first recommendation above. Prefer a separate product
candidate, using the better existing clone if it passes the daily-study and
ownership gates, then layer the broader course vision. The note-rediscovery
slice remains useful at its bounded scope; it does not demonstrate that the
existing overall product is the best foundation. This is a recommendation,
not an executed archive or accepted architecture change.
