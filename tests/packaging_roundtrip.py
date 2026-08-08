#!/usr/bin/env python3
"""DEL-01/DEL-02 coverage: `python build.py` produces a real `.pyz`, and that
artifact builds, runs, and is plain Python inside -- proved by building one
into a temp directory and driving it as a subprocess exactly the way a
learner or agent does, not by inspecting `build.py`'s source.

Standard library only, runnable as `python tests/packaging_roundtrip.py`.
"""
import fnmatch, hashlib, os, shutil, subprocess, sys, tempfile, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
FIXTURE = os.path.join(ROOT, "fixtures", "sample_bank.md")

import build                                                # noqa: E402
import itembank                                             # noqa: E402

# The same shapes .gitignore already names for learner evidence and any real
# bank; a filename matching one of these has no business inside a release
# artifact built from build.py's own STAGE_FILES/STAGE_DIRS allowlists.
BANK_OR_EVIDENCE_PATTERNS = ("session_*.json", "*_attempt_*.md", "*_quiz.html",
                             "*_study.html")

# Locked verbatim in 02.1-UI-SPEC.md's Copywriting Contract for the launcher
# failure path, shared word-for-word by all three OS shims -- defined once
# here so the three assertions below cannot drift from each other or from
# the shims themselves.
LOCKED_LAUNCHER_FAILURE_SENTENCE = (
    "itembank needs Python 3.11 or newer. Install it from https://python.org "
    "and run this file again.")


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def test_builds_into_a_temp_directory(out_dir):
    artifact = build.build(out_dir)
    if not os.path.exists(artifact):
        fail("build.build() returned a path that does not exist: %r" % artifact)
    if os.path.getsize(artifact) == 0:
        fail("built artifact is empty: %r" % artifact)
    base = os.path.basename(artifact)
    if not (base.startswith("itembank-") and base.endswith(".pyz")
            and itembank.__version__ in base):
        fail("artifact basename %r does not carry itembank.__version__ (%r) "
             "between the itembank- prefix and the .pyz suffix" %
             (base, itembank.__version__))
    return artifact


def test_artifact_runs_every_resource_reading_command(artifact):
    """The two schema-reading commands (config, schema item) are the point
    of this test: they are what a __file__-relative open() breaks.
    """
    cwd = tempfile.mkdtemp()
    try:
        commands = [
            ["spec"],
            ["lint", FIXTURE],
            ["stats", FIXTURE],
            ["config", "--base", cwd],
            ["schema", "item"],
        ]
        for args in commands:
            r = subprocess.run([sys.executable, artifact] + args,
                               capture_output=True, text=True, encoding="utf-8",
                               cwd=cwd)
            if r.returncode != 0:
                fail("%r exited %d: %s" % (args, r.returncode, r.stderr))
    finally:
        shutil.rmtree(cwd, ignore_errors=True)


def test_artifact_is_plain_python_inside(artifact):
    with zipfile.ZipFile(artifact) as zf:
        names = zf.namelist()
        py_members = [n for n in names if n.endswith(".py")]
        if not py_members:
            fail("artifact has no .py members at all")
        model_text = None
        for name in py_members:
            data = zf.read(name)
            try:
                text = data.decode("utf-8")
            except UnicodeDecodeError as exc:
                fail("%s does not decode as UTF-8: %s" % (name, exc))
                return
            if name == "model.py":
                model_text = text
        if model_text is None or "def parse_bank" not in model_text:
            fail("model.py inside the artifact does not contain 'def parse_bank'")
        bad = [n for n in names if n.endswith(".pyc") or "__pycache__" in n]
        if bad:
            fail("artifact carries compiled/cache members: %r" % bad)


def test_no_evidence_or_bank_in_the_artifact(artifact):
    with zipfile.ZipFile(artifact) as zf:
        names = zf.namelist()
    bad = []
    for n in names:
        if n.startswith("_evidence/") or n.startswith("_attempts/"):
            bad.append(n)
            continue
        base = os.path.basename(n)
        if any(fnmatch.fnmatch(base, pat) for pat in BANK_OR_EVIDENCE_PATTERNS):
            bad.append(n)
    if bad:
        fail("artifact carries evidence/bank-shaped members: %r" % bad)


def test_checksums_cover_every_artifact(out_dir):
    build.copy_launchers(out_dir)
    checksums = build.sha256sums(out_dir)
    lines = [l for l in open(checksums, encoding="utf-8").read().splitlines() if l]
    listed = {}
    for line in lines:
        digest, name = line.split("  ", 1)
        listed[name] = digest
        path = os.path.join(out_dir, name)
        if not os.path.exists(path):
            fail("SHA256SUMS.txt names %r, which does not exist" % name)
        actual = hashlib.sha256(open(path, "rb").read()).hexdigest()
        if actual != digest:
            fail("checksum mismatch for %r: recorded %s, actual %s" %
                 (name, digest, actual))
    if "itembank.bat" not in listed:
        fail("SHA256SUMS.txt does not list itembank.bat")
    if not any(n.startswith("itembank-") and n.endswith(".pyz") for n in listed):
        fail("SHA256SUMS.txt does not list the .pyz artifact")


def test_every_launcher_ships(out_dir):
    """Every file in launchers/ ends up in the release directory and in
    SHA256SUMS.txt with a matching digest -- read from os.listdir() rather
    than a hardcoded name list, so a fourth shim added later is covered
    automatically instead of silently unasserted.
    """
    names = os.listdir(build.LAUNCHER_DIR)
    if not names:
        fail("build.LAUNCHER_DIR (%r) is empty" % build.LAUNCHER_DIR)
    checksums_path = os.path.join(out_dir, "SHA256SUMS.txt")
    lines = [l for l in open(checksums_path, encoding="utf-8").read().splitlines() if l]
    listed = {}
    for line in lines:
        digest, name = line.split("  ", 1)
        listed[name] = digest
    for name in names:
        path = os.path.join(out_dir, name)
        if not os.path.exists(path):
            fail("launcher %r was not copied into %r" % (name, out_dir))
        if name not in listed:
            fail("SHA256SUMS.txt does not list launcher %r" % name)
        actual = hashlib.sha256(open(path, "rb").read()).hexdigest()
        if actual != listed[name]:
            fail("checksum mismatch for launcher %r: recorded %s, actual %s" %
                 (name, listed[name], actual))


def test_launchers_carry_the_locked_failure_sentence():
    """All three shims print the identical locked sentence and each names
    an explicit interpreter invocation rather than relying on file
    association state.
    """
    for name in os.listdir(build.LAUNCHER_DIR):
        text = open(os.path.join(build.LAUNCHER_DIR, name), encoding="utf-8").read()
        if LOCKED_LAUNCHER_FAILURE_SENTENCE not in text:
            fail("%s does not carry the locked failure sentence" % name)
    bat_path = os.path.join(build.LAUNCHER_DIR, "itembank.bat")
    bat_text = open(bat_path, encoding="utf-8").read()
    if "py -3" not in bat_text:
        fail("itembank.bat does not name the Windows Python launcher (py -3)")
    for name in ("itembank.command", "itembank.desktop"):
        path = os.path.join(build.LAUNCHER_DIR, name)
        text = open(path, encoding="utf-8").read()
        if "python3" not in text:
            fail("%s does not name python3 explicitly" % name)


def main():
    out_dir = tempfile.mkdtemp()
    try:
        artifact = test_builds_into_a_temp_directory(out_dir)
        test_artifact_runs_every_resource_reading_command(artifact)
        test_artifact_is_plain_python_inside(artifact)
        test_no_evidence_or_bank_in_the_artifact(artifact)
        test_checksums_cover_every_artifact(out_dir)
        test_every_launcher_ships(out_dir)
        test_launchers_carry_the_locked_failure_sentence()
    finally:
        shutil.rmtree(out_dir, ignore_errors=True)
    print("packaging contract: ok (DEL-01/DEL-02 -- builds, runs every "
          "resource-reading command from outside the checkout, is plain "
          "Python inside, carries no evidence/bank content, checksums cover "
          "every artifact, all three OS launchers ship and carry the locked "
          "failure sentence)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
