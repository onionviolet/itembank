"""Disposable synthetic clients over the shipped parser, session and journal.

No second assessment cursor, parser, scorer, or evidence store. A runtime
sitting is canonical. The sidecar stores revision binding and presentation
drafts only. Run this file to serve a new temporary synthetic workspace.
"""
import argparse
import hashlib
import html
import json
import shutil
import sys
import tempfile
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import evidence
import identity
import journal
import model
import runtime
from surfaces import session
from polynomial import analyze

HERE = Path(__file__).resolve().parent
PAIR = "a2-counter"
BRANCHES = {
    "route-a": {"prompt": "Change the starting value to four.",
                "transcript": "One addition of two now reaches six. The operation stays the same.",
                "ending": "transfer-example"},
    "route-b": {"prompt": "Trace one application from the original starting value.",
                "transcript": "Start at three, then add two once to reach five. Doubling is a different rule.",
                "ending": "trace-example"},
}
PASSAGE = "Rule: add two once. Start: three. Operation: addition, not doubling."
ANCHORS = {
    "A": {"id": "rule", "start": 0, "end": 19, "quote": "Rule: add two once."},
    "B": {"id": "start", "start": 20, "end": 33, "quote": "Start: three."},
    "C": {"id": "operation", "start": 34, "end": 68,
          "quote": "Operation: addition, not doubling."},
}


class Refusal(ValueError):
    pass


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class Journey:
    """Single-process local demo; production concurrent submission is excluded."""
    def __init__(self, base):
        self.base = Path(base)
        self.bank = self.base / "bank.md"
        self.sitting = self.base / "sitting.json"
        self.sidecar = self.base / "presentation.json"

    @classmethod
    def create(cls, base, family="staged", mode="exam"):
        if mode not in ("exam", "diagnostic"):
            raise Refusal("Staged practice is unavailable until runtime commitment policy is reviewed.")
        if family not in ("staged", "blanks", "evidence"):
            raise Refusal("Unknown synthetic family.")
        obj = cls(base)
        obj.base.mkdir(parents=True, exist_ok=True)
        if obj.bank.exists() or obj.sitting.exists() or obj.sidecar.exists():
            raise Refusal("Use a fresh disposable workspace; existing files are preserved.")
        shutil.copyfile(HERE / "fixtures" / "bank.md", obj.bank)
        spec = {"count": 1, "seed": 3}
        spec.update({"pair": PAIR} if family == "staged" else {
            "objective": "synthetic:flag" if family == "blanks" else "synthetic:evidence"})
        state = {"version": 1, "object_id": identity.new_object_id(), "family": family,
                 "bank_fingerprint": digest(obj.bank), "draft": None,
                 "playback_seconds": 0, "checkpoint": False,
                 "passage_fingerprint": hashlib.sha256(PASSAGE.encode()).hexdigest()}
        journal.commit_operation(str(obj.base), state["object_id"], "component",
                                 obj.sidecar.name, "mint", obj._encode(state), None,
                                 "agent", "a2-synthetic", create_if_missing=True)
        session.do_start(str(obj.bank), spec, mode, str(obj.sitting), False)
        return obj

    @staticmethod
    def _encode(state):
        return (json.dumps(state, sort_keys=True, indent=2) + "\n").encode()

    def state(self):
        state = json.loads(self.sidecar.read_text())
        if state["bank_fingerprint"] != digest(self.bank):
            raise Refusal("Stale bank revision; retain sitting and drafts, then inspect the original bank.")
        if state["passage_fingerprint"] != hashlib.sha256(PASSAGE.encode()).hexdigest():
            raise Refusal("Stale evidence anchors; retain the original selection for review.")
        return state

    def revision(self):
        return identity.object_fingerprint(self.sidecar.read_bytes(), "component")

    def _write(self, state, expected):
        if expected == self.revision() and self._encode(state) == self.sidecar.read_bytes():
            return None
        return journal.commit_operation(str(self.base), state["object_id"], "component",
                                        self.sidecar.name, "edit_in_place", self._encode(state),
                                        expected, "agent", "a2-synthetic")

    def view(self):
        state = self.state()
        data = runtime.read_session(str(self.sitting))
        qs = model.load(str(self.bank))
        # Derive stage from the runtime cursor; there is no persisted stage flag.
        out = runtime.session_view(data, qs)
        out["family"] = state["family"]
        out["presentation_revision"] = self.revision()
        out["bank_revision"] = state["bank_fingerprint"]
        if state["family"] == "staged":
            out["stage"] = "complete" if data["status"] == "complete" else (
                "answer" if data["cursor"] == 0 else "reason")
            if data["responses"]:
                out["committed_answer"] = data["responses"][0]["answer"]
                # Branch on the chosen option, never correctness or a hidden key.
                out["branch"] = "route-a" if out["committed_answer"] == "A" else "route-b"
            out["checkpoint"] = {"seconds": state["playback_seconds"],
                                 "complete": state["checkpoint"]}
            if data["status"] == "complete":
                out["observation"] = BRANCHES[out["branch"]]
        if "item" in out:
            draft = state.get("draft")
            if draft and draft["item_id"] == out["item"]["id"]:
                out["draft"] = draft["answer"]
        if state["family"] == "evidence":
            for anchor in ANCHORS.values():
                if PASSAGE[anchor["start"]:anchor["end"]] != anchor["quote"]:
                    raise Refusal("Invalid source anchor; inspect the passage instead of guessing.")
            out["passage"] = PASSAGE
            out["anchors"] = ANCHORS
        return out

    def save_draft(self, item_id, answer, expected):
        state = self.state()
        current = self.view().get("item")
        if not current or current["id"] != item_id:
            raise Refusal("Stale draft item; preserve input and reload the current stage.")
        # Invalid raw entry is saved for correction, never scored here.
        state["draft"] = {"item_id": item_id, "answer": answer}
        return self._write(state, expected)

    def submit(self, item_id, answer, expected, bank_revision):
        state = self.state()
        if bank_revision != state["bank_fingerprint"] or expected != self.revision():
            raise Refusal("Stale submission; reload without replacing the draft.")
        current = self.view().get("item")
        if not current or current["id"] != item_id:
            raise Refusal("Unopened or already committed stage; reload the runtime sitting.")
        # Preserve the entry before runtime refusal, including unsaved corrections.
        self.save_draft(item_id, answer, expected)
        # Generic MC/multi entry validity, not correctness. The runtime owns scoring.
        allowed = current.get("response_schema", {}).get("allowed", [])
        if current["type"] == "mc" and (not isinstance(answer, str) or answer not in allowed):
            raise Refusal("Choose a declared option.")
        if current["type"] == "multi" and (not isinstance(answer, list) or
                not answer or len(set(map(str, answer))) != len(answer) or
                any(not isinstance(x, str) or x not in allowed for x in answer)):
            raise Refusal("Select distinct declared evidence spans.")
        # do_submit validates fill input, records synthetic evidence and advances.
        return session.do_submit(str(self.sitting), answer, None)

    def checkpoint(self, seconds, complete, expected):
        state = self.state()
        if state["family"] != "staged" or self.view().get("stage") != "complete":
            raise Refusal("Commit prediction and reason before opening this observation.")
        if type(seconds) is not int or not 0 <= seconds <= 60 or type(complete) is not bool:
            raise Refusal("Use whole seconds from zero to sixty and a boolean checkpoint.")
        if complete and seconds != 60:
            raise Refusal("Read the full static observation before closing the checkpoint.")
        state.update(playback_seconds=seconds, checkpoint=complete)
        return self._write(state, expected)

    def report(self):
        self.state()
        return session.do_report(str(self.sitting))

    def render(self, message=""):
        view = self.view()
        esc = lambda s: html.escape(str(s), quote=True)
        heading = "Synthetic " + view["family"] + " journey"
        content = '<h1>' + esc(heading) + '</h1><p>Disposable prototype. Runtime-owned formal sitting.</p>'
        if message:
            content += '<p role="alert">' + esc(message) + '</p>'
        if "committed_answer" in view:
            content += '<p>Committed response: ' + esc(view["committed_answer"]) + '</p>'
            content += '<p>Selected branch: ' + esc(view["branch"]) + '</p>'
            if view.get("stage") == "complete":
                observation = view["observation"]
                content += '<h2>' + esc(observation["prompt"]) + '</h2><p>Static observation: ' + esc(observation["transcript"]) + '</p><p>Ending: ' + esc(observation["ending"]) + '</p>'
        if "passage" in view:
            content += '<p>' + esc(view["passage"]) + '</p>'
        item = view.get("item")
        if item:
            content += '<h2>' + esc("Complete each blank" if item["type"] == "fill" else item["stem"]) + '</h2><form method="post">'
            for key, value in (("item_id", item["id"]), ("revision", view["presentation_revision"]),
                               ("bank_revision", view["bank_revision"])):
                content += '<input type="hidden" name="' + key + '" value="' + esc(value) + '">'
            draft = view.get("draft")
            if item["type"] in ("mc", "multi"):
                for opt in item["options"]:
                    checked = draft == opt["key"] if item["type"] == "mc" else isinstance(draft, list) and opt["key"] in draft
                    content += '<label><input type="' + ('radio' if item["type"] == "mc" else 'checkbox') + '" name="answer" value="' + esc(opt["key"]) + '"' + (' checked' if checked else '') + '>' + esc(opt["text"]) + '</label>'
            elif item["type"] == "fill":
                inline = esc(item["stem"])
                for field in item["fields"]:
                    value = draft.get(field["id"], "") if isinstance(draft, dict) else ""
                    marker = "{{" + field["id"] + "}}"
                    if inline.count(marker) != 1:
                        raise Refusal("Each inline marker must name exactly one stable field.")
                    control = '<label class="inline" for="' + esc(field["id"]) + '">' + esc(field["label"]) + '<input id="' + esc(field["id"]) + '" name="field_' + esc(field["id"]) + '" value="' + esc(value) + '"></label>'
                    inline = inline.replace(marker, control)
                content += '<p>' + inline + '</p>'
            content += '<button name="action" value="save">Save draft</button><button name="action" value="submit">Commit response</button></form>'
        else:
            content += '<h2>Sitting complete</h2><pre>' + esc(json.dumps(self.report(), indent=2)) + '</pre>'
            if view.get("stage") == "complete":
                cp = view["checkpoint"]
                content += '<form method="post"><input type="hidden" name="revision" value="' + esc(view["presentation_revision"]) + '"><label for="seconds">Observation position in seconds (static transcript: 0 to 60)</label><input id="seconds" type="number" min="0" max="60" name="seconds" value="' + esc(cp["seconds"]) + '"><label><input type="checkbox" name="complete" value="yes"' + (' checked' if cp["complete"] else '') + '>I read the complete static observation</label><button name="action" value="checkpoint">Save observation checkpoint</button></form>'
        content += '<p role="status">' + esc(view.get("stage", view["status"])) + '</p>'
        return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>' + esc(heading) + '</title><style>body{font:18px system-ui;max-width:42rem;margin:2rem auto;padding:1rem}label{display:block;margin:1rem 0}.inline{display:inline-flex;flex-wrap:wrap;gap:.3rem;align-items:center;max-width:100%}.inline input{width:7rem}input,button{font:inherit;min-height:44px;max-width:100%}button{margin:.5rem}:focus-visible{outline:2px solid #165dcc;outline-offset:3px}pre{white-space:pre-wrap;overflow-wrap:anywhere}</style><main>' + content + '</main></html>'


def serve(port=0):
    temporary = tempfile.TemporaryDirectory(prefix="itembank-a2-demo-")
    base = Path(temporary.name)
    journeys = {name: Journey.create(base / name, name) for name in ("staged", "blanks", "evidence")}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            name = urlparse(self.path).path.strip("/") or "staged"
            if name not in journeys:
                self.send_error(404)
                return
            self.respond(journeys[name].render())

        def respond(self, body, status=200):
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(body.encode())

        def do_POST(self):
            name = urlparse(self.path).path.strip("/") or "staged"
            if name not in journeys:
                self.send_error(404)
                return
            obj = journeys[name]
            size = int(self.headers.get("Content-Length", "0"))
            if size > 8192:
                self.send_error(413)
                return
            fields = parse_qs(self.rfile.read(size).decode(), keep_blank_values=True)
            one = lambda key: fields.get(key, [""])[0]
            try:
                if one("action") == "checkpoint":
                    obj.checkpoint(int(one("seconds")), one("complete") == "yes", one("revision"))
                    self.send_response(303)
                    self.send_header("Location", "/" + name)
                    self.end_headers()
                    return
                item = obj.view().get("item")
                if not item:
                    raise Refusal("Sitting already complete.")
                answer = ({f["id"]: one("field_" + f["id"]) for f in item["fields"]}
                          if item["type"] == "fill" else fields.get("answer", [])
                          if item["type"] == "multi" else one("answer"))
                if one("action") == "save":
                    obj.save_draft(one("item_id"), answer, one("revision"))
                elif one("action") == "submit":
                    obj.submit(one("item_id"), answer, one("revision"), one("bank_revision"))
                else:
                    raise Refusal("Unknown action.")
                self.send_response(303)
                self.send_header("Location", "/" + name)
                self.end_headers()
            except (ValueError, SystemExit, journal.JournalError) as exc:
                self.respond(obj.render(str(exc)), 400)

    httpd = HTTPServer(("127.0.0.1", port), Handler)
    print("Synthetic demo: http://127.0.0.1:%d/staged (also /blanks and /evidence)" % httpd.server_port, flush=True)
    print("Disposable session root: " + temporary.name, flush=True)
    try:
        httpd.serve_forever()
    finally:
        httpd.server_close()
        temporary.cleanup()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=0)
    args = parser.parse_args()
    serve(args.port)
