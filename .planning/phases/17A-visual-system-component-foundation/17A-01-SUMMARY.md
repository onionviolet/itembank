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

---

## Revision, 2026-08-20, after Weibao's review

Three corrections, all from direct feedback on the first rendering.

**1. Keep all three directions, do not freeze one.** `PLANNING-DIRECTIVES.md`
section 1 already records the standing rule: "if conflicting potentially
implement all of them and let the user choose in the future". The prototype now
carries a direction switcher on every screen, and
`check_all_directions_reachable` asserts every screen can reach every
direction. 17A-02 becomes a default-picking decision rather than a
delete-the-losers decision.

**2. Hover definitions for confusable terms.** Weibao named the real case:
"inspiration" in a respiratory context means breathing in, not a good idea.
The Phase 3.1 glossary already shipped this (`## TERMS`, `[[term]]`, the
Popover API trigger, the panel, the appendix, the print fallback), so the
fixture reuses `lesson._gloss_trigger_html`, `lesson._gloss_panel_html`,
`lesson._glossary_html`, and `lesson._gloss_anchor_css` rather than building a
second glossary. A second hover-definition implementation would be the same
class of mistake as a second scorer.

`lesson.gloss_css()` was added as a slice of the shipped `LESSON_CSS`, guarded
by explicit markers that raise if they move, so the tracer and the reader style
their definitions from the same bytes. `LESSON_CSS` itself is unchanged.

Five terms are defined: inspiration, patent, acute, oropharynx, stridor. Each
was chosen because its everyday meaning misleads.
`check_hover_definitions` asserts the definition text ships with the page, the
panel and appendix entry both exist, and no definition rides on the trigger's
accessible name. `check_no_raw_term_markers` asserts no `[[term]]` reaches a
page as literal brackets.

**3. The first rendering was a state catalog, not a flow.** Weibao: "where is
the logical multi page flow". Correct, and the tracer scope is the reason:
seven states stacked on one scroll proves the seam and tests nothing about
navigation. The prototype is now seven screens, one stage each, with a pager
that states "Step N of 7" and links back and forward.
`check_multi_page_flow` asserts each screen renders exactly one stage, states
its position, and links to both neighbours.

Semantic parity is now asserted per screen. The fingerprint additionally
strips the prototype chrome nav and the `direction=` query parameter, both of
which are prototype plumbing rather than product markup: in the product a route
names a screen, never a visual direction.

**Design pass.** `CHROME_CSS` in `visual_fixture.py` now carries a real type
scale (`--vf-h1` through `--vf-micro`, tightening under compact density), a
spacing rhythm, and styling for every content form. The three direction files
were rewritten to differ by layout and rhythm rather than by border colour:
Structured Studio is a two-column workspace with a support rail, Quiet
Workbench is a single 46rem column with no card edges at all, and Guided Canvas
is a single stepped panel with a named step band and pill controls.

**Static export is now walkable.** `write_static` writes 21 files, seven
screens for each of three directions, and rewrites the query links into sibling
file links so the whole flow can be walked by opening one file with no server.

### Verification after the revision

```
$ python tests/visual_system_roundtrip.py     15/15 checks pass
$ python tests/stylesheet_roundtrip.py        PASS
$ python itembank.py guard .                  0 offending files
```

`tests/lesson_roundtrip.py` fails on "plain-bank public item drifted from the
pre-13.5 golden". This was verified as pre-existing: stashing every change in
this working tree leaves it failing. The cause is the modified
`fixtures/quiz_public_item_pre_13_5.json` that arrived from a concurrent track,
not this plan.

---

## Second revision, 2026-08-20: app shell, home screen, navigation shapes

Weibao: "what about the home UI? app based flow? tabs for things? side bar?"

**Finding first.** The information architecture is already settled and nobody
had noticed. `16B-UI-SPEC.md` "Information Architecture & Route Contract"
names every area and its route: app level `/`, `/activity`, `/settings`,
`/help/<code>` with Search reserved but explicitly not built; course level
`/course/<id>` Overview plus `/learn`, `/practice`, `/test`, `/map`,
`/sources`, `/build`, `/evidence`, with Notes deliberately having no route of
its own.

What is **not** settled anywhere is the shape of that navigation. Searching
`16B-UI-SPEC.md`, `17A-UI-SPEC.md`, and the project `UI-SPEC.md` for sidebar,
side rail, tab bar, tabbed, top nav, and nav rail returns zero hits. The areas
were designed; the navigation was never drawn.

**So the shape became a second axis, not a decision.** `NAV_SHAPES` offers
`sidebar`, `tabs`, and `bottom`. All three render byte-identical markup and
differ only in CSS, so picking one later is a stylesheet change rather than a
rewrite. `check_nav_shapes` asserts the markup parity and that every shape can
reach every other.

| Shape | Thesis | Cost |
|---|---|---|
| `sidebar` | Every area visible at once, routes legible, nothing behind a menu | Horizontal space, which is free on a laptop and gone on a phone |
| `tabs` | One row per level, full width stays with the content | Reads as a document with sections rather than as an application |
| `bottom` | Thumb-reachable, survives one-handed use on a shift | A strip of vertical space on every screen |

The look axis and the nav axis compose independently, so the static export is
now 63 files: three looks by three navigation shapes by seven screens.

**Home is a real screen now.** It carries a justified resume card (course, the
reason this is next, and the action), the full course list including locked
cards with their unlock conditions, and the activity queue with "Needs you"
first. `check_home_screen` asserts all three regions exist and that no
percentage is invented anywhere on it.

**The shell shows its own routes.** Each nav entry renders its 16B route
beneath its label in the sidebar shape, so the prototype can be diffed against
the contract instead of trusted. `check_app_shell_matches_16b` fails if any of
the eight course areas goes missing.

Four areas (Test, Map, Sources, and the app-level Help and Settings targets)
render as visibly unavailable rather than as working links, because no fixture
stage backs them yet. That is deliberate: an area that looks clickable and does
nothing is worse than one that says it is not built.

### Verification after the second revision

```
$ python tests/visual_system_roundtrip.py     18/18 checks pass
$ python tests/stylesheet_roundtrip.py        PASS
$ python tests/daemon_roundtrip.py            PASS
$ python itembank.py guard .                  0 offending files
```

### Still open, and deliberately not decided here

Search is reserved in 16B and not built. Notes has no route by 16B's explicit
choice. The default look and the default navigation shape are both 17A-02
checkpoints and belong to Weibao.
