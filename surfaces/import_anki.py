"""Anki .apkg import: container reader, note-type mapper, lint gate, per-note report.

The importer is a client of the one parser/validator: every candidate item is a
`model.parse_question()`-shaped dict and is run through `model.lint()` before it
may be reported as convertible -- nothing is written without passing the same
lint the human authoring path uses (D-05). It never writes to a bank directly
(D-06): this module assembles candidates and the report, and the CLI stages the
lint-clean candidates for plan 03.2-03's human-accept loop, never a bank write.

Container. An .apkg is a ZIP whose collection member is either a plain SQLite
file (`collection.anki21`, or the legacy `collection.anki2`) or a zstd-
compressed SQLite file (`collection.anki21b`, Anki 2.1.50+). Legacy members open
through stdlib `sqlite3` with zero extra dependencies. The modern member decodes
through the single pinned, checksummed, license-reviewed dependency `zstandard`
(03.2-RESEARCH section 1, Directive 4a), imported conditionally so the legacy
path never touches it. A missing or invalid container, or a collection member
that cannot be read, fails with a named error naming the file -- never a silent
empty import.

Note-type mapping (`anki_note_type_map`). Known Anki note types map to itembank
item types by name (case-insensitive), documented here:

    Basic, Basic (and reversed card), Basic (optional reversed card)  ->  mc
        Front becomes the stem. Option lines (`A) ...`-shaped) and a
        `CORRECT:` line, wherever the author put them in the note's fields,
        become the option set and the key.
    Cloze  ->  short
        The cloze text becomes the stem with `{{c1::...}}` markers blanked;
        the same text with markers stripped becomes the model answer.
    Basic (type in the answer)  ->  short
        Front is the stem, Back the model answer.

The extra itembank directives the lint gate requires (`WHY BEST:`,
`SECOND-BEST:`, `TRAP:`, `KEY DISCRIMINATOR:`, `CONFIDENCE:`, `RUBRIC:`,
`DISTRACTOR ANALYSIS:`, `[OBJECTIVE:]`) are recognised inside any field when an
author embedded them, so a note carrying them can convert lint-clean. A note
that lacks them is reported Skipped with the named lint codes rather than
approximated. An unknown note type produces a loud named refusal per note
(D-04, the GIFT precedent) -- never a lossy approximation.

Report. `import_apkg()` returns the exhaustive per-note account (D-03):
Converted / Skipped / Refused rows, each with the note id and reason, plus the
verbatim UI-SPEC 3 total line `{n} notes accounted for, 0 dropped silently.`
A note appears exactly once. The CLI writes this report and the staged
candidates (lint-clean dicts, deterministic JSON keyed by note id) for plan
03.2-03's accept loop; a re-import of the same file is report-idempotent.
"""
import json
import os
import re
import sqlite3
import sys
import tempfile
import zipfile

from model import LETTERS, grab, lint

try:
    import zstandard
    ZSTD_AVAILABLE = True
except ImportError:  # pragma: no cover - depends on the environment
    zstandard = None
    ZSTD_AVAILABLE = False


# The published dotted error-code namespace (the GIFT precedent, extending
# model.LINT_CODES). Built from a set-then-sorted tuple so sortedness is
# structural rather than maintained by eye.
APKG_INVALID_CONTAINER = "apkg.invalid_container"
APKG_NO_COLLECTION = "apkg.no_collection_member"
APKG_ZSTD_MISSING = "apkg.zstd_missing"
APKG_ZSTD_DECODE = "apkg.zstd_decode_failed"
APKG_SQLITE_READ = "apkg.collection_unreadable"
APKG_TYPE_REFUSED = "apkg.type_unsupported"
APKG_MEDIA_UNSAFE = "apkg.media_path_traversal"

ANKI_CODES = tuple(sorted({
    APKG_INVALID_CONTAINER, APKG_NO_COLLECTION, APKG_ZSTD_MISSING,
    APKG_ZSTD_DECODE, APKG_SQLITE_READ, APKG_TYPE_REFUSED, APKG_MEDIA_UNSAFE,
}))


class AnkiImportError(Exception):
    """A named import failure. `code` is the dotted API namespace an agent can
    branch on; `str(exc)` carries the message naming the offending file/note.
    """

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


# Anki's collection member names, in the order the importer prefers them.
COLLECTION_MEMBERS = ("collection.anki21b", "collection.anki21", "collection.anki2")

# The named note-type map (D-04): known types map to itembank item types;
# anything absent here is refused per note, never approximated.
anki_note_type_map = {
    "basic": "mc",
    "basic (and reversed card)": "mc",
    "basic (optional reversed card)": "mc",
    "cloze": "short",
    "basic (type in the answer)": "short",
}

_OPTION_RE = re.compile(r"(?m)^([A-H])[).]\s*(.+?)\s*$")
_CORRECT_RE = re.compile(r"(?m)^CORRECT:\s*(.*?)\s*$")
_WHY_RE = re.compile(r"(?m)^WHY BEST:\s*(.*?)\s*(?=\n[A-Z][A-Z \-]+:|\Z)", re.S)
_RUBRIC_RE = re.compile(r"(?m)^RUBRIC:\s*(.*?)\s*(?=^[A-Z][A-Z \-]+:|\Z)", re.S)
_CLOZE_RE = re.compile(r"\{\{([^{}]*)\}\}")


def safe_media_name(name, path):
    """Refuse a media reference that could escape the import output directory
    (T-032-04): any name that is not a plain file name -- a path separator, a
    parent climb, a drive colon, a NUL -- is refused by name before any write,
    in the same containment posture `surfaces/migrate.py` takes."""
    if not name:
        return name
    for sep in (os.sep, os.altsep, "/", "\\"):
        if sep and sep in name:
            raise AnkiImportError(
                APKG_MEDIA_UNSAFE,
                "%s: %s media reference %r is not a plain file name"
                % (APKG_MEDIA_UNSAFE, path, name))
    if ".." in name or ":" in name or "\x00" in name:
        raise AnkiImportError(
            APKG_MEDIA_UNSAFE,
            "%s: %s media reference %r is not a plain file name"
            % (APKG_MEDIA_UNSAFE, path, name))
    return name


def _collection_bytes(path):
    """Return (member_name, member_bytes) for the .apkg's collection member,
    decoding the zstd member through the pinned binding. Named failures only.
    """
    try:
        zf = zipfile.ZipFile(path)
    except (zipfile.BadZipFile, OSError) as exc:
        raise AnkiImportError(
            APKG_INVALID_CONTAINER,
            "%s: %s is not a readable .apkg archive: %s"
            % (APKG_INVALID_CONTAINER, path, exc))
    with zf:
        names = set(zf.namelist())
        member = next((m for m in COLLECTION_MEMBERS if m in names), None)
        if member is None:
            raise AnkiImportError(
                APKG_NO_COLLECTION,
                "%s: %s carries no collection member "
                "(collection.anki21b/anki21/anki2)"
                % (APKG_NO_COLLECTION, path))
        raw = zf.read(member)
    if member == "collection.anki21b":
        if not ZSTD_AVAILABLE:
            raise AnkiImportError(
                APKG_ZSTD_MISSING,
                "%s: %s carries a zstd-compressed collection.anki21b and the "
                "pinned zstandard dependency is not installed; install the "
                "pinned version from requirements.txt"
                % (APKG_ZSTD_MISSING, path))
        try:
            raw = zstandard.ZstdDecompressor().decompress(raw)
        except Exception as exc:
            raise AnkiImportError(
                APKG_ZSTD_DECODE,
                "%s: %s failed to decompress collection.anki21b: %s"
                % (APKG_ZSTD_DECODE, path, exc))
    return member, raw


def _open_collection(path):
    """Open the collection as SQLite in a temp file. Returns
    (connection, member_name, temp_path); the caller closes and unlinks."""
    member, raw = _collection_bytes(path)
    fd, tmp = tempfile.mkstemp(prefix="itembank_import_", suffix=".db")
    os.close(fd)
    try:
        with open(tmp, "wb") as fh:
            fh.write(raw)
        try:
            conn = sqlite3.connect(tmp)
        except sqlite3.Error as exc:
            raise AnkiImportError(
                APKG_SQLITE_READ,
                "%s: %s collection member is not a readable SQLite database: %s"
                % (APKG_SQLITE_READ, path, exc))
        return conn, member, tmp
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _read_notes(conn, path):
    """Read the notes and note-type tables into (notes, type_map). The type
    table is `notetypes` on modern collections and `note_types` on legacy
    ones; both are handled, in that order, with the member's field-name list
    parsed from the JSON each carries."""
    try:
        tables = {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")}
    except sqlite3.Error as exc:
        raise AnkiImportError(APKG_SQLITE_READ,
                              "%s: %s collection unreadable: %s"
                              % (APKG_SQLITE_READ, path, exc))
    if "notes" not in tables:
        raise AnkiImportError(APKG_SQLITE_READ,
                              "%s: %s collection has no notes table"
                              % (APKG_SQLITE_READ, path))
    type_map = {}
    for table, fields_col in (("notetypes", "fields"), ("note_types", "flds")):
        if table not in tables:
            continue
        try:
            for nid, name, fields_json in conn.execute(
                    "SELECT id, name, %s FROM %s" % (fields_col, table)):
                field_names = []
                try:
                    parsed = json.loads(fields_json or "[]")
                    field_names = [f.get("name", "") for f in parsed
                                   if isinstance(f, dict)]
                except (ValueError, AttributeError):
                    field_names = []
                type_map[nid] = {"name": name or "", "field_names": field_names}
        except sqlite3.Error as exc:
            raise AnkiImportError(APKG_SQLITE_READ,
                                  "%s: %s %s table unreadable: %s"
                                  % (APKG_SQLITE_READ, path, table, exc))
        break
    try:
        notes = [{"id": r[0], "mid": r[1], "flds": r[2] or "", "tags": r[3] or ""}
                 for r in conn.execute(
                     "SELECT id, mid, flds, tags FROM notes ORDER BY id")]
    except sqlite3.Error as exc:
        raise AnkiImportError(APKG_SQLITE_READ,
                              "%s: %s notes table unreadable: %s"
                              % (APKG_SQLITE_READ, path, exc))
    return notes, type_map


def _directives(note, note_type):
    """The concatenated field text of one note (for option/directive scans)
    and the name-indexed field values."""
    values = (note.get("flds") or "").split("\x1f")
    names = note_type.get("field_names") or []
    by_name = {name: values[i] for i, name in enumerate(names)
               if name and i < len(values)}
    rest = values[len(names):]
    text = "\n".join([by_name.get(k, "") for k in names] + list(rest))
    return text, by_name


def _parse_options(text):
    """`A) ...`-shaped option lines anywhere in a note's fields, first
    occurrence per letter wins. A documented heuristic, not a lossy
    approximation: the candidate still has to pass model.lint()."""
    opts = {}
    for m in _OPTION_RE.finditer(text):
        letter = m.group(1)
        value = m.group(2).strip()
        if value and letter not in opts:
            opts[letter] = value
    return opts


def _parse_correct(text):
    return [c.upper() for c in re.split(r"[,\s]+", grab(_CORRECT_RE.pattern, text))
            if c.upper() in LETTERS]


def _strip_cloze(text):
    """`{{c1::mitochondria}}` -> `mitochondria`; a bare `{{x}}` -> `x`."""
    def rep(m):
        inner = m.group(1)
        return inner.split("::", 1)[1] if "::" in inner else inner
    return _CLOZE_RE.sub(rep, text)


def _blank_cloze(text):
    """`{{c1::mitochondria}}` -> `_____`: the cloze blank becomes the stem."""
    return _CLOZE_RE.sub(lambda m: "_____", text)


def _rubric_points(text):
    block = grab(_RUBRIC_RE.pattern, text, re.S)
    return [b.strip() for b in re.findall(r"(?m)^-\s*(.+?)\s*$", block)]


def build_candidate(note, note_type, seq):
    """Build one `model.parse_question()`-shaped candidate, or return
    (None, refusal_reason) when the note type is unknown (D-04)."""
    type_name = (note_type.get("name") or "").strip().lower()
    itype = anki_note_type_map.get(type_name)
    if itype is None:
        return None, (
            "%s: note %s: Anki note type %r is not supported -- refused, "
            "never approximated (D-04)"
            % (APKG_TYPE_REFUSED, note["id"], note_type.get("name") or ""))
    text, by_name = _directives(note, note_type)
    values = (note.get("flds") or "").split("\x1f")
    stem = (by_name.get("Front") or by_name.get("Text")
            or next((v for v in values if v.strip()), ""))
    common = {
        "id": "q%d" % seq,
        "number": seq,
        "type": itype,
        "stem": stem,
        "difficulty": "",
        "objective": grab(r"\[OBJECTIVE:\s*(.*?)\]", text),
        "objective_line": "",
        "pair": "",
        "prereq": [],
        "lesson_ref": "",
        "lesson_slug": "",
        "item_id": "",
        "content_hash": "",
        "why": grab(_WHY_RE.pattern, text, re.S),
        "disc": grab(r"(?m)^KEY DISCRIMINATOR:\s*(.*?)\s*$", text),
        "second": grab(r"(?m)^SECOND-BEST:\s*(.*?)\s*$", text),
        "trap": grab(r"(?m)^TRAP:\s*(.*?)\s*$", text),
        "conf": grab(r"(?m)^CONFIDENCE:\s*(.*?)\s*$", text),
    }
    if itype in ("mc", "multi"):
        correct = _parse_correct(text)
        common.update({"opts": _parse_options(text),
                       "correct": correct,
                       "select": len(correct),
                       "da": {}})
        return common, None
    if itype == "short":
        if type_name.startswith("cloze"):
            common["stem"] = _blank_cloze(stem)
            model = _strip_cloze(stem)
        else:
            model = by_name.get("Back") or (values[1] if len(values) > 1 else "")
        common.update({"model": model, "rubric": _rubric_points(text)})
        return common, None
    return None, ("%s: note %s: mapped type %r has no candidate builder"
                  % (APKG_TYPE_REFUSED, note["id"], itype))


def build_report(notes, type_map):
    """The exhaustive per-note account (D-03): every note maps to exactly one
    Converted / Skipped / Refused row, each with its id and reason. Nothing is
    reported convertible until model.lint() passed it (D-05)."""
    rows, candidates = [], []
    converted = skipped = refused = 0
    for seq, note in enumerate(notes, 1):
        note_type = type_map.get(note["mid"])
        if note_type is None:
            rows.append(("Refused", str(note["id"]),
                         "%s: note %s: note type id %s is not defined in this "
                         "collection -- refused (D-04)"
                         % (APKG_TYPE_REFUSED, note["id"], note["mid"])))
            refused += 1
            continue
        cand, refusal = build_candidate(note, note_type, seq)
        if cand is None:
            rows.append(("Refused", str(note["id"]), refusal))
            refused += 1
            continue
        errors, _ = lint([cand])
        if errors:
            reasons = "; ".join("%s (%s)" % (e.code, e) for e in errors)
            rows.append(("Skipped", str(note["id"]), reasons))
            skipped += 1
            continue
        rows.append(("Converted", str(note["id"]),
                     "%s -> %s" % (note_type["name"], cand["type"])))
        candidates.append({"note_id": note["id"],
                           "note_type": note_type["name"],
                           "item": cand})
        converted += 1
    total_line = "%d notes accounted for, 0 dropped silently." % len(notes)
    report_text = "\n".join("%-10s | %s | %s" % (r[0], r[1], r[2])
                            for r in rows)
    if report_text:
        report_text += "\n"
    report_text += total_line + "\n"
    return {"converted": converted, "skipped": skipped, "refused": refused,
            "rows": rows, "candidates": candidates,
            "total_line": total_line, "report_text": report_text}


def _media_map(path):
    """Resolve the `media` member's name map (T-032-04): every name is checked
    by `safe_media_name` so no media reference escapes the import output."""
    try:
        zf = zipfile.ZipFile(path)
    except (zipfile.BadZipFile, OSError):
        return []
    with zf:
        if "media" not in zf.namelist():
            return []
        try:
            raw = zf.read("media")
        except KeyError:
            return []
    try:
        mapping = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return []
    names = []
    for num, name in sorted(mapping.items()):
        safe_media_name(name, path)
        names.append(name)
    return names


def import_apkg(path, out=None, force=False):
    """Read an .apkg, map every note, gate every candidate through
    `model.lint()`, and return the exhaustive per-note account (D-03).

    With `out`, writes `<out>/<deck>_import.md` (the report) and
    `<out>/<deck>_candidates.json` (the lint-clean candidates staged for plan
    03.2-03's accept loop). Never writes a bank (D-06). `force` is the CLI's
    `--force`: it suppresses the nothing-converted exit code there, and is
    never a bypass of the lint gate (D-05).
    """
    conn, member, tmp = _open_collection(path)
    try:
        notes, type_map = _read_notes(conn, path)
        result = build_report(notes, type_map)
    finally:
        conn.close()
        try:
            os.unlink(tmp)
        except OSError:
            pass
    result["collection"] = member
    result["notes_total"] = len(notes)
    result["media"] = _media_map(path)
    if out:
        os.makedirs(out or ".", exist_ok=True)
        stem = os.path.splitext(os.path.basename(path))[0]
        report_path = os.path.join(out, stem + "_import.md")
        with open(report_path, "w", encoding="utf-8") as fh:
            fh.write(result["report_text"])
        candidates_path = os.path.join(out, stem + "_candidates.json")
        payload = {"schema_version": 1,
                   "source": os.path.basename(path),
                   "collection_member": member,
                   "candidates": result["candidates"]}
        with open(candidates_path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        result["report_path"] = report_path
        result["candidates_path"] = candidates_path
    return result


def cmd_import_anki(a):
    """The `itembank import anki <file> --out <dir>` branch: read the
    container, lint candidates, write the report, and stage convertible
    candidates for the accept loop (plan 03.2-03) -- never a bank write
    (D-06), and never dependent on a model backend (D-10)."""
    result = import_apkg(a.file, out=a.out, force=a.force)
    sys.stdout.write(result["report_text"])
    if result["converted"] or a.force:
        print("%d notes converted, %d skipped, %d refused"
              % (result["converted"], result["skipped"], result["refused"]))
        if result.get("report_path"):
            print("report: %s" % result["report_path"])
            print("candidates staged: %s" % result["candidates_path"])
        return 0
    print("0 notes converted -- nothing staged for accept; review the report above")
    return 1
