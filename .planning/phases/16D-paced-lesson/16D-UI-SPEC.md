# 16D UI spec: the paced lesson view

Scope: the learner-facing experience contract for `mode="paced"` on the one
lesson renderer. Inherits every gate in `.planning/UI-SPEC.md` section 8 and
every 16A/16B component contract; nothing here mints a token, a color, or a
new primitive (17A owns those). No em dashes anywhere in rendered copy.

## Information architecture

- Route: the existing `GET /lesson/<stem>` with `?view=paced` and
  `&step=<id>`. No query renders the continuous document exactly as today.
  An unknown step id renders step 1 with a polite `role=status` line:
  "That step is not in this lesson any more. Showing the first step."
- The paced view shows exactly one step's already-rendered blocks (the
  guided-mode grouping rule: group, never re-render; containers stay
  byte-identical to continuous mode).
- Chrome, top to bottom: the shared context line; the lesson `h1`; a step
  header line "Step {n} of {total}: {first heading in step, or the lesson
  title for a headingless step}"; the step body; the checkpoint band when
  the step carries one; the pager.

## Table of contents

- A native `<details>` disclosure labelled "Steps", open by default at
  desktop width, containing one link per step: "{n}. {step heading or first
  words}". Every link always works (jump, never gate), including forward
  past an unattempted gate. Visited steps get the standard visited link
  treatment plus the text suffix "(seen)"; no color-only state.

## Pager and gating

- Two controls: "Back" and "Continue". Back always enabled. On a step whose
  checkpoint is a declared gate and unattempted, the Continue control is
  replaced by the exact sentence "Attempt the checkpoint above to continue,
  or use the Steps list to jump ahead." rendered as text beside a live
  Steps link, because a disabled button with no reason is forbidden
  (UI-SPEC section 8 rule 9) and the TOC must remain a jump.
- After any attempt (right, wrong, or skip via the band's ordinary skip
  control), Continue is an ordinary link. Gate on attempted, never correct.
- No timer anywhere. Advancing is the learner's click.

## Checkpoint band and tier disclosure

- The band is the shipped Phase 6.2 gate band, unchanged in structure:
  check first in DOM order, skip second, no JavaScript required.
- Wrong answer, first attempt (tier 1 and 2, teaching context only): the
  band re-renders held, with the learner's own selections annotated:
  each selected option gains the text chip "right" or "not right", never
  color alone, and beneath them the authored `DA:` rationale for exactly
  the options the learner touched, under the heading "About what you
  picked". Unselected correct options are not revealed or hinted.
- Second wrong attempt, or the learner control "Show the answer" (an
  ordinary button, present from the first wrong attempt): the full key and
  why, through the existing reveal rendering.
- In diagnostic or exam sittings nothing here applies; those modes are
  untouched and stay silent. The tier state is the runtime's; the page only
  renders what the payload it was handed contains.

## Resume

- Opening `?view=paced` with an existing lesson-run session for this lesson
  resumes at the recorded step id, with the polite status line "Resuming at
  step {n}." If the recorded id no longer exists (the lesson was edited),
  fall back to step 1 with the not-in-this-lesson line above; never guess a
  neighbouring step.
- Position is presentation state: no view, screen, or export may count it
  as coverage, mastery, or progress. Steps that emit no evidence are
  labelled "This step records nothing." in the step header's Ledger line
  when the lesson carries any checkpoint at all.

## States (16A/16B state matrix applies)

- zero steps cannot occur (rung 3 makes the whole document one step).
- runtime unreachable: the band's shipped 12.1 degrade line; reading
  continues; Continue is never gated when the runtime cannot record an
  attempt (a gate that cannot be satisfied must not hold).
- offline static build: the paced query renders the continuous document
  with the one-line notice "Paced view needs a served session. This is the
  whole lesson." Checkpoints refuse exactly as the static build already
  refuses served-only items.

## Accessibility specifics

- The step change is announced once via the existing `role=status` region:
  "Step {n} of {total}." Focus stays on the activated control; no focus
  jump on navigation.
- The whole flow is keyboard operable: TOC links, pager links, band
  controls. 44px targets per the 17A-04 rule. Reduced motion: no
  transition on step change.
- Screen readers receive the same step text, the same band, the same tier
  content, and nothing more (no key material in hidden text at tiers 0-2).
