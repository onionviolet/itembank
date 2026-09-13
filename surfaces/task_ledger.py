"""Owner-backed assignment rows for the Day surface.

The vault ledger remains canonical. This adapter reads its existing Markdown
table in place and changes only the Status cell through the shared operation
journal. It never creates an Itembank task database or evidence event.
"""
import hashlib
import os
import re
from datetime import date, timedelta

import identity
import journal
from surfaces import day_document


REQUIRED = ("id", "type", "title", "source", "assigned", "due", "status", "link")
DONE_RE = re.compile(r"^done(?:\s+\d{4}-\d{2}-\d{2})?$", re.I)
COURSE_RE = re.compile(r"<!--\s*course:\s*(.*?)\s*-->", re.I)
PURPOSES = {
    "reading": "Prepare for the assigned class or discussion",
    "homework": "Complete the instructor-assigned work",
    "quiz": "Demonstrate current course understanding",
    "exam": "Complete the scheduled course assessment",
    "project": "Advance the assigned course project",
    "lab": "Complete the assigned practical work",
}


def _revision(raw):
    return identity.object_fingerprint(raw, "component")


def _clean_header(value):
    return re.sub(r"[^a-z]", "", value.lower())


def _read(path):
    try:
        raw = open(path, "rb").read()
    except OSError as exc:
        return None, "owner unavailable: %s" % exc
    try:
        raw.decode("utf-8")
    except UnicodeDecodeError:
        return None, "owner is not valid UTF-8"
    return raw, None


def _rows(path, raw):
    text = raw.decode("utf-8")
    course_match = COURSE_RE.search(text)
    course = course_match.group(1).strip() if course_match else \
        os.path.basename(path).replace("_Assignments.md", "").replace("_", " ")
    lines = list(day_document._split_lines(raw))
    tables = day_document._table_blocks(lines)
    matches = []
    problems = []
    for block in tables:
        parsed = []
        for line, start, end in block:
            cells, _, error = day_document._scan_line(day_document._strip_cr(line))
            if error:
                problems.append("line %d: malformed table row (%s)" %
                                (raw[:start].count(b"\n") + 1, error))
                continue
            if day_document._is_rule_row(cells):
                continue
            parsed.append((line, start, end, cells))
        if not parsed:
            continue
        header = [day_document._display(c[2]) for c in parsed[0][3]]
        normalized = tuple(_clean_header(h) for h in header)
        if normalized != REQUIRED:
            continue
        for line, start, end, cells in parsed[1:]:
            line_no = raw[:start].count(b"\n") + 1
            if len(cells) != len(REQUIRED):
                problems.append("line %d: assignment row has %d cells, expected %d" %
                                (line_no, len(cells), len(REQUIRED)))
                continue
            values = [day_document._display(c[2]).strip() for c in cells]
            row = dict(zip(REQUIRED, values))
            if not row["id"] or not row["title"]:
                problems.append("line %d: assignment row needs ID and Title" % line_no)
                continue
            if row["due"]:
                try:
                    date.fromisoformat(row["due"])
                except ValueError:
                    problems.append("line %d: invalid Due date %r" %
                                    (line_no, row["due"]))
                    continue
            if row["assigned"]:
                try:
                    date.fromisoformat(row["assigned"])
                except ValueError:
                    problems.append("line %d: invalid Assigned date %r" %
                                    (line_no, row["assigned"]))
                    continue
            row.update({"course": course, "line": line_no,
                        "status_span": (start + cells[6][0], start + cells[6][1])})
            matches.append(row)
    if not matches and not problems:
        problems.append("no assignment ledger table with the required columns")
    return matches, problems


def _bucket(row, today):
    if row["due"]:
        due = date.fromisoformat(row["due"])
        if not DONE_RE.match(row["status"]) and due <= today:
            return "Now"
        if not DONE_RE.match(row["status"]) and due <= today + timedelta(days=7):
            return "Next"
    return "Later"


def snapshot(paths, iso):
    """Return ranked tasks plus honest per-owner unavailable/malformed states."""
    today = date.fromisoformat(iso)
    tasks = []
    issues = []
    for path in paths:
        full = os.path.abspath(path)
        raw, error = _read(full)
        if error:
            issues.append({"owner": full, "state": "unavailable", "reason": error})
            continue
        rows, problems = _rows(full, raw)
        for problem in problems:
            issues.append({"owner": full, "state": "malformed", "reason": problem})
        revision = _revision(raw)
        for row in rows:
            checked = bool(DONE_RE.match(row["status"]))
            due_label = "Due date unknown"
            if row["due"]:
                due = date.fromisoformat(row["due"])
                delta = (due - today).days
                due_label = ("Overdue by %d day%s" % (-delta, "" if delta == -1 else "s")
                             if delta < 0 and not checked else
                             "Due today" if delta == 0 else
                             "Due %s" % row["due"])
            task_id = hashlib.sha256((os.path.realpath(full) + "\0" + row["id"])
                                     .encode("utf-8")).hexdigest()[:24]
            tasks.append({
                "task_id": task_id, "owner_id": row["id"], "name": row["title"],
                "course": row["course"], "type": row["type"], "source": row["source"],
                "assigned": row["assigned"], "due": row["due"],
                "due_label": due_label, "status": row["status"], "checked": checked,
                "estimate": "Not provided", "purpose": PURPOSES.get(
                    row["type"].lower(), "Complete the declared course obligation"),
                "completion_gate": "Ledger Status is done with the completion date",
                "owner": full, "revision": revision, "bucket": _bucket(row, today),
                "line": row["line"],
            })
    order = {"Now": 0, "Next": 1, "Later": 2}
    tasks.sort(key=lambda task: (order[task["bucket"]], task["checked"],
                                 task["due"] or "9999-12-31", task["course"],
                                 task["name"]))
    return {"tasks": tasks, "issues": issues, "owners": list(paths)}


def set_checked(task, checked, expected_revision, iso):
    """Update exactly one current Status cell, or return a no-write refusal."""
    path = task["owner"]
    raw, error = _read(path)
    if error:
        return {"status": "unavailable", "reason": error}
    current_revision = _revision(raw)
    if current_revision != expected_revision:
        return {"status": "conflict", "reason": "owner changed outside itembank; nothing was overwritten",
                "revision": current_revision}
    rows, problems = _rows(path, raw)
    if problems:
        return {"status": "malformed", "reason": problems[0]}
    matches = [row for row in rows if row["id"] == task["owner_id"]]
    if len(matches) != 1:
        return {"status": "conflict", "reason": "assignment identity is missing or ambiguous; nothing was overwritten"}
    row = matches[0]
    current_checked = bool(DONE_RE.match(row["status"]))
    if current_checked == bool(checked):
        return {"status": "unchanged", "checked": current_checked,
                "revision": current_revision}
    replacement = ("done %s" % iso if checked else "planned").encode("utf-8")
    new_raw = day_document._apply_spans(
        raw, [(row["status_span"][0], row["status_span"][1], replacement)])
    base = os.path.dirname(path) or "."
    rel_path = os.path.basename(path)
    object_id = "assignment-ledger:" + hashlib.sha256(
        os.path.realpath(path).encode("utf-8")).hexdigest()[:24]
    try:
        record = journal.commit_operation(
            base, object_id, "component", rel_path, "edit_in_place", new_raw,
            current_revision, "human", "day-task", note=(
                "%s assignment %s" % ("completed" if checked else "reopened",
                                        row["id"])))
    except journal.JournalError as exc:
        state = "conflict" if exc.code in ("journal.conflict", "journal.stale_preflight") \
            else "unavailable"
        return {"status": state, "reason": str(exc)}
    entry_id = journal.read_registry(base)[object_id]["last_entry_id"]
    return {"status": "saved", "checked": bool(checked),
            "revision": record["fingerprint"], "entry_id": entry_id}
