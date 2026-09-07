"""The command line: the four commands that need no surface, and the parser.

`main` is the only place that knows every command exists. Each surface exports a
`cmd_*` and stays unaware of argparse, so a new front end is a new module rather
than an edit here and there.
"""
import argparse, collections, json, os, re, sys

import director
import evidence
import graph
import identity
import journal
import selection
import source_adapters
from model import (BANK_FILE_HINTS, SPEC, STYLE_CHECK_CATALOGUE, coverage_map,
                   lint, load, load_style, parse_bank, parse_key_blocks,
                   parse_activities, parse_lesson, parse_media, parse_sources,
                   parse_terms, warning_ship_state)
from surfaces.anki import cmd_export
from surfaces.audio import cmd_export_audio
from surfaces.audit_cli import cmd_audit
from surfaces import binding_cli
from surfaces import course_ops
from surfaces.daemon import (cmd_cli_twin, cmd_daemon, cmd_disclosure,
                             cmd_sidecar)
from surfaces.day import cmd_day
from surfaces.evidence_cli import (cmd_evidence, cmd_id_assign, cmd_mark, cmd_marks,
                                   cmd_render, cmd_retract, cmd_trends)
from surfaces.ia import (SHELF_ACTIONS, cmd_activity, cmd_help_code,
                         cmd_shelf)
from surfaces.import_anki import cmd_import_anki
from surfaces.lesson import cmd_gloss, cmd_key_review, cmd_lesson, cmd_render_style
from surfaces.lti import (PRIVACY_STATEMENT, cmd_lti_doctor, cmd_lti_serve,
                          cmd_lti_status)
from surfaces.migrate import cmd_migrate
from surfaces.protocol_cli import cmd_schema, cmd_usage
from surfaces.quiz import (cmd_build, cmd_lesson_check, cmd_lesson_skip,
                          cmd_serve)
from surfaces.selection_cli import cmd_select
from surfaces.session import (cmd_hint, cmd_interact, cmd_next, cmd_override,
                              cmd_report, cmd_rubric_review, cmd_start,
                              cmd_submit, cmd_teach)
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

THE GATE DIRECTIVE ([GATE:])
  One optional `[GATE: required|recommended|off]` in the lesson preamble
  sets how the lesson's inline checks gate reading. `required` truncates
  the lesson at the first uncleared check (the server does not emit the
  sections below it); `recommended` (the default when the directive is
  absent) renders the whole lesson with each check in the flow; `off`
  renders the Phase 3.1 reader unchanged. A learner can always read ahead
  by the recorded `Read ahead without answering` control; in diagnostic
  and exam sittings a `required` gate degrades to `recommended`. A value
  outside the three is a lint error (`lesson.invalid_gate`); a
  `[!CHECK: <id>]` naming no item in its own bank is a lint error
  (`lesson.check_ref_unknown`).

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


def _source_options(a, base):
    """The `source` settings group, with any per-invocation override applied
    over it. Settings are read here, in the surface, rather than inside
    `source_adapters`: the adapter is a model-tier module and reaching up
    into `surfaces.settings` for a policy would invert the layering."""
    from surfaces.settings import load_settings
    options = dict((load_settings(base) or {}).get("source") or {})
    if getattr(a, "snapshot_storage", None):
        options["snapshot_storage"] = a.snapshot_storage
    return options


def _cmd_source_capture(a, base):
    """`itembank source import --url` -- capture a remote page as a source.

    D-04: what is bound is the capture, not the URL. The fingerprint is
    taken over the derived Markdown, the URL and the capture timestamp are
    recorded as provenance, and the captured page reads back from disk with
    the network unplugged.
    """
    result = source_adapters.capture_url(
        base, a.url, "human", "cli", options=_source_options(a, base),
        confirm=getattr(a, "confirm", False))
    if result["status"] != "ok":
        if a.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("%s: %s" % (result["error"]["code"],
                              result["error"]["message"]))
        sys.exit(1)
    if a.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    print("%s -> %s" % (a.url, result["md_rel_path"]))
    print("   sidecar: %s" % result["sidecar_rel_path"])
    print("   source id: %s" % result["source_id"])
    print("   note: the capture is minted with all seven rights unknown; "
          "record a grant before deriving anything from it")


def cmd_source_recheck(a):
    """`itembank source recheck` -- report whether a captured remote origin
    still matches. It writes nothing and journals nothing, and it exits 0 for
    all three states, `origin_unreachable` included, because an unreachable
    network is a reported state and not a command failure. That is the
    degrade-never-block rule applied to this command.
    """
    base = os.path.abspath(a.base)
    result = source_adapters.recheck_origin(
        base, a.object_id, options=_source_options(a, base))
    if a.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get("state") else 1
    if not result.get("state"):
        print("%s: %s" % (result["error"]["code"],
                          result["error"]["message"]))
        return 1
    print(result["state"])
    print("   origin: %s" % (result["origin"].get("value") or "(none)"))
    print("   %s" % result["note"])
    return 0


def cmd_source(a):
    """`itembank source import` -- the CLI half of the one source-import
    boundary (plan 14C-01). It reaches exactly the same
    `source_adapters.import_source` the daemon route reaches; neither surface
    is the real one and neither extracts anything itself.

    A raw file is linked before it is imported, because linking is what mints
    the raw object's id and records the learner's rights declaration about a
    file they already hold. `--grant` applies only to that first link: a
    later run never overwrites a recorded grant, so widening a right is its
    own decision rather than a side effect of importing again.
    """
    base = os.path.abspath(a.base)
    if getattr(a, "url", None):
        return _cmd_source_capture(a, base)
    if not getattr(a, "file", None):
        sys.exit("source import needs one of --file or --url")
    if not a.adapter:
        sys.exit("source import --file needs --adapter")
    rel_path = os.path.relpath(os.path.abspath(
        os.path.join(base, a.file)), base)
    grant = None
    if a.grant:
        names = [n.strip() for n in a.grant.split(",") if n.strip()]
        unknown = [n for n in names if n not in identity.RIGHTS_OPERATIONS]
        if unknown:
            sys.exit("unknown right %r; the seven rights are: %s"
                     % (unknown[0], ", ".join(identity.RIGHTS_OPERATIONS)))
        grant = {op: ("granted" if op in names else "unknown")
                 for op in identity.RIGHTS_OPERATIONS}

    registry = journal.read_registry(base)
    raw_object_id = None
    for object_id, row in registry.items():
        if row.get("path") == rel_path and row.get("kind") == "source":
            raw_object_id = object_id
            break
    if raw_object_id is None:
        try:
            record = journal.op_link(base, "source", rel_path, "human", "cli",
                                     rights=grant)
        except journal.JournalError as exc:
            sys.exit("%s: %s" % (exc.code, exc))
        raw_object_id = record["object_id"]
    elif grant is not None:
        print("note: %s is already linked; its recorded rights stand and "
              "--grant was not applied" % rel_path)

    if a.preview:
        result = source_adapters.preview_source(base, a.adapter, raw_object_id)
    else:
        try:
            result = source_adapters.import_source(
                base, a.adapter, raw_object_id, "human", "cli",
                rights_grant=grant, options=_source_options(a, base),
                confirm=getattr(a, "confirm", False))
        except journal.JournalError as exc:
            sys.exit("%s: %s" % (exc.code, exc))

    if result["status"] != "ok":
        if a.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("%s: %s" % (result["error"]["code"],
                              result["error"]["message"]))
        sys.exit(1)

    if a.json:
        preview = result.pop("preview", None)
        if preview is not None:
            result["preview"] = preview
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    if a.preview:
        sidecar = result["preview"]["sidecar"]
        print("%s: %d locators, %d unsupported, nothing written"
              % (a.adapter, len(sidecar["locators"]),
                 len(sidecar["unsupported"])))
        return
    print("%s -> %s" % (rel_path, result["md_rel_path"]))
    print("   sidecar: %s" % result["sidecar_rel_path"])
    print("   source id: %s" % result["source_id"])



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
                            keys=parse_key_blocks(a.bank),
                            media=parse_media(a.bank),
                            activities=parse_activities(a.bank))
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
    _print_distractor_usage(a, qs)
    return 0


def _print_distractor_usage(a, qs):
    """Empirical distractor analysis: which options no learner has ever
    chosen (research 2026-08-24, "the check we are not doing, and should").

    It needs no model and no external authority, only the evidence store that
    already exists beside the bank, and it is the one item-quality check no
    standards body can give you. Every count below is measured; nothing here
    is a judgement about the option's wording.

    Degrades rather than blocks, the way `day` omits Anki counts when Anki is
    closed: no log beside the bank means no section. Both denominators are
    printed, because an item with two attempts says nothing about its
    distractors and a report that hid that would be worse than no report.
    """
    log = evidence.log_path(os.path.dirname(os.path.abspath(a.bank)) or ".")
    if not os.path.exists(log):
        return
    floor = getattr(a, "min_attempts", 5)
    rows = evidence.distractor_usage(log, qs, bank=os.path.basename(a.bank),
                                     min_attempts=floor)
    assessed = [r for r in rows if r["assessed"]]
    thin = [r for r in rows if not r["assessed"]]
    if not rows:
        return
    print("\ndistractor usage, %d of %d choice items with at least %d recorded "
          "response%s" % (len(assessed), len(rows), floor,
                          "" if floor == 1 else "s"))
    dead = [r for r in assessed if r["unused"]]
    for r in dead:
        print("  %-4s %3d recorded, never chosen: %s%s"
              % (r["item"], r["attempts"], ", ".join(r["unused"]),
                 "   [%s]" % r["objective"] if r["objective"] else ""))
    if assessed and not dead:
        print("  every distractor on every assessed item has been chosen at "
              "least once")
    if thin:
        print("  not assessed (fewer than %d recorded): %s"
              % (floor, ", ".join("%s [%d]" % (r["item"], r["attempts"])
                                  for r in thin)))


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

# Plan 16C-02: a learner note document is corpus content too. Its markdown
# half carries no `##` section marker at all, so the two patterns above miss
# it entirely; what it always carries is the sidecar key `note_document_id`,
# in the JSON sidecar and in any markdown that inlines the record. This is
# one additive branch in the marker helper below, deliberately not a second
# walker: two guards drift, and the one that drifts is always the newer one.
NOTE_DOCUMENT_MARKER = r"(?m)^\s*\"?note_document_id\"?\s*:"


def _under_corpus_dir(path):
    """True when `path` sits under a private-bank/corpus-named directory
    (D-17): real corpus content is frequently organized under a bank/corpus
    root directory, whatever the file's own shape."""
    parts = path.replace(os.sep, "/").split("/")
    return any(p.lower() in CORPUS_DIR_MARKERS for p in parts)


def _corpus_marker(path):
    """The first corpus-residency section marker `path` carries, or None
    (D-17). `## SOURCES` is the provenance registry every real corpus item
    resolves through (D-11); `## LESSON` is lesson prose; `note_document_id`
    is the learner note document's own key (16C-02). A real corpus file that
    does not parse as a question bank still carries one of these."""
    try:
        text = open(path, encoding="utf-8").read()
    except Exception:
        return None
    for marker in CORPUS_SECTION_MARKERS:
        if re.search(marker, text):
            return marker
    if re.search(NOTE_DOCUMENT_MARKER, text):
        return "note_document_id"
    return None


def _without_fenced_blocks(text):
    """`text` with every fenced code block's contents removed.

    Docs demonstrate the item grammar inside a fence -- README's "Here is
    the whole format" block is the canonical case -- and the phase-05 grammar
    widening made that illustration parse as a real item, so `guard` started
    refusing the repo's own README. A fence is how markdown says "this is a
    sample, not the document"; the same reason `.agents`, `.claude` and
    `.planning` are already skipped whole. This does not soften the gate: a
    real bank's items are not wrapped in fences, and stripping a LESSON code
    fence out of one still leaves every item behind to be counted.
    """
    out, in_fence = [], False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(line)
    return "\n".join(out)


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
        # transient class `.gitignore` already keeps out of CI. `_sample_course`
        # and `_ia` are plan 16B-09's gitignored runtime state, materialized
        # per install and never committed, so nothing in them can reach a
        # commit, which is the only thing guard exists to prevent.
        # `course_fixture_17b` is the Phase 17B tracer's synthetic fixture
        # course (17B-CONTEXT D-02): invented subject matter kept in this
        # repository on purpose, like `fixtures/` but shaped as a real
        # course root. It is not real corpus content, and D-02 requires it
        # to be guard clean, so it is skipped by name rather than by
        # weakening either refusal class.
        dirs[:] = [d for d in dirs
                   if d not in (".git", "fixtures", ".github", ".agents",
                                ".claude", ".cursor", ".reasonix",
                                ".planning", "_sample_course", "_ia",
                                "course_fixture_17b")
                   and not d.startswith("_tmp")]
        for f in files:
            if not f.lower().endswith(".md"):
                continue
            p = os.path.join(root, f)
            try:
                n = len(parse_bank(
                    _without_fenced_blocks(open(p, encoding="utf-8").read())))
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


def _cmd_export(a):
    """`itembank export audio <bank> --objective <id>` dispatches to the audio
    drill-pack exporter; any other first token is the legacy flat export form,
    which must keep parsing and behaving byte-identically (D-08, AUDIO-05)."""
    if a.bank == "audio":
        return cmd_export_audio(a)
    return cmd_export(a)


def _configured_author_callable(settings_data):
    """The Phase 8 configured adapter as the repository-blind author
    callable (plan 11-05 Task 1): builds the bounded adapter request
    (operation author) carrying only the public contract, the bounded
    authoring request, the attempt number, and versioned structured
    findings, then returns the candidate for the authoring pipeline to
    validate. An unavailable/refusal result becomes a malformed empty
    response so the pipeline retries within its cap and retains a report
    with zero writes -- the model can never change scope, tools, autonomy,
    caps, or writer permission (T-11-25/T-11-26)."""
    def _author(payload):
        import authoring
        import model_adapter
        request = payload.get("request") or {}
        interaction_id = "author-" + authoring.request_fingerprint(
            request)[:16]
        adapter_request = model_adapter.request_from_operation(
            "author", interaction_id, "", author_request=payload)
        result = model_adapter.invoke(adapter_request, settings_data)
        if result.get("status") != "ok":
            return {"schema_version": 1, "items": []}
        candidate = result.get("candidate")
        if isinstance(candidate, dict):
            return candidate
        return {"schema_version": 1, "items": []}
    return _author


def build_parser():
    """The whole CLI as an `argparse.ArgumentParser`, built and not run.

    Split out of `main()` on 2026-09-05 so the command surface can be READ
    as well as executed: the surface-coverage report enumerates every
    command from this parser rather than from a hand-kept list, and the
    command palette offers the same set. A list of commands maintained
    beside the parser would drift from it the first time someone added a
    command; a parser that can be built without being run cannot.
    """
    # Imported lazily and inside this function, not at module scope:
    # itembank.py itself does `from surfaces.cli import main`, and the built
    # .pyz's __main__.py does `from surfaces.cli import main` directly
    # (bypassing itembank.py entirely) -- a module-scope `from itembank
    # import __version__` here would circle back into a partially-initialized
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
    s.add_argument("--seed", type=int, default=0,
                   help="deterministic item-order seed, the same one `start` takes "
                        "(default: 0). Order matters more than it looks: a sitting "
                        "parks on a constructed response until a marker rules on it, "
                        "so a short item served first ends the sitting at item one")
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

    s = sub.add_parser("stats", help="item mix, coverage, answer-position skew, "
                       "and empirical distractor usage when evidence exists")
    s.add_argument("bank")
    s.add_argument("--min-attempts", type=int, default=5,
                   help="how many recorded responses an item needs before its "
                        "distractors are assessed (default: 5). An item below "
                        "the floor is listed with its real count, never hidden")
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
    s.add_argument("--subject-profile", default=None,
                   help="subject-profile id from the validated subject_profiles "
                        "registry (emt, math, cs, or a configured fourth); only "
                        "the id crosses the client boundary, the snapshot is "
                        "resolved server-side")
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

    s = sub.add_parser("teach", help="read or open the next tier of the fixed "
                                     "six-tier AUTHORED hint ladder for the "
                                     "current item; the CLI twin of POST "
                                     "/api/teach, and never a caller-supplied "
                                     "tier (D-09)")
    s.add_argument("session", help="the session JSON path")
    s.add_argument("--next", action="store_true",
                   help="open the next tier the learner has already earned "
                        "with a genuine wrong attempt")
    s.add_argument("--stumped", action="store_true",
                   help="open the next tier without that entitlement -- the "
                        "\"I'm stumped\" path, one tier and no more")
    s.set_defaults(fn=cmd_teach)

    s = sub.add_parser("rubric-review", help="request pending per-point rubric "
                        "suggestions for the current short response; a model "
                        "suggestion can never settle a mark (D-25)")
    s.add_argument("--session", required=True, help="the session JSON path")
    s.set_defaults(fn=cmd_rubric_review)

    s = sub.add_parser("interact", help="commit one semantic state-changing "
                        "action on the current visual item (plan 06.1-02); "
                        "the CLI twin of POST /api/interact")
    s.add_argument("session", help="the session JSON path")
    s.add_argument("--action", required=True, metavar="JSON",
                   help="exactly {\"interaction_version\": 1, \"action_id\": "
                        "\"<uuid4>\", \"action_type\": \"place_point\", "
                        "\"state\": {...}}; the session and item are resolved "
                        "server-side, never from this flag")
    s.set_defaults(fn=cmd_interact)

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
    s.add_argument("--notes", default=None, help="free-text note recorded on the "
                   "single-form mark (--item/--proposal); batch entries carry "
                   "their own notes key")
    s.set_defaults(fn=cmd_mark)

    s = sub.add_parser("marks", help="list short answers awaiting a mark across "
                       "every session under --base; read-only")
    s.add_argument("--base", default=".", help="course root holding _attempts and _evidence")
    s.set_defaults(fn=cmd_marks)

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
    s.add_argument("--subject-profile", default=None,
                   help="subject-profile id whose presentation this lesson "
                        "renders under (emt, math, cs, or a configured "
                        "fourth); only the id crosses the client boundary")
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

    s = sub.add_parser("lesson-check", help="score and record one gate band "
                       "check submission (the CLI twin of POST "
                       "/lesson/<stem>/check)")
    s.add_argument("bank")
    s.add_argument("check", help="the [!CHECK:] id of the item to score")
    s.add_argument("--answer", required=True,
                   help="the learner response as submit --answer JSON")
    s.set_defaults(fn=cmd_lesson_check)

    s = sub.add_parser("lesson-skip", help="record one gate_skip event (the "
                       "CLI twin of POST /lesson/<stem>/skip)")
    s.add_argument("bank")
    s.add_argument("check", help="the [!CHECK:] id being skipped")
    s.set_defaults(fn=cmd_lesson_skip)

    s = sub.add_parser("export", help="export a bank as Anki TSV or GIFT for LMS "
                                      "import, or one objective as an audio drill "
                                      "pack (stem, timed pause, key, why) plus a "
                                      "plain-text transcript")
    s.add_argument("bank")
    s.add_argument("out", nargs="?",
                   help="output path (required for basic/cloze/gift; keys "
                        "defaults to <bank>_keys.tsv; for `export audio` this "
                        "is the bank file)")
    s.add_argument("--format", choices=("basic", "cloze", "gift", "keys"),
                   default="basic")
    s.add_argument("--strict", action="store_true",
                   help="GIFT export only: promote the multi scoring-divergence "
                        "warning to a per-item failure")
    s.add_argument("--force", action="store_true", help="export despite lint errors")
    s.add_argument("--objective", metavar="ID",
                   help="audio export: the objective id to turn into a drill pack")
    s.add_argument("--engine", metavar="NAME",
                   help="audio export: the registered TTS engine "
                        "(edge-tts | piper | transcript-only; default from "
                        "settings audio.engine). edge-tts sends item text to "
                        "Microsoft's endpoint; piper runs locally; "
                        "transcript-only writes no audio")
    s.add_argument("--split", choices=("per-pack", "per-item"),
                   help="audio export: one file per objective (per-pack, the "
                        "default) or one file per item (per-item)")
    s.add_argument("--container", choices=("mp3", "wav"),
                   help="audio export: output container (default mp3)")
    s.add_argument("--out", dest="out_dir", metavar="DIR",
                   help="audio export: output directory for the pack "
                        "(default: the bank's directory)")
    s.set_defaults(fn=_cmd_export)

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

    s = sub.add_parser("activity", help="list durable agent and maintenance "
                       "jobs (the Activity view's CLI twin)")
    s.add_argument("dir", nargs="?", default=".")
    s.set_defaults(fn=cmd_activity)

    s = sub.add_parser("help-code", help="print the offline help entry for one "
                       "named error code")
    s.add_argument("code")
    s.set_defaults(fn=cmd_help_code)

    s = sub.add_parser("shelf", help="apply one course-shelf or first-run "
                       "action (the POST /api/shelf CLI twin)")
    s.add_argument("action", choices=list(SHELF_ACTIONS))
    s.add_argument("dir", nargs="?", default=".")
    s.set_defaults(fn=cmd_shelf)

    s = sub.add_parser("source", help="import a book, document, page, or "
                       "transcript as a cited source")
    t = s.add_subparsers(dest="action", required=True)
    si = t.add_parser("import", help="extract one source file into Markdown "
                      "plus a locator sidecar")
    si.add_argument("--base", default=".",
                    help="approved root holding the file and its journal "
                         "(default: current directory)")
    what = si.add_mutually_exclusive_group(required=True)
    what.add_argument("--file",
                      help="path to the raw file, relative to --base. A path "
                           "is accepted here because the CLI is not a network "
                           "boundary; the daemon route takes an opaque id "
                           "instead")
    what.add_argument("--url",
                      help="a remote page to capture. What is bound is the "
                           "capture, never the URL (D-04): the snapshot is "
                           "fingerprinted and reads back offline")
    si.add_argument("--adapter", default=None,
                    choices=sorted(source_adapters.ADAPTER_REGISTRY),
                    help="which registered adapter extracts this medium. "
                         "Required with --file; ignored with --url, which "
                         "always captures through the web adapter")
    si.add_argument("--grant", default="",
                    help="comma-separated rights to record when this file is "
                         "linked for the first time, from: %s. Omitted rights "
                         "stay unknown, and unknown is restrictive"
                         % ", ".join(identity.RIGHTS_OPERATIONS))
    si.add_argument("--preview", action="store_true",
                    help="extract and print without writing anything")
    si.add_argument("--snapshot-storage", dest="snapshot_storage",
                    choices=("auto", "inline", "reference"), default=None,
                    help="how a captured remote snapshot is stored, "
                         "overriding source.snapshot_storage for this run. "
                         "inline keeps the bytes beside the course; reference "
                         "caches them as disposable derived state")
    si.add_argument("--confirm", action="store_true",
                    help="approve this bind under the approve_before_bind "
                         "policy. Only an agent actor needs it; a human at "
                         "this terminal is the approval")
    si.add_argument("--json", action="store_true",
                    help="emit the result dict as JSON")
    si.set_defaults(fn=cmd_source)

    sr = t.add_parser("recheck", help="report whether a captured remote "
                      "origin still matches (a read: writes nothing, exits 0 "
                      "for all three states including origin_unreachable)")
    sr.add_argument("--base", default=".",
                    help="approved root holding the source and its journal "
                         "(default: current directory)")
    sr.add_argument("object_id",
                    help="the opaque id of the captured source object")
    sr.add_argument("--json", action="store_true",
                    help="emit the report dict as JSON")
    sr.set_defaults(fn=cmd_source_recheck)

    s = sub.add_parser("course", help="create, rename, read a course, or "
                       "record a source in it, the CLI twin of POST "
                       "/api/course/<operation>")
    ct = s.add_subparsers(dest="action", required=True)
    for name, blurb in (
            ("create", "mint a course: one course-graph.md sidecar written "
                       "through the compare-and-swap path, every section "
                       "empty"),
            ("rename", "retitle a course; identity, bindings and evidence "
                       "are untouched"),
            ("add-source", "record an imported source in this course's "
                           "Sources section, the step between importing a "
                           "source and binding it")):
        cp = ct.add_parser(name, help=blurb)
        cp.add_argument("course_id",
                        help="the course id, as the shelf and /course/<id> "
                             "spell it")
        cp.add_argument("--title", required=True,
                        help="the source's title for a human reader"
                             if name == "add-source"
                             else "the course's human-readable title")
        cp.add_argument("--root", default=".",
                        help="the workspace holding course directories "
                             "(default: current directory)")
        cp.add_argument("--actor", default="",
                        help="who is recording this, for the operation journal")
        cp.add_argument("--json", action="store_true",
                        help="emit the operation result as JSON")
        if name == "add-source":
            cp.add_argument("--source", required=True,
                            dest="source_object_id",
                            help="the opaque id of a source object this "
                                 "course root's journal registry already "
                                 "holds, as `itembank bind list` prints it")
            cp.add_argument("--note", default="",
                            help="why this source is in this course; never "
                                 "read back for a decision")
        if name in ("rename", "add-source"):
            cp.add_argument("--expect", default="",
                            dest="expected_fingerprint",
                            help="the fingerprint you believe the sidecar "
                                 "carries; a stale one is refused by name")
        cp.set_defaults(fn=course_ops.cmd_course)

    def structural(name, blurb):
        """One `itembank course <name>` parser with the four arguments every
        structural write shares. The operation's own fields are added by the
        caller, each named exactly as the published node names it."""
        sp = ct.add_parser(name, help=blurb)
        sp.add_argument("course_id", help="the course id")
        sp.add_argument("--root", default=".",
                        help="the workspace holding course directories "
                             "(default: current directory)")
        sp.add_argument("--actor", default="",
                        help="who is recording this, for the operation journal")
        sp.add_argument("--expect", default="", dest="expected_fingerprint",
                        help="the fingerprint you believe the sidecar "
                             "carries; a stale one is refused by name")
        sp.add_argument("--json", action="store_true",
                        help="emit the operation result as JSON")
        sp.set_defaults(fn=course_ops.cmd_course)
        return sp

    cc = structural("add-container", "add one structural container (a "
                    "module, a week, a unit); adds zero edges, because "
                    "structure is not a prerequisite claim")
    cc.add_argument("--label", required=True,
                    help="what kind of container this is: module, week, "
                         "unit, or the word this course uses instead")
    cc.add_argument("--title", required=True,
                    help="the container's human-readable title")
    cc.add_argument("--parent", default="",
                    help="the id of the container this one sits inside "
                         "(default: top level)")
    cc.add_argument("--order", type=int, default=None,
                    help="the authored position within the section "
                         "(default: the end)")

    co = structural("add-objective", "add one objective; adds zero edges, "
                    "and is always recorded with origin local")
    co.add_argument("--statement", required=True,
                    help="what the learner will be able to do, in one "
                         "sentence")
    co.add_argument("--container", default="",
                    help="the id of the container it belongs to (default: "
                         "unplaced, which is a real state)")
    co.add_argument("--order", type=int, default=None,
                    help="the authored position within the section "
                         "(default: the end)")

    ce = structural("add-edge", "record one relation between two things "
                    "this course graph already holds")
    ce.add_argument("--source", required=True,
                    help="the endpoint the relation runs from; for a "
                         "prerequisite-of edge, the objective that comes "
                         "first")
    ce.add_argument("--type", required=True, dest="edge_type",
                    choices=list(graph.EDGE_TYPES),
                    help="which of the four frozen relations this asserts")
    ce.add_argument("--target", required=True,
                    help="the endpoint the relation runs to")
    ce.add_argument("--authority", default=graph.EDGE_FIELD_DEFAULTS["authority"],
                    choices=list(graph.EDGE_AUTHORITIES),
                    help="where the claim comes from (default: proposed, "
                         "the least-blocking value)")
    ce.add_argument("--rationale", default="", help="why this relation holds")
    ce.add_argument("--confidence", default=graph.EDGE_FIELD_DEFAULTS["confidence"],
                    choices=list(graph.EDGE_CONFIDENCES),
                    help="how sure the claim is (default: unknown)")
    ce.add_argument("--override", default=graph.EDGE_FIELD_DEFAULTS["override"],
                    choices=list(graph.EDGE_OVERRIDES),
                    help="how hard this edge blocks; hard-gate is never a "
                         "default and has to be written explicitly")

    cst = ct.add_parser("structure", help="print the containers, objectives "
                        "and edges, each edge as this build reads it, and "
                        "the warnings the authored order earns")
    cst.add_argument("course_id", help="the course id")
    cst.add_argument("--root", default=".",
                     help="the workspace holding course directories "
                          "(default: current directory)")
    cst.add_argument("--propose-order", action="store_true",
                     dest="propose_order",
                     help="also compute an order satisfying every "
                          "prerequisite; a proposal, never written")
    cst.add_argument("--json", action="store_true",
                     help="emit the whole reading as JSON")
    cst.set_defaults(fn=course_ops.cmd_course)

    cr = structural("rename-objective", "restate one objective as a "
                    "reviewed proposal: a new row and a migration, never an "
                    "edit to the original")
    cr.add_argument("--objective", required=True,
                    help="the id of the objective being restated")
    cr.add_argument("--statement", required=True, help="the new statement")
    cr.add_argument("--rationale", required=True,
                    help="why the identity is moving; a reviewer reads this")

    csp = structural("split-objective", "split one objective into several "
                     "as a reviewed proposal; adds rows and deletes none")
    csp.add_argument("--objective", required=True,
                     help="the id of the objective being split")
    csp.add_argument("--statement", required=True, nargs="+",
                     dest="statements",
                     help="the statements it splits into, at least two, in "
                          "authored order")
    csp.add_argument("--rationale", required=True,
                     help="why the identity is moving; a reviewer reads this")

    cm = structural("merge-objectives", "merge several objectives into one "
                    "as a reviewed proposal; every merged-from row stays")
    cm.add_argument("--objective", required=True, nargs="+",
                    dest="objectives",
                    help="the ids being merged, at least two, each named once")
    cm.add_argument("--statement", required=True,
                    help="the statement the merged objective carries")
    cm.add_argument("--rationale", required=True,
                    help="why the identity is moving; a reviewer reads this")

    cov = structural("overlay-objective", "record a local revision of an "
                     "imported objective as a sibling row, which is what to "
                     "reach for when a rename refuses because the target "
                     "was imported")
    cov.add_argument("--objective", required=True,
                     help="the id of the imported objective being revised")
    cov.add_argument("--statement", required=True,
                     help="the local revision's statement")

    for name, blurb in (("accept-migration", "accept a proposed migration"),
                        ("reject-migration", "reject a proposed migration")):
        mp = structural(name, blurb)
        mp.add_argument("--migration-id", required=True)
        mp.add_argument("--rationale", required=True)
        mp.add_argument("--operation", dest="operation_id", default="",
                        help="operation id to attach to the settlement; one is "
                             "minted when omitted and may be passed to "
                             "course reverse-operation for exact undo")

    def blueprint_cmd(name, blurb):
        bp = ct.add_parser(name, help=blurb)
        bp.add_argument("course_id", help="the course id")
        bp.add_argument("--root", default=".")
        bp.add_argument("--actor", default="")
        bp.add_argument("--json", action="store_true")
        bp.set_defaults(fn=course_ops.cmd_course)
        return bp
    bb = blueprint_cmd("bind-blueprint", "record an accepted blueprint")
    bb.add_argument("--blueprint", required=True, type=json.loads)
    bb.add_argument("--expect", default="", dest="expected_fingerprint")
    bg = blueprint_cmd("blueprint-gate", "check questions against a blueprint")
    bg.add_argument("--questions", required=True, type=json.loads)
    bg.add_argument("--blueprint", type=json.loads, default=None)
    bg.add_argument("--item-facts", type=json.loads, default=None, dest="item_facts")
    au = blueprint_cmd("audit", "aggregate course audit signals")
    for field in ("treatment_rows", "coverage_rows", "quality_findings", "blueprint_findings"):
        au.add_argument("--" + field.replace("_", "-"), type=json.loads, default=None, dest=field)
    au.add_argument("--vocabulary-members", type=json.loads, default=None, dest="vocabulary_members")
    au.add_argument("--tool-version", default="", dest="tool_version")
    st = blueprint_cmd("staleness", "report stale dependents")
    st.add_argument("--dependents", required=True, type=json.loads)

    pe = ct.add_parser("export-package", help="export one course to a local "
                       "plain-directory package below _packages")
    pe.add_argument("course_id", help="the course id")
    pe.add_argument("--root", default=".",
                    help="the workspace holding the course and _packages")
    pe.add_argument("--expect", default="", dest="expected_fingerprint",
                    help="the course fingerprint expected before export")
    pe.add_argument("--actor", default="",
                    help="who requested the local export")
    pe.add_argument("--json", action="store_true",
                    help="emit the complete package result as JSON")
    pe.set_defaults(fn=course_ops.cmd_course)

    for name, blurb in (
            ("verify-package", "verify every payload fingerprint without "
                               "writing"),
            ("restore-package", "restore into a fresh course directory "
                                "through fixed staging"),
            ("package-losses", "read the structured and plain-text package "
                               "loss report")):
        pp = ct.add_parser(name, help=blurb)
        pp.add_argument("package_id", help="the opaque package id")
        pp.add_argument("--root", default=".",
                        help="the workspace holding _packages")
        if name == "restore-package":
            pp.add_argument("--actor", default="",
                            help="who requested the local restore")
        pp.add_argument("--json", action="store_true",
                        help="emit the complete package result as JSON")
        pp.set_defaults(fn=course_ops.cmd_course)

    # The director family (19A-05). One helper, because these six share the
    # course id and root every course command takes and differ only in what
    # they declare; `--expect` is deliberately absent, since none of them is
    # an edit_in_place on the sidecar.
    def director_cmd(name, blurb):
        dp = ct.add_parser(name, help=blurb)
        dp.add_argument("course_id", help="the course id")
        dp.add_argument("--root", default=".",
                        help="the workspace holding course directories and "
                             "itembank.json, whose agent_policy grants this "
                             "operation's authority (default: current "
                             "directory)")
        dp.add_argument("--actor", default="",
                        help="who is recording this, for the operation journal")
        dp.add_argument("--json", action="store_true",
                        help="emit the operation result as JSON")
        dp.set_defaults(fn=course_ops.cmd_course)
        return dp

    def declaring_cmd(name, blurb):
        """A director command that declares an authority. The level is a
        DECLARATION checked against settings, never a grant: an
        over-declaration is refused rather than narrowed."""
        dp = director_cmd(name, blurb)
        dp.add_argument("--role", required=True, dest="actor_role",
                        help="what role this operation acts in "
                             "(course-builder, reviewer); a description of "
                             "the work and never a permission")
        dp.add_argument("--autonomy", required=True,
                        choices=list(director.AUTONOMY_LEVELS),
                        help="the authority this operation declares; it is "
                             "checked against itembank.json's "
                             "agent_policy.autonomy_level and an "
                             "over-declaration is refused, not narrowed")
        dp.add_argument("--scope", default=[], nargs="+", dest="scopes",
                        help="the approved roots this operation declares it "
                             "will work within")
        return dp

    ca = director_cmd("autonomy", "print what this installation permits an "
                      "agent operation to do, and whether one declaration "
                      "would be authorized; reads settings and writes "
                      "nothing")
    ca.add_argument("--declare", default="", dest="declared_level",
                    choices=[""] + list(director.AUTONOMY_LEVELS),
                    help="also dry-run this exact declaration")
    ca.add_argument("--bindings", type=int, default=None,
                    dest="bindings_requested",
                    help="how many bindings the hypothetical operation would "
                         "write, checked against the per-operation cap")

    cb = declaring_cmd("begin-operation", "declare an operation's intent, "
                       "role, authority and scopes before it does anything, "
                       "and get the operation id every later phase carries")
    cb.add_argument("--intent", required=True,
                    help="what is about to be attempted, in one sentence")

    crp = ct.add_parser("replay", help="replay one recorded operation "
                        "against the thirteen-step protocol, say where an "
                        "interrupted one resumes, and print what left this "
                        "machine")
    crp.add_argument("course_id", help="the course id")
    crp.add_argument("--operation", required=True, dest="operation_id",
                     help="the operation id `course begin-operation` minted")
    crp.add_argument("--root", default=".",
                     help="the workspace holding course directories "
                          "(default: current directory)")
    crp.add_argument("--json", action="store_true",
                     help="emit the whole report as JSON")
    crp.set_defaults(fn=course_ops.cmd_course)

    cro = director_cmd("reverse-operation", "undo one operation's durable "
                       "writes, newest first, through journal.undo; entries "
                       "that wrote no bytes are skipped and reported")
    cro.add_argument("--operation", required=True, dest="operation_id",
                     help="the operation id to reverse")

    crec = declaring_cmd("recommend", "ask the configured model backend to "
                         "recommend a treatment for one objective; records "
                         "the attempt and binds nothing")
    crec.add_argument("--objective", required=True,
                      help="the objective id to recommend a treatment for")
    crec.add_argument("--profile", default="",
                      help="which model profile from settings to use "
                           "(default: the active one)")

    cpass = declaring_cmd("recommend-pass", "one recommendation pass over "
                          "many objectives: one entry each, none skipped, "
                          "and bindings written only at "
                          "approved-bounded-write within the cap")
    cpass.add_argument("--objective", required=True, nargs="+",
                       dest="objectives",
                       help="the objective ids to pass over, in order")
    cpass.add_argument("--profile", default="",
                       help="which model profile from settings to use "
                            "(default: the active one)")

    cap = director_cmd("apply-recommendation", "bind an accepted "
                       "recommendation, or refuse it against the rights as "
                       "they read right now")
    cap.add_argument("--source", required=True,
                     help="the source object id the treatment is bound to")
    cap.add_argument("--record", required=True, type=json.loads,
                     help="the recommendation record as JSON, as `course "
                          "recommend --json` returned it; its contract is "
                          "schemas/treatment_recommendation.schema.json")
    cap.add_argument("--operation", default="", dest="operation_id",
                     help="the operation id this bind belongs to (default: "
                          "a new one)")
    cap.add_argument("--profile", default="",
                     help="the profile name to record on the bind's egress "
                          "disclosure")

    cs = ct.add_parser("show", help="print a course's identity, title, "
                       "fingerprint and section counts")
    cs.add_argument("course_id", help="the course id")
    cs.add_argument("--root", default=".",
                    help="the workspace holding course directories "
                         "(default: current directory)")
    cs.add_argument("--json", action="store_true",
                    help="emit the reading as JSON")
    cs.set_defaults(fn=course_ops.cmd_course)

    s = sub.add_parser("bind", help="bind a source or a treatment to an "
                       "objective, list what a course holds, or record a "
                       "source's rights")
    bt = s.add_subparsers(dest="action", required=True)
    for name, blurb in (
            ("source", "bind a source to an objective as coverage; consumes "
                       "the source's read right"),
            ("treatment", "bind a treatment to an objective; the treatment "
                          "decides which right it consumes, so an excerpt "
                          "refuses on quote and a guided lesson on "
                          "transform")):
        bp = bt.add_parser(name, help=blurb)
        bp.add_argument("--base", default=".",
                        help="the course root holding course-graph.md "
                             "(default: current directory)")
        bp.add_argument("--objective", required=True,
                        help="the objective id, as `itembank bind list` prints it")
        bp.add_argument("--source", required=True,
                        help="the source object id, as `itembank bind list` prints it")
        bp.add_argument("--locator", default="",
                        help="where in the source: a path, an anchor, a page")
        bp.add_argument("--state", default="unknown",
                        choices=list(graph.BINDING_STATES),
                        help="the coverage state this binding claims "
                             "(default: unknown; covered is never a default)")
        bp.add_argument("--confidence", default="unknown",
                        choices=list(graph.EDGE_CONFIDENCES),
                        help="how sure the claim is (default: unknown)")
        bp.add_argument("--actor", default="",
                        help="who is recording this, for the operation journal")
        bp.add_argument("--json", action="store_true",
                        help="emit the result as JSON")
        if name == "treatment":
            bp.add_argument("--treatment", required=True,
                            choices=list(graph.TREATMENT_KINDS),
                            help="which of the eleven treatments this is")
        bp.set_defaults(fn=binding_cli.cmd_bind)

    btr = bt.add_parser("treatments", help="print the eleven treatments, the "
                        "right each one consumes, and, for one source, "
                        "whether that right is granted right now")
    btr.add_argument("--base", default=".",
                     help="the course root (default: current directory)")
    btr.add_argument("--source", default="",
                     help="the source object id to resolve the table "
                          "against; omitted prints the mapping alone, with "
                          "no right resolved")
    btr.add_argument("--json", action="store_true",
                     help="emit the whole reading as JSON")
    btr.set_defaults(fn=binding_cli.cmd_bind)

    bl = bt.add_parser("list", help="print this course's objectives, sources "
                       "with their recorded rights, and every binding's "
                       "effective reading, including whether the right it "
                       "was made under still reads the same way")
    bl.add_argument("--base", default=".",
                    help="the course root (default: current directory)")
    bl.add_argument("--json", action="store_true",
                    help="emit the whole reading as JSON")
    bl.set_defaults(fn=binding_cli.cmd_bind)

    br = bt.add_parser("rights", help="record what may be done with one "
                       "source, without touching its bytes")
    br.add_argument("--base", default=".",
                    help="the course root (default: current directory)")
    br.add_argument("--source", required=True, help="the source object id")
    br.add_argument("--grant", default="",
                    help="comma-separated rights to record as granted")
    br.add_argument("--deny", default="",
                    help="comma-separated rights to record as denied")
    br.add_argument("--actor", default="",
                    help="who is recording this, for the operation journal")
    br.add_argument("--json", action="store_true",
                    help="emit the result as JSON")
    br.set_defaults(fn=binding_cli.cmd_bind)

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

    tl = t.add_parser("looks", help="list the shipped looks (shape, type and "
                      "control language) and which one is selected")
    tl.add_argument("--base", default=".",
                    help="directory holding itembank.json (default: current directory)")
    tl.add_argument("--json", action="store_true",
                    help="emit the catalogue as JSON instead of human lines")
    tl.set_defaults(fn=cmd_theme)

    tlk = t.add_parser("look", help="select a look; writes the look plus the "
                       "accent and mode it was designed around, all of which "
                       "stay changeable afterwards")
    tlk.add_argument("look")
    tlk.add_argument("--base", default=".",
                     help="directory holding itembank.json (default: current directory)")
    tlk.set_defaults(fn=cmd_theme)

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

    # Phase 11: the closed authoring loop and curriculum auditor. The author
    # subcommand binds the configured Phase 8 adapter in this composition
    # root (load_settings -> model_backend -> model_adapter.invoke); the
    # other subcommands are thin argument converters over the domain APIs.
    s = sub.add_parser("audit", help="closed authoring loop and curriculum "
                                     "auditor (Phase 11)")
    aud = s.add_subparsers(dest="audit_command", required=True)
    sa = aud.add_parser("source", help="normalize a source file into a "
                                       "locator-faithful record (read-only)")
    sa.add_argument("source")
    sa.add_argument("--source-id", default=None,
                    help="stable source identity (default: the path)")
    sa.add_argument("--kind", default=None,
                    help="adapter kind: markdown or text (default: by extension)")
    sa.set_defaults(fn=lambda a: cmd_audit(a))
    sc = aud.add_parser("coverage", help="citation-first coverage report of "
                                         "a source against a bank (read-only)")
    sc.add_argument("--source", required=True)
    sc.add_argument("--source-id", default=None)
    sc.add_argument("--bank", required=True)
    sc.set_defaults(fn=lambda a: cmd_audit(a))
    sm = aud.add_parser("material", help="turn obtained material into a new "
                                         "bounded authoring request (never "
                                         "authorizes a write)")
    sm.add_argument("material")
    sm.add_argument("--source-id", default=None)
    sm.add_argument("--objective", action="append", required=True,
                  dest="objectives")
    sm.add_argument("--count", type=int, default=1)
    sm.add_argument("--item-type", default="mc")
    sm.add_argument("--retry-cap", type=int, default=3)
    sm.add_argument("--mode", choices=["report_only", "draft_and_approve",
                                       "full"], default="report_only")
    sm.set_defaults(fn=lambda a: cmd_audit(a))
    sauth = aud.add_parser("author", help="run the bounded authoring loop "
                                          "through the configured model "
                                          "backend")
    sauth.add_argument("--source", required=True,
                       help="the cited source (syllabus) file")
    sauth.add_argument("--source-id", default=None)
    sauth.add_argument("--bank", required=True,
                       help="the bank file to extend (mutated only per mode)")
    sauth.add_argument("--objective", action="append", required=True,
                      dest="objectives")
    sauth.add_argument("--count", type=int, default=1)
    sauth.add_argument("--item-type", default="mc")
    sauth.add_argument("--retry-cap", type=int, default=3)
    sauth.add_argument("--mode", choices=["report_only", "draft_and_approve",
                                          "full"], default="report_only")
    sauth.add_argument("--state-dir", default=None,
                       help="manifest/before-image/pending directory "
                            "(required to write)")
    sauth.add_argument("--write", action="store_true",
                       help="wire the writer; the mode still decides whether "
                            "it may act")
    sauth.add_argument("--approve", action="append", default=[],
                       help="exact write id to approve in draft_and_approve "
                            "(repeatable; must name the pending set exactly)")
    sauth.add_argument("--cap-run", type=int, default=0,
                       help="per-run item cap for full autonomy")
    sauth.add_argument("--cap-objective", type=int, default=0,
                       help="per-objective cap for full autonomy")
    sauth.add_argument("--base", default=".",
                       help="directory whose itembank.json resolves the model "
                            "backend (default: current directory)")
    sauth.set_defaults(fn=lambda a: cmd_audit(
        a, author_callable=_configured_author_callable(
            _load_settings_for(a.base))))
    su = aud.add_parser("undo", help="one-step undo by write id (routes by "
                                     "manifest backend; refuses stale work)")
    su.add_argument("write_id")
    su.add_argument("--bank", required=True)
    su.add_argument("--state-dir", required=True)
    su.add_argument("--base", default=".",
                    help="accepted for a uniform invocation shape; undo "
                         "routes by manifest backend and never reads "
                         "settings")
    su.set_defaults(fn=lambda a: cmd_audit(a))

    # Phase 999.4: Canvas LMS integration via LTI 1.3 — the verified-launch
    # surface, the platforms registration store, and the opt-in bind.
    s = sub.add_parser("lti", help="Canvas LMS integration via LTI 1.3 "
                       "(phase 999.4): registration status, doctor, and the "
                       "opt-in bind. " + PRIVACY_STATEMENT,
                       description="Canvas LMS integration via LTI 1.3: the "
                       "verified-launch surface, the platforms registration "
                       "store, and the opt-in bind.",
                       epilog=PRIVACY_STATEMENT)
    lt = s.add_subparsers(dest="lti_action", required=True)
    lp = lt.add_parser("status", help="print the LTI registration state and "
                       "the D-09 privacy statement", epilog=PRIVACY_STATEMENT)
    lp.add_argument("--base", default=".",
                    help="directory holding itembank.json (default: current directory)")
    lp.set_defaults(fn=cmd_lti_status)
    lp = lt.add_parser("doctor", help="validate the LTI registration and print "
                       "the OIDC initiation / launch / JWKS URLs to paste into "
                       "Canvas, plus the privacy statement (D-09)",
                       epilog=PRIVACY_STATEMENT)
    lp.add_argument("--base", default=".",
                    help="directory holding itembank.json (default: current directory)")
    lp.set_defaults(fn=cmd_lti_doctor)
    lp = lt.add_parser("serve", help="start the opt-in LTI handler family "
                       "(requires lti.enabled true; TLS via lti.tls_cert/"
                       "lti.tls_key or documented reverse proxy)",
                       epilog=PRIVACY_STATEMENT)
    lp.add_argument("dir", nargs="?", default=".")
    lp.add_argument("--host", default="127.0.0.1",
                    help="bind host (default: 127.0.0.1; put a reverse proxy "
                         "in front for the public posture)")
    lp.add_argument("--port", type=int, default=None,
                   help="bind port (default: 8732)")
    lp.add_argument("--no-open", action="store_true", dest="no_open",
                    help="do not launch a browser (the LTI bind never opens "
                         "a browser on its own)")
    lp.set_defaults(fn=cmd_lti_serve)

    return ap


def command_names(parser=None):
    """Every top-level command name, sorted. Read from the parser itself."""
    parser = parser or build_parser()
    for action in parser._subparsers._group_actions:
        if hasattr(action, "choices"):
            return sorted(action.choices)
    return []


def subcommand_names(parser=None):
    """`{command: [subcommand, ...]}` for the commands that have them."""
    parser = parser or build_parser()
    found = {}
    for action in parser._subparsers._group_actions:
        if not hasattr(action, "choices"):
            continue
        for name, sub in sorted(action.choices.items()):
            subs = []
            if getattr(sub, "_subparsers", None):
                for inner in sub._subparsers._group_actions:
                    if hasattr(inner, "choices"):
                        subs.extend(sorted(inner.choices))
            if subs:
                found[name] = subs
    return found


def main():
    a = build_parser().parse_args()
    sys.exit(a.fn(a))


def _load_settings_for(base):
    """The settings loader used by the audit author composition root; kept
    as a function so the closure binds the resolved document once."""
    from surfaces.settings import load_settings
    return load_settings(base)
