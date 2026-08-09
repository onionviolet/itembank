#!/usr/bin/env python3
"""Wave 0 harness for Phase 4's structured day-document editing (plans 04-02
and 04-06).

This module is deliberately infrastructure-only: it builds isolated LF/CRLF
plan documents, carries the supported/refused table-grammar corpus from
04-UI-SPEC.md, provides raw-byte hash/diff/apply helpers, concurrent-rewrite
hooks, and CLI/HTTP helpers -- all of which later TDD tasks will turn into
RED assertions against `surfaces/day_document.py` when that module exists.
It must run green *before* `surfaces/day_document.py` exists, so its
self-checks exercise only its own builders/helpers plus `surfaces/day.py`'s
current public behavior (the cockpit parser the phase does not replace).

Standard library only, no test framework, runnable as
`python tests/day_edit_roundtrip.py`.
"""
import difflib, hashlib, json, os, subprocess, sys, tempfile, threading, time
import urllib.error, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from surfaces import day                                # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


# ---- isolated plan builders -------------------------------------------------

def plan_bytes(rows, lf=True, outer_pipes=True, padding=True,
               prose=("Prose above the table.",), decoy_table=True):
    """Build one plan document as bytes.

    `rows` is a list of cell lists; the first row is the header. Controls the
    byte-level shapes the grammar contract cares about: line endings (LF or
    CRLF), optional outer pipes, leading/trailing cell padding, surrounding
    prose, and an unrelated decoy table that the cockpit parser must ignore.
    Returns UTF-8 bytes (no trailing newline), so raw-byte assertions in later
    plans compare exact spans.
    """
    nl = "\r\n" if not lf else "\n"
    out = ["# plan" + nl, nl.join(prose) + nl, nl]
    if decoy_table:
        out.append("| Setting | Value |" + nl)
        out.append("|---|---|" + nl)
        out.append("| Timezone | UTC |" + nl)
        out.append(nl)
    for idx, row in enumerate(rows):
        if outer_pipes:
            line = "| " + " | ".join(row) + " |"
        else:
            line = " | ".join(row)
        if padding:
            line = "  " + line + "  "
        out.append(line + nl)
        if idx == 0:
            rule = "|" + "|".join("---" for _ in row) + "|"
            if not outer_pipes:
                rule = rule.strip("|")
            if padding:
                rule = "  " + rule + "  "
            out.append(rule + nl)
    return "".join(out).encode("utf-8")


def write_plan(base_dir, rows, name="plan.md", **kwargs):
    """Write `plan_bytes(...)` into a fresh temp directory and return its path."""
    path = os.path.join(base_dir, name)
    with open(path, "wb") as fh:
        fh.write(plan_bytes(rows, **kwargs))
    return path


def row_for(iso="2026-01-07", cells=("ch 2 finish", "Ch 1 finish", "Lab 0")):
    """A single dated data row (header lives outside this helper's rows)."""
    return [iso] + list(cells)


HEADER = ["Date", "EMT (top priority)", "Math, ~25 min", "CS + other"]


# ---- supported / refused grammar corpus (04-UI-SPEC.md) ---------------------
# Each entry is (name, bytes). Later plans turn each into RED assertions; the
# harness itself only guarantees the corpus is constructible and uniquely
# named, and that the *supported* shapes parse with today's cockpit parser.

SUPPORTED_GRAMMAR = (
    ("lf-basic", plan_bytes([HEADER, row_for()])),
    ("crlf-basic", plan_bytes([HEADER, row_for()], lf=False)),
    ("no-outer-pipes", plan_bytes([HEADER, row_for()], outer_pipes=False)),
    ("padded-cells", plan_bytes([HEADER, row_for()], padding=True)),
    ("unknown-columns", plan_bytes(
        [["Date", "EMT", "Notes", "Math"],
         row_for(cells=("x", "handwritten note", "y"))])),
    ("surrounding-prose", plan_bytes([HEADER, row_for()], prose=(
        "A line before.", "Another line before."))),
    ("unrelated-tables", plan_bytes([HEADER, row_for()], decoy_table=True)),
    ("escaped-pipe-cell", plan_bytes(
        [["Date", "EMT"], ["2026-01-07", "read p. 1 \\| 2"]])),
    ("inline-code-pipe-cell", plan_bytes(
        [["Date", "EMT"], ["2026-01-07", "run `a | b` and note it"]])),
)


def _refused_entries():
    """The refused-grammar corpus. Builders must not crash; whether today's
    cockpit parser tolerates them is deliberately NOT asserted here -- the
    strict `no write` contract belongs to plan 04-02's RED phase.
    """
    entries = []
    dup = [HEADER, row_for(), row_for()]
    entries.append(("duplicate-matching-date", plan_bytes(dup)))
    # Missing delimiter/rule row: header + data rows only.
    nl = "\n"
    no_rule = ("# plan\n\n| Date | EMT |\n| 2026-01-07 | task |\n").encode()
    entries.append(("missing-rule-row", no_rule))
    # Missing dated row: header + rule only.
    only_header = ("# plan\n\n| Date | EMT |\n|---|---|\n").encode()
    entries.append(("missing-dated-row", only_header))
    # Missing header: rule + dated row only.
    no_header = ("# plan\n\n|---|---|\n| 2026-01-07 | task |\n").encode()
    entries.append(("missing-header", no_header))
    # Multiline cell/table extension: a data row spanning two lines.
    multiline = ("# plan\n\n| Date | EMT |\n|---|---|\n"
                 "| 2026-01-07 | first line\nsecond line |\n").encode()
    entries.append(("multiline-cell", multiline))
    # HTML table.
    html_table = ("# plan\n\n<table><tr><th>Date</th><th>EMT</th></tr>\n"
                  "<tr><td>2026-01-07</td><td>task</td></tr></table>\n").encode()
    entries.append(("html-table", html_table))
    # Unclosed inline-code span in the target cell.
    unclosed_code = ("# plan\n\n| Date | EMT |\n|---|---|\n"
                     "| 2026-01-07 | run `a | b\n").encode()
    entries.append(("unclosed-code-span", unclosed_code))
    # Newline/control character in edit input is a client-side refusal; the
    # corpus entry just proves the harness can represent the pathological byte.
    control_input = ("# plan\n\n| Date | EMT |\n|---|---|\n"
                     "| 2026-01-07 | task\u0000nul |\n").encode()
    entries.append(("control-char-input", control_input))
    return tuple(entries)


REFUSED_GRAMMAR = _refused_entries()


# ---- raw-byte helpers -------------------------------------------------------

def sha256_bytes(data):
    """SHA-256 of raw bytes -- the revision token family later plans compare."""
    return hashlib.sha256(data).hexdigest()


def changed_spans(before, after):
    """`(start, end, replacement_bytes)` triples that patch `before` into
    `after`, computed by difflib's opcodes -- the harness's own expectation
    helper for "nothing outside the edited cell changed". Callers apply them
    in descending `start` order (see `apply_spans`).
    """
    spans = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, before, after).get_opcodes():
        if tag != "equal":
            spans.append((i1, i2, after[j1:j2]))
    return spans


def apply_spans(data, edits):
    """Apply `edits` (list of `(start, end, replacement_bytes)`) to `data`,
    replacements applied in descending byte-offset order so earlier offsets
    stay valid -- the exact replacement discipline the future patcher uses.
    """
    out = bytearray(data)
    for start, end, replacement in sorted(edits, key=lambda e: e[0], reverse=True):
        out[start:end] = replacement
    return bytes(out)


# ---- concurrency hooks ------------------------------------------------------

def concurrent_rewrite(path, new_bytes, delay=0.1):
    """A daemon thread that atomically replaces `path` with `new_bytes` after
    `delay` seconds -- the "external editor saves while the browser holds the
    old revision" hook plan 04-06's conflict tests will drive.
    """
    def _rewrite():
        time.sleep(delay)
        tmp = path + ".tmp"
        with open(tmp, "wb") as fh:
            fh.write(new_bytes)
        os.replace(tmp, path)
    thread = threading.Thread(target=_rewrite, daemon=True)
    thread.start()
    return thread


# ---- CLI / HTTP helpers -----------------------------------------------------

def run_cli(args, cwd=None, timeout=15):
    """Run `itembank <args>` as a subprocess and return (returncode, stdout)."""
    result = subprocess.run(
        [sys.executable, "-u", os.path.join(ROOT, "itembank.py")] + list(args),
        cwd=cwd or ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, timeout=timeout)
    return result.returncode, result.stdout


def http_post(url, payload, timeout=5):
    """POST a JSON payload, returning parsed JSON. Raises HTTPError on a
    non-2xx so callers can assert refusal codes exactly.
    """
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as res:
        return json.loads(res.read().decode("utf-8"))


# ---- self-checks (green without surfaces/day_document.py) -------------------

def check_builders_and_corpus():
    with tempfile.TemporaryDirectory() as tmp:
        lf = write_plan(tmp, [HEADER, row_for()], "lf.md")
        crlf = write_plan(tmp, [HEADER, row_for()], "crlf.md", lf=False)
        for path in (lf, crlf):
            parsed = day.parse_plan(path, 2026)
            if "2026-01-07" not in parsed:
                fail("built plan did not parse into the dated row: %r" % parsed)
            if parsed["2026-01-07"].get("EMT") != "ch 2 finish":
                fail("built plan parsed the wrong EMT cell: %r" % parsed["2026-01-07"])
        if b"\r\n" not in open(crlf, "rb").read():
            fail("crlf builder did not actually emit CRLF bytes")
        if b"\r\n" in open(lf, "rb").read():
            fail("lf builder emitted CRLF bytes")

        names = [name for name, _ in SUPPORTED_GRAMMAR]
        if len(set(names)) != len(names):
            fail("SUPPORTED_GRAMMAR has duplicate names")
        for name, data in SUPPORTED_GRAMMAR:
            if not isinstance(data, bytes):
                fail("supported entry %r is not bytes" % name)
        names = [name for name, _ in REFUSED_GRAMMAR]
        if len(set(names)) != len(names):
            fail("REFUSED_GRAMMAR has duplicate names")
        for name, data in REFUSED_GRAMMAR:
            if not isinstance(data, bytes):
                fail("refused entry %r is not bytes" % name)


def check_byte_helpers():
    a = b"| Date | EMT |\n| 2026-01-07 | old task |\n"
    b = b"| Date | EMT |\n| 2026-01-07 | new task |\n"
    if sha256_bytes(a) == sha256_bytes(b):
        fail("sha256_bytes gave identical hashes for different content")
    spans = changed_spans(a, b)
    want = [(30, 33, b"new")]      # "old" -> "new"; the trailing " task" matches
    if spans != want:
        fail("changed_spans returned %r, expected %r" % (spans, want))
    rebuilt = apply_spans(a, spans)
    if rebuilt != b:
        fail("apply_spans did not rebuild the edited document byte-for-byte")
    # Descending-order application: two edits, later offset applied first.
    multi = apply_spans(b"abcdef", [(0, 1, b"X"), (4, 6, b"YZ")])
    if multi != b"XbcdYZ":
        fail("apply_spans misapplied multiple edits: %r" % multi)


def check_concurrent_and_cli_helpers():
    with tempfile.TemporaryDirectory() as tmp:
        path = write_plan(tmp, [HEADER, row_for()], "race.md")
        original = open(path, "rb").read()
        replaced = plan_bytes([HEADER, row_for(cells=("x", "y", "z"))])
        thread = concurrent_rewrite(path, replaced, delay=0.05)
        thread.join(timeout=5)
        if open(path, "rb").read() != replaced:
            fail("concurrent_rewrite did not replace the plan bytes")
        if open(path, "rb").read() == original:
            fail("concurrent_rewrite wrote identical bytes")

    code, out = run_cli(["--help"])
    if code != 0 or "usage" not in out.lower():
        fail("run_cli could not run `itembank --help`: code=%d out=%r" % (code, out[:200]))


def check_http_helper_refuses_closed_port():
    # A closed port must raise HTTPError (or urllib.error.URLError), never
    # silently return a body -- the refusal-assertion shape later plans rely on.
    try:
        http_post("http://127.0.0.1:1/day/nope/save", {"date": "2026-01-07"})
    except urllib.error.HTTPError:
        return
    except OSError:
        return
    fail("http_post against a closed port did not raise")


def main():
    check_builders_and_corpus()
    check_byte_helpers()
    check_concurrent_and_cli_helpers()
    check_http_helper_refuses_closed_port()
    print("ok: day-edit Wave 0 harness -- LF/CRLF builders, %d supported + %d "
          "refused grammar entries, byte hash/diff/apply helpers, concurrent "
          "rewrite hooks, CLI/HTTP helpers all self-check green before "
          "surfaces/day_document.py exists"
          % (len(SUPPORTED_GRAMMAR), len(REFUSED_GRAMMAR)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
