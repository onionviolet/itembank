"""Bring the history in: a one-time, re-runnable import from the three
pre-evidence stores (`_attempts/*.md`, session JSON, `daily_log.md`) into
`_evidence/evidence.jsonl`.

This module reads the legacy stores and never writes to them (D-11's rule
that a store `itembank migrate` brings in stays read-only from here on).
Every event it produces reaches the log through `evidence.append_event()`
alone, the same one writer every other surface uses (D-08) -- this tool
never calls `evidence.append_line`/`append_line_checked` directly.

**Deterministic identity (D-13).** Every source record maps to a
`dedupe_key` computed by `source_key(kind, path, ref)`, a sha256 digest of
the record's kind, its source file's basename, and a reference identifying
it within that file. This is what makes "a second run imports nothing new"
fall out of `evidence.append_event()`'s own idempotency check rather than
needing separate bookkeeping here: a migrated event's dedupe key means "this
source record", a different question from what the live path's dedupe key
means ("this attempt at this item in this session"). `mark` events reuse
`evidence.mark_event()`'s own dedupe key (already idempotent per D-12, over
session_id/marks_event/verdict/rubric) and `day_tick` events reuse
`evidence.day_tick_event()`'s own dedupe key (already idempotent per D-11,
over date/lane alone) -- neither needs the `source_key` override, because
neither is a `response` event whose natural dedupe key would otherwise
collide across unrelated migrated records (two different unresolved `short`
records from two different files can share an empty item key and an
identical answer canon; `source_key` keeps their identities apart).

**No resolution by default (D-14).** A legacy record keyed by a positional
reference (`q7`, item heading `9`) is imported with `item_id` of `""` and
`item_ref` set to the reference itself -- unresolved, counted, never
dropped. `--resolve-by-position BANK.md` is a separately-invoked opt-in that
matches a reference against *today's* bank by current item number; a
reference with no match stays unresolved even under this flag, and every
event this flag resolves records `source_ref.resolution = "position"` so
how it was attributed lives in the record, not in the operator's memory.
There is no stem-similarity path, deliberately, and none is to be added --
RESEARCH.md's Pitfall 3 names position-based "resolution" as exactly as
wrong as stem-similarity matching when a bank has been reordered since the
record was written.

**Dry run by default.** `cmd_migrate` scans, resolves, computes every event
and checks it against the existing log without appending anything unless
`--write` is given. The reconciliation it prints (`found` vs `written`) is
what makes "no recorded response lost" verifiable by a diff of two JSON
objects rather than a claim.
"""
import glob
import hashlib
import json
import os
import re
import sys

import model
import evidence
import surfaces.day as day


KNOWN_ITEM_TYPES = ("mc", "multi", "table", "dnd", "build", "short")


class MigrationScopeError(Exception):
    """Raised when `--legacy-dir` resolves outside `--base` (T-1-03)."""


def source_key(kind, path, ref):
    """A sha256 hex digest identifying one legacy source record: its kind
    (`attempt_md`, `session_json` or `daily_log`), its source file's
    **basename** (not the full path, so moving the legacy files around does
    not change their records' identity), and `ref`, which identifies the
    record within its file.

    This becomes the imported `response` event's `dedupe_key` (D-13).
    """
    raw = "%s|%s|%s" % (kind, os.path.basename(path), ref)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


# ---- attempt markdown reader -------------------------------------------------
# The pre-01-09 shape `surfaces/quiz.attempt_markdown` produced: one `## Item
# N, type` heading per section, an `[auto: correct]`/`[auto: WRONG]` suffix
# on an auto-scored item, a fenced verbatim block plus a hand-edited `MARK:`
# line on a `short` item.

_ATTEMPT_HEAD_RE = re.compile(
    r"^##\s+Item\s+(\d+),\s*(\w+)\s*(?:\[auto:\s*(correct|WRONG)\])?\s*$")
_OBJECTIVE_RE = re.compile(r"(?m)^\*Objective:\s*(.*?)\*\s*$")
_SELECTED_RE = re.compile(r"(?m)^\*\*Selected:\*\*\s*(.*)$")
_FENCE_RE = re.compile(r"```\n(.*?)\n```", re.S)
_MARK_RE = re.compile(r"(?m)^MARK:\s*\(?(pass|fail|unmarked)\)?", re.I)
_RUBRIC_BULLET_RE = re.compile(r"(?m)^-\s*\((pass|fail|unmarked)\)\s*(.+?)\s*$", re.I)


def read_attempt_md(path):
    """Every `## Item N, type` section in a pre-migration attempt file.

    Returns a list of dicts. A well-formed section carries `ref` (the
    heading's item number, a string), `item_ref` (`"q" + ref`, matching the
    positional-id shape every other reader/writer in this codebase uses),
    `type`, `objective`, `answer`, `score` (`True`/`False`/`None`), `mark`
    (`True`/`False`/`None` from the `MARK:` line) and `rubric` (a list of
    `{"point", "pass"}` for any bullet not left `(unmarked)`).

    A section whose heading does not match the expected shape, or whose
    type is not one this build recognizes, is recorded as `{"ref": ...,
    "unparsed": True}` and counted, never silently dropped -- D-09's
    per-line tolerance, extended to a per-section tolerance here, because a
    hand-edited legacy file is exactly the kind of malformed input D-09
    exists for.

    Never writes to `path`.
    """
    text = open(path, encoding="utf-8").read()
    blocks = re.split(r"(?m)^(?=##\s+Item\s)", text)
    records = []
    for block in blocks:
        if not block.startswith("## Item"):
            continue
        head_line = block.splitlines()[0].strip()
        m = _ATTEMPT_HEAD_RE.match(head_line)
        if not m:
            records.append({"ref": head_line[:120], "unparsed": True})
            continue
        ref, item_type, verdict = m.group(1), m.group(2).lower(), m.group(3)
        if item_type not in KNOWN_ITEM_TYPES:
            records.append({"ref": ref, "unparsed": True})
            continue

        om = _OBJECTIVE_RE.search(block)
        objective = om.group(1).strip() if om else ""

        score = None
        if verdict == "correct":
            score = True
        elif verdict == "WRONG":
            score = False

        mark = None
        mm = _MARK_RE.search(block)
        if mm:
            state = mm.group(1).lower()
            if state == "pass":
                mark = True
            elif state == "fail":
                mark = False

        rubric = []
        for bstate, point in _RUBRIC_BULLET_RE.findall(block):
            bstate = bstate.lower()
            if bstate != "unmarked":
                rubric.append({"point": point.strip(), "pass": bstate == "pass"})

        answer = ""
        sm = _SELECTED_RE.search(block)
        if sm:
            answer = sm.group(1).strip()
        else:
            fm = _FENCE_RE.search(block)
            if fm:
                answer = fm.group(1)

        records.append({
            "ref": ref, "item_ref": "q" + ref, "type": item_type,
            "objective": objective, "answer": answer, "score": score,
            "mark": mark, "rubric": rubric, "unparsed": False,
        })
    return records


# ---- legacy session JSON reader ---------------------------------------------

def read_legacy_session(path):
    """Every entry of a legacy session JSON's `responses` array, in file
    order.

    `ref` is `"<index>:<item_id>"` (the response's position in the array
    plus its positional `item_id`), so two responses to the same item
    within one legacy sitting -- a resubmit the old in-memory writer
    overwrote -- still get distinct source identities. `item_ref` is the
    response's own `item_id` alone (`"q7"`), matching an attempt file's
    `item_ref` shape.

    A response that is not a dict, carries no `item_id`, or names a `type`
    this build does not recognize is `{"ref": ..., "unparsed": True}`,
    counted rather than dropped. A file that fails to parse as JSON at all
    is one `{"ref": ..., "unparsed": True}` record naming the whole file.

    Never writes to `path`.
    """
    try:
        data = json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [{"ref": os.path.basename(path), "unparsed": True,
                 "file_error": str(exc)}]

    session_id = data.get("session_id") or (
        "legacy:" + os.path.splitext(os.path.basename(path))[0])
    mode = data.get("mode") or ""
    bank = data.get("bank") or ""

    records = []
    for idx, r in enumerate(data.get("responses") or []):
        if not isinstance(r, dict) or not r.get("item_id"):
            records.append({"ref": "%d" % idx, "unparsed": True})
            continue
        item_type = str(r.get("type") or "").lower()
        legacy_item_id = str(r["item_id"])
        if item_type not in KNOWN_ITEM_TYPES:
            records.append({"ref": "%d:%s" % (idx, legacy_item_id), "unparsed": True})
            continue
        records.append({
            "ref": "%d:%s" % (idx, legacy_item_id), "item_ref": legacy_item_id,
            "type": item_type, "objective": r.get("objective") or "",
            "answer": r.get("answer"), "score": r.get("score"),
            "session_id": session_id, "mode": mode, "bank": bank,
            "unparsed": False,
        })
    return records


# ---- scoping the inputs (T-1-03) --------------------------------------------

def scan_legacy(base, legacy_dir=None):
    """Resolve where the three legacy stores live.

    By default: `_attempts/` beside `base` (holding both attempt markdown
    and session JSON files, the same directory `surfaces/session.py` and
    `surfaces/quiz.py` already write into) and `daily_log.md` beside
    `base`. `--legacy-dir`, when given, overrides where attempts and
    session files are read from; it is resolved with `os.path.abspath` and
    rejected with `MigrationScopeError` unless it lies inside
    `os.path.abspath(base)` -- a migration tool handed an arbitrary path
    reads files it was never meant to see, the same documented-trust-
    boundary discipline `.planning/codebase/CONCERNS.md` already asks for
    around `surfaces/day.resolve_notes()`.

    Returns a dict: `attempts_dir`, `attempt_files` (sorted `*.md` under
    `attempts_dir`), `session_files` (sorted `*.json` under `attempts_dir`),
    and `daily_log` (the resolved path, or `None` if it does not exist).
    """
    base_abs = os.path.abspath(base)
    if legacy_dir:
        resolved = os.path.abspath(legacy_dir)
        if resolved != base_abs and not resolved.startswith(base_abs + os.sep):
            raise MigrationScopeError(
                "migrate: --legacy-dir %r resolves to %r, outside --base %r; "
                "migration inputs must stay inside the given base, never an "
                "arbitrary path (T-1-03)" % (legacy_dir, resolved, base_abs))
        attempts_dir = resolved
    else:
        attempts_dir = os.path.join(base_abs, "_attempts")

    daily_log_path = os.path.join(base_abs, "daily_log.md")
    attempt_files = (sorted(glob.glob(os.path.join(attempts_dir, "*.md")))
                     if os.path.isdir(attempts_dir) else [])
    session_files = (sorted(glob.glob(os.path.join(attempts_dir, "*.json")))
                     if os.path.isdir(attempts_dir) else [])
    return {
        "attempts_dir": attempts_dir,
        "attempt_files": attempt_files,
        "session_files": session_files,
        "daily_log": daily_log_path if os.path.isfile(daily_log_path) else None,
    }


# ---- building and checking events -------------------------------------------

_ATTEMPT_FILENAME_RE = re.compile(r"^(.*)_attempt_\d{4}-\d{2}-\d{2}_\d{4}$")


def _bank_from_attempt_filename(path):
    """`sample_bank_attempt_2026-01-02_0900.md` -> `sample_bank.md`, the
    same naming `surfaces/quiz.cmd_serve` writes; `None` when the filename
    does not match that shape.
    """
    stem = os.path.splitext(os.path.basename(path))[0]
    m = _ATTEMPT_FILENAME_RE.match(stem)
    return (m.group(1) + ".md") if m else None


def _namespace_objective(objective, subject):
    """`--subject` prefixes `"<subject>:"` onto a non-empty objective that
    carries no colon (D-06). Without the flag, an unnamespaced objective
    imports exactly as written; `item.objective_unnamespaced` is what
    surfaces it later.
    """
    objective = objective or ""
    if subject and objective and ":" not in objective:
        return "%s:%s" % (subject, objective)
    return objective


def _migrated_canon(answer):
    """A migrated event's `canonical` field: a stable hash of the recorded
    answer text, never `runtime.canonical_response()`'s own output.

    An unresolved (or even a resolved-by-position) migrated record does not
    carry the full item metadata `canonical_response()` needs for every
    type (a `table`/`dnd` answer needs the item's row count to validate
    against, which a rendered attempt file's text never preserves). This
    field's job for a migrated event is D-17's spirit -- "what did the
    answer look like" -- not scoring compatibility with the live path,
    since a migrated event's `score` is taken directly from the source,
    never recomputed. Never `None`.
    """
    if isinstance(answer, str):
        text = answer
    else:
        text = json.dumps(answer, ensure_ascii=False, sort_keys=True)
    return "migrated:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def _build_response_event(kind, path, ref, session_id, item_ref, item_type,
                           objective, subject, answer, score, mode, bank_name,
                           resolution, item_id):
    """One migrated `response` event. `attempt_number` is fixed at `1` for
    every migrated record (a documented, deliberate simplification: a
    legacy store never captured which attempt a response was, and guessing
    would manufacture a number a later trend query would read as real).
    `response_time_ms`/`confidence`/`error_category`/`hint_tier` are always
    `None`, the same option-a posture 01-02 already took for a field with
    no capture point -- recording a fabricated value here would be worse
    evidence than an honest null.
    """
    objective = _namespace_objective(objective, subject)
    return {
        "schema_version": evidence.EVENT_SCHEMA_VERSION,
        "event_id": evidence.new_event_id(),
        "event_type": evidence.RESPONSE_EVENT_TYPE,
        "ts": evidence.utc_now(),
        "session_id": session_id,
        "item_id": item_id,
        "item_ref": item_ref,
        "item_type": item_type,
        "bank": bank_name,
        "objective": objective,
        "subject": evidence.subject_of(objective),
        "mode": mode or "legacy",
        "attempt_number": 1,
        "answer": answer,
        "canonical": _migrated_canon(answer),
        "score": score,
        "response_time_ms": None,
        "confidence": None,
        "error_category": None,
        "check_source": None,       # reserved; a migrated record predates code items (05-01)
        "interaction_version": None,   # reserved; a migrated record predates the interaction contract (05-01)
        "hint_tier": None,
        "review_state": "pending" if item_type == "short" else "n/a",
        "dedupe_key": source_key(kind, path, ref),
        "source_ref": {"kind": kind, "path": os.path.basename(path), "ref": ref,
                       "resolution": resolution},
    }


def _check_or_write(log, event, write, seen):
    """Classify `event` as `recorded` or `already_recorded` against `seen`
    (a dedupe_key -> event_id map, seeded from `evidence.recent_dedupe_keys`
    and updated as this run proceeds) without necessarily appending it.

    `write` is `False` for a dry run: the event is classified exactly as it
    would be for real (so the dry run's reconciliation matches a real run's
    one-for-one), but nothing reaches `evidence.append_event`. `write` is
    `True` for a real run: `evidence.append_event` is the one writer this
    goes through, same as every other surface (D-08).
    """
    dk = event.get("dedupe_key")
    if dk in seen:
        return {"accepted": False, "status": "already_recorded", "event_id": seen[dk]}
    if write:
        result = evidence.append_event(log, event)
    else:
        result = {"accepted": True, "status": "recorded", "event_id": event["event_id"]}
    seen[dk] = result["event_id"]
    return result


def cmd_migrate(a):
    """The one-shot, re-runnable migration (D-13). A dry run by default;
    `--write` is what actually imports. Prints the house-style status lines
    and a JSON reconciliation object (`found`, `written`, `unresolved_refs`)
    so the pre/post comparison the phase's success criterion asks for is a
    diff of two JSON objects.
    """
    try:
        scope = scan_legacy(a.base, a.legacy_dir)
    except MigrationScopeError as exc:
        sys.exit(str(exc))

    resolve_map = {}
    if a.resolve_by_position:
        for q in model.load(a.resolve_by_position):
            resolve_map[q["id"]] = q

    def resolve(item_ref):
        if not resolve_map:
            return "", "unresolved"
        q = resolve_map.get(item_ref)
        if q and q.get("item_id"):
            return q["item_id"], "position"
        return "", "unresolved"

    log = evidence.log_path(a.base)
    seen = dict(evidence.recent_dedupe_keys(log))
    fallback_bank = os.path.basename(a.bank) if a.bank else ""

    found = {"attempt_md": 0, "session_json": 0, "daily_log": 0}
    written = {"resolved": 0, "unresolved": 0, "unparsed": 0,
               "ticks": 0, "marks": 0, "already_present": 0}
    unresolved_refs = []

    for path in scope["attempt_files"]:
        session_id = "legacy:" + os.path.splitext(os.path.basename(path))[0]
        bank_name = (_bank_from_attempt_filename(path) or fallback_bank
                    or "unknown_bank.md")
        for rec in read_attempt_md(path):
            found["attempt_md"] += 1
            if rec.get("unparsed"):
                written["unparsed"] += 1
                continue
            item_id, resolution = resolve(rec["item_ref"])
            if resolution == "unresolved":
                unresolved_refs.append({"kind": "attempt_md",
                                        "path": os.path.basename(path),
                                        "ref": rec["item_ref"]})
            event = _build_response_event(
                "attempt_md", path, rec["ref"], session_id, rec["item_ref"],
                rec["type"], rec["objective"], a.subject, rec["answer"],
                rec["score"], "legacy", bank_name, resolution, item_id)
            result = _check_or_write(log, event, a.write, seen)
            if result["status"] == "already_recorded":
                written["already_present"] += 1
            elif resolution == "position":
                written["resolved"] += 1
            else:
                written["unresolved"] += 1

            if rec.get("mark") is not None:
                mark_ev = evidence.mark_event(
                    session_id, item_id, rec["item_ref"], result["event_id"],
                    rec["mark"], rubric=rec.get("rubric") or [])
                mark_result = _check_or_write(log, mark_ev, a.write, seen)
                if mark_result["status"] == "recorded":
                    written["marks"] += 1

    for path in scope["session_files"]:
        for rec in read_legacy_session(path):
            found["session_json"] += 1
            if rec.get("unparsed"):
                written["unparsed"] += 1
                continue
            item_id, resolution = resolve(rec["item_ref"])
            if resolution == "unresolved":
                unresolved_refs.append({"kind": "session_json",
                                        "path": os.path.basename(path),
                                        "ref": rec["item_ref"]})
            bank_name = (os.path.basename(rec["bank"]) if rec.get("bank")
                        else (fallback_bank or "unknown_bank.md"))
            event = _build_response_event(
                "session_json", path, rec["ref"], rec["session_id"],
                rec["item_ref"], rec["type"], rec["objective"], a.subject,
                rec["answer"], rec["score"], rec.get("mode") or "legacy",
                bank_name, resolution, item_id)
            result = _check_or_write(log, event, a.write, seen)
            if result["status"] == "already_recorded":
                written["already_present"] += 1
            elif resolution == "position":
                written["resolved"] += 1
            else:
                written["unresolved"] += 1

    if scope["daily_log"]:
        # Read through surfaces.day.load_day_log rather than a second table
        # parser; a day_tick_event() per (date, lane) already-done pair,
        # which is what load_day_log's own {date: set-of-lanes} mapping
        # enumerates. day_tick_event()'s own dedupe_key (date, lane alone)
        # is reused unmodified: it is already idempotent per D-11, and it
        # also naturally reconciles against a lane already ticked live
        # through `itembank day` since plan 01-10, which is a feature, not
        # a residual to work around.
        tick_log = day.load_day_log(scope["daily_log"])
        for iso in sorted(tick_log):
            for lane in sorted(tick_log[iso]):
                found["daily_log"] += 1
                event = evidence.day_tick_event(iso, lane, source="migrate")
                result = _check_or_write(log, event, a.write, seen)
                if result["status"] == "already_recorded":
                    written["already_present"] += 1
                else:
                    written["ticks"] += 1

    total_found = sum(found.values())
    total_accounted = (written["resolved"] + written["unresolved"] +
                       written["unparsed"] + written["ticks"] +
                       written["already_present"])

    print("found:  %(attempt_md)d attempt-file answers, %(session_json)d session "
          "responses, %(daily_log)d day-log ticks" % found)
    verb = "wrote" if a.write else "would write"
    print("%s: %d resolved, %d unresolved, %d unparsed, %d ticks, "
          "%d already present, %d marks" %
          (verb, written["resolved"], written["unresolved"], written["unparsed"],
           written["ticks"], written["already_present"], written["marks"]))

    if total_found != total_accounted:
        print("error  migration count mismatch: found %d, accounted for %d "
              "(marks are additional events attached to an already-counted "
              "record, never separately found, so this must never happen)" %
              (total_found, total_accounted))
        sys.exit(1)

    payload = {"schema_version": 1, "dry_run": not bool(a.write),
              "found": found, "written": written,
              "unresolved_refs": unresolved_refs}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0
