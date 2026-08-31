#!/usr/bin/env python3
"""The Phase 15B freeze gate: one blueprint, one drafted lesson treatment, and
one drafted practice set walked from draft to a journaled acceptance.

This builds no capability. It proves the six plans before it, and either the
whole gate is green or the freeze is withheld by name.

Each `scenario_*` function implements exactly one clause of the ROADMAP's
Phase 15B freeze gate and names it in its docstring, so a reader can tell what
a green line means without reading the assertions.

The corpus is fictional. Its only relationship to a real assessment is its
shape: no real course, exam, syllabus, learner note, or bank appears, and
nothing here is a paraphrase of any.

Standard library only, runnable as `python tests/acceptance_tracer.py`.
"""
import json, os, platform, shutil, subprocess, sys, tempfile, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "fixtures"))

FAILURES = []
SKIPS = []
MEASURED = {}

FORBIDDEN = ("mastery", "completion", "readiness", "progress", "percent",
             "score")


def fail(msg):
    print("FAIL: " + msg)
    FAILURES.append(msg)


def skip(what, why):
    print("SKIP: %s (%s)" % (what, why))
    SKIPS.append((what, why))


def walk_forbidden(obj, where, path="$"):
    """Every float and every aggregate-shaped key, at any depth."""
    found = []
    if isinstance(obj, float):
        found.append("%s (a float)" % path)
    elif isinstance(obj, dict):
        for key, value in obj.items():
            if any(b in str(key).lower() for b in FORBIDDEN):
                found.append("%s.%s" % (path, key))
            found.extend(walk_forbidden(value, where, "%s.%s" % (path, key)))
    elif isinstance(obj, (list, tuple)):
        for n, value in enumerate(obj):
            found.extend(walk_forbidden(value, where, "%s[%d]" % (path, n)))
    return found


def shipped_suite_check():
    """The shipped runtime is green and all three upstream freezes are real.

    Run before any 15B module is imported. A green 15B tracer over a broken
    runtime would report a pass for something nobody should trust, and a
    freeze that was WITHHELD is not a freeze 15B may plan against.
    """
    ok = True
    for name in ("scoring_roundtrip.py", "evidence_roundtrip.py",
                 "audit_authoring_roundtrip.py", "audit_quality_roundtrip.py",
                 "audit_coverage_roundtrip.py", "audit_roundtrip.py"):
        completed = subprocess.run(
            [sys.executable, os.path.join(ROOT, "tests", name)],
            capture_output=True, text=True, timeout=900)
        if completed.returncode != 0:
            skip("every scenario", "the shipped suite %s is red: %s"
                 % (name, completed.stderr.strip()[-200:]))
            ok = False
    for phase, short in (("14A-identity-lifecycle-operation", "14A"),
                         ("14B-graph-course-package-prototype", "14B"),
                         ("15A-director-treatment-policy", "15A")):
        path = os.path.join(ROOT, ".planning", "phases", phase,
                            "%s-FREEZE.md" % short)
        if not os.path.exists(path):
            skip("every scenario", "%s does not exist" % path)
            ok = False
            continue
        text = open(path, encoding="utf-8").read()
        if "## Frozen at %s" % short not in text:
            skip("every scenario", "%s carries no frozen heading" % path)
            ok = False
        if "## Freeze withheld" in text:
            skip("every scenario",
                 "%s WITHHELD its freeze; a withheld freeze is not a surface "
                 "15B may plan against" % path)
            ok = False
    return ok


def _settings(level="approved-bounded-write", cap=50):
    script = os.path.join(ROOT, "fixtures", "mock_backends.py")
    return {"model_backend": {"active": "hosted", "profiles": [
                {"name": "hosted", "transport": "hosted_cli",
                 "command": [sys.executable, script, "--cli"],
                 "model": "mock", "timeout_seconds": 30,
                 "max_output_bytes": 65536, "context_window": 4096}]},
            "agent_policy": {"autonomy_level": level,
                             "max_bindings_per_operation": cap}}


def scenario_five_gate_acceptance(built):
    """ROADMAP 15B: one drafted lesson treatment and one drafted practice set
    walked from draft through all five ACTIVITY-02 gates to an accepted write.
    """
    import audit_writer, authoring, blueprint, course, graph, model

    root = built["course_root"]
    rows = graph.blueprints(course.read_course(root)["doc"])
    if len(rows) != 1:
        fail("the fixture bound %d blueprints" % len(rows))

    # The drafted lesson treatment, bound from the closed vocabulary.
    before = len(course.read_course(root)["doc"]["bindings"])
    course.bind_treatment(root, built["treatment_objective"],
                          built["source_object_id"], "guided-lesson",
                          locator="section 1", state="unknown",
                          confidence="high", actor_kind="human",
                          actor_name="weibao")
    doc = course.read_course(root)["doc"]
    if len(doc["bindings"]) != before + 1:
        fail("the treatment bind added %d rows"
             % (len(doc["bindings"]) - before))
    treated = [r for r in doc["bindings"]
               if r.get("binding_kind") == "treatment"]
    for row in treated:
        if row["treatment_kind"] not in graph.TREATMENT_KINDS:
            fail("a bound treatment names %r, outside the closed eleven"
                 % (row["treatment_kind"],))

    # The five gates over the drafted practice set.
    questions = built["questions"]
    facts = built["item_facts"]
    bp = built["blueprint"]
    lint_errors, lint_warnings = model.lint(questions)
    quality = authoring.quality_gate(questions)
    findings = blueprint.blueprint_gate(questions, bp, facts)
    conformance = blueprint.runtime_conformance(questions)

    results = [
        blueprint.gate_result("parser", bool(questions), []),
        blueprint.gate_result("lint", not lint_errors, []),
        blueprint.gate_result(
            "review", not any(f["severity"] == "block" for f in quality),
            quality),
        blueprint.gate_result(
            "blueprint", not blueprint.blueprint_gate_blocks(questions, bp,
                                                             facts),
            findings),
        blueprint.gate_result("runtime", not conformance, conformance),
    ]
    if [r["step"] for r in results] != list(blueprint.GATE_STEPS):
        fail("the recorded gates are %r" % ([r["step"] for r in results],))
    for result in results:
        if not result["passed"]:
            fail("the %s gate did not pass on the conforming set: %r"
                 % (result["step"], result["findings"][:1]))
    MEASURED["gates_passed"] = sum(1 for r in results if r["passed"])

    # The write, through the shipped Phase 11 seam.
    request = {"schema_version": 1, "mode": "report_only", "citations": [],
               "retry_cap": 1}
    proposal = authoring.build_proposal(
        request, "", built["bank_text"], [], {}, lint_errors, lint_warnings,
        quality, [], "tracer-run", findings)
    for key in ("lint_errors", "lint_warnings", "quality_findings",
                "blueprint_findings"):
        if key not in proposal["gates"]:
            fail("the proposal's gates lack %r" % (key,))
    MEASURED["gate_arrays"] = len(proposal["gates"])
    return "pass"


def scenario_fidelity_claim_ordering(built):
    """ROADMAP 15B: the exam-fidelity claim appears only after all five gates,
    and never against an absent blueprint."""
    import authoring, blueprint, model

    questions = built["questions"]
    facts = built["item_facts"]
    bp = built["blueprint"]

    # False at each of the first four points, True only at the fifth.
    steps = list(blueprint.GATE_STEPS)
    accumulated = []
    for step in steps:
        accumulated.append(blueprint.gate_result(step, True, []))
        claim = blueprint.fidelity_claim(accumulated)
        if step != steps[-1] and claim is not False:
            fail("the claim was True after only the %s gate" % step)
        if step == steps[-1] and claim is not True:
            fail("the claim was not True after all five gates")

    # An absent blueprint: the write is unaffected, the claim is withheld.
    absent = blueprint.blueprint_gate(questions, None)
    if len(absent) != 1 or absent[0]["code"] != "blueprint.absent":
        fail("an absent blueprint produced %r" % (absent,))
    if absent[0]["severity"] != "warn":
        fail("an absent blueprint blocks the write")
    withheld = [blueprint.gate_result(s, True, []) for s in steps[:4]]
    if blueprint.fidelity_claim(withheld) is not False:
        fail("a claim survived an unrun runtime gate")

    # Gate 4 alone failing withholds the claim while 1, 2, 3 and 5 pass.
    forbidden_facts = None
    import corpus_15b
    forbidden_facts = corpus_15b.build_item_facts(questions, "tool_forbidden")
    blocked = blueprint.blueprint_gate(questions, bp, forbidden_facts)
    if not blueprint.blueprint_gate_blocks(questions, bp, forbidden_facts):
        fail("the tool_forbidden set did not block gate 4")
    results = [blueprint.gate_result("parser", True, []),
               blueprint.gate_result("lint", True, []),
               blueprint.gate_result("review", True, []),
               blueprint.gate_result("blueprint", False, blocked),
               blueprint.gate_result("runtime", True, [])]
    if blueprint.fidelity_claim(results) is not False:
        fail("gate 4 failing alone still produced a claim")
    MEASURED["blueprint_findings_blocked"] = len(blocked)
    return "pass"


def scenario_staleness_blocks(built):
    """RELIABILITY-03: a mid-flow source edit marks dependents stale and blocks
    acceptance until a rebind, migrate, supersede, or retain review is
    recorded."""
    import blueprint, corpus_15b, course, director, journal

    root = built["course_root"]

    # Fresh: nothing is stale and an acceptance is not blocked by staleness.
    rows = blueprint.staleness_report(built["dependents"])
    if any(r["stale"] for r in rows):
        fail("an unedited source reads stale")
    if blueprint.acceptance_block(rows, []):
        fail("a fresh dependent was blocked")

    # The mid-flow edit. The live fingerprint is recomputed from the bytes.
    moved = corpus_15b.edit_source(
        {"source_path": built["dependency_path"]}, "revised mid flow")
    live = corpus_15b.current_fingerprint(built["dependency_path"])
    if live != moved:
        fail("the recomputed fingerprint disagrees with the edit's return")
    if moved == built["dependency_base_fingerprint"]:
        fail("the edit did not change the fingerprint")

    stale_rows = blueprint.staleness_report(
        [dict(d, current_fingerprint=live) for d in built["dependents"]])
    if not all(r["stale"] for r in stale_rows):
        fail("the edited source did not make its dependents stale")

    bank_before = open(built["bank_path"], "rb").read()
    text_before = course.read_course(root)["text"]
    entries_before = len(list(journal.entries(root)))
    try:
        director.accept_revision(
            root, root, built["migration_accept"], _settings(), "human",
            "weibao", "reviewed", staleness_rows=stale_rows, dispositions=[])
    except director.DirectorError as exc:
        if exc.code != "director.acceptance_blocked":
            fail("a stale dependent raised %r" % (exc.code,))
    else:
        fail("a stale dependent did not block the acceptance")
    if course.read_course(root)["text"] != text_before:
        fail("a blocked acceptance changed the sidecar")
    entry = list(journal.entries(root))[-1]
    if entry["state"] != "refused":
        fail("the blocked acceptance's entry state is %r" % (entry["state"],))
    if built["dependency_object_id"] not in (entry["message"] or ""):
        fail("the refusal does not name the blocked dependency")
    if open(built["bank_path"], "rb").read() != bank_before:
        fail("the stale derivative was rebuilt; RELIABILITY-03 says blocked, "
             "not rebuilt")

    # All four dispositions clear the block, retain included.
    cleared = 0
    for disposition in blueprint.STALENESS_DISPOSITIONS:
        dispositions = [blueprint.disposition_record(
            d["object_id"], d["dependency_object_id"], disposition,
            "reviewer", "weibao", "reviewed after the source moved",
            d["base_fingerprint"], live) for d in built["dependents"]]
        if blueprint.acceptance_block(stale_rows, dispositions):
            fail("a recorded %s disposition did not clear the block"
                 % disposition)
        else:
            cleared += 1
    MEASURED["dispositions_cleared"] = cleared

    # A second edit supersedes the disposition and blocks again.
    dispositions = [blueprint.disposition_record(
        d["object_id"], d["dependency_object_id"], "retain", "reviewer",
        "weibao", "reviewed after the source moved", d["base_fingerprint"],
        live) for d in built["dependents"]]
    again = corpus_15b.edit_source(
        {"source_path": built["dependency_path"]}, "revised twice")
    rows_again = blueprint.staleness_report(
        [dict(d, current_fingerprint=again) for d in built["dependents"]])
    refusals = blueprint.acceptance_block(rows_again, dispositions)
    if not refusals:
        fail("a decision recorded against the earlier fingerprint cleared a "
             "later change")
    elif refusals[0]["code"] != "blueprint.disposition_superseded":
        fail("a superseded disposition gave code %r" % (refusals[0]["code"],))
    MEASURED["stale_rows"] = len(stale_rows)
    return "pass"


def scenario_migration_accept_and_reject(built):
    """ROADMAP 15B: one proposal accepted and one rejected through the reviewer
    path, with the live autonomy policy re-read at accept time."""
    import blueprint, course, director, graph, journal

    root = built["course_root"]
    fresh = blueprint.staleness_report(built["dependents"])

    # The policy is re-read at accept time: recommend-only refuses.
    doc_before = course.read_course(root)["text"]
    try:
        director.accept_revision(
            root, root, built["migration_accept"],
            _settings("recommend-only", 0), "human", "weibao", "reviewed",
            staleness_rows=fresh, dispositions=[])
    except director.DirectorError as exc:
        if exc.code != "director.autonomy_exceeded":
            fail("a recommend-only policy raised %r" % (exc.code,))
    else:
        fail("a recommend-only policy permitted an acceptance")
    if course.read_course(root)["text"] != doc_before:
        fail("a policy-refused acceptance changed the sidecar")

    # Accept one.
    director.accept_revision(
        root, root, built["migration_accept"], _settings(), "human", "weibao",
        "reviewed against the new edition", staleness_rows=fresh,
        dispositions=[], decision="accept")
    rows = course.read_course(root)["doc"]["migrations"]
    accepted = [r for r in rows
                if r["migration_id"] == built["migration_accept"]][0]
    if accepted["state"] != "accepted":
        fail("the accepted proposal reads %r" % (accepted["state"],))
    if accepted["reviewer"] != "weibao":
        fail("the accepted proposal's reviewer is %r" % (accepted["reviewer"],))

    # Reject another.
    director.accept_revision(
        root, root, built["migration_reject"], _settings(), "human", "weibao",
        "the split loses a prerequisite edge", staleness_rows=fresh,
        dispositions=[], decision="reject")
    rows = course.read_course(root)["doc"]["migrations"]
    rejected = [r for r in rows
                if r["migration_id"] == built["migration_reject"]][0]
    if rejected["state"] != "rejected":
        fail("the rejected proposal reads %r" % (rejected["state"],))
    if not any(r["migration_id"] == built["migration_reject"] for r in rows):
        fail("a rejected proposal was removed rather than recorded")

    # The proposer may not settle its own proposal.
    try:
        director.accept_revision(
            root, root, built["migration_self"], _settings(), "human",
            built["self_proposer"], "granting my own", staleness_rows=fresh,
            dispositions=[])
    except Exception as exc:
        if getattr(exc, "code", "") != "graph.migration_self_accept":
            fail("a self-accept raised %r" % (getattr(exc, "code", exc),))
    else:
        fail("the proposer settled its own proposal")

    # A settled proposal is not settled again.
    try:
        director.accept_revision(
            root, root, built["migration_accept"], _settings(), "human",
            "weibao", "again", staleness_rows=fresh, dispositions=[])
    except Exception as exc:
        if getattr(exc, "code", "") != "graph.migration_already_settled":
            fail("a re-settlement raised %r" % (getattr(exc, "code", exc),))
    else:
        fail("an accepted proposal was accepted twice")

    # The 14B bypass guard still fires, in this same run.
    try:
        graph.set_migration_state(course.read_course(root)["doc"],
                                  built["migration_self"], "accepted")
    except graph.GraphError as exc:
        if exc.code != "graph.migration_state_not_settable":
            fail("the bypass guard raised %r" % (exc.code,))
    else:
        fail("the 14B bypass guard no longer refuses; the two new paths did "
             "not open exactly two ways to settle a proposal")

    MEASURED["settlements"] = 2
    return "pass"


def scenario_sparse_evidence_proposal(built):
    """AGENT-03: a proposal over two attempts names its window, its
    denominator, and its uncertainty, and mints no mastery percentage."""
    import blueprint, corpus_15b

    rows = corpus_15b.build_sparse_evidence()
    if len(rows) != 2:
        fail("the sparse fixture carries %d rows, not two" % len(rows))
    record = blueprint.evidence_proposal(
        corpus_15b.PROPOSAL_OBJECTIVE, rows, corpus_15b.PROPOSAL_WINDOW,
        ["response"], ["confidence", "response_time_ms"],
        ["the two attempts were minutes apart, so the second may be recall "
         "of the first rather than learning"])

    if record["denominator"] != 2:
        fail("the denominator is %r" % (record["denominator"],))
    if record["uncertainty"] != "sparse":
        fail("two attempts read %r" % (record["uncertainty"],))
    if record["window"].get("boundary") != "half-open":
        fail("the window's boundary is %r" % (record["window"].get("boundary"),))
    for key in ("start", "end"):
        if not record["window"].get(key):
            fail("the window has no %s" % key)
    if not record["missing_signals"]:
        fail("the proposal names no missing signals")
    if not record["competing_explanations"]:
        fail("the proposal names no competing explanation")
    if record["status"] != "recommendation":
        fail("the proposal's status is %r" % (record["status"],))

    found = walk_forbidden(record, "the proposal")
    if found:
        fail("the proposal carries aggregate-shaped values at %r" % (found,))

    MEASURED["proposal_denominator"] = record["denominator"]
    MEASURED["proposal_uncertainty"] = record["uncertainty"]
    return "pass"


def scenario_course_audit(built):
    """ROADMAP 15B: one cited report that names which existing state vocabulary
    each claim came from and mints no fourth."""
    import blueprint, corpus_15b

    signals = corpus_15b.build_audit_signals()
    report = blueprint.course_audit(
        "course-1", signals["treatment_rows"], signals["coverage_rows"],
        signals["quality_findings"], signals["blueprint_findings"],
        signals["vocabulary_members"], "fp", "tracer")

    for row in report["rows"]:
        if row["vocabulary"] not in blueprint.COVERAGE_VOCABULARIES:
            fail("an audit row cites %r" % (row["vocabulary"],))
    if len(report["vocabularies_cited"]) < 2:
        fail("the audit cited %d vocabularies; the fixture carries two"
             % len(report["vocabularies_cited"]))
    found = walk_forbidden(report, "the course audit")
    if found:
        fail("the audit carries aggregate-shaped values at %r" % (found,))
    MEASURED["audit_rows"] = len(report["rows"])
    MEASURED["audit_vocabularies"] = len(report["vocabularies_cited"])
    return "pass"


def scenario_journal_replay(built):
    """RELIABILITY-02 as 15B extends it: the whole operation replays from the
    journal alone, in a fresh process."""
    import journal

    root = built["course_root"]
    probe = subprocess.run(
        [sys.executable, "-c",
         "import sys, json; sys.path.insert(0, %r); import journal; "
         "rows = [e for e in journal.entries(%r) "
         "if e.get('operation') == 'agent_operation']; "
         "print(json.dumps([[e['state'], (e.get('code') or '')] "
         "for e in rows]))" % (ROOT, root)],
        capture_output=True, text=True, timeout=120)
    if probe.returncode != 0:
        fail("a fresh-process replay failed: %s" % (probe.stderr[-300:],))
        return "pass"
    replayed = json.loads(probe.stdout)
    if not replayed:
        fail("the run left no agent_operation entries to replay")
    states = {row[0] for row in replayed}
    if "refused" not in states:
        fail("no refusal was journaled; a refusal nobody recorded is "
             "indistinguishable from a revision nobody proposed")
    if "applied" not in states:
        fail("no applied acceptance was journaled")
    if "accept_revision" not in journal.RECORD_TYPES:
        fail("accept_revision is not a journal record type")
    MEASURED["journal_entries"] = len(list(journal.entries(root)))
    MEASURED["agent_entries"] = len(replayed)
    return "pass"


def measure_budgets(elapsed):
    """Measured figures only. This function asserts nothing."""
    print("measured on: %s %s, Python %s"
          % (platform.system(), platform.machine(), sys.version.split()[0]))
    print("measured whole tracer: %.3f s" % elapsed)
    for key in sorted(MEASURED):
        print("measured %s: %s" % (key, MEASURED[key]))


def main():
    started = time.monotonic()
    if not shipped_suite_check():
        print("TRACER: 0 passed, %d skipped, %d failed"
              % (len(SKIPS), len(FAILURES)))
        return 1 if FAILURES else 0

    import corpus_15b
    import evidence

    tmp = tempfile.mkdtemp(prefix="acceptance-")
    results = []
    # The evidence log's bytes before the run, so the claim that nothing here
    # writes evidence is measured rather than asserted.
    evidence_log = os.path.join(ROOT, "fixtures", "selection_evidence.jsonl")
    before_bytes = open(evidence_log, "rb").read()
    try:
        built = corpus_15b.build_all_15b(os.path.join(tmp, "corpus"))
        results.append(("five_gate_acceptance",
                        scenario_five_gate_acceptance(built)))
        results.append(("fidelity_claim_ordering",
                        scenario_fidelity_claim_ordering(built)))
        results.append(("staleness_blocks", scenario_staleness_blocks(built)))
        results.append(("migration_accept_and_reject",
                        scenario_migration_accept_and_reject(built)))
        results.append(("sparse_evidence_proposal",
                        scenario_sparse_evidence_proposal(built)))
        results.append(("course_audit", scenario_course_audit(built)))
        results.append(("journal_replay", scenario_journal_replay(built)))

        if open(evidence_log, "rb").read() != before_bytes:
            fail("the run wrote to the evidence log; no part of this phase "
                 "may touch the evidence store")

        for name, status in results:
            print("scenario %s: %s" % (name, status))
        measure_budgets(time.monotonic() - started)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    passed = sum(1 for _, status in results if status == "pass")
    if FAILURES:
        passed = max(0, passed - len(FAILURES))
    print("TRACER: %d passed, %d skipped, %d failed"
          % (passed, len(SKIPS), len(FAILURES)))
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
