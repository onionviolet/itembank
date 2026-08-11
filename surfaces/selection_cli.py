"""The selector's CLI surface: render the trace as prose a learner reads.

The trace is produced in the runtime tier (`selection.select`) and RENDERED
in the CLI tier -- `render_trace` lives here, never in `selection.py`, so the
selector stays pure and the rendering stays a surface concern.
"""
import json
import sys

from surfaces.session import do_select


def render_trace(trace):
    """Plain text, one block per chosen item: who it is, why it was chosen,
    and which named item lost and why. A learner reads this; no rule ids, no
    field names, no JSON."""
    lines = []
    ev = trace.get("evidence") or {}
    lines.append("Selection: %s" % trace.get("spec", {}).get("selection_mode",
                                                             "practice"))
    if ev.get("log"):
        lines.append("Evidence: %s (%d response(s), %s)"
                     % (ev.get("log"), ev.get("responses", 0),
                        ev.get("source", "none")))
    for note in trace.get("notes") or []:
        lines.append("Note: %s" % note)
    for block in trace.get("chosen") or []:
        lines.append("")
        lines.append("- %s (Q%s): %s"
                     % (block.get("item_id", "?"),
                        block.get("item_ref", "?").lstrip("q"),
                        block.get("reason", "")))
        runner_up = block.get("runner_up")
        if runner_up:
            lines.append("    runner-up: %s (Q%s) -- %s"
                         % (runner_up.get("item_id", "?"),
                            runner_up.get("item_ref", "?").lstrip("q"),
                            runner_up.get("reason", "")))
    return "\n".join(lines)


def cmd_select(a):
    spec = {}
    for key in ("objective", "prerequisite", "type", "difficulty",
                "selection_mode", "seed", "count", "pair", "profile"):
        value = getattr(a, key, None)
        if value is not None:
            spec[key] = value
    if getattr(a, "prereq_satisfied", False):
        spec["prereq_satisfied"] = True
    if getattr(a, "exclude", None):
        spec["exclude_item_ids"] = list(a.exclude)
    result = do_select(a.bank, spec, a.force)
    if a.explain:
        print(render_trace(result["trace"]))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0
