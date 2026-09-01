# course_fixture_17b

This course is entirely synthetic. The subject, Aldrasse fen ecology, is
invented for the 17B tracer at production depth and derives from no real
course material. This directory sits outside fixtures/ deliberately:
fixtures/ has concurrent in-flight edits as of 2026-08-17.

## Contents

- `scope.md`: the minimal scope tree required by 17B-CONTEXT D-03, one
  open field scope containing one bounded course scope containing the
  unit under test.
- `objectives.md`: the unit objectives, each carrying a `[SRC: ...]`
  citation into one of the two sources.
- `sources/fen_hydrology_field_notes.md` and
  `sources/lantern_moss_survey.md`: the two synthetic sources at
  production depth, with headed sections whose heading slugs are the
  stable locator anchors the objectives cite.

## Rules this fixture is built under

Every gate in `17B-GATES.md` is proven on this fixture (17B-CONTEXT
D-02). It is kept `itembank guard` clean, contains no real course
content, no AAOS-derivative text, and no em dash characters. Weibao may
run the same flow on a real course outside the repository; that evidence
is supplementary, and repo-side records carry pointers, counts, and
hashes only.
