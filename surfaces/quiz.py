"""The quiz surfaces: a static file to drill against, and a graded sitting.

`build` writes a page with no process behind it, so it carries the answer key
and saves nothing. `serve` puts the same page behind a loopback server that
scores every response and writes the attempt file, so the browser never holds an
answer. Both are clients of the runtime.
"""
import collections, html, json, os, sys

import server
from model import grab, lint, load
from runtime import explain_payload, page_item, response_text, score_response
from surfaces.quiz_page import TEMPLATE
from surfaces.theme import THEME_CSS


def page_for(bank_path, qs, serve=False, reveal=False):
    text = open(bank_path, encoding="utf-8").read()
    title = grab(r"(?m)^#\s+(.*?)\s*$", text) or os.path.basename(bank_path)
    counts = collections.Counter(q["type"] for q in qs)
    mix = ", ".join("%d %s" % (v, k) for k, v in counts.most_common())
    sub = "%d items &middot; %s &middot; dichotomous scoring" % (len(qs), mix)
    sub += " &middot; answers recorded" if serve else " &middot; nothing recorded"
    items = [page_item(q, reveal=reveal, offline=not serve) for q in qs]
    # __DATA__ goes in last so that bank text which happens to contain another
    # placeholder is never itself substituted.
    return mix, (TEMPLATE
                 .replace("__THEME__", THEME_CSS)
                 .replace("__SERVE__", "true" if serve else "false")
                 .replace("__TITLE__", html.escape(title))
                 .replace("__SUB__", sub)
                 .replace("__DATA__", json.dumps(items, ensure_ascii=False)))


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


# ---- attempt file -----------------------------------------------------------
# One markdown file per sitting, rewritten in full on every answer. Markdown
# rather than JSON because the reader is a human or an LLM, both of which read
# prose better than they read a data structure, and because it lands in a vault
# next to the notes it feeds.

def attempt_markdown(bank_path, answers, done):
    from datetime import datetime
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    body = list(answers)
    auto = [a for a in body if a.get("correct") is not None]
    right = [a for a in auto if a["correct"]]
    shorts = [a for a in body if a.get("type") == "short"]
    L = []
    L.append("# Attempt: %s" % os.path.basename(bank_path))
    L.append("")
    L.append("*Written by `itembank serve`. Bank: `%s`. Started %s.*" % (bank_path, stamp))
    L.append("")
    L.append("**Status:** %s. %d auto-marked, %d correct. %d short answer(s) awaiting a marker."
             % ("finished" if done else "IN PROGRESS, file may be partial",
                len(auto), len(right), len(shorts)))
    L.append("")
    L.append("**To grade this:** see `GRADING.md` in the itembank repo. Mark each short answer "
             "against its rubric, write the verdict into the `MARK:` line, and leave the "
             "answer text exactly as written.")
    L.append("")
    for a in body:
        L.append("---")
        L.append("")
        head = "## Item %d, %s" % (a.get("n", 0), a.get("type", "?"))
        if a.get("correct") is True:
            head += "  [auto: correct]"
        elif a.get("correct") is False:
            head += "  [auto: WRONG]"
        L.append(head)
        if a.get("objective"):
            L.append("")
            L.append("*Objective: %s*" % a["objective"])
        L.append("")
        L.append("**Q.** %s" % a.get("stem", "").replace("\n", " "))
        L.append("")
        if a.get("type") == "short":
            L.append("**His answer, verbatim:**")
            L.append("")
            L.append("```")
            L.append(a.get("answer", "") or "(left blank)")
            L.append("```")
            L.append("")
            if a.get("model"):
                L.append("**Model answer (from the bank, NOT his):** %s" % a["model"].replace("\n", " "))
                L.append("")
            if a.get("rubric"):
                L.append("**Rubric. Replace each `(unmarked)` with `(pass)` or `(fail)`:**")
                L.append("")
                for r in a["rubric"]:
                    L.append("- (unmarked) %s" % r)
                L.append("")
            L.append("MARK: (unmarked)")
        else:
            L.append("**Selected:** %s" % (a.get("answer") or "(nothing)"))
        L.append("")
    if not done:
        L.append("---")
        L.append("")
        L.append("*Sitting was not finished. Everything above is real; nothing after it was answered.*")
        L.append("")
    return "\n".join(L)


def cmd_serve(a):
    """Run the quiz against a local process so every answer is written to disk.

    The static `build` page is sandboxed by the browser and cannot write a file,
    which is why answers used to evaporate when the tab closed. A loopback
    server is the smallest thing that fixes it without adding a dependency.

    It also does the scoring. The page is sent items with the key stripped, and
    POSTs each response here; this process calls the one scorer, records the
    result, and returns the verdict with the explanation. So a sitting that is
    meant to count is one where the browser never held the answers.
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
    # Keyed by item id and rewritten in full on every answer, so re-answering an
    # item replaces its entry instead of appending a second one, and a sitting
    # that stops halfway still leaves a valid file.
    answered = collections.OrderedDict()
    state = {"writes": 0}

    def record(q, response):
        score = score_response(q, response)
        answered[q["id"]] = {
            "n": q["number"], "type": q["type"], "stem": q["stem"],
            "objective": q.get("objective", ""),
            "answer": response_text(q, response), "correct": score,
            "model": q.get("model", ""), "rubric": q.get("rubric") or []}
        done = len(answered) >= len(qs)
        md = attempt_markdown(a.bank, list(answered.values()), done)
        open(out, "w", encoding="utf-8").write(md)
        state["writes"] += 1
        sys.stdout.write("\r  %d/%d answered, saved" % (len(answered), len(qs)))
        sys.stdout.flush()
        if done:
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
                payload = {"item_id": q["id"], "score": record(q, data.get("response")),
                           "explain": explain_payload(q, a.reveal)}
            except Exception as exc:                # never let a bad POST kill a sitting
                self.send_error(500, str(exc))
                return
            self.send_json(payload)

    print("itembank serve")
    srv = server.bind(H, a.port)

    with srv:
        url = "http://127.0.0.1:%d/" % srv.server_address[1]
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
