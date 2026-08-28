# 16B-01 precondition check, second dry run 2026-08-28

**This is not `16B-PRECONDITION.md` and must not be renamed to it.** Plan
16B-01 step 9 creates that file on success only, as part of executing 16B-01
with its blocking decision checkpoint. This run does not execute that plan; it
re-runs the seven checks read-only, because the blocker the 2026-08-27 dry run
found has been cleared and the answer is useful now.

Run by an agent, read-only. Nothing outside `.planning/` was touched.

Supersedes nothing. `16B-PRECONDITION-DRYRUN-2026-08-27.md` stays as the record
of what was true that day.

## Result

**The 2026-08-27 blocker is CLEARED. A different, smaller divergence has taken
its place.**

Phase 16A executed and froze on 2026-08-28. Every one of the four steps that
was divergent on 2026-08-27 now passes:

| Step | Check | 2026-08-27 | 2026-08-28 |
|---|---|---|---|
| 1 | Seven dependency modules import | **divergent** (`capabilities` absent) | **ok**, all seven |
| 2 | 14A journal surface matches plan text | ok | ok |
| 3 | 16A surface matches plan text | **divergent** (two of three legs) | **ok**, all three |
| 4 | Both freeze records exist and are real freezes | **divergent** (`16A-FREEZE.md` absent) | **ok**, both real |
| 5 | What those freezes rest on | **divergent** (`16A-PRECONDITION.md` absent) | **ok** |
| 6 | Shipped daemon and settings surface unmoved | ok, two recorded deviations | **ok on every halt field**, five counts drifted |
| 7 | Additivity baseline captured, shipped suites green | ok | ok, baseline retaken |

### Step 3, 16A surface, now matching

```
capabilities.RENDERER_AVAILABILITY  ('available', 'degraded', 'unavailable')
model.SEMANTIC_PROFILE_VERSION      1
lesson._CALLOUT_KINDS               11, all four shipped kinds present
```

The planned value for `_CALLOUT_KINDS` was the shipped four. It is now eleven,
which is 16A's own additive growth and is what `16A-FREEZE.md` freezes. A 16B
plan that asserts exactly four would be asserting a pre-16A tree.

### Step 4, freeze records

```
14A  ## Frozen at 14A   present, no withholding
16A  ## Frozen at 16A   present, no withholding
```

`16A-FREEZE.md` records that its review leg closed as `accept-with-findings`
under a standing delegation from Weibao and is labelled there as an agent
judgment rather than his own. **Whoever executes 16B-01 should read that record
and its `16A-REVIEW.md` Provenance section before relying on the freeze**, since
striking that section reopens it.

### Step 5, what the freezes rest on

`16A-PRECONDITION.md` is present and its dated result line reads
"2026-08-27. Phase 16A may proceed." with all seven checks `ok` and no
divergence. Three `13.9-*-SUMMARY.md` files are present, so 13.9 was walked.
This is not the "16A froze on an unresolved precondition divergence" case.

## The new divergence: 16B-01's expected counts are stale

Step 6's probe, run verbatim from `16B-01-PLAN.md` line 282:

```
found 2026-08-28:   13 37 True 13 6 22 False 19
dry run 2026-08-27: 12 36 True 12 6 21 False 18
planned in 16B-01:  12 34 True 12 6 20 False 18
```

**Every halt-triggering field is clean.** The third field is `True`, so
`daemon.ROUTE_CLI`'s key set still equals `daemon.ROUTES`' method and pattern
pairs; `len(settings.SETTINGS_CODES)` is still `6`; and the schema's
`additionalProperties` is still `False`. Those three are what step 6 exists to
protect and none has moved.

Five counts have drifted, all upward and all from phases that landed after 16B
was planned:

| Field | Planned | Now | Moved by |
|---|---|---|---|
| `len(daemon.API_ROUTES)` | 12 | 13 | `14C-01`, the one source route |
| `len(daemon.ROUTES)` | 34 | 37 | `14C-01` plus `17A-05` and `17A-08` |
| `len(daemon.SURFACE_PARITY)` | 12 | 13 | `14C-01` |
| `len(settings.schema properties)` | 20 | 22 | `14C-01` source group, `17A-05` oled theme, `17A-08` home modes |
| `len(settings.schema required)` | 18 | 19 | the same |

**None of it is Phase 16A's.** `git log -- schemas/settings.schema.json` names
`14C-01`, `17A-05`, and `17A-08`.

**Why this matters, and it is not a halt.** Plan `16B-01`'s own automated verify
at line 418 asserts `len(daemon.API_ROUTES)==12` and `len(s['properties'])==20`
as hard equalities. Those assertions would fail today against a tree that is
perfectly healthy. Whoever executes 16B-01 must **reconcile those expected
values against the landed tree first**, recording the found-versus-planned pair
the way `16A-PRECONDITION.md` does, rather than treating a legitimate 14C and
17A addition as a regression. The equality on `ROUTE_CLI` and the three fields
above should stay hard assertions; the five counts should become
recorded-and-compared rather than pinned.

## Step 7, additivity baseline RETAKEN

The 2026-08-27 dry run warned that its baseline was taken while 16A had not
landed and must be retaken. It has been:

```
schemas/settings.schema.json 3926dad1d8ae933787cfb4bb2bc14817095143cf7012614423a46fe057420c5b
itembank.json                47c69e77940a38014c92377b9f5702d802148edff23100cccf786181e4219ce7
settings schema properties   22
SETTINGS_CODES fingerprint   375fe7cd8045ff70a9293e4ca4019bb689ce95b5c19a2217ffb5df72625260e6
```

**Phase 16A added no settings key and did not touch
`schemas/settings.schema.json`.** The change from the 2026-08-27 values is the
14C and 17A drift above, not 16A's.

Shipped suites, both green:

```
python tests/daemon_roundtrip.py   exit 0
python tests/config_roundtrip.py   exit 0
```

## What still stops 16B, and it is not a divergence

Two things, both by design rather than by drift:

1. **`16B-DECISIONS.md` does not exist.** Plan 16B-01 Task 1 step 9 writes it,
   and 16B-01's automated verify asserts it carries `## D9.`, `## D-16B-9.`,
   `## Assumption-delta disposition`, and `## APP-02 probe enumeration`. That is
   executing 16B-01, not a precondition on it.
2. **16B-01 Task 2 is a `checkpoint:decision` gated `blocking`**: where the IA
   read models and the new CLI handlers live. It is a one-way module-boundary
   decision of the same class as `D-16A-2`, and it is reserved for Weibao.

## Dated result line

**2026-08-28. The Phase 16A blocker on Phase 16B is cleared.** Steps 1 through
5 pass, step 6 passes on every halt field with five counts to reconcile, and
step 7's baseline is retaken. Phase 16B is ready to be executed as soon as its
own blocking decision checkpoint is answered.
