#!/usr/bin/env python3
"""Honest progress as claims, never as a score (GRAPH-03).

There is no aggregate here. Not a completion percentage, not a mastery
number, not a readiness ring, not a summary bar. That is not an omission to
be filled in later: a single number across seven independent dimensions is a
claim nobody can defend, and Do-Not-Re-Open row 1 records it as settled. A
summary may LINK to component claims; it may never replace them.

Progress is reported through the nine-field claim tuple, seven separate
dimensions that never merge, and three membership classes that keep separate
denominators. Where the evidence does not support a number, the display says
so in fixed words: indeterminate when there is no denominator, pending when a
mark has not settled, unknown when an objective's identity changed and its
earlier evidence stayed with the earlier version.

The authority split is GRAPH-03's: course records own design coverage and
formal completion, the evidence store owns participation and settled
evidence, and the retention module owns retention states. This module owns
none of them. It formats what it is handed.

Purity is structural, not a promise. Nothing here opens a file, imports
`evidence`, or reads a clock. The event snapshot arrives as an argument,
because `evidence.capture_events` exists precisely so that appending to the
log after a render cannot change claims the render already returned, and a
second reader inside this module would defeat it.

Rendering is `surfaces/retention_view.py`'s discipline carried forward: the
projection formats already-derived claims and performs no arithmetic of its
own.
"""

# The nine fields, in order. A field added later is additive; a field renamed
# is a breaking change for the 16C-09 tracer and for 17A both.
CLAIM_FIELDS = ("claim_kind", "scope", "numerator", "denominator", "rule",
                "window", "settlement", "authority", "uncertainty")

CLAIM_DIMENSIONS = ("design_coverage", "participation", "settled_evidence",
                    "current_retention", "formal_completion",
                    "selected_enrichment", "open_uncertainty")

DIMENSION_LABELS = {
    "design_coverage": "Design coverage",
    "participation": "Participation",
    "settled_evidence": "Settled evidence",
    "current_retention": "Current retention",
    "formal_completion": "Formal completion",
    "selected_enrichment": "Selected enrichment",
    "open_uncertainty": "Open uncertainty",
}

# Three memberships, three denominators. Adding enrichment can never lower a
# required denominator's completion, which is only structurally true if the
# two are never summed (GRAPH-03).
MEMBERSHIP_CLASSES = ("required", "required_choice", "enrichment")

# Retention is state words with counts and a window. Retrievability is never
# surfaced as a percentage or a probability anywhere in this display.
RETENTION_STATE_WORDS = ("due", "stable", "weak", "at risk", "unknown")

SETTLEMENTS = ("settled", "pending", "unknown")

# Locked copy, transcribed verbatim from the 16C-UI-SPEC Copywriting Contract
# and the Progress Comprehension Display Contract.
INDETERMINATE_COPY = "Indeterminate: {scope} has no fixed denominator."
PENDING_COPY = "{n} pending review"
VERSION_SPLIT_COPY = "Unknown for this version of {objective}. Earlier evidence stays with the earlier version."
FILL_STATE_LEGEND = "Filled blocks show current standing for this objective. They move up and down as evidence and retention change. This is not a permanent grade."

# The number of discrete blocks in the text projection. D-14A-3 fixes
# discrete blocks, self-adjustable in both directions, and the legend; it
# does not fix a count. Four keeps the text legible and 17A may rescale the
# visual count without touching this contract.
FILL_BLOCKS = 4

# D10, recorded as data so 17A renders against a decision rather than a
# reading of prose.
ARIA_CONTRACT = {
    "determinate_claim": {
        "role": "progressbar",
        "attributes": ("aria-valuemin", "aria-valuemax", "aria-valuenow",
                       "aria-valuetext"),
        "aria_valuetext": "the full claim text, {n} of {N} {metric name}",
        "note": "the number alone is not meaningful, so valuetext always "
                "carries the words as well",
    },
    "fill_state": {
        "role": "progressbar",
        "attributes": ("aria-valuetext",),
        "aria_valuetext": "the filled and total block counts in words",
        "note": "no aria-valuenow: the fill state is a standing, not a "
                "measured quantity on a scale",
    },
    "indeterminate_claim": {
        "role": "progressbar",
        "attributes": ("aria-valuetext",),
        "indeterminate": True,
        "note": "an indeterminate progressbar with visible text, never an "
                "unexplained spinner",
    },
    "announcements": {
        "region": "role=status",
        "note": "one shared live region; every state change announces once "
                "through it",
    },
}


def claim(claim_kind, scope, numerator, denominator, rule, window,
          settlement, authority, uncertainty):
    """One progress claim, carrying exactly the nine `CLAIM_FIELDS`.

    A `denominator` of None is stored as the string "indeterminate" rather
    than left null, so a consumer that forgets to check cannot divide by it
    and cannot render it as zero.

    An unrecognized settlement raises. There are exactly three states a claim
    can be in, and a fourth invented at a call site would be a fourth
    epistemic status nothing downstream knows how to render honestly.
    """
    if settlement not in SETTLEMENTS:
        raise ValueError("unknown settlement: %r" % (settlement,))
    return {"claim_kind": claim_kind,
            "scope": scope,
            "numerator": numerator,
            "denominator": ("indeterminate" if denominator is None
                            else denominator),
            "rule": rule,
            "window": window,
            "settlement": settlement,
            "authority": authority,
            "uncertainty": uncertainty}


def claim_text(c, scope_name=""):
    """One claim as the sentence a learner reads.

    The determinate form is "{n} of {N} {metric name}". The metric name is
    the claim's own `rule` and is always specific: never the bare word
    progress, which would say only that something is being counted without
    saying what (report 08 section 6.3 item 6).
    """
    name = scope_name or c["scope"]
    if c["settlement"] == "unknown":
        if c.get("uncertainty") == "version_split":
            return VERSION_SPLIT_COPY.replace("{objective}", name)
        if c.get("uncertainty"):
            return "Unknown: %s" % c["uncertainty"]
        return "Unknown"
    # Pending is checked before indeterminate on purpose. A pending claim
    # usually has no denominator (nobody knows how many marks are coming),
    # and reading it as indeterminate would report a missing denominator
    # where the honest statement is that a count is awaiting review.
    if c["settlement"] == "pending":
        return PENDING_COPY.replace("{n}", str(c["numerator"]))
    if c["denominator"] == "indeterminate":
        return INDETERMINATE_COPY.replace("{scope}", name)
    return "%s of %s %s" % (c["numerator"], c["denominator"], c["rule"])


def fill_state(objective_id, settled_count, retention_state):
    """The D-14A-3 per-objective fill state: discrete blocks that move both
    ways.

    Filled blocks come from settled evidence and are then stepped DOWN by a
    weakening retention state, so the same objective falls as retention
    decays and rises again as it recovers. That two-way movement is the whole
    point: a fill that only ever rises is a grade wearing a progress bar's
    clothes, and D-14A-3 exists to refuse exactly that.

    Discrete integers, never a float and never a percent.
    """
    if retention_state not in RETENTION_STATE_WORDS:
        raise ValueError("unknown retention state: %r" % (retention_state,))
    filled = min(int(settled_count), FILL_BLOCKS)
    if retention_state == "due":
        filled = min(filled, FILL_BLOCKS - 1)
    elif retention_state == "weak":
        filled = min(filled, FILL_BLOCKS - 2)
    elif retention_state == "at risk":
        filled = min(filled, 1)
    elif retention_state == "unknown":
        filled = min(filled, FILL_BLOCKS - 1)
    filled = max(0, filled)
    return {"objective_id": objective_id,
            "filled": filled,
            "total": FILL_BLOCKS,
            "retention_state": retention_state,
            "legend": FILL_STATE_LEGEND}


def _count_types(snapshot, wanted):
    return sum(1 for e in snapshot if e.get("event_type") == wanted)


def claims_from_events(snapshot, course_records):
    """Every dimension's claims, computed only from the two arguments.

    `snapshot` is the tuple `evidence.capture_events` returns, captured by
    the caller and handed in. This module never opens the log: capture once,
    render from that capture, and an append during a render cannot split the
    story the render tells.

    `course_records` is a synthetic course-record stand-in for now
    (16C-RESEARCH Assumption A4). The 14B course graph feeds it for real once
    wired, and the signature does not change when it does.

    Expected `course_records` shape, per objective id:
    `{"membership": one of MEMBERSHIP_CLASSES, "designed": int,
      "cited": int, "complete": bool, "version_split": bool}`.
    """
    claims = dict((d, []) for d in CLAIM_DIMENSIONS)
    window = "as of the captured snapshot"

    # Design coverage and formal completion are the course records' to state.
    # Each membership class keeps its own denominator: three claims, never a
    # sum, so adding enrichment cannot move a required row.
    for membership in MEMBERSHIP_CLASSES:
        members = [(oid, r) for oid, r in sorted(course_records.items())
                   if r.get("membership") == membership
                   and not r.get("version_split")]
        if not members:
            continue
        designed = sum(int(r.get("designed", 0)) for _, r in members)
        cited = sum(int(r.get("cited", 0)) for _, r in members)
        dimension = ("selected_enrichment" if membership == "enrichment"
                     else "design_coverage")
        claims[dimension].append(claim(
            "count", membership, cited, designed or None,
            "%s objectives with a cited source" % membership.replace("_", " "),
            window, "settled", "course records", ""))
        complete = sum(1 for _, r in members if r.get("complete"))
        claims["formal_completion"].append(claim(
            "count", membership, complete, len(members),
            "%s objectives formally complete" % membership.replace("_", " "),
            window, "settled", "course records", ""))

    # A version-split objective reads unknown on the NEW identity. Nothing
    # transfers: the earlier evidence stays with the earlier version, and no
    # code path here moves it (Do-Not-Re-Open row 9).
    for oid, record in sorted(course_records.items()):
        if record.get("version_split"):
            claims["design_coverage"].append(claim(
                "state", oid, 0, None, "objective identity changed", window,
                "unknown", "course records", "version_split"))

    # Participation counts the two D-16C-1 lifecycle types by name. Plan
    # 16C-06 ships them; counting them here by name is what lets that plan be
    # purely additive.
    completed = _count_types(snapshot, "activity_completed")
    skipped = _count_types(snapshot, "activity_skipped")
    if completed or skipped:
        claims["participation"].append(claim(
            "count", "course", completed, completed + skipped,
            "activities completed rather than skipped", window, "settled",
            "evidence store", ""))

    # Settled evidence joins responses with settled marks. A response whose
    # mark has not settled contributes to the PENDING claim and to nothing
    # else: it is never a pass and never a failure.
    responses = [e for e in snapshot if e.get("event_type") == "response"]
    marked_ids = set()
    for event in snapshot:
        if event.get("event_type") == "mark":
            marked_ids.add(event.get("response_event_id")
                           or event.get("retracts") or "")
    settled = [r for r in responses if r.get("event_id") in marked_ids
               or r.get("score") is not None]
    pending = [r for r in responses if r not in settled]
    if responses:
        claims["settled_evidence"].append(claim(
            "count", "course", len(settled), len(responses),
            "responses with a settled mark", window, "settled",
            "evidence store", ""))
    if pending:
        claims["open_uncertainty"].append(claim(
            "count", "course", len(pending), None,
            "responses awaiting review", window, "pending",
            "evidence store", ""))

    # Retention is a state distribution with the window named. No
    # probability, no percentage, no Retrievability number.
    distribution = dict((w, 0) for w in RETENTION_STATE_WORDS)
    for record in course_records.values():
        state = record.get("retention_state", "unknown")
        if state in distribution:
            distribution[state] += 1
    for word in RETENTION_STATE_WORDS:
        if distribution[word]:
            claims["current_retention"].append(claim(
                "state", "course", distribution[word], len(course_records),
                "objectives %s" % word, window, "settled",
                "retention module", ""))
    unknown_states = distribution["unknown"]
    if unknown_states:
        claims["open_uncertainty"].append(claim(
            "count", "course", unknown_states, None,
            "objectives with no retention state yet", window, "unknown",
            "retention module", "not enough settled attempts yet"))
    return claims


def render_claims_text(claims_by_dimension, fill_states):
    """The whole display as one plain-text block.

    This is the contract-level projection 17A later styles, and it is the one
    place claims become rendered output, which is what makes the no-aggregate
    scan in the test meaningful: a surface that rendered its own summary
    would be outside the scan.

    It computes nothing. Every number here was derived before it arrived
    (the `retention_view` discipline).
    """
    lines = []
    for dimension in CLAIM_DIMENSIONS:
        lines.append(DIMENSION_LABELS[dimension])
        rows = claims_by_dimension.get(dimension) or []
        if not rows:
            lines.append("  Nothing recorded yet.")
        for row in rows:
            # The scope id is a machine identity; underscores are not a
            # learner's word. Only the indeterminate and unknown sentences
            # interpolate it, and those are the two a learner reads most
            # carefully, so they read it in words.
            lines.append("  " + claim_text(
                row, str(row["scope"]).replace("_", " ")))
        lines.append("")
    if fill_states:
        lines.append("Objectives")
        for state in fill_states:
            blocks = "#" * state["filled"] + "." * (state["total"]
                                                    - state["filled"])
            lines.append("  %s  %s  (%d of %d blocks, retention %s)"
                         % (state["objective_id"], blocks, state["filled"],
                            state["total"], state["retention_state"]))
        lines.append("  " + FILL_STATE_LEGEND)
    return "\n".join(lines)
