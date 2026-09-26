#!/usr/bin/env python3
"""Focused surface checks for the typed `fill` response."""
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import model  # noqa: E402
import runtime  # noqa: E402
import evidence  # noqa: E402
from surfaces import anki, daemon, gift, quiz, quiz_page  # noqa: E402


BANK = """# Synthetic fill bank

Q1. Complete every field.
[ID: 1111111111111111]
[TYPE: fill]
[OBJECTIVE: demo:fill]
[FIELDS: [{"id":"color","label":"Color","kind":"text","accepted":["blue","azure"]},{"id":"count","label":"Count","kind":"numeric","answer":"2.5","atol":"0.01"},{"id":"length","label":"Length in m or cm","kind":"numeric","answer":"1","unit":"m","units":{"m":"1","cm":"0.01"}}]]

WHY BEST: Synthetic typed fields exercise text, numeric tolerance, and unit input.
CONFIDENCE: high
"""


def fail(message):
    raise AssertionError(message)


def item():
    return model.parse_bank(BANK)[0]


def check_public_and_offline_contract():
    q = item()
    public = runtime.public_item(q)
    if public.get("type") != "fill":
        fail("public item did not preserve the fill type")
    if public.get("response_schema") != {
            "type": "object", "required": ["color", "count", "length"],
            "values": "string", "additional_properties": False}:
        fail("public response schema does not require the exact field mapping")
    text_field, number_field, unit_field = public["fields"]
    if text_field != {"id": "color", "label": "Color", "kind": "text",
                     "case_sensitive": True, "whitespace": "trim"}:
        fail("public text field does not carry only its input rules")
    if number_field != {"id": "count", "label": "Count", "kind": "numeric"}:
        fail("public numeric field leaked its target or tolerance")
    if unit_field.get("units") != ["m", "cm"]:
        fail("public unit field did not expose the allowed unit names")
    for private in ("accepted", "answer", "atol", "rtol", "unit"):
        if any(private in field for field in public["fields"]):
            fail("public fields leaked private member %s" % private)
    offline = runtime.page_item(q, offline=True)
    if offline.get("served_required") is not True:
        fail("offline fill item does not require the served runtime")
    if "key" in offline or "explain" in offline:
        fail("offline fill item carries keyed material")


def check_native_form_and_decoder():
    q = item()
    public = runtime.public_item(q)
    fields = {"fill_color": ["  blue  "], "fill_count": ["5/2"],
              "fill_length": ["100 cm"]}
    html = quiz_page.baseline_for(
        {"session_id": "s", "item": public}, {}, "/answer",
        {"submit": "token"}, prefill=fields)
    for name, raw in (("fill_color", "  blue  "), ("fill_count", "5/2"),
                      ("fill_length", "100 cm")):
        if 'type="text" name="%s"' % name not in html or raw not in html:
            fail("native form did not render and restore %s" % name)
    if 'type="number"' in html:
        fail("fill fields use number inputs, which reject fractions or units")
    for text in ("Case matters.", "Leading and trailing spaces are ignored.",
                 "Enter a decimal, fraction, or scientific number.",
                 "Add a space, then one of: m, cm.", 'maxlength="4096"'):
        if text not in html:
            fail("native form omits field help or bound %r" % text)
    answer = daemon._form_answer(public, fields)
    if answer != {"color": "  blue  ", "count": "5/2", "length": "100 cm"}:
        fail("native form decoder changed raw field strings: %r" % answer)


def check_browser_clients():
    if "fill:asFillOffline" not in quiz_page.OFFLINE_JS:
        fail("offline dispatcher does not handle fill")
    if "Serve to check response" not in quiz_page.OFFLINE_JS:
        fail("offline fill renderer has no explicit runtime-needed state")
    if "fill:asFill" not in quiz_page.SERVED_JS:
        fail("served dispatcher does not handle fill")
    for required in ("input.type = \"text\"", "input.maxLength = 4096",
                     "Uppercase and lowercase are treated the same.",
                     "Add a space, then one of:", "response()",
                     "localStorage.setItem", "settle(q, response()",
                     "v.entry_error", "esc(v.entry_error)"):
        if required not in quiz_page.SERVED_JS:
            fail("served fill renderer is missing %r" % required)
    for forbidden in ("input.type = \"number\"", ".accepted", ".atol", ".rtol"):
        if forbidden in quiz_page.SERVED_JS:
            fail("served client contains fill scoring material %r" % forbidden)


def check_invalid_legacy_response_is_not_recorded():
    q = item()
    with tempfile.TemporaryDirectory() as td:
        log = os.path.join(td, "evidence.jsonl")
        attempt = os.path.join(td, "attempt.md")
        try:
            quiz.record_answer("synthetic.md", [q], "session", log, attempt,
                               "practice", q,
                               {"color": "blue", "count": "not a number",
                                "length": "100 cm"}, 1)
        except SystemExit as exc:
            if "Count" not in str(exc):
                fail("legacy refusal was not learner-readable: %s" % exc)
        else:
            fail("legacy recorder accepted a structurally invalid fill response")
        if os.path.exists(log) or os.path.exists(attempt):
            fail("invalid fill response reached evidence or attempt output")


def check_gift_refusal():
    document, errors, _warnings = gift.render_gift([item()])
    if document:
        fail("GIFT approximated a fill item")
    if not any(error.startswith(gift.GIFT_TYPE_UNSUPPORTED) and "type 'fill'" in error
               for error in errors):
        fail("GIFT did not explicitly refuse fill conversion")


def check_anki_refusal_precedes_output():
    class Args:
        format = "basic"
        force = True

    with tempfile.TemporaryDirectory() as td:
        Args.bank = os.path.join(td, "fill.md")
        Args.out = os.path.join(td, "fill.tsv")
        with open(Args.bank, "w", encoding="utf-8") as fh:
            fh.write(BANK)
        try:
            anki.cmd_export(Args)
        except SystemExit as exc:
            if not str(exc).startswith("export.fill_unsupported"):
                fail("Anki refusal lacks its stable code: %s" % exc)
        else:
            fail("forced Basic export flattened fill scoring rules")
        if os.path.exists(Args.out):
            fail("Anki wrote output before refusing fill conversion")


def start_daemon(workdir):
    proc = subprocess.Popen(
        [sys.executable, "-u", os.path.join(ROOT, "itembank.py"), "daemon",
         workdir, "--no-open", "--port", "0"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    lines = []
    threading.Thread(target=lambda: [lines.append(line) for line in proc.stdout],
                     daemon=True).start()
    for _ in range(60):
        time.sleep(0.1)
        match = re.search(r"http://127\.0\.0\.1:\d+/", "".join(lines))
        if match:
            return proc, match.group(0)
    proc.terminate()
    fail("fill route daemon did not start: " + "".join(lines))


def post_json(url, payload):
    request = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"), method="POST",
        headers={"Content-Type": "application/json"})
    try:
        response = urllib.request.urlopen(request, timeout=5)
    except urllib.error.HTTPError as exc:
        response = exc
    raw = response.read().decode("utf-8")
    try:
        body = json.loads(raw)
    except ValueError:
        body = raw
    return response.status, body


def response_events(workdir):
    path = evidence.log_path(workdir)
    if not os.path.exists(path):
        return []
    return [event for event in evidence.live_events(path)
            if event.get("event_type") == "response"]


def check_fill_route_retry(route):
    with tempfile.TemporaryDirectory() as td:
        bank = os.path.join(td, "fill.md")
        with open(bank, "w", encoding="utf-8") as fh:
            fh.write(BANK)
        proc, base = start_daemon(td)
        try:
            if route == "api":
                status, started = post_json(base + "api/start", {
                    "bank": "fill", "count": 1, "mode": "practice"})
                if status != 200:
                    fail("fill API session did not start: %r" % (started,))
                endpoint = base + "api/submit"
                invalid = {"session_id": started["session_id"], "answer": {
                    "color": "blue", "count": "two", "length": "100 cm"}}
                valid = {"session_id": started["session_id"], "answer": {
                    "color": "blue", "count": "5/2", "length": "100 cm"}}
            else:
                urllib.request.urlopen(base + "quiz/fill", timeout=5).read()
                endpoint = base + "quiz/fill/answer"
                invalid = {"id": "q1", "response": {
                    "color": "blue", "count": "two", "length": "100 cm"}}
                valid = {"id": "q1", "response": {
                    "color": "blue", "count": "5/2", "length": "100 cm"}}
            status, refused = post_json(endpoint, invalid)
            if status != 200 or "entry_error" not in refused:
                fail("%s fill validation was not a retryable JSON body: %r %r"
                     % (route, status, refused))
            if response_events(td):
                fail("%s invalid fill response wrote evidence" % route)
            status, accepted = post_json(endpoint, valid)
            if status != 200 or accepted.get("accepted") is not True:
                fail("%s fill retry did not succeed: %r %r"
                     % (route, status, accepted))
            if len(response_events(td)) != 1:
                fail("%s fill retry did not write exactly one response" % route)
        finally:
            proc.terminate()
            proc.wait(timeout=5)


def main():
    check_public_and_offline_contract()
    check_native_form_and_decoder()
    check_browser_clients()
    check_invalid_legacy_response_is_not_recorded()
    check_gift_refusal()
    check_anki_refusal_precedes_output()
    check_fill_route_retry("api")
    check_fill_route_retry("legacy")
    print("fill surface roundtrip: ok")


if __name__ == "__main__":
    main()
