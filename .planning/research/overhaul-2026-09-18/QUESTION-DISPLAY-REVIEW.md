# Question display and assessment review

Date: 2026-09-18. Status: audit, not implementation or parity acceptance.

## Answer

The previous overhaul covered assessment and interactive teaching at a planning
level. It did not establish that every question type, installed display or exam
journey had been tested. This follow-up adds source/test review, official
competitor documentation and a bounded rendered check.

Question display is partly enhanced. Native radio/checkbox controls, explicit
selection instructions, symbol help, runtime-controlled hints, own-selection
feedback and explicit Next are real features. The richer renewal and code
workspace prototypes are not proof those experiences have shipped in the app.

## Direct observations

| ID | Observation | Meaning and limit |
|---|---|---|
| V1 | Read-only installed-app inspection showed symbol definitions, Single choice instructions and radio controls. Its expanded assisted-question panel showed technical tier names and an empty lesson-pointer message. At the observed 1100 by 760 window, the answer list began below the fold. | Support competes with the decision surface. Prefer useful, compact, progressively disclosed help. No real answer was selected or submitted. |
| V2 | Installed accessibility text reported Math unavailable and formula source shown. The visible objective cue also appeared unrelated to the logic prompt. | Observed degraded/content states, not a diagnosed cause. Verify asset loading and authored objective binding separately. Do not silently rewrite the course. |
| V3 | A disposable served session using the synthetic selection fixture rendered table selects and accepted a response. Feedback stayed on Item 1 until explicit Next question, 2 of 30. The new prompt received focus. | Current source baseline transition worked in a real browser. This does not verify every installed route or all keyboard/screen-reader behavior. |
| V4 | On synthetic Item 2, selecting A and B produced wrong-answer feedback naming only selected A as right and selected B as not right. It disclosed nothing about unselected options. Submit remained available. Selecting A and C on retry succeeded. | The normal server-rendered multi-select retry path works. This does not falsify the separate API-driven retry findings. |
| V5 | After the wrong multi-select submission, every checkbox was unchecked. Feedback retained the prior response in text, but the editable response did not retain it. Successful feedback then removed choices and showed a short recorded message. | Preserve or explicitly distinguish the previous response from the next draft. Rich rationale and a response receipt are not demonstrated by this success state. |

The synthetic session used temporary output outside the repository. No learner
bank, existing sitting, installed application or production source was changed.
Screenshots of private course content were not saved into the repository.

## Assessment coverage and risks

See [the source audit](ASSESSMENT-AUDIT.md) for eight response types, ten
findings and exact seams. Its F1-F5 predict missing retry actions, dropped
feedback fields, stale response retries, empty-selection feedback and shuffled
letter-reference problems in the API-driven client. These require rendered
reproduction. They were not observed defects in the installed page.

The three paths are separate acceptance targets: server-native forms, the
no-baseline API-driven client and static offline builds. A static build contains
keys and records nothing. It cannot stand in for a protected served exam.

Executed checks passed: `tests/serve_roundtrip.py`,
`tests/surface_roundtrip.py`, `tests/presentation_profiles_roundtrip.py`, and
the assessment lane's `tests/hint_roundtrip.py`. Several JavaScript assertions
inspect emitted text rather than operating controls, so they cannot establish
complete UI flow.

Not completed: rendered MC retry, no-baseline API retry/error reproduction,
full exam closure, all eight response types, narrow-screen/touch review,
screen-reader acceptance, a full test suite or live competitor sittings.
These remain gates, not implied passes. Large implementation modules were
sampled by symbol rather than read completely.

## Five integration priorities

| ID | Proposed work | Acceptance |
|---|---|---|
| Q1 | Reliable transitions. Reproduce source findings F1-F5 and fix confirmed defects in their owning path. Add explicit answer-receipt and retry state. | MC/multi wrong-change-retry, empty input, interrupted acknowledgement, reload, duplicate submission and truthful summary pass in each applicable path. |
| Q2 | Question-first layout with compact useful help and response retention. Resolve observed math and metadata states through their actual owners. | Prompt, response rule and choices are easy to find. Previous response remains inspectable. Help never bypasses disclosure. |
| Q3 | Better misconception feedback and learner-owned review tools. Evaluate option-level explanations, reversible elimination and flags. | Annotations remain separate from responses and marks. Exam policy governs navigation. Restart preserves explicitly owned state. |
| Q4 | Rich shared stimuli and answer-plus-reason experiments. Evaluate graph/image/code alternatives and optional descriptive confidence. | Useful static alternatives, no cross-question leakage, stable option identity and no automatically settled prose marks. |
| Q5 | Predict, manipulate, explain, then transfer. Reuse planned interactive teaching primitives where interaction teaches something. | A second changed-content lesson reuses the primitive. An unassisted transfer question tests understanding beyond remembering the revealed answer. |

These extend existing packets, not a second roadmap. Q1/Q2 gate P1, Q3/Q4
refine P3, and Q5 strengthens P2. New schema, scoring or annotation storage
decisions require a bounded proposal before implementation.

## Useful competitor patterns

[QUESTION-PATTERNS.md](QUESTION-PATTERNS.md) preserves the official-source
register and broader ideas. Moodle supplies review flags and explicit feedback
policies. PrairieLearn separates checkbox feedback, selection bounds and scoring
and supports parameterized variants. Runestone documents rich options and
option-specific feedback. H5P documents image choices. These are documented
patterns, not proof of live usability or learning gains.

Some ideas were already in older research. This pass makes question-level
behavior and acceptance tests concrete. Elimination, two-stage reasoning and
the exact proposed combinations are our synthesis where the report says so.
They are not attributed to Brilliant without evidence.

No production fixes or commits were made. This audit does not claim feature
parity, accessibility acceptance or discovery of every useful idea.

## Q1 continuation, 2026-09-19

The user requested "audit and continue", then "continue with lesser cost
agentws accordingly". This continuation repairs demonstrated regressions in
the current candidate before broader P1 integration. Root owns integration.
Luna workers finish disjoint renderer, route, hint and verification work.

Scope is the API client's response controls, runtime-result projection,
uncertain acknowledgement recovery, truthful summary copy, symbol-definition
return routes, decimal-safe argument presentation and nonempty objective hints.
Existing runtime scoring, keyed disclosure and session formats remain the
authority. No new assessment policy, schema or durable learner object is added.
All trial content is synthetic and stays in temporary local roots.

Recovery reads the current session after an uncertain acknowledgement.
It never automatically retransmits an answer against an unknown cursor.
The learner explicitly continues from the returned view or reviews the same
question before submitting again. This is a bounded client repair, not a new
durable operation-receipt protocol.

The installed application, real course content and production rollout are
outside this source-candidate repair. Existing unrelated dirty changes are
preserved. Undo is a review of this continuation's diff, never a checkout reset.

### Repaired behavior

| ID | Result | Evidence boundary |
|---|---|---|
| C1 | API retry restores Submit for choice, assignment, ordering, prose and code controls. Empty MC cannot submit. Multi selection limits have visible count and recovery copy. | Behavioral DOM checks cover the exercised control paths. Synthetic Chrome covers MC and multi against the real daemon. |
| C2 | Runtime feedback, refusals and code observations survive API projection. Held or deferred responses do not invent option verdicts. Authored letters retain their meaning. | Projection tests use public envelopes. The server remains the scoring and disclosure authority. |
| C3 | Uncertain acknowledgement offers a saved-state read instead of resending to an unknown question. Summary copy no longer infers a clean sweep from an empty client history. | Behavioral tests cover same, advanced and complete cursors. Network-failure cases were not reproduced in Chrome. |
| C4 | Symbol-definition returns retain the explicit quiz mode and sitting. Numeric objective references no longer produce empty available hints. | HTTP return tests cover default, practice and exam routes. Existing restart selection policy is preserved. |
| C5 | Argument presentation preserves decimal values and falls back to authored prose for ambiguous abbreviations. Native wrong-answer retries retain selected controls through the existing expiring receipt. | DOM and focused HTTP checks own these boundaries. No new durable draft storage is claimed. |

### Verification and remaining work

All 40 JavaScript tests pass, including 22 new behavioral tests. Running the
new suite against the saved earlier served renderer produced 20 failures and
2 passes. That comparison did not replace shared checkout files.
Focused surface, serve, daemon, presentation-profile, protocol, hint and
symbol-return gates pass. The daemon suite covered 78 checks. Quick preflight
passed every executed gate. Full Python preflight, clean-tree and installed
desktop checks were not run for this bounded repair.
The existing serve roundtrip now asserts retained MC and multi selections
after a held response and no selection carryover after explicit Next.
That suite passed again after the final assertions were added.

A separate real Chrome journey loaded a generated page with zero
`data-server-baseline` elements and used a disposable proxy to the real daemon.
Wrong MC and multi responses retained their controls and selections. Correct
responses waited for explicit Next or View summary. Next focused the new
prompt. Own-selection feedback named only the chosen options. No scoring was
mocked. The synthetic processes and browser tab were cleaned up afterward.

The earlier server-native Chrome run reproduced lost selections and motivated
the receipt repair. A fresh daemon then passed a second native Chrome run:
wrong MC retained B, wrong multi retained B and C, and both retries remained
usable. Correcting MC and choosing Next opened multi without old selections
and focused its prompt. Correcting multi reached View summary. These runs used
only synthetic answers. Large modules were inspected around changed symbols
rather than read in full.

**Next gate:** finish Q1's two-item formal-assessment journey through its
existing runtime-owned close authority. Reproduce F6 and F8 before changing
exam or marker behavior. Q1 is not fully closed, and P1's connected-unit,
installed, human accessibility and comparative acceptance gates remain open.
Static offline option-reference parity also remains a separate check.
