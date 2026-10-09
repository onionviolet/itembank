#!/usr/bin/env python3
"""Run the CI gates locally, in one command, before pushing.

The problem this closes: CI runs twelve named gates, and locally an agent or a
human finishing a change has to remember which of them apply. Nobody does. The
gate that only fires after the push is the gate that finds the breakage after
the handoff was already written, which is the same failure this repo was
founded on (a prose contract with no feedback signal) moved up one level from
question banks to the build itself.

    python scripts/preflight.py            # every portable gate
    python scripts/preflight.py --quick    # skip the two slow suites
    python scripts/preflight.py --list     # gate ids and their CI step names
    python scripts/preflight.py --source-only  # defer app builds and installs

Exit 0 = every gate that ran passed. Exit 1 = at least one failed.

This is a mirror, not a reimplementation. Each gate names the exact CI step it
stands in for, and `tests/preflight_roundtrip.py` fails the build if a CI step
appears that no gate claims, so the mirror cannot silently drift the way the
old hand-listed test file did. Two CI steps are deliberately not mirrored and
are named in CI_ONLY below with the reason.
Local architecture checks are named separately in LOCAL_ONLY.

Standard library only, same as everything else in scripts/.
"""
import argparse
import ast
import filecmp
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable

# Local architecture checks supplement the mirrored CI steps.
LOCAL_ONLY = {
    "Python module size warning":
        "local advisory gate; warns for tracked root and surfaces Python "
        "modules over 3,000 lines without affecting exit status",
    "Core modules do not import client surfaces":
        "local architecture gate; scans every root Python module except "
        "the launcher, packager, and server",
}

# CI steps this script deliberately does not mirror, and why. Named here so the
# drift test can tell "not mirrored on purpose" from "quietly forgotten".
CI_ONLY = {
    "Install pinned optional test dependencies":
        "environment setup, not a gate; CI installs reviewed LTI and source "
        "adapter pins so their success paths run alongside missing-package refusals",
    "Runtime output matches published schema":
        "a 40-line shell pipeline over /tmp; reimplementing it here would create "
        "a second contract that can disagree with CI, which is the exact failure "
        "this repo exists to prevent. Push and read the CI log for this one.",
}

# The linter must keep reporting each of these on the deliberately broken
# fixture. Kept identical to the CI step's list; the drift test compares them.
BROKEN_MESSAGES = [
    "SELECT is 2", "does not exist", "not in CATEGORIES", "duplicate steps",
    "no WHY BEST", "stem duplicates", "WOULD be correct", "CONFIDENCE is low",
    "does not match any lesson heading", "collides with",
    "is not referenced by any item",
]

PATH_LEAK = re.compile(r"C:/Users|C:\\Users|/Users/wayba|wayba")
PATH_LEAK_TARGETS = ["AGENTS.md", "README.md", ".agents", ".claude",
                     "reasonix.toml.example"]


def run(cmd, **kw):
    """Run a command from the repo root and return (returncode, combined output)."""
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", **kw)
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def gate_lint_clean():
    code, out = run([PY, "itembank.py", "lint", "fixtures/sample_bank.md"])
    if code != 0:
        return False, out
    errors = [l for l in out.splitlines() if l.startswith("error")]
    if errors:
        return False, "the sample fixture reports errors:\n" + "\n".join(errors)
    return True, ""


def gate_broken_caught():
    code, out = run([PY, "itembank.py", "lint", "fixtures/broken_bank.md"])
    if code == 0:
        return False, "the linter passed a deliberately broken bank; it regressed"
    missing = [m for m in BROKEN_MESSAGES if m not in out]
    if missing:
        return False, "the linter no longer reports: " + ", ".join(missing)
    return True, ""


def gate_build():
    tmp = tempfile.mkdtemp(prefix="itembank-preflight-")
    try:
        code, out = run([PY, "itembank.py", "build", "fixtures/sample_bank.md",
                         os.path.join(tmp, "out.html")])
        return code == 0, out
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


APP_BUILD_TESTS = frozenset({
    "a5_integrated_package_roundtrip.py", "math_offline_roundtrip.py",
    "packaging_roundtrip.py",
})


def gate_tests(source_only=False):
    # Every file under tests/, matching CI. The suite takes minutes, so it
    # reports each file as it finishes rather than going dark; a gate you
    # cannot watch is a gate you interrupt.
    tests = sorted(f for f in os.listdir(os.path.join(ROOT, "tests"))
                   if f.endswith(".py"))
    failures = []
    deferred = []
    for i, name in enumerate(tests, 1):
        if source_only and name in APP_BUILD_TESTS:
            deferred.append(name)
            print("        deferred app build: %s" % name, flush=True)
            continue
        print("        [%d/%d] %s" % (i, len(tests), name), flush=True)
        code, out = run([PY, os.path.join("tests", name)])
        if code != 0:
            failures.append("== tests/%s\n%s" % (name, out.rstrip()))
    executed = len(tests) - len(deferred)
    summary = ("Python suite: %d discovered, %d executed, %d passed, "
               "%d failed, %d deferred app-build checks."
               % (len(tests), executed, executed - len(failures),
                  len(failures), len(deferred)))
    if deferred:
        summary += "\nApp-build checks deferred: " + ", ".join(deferred)
    if failures:
        return False, summary + "\n" + "\n".join(failures)
    return True, summary


def gate_clean_tree():
    """A test that rewrites tracked content edits the record it is checking.

    `tests/file_fault_tracer.py` rewrote `14A-TRACER-REPORT.md` on every run,
    so two commits carried a stray run's timings into unrelated work and a
    third had to put 14A's numbers back. Ordered after the suite gate, so what
    it reports is what the suite just did.
    """
    code, out = run(["git", "status", "--porcelain"])
    if code != 0:
        return None, "git is not available here; CI still runs this gate"
    dirty = [line for line in out.splitlines() if line.strip()]
    if not dirty:
        return True, "working tree clean"
    _, diff = run(["git", "diff"])
    return False, ("the suite left the working tree dirty:\n%s\n\n"
                    "Write to a temp dir instead, or gate the write behind an "
                    "explicit flag the way tests/file_fault_tracer.py does."
                    "\n\n%s" % ("\n".join(dirty), diff.rstrip()))


def gate_js_tests(source_only=False):
    if shutil.which("npm") is None or shutil.which("node") is None:
        return None, "node or npm is not on PATH; CI still runs this gate"
    if source_only:
        try:
            with open(os.path.join(ROOT, "tests/js/package.json")) as stream:
                expected = json.load(stream)["dependencies"]["jsdom"]
            with open(os.path.join(ROOT, "tests/js/node_modules/jsdom/package.json")) as stream:
                installed = json.load(stream)["version"]
        except (OSError, ValueError, KeyError):
            return None, "JS dependency installation deferred in source-only mode"
        if installed != expected:
            return None, "installed JS dependency differs from the pin; installation deferred"
    else:
        code, out = run(["npm", "ci", "--prefix", "tests/js"], shell=os.name == "nt")
        if code != 0:
            return False, out
    js = sorted(os.path.join("tests", "js", f)
                for f in os.listdir(os.path.join(ROOT, "tests", "js"))
                if f.endswith(".test.mjs"))
    # An explicit file list, not the directory: node resolves a bare directory
    # as a module on Windows and the tests cannot be run locally at all.
    code, out = run(["node", "--test", *js], shell=os.name == "nt")
    return code == 0, out


def gate_guard():
    code, out = run([PY, "itembank.py", "guard", "."])
    return code == 0, out


def gate_core_layers():
    """Reject static client imports anywhere in a root core module."""
    excluded = {"build.py", "itembank.py", "server.py"}
    violations = []
    checked = 0
    for name in sorted(os.listdir(ROOT)):
        path = os.path.join(ROOT, name)
        if not name.endswith(".py") or name in excluded or not os.path.isfile(path):
            continue
        checked += 1
        try:
            with open(path, encoding="utf-8") as source:
                tree = ast.parse(source.read(), filename=name)
        except (OSError, SyntaxError) as exc:
            violations.append("%s: cannot inspect imports: %s" % (name, exc))
            continue
        for node in ast.walk(tree):
            modules = []
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                modules = [node.module or ""]
            for module in modules:
                if module == "surfaces" or module.startswith("surfaces."):
                    violations.append("%s:%d: core imports %s" %
                                      (name, node.lineno, module))
    return not violations, ("\n".join(violations) if violations else
                            "%d core modules have no client imports" % checked)


def gate_module_size():
    """Report large tracked modules without failing preflight."""
    code, out = run(["git", "ls-files", "-z", "--", "*.py"])
    if code != 0:
        return True, "WARN: cannot inspect tracked Python module sizes: " + out.strip()
    oversized = []
    for name in out.split("\0"):
        if not name.endswith(".py") or ("/" in name and not name.startswith("surfaces/")):
            continue
        try:
            with open(os.path.join(ROOT, name), encoding="utf-8") as source:
                count = sum(1 for _ in source)
        except OSError as exc:
            print("WARN    size     %s: cannot count lines: %s" % (name, exc), flush=True)
            continue
        if count > 3000:
            oversized.append((count, name))
    if oversized:
        rows = sorted(oversized, key=lambda row: (-row[0], row[1]))
        return True, "WARN: Python modules over 3,000 lines:\n" + "\n".join(
            "%s: %d lines" % (name, count) for count, name in rows)
    return True, "no tracked root or surfaces Python modules over 3,000 lines"


def gate_skill_mirrors():
    # Python rather than `diff -rq`: diff is not on a stock Windows box, so the
    # shell version of this gate simply could not run locally.
    left = os.path.join(ROOT, ".agents", "skills")
    right = os.path.join(ROOT, ".claude", "skills")
    drift = []

    def walk(cmp_result, prefix=""):
        for name in cmp_result.left_only:
            drift.append("only in .agents/skills: %s%s" % (prefix, name))
        for name in cmp_result.right_only:
            drift.append("only in .claude/skills: %s%s" % (prefix, name))
        for name in cmp_result.diff_files:
            drift.append("differs: %s%s" % (prefix, name))
        for name, sub in cmp_result.subdirs.items():
            walk(sub, prefix + name + "/")

    walk(filecmp.dircmp(left, right))
    return not drift, "\n".join(drift)


def gate_readme_commands():
    code, out = run([PY, "scripts/check_readme_commands.py"])
    return code == 0, out


def gate_schemas():
    code, out = run([PY, "schema_validate.py", "--all", "schemas"])
    return code == 0, out


def gate_vendored():
    code, out = run([PY, "scripts/check_vendored.py"])
    return code == 0, out


def gate_paths():
    leaks = []
    for target in PATH_LEAK_TARGETS:
        full = os.path.join(ROOT, target)
        files = []
        if os.path.isdir(full):
            for dirpath, _, names in os.walk(full):
                files.extend(os.path.join(dirpath, n) for n in names)
        elif os.path.isfile(full):
            files.append(full)
        for path in files:
            try:
                with open(path, encoding="utf-8", errors="replace") as source_handle:
                    text = source_handle.read()
            except OSError:
                continue
            for lineno, line in enumerate(text.splitlines(), 1):
                if PATH_LEAK.search(line):
                    rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
                    leaks.append("%s:%d  %s" % (rel, lineno, line.strip()[:90]))
    return not leaks, "\n".join(leaks)


def gate_summaries():
    code, out = run([PY, "scripts/summary_gate.py"])
    return code == 0, out


# (gate id, CI step or local check name, function, slow?)
GATES = [
    ("size", "Python module size warning", gate_module_size, False),
    ("layers", "Core modules do not import client surfaces", gate_core_layers, False),
    ("lint", "Sample fixture lints clean", gate_lint_clean, False),
    ("broken", "Broken fixture is caught", gate_broken_caught, False),
    ("build", "Sample fixture builds", gate_build, False),
    ("guard", "No real question bank committed", gate_guard, False),
    ("mirrors", "Skill mirrors stay identical", gate_skill_mirrors, False),
    ("readme", "README command index names only shipped subcommands",
     gate_readme_commands, False),
    ("schemas", "Every published schema self-checks", gate_schemas, False),
    ("vendored", "Vendored artifacts match their recorded checksums",
     gate_vendored, False),
    ("paths", "No machine-specific path in agent docs or config", gate_paths, False),
    ("summaries", "New plan summaries stay short and justified", gate_summaries,
     False),
    ("tests", "Test suite", gate_tests, True),
    ("clean", "The test suite left the working tree clean", gate_clean_tree,
     True),
    ("js", "JS editor test runner", gate_js_tests, True),
]


def main():
    ap = argparse.ArgumentParser(description="Run the CI gates locally.")
    ap.add_argument("--quick", action="store_true",
                    help="skip the Python and JS suites")
    ap.add_argument("--list", action="store_true",
                    help="print the gate table and exit")
    ap.add_argument("--source-only", action="store_true",
                    help="defer fresh app archives and sample builds; use already installed JS dependencies")
    args = ap.parse_args()

    if args.list:
        for gate_id, step, _, slow in GATES:
            print("%-8s %-6s %s" % (gate_id, "slow" if slow else "fast", step))
        for step, why in CI_ONLY.items():
            print("%-8s %-6s %s\n%22s%s" % ("(none)", "ci", step, "", why))
        return 0

    failed, skipped = [], []
    if args.source_only:
        print("source-only: fresh app archives, sample builds and dependency installation are deferred", flush=True)
    for gate_id, step, fn, slow in GATES:
        if args.source_only and gate_id == "build":
            skipped.append(gate_id)
            print("skip    build    sample build deferred (--source-only)", flush=True)
            continue
        if args.quick and slow:
            skipped.append(gate_id)
            print("skip    %-8s (--quick)" % gate_id, flush=True)
            continue
        if slow:
            print("run     %-8s (slow)" % gate_id, flush=True)
        ok, out = (fn(source_only=True) if args.source_only and gate_id in ("tests", "js") else fn())
        if ok is None:
            skipped.append(gate_id)
            print("skip    %-8s %s" % (gate_id, out), flush=True)
            continue
        if ok and out.startswith("WARN:"):
            for line in out.removeprefix("WARN: ").splitlines():
                print("WARN    %-8s %s" % (gate_id, line), flush=True)
            continue
        if ok:
            print("ok      %-8s %s" % (gate_id, out.strip().splitlines()[0]
                                       if out.strip() else ""), flush=True)
            continue
        failed.append(gate_id)
        print("FAIL    %-8s (CI step: %s)" % (gate_id, step), flush=True)
        diagnostics = out.rstrip().splitlines()
        # Suite output starts with passing cases. Keep the later failures and
        # tracebacks visible for both Python and JavaScript diagnostics.
        if gate_id not in ("tests", "js"):
            diagnostics = diagnostics[:20]
        for line in diagnostics:
            print("        " + line)

    for step in CI_ONLY:
        print("ci-only %-8s %s" % ("-", step))

    if failed:
        print("\npreflight: FAILED on %s." % ", ".join(failed))
        return 1
    tail = " (%s skipped)" % ", ".join(skipped) if skipped else ""
    print("\npreflight: every gate that ran passed%s." % tail)
    return 0


if __name__ == "__main__":
    sys.exit(main())
