#!/usr/bin/env python3
"""Phase 16C (16C-05) strategy precedence roundtrip.

Direct standard-library roundtrip script in the project's established shape:
`fail(msg)` and a non-zero exit on failure. It proves STRATEGY-02: the
composed resolver is a COLLECTOR over 16B's one precedence function, the
conflict sentence is 16B's own output and is never rebuilt from parts here,
the picker's locked rows carry that sentence verbatim, and during a sitting a
learner preference is refused with the locked line rather than losing a
conflict.

The degraded state this file exists to prove is the mid-sitting refusal: with
a sitting active the effective value does not move and the lock says why.

The structural check that matters most is `check_no_second_implementation`.
Two implementations of one precedence contract drift, and the one that drifts
is always the newer one, so this file asserts the newer one does not exist.
"""
import ast
import inspect
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import strategies
from surfaces import ia

FAILURES = []


def fail(msg):
    print("FAIL: %s" % msg)
    FAILURES.append(msg)


def check_collector_shape():
    """Every behavior-block case, including the empty input and the
    propagated ValueError."""
    result = strategies.composed_resolve(
        {"Strategy": {"learner_preference": "retrieval_first",
                      "instructor_policy": "continuous_reading"}})
    if result["effective"].get("Strategy") != "continuous_reading":
        fail("the higher layer did not win: %r" % (result["effective"],))
    if len(result["conflicts"]) != 1:
        fail("expected one conflict, got %r" % (result["conflicts"],))
    else:
        expected = ia.mode_layer_conflict_copy("Strategy",
                                               "instructor_policy")
        if result["conflicts"][0]["copy"] != expected:
            fail("the conflict sentence is %r, expected 16B's %r"
                 % (result["conflicts"][0]["copy"], expected))

    result = strategies.composed_resolve(
        {"Strategy": {"learner_preference": "guided_note_spine"}})
    if result["effective"].get("Strategy") != "guided_note_spine":
        fail("an uncontested preference did not survive: %r" % (result,))
    if result["conflicts"] or result["locks"]:
        fail("an uncontested preference produced %r" % (result,))

    empty = strategies.composed_resolve({})
    if empty != {"effective": {}, "conflicts": [], "locks": []}:
        fail("the empty case returned %r" % (empty,))

    try:
        strategies.composed_resolve({"Strategy": {"not_a_layer": "x"}})
    except ValueError as exc:
        if "not_a_layer" not in str(exc):
            fail("the propagated error was re-worded: %s" % exc)
    else:
        fail("an unknown layer key was swallowed")


def check_strategy_conflict_matrix():
    """The STRATEGY-02 matrix: a learner preference contradicted by an
    accommodation override and by an instructor policy."""
    matrix = {
        "Learning strategy (accommodation case)": {
            "learner_preference": "retrieval_first",
            "accommodation_override": "continuous_reading"},
        "Learning strategy (policy case)": {
            "learner_preference": "retrieval_first",
            "instructor_policy": "guided_note_spine"},
    }
    result = strategies.composed_resolve(matrix)
    wanted = {"Learning strategy (accommodation case)":
              ("accommodation_override", "continuous_reading"),
              "Learning strategy (policy case)":
              ("instructor_policy", "guided_note_spine")}
    if len(result["conflicts"]) != 2:
        fail("expected two conflicts, got %r" % (result["conflicts"],))
    for conflict in result["conflicts"]:
        layer, value = wanted[conflict["setting"]]
        if conflict["winning_layer"] != layer:
            fail("%s resolved to %r, expected %r"
                 % (conflict["setting"], conflict["winning_layer"], layer))
        if result["effective"][conflict["setting"]] != value:
            fail("%s produced %r, expected %r"
                 % (conflict["setting"],
                    result["effective"][conflict["setting"]], value))
        expected = ia.mode_layer_conflict_copy(conflict["setting"], layer)
        if conflict["copy"] != expected:
            fail("%s carried %r, expected 16B's %r"
                 % (conflict["setting"], conflict["copy"], expected))
        # 16B's substitution rule: the rendered sentence names the layer in
        # words a learner reads, never the internal key.
        if "_" in conflict["copy"]:
            fail("the sentence leaked an internal key: %r" % conflict["copy"])
        if layer in conflict["copy"]:
            fail("the sentence names the layer key %r verbatim" % layer)


def check_mid_sitting_lock():
    """During a sitting the preference never reaches the resolver."""
    state = {"Strategy": {"learner_preference": "guided_note_spine",
                          "runtime_authority": "continuous_reading"}}
    locked = strategies.composed_resolve(state, sitting_active=True)
    open_ = strategies.composed_resolve(state, sitting_active=False)

    if locked["effective"].get("Strategy") != "continuous_reading":
        fail("the pinned value moved during a sitting: %r"
             % (locked["effective"],))
    if len(locked["locks"]) != 1:
        fail("expected one lock, got %r" % (locked["locks"],))
    elif locked["locks"][0]["copy"] != \
            "Strategy changes are paused during a test sitting.":
        fail("the lock sentence is %r" % locked["locks"][0]["copy"])
    if locked["conflicts"]:
        fail("a refused request must not also render as a conflict: %r"
             % (locked["conflicts"],))

    # With the sitting over, the same state takes the ordinary conflict path
    # and reaches the same effective value by a different route.
    if open_["effective"].get("Strategy") != "continuous_reading":
        fail("the open case resolved to %r" % (open_["effective"],))
    if not open_["conflicts"]:
        fail("the open case must render a conflict, not a lock")
    if open_["locks"]:
        fail("the open case must carry no lock: %r" % (open_["locks"],))
    print("  mid-sitting: locked=%r open=%r"
          % (locked["effective"]["Strategy"], open_["effective"]["Strategy"]))


def check_no_second_implementation():
    """16C must not reimplement precedence (16B D8, 16C-DECISIONS D-16C-5)."""
    src = inspect.getsource(strategies.composed_resolve)
    for forbidden in ("MODE_LAYERS", "MODE_LAYERS_FIXED", "index(",
                      "MODE_LAYER_CONFLICT_TEMPLATE"):
        if forbidden in src:
            fail("composed_resolve reads %r; precedence lives in "
                 "surfaces/ia.py alone (16B D8, D-16C-5)" % forbidden)

    module_src = open(os.path.join(ROOT, "strategies.py"),
                      encoding="utf-8").read()
    tree = ast.parse(module_src)
    allowed = {"composed_resolve", "locked_picker_copy"}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                                 ast.ClassDef)):
            continue
        lowered = node.name.lower()
        if node.name in allowed:
            continue
        for shape in ("mode_layer", "layer_order", "precedence_table",
                      "precedence"):
            if shape in lowered:
                fail("strategies.py defines %r, a precedence-shaped name; "
                     "one precedence rule exists and it is 16B's "
                     "(D8, D-16C-5)" % node.name)

    # The conflict sentence is never built here: no format string in this
    # module may carry the template's substitutions.
    for marker in ("is set by", "can't be changed here"):
        if marker in module_src:
            fail("strategies.py contains %r; the conflict sentence comes "
                 "from ia.mode_layer_conflict_copy alone" % marker)


def check_picker_locked_rows():
    """A disallowed strategy's row carries the resolver's sentence."""
    # A same-value request is no conflict, so the case has to be a real
    # disagreement: the instructor pins retrieval_first for this setting and
    # the learner asked for something else, which is what makes the row
    # locked rather than merely unselected.
    state = {"Retrieval first": {"learner_preference": "guided_note_spine",
                                 "instructor_policy": "retrieval_first"}}
    result = strategies.composed_resolve(state)
    locked_copy = strategies.locked_picker_copy(result["conflicts"])
    if "retrieval_first" not in locked_copy:
        fail("locked_picker_copy produced %r" % (locked_copy,))
        return
    allowed = tuple(s for s in strategies.STRATEGY_IDS
                    if s != "retrieval_first")
    rows = dict((r["strategy_id"], r) for r in strategies.picker_rows(
        strategies.STRATEGY_IDS, allowed, locked_copy))
    row = rows["retrieval_first"]
    if row["row_class"] != "locked":
        fail("the disallowed row read %r" % row["row_class"])
    expected = ia.mode_layer_conflict_copy("Retrieval first",
                                           "instructor_policy")
    if row["copy"] != expected:
        fail("the locked row carried %r, expected %r" % (row["copy"],
                                                         expected))
    if not row["copy"]:
        fail("16C-03's empty-copy interim state is still reachable")


def main():
    checks = [check_collector_shape, check_strategy_conflict_matrix,
              check_mid_sitting_lock, check_no_second_implementation,
              check_picker_locked_rows]
    for check in checks:
        check()
    failed = len(FAILURES)
    print("STRATEGY PRECEDENCE: %d passed, %d failed"
          % (len(checks) - failed, failed))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
