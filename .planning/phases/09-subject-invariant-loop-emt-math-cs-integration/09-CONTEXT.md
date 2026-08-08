# Phase 9: Subject-Invariant Loop — EMT, Math, CS Integration - Context

**Gathered:** 2026-08-08
**Status:** Ready for planning

<domain>
## Phase Boundary

This integration phase proves that the already-built lesson, feedback, scoring, and code-execution pieces form one configurable teaching loop across EMT, Math, and CS. It adds offline math rendering, runnable code blocks in lessons, EMT prose/table fidelity, and a subject-profile contract. It does not create three separate applications or introduce subject-specific scoring forks.

</domain>

<decisions>
## Implementation Decisions

### One loop, configurable variation
- **D-01:** A versioned subject profile defines exactly the intended variation: lesson media/rendering capabilities, allowed item types, and verifier. The session loop, cursor policy, evidence, selector, and surfaces remain shared.
- **D-02:** Profiles are data selected by subject id, not Python subclasses or conditionals spread through surfaces. EMT, Math, and CS ship as three entries; adding a fourth subject is a settings/config entry plus referenced assets, not a code fork.
- **D-03:** Unknown subjects use a conservative default profile (plain markdown, existing item types, runtime scorer) and report unsupported requested capabilities explicitly.
- **D-04:** The subject id comes from namespaced objectives/bank metadata and is recorded on the session. Ambiguous mixed-subject banks require an explicit profile rather than guessing. — **Reversibility:** costly — profile selection becomes part of reproducible sessions and evidence interpretation.

### Lesson media contract
- **D-05:** Phase 3's preserved fenced-code info strings are the extension seam. Rendering produces semantic placeholders/attributes; capability adapters enhance them. The lesson parser is not forked per subject.
- **D-06:** Unsupported media renders the escaped source and an honest unavailable notice. Content never disappears and the lesson remains readable offline.

### Math
- **D-07:** Vendored KaTeX assets are bundled and served locally with no CDN/network fallback. Both inline and display math are supported through an explicit lesson syntax selected during research; raw source remains available when rendering fails.
- **D-08:** Math rendering is presentation only. Correctness still goes through existing item verifiers/runtime scoring; browser math code never scores an answer.

### Computer science
- **D-09:** Runnable lesson code calls the same bounded runner and refusal policy created for Phase 5 `check` items. No second executor, timeout, or process-tree policy is allowed.
- **D-10:** A fenced block is runnable only when its language is enabled in the subject profile and runner settings. Output, timeout, and refusal states render beside the block through the daemon; static/offline-without-daemon output remains readable but not falsely runnable.
- **D-11:** Editing/running a lesson example is ephemeral learning activity unless explicitly submitted as a `check` response; merely pressing Run does not create correctness evidence.

### EMT
- **D-12:** EMT uses the shared small markdown renderer with prose, headings, lists, and tables preserving source order and structure. No EMT-only renderer or hard-coded medical vocabulary is introduced.
- **D-13:** Tables remain accessible on narrow screens through semantic HTML and a scroll/wrap strategy chosen by UI planning; information is not flattened into screenshots.

### Integration proof
- **D-14:** One synthetic fixture per subject exercises the same lesson→item→wrong answer→hint→retry→evidence flow, varying only its profile-controlled medium/item/verifier.
- **D-15:** A fourth synthetic profile is created in tests without changing application code. This is the acceptance proof for LOOP-05, not a documentation claim.

### Codex's Discretion
Exact profile keys, math delimiters, and responsive table presentation remain for research/UI planning. The shared-loop and no-second-runner/scorer/parser invariants are locked.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

- `.planning/ROADMAP.md` § "Phase 9: Subject-Invariant Loop — EMT, Math, CS Integration" — five integration criteria.
- `.planning/REQUIREMENTS.md` LOOP-01 through LOOP-05 — binding subject-loop requirements.
- `.planning/PROJECT.md` — Execute Program, Runestone, and PrairieLearn references; stdlib-only rule and vendored-KaTeX exception.
- `.planning/phases/03-lesson-format-in-app-reader/03-CONTEXT.md` — lesson grammar, renderer scope, and fenced-code seam.
- `.planning/phases/05-check-item-type-code-editor/05-CONTEXT.md` — bounded runner and honest non-sandbox contract.
- `.planning/phases/06-hint-ladder-cursor-hold-feedback-modes/06-CONTEXT.md` — shared teaching-loop transitions.
- `model.py`, `runtime.py`, and `evidence.py` — parser/scorer/evidence invariants.
- `surfaces/lesson.py` (when Phase 3 executes), `runner.py` (when Phase 5 executes), and `surfaces/daemon.py` — intended integration seams.
- `build.py` and `resources.py` — explicit bundled-asset allowlists KaTeX must join.
- `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/STACK.md`, and `.planning/codebase/STRUCTURE.md` — shared layers and bundled-file constraints.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Namespaced objective `subject` extraction already exists in evidence.
- Phase 3 preserves fenced-code language metadata.
- Phase 5 owns the one runner; Phase 2 daemon owns browser execution routes.
- Packaging has explicit resource allowlists for vendored assets.

### Established Patterns
- One parser, scorer, daemon, evidence store, and now teaching loop.
- Static views omit capabilities they cannot honestly provide.
- Synthetic fixtures keep real course banks out of the repository.

### Integration Points
- Subject-profile schema and loader.
- Lesson renderer capability hooks for math/code.
- Bundled KaTeX resources and CSP/local asset serving.
- Daemon run endpoint reusing the Phase 5 runner.
- Cross-subject integration roundtrip with a fourth-profile no-code-change proof.

</code_context>

<specifics>
## Specific Ideas

Use Execute Program's single-loop discipline, Runestone's code-in-prose affordance, and EMT's source-structured prose/tables as inspiration without copying their product layers. UI presentation should receive a dedicated design contract before implementation.

</specifics>

<deferred>
## Deferred Ideas

- Objective scheduling and cross-subject daily pacing — Phase 10.
- Subject-specific content authoring — private-bank work, not repository implementation.
- Additional language runners — profile extension when a real course needs one.

</deferred>

---

*Phase: 9-subject-invariant-loop-emt-math-cs-integration*
*Context gathered: 2026-08-08*
