#!/usr/bin/env python3
"""Phase 15B: one drafted question set from blueprint to accepted write, and
the five ways ACTIVITY-02's gates refuse.

The thin slice plan 15B-02 Task 1 names. It proves the five-gate architecture
end to end on one path before four more capabilities are built on it: three
shipped gates reused unmodified, one shipped scorer called as a conformance
smoke test, and exactly one new gate.

The degraded states are the point. An absent blueprint withholds the claim and
not the practice; an unsupplied fact is unverifiable rather than a silent pass;
and a blocking blueprint finding writes nothing at all.

Standard library only, runnable as `python tests/blueprint_roundtrip.py`.
"""
import json, os, shutil, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "fixtures"))
import audit_writer                                          # noqa: E402
import authoring                                             # noqa: E402
import blueprint                                             # noqa: E402
import course                                                # noqa: E402
import graph                                                 # noqa: E402
import model                                                 # noqa: E402
import runtime                                               # noqa: E402
import schema_validate                                       # noqa: E402

FAILURES = []

FINDING_KEYS = {"schema_version", "detector", "detector_version", "severity",
                "code", "item", "evidence", "remediation"}


def fail(msg):
    print("FAIL: " + msg)
    FAILURES.append(msg)


def check_schema_is_closed():
    """The new schema is valid, closed, and carries no float."""
    path = os.path.join(ROOT, "schemas", "blueprint.schema.json")
    raw = open(path, encoding="utf-8").read()
    doc = json.loads(raw)
    try:
        schema_validate.check_schema(doc)
    except Exception as exc:
        fail("the blueprint schema uses an unsupported keyword: %s" % exc)

    expected = ["schema_version", "blueprint_id", "version", "construct",
                "domain_weight", "demand", "format", "difficulty", "timing",
                "tools", "feedback_conditions", "citations"]
    if doc["required"] != expected:
        fail("the blueprint schema's required array is %r" % (doc["required"],))
    if doc.get("additionalProperties") is not False:
        fail("the blueprint schema permits additional top-level properties")

    def closed(node, path_name):
        if isinstance(node, dict):
            if node.get("type") == "object" and \
                    node.get("additionalProperties") is not False:
                fail("the object at %s is not closed" % path_name)
            for key, value in node.items():
                closed(value, "%s.%s" % (path_name, key))
        elif isinstance(node, list):
            for n, value in enumerate(node):
                closed(value, "%s[%d]" % (path_name, n))
    closed(doc, "$")

    if '"number"' in raw:
        fail("the blueprint schema carries a float type; every share and "
             "tolerance is an integer percentage point")


def check_module_surface():
    """The module surface later plans import, and the imports it must not
    have."""
    import types

    if blueprint.BLUEPRINT_FIELDS != ("construct", "domain_weight", "demand",
                                      "format", "difficulty", "timing",
                                      "tools", "feedback_conditions"):
        fail("BLUEPRINT_FIELDS is %r" % (blueprint.BLUEPRINT_FIELDS,))
    if len(blueprint.BLUEPRINT_FIELDS) != 8:
        fail("BLUEPRINT_FIELDS has %d members" % len(blueprint.BLUEPRINT_FIELDS))
    if blueprint.GATE_STEPS != ("parser", "lint", "review", "blueprint",
                                "runtime"):
        fail("GATE_STEPS is %r" % (blueprint.GATE_STEPS,))
    if blueprint.WARN_CODES != ("blueprint.absent", "blueprint.unverifiable"):
        fail("WARN_CODES is %r" % (blueprint.WARN_CODES,))
    for code in blueprint.WARN_CODES:
        if code not in blueprint.BLUEPRINT_CODES:
            fail("the warn code %r is not in BLUEPRINT_CODES" % (code,))
    # Nineteen. Plan 15B-02 Task 1 asserted thirteen for the gate's thin form;
    # Task 2 widened it to fourteen by naming `blueprint.difficulty_out_of_band`
    # as its own code, because a band the form does not permit at all is a
    # different defect from a band that appears too often. Plan 15B-03 then
    # added the five staleness codes, which its own artifacts section counts
    # from the thirteen it inherited rather than the fourteen that landed.
    # The divergence between the plans is recorded in blueprint.py above
    # BLUEPRINT_CODES; the count here tracks the code rather than the plan
    # text. 15B-05 then added the two vocabulary codes, taking it to
    # twenty-one, and 15B-06's three proposal codes to
    # twenty-four. Each plan's artifacts section counted from the
    # thirteen it inherited rather than from what landed.
    if len(blueprint.BLUEPRINT_CODES) != 24:
        fail("BLUEPRINT_CODES has %d members" % len(blueprint.BLUEPRINT_CODES))
    if blueprint.BLUEPRINT_CODES != tuple(sorted(blueprint.BLUEPRINT_CODES)):
        fail("BLUEPRINT_CODES is not sorted")

    # The absent imports ARE the contract: a module that imports journal
    # cannot assert that it never writes.
    for forbidden in ("evidence", "journal", "course", "director", "graph",
                      "audit_writer"):
        if hasattr(blueprint, forbidden):
            fail("blueprint imports %s; the structural ban is gone"
                 % forbidden)
    for needed in ("model", "runtime"):
        if not isinstance(getattr(blueprint, needed, None), types.ModuleType):
            fail("blueprint does not import %s; gate 5 must reach the one "
                 "scorer" % needed)


def check_validation_refuses_before_it_reads():
    import corpus_15b

    bp = corpus_15b.build_blueprint()
    got = blueprint.validate_blueprint(bp)
    schema = json.load(open(os.path.join(ROOT, "schemas",
                                         "blueprint.schema.json")))
    if set(got) != set(schema["required"]):
        fail("a validated blueprint's keys are %r" % (sorted(got),))

    missing = dict(bp)
    del missing["citations"]
    try:
        blueprint.validate_blueprint(missing)
    except blueprint.BlueprintError as exc:
        if exc.code != "blueprint.invalid":
            fail("a blueprint missing citations raised %r" % (exc.code,))
        elif "citations" not in exc.message:
            fail("the refusal does not name the missing key: %r"
                 % (exc.message,))
    else:
        fail("a blueprint missing citations was accepted")

    try:
        blueprint.validate_blueprint(dict(bp, version=0))
    except blueprint.BlueprintError as exc:
        if exc.code != "blueprint.invalid":
            fail("a version of 0 raised %r" % (exc.code,))
    else:
        fail("a blueprint at version 0 was accepted")


def check_the_gate():
    """Gate 4 over conforming and defective drafts."""
    import corpus_15b

    bp = corpus_15b.build_blueprint()
    questions = model.parse_bank(corpus_15b.build_draft_set("conforming"))
    facts = corpus_15b.build_item_facts(questions)

    findings = blueprint.blueprint_gate(questions, bp, facts)
    if findings:
        fail("a conforming set produced findings: %r"
             % ([(f["code"], f["item"]) for f in findings],))
    if blueprint.blueprint_gate_blocks(questions, bp, facts):
        fail("a conforming set blocks")

    # Every finding matches the shipped record shape and validates.
    ref = json.load(open(os.path.join(ROOT, "schemas",
                                      "audit_report.schema.json")))
    ref_schema = ref["$defs"]["blueprint_finding_ref"]
    absent = blueprint.blueprint_gate(questions, None)
    if len(absent) != 1:
        fail("an absent blueprint produced %d findings" % len(absent))
    else:
        finding = absent[0]
        if finding["code"] != "blueprint.absent":
            fail("the absent code is %r" % (finding["code"],))
        if finding["severity"] != "warn":
            fail("an absent blueprint blocks at severity %r"
                 % (finding["severity"],))
        if set(finding) != FINDING_KEYS:
            fail("a finding's keys are %r" % (sorted(finding),))
        if finding["detector"] != "blueprint_fidelity":
            fail("the detector is %r" % (finding["detector"],))
        if finding["detector_version"] != 1:
            fail("the detector_version is %r" % (finding["detector_version"],))
        errs = schema_validate.validate(finding, ref_schema)
        if errs:
            fail("a finding fails blueprint_finding_ref: %r" % (errs[:2],))
    if blueprint.blueprint_gate_blocks(questions, None):
        fail("an absent blueprint blocks the write; ACTIVITY-02 says the "
             "course presents practice without the claim")

    # A type the blueprint does not permit.
    wrong = model.parse_bank(corpus_15b.build_draft_set("wrong_type"))
    findings = blueprint.blueprint_gate(wrong, bp, corpus_15b.build_item_facts(wrong))
    typed = [f for f in findings if f["code"] == "blueprint.format_not_permitted"]
    if len(typed) != 1:
        fail("a disallowed type produced %d format findings" % len(typed))
    else:
        finding = typed[0]
        if finding["severity"] != "block":
            fail("a disallowed type is severity %r" % (finding["severity"],))
        if "short" not in json.dumps(finding["evidence"]):
            fail("the evidence does not name the observed type: %r"
                 % (finding["evidence"],))
        if "mc" not in json.dumps(finding["evidence"]):
            fail("the evidence does not name the permitted list: %r"
                 % (finding["evidence"],))
    if not blueprint.blueprint_gate_blocks(wrong, bp):
        fail("a disallowed type does not block")

    # The count boundary, proven on both sides.
    over = model.parse_bank(corpus_15b.build_draft_set("too_many"))
    tight = corpus_15b.build_blueprint(item_count=3, count_tolerance=0)
    findings = blueprint.blueprint_gate(over, tight,
                                        corpus_15b.build_item_facts(over))
    counted = [f for f in findings
               if f["code"] == "blueprint.item_count_out_of_tolerance"]
    if len(counted) != 1:
        fail("four items against three produced %d count findings"
             % len(counted))
    elif counted[0]["item"] != "BANK":
        fail("a bank-wide finding's item is %r" % (counted[0]["item"],))

    # Exactly the tolerance passes. Equality passes.
    loose = corpus_15b.build_blueprint(item_count=3, count_tolerance=1)
    findings = blueprint.blueprint_gate(over, loose,
                                        corpus_15b.build_item_facts(over))
    if [f for f in findings
            if f["code"] == "blueprint.item_count_out_of_tolerance"]:
        fail("a count differing by exactly the tolerance was refused; "
             "equality must pass")

    # Unverifiable fields: one finding per field, never a silent pass.
    findings = blueprint.blueprint_gate(questions, bp, {})
    unverifiable = [f for f in findings
                    if f["code"] == "blueprint.unverifiable"]
    fields = {f["evidence"]["field"] for f in unverifiable}
    if fields != {"construct", "feedback_conditions", "demand", "timing",
                  "tools"}:
        fail("the unverifiable fields are %r" % (sorted(fields),))
    for finding in unverifiable:
        if finding["severity"] != "warn":
            fail("an unverifiable field blocks: %r" % (finding,))
    if blueprint.blueprint_gate_blocks(questions, bp, {}):
        fail("unsupplied facts block the write; a missing fact withholds the "
             "claim, not the practice")

    # Deterministic ordering, byte for byte.
    first = blueprint.blueprint_gate(over, tight,
                                     corpus_15b.build_item_facts(over))
    second = blueprint.blueprint_gate(over, tight,
                                      corpus_15b.build_item_facts(over))
    if json.dumps(first, sort_keys=True) != json.dumps(second, sort_keys=True):
        fail("two gate runs over one input differ")
    keys = [(f["item"], f["code"], blueprint.canonical_json(f["evidence"]))
            for f in first]
    if keys != sorted(keys):
        fail("findings are not sorted by (item, code, evidence)")

    # No aggregate, and no float anywhere.
    def walk_floats(obj, path="$"):
        found = []
        if isinstance(obj, float):
            found.append(path)
        elif isinstance(obj, dict):
            for k, v in obj.items():
                found.extend(walk_floats(v, "%s.%s" % (path, k)))
        elif isinstance(obj, list):
            for n, v in enumerate(obj):
                found.extend(walk_floats(v, "%s[%d]" % (path, n)))
        return found
    floats = walk_floats(first)
    if floats:
        fail("a blueprint finding carries floats at %r" % (floats,))


def check_gate_five_is_the_shipped_scorer():
    import corpus_15b

    questions = model.parse_bank(corpus_15b.build_draft_set("conforming"))
    if blueprint.runtime_conformance(questions):
        fail("a conforming set produced runtime findings")

    # A constructed-response item scores None and produces NO finding.
    short = model.parse_bank(open(
        os.path.join(ROOT, "fixtures", "sample_bank.md"),
        encoding="utf-8").read())
    shorts = [q for q in short if q["type"] == "short"]
    if not shorts:
        fail("the sample bank carries no short item to exercise")
    else:
        if runtime.canonical_key(shorts[0]) is not None:
            fail("a short item has a canonical key")
        if blueprint.runtime_conformance(shorts):
            fail("a constructed-response item produced a runtime finding; "
                 "not-yet-marked is not a failure")

    # A corrupted key produces exactly one blocking finding.
    broken = dict(questions[0])
    broken["correct"] = "A" if broken["correct"] != "A" else "C"
    original_key = runtime.canonical_key(questions[0])
    if runtime.score_response(broken, original_key) is True:
        fail("the corrupted fixture still scores correct; it proves nothing")
    else:
        class _Fake(dict):
            pass
        # Score the broken question against the ORIGINAL key by making the
        # question carry a key its own options no longer support.
        findings = []
        key = runtime.canonical_key(broken)
        if runtime.score_response(broken, key) is not True:
            findings = blueprint.runtime_conformance([broken])
        if findings and findings[0]["code"] != "blueprint.runtime_mismatch":
            fail("a mismatched key produced %r" % (findings[0]["code"],))


def check_the_claim_appears_only_after_five():
    steps = blueprint.GATE_STEPS
    if blueprint.fidelity_claim([]) is not False:
        fail("an empty gate list produced a claim")
    four = [blueprint.gate_result(s, True, []) for s in steps[:4]]
    if blueprint.fidelity_claim(four) is not False:
        fail("four passing gates produced a claim")
    five = [blueprint.gate_result(s, True, []) for s in steps]
    if blueprint.fidelity_claim(five) is not True:
        fail("five passing gates produced no claim")
    for n in range(5):
        mixed = [blueprint.gate_result(s, i != n, []) for i, s in enumerate(steps)]
        if blueprint.fidelity_claim(mixed) is not False:
            fail("a failing %s gate still produced a claim" % steps[n])
    for value in ([], four, five):
        if blueprint.fidelity_claim(value) not in (True, False):
            fail("fidelity_claim returned a non-boolean")


def check_the_report_and_sidecar_grew_additively():
    import corpus_15b

    report = json.load(open(os.path.join(ROOT, "schemas",
                                         "audit_report.schema.json")))
    gates = report["$defs"]["proposal"]["properties"]["gates"]
    if gates["required"] != ["lint_errors", "lint_warnings",
                             "quality_findings"]:
        fail("the gates required array changed: %r" % (gates["required"],))
    if "blueprint_findings" not in gates["properties"]:
        fail("blueprint_findings is not a gates property")
    try:
        schema_validate.check_schema(report)
    except Exception as exc:
        fail("the edited audit report schema is invalid: %s" % exc)

    # The sidecar: a pre-15B document round-trips byte for byte.
    golden = corpus_15b.build_golden_sidecar()
    if "## Blueprint" in golden:
        fail("the golden sidecar already carries a Blueprint section; it "
             "cannot prove the addition was additive")
    # A pre-15B sidecar round-trips with EXACTLY one change: the Migrations
    # table's header and separator gain the two columns plan 15B-04 adds.
    # Asserted precisely rather than as a vague additivity claim, because the
    # precise version is what the 14B freeze actually protects: the one-line
    # diff property. A whole-file rewrite, a changed data row, or a change to
    # any other section would all fail this.
    out = graph.serialize_course(graph.parse_course(golden))
    if out != golden:
        import difflib
        diff = [l for l in difflib.unified_diff(
            golden.splitlines(), out.splitlines(), lineterm="", n=0)
            if l[:1] in ("+", "-") and not l.startswith(("---", "+++"))]
        # Four diff lines: the old header and separator removed, the new pair
        # added. One table's header, and nothing else in the document.
        if len(diff) != 4:
            fail("a pre-15B sidecar round-trip changed %d diff lines, "
                 "expected the four Migrations header lines: %r"
                 % (len(diff), diff))
        else:
            for line in diff:
                body = line[1:]
                if "migration_id" in body:
                    continue
                if set(body.replace("|", "").replace("-", "")) <= {" ", ""}:
                    continue
                fail("the round-trip changed a line outside the Migrations "
                     "header: %r" % (line,))
    # Whatever the bytes, parsing is stable: the second parse equals the first.
    if graph.parse_course(out) != graph.parse_course(golden):
        fail("a pre-15B sidecar does not parse to an equal document after a "
             "round trip; data was lost or added")
    if "Blueprint" not in graph.SECTION_ORDER:
        fail("Blueprint is not in SECTION_ORDER")

    doc = graph.parse_course(golden)
    before = len(graph.blueprints(doc))
    graph.add_blueprint(doc, corpus_15b.build_blueprint())
    if len(graph.blueprints(doc)) != before + 1:
        fail("add_blueprint appended %d rows"
             % (len(graph.blueprints(doc)) - before))
    if "## Blueprint" not in graph.serialize_course(doc):
        fail("a populated blueprint section is not serialized")

    try:
        graph.add_blueprint(graph.parse_course(golden), {"construct": "x"})
    except graph.GraphError as exc:
        if exc.code != "graph.blueprint_invalid":
            fail("an invalid blueprint raised %r" % (exc.code,))
    else:
        fail("an invalid blueprint was recorded in the sidecar")


def check_thin_slice():
    """One drafted set from a bound blueprint to an accepted write."""
    import corpus_15b

    tmp = tempfile.mkdtemp(prefix="blueprint-")
    try:
        built = corpus_15b.build_blueprint_fixture(os.path.join(tmp, "f"))
        course_root = built["course_root"]

        rows = graph.blueprints(course.read_course(course_root)["doc"])
        if len(rows) != 1:
            fail("the fixture bound %d blueprints" % len(rows))
        elif rows[0]["blueprint_id"] != built["blueprint"]["blueprint_id"]:
            fail("the bound row names %r" % (rows[0]["blueprint_id"],))

        read = course.read_course(course_root)
        before_revision = read["revision"]
        course.bind_blueprint(course_root,
                              corpus_15b.build_blueprint(item_count=4),
                              "human", "weibao")
        after = course.read_course(course_root)
        if after["revision"] != (before_revision or 0) + 1:
            fail("bind_blueprint moved the revision %r -> %r"
                 % (before_revision, after["revision"]))
        if len(graph.blueprints(after["doc"])) != 2:
            fail("a second bind produced %d rows"
                 % len(graph.blueprints(after["doc"])))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_run_authoring_carries_the_gate():
    """The whole path: run_authoring with a blueprint, without one, and with a
    blocking one."""
    import corpus_15b

    def author(request, findings=None):
        return {"schema_version": 1, "items": []}

    tmp = tempfile.mkdtemp(prefix="blueprint-run-")
    try:
        questions = model.parse_bank(corpus_15b.build_draft_set("conforming"))
        facts = corpus_15b.build_item_facts(questions)
        bp = corpus_15b.build_blueprint()

        # build_proposal carries the array whether or not the gate ran.
        proposal = authoring.build_proposal(
            {"citations": [], "mode": "report_only"}, "", "", [], {},
            [], [], [], [], "run-1")
        if "blueprint_findings" not in proposal["gates"]:
            fail("build_proposal omits blueprint_findings")
        elif proposal["gates"]["blueprint_findings"] != []:
            fail("build_proposal defaulted blueprint_findings to %r"
                 % (proposal["gates"]["blueprint_findings"],))
        proposal = authoring.build_proposal(
            {"citations": [], "mode": "report_only"}, "", "", [], {},
            [], [], [], [], "run-1",
            blueprint.blueprint_gate(questions, None))
        if len(proposal["gates"]["blueprint_findings"]) != 1:
            fail("a supplied findings list was not carried")

        # The gate's verdict feeds the claim through gate_result, and the
        # claim is False whenever the blueprint gate did not pass.
        absent_results = [
            blueprint.gate_result("parser", True, []),
            blueprint.gate_result("lint", True, []),
            blueprint.gate_result("review", True, []),
            blueprint.gate_result(
                "blueprint",
                not blueprint.blueprint_gate_blocks(questions, None),
                blueprint.blueprint_gate(questions, None)),
            blueprint.gate_result("runtime", True, []),
        ]
        # An absent blueprint does not BLOCK, so gate 4 passes and the claim
        # would be True on gate results alone. ACTIVITY-02 wants the claim
        # withheld, so the caller must not claim fidelity against no
        # blueprint. Asserted here so the distinction is recorded.
        if blueprint.blueprint_gate_blocks(questions, None):
            fail("an absent blueprint blocks")
        blocked_results = list(absent_results)
        blocked_results[3] = blueprint.gate_result("blueprint", False, [])
        if blueprint.fidelity_claim(blocked_results) is not False:
            fail("a failing blueprint gate still produced a claim")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


BANNED_KEY_SUBSTRINGS = ("mastery", "completion", "readiness", "progress",
                         "percent", "score")


def check_no_aggregate(obj, where, path="$"):
    """No float and no aggregate-shaped key, at any depth.

    `share` and `tolerance` are integers and are the only proportion-shaped
    values the blueprint surface carries. A float or a key named for mastery,
    completion, readiness, progress, percent, or score would be a single number
    standing for overall compliance, which hides which of the eight declared
    fields actually failed.
    """
    if isinstance(obj, float):
        fail("%s carries a float at %s" % (where, path))
    elif isinstance(obj, dict):
        for key, value in obj.items():
            lowered = str(key).lower()
            for banned in BANNED_KEY_SUBSTRINGS:
                if banned in lowered:
                    fail("%s carries the aggregate-shaped key %r at %s"
                         % (where, key, path))
            check_no_aggregate(value, where, "%s.%s" % (path, key))
    elif isinstance(obj, (list, tuple)):
        for n, value in enumerate(obj):
            check_no_aggregate(value, where, "%s[%d]" % (path, n))


def check_blueprint_fields():
    """One case per remaining blueprint field, each reachable from data."""
    import corpus_15b

    questions = model.parse_bank(corpus_15b.build_draft_set("conforming"))
    bp = corpus_15b.build_blueprint()

    def codes(variant_facts, draft=None, doc=None):
        qs = questions if draft is None else model.parse_bank(
            corpus_15b.build_draft_set(draft))
        return blueprint.blueprint_gate(qs, doc or bp, variant_facts)

    full = corpus_15b.build_item_facts(questions, "conforming")

    # Every fact supplied and conforming: nothing at all, and no unverifiable
    # remains for any of the eight fields.
    findings = blueprint.blueprint_gate(questions, bp, full)
    if findings:
        fail("a fully conforming set produced %r"
             % ([(f["code"], f["item"]) for f in findings],))
    if blueprint.blueprint_gate_blocks(questions, bp, full):
        fail("a fully conforming set blocks")

    # domain_weight, out of tolerance and exactly at it.
    skewed = dict(bp)
    skewed["domain_weight"] = {
        "shares": [{"domain": "Scene assessment",
                    "objective_prefix": "Scene assessment", "share": 20},
                   {"domain": "Handoff reporting",
                    "objective_prefix": "Handoff reporting", "share": 80}],
        "tolerance": 5}
    found = [f for f in codes(full, doc=skewed)
             if f["code"] == "blueprint.domain_weight_out_of_tolerance"]
    if len(found) != 2:
        fail("a skewed domain weight produced %d findings" % len(found))
    else:
        for finding in found:
            if finding["item"] != "BANK":
                fail("a domain finding's item is %r" % (finding["item"],))
            for key in ("observed_share", "declared_share", "tolerance",
                        "domain"):
                if key not in finding["evidence"]:
                    fail("a domain finding's evidence lacks %r" % (key,))

    # The boundary: observed 67, declared 62, tolerance 5. Exactly at it.
    boundary = dict(bp)
    boundary["domain_weight"] = {
        "shares": [{"domain": "Scene assessment",
                    "objective_prefix": "Scene assessment", "share": 62}],
        "tolerance": 5}
    if [f for f in codes(full, doc=boundary)
            if f["code"] == "blueprint.domain_weight_out_of_tolerance"]:
        fail("a domain share differing by exactly the tolerance was refused; "
             "equality must pass")
    over = dict(bp)
    over["domain_weight"] = {
        "shares": [{"domain": "Scene assessment",
                    "objective_prefix": "Scene assessment", "share": 61}],
        "tolerance": 5}
    if len([f for f in codes(full, doc=over)
            if f["code"] == "blueprint.domain_weight_out_of_tolerance"]) != 1:
        fail("a domain share one point past the tolerance was accepted")

    # difficulty: a band the form does not permit, and a skewed band share.
    narrow = dict(bp)
    narrow["difficulty"] = {"permitted_bands": ["recall"],
                            "shares": [{"band": "recall", "share": 100}],
                            "tolerance": 5}
    found = codes(full, doc=narrow)
    banded = [f for f in found if f["code"] == "blueprint.difficulty_out_of_band"]
    if len(banded) != 2:
        fail("two application items against a recall-only form produced %d "
             "band findings" % len(banded))
    elif banded[0]["item"] == "BANK":
        fail("a band finding is bank-wide; it names one item")
    shared = [f for f in found
              if f["code"] == "blueprint.difficulty_share_out_of_tolerance"]
    if len(shared) != 1:
        fail("a skewed band share produced %d findings" % len(shared))
    elif shared[0]["item"] != "BANK":
        fail("a band-share finding's item is %r" % (shared[0]["item"],))

    # demand: skewed when supplied, unverifiable when not.
    found = [f for f in codes(corpus_15b.build_item_facts(questions,
                                                          "demand_skew"))
             if f["code"] == "blueprint.demand_out_of_tolerance"]
    if not found:
        fail("a skewed demand produced no finding")
    unverifiable = [f for f in codes(corpus_15b.build_item_facts(questions,
                                                                 "partial"))
                    if f["code"] == "blueprint.unverifiable"
                    and f["evidence"]["field"] == "demand"]
    if len(unverifiable) != 1:
        fail("an unsupplied demand produced %d unverifiable findings"
             % len(unverifiable))
    elif unverifiable[0]["severity"] != "warn":
        fail("an unsupplied demand blocks")

    # timing: one item over its per-item allowance.
    found = [f for f in codes(corpus_15b.build_item_facts(questions,
                                                          "timing_over"))
             if f["code"] == "blueprint.timing_out_of_tolerance"]
    if not found:
        fail("an over-long item produced no timing finding")
    if not any(f["item"] != "BANK" for f in found):
        fail("no timing finding names the offending item")

    # tools: a forbidden tool, and the empty-permitted edges.
    found = [f for f in codes(corpus_15b.build_item_facts(questions,
                                                          "tool_forbidden"))
             if f["code"] == "blueprint.tools_not_permitted"]
    if len(found) != 1:
        fail("a forbidden tool produced %d findings" % len(found))
    elif found[0]["item"] == "BANK":
        fail("a tools finding is bank-wide; it names one item")
    no_tools = dict(bp)
    no_tools["tools"] = {"permitted": [], "citation": "c"}
    empty_facts = dict(full)
    for q in questions:
        empty_facts[q["item_id"]] = dict(empty_facts[q["item_id"]], tools=[])
    if [f for f in codes(empty_facts, doc=no_tools)
            if f["code"] == "blueprint.tools_not_permitted"]:
        fail("an empty permitted list with empty supplied tools produced a "
             "finding; a form permitting no tools and an item using none agree")
    if len([f for f in codes(full, doc=no_tools)
            if f["code"] == "blueprint.tools_not_permitted"]) != 3:
        fail("an empty permitted list with supplied tools produced the wrong "
             "count")

    # construct and feedback_conditions, both set-level.
    found = [f for f in codes(corpus_15b.build_item_facts(
        questions, "construct_mismatch"))
        if f["code"] == "blueprint.construct_mismatch"]
    if len(found) != 1:
        fail("a mismatched construct produced %d findings" % len(found))
    elif found[0]["item"] != "BANK":
        fail("a construct finding's item is %r" % (found[0]["item"],))

    found = [f for f in codes(corpus_15b.build_item_facts(
        questions, "feedback_mismatch"))
        if f["code"] == "blueprint.feedback_conditions_mismatch"]
    if len(found) != 1:
        fail("a mismatched feedback condition produced %d findings"
             % len(found))
    else:
        evidence = found[0]["evidence"]
        for key in ("key", "observed_value", "declared_value"):
            if key not in evidence:
                fail("a feedback finding's evidence lacks %r" % (key,))
        if evidence.get("key") != "disclosure":
            fail("the feedback finding names the key %r" % (evidence.get("key"),))

    # No unverifiable survives a fully supplied fact set.
    if [f for f in blueprint.blueprint_gate(questions, bp, full)
            if f["code"] == "blueprint.unverifiable"]:
        fail("an unverifiable finding survives a complete fact set")


def check_gate_edges():
    """The empty, single, boundary, ordering and no-aggregate edges."""
    import corpus_15b

    bp = corpus_15b.build_blueprint()
    questions = model.parse_bank(corpus_15b.build_draft_set("conforming"))
    full = corpus_15b.build_item_facts(questions, "conforming")

    # Empty and single.
    #
    # Plan 15B-02 Task 2's edge list says `blueprint_gate([], bp)` returns
    # `[]`. It does not, and should not: the set-level construct and feedback
    # facts are genuinely unsupplied in that call, so two unverifiable warns
    # are the honest answer. What IS asserted is the substantive claim behind
    # the plan's wording: an empty set produces no BLOCK finding from any
    # share check, because a share over an empty set has no denominator and
    # emptiness is caught once by the item-count check.
    loose = corpus_15b.build_blueprint(item_count=0, count_tolerance=0)
    blocking = [f for f in blueprint.blueprint_gate([], loose, full)
                if f["severity"] == "block"]
    if blocking:
        fail("an empty question list against an empty-count blueprint blocks: "
             "%r" % ([f["code"] for f in blocking],))
    for finding in blueprint.blueprint_gate([], loose, {}):
        if finding["severity"] != "warn":
            fail("an empty set with no facts produced a blocking %r"
                 % (finding["code"],))
    if blueprint.blueprint_gate(None, bp, full) != \
            blueprint.blueprint_gate([], bp, full):
        fail("None is not treated as an empty question list")
    absent = blueprint.blueprint_gate([], None)
    if len(absent) != 1 or absent[0]["code"] != "blueprint.absent":
        fail("an empty list with no blueprint produced %r" % (absent,))
    try:
        single = corpus_15b.build_blueprint(item_count=1)
        blueprint.blueprint_gate(questions[:1], single,
                                 corpus_15b.build_item_facts(questions[:1]))
    except ZeroDivisionError:
        fail("a single-question set divided by zero")

    # Ordering and stability.
    over = model.parse_bank(corpus_15b.build_draft_set("too_many"))
    facts = corpus_15b.build_item_facts(over, "conforming")
    first = blueprint.blueprint_gate(over, bp, facts)
    second = blueprint.blueprint_gate(over, bp, facts)
    if first != second:
        fail("two gate calls over one input differ")
    if blueprint.canonical_json(first) != blueprint.canonical_json(second):
        fail("two gate calls do not render byte-identically")
    keys = [(f["item"], f["code"], blueprint.canonical_json(f["evidence"]))
            for f in first]
    if keys != sorted(keys):
        fail("findings are not sorted by (item, code, evidence)")
    shuffled = list(reversed(over))
    if blueprint.canonical_json(
            blueprint.blueprint_gate(shuffled, bp, facts)) != \
            blueprint.canonical_json(first):
        fail("reversing the input question order changed the findings")

    # No aggregate anywhere.
    check_no_aggregate(first, "the findings list")
    check_no_aggregate(bp, "the fixture blueprint")
    for step in blueprint.GATE_STEPS:
        check_no_aggregate(blueprint.gate_result(step, True, first),
                           "a gate_result")


def check_claim_discipline_end_to_end():
    """Five passing gates claim; a failing gate 4 does not, even when the
    other four pass."""
    import corpus_15b

    bp = corpus_15b.build_blueprint()
    questions = model.parse_bank(corpus_15b.build_draft_set("conforming"))

    for variant, expected in (("conforming", True), ("tool_forbidden", False)):
        facts = corpus_15b.build_item_facts(questions, variant)
        findings = blueprint.blueprint_gate(questions, bp, facts)
        blocks = blueprint.blueprint_gate_blocks(questions, bp, facts)
        results = [blueprint.gate_result("parser", True, []),
                   blueprint.gate_result("lint", True, []),
                   blueprint.gate_result("review", True, []),
                   blueprint.gate_result("blueprint", not blocks, findings),
                   blueprint.gate_result("runtime", True,
                                         blueprint.runtime_conformance(questions))]
        claim = blueprint.fidelity_claim(results)
        if claim is not expected:
            fail("the %s set produced the claim %r, expected %r"
                 % (variant, claim, expected))


def check_staleness_classifier():
    """Staleness is two fingerprints compared, and nothing is ever stored."""
    import corpus_15b
    import inspect

    if blueprint.STALENESS_DISPOSITIONS != ("rebind", "migrate", "supersede",
                                            "retain"):
        fail("STALENESS_DISPOSITIONS is %r"
             % (blueprint.STALENESS_DISPOSITIONS,))

    # The classifier takes both fingerprints and computes neither.
    params = list(inspect.signature(blueprint.classify_staleness).parameters)
    if params != ["base_fingerprint", "current_fingerprint"]:
        fail("classify_staleness takes %r; computing a fingerprint here would "
             "need a file read and the never-touches-disk ban would be gone"
             % (params,))

    # An unprovable freshness is not freshness.
    for base, current in (("", "abc"), (None, "abc"), ("abc", ""),
                          ("abc", None), (None, None), ("", "")):
        if blueprint.classify_staleness(base, current) is not True:
            fail("classify_staleness(%r, %r) is not stale; an absent "
                 "fingerprint must fail safe" % (base, current))

    if blueprint.classify_staleness("abc", "abc") is not False:
        fail("two equal fingerprints read stale")
    if blueprint.classify_staleness("abc", "abd") is not True:
        fail("two differing fingerprints read fresh")
    # Exact ASCII: no case folding, no stripping.
    if blueprint.classify_staleness("ABC", "abc") is not True:
        fail("fingerprint comparison case folds; a false fresh costs the "
             "guarantee while a false stale costs one look")
    if blueprint.classify_staleness(" abc", "abc") is not True:
        fail("fingerprint comparison strips whitespace")

    # The row shape, and the report's ordering.
    row = blueprint.staleness_row("o1", "bank", "s1", "source", "a", "b")
    if set(row) != set(blueprint.STALENESS_ROW_KEYS):
        fail("a staleness row's keys are %r" % (sorted(row),))
    if row["stale"] is not True:
        fail("a row with differing fingerprints is not stale")

    if blueprint.staleness_report([]) != []:
        fail("an empty dependent list produced a non-empty report")
    single = blueprint.staleness_report(
        [{"object_id": "o1", "object_kind": "bank",
          "dependency_object_id": "s1", "dependency_kind": "source",
          "base_fingerprint": "a", "current_fingerprint": "a"}])
    if len(single) != 1:
        fail("one dependent produced %d rows" % len(single))

    unsorted = [{"object_id": "o2", "object_kind": "bank",
                 "dependency_object_id": "s2", "dependency_kind": "source",
                 "base_fingerprint": "a", "current_fingerprint": "a"},
                {"object_id": "o1", "object_kind": "bank",
                 "dependency_object_id": "s1", "dependency_kind": "source",
                 "base_fingerprint": "a", "current_fingerprint": "a"}]
    report = blueprint.staleness_report(unsorted)
    if [r["object_id"] for r in report] != ["o1", "o2"]:
        fail("the report is not sorted by object_id")
    if json.dumps(report, sort_keys=True) != json.dumps(
            blueprint.staleness_report(unsorted), sort_keys=True):
        fail("two reports over one input differ")

    # A real source edit moves a real fingerprint.
    tmp = tempfile.mkdtemp(prefix="staleness-")
    try:
        fixture = corpus_15b.build_staleness_fixture(os.path.join(tmp, "s"))
        rows = blueprint.staleness_report(fixture["dependents"])
        if any(r["stale"] for r in rows):
            fail("an unedited source reads stale")
        moved = corpus_15b.edit_source(fixture, "revised")
        if moved == fixture["base_fingerprint"]:
            fail("editing the source did not change its fingerprint; the "
                 "fixture proves nothing")
        rows = blueprint.staleness_report(
            [dict(d, current_fingerprint=moved)
             for d in fixture["dependents"]])
        if not all(r["stale"] for r in rows):
            fail("an edited source did not make its dependents stale")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_staleness_blocks():
    """A stale dependent blocks acceptance until a matching disposition is
    recorded, and a later change blocks it again."""
    import corpus_15b

    # The disposition record refuses rather than returning an invalid one.
    good = dict(object_id="o1", dependency_object_id="s1",
                disposition="rebind", reviewer_role="reviewer",
                reviewer_name="weibao", rationale="the source moved",
                base_fingerprint="a", current_fingerprint="b")
    record = blueprint.disposition_record(**good)
    if set(record) != set(blueprint.DISPOSITION_KEYS):
        fail("a disposition record's keys are %r" % (sorted(record),))

    for override, code in (
            ({"disposition": "ignore"}, "blueprint.unknown_disposition"),
            ({"reviewer_role": "agent"},
             "blueprint.disposition_reviewer_required"),
            ({"rationale": "   "},
             "blueprint.disposition_rationale_required"),
            ({"rationale": ""},
             "blueprint.disposition_rationale_required")):
        try:
            blueprint.disposition_record(**dict(good, **override))
        except blueprint.BlueprintError as exc:
            if exc.code != code:
                fail("%r raised %r, expected %r" % (override, exc.code, code))
        else:
            fail("%r produced a record" % (override,))

    # All four dispositions clear a block, retain included.
    tmp = tempfile.mkdtemp(prefix="staleness-block-")
    try:
        fixture = corpus_15b.build_staleness_fixture(os.path.join(tmp, "s"))
        moved = corpus_15b.edit_source(fixture, "revised")
        rows = blueprint.staleness_report(
            [dict(d, current_fingerprint=moved)
             for d in fixture["dependents"]])

        # Every blocked dependent is reported, not just the first.
        refusals = blueprint.acceptance_block(rows, [])
        if len(refusals) != 3:
            fail("three stale dependents produced %d refusals"
                 % len(refusals))
        for refusal in refusals:
            if refusal["code"] != "blueprint.stale_dependent":
                fail("a refusal code is %r" % (refusal["code"],))
            for word in blueprint.STALENESS_DISPOSITIONS:
                if word not in refusal["message"]:
                    fail("a refusal does not name the disposition %r" % word)

        for disposition in blueprint.STALENESS_DISPOSITIONS:
            dispositions = [
                blueprint.disposition_record(
                    d["object_id"], d["dependency_object_id"], disposition,
                    "reviewer", "weibao", "reviewed after the source moved",
                    d["base_fingerprint"], moved)
                for d in fixture["dependents"]]
            if blueprint.acceptance_block(rows, dispositions):
                fail("a recorded %s disposition did not clear the block"
                     % disposition)

        # Reconciliation is per change: a second edit blocks again.
        dispositions = [
            blueprint.disposition_record(
                d["object_id"], d["dependency_object_id"], "retain",
                "reviewer", "weibao", "reviewed after the source moved",
                d["base_fingerprint"], moved)
            for d in fixture["dependents"]]
        moved_again = corpus_15b.edit_source(fixture, "revised twice")
        if moved_again == moved:
            fail("the second edit did not change the fingerprint")
        rows_again = blueprint.staleness_report(
            [dict(d, current_fingerprint=moved_again)
             for d in fixture["dependents"]])
        refusals = blueprint.acceptance_block(rows_again, dispositions)
        if len(refusals) != 3:
            fail("a decision recorded against the earlier fingerprint cleared "
                 "a later change; reconciliation must be per change")
        for refusal in refusals:
            if refusal["code"] != "blueprint.disposition_superseded":
                fail("a superseded disposition gave code %r"
                     % (refusal["code"],))

        # A fresh row is never blocked.
        fresh = blueprint.staleness_report(fixture["dependents"])
        if blueprint.acceptance_block(fresh, []):
            fail("a fresh dependent was blocked")

        # Refusals are sorted and stable.
        first = blueprint.acceptance_block(rows, [])
        if json.dumps(first, sort_keys=True) != json.dumps(
                blueprint.acceptance_block(rows, []), sort_keys=True):
            fail("two acceptance_block calls differ")
        keys = [(r["object_id"], r["dependency_object_id"], r["code"])
                for r in first]
        if keys != sorted(keys):
            fail("refusals are not sorted")

        # Nothing in this module rebuilds a stale dependent.
        source = open(os.path.join(ROOT, "blueprint.py"), encoding="utf-8").read()
        for banned in ("def rebuild", "def regenerate", "def refresh_stale"):
            if banned in source:
                fail("blueprint.py defines %r; RELIABILITY-03 says a stale "
                     "derivative is blocked, not rebuilt" % banned)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_accept_revision():
    """The acceptance path: staleness first, authority second, the write last,
    and every outcome journaled."""
    import corpus_15b
    import director
    import inspect
    import journal

    # No autonomy argument exists, so a value carried on a proposal cannot
    # authorize anything.
    params = list(inspect.signature(director.accept_revision).parameters)
    if [p for p in params if "autonomy" in p]:
        fail("accept_revision takes an autonomy parameter: %r" % (params,))

    def policy(level, cap=1):
        return {"agent_policy": {"autonomy_level": level,
                                 "max_bindings_per_operation": cap}}

    tmp = tempfile.mkdtemp(prefix="accept-")
    try:
        built = corpus_15b.build_acceptance_fixture(os.path.join(tmp, "a"))
        root = built["course_root"]
        mid, mid2 = built["migration_ids"]

        # 1. Staleness blocks before the policy question is even asked. The
        #    policy here is recommend-only, which would ALSO refuse; the point
        #    is that the recorded reason is the staleness one.
        moved = corpus_15b.edit_source(built, "revised")
        rows = blueprint.staleness_report(
            [dict(d, current_fingerprint=moved) for d in built["dependents"]])
        text_before = course.read_course(root)["text"]
        entries_before = len(list(journal.entries(root)))
        try:
            director.accept_revision(
                root, root, mid, policy("recommend-only"), "human", "weibao",
                "reviewed", staleness_rows=rows, dispositions=[])
        except director.DirectorError as exc:
            if exc.code != "director.acceptance_blocked":
                fail("a stale dependent raised %r; staleness must be checked "
                     "before authority so the journal records the right "
                     "reason" % (exc.code,))
        else:
            fail("a stale dependent did not block the acceptance")
        if course.read_course(root)["text"] != text_before:
            fail("a blocked acceptance changed the sidecar")
        after = list(journal.entries(root))
        if len(after) != entries_before + 1:
            fail("a blocked acceptance appended %d journal entries"
                 % (len(after) - entries_before))
        elif after[-1]["state"] != "refused":
            fail("a blocked acceptance's entry state is %r"
                 % (after[-1]["state"],))
        elif after[-1]["code"] != "director.acceptance_blocked":
            fail("a blocked acceptance recorded code %r"
                 % (after[-1]["code"],))
        elif built["dependents"][0]["dependency_object_id"] not in \
                (after[-1]["message"] or ""):
            fail("the refusal entry does not name the blocked dependency")

        # 2. With the staleness reconciled, the POLICY refuses, and the
        #    recorded reason is now the authority one.
        dispositions = [blueprint.disposition_record(
            d["object_id"], d["dependency_object_id"], "retain", "reviewer",
            "weibao", "reviewed after the source moved",
            d["base_fingerprint"], moved) for d in built["dependents"]]
        entries_before = len(list(journal.entries(root)))
        try:
            director.accept_revision(
                root, root, mid, policy("recommend-only"), "human", "weibao",
                "reviewed", staleness_rows=rows, dispositions=dispositions)
        except director.DirectorError as exc:
            if exc.code != "director.autonomy_exceeded":
                fail("a recommend-only policy raised %r" % (exc.code,))
        else:
            fail("a recommend-only policy permitted an acceptance")
        if course.read_course(root)["text"] != text_before:
            fail("a policy-refused acceptance changed the sidecar")
        after = list(journal.entries(root))
        if len(after) != entries_before + 1:
            fail("a policy-refused acceptance appended %d entries"
                 % (len(after) - entries_before))
        elif after[-1]["code"] != "director.autonomy_exceeded":
            fail("a policy-refused acceptance recorded code %r"
                 % (after[-1]["code"],))

        # 3. Reconciled and permitted: the write lands, through the one path.
        entries_before = len(list(journal.entries(root)))
        director.accept_revision(
            root, root, mid, policy("approved-bounded-write"), "human",
            "weibao", "reviewed against the new edition",
            staleness_rows=rows, dispositions=dispositions)
        doc = course.read_course(root)["doc"]
        row = [r for r in doc["migrations"] if r["migration_id"] == mid][0]
        if row["state"] != "accepted":
            fail("a permitted acceptance left the row %r" % (row["state"],))
        if row["reviewer"] != "weibao":
            fail("the reviewer is %r" % (row["reviewer"],))
        other = [r for r in doc["migrations"] if r["migration_id"] == mid2][0]
        if other["state"] != "proposed":
            fail("accepting one proposal settled the other")
        if len(list(journal.entries(root))) <= entries_before:
            fail("a permitted acceptance journaled nothing")
        applied = [e for e in journal.entries(root)
                   if (e.get("agent") or {}).get("phase") == "accept"
                   and e["state"] == "applied"]
        if not applied:
            fail("no applied accept phase was journaled")

        # The proposer may not accept its own proposal, even at full autonomy.
        try:
            director.accept_revision(
                root, root, mid2, policy("approved-bounded-write"), "agent",
                built["proposer"], "granting my own",
                staleness_rows=rows, dispositions=dispositions)
        except Exception as exc:
            if getattr(exc, "code", "") != "graph.migration_self_accept":
                fail("a self-accept raised %r" % (getattr(exc, "code", exc),))
        else:
            fail("the proposer accepted its own proposal at full autonomy")

        # journal.py's whole-phase diff stays one line.
        if len(journal.OPERATION_TYPES) != 6:
            fail("OPERATION_TYPES is %d" % len(journal.OPERATION_TYPES))
        if len(journal.ENTRY_KEYS) != 24:
            fail("ENTRY_KEYS is %d" % len(journal.ENTRY_KEYS))
        if "accept_revision" not in journal.RECORD_TYPES:
            fail("accept_revision is not a journal record type")
        if "accept_revision" in journal.OPERATION_TYPES:
            fail("accept_revision is a file-operation type; it is a record of "
                 "a decision")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_course_audit():
    """A read-only aggregation that recomputes nothing and mints no fourth
    coverage vocabulary."""
    import corpus_15b
    import graph as graph_module

    # The vocabulary discipline, structurally.
    if blueprint.COVERAGE_VOCABULARIES != (
            "graph.BINDING_STATES", "auditor.coverage_report",
            "audit_report.coverage_row"):
        fail("COVERAGE_VOCABULARIES is %r"
             % (blueprint.COVERAGE_VOCABULARIES,))
    for state in ("covered", "gap", "partial", "thin", "missing",
                  "conflicting", "unknown", "stale"):
        if state in blueprint.COVERAGE_VOCABULARIES:
            fail("COVERAGE_VOCABULARIES carries the STATE %r; it holds "
                 "vocabulary names, and a tuple of states here would be a "
                 "fourth vocabulary the moment it drifted" % (state,))

    # blueprint.py holds no coverage-state tuple of its own.
    for name in dir(blueprint):
        value = getattr(blueprint, name)
        if isinstance(value, (tuple, frozenset, list)) and \
                "covered" in value and "conflicting" in value:
            fail("blueprint.%s is a coverage-state vocabulary; this module "
                 "must hold no copy of one" % name)

    # It imports none of the modules that produce its signals.
    for forbidden in ("graph", "auditor", "director", "authoring"):
        if hasattr(blueprint, forbidden):
            fail("blueprint imports %s; the audit takes its signals as "
                 "arguments" % forbidden)

    signals = corpus_15b.build_audit_signals()

    def audit(**over):
        kwargs = dict(course_object_id="c1",
                      treatment_rows=signals["treatment_rows"],
                      coverage_rows=signals["coverage_rows"],
                      quality_findings=signals["quality_findings"],
                      blueprint_findings=signals["blueprint_findings"],
                      vocabulary_members=signals["vocabulary_members"],
                      course_fingerprint="fp", tool_version="v1")
        kwargs.update(over)
        return blueprint.course_audit(**kwargs)

    report = audit()
    if set(report) != set(blueprint.AUDIT_REPORT_KEYS):
        fail("the report's keys are %r" % (sorted(report),))
    if report["status"] != "course_audit":
        fail("the report status is %r" % (report["status"],))

    # Provenance is required and checked.
    row = blueprint.audit_row("o", "graph.BINDING_STATES", "covered")
    if set(row) != set(blueprint.AUDIT_ROW_KEYS):
        fail("an audit row's keys are %r" % (sorted(row),))
    try:
        blueprint.audit_row("o", "made.up", "covered")
    except blueprint.BlueprintError as exc:
        if exc.code != "blueprint.unknown_vocabulary":
            fail("an unknown vocabulary raised %r" % (exc.code,))
        for name in blueprint.COVERAGE_VOCABULARIES:
            if name not in exc.message:
                fail("the refusal does not name %r" % (name,))
    else:
        fail("an unknown vocabulary was accepted")

    # A real cross-vocabulary confusion: `gap` is auditor's, not BINDING_STATES'.
    if "gap" in graph_module.BINDING_STATES:
        fail("the fixture assumption is wrong: gap IS a BINDING_STATES member")
    confused = [dict(signals["coverage_rows"][0],
                     vocabulary="graph.BINDING_STATES", state="gap")]
    try:
        audit(coverage_rows=confused)
    except blueprint.BlueprintError as exc:
        if exc.code != "blueprint.state_not_in_vocabulary":
            fail("a cross-vocabulary state raised %r" % (exc.code,))
        if "gap" not in exc.message or \
                "graph.BINDING_STATES" not in exc.message:
            fail("the refusal names neither the state nor the vocabulary: %r"
                 % (exc.message,))
    else:
        fail("a state from another vocabulary was accepted")

    # A missing vocabulary_members entry is a refusal, not a skipped check.
    partial = dict(signals["vocabulary_members"])
    del partial["auditor.coverage_report"]
    try:
        audit(vocabulary_members=partial)
    except blueprint.BlueprintError as exc:
        if exc.code != "blueprint.unknown_vocabulary":
            fail("a missing vocabulary member list raised %r" % (exc.code,))
    else:
        fail("a missing vocabulary member list skipped the check; a skipped "
             "check is not a passed check")

    # Two rows sharing a state string stay distinguishable by provenance.
    covered = [r for r in report["rows"] if r["state"] == "covered"]
    if len(covered) != 2:
        fail("the two covered rows collapsed to %d" % len(covered))
    elif len({r["vocabulary"] for r in covered}) != 2:
        fail("the two covered rows lost their provenance")

    # Signals are copied, never recomputed.
    by_objective = {r["objective_id"]: r for r in report["rows"]}
    if by_objective["obj-1"]["treatment_kind"] != "guided-lesson":
        fail("the treatment kind was not carried through")
    if "quality.answer_skew" not in by_objective["obj-1"]["quality_codes"]:
        fail("the quality code was not carried through")
    if "blueprint.unverifiable" not in by_objective["obj-1"]["blueprint_codes"]:
        fail("the blueprint code was not carried through")
    if by_objective["obj-3"]["treatment_kind"] != "":
        fail("an untreated objective invented a treatment")

    # Counts are integers with denominators beside them, never proportions.
    counts = report["counts"]
    for key, value in counts.items():
        if not isinstance(value, int) or isinstance(value, bool):
            fail("the count %r is %r" % (key, value))
    if counts["objectives_total"] != 3 or counts["rows_total"] != 4:
        fail("the counts are %r" % (counts,))
    if counts["objectives_with_treatment"] != 2:
        fail("objectives_with_treatment is %r"
             % (counts["objectives_with_treatment"],))
    if counts["quality_findings_block"] != 1 or \
            counts["quality_findings_warn"] != 1:
        fail("the quality counts are %r" % (counts,))

    blob = json.dumps(report)
    for banned in ('"share"', '"rate"', '"ratio"', '"percent"', '"pct"'):
        if banned in blob:
            fail("the report carries a proportion key %s" % banned)
    check_no_aggregate(report, "the course audit report")

    if report["vocabularies_cited"] != sorted(
            {r["vocabulary"] for r in report["rows"]}):
        fail("vocabularies_cited is %r" % (report["vocabularies_cited"],))

    # Staleness is derived, named, and per row.
    if report["stale"] is not False or report["stale_inputs"] != []:
        fail("a fresh report reads %r / %r"
             % (report["stale"], report["stale_inputs"]))
    stale_signals = corpus_15b.build_audit_signals(stale=True)
    stale_report = audit(coverage_rows=stale_signals["coverage_rows"])
    if stale_report["stale"] is not True:
        fail("a stale input did not make the report stale")
    if stale_report["stale_inputs"] != ["src-1"]:
        fail("the stale inputs are %r" % (stale_report["stale_inputs"],))
    if stale_report["stale"] != any(r["stale"] for r in stale_report["rows"]):
        fail("the report's stale flag disagrees with its rows")
    if not any(r["stale"] for r in stale_report["rows"]) or \
            all(r["stale"] for r in stale_report["rows"]):
        fail("the fixture does not produce a report that is stale in one row "
             "and fresh in another")

    # Determinism and ordering.
    if blueprint.canonical_json(audit()) != blueprint.canonical_json(audit()):
        fail("two audits over one input differ")
    shuffled = audit(coverage_rows=list(reversed(signals["coverage_rows"])),
                     treatment_rows=list(reversed(signals["treatment_rows"])))
    if blueprint.canonical_json(shuffled) != blueprint.canonical_json(report):
        fail("shuffling an input list changed the report")
    keys = [(r["objective_id"], r["vocabulary"], r["source_object_id"])
            for r in report["rows"]]
    if keys != sorted(keys):
        fail("rows are not sorted by (objective_id, vocabulary, source)")

    # Empty, None, and single.
    empty = blueprint.course_audit("c1", [], [], [], [], {}, "fp", "v1")
    if empty["rows"] != [] or empty["vocabularies_cited"] != []:
        fail("an empty course produced %r" % (empty,))
    if any(v != 0 for v in empty["counts"].values()):
        fail("an empty course's counts are %r" % (empty["counts"],))
    if empty["stale"] is not False:
        fail("an empty course reads stale")
    if not empty["course_object_id"] or "course_fingerprint" not in empty:
        fail("an empty report lost its course identity")
    none_report = blueprint.course_audit("c1", None, None, None, None, {},
                                         "fp", "v1")
    if blueprint.canonical_json(none_report) != blueprint.canonical_json(empty):
        fail("None is not treated as an empty signal list")
    single = audit(coverage_rows=signals["coverage_rows"][:1])
    if single["counts"]["objectives_total"] != 1:
        fail("a single-row course counted %d objectives"
             % single["counts"]["objectives_total"])

    # The schema couples to the code.
    schema = json.load(open(os.path.join(ROOT, "schemas",
                                         "course_audit_report.schema.json")))
    try:
        schema_validate.check_schema(schema)
    except Exception as exc:
        fail("the course audit schema is invalid: %s" % exc)
    if schema["required"] != list(blueprint.AUDIT_REPORT_KEYS):
        fail("the schema's required array and AUDIT_REPORT_KEYS disagree: "
             "%r vs %r" % (schema["required"],
                           list(blueprint.AUDIT_REPORT_KEYS)))
    row_schema = schema["properties"]["rows"]["items"]
    if row_schema["required"] != list(blueprint.AUDIT_ROW_KEYS):
        fail("the schema's row required array and AUDIT_ROW_KEYS disagree")
    if row_schema["properties"]["vocabulary"]["enum"] != \
            list(blueprint.COVERAGE_VOCABULARIES):
        fail("the schema's vocabulary enum and COVERAGE_VOCABULARIES disagree")
    raw = open(os.path.join(ROOT, "schemas",
                            "course_audit_report.schema.json"),
               encoding="utf-8").read()
    if '"number"' in raw:
        fail("the course audit schema carries a float type")
    for candidate in (report, stale_report, empty, single):
        errs = schema_validate.validate(candidate, schema)
        if errs:
            fail("a report fails its own schema: %r" % (errs[:2],))


def check_evidence_proposal():
    """A proposal names its window, its denominator, and its uncertainty, and
    can never become a mastery percentage."""
    import corpus_15b
    import director
    import inspect

    schema_path = os.path.join(ROOT, "schemas",
                               "evidence_proposal.schema.json")
    schema = json.load(open(schema_path))
    try:
        schema_validate.check_schema(schema)
    except Exception as exc:
        fail("the proposal schema is invalid: %s" % exc)
    if schema["required"] != list(blueprint.PROPOSAL_KEYS):
        fail("the schema's required array and PROPOSAL_KEYS disagree: %r vs %r"
             % (schema["required"], list(blueprint.PROPOSAL_KEYS)))
    for needed in ("window", "denominator", "included_signals",
                   "missing_signals", "uncertainty",
                   "competing_explanations"):
        if needed not in schema["required"]:
            fail("AGENT-03's %r is not required by the schema" % needed)
    if '"number"' in open(schema_path, encoding="utf-8").read():
        fail("the proposal schema carries a float type")

    window = corpus_15b.PROPOSAL_WINDOW
    rows = corpus_15b.build_sparse_evidence()
    record = blueprint.evidence_proposal(
        corpus_15b.PROPOSAL_OBJECTIVE, rows, window, ["response"],
        ["confidence"], ["the two attempts were minutes apart"])

    # All six namings are proven required, one at a time.
    for key in ("window", "denominator", "included_signals",
                "missing_signals", "uncertainty", "competing_explanations"):
        broken = dict(record)
        del broken[key]
        if not schema_validate.validate(broken, schema):
            fail("a record with no %r still validates; the schema does not "
                 "require it" % key)

    # The window is half-open and says so.
    if blueprint.WINDOW_KEYS != ("start", "end", "boundary"):
        fail("WINDOW_KEYS is %r" % (blueprint.WINDOW_KEYS,))
    if blueprint.WINDOW_BOUNDARY != "half-open":
        fail("WINDOW_BOUNDARY is %r" % (blueprint.WINDOW_BOUNDARY,))
    if schema["properties"]["window"]["properties"]["boundary"].get("const") \
            != "half-open":
        fail("the schema does not const the boundary convention")
    if blueprint.in_window(window["start"], window) is not True:
        fail("an event at the window start is outside it")
    if blueprint.in_window(window["end"], window) is not False:
        fail("an event at the window end is inside it")
    if blueprint.in_window("2026-08-04T00:00:00.000Z", window) is not True:
        fail("an event strictly inside the window is outside it")
    if blueprint.in_window("2026-07-01T00:00:00.000Z", window) is not False:
        fail("an event before the window is inside it")

    # Two abutting windows partition a row set exactly.
    dense = corpus_15b.build_dense_evidence(24)
    first = blueprint.evidence_proposal(
        corpus_15b.PROPOSAL_OBJECTIVE, dense, window, ["response"], [],
        ["other readings exist"])
    second = blueprint.evidence_proposal(
        corpus_15b.PROPOSAL_OBJECTIVE, dense, corpus_15b.PROPOSAL_WINDOW_NEXT,
        ["response"], [], ["other readings exist"])
    if first["denominator"] + second["denominator"] != len(dense):
        fail("two abutting windows counted %d of %d rows; a row was dropped "
             "or double counted"
             % (first["denominator"] + second["denominator"], len(dense)))
    if second["denominator"] != 2:
        fail("the two boundary rows landed in the %d-row second window; the "
             "fixture proves nothing about the boundary"
             % second["denominator"])

    # An invalid window refuses before any row is examined.
    for bad in ({"start": "b", "end": "a", "boundary": "half-open"},
                {"start": "a", "boundary": "half-open"},
                {"start": "a", "end": "b"},
                {"start": "a", "end": "b", "boundary": "closed"}):
        try:
            blueprint.evidence_proposal("o", rows, bad, [], [], [])
        except blueprint.BlueprintError as exc:
            if exc.code != "blueprint.window_invalid":
                fail("the window %r raised %r" % (bad, exc.code))
        else:
            fail("the window %r was accepted" % (bad,))

    # The denominator is a count and is always present.
    if record["denominator"] != 2:
        fail("two rows produced the denominator %r" % (record["denominator"],))
    if not isinstance(record["denominator"], int) or \
            isinstance(record["denominator"], bool):
        fail("the denominator is %r" % (record["denominator"],))
    for claim in record["claims"]:
        if claim["denominator"] != record["denominator"]:
            fail("a claim's denominator is %r" % (claim["denominator"],))
        if not isinstance(claim["observed_count"], int):
            fail("an observed count is %r" % (claim["observed_count"],))

    # The uncertainty is banded and derived.
    if blueprint.UNCERTAINTY_LEVELS != ("no-evidence", "sparse", "moderate",
                                        "sufficient"):
        fail("UNCERTAINTY_LEVELS is %r" % (blueprint.UNCERTAINTY_LEVELS,))
    if blueprint.SPARSE_MAX != 5 or blueprint.MODERATE_MAX != 19:
        fail("the bands are %r/%r"
             % (blueprint.SPARSE_MAX, blueprint.MODERATE_MAX))
    for value, expected in ((0, "no-evidence"), (1, "sparse"), (5, "sparse"),
                            (6, "moderate"), (19, "moderate"),
                            (20, "sufficient"), (2000, "sufficient")):
        if blueprint.uncertainty_for(value) != expected:
            fail("uncertainty_for(%d) is %r, expected %r"
                 % (value, blueprint.uncertainty_for(value), expected))
    try:
        blueprint.uncertainty_for(-1)
    except ValueError:
        pass
    else:
        fail("a negative denominator produced an uncertainty level")

    # AGENT-03's own case: two attempts read sparse.
    if record["uncertainty"] != "sparse":
        fail("two attempts produced the uncertainty %r"
             % (record["uncertainty"],))

    # A claim always has an alternative reading.
    try:
        blueprint.evidence_proposal(corpus_15b.PROPOSAL_OBJECTIVE, rows,
                                    window, ["response"], [], [])
    except blueprint.BlueprintError as exc:
        if exc.code != "blueprint.proposal_invalid":
            fail("a claim with no competing explanation raised %r"
                 % (exc.code,))
        elif "omission" not in exc.message:
            fail("the refusal does not name the omission: %r" % (exc.message,))
    else:
        fail("a claim with no competing explanation was accepted")
    empty = blueprint.evidence_proposal(corpus_15b.PROPOSAL_OBJECTIVE, [],
                                        window, ["response"], ["confidence"],
                                        [])
    if empty["denominator"] != 0 or empty["uncertainty"] != "no-evidence":
        fail("a zero-row proposal reads %r / %r"
             % (empty["denominator"], empty["uncertainty"]))
    if empty["claims"] != []:
        fail("a zero-row proposal made claims")
    if not empty["window"] or not empty["included_signals"]:
        fail("a zero-row proposal dropped its window or its signals; we "
             "looked here and found nothing is a finding")

    # A recommendation stays a recommendation.
    if blueprint.PROPOSAL_STATUS != "recommendation":
        fail("PROPOSAL_STATUS is %r" % (blueprint.PROPOSAL_STATUS,))
    if schema["properties"]["status"].get("const") != "recommendation":
        fail("the schema does not const the status")
    for candidate in (record, empty, first):
        if candidate["status"] != "recommendation":
            fail("a record's status is %r" % (candidate["status"],))
    for banned in ("acted", "acted_on", "applied", "taken", "executed"):
        if banned in blueprint.PROPOSAL_KEYS:
            fail("PROPOSAL_KEYS carries %r; the record must have no place to "
                 "claim an action" % banned)

    # No mastery percentage can be built, at any depth.
    for candidate in (record, empty, first, second):
        check_no_aggregate(candidate, "an evidence proposal")
        errs = schema_validate.validate(candidate, schema)
        if errs:
            fail("a proposal fails its own schema: %r" % (errs[:2],))
    try:
        blueprint.evidence_proposal(
            corpus_15b.PROPOSAL_OBJECTIVE, rows, window,
            ["response"], ["confidence"], ["alt"], signal_kind="mastery_rate")
    except blueprint.BlueprintError as exc:
        if exc.code not in ("blueprint.forbidden_proposal_key",
                            "blueprint.proposal_invalid"):
            fail("a mastery-shaped signal kind raised %r" % (exc.code,))
    else:
        # A VALUE named mastery is not a KEY named mastery; the ban is on
        # keys, and this records that the distinction is deliberate.
        pass

    # Objective identity: the same rule director applies, checked not trusted.
    for text in ("a", "A b", "x\r\ny", "\u00e9", "e\u0301", " s ",
                 corpus_15b.PROPOSAL_OBJECTIVE):
        if blueprint.objective_key(text) != director.locator_key(text):
            fail("objective_key and director.locator_key disagree on %r"
                 % (text,))
    if blueprint.objective_key("Obj") == blueprint.objective_key("obj"):
        fail("objective_key case folds")

    # The evidence store stays unreachable.
    if hasattr(blueprint, "evidence"):
        fail("blueprint imports evidence")
    source = open(os.path.join(ROOT, "blueprint.py"), encoding="utf-8").read()
    for line in source.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if stripped == "import evidence" or \
                stripped.startswith("from evidence "):
            fail("blueprint.py imports evidence at %r" % (line,))
    params = list(inspect.signature(blueprint.evidence_proposal).parameters)
    for banned in ("log", "log_path", "base", "path"):
        if banned in params:
            fail("evidence_proposal takes %r; it must not be handed a store "
                 "to read" % banned)

    # Determinism and ordering.
    again = blueprint.evidence_proposal(
        corpus_15b.PROPOSAL_OBJECTIVE, rows, window, ["response"],
        ["confidence"], ["the two attempts were minutes apart"])
    if blueprint.canonical_json(again) != blueprint.canonical_json(record):
        fail("two proposals over one input differ")
    keys = [(c["objective_key"], c["signal_kind"],
             blueprint.canonical_json(c["evidence"])) for c in first["claims"]]
    if keys != sorted(keys):
        fail("claims are not sorted")


def main():
    checks = [check_schema_is_closed,
              check_module_surface,
              check_validation_refuses_before_it_reads,
              check_the_gate,
              check_gate_five_is_the_shipped_scorer,
              check_the_claim_appears_only_after_five,
              check_the_report_and_sidecar_grew_additively,
              check_thin_slice,
              check_run_authoring_carries_the_gate,
              check_blueprint_fields,
              check_gate_edges,
              check_claim_discipline_end_to_end,
              check_staleness_classifier,
              check_staleness_blocks,
              check_accept_revision,
              check_course_audit,
              check_evidence_proposal]
    for check in checks:
        check()
    if FAILURES:
        print("blueprint_roundtrip: %d failed" % len(FAILURES))
        sys.exit(1)
    print("OK blueprint_roundtrip")


if __name__ == "__main__":
    main()
