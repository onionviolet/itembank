"""Synthetic staged tracer. Never register this adapter as a production route.

The sitting cursor, scorer, public projection and evidence writer are shipped
authorities. Optional binding below is a prototype, not an accepted schema.
Practice uses an explicitly disclosed exam transport to prove the barrier.
"""
import hashlib
import html
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import evidence
import journal
import model
import runtime
from surfaces import session

HERE = Path(__file__).resolve().parent
CHILDREN = ["a200000000000001", "a200000000000002"]


class Refusal(ValueError):
    pass


def fingerprint(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def case_revision(case):
    return hashlib.sha256(json.dumps(case, sort_keys=True,
                                    separators=(",", ":")).encode()).hexdigest()


def declaration(bank):
    return {"version": 1, "activity_id": "synthetic:counter-staged",
            "bank_fingerprint": fingerprint(bank), "stimulus":
            "A fictional counter starts at 3. A rule adds 2 once.",
            "children": CHILDREN[:], "order": ["answer", "reason"]}


def validate_case(case, qs, bank):
    if set(case) != {"version", "activity_id", "bank_fingerprint",
                     "stimulus", "children", "order"} or case["version"] != 1:
        raise Refusal("Unsupported case declaration.")
    if not isinstance(case["activity_id"], str) or not case["activity_id"]:
        raise Refusal("Name a stable activity identity.")
    if not isinstance(case["stimulus"], str) or not case["stimulus"].strip():
        raise Refusal("Supply a static stimulus.")
    if case["bank_fingerprint"] != fingerprint(bank):
        raise Refusal("Stale bank revision; preserve the sitting and restore its accepted bank.")
    ids = case["children"]
    if not isinstance(ids, list) or len(ids) != 2 or any(
            not isinstance(child, str) for child in ids) or len(set(ids)) != 2:
        raise Refusal("Declare exactly two distinct stable children.")
    found = {q.get("item_id"): q for q in qs}
    if case["order"] != ["answer", "reason"] or any(
            child not in found or found[child]["type"] != "mc" for child in ids):
        raise Refusal("Only fixed answer/reason order with two existing MC children is supported.")
    if any(sum(q.get("item_id") == child for q in qs) != 1 for child in ids):
        raise Refusal("Child identities must be unambiguous.")
    return [qs.index(found[child]) for child in ids]


def validate_cases(cases, qs, bank):
    activities, children = set(), set()
    for case in cases:
        validate_case(case, qs, bank)
        if case["activity_id"] in activities or children.intersection(case["children"]):
            raise Refusal("Duplicate activity or overlapping child membership.")
        activities.add(case["activity_id"])
        children.update(case["children"])


class StagedJourney:
    def __init__(self, base):
        self.base = Path(base)
        self.bank = self.base / "bank.md"
        self.sitting = self.base / "sitting.json"

    @classmethod
    def create(cls, base, mode="exam", selected=None):
        if mode not in ("practice", "exam", "diagnostic"):
            raise Refusal("Unsupported staged mode.")
        obj = cls(base)
        if obj.base.exists():
            raise Refusal("Use a fresh disposable workspace.")
        obj.base.mkdir(parents=True)
        shutil.copyfile(HERE / "fixtures" / "bank.md", obj.bank)
        case = declaration(obj.bank)
        indices = validate_case(case, model.load(str(obj.bank)), obj.bank)
        if selected is not None and selected != case["children"]:
            raise Refusal("Select the complete ordered case or explicitly exclude it.")
        # A dedicated two-item exam transport gives one genuine attempt per
        # child and no immediate practice feedback. Raw evidence remains exam.
        session.do_start(str(obj.bank), {"pair": "a2-counter", "count": 2,
                                        "seed": 3},
                         "exam" if mode == "practice" else mode,
                         str(obj.sitting), False)
        data = runtime.read_session(str(obj.sitting))
        data["items"] = indices
        data["staged_prototype"] = {"case": case, "case_revision": case_revision(case),
                                    "requested_mode": mode}
        runtime.write_session(str(obj.sitting), data)
        return obj

    def _load(self):
        data = runtime.read_session(str(self.sitting))
        binding = data.get("staged_prototype")
        if not binding:
            raise Refusal("Case revision unavailable; preserve responses and recover the bound revision.")
        if not self.bank.is_file():
            raise Refusal("Bank revision unavailable; preserve responses and recover the accepted bank.")
        if binding.get("case_revision") != case_revision(binding["case"]):
            raise Refusal("Stale case revision; preserve responses and recover the bound declaration.")
        qs = model.load(str(self.bank))
        indices = validate_case(binding["case"], qs, self.bank)
        if data["items"] != indices or data["cursor"] != len(data["responses"]):
            raise Refusal("Conflict in sitting commitment; preserve evidence for recovery.")
        events = self._events(data)
        if len(events) != len(data["responses"]):
            raise Refusal("Evidence/session crash window; preserve both for runtime reconciliation.")
        for i, (ev, response) in enumerate(zip(events, data["responses"])):
            if ev["item_id"] != binding["case"]["children"][i] or ev["answer"] != response["answer"]:
                raise Refusal("Evidence/session conflict; preserve both for review.")
        return data, qs, binding

    def _events(self, data):
        return [ev for ev in evidence.live_events(evidence.log_path(str(self.base)))
                if ev.get("session_id") == data["session_id"]
                and ev.get("event_type") == evidence.RESPONSE_EVENT_TYPE]

    def view(self):
        data, qs, binding = self._load()
        out = runtime.session_view(data, qs)
        out.update(stage=("complete" if data["status"] == "complete" else
                          binding["case"]["order"][data["cursor"]]),
                   stimulus=binding["case"]["stimulus"],
                   requested_mode=binding["requested_mode"],
                   transport_mode=data["mode"], revision=fingerprint(self.sitting))
        if data["responses"]:
            out["committed_answer"] = data["responses"][0]["answer"]
        if binding["requested_mode"] == "practice" and runtime.assessment_feedback_released(data["mode"], data):
            out["child_feedback"] = [runtime.explain_payload(qs[i], True) for i in data["items"]]
        return out

    def submit(self, item_id, answer, revision, *, stage=None):
        # The existing journal lock serializes all prototype reads/commits
        # across threads/processes. Production needs a session-owner lock.
        with journal._journal_lock(str(self.base)):
            data, qs, binding = self._load()
            if stage is not None:
                raise Refusal("Clients may not supply a stage.")
            if revision != fingerprint(self.sitting):
                raise Refusal("Stale or replayed commitment; reload the sitting.")
            if data["status"] != "active":
                raise Refusal("The case is already committed.")
            q = qs[data["items"][data["cursor"]]]
            public = runtime.public_item(q)
            if item_id != public["id"]:
                raise Refusal("Unopened or already committed child.")
            if not isinstance(answer, str) or answer not in public["response_schema"]["allowed"]:
                raise Refusal("Choose a declared MC option.")
            return session.do_submit(str(self.sitting), answer, None)

    def linked_events(self):
        """Derived linkage, not a second store or patched raw evidence event."""
        data, qs, binding = self._load()
        case = binding["case"]
        return [dict(runtime.evidence_feedback(ev, data), activity_id=case["activity_id"],
                     case_revision=binding["case_revision"], child_id=ev["item_id"],
                     stage=case["order"][i]) for i, ev in enumerate(self._events(data))]

    def render(self):
        view = self.view()
        esc = lambda value: html.escape(str(value), quote=True)
        body = '<h1>Synthetic staged case</h1><p>' + esc(view["stimulus"]) + '</p>'
        body += '<p>Requested mode: ' + esc(view["requested_mode"]) + '. Runtime transport: ' + esc(view["transport_mode"]) + '.</p>'
        if "committed_answer" in view:
            body += '<p>Committed answer: ' + esc(view["committed_answer"]) + '</p>'
        if "item" in view:
            item = view["item"]
            body += '<fieldset><legend>' + esc(item["stem"]) + '</legend>'
            for opt in item["options"]:
                body += '<label><input type="radio" name="answer" value="' + esc(opt["key"]) + '">' + esc(opt["text"]) + '</label>'
            body += '<button type="button">Commit response</button></fieldset>'
        else:
            body += '<p>Both responses committed.</p>'
        return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Staged tracer</title><main>' + body + '</main></html>'
