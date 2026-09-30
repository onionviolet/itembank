#!/usr/bin/env python3
"""Real served form and optional browser fixture for the W1/W2 repair."""
import argparse
import html
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import model


def main(runtime=None, browser_hold=False):
    with tempfile.TemporaryDirectory(prefix="itembank-a1-") as directory:
        root = Path(directory)
        sample = (ROOT / "fixtures/sample_bank.md").read_text()
        blocks = re.split(r"(?m)(?=^Q\d+\.)", sample)
        build = next(block for block in blocks if "[TYPE: build]" in block)
        assignment = next(block for block in blocks if "[TYPE: dnd]" in block)
        assignment = re.sub(r"(?m)^ITEM\) (.*?) ::", "ITEM) A ___ parameter. ::", assignment)
        text = "# Synthetic workflow fixture\n\n" + re.sub(r"^Q5\.", "Q1.", assignment) + re.sub(r"^Q4\.", "Q2.", build)
        text = re.sub(r"(?m)^\[HASH:.*\]\n", "", text)
        bank = root / "a1_recovery.md"
        bank.write_text(text)
        questions = model.parse_bank(text)
        by_id = {q["id"]:q for q in questions}
        proc = subprocess.Popen([sys.executable, str(runtime or ROOT / "itembank.py"),
            "serve", str(bank), "--no-open", "--mode", "exam", "--port", "0"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        lines = []
        threading.Thread(target=lambda: lines.extend(proc.stdout), daemon=True).start()
        try:
            base = None
            for _ in range(100):
                match = re.search(r"http://127\.0\.0\.1:\d+/", "".join(lines))
                if match:
                    base = match.group(0)
                    break
                if proc.poll() is not None:
                    break
                time.sleep(.1)
            assert base, "Serve did not launch: " + "".join(lines)
            url = base + "quiz/a1_recovery"
            if browser_hold:
                print(json.dumps({"url":url,"root":directory,"mode":"exam"}), flush=True)
                input("Press Enter after the disposable browser checks: ")
                return
            def get(address):
                return urllib.request.urlopen(address, timeout=10).read().decode()
            page = get(url)
            for index in range(2):
                ident = re.search(r'data-item-id="([^"]+)"',page).group(1)
                q = by_id[ident]
                token = re.search(r'name="form_token" value="([^"]+)"',page).group(1)
                action = html.unescape(re.search(r'<form method="post" action="([^"]+)"',page).group(1))
                assert "function installInlineWordBank(" in page
                assert "function readBuildDraft(" in page
                if q["type"] == "dnd":
                    assert page.count('class="inline-completion"') == 4
                    fields = [("row_"+str(i),row["cat"]) for i,row in enumerate(q["rows"])]
                else:
                    assert 'name="step_0"' in page
                    fields = [("step_"+str(i),value) for i,value in enumerate(q["steps"])]
                refused = urllib.request.Request(urllib.parse.urljoin(base,action),
                    data=urllib.parse.urlencode(fields+[("action","submit"),("form_token","invalid")]).encode())
                try:
                    urllib.request.urlopen(refused,timeout=10)
                    raise AssertionError("Invalid token was accepted")
                except urllib.error.HTTPError as exc:
                    assert exc.code == 403
                    rejected = exc.read().decode()
                    assert " selected" in rejected
                submitted = urllib.request.Request(urllib.parse.urljoin(base,action),
                    data=urllib.parse.urlencode(fields+[("action","submit"),("form_token",token)]).encode())
                page = urllib.request.urlopen(submitted,timeout=10).read().decode()
                assert "data-feedback-pause" in page
                assert "Correct. Your answer" not in page
                if index == 0:
                    home = get(base)
                    assert "Answered q1" in home
                    assert "Answered q1 (correct)" not in home
                    assert "Answered q1 (wrong)" not in home
                    report_url = html.unescape(re.search(
                        r'href="(/report\?session=[^"]+)"', home).group(1))
                    report = get(urllib.parse.urljoin(base, report_url))
                    assert re.search(r'data-field="auto_correct"><div class="figure-value">([^<]+)',report).group(1) != '1'
                    assert "No activity yet" in get(base + "activity")
                match = re.search(r'data-feedback-continue\s+href="([^"]+)"',page)
                if match:
                    page = get(urllib.parse.urljoin(base,html.unescape(match.group(1))))
            events = [json.loads(line) for path in root.rglob("evidence.jsonl")
                      for line in path.read_text().splitlines() if line.strip()]
            responses = [row for row in events if row.get("event_type") == "response"]
            assert len(responses) == 2, events
            assert all(row["mode"] == "exam" and row["score"] is True for row in responses)
            print("W1/W2 served recovery: two native forms, refused retries, exam withholding and two recorded responses pass")
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", type=Path)
    parser.add_argument("--browser-hold", action="store_true")
    args = parser.parse_args()
    main(args.runtime,args.browser_hold)
