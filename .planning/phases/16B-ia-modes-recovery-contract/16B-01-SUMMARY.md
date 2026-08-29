# 16B-01 summary

Plan `16B-01`, wave 1, two tasks, both complete. Two planning artifacts created
and no file outside `.planning/` touched.

## Precondition result

**2026-08-28. Phase 16B may proceed.** All seven check groups returned `ok` on
every halt-triggering field. `16B-PRECONDITION.md` holds the full record.

The landed 14A and 16A surfaces showed **no deviation from their plan text**.
Every constant this plan asserted from plan text matched source:

| Asserted from plan text | Landed value | Result |
|---|---|---|
| `journal.OBJECT_STATES` | `("clean", "conflict", "interrupted", "missing", "unavailable")` | match |
| `journal.ENTRY_STATES` | `("prepared", "applied", "refused")` | match |
| `journal.entries`, `replay`, `object_state`, `undo` | all callable | match |
| `identity.OBJECT_KINDS` is a tuple containing `"lesson"` | true | match |
| `capabilities.RENDERER_AVAILABILITY` | `("available", "degraded", "unavailable")` | match |
| `model.SEMANTIC_PROFILE_VERSION` | `1` | match |
| `lesson._CALLOUT_KINDS` contains the shipped four | 11 members, all four present | match, and larger membership is 16A's own additive growth, not a divergence |

## What 16A's freeze rests on

`16A-PRECONDITION.md` exists and its `## Dated result line` reads "2026-08-27.
Phase 16A may proceed." with all seven checks `ok` and no divergence. This is
not the "16A froze on an unresolved precondition divergence" case.
`.planning/phases/13.9-walking-skeleton/13.9-03-SUMMARY.md` exists, alongside
`13.9-01-SUMMARY.md` and `13.9-02-SUMMARY.md`, so 13.9 was walked and this is
not the "13.9 unwalked behind a frozen 16A" case. Both freeze files carry their
own `## Frozen at` heading and neither carries `## Freeze withheld`.

`16A-FREEZE.md`'s review leg closed as `accept-with-findings` under a standing
delegation from Weibao and is labelled there as an agent judgment rather than
his own. That record and `16A-REVIEW.md`'s Provenance section were read before
this check relied on the freeze.

## Additivity baseline as recorded

```
schemas/settings.schema.json 3926dad1d8ae933787cfb4bb2bc14817095143cf7012614423a46fe057420c5b
itembank.json 47c69e77940a38014c92377b9f5702d802148edff23100cccf786181e4219ce7
22
3d9a94c70270413b29390317660b37dc198fc6ae1530c4d5dd3041710c4a1235
```

Taken before any 16B change existed. `git status` after this plan shows exactly
two new files, both under `.planning/phases/16B-ia-modes-recovery-contract/`.

## Task 2 checkpoint

**Weibao chose `option-a`.** One new module `surfaces/ia.py` holds the IA read
models, the closed vocabularies, the copy tables, and `cmd_activity`,
`cmd_help_code`, and `cmd_shelf`. `surfaces/daemon.py` keeps route registration
and HTML rendering only and may contain no 16B copy string. `activity_view_state`
and `help_entry` both live in `surfaces/ia.py`. The answer is recorded verbatim
in `16B-DECISIONS.md` under `## D-16B-2`.

**Plan edits this choice forces: none.** Plans `16B-02` through `16B-11` are
already written against `surfaces/ia.py`. The module path every later plan must
use is `surfaces/ia.py`, unchanged in every `files_modified`, `<files>`,
`<read_first>`, structural ban assertion, and acceptance criterion.

## Which truth was verified by which command

| Truth | Command | Actual stdout |
|---|---|---|
| Seven dependency modules import | step 1 `python3 -c "import identity, journal, discovery, graph, course, course_package, capabilities; ..."` | `modules present` |
| 14A journal surface matches | step 2 assertion block | `14A journal surface matches` |
| 16A surface matches | step 3 assertion block | `16A surface matches` |
| Both freezes are real freezes | step 4 grep over both files | `frozen=1 withheld=0` for each |
| Shipped route and settings surface | step 6 probe | `13 37 True 13 6 22 False 19` |
| Additivity baseline | step 7 hashes | the four lines above |
| Shipped suites green | `python3 tests/daemon_roundtrip.py`, `python3 tests/config_roundtrip.py` | exit 0, exit 0 |
| Decisions file has every required heading, no `surfaces/ia.py` on disk | the plan's automated verify, with the two reconciled counts | `16B preconditions match` |

## Deviations from this plan, with reasons

**1. The plan's step 6 expected stdout and its automated verify carry stale
counts.** The plan expects `12 34 True 12 6 20 False 18` and its verify pins
`len(daemon.API_ROUTES)==12` and `len(s['properties'])==20`. The landed tree is
`13 37 True 13 6 22 False 19`. The drift is `14C-01`, `17A-05`, and `17A-08`,
every one of which landed after 16B was planned, and none of it is 16A's. Every
field step 6 exists to protect is unmoved: `ROUTE_CLI` still equals `ROUTES`'
method and pattern pairs, `SETTINGS_CODES` is still 6, and
`additionalProperties` is still `False`. The five counts were reconciled and
recorded side by side in `16B-PRECONDITION.md`'s Deviations section rather than
treated as a regression, exactly as `16B-PRECONDITION-DRYRUN-2026-08-28.md`
directed. This forces one arithmetic change downstream: `D-16B-7`'s
"`check_api_route_scope`'s literal `12` becomes `13`" is executed against the
landed tree as `13` becoming `14`, and the new `SURFACE_PARITY` row is the
fourteenth rather than the thirteenth. No structural change follows, because
every 16B plan addresses routes by name and by position relative to a named
neighbour rather than by index.

**2. `python3` was substituted for `python` in every command.** No `python`
executable exists on this machine. `python3` is Python 3.14.6. Nothing else in
any command was changed.

## Artifacts created

- `.planning/phases/16B-ia-modes-recovery-contract/16B-PRECONDITION.md`, five named sections
- `.planning/phases/16B-ia-modes-recovery-contract/16B-DECISIONS.md`, D1 through D9 transcribed verbatim, D-16B-1 through D-16B-9 locked, plus the assumption-delta disposition, the APP-02 probe enumeration, and the API coverage note
