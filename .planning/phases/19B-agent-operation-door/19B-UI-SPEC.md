---
phase: 19B
slug: agent-operation-door
status: draft
shadcn_initialized: false
preset: none
created: 2026-09-06
---

# Phase 19B: Agent Operation Door UI Design Contract

> Visual and interaction contract for starting, reviewing, settling, auditing,
> and undoing agent proposals from the canonical course Agent tab. This file is
> additive to `.planning/UI-SPEC.md` and preserves the Phase 17A visual system.

## Scope and authority

The Agent tab is a client of the existing operation protocol. It may start one
bounded skill operation, display its durable state, present a stored proposal,
and ask the learner to accept, reject, or undo it. It never receives assessment
keys, settles marks, decides correctness, or writes model-provided bytes sent
back from the browser. Accept and reject identify a course-side proposal by its
opaque identity. Accept is the only action that may change accepted course
content, and it does so through exactly one applied `journal.commit_operation`
entry.

Proposed, accepted, rejected, conflicted, and undone records remain available
for later review. Settlement does not remove them. Future compaction is outside
this phase and must preserve identity, provenance, disposition, journal links,
review facts, and explanation.

## Design System

| Property | Value |
|----------|-------|
| Tool | none, stdlib Python with server-rendered HTML, shared CSS, and vanilla JavaScript |
| Preset | not applicable |
| Component library | none, use semantic HTML and `surfaces/presentation.py` primitives |
| Icon library | none, state meaning is always written as text; optional glyphs are decorative |
| Font | existing Paper, Ledger, Chrome, and Code voice tokens only |

No `components.json`, Tailwind configuration, PostCSS configuration, React,
Next.js, or Vite design-system seam is present. The shadcn initialization gate
does not apply. Do not add a component registry, npm dependency, new palette,
new font family, or Agent-specific theme.

## Information hierarchy

The existing Agent tab and course shell remain intact. Within the tab, render in
this order:

1. Page heading and one-sentence authority summary.
2. Current operation status and its next action.
3. Start section containing runnable skills and unavailable skills.
4. Review section containing the selected proposal, validation, citations,
   egress disclosure when applicable, and the diff.
5. Decision controls for the selected proposal.
6. Review history with disposition, evidence, journal link, and undo state.
7. Model, autonomy, spend, and open-ended console disclosures already present.

The current operation and the proposal awaiting review outrank provider and
spend metadata. Do not place history above an unsettled proposal. The framed
console remains the open-ended external path. The skill list is the itembank-
driven path. Keep the existing explanatory sentence distinguishing them.

## Spacing Scale

Use only the shipped scale.

| Token | Value | Usage |
|-------|-------|-------|
| `--space-1` | 4px | Inline status and code-marker gaps |
| `--space-2` | 8px | Compact metadata, chips, and button groups |
| `--space-3` | 16px | Card interiors and default control separation |
| `--space-4` | 24px | Proposal sections and stacked panel padding |
| `--space-5` | 32px | Major groups within the Agent tab |
| `--space-6` | 48px | Review and history section breaks |
| `--space-7` | 64px | Page-level spacing only |

Exceptions: none. Every button, disclosure summary, skill action, and history
action has a minimum 44px touch target. Diff line height and horizontal scroll
do not reduce the target floor.

## Typography

Only four UI sizes and two weights apply in this phase. `--text-lesson` is not
used because the Agent tab contains no sustained authored lesson prose.

| Role | Token | Size | Weight | Line Height | Voice |
|------|-------|------|--------|-------------|-------|
| Compact label | `--text-xs` | 12px | 600 | 1.4 | Ledger for durable state and identifiers; Chrome for control labels |
| Body | `--text-body` | 16px | 400 | 1.5 | Chrome for UI copy; generated text remains Chrome inside a labeled container |
| Section heading | `--text-heading` | 20px | 600 | 1.2 | Chrome |
| Page heading | `--text-display` | 32px | 600 | 1.1 | Chrome, once per page |

Use `--font-code` for diff bodies and exact fingerprints only. Use
`--font-ledger` for proposal ids, operation ids, journal entry ids, validation
outcomes, timestamps, and runtime assertions. The model receives no distinct
typographic voice. Do not introduce a third weight.

## Color

All values come from `surfaces/theme.py`. Every semantic state uses text and
structure in addition to color.

| Role | Value | Usage |
|------|-------|-------|
| Dominant, 60% | `--bg`, `--ink` | Page field and primary text |
| Secondary, 30% | `--card`, `--chip`, `--line`, `--mut` | Proposal cards, history, disclosures, metadata, borders |
| Accent, 10% | derived `--accent`, `--accent-soft` | Visible focus ring, selected Agent navigation, and the one current primary action |
| Pending | `--pending`, `--pending-bg` | Running, proposed, needs-input, and awaiting-review states, always with a written label |
| Warning | `--warn`, `--warn-bg` | Conflict, stale proposal, or recoverable attention, always with a written label |
| Unknown | `--unknown`, `--unknown-bg` | Neutral empty state and unavailable metadata that is not an error |
| Success | `--ok`, `--ok-bg` | Accepted and successfully undone dispositions, always with a written label |
| Destructive | `--bad`, `--bad-bg` | Reject confirmation only; never an error-state substitute |

Accent is reserved for the focus ring, selected Agent tab, `Start skill` when
nothing is active, `Accept proposal` while a valid proposal is selected, or
`Undo accepted change` on an accepted record. Only one of those actions is the
accent primary action in a rendered state. Reject uses the destructive token.
Unavailable, conflict, rejection, and model failure never borrow the accent.

## Component inventory

| Component | Contract |
|-----------|----------|
| Operation status | One persistent status region naming state, skill, target, updated time, and next action. Use `role="status"` with `aria-live="polite"`; reserve `role="alert"` for a newly surfaced blocking conflict or failed settlement. |
| Skill list | Native list. Runnable rows expose `Start {skill}`. Stub or unsupported rows show `Unavailable` and a reason instead of a dead button. One operation at a time. |
| Needs-input panel | Names the exact missing choice or authority and provides its one next action. It does not discard the durable operation. |
| Proposal summary | Shows opaque proposal id, skill, target path, object kind, expected base fingerprint, created time, backend, provenance, validation state, and disposition. |
| Source citation | Separates source-authored material from generated synthesis. Shows source label, locator, fingerprint or version, and uncertainty or disagreement where present. |
| Egress disclosure | For hosted work, lists the exact approved spans and destination before start. Unknown remote-process rights block start by name. Local work states that no remote egress is planned. |
| Diff review | Uses the shipped open `diff_review` form. The current bounded page is expanded by default. It includes base, current, and proposal context, line markers, withheld-line count, and `Show next changes` pagination. It never hides the portion being accepted behind a collapsed disclosure. |
| Decision group | Separate `Accept proposal` and `Reject proposal` controls in one named group. Accept requires confirmation. Reject requires confirmation and records no course-content write. |
| Review history | Durable list grouped by current state, then reverse chronological order. Every row shows disposition, actor, timestamp, target, validation, proposal id, and linked journal evidence where applicable. |
| Evidence disclosure | Summary first. Native disclosure shows operation id, interaction id, backend profile, authority and rights snapshot, expected and observed fingerprints, validation results, accepted journal entry, prior revision, and undo entry. No secret or assessment key appears. |
| Undo control | Present only for the latest accepted change that the existing journal says is undoable and not already undone. It is never inferred from proposal status alone. |

## State and interaction contract

| State | Required presentation | Available actions | Forbidden implication |
|-------|-----------------------|-------------------|-----------------------|
| Start | Heading `Start an agent operation`; show runnable skills, each target summary, local or hosted disclosure, and current autonomy. | `Start {skill}` | Starting does not authorize acceptance or imply that a change will occur. |
| Running | `Running {skill}. No course content has changed.` Show current checkpoint and elapsed time as static text. | `View operation details`; cancel only if the operation protocol already supports durable cancellation | No looping typing animation, fake progress percentage, or implied completion. |
| Pending | `Proposal pending review.` Show the stored proposal summary and validation state. | `Review proposal` | Pending is not accepted, published, scored, or evidence of mastery. |
| Needs input | `This operation needs your input before it can continue.` Name the missing choice or authority. | One specific continuation action, such as `Choose a source`, `Review rights`, or `Open settings` | Never turn missing authority into consent or abandon the durable record. |
| Unavailable | `Agent operation unavailable. {reason}` Follow with the named recovery action and `Your course, lessons, practice, scoring, and authored hints still work.` | One retry or configuration action when legal | No indefinite spinner, hidden reason, automatic retry, or disabled button without explanation. |
| Conflict | `The target changed after this proposal was created. Nothing was overwritten.` Show base fingerprint, current fingerprint, proposal target, and the available reconciliation paths. | `Review base, current, and proposal`; `Start a new proposal`; retain the conflicted record | No Accept button, silent rebase, automatic merge, or destructive overwrite. |
| Review diff | Heading `Review proposed change`; show target, citations, validation, exact changed lines, and truncation disclosure. | `Accept proposal`; `Reject proposal`; `Show next changes`; `Review evidence` | No acceptance from a summary-only view. No reposting draft bytes from the client. |
| Accept confirmation | `Accept this proposal? This writes one reviewed change to {target} and records a journal entry you can undo.` | Primary `Accept proposal`; secondary `Keep reviewing` | Confirmation never claims accessibility certification or source truth beyond recorded validation. |
| Reject confirmation | `Reject this proposal? The decision will remain in review history. Accepted course content will not change.` | Destructive `Reject proposal`; secondary `Keep reviewing` | Reject is not undo, conflict, cancel, or backend failure. |
| Accepted | `Proposal accepted. One journaled change was applied.` Show journal entry id, accepted revision, prior revision, actor, and verification result. | `Undo accepted change`; `Review evidence` | Accepted does not mean model-authored content scored or approved itself. |
| Rejected | `Proposal rejected. No accepted course content changed.` Show reviewer, time, and reason when supplied. | `Review proposal`; `Start a new proposal` | Do not delete or hide the proposal. |
| Undone | `Accepted change undone. The previous valid bytes were restored and the reversal was recorded.` Show original accepted entry and undo entry. | `Review evidence`; `Start a new proposal` | Undo is a recorded forward recovery action, not deletion of history. |
| Empty | Heading `No agent operations yet`; body `Start a skill to create a reviewable proposal. Nothing changes until you accept it.` | `Start a skill`; if no backend is active, `Open model settings` | Never show a blank panel, generic `Nothing here`, or a disabled unexplained control. |

`report_only` keeps proposal creation and review available but removes the
accept control from the actionable decision group. In its place render:
`Accept is unavailable because auditor_autonomy is report_only. Change it in
Settings, Agent autonomy, if you want reviewed proposals to become revisions.`
Reject remains available.

Repeated Accept, Reject, and Undo submissions return the already-settled state
without a second write. The UI disables the submitted control only while the
request is in flight. It then renders the durable server response rather than
optimistically inventing a disposition.

## Focus, keyboard, touch, and screen-reader contract

The DOM and focus order are: Agent heading, current status, start controls,
proposal heading, citations and validation, diff, decision controls, evidence,
history, then secondary model and console disclosures. Hidden or collapsed
secondary information does not precede the active proposal in focus order.

- Starting a skill moves focus to the operation-status heading after the server
  confirms the durable operation id. Status changes are announced once through
  the single polite live region.
- Opening a proposal moves focus to `Review proposed change`, not directly to
  Accept. Diff lines remain selectable text inside a labeled scroll region.
- Opening Accept or Reject confirmation moves focus to the confirmation heading,
  traps focus only while the native or accessible modal is open, closes on
  Escape without settling, and returns focus to the invoking control.
- After settlement, move focus to the accepted, rejected, conflicted, or undone
  status heading. On validation failure, focus the error summary and link each
  finding to the relevant review section.
- Every action is reachable by Tab and activated by Enter or Space. Diff paging,
  history disclosure, and evidence disclosure use native buttons or `details`.
  No action depends on hover, drag, long press, color, or pointer precision.

All controls have visible focus at 3:1 or better and 44px targets. Adjacent
Accept and Reject targets retain at least `--space-2` separation. Screen-reader
names include action plus object, for example `Accept proposal p_…` and `Undo
accepted change for lesson.md`. Do not announce the whole diff on every status
change. The diff region has a concise accessible name and its own reading order.

## Responsive and mobile disclosure

At 1024px and wider, the proposal review may use two columns: proposal metadata
and evidence in the secondary column, with the diff and decision group primary.
DOM order remains the linear order specified above.

From 768px through 1023px, use one column. Evidence, model configuration, spend,
and review-history detail become in-flow native disclosures after the decision
group. The selected proposal summary and diff remain open.

Below 768px and at 400% zoom, use one column with no horizontal page scroll.
Code diff lines may scroll inside their labeled region. Each line preserves its
add, remove, or context text marker. Accept and Reject stack full width. A
compact sticky decision bar is allowed only when it duplicates no controls and
does not cover content or status. Dense review may say `Reviewing long diffs is
easier on a larger screen`, but every operation remains completable on mobile.

## Motion and loading

Functional transitions are at most 150ms. Running uses static text and may show
a non-animated elapsed time. There is no typing animation, looping shimmer,
autoplay, celebratory effect, or progress estimate without measured progress.
Under `prefers-reduced-motion: reduce`, remove all animation and transition.
State changes remain visible through text, borders, and placement.

## Static and degraded fallback

The server-rendered page is a useful static record before JavaScript runs. It
shows the current durable state, proposal summary, citations, validation, diff,
disposition, evidence ids, and exact CLI twin for the next legal action. Forms
remain normal POST forms where the existing route pattern permits. If client
enhancement fails, the page reloads to the server-confirmed state.

If the Agent backend is offline, the Agent tab remains readable and review
history remains inspectable. Existing lessons, practice, scoring, authored
hints, reports, and accepted course content continue working. A static build,
which cannot execute a local operation, renders the status `Agent operations
require the local itembank server` and the exact local start command. It never
renders an enabled action that cannot work.

## Evidence and undo affordances

Every visible state maps to one durable proposal or operation identity. The
default row shows only the state, action, target, actor, and time. `Review
evidence` exposes:

- proposal id, operation id, interaction id, and skill id;
- backend profile, local or hosted status, exact egress manifest, and rights
  decision when applicable;
- target path, object kind, expected base fingerprint, current fingerprint at
  settlement, citations, and validation results;
- disposition, reviewer, decision time, applied journal entry id, accepted
  revision, and prior revision;
- undo entry id, restored revision, byte-equivalence verification, and time.

The accepted row exposes `Undo accepted change` beside `Review evidence`.
Confirmation copy is: `Undo this accepted change? This restores the previous
valid bytes and records the reversal. The proposal and both journal entries will
remain in review history.` Confirmation action: `Undo accepted change`.

After undo, show both ids and the result `Previous valid bytes restored` only
when verification succeeds. If verification fails, show `Undo could not be
verified. The last accepted state was preserved.` followed by one named recovery
action. Never report restoration based only on an HTTP success status.

## Copywriting Contract

| Element | Exact copy |
|---------|------------|
| Primary start CTA | `Start {skill}` |
| Pending CTA | `Review proposal` |
| Review heading | `Review proposed change` |
| Accept CTA | `Accept proposal` |
| Reject CTA | `Reject proposal` |
| Undo CTA | `Undo accepted change` |
| Evidence CTA | `Review evidence` |
| Empty heading | `No agent operations yet` |
| Empty body | `Start a skill to create a reviewable proposal. Nothing changes until you accept it.` |
| No active backend | `Agent operation unavailable. No model backend is active. Choose one in Settings, Model. Your course, lessons, practice, scoring, and authored hints still work.` |
| Conflict | `The target changed after this proposal was created. Nothing was overwritten.` |
| Accepted | `Proposal accepted. One journaled change was applied.` |
| Rejected | `Proposal rejected. No accepted course content changed.` |
| Undone | `Accepted change undone. The previous valid bytes were restored and the reversal was recorded.` |
| Accept confirmation | `Accept this proposal? This writes one reviewed change to {target} and records a journal entry you can undo.` |
| Reject confirmation | `Reject this proposal? The decision will remain in review history. Accepted course content will not change.` |
| Undo confirmation | `Undo this accepted change? This restores the previous valid bytes and records the reversal. The proposal and both journal entries will remain in review history.` |

Adapter-specific next actions already defined by
`surfaces/agent_operation.py::NEXT_ACTIONS` remain canonical. Render the typed
code with that exact next-action copy. A new adapter code without copy is a
contract failure, not a generic fallback.

## Required state fixtures and verification

The Phase 19B gate must render and exercise start, running, pending,
needs-input, unavailable for every typed adapter family, conflict, long diff,
accept confirmation, reject confirmation, accepted, rejected, undone, empty,
and `report_only`. Include one long target name, long citation, more than one
diff page, and a backend loss after a durable proposal already exists.

Verification must cover desktop at 1280px, narrow at 375px, 400% zoom and
reflow, keyboard-only operation, touch targets, scripted screen-reader names and
announcements, high contrast, reduced motion, and JavaScript-disabled fallback.
The deterministic route and CLI fixtures must prove that each surface accepts
one proposal as one applied journal entry, rejects without changing accepted
bytes, conflicts without overwrite, and undoes to byte-identical prior content.
A human screen-reader and visual review remains an owed leg. No agent may mark
that human leg complete.

## Registry Safety

| Registry | Blocks Used | Safety Gate |
|----------|-------------|-------------|
| none | none | not applicable, the project uses no registry or third-party UI blocks |

## Checker Sign-Off

- [ ] Dimension 1 Copywriting: PASS
- [ ] Dimension 2 Visuals: PASS
- [ ] Dimension 3 Color: PASS
- [ ] Dimension 4 Typography: PASS
- [ ] Dimension 5 Spacing: PASS
- [ ] Dimension 6 Registry Safety: PASS

**Approval:** pending
