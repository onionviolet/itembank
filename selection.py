"""The one place an item is chosen.

Every surface reaches a selection by calling into this module rather than by
reimplementing the filters, `itembank start` and `/api/start` included. That is
what stops the CLI, the JSON session interface and Phase 10 from quietly
disagreeing about what a sitting contains.

Selection is pure: `select(questions, spec, history)` is deterministic given
its three inputs and opens no file of its own (D-09). The caller reads the
evidence snapshot and passes it in; the trace records which snapshot it rested
on. This mirrors `runtime.score_response`'s everything-arrives-as-an-argument
shape, and it is what keeps the selector testable against a synthetic history.
"""
import random
import sys

import evidence
import model  # noqa: F401  (the question shape `select` consumes comes from model.load)


# The selection-spec keys this build honours. A field a later plan has not
# wired yet is refused loudly rather than silently ignored: each later plan in
# this phase appends its own field to this tuple in the same commit that wires
# it.
SPEC_FIELDS = ("objective", "count", "seed", "exclude_item_ids")

# Matches `surfaces/cli.py`'s `--count` default and `handle_api_start`'s
# `data.get("count", 10)`.
DEFAULT_COUNT = 10


def filter_by_spec(questions, spec, excluded):
    """The objective filter and hard exclusions, in ascending bank order.

    `excluded` is a set of `evidence.evidence_key(q)` values built by the
    caller's exclusion list -- never positional item numbers, per 01-CONTEXT
    D-05, because numbers move when a bank is edited.
    """
    objective = spec.get("objective") or ""
    return [q for q in questions
            if (not objective or q.get("objective") == objective)
            and evidence.evidence_key(q) not in excluded]


def order_shuffled(indices, rng):
    """The tracer's one ordering primitive: shuffle candidate bank indices
    with the seeded `rng` in the same ascending order `do_start` used to build
    them, so the output is byte-identical to the inline `rng.shuffle` this
    module replaced. A fillable stub, not an architectural one: plan 07-05
    swaps ordering functions per mode inside the same table slot."""
    rng.shuffle(indices)
    return indices


def select(questions, spec, history):
    """Turn a selection request plus the evidence history into an ordered item
    list and a trace (D-01/D-04/D-09). Pure and deterministic given its three
    arguments: same bank, same spec, same history, same seed in, same items in
    the same order out (D-10).

    `questions` is `model.load()`'s list; `history` is a list of response rows
    the caller already read (the tracer passes an empty list; plan 07-05 wires
    the real evidence read). `items` is a list of the selected question dicts,
    each the same object that arrived in `questions`.
    """
    unknown = sorted(set(spec) - set(SPEC_FIELDS))
    if unknown:
        sys.exit("unknown selection field(s) %r; known fields: %s"
                 % (unknown, ", ".join(SPEC_FIELDS)))

    # A non-positive count is rejected outright rather than handed to the
    # slice below: Python's slice semantics treat a negative stop index as
    # "up to but excluding the last |count| elements," so count=-1 would
    # otherwise silently produce nearly the entire bank instead of erroring
    # on the obviously-invalid input. Checked here, not per-caller, so both
    # the CLI's --count and /api/start's count field get the same guard.
    count = spec.get("count", DEFAULT_COUNT)
    if not isinstance(count, int) or isinstance(count, bool) or count < 1:
        sys.exit("count must be a positive integer, got %r" % (count,))

    objective = spec.get("objective") or ""
    seed = spec.get("seed", 0)
    excluded = set(spec.get("exclude_item_ids") or [])
    candidates = filter_by_spec(questions, spec, excluded)
    if not candidates:
        sys.exit("no items match objective %r" % objective)

    rng = random.Random(seed)
    order = order_shuffled(list(range(len(candidates))), rng)
    items = [candidates[i] for i in order[:count]]

    chosen = []
    for pos, q in enumerate(items):
        runner_up = None
        if pos + count < len(order):
            rq = candidates[order[pos + count]]
            runner_up = {
                "item_id": evidence.evidence_key(rq),
                "item_ref": rq["id"],
                "reason": "it fell outside the requested count of %d" % count,
            }
        if runner_up is None:
            reason = ("chosen because it is on objective %r and the seed %r "
                      "placed it %d of %d matching items; there was no other "
                      "candidate outside the requested count"
                      % (objective, seed, pos + 1, len(candidates)))
        else:
            reason = ("chosen because it is on objective %r and the seed %r "
                      "placed it %d of %d matching items; the runner-up %s "
                      "%s" % (objective, seed, pos + 1, len(candidates),
                              runner_up["item_ref"], runner_up["reason"]))
        chosen.append({
            "item_id": evidence.evidence_key(q),
            "item_ref": q["id"],
            "objective": q.get("objective", ""),
            "reason": reason,
            "runner_up": runner_up,
        })

    resolved = {"objective": objective, "count": count, "seed": seed}
    if excluded:
        resolved["exclude_item_ids"] = sorted(excluded)
    trace = {
        "spec": resolved,
        "evidence": {"log": "", "responses": len(history), "source": "none"},
        "chosen": chosen,
        "notes": [],
    }
    return items, trace
