#!/usr/bin/env python3
"""Phase 16C (16C-03) strategy registry roundtrip.

Direct standard-library roundtrip script in the project's established shape:
`fail(msg)` and a non-zero exit on failure. It proves STRATEGY-01's registry
and its degraded path: four strategies as complete versioned data records, a
code-owned fallback that never raises, evidence effects confined to the two
D-16C-1 lifecycle types, an accessibility equivalent for every required
action, and a picker that renders exactly three row classes and never invents
a fifth option.

The degraded state this file exists to prove is the fallback: an unknown, an
unavailable, and a disallowed strategy all resolve to continuous reading,
and the picker says which case it was in the learner's own words.
"""
import ast
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import strategies

FAILURES = []


def fail(msg):
    print("FAIL: %s" % msg)
    FAILURES.append(msg)


def check_registry_shape():
    """Four ids, one fallback, eleven keys each, and no evidence effect
    outside the two lifecycle types."""
    if strategies.STRATEGY_IDS != ("continuous_reading", "guided_note_spine",
                                   "worked_reasoning", "retrieval_first"):
        fail("STRATEGY_IDS is %r" % (strategies.STRATEGY_IDS,))
    if strategies.FALLBACK_STRATEGY != "continuous_reading":
        fail("FALLBACK_STRATEGY is %r" % (strategies.FALLBACK_STRATEGY,))
    if set(strategies.STRATEGY_CONTRACTS) != set(strategies.STRATEGY_IDS):
        fail("the contract set does not match the id set")

    keys = set(strategies.CONTRACT_KEYS)
    if len(keys) != 11:
        fail("CONTRACT_KEYS holds %d keys, expected 11" % len(keys))
    for strategy_id in strategies.STRATEGY_IDS:
        contract = strategies.strategy_contract(strategy_id)
        if set(contract) != keys:
            fail("%s carries %r" % (strategy_id, sorted(contract)))
        for key, value in contract.items():
            # required_actions and optional_actions are legitimately empty
            # for a strategy that asks nothing of the learner; every other
            # field must say something.
            if key in ("required_actions", "optional_actions"):
                continue
            if not value:
                fail("%s.%s is empty" % (strategy_id, key))
        if contract["strategy_id"] != strategy_id:
            fail("%s names itself %r" % (strategy_id,
                                         contract["strategy_id"]))
        for effect in contract["evidence_effects"]:
            if effect not in strategies.LIFECYCLE_EVENT_TYPES:
                fail("%s declares evidence effect %r, outside the two "
                     "D-16C-1 lifecycle types" % (strategy_id, effect))
        if not str(contract["tests"][0]).startswith("tests/"):
            fail("%s does not name a test file" % strategy_id)

    # A returned contract is a copy: annotating one must not edit the
    # registry for the next caller.
    mutated = strategies.strategy_contract("guided_note_spine")
    mutated["learning_purpose"] = "edited by a caller"
    mutated["accommodations"]["select_target"] = "edited by a caller"
    fresh = strategies.strategy_contract("guided_note_spine")
    if fresh["learning_purpose"] == "edited by a caller" \
            or fresh["accommodations"]["select_target"] == "edited by a caller":
        fail("strategy_contract returned a live reference, not a copy")

    try:
        strategies.strategy_contract("close_reading")
    except ValueError as exc:
        if "close_reading" not in str(exc):
            fail("the unknown-strategy error does not name the id: %s" % exc)
    else:
        fail("strategy_contract accepted an unregistered strategy")

    # The tier rule, asserted over the source rather than over what happens
    # to be imported. A strategy influences presentation, never settlement.
    tree = ast.parse(open(os.path.join(ROOT, "strategies.py"),
                         encoding="utf-8").read())
    forbidden = ("runtime", "evidence", "notes")
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [node.module or ""]
        else:
            continue
        for name in names:
            head = name.split(".")[0]
            if head in forbidden or head == "surfaces":
                fail("strategies.py imports %s; the tier rule forbids it"
                     % name)


def check_fallback():
    """Every degraded case returns continuous reading and raises nothing."""
    ids = strategies.STRATEGY_IDS
    cases = [
        ("unavailable", "worked_reasoning", ("continuous_reading",), ids,
         "continuous_reading"),
        ("disallowed", "retrieval_first", ids,
         ("continuous_reading", "guided_note_spine"), "continuous_reading"),
        ("unknown", "not_a_strategy", ids, ids, "continuous_reading"),
        ("allowed and available", "guided_note_spine", ids, ids,
         "guided_note_spine"),
        ("empty availability", "guided_note_spine", (), ids,
         "continuous_reading"),
    ]
    for label, requested, available, allowed, expected in cases:
        try:
            got = strategies.resolve_strategy(requested, available, allowed)
        except Exception as exc:
            fail("resolve_strategy raised on the %s case: %r" % (label, exc))
            continue
        if got != expected:
            fail("the %s case resolved to %r, expected %r"
                 % (label, got, expected))
    for strategy_id in ids:
        if strategies.resolve_strategy(strategy_id, ids, ids) != strategy_id:
            fail("%s did not survive a fully permissive resolve"
                 % strategy_id)


def check_accessibility_equivalents():
    """No required action is drag-only, hover-only, or pointer-only."""
    for strategy_id in strategies.STRATEGY_IDS:
        contract = strategies.strategy_contract(strategy_id)
        accommodations = contract["accommodations"]
        for action in contract["required_actions"]:
            entry = accommodations.get(action, "")
            if not entry:
                fail("%s requires %r with no accommodation named"
                     % (strategy_id, action))
                continue
            if "keyboard" not in entry and "structured" not in entry \
                    and "tab order" not in entry:
                fail("%s.%s names no keyboard path: %r"
                     % (strategy_id, action, entry))
        for action in contract["optional_actions"]:
            if not accommodations.get(action, ""):
                fail("%s offers %r with no accommodation named"
                     % (strategy_id, action))


def check_picker_rows():
    """Three row classes, registry order, and never a fifth row."""
    ids = strategies.STRATEGY_IDS
    if strategies.PICKER_HEADING != "How do you want to work through this?":
        fail("PICKER_HEADING is %r" % (strategies.PICKER_HEADING,))
    if strategies.PICKER_ROW_CLASSES != ("choosable", "fallback", "locked"):
        fail("PICKER_ROW_CLASSES is %r" % (strategies.PICKER_ROW_CLASSES,))

    rows = strategies.picker_rows(ids, ids)
    if [r["strategy_id"] for r in rows] != list(ids):
        fail("the picker reordered the registry: %r"
             % [r["strategy_id"] for r in rows])
    if any(r["row_class"] != "choosable" for r in rows):
        fail("a fully available registry produced a non-choosable row")
    if [r["preselected"] for r in rows] != [True, False, False, False]:
        fail("the first choosable row must be preselected: %r"
             % [r["preselected"] for r in rows])
    for row in rows:
        if row["name"] != strategies.STRATEGY_NAMES[row["strategy_id"]] \
                or row["purpose"] != \
                strategies.STRATEGY_PURPOSES[row["strategy_id"]]:
            fail("row %r does not carry the locked name and purpose"
                 % row["strategy_id"])

    without = tuple(s for s in ids if s != "worked_reasoning")
    rows = dict((r["strategy_id"], r)
                for r in strategies.picker_rows(without, ids))
    row = rows["worked_reasoning"]
    if row["row_class"] != "fallback":
        fail("an unavailable strategy read %r" % row["row_class"])
    if row["copy"] != ("Worked reasoning isn't available right now. "
                       "Continuing with continuous reading."):
        fail("the unavailable sentence is %r" % row["copy"])
    if not rows["continuous_reading"]["preselected"]:
        fail("a degraded picker must preselect continuous reading")
    if rows["worked_reasoning"]["preselected"]:
        fail("an unavailable row must never be preselected")

    locked_sentence = ("Retrieval first is set by your instructor's policy "
                       "for this course and can't be changed here.")
    rows = dict((r["strategy_id"], r) for r in strategies.picker_rows(
        ids, tuple(s for s in ids if s != "retrieval_first"),
        {"retrieval_first": locked_sentence}))
    row = rows["retrieval_first"]
    if row["row_class"] != "locked":
        fail("a disallowed strategy read %r" % row["row_class"])
    if row["copy"] != locked_sentence:
        fail("the locked row did not carry the supplied sentence verbatim: "
             "%r" % row["copy"])
    if row["preselected"]:
        fail("a locked row must never be preselected")

    # A disallowed strategy is shown, not hidden (D8), even with no sentence
    # supplied yet.
    rows = strategies.picker_rows(ids, tuple(s for s in ids
                                             if s != "retrieval_first"))
    if len(rows) != len(ids):
        fail("a disallowed strategy was hidden rather than explained")

    # A bogus id inside `available` never becomes a row.
    rows = strategies.picker_rows(ids + ("close_reading",), ids)
    if [r["strategy_id"] for r in rows] != list(ids):
        fail("the picker invented a row: %r"
             % [r["strategy_id"] for r in rows])


def check_mid_sitting_copy():
    """The sitting lock line is locked copy here; 16C-05 wires the logic."""
    if strategies.MID_SITTING_LOCK_COPY != \
            "Strategy changes are paused during a test sitting.":
        fail("MID_SITTING_LOCK_COPY is %r"
             % (strategies.MID_SITTING_LOCK_COPY,))
    if strategies.UNAVAILABLE_COPY != ("{Strategy name} isn't available "
                                       "right now. Continuing with "
                                       "continuous reading."):
        fail("UNAVAILABLE_COPY is %r" % (strategies.UNAVAILABLE_COPY,))
    names = {"continuous_reading": "Continuous reading",
             "guided_note_spine": "Guided note spine",
             "worked_reasoning": "Worked reasoning",
             "retrieval_first": "Retrieval first"}
    purposes = {
        "continuous_reading": "Read straight through, with optional highlights and notes.",
        "guided_note_spine": "Prompted selection and restatement as you go.",
        "worked_reasoning": "Predict, explain, and self-check worked steps.",
        "retrieval_first": "Try questions first, then read what you missed.",
    }
    if strategies.STRATEGY_NAMES != names:
        fail("STRATEGY_NAMES is %r" % (strategies.STRATEGY_NAMES,))
    if strategies.STRATEGY_PURPOSES != purposes:
        fail("STRATEGY_PURPOSES is %r" % (strategies.STRATEGY_PURPOSES,))


def main():
    checks = [check_registry_shape, check_fallback,
              check_accessibility_equivalents, check_picker_rows,
              check_mid_sitting_copy]
    for check in checks:
        check()
    failed = len(FAILURES)
    print("STRATEGY REGISTRY: %d passed, %d failed"
          % (len(checks) - failed, failed))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
