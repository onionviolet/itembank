#!/usr/bin/env python3
"""Symbol definition navigation returns to the same served quiz sitting."""
import json
import os
import re
import sys
import tempfile
import urllib.parse
import urllib.request
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import evidence
from daemon_roundtrip import get, start_daemon


BANK = """# Symbol return bank (synthetic)

## TERMS

P | A statement variable.

Q1. Read P in the first invented example.
[OBJECTIVE: logic:notation]
A) Orange
B) Purple
C) Yellow
CORRECT: B
WHY BEST: The invented rule selects the second color.
CONFIDENCE: high

Q2. Read P in the second invented example.
[OBJECTIVE: logic:notation]
A) Orange
B) Purple
C) Yellow
CORRECT: B
WHY BEST: The invented rule selects the second color.
CONFIDENCE: high
"""


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.card = {}
        self.links = []
        self.answer_path = None
        self.form_token = None
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "data-server-baseline" in attrs:
            self.card = attrs
        if tag == "a":
            self.links.append(attrs)
        if tag == "form" and "data-answer-form" in attrs:
            self.answer_path = attrs["action"]
        if tag == "input" and attrs.get("name") == "form_token" \
                and self.form_token is None:
            self.form_token = attrs["value"]


def check_symbol_return_keeps_sitting():
    with tempfile.TemporaryDirectory(prefix="quiz-symbol-return-") as root:
        with open(os.path.join(root, "symbols.md"), "w", encoding="utf-8") as fh:
            fh.write(BANK)
        proc, base, _lines = start_daemon(root)
        try:
            for suffix in ("", "?mode=practice", "?mode=exam"):
                route = "/quiz/symbols" + suffix
                _, first = get(urllib.parse.urljoin(base, route))
                first_page = Page(first)
                session_id = first_page.card["data-session-id"]
                current = first
                current_page = first_page
                assert '<b id="pos">1</b>' in current
                symbol = next(link for link in current_page.links
                              if "data-gloss-fetch" in link)
                payload = json.loads(re.search(
                    r"window.ItembankQuestionSymbols=(.*?);</script>",
                    current).group(1))
                item_id = current_page.card["data-item-id"]
                assert payload[item_id][0]["href"] == symbol["href"], \
                    "client metadata and baseline disagree on the return route"
                expected_return = urllib.parse.parse_qs(
                    urllib.parse.urlsplit(symbol["href"]).query)["return"][0]
                assert urllib.parse.urldefrag(expected_return)[0] == route, \
                    "symbol return dropped the launch route: %r" % expected_return

                before = [row for row in evidence.live_events(evidence.log_path(root))
                          if row.get("event_type") == "response"]
                _, definition = get(urllib.parse.urljoin(base, symbol["href"]))
                back = Page(definition).links[0]["href"]
                assert back == expected_return, "definition page changed its return route"
                _, returned = get(urllib.parse.urljoin(base, back))
                returned_page = Page(returned)
                assert returned_page.card["data-session-id"] == session_id, \
                    "symbol lookup returned to a different sitting"
                assert returned_page.card["data-item-id"] == item_id, \
                    "symbol lookup changed the current question"
                assert '<b id="pos">1</b>' in returned, "symbol lookup lost position"
                after = [row for row in evidence.live_events(evidence.log_path(root))
                         if row.get("event_type") == "response"]
                assert after == before, "symbol navigation replayed an answer"

                _, lookup = get(urllib.parse.urljoin(base, symbol["data-gloss-fetch"]))
                assert json.loads(lookup)["def"] == "A statement variable."
        finally:
            proc.terminate()
            proc.wait(timeout=5)


if __name__ == "__main__":
    check_symbol_return_keeps_sitting()
    print("quiz symbol return: default, practice, and exam retain their sitting and cursor")
