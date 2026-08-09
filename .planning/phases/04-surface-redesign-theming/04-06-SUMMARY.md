---
phase: 04-surface-redesign-theming
plan: 06
subsystem: ui
tags: [day, editor, conflict-recovery, force-gate, accessibility, theme, tdd]

# Dependency graph
requires:
  - phase: 04-02
    provides: day_document snapshot/save adapter with exact-byte patching, stale-revision conflicts, and confirmed force
  - phase: 04-04
    provides: theme_css single palette, presentation semantic shell/primitives, and the per-render theme_css(load_settings(root)) pattern
  - phase: 04-05
    provides: the study surface's progressive-disclosure/primary-action and settings-beside-the-bank conventions
provides:
  - Structured in-page day editor: GET /day/<stem> embeds a ready snapshot; POST /day/<stem>/edit patches only changed cells against the displayed revision (D-08, D-09)
  - No-write conflict recovery with labeled draft/current panes, copy/download/reload/reapply, and a one-use force gate (D-10, SURF-09)
  - Day cockpit migrated onto the shared generated palette; DAY_CSS reduced to component/layout rules with no color literals (D-04, SURF-07)
affects: [05-check-item-type-code-editor, later surfaces, 04-UAT browser verification]

actuals:
  tokens: 14324      # chars/4 over the realized diff (57,297 chars across day.py, daemon.py, day_edit_roundtrip.py, daemon_roundtrip.py)
  tasks: 2           # tasks completed
  commits: 6         # commits made (2 RED test + 2 GREEN feat + 1 recovery-actions feat + 1 test-cleanup)

tech-stack:
  added: []
  patterns:
    - "Structured edit without a Markdown owner: the browser sends revision plus changed cells; day.apply_day_edit is the one surface wrapper around day_document.save and reloads only parsed-plan/render state on saved"
    - "One-use force gate: secrets.token_hex token minted on conflict, bound to stem, the conflict's current revision, and a canonical draft hash; consumed before save, revalidated, and rechecked by day_document's fresh-read revision gate"
    - "Palette provenance: day_render loads validated settings beside the plan and injects theme_css; DAY_CSS consumes only semantic var() tokens"

key-files:
  created: []
  modified:
    - surfaces/day.py
    - surfaces/daemon.py
    - tests/day_edit_roundtrip.py
    - tests/daemon_roundtrip.py

key-decisions:
  - "The force request re-submits against the conflict's current revision (the revision the token is bound to), not the page-load revision; day_document.save's fresh-read gate then catches a third concurrent version."
  - "Day editor markup (conflict panes, force controls) ships server-side with the page; the client only toggles state and wires behavior, so a no-JS or mid-fetch state still has full recovery semantics."
  - "Token refusals are expressed as 200 + {status: invalid, reason} like every other day edit refusal, never as HTTP 4xx, so the client has one error shape to handle."
  - "Force tokens are consumed before the save and the store is reset per serve_scoped; a third-version conflict therefore cannot reuse an old gate and returns to recovery."

patterns-established:
  - "Exact-byte structured editing: revision + changed cells over the wire; unknown Markdown outside a submitted cell is preserved byte-for-byte by the adapter"
  - "Conflict recovery without data loss: draft stays in the form, both versions are copyable/downloadable, reload retains a recoverable draft, reapply overlays without saving"
  - "Dirty navigation contract: beforeunload attaches only while field values differ from the saved baseline and is removed on save/reload/discard"

requirements-completed: [SURF-09, SURF-07]

coverage:
  - id: D1
    description: "GET /day/<stem> embeds a ready snapshot (revision, actual editable column labels, cell values, no filesystem path in browser data) and renders an explicit Edit plan semantic form with single-line labeled controls -- no textarea, path, or new-column control -- while keeping the date/status/lane/streak/task/evidence cockpit"
    requirement: SURF-09
    verification:
      - kind: unit
        ref: "tests/day_edit_roundtrip.py#check_edit_snapshot_and_form"
        status: pass
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_day_edit_route"
        status: pass
    human_judgment: false
  - id: D2
    description: "apply_day_edit is the only surface wrapper around day_document.save; on saved it reloads the parsed plan, invalidates only render cache, and returns the fresh row/revision; invalid/unsupported results preserve drafts verbatim and never touch tick/evidence state"
    requirement: SURF-09
    verification:
      - kind: unit
        ref: "tests/day_edit_roundtrip.py#check_apply_day_edit_and_cache"
        status: pass
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_day_edit_route"
        status: pass
    human_judgment: false
  - id: D3
    description: "POST /day/<stem>/edit is allowlisted after fixed routes with CLI parity; stem resolves only through handler.plans; path/document/full-file authority fields and unknown fields are refused before any write helper runs; tick-save/open routes stay independent"
    requirement: SURF-09
    verification:
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_day_edit_route"
        status: pass
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_route_cli_inventory"
        status: pass
    human_judgment: false
  - id: D4
    description: "A stale save returns a no-write conflict with draft, fresh current snapshot, both revisions, and a one-use force token bound to stem, the conflict's current revision, and the canonical draft hash; no-token, wrong-token, changed-draft, replayed-token, wrong-stem, missing-confirmation, and third-version requests write nothing"
    requirement: SURF-09
    verification:
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_day_edit_conflict_and_force"
        status: pass
    human_judgment: false
  - id: D5
    description: "A confirmed force requires the exact UI-SPEC checkbox statement plus a separate Force overwrite button, patches only submitted cells, returns a new revision, and consumes the token; another conflict drops the old token and returns to recovery"
    requirement: SURF-09
    verification:
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_day_edit_conflict_and_force"
        status: pass
    human_judgment: false
  - id: D6
    description: "The day page carries the exact conflict heading, labeled Your draft/Current file panes, Copy/Download for each version, Reload current, Reapply draft, Retry/Copy/Download source recovery, beforeunload dirty wiring, and narrow stacking without page-level horizontal scroll"
    requirement: SURF-09
    verification:
      - kind: unit
        ref: "tests/day_edit_roundtrip.py#check_conflict_recovery_markup_and_dirty_js"
        status: pass
    human_judgment: false
  - id: D7
    description: "Day CLI/scoped rendering loads validated settings beside the plan (schema defaults when absent), injects the same generated accent/system/light/dark tokens as other surfaces, and DAY_CSS contains no hex/rgb/hsl palette literals or accent-as-semantic-status rules"
    requirement: SURF-07
    verification:
      - kind: unit
        ref: "tests/day_edit_roundtrip.py#check_day_palette_and_no_css_literals"
        status: pass
    human_judgment: false
  - id: D8
    description: "Visual adequacy of the reworked day page/editor/conflict recovery in a real browser (keyboard-only pass, 320px/200% zoom, both color modes, screen reader, reduced motion)"
    verification: []
    human_judgment: true
    rationale: "Structural/a11y contracts are automated, but final visual adequacy of the editor and conflict panes requires human UAT per 04-VALIDATION (same precedent as 04-04 D12 and 04-05 D9)."

# Metrics
duration: 30min
completed: 2026-08-09
status: complete
---

# Phase 4 Plan 6: Structured Day Editing with Conflict Recovery and Shared Palette

**The day page now edits its current plan row in-page as structured cells, surfaces concurrent file changes with a no-write draft/current recovery UI and a one-use force gate, and runs on the single generated palette -- no second color owner (D-04, D-08 through D-11, SURF-07, SURF-09)**

## Performance

- **Duration:** 30 min
- **Started:** 2026-08-08T23:34:47Z
- **Completed:** 2026-08-09T00:04:41Z
- **Tasks:** 2
- **Files modified:** 4 (surfaces/day.py, surfaces/daemon.py, tests/day_edit_roundtrip.py, tests/daemon_roundtrip.py)

## Accomplishments

- `GET /day/<stem>` now embeds a ready `day_document.snapshot` (revision, actual parsed column labels, cell values -- never a filesystem path) and an explicit **Edit plan** semantic form with one labeled single-line control per editable cell. There is no raw Markdown textarea, path input, or new-column control; the date/status/lane/streak/task/evidence cockpit stays intact (D-08).
- `apply_day_edit(state, data, force=False)` is the one surface wrapper around `day_document.save`: on `saved` it reloads the parsed plan and invalidates only the render-info cache, then returns the fresh row and revision. Invalid/unsupported results preserve every typed draft value verbatim and never touch tick/evidence state (D-09, D-11).
- The daemon adds `POST /day/<stem>/edit` after every fixed literal route with CLI parity. The stem resolves only through `handler.plans`; `path`/`document`/`plan`/`bytes` and unknown authority fields are refused before any write helper runs (T-04-21).
- A stale save returns a no-write conflict carrying the draft, the fresh current snapshot, both revisions, and a `secrets`-based one-use force token bound to plan stem, the conflict's current revision, and the canonical draft hash. Force requires the exact UI-SPEC confirmation statement and a separate **Force overwrite** button; the token is consumed before the save, and `day_document.save`'s fresh-read gate turns a third concurrent version into another no-write conflict (D-10, T-04-22, T-04-23).
- The conflict UI shows the exact heading "Plan changed outside itembank — nothing was overwritten." with labeled **Your draft** / **Current file** panes, Copy/Download for each version, **Reload current** (baseline refresh, recoverable draft retained), **Reapply draft** (overlay without saving), and a force panel gated by the checkbox statement. Unavailable/unreadable sources keep the draft and expose Retry/Copy/Download recovery instead of a dead editor.
- `beforeunload` attaches only while form values differ from the saved baseline and is removed on save, reload, or explicit discard; focus moves to the conflict heading, panes stack at narrow widths without page-level horizontal scroll, and the full documents stay selectable/copyable/downloadable.
- Day now loads validated settings beside the plan (schema defaults when absent) and injects the one `theme.theme_css` output; `DAY_CSS` was reduced to component/layout rules expressed through semantic `var()` tokens with no hex/rgb/hsl literals and no accent-as-correctness styling (D-04, SURF-07).

## Task Commits

Each task was committed atomically (RED test gate then GREEN implementation, per `tdd="true"`):

1. **Task 1: Edit and save the current day row from the themed page** - `8890453` (test) + `b0d7804` (feat)
2. **Task 2: Preserve drafts through conflicts and require a second force confirmation** - `b2807fa` (test) + `8bfa5a9` (feat)
3. **Follow-up (Task 2 scope): unavailable-source recovery actions** - `bb4af90` (feat)
4. **Follow-up (test hygiene): temp-dir cleanup in day daemon tests** - `660a1f6` (test)

## Files Created/Modified

- `surfaces/day.py` - `day_page` embeds the snapshot and renders the semantic editor/conflict/force markup; `day_render` loads settings and injects `theme_css`; `apply_day_edit` wraps `day_document.save` with plan reload/cache invalidation; `DAY_CSS` is palette-free; `DAY_JS` wires dirty tracking, save, conflict recovery, force, copy/download, and reload/reapply
- `surfaces/daemon.py` - `DAY_EDIT_RE` + `handle_day_edit` allowlisted route, `day_force_tokens` one-use store reset in `serve_scoped`, and token issue/consume helpers with canonical draft hashing
- `tests/day_edit_roundtrip.py` - editor boot snapshot/form, apply_day_edit cache/draft, palette/CSS-literal, and conflict-recovery markup/dirty-JS checks
- `tests/daemon_roundtrip.py` - edit route order/CLI/authority-field checks and the full conflict/force/token/replay/third-version scenario

## Decisions Made

- The force request re-submits against the **conflict's current revision** (the revision the token is bound to), not the page-load revision; `day_document.save`'s fresh-read gate then catches a third concurrent version. This matches the 04-02 adapter contract where a confirmed force still requires the conflict's current revision.
- Conflict/force markup ships server-side with the page; the client only toggles state and wires behavior, so recovery semantics survive no-JS and mid-fetch states.
- Token refusals use the same `200 + {status: invalid, reason}` shape as every other day edit refusal -- one client error path, no HTTP-status branching.
- `DAY_CSS` migrated onto semantic tokens: `--ok/--ok-bg` for full/floor states, `--bad/--bad-bg` for chips/badges, `--warn` for amber, `--accent` for interaction only.

## Deviations from Plan

None - plan executed exactly as written. (Test refinements during GREEN are documented under Issues Encountered; the two follow-up commits were in-scope Task 2 acceptance items.)

## Issues Encountered

- **Force revision binding (GREEN refinement):** the first force attempt sent the page-load (stale) revision and the daemon refused the token binding. Fixed by binding the token to the conflict's current revision and having the client re-submit that revision on force (commit `8bfa5a9`).
- **Third-version fixture (test refinement):** the test's "third version" byte replacement targeted text the force save had already replaced, so the third file was byte-identical; changed the mutation to the Math cell so the third-version gate is actually exercised.
- **Test isolation race (fixed):** the new day conflict/force daemon test left its `tempfile.mkdtemp()` workdir orphaned; a later pre-existing check (`check_api_start_traversal`) snapshots the system temp parent and intermittently caught the orphan. Both new daemon tests now remove their workdirs in `finally` blocks (commit `660a1f6`). Confirmed the check is otherwise stable: it passes repeatedly in isolation and in sequential full-suite runs; concurrent test-suite execution pollutes the shared temp parent.
- **Embedded-JS regex warning:** the client's `window.__day__` extraction regex inside the Python triple-quoted JS string emits a benign SyntaxWarning on Python startup; validated with `node --check` that the embedded JS itself is syntactically correct.

## TDD Gate Compliance

Commit log shows the mandatory RED->GREEN gate sequence for both tasks:

1. `8890453` `test(04-06)` (RED) followed by `b0d7804` `feat(04-06)` (GREEN)
2. `b2807fa` `test(04-06)` (RED) followed by `8bfa5a9` `feat(04-06)` (GREEN)

No REFACTOR commits were needed. The Task 2 daemon RED gate was observed against the pre-Task-2 code (force-token flow absent); the day markup assertions passed against the Task 1 commit because the recovery markup deliberately ships server-side from Task 1.

## Known Stubs

None - no placeholders, mock data, or unwired controls were introduced.

## Next Phase Readiness

- SURF-07 and SURF-09 are ready to flip Complete; Phase 04's final browser UAT covers quiz hierarchy/API authority, global accessible theming, complete study explanations, and day conflict recovery per the plan's human-check.
- Phase 05 (check item type / code editor) can reuse the editor's structured-form/status/recovery conventions and the shared palette path.
- `tests/theme_roundtrip.py`, `tests/surface_roundtrip.py`, `tests/presentation_roundtrip.py`, `tests/day_roundtrip.py`, `tests/due_roundtrip.py`, and the broader regression set remain green.

## Self-Check: PASSED

---
*Phase: 04-surface-redesign-theming*
*Completed: 2026-08-09*
