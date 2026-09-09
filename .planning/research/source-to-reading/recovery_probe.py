#!/usr/bin/env python3
"""Readiness probe, not a regression test that endorses current defects.

Run from any directory. All mutations use disposable synthetic roots.
Print observed recovery outcomes and acceptance gates as JSON.
"""
import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "fixtures" / "audit"))

import director
import identity
import journal
import locator_fidelity_cases
import source_adapters


def seed_pdf(base):
    case = next(c for c in locator_fidelity_cases.CASE_TABLE
                if c["id"] == "pdf-born-digital-single-column")
    raw = Path(base, case["filename"])
    raw.write_bytes(case["build"]())
    record = journal.op_link(
        base, "source", case["filename"], "human", "synthetic-probe",
        rights={right: "granted" for right in identity.RIGHTS_OPERATIONS})
    return record["object_id"], raw


def main():
    results = {}
    with tempfile.TemporaryDirectory() as base:
        operation_id = director.new_operation_id()
        agent = director._agent_dict(
            operation_id, "recovery probe", "course_builder",
            "draft-and-review", (), "accept", 3)
        journal.commit_operation(
            base, identity.new_object_id(), "source", "new.md", "mint",
            b"# Synthetic source\n", None, "human", "synthetic-probe",
            create_if_missing=True, applied_agent=agent)
        entry = [e for e in journal.entries(base)
                 if e["state"] == "applied"][-1]
        result = director.reverse_operation(
            base, operation_id, "human", "synthetic-probe")
        target = Path(base, "new.md")
        results["R1_director_mint"] = {
            "result": result, "target_exists": target.exists(),
            "gate": "A completed reversal restores prior absence",
            "passed": result["complete"] and not target.exists()}
        if target.exists():
            journal.undo(base, entry["entry_id"], "human", "synthetic-probe")
        results["R2_journal_mint"] = {
            "target_exists": target.exists(),
            "bytes": target.stat().st_size if target.exists() else None,
            "gate": "Undo of creation restores absence, not an empty file",
            "passed": not target.exists()}

    with tempfile.TemporaryDirectory() as base:
        source_id, raw = seed_pdf(base)
        raw_before = raw.read_bytes()
        result = source_adapters.import_source(
            base, "pdf", source_id, "human", "synthetic-probe")
        if result["status"] != "ok":
            results["R3_adapter_undo"] = {"unavailable": result}
        else:
            md = Path(base, result["md_rel_path"])
            sidecar = Path(base, result["sidecar_rel_path"])
            journal.undo(base, result["journal_entry_id"],
                         "human", "synthetic-probe")
            results["R3_adapter_undo"] = {
                "markdown_exists": md.exists(),
                "sidecar_exists": sidecar.exists(),
                "raw_unchanged": raw.read_bytes() == raw_before,
                "gate": "Undo removes both derived objects and retains raw input",
                "passed": not md.exists() and not sidecar.exists()
                and raw.read_bytes() == raw_before}

    with tempfile.TemporaryDirectory() as base:
        source_id, raw = seed_pdf(base)
        before = {p.relative_to(base) for p in Path(base).rglob("*") if p.is_file()}
        failure = None
        response = None
        try:
            with patch.object(journal, "commit_operation",
                              side_effect=RuntimeError("synthetic interruption")) as commit:
                response = source_adapters.import_source(
                    base, "pdf", source_id, "human", "synthetic-probe")
        except RuntimeError as exc:
            failure = str(exc)
        injected = commit.called
        added = sorted(str(p.relative_to(base)) for p in Path(base).rglob("*")
                       if p.is_file() and p.relative_to(base) not in before)
        results["R3_adapter_interruption"] = {
            "injection_reached": injected, "raised": failure,
            "returned": response, "added_files": added,
            "gate": "Interruption before journal commit leaves no orphan sidecar",
            "passed": injected and not added}

    with tempfile.TemporaryDirectory() as base:
        target = Path(base, "conflict.md")
        journal.commit_operation(
            base, identity.new_object_id(), "source", target.name, "mint",
            b"# Synthetic source\n", None, "human", "synthetic-probe",
            create_if_missing=True)
        entry = [e for e in journal.entries(base)
                 if e["state"] == "applied"][-1]
        external = b"# External synthetic edit\n"
        target.write_bytes(external)
        code = None
        try:
            journal.undo(base, entry["entry_id"], "human", "synthetic-probe")
        except journal.JournalError as exc:
            code = exc.code
        results["C1_conflict_preserved"] = {
            "code": code, "external_bytes_preserved": target.read_bytes() == external,
            "passed": code == "journal.conflict" and target.read_bytes() == external}

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
