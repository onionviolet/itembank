# 17A-01 Summary: same-flow three-direction tracer

- **Plan:** 17A-01, type tracer, wave 1
- **Requirements:** VISUAL-01, VISUAL-02
- **Executed:** 2026-08-20
- **Status:** complete, both task verify commands green

## Semantic fingerprint

`edd1fe0d46435ea2` (sha256 prefix of the `<main>` body with `class`,
`data-direction`, and `<style>` stripped).

All three directions produce this identical fingerprint. That is the VISUAL-01
assertion: the directions are a token and stylesheet overlay, never a fork of
the markup. `check_semantic_parity` fails the build if any direction diverges,
and `check_directions_differ` fails if two directions render identically, so
the pair together prove the comparison has exactly one variable.

## Route

`/_visual-fixture?direction=<id>`, served by `server.maybe_visual_fixture`.

The route returns False unless `ITEMBANK_VISUAL_FIXTURE=1` is set in the
environment, so a learner running the shipped app cannot reach a prototype by
guessing a URL. `server.visual_fixture_enabled()` is the single gate and
`check_route_is_dev_only` asserts both directions of it.

The page is built by `visual_fixture.page`, which calls
`presentation.surface_shell`. There is no second document shell:
`check_one_shell` fails if `visual_fixture.py` ever emits its own doctype.

## Direction IDs

| ID | Panel structure | Border treatment | Stylesheet |
|---|---|---|---|
| `structured-studio` | Two column workspace, sticky context line | Visible `--line` at `--r-2` | `prototypes/17a/structured-studio.css` |
| `quiet-workbench` | Single column, generous vertical rhythm | Low-contrast `--chip`, whitespace over borders | `prototypes/17a/quiet-workbench.css` |
| `guided-canvas` | Staged step-framed panels, numbered steps | Heavier `--r-3`, accent-framed guided moments | `prototypes/17a/guided-canvas.css` |

Each direction's CSS is one deletable file. Removing one leaves the other two
and every shipped surface untouched, which is the D-04 reversibility
requirement. `direction_css` degrades to an empty overlay when a file is
absent rather than raising, so deletion is genuinely safe.
`check_directions_are_deletable` asserts the three files exist separately.

## Fixture coverage

`fixtures/visual_system_flow.json`, synthetic only, seven stages:

1. `shelf_resume` including two locked cards, each rendered independently with
   its own one-sentence unlock condition (D-06 ruling 12, never summarized as
   a count)
2. `source_linked_objective` with a cited source, prerequisites, and a
   five-block discrete fill state with its legend adjacent (D-06 ruling 10,
   never a bar and never a percentage)
3. `long_lesson` carrying all six named content forms: definition, warning,
   table, cited image, inline prediction, inline check
4. `wrong_answer_retry` with entitled feedback, one released hint tier, and two
   locked tiers
5. `evidence_review`, sparse, with an explicit denominator note and one pending
   prose mark
6. `ai_proposed_change`, pending review, with citations and an add/context diff
7. `agent_offline_status`, model unavailable and network offline

No key exists in the fixture or in any rendered direction. The inline check is
unreleased and locked hint tiers are absent from the DOM rather than collapsed,
which `check_no_keyed_leak` enforces against all three renderings.

## Degraded states

- **Empty or missing flow:** renders an explicit unavailable `state_panel`, not
  a blank page. `check_degraded_states` also asserts no invented percentage
  appears in the rendered body.
- **Unknown stage kind:** renders an unavailable panel for that stage instead
  of dropping it silently.
- **Missing direction stylesheet:** empty overlay, page still renders.
- **Unknown direction ID:** falls back to `structured-studio`.

## VISUAL-02 token and rule split

Configurable and clamped by `clamp_tokens`: `density` to the two named values,
`measure` to 48ch through 90ch, `leading` to 1.3 through 1.9, `accent` to a
six-digit hex. Anything else falls back to its default rather than passing
through.

Fixed and always emitted regardless of caller input: `:focus-visible` outline,
the `prefers-reduced-motion` block, and the non-color `data-state` border cue.
`check_abuse_clamp` drives density `9999`, measure `10000px`, leading `-4`, and
accent `javascript:alert(1)` through the renderer and asserts none reaches the
page while both fixed rules survive.

## Verification output

```
$ python tests/visual_system_roundtrip.py
OK   check_fixture_shape
OK   check_no_em_dash
OK   check_no_keyed_leak
OK   check_semantic_parity
OK   check_directions_differ
OK   check_tokens_resolve
OK   check_abuse_clamp
OK   check_degraded_states
OK   check_route_is_dev_only
OK   check_one_shell
OK   check_directions_are_deletable

all visual-system contract checks passed

$ python tests/stylesheet_roundtrip.py     PASS
$ python itembank.py guard .               0 offending files
$ python tests/serve_roundtrip.py          PASS
$ python tests/daemon_roundtrip.py         PASS
```

## Deviation recorded

`17A-UI-SPEC.md` "Prototype implementation vehicle" resolves prototypes as
static files under `prototypes/17a/`, while this plan's `key_links` requires
`server.py` to expose the fixture through `presentation.surface_shell`. Both
are satisfied rather than one being chosen: the route exists and goes through
the one shell, and `visual_fixture.write_static` also writes the three
directions to standalone files for side-by-side viewing without a server. The
direction CSS lives in separate deletable files either way, so the D-04
reversibility requirement holds under both.

## Out of scope, untouched

No token freeze, no chosen default direction, no `day` migration, no real
learner data, and no upstream 16B or 16C capability implementation. The default
choice is 17A-02's `checkpoint:decision` and belongs to Weibao.

## Next

17A-02: review all three renderings at 1280, 768, and 375 pixels and record the
chosen direction in `17A-DIRECTION.md`. That plan is `autonomous: false` by
design.
