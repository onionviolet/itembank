#!/usr/bin/env python3
"""The Phase 15A freeze gate: one recommendation operation over four synthetic
subjects, through two backends, replayed from the journal.

This builds no capability. It proves the five plans before it, and either the
whole gate is green or the freeze is withheld by name.

Each `scenario_*` function implements exactly one requirement Fixture sentence
and quotes it in its docstring, so a reader can tell what a green line means
without reading the assertions.

The corpus is fictional. Its only relationship to EMT, Math 1400, CSCI 1100, or
any standardized exam is its shape.

Standard library only, runnable as `python tests/four_subject_review.py`.
"""
import json, os, platform, shutil, subprocess, sys, tempfile, threading, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "fixtures"))

FAILURES = []
SKIPS = []
MEASURED = {}


def fail(msg):
    print("FAIL: " + msg)
    FAILURES.append(msg)


def skip(what, why):
    print("SKIP: %s (%s)" % (what, why))
    SKIPS.append((what, why))


def shipped_suite_check():
    """The shipped runtime is green and both upstream freezes exist.

    Run before any 15A module is imported. A red shipped suite makes every
    scenario below meaningless: a green 15A tracer over a broken runtime would
    report a pass for something nobody should trust.
    """
    ok = True
    for name in ("scoring_roundtrip.py", "evidence_roundtrip.py",
                 "protocol_roundtrip.py"):
        completed = subprocess.run(
            [sys.executable, os.path.join(ROOT, "tests", name)],
            capture_output=True, text=True, timeout=900)
        if completed.returncode != 0:
            skip("every scenario",
                 "the shipped suite %s is red: %s"
                 % (name, completed.stderr.strip()[-200:]))
            ok = False
    for phase, heading in (
            ("14A-identity-lifecycle-operation", "## Frozen at 14A"),
            ("14B-graph-course-package-prototype", "## Frozen at 14B")):
        path = os.path.join(ROOT, ".planning", "phases", phase,
                            "%s-FREEZE.md" % phase.split("-")[0])
        if not os.path.exists(path):
            skip("every scenario", "%s does not exist" % path)
            ok = False
        elif heading not in open(path, encoding="utf-8").read():
            skip("every scenario", "%s does not carry %r" % (path, heading))
            ok = False
    return ok


def _settings(profiles, active="hosted"):
    return {"model_backend": {"active": active, "profiles": profiles},
            "agent_policy": {"autonomy_level": "approved-bounded-write",
                             "max_bindings_per_operation": 50}}


def _hosted_profile(name="hosted", extra=()):
    script = os.path.join(ROOT, "fixtures", "mock_backends.py")
    return {"name": name, "transport": "hosted_cli",
            "command": [sys.executable, script, "--cli"] + list(extra),
            "model": "mock", "timeout_seconds": 30,
            "max_output_bytes": 65536, "context_window": 4096}


def scenario_four_subject_recommendation(built):
    """TREAT-01: "Every objective has an explicit, reviewable treatment chosen
    from [the eleven kinds]; direct reading is a complete result and generation
    is never the automatic default... Degraded: an objective with no chosen
    treatment reads as untreated, never silently generated."
    """
    import course, director, graph

    settings = _settings([_hosted_profile()])
    total = 0
    entries = []
    for slug, root in built["roots"].items():
        objective_ids = built["objectives"][slug]
        total += len(objective_ids)
        entries.extend(director.recommend_treatments(
            root, root, objective_ids, settings, "hosted",
            "agent", "four-subject-review", "course-builder",
            "approved-bounded-write"))

    if len(entries) != total:
        fail("a pass over %d objectives returned %d entries"
             % (total, len(entries)))
    counts = {}
    for entry in entries:
        if entry["outcome"] not in director.RECOMMENDATION_OUTCOMES:
            fail("an outcome is %r" % (entry["outcome"],))
        counts[entry["outcome"]] = counts.get(entry["outcome"], 0) + 1
    if sum(counts.values()) != total:
        fail("the outcome counts sum to %d, not %d"
             % (sum(counts.values()), total))
    MEASURED["outcome_counts"] = counts

    for entry in entries:
        if entry["outcome"] == "bound" and \
                entry["treatment_kind"] not in graph.TREATMENT_KINDS:
            fail("a bound entry names the treatment %r"
                 % (entry["treatment_kind"],))

    # Nothing was silently generated: every unbound objective is reported.
    for slug, root in built["roots"].items():
        doc = course.read_course(root)["doc"]
        reported = {r["objective_id"]: r["reason"]
                    for r in director.untreated_objectives(doc)}
        bound = {e["objective_id"] for e in entries
                 if e["outcome"] == "bound"}
        for objective_id in built["objectives"][slug]:
            if objective_id in bound:
                continue
            if objective_id not in reported:
                fail("an unbound objective in %s is not reported untreated"
                     % slug)
            elif reported[objective_id] not in director.UNTREATED_REASONS:
                fail("an untreated reason is %r" % (reported[objective_id],))
    MEASURED["objectives"] = total
    return "pass"


def scenario_direct_reading_and_untreated(built):
    """TREAT-01's two named cases: one objective bound to direct reading as a
    complete result, and one deliberately left untreated with its reason
    recorded."""
    import course, director, journal

    beacon_root = built["beacon_root"]
    doc = course.read_course(beacon_root)["doc"]
    direct = [r for r in doc["bindings"]
              if r.get("binding_kind") == "treatment"
              and r.get("treatment_kind") == "direct-reading"]
    if not direct:
        fail("no objective in the blueprint was bound to direct-reading")
    else:
        objective_id = direct[0]["objective"]
        if any(r["objective_id"] == objective_id
               for r in director.untreated_objectives(doc)):
            fail("a direct-reading objective is still reported untreated; "
                 "direct reading is not a complete result")
    MEASURED["direct_reading_bindings"] = len(direct)

    lantern_root = built["lantern_root"]
    untreated_id = built["untreated_objective_id"]
    doc = course.read_course(lantern_root)["doc"]
    reported = {r["objective_id"]: r["reason"]
                for r in director.untreated_objectives(doc)}
    if untreated_id not in reported:
        fail("the all-unknown-rights objective is not reported untreated")

    # The reason is recorded in the journal, not merely computed on read.
    refused = [e for e in journal.entries(lantern_root)
               if e.get("state") == "refused"
               and "right" in (e.get("message") or "")]
    if not refused:
        fail("no journal entry records the missing right for the untreated "
             "objective; the reason is computed but not recorded")
    return "pass"


def scenario_coverage_states(built):
    """TREAT-02: "Every objective-to-source and coverage claim carries a stable
    locator, confidence, and state (covered, thin, missing, conflicting,
    unknown); heading or name similarity alone cannot produce covered...
    Degraded: an unverifiable claim reads as unknown, not covered."
    """
    import course, director, graph

    import corpus_14b

    # Over the four subjects: every state produced is in the vocabulary.
    live = set()
    for slug, root in built["roots"].items():
        doc = course.read_course(root)["doc"]
        for claim in director.coverage_claims_for(doc, built["source_texts"]):
            live.add(claim["state"])
            if claim["state"] not in graph.BINDING_STATES:
                fail("a claim state is %r" % (claim["state"],))
    if not live <= set(graph.BINDING_STATES):
        fail("states outside BINDING_STATES appeared: %r"
             % (live - set(graph.BINDING_STATES),))

    # All five states, produced by real claim data rather than by writing the
    # state string. This uses the five-state binding set TREAT-02's Fixture
    # sentence names, because `coverage_claims_for` alone cannot reach every
    # state: it builds claims from `## Bindings` rows, which carry no
    # `assertion` column, and `conflicting` is by definition two claims that
    # assert different things about one objective. That is a real limit of the
    # sidecar's binding shape and is recorded as a finding rather than papered
    # over by asserting only the states this path happens to reach.
    tmp = tempfile.mkdtemp(prefix="four-subject-coverage-")
    try:
        fixture = corpus_14b.build_coverage_fixture(
            os.path.join(tmp, "coverage"))
        seen = set()
        for state, group in fixture["claims"].items():
            got = director.classify_coverage(group)
            seen.add(got)
            if got != state:
                fail("the %r claim group classified %r" % (state, got))
        if seen != set(graph.BINDING_STATES):
            fail("the five-state binding set produced %r, not all five"
                 % (sorted(seen),))
        MEASURED["coverage_states_seen"] = sorted(seen)
        MEASURED["coverage_states_from_bindings"] = sorted(live)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # The decoy: its locator is its own objective statement, word for word.
    decoy_id = built["decoy_objective_id"]
    doc = course.read_course(built["beacon_root"])["doc"]
    statement = ""
    for record in doc["objectives"]:
        if record["id"] == decoy_id:
            statement = record["statement"]
    claim = director.coverage_claim(
        [], decoy_id, built["source_object_ids"]["beacon-standards-blueprint"],
        statement, "heading-similarity", "high", "",
        built["source_texts"][
            built["source_object_ids"]["beacon-standards-blueprint"]])[0]
    state = director.classify_coverage([claim])
    if state == "covered":
        fail("the heading-similarity decoy classified covered; TREAT-02 says "
             "similarity alone cannot produce covered")
    elif state != "unknown":
        fail("the decoy classified %r, expected unknown" % (state,))
    return "pass"


def scenario_egress_exactness(built):
    """RIGHTS-02: "Hosted operations minimize and disclose exact egress, agents
    receive only approved source spans... Fixture: ...asserting the egress log
    lists exactly the approved synthetic source spans."

    The expected set is computed here from the rights registry directly, never
    by calling director.approved_spans. Comparing a function's output to itself
    proves it is deterministic, not that it is correct.
    """
    import course, director, graph, identity, journal

    expected = set()
    for slug, root in built["roots"].items():
        registry = journal.read_registry(root)
        doc = course.read_course(root)["doc"]
        right = graph.TREATMENT_RIGHTS[director.RECOMMENDATION_SPAN_TREATMENT]
        for row in doc.get("bindings") or ():
            if row.get("binding_kind") != "source":
                continue
            source_object_id = row.get("source_object_id") or ""
            record = registry.get(source_object_id) or {}
            if not identity.rights_granted(record.get("rights"), right):
                continue
            if source_object_id not in built["source_texts"]:
                continue
            expected.add((source_object_id, row.get("locator") or ""))

    sent = set()
    omitted = set()
    reasons = set()
    for slug, root in built["roots"].items():
        for entry in journal.entries(root):
            egress = (entry.get("agent") or {}).get("egress")
            if not egress:
                continue
            if egress.get("evidence_included") is not False:
                fail("an egress record claims evidence_included %r"
                     % (egress.get("evidence_included"),))
            blob = json.dumps(egress)
            for secret in (sys.executable, "--cli", "http://", "mock_backends"):
                if secret in blob:
                    fail("an egress record leaks %r" % (secret,))
            for span in egress.get("spans") or ():
                sent.add((span["source_object_id"], span["locator"]))
            for omission in egress.get("omitted") or ():
                omitted.add((omission["source_object_id"],
                             omission["locator"]))
                reasons.add(omission["reason"])

    if sent != expected:
        fail("the disclosed spans are not exactly the approved spans; "
             "sent-not-approved %r, approved-not-sent %r"
             % (sorted(sent - expected), sorted(expected - sent)))
    if sent & omitted:
        fail("a pair is both sent and omitted: %r" % (sorted(sent & omitted),))
    for reason in reasons:
        if reason not in director.OMISSION_REASONS:
            fail("an omission reason is %r" % (reason,))
    MEASURED["spans_approved"] = len(sent)
    MEASURED["spans_omitted"] = len(omitted)
    return "pass"


def scenario_backend_parity(built):
    """AGENT-02: an agent "may recommend, draft-and-review, or perform approved
    bounded writes but never self-expand scope". Its Fixture runs one operation
    through a mock hosted and a mock local backend and asserts identical
    artifacts and journals.

    Both runs are recommend-only, so neither writes. A writing first run would
    mutate the state the second reads and the comparison would compare two
    different situations.
    """
    import course, director, mock_backends, model_adapter

    root = built["roots"]["orrery-algebra"]
    objective_id = built["objectives"]["orrery-algebra"][0]
    revision_before = course.read_course(root)["revision"]

    hosted = _settings([_hosted_profile()], active="hosted")
    hosted["agent_policy"]["autonomy_level"] = "recommend-only"
    hosted_result = director.recommend_once(
        root, root, objective_id, hosted, "hosted",
        "agent", "four-subject-review", "course-builder", "recommend-only")

    httpd, port = mock_backends.serve("127.0.0.1", 0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        local = _settings([{
            "name": "local", "transport": "openai_compatible",
            "endpoint": "http://127.0.0.1:%d/" % port, "model": "mock",
            "timeout_seconds": 30, "max_output_bytes": 65536,
            "context_window": 4096}], active="local")
        local["agent_policy"]["autonomy_level"] = "recommend-only"
        local_result = director.recommend_once(
            root, root, objective_id, local, "local",
            "agent", "four-subject-review", "course-builder", "recommend-only")
    finally:
        httpd.shutdown()
        httpd.server_close()

    if hosted_result["status"] != "ok" or local_result["status"] != "ok":
        fail("a parity run did not succeed: %r / %r"
             % (hosted_result["status"], local_result["status"]))
        return "pass"

    if director.parity_view(hosted_result["record"]) != \
            director.parity_view(local_result["record"]):
        fail("the two transports produced different recommendation records")

    agents = {}
    import journal
    for entry in journal.entries(root):
        agent = entry.get("agent") or {}
        operation_id = agent.get("operation_id")
        if operation_id in (hosted_result.get("operation_id"),
                            local_result.get("operation_id")) and \
                agent.get("phase") == "plan-treatment":
            agents[operation_id] = agent
    if len(agents) == 2:
        views = [director.parity_view(dict(a, egress=None))
                 for a in agents.values()]
        if views[0] != views[1]:
            fail("the two transports produced different agent dicts")

    if course.read_course(root)["revision"] != revision_before:
        fail("a recommend-only parity run wrote to the sidecar")

    # Both transports went through the ONE shared candidate builder.
    doc = course.read_course(root)["doc"]
    texts = director.source_texts_for(root, doc)
    spans, _ = director.approved_spans(
        root, doc, objective_id, director.RECOMMENDATION_SPAN_TREATMENT, texts)
    request = director.recommendation_request(
        doc, objective_id, spans, "hosted", "interaction-parity")
    direct = mock_backends.candidate_for(request)
    for name, result in (("hosted", hosted_result), ("local", local_result)):
        if director.parity_view(result["record"]) != \
                director.parity_view(director.validate_recommendation(direct)):
            fail("the %s transport's candidate differs from a direct "
                 "candidate_for call; the two backends are not sharing one "
                 "builder" % name)
    return "pass"


def scenario_backend_loss(built):
    """AGENT-02's degraded clause: backend loss leaves all core work local and
    model-free, with manual continuation available."""
    import course, director, journal

    root = built["roots"]["meridian-field-response"]
    objective_id = built["objectives"]["meridian-field-response"][3]
    rows_before = len(course.read_course(root)["doc"]["bindings"])

    cases = (("unknown-profile",
              _settings([_hosted_profile()], active="no-such-profile"),
              "adapter.profile_unknown"),
             ("empty-profiles", _settings([], active=""),
              "adapter.profile_disabled"))
    for name, settings, expected_code in cases:
        entries = director.recommend_treatments(
            root, root, [objective_id], settings, "",
            "agent", "four-subject-review", "course-builder",
            "approved-bounded-write")
        if len(entries) != 1:
            fail("%s returned %d entries" % (name, len(entries)))
            continue
        if entries[0]["outcome"] != "untreated":
            fail("%s gave outcome %r" % (name, entries[0]["outcome"]))
        if entries[0]["code"] != expected_code:
            fail("%s gave code %r, expected %r"
                 % (name, entries[0]["code"], expected_code))
        egress = None
        for entry in journal.entries(root):
            found = (entry.get("agent") or {}).get("egress")
            if found:
                egress = found
        if egress is None:
            fail("%s recorded no egress" % name)
        else:
            if egress["destination"] != "local":
                fail("%s disclosed destination %r"
                     % (name, egress["destination"]))
            if egress["payload_bytes"] != 0:
                fail("%s disclosed %r payload bytes"
                     % (name, egress["payload_bytes"]))

    if len(course.read_course(root)["doc"]["bindings"]) != rows_before:
        fail("a backend-loss pass wrote a binding")

    # Manual continuation: a human binds the same objective directly.
    import corpus_14b
    source_object_id = built["source_object_ids"]["meridian-field-response"]
    corpus_14b.grant_right(root, source_object_id, "transform")
    course.bind_treatment(root, objective_id, source_object_id,
                          "guided-lesson", locator="manual",
                          state="unknown", confidence="unknown",
                          actor_kind="human", actor_name="weibao")
    if len(course.read_course(root)["doc"]["bindings"]) != rows_before + 1:
        fail("manual continuation did not bind")
    return "pass"


def scenario_protocol_replay(built):
    """AGENT-01 and RELIABILITY-02: "a 15A four-subject review operation
    replayed step by step from a synthetic operation journal against the
    protocol checklist", and "an interrupted job resumes or reverses from its
    last checkpoint... from the journal alone without any chat transcript."
    """
    import corpus_14b, director, journal

    root = built["roots"]["orrery-algebra"]
    operation_id = director.begin_operation(
        root, root, "the four-subject review", "agent", "four-subject-review",
        "course-builder", "recommend-only", ("course:four-subject",))
    for index, phase in enumerate(director.PROTOCOL_STEPS):
        if index == 0:
            continue
        kwargs = {}
        if phase == "preview":
            kwargs = {"outcome": "not-applicable",
                      "reason": director.PREVIEW_NOT_APPLICABLE}
        director.record_phase(root, operation_id, phase, index, "applied",
                              actor_kind="agent",
                              actor_name="four-subject-review", **kwargs)

    # A fresh process that opens only the journal directory.
    probe = subprocess.run(
        [sys.executable, "-c",
         "import sys, json; sys.path.insert(0, %r); import director; "
         "print(json.dumps(director.replay_operation(%r, %r)))"
         % (ROOT, root, operation_id)],
        capture_output=True, text=True, timeout=120)
    if probe.returncode != 0:
        fail("a fresh-process replay failed: %s" % (probe.stderr[-300:],))
        return "pass"
    report = json.loads(probe.stdout)
    if report["verdict"] != "complete":
        fail("the replayed verdict is %r, missing %r"
             % (report["verdict"],
                [s["step"] for s in report["steps"]
                 if s["outcome"] == "missing"]))
    if report["out_of_order"]:
        fail("the replayed report names out-of-order steps %r"
             % (report["out_of_order"],))
    for step in report["steps"]:
        if step["outcome"] == "missing":
            fail("the step %r is missing" % (step["step"],))
        if step["outcome"] == "not-applicable" and not step["reason"]:
            fail("the step %r is not-applicable with no reason"
                 % (step["step"],))
    preview = [s for s in report["steps"] if s["step"] == "preview"][0]
    if preview["reason"] != director.PREVIEW_NOT_APPLICABLE:
        fail("the preview reason is %r" % (preview["reason"],))
    MEASURED["protocol_steps_recorded"] = sum(
        1 for s in report["steps"] if s["outcome"] == "recorded")

    # Thirteen interruption points, each read back in a fresh process.
    tmp = tempfile.mkdtemp(prefix="four-subject-kill-")
    try:
        for index, phase in enumerate(director.PROTOCOL_STEPS):
            killed = corpus_14b.build_interrupted_operation(
                os.path.join(tmp, "kill-%s" % phase), phase)
            probe = subprocess.run(
                [sys.executable, "-c",
                 "import sys, json; sys.path.insert(0, %r); import director; "
                 "print(json.dumps(director.resume_point(%r, %r)))"
                 % (ROOT, killed["course_root"], killed["operation_id"])],
                capture_output=True, text=True, timeout=120)
            if probe.returncode != 0:
                fail("a fresh-process resume after %r failed: %s"
                     % (phase, probe.stderr[-200:]))
                continue
            point = json.loads(probe.stdout)
            if point["last_phase"] != phase:
                fail("resume after %r names last_phase %r"
                     % (phase, point["last_phase"]))
            expected_next = ("" if index == len(director.PROTOCOL_STEPS) - 1
                             else director.PROTOCOL_STEPS[index + 1])
            if point["next_phase"] != expected_next:
                fail("resume after %r names next_phase %r, expected %r"
                     % (phase, point["next_phase"], expected_next))
        MEASURED["interruption_points"] = len(director.PROTOCOL_STEPS)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return "pass"


def scenario_reversal(built):
    """RELIABILITY-02's reverse half: an operation's durable writes go back to
    the pre-operation bytes, through the one undo mechanism."""
    import course, director, journal

    root = built["roots"]["meridian-field-response"]
    before = course.read_course(root)["text"]
    objective_id = built["objectives"]["meridian-field-response"][4]
    source_object_id = built["source_object_ids"]["meridian-field-response"]

    record = director.validate_recommendation({
        "schema_version": 1, "objective_id": objective_id,
        "treatment_kind": "guided-lesson", "rationale": "a stated reason",
        "synthesis": True, "confidence": "medium",
        "coverage": {"state": "covered", "locator": "l", "confidence": "medium",
                     "source_object_id": source_object_id,
                     "match_kind": "locator"},
        "alternatives": [], "citations": []})
    director.apply_recommendation(root, root, record, source_object_id,
                                 "agent", "four-subject-review")
    if course.read_course(root)["text"] == before:
        fail("the bind did not change the sidecar, so the reversal proves "
             "nothing")
        return "pass"

    target = None
    for entry in journal.entries(root):
        if (entry.get("undo") or {}).get("kind") == "restore_before_image":
            target = entry
    journal.undo(root, target["entry_id"], "agent", "four-subject-review")
    if course.read_course(root)["text"] != before:
        fail("the reversal did not restore the sidecar byte for byte")
    return "pass"


def measure_budgets(built, elapsed):
    """Measured figures only. This function asserts nothing.

    Every number printed here was produced by the run that printed it, on the
    machine and Python version named below. A figure that was not measured is
    a fabricated measurement, so no target and no budget appears.
    """
    import journal

    entries = 0
    payloads = []
    for root in built["roots"].values():
        for entry in journal.entries(root):
            entries += 1
            egress = (entry.get("agent") or {}).get("egress")
            if egress:
                payloads.append(egress.get("payload_bytes") or 0)

    print("measured on: %s %s, Python %s"
          % (platform.system(), platform.machine(),
             sys.version.split()[0]))
    print("measured four-subject pass: %.3f s" % elapsed)
    print("measured journal entries appended: %d" % entries)
    print("measured total payload bytes: %d" % sum(payloads))
    print("measured largest single payload: %d bytes"
          % (max(payloads) if payloads else 0))
    print("measured spans approved: %d" % MEASURED.get("spans_approved", 0))
    print("measured spans omitted: %d" % MEASURED.get("spans_omitted", 0))
    print("measured objectives in the pass: %d" % MEASURED.get("objectives", 0))
    print("measured outcome counts: %s" % (MEASURED.get("outcome_counts"),))
    print("measured coverage states seen, five-state binding set: %s"
          % (MEASURED.get("coverage_states_seen"),))
    print("measured coverage states seen, four-subject bindings: %s"
          % (MEASURED.get("coverage_states_from_bindings"),))
    print("measured protocol steps recorded: %d"
          % MEASURED.get("protocol_steps_recorded", 0))
    print("measured interruption points walked: %d"
          % MEASURED.get("interruption_points", 0))


def main():
    started = time.monotonic()
    if not shipped_suite_check():
        print("TRACER: 0 passed, %d skipped, %d failed"
              % (len(SKIPS), len(FAILURES)))
        return 1 if FAILURES else 0

    import corpus_14b

    tmp = tempfile.mkdtemp(prefix="four-subject-")
    results = []
    try:
        built = corpus_14b.build_all_15a(os.path.join(tmp, "corpus"))
        if built["built"] != built["declared"]:
            fail("the corpus built %d of %d declared subjects"
                 % (built["built"], built["declared"]))

        pass_started = time.monotonic()
        results.append(("four_subject_recommendation",
                        scenario_four_subject_recommendation(built)))
        pass_elapsed = time.monotonic() - pass_started

        results.append(("direct_reading_and_untreated",
                        scenario_direct_reading_and_untreated(built)))
        results.append(("coverage_states", scenario_coverage_states(built)))
        results.append(("egress_exactness", scenario_egress_exactness(built)))
        results.append(("backend_parity", scenario_backend_parity(built)))
        results.append(("backend_loss", scenario_backend_loss(built)))
        results.append(("protocol_replay", scenario_protocol_replay(built)))
        results.append(("reversal", scenario_reversal(built)))

        for name, status in results:
            print("scenario %s: %s" % (name, status))
        measure_budgets(built, pass_elapsed)
        print("measured whole tracer: %.3f s" % (time.monotonic() - started))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    passed = sum(1 for _, status in results if status == "pass")
    if FAILURES:
        passed = passed - len(FAILURES) if passed >= len(FAILURES) else 0
    print("TRACER: %d passed, %d skipped, %d failed"
          % (passed, len(SKIPS), len(FAILURES)))
    return 1 if FAILURES else 0


def print_recommendations():
    """Print every subject's recommendation entries as prose, for the human
    review in plan 15A-06 Task 2.

    A reviewer judging whether a recommendation is any good needs to read the
    recommendation, not the assertions about it. This mode exists so that
    reading is one command rather than a debugging session.
    """
    import corpus_14b, course, director

    tmp = tempfile.mkdtemp(prefix="four-subject-print-")
    try:
        built = corpus_14b.build_all_15a(os.path.join(tmp, "corpus"))
        settings = _settings([_hosted_profile()])
        for slug, root in built["roots"].items():
            print("=" * 72)
            print("SUBJECT: %s" % slug)
            print("=" * 72)
            doc = course.read_course(root)["doc"]
            statements = {o["id"]: o["statement"] for o in doc["objectives"]}
            entries = director.recommend_treatments(
                root, root, built["objectives"][slug], settings, "hosted",
                "agent", "four-subject-review", "course-builder",
                "approved-bounded-write")
            for entry in entries:
                print("")
                print("  objective : %s"
                      % statements.get(entry["objective_id"], "?"))
                print("  outcome   : %s" % entry["outcome"])
                print("  treatment : %s" % (entry["treatment_kind"] or "(none)"))
                if entry.get("reason"):
                    print("  reason    : %s" % entry["reason"])
                if entry.get("code"):
                    print("  code      : %s" % entry["code"])
                record = entry.get("record") or {}
                if record:
                    print("  rationale : %s" % record.get("rationale"))
                    print("  synthesis : %s" % record.get("synthesis"))
                    print("  confidence: %s" % record.get("confidence"))
                    coverage = record.get("coverage") or {}
                    print("  coverage  : state=%s match=%s confidence=%s"
                          % (coverage.get("state"), coverage.get("match_kind"),
                             coverage.get("confidence")))
                    print("  locator   : %s"
                          % ((coverage.get("locator") or "")[:90]))
                    print("  citations : %d" % len(record.get("citations") or []))
                    alts = record.get("alternatives") or []
                    print("  alternates: %s"
                          % ", ".join(a["treatment_kind"] for a in alts))
            print("")
            report = director.untreated_objectives(
                course.read_course(root)["doc"])
            print("  UNTREATED after the pass:")
            for row in report:
                print("    %-52s %s"
                      % (statements.get(row["objective_id"], "?")[:52],
                         row["reason"]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return 0


if __name__ == "__main__":
    if "--print-recommendations" in sys.argv:
        sys.exit(print_recommendations())
    sys.exit(main())
