# Source-to-course transition audit synthesis

**Status:** authoritative transition record  
**Effective:** 2026-08-13  
**Scope:** reconcile the five completed audits with `USER-VISION.md`, the
current tree, and shipped behavior; govern the move from v1 to Phases 14–16  
**Does not supersede:** completed phase records, which remain historical evidence

## Verdict

The audits make sense in their central claim. The project did not build the
wrong foundation; it promoted an assessment subsystem into the product thesis.
The corrected composition is:

`course -> objectives and treatments -> sources, readings, lessons, examples,
visuals, practice, tests, and evidence`

The true goal is now adequately captured by `USER-VISION.md` and
`SOURCE-TO-COURSE.md`: source-owned course construction, deliberate direct
reading versus generation, high-quality learning UI, blueprint-appropriate
assessment, useful AI, local/hosted operation, and honest evidence. Remaining
gaps are contract and prototype questions, not ambiguity about the north star:
source-update semantics, objective/alignment schemas, artifact lifecycle and
undo, operation-scoped authority vocabulary, backend capability disclosure,
and the exact reader/guided/mobile interaction model.

## Audits reconciled

| Task | Scope | Accepted contribution |
|---|---|---|
| `019ff9b0-3f86-7ad3-b375-9635c8cbee75` | Phases 1–13/13.x | Compatibility and residue inventory |
| `019ff9b0-3f83-7cf2-8732-106794a8b794` | Learning UI and prior art | Course shelf/workspace, ordered mixed-treatment journey, inspectable map, mobile/accessibility cautions |
| `019ff9b0-3f7c-7383-ba18-fab6ed37f5d5` | Agentic course quality | Missing course schemas, operations, evaluations, and skill gates |
| `019ff9b0-3f8a-7161-a148-38fc3611f3c7` | Documentation hygiene | Authority, state, roadmap, handoff, archive, and research lifecycle |
| `019ff9b1-3be7-7813-b45a-d620add582cd` | Sectional learning-program landscape | Research-to-requirements taxonomy and evidence-strength cautions |

Consensus: course-first navigation; objectives as the spine; direct reading is
a valid terminal treatment; AI proposals are cited, bounded, reviewable, and
recoverable; assessment authority remains deterministic; evidence reports
denominators and uncertainty; accessibility/offline degradation are contract
fields from the start.

Complementary findings: the UI audit supplies interaction architecture; the
agent audit supplies schemas/evaluations; the hygiene audit supplies authority
and archive boundaries; landscape research supplies precedents and refusal
criteria. They reinforce rather than replace the user vision.

Contradictions resolved: the audits varied on whether to move all completed
phase folders immediately. We retain them in place for this transition because
a large move would obscure the existing reframe diff and offers no product
value by itself. The durable archive plan below schedules indexed moves later.
They also proposed many new skills; only proven errors in existing skills are
corrected now. New skills wait for the schemas and commands they must teach.

Unsupported proposals rejected: generic mastery percentages; time-on-page as
learning; engagement scores; automatic publication; unbounded filesystem
search; vector indexes as authority; model confidence as QA; an LMS dashboard
or chat pane as the primary UI; copying another product's protected content or
visual identity; assuming a local model is quality-equivalent to a hosted one.

Open prototypes: default outline versus graph map; source-update reconciliation;
semantic-diff granularity; accessible equivalence review; offline keyed-test
sync; item-family invariants; minimum evidence for misconception clustering;
and which local capabilities are sufficient per operation.

## Grievance ledger

Each material grievance has exactly one disposition.

| ID | Grievance | Disposition | Closure |
|---|---|---|---|
| G01 | Bank treated as the product/navigation unit | **correct now** | Active contracts and Phases 14–16 make course primary |
| G02 | AI framed only as tutor or late auditor | **correct now** | AI is builder, analyst, reviewer, and optional teacher |
| G03 | Runtime boundary inflated to prohibit useful AI teaching | **correct now** | Boundary narrowed to scoring, session/evidence, and keyed disclosure |
| G04 | Direct reading rewritten by default | **reject** | Treatment choice precedes generation |
| G05 | One mandatory lesson-check loop for every objective/subject | **reinterpret** | Preserve as one guided treatment pattern |
| G06 | Sparse evidence becomes `mastered` and drops from rotation | **correct now** | Evidence-state language and inspectable deprioritization |
| G07 | Global “full auditor autonomy” | **correct now** | Operation-scoped recommend/draft/approved-write authority |
| G08 | Source coverage terminates at bank item IDs | **reinterpret** | Item coverage is one facet of course coverage |
| G09 | No canonical course/source/objective/artifact lifecycle schemas | **open prototype** | Phase 14B discussion and schema tracer |
| G10 | Heading similarity treated as coverage | **reject** | Cited semantic alignment required |
| G11 | Standardized-test fidelity without a versioned blueprint | **reject** | Mapping required before fidelity claims |
| G12 | Knowledge courses forced into standardized-test distributions | **reject** | Follow actual syllabus and cognitive demand |
| G13 | Source changes and locator reconciliation unspecified | **open prototype** | Phase 14B |
| G14 | Accessibility/offline treated as polish | **correct now** | Required artifact metadata and exit tracers |
| G15 | Reader/guided/mobile IA not yet proven | **open prototype** | Phase 14B/16 realistic tracer |
| G16 | Daemon discovers banks, not courses | **migrate later** | Phase 14C adapter and course index |
| G17 | Lessons structurally subordinate to banks | **migrate later** | Bind shared parsed content as course artifact |
| G18 | Selection/cooldown is bank-scoped | **migrate later** | Assessment-set policy inside course/objective scope |
| G19 | Existing folders lack a lossless course binding | **migrate later** | Legacy unbound-course adapter |
| G20 | Generation pipeline requests only bank items | **migrate later** | Generic course proposal bundles in Phase 15 |
| G21 | Course semantic QA collapses into bank lint | **reject** | Named quality vector plus deterministic lint |
| G22 | Metrics omit missingness/alternatives/version context | **migrate later** | Metric interpretation objects in Phase 15 |
| G23 | Hosted/local backends silently degrade quality | **reject** | Capability negotiation and explicit unsupported results |
| G24 | Accepted mutation/undo is bank-specific | **migrate later** | Generic artifact transaction contract |
| G25 | New course skills lack executable schemas/evaluations | **preserve** | Existing interim prose guidance; expand only with product contracts |
| G26 | Rich roles are decorative card types | **reinterpret** | Semantic teaching roles with accessible degradation |
| G27 | Visual assessment primitives cannot teach unscored concepts | **migrate later** | Reuse semantic accessible actions for explanations |
| G28 | Phone support assumed secondary | **correct now** | Phone-width tracer and learner control required |
| G29 | Assisted activity success reported as summative mastery | **reject** | Keep assistance/mode/evidence context visible |
| G30 | Model connection required to open or use a course | **reject** | Reading, accepted lessons, scoring, evidence, and reports remain model-off |
| G31 | Root roadmap presents shipped work as future work | **archive/supersede** | Authority notice now; indexed archive later |
| G32 | State says no active phase | **correct now** | State points to Phase 14 transition contracts |
| G33 | Requirements retain Phase 12 and old product claims | **correct now** | Delivery mapping and active claims corrected |
| G34 | Closed handoffs can instruct agents to resume old branches | **archive/supersede** | Archive intact after consumer audit |
| G35 | Completed phase history overwhelms active planning | **archive/supersede** | Indexed v1 archive, no deletion |
| G36 | Stale research/probes appear authoritative | **archive/supersede** | Classify adopted/partial/rejected/superseded |
| G37 | USER-VISION could be normalized away | **preserve** | Verbatim additive file unchanged |

## Phases 1–13/13.x compatibility audit

Historical plans are not rewritten. This table governs their use now.

| Phase | Historical capability | Course-first disposition |
|---|---|---|
| 1 | Stable item identity, append-only evidence, migrations | Preserve; add course/objective/artifact identity above it |
| 2 | One daemon, settings, routes | Preserve transport; migrate discovery/home to courses |
| 2.1 | Packaging, update, export | Preserve; expose exports from course artifacts |
| 3 | Lesson parser and reader | Preserve; lesson becomes one treatment |
| 3.1 | Terms, callouts, style/accessibility | Preserve and broaden semantic roles; remove same-bank assumptions later |
| 3.2 | Source locators, provenance, seed/import | Preserve mechanics; reinterpret destination as objective/treatment |
| 4 | Shared responsive surfaces/tokens | Preserve; replace top-level bank IA |
| 5 | Deterministic code/check runner | Preserve for scored and unscored activities |
| 6 | Runtime hint ladder and feedback modes | Preserve for keyed assessment only |
| 6.1 | Semantic visual assessment actions | Preserve; extend to unscored explanations |
| 6.2 | Lesson gate/executable loop | Preserve as optional guided pattern, never universal wall |
| 7 | Explainable deterministic selector | Preserve inside Practice/Test; migrate scope |
| 8 | Provider-neutral model adapter/tier gate | Preserve; add course-builder operations |
| 9 | Shared subject rendering/profiles | Preserve primitives; supersede universal loop claim |
| 9.1 | Privacy-disclosed audio export | Preserve as unit/treatment/review export |
| 10 | Retention windows, trends, denominators | Preserve observations; supersede generic mastery semantics |
| 11 | Citations, findings, proposals, diffs, approval, undo | Preserve machinery; migrate from bank-only to course artifacts |
| 12 | Retired slot | Preserve retirement; delivery work belongs to 2.1 |
| 13 | Tauri shell over one Python sidecar | Preserve; render the course workspace through same transport |
| 999.x | Visual families, LTI, agent skills | Preserve as optional capabilities; bind through courses when relevant |

## Active wrong-direction claims and corrections

These claims were verified in the current tree. Completed phase files retain
their historical wording; the active sources are corrected or explicitly
superseded.

- `.planning/REQUIREMENTS.md:1` named an “AI-taught learning platform”;
  corrected to source-to-course.
- `.planning/REQUIREMENTS.md:97` used `mastered` dropout; corrected to
  evidence-bounded, inspectable deprioritization.
- `.planning/REQUIREMENTS.md:145` made source acquisition terminate in bank
  absorption; corrected to treatment choice.
- `.planning/REQUIREMENTS.md:216` exposed a local bank registry as the LTI
  product object; corrected to course/objective/artifact binding.
- `.planning/REQUIREMENTS.md:482-489` mapped delivery back to retired Phase 12;
  corrected to Phase 2.1.
- `.planning/PROJECT.md:12` and the authoring skills said six item types while
  `visual` and `check` ship; corrected to eight.
- `.planning/STATE.md:54` said no active phase; corrected to the Phase 14
  transition-contract stage.
- `ROADMAP.md:49-117` lists shipped foundations as future work; it now carries
  an authority notice and is scheduled for indexed archival, not silent rewrite.
- Historical residues remain intentionally visible at
  `.planning/phases/03.1-lesson-rich-blocks-glossary-style/03.1-CONTEXT.md:25`,
  `.planning/phases/07-selection-engine/07-CONTEXT.md:176`,
  `.planning/phases/09-subject-invariant-loop-emt-math-cs-integration/09-CONTEXT.md:40`,
  `.planning/phases/10-retention-pacing-trends/10-CONTEXT.md:9-34`, and
  `.planning/phases/11-closed-authoring-loop-curriculum-auditor/11-CONTEXT.md:17-39`.
  They are historical decisions governed by the compatibility table above.

## Shipped-to-proposed compatibility map

| Shipped now | Proposed course use | Migration rule |
|---|---|---|
| Markdown bank parser/linter | Practice/test artifact | Reference it; never parse twice |
| Runtime/scorer/sessions | Diagnostic, practice, test evidence | Course layer calls existing commands |
| Evidence log/index/trends | Objective observations and next-action input | Raw log remains authority; interpretations show context |
| `## LESSON` parser/reader | Guided or continuous lesson treatment | One parsed content model, two presentations |
| Terms/callouts/math/code/visual/check | Semantic learning activities | Declare accessibility, offline, and model fallback |
| Coverage/source locators | One assessment-coverage facet | Add objective/treatment/source edges above it |
| Seed/audit proposals/diffs/undo | Generic course artifact proposals | Generalize exact-write transaction, not authority |
| Selector/retention | Practice/test recommendation primitive | Invoke after learner chooses action; scope to course |
| Model adapter | Hosted/local course operations | Capability and privacy negotiation per operation |
| Daemon/Tauri/package/export | Delivery shell | Preserve one transport and bind course routes |

## Documentation authority and archive plan

Current reading order:

1. `AGENTS.md` — repository invariants and on-ramp.
2. `USER-VISION.md` — verbatim additive intent.
3. `SOURCE-TO-COURSE.md` — binding interpreted product contract.
4. This synthesis — transition decisions and grievance disposition.
5. `PROJECT.md`, `REQUIREMENTS.md`, `ROADMAP.md`, `UI-SPEC.md`, `STATE.md`.
6. Active phase package; then historical records only when needed.

Archive policy:

- Keep at most one live `.planning/HANDOFF.md`, only for interrupted current
  work. Move closed root, planning, and phase handoffs intact to
  `.planning/archive/v1/handoffs/` after checking automation consumers; index
  phase/date/final disposition/canonical summary. Do not delete unique branch or
  operational evidence.
- Move completed phase directories intact to `.planning/archive/v1/phases/`
  only in a dedicated mechanical transition after an index exists. Until then,
  this document labels them historical.
- Classify old research as `adopted`, `partially adopted`, `rejected`, or
  `superseded`; archive reports, but delete generated probes/prompts only after
  proving their content and outcome are duplicated and no tool consumes them.
- `.planning/HANDOFF.json` is a deletion candidate only after a consumer search.
- Later split durable UI/runtime/AI contracts from dated deliberation. Do not do
  a mass move inside this already-dirty correction set.

## Transition exit condition

The direction is correctly pointed now. Phase 14 implementation planning may
begin only after 14B closes the open prototypes with schemas, UI flows, and
evaluation fixtures. This transition itself is complete when documentation
checks verify authority, mirrors, links/commands, path hygiene, and tests—and
when the user agrees the projected product in `PROJECTED-PRODUCT.md` is the
experience they intend.
