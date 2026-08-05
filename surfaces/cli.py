"""The command line: the four commands that need no surface, and the parser.

`main` is the only place that knows every command exists. Each surface exports a
`cmd_*` and stays unaware of argparse, so a new front end is a new module rather
than an edit here and there.
"""
import argparse, collections, os, sys

from model import BANK_FILE_HINTS, SPEC, lint, load, parse_bank
from surfaces.anki import cmd_export
from surfaces.day import cmd_day
from surfaces.quiz import cmd_build, cmd_serve
from surfaces.session import cmd_next, cmd_report, cmd_start, cmd_submit
from surfaces.study import cmd_study


def cmd_spec(a):
    print(SPEC)
    return 0


def cmd_lint(a):
    qs = load(a.bank)
    errors, warnings = lint(qs)
    for e in errors:
        print("error  " + e)
    for w in warnings:
        print("warn   " + w)
    print("\n%d items, %d errors, %d warnings" % (len(qs), len(errors), len(warnings)))
    return 1 if errors else 0


def cmd_stats(a):
    qs = load(a.bank)
    counts = collections.Counter(q["type"] for q in qs)
    print("%d items" % len(qs))
    for k, v in counts.most_common():
        print("  %-6s %4d  %4.0f%%" % (k, v, v / len(qs) * 100))
    objs = collections.Counter(q["objective"] for q in qs if q["objective"])
    if objs:
        print("\nobjective coverage (%d distinct)" % len(objs))
        for k, v in objs.most_common(12):
            print("  %3d  %s" % (v, k))
    diff = collections.Counter(q["difficulty"] for q in qs if q["difficulty"])
    if diff:
        print("\ndifficulty")
        for k, v in diff.most_common():
            print("  %3d  %s" % (v, k))
    mc = [q for q in qs if q["type"] == "mc" and q["correct"]]
    if mc:
        pos = collections.Counter(q["correct"][0] for q in mc)
        print("\nanswer position, %d multiple-choice items" % len(mc))
        for k in sorted(pos):
            print("  %s  %3d  %4.0f%%" % (k, pos[k], pos[k] / len(mc) * 100))
    return 0


def cmd_guard(a):
    """Fail if any markdown outside fixtures/ parses as a real question bank.

    The mechanical half of the content rule. Discipline does not survive a
    late-night commit; a CI check does.
    """
    offenders = []
    for root, dirs, files in os.walk(a.dir):
        dirs[:] = [d for d in dirs if d not in (".git", "fixtures", ".github")]
        for f in files:
            if not f.lower().endswith(".md"):
                continue
            p = os.path.join(root, f)
            try:
                n = len(parse_bank(open(p, encoding="utf-8").read()))
            except Exception:
                continue
            if n > 0 or any(h in f.lower() for h in BANK_FILE_HINTS):
                offenders.append((p, n))
    for p, n in offenders:
        print("error  %s parses as a question bank (%d items). Banks belong in your "
              "private vault, never in this repo." % (p, n))
    print("\n%d offending files" % len(offenders))
    return 1 if offenders else 0


def main():
    ap = argparse.ArgumentParser(
        prog="itembank",
        description="Author, validate and render exam-style question banks in markdown.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("spec", help="print the format contract")
    s.set_defaults(fn=cmd_spec)

    s = sub.add_parser("lint", help="validate a bank")
    s.add_argument("bank")
    s.set_defaults(fn=cmd_lint)

    s = sub.add_parser("build", help="render an interactive HTML quiz (nothing is saved)")
    s.add_argument("bank")
    s.add_argument("out", nargs="?")
    s.add_argument("--force", action="store_true", help="build despite lint errors")
    s.add_argument("--blind", action="store_true",
                   help="hide model answers on short items, for a self-marked sitting")
    s.set_defaults(fn=cmd_build)

    s = sub.add_parser("serve", help="sit the quiz with every answer written to disk")
    s.add_argument("bank")
    s.add_argument("--out", help="attempt file (default: _attempts/<bank>_attempt_<date>.md)")
    s.add_argument("--port", type=int, default=8731)
    s.add_argument("--reveal", action="store_true",
                   help="show model answers after each short item; off by default so an "
                        "early item cannot teach a later one")
    s.add_argument("--no-open", action="store_true", dest="no_open",
                   help="do not launch a browser")
    s.add_argument("--force", action="store_true", help="serve despite lint errors")
    s.set_defaults(fn=cmd_serve)

    s = sub.add_parser("stats", help="item mix, coverage, answer-position skew")
    s.add_argument("bank")
    s.set_defaults(fn=cmd_stats)

    s = sub.add_parser("start", help="start a resumable JSON assessment session")
    s.add_argument("bank")
    s.add_argument("--count", type=int, default=10)
    s.add_argument("--objective", default="", help="limit the session to one objective")
    s.add_argument("--mode", default="diagnostic",
                   choices=("diagnostic", "practice", "exam", "remediation"))
    s.add_argument("--seed", type=int, default=0, help="deterministic item-selection seed")
    s.add_argument("--out", help="session JSON path")
    s.add_argument("--force", action="store_true", help="start despite lint errors")
    s.set_defaults(fn=cmd_start)

    s = sub.add_parser("next", help="return the next item in a JSON assessment session")
    s.add_argument("session")
    s.set_defaults(fn=cmd_next)

    s = sub.add_parser("submit", help="score and record the current session response")
    s.add_argument("session")
    s.add_argument("--answer", required=True,
                   help="response value, or a JSON array/object for structured items")
    s.set_defaults(fn=cmd_submit)

    s = sub.add_parser("report", help="summarize a JSON assessment session")
    s.add_argument("session")
    s.set_defaults(fn=cmd_report)

    s = sub.add_parser("study", help="render flashcards and a session-only Learn loop")
    s.add_argument("bank")
    s.add_argument("out", nargs="?")
    s.add_argument("--force", action="store_true", help="study despite lint errors")
    s.set_defaults(fn=cmd_study)

    s = sub.add_parser("export", help="export a bank as Anki TSV")
    s.add_argument("bank")
    s.add_argument("out")
    s.add_argument("--format", choices=("basic", "cloze"), default="basic")
    s.add_argument("--force", action="store_true", help="export despite lint errors")
    s.set_defaults(fn=cmd_export)

    s = sub.add_parser("day", help="today's work across every subject, ticked and logged")
    s.add_argument("plan", help="markdown document holding a dated plan table")
    s.add_argument("--log", help="daily log file (default: daily_log.md beside the plan)")
    s.add_argument("--lanes", help="wiring file (default: lanes.md beside the plan)")
    s.add_argument("--due", action="store_true",
                   help="print what is outstanding across every lane and exit")
    s.add_argument("--date", help="run a different day, for backfilling a missed one")
    s.add_argument("--port", type=int, default=8732)
    s.add_argument("--lan", action="store_true",
                   help="bind all interfaces so a phone on the same wifi can open it")
    s.add_argument("--check", action="store_true",
                   help="print today's row and exit, without serving")
    s.add_argument("--no-open", action="store_true", dest="no_open",
                   help="do not launch a browser")
    s.set_defaults(fn=cmd_day)

    s = sub.add_parser("guard", help="fail if a real bank was committed")
    s.add_argument("dir", nargs="?", default=".")
    s.set_defaults(fn=cmd_guard)

    a = ap.parse_args()
    sys.exit(a.fn(a))
