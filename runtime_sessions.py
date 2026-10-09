"""Internal runtime component; public access goes through runtime."""
import hashlib, json, os, sys


SESSION_VERSION = 4


def session_path(path):
    import runtime
    return os.path.abspath(path)


SESSION_UPGRADES = {
    1: lambda data: dict(data, teaching_state={}),
    # v2-to-v3 (Phase 9): a nullable subject-profile slot only. The upgrade
    # never inspects a bank or settings; the first action on a legacy session
    # resolves and persists the snapshot once (D-04).
    2: lambda data: dict(data, subject_profile=None),
    3: lambda data: dict(data, staged_cases=[]),
}


def upgrade_session(data):
    """Carry a session dict forward to SESSION_VERSION, one registered step
    at a time.

    A non-integer `schema_version` and a version above what this build
    understands each exit with a named error rather than guessing at a
    shape. This is the migration path `.planning/codebase/CONCERNS.md`
    flagged as missing: a version stamp with no way to move forward from it.
    """
    import runtime
    version = data.get("schema_version")
    if not isinstance(version, int):
        sys.exit("session has no valid schema_version (got %r)" % (version,))
    while version < runtime.SESSION_VERSION:
        upgrade = runtime.SESSION_UPGRADES.get(version)
        if upgrade is None:
            sys.exit("no upgrade path from session schema %d to %d" %
                     (version, runtime.SESSION_VERSION))
        data = upgrade(data)
        version += 1
        data["schema_version"] = version
    if version > runtime.SESSION_VERSION:
        sys.exit("session schema %d is newer than this build understands (%d); "
                 "upgrade itembank" % (version, runtime.SESSION_VERSION))
    return data


def read_session(path):
    import runtime
    try:
        with open(runtime.session_path(path), encoding="utf-8") as stream:
            data = json.load(stream)
    except (OSError, ValueError) as exc:
        sys.exit("cannot read session %s: %s" % (path, exc))
    return runtime.upgrade_session(data)


def write_session(path, data):
    """Write one session atomically, through a temp name no other writer can
    claim.

    The temp name carries a per-write nonce because the daemon is threaded and
    two requests can write one session file at the same moment. A shared
    `<target>.tmp` made that collide rather than serialize: the first
    `os.replace` consumed the temp file, and the second raised
    `FileNotFoundError` on a path it had just written. That surfaced as an
    intermittent `400 Bad Request` out of `handle_quiz_get`, reproduced on
    2026-08-30 at twelve concurrent requests. Last-writer-wins on the content
    is unchanged and still the caller's problem to avoid; what is fixed is one
    writer destroying another's in-flight temp file.

    The suffix stays `.tmp` so every leftover sweep that looks for
    `endswith(".tmp")` still sees these.
    """
    import runtime
    target = runtime.session_path(path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    tmp = "%s.%s.tmp" % (target, os.urandom(4).hex())
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        os.replace(tmp, target)
    except BaseException:
        # A failed write leaves the old session valid; it may not also leave
        # a half-written temp file behind for a leftover sweep to find.
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise


def staged_case(data, position=None):
    """Resolve a case from the one canonical sitting cursor."""
    import runtime
    position = data.get("cursor", 0) if position is None else position
    return next((case for case in data.get("staged_cases", [])
                 if position in case["positions"]), None)


def staged_token(data, case):
    import runtime
    value = [data["session_id"], case["case_revision"],
             case["bank_fingerprint"], data["cursor"], len(data["responses"])]
    return hashlib.sha256(json.dumps(value).encode()).hexdigest()


def staged_activity(data):
    import runtime
    case = runtime.staged_case(data)
    if case is None or data.get("status") != "active":
        return None
    stage = case["positions"].index(data["cursor"])
    result = {"activity_id": case["activity_id"],
              "case_revision": case["case_revision"],
              "stimulus": case["stimulus"], "stage": case["order"][stage],
              "child_id": case["children"][stage],
              "submission_token": runtime.staged_token(data, case)}
    if stage:
        result["committed_answer"] = next(row["answer"] for row in data["responses"]
            if row["item_id"] == case["item_refs"][0])
    return result


def staged_binding(bank_path, qs, indices):
    """Bind declarations to the exact accepted bytes and selected positions."""
    import runtime
    with open(bank_path, "rb") as stream:
        fingerprint = "sha256:" + hashlib.sha256(stream.read()).hexdigest()
    selected = {qs[index].get("item_id"): pos for pos, index in enumerate(indices)}
    bound = []
    for declaration in getattr(qs, "staged_cases", []):
        children = declaration["children"]
        present = [child in selected for child in children]
        if any(present) and not all(present):
            sys.exit("staged case must retain both children; increase count or exclude the whole case")
        if all(present):
            positions = [selected[child] for child in children]
            if positions[1] != positions[0] + 1:
                sys.exit("staged case requires adjacent answer then reason; remove focus or change selection")
            revision = "sha256:" + hashlib.sha256(json.dumps(
                declaration, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            bound.append(dict(declaration, case_revision=revision,
                              bank_fingerprint=fingerprint, positions=positions,
                              item_refs=[qs[indices[pos]]["id"] for pos in positions]))
    return bound


def validate_staged_binding(data, qs):
    import runtime
    if data.get("staged_binding_required") and not data.get("staged_cases"):
        sys.exit("staged binding missing; restore the accepted session before resuming")
    if not data.get("staged_cases"):
        return
    current = runtime.staged_binding(data["bank"], qs, data["items"])
    if current != data["staged_cases"]:
        sys.exit("staged binding changed or unavailable; restore the accepted bank before resuming")


def session_view(data, qs):
    import runtime
    runtime.validate_staged_binding(data, qs)
    selected = data["items"]
    cursor = data["cursor"]
    view = {"schema_version": runtime.SESSION_VERSION, "session_id": data["session_id"],
            "status": data["status"], "mode": data["mode"],
            "objective": data.get("objective", ""), "position": cursor,
            "total": len(selected), "responses": len(data["responses"])}
    if data.get("timing"):
        view["timing"] = dict(data["timing"])
    # Phase 9 (D-04): the persisted subject/profile snapshot is part of the
    # public view. Legacy sessions whose null slot is not filled yet report
    # an empty subject id and no profile metadata.
    sp = data.get("subject_profile")
    if isinstance(sp, dict):
        prof = sp.get("profile") or {}
        view["subject_id"] = sp.get("subject_id", "")
        view["subject_profile"] = {
            "id": prof.get("id", ""),
            "version": prof.get("version"),
            "registry_version": sp.get("registry_version"),
            "profile_version": sp.get("profile_version"),
            "lesson": prof.get("lesson"),
            "allowed_item_types": prof.get("allowed_item_types"),
            "verifier": prof.get("verifier"),
            "unsupported_capabilities": sp.get("unsupported_capabilities", []),
        }
    else:
        view["subject_id"] = ""
    if data["status"] == "active" and cursor < len(selected):
        view["item"] = runtime.public_item(qs[selected[cursor]], data.get("seed", 0) + cursor)
        activity = runtime.staged_activity(data)
        if activity is not None:
            view["activity"] = activity
    else:
        view["summary"] = runtime.session_summary(data)
    if data.get("mode") not in ("exam", "diagnostic"):
        for case in data.get("staged_cases", []):
            if cursor == case["positions"][-1] + 1:
                feedback = runtime.staged_feedback(data, qs, case)
                if feedback is not None:
                    view["activity_feedback"] = feedback
    return view
