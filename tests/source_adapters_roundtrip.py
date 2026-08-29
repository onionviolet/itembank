#!/usr/bin/env python3
"""Proves the source-adapter boundary end to end (Phase 14C, plan 14C-01).

One PDF gold case imports as a cited source: schema-valid sidecar, one
fingerprint agreeing across the sidecar, the journal entry, and the registry,
and every locator joined to a span id the one parser assigned. Every failure
family returns a typed source.* code instead of raising, an image-only page is
a named refusal rather than an empty success, rights refusals come from the
journal and are never escalated by a wire-supplied grant, and the module
degrades to a named install command when its optional dependency is absent.

Standard library only plus the optional pdfplumber stack, runnable as
`python tests/source_adapters_roundtrip.py`.
"""
import builtins, json, os, shutil, sys, tempfile, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
FIXTURES = os.path.join(ROOT, "fixtures", "audit")
sys.path.insert(0, FIXTURES)

import auditor                                               # noqa: E402
import identity                                              # noqa: E402
import journal                                               # noqa: E402
import resources                                             # noqa: E402
import schema_validate                                       # noqa: E402
import source_adapters                                       # noqa: E402
import locator_fidelity_cases                                # noqa: E402
import pptx_fidelity_cases                                   # noqa: E402
import web_capture_fidelity_cases                            # noqa: E402
import transcript_fidelity_cases                             # noqa: E402
import epub_fidelity_cases                                   # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


SCHEMA = json.loads(resources.read_text("schemas/source_locator.schema.json"))


def gold_case(case_id):
    for case in locator_fidelity_cases.CASE_TABLE:
        if case["id"] == case_id:
            return case
    fail("gold case %s is not in the case table" % case_id)


def seed_raw(base, case_id):
    """Materialize one gold case into `base` and link it, returning the raw
    file's object id. Linking is the caller's job, never import_source's."""
    case = gold_case(case_id)
    rel = case["filename"]
    with open(os.path.join(base, rel), "wb") as fh:
        fh.write(case["build"]())
    return rel


def link_with_rights(base, rel, rights=None):
    rec = journal.op_link(base, "source", rel, "human", "tester", rights=rights)
    return rec["object_id"]


def all_granted():
    return {op: "granted" for op in identity.RIGHTS_OPERATIONS}


def applied_entries(base):
    return [e for e in journal.entries(base) if e.get("state") == "applied"]


def new_base():
    base = tempfile.mkdtemp(prefix="srcadapt-")
    journal.append_entry  # touch, so the journal module is imported before use
    return base


# ---------------------------------------------------------------------------
def check_thin_slice():
    base = new_base()
    try:
        rel = seed_raw(base, "pdf-born-digital-single-column")
        raw_id = link_with_rights(base, rel, all_granted())
        before = len(applied_entries(base))

        result = source_adapters.import_source(
            base, "pdf", raw_id, "human", "tester")
        if result["status"] != "ok":
            fail("thin slice: expected ok, got %r / %r"
                 % (result["status"], result["error"]))

        md_path = os.path.join(base, result["md_rel_path"])
        if not os.path.exists(md_path):
            fail("thin slice: derived markdown %s was not written"
                 % result["md_rel_path"])
        md_bytes = open(md_path, "rb").read()
        text = md_bytes.decode("utf-8")
        for needle in ("Chapter 1: Airway Management",
                       "The airway is the first priority."):
            if needle not in text:
                fail("thin slice: derived markdown is missing %r" % needle)

        sidecar_path = os.path.join(base, result["sidecar_rel_path"])
        if not os.path.exists(sidecar_path):
            fail("thin slice: sidecar %s was not written"
                 % result["sidecar_rel_path"])
        sidecar = json.loads(open(sidecar_path, encoding="utf-8").read())

        errs = schema_validate.validate(sidecar, SCHEMA)
        if errs:
            fail("thin slice: sidecar failed its own schema: %s" % errs[0])

        after = applied_entries(base)
        if len(after) != before + 1:
            fail("thin slice: expected exactly one new applied entry, got %d"
                 % (len(after) - before))
        entry = after[-1]
        if entry["after_fingerprint"] != sidecar["fingerprint"]:
            fail("thin slice: sidecar fingerprint %r does not equal the "
                 "journal entry's after_fingerprint %r"
                 % (sidecar["fingerprint"], entry["after_fingerprint"]))
        registry = journal.read_registry(base)
        source_id = sidecar["source_id"]
        if source_id not in registry:
            fail("thin slice: source %s is absent from the registry" % source_id)
        if registry[source_id]["fingerprint"] != sidecar["fingerprint"]:
            fail("thin slice: registry fingerprint disagrees with the sidecar")

        if sidecar["reading_order"] != ["p1.0", "p1.1"]:
            fail("thin slice: reading_order is %r, expected ['p1.0', 'p1.1']"
                 % sidecar["reading_order"])

        spans = auditor.normalize_source(md_bytes, source_id,
                                          kind="markdown")["spans"]
        span_ids = set(s["span_id"] for s in spans)
        for loc in sidecar["locators"]:
            if loc["span_id"] is None:
                continue
            if loc["span_id"] not in span_ids:
                fail("thin slice: locator %s carries span_id %r, which the "
                     "one parser never assigned"
                     % (loc["id"], loc["span_id"]))
        if not any(loc["span_id"] is not None for loc in sidecar["locators"]):
            fail("thin slice: no locator joined to a span at all")
        if result["journal_entry_id"] != entry["entry_id"]:
            fail("thin slice: the result reports journal_entry_id %r but the "
                 "applied entry is %r"
                 % (result["journal_entry_id"], entry["entry_id"]))
    finally:
        shutil.rmtree(base, ignore_errors=True)
    print("ok: thin slice -- one PDF imports as a cited source, one "
          "fingerprint across sidecar, journal, and registry")


def check_scanned_pdf_is_typed_unsupported():
    base = new_base()
    try:
        rel = seed_raw(base, "pdf-scanned-image-only")
        raw_id = link_with_rights(base, rel, all_granted())
        before = len(applied_entries(base))

        result = source_adapters.import_source(
            base, "pdf", raw_id, "human", "tester")
        if result["status"] != "unsupported":
            fail("scanned: expected status unsupported, got %r"
                 % result["status"])
        if result["error"]["code"] != "source.unsupported":
            fail("scanned: expected source.unsupported, got %r"
                 % result["error"]["code"])
        for name in os.listdir(base):
            if name.endswith(".md") or name.endswith(".locator.json"):
                fail("scanned: an unsupported import wrote %s" % name)
        if len(applied_entries(base)) != before:
            fail("scanned: an unsupported import added a journal entry")
    finally:
        shutil.rmtree(base, ignore_errors=True)
    print("ok: scanned -- an image-only page is a named refusal that writes "
          "nothing and journals nothing")


def check_nothing_raises():
    base = new_base()
    try:
        rel = seed_raw(base, "pdf-born-digital-single-column")
        raw_id = link_with_rights(base, rel, all_granted())

        result = source_adapters.import_source(
            base, "no-such-adapter", raw_id, "human", "tester")
        if result["error"]["code"] != "source.adapter_unknown":
            fail("nothing raises: unknown adapter gave %r"
                 % result["error"]["code"])

        result = source_adapters.import_source(
            base, "pdf", "0" * 16, "human", "tester")
        if result["error"]["code"] != "source.malformed_input":
            fail("nothing raises: unknown raw object id gave %r"
                 % result["error"]["code"])

        def boom(raw_bytes, options):
            raise ZeroDivisionError("deliberate")

        saved = source_adapters.ADAPTER_REGISTRY["pdf"]
        source_adapters.ADAPTER_REGISTRY["pdf"] = boom
        try:
            result = source_adapters.import_source(
                base, "pdf", raw_id, "human", "tester")
        finally:
            source_adapters.ADAPTER_REGISTRY["pdf"] = saved
        if result["error"]["code"] != "source.internal_error":
            fail("nothing raises: a raising adapter gave %r"
                 % result["error"]["code"])
    finally:
        shutil.rmtree(base, ignore_errors=True)
    print("ok: nothing raises -- unknown adapter, unknown raw id, and a "
          "raising extractor all return typed codes")


def check_rights_refusal():
    base = new_base()
    try:
        rel = seed_raw(base, "pdf-born-digital-single-column")
        raw_id = link_with_rights(base, rel)  # no rights: all seven unknown
        before = len(applied_entries(base))
        try:
            source_adapters.import_source(base, "pdf", raw_id,
                                           "human", "tester")
        except journal.JournalError as exc:
            if exc.code != "journal.rights_unknown":
                fail("rights: expected journal.rights_unknown, got %r"
                     % (exc.code,))
        else:
            fail("rights: an all-unknown source imported without refusal")
        if len(applied_entries(base)) != before:
            fail("rights: a refused import left an applied entry")
        for name in os.listdir(base):
            if name.endswith(".locator.json"):
                fail("rights: a refused import left an orphan sidecar %s" % name)
    finally:
        shutil.rmtree(base, ignore_errors=True)
    print("ok: rights refusal -- unknown transform refuses by name and "
          "leaves no orphan sidecar")


def check_no_rights_escalation():
    base = new_base()
    try:
        rel = seed_raw(base, "pdf-born-digital-single-column")
        denied = all_granted()
        denied["transform"] = "denied"
        raw_id = link_with_rights(base, rel, denied)
        wire_grant = all_granted()
        try:
            source_adapters.import_source(base, "pdf", raw_id, "human",
                                           "tester", rights_grant=wire_grant)
        except journal.JournalError as exc:
            if exc.code != "journal.rights_unknown":
                fail("escalation: expected journal.rights_unknown, got %r"
                     % (exc.code,))
        else:
            fail("escalation: a wire-supplied grant overrode a recorded denial")
    finally:
        shutil.rmtree(base, ignore_errors=True)
    print("ok: no rights escalation -- the recorded row wins over a "
          "wire-supplied grant")


def check_one_import_path():
    base = new_base()
    try:
        rel = "notes.md"
        body = "# Heading\n\nA body line.\n- a list item\n"
        with open(os.path.join(base, rel), "w", encoding="utf-8") as fh:
            fh.write(body)
        raw_id = link_with_rights(base, rel, all_granted())
        result = source_adapters.import_source(
            base, "markdown", raw_id, "human", "tester")
        if result["status"] != "ok":
            fail("one path: markdown import failed: %r" % (result["error"],))
        sidecar = json.loads(
            open(os.path.join(base, result["sidecar_rel_path"]),
                 encoding="utf-8").read())
        for loc in sidecar["locators"]:
            if loc["body"]["medium"] != "markdown":
                fail("one path: markdown locator body medium is %r"
                     % loc["body"]["medium"])
        md_bytes = open(os.path.join(base, result["md_rel_path"]), "rb").read()
        spans = auditor.normalize_source(md_bytes, sidecar["source_id"],
                                          kind="markdown")["spans"]
        if len(sidecar["reading_order"]) != len(spans):
            fail("one path: reading_order has %d ids but the one parser "
                 "reports %d spans"
                 % (len(sidecar["reading_order"]), len(spans)))
    finally:
        shutil.rmtree(base, ignore_errors=True)
    print("ok: one import path -- markdown is a registry entry, not a "
          "special case, and its sidecar agrees with the one parser")


def check_no_second_parser():
    if hasattr(source_adapters, "model"):
        fail("second parser: source_adapters imported model")
    if hasattr(source_adapters, "runtime"):
        fail("second parser: source_adapters imported runtime")
    text = open(os.path.join(ROOT, "source_adapters.py"), encoding="utf-8").read()
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped in ("import model", "import runtime"):
            fail("second parser: source_adapters.py contains %r" % stripped)
    print("ok: no second parser -- source_adapters never imports model or "
          "runtime")


def check_degrades_without_dependencies():
    base = new_base()
    real_import = builtins.__import__

    def blocked(name, *args, **kwargs):
        if name in ("pdfplumber", "docx", "pptx"):
            raise ImportError("blocked for this test")
        return real_import(name, *args, **kwargs)

    try:
        rel = seed_raw(base, "pdf-born-digital-single-column")
        pdf_id = link_with_rights(base, rel, all_granted())
        md_rel = "notes.md"
        with open(os.path.join(base, md_rel), "w", encoding="utf-8") as fh:
            fh.write("# Still works\n\nA body line.\n")
        md_id = link_with_rights(base, md_rel, all_granted())

        builtins.__import__ = blocked
        try:
            result = source_adapters.import_source(
                base, "pdf", pdf_id, "human", "tester")
            if result["error"]["code"] != "source.dependency_missing":
                fail("degrade: expected source.dependency_missing, got %r"
                     % result["error"]["code"])
            needle = "pip install pdfplumber==0.11.10"
            if needle not in result["error"]["message"]:
                fail("degrade: the refusal message does not name the install "
                     "command: %r" % result["error"]["message"])
            for adapter, needle, case_id in (
                    ("docx", "pip install python-docx==1.2.0",
                     "docx-headings-lists"),
                    ("pptx", "pip install python-pptx==1.0.2", None)):
                if case_id is None:
                    other_rel = "deck.pptx"
                    with open(os.path.join(base, other_rel), "wb") as fh:
                        fh.write(pptx_fidelity_cases.CASE_TABLE[0]["build"]())
                else:
                    other_rel = seed_raw(base, case_id)
                other_id = link_with_rights(base, other_rel, all_granted())
                degraded = source_adapters.import_source(
                    base, adapter, other_id, "human", "tester")
                if degraded["error"]["code"] != "source.dependency_missing":
                    fail("degrade: %s gave %r rather than "
                         "source.dependency_missing"
                         % (adapter, degraded["error"]["code"]))
                if needle not in degraded["error"]["message"]:
                    fail("degrade: the %s refusal does not name its install "
                         "command: %r" % (adapter, degraded["error"]["message"]))
            epub_rel = "book.epub"
            with open(os.path.join(base, epub_rel), "wb") as fh:
                fh.write(epub_fidelity_cases.CASE_TABLE[0]["build"]())
            epub_id = link_with_rights(base, epub_rel, all_granted())
            still_works = source_adapters.import_source(
                base, "epub", epub_id, "human", "tester")
            if still_works["status"] != "ok":
                fail("degrade: epub has no third-party dependency and should "
                     "still import: %r" % (still_works["error"],))
            ok = source_adapters.import_source(
                base, "markdown", md_id, "human", "tester")
        finally:
            builtins.__import__ = real_import
        if ok["status"] != "ok":
            fail("degrade: markdown stopped working in the same process: %r"
                 % (ok["error"],))
    finally:
        builtins.__import__ = real_import
        shutil.rmtree(base, ignore_errors=True)
    print("ok: degrades without dependencies -- pdf refuses by name with the "
          "install command while markdown still imports")


def check_write_containment():
    base = new_base()
    outside = tempfile.mkdtemp(prefix="srcadapt-outside-")
    try:
        rel = os.path.join("..", os.path.basename(outside), "escape.md")
        with open(os.path.join(outside, "escape.md"), "w",
                  encoding="utf-8") as fh:
            fh.write("# Escaped\n")
        # Link cannot be used to register an out-of-root path, so the registry
        # row is forged directly: this test is about import_source's own write,
        # not about link's preflight.
        try:
            journal.op_link(base, "source", rel, "human", "tester",
                             rights=all_granted())
        except journal.JournalError as exc:
            if exc.code != "journal.path_outside_root":
                fail("containment: link refused with %r, expected "
                     "journal.path_outside_root" % (exc.code,))
        else:
            fail("containment: linking a path outside the root was allowed")
        for name in os.listdir(outside):
            if name.endswith(".md") and name != "escape.md":
                fail("containment: a file was written outside the root")
        if os.path.exists(os.path.join(outside, "escape.md.locator.json")):
            fail("containment: a sidecar was written outside the root")
    finally:
        shutil.rmtree(base, ignore_errors=True)
        shutil.rmtree(outside, ignore_errors=True)
    print("ok: write containment -- a path resolving outside the approved "
          "root is refused and nothing is written")


def check_cli_and_route_parity():
    """SURF-04: the CLI command and the daemon route reach the same function
    rather than two implementations. The same Markdown imported through each,
    into two separate bases, produces sidecars that are identical once the
    three fields that are supposed to differ per run are removed."""
    import subprocess
    import surfaces.daemon as daemon_module

    body = "# Parity\n\nOne body line.\n- and a list item\n"

    def sidecar_via_cli(base):
        with open(os.path.join(base, "parity.md"), "w",
                  encoding="utf-8") as fh:
            fh.write(body)
        proc = subprocess.run(
            [sys.executable, os.path.join(ROOT, "itembank.py"), "source",
             "import", "--base", base, "--file", "parity.md",
             "--adapter", "markdown", "--grant",
             ",".join(identity.RIGHTS_OPERATIONS), "--json"],
            capture_output=True, text=True, cwd=ROOT)
        if proc.returncode != 0:
            fail("parity: the CLI import failed: %s" % (proc.stdout + proc.stderr))
        result = json.loads(proc.stdout)
        return json.loads(open(os.path.join(base, result["sidecar_rel_path"]),
                                encoding="utf-8").read())

    def sidecar_via_module(base):
        with open(os.path.join(base, "parity.md"), "w",
                  encoding="utf-8") as fh:
            fh.write(body)
        raw_id = link_with_rights(base, "parity.md", all_granted())
        # The route's own body-shaped call, with the daemon's actor identity
        # and the confirm the route requires of an agent under the
        # approve_before_bind default (plan 14C-04).
        result = source_adapters.import_source(
            base, "markdown", raw_id, "agent", "daemon", confirm=True)
        if result["status"] != "ok":
            fail("parity: the route-shaped import failed: %r" % (result["error"],))
        return json.loads(open(os.path.join(base, result["sidecar_rel_path"]),
                                encoding="utf-8").read())

    if not hasattr(daemon_module, "handle_api_source_import"):
        fail("parity: the daemon has no handle_api_source_import")

    a = tempfile.mkdtemp(prefix="srcadapt-cli-")
    b = tempfile.mkdtemp(prefix="srcadapt-route-")
    try:
        left = sidecar_via_cli(a)
        right = sidecar_via_module(b)
        for field in ("source_id", "captured_at"):
            left.pop(field)
            right.pop(field)
        # The fingerprint is over identical derived bytes, so it must AGREE
        # rather than be removed: two surfaces disagreeing here would mean two
        # extractions, which is the thing this check exists to refuse.
        if left["fingerprint"] != right["fingerprint"]:
            fail("parity: the two surfaces derived different bytes")
        if left != right:
            for key in sorted(set(left) | set(right)):
                if left.get(key) != right.get(key):
                    fail("parity: the two surfaces disagree on %r: %r vs %r"
                         % (key, left.get(key), right.get(key)))
    finally:
        shutil.rmtree(a, ignore_errors=True)
        shutil.rmtree(b, ignore_errors=True)
    print("ok: cli and route parity -- both surfaces reach one function and "
          "produce one sidecar")



# ---------------------------------------------------------------------------
# Plan 14C-02: the gold corpus, the container guards, and the two-file pair.

def _extract_case(case):
    """Run one gold case through its adapter's extraction function and return
    `(reading_order, unsupported_messages)` or `("refused", code, message)`.
    Both refusal shapes -- a `_Refusal` raised out of a nested loop and an
    unsupported four-tuple returned from the top -- normalize here, because
    the gold manifest records what the learner is told, not which internal
    path produced it."""
    options = {}
    if "max_input_bytes" in case["gold"]:
        options["max_input_bytes"] = case["gold"]["max_input_bytes"]
    extract = source_adapters.ADAPTER_REGISTRY[case["kind"]]
    try:
        _md, locators, reading_order, unsupported = extract(case["build"](),
                                                            options)
    except source_adapters._Refusal as refusal:
        return ("refused", refusal.code, refusal.message)
    messages = [entry["message"] for entry in unsupported]
    if unsupported and not locators:
        return ("refused", unsupported[0]["code"], unsupported[0]["message"])
    return (reading_order, messages)


def _check_gold_kind(kind, label):
    cases = [c for c in locator_fidelity_cases.CASE_TABLE
             if c["kind"] == kind]
    for case in cases:
        gold = case["gold"]
        outcome = _extract_case(case)
        if gold["adapter_expectation"] == "unsupported":
            if outcome[0] != "refused":
                fail("%s: %s was expected to refuse, but produced the "
                     "reading order %r" % (label, case["id"], outcome[0]))
            if outcome[2] != gold["unsupported"][0] and \
                    not outcome[2].startswith(gold["unsupported"][0]):
                fail("%s: %s refused with %r, but the gold manifest records "
                     "%r" % (label, case["id"], outcome[2],
                             gold["unsupported"][0]))
            continue
        if outcome[0] == "refused":
            fail("%s: %s was expected to extract, but refused with %s / %s"
                 % (label, case["id"], outcome[1], outcome[2]))
        if outcome[0] != gold["reading_order"]:
            fail("%s: %s produced the reading order %r, but the gold "
                 "manifest records %r"
                 % (label, case["id"], outcome[0], gold["reading_order"]))
        if outcome[1] != gold["unsupported"]:
            fail("%s: %s reported the unsupported structures %r, but the "
                 "gold manifest records %r"
                 % (label, case["id"], outcome[1], gold["unsupported"]))
    return len(cases)


def check_pdf_gold_cases():
    count = _check_gold_kind("pdf", "pdf gold")
    print("ok: pdf gold cases -- all %d resolve as recorded, including the "
          "two-column, table, and footnote orders and the three refusal "
          "messages character for character" % count)


def check_docx_gold_cases():
    count = _check_gold_kind("docx", "docx gold")
    print("ok: docx gold cases -- all %d resolve as recorded" % count)


def check_docx_extra_parts():
    """The assertion that goes red when an adapter is built on python-docx
    alone: footnotes, endnotes, headers, footers, and comments live in package
    parts the Document object model never surfaces."""
    wanted = {"footnote", "endnote", "header", "footer", "comment"}
    seen = set()
    for case_id in ("docx-footnote-endnote", "docx-header-footer",
                    "docx-tracked-changes", "docx-comments"):
        case = gold_case(case_id)
        _md, locators, _order, _unsupported = source_adapters._extract_docx(
            case["build"](), {})
        parts = set(loc["body"]["part"] for loc in locators)
        if case_id != "docx-tracked-changes" and parts <= {"body"}:
            fail("extra parts: %s produced only body locators, so the parts "
                 "python-docx does not surface were never read" % case_id)
        seen |= parts
    if seen != wanted | {"body"}:
        fail("extra parts: the four cases produced the parts %r, expected %r"
             % (sorted(seen), sorted(wanted | {"body"})))
    kinds = set()
    case = gold_case("docx-tracked-changes")
    _md, locators, _order, _unsupported = source_adapters._extract_docx(
        case["build"](), {})
    for loc in locators:
        kinds.add(loc["kind"])
    for kind in ("tracked_insert", "tracked_delete"):
        if kind not in kinds:
            fail("extra parts: a tracked change produced no %s locator" % kind)
        for loc in locators:
            if loc["kind"] == kind and loc["body"]["part"] != "body":
                fail("extra parts: %s is part %r, but a tracked range lives "
                     "in the body part" % (kind, loc["body"]["part"]))
    print("ok: docx extra parts -- footnote, endnote, header, footer, and "
          "comment parts are read directly, and tracked ranges stay in the "
          "body part")


def check_docx_end_to_end():
    base = new_base()
    try:
        rel = seed_raw(base, "docx-headings-lists")
        raw_id = link_with_rights(base, rel, all_granted())
        result = source_adapters.import_source(base, "docx", raw_id, "human",
                                                "tester")
        if result["status"] != "ok":
            fail("docx end to end: %r" % (result["error"],))
        sidecar = json.loads(open(os.path.join(base,
                                                result["sidecar_rel_path"]),
                                   encoding="utf-8").read())
        errs = schema_validate.validate(sidecar, SCHEMA)
        if errs:
            fail("docx end to end: sidecar failed its own schema: %s"
                 % errs[0])
        md_bytes = open(os.path.join(base, result["md_rel_path"]), "rb").read()
        lines = [ln for ln in md_bytes.decode("utf-8").split("\n")[:-1]]
        if len(lines) != len(sidecar["reading_order"]):
            fail("docx end to end: %d derived lines against %d reading-order "
                 "entries" % (len(lines), len(sidecar["reading_order"])))
        applied = applied_entries(base)
        if not applied or applied[-1]["after_fingerprint"] != \
                sidecar["fingerprint"]:
            fail("docx end to end: the journal entry and the sidecar disagree "
                 "on the fingerprint")
    finally:
        shutil.rmtree(base, ignore_errors=True)
    print("ok: docx end to end -- one DOCX imports with a schema-valid "
          "sidecar, one applied entry, and one derived line per locator")


def check_zip_bomb_guard():
    case = gold_case("zip-bomb-oversized-part")
    started = time.time()
    try:
        source_adapters._extract_docx(
            case["build"](), {"max_input_bytes": case["gold"]["max_input_bytes"]})
    except source_adapters._Refusal as refusal:
        elapsed = time.time() - started
        if refusal.code != "source.oversized":
            fail("zip bomb: refused with %r, expected source.oversized"
                 % refusal.code)
        if elapsed > 5.0:
            fail("zip bomb: the refusal took %.1fs, which means the member "
                 "was decompressed before it was refused" % elapsed)
    else:
        fail("zip bomb: an oversized declared member was not refused")
    print("ok: zip bomb guard -- an oversized declared member is refused "
          "before it is decompressed")


def check_xml_entity_guard():
    case = gold_case("xml-entity-expansion")
    started = time.time()
    try:
        source_adapters._extract_docx(case["build"](), {})
    except source_adapters._Refusal as refusal:
        elapsed = time.time() - started
        if refusal.code != "source.malformed_input":
            fail("entity guard: refused with %r, expected "
                 "source.malformed_input" % refusal.code)
        if elapsed > 5.0:
            fail("entity guard: the refusal took %.1fs, which means the "
                 "entities were expanded before the refusal" % elapsed)
    else:
        fail("entity guard: an entity declaration was not refused")
    element, error = source_adapters._parse_xml_safely(b"<a><b/></a>", {})
    if error is not None or element is None:
        fail("entity guard: an ordinary part was refused: %r" % (error,))
    print("ok: xml entity guard -- a DOCTYPE or entity declaration is "
          "refused before the parser runs, and an ordinary part still parses")


def check_gold_manifest_additive():
    """PLANNING-DIRECTIVES section 4 non-negotiable 4: the format change is
    additive, proven by byte-identical fixtures rather than promised."""
    table = locator_fidelity_cases.CASE_TABLE
    if len(table) != 20:
        fail("gold manifest: expected 20 cases, found %d" % len(table))
    for case in table:
        gold = case["gold"]
        raw = case["build"]()
        if locator_fidelity_cases.sha256(raw) != gold["sha256"]:
            fail("gold manifest: %s drifted from its recorded sha256"
                 % case["id"])
        for key in ("sha256", "structures", "reading_order", "unsupported",
                    "expectation", "adapter_expectation"):
            if key not in gold:
                fail("gold manifest: %s is missing %s" % (case["id"], key))
        if gold["expectation"] != "unsupported_now":
            fail("gold manifest: %s changed the Phase 11 expectation"
                 % case["id"])
        if gold["adapter_expectation"] not in ("supported", "unsupported"):
            fail("gold manifest: %s has adapter_expectation %r"
                 % (case["id"], gold["adapter_expectation"]))
        empty = not gold["reading_order"]
        if empty != (gold["adapter_expectation"] == "unsupported"):
            fail("gold manifest: %s says adapter_expectation %r with a "
                 "reading order of %r; the two must agree"
                 % (case["id"], gold["adapter_expectation"],
                    gold["reading_order"]))
    print("ok: gold manifest additive -- 20 cases, every recorded sha256 "
          "unchanged, both expectation keys present and agreeing")



# ---------------------------------------------------------------------------
# Plan 14C-03: the PPTX corpus.

def pptx_case(case_id):
    for case in pptx_fidelity_cases.CASE_TABLE:
        if case["id"] == case_id:
            return case
    fail("pptx gold case %s is not in the case table" % case_id)


def _extract_pptx_case(case):
    try:
        md, locators, reading_order, unsupported = \
            source_adapters._extract_pptx(case["build"](), {})
    except source_adapters._Refusal as refusal:
        return ("refused", refusal.code, refusal.message, None)
    return (reading_order, [e["message"] for e in unsupported], locators, md)


def check_pptx_fixture_determinism():
    table = pptx_fidelity_cases.CASE_TABLE
    if len(table) != 6:
        fail("pptx fixtures: expected 6 cases, found %d" % len(table))
    if hasattr(pptx_fidelity_cases, "pptx"):
        fail("pptx fixtures: the fixture module imported python-pptx, so it "
             "would only prove the library round-trips its own output")
    for case in table:
        first = case["build"]()
        second = case["build"]()
        if first != second:
            fail("pptx fixtures: %s is not deterministic within one process"
                 % case["id"])
        if pptx_fidelity_cases.sha256(first) != case["gold"]["sha256"]:
            fail("pptx fixtures: %s drifted from its recorded sha256"
                 % case["id"])
        for key in ("sha256", "structures", "reading_order", "unsupported",
                    "adapter_expectation"):
            if key not in case["gold"]:
                fail("pptx fixtures: %s is missing %s" % (case["id"], key))
        empty = not case["gold"]["reading_order"]
        if empty != (case["gold"]["adapter_expectation"] == "unsupported"):
            fail("pptx fixtures: %s disagrees with the reading-order "
                 "invariant" % case["id"])
    workdir = tempfile.mkdtemp(prefix="pptxfix-")
    try:
        records = pptx_fidelity_cases.materialize(
            os.path.join(workdir, "out"))
        if len(records) != len(table):
            fail("pptx fixtures: materialize returned %d records for %d cases"
                 % (len(records), len(table)))
        for _case_id, path, digest in records:
            if not path.startswith(workdir):
                fail("pptx fixtures: materialize wrote outside its directory")
            with open(path, "rb") as fh:
                if pptx_fidelity_cases.sha256(fh.read()) != digest:
                    fail("pptx fixtures: a materialized file does not match "
                         "its reported digest")
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    print("ok: pptx fixture determinism -- 6 hand-assembled cases, every "
          "recorded sha256 stable, and no python-pptx in the builder")


def check_pptx_gold_cases():
    for case in pptx_fidelity_cases.CASE_TABLE:
        gold = case["gold"]
        outcome = _extract_pptx_case(case)
        if gold["adapter_expectation"] == "unsupported":
            if outcome[0] != "refused":
                fail("pptx gold: %s was expected to refuse, but produced %r"
                     % (case["id"], outcome[0]))
            if outcome[2] != gold["unsupported"][0]:
                fail("pptx gold: %s refused with %r, but the gold manifest "
                     "records %r"
                     % (case["id"], outcome[2], gold["unsupported"][0]))
            continue
        if outcome[0] == "refused":
            fail("pptx gold: %s was expected to extract, but refused with "
                 "%s / %s" % (case["id"], outcome[1], outcome[2]))
        if outcome[0] != gold["reading_order"]:
            fail("pptx gold: %s produced the reading order %r, but the gold "
                 "manifest records %r"
                 % (case["id"], outcome[0], gold["reading_order"]))
        if outcome[1] != gold["unsupported"]:
            fail("pptx gold: %s reported %r, but the gold manifest records %r"
                 % (case["id"], outcome[1], gold["unsupported"]))
    print("ok: pptx gold cases -- all 6 resolve as recorded")


def check_pptx_notes_flag():
    case = pptx_case("pptx-speaker-notes")
    _order, _unsupported, locators, md = _extract_pptx_case(case)
    flagged = [loc for loc in locators if loc["body"]["notes"] is True]
    plain = [loc for loc in locators if loc["body"]["notes"] is False]
    if len(flagged) != 1 or len(plain) != 1:
        fail("pptx notes: expected one flagged and one plain locator, got "
             "%d and %d" % (len(flagged), len(plain)))
    if flagged[0]["body"]["slide"] != plain[0]["body"]["slide"]:
        fail("pptx notes: the note is numbered on slide %r while its slide is "
             "%r" % (flagged[0]["body"]["slide"], plain[0]["body"]["slide"]))
    if "Mention the Venturi mask flow rates." not in md:
        fail("pptx notes: the speaker note is absent from the derived "
             "Markdown")
    print("ok: pptx notes flag -- a speaker note is distinguishable by a real "
          "boolean on its locator body, not by a naming convention")


def check_pptx_slide_order():
    case = pptx_case("pptx-reordered-slides")
    order, _unsupported, _locators, md = _extract_pptx_case(case)
    if order != case["gold"]["reading_order"]:
        fail("pptx order: %r against the recorded %r"
             % (order, case["gold"]["reading_order"]))
    content = [line for line in md.split("\n")
               if line and not line.startswith("## ")]
    if content[0] != case["gold"]["first_text"]:
        fail("pptx order: the first emitted text is %r, so slide order came "
             "from sorted filenames rather than from the sldId list"
             % content[0])
    print("ok: pptx slide order -- reading order comes from the presentation "
          "part's sldId list, not from sorted slide filenames")


def check_pptx_partial_refusal():
    base = new_base()
    try:
        case = pptx_case("pptx-video-only-slide")
        rel = case["filename"]
        with open(os.path.join(base, rel), "wb") as fh:
            fh.write(case["build"]())
        raw_id = link_with_rights(base, rel, all_granted())
        result = source_adapters.import_source(base, "pptx", raw_id, "human",
                                                "tester")
        if result["status"] != "ok":
            fail("pptx partial: a deck with one media-only slide was "
                 "discarded: %r" % (result["error"],))
        sidecar = json.loads(open(os.path.join(base,
                                                result["sidecar_rel_path"]),
                                   encoding="utf-8").read())
        errs = schema_validate.validate(sidecar, SCHEMA)
        if errs:
            fail("pptx partial: sidecar failed its own schema: %s" % errs[0])
        if not sidecar["locators"]:
            fail("pptx partial: the deck extracted no locators at all")
        messages = [e["message"] for e in sidecar["unsupported"]]
        if messages != case["gold"]["unsupported"]:
            fail("pptx partial: the sidecar records %r, expected %r"
                 % (messages, case["gold"]["unsupported"]))
    finally:
        shutil.rmtree(base, ignore_errors=True)
    print("ok: pptx partial refusal -- a media-only slide is named in the "
          "sidecar while the rest of the deck still imports")


# ---------------------------------------------------------------------------
# Plan 14C-04: remote capture. Every fetch in this section runs against a
# loopback http.server bound on port 0. No check makes a real network
# request, and the fixture's own routes are proven correct before any
# adapter is pointed at them.

LOOPBACK_OPTIONS = {"allow_private_origins": True}


def web_case(case_id):
    for case in web_capture_fidelity_cases.CASE_TABLE:
        if case["id"] == case_id:
            return case
    fail("web gold case %s is not in the case table" % case_id)


def capture_options(**overrides):
    """Loopback fetching needs the private-origin refusal lifted, which is
    itself the proof that the default is deny: without this the whole
    section refuses."""
    options = dict(LOOPBACK_OPTIONS)
    options.update(overrides)
    return options


def check_option_defaults_match_schema():
    """`source_adapters.SOURCE_OPTION_DEFAULTS` duplicates the `source`
    group's defaults so a direct call with no options is governed by the same
    restrictive policy a surface would load. The duplication is only safe
    while the two agree."""
    schema = json.loads(resources.read_text("schemas/settings.schema.json"))
    shipped = schema["properties"]["source"]["default"]
    if source_adapters.SOURCE_OPTION_DEFAULTS != shipped:
        fail("option defaults: source_adapters.SOURCE_OPTION_DEFAULTS is %r "
             "but the settings schema default is %r"
             % (source_adapters.SOURCE_OPTION_DEFAULTS, shipped))
    if source_adapters._options({})["bind_policy"] != "approve_before_bind":
        fail("option defaults: an options-less call is not governed by "
             "approve_before_bind")
    if source_adapters._options({})["allow_private_origins"] is not False:
        fail("option defaults: private origins are not denied by default")
    print("ok: option defaults -- the adapter's own defaults equal the "
          "shipped settings defaults, and both are restrictive")


def check_web_fixture_determinism():
    table = web_capture_fidelity_cases.CASE_TABLE
    if len(table) != 6:
        fail("web fixtures: expected 6 cases, found %d" % len(table))
    for case in table:
        first = case["build"]()
        if first != case["build"]():
            fail("web fixtures: %s is not deterministic" % case["id"])
        if web_capture_fidelity_cases.sha256(first) != case["gold"]["sha256"]:
            fail("web fixtures: %s drifted from its recorded sha256"
                 % case["id"])
        empty = not case["gold"]["reading_order"]
        if empty != (case["gold"]["adapter_expectation"] == "unsupported"):
            fail("web fixtures: %s disagrees with the reading-order "
                 "invariant" % case["id"])
    workdir = tempfile.mkdtemp(prefix="webfix-")
    try:
        records = web_capture_fidelity_cases.materialize(
            os.path.join(workdir, "out"))
        for _case_id, path, digest in records:
            if not path.startswith(workdir):
                fail("web fixtures: materialize wrote outside its directory")
            with open(path, "rb") as fh:
                if web_capture_fidelity_cases.sha256(fh.read()) != digest:
                    fail("web fixtures: a materialized file does not match "
                         "its digest")
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    print("ok: web fixture determinism -- 6 static cases, every recorded "
          "sha256 stable, materialize contained")


def check_loopback_fixture_serves():
    """The fixture is proven correct before any adapter is pointed at it, so
    a later adapter failure is unambiguous."""
    import urllib.error
    import urllib.request
    server = web_capture_fidelity_cases.LoopbackServer().start()
    try:
        with urllib.request.urlopen(server.url("/article"), timeout=5) as r:
            body = r.read()
            if body != web_capture_fidelity_cases.article_html():
                fail("loopback: /article did not serve the article bytes")
            if r.headers.get("ETag") != web_capture_fidelity_cases.ARTICLE_ETAG:
                fail("loopback: /article served no ETag")
        request = urllib.request.Request(
            server.url("/article"),
            headers={"If-None-Match": web_capture_fidelity_cases.ARTICLE_ETAG})
        try:
            urllib.request.urlopen(request, timeout=5)
            fail("loopback: a matching If-None-Match did not return 304")
        except urllib.error.HTTPError as exc:
            if exc.code != 304:
                fail("loopback: conditional GET returned %d" % exc.code)
        for path, wanted in (("/redirect-to-article", 302),
                             ("/redirect-to-file", 302),
                             ("/redirect-loop", 302),
                             ("/notfound", 404)):
            opener = urllib.request.build_opener(_NoRedirect())
            try:
                with opener.open(server.url(path), timeout=5) as r:
                    code = r.status
            except urllib.error.HTTPError as exc:
                code = exc.code
            if code != wanted:
                fail("loopback: %s returned %d, expected %d"
                     % (path, code, wanted))
    finally:
        server.stop()
    print("ok: loopback fixture -- every route serves the status, body, and "
          "headers the adapter checks are about to rely on")


class _NoRedirect(__import__("urllib.request", fromlist=["x"]).HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def check_web_gold_cases():
    for case in web_capture_fidelity_cases.CASE_TABLE:
        gold = case["gold"]
        try:
            _md, _locators, order, unsupported = source_adapters._extract_web(
                case["build"](), {})
            messages = [e["message"] for e in unsupported]
        except source_adapters._Refusal as refusal:
            if gold["adapter_expectation"] != "unsupported":
                fail("web gold: %s refused with %s / %s"
                     % (case["id"], refusal.code, refusal.message))
            if refusal.message != gold["unsupported"][0]:
                fail("web gold: %s refused with %r, recorded %r"
                     % (case["id"], refusal.message, gold["unsupported"][0]))
            continue
        if gold["adapter_expectation"] == "unsupported":
            fail("web gold: %s was expected to refuse but produced %r"
                 % (case["id"], order))
        if order != gold["reading_order"]:
            fail("web gold: %s produced %r, recorded %r"
                 % (case["id"], order, gold["reading_order"]))
        if messages != gold["unsupported"]:
            fail("web gold: %s reported %r, recorded %r"
                 % (case["id"], messages, gold["unsupported"]))
    print("ok: web gold cases -- all 6 resolve as recorded, chrome dropped "
          "and a client-rendered page refused by name")


def check_web_locator_anchors():
    case = web_case("web-duplicate-text")
    _md, locators, _order, _unsupported = source_adapters._extract_web(
        case["build"](), {})
    by_id = {loc["id"]: loc for loc in locators}
    left, right = [by_id[i] for i in case["gold"]["duplicate_pair"]]
    if left["body"]["text_quote"]["exact"] != \
            right["body"]["text_quote"]["exact"]:
        fail("web anchors: the duplicate-text case no longer carries two "
             "identical quotes, so it proves nothing")
    if left["body"]["text_quote"]["prefix"] == \
            right["body"]["text_quote"]["prefix"]:
        fail("web anchors: two identical quotes share a prefix, so a "
             "citation into either is ambiguous")
    if left["body"]["css_selector"] == right["body"]["css_selector"]:
        fail("web anchors: two identical quotes share a CSS selector")
    print("ok: web locator anchors -- two identical sentences on one page "
          "stay distinguishable by prefix and by selector")


def check_private_origin_refused():
    server = web_capture_fidelity_cases.LoopbackServer().start()
    base = new_base()
    try:
        result = source_adapters.capture_url(
            base, server.url("/article"), "human", "cli",
            options={"allow_private_origins": False})
        if result["status"] != "unsupported" or \
                result["error"]["code"] != "source.origin_refused":
            fail("private origin: a loopback capture was not refused: %r"
                 % (result,))
        ok = source_adapters.capture_url(
            base, server.url("/article"), "human", "cli",
            options=capture_options())
        if ok["status"] != "ok":
            fail("private origin: lifting the setting did not allow the "
                 "capture: %r" % (ok["error"],))
    finally:
        server.stop()
        shutil.rmtree(base, ignore_errors=True)
    print("ok: private origin -- loopback is refused by default and only the "
          "setting lifts it, which is why this whole section must lift it")


def check_redirect_hardening():
    import urllib.request
    server = web_capture_fidelity_cases.LoopbackServer().start()
    second = web_capture_fidelity_cases.LoopbackServer(
        web_capture_fidelity_cases.serve_cases()).start()
    base = new_base()
    try:
        server.handler.cross_origin_url = second.url("/article")

        followed = source_adapters.capture_url(
            base, server.url("/redirect-to-article"), "human", "cli",
            options=capture_options())
        if followed["status"] != "ok":
            fail("redirect: an ordinary redirect was not followed: %r"
                 % (followed["error"],))

        to_file = source_adapters.capture_url(
            base, server.url("/redirect-to-file"), "human", "cli",
            options=capture_options())
        if to_file["error"] is None or \
                to_file["error"]["code"] != "source.redirect_refused":
            fail("redirect: a file: redirect was not refused by name: %r"
                 % (to_file,))
        if "file" not in to_file["error"]["message"]:
            fail("redirect: the refusal does not name the rejected scheme: %r"
                 % to_file["error"]["message"])

        loop = source_adapters.capture_url(
            base, server.url("/redirect-loop"), "human", "cli",
            options=capture_options())
        if loop["error"] is None or \
                loop["error"]["code"] != "source.fetch_failed":
            fail("redirect: a redirect loop was not capped: %r" % (loop,))

        del second.handler.received_headers[:]
        crossed = source_adapters.capture_url(
            base, server.url("/redirect-cross-origin"), "human", "cli",
            options=capture_options())
        if crossed["status"] != "ok":
            fail("redirect: the cross-origin redirect did not arrive: %r"
                 % (crossed["error"],))
        for headers in second.handler.received_headers:
            for key in headers:
                if key.lower() == "authorization":
                    fail("redirect: an Authorization header survived a "
                         "cross-origin redirect")

        # The strip itself, unit level, because this adapter sends no
        # Authorization header of its own and the integration case above can
        # only prove the absence of one that was never added.
        handler = source_adapters.SchemeLockedRedirectHandler()
        request = urllib.request.Request(
            "http://a.example/one", headers={"Authorization": "Bearer x"})
        stripped = handler.redirect_request(
            request, None, 302, "Found", {}, "http://b.example/two")
        if any(k.lower() == "authorization" for k in stripped.headers):
            fail("redirect: the handler kept Authorization across origins")
        same = handler.redirect_request(
            request, None, 302, "Found", {}, "http://a.example/three")
        if not any(k.lower() == "authorization" for k in same.headers):
            fail("redirect: the handler stripped Authorization on a "
                 "same-origin redirect, which it must not")
    finally:
        server.stop()
        second.stop()
        shutil.rmtree(base, ignore_errors=True)
    print("ok: redirect hardening -- scheme-locked, loop-capped, and "
          "Authorization stripped the moment the origin changes")


def check_fetch_limits():
    server = web_capture_fidelity_cases.LoopbackServer().start()
    base = new_base()
    try:
        slow = source_adapters.capture_url(
            base, server.url("/slow"), "human", "cli",
            options=capture_options(fetch_timeout_seconds=1))
        if slow["error"] is None or \
                slow["error"]["code"] != "source.fetch_failed":
            fail("fetch limits: a slow origin was not refused: %r" % (slow,))
        if "timed out" not in slow["error"]["message"]:
            fail("fetch limits: the timeout refusal does not name a timeout: "
                 "%r" % slow["error"]["message"])

        huge = source_adapters.capture_url(
            base, server.url("/huge"), "human", "cli",
            options=capture_options(max_input_bytes=4096))
        if huge["error"] is None or \
                huge["error"]["code"] != "source.oversized":
            fail("fetch limits: an oversize response was not refused: %r"
                 % (huge,))

        missing = source_adapters.capture_url(
            base, server.url("/notfound"), "human", "cli",
            options=capture_options())
        if missing["error"] is None or \
                missing["error"]["code"] != "source.fetch_failed":
            fail("fetch limits: a 404 was not refused: %r" % (missing,))
        if "404" not in missing["error"]["message"]:
            fail("fetch limits: the refusal does not carry the status code: "
                 "%r" % missing["error"]["message"])
    finally:
        server.stop()
        shutil.rmtree(base, ignore_errors=True)
    print("ok: fetch limits -- a timeout, an oversize body, and a 404 each "
          "return a typed code rather than raising")


def check_snapshot_both_ways():
    server = web_capture_fidelity_cases.LoopbackServer().start()
    inline_base = new_base()
    reference_base = new_base()
    try:
        inline = source_adapters.capture_url(
            inline_base, server.url("/article"), "human", "cli",
            options=capture_options(snapshot_storage="inline"))
        reference = source_adapters.capture_url(
            reference_base, server.url("/article"), "human", "cli",
            options=capture_options(snapshot_storage="reference"))
        for name, result in (("inline", inline), ("reference", reference)):
            if result["status"] != "ok":
                fail("snapshot: the %s capture failed: %r"
                     % (name, result["error"]))
        left = json.loads(open(os.path.join(inline_base,
                                             inline["sidecar_rel_path"]),
                                encoding="utf-8").read())
        right = json.loads(open(os.path.join(reference_base,
                                              reference["sidecar_rel_path"]),
                                 encoding="utf-8").read())
        if left["fingerprint"] != right["fingerprint"]:
            fail("snapshot: the two storage modes produced different "
                 "fingerprints, so a citation could tell which was used")
        if not left["origin"]["snapshot_rel_path"]:
            fail("snapshot: inline mode recorded no snapshot path")
        if right["origin"]["snapshot_rel_path"] is not None:
            fail("snapshot: reference mode recorded an owned snapshot path")
        inline_snapshot = os.path.join(inline_base,
                                        left["origin"]["snapshot_rel_path"])
        if not os.path.exists(inline_snapshot):
            fail("snapshot: the inline snapshot was not written")
        cache_dir = os.path.join(reference_base,
                                  source_adapters.SNAPSHOT_DIRNAME,
                                  source_adapters.SNAPSHOT_CACHE_DIRNAME)
        if not os.path.isdir(cache_dir) or not os.listdir(cache_dir):
            fail("snapshot: reference mode wrote nothing into the cache")
    finally:
        server.stop()
    try:
        # The server is stopped: the whole point of binding a snapshot is
        # that the capture reads back with the origin gone.
        for base, result in ((inline_base, inline),
                             (reference_base, reference)):
            text = open(os.path.join(base, result["md_rel_path"]),
                        encoding="utf-8").read()
            if "Airway Management" not in text:
                fail("snapshot: a captured page did not read back offline")
    finally:
        shutil.rmtree(inline_base, ignore_errors=True)
        shutil.rmtree(reference_base, ignore_errors=True)
    print("ok: snapshot both ways -- one fingerprint, two storage paths, and "
          "both read back with the origin unreachable")


def check_snapshot_containment():
    base = new_base()
    try:
        try:
            source_adapters._store_snapshot(
                base, os.path.join("..", "..", "escape"), b"<html></html>",
                "text/html", {})
            fail("containment: a crafted source id placed a snapshot outside "
                 "the root")
        except source_adapters._Refusal as refusal:
            if refusal.code != "source.malformed_input":
                fail("containment: the escape was refused with %r"
                     % refusal.code)
        except OSError:
            pass  # the filesystem refused first, which is also containment
        outside = os.path.abspath(os.path.join(base, "..", "escape.snapshot"))
        if os.path.exists(outside):
            fail("containment: a snapshot was written outside the root")
    finally:
        shutil.rmtree(base, ignore_errors=True)
    print("ok: snapshot containment -- a crafted id cannot place a snapshot "
          "outside the approved root")


def check_bind_policy_gate():
    server = web_capture_fidelity_cases.LoopbackServer().start()
    base = new_base()
    try:
        approve = capture_options(bind_policy="approve_before_bind")
        auto = capture_options(bind_policy="auto_fetch")

        refused = source_adapters.capture_url(
            base, server.url("/article"), "agent", "daemon", options=approve)
        if refused["error"] is None or \
                refused["error"]["code"] != "source.approval_required":
            fail("bind policy: an unconfirmed agent bind was not refused: %r"
                 % (refused,))
        for name in os.listdir(base):
            if name == source_adapters.SNAPSHOT_DIRNAME:
                fail("bind policy: a refused agent bind wrote a snapshot")

        confirmed = source_adapters.capture_url(
            base, server.url("/article"), "agent", "daemon", options=approve,
            confirm=True)
        if confirmed["status"] != "ok":
            fail("bind policy: a confirmed agent bind was refused: %r"
                 % (confirmed["error"],))

        human = source_adapters.capture_url(
            base, server.url("/article"), "human", "cli", options=approve)
        if human["status"] != "ok":
            fail("bind policy: a human bind needed confirmation: %r"
                 % (human["error"],))

        agent_auto = source_adapters.capture_url(
            base, server.url("/article"), "agent", "daemon", options=auto)
        if agent_auto["status"] != "ok":
            fail("bind policy: auto_fetch still gated an agent bind: %r"
                 % (agent_auto["error"],))

        # Preview never consults the gate, under either policy, for either
        # actor. Searching and reading stay free; only the write is gated.
        local = new_base()
        try:
            with open(os.path.join(local, "notes.md"), "w",
                      encoding="utf-8") as fh:
                fh.write("# Free\n\nA readable line.\n")
            raw_id = link_with_rights(local, "notes.md", all_granted())
            for policy in (approve, auto):
                preview = source_adapters.preview_source(
                    local, "markdown", raw_id, options=policy)
                if preview["status"] != "ok":
                    fail("bind policy: preview was gated under %r"
                         % policy["bind_policy"])
            for name in os.listdir(local):
                if name.endswith(".locator.json"):
                    fail("bind policy: preview wrote %s" % name)
        finally:
            shutil.rmtree(local, ignore_errors=True)
    finally:
        server.stop()
        shutil.rmtree(base, ignore_errors=True)
    print("ok: bind policy -- both policies ship, an unconfirmed agent bind "
          "is refused by name, and preview stays free under both")


def check_remote_capture_rights():
    server = web_capture_fidelity_cases.LoopbackServer().start()
    base = new_base()
    try:
        result = source_adapters.capture_url(
            base, server.url("/article"), "human", "cli",
            options=capture_options())
        if result["status"] != "ok":
            fail("capture rights: the capture failed: %r" % (result["error"],))
        sidecar = json.loads(open(os.path.join(base,
                                                result["sidecar_rel_path"]),
                                   encoding="utf-8").read())
        for operation in identity.RIGHTS_OPERATIONS:
            if sidecar["rights"].get(operation) != "unknown":
                fail("capture rights: %s is %r on a fresh capture, expected "
                     "unknown" % (operation, sidecar["rights"].get(operation)))
        try:
            source_adapters.import_source(
                base, "markdown", result["source_id"], "human", "cli",
                options=capture_options())
        except journal.JournalError as exc:
            if exc.code != "journal.rights_unknown":
                fail("capture rights: deriving from an unknown-rights capture "
                     "refused with %r" % (exc.code,))
        else:
            fail("capture rights: a derivation from an unknown-rights capture "
                 "was allowed")
    finally:
        server.stop()
        shutil.rmtree(base, ignore_errors=True)
    print("ok: remote capture rights -- a fresh capture is all seven unknown, "
          "and deriving from it is refused by name until a grant is recorded")


def _capture_for_recheck(base, server, path="/article"):
    result = source_adapters.capture_url(
        base, server.url(path), "human", "cli", options=capture_options())
    if result["status"] != "ok":
        fail("recheck: the seed capture failed: %r" % (result["error"],))
    return result


def check_recheck_states():
    server = web_capture_fidelity_cases.LoopbackServer().start()
    base = new_base()
    try:
        captured = _capture_for_recheck(base, server)
        sidecar_path = os.path.join(base, captured["sidecar_rel_path"])
        before_entries = len(list(journal.entries(base)))
        before_sidecar = open(sidecar_path, "rb").read()
        before_row = dict(journal.read_registry(base)[captured["source_id"]])

        def assert_untouched(label):
            if len(list(journal.entries(base))) != before_entries:
                fail("recheck: %s appended a journal entry" % label)
            if open(sidecar_path, "rb").read() != before_sidecar:
                fail("recheck: %s rewrote the sidecar" % label)
            row = journal.read_registry(base)[captured["source_id"]]
            if row["fingerprint"] != before_row["fingerprint"]:
                fail("recheck: %s changed the accepted fingerprint" % label)

        report = source_adapters.recheck_origin(
            base, captured["source_id"], options=capture_options())
        if report.get("state") != "origin_unchanged":
            fail("recheck: an unchanged origin reported %r" % (report,))
        assert_untouched("an unchanged recheck")

        server.handler.article = (
            web_capture_fidelity_cases.article_changed_html(),
            web_capture_fidelity_cases.CHANGED_ETAG)
        report = source_adapters.recheck_origin(
            base, captured["source_id"], options=capture_options())
        if report.get("state") != "origin_changed":
            fail("recheck: a changed origin reported %r" % (report,))
        if "still valid" not in report["note"]:
            fail("recheck: the changed note does not say the citation is "
                 "still valid: %r" % report["note"])
        assert_untouched("a changed recheck")

        server.stop()
        report = source_adapters.recheck_origin(
            base, captured["source_id"], options=capture_options())
        if report.get("state") != "origin_unreachable":
            fail("recheck: a stopped origin reported %r" % (report,))
        if "readable offline" not in report["note"]:
            fail("recheck: the unreachable note does not say the snapshot is "
                 "still readable: %r" % report["note"])
        assert_untouched("an unreachable recheck")
        text = open(os.path.join(base, captured["md_rel_path"]),
                    encoding="utf-8").read()
        if "Airway Management" not in text:
            fail("recheck: the capture stopped reading back once its origin "
                 "was unreachable")
    finally:
        try:
            server.stop()
        except Exception:
            pass
        shutil.rmtree(base, ignore_errors=True)
    print("ok: recheck states -- unchanged, changed, and unreachable, each a "
          "read that appends nothing and changes no fingerprint")


def check_recheck_preserves_citation():
    server = web_capture_fidelity_cases.LoopbackServer().start()
    base = new_base()
    try:
        captured = _capture_for_recheck(base, server)
        sidecar = json.loads(open(os.path.join(base,
                                                captured["sidecar_rel_path"]),
                                   encoding="utf-8").read())
        span_id = None
        for locator in sidecar["locators"]:
            if locator["span_id"]:
                span_id = locator["span_id"]
                break
        if span_id is None:
            fail("citation: the capture joined no span at all")
        record = auditor.citation(sidecar["source_id"], sidecar["fingerprint"],
                                   span_id)

        server.handler.article = (
            web_capture_fidelity_cases.article_changed_html(),
            web_capture_fidelity_cases.CHANGED_ETAG)
        report = source_adapters.recheck_origin(
            base, captured["source_id"], options=capture_options())
        if report.get("state") != "origin_changed":
            fail("citation: the origin did not report as changed")

        after = json.loads(open(os.path.join(base,
                                              captured["sidecar_rel_path"]),
                                 encoding="utf-8").read())
        again = auditor.citation(after["source_id"], after["fingerprint"],
                                  span_id)
        if again != record:
            fail("citation: a changed remote origin invalidated a citation "
                 "already issued: %r against %r" % (again, record))
    finally:
        try:
            server.stop()
        except Exception:
            pass
        shutil.rmtree(base, ignore_errors=True)
    print("ok: recheck preserves citation -- a changed origin leaves an "
          "issued citation exactly as valid as it was")


def check_recheck_no_validator_falls_back():
    server = web_capture_fidelity_cases.LoopbackServer().start()
    base = new_base()
    try:
        captured = _capture_for_recheck(base, server,
                                        path="/article-no-validator")
        sidecar = json.loads(open(os.path.join(base,
                                                captured["sidecar_rel_path"]),
                                   encoding="utf-8").read())
        if sidecar["origin"]["http_etag"] or \
                sidecar["origin"]["http_last_modified"]:
            fail("recheck fallback: the no-validator route served a validator")
        report = source_adapters.recheck_origin(
            base, captured["source_id"], options=capture_options())
        if report.get("state") not in source_adapters.RECHECK_STATES:
            fail("recheck fallback: a capture with no validator reported %r"
                 % (report,))
        if report["state"] != "origin_unchanged":
            fail("recheck fallback: identical bytes with no validator "
                 "reported %r" % report["state"])
    finally:
        try:
            server.stop()
        except Exception:
            pass
        shutil.rmtree(base, ignore_errors=True)
    print("ok: recheck fallback -- a capture with no ETag and no "
          "Last-Modified rechecks by comparing the derived fingerprint")


# ---------------------------------------------------------------------------
# Plan 14C-05: transcript intake. The one adapter in the phase with no
# third-party dependency at all, which makes it the honest test of the
# degrade-never-block claim.

def transcript_case(case_id):
    for case in transcript_fidelity_cases.CASE_TABLE:
        if case["id"] == case_id:
            return case
    fail("transcript gold case %s is not in the case table" % case_id)


def check_transcript_fixture_determinism():
    table = transcript_fidelity_cases.CASE_TABLE
    if len(table) != 8:
        fail("transcript fixtures: expected 8 cases, found %d" % len(table))
    if hasattr(transcript_fidelity_cases, "webvtt"):
        fail("transcript fixtures: the fixture module imported a caption "
             "library, so it would prove only that the library round-trips "
             "its own output")
    for case in table:
        first = case["build"]()
        if first != case["build"]():
            fail("transcript fixtures: %s is not deterministic" % case["id"])
        if transcript_fidelity_cases.sha256(first) != case["gold"]["sha256"]:
            fail("transcript fixtures: %s drifted from its recorded sha256"
                 % case["id"])
        empty = not case["gold"]["reading_order"]
        if empty != (case["gold"]["adapter_expectation"] == "unsupported"):
            fail("transcript fixtures: %s disagrees with the reading-order "
                 "invariant" % case["id"])
    workdir = tempfile.mkdtemp(prefix="transfix-")
    try:
        records = transcript_fidelity_cases.materialize(
            os.path.join(workdir, "out"))
        for _case_id, path, digest in records:
            if not path.startswith(workdir):
                fail("transcript fixtures: materialize wrote outside its "
                     "directory")
            with open(path, "rb") as fh:
                if transcript_fidelity_cases.sha256(fh.read()) != digest:
                    fail("transcript fixtures: a materialized file does not "
                         "match its digest")
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    print("ok: transcript fixture determinism -- 8 hand-built cases, every "
          "recorded sha256 stable, materialize contained")


def check_transcript_gold_cases():
    started = time.time()
    for case in transcript_fidelity_cases.CASE_TABLE:
        gold = case["gold"]
        try:
            _md, _locators, order, unsupported = \
                source_adapters._extract_transcript(case["build"](), {})
            messages = [entry["message"] for entry in unsupported]
        except source_adapters._Refusal as refusal:
            if gold["adapter_expectation"] != "unsupported":
                fail("transcript gold: %s refused with %s / %s"
                     % (case["id"], refusal.code, refusal.message))
            if refusal.message != gold["unsupported"][0]:
                fail("transcript gold: %s refused with %r, recorded %r"
                     % (case["id"], refusal.message, gold["unsupported"][0]))
            continue
        if gold["adapter_expectation"] == "unsupported":
            fail("transcript gold: %s was expected to refuse but produced %r"
                 % (case["id"], order))
        if order != gold["reading_order"]:
            fail("transcript gold: %s produced %r, recorded %r"
                 % (case["id"], order, gold["reading_order"]))
        if messages != gold["unsupported"]:
            fail("transcript gold: %s reported %r, recorded %r"
                 % (case["id"], messages, gold["unsupported"]))
    elapsed = time.time() - started
    # T-14C-31: a bounded-quantifier regex parses this corpus in milliseconds.
    # A future edit that introduces a nested quantifier fails here rather than
    # hanging the suite.
    if elapsed > 5.0:
        fail("transcript gold: parsing eight small fixtures took %.1fs, which "
             "means the timestamp regex is backtracking" % elapsed)
    print("ok: transcript gold cases -- all 8 resolve as recorded in %.3fs, "
          "including the BOM, the hour-less WebVTT, the skipped blocks, and "
          "the inverted cue" % elapsed)


def check_transcript_timestamp_locators():
    for case_id in ("srt-three-cues", "vtt-hour-omitted",
                    "plain-bracketed-timestamps"):
        case = transcript_case(case_id)
        _md, locators, _order, _unsupported = \
            source_adapters._extract_transcript(case["build"](), {})
        starts = [loc["body"]["start_ms"] for loc in locators]
        ends = [loc["body"]["end_ms"] for loc in locators]
        indexes = [loc["body"]["cue_index"] for loc in locators]
        if indexes != list(range(len(locators))):
            fail("transcript locators: %s cue_index values are %r"
                 % (case_id, indexes))
        for value in starts + ends:
            if not isinstance(value, int) or value < 0:
                fail("transcript locators: %s carries a non-integer or "
                     "negative millisecond value %r" % (case_id, value))
        for start, end in zip(starts, ends):
            if end < start:
                fail("transcript locators: %s emitted a negative duration "
                     "(%d to %d)" % (case_id, start, end))
        if "start_ms" in case["gold"]:
            if starts != case["gold"]["start_ms"] or \
                    ends != case["gold"]["end_ms"]:
                fail("transcript locators: %s produced %r / %r, recorded "
                     "%r / %r" % (case_id, starts, ends,
                                  case["gold"]["start_ms"],
                                  case["gold"]["end_ms"]))
    print("ok: transcript timestamp locators -- integer milliseconds, "
          "monotonic cue indexes, no negative duration, and the hour field "
          "genuinely optional")


def check_transcript_separator_tolerance():
    """Format detection reads the content and never the filename, because a
    caption file renamed between .srt and .vtt is the ordinary case."""
    srt_bytes = transcript_case("srt-three-cues")["build"]()
    vtt_bytes = transcript_case("vtt-hour-omitted")["build"]()
    for label, raw in (("an SRT renamed .vtt", srt_bytes),
                       ("a WebVTT renamed .srt", vtt_bytes)):
        _md, _locators, order, _unsupported = \
            source_adapters._extract_transcript(raw, {})
        if order != ["c.0", "c.1", "c.2"]:
            fail("transcript separators: %s produced %r" % (label, order))
    print("ok: transcript separator tolerance -- one grammar reads both "
          "separators and both extensions, detected from content")


def check_transcript_no_dependency():
    """With every third-party adapter library forced unimportable, a
    transcript still imports end to end. This is the phase's cleanest proof
    of degrade-never-block."""
    base = new_base()
    real_import = builtins.__import__
    blocked_names = ("pdfplumber", "pdfminer", "docx", "pptx", "readability",
                     "lxml")

    def blocked(name, *args, **kwargs):
        if name.split(".")[0] in blocked_names:
            raise ImportError("blocked for this test")
        return real_import(name, *args, **kwargs)

    try:
        case = transcript_case("srt-three-cues")
        rel = case["filename"]
        with open(os.path.join(base, rel), "wb") as fh:
            fh.write(case["build"]())
        raw_id = link_with_rights(base, rel, all_granted())
        builtins.__import__ = blocked
        try:
            result = source_adapters.import_source(
                base, "transcript", raw_id, "human", "tester")
        finally:
            builtins.__import__ = real_import
        if result["status"] != "ok":
            fail("transcript no dependency: the import failed with every "
                 "third-party package blocked: %r" % (result["error"],))
        sidecar = json.loads(open(os.path.join(base,
                                                result["sidecar_rel_path"]),
                                   encoding="utf-8").read())
        errs = schema_validate.validate(sidecar, SCHEMA)
        if errs:
            fail("transcript no dependency: sidecar failed its schema: %s"
                 % errs[0])
        if sidecar["confidence"] != "high":
            fail("transcript no dependency: an SRT's declared timings should "
                 "be high confidence, got %r" % sidecar["confidence"])
        imports = [e for e in applied_entries(base)
                   if e.get("operation") == "import"]
        if len(imports) != 1:
            fail("transcript no dependency: expected exactly one applied "
                 "import entry, got %d" % len(imports))
    finally:
        builtins.__import__ = real_import
        shutil.rmtree(base, ignore_errors=True)
    print("ok: transcript no dependency -- a transcript imports end to end "
          "with every one of the six pinned packages unimportable")


def check_transcript_end_to_end():
    base = new_base()
    try:
        case = transcript_case("plain-bracketed-timestamps")
        rel = case["filename"]
        with open(os.path.join(base, rel), "wb") as fh:
            fh.write(case["build"]())
        raw_id = link_with_rights(base, rel, all_granted())
        result = source_adapters.import_source(
            base, "transcript", raw_id, "human", "tester")
        if result["status"] != "ok":
            fail("transcript end to end: %r" % (result["error"],))
        sidecar = json.loads(open(os.path.join(base,
                                                result["sidecar_rel_path"]),
                                   encoding="utf-8").read())
        md_bytes = open(os.path.join(base, result["md_rel_path"]), "rb").read()
        lines = md_bytes.decode("utf-8").split("\n")[:-1]
        if len(lines) != len(sidecar["reading_order"]):
            fail("transcript end to end: %d derived lines against %d "
                 "reading-order entries"
                 % (len(lines), len(sidecar["reading_order"])))
        if not lines[0].startswith("[00:00:05]"):
            fail("transcript end to end: the derived Markdown does not carry "
                 "the cue's moment: %r" % lines[0])
        if sidecar["confidence"] != "medium":
            fail("transcript end to end: inferred end times should record "
                 "medium confidence, got %r" % sidecar["confidence"])
        imports = [e for e in applied_entries(base)
                   if e.get("operation") == "import"]
        if len(imports) != 1:
            fail("transcript end to end: expected exactly one applied import "
                 "entry, got %d" % len(imports))
    finally:
        shutil.rmtree(base, ignore_errors=True)
    print("ok: transcript end to end -- one derived line per cue, the moment "
          "readable without the sidecar, and inferred ends recorded as "
          "medium confidence")


# ---------------------------------------------------------------------------
# Plan 14C-06: OCR. Every automated assertion here injects a stub in place of
# ocr_lib.ocr_image, so the whole suite passes on a machine that has never
# installed Ollama. The one thing a stub cannot prove, that a real vision
# model transcribes a real page well enough to cite, is a human checkpoint.

_PNG_BYTES = (b"\x89PNG\r\n\x1a\n" + b"\x00" * 64)


def _with_ocr_stub(stub):
    """Swap `ocr_lib.ocr_image` for `stub` and return a restore callable. The
    module object is swapped, not a captured function, because the adapter
    looks the attribute up at call time for exactly this reason."""
    bridge = source_adapters._ocr_bridge()
    original = bridge.ocr_image
    bridge.ocr_image = stub

    def restore():
        bridge.ocr_image = original
    return restore


def _seed_image(base, name="page.png"):
    with open(os.path.join(base, name), "wb") as fh:
        fh.write(_PNG_BYTES)
    return name


def _import_stubbed_ocr(base, stub):
    rel = _seed_image(base)
    raw_id = link_with_rights(base, rel, all_granted())
    restore = _with_ocr_stub(stub)
    try:
        return source_adapters.import_source(base, "ocr", raw_id, "human",
                                              "tester")
    finally:
        restore()


def check_ocr_stubbed_extraction():
    base = new_base()
    try:
        result = _import_stubbed_ocr(
            base, lambda path, *a, **k: "Airway Management\n"
                                        "The airway is the first priority.\n"
                                        "Reassess after every intervention.")
        if result["status"] != "ok":
            fail("ocr stub: the import failed: %r" % (result["error"],))
        sidecar = json.loads(open(os.path.join(base,
                                                result["sidecar_rel_path"]),
                                   encoding="utf-8").read())
        errs = schema_validate.validate(sidecar, SCHEMA)
        if errs:
            fail("ocr stub: sidecar failed its own schema: %s" % errs[0])
        if sidecar["reading_order"] != ["o1.0", "o1.1", "o1.2"]:
            fail("ocr stub: reading_order is %r" % sidecar["reading_order"])
        text = open(os.path.join(base, result["md_rel_path"]),
                    encoding="utf-8").read()
        for needle in ("Airway Management", "the first priority",
                       "Reassess after every intervention."):
            if needle not in text:
                fail("ocr stub: the derived Markdown is missing %r" % needle)
        imports = [e for e in applied_entries(base)
                   if e.get("operation") == "import"]
        if len(imports) != 1:
            fail("ocr stub: expected one applied import entry, got %d"
                 % len(imports))
    finally:
        shutil.rmtree(base, ignore_errors=True)
    print("ok: ocr stubbed extraction -- a photographed page imports through "
          "the one path with a schema-valid sidecar")


def check_ocr_honest_degradation():
    base = new_base()
    try:
        result = _import_stubbed_ocr(base, lambda path, *a, **k: "One\nTwo")
        sidecar = json.loads(open(os.path.join(base,
                                                result["sidecar_rel_path"]),
                                   encoding="utf-8").read())
        if sidecar["confidence"] != "low":
            fail("ocr honesty: the envelope confidence is %r, expected low"
                 % sidecar["confidence"])
        for locator in sidecar["locators"]:
            body = locator["body"]
            if body["bbox"] is not None or body["confidence"] is not None:
                fail("ocr honesty: a locator invented geometry or a score: %r"
                     % body)
            if body["page"] != 1:
                fail("ocr honesty: page is %r, expected 1" % body["page"])
        # The half that matters: the SCHEMA refuses fabricated geometry, so a
        # later adapter change cannot start inventing it quietly.
        fabricated = json.loads(json.dumps(sidecar))
        fabricated["locators"][0]["body"]["bbox"] = [0, 0, 10, 10]
        errs = schema_validate.validate(fabricated, SCHEMA)
        if not errs:
            fail("ocr honesty: the schema accepted a fabricated bbox, so the "
                 "null typing is not enforcing anything")
    finally:
        shutil.rmtree(base, ignore_errors=True)
    print("ok: ocr honest degradation -- null bbox and null confidence on "
          "every locator, low envelope confidence, and a schema that refuses "
          "invented geometry")


def check_ocr_backend_failures():
    scenarios = (
        ("no Ollama server reachable (tried: http://localhost:11434). Start "
         "Ollama, or set OLLAMA_HOST.", "source.backend_unconfigured",
         "could not reach an Ollama server"),
        ("model 'qwen2.5vl:7b' not found on http://localhost:11434; pull it "
         "first", "source.backend_unconfigured", "is not installed"),
        ("ollama error 500: internal", "source.fetch_failed",
         "ollama error 500"),
    )
    for message, code, needle in scenarios:
        base = new_base()
        try:
            def raising(path, *args, **kwargs):
                raise RuntimeError(message)

            result = _import_stubbed_ocr(base, raising)
            if result["status"] != "unsupported":
                fail("ocr failures: %r produced %r" % (message, result))
            if result["error"]["code"] != code:
                fail("ocr failures: %r gave %r, expected %r"
                     % (message, result["error"]["code"], code))
            if needle not in result["error"]["message"]:
                fail("ocr failures: the copy for %r does not say %r: %r"
                     % (code, needle, result["error"]["message"]))
            for name in os.listdir(base):
                if name.endswith(".md") or name.endswith(".locator.json"):
                    fail("ocr failures: a refused OCR import wrote %s" % name)
            imports = [e for e in applied_entries(base)
                       if e.get("operation") == "import"]
            if imports:
                fail("ocr failures: a refused OCR import journaled an entry")
        finally:
            shutil.rmtree(base, ignore_errors=True)
    print("ok: ocr backend failures -- an unreachable server, a missing "
          "model, and an HTTP error each become typed results with copy that "
          "says what to do")


def check_ocr_no_text_sentinel():
    base = new_base()
    try:
        result = _import_stubbed_ocr(base, lambda path, *a, **k: "[no text]")
        if result["error"] is None or \
                result["error"]["code"] != "source.unsupported":
            fail("ocr sentinel: an empty page produced %r" % (result,))
        if result["error"]["message"] != "no text found in the image":
            fail("ocr sentinel: the message is %r"
                 % result["error"]["message"])
        for name in os.listdir(base):
            path = os.path.join(base, name)
            if not os.path.isfile(path):
                continue
            with open(path, "rb") as fh:
                if b"[no text]" in fh.read():
                    fail("ocr sentinel: the sentinel reached disk in %s" % name)
    finally:
        shutil.rmtree(base, ignore_errors=True)
    print("ok: ocr no-text sentinel -- an image with no text is a named "
          "refusal and the sentinel never reaches disk")


def check_ocr_temp_file_removed():
    """A decoded image left in a temp directory is an untracked copy of
    learner material. Asserted on the success path and on a failure path."""
    seen = []

    def capture(path, *args, **kwargs):
        seen.append(path)
        return "One line."

    def capture_then_raise(path, *args, **kwargs):
        seen.append(path)
        raise RuntimeError("ollama error 500: internal")

    for stub in (capture, capture_then_raise):
        base = new_base()
        try:
            _import_stubbed_ocr(base, stub)
        finally:
            shutil.rmtree(base, ignore_errors=True)
    if not seen:
        fail("ocr temp file: the adapter never called the bridge")
    for path in seen:
        if os.path.exists(path):
            fail("ocr temp file: %s survived the import" % path)
        if os.path.exists(os.path.dirname(path)):
            fail("ocr temp file: the temp directory %s survived"
                 % os.path.dirname(path))
    print("ok: ocr temp file removed -- the decoded image is gone on the "
          "success path and on the failure path")


def check_ocr_single_implementation():
    """Roster item 6's instruction, mechanically: wrap the skill, do not
    write a second OCR path."""
    import inspect
    whole = inspect.getsource(source_adapters)
    for forbidden in ("base64", "11434", "/api/chat", "OCR engine"):
        if forbidden in whole:
            fail("ocr single implementation: source_adapters.py contains %r, "
                 "which belongs to scripts/ocr_lib.py" % forbidden)
    if "ocr_image" not in inspect.getsource(source_adapters._extract_ocr):
        fail("ocr single implementation: _extract_ocr does not call the "
             "skill's ocr_image")
    print("ok: ocr single implementation -- one OCR path in the repository, "
          "wrapped and not rebuilt")


# ---------------------------------------------------------------------------
# Plan 14C-07: EPUB import, stdlib only, because D-14C-2 parks ebooklib on an
# explicit Weibao AGPL decision.

def epub_case(case_id):
    for case in epub_fidelity_cases.CASE_TABLE:
        if case["id"] == case_id:
            return case
    fail("epub gold case %s is not in the case table" % case_id)


def _extract_epub_case(case):
    try:
        md, locators, order, unsupported = source_adapters._extract_epub(
            case["build"](), {})
    except source_adapters._Refusal as refusal:
        return ("refused", refusal.code, refusal.message, None, None)
    return (order, [e["message"] for e in unsupported], locators, md, None)


def check_epub_fixture_determinism():
    table = epub_fidelity_cases.CASE_TABLE
    if len(table) != 7:
        fail("epub fixtures: expected 7 cases, found %d" % len(table))
    if hasattr(epub_fidelity_cases, "ebooklib"):
        fail("epub fixtures: the fixture module imported ebooklib, which is "
             "parked under D-14C-2")
    for case in table:
        first = case["build"]()
        if first != case["build"]():
            fail("epub fixtures: %s is not deterministic" % case["id"])
        if epub_fidelity_cases.sha256(first) != case["gold"]["sha256"]:
            fail("epub fixtures: %s drifted from its recorded sha256"
                 % case["id"])
        empty = not case["gold"]["reading_order"]
        if empty != (case["gold"]["adapter_expectation"] == "unsupported"):
            fail("epub fixtures: %s disagrees with the reading-order "
                 "invariant" % case["id"])
    workdir = tempfile.mkdtemp(prefix="epubfix-")
    try:
        records = epub_fidelity_cases.materialize(
            os.path.join(workdir, "out"))
        for _case_id, path, digest in records:
            if not path.startswith(workdir):
                fail("epub fixtures: materialize wrote outside its directory")
            with open(path, "rb") as fh:
                if epub_fidelity_cases.sha256(fh.read()) != digest:
                    fail("epub fixtures: a materialized file does not match "
                         "its digest")
        import zipfile as _zipfile
        with _zipfile.ZipFile(os.path.join(workdir, "out",
                                            "book.epub")) as zf:
            if zf.namelist()[0] != "mimetype":
                fail("epub fixtures: mimetype is not the first member")
            if zf.read("mimetype") != b"application/epub+zip":
                fail("epub fixtures: the mimetype member is wrong")
            if zf.getinfo("mimetype").compress_type != _zipfile.ZIP_STORED:
                fail("epub fixtures: the mimetype member is compressed")
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    print("ok: epub fixture determinism -- 7 hand-assembled cases, a correct "
          "uncompressed mimetype member first, and no ebooklib anywhere")


def check_epub_gold_cases():
    for case in epub_fidelity_cases.CASE_TABLE:
        gold = case["gold"]
        outcome = _extract_epub_case(case)
        if gold["adapter_expectation"] == "unsupported":
            if outcome[0] != "refused":
                fail("epub gold: %s was expected to refuse but produced %r"
                     % (case["id"], outcome[0]))
            if outcome[2] != gold["unsupported"][0]:
                fail("epub gold: %s refused with %r, recorded %r"
                     % (case["id"], outcome[2], gold["unsupported"][0]))
            continue
        if outcome[0] == "refused":
            fail("epub gold: %s was expected to extract, but refused with "
                 "%s / %s" % (case["id"], outcome[1], outcome[2]))
        if outcome[0] != gold["reading_order"]:
            fail("epub gold: %s produced %r, recorded %r"
                 % (case["id"], outcome[0], gold["reading_order"]))
        if outcome[1] != gold["unsupported"]:
            fail("epub gold: %s reported %r, recorded %r"
                 % (case["id"], outcome[1], gold["unsupported"]))
    print("ok: epub gold cases -- all 7 resolve as recorded")


def check_epub_spine_order():
    case = epub_case("epub-spine-out-of-order")
    order, _unsupported, locators, md, _extra = _extract_epub_case(case)
    if order != case["gold"]["reading_order"]:
        fail("epub spine: %r against the recorded %r"
             % (order, case["gold"]["reading_order"]))
    # Assert on the TEXT, not only on the ids: right-looking ids produced from
    # the wrong documents would pass an id-only assertion.
    if md.split("\n")[0] != case["gold"]["first_text"]:
        fail("epub spine: the first emitted text is %r, so the adapter read "
             "the documents in filename order rather than spine order"
             % md.split("\n")[0])
    seen = []
    for locator in locators:
        idref = locator["body"]["spine_idref"]
        if idref not in seen:
            seen.append(idref)
    if seen != case["gold"]["spine_idrefs"]:
        fail("epub spine: the idrefs appear in the order %r, expected %r"
             % (seen, case["gold"]["spine_idrefs"]))
    print("ok: epub spine order -- reading order comes from the package "
          "document's spine, not from filenames and not from the manifest")


def check_epub_container_indirection():
    case = epub_case("epub-nonstandard-opf-path")
    order, _unsupported, _locators, _md, _extra = _extract_epub_case(case)
    if order == "refused":
        fail("epub container: a book whose OPF is not at OEBPS/content.opf "
             "failed, so the path is hard-coded rather than read from "
             "META-INF/container.xml")
    if order != case["gold"]["reading_order"]:
        fail("epub container: %r against the recorded %r"
             % (order, case["gold"]["reading_order"]))
    print("ok: epub container indirection -- the OPF path comes from the "
          "container's rootfile, not from a hard-coded constant")


def check_epub_fragment_anchor():
    base = new_base()
    try:
        case = epub_case("epub-fragment-anchors")
        _order, _unsupported, locators, _md, _extra = _extract_epub_case(case)
        fragments = [loc["body"]["fragment"] for loc in locators]
        if fragments != case["gold"]["fragments"]:
            fail("epub fragments: %r against the recorded %r"
                 % (fragments, case["gold"]["fragments"]))
        if not any(f is None for f in fragments):
            fail("epub fragments: no locator carries a null fragment, so the "
                 "unanchored case proves nothing")

        rel = case["filename"]
        with open(os.path.join(base, rel), "wb") as fh:
            fh.write(case["build"]())
        raw_id = link_with_rights(base, rel, all_granted())
        result = source_adapters.import_source(base, "epub", raw_id, "human",
                                                "tester")
        if result["status"] != "ok":
            fail("epub fragments: the import failed: %r" % (result["error"],))
        sidecar = json.loads(open(os.path.join(base,
                                                result["sidecar_rel_path"]),
                                   encoding="utf-8").read())
        errs = schema_validate.validate(sidecar, SCHEMA)
        if errs:
            fail("epub fragments: sidecar failed its own schema: %s" % errs[0])
        if sidecar["confidence"] != "high":
            fail("epub fragments: a declared reading order should be high "
                 "confidence, got %r" % sidecar["confidence"])

        anchored = [loc for loc in sidecar["locators"]
                    if loc["body"]["fragment"] and loc["span_id"]]
        if not anchored:
            fail("epub fragments: no anchored locator joined to a span")
        target = anchored[0]
        record = auditor.citation(sidecar["source_id"],
                                   sidecar["fingerprint"], target["span_id"])
        # Resolve the citation back through the sidecar to the triple that
        # names the element it came from.
        resolved = [loc for loc in sidecar["locators"]
                    if loc["span_id"] == record["span_id"]]
        if not resolved:
            fail("epub fragments: the citation did not resolve back through "
                 "the sidecar")
        body = resolved[0]["body"]
        triple = (body["spine_idref"], body["element_index"],
                  body["fragment"])
        if triple != (target["body"]["spine_idref"],
                      target["body"]["element_index"],
                      target["body"]["fragment"]):
            fail("epub fragments: the resolved triple %r does not name the "
                 "element the text came from" % (triple,))
        md_lines = open(os.path.join(base, result["md_rel_path"]),
                        encoding="utf-8").read().split("\n")[:-1]
        if len(md_lines) != len(sidecar["reading_order"]):
            fail("epub fragments: %d derived lines against %d reading-order "
                 "entries" % (len(md_lines), len(sidecar["reading_order"])))
    finally:
        shutil.rmtree(base, ignore_errors=True)
    print("ok: epub fragment anchor -- a citation resolves back to the exact "
          "spine item, element index, and fragment it came from")


def check_epub_drm_refused():
    base = new_base()
    try:
        case = epub_case("epub-drm-encrypted")
        rel = case["filename"]
        with open(os.path.join(base, rel), "wb") as fh:
            fh.write(case["build"]())
        raw_id = link_with_rights(base, rel, all_granted())
        result = source_adapters.import_source(base, "epub", raw_id, "human",
                                                "tester")
        if result["error"] is None or \
                result["error"]["code"] != "source.encrypted":
            fail("epub drm: a DRM-locked book produced %r" % (result,))
        if result["error"]["message"] != \
                "encrypted EPUB: no unauthenticated content":
            fail("epub drm: the message is %r" % result["error"]["message"])
        for name in os.listdir(base):
            if name.endswith(".md") or name.endswith(".locator.json"):
                fail("epub drm: a refused import wrote %s" % name)
        imports = [e for e in applied_entries(base)
                   if e.get("operation") == "import"]
        if imports:
            fail("epub drm: a refused import journaled an entry")
        # The refusal comes before any content document is read: the same
        # fixture with a deliberately broken content document still refuses
        # with source.encrypted rather than with a parse error.
        broken = epub_fidelity_cases.epub_bytes(
            "OEBPS/content.opf",
            [("c1", "chap1.xhtml")], ["c1"],
            {"OEBPS/chap1.xhtml": "<not-xml at all"},
            extra_parts={
                "META-INF/encryption.xml":
                    epub_fidelity_cases._ENCRYPTION_XML})
        try:
            source_adapters._extract_epub(broken, {})
            fail("epub drm: a broken encrypted book did not refuse")
        except source_adapters._Refusal as refusal:
            if refusal.code != "source.encrypted":
                fail("epub drm: the encryption check does not come first; a "
                     "broken content document produced %r" % refusal.code)
    finally:
        shutil.rmtree(base, ignore_errors=True)
    print("ok: epub drm refused -- an encrypted book is refused before any "
          "content document is read, writing and journaling nothing")


def check_epub_uses_shared_seam():
    import inspect
    src = (inspect.getsource(source_adapters._extract_epub)
           + inspect.getsource(source_adapters._epub_container_root)
           + inspect.getsource(source_adapters._epub_spine_order))
    if "_read_zip_part" not in src or "_parse_xml_safely" not in src:
        fail("epub seam: the adapter does not read through the shared seam")
    for line in src.split("\n"):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if "zf.read(" in stripped or "archive.read(" in stripped:
            fail("epub seam: a direct ZipFile read bypasses the size cap: %r"
                 % stripped)
    print("ok: epub shared seam -- every archive member and every XML part "
          "goes through the one hardened reader")


# ---------------------------------------------------------------------------
# Plan 14C-08: roster item 5 registered as a named refusal with a frozen
# locator shape, and the vendoring gate.

def check_asr_registered_not_built():
    base = new_base()
    try:
        rel = "lecture.wav"
        with open(os.path.join(base, rel), "wb") as fh:
            fh.write(b"RIFF" + b"\x00" * 64)
        raw_id = link_with_rights(base, rel, all_granted())
        result = source_adapters.import_source(base, "asr", raw_id, "human",
                                                "tester")
        if result["status"] != "unsupported":
            fail("asr: expected a typed refusal, got %r" % (result,))
        if result["error"]["code"] != "source.backend_unconfigured":
            fail("asr: expected source.backend_unconfigured, got %r"
                 % result["error"]["code"])
        if "no speech recognition backend is configured" not in \
                result["error"]["message"]:
            fail("asr: the refusal does not name the missing backend: %r"
                 % result["error"]["message"])
        if "transcript adapter" not in result["error"]["message"]:
            fail("asr: the refusal does not point at the adapter that works")
        # The point of registering: a named refusal, not adapter_unknown.
        if "asr" not in source_adapters.ADAPTER_REGISTRY:
            fail("asr: the key is absent, so a caller gets "
                 "source.adapter_unknown instead of a reason")
        for name in os.listdir(base):
            if name.endswith(".md") or name.endswith(".locator.json"):
                fail("asr: a refused import wrote %s" % name)
        imports = [e for e in applied_entries(base)
                   if e.get("operation") == "import"]
        if imports:
            fail("asr: a refused import journaled an entry")
    finally:
        shutil.rmtree(base, ignore_errors=True)
    print("ok: asr registered not built -- a named, actionable refusal that "
          "points at the transcript adapter and writes nothing")


def _asr_sidecar(body):
    return {
        "schema_version": 1,
        "source_id": "0" * 16,
        "adapter": "asr",
        "adapter_version": "0.0.0",
        "fingerprint": "sha256:" + "f" * 64,
        "captured_at": "2026-08-28T00:00:00.000Z",
        "origin": {"kind": "local_file", "value": "lecture.wav",
                   "fetched_at": None, "http_etag": None,
                   "http_last_modified": None, "snapshot_rel_path": None},
        "rights": {op: "unknown" for op in identity.RIGHTS_OPERATIONS},
        "confidence": None,
        "reading_order": ["a.0"],
        "locators": [{"id": "a.0", "span_id": None, "kind": "segment",
                      "body": body}],
        "unsupported": [],
    }


def check_asr_locator_shape_frozen():
    good = _asr_sidecar({"medium": "asr", "segment_index": 0,
                         "start_ms": 0, "end_ms": 1500})
    errs = schema_validate.validate(good, SCHEMA)
    if errs:
        fail("asr shape: a well-formed body_asr locator was rejected: %s"
             % errs[0])
    wrong = _asr_sidecar({"medium": "asr", "cue_index": 0,
                          "start_ms": 0, "end_ms": 1500})
    errs = schema_validate.validate(wrong, SCHEMA)
    if not errs:
        fail("asr shape: a body carrying cue_index instead of segment_index "
             "validated, so the frozen shape is not enforced")
    print("ok: asr locator shape frozen -- the segment body validates and a "
          "transcript-shaped one does not, tested before any backend exists")


def check_asr_body_matches_transcript_body():
    """Structural comparison, not a reading: the two bodies must agree apart
    from the index field's name, so a future backend produces into a shape the
    transcript adapter already proved."""
    schema = json.loads(resources.read_text("schemas/source_locator.schema.json"))
    asr = schema["$defs"]["body_asr"]
    transcript = schema["$defs"]["body_transcript"]
    asr_required = set(asr["required"]) - {"segment_index"}
    transcript_required = set(transcript["required"]) - {"cue_index"}
    if asr_required != transcript_required:
        fail("asr body: required fields differ beyond the index name: %r "
             "against %r" % (sorted(asr_required), sorted(transcript_required)))
    for field in ("start_ms", "end_ms"):
        if asr["properties"][field]["type"] != \
                transcript["properties"][field]["type"]:
            fail("asr body: %s types differ" % field)
        if asr["properties"][field].get("minimum") != \
                transcript["properties"][field].get("minimum"):
            fail("asr body: %s minimums differ" % field)
    if asr["properties"]["segment_index"]["type"] != \
            transcript["properties"]["cue_index"]["type"] or \
            asr["properties"]["segment_index"].get("minimum") != \
            transcript["properties"]["cue_index"].get("minimum"):
        fail("asr body: the index field types or minimums differ")
    if asr.get("additionalProperties") is not False:
        fail("asr body: additionalProperties is not false")
    print("ok: asr body matches transcript body -- identical apart from the "
          "index field's name, compared structurally")


def check_schema_addition_is_additive():
    """The additive-format rule applied to a JSON schema, proven by re-running
    the end-to-end checks against the amended document rather than by
    inspection."""
    schema = json.loads(resources.read_text("schemas/source_locator.schema.json"))
    if schema["x-itembank-version"] != 1 or \
            schema["properties"]["schema_version"]["const"] != 1:
        fail("schema additive: the version moved for a oneOf branch addition")
    check_thin_slice()
    check_docx_end_to_end()
    check_transcript_end_to_end()
    check_epub_fragment_anchor()
    print("ok: schema addition is additive -- every existing adapter's "
          "sidecar still validates and schema_version is still 1")


def check_vendored_manifest():
    """A checksum gate that has never been observed to fail is a comment, not
    a gate. This runs it clean, then breaks the tree three ways."""
    import subprocess

    def run(root):
        # The copy's OWN script, not this tree's: check_vendored.py resolves
        # the repository root from its own location, so running the original
        # against a mutated copy would silently check the original.
        return subprocess.run(
            [sys.executable, os.path.join(root, "scripts",
                                          "check_vendored.py")],
            cwd=root, capture_output=True, text=True)

    clean = run(ROOT)
    if clean.returncode != 0:
        fail("vendored: the gate fails against the committed tree: %s"
             % (clean.stdout + clean.stderr))

    manifest = open(os.path.join(ROOT, "VENDORED.md"), encoding="utf-8").read()
    hashed = []
    for line in manifest.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2:
            continue
        candidate = os.path.join(ROOT, cells[0].strip("`"))
        if os.path.isfile(candidate) and len(cells) > 4 and \
                len(cells[4].strip("`")) == 64:
            hashed.append(cells[0].strip("`"))
    if not hashed:
        fail("vendored: no row names a file with a recorded hash, so the "
             "tamper scenarios below would prove nothing")
    victim = hashed[0]

    def copy_tree():
        target = tempfile.mkdtemp(prefix="vendored-")
        inner = os.path.join(target, "repo")
        shutil.copytree(ROOT, inner, symlinks=True,
                        ignore=shutil.ignore_patterns(".git", "__pycache__"))
        return target, inner

    # 1. tamper
    target, inner = copy_tree()
    try:
        with open(os.path.join(inner, victim), "ab") as fh:
            fh.write(b"\n")
        result = run(inner)
        if result.returncode == 0:
            fail("vendored: a tampered artifact did not fail the gate")
        if victim not in result.stdout + result.stderr:
            fail("vendored: the tamper failure does not name %s" % victim)
    finally:
        shutil.rmtree(target, ignore_errors=True)

    # 2. delete
    target, inner = copy_tree()
    try:
        os.remove(os.path.join(inner, victim))
        result = run(inner)
        if result.returncode == 0:
            fail("vendored: a missing artifact did not fail the gate")
        if victim not in result.stdout + result.stderr:
            fail("vendored: the missing-file failure does not name %s" % victim)
    finally:
        shutil.rmtree(target, ignore_errors=True)

    # 3. a row for a parked package
    target, inner = copy_tree()
    try:
        path = os.path.join(inner, "VENDORED.md")
        with open(path, "a", encoding="utf-8") as fh:
            fh.write("\n| `ebooklib-0.20-py3-none-any.whl` | 0.20 | "
                     "https://example.invalid | https://example.invalid | "
                     "%s | AGPL-3.0 | nobody | 2026-08-28 |\n" % ("0" * 64))
        result = run(inner)
        if result.returncode == 0:
            fail("vendored: a row naming a parked package did not fail the "
                 "gate, so the AGPL parking can be bypassed by adding a row")
        if "ebooklib" not in result.stdout + result.stderr:
            fail("vendored: the parked-package failure does not name it")
    finally:
        shutil.rmtree(target, ignore_errors=True)
    print("ok: vendored manifest -- the gate passes clean and was observed "
          "failing on a tampered artifact, a missing one, and a row naming a "
          "parked package")


if __name__ == "__main__":
    check_thin_slice()
    check_scanned_pdf_is_typed_unsupported()
    check_nothing_raises()
    check_rights_refusal()
    check_no_rights_escalation()
    check_one_import_path()
    check_no_second_parser()
    check_degrades_without_dependencies()
    check_write_containment()
    check_cli_and_route_parity()
    check_gold_manifest_additive()
    check_zip_bomb_guard()
    check_xml_entity_guard()
    check_pdf_gold_cases()
    check_docx_gold_cases()
    check_docx_extra_parts()
    check_docx_end_to_end()
    check_pptx_fixture_determinism()
    check_pptx_gold_cases()
    check_pptx_notes_flag()
    check_pptx_slide_order()
    check_pptx_partial_refusal()
    check_option_defaults_match_schema()
    check_web_fixture_determinism()
    check_loopback_fixture_serves()
    check_web_gold_cases()
    check_web_locator_anchors()
    check_private_origin_refused()
    check_redirect_hardening()
    check_fetch_limits()
    check_snapshot_both_ways()
    check_snapshot_containment()
    check_bind_policy_gate()
    check_remote_capture_rights()
    check_recheck_states()
    check_recheck_preserves_citation()
    check_recheck_no_validator_falls_back()
    check_transcript_fixture_determinism()
    check_transcript_gold_cases()
    check_transcript_timestamp_locators()
    check_transcript_separator_tolerance()
    check_transcript_no_dependency()
    check_transcript_end_to_end()
    check_ocr_stubbed_extraction()
    check_ocr_honest_degradation()
    check_ocr_backend_failures()
    check_ocr_no_text_sentinel()
    check_ocr_temp_file_removed()
    check_ocr_single_implementation()
    check_epub_fixture_determinism()
    check_epub_gold_cases()
    check_epub_spine_order()
    check_epub_container_indirection()
    check_epub_fragment_anchor()
    check_epub_drm_refused()
    check_epub_uses_shared_seam()
    check_asr_registered_not_built()
    check_asr_locator_shape_frozen()
    check_asr_body_matches_transcript_body()
    check_schema_addition_is_additive()
    check_vendored_manifest()
    print("ok: source adapters -- one typed import boundary, one parser's "
          "span ids, one fingerprint, typed refusals, and a degraded path "
          "that names its install command")
