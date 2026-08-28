#!/usr/bin/env python3
"""The Phase 16A activity-declaration unit check (plan 16A-06 Tasks 1 and 2).

ACTIVITY-01 says every activity declares ten things, that existing response
forms serve many purposes, and that an unsupported response form falls back to
its declared static equivalent. This file asserts the parser and the eleven
lint checks behind that: the six closed vocabularies, the four probe rows
ACTIVITY-01 returned (adjacency, empty, ordering, idempotency), that a
malformed registry never raises, and that each of the eleven codes fires on
exactly the row that should produce it and lands on the right side of the
error/warning split.

Standard library only, no test framework, runnable as
`python tests/activity_declaration_check.py`.
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import capabilities                                          # noqa: E402
import model                                                 # noqa: E402

LESSON_BANK = os.path.join(ROOT, "fixtures", "lesson_bank.md")

# One well-formed row, as a list of the ten cells after the item id. Every
# test bank below starts from this and breaks exactly one cell, so a finding
# can only come from the thing that was broken.
GOOD_CELLS = [
    "retrieval",
    "recall a stated definition without the source in view",
    "nav:tides.recall",
    "No stimulus; the learner works from memory",
    "short",
    "none",
    "after_commitment",
    "pending_human_mark",
    "A labelled text area reachable in document order.",
    "Say the definition out loud, then check it against the glossary.",
]

ITEM_BLOCK = """
Q1. State what a turning point on an invented tide table is.   (difficulty: recall)
[OBJECTIVE: nav:tides.recall]
[TYPE: short]
MODEL: A listed moment when the water stops rising or falling and reverses.
RUBRIC:
- names the reversal of direction
- states that the row fixes a height at that moment only

TRAP: Describing a turning point as the highest point of the day.

CONFIDENCE: high
"""


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def _bank(rows, header=True, item_block=ITEM_BLOCK):
    """Write a temporary bank carrying a `## ACTIVITIES` section built from
    `rows`, and return its path. `rows` are already-joined pipe rows."""
    tmp = tempfile.mkdtemp(prefix="activity-check-")
    path = os.path.join(tmp, "activity_bank.md")
    parts = ["# Activity check bank (synthetic)\n"]
    if header:
        parts.append("## ACTIVITIES\n")
        for row in rows:
            parts.append(row)
        parts.append("")
    parts.append(item_block)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(parts))
    return path


def _row(item="q1", **overrides):
    cells = list(GOOD_CELLS)
    for column, value in overrides.items():
        cells[model.ACTIVITY_COLUMNS.index(column) - 1] = value
    return " | ".join([item] + cells)


def _codes(path):
    parsed = model.parse_activities(path)
    errors, warnings = model.lint(model.load(path), activities=parsed)
    return ([e.code for e in errors if e.code.startswith("activity.")],
            [w.code for w in warnings if w.code.startswith("activity.")])


def check_vocabularies():
    expected = {
        "ACTIVITY_COLUMNS": ("item", "purpose", "demand", "objective",
                             "stimulus", "response_schema", "retry",
                             "feedback", "evidence", "a11y_equivalent",
                             "static_fallback"),
        "ACTIVITY_PURPOSES": ("prediction", "noticing", "retrieval",
                              "explanation", "comparison", "diagnosis",
                              "practice", "transfer", "reflection",
                              "formal_assessment"),
        "ACTIVITY_RETRY": ("none", "unlimited", "until_correct",
                           "mode_controlled"),
        "ACTIVITY_FEEDBACK": ("immediate", "after_commitment", "staged",
                              "withheld_until_submit", "non_evaluative"),
        "ACTIVITY_EVIDENCE_STATES": ("not_recorded", "activity_trace",
                                     "scored_by_runtime",
                                     "pending_human_mark"),
        "RESPONSE_FORMS": ("mc", "multi", "table", "dnd", "build", "short",
                           "check", "visual"),
    }
    for name, want in expected.items():
        got = getattr(model, name)
        if got != want:
            fail("model.%s is %r, expected %r" % (name, got, want))


def check_absent_section():
    """The degraded path: a bank with no ## ACTIVITIES section."""
    if model.parse_activities(LESSON_BANK) is not None:
        fail("parse_activities returned something for a bank with no "
             "## ACTIVITIES section")
    plain = model.lint(model.load(LESSON_BANK))
    with_arg = model.lint(model.load(LESSON_BANK),
                          activities=model.parse_activities(LESSON_BANK))
    if [str(e) for e in plain[0]] != [str(e) for e in with_arg[0]] \
            or [str(w) for w in plain[1]] != [str(w) for w in with_arg[1]]:
        fail("passing activities data changed the lint output of a bank that "
             "declares no activities, so the addition was not additive")


def check_empty_block():
    """ACTIVITY-01's empty probe: a section with a header row and no data."""
    path = _bank([])
    parsed = model.parse_activities(path)
    if parsed is None:
        fail("a ## ACTIVITIES section with no rows parsed to None; absent and "
             "empty are different states and must stay distinguishable")
    if parsed["empty"] is not True:
        fail("a ## ACTIVITIES section with no rows did not report empty")
    if parsed["activities"] or parsed["order"]:
        fail("an empty section produced declarations")
    errors, warnings = _codes(path)
    if warnings != ["activity.empty_block"] or errors:
        fail("an empty section produced %r / %r, expected exactly the "
             "activity.empty_block warning" % (errors, warnings))


def check_duplicate_item():
    """ACTIVITY-01's adjacency probe: two rows naming one item."""
    first = _row(purpose="retrieval")
    second = _row(purpose="reflection", feedback="non_evaluative")
    path = _bank([first, second])
    parsed = model.parse_activities(path)
    if parsed["duplicates"] != ["q1"]:
        fail("two rows naming q1 produced duplicates %r, expected ['q1']"
             % parsed["duplicates"])
    if parsed["activities"]["q1"]["purpose"] != "retrieval":
        fail("the second declaration won; the first registration must win "
             "and the two field sets must never be merged")
    if parsed["activities"]["q1"]["feedback"] != "after_commitment":
        fail("a field from the second declaration leaked into the first, so "
             "the two rows were merged")
    errors, _warnings = _codes(path)
    if "activity.duplicate_item" not in errors:
        fail("a duplicate item id produced no activity.duplicate_item error")


def check_document_order():
    """ACTIVITY-01's ordering probe: two rows sharing a purpose keep the
    order their author wrote them in."""
    path = _bank([_row(item="q9"), _row(item="q1")],
                 item_block=ITEM_BLOCK + ITEM_BLOCK.replace("Q1.", "Q2."))
    parsed = model.parse_activities(path)
    if parsed["order"] != ["q9", "q1"]:
        fail("order is %r, expected document order ['q9', 'q1']; sorting the "
             "registry would discard information the author supplied"
             % parsed["order"])


def check_idempotent_and_pure():
    """ACTIVITY-01's idempotency probe, and its concurrency backstop: two
    calls return equal dicts and nothing is written."""
    path = _bank([_row()])
    before = sorted(os.listdir(os.path.dirname(path)))
    first = model.parse_activities(path)
    second = model.parse_activities(path)
    if first != second:
        fail("two parse_activities calls on an unchanged file returned "
             "different dicts")
    if sorted(os.listdir(os.path.dirname(path))) != before:
        fail("parse_activities wrote something; it is a pure read and an "
             "interrupted parse must have nothing durable to leave behind")


def check_malformed_never_raises():
    cases = {
        "one cell": "q1",
        "twenty cells": " | ".join(["q1"] + ["x"] * 19),
        "unknown item": _row(item="q404"),
        "empty everything": " | ".join(["q1"] + [""] * 10),
    }
    for label, row in cases.items():
        path = _bank([row])
        try:
            parsed = model.parse_activities(path)
        except Exception as exc:                             # noqa: BLE001
            fail("a %s row raised %s; a malformed row is lint's problem and "
                 "never a parse failure" % (label, exc))
        if not isinstance(parsed, dict):
            fail("a %s row parsed to %r, expected a dict" % (label, parsed))
        for item, activity in parsed["activities"].items():
            if tuple(sorted(activity)) != tuple(sorted(model.ACTIVITY_COLUMNS)):
                fail("a %s row produced the key set %s for %r, expected "
                     "exactly ACTIVITY_COLUMNS"
                     % (label, sorted(activity), item))
        try:
            _codes(path)
        except Exception as exc:                             # noqa: BLE001
            fail("linting a %s row raised %s" % (label, exc))


def check_every_code_fires():
    """One bank per code, each breaking exactly one cell, so a finding can
    only come from the thing that was broken."""
    cases = [
        ("activity.item_unknown", _row(item="q404"), "errors"),
        ("activity.unknown_purpose", _row(purpose="vibing"), "errors"),
        ("activity.demand_empty", _row(demand="  "), "errors"),
        ("activity.unknown_retry", _row(retry="sometimes"), "errors"),
        ("activity.unknown_feedback", _row(feedback="eventually"), "errors"),
        ("activity.unknown_evidence_state", _row(evidence="mixed"), "errors"),
        ("activity.missing_static_fallback", _row(static_fallback=""),
         "errors"),
        ("activity.missing_a11y_equivalent", _row(a11y_equivalent=""),
         "errors"),
        ("activity.unsupported_response_form",
         _row(response_schema="oral_explanation"), "warnings"),
    ]
    for code, row, side in cases:
        errors, warnings = _codes(_bank([row]))
        found = errors if side == "errors" else warnings
        other = warnings if side == "errors" else errors
        if found != [code]:
            fail("the %s case produced %s %r, expected exactly [%r]"
                 % (code, side, found, code))
        if other:
            fail("the %s case also produced %r on the other side of the "
                 "error/warning split" % (code, other))


def check_split_is_deliberate():
    """`activity.unsupported_response_form` is a warning because falling back
    is the declared behavior ACTIVITY-01 names, not a defect.
    `activity.empty_block` is a warning because `terms.empty_block` is."""
    _errors, warnings = _codes(
        _bank([_row(response_schema="oral_explanation")]))
    if "activity.unsupported_response_form" not in warnings:
        fail("an unsupported response form is an error; ACTIVITY-01's "
             "Degraded clause makes falling back the declared behavior, so "
             "it is a warning")


def check_activity_fallback():
    supported = {"response_schema": "mc",
                 "static_fallback": "Read the printed version."}
    if capabilities.activity_fallback(supported) != "":
        fail("activity_fallback returned text for a supported response form")
    unsupported = {"response_schema": "oral_explanation",
                   "static_fallback": "Say it out loud, then compare."}
    if capabilities.activity_fallback(unsupported) \
            != "Say it out loud, then compare.":
        fail("activity_fallback did not return the declared static fallback "
             "for an unsupported response form")
    for junk in (None, "", [], {}):
        if capabilities.activity_fallback(junk) != "":
            fail("activity_fallback returned something for %r" % (junk,))


CHECKS = (check_vocabularies, check_absent_section, check_empty_block,
          check_duplicate_item, check_document_order,
          check_idempotent_and_pure, check_malformed_never_raises,
          check_every_code_fires, check_split_is_deliberate,
          check_activity_fallback)


def main():
    for check in CHECKS:
        check()
    print("activity declarations ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
