"""Fixed authored staged cases use the existing bank parser and stable IDs."""
import copy
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import model
import identity
import tempfile
from surfaces import agent_operation


def case_fixture():
    return {"version": 1, "activity_id": "synthetic:counter-staged",
            "stimulus": "A fictional counter increments once.",
            "children": ["answer-child", "reason-child"], "order": ["answer", "reason"]}


def bank_fixture(case=None):
    header = "" if case is None else "STAGED-CASES: " + json.dumps([case]) + "\n"
    return header + "\n".join(
        "Q%d. Select fictional choice %d.\n[TYPE: mc]\n[OBJECTIVE: synthetic]\n[ID: %s]\nA) First\nB) Second\nC) Third\nD) Fourth\nCORRECT: A\nWHY BEST: First fits.\nKEY DISCRIMINATOR: First.\nDISTRACTOR ANALYSIS:\n- B) Second fits a different case; it WOULD be correct for a two-count case.\n- C) Third fits a three-count case and WOULD be correct there.\n- D) Fourth fits a four-count case and WOULD be correct there.\nTRAP: Second.\nCONFIDENCE: high\n" % (n, n, ident)
        for n, ident in enumerate(("answer-child", "reason-child"), 1))


class StagedParserTests(unittest.TestCase):
    def test_declaration_preserves_list_and_fixed_identities(self):
        qs = model.parse_bank(bank_fixture(case_fixture()))
        self.assertIsInstance(qs, list)
        self.assertEqual(qs.staged_cases, [case_fixture()])
        self.assertEqual(model.staged_case_spec_errors(qs), [])
        self.assertEqual([q["item_id"] for q in qs], case_fixture()["children"])

    def test_absent_declaration_does_not_infer_pair(self):
        qs = model.parse_bank(bank_fixture().replace("[TYPE: mc]", "[TYPE: mc]\n[PAIR: example]"))
        self.assertEqual(qs.staged_cases, [])

    def test_rejects_reorder_overlap_unknown_type_and_version(self):
        for member, value in (("order", ["reason", "answer"]), ("version", 2),
                              ("children", ["missing", "reason-child"]),
                              ("children", [[], "reason-child"]), ("stimulus", "")):
            case = case_fixture(); case[member] = value
            self.assertTrue(model.staged_case_spec_errors(model.parse_bank(bank_fixture(case))))
        qs = model.parse_bank(bank_fixture(case_fixture()))
        qs.staged_cases.append(dict(case_fixture(), activity_id="second"))
        self.assertTrue(model.staged_case_spec_errors(qs))
        qs = model.parse_bank(bank_fixture(case_fixture()).replace("[TYPE: mc]", "[TYPE: short]", 1))
        self.assertTrue(model.staged_case_spec_errors(qs))

    def test_reviewed_header_accept_cancel_stale_and_exact_undo(self):
        with tempfile.TemporaryDirectory(prefix="itembank-staged-author-") as directory:
            root = Path(directory); bank = root / "synthetic.md"
            before = bank_fixture().encode(); bank.write_bytes(before)
            fingerprint = identity.object_fingerprint(before, "bank")
            proposal = agent_operation.propose_staged_cases(directory, "synthetic.md", [case_fixture()], fingerprint)
            self.assertEqual(bank.read_bytes(), before)
            cancelled = agent_operation.reject(directory, proposal["proposal_id"], "synthetic reviewer", "Cancel")
            self.assertEqual(cancelled["disposition"], "rejected")
            self.assertEqual(bank.read_bytes(), before)
            proposal = agent_operation.propose_staged_cases(directory, "synthetic.md", [case_fixture()], fingerprint)
            bank.write_bytes(before + b"\nNewer author bytes.\n")
            newer = bank.read_bytes()
            stale = agent_operation.accept(proposal["proposal_id"], {"auditor_autonomy":"draft_and_approve"},
                                           base=directory, reviewer="synthetic reviewer")
            self.assertEqual(stale["disposition"], "conflicted")
            self.assertEqual(bank.read_bytes(), newer)
            bank.write_bytes(before)
            proposal = agent_operation.propose_staged_cases(directory, "synthetic.md", [case_fixture()], fingerprint)
            accepted = agent_operation.accept(proposal["proposal_id"], {"auditor_autonomy":"draft_and_approve"},
                                              base=directory, reviewer="synthetic reviewer",
                                              expected_draft_fingerprint=agent_operation.draft_fingerprint(proposal["draft"]))
            self.assertEqual(accepted["disposition"], "accepted")
            self.assertEqual(model.load(str(bank)).staged_cases, [case_fixture()])
            self.assertTrue(bank.read_bytes().endswith(before))
            undone = agent_operation.undo(directory, proposal["proposal_id"], "synthetic reviewer")
            self.assertEqual(undone["disposition"], "undone")
            self.assertEqual(bank.read_bytes(), before)

    def test_invalid_json_duplicate_members_and_declarations(self):
        for declaration in ('{', '[{"version":1,"version":1}]'):
            qs = model.parse_bank("STAGED-CASES: " + declaration + "\n" + bank_fixture())
            self.assertTrue(model.staged_case_spec_errors(qs))
        qs = model.parse_bank("STAGED-CASES: []\nSTAGED-CASES: []\n" + bank_fixture())
        self.assertTrue(model.staged_case_spec_errors(qs))


if __name__ == "__main__":
    unittest.main()
