# Implementation-readiness audit checklist (gates Phase 14A)

**Status:** slice-5 audit spec. Run this as a single bounded pass, not a research
stream. It exists to catch silent contract drift cheaply before any Phase 14A
implementation plan, and to stop further documentation expansion.

**Source obligation:** `.planning/research/phase-16/14-synthesis.md` section 16.3.
**Inputs:** the updated contract files (SOURCE-TO-COURSE, PROJECT, REQUIREMENTS,
ROADMAP, UI-SPEC, PLANNING-DIRECTIVES, AGENTS, .claude/CLAUDE.md, README) and the
mirrored skill library.
**Outputs (exactly two):** an audit report and a contract-delta patch. The audit
produces no new requirements prose of its own.

The audit is complete when every box below is checked or explicitly waived with a
recorded reason. Any **Fail** condition blocks the Phase 14A plan.

## A1. Clause-fidelity diff (16.3.1)

- [ ] Extract every accepted clause from synthesis sections 2 through 13 into a
      flat list.
- [ ] Locate each clause's landing across the contract files and skills.
- [ ] Tag each landing: faithful, missing, duplicated, conflicting, or weaker.
- [ ] Every non-faithful tag gets a one-line fix in the delta patch.
- **Fail** if any accepted clause has no landing.

## A2. Requirement completeness matrix (16.3.2)

- [ ] Every requirement in the eighteen families (GRAPH through MAINT) carries all
      nine fields: owner, durable object, authority, subphase, prerequisite,
      fixture, success gate, degraded state, migration, documentation, maintenance
      owner.
- **Fail** on any requirement missing a subphase or a fixture (the two execution
  handles an executor needs).

## A3. Prototype-before-freeze ordering (16.3.3)

- [ ] For each freeze gate in synthesis section 15, confirm its named prototype is
      scheduled earlier in the sequence:
  - graph-to-outline before course schema freeze
  - markdown rich-lesson stress corpus before lesson-profile grammar freeze
  - guided-note, worked-reasoning, incorrect-note pathways before strategy registry
  - restricted notebook preview before execute/trust UI
  - visual-math equivalence before broad interaction registry
  - cross-client interruption before agent job protocol freeze
  - clean-machine restore before course package or export promise
  - three visual directions before Phase 17 token freeze
- **Fail** on any freeze whose prototype lands in the same or a later subphase.

## A4. Dependency graph, no cycles (16.3.4)

- [ ] Build the ownership graph across course, lesson, evidence, notes, jobs, and
      UI state.
- **Fail** on any circular ownership. Note: notes owning lesson truth, or
  presentation state owning authorization, are already hard-rejected, so a cycle
  through them is a red flag, not a modeling choice.

## A5. Work-type separation (16.3.5)

- [ ] Classify every requirement as foundation, prototype, productization,
      migration, documentation, packaging, or maintenance.
- [ ] Confirm no subphase silently bundles productization into a foundation
      prototype (the failure that made the original four-phase plan too coarse).

## A6. No second authority; shipped tests intact (16.3.6)

- [ ] Grep the deltas for any new parser, scorer, or evidence store. **Fail** on any.
- [ ] Confirm the course manifest is an index composing existing contracts, not a
      new store.
- [ ] Confirm the shipped parser/scorer/evidence test suite is asserted
      byte-compatible where required.

## A7. Execution sequence and re-audit triggers (16.3.7)

- [ ] Emit the realistic ordered sequence: 14A, 14B, then the parallel fork of the
      15 track (15A, 15B) and the 16 track (16A, 16B, 16C), converging at 17A, 17B.
- [ ] Register three named re-audit triggers: after 14B, after 16C, after 17B.

## A8. Disposition and rejection integrity (16.3.8)

- [ ] Every research proposal has a disposition in synthesis section 12.
- [ ] Every section 12.4 hard-reject carries all eight fields: proposal, origin,
      evidence, exact reason, conflicting rule, retained alternative, date,
      reconsideration condition.
- **Fail** on any simplicity-only rejection or any silently deleted proposal.

## Bake-in gate (research findings that are cheap now, expensive later)

Before sign-off, confirm these Phase 16 research findings are written into the
16A/16B requirement stubs:

- [ ] Worked example before formal definition as the default lesson block order
      (16A). Source: `research/2026-08-10-style-registry-mechanics.md`.
- [ ] No compelled learner highlighting; author-provided semantic emphasis only.
      Learner highlighting aids memory but not comprehension (16A / CAP family).
      Source: `research/phase-16/12-active-annotation-notes.md`.
- [ ] Difficulty, Stability, and Retrievability are inspectable, but Retrievability
      is never surfaced to the learner as a percentage (16B honest-progress).
      Source: `research/2026-08-10-ui-inspiration-missing-surfaces.md`.

## Sign-off

- [ ] Audit report written.
- [ ] Contract-delta patch written and applied.
- [ ] Three gating pre-14A decisions resolved (see
      `DECISIONS-PRE-14A-2026-08-14.md`).
- [ ] STATE.md updated: slice 5 complete, Phase 14A unblocked.
