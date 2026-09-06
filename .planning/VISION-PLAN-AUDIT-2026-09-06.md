# Vision-to-plan audit, 2026-09-06

**Status:** active planning audit. This report is additive. It does not alter
user quotations, supersede historical decisions, claim behavior has been
verified, or authorize implementation work.

**Scope:** whole-vision trace through the active reach milestone and its
predecessor evidence. Read every dated vision and inbox heading, verbatim
quotation, and recorded planning-effect pointer. Read targeted interpretation
sections where a quotation affected the active route. Targeted reads:
`AGENT-WORKFLOW.md`, `SOURCE-TO-COURSE.md`, `STATE.md`, `ROADMAP.md`,
`REQUIREMENTS.md`, `IDEA-LEDGER.md`, Phase 16 synthesis sections 1 to 18,
`REACH-MILESTONE.md`, `19A-CONTEXT.md`, 14C context, and available phase
verification and audit records. The audit did not inspect implementation code,
all historical plan bodies, or execute learner UI flows.

## Authority reconciliation

| Source | Authority in this audit | Resolution |
|---|---|---|
| `USER-VISION.md` and promoted inbox statements | Desired outcomes, boundaries, and experience | Never rewritten. A prior summary or shipped artifact is not proof of satisfaction. |
| `SOURCE-TO-COURSE.md` | Binding current product direction | Defines the course-first, source-grounded product and authority boundaries. |
| `REQUIREMENTS.md`, `ROADMAP.md`, phase contexts | Current commitments, ownership, and sequencing | May bound work, but cannot silently narrow the vision. |
| Phase 16 synthesis and research | Evidence, design rationale, and dispositions | Prototype-gated recommendations are not commitments. |
| Runtime and verification records | Behavior actually verified | Documentary coverage is not implementation evidence. |

There is no unresolved conflict that authorizes a change of product direction.
The apparent conflict is one of claim scope: the reach milestone proves an
entrance and a first real use, while the vision asks for a durable course
workspace and learning product. `REACH-MILESTONE.md` already resolves this by
describing reach as a milestone rather than full-vision completion.

## Reconstructed product

### Exact user statements, retained in the vision record

- A course should be built from a book, syllabus, or other material, choosing
  readings, lessons, terms, notes, quizzes, and tests according to what helps.
  `USER-VISION.md` 2026-08-13, "source-to-course goal".
- Courses should have sound objective and assessment alignment, including
  standardized-test constraints, and be partially AI-drivable. 2026-08-13,
  "course generator, assessment alignment, UI, and agents".
- The product should have a comprehensive, coherent, visually appealing app
  flow with lessons, definitions, teaching blocks, tips, and course selection.
  2026-08-13 through 2026-08-26 UI and course-page entries.
- Existing lessons and question banks in separate folders or an Obsidian vault
  must be found and linked. Lesson files should remain useful outside the UI.
  2026-08-13, "finding prior work, progressive lessons, and agent skills".
- Learners may build notes through learning activities. Notes and lesson
  presentation require research before commitment. 2026-08-13,
  "guided highlighting, learner-built notes, and configurable learning paths".
- The product must become useful enough to finish and use without unbounded
  token waste. 2026-08-21 first-sitting entry and 2026-09-06 inbox entry.

### Interpretation and implementation choices, not user quotations

Course as the primary object, seven end-to-end loops, durable Markdown, one
parser and scoring authority, staged agent operations, operation journals,
semantic capability profiles, and the reach milestone are contract or plan
choices. They are consistent with the quotations but should not be represented
as direct user statements.

## Coverage matrix

| Vision outcome or boundary | Contract and requirement route | Execution / evidence route | Status |
|---|---|---|---|
| Source to objective to suitable treatment | Course-building loop; TREAT-01/02 | 15A, 19A-04 to 06, 19D | Partial, real-course proof pending |
| Existing files, provenance, roots, conflicts | Agent-operable workspace; FILE, ID, GRAPH | 14A to 14C, 17B, 19A-02/03/07 | Documented and fixture-tested, real-use linkage pending |
| Learn, practice, test, evidence, resume | Learner experience; FLOW, APP, ACTIVITY | 16B, 16D, 17A/17B, 19D | Partial, human and continuous-walkthrough legs pending |
| Notes and learner artifacts | Object model; NOTE-01 to 03 | 16C, 19D walkthrough | Documented, no real-course proof yet |
| AI course builder, reviewed writes, local backend | AI role; AGENT-01 to 03 | 15A/15B, 19B/19C/19D | Partial, backend and agent-door runs pending |
| Accessibility and plain-file fallback | Course-quality contract; APP and capability profiles | 16A to 17B, 19D | Contract and fixtures exist, human review owed |
| Export, recovery, and loss disclosure | Object model; FILE and reliability requirements | 14B, 17B/17C, 19A-08 | Known incomplete, five loss findings routed |
| Onboarding, external usefulness, multi-course breadth | Learner experience; APP-03 | 18, later registered work | Deliberately deferred, not a reach exit |

## Findings and dispositions

| ID | Severity | Exact source references | Affected plans | Rationale and disposition | Resolution status |
|---|---|---|---|---|---|
| VPA-01 | High | `USER-VISION.md` 2026-08-21 first sitting; `SOURCE-TO-COURSE.md` Learner experience; `REACH-MILESTONE.md` vision refinement F1 | 19A-09, 19B, 19D | Route and CLI parity cannot demonstrate that a learner can find, traverse, and return from the intended course flow. Existing direction correctly assigns a visible, no-guessed-URL walkthrough to 19D. | Open, already scoped. |
| VPA-02 | High | `USER-VISION.md` 2026-08-13 source-to-course goal; `SOURCE-TO-COURSE.md` Course-quality contract; `REACH-MILESTONE.md` F2-F3 | 19C, 19D | A diagnostic model run and one sitting do not demonstrate instructional quality. 19D must review source locators, objective demand, direct-reading choice, one accepted generated treatment, transfer, and evidence uncertainty. | Open, already scoped. |
| VPA-03 | High | `SOURCE-TO-COURSE.md` Agent-operable workspace; `REACH-MILESTONE.md` Phase 19C; `AGENT-WORKFLOW.md` sections 6-7 | 19C, 19D | The 19C gate retains output but does not expressly require a declared model profile, egress, rights basis, write authority, or fallback. The operation protocol requires them. This is a planning acceptance gap, not permission to widen backend capability. | Open. Add these fields to 19C context before execution. |
| VPA-04 | High | `AGENT-WORKFLOW.md` sections 6-7; `SOURCE-TO-COURSE.md` scope and export boundaries; `17C-AUDIT.md` F-LOSS-1 through F-LOSS-5 | 19A-08, 19D | Known restore losses mean a package can only be claimed with its loss report. The Math course may exercise export and recovery, but must not claim clean restoration until affected loss owners repair and rerun. | Open, explicitly routed to 19A-08 and existing loss owners. |
| VPA-05 | Medium | `USER-VISION.md` 2026-08-13 hierarchy/onboarding entry; `USER-VISION-INBOX.md` 2026-08-14 external-user v1; APP-03 | 18, future milestone | First-launch guidance, a removable sample, multiple-course hierarchy, and external-user usability matter to the vision but exceed the reach objective. Phase 18 and registered breadth retain them. | Deliberately deferred. Revisit after 19D defects are routed and Phase 18 human install is complete. |
| VPA-06 | Medium | `USER-VISION.md` 2026-08-13 note modes and OCR entries; `USER-VISION-INBOX.md` 2026-08-20 paper-note OCR; NOTE-01 to 03 | 14C, 16C, future capability runway | Notes, OCR, stylized outputs, and annotations are not accidentally omitted. They are registered or prototype-gated because they need provenance, privacy, accessible fallback, and review semantics. | Deliberately deferred. Revisit only on a real learner source or note workflow. |
| VPA-07 | Medium | `USER-VISION.md` 2026-08-26 Navigate2 and course-first-page entries; `SOURCE-TO-COURSE.md` Learner experience; APP-01/02 | 19A-09, 19D, 17B human legs | Course shelf, home navigation, reading surface, and visual coherence are contract-covered. Existing automated evidence does not substitute for the owed visual and screen-reader reviews. | Partial. Keep human legs visible. |
| VPA-08 | Low | `USER-VISION-INBOX.md` 2026-09-06; `AGENT-WORKFLOW.md` planning reading order and budget rules | All future planning | The user asks to reduce future waste. Bounded, symbol-first reading and reusing existing fixtures are sufficient scope controls. A new token-management feature is not warranted. | Resolved by existing workflow and 19D reuse instruction. |

## Bounded refinements

The active `REACH-MILESTONE.md` already contains the warranted refinement for
VPA-01, VPA-02, and VPA-07. This audit adds no competing requirement or phase.
Before 19C starts, its context must name the model and profile revision, local
or hosted egress and its rights basis, authority level, inputs retained on disk,
expected output paths, validation, and the manual fallback. Before 19A-08 or
19D claims recovery, attach the resulting package loss report and state whether
each known loss applies. These are acceptance evidence, not new features.

## Verification performed

- `python3 scripts/vision_audit.py` reports 31 vision entries, 12 inbox entries,
  no missing dated interpretations, no missing planning effects, no broken named
  files, and no inbox entry without a disposition.
- The same audit reports ten older interpretations without a named relationship
  to an earlier entry. It labels that list a backlog, not a failure. No entry was
  rewritten merely to silence it.
- Existing records establish that 17C found five silent restore losses and that
  17B and 18 retain human legs. This audit did not rerun their behavior tests.

## Completion condition for this audit

This audit is complete as a planning record when the active 19C and 19D contexts
cite VPA-03 and VPA-04 or equivalent named acceptance evidence. The broader
vision remains intentionally open until a later milestone explicitly accepts the
deferred product outcomes. No source supports a claim that the full vision is
already complete.
