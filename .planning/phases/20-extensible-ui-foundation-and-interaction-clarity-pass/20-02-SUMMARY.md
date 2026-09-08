# 20-02 Summary

## Why this summary exists

The plan was left incomplete because its human home comparison and
screen-reader review were skipped by explicit user direction. This summary
records the completed deterministic showcase pass without selecting Agenda or
Path or converting either skipped gate into a pass.

Plan 20-02 is complete for the user-authorized deterministic showcase pass.
Resume, Shelf, Agenda, and Path render over one canonical, caller-supplied home
state. Resume and Shelf refine the stable `next-action` and `shelf` modes.
Agenda and Path remain prototype names and did not enter the settings schema.
The shipped `agent` and `split` modes remain available in both presentation
profiles.

Synthetic fixtures cover empty, one-course, many-course, archived, corrupted,
interrupted, and unavailable states. Each course projection exposes one short
primary action. Agenda hides empty groups. Anki due, itembank due, course
completion, and evidence standing remain separate. Path presents durable node
states without treating a visit as mastery. Rendering preserves course IDs,
routes, resume targets, evidence labels, and appearance axes.

Verification passed:

- `python3 tests/home_roundtrip.py`
- `python3 tests/presentation_profiles_roundtrip.py`
- `python3 tests/ia_route_roundtrip.py`, 26 passed and 0 failed
- `python3 scripts/preflight.py --quick`
- `git diff --check`

Human visual comparison and screen-reader review were skipped by explicit user
direction. They are not passed. Agenda and Path have no human-approved final
disposition, and no accessibility or usability certification is claimed. No
real Math 1400 sitting, model backend, remote service, Canvas change, or
canonical assessment mutation was used. No commit was made.

The large `surfaces/daemon.py` and `tests/ia_route_roundtrip.py` modules were
sampled by symbol and narrow line windows rather than read whole.
