---
quick_id: 260813-x3g
status: complete
date: 2026-08-14
files_modified:
  - .planning/ROADMAP.md
  - .planning/SOURCE-TO-COURSE.md
  - .planning/REQUIREMENTS.md
  - .planning/PROJECT.md
  - .planning/UI-SPEC.md
  - .planning/PLANNING-DIRECTIVES.md
  - AGENTS.md
  - .claude/CLAUDE.md
  - README.md
---

# Quick Task 260813-x3g Summary

Source-to-course contract reframe: applied `.planning/research/phase-16/14-synthesis.md`
section 14 across the planning contracts and top-level docs. Every edit is additive
or a bounded REPLACE; superseded content is dated 2026-08-13 with forward pointers,
never deleted. Zero em dash characters introduced in any slice.

## Slices done and committed

- **Slice 1** (commit 8b5cab4): ROADMAP.md flat Phase 14-17 -> nine subphases
  (14A, 14B, 15A, 15B, 16A, 16B, 16C, 17A, 17B) with deliverable/depends-on/freeze
  gate each, plus four governance clauses (prototype-before-freeze;
  implementation-readiness audit gate before any 14A plan; post-Phase-17
  maintenance/restore audit; capability runway; permanent rejection ledger).
  SOURCE-TO-COURSE.md "Next-milestone sequence" points at the subphases. Originals
  preserved as historical rationale.
- **Slice 2** (content in commits e838407 + e349c06): REQUIREMENTS.md expanded into
  eighteen families (GRAPH, FILE, ID, TREAT, FLOW, CAP, ACTIVITY, NOTE, STRATEGY,
  RIGHTS, A11Y, PORT, RELIABILITY, APP, VISUAL, AGENT, UPGRADE, MAINT). 47 new
  requirements, each with Owner / Durable object / Authority / Degraded / Gate
  (gates tied to synthesis G1-G12). Twelve old IDs (COURSE/DIRECTOR/LEARNUI) mapped
  and relabeled superseded with an old-to-new table; universal-hierarchy,
  aggregate-progress, and widget-lesson-grammar patterns explicitly superseded.
- **Slice 3** (commit e838407): PROJECT.md course-first product framing +
  boundaries (derived views not truth; presentation not authorization; note content
  not assessment authority). UI-SPEC.md section 15 additions: course-first IA,
  route/resume, durable jobs, approval hierarchy, error/recovery matrix, structured
  map/pane/diff/activity/progress equivalents, Structured Studio visual direction,
  six new acceptance scenarios. The nine LOCKED accessibility gates in UI-SPEC
  section 8 are untouched. PLANNING-DIRECTIVES.md: finite-strategy qualification on
  "build both", append-only rejection record, accepted-recommendation discipline,
  mandatory reversible prototypes, and section 8 replaced with the nine-subphase
  dependency table (original preserved).
- **Slice 4a** (commit e349c06): AGENTS.md object/authority model + operation
  protocol (compare-and-swap, rights/egress, state axes, accessibility, clean
  recovery) and expanded course workflow steps; .claude/CLAUDE.md mirrors the same
  summary plus the rejection-ledger rule (Runtime invariant and five
  non-negotiables intact, purely additive); README.md leads with the
  source-to-course journey, task-oriented paths, and honest shipped-vs-planned
  status (no item-parseable fenced block added).

## Commit-hygiene note

REQUIREMENTS.md was written by a background agent while slices 3 and 4a were being
committed, and `gsd-tools query commit` sweeps all modified tracked files, so the
REQUIREMENTS content landed split across e838407 and e349c06 rather than in its own
commit, and 2 lines of a 13.5-track planning doc (13.5-GATES.md) rode into e838407.
Content verified complete and coherent on disk (all 18 families, 47 requirements
with all five fields, old IDs preserved, working tree clean); nothing lost. No
13.5-track source code was captured in the reframe commits. History was not
rewritten because the parallel 13.5 execution track was committing to the same
`main` concurrently.

## Still owed before any Phase 14A plan

- **Slice 4b (skills):** rewrite build-course, curriculum-design, absorb-book,
  author-bank per synthesis section 10; mirror `.agents/skills` <-> `.claude/skills`;
  add lesson-authoring, discovery-and-binding, media-intake, legacy-upgrade skills
  and a shared object/permission/rights/provenance/acceptance/recovery reference.
- **Slice 5 (readiness audit):** the synthesis section 16.3 implementation-readiness
  audit. It gates Phase 14A: diff every accepted synthesis clause against the
  updated contracts, map each requirement to owner/subphase/prerequisite/fixture/
  gate/degraded-state/migration/docs/maintenance, confirm prototypes precede their
  freezes, reject circular ownership, confirm the shipped parser/scorer/evidence
  stay byte-compatible, and confirm every proposal has a permanent disposition.

**Resume point:** run slice 5 (readiness audit), which will also flag slice 4b as a
known open gap rather than assert full coverage.
