# Phase 15A: Director & Treatment Policy - Research

**Researched:** 2026-08-14
**Domain:** Agent operation protocol, treatment recommendation, rights/egress
gating, and cross-backend parity over an unexecuted identity/journal/graph
foundation (Phases 14A and 14B, both planned but not yet on disk).
**Confidence:** MEDIUM. Every architectural conclusion that depends on the
14A/14B API is grounded in *plan text read this session*, not in a verified
running module (see "Critical caveat" immediately below). Everything about the
shipped Phase 8 model adapter, tier gate, and Phase 11 auditor is grounded in
real, executed source code read this session.

## Critical caveat: Phase 15A's entire dependency chain is unexecuted

Confirmed by direct filesystem check this session
(`identity.py`, `journal.py`, `discovery.py`, `graph.py`, `course.py`,
`course_package.py` all `MISSING` at repo root; `.planning/phases/14A-*/` and
`14B-*/` contain only `*-PLAN.md` files, no `*-SUMMARY.md`; `.planning/phases/
13.9-walking-skeleton/` likewise has only `*-PLAN.md` files):

- **Phase 13.9** (walking skeleton) has not been executed.
- **Phase 14A** (identity, journal, discovery) has not been executed.
- **Phase 14B** (graph, course sidecar, course package) has not been executed.
- **Phase 15A is next in a chain of three unexecuted phases.**

This is expected sequencing, not a defect: ROADMAP.md's own Phase 15A entry
states "Phase 14B is planned but not yet executed, so every 14B and 14A
signature this phase imports is read from plan text at planning time; the
first 15A plan opens with a recorded precondition check that halts by name on
any divergence, the same pattern plan 14B-01 set." `[VERIFIED:
ROADMAP.md:1643-1647]` (quoted verbatim above).

Consequences for the 15A plan the planner writes:

1. Every function signature, constant, and refusal code cited below as "from
   14A" or "from 14B" is `[VERIFIED: 14A-0N-PLAN.md]` / `[VERIFIED:
   14B-0N-PLAN.md]` (a planning artifact read in full this session, with the
   exact line range and verbatim quote given at each citation) and **not**
   `[VERIFIED: identity.py]` or `[VERIFIED: graph.py]`, because those modules
   do not exist on disk to read.
2. The first 15A plan must open with a precondition check, following the
   exact pattern `14B-01-PLAN.md` Task 1 already used against 14A (see Code
   Examples below): confirm `14A-FREEZE.md` and `14B-FREEZE.md` both exist and
   carry their respective `## Frozen at 14A` / `## Frozen at 14B` sections,
   and that the live constants match what this research and the 15A plan were
   written against. If either phase's real implementation deviated from its
   plan during execution, 15A's plan must be re-verified against the
   `*-FREEZE.md` records, not against this research.
3. Per ROADMAP's Phase 13.9 governance clause ("no 14B-or-later freeze closes
   before this has been walked", `[VERIFIED: ROADMAP.md:104]`), the 15A
   freeze gate (the four-subject recommendation review) also requires 13.9
   evidence to exist, exactly as `14B-06-PLAN.md`'s freeze task already checks
   it (`[VERIFIED: 14B-06-PLAN.md:21]`, quoted: "No 14B freeze closes before
   Phase 13.9 has been walked: the freeze task checks for the recorded 13.9
   evidence as a precondition, and on its absence writes a Freeze withheld
   section"). The 15A freeze task should carry the same precondition.
4. This research is safe to use for **planning** 15A now (per
   `PLANNING-DIRECTIVES.md` section 5: "Claude plans... execution is
   transcription"), but the plan must name the precondition explicitly as its
   first task.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| TREAT-01 | Every objective has an explicit, reviewable treatment from the eleven-kind vocabulary; direct reading is a complete result, generation never automatic. `[VERIFIED: REQUIREMENTS.md:496-506]` | 14B-03's `graph.TREATMENT_KINDS` (eleven values, closed) and `course.bind_treatment` already gate treatment assignment by rights; 15A's recommender proposes a `treatment_kind` from that same closed vocabulary and writes through `course.bind_treatment`, never inventing a twelfth value or a parallel enum. |
| TREAT-02 | Every objective-to-source coverage claim carries a locator, confidence, and one of five states (covered, thin, missing, conflicting, unknown); heading similarity never produces covered. `[VERIFIED: REQUIREMENTS.md:508-515]` | 14B-03's `graph.BINDING_STATES = ("covered", "thin", "missing", "conflicting", "unknown")` is the exact closed vocabulary. **Pitfall:** the shipped Phase 11 `auditor.coverage_report` uses a *different*, older state vocabulary (`"gap"`, `"partial"`, `"unknown"`, `"conflicting"`, `"covered"`) that predates TREAT-02 and must not be conflated with it (see Common Pitfalls). |
| RIGHTS-02 | Hosted operations minimize and disclose exact egress; agents receive only approved source spans and operation authority; presentation visibility is never authorization. `[VERIFIED: REQUIREMENTS.md:706-715]` | No egress-log module exists yet in any executed or planned code. 15A must design and build it fresh, reusing `identity.rights_state`/`identity.rights_granted` (from 14A-03, unexecuted) for the rights half and `model_adapter.py`'s existing typed request/result envelope (shipped, executed) as the transport boundary the egress log wraps. |
| RELIABILITY-02 | Agent and maintenance operations run through a durable local operation journal with intent, actor, scopes, checkpoints, and undo, shared across hosted/local/manual continuation. `[VERIFIED: REQUIREMENTS.md:794-802]` | 14A-02's `journal.py` (compare-and-swap write path, append-only `journal.jsonl`, `commit_operation`, `undo`) is the one operation journal already frozen (pending execution) for this exact purpose. 15A must NOT build a second journal; it records agent operations as journal entries through 14A's existing `journal.py` surface, extended additively if a new record shape is needed (following the precedent 14A-03 and 14B-04 already set of adding one new `RECORD_TYPES`/`OPERATION_TYPES` member per plan). |
| AGENT-01 | All clients implement one operation protocol (intent, authority, inventory, treatment plan, checkpoint, draft, cite, validate, preview, diff, review, atomic accept, staleness update, undo/uncertainty report). `[VERIFIED: REQUIREMENTS.md:881-893]` | `.claude/skills/OPERATION-CONTRACT.md` (and its byte-identical mirror `.agents/skills/OPERATION-CONTRACT.md`) already states this thirteen-step protocol in prose and names which steps have shipped surfaces today. 15A's job is to make the protocol *checkable* against a journal, not to re-invent it: the four-subject recommendation review replays a recorded operation step by step against this checklist. |
| AGENT-02 | Hosted and registered local backends reach the same operations and schemas; backend choice changes capability/latency/cost/disclosure, not the artifact or authority contract. `[VERIFIED: REQUIREMENTS.md:895-907]` | `model_adapter.py`'s shipped `TRANSPORT_REGISTRY` (`hosted_cli`, `openai_compatible`) plus `settings.model_backend.profiles` is the existing, executed backend-parity mechanism (D-17/D-18/D-27, `[VERIFIED: schemas/settings.schema.json:199-246]`). 15A's mock-hosted/mock-local fixture is a new profile pair registered the same way Phase 8 already registers profiles, not a new dispatcher. |
</phase_requirements>

## Summary

Phase 15A adds one new capability, the treatment/coverage recommender, on top
of three layers that already have a designed (though largely unexecuted)
shape: 14A's identity/rights/journal kernel, 14B's typed graph with its
closed treatment and binding-state vocabularies and its rights-gated
`bind_source`/`bind_treatment` calls, and Phase 8's shipped model-adapter
transport registry and tier gate. The correct architecture is additive
composition, not a fourth parallel system: a recommendation is a *proposal*
that an agent client drafts and a reviewer accepts through `course.py`'s
existing (planned) bind calls; the operation that produced it is a journal
entry through 14A's `journal.py`; the backend that generated it is a
`model_backend.profiles` entry read through `model_adapter.py`'s existing
`invoke()` boundary; and the egress it required is a new, narrow log this
phase must design, because nothing in the shipped or planned code owns egress
disclosure yet.

The single highest-risk design decision this phase must make and lock is:
**what wire boundary carries a treatment recommendation from an agent to the
graph, and is it a new `model_adapter.py` operation (a fourth member of the
closed `["hint", "rubric_review", "author"]` enum) or a separate, journal-only
path that never goes through the tier-gated learner-facing adapter at all?**
Recommendation: **a new, separate path**, not a fourth adapter operation,
because `model_adapter.py`'s three existing operations are all learner-facing
(hint, rubric marking, item authoring) and route through the tier gate's
five-step no-leak algorithm, which is architecturally wrong for a
course-builder-facing treatment proposal that has no learner tier to gate
against and instead needs a *rights* gate. Building a fourth adapter
operation would either bypass the tier gate (inconsistent with why the gate
exists) or force treatment recommendations through machinery designed to
protect a different asymmetry (model sees the key, learner must not).

**Primary recommendation:** build the treatment recommender as a course-tier
operation that (a) calls `model_adapter.invoke()` directly with a new
`operation` value added additively to the adapter schema's closed enum
(`["hint", "rubric_review", "author", "treatment_recommend"]`), since
`model_adapter.py`'s request/result envelope, typed-failure discipline, and
`TRANSPORT_REGISTRY` backend parity are exactly what AGENT-02 needs and
duplicating them is the one thing this research forbids; (b) never routes a
`treatment_recommend` response through `tier_gate.py` (wrong tool: no
learner-facing disclosure boundary applies to a course-builder recommendation)
but instead through a new, narrower validation this phase builds: schema
validation plus a rights check against `identity.rights_state`; and (c)
records every recommendation operation as a `journal.py` entry so
RELIABILITY-02's resume/undo/checkpoint requirement is satisfied by the one
journal, never a second one.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Treatment recommendation (the model's proposal) | Agent client (hosted CLI or local backend, via `model_adapter.invoke()`) | Course tier (`course.py`, receives the proposal) | The model drafts; it never writes. `model_adapter.py` is the shipped boundary for exactly this shape of typed request/typed result. |
| Treatment acceptance (binding the recommendation) | Course tier (`course.py`'s planned `bind_treatment`) | Runtime tier (`journal.py`'s compare-and-swap write) | TREAT-01/RIGHTS-01: a binding is a durable write gated by rights, already designed in 14B-03 as a `course.py` function that calls `journal.commit_operation` underneath. 15A supplies the proposal; it reuses the write path, it does not add one. |
| Coverage-state computation (TREAT-02) | Model tier (`graph.py`, pure, no I/O) | Course tier (`course.py`, orchestrates the read) | `graph.BINDING_STATES` is a pure closed-vocabulary classification over data already in the sidecar; it must stay a pure function per 14B's "no I/O in graph.py" rule, consistent with the model-tier split identity.py/graph.py already establish. |
| Operation journal (RELIABILITY-02) | Runtime tier (`journal.py`) | N/A | One journal, already frozen (pending execution) in 14A-02. 15A must not create `agent_journal.py` or any second append-only log. |
| Egress log and manifest (RIGHTS-02) | Agent client tier (new module this phase builds) | Runtime tier (journal entries record egress as a field, not a second store) | No shipped or planned module owns "what left the machine and to whom" today. This is 15A's one genuinely new durable object; it should be a field set added to the existing journal entry, not a sibling log, to avoid duplicating RELIABILITY-02's single-journal rule. |
| Backend parity (AGENT-02) | Agent client tier (`model_adapter.py`'s `TRANSPORT_REGISTRY`, shipped) | Settings tier (`model_backend.profiles`, shipped schema) | Already built and executed in Phase 8. 15A registers a `treatment_recommend`-capable profile pair (mock hosted, mock local) the same way, not a new dispatcher. |
| Autonomy levels (recommend-only / draft-and-review / approved bounded writes) | Agent client tier, enforced at the `course.py` write call | Reviewer (human), who is the actual gate for anything above recommend-only | `OPERATION-CONTRACT.md` step 11 already names these three levels in prose; 15A is where they become a checked field on the operation record, read by `course.py` before a bounded write is allowed to proceed unreviewed. |
| Direct-reading-as-complete-treatment (TREAT-01's "generation never automatic") | Course tier (`course.bind_treatment` with `treatment_kind="direct-reading"`) | Agent client tier (the recommender must be able to emit this as its top recommendation, not only as a fallback) | 14B-03's own test fixture already proves `direct-reading` binds against a source whose `read` right is unknown and refuses exactly like every other treatment kind; the recommender must not special-case it as "no bind needed." |

## Standard Stack

This phase adds no new third-party dependency and no new runtime. It composes
existing or already-planned Python-stdlib-only modules.

### Core (already shipped and executed)

| Module | Status | Purpose | Why reused, not rebuilt |
|--------|--------|---------|--------------------------|
| `model_adapter.py` | Shipped, executed (Phase 8) `[VERIFIED: model_adapter.py:1-96]` | Typed `invoke(request, settings)` boundary; `TRANSPORT_REGISTRY` for `hosted_cli`/`openai_compatible`; `request_from_operation`; `unavailable_result`; `ADAPTER_CODES` | AGENT-02's exact "same operations and schemas across backends" requirement, already built. Do not fork a second transport layer. |
| `tier_gate.py` | Shipped, executed (Phase 8) `[VERIFIED: tier_gate.py:1-60]` | Deterministic, fail-closed boundary between provider output and a *learner-facing* payload; five-step no-leak algorithm | Cited as the pattern for "how this codebase gates model output", but its authority (protect against a model over-disclosing to a *learner*) does not map onto a *course-builder* recommendation review. 15A needs a rights gate, not a tier gate; see Summary. |
| `auditor.py` | Shipped, executed (Phase 11) `[VERIFIED: auditor.py:370-484]` | `coverage_report()`, a citation-first coverage transform with its own five-state vocabulary | Do not reuse its state vocabulary for TREAT-02 (see Common Pitfalls); its citation-discipline pattern (empty/null/mismatched citation is never `covered`) is the right pattern to copy into `graph.py`'s TREAT-02 classification, even though the state names differ. |
| `evidence.py` | Shipped, executed | Append-only evidence log, `KNOWN_EVENT_TYPES` closed-vocabulary read discipline | 15A's AGENT-03-adjacent proposal work (owned by 15B, not 15A) will read evidence; 15A itself must not import `evidence` from any new course-tier module it adds, following the same structural ban `course.py` already carries (`[VERIFIED: 14B-04-PLAN.md:22]`: "course.py structurally cannot transfer evidence: the imported module exposes no attribute named evidence"). |
| `settings.schema.json` / `surfaces/settings.py` | Shipped, executed | `model_backend.profiles` registry: `transport` enum `["hosted_cli", "openai_compatible"]`, per-profile `secret_env`, timeout, output cap, context window | The exact registered-backend mechanism AGENT-02 needs; a third transport is "a `TRANSPORT_REGISTRY` entry, not a code fork (D-27)" `[VERIFIED: schemas/settings.schema.json:205]`. |

### Core (planned, not yet executed - 14A/14B)

| Module | Status | Purpose | Why reused, not rebuilt |
|--------|--------|---------|--------------------------|
| `identity.py` | Planned `[VERIFIED: 14A-01-PLAN.md:110-147]` | `rights_default()`, `rights_state(record, operation)`, `rights_granted(record, operation)`, `RIGHTS_STATES = ("granted", "denied", "unknown")`, `RIGHTS_OPERATIONS` (seven names) | RIGHTS-02's rights half is this exact function pair, already used at 14A-03's `op_import`/`op_copy` gate and 14B-03's `bind_source`/`bind_treatment` gate. A second rights vocabulary anywhere in 15A is the exact regression 14B-03's own key_links section names as the failure mode. |
| `journal.py` | Planned `[VERIFIED: 14A-02-PLAN.md:104-141]` | `commit_operation`, append-only `journal.jsonl`, `entries()`, `replay()`, `undo()`, `OPERATION_TYPES` (six, frozen), `RECORD_TYPES` (additive) | RELIABILITY-02's one operation journal. 15A's agent-operation record is a new `RECORD_TYPES` member (following the precedent 14A-03's `reconcile` and 14B-04's `migrate` already set), never a second journal file. |
| `graph.py` | Planned `[VERIFIED: 14B-02-PLAN.md:107-119, 14B-03-PLAN.md:101-114]` | `TREATMENT_KINDS` (eleven, closed), `TREATMENT_RIGHTS` (eleven-key map), `BINDING_STATES` (five, closed, TREAT-02's exact vocabulary), `treatment_right(kind)` | TREAT-01/TREAT-02's closed vocabularies already exist in plan text. 15A's recommender must propose only members of `TREATMENT_KINDS` and classify only into `BINDING_STATES`. |
| `course.py` | Planned `[VERIFIED: 14B-01-PLAN.md:119-127, 14B-03-PLAN.md:116-121]` | `bind_source`, `bind_treatment`, `rights_for_binding`, `read_course`, `write_course` | The one write path for a course sidecar. A treatment recommendation becomes durable only by calling `course.bind_treatment`; 15A never writes the sidecar directly. |
| `course_package.py` | Planned `[VERIFIED: 14B-01-PLAN.md:128-134]` | Package export/restore, rights-gated payload inclusion | Not directly consumed by 15A's freeze gate, but the egress-log design this phase builds should follow the same "gate at the moment of the operation, never at export" rule 14B-03 establishes for bindings (`[VERIFIED: 14B-03-PLAN.md:38-40]`). |

### New in this phase

| Component | Purpose | Why it is new |
|-----------|---------|----------------|
| A `treatment_recommend` adapter operation (additive enum member on `schemas/model_adapter.schema.json`'s closed `operation` enum, currently `["hint", "rubric_review", "author"]` `[VERIFIED: schemas/model_adapter.schema.json:26-29]`) | Carries a treatment/coverage proposal request and result through the existing typed boundary | No existing operation shape fits: `hint` and `rubric_review` are learner-facing and tier-gated; `author` is bounded item-drafting. A recommendation is course-scope, not item- or learner-scope. |
| An egress manifest/log (new fields on a `journal.py` entry, or a new `journal.RECORD_TYPES` member `agent_operation`) | RIGHTS-02: "hosted operations minimize and disclose exact egress" | Nothing existing owns this. Must be designed to extend the one journal, not create a second store. |
| A recommendation validation pass (new, narrow function, not `tier_gate.py`) | Schema-validate a `treatment_recommend` result and re-check rights against the live registry (never a cached snapshot), following the exact discipline 14B-03's `bind_source`/`bind_treatment` already apply | `tier_gate.py`'s five-step algorithm is purpose-built for learner-facing fact disclosure; reusing it for a course-builder recommendation would import an unrelated authority model. |
| A synthetic four-subject corpus extension to `fixtures/corpus_14b.py` | The freeze-gate fixture (see Validation Architecture) | `fixtures/corpus_14b.py`'s planned `build_three_domains` already builds three fictional domains standing in for EMT/Math/CS (`meridian-field-response`, `orrery-algebra`, `lantern-computing`, `[VERIFIED: 14B-02-PLAN.md:85]`); 15A's fourth domain (a standardized-exam blueprint) is an addition to that same generator, not a new one. |

### Alternatives Considered

| Instead of | Could use | Tradeoff |
|------------|-----------|----------|
| Extending `model_adapter.py`'s closed operation enum | A wholly separate adapter module for course-scope operations | Rejected: duplicates the typed-envelope, `TRANSPORT_REGISTRY`, and profile-resolution machinery AGENT-02 explicitly requires stay shared across backends. The existing enum is additive by design (`operation` is a plain JSON Schema `enum`, not a closed keyword the validator refuses to extend). |
| A rights re-check at bind time (query the live registry) | Trusting a rights snapshot carried on the recommendation | Rejected on the same grounds 14B-03 already rejected it for bindings: "the `rights_snapshot` column exists for history only... if any code path ever reads it to decide whether an operation may proceed, a revoked right stays effective forever" `[VERIFIED: 14B-03-PLAN.md:33]` (Pitfall 5). |
| Recording egress as fields on the existing journal entry | A dedicated `egress_log.jsonl` sibling file | The dedicated-file option is defensible (egress is a different concern from object mutation) but risks becoming a second "operation journal" in spirit even if not in RELIABILITY-02's literal member count. Recommend fields on the journal entry (e.g. `egress: {spans: [...], destination: "hosted"}`) unless the 15A plan finds a concrete reason a sibling file is needed; either way, this is a `checkpoint:decision` for the plan, not something this research should silently resolve. |

## Package Legitimacy Audit

Not applicable. This phase installs no new external package; it is pure
Python-stdlib composition over existing and planned in-repo modules, per the
project's stated preference (still a preference, not a rule, per the
2026-08-09 constraint relaxation) and the fact that no research question in
this phase's scope names a new library.

## Architecture Patterns

### System Architecture Diagram

```text
 Agent client (Claude Code / Codex / local backend)
   |
   |  1. declare intent + authority (OPERATION-CONTRACT.md step 1-2)
   v
 journal.py  --------------------------------------------+
   | commit_operation("agent_operation", ...)             |
   | (checkpoint recorded here; RELIABILITY-02)            |
   v                                                       |
 model_adapter.invoke(request, settings)                   |
   operation = "treatment_recommend"  (NEW enum member)    |
   |  routes through TRANSPORT_REGISTRY                     |
   |  [hosted_cli]  <-- profile: mock-hosted / real Claude   |
   |  [openai_compatible] <-- profile: mock-local / real Qwen|
   v                                                        |
 candidate treatment proposal (typed result, "ok"/"refused"/"unavailable")
   |
   |  2. egress recorded: exact source spans sent, exact backend used
   v                                                        |
 recommendation validation (NEW, narrow -- schema + rights, not tier_gate.py)
   | reads identity.rights_state(source_record, treatment_right(kind))
   | LIVE registry read, never a cached snapshot (Pitfall 5)
   v
 [refused: rights_not_granted] ---------> journaled as "refused", nothing written
   |
   | granted
   v
 course.bind_treatment(...) --> graph.add_binding(...) --> course.write_course(...)
   | (existing 14B-03 write path: compare-and-swap through journal.commit_operation)
   v
 course sidecar (course-graph.md), one kind=course object, one revision lineage
   |
   v
 reviewer (recommend-only | draft-and-review | approved-bounded-write autonomy level)
   | accept / reject, recorded per OPERATION-CONTRACT.md steps 10-13
   v
 accepted binding, staleness/dependency state updated, undo path recorded in journal
```

A reader can trace the primary use case (an agent proposes a treatment for one
objective, and it becomes a reviewed binding) from the top (agent declares
intent) to the bottom (accepted binding, undo recorded) by following the
arrows: nothing is written to the course sidecar without passing through the
rights re-check and the one journal, and the tier-gated learner-facing path
(`tier_gate.py`) never appears in this diagram because it gates a different
asymmetry.

### Recommended Project Structure

No new top-level package is warranted; this phase's new code is root-level
peer modules, following every prior phase's precedent (`identity.py`,
`journal.py`, `graph.py`, `course.py` are all root-level peers of `model.py`,
`runtime.py`, `evidence.py`).

```text
<repo root>/
├── model_adapter.py       # existing; gains "treatment_recommend" in the operation enum
├── tier_gate.py            # existing; UNCHANGED by this phase
├── identity.py             # planned by 14A; consumed, not modified structurally
├── journal.py               # planned by 14A; gains one RECORD_TYPES member for agent operations
├── graph.py                  # planned by 14B; consumed for TREATMENT_KINDS / BINDING_STATES
├── course.py                  # planned by 14B; consumed for bind_source / bind_treatment
├── director.py                 # NEW (name is this research's proposal, a checkpoint:decision
│                                  candidate) -- the treatment recommender and its rights/egress
│                                  gate, calling model_adapter.invoke() and course.bind_treatment()
├── schemas/
│   ├── model_adapter.schema.json   # existing; "operation" enum gains one member
│   └── course_graph.schema.json    # planned by 14B; unchanged by this phase
├── fixtures/
│   └── corpus_14b.py            # planned by 14B; gains a fourth synthetic domain
│                                   (standardized-exam blueprint) for the freeze fixture
└── tests/
    └── four_subject_review.py   # NEW, following tests/three_domain_tracer.py's
                                    and tests/file_fault_tracer.py's structure
                                    (fail(msg), scenario_*(), main(), "TRACER: N passed" line)
```

### Pattern 1: Precondition check against an unexecuted prior phase

**What:** Before importing a module a dependency phase has only planned (not
executed), the plan's first task runs a live import-and-constant-check and
halts by name on any divergence.
**When to use:** Any time a plan's `depends_on` phase may not have executed
yet relative to when the plan is written, which is true for every subphase
14B onward right now.
**Example (from the shipped precedent, quoted verbatim):**

```text
# Source: 14B-01-PLAN.md, Task 1 "verify Phase 14A landed, or halt by name"
1. Check that the three 14A modules import. Run
   `python -c "import identity, journal, discovery; print('modules present')"`.
   Expected stdout: `modules present`, exit code 0.

2. Check that the frozen constants match what Phase 14B was planned against.
   Run a single `python -c` that asserts, in this order, every one of the
   following, printing `14A surface matches` on success:
   - `identity.OBJECT_KINDS` equals `("course", "objective", "source",
     "lesson", "bank", "component")`.
   ...
```
`[VERIFIED: 14B-01-PLAN.md:176-190]`

The 15A plan's first task should be the same shape, checking both
`14A-FREEZE.md` and `14B-FREEZE.md` for their `## Frozen at ...` sections and
re-asserting the constants this research cites (`graph.TREATMENT_KINDS`,
`graph.BINDING_STATES`, `identity.RIGHTS_STATES`, `journal.OPERATION_TYPES`).

### Pattern 2: Rights re-checked live, never trusted from a snapshot

**What:** A rights-gated operation reads `identity.rights_state`/
`identity.rights_granted` against the *current* registry at the moment of the
operation; any snapshot value carried on a record is historical only and is
never read back for an authorization decision.
**When to use:** Every point 15A's recommender or its write path needs to
know whether an operation is permitted.
**Example (quoted from the planned precedent this phase must follow):**

```text
# Source: 14B-03-PLAN.md, "No stale snapshot ever authorizes (Pitfall 5)"
- After a successful bind, the written row's `rights_snapshot` cell records the
  state at bind time.
- Change the source's rights record so the same operation now reads `denied`,
  then call the same binding again for a second objective. It refuses with
  `course.rights_not_granted` naming `denied`, even though the earlier binding
  row still shows `granted`. The current registry decides; the snapshot never
  does.
```
`[VERIFIED: 14B-03-PLAN.md:201-209]`

### Pattern 3: One closed vocabulary, validated at write time, skip-and-warn at read time

**What:** A new enumerable concept (treatment kinds, binding states, operation
types, adapter operations) is a plain tuple constant, validated with a raise
on write and a skip-and-warn on an unrecognized value at read, never a second
parser.
**When to use:** The `treatment_recommend` operation's own result shape;
15A's recommendation autonomy-level field.
**Example:**

```text
# Source: 14A-03-PLAN.md, "Task 1" read_first note, citing the established precedent
- `evidence.py` lines 51 to 55 (`KNOWN_EVENT_TYPES`) and lines 755 to 774
  (`events`, the skip-and-warn-on-unknown read discipline), the closed-vocabulary
  precedent this task mirrors.
```
`[VERIFIED: 14A-03-PLAN.md:146-148]`

### Anti-Patterns to Avoid

- **A fourth write path.** Any code that writes the course sidecar, the
  journal, or an egress record without going through `course.write_course`
  (planned) / `journal.commit_operation` (planned) is the exact regression
  14A-RESEARCH.md's own Pattern 3 warns against for the six operations, and
  the same discipline applies to a seventh consumer (the recommender) of the
  one write path.
- **A second rights vocabulary.** `RIGHTS_STATES`, the seven `RIGHTS_OPERATIONS`
  names, and `TREATMENT_RIGHTS`'s mapping from treatment kind to consumed
  right already exist in plan text; inventing a parallel "can-egress"
  boolean or a different three-state name set anywhere in 15A breaks
  non-negotiable 2 (one parser, one scorer, one evidence store's spirit
  extended structurally to "one rights vocabulary").
- **Routing a course-builder recommendation through `tier_gate.py`.** The gate
  exists to stop a model from over-disclosing to a *learner* mid-sitting; a
  treatment recommendation has no learner-facing tier to protect and instead
  needs a rights check. Using the wrong gate either weakens the tier gate's
  contract or produces confusing refusal codes that mean the wrong thing.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Cross-backend request/result parity | A second typed envelope or dispatcher for course-scope operations | `model_adapter.py`'s `invoke()`, `TRANSPORT_REGISTRY`, `request_from_operation` | Shipped, executed, exactly matches AGENT-02's contract; a fourth `operation` enum member is the additive extension point. |
| Rights authorization | A new rights-state enum, a boolean "has permission" flag, or a cached grant | `identity.rights_state`/`identity.rights_granted` (planned by 14A-03, already the single call path 14B-03 uses) | A second rights vocabulary is the exact failure mode 14B-03's own key_links section names as breaking non-negotiable 2. |
| Durable operation record-keeping | A new `agent_journal.jsonl` or in-memory job tracker | `journal.py`'s append-only `journal.jsonl` (planned by 14A-02), extended with one new `RECORD_TYPES` member | RELIABILITY-02 requires *the* durable local operation journal, singular; 14A-03 and 14B-04 already establish the additive-RECORD_TYPES pattern for exactly this kind of extension. |
| Treatment/coverage-state vocabularies | A new eleven-kind or five-state enum | `graph.TREATMENT_KINDS` and `graph.BINDING_STATES` (planned by 14B-02/14B-03) | These are TREAT-01's and TREAT-02's literal closed vocabularies, already locked in plan text with their exact member lists. |
| Package/course export loss reporting | A new export/restore mechanism for whatever 15A needs to hand a reviewer | `course_package.py`'s planned loss-report and manifest pattern (14B-05), if 15A ever needs to export a recommendation bundle | Not required for 15A's freeze gate itself, but if a future need arises, reuse the loss-category pattern rather than inventing a second one. |

**Key insight:** every problem this phase touches already has a designed
(if unexecuted) owner in 14A or 14B, or a shipped owner in Phase 8/11. The
actual net-new surface area of 15A is narrow: one new adapter operation, one
new narrow validation function that is explicitly not the tier gate, and one
new egress-recording extension to the journal. Everything else is composition.

## Common Pitfalls

### Pitfall 1: Conflating TREAT-02's coverage-state vocabulary with the shipped auditor's

**What goes wrong:** `auditor.coverage_report()` (Phase 11, shipped) already
returns a five-state coverage classification, but its states are `"covered"`,
`"gap"`, `"partial"`, `"conflicting"`, `"unknown"` `[VERIFIED:
auditor.py:439-484]` (quoted: `_row(key, "gap", ...)`, `_row(key, "partial",
...)`, `_row(key, "covered", ...)`), not TREAT-02's required `"covered"`,
`"thin"`, `"missing"`, `"conflicting"`, `"unknown"` `[VERIFIED:
REQUIREMENTS.md:508-509]`.
**Why it happens:** the two systems look alike (both are "citation-first
coverage classifiers over a bank/source pair") and a planner skimming the
codebase for "the coverage function" will find `auditor.coverage_report`
first, since it is the one that actually runs today.
**How to avoid:** TREAT-02's vocabulary lives in `graph.BINDING_STATES`
(planned by 14B-03), scoped to objective-to-source bindings inside a course
graph. `auditor.coverage_report` is scoped to syllabus-objective-to-bank-item
coverage (a different pairing, from Phase 11's older auditor domain) and
predates the TREAT-02 requirement. Do not rename one to match the other; keep
them as two distinct, correctly-scoped classifiers. If 15A's recommender
needs bank-level coverage as one input to a treatment decision, it may call
`auditor.coverage_report` as a signal, but the recommendation record's own
state field must be `graph.BINDING_STATES`, never `auditor.coverage_report`'s
states.
**Warning signs:** a `treatment_recommend` result or a `course.bind_source`
call anywhere in 15A's code carrying the string `"gap"` or `"partial"`.

### Pitfall 2: Trusting a rights snapshot at recommendation time

**What goes wrong:** a recommendation is drafted while a source's rights are
granted, sits in a review queue, and is accepted after the rights are revoked
(or were never actually granted, and the recommender read a stale cached
value).
**Why it happens:** the natural implementation shape for "draft, then later
accept" is to carry forward whatever the drafting step observed.
**How to avoid:** the rights check happens at `course.bind_treatment` time
(the actual write), reading the live registry via `identity.rights_state`,
exactly as 14B-03's Pitfall 5 discipline already establishes for ordinary
bindings. A recommendation record may *display* a rights state it observed at
draft time for the reviewer's context, but that display value must never gate
the write.
**Warning signs:** a recommendation's rights field is read anywhere other
than a UI display path; a bind call that skips `identity.rights_granted` when
a recommendation record already carries a `rights: "granted"` field.

### Pitfall 3: Building a second operation journal because "agent operations are different"

**What goes wrong:** RELIABILITY-02 asks for "a durable local operation
journal with intent, actor, scopes, inputs, expected fingerprints, phases,
checkpoints, proposals, validation, and undo" `[VERIFIED: REQUIREMENTS.md:
794-797]`, and a planner reading only that sentence in isolation may design a
new, richer journal shape from scratch because the field list looks bigger
than `journal.py`'s existing `ENTRY_KEYS`.
**Why it happens:** RELIABILITY-02's field list (intent, actor, phases,
checkpoints, proposals) does not exactly name-match `journal.py`'s planned
`ENTRY_KEYS` (`operation`, `state`, `object_id`, `revision`, ...), inviting
"this needs its own table."
**How to avoid:** RELIABILITY-02 is a requirement on *what the journal must
be able to express*, not a mandate for a second journal. `journal.py`'s
`RECORD_TYPES` is already an additive-growth vocabulary (14A-03 added
`reconcile`, 14B-04 added `migrate` this same way); 15A adds `agent_operation`
(or equivalent) as one more member, mapping RELIABILITY-02's field list onto
new optional keys on the existing entry shape (e.g. `intent`, `checkpoint`,
`egress`), following the exact precedent both prior additions already set.
**Warning signs:** a new file matching the pattern `*_journal.py` or
`*_log.jsonl` anywhere in the 15A plan's `files_modified` list.

### Pitfall 4: Letting "backend parity" become a second dispatcher

**What goes wrong:** AGENT-02's mock-hosted/mock-local fixture requirement
("run through a mock hosted backend and a mock local backend, asserting
identical artifacts and journals" `[VERIFIED: REQUIREMENTS.md:904-906]`) can
be misread as needing a purpose-built two-backend harness separate from the
shipped `model_backend.profiles` registry.
**Why it happens:** "mock" sounds like test-only infrastructure, inviting a
throwaway harness rather than a first-class settings registration.
**How to avoid:** register two ordinary profiles in `settings.model_backend.
profiles` (one `transport: "hosted_cli"` pointed at a fixture script, one
`transport: "openai_compatible"` pointed at a fixture HTTP server), exactly
as any other profile is registered, and drive both through the unmodified
`model_adapter.invoke()`. This is the same mechanism Phase 8's own tests
already use to prove transport parity, so 15A's fixture is additional
profiles and a scenario function, not new dispatch code.
**Warning signs:** a new module or function whose name contains `mock_hosted`
or `mock_local` that does not go through `model_adapter.invoke()`.

## Code Examples

### The additive operation-enum extension (schema change, not a code fork)

```json
// Source: schemas/model_adapter.schema.json:26-29, quoted verbatim, showing
// the exact enum this phase must extend additively (add "treatment_recommend"
// as a fourth member; do not replace or restructure the existing three).
"operation": {
  "type": "string",
  "enum": ["hint", "rubric_review", "author"],
  "description": "The bounded operation: hint generation, rubric point review, or bounded item authoring ..."
}
```

### The bounded request builder (existing, reused as-is)

```python
# Source: model_adapter.py:73-85, quoted verbatim -- the exact function 15A's
# treatment_recommend request must be built through, unmodified except for
# whatever new _PAYLOAD_KEYS entry a recommendation payload needs (e.g.
# "course_context", "objective_id") added to the existing bounded tuple.
def request_from_operation(operation, interaction_id, profile, **payload):
    """Build a bounded adapter request: exactly the fixed envelope fields and
    the fixed payload keys, nothing else. A payload key that was not passed
    is left absent; invoke's runtime check requires payload.rubric_points for
    operation rubric_review (adapter.request_invalid)."""
    return {
        "schema_version": 1,
        "operation": operation,
        "interaction_id": interaction_id,
        "profile": profile,
        "version": "1",
        "payload": {k: payload[k] for k in _PAYLOAD_KEYS if k in payload},
    }
```

### The rights-gate call shape 15A's write path must reuse

```text
# Source: 14B-03-PLAN.md:174-199, quoted (abridged) -- the exact assertions
# course.bind_source/course.bind_treatment already prove, which any 15A
# write path built on top of them inherits for free, and which a bypassing
# write path would have to reprove from scratch (a strong signal it should
# not bypass):
- Against a source whose seven rights are all `unknown`: `course.bind_source(...)`
  raises `CourseError` with code `course.rights_not_granted`. The message
  contains the source object id, the string `read`, and the string `unknown`.
- The refusal names the fix: the message contains the substring
  `next safe action: record`.
- After the refusal, the sidecar bytes on disk are unchanged and
  `len(journal.entries(root))` is unchanged. A refused binding writes nothing.
- `course.bind_treatment(..., treatment_kind="direct-reading", ...)` against a
  source whose `read` right is unknown refuses. Direct reading is a complete
  treatment result, not a free pass.
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| Superseded `DIRECTOR-01`/`DIRECTOR-02`/`DIRECTOR-04` requirement family (course-director-as-one-blob) | Split into `AGENT-01`, `AGENT-02`, `AGENT-03` (the last owned by 15B) plus `TREAT-01`/`TREAT-02` | 2026-08-13 family expansion, `[VERIFIED: REQUIREMENTS.md:290-293]` | The old "AI course director" family conflated the operation protocol, backend parity, treatment choice, and evidence-based proposals into one story; 15A owns exactly the first four of those (the protocol and treatment/coverage halves), and 15B owns the evidence-proposal half. A plan that tries to build evidence-based remediation proposals inside 15A is out of scope; that is `AGENT-03`, owned by 15B. |
| Four broad Phases 14-17 | Nine subphases 14A-17B | 2026-08-13, `[VERIFIED: ROADMAP.md:128-135]` | 15A is scoped narrower than the old "Phase 15: AI Course Director & Quality Pipeline" description in `SOURCE-TO-COURSE.md`; blueprint fidelity, course audit, and accepted-revision work moved to 15B. |

**Deprecated/outdated:** the `SOURCE-TO-COURSE.md` "Phase 15" narrative
description (still present in that file as historical rationale, explicitly
marked superseded) describes a broader scope than the current 15A ROADMAP
entry; the ROADMAP entry and REQUIREMENTS.md's TREAT-01/TREAT-02/RIGHTS-02/
RELIABILITY-02/AGENT-01/AGENT-02 rows are authoritative for what 15A actually
owns.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | A `treatment_recommend` adapter operation is the right wire shape (versus a wholly separate agent-operation protocol outside `model_adapter.py`). | Summary, Standard Stack "New in this phase" | If wrong, 15A either duplicates `TRANSPORT_REGISTRY`/profile-resolution machinery (violating AGENT-02's "same operations and schemas" intent) or forces an awkward reuse. This is exactly the kind of one-way format decision `PLANNING-DIRECTIVES.md` section 2 rule 1 says should stop a planning session; the 15A plan should carry this as an explicit `checkpoint:decision` with this research's recommendation as the stated default, not silently adopt it. |
| A2 | Egress recording belongs on the existing journal entry (new optional keys) rather than a sibling `egress_log.jsonl`. | Alternatives Considered | If wrong, RIGHTS-02's audit trail is split across two files with no single source of truth for "what happened in this operation", weakening exactly the auditability RELIABILITY-02 asks for. Flagged as a `checkpoint:decision` candidate in the Alternatives Considered table. |
| A3 | The recommender module should be a new root-level peer module (proposed name `director.py`) rather than added to `course.py` directly. | Recommended Project Structure | Low risk either way; `course.py`'s own key_links already forbid it from importing `evidence`, and a recommender that needs to call `model_adapter.invoke()` (which itself imports `surfaces.settings`) sits more naturally as a peer that calls into `course.py`, not inside it. The exact module name and boundary is a planner decision, not something this research should lock. |
| A4 | The fourth synthetic domain for the four-subject review (the standardized-exam blueprint) extends `fixtures/corpus_14b.py`'s planned `build_three_domains`/`build_all` rather than a new fixture module. | Standard Stack "New in this phase", Validation Architecture | If wrong, the freeze-gate fixture duplicates corpus-generation machinery 14B already builds (symlink handling, denied-path pockets, rights defaults), which the "Don't Hand-Roll" discipline this research documents argues against. |

**If this table is empty:** N/A, four assumptions are recorded above; none of
them touches a currently-locked decision record, so none blocks planning, but
A1 and A2 should be surfaced to the user as checkpoints per
`PLANNING-DIRECTIVES.md` section 2 (format decisions other phases will build
against).

## Open Questions

1. **Does the reviewer accept a treatment recommendation through a CLI command,
   a daemon route, or only as a manual file-edit review (per `OPERATION-
   CONTRACT.md`'s "Pending surfaces" list, which names "a general
   expected-fingerprint compare-and-swap write surface outside the `audit
   author` loop" as pending)?**
   - What we know: `OPERATION-CONTRACT.md` explicitly lists course-manifest
     commands, discovery/binding commands, and rights-grant commands as
     pending, not shipped `[VERIFIED: .claude/skills/OPERATION-CONTRACT.md:
     108-116]`.
   - What's unclear: whether 15A is expected to ship the first such CLI
     command/daemon route, or whether the four-subject recommendation review
     can pass purely through direct Python calls into `course.py`/`journal.py`
     (an internal API test) without a user-facing surface.
   - Recommendation: default to the internal-API shape for 15A's freeze gate
     (matching how 14A-04's and 14B-06's tracers exercise their modules
     directly, never through a CLI), and treat any CLI/daemon surface for
     accepting a recommendation as explicitly out of scope for 15A, deferred
     to whichever subphase first ships a learner- or builder-facing course UI
     (16B).

2. **What does "autonomy levels bound what an agent may do without review"
   concretely check at write time?**
   - What we know: `OPERATION-CONTRACT.md` step 11 names three levels
     (recommend-only, draft-and-review, approved bounded writes) in prose.
   - What's unclear: whether the level is a per-operation field the agent
     itself declares (self-reported) or a per-course/per-treatment-kind
     policy the course record enforces independent of what the agent claims.
   - Recommendation: enforce it as a course/policy-side check (never
     self-reported by the agent), consistent with AGENT-02's explicit ban on
     an agent that can "self-expand scope" `[VERIFIED: REQUIREMENTS.md:
     899-900]`. The exact storage location (a new course-record field vs. a
     settings-level policy) is a planner decision.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.11+ | Everything in this phase | Present (existing project runtime) | 3.11+ | N/A |
| A hosted CLI backend (Claude Code / Codex) | The real `hosted_cli` transport profile | Not required for the freeze gate, which uses mock profiles | N/A | Freeze gate uses `mock-hosted`/`mock-local` fixture profiles per AGENT-02's own fixture requirement; a real backend is not needed to plan or verify this phase. |
| An OpenAI-compatible local server | The real `openai_compatible` transport profile | Not required for the freeze gate | N/A | Same as above. |

No missing dependency blocks this phase; the freeze gate is explicitly
designed (by REQUIREMENTS.md's own AGENT-02 Fixture sentence) to run through
mock backends, and "Degraded: backend loss falls back to another registered
backend or manual continuation" `[VERIFIED: REQUIREMENTS.md:902]` is itself
one of the behaviors the fixture must prove.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Direct-execution Python scripts (`tests/*.py`), no pytest/unittest framework dependency, per the project's shipped convention `[VERIFIED: .claude/CLAUDE.md "Test runner" section]` |
| Config file | None; every test file defines its own local `fail(msg)` helper (project convention, confirmed by every `tests/*_roundtrip.py` and `tests/*_tracer.py` file read this session) |
| Quick run command | `python tests/<new_test_file>.py` for whichever single new test the plan adds per task |
| Full suite command | `for t in tests/*.py; do python "$t" || exit 1; done` (the exact command `14A-04-PLAN.md`'s precondition already uses, `[VERIFIED: 14A-04-PLAN.md:120]`) |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|---------------------|-------------|
| TREAT-01 | Recommender proposes only closed `TREATMENT_KINDS` members; direct-reading binds as a complete result; an untreated objective stays untreated, never silently generated | Unit + tracer scenario | `python tests/four_subject_review.py` (new) | Wave 0 gap |
| TREAT-02 | Coverage classification uses only `graph.BINDING_STATES`; a heading-similarity decoy never reads as `covered` | Unit + tracer scenario | `python tests/four_subject_review.py` (new) | Wave 0 gap |
| RIGHTS-02 | Egress log lists exactly the approved synthetic source spans; unreachable backend leaves core work local/model-free | Tracer scenario | `python tests/four_subject_review.py` (new) | Wave 0 gap |
| RELIABILITY-02 | A journaled synthetic agent operation interrupted at each checkpoint phase resumes/reverses from the journal alone | Fault-injection tracer scenario, following `tests/journal_roundtrip.py`'s and `tests/file_fault_tracer.py`'s kill/interrupt harness pattern | `python tests/four_subject_review.py` (new); may also add assertions to a extended `tests/journal_roundtrip.py` if the `agent_operation` record type lands in a 14A-adjacent plan instead | Wave 0 gap |
| AGENT-01 | Replay a recorded operation step by step from the journal against the thirteen-step protocol checklist in `OPERATION-CONTRACT.md` | Tracer scenario (a new `scenario_protocol_checklist()` function) | `python tests/four_subject_review.py` (new) | Wave 0 gap |
| AGENT-02 | Identical artifacts/journals through a mock-hosted and a mock-local profile; fallback/manual continuation on backend loss | Tracer scenario, reusing `model_adapter.py`'s existing transport-parity test pattern from Phase 8 | `python tests/four_subject_review.py` (new) | Wave 0 gap |

### Sampling Rate

- **Per task commit:** the single new/extended test file for that task's
  scope (following every prior 14A/14B plan's per-task `<verify>` convention).
- **Per wave merge:** `for t in tests/*.py; do python "$t" || exit 1; done`,
  the exact command 14A-04's precondition already establishes as this
  project's full-suite check.
- **Phase gate:** the four-subject recommendation review tracer green, plus
  the shipped-suite check inherited from the 14A-04/14B-06 tracer pattern
  (confirms 15A introduced no regression in `model.py`/`runtime.py`/
  `evidence.py` byte-compatibility).

### Wave 0 Gaps

- [ ] `tests/four_subject_review.py` -- the freeze-gate tracer; covers all six
  requirement rows above in one run, following `tests/three_domain_tracer.py`'s
  structure (`fail(msg)`, named `scenario_*()` functions, `main()`, a final
  `"TRACER: N passed, M skipped, 0 failed"` line).
- [ ] A fourth synthetic domain (standardized-exam blueprint) added to
  `fixtures/corpus_14b.py` (or a 15A-owned extension of it) for the fixture's
  input corpus.
- [ ] If the `agent_operation` journal record type is not added by a 14A- or
  14B-scoped plan before 15A executes, `tests/journal_roundtrip.py` needs a
  corresponding `check_agent_operation_record()` addition; the 15A plan should
  state explicitly which phase owns this addition.

*(No pre-existing test infrastructure covers this phase's requirements; all
listed gaps are new.)*

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-------------------|
| V2 Authentication | No | Single-learner local product; no accounts, no auth surface (`.claude/CLAUDE.md` Users constraint, unchanged by this phase). |
| V3 Session Management | No | No new session concept; the existing `runtime.py` session model is untouched by 15A. |
| V4 Access Control | Yes | `identity.rights_state`/`identity.rights_granted` (planned by 14A-03), re-checked live at every write, per Pattern 2 above. This is the phase's actual access-control surface: which operation may touch which source. |
| V5 Input Validation | Yes | `schema_validate.py`'s closed-keyword subset validator, already used by `model_adapter.py` and (planned) by `graph.py`/`course_package.py`; the new `treatment_recommend` result shape must validate against an additive schema extension the same way. |
| V6 Cryptography | No | No new secret material; `model_adapter.py`'s existing `secret_env` resolution (env-var only, never stored, never logged, `[VERIFIED: model_adapter.py:14-15]`) is reused unchanged. |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|------------------------|
| Rights escalation via a stale/cached snapshot (a recommendation accepted after its source's rights were revoked) | Elevation of Privilege | Live rights re-check at write time only, never a cached/snapshot value (Pattern 2, Pitfall 2 above); this is the exact discipline 14B-03's Pitfall 5 already documents and tests for ordinary bindings. |
| Excess egress (a hosted backend receiving more of a source than the approved span, or the egress log not matching what was actually sent) | Information Disclosure | The egress log/manifest records the exact spans sent, checked against the approved-source-span authority per operation (RIGHTS-02's own wording); the fixture's own acceptance bar is "the egress log lists exactly the approved synthetic source spans" `[VERIFIED: REQUIREMENTS.md:713-714]`. |
| A second, divergent rights or state vocabulary silently reintroducing a permissive default (e.g. a new module treating an absent rights record as granted instead of unknown) | Tampering / Elevation of Privilege | Single call path discipline: every rights decision in 15A's new code goes through `identity.rights_state`/`identity.rights_granted`, asserted structurally (a test that `director.py` contains no second literal comparison against a rights string), following the exact pattern 14B-03's own `must_haves` already assert for `course.py`. |
| Self-expanded agent scope (an agent operation that silently performs a write beyond its declared authority) | Elevation of Privilege | Autonomy level enforced course/policy-side, never self-reported by the agent (Open Question 2's recommendation); AGENT-02's own prohibition list names this explicitly. |
| Package/journal path traversal if 15A's egress record or recommendation payload ever references a filesystem path pulled from agent-supplied data | Tampering | Reuse `course_package.py`'s planned `safe_target`/containment-guard pattern (14B-05) if any path resolution is needed; do not resolve an agent-supplied relative path without containment, following the Zip Slip precedent already designed for package restore. |

## Sources

### Primary (HIGH confidence -- shipped, executed code and requirements read this session)

- `model_adapter.py` (full read of lines 1-100, structural grep of full file) - the shipped adapter boundary, `TRANSPORT_REGISTRY`, `request_from_operation`, `ADAPTER_CODES`.
- `tier_gate.py` (lines 1-60) - the shipped learner-facing no-leak gate and why it does not apply to 15A.
- `auditor.py` (lines 360-489) - the shipped, differently-scoped coverage-state vocabulary (Pitfall 1).
- `schemas/model_adapter.schema.json` and `schemas/settings.schema.json` (targeted greps with line numbers) - the closed `operation` enum and the `model_backend.profiles` registry shape.
- `.planning/REQUIREMENTS.md` (full TREAT/RIGHTS/RELIABILITY/AGENT family sections, and the traceability table) - the six owned requirements verbatim, with Fixture sentences.
- `.planning/ROADMAP.md` (Phase 14A, 14B, 15A entries; the nine-subphase table; governance clauses) - phase goals, dependencies, and freeze gates.
- `.planning/PLANNING-DIRECTIVES.md` (full read) - the autonomy rule, build-both rule, five non-negotiables, executor bar.
- `.planning/AGENT-WORKFLOW.md` (full read) - the cross-agent operating contract.
- `.claude/skills/OPERATION-CONTRACT.md` (full read) - the thirteen-step operation protocol and the shipped-versus-pending surface table.
- `.planning/DECISIONS-PRE-14A-2026-08-14.md` (full read) - D-14A-1/2/3.
- `.planning/phases/14A-identity-lifecycle-operation/14A-BRIEF.md`, `14A-01-PLAN.md`, `14A-02-PLAN.md`, `14A-03-PLAN.md`, `14A-04-PLAN.md` (objective, decisions-locked table, and full "Artifacts this phase produces" sections read for each) - planned identity/journal/operation-vocabulary API surface.
- `.planning/phases/14B-graph-course-package-prototype/14B-01-PLAN.md` through `14B-06-PLAN.md` (objective, decisions-locked table, and full "Artifacts this phase produces" sections read for each) - planned graph/course/package API surface, treatment and binding vocabularies, rights-at-bind-time gate.
- `.planning/research/phase-16/14-synthesis.md` sections 2, 3 (partially), 10, 11, 12, 15, 16, 17 - product model, operation protocol, cross-cutting rules, subphase table, exit gates.
- `.planning/PLAN-TEMPLATE.md` (full read) - the executor-bar structure every 15A plan must satisfy.
- `.planning/STATE.md` (lines 1-470) - project history and decision log context.

### Secondary (MEDIUM confidence)

- `.planning/SOURCE-TO-COURSE.md` (full read) - the superseded-but-traceable Phase 15 narrative description, used only to confirm current ROADMAP/REQUIREMENTS supersede it.
- `.planning/READINESS-AUDIT-14A.md` (targeted grep for A9/A10) - confirms the walking-skeleton and external-user gates that also bound 15A's freeze.

### Tertiary (LOW confidence)

- None used; no web search was performed, as this phase's research scope is entirely in-repo architecture composition with no new external library or API to verify against an authoritative external source.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH for shipped modules (`model_adapter.py`, `tier_gate.py`, `auditor.py`, `settings.schema.json`), MEDIUM for planned-but-unexecuted modules (`identity.py`, `journal.py`, `graph.py`, `course.py`) because their real implementation may deviate from plan text during 14A/14B execution.
- Architecture: MEDIUM - the composition pattern (reuse the one journal, the one rights vocabulary, the one adapter boundary) is well-grounded in explicit, cited precedent, but the two genuinely new design decisions (A1: adapter-operation vs. separate path; A2: journal-field egress vs. sibling log) are recommendations, not locked facts, and are flagged as checkpoint candidates.
- Pitfalls: HIGH - Pitfall 1 (coverage-vocabulary collision) is directly verified against two pieces of executed/planned code with exact quoted state names; Pitfalls 2-4 are directly grounded in explicit "key_links"/"Pitfall" sections the 14A/14B plans themselves already name.

**Research date:** 2026-08-14
**Valid until:** Re-check immediately if `14A-FREEZE.md` or `14B-FREEZE.md` appears in the repository before 15A is planned/executed (their real, frozen constants supersede the plan-text citations in this document per the Critical Caveat above). Otherwise, valid for approximately 14 days (fast-moving: this phase sits directly downstream of two unexecuted phases whose real implementation may shift plan-text details).
