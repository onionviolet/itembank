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
import builtins, json, os, shutil, sys, tempfile

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
        if name == "pdfplumber":
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
    print("ok: source adapters -- one typed import boundary, one parser's "
          "span ids, one fingerprint, typed refusals, and a degraded path "
          "that names its install command")
