# Projected product: what itembank becomes

**Status:** user-facing product projection; proposed behavior unless marked
**shipped**. This document makes the source-to-course contract tangible.

## The first screen: a course shelf

```text
My courses

EMT certification                         Continue: Airway scenarios
18 objectives supported · 3 thin · 2 unknown
Reason: recent practice exposed a positioning confusion

Calculus I                                Review course
Source changed · 2 proposals awaiting review

+ Create course
```

The shelf shows courses, not banks. It reports source and evidence states with
counts and reasons, not a fictional mastery dial. Selecting a course opens one
workspace: Overview, Learn, Practice, Test, Map, Sources, and Build/review.

## Creating a course

The user chooses a syllabus, book, folder, exam blueprint, notes, or existing
bank and grants explicit search roots. Discovery is read-only. The system shows
what it found, fingerprints and extraction status, ownership/privacy choices,
duplicates, conflicts, and unsupported formats. Nothing found is automatically
uploaded or changed.

Next it proposes a cited objective map:

```text
Unit 2 — Airway
  O2.1 Recognize inadequate ventilation       source pp. 88–94 · high confidence
  O2.2 Select positioning and adjunct          syllabus §3 + source pp. 95–103
  O2.3 Apply protocol in changing scenarios    thin support · review needed
```

The user approves or edits the target, hierarchy, prerequisites, and scope.
Only then does the system propose treatments and missing artifacts.

## How treatment is chosen

For each objective the course director asks: what is the cognitive demand, how
well does the source teach it, what prerequisite or misconception matters, and
what will count as useful evidence?

- A clear authoritative explanation stays a direct reading.
- Dense but important pages may become a cited excerpt plus key terms.
- A diffuse concept may need a guided lesson.
- A procedure may need a worked example with fading steps.
- A spatial or causal idea may need an accessible diagram or simulation.
- Durable recall may need retrieval practice.
- Performance under exam conditions may need a test.
- Ambiguous or conflicting material stays visible for human review.

One objective may combine a primary reading with an example and later practice.
“Do not generate” is a successful decision.

## AI proposals and bounded autonomy

Every proposal appears as a reviewable unit:

```text
Proposal: add worked example for O2.2
Why: source explains the rule but has no application example
Sources: EMT text pp. 98–101; syllabus §3.2
Generated synthesis: yes
Changes: +1 example, +2 practice items
Checks: format clean · citation review pending · accessibility passed
[Accept] [Edit] [Reject] [Ask why]
```

Recommend-only makes no drafts. Draft-and-review produces proposals. Approved
bounded writes can apply an exact reviewed proposal inside an allowed root.
Accepted changes retain citations, provenance, diff, and undo. AI never silently
publishes, invents scores, or sees/transmits a source merely because discovery
found it.

## Learning one objective

Learn is an ordered stream of purposeful activities, not a pile of cards:

```text
O2.2 Select positioning and adjunct

1 Read pp. 98–101             Original source · open beside lesson
2 Predict                     What changes when trauma is suspected?
3 Observe                     Accessible airway-position diagram
4 Explain                     Things to know · hover/focus definitions · expert tip
5 Complete                    Finish the partially worked scenario
6 Transfer                    New patient/context, same underlying decision
7 Choose next                 Continue · practice · revisit prerequisite · read ahead
```

The same accepted content supports continuous reader and guided modes. Terms
work on hover and keyboard focus. Things-to-know, warnings, citations, tips,
math, code, visuals, and examples are semantic roles with screen-reader and
static fallbacks. A learner can skip or read ahead; the system records what
happened without pretending that viewing means learning.

## Practice is not Test

Practice is formative: select a unit/objective/difficulty or accept a transparent
recommendation; use runtime-permitted hints, retries, explanations, and spaced
returns. The UI explains why an item was selected.

Test is an assessment sitting: diagnostic, unit, cumulative, or exam simulation.
The runtime controls timing, feedback mode, scoring, keyed disclosure, and
evidence. Prose remains pending review. A standardized-test course must show its
versioned blueprint and compare actual domain, construct, format, difficulty,
timing, and tool distribution. A knowledge course follows the real syllabus and
expected demand rather than imitating a generic test company.

## Evidence changes recommendations honestly

After activity, the course may say:

> In the last 14 days, 3 of 5 unassisted positioning items were correct; both
> misses involved suspected trauma. One prose response is pending and there is
> no delayed-retention sample. Suggested next action: one changed-context
> example, then a short retrieval set tomorrow.

It may say `recently successful`, `weak evidence`, `due for retrieval`, `at
risk`, `pending review`, or `unknown`. It does not claim a universal mastery
percentage. Recommendations show their window, denominator, missing signals,
assistance context, uncertainty, and learner override.

## Offline, local AI, and hosted AI

**Shipped:** parsing, lessons, bank validation, deterministic scoring, sessions,
evidence, and reports are local. **Proposed:** course files and accepted
artifacts remain readable locally; indexes are disposable; accepted lessons,
practice, tests, and reports open without a model.

A hosted coding-agent client can provide stronger extraction, synthesis,
vision, and review when the user permits source transmission. A registered
local backend uses the same operation contracts but declares its capabilities
and limitations. If it cannot perform citation review or vision extraction, the
operation says unsupported or requests review; it does not quietly lower the
quality bar. With AI off, the course remains useful and queued proposals simply
wait.

## One end-to-end journey

Weibao creates “NREMT Airway” from a syllabus, a current exam blueprint, and an
owned EMT textbook folder. Discovery finds the files locally. The proposed map
identifies twelve objectives, flags one blueprint objective with thin source
support, and retains six textbook sections as direct readings. Weibao approves
the map.

The director proposes key terms for two dense sections, one worked airway
example, an accessible positioning diagram, a short practice bank, and a timed
blueprint-aligned unit test. Every generated claim cites a source; the thin
objective remains a visible gap until another approved protocol document is
added. Weibao reviews the diffs and accepts all but one weak distractor set.

In Learn, the course opens the original pages beside a guided sequence. Weibao
predicts the response to a scenario, explores the diagram by mouse or keyboard,
completes a partially worked decision, and applies it to a changed trauma case.
Practice supplies a permitted hint after a wrong choice; Test later stays silent
until the sitting ends.

The evidence report does not announce mastery. It shows five relevant attempts,
hint context, one repeated misconception, no delayed sample, and a pending prose
mark. The director recommends revisiting the trauma exception and scheduling a
short unassisted set tomorrow. Weibao can accept, change, or ignore that path.
Later, when the source file changes, the course marks affected citations stale
and proposes bounded updates instead of regenerating the whole course.
