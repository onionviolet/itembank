# UI and architecture considerations (2026-10-08)

Status: findings and proposals only. Nothing here is accepted or implemented.
Method: read the ui-generic-audit (2026-10-07) and product-gm UI lane brief,
counted module sizes and top-level symbols, grepped cross-layer imports and
embedded asset strings. Modules were sampled by symbol, not read in full.

## Findings

F1. Uncommitted work is the largest live risk. `git status` shows 153 dirty
paths, 76 tracked files with about 5,082 insertions, spanning several GSD lanes
(UI GM stages 1 to 4, prior-implementation F1 to F5, feature work). AGENTS.md
says a plan's work should not sit uncommitted where concurrent processes can
remove it. The UI audit already documents per-stage recovery, which makes
per-lane commits feasible.

F2. Open verification debt on the UI overhaul. Per the 2026-10-07 audit:
`tests/js/quiz_observers.test.mjs:130` ("bundled auto-render must handle
delimiters") fails; daemon-backed tests time out at about 6s under load;
no browser evidence exists for stages 2 to 4 (Soft, Cash, Neo, lesson, 390px
question); human visual acceptance (COORDINATION W4) is still owed.

F3. `surfaces/daemon.py` is an 8,616-line god module: 218 top-level defs, 108
`handle_*` handlers, a `ROUTES` table, its own `COURSE_FRAME_CSS`, quiz form
tokens, flash receipts, day force tokens and a module lock. Rule 1 holds (it
calls the runtime), but every UI lane collides on it, which is why the product
GM brief had to reserve it for Integration alone.

F4. Front-end code lives in Python strings. `quiz_page.py` holds `SERVED_JS`
(about 2,990 lines) and `OFFLINE_JS` (about 957). Lesson, day, home, palette,
lti and lesson_interaction each carry their own CSS/JS blobs. JS tests import
adapters by slicing these strings out of `quiz_page.py`. Consequences: no
editor tooling or syntax checking, and CSS authority is split across about
twelve modules despite `presentation.py` and `theme.py` being the intended
owners.

F5. Layering inversions. `model.py` imports `_is_separator_row`,
`_split_cells` and `_CALLOUT_MARK_RE` from `surfaces.lesson` (lines 1082, 1956,
4421). `runtime.py` imports `surfaces.settings` (3613, 3742). The parser and
scorer depend on a client layer, against the four-layer diagram, and the
imported names are underscore-private, which the conventions forbid.

F6. Composition work is the right direction but is unproven in a browser. The
seven-look composition tokens (P4) make looks differ in shape, not just tint,
which answers the owner's W4 complaint. The risk now is breadth: seven looks
times light/dark times four screens is 56 states no human has compared.

## Proposals (ranked)

A1 (S). Commit by lane. Stage each lane's named paths into its own commit
after its targeted tests pass. Needs Weibao's git authorization.

A2 (S). Close F2 before more UI. Fix or explain the quiz_observers failure,
rerun daemon tests on an idle machine, take the missing screenshots. Then ask
Weibao to pick the looks that earn their keep; retiring three or four would cut
the review matrix and maintenance in half.

A3 (M). Split the daemon by route family, mechanically. Move handlers into
`surfaces/routes/{quiz,course,day,reading,api,media,settings}.py`, keep
`ROUTES` as the single table in daemon.py, move per-handler token stores into
a small state object. No behavior change; the diff is moves only, verified by
the existing route tests. This lets UI and feature lanes work in parallel.

A4 (M). Move JS and CSS into real files under `surfaces/assets/`, loaded by a
tiny reader that returns the same strings. Offline export still inlines them,
so the single-file offline quiz is unchanged. JS tests import the module files
directly instead of string-slicing. Do the 3k-line `SERVED_JS` first.

A5 (S). Fix the inversions. Move the table and callout helpers into `model.py`
(or a `markdown_blocks.py` below both) as public names; pass settings into the
runtime as arguments instead of importing a surface.

## Further considerations (not ranked)

- Add a layering check to `preflight --quick`: fail if `model.py`, `runtime.py`
  or `evidence.py` import `surfaces`. Cheap and prevents F5 recurring.
- Add a size budget warning (for example 3,000 lines per module) so new god
  modules surface early, not after the fact.
- Packaged desktop app is a stated end goal; A3 and A4 are prerequisites for a
  clean webview shell, since assets as files are what a packager expects.
- Copy voice (audit P5) remains half done: runtime-owned hint-ladder strings
  ("Tier N is unlocked") still leak runtime vocabulary. Changing them is a
  runtime disclosure-copy change and needs its own decision.
