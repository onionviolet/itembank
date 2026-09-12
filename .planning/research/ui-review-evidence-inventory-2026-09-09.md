# UI review evidence inventory, 2026-09-09

**Scope:** Read-only inventory of recent learner UI evidence. This is not a new
whole-product audit, an implementation plan, or human acceptance.

**Current routing owner:** `phases/20-extensible-ui-foundation-and-interaction-clarity-pass/20-AUDIT-CROSSWALK.md`.
All conclusions below are sampled record evidence, not fresh UI findings or a
closure decision.

## Current signal

Phase 20 has passed its scoped deterministic transition, profile, disclosure,
and responsive fixtures. It has not passed human visual, touch-device,
screen-reader, 200% text, 400% zoom, or aesthetic review. A dated synthetic
course walkthrough reported a basic shelf to lesson to practice loop and a
false "Not started" resume cue after a recorded response. Fresh runtime
verification is needed before treating that report as a current defect. The
implementation has evidence for specified contracts, while learner experience
still needs sampled human review.

## Reusable progressive-history seeds

| Artifact and anchor | Role in a future history or ideaboard |
|---|---|
| `phases/20-extensible-ui-foundation-and-interaction-clarity-pass/20-AUDIT-INDEX.md` "Read order" and "Historical audit groups" | Existing index and routing rule. Use as the intake map, not as a timeline itself. |
| `phases/20-extensible-ui-foundation-and-interaction-clarity-pass/20-AUDIT-CROSSWALK.md` "Phase closure status" and "Reopen triggers" | Current disposition, owner, evidence, blocked condition, and reopening rules for each audited concern. |
| `phases/20-extensible-ui-foundation-and-interaction-clarity-pass/20-VERIFICATION.md` "Human and sampling results" | Separates passing deterministic legs from human legs owed and describes synthetic coverage limits. |
| `UI-INTEGRATION-2026-09-08.md` "Reconciliation" and "Verification record" | Accepted prototype-to-production mapping, route ownership, and responsive boundary. |
| `UI-CHARACTER-AUDIT-2026-09-06.md` "Scope and evidence", "Open design-language comparison", and "Replace-or-retain fitness rule" | Dated audit inputs and unselected visual candidates. Preserve them as proposals with their sampled evidence, not accepted design. |
| `phases/17B-production-vertical-tracer/evidence/17B-03-learner-pass.md` F1, F3, F4, and "Observed layouts" | Concrete learner-journey observations, regressions, open seams, and declared blind spots. |
| `SOURCE-TO-READING-NEXT-PACKET-2026-09-08.md` "Walkthrough evidence" and F1 | Newer, small real-route exercise. Records the resume-copy defect and a repeatable gate without inventing another store. |
| `phases/20-extensible-ui-foundation-and-interaction-clarity-pass/20-HOME-COMPARISON.md` "Learner job" | Historical disposition of Resume, Shelf, Agenda, and Path before the newer single-identity selection. |

## Gaps worth carrying forward

**G1, truthful resume and evidence context need reconciliation.** The dated
walkthrough reported a correct underlying resume at item 2 of 3 while the shelf
said "Not started." The earlier tracer reported unlabelled divergence between
course evidence and the global report. Fresh runtime verification is required
before either becomes a current defect. If reproduced, retain canonical
session/evidence references, observed copy, scope, and a verification result.
Do not add a parallel progress store. Evidence:
`SOURCE-TO-READING-NEXT-PACKET-2026-09-08.md` F1;
`17B-03-learner-pass.md` F4 follow-up.

**G2, several promised course areas need fresh visible-route verification.**
The dated tracer reported no visible source opening, saved notes, formal test,
or reviewed proposal/undo journey. This is an availability report, not proof
their underlying engines fail or a present-state defect. Track the dated result
and rerun the visible route before recording it as unavailable now. Evidence:
`17B-03-learner-pass.md` F4.

**G3, human acceptance is owed, not implied by fixture coverage.** Phase 20
automates keyboard, focus, targets, reflow, fallback, profile state, desktop,
and phone breakpoints. Its own record excludes touch, screen-reader, zoom, and
aesthetic acceptance. Evidence: `20-VERIFICATION.md` requirement table and
"Human and sampling results"; `UI-INTEGRATION-2026-09-08.md` verification.

**G4, reconcile older home-projection records with the newer accepted identity.**
The dated home table retained Resume and Shelf, with Agenda and Path registered
prototypes awaiting comparison. The 2026-09-08 vision entry resolves comparative
exploration and selects the greenfield learner interface as one product identity.
Preserve the old statuses and comparison evidence as history. Do not elevate
them into current requirements without a fresh decision. Evidence:
`20-HOME-COMPARISON.md` learner-job table; `USER-VISION.md` 2026-09-08
"adopt the greenfield learner interface" interpretation and relationship.

## Representative future review journeys

1. **Resume truth:** Shelf, recorded response, reopen, resume cue, current
   item, and named evidence/report scope.
2. **Learn-to-practice:** Course, assigned source or lesson, return context,
   practice, permitted hint, feedback pause, and exact resume.
3. **Course work and recovery:** Source opening with rights refusal, saved
   learner note, formal sitting, agent proposal review, accept or undo, and a
   truthful unavailable state at each missing seam.

Use the same fixture content across desktop and phone. Each event should retain
date, artifact/revision, claim type (observed, deterministic, proposal, human
review), counterevidence, disposition, owner, and reopen trigger. That makes
the surface auditable without letting accepted work erase prior rejected,
deferred, or unverified evidence.

## Blind spots

No new UI was launched. This inventory sampled planning records only. It does
not establish real learner efficacy, populated source/objective quality across
subjects, clean-machine restore, accessibility acceptance, or a final visual
direction.
