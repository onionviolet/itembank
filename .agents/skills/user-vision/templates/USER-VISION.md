# User vision, verbatim and additive

**Owner:** <name>
**Status:** authoritative intent record
**Editing rule:** preserve entries verbatim. Do not silently correct spelling,
grammar, emphasis, or ambiguity. Add new dated entries instead of rewriting old
ones. A dated interpretation note may follow an entry, but it must stay visibly
separate from the quotation and point to any binding decision in the project's
contract, requirements, or plan files.

This file exists so the program's goal stays available in the user's own words
next to the team's interpretation. When the two appear to conflict, reread this
file, record the interpretation explicitly, and resolve the difference rather
than treating a prior summary as the user's intent.

## Verbatim goal statements

Add each statement below as its own dated section. Keep the exact words.

Keep the heading format stable: a date, one separator, a title. A colon, hyphen,
or dash all parse; a comma does not, and an entry a script cannot see is an
entry no audit covers.

### YYYY-MM-DD: title

> Add the user's exact words here. They may be short, rough, contradictory,
> exploratory, or a question. Do not rewrite them.

#### Interpretation recorded YYYY-MM-DD

**Status:** active | exploratory | partly superseded | superseded | resolved.

**Current interpretation:** the smallest faithful statement of meaning.

**Open questions:** ambiguities that research or later ideaboarding must test.

**Planning effect:** which documents, requirements, or phases this affects.

**Relationship to earlier entries:** confirms, extends, narrows, conflicts with,
or supersedes named earlier statements.

## Interpretation protocol

An interpretation may appear immediately after a verbatim entry when it helps
the user inspect how rough ideaboarding became product direction. Use a dated
subheading and keep the five fields above explicit.

Never edit the quotation when interpretation changes. Add a new dated
interpretation note, mark the older interpretation's status, and link both to
the decision that resolved the change. Later statements do not silently erase
earlier ones. A conflict stays visible until a dated resolution explains what
changed and why.

## Interpretation pointers

List the files that interpret, but do not replace, the statements above. For
example: the product contract, the milestone context, the testable
requirements, the phased roadmap, the experience spec, and the standing rules
for planning agents.

- `<contract file>`: current product contract and boundaries.
- `<requirements file>`: testable obligations.
- `<roadmap file>`: phased delivery.

## What this vision is building into

The verbatim entries above feed a visible chain:

1. The inbox captures meaningful rough ideaboarding.
2. This file preserves promoted product intent and dated interpretations.
3. The product contract states the current binding direction.
4. Research files test open questions and competing possibilities.
5. Requirements, roadmap, and experience specs turn accepted conclusions into
   obligations, sequence, and experience contracts.
6. Phase plans implement bounded work and check shipped behavior against the
   original intent.

This chain is traceable in both directions. A plan should identify the vision
and research behind it. A vision entry should identify its current planning
effect without pretending that an unresolved idea is already a requirement.
