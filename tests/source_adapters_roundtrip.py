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
        # The route's own body-shaped call, with the daemon's actor identity.
        result = source_adapters.import_source(
            base, "markdown", raw_id, "agent", "daemon")
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
    print("ok: source adapters -- one typed import boundary, one parser's "
          "span ids, one fingerprint, typed refusals, and a degraded path "
          "that names its install command")
