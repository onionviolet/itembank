# Source-to-reading readiness and next packet

Date: 2026-09-08.
Status: walkthrough and recovery investigation complete. Reading design below
is a proposal for a reversible prototype, not an accepted storage format.

## Outcome and route

The user authorized the populated-course walkthrough, reading-slice planning,
and exact recovery checks after asking what comes next. Efficient-agent-routing
selected one agent in the current task because navigation, source identity,
and recovery share context. No workers, provider calls, or new tasks were used.
The configured primary model was retained. No cost savings are claimed.

Reads were limited to this repository and the named routing skill. Runtime
writes went to disposable synthetic roots outside the repository. Durable
outputs are this packet, the diagnostic script, its JSON evidence, and a state
pointer. Real coursework was neither read nor changed. No commit was requested.

## Walkthrough evidence

The production daemon served two fictional courses created with
`fixtures.course_storyboard_corpus.build_two_course_shelf`. The first course
contained an unchanged copy of `fixtures/lesson_bank.md`. This is a real
production route exercise over synthetic content, not a real learner sitting.
The fixture had zero objectives and zero bound sources. It therefore proves
course and lesson navigation, not source binding or objective alignment.

| Step | Observed result |
|---|---|
| Shelf to Kestrel County Field Basics | Course overview showed one bank and zero recorded responses |
| Start reading | Actual lesson body opened with Back to course, Courses, and Continue to practice |
| Continue to practice | Runtime opened item 1 of 3 with response controls and the next locked hint tier |
| Submit synthetic option B | Runtime displayed Correct and kept item 1 visible until Continue |
| Continue | Item 2 appeared with a short-response field and pending-review wording |
| Your desk, reopen course | Overview showed one recorded response |
| Sit the items again | Session resumed at item 2 of 3 |

A screenshot of the reader showed readable text and visible navigation in the
in-app browser. This was one viewport inspection. It does not certify human
aesthetics, touch hardware, screen-reader behavior, 200 percent text, or 400
percent zoom. Those Phase 20 legs remain owed.

**F1: shelf resume wording is misleading.** After a recorded response, the
shelf still displayed Not started and Start Kestrel County Field Basics.
The underlying session resumed correctly. The sampled
`surfaces.ia._healthy_card` defaults missing `resume_cue` to Not started.
Owner: learner shelf projection. Disposition: open repair. Next action: derive
a truthful cue from canonical session evidence or show an explicitly unknown
state when no projection is available. Do not write a second progress store.
Gate: the same walkthrough shows a truthful resume cue and returns to item 2.

## Recovery evidence and dispositions

Reproduce with:

```bash
python3 .planning/research/source-to-reading/recovery_probe.py
```

The script uses real journal and adapter functions with disposable synthetic
objects. It prints observations rather than asserting that defects should
continue to exist. Exit zero means the probe ran, not that recovery passed.
The captured [JSON](research/source-to-reading/recovery-probe-2026-09-08.json)
contains four failed acceptance observations and one passing conflict check.

| Ref | Observed failure | Owner and next gate |
|---|---|---|
| R1 | `director.reverse_operation` returned `complete: true` with no reversed entries while the newly minted file remained | Director reversal must account for every durable mutation and refuse a complete claim when any remains |
| R2 | `journal.undo` turned a newly minted source into a zero-byte file instead of restoring absence | Journal must model prior absence explicitly and restore it under the existing lock, fingerprint, registry, and replay rules |
| R3 | Undo of a PDF import retained both empty Markdown and its locator sidecar. An injected pre-commit RuntimeError returned `source.internal_error` but left an orphan sidecar | Source adapter and journal must pair derived Markdown and locator metadata in recoverable state, including interruption and retry |

All three are open and block a claim of exact import or batch-job undo.
R3's interruption was an exception injection at `journal.commit_operation`,
not an OS process-kill experiment. Existing journal kill and disk-full tests
passed, but they do not establish paired adapter recovery.

**C1 passed:** undo refused an external divergent edit with `journal.conflict`
and preserved its bytes. The imported raw PDF also remained unchanged.
Preserve these behaviors in any repair.

## Proposed reading slice

The smallest observable result is one existing authorized local source range
opened from a course, returned to the same activity, and explicitly marked
read without a score or mastery claim. Reuse the source and its binding.
No downloader or generated lesson is required.

The [combined audit](SOURCE-TO-READING-COMBINED-AUDIT-2026-09-08.md) owns the
semantic proposal. The binding product contract already permits direct
reading and keeps runtime assessment authority unchanged. Current
`schemas/course_graph.schema.json` contains direct-reading treatment and a
locator, but no complete reading-occurrence record. The existing
`evidence.lesson_complete_event` is bank and lesson-heading based. Its dedupe
identity does not distinguish two reading occurrences over shared content.
It must not be reused unchanged to claim independent reading completion.

| Proposed responsibility | Existing authority or proposed representation |
|---|---|
| Course and objective identity | Existing course graph and stable IDs |
| Source revision and exact range | Reference accepted source identity, journal revision and locator metadata. Do not copy source truth into a card |
| Reading occurrence | Proposed stable occurrence ID and references to course, objectives, source revision, range, and treatment |
| Learning and activation | Occurrence-scoped Ahead/Deepen/Prove and Now/Next/Library. Allow not-applicable where the job has no relevant axis |
| Sequence and scope | Published/Bounded/Provisional remains separate from activation. Record assigned versus selected range and who chose it |
| Assistance and time | Explicit assistance and any deadline or estimate, with provenance. Elapsed time and scrolling do not mean completion |
| Reading completion | Learner-declared descriptive occurrence event through the one evidence writer. Never a response score or mastery event |
| Return context | Derived course, occurrence and locator navigation state. It cannot authorize a source read or durable write |

Proposed prototype flow: Course Learn shows a synthetic Ahead/Now reading.
Open source resolves the exact accepted range or reports unavailable with a
safe return. Back returns to that occurrence. Mark read changes only its
descriptive state. A separately activated Deepen occurrence references the
same content and starts incomplete. A Published/Library occurrence stays off
the daily view until deliberately activated.

Source rights are checked at opening and mutation boundaries. Unknown rights
remain restrictive. Remote egress is zero for this slice. A missing revision
or locator must not silently fall back to unrelated or newer content. New
source revisions affect only linked future work after review. Historical
reading and assessment evidence remain attached to their original revisions.

## Next ready packet

**D1: prototype the occurrence contract before changing durable formats.**
Owner: source-to-reading coordinator, with one writer for the coupled UI.
This authorization covers the plan. It does not silently accept a new schema.
The next implementation packet should stay bounded to the following work:

1. Build a disposable occurrence fixture around an existing local source and
   binding. Inventory current course and source APIs first. No import is needed.
2. Render the flow above through the existing course and reader seams, with
   explicit synthetic state. Keep the plain source useful outside the app.
3. Verify independent completion, Library exclusion, exact locator failure,
   rights refusal, return context, and no scoring or evidence mutation by the
   prototype. Include keyboard checks and retain human review as owed.
4. Present the smallest contract delta for review in SOURCE-TO-COURSE.md.
   Settle occurrence storage and the additive evidence schema before durable
   completion writes. Legacy records keep unknown history rather than inferred
   learning phase, assistance, or completion.
5. Before durable import work, resolve R1 through R3 through the journal owner.
   Require creation, edit, divergent bytes, repeated undo, interruption,
   sidecar pairing, registry reconstruction, and offline restore tests.

Primary implementation seams to inspect are `course.bind_source`,
`course.bind_treatment`, `surfaces.course_ops._op_bindings`, the course Learn
renderer and `surfaces.daemon._lesson_context_nav`. Completion design must
inspect `evidence.lesson_complete_event` and the canonical event schemas.
Recovery changes belong to `journal.undo`, `director.reverse_operation`,
and source adapter import composition. Do not create another parser, scorer,
source identity system, or evidence store.

Stop and revise the design if two occurrences require duplicate content,
completion leaks across occurrences, unavailable content appears complete,
or a prototype needs to mutate accepted truth. These falsify the slice.

Canvas acquisition, Drive, ASR, external calendars, and batch imports remain
backburner under the combined audit. Revisit after local reading has a verified
contract and actual user access justifies acquisition. Local model parity stays
separately deferred. Neither dependency blocks a read-only local prototype.

## Verification and limits

`tests/journal_roundtrip.py` passed, including before/after-commit kill,
disk-full, permission-denied, and concurrency checks.
`tests/source_adapters_roundtrip.py` passed. Their success does not cover the
newly demonstrated exact-recovery gaps.

Quick preflight passed lint, broken fixture, build, guard, README commands,
schemas, vendored artifacts, paths, and summaries. It failed the skill mirror
gate because `.agents/skills/author-bank/_attempts` exists only on one side.
This task did not create or alter that directory. Full preflight was not rerun
because this packet changes no production code and targeted checks cover the
investigation. Existing model-parity debt is not claimed resolved.

Existing uncommitted Phase 20 edits were preserved. Another untracked
`tests/responsive_product_roundtrip.py` appeared during this run and was left
untouched. Large modules were sampled by the symbols named above. This is not
an exhaustive code, accessibility, vision, or source-policy audit.

Drift check: the 2026-09-08 adopted learner UI remains the visual direction.
The proposed occurrence model stays distinct from accepted schema authority.
Direct reading remains a valid treatment. No existing idea was rejected or
removed, and no human acceptance was claimed.

Recovery for this planning change is removal of these newly added packet and
probe files and the narrowly added state pointer. Existing files and learner
objects require no rollback from this investigation.
