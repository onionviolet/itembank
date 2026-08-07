"""The quiz surfaces: a static file to drill against, and a graded sitting.

`build` writes a page with no process behind it, so it carries the answer key
and saves nothing. `serve` puts the same page behind a loopback server that
scores every response and writes the attempt file, so the browser never holds an
answer. Both are clients of the runtime.
"""
import collections, html, json, os, sys, uuid

import evidence
import server
from model import grab, lint, load
from runtime import explain_payload, page_item, score_response
from surfaces.quiz_page import TEMPLATE
from surfaces.theme import THEME_CSS


def page_for(bank_path, qs, serve=False, reveal=False, post_path="/answer"):
    text = open(bank_path, encoding="utf-8").read()
    title = grab(r"(?m)^#\s+(.*?)\s*$", text) or os.path.basename(bank_path)
    counts = collections.Counter(q["type"] for q in qs)
    mix = ", ".join("%d %s" % (v, k) for k, v in counts.most_common())
    sub = "%d items &middot; %s &middot; dichotomous scoring" % (len(qs), mix)
    sub += " &middot; answers recorded" if serve else " &middot; nothing recorded"
    items = [page_item(q, reveal=reveal, offline=not serve) for q in qs]
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
    """Run the quiz against a local process so every answer is written to disk.

    The static `build` page is sandboxed by the browser and cannot write a file,
    which is why answers used to evaporate when the tab closed. A loopback
    server is the smallest thing that fixes it without adding a dependency.

    It also does the scoring. The page is sent items with the key stripped, and
    POSTs each response here; this process calls the one scorer, records the
    result, and returns the verdict with the explanation. So a sitting that is
    meant to count is one where the browser never held the answers.

    Persistence is `evidence.append_event()`, the same one writer every other
    surface uses (D-08) -- this is the last surface that used to write its own
    store instead. The attempt file is `evidence.render_attempt_md()`'s output,
    written atomically; it is a view over `_evidence/evidence.jsonl`, never a
    second place a response is recorded, and it is rebuilt in full after every
    answer rather than accumulated in memory, so a sitting interrupted mid-write
    never leaves a half-written file.
    """
    import webbrowser, threading
    from datetime import datetime

    qs = load(a.bank)
    errors, _ = lint(qs)
    if errors and not a.force:
        for e in errors:
            print("error  " + str(e))
        sys.exit("refusing to serve a bank with errors; fix them or pass --force")

    out = a.out or os.path.join(
        os.path.dirname(os.path.abspath(a.bank)) or ".", "_attempts",
        "%s_attempt_%s.md" % (os.path.splitext(os.path.basename(a.bank))[0],
                              datetime.now().strftime("%Y-%m-%d_%H%M")))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    _, page = page_for(a.bank, qs, serve=True, reveal=a.reveal)
    page_bytes = page.encode("utf-8")
    by_id = dict((q["id"], q) for q in qs)

    # One id per sitting, printed here so a marker can pass it to
    # `itembank mark`/`itembank render attempt` later -- the evidence log,
    # not this process's memory, is what a marker or a crash-recovered
    # attempt file is read back out of.
    session_id = uuid.uuid4().hex
    log = evidence.log_path(os.path.dirname(os.path.abspath(a.bank)) or ".")
    state = {"writes": 0}

    def record(q, response, elapsed_ms):
        # `record_answer` is the one function both this CLI path and the
        # daemon call (D-08 continued); the log's byte size before/after is
        # how this closure alone still tells a genuinely new answer from a
        # replayed one, without record_answer needing to report anything
        # beyond the score it was asked to return.
        size_before = os.path.getsize(log) if os.path.exists(log) else -1
        score = record_answer(a.bank, qs, session_id, log, out, a.mode, q, response, elapsed_ms)
        already = size_before >= 0 and os.path.getsize(log) == size_before
        state["writes"] += 1

        answered = len(set(ev["item_ref"] for ev in evidence.session_events(log, session_id)))
        note = " (already recorded)" if already else ""
        sys.stdout.write("\r  %d/%d answered, saved%s" % (answered, len(qs), note))
        sys.stdout.flush()
        if answered >= len(qs):
            print("\n  finished. Attempt file: %s" % out)
        return score

    class H(server.Handler):
        def do_GET(self):
            if self.path not in ("/", "/index.html"):
                self.send_error(404)
                return
            self.send_html(page_bytes)

        def do_POST(self):
            if self.path != "/answer":
                self.send_error(404)
                return
            try:
                data = self.read_json()
                q = by_id.get(data.get("id"))
                if q is None:
                    self.send_error(404, "no item %r in this bank" % data.get("id"))
                    return
                elapsed_ms = data.get("elapsed_ms")
                if not isinstance(elapsed_ms, int) or isinstance(elapsed_ms, bool):
                    # Absent, non-integer, or an older cached page that never
                    # sent the field at all: record an honest null rather
                    # than a fabricated number.
                    elapsed_ms = None
                payload = {"item_id": q["id"],
                           "score": record(q, data.get("response"), elapsed_ms),
                           "explain": explain_payload(q, a.reveal)}
            except Exception as exc:                # never let a bad POST kill a sitting
                self.send_error(500, str(exc))
                return
            self.send_json(payload)

    print("itembank serve")
    srv = server.bind(H, a.port)

    with srv:
        url = "http://127.0.0.1:%d/" % srv.server_address[1]
        print("  session %s" % session_id)
        print("  bank    %s (%d items)" % (a.bank, len(qs)))
        print("  attempt %s" % out)
        print("  url     %s" % url)
        print("  Answers are written as you give them. Ctrl-C when you are done.")
        sys.stdout.flush()
        if not a.no_open:
            threading.Timer(0.4, lambda: webbrowser.open(url)).start()
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped. %d save(s) written to %s"
                  % (state["writes"], out if state["writes"] else "nothing yet"))
    return 0
