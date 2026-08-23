#!/usr/bin/env python3
"""The Agent area's run-propose-accept machine (plan 17A-07).

One bounded state machine joins the two halves that already shipped:

- a skill run reaches a model only through ``model_adapter.invoke``, the
  single typed boundary. This module opens no socket of its own and adds
  no transport;
- an accepted draft becomes real only through ``journal.commit_operation``,
  the single compare-and-swap writer. This module writes nothing else, and
  the undo path is the prior revision that writer already records.

Four states, no others: ``idle``, ``running``, ``proposed``, ``settled``.
Every public function takes and returns plain state dicts so the page can
render each one without JavaScript.

This module never scores, never marks, never touches keyed assessment
content, and never decides how much of anything to disclose. It proposes
file drafts against a fingerprint, and the learner accepts or rejects.

A run names its write target from the settings document (``agent_runs``
keyed by skill id), never from the model: the model supplies text for a
file the configuration already named, so a stray answer cannot choose
what gets overwritten.
"""
import difflib
import os
import uuid

import identity
import journal
import model_adapter


# The whole machine. Anything else a caller sees is a bug.
STATES = ("idle", "running", "proposed", "settled")

# A proposal shows at most this many unified-diff lines. The rest are
# counted in ``diff.withheld`` so the cap is visible, never silent.
DIFF_MAX_LINES = 60

# Autonomy levels that may turn an accepted draft into a journal write.
# Every other value, including a missing setting, reads as report_only:
# restrictive by default, because the shipped default IS report_only.
AUTONOMY_MAY_WRITE = ("draft_and_approve", "audit_draft_lint_fix_commit")

# One named next action per typed unavailable code in
# model_adapter.ADAPTER_CODES. A missing entry is a test failure by
# design, so a new adapter code cannot ship with no copy on the page;
# the import-time check below makes it loud even before the suite runs.
NEXT_ACTIONS = {
    "adapter.profile_disabled":
        "No backend is active. Choose one in Settings, Model, then start "
        "the skill again. Studying, scoring and authored hints are "
        "unaffected and keep working right now.",
    "adapter.profile_invalid":
        "The backend profile has a field this transport does not take "
        "(for example base_url instead of endpoint). Fix the profile in "
        "Settings, Model, then start again.",
    "adapter.profile_unknown":
        "The active backend name no longer matches a configured profile. "
        "Pick the backend again in Settings, Model.",
    "adapter.unreachable":
        "Nothing answered at the endpoint. Start the model server shown "
        "in Settings, Model, then start the skill again. Nothing was "
        "written.",
    "adapter.timeout":
        "The server did not answer in time. Start the skill again, or "
        "raise timeout_seconds on the profile. Nothing was written.",
    "adapter.malformed_response":
        "The endpoint answered with something that is not JSON. Check "
        "that the endpoint URL points at the chat completions address.",
    "adapter.http_error":
        "The endpoint returned an HTTP error. Check the endpoint URL and "
        "any access key the server requires.",
    "adapter.executable_missing":
        "The command this backend runs was not found on this machine. "
        "Install it, or fix the command in Settings, Model.",
    "adapter.subprocess_error":
        "The backend command failed while running. Run it once in a "
        "terminal to see why, then start the skill again.",
    "adapter.provider_refused":
        "The backend refused the request. Check its logs; nothing was "
        "written here.",
    "adapter.request_invalid":
        "itembank built a request the model boundary rejected. This is a "
        "bug in itembank, not something you did. Nothing was written.",
    "adapter.output_cap_exceeded":
        "The answer was longer than the profile allows. Raise "
        "max_output_bytes in Settings, Model, or ask for a smaller "
        "draft.",
    "adapter.transport_unknown":
        "The profile names a transport this build does not ship. Choose "
        "a listed transport in Settings, Model.",
    "adapter.internal_error":
        "Something failed unexpectedly inside the model boundary. "
        "Nothing was written. Start the skill again.",
}

for _code in model_adapter.ADAPTER_CODES:
    if _code not in NEXT_ACTIONS:
        raise RuntimeError(
            "adapter code %r shipped with no next-action copy; add it to "
            "surfaces.agent_operation.NEXT_ACTIONS" % (_code,))

# What each state means, in the page's words. Rendered verbatim by the
# Agent tab so the screen explains the machine instead of hiding it.
STATE_COPY = {
    "idle":
        "Nothing is running. Pick a skill below to start one.",
    "running":
        "The skill is at the model boundary. It comes back as a proposal "
        "or as a typed unavailable, never as a half-written file.",
    "proposed":
        "The draft is shown as a bounded diff against the file as it "
        "stands, with its citations. Accept writes once through the "
        "journal; Reject writes nothing.",
    "settled":
        "The run is over: either one journalled change you can undo, or "
        "a typed reason and the next action to take.",
}


def idle():
    """The resting state, rendered before any skill runs."""
    return {"state": "idle", "skill": None, "note": STATE_COPY["idle"]}


def _settled(iid, skill, code, reason, **extra):
    state = {"state": "settled", "ok": False, "skill": skill,
             "interaction_id": iid, "code": code, "reason": reason,
             "entry_id": None, "conflict": False}
    state.update(extra)
    return state


def _run_spec(skill, settings):
    """The write target for this skill, taken from the settings document
    and never from the model. Returns None when the skill has none."""
    runs = (settings or {}).get("agent_runs") or {}
    spec = runs.get(skill)
    if not isinstance(spec, dict) or not spec.get("target"):
        return None
    kind = spec.get("kind") or "bank"
    if kind not in identity.OBJECT_KINDS:
        return None
    return {"target": str(spec["target"]), "kind": kind}


def _bounded_diff(rel, before_raw, draft):
    """A capped unified diff of the draft against the current bytes. The
    withheld count travels with the shown lines, so a truncation is a
    stated fact rather than a silent one."""
    before = before_raw.decode("utf-8", errors="replace").splitlines()
    after = draft.splitlines()
    full = list(difflib.unified_diff(
        before, after,
        fromfile="current/%s" % rel, tofile="draft/%s" % rel,
        lineterm=""))
    shown = full[:DIFF_MAX_LINES]
    return {"lines": shown, "shown": len(shown), "total": len(full),
            "withheld": max(0, len(full) - len(shown))}


def _author_payload(skill, target):
    """The bounded author request the adapter schema requires: the public
    format contract, the bounded request (here, which configured skill
    and file to draft for), the attempt number, and empty findings. No
    repository contents ride along."""
    import model
    return {
        "schema_version": 1,
        "contract": model.SPEC,
        "request": {"skill": skill, "target": target},
        "attempt": 1,
        "findings": [],
    }


def start(skill, settings, base):
    """Run one skill: build the bounded request, invoke the boundary, and
    land in exactly one of two places. An ok result becomes a ``proposed``
    state carrying the draft, its citations, and a bounded diff against
    the current bytes of the target file. Any unavailable result becomes
    a ``settled`` state carrying the typed code, the adapter's message,
    and the next action named in NEXT_ACTIONS."""
    iid = "agent-%s-%s" % (skill, uuid.uuid4().hex[:12])
    base = os.path.abspath(base)

    spec = _run_spec(skill, settings)
    if spec is None:
        return _settled(
            iid, skill, "agent.no_run_target",
            "The skill '%s' has no file to draft into. Add an "
            "agent_runs.%s.target entry to itembank.json naming the file "
            "inside the course directory this skill should draft."
            % (skill, skill))

    request = model_adapter.request_from_operation(
        "author", iid, "",
        author_request=_author_payload(skill, spec["target"]))
    result = model_adapter.invoke(request, settings or {})

    if result.get("status") != "ok":
        error = result.get("error") or {}
        code = error.get("code")
        # Indexing directly, not .get(): a missing entry is a failure to
        # fix in the map above, never a silent fallback.
        return _settled(iid, skill, code, error.get("message"),
                        next_action=NEXT_ACTIONS[code],
                        message=error.get("message"))

    candidate = result.get("candidate")
    if not isinstance(candidate, dict) \
            or not isinstance(candidate.get("draft"), str) \
            or not isinstance(candidate.get("citations"), list):
        return _settled(
            iid, skill, "agent.candidate_invalid",
            "The backend answered, but not with a draft this page can "
            "propose (it needs JSON with a draft string and a citations "
            "list). Check the endpoint serves this skill's output "
            "format.")

    draft = candidate["draft"]
    citations = [str(c) for c in candidate["citations"]]
    target_path = os.path.join(base, spec["target"])
    raw = None
    if os.path.exists(target_path):
        with open(target_path, "rb") as fh:
            raw = fh.read()

    return {
        "state": "proposed",
        "skill": skill,
        "base": base,
        "interaction_id": iid,
        "target": spec["target"],
        "kind": spec["kind"],
        "draft": draft,
        "citations": citations,
        "expected_fingerprint":
            identity.object_fingerprint(raw, spec["kind"])
            if raw is not None else None,
        "diff": _bounded_diff(spec["target"], raw or b"", draft),
        "provider": result.get("provider"),
    }


def accept(state, settings):
    """Turn a proposal into exactly one journalled change, or refuse.

    - On an already-settled state (or any non-proposal) it returns the
      same state unchanged and records nothing, so a double submit
      cannot write twice: the guard is here, not in the page.
    - Under report_only autonomy it refuses visibly: a settled state
      whose reason names the setting and where to change it.
    - On a fingerprint that no longer matches it reports the conflict in
      words a learner can act on; journal.commit_operation already
      refused the overwrite, this only says so.

    Exactly one journal operation per accepted proposal: prepared and
    applied entries for one change, never two changes.
    """
    if not isinstance(state, dict) or state.get("state") != "proposed":
        return state

    skill = state.get("skill") or ""
    iid = state.get("interaction_id")
    autonomy = (settings or {}).get("auditor_autonomy")
    if autonomy not in AUTONOMY_MAY_WRITE:
        shown = autonomy if autonomy else "unset, which reads as"
        return _settled(
            iid, skill, "agent.report_only",
            "auditor_autonomy is %s 'report_only', so drafts are shown "
            "but never written. To let an accepted draft become a "
            "revision, set auditor_autonomy to 'draft_and_approve' in "
            "itembank.json." % shown,
            refusal="report_only")

    base = state["base"]
    rel = state["target"]
    kind = state["kind"]

    existing = None
    for row in (journal.read_registry(base) or {}).values():
        if isinstance(row, dict) and row.get("path") == rel:
            existing = row
            break
    object_id = existing["object_id"] if existing \
        else identity.new_object_id()
    operation = "edit_in_place" if existing else "mint"

    try:
        record = journal.commit_operation(
            base, object_id, kind, rel, operation,
            state["draft"].encode("utf-8"),
            expected_fingerprint=state.get("expected_fingerprint"),
            actor_kind="agent", actor_name="agent-area:%s" % skill,
            create_if_missing=True)
    except journal.JournalError as exc:
        conflict = exc.code in ("journal.conflict", "journal.stale_preflight")
        if conflict:
            reason = ("%s changed since this draft was shown, so nothing "
                      "was written. Open the file, keep what you need, "
                      "then start the skill again. (%s)"
                      % (rel, exc.message))
        else:
            reason = ("Nothing was written: %s Next safe action: try the "
                      "skill again; if it keeps failing, check the course "
                      "directory is reachable." % exc.message)
        return _settled(iid, skill, exc.code, reason, conflict=conflict)

    entry_id = None
    for entry in journal.entries(base):
        if entry.get("object_id") == object_id \
                and entry.get("state") == "applied" \
                and entry.get("revision") == record["revision"]:
            entry_id = entry.get("entry_id")

    return {
        "state": "settled",
        "ok": True,
        "skill": skill,
        "interaction_id": iid,
        "target": rel,
        "operation": operation,
        "entry_id": entry_id,
        "revision": record["revision"],
        "prior_revision": record.get("parent_revision"),
        "undoable": True,
        "conflict": False,
        "reason": "Draft accepted into %s as revision %s. Undo restores "
                  "the previous content from the journal."
                  % (rel, record["revision"]),
    }
