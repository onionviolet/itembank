"""The evidence query surface: reading a learner's recorded history back out.

`itembank evidence --objective X` is the first reader over `_evidence/evidence.jsonl`.
It answers "how am I doing on this objective" from the log alone, the same way
`surfaces/session.py` is the first writer into it. An objective with no recorded
events is an empty history, not an error — the command still exits 0.

`itembank id-assign` is the identity writer: the only command that rewrites a
bank file. `lint` stays read-only by design (D-03) — every identity change a
learner's bank ever gets lands in `git diff` through this command alone.
"""
import json
import os
import sys

import model
import evidence


def cmd_evidence(a):
    log = evidence.log_path(a.base)
    rows = evidence.objective_history(log, a.objective)
    result = {"schema_version": evidence.EVENT_SCHEMA_VERSION,
              "objective": a.objective, "count": len(rows), "events": rows}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_id_assign(a):
    paths = a.banks
    texts = {}
    taken = set()
    owner = {}
    for path in paths:
        text = open(path, encoding="utf-8", newline="").read()
        texts[path] = text
        for q in model.parse_bank(text):
            item_id = q.get("item_id", "")
            if not item_id:
                continue
            if item_id in owner and owner[item_id] != path:
                sys.exit("id-assign: item id %s appears in both %s and %s; "
                          "D-05 requires ids to be globally unique across banks" %
                          (item_id, os.path.basename(owner[item_id]),
                           os.path.basename(path)))
            owner[item_id] = path
            taken.add(item_id)

    banks_out = []
    total_assigned = total_recorded = total_updated = 0
    for path in paths:
        new_text, changes = model.assign_ids(texts[path], taken)
        assigned = sum(1 for c in changes if c["action"] == "assigned")
        recorded = sum(1 for c in changes if c["hash_action"] == "recorded")
        updated = sum(1 for c in changes if c["hash_action"] == "updated")
        total_assigned += assigned
        total_recorded += recorded
        total_updated += updated
        banks_out.append({"bank": os.path.basename(path), "assigned": assigned,
                          "hashes_recorded": recorded, "hashes_updated": updated,
                          "changes": changes})
        if not a.dry_run and new_text != texts[path]:
            tmp = path + ".tmp"
            with open(tmp, "w", encoding="utf-8", newline="") as fh:
                fh.write(new_text)
            os.replace(tmp, path)

    payload = {"schema_version": 1, "banks": banks_out, "dry_run": bool(a.dry_run)}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print("%d ids assigned, %d hashes recorded, %d hashes updated" %
          (total_assigned, total_recorded, total_updated))
    return 0
