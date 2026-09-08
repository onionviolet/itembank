# 20-03 Summary

## Why this summary exists

Plan 20-03 is complete for its deterministic implementation and verification
gate. This summary records the shared working-tree evidence without treating
the explicitly skipped human visual or screen-reader review as a pass.

Lessons, Study, and served Quiz now carry the common application, course,
reading, and learner-activity hierarchy while retaining distinct learning
purposes and controls. The activity frame separates purpose, response format,
runtime-controlled disclosure, and position. Study hides front actions after
reveal and wires duplicate navigation controls. Lesson navigation retains the
course return and adds the existing supported continuation to practice.

All eight canonical response types retain their runtime names and response
schemas. Learner-facing labels and instructions cover single choice, multiple
choice, table response, build response, ordering or matching, short response,
visual interaction, and code check. Short responses state that review is
pending. Visual no-script output names its unavailable interactive control and
does not record a response. Local overflow handling keeps wide response areas
from causing page-wide overflow. Quiz help exposes only runtime-released help
instead of unreleased hint-tier vocabulary.

Verification passed:

- `python3 tests/lesson_roundtrip.py`
- `python3 tests/surface_roundtrip.py`
- `python3 tests/hint_roundtrip.py`
- `python3 tests/protocol_roundtrip.py`
- `python3 tests/presentation_profiles_roundtrip.py`
- `python3 tests/visual_accessibility_roundtrip.py`
- `git diff --check`
- `python3 scripts/preflight.py --quick`

The protocol suite emitted its pre-existing warnings for the unknown
`model_proposal` evidence event. It still passed. Human visual, touch-device,
and screen-reader review remain skipped by explicit user direction. They are
not passed or certified. No runtime scoring, item-type naming, keyed
disclosure authority, canonical assessment data, real learner evidence, remote
service, commit, or push changed.

The large lesson, quiz, and runtime modules were inspected by symbol and
narrow diff windows. The actual scoped diff was reviewed after the gates:
response labels and controls are presentation-only, formal disclosure remains
mode-derived, and no second scorer or parallel item taxonomy was introduced.
