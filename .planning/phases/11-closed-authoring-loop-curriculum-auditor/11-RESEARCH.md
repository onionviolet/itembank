# Phase 11: Closed Authoring Loop & Curriculum Auditor - Research

**Researched:** 2026-08-08  
**Domain:** Contract-governed machine authoring, curriculum coverage audit, and reversible local-bank writes  
**Confidence:** HIGH for repository seams and locked scope; MEDIUM for the proposed detector thresholds.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

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

### the agent's Discretion

Exact similarity algorithms, thresholds, source-adapter scope, and report UI require dedicated research and stronger planning. Compatible algorithms may be implemented together when their findings remain explainable and user-selectable. The citation, validation, autonomy, and undo invariants are locked.

### Deferred Ideas (OUT OF SCOPE)

- Guaranteed PDF/DOCX ingestion if stable locator-preserving extraction cannot be achieved under current dependencies.
- Unbounded autonomous curriculum invention — out of scope.
- Hosted storage or shared gradebook — out of scope.
</user_constraints>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| AUTH-01 | One command performs the spec → draft → lint → retry/write cycle. | One orchestrator over the existing public `SPEC`, `lint`, and a transactional writer. |
| AUTH-02 | The model cannot author outside the request. | Validate exact count, allowed item types/objectives, and supplied citations before lint. |
| AUTH-03 | A repository-blind model can use the contract. | Give only public spec/schema plus a serialised request and structured findings. |
| AUDIT-01 | Ingest and extract detailed objectives. | Versioned Markdown/text adapter with stable line and heading locators. |
| AUDIT-02 | Map objectives to coverage and gaps. | Citation-first objective-to-item coverage engine. |
| AUDIT-03 | Covered claims are cited; unciteable claims are unknown. | Require both source-span and bank-item citation sets. |
| AUDIT-04 | Point at materials and absorb them only once obtained. | Report candidate materials separately; issue a new explicit authoring request to write. |
| AUDIT-05 | Support the configured autonomy range. | One pipeline with permission checks at the final write stage. |
| AUDIT-06 | Generated items pass lint. | Treat `lint` errors and chosen blocking warnings as retry findings before quality gate. |
| AUDIT-07 | Catch non-format machine-authoring failures. | Separate deterministic quality-gate profile and versioned findings. |
| AUDIT-08 | Show and undo every write. | Per-item Git commit if tracked, otherwise pre-replacement shadow snapshot and manifest. |
| AUDIT-09 | Show highest-autonomy volume. | Return proposed, accepted, rejected, retried, and written counts in the run report. |

## Summary

Use a pure audit/authoring domain layer, a thin CLI surface, and one writer selected at runtime from the target bank's Git status. The existing tool already publishes an AI-facing text contract via `spec`, emits structured lint objects via `lint --json`, keeps parsing in `model.py`, and confines the present bank mutation to `id-assign`; Phase 11 should compose those seams rather than teach a model private repository details. [VERIFIED: model.py:1-5; surfaces/cli.py:24-47; surfaces/cli.py:249-255]

Treat Markdown and UTF-8 text as the only registered adapters in this phase. A normalized document must retain raw fingerprint, heading/line locator, verbatim span, and objective candidate; a coverage record is `covered` only when it names both a source span and stable bank IDs. This meets the locked no-guessing contract while leaving PDF/DOCX as unregistered future adapters, not silently lossy inputs. [VERIFIED: .planning/phases/11-closed-authoring-loop-curriculum-auditor/11-CONTEXT.md]

**Primary recommendation:** Build one contract-first pipeline whose final operation is a preflighted per-item writer; default the existing highest setting, `audit_draft_lint_fix_commit`, to explicit opt-in and retain every rejected draft/report. [VERIFIED: schemas/settings.schema.json:64-69]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Source normalization and objective extraction | API / Backend | Database / Storage | It must read files safely and produce reproducible derived records, never depend on browser state. [ASSUMED] |
| Coverage calculation and citations | API / Backend | Database / Storage | The rules must be deterministic and serve identical CLI/UI reports. [ASSUMED] |
| Model authoring retry loop | API / Backend | — | It owns contract construction, response validation, retries, and gates. [ASSUMED] |
| Diff/approval/autonomy display | Browser / Client | API / Backend | The client displays a server/CLI-produced proposal; it never approves a bypassed gate. [ASSUMED] |
| Transactional mutation and undo | API / Backend | Database / Storage | Filesystem and Git/shadow manifests require crash-safe, auditable local writes. [ASSUMED] |

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python standard library | Python 3.13.5 available | Parsing, JSON, hashing, diffs, subprocess Git, and atomic replacement. | The project explicitly has no dependencies or install step. [VERIFIED: itembank.py:39-40; environment probe 2026-08-08] |
| Existing `model.py` | repository source | Public author contract, parsing, lint, IDs, content fingerprints. | It deliberately knows no surface/session layer. [VERIFIED: model.py:1-5; model.py:142-177; model.py:403-559] |
| Existing `schema_validate.py` | repository source | Validate newly published JSON payload schemas. | Settings already use this single validator rather than a duplicate validator. [VERIFIED: surfaces/settings.py:94-125] |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|
| `hashlib` / `difflib` | stdlib | SHA-256 source/snapshot fingerprints and explainable lexical comparisons. | Use for source fingerprints, optimistic undo protection, and near-duplicate candidate evidence. [ASSUMED] |
| `subprocess` invoking installed Git | Git 2.54.0.windows.1 available | Per-write commits and reversions for tracked banks. | Only after verifying that the exact bank path is in a worktree, tracked, and clean at that path. [ASSUMED] |

**Installation:** None. This phase must not add packages. [VERIFIED: itembank.py:39-40]

## Architecture Patterns

### System Architecture Diagram

```text
syllabus.md / syllabus.txt ──► source adapter ──► normalized document + fingerprint
                                                    │
bank.md ──► model.parse_bank ──► coverage engine ◄─┘
                                  │
                                  ├──► cited report: covered / partial / conflict / unknown
                                  └──► explicit authoring request (only after human supplies material)
                                                     │
public SPEC + schema + request ──► model adapter ─► draft
                                                     │
                  response scope check ─► lint ─► quality gate ─► reproducible diff
                                                     │                         │
                                          retry report / retained draft      autonomy decision
                                                                                │
                                                      ┌─────────────────────────┴────────────────────────┐
                                                      ▼                                                  ▼
                                            tracked + clean Git bank                         non-tracked bank
                                            commit bank + manifest                            shadow + manifest + replace
                                                      └─────────────────────► audit undo ◄─────────────────┘
```

### Recommended Project Structure

```text
auditor.py                  # source adapters, normalized documents, citations, coverage records
authoring.py                # bounded request, retry orchestration, quality gate, proposal assembly
surfaces/audit_cli.py       # CLI commands only; no parsing/business-rule duplicates
surfaces/cli.py             # parser/import/dispatch registration
surfaces/daemon.py          # later UI-approved route twin over the same authoring functions
schemas/                    # request, normalized document, report, quality finding, write-manifest contracts
tests/audit_roundtrip.py    # isolated end-to-end contract suite
fixtures/audit/             # entirely synthetic syllabus, banks, drafts, and fidelity fixtures
```

The module names and derived-artifact locations above are recommended file boundaries, not current repository paths. [ASSUMED]

### Pattern 1: Validate the whole candidate set before writing

**What:** Build the proposed post-write bank in memory, structurally number and assign IDs, then parse, lint, and quality-gate the complete candidate plus existing bank before any write. `assign_ids()` is already a pure transform and current ID assignment first scans every supplied bank for global collisions, so this preserves the existing all-or-nothing discipline. [VERIFIED: model.py:196-209; surfaces/evidence_cli.py:305-342]

**When to use:** Every generated request, including `draft_and_approve` previews. A clean prefix of a failed batch is never written. [VERIFIED: .planning/phases/11-closed-authoring-loop-curriculum-auditor/11-CONTEXT.md]

```python
# Proposed contract sketch; field names and version are [ASSUMED].
proposal = compose_existing_and_candidate(bank_text, draft_text)  # [ASSUMED]
proposal, id_changes = model.assign_ids(proposal, known_ids)     # [VERIFIED: model.py:196-209]
questions = model.parse_bank(proposal)                            # [VERIFIED: model.py:27-36]
errors, warnings = model.lint(questions)                          # [VERIFIED: model.py:403-559]
findings = quality_gate(questions, machine_authored=True)         # [ASSUMED]
if errors or blocks(warnings, findings):                           # [ASSUMED]
    retain_draft_and_report()                                     # [ASSUMED]
```

### Pattern 2: Citation-first coverage states

**What:** Every coverage row holds the exact normalized source span citation(s) and exact `item_id` citation(s). A row with either set absent is `unknown`; `partial` and `conflicting` preserve unresolved evidence instead of averaging it into `covered`. [VERIFIED: .planning/phases/11-closed-authoring-loop-curriculum-auditor/11-CONTEXT.md; model.py:55-56]

**When to use:** Audit reports, draft requests derived from a gap, and the write manifest for any resulting item. [ASSUMED]

### Pattern 3: Capability changes only at the final action

**What:** The pipeline always normalizes, validates scope, lints, runs the quality gate, records a diff, and writes an audit event. `report_only` stops after reporting, `draft_and_approve` awaits one explicit acceptance per reversible unit, and the schema's `audit_draft_lint_fix_commit` value alone may commit a clean unit automatically. The exact current enum is: `"enum": ["report_only", "draft_and_approve", "audit_draft_lint_fix_commit"]`. [VERIFIED: schemas/settings.schema.json:64-69]

**When to use:** All entry points; the daemon route must call the same domain function as the CLI. Current routes are a centrally declared table with CLI twins, so retain that convention when the UI contract permits Phase 11 endpoints. [VERIFIED: surfaces/daemon.py:48-99]

### Anti-Patterns to Avoid

- **Prompt-only scope enforcement:** reject response count/type/objective/citation mismatches in code before lint; a prompt is not authorization. [ASSUMED]
- **PDF/DOCX best-effort extraction:** do not register these adapters without stable-locator fidelity fixtures. [VERIFIED: .planning/phases/11-closed-authoring-loop-curriculum-auditor/11-CONTEXT.md]
- **Writing a clean prefix:** retain the complete failed batch and its structured reasons instead. [VERIFIED: .planning/phases/11-closed-authoring-loop-curriculum-auditor/11-CONTEXT.md]
- **A second hidden linter:** retain independent, named quality findings rather than folding detector scores into prose or mutating `lint` semantics. [VERIFIED: model.py:385-400; .planning/phases/11-closed-authoring-loop-curriculum-auditor/11-CONTEXT.md]
- **Assuming a bank is Git-safe from its directory name:** detect exact worktree and tracked-file status immediately before the write. [ASSUMED]

## Second Quality Gate: Recommended Deterministic Profile

Run this as a separate, versioned `quality_gate()` result after format lint. The existing linter already detects exact duplicate stems and warns on answer skew only after twelve MC items and a greater-than-40% top key share; preserve it unchanged and have the second gate independently report its machine-authoring decision. The existing values are: `"if total >= 12:"` and `"if n / total > 0.40:"`. [VERIFIED: model.py:542-559]

| Detector | Default blocking rule | Explainable evidence | Confidence |
|----------|-----------------------|----------------------|------------|
| Answer-position skew | Evaluate MC items in proposed full bank; when count ≥ 12, block if one keyed position exceeds 40%. | total, per-letter counts, max share, threshold. | MEDIUM — threshold preserves the live lint precedent. [VERIFIED: model.py:548-558] |
| Near-duplicate stems | After exact-lint duplicate check, block candidate against existing/proposed other items if normalized non-stopword token Jaccard similarity ≥ 0.85, with ≥ 6 tokens in each stem. | token sets, intersection, union, score, compared item IDs. | [ASSUMED] |
| Answer leak | Block when a correct option contributes a contiguous run of ≥ 3 normalized content tokens to the stem and no incorrect option has the same run. | matching run, correct option, competing-option comparison. | [ASSUMED] |
| Distractor-rationale completeness | For each non-correct MC option, block if its rationale is absent or lacks a “would be correct” condition. | option letter and missing/failed rationale predicate. | MEDIUM — current lint already exposes both missing rationale and missing “would be” conditions. [VERIFIED: model.py:475-485] |

Do not combine detector scores into one opaque score. Emit every applicable finding with detector version, severity, item reference, measured values, and a concise remediation message; profiles may later change severity but not erase evidence. [ASSUMED]

## Reversibility Decision

Choose backend per target file at write time:

1. **Git backend:** use only when the bank is inside a Git worktree, is tracked by that worktree, and has no staged or unstaged changes at that exact path. Write one additive item plus its write manifest, stage only those paths, and create one machine-authored commit containing request/source metadata. Undo invokes a documented `git revert` of that write commit. [ASSUMED]
2. **Shadow backend:** otherwise create a content-addressed before-image and write manifest durably, then replace the bank using the current tmp-then-`os.replace()` pattern. Undo verifies that the current content fingerprint equals the manifest's recorded after-image before atomically restoring the before-image; mismatch refuses rather than overwriting newer work. [ASSUMED]

This is necessary because repository policy keeps real banks out of this checkout: `guard` fails Markdown banks outside `fixtures/`, while the committed synthetic fixture is Git-tracked. The current guard explicitly says, “Banks belong in your private vault, never in this repo.” [VERIFIED: surfaces/cli.py:75-98; git ls-files probe 2026-08-08]

Use `itembank audit undo <write-id>` as the sole public operation and put the selected backend, paths, pre/post SHA-256, request fingerprint, source fingerprints, tool version, and Git commit (when applicable) in the write manifest. Do not use a user-visible one-way “restore anyway” bypass. [ASSUMED]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Format validation | A second parser or English-only repair prompt | Existing `SPEC`, `parse_bank`, `lint`, and lint JSON records | Those are already the public authoring contract. [VERIFIED: model.py:1-5; surfaces/cli.py:24-47] |
| IDs and content drift | New authoring-only IDs/hashes | Existing `assign_ids()` and `content_fingerprint()` | IDs are stable and the fingerprint deliberately tracks tested content. [VERIFIED: model.py:142-177; model.py:196-209] |
| JSON schema checks | A new ad hoc validator | `schema_validate.validate()` | Settings use this as the one validation seam. [VERIFIED: surfaces/settings.py:94-125] |
| Crash-safe replacement | Direct overwrite | tmp write plus `os.replace()` | Existing writers use this pattern to avoid partial replacements. [VERIFIED: runtime.py:178-185; surfaces/evidence_cli.py:338-342] |
| Coverage inference | Uncited model assertion | Exact source spans plus bank IDs | The locked contract makes uncited coverage unknown. [VERIFIED: .planning/phases/11-closed-authoring-loop-curriculum-auditor/11-CONTEXT.md] |

## Common Pitfalls

### Citation drift
**What goes wrong:** A report claims coverage after its source or bank changed.  
**Why it happens:** Objective labels alone do not prove which exact syllabus passage or bank revision was evaluated.  
**How to avoid:** Store source and bank SHA-256 fingerprints in each derived report/manifest; mark a report stale if either differs. [ASSUMED]  
**Warning signs:** A source path resolves but its fingerprint no longer matches the cited report. [ASSUMED]

### Lint-clean but pedagogically weak items
**What goes wrong:** Format lint passes a near duplicate, answer leak, or poor distractor rationale.  
**Why it happens:** Existing lint is deliberately a format contract and classifies several authoring-quality defects as warnings. [VERIFIED: model.py:403-559]  
**How to avoid:** Make the separate quality profile blocking for machine-authored writes, retaining its independent findings. [ASSUMED]  
**Warning signs:** A proposal has zero lint errors but non-empty quality findings. [ASSUMED]

### Partial batch mutation
**What goes wrong:** The author loop writes accepted early drafts when later drafts exhaust retries.  
**Why it happens:** Writing is interleaved with generation. [ASSUMED]  
**How to avoid:** Assemble and gate the entire request in memory; only split into per-item write units after the whole candidate is clean. [ASSUMED]  
**Warning signs:** A failed run has a write ID or changed bank fingerprint. [ASSUMED]

### Undo clobbers later edits
**What goes wrong:** A shadow restore replaces edits made after the machine write.  
**Why it happens:** Restore targets a pathname rather than the recorded after-image. [ASSUMED]  
**How to avoid:** Compare current fingerprint with manifest after-fingerprint; refuse on mismatch. [ASSUMED]  
**Warning signs:** Undo reports a fingerprint mismatch or Git revert conflict. [ASSUMED]

## Code Examples

### UTF-8 text/Markdown locator adapter

```python
# Proposed pseudocode; all new field names are [ASSUMED].
def normalize_text_source(path, source_id):
    raw = open(path, "rb").read()                         # [ASSUMED]
    text = raw.decode("utf-8")                             # [ASSUMED]
    return {
        "schema_version": 1,                               # [ASSUMED]
        "source_id": source_id,                            # [ASSUMED]
        "fingerprint": sha256(raw).hexdigest(),            # [ASSUMED]
        "spans": heading_and_line_spans(text),             # [ASSUMED]
    }
```

### Scope validator before retry

```python
# Proposed pseudocode; all predicates are [ASSUMED].
def scope_findings(request, parsed_draft):
    require(len(parsed_draft) == request["count"])          # [ASSUMED]
    require(all(q["type"] in request["item_types"]          # [ASSUMED]
                and q["objective"] in request["objectives"]
                for q in parsed_draft))
    require(request["source_citations"])                    # [ASSUMED]
```

## State of the Art

| Old Approach | Current Project Approach | Impact |
|--------------|--------------------------|--------|
| A prose prompt tells an author what a bank should look like. | `itembank spec` prints the contract and `lint --json` returns schema-versioned structured findings. [VERIFIED: itembank.py:4-14; surfaces/cli.py:24-47] | Phase 11 can pass failures mechanically, without a human translating them. |
| Direct writer changes a bank. | Existing `id-assign` reads all target banks, checks cross-bank IDs, then tmp-writes changed files. [VERIFIED: surfaces/evidence_cli.py:305-342] | Phase 11 should retain preflight-before-write and make its writer the sole mutation seam. |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The proposed module names, sidecar manifest design, and CLI command shape are the best local boundaries. | Architecture Patterns / Reversibility | Planner may need to align names with the Phase 8 adapter when it lands. |
| A2 | Jaccard ≥ 0.85 with a six-token floor is an appropriate default near-duplicate threshold. | Second Quality Gate | False positives/negatives may require profile tuning. |
| A3 | A three-token correct-option run absent from distractors is a useful answer-leak detector. | Second Quality Gate | It may flag legitimate technical phrasing. |
| A4 | Git eligibility should require target-path clean status and shadow undo should use optimistic fingerprint matching. | Reversibility | Git or shadow semantics may need a dedicated recovery procedure. |
| A5 | Phase 11 consumes the named Phase 8 dependency through `model_adapter.invoke(request, profile)` and an additive strict `author` operation without exposing repository files. | Architecture Patterns | Phase 8 has not executed yet, so its artifact/schema/test existence is a blocking execution precondition verified before the binding task. |

## Open Questions (RESOLVED)

1. **Phase 8 adapter API availability — RESOLVED**
   - Resolution: Phase 8 has research/context but no executed PLAN or live adapter artifact yet, so Phase 11 retains the roadmap's hard Phase 8 execution dependency. The binding target is Phase 8's published provider-neutral artifact and symbol, `model_adapter.py::invoke(request, profile)`, not a Phase 11 transport. Phase 11 additively registers the `author` operation in the same strict adapter schema, uses `surfaces.settings.load_settings(base)["model_backend"]` for the profile, and binds the callable in the actual CLI composition root, `surfaces/cli.py::main`. A configured fake hosted executable must complete the public author command without callable injection after Phase 8 executes; typed unavailable remains only a failure-path outcome. [VERIFIED: .planning/phases/08-model-adapter-interface-tier-gate-enforcement/08-RESEARCH.md:61-64,76,158-170; surfaces/cli.py:101-115,349-350; surfaces/settings.py:86-125]

2. **UI route contract — RESOLVED**
   - Resolution: Phase 11 creates no daemon or frontend route. The deterministic frontend gate was false, the UI-dependent surfaces remain blocked pending `.planning/UI-SPEC.md`, and the locked public surface for this phase is the CLI command family (`itembank audit source|material|author|undo`) over the reusable domain functions. A later UI-approved phase may add a route twin without changing the Phase 11 domain contract. [VERIFIED: .planning/ROADMAP.md:495-502; .planning/phases/11-closed-authoring-loop-curriculum-auditor/11-CONTEXT.md; surfaces/cli.py:101-115]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Python | All Phase 11 code/tests | ✓ | 3.13.5 | — |
| Git | Tracked-bank reversible writer | ✓ | 2.54.0.windows.1 | Shadow backend for a non-tracked target. [ASSUMED] |
| External model adapter | Authoring loop | Phase 8 contract planned; implementation is an execution precondition | `model_adapter.invoke(request, profile)` | Phase 11 binds this exact provider-neutral API in `surfaces/cli.py::main` and proves a configured fake hosted adapter; it does not add a separate transport. [VERIFIED: Phase 8 RESEARCH.md:61-64,76,158-170] |

**Missing dependencies with no fallback:** Phase 8 must execute and publish `model_adapter.py`, its strict schema, and passing adapter contract tests before Phase 11's public author-command integration task runs. This is an explicit cross-phase precondition, not a Phase 11 scope reduction. [VERIFIED: .planning/ROADMAP.md Phase 11 dependency]

**Missing dependencies with fallback:** A non-Git bank uses the shadow backend. [ASSUMED]

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Standalone standard-library roundtrip scripts with plain `fail()` assertions. [VERIFIED: .planning/codebase/TESTING.md] |
| Config file | none. [VERIFIED: .planning/codebase/TESTING.md] |
| Quick run command | `python tests/audit_roundtrip.py` [ASSUMED — Wave 0 file] |
| Full suite command | `Get-ChildItem tests/*_roundtrip.py \| ForEach-Object { python $_.FullName }` [ASSUMED] |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| AUTH-01 / AUTH-03 | Configured Phase 8 hosted-adapter fixture receives the public contract; malformed first draft gets structured findings and clean retry writes only after all gates, with no callable injection in the public command test. | integration | `python tests/audit_cli_roundtrip.py` | ❌ Wave 0 |
| AUTH-02 | Count/type/objective/citation mismatch is rejected and leaves bank unchanged. | unit + integration | `python tests/audit_roundtrip.py` | ❌ Wave 0 |
| AUDIT-01 / AUDIT-03 | Markdown/text locator fidelity and citation-required `unknown` state. | unit | `python tests/audit_roundtrip.py` | ❌ Wave 0 |
| AUDIT-02 / AUDIT-04 | Objective coverage/gap report; candidate material does not authorize a write. | integration | `python tests/audit_roundtrip.py` | ❌ Wave 0 |
| AUDIT-05 / AUDIT-09 | Three modes yield correct no-write/approval/auto-write behavior and volume totals. | integration | `python tests/audit_roundtrip.py` | ❌ Wave 0 |
| AUDIT-06 / AUDIT-07 | Lint and each four quality detectors block synthetic failing candidates. | unit + integration | `python tests/audit_roundtrip.py` | ❌ Wave 0 |
| AUDIT-08 | Git and shadow backends each show a diff, perform one write, and undo it; changed-after-write shadow undo refuses. | integration | `python tests/audit_roundtrip.py` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `python tests/audit_roundtrip.py` once the Wave 0 harness exists. [ASSUMED]
- **Per wave merge:** Run every existing `*_roundtrip.py` script plus the new audit suite. The project already uses executable scripts rather than a test framework. [VERIFIED: .planning/codebase/TESTING.md]
- **Phase gate:** Full suite green; manually inspect one rendered diff/approval flow after the Phase 11 UI contract is available. [ASSUMED]

### Wave 0 Gaps

- [ ] `tests/audit_roundtrip.py` — source normalization, coverage states, retry, quality, autonomy, Git/shadow undo. [ASSUMED]
- [ ] `fixtures/audit/` — synthetic Markdown/text source, malformed/clean drafts, and a Git-initialized temp bank fixture. [ASSUMED]
- [ ] New published schemas plus protocol assertions that every finding/report/manifest carries its schema version. Existing protocol tests already check code/schema alignment. [VERIFIED: tests/protocol_roundtrip.py:62-110; tests/protocol_roundtrip.py:164-220]

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | Local tool has no user-authentication flow in Phase 11. [ASSUMED] |
| V3 Session Management | no | No web session is needed for source/audit mutation authorization. [ASSUMED] |
| V4 Access Control | yes | Explicit autonomy setting plus per-item approval; never infer authority from model output. [VERIFIED: schemas/settings.schema.json:64-69; .planning/phases/11-closed-authoring-loop-curriculum-auditor/11-CONTEXT.md] |
| V5 Input Validation | yes | Validate paths, UTF-8 decoding, request schemas, model response scope, lint, and quality findings before write. [ASSUMED] |
| V6 Cryptography | yes | Use stdlib SHA-256 only for integrity/fingerprint comparisons; it is not an authorization mechanism. [VERIFIED: model.py:142-177] |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Prompt/model output attempts to expand scope | Elevation of privilege | Treat output as untrusted data; enforce request count, type, objective, and citations in code. [ASSUMED] |
| Path traversal / arbitrary overwrite | Tampering | Resolve sources and bank targets from explicit validated paths; UI routes must use allowlisted identifiers, mirroring existing daemon practice. [VERIFIED: surfaces/daemon.py:108-114; surfaces/daemon.py:763-769] |
| Stale or altered source cited as current | Tampering | Source/bank fingerprints in report and write manifest; stale result is not silently reused. [ASSUMED] |
| Undo overwrites later work | Tampering | Git revert conflict or shadow after-fingerprint check refuses unsafe undo. [ASSUMED] |

## Sources

### Primary (HIGH confidence)

- `model.py:1-5, 142-209, 385-559` — public format contract, fingerprints, IDs, lint behavior and current skew threshold.
- `surfaces/cli.py:24-47, 75-98, 249-255` and `surfaces/evidence_cli.py:305-342` — structured lint, guard, only current bank writer, and atomic update precedent.
- `schemas/settings.schema.json:64-102` and `surfaces/settings.py:86-142` — autonomy enum/model setting and schema-validated atomic settings writes.
- `.planning/phases/11-closed-authoring-loop-curriculum-auditor/11-CONTEXT.md` and `.planning/ROADMAP.md:477-493` — locked phase contract and acceptance criteria.
- `.planning/codebase/TESTING.md` and `tests/protocol_roundtrip.py:62-110` — test conventions and contract test pattern.

### Secondary (MEDIUM confidence)

- No external documentation was needed: the phase is standard-library/convention work constrained by the live repository and locked Phase 11 decisions.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — directly verified repository stdlib and public-contract seams.
- Architecture: HIGH for seams; MEDIUM for proposed new module boundaries.
- Pitfalls: HIGH for existing lint/write/guard hazards; MEDIUM for detector thresholds and undo protocol.

**Research date:** 2026-08-08  
**Valid until:** 2026-09-07 for codebase findings; reconfirm the Phase 8 adapter API immediately before implementation.
