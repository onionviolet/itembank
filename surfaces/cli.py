"""The command line: the four commands that need no surface, and the parser.

`main` is the only place that knows every command exists. Each surface exports a
`cmd_*` and stays unaware of argparse, so a new front end is a new module rather
than an edit here and there.
"""
import argparse, collections, json, os, re, sys

import selection
from model import (BANK_FILE_HINTS, SPEC, STYLE_CHECK_CATALOGUE, coverage_map,
                   lint, load, load_style, parse_bank, parse_key_blocks,
                   parse_lesson, parse_sources, parse_terms,
                   warning_ship_state)
from surfaces.anki import cmd_export
from surfaces.daemon import (cmd_cli_twin, cmd_daemon, cmd_disclosure,
                             cmd_sidecar)
from surfaces.day import cmd_day
from surfaces.evidence_cli import (cmd_evidence, cmd_id_assign, cmd_mark, cmd_render,
                                   cmd_retract, cmd_trends)
from surfaces.import_anki import cmd_import_anki
from surfaces.lesson import cmd_gloss, cmd_key_review, cmd_lesson, cmd_render_style
from surfaces.migrate import cmd_migrate
from surfaces.protocol_cli import cmd_schema, cmd_usage
from surfaces.quiz import cmd_build, cmd_serve
from surfaces.selection_cli import cmd_select
from surfaces.session import (cmd_hint, cmd_next, cmd_override, cmd_report,
                              cmd_rubric_review, cmd_start, cmd_submit)
from surfaces.settings import cmd_config
from surfaces import seeding
from surfaces.study import cmd_study
from surfaces.theme import cmd_theme
from surfaces.update import cmd_update


# The Phase 3.1 grammar contract, appended verbatim by `itembank spec` after
# model.SPEC (plan 03.1-06 Task 3). The existing directive list in model.SPEC
# is byte-unchanged; these sections are the additive 03.1 constructs an
# authoring agent must be able to write with no source access. Every claim
# below states what the parser/linter actually does (D-18, D-24, D-06, D-22).
SPEC_03_1 = r"""PHASE 3.1 GRAMMAR (additive)
==============================

Everything in this section is additive: a bank that uses none of these
constructs parses exactly as it did before they existed. Each construct is
independent of the others.

THE GLOSSARY (## TERMS and [[term]])
  A bank may carry one optional `## TERMS` section in its preamble, above
  the first question (same boundary rule as ## LESSON). Each glossary entry
  is one pipe row:
     Airway | The passage from the mouth to the lungs | Air passage
  The first cell is the term, the second its definition, and any later
  cells are aliases. A trailing `key=value` cell is meta data: `zh=` is the
  one reserved meta key (it is read additively by a later bilingual reader)
  and is dropped from rendered output entirely; an unknown meta key is
  ignored, never an error.

  Inside lesson prose, `[[term]]` marks one use of a term. The marked text
  must have a matching ## TERMS entry: a reference with no entry is a lint
  error (`terms.unknown_ref`) naming the reference. A ## TERMS block with
  zero entries is a lint warning and renders nothing. Two terms (or a term
  and an alias) whose slugified forms collide are a lint error
  (`terms.duplicate_slug`).

THE MUST-MEMORIZE CARD ([!KEY])
  `> [!KEY: <title>]` opens an index card inside lesson prose. It must have
  an Anki front: the marker title, or a `{{cloze}}` marker in its body.
  `itembank id-assign` mints the block's machine identity -- `[ID:]` and
  `[HASH:]` lines in the same namespace item ids use, never a separate one
  -- and `itembank export --format keys` ships every card as Anki TSV with
  a `#guid` that round-trips on re-export. A [!KEY] marker inside an item
  rationale is a lint error (`key.in_rationale`); a block with neither a
  title nor a cloze has no Anki front (`key.no_front`); two blocks sharing
  an [ID:] are a lint error (`key.duplicate_id`).

CALL OUT KINDS
  `> [!EXAMPLE]` renders as an Example callout -- a callout kind against
  the one callout container, not a new block (D-18).
  `> [!CHECK: <id>]` is an anchor with no key and no scoring path: it
  renders as the reserved gate slot and is consumed by the Phase 6.2 loop.
  It may reference an item in its own bank only; a cross-bank reference is
  a lint error naming the rule (D-06).

THE EDUCATIONAL OBJECTIVE LINE
  `Objective: <one sentence>` on its own line inside an item adds that
  item's educational objective. It is private payload: consumed by
  selection, dedup, Anki export and the auditor, and never rendered to the
  learner as teaching text. A multi-sentence objective is a lint warning
  (`item.objective_line_multi_sentence`).

STYLE FILES (styles/<id>.md)
  A lesson's written voice is one file per style id. A style file carries
  `## Voice` (the prose zone), `## Rules` (a pipe table
  `id | kind | params | severity | lock | prompt` that may enable, disable,
  re-severity downward, or parameterize a closed-catalogue check -- it may
  never define a check), and `## Exemplar` (the single exemplar an
  authoring model receives; it never receives the Voice zone). The house
  `lock` column encodes the five non-negotiables and is owned by code, not
  by the file: the styles document, the code decides. `[STYLE-PARENT: house]`
  is the only legal parent (one inheritance level). Selection precedence is
  lesson -> bank -> subject profile -> house.
"""


def cmd_spec(a):
    print(SPEC)
    print()
    print(SPEC_03_1)
    return 0


def cmd_lint(a):
    qs = load(a.bank)
    # cmd_lint is the one call site that both loads a bank by path and is the
    # acceptance gate for ROADMAP SC3, so it is the one that supplies the
    # lesson: a LESSON-REF naming a missing heading is an error by item
    # number, never a render-time crash. `--force` is not offered here --
    # the whole point of lint is that it fails loudly.
    errors, warnings = lint(qs, lesson=parse_lesson(a.bank),
                            terms=parse_terms(a.bank),
                            keys=parse_key_blocks(a.bank))
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


def cmd_coverage(a):
    """The on-demand objective coverage map (D-12, plan 03.2-02): objective ->
    item tags, computed from the bank and its ## SOURCES registry at request
    time and never stored."""
    m = coverage_map(a.bank)
    if not m:
        print("no objectives")
        return 0
    print("%d objectives" % len(m))
    for o, tags in m.items():
        print("  %s  %s" % (o, ", ".join(tags)))
    return 0


def cmd_seed(a):
    """`itembank seed <bank>` -- the CLI half of the one accept loop (D-07).

    Runs the six-stage pipeline (D-08) and then presents the drafts one at a
    time, reading `accept` / `skip` / `cancel` from stdin. Accept goes through
    `seeding.accept_candidate` -- the same endpoint the daemon's
    `POST /seed/accept` route calls, never a second implementation of the
    decision. With no model backend reachable it refuses by name (D-10) and
    starts no draft; import, lint, and coverage are unaffected.
    """
    run = seeding.run_seeding_run(a.bank)
    if run.refused:
        print(run.refusal)
        return 1
    decisions = (line.strip().lower() for line in sys.stdin)
    for i, draft in enumerate(run.drafts, 1):
        print(seeding.BATCH_FRAMING_LINE)
        print(seeding.PROGRESS_LINE.format(n=i, m=len(run.drafts),
                                           stage=seeding.STAGE_ACCEPT))
        print(draft["block"])
        for err in draft.get("lint_errors") or []:
            print("error  " + err)
        decision = next(decisions, "cancel")
        if decision == "accept":
            result = seeding.accept_candidate(run.bank_path,
                                              draft["candidate"])
            if result.get("accepted"):
                run.accepted.append(i - 1)
                print("accepted item %d" % i)
            else:
                print("accept refused: %s" % result.get("reason", ""))
        elif decision == "skip":
            run.skip(i - 1)
            print("skipped item %d (deferred)" % i)
        else:
            run.cancel()
            print(seeding.CANCELLED_SUMMARY)
            break
    print(run.summary())
    return 0


# D-17 corpus-residency markers (plan 03.2-05): the real EMT / Math 1400 /
# CSCI 1100 corpus lives beside the private bank, outside this repository,
# and these are its known shapes. `cmd_guard` refuses any of them anywhere
# under the walked tree (fixtures/, repo-owned playbook trees, and `_tmp*`
# scratch dirs excepted), so real corpus content that never parses as a
# question bank -- lesson prose, provenance registries -- still fails CI
# (D-17, T-032-15). The section markers are content shapes; the dir markers
# are the private bank's known directory names.
CORPUS_DIR_MARKERS = ("bank", "banks", "corpus", "corpora",
                      "private-bank", "private_bank")
CORPUS_SECTION_MARKERS = (r"(?m)^##\s+SOURCES\s*$",
                          r"(?m)^##\s+LESSON\s*$")


def _under_corpus_dir(path):
    """True when `path` sits under a private-bank/corpus-named directory
    (D-17): real corpus content is frequently organized under a bank/corpus
    root directory, whatever the file's own shape."""
    parts = path.replace(os.sep, "/").split("/")
    return any(p.lower() in CORPUS_DIR_MARKERS for p in parts)


def _corpus_marker(path):
    """The first corpus-residency section marker `path` carries, or None
    (D-17). `## SOURCES` is the provenance registry every real corpus item
    resolves through (D-11); `## LESSON` is lesson prose. A real corpus file
    that does not parse as a question bank still carries one of these."""
    try:
        text = open(path, encoding="utf-8").read()
    except Exception:
        return None
    for marker in CORPUS_SECTION_MARKERS:
        if re.search(marker, text):
            return marker
    return None


def cmd_guard(a):
    """Fail if any markdown outside fixtures/ is a question bank or is
    real-corpus-shaped content.

    The mechanical half of the content rule. Discipline does not survive a
    late-night commit; a CI check does. Two refusal classes, both part of the
    D-17 gate (plan 03.2-05): a file that parses as a question bank or carries
    a bank filename hint (the pre-existing gate), and a file carrying a
    corpus-residency marker -- a `## SOURCES` provenance registry or a
    `## LESSON` lesson-prose section, or a file under a private-bank/corpus
    directory -- so real content that never parses as a bank still fails CI.
    """
    offenders = []
    for root, dirs, files in os.walk(a.dir):
        # `.agents`/`.claude`/`.reasonix`/`.cursor`/`.github` skill and
        # workflow trees are repo-owned playbooks whose illustrative `Qn.`
        # snippets are teaching content, not real banks; `.planning` is the
        # repo's own planning/format documentation, which legitimately
        # quotes the `## SOURCES` / `## LESSON` grammar it documents. These
        # trees are authored repo content, not committed corpus data --
        # everything else outside fixtures/ is fair game. `_tmp*` dirs are
        # uncommitted scratch debris (e.g. `_tmp_lesson_trial/`), the same
        # transient class `.gitignore` already keeps out of CI.
        dirs[:] = [d for d in dirs
                   if d not in (".git", "fixtures", ".github", ".agents",
                                ".claude", ".cursor", ".reasonix",
                                ".planning")
                   and not d.startswith("_tmp")]
        for f in files:
            if not f.lower().endswith(".md"):
                continue
            p = os.path.join(root, f)
            try:
                n = len(parse_bank(open(p, encoding="utf-8").read()))
            except Exception:
                continue
            if n > 0 or any(h in f.lower() for h in BANK_FILE_HINTS):
                offenders.append((p, "parses as a question bank (%d items)"
                                 % n))
            elif _under_corpus_dir(p):
                offenders.append((p, "sits under a private-bank/corpus "
                                 "directory"))
            else:
                marker = _corpus_marker(p)
                if marker is not None:
                    offenders.append((p, "carries the corpus marker %s"
                                     % marker))
    for p, why in offenders:
        print("error  %s %s. Banks and corpus content belong in your "
              "private vault, never in this repo." % (p, why))
    print("\n%d offending files" % len(offenders))
    return 1 if offenders else 0


# ---------------------------------------------------------------------------
# Warning calibration (D-18, plan 03.2-05): the Phase 3.1 content checks
# measured against a corpus directory. The real EMT / Math / CS corpus lives
# outside this repository (D-17); the command takes the corpus directory as
# its argument and reads it read-only. The real-corpus run is a human action
# beside the private bank -- never CI.
# ---------------------------------------------------------------------------

# The calibrated set: every code the closed style content catalogue can emit,
# plus style.unsourced_specific (plan 03.2-04), the structural provenance
# check. Every one of these gets a recorded false-positive rate.
CALIBRATED_WARNING_CODES = tuple(sorted(STYLE_CHECK_CATALOGUE)) + (
    "style.unsourced_specific",)

# A corpus document declares the warnings it is *expected* to trip with an
# HTML comment; a document without the marker is a negative example. Firing
# on a negative document is a false positive; firing on a positive one is a
# true positive.
_CORPUS_EXPECT_RE = re.compile(
    r"<!--\s*CORPUS-EXPECT:\s*([^>]*?)\s*-->")


def _calibration_threshold(base):
    """The ship-state threshold from the `style.warn_fp_threshold` setting
    (default 0.20, surfaces/settings.py plan 03.1-05 Task 3); falls back to
    the shipped default when no settings file resolves. The rate-to-ship
    rule mirrors `model.warning_ship_state` (above 0.20 ships disabled by
    default)."""
    default = 0.20
    try:
        from surfaces.settings import load_settings, style_defaults
        return (load_settings(base).get("style") or {}).get(
            "warn_fp_threshold", style_defaults()["warn_fp_threshold"])
    except Exception:
        return default


def _corpus_documents(corpus_dir):
    """Every markdown document under `corpus_dir`, deterministically ordered."""
    out = []
    for root, dirs, files in os.walk(corpus_dir):
        dirs.sort()
        for f in sorted(files):
            if f.lower().endswith(".md"):
                out.append(os.path.join(root, f))
    return out


def _expected_codes(path):
    """The style codes a corpus document declares it is expected to trip."""
    try:
        text = open(path, encoding="utf-8").read()
    except OSError:
        return frozenset()
    m = _CORPUS_EXPECT_RE.search(text)
    if m is None:
        return frozenset()
    return frozenset(tok.strip() for tok in m.group(1).split(",")
                     if tok.strip())


def calibrate_corpus(corpus_dir, threshold=None):
    """Measure every calibrated style warning over `corpus_dir`.

    Each document is parsed as a bank (items + lesson + provenance) and run
    through `model.lint` with the shipped house style -- the floor every
    lesson sits on. For every calibrated code the run counts, over documents:
      true positives  -- fired on a document declaring the code expected
      false positives -- fired on a document not declaring it
      missed          -- declared but never fired
    The false-positive rate is FP / (TP + FP), 0.00 when the warning never
    fires, so a code ships enabled only with a recorded rate (D-18).

    Returns (rates, records) where `rates` is {code: fp_rate} and `records`
    is the per-code list of dicts ready for the markdown report. Populates
    `model.STYLE_WARNING_FP_RATES` with the measured rates, the calibration
    seam plan 03.1-05 opened."""
    if threshold is None:
        threshold = _calibration_threshold(corpus_dir)
    house = load_style("house", corpus_dir)
    tp = collections.Counter()     # fired on a positive document
    fp = collections.Counter()     # fired on a negative document
    fired = collections.Counter()  # documents where the code fired
    missed = collections.Counter()  # declared but never fired
    for path in _corpus_documents(corpus_dir):
        try:
            qs = parse_bank(open(path, encoding="utf-8").read())
            lesson = parse_lesson(path)
            sources = parse_sources(path)
        except OSError:
            continue
        errors, warnings = lint(qs, lesson=lesson, style=house,
                                sources=sources)
        codes = {e.code for e in errors} | {w.code for w in warnings}
        codes &= set(CALIBRATED_WARNING_CODES)
        expected = _expected_codes(path)
        for code in codes:
            fired[code] += 1
            (tp if code in expected else fp)[code] += 1
        for code in expected:
            if code not in codes:
                missed[code] += 1
    rates = {}
    records = []
    for code in CALIBRATED_WARNING_CODES:
        denom = tp[code] + fp[code]
        rate = (fp[code] / denom) if denom else 0.0
        rates[code] = rate
        records.append({
            "code": code,
            "fired": fired[code],
            "true_positives": tp[code],
            "false_positives": fp[code],
            "missed": missed[code],
            "fp_rate": rate,
            "ship_state": "disabled" if rate > threshold else "enabled",
            "threshold": threshold,
        })
    from model import STYLE_WARNING_FP_RATES
    STYLE_WARNING_FP_RATES.update(rates)
    return rates, records


def _render_calibration_md(corpus_dir, threshold, records):
    """The 03.2-CALIBRATION.md deliverable (D-18): one row per calibrated
    code with the measured rate and the ship-state decision."""
    import datetime
    lines = [
        "# Phase 3.2 Style Warning Calibration",
        "",
        "**Measured:** %s UTC" % datetime.datetime.utcnow().strftime(
            "%Y-%m-%d %H:%M"),
        "**Corpus:** %s" % corpus_dir,
        "**Threshold:** `style.warn_fp_threshold` = %g (rates above it ship "
        "the warning disabled by default, D-18)." % threshold,
        "",
        "| code | fired | TP | FP | missed | FP rate | ship-state |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in records:
        state = "disabled by default" if r["ship_state"] == "disabled" \
            else "enabled"
        lines.append("| %s | %d | %d | %d | %d | %.2f | %s |"
                     % (r["code"], r["fired"], r["true_positives"],
                        r["false_positives"], r["missed"], r["fp_rate"],
                        state))
    lines += [
        "",
        "The real EMT / Math 1400 / CSCI 1100 corpus lives beside the "
        "private bank, outside this repository (D-17). The rates above were "
        "measured on a synthetic corpus; the real-corpus run is the "
        "human/private-bank action and records the true rates here.",
        "",
    ]
    return "\n".join(lines)


def cmd_calibrate(a):
    """Run every Phase 3.1 style warning over a corpus directory and record
    each warning's false-positive rate with its ship-state decision (D-18).

    Reads the corpus directory read-only (it lives outside the repo, D-17);
    writes the recorded rates to `--out` (default 03.2-CALIBRATION.md in the
    current directory) and prints the table to stdout. The real-corpus run is
    a human/private-bank action, never CI.
    """
    _rates, records = calibrate_corpus(a.dir, threshold=a.threshold)
    md = _render_calibration_md(a.dir, records[0]["threshold"] if records
                                else _calibration_threshold(a.dir), records)
    out = a.out or "03.2-CALIBRATION.md"
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md)
    print("recorded %d calibrated warnings in %s" % (len(records), out))
    return 0


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

    s = sub.add_parser("sidecar", help="packaged-app launch (D-03/D-04): the "
                       "daemon in sidecar mode, printing the fixed stdout "
                       "handshake (itembank-port/token/version) after binding "
                       "and gating every route except the marker with a "
                       "per-launch token")
    s.add_argument("dir", nargs="?", default=".")
    s.add_argument("--port", type=int, default=None,
                   help="default: itembank.json's daemon.port, or 8730 if unset")
    s.add_argument("--no-open", action="store_true", dest="no_open",
                   help="do not launch a browser")
    s.set_defaults(fn=cmd_sidecar)

    s = sub.add_parser("cli-twin", help="print the CLI command that reaches "
                       "the same runtime call as a served view path")
    s.add_argument("path")
    s.set_defaults(fn=cmd_cli_twin)

    s = sub.add_parser("disclosure", help="print the one-disclosure render-"
                       "hook state (notified_at, locked copy, settings path)")
    s.add_argument("dir", nargs="?", default=".")
    s.set_defaults(fn=cmd_disclosure)

    s = sub.add_parser("stats", help="item mix, coverage, answer-position skew")
    s.add_argument("bank")
    s.set_defaults(fn=cmd_stats)

    s = sub.add_parser("coverage", help="objective coverage map, computed on "
                       "demand from the bank and its ## SOURCES registry, "
                       "never stored")
    s.add_argument("bank")
    s.set_defaults(fn=cmd_coverage)

    s = sub.add_parser("start", help="start a resumable JSON assessment session")
    s.add_argument("bank")
    s.add_argument("--count", type=int, default=None)
    s.add_argument("--objective", default=None,
                   help="limit the session to one objective")
    s.add_argument("--prerequisite", default=None,
                   help="select items that name this prerequisite objective")
    s.add_argument("--prereq-satisfied", action="store_true", default=None,
                   help="only items whose prerequisites have a recorded pass")
    s.add_argument("--type", default=None,
                   help="item type (mc, multi, table, dnd, build, short)")
    s.add_argument("--difficulty", default=None,
                   help="difficulty annotation (recall, application, analysis)")
    s.add_argument("--mode", default="diagnostic",
                   choices=("diagnostic", "practice", "exam", "remediation", "drill"))
    s.add_argument("--selection-mode", default="practice",
                   choices=selection.SELECTION_MODES,
                   help="how the session is composed (diagnostic, practice, "
                        "remediation, exam) -- not the feedback policy that "
                        "--mode sets")
    s.add_argument("--seed", type=int, default=None,
                   help="deterministic item-selection seed")
    s.add_argument("--exclude", action="append", default=None, metavar="ID",
                   help="exclude one opaque [ID:] value; repeatable")
    s.add_argument("--pair", default=None,
                   help="serve the whole named confusion set together")
    s.add_argument("--profile", default=None,
                   help="named selection profile from settings")
    s.add_argument("--out", help="session JSON path")
    s.add_argument("--force", action="store_true", help="start despite lint errors")
    s.add_argument("--subject", default=None,
                   help="subject namespace whose per-day cap gates this "
                        "sitting (default: derived from --objective's "
                        "namespace)")
    s.add_argument("--override-cap", default="", metavar="CONFIRM",
                   help="start one additional sitting after the cap is "
                        "reached; CONFIRM must be exactly the override "
                        "confirmation phrase (see `itembank override --help`)")
    s.set_defaults(fn=cmd_start)

    s = sub.add_parser("override", help="start one additional sitting past "
                                        "today's cap after explicit confirmation")
    s.add_argument("bank")
    s.add_argument("--subject", default=None,
                   help="subject namespace at cap; the override is bound to "
                        "exactly this subject for one sitting")
    s.add_argument("--confirm", default="", metavar="CONFIRM",
                   help="exact confirmation phrase required (start uses "
                        "--override-cap with the same value)")
    s.add_argument("--count", type=int, default=None)
    s.add_argument("--objective", default=None)
    s.add_argument("--prerequisite", default=None)
    s.add_argument("--prereq-satisfied", action="store_true", default=None)
    s.add_argument("--type", default=None)
    s.add_argument("--difficulty", default=None)
    s.add_argument("--mode", default="diagnostic",
                   choices=("diagnostic", "practice", "exam", "remediation", "drill"))
    s.add_argument("--selection-mode", default="practice",
                   choices=selection.SELECTION_MODES)
    s.add_argument("--seed", type=int, default=None)
    s.add_argument("--pair", default=None)
    s.add_argument("--profile", default=None)
    s.add_argument("--out", help="session JSON path")
    s.add_argument("--force", action="store_true", help="start despite lint errors")
    s.set_defaults(fn=cmd_override)

    s = sub.add_parser("select", help="preview a selection without starting a session")
    s.add_argument("bank")
    s.add_argument("--objective", default=None)
    s.add_argument("--prerequisite", default=None)
    s.add_argument("--prereq-satisfied", action="store_true", default=None)
    s.add_argument("--type", default=None)
    s.add_argument("--difficulty", default=None)
    s.add_argument("--selection-mode", default=None,
                   choices=selection.SELECTION_MODES)
    s.add_argument("--count", type=int, default=None)
    s.add_argument("--seed", type=int, default=None)
    s.add_argument("--exclude", action="append", default=None, metavar="ID")
    s.add_argument("--pair", default=None)
    s.add_argument("--profile", default=None)
    s.add_argument("--explain", action="store_true",
                   help="print the trace as plain English instead of JSON")
    s.add_argument("--force", action="store_true",
                   help="select despite lint errors")
    s.set_defaults(fn=cmd_select)

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

    s = sub.add_parser("hint", help="request one error-specific hint from the "
                                    "model backend; falls back to the authored "
                                    "tier offline and never accepts a caller-"
                                    "supplied tier (D-09)")
    s.add_argument("--session", required=True, help="the session JSON path")
    s.add_argument("--retry", action="store_true",
                   help="explicitly regenerate as a parent-linked retry; at "
                        "most one generation per interaction id otherwise (D-12)")
    s.set_defaults(fn=cmd_hint)

    s = sub.add_parser("rubric-review", help="request pending per-point rubric "
                        "suggestions for the current short response; a model "
                        "suggestion can never settle a mark (D-25)")
    s.add_argument("--session", required=True, help="the session JSON path")
    s.set_defaults(fn=cmd_rubric_review)

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
    s.add_argument("--bank", default="",
                   help="filter by the recorded bank filename (the basename "
                        "response_event() records, not a path); composes with "
                        "--objective and --subject rather than replacing them")
    s.add_argument("--since", default="",
                   help="only events at or after this date, YYYY-MM-DD")
    s.add_argument("--rebuild-index", action="store_true", dest="rebuild_index",
                   help="delete and rebuild the disposable query index before "
                        "querying; the index is a cache, so this loses nothing")
    s.add_argument("--base", default=".",
                   help="directory holding _evidence/ (default: current directory)")
    s.set_defaults(fn=cmd_evidence)

    s = sub.add_parser("trends", help="longitudinal retention report: due "
                       "objectives, week series, weights, and evidence claim "
                       "from one captured snapshot (Phase 10)")
    s.add_argument("--weeks", type=int, default=4, choices=(1, 2, 4, 8, 12),
                   help="report window in weeks (default: 4)")
    s.add_argument("--subject", default="",
                   help="filter the report to one namespaced subject")
    s.add_argument("--objective", default="",
                   help="filter the report to one objective")
    s.add_argument("--cutoff", default="",
                   help="ISO-8601 UTC cutoff timestamp (default: now)")
    s.add_argument("--zone", default="UTC",
                   help="local-day zone: UTC, local, UTC+HH:MM/UTC-HH:MM, or an "
                        "IANA name (default: UTC)")
    s.add_argument("--json", action="store_true",
                   help="emit the machine-readable report payload instead of "
                        "plain text")
    s.add_argument("--base", default=".",
                   help="directory holding _evidence/ (default: current directory)")
    s.set_defaults(fn=cmd_trends)

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
    s.add_argument("--proposal", help="single-proposal accept form: the event id "
                   "of the mark_proposal to accept; requires --verdict (plan 08-04)")
    s.add_argument("--rubric", help="JSON array of {point, pass} booleans for the "
                   "single-form marks (--item/--proposal)")
    s.add_argument("--verdict", choices=("pass", "fail"), default=None,
                   help="required with --item or --proposal")
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

    s = sub.add_parser("lesson", help="render the LESSON section as reading material")
    s.add_argument("bank")
    s.add_argument("--out")
    s.add_argument("--ref", default="",
                   help="render only the section whose heading matches this text")
    s.add_argument("--complete", action="store_true",
                   help="record an explicit completion of the --ref heading: the "
                        "referenced objectives enter the derived review queue "
                        "(valid only with --ref)")
    s.add_argument("--zone", default="UTC",
                   help="local-day zone for a --complete event: an IANA name, "
                        "'UTC', or a fixed offset such as 'UTC+09:00' "
                        "(default: UTC)")
    s.set_defaults(fn=cmd_lesson)

    s = sub.add_parser("render-style", help="render the lesson permuted "
                       "into a named style (the five impossible transforms "
                       "are refused by name)")
    s.add_argument("bank")
    s.add_argument("--style", required=True,
                   help="the target style id to render the lesson in")
    s.add_argument("--out",
                   help="output path (default: <bank>_<style>.html)")
    s.set_defaults(fn=cmd_render_style)

    s = sub.add_parser("gloss", help="print one term's definition from the "
                       "bank's ## TERMS block, gated by the runtime")
    s.add_argument("bank")
    s.add_argument("term", help="the term to look up, matched by lesson_slug")
    s.set_defaults(fn=cmd_gloss)

    s = sub.add_parser("key-review", help="record a [!KEY] card as added to "
                       "review (the CLI twin of POST /key/<id>/review)")
    s.add_argument("bank")
    s.add_argument("key_id", help="the [!KEY] block's minted [ID:] value")
    s.set_defaults(fn=cmd_key_review)

    s = sub.add_parser("export", help="export a bank as Anki TSV or GIFT for LMS import")
    s.add_argument("bank")
    s.add_argument("out", nargs="?",
                   help="output path (required for basic/cloze/gift; keys "
                        "defaults to <bank>_keys.tsv)")
    s.add_argument("--format", choices=("basic", "cloze", "gift", "keys"),
                   default="basic")
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
    s.add_argument("--edit", action="store_true",
                   help="structured row/cell edit mode: print the dated-row "
                        "snapshot, or save with --set plus --revision")
    s.add_argument("--set", action="append", default=[], metavar="COLUMN=TEXT",
                   help="repeatable cell edit COLUMN=TEXT; requires --edit "
                        "and the snapshot's --revision")
    s.add_argument("--revision", default="",
                   help="the SHA-256 revision the edit is based on (printed "
                        "by the snapshot)")
    s.add_argument("--force", action="store_true",
                   help="second-confirmation save after a conflict; requires "
                        "--confirm-force OVERWRITE and the conflict's --revision")
    s.add_argument("--confirm-force", default="", metavar="WORD",
                   help="exact confirmation text required with --force")
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

    s = sub.add_parser("usage", help="print the machine-readable agent usage "
                        "contract -- permissions, prohibitions, disclosure, "
                        "retry, manual-grading rules, and forbidden "
                        "inferences -- the bytes on disk verbatim (MODEL-04)")
    s.set_defaults(fn=cmd_usage)

    s = sub.add_parser("config", help="print the settings schema the way `spec` prints "
                       "the format contract")
    s.add_argument("action", nargs="?", choices=("schema", "set"))
    s.add_argument("key", nargs="?")
    s.add_argument("value", nargs="?")
    s.add_argument("--base", default=".",
                   help="directory holding itembank.json (default: current directory)")
    s.set_defaults(fn=cmd_config)

    s = sub.add_parser("theme", help="preview, set, reset, or pick the source accent")
    t = s.add_subparsers(dest="action", required=True)
    tp = t.add_parser("preview", help="show the derived light/dark accent tokens "
                      "and contrast ratios for COLOR")
    tp.add_argument("color")
    tp.add_argument("--base", default=".",
                    help="directory holding itembank.json (default: current directory)")
    tp.set_defaults(fn=cmd_theme)

    ts = t.add_parser("set", help="persist COLOR as the source accent")
    ts.add_argument("color")
    ts.add_argument("--base", default=".",
                    help="directory holding itembank.json (default: current directory)")
    ts.set_defaults(fn=cmd_theme)

    tr = t.add_parser("reset", help="restore the default source accent after confirmation")
    tr.add_argument("--base", default=".",
                    help="directory holding itembank.json (default: current directory)")
    tr.add_argument("--confirm-reset", default="", metavar="RESET",
                    help="exact confirmation text RESET required to restore #0e6e62")
    tr.set_defaults(fn=cmd_theme)

    tk = t.add_parser("pick", help="open the native OS color picker "
                      "(preview-only until an explicit theme set)")
    tk.add_argument("--base", default=".",
                    help="directory holding itembank.json (default: current directory)")
    tk.add_argument("--initial", default="",
                    help="seed the picker with this source color (default: saved accent)")
    tk.add_argument("--json", action="store_true",
                    help="emit the structured picker contract instead of human lines")
    tk.set_defaults(fn=cmd_theme)

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

    s = sub.add_parser("update", help="check GitHub for a newer release, download and "
                       "verify it, and prepare it beside the running artifact")
    s.add_argument("--check", action="store_true",
                   help="report whether a newer version exists without downloading it")
    s.add_argument("--repo", default=None,
                   help="owner/name of the GitHub repository to check "
                        "(default: itembank.json's update.repo)")
    s.add_argument("--timeout", type=int, default=30,
                   help="network timeout in seconds (default: 30)")
    s.set_defaults(fn=cmd_update)

    s = sub.add_parser("import", help="import external content into itembank candidates")
    imp = s.add_subparsers(dest="import_format", required=True)
    apk = imp.add_parser("anki", help="import an Anki .apkg deck")
    apk.add_argument("file", help="path to the .apkg file")
    apk.add_argument("--out",
                     help="directory for the per-note report and staged candidates "
                          "(default: current directory)")
    apk.add_argument("--force", action="store_true",
                     help="exit 0 even when no note converted; the model.lint() gate "
                          "is never bypassed")
    apk.set_defaults(fn=cmd_import_anki)

    s = sub.add_parser("seed", help="seed one bank through the six-stage "
                                    "accept loop one item at a time (needs a "
                                    "model backend; refuses by name without one)")
    s.add_argument("bank")
    s.set_defaults(fn=cmd_seed)

    s = sub.add_parser("guard", help="fail if a real bank was committed")
    s.add_argument("dir", nargs="?", default=".")
    s.set_defaults(fn=cmd_guard)

    s = sub.add_parser("calibrate", help="measure every Phase 3.1 style "
                                        "warning's false-positive rate over "
                                        "a corpus directory (D-18)")
    s.add_argument("dir", help="the corpus directory (lives outside the repo, D-17)")
    s.add_argument("--out", help="markdown report path (default: 03.2-CALIBRATION.md)")
    s.add_argument("--threshold", type=float, default=None,
                   help="FP-rate threshold for disabled-by-default (default: "
                        "style.warn_fp_threshold = 0.20)")
    s.set_defaults(fn=cmd_calibrate)

    a = ap.parse_args()
    sys.exit(a.fn(a))
