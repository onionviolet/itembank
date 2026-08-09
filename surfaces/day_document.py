"""The day-document adapter: lossless structured edits to one dated plan row.

Phase 4 (plan 04-02) proves the data-loss boundary for in-page day editing
before any browser wiring: the CLI twin reads a dated plan row as structured
cell values, patches exact UTF-8 cell spans, refuses every table shape the
UI-SPEC calls unsupported, and writes only through a same-directory
temporary file plus fsync and `os.replace` (D-08 through D-11).

The adapter is deliberately NOT a second Markdown parser. It reuses
`day.parse_day_date` and `day.lane_for_header` for semantic identification,
and it tracks byte offsets so everything outside a submitted cell -- prose,
unknown columns, unrelated tables, line endings, padding, escaped pipes,
inline-code pipes -- survives byte-for-byte. It never serializes the
document: a successful save is a set of exact-span replacements applied in
descending byte-offset order, nothing more.

Status contract (stable for plan 04-06's browser editor):

- `snapshot(path, year, iso)` -> ready snapshot, or invalid/unsupported
- `save(path, iso, edits, revision, force=False)` -> saved, or
  invalid/unsupported/conflict. Invalid and conflict results carry the
  submitted `draft`; conflict additionally carries the fresh `current`
  snapshot, and neither branch ever writes a byte.
"""
import hashlib, os, re

from surfaces import day


RULE_RE = re.compile(r"^:?-{2,}:?$")
CONTROL_RE = re.compile(r"[\x00-\x1f\x7f]")


class StaleRevisionError(Exception):
    """Raised when the target changed between `save`'s first read and replace.

    Carries the freshly read bytes so the caller can build a conflict result
    without a third read.
    """

    def __init__(self, current_bytes):
        super().__init__("plan changed on disk during the save")
        self.current_bytes = current_bytes


# ---- reading and line structure --------------------------------------------

def _read_plan(path):
    """Read the plan as raw bytes plus its UTF-8 text and SHA-256 revision.

    Returns (data, text, revision, error); exactly one of text/revision and
    error is meaningful on any given return.
    """
    try:
        data = open(path, "rb").read()
    except OSError as exc:
        return None, "", "", "cannot read plan: %s" % exc
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        return data, "", hashlib.sha256(data).hexdigest(), (
            "plan is not valid UTF-8: %s" % exc)
    return data, text, hashlib.sha256(data).hexdigest(), None


def _split_lines(data):
    """Yield (line_bytes, start, end) for every line; `end` includes the newline."""
    start = 0
    n = len(data)
    while start < n:
        nl = data.find(b"\n", start)
        if nl == -1:
            yield data[start:], start, n
            return
        yield data[start:nl], start, nl + 1
        start = nl + 1


def _strip_cr(line):
    return line[:-1] if line.endswith(b"\r") else line


def _scan_line(line):
    """Split one pipe-table row line into cells without touching escapes.

    Returns (cells, separators, error). `cells` is a list of
    (content_start, content_end, raw_bytes) spans relative to the line, with
    padding trimmed; `separators` is how many unescaped, non-code pipes the
    line carries; `error` is None or a reason string for an unclosed code
    span or a dangling escape.

    Escaped pipes (`\\|`) and pipes inside closed inline-code spans are data
    inside the cell: the scanner skips them, so they can never split a row
    into phantom columns.
    """
    n = len(line)
    in_code = False
    escaped = False
    seps = []
    i = 0
    while i < n:
        b = line[i:i + 1]
        if escaped:
            escaped = False
            i += 1
            continue
        if not in_code and b == b"\\":
            escaped = True
            i += 1
            continue
        if b == b"`":
            in_code = not in_code
            i += 1
            continue
        if not in_code and b == b"|":
            seps.append(i)
        i += 1
    if in_code:
        return None, 0, "unclosed inline-code span"
    if escaped:
        return None, 0, "dangling escape at end of line"

    bounds = []
    prev = 0
    for p in seps:
        bounds.append((prev, p))
        prev = p + 1
    bounds.append((prev, n))
    # Optional outer pipes: drop the empty region before a leading pipe and
    # the whitespace-only region after the last separator when the row really
    # ends with a closing pipe (never when the last character is an escaped
    # pipe, which is cell data).
    if line.lstrip().startswith(b"|"):
        bounds.pop(0)
    if seps and line[seps[-1] + 1:].strip(b" \t") == b"":
        bounds.pop()

    cells = []
    for start, end in bounds:
        s, e = start, end
        while s < e and line[s:s + 1] in (b" ", b"\t"):
            s += 1
        while e > s and line[e - 1:e] in (b" ", b"\t"):
            e -= 1
        cells.append((s, e, line[s:e]))
    return cells, len(seps), None


def _is_table_line(line):
    cells, seps, err = _scan_line(_strip_cr(line))
    if err:
        # An ambiguous span still groups the line as table content so the
        # block-level analysis can refuse it as unsupported.
        return b"|" in line
    return seps > 0


def _is_rule_row(cells):
    if not cells:
        return False
    texts = [c[2].decode("utf-8") for c in cells]
    return bool(texts) and all(RULE_RE.match(t) for t in texts if t)


def _table_blocks(lines):
    """Group consecutive table-ish lines into blocks of (line, start, end)."""
    blocks, cur = [], []
    for line, start, end in lines:
        if _is_table_line(line):
            cur.append((line, start, end))
        else:
            if cur:
                blocks.append(cur)
                cur = []
    if cur:
        blocks.append(cur)
    return blocks


def _row_date(row, year):
    if not row["cells"]:
        return ""
    return day.parse_day_date(row["cells"][0][2].decode("utf-8"), year)


def _display(raw):
    """Cell bytes as a learner sees them: `\\|` -> `|`, `\\\\` -> `\\`."""
    text = raw.decode("utf-8")
    out = []
    i, n = 0, len(text)
    while i < n:
        if text[i] == "\\" and i + 1 < n and text[i + 1] in ("\\", "|"):
            out.append(text[i + 1])
            i += 2
        else:
            out.append(text[i])
            i += 1
    return "".join(out)


def _encode(value):
    """Submitted display text as safe cell bytes: `\\` -> `\\\\`, `|` -> `\\|`.

    Escaping backslashes first keeps `\\|` and `|` unambiguous, so
    `_display(_encode(value)) == value` always holds.
    """
    out = []
    for ch in value:
        if ch == "\\":
            out.append("\\\\")
        elif ch == "|":
            out.append("\\|")
        else:
            out.append(ch)
    return "".join(out).encode("utf-8")


def _apply_spans(data, edits):
    """Apply (start, end, replacement_bytes) triples in descending order."""
    out = bytearray(data)
    for start, end, replacement in sorted(edits, key=lambda e: e[0], reverse=True):
        out[start:end] = replacement
    return bytes(out)


# ---- analysis ---------------------------------------------------------------

def _build_snapshot(internals, iso, revision, text):
    header = internals["header"]
    columns = [_display(c[2]) for c in header["cells"]]
    row = internals["rows"][internals["match_idx"]]
    cells = {}
    for i, cell in enumerate(row["cells"]):
        if i == 0:
            continue                      # the date is the row key, not a lane
        if i < len(columns):
            cells[columns[i]] = _display(cell[2])
    return {"status": "ready", "revision": revision, "date": iso,
            "columns": columns, "cells": cells, "document": text}


def _conflict_result(edits, submitted_revision, data, iso, forced):
    """A no-write conflict carrying draft, fresh current data, both revisions."""
    revision = hashlib.sha256(data).hexdigest()
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        # A concurrent edit can land non-UTF-8 bytes between the read and
        # the atomic replace; the conflict document is display/copy text only
        # and is never written back, so a lossy decode there is safe and the
        # advertised no-write recovery UI still appears (WR-02).
        text = data.decode("utf-8", errors="replace")
    result, internals = _analyze(data, int(iso[:4]), iso)
    if result["status"] == "ready":
        current = _build_snapshot(internals, iso, revision, text)
    else:
        current = {"status": result["status"], "reason": result["reason"],
                   "revision": revision, "date": iso, "document": text}
    return {"status": "conflict",
            "reason": "plan changed on disk since revision %s; nothing "
                      "was overwritten" % submitted_revision,
            "draft": edits, "revision": revision,
            "submitted_revision": submitted_revision, "current": current,
            "document": text, "forced": bool(forced)}


def _analyze(data, year, iso):
    """Locate the one unambiguous dated row and build its snapshot.

    Returns (public_result, internals). `internals` carries the header and
    the data rows with their absolute byte offsets so `save` can patch exact
    spans without re-parsing; it is None unless status is `ready`.
    """
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        return {"status": "unsupported",
                "reason": "plan is not valid UTF-8: %s" % exc}, None
    html_seen = any(t in data.lower() for t in (b"<table", b"<tr", b"<td"))
    blocks = _table_blocks(list(_split_lines(data)))
    if not blocks:
        if html_seen:
            return {"status": "unsupported",
                    "reason": "HTML tables are not supported; edit this plan "
                              "in your Markdown editor"}, None
        return {"status": "invalid",
                "reason": "no dated plan table found for %s" % iso}, None

    for block in blocks:
        for line, _start, _end in block:
            _cells, _seps, err = _scan_line(_strip_cr(line))
            if err:
                return {"status": "unsupported",
                        "reason": "%s makes the plan table ambiguous" % err}, None

    parsed = []
    for block in blocks:
        rows = []
        for line, start, _end in block:
            cells, _seps, _err = _scan_line(_strip_cr(line))
            rows.append({"line": line, "abs_start": start, "cells": cells})
        rule_idx = None
        for i, r in enumerate(rows):
            if _is_rule_row(r["cells"]):
                rule_idx = i
                break
        if rule_idx is None:
            if len(rows) >= 2:
                parsed.append({"kind": "missing-rule", "rows": rows})
            continue
        if rule_idx == 0:
            parsed.append({"kind": "missing-header", "rows": rows})
            continue
        parsed.append({"kind": "table", "rows": rows, "header": rows[0],
                       "data_rows": rows[rule_idx + 1:]})

    matching = []
    for entry in parsed:
        if entry["kind"] != "table":
            continue
        matched = [i for i, r in enumerate(entry["data_rows"])
                   if _row_date(r, year) == iso]
        if matched:
            matching.append((entry, matched))

    if len(matching) > 1:
        return {"status": "invalid",
                "reason": "multiple plan tables contain a dated row for %s; "
                          "edit the ambiguous table in your Markdown editor" % iso}, None
    if len(matching) == 1:
        entry, matched = matching[0]
        if len(matched) > 1:
            return {"status": "invalid",
                    "reason": "duplicate dated rows for %s; the plan table "
                              "must name each date once" % iso}, None
        ncols = len(entry["header"]["cells"])
        for r in entry["data_rows"]:
            if len(r["cells"]) != ncols:
                return {"status": "invalid",
                        "reason": "a row has %d cells but the header has %d; "
                                  "multiline cells and ragged rows are "
                                  "read-only here" % (len(r["cells"]), ncols)}, None
        internals = {"header": entry["header"], "rows": entry["data_rows"],
                     "match_idx": matched[0]}
        result = _build_snapshot(internals, iso,
                                 hashlib.sha256(data).hexdigest(), text)
        return result, internals

    for entry in parsed:
        if entry["kind"] == "missing-rule":
            return {"status": "invalid",
                    "reason": "the plan table is missing its delimiter/rule "
                              "row; edit it in your Markdown editor"}, None
    for entry in parsed:
        if entry["kind"] == "missing-header":
            return {"status": "invalid",
                    "reason": "the plan table is missing its header row; edit "
                              "it in your Markdown editor"}, None
    if html_seen:
        return {"status": "unsupported",
                "reason": "HTML tables are not supported; edit this plan in "
                          "your Markdown editor"}, None
    return {"status": "invalid",
            "reason": "no dated row for %s in the plan table" % iso}, None


# ---- the stable public contract --------------------------------------------

def snapshot(path, year, iso):
    """Return the structured dated-row snapshot for `iso`, or a refusal."""
    data, text, revision, err = _read_plan(path)
    if err:
        return {"status": "unsupported", "reason": err}
    result, _internals = _analyze(data, year, iso)
    if result["status"] != "ready":
        result["revision"] = revision
        result["document"] = text
        return result
    return result


def save(path, iso, edits, revision, force=False):
    """Patch only the submitted cells against the current bytes (D-08..D-11).

    Every save re-reads the full target bytes and compares their SHA-256 to
    the submitted `revision` immediately before patching; a mismatch returns
    a no-write `conflict` carrying both the draft and the fresh current
    snapshot. A confirmed force (`force=True`) still requires the conflict's
    current revision and still fails if the file changed a third time --
    force is a second explicit confirmation, never a bypass of the byte gate.
    """
    data, text, rev, err = _read_plan(path)
    if err:
        return {"status": "unsupported", "reason": err, "draft": edits}

    for column, value in edits.items():
        if not isinstance(value, str) or CONTROL_RE.search(value):
            return {"status": "invalid",
                    "reason": "cell value for %r contains a newline or "
                              "control character; keep cell values on one line"
                              % column,
                    "draft": edits, "revision": rev, "document": text}

    result, internals = _analyze(data, int(iso[:4]), iso)
    if result["status"] != "ready":
        result["draft"] = edits
        result["revision"] = rev
        result["document"] = text
        return result

    if rev != revision:
        return _conflict_result(edits, revision, data, iso, force)

    columns = [_display(c[2]) for c in internals["header"]["cells"]]
    exact, lanes = {}, {}
    for i, label in enumerate(columns):
        if i == 0:
            continue
        exact.setdefault(label, i)
        lane = day.lane_for_header(label)
        if lane:
            lanes.setdefault(lane, i)

    resolved = []
    for key, value in edits.items():
        idx = exact.get(key)
        if idx is None:
            candidates = [j for lane, j in lanes.items() if lane == key]
            if len(candidates) != 1:
                return {"status": "invalid",
                        "reason": "unknown plan column %r (known columns: %s)"
                                  % (key, ", ".join(columns)),
                        "draft": edits, "revision": rev, "document": text}
            idx = candidates[0]
        if idx == 0:
            return {"status": "invalid",
                    "reason": "the date column is the row key and is not "
                              "editable",
                    "draft": edits, "revision": rev, "document": text}
        resolved.append((idx, value))

    row = internals["rows"][internals["match_idx"]]
    spans = []
    for idx, value in resolved:
        s, e, _raw = row["cells"][idx]
        spans.append((row["abs_start"] + s, row["abs_start"] + e,
                      _encode(value)))
    new_bytes = _apply_spans(data, spans)

    # The edited bytes must still be a supported table: refuse the save if
    # the submitted text would brick the document (e.g. an unclosed code
    # span), keeping the draft intact and the file untouched.
    new_result, new_internals = _analyze(new_bytes, int(iso[:4]), iso)
    if new_result["status"] != "ready":
        return {"status": "invalid",
                "reason": "the edited value would make the plan table "
                          "unreadable: %s" % new_result["reason"],
                "draft": edits, "revision": rev, "document": text}

    try:
        _atomic_replace(path, new_bytes, rev)
    except StaleRevisionError as stale:
        # D-09: the revision check happens immediately before replacement.
        # A write that landed in the analysis window is never overwritten.
        return _conflict_result(edits, revision, stale.current_bytes, iso, force)
    new_rev = hashlib.sha256(new_bytes).hexdigest()
    saved_cells = _build_snapshot(new_internals, iso, new_rev,
                                  new_bytes.decode("utf-8"))["cells"]
    return {"status": "saved", "revision": new_rev, "date": iso,
            "cells": saved_cells, "document": new_bytes.decode("utf-8"),
            "forced": bool(force)}


def _atomic_replace(path, data, expected_rev):
    """Fresh-read revision gate plus same-directory atomic replace (D-09, D-11)."""
    try:
        current = open(path, "rb").read()
    except OSError:
        current = b""
    if hashlib.sha256(current).hexdigest() != expected_rev:
        raise StaleRevisionError(current)
    tmp = path + ".tmp"
    with open(tmp, "wb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)
    # Best-effort directory fsync so the rename itself is durable on POSIX;
    # Windows cannot open a directory for fsync and that is fine -- the file
    # bytes are already flushed before the replace.
    try:
        fd = os.open(os.path.dirname(os.path.abspath(path)) or ".", os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    except OSError:
        pass
