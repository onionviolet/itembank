#!/usr/bin/env python3
"""Anki .apkg import round-trip tests (plan 03.2-01).

Covers the three tasks: the container reader (ZIP member detection, zstd
decode, named failures), the note-type map with per-note loud refusals and the
model.lint() gate every candidate passes, the exhaustive per-note report with
zero silent drops, and the `itembank import anki` CLI that stages and reports
without ever writing a bank directly.

Standard library only, runnable as `python tests/import_roundtrip.py`. All
fixtures are synthetic .apkg archives built in-test -- never real user data.
The zstd half of the suite is conditional: with the pinned zstandard binding
installed a real compressed member is built and decoded; without it, the
importer's named `apkg.zstd_missing` refusal is asserted and the legacy member
path is proven dependency-free -- exactly the degrade contract the plan pins.
"""
import json
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
TOOL = os.path.join(ROOT, "itembank.py")
REQUIREMENTS = os.path.join(ROOT, "requirements.txt")

from surfaces import import_anki                                  # noqa: E402
from surfaces.import_anki import AnkiImportError, import_apkg     # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def run_cli(*args):
    return subprocess.run([sys.executable, TOOL, *map(str, args)],
                          cwd=ROOT, capture_output=True, text=True)


# ---------------------------------------------------------------------------
# Synthetic .apkg fixture builders
# ---------------------------------------------------------------------------

FIELDS_SEP = "\x1f"      # the real Anki note-field separator

BASIC_FIELDS = json.dumps([{"name": "Front"}, {"name": "Back"}])
CLOZE_FIELDS = json.dumps([{"name": "Text"}, {"name": "Back Extra"}])
IMG_FIELDS = json.dumps([{"name": "Image"}, {"name": "Back"}])

# A Basic note that converts: Front -> stem, Back carries a parseable option
# list, a CORRECT: line and the WHY BEST: directive the lint gate requires.
CONVERTED_MC = (1610000001, 11, FIELDS_SEP.join([
    "A patient with bilateral crackles and frothy sputum most likely has "
    "which condition?",
    "A) Pulmonary edema\nB) Bronchospasm\nC) Anaphylaxis\n"
    "CORRECT: A\nWHY BEST: Fluid overload produces crackles and frothy sputum.",
]), "")

# A Cloze note that converts: cloze markers blanked into the stem, stripped
# into the model answer, with RUBRIC points the short-type lint gate requires.
CONVERTED_CLOZE = (1610000002, 12, FIELDS_SEP.join([
    "The {{c1::mitochondria}} are the powerhouses of the cell.",
    "RUBRIC:\n- Names the organelle\n- States its cellular function",
]), "")

# An unknown note type: must refuse loudly per note, never approximate.
REFUSED_NOTE = (1610000003, 13, "an image of a lung\x1f", "")

# A known-type note that maps but fails lint: must be reported Skipped with
# the named lint codes, and must never be staged.
SKIPPED_NOTE = (1610000004, 11, FIELDS_SEP.join([
    "What color is the sky?",
    "The sky is blue.",
]), "")

NOTES = [CONVERTED_MC, CONVERTED_CLOZE, REFUSED_NOTE, SKIPPED_NOTE]

NOTETYPES = [
    (11, "Basic", BASIC_FIELDS),
    (12, "Cloze", CLOZE_FIELDS),
    (13, "Image Occlusion", IMG_FIELDS),
]


def build_collection_db(db_path, notes, notetypes, modern=True):
    """A real, synthetic Anki collection schema -- modern `notetypes` when
    `modern`, legacy `note_types` otherwise -- so both member layouts are
    exercised end to end."""
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            "CREATE TABLE notes (id INTEGER PRIMARY KEY, guid TEXT, mid INTEGER, "
            "mod INTEGER, usn INTEGER, tags TEXT, flds TEXT, sfld TEXT, "
            "csum INTEGER, flags INTEGER, data TEXT)")
        if modern:
            conn.execute(
                "CREATE TABLE notetypes (id INTEGER PRIMARY KEY, name TEXT, "
                "mtime_secs INTEGER, usn INTEGER, config TEXT, fields TEXT, "
                "tmpls TEXT, latex TEXT, latexsvg TEXT, req TEXT, sortf INTEGER, "
                "did INTEGER, vers INTEGER, tags TEXT)")
            nt_sql = ("INSERT INTO notetypes (id, name, mtime_secs, usn, config, "
                      "fields, tmpls, latex, latexsvg, req, sortf, did, vers, tags) "
                      "VALUES (?,?,0,0,'',?,'','','','',0,0,0,'')")
        else:
            conn.execute(
                "CREATE TABLE note_types (id INTEGER PRIMARY KEY, name TEXT, "
                "mtime_secs INTEGER, usn INTEGER, tags TEXT, flds TEXT, req TEXT, "
                "sfld TEXT, tmpls TEXT, did INTEGER, type INTEGER, css TEXT)")
            nt_sql = ("INSERT INTO note_types (id, name, mtime_secs, usn, tags, "
                      "flds, req, sfld, tmpls, did, type, css) "
                      "VALUES (?,?,0,0,'',?,'','','',0,0,'')")
        for nid, name, fields_json in notetypes:
            conn.execute(nt_sql, (nid, name, fields_json))
        for nid, mid, flds, tags in notes:
            conn.execute(
                "INSERT INTO notes (id, guid, mid, mod, usn, tags, flds, sfld, "
                "csum, flags, data) VALUES (?,?,?,0,0,?,?,'',0,0,'')",
                (nid, "guid-%d" % nid, mid, tags, flds))
        conn.commit()
    finally:
        conn.close()


def make_apkg(path, member, member_bytes):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(member, member_bytes)
        zf.writestr("media", "{}")


def build_apkg(tmpdir, name, member, notes, notetypes=NOTETYPES):
    """A synthetic .apkg: `collection.anki21`/`anki21b` (modern) or
    `collection.anki2` (legacy), zstd-compressed only when asked for the
    modern compressed member."""
    db_path = os.path.join(tmpdir, "collection.db")
    if os.path.exists(db_path):
        os.remove(db_path)  # each member gets a fresh synthetic collection
    build_collection_db(db_path, notes, notetypes,
                        modern=member in ("collection.anki21", "collection.anki21b"))
    with open(db_path, "rb") as fh:
        db_bytes = fh.read()
    if member == "collection.anki21b":
        import zstandard
        db_bytes = zstandard.ZstdCompressor().compress(db_bytes)
    apkg = os.path.join(tmpdir, name)
    make_apkg(apkg, member, db_bytes)
    return apkg


# ---------------------------------------------------------------------------
# Task 1: the container reader
# ---------------------------------------------------------------------------

def test_module_imports_without_zstandard():
    """The module imports and the binding is conditional -- a missing zstandard
    never breaks the legacy path."""
    if not isinstance(import_anki.ZSTD_AVAILABLE, bool):
        fail("ZSTD_AVAILABLE must be a bool, got %r" % import_anki.ZSTD_AVAILABLE)


def test_legacy_collection_reads_with_no_extra_dependency():
    with tempfile.TemporaryDirectory() as td:
        for member in ("collection.anki21", "collection.anki2"):
            apkg = build_apkg(td, "legacy.apkg", member, NOTES)
            result = import_apkg(apkg)
            if result["collection"] != member:
                fail("expected collection %s, got %r" % (member, result["collection"]))
            if result["notes_total"] != 4:
                fail("%s: expected 4 notes, got %d" % (member, result["notes_total"]))
            if result["converted"] != 2 or result["skipped"] != 1 or result["refused"] != 1:
                fail("%s: unexpected account: converted=%d skipped=%d refused=%d"
                     % (member, result["converted"], result["skipped"],
                        result["refused"]))


def test_zstd_member_decodes_or_refuses_by_name():
    with tempfile.TemporaryDirectory() as td:
        if import_anki.ZSTD_AVAILABLE:
            apkg = build_apkg(td, "modern.apkg", "collection.anki21b", NOTES)
            result = import_apkg(apkg)
            if result["collection"] != "collection.anki21b":
                fail("expected collection.anki21b, got %r" % result["collection"])
            if result["notes_total"] != 4:
                fail("zstd collection: expected 4 notes, got %d" % result["notes_total"])
        else:
            # No binding: a zstd member must refuse loudly and by name, never
            # import as an empty deck.
            fake = os.path.join(td, "fake_zstd.apkg")
            with zipfile.ZipFile(fake, "w") as zf:
                zf.writestr("collection.anki21b", b"not a zstd frame")
            try:
                import_apkg(fake)
            except AnkiImportError as exc:
                if exc.code != "apkg.zstd_missing":
                    fail("expected apkg.zstd_missing, got %s: %s" % (exc.code, exc))
                if fake not in str(exc):
                    fail("zstd_missing refusal must name the file, got: %s" % exc)
            else:
                fail("a zstd member with no binding must refuse, not import")
            # ...and the legacy path still reads, dependency-free.
            apkg = build_apkg(td, "legacy.apkg", "collection.anki21", NOTES)
            if import_apkg(apkg)["notes_total"] != 4:
                fail("legacy member must still read when zstandard is absent")


def test_invalid_container_fails_by_name():
    with tempfile.TemporaryDirectory() as td:
        notzip = os.path.join(td, "not_a_zip.apkg")
        with open(notzip, "w") as fh:
            fh.write("definitely not a zip archive")
        try:
            import_apkg(notzip)
        except AnkiImportError as exc:
            if exc.code != "apkg.invalid_container":
                fail("expected apkg.invalid_container, got %s: %s" % (exc.code, exc))
            if notzip not in str(exc):
                fail("invalid_container must name the file, got: %s" % exc)
        else:
            fail("a non-zip .apkg must fail by name, never import as empty")

        nocol = os.path.join(td, "no_collection.apkg")
        with zipfile.ZipFile(nocol, "w") as zf:
            zf.writestr("media", "{}")
        try:
            import_apkg(nocol)
        except AnkiImportError as exc:
            if exc.code != "apkg.no_collection_member":
                fail("expected apkg.no_collection_member, got %s: %s" % (exc.code, exc))
            if nocol not in str(exc):
                fail("no_collection_member must name the file, got: %s" % exc)
        else:
            fail("an archive with no collection member must fail by name")


def test_zstandard_pinned_with_checksum_and_license():
    if not os.path.exists(REQUIREMENTS):
        fail("requirements.txt does not exist -- the pin is part of this plan")
    text = open(REQUIREMENTS, encoding="utf-8").read()
    if not re.search(r"(?m)^zstandard==\S+", text):
        fail("requirements.txt must pin zstandard with an exact version")
    if "--hash=sha256:" not in text:
        fail("requirements.txt must record a sha256 checksum for zstandard")
    if "BSD" not in text:
        fail("requirements.txt must record the zstandard license review")


def test_media_guard_rejects_path_traversal():
    for name in ("../escape.png", "sub\\file.png", "a/b.png", "..\\..\\x.png"):
        try:
            import_anki.safe_media_name(name, "deck.apkg")
        except AnkiImportError as exc:
            if exc.code != "apkg.media_path_traversal":
                fail("expected apkg.media_path_traversal, got %s" % exc.code)
        else:
            fail("media name %r must be refused (T-032-04)" % name)
    if import_anki.safe_media_name("normal.png", "deck.apkg") != "normal.png":
        fail("a plain media file name must resolve unchanged")


# ---------------------------------------------------------------------------
# Task 2: note-type mapping, loud refusal, lint gate, exhaustive report
# ---------------------------------------------------------------------------

def test_note_type_map_and_loud_per_note_refusal():
    if import_anki.anki_note_type_map.get("basic") != "mc":
        fail("anki_note_type_map must map Basic -> mc")
    if import_anki.anki_note_type_map.get("cloze") != "short":
        fail("anki_note_type_map must map Cloze -> short")
    if import_anki.anki_note_type_map.get("image occlusion") is not None:
        fail("an unknown note type must never be silently mapped")
    with tempfile.TemporaryDirectory() as td:
        apkg = build_apkg(td, "refuse.apkg", "collection.anki21",
                          [REFUSED_NOTE], [NOTETYPES[2]])
        result = import_apkg(apkg)
        row = result["rows"][0]
        if row[0] != "Refused":
            fail("an unknown type must be refused, got row %r" % (row,))
        if row[1] != "1610000003":
            fail("the refusal must name the note id, got %r" % row[1])
        if "Image Occlusion" not in row[2]:
            fail("the refusal must name the note type, got %r" % row[2])
        if result["converted"] != 0 or result["candidates"]:
            fail("a refused note must never be converted or staged")


def test_every_candidate_passes_lint_before_convertible():
    with tempfile.TemporaryDirectory() as td:
        apkg = build_apkg(td, "gate.apkg", "collection.anki21",
                          [SKIPPED_NOTE], [NOTETYPES[0]])
        result = import_apkg(apkg)
        row = result["rows"][0]
        if row[0] != "Skipped":
            fail("a candidate that fails lint must be reported Skipped, got %r" % (row,))
        if row[1] != "1610000004":
            fail("the skipped row must name the note id, got %r" % row[1])
        if "item.missing_why_best" not in row[2] and "item.too_few_options" not in row[2]:
            fail("the skipped reason must name the lint codes, got %r" % row[2])
        if result["converted"] != 0 or result["candidates"]:
            fail("nothing may convert or stage without passing model.lint()")


def test_report_is_exhaustive_no_silent_drop():
    with tempfile.TemporaryDirectory() as td:
        apkg = build_apkg(td, "all.apkg", "collection.anki21", NOTES)
        result = import_apkg(apkg)
        seen = [r[1] for r in result["rows"]]
        if len(seen) != 4 or len(set(seen)) != 4:
            fail("every note must appear exactly once, got %r" % seen)
        for expected in ("1610000001", "1610000002", "1610000003", "1610000004"):
            if expected not in seen:
                fail("note %s is missing from the exhaustive report" % expected)
        if result["total_line"] != "4 notes accounted for, 0 dropped silently.":
            fail("total line must be the UI-SPEC 3 verbatim line, got %r"
                 % result["total_line"])
        if "Converted |" not in result["report_text"] and \
                re.sub(r"[ \t]+", " ", result["report_text"]).find(
                    "Converted | 1610000001 |") == -1:
            fail("report must render Converted rows")
        if "Skipped |" not in result["report_text"] and \
                re.sub(r"[ \t]+", " ", result["report_text"]).find(
                    "Skipped | 1610000004 |") == -1:
            fail("report must render Skipped rows")
        if "Refused |" not in result["report_text"] and \
                re.sub(r"[ \t]+", " ", result["report_text"]).find(
                    "Refused | 1610000003 |") == -1:
            fail("report must render Refused rows")


def test_zero_note_import_is_explicit():
    with tempfile.TemporaryDirectory() as td:
        apkg = build_apkg(td, "empty.apkg", "collection.anki21", [])
        result = import_apkg(apkg)
        if result["total_line"] != "0 notes accounted for, 0 dropped silently.":
            fail("zero-note total must be the explicit state, got %r"
                 % result["total_line"])
        if result["report_text"].strip() != "0 notes accounted for, 0 dropped silently.":
            fail("a zero-note report must be an explicit line, never blank")


# ---------------------------------------------------------------------------
# Task 3: the CLI, staging, no-backend degrade, re-import idempotency
# ---------------------------------------------------------------------------

def test_cli_import_stages_reports_without_writing_a_bank():
    with tempfile.TemporaryDirectory() as td:
        apkg = build_apkg(td, "deck.apkg", "collection.anki21", NOTES)
        out = os.path.join(td, "out")
        r = run_cli("import", "anki", apkg, "--out", out)
        if r.returncode != 0:
            fail("import anki exited %d:\n%s\n%s" % (r.returncode, r.stdout, r.stderr))
        report_path = os.path.join(out, "deck_import.md")
        cand_path = os.path.join(out, "deck_candidates.json")
        if not os.path.exists(report_path):
            fail("the per-note report was not written: " + report_path)
        if not os.path.exists(cand_path):
            fail("convertible candidates were not staged: " + cand_path)
        report = open(report_path, encoding="utf-8").read()
        if "4 notes accounted for, 0 dropped silently." not in report:
            fail("report file lacks the exhaustive total line:\n%s" % report)
        data = json.load(open(cand_path, encoding="utf-8"))
        if len(data.get("candidates", [])) != 2:
            fail("expected 2 staged candidates, got %r" % data.get("candidates"))
        for f in os.listdir(out):
            if f.endswith(".md") and f != "deck_import.md":
                fail("import wrote an unexpected markdown file (a bank?): " + f)
        if "0 dropped silently" not in r.stdout:
            fail("the report must print to stdout")


def test_import_needs_no_model_backend():
    src = open(os.path.join(ROOT, "surfaces", "import_anki.py"),
               encoding="utf-8").read()
    for forbidden in ("from surfaces.anki", "from runtime", "import runtime",
                      "itembank.json"):
        if forbidden in src:
            fail("the importer must be backend-free, found %r in source" % forbidden)
    # Runs in a bare temp directory with no config of any kind (D-10).
    with tempfile.TemporaryDirectory() as td:
        apkg = build_apkg(td, "deck.apkg", "collection.anki21", NOTES)
        out = os.path.join(td, "out")
        r = run_cli("import", "anki", apkg, "--out", out)
        if r.returncode != 0:
            fail("import with no backend config exited %d:\n%s\n%s"
                 % (r.returncode, r.stdout, r.stderr))


def test_reimport_is_report_idempotent():
    with tempfile.TemporaryDirectory() as td:
        apkg = build_apkg(td, "deck.apkg", "collection.anki21", NOTES)
        outs = (os.path.join(td, "o1"), os.path.join(td, "o2"))
        for out in outs:
            r = run_cli("import", "anki", apkg, "--out", out)
            if r.returncode != 0:
                fail("re-import exited %d:\n%s\n%s" % (r.returncode, r.stdout, r.stderr))
        report1 = open(os.path.join(outs[0], "deck_import.md"), encoding="utf-8").read()
        report2 = open(os.path.join(outs[1], "deck_import.md"), encoding="utf-8").read()
        if report1 != report2:
            fail("re-import must be report-idempotent:\n---\n%s\n---\n%s"
                 % (report1, report2))
        cand1 = open(os.path.join(outs[0], "deck_candidates.json"), encoding="utf-8").read()
        cand2 = open(os.path.join(outs[1], "deck_candidates.json"), encoding="utf-8").read()
        if cand1 != cand2:
            fail("re-import must stage the same candidates")


def test_import_writes_only_through_the_accept_loop():
    """The plan's verification grep: no direct bank-write path in the staged
    importer. The importer never loads or rewrites a bank; its only writes are
    the report and the staged candidates."""
    src = open(os.path.join(ROOT, "surfaces", "import_anki.py"),
               encoding="utf-8").read()
    if "model.load(" in src or "parse_bank(" in src:
        fail("the importer must never load or rewrite a bank directly")
    writes = list(re.finditer(r"open\(([^,)]+),\s*['\"]w['\"]", src))
    if not writes:
        fail("expected the report/candidates writes, found none")
    for m in writes:
        if "report" not in m.group(1) and "candidates" not in m.group(1):
            fail("a write outside the report/candidates staging: open(%s, 'w')"
                 % m.group(1))


# ---------------------------------------------------------------------------
# plan 03.2-02: the ## SOURCES registry and the on-demand coverage map
# ---------------------------------------------------------------------------

COVERAGE_REGISTRY = ("emt:airway | EMT airway chapter, sect. 5\n"
                     "emt:ops | EMT operations chapter 9\n")


def coverage_item(number, stem, objs):
    """A clean mc item for the coverage fixtures. `objs` lists [OBJ:] values,
    each of which must be registered in the fixture's ## SOURCES."""
    obj_dirs = "".join("[OBJ: %s]\n" % o for o in objs)
    return ("Q%d. %s   (difficulty: recall)\n%s[OBJECTIVE: %s]\n"
            "A) One\nB) Two\nC) Three\nD) Four\n\nCORRECT: A\n\n"
            "WHY BEST: One is the keyed answer.\n\n"
            "KEY DISCRIMINATOR: One vs the rest.\n\n"
            "SECOND-BEST: B. Two is the runner-up; this would be correct if "
            "the question asked for two.\n\n"
            "DISTRACTOR ANALYSIS:\n"
            "- A) Correct: the keyed answer.\n"
            "- B) Two.\n- C) Three.\n- D) Four.\n\n"
            "TRAP: Picking any other.\n\nCONFIDENCE: high\n"
            % (number, stem, obj_dirs, objs[0]))


COVERAGE_BANK = ("# Coverage fixture (synthetic)\n\n## SOURCES\n\n"
                 + COVERAGE_REGISTRY + "\n"
                 + coverage_item(1, "Which finding suggests an at-risk airway?",
                                 ["emt:airway"])
                 + coverage_item(2, "Which task is an emergency response?",
                                 ["emt:ops"]))


def test_registry_validates_through_supported_keyword_set():
    """The ## SOURCES registry validates through schema_validate.py's
    supported keyword set alone (T-032-06): a schema built from exactly the
    supported keywords accepts a well-formed registry and rejects a
    malformed one."""
    import schema_validate
    from model import parse_sources
    registry_schema = {
        "type": "object",
        "properties": {
            "sources": {
                "type": "object",
                "additionalProperties": {"type": "string"},
            },
        },
        "required": ["sources"],
        "additionalProperties": False,
    }
    with tempfile.TemporaryDirectory() as td:
        bank = os.path.join(td, "reg.md")
        open(bank, "w", encoding="utf-8").write(
            "# Registry fixture (synthetic)\n\n## SOURCES\n\n"
            + COVERAGE_REGISTRY + "\n"
            + coverage_item(1, "Which finding suggests an at-risk airway?",
                            ["emt:airway"]))
        reg = parse_sources(bank)
        errs = schema_validate.validate({"sources": reg["sources"]},
                                        registry_schema)
        if errs:
            fail("a well-formed registry must pass the supported-keyword "
                 "schema: %s" % errs)
        errs = schema_validate.validate({"sources": {"emt:airway": 42}},
                                        registry_schema)
        if not errs:
            fail("a non-string locator must fail the registry schema")
        errs = schema_validate.validate({"extra": True}, registry_schema)
        if not errs:
            fail("an unknown top-level key must fail additionalProperties")


def test_coverage_map_on_demand_and_writes_nothing():
    """`itembank coverage <bank>` computes the objective-to-items map from
    the bank and its resolved [OBJ:] values at request time, prints it, and
    writes nothing to disk (D-12, SEED-08, T-032-07)."""
    from model import coverage_map
    with tempfile.TemporaryDirectory() as td:
        bank = os.path.join(td, "cov.md")
        open(bank, "w", encoding="utf-8").write(COVERAGE_BANK)
        before = sorted(os.listdir(td))
        m = coverage_map(bank)
        if m.get("emt:airway") != ["Q1"]:
            fail("coverage map must map emt:airway -> [Q1], got %r" % m)
        if m.get("emt:ops") != ["Q2"]:
            fail("coverage map must map emt:ops -> [Q2], got %r" % m)
        if set(m) != {"emt:airway", "emt:ops"}:
            fail("coverage map carries unexpected objectives: %r" % m)
        r = run_cli("coverage", bank)
        if r.returncode != 0:
            fail("coverage exited %d:\n%s\n%s"
                 % (r.returncode, r.stdout, r.stderr))
        if "emt:airway" not in r.stdout or "Q1" not in r.stdout:
            fail("coverage CLI must print objectives and item tags:\n%s"
                 % r.stdout)
        after = sorted(os.listdir(td))
        if after != before:
            fail("coverage must write nothing to disk; directory changed: %r"
                 % (after,))


def test_coverage_map_reflects_current_bank_state():
    """A changed bank changes the next run's map -- the map is computed on
    demand and never stored, so it cannot go stale (D-12, T-032-07)."""
    from model import coverage_map
    with tempfile.TemporaryDirectory() as td:
        bank = os.path.join(td, "cov.md")
        open(bank, "w", encoding="utf-8").write(COVERAGE_BANK)
        m1 = coverage_map(bank)
        if "Q1" not in m1.get("emt:airway", []):
            fail("baseline map missing Q1 under emt:airway: %r" % m1)
        text = open(bank, encoding="utf-8").read()
        text = text.replace(
            "[OBJ: emt:airway]\n[OBJECTIVE: emt:airway]",
            "[OBJ: emt:airway]\n[OBJ: emt:ops]\n[OBJECTIVE: emt:airway]", 1)
        open(bank, "w", encoding="utf-8").write(text)
        m2 = coverage_map(bank)
        if m2.get("emt:ops") != ["Q1", "Q2"]:
            fail("next-run map must reflect the edited bank (Q1 now teaches "
                 "emt:ops): %r" % m2)
        if m2.get("emt:airway") != ["Q1"]:
            fail("next-run map must keep emt:airway -> [Q1]: %r" % m2)


def test_guard_refuses_corpus_shaped_content_and_fixtures_pass():
    """D-17 (SEED-07, T-032-15): `itembank guard` refuses real-corpus-shaped
    content anywhere outside fixtures/ -- a lesson-prose file and a
    provenance-registry file in a temp dir are refused -- while a fixtures/
    subtree (the in-repo synthetic home) still passes, and a bank-shaped file
    outside fixtures/ is still refused (the pre-existing gate does not
    regress)."""
    with tempfile.TemporaryDirectory() as td:
        # A fixtures/ subtree stays synthetic: a bank-shaped file under it
        # must pass the guard exactly as the repo's fixtures/ do.
        os.makedirs(os.path.join(td, "fixtures"))
        open(os.path.join(td, "fixtures", "sample_bank.md"), "w",
             encoding="utf-8").write(COVERAGE_BANK)
        # Corpus-shaped content that does NOT parse as a bank: lesson prose
        # and a provenance registry (D-17's known corpus shapes).
        open(os.path.join(td, "lesson_prose.md"), "w",
             encoding="utf-8").write(
                 "# Lesson prose\n\n## LESSON\n\n### Section One\n\nTeaching "
                 "text that never becomes an item.\n")
        open(os.path.join(td, "sources_registry.md"), "w",
             encoding="utf-8").write(
                 "# Corpus registry\n\n## SOURCES\n\nemt:airway | chapter 5\n")
        # A bank-shaped file outside fixtures/ must still be refused.
        open(os.path.join(td, "notes.md"), "w",
             encoding="utf-8").write(COVERAGE_BANK)
        r = run_cli("guard", td)
        if r.returncode == 0:
            fail("guard must refuse corpus-shaped content, got rc 0:\n%s"
                 % r.stdout)
        refused = [line for line in r.stdout.splitlines()
                   if line.startswith("error ")]
        for expect in ("lesson_prose.md", "sources_registry.md", "notes.md"):
            if not any(expect in line for line in refused):
                fail("guard must refuse %s, refused: %r" % (expect, refused))
        if any("sample_bank.md" in line for line in refused):
            fail("guard must not refuse fixtures/ content: %r" % refused)
        if not any("carries the corpus marker" in line for line in refused):
            fail("guard must name the corpus marker it refused: %s"
                 % "\n".join(refused))
        if not any("parses as a question bank" in line for line in refused):
            fail("guard must keep refusing bank-shaped files by parse: %s"
                 % "\n".join(refused))


def _corpus_lesson(sentence, expect=""):
    """A synthetic lesson whose single section carries `sentence`; filler
    prose keeps the section inside the house cadence band (120..400 words)
    and opens with prose, so the only warnings the section can trip are the
    deliberately-planted one plus the house require-marker rule."""
    expect_line = ("<!-- CORPUS-EXPECT: %s -->\n" % expect) if expect else ""
    filler = ("The airway stays open when the head is tilted and the chin "
              "is lifted into a neutral position.")
    lines = [expect_line + "# Synthetic corpus lesson",
             "", "## LESSON", "", "### Section One", "", sentence, ""]
    words = len(sentence.split())
    while words < 125:
        lines.append(filler)
        lines.append("")
        words += len(filler.split())
    return "\n".join(lines)


def _write_synthetic_corpus(td):
    """Three synthetic corpus documents (never real data):
      1. long_sentence.md       -- negative: trips style.sentence_length but
                                   does not declare it (a false positive)
      2. long_sentence_exp.md   -- positive: trips it and declares it
      3. unsourced_dose.md      -- positive: a dose item with no [SRC:]
                                   under a ## SOURCES registry trips
                                   style.unsourced_specific (D-14)
    """
    os.makedirs(td, exist_ok=True)
    long_sentence = " ".join(["airway"] * 45) + "."
    open(os.path.join(td, "long_sentence.md"), "w",
         encoding="utf-8").write(_corpus_lesson(long_sentence))
    open(os.path.join(td, "long_sentence_exp.md"), "w",
         encoding="utf-8").write(_corpus_lesson(
             long_sentence, expect="style.sentence_length"))
    open(os.path.join(td, "unsourced_dose.md"), "w",
         encoding="utf-8").write(
             "# Corpus dose item\n\n"
             "<!-- CORPUS-EXPECT: style.unsourced_specific -->\n\n"
             "## SOURCES\n\nemt:airway | chapter 5\n\n"
             + coverage_item(1, "What dose should be delivered? 5 mg",
                             ["emt:airway"]))


def test_calibrate_measures_every_style_warning_and_ship_state():
    """D-18 (T-032-16): the calibration run measures every Phase 3.1 style
    warning over the corpus and records a false-positive rate + ship-state
    decision per warning; a warning above the 0.20 threshold is recorded
    disabled by default. On the synthetic corpus: style.sentence_length
    fires once as a false positive and once as a true positive (rate 0.50,
    disabled), style.unsourced_specific fires once as a true positive (rate
    0.00, enabled), and every calibrated code carries a recorded rate."""
    from surfaces import cli as cli_surface
    with tempfile.TemporaryDirectory() as td:
        _write_synthetic_corpus(td)
        rates, records = cli_surface.calibrate_corpus(td)
        codes = [r["code"] for r in records]
        expected_codes = tuple(sorted(cli_surface.CALIBRATED_WARNING_CODES))
        if codes != list(expected_codes):
            fail("calibration must record every calibrated code, got %r"
                 % codes)
        by_code = {r["code"]: r for r in records}
        sl = by_code["style.sentence_length"]
        if sl["fp_rate"] != 0.5 or sl["false_positives"] != 1 \
                or sl["true_positives"] != 1:
            fail("sentence_length must be 1 FP + 1 TP -> 0.50, got %r" % sl)
        if sl["ship_state"] != "disabled":
            fail("a 0.50 FP rate must ship disabled by default: %r" % sl)
        us = by_code["style.unsourced_specific"]
        if us["fp_rate"] != 0.0 or us["true_positives"] != 1:
            fail("unsourced_specific must be a clean true positive: %r" % us)
        if us["ship_state"] != "enabled":
            fail("a 0.00 FP rate must ship enabled: %r" % us)
        if by_code["style.open_with"]["fp_rate"] != 0.0 \
                or by_code["style.open_with"]["ship_state"] != "enabled":
            fail("a never-firing warning must record rate 0.00 and ship "
                 "enabled: %r" % by_code["style.open_with"])
        # The seam agrees: warning_ship_state applies the same rule.
        from model import warning_ship_state
        if warning_ship_state("style.sentence_length",
                              sl["fp_rate"])["ship_state"] != "disabled":
            fail("warning_ship_state must agree at the 0.20 threshold")
        # The CLI records the rates in the deliverable markdown file.
        out = os.path.join(td, "03.2-CALIBRATION.md")
        r = run_cli("calibrate", td, "--out", out)
        if r.returncode != 0:
            fail("calibrate exited %d:\n%s\n%s"
                 % (r.returncode, r.stdout, r.stderr))
        if not os.path.isfile(out):
            fail("calibrate must write the calibration markdown to %s" % out)
        text = open(out, encoding="utf-8").read()
        for code in expected_codes:
            if code not in text:
                fail("the calibration report must record %s" % code)
        if "disabled by default" not in text or "enabled" not in text:
            fail("the report must carry both ship-states: %s" % text)
        if "human/private-bank action" not in text:
            fail("the report must mark the real-corpus run as the human/"
                 "private-bank action (D-17): %s" % text)


def test_seed_requirements_covered_9_of_9():
    """Every one of SEED-01..SEED-09 appears in a Phase 3.2 plan with a named
    verification fixture -- the audit fails if any SEED id is missing from the
    plans' frontmatter `requirements:` fields."""
    import glob as _glob
    phase = os.path.join(ROOT, ".planning", "phases",
                         "03.2-seeding-import-provenance")
    plans = sorted(_glob.glob(os.path.join(phase, "03.2-0*-PLAN.md")))
    if not plans:
        fail("no Phase 3.2 PLAN files found under %s" % phase)
    covered = {}
    for plan in plans:
        text = open(plan, encoding="utf-8").read()
        fm = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
        if fm is None:
            continue
        frontmatter = fm.group(1)
        m = re.search(r"^requirements:\s*$", frontmatter, re.M)
        if m is None:
            continue
        for sid in re.findall(r"^\s*-\s*(SEED-\d\d)\s*$",
                              frontmatter[m.end():], re.M):
            covered.setdefault(sid, []).append(os.path.basename(plan))
    missing = []
    for n in range(1, 10):
        sid = "SEED-%02d" % n
        if sid not in covered:
            missing.append(sid)
    if missing:
        fail("SEED coverage gap: %s not listed in any Phase 3.2 plan "
             "frontmatter" % ", ".join(missing))
    if len(covered) != 9:
        fail("expected exactly 9 SEED ids covered, got %r" % sorted(covered))
    for sid, in_plans in sorted(covered.items()):
        if len(in_plans) < 1:
            fail("%s must appear in a plan with a named verification"
                 % sid)
        plan = os.path.join(phase, in_plans[0])
        body = open(plan, encoding="utf-8").read()
        if "tests/" not in body and "python " not in body:
            fail("%s's plan %s names no verification fixture"
                 % (sid, in_plans[0]))
    print("seed coverage: 9/9 SEED ids -> %s"
         % ", ".join("%s in %s" % (k, ",".join(v))
                     for k, v in sorted(covered.items())))


def main():
    tests = [v for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    for t in tests:
        t()
    print("import_roundtrip: %d tests passed" % len(tests))
    return 0


if __name__ == "__main__":
    sys.exit(main())
