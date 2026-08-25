#!/usr/bin/env python3
"""Seeding accept-loop round-trip tests (plan 03.2-03).

Covers the three tasks: the six-stage pipeline in the locked order (D-08)
with deterministic checks before any model critique and retry within a cap,
the one accept endpoint (`accept_candidate`) shared by the CLI and the daemon
route (D-07) with lint-refuse / append-exactly-once / skip-defer, the
batch-framed browser surface per UI-SPEC sections 2 and 4 (verbatim copy, no
chat affordance, no fill bar, Accept disabled with a stated reason on lint
errors), and the refuse-by-name degrade when no backend is reachable (D-10).

Standard library only, runnable as `python tests/seeding_roundtrip.py`. The
pipeline is driven headless through the deterministic FakeModelAdapter (the
Phase 8 adapter seam is not built in code yet -- the plan documents the
interface and satisfies tests with a fake).
"""
import contextlib
import io
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import types
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
TOOL = os.path.join(ROOT, "itembank.py")

from model import content_fingerprint, parse_bank, parse_question, parse_sources  # noqa: E402
from surfaces import cli, daemon, seeding                                 # noqa: E402
from surfaces.seeding import (                                            # noqa: E402
    ACCEPT_COPY, BACKEND_UNREACHABLE, BATCH_FRAMING_LINE, CANCEL_COPY,
    CANCELLED_SUMMARY, NO_SOURCE_RECORDED, PROGRESS_LINE, SKIP_COPY,
    FakeModelAdapter, run_seeding_run, render_accept_surface,
    render_cancelled_surface, render_degraded_surface)


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def run_cli(*args, **kw):
    return subprocess.run([sys.executable, TOOL, *map(str, args)],
                          cwd=ROOT, capture_output=True, text=True, **kw)


# ---------------------------------------------------------------------------
# Synthetic fixtures (never real data)
# ---------------------------------------------------------------------------

REGISTRY = ("emt:airway | EMT airway chapter, sect. 5\n"
            "emt:ops | EMT operations chapter 9\n")

AIRWAY_ITEM = (
    "Q1. Which finding suggests an at-risk airway?   (difficulty: recall)\n"
    "[OBJECTIVE: emt:airway]\n"
    "[SRC: emt:airway sect-5]\n"
    "\n"
    "A) Stridor\n"
    "B) Normal breath sounds\n"
    "C) Wheezing\n"
    "D) Hiccups\n"
    "\n"
    "CORRECT: A\n"
    "\n"
    "WHY BEST: Stridor indicates upper-airway obstruction.\n"
    "\n"
    "KEY DISCRIMINATOR: Upper-airway origin.\n"
    "\n"
    "SECOND-BEST: C. Wheezing is lower-airway.\n"
    "\n"
    "DISTRACTOR ANALYSIS:\n"
    "- A) Correct: stridor is the keyed answer.\n"
    "- B) Normal.\n"
    "- C) Lower airway.\n"
    "\n"
    "TRAP: Confusing upper and lower airway sounds.\n"
    "\n"
    "CONFIDENCE: high\n")

SEED_BANK = ("# Seeding fixture (synthetic)\n\n"
             "## SOURCES\n\n" + REGISTRY + "\n" + AIRWAY_ITEM)


def write_seed_bank(td, name="seed_bank.md"):
    bank = os.path.join(td, name)
    open(bank, "w", encoding="utf-8").write(SEED_BANK)
    return bank


FAKE_OUTLINE = "Stem\nOptions\nRationale"
# Deliberately distinct from the bank's own Q1 (an airway item) so the
# exactly-once fingerprint dedup never fires on a first accept.
FAKE_STEM = "Which sign most strongly suggests upper-airway obstruction?"
# Four options, not three: an `emt:` item is linted against NREMT's published
# structure (1 correct of exactly 4), so a three-option draft would now be a
# stage-4 error and would change the retry counts these tests assert.
FAKE_OPTIONS = ("A) Inspiratory stridor\nB) Expiratory wheeze\n"
                "C) Productive cough\nD) Hoarse voice\n\nCORRECT: A")
FAKE_RATIONALE = (
    "WHY BEST: Inspiratory stridor is the upper-airway sign.\n\n"
    "KEY DISCRIMINATOR: Inspiratory timing.\n\n"
    "SECOND-BEST: B. Expiratory wheeze is lower-airway.\n\n"
    "TRAP: Confusing inspiratory and expiratory findings.\n\n"
    "CONFIDENCE: high")
FAKE_DIRTY_RATIONALE = ""


def bank_item_count(bank_path):
    return len(parse_bank(open(bank_path, encoding="utf-8").read()))


# ---------------------------------------------------------------------------
# Task 1: the six-stage pipeline in the locked order
# ---------------------------------------------------------------------------

def test_six_stage_order_is_locked():
    """The stage order is asserted structurally: STAGES is the exact locked
    tuple (D-08) and an executed run walks it in that order. A reorder of
    either the constant or the pipeline fails this fixture."""
    expected = ("source selection", "outline", "drafting", "checks",
                "verification", "accept")
    if seeding.STAGES != expected:
        fail("STAGES was reordered: %r != %r" % (seeding.STAGES, expected))
    with tempfile.TemporaryDirectory() as td:
        bank = write_seed_bank(td)
        run = run_seeding_run(bank, FakeModelAdapter(
            outline=FAKE_OUTLINE, stem=FAKE_STEM, options=FAKE_OPTIONS,
            rationale=FAKE_RATIONALE))
        if run.refused:
            fail("a fake-adapter run must not refuse: %r" % run.refusal)
        if tuple(run.stages) != expected:
            fail("the run did not walk the stages in the locked order: %r"
                 % run.stages)


def test_fake_adapter_runs_headless_with_each_stage_visible():
    with tempfile.TemporaryDirectory() as td:
        bank = write_seed_bank(td)
        adapter = FakeModelAdapter(
            outline=FAKE_OUTLINE, stem=FAKE_STEM, options=FAKE_OPTIONS,
            rationale=FAKE_RATIONALE)
        run = run_seeding_run(bank, adapter)
        if run.refused:
            fail("fake-adapter run refused")
        # Stage 1: deterministic source selection from the ## SOURCES registry.
        if run.source_selection != ["emt:airway", "emt:ops"]:
            fail("stage 1 must select sources deterministically from the "
                 "registry: %r" % run.source_selection)
        if run.objective != "emt:airway":
            fail("the run objective must derive deterministically: %r"
                 % run.objective)
        if not run.outline:
            fail("stage 2 must produce an outline")
        if len(run.drafts) != 1:
            fail("one clean draft expected, got %d" % len(run.drafts))
        draft = run.drafts[0]
        if draft["candidate"] is None:
            fail("the draft must parse as an item")
        if draft["lint_errors"]:
            fail("a clean fake draft must pass the deterministic checks, got %r"
                 % draft["lint_errors"])
        if not draft.get("verify"):
            fail("stage 5 must record the independent verification pass")
        if adapter.verify_calls != 1:
            fail("verification must run exactly once over the clean draft, got %d"
                 % adapter.verify_calls)


def test_retry_before_critique_within_the_cap():
    """A draft that fails the deterministic checks (stage 4) is retried before
    any model critique; verification only ever runs over a clean draft."""
    with tempfile.TemporaryDirectory() as td:
        bank = write_seed_bank(td)
        adapter = FakeModelAdapter(
            outline=FAKE_OUTLINE, stem=FAKE_STEM, options=FAKE_OPTIONS,
            rationale=FAKE_RATIONALE, rationale_dirty_attempts=1)
        run = run_seeding_run(bank, adapter, retry_cap=3)
        draft = run.drafts[0]
        if draft["attempts"] != 2:
            fail("a dirty first draft must retry exactly once, got attempts=%d"
                 % draft["attempts"])
        if draft["lint_errors"]:
            fail("the retried draft must be clean, got %r" % draft["lint_errors"])
        if adapter.verify_calls != 1:
            fail("the model critique must run exactly once, after the clean "
                 "draft: %d" % adapter.verify_calls)


def test_retry_cap_enforced_and_no_critique_of_a_dirty_draft():
    with tempfile.TemporaryDirectory() as td:
        bank = write_seed_bank(td)
        adapter = FakeModelAdapter(
            outline=FAKE_OUTLINE, stem=FAKE_STEM, options=FAKE_OPTIONS,
            rationale=FAKE_RATIONALE, rationale_dirty_attempts=99)
        run = run_seeding_run(bank, adapter, retry_cap=2)
        if run.drafts:
            fail("a cap-exhausted draft must not be presented for accept")
        if len(run.failed_drafts) != 1:
            fail("expected exactly one failed draft, got %d"
                 % len(run.failed_drafts))
        if adapter.verify_calls != 0:
            fail("the model must never critique a draft that failed the "
                 "deterministic checks, got %d verify calls" % adapter.verify_calls)
        if not run.failed_drafts[0]["lint_errors"]:
            fail("the failed draft must record its deterministic errors")


def test_provenance_directives_checked_deterministically_in_stage4():
    """A draft whose [SRC:] does not resolve in the bank's ## SOURCES registry
    fails the deterministic checks before any model critique (D-11)."""
    with tempfile.TemporaryDirectory() as td:
        bank = write_seed_bank(td)
        rationale = FAKE_RATIONALE + "\n[SRC: bogus chapter-1]\n"
        adapter = FakeModelAdapter(
            outline=FAKE_OUTLINE, stem=FAKE_STEM, options=FAKE_OPTIONS,
            rationale=rationale, rationale_dirty_attempts=0)
        run = run_seeding_run(bank, adapter, retry_cap=1)
        if run.drafts:
            fail("an unresolvable [SRC:] draft must not be presented")
        if len(run.failed_drafts) != 1:
            fail("expected one provenance-failed draft")
        joined = " ".join(run.failed_drafts[0]["lint_errors"])
        if "prov.src_unknown" not in joined or "bogus" not in joined:
            fail("stage 4 must name the unresolvable source id, got %r"
                 % run.failed_drafts[0]["lint_errors"])
        if adapter.verify_calls != 0:
            fail("no model critique may run on a provenance-failing draft")


def test_cancelled_run_writes_nothing():
    with tempfile.TemporaryDirectory() as td:
        bank = write_seed_bank(td)
        before = open(bank, "rb").read()
        adapter = FakeModelAdapter(
            outline=FAKE_OUTLINE, stem=FAKE_STEM, options=FAKE_OPTIONS,
            rationale=FAKE_RATIONALE)
        run = run_seeding_run(bank, adapter)
        run.cancel()
        if not run.cancelled:
            fail("cancel must mark the run cancelled")
        if open(bank, "rb").read() != before:
            fail("a cancelled run must write nothing (D-09)")
        if CANCELLED_SUMMARY not in run.summary():
            fail("the cancelled summary must state Nothing was written.")


# ---------------------------------------------------------------------------
# Task 2: the one accept endpoint behind two surfaces
# ---------------------------------------------------------------------------

def test_accept_refuses_lint_error_candidates():
    with tempfile.TemporaryDirectory() as td:
        bank = write_seed_bank(td)
        before = bank_item_count(bank)
        # A parseable mc item missing its WHY BEST field fails lint.
        dirty = parse_question(
            "Q1. Which is the keyed answer?   (difficulty: recall)\n"
            "A) One\nB) Two\n\nCORRECT: A\n")
        result = seeding.accept_candidate(bank, dirty)
        if result.get("accepted"):
            fail("a lint-error candidate must never be accepted")
        if "item.missing_why_best" not in result.get("reason", ""):
            fail("the refusal must name the lint code, got %r" % result)
        if bank_item_count(bank) != before:
            fail("a refused candidate must not write to the bank")


def test_accept_appends_clean_item_exactly_once():
    with tempfile.TemporaryDirectory() as td:
        bank = write_seed_bank(td)
        before = bank_item_count(bank)
        adapter = FakeModelAdapter(
            outline=FAKE_OUTLINE, stem=FAKE_STEM, options=FAKE_OPTIONS,
            rationale=FAKE_RATIONALE)
        run = run_seeding_run(bank, adapter)
        draft = run.drafts[0]
        result = seeding.accept_candidate(bank, draft["candidate"])
        if not result.get("accepted"):
            fail("a clean candidate must accept, got %r" % result)
        after = bank_item_count(bank)
        if after != before + 1:
            fail("accept must append exactly one item, %d -> %d"
                 % (before, after))
        # Appending the same item a second time is refused -- exactly once.
        result2 = seeding.accept_candidate(bank, draft["candidate"])
        if result2.get("accepted"):
            fail("the same item must never be appended twice")
        if not result2.get("already_accepted"):
            fail("a duplicate accept must be reported as already accepted: %r"
                 % result2)
        if bank_item_count(bank) != after:
            fail("a duplicate accept must not write a second copy")


def test_skip_defers_and_reports_never_discards():
    with tempfile.TemporaryDirectory() as td:
        bank = write_seed_bank(td)
        adapter = FakeModelAdapter(
            outline=FAKE_OUTLINE, stem=FAKE_STEM, options=FAKE_OPTIONS,
            rationale=FAKE_RATIONALE)
        run = run_seeding_run(bank, adapter)
        before = bank_item_count(bank)
        run.skip(0)
        if run.skipped != [0]:
            fail("skip must record the deferral, got %r" % run.skipped)
        if len(run.drafts) != 1:
            fail("a skipped item must stay in the draft set (deferral, not discard)")
        summary = run.summary()
        if "1 skipped" not in summary:
            fail("the end-of-run report must surface skipped items: %r" % summary)
        if bank_item_count(bank) != before:
            fail("a skipped item must not be written to the bank")


def test_cli_and_route_share_accept_candidate():
    """D-07's import-grep proof: the CLI command and the daemon route call the
    SAME accept_candidate function -- one implementation, two surfaces."""
    cli_src = open(os.path.join(ROOT, "surfaces", "cli.py"),
                   encoding="utf-8").read()
    daemon_src = open(os.path.join(ROOT, "surfaces", "daemon.py"),
                      encoding="utf-8").read()
    if "from surfaces import seeding" not in cli_src:
        fail("the CLI must import the seeding module")
    if "seeding.accept_candidate" not in cli_src:
        fail("the CLI command must call seeding.accept_candidate")
    if "seeding.accept_candidate" not in daemon_src:
        fail("the daemon route must call seeding.accept_candidate")


def test_cli_accept_loop_reaches_the_shared_endpoint():
    """The CLI accept loop drives the same accept_candidate the route uses:
    an accept decision appends to the bank through that one endpoint, and a
    cancel decision prints the verbatim summary without writing (D-07/D-09).
    A run produces exactly one draft, so the two decisions are exercised in
    two invocations -- one decision per draft, per the per-item contract."""
    with tempfile.TemporaryDirectory() as td:
        bank = write_seed_bank(td)
        before = bank_item_count(bank)
        run = run_seeding_run(bank, FakeModelAdapter(
            outline=FAKE_OUTLINE, stem=FAKE_STEM, options=FAKE_OPTIONS,
            rationale=FAKE_RATIONALE))
        saved = cli.seeding.run_seeding_run
        old_stdin = sys.stdin
        try:
            cli.seeding.run_seeding_run = lambda bank_, adapter=None: run
            # Leg 1: accept -- one decision for the single draft.
            out = io.StringIO()
            sys.stdin = io.StringIO("accept\n")
            with contextlib.redirect_stdout(out):
                rc = cli.cmd_seed(types.SimpleNamespace(bank=bank))
            if rc != 0:
                fail("cmd_seed exited %d on the accept leg" % rc)
            if bank_item_count(bank) != before + 1:
                fail("the CLI accept decision must write through accept_candidate")
            # Leg 2: cancel a fresh decision pass -- nothing more is written.
            out2 = io.StringIO()
            sys.stdin = io.StringIO("cancel\n")
            with contextlib.redirect_stdout(out2):
                rc2 = cli.cmd_seed(types.SimpleNamespace(bank=bank))
            if rc2 != 0:
                fail("cmd_seed exited %d on the cancel leg" % rc2)
            if bank_item_count(bank) != before + 1:
                fail("the cancelled leg must write nothing (D-09)")
            if CANCELLED_SUMMARY not in out2.getvalue():
                fail("cancelling the CLI run must print Nothing was written.")
        finally:
            cli.seeding.run_seeding_run = saved
            sys.stdin = old_stdin


class StubHandler:
    """A minimal stand-in for the daemon's Handler: route handlers read JSON,
    resolve a bank stem through the startup allowlist, and reply with
    send_json/send_error. Enough to exercise handle_seed_accept headlessly
    without binding a socket."""

    def __init__(self, body, client=("127.0.0.1", 5000), origin=None):
        self._body = body
        self.client_address = client
        self.headers = {"Host": "127.0.0.1:8730"}
        if origin:
            self.headers["Origin"] = origin
        self.sent = {}

    def read_json(self):
        return self._body

    def send_json(self, payload):
        self.sent["json"] = payload

    def send_error(self, code, msg=None):
        self.sent["error"] = (code, msg)

    def send_not_found(self, name):
        self.sent["error"] = (404, name)


def _clean_draft_dict():
    return parse_question(
        "Q1. Which sign most strongly suggests upper-airway obstruction?   "
        "(difficulty: recall)\n"
        "A) Inspiratory stridor\nB) Expiratory wheeze\nC) Productive cough\n"
        "\nCORRECT: A\n\n"
        "WHY BEST: Inspiratory stridor is the upper-airway sign.\n\n"
        "KEY DISCRIMINATOR: Inspiratory timing.\n\n"
        "SECOND-BEST: B. Expiratory wheeze is lower-airway.\n\n"
        "TRAP: Confusing inspiratory and expiratory findings.\n\n"
        "CONFIDENCE: high\n")


def test_route_sits_behind_the_loopback_authority_gate():
    """The accept route is a mutating write: a non-loopback client is refused
    before any helper runs, and nothing is written (no network writes)."""
    with tempfile.TemporaryDirectory() as td:
        bank = write_seed_bank(td)
        before = bank_item_count(bank)
        handler = StubHandler(
            {"bank": "seed_bank", "action": "accept",
             "draft": _clean_draft_dict()},
            client=("203.0.113.5", 5000))
        handler.banks = {"seed_bank": bank}
        daemon.handle_seed_accept(handler)
        err = handler.sent.get("error")
        if not err or err[0] != 403:
            fail("a non-loopback accept must be refused with 403, got %r"
                 % handler.sent)
        if bank_item_count(bank) != before:
            fail("a refused accept must write nothing")


def test_route_accept_calls_the_same_accept_candidate():
    """A loopback POST /seed/accept accept reaches seeding.accept_candidate
    and appends the item -- the daemon's one surface over the one endpoint."""
    with tempfile.TemporaryDirectory() as td:
        bank = write_seed_bank(td)
        before = bank_item_count(bank)
        handler = StubHandler(
            {"bank": "seed_bank", "action": "accept",
             "draft": _clean_draft_dict()})
        handler.banks = {"seed_bank": bank}
        daemon.handle_seed_accept(handler)
        result = handler.sent.get("json")
        if not result or not result.get("accepted"):
            fail("a loopback accept must succeed, got %r" % handler.sent)
        if bank_item_count(bank) != before + 1:
            fail("the route accept must append through accept_candidate")


def test_route_unknown_bank_is_a_404():
    with tempfile.TemporaryDirectory() as td:
        bank = write_seed_bank(td)
        handler = StubHandler({"bank": "not_a_bank", "action": "cancel"})
        handler.banks = {"seed_bank": bank}
        daemon.handle_seed_accept(handler)
        err = handler.sent.get("error")
        if not err or err[0] != 404:
            fail("an unknown bank stem must be a 404, got %r" % handler.sent)


# ---------------------------------------------------------------------------
# Task 3: the batch-framed surface and the degrade contract
# ---------------------------------------------------------------------------

def test_copy_contract_verbatim():
    """Every UI-SPEC section 4 string exists verbatim, in its assigned voice."""
    if BATCH_FRAMING_LINE != "This is a batch authoring run. Each item is drafted, checked, and accepted one at a time.":
        fail("the batch framing line drifted: %r" % BATCH_FRAMING_LINE)
    if PROGRESS_LINE != "Draft {n} of {m} · stage {stage}":
        fail("the stage/progress line drifted: %r" % PROGRESS_LINE)
    if ACCEPT_COPY != "Accept item":
        fail("the accept control drifted: %r" % ACCEPT_COPY)
    if SKIP_COPY != "Skip item":
        fail("the skip control drifted: %r" % SKIP_COPY)
    if CANCEL_COPY != "Cancel run":
        fail("the cancel control drifted: %r" % CANCEL_COPY)
    if CANCELLED_SUMMARY != "Nothing was written.":
        fail("the cancelled summary drifted: %r" % CANCELLED_SUMMARY)
    if BACKEND_UNREACHABLE != "The authoring backend is unreachable. Import, lint, and provenance still work.":
        fail("the backend-unreachable line drifted: %r" % BACKEND_UNREACHABLE)
    if NO_SOURCE_RECORDED != "No source recorded":
        fail("the missing-source line drifted: %r" % NO_SOURCE_RECORDED)


def test_batch_surface_verbatim_no_chat_no_fill_bar():
    with tempfile.TemporaryDirectory() as td:
        bank = write_seed_bank(td)
        run = run_seeding_run(bank, FakeModelAdapter(
            outline=FAKE_OUTLINE, stem=FAKE_STEM, options=FAKE_OPTIONS,
            rationale=FAKE_RATIONALE))
        draft = run.drafts[0]
        page = render_accept_surface(bank, draft, 1, 1, stage="accept")
        if BATCH_FRAMING_LINE not in page:
            fail("the surface must render the exact batch-framing line")
        if "Draft 1 of 1 · stage accept" not in page:
            fail("the surface must render the staged progress line")
        if ACCEPT_COPY not in page or SKIP_COPY not in page or CANCEL_COPY not in page:
            fail("the surface must render Accept/Skip/Cancel controls")
        if NO_SOURCE_RECORDED not in page:
            fail("a draft with no [SRC:] must render No source recorded")
        # No chat affordance: no input box, no textarea, no streaming, no
        # "ask the model" affordance anywhere in the markup.
        for forbidden in ("<input", "<textarea", "ask the model", "streaming"):
            if forbidden in page:
                fail("the batch surface must carry no chat affordance; found %r"
                     % forbidden)
        # No percentage or fill bar: no progress element, no bar/fill marker.
        for forbidden in ("<progress", "data-fill", "progress-bar"):
            if forbidden in page:
                fail("the batch surface must carry no fill bar; found %r"
                     % forbidden)
        if "%" in _accept_body(page):
            fail("the accept-loop markup must carry no percentage")
        if "· stage" not in page:
            fail("the staged progress must be a count, never a bar")


def _accept_body(page):
    """The page body (between <main> and </main>) -- where the surface's own
    markup lives, excluding the shared design-token CSS (which legitimately
    carries token widths, not a fill bar)."""
    return page.split("<main>", 1)[1].split("</main>", 1)[0]


def test_accept_disabled_with_reason_on_lint_errors():
    """Accept is disabled WITH the stated reason on a lint-error candidate --
    never a silent dead button (C9)."""
    with tempfile.TemporaryDirectory() as td:
        bank = write_seed_bank(td)
        dirty = parse_question(
            "Q1. Which is the keyed answer?   (difficulty: recall)\n"
            "A) One\nB) Two\n\nCORRECT: A\n")
        draft = {"block": "Q1. Which is the keyed answer?\n", "candidate": dirty,
                 "lint_errors": ["Q1: no WHY BEST field"],
                 "warnings": [], "sections": [], "section_texts": {},
                 "attempts": 1, "verify": None}
        page = render_accept_surface(bank, draft, 1, 1, stage="accept")
        if 'data-seed-action="accept" disabled' not in page:
            fail("Accept must be disabled on a lint-error candidate")
        if "Accept disabled:" not in page:
            fail("the disabled Accept must state its reason, never be silent")
        if "no WHY BEST field" not in page:
            fail("the reason must name the lint finding")


def test_cancelled_and_degraded_surfaces_verbatim():
    cancelled = render_cancelled_surface()
    if CANCELLED_SUMMARY not in cancelled:
        fail("the cancelled surface must state Nothing was written.")
    degraded = render_degraded_surface()
    if BACKEND_UNREACHABLE not in degraded:
        fail("the degraded surface must refuse by name")


def test_render_candidate_roundtrips():
    q = parse_question(
        "Q1. Which sign most strongly suggests upper-airway obstruction?   "
        "(difficulty: recall)\n"
        "A) Inspiratory stridor\nB) Expiratory wheeze\nC) Productive cough\n"
        "\nCORRECT: A\n\n"
        "WHY BEST: Inspiratory stridor is the upper-airway sign.\n\n"
        "KEY DISCRIMINATOR: Inspiratory timing.\n\n"
        "SECOND-BEST: B. Expiratory wheeze is lower-airway.\n\n"
        "TRAP: Confusing inspiratory and expiratory findings.\n\n"
        "CONFIDENCE: high\n")
    block = seeding.render_candidate(q, 7)
    q2 = parse_question(block)
    if q2 is None:
        fail("render_candidate output must re-parse:\n%s" % block)
    if q2["number"] != 7:
        fail("the rendered block must carry the assigned number, got %d"
             % q2["number"])
    if content_fingerprint(q) != content_fingerprint(q2):
        fail("render_candidate must round-trip the tested content byte-faithfully")


def test_no_backend_refuses_by_name_and_starts_no_draft():
    with tempfile.TemporaryDirectory() as td:
        bank = write_seed_bank(td)
        before = open(bank, "rb").read()
        run = run_seeding_run(bank, adapter=None)
        if not run.refused:
            fail("no adapter must refuse the run")
        if run.refusal != BACKEND_UNREACHABLE:
            fail("the refusal must be the exact backend-unreachable line: %r"
                 % run.refusal)
        if run.stages or run.drafts:
            fail("a refused run must start no draft")
        # The CLI refuses by name and every other command still works (D-10).
        r = run_cli("seed", bank, timeout=60)
        if r.returncode == 0:
            fail("seed with no backend must exit non-zero")
        if BACKEND_UNREACHABLE not in r.stdout:
            fail("the CLI must print the exact refusal line, got:\n%s"
                 % r.stdout)
        if open(bank, "rb").read() != before:
            fail("seed with no backend must never touch the bank (D-10)")
        r = run_cli("lint", bank, timeout=60)
        if r.returncode != 0:
            fail("lint must still work with no backend:\n%s\n%s"
                 % (r.stdout, r.stderr))
        r = run_cli("coverage", bank, timeout=60)
        if r.returncode != 0 or "emt:airway" not in r.stdout:
            fail("coverage must still work with no backend:\n%s" % r.stdout)


def test_import_still_works_with_no_backend():
    """D-10's import clause: `itembank import anki` runs backend-free in a
    bare temp directory (mirrors plan 03.2-01's degrade fixture)."""
    with tempfile.TemporaryDirectory() as td:
        apkg = os.path.join(td, "deck.apkg")
        build_apkg(apkg, [
            (1610000001, 11, "\x1f".join([
                "A patient with bilateral crackles and frothy sputum most "
                "likely has which condition?",
                "A) Pulmonary edema\nB) Bronchospasm\nC) Anaphylaxis\n"
                "CORRECT: A\nWHY BEST: Fluid overload produces crackles and "
                "frothy sputum."])),
        ], [(11, "Basic", json.dumps([{"name": "Front"}, {"name": "Back"}]))])
        out = os.path.join(td, "out")
        r = run_cli("import", "anki", apkg, "--out", out, timeout=60)
        if r.returncode != 0:
            fail("import with no backend exited %d:\n%s\n%s"
                 % (r.returncode, r.stdout, r.stderr))


# ---------------------------------------------------------------------------
# plan 03.2-04 Task 3: the stage-4 deterministic gate catches transcription
# and fabrication before any model critique (D-08)
# ---------------------------------------------------------------------------

SEED_CORPUS = (
    "A patent airway is the single highest priority and must be opened "
    "before oxygen is administered in every case of respiratory distress."
)
SEED_COPY_PHRASE = "A patent airway is the single highest priority"

PARA_SEED_BANK = (
    "# Seeding fixture (synthetic)\n\n"
    "## SOURCES\n\n"
    "emt:airway | corpus/ch5.txt\n\n"
    "Q1. Which finding suggests an at-risk airway?   (difficulty: recall)\n"
    "[OBJECTIVE: emt:airway]\n"
    "A) Stridor\nB) Normal breath sounds\nC) Wheezing\nD) Hiccups\n"
    "CORRECT: A\n"
    "WHY BEST: Stridor indicates upper-airway obstruction.\n"
    "CONFIDENCE: high\n")


def write_para_seed_bank(td):
    """A seeding bank whose registry locator resolves to a real corpus file
    beside it (the paraphrase source), with a bank item that carries no
    [SRC:] so a draft's unsourced state is observable in stage 4."""
    corpus = os.path.join(td, "corpus")
    os.makedirs(corpus, exist_ok=True)
    open(os.path.join(corpus, "ch5.txt"), "w",
         encoding="utf-8").write(SEED_CORPUS)
    bank = os.path.join(td, "seed_bank.md")
    open(bank, "w", encoding="utf-8").write(PARA_SEED_BANK)
    return bank


def test_stage4_retries_paraphrase_and_unsourced_drafts_before_critique():
    """Test 1: a draft failing prov.paraphrase_* or style.unsourced_specific
    is retried at stage 4 within the cap and never reaches the model critique
    stage (D-08)."""
    import model
    with tempfile.TemporaryDirectory() as td:
        bank = write_para_seed_bank(td)
        src_line = "[SRC: emt:airway corpus/ch5.txt]\n\n"
        # Leg 1: paraphrase transcription -- the first draft quotes the
        # corpus verbatim; the retried draft is clean.
        adapter = FakeModelAdapter(
            outline=FAKE_OUTLINE, stem=FAKE_STEM, options=FAKE_OPTIONS,
            rationale=src_line + FAKE_RATIONALE,
            rationale_dirty_attempts=1,
            dirty_rationale=(src_line +
                             "WHY BEST: " + SEED_COPY_PHRASE + ".\n\n"
                             "CONFIDENCE: high\n"))
        run = run_seeding_run(bank, adapter, retry_cap=3,
                              extra_checks=model.make_seeding_checks(bank))
        draft = run.drafts[0]
        if draft["attempts"] != 2:
            fail("a paraphrase-failing first draft must retry once, got "
                 "attempts=%d" % draft["attempts"])
        if any("prov.paraphrase_copy" in e for e in draft["lint_errors"]):
            fail("the retried draft must be paraphrase-clean, got %r"
                 % draft["lint_errors"])
        if adapter.verify_calls != 1:
            fail("the model critique must run once, over the clean draft "
                 "only, got %d" % adapter.verify_calls)
        # Leg 2: unsourced specific -- a dose in the draft without [SRC:]
        # is a stage-4 error, retried before critique.
        adapter2 = FakeModelAdapter(
            outline=FAKE_OUTLINE, stem=FAKE_STEM, options=FAKE_OPTIONS,
            rationale=FAKE_RATIONALE,
            rationale_dirty_attempts=1,
            dirty_rationale=("WHY BEST: The correct dose is 0.5 mg.\n\n"
                             "CONFIDENCE: high\n"))
        run2 = run_seeding_run(bank, adapter2, retry_cap=3,
                               extra_checks=model.make_seeding_checks(bank))
        draft2 = run2.drafts[0]
        if draft2["attempts"] != 2:
            fail("an unsourced-specific first draft must retry once, got "
                 "attempts=%d" % draft2["attempts"])
        if any("style.unsourced_specific" in e for e in draft2["lint_errors"]):
            fail("the retried draft must be unsourced-clean, got %r"
                 % draft2["lint_errors"])
        if adapter2.verify_calls != 1:
            fail("leg 2: the model critique must run once over the clean "
                 "draft, got %d" % adapter2.verify_calls)


def test_stage4_gate_deterministic_and_headless():
    """Test 2: the stage-4 gate is deterministic and headless -- a draft that
    always fails the deterministic checks is capped out with zero model calls,
    and two identical runs produce identical failures (no model involved)."""
    import model
    with tempfile.TemporaryDirectory() as td:
        bank = write_para_seed_bank(td)
        src_line = "[SRC: emt:airway corpus/ch5.txt]\n\n"

        def run_once():
            adapter = FakeModelAdapter(
                outline=FAKE_OUTLINE, stem=FAKE_STEM, options=FAKE_OPTIONS,
                rationale=src_line + "WHY BEST: " + SEED_COPY_PHRASE + ".\n\n"
                           "CONFIDENCE: high\n",
                rationale_dirty_attempts=0)
            r = run_seeding_run(bank, adapter, retry_cap=2,
                                extra_checks=model.make_seeding_checks(bank))
            return r, adapter

        r1, a1 = run_once()
        r2, a2 = run_once()
        if r1.drafts or len(r1.failed_drafts) != 1:
            fail("a permanently-failing draft must be capped out, not "
                 "presented: %r" % r1.drafts)
        if r1.failed_drafts[0]["attempts"] != 2:
            fail("the retry cap must bound a permanently-failing draft")
        joined = " ".join(r1.failed_drafts[0]["lint_errors"])
        if "prov.paraphrase_copy" not in joined:
            fail("the failed draft must record its deterministic errors: %r"
                 % joined)
        if a1.verify_calls != 0 or a2.verify_calls != 0:
            fail("the deterministic gate must never call the model, got "
                 "verify calls %d/%d" % (a1.verify_calls, a2.verify_calls))
        if r1.failed_drafts[0]["lint_errors"] != \
                r2.failed_drafts[0]["lint_errors"]:
            fail("two identical runs must fail identically: %r != %r"
                 % (r1.failed_drafts[0]["lint_errors"],
                    r2.failed_drafts[0]["lint_errors"]))
        if r1.failed_drafts[0]["block"] != r2.failed_drafts[0]["block"]:
            fail("the assembled draft blocks must be byte-identical across "
                 "runs")


def build_apkg(path, notes, notetypes):
    """A synthetic legacy .apkg (plain SQLite collection.anki21 member) --
    stdlib sqlite3 + zipfile only, never real user data."""
    db = path + ".db"
    conn = sqlite3.connect(db)
    try:
        conn.execute("CREATE TABLE notetypes (id INTEGER PRIMARY KEY, name TEXT, "
                     "mtime_secs INTEGER, usn INTEGER, config TEXT, fields TEXT, "
                     "tmpls TEXT, latex TEXT, latexsvg TEXT, req TEXT, sortf INTEGER, "
                     "did INTEGER, vers INTEGER, tags TEXT)")
        conn.execute("CREATE TABLE notes (id INTEGER PRIMARY KEY, guid TEXT, mid INTEGER, "
                     "mod INTEGER, usn INTEGER, tags TEXT, flds TEXT, sfld TEXT, "
                     "csum INTEGER, flags INTEGER, data TEXT)")
        for nid, name, fields in notetypes:
            conn.execute("INSERT INTO notetypes (id, name, mtime_secs, usn, config, "
                         "fields, tmpls, latex, latexsvg, req, sortf, did, vers, tags) "
                         "VALUES (?,?,0,0,'',?,'','','','',0,0,0,'')",
                         (nid, name, fields))
        for nid, mid, flds in notes:
            conn.execute("INSERT INTO notes (id, guid, mid, mod, usn, tags, flds, sfld, "
                         "csum, flags, data) VALUES (?,?,?,0,0,?,?,'',0,0,'')",
                         (nid, "guid-%d" % nid, mid, "", flds))
        conn.commit()
    finally:
        conn.close()
    with open(db, "rb") as fh:
        raw = fh.read()
    os.remove(db)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("collection.anki21", raw)
        zf.writestr("media", "{}")


def test_d19_item_and_prose_writes_never_contend_one_file():
    """D-19 (R5): in the two-file layout -- items in the bank file, prose in
    an external [LESSON-SRC:] file -- an item write (seeding accept) and a
    prose write (the lesson render, the style pass's output side) target
    different files in one pass: no single file receives both kinds of write,
    and neither write touches the other's file (T-032-17)."""
    from surfaces import lesson as lesson_surface
    with tempfile.TemporaryDirectory() as td:
        bank = os.path.join(td, "bank.md")
        prose = os.path.join(td, "lesson.md")
        open(prose, "w", encoding="utf-8").write(
            "# Shared lesson\n\n## LESSON\n\n### Section One\n\nThe airway "
            "stays open when the head is tilted and the chin is lifted.")
        open(bank, "w", encoding="utf-8").write(
            "# Two-file layout (synthetic)\n\n[LESSON-SRC: lesson.md]\n\n"
            "## SOURCES\n\n" + REGISTRY + "\n" + AIRWAY_ITEM)
        bank_before = open(bank, "rb").read()
        prose_before = open(prose, "rb").read()

        # Item write: the seeding accept appends an item to the bank file.
        adapter = FakeModelAdapter(outline=FAKE_OUTLINE, stem=FAKE_STEM,
                                   options=FAKE_OPTIONS,
                                   rationale=FAKE_RATIONALE)
        run = run_seeding_run(bank, adapter)
        result = seeding.accept_candidate(bank, run.drafts[0]["candidate"])
        if not result.get("accepted"):
            fail("D-19: the item write must accept, got %r" % result)
        bank_after_item = open(bank, "rb").read()
        if bank_after_item == bank_before:
            fail("D-19: the item write must change the bank file")
        if open(prose, "rb").read() != prose_before:
            fail("D-19: the item write must not touch the prose file")

        # Prose write: the lesson render writes prose to the prose file.
        ns = types.SimpleNamespace(bank=bank, out=prose, ref=None)
        if lesson_surface.cmd_lesson(ns) != 0:
            fail("D-19: the prose write must succeed")
        if open(prose, "rb").read() == prose_before:
            fail("D-19: the prose write must change the prose file")
        if open(bank, "rb").read() != bank_after_item:
            fail("D-19: the prose write must not touch the bank file")

        # The two writes resolved to two different files: no single file
        # received both an item write and a prose write in one pass.
        if os.path.abspath(bank) == os.path.abspath(prose):
            fail("D-19: item and prose writes must target different files")


def main():
    tests = [v for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    for t in tests:
        t()
    print("seeding_roundtrip: %d tests passed" % len(tests))
    return 0


if __name__ == "__main__":
    sys.exit(main())
