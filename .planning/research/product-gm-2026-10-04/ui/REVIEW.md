# U1-U3 independent delta review

Reviewed the frozen presentation delta against the preserved `before/base`
lesson and reader files, `REPORT.md` and `lesson-worker.md` (the requested
`worker.md` does not exist). Large modules were sampled symbol-first. No
production, test, shared planning, Git, provider or learner-data writes were
performed. This review does not certify human accessibility or release status.

## F1: P2, failed selection help loses keyboard focus, resolved

File/symbol: `surfaces/reading_desk.py`, `VIEW_SCRIPT`, the new unconditional
`reading-help-selection` click listener (line 131), together with the existing
`surfaces/context_help.py` `helpSelect` validation.

Reproduction: open Reading tools, focus Ask about selection without selecting
source words, and press Enter. The new listener closes the details before
`helpSelect` refuses the missing selection. Unlike the successful help path,
the refusal never moves focus. A focused native Chrome reproduction using the
exact extracted listener and validation function verified `open=false`, focus
on the document body, and the next Tab landing on a later control, skipping the
Reading tools summary. The status asks the learner to retry a control whose
panel has just disappeared. The same refusal exists for unavailable content.

This is introduced by U3: the baseline kept this button outside Reading tools
and did not close any disclosure on a refused selection. Close tools only after
successful help selection, or restore summary focus on refusal. Preserve the
existing successful focus transfer to the help question and ensure the refusal
does not lose the learner's passage selection or draft.

Resolution: parent removed the unconditional listener. The visible repair leaves
`context_help.helpSelect` responsible for validation and focus. A second exact
function Chrome reproduction verified that invalid keyboard activation now
keeps tools open and focus on `reading-help-selection`, with the same useful
retry status. Existing Escape and source/note dismissal listeners remain.
No outstanding finding remains from this scoped review.

## Other reviewed paths

No additional concrete introduced defects found in compact lesson orientation,
visible-heading outline filtering, escaped public-stem previews, matching-bank
context navigation, exact sitting return semantics, Escape handling, source or
note focus transfers, or note/save behavior. The inherited context header trusts
caller-provided hrefs; the added practice path further requires a local
matching-bank URL and escapes its output. No new key, rationale, score, provider
egress or durable save path was found in this delta.

Verification was a focused disposable Chrome DOM reproduction only. No broad
suite was run, and the parent's reported viewport/journey results were treated
as supplied evidence rather than independently repeated.
