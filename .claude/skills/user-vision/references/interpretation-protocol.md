# Interpretation protocol

An interpretation records how a rough, verbatim statement became product
direction. It never replaces the words. It sits below the quotation, dated, so
the user can inspect the reasoning and challenge it later.

## The five fields

Write every interpretation note with these fields, in this order:

- **Status:** one of active, exploratory, partly superseded, superseded, or
  resolved. This is the state of the interpretation, not of the work.
- **Current interpretation:** the smallest faithful statement of what the words
  mean for the product. Do not add scope the user did not imply. Do not drop
  scope the user did imply.
- **Open questions:** the ambiguities that research, a prototype, or later
  ideaboarding must test before this becomes a commitment. Name what would
  resolve each one.
- **Planning effect:** the concrete documents, requirements, or phases this
  changes. If it changes nothing yet, say so.
- **Relationship to earlier entries:** whether it confirms, extends, narrows,
  conflicts with, or supersedes named earlier statements. Name them.

**Write the field labels exactly, and pick one spelling per project.** Tooling
greps for these strings, so "Relationship to prior entries" and "Relationship to
earlier entries" are two different fields to a script even though they read as
one to a person. If the host project already uses a spelling, match it rather
than importing this one. **This is the field most often skipped**, and it is the
one that makes supersession inspectable, so an audit that counts it is worth
more than an audit that counts the other four.

## Separating the three layers

- The **quotation** is the user's exact words. Append-only. Never corrected.
- The **interpretation** is your reading of them. Dated. Superseded, not edited.
- The **decision** is the commitment a contract or plan settled. It lives in the
  owning file and links back to the quotation and interpretation that produced
  it.

Keep them visibly distinct on the page. A reader must be able to tell, at a
glance, which text is the user speaking, which is you interpreting, and which is
a settled obligation.

## Changing an interpretation

When later ideaboarding changes an earlier direction:

1. Do not edit the old quotation.
2. Do not overwrite the old interpretation.
3. Add a new dated interpretation note below the relevant quotation.
4. Set the old interpretation's Status to partly superseded or superseded.
5. In the new note's Relationship field, name the earlier entry and state what
   changed.
6. Link the decision (in the contract, requirements, or plan) that resolved the
   change.

A conflict between two statements stays visible until a dated resolution
explains what changed and why. Do not resolve a conflict by deleting the losing
side. The losing side stays, marked, with a pointer to the resolution.

## Common failures this prevents

- A summary quietly replacing the user's words, so the original intent is lost.
- A recent statement silently overriding an earlier one without a recorded
  reason.
- An interpretation hardening into a requirement while its open questions are
  still unanswered.
- Scope creep or scope loss hidden inside a paraphrase.
