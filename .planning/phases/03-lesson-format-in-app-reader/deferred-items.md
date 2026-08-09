# Deferred Items - Phase 03 (Plan 03-04)

Out-of-scope discoveries logged during execution per the deviation scope
boundary (not caused by 03-04's changes; left for a later plan to decide).

## 1. Pre-existing backlink placement quirk in lesson_page

- **Where:** `surfaces/lesson.py` `lesson_page()` (written in plan 03-01)
- **What:** The backlink assembly re-splits `render_markdown`'s output on
  `</section>` and attaches each heading's backlinks to the *next* chunk, so
  section B is nested inside section A and both backlink lists land after the
  last heading's prose instead of under their own heading (the 03-UI-SPEC
  Copywriting Contract wants each heading's prose followed by its own
  backlinks list).
- **Why deferred:** Pre-existing 03-01 behavior, unrelated to this plan's
  renderer work; fixing it changes `lesson_page()`'s assembly logic and
  should be its own small task (candidate: a later plan in Phase 3 or the
  Phase 4 surface reconciliation).
- **Evidence:** Confirmed by rendering `fixtures/lesson_bank.md` and tracing
  the split parts; all existing substring assertions pass regardless, so no
  test catches the placement.
