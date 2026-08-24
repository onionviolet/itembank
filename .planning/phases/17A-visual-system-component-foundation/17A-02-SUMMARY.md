# 17A-02 summary

Executed 2026-08-24. Written because the plan asks for it by name: a token
table, day parity evidence, a raw-value allowlist and rollback notes.

## Task 1, the decision checkpoint

Closed before this session, on 2026-08-20, and recorded in `17A-DIRECTION.md`:
look `structured-studio`, navigation `sidebar`, accent `indigo` (`#4a4ad4`),
with the other two looks and the other two navigation shapes kept as options
rather than deleted. No artifact was produced here and Weibao was not asked
again.

## Token table, as frozen in `presentation.SHARED_CSS`

| Token | Value | Notes |
|---|---|---|
| `--text-xs` | `12px` | Labels, provenance, compact status, table headers, chip text |
| `--text-body` | `16px` | Default UI copy, item stems and options |
| `--text-lesson` | `18px` | Sustained authored lesson prose only |
| `--text-heading` | `20px` | Section, activity and panel headings |
| `--text-display` | `32px` | Page-level result, score, or major report heading |
| `--density-row-gap` | `var(--space-3)` / `var(--space-2)` | comfortable / compact |
| `--density-card-pad` | `var(--space-3)` / `var(--space-2)` | comfortable / compact |
| `--density-list-gap` | `var(--space-2)` / `var(--space-1)` | comfortable / compact |

Each token carries only the size. The paired weight and line height stay in
the rule that uses them, because a weight belongs to a heading rather than to
a size, and putting both in one token would have invented eight names where
the spec froze five.

`check_frozen_type_tokens` pins every value and additionally asserts that the
set of token values equals `TYPE_SCALE_SIZES`. Without that second assertion a
sixth size could enter through a token while gate 12 kept passing, since gate
12 reads literal `font-size` declarations and a rule that says
`font-size:var(--text-small)` carries no literal.

## Raw-value allowlist

The only raw lengths this plan added are the five type sizes above, and they
are the existing project scale rather than new values. Density added no raw
length at all: both sides are aliases of `--space-*`. That aliasing is the
bound the spec asks for, and it is mechanical rather than documentary, because
`--space-1` is the floor of the scale, so nothing tighter than 4px is
expressible without adding a spacing step. `check_density_bounds` fails any
density value that is not `var(--space-N)`, and separately fails any
`min-height` or `min-width` sized from a density token, so the 44px touch
floor stays fixed regardless of density.

## Day parity evidence

`surfaces/day.py` was the one served route that owned its own doctype. It
therefore carried neither the shared token layer nor any of the four vendored
faces, which is the same defect as D-B on a surface Phase 14 did not own.

What moved:

- `day_page` now returns `presentation.surface_shell(...)`. `doc_title` keeps
  the tab on the date while the `h1` keeps the weekday, which is the split the
  route always had. `tail` keeps the boot script after the `main` landmark,
  where it was. `extra_css` emits `DAY_CSS` after `SHARED_CSS`, so day's sheet
  still wins the cascade it won when it owned the whole document.
- `DAY_CSS` lost `*{box-sizing:border-box}`, `max-width`, `margin-inline`,
  `margin`, and the body padding. Those are the shell's, and they were deleted
  rather than overridden, because two owners of one layout is the duplication
  the migration exists to remove. It kept day's `15px/1.45` chrome font, the
  `-webkit-text-size-adjust` guard, and `.surface{padding:14px 16px 24px}`,
  which preserves day's tighter column against the shell's 24/64 reading
  padding.

What is asserted, in `day_roundtrip.check_day_composes_one_shell`: exactly one
doctype, one `h1` and one `main`; the `surface` wrapper present; `SHARED_CSS`
present verbatim; four vendored faces where there were zero; the title/heading
split intact; every id the day JS binds to (`streak`, `streakword`, `hist`,
`verdict`, `sub`, `bar`, `note`), the `window.__day__` boot payload, the plan
path line, and all six lanes still present; and the boot script still after
`</main>` rather than inside it.

In `stylesheet_roundtrip`, `served /day/sample_plan` moved out of
`REPORTED_FONT_ROUTES` and into `REQUIRED_FONT_ROUTES`, so gate 9 now asserts
four served routes instead of three. The reported tuple was left in place,
empty, rather than deleted: it is the mechanism that kept this gap visible for
a year, and the next surface that needs it should not have to reinvent it.

## Two contradictions with the plan, both recorded rather than worked around

**`surfaces/theme.py` is in `files_modified` and was not modified.** Two
reasons, and both are the plan's own. `--edge` is verify-only per 17A-UI-SPEC
(it already ships in `SEMANTIC_TOKENS` at `#7f8b88` light and `#697774` dark,
and `check_semantic_token_contrast` already measures it at 3:1 against card,
bg and chip), so verifying it is the whole task and it needed no edit. And
"promote only the checkpoint-selected overlay" was already done by the
checkpoint itself: `visual_fixture.DEFAULT_DIRECTION` is `structured-studio`
and `17A-DIRECTION.md` explicitly defers moving the shipped
`theme.DEFAULT_ACCENT` from teal to indigo to 17A-04, because that changes
what every existing surface renders and needs 17A-04's accessibility pass.
Promoting it here would have contradicted the direction record.

**The type and density tokens went into `presentation.SHARED_CSS`, not
`theme.py`.** `theme.py` owns the per-document colour block emitted through
`_TOKEN_ORDER`; the non-colour scale tokens (`--space-*`, `--measure-*`,
`--r-*`, `--leading-lesson`) all live in the `SHARED_CSS` `:root`, and
17A-UI-SPEC's spacing section confirms that placement. Type and density are
scale tokens, so they joined their own kind.

## Rollback

Three independent reverts, in this order if all are wanted:

1. The day migration alone: restore `day_page`'s inline document and the five
   deleted `DAY_CSS` declarations, then move `served /day/sample_plan` back
   into `REPORTED_FONT_ROUTES` and drop `check_day_composes_one_shell`. The
   token work does not depend on it.
2. The `surface_shell` arguments alone: they are additive with defaults that
   reproduce today's output byte for byte, so removing them is safe once the
   day migration is reverted, and unsafe before.
3. The tokens alone: delete the two commented blocks in the `SHARED_CSS`
   `:root` and the `[data-density="compact"]` rule, plus
   `check_frozen_type_tokens` and `check_density_bounds`. Nothing consumes the
   tokens yet, so nothing else moves.

## Verification

`stylesheet_roundtrip`, `day_roundtrip`, `visual_system_roundtrip`,
`serve_roundtrip`, `lesson_roundtrip`, `daemon_roundtrip` and
`python3 itembank.py guard .` all exit 0.

`day_roundtrip` requires Anki quit, or `ANKI_CONNECT_URL` pointed at a dead
port, because it asserts the exact Anki-closed copy and Anki Desktop is
running on this Mac. That failure is environmental and predates this plan; a
full-suite baseline taken immediately before this work showed 67 of 70 suites
green with the same three environmental failures (`day_roundtrip`,
`retention_ui_roundtrip`, and an order-dependent flake in `day_edit_roundtrip`
whose `run_cli` helper merges stderr into stdout before `json.loads`).
