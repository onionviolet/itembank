"""The command line: the four commands that need no surface, and the parser.

`main` is the only place that knows every command exists. Each surface exports a
`cmd_*` and stays unaware of argparse, so a new front end is a new module rather
than an edit here and there.
"""
import argparse, collections, json, os, sys

from model import BANK_FILE_HINTS, SPEC, lint, load, parse_bank
from surfaces.anki import cmd_export
from surfaces.daemon import cmd_daemon
from surfaces.day import cmd_day
from surfaces.evidence_cli import (cmd_evidence, cmd_id_assign, cmd_mark, cmd_render,
                                   cmd_retract)
from surfaces.migrate import cmd_migrate
from surfaces.protocol_cli import cmd_schema
from surfaces.quiz import cmd_build, cmd_serve
from surfaces.session import cmd_next, cmd_report, cmd_start, cmd_submit
from surfaces.settings import cmd_config
from surfaces.study import cmd_study


def cmd_spec(a):
    print(SPEC)
    return 0


def cmd_lint(a):
    qs = load(a.bank)
    errors, warnings = lint(qs)
    if a.json:
        payload = {
            "schema_version": 1,
            "bank": os.path.basename(a.bank),
            "items": len(qs),
            "errors": [e._asdict() for e in errors],
            "warnings": [w._asdict() for w in warnings],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 1 if errors else 0
    for e in errors:
        print("error  " + str(e))
    for w in warnings:
        print("warn   " + str(w))
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
    # Imported lazily and inside main(), not at module scope: itembank.py
    # itself does `from surfaces.cli import main`, and the built .pyz's
    # __main__.py does `from surfaces.cli import main` directly (bypassing
    # itembank.py entirely) -- a module-scope `from itembank import
    # __version__` here would circle back into a partially-initialized
    # surfaces.cli in that second case and break every command.
    import itembank

    ap = argparse.ArgumentParser(
        prog="itembank",
        description="Author, validate and render exam-style question banks in markdown.")
    ap.add_argument("--version", action="version",
                    version="%(prog)s " + itembank.__version__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("spec", help="print the format contract")
    s.set_defaults(fn=cmd_spec)

    s = sub.add_parser("lint", help="validate a bank")
    s.add_argument("bank")
    s.add_argument("--json", action="store_true",
                   help="emit the machine-readable lint contract instead of human lines")
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
    s.add_argument("--mode", default="practice",
                   choices=("diagnostic", "practice", "exam", "remediation", "drill"),
                   help="recorded on every response, so a drill sitting is distinguishable "
                        "from an exam sitting in the evidence")
    s.add_argument("--no-open", action="store_true", dest="no_open",
                   help="do not launch a browser")
    s.add_argument("--force", action="store_true", help="serve despite lint errors")
    s.set_defaults(fn=cmd_serve)

    s = sub.add_parser("daemon", help="one process on one port for every surface")
    s.add_argument("dir", nargs="?", default=".")
    s.add_argument("--port", type=int, default=None,
                   help="default: itembank.json's daemon.port, or 8730 if unset")
    s.add_argument("--lan", action="store_true",
                   help="bind all interfaces so a phone on the same wifi can open it")
    s.add_argument("--no-open", action="store_true", dest="no_open",
                   help="do not launch a browser")
    s.add_argument("--force", action="store_true", help="serve despite lint errors")
    s.set_defaults(fn=cmd_daemon)

    s = sub.add_parser("stats", help="item mix, coverage, answer-position skew")
    s.add_argument("bank")
    s.set_defaults(fn=cmd_stats)

    s = sub.add_parser("start", help="start a resumable JSON assessment session")
    s.add_argument("bank")
    s.add_argument("--count", type=int, default=10)
    s.add_argument("--objective", default="", help="limit the session to one objective")
    s.add_argument("--mode", default="diagnostic",
                   choices=("diagnostic", "practice", "exam", "remediation", "drill"))
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
    s.add_argument("--confidence", choices=("high", "medium", "low"), default=None,
                   help="the learner's self-rated confidence in this response, optional")
    s.set_defaults(fn=cmd_submit)

    s = sub.add_parser("report", help="summarize a JSON assessment session")
    s.add_argument("session")
    s.set_defaults(fn=cmd_report)

    s = sub.add_parser("evidence", help="read recorded response history across every "
                       "session and subject")
    s.add_argument("--objective", default="",
                   help="the objective to query; exact match unless --prefix is given")
    s.add_argument("--prefix", action="store_true",
                   help="match --objective as a prefix (emt:airway also matches "
                        "emt:airway.opa, never emt:airwaymanagement)")
    s.add_argument("--subject", default="",
                   help="filter by subject alone, ignoring --objective entirely")
    s.add_argument("--mode", default="",
                   help="filter by session mode (diagnostic, practice, exam, "
                        "remediation, drill)")
    s.add_argument("--session", default="", help="filter by session_id")
    s.add_argument("--since", default="",
                   help="only events at or after this date, YYYY-MM-DD")
    s.add_argument("--rebuild-index", action="store_true", dest="rebuild_index",
                   help="delete and rebuild the disposable query index before "
                        "querying; the index is a cache, so this loses nothing")
    s.add_argument("--base", default=".",
                   help="directory holding _evidence/ (default: current directory)")
    s.set_defaults(fn=cmd_evidence)

    s = sub.add_parser("retract", help="undo a recorded evidence event by appending a "
                       "reasoned compensating event; nothing is ever deleted (D-10)")
    s.add_argument("event_id")
    s.add_argument("--reason", required=True,
                   help="why this event is being retracted -- an undo with no stated "
                        "reason is not an audit trail")
    s.add_argument("--base", default=".",
                   help="directory holding _evidence/ (default: current directory)")
    s.set_defaults(fn=cmd_retract)

    s = sub.add_parser("render", help="regenerate the attempt markdown or session JSON for "
                       "one session from the evidence log; editing the output changes "
                       "nothing (D-11)")
    s.add_argument("kind", choices=("attempt", "session", "daily"),
                   help="which view to render; 'daily' is not yet implemented (plan 01-10)")
    s.add_argument("--session", required=True, help="the session_id to render")
    s.add_argument("--bank", help="the bank file (required for 'attempt' and 'session')")
    s.add_argument("--base", default=".",
                   help="directory holding _evidence/ (default: current directory)")
    s.add_argument("--out", help="write atomically to this path instead of stdout")
    s.set_defaults(fn=cmd_render)

    s = sub.add_parser("mark", help="record a batch of short-answer marks as timestamped "
                       "events; the attempt file no longer accepts a hand-edited MARK: "
                       "line (D-12)")
    s.add_argument("--session", required=True, help="the session_id being marked")
    s.add_argument("--base", default=".",
                   help="directory holding _evidence/ (default: current directory)")
    s.add_argument("--file", help="NDJSON batch file, one mark per line; '-' reads stdin")
    s.add_argument("--marks", help="inline JSON array of marks")
    s.add_argument("--item", help="single-mark convenience form: the item_ref to mark")
    s.add_argument("--verdict", choices=("pass", "fail"), default=None,
                   help="required with --item")
    s.set_defaults(fn=cmd_mark)

    s = sub.add_parser("id-assign", help="assign opaque ids and content-hash fingerprints "
                       "into a bank; the only command that writes into a bank -- lint "
                       "stays read-only by design")
    s.add_argument("banks", nargs="+")
    s.add_argument("--dry-run", action="store_true", dest="dry_run",
                   help="print the change set without writing anything")
    s.set_defaults(fn=cmd_id_assign)

    s = sub.add_parser("study", help="render flashcards and a session-only Learn loop")
    s.add_argument("bank")
    s.add_argument("out", nargs="?")
    s.add_argument("--force", action="store_true", help="study despite lint errors")
    s.set_defaults(fn=cmd_study)

    s = sub.add_parser("export", help="export a bank as Anki TSV or GIFT for LMS import")
    s.add_argument("bank")
    s.add_argument("out")
    s.add_argument("--format", choices=("basic", "cloze", "gift"), default="basic")
    s.add_argument("--strict", action="store_true",
                   help="GIFT export only: promote the multi scoring-divergence "
                        "warning to a per-item failure")
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

    s = sub.add_parser("schema", help="print the published JSON contracts the way "
                       "`spec` prints the format contract")
    s.add_argument("name", nargs="?")
    s.add_argument("--all", action="store_true",
                   help="emit the format contract, all five documents and the "
                        "command sequence to run a session, in one object")
    s.set_defaults(fn=cmd_schema)

    s = sub.add_parser("config", help="print the settings schema the way `spec` prints "
                       "the format contract")
    s.add_argument("action", nargs="?", choices=("schema", "set"))
    s.add_argument("key", nargs="?")
    s.add_argument("value", nargs="?")
    s.add_argument("--base", default=".",
                   help="directory holding itembank.json (default: current directory)")
    s.set_defaults(fn=cmd_config)

    s = sub.add_parser("migrate", help="one-time, re-runnable import of the three legacy "
                       "stores (_attempts/*.md, session JSON, daily_log.md) into the "
                       "evidence log; a dry run by default, pass --write to actually import")
    s.add_argument("--base", default=".",
                   help="directory holding the legacy stores and where _evidence/ is "
                        "written (default: current directory)")
    s.add_argument("--legacy-dir", dest="legacy_dir",
                   help="override where attempt markdown and session JSON are read from "
                        "(default: _attempts/ beside --base); must resolve inside --base "
                        "or the command refuses to read it (T-1-03)")
    s.add_argument("--bank",
                   help="fallback bank basename recorded on an imported event when it "
                        "cannot be inferred from the source filename")
    s.add_argument("--subject", default="",
                   help="prefix 'subject:' onto any imported objective that carries no "
                        "colon (D-06)")
    s.add_argument("--resolve-by-position", dest="resolve_by_position",
                   help="load BANK.md and resolve a legacy positional reference to that "
                        "item's current [ID:] by matching today's item number -- correct "
                        "ONLY if the bank has not been reordered since the record was "
                        "written; a wrong match attaches history to the wrong question "
                        "with nothing to tell you. A reference with no match in BANK.md "
                        "stays unresolved even with this flag.")
    s.add_argument("--write", action="store_true",
                   help="actually import; without this flag, migrate is a dry run that "
                        "reports the counts it expects and writes nothing")
    s.set_defaults(fn=cmd_migrate)

    s = sub.add_parser("guard", help="fail if a real bank was committed")
    s.add_argument("dir", nargs="?", default=".")
    s.set_defaults(fn=cmd_guard)

    a = ap.parse_args()
    sys.exit(a.fn(a))
