# R5 course shell and first-use journey evidence

Date: 2026-09-06. Status: implemented and verified.

## Result

The shelf and course pages now share an application navigation region. Courses
is visibly current on the shelf. Every course page states its current area in
text and with `aria-current`. Desktop keeps the existing area row. Narrow
screens expose the same routes through a native details disclosure.

After the learner removes the sample course, the shelf stays visible and offers
`Add the sample course`. The action uses the existing shelf route and sample
writer, then returns to the shelf.

## Verification

- `python3 tests/course_shell_roundtrip.py`: passed.
- `python3 tests/ia_route_roundtrip.py`: passed with the current working tree.
- `python3 tests/presentation_roundtrip.py`: passed with the current working
  tree.

This packet does not change course identity, scoring, assessment disclosure,
or stored navigation preferences.
