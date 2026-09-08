# Pace-course and Itembank architecture audit

Date: 2026-09-08.
Status: read-only audit findings and recommendations, not an accepted format or implementation plan.
Scope: the repository working state, including pre-existing uncommitted changes.

## Answer

Itembank has much of the source-binding foundation, but `pace-course` remains an agent workflow rather than a complete Itembank reading feature. The missing connection is a first-class reading activity with explicit scope, source revision, preparation state, assistance and descriptive completion evidence.

## Inputs and verification limits

Read the pace-course skill and its `references/reading-to-itembank.md`, efficient-agent-routing and its provider mapping, the product contract, agent workflow, current state, and relevant user-vision entries. Sampled relevant schemas and symbols in discovery, identity, journal, course, graph, source adapters, evidence, day, course operations, daemon and packaging code. Inspected relevant test references and the existing source-acquisition audit.

Executed CLI help for the root command, `source`, and `import`. No behavioral suites or learner UI walkthrough were run. Large parser, runtime, daemon and test modules were not read wholesale. This is not a release certification or exhaustive vision audit. No implementation files were changed by the audit.

## Current-state map

| Ref | Capability | Status | Evidence |
|---|---|---|---|
| F1 | Multi-root inventory, fingerprints, unavailable/denied states and cancellation | Implemented | `discovery.inventory`, `discovery.run_report`. Approval is partly the caller's responsibility. |
| F2 | IDs, revisions, rights, link/import/copy/move/supersede, reconciliation and undo | Implemented primitives | `identity.py`, `journal.op_link` through `op_supersede`, `detect_external_edits`, `reconcile`, `undo`. Complete learner UI parity was not established. |
| F3 | Source/treatment bindings, direct reading, source adaptation and locators | Implemented | `schemas/course_graph.schema.json` binding definition, `course.bind_source`, `course.bind_treatment`, `source_adapters.import_source`. |
| F4 | Published/bounded/provisional reading, familiarity, time budget, assistance and recheck tracking | Specified-only as a combined protocol | pace-course reading-to-itembank reference. No complete first-class reading contract was found in searched Python and JSON schemas. |
| F5 | Authenticated course acquisition, incremental remote sync, calendar reconciliation and automatic dependency propagation | Missing or incomplete | Source-acquisition audit proposes acquisition. `surfaces.course_ops._op_staleness` classifies caller-supplied dependents rather than discovering the complete chain. |

## Q1. What pace-course creates today

The skill directs an agent to acquire permitted originals, record snapshot manifests when useful, reconcile an existing accepted course artifact, select reading ranges and dates, and optionally create missing teaching or practice. It preserves superseded material and reports posting dependencies.

It is not an executable pipeline with fixed output paths or guaranteed Itembank writes. Calendar entries need a separate operation. The skill does not implement event IDs or calendar reconciliation.

Its persistence record is `course | class/topic | evidence state | source version and locator | reading range | time budget | targets | completion evidence | next recheck`.

The reference labels `source_state`, `acquisition_status`, `coverage`, `source_version`, `mode` and `assistance` as protocol fields until supported directly. Related coverage, revision and assessment-mode concepts already exist elsewhere in Itembank. Their existence does not implement this complete reading record.

## Q2. Proposed learner flow

1. Enter through Course Learn or Day. Show topic, assigned versus agent-selected range, published/bounded/provisional status, estimated time and recheck. Never invent a provisional deadline.
2. Open the exact source location. Distinguish the accepted snapshot from the original and preserve the activity's place on return.
3. Use the selected treatment. Familiarity normally takes 5 to 10 minutes. A coherent pre-read normally takes 20 to 35 minutes. These are defaults, not completion requirements.
4. Record descriptive completion and attempt closed-source recall. Distinguish marked-read from a saved response. Label source access and assistance. Closing an in-app source does not prove absence of outside help.
5. Continue according to evidence. Exposure means contact, guided performance means supported work, and independent retrieval may support readiness. Neither a checkbox nor one answer establishes mastery.

`surfaces/day.py:DAY_LANES` and `parse_plan` implement dated Markdown tables and lane completion, not a general course-activity contract. `evidence.lesson_complete_event` exists but uses a bank/lesson/objective shape.

## Q3. Artifacts and modes

Use both, with separation driven by ownership and evidence meaning. Original sources remain source-owned with provenance and permitted snapshots. Accepted familiarity guides, summaries and lessons are authored files. Learner notes and recall responses remain learner-owned. Validated assessment artifacts feed runtime-owned sessions and disclosure.

Continuous and guided presentations may share parsed content. Familiarity can reuse terms and orientation without another file. Separately authored summaries need their own provenance and revisions. Practice and test activities may reuse validated items through permitted runtime modes.

HTML, indexes, course cards and calendar projections remain derived. They are not accepted content or assessment authority.

## Q4. External discovery and binding

Local primitives exist. Inventory reads approved roots. Linking records an identity without rewriting file bytes. Binding connects a registered object to an objective or treatment.

Import and copy mint new identities and source provenance. Move retains identity and changes location. Supersede preserves both identities and their relationship. General ongoing synchronization was not demonstrated.

`identity.RIGHTS_OPERATIONS` separates read, quote, transform, remote_process, package, export and share. Unknown rights stay restrictive. Import and copy currently consume transform rights. Names are hints rather than identity. Discovery grants neither mutation nor upload authority.

No complete external-folder to learner-activity to relocation to restore UI walkthrough was performed. The broader product model also names objects and relationships beyond those proven in implemented schemas.

## Q5. External resource representation

| Resource | Representation and boundary |
|---|---|
| Textbook/PDF | Edition, source ID, accepted fingerprint and page/section range. Preserve printed-page versus PDF-page distinctions. PDF adaptation exists. |
| Canvas/Drive/web | Provider identity, locator, revision/capture metadata and access state. Public web capture exists. Authenticated Canvas acquisition is proposed. Native Drive acquisition was not established. |
| Obsidian notes | Link existing files with identity and fingerprint. Preserve learner ownership and vault links. Discovery does not authorize rewriting. |
| Flashcards | Retain external deck identity or explicitly import candidates. `itembank import anki` exists. Imported cards are not automatically approved assessment items. |
| Calendar | External scheduling record linked to a canonical activity. Scheduled time and completion flags are not source or scoring authority. Sync was not found in inspected commands. |

An external link must not silently become a local copy. Offline availability must disclose remote-only dependencies.

## Q6. Source changes and failures

`source_adapters.recheck_origin` is deliberately read-only. Remote drift or an unreachable origin does not invalidate citations to an accepted snapshot. Local external edits have detection and reconciliation primitives.

`surfaces.course_ops._op_staleness` accepts supplied dependent rows. It does not establish automatic propagation through readings, summaries, lessons, objectives, items and calendar events.

Recommended behavior: preserve history, flag affected future use, and review the smallest affected dependency set. Changed emphasis may only change a reading range. Changed answers require item review or quarantine. A disappeared origin may leave a usable permitted snapshot. Unknown rights and policy prohibitions block affected operations without inventing permission.

Historical attempts remain historical. Current applicability may change without rewriting scores or automatically transferring evidence to revised objectives.

## Q7. Promotion to practice

Require permitted generation, stable objective wording and exact locators, independently checked answers or rubrics, original scope that does not imitate collected work, and explicit forecast status. Published and stable bounded objectives may qualify. Provisional objectives never enter graded or mastery-scored quizzes.

Release requires policy/source review, lint/schema validation, statistics and coverage review, and a runtime smoke test. Reading completion, summaries, notes, assisted repetition and model judgments never silently become assessment authority. Prose remains pending until an authorized marking action settles it.

## Q8. Interface constraints

Preserve accessible interactions and useful static fallbacks, local canonical files, declared remote processing, recoverable writes, runtime-owned keyed disclosure and learner control over notes and exports. Offline states distinguish usable snapshots from unavailable remote-only resources.

Package/restore machinery exists in `course_package.py`, including manifests and loss reporting. An export promise still requires a clean restore of the relevant slice. Current STATE explicitly records skipped human visual and screen-reader review, not passed accessibility certification.

## Q9. Prioritized gaps and decisions

| Ref | Decision | Rationale |
|---|---|---|
| D1 | Smallest reading-activity contract and owner | Treatment bindings lack the combined timing, forecast, assistance and completion semantics. |
| D2 | Preparation versus assessment evidence | Prevent read, recognized, assisted and independently ready from collapsing into mastery. |
| D3 | Dependency review and policy-change behavior | Fingerprints and staleness classification do not establish the complete rescoping workflow. |
| D4 | Calendar ownership and reconciliation | Distinguish instructor deadlines from learner plans, round-trip edits, duplicates and timezone changes. |
| D5 | One external reading end to end | Prove link, opening, return, completion, recall, source change, denied transformation and offline losses before provider breadth. |

Questions to resolve within those decisions: Can assigned reading finish without generation? Can policy change without erasing history? How is assistance recorded honestly? Who accepts a changed range? How does one source serve courses with different policies?

## Copy-ready follow-up prompt

### Outcome

Settle and document one bounded Itembank reading-activity contract. Produce only the next executable packet for an end-to-end direct-reading slice.

### Context

Use this repository and read AGENTS.md, relevant USER-VISION entries, SOURCE-TO-COURSE.md, AGENT-WORKFLOW.md and current STATE.md. Use pace-course with its reading-to-itembank reference and efficient-agent-routing. Read this audit and refresh its relevant symbols against the working tree.

Existing foundations include discovery, identity/journal operations, course bindings, source adapters/locators, runtime evidence, Day tables and package/restore. Reading protocol fields are not established as one first-class activity. Remote-origin rechecks do not invalidate accepted snapshots. Course staleness consumes supplied dependency rows. Preserve concurrent work.

### Scope

Resolve reading ownership, revision/range, published/bounded/provisional state, time budget, assistance, descriptive completion, closed-source recall, dependency review and day/calendar ownership. Reuse existing contracts. Keep source, accepted content, learner notes, runtime evidence and derived views distinct.

Discovery authorizes neither mutation nor remote processing. Preserve one parser, one scorer, runtime disclosure, restrictive unknown rights, expected-base writes, atomic acceptance, journal and recovery. Do not implement Canvas/Drive acquisition or calendar sync. Do not edit code or commit. Update only necessary owning planning documents without duplicating acquisition or Phase 20 plans.

### Execution

One GPT-6 Astra agent at low reasoning, no delegation. Unresolved activity/evidence/recovery boundaries warrant the frontier tier. After decisions settle, route implementation to one GPT-5.6 Terra agent at medium reasoning unless a named unresolved risk requires more. This is capability-based routing, not measured cost savings.

### Acceptance gate

Provide a field/owner/state map distinguishing existing, additive and deferred concepts. Show Course/Day to exact source opening, return, descriptive completion and permitted recall. Define checks for source change, missing source, unknown rights, policy prohibition, assistance, offline availability, restore losses and keyed disclosure. Name exact symbols and tests for only the next slice. Preserve history and prohibit automatic mastery credit or evidence transfer. Record unresolved decisions and never certify unperformed human accessibility review.
