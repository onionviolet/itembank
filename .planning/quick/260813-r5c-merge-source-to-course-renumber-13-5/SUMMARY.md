---
task_id: 260813-r5c
slug: merge-source-to-course-renumber-13-5
created: 2026-08-13
completed: 2026-08-13
mode: quick
status: complete
commits:
  - 74db047 docs(quick-260813-r5c): plan
  - 485ecd2 merge(source-to-course): take the reframe and renumber phase 14 to 13.5
---

# Summary: the source-to-course merge and the 13.5 renumber

## What was wrong

Two branches authored a phase numbered 14 on the same day, and they were
different phases. Local `main` had Reading & Teaching Surface Quality Pass with
three of eight plans executed across 22 commits; `origin/main` had Course
Workspace & Source Binding with 15 commits of reframe documents and phase-16
research.

The collision was invisible to the tools. `git merge-tree` reported exactly one
content conflict, in `REQUIREMENTS.md`, where both sides append to the
traceability table. `ROADMAP.md` merged clean and produced two `### Phase 14`
headings. Nothing would have flagged that.

## What was done

**Merged** `origin/main` into `main`, keeping both requirement blocks.

**Renumbered** the reading and teaching work to Phase 13.5. It kept every word
of its content and changed only its number, which is also correct on
dependencies: it hardens the reader and quiz surfaces shipped through Phase 13,
and the source-to-course spine builds on those surfaces. Decimal inserts are the
existing convention here (02.1, 03.1, 03.2, 06.2, 09.1), and the retired Phase 12
slot is the standing precedent for not reusing a number that came to mean two
things.

Renamed with the number:

- the phase directory and all thirteen files inside it
- the eight plan references and the UI-spec reference in `ROADMAP.md`
- the twelve RTS rows in the `REQUIREMENTS.md` traceability table
- the `teaching` settings group's `x-itembank-phase` annotation, now `13.5`
  alongside the existing `2.1` on `update_policy`
- the "Phase 14" comments in `runtime.py`, `surfaces/daemon.py`,
  `surfaces/session.py` and `surfaces/settings.py`

`tests/config_roundtrip.py` asserted the annotation was `14`; it now asserts
`13.5`, with the reason in a comment so the next reader does not treat it as
drift.

**Routed the twelve RTS requirements** rather than retiring them.
`research/phase-16/14-synthesis.md` section 15 replaces the flat 14-to-17
sequence with nine subphases, and each RTS row has a home there: RTS-01, 03, 04
and 11 to 17A; RTS-02 and 06 to 16B; RTS-05 to 16A, where hover/focus/touch
definitions are the first catalogued capability; RTS-07, 08 and 09 to gate G6,
which the reframe leaves untouched; RTS-10 and 12 to gate G4. Recorded in
`REQUIREMENTS.md` under § Reading & teaching surface quality.

**Repaired `STATE.md`**, which read `current_phase: complete` and `18/18`
throughout the period Phase 13.5 was accruing commits.

## Corrected in passing

`REQUIREMENTS.md` claimed "127 total" requirements on both sides of the merge, a
figure that stopped being true several phases before either branch existed.
Recounted at merge time: 170 checklist ids (105 open, 65 closed) and 170 rows in
the traceability table, so the mapping is still complete. The number was
recounted rather than carried forward.

## Verification

- No conflict markers anywhere under `.planning/`.
- `grep -c "^### Phase 14" .planning/ROADMAP.md` returns 1, and it is Course
  Workspace & Source Binding.
- No RTS row names Phase 14.
- The phase directory is `13.5-reading-teaching-surface-quality-pass/` with all
  thirteen files intact through `git mv`.
- `tests/config_roundtrip.py` and `tests/hint_roundtrip.py` pass.
- `python itembank.py lint fixtures/sample_bank.md`: 6 items, 0 errors.
- Full Python suite run after the rename; result recorded in the session, not
  re-asserted here.

## Deliberately not done

- Synthesis sections 14 and 15 propose replacing the flat 14-to-17 sequence with
  nine subphases (14A, 14B, 15A, 15B, 16A, 16B, 16C, 17A, 17B) and rewriting
  `SOURCE-TO-COURSE.md`, `PROJECT.md`, `REQUIREMENTS.md`, `ROADMAP.md`,
  `UI-SPEC.md`, `PLANNING-DIRECTIVES.md`, `AGENTS.md` and `README.md`. That is a
  planning decision with its own readiness audit (synthesis section 16.3), not a
  mechanical renumber. **The roadmap still carries the sequence its own research
  supersedes.**
- Plans 13.5-04 through 13.5-08.
- Pushing. The merge is local so a human can review the renumber before it
  becomes shared history.

## Open question for Weibao

Did whoever authored the source-to-course reframe know Phase 13.5 existed? If
the reframe was meant to supersede the reading and teaching work rather than sit
beside it, plans 13.5-04 through 13.5-08 may be cancellable rather than
re-homed. Nothing in the merged documents mentions the phase either way.
