#!/usr/bin/env python3
"""Recompute the PLANNING-DIRECTIVES budget table.

The rules B1 to B6 were written against numbers measured once, by hand, on
2026-08-21. A rule with no scoreboard decays into a preference. This prints the
same table on demand so the ratio can be watched instead of remembered.

Read-only. Run from the repository root.
"""
import subprocess
import sys
from pathlib import Path

SKIP = {".git", "node_modules", "deps", "vendor", "__pycache__", ".codex"}


def walk(root, suffix):
    for p in Path(root).rglob(f"*{suffix}"):
        if any(part in SKIP for part in p.parts):
            continue
        yield p


def count_lines(paths):
    files = 0
    lines = 0
    for p in paths:
        try:
            lines += sum(1 for _ in p.open(encoding="utf-8", errors="ignore"))
        except OSError:
            continue
        files += 1
    return files, lines


def git(*args):
    out = subprocess.run(("git",) + args, capture_output=True, text=True)
    return out.stdout


def main():
    root = Path(".").resolve()
    if not (root / ".planning").is_dir():
        sys.exit("run this from the itembank repository root")

    plan_md = [p for p in walk(".", ".md") if ".planning" in p.parts]
    other_md = [p for p in walk(".", ".md") if ".planning" not in p.parts]
    md_files, md_lines = count_lines(plan_md)
    doc_files, doc_lines = count_lines(other_md)
    all_py = list(walk(".", ".py"))
    py_files, py_lines = count_lines(p for p in all_py if "tests" not in p.parts)
    test_files, test_lines = count_lines(p for p in all_py if "tests" in p.parts)

    summaries = list(walk(".planning", "-SUMMARY.md"))
    sum_files, sum_lines = count_lines(summaries)
    plans = list(walk(".planning", "-PLAN.md"))
    unsummarized = sum(
        1 for p in plans
        if not p.with_name(p.name.replace("-PLAN.md", "-SUMMARY.md")).exists()
    )

    subjects = git("log", "--pretty=%s")
    docs = sum(1 for s in subjects.splitlines() if s.startswith("docs"))
    code = sum(
        1 for s in subjects.splitlines()
        if s.split("(")[0].split(":")[0] in {"feat", "fix", "test", "refactor", "perf", "chore", "build"}
    )

    ratio = md_lines / py_lines if py_lines else 0.0

    print(f"{'Thing':<40} {'Count':>10}")
    print("-" * 51)
    print(f"{'.planning prose (lines)':<40} {md_lines:>10,}")
    print(f"{'  across markdown files':<40} {md_files:>10,}")
    print(f"{'Other markdown (lines)':<40} {doc_lines:>10,}")
    print(f"{'  across markdown files':<40} {doc_files:>10,}")
    print(f"{'Runtime Python, tests excluded':<40} {py_lines:>10,}")
    print(f"{'  across python files':<40} {py_files:>10,}")
    print(f"{'Test Python (lines)':<40} {test_lines:>10,}")
    print(f"{'  across python files':<40} {test_files:>10,}")
    print(f"{'-SUMMARY.md files':<40} {sum_files:>10,}")
    print(f"{'  holding lines':<40} {sum_lines:>10,}")
    print(f"{'Plan files with no summary':<40} {unsummarized:>10,} of {len(plans)}")
    print(f"{'Commits, docs':<40} {docs:>10,}")
    print(f"{'Commits, code types':<40} {code:>10,}")
    print("-" * 51)
    print(f"{'Prose per line of runtime code':<40} {ratio:>10.2f}")
    print()
    print("Baseline hand-measured 2026-08-21: ratio 2.7, prose 111,747 lines across")
    print("673 files, summaries 129 holding 23,261, docs 391 vs code 367, 71 of 200")
    print("plans unsummarized. That prose count does NOT reproduce here at a nearly")
    print("identical file count, so the two are measuring different sets. Trust this")
    print("script's series against itself, not against the hand-measured row.")
    print("B1 says a summary is exceptional. If the summary count keeps climbing,")
    print("B1 is not being followed, whatever the plans say.")


if __name__ == "__main__":
    main()
