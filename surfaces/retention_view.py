"""Render-only server-side components for the Phase 10 retention surfaces
(plan 10-05, 10-UI-SPEC).

This module is the "shared SSR components" seam: `SnapshotStamp`,
`SignalCard`, `ObjectiveState`, `EvidenceDrawer`, `TrendSeries`, `CapGate`
and `PendingReviewBadge`, built from Phase 4 presentation primitives and
the generated theme tokens. Every function accepts ALREADY-DERIVED
dictionaries (a snapshot claim, a report payload, a cap decision, an
objective row) and performs NO state/weight/cap arithmetic, NO I/O, NO
model/Anki reads, and NO item choice -- the browser renders only what a
server-issued snapshot says, and this module only formats it (D-01, D-03,
D-13). The exact locked copies from 10-UI-SPEC.md are used verbatim; no
streaks, points, targets, or loss states ever render here (D-19/D-20).
"""
import html

from surfaces import presentation

esc = presentation.esc


def _fmt_rate(value):
    """A rate as text, or 'unknown' -- reading the already-derived number,
    never recomputing it (D-15: no arithmetic in the renderer)."""
    if value is None:
        return "unknown"
    return "%.2f" % value


# ---------------------------------------------------------------------------
# SnapshotStamp -- the provenance marker every derived surface carries
# ---------------------------------------------------------------------------

def snapshot_stamp(claim):
    """`Snapshot S-… · Nw · M live events · zone` from one claim dict
    (10-UI-SPEC Evidence and Determinism Contract): the visible marker that
    the same snapshot id appears on the card, the disclosure, the start
    request, the resulting session and the Phase 7 trace."""
    claim = claim or {}
    sid = claim.get("snapshot_id") or ""
    short = sid[:8] if sid else "unavailable"
    weeks = (claim.get("window") or {}).get("weeks")
    weeks = "" if weeks is None else "%dw" % weeks
    count = claim.get("live_event_count")
    count = "" if count is None else "%s live events" % count
    zone = claim.get("local_day_zone") or ""
    parts = [p for p in ("Snapshot " + short, weeks, count, zone) if p]
    return ('<p class="stamp" data-snapshot="%s" data-cutoff="%s">%s</p>'
            % (esc(sid), esc(claim.get("cutoff") or ""),
               esc(" \u00b7 ".join(parts))))


# ---------------------------------------------------------------------------
# SignalCard -- one owner-labelled signal; owners are never summed
# ---------------------------------------------------------------------------

def signal_card(owner, text):
    """One owner-prefixed signal line (10-UI-SPEC Anki separation): the
    owner (`itembank` or `Anki`) is read before the counts, and this
    component structurally disallows aggregation across owners -- callers
    pass one owner and one text, never a merged total."""
    return ('<p class="signal"><span class="owner">%s</span>%s</p>'
            % (esc(owner), esc(text)))


# ---------------------------------------------------------------------------
# ObjectiveState -- text label plus shape; never color-only
# ---------------------------------------------------------------------------

STATE_TITLES = {
    "unknown": "Not enough evidence yet",
    "weak": "Weak -- below the configured accuracy threshold",
    "due": "Due -- the review interval has elapsed",
    "at-risk": "At risk of needing review",
    "stable": "Stable -- within the configured interval",
    "mastered": "Mastered -- recent accuracy at/above the configured threshold",
    "conflicting": "Signals disagree",
}

STATE_SHAPES = {
    "unknown": "\u25cb", "weak": "\u25b3", "due": "\u25c7",
    "at-risk": "\u26a0", "stable": "\u25cf", "mastered": "\u2605",
    "conflicting": "\u2049",
}


def objective_state(state, title=None):
    """A text state chip with a shape, from an already-derived state name.
    The state name is always read in text; color carries no meaning alone
    (10-UI-SPEC responsive/SR rules)."""
    state = state or "unknown"
    label = title or STATE_TITLES.get(state, state)
    shape = STATE_SHAPES.get(state, "\u2022")
    return ('<span class="state %s" title="%s">%s %s</span>'
            % (esc(state), esc(label), esc(shape), esc(state)))


# ---------------------------------------------------------------------------
# PendingReviewBadge -- pending counts toward pacing only (D-09/D-22)
# ---------------------------------------------------------------------------

def pending_review_badge(count, model_suggested=0):
    """The pending-review marker: attempted work that counts toward today's
    pacing but is explicitly excluded from mastery, intervals and due state.
    A Phase 8 model suggestion counts as attempted work only (D-22)."""
    if not count and not model_suggested:
        return ""
    total = (count or 0) + (model_suggested or 0)
    detail = "Counts toward today\u2019s work, not mastery, until a human " \
             "mark is accepted."
    if model_suggested:
        detail = ("Counts toward today\u2019s work, not mastery, until a "
                  "human mark is accepted; %d model suggestion(s) are "
                  "attempted work only, never mastery." % model_suggested)
    return ('<p class="pending" data-pending="%d" title="%s">'
            "Pending manual review: %d</p>" % (total, esc(detail), total))


# ---------------------------------------------------------------------------
# EvidenceDrawer -- observed facts, configured rules, derived conclusion
# ---------------------------------------------------------------------------

def evidence_drawer(row, claim=None, subject=None):
    """The `Why this recommendation` native disclosure (10-UI-SPEC
    EvidenceDrawer): source data before inference. Three labelled regions --
    observed facts, configured rules, and derived conclusion -- so the
    learner can always tell what was measured from what was decided
    (D-03/D-04). `row` is one already-derived objective row from
    `retention.retention_report` (or the day recommendation); nothing here
    is recomputed."""
    row = row or {}
    claim = claim or {}
    obj = row.get("objective") or ""
    state = row.get("state") or "unknown"
    observed = []
    if row.get("attempts") is not None:
        observed.append("%d attempt(s), %d settled, %d correct"
                        % (row["attempts"], row.get("settled") or 0,
                           row.get("correct") or 0))
    if row.get("recent_accuracy") is not None:
        observed.append("recent accuracy %s"
                        % _fmt_rate(row["recent_accuracy"]))
    if row.get("highest_hint") is not None:
        observed.append("highest hint tier %s" % row["highest_hint"])
    if row.get("average_hint") is not None:
        observed.append("average hint tier %s" % _fmt_rate(row["average_hint"]))
    if row.get("pending"):
        observed.append("%d pending manual review" % row["pending"])
    if row.get("last_evidence"):
        observed.append("last evidence %s" % row["last_evidence"])
    if row.get("success_days") is not None:
        observed.append("%d day(s) with confirmed success"
                        % row["success_days"])
    observed_text = "; ".join(observed) if observed else "No live evidence yet."

    reason = row.get("risk_reason") or row.get("reason")
    derived = ("%s" % STATE_TITLES.get(state, state))
    if reason:
        derived += " -- %s" % reason
    if state in ("unknown", "conflicting") or not row.get("attempts"):
        derived = ("Not enough evidence yet. This objective has fewer than "
                   "the settled attempts needed for a recommendation. "
                   "Practice is still available; no mastery or trend is "
                   "claimed.")
        if state == "conflicting":
            derived = ("Signals disagree. Review the evidence before "
                       "changing your plan. This is not a prediction or a "
                       "score.")
    if state == "at-risk":
        derived = ("At risk of needing review. You previously showed "
                   "success, but there has been no confirming evidence for "
                   "the configured interval.")

    body = (
        '<dl class="drawer">'
        '<dt>Observed facts</dt><dd>%s</dd>'
        "<dt>Configured rules</dt><dd>State labels come from "
        "schema-bounded settings (settings version %s); no model or "
        "prediction is involved.</dd>"
        "<dt>Derived conclusion</dt><dd>%s</dd>"
        "</dl>"
        % (esc(observed_text),
           esc(claim.get("settings_version") or "unknown"), esc(derived)))
    return presentation.details_section(
        "Why this recommendation", body,
        data={"objective": obj, "subject": subject or "",
              "snapshot": claim.get("snapshot_id") or ""})


# ---------------------------------------------------------------------------
# CapGate -- runtime-issued block/allowed result + recovery (D-07/D-08)
# ---------------------------------------------------------------------------

def cap_gate(decision, recovery_href="/report", lesson_href=None,
             override_id=None):
    """Render one runtime-issued cap decision (never a browser counter):
    at cap, the exact locked block copy plus recovery choices; below cap, a
    calm one-line all-clear. `override_id` is the id of the native
    confirmation dialog's trigger pairing, or None to omit the override
    affordance."""
    decision = decision or {}
    subject = decision.get("subject") or ""
    blocked = bool(decision.get("blocked"))
    count = decision.get("count")
    cap = decision.get("cap")
    if not blocked or cap is None:
        line = "Cap: %d of %d ordinary attempts today." % (count or 0, cap) \
            if cap is not None else "No daily cap is configured."
        return '<p class="cap ok">%s</p>' % esc(line)
    block = ("Today\u2019s %s cap is reached (%d of %d ordinary attempts)."
             % (subject, count or 0, cap))
    recovery = ['<a class="go" href="%s">Review evidence</a>'
                % esc(recovery_href)]
    if lesson_href:
        recovery.append('<a class="go" href="%s">Read a lesson</a>'
                        % esc(lesson_href))
    if override_id:
        recovery.append(
            '<button type="button" class="go" id="%s">'
            "Request one-sitting override</button>" % esc(override_id))
    return ('<div class="cap blocked" role="alert">'
            "<p>%s</p><p>Review evidence, read a lesson, or request one "
            "additional sitting.</p>"
            '<p class="acts">%s</p></div>'
            % (esc(block), "".join(recovery)))


def override_dialog(override_id, subject, confirm_id, objective=None):
    """The native one-sitting override confirmation (10-UI-SPEC Copy
    Contract): exact title/body/buttons; the page's JS opens it, Escape or
    cancel restores focus, and only `confirm_id` sends the action token.
    Writes nothing by itself -- confirmation delegates to the runtime
    guard (D-08). `objective` is the namespaced objective the server
    derives the subject from; it rides in a data attribute, never in the
    visible copy."""
    obj_attr = ' data-objective="%s"' % esc(objective) if objective else ""
    return (
        '<dialog id="%s" class="override-dialog"%s aria-labelledby="%s-head">'
        '<h2 id="%s-head">Start one additional %s sitting?</h2>'
        "<p>This exception applies only to this sitting and will be "
        "recorded. It does not change your daily cap.</p>"
        '<form method="dialog" class="acts">'
        '<button type="submit" value="cancel" class="go cancel" '
        'id="%s-cancel">Keep today\u2019s cap</button>'
        '<button type="submit" value="confirm" class="go primary" '
        'id="%s">Start one additional sitting</button>'
        "</form></dialog>"
        % (esc(override_id), obj_attr, esc(override_id), esc(override_id),
           esc(subject or ""), esc(override_id), esc(confirm_id)))


# ---------------------------------------------------------------------------
# TrendSeries -- semantic table + text summary are canonical (D-13/D-15)
# ---------------------------------------------------------------------------

def trend_text(payload):
    """A plain-text summary of the SAME report payload (labels may reorder,
    never recompute, never omit uncertainty or provenance) -- the text twin
    of the semantic table below, both reading already-derived fields."""
    claim = payload.get("claim") or {}
    overview = payload.get("overview") or {}
    lines = [
        "Retention & trends report",
        "",
        "snapshot: %s" % (claim.get("snapshot_id") or "unavailable"),
        "cutoff: %s  zone: %s  window: %s week(s)" %
        (claim.get("cutoff") or "", claim.get("local_day_zone") or "",
         (claim.get("window") or {}).get("weeks") or 0),
        "filters: %s  live events: %s  settings: %s" %
        (claim.get("filters") or {}, claim.get("live_event_count"),
         claim.get("settings_version")),
        "",
        "overview: %d objective(s) across %d subject(s); %d attempts, %d "
        "settled, %d correct"
        % (overview.get("objective_count", 0), overview.get("subject_count", 0),
           overview.get("attempts", 0), overview.get("settled", 0),
           overview.get("correct", 0)),
    ]
    rr = payload.get("return_rate") or {}
    if rr.get("due"):
        lines.append("return rate: %s (%d occurred / %d due sittings)"
                     % (_fmt_rate(rr.get("rate")), rr.get("occurred", 0),
                        rr.get("due", 0)))
    for subject, sub in sorted((payload.get("subjects") or {}).items()):
        lines.append("subject %r: %d objective(s), %d attempts, %d settled, "
                     "%d correct, %d due"
                     % (subject, sub.get("objective_count", 0),
                        sub.get("attempts", 0), sub.get("settled", 0),
                        sub.get("correct", 0), sub.get("due", 0)))
    return "\n".join(lines)


def trend_table(payload):
    """The semantic trend table -- the canonical representation. Rows are
    already-derived objective summaries; the table adds no arithmetic, only
    raw counts and labels beside every rate (D-15)."""
    objectives = payload.get("objectives") or {}
    if not objectives:
        return ('<p class="empty">Not enough evidence yet. This objective '
                "has fewer than the settled attempts needed for a "
                "recommendation. Practice is still available; no mastery or "
                "trend is claimed.</p>")
    rows = []
    for objective in sorted(objectives):
        o = objectives[objective]
        state = o.get("state") or "unknown"
        rate = _fmt_rate(o.get("recent_accuracy"))
        rows.append(
            "<tr><th scope=row>%s</th><td>%s</td><td>%s</td><td>%d</td>"
            "<td>%d</td><td>%d</td><td>%d</td><td>%s</td><td>%s</td>"
            "<td>%s</td></tr>"
            % (esc(objective), objective_state(state), esc(rate),
               o.get("attempts", 0), o.get("settled", 0),
               o.get("correct", 0), o.get("pending", 0),
               esc("" if o.get("highest_hint") is None
                   else str(o["highest_hint"])),
               esc(o.get("last_evidence") or ""),
               esc(o.get("risk_reason") or "")))
    return (
        '<div class="trend-wrap" tabindex="0" aria-label="trend table, '
        'horizontally scrollable">'
        '<table class="trend">'
        "<thead><tr><th>Objective</th><th>State</th><th>Recent accuracy</th>"
        "<th>Attempts</th><th>Settled</th><th>Correct</th><th>Pending</th>"
        "<th>Highest hint</th><th>Last evidence</th><th>Risk reason</th>"
        "</tr></thead><tbody>%s</tbody></table></div>"
        '<p class="trend-note">Trend table -- The table is the complete '
        "report; the chart is an optional visual summary.</p>" % "".join(rows))


def objective_detail(row, claim=None):
    """One objective's derived detail block for the drilldown view: state,
    raw counts, hint fields, pending, last date, risk reason, and the
    snapshot marker -- all already-derived (D-13/D-15)."""
    row = row or {}
    state = row.get("state") or "unknown"
    fields = [
        ("State", objective_state(state)),
        ("Attempts", str(row.get("attempts", 0))),
        ("Settled", str(row.get("settled", 0))),
        ("Correct", str(row.get("correct", 0))),
        ("Pending manual review", str(row.get("pending", 0))),
        ("Recent accuracy", _fmt_rate(row.get("recent_accuracy"))),
        ("Highest hint tier",
         str(row["highest_hint"]) if row.get("highest_hint") is not None else ""),
        ("Average hint tier", _fmt_rate(row.get("average_hint"))),
        ("Last evidence", row.get("last_evidence") or ""),
        ("Reason", row.get("risk_reason") or ""),
    ]
    cells = "".join("<tr><th scope=row>%s</th><td>%s</td></tr>"
                    % (esc(k), v) for k, v in fields if v)
    return ('<table class="detail"><tbody>%s</tbody></table>%s'
            % (cells, snapshot_stamp(claim or row.get("claim"))))


__all__ = [
    "snapshot_stamp", "signal_card", "objective_state",
    "pending_review_badge", "evidence_drawer", "cap_gate",
    "override_dialog", "trend_text", "trend_table", "objective_detail",
]
