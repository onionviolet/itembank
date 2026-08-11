#!/usr/bin/env python3
"""Whole-command audit/author/approve/full/undo contract suite for the Phase
11 public CLI (plan 11-05 Task 1 + Task 3 wiring).

Run:
    python tests/audit_cli_roundtrip.py --case configured-adapter
    python tests/audit_cli_roundtrip.py --case modes
    python tests/audit_cli_roundtrip.py            (all cases)

AUTH-01/AUTH-03 are proven with a REAL subprocess: `python itembank.py audit
author ...` resolves the configured Phase 8 model backend from itembank.json
inside `surfaces.cli.main` and reaches `model_adapter.invoke` -- no callable
is injected, no import is monkeypatched, and no command handler is called
in-process. The fake hosted executable records every strict request so the
test can assert the repository-blind allowlist.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

FIXTURES = os.path.join(ROOT, "fixtures", "audit")
ITEMPATH = os.path.join(ROOT, "itembank.py")


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def read_text(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


# The clean draft the fake hosted adapter returns on its final attempt. The
# bounded request's citations are echoed so the response is in scope.
CLEAN_DRAFT = """Q1. During a primary assessment, the first action for an unresponsive patient is:
[OBJECTIVE: emt:airway.opa]
A) Opening and maintaining the airway
B) Checking for a pulse
C) Applying supplemental oxygen
D) Rechecking the blood pressure
CORRECT: A
WHY BEST: Opening the airway comes first because an unresponsive patient cannot protect their own airway.
KEY DISCRIMINATOR: The item turns on the order of the primary assessment.
SECOND-BEST: Checking for a pulse would be the second priority after the airway is opened.
DISTRACTOR ANALYSIS:
- B) Checking for a pulse would be correct if the airway were already patent.
- C) Applying supplemental oxygen would be correct after the airway is secured.
- D) Rechecking the blood pressure would be correct if the patient were stable and awake.
TRAP: Learners jump to circulation; the airway still comes first.
CONFIDENCE: high
"""

BAD_DRAFT = CLEAN_DRAFT.replace("[OBJECTIVE: emt:airway.opa]",
                                "[OBJECTIVE: emt:cardiac.arrest]")


def fake_hosted_script(capture, kind="retry"):
    """The fake hosted-CLI executable: reads the strict adapter request from
    stdin, records it (for the AUTH-03 assertions), and returns an
    out-of-scope draft on attempt 1 then a clean draft on later attempts
    (kind=retry) or always-clean (kind=clean)."""
    return '''#!/usr/bin/env python3
import json
import sys

CAPTURE = %(capture)r

req = json.load(sys.stdin)
payload = (req.get("payload") or {}).get("author_request") or {}
record = {
    "operation": req.get("operation"),
    "attempt": payload.get("attempt"),
    "findings_kinds": [f.get("kind") for f in (payload.get("findings") or [])],
    "request_keys": sorted((payload.get("request") or {}).keys()),
    "has_contract": "Qn." in (payload.get("contract") or ""),
    "serialized": json.dumps(req),
}
with open(CAPTURE, "a", encoding="utf-8") as fh:
    fh.write(json.dumps(record) + "\\n")

citations = (payload.get("request") or {}).get("citations") or []
attempt = payload.get("attempt") or 1
if %(retry)s and attempt == 1:
    item = {"objective": "emt:cardiac.arrest", "type": "mc",
            "citations": citations, "text": %(bad)s}
else:
    item = {"objective": "emt:airway.opa", "type": "mc",
            "citations": citations, "text": %(clean)s}
print(json.dumps({"schema_version": 1, "items": [item]}))
''' % {
    "capture": capture,
    "bad": json.dumps(BAD_DRAFT),
    "clean": json.dumps(CLEAN_DRAFT),
    "retry": "True" if kind == "retry" else "False",
}


def write_settings(base, command, active="fake"):
    data = {
        "model_backend": {
            "active": active,
            "profiles": [{
                "name": active,
                "transport": "hosted_cli",
                "command": command,
                "model": "fake-hosted",
                "timeout_seconds": 30,
                "max_output_bytes": 65536,
                "context_window": 4096,
            }],
        }
    }
    path = os.path.join(base, "itembank.json")
    with open(path, "w", encoding="utf-8", newline="") as fh:
        json.dump(data, fh, indent=2)
    return path


def run_cli(args, base):
    """A REAL subprocess of the public command; configuration comes only
    from files and arguments -- never an injected callable."""
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(
        [sys.executable, ITEMPATH] + args + ["--base", base],
        capture_output=True, text=True, env=env, timeout=120)


def setup_case(wd, script_kind="retry"):
    """A temp source, bank, fake hosted profile, and settings file."""
    source = os.path.join(wd, "syllabus.md")
    shutil.copy(os.path.join(FIXTURES, "syllabus.md"), source)
    bank = os.path.join(wd, "bank.md")
    shutil.copy(os.path.join(FIXTURES, "writer_bank.md"), bank)
    capture = os.path.join(wd, "capture.jsonl")
    script = os.path.join(wd, "fake_hosted.py")
    with open(script, "w", encoding="utf-8", newline="") as fh:
        fh.write(fake_hosted_script(capture, script_kind))
    state = os.path.join(wd, "state")
    write_settings(wd, [sys.executable, script])
    return source, bank, capture, state


def parse_report(out):
    """Parse the first JSON value on stdout; the CLI appends a concise
    human summary line after the machine-readable report."""
    try:
        report, _ = json.JSONDecoder().raw_decode(out)
    except ValueError:
        fail("cli: stdout is not a report JSON: %r" % out[:300])
    return report


def assert_repository_blind(capture):
    """AUTH-03: every recorded adapter request carries only the allowlist
    fields, and never repository paths, bank contents, or credentials."""
    lines = [l for l in read_text(capture).splitlines() if l.strip()]
    if not lines:
        fail("cli: the fake hosted adapter recorded no requests")
    for line in lines:
        rec = json.loads(line)
        if rec["operation"] != "author":
            fail("cli: adapter saw a non-author operation %r"
                 % rec["operation"])
        if not rec["has_contract"]:
            fail("cli: the author request must carry the public format "
                 "contract")
        if rec["request_keys"] != sorted(["schema_version", "objectives",
                                          "count", "item_types",
                                          "citations", "retry_cap",
                                          "mode"]):
            fail("cli: adapter request keys drifted: %s"
                 % rec["request_keys"])
        serialized = rec["serialized"]
        for forbidden in ("model.py", "surfaces/", "audit_writer.py",
                          "authoring.py", "bank.md", "fixtures/",
                          "/Users/", "/mnt/", "secret", "token",
                          "password", "BANK_TEMPLATE"):
            if forbidden in serialized:
                fail("cli: repository context reached the adapter: %r"
                     % forbidden)


def case_configured_adapter():
    """AUTH-01/AUTH-03 through the real composition root: the configured
    fake hosted profile serves a malformed-first/clean-second authoring run
    that retries from structured findings and writes exactly one unit."""
    wd = tempfile.mkdtemp(prefix="audit-cli-adapter-")
    try:
        source, bank, capture, state = setup_case(wd, "retry")
        result = run_cli([
            "audit", "author",
            "--source", source,
            "--bank", bank,
            "--objective", "emt:airway.opa",
            "--count", "1",
            "--item-type", "mc",
            "--mode", "full",
            "--retry-cap", "2",
            "--state-dir", state,
            "--write",
        ], wd)
        if result.returncode != 0:
            fail("cli: author command failed (%d): %s"
                 % (result.returncode, result.stderr[-500:]))
        report = parse_report(result.stdout)
        if report.get("status") != "written":
            fail("cli: configured-adapter run must write, got %r"
                 % report.get("status"))
        if not report.get("write_allowed"):
            fail("cli: full mode must allow the write")
        manifest = report.get("manifest") or {}
        if manifest.get("backend") != "shadow" or \
                manifest.get("state") != "applied":
            fail("cli: non-Git bank must produce an applied shadow manifest")
        if len(__import__("model").parse_bank(read_text(bank))) != 3:
            fail("cli: the bank must carry exactly one added item")

        # structured retry: two strict requests, findings on the second
        lines = [json.loads(l) for l in read_text(capture).splitlines()
                 if l.strip()]
        if len(lines) != 2:
            fail("cli: expected 2 adapter requests, got %d" % len(lines))
        if lines[0]["attempt"] != 1 or lines[1]["attempt"] != 2:
            fail("cli: attempt numbers wrong: %s"
                 % [l["attempt"] for l in lines])
        if lines[1]["findings_kinds"] != ["scope"]:
            fail("cli: second attempt must carry the structured scope "
                 "finding, got %s" % lines[1]["findings_kinds"])
        assert_repository_blind(capture)

        # the public undo command routes by manifest
        undo = run_cli(["audit", "undo", manifest["write_id"],
                        "--bank", bank, "--state-dir", state], wd)
        if undo.returncode != 0:
            fail("cli: undo command failed: %s" % undo.stderr[-300:])
        ureport = parse_report(undo.stdout)
        if ureport.get("status") != "reverted":
            fail("cli: undo must restore, got %r" % ureport.get("status"))
        if len(__import__("model").parse_bank(read_text(bank))) != 2:
            fail("cli: undo must restore the two-item bank")

        print("OK: configured-adapter -- no-DI subprocess author retry "
              "through surfaces.cli.main -> model_adapter.invoke, structured "
              "findings, one shadow write, repository-blind requests, "
              "public undo")
    finally:
        shutil.rmtree(wd, ignore_errors=True)


def case_modes():
    """Report-only, exact-approval, and full/capped behavior through the
    registered public command (AUDIT-05/AUDIT-09). Each mode runs against
    its own fresh bank copy so the runs stay independent."""
    wd = tempfile.mkdtemp(prefix="audit-cli-modes-")
    try:
        source, bank, capture, state = setup_case(wd, "clean")

        def fresh_bank(name):
            path = os.path.join(wd, name)
            shutil.copy(os.path.join(FIXTURES, "writer_bank.md"), path)
            return path

        # report_only: proposes, never writes
        bank_ro = fresh_bank("bank_ro.md")
        ro = run_cli(["audit", "author",
                      "--source", source, "--bank", bank_ro,
                      "--objective", "emt:airway.opa",
                      "--count", "1", "--item-type", "mc",
                      "--mode", "report_only",
                      "--state-dir", state], wd)
        if ro.returncode != 0:
            fail("cli: report_only failed: %s" % ro.stderr[-300:])
        rro = parse_report(ro.stdout)
        if rro.get("status") != "proposed" or rro.get("write_allowed"):
            fail("cli: report_only must propose without writing, got %r"
                 % rro.get("status"))
        if len(__import__("model").parse_bank(read_text(bank_ro))) != 2:
            fail("cli: report_only must not mutate the bank")

        # draft_and_approve: awaiting_approval, then exact write-id approval
        bank_da = fresh_bank("bank_da.md")
        da = run_cli(["audit", "author",
                      "--source", source, "--bank", bank_da,
                      "--objective", "emt:airway.opa",
                      "--count", "1", "--item-type", "mc",
                      "--mode", "draft_and_approve",
                      "--state-dir", state], wd)
        if da.returncode != 0:
            fail("cli: draft_and_approve failed: %s" % da.stderr[-300:])
        rda = parse_report(da.stdout)
        if rda.get("status") != "awaiting_approval":
            fail("cli: draft_and_approve must await approval, got %r"
                 % rda.get("status"))
        pending = rda.get("pending_write_ids") or []
        if len(pending) != 1:
            fail("cli: awaiting report must list the pending write id")
        if len(__import__("model").parse_bank(read_text(bank_da))) != 2:
            fail("cli: awaiting approval must not mutate the bank")

        approved = run_cli(["audit", "author",
                            "--source", source, "--bank", bank_da,
                            "--objective", "emt:airway.opa",
                            "--count", "1", "--item-type", "mc",
                            "--mode", "draft_and_approve",
                            "--state-dir", state,
                            "--approve", pending[0], "--write"], wd)
        if approved.returncode != 0:
            fail("cli: approval invocation failed: %s"
                 % approved.stderr[-300:])
        rap = parse_report(approved.stdout)
        if rap.get("status") != "written":
            fail("cli: exact approval must write, got %r"
                 % rap.get("status"))
        if len(__import__("model").parse_bank(read_text(bank_da))) != 3:
            fail("cli: approved write must add exactly one item")

        # full with a cap: writes and reports volume on every exit
        bank_full = fresh_bank("bank_full.md")
        state2 = os.path.join(wd, "state2")
        full = run_cli(["audit", "author",
                        "--source", source, "--bank", bank_full,
                        "--objective", "emt:airway.opa",
                        "--count", "1", "--item-type", "mc",
                        "--mode", "full",
                        "--state-dir", state2, "--write",
                        "--cap-run", "5"], wd)
        if full.returncode != 0:
            fail("cli: full failed: %s" % full.stderr[-300:])
        rfull = parse_report(full.stdout)
        if rfull.get("status") != "written":
            fail("cli: full must write, got %r/%r"
                 % (rfull.get("status"), rfull.get("outcome")))
        for key in ("proposed_volume", "written_volume", "completed_volume",
                    "retried_volume", "rejected_volume"):
            if key not in rfull:
                fail("cli: full report missing volume key %r" % key)
        if rfull["written_volume"] != 1:
            fail("cli: full volume accounting wrong: %s"
                 % {k: rfull[k] for k in
                    ("proposed_volume", "written_volume")})

        print("OK: modes -- report_only / exact write-id approval / full "
              "capped volume through the registered command")
    finally:
        shutil.rmtree(wd, ignore_errors=True)


CASES = {
    "configured-adapter": case_configured_adapter,
    "modes": case_modes,
}


def main(argv):
    case = None
    rest = list(argv)
    if rest and rest[0] == "--case":
        case = rest[1] if len(rest) > 1 else None
    if case is None:
        for name, fn in sorted(CASES.items()):
            fn()
        return 0
    if case not in CASES:
        print("unknown case %r; known: %s" % (case, sorted(CASES)))
        return 2
    CASES[case]()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
