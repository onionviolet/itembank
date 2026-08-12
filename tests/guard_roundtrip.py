#!/usr/bin/env python3
"""`itembank guard` coverage: the content gate must refuse real banks and
corpus content, and must not refuse the repo's own documentation.

The gate had no test. Its only exercise was a CI step that ran after four
earlier steps, so when the phase-05 grammar widening made README's fenced
"here is the whole format" sample parse as a real item, nothing caught it --
the CI job was already failing further up and never reached the guard. This
drives the CLI as a subprocess, the way CI does.

Standard library only, runnable as `python tests/guard_roundtrip.py`.
"""
import os, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
FIXTURES = os.path.join(ROOT, "fixtures")


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def guard(path):
    """Run `itembank guard <path>`; return (exit_code, combined output)."""
    proc = subprocess.run(
        [sys.executable, os.path.join(ROOT, "itembank.py"), "guard", path],
        capture_output=True, text=True)
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def write(tmp, name, text):
    path = os.path.join(tmp, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path


DOC_WITH_FENCED_SAMPLE = """# How to author

Here is the whole format:

```
Q1. An operator notices a low chlorine residual at the far end of the
     distribution network. What is the most likely explanation?
     A) Dead-end stagnation  B) A leaking service line  C) Pump cavitation
     CORRECT: A

Q2. Name two lab checks before clearing a main for service.  [TYPE: short]
     MODEL: turbidity, total chlorine
```

That is the whole format.
"""


def check_fenced_sample_is_not_a_bank():
    """A doc that only demonstrates the grammar inside a fence passes. This
    is the exact shape of README.md, which the gate started refusing."""
    tmp = tempfile.mkdtemp(prefix="guard_doc_")
    try:
        write(tmp, "authoring.md", DOC_WITH_FENCED_SAMPLE)
        code, out = guard(tmp)
        if code != 0:
            fail("a fenced format sample must not read as a bank: %s" % out)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_repo_itself_passes():
    """The gate's real subject: this checkout. Guarding the repo is the CI
    step verbatim, so a doc drifting into bank shape fails here first."""
    code, out = guard(ROOT)
    if code != 0:
        fail("the repository must pass its own content gate: %s" % out)


def check_real_bank_is_refused():
    """The gate still does its job -- including a bank whose LESSON section
    carries fenced code, which is what the fence-stripping must not blind
    it to."""
    for fixture, label in (("sample_bank.md", "a plain bank"),
                           ("lesson_bank.md", "a bank with fenced lesson "
                                              "code")):
        src = os.path.join(FIXTURES, fixture)
        if not os.path.exists(src):
            continue
        tmp = tempfile.mkdtemp(prefix="guard_bank_")
        try:
            # Renamed, so this is the parse result and not a filename hint.
            shutil.copy(src, os.path.join(tmp, "notes.md"))
            code, out = guard(tmp)
            if code == 0:
                fail("%s must be refused by the gate" % label)
            if "parses as a question bank" not in out:
                fail("%s must be refused by name, got: %s" % (label, out))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


def check_bank_filename_hint_is_refused():
    """The filename half of the gate is independent of the parse."""
    tmp = tempfile.mkdtemp(prefix="guard_hint_")
    try:
        write(tmp, "emt_mc_bank.md", "# not actually a bank\n\nProse only.\n")
        code, out = guard(tmp)
        if code == 0:
            fail("a bank-hinted filename must be refused: %s" % out)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    checks = [check_fenced_sample_is_not_a_bank,
              check_repo_itself_passes,
              check_real_bank_is_refused,
              check_bank_filename_hint_is_refused]
    for check in checks:
        check()
        print("ok  %s" % check.__name__)
    print("guard roundtrip: ok (%d checks)" % len(checks))


if __name__ == "__main__":
    main()
