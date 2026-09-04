---
name: user-vision
description: >
  Capture a user's product vision in their exact words, interpret it in a
  visibly separate layer, give every idea a durable disposition instead of
  deleting it, and drift-audit a planning pass before it closes. Use when
  starting or steering a project from rough ideaboarding, when a later idea
  changes an earlier direction, when deciding what belongs in a vision record
  versus a research or planning file, or when an agent must continue a project
  without flattening the user's intent. Portable across projects and agent
  clients (Claude Code, Codex, local agents).
---

# User Vision: capture, disposition, drift-audit

This skill preserves a user's product vision so a capable agent can continue a
project without flattening intent, repeating research, silently dropping ideas,
or turning provisional findings into commitments. It is subject-neutral. It
governs a records process, not any specific product's runtime.

It has three jobs, done in order and repeated as the project evolves:

1. **Capture** the user's meaning in their own words, with interpretation kept
   visibly separate from the quotation.
2. **Disposition** every substantial idea into a durable route rather than
   reducing the set for neatness.
3. **Drift-audit** a planning or direction pass before closing it, so the record
   stays honest about what is user intent, what is inference, and what is a
   commitment.

## Deference: the host project wins

This skill describes a records process. It never outranks the project it is
installed into. When this skill and the host project's own contract, workflow,
or planning directives disagree, **the project's files win** and this skill is
the generic fallback. Name that file at install time, here:

> Host contract for this installation: `.planning/AGENT-WORKFLOW.md` sections 2, 5 and 10, under `.planning/SOURCE-TO-COURSE.md` and `.claude/skills/OPERATION-CONTRACT.md`. Those win on any disagreement. The live records are `.planning/USER-VISION.md`, `.planning/USER-VISION-INBOX.md` and `.planning/IDEA-LEDGER.md`; the templates here are not to be copied over them, and the audit is `python3 scripts/vision_audit.py`.

If the host already runs an equivalent process under different file names, do
not create a second copy. Adopt the existing files and treat the templates below
as a description of what those files should contain. Two ledgers with the same
purpose is the failure this skill is supposed to prevent, not a clean install.

## When to use this

- A project is starting from rough, contradictory, or exploratory ideaboarding.
- A new statement seems to change an earlier direction and both must survive.
- You are deciding what belongs in the authoritative vision versus a research or
  planning file.
- Another agent (or a future you) must pick up the project cold.
- You are about to write requirements and want to preserve breadth without
  shipping everything at once.

## Core rule: three separate layers

Keep these three visibly distinct at all times. Collapsing them is the failure
this skill exists to prevent.

| Layer | What it holds | Editing rule |
|-------|---------------|--------------|
| **Quotation** | The user's exact words | Never rewritten. Never silently corrected. Append-only, dated. |
| **Interpretation** | What the words mean for the product | Dated. Sits below the quote. Superseded, never overwritten. |
| **Decision** | The commitment a contract or plan settled | Lives in the owning contract/requirements/plan file, linked back. |

A summary is never allowed to stand in for the user's words. When the layers
appear to conflict, reread the quotation, record the conflict, trace each
statement to its origin, and resolve it in the owning document. Do not default
to the most recent summary.

## 1. Capture

Every meaningful user statement first enters the capture funnel
(`templates/USER-VISION-INBOX.md`), verbatim. Then decide its route:

- **Promote** to the authoritative vision (`templates/USER-VISION.md`) only
  statements about outcomes, experience, scope, values, boundaries, users,
  success, or unresolved product direction.
- **Route** implementation guesses, tool choices, links, task mechanics, and
  research leads to their owning research or planning file. Keep the verbatim
  copy in the inbox with a link.
- **Split** a mixed statement: promote the product-intent clauses, route the
  implementation clauses.
- **Hold** anything whose meaning is not yet stable.
- **Duplicate**: link to the earlier statement it restates without adding a
  second authoritative copy.

**Entry headings must be machine-readable, because something will parse them.**
Use `### YYYY-MM-DD: title`, with a colon, a hyphen, or a dash as the separator,
and keep one format for the whole file. A comma after the date reads fine to a
human and defeats a date-anchored regex, which means the entry silently drops
out of every audit that walks the file. Pick the separator the host project's
existing entries already use before adding the first new one.

Preserve the wording even when it is rough, misspelled, or self-contradictory.
Do not require a statement to be rewritten as a requirement before recording it.

When you promote a statement, attach a dated interpretation note directly below
the quotation using the five fields in `references/interpretation-protocol.md`:
Status, Current interpretation, Open questions, Planning effect, Relationship to
earlier entries. Read that file before writing any interpretation.

## 2. Disposition

Coalescing a project into one coherent product does not mean deleting ideas for
minimalism. Every substantial proposal receives exactly one disposition and is
recorded in the project's idea ledger. **If the project already keeps one, under
any name, use it.** The template here is a shape to check an existing ledger
against, not a file to add beside it. The seven dispositions and their
required fields are defined in `references/disposition-vocabulary.md`; read it
before assigning one.

The dispositions are: **Core, Registered, Prototype, Backburner, Deferred,
Superseded, Rejected.**

Two rules bind hardest:

- **Simplicity alone is never a rejection reason.** A viable idea that does not
  fit now becomes Backburner or Deferred with a revisit trigger, not a deletion.
- **The rejection ledger is append-only.** A rejected idea keeps its original
  proposal, origin, evidence considered, exact reason, conflicting rule,
  retained alternatives, date, and reconsideration condition. It is never
  silently removed.

## 3. Drift-audit

Before closing a planning or product-direction pass, run the checklist in
`references/drift-audit.md`. It verifies that statements were captured or
deliberately routed, that interpretation stayed separate from quotation, that
research conclusions did not silently become commitments, that every viable idea
has a disposition, and that rejections carry evidence and a reconsideration
condition. A pass does not close until the audit passes or its failures are
recorded as open items.

**Items 8 and 9 of that checklist are placeholders and must be filled at install
time**, with the host project's own invariants and style rules. An unfilled
placeholder makes the audit weaker than whatever the project was already doing,
which is a regression disguised as adoption. If the project has its own drift
audit, keep the project's items and use this file only to check for gaps.

## Files in this skill

- `templates/USER-VISION.md`: the authoritative, verbatim-plus-interpretation
  record. Adopt the project's equivalent if one exists; copy this only if none does.
- `templates/USER-VISION-INBOX.md`: the capture funnel for rough ideaboarding.
- `templates/DISPOSITION-LEDGER.md`: the durable route for every idea.
- `references/interpretation-protocol.md`: the five-field interpretation note
  and the rule for changing an interpretation without erasing the old one.
- `references/disposition-vocabulary.md`: the seven dispositions and their
  required fields.
- `references/drift-audit.md`: the closing checklist for a planning pass.

## Installing into a project

Drop this directory into a project's skills path (for Claude Code:
`.claude/skills/user-vision/`). If the project mirrors its skills across agent
clients, install into every mirrored tree, or its byte-identical mirror check
will fail.

**Then inventory before you copy anything.** Look for a vision record, a capture
funnel, and an idea ledger that already exist under other names. Adopt what is
there. Copy a template into the project's planning directory only for a record
the project does not already keep, and never over a file that has content: the
templates are empty scaffolds and would destroy a live record. Fill in the host
contract path above, the drift-audit placeholders, and the field names the
project's own tooling greps for. The `references/` files stay in the skill and
are read on demand.

**Then regenerate whatever the host derives from its skill tree, and run the
host's own checks.** Installing a skill is not always purely additive: a project
may ship a generated manifest, index, or capability file that enumerates its
skills, and adding a directory makes that artifact stale and its test fail. Look
for a generator before assuming a copy is the whole install.

## Adapting per project

This skill carries no product-specific rules. A project layers its own
non-negotiables (its runtime invariants, authority boundaries, house style)
on top, in its own contract file, and links them from the vision record's
interpretation pointers. Keep the process generic here; keep the product rules
in the project.

## Status

Version 0.2, 2026-09-04. The capture and interpretation protocol is stable. The
disposition and conflict-resolution rules are still expected to change once a
project stress-tests a real "a later idea changed an earlier direction"
resolution end to end. Treat the API as pre-1.0.

**What 0.2 changed, and why.** v0.1 was extracted from one project and then
installed back into it, which surfaced five faults that are invisible from
inside the project a skill came from: no deference rule, so nothing said which
copy wins; a ledger template that duplicated an 82KB ledger already running the
same seven dispositions; an interpretation field named differently from the
record it was extracted from, so a grep for it found nothing; a template entry
heading whose comma separator the host's audit script could not parse; and a
drift audit whose two project-specific slots shipped empty, making it weaker
than the audit it replaced. Running the host's full preflight then found a sixth
that no amount of reading would have shown: the host generates a capability
manifest from its skill directories, so the install broke one of its tests until
that manifest was regenerated. All six are addressed above. **The pattern behind
them: a generic skill fails at the seams where it meets a project that already
has a process, not in its own body text.**
