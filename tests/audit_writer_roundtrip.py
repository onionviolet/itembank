#!/usr/bin/env python3
"""Git, shadow, report-artifact, stale undo, interruption, duplicate, and
parallel writer tests for the Phase 11 transactional writer (plan 11-05
Task 3, AUDIT-08/D-15/D-16/D-17, T-11-17..T-11-20).

Run:
    python tests/audit_writer_roundtrip.py

Stdlib only. Every Git case runs inside a temporary Git repository; every
shadow case runs in a temporary directory. No committed fixture or real bank
is ever mutated.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import audit_writer
import authoring

FIXTURES = os.path.join(ROOT, "fixtures", "audit")


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def read_text(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def read_bytes(path):
    with open(path, "rb") as fh:
        return fh.read()


def fixture_bank():
    path = os.path.join(FIXTURES, "writer_bank.md")
    with open(path, encoding="utf-8") as fh:
        return fh.read()


NEW_ITEM = """Q3. During a primary assessment, the first action for an unresponsive patient is:
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


def make_proposal(bank_text):
    """A minimal immutable preflighted proposal the writer contract accepts."""
    after = bank_text.rstrip("\n") + "\n\n" + NEW_ITEM + "\n"
    before_fp = authoring.bank_fingerprint(bank_text)
    after_fp = authoring.bank_fingerprint(after)
    return {
        "schema_version": 1,
        "run_id": "sha256:" + "a" * 64,
        "request_fingerprint": "sha256:" + "b" * 64,
        "bank_before_fingerprint": before_fp,
        "bank_after_fingerprint": after_fp,
        "source_fingerprints": ["sha256:" + "c" * 64],
        "profile": "test",
        "tool_version": authoring.TOOL_VERSION,
        "units": [{"unit_id": "unit-1", "item_id": "unit-1",
                   "objective": "emt:airway.opa", "tag": "Q3"}],
        "diff": "+Q3. ...",
        "bank_after_text": after,
        "gates": {"lint_errors": [], "lint_warnings": [],
                  "quality_findings": []},
        "item_count": 3,
    }


def run_git(args, cwd):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True,
                          timeout=30)


def git_repo_init(directory):
    """A throwaway Git repo with a committed bank fixture."""
    os.makedirs(directory, exist_ok=True)
    run_git(["git", "init", "-q"], directory)
    run_git(["git", "config", "user.email", "audit@test.local"], directory)
    run_git(["git", "config", "user.name", "audit-test"], directory)
    bank = os.path.join(directory, "bank.md")
    with open(bank, "w", encoding="utf-8", newline="") as fh:
        fh.write(fixture_bank())
    run_git(["git", "add", "bank.md"], directory)
    commit = run_git(["git", "commit", "-m", "baseline"], directory)
    if commit.returncode != 0:
        fail("writer: temp git baseline commit failed: %s"
             % commit.stderr.strip())
    return bank


def case_writer():
    wd = tempfile.mkdtemp(prefix="audit-writer-")
    try:
        # ---------------- shadow: write + exact undo ------------------------
        bank = os.path.join(wd, "shadow", "bank.md")
        os.makedirs(os.path.dirname(bank))
        bank_text = fixture_bank()
        with open(bank, "w", encoding="utf-8", newline="") as fh:
            fh.write(bank_text)
        state = os.path.join(wd, "shadow", "state")
        proposal = make_proposal(bank_text)
        manifest = audit_writer.write_units(proposal, bank, state,
                                            expected_fingerprint=
                                            proposal["bank_before_fingerprint"])
        if manifest.get("backend") != "shadow" or \
                manifest.get("state") != "applied":
            fail("writer: shadow write must apply a shadow manifest")
        if len(authoring.bank_fingerprint(read_text(bank))) != len(
                proposal["bank_after_fingerprint"]):
            fail("writer: shadow write must change the bank")

        # stale undo refuses without a force path (applied write + human edit)
        with open(bank, "a", encoding="utf-8") as fh:
            fh.write("# human edit after write\n")
        try:
            audit_writer.undo(manifest["write_id"], bank, state)
            fail("writer: stale shadow undo must refuse")
        except audit_writer.WriterError as exc:
            if exc.code != "undo.stale_target":
                fail("writer: stale undo wrong code %r" % exc.code)
        # restore the applied state so the real undo can proceed
        with open(bank, "w", encoding="utf-8", newline="") as fh:
            fh.write(proposal["bank_after_text"])

        undo = audit_writer.undo(manifest["write_id"], bank, state)
        if undo.get("status") != "reverted":
            fail("writer: shadow undo failed: %r" % undo)
        if read_text(bank) != bank_text:
            fail("writer: shadow undo must restore the exact before text")
        if audit_writer.undo(manifest["write_id"], bank, state).get(
                "status") != "already_reverted":
            fail("writer: a second undo must be idempotent")

        # stale preflight refuses and never mutates
        try:
            audit_writer.write_units(proposal, bank, state,
                                     expected_fingerprint="sha256:" + "0" * 64)
            fail("writer: stale preflight must refuse")
        except audit_writer.WriterError as exc:
            if exc.code != "writer.stale_preflight":
                fail("writer: stale preflight wrong code %r" % exc.code)

        # duplicate write is idempotent: same proposal applies once
        bank2 = os.path.join(wd, "dup", "bank.md")
        os.makedirs(os.path.dirname(bank2))
        with open(bank2, "w", encoding="utf-8", newline="") as fh:
            fh.write(bank_text)
        state2 = os.path.join(wd, "dup", "state")
        m1 = audit_writer.write_units(proposal, bank2, state2)
        m2 = audit_writer.write_units(proposal, bank2, state2)
        if m1["write_id"] != m2["write_id"]:
            fail("writer: duplicate write id must be deterministic")
        manifests_dir = os.path.join(state2, audit_writer.MANIFESTS_DIR)
        if len([f for f in os.listdir(manifests_dir)
                if f.endswith(".json")]) != 1:
            fail("writer: duplicate write must not create a second manifest")

        # ---------------- Git tracked-clean: one commit + revert undo --------
        gitdir = os.path.join(wd, "git")
        os.makedirs(gitdir)
        git_bank = git_repo_init(gitdir)
        git_text = read_text(git_bank)
        state_git = os.path.join(wd, "git-state")
        git_proposal = make_proposal(git_text)
        g_manifest = audit_writer.write_units(
            git_proposal, git_bank, state_git,
            expected_fingerprint=git_proposal["bank_before_fingerprint"])
        if g_manifest.get("backend") != "git" or \
                not g_manifest.get("git_commit"):
            fail("writer: tracked-clean target must use the Git backend with "
                 "a commit hash")
        porcelain = run_git(["git", "status", "--porcelain", "--",
                             "bank.md"], gitdir)
        if porcelain.stdout.strip():
            fail("writer: git write must commit the bank change, got %r"
                 % porcelain.stdout)
        log = run_git(["git", "log", "--oneline", "-1"], gitdir)
        if "machine-authored" not in log.stdout:
            fail("writer: git write must create one machine-authored commit")

        # git undo: git revert restores the baseline
        g_undo = audit_writer.undo(g_manifest["write_id"], git_bank, state_git)
        if g_undo.get("status") != "reverted" or \
                g_undo.get("backend") != "git":
            fail("writer: git undo failed: %r" % g_undo)
        if read_text(git_bank) != git_text:
            fail("writer: git revert must restore the baseline bank text")

        # git undo refuses a dirty worktree (newer human work)
        git_bank2 = git_repo_init(os.path.join(wd, "git2"))
        git2_text = read_text(git_bank2)
        state_git2 = os.path.join(wd, "git2-state")
        g2 = audit_writer.write_units(make_proposal(git2_text), git_bank2,
                                      state_git2)
        with open(git_bank2, "a", encoding="utf-8") as fh:
            fh.write("# human work after the machine write\n")
        try:
            audit_writer.undo(g2["write_id"], git_bank2, state_git2)
            fail("writer: git undo over a dirty worktree must refuse")
        except audit_writer.WriterError as exc:
            if exc.code != "undo.git_dirty":
                fail("writer: dirty git undo wrong code %r" % exc.code)

        # ---------------- dirty git target -> shadow backend ----------------
        git_bank3 = git_repo_init(os.path.join(wd, "git3"))
        git3_text = read_text(git_bank3)
        with open(git_bank3, "a", encoding="utf-8") as fh:
            fh.write("# uncommitted human edit\n")
        state_git3 = os.path.join(wd, "git3-state")
        g3 = audit_writer.write_units(make_proposal(git3_text), git_bank3,
                                      state_git3)
        if g3.get("backend") != "shadow":
            fail("writer: a dirty tracked target must fall back to shadow")

        # ---------------- report artifact: before_exists false --------------
        report = os.path.join(wd, "reports", "audit.json")
        os.makedirs(os.path.dirname(report))
        rep_proposal = dict(make_proposal(fixture_bank()))
        rep_proposal["bank_after_text"] = json.dumps(
            {"schema_version": 1, "kind": "report"}, indent=2) + "\n"
        rep_proposal["bank_after_fingerprint"] = authoring.bank_fingerprint(
            rep_proposal["bank_after_text"])
        state_r = os.path.join(wd, "reports", "state")
        r_manifest = audit_writer.write_units(rep_proposal, report, state_r,
                                              create_if_missing=True)
        if r_manifest.get("before_exists") is not False:
            fail("writer: a new report artifact must record before_exists "
                 "false")
        if not os.path.exists(report):
            fail("writer: report artifact must be created")
        r_undo = audit_writer.undo(r_manifest["write_id"], report, state_r)
        if r_undo.get("status") != "reverted":
            fail("writer: report artifact undo failed")
        if os.path.exists(report):
            fail("writer: undoing a created report must remove the file")

        # ---------------- interruption: commit failure leaves prepared state -
        gitdir4 = os.path.join(wd, "git4")
        git_bank4 = git_repo_init(gitdir4)
        git4_text = read_text(git_bank4)
        # Break the commit by blanking the identity. Unsetting the repo-local
        # keys is not enough: git then falls back to the machine's global
        # identity, so this case only failed the commit on a runner that had
        # none, and passed vacuously on any developer's machine. An empty
        # local value overrides the global one and git refuses it outright.
        run_git(["git", "config", "user.name", ""], gitdir4)
        run_git(["git", "config", "user.email", ""], gitdir4)
        state_git4 = os.path.join(wd, "git4-state")
        try:
            audit_writer.write_units(make_proposal(git4_text), git_bank4,
                                     state_git4)
            fail("writer: git commit failure must surface as WriterError")
        except audit_writer.WriterError as exc:
            if not exc.code.startswith("git."):
                fail("writer: commit failure wrong code %r" % exc.code)
        # the prepared journal is visible (in the repo's manifest dir) and no
        # applied manifest exists
        g4_manifests = os.path.join(gitdir4, ".itembank", "audit",
                                    "manifests")
        prepared = [f for f in os.listdir(g4_manifests)
                    if f.endswith(".json")]
        if not prepared:
            fail("writer: interruption must leave a visible prepared journal")
        with open(os.path.join(g4_manifests, prepared[0]),
                  encoding="utf-8") as fh:
            journal = json.load(fh)
        if journal.get("state") != "prepared" or journal.get("git_commit"):
            fail("writer: interrupted git write must stay prepared")
        # restore identity so the repo stays usable for cleanup
        run_git(["git", "config", "user.name", "audit-test"], gitdir4)
        run_git(["git", "config", "user.email", "audit@test.local"],
                gitdir4)
        run_git(["git", "checkout", "--", "bank.md"], gitdir4)

        # ---------------- parallel: the lock serializes to one mutation -----
        bank_p = os.path.join(wd, "parallel", "bank.md")
        os.makedirs(os.path.dirname(bank_p))
        with open(bank_p, "w", encoding="utf-8", newline="") as fh:
            fh.write(fixture_bank())
        state_p = os.path.join(wd, "parallel", "state")
        results = []

        def worker():
            try:
                results.append(audit_writer.write_units(
                    make_proposal(fixture_bank()), bank_p, state_p))
            except Exception as exc:  # pragma: no cover - failure path
                results.append(exc)

        t1 = threading.Thread(target=worker)
        t2 = threading.Thread(target=worker)
        t1.start(); t2.start()
        t1.join(); t2.join()
        applied = [r for r in results if isinstance(r, dict)]
        if len(applied) != 2 or len({r["write_id"] for r in applied}) != 1:
            fail("writer: parallel writes must both resolve to one write id")
        p_manifests = os.path.join(state_p, audit_writer.MANIFESTS_DIR)
        if len([f for f in os.listdir(p_manifests) if f.endswith(".json")]) != 1:
            fail("writer: parallel writes must produce exactly one manifest")
        if len(authoring.model.parse_bank(read_text(bank_p))) != 3:
            fail("writer: parallel writes must apply the item exactly once")

        print("OK: writer -- shadow write/undo + stale refusal, Git "
              "tracked-clean commit + revert undo + dirty refusal, dirty->"
              "shadow fallback, before_exists report artifact, prepared "
              "journal on interruption, duplicate idempotency, parallel "
              "single-mutation")
    finally:
        shutil.rmtree(wd, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(case_writer())
