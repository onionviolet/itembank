# 16C-04 summary

**Plan:** 16C-04, the honest-progress claim contract.
**Executed:** 2026-08-29. **Tasks:** 2 of 2. **Files:** `progress_claims.py`,
`tests/progress_claim_roundtrip.py`.

## Verification, with actual final lines

```
python3 tests/progress_claim_roundtrip.py  ->  PROGRESS CLAIMS: 6 passed, 0 failed   (exit 0)
python3 itembank.py guard .                ->  0 offending files
```

No em dash character in either file, verified with the `chr(0x2014)` form.

## The full scenario, rendered in full

All seven dimensions populated, one missing denominator, one pending mark,
one version-split objective, all three membership classes, two fill states:

```
Design coverage
  6 of 7 required objectives with a cited source
  Indeterminate: required choice has no fixed denominator.
  Unknown for this version of emt.obj.5. Earlier evidence stays with the earlier version.

Participation
  2 of 3 activities completed rather than skipped

Settled evidence
  1 of 2 responses with a settled mark

Current retention
  1 of 5 objectives due
  1 of 5 objectives stable
  1 of 5 objectives weak
  2 of 5 objectives unknown

Formal completion
  1 of 2 required objectives formally complete
  0 of 1 required choice objectives formally complete
  0 of 1 enrichment objectives formally complete

Selected enrichment
  2 of 5 enrichment objectives with a cited source

Open uncertainty
  1 pending review
  Unknown: not enough settled attempts yet

Objectives
  emt.obj.1  ###.  (3 of 4 blocks, retention stable)
  emt.obj.2  ###.  (3 of 4 blocks, retention due)
  Filled blocks show current standing for this objective. They move up and down as evidence and retention change. This is not a permanent grade.
```

The scan over that text asserts: no percent character anywhere; no aggregate
word (`overall`, `readiness`, `mastery score`, `total progress`); each of the
seven dimension labels exactly once; no line carrying two dimensions; the
indeterminate, pending, and version-split sentences exactly once each; and
`retrievability` absent.

## Fill state, both directions

| Settled | Retention | Filled |
|---|---|---|
| 4 | `stable` | 4 |
| 4 | `due` | 3 |
| 4 | `weak` | 2 |
| 4 | `at risk` | 1 |
| 1 | `stable` | 1 |

Integers throughout, never a float and never a percent. The test asserts the
strict ordering `stable > weak > at risk` and that thinner evidence at the
same retention state fills fewer blocks, so movement is proven in both
directions rather than asserted in a docstring. An unknown retention state
raises and names itself.

## The three degraded paths, each with its locked sentence

- **Missing denominator.** `Indeterminate: required choice has no fixed
  denominator.` The scenario reaches it the way a real course would: a
  required-choice group with no fixed designed count, not a synthetic null.
- **Pending.** `1 pending review`. The unmarked response is in the
  settled-evidence denominator and NOT in its numerator, asserted as
  `1 of 2`: it is neither a pass nor a failure.
- **Version split.** `Unknown for this version of {objective}. Earlier
  evidence stays with the earlier version.` The split objective contributes
  zero to the claim and is excluded from every membership denominator, both
  asserted.

## Separate denominators, proven by rendering twice

The required rows are byte-identical with and without the enrichment
objective present, which is GRAPH-03's "adding enrichment can never lower
completion" tested rather than promised. Required and enrichment carry
different denominators, also asserted.

## Purity

`progress_claims.py` imports nothing at all: no `evidence`, no `runtime`, no
surface, no standard-library module. The test walks its AST for imports and
for any `open(` call, because the snapshot arriving as an argument is the
whole reason `evidence.capture_events` exists, and a second reader inside
this module would let an append during a render split the story the render
tells.

## Deviations from the plan

Three, all small and none changing a contract:

1. **`claim_text` checks pending before indeterminate.** The plan lists the
   branches determinate, indeterminate, pending, unknown, which as written
   makes a pending claim with no denominator (the usual shape, since nobody
   knows how many marks are coming) render the indeterminate sentence. The
   plan's own behavior block requires `2 pending review` for exactly that
   claim, so the order was corrected and the reason recorded in the code.
2. **`SETTLEMENTS` and `FILL_BLOCKS` exist as named constants.** The plan
   inlines both. Naming them lets the test and the later tracer read the
   vocabulary rather than retype it.
3. **`render_claims_text` humanizes the scope id** when interpolating it
   into the indeterminate and unknown sentences, so a learner reads
   `required choice` rather than `required_choice`. The stored scope is
   unchanged and is still the machine identity.

The plan's commands are written as `python`; this machine has only `python3`,
the deviation `16C-PRECONDITION.md` records as item 3.
