"""The quiz surfaces: a static file to drill against, and a graded sitting.

`build` writes a page with no process behind it, so it carries the answer key
and saves nothing. `serve` puts the same page behind a loopback server that
scores every response and writes the attempt file, so the browser never holds an
answer. Both are clients of the runtime.
"""
import collections, html, json, os, sys, uuid

import evidence
from model import HONEST_LIMITS_NOTE, grab, lint, load, parse_lesson
from runtime import INTERACTION_VERSION, page_item, score_response
from surfaces.session import run_check_source
from surfaces import presentation, settings
from surfaces.quiz_page import (AGENT_ASSIST_HTML, ASSIST_JS, OFFLINE_JS,
                                SERVED_JS, TEMPLATE)
from surfaces.theme import THEME_CSS, theme_css

# The vendored CodeMirror 6 bundle (plan 05-05 Task 2, ruling 5/11 + the
# Directive 4a supply-chain rule). It is embedded into the page only when the
# bank actually contains a check item, so every non-check bank's rendered page
# stays byte-identical to before this phase. The record of version, SHA-256
# and license review lives beside the file in assets/vendor/codemirror/.
_CM6_BUNDLE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets", "vendor", "codemirror", "codemirror.bundle.js")
_CM6_BOOT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets", "vendor", "codemirror", "check-editor-boot.js")
_CM6_BUNDLE_CACHE = None
_CM6_BOOT_CACHE = None


def _cm6_bundle():
    global _CM6_BUNDLE_CACHE
    if _CM6_BUNDLE_CACHE is None:
        with open(_CM6_BUNDLE_PATH, encoding="utf-8") as fh:
            _CM6_BUNDLE_CACHE = fh.read()
    return _CM6_BUNDLE_CACHE


def _cm6_boot():
    global _CM6_BOOT_CACHE
    if _CM6_BOOT_CACHE is None:
        with open(_CM6_BOOT_PATH, encoding="utf-8") as fh:
            _CM6_BOOT_CACHE = fh.read()
    return _CM6_BOOT_CACHE


def _resolve_check_item(qs, check_id):
    """The one check-item resolution shared by the daemon routes and the
    CLI twins (D-01): by positional id or opaque [ID:]."""
    for q in qs:
        if q["id"] == check_id or q.get("item_id") == check_id:
            return q
    return None


def record_gate_check(bank_path, check_id, answer, mode="practice",
                      session_id="reader"):
    """The one gate-check recording path shared by the daemon route and the
    CLI twin (SURF-04): resolves the check item, scores through
    `runtime.score_response()` (the one verdict path), and records ordinary
    response evidence with context="lesson_gate" (D-08) -- a lesson-gate
    attempt is the same object as a quiz attempt to every consumer.
    Returns None when the check id names no item."""
    qs = load(bank_path)
    q = _resolve_check_item(qs, check_id)
    if q is None:
        return None
    score = score_response(q, answer)
    bank_dir = os.path.dirname(os.path.abspath(bank_path)) or "."
    log = evidence.log_path(bank_dir)
    canon = evidence.idempotency_canon(q, answer)
    key = evidence.evidence_key(q)
    attempt = evidence.attempt_number(log, session_id, key, canon)
    event = evidence.response_event(
        session_id=session_id, q=q,
        answer=(json.dumps(answer, ensure_ascii=False)
                if isinstance(answer, (dict, list)) else answer),
        score=score, mode=mode, attempt_num=attempt,
        bank=os.path.basename(bank_path), context="lesson_gate")
    evidence.append_event(log, event)
    return score


def record_gate_skip(bank_path, check_id, mode="practice", session_id="reader"):
    """The one gate_skip recording path shared by the daemon route and the
    CLI twin (SURF-04): resolves the check and appends exactly one
    gate_skip event through the one evidence writer (D-07). Returns None
    when the check id names no item; returns "off" when the lesson declares
    [GATE: off] and therefore offers no skip."""
    qs = load(bank_path)
    q = _resolve_check_item(qs, check_id)
    if q is None:
        return None
    les = parse_lesson(bank_path)
    as_authored = (les or {}).get("gate") or "recommended"
    if as_authored == "off":
        return "off"
    bank_dir = os.path.dirname(os.path.abspath(bank_path)) or "."
    event = evidence.gate_skip_event(
        session_id=session_id, bank=os.path.basename(bank_path),
        lesson_slug=os.path.splitext(os.path.basename(bank_path))[0],
        check_item_id=check_id, check_item_ref=q["id"],
        objective=q.get("objective", ""), gate_mode=as_authored)
    evidence.append_event(evidence.log_path(bank_dir), event)
    return "Read ahead recorded. This check stays open."


def cmd_lesson_check(a):
    """The CLI twin of `POST /lesson/<stem>/check` (SURF-04): scores the
    check item's answer through the one scorer and records response
    evidence with context="lesson_gate"; prints the verdict. An unknown
    check id exits non-zero, matching the route's 404."""
    try:
        answer = json.loads(a.answer) if a.answer.strip() else ""
    except (ValueError, TypeError):
        answer = a.answer
    score = record_gate_check(a.bank, a.check, answer)
    if score is None:
        sys.exit("no item matching check id %r in %s" % (a.check, a.bank))
    print("recorded score=%s" % ("null" if score is None else
                                 ("correct" if score else "not correct")))
    return 0


def cmd_lesson_skip(a):
    """The CLI twin of `POST /lesson/<stem>/skip` (SURF-04): records
    exactly one gate_skip event and prints the status string; an unknown
    check id exits non-zero (the route's 404), and an [GATE: off] lesson
    refuses the skip."""
    status = record_gate_skip(a.bank, a.check)
    if status is None:
        sys.exit("no item matching check id %r in %s" % (a.check, a.bank))
    if status == "off":
        sys.exit("this lesson declares [GATE: off] and offers no skip")
    print(status)
    return 0


def page_for(bank_path, qs, serve=False, reveal=False, post_path="/answer",
             lesson_base="", lesson_slugs=None, bank_stem=None, mode=None,
             theme_css=None, lti_framing="", boot_extra=None, assist=False,
             home_href=""):
    """Render one quiz page. `theme_css`, when given, is the per-render
    generated token block (the daemon passes
    `theme.theme_css(load_settings(root))` so quiz shares the one palette
    with index/report/settings -- plan 04-04 Task 2); when omitted the
    module's THEME_CSS constant keeps every existing caller byte-identical.

    `lti_framing` (phase 999.4) is an optional HTML snippet rendered above
    the first item -- the LTI embedded player's privacy line -- and
    `boot_extra` (phase 999.4) is an optional dict merged into the served
    page's BOOT metadata (the LTI player's objective). Both default to empty
    so every existing caller renders byte-identically.

    `assist`, when true and the page is served, threads the plan 08-05
    AgentAssist payload (AGENT_ASSIST_HTML + ASSIST_JS) into the assist slot
    -- the daemon is the only caller that sets it, so build/offline mode
    ships no assist at all.
    """
    text = open(bank_path, encoding="utf-8").read()
    title = grab(r"(?m)^#\s+(.*?)\s*$", text) or os.path.basename(bank_path)
    counts = collections.Counter(q["type"] for q in qs)
    mix = ", ".join("%d %s" % (v, k) for k, v in counts.most_common())
    sub = "%d items &middot; %s &middot; dichotomous scoring" % (len(qs), mix)
    sub += " &middot; answers recorded" if serve else " &middot; nothing recorded"
    # The way back. Weibao sat the 13.9 skeleton on 2026-08-21 and reported
    # "no way to go back to home page". The home existed the whole time: serve
    # and daemon are the same server (cmd_serve calls daemon.serve_scoped),
    # and both answer GET /. The page just never linked to it.
    #
    # Off by default so every existing caller stays byte-identical, and
    # because two callers genuinely have no home to offer: the offline build
    # output has no server at all, and an LTI launch is framed inside the
    # host LMS, where a link to itembank's own index would walk the learner
    # out of the course they launched from.
    ctx_bank = html.escape(title)
    if home_href:
        ctx_bank = ('<a class="cx-home" href="%s">%s</a>'
                    % (html.escape(home_href), ctx_bank))
    ctx_mode = html.escape(mode or "")
    # Served mode (SURF-02): the page receives bootstrap metadata only --
    # allowlisted bank stem, item count, configured session mode, and the
    # resolving lesson-slug set -- plus an empty item array. The browser
    # starts the sitting through POST /api/start and submits through
    # POST /api/submit, so no key, explanation or full bank item array ever
    # reaches the served source. The offline client script is substituted
    # away entirely (plan 04-01 Test 5).
    if serve:
        items = []
        boot = {"bank": bank_stem or "", "count": len(qs), "mode": mode or "",
                "lesson_slugs": sorted(lesson_slugs) if lesson_slugs else []}
        if boot_extra:
            boot.update(boot_extra)
    else:
        # The static `build` compatibility path: the full Python-produced
        # item array with canonical keys and explanations, and the offline
        # canonical-key comparison client. When the caller knows which lesson
        # headings actually resolve (from parse_lesson), blank the slug of any
        # item whose LESSON-REF does not resolve -- the D-12 chip rule for the
        # one surface with no daemon behind it.
        items = []
        for q in qs:
            it = page_item(q, reveal=reveal, offline=True)
            if it.get("lesson_slug") and lesson_slugs is not None \
                    and it["lesson_slug"] not in lesson_slugs:
                it["lesson_slug"] = ""
            items.append(it)
        boot = {}
    # The chip label is the locked string, but it only ships when a reader
    # actually sits behind this page (D-12): a static file:// page has no
    # daemon at /lesson/<stem> to link to, so the label is substituted away
    # and the chip never renders.
    lesson_label = "Read the lesson" if lesson_base else ""
    # The chip base/label live inside the two client scripts (quiz_page.py),
    # not in the shared shell, so the substitutions must target the JS strings
    # themselves before they are inserted into the template. Same for the
    # honest-limits sentence: asCheck renders a __HONEST_LIMITS__ placeholder
    # inside the client script, substituted here from the one constant SPEC
    # reads (D-10) -- the page and the format contract cannot drift.
    offline_js = (OFFLINE_JS
                  .replace("__LESSON_BASE__", lesson_base)
                  .replace("__LESSON_LABEL__", lesson_label)
                  .replace("__HONEST_LIMITS__", HONEST_LIMITS_NOTE))
    served_js = (SERVED_JS
                 .replace("__LESSON_BASE__", lesson_base)
                 .replace("__LESSON_LABEL__", lesson_label)
                 .replace("__HONEST_LIMITS__", HONEST_LIMITS_NOTE))
    # __DATA__/__BOOT__ go in last so that bank text which happens to contain
    # another placeholder is never itself substituted. __CM6_TAG__ and
    # __HONEST_LIMITS__ are substituted before that, alongside the other
    # fixed copy: the CM6 bundle embeds only when the bank has a check item
    # (a non-check bank's page stays byte-identical), and the honest-limits
    # sentence comes from the one constant SPEC reads (D-10).
    has_check = any(q.get("type") == "check" for q in qs)
    cm6 = ("<script id=\"cm6\">" + _cm6_bundle() + "</script>"
           if has_check else "")
    cm6_boot_html = ("<script id=\"cm6-boot\">" + _cm6_boot() + "</script>"
                     if has_check else "")
    assist_html = AGENT_ASSIST_HTML if (serve and assist) else ""
    assist_js = ASSIST_JS if (serve and assist) else ""
    # __THEME__ then __SHARED__ then the page's own layer, in that order and
    # not another: the generated palette, then presentation.SHARED_CSS (the
    # token layer holding the four vendored @font-face rules and the
    # spacing/radius/voice/measure :root block), then quiz_page's own rules,
    # which still win on equal specificity. Substituting __THEME__ alone --
    # everything this call did before 14-01 -- is DEFECT D-B.
    return mix, (TEMPLATE
                 .replace("__THEME__", THEME_CSS if theme_css is None
                          else theme_css)
                 .replace("__SHARED__", presentation.SHARED_CSS)
                 .replace("__SERVE__", "true" if serve else "false")
                 .replace("__TITLE__", html.escape(title))
                 .replace("__SUB__", sub)
                 .replace("__CTX_BANK__", ctx_bank)
                 .replace("__CTX_MODE__", ctx_mode)
                 .replace("__LTI_FRAMING__", lti_framing or "")
                 .replace("__HONEST_LIMITS__", HONEST_LIMITS_NOTE)
                 .replace("__CM6_TAG__", cm6)
                 .replace("__CM6_BOOT__", cm6_boot_html)
                 .replace("__ASSIST__", assist_html)
                 .replace("__ASSIST_JS__", assist_js)
                 .replace("__OFFLINE_JS__", "" if serve else offline_js)
                 .replace("__SERVED_JS__", served_js if serve else "")
                 .replace("__BOOT__", presentation.script_safe_json(boot))
                 .replace("__DATA__", presentation.script_safe_json(items)))


def record_answer(bank_path, qs, session_id, log, out_path, mode, q, response, elapsed_ms):
    """Score one response, append it to the evidence log, and re-render the
    attempt file atomically. The one function `cmd_serve` and
    `surfaces/daemon.py` both call, so the CLI path and the daemon path can
    never diverge in how a response is scored or recorded -- one scorer
    (`runtime.score_response`) and one writer (`evidence.append_event`),
    reached through exactly one place (D-08 continued).

    A `check` item is the one type whose answer is not what the scorer
    receives: the runner executes the submitted source once per authored case
    (plan 05-01, D-01 -- the scorer never runs code), the per-case pass flags
    reduce to a vector, and that vector is what score_response sees. The raw
    source is preserved on the evidence event as check_source. A run the
    deadline killed scores None and records error_category "timeout", never a
    fabricated dichotomous verdict (criterion 12).
    """
    run_result = None
    check_source = None
    if q["type"] == "check":
        check_source = response
        base = os.path.dirname(os.path.abspath(bank_path)) or "."
        run_result, answer, score = run_check_source(q, response, base)
    else:
        answer = response
        score = score_response(q, response)
    killed = bool(run_result) and any(c.get("timed_out") for c in run_result)
    item_key = evidence.evidence_key(q)
    canon = evidence.idempotency_canon(q, answer)
    attempt_num = evidence.attempt_number(log, session_id, item_key, canon)
    event = evidence.response_event(
        session_id, q, answer, score, mode, attempt_num,
        os.path.basename(bank_path), response_time_ms=elapsed_ms, confidence=None,
        check_source=check_source,
        interaction_version=INTERACTION_VERSION if q["type"] == "check" else None,
        error_category="timeout" if killed else None)
    evidence.append_event(log, event)

    # Regenerate the whole attempt file from the log, atomically -- the
    # render is the only generator of this document (D-11); a sitting
    # killed mid-write must never leave a half-written attempt file.
    md = evidence.render_attempt_md(log, session_id, qs, bank_path)
    tmp = out_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(md)
    os.replace(tmp, out_path)
    # The per-case run result rides along so the caller can build an explain
    # payload from the one run that produced the score (05-05 Task 1); it is
    # None for every non-check type, and the score is unchanged.
    return (score, run_result)


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
    # The static page reads settings beside the bank and uses the same
    # generator as every served surface (plan 04-04 Task 2 Test 3): a
    # missing settings file falls back to schema defaults, so the offline
    # build stays byte-compatible for banks with no itembank.json.
    base = os.path.dirname(os.path.abspath(a.bank)) or "."
    cfg = settings.load_settings(base)
    css = theme_css(cfg)
    # A file:// page cannot write anywhere and has no process to ask, so `build`
    # records nothing and is the one surface that carries the answer key to the
    # client. It stays the shareable, no-process mode; `serve` is the graded one.
    mix, page = page_for(a.bank, qs, serve=False, reveal=not a.blind,
                         theme_css=css)
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
