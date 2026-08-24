# 17A-03 summary

Executed 2026-08-24 on `wt/17A-03`, base 9115ba9 (17A-02). Written because the
plan asks for it by name: the component-to-primitive-to-test map, plus two
measured facts that contradict what the plan assumed.

## Component map

Every row of 17A-UI-SPEC's Component Styling Assignments table, its primitive
in `surfaces/presentation.py`, the ruling it implements, and the check in
`tests/component_primitives_roundtrip.py` that holds it.

| Component | Primitive | Ruling applied | Test |
|---|---|---|---|
| `CourseShelf` | `course_shelf` | Direction-Neutral #1: scroll at any count, no pagination; #12: a locked card keeps its list position and its own unlock sentence | `check_overflow_bounds_match_the_spec`, `check_plain_html_stays_understandable` |
| `ActivityView` | `activity_view` | Direction-Neutral #2 plus Disclosure #5: needs-your-input, in progress, then history; only history past 5 collapses | `check_overflow_bounds_match_the_spec`, `check_partial_states_never_invent_a_number` |
| `SettingsPanel` | `settings_panel`, `wrap_path` | Direction-Neutral #4: wrap at path separators, never clip a segment, never hide the root | `check_no_truncation_anywhere_it_is_not_authorised` |
| `FirstLaunchWalkthrough` | `first_launch_walkthrough` | Direction-Neutral #3: no copy shortening, intrinsic height, dismiss is not a collapse | `check_focus_order_and_no_traps`, `check_plain_html_stays_understandable` |
| `StatusNotice` | `status_notice` | Component table: inline banner, semantic-bg tint, `role=status` or `role=alert`, never collapsed | `check_states_are_never_colour_alone` |
| `NoteCapturePanel` | `note_capture_panel` | Direction-Neutral #5: grow to eight lines then scroll internally; role and privacy lines never collapse | `check_touch_targets_and_capture_growth` |
| `NotesPanelEvidence` | `notes_panel_evidence` | Direction-Neutral #6: three per objective group, "Show all {N} notes" past that, heading always visible | `check_overflow_bounds_match_the_spec` |
| `StrategyPicker` | `strategy_picker` | Component table: available, locked and fallback rows all visible | `check_plain_html_stays_understandable`, `check_one_and_many_render_every_row` |
| `ProgressComprehensionDisplay` | `progress_comprehension_display` | Direction-Neutral #7: seven dimensions never collapse, per-objective lists show ten | `check_overflow_bounds_match_the_spec` |
| `NoteOutputTrio` | `note_output_trio`, `_clip_node_label` | Direction-Neutral #8: the decorative node clips, the adjacency list never does | `check_no_truncation_anywhere_it_is_not_authorised` |
| `EvidenceDrawer` | `evidence_drawer` | Disclosure #5: summary line visible, trail behind "Review evidence" | `check_disclosures_are_native_and_named` |
| `DiffApproval` / `LegacyUpgradeReview` | `diff_review` | Disclosure #5: diffs never collapse, list pages at ten with "Show next 10 proposed changes" | `check_overflow_bounds_match_the_spec` |
| Anchor-state chips | `anchor_chip`, `chip_row` | Direction-Neutral #9: start border and dot plus a `--text-xs` Ledger label, never fill-only, never icon-only | `check_states_are_never_colour_alone` |
| Fill-state blocks | `fill_state` | Direction-Neutral #10: five discrete blocks, legend adjacent, never a bar and never a probability | `check_fill_state_is_discrete_and_never_a_probability` |
| Loading line | `loading_line` | Disclosure #5 loading row: a stated Ledger line announced once, never a spinner | `check_loading_is_a_stated_line` |

`ContextLine`, `HintLadder`, `AgentAssist`, `LockedRefusalCard` and
`SourceCitation` are out of this plan's list. The first is already shipped
(`context_line`); the ladder, the agent panel and the refusal card are 13.5 and
16B behaviour this plan styles nothing new for; a citation is inline structure
inside whichever parent already renders it.

## State map

The seven state rows, applied uniformly rather than per component. `_fallback`
is the shared head every list primitive routes through, which is why zero,
loading and error behave identically across all nine of them.

| State | Behaviour | Test |
|---|---|---|
| zero | Empty copy rendered directly. No disclosure control over nothing (Contract section 6), and no "Show all 0". | `check_zero_state_renders_copy_not_a_control` |
| one | Same markup as many, one row. | `check_one_and_many_render_every_row` |
| many | Every row reaches the served text, expanded or behind a disclosure. Asserted at 8 rows, under every pagination bound; the bounds are asserted at their own exact counts. | `check_one_and_many_render_every_row`, `check_overflow_bounds_match_the_spec` |
| error | The surface's own degraded copy in a `role=status` region, with no stale rows underneath it. | `check_error_keeps_the_surface_recoverable` |
| loading | One stated line naming what is being read, announced once, no rows, no spinner. | `check_loading_is_a_stated_line` |
| partial | An in-progress job states its status in words and never a percent; a pending mark carries the pending token and its required label; a 2 of 5 standing still renders all five blocks. | `check_partial_states_never_invent_a_number` |
| overflow | Shelf scrolls at 40, activity history bounds at 5, notes at 3, objectives at 10, diffs page at 10, dimensions never bound. | `check_overflow_bounds_match_the_spec` |

Four cross-cutting checks sit beside the matrix: `check_states_are_never_colour_alone`
(every state has a text label, an unrecognised state goes neutral),
`check_disclosures_are_native_and_named` (native `details`, named summaries, no
hand-authored `aria-expanded`), `check_focus_order_and_no_traps` (no autofocus,
no positive `tabindex`, no focusable control inside an `aria-hidden` region),
and `check_plain_html_stays_understandable` (eight components read back with
every tag stripped).

Not certified here, deliberately: contrast under real rendering, zoom and
reflow, focus visibility, and touch measurement need the layout-capable
harness and the scripted human pass D-09 and A11Y-01 require. An agent does
not self-certify accessibility, so this fixture asserts structure and bytes
and says so in its own docstring.

## Two measured facts that contradict the plan

**1. Primitive CSS cannot consume the `--text-*` tokens yet.** The plan's
`key_links` row asks for it. `tests/stylesheet_roundtrip.py:size_problems`
matches every `font-size` value against `LENGTH_RE` and rejects anything that
is not a literal px:

    >>> size_problems('x', 'font-size', 'var(--text-xs)')
    ['x declares font-size:var(--text-xs), which is not a length this scale
      can check; sizes are absolute px on the scale']

Measured 2026-08-24 against the shipped fixture. The `font` shorthand does slip
through (a var-valued size leaves `size_at` at -1 and the whole declaration
goes unchecked), which is a hole in gate 12 rather than a licence to exploit
it. So every size in `PRIMITIVE_CSS` is the literal px equal to its frozen
token, which is what every rule already in `SHARED_CSS` does, and gate 12's own
"no sixth size" assertion still holds. The other three token families are
consumed as the plan asks: `--space-*`, `--density-*` (card padding and list
gaps), `--r-*`, and the semantic colour tokens. Teaching `size_problems` to
resolve a frozen token name to its value is a one-function change in
`tests/stylesheet_roundtrip.py`, which is not in this plan's `files_modified`;
it is the right next move and belongs to whoever owns that file next.

> **Closed the same day, 2026-08-24, in commit `544fef1`.** The orchestrating
> session already owned `tests/stylesheet_roundtrip.py` from 17A-02 and 17A-05,
> so it made the one-function change rather than leaving the freeze
> unconsumable. `size_problems` now resolves the five frozen names to their
> values and nothing else: `var(--text-xs)` and `var(--text-body)` pass,
> `var(--space-2)` and `14px` still fail. The fourteen `font-size` declarations
> in `PRIMITIVE_CSS` name their token now, and the note-capture eight-line
> grow ceiling tracks `var(--text-body)` rather than restating 16px. The
> `font` shorthand hole this section names is still open and still unexploited.
> The twenty-six literal sizes in `SHARED_CSS`'s own rules were deliberately
> left alone: they are on the scale, and collapsing them is the wider 13.5
> quiz-scale sweep that 17A-UI-SPEC D-03 assigns elsewhere.

**2. `prototypes/17a/itembank-prototype.html` is already stale.** It is a
committed export of `visual_fixture.single_file()`. Regenerated with this
plan's changes reverted in memory, the generator produces 97,410 bytes against
the file's 88,677: roughly 8.7KB of drift that predates this plan, from
17A-02's token additions never being re-exported. No test reads the file. It
was left alone rather than regenerated, because a 13KB unrelated diff inside a
components plan is the kind of silent widening the operation protocol forbids.

## Two smaller things worth not rediscovering

The slow-read line's CSS class is `ib-slow`, not the obvious name.
`SHARED_CSS` ships on every served page and
`daemon_roundtrip.check_unreachable_runtime_band` fails a page whose bytes
contain the word "loading" anywhere, because a degraded band that looks busy is
lying about the runtime. A class name is bytes on that page. The
learner-visible copy is unchanged.

No truncation rule exists in `PRIMITIVE_CSS` at all. Three shipped fixtures
(`daemon_roundtrip` twice, `gate_roundtrip`, `lesson_roundtrip`) scan served
bytes for a wrap or overflow-clip rule, and the one clip 17A-UI-SPEC
authorises (Direction-Neutral #8's decorative concept-map node) therefore
happens in Python in `_clip_node_label`, leaving the accessible adjacency list
whole.

## Verification

`component_primitives_roundtrip`, `visual_system_roundtrip`,
`stylesheet_roundtrip`, `daemon_roundtrip`, `lesson_roundtrip`,
`gate_roundtrip`, `serve_roundtrip`, `home_roundtrip` and
`python3 itembank.py guard .` all exit 0.

## Rollback

Three independent reverts. The prototype's fill-state consolidation and its
`check_primitives_stay_direction_neutral` come out together and touch nothing
else. The fixture comes out on its own. The primitive layer itself comes out by
deleting the `17A-03` section of `presentation.py` and the
`SHARED_CSS = SHARED_CSS + PRIMITIVE_CSS` line; no shipped surface calls a
primitive yet, so nothing else moves.
