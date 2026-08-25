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
- **Fail** on any freeze whose prototype has not completed before the freeze
  commits. A prototype satisfies this when it lands in an earlier subphase, or
  earlier within the freezing subphase whose exit gate is the freeze; in the
  latter case the subphase's plan set must order the tracer/prototype plans
  first and the freeze commit last, explicitly. *(Wording amended 2026-08-14 by
  the audit: the original "same or a later subphase = Fail" would fail the
  synthesis section 15 table itself, where six of eight freeze gates are the
  prototype passing at that subphase's exit.)*

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

## A9. Walking-skeleton gate (added 2026-08-14)

**Vision source:** `USER-VISION-INBOX.md` entry 2026-08-14 (walking skeleton),
following the 2026-08-14 direction review. **Rationale:** the nine-subphase
sequence proves durability first and learner value last; the only end-to-end
tracer (17B) is the final gate, while Weibao's live courses (EMT, Math 1400,
CSCI 1100) begin within weeks of this audit. The biggest unresolved risk is not
any subsystem but whether the loop as a whole produces something a learner
wants to use, and the sequence currently answers that question last. The
skeleton inverts that: a thin, ugly, real slice early, with the deep phases
frozen only after the slice has been walked.

- [x] The Phase 14A plan set (or a sibling plan scheduled no later than 14B)
      names a **walking-skeleton tracer**: one real source from one live fall
      course, discovered and bound read-only, mapped to at least three cited
      objectives, with a recorded treatment decision per objective (at least
      one direct reading and at least one generated lesson plus practice), and
      **sat by Weibao end to end** through the shipped serve/teach/evidence
      loop. Ugly is acceptable; simulated is not.
      (satisfied 2026-08-24: Phase 13.9 plans 01 through 03. One real source
      (`src-01`, Weibao's own worked AAOS 12e chapter sheet), four cited
      objectives, both treatment kinds recorded (obj-01 and obj-04 direct
      reading, obj-02 and obj-03 lesson plus practice), sat end to end through
      `itembank serve` as session `13d56ab15efb4709821a6dd86357a5dc`, status
      complete, 10 items, 18 auto attempts and 1 settled human mark. Counts,
      hashes and pointers in `13.9-CALIBRATION.md`. It was ugly: the sitting
      before it produced one response of ten and exposed a blocking runtime
      defect, recorded in `13.9-DECISIONS.md` 2026-08-24 and fixed under
      `.planning/quick/260824-m4k-marker-closed-transition/`. It was not
      simulated.
      **Open, and deliberately not waived:** Task 1 step 4's two-sentence
      reaction after the sitting is still uncaptured. It is Weibao's to give
      and no agent may write it for him. It is evidence about the experience,
      not about whether the skeleton was walked, so it does not hold this
      checkbox open, and the slot stays named here until he fills it.)
- [x] The skeleton runs on shipped surfaces (`serve`, `lesson`, `study`,
      `teach`, evidence). It may stub course-level storage with the smallest
      14A identity/journal slice, and it introduces no second parser, scorer,
      or evidence store (A6 applies to it in full).
      (satisfied 2026-08-24: the sitting ran on `itembank serve` with no
      flags beyond the defaults, the reading was the direct-reading treatment
      in `course.md`, the hint ladder used was the shipped authored one (four
      tiers opened on one item, `stumped` path), and every response went
      through `runtime.score_response` into the one `_evidence/evidence.jsonl`.
      No second parser, scorer, or store was added by 13.9; `course.md`
      remains a stub no tool parses, as 14B-01 records.)
- [x] Evidence recorded by the skeleton sitting lands in the one evidence
      store, and at least one later plan (14B, 15A, or the 3.2-style warning
      calibration obligations) names that evidence as its calibration corpus in
      place of a synthetic fixture.
      (satisfied 2026-08-24: all 19 responses, 4 hint events and 1 mark landed
      in `<course-root>/_evidence/evidence.jsonl` and are queryable per
      objective with honest denominators. `13.9-CALIBRATION.md` names three
      consumers, and both `14B-VALIDATION.md` and `15A-VALIDATION.md` now cite
      it by name. What the corpus replaces is the claim that a synthetic
      corpus is sufficient evidence; it cannot replace the generated fixtures
      themselves, because no real item text may enter this repository and
      `itembank guard` enforces that.)
- [x] Phase 13.5 waves 3 and later are scheduled before or beside the
      skeleton, or explicitly waived with a reason, because the skeleton
      renders through exactly the surfaces 13.5 hardens.
      (WAIVED 2026-08-24 by Weibao, reason and measured supporting evidence in
      `13.9-DECISIONS.md` entry 2026-08-24: 17A-02 and 17A-03 hardened the
      token layer and primitive layer these surfaces render through on the same
      date, and a smoke test of the sitting path found the loop working with
      one cosmetic defect, `Item 1 of 0`, routed to 13.5. This waiver closes
      this checkbox only; every other A9 box still requires the real sitting.)
- [x] Freeze gates in A3 that the skeleton can exercise cheaply (graph-to-
      outline, rich-lesson stress corpus) cite skeleton artifacts where they
      exist rather than inventing parallel fixtures.
      (satisfied 2026-08-24: `14B-VALIDATION.md` and `15A-VALIDATION.md` carry
      a dated calibration-corpus row pointing at `13.9-CALIBRATION.md`, and
      14B-06's existing freeze gate already checks that Phase 13.9 has been
      walked. The citation is a pointer to artifacts outside this repository,
      which is the only form it can take under the guard.)
- **Fail** if the first learner-visible course experience in the sequence
  remains 17B.

## A10. External-user v1 bar (added 2026-08-14)

**Vision source:** `USER-VISION-INBOX.md` entry 2026-08-14 (external-user v1
and agent-guided onboarding). A "proper v1" now means: a friend with no
knowledge of this project can install it, be walked through setup by an AI
agent reading the public repo, and get real value from the shipped loop. This
audit does not build any of it; it checks that the roadmap owns it.

The bar, stated once so plans can cite it:

1. **Install without folklore.** One downloaded artifact plus Python 3.11+, or
   the Phase 13 shell. The macOS Gatekeeper workaround is documented where the
   user hits it. `V2-DEL-01`'s recorded trigger ("when a second person runs
   the tool") has now fired: signing gets a dated cost decision, not silence.
2. **Agent-guided onboarding.** The README carries a section a coding agent
   can follow cold: verify Python, fetch, launch, author a first bank from the
   user's own material, run a first graded sitting. The user's only skill is
   pasting the repo URL into Claude Code or a peer.
3. **First-run self-explanation.** A fresh launch shows something that
   explains itself (sample bank or walkthrough), not an empty directory.
4. **Scope honesty.** User-facing docs sell only the shipped bank/lesson/
   session loop. The course workspace is described as being built, never
   implied present.
5. **Privacy defaults hold for a stranger.** Fresh install never phones home
   without disclosure (the D-13 divergence stays repo-only), evidence stays on
   disk, and the update check discloses before its first request.
6. **Recovery.** Common failure states (wrong Python, port taken, quarantine
   flag, offline) name the next safe action in the error itself.

Checks:

- [ ] ROADMAP names an external-user v1 milestone (or a dated deferral
      decision) that carries the six criteria above as its acceptance bar.
- [ ] The onboarding README section exists and a cold agent transcript (any
      agent, one run) is recorded as its fixture.
- [ ] The "Users: One" constraint text in `.claude/CLAUDE.md` and `AGENTS.md`
      is amended to "one learner per installation; external installations
      supported; still no accounts, auth, or multi-tenancy" in the delta
      patch.
- **Fail** only on the constraint-text check; the milestone may be deferred
  with a recorded reason, but the recorded scope must stop saying a second
  user gets no design work.

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
