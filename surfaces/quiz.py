"""The quiz surfaces: a static file to drill against, and a graded sitting.

`build` writes a page with no process behind it, so it carries the answer key
and saves nothing. `serve` puts the same page behind a loopback server that
scores every response and writes the attempt file, so the browser never holds an
answer. Both are clients of the runtime.
"""
import collections, html, json, os, sys, uuid

import evidence
from model import grab, lint, load, parse_lesson
from runtime import page_item, score_response
from surfaces.quiz_page import TEMPLATE
from surfaces.theme import THEME_CSS


def page_for(bank_path, qs, serve=False, reveal=False, post_path="/answer",
             lesson_base=""):
    text = open(bank_path, encoding="utf-8").read()
    title = grab(r"(?m)^#\s+(.*?)\s*$", text) or os.path.basename(bank_path)
    counts = collections.Counter(q["type"] for q in qs)
    mix = ", ".join("%d %s" % (v, k) for k, v in counts.most_common())
    sub = "%d items &middot; %s &middot; dichotomous scoring" % (len(qs), mix)
    sub += " &middot; answers recorded" if serve else " &middot; nothing recorded"
    items = [page_item(q, reveal=reveal, offline=not serve) for q in qs]
    # The chip label is the locked string, but it only ships when a reader
    # actually sits behind this page (D-12): a static file:// page has no
    # daemon at /lesson/<stem> to link to, so the label is substituted away
    # and the chip never renders.
    lesson_label = "Read the lesson" if lesson_base else ""
    # `post_path` lets one process serve more than one bank -- each bank's
    # page posts an answer back to its own bank-scoped path instead of a
    # single hardcoded "/answer", which was correct only while exactly one
    # bank was served per process. The default keeps `cmd_build`'s static
    # page and `cmd_serve`'s single-bank page byte-compatible.
    # __DATA__ goes in last so that bank text which happens to contain another
    # placeholder is never itself substituted.
    return mix, (TEMPLATE
                 .replace("__THEME__", THEME_CSS)
                 .replace("__SERVE__", "true" if serve else "false")
                 .replace("__TITLE__", html.escape(title))
                 .replace("__SUB__", sub)
                 .replace("__POST__", post_path)
                 .replace("__LESSON_BASE__", lesson_base)
                 .replace("__LESSON_LABEL__", lesson_label)
                 .replace("__DATA__", json.dumps(items, ensure_ascii=False)))


def record_answer(bank_path, qs, session_id, log, out_path, mode, q, response, elapsed_ms):
    """Score one response, append it to the evidence log, and re-render the
    attempt file atomically. The one function `cmd_serve` and
    `surfaces/daemon.py` both call, so the CLI path and the daemon path can
    never diverge in how a response is scored or recorded -- one scorer
    (`runtime.score_response`) and one writer (`evidence.append_event`),
    reached through exactly one place (D-08 continued).
    """
    score = score_response(q, response)
    item_key = evidence.evidence_key(q)
    canon = evidence.idempotency_canon(q, response)
    attempt_num = evidence.attempt_number(log, session_id, item_key, canon)
    event = evidence.response_event(
        session_id, q, response, score, mode, attempt_num,
        os.path.basename(bank_path), response_time_ms=elapsed_ms, confidence=None)
    evidence.append_event(log, event)

    # Regenerate the whole attempt file from the log, atomically -- the
    # render is the only generator of this document (D-11); a sitting
    # killed mid-write must never leave a half-written attempt file.
    md = evidence.render_attempt_md(log, session_id, qs, bank_path)
    tmp = out_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(md)
    os.replace(tmp, out_path)
    return score


def cmd_build(a):
    qs = load(a.bank)
    # build/study/export keep calling lint(qs) with one argument: none of them
    # renders a lesson link, so the lesson checks stay off there -- the static
    # page omits the chip entirely by D-12, and turning the checks on would
    # refuse a bank over a link that surface never shows.
    errors, _ = lint(qs)
    if errors and not a.force:
        for e in errors:
            print("error  " + str(e))
        sys.exit("refusing to build a bank with errors; fix them or pass --force")
    out = a.out or os.path.splitext(a.bank)[0] + "_quiz.html"
    if os.path.dirname(out):
        os.makedirs(os.path.dirname(out), exist_ok=True)
    # A file:// page cannot write anywhere and has no process to ask, so `build`
    # records nothing and is the one surface that carries the answer key to the
    # client. It stays the shareable, no-process mode; `serve` is the graded one.
    mix, page = page_for(a.bank, qs, serve=False, reveal=not a.blind)
    open(out, "w", encoding="utf-8").write(page)
    print("%d items -> %s" % (len(qs), out))
    print("   mix: " + mix)
    if any(q["type"] == "short" for q in qs):
        print("   note: short answers cannot be saved by a file:// page. "
              "Use `itembank serve` if this sitting is meant to be graded.")
    return 0


def cmd_serve(a):
    """Sit the quiz against the daemon, scoped to this one bank, so every
    answer is written to disk.

    The static `build` page is sandboxed by the browser and cannot write a
    file, which is why answers used to evaporate when the tab closed. This
    command still owns every one of its own responsibilities -- loading and
    linting the bank, defaulting the attempt path, minting one session id,
    printing its banner -- but it no longer binds its own socket to do it.
    `surfaces/daemon.py` is the only module in the codebase that defines an
    HTTP request handler; this command launches that daemon scoped to one
    bank instead of duplicating its route table (SURF-01's consolidation,
    finished).

    Persistence is `evidence.append_event()`, the same one writer every other
    surface uses (D-08), reached by way of `quiz.record_answer()` -- the CLI
    path and the daemon path score and record through exactly the same
    function, never a second copy of either.
    """
    from datetime import datetime
    from surfaces.daemon import serve_scoped

    qs = load(a.bank)
    # The same lesson-supplied gate cmd_lint applies: a bank whose lesson
    # reference names a missing heading is refused before a learner sees a
    # chip pointing at an anchor that does not exist (ROADMAP SC3).
    errors, _ = lint(qs, lesson=parse_lesson(a.bank))
    if errors and not a.force:
        for e in errors:
            print("error  " + str(e))
        sys.exit("refusing to serve a bank with errors; fix them or pass --force")

    out = a.out or os.path.join(
        os.path.dirname(os.path.abspath(a.bank)) or ".", "_attempts",
        "%s_attempt_%s.md" % (os.path.splitext(os.path.basename(a.bank))[0],
                              datetime.now().strftime("%Y-%m-%d_%H%M")))
    os.makedirs(os.path.dirname(out), exist_ok=True)

    # One id per sitting, printed here so a marker can pass it to
    # `itembank mark`/`itembank render attempt` later -- the evidence log,
    # not this process's memory, is what a marker or a crash-recovered
    # attempt file is read back out of.
    session_id = uuid.uuid4().hex
    log = evidence.log_path(os.path.dirname(os.path.abspath(a.bank)) or ".")
    stem = os.path.splitext(os.path.basename(a.bank))[0]

    print("itembank serve")
    print("  session %s" % session_id)
    print("  bank    %s (%d items)" % (a.bank, len(qs)))
    print("  attempt %s" % out)

    def on_bound(port):
        print("  Answers are written as you give them. Ctrl-C when you are done.")

    serve_scoped(
        os.path.dirname(os.path.abspath(a.bank)) or ".",
        {stem: os.path.abspath(a.bank)}, {}, a.port,
        open_path="/quiz/%s" % stem, no_open=a.no_open, on_bound=on_bound,
        extra={"sessions": {stem: {
            "session_id": session_id, "log": log, "out": out, "mode": a.mode,
            "reveal": a.reveal, "progress": True,
        }}})
    return 0
