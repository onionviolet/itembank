---
task_id: 260813-r5c
slug: merge-source-to-course-renumber-13-5
created: 2026-08-13
mode: quick
status: planned
---

# Quick task: merge the source-to-course reframe and renumber Phase 14 to 13.5

## Why

`origin/main` and local `main` diverged on 2026-08-13. Both sides introduced a
phase numbered 14, and they are different phases:

| | local `main` | `origin/main` |
|---|---|---|
| Phase 14 | Reading & Teaching Surface Quality Pass | Course Workspace & Source Binding |
| Requirements | RTS-01..12 mapped to "Phase 14" | COURSE-01..04 mapped to "Phase 14" |
| Work done | 3 of 8 plans executed, 22 commits | planning docs only, 15 commits |

`git merge-tree` reports exactly one content conflict, in
`.planning/REQUIREMENTS.md`, where both sides append to the traceability table.
`ROADMAP.md` merges clean and silently produces two Phase 14 headings, which is
the worse failure because nothing flags it.

The roadmap already set precedent for this in the Phase 12 slot: a number that
came to mean two things was retired rather than reused.

## Decision

The reading and teaching work keeps its content and loses its number. It becomes
**Phase 13.5**, which is where it actually sits: it hardens the reader and quiz
surfaces shipped through Phase 13, and it precedes the source-to-course spine
that Phases 14 through 17 open. The repository's own convention for an insert
between shipped phases is a decimal (02.1, 03.1, 03.2, 06.2, 09.1).

The twelve RTS requirements are not retired. `research/phase-16/14-synthesis.md`
section 15 replaces the flat 14-to-17 sequence with subphases, and every RTS
requirement has a home there:

| Requirements | Destination | Reason |
|---|---|---|
| RTS-01, RTS-03, RTS-04, RTS-11 | 17A visual system and component foundation | tokens, type scale, rhythm, control boundaries |
| RTS-02, RTS-06 | 16B IA, modes and recovery contract | sticky band, anchor landing, `reader_nav` |
| RTS-05 | 16A semantic capability contract | hover/focus/touch definitions, first item in the S2C capability catalog |
| RTS-07, RTS-08, RTS-09 | gate G6, assessment authority | the runtime owns disclosure of keyed content; unchanged by the reframe |
| RTS-10, RTS-12 | gate G4, portable capability | live regions and the additive-format floor |

## Scope

In scope:

1. Merge `origin/main` into `main`, resolving `.planning/REQUIREMENTS.md` by
   keeping both requirement blocks.
2. Renumber the local phase to 13.5: `git mv` the phase directory, rewrite the
   roadmap headings, and record the collision at the Phase 14 slot.
3. Retarget the RTS-01..12 traceability rows from "Phase 14" to "Phase 13.5".
4. Repair `.planning/STATE.md`, which still reads `current_phase: complete` and
   `18/18` while Phase 13.5 has three executed plans.

Out of scope, and deliberately so:

- Applying synthesis section 14 and section 15 change proposals to ROADMAP,
  PROJECT, REQUIREMENTS, UI-SPEC and PLANNING-DIRECTIVES. That is a planning
  decision with its own readiness audit (synthesis section 16.3), not a
  mechanical renumber.
- Executing plans 13.5-04 through 13.5-08.
- Pushing. The merge stays local until a human reviews the renumber.

## Tasks

- [ ] T1: Merge `origin/main`, resolve `REQUIREMENTS.md` keeping both blocks,
      retarget the twelve RTS rows to Phase 13.5. One commit.
- [ ] T2: Renumber in `ROADMAP.md` and `git mv` the phase directory; leave a
      supersession note at the Phase 14 heading naming the collision and the
      date. One commit.
- [ ] T3: Repair `STATE.md` frontmatter and current-position prose; record this
      quick task. One commit.

## Verification

- `git status` clean, no conflict markers anywhere under `.planning/`.
- `grep -c "^### Phase 14" .planning/ROADMAP.md` returns 1, and that heading is
  Course Workspace & Source Binding.
- No RTS row in the traceability table names Phase 14.
- The phase directory is `.planning/phases/13.5-reading-teaching-surface-quality-pass/`
  and its eleven plan/spec files survived the move.
- `python itembank.py lint` on a fixture bank still passes, proving the merge
  did not disturb the runtime.
