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

### P-20260913-01: course Practice and Test hide available learner content

**Reported by:** Weibao, 2026-09-13
**Status:** Deterministically fixed and installed; human acceptance pending
**Area:** installed macOS app, course Practice and Test
**Severity:** High, current-course learning-flow blocker

**Verbatim observation:**

> I dont see practice or test content in app yet for some reason, thoughts and suggesrtions?

**Observed environment:** Itembank 0.4.0 was running its sidecar against
`/Users/weiwei/Documents/itembank`. The live CSCI 1100 Practice area said
"Nothing has been added to Practice for this course yet." The workspace course
entries are directory symlinks. The CSCI target already contains
`selection-and-boolean-practice.md`, a six-item formative bank, and its course
graph records that practice treatment.

**Diagnosis, separate from the observation:** Reproduced as two defects. First,
the course shelf discovers immediate symlinked course directories, while the
daemon's startup bank scan uses `os.walk(root)` without following those links.
The Practice area only displays banks admitted by that startup scan, so it sees
none inside symlinked courses. The running daemon also started before the
current symlinks were created, which independently requires a rescan or restart.
Second, `_course_area_rows` implements Learn and Practice rows but has no Test
branch. Test therefore resolves to the generic empty state even when a course
contains banks. This is presentation and discovery failure. No scoring-runtime
failure was observed.

**Owner:** `surfaces/daemon.py` owns startup bank discovery and course-area
projection. Workspace-root and symlink policy must remain consistent with the
identity and containment rules in `surfaces/ia.py`.

**Suggested repair order:** Add a safe course-aware scan that resolves approved
course entries without escaping the workspace. Refresh that allowlist when the
workspace changes or expose an explicit rescan action. Then implement Test as a
separate fixed-sitting launcher backed by the existing runtime rather than a
second scorer. Finally, test the installed app with a symlinked course that
contains one lesson bank and one practice-only bank.

**Evidence required to close:** In a fresh installed-app process, the CSCI
Practice area visibly lists the existing six-item bank and opens a scored
practice sitting. Test visibly lists an eligible fixed test and starts it under
formal conditions. A newly added approved course artifact appears after the
documented refresh action. Containment tests prove that out-of-root symlink
targets remain refused. Human acceptance remains required.

**2026-09-13 implementation record:** `surfaces/daemon.py` now rescans immediate
approved course links without following nested escapes. Practice publishes only
explicit `practice` treatment bindings. Test publishes only explicit
`formal-test` bindings and launches the existing runtime in a separate fixed
exam-mode sitting. `tests/daemon_discovery_roundtrip.py` and
`tests/course_assessment_area_roundtrip.py` cover the new contracts, and
`tests/ia_route_roundtrip.py` covers the course route. Focused daemon, course,
serve, and math-offline suites pass. Quick preflight passes every runnable gate
except pre-existing skill-mirror drift at `.agents/skills/author-bank/_attempts`.

The signed macOS bundle and DMG were rebuilt. The previous installed bundle is
recoverable at `/Applications/itembank.app.backup-20260913`. In the fresh
installed process, CSCI Practice visibly listed its six-item bank and opened
Item 1 of 6. A distinct MATH 1400 Discrete Mathematics course visibly listed
the accepted 12-item §§1.1-1.2 formative bank after IDs, source rights, graph
bindings, and the workspace link were recorded. Its Test area remained empty,
which is correct until a reviewed bank receives a `formal-test` binding. The
synthetic fixed-exam contract is deterministically verified, but the real-test
content and human acceptance parts of this problem remain open.

The same installed process refreshed without a restart after later course
writes. CHIN 3101 Practice visibly listed a 22-item eligible-vocabulary pool.
POL 1005 Practice visibly listed a six-item independent general-IR enrichment
bank. CHIN does not guess the instructor-selected ten words. POL uses no
assigned course material. Both remain formative only, with Test empty.

MATH 1400 Test then visibly listed an eight-item Quiz 1 readiness self-test
covering the locally verified §0 and §1.1 scope. Opening it showed Item 1 of 8
in runtime `exam` mode and stated that feedback is held until the attempt is
marked. No answer was submitted during verification. This supplies the real
formal-test acceptance fixture that was previously missing. Only the learner's
human acceptance of the installed experience remains open.

## Link audit, 2026-09-08

### P-20260908-04: selected course navigation text disappears

**Reported by:** Weibao, 2026-09-08
**Status:** Reproduced, repair in progress
**Area and owner:** shared course navigation, `surfaces/presentation.py`

**Verbatim observation:**

> make prompt to audit little bugs and more like color of the text. being the same as the shading once its clicked on and more, then run in new hat, make sure we have absorbed all good and missing features from the other stuff and more accordingly

**Observed environment:** The supplied screenshot shows Current area: Learn
and an unreadable selected pill. Input method was not supplied. The live local
course was initially on Practice. Clicking Learn reproduced the screenshot.
Current settings were Neo, light, Field Guide, and custom accent `#1e46c8`.

**Diagnosis, separate from observation:** Browser computed styles on both
routes returned `rgb(36, 58, 68)` for selected text and background, or 1:1
contrast. The Neo look supplies a dark selected background. The later product
shell replaces only its foreground with the same dark product ink. Both desktop
and mobile navigation copies inherit the collision. Route, heading, and
`aria-current` agree, so no route-state mismatch was reproduced.

**Repair scope:** Own the selected foreground and background together in the
shared product rule. Preserve underline and `aria-current`, appearance settings,
routes, and runtime authority. Regression and browser checks cover look/theme
and presentation-profile combinations. Human accessibility acceptance remains
separate. The competitor reconciliation belongs in the existing ABSORPTION.md.

**Before-repair evidence:** `python3 tests/navigation_color_roundtrip.py`
failed its final-rule check in all 56 configuration combinations. The contrast
test for the intended paired tokens passed. Those structural failures do not
mean all 56 variants had an identical visible collision.

**Nearby finding:** The same Neo navigation renders inactive labels with
`#65716f` on `#e6eade`, measured at 4.15:1 for 14px text. The bounded repair
uses existing product ink for these labels as well. This is an agent-observed
contrast defect, not a second quotation from the user.

### P-20260908-05: Courses links return to Your desk

**Reported by:** Agent walkthrough prompted by Weibao's P-20260908-04 audit
request, 2026-09-08. No additional user quotation is claimed.
**Status:** Reproduced, repair in progress
**Owner:** `surfaces/daemon.py`, lesson context and course-back navigation

**Observation:** Keyboard/browser navigation from the synthetic Unit 3 lesson
via its Courses link opened `/` with title Your desk. The shared application
Courses link points to `/courses`. The same stale destination exists in the
course overview, unknown-course recovery, and help back links.

**Diagnosis:** These links retain the old shelf-at-root route after the product
home split. Replace their destination with the existing `/courses` route. No
new route or runtime change is needed.

**Before-repair evidence:** The new fallback-navigation regression in
`tests/navigation_color_roundtrip.py` fails with actual `/`, expected `/courses`.
Browser observation confirms the misleading destination with course metadata
present as well. Repair verification must exercise the real destination.

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

## UI contrast audit transitions, 2026-09-08

### P-20260908-04 state transition

**Status:** Fixed and deterministically verified. Direct browser recheck
passed. Human accessibility and aesthetic acceptance remain owed.

**Repair:** `surfaces/presentation.py` now owns a paired selected background
and foreground and uses darker existing ink for inactive course links.
Selected text measures 10.91:1 instead of 1:1. Inactive labels no longer use
the failed 4.15:1 muted pair. Underline and `aria-current` remain explicit.

**Proof:** `python3 tests/navigation_color_roundtrip.py` passes 3 tests.
Browser checks passed 280 rendered selected-link states across seven looks,
four theme settings, two profiles and five interaction states. Native course
routes agree with their selected labels. At 390px, Enter opens the course menu,
links are 44px high and no horizontal overflow occurs. Emulated doubled text
also retains 390px scroll width. Focus, reduced motion and contrast preference
checks passed within the recorded scope. Physical touch, screen reader and
human zoom/aesthetic acceptance are not certified.

**Related test repair:** `tests/course_shell_roundtrip.py` counted the
application's current link as a course selection. It now requires exactly one
current Learn link in each course menu and passes. This does not weaken native
selection checks.

### P-20260908-05 state transition

**Status:** Fixed and deterministically verified. Direct browser recheck passed.

**Repair:** Four stale Courses/back destinations in `surfaces/daemon.py` now
point to `/courses`. The existing profile test's expected link was updated.
No route or scoring behavior changed.

**Proof:** The native lesson's Courses link now opens the Courses title and
course shelf. The no-metadata fallback test passes. Final course-shell,
presentation-profile, stylesheet and navigation checks pass. The daemon suite
passes 78 served checks after the route repair.

**Ownership and remaining work:** Detailed browser scope, changed paths,
competitor capability dispositions, full preflight failures and recovery are
in `research/competition-2026-09-08/ABSORPTION.md`, Native UI repair and
capability reconciliation. This repair does not close P-20260908-02/03,
source-reading R1-R3, or competitor prototype promotion gates. The original
8767 process was left running. A fresh 8768 audit process supplied repaired
browser evidence because a Python daemon retains already-imported code.
