#!/usr/bin/env python3
"""The surface grid stays honest: every command and every route is
classified, and every empty cell says what it costs.

`tools/surface_coverage.py` is only worth trusting if it cannot go stale.
Two ways it could: a command or a route lands and nobody classifies it, so
it sits in a blind spot the report reads as coverage; or a cell is left
empty with no note, so the report says a gap exists and not what it costs.
Both fail here.

This does not assert HOW MANY cells are reached. That number is supposed to
move, and pinning it would turn every new door into a test edit.

Standard library only, runnable as `python tests/surface_coverage_check.py`.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))

import surface_coverage as sc                                # noqa: E402

FAILURES = []


def fail(msg):
    print("FAIL: " + msg)
    FAILURES.append(msg)


def check_every_command_and_route_is_classified():
    data = sc.report()
    for key, what in (
            ("unclassified_commands", "command"),
            ("unclassified_routes", "route")):
        for name in data[key]:
            fail("%s %r is in no cell and is not named in NOT_A_CAPABILITY; "
                 "a surface nobody classified reads as coverage it does not "
                 "have" % (what, name))
    for key, what in (("phantom_commands", "command"),
                      ("phantom_routes", "route")):
        for name in data[key]:
            fail("a cell claims %s %r, which the shipped surface does not "
                 "have; the grid must name what is there" % (what, name))


def check_every_gap_states_its_cost():
    data = sc.report()
    for row in data["grid"]:
        for verb in sc.VERBS:
            cell = row["cells"][verb]
            if cell["reached"] or not cell["meaningful"]:
                continue
            if not cell["note"].strip():
                fail("%s / %s is empty and says nothing about what that "
                     "costs; a gap with no consequence recorded is a gap "
                     "nobody can prioritise" % (row["object"], verb))


def check_not_meaningful_cells_carry_a_reason():
    for (obj, verb), reason in sc.NOT_MEANINGFUL.items():
        if obj not in sc.OBJECTS:
            fail("NOT_MEANINGFUL names object %r, which is not in OBJECTS"
                 % obj)
        if verb not in sc.VERBS:
            fail("NOT_MEANINGFUL names verb %r, which is not in VERBS" % verb)
        if len(reason.split()) < 4:
            fail("%s / %s is excused in four words or fewer; 'does not "
                 "apply' is a claim that needs a sentence" % (obj, verb))
    for (obj, verb) in sc.CELLS:
        if (obj, verb) in sc.NOT_MEANINGFUL:
            fail("%s / %s is both reached and declared not meaningful"
                 % (obj, verb))


def main():
    check_every_command_and_route_is_classified()
    check_every_gap_states_its_cost()
    check_not_meaningful_cells_carry_a_reason()
    if FAILURES:
        print("SURFACE COVERAGE: %d failure(s)" % len(FAILURES))
        return 1
    data = sc.report()
    print("ok: surface coverage -- %d commands and %d routes all classified, "
          "%d of %d meaningful cells reached, every one of the %d empty cells "
          "states its cost"
          % (len(data["commands_measured"]), len(data["routes_measured"]),
             data["cells_reached"], data["cells_meaningful"],
             data["cells_meaningful"] - data["cells_reached"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
