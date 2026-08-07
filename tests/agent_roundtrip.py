#!/usr/bin/env python3
"""Smoke-test the JSON assessment contract without a browser or service."""
import inspect
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "fixtures" / "sample_bank.md"
TOOL = ROOT / "itembank.py"

sys.path.insert(0, str(ROOT))
from surfaces import session as session_surface       # noqa: E402


def run(*args):
    result = subprocess.run([sys.executable, str(TOOL), *map(str, args)],
                            cwd=ROOT, check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def answer_for(item):
    schema = item["response_schema"]
    if item["type"] == "mc":
        return schema["allowed"][0]
    if item["type"] == "multi":
        return schema["allowed"][:schema["select"]]
    if item["type"] in ("table", "dnd"):
        return {str(row["id"]): item["categories"][0] for row in item["rows"]}
    if item["type"] == "build":
        return item["steps"]
    return "A concise constructed response."


def check_cli_reaches_shared_do_functions():
    """The CLI's `cmd_start`/`cmd_next`/`cmd_submit`/`cmd_report` must each
    call the matching `do_*` function -- the exact function
    `surfaces/daemon.py`'s `/api/*` handlers call too -- so the CLI half
    and the daemon half of this contract cannot drift apart silently
    (SURF-04: one runtime call behind both surfaces, never two).
    """
    pairs = (("cmd_start", "do_start"), ("cmd_next", "do_next"),
            ("cmd_submit", "do_submit"), ("cmd_report", "do_report"))
    for cmd_name, do_name in pairs:
        src = inspect.getsource(getattr(session_surface, cmd_name))
        if (do_name + "(") not in src:
            raise AssertionError(
                "%s does not call %s() -- the CLI and the daemon's /api/* "
                "routes must reach the same do_* function" % (cmd_name, do_name))
    print("agent/daemon shared do_* inventory: ok")


def main():
    check_cli_reaches_shared_do_functions()
    with tempfile.TemporaryDirectory() as tmp:
        session = Path(tmp) / "session.json"
        first = run("start", BANK, "--count", "6", "--seed", "7", "--out", session)
        assert first["status"] == "active"
        assert "correct" not in first["item"]
        while first["status"] == "active":
            item = first["item"]
            result = run("submit", session, "--answer", json.dumps(answer_for(item)))
            assert result["accepted"] is True
            first = result["next"]
        report = run("report", session)
        assert report["status"] == "complete"
        assert report["summary"]["auto_attempts"] >= 1
        assert session.exists()
    print("agent JSON roundtrip: ok")


if __name__ == "__main__":
    main()
