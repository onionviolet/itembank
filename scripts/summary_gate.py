"""Hold the 2026-08-21 summary rule mechanically.

PLANNING-DIRECTIVES B1 and EXEC-CONTEXT say a `-SUMMARY.md` is exceptional:
written only when a plan was left incomplete or a measured fact contradicts
it; otherwise the commit body is the record. Prose alone did not hold. In the
ten days after the rule was written, 61 new summaries landed (478 KB), and 56
of them contained the very words a text check would look for, so a keyword
gate would be toothless. This gate checks the two things that are cheap to
check and that carry the cost: a summary not in the baseline must open with a
`## Why this summary exists` heading naming which condition holds, and must
stay under SIZE_CAP bytes.

The baseline (`.planning/summary-baseline.txt`) lists every summary that
existed when the gate landed on 2026-09-03. Those are grandfathered. Rebuild
it only when deliberately raising the floor (`--rebaseline`), never to get a
red build green.

Exit 0 when clean, 1 with every offender listed otherwise.
"""
import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHASES = os.path.join(ROOT, ".planning", "phases")
BASELINE = os.path.join(ROOT, ".planning", "summary-baseline.txt")
HEADING = "## Why this summary exists"
SIZE_CAP = 3000
HEAD_LINES = 12


def summaries():
    """Every plan summary under .planning/phases, as sorted repo-relative posix paths."""
    found = []
    for dirpath, _dirs, files in os.walk(PHASES):
        for name in files:
            if name.endswith("-SUMMARY.md"):
                rel = os.path.relpath(os.path.join(dirpath, name), ROOT)
                found.append(rel.replace(os.sep, "/"))
    return sorted(found)


def read_baseline():
    if not os.path.exists(BASELINE):
        return set()
    with open(BASELINE, encoding="utf-8") as fh:
        return set(line.strip() for line in fh if line.strip() and not line.startswith("#"))


def check(path):
    """Return the list of complaints for one summary outside the baseline."""
    full = os.path.join(ROOT, path)
    complaints = []
    size = os.path.getsize(full)
    if size > SIZE_CAP:
        complaints.append("%d bytes, cap is %d; the commit body is the record" % (size, SIZE_CAP))
    with open(full, encoding="utf-8", errors="replace") as fh:
        head = [next(fh, "") for _ in range(HEAD_LINES)]
    if not any(line.strip() == HEADING for line in head):
        complaints.append("missing `%s` in the first %d lines; say which of the two "
                          "conditions holds (plan left incomplete, or a measured fact "
                          "contradicts the plan)" % (HEADING, HEAD_LINES))
    return complaints


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--rebaseline", action="store_true",
                    help="rewrite the baseline from the summaries present now")
    args = ap.parse_args(argv)

    present = summaries()
    if args.rebaseline:
        with open(BASELINE, "w", encoding="utf-8") as fh:
            fh.write("# Plan summaries grandfathered by scripts/summary_gate.py.\n")
            fh.write("# Rewritten by --rebaseline; do not hand-edit to pass a build.\n")
            fh.write("\n".join(present) + "\n")
        print("baseline written: %d summaries" % len(present))
        return 0

    baseline = read_baseline()
    new = [p for p in present if p not in baseline]
    offenders = []
    for path in new:
        for why in check(path):
            offenders.append("%s: %s" % (path, why))
    print("summaries: %d present, %d in baseline, %d new" % (len(present), len(baseline), len(new)))
    if offenders:
        print("\n".join(offenders))
        return 1
    print("summary gate clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
