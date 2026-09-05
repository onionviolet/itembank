#!/usr/bin/env python3
"""Render the two registered rollup screens over a real course's evidence.

ROLLUP-DIM and ROLLUP-MAP are the two progress models IDEA-LEDGER
IL-20260817-01 registered, and gate G5 asks that a learner can choose
between them from the rendered screens rather than from a description. The
17B wave-3 pass rendered them once from a scratch script that was never
committed, so the screens could not be rebuilt after the primitives they
compose were fixed. This is that script, kept.

It reads nothing but the course's own evidence log and its scope and graph
sidecars, computes the GRAPH-03 tuples once through the frozen 16C
`progress_claims` surface, and renders both screens from that one tuple set
through the 17A primitives only. Both screens therefore read the same
numbers by construction rather than by inspection, which is the property
the gate actually cares about.

Stdlib only. Usage:

    PYTHONPATH=. python3 tools/rollup_screens.py <course dir> <out dir>
"""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import evidence                                              # noqa: E402
import progress_claims as pc                                 # noqa: E402
from surfaces import presentation, theme                     # noqa: E402


def course_records(objective_ids):
    """The synthetic per-objective record shape `claims_from_events`
    documents, with every objective required, designed, cited and complete.

    Stated here rather than derived, and stated in one place, because the
    14B graph does not yet feed this function (16C-RESEARCH assumption A4).
    A screen rendered from an assumption should name the assumption.
    """
    return dict((oid, {"membership": "required", "designed": 1, "cited": 1,
                       "complete": True, "version_split": False})
                for oid in objective_ids)


def scopes_from(course_dir):
    """The scope tree this course records, read from `scope.md`.

    One `## <kind> scope: <name>` heading per scope, in file order, with the
    boundedness line under it. Read from the file rather than assumed,
    because a screen that hardcoded the tracer's three scopes would prove
    nothing about a second course.
    """
    path = os.path.join(course_dir, "scope.md")
    scopes = []
    if os.path.exists(path):
        kind = name = None
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line.startswith("## ") and ": " in line:
                    head = line[3:]
                    kind, name = head.split(": ", 1)
                    kind = kind.strip().lower().replace(" scope", "")
                    scopes.append({"id": kind, "name": name.strip(),
                                   "bounded": True})
                elif scopes and line.startswith("- **Boundedness:**"):
                    scopes[-1]["bounded"] = "open" not in line.lower()
    if not scopes:
        scopes = [{"id": "course", "name": os.path.basename(course_dir),
                   "bounded": True}]
    return scopes


def tuples_for(course_dir):
    """The one tuple set both screens read: claims per scope, plus the
    per-objective fill states."""
    log = evidence.log_path(course_dir)
    snapshot = list(evidence.capture_events(log))
    objective_ids = sorted(set(
        e.get("objective") for e in snapshot if e.get("objective")))
    records = course_records(objective_ids)
    claims = pc.claims_from_events(snapshot, records)
    settled = {}
    for event in snapshot:
        oid = event.get("objective")
        if oid and event.get("event_type") == "response":
            settled[oid] = settled.get(oid, 0) + 1
    fills = [(oid, pc.fill_state(oid, settled.get(oid, 0), "unknown"))
             for oid in objective_ids]
    return {"objectives": objective_ids, "claims": claims, "fills": fills}


def _dimension_rows(claims, scope_name):
    """One row per claim dimension, carrying the numbers the ARIA contract
    needs beside the sentence a learner reads."""
    rows = []
    for dimension in pc.CLAIM_DIMENSIONS:
        entries = claims.get(dimension) or []
        if not entries:
            continue
        entry = entries[0]
        text = pc.claim_text(entry, scope_name)
        row = {"label": pc.DIMENSION_LABELS[dimension], "text": text}
        num, den = entry.get("numerator"), entry.get("denominator")
        if isinstance(den, int) and isinstance(num, int):
            row["value"], row["max"] = num, den
        rows.append(row)
    return rows


def _objective_rows(fills):
    return [{"label": oid, "filled": state["filled"],
             "legend": state["legend"]} for oid, state in fills]


def _page(title, body):
    return presentation.surface_shell(
        title, body, theme_css=theme.THEME_CSS,
        back={"href": "/", "label": "Back to courses"})


def render_dim(data, scopes):
    """ROLLUP-DIM: every scope states all seven dimensions under its own
    heading. The scope heading is the section label, so a reader never has to
    reach the note at the end of a block to learn which scope they are in."""
    parts = []
    for scope in scopes:
        objectives = (_objective_rows(data["fills"])
                      if scope is scopes[-1] else ())
        # A visible heading, because `_section` puts the label in
        # `aria-label` only: three stacked blocks of identical row labels
        # left a sighted reader working out which scope they were in from
        # the note at the END of the block.
        parts.append(_scope_head(scope))
        parts.append(presentation.progress_comprehension_display(
            _dimension_rows(data["claims"], scope["name"]),
            objectives, label=scope["name"]))
    return _page("ROLLUP-DIM over the scope tree", "".join(parts))


def render_map(data, scopes):
    """ROLLUP-MAP: each scope is a card carrying its own standing, under its
    own heading, with its own note. One primitive per card, and one legend for
    the whole screen."""
    parts = []
    for index, scope in enumerate(scopes):
        if scope is scopes[-1]:
            cards = [{"name": oid, "fill": state["filled"],
                      "meta": "%d of %d blocks, current standing"
                              % (state["filled"], state["total"])}
                     for oid, state in data["fills"]]
            legend = pc.FILL_STATE_LEGEND
        else:
            cards = [{"name": child["name"],
                      "meta": _summary_line(data, child["name"]),
                      "chips": [{"label": "bounded scope" if child["bounded"]
                                 else "open scope", "kind": "unknown"}]}
                     for child in scopes[index + 1:index + 2]]
            legend = ""
        # The heading and the note belong to the scope whose children the
        # cards are, and they bracket those cards. Before this the note fell
        # after the next scope's cards, so an open field's "never reports
        # complete" sentence read as if it described the bounded course.
        parts.append(_scope_head(scope))
        parts.append(presentation.course_shelf(
            cards, label=scope["name"],
            empty="Nothing under this scope yet.",
            legend=legend, legend_id="fill-legend-%d" % index))
    return _page("ROLLUP-MAP over the scope tree", "".join(parts))


def _scope_head(scope):
    """One scope's visible heading and its own note, above its own block."""
    return ('<h2 class="ib-group-head">%s</h2><p class="ib-meta">%s</p>'
            % (presentation.esc(scope["name"]),
               presentation.esc(_scope_note(scope))))


def _scope_note(scope):
    if scope["bounded"]:
        return ("Bounded scope. It may report complete, under the completion "
                "predicate its course records.")
    return ("Open scope. Never reports complete. Every claim above is as of "
            "this scope's recorded version.")


def _summary_line(data, scope_name):
    rows = _dimension_rows(data["claims"], scope_name)
    for row in rows:
        if row["label"] == pc.DIMENSION_LABELS["settled_evidence"]:
            return row["text"]
    return ""


def main(argv):
    if len(argv) != 3:
        sys.exit("usage: rollup_screens.py <course dir> <out dir>")
    course_dir, out_dir = os.path.abspath(argv[1]), os.path.abspath(argv[2])
    os.makedirs(out_dir, exist_ok=True)
    data = tuples_for(course_dir)
    scopes = scopes_from(course_dir)
    payload = json.dumps(
        {"objectives": data["objectives"],
         "fills": [[oid, f] for oid, f in data["fills"]],
         "claims": {k: v for k, v in sorted(data["claims"].items())}},
        ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    written = []
    for name, body in (("rollup-dim.html", render_dim(data, scopes)),
                       ("rollup-map.html", render_map(data, scopes)),
                       ("rollup-tuples.json", payload)):
        path = os.path.join(out_dir, name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(body)
        raw = open(path, "rb").read()
        written.append((name, len(raw), hashlib.sha256(raw).hexdigest()))
    for name, size, digest in written:
        print("%s bytes=%d sha256=%s" % (name, size, digest))
    for name, _size, _digest in written[:2]:
        text = open(os.path.join(out_dir, name), encoding="utf-8").read()
        body = text.split("</style>")[-1]
        print("%s: visible percent signs=%d, 'score'=%d, progressbar rows=%d"
              % (name, body.count("%"), body.lower().count("score"),
                 text.count('role="progressbar"')))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
