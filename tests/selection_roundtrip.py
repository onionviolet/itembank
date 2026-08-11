#!/usr/bin/env python3
"""The selection engine's round-trip contract (phase 7).

One selector (`selection.select(questions, spec, history) -> (items, trace)`)
is the only place an item is chosen, reachable from `itembank start` and
`POST /api/start` alike. This suite pins the tracer behaviours plan 07-01
shipped (objective filter, determinism, a trace that names a runner-up, and a
trace that leaks no answer key), and declares the checks later plans in the
phase will fill in.

Standard library only, runnable as `python tests/selection_roundtrip.py`.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import model                                                # noqa: E402
import schema_validate                                      # noqa: E402
import selection                                            # noqa: E402

BANK = os.path.join(ROOT, "fixtures", "selection_bank.md")
HISTORY = os.path.join(ROOT, "fixtures", "selection_evidence.jsonl")
RESPONSE_SCHEMA = os.path.join(ROOT, "schemas", "response.schema.json")


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


# A declared check a later plan owns. Runs green from this commit; the owning
# plan replaces the body with a real assertion. A lambda (not a def) so the
# pending call-site count in the plan's acceptance grep is exact.
pending = lambda name, plan: print("skip %s (filled by plan %s)" % (name, plan))


def check_fixture_lints_clean():
    qs = model.load(BANK)
    errors, warnings = model.lint(qs)
    if errors:
        fail("fixture bank has lint errors: %r" % errors)
    if warnings:
        fail("fixture bank has lint warnings: %r" % warnings)
    print("check_fixture_lints_clean: %d items, 0 errors, 0 warnings" % len(qs))


def check_fixture_history_matches_response_schema():
    schema = json.load(open(RESPONSE_SCHEMA, encoding="utf-8"))
    seen = 0
    for line_no, line in enumerate(open(HISTORY, encoding="utf-8"), 1):
        ev = json.loads(line)
        if ev.get("event_type") != "response":
            continue
        seen += 1
        errs = schema_validate.validate(ev, schema)
        if errs:
            fail("history line %d fails the response schema: %s"
                 % (line_no, "; ".join(errs)))
    if seen == 0:
        fail("history file carries no response events")
    print("check_fixture_history_matches_response_schema: %d events valid" % seen)


def check_objective_filter():
    qs = model.load(BANK)
    items, _ = selection.select(
        qs, {"objective": "water:regulatory.reporting", "count": 30, "seed": 0},
        history=[])
    if len(items) != 7:
        fail("objective filter returned %d items, expected the fixture's 7"
             % len(items))
    for q in items:
        if q.get("objective") != "water:regulatory.reporting":
            fail("objective filter returned %r on objective %r"
                 % (q["id"], q.get("objective")))
    print("check_objective_filter: 7/7 on water:regulatory.reporting")


def check_determinism():
    qs = model.load(BANK)
    spec = {"objective": "", "count": 8, "seed": 42}
    first, _ = selection.select(qs, spec, history=[])
    second, _ = selection.select(qs, spec, history=[])
    a = [q["id"] for q in first]
    b = [q["id"] for q in second]
    if a != b:
        fail("same bank/spec/history/seed produced different orders: %r vs %r"
             % (a, b))
    third, _ = selection.select(
        qs, {"objective": "", "count": 8, "seed": 43}, history=[])
    c = [q["id"] for q in third]
    if c == a:
        fail("a different seed produced the same order -- the seed is ignored")
    print("check_determinism: seed 42 stable, seed 43 differs")


def check_trace_names_runner_up():
    qs = model.load(BANK)
    _, trace = selection.select(
        qs, {"objective": "water:regulatory.reporting", "count": 3, "seed": 5},
        history=[])
    for block in trace["chosen"]:
        reason = block.get("reason") or ""
        runner_up = block.get("runner_up")
        if not reason or len(reason) < 20 or " " not in reason:
            fail("%s: reason is not plain prose: %r" % (block["item_ref"], reason))
        if runner_up is None:
            fail("%s: no runner-up named although the pool exceeds the count"
                 % block["item_ref"])
        if runner_up["item_ref"] == block["item_ref"]:
            fail("%s: runner-up is the item itself" % block["item_ref"])
        if not runner_up.get("reason"):
            fail("%s: runner-up has no reason" % block["item_ref"])
    print("check_trace_names_runner_up: %d blocks name a distinct runner-up"
          % len(trace["chosen"]))


def check_trace_leaks_no_key():
    qs = model.load(BANK)
    _, trace = selection.select(
        qs, {"objective": "", "count": len(qs), "seed": 1}, history=[])
    rendered = json.dumps(trace, ensure_ascii=False)
    for q in qs:
        tag = q["id"]
        if q["type"] in ("mc", "multi"):
            for letter in q["correct"]:
                if ('"%s"' % letter) in rendered:
                    fail("%s: trace carries the correct letter %s as a value"
                         % (tag, letter))
        for field in ("why", "disc", "second", "trap"):
            text = q.get(field) or ""
            if text and text in rendered:
                fail("%s: trace leaks the %s rationale" % (tag, field))
        for letter, opt in (q.get("opts") or {}).items():
            if opt and opt in rendered:
                fail("%s: trace leaks option %s text" % (tag, letter))
    print("check_trace_leaks_no_key: no key, rationale, or option text leaked")


def check_pair_served_together():
    pending("check_pair_served_together", "07-02")


def check_prereq_filter():
    pending("check_prereq_filter", "07-02")


def check_pair_singleton_lint():
    pending("check_pair_singleton_lint", "07-02")


def check_prereq_unknown_lint():
    pending("check_prereq_unknown_lint", "07-02")


def check_selection_mode_recorded():
    pending("check_selection_mode_recorded", "07-04")


def check_selection_spec_recorded():
    pending("check_selection_spec_recorded", "07-04")


def check_mode_compositions_differ():
    pending("check_mode_compositions_differ", "07-05")


def check_cooldown_survives_resume():
    pending("check_cooldown_survives_resume", "07-05")


def check_cooldown_is_bank_scoped():
    pending("check_cooldown_is_bank_scoped", "07-05")


def check_explain_renders_plain_text():
    pending("check_explain_renders_plain_text", "07-06")


def check_preview_writes_no_session():
    pending("check_preview_writes_no_session", "07-06")


def check_profile_flags_override():
    pending("check_profile_flags_override", "07-06")


def main():
    check_fixture_lints_clean()
    check_fixture_history_matches_response_schema()
    check_objective_filter()
    check_determinism()
    check_trace_names_runner_up()
    check_trace_leaks_no_key()
    check_pair_served_together()
    check_prereq_filter()
    check_pair_singleton_lint()
    check_prereq_unknown_lint()
    check_selection_mode_recorded()
    check_selection_spec_recorded()
    check_mode_compositions_differ()
    check_cooldown_survives_resume()
    check_cooldown_is_bank_scoped()
    check_explain_renders_plain_text()
    check_preview_writes_no_session()
    check_profile_flags_override()
    print("PASS: selection fixture lints clean, history schema-valid, later checks declared")
    return 0


if __name__ == "__main__":
    sys.exit(main())
