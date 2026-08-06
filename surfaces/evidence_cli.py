"""The evidence query surface: reading a learner's recorded history back out.

`itembank evidence --objective X` is the first reader over `_evidence/evidence.jsonl`.
It answers "how am I doing on this objective" from the log alone, the same way
`surfaces/session.py` is the first writer into it. An objective with no recorded
events is an empty history, not an error — the command still exits 0.
"""
import json

import evidence


def cmd_evidence(a):
    log = evidence.log_path(a.base)
    rows = evidence.objective_history(log, a.objective)
    result = {"schema_version": evidence.EVENT_SCHEMA_VERSION,
              "objective": a.objective, "count": len(rows), "events": rows}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0
