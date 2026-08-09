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
import difflib, hashlib, json, os, re, subprocess, sys, tempfile, threading, time
import urllib.error, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from surfaces import day                                # noqa: E402

try:
    from surfaces import day_document                     # noqa: E402
except ImportError:
    # Plan 04-02 is TDD: the adapter does not exist until Task 1's RED gate
    # is observed. Every Task 1/2 check below fails cleanly in that state.
    day_document = None


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


def single_replacement(before, after):
    """If `after` is `before` with exactly one contiguous region replaced,
    return (start, end, replacement_bytes); otherwise return None.

    `changed_spans` (difflib opcodes) is alignment-dependent and can report
    several overlapping spans for one true replacement, so the exact-byte
    contract is asserted through common-prefix/suffix math instead.
    """
    n = min(len(before), len(after))
    i = 0
    while i < n and before[i] == after[i]:
        i += 1
    j = 0
    while j < len(before) - i and j < len(after) - i \
            and before[-1 - j] == after[-1 - j]:
        j += 1
    start, end = i, len(before) - j
    replacement = after[i:len(after) - j]
    if before[:start] + replacement + before[end:] != after:
        return None
    return (start, end, replacement)


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


# ---- plan 04-02 Task 1: lossless dated-row snapshot/edit --------------------

def check_task1_snapshot_via_cli():
    if day_document is None:
        fail("Task 1 RED: surfaces.day_document does not exist yet")
    with tempfile.TemporaryDirectory() as tmp:
        path = write_plan(tmp, [HEADER, row_for()])
        code, out = run_cli(["day", path, "--date", "2026-01-07", "--edit"])
        if code != 0:
            fail("snapshot exited %d, want 0: %s" % (code, out))
        snap = json.loads(out)
        if snap.get("status") != "ready":
            fail("snapshot status %r, want 'ready'" % snap.get("status"))
        if not re.fullmatch(r"[0-9a-f]{64}", snap.get("revision", "")):
            fail("snapshot revision %r is not a 64-hex SHA-256" % snap.get("revision"))
        if snap.get("date") != "2026-01-07":
            fail("snapshot date %r, want 2026-01-07" % snap.get("date"))
        if snap.get("columns") != list(HEADER):
            fail("snapshot columns %r, want %r" % (snap.get("columns"), list(HEADER)))
        cells = snap.get("cells", {})
        if cells.get("EMT (top priority)") != "ch 2 finish":
            fail("snapshot EMT cell %r, want 'ch 2 finish'" % cells.get("EMT (top priority)"))
        if cells.get("Math, ~25 min") != "Ch 1 finish":
            fail("snapshot Math cell %r, want 'Ch 1 finish'" % cells.get("Math, ~25 min"))
        if cells.get("CS + other") != "Lab 0":
            fail("snapshot CS cell %r, want 'Lab 0'" % cells.get("CS + other"))
        if "Date" in cells:
            fail("snapshot made the date column editable")
        if snap.get("document") != open(path, encoding="utf-8").read():
            fail("snapshot document does not match the file text")
        if snap.get("revision") != sha256_bytes(open(path, "rb").read()):
            fail("snapshot revision is not the SHA-256 of the file bytes")


def check_task1_single_cell_edit():
    if day_document is None:
        fail("Task 1 RED: surfaces.day_document does not exist yet")
    with tempfile.TemporaryDirectory() as tmp:
        path = write_plan(tmp, [HEADER, row_for()])
        before = open(path, "rb").read()
        code, out = run_cli(["day", path, "--date", "2026-01-07", "--edit"])
        snap = json.loads(out)
        rev = snap["revision"]
        code, out = run_cli(["day", path, "--date", "2026-01-07", "--edit",
                             "--set", "EMT=ch 3, start", "--revision", rev])
        if code != 0:
            fail("save exited %d: %s" % (code, out))
        result = json.loads(out)
        if result.get("status") != "saved":
            fail("save status %r, want 'saved'" % result.get("status"))
        if result.get("revision") == rev:
            fail("save returned the same revision it was given")
        after = open(path, "rb").read()
        if result.get("revision") != sha256_bytes(after):
            fail("save revision is not the SHA-256 of the bytes now on disk")
        start = before.index(b"ch 2 finish")
        end = start + len(b"ch 2 finish")
        want = before[:start] + b"ch 3, start" + before[end:]
        if after != want:
            fail("bytes outside the edited cell changed")
        changed = single_replacement(before, after)
        if changed is None:
            fail("single edit produced more than one contiguous change")
        s, e, repl = changed
        if not (start <= s and e <= end):
            fail("changed region %r escapes the EMT cell span (%d, %d)"
                 % (changed, start, end))


def check_task1_preservation_corpus():
    if day_document is None:
        fail("Task 1 RED: surfaces.day_document does not exist yet")
    with tempfile.TemporaryDirectory() as tmp:
        for name, data in SUPPORTED_GRAMMAR:
            if name == "lf-basic":
                continue
            path = os.path.join(tmp, name + ".md")
            with open(path, "wb") as fh:
                fh.write(data)
            code, out = run_cli(["day", path, "--date", "2026-01-07", "--edit"])
            if code != 0:
                fail("%s: snapshot exited %d: %s" % (name, code, out))
            snap = json.loads(out)
            if snap.get("status") != "ready":
                fail("%s: snapshot status %r, want ready" % (name, snap.get("status")))
            editable = [c for c in snap["columns"] if c != "Date"]
            if not editable:
                fail("%s: no editable columns in %r" % (name, snap["columns"]))
            target = {"unknown-columns": "Notes"}.get(name, editable[0])
            new_text = "edited " + name
            before = open(path, "rb").read()
            code, out = run_cli(["day", path, "--date", "2026-01-07", "--edit",
                                 "--set", "%s=%s" % (target, new_text),
                                 "--revision", snap["revision"]])
            if code != 0:
                fail("%s: save exited %d: %s" % (name, code, out))
            result = json.loads(out)
            if result.get("status") != "saved":
                fail("%s: save status %r, want saved" % (name, result.get("status")))
            after = open(path, "rb").read()
            changed = single_replacement(before, after)
            if changed is None:
                fail("%s: more than one contiguous region changed" % name)
            row_start = before.find(b"2026-01-07")
            if row_start < 0:
                fail("%s: dated row bytes not found in document" % name)
            row_end = before.find(b"\n", row_start)
            if row_end < 0:
                row_end = len(before)
            s, e, repl = changed
            if not (row_start <= s and e <= row_end):
                fail("%s: changed span %r escapes the dated row line" % (name, (s, e)))
            if repl != new_text.encode("utf-8"):
                fail("%s: changed bytes %r, want the submitted value %r"
                     % (name, repl, new_text))
            if name == "crlf-basic":
                if b"\r\n" not in after or after.count(b"\r\n") != before.count(b"\r\n"):
                    fail("crlf-basic: CRLF line endings were not preserved")
            if name == "padded-cells":
                if before.count(b"  | ") != after.count(b"  | "):
                    fail("padded-cells: cell padding was not preserved")
            if name == "no-outer-pipes":
                if after.strip().startswith(b"|"):
                    fail("no-outer-pipes: an outer pipe was introduced")
            if name == "escaped-pipe-cell":
                if snap["cells"].get(target) != "read p. 1 | 2":
                    fail("escaped-pipe-cell: snapshot did not unescape \\| -> |: %r"
                         % snap["cells"].get(target))
                if b"\\|" not in before:
                    fail("escaped-pipe-cell fixture lost its escape before the edit")
            if name == "inline-code-pipe-cell":
                if snap["cells"].get(target) != "run `a | b` and note it":
                    fail("inline-code-pipe-cell: snapshot cell %r"
                         % snap["cells"].get(target))
            if name == "unknown-columns":
                if target != "Notes":
                    fail("unknown-columns: expected to edit the Notes column, got %r" % target)
            if name == "surrounding-prose":
                if b"A line before." not in after or b"Another line before." not in after:
                    fail("surrounding-prose: prose was not preserved")
            if name == "unrelated-tables":
                if b"| Timezone | UTC |" not in after:
                    fail("unrelated-tables: decoy table was not preserved")


def check_task1_escape_survival_outside_edit():
    """Escaped pipes and inline-code pipes survive byte-identically when the
    cell *containing* them is not the one being edited (Test 3 wording:
    'outside edited cells')."""
    if day_document is None:
        fail("Task 1 RED: surfaces.day_document does not exist yet")
    with tempfile.TemporaryDirectory() as tmp:
        doc = plan_bytes(
            [["Date", "EMT", "Notes", "Math"],
             ["2026-01-07", "read p. 1 \\| 2", "run `a | b` and note it",
              "something"]],
            prose=("Prose line.",))
        path = os.path.join(tmp, "survive.md")
        with open(path, "wb") as fh:
            fh.write(doc)
        before = open(path, "rb").read()
        code, out = run_cli(["day", path, "--date", "2026-01-07", "--edit"])
        snap = json.loads(out)
        if snap.get("status") != "ready":
            fail("survival: snapshot not ready: %r" % snap)
        if snap["cells"].get("EMT") != "read p. 1 | 2":
            fail("survival: escaped-pipe display %r" % snap["cells"].get("EMT"))
        if snap["cells"].get("Notes") != "run `a | b` and note it":
            fail("survival: inline-code-pipe display %r"
                 % snap["cells"].get("Notes"))
        code, out = run_cli(["day", path, "--date", "2026-01-07", "--edit",
                             "--set", "Math=edited math",
                             "--revision", snap["revision"]])
        if code != 0:
            fail("survival: save exited %d: %s" % (code, out))
        result = json.loads(out)
        if result.get("status") != "saved":
            fail("survival: save status %r" % result.get("status"))
        after = open(path, "rb").read()
        if b"read p. 1 \\| 2" not in after:
            fail("survival: escaped pipe outside the edited cell did not "
                 "survive byte-identically")
        if b"run `a | b` and note it" not in after:
            fail("survival: inline code pipe outside the edited cell did not "
                 "survive byte-identically")
        changed = single_replacement(before, after)
        if changed is None:
            fail("survival: more than one contiguous region changed")
        s, e, repl = changed
        if before[s:e] != b"something" or repl != b"edited math":
            fail("survival: changed region %r is not exactly the Math cell"
                 % (changed,))


def check_task1_refusals():
    if day_document is None:
        fail("Task 1 RED: surfaces.day_document does not exist yet")
    with tempfile.TemporaryDirectory() as tmp:
        for name, data in REFUSED_GRAMMAR:
            if name == "control-char-input":
                # The corpus comment defines this entry as a representational
                # proof for client-side refusal of *submitted* values; the
                # document itself must not be treated as unreadable. The
                # submitted-value refusal is asserted separately below.
                continue
            path = os.path.join(tmp, "refused-" + name + ".md")
            with open(path, "wb") as fh:
                fh.write(data)
            code, out = run_cli(["day", path, "--date", "2026-01-07", "--edit"])
            if code == 0:
                fail("%s: refusal snapshot exited 0" % name)
            result = json.loads(out)
            if result.get("status") not in ("invalid", "unsupported"):
                fail("%s: snapshot status %r, want invalid/unsupported"
                     % (name, result.get("status")))
            if open(path, "rb").read() != data:
                fail("%s: refusal wrote to the file" % name)
            if os.path.exists(path + ".tmp"):
                fail("%s: refusal left a temporary file" % name)

        path = write_plan(tmp, [HEADER, row_for()], "valid.md")
        before = open(path, "rb").read()
        code, out = run_cli(["day", path, "--date", "2026-01-07", "--edit"])
        snap = json.loads(out)

        code, out = run_cli(["day", path, "--date", "2026-01-07", "--edit",
                             "--set", "NoSuchColumn=value",
                             "--revision", snap["revision"]])
        if code == 0:
            fail("unknown-column edit exited 0, want failure")
        result = json.loads(out)
        if result.get("status") != "invalid":
            fail("unknown-column edit status %r, want invalid" % result.get("status"))
        if result.get("draft") != {"NoSuchColumn": "value"}:
            fail("unknown-column edit did not echo the draft verbatim: %r"
                 % result.get("draft"))
        if open(path, "rb").read() != before:
            fail("unknown-column edit changed the file")

        code, out = run_cli(["day", path, "--date", "2026-01-07", "--edit",
                             "--set", "Date=2026-01-08",
                             "--revision", snap["revision"]])
        result = json.loads(out)
        if result.get("status") != "invalid":
            fail("date-column edit status %r, want invalid" % result.get("status"))

        for bad in ("EMT=a\nb", "EMT=a\x00b"):
            # The newline case is CLI-reachable; the NUL case cannot pass
            # through Windows CreateProcess argv, so both go through the
            # adapter API -- the exact path the CLI wraps.
            result = day_document.save(path, "2026-01-07",
                                       {"EMT": bad}, snap["revision"])
            if result.get("status") != "invalid":
                fail("control-value edit status %r, want invalid" % result.get("status"))
            if open(path, "rb").read() != before:
                fail("control-value edit changed the file")

        code, out = run_cli(["day", path, "--date", "2026-01-08", "--edit"])
        if code == 0:
            fail("missing-date snapshot exited 0, want failure")
        result = json.loads(out)
        if result.get("status") != "invalid":
            fail("missing-date snapshot status %r, want invalid" % result.get("status"))


def check_task1_atomic_write():
    if day_document is None:
        fail("Task 1 RED: surfaces.day_document does not exist yet")
    with tempfile.TemporaryDirectory() as tmp:
        path = write_plan(tmp, [HEADER, row_for()])
        snap = day_document.snapshot(path, 2026, "2026-01-07")
        if snap["status"] != "ready":
            fail("atomic: snapshot not ready: %r" % snap)
        calls = []
        orig_replace = os.replace

        def spy_replace(src, dst):
            calls.append((src, dst, os.path.exists(src)))
            return orig_replace(src, dst)

        os.replace = spy_replace
        try:
            result = day_document.save(path, "2026-01-07",
                                       {"EMT": "ch 3"}, snap["revision"])
        finally:
            os.replace = orig_replace
        if result["status"] != "saved":
            fail("atomic: save status %r" % result["status"])
        if not calls:
            fail("atomic: os.replace was never called")
        tmp_src, dst, existed = calls[-1]
        if dst != path:
            fail("atomic: os.replace target %r, want the plan path" % dst)
        if not existed:
            fail("atomic: temporary sibling file did not exist before replace")
        if os.path.basename(tmp_src) != os.path.basename(path) + ".tmp":
            fail("atomic: temporary file %r is not a sibling of the plan" % tmp_src)
        if os.path.exists(path + ".tmp"):
            fail("atomic: temporary file left behind")
        if result["revision"] != sha256_bytes(open(path, "rb").read()):
            fail("atomic: returned revision does not match bytes on disk")


# ---- plan 04-02 Task 2: stale revisions, conflicts, confirmed force ---------

def check_task2_conflict_no_write():
    if day_document is None:
        fail("Task 2 RED: surfaces.day_document does not exist yet")
    with tempfile.TemporaryDirectory() as tmp:
        path = write_plan(tmp, [HEADER, row_for()])
        snap = day_document.snapshot(path, 2026, "2026-01-07")
        concurrent = plan_bytes(
            [HEADER, row_for(cells=("ch 2 finish", "changed by Obsidian", "Lab 0"))])
        with open(path, "wb") as fh:
            fh.write(concurrent)

        result = day_document.save(path, "2026-01-07",
                                   {"EMT": "ch 3"}, snap["revision"])
        if result.get("status") != "conflict":
            fail("stale save status %r, want conflict" % result.get("status"))
        if open(path, "rb").read() != concurrent:
            fail("conflict wrote to the file")
        if result.get("draft") != {"EMT": "ch 3"}:
            fail("conflict lost the draft: %r" % result.get("draft"))
        if result.get("revision") != sha256_bytes(concurrent):
            fail("conflict did not carry the fresh revision")
        if result.get("submitted_revision") != snap["revision"]:
            fail("conflict did not carry the submitted revision")
        current = result.get("current", {})
        if current.get("revision") != result.get("revision"):
            fail("conflict current snapshot revision mismatch")
        if current.get("cells", {}).get("Math, ~25 min") != "changed by Obsidian":
            fail("conflict current snapshot did not carry the fresh cell value")
        if current.get("document") != concurrent.decode("utf-8"):
            fail("conflict current snapshot document mismatch")
        if os.path.exists(path + ".tmp"):
            fail("conflict left a temporary file")

        code, out = run_cli(["day", path, "--date", "2026-01-07", "--edit",
                             "--set", "EMT=ch 3", "--revision", snap["revision"]])
        if code == 0:
            fail("CLI conflict exited 0")
        cli = json.loads(out)
        if cli.get("status") != "conflict":
            fail("CLI conflict status %r" % cli.get("status"))
        if cli.get("draft") != {"EMT": "ch 3"}:
            fail("CLI conflict lost the draft: %r" % cli.get("draft"))
        if open(path, "rb").read() != concurrent:
            fail("CLI conflict wrote to the file")


def check_task2_metadata_no_false_conflict():
    if day_document is None:
        fail("Task 2 RED: surfaces.day_document does not exist yet")
    with tempfile.TemporaryDirectory() as tmp:
        path = write_plan(tmp, [HEADER, row_for()])
        snap = day_document.snapshot(path, 2026, "2026-01-07")
        os.utime(path, (time.time() + 5, time.time() + 5))
        result = day_document.save(path, "2026-01-07",
                                   {"EMT": "ch 3"}, snap["revision"])
        if result.get("status") != "saved":
            fail("metadata-only change caused %r, want saved" % result.get("status"))
        after = open(path, "rb").read()
        if result.get("revision") != sha256_bytes(after):
            fail("metadata-only save returned a wrong revision")

        snap2 = day_document.snapshot(path, 2026, "2026-01-07")
        mutated = after.replace(b"ch 3", b"ch 9")
        with open(path, "wb") as fh:
            fh.write(mutated)
        result = day_document.save(path, "2026-01-07",
                                   {"EMT": "ch 4"}, snap2["revision"])
        if result.get("status") != "conflict":
            fail("byte change did not conflict: %r" % result.get("status"))
        if open(path, "rb").read() != mutated:
            fail("byte-change conflict wrote to the file")


def check_task2_force_cli_gates():
    if day_document is None:
        fail("Task 2 RED: surfaces.day_document does not exist yet")
    with tempfile.TemporaryDirectory() as tmp:
        path = write_plan(tmp, [HEADER, row_for()])
        original = open(path, "rb").read()
        base = ["day", path, "--date", "2026-01-07", "--edit",
                "--set", "EMT=x"]

        code, out = run_cli(base + ["--revision", "a" * 64, "--force"])
        if code == 0:
            fail("--force alone was accepted")
        if "OVERWRITE" not in out:
            fail("--force alone did not name the required confirmation")

        code, out = run_cli(base + ["--revision", "a" * 64,
                                    "--confirm-force", "OVERWRITE"])
        if code == 0:
            fail("--confirm-force OVERWRITE alone was accepted")

        code, out = run_cli(base + ["--force", "--confirm-force", "OVERWRITE"])
        if code == 0:
            fail("--force without --revision was accepted")

        code, out = run_cli(base + ["--revision", "a" * 64,
                                    "--force", "--confirm-force", "wrong"])
        if code == 0:
            fail("a wrong confirmation word was accepted")

        if open(path, "rb").read() != original:
            fail("gated force attempts wrote to the file")
        if os.path.exists(path + ".tmp"):
            fail("gated force attempts left a temporary file")


def check_task2_confirmed_force():
    if day_document is None:
        fail("Task 2 RED: surfaces.day_document does not exist yet")
    with tempfile.TemporaryDirectory() as tmp:
        path = write_plan(tmp, [HEADER, row_for()])
        snap = day_document.snapshot(path, 2026, "2026-01-07")
        concurrent = plan_bytes(
            [HEADER, row_for(cells=("ch 2 finish", "changed by Obsidian", "Lab 0"))],
            prose=("Prose edited by Obsidian.",))
        with open(path, "wb") as fh:
            fh.write(concurrent)

        first = day_document.save(path, "2026-01-07",
                                  {"EMT": "ch 3"}, snap["revision"])
        if first.get("status") != "conflict":
            fail("stale save did not conflict: %r" % first.get("status"))

        forced = day_document.save(path, "2026-01-07", {"EMT": "ch 3"},
                                   first["revision"], force=True)
        if forced.get("status") != "saved":
            fail("confirmed force did not save: %r" % forced)
        after = open(path, "rb").read()
        if forced.get("revision") != sha256_bytes(after):
            fail("confirmed force returned a wrong revision")
        if b"changed by Obsidian" not in after:
            fail("confirmed force lost the concurrent Math edit")
        if b"Prose edited by Obsidian." not in after:
            fail("confirmed force lost the concurrent prose edit")
        if forced.get("cells", {}).get("EMT (top priority)") != "ch 3":
            fail("confirmed force did not apply the draft cell")

        snap3 = day_document.snapshot(path, 2026, "2026-01-07")
        third = plan_bytes(
            [HEADER, row_for(cells=("ch 3", "changed again", "Lab 0"))])
        with open(path, "wb") as fh:
            fh.write(third)
        replay = day_document.save(path, "2026-01-07", {"EMT": "ch 4"},
                                   snap3["revision"], force=True)
        if replay.get("status") != "conflict":
            fail("third-version replay was not refused: %r" % replay.get("status"))
        if open(path, "rb").read() != third:
            fail("third-version replay wrote to the file")
        if os.path.exists(path + ".tmp"):
            fail("third-version conflict left a temporary file")

        snap4 = day_document.snapshot(path, 2026, "2026-01-07")
        code, out = run_cli(["day", path, "--date", "2026-01-07", "--edit",
                             "--set", "EMT=ch 5", "--revision", snap4["revision"],
                             "--force", "--confirm-force", "OVERWRITE"])
        if code != 0:
            fail("CLI confirmed force exited %d: %s" % (code, out))
        cli = json.loads(out)
        if cli.get("status") != "saved":
            fail("CLI confirmed force status %r" % cli.get("status"))


def check_task2_draft_and_no_temp():
    if day_document is None:
        fail("Task 2 RED: surfaces.day_document does not exist yet")
    with tempfile.TemporaryDirectory() as tmp:
        path = write_plan(tmp, [HEADER, row_for()])
        before = open(path, "rb").read()
        snap = day_document.snapshot(path, 2026, "2026-01-07")
        result = day_document.save(path, "2026-01-07",
                                   {"EMT": "bad\nvalue"}, snap["revision"])
        if result.get("status") != "invalid":
            fail("invalid-value save status %r, want invalid" % result.get("status"))
        if result.get("draft") != {"EMT": "bad\nvalue"}:
            fail("invalid result lost the draft verbatim: %r" % result.get("draft"))
        if open(path, "rb").read() != before:
            fail("invalid result wrote to the file")
        if os.path.exists(path + ".tmp"):
            fail("invalid result left a temporary file")


def main():
    check_builders_and_corpus()
    check_byte_helpers()
    check_concurrent_and_cli_helpers()
    check_http_helper_refuses_closed_port()
    check_task1_snapshot_via_cli()
    check_task1_single_cell_edit()
    check_task1_preservation_corpus()
    check_task1_escape_survival_outside_edit()
    check_task1_refusals()
    check_task1_atomic_write()
    check_task2_conflict_no_write()
    check_task2_metadata_no_false_conflict()
    check_task2_force_cli_gates()
    check_task2_confirmed_force()
    check_task2_draft_and_no_temp()
    print("ok: day-edit plan 04-02 -- structured snapshot, exact-span edit, "
          "grammar refusals, atomic replace, stale conflicts, confirmed force "
          "all green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
