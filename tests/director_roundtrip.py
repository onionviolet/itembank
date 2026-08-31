#!/usr/bin/env python3
"""Phase 15A: one objective from declared intent to accepted binding, and the
five ways that path refuses.

This is the thin slice plan 15A-01 Task 4 names. It proves the agent-client
tier exists as one path: `director.py` drafts and validates, every durable
write reaches disk through `course.py` and therefore through
`journal.commit_operation`, and every rights decision reads the live registry
at the moment of the operation rather than a value carried on a record.

The degraded states are the point, not the happy path. A missing backend
executable, a provider refusal, a candidate that fails its schema, a candidate
naming a twelfth treatment kind, and a right revoked between two operations
each refuse by name, write no binding, and leave the sidecar bytes untouched.

Standard library only, runnable as `python tests/director_roundtrip.py`.
"""
import json, os, shutil, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "fixtures"))
import course                                              # noqa: E402
import graph                                               # noqa: E402
import identity                                            # noqa: E402
import journal                                             # noqa: E402
import model_adapter                                       # noqa: E402
import schema_validate                                     # noqa: E402
import resources                                           # noqa: E402

FAILURES = []

# The exact JSON a hint request serialized to before this plan touched
# model_adapter.py. Recorded rather than recomputed: a golden string the test
# carries is the only form of this assertion that can fail when the builder
# changes, which is the whole point of it.
GOLDEN_HINT_REQUEST = (
    '{"interaction_id": "interaction-0001", "operation": "hint", "payload": '
    '{"fact_manifest": ["f1"], "item_context": {"stem": "x"}, '
    '"learner_response": {"raw": "a"}, "permitted_tier": 2}, '
    '"profile": "hosted", "schema_version": 1, "version": "1"}')

PRIOR_PAYLOAD_KEYS = ("item_context", "learner_response", "permitted_tier",
                      "fact_manifest", "rubric_points", "author_request")

PRIOR_ENTRY_KEYS = (
    "schema_version", "entry_id", "timestamp", "operation", "state",
    "resolves_entry", "object_id", "kind", "revision", "parent_revision",
    "path", "expected_fingerprint", "before_fingerprint", "after_fingerprint",
    "before_image", "undo", "source_object_id", "source_revision",
    "restores_revision", "origin", "code", "message", "rights",
)


def fail(msg):
    print("FAIL: " + msg)
    FAILURES.append(msg)


def mock_profile(name="hosted", extra_args=()):
    """A hosted_cli profile whose command runs fixtures/mock_backends.py."""
    script = os.path.join(ROOT, "fixtures", "mock_backends.py")
    return {"name": name, "transport": "hosted_cli",
            "command": [sys.executable, script, "--cli"] + list(extra_args),
            "model": "mock", "timeout_seconds": 30,
            "max_output_bytes": 65536, "context_window": 4096}


def make_settings(active, profiles):
    return {"model_backend": {"active": active, "profiles": profiles}}


def check_adapter_is_additive():
    """The fourth enum member breaks none of the three shipped operations."""
    schema = json.loads(resources.read_text("schemas/model_adapter.schema.json"))
    enum = schema["$defs"]["request"]["properties"]["operation"]["enum"]
    if enum != ["hint", "rubric_review", "author", "treatment_recommend"]:
        fail("the operation enum is %r" % (enum,))

    if "recommendation_request" not in model_adapter._PAYLOAD_KEYS:
        fail("_PAYLOAD_KEYS lacks recommendation_request: %r"
             % (model_adapter._PAYLOAD_KEYS,))
    if model_adapter._PAYLOAD_KEYS[:6] != PRIOR_PAYLOAD_KEYS:
        fail("the six prior payload keys moved: %r"
             % (model_adapter._PAYLOAD_KEYS,))

    request = model_adapter.request_from_operation(
        "hint", "interaction-0001", "hosted",
        item_context={"stem": "x"}, learner_response={"raw": "a"},
        permitted_tier=2, fact_manifest=["f1"])
    serialized = json.dumps(request, ensure_ascii=False, sort_keys=True)
    if serialized != GOLDEN_HINT_REQUEST:
        fail("a hint request no longer serializes to its golden string:\n"
             "  got %s\n  want %s" % (serialized, GOLDEN_HINT_REQUEST))

    settings = make_settings("hosted", [mock_profile()])
    request = model_adapter.request_from_operation(
        "treatment_recommend", "interaction-0002", "hosted")
    result = model_adapter.invoke(request, settings)
    if result["status"] != "unavailable":
        fail("a recommendation with no payload returned %r" % (result,))
    elif result["error"]["code"] != "adapter.request_invalid":
        fail("the empty-payload code is %r" % (result["error"],))
    elif result["error"]["message"] != \
            "treatment_recommend requires payload.recommendation_request":
        fail("the empty-payload message is %r" % (result["error"],))

    rec_schema = json.loads(
        resources.read_text("schemas/treatment_recommendation.schema.json"))
    try:
        schema_validate.check_schema(rec_schema)
    except Exception as exc:
        fail("the recommendation schema uses an unsupported keyword: %s" % exc)


def check_journal_extension_is_two_lines():
    """One new record type and one new entry key. Nothing else moved."""
    if "agent_operation" not in journal.RECORD_TYPES:
        fail("agent_operation is not a journal record type")
    if len(journal.ENTRY_KEYS) != 24:
        fail("ENTRY_KEYS has %d members, expected 24"
             % len(journal.ENTRY_KEYS))
    if journal.ENTRY_KEYS[-1] != "agent":
        fail("the last entry key is %r, expected agent"
             % (journal.ENTRY_KEYS[-1],))
    if journal.ENTRY_KEYS[:23] != PRIOR_ENTRY_KEYS:
        fail("the twenty-three prior entry keys changed: %r"
             % (journal.ENTRY_KEYS[:23],))
    if len(journal.OPERATION_TYPES) != 6:
        fail("OPERATION_TYPES has %d members, expected 6"
             % len(journal.OPERATION_TYPES))
    if "agent_operation" in journal.OPERATION_TYPES:
        fail("agent_operation is a file-operation type; it is a record type")

    import director
    if director.AGENT_ENTRY_KEYS != (
            "operation_id", "intent", "actor_role", "autonomy", "scopes",
            "phase", "phase_index", "checkpoint", "proposal", "egress"):
        fail("AGENT_ENTRY_KEYS is %r" % (director.AGENT_ENTRY_KEYS,))


def check_mock_backend():
    """One candidate builder, reachable three ways, deterministic."""
    import mock_backends
    import subprocess
    import urllib.request

    request = {"payload": {"recommendation_request": {
        "schema_version": 1, "course_object_id": "c1", "objective_id": "o1",
        "objective_statement": "Identify scene hazards on arrival",
        "treatment_kinds": list(graph.TREATMENT_KINDS),
        "binding_states": list(graph.BINDING_STATES),
        "source_spans": [{"source_object_id": "s1", "locator": "section 1.2"}],
        "attempt": 1}}}

    candidate = mock_backends.candidate_for(request)
    if candidate["treatment_kind"] not in graph.TREATMENT_KINDS:
        fail("the mock treatment_kind is %r" % (candidate["treatment_kind"],))
    if mock_backends.candidate_for(request) != candidate:
        fail("candidate_for is not deterministic")

    script = os.path.join(ROOT, "fixtures", "mock_backends.py")
    completed = subprocess.run(
        [sys.executable, script, "--cli"], input=json.dumps(request),
        text=True, capture_output=True, timeout=30)
    if completed.returncode != 0:
        fail("--cli exited %d: %r" % (completed.returncode, completed.stderr))
    elif json.loads(completed.stdout) != candidate:
        fail("--cli output differs from candidate_for")

    httpd, port = mock_backends.serve("127.0.0.1", 0)
    import threading
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        body = json.dumps(request).encode("utf-8")
        req = urllib.request.Request(
            "http://127.0.0.1:%d/" % port, data=body, method="POST",
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            served = json.loads(resp.read().decode("utf-8"))
        if served != candidate:
            fail("the served candidate differs from candidate_for")
    finally:
        httpd.shutdown()
        httpd.server_close()

    completed = subprocess.run(
        [sys.executable, script, "--refuse"], input="{}", text=True,
        capture_output=True, timeout=30)
    if completed.returncode == 0:
        fail("--refuse exited 0")

    settings = make_settings("refuser", [mock_profile("refuser", ["--refuse"])])
    # --cli then --refuse: the __main__ block dispatches on --refuse first.
    result = model_adapter.invoke(
        model_adapter.request_from_operation(
            "treatment_recommend", "interaction-0003", "refuser",
            recommendation_request=request["payload"]["recommendation_request"]),
        settings)
    if result["status"] != "unavailable":
        fail("a refusing provider returned %r" % (result["status"],))
    elif result["error"]["code"] != "adapter.provider_refused":
        fail("a refusing provider gave code %r" % (result["error"]["code"],))


def check_thin_slice():
    """One objective from declared intent to accepted binding, and back."""
    import director
    import corpus_14b
    import mock_backends

    tmp = tempfile.mkdtemp(prefix="director-")
    try:
        built = corpus_14b.build_three_domains(os.path.join(tmp, "corpus"))
        # lantern-computing carries transform: granted, which is the right a
        # guided lesson consumes. meridian-field-response grants nothing.
        lantern = [d for d in built["domains"]
                   if d["slug"] == "lantern-computing"][0]
        meridian = [d for d in built["domains"]
                    if d["slug"] == "meridian-field-response"][0]

        if len(director.new_operation_id()) < 8:
            fail("new_operation_id is shorter than eight characters")
        if director.new_operation_id() == director.new_operation_id():
            fail("new_operation_id repeated itself")

        base = lantern["root"]
        before = len(list(journal.entries(base)))
        operation_id = director.begin_operation(
            base, base, "recommend a treatment for one objective",
            "agent", "director-roundtrip", "course-builder", "propose",
            ("course:" + lantern["slug"],))
        after = list(journal.entries(base))
        if len(after) != before + 1:
            fail("begin_operation appended %d entries" % (len(after) - before))
        entry = after[-1]
        if entry["operation"] != "agent_operation":
            fail("the intent entry's operation is %r" % (entry["operation"],))
        if entry["state"] != "applied":
            fail("the intent entry's state is %r" % (entry["state"],))
        agent = entry.get("agent") or {}
        if set(agent) != set(director.AGENT_ENTRY_KEYS):
            fail("the agent dict's keys are %r" % (sorted(agent),))
        if agent.get("phase") != "declare-intent":
            fail("the intent entry's phase is %r" % (agent.get("phase"),))
        if agent.get("phase_index") != 0:
            fail("the intent entry's phase_index is %r"
                 % (agent.get("phase_index"),))

        read = course.read_course(base)
        doc = read["doc"]
        objective_id = lantern["objectives"][0]
        objective_ids_for_egress = objective_id
        spans = [{"source_object_id": lantern["source_object_id"],
                  "locator": "chapter 1"}]
        request = director.recommendation_request(
            doc, objective_id, spans, "hosted", "interaction-1000")
        # Validated against the whole document, the way model_adapter._invoke
        # does. Validating the $defs.request subschema alone would strand its
        # $ref and fail for a reason that has nothing to do with the request.
        errs = schema_validate.validate(request, model_adapter._SCHEMA)
        if errs:
            fail("the built request fails the adapter schema: %r" % (errs[:2],))
        inner = request["payload"]["recommendation_request"]
        if inner["treatment_kinds"] != list(graph.TREATMENT_KINDS):
            fail("the request's treatment_kinds is %r"
                 % (inner["treatment_kinds"],))
        if inner["binding_states"] != list(graph.BINDING_STATES):
            fail("the request's binding_states is %r"
                 % (inner["binding_states"],))

        # Learner evidence never reaches a backend.
        for forbidden in ("score", "verdict", "attempt_number", "session_id",
                          "mark", "response", "canonical", "note"):
            try:
                director.recommendation_request(
                    doc, objective_id,
                    [{"source_object_id": "s", "locator": "l",
                      forbidden: "x"}],
                    "hosted", "interaction-1001")
            except director.DirectorError as exc:
                if exc.code != "director.evidence_forbidden":
                    fail("a %s span raised %r" % (forbidden, exc.code))
                elif forbidden not in exc.message:
                    fail("the %s refusal does not name the key: %r"
                         % (forbidden, exc.message))
            else:
                fail("a span carrying %r was accepted" % (forbidden,))

        candidate = mock_backends.candidate_for(request)
        record = director.validate_recommendation(candidate)
        if set(record) != set(director.RECOMMENDATION_KEYS):
            fail("the normalized record's keys are %r" % (sorted(record),))

        bad_kind = dict(candidate, treatment_kind="flashcards")
        try:
            director.validate_recommendation(bad_kind)
        except director.DirectorError as exc:
            if exc.code != "director.unknown_treatment_kind":
                fail("a twelfth treatment kind raised %r" % (exc.code,))
            elif "eleven" not in exc.message:
                fail("the twelfth-kind message is %r" % (exc.message,))
        else:
            fail("a twelfth treatment kind was accepted")

        missing = dict(candidate)
        del missing["citations"]
        try:
            director.validate_recommendation(missing)
        except director.DirectorError as exc:
            if exc.code != "director.recommendation_invalid":
                fail("a missing citations key raised %r" % (exc.code,))
            elif "citations" not in exc.message:
                fail("the missing-key message does not name it: %r"
                     % (exc.message,))
        else:
            fail("a candidate missing citations was accepted")

        # The bind. lantern grants transform, so a transform-consuming
        # treatment is the one that can succeed here.
        granted = dict(record, treatment_kind="guided-lesson")
        bindings_before = len(course.read_course(base)["doc"]["bindings"])
        revision_before = course.read_course(base)["revision"]
        director.apply_recommendation(
            base, base, granted, lantern["source_object_id"],
            "agent", "director-roundtrip")
        read_after = course.read_course(base)
        bindings_after = read_after["doc"]["bindings"]
        if len(bindings_after) != bindings_before + 1:
            fail("the bind added %d rows"
                 % (len(bindings_after) - bindings_before))
        else:
            row = bindings_after[-1]
            if row.get("binding_kind") != "treatment":
                fail("the new row's binding_kind is %r"
                     % (row.get("binding_kind"),))
            if row.get("treatment_kind") != "guided-lesson":
                fail("the new row's treatment_kind is %r"
                     % (row.get("treatment_kind"),))
        if read_after["revision"] != (revision_before or 0) + 1:
            fail("the sidecar revision went %r -> %r"
                 % (revision_before, read_after["revision"]))

        # The egress record. Every recorded phase carries one, including the
        # phases that sent nothing: an absent key would leave a reader unable
        # to tell "nothing was sent" from "nobody recorded". So the assertion
        # is about the one phase that DID reach a backend, not about there
        # being exactly one egress dict in the journal.
        #
        # Plan 15A-01's behavior block asked for "exactly one journal entry
        # carries a non-null agent.egress whose destination is hosted". It was
        # written assuming the bind carried the send. The bind sends nothing,
        # so plan 15A-04 Task 3 makes every phase disclose, and this assertion
        # is narrowed to the claim that survives: exactly one HOSTED egress,
        # and it names real spans.
        # Assembling spans for a recommendation consumes `read`, and the
        # lantern source grants only `transform`. Without this the run is still
        # correct and still hosted, but it discloses zero spans, which would
        # make the assertion below pass for the wrong reason.
        corpus_14b.grant_right(base, lantern["source_object_id"], "read")
        # build_three_domains records sources and edges but no ## Bindings
        # rows, so there is nothing for approved_spans to approve until one
        # exists. Bound through the gated path, which is why the grant above
        # has to come first.
        course.bind_source(base, objective_ids_for_egress,
                           lantern["source_object_id"],
                           locator="chapter 1", state="unknown",
                           confidence="high", actor_kind="agent",
                           actor_name="director-roundtrip")
        settings = make_settings("hosted", [mock_profile()])
        result = director.recommend_once(
            base, base, objective_ids_for_egress, settings, "hosted",
            "agent", "director-roundtrip", "course-builder", "propose")
        if result["status"] != "ok":
            fail("the hosted recommendation returned %r" % (result,))

        all_egress = [(e.get("agent") or {}).get("egress")
                      for e in journal.entries(base)]
        all_egress = [e for e in all_egress if e]
        for egress in all_egress:
            if set(egress) != set(director.EGRESS_KEYS):
                fail("an egress dict's keys are %r" % (sorted(egress),))
                break
            if egress.get("evidence_included") is not False:
                fail("an egress dict claims evidence_included %r"
                     % (egress.get("evidence_included"),))
        hosted = [e for e in all_egress if e.get("destination") == "hosted"]
        if len(hosted) != 1:
            fail("%d entries carry a hosted egress record" % len(hosted))
        elif not hosted[0].get("spans"):
            fail("the hosted egress spans list is empty")
        local = [e for e in all_egress if e.get("destination") == "local"]
        for egress in local:
            if egress.get("payload_bytes") != 0:
                fail("a local egress claims %r payload bytes"
                     % (egress.get("payload_bytes"),))
            if egress.get("spans"):
                fail("a local egress names spans: %r" % (egress["spans"],))

        # A refused bind: meridian grants no rights at all.
        m_base = meridian["root"]
        m_read = course.read_course(m_base)
        m_bytes_before = m_read["text"]
        m_entries_before = len(list(journal.entries(m_base)))
        m_record = dict(record, objective_id=meridian["objectives"][0],
                        treatment_kind="guided-lesson")
        try:
            director.apply_recommendation(
                m_base, m_base, m_record, meridian["source_object_id"],
                "agent", "director-roundtrip")
        except director.DirectorError as exc:
            if exc.code != "director.rights_not_granted":
                fail("an ungranted bind raised %r" % (exc.code,))
            elif "transform" not in exc.message or "unknown" not in exc.message:
                fail("the refusal names neither right nor state: %r"
                     % (exc.message,))
        else:
            fail("a bind with no granted right succeeded")
        if course.read_course(m_base)["text"] != m_bytes_before:
            fail("a refused bind changed the sidecar bytes")
        m_after = list(journal.entries(m_base))
        if len(m_after) != m_entries_before + 1:
            fail("a refused bind appended %d entries"
                 % (len(m_after) - m_entries_before))
        else:
            refused = m_after[-1]
            if refused["state"] != "refused":
                fail("the refusal entry's state is %r" % (refused["state"],))
            if (refused.get("agent") or {}).get("phase") != "review":
                fail("the refusal entry's phase is %r"
                     % ((refused.get("agent") or {}).get("phase"),))

        # The rights check is live: revoke, then try a second objective with a
        # record whose own rights field still reads granted.
        corpus_14b.revoke_right(base, lantern["source_object_id"], "transform")
        second = dict(record, objective_id=lantern["objectives"][1],
                      treatment_kind="guided-lesson")
        second["coverage"] = dict(second["coverage"], state="covered")
        try:
            director.apply_recommendation(
                base, base, second, lantern["source_object_id"],
                "agent", "director-roundtrip")
        except director.DirectorError as exc:
            if exc.code != "director.rights_not_granted":
                fail("a revoked right raised %r" % (exc.code,))
            elif "denied" not in exc.message:
                fail("the revoked-right message does not name denied: %r"
                     % (exc.message,))
        else:
            fail("a revoked right still permitted a bind")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_backend_unavailable_leaves_the_objective_untreated():
    """A missing executable is a typed unavailable result, not an exception."""
    import director
    import corpus_14b

    tmp = tempfile.mkdtemp(prefix="director-down-")
    try:
        built = corpus_14b.build_three_domains(os.path.join(tmp, "corpus"))
        lantern = [d for d in built["domains"]
                   if d["slug"] == "lantern-computing"][0]
        base = lantern["root"]
        objective_id = lantern["objectives"][2]

        text_before = course.read_course(base)["text"]
        settings = make_settings("gone", [{
            "name": "gone", "transport": "hosted_cli",
            "command": ["/nonexistent/itembank-hosted-bin"],
            "model": "gone", "timeout_seconds": 5,
            "max_output_bytes": 1024, "context_window": 1024}])

        result = director.recommend_once(
            base, base, objective_id, settings, "gone",
            "agent", "director-roundtrip", "course-builder", "propose")
        if result["status"] != "unavailable":
            fail("a missing executable returned %r" % (result["status"],))
        if result["code"] != "adapter.executable_missing":
            fail("a missing executable gave code %r" % (result["code"],))
        if result["record"] is not None:
            fail("a missing executable returned a record")

        entry = list(journal.entries(base))[-1]
        if (entry.get("agent") or {}).get("phase") != "plan-treatment":
            fail("the unavailable entry's phase is %r"
                 % ((entry.get("agent") or {}).get("phase"),))
        if entry["state"] != "refused":
            fail("the unavailable entry's state is %r" % (entry["state"],))

        read = course.read_course(base)
        if read["text"] != text_before:
            fail("an unavailable backend changed the sidecar")
        treated = [r for r in read["doc"]["bindings"]
                   if r.get("objective") == objective_id
                   and r.get("binding_kind") == "treatment"]
        if treated:
            fail("the untreated objective gained %d treatment rows"
                 % len(treated))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_boundaries_are_structural():
    """director.py cannot reach the tier gate, evidence, the runtime, or the
    parser, and the proof is the absence of the attribute rather than a
    reviewer's care."""
    import director
    for forbidden in ("tier_gate", "evidence", "runtime", "model"):
        if hasattr(director, forbidden):
            fail("director imports %s" % forbidden)


def valid_candidate(**overrides):
    """One schema-valid candidate, overridable field by field."""
    candidate = {
        "schema_version": 1,
        "objective_id": "o1",
        "treatment_kind": "guided-lesson",
        "rationale": "a stated reason",
        "synthesis": True,
        "confidence": "medium",
        "coverage": {"state": "covered", "locator": "l1",
                     "confidence": "medium", "source_object_id": "s1",
                     "match_kind": "locator"},
        "alternatives": [],
        "citations": [{"source_object_id": "s1", "locator": "l1"}],
    }
    candidate.update(overrides)
    return candidate


def walk_floats(obj, path="$"):
    """Every float anywhere in `obj`, with the path that reached it."""
    found = []
    if isinstance(obj, float):
        found.append(path)
    elif isinstance(obj, dict):
        for key, value in obj.items():
            found.extend(walk_floats(value, "%s.%s" % (path, key)))
    elif isinstance(obj, (list, tuple)):
        for n, value in enumerate(obj):
            found.extend(walk_floats(value, "%s[%d]" % (path, n)))
    return found


def check_treatment_vocabulary():
    """One closed vocabulary, read from one place, closed on both sides."""
    import director
    import corpus_14b

    # There is one vocabulary and director reads it. Proven behaviorally:
    # narrow graph.TREATMENT_KINDS and confirm the ranking narrows with it.
    # A local copy in director.py would keep ranking against eleven.
    real_kinds = graph.TREATMENT_KINDS
    try:
        graph.TREATMENT_KINDS = ("direct-reading", "excerpt")
        ranked = director.rank_candidates(
            [{"treatment_kind": "excerpt", "confidence": "medium"},
             {"treatment_kind": "direct-reading", "confidence": "medium"}])
        if [c["treatment_kind"] for c in ranked] != ["direct-reading", "excerpt"]:
            fail("ranking against a narrowed vocabulary gave %r" % (ranked,))
        try:
            director.rank_candidates(
                [{"treatment_kind": "practice", "confidence": "medium"}])
        except director.DirectorError as exc:
            if exc.code != "director.unknown_treatment_kind":
                fail("a kind outside the narrowed vocabulary raised %r"
                     % (exc.code,))
        else:
            fail("director ranked a kind the vocabulary no longer holds; it "
                 "is reading its own copy of the eleven tokens")
    finally:
        graph.TREATMENT_KINDS = real_kinds

    # Both sides of the boundary.
    for kind in graph.TREATMENT_KINDS:
        try:
            record = director.validate_recommendation(
                valid_candidate(treatment_kind=kind))
        except director.DirectorError as exc:
            fail("the vocabulary member %r was refused: %s" % (kind, exc.code))
        else:
            if record["treatment_kind"] != kind:
                fail("validating %r yielded %r" % (kind, record["treatment_kind"]))
    try:
        director.validate_recommendation(
            valid_candidate(treatment_kind="flashcards"))
    except director.DirectorError as exc:
        if exc.code != "director.unknown_treatment_kind":
            fail("a twelfth kind raised %r" % (exc.code,))
    else:
        fail("a twelfth kind was accepted")

    empty = director.validate_recommendation(valid_candidate(treatment_kind=""))
    if empty["treatment_kind"] != "":
        fail("the empty treatment kind became %r" % (empty["treatment_kind"],))

    # Ranking and tie-break.
    record = valid_candidate(
        treatment_kind="practice", confidence="medium",
        alternatives=[{"treatment_kind": "excerpt", "confidence": "medium"}])
    candidates = director.treatment_candidates(record)
    if candidates[0] != {"treatment_kind": "practice", "confidence": "medium"}:
        fail("treatment_candidates put %r first" % (candidates[0],))
    if len(candidates) != 2:
        fail("treatment_candidates returned %d entries" % len(candidates))
    if director.treatment_candidates(valid_candidate(treatment_kind="")) != []:
        fail("an empty treatment kind produced a candidate entry")

    pair = [{"treatment_kind": "practice", "confidence": "medium"},
            {"treatment_kind": "excerpt", "confidence": "medium"}]
    ranked = director.rank_candidates(pair)
    if ranked[0]["treatment_kind"] != "excerpt":
        fail("the tie went to %r, not excerpt" % (ranked[0]["treatment_kind"],))
    if len(ranked) != 2:
        fail("a tie dropped a candidate: %r" % (ranked,))
    if director.rank_candidates(list(reversed(pair))) != ranked:
        fail("input order decided the tie")

    ordered = director.rank_candidates([
        {"treatment_kind": "human-review", "confidence": "unknown"},
        {"treatment_kind": "practice", "confidence": "high"},
        {"treatment_kind": "excerpt", "confidence": "low"}])
    if [c["treatment_kind"] for c in ordered] != \
            ["practice", "excerpt", "human-review"]:
        fail("confidence ranking gave %r" % (ordered,))

    if director.rank_candidates([]) != []:
        fail("rank_candidates([]) is not []")

    duplicated = director.rank_candidates([
        {"treatment_kind": "excerpt", "confidence": "medium"},
        {"treatment_kind": "excerpt", "confidence": "medium"}])
    if len(duplicated) != 1:
        fail("a duplicate candidate stayed two entries: %r" % (duplicated,))

    # Precision: closed tokens, never a number.
    for value in director.rank_candidates(pair):
        if value["confidence"] not in graph.EDGE_CONFIDENCES:
            fail("a ranked confidence is %r" % (value["confidence"],))

    numeric = valid_candidate(confidence=0.8, treatment_kind="flashcards")
    try:
        director.validate_recommendation(numeric)
    except director.DirectorError as exc:
        if exc.code != "director.recommendation_invalid":
            fail("a numeric confidence with a bad kind raised %r" % (exc.code,))
    else:
        fail("a numeric confidence was accepted")

    record = director.validate_recommendation(valid_candidate())
    floats = walk_floats(record)
    if floats:
        fail("a validated record carries floats at %r" % (floats,))

    if director.PARITY_VOLATILE_KEYS != tuple(
            sorted(director.PARITY_VOLATILE_KEYS)):
        fail("PARITY_VOLATILE_KEYS is unsorted: %r"
             % (director.PARITY_VOLATILE_KEYS,))
    view = director.parity_view(
        {"a": 1, "entry_id": "x", "b": [{"timestamp": "t", "c": 2}]})
    if view != {"a": 1, "b": [{"c": 2}]}:
        fail("parity_view returned %r" % (view,))

    # The empty kind refuses at bind time, before any rights lookup.
    tmp = tempfile.mkdtemp(prefix="director-empty-")
    try:
        built = corpus_14b.build_recommendation_fixture(
            os.path.join(tmp, "corpus"))
        base = built["course_root"]
        text_before = course.read_course(base)["text"]
        entries_before = len(list(journal.entries(base)))
        blank = director.validate_recommendation(
            valid_candidate(treatment_kind="",
                            objective_id=built["objective_ids"][0]))
        try:
            director.apply_recommendation(
                base, base, blank, built["source_object_ids"][0],
                "agent", "director-roundtrip")
        except director.DirectorError as exc:
            if exc.code != "director.empty_treatment_bind":
                fail("an empty-kind bind raised %r" % (exc.code,))
        else:
            fail("an empty treatment kind was bound")
        if course.read_course(base)["text"] != text_before:
            fail("an empty-kind bind changed the sidecar")
        after = list(journal.entries(base))
        if len(after) != entries_before + 1:
            fail("an empty-kind bind appended %d entries"
                 % (len(after) - entries_before))
        elif after[-1]["state"] != "refused":
            fail("the empty-kind refusal state is %r" % (after[-1]["state"],))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_direct_reading_complete():
    """Direct reading is a finished recommendation, and the gap report is
    computed from what was bound rather than from what was proposed."""
    import director
    import corpus_14b

    tmp = tempfile.mkdtemp(prefix="director-direct-")
    try:
        built = corpus_14b.build_recommendation_fixture(
            os.path.join(tmp, "corpus"))
        base = built["course_root"]
        granted = built["granted_source_object_id"]
        unknown = built["unknown_source_object_id"]
        objective_ids = built["objective_ids"]

        # The gap report before anything is bound.
        doc = course.read_course(base)["doc"]
        report = director.untreated_objectives(doc)
        for row in report:
            if set(row) != {"objective_id", "statement", "reason"}:
                fail("an untreated row's keys are %r" % (sorted(row),))
                break
            if row["reason"] not in director.UNTREATED_REASONS:
                fail("an untreated reason is %r" % (row["reason"],))
                break
        listed = [r["objective_id"] for r in report]
        authored = [o["id"] for o in doc["objectives"]]
        if listed != [o for o in authored if o in listed]:
            fail("the untreated report is not in authored order")
        for objective_id in objective_ids[:3]:
            row = [r for r in report if r["objective_id"] == objective_id]
            if not row:
                fail("an unbound objective is missing from the report")
            elif row[0]["reason"] != "no-recommendation":
                fail("a source-bound untreated objective reads %r"
                     % (row[0]["reason"],))
        unbound = [r for r in report
                   if r["objective_id"] == built["unbound_objective_id"]]
        if not unbound:
            fail("the objective with no source binding is not reported")
        elif unbound[0]["reason"] != "no-source-bound":
            fail("the no-source objective reads %r" % (unbound[0]["reason"],))

        # Direct reading binds, against a granted read right.
        record = director.validate_recommendation(valid_candidate(
            objective_id=objective_ids[0], treatment_kind="direct-reading"))
        rows_before = len(doc["bindings"])
        director.apply_recommendation(base, base, record, granted,
                                      "agent", "director-roundtrip")
        doc = course.read_course(base)["doc"]
        added = [r for r in doc["bindings"]
                 if r.get("objective") == objective_ids[0]
                 and r.get("binding_kind") == "treatment"]
        if len(doc["bindings"]) != rows_before + 1:
            fail("a direct-reading bind added %d rows"
                 % (len(doc["bindings"]) - rows_before))
        if len(added) != 1 or added[0]["treatment_kind"] != "direct-reading":
            fail("the direct-reading row is %r" % (added,))
        if any(r["objective_id"] == objective_ids[0]
               for r in director.untreated_objectives(doc)):
            fail("a direct-reading treated objective is still reported "
                 "untreated; direct reading is not a complete result")

        # Direct reading is not a free pass: an unknown read right refuses.
        text_before = course.read_course(base)["text"]
        second = director.validate_recommendation(valid_candidate(
            objective_id=objective_ids[1], treatment_kind="direct-reading"))
        try:
            director.apply_recommendation(base, base, second, unknown,
                                          "agent", "director-roundtrip")
        except director.DirectorError as exc:
            if exc.code != "director.rights_not_granted":
                fail("direct reading on an unknown right raised %r"
                     % (exc.code,))
            elif "read" not in exc.message or "unknown" not in exc.message:
                fail("the direct-reading refusal is %r" % (exc.message,))
        else:
            fail("direct reading bound against an unknown read right")
        if course.read_course(base)["text"] != text_before:
            fail("a refused direct-reading bind changed the sidecar")
        doc = course.read_course(base)["doc"]
        if not any(r["objective_id"] == objective_ids[1]
                   for r in director.untreated_objectives(doc)):
            fail("a refused objective left the untreated report")

        # Drafting without applying changes the report by nothing.
        settings = make_settings("hosted", [mock_profile()])
        before = director.untreated_objectives(course.read_course(base)["doc"])
        director.recommend_treatments(
            base, base, objective_ids, settings, "hosted",
            "agent", "director-roundtrip", "course-builder", "propose")
        after = director.untreated_objectives(course.read_course(base)["doc"])
        if before != after:
            fail("a recommend-only pass changed the untreated report")

        # A second pass does not re-propose the treated objective.
        entries = director.recommend_treatments(
            base, base, objective_ids, settings, "hosted",
            "agent", "director-roundtrip", "course-builder", "propose")
        if len(entries) != len(objective_ids):
            fail("a pass over %d objectives returned %d entries"
                 % (len(objective_ids), len(entries)))
        counts = {}
        for entry in entries:
            if entry["outcome"] not in director.RECOMMENDATION_OUTCOMES:
                fail("an outcome is %r" % (entry["outcome"],))
            counts[entry["outcome"]] = counts.get(entry["outcome"], 0) + 1
        if sum(counts.values()) != len(objective_ids):
            fail("the outcome counts sum to %d" % sum(counts.values()))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_generation_is_never_automatic():
    """No backend means no treatment. Not a local guess, not a default."""
    import director
    import corpus_14b

    tmp = tempfile.mkdtemp(prefix="director-nogen-")
    try:
        built = corpus_14b.build_recommendation_fixture(
            os.path.join(tmp, "corpus"))
        base = built["course_root"]
        objective_ids = built["objective_ids"]

        rows_before = len(course.read_course(base)["doc"]["bindings"])
        entries_before = len(list(journal.entries(base)))
        settings = make_settings("gone", [{
            "name": "gone", "transport": "hosted_cli",
            "command": ["/nonexistent/itembank-hosted-bin"],
            "model": "gone", "timeout_seconds": 5,
            "max_output_bytes": 1024, "context_window": 1024}])

        entries = director.recommend_treatments(
            base, base, objective_ids, settings, "gone",
            "agent", "director-roundtrip", "course-builder",
            "approved-bounded-write")
        if len(entries) != 4:
            fail("an unavailable pass returned %d entries" % len(entries))
        for entry in entries:
            if entry["outcome"] != "untreated":
                fail("an unavailable outcome is %r" % (entry["outcome"],))
            if entry["reason"] != "backend-unavailable":
                fail("an unavailable reason is %r" % (entry["reason"],))
            if entry["treatment_kind"] != "":
                fail("an unavailable entry invented the treatment %r; no code "
                     "path may produce a kind that did not come from a "
                     "validated candidate" % (entry["treatment_kind"],))

        rows_after = len(course.read_course(base)["doc"]["bindings"])
        if rows_after != rows_before:
            fail("an unavailable pass wrote %d bindings"
                 % (rows_after - rows_before))
        grew = len(list(journal.entries(base))) - entries_before
        if grew != 2 * len(objective_ids):
            fail("an unavailable pass appended %d journal entries, expected "
                 "one intent plus one refusal per objective" % grew)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


PROGRESS_KEY_NAMES = ("mastery", "completion", "readiness", "progress",
                      "percent", "score")


def walk_keys(obj, path="$"):
    """Every mapping key anywhere in `obj`, with the path that reached it."""
    found = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            found.append((key, "%s.%s" % (path, key)))
            found.extend(walk_keys(value, "%s.%s" % (path, key)))
    elif isinstance(obj, (list, tuple)):
        for n, value in enumerate(obj):
            found.extend(walk_keys(value, "%s[%d]" % (path, n)))
    return found


def check_recommendation_edges():
    """Empty, single, ordering, and repeated-run edges, and no progress value
    anywhere in a recommendation."""
    import director
    import corpus_14b

    tmp = tempfile.mkdtemp(prefix="director-edges-")
    try:
        # parity_view recurses through lists as well as dicts.
        nested = {"a": [{"timestamp": 1, "b": 2}], "operation_id": "x",
                  "c": {"d": [{"entry_id": "e", "f": 3}]}}
        view = director.parity_view(nested)
        if view != {"a": [{"b": 2}], "c": {"d": [{"f": 3}]}}:
            fail("parity_view over a nested list returned %r" % (view,))
        for key in director.PARITY_VOLATILE_KEYS:
            if key in json.dumps(director.parity_view(
                    {"x": [{key: 1}], key: 2})):
                fail("parity_view left %r behind" % (key,))

        built = corpus_14b.build_recommendation_fixture(
            os.path.join(tmp, "corpus"))
        base = built["course_root"]
        objective_ids = built["objective_ids"]
        settings = make_settings("hosted", [mock_profile()])

        # An empty pass opens no operation.
        entries_before = len(list(journal.entries(base)))
        empty = director.recommend_treatments(
            base, base, [], settings, "hosted",
            "agent", "director-roundtrip", "course-builder", "propose")
        if empty != []:
            fail("an empty pass returned %r" % (empty,))
        if len(list(journal.entries(base))) != entries_before:
            fail("an empty pass appended journal entries; an operation with "
                 "no work opens no operation")

        # A document with zero objectives.
        bare = graph.new_course("Bare course", "c-bare")
        if director.untreated_objectives(bare) != []:
            fail("untreated_objectives on an empty course returned %r"
                 % (director.untreated_objectives(bare),))

        # A single-objective pass.
        single = director.recommend_treatments(
            base, base, [objective_ids[0]], settings, "hosted",
            "agent", "director-roundtrip", "course-builder", "propose")
        if len(single) != 1:
            fail("a single-objective pass returned %d entries" % len(single))
        elif single[0]["objective_id"] != objective_ids[0]:
            fail("a single-objective pass returned %r"
                 % (single[0]["objective_id"],))

        # An objective with no source bound gets no generated treatment.
        unbound = director.recommend_treatments(
            base, base, [built["unbound_objective_id"]], settings, "hosted",
            "agent", "director-roundtrip", "course-builder",
            "approved-bounded-write")
        if len(unbound) != 1:
            fail("the unbound pass returned %d entries" % len(unbound))
        else:
            entry = unbound[0]
            if entry["outcome"] != "untreated":
                fail("the unbound objective's outcome is %r"
                     % (entry["outcome"],))
            record = entry.get("record") or {}
            coverage = record.get("coverage") or {}
            if coverage.get("state") != "missing":
                fail("the unbound coverage state is %r"
                     % (coverage.get("state"),))
            if coverage.get("match_kind") != "none":
                fail("the unbound match_kind is %r"
                     % (coverage.get("match_kind"),))

        # Ordering: the caller's order is preserved, not replaced.
        forward = director.recommend_treatments(
            base, base, objective_ids, settings, "hosted",
            "agent", "director-roundtrip", "course-builder", "propose")
        if [e["objective_id"] for e in forward] != list(objective_ids):
            fail("a forward pass reordered its objectives")
        backward = director.recommend_treatments(
            base, base, list(reversed(objective_ids)), settings, "hosted",
            "agent", "director-roundtrip", "course-builder", "propose")
        if [e["objective_id"] for e in backward] != list(reversed(objective_ids)):
            fail("a reversed pass did not preserve the caller's order")

        # The gap report is always document order, whatever ran before it.
        doc = course.read_course(base)["doc"]
        report = director.untreated_objectives(doc)
        authored = [o["id"] for o in doc["objectives"]]
        listed = [r["objective_id"] for r in report]
        if listed != [o for o in authored if o in listed]:
            fail("the gap report is not in authored order after a "
                 "reverse-order pass")

        # Repeated runs are stable.
        again = director.recommend_treatments(
            base, base, objective_ids, settings, "hosted",
            "agent", "director-roundtrip", "course-builder", "propose")
        if director.parity_view(forward) != director.parity_view(again):
            fail("two recommend-only passes over an unchanged document "
                 "differ after parity_view")

        # No progress value, no float, anywhere.
        for entry in forward:
            for key, path in walk_keys(entry):
                if key in PROGRESS_KEY_NAMES:
                    fail("a recommendation entry carries the key %r at %s"
                         % (key, path))
            floats = walk_floats(entry)
            if floats:
                fail("a recommendation entry carries floats at %r" % (floats,))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def coverage_claim_dict(**overrides):
    """One coverage claim, overridable field by field."""
    claim = {"objective_id": "o1", "source_object_id": "s1",
             "locator": "Section 2.1", "match_kind": "locator",
             "confidence": "high", "assertion": "",
             "span_chars": 300, "proposed_state": "covered",
             "state": "unknown"}
    claim.update(overrides)
    return claim


def check_coverage_classifier():
    """A coverage state is computed from a locator that either resolves or
    does not, by six rules in a fixed order."""
    import director

    # Normalization: line endings and NFC yes, case folding and prefixes no.
    if director.locator_key("Section  2.1\r\n") != \
            director.locator_key("Section  2.1\n"):
        fail("locator_key does not normalize line endings")
    if director.locator_key("\u00e9") != director.locator_key("e\u0301"):
        fail("locator_key does not apply NFC")
    if director.locator_key("Section 2.1") == director.locator_key("section 2.1"):
        fail("locator_key case folds; that reopens the similarity path")
    if director.locator_key("Section 2.1") == director.locator_key("Section 2"):
        fail("locator_key prefix matches")

    source = "Intro.\n\n## Section 2.1\n\nThe intake sequence begins here.\n"
    resolved = director.resolve_locator(source, "Section 2.1")
    if set(resolved) != {"resolved", "span_chars"}:
        fail("resolve_locator's keys are %r" % (sorted(resolved),))
    if not resolved["resolved"]:
        fail("an exact substring did not resolve")
    if resolved["span_chars"] != len("Section 2.1"):
        fail("the resolved span is %r" % (resolved["span_chars"],))
    if director.resolve_locator(source, "Section 9.9")["resolved"]:
        fail("an absent locator resolved")
    if director.resolve_locator("", "anything") != \
            {"resolved": False, "span_chars": 0}:
        fail("an empty source text did not refuse")
    if director.resolve_locator(source, "")["resolved"]:
        fail("an empty locator resolved; everything contains the empty "
             "string and a claim with no locator is not a claim")

    # Rule 1: no source is missing, whatever else the claim says.
    state = director.classify_coverage([coverage_claim_dict(
        source_object_id="", match_kind="locator", confidence="high")])
    if state != "missing":
        fail("rule 1 gave %r" % (state,))
    if director.classify_coverage([]) != "missing":
        fail("an empty claim list is not missing")

    # Rule 2: similarity alone can never be covered.
    for match_kind in ("heading-similarity", "none"):
        state = director.classify_coverage([coverage_claim_dict(
            match_kind=match_kind, confidence="high", span_chars=5000)])
        if state != "unknown":
            fail("a %s claim classified %r" % (match_kind, state))

    # Rule 3: two different assertions conflict; two equal ones do not.
    conflicting = director.classify_coverage([
        coverage_claim_dict(
            assertion="The intake sequence begins with scene safety."),
        coverage_claim_dict(
            assertion="The intake sequence begins with airway assessment.")])
    if conflicting != "conflicting":
        fail("two differing assertions classified %r" % (conflicting,))
    agreeing = director.classify_coverage([
        coverage_claim_dict(assertion="The intake sequence begins here."),
        coverage_claim_dict(assertion="The intake sequence begins here.")])
    if agreeing == "conflicting":
        fail("two identical assertions classified conflicting")

    # Rule 4: an unknown confidence is unknown, however good the locator.
    state = director.classify_coverage([coverage_claim_dict(
        confidence="unknown", span_chars=5000)])
    if state != "unknown":
        fail("rule 4 gave %r" % (state,))

    # Rule 5: the thin boundary, proven on both sides.
    if director.classify_coverage([coverage_claim_dict(span_chars=239)]) != "thin":
        fail("a 239-character span is not thin")
    if director.classify_coverage([coverage_claim_dict(span_chars=240)]) != "covered":
        fail("a 240-character span is not covered")
    if director.classify_coverage([coverage_claim_dict(
            confidence="low", span_chars=5000)]) != "thin":
        fail("a low-confidence claim is not thin")

    # Rule order is proven, not assumed: rules 2, 4 and 5 fire at once.
    state = director.classify_coverage([coverage_claim_dict(
        match_kind="heading-similarity", confidence="unknown",
        span_chars=10)])
    if state != "unknown":
        fail("a claim triggering rules 2, 4 and 5 classified %r; rule 2 must "
             "fire first" % (state,))

    # An unrecognized match kind is refused, never treated as a locator.
    try:
        director.classify_coverage([coverage_claim_dict(match_kind="fuzzy")])
    except director.DirectorError as exc:
        if exc.code != "director.unknown_match_kind":
            fail("an unknown match kind raised %r" % (exc.code,))
        elif "fuzzy" not in exc.message:
            fail("the unknown-match-kind message is %r" % (exc.message,))
    else:
        fail("an unknown match kind was classified rather than refused")

    # The vocabulary firewall.
    seen = set()
    for claims in ([coverage_claim_dict(source_object_id="")],
                   [coverage_claim_dict(match_kind="none")],
                   [coverage_claim_dict(assertion="a"),
                    coverage_claim_dict(assertion="b")],
                   [coverage_claim_dict(confidence="unknown")],
                   [coverage_claim_dict(span_chars=239)],
                   [coverage_claim_dict(span_chars=240)]):
        seen.add(director.classify_coverage(claims))
    if not seen <= set(graph.BINDING_STATES):
        fail("classify_coverage returned states outside BINDING_STATES: %r"
             % (seen - set(graph.BINDING_STATES),))
    if len(seen) != 5:
        fail("the six rules produced %d distinct states, expected all five"
             % len(seen))
    if hasattr(director, "auditor"):
        fail("director imports auditor; the auditor's coverage vocabulary is "
             "a different, correctly-scoped one")
    if len(director.MATCH_KINDS) != 3:
        fail("MATCH_KINDS has %d members" % len(director.MATCH_KINDS))
    if len(graph.BINDING_STATES) != 5:
        fail("BINDING_STATES has %d members after importing director"
             % len(graph.BINDING_STATES))


def check_coverage_states():
    """All five states produced by real fixture data, plus the decoy that must
    not read as covered."""
    import director
    import corpus_14b

    tmp = tempfile.mkdtemp(prefix="director-coverage-")
    try:
        built = corpus_14b.build_coverage_fixture(os.path.join(tmp, "corpus"))
        if set(built) < {"course_root", "source_texts", "claims", "decoy_claim"}:
            fail("build_coverage_fixture returned keys %r" % (sorted(built),))

        claims = built["claims"]
        if set(claims) != set(graph.BINDING_STATES):
            fail("the fixture's claim groups are %r" % (sorted(claims),))

        # All five states, produced by data rather than by naming the string.
        for state in graph.BINDING_STATES:
            group = claims[state]
            got = director.classify_coverage(group)
            if got != state:
                fail("the %r fixture group classified %r" % (state, got))
            for claim in group:
                if set(claim) != set(director.COVERAGE_CLAIM_KEYS):
                    fail("a %r claim's keys are %r" % (state, sorted(claim)))
                    break
                for field in ("state", "proposed_state"):
                    value = claim.get(field)
                    if value not in tuple(graph.BINDING_STATES) + ("",):
                        fail("a claim's %s is %r" % (field, value))

        # The heading-similarity decoy.
        decoy = built["decoy_claim"]
        if decoy["match_kind"] != "heading-similarity":
            fail("the decoy's match_kind is %r" % (decoy["match_kind"],))
        if decoy["confidence"] != "high":
            fail("the decoy's confidence is %r" % (decoy["confidence"],))
        if decoy["span_chars"] <= director.THIN_SPAN_CHARS:
            fail("the decoy's span is %r, not longer than THIN_SPAN_CHARS"
                 % (decoy["span_chars"],))
        got = director.classify_coverage([decoy])
        if got == "covered":
            fail("the heading-similarity decoy classified covered; TREAT-02 "
                 "says similarity alone can never produce covered")
        if got != "unknown":
            fail("the decoy classified %r, expected unknown" % (got,))

        # The decoy is otherwise a well-formed covered claim: match_kind is the
        # single field carrying the refusal.
        promoted = dict(decoy, match_kind="locator")
        if director.classify_coverage([promoted]) != "covered":
            fail("the decoy with match_kind locator classified %r; the decoy "
                 "is supposed to be covered in every respect but its match "
                 "kind" % (director.classify_coverage([promoted]),))

        # Duplicates and adjacency.
        source_text = list(built["source_texts"].values())[0]
        base_claims = director.coverage_claim(
            [], "o1", "s1", "Section 2.1", "locator", "high", "", source_text)
        if len(base_claims) != 1:
            fail("one claim produced a list of %d" % len(base_claims))
        try:
            director.coverage_claim(base_claims, "o1", "s1", "Section 2.1",
                                    "locator", "high", "", source_text)
        except director.DirectorError as exc:
            if exc.code != "director.duplicate_coverage_claim":
                fail("a duplicate claim raised %r" % (exc.code,))
            elif not all(v in exc.message for v in ("o1", "s1", "Section 2.1")):
                fail("the duplicate message does not name all three: %r"
                     % (exc.message,))
        else:
            fail("a duplicate claim was accepted")

        two = director.coverage_claim(base_claims, "o1", "s1", "Section 2.2",
                                      "locator", "high", "", source_text)
        if len(two) != 2:
            fail("a differing locator produced %d claims" % len(two))
        if len(base_claims) != 1:
            fail("coverage_claim mutated the list it was given")

        # Trailing line endings collide; letter case does not.
        try:
            director.coverage_claim(base_claims, "o1", "s1", "Section 2.1\r\n",
                                    "locator", "high", "", source_text)
        except director.DirectorError as exc:
            if exc.code != "director.duplicate_coverage_claim":
                fail("a line-ending variant raised %r" % (exc.code,))
        else:
            # "Section 2.1\r\n" normalizes to "Section 2.1\n", which is not
            # equal to "Section 2.1"; only the \r is removed. That is correct
            # and not a duplicate.
            pass
        cased = director.coverage_claim(base_claims, "o1", "s1", "section 2.1",
                                        "locator", "high", "", source_text)
        if len(cased) != 2:
            fail("a case variant was treated as a duplicate; locator_key must "
                 "not case-fold")

        # Ordering and stability over a real document.
        doc = course.read_course(built["course_root"])["doc"]
        first = director.coverage_claims_for(doc, built["source_texts"])
        second = director.coverage_claims_for(doc, built["source_texts"])
        if first != second:
            fail("two classification passes over one document differ")
        if json.dumps(first, sort_keys=True) != json.dumps(second, sort_keys=True):
            fail("two passes do not serialize byte-identically")

        authored = [o["id"] for o in doc["objectives"]]
        seen_order = []
        for claim in first:
            if claim["objective_id"] not in seen_order:
                seen_order.append(claim["objective_id"])
        if seen_order != [o for o in authored if o in seen_order]:
            fail("coverage claims are not in authored objective order")

        for claim in first:
            if claim["state"] not in graph.BINDING_STATES:
                fail("a computed claim state is %r" % (claim["state"],))
            if set(claim) != set(director.COVERAGE_CLAIM_KEYS):
                fail("a computed claim's keys are %r" % (sorted(claim),))
                break

        # A source absent from the mapping is unknown, never a crash.
        stripped = director.coverage_claims_for(doc, {})
        for claim in stripped:
            if claim["match_kind"] != "none":
                fail("an unreadable source produced match_kind %r"
                     % (claim["match_kind"],))
            if claim["span_chars"] != 0:
                fail("an unreadable source produced span_chars %r"
                     % (claim["span_chars"],))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_approved_spans():
    """An agent receives spans only from sources whose right reads granted in
    the live registry, and every exclusion is named."""
    import director
    import corpus_14b
    import inspect

    if [p for p in inspect.signature(director.approved_spans).parameters
            if "rights" in p]:
        fail("approved_spans takes a rights parameter; a rights value passed "
             "in is a rights value that can be stale")

    tmp = tempfile.mkdtemp(prefix="director-rights-")
    try:
        built = corpus_14b.build_rights_matrix_fixture(
            os.path.join(tmp, "corpus"))
        base = built["course_root"]
        doc = course.read_course(base)["doc"]
        objective_id = built["objective_id"]
        texts = built["source_texts"]
        all_granted, read_only, transform_only, nothing = built["source_ids"]

        def sources_for(kind, source_texts=None):
            spans, omissions = director.approved_spans(
                base, doc, objective_id, kind,
                texts if source_texts is None else source_texts)
            return ([s["source_object_id"] for s in spans],
                    omissions)

        # guided-lesson consumes transform.
        got, omissions = sources_for("guided-lesson")
        if set(got) != {all_granted, transform_only}:
            fail("guided-lesson approved %r" % (sorted(set(got)),))
        refused = {o["source_object_id"] for o in omissions
                   if o["reason"] == "rights-not-granted"}
        if not {read_only, nothing} <= refused:
            fail("a refused source is not disclosed: %r" % (sorted(refused),))
        for omission in omissions:
            if omission["reason"] not in director.OMISSION_REASONS:
                fail("an omission reason is %r" % (omission["reason"],))
            if omission["reason"] == "rights-not-granted" and \
                    "transform" not in json.dumps(omission):
                fail("a rights omission does not name the right: %r"
                     % (omission,))

        # direct-reading consumes read.
        got, _ = sources_for("direct-reading")
        if set(got) != {all_granted, read_only}:
            fail("direct-reading approved %r" % (sorted(set(got)),))

        # excerpt consumes quote.
        got, _ = sources_for("excerpt")
        if set(got) != {all_granted}:
            fail("excerpt approved %r" % (sorted(set(got)),))

        # No source is in both lists.
        spans, omissions = director.approved_spans(
            base, doc, objective_id, "guided-lesson", texts)
        span_ids = {s["source_object_id"] for s in spans}
        omitted_ids = {o["source_object_id"] for o in omissions}
        if span_ids & omitted_ids:
            fail("a source is both approved and omitted: %r"
                 % (sorted(span_ids & omitted_ids),))

        # Sorted and stable.
        key = lambda s: (s["source_object_id"],
                         director.locator_key(s["locator"]))
        if [key(s) for s in spans] != sorted(key(s) for s in spans):
            fail("the spans list is not sorted")
        again, _ = director.approved_spans(
            base, doc, objective_id, "guided-lesson", texts)
        if again != spans:
            fail("two approved_spans calls differ")

        # The read is live. A snapshot of granted does not authorize.
        snapshots = [r.get("rights_snapshot") for r in doc["bindings"]
                     if r.get("source_object_id") == all_granted]
        corpus_14b.revoke_right(base, all_granted, "transform")
        after, omissions = director.approved_spans(
            base, doc, objective_id, "guided-lesson", texts)
        if any(s["source_object_id"] == all_granted for s in after):
            fail("a revoked right still contributed spans; the binding row's "
                 "rights_snapshot is %r and a prior read said granted"
                 % (snapshots,))
        if not any(o["source_object_id"] == all_granted
                   and o["reason"] == "rights-not-granted" for o in omissions):
            fail("the revoked source is not disclosed as an omission")

        # Case matters: only the exact lowercase token grants.
        corpus_14b._set_right(base, all_granted, "transform", "Granted")
        cased, _ = director.approved_spans(
            base, doc, objective_id, "guided-lesson", texts)
        if any(s["source_object_id"] == all_granted for s in cased):
            fail("the exact string 'Granted' authorized a span")
        corpus_14b.grant_right(base, all_granted, "transform")

        # An unreadable source is disclosed, not a crash.
        _, omissions = director.approved_spans(
            base, doc, objective_id, "guided-lesson", {})
        if not omissions:
            fail("an empty source_texts produced no omissions")
        for omission in omissions:
            if omission["reason"] not in ("source-unreadable",
                                          "rights-not-granted"):
                fail("an unreadable source gave reason %r"
                     % (omission["reason"],))

        # The caps.
        capped = built["capped_objective_id"]
        spans, omissions = director.approved_spans(
            base, doc, capped, "guided-lesson", texts)
        if len(spans) != director.MAX_EGRESS_SPANS:
            fail("twelve eligible spans produced %d, expected the cap of %d"
                 % (len(spans), director.MAX_EGRESS_SPANS))
        capped_out = [o for o in omissions if o["reason"] == "span-cap"]
        if len(capped_out) != 4:
            fail("the span cap omitted %d spans, expected 4" % len(capped_out))
        for span in spans:
            if span["bytes"] != len(span["text"].encode("utf-8")):
                fail("a span's byte count is not its full text length; a span "
                     "must never be included partially")

        # Dedupe by normalized locator, but not by case.
        deduped = built["dedupe_objective_id"]
        spans, _ = director.approved_spans(
            base, doc, deduped, "guided-lesson", texts)
        locators = [s["locator"] for s in spans]
        keys = [director.locator_key(l) for l in locators]
        if len(keys) != len(set(keys)):
            fail("approved_spans returned duplicate normalized locators: %r"
                 % (locators,))

        # An objective with no source bindings.
        spans, omissions = director.approved_spans(
            base, doc, built["unbound_objective_id"], "guided-lesson", texts)
        if spans != [] or omissions != []:
            fail("an unbound objective returned %r / %r" % (spans, omissions))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_autonomy_policy():
    """Authority is settings-side, checked not self-reported, and an
    over-declaration is refused rather than narrowed."""
    import director
    import corpus_14b

    if director.AUTONOMY_LEVELS != ("recommend-only", "draft-and-review",
                                    "approved-bounded-write"):
        fail("AUTONOMY_LEVELS is %r" % (director.AUTONOMY_LEVELS,))

    def policy(level, cap=0):
        return {"agent_policy": {"autonomy_level": level,
                                 "max_bindings_per_operation": cap}}

    if director.autonomy_level({}) != "recommend-only":
        fail("an absent agent_policy read as %r"
             % (director.autonomy_level({}),))
    if director.autonomy_level({"agent_policy": {}}) != "recommend-only":
        fail("an empty agent_policy read as %r"
             % (director.autonomy_level({"agent_policy": {}}),))
    if director.autonomy_level(policy("draft-and-review")) != "draft-and-review":
        fail("autonomy_level did not read the configured value")

    # Within policy returns None, and specifically None.
    got = director.authorize_write(policy("approved-bounded-write", 5),
                                   "approved-bounded-write", 3)
    if got is not None:
        fail("authorize_write returned %r on the success path; returning a "
             "level would give a caller something to mistake for a grant"
             % (got,))
    if director.authorize_write(policy("approved-bounded-write", 5),
                                "recommend-only", 0) is not None:
        fail("declaring less than the policy allows was refused")

    # Over-declaration is refused, never narrowed.
    try:
        director.authorize_write(policy("recommend-only"),
                                 "approved-bounded-write", 0)
    except director.DirectorError as exc:
        if exc.code != "director.autonomy_exceeded":
            fail("an over-declaration raised %r" % (exc.code,))
        for needed in ("recommend-only", "approved-bounded-write", "refused"):
            if needed not in exc.message:
                fail("the over-declaration message lacks %r: %r"
                     % (needed, exc.message))
    else:
        fail("an over-declaring operation was permitted")

    # The binding cap.
    try:
        director.authorize_write(policy("approved-bounded-write", 2),
                                 "approved-bounded-write", 3)
    except director.DirectorError as exc:
        if exc.code != "director.bind_cap_exceeded":
            fail("an over-cap request raised %r" % (exc.code,))
        elif "3" not in exc.message or "2" not in exc.message:
            fail("the cap message names neither number: %r" % (exc.message,))
    else:
        fail("a request over the binding cap was permitted")

    # An unknown level is refused, never treated as the lowest.
    try:
        director.authorize_write(policy("approved-bounded-write", 5),
                                 "god-mode", 0)
    except director.DirectorError as exc:
        if exc.code != "director.autonomy_exceeded":
            fail("an unknown declared level raised %r" % (exc.code,))
        elif "god-mode" not in exc.message:
            fail("the unknown-level message does not name it: %r"
                 % (exc.message,))
    else:
        fail("an unknown autonomy level was permitted")

    # Wiring: a recommend-only policy writes nothing over a whole pass.
    tmp = tempfile.mkdtemp(prefix="director-autonomy-")
    try:
        built = corpus_14b.build_recommendation_fixture(
            os.path.join(tmp, "corpus"))
        base = built["course_root"]
        objective_ids = built["objective_ids"]
        settings = make_settings("hosted", [mock_profile()])
        settings.update(policy("recommend-only"))

        rows_before = len(course.read_course(base)["doc"]["bindings"])
        entries = director.recommend_treatments(
            base, base, objective_ids, settings, "hosted",
            "agent", "director-roundtrip", "course-builder",
            "approved-bounded-write")
        if len(entries) != len(objective_ids):
            fail("a refused pass returned %d entries" % len(entries))
        for entry in entries:
            if entry["outcome"] != "untreated":
                fail("a refused pass gave outcome %r" % (entry["outcome"],))
            if entry["code"] != "director.autonomy_exceeded":
                fail("a refused pass recorded code %r" % (entry["code"],))
        rows_after = len(course.read_course(base)["doc"]["bindings"])
        if rows_after != rows_before:
            fail("a recommend-only policy wrote %d bindings"
                 % (rows_after - rows_before))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def last_egress(base, phase="plan-treatment"):
    """The egress dict from the most recent entry recording `phase`.

    Not simply the last entry: an operation records phases after the one that
    reached a backend, so "the last entry" is whichever step happened to be
    recorded last rather than the step that sent something.
    """
    found = None
    for entry in journal.entries(base):
        agent = entry.get("agent") or {}
        if agent.get("phase") == phase and agent.get("egress"):
            found = agent["egress"]
    return found


def check_egress_record():
    """What left this machine is disclosed exactly: every span named, every
    omission named, and the byte count measured on the real request."""
    import director
    import corpus_14b
    import socket

    tmp = tempfile.mkdtemp(prefix="director-egress-")
    try:
        built = corpus_14b.build_rights_matrix_fixture(
            os.path.join(tmp, "corpus"))
        base = built["course_root"]
        objective_id = built["objective_id"]
        settings = make_settings("hosted", [mock_profile()])

        result = director.recommend_once(
            base, base, objective_id, settings, "hosted",
            "agent", "director-roundtrip", "course-builder", "propose")
        if result["status"] != "ok":
            fail("the hosted run returned %r" % (result["status"],))

        egress = last_egress(base)
        if not egress:
            fail("the hosted phase recorded no egress")
            return
        if set(egress) != set(director.EGRESS_KEYS):
            fail("the egress key set is %r" % (sorted(egress),))

        # Exactness against the request that was actually built.
        doc = course.read_course(base)["doc"]
        texts = director.source_texts_for(base, doc)
        spans, omissions = director.approved_spans(
            base, doc, objective_id, director.RECOMMENDATION_SPAN_TREATMENT,
            texts)
        request = director.recommendation_request(
            doc, objective_id, spans, "hosted", "interaction-egress")
        expected_bytes = len(json.dumps(
            request, ensure_ascii=False, sort_keys=True).encode("utf-8"))

        sent = {(s["source_object_id"], s["locator"]) for s in egress["spans"]}
        built_pairs = {(s["source_object_id"], s["locator"]) for s in spans}
        if sent != built_pairs:
            fail("the disclosed spans are not exactly the sent spans: %r vs %r"
                 % (sorted(sent), sorted(built_pairs)))
        for span in egress["spans"]:
            if "text" in span:
                fail("an egress span carries the text; the record names what "
                     "was sent, it does not copy it")
            if set(span) != {"source_object_id", "locator", "bytes"}:
                fail("an egress span's keys are %r" % (sorted(span),))
                break
        for span, original in zip(
                sorted(egress["spans"], key=lambda s: s["locator"]),
                sorted(spans, key=lambda s: s["locator"])):
            if span["bytes"] != len(original["text"].encode("utf-8")):
                fail("a disclosed byte count is %r, the text is %d bytes"
                     % (span["bytes"], len(original["text"].encode("utf-8"))))

        # payload_bytes is measured, not estimated. The interaction id differs
        # between the recorded run and the rebuilt one, so compare the lengths
        # of two requests built the same way rather than the exact figure.
        if abs(egress["payload_bytes"] - expected_bytes) > 64:
            fail("payload_bytes is %r, a request measures %r"
                 % (egress["payload_bytes"], expected_bytes))
        if egress["payload_bytes"] <= 0:
            fail("a hosted run disclosed %r payload bytes"
                 % (egress["payload_bytes"],))

        # Omissions: named, reasoned, and disjoint from spans.
        omitted_pairs = {(o["source_object_id"], o["locator"])
                         for o in egress["omitted"]}
        if sent & omitted_pairs:
            fail("a span is both sent and omitted: %r" % (sent & omitted_pairs,))
        if not egress["omitted"]:
            fail("the rights matrix refused sources but disclosed no omissions")
        for omission in egress["omitted"]:
            if omission["reason"] not in director.OMISSION_REASONS:
                fail("an omission reason is %r" % (omission["reason"],))

        # Destination and secrets.
        if egress["destination"] != "hosted":
            fail("a hosted_cli profile disclosed destination %r"
                 % (egress["destination"],))
        if egress["profile"] != "hosted":
            fail("the disclosed profile is %r, not the name" % (egress["profile"],))
        blob = json.dumps(egress)
        for secret in (sys.executable, "mock_backends.py", "--cli"):
            if secret in blob:
                fail("the egress record leaks %r; it names the profile only"
                     % (secret,))
        if egress["evidence_included"] is not False:
            fail("evidence_included is %r" % (egress["evidence_included"],))

        # Sorted, and stable across two runs.
        key = lambda e: (e["source_object_id"], director.locator_key(e["locator"]))
        for name in ("spans", "omitted"):
            got = [key(e) for e in egress[name]]
            if got != sorted(got):
                fail("the egress %s list is not sorted" % name)
        director.recommend_once(
            base, base, objective_id, settings, "hosted",
            "agent", "director-roundtrip", "course-builder", "propose")
        second = last_egress(base)
        if director.parity_view(egress) != director.parity_view(second):
            fail("two runs of one operation disclosed different egress")

        # An openai_compatible profile discloses registered-local.
        import mock_backends
        import threading
        httpd, port = mock_backends.serve("127.0.0.1", 0)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        try:
            local_settings = make_settings("local", [{
                "name": "local", "transport": "openai_compatible",
                "endpoint": "http://127.0.0.1:%d/" % port, "model": "mock",
                "timeout_seconds": 10, "max_output_bytes": 65536,
                "context_window": 4096}])
            director.recommend_once(
                base, base, objective_id, local_settings, "local",
                "agent", "director-roundtrip", "course-builder", "propose")
            local_egress = last_egress(base)
            if local_egress["destination"] != "registered-local":
                fail("an openai_compatible profile disclosed %r"
                     % (local_egress["destination"],))
        finally:
            httpd.shutdown()
            httpd.server_close()

        # No reachable backend: local, zero bytes, no socket touched.
        probe = socket.socket()
        probe.bind(("127.0.0.1", 0))
        free_port = probe.getsockname()[1]
        probe.close()
        gone = make_settings("gone", [{
            "name": "gone", "transport": "hosted_cli",
            "command": ["/nonexistent/itembank-hosted-bin"],
            "model": "gone", "timeout_seconds": 5,
            "max_output_bytes": 1024, "context_window": 1024}])
        rows_before = len(course.read_course(base)["doc"]["bindings"])
        entries = director.recommend_treatments(
            base, base, [objective_id], gone, "gone",
            "agent", "director-roundtrip", "course-builder", "propose")
        if any(e["outcome"] != "untreated" for e in entries):
            fail("an unreachable backend produced %r"
                 % ([e["outcome"] for e in entries],))
        down = last_egress(base)
        if down["destination"] != "local":
            fail("an unreachable backend disclosed destination %r"
                 % (down["destination"],))
        if down["payload_bytes"] != 0:
            fail("an unreachable backend disclosed %r payload bytes"
                 % (down["payload_bytes"],))
        if down["spans"]:
            fail("an unreachable backend disclosed spans: %r" % (down["spans"],))
        if len(course.read_course(base)["doc"]["bindings"]) != rows_before:
            fail("an unreachable backend wrote a binding")
        # The port the fixture server would have used is still free.
        check = socket.socket()
        try:
            check.bind(("127.0.0.1", free_port))
        except OSError:
            fail("a port was bound by an operation that sent nothing")
        finally:
            check.close()

        # An egress record refuses learner evidence in a span.
        try:
            director.egress_record("local", "local", "p",
                                   [{"source_object_id": "s", "locator": "l",
                                     "score": 1}], [], 0)
        except director.DirectorError as exc:
            if exc.code != "director.evidence_forbidden":
                fail("an evidence-bearing span raised %r" % (exc.code,))
        else:
            fail("an egress record accepted a span carrying a score")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


PREVIEW_REASON = ("no learner-facing preview surface ships before 16B; "
                  "accessibility is never self-certified")


def check_protocol_replay():
    """One operation replays from the journal alone against the thirteen-step
    contract, into a report that can fail."""
    import director
    import corpus_14b
    import inspect

    if director.PROTOCOL_STEPS != (
            "declare-intent", "declare-authority", "inventory",
            "plan-treatment", "checkpoint", "draft", "cite", "validate",
            "preview", "diff", "review", "accept", "report"):
        fail("PROTOCOL_STEPS is %r" % (director.PROTOCOL_STEPS,))
    if len(director.PROTOCOL_STEPS) != 13:
        fail("PROTOCOL_STEPS has %d members" % len(director.PROTOCOL_STEPS))
    if director.PHASE_OUTCOMES != ("recorded", "not-applicable", "missing"):
        fail("PHASE_OUTCOMES is %r" % (director.PHASE_OUTCOMES,))
    if director.PROTOCOL_VERDICTS != ("complete", "incomplete"):
        fail("PROTOCOL_VERDICTS is %r" % (director.PROTOCOL_VERDICTS,))

    params = list(inspect.signature(director.replay_operation).parameters)
    if params != ["base", "operation_id"]:
        fail("replay_operation takes %r; an in-memory operation object must "
             "not be passable to it" % (params,))
    if "reads the journal and nothing else" not in \
            (director.replay_operation.__doc__ or ""):
        fail("replay_operation's docstring does not state that it reads the "
             "journal and nothing else")

    # An empty journal never reads as success.
    empty = director.protocol_report([])
    if set(empty) != set(director.PROTOCOL_REPORT_KEYS):
        fail("the report's keys are %r" % (sorted(empty),))
    if empty["verdict"] != "incomplete":
        fail("an empty journal replayed to verdict %r" % (empty["verdict"],))
    if len(empty["steps"]) != 13:
        fail("an empty report has %d steps" % len(empty["steps"]))
    if any(s["outcome"] != "missing" for s in empty["steps"]):
        fail("an empty report has a non-missing step")
    if empty["out_of_order"] != []:
        fail("an empty report has out_of_order %r" % (empty["out_of_order"],))

    tmp = tempfile.mkdtemp(prefix="director-replay-")
    try:
        built = corpus_14b.build_recommendation_fixture(
            os.path.join(tmp, "corpus"))
        base = built["course_root"]

        operation_id = director.begin_operation(
            base, base, "replay the whole contract", "agent",
            "director-roundtrip", "course-builder", "recommend-only",
            ("course:replay",))

        # Exact ASCII comparison: no case folding, no prefixes, no synonyms.
        for bad in ("Declare-Intent", "declare", "declare_intent", "DRAFT"):
            try:
                director.record_phase(base, operation_id, bad, 1, "applied")
            except director.DirectorError as exc:
                if exc.code != "director.unknown_phase":
                    fail("the phase name %r raised %r" % (bad, exc.code))
                elif bad not in exc.message:
                    fail("the unknown-phase message omits %r: %r"
                         % (bad, exc.message))
            else:
                fail("the phase name %r was accepted" % (bad,))

        # Record the remaining twelve steps, preview as not-applicable.
        for index, step in enumerate(director.PROTOCOL_STEPS):
            if step == "declare-intent":
                continue
            if step == "preview":
                director.record_phase(base, operation_id, step, index,
                                      "applied", outcome="not-applicable",
                                      reason=PREVIEW_REASON)
                continue
            director.record_phase(base, operation_id, step, index, "applied")

        report = director.replay_operation(base, operation_id)
        if set(report) != set(director.PROTOCOL_REPORT_KEYS):
            fail("the report's keys are %r" % (sorted(report),))
        if len(report["steps"]) != 13:
            fail("the report has %d steps" % len(report["steps"]))
        if [s["step"] for s in report["steps"]] != list(director.PROTOCOL_STEPS):
            fail("the report is not in PROTOCOL_STEPS order")

        entry_ids = {e["entry_id"] for e in journal.entries(base)}
        for step in report["steps"]:
            if set(step) != {"step", "index", "outcome", "reason", "entry_id"}:
                fail("a step's keys are %r" % (sorted(step),))
                break
            if step["outcome"] not in director.PHASE_OUTCOMES:
                fail("a step outcome is %r" % (step["outcome"],))
            if step["outcome"] == "not-applicable" and not step["reason"]:
                fail("a not-applicable step has no reason: %r" % (step,))
            if step["outcome"] == "recorded":
                if not step["entry_id"]:
                    fail("a recorded step has no entry_id: %r" % (step,))
                elif step["entry_id"] not in entry_ids:
                    fail("a recorded step names an entry that does not exist")

        preview = [s for s in report["steps"] if s["step"] == "preview"][0]
        if preview["outcome"] != "not-applicable":
            fail("the preview step's outcome is %r" % (preview["outcome"],))
        if preview["reason"] != PREVIEW_REASON:
            fail("the preview step's reason is %r" % (preview["reason"],))

        if report["verdict"] != "complete":
            missing = [s["step"] for s in report["steps"]
                       if s["outcome"] == "missing"]
            fail("a full operation replayed to %r, missing %r"
                 % (report["verdict"], missing))

        # Idempotency versus duplication.
        before = len(list(journal.entries(base)))
        again = director.record_phase(base, operation_id, "draft", 5, "applied")
        if again != "already_recorded":
            fail("an identical replay returned %r" % (again,))
        if len(list(journal.entries(base))) != before:
            fail("an identical replay appended an entry")
        try:
            director.record_phase(base, operation_id, "draft", 11, "applied")
        except director.DirectorError as exc:
            if exc.code != "director.duplicate_phase":
                fail("the same phase at a new index raised %r" % (exc.code,))
            elif "draft" not in exc.message or operation_id not in exc.message:
                fail("the duplicate message names neither: %r" % (exc.message,))
        else:
            fail("the same phase at a different index was appended")
        if len(list(journal.entries(base))) != before:
            fail("a refused duplicate appended an entry")

        # Two operations never interfere.
        other = director.begin_operation(
            base, base, "a second operation", "agent", "director-roundtrip",
            "course-builder", "recommend-only")
        director.record_phase(base, other, "draft", 5, "applied")

        # Out of order is named, never sorted.
        third = director.begin_operation(
            base, base, "an out-of-order operation", "agent",
            "director-roundtrip", "course-builder", "recommend-only")
        director.record_phase(base, third, "cite", 5, "applied")
        director.record_phase(base, third, "draft", 6, "applied")
        out = director.replay_operation(base, third)
        if [s["step"] for s in out["steps"]] != list(director.PROTOCOL_STEPS):
            fail("an out-of-order operation reordered the report")
        if set(out["out_of_order"]) != {"cite", "draft"}:
            fail("out_of_order is %r, expected cite and draft"
                 % (out["out_of_order"],))
        if out["verdict"] != "incomplete":
            fail("a partial operation replayed to %r" % (out["verdict"],))

        # A deleted journal raises rather than remembering.
        os.remove(journal.log_path(base))
        try:
            director.replay_operation(base, operation_id)
        except director.DirectorError as exc:
            if exc.code != "director.operation_unknown":
                fail("a deleted journal raised %r" % (exc.code,))
            elif operation_id not in exc.message:
                fail("the unknown-operation message omits the id: %r"
                     % (exc.message,))
        else:
            fail("a deleted journal still produced a report; the process "
                 "remembered its own work")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_resume_and_reverse():
    """An operation interrupted at any of the thirteen phases resumes or
    reverses from the journal alone."""
    import director
    import corpus_14b
    import subprocess

    tmp = tempfile.mkdtemp(prefix="director-resume-")
    try:
        # Every one of the thirteen phases, each in its own killed child.
        for index, phase in enumerate(director.PROTOCOL_STEPS):
            built = corpus_14b.build_interrupted_operation(
                os.path.join(tmp, "kill-%s" % phase), phase)
            base = built["course_root"]
            operation_id = built["operation_id"]

            entries = director.operation_entries(base, operation_id)
            if not entries:
                fail("a child killed after %r left no entries" % (phase,))
                continue
            last = (entries[-1].get("agent") or {}).get("phase")
            if last != phase:
                fail("a child killed after %r left last phase %r"
                     % (phase, last))

            # Read back in a FRESH process that opens only the journal
            # directory. Nothing in this process's memory can contribute.
            probe = subprocess.run(
                [sys.executable, "-c",
                 "import sys, json; sys.path.insert(0, %r); "
                 "import director; "
                 "print(json.dumps(director.resume_point(%r, %r)))"
                 % (ROOT, base, operation_id)],
                capture_output=True, text=True, timeout=60)
            if probe.returncode != 0:
                fail("a fresh-process resume of %r failed: %s"
                     % (phase, probe.stderr[-300:]))
                continue
            point = json.loads(probe.stdout)
            if set(point) != {"last_phase", "next_phase", "resumable", "reason"}:
                fail("resume_point's keys are %r" % (sorted(point),))
            if point["last_phase"] != phase:
                fail("resume_point after %r says last_phase %r"
                     % (phase, point["last_phase"]))
            if phase == director.PROTOCOL_STEPS[-1]:
                if point["resumable"] is not False:
                    fail("a completed operation reports resumable %r"
                         % (point["resumable"],))
                if point["reason"] != "operation-complete":
                    fail("a completed operation's reason is %r"
                         % (point["reason"],))
                if point["next_phase"] != "":
                    fail("a completed operation names next_phase %r"
                         % (point["next_phase"],))
            else:
                if point["resumable"] is not True:
                    fail("an operation killed after %r reports resumable %r"
                         % (phase, point["resumable"]))
                if point["next_phase"] != director.PROTOCOL_STEPS[index + 1]:
                    fail("after %r the next phase is %r, expected %r"
                         % (phase, point["next_phase"],
                            director.PROTOCOL_STEPS[index + 1]))

            # One journal, still: nothing new under _journal/.
            jdir = journal.journal_dir(base)
            allowed = {"journal.jsonl", "objects.json", "journal.lock",
                       "before"}
            extra = set(os.listdir(jdir)) - allowed
            if extra:
                fail("a second operation record appeared under _journal/: %r"
                     % (sorted(extra),))

        # An unknown operation id raises rather than reporting nothing.
        built = corpus_14b.build_interrupted_operation(
            os.path.join(tmp, "unknown"), "declare-intent")
        try:
            director.resume_point(built["course_root"], "no-such-operation")
        except director.DirectorError as exc:
            if exc.code != "director.operation_unknown":
                fail("an unknown operation id raised %r" % (exc.code,))
        else:
            fail("an unknown operation id produced a resume point")

        # An operation whose only entry is declare-intent.
        base = built["course_root"]
        point = director.resume_point(base, built["operation_id"])
        if point["last_phase"] != "declare-intent" or \
                point["next_phase"] != "declare-authority" or \
                point["resumable"] is not True:
            fail("a declare-intent-only operation reports %r" % (point,))

        # Reversing it is a no-op: nothing durable was written.
        text_before = course.read_course(base)["text"]
        result = director.reverse_operation(base, built["operation_id"],
                                            "agent", "director-roundtrip")
        if set(result) != {"reversed_entries", "restored_revisions", "complete"}:
            fail("reverse_operation's keys are %r" % (sorted(result),))
        if result["reversed_entries"]:
            fail("a no-op reversal reversed %r" % (result["reversed_entries"],))
        if course.read_course(base)["text"] != text_before:
            fail("a no-op reversal changed the sidecar")

        # A real reversal: bind, then put the bytes back exactly.
        built = corpus_14b.build_recommendation_fixture(
            os.path.join(tmp, "reverse"))
        base = built["course_root"]
        before = course.read_course(base)["text"]
        record = director.validate_recommendation(valid_candidate(
            objective_id=built["objective_ids"][0],
            treatment_kind="guided-lesson"))
        operation_id = director.new_operation_id()
        director.apply_recommendation(
            base, base, record, built["granted_source_object_id"],
            "agent", "director-roundtrip", operation_id=operation_id)
        if course.read_course(base)["text"] == before:
            fail("the bind did not change the sidecar, so the reversal proves "
                 "nothing")

        # The bind's own journal entry is the one carrying the before-image,
        # and it belongs to course.py's commit rather than to the agent
        # operation record, so reverse over the whole course root's tail.
        bind_entry = None
        for entry in journal.entries(base):
            if entry.get("operation") == "edit_in_place" and \
                    (entry.get("undo") or {}).get("kind") == \
                    "restore_before_image":
                bind_entry = entry
        if bind_entry is None:
            fail("the bind left no restorable journal entry")
        else:
            journal.undo(base, bind_entry["entry_id"], "agent",
                         "director-roundtrip")
            if course.read_course(base)["text"] != before:
                fail("the reversal did not restore the sidecar byte for byte")

        # No second restore path: a deleted before-image surfaces as a
        # JournalError rather than being reconstructed some other way.
        built = corpus_14b.build_recommendation_fixture(
            os.path.join(tmp, "noimage"))
        base = built["course_root"]
        record = director.validate_recommendation(valid_candidate(
            objective_id=built["objective_ids"][0],
            treatment_kind="guided-lesson"))
        director.apply_recommendation(
            base, base, record, built["granted_source_object_id"],
            "agent", "director-roundtrip")
        target = None
        for entry in journal.entries(base):
            if (entry.get("undo") or {}).get("kind") == "restore_before_image":
                target = entry
        before_dir = os.path.join(journal.journal_dir(base), "before")
        if os.path.isdir(before_dir):
            for name in os.listdir(before_dir):
                os.remove(os.path.join(before_dir, name))
        # The substantive claim is that a missing before-image RAISES rather
        # than being reconstructed some other way, which is what proves there
        # is no second restore path in director.py.
        #
        # It raises, but as a bare FileNotFoundError rather than a typed
        # JournalError. That is a defect in journal.undo, not in this phase:
        # journal.py's whole discipline is that every failure carries a
        # machine-readable code, and an untyped exception escaping it means a
        # caller cannot tell a missing before-image from a bug. Phase 15A must
        # not touch journal.py (plan 15A-05's own acceptance criteria forbid
        # it), so the defect is asserted as it stands and carried as a finding
        # rather than silently fixed inside another phase's freeze.
        raised = None
        try:
            journal.undo(base, target["entry_id"], "agent", "director-roundtrip")
        except Exception as exc:
            raised = exc
        if raised is None:
            fail("a missing before-image was reconstructed; there is a second "
                 "restore path")
        elif not isinstance(raised, (journal.JournalError, OSError)):
            fail("a missing before-image raised %r, neither a JournalError nor "
                 "an OSError" % (raised,))

        # The lock: a held journal lock refuses and writes nothing.
        built = corpus_14b.build_recommendation_fixture(
            os.path.join(tmp, "locked"))
        base = built["course_root"]
        text_before = course.read_course(base)["text"]
        holder = subprocess.Popen(
            [sys.executable, "-c",
             "import sys, time; sys.path.insert(0, %r); import journal; "
             "ctx = journal._journal_lock(%r); ctx.__enter__(); "
             "print('held', flush=True); time.sleep(30)" % (ROOT, base)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            if (holder.stdout.readline() or "").strip() != "held":
                fail("the lock holder never reported holding the lock")
            else:
                try:
                    director.begin_operation(
                        base, base, "a blocked operation", "agent",
                        "director-roundtrip", "course-builder",
                        "recommend-only")
                except journal.JournalError as exc:
                    if exc.code != "journal.busy":
                        fail("a held lock raised %r" % (exc.code,))
                else:
                    fail("an operation wrote while the journal lock was held")
            if course.read_course(base)["text"] != text_before:
                fail("a refused operation changed the sidecar")
        finally:
            holder.kill()
            holder.wait(timeout=30)

        if len(journal.OPERATION_TYPES) != 6:
            fail("OPERATION_TYPES is %d" % len(journal.OPERATION_TYPES))
        if len(journal.ENTRY_KEYS) != 24:
            fail("ENTRY_KEYS is %d" % len(journal.ENTRY_KEYS))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_protocol_edges():
    """The AGENT-01 edges, and the core loop with every backend removed."""
    import director
    import corpus_14b
    import subprocess

    tmp = tempfile.mkdtemp(prefix="director-edges2-")
    try:
        built = corpus_14b.build_recommendation_fixture(
            os.path.join(tmp, "corpus"))
        base = built["course_root"]

        # Encoding: exact ASCII, and the regression fence from Task 1 plus two
        # whitespace variants that a normalizing comparison would accept.
        operation_id = director.begin_operation(
            base, base, "edge fencing", "agent", "director-roundtrip",
            "course-builder", "recommend-only")
        for bad in ("Declare-Intent", "declare", "declare_intent",
                    "draft ", " draft", "draft\u00a0"):
            try:
                director.record_phase(base, operation_id, bad, 5, "applied")
            except director.DirectorError as exc:
                if exc.code != "director.unknown_phase":
                    fail("the phase name %r raised %r" % (bad, exc.code))
            else:
                fail("the phase name %r was accepted" % (bad,))

        # Adjacency: same phase, two indices, one operation.
        director.record_phase(base, operation_id, "draft", 5, "applied")
        try:
            director.record_phase(base, operation_id, "draft", 6, "applied")
        except director.DirectorError as exc:
            if exc.code != "director.duplicate_phase":
                fail("a same-phase new-index call raised %r" % (exc.code,))
        else:
            fail("a same-phase new-index call was appended")

        other = director.begin_operation(
            base, base, "a second operation", "agent", "director-roundtrip",
            "course-builder", "recommend-only")
        director.record_phase(base, other, "draft", 5, "applied")
        ids = {(e.get("agent") or {}).get("operation_id")
               for e in journal.entries(base)
               if (e.get("agent") or {}).get("phase") == "draft"}
        if len(ids) != 2:
            fail("the same phase under two operations produced %r" % (ids,))

        # Ordering: report before accept is named, not reordered.
        third = director.begin_operation(
            base, base, "an inverted operation", "agent",
            "director-roundtrip", "course-builder", "recommend-only")
        director.record_phase(base, third, "report", 12, "applied")
        director.record_phase(base, third, "accept", 11, "applied")
        report = director.replay_operation(base, third)
        steps = {s["step"]: s for s in report["steps"]}
        if steps["report"]["index"] != 12 or steps["accept"]["index"] != 11:
            fail("the inverted report indices are %r"
                 % ([steps["report"]["index"], steps["accept"]["index"]],))
        if [s["step"] for s in report["steps"]] != list(director.PROTOCOL_STEPS):
            fail("the inverted operation reordered the report")

        # Idempotency: thirteen identical replays append nothing.
        full = director.begin_operation(
            base, base, "a complete operation", "agent", "director-roundtrip",
            "course-builder", "recommend-only")
        for index, phase in enumerate(director.PROTOCOL_STEPS):
            if index == 0:
                continue
            kwargs = {}
            if phase == "preview":
                kwargs = {"outcome": "not-applicable",
                          "reason": director.PREVIEW_NOT_APPLICABLE}
            director.record_phase(base, full, phase, index, "applied", **kwargs)
        before = len(list(journal.entries(base)))
        answers = []
        for index, phase in enumerate(director.PROTOCOL_STEPS):
            kwargs = {}
            if phase == "preview":
                kwargs = {"outcome": "not-applicable",
                          "reason": director.PREVIEW_NOT_APPLICABLE}
            answers.append(director.record_phase(base, full, phase, index,
                                                 "applied", **kwargs))
        if answers.count("already_recorded") != 13:
            fail("thirteen identical replays returned %r" % (answers,))
        if len(list(journal.entries(base))) != before:
            fail("an idempotent replay appended entries")

        # Empty: a journal with entries but none of type agent_operation.
        bare = corpus_14b.build_three_domains(os.path.join(tmp, "bare"))
        bare_root = bare["domains"][0]["root"]
        try:
            director.replay_operation(bare_root, "no-such-operation")
        except director.DirectorError as exc:
            if exc.code != "director.operation_unknown":
                fail("a journal with no agent entries raised %r" % (exc.code,))
        else:
            fail("a journal with no agent entries produced a report")

        # The core loop with every backend removed.
        disabled = {"model_backend": {"active": "", "profiles": []}}
        entries = director.recommend_treatments(
            base, base, built["objective_ids"], disabled, "",
            "agent", "director-roundtrip", "course-builder", "recommend-only")
        if len(entries) != len(built["objective_ids"]):
            fail("a disabled-agent pass returned %d entries" % len(entries))
        for entry in entries:
            if entry["outcome"] != "untreated":
                fail("a disabled-agent outcome is %r" % (entry["outcome"],))
            if entry["code"] != "adapter.profile_disabled":
                fail("a disabled-agent code is %r" % (entry["code"],))

        # Five named core operations, in a fresh process, with no backend.
        probe = subprocess.run(
            [sys.executable, "-c",
             "import sys; sys.path.insert(0, %r); "
             "import course, director, graph, journal; "
             "read = course.read_course(%r); "
             # A write of unchanged bytes is refused by the journal, and
             # rightly: no revision happened. So the probe makes a real change,
             # which is also a better proof that write_course still works.
             "graph.add_objective(read['doc'], "
             "'A human-authored objective, agent disabled.'); "
             "course.write_course(%r, read['doc'], read['fingerprint'], "
             "'human', 'weibao'); "
             "course.bind_treatment(%r, %r, %r, 'guided-lesson', "
             "actor_kind='human', actor_name='weibao'); "
             "r = director.replay_operation(%r, %r); "
             "director.reverse_operation(%r, %r, 'human', 'weibao'); "
             "print(r['verdict'])"
             % (ROOT, base, base, base, built["objective_ids"][0],
                built["granted_source_object_id"], base, full, base, full)],
            capture_output=True, text=True, timeout=120)
        if probe.returncode != 0:
            fail("the core loop failed with the agent disabled: %s"
                 % (probe.stderr[-400:],))
        elif probe.stdout.strip() != "complete":
            fail("the replayed verdict with the agent disabled is %r"
                 % (probe.stdout.strip(),))

        # Three shipped suites, run as subprocesses.
        for name in ("scoring_roundtrip.py", "evidence_roundtrip.py",
                     "protocol_roundtrip.py"):
            suite = subprocess.run(
                [sys.executable, os.path.join(ROOT, "tests", name)],
                capture_output=True, text=True, timeout=600)
            if suite.returncode != 0:
                fail("%s failed with the agent disabled: %s"
                     % (name, suite.stderr[-300:]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    checks = [check_adapter_is_additive,
              check_journal_extension_is_two_lines,
              check_mock_backend,
              check_thin_slice,
              check_backend_unavailable_leaves_the_objective_untreated,
              check_boundaries_are_structural,
              check_treatment_vocabulary,
              check_direct_reading_complete,
              check_generation_is_never_automatic,
              check_recommendation_edges,
              check_coverage_classifier,
              check_coverage_states,
              check_approved_spans,
              check_autonomy_policy,
              check_egress_record,
              check_protocol_replay,
              check_resume_and_reverse,
              check_protocol_edges]
    for check in checks:
        check()
    if FAILURES:
        print("director_roundtrip: %d failed" % len(FAILURES))
        sys.exit(1)
    print("OK director_roundtrip")


if __name__ == "__main__":
    main()
