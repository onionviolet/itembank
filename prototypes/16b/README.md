# prototypes/16b

Development-only. Nothing here is imported by a shipped module, registers a
route, holds a key, scores anything, or reaches session state. The whole
directory is deletable.

## What this is

A mockup of the course shelf that plan **16B-04** will build, drawn against
that plan's copy contract and the tokens in `surfaces/theme.py`. It exists so
the surface can be looked at and argued about several phases before it can be
written.

Phase 16B has not started. Its precondition check halts on Phase 16A: see
`.planning/phases/16B-ia-modes-recovery-contract/16B-PRECONDITION-DRYRUN-2026-08-27.md`.

## Files

- `build_shelf_mockup.py` builds `fixtures/corpus_14b.py`'s three synthetic
  domains into a temp directory, reads them back through `course.read_course`,
  and renders the cards from real `graph.py` records.
- `shelf_template.html` is the page shell with `@@TOKEN@@` placeholders.
- `course-shelf.html` is the generated output, committed so it can be opened
  without running anything.

## Regenerate

```
python prototypes/16b/build_shelf_mockup.py > prototypes/16b/course-shelf.html
```

Byte-identical between runs except for the three course object IDs, which
`identity.new_object_id()` mints fresh each build. Those lines are the only
expected diff. Anything else moving means a shipped record shape changed, which
makes this a cheap canary on `graph.py` and `course.py`.

## What is real and what is not

**Read from shipped code:** course titles, course object IDs, container counts
and their free-text labels (including the corpus's deliberate `fortnight`),
objective counts, edge counts, source counts, and the journal object state and
revision.

**Illustration, marked with an `i` on the card:** the attention state, the
resume cue, and the last-activity date. None can be sourced today, and that is
the mockup's most useful output rather than a shortcut:

- `course_shelf_state` belongs to plan 16B-04 and does not exist.
- A resume cue needs evidence, and `course.py` imports no `evidence` by design,
  so the sidecar structurally cannot answer it. Whatever computes the cue will
  be a third thing reading both.
- Nothing in `graph.py` holds a date, which is the open half of
  `IDEA-LEDGER.md` IL-20260826-07 and the reason `due` has no source.

So the structural half of the shelf is fully backed by shipped code today, and
the attention-and-resume half, which is what makes a shelf worth looking at, has
no data behind it yet.

## Contract check

The page runs 16B-04's own percent-character assertion against its own DOM:
no shelf card, chip, or resume cue may contain a percent character, and no
single aggregate completion, mastery, or readiness score may appear. That
prohibition carries `status: kept` in the plan.
