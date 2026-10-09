#!/usr/bin/env python3
"""preflight_roundtrip: the local gate mirror cannot drift from CI.

`scripts/preflight.py` exists so a change can be checked before it is pushed.
A mirror maintained by hand rots, and this repo already paid for that once:
the CI test-suite step used to name its test files explicitly and two files
existed that CI never ran. The fix there was to stop hand-listing. The fix
here is the same move applied to the mirror: every step name in
`.github/workflows/ci.yml` must be claimed by a preflight gate or listed in
`CI_ONLY` with a reason, and the broken-fixture message list must be
identical in both places.

Standard library only. Run directly: python tests/preflight_roundtrip.py
"""
import os
import contextlib
import io
import re
import sys
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import preflight  # noqa: E402

CI = os.path.join(ROOT, ".github", "workflows", "ci.yml")

failures = []


def check(condition, message):
    if not condition:
        failures.append(message)


ci_text = open(CI, encoding="utf-8").read()

# Step names, not `uses:` entries: `- name:` lines nested under steps.
ci_steps = re.findall(r"^      - name: (.+)$", ci_text, re.M)
check(len(ci_steps) >= 10, "parsed only %d CI steps; the regex has drifted "
      "from the workflow's indentation" % len(ci_steps))

claimed = {step for _, step, _, _ in preflight.GATES} | set(preflight.CI_ONLY)

unmirrored = [s for s in ci_steps if s not in claimed]
check(not unmirrored,
      "CI steps that no preflight gate claims and CI_ONLY does not excuse: %s"
      % ", ".join(unmirrored))

stale = [s for s in claimed if s not in ci_steps]
check(not stale,
      "preflight names steps that CI no longer has: %s" % ", ".join(stale))

# Every CI_ONLY entry carries a real reason, so "not mirrored" never becomes a
# silent dumping ground.
for step, why in preflight.CI_ONLY.items():
    check(len(why.strip()) > 30,
          "CI_ONLY[%r] needs a reason, not a placeholder" % step)

# The broken-fixture message list is duplicated by necessity (CI is shell, the
# mirror is Python). Duplication is fine; divergence is not.
# Read the `for msg in "..." "..."; do` list only. A plain quoted-string scan
# over the whole step also swallows the two echo lines, which are prose, not
# linter contract.
loop = re.search(r"for msg in\s+(.*?);\s*do",
                 ci_text.split("Broken fixture is caught")[1].split("- name:")[0],
                 re.S)
check(loop is not None, "the broken-fixture step no longer has a `for msg in` list")
ci_messages = re.findall(r'"([^"]+)"', loop.group(1)) if loop else []
check(sorted(ci_messages) == sorted(preflight.BROKEN_MESSAGES),
      "BROKEN_MESSAGES disagrees with CI.\n  CI:        %s\n  preflight: %s"
      % (sorted(ci_messages), sorted(preflight.BROKEN_MESSAGES)))

# Gate ids are unique and usable on a command line.
ids = [g[0] for g in preflight.GATES]
check(len(ids) == len(set(ids)), "duplicate preflight gate id: %s" % ids)

# Source-only verification must never launch one of the fresh archive tests,
# while default CI parity still runs the whole inventory.
names = sorted(preflight.APP_BUILD_TESTS) + ["protocol_roundtrip.py"]
with mock.patch.object(preflight.os, "listdir", return_value=names), \
        mock.patch.object(preflight, "run", return_value=(0, "")) as runner, \
        mock.patch("builtins.print"):
    ok, message = preflight.gate_tests(source_only=True)
    check(ok and runner.call_count == 1 and "deferred" in message,
          "source-only tests launched a fresh archive or hid the deferred gate")
    runner.reset_mock()
    preflight.gate_tests()
    check(runner.call_count == len(names), "default preflight omitted an archive test")

with mock.patch.object(preflight.shutil, "which", return_value="available"), \
        mock.patch.object(preflight, "run", return_value=(0, "")) as runner:
    ok, _message = preflight.gate_js_tests(source_only=True)
    check(ok is not False, "installed JS dependency inspection failed")
    check(not any(call.args[0][:2] == ["npm", "ci"] for call in runner.call_args_list),
          "source-only JS gate installed dependencies")

# Passing cases and long early failures must not hide a later failed test.
for gate_id in ("tests", "js"):
    diagnostics = "passing cases\n" * 30 + "== tests/later.py\nlate failure traceback"
    output = io.StringIO()
    with mock.patch.object(preflight, "GATES", [(gate_id, "Synthetic suite", lambda: (False, diagnostics), False)]), \
            mock.patch.object(sys, "argv", ["preflight.py"]), contextlib.redirect_stdout(output):
        status = preflight.main()
    check(status == 1 and "== tests/later.py" in output.getvalue() and "late failure traceback" in output.getvalue(),
          "preflight hid a later %s failure behind truncated diagnostics" % gate_id)

if failures:
    for f in failures:
        print("FAIL " + f)
    sys.exit(1)
print("preflight_roundtrip: ok (%d CI steps, %d mirrored gates, %d ci-only)"
      % (len(ci_steps), len(preflight.GATES), len(preflight.CI_ONLY)))
