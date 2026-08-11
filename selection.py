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
SPEC_FIELDS = ("objective", "count", "seed", "exclude_item_ids",
               "pair", "prerequisite", "selection_mode", "prereq_satisfied")

# The four selection compositions. These strings deliberately share three of
# `daemon.SESSION_MODES`' values (`diagnostic`, `practice`, `exam`) and one
# orphan (`remediation`) -- they live in a DIFFERENT field than the feedback
# policy `mode` for exactly that reason (D-11). A future reader who "tidies"
# one into the other is undoing a one-way door.
SELECTION_MODES = ("diagnostic", "practice", "remediation", "exam")

# Difficulty ordinals. The fallback is 99 and sorts LAST, never first:
# `difficulty` is free text with no lint-enforced enum, and an unlabelled
# item silently treated as "easiest" would corrupt every ascending ordering.
DIFFICULTY_ORDER = {"recall": 0, "application": 1, "analysis": 2}
_DIFFICULTY_FALLBACK = 99

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
    pair = spec.get("pair") or ""
    prereq = spec.get("prerequisite") or ""
    out = [q for q in questions
           if (not objective or q.get("objective") == objective)
           and evidence.evidence_key(q) not in excluded]
    if pair:
        out = filter_by_pair(out, pair)
    if prereq:
        out = filter_by_prereq(out, prereq)
    return out


def filter_by_pair(candidates, name):
    """Every candidate whose `q["pair"]` equals `name` -- exact string
    comparison over an in-memory list, never regex and never a scan of
    anything unbounded (T-07-01)."""
    return [q for q in candidates if q.get("pair") == name]


def filter_by_prereq(candidates, objective):
    """Every candidate whose `q["prereq"]` list contains `objective` -- exact
    membership over an in-memory list, never a path or SQL interpolation
    (T-07-05)."""
    return [q for q in candidates if objective in (q.get("prereq") or [])]


def order_shuffled(candidates, rng, rank=None):
    """The seeded shuffle: the tracer's ordering primitive, now in the mode
    table's `(candidates, rng, rank)` contract. When a recency `rank` map is
    supplied, a recently-seen item sorts later than an equally-eligible
    unseen one (the D-08 soft penalty)."""
    return _seeded_sort(candidates, rng, None, rank)


def _seeded_sort(candidates, rng, ordinal, rank=None):
    """Sort `candidates` by `ordinal` (a per-item sort key) with ties broken
    by the seeded order, so every ordering primitive is deterministic for a
    given seed (D-10). `rank` is the recency-penalty map from
    `exposure_sets`; when present it is the primary key so a recently-seen
    item ranks later than an equally-eligible unseen one."""
    order = list(range(len(candidates)))
    rng.shuffle(order)
    seeded_pos = {i: pos for pos, i in enumerate(order)}
    if rank:
        order.sort(key=lambda i: (rank.get(
            evidence.evidence_key(candidates[i]), 0.0), seeded_pos[i]))
    if ordinal is not None:
        order.sort(key=lambda i: (ordinal(candidates[i]), seeded_pos[i]))
    return [candidates[i] for i in order]


def order_difficulty_asc(candidates, rng, rank=None):
    """Ascending difficulty, unknown/unlabelled last."""
    return _seeded_sort(candidates, rng,
                        lambda q: DIFFICULTY_ORDER.get(q.get("difficulty") or "",
                                                      _DIFFICULTY_FALLBACK),
                        rank)


def order_difficulty_desc(candidates, rng, rank=None):
    """Descending difficulty (hardest first), unknown/unlabelled last."""
    return _seeded_sort(candidates, rng,
                        lambda q: -DIFFICULTY_ORDER.get(q.get("difficulty") or "",
                                                        _DIFFICULTY_FALLBACK),
                        rank)


def order_balanced(candidates, rng, rank=None):
    """Round-robin across the difficulty buckets so a fixed-count session
    draws evenly rather than front-loading one band."""
    buckets = {"recall": [], "application": [], "analysis": [], "other": []}
    for q in candidates:
        d = q.get("difficulty") or ""
        buckets[d if d in DIFFICULTY_ORDER else "other"].append(q)
    for b in buckets.values():
        rng.shuffle(b)
    out = []
    while any(buckets.values()):
        for b in ("recall", "application", "analysis", "other"):
            if buckets[b]:
                out.append(buckets[b].pop(0))
    return out


def one_per_objective(candidates):
    """At most one item per objective, in ascending bank order."""
    seen = set()
    out = []
    for q in candidates:
        o = q.get("objective", "")
        if o not in seen:
            seen.add(o)
            out.append(q)
    return out


def _filter_none(candidates, spec, history):
    return list(candidates)


def _filter_diagnostic(candidates, spec, history):
    return one_per_objective(candidates)


def _filter_remediation(candidates, spec, history):
    """Items whose objective has a recorded failure, plus every pair partner
    of any such item (D-06/D-07)."""
    failed = {row.get("objective") for row in history
              if row.get("score") is False}
    out = [q for q in candidates if q.get("objective", "") in failed]
    pair_names = {q.get("pair") for q in out if q.get("pair")}
    for q in candidates:
        if q.get("pair") in pair_names and q not in out:
            out.append(q)
    return out


# ONE table of compositions, not four code paths (D-06): a reader checks
# SEL-02 by inspecting this dict. Each row names the filter, ordering,
# count policy and exposure policy that define the mode.
MODES = {
    "diagnostic": {"filter": _filter_diagnostic, "order": order_difficulty_asc,
                   "count": "spread", "exposure": "ignore"},
    "practice": {"filter": _filter_none, "order": order_shuffled,
                 "count": "exact", "exposure": "hard_and_soft"},
    "remediation": {"filter": _filter_remediation, "order": order_difficulty_asc,
                    "count": "exact_keep_pairs", "exposure": "hard_and_soft"},
    "exam": {"filter": _filter_none, "order": order_balanced,
             "count": "exact", "exposure": "none"},
}


def exposure_sets(history, cooldown, decay):
    """The hard/soft exposure split (D-08). `history` arrives already scoped
    to this bank and retraction-filtered -- this function neither re-filters
    nor re-reads (D-09).

    Returns `(hard, ranks, notes)`: `hard` is the set of item keys appearing
    in the last `cooldown` responses; `ranks` maps every key to the float
    recency penalty `decay * (1 / (1 + age))` where `age` is how many
    responses back its most recent occurrence was; `notes` is empty."""
    hard = set()
    last_seen = {}
    if history:
        window = history[-cooldown:] if cooldown else []
        for row in window:
            hard.add(row.get("item_id") or ("ref:" + row.get("item_ref", "")))
        total = len(history)
        for age, row in enumerate(reversed(history)):
            key = row.get("item_id") or ("ref:" + row.get("item_ref", ""))
            last_seen[key] = max(last_seen.get(key, 0.0),
                                 decay * (1.0 / (1.0 + age)))
    return hard, last_seen, []


def select(questions, spec, history, cooldown=None, decay=None):
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

    # `practice` is the default rather than `diagnostic`: a diagnostic
    # composition deliberately ignores cooldown and spreads at most one item
    # per objective, which is the wrong shape for an ordinary sitting.
    selection_mode = spec.get("selection_mode", "practice")
    if selection_mode not in SELECTION_MODES:
        sys.exit("unknown selection_mode %r; known modes: %s"
                 % (selection_mode, ", ".join(SELECTION_MODES)))

    objective = spec.get("objective") or ""
    pair = spec.get("pair") or ""
    prereq = spec.get("prerequisite") or ""
    seed = spec.get("seed", 0)
    excluded = set(spec.get("exclude_item_ids") or [])
    candidates = filter_by_spec(questions, spec, excluded)
    if pair and not candidates:
        known = sorted({q.get("pair") for q in questions if q.get("pair")})
        sys.exit("no items carry pair %r; known pairs: %s"
                 % (pair, ", ".join(known) if known else "(none)"))
    if not candidates:
        sys.exit("no items match objective %r" % objective)

    notes = []
    rng = random.Random(seed)
    if pair:
        # D-07: the whole confusion set is served together, adjacently, in
        # ascending bank order; serving one half of a pair is worse than
        # serving neither, so the count is raised to hold the set and the
        # raise is recorded in the trace.
        count = max(count, len(candidates))
        items = list(candidates)
        ordered_pool = list(candidates)
        notes.append("count raised to %d to hold the whole %r pair"
                     % (count, pair))
        exposure_policy = "none"
    else:
        mode_row = MODES[selection_mode]
        if spec.get("prereq_satisfied"):
            mastered = {row.get("objective") for row in history
                        if row.get("score") is True}
            narrowed = [q for q in candidates
                        if all(p in mastered for p in (q.get("prereq") or []))]
            if not narrowed:
                sys.exit("no items satisfy the requested prerequisites")
            candidates = narrowed
        candidates = mode_row["filter"](candidates, spec, history)
        if not candidates:
            sys.exit("no items match objective %r" % objective)

        exposure_policy = mode_row["exposure"]
        hard, ranks = set(), {}
        if exposure_policy != "none":
            hard, ranks, _ = exposure_sets(
                history, cooldown if cooldown is not None else 20,
                decay if decay is not None else 0.2)
        if exposure_policy == "hard_and_soft":
            windowed = [q for q in candidates
                        if evidence.evidence_key(q) not in hard]
            if len(windowed) < count:
                # Readmission, degrade never block: a small bank must not
                # return an empty session, and the trace says so plainly.
                last_pos = {}
                for i, row in enumerate(history):
                    last_pos[row.get("item_id")
                             or ("ref:" + row.get("item_ref", ""))] = i
                readmit = sorted(
                    (q for q in candidates
                     if evidence.evidence_key(q) in hard),
                    key=lambda q: last_pos.get(evidence.evidence_key(q), 0))
                readmitted = []
                for q in readmit:
                    if len(windowed) >= count:
                        break
                    windowed.append(q)
                    readmitted.append(q["id"])
                if readmitted:
                    notes.append(
                        "%d item(s) were inside the cooldown window and were "
                        "readmitted oldest-seen-first so the session was not "
                        "left short: %s" % (len(readmitted),
                                            ", ".join(readmitted)))
            candidates = windowed

        ordered_pool = mode_row["order"](
            candidates, rng,
            ranks if exposure_policy == "hard_and_soft" else None)
        if mode_row["count"] == "spread":
            items = ordered_pool[:min(count, len(ordered_pool))]
        elif mode_row["count"] == "exact_keep_pairs":
            cut = ordered_pool[:count]
            pair_names = {q.get("pair") for q in cut if q.get("pair")}
            items = cut + [q for q in ordered_pool[count:]
                           if q.get("pair") in pair_names]
        else:
            items = ordered_pool[:count]

    chosen = []
    for pos, q in enumerate(items):
        admitted = []
        if objective:
            admitted.append("it is on objective %r" % objective)
        if pair:
            admitted.append("it is one of %d items in the confusion set %r"
                            % (len(candidates), pair))
        if prereq:
            admitted.append("it builds on prerequisite %r" % prereq)
        if selection_mode == "diagnostic":
            admitted.append("the %s composition spreads at most one item per "
                            "objective" % selection_mode)
        elif selection_mode == "remediation":
            admitted.append("the %s composition draws only from objectives "
                            "with a recorded failure" % selection_mode)
        else:
            admitted.append("the %s composition ordered it" % selection_mode)
        key = evidence.evidence_key(q)
        if exposure_policy == "hard_and_soft" and key in ranks:
            admitted.append("recency lowered its position (%.2f penalty)"
                            % ranks[key])
        opening = "chosen because " + ", ".join(admitted)
        runner_up = None
        if len(items) < len(ordered_pool):
            rq = ordered_pool[len(items)]
            runner_up = {
                "item_id": evidence.evidence_key(rq),
                "item_ref": rq["id"],
                "reason": "it fell outside the requested count of %d" % count,
            }
        if runner_up is None:
            reason = ("%s; there was no other candidate outside the requested "
                      "count" % opening)
        else:
            reason = ("%s; the runner-up %s %s"
                      % (opening, runner_up["item_ref"], runner_up["reason"]))
        chosen.append({
            "item_id": key,
            "item_ref": q["id"],
            "objective": q.get("objective", ""),
            "reason": reason,
            "runner_up": runner_up,
        })

    resolved = {"objective": objective, "count": count, "seed": seed,
                "selection_mode": selection_mode}
    if pair:
        resolved["pair"] = pair
    if prereq:
        resolved["prerequisite"] = prereq
    if excluded:
        resolved["exclude_item_ids"] = sorted(excluded)
    trace = {
        "spec": resolved,
        "evidence": {"log": "", "responses": len(history), "source": "none"},
        "chosen": chosen,
        "notes": notes,
    }
    return items, trace
