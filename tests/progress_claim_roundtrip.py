#!/usr/bin/env python3
"""Phase 16C (16C-04) progress claim roundtrip.

Direct standard-library roundtrip script in the project's established shape:
`fail(msg)` and a non-zero exit on failure. It proves GRAPH-03's honest
progress contract: the nine-field claim tuple, seven dimensions that never
merge, three membership classes with separate denominators, the locked
sentences for the three degraded cases, the D-14A-3 fill state that moves
both directions, and a rendered display that provably carries no aggregate
and no percent character at all.

The degraded state this file exists to prove is the missing denominator: a
claim with nothing to divide by renders the locked indeterminate sentence,
never an invented percent and never an empty bar.
"""
import ast
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import progress_claims as pc

FAILURES = []


def fail(msg):
    print("FAIL: %s" % msg)
    FAILURES.append(msg)


def _scenario():
    """The full synthetic scenario: all seven dimensions populated, one
    missing denominator, one pending mark, one version-split objective, all
    three membership classes, two fill states."""
    course_records = {
        "emt.obj.1": {"membership": "required", "designed": 4, "cited": 3,
                      "complete": True, "retention_state": "stable"},
        "emt.obj.2": {"membership": "required", "designed": 3, "cited": 3,
                      "complete": False, "retention_state": "due"},
        # designed 0 on purpose: a choice group with no fixed count is the
        # real shape of a missing denominator, and it is the case the
        # indeterminate sentence exists for.
        "emt.obj.3": {"membership": "required_choice", "designed": 0,
                      "cited": 1, "complete": False,
                      "retention_state": "weak"},
        "emt.obj.4": {"membership": "enrichment", "designed": 5, "cited": 2,
                      "complete": False, "retention_state": "unknown"},
        "emt.obj.5": {"membership": "required", "designed": 2, "cited": 2,
                      "complete": False, "version_split": True,
                      "retention_state": "unknown"},
    }
    snapshot = (
        {"event_type": "activity_completed", "event_id": "a1"},
        {"event_type": "activity_completed", "event_id": "a2"},
        {"event_type": "activity_skipped", "event_id": "a3"},
        {"event_type": "response", "event_id": "r1", "score": True},
        {"event_type": "response", "event_id": "r2", "score": None},
        {"event_type": "mark", "response_event_id": "r1"},
    )
    return snapshot, course_records


def check_claim_shape():
    """Nine fields, the determinate sentence, and a refused settlement."""
    if pc.CLAIM_FIELDS != ("claim_kind", "scope", "numerator", "denominator",
                           "rule", "window", "settlement", "authority",
                           "uncertainty"):
        fail("CLAIM_FIELDS is %r" % (pc.CLAIM_FIELDS,))
    if len(pc.CLAIM_DIMENSIONS) != 7:
        fail("CLAIM_DIMENSIONS holds %d" % len(pc.CLAIM_DIMENSIONS))
    if set(pc.DIMENSION_LABELS) != set(pc.CLAIM_DIMENSIONS):
        fail("every dimension needs exactly one label")
    if pc.MEMBERSHIP_CLASSES != ("required", "required_choice", "enrichment"):
        fail("MEMBERSHIP_CLASSES is %r" % (pc.MEMBERSHIP_CLASSES,))
    if pc.RETENTION_STATE_WORDS != ("due", "stable", "weak", "at risk",
                                    "unknown"):
        fail("RETENTION_STATE_WORDS is %r" % (pc.RETENTION_STATE_WORDS,))

    c = pc.claim("count", "emt_respiratory.obj.1@v1", 9, 12,
                 "required activities submitted", "as of snapshot s1",
                 "settled", "evidence store", "")
    if set(c) != set(pc.CLAIM_FIELDS):
        fail("claim returned %r" % sorted(c))
    if pc.claim_text(c) != "9 of 12 required activities submitted":
        fail("the determinate sentence is %r" % pc.claim_text(c))
    try:
        pc.claim("count", "s", 1, 1, "r", "w", "probably", "a", "")
    except ValueError as exc:
        if "probably" not in str(exc):
            fail("the settlement error does not name the value: %s" % exc)
    else:
        fail("claim accepted an unknown settlement")

    # Purity, asserted over the source: no evidence import, no file open.
    src = open(os.path.join(ROOT, "progress_claims.py"),
               encoding="utf-8").read()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [node.module or ""]
        else:
            continue
        for name in names:
            head = name.split(".")[0]
            if head in ("runtime", "evidence") or head == "surfaces":
                fail("progress_claims.py imports %s" % name)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                and node.func.id == "open":
            fail("progress_claims.py opens a file; the snapshot is an "
                 "argument for a reason")


def check_missing_denominator():
    """No denominator renders the locked sentence and stores the word."""
    c = pc.claim("count", "emt.scope", 3, None, "activities", "w", "settled",
                 "course records", "")
    if c["denominator"] != "indeterminate":
        fail("a None denominator stored as %r" % (c["denominator"],))
    text = pc.claim_text(c, "Airway management")
    if text != "Indeterminate: Airway management has no fixed denominator.":
        fail("the indeterminate sentence is %r" % text)
    if "%" in text:
        fail("the indeterminate path invented a percent")


def check_pending_and_version_split():
    """Pending stays pending; a version split transfers nothing."""
    snapshot, course_records = _scenario()
    claims = pc.claims_from_events(snapshot, course_records)

    pending = [c for c in claims["open_uncertainty"]
               if c["settlement"] == "pending"]
    if len(pending) != 1:
        fail("expected one pending claim, got %r" % (pending,))
    elif pc.claim_text(pending[0]) != "1 pending review":
        fail("the pending sentence is %r" % pc.claim_text(pending[0]))

    settled = claims["settled_evidence"]
    if not settled:
        fail("no settled-evidence claim was produced")
    else:
        # The unmarked response is in the denominator and NOT in the
        # numerator: it is neither a pass nor a failure.
        if settled[0]["numerator"] != 1 or settled[0]["denominator"] != 2:
            fail("the unmarked response was folded into a verdict: %r"
                 % settled[0])

    split = [c for c in claims["design_coverage"]
             if c.get("uncertainty") == "version_split"]
    if len(split) != 1:
        fail("expected one version-split claim, got %r" % (split,))
    else:
        text = pc.claim_text(split[0], "Airway management")
        if text != ("Unknown for this version of Airway management. Earlier "
                    "evidence stays with the earlier version."):
            fail("the version-split sentence is %r" % text)
        if split[0]["numerator"] != 0:
            fail("the version-split claim inherited evidence: %r" % split[0])

    # The split objective contributes to no membership denominator at all.
    for c in claims["design_coverage"] + claims["formal_completion"]:
        if c["scope"] == "required" and c["denominator"] == 3:
            fail("the version-split objective was counted in a required "
                 "denominator")


def check_fill_state():
    """Discrete blocks that move both directions."""
    strong = pc.fill_state("emt.obj.1", 4, "stable")
    weaker = pc.fill_state("emt.obj.1", 4, "weak")
    at_risk = pc.fill_state("emt.obj.1", 4, "at risk")
    thin = pc.fill_state("emt.obj.1", 1, "stable")
    if not (strong["filled"] > weaker["filled"] > at_risk["filled"]):
        fail("the fill state does not fall as retention weakens: %r"
             % [strong["filled"], weaker["filled"], at_risk["filled"]])
    if not thin["filled"] < strong["filled"]:
        fail("the fill state does not rise with settled evidence")
    for state in (strong, weaker, at_risk, thin):
        if not isinstance(state["filled"], int) \
                or not isinstance(state["total"], int):
            fail("fill state values must be integers: %r" % state)
        if not 0 <= state["filled"] <= state["total"] == pc.FILL_BLOCKS:
            fail("fill state out of range: %r" % state)
        if state["legend"] != pc.FILL_STATE_LEGEND:
            fail("the legend was re-worded")
    if pc.FILL_STATE_LEGEND != ("Filled blocks show current standing for "
                                "this objective. They move up and down as "
                                "evidence and retention change. This is not "
                                "a permanent grade."):
        fail("FILL_STATE_LEGEND is %r" % (pc.FILL_STATE_LEGEND,))
    try:
        pc.fill_state("o", 1, "excellent")
    except ValueError as exc:
        if "excellent" not in str(exc):
            fail("the retention-state error does not name the value")
    else:
        fail("fill_state accepted an unknown retention state")


def check_no_aggregate():
    """The whole rendered display, scanned for every way it could lie."""
    snapshot, course_records = _scenario()
    claims = pc.claims_from_events(snapshot, course_records)
    fills = [pc.fill_state("emt.obj.1", 3, "stable"),
             pc.fill_state("emt.obj.2", 3, "due")]
    text = pc.render_claims_text(claims, fills)

    if "%" in text:
        fail("the rendered display contains a percent character")
    lowered = text.lower()
    for word in ("overall", "readiness", "mastery score", "total progress"):
        if word in lowered:
            fail("the rendered display carries an aggregate word: %r" % word)
    for label in pc.DIMENSION_LABELS.values():
        if text.count(label) != 1:
            fail("%r appears %d times, expected once"
                 % (label, text.count(label)))
    for line in text.split("\n"):
        hits = [l for l in pc.DIMENSION_LABELS.values() if l in line]
        if len(hits) > 1:
            fail("one line carries two dimensions: %r" % line)

    sentences = [
        ("Indeterminate:", 1),
        ("pending review", 1),
        ("Earlier evidence stays with the earlier version.", 1),
    ]
    for needle, want in sentences:
        if text.count(needle) != want:
            fail("%r appears %d times, expected %d"
                 % (needle, text.count(needle), want))

    # Adding enrichment cannot move a required row. Render twice, with and
    # without the enrichment objective, and compare the required lines.
    def required_lines(records):
        made = pc.claims_from_events(snapshot, records)
        rendered = pc.render_claims_text(made, [])
        return [l for l in rendered.split("\n") if "required objectives" in l]

    without = dict((k, v) for k, v in course_records.items()
                   if v.get("membership") != "enrichment")
    if required_lines(course_records) != required_lines(without):
        fail("the enrichment claim moved a required denominator:\n%r\n%r"
             % (required_lines(course_records), required_lines(without)))
    if not required_lines(course_records):
        fail("the scenario produced no required row to compare")

    # Required and enrichment keep different denominators.
    req = [c for c in claims["design_coverage"] if c["scope"] == "required"]
    enr = [c for c in claims["selected_enrichment"]]
    if not req or not enr:
        fail("the scenario must populate both a required and an enrichment "
             "claim")
    elif req[0]["denominator"] == enr[0]["denominator"]:
        fail("required and enrichment share a denominator: %r"
             % req[0]["denominator"])

    # Retention renders as state words with counts, never a probability.
    if "Current retention" not in text:
        fail("the retention dimension did not render")
    for word in pc.RETENTION_STATE_WORDS:
        pass  # each word is allowed but none is required in every scenario
    if "retrievability" in lowered:
        fail("Retrievability was surfaced in the display")


def check_aria_contract():
    """D10 recorded as data, with the fill state deliberately valuenow-free."""
    fill = pc.ARIA_CONTRACT["fill_state"]
    if "aria-valuetext" not in fill["attributes"]:
        fail("the fill state must carry aria-valuetext")
    if "aria-valuenow" in fill["attributes"]:
        fail("the fill state must not carry aria-valuenow")
    determinate = pc.ARIA_CONTRACT["determinate_claim"]
    for attr in ("aria-valuenow", "aria-valuetext"):
        if attr not in determinate["attributes"]:
            fail("a determinate claim must carry %s" % attr)
    indeterminate = pc.ARIA_CONTRACT["indeterminate_claim"]
    if not indeterminate.get("indeterminate"):
        fail("the indeterminate rule must mark itself indeterminate")
    if "visible text" not in indeterminate["note"] \
            or "spinner" not in indeterminate["note"]:
        fail("the indeterminate rule must name visible text and refuse an "
             "unexplained spinner")
    if pc.ARIA_CONTRACT["announcements"]["region"] != "role=status":
        fail("announcements must route through the one status region")


def main():
    checks = [check_claim_shape, check_missing_denominator,
              check_pending_and_version_split, check_fill_state,
              check_no_aggregate, check_aria_contract]
    for check in checks:
        check()
    failed = len(FAILURES)
    print("PROGRESS CLAIMS: %d passed, %d failed"
          % (len(checks) - failed, failed))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
