"""Internal runtime component; public access goes through runtime."""
import fractions, json, re


def _validate_interaction_contract(config):
    """The public_item boundary gate for a check item's interaction contract:
    the envelope and the renderer_config must carry exactly the declared keys
    with the declared value kinds, and the whole config must serialize as JSON
    data -- no callables, no case material, no key. A config built from a
    parsed question can never fail this; it exists so a future caller cannot
    slip something through the boundary unnoticed."""
    import runtime
    if not isinstance(config, dict):
        raise ValueError("interaction contract must be an object")
    for key in ("version", "type", "renderer_config", "response_schema"):
        if key not in config:
            raise ValueError("interaction contract missing %r" % key)
    if config["type"] != "check":
        raise ValueError("interaction contract type must be 'check'")
    rc = config["renderer_config"]
    if not isinstance(rc, dict):
        raise ValueError("renderer_config must be an object")
    for key in ("language", "starter_source", "hidden_case_count"):
        if key not in rc:
            raise ValueError("renderer_config missing %r" % key)
    if not isinstance(rc["hidden_case_count"], int)             or isinstance(rc["hidden_case_count"], bool):
        raise ValueError("hidden_case_count must be an integer")
    if not isinstance(config["response_schema"], dict):
        raise ValueError("response_schema must be an object")
    json.dumps(config)      # JSON data only: a callable or a non-JSON value dies here


VISUAL_ACTIONS = ("place_point", "move_point",
                  "select_numberline_point", "set_interval",
                  "select_hotspot", "place_timeline_event",
                  "move_timeline_event", "connect_diagram",
                  "place_trace_point", "move_trace_point")


_VISUAL_SCENE_MEMBERS = {
    "plot": frozenset({"version", "axes", "initial", "actions",
                       "accessibility"}),
    "numberline": frozenset({"version", "axis", "initial", "actions",
                             "accessibility"}),
    "hotspot": frozenset({"version", "plane", "regions", "initial",
                          "actions", "accessibility"}),
    "timeline": frozenset({"version", "axis", "events", "initial",
                           "actions", "accessibility"}),
    "diagram": frozenset({"version", "plane", "nodes", "initial",
                          "actions", "accessibility"}),
    "trace": frozenset({"version", "axes", "point_count", "initial",
                        "actions", "accessibility"}),
}


_VISUAL_KIND_BY_INTERACTION = {
    "plot": ("point",),
    "numberline": ("numberline_point", "interval"),
    "hotspot": ("hotspot",),
    "timeline": ("timeline_event",),
    "diagram": ("diagram_connection",),
    "trace": ("trace_path",),
}


_VISUAL_SCORING_MEMBERS = frozenset({"kind", "accepted", "tolerance",
                                     "partial_credit", "feedback"})


_VISUAL_EXEC_RE = re.compile(
    r"<\s*script|javascript:|eval\s*\(|new\s+Function|setTimeout|setInterval|"
    r"document\.|window\.|innerHTML\s*=|alert\s*\(|prompt\s*\(|confirm\s*\(|"
    r"location\.|localStorage|sessionStorage|fetch\s*\(|XMLHttpRequest|"
    r"(?:^|[^A-Za-z0-9])on(?:click|load|mouse|pointer|touch|key|input|change|"
    r"focus|blur|submit|error|dblclick|wheel|unload|resize|scroll|over|out)"
    r"\b", re.I)


def _reject_visual_exec(member, where):
    """Recursively scan one authored JSON member and reject any string or key
    carrying a script-bearing token, so no bank content can become browser
    code (T-06.1-03). Raises ValueError with the offending path."""
    import runtime
    if isinstance(member, str):
        if runtime._VISUAL_EXEC_RE.search(member):
            raise ValueError("visual %s carries a script-bearing value" % where)
    elif isinstance(member, dict):
        for key, value in member.items():
            if runtime._VISUAL_EXEC_RE.search(str(key)):
                raise ValueError("visual %s carries a script-bearing key %r"
                                 % (where, key))
            runtime._reject_visual_exec(value, where)
    elif isinstance(member, list):
        for item in member:
            runtime._reject_visual_exec(item, where)


def _visual_response_schema(kind):
    import runtime
    if kind == "point":
        return {"type": "object", "kind": "point",
                "fields": {"x": "scalar", "y": "scalar"}}
    if kind == "numberline_point":
        return {"type": "object", "kind": "numberline_point",
                "fields": {"value": "scalar"}}
    if kind == "interval":
        return {"type": "object", "kind": "interval",
                "fields": {"start": "scalar", "end": "scalar",
                           "start_closed": "boolean", "end_closed": "boolean"}}
    if kind == "hotspot":
        return {"type": "object", "kind": "hotspot",
                "fields": {"region": "identifier"}}
    if kind == "timeline_event":
        return {"type": "object", "kind": "timeline_event",
                "fields": {"event": "identifier", "value": "scalar"}}
    if kind == "diagram_connection":
        return {"type": "object", "kind": "diagram_connection",
                "fields": {"from": "identifier", "to": "identifier"}}
    return {"type": "object", "kind": "trace_path",
            "fields": {"points": "point_list"}}


def _visual_interaction_contract(q):
    """Build the key-free public interaction contract for a visual item,
    validating the declarative scene and scoring envelope first.

    The contract carries exactly `version`, `type`, `interaction`,
    `renderer_config` (scene, initial state, actions, accessibility) and
    `response_schema` -- never accepted states, tolerance, partial_credit,
    reveal content, or any scoring authority (D-02/D-03). Raises ValueError
    on unknown members, executable/script-bearing content, an invalid scene,
    or a malformed scoring envelope, so a bad bank fails before a renderer
    sees it.
    """
    import runtime
    interaction = q.get("interaction")
    if interaction not in runtime.VISUAL_INTERACTIONS:
        raise ValueError(
            "visual item %s: unknown INTERACTION %r (protocol %d supports %s)"
            % (q["id"], interaction, runtime.VISUAL_PROTOCOL_VERSION,
               ", ".join(runtime.VISUAL_INTERACTIONS)))
    scene = q.get("visual")
    scoring = q.get("scoring")
    if not isinstance(scene, dict) or not isinstance(scoring, dict):
        raise ValueError("visual item %s: VISUAL and SCORING must be JSON "
                         "objects" % q["id"])
    unknown = set(scene) - runtime._VISUAL_SCENE_MEMBERS[interaction]
    if unknown:
        raise ValueError("visual item %s: unknown VISUAL member(s) %s"
                         % (q["id"], ", ".join(sorted(unknown))))
    unknown = set(scoring) - runtime._VISUAL_SCORING_MEMBERS
    if unknown:
        raise ValueError("visual item %s: unknown SCORING member(s) %s"
                         % (q["id"], ", ".join(sorted(unknown))))
    runtime._reject_visual_exec(scene, "VISUAL")
    runtime._reject_visual_exec(scoring, "SCORING")

    kind = scoring.get("kind")
    if kind not in runtime.VISUAL_KINDS:
        raise ValueError("visual item %s: unknown SCORING kind %r"
                         % (q["id"], kind))
    if kind not in runtime._VISUAL_KIND_BY_INTERACTION.get(interaction, ()):
        raise ValueError("visual item %s: SCORING kind %r does not match "
                         "INTERACTION %r" % (q["id"], kind, interaction))
    if scoring.get("partial_credit") is not False:
        raise ValueError("visual item %s: protocol %d is dichotomous; "
                         "partial_credit must be false"
                         % (q["id"], runtime.VISUAL_PROTOCOL_VERSION))
    scene_data = runtime._visual_scene(q, interaction)
    if scene_data is None:
        raise ValueError("visual item %s: scene geometry is invalid"
                         % q["id"])

    actions = scene.get("actions")
    if not isinstance(actions, list) or not actions \
            or any(a not in runtime.VISUAL_ACTIONS for a in actions):
        raise ValueError("visual item %s: actions must be a non-empty subset "
                         "of %s" % (q["id"], ", ".join(runtime.VISUAL_ACTIONS)))
    accessibility = scene.get("accessibility")
    if not isinstance(accessibility, dict) \
            or not str(accessibility.get("description") or "").strip():
        raise ValueError("visual item %s: accessibility.description is "
                         "required (D-07)" % q["id"])

    # The accepted states and tolerance are validated here (server-side) so a
    # malformed scoring envelope fails before any learner sees the item; they
    # are never emitted into the public contract.
    accepted = scoring.get("accepted")
    if not isinstance(accepted, list) or not accepted:
        raise ValueError("visual item %s: SCORING.accepted must be a "
                         "non-empty list" % q["id"])
    for raw in accepted:
        state = runtime._canonical_accepted_state(q, raw)
        if state is None or not runtime.visual_state_in_domain(q, state):
            raise ValueError("visual item %s: an accepted state is invalid "
                             "or out of domain" % q["id"])
    tolerance = scoring.get("tolerance") or {}
    if not isinstance(tolerance, dict):
        raise ValueError("visual item %s: SCORING.tolerance must be an "
                         "object" % q["id"])
    for key, raw in tolerance.items():
        if runtime.canonical_scalar(raw) is None or fractions.Fraction(raw) < 0:
            raise ValueError("visual item %s: tolerance %r is not a "
                             "non-negative SCALAR" % (q["id"], key))
    if kind in ("hotspot", "diagram_connection") and any(
            fractions.Fraction(runtime.canonical_scalar(v)) > 0
            for v in tolerance.values()):
        raise ValueError("visual item %s: %s scoring is exact-id; tolerance "
                         "must be zero" % (q["id"], kind))

    renderer_config = {"actions": list(actions),
                       "accessibility": {"description":
                                         str(accessibility["description"])}}
    if interaction == "plot":
        renderer_config["axes"] = {"x": scene_data["x"], "y": scene_data["y"]}
        renderer_config["initial"] = scene.get("initial") or {"points": []}
    elif interaction == "numberline":
        renderer_config["axis"] = scene_data["axis"]
        renderer_config["initial"] = scene.get("initial") or {
            "points": [], "interval": None}
    elif interaction == "hotspot":
        renderer_config["plane"] = scene_data["plane"]
        renderer_config["regions"] = [
            {"id": rid, "label": r["label"], "shape": r["shape"],
             "coords": r["coords"]}
            for rid, r in scene_data["regions"].items()]
        renderer_config["initial"] = scene.get("initial") or {"region": None}
    elif interaction == "timeline":
        renderer_config["axis"] = scene_data["axis"]
        renderer_config["events"] = [
            {"id": eid, "label": entry["label"]}
            for eid, entry in scene_data["events"].items()]
        renderer_config["initial"] = scene.get("initial") or {"placements": []}
    elif interaction == "diagram":
        renderer_config["plane"] = scene_data["plane"]
        renderer_config["nodes"] = [
            {"id": nid, "label": n["label"], "x": n["x"], "y": n["y"]}
            for nid, n in scene_data["nodes"].items()]
        renderer_config["initial"] = scene.get("initial") or {
            "connections": []}
    else:  # trace
        renderer_config["axes"] = {"x": scene_data["axes"]["x"],
                                    "y": scene_data["axes"]["y"]}
        renderer_config["point_count"] = scene_data["point_count"]
        renderer_config["initial"] = scene.get("initial") or {"points": []}
    return {"version": runtime.VISUAL_PROTOCOL_VERSION, "type": "visual",
            "interaction": interaction, "renderer_config": renderer_config,
            "response_schema": runtime._visual_response_schema(kind)}
