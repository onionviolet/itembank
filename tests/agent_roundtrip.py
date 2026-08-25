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


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def run_raw(*args):
    """Run a command without parsing stdout.

    `mark` prints its JSON document and then a human summary line ("1
    recorded, 0 already recorded"), so `json.loads` over the whole stream
    raises "Extra data". Callers that only need the side effect use this.
    """
    return subprocess.run([sys.executable, str(TOOL), *map(str, args)],
                          cwd=ROOT, check=True, capture_output=True, text=True)


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


def check_marker_close():
    """The marker's desk is collected: a sitting parked on a pending prose
    answer advances once the mark is recorded, and not one action before.

    This is the regression test for `runtime.marker_close`. Before 2026-08-24 a
    bank holding one short item could not be completed on any surface: the park
    is deliberate and pinned by `hint_roundtrip`, but nothing ever unparked it,
    so `lti_roundtrip` reached the marker-closed state by hand-writing cursor
    and status into the session file. Both halves are asserted here, because a
    test that only checked the advance would pass on a runtime that never
    parked at all.
    """
    with tempfile.TemporaryDirectory() as tmp:
        bank = Path(tmp) / "sample_bank.md"
        shutil.copyfile(BANK, bank)
        session = Path(tmp) / "marker.json"
        view = run("start", bank, "--count", "6", "--seed", "7",
                   "--mode", "practice", "--out", session)
        # Drive to the first short item; every other type is answered
        # correctly, since practice holds the cursor on a wrong answer.
        while view["status"] == "active" and view["item"]["type"] != "short":
            view = run("submit", session, "--answer",
                       json.dumps(answer_for(view["item"])))["next"]
        if view["status"] != "active" or view["item"]["type"] != "short":
            fail("the seeded sitting never reached a short item")
        short_id = view["item"]["id"]
        before = json.loads(session.read_text())["cursor"]

        result = run("submit", session, "--answer",
                     json.dumps("A constructed response, in full sentences."))
        if result["action"] != "defer_feedback" or result["score"] is not None:
            fail("a short response must defer with no score: %r" % result)
        if json.loads(session.read_text())["cursor"] != before:
            fail("a pending short response must not advance the cursor")

        # Parked: `next` re-serves the same item, because nothing has ruled.
        if run("next", session)["item"]["id"] != short_id:
            fail("next moved past a pending item before any mark existed")

        session_id = json.loads(session.read_text())["session_id"]
        run_raw("mark", "--session", session_id, "--base", tmp,
                "--item", short_id, "--verdict", "pass")

        # Collected: the same call now hands back the following item.
        after = run("next", session)
        if after.get("status") == "active" and after["item"]["id"] == short_id:
            fail("next stayed on a marked item; the marker's desk was not collected")
        if json.loads(session.read_text())["cursor"] == before:
            fail("an accepted mark did not advance the cursor")

        while after["status"] == "active":
            item = after["item"]
            if item["type"] == "short":
                run("submit", session, "--answer", json.dumps("More prose."))
                sid = json.loads(session.read_text())["session_id"]
                run_raw("mark", "--session", sid, "--base", tmp,
                        "--item", item["id"], "--verdict", "pass")
                after = run("next", session)
                continue
            after = run("submit", session, "--answer",
                        json.dumps(answer_for(item)))["next"]
        if json.loads(session.read_text())["status"] != "complete":
            fail("a sitting containing a short item never reached complete")
        report = run("report", session)
        # A settled mark is not outstanding work. This assertion previously
        # required `pending_manual >= 1` after a `pass` verdict, which pinned
        # the very defect the 13.9 sitting later exposed: the marker's own
        # ruling stayed invisible to the marker, and the report went on asking
        # for work that was already done.
        if report["summary"]["pending_manual"] != 0:
            fail("a sitting whose only short item is marked still reports %d "
                 "pending manual mark(s)"
                 % report["summary"]["pending_manual"])
        outcomes = report["summary"]["teaching_outcomes"]
        settled = [r["outcome"] for r in outcomes.values()
                   if r["item_ref"] == short_id]
        if settled != ["accepted_mark"]:
            fail("a passed mark should read accepted_mark, got %r" % settled)

        # The fail verdict is settled too, and reads differently. Both halves
        # matter: `pending` must mean nobody has looked yet, never "looked and
        # said no".
        sid = json.loads(session.read_text())["session_id"]
        run_raw("mark", "--session", sid, "--base", tmp,
                "--item", short_id, "--verdict", "fail")
        report = run("report", session)
        if report["summary"]["pending_manual"] != 0:
            fail("a failed mark left the item counted as pending manual work")
        outcomes = report["summary"]["teaching_outcomes"]
        failed = [r["outcome"] for r in outcomes.values()
                  if r["item_ref"] == short_id]
        if failed != ["marked_incorrect"]:
            fail("a failed mark should read marked_incorrect, got %r" % failed)
    print("  marker close: parked before a mark, advances after, sitting completes")


def main():
    check_cli_reaches_shared_do_functions()
    check_marker_close()
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
