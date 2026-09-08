---
schema_version: 1
owner: user-reported product problems
editing_rule: append new reports and state transitions, do not rewrite observations
---

# Problem Ledger

This is the single intake for user-reported product problems. It complements
`WINDOWS.md`, which remains the narrow cross-phase ship blocker register.
Each record separates a direct observation from diagnosis, repair, and proof.
Do not close a row from an automated check when the report requires human
experience review.

## Open

### P-20260908-01: practice feedback skips the learner's review moment

**Reported by:** Weibao, 2026-09-08
**Status:** Repair in progress, unverified
**Area:** served Quiz, practice mode
**Severity:** High, learner-flow blocker

**Verbatim observation:**

> it should show correct and should remain in the same page before moving onto the next, Im not going to lie the UI looks same, and right now it says item 3 of 2, there are many things to adjust accordingly?

**Observed environment:** Local daemon, normal Courses to Course to Lesson to
Quiz flow. The browser was on `/quiz/study_skills_sample?receipt=...` after a
submission.

**Reproduction:** Submit the final auto-scored item through the server-rendered
form path. The receipt redirect can render the terminal runtime cursor as Item
3 of 2. Earlier correct answers advance before the learner sees the correct
verdict and chooses to continue.

**Diagnosis, separate from the observation:** The server form PRG advances the
runtime cursor before rendering its receipt page. The context band derives its
position from that terminal cursor, producing the impossible denominator. The
runtime owns the verdict and is not at fault.

**Repair scope:** Keep scoring, evidence, and keyed disclosure in the runtime.
Render the just-answered public item and runtime-issued verdict on the receipt
page. Offer one explicit Continue action that renders the already-current
runtime item. Use the submitted item's position in that pause screen.

**Evidence required to close:** A server-form test proves correct feedback,
one explicit Continue action, no duplicate evidence event, Item N of M during
the pause, and Item N+1 only after Continue. A human rechecks the actual flow.

### P-20260908-02: presentation profiles do not yet feel meaningfully distinct

**Reported by:** Weibao, 2026-09-08
**Status:** Open, audit required
**Area:** Phase 20 learner UI
**Severity:** High, Phase 20 acceptance blocker

**Verbatim observation:**

> the UI looks same as before

**Observed environment:** Local normal learner flow. Field Guide default home,
course overview, lesson, and practice were shown. Trajectory Deck was only
previewed in Settings and was not saved or exercised across the learner flow.

**Diagnosis, separate from the observation:** Not settled. Phase 20's contract
requires distinct composition and emphasis, but the required comparative human
review was not completed. Do not call profile values accepted on the strength
of deterministic DOM parity or a settings preview.

**Next action:** Run the bounded audit in
`PROMPT-PHASE-20-UI-IMPLEMENTATION-AUDIT-2026-09-08.md`. It must test the
actual learner entry flow and reconcile every current Phase 20 audit finding.

**Evidence required to close:** Weibao's comparison notes across both profiles
and the retained home projections, plus an evidence-backed disposition for
every audited finding.

### P-20260908-03: replace or retire presentation profiles only through a decision gate

**Reported by:** Weibao, 2026-09-08
**Status:** Registered proposal, decision required
**Area:** Phase 20 presentation profiles and default setting
**Severity:** High, product-direction decision

**Verbatim observation:**

> we might need to make new profiles as defaults, consider purging old ones and more

**Diagnosis, separate from the observation:** The current profile pair has not
met its comparative human acceptance gate. That is enough to investigate
replacement candidates. It is not evidence to delete existing settings values,
change the default, or claim a migration plan works.

**Decision gate:** First compare at least one replacement profile against Field
Guide and Trajectory Deck on identical learner flows. Then Weibao selects retain,
revise, replace, combine, or retire. A retirement proposal names settings
migration, invalid-value fallback, recovery, compatibility, and rollback before
any shipped profile is removed.

**Owner:** Weibao selects the experience direction. Phase 20 owns the audit and
any resulting migration proposal.

## Link audit, 2026-09-08

### P-20260908-01 state transition

**Status:** Fixed and deterministically verified. Direct local recheck passed.
Human acceptance remains owed.

**Direct evidence:** In the visible local flow, Courses to Sit sample_bank to
submit a correct table response rendered Item 1 of 6, the runtime-issued
"Correct. Your answer was recorded." verdict, and one "Continue to item 2"
link. Activating Continue then rendered Item 2 of 6. A fresh server after the
repair exposed only Tier 0 and one "I'm stumped" action, rather than all six
locked tiers.

**Deterministic evidence:** `python3 tests/serve_roundtrip.py` passed after a
new assertion that the first served page exposes exactly one locked hint tier.

### P-20260908-02 state transition

**Status:** Open, human comparison and decision required.

**Direct evidence:** Settings now renders an unsaved identical-state preview
for each profile. Field Guide keeps source context in a reading-oriented
composition before its final action. Trajectory Deck renders a named Current
task region with Continue before recovery and source detail. This repairs the
preview's cosmetic-only comparison, but it does not substitute for Weibao's
comparison of both profiles across the full learner flow.

**Deterministic evidence:** `python3 tests/presentation_profiles_roundtrip.py`
and `python3 tests/settings_roundtrip.py` passed. The profile choice was not
saved and no default, profile value, or migration state changed.
