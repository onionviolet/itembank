---
phase: 14B
slug: graph-course-package-prototype
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-14
---

# Phase 14B Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded from `14B-RESEARCH.md` section "Validation Architecture". The planner
> fills the Per-Task Verification Map once plan and task IDs exist.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | None. Direct-execution Python scripts, this project's established convention (not pytest, not unittest) |
| **Config file** | none. See the `tests/*_roundtrip.py` convention |
| **Quick run command** | `python tests/graph_roundtrip.py` (or the specific new test file a task targets) |
| **Full suite command** | `for t in tests/*.py; do python "$t" || exit 1; done` |
| **Estimated runtime** | Unknown for the new 14B files. Do not record a figure until one has been measured on this machine. |

---

## Sampling Rate

- **After every task commit:** the quick run command for that task's specific new or changed test file.
- **After every plan wave:** the 14B subset `for t in tests/graph_roundtrip.py tests/course_package_roundtrip.py; do python "$t" || exit 1; done`, plus the shipped-anchor spot check `python tests/scoring_roundtrip.py && python tests/evidence_roundtrip.py` (the anchor-check discipline 14A-01 Task 3 established).
- **Before `/gsd-verify-work`:** full suite green, `python tests/three_domain_tracer.py` green, and `python itembank.py guard .` reporting `0 offending files`.
- **Freeze gate:** no 14B freeze record is written on a red tracer (mirrors 14A-04 Task 4).
- **Max feedback latency:** to be measured, not asserted.

---

## Per-Task Verification Map

Populated by the planner at plan time (2026-08-14). Plan 14B-06 Task 2 updates
the Status column and replaces the Estimated runtime placeholder above with a
measured figure.

| Plan | Task | Req ID | Behavior | Test Type | Automated Command | Assertion function | Status |
|------|------|--------|----------|-----------|-------------------|--------------------|--------|
| 14B-01 | 1 | (precondition) | Phase 14A landed and its frozen surface matches what 14B was planned against; halt by name on divergence | precondition | `python -c "import identity, journal, discovery; assert len(identity.REVISION_KEYS)==11 and len(journal.OPERATION_TYPES)==6 and len(journal.ENTRY_KEYS)==22; print('14A surface matches')"` | n/a | ⬜ pending |
| 14B-01 | 2 | (decision) | Sidecar path and the Phase 13.9 supersession recorded as D-14B-1 | checkpoint | manual, blocking | n/a | ⬜ pending |
| 14B-01 | 3 | GRAPH-01, PORT-03 | One objective end to end: mint, edge, sidecar compare-and-swap write, outline, package, clean restore. Empty-course and single-objective projection. Unknown section and column round trip | tracer | `python tests/graph_roundtrip.py` | `check_thin_slice()` | ⬜ pending |
| 14B-02 | 1 | GRAPH-02 | Four frozen edge types plus one unknown; degrade to advisory recommended-before, never dropped, never blocking; duplicate and self edge refused | unit | `python tests/graph_roundtrip.py` | `check_edges()` | ⬜ pending |
| 14B-02 | 2 | GRAPH-01, GRAPH-02 | Any local container label without a schema change; structural order mints no prerequisite edge; stable outline across runs; order validation without reordering; Kahn fallback with sorted tie-break; cycle named | unit + integration | `python tests/graph_roundtrip.py` | `check_structure_and_outline()` | ⬜ pending |
| 14B-02 | 3 | GRAPH-01, GRAPH-02 | Published schema fully checked by the shipped subset validator; byte-identical format additivity against the pre-phase golden parse | unit | `python tests/graph_roundtrip.py && python schema_validate.py && python tests/lesson_roundtrip.py` | `check_schema_file()`, `check_format_additivity()` | ⬜ pending |
| 14B-03 | 1 | GRAPH-01 | Bindings gated by `identity.rights_granted` at bind time; unknown and denied both refuse and name the fix; a revoked right refuses despite a stale snapshot; eleven treatment kinds closed | unit + integration | `python tests/graph_roundtrip.py` | `check_bindings_and_rights()` | ⬜ pending |
| 14B-03 | 2 | GRAPH-01 | Imported scope immutable; local edit is an overlay record with its own identity and a migration relation | unit | `python tests/graph_roundtrip.py` | `check_bindings_and_rights()` | ⬜ pending |
| 14B-03 | 3 | GRAPH-01 | Version migration prototype: older version upgrades through a named step, future version refused before any field is read, gap in the chain named | unit | `python tests/graph_roundtrip.py` | `check_version_migration()` | ⬜ pending |
| 14B-04 | 1 | (decision) | Where `migrate` lives and what a proposal carries, recorded as D-14B-3 | checkpoint | manual, blocking | n/a | ⬜ pending |
| 14B-04 | 2 | GRAPH-04 | `migrate` additive in `RECORD_TYPES` with `OPERATION_TYPES` still six; proposal is reviewed, rationale-bearing, never self-accepting | unit | `python tests/graph_roundtrip.py && python tests/evidence_roundtrip.py && python tests/scoring_roundtrip.py` | `check_migration()` | ⬜ pending |
| 14B-04 | 3 | GRAPH-04 | Split and rename produce proposals; evidence count unchanged; existing event keeps its original identity; each new identity reads unknown | unit + integration | `python tests/graph_roundtrip.py` | `check_migration()` | ⬜ pending |
| 14B-05 | 1 | (decision) | Package manifest format, recorded as D-14B-4 | checkpoint | manual, blocking | n/a | ⬜ pending |
| 14B-05 | 2 | PORT-03 | Manifest key set; rights gate on payload inclusion; five named loss categories; stable entry and loss ordering; duplicate-fingerprint sources not deduplicated; empty-course export; interrupted export refused | integration | `python tests/course_package_roundtrip.py` | `check_manifest_and_losses()` | ⬜ pending |
| 14B-05 | 3 | PORT-03 | Clean-machine offline restore with no shared state; fingerprints recomputed; both loss reports returned; idempotent evidence restore; Zip Slip, symlink, and oversized entry refused | integration, fault-injection-adjacent | `python tests/course_package_roundtrip.py` | `check_clean_restore()`, `check_archive_containment()` | ⬜ pending |
| 14B-06 | 1 | GRAPH-01, GRAPH-02, GRAPH-04, PORT-03 | All four requirement Fixture sentences as named scenario functions on one three-domain corpus; refuses to run against a red suite | tracer | `python tests/three_domain_tracer.py` | `scenario_three_domain_outline()`, `scenario_edge_vocabulary()`, `scenario_migration()`, `scenario_clean_restore()` | ⬜ pending |
| 14B-06 | 2 | (freeze gate) | Authorability: one-line diff on a hand edit, reordering round trip, line-length ceiling; plus the human judgment | tracer + manual | `python tests/three_domain_tracer.py` | `scenario_authorability_roundtrip()` plus human sign-off | ⬜ pending |
| 14B-06 | 3 | (decision) | Freeze scope confirmed against real evidence, recorded as D-14B-5 | checkpoint | manual, blocking | n/a | ⬜ pending |
| 14B-06 | 4 | (freeze gate) | Phase 13.9 gate checked; freeze declared on three green legs or withheld with the missing leg named | gate | `python tests/three_domain_tracer.py` then `for t in tests/*.py; do python "$t" \|\| exit 1; done` then `python itembank.py guard .` | `main()` | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

**Sampling continuity check (planner, 2026-08-14):** no three consecutive
code-producing tasks lack an automated verify. Every `auto` and `tracer` task
above names one. The four `checkpoint:decision` rows and the human half of the
authorability review are the only non-automated verifications in the phase, and
each is a decision or a judgment that cannot be automated rather than a gap.

---

## Wave 0 Requirements

- [ ] `tests/graph_roundtrip.py`: covers GRAPH-01, GRAPH-02, GRAPH-04
- [ ] `tests/course_package_roundtrip.py`: covers PORT-03
- [ ] `tests/three_domain_tracer.py`: freeze-gate tracer, following `tests/file_fault_tracer.py`'s structure (named scenario functions, a final `TRACER: N passed, M skipped, 0 failed` line, a precondition check that the shipped suite is green first)
- [ ] `fixtures/corpus_14b.py` (or an extension of `fixtures/corpus_14a.py`): three fictional, structurally faithful synthetic domains
- [ ] Framework install: none. The direct-execution convention needs no install step.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Authorability review | freeze gate | Judging whether a human can read and hand-edit the outline and the sidecar in plain Markdown or Obsidian is a human judgment, not an assertion | Open the generated outline and the cross-object edge sidecar in a plain editor and in Obsidian. Hand-edit one structural order entry. Re-run the projection. Confirm the edit round-trips and the diff is one line. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency measured, not asserted
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
