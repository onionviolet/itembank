---
phase: 19D-math-1400
plan: 01
type: execute
wave: 1
depends_on: ["19A-09", "19B-01", "19C-01"]
files_modified:
  - .planning/phases/19D-math-1400/19D-CONTEXT.md
  - .planning/phases/19D-math-1400/19D-WALKTHROUGH.md
  - .planning/phases/19D-math-1400/19D-DEFECTS.md
  - .planning/phases/19D-math-1400/19D-VERIFICATION.md
  - .planning/REACH-CLOSURE-INDEX.md
  - .planning/STATE.md
autonomous: true
requirements: [TREAT-01, TREAT-02, RIGHTS-02, ACTIVITY-02, AGENT-01, AGENT-02, AGENT-03, APP-01, APP-02, RELIABILITY-02, RELIABILITY-03]
user_setup: []
must_haves:
  truths:
    - "A learner can enter the canonical shelf, open a real Math 1400 course, identify the current area and next action, and return home without a guessed URL or CLI repair."
    - "The course binds a per-title verified open licence and stable source locators, maps a representative unit to actual course objectives, justifies one direct reading, and accepts one reviewed generated treatment through the shared 19B agent door and repaired 19C backend."
    - "The learner can complete one continuous Learn, Practice, Test, evidence, next-activity, and back-home journey with a private note, source return, changed-context application, exact resume, and runtime-owned result."
    - "Visible transitions preserve orientation, history, focus, unsaved work, and legal next actions; empty, unavailable, interrupted, conflicted, and recovery states explain what happened and what the learner can do next."
    - "Every journey-blocking correctness, lost-work, navigation, or unusable-content defect is repaired at its owning seam and only the affected step is rerun; all other findings have an owner, evidence, disposition, and next action."
    - "Reach closes only with a compact audit index and the exact label `Reach achieved, broader vision and human legs open`; human and post-Reach legs remain explicitly open."
  artifacts:
    - path: ".planning/phases/19D-math-1400/19D-CONTEXT.md"
      provides: "Source-title licence read, representative-unit scope, approved roots, rights, and evidence rules"
    - path: ".planning/phases/19D-math-1400/19D-WALKTHROUGH.md"
      provides: "Rerunnable visible-flow transcript with start state, action, durable result, transition judgment, and failure record"
    - path: ".planning/phases/19D-math-1400/19D-DEFECTS.md"
      provides: "Observed-defect routing and affected-step rerun ledger"
    - path: ".planning/phases/19D-math-1400/19D-VERIFICATION.md"
      provides: "Focused gates, real sitting evidence, denominators, uncertainty, and recovery results"
    - path: ".planning/REACH-CLOSURE-INDEX.md"
      provides: "One-state, one-owner index for every current Reach audit finding"
  key_links:
    - from: "canonical shelf course card"
      to: "Math 1400 overview and course areas"
      via: "visible 19A links and opaque route identity"
      pattern: "shelf -> course -> Learn|Practice|Test|Evidence|Agent -> home"
    - from: "verified algebra source binding"
      to: "representative objectives and treatments"
      via: "19A add-source, add-objective, bind-treatment, and publish operations"
      pattern: "source_id.*locator.*objective_id.*treatment"
    - from: "19C local backend result"
      to: "accepted generated treatment"
      via: "19B stored proposal review, deterministic validation, accept, journal entry, and undo"
      pattern: "proposal_id.*accepted.*journal.*undo"
    - from: "assessment sitting"
      to: "next activity"
      via: "runtime evidence with observation window, denominator, uncertainty, and AGENT-03 recommendation"
      pattern: "denominator.*uncertainty.*next"
---

<objective>
Build and use one real representative Math 1400 unit through the product's own
visible doors, then close Reach from observed evidence.

Purpose: Prove that 19A's course routes, 19B's agent operation door, and 19C's
repaired backend form one dependable learner journey, including instruction,
assessment, recovery, and return transitions, without expanding into the
post-Reach visual redesign.
Output: A private on-disk Math 1400 course, one completed sitting, a rerunnable
journey transcript, routed defects, verification evidence, and the Reach audit
closure index.
</objective>

## Scope amendment, 2026-09-08

The user deferred local AI and said, "we can skip the sitting for now." This
plan closes as waived for milestone sequencing. Its failed and unrun gates stay
recorded in `19D-VERIFICATION.md` and `19D-DEFECTS.md`; they do not become
passes. Phase 20 may proceed without a model proposal or new sitting and may
not claim scores, mastery, recommendations, or dependent restore evidence.

<execution_context>
@.codex/get-shit-done/workflows/execute-plan.md
@.codex/get-shit-done/templates/summary.md
</execution_context>

<context>
@AGENTS.md
@.planning/phases/19D-math-1400/19D-SEED.md
@.planning/REACH-MILESTONE.md
@.planning/SOURCE-TO-COURSE.md
@.planning/AGENT-WORKFLOW.md
@.planning/PROMPT-REACH-FINALIZATION-AND-UI-HANDOFF-2026-09-07.md
@.planning/PROMPT-EXTENSIBLE-UI-CONTINUATION-2026-09-07.md
@.planning/phases/19A-course-operating-surface/19A-09-SUMMARY.md
@.planning/phases/19A-course-operating-surface/19A-09-VERIFICATION.md
@.planning/phases/19A-course-operating-surface/evidence/19A-08-manifest.json
@.planning/phases/19A-course-operating-surface/evidence/19A-08-loss-report.md
@.planning/phases/19B-agent-operation-door/19B-01-PLAN.md
@.planning/phases/19C-backend-on/19C-VERIFICATION.md
@.planning/phases/17C-maintenance-restore-audit/17C-AUDIT.md

<interfaces>
- `surfaces.course_ops.run(root, operation, request, actor_kind="human", actor_name="", base=None)` is the shared 19A operation dispatcher. Use its published operations and schemas, not private helpers.
- `surfaces.agent_operation.start`, `accept`, `reject`, and `undo` are the 19B proposal lifecycle. Acceptance uses stored proposal bytes and the journal; the browser must not repost draft bytes.
- The repaired 19C path resolves the active registered profile through `model_adapter.invoke`; deterministic validation and human review remain mandatory before acceptance.
- `surfaces.daemon.API_ROUTES`, `ROUTE_CLI`, and `SURFACE_PARITY` identify canonical public routes and twins. Visible flow begins from the shelf returned by the packaged or canonical browser-served shell.
- The runtime remains the only scorer and keyed-disclosure authority. Short prose remains pending unless settled by its authorized review path.
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Build the representative unit through 19A, 19B, and 19C</name>
  <files>.planning/phases/19D-math-1400/19D-CONTEXT.md, .planning/phases/19D-math-1400/19D-WALKTHROUGH.md</files>
  <action>
Create the real course below the user-approved external course root so no real
source, bank, learner note, or evidence enters this repository. Select one
representative Math 1400 unit from OpenStax College Algebra 2e only after
reading the exact title page and licence statement at execution time. Record
the title, edition, canonical URL, access date, licence text and URL,
attribution, permitted rights, restrictions, source fingerprint, approved read
and write roots, and remote-egress decision in `19D-CONTEXT.md`. If that exact
title is unavailable or the licence cannot be verified per title, stop before
binding and record the typed blocked state. Never infer rights from OpenStax as
a publisher.

Use only published 19A browser or public course-operation controls to create
the course, bind the source with stable locators, add the actual representative
objectives, and assign explicit treatments per TREAT-01, TREAT-02, and
RIGHTS-02. Review the unit against its source locators and objectives. Justify
one direct reading where the source is sufficient. Identify one genuinely
missing teaching treatment that includes a rich lesson and a coherent,
study-usable plain-Markdown fallback. Ask the repaired 19C active local backend
to draft that treatment through the 19B Agent tab. Record exact egress and
operation identity. Review citations, source fidelity, changed-context
application, uncertainty, plain fallback, deterministic validation, and the
bounded diff before accepting the stored proposal. Acceptance must create one
applied journal entry. Exercise visible Undo, prove byte-identical restoration,
then accept the reviewed proposal again as a separately identified operation
so the course retains the treatment. Do not accept weak backend output, invent
citations, or let the model define course, scoring, rights, or assessment
authority.

In `19D-WALKTHROUGH.md`, start the rerunnable transcript with the exact launch
command or packaged entry, shelf state, visible control labels, resulting
opaque route identities, durable object ids, fingerprints, proposal ids,
journal ids, undo result, and any failure. Do not use guessed URLs or a CLI to
repair missing navigation.
  </action>
  <verify>
    <automated>python3 tests/source_binding_surface_roundtrip.py &amp;&amp; python3 tests/binding_roundtrip.py &amp;&amp; python3 tests/course_ops_roundtrip.py &amp;&amp; python3 tests/agent_operation_roundtrip.py &amp;&amp; python3 tests/model_adapter_roundtrip.py &amp;&amp; python3 tests/seeding_roundtrip.py &amp;&amp; python3 itembank.py guard .</automated>
  </verify>
  <done>The external real course has a per-title verified rights record, stable source and objective bindings, one justified direct reading, and one source-grounded generated treatment accepted through the repaired backend and Agent door after a visible verified undo.</done>
</task>

<task type="auto">
  <name>Task 2: Complete and repair the visible shelf-to-learning journey</name>
  <files>.planning/phases/19D-math-1400/19D-WALKTHROUGH.md, .planning/phases/19D-math-1400/19D-DEFECTS.md, .planning/phases/19D-math-1400/19D-VERIFICATION.md</files>
  <action>
From the packaged or canonical browser-served shelf, follow visible controls
through course overview, source reading, the representative lesson, permitted
help, Practice, Test, evidence, next activity, and back home. Include one
private learner note, one source lookup or return, one changed-context transfer
item, leaving and returning mid-unit, and exact resume to the same durable
activity. Complete at least one real sitting. Use the runtime's public session
surface for selection, disclosure, scoring, pending prose, and evidence. Record
the observation window, numerator and denominator, unanswered and pending
counts, uncertainty, and one AGENT-03 next-activity proposal. Do not imply
whole-course mastery or settle prose outside the authorized review path.

For every transition record starting state, visible action, resulting URL or
opaque identity, current-area cue, next-action cue, focus destination, history
and Back behavior, unsaved-work result, durable evidence, and failure state.
Judge whether labels, hierarchy, status, and continuity make the experience
read as one product. Exercise populated and actionable empty states for shelf,
course areas, Agent history, evidence, and next activity. Exercise adapter
unavailable, interrupted durable operation and resume, proposal conflict, and
assessment recovery. Each state must distinguish what happened from what the
learner can do next, remain useful without scripting where the contract
promises it, and never require a guessed URL or CLI repair.

Record every observation in `19D-DEFECTS.md` with severity, affected rerunnable
step, evidence, owner, disposition, next safe action, and recovery. Repair only
correctness, lost-work, navigation, or unusable-content defects that block this
representative journey. Make each repair at the existing owning seam, preserve
unrelated concurrent edits, run its focused existing test, and rerun only the
affected walkthrough step. If a blocking repair requires files not named by
the owning prior plan, stop with the exact target and evidence instead of
expanding 19D implicitly. Route presentation refinements that do not block the
journey to the post-Reach UI continuation. Do not implement presentation
profiles, a new renderer, a route table, a state store, or a broad redesign.
  </action>
  <verify>
    <automated>python3 tests/home_roundtrip.py &amp;&amp; python3 tests/lesson_roundtrip.py &amp;&amp; python3 tests/agent_operation_roundtrip.py &amp;&amp; python3 tests/evidence_roundtrip.py &amp;&amp; python3 tests/assessment_authority_adversarial.py &amp;&amp; python3 tests/journal_roundtrip.py &amp;&amp; python3 tests/course_ops_roundtrip.py &amp;&amp; python3 tests/daemon_roundtrip.py</automated>
    <human-check>Record representative screen-reader, visual, and instructional acceptance as human owed unless a human signs those exact walks. Automated keyboard, reflow, disclosure, and source checks are evidence, not human certification.</human-check>
  </verify>
  <done>The transcript proves one visible shelf-to-Learn-to-Practice-to-Test-to-evidence-to-home journey, exact resume and interruption recovery, one real sitting and bounded next recommendation, with every blocker repaired and rerun or the phase left explicitly unmet.</done>
</task>

<task type="auto">
  <name>Task 3: Exercise recovery and publish the Reach closure index</name>
  <files>.planning/phases/19D-math-1400/19D-WALKTHROUGH.md, .planning/phases/19D-math-1400/19D-DEFECTS.md, .planning/phases/19D-math-1400/19D-VERIFICATION.md, .planning/REACH-CLOSURE-INDEX.md, .planning/STATE.md</files>
  <action>
Export the course through the 19A public control, verify its manifest, restore
it into an isolated empty root, and replay the representative source, lesson,
session/evidence, note, and resume checks against the restored copy. Attach or
link the generated manifest and loss report without committing private course
content. Map each applicable `17C-AUDIT.md` F-LOSS finding to observed retained,
lost, unsupported, or repaired behavior. Never call recovery clean when an
applicable loss remains. Keep second-person cold install and external first use
under Phase 18.

Complete `19D-VERIFICATION.md` with exact focused and full gate commands,
results, course and source fingerprints, source licence evidence, route and
operation ids safe to publish, sitting denominator, pending and uncertain
evidence, accepted and undo journal links, interruption recovery, export and
restore evidence, all F1 through F5 outcomes, and which large files were only
sampled symbol-first. Run quick preflight, then full preflight on the exact
candidate revision. A red deterministic gate remains red and blocks only the
outcome it proves unless evidence shows it is inherited or platform-only.

Create `.planning/REACH-CLOSURE-INDEX.md` as the single compact index for every
current vision, UI, recovery, human-gate, and external-install finding. Give
each exactly one state: verified closed, human owed, deferred with trigger,
superseded with replacement evidence, or rejected with reconsideration
condition. Link its evidence and owner. No item may remain as ambiguous later
work. Link the existing 14A/14B multi-root and plain-file evidence, 17B subject
tracer, 17C recovery audit, Phase 18 install evidence, UI character audit, and
19D records rather than replaying their suites. Update `STATE.md` from observed
results. Use the exact label `Reach achieved, broader vision and human legs
open` only when the real journey and deterministic gates pass. Otherwise name
the failed step, retained evidence, owner, and next safe action and leave Reach
open.
  </action>
  <verify>
    <automated>python3 scripts/vision_audit.py &amp;&amp; python3 scripts/preflight.py --quick &amp;&amp; python3 scripts/preflight.py</automated>
  </verify>
  <done>The isolated restore has an attached manifest and honest loss report, every current audit finding has one evidence-linked state and owner, STATE matches observation, and Reach receives its exact bounded completion label only after the real journey and all applicable deterministic gates are green.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Public source to accepted course | External content, licence claims, and locators cross into learner-owned durable records. |
| Local model to proposal review | Generated teaching content and citations are untrusted until validated and explicitly accepted. |
| Browser to runtime assessment | Learner responses cross into the sole scoring, disclosure, and evidence authority. |
| Course root to export and isolated restore | Private content and evidence cross a packaging boundary with possible loss or unintended egress. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-19D-01 | Spoofing | source and licence identity | mitigate | Capture canonical per-title URL, licence URL, access date, source fingerprint, and attribution before binding. |
| T-19D-02 | Tampering | generated treatment acceptance | mitigate | Stored proposal identity, deterministic validation, expected-base fingerprint, human review boundary, atomic journal commit, and verified undo. |
| T-19D-03 | Repudiation | course build and sitting | mitigate | Retain operation, proposal, journal, session, evidence, manifest, and rerun identifiers in the walkthrough and verification records. |
| T-19D-04 | Information disclosure | model egress, UI, export | mitigate | Declare exact egress, keep real course data outside the repository, preserve runtime key tiers, and inspect package manifest and losses. |
| T-19D-05 | Denial of service | backend and interrupted operations | mitigate | Typed unavailable state, durable interruption record, exact resume point, and authored fallback that leaves learning usable. |
| T-19D-06 | Elevation of privilege | model recommendation and prose mark | mitigate | Model output stays advisory; reviewer accepts content, runtime settles deterministic scores, and pending prose is not silently graded. |
| T-19D-SC | Tampering | package installs | accept | No package-manager installation occurs in this plan. |
</threat_model>

<source_audit>
GOAL is covered across Tasks 1 through 3. REQ TREAT-01, TREAT-02, RIGHTS-02,
AGENT-01, and AGENT-02 are exercised in Task 1. REQ ACTIVITY-02, AGENT-03,
APP-01, APP-02, RELIABILITY-02, and RELIABILITY-03 are exercised in Tasks 2
and 3. RESEARCH and the 19D seed require a per-title licence read, real
representative unit, one direct reading, one missing generated treatment, one
sitting, honest denominators, source locators, and no claim of broad course
coverage; Tasks 1 and 2 cover each. CONTEXT is not yet a separate artifact, so
Task 1 converts the locked seed and Reach F1 through F5 into the required
source-specific operation record before mutation. Post-Reach presentation
profiles, broad visual redesign, external package loading, second-person cold
install, broader subject proof, and human certification are excluded and
remain linked in the closure index.
</source_audit>

<verification>
The real external course and licence record exist. The visible transcript
contains every seed step with start state, visible action, durable evidence,
transition quality, and failure record. Focused route, source, lesson, agent,
assessment, evidence, journal, export, and restore checks pass. Quick and full
preflight pass or any exact inherited/platform failure is retained without a
false green claim. The closure index gives every current finding one state,
owner, and evidence link.
</verification>

<success_criteria>
A real Math 1400 representative unit is built through 19A, 19B, and the repaired
19C backend from a per-title verified open-licence algebra source. A learner
completes the visible shelf-to-learning-to-assessment-to-evidence-to-home
journey and one sitting without guessed URLs or CLI repair. Blocking defects
are repaired and rerun, recovery losses are reported honestly, and the Reach
closure index supports the exact bounded milestone label while preserving all
human and post-Reach obligations.
</success_criteria>

<output>
Create `.planning/phases/19D-math-1400/19D-01-SUMMARY.md` when done.
</output>
