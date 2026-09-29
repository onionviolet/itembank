#!/usr/bin/env python3
"""Saved practice evidence keeps misses, pending prose, and due review apart."""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import evidence
import retention
from model import load
from surfaces import retention_view, study


def response(ref, score, ts, item_type="mc"):
    event = evidence.response_event(
        "practice-1", {"objective": "water:review", "id": ref,
                       "type": item_type, "item_id": ""},
        "B" if item_type == "mc" else "My reasoning", score,
        "practice", 1, "synthetic.md")
    event["ts"] = ts
    return event


def main():
    with tempfile.TemporaryDirectory() as base:
        log = evidence.log_path(base)
        os.makedirs(os.path.dirname(log), exist_ok=True)
        events = [
            response("R1", True, "2026-08-01T10:00:00.000Z"),
            response("R2", True, "2026-08-02T10:00:00.000Z"),
            response("R3", False, "2026-08-03T10:00:00.000Z"),
            response("R4", None, "2026-08-04T10:00:00.000Z", "short"),
        ]
        for event in events:
            evidence.append_event(log, event)
        payload = retention.retention_report(
            evidence.capture_events(log),
            cutoff="2026-08-10T12:00:00.000Z", weeks=4)
        row = payload["objectives"]["water:review"]
        assert (row["attempts"], row["settled"], row["correct"],
                row["missed"], row["pending"]) == (4, 3, 2, 1, 1)
        assert row["due"] is True, row
        table = retention_view.trend_table(payload)
        detail = retention_view.objective_detail(row)
        assert "Missed settled</th><td>1" in detail
        assert "Pending manual review</th><td>1" in detail
        assert "Due review</th><td>" in detail
        assert "<th>Missed settled</th><th>Pending manual review</th>" in table
        assert "<th>Scheduled review date</th>" in table
        assert "Due review</th><td>Due" in detail
        due_date = (row["scheduler"] or {}).get("due_date")
        assert due_date and due_date in detail

        bank = os.path.join(ROOT, "fixtures", "selection_bank.md")
        page = study.study_page(bank, load(bank))
        assert "Recall rating" in page
        assert "Local to this page, not graded or saved as evidence" in page
        assert "mastered" not in page
    print("practice_review_roundtrip: ok")


if __name__ == "__main__":
    main()
