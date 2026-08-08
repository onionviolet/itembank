# Phase 11: Closed Authoring Loop & Curriculum Auditor - Context

**Gathered:** 2026-08-08
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase closes two contract-governed loops: draft→lint→repair for requested item authoring, and source objective→cited coverage claim→gap→optional draft for curriculum auditing. It adds graduated autonomy, a second machine-authoring quality gate, and one-step reversible writes. It does not let the runtime invent unrequested curriculum, accept uncited coverage, or bypass human approval implicitly.

</domain>

<decisions>
## Implementation Decisions

### Source ingestion and citation contract
- **D-01:** Every source is normalized into a versioned document shape preserving source id, section/page locator where available, verbatim span boundaries, and extracted objective candidates. Coverage claims must cite both the exact source span and exact bank item ids.
- **D-02:** A claim without adequate citations is `unknown`, never `covered`. Partial and conflicting coverage are explicit states; confidence never upgrades an uncited claim.
- **D-03:** Markdown and UTF-8 text are the guaranteed first-class inputs under the stdlib constraint. The ingestion interface is adapter-based so PDF/DOCX support can coexist later. Research may include PDF/DOCX in this phase only if extraction preserves stable locators and passes fidelity fixtures; lossy silent extraction is forbidden.
- **D-04:** Original source files remain read-only. Normalized extraction and audit reports are derived artifacts with source fingerprints so stale reports are detectable.

### Closed authoring loop
- **D-05:** One orchestration command/route performs: obtain published spec/schema, request only the scoped item(s), validate response shape, lint, return machine-readable lint failures to the model, retry to a configured cap, run the second quality gate, show a diff, then act according to autonomy.
- **D-06:** The model receives the same public format contract an external author receives; repository source access is not required. Retry prompts contain structured failures, not hand-relayed prose.
- **D-07:** Generation is bounded by an explicit authoring request carrying objectives, count, item types, and source citations. Material outside that request is rejected rather than treated as initiative.
- **D-08:** Exhausting the retry cap produces a retained draft/report with reasons and no bank write. A partially clean batch does not silently write its prefix.

### Second quality gate
- **D-09:** The second gate is distinct from format lint and returns versioned machine-readable findings for answer-position skew, near-duplicate stems, answer-leaking stem/option overlap, distractor rationale completeness, and any research-supported high-value checks.
- **D-10:** Deterministic checks and explainable thresholds are preferred. Thresholds may be configurable within schema bounds, and multiple compatible detectors may run together; a composite result names every contributing finding.
- **D-11:** Machine-authored items must pass both lint and the second gate before approval/write. Human-authored items may run the same gate, but this phase does not retroactively block existing banks without an explicit audit.

### Graduated autonomy
- **D-12:** Three modes share one pipeline: `report_only` writes no bank changes; `draft_and_approve` presents each clean diff and waits for explicit acceptance; `full` writes independently only after all gates pass.
- **D-13:** `full` remains an explicit opt-in flagged as higher risk. It reports proposed volume before work and completed/rejected/retried volume afterward; caps apply per run and per objective.
- **D-14:** Autonomy changes permissions, not validation rigor. The same citations, lint, quality gate, diff, and audit events apply in every mode.

### Reversibility
- **D-15:** All bank mutations go through one transactional writer. If the bank is git-tracked, each accepted unit is its own machine-authored commit with source/request metadata. If not git-tracked, the writer creates a content-addressed shadow copy plus manifest before replacement. One `itembank audit undo <write-id>` command abstracts both mechanisms. — **Reversibility:** one-way as a public contract — once autonomous writes exist, changing identifiers/undo semantics requires migrating manifests and audit records; planning must checkpoint this choice.
- **D-16:** A batch never hides multiple item writes in one opaque action. The default reversible unit is one item/additive edit; unavoidable coordinated edits declare their set before writing and undo atomically.
- **D-17:** Every report and proposed diff is reproducible from request, source fingerprints, bank fingerprint, adapter profile, and tool version.

### Coverage-to-authoring flow
- **D-18:** The auditor first reports gaps and candidate supporting materials. Absorbing obtained material is a separate explicit authoring request that preserves citations; finding a gap does not itself authorize content generation.
- **D-19:** Phase 10 weak-objective signals may prioritize which already-defined objectives to audit, but never create syllabus objectives or substitute performance weakness for curriculum evidence.

### Codex's Discretion
Exact similarity algorithms, thresholds, source-adapter scope, and report UI require dedicated research and stronger planning. Compatible algorithms may be implemented together when their findings remain explainable and user-selectable. The citation, validation, autonomy, and undo invariants are locked.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

- `.planning/ROADMAP.md` § "Phase 11: Closed Authoring Loop & Curriculum Auditor" — five acceptance criteria and open mechanism decisions.
- `.planning/REQUIREMENTS.md` AUTH-01 through AUTH-03 and AUDIT-01 through AUDIT-09 — binding authoring/auditing contract.
- `.planning/PROJECT.md` — auditor autonomy range, reversible-write requirement, uncertainty posture, and machine-generation decision flagged for revisit.
- `.planning/phases/08-model-adapter-interface-tier-gate-enforcement/08-CONTEXT.md` — provider-neutral model adapter and interaction evidence.
- `.planning/phases/10-retention-pacing-trends/10-CONTEXT.md` — weak-objective signal and provenance rules.
- `.planning/phases/01-evidence-spine-protocol-foundation/01-CONTEXT.md` — stable item ids, fingerprints, append-only audit evidence, and transactional discipline.
- `model.py` — public `SPEC`, parser, content fingerprints, `lint`, and current distractor checks.
- `schemas/lint_error.schema.json` and item/settings schemas — machine-readable validation and existing `auditor_autonomy` setting.
- `surfaces/settings.py`, `surfaces/cli.py`, and `surfaces/daemon.py` — settings validation and CLI/route twin conventions.
- `guard` implementation and repository content safeguards — real-bank isolation that generated fixtures must respect.
- `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/CONCERNS.md`, `.planning/codebase/INTEGRATIONS.md`, and `.planning/codebase/TESTING.md` — write boundaries, risks, adapter seams, and test conventions.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `model.SPEC`, `lint()`, declared lint codes, stable `[ID:]`, and content fingerprints provide the first gate and identity basis.
- Phase 8's adapter supplies model calls without coupling the auditor to a provider.
- Settings already reserve `auditor_autonomy`.
- Git and atomic-replace patterns exist in updater/session work; guard prevents real banks entering this repository.

### Established Patterns
- Contracts are public and machine-readable; agents consume errors without a human relay.
- Writes validate fully before any prefix is committed.
- Unknown is preserved rather than guessed; audit facts are append-only and derived views are reproducible.

### Integration Points
- Source-normalization/adapters and citation schema.
- Auditor/authoring orchestrator shared by CLI and daemon route.
- Second-quality-gate module and finding schema.
- Transactional writer plus git/shadow-copy undo backend.
- Audit report/diff UI requiring a dedicated UI design contract.
- Synthetic syllabus/bank fixtures covering citations, uncertainty, retries, full-autonomy volume, and both undo backends.

</code_context>

<specifics>
## Specific Ideas

Where quality detectors conflict, preserve their individual findings and let a profile choose enforcement rather than averaging them into an opaque score. The strongest planning model should research established curriculum-mapping citation practices and near-duplicate/distractor heuristics before choosing defaults.

</specifics>

<deferred>
## Deferred Ideas

- Guaranteed PDF/DOCX ingestion if stable locator-preserving extraction cannot be achieved under current dependencies.
- Unbounded autonomous curriculum invention — out of scope.
- Hosted storage or shared gradebook — out of scope.

</deferred>

---

*Phase: 11-closed-authoring-loop-curriculum-auditor*
*Context gathered: 2026-08-08*
