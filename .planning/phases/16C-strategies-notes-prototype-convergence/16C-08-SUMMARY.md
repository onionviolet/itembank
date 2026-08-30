# 16C-08 summary

**Plan:** 16C-08, the legacy-upgrade audit, bounded diff, and keyed-meaning
halt.
**Executed:** 2026-08-29. **Tasks:** 3 of 3. **Files:** `upgrade_audit.py`,
`fixtures/legacy_pre135_bank.md`, `tests/legacy_upgrade_roundtrip.py`, both
`legacy-upgrade/SKILL.md` mirrors.

## Verification, with actual final lines

```
python3 tests/legacy_upgrade_roundtrip.py  ->  LEGACY UPGRADE: 8 passed, 0 failed  (exit 0)
python3 itembank.py guard .                ->  0 offending files
diff -rq .agents/skills .claude/skills     ->  no output, exit 0
```

No em dash character in any file this plan wrote.

## A pre-existing CI break, found and fixed on the way

Task 3 requires `diff -rq .agents/skills .claude/skills` to pass. It did not,
and had not since two earlier commits: `2c34a65` (13.9) added the NREMT
option-count paragraph to `.claude/skills/author-bank` only, and `d2804f0`
(14C-06) added the source-import section to `.claude/skills/ocr` only. CI's
"Skill mirrors stay identical" step has been red on main since then.

In both cases the `.claude` copy is a strict superset (the diff carries only
`>` lines), so the repair was a copy in one direction with nothing to
reconcile. Committed separately as `55379fb` so the repair is legible as a
repair rather than buried in this phase's work. `check_skill_mirrors` in this
plan's test now runs the same comparison, so a one-sided edit fails locally
before it reaches CI.

## The fixture

`fixtures/legacy_pre135_bank.md` is an invented overnight-handover procedure:
three plain lesson headings, no callouts, no `[[term]]` references, no
`## TERMS` section, and two keyed `mc` items with `[ID:]` lines. The test
asserts the absent 13.5-era constructs rather than only the present ones,
because what makes it a legacy artifact is what it does not have. It parses
with 2 items and 3 headings and leaves guard green. Its `validation` audit row
reads `0 errors, 9 warnings`, which is `model.lint(questions)` over the items
alone, the call the audit makes; the full `itembank lint` run, which also
passes the lesson and terms, reports 12 warnings. Both numbers are recorded
here because the audit row states one of them and a reader checking by hand
would see the other. A legacy artifact that lints perfectly would not be a
legacy artifact.

## The audit

Eleven rows in the locked order, every one non-empty. `rights`, `sources`,
and `media` read exactly `plan-text stand-in`, and the four rows that can be
computed are asserted NOT to stand in, so a stand-in cannot spread into a
check the audit could actually run. Passing `{"rights": True}` flips that row
to a real result with no other edit, which is how the row stops standing in
when its record ships.

The module writes nothing. The test walks its AST for any `open(` carrying a
write mode or a `mode=` keyword, and for imports of `runtime`, `evidence`, or
any surface. Every function that touches the fixture is followed by a
byte-digest comparison in the test, on the halted path as well as the clean
one: a module that writes during a dry run is a module whose review step is
decorative.

## The bounded diff

Three changes in, one proposed and two skipped. The reasonless and the
`cosmetic` ones both carry `Skipped: no learning value added.` and neither
appears in the proposed list. They are not disabled or greyed; they are not
offered. Every proposed entry keeps `before`, `after`, and `reason` together,
asserted per key, because a diff separated from its reason is a diff whose
argument the reviewer has to reconstruct, and that is how churn gets
approved.

## The halt

A flipped `CORRECT:` letter produces:

```
Halted: this change would alter keyed assessment meaning (keyed content).
Assessment changes are reviewed separately and are never part of an upgrade.
```

with affordances exactly `("Open assessment review", "Cancel upgrade")`, no
`diff` key, no key containing `override` or `force`, the audit rows still
present, and the fixture's bytes unchanged. Difficulty and objective changes
each halt with their own `{what}` substitution, tested separately.

A rationale rewrite does not halt: it proposes one change and reports
`All 11 baseline checks recorded.` That asymmetry is the point, and it comes
for free from `model.content_fingerprint`, which already excludes the
reasoning around an item.

## The skill

Both mirrors now describe what shipped: the eleven-item order, the three rows
that stand in and why, the propose-never-apply boundary with mutation routed
to the 14A journal operations, the cannot-express link with its portability
cost, and the halt with its two affordances and the sentence "Do not offer
the learner or the reviewer a way past it, and do not build one." The test
asserts the stub language is gone, the three function names are present, and
the stand-in rows are named.

## Deviations from the plan

1. **Eight checks rather than seven**, because `check_skill_mirrors` was
   added: the plan verifies the mirror with a shell `diff` outside the test,
   and a mirror that only CI checks is a mirror that drifts for a week
   between checks, as it just had.
2. **`DEFAULT_AVAILABILITY` is a module constant** rather than an inline
   default, so a later phase flips one value when its record ships.
3. **`keyed_meaning_delta` also treats an added or removed item as a delta**
   (`what` reads `item set`). The plan lists three comparisons for paired
   items and says nothing about unpaired ones; silently ignoring an item
   that appeared or vanished would be the largest keyed change of all going
   unnoticed.
4. **`cannot_express` returns `derived_ok`** alongside the derived text, so a
   caller can tell a clean projection from one the trio validator refused.
5. The plan's commands are written as `python`; this machine has only
   `python3`.
