# Drift audit

Run this before closing a planning or product-direction pass. Its job is to
catch the record drifting away from the user's actual intent: a summary standing
in for the words, a research guess hardening into a commitment, a viable idea
quietly dropped. A pass does not close until this audit passes or its failures
are written down as open items.

## Checklist

1. **Capture:** every meaningful user statement from this pass was captured
   verbatim or deliberately routed to its owning file. None was paraphrased away.
2. **Separation:** interpretations stay visibly separate from quotations. No
   quotation was edited to match a new reading.
3. **No silent commitments:** research conclusions did not become product
   commitments without a recorded decision. A finding is still a finding until a
   contract or plan accepts it.
4. **Every idea routed:** every viable idea has one durable disposition. Nothing
   substantial is sitting undecided or silently dropped.
5. **Rejections are honest:** each rejection carries evidence, the conflicting
   rule, retained alternatives, and a reconsideration condition. None was removed.
6. **Conflicts stay visible:** where a later statement changed an earlier one,
   both survive, the older interpretation is marked, and a dated resolution links
   them.
7. **Instructions match the contract:** agent-facing instructions match the
   binding product contract. No instruction file contradicts the accepted
   direction.
8. **Product invariants intact:** no plan from this pass weakens a named
   non-negotiable the project declared (its authority boundaries, safety gates,
   or quality promises). Fill in the project's specific invariants here.
9. **House style:** the pass respects the project's own prose and formatting
   rules in generated text.

## What a failed item means

A failed item is not a blocker by itself. It becomes an explicit open item with
an owner and a next action, recorded in the owning file, so the next agent sees
it. The failure this audit exists to prevent is the silent kind: drift that no
one wrote down and no one can later trace.

## Adapting per project

Items 8 and 9 are placeholders for project-specific rules. A project fills them
with its own invariants and style rules and links them from the vision record's
interpretation pointers. The other seven items are generic and apply to any
project using this skill.

**Fill them at install time, not later.** An unfilled placeholder silently drops
whatever the project was already checking. Real examples worth stealing, from
the project this skill was extracted from: mirrored skill trees stay
byte-identical, no plan weakens the one-parser and one-evidence-store boundary,
and no em dash characters appear outside verbatim quotations. Add an item for
any check the project's own tooling can run, and name the command next to it, so
the audit says what to type rather than what to remember.
