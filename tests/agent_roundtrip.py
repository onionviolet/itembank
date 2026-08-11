#!/usr/bin/env python3
"""Smoke-test the JSON assessment contract without a browser or service."""
import inspect
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "fixtures" / "sample_bank.md"
TOOL = ROOT / "itembank.py"

sys.path.insert(0, str(ROOT))
from surfaces import session as session_surface       # noqa: E402
from surfaces import selection_cli as selection_surface  # noqa: E402


def run(*args):
    result = subprocess.run([sys.executable, str(TOOL), *map(str, args)],
                            cwd=ROOT, check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def answer_for(item):
    """The response the runtime must score true for the public item payload
    -- resolved through the full bank item, because a `dnd`/`table`/`build`
    item's first listed category or step order is not necessarily its key
    (Phase 6 holds the cursor on a wrong practice answer, so driving the
    sitting requires genuinely correct answers)."""
    import serve_roundtrip
    qs = __import__("model").load(os.path.join(ROOT, "fixtures", "sample_bank.md"))
    q = next(q for q in qs if q["id"] == item["id"])
    return serve_roundtrip.correct_answer(q)


def check_cli_reaches_shared_do_functions():
    """The CLI's `cmd_start`/`cmd_next`/`cmd_submit`/`cmd_report` must each
    call the matching `do_*` function -- the exact function
    `surfaces/daemon.py`'s `/api/*` handlers call too -- so the CLI half
    and the daemon half of this contract cannot drift apart silently
    (SURF-04: one runtime call behind both surfaces, never two).
    """
    pairs = (("cmd_start", "do_start"), ("cmd_next", "do_next"),
            ("cmd_submit", "do_submit"), ("cmd_report", "do_report"),
            ("cmd_select", "do_select"))
    for cmd_name, do_name in pairs:
        mod = session_surface if hasattr(session_surface, cmd_name) \
            else selection_surface
        src = inspect.getsource(getattr(mod, cmd_name))
        if (do_name + "(") not in src:
            raise AssertionError(
                "%s does not call %s() -- the CLI and the daemon's /api/* "
                "routes must reach the same do_* function" % (cmd_name, do_name))
    print("agent/daemon shared do_* inventory: ok")


def main():
    check_cli_reaches_shared_do_functions()
    with tempfile.TemporaryDirectory() as tmp:
        # Run against a temp COPY of the fixture bank so the evidence log
        # lands in tmp/_evidence, never fixtures/_evidence: plan 10-03 makes
        # start retention-aware, and accumulated evidence beside the shared
        # fixture would reorder this sitting (the short item is served first
        # once its objective is weighted ahead, leaving zero auto attempts).
        bank = Path(tmp) / "sample_bank.md"
        shutil.copyfile(BANK, bank)
        session = Path(tmp) / "session.json"
        first = run("start", bank, "--count", "6", "--seed", "7",
                    "--mode", "practice", "--out", session)
        assert first["status"] == "active"
        assert "correct" not in first["item"]
        while first["status"] == "active":
            item = first["item"]
            if item["type"] == "short":
                # Phase 6: a constructed response stays pending for a human
                # marker and never advances the cursor.
                result = run("submit", session, "--answer",
                             json.dumps("A constructed response, written out "
                                        "in full sentences."))
                assert result["action"] == "defer_feedback"
                assert result["score"] is None
                break
            result = run("submit", session, "--answer", json.dumps(answer_for(item)))
            assert result["accepted"] is True
            first = result["next"]
        report = run("report", session)
        assert report["summary"]["auto_attempts"] >= 1
        assert report["summary"]["pending_manual"] >= 1
        assert report["summary"]["teaching_outcomes"]
        assert session.exists()
    print("agent JSON roundtrip: ok")


if __name__ == "__main__":
    main()
