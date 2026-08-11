"""The contract-delivery surface: hands over the published documents and does
nothing else.

`itembank schema` is to the five `schemas/*.json` documents what `itembank
spec` is to the bank format: no processing, no summarizing, no rendering --
the bytes on disk, printed verbatim, because a consumer who has to trust a
paraphrase instead of the document itself is a consumer this contract has
already failed. A route serving these same bytes over the loopback server
arrives with the Phase 2 daemon; this command is what exists before it, and
the route will read the same files off disk this command does, not a second
copy embedded in Python.
"""
import json
import sys

import resources
from model import SPEC


# Listed in the order handed to a reader: what a learner sees before
# answering, the session that carries it, the evidence a response leaves
# behind, what comes back out in a report, and one lint finding.
CONTRACTS = (
    ("item", "what a learner sees before answering, from `itembank next`/`start`"),
    ("selection", "the one selection request every surface builds, recorded on the "
                  "session and in the evidence log"),
    ("session", "the resumable session file `start`/`next`/`submit`/`report` share"),
    ("response", "one recorded evidence event, one line of `_evidence/evidence.jsonl` "
                 "-- response, hint, and (Phase 10) explicit lesson completion"),
    ("report", "a session summary, an objective's response history, or the Phase 10 "
               "retention/trends report with its complete evidence claim"),
    ("lint_error", "one finding from `itembank lint --json`'s `errors`/`warnings` arrays"),
    ("agent_usage", "the permissions, disclosure, retry, and manual-grading contract "
                    "for model-facing agents"),
)

CONTRACT_NAMES = tuple(name for name, _ in CONTRACTS)

# The exact command sequence for running one session end to end, each tied to
# the contract its output conforms to -- `contract` is None where no
# published document covers the shape, so an agent is not sent chasing one
# that does not exist. This is what turns a pile of schemas into something an
# agent can actually run (PROTO-05).
COMMANDS = (
    {"command": "itembank lint BANK.md --json",
     "description": "validate a bank; each entry of errors/warnings is one finding",
     "contract": "lint_error"},
    {"command": "itembank id-assign BANK.md",
     "description": "assign opaque item ids and content-hash fingerprints; the only "
                     "command that writes into a bank",
     "contract": None},
    {"command": "itembank select BANK.md --selection-mode MODE --explain",
     "description": "preview a selection and read, in plain English, why each item "
                     "was chosen over a named alternative",
     "contract": "selection"},
    {"command": "itembank start BANK.md --count N --mode MODE --out SESSION.json",
     "description": "start a resumable session; writes SESSION.json and prints its "
                     "first item",
     "contract": "session"},
    {"command": "itembank next SESSION.json",
     "description": "return the current item without its answer key",
     "contract": "item"},
    {"command": "itembank submit SESSION.json --answer A --confidence high",
     "description": "score the current response and record it as a response event "
                     "in _evidence/evidence.jsonl",
     "contract": "response"},
    {"command": "itembank report SESSION.json",
     "description": "summarize the session recorded so far",
     "contract": "report"},
    {"command": "itembank evidence --objective OBJ --base DIR",
     "description": "read one objective's recorded response history",
     "contract": "report"},
)


def _schema_path(name):
    return "schemas/" + name + ".schema.json"


def _load_schema_text(name):
    return resources.read_text(_schema_path(name))


def cmd_usage(a):
    """Print the agent usage contract byte-for-byte off disk, then one
    one-line human summary. The bytes are the contract; the summary is a
    convenience, never a paraphrase an agent should trust."""
    print(_load_schema_text("agent_usage"), end="")
    print()
    print("# An agent may request hints and rubric-review suggestions, read "
          "pending proposals, and accept them only by explicit human action; "
          "it may never write evidence, score responses, select items, "
          "advance tiers, read dropped text, or auto-accept.")
    return 0


def cmd_schema(a):
    if a.all:
        contracts = dict((name, json.loads(_load_schema_text(name))) for name in CONTRACT_NAMES)
        payload = {
            "schema_version": 1,
            "spec": SPEC,
            "contracts": contracts,
            "commands": [dict(c) for c in COMMANDS],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return 0

    if a.name:
        if a.name not in CONTRACT_NAMES:
            sys.exit("unknown contract %r; valid names: %s" %
                     (a.name, ", ".join(CONTRACT_NAMES)))
        print(_load_schema_text(a.name), end="")
        return 0

    print("Published JSON contracts (schemas/*.json):\n")
    for name, summary in CONTRACTS:
        doc = json.loads(_load_schema_text(name))
        print("  %-12s v%-3d  %s" % (name, doc["x-itembank-version"], summary))
    print("\nRun `itembank schema NAME` for one document, or "
          "`itembank schema --all` for the whole contract -- the bank format, "
          "all seven documents, and the command sequence to run a session -- "
          "in one object.")
    return 0
