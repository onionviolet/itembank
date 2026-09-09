# Phase 16B precondition check

## Why this check exists

`16B-RESEARCH.md`'s "Critical caveat" records that `identity.py`, `journal.py`,
`discovery.py`, `graph.py`, `course.py`, `course_package.py`, `director.py`, and
`blueprint.py` all read MISSING at the repository root when this phase was
researched and planned, that no `14A-FREEZE.md` and no `16A-FREEZE.md` existed,
and that `.planning/phases/13.9-walking-skeleton/` held only PLAN files with no
SUMMARY. Every 14A and 16A signature in the 16B research and pattern map was
therefore read from plan text, never from source. 16B also sits downstream of
two phases that had not executed plus, transitively, 14B and a 13.9 that
ROADMAP.md makes 14B's freeze conditional on. This check is one degree stricter
than 16A-01's for the reason `16B-RESEARCH.md` Pitfall 1 states: 16B must
distrust two freeze records, so it reads `16A-PRECONDITION.md`'s own dated
result line and 13.9's summary evidence rather than trusting a frozen heading.

## What was checked

- Step 1, the seven dependency modules import: `ok`
- Step 2, the frozen 14A journal and identity surface matches plan text: `ok`
- Step 3, the frozen 16A capability, profile-version, and callout surface matches: `ok`
- Step 4, `14A-FREEZE.md` carries `## Frozen at 14A` and no `## Freeze withheld`: `ok`
- Step 4, `16A-FREEZE.md` carries `## Frozen at 16A` and no `## Freeze withheld`: `ok`
- Step 5, `16A-PRECONDITION.md` exists and its dated result line states 16A may proceed: `ok`
- Step 5, `.planning/phases/13.9-walking-skeleton/13.9-03-SUMMARY.md` exists, so 13.9 was walked: `ok`
- Step 6, `daemon.ROUTE_CLI` key set still equals `daemon.ROUTES`' method and pattern pairs: `ok`
- Step 6, `len(settings.SETTINGS_CODES)` is still `6`: `ok`
- Step 6, the settings schema's `additionalProperties` is still `False`: `ok`
- Step 6, the five route and settings counts: `divergent`, recorded in Deviations, not a halt
- Step 7, additivity baseline recorded before any file outside `.planning/` was touched: `ok`
- Step 7, `tests/daemon_roundtrip.py` and `tests/config_roundtrip.py` both exit 0: `ok`

## Additivity baseline

Plan 16B-06 asserts every pre-existing settings key unchanged against these
values. A changed pre-existing key means the settings change was not additive.

```
schemas/settings.schema.json 3926dad1d8ae933787cfb4bb2bc14817095143cf7012614423a46fe057420c5b
itembank.json 47c69e77940a38014c92377b9f5702d802148edff23100cccf786181e4219ce7
22
3d9a94c70270413b29390317660b37dc198fc6ae1530c4d5dd3041710c4a1235
```

## Current compatibility baseline

The original additivity evidence above remains historical evidence. The
configuration compatibility fixture uses this later baseline because Phase 19D
deliberately changed the shipped `model_backend` profile. It still excludes
every additive key listed in `tests/config_roundtrip.py`, including Phase 20's
`presentation_profile`, and therefore catches any unapproved change to the
remaining existing effective settings values.

```
22
30483f6f1f49a06ba3949420bfb041254745876d80dfad0508df03a519ff1bc5
```

## Current rendered-settings compatibility baseline

The no-sections `theme_page(cfg)` fixture keeps its original historical
fingerprints in `tests/mode_layer_roundtrip.py`. Phase 20 deliberately passes
the settings-derived `presentation_profile` to the shared shell. On 2026-09-08
the same recorded hash command returned the current compatibility value below.
The preceding value remains in that test's dated history.

```
bd95f46dad87ce478d6954a198caaefb9ab044c31c671980974bb2caaf3012e9
```

## Deviations found

Two, neither a halt.

**1. The step 6 route and settings counts moved. Every halt-triggering field is
clean.** Plan `16B-01` step 6 expects `12 34 True 12 6 20 False 18`. The landed
tree prints `13 37 True 13 6 22 False 19`. The third field is `True`, the fifth
is `6`, and the seventh is `False`, which are the three fields step 6 exists to
protect, and none has moved.

| Field | Planned in 16B-01 | Landed 2026-08-28 | Moved by |
|---|---|---|---|
| `len(daemon.API_ROUTES)` | 12 | 13 | `14C-01`, the one source route |
| `len(daemon.ROUTES)` | 34 | 37 | `14C-01` plus `17A-05` and `17A-08` |
| `set(daemon.ROUTE_CLI) == set(e[:2] for e in daemon.ROUTES)` | True | True | unchanged |
| `len(daemon.SURFACE_PARITY)` | 12 | 13 | `14C-01` |
| `len(settings.SETTINGS_CODES)` | 6 | 6 | unchanged |
| `len(schema properties)` | 20 | 22 | `14C-01` source group, `17A-05` oled theme, `17A-08` home modes |
| `schema additionalProperties` | False | False | unchanged |
| `len(schema required)` | 18 | 19 | `14C-01`, `17A-05`, `17A-08` |

None of the drift is Phase 16A's; `git log -- schemas/settings.schema.json`
names `14C-01`, `17A-05`, and `17A-08`, all of which landed after 16B was
planned. Plan `16B-01`'s own automated verify pins
`len(daemon.API_ROUTES)==12` and `len(s['properties'])==20` as hard equalities.
Those two equalities are reconciled here against the landed tree and are
recorded-and-compared rather than pinned, exactly as the flagged assumption on
`len(daemon.ROUTES)` already provides for; the equality on `ROUTE_CLI`, on
`SETTINGS_CODES`, and on `additionalProperties` stays a hard assertion. The
consequence for later plans is arithmetic, not structural: `D-16B-7`'s
"`check_api_route_scope`'s literal `12` becomes `13`" is executed against the
landed tree as `13` becoming `14`, and `SURFACE_PARITY` gains its row as the
fourteenth rather than the thirteenth.

**2. The interpreter is invoked as `python3`, not `python`.** Every command in
plan `16B-01` is written as `python ...`. No `python` executable exists on this
machine; `python3` is Python 3.14.6 at `/opt/homebrew/bin/python3`. Every command
recorded below was run verbatim with `python3` substituted for `python` and
nothing else changed.

`16A-FREEZE.md` records that its review leg closed as `accept-with-findings`
under a standing delegation from Weibao and is labelled there as an agent
judgment rather than his own. That record and its `16A-REVIEW.md` Provenance
section were read before this check relied on the freeze; striking that section
reopens it. This is noted rather than recorded as a deviation, because the
freeze is a real freeze and carries no withholding heading.

## Dated result line

**2026-08-28. Phase 16B may proceed.** Steps 1 through 5 returned `ok`, step 6
returned `ok` on every halt-triggering field with five counts reconciled above,
and step 7's additivity baseline was recorded before any file outside
`.planning/` was touched.

Command output, verbatim.

Step 2:

```
14A journal surface matches
```

Step 3:

```
16A surface matches
```

Step 6:

```
13 37 True 13 6 22 False 19
```

Step 7:

```
schemas/settings.schema.json 3926dad1d8ae933787cfb4bb2bc14817095143cf7012614423a46fe057420c5b
itembank.json 47c69e77940a38014c92377b9f5702d802148edff23100cccf786181e4219ce7
22
3d9a94c70270413b29390317660b37dc198fc6ae1530c4d5dd3041710c4a1235
daemon_roundtrip exit 0
config_roundtrip exit 0
```
